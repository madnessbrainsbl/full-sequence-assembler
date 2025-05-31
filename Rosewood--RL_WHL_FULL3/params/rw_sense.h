// -----------------------------------------------------------------------------
//
// Do NOT modify or remove this copyright and confidentiality notice!
//
// Copyright (c) 2001 - $Date: 2016/09/20 $ Seagate Technology, LLC.
//
// The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
// Portions are also trade secret. Any use, duplication, derivation, distribution
// or disclosure of this code, for any reason, not expressly authorized is
// prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
//
//   VCS Information: $File: //depot/SGP/ProductBranches/RosewoodLC/RDT1_SF3/F1_Dev/source/Include/rw_sense.h $
//                    $Change: 1121346 $
//                    $Revision: #1 $
//                    $Author: chiliang.woo $
//                    $Date: 2016/09/20 $
//
//   Description:   Definition of R/W sense/error reporting information.
//
// -----------------------------------------------------------------------------
// Updated to meet SKDG Specifications
//-----------------------------------------------------------------------------

#ifndef __INCLUDE_RW_SENSE_H

#define __INCLUDE_RW_SENSE_H

// =============================================================================
// The R/W error codes
// =============================================================================

//<RW_SENSE_ERROR_CODES>
//---------------------------------------------------------------------------------------------
// Read/Write Sense Error Codes
//---------------------------------------------------------------------------------------------
//
// R/W Sense Error Codes are error codes that R/W reports to its clients.  Although they are
// very similar to traditional SCSI sense codes, there is not a one-to-one correspondence with
// traditional SCSI sense codes.  These R/W Sense Error Codes should be treated and interpreted
// independently from them.  SCSI sense code definitions can be found at the following link.
//
// <a href="notes://NA-DB01/8625694B006C12FC/8AB05DDA3C4AF614862573EC005B2022/555EF70CE61CAAF686256E9A00734EEF">"FRU, Sense key code descriptions" in F1 Documentation</a>
//
// R/W Sense Error Codes may be reported with one or more bits of their most significant nybble
// set.  These bits are described below:
//
// Bit 31: Move FRU Flag.
//
//         If this bit is set, it indicates that the least significant byte of the sense code
//         should be copied into the additional sense code qualifier when it is translated into
//         a SCSI sense code.
//
// Bit 30: Read/Write Retryable Error Type.
//
//         If this bit is set, it indicates that the condition that caused R/W to report the
//         R/W Sense Error Code is retryable.  This gives R/W clients an opportunity to perform
//         higher level retries.  IMPORTANT!  Please note that R/W Sense Error Codes that are
//         reported in a diagnostic environment (e.g. serial port debug statements) should
//         never be considered hard errors when this bit is set.
//
//</RW_SENSE_ERROR_CODES>

#define RW_RETRYABLE_ERR_TYPE                0x40000000  // retryable error code for read/write.
#define RW_ERROR_CODE_MASK                   RW_RETRYABLE_ERR_TYPE

#if FE_0115105_212104_CHANNEL_FAULTS_RETRYABLE
// Some product configurations require channel faults to be set to retryable
// type by default (PSG and post-gen-2.0 ESG configurations).
// A compile-time conditional option serves this purpose so that
// ESG configurations (primarily) can choose which faults are
// permitted retries.
#define RW_CONDITIONAL_RETRY_OPTION         RW_RETRYABLE_ERR_TYPE
#else
#define RW_CONDITIONAL_RETRY_OPTION         0x00000000
#endif

#define RW_FORCED_RETRYABLE_ERR_TYPE        RW_RETRYABLE_ERR_TYPE

#if RW_SCSI_SUPPORT || SATA_TRANSPORT // ###mah temporarily enable for ATA


   #define  RW_SENSE_KEY_MASK                0xF0FFFFFF
   #define  RW_ERROR_CATEGORY_MASK           0xBFFFFFFF   // Mask field for R/W error category.

// -----------------------------------------------------------------------------
//
// Defined Sense Error Code.
//
typedef uint32 rw_error_code;

// --------------------------------------------------------------------------
   // Note:  1.FRU codes associated with the R/W subsystem must be in the range
   //          0x80-0xFF in each category to avoid overlap with Interface
   //          subsystem FRU codes (which occupy the range 0x00-0x7F).
   //        2.Changes to the FRU code also require update "FRU code descriptions"
   //          document in F1 Documentation under specification.
   //
   // --------------------------------------------------------------------------

   //<RW_SENSE_ERROR_CODES>

   //***************************************************************************
   // Internal x0/00 Errors.
   //***************************************************************************
   // 0x00000080: RW_NO_ERRORS - No R/W Errors encountered.
   // 0x00000081: RW_REQUEST_ABORTED - Request failed due to abort of request.
   // 0x00000082: RW_REQUEST_SOFT_ABORTED - Request failed due to soft abort of request.
   // 0x00000083: RW_DATA_SCRUB_SUCCESSFUL - Reallocate Block - Data scrub of the original sector was successful.
   // 0x00000084: RW_FILE_ERROR - R/W file error encountered.
   // 0x00000085: RW_XFR_PARTITION_OVERFLOWED - Disc Xfr - Partition overflowed.
   // 0x40000087: RW_BLOCK_REALLOCATED_01 - Disc Xfr - Reallocated block encountered.
   // 0x40000088: RW_BLOCK_REALLOCATED_02 - Disc Xfr - Reallocated block encountered.
   // 0x40000089: RW_BLOCK_REALLOCATED_03 - Disc Xfr - Reallocated block encountered.
   // 0x0000008A: RW_FBA_OBTAINED - This is not an error type.
   // 0x0000008B: RW_REQUEST_ABORTED_DUE_TO_INVALID_INPUT - Inputs for the FDB leakage detection test were invalid
   // 0x0000008C: RW_SERVO_OP_ABORTED - Servo operation was aborted.
   // 0x0000008D: RW_SUPER_SECTOR_EARLY_DISC_HALT - Super Sector - Early disc halt.
   // 0x0000008E: RW_POWER_SAVE_INVALID_REQUEST_01 - Power Save - Invalid request.
   // 0x0000008F: RW_READ_AFTER_WRITE_REQ - Read After Write mode requested
   // 0x00000090: RW_SWD_DVGAS_FAULT_RAW_REQ - Read After Write mode due to SWD Dvgas fault requested
   // 0x00000091: RW_SWD_RVGAS_FAULT_RAW_REQ - Read After Write mode due to SWD Rvgas fault requested
   // 0x00000092: RW_SWD_FVGAS_FAULT_RAW_REQ - Read After Write mode due to SWD Fvgas fault requested
   // 0x00000093: RW_SWD_DVGAS_SUM_FAULT_RAW_REQ - RAW mode due to SWD Sum fault, last SWD fault was a Dvgas fault, requested
   // 0x00000094: RW_SWD_RVGAS_SUM_FAULT_RAW_REQ - RAW mode due to SWD Sum fault, last SWD fault was a Rvgas fault, requested
   // 0x00000095: RW_SWD_FVGAS_SUM_FAULT_RAW_REQ - RAW mode due to SWD Sum fault, last SWD fault was a Fvgas fault, requested
   // 0x00000096: RW_SERVICE_DRIVE_FREE_FALL_CONDITION_ABORTED - Servicing of free-fall condition was aborted.
   // 0x00000097: RW_FORMAT_MAX_NUM_SWD_ERRORS_PER_TRACK_EXCEEDED - Format - Number of SWD errors per track exceeded.
   // 0x00000098: RW_SERVO_DISC_SLIP_RECAL_NOT_ALLOWED - Servo Disc Slip recalibration not allowed.
   // 0x00000099: RW_DATA_SCRUB_PARTIALLY_SUCCESSFUL - Requested multiple blks be reallocated and scrubbed but an error occurred which truncated the scrubbing process.
   // 0x000000A0: RW_UNKNOWN_CHANNEL_NON_CONVERGED_ERROR - Read Channel LDPC detector non-converged due to unknown error
   // 0x000000A1: RW_THERMAL_ASPERITY - Read Channel LDPC detector non-converged due to Thermal Asperity error
   // 0x000000A2: RW_CODE_VIOLATION - Read Channel LDPC detector non-converged due to Code Violation error
   // 0x000000A3: RW_FLAWSCAN_BUS - Read Channel LDPC detector non-converged due to Flawscan Bus error
   // 0x000000A4: RW_BERP_UNKNOWN_ERR - No Description Added @@@
   // 0x000000A5: RW_SKIP_LBA_ALTED_DURING_RUNT_SUPER_BLK_DIRTY_MARK - Skip LBA was reallocated during runt super block dirty marking.
   // 0x000000A6: RW_XFR_PARITY_SECTOR_ERROR - Error encountered on a parity sector during transfer.
   // 0x000000AB: RW_INITIATE_SEEK_ERROR - The actuator was not in a proper state to initiate a seek request
   // 0x000000D0: RW_EFD_WRITE_CONTACT_FAULT_RAW_REQ - RAW mode due to EBMS Contact fault during Write.
   // 0x000000D1: RW_EFD_SWOT_FAULT_RAW_REQ - RAW mode due to EBMS SWOT fault.
   // 0x000000D2: RW_ATTEMPT_TO_ACCESS_FAFH_TEST_SERPENT - Seek to an FAFH Test Serpent was requested without the FAFH_TEST_SERPENT_ACCESS_ALLOWED bit of UtiltiyFlags set.
   // 0x000000D3: RW_DATA_SCRUB_METRICS_FAILED - Data scrub failed due to read channel metrics.
   // 0x000000D4: RW_MED_RECOVERY_FIRST_WRITE_DONE - Markov Write Retry for first write done setup so that FW can continue to do write retry.
   // 0x000000D5: RW_MED_RECOVERY_FIRST_WRITE_RETRY_DONE - Markov Write Retry for failed first write due to pseudo encoding on first failed sector.
   // 0x000000D6: RW_OC_RANDOMIZER_SEED_WRITE_DONE - Outer code randomizer seed write done so that FW can continue to do write retry.
   // 0x000000D7: RW_OC_SPRAM_TO_DRAM_FLUSH_TIMEOUT - Outer code Data flush from SuperParity RAM to DRAM timed out.
   //</RW_SENSE_ERROR_CODES>

   #define RW_NO_ERRORS                                       0x00000080
   #define RW_REQUEST_ABORTED                                 0x00000081
   #define RW_REQUEST_SOFT_ABORTED                            0x00000082
   #define RW_DATA_SCRUB_SUCCESSFUL                           0x00000083
   #define RW_FILE_ERROR                                      0x00000084
   #define RW_XFR_PARTITION_OVERFLOWED                        0x00000085
   #define RW_BLOCK_REALLOCATED_01                            (0x00000087 | RW_RETRYABLE_ERR_TYPE)
   #define RW_BLOCK_REALLOCATED_02                            (0x00000088 | RW_RETRYABLE_ERR_TYPE)
   #define RW_BLOCK_REALLOCATED_03                            (0x00000089 | RW_RETRYABLE_ERR_TYPE)
   #define RW_FBA_OBTAINED                                    0x0000008A

#if DETECT_FDB_MOTOR_LEAKAGE || SCHEDULED_DIAGNOSIS_AND_REPAIR
   #define RW_REQUEST_ABORTED_DUE_TO_INVALID_INPUT            0x0000008B
#endif

   #define RW_SERVO_OP_ABORTED                                0x0000008C
   #define RW_SUPER_SECTOR_EARLY_DISC_HALT                    0x0000008D
   #define RW_POWER_SAVE_INVALID_REQUEST_01                   0x0000008E

#if RW_READ_AFTER_WRITE
   #define RW_READ_AFTER_WRITE_REQ                            0x0000008F
#endif
#if RW_SKIP_WRITE_DETECT
   #define RW_SWD_DVGAS_FAULT_RAW_REQ                         0x00000090
   #define RW_SWD_RVGAS_FAULT_RAW_REQ                         0x00000091
   #define RW_SWD_FVGAS_FAULT_RAW_REQ                         0x00000092
   #define RW_SWD_DVGAS_SUM_FAULT_RAW_REQ                     0x00000093
   #define RW_SWD_RVGAS_SUM_FAULT_RAW_REQ                     0x00000094
   #define RW_SWD_FVGAS_SUM_FAULT_RAW_REQ                     0x00000095
#endif
#if DRIVE_FREE_FALL_PROTECTION_SUPPORT
   #define RW_SERVICE_DRIVE_FREE_FALL_CONDITION_ABORTED       0x00000096
#endif
//#if RW_FORMAT_DEALLOCATE_TRACK_SWD_ERRORS
   #define RW_FORMAT_MAX_NUM_SWD_ERRORS_PER_TRACK_EXCEEDED    0x00000097
//#endif
#if (SERVO_DISC_SLIP_SUPPORT && F3_CERT_AND_DIAG)
   #define RW_SERVO_DISC_SLIP_RECAL_NOT_ALLOWED               0x00000098
#endif
#if TRACK_USAGE_MONITOR_TABLE
   #define RW_READ_ON_UNWRITTEN_NOT_ALLOWED                   0x0000009A
#endif
#if RW_BERP_ERROR_RECOVERY
   #define RW_UNKNOWN_CHANNEL_NON_CONVERGED_ERROR             (0x000000A0 | RW_RETRYABLE_ERR_TYPE)
   #define RW_THERMAL_ASPERITY                                (0x000000A1 | RW_RETRYABLE_ERR_TYPE)
   #define RW_CODE_VIOLATION                                  (0x000000A2 | RW_RETRYABLE_ERR_TYPE)
   #define RW_FLAWSCAN_BUS                                    (0x000000A3 | RW_RETRYABLE_ERR_TYPE)
   #define RW_BERP_UNKNOWN_ERR                                (0x000000A4 | RW_RETRYABLE_ERR_TYPE)
#endif
#if INLINE_PARITY_SECTORS
   #define RW_SKIP_LBA_ALTED_DURING_RUNT_SUPER_BLK_DIRTY_MARK (0x000000A5 | RW_RETRYABLE_ERR_TYPE)
   #define RW_XFR_PARITY_SECTOR_ERROR                         (0x000000A6 | RW_RETRYABLE_ERR_TYPE)
#endif
   #define RW_INITIATE_SEEK_ERROR                             0x000000AB

#if RW_MARVELL_ERM_RTM
   #define RW_DYN_CHN_RECOV_MISUSE_ERR                         (0x000000AC | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_START_CF_HALT_ERR                  (0x000000AD | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_CHN_RDY_TEP_ERROR                  (0x000000AE | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_XFR_START_CW_ALIGN_ERR             (0x000000AF | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_CF_HALT_MX_XFR_END_RETRY_ERR       (0x000000B0 | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_CF_HALT_RETRY_START_ERR            (0x000000B1 | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_CF_HALT_RETRY_XFR_ERR              (0x000000B2 | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_RETRY_EXHST_ERR                    (0x000000B3 | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_UNDEFINED_RTM_METHOD_ERR           (0x000000B4 | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_CF_HALT_SM_CORNER_CASE_MEDIA_REACQUIRE_ERR     (0x000000B5 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_CF_HALT_MX_XFR_END_RETRY_ERR2         (0x000000B6 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_SINGLE_SECTOR_MEDIA_RETRY_START_ERROR (0x000000B7 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_CF_HALT_MX_XFR_END_RETRY_ERR3         (0x000000B8 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_RESYNC_CW0_ERR                        (0x000000B9 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_RESYNC_CW1_ERR                        (0x000000BA | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_WAIT_FOR_READGATE_TIMEOUT_ERR         (0x000000BB | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_RTM_NCW_LIBRARY_NOT_LOADED            (0x000000BC | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_UNEXPECTED_DX_STATE_ERR               (0x000000BD | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_CF_HALT_MX_XFR_END_RETRY_ERR4         (0x000000BE | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_CF_HALT_MX_XFR_END_RETRY_ERR5         (0x000000BF | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_CF_HALT_MX_XFR_END_RETRY_ERR6         (0x000000C0 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_CF_EDAC_HALT_RETRY_START_ERR          (0x000000C1 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_WAIT_FOR_START_END_CNT_TIMEOUT_ERR    (0x000000C2 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_ABORT_WITHIN_RTM_ERR                  (0x000000C3 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_ABORT_WITHIN_RTM_ERR2                 (0x000000C4 | RW_RETRYABLE_ERR_TYPE)
#if RW_MARVELL_ERM_RTM_ENHANCEMENT_V00
   #define DYN_CHN_RECOV_CF_HALT_MX_XFR_END_RETRY_ERR7         (0x000000C5 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_CF_HALT_MX_XFR_END_RETRY_ERR8         (0x000000C6 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_ABORT_WITHIN_RTM_ERR3                 (0x000000C7 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_ABORT_WITHIN_RTM_ERR4                 (0x000000C8 | RW_RETRYABLE_ERR_TYPE)
   #define DYN_CHN_RECOV_ABORT_WITHIN_RTM_ERR5                 (0x000000C9 | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_CF_HALT_RETRY_START_ERR1           (0x000000CA | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_DECODE_HALT_ERR                    (0x000000CB | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_FIRAVG_HALT_ERR                    (0x000000CC | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_RESYNC_HALT_ERR                    (0x000000CD | RW_RETRYABLE_ERR_TYPE)
   #define RW_DYN_CHN_RECOV_SYNDROMEWEIGHT_HALT_ERR            (0x000000CE | RW_RETRYABLE_ERR_TYPE)
#endif   //RW_MARVELL_ERM_RTM_ENHANCEMENT_V00
#endif   //RW_MARVELL_ERM_RTM

#if RW_CONTACT_FAULT_DETECTION
   #define RW_EFD_WRITE_CONTACT_FAULT_RAW_REQ                  0x000000D0
   #define RW_EFD_SWOT_FAULT_RAW_REQ                           0x000000D1
#endif
   #define RW_ATTEMPT_TO_ACCESS_FAFH_TEST_SERPENT              0x000000D2
   #define RW_DATA_SCRUB_METRICS_FAILED                        0x000000D3

   #define RW_MED_RECOVERY_FIRST_WRITE_DONE                    (0x000000D4 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MED_RECOVERY_FIRST_WRITE_RETRY_DONE              (0x000000D5 | RW_RETRYABLE_ERR_TYPE)

   #define RW_OC_PARITY_SECTORS_RE_WRITE_DONE                  (0x000000D6 | RW_RETRYABLE_ERR_TYPE)
   #define RW_OC_SPRAM_TO_DRAM_FLUSH_TIMEOUT                   0x000000D7

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x1/40 Errors.
   //***************************************************************************
   // 0x81400280: RW_SERVO_SPINUP_RECOVERED_01 - Spinup error recovered with buzz retries.
   // 0x81400281: RW_SERVO_SPINUP_RECOVERED_02 - Spinup error recovered without buzz retries.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_SERVO_SPINUP_RECOVERED_01                       0x01400280
   #define RW_SERVO_SPINUP_RECOVERED_02                       0x01400281

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x2/04 Errors.
   //***************************************************************************
   // 0x02040080: RW_NOT_READY - Initialization - R/W system not ready for client requests.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_NOT_READY                                       0x02040080

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x3/0C Errors.
   //***************************************************************************
   // 0x430C0080: RW_UPDATE_BVD_FAILED - Disc Xfr - BVD update error.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_UPDATE_BVD_FAILED                               (0x030C0080 | RW_RETRYABLE_ERR_TYPE)

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x3/11 Errors.
   //***************************************************************************
   // 0x43110080: RW_READ_PREAMP_UNSAFE_FAULT - Disc Xfr - Read during preamp unsafe fault.
   // 0x43110081: RW_EDAC_HW_UNCORR_ERR - Disc Xfr - HW uncorrectable medium error.
   // 0x43110082: RW_EDAC_OVERRUN_ERR - Disc Xfr - EDAC overrun error.
   // 0x03110083: RW_COR_DIS_UNCORR_ERR - Disc Xfr - EDAC error is injected by Correction Disable.
   // 0x031100A0: RW_READ_PREAMP_HTR_OPEN_SHORT_FAULT - Read preamp unsafe fault with short/open fault set
   // 0x03110480: RW_WRITE_ALTERNATE_FAILED_NO_SERVO_DEFECTS - Reallocate Block - Write alternate block failed, no servo defects.
   // 0x03110481: RW_ALTERNATE_BLK_COMPARE_TEST_FAILED - Reallocate Block - Alternate block compare test failed.
   // 0x03110482: RW_ALTERNATE_BLK_SYNC_MARK_ERR - Reallocate Block - Alternate block sync mark error.
   // 0x03110483: RW_ALTERNATE_BLOCK_SELECTION_EXHAUSTED - Reallocate Block - Maximum allowed alternate selection exhausted.
   // 0x03110484: RW_REPETITIVE_REALLOCATION_NOT_ALLOWED - Reallocate Block - Resource is not available for a repetitive reallocation.
   // 0x03110485: RW_SERV_HWEDAC_FAILURE - SERV HW EDAC failure
   // 0x03110486: RW_SERV_SID_FAILURE - SERV DIS failure
   // 0x03110487: RW_NUM_PEND_REAL_SECS_IN_SUPER_BLK_LIMIT_EXCEEDED - Pending reallocation sectors count, in target super block, exceeded limit.
   // 0x03110488: RW_READ_SUPER_BLK_PENDING_FOR_REALLOCATION - A sector pending reallocation was encountered during read of super block data.
   // 0x03110489: RW_WRITE_SUPER_BLK_PENDING_FOR_REALLOCATION - A sector pending reallocation was encountered during write of super block data.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_READ_PREAMP_UNSAFE_FAULT                        (0x03110080 | RW_RETRYABLE_ERR_TYPE)
   #define RW_EDAC_HW_UNCORR_ERR                              (0x03110081 | RW_RETRYABLE_ERR_TYPE)
   #define RW_EDAC_OVERRUN_ERR                                (0x03110082 | RW_RETRYABLE_ERR_TYPE)
   #define RW_COR_DIS_UNCORR_ERR                              0x03110083

#if FE_0116076_355860_MEDIA_CACHE
   #define RW_READ_FROM_MEDIA_CACHE_HARDENED_LBA              0x03110084
#endif

//#if ( REMOVED Flag: REPORT_PREAMP_HEATER_OPEN_SHORT_FAULT = 0 )
   #define RW_READ_PREAMP_HTR_OPEN_SHORT_FAULT                0x031100A0
//#endif

   #define RW_WRITE_ALTERNATE_FAILED_NO_SERVO_DEFECTS         0x03110480
   #define RW_ALTERNATE_BLK_COMPARE_TEST_FAILED               0x03110481
   #define RW_ALTERNATE_BLK_SYNC_MARK_ERR                     0x03110482
   #define RW_ALTERNATE_BLOCK_SELECTION_EXHAUSTED             0x03110483
   #define RW_REPETITIVE_REALLOCATION_NOT_ALLOWED             0x03110484
   #define RW_SERV_HWEDAC_FAILURE                             0x03110485
   #define RW_SERV_SID_FAILURE                                0x03110486

#if INLINE_PARITY_SECTORS
   #define RW_NUM_PEND_REAL_SECS_IN_SUPER_BLK_LIMIT_EXCEEDED  0x03110487
   #define RW_READ_SUPER_BLK_PENDING_FOR_REALLOCATION         0x03110488
   #define RW_WRITE_SUPER_BLK_PENDING_FOR_REALLOCATION        0x03110489
#endif

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x3/14 Errors.
   //***************************************************************************
   // 0x83140180: RW_SEARCH_EXHAUSTED - Disc Xfr - Search exhaust error.
   // 0x83140181: RW_REALLOCATED_LBA_WRITE_DISALLOWED - Disc Xfr - Reallocated LBA is restricted from write access.
   // 0x83140182: RW_REALLOCATED_LBA_READ_DISALLOWED - Disc Xfr - Reallocated LBA is restricted from read access.
   // 0x03140183: RW_RESERVE_ZONE_LOGPAGE_READ_WRITE_FAILURE - Disc Xfr - Reserved zone Read/Write for logpage data is failed.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_SEARCH_EXHAUSTED                                0x03140180
   #define RW_REALLOCATED_LBA_WRITE_DISALLOWED                0x03140181
   #define RW_REALLOCATED_LBA_READ_DISALLOWED                 0x03140182
   #define RW_RESERVE_ZONE_LOGPAGE_READ_WRITE_FAILURE         0x03140183

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x3/16 Errors.
   //***************************************************************************
   // 0xC3160080: RW_DATA_SYNC_TIMEOUT - Disc Xfr - Data sync timeout error.
   // 0xC3160081: RW_PBM_DETECTED_FORM_FIFO_PARITY_ERR - Disc Xfr - PBM detected Formatter FIFO parity error.
   // 0xC3160082: RW_FORMATTER_DETECTED_FORM_FIFO_PARITY_ERR - Disc Xfr - Formatted detected Formatter FIFO parity error.
   // 0xC3160083: RW_SUPER_SECTOR_DATA_SYNC_TIMEOUT - Super Sector - Data sync timeout error.
   // 0xC3160084: RW_DATA_SPLIT_SYNC_TIMEOUT - Disc Xfr - Data sync timeout error on sector splits.
   // 0xC3160100: RW_DATA_MISSED_SYNC - Disc Xfr - Data missed sync mark error. FRU code is bits mask indicating which
   //                                              fragment(s) have missed sync error. Bit n represents fragment n.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_DATA_SYNC_TIMEOUT                               (0x03160080 | RW_RETRYABLE_ERR_TYPE)
   #define RW_PBM_DETECTED_FORM_FIFO_PARITY_ERR               (0x03160081 | RW_RETRYABLE_ERR_TYPE)
   #define RW_FORMATTER_DETECTED_FORM_FIFO_PARITY_ERR         (0x03160082 | RW_RETRYABLE_ERR_TYPE)
   #define RW_SUPER_SECTOR_DATA_SYNC_TIMEOUT                  (0x03160083 | RW_RETRYABLE_ERR_TYPE)
   #define RW_DATA_SPLIT_SYNC_TIMEOUT                         (0x03160084 | RW_RETRYABLE_ERR_TYPE)
   #define RW_DATA_MISSED_SYNC                                (0x03160100 | RW_RETRYABLE_ERR_TYPE)

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x3/32/01 Errors.
   //***************************************************************************
   // 0x83320180: RW_SAVE_DEFECT_FILES_FAILED - Reallocate Block - Failed to save defect files.
   // 0x83320181: RW_SAVE_POST_FORMAT_DEFECTS_INFO_FILE_FAILED_1 - Reallocate Block - Failed to save defect files post format.
   // 0x83320182: RW_SAVE_POST_FORMAT_DEFECTS_INFO_FILE_FAILED_2 - Reallocate Block - Failed to save defect files post format.
   // 0x83320183: RW_SAVE_POST_FORMAT_DEFECTS_INFO_FILE_FAILED_3 - Reallocate Block - Failed to save defect files post format.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_SAVE_DEFECT_FILES_FAILED                        0x03320180
   #define RW_SAVE_POST_FORMAT_DEFECTS_INFO_FILE_FAILED_1     0x03320181
   #define RW_SAVE_POST_FORMAT_DEFECTS_INFO_FILE_FAILED_2     0x03320182
   #define RW_SAVE_POST_FORMAT_DEFECTS_INFO_FILE_FAILED_3     0x03320183

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/01 Errors.
   //***************************************************************************
   // 0x84010080: RW_MEDIA_MGR_SPINUP_ERR - Spinup - Media Manager error encountered.
   // 0xC4010081: RW_SEQ_DATA_FIELD_TIMEOUT - Disc Xfr - Data field timeout error.
   // 0xC4010082: RW_MM_TDT_FIFO_CTR_ERR - Disc Xfr - Media Manager's TDT FIFO Counter error.
   // 0xC4010083: RW_MM_SERVO_CTR_ERR - Disc Xfr - Media Manager's Servo Counter error.
   // 0xC4010084: RW_MM_LATENCY_ERR - Disc Xfr - Media Manager's Latency error.
   // 0xC4010085: RW_MM_INDEX_ERR - Disc Xfr - Media Manager's Index error.
   // 0xC4010086: RW_MM_SERVO_ERR - Disc Xfr - Media Manager's Servo error.
   // 0x84010087: RW_CLEAR_MM_ERRORS_FAILED - Disc Xfr - Media Manager errors could not be cleared successfully.
   // 0x84010088: RW_CLEAR_SERVO_INDUCED_MM_ERRORS_FAILED - Disc Xfr - Clearing of MM errors due to a servo error failed.
   // 0x84010089: RW_SECTOR_WORD_COUNT_ENABLED_ON_SERVO - Disc Xfr - SWCE/SGate overlap error.
   // 0x8401008A: RW_SEQ_SERVO_GATE_TIMEOUT_01 - Disc Xfr - Servo gate timeout error.
   // 0x8401008B: RW_SEQ_SERVO_GATE_TIMEOUT_02 - Disc Xfr - Servo gate timeout error.
   // 0x8401008C: RW_SEQ_SERVO_GATE_TIMEOUT_03 - Disc Xfr - Servo gate timeout error.
   // 0x8401008D: RW_SEQ_SERVO_GATE_TIMEOUT_04 - Disc Xfr - Servo gate timeout error.
   // 0x8401008E: RW_SEQ_SERVO_GATE_TIMEOUT_05 - Disc Xfr - Servo gate timeout error.
   // 0x8401008F: RW_SMART_HANDSHAKE_ERR - Super Sector - Handshake error.
   // 0x84010090: RW_SMART_SEQ_SGATE_TIMEOUT_01 - Super Sector - Servo gate timeout error.
   // 0x84010091: RW_SMART_SEQ_SGATE_TIMEOUT_02 - Super Sector - Servo gate timeout error.
   // 0x84010092: RW_SMART_SEQ_SGATE_TIMEOUT_03 - Super Sector - Servo gate timeout error.
   // 0x84010093: RW_SMART_SEQ_SGATE_TIMEOUT_04 - Super Sector - Servo gate timeout error.
   // 0x84010094: RW_SMART_SEQ_SGATE_TIMEOUT_05 - Super Sector - Servo gate timeout error.
   // 0x84010095: RW_ASEEK_REQ_PULSE_SGATE_TIMEOUT - Disc Xfr - Servo gate timeout error during generation of Aseek Req.
   // 0x84010096: RW_SEQ_BVD_CHECK_TIMEOUT - Disc Xfr - BVD check timeout error.
   // 0x84010097: RW_SEQ_NRZ_XFR_DONE_TIMEOUT - Disc Xfr - NRZ sequencer completion timeout error.
   // 0xC4010098: RW_SEQ_MEDIA_MGR_TIMEOUT - Disc Xfr - Sequencer timeout on Media Manager event.
   // 0xC4010099: RW_NRZ_XFR_MEDIA_MGR_ERR - Disc Xfr - NRZ xfr error on Media Manager event.
   // 0x8401009A: RW_DISC_SEQ_HANDSHAKE_ERR - Disc Xfr - Handshake error.
   // 0x8401009B: RW_MEDIUM_LATENCY_SYNC_ERR - Disc Xfr - Medium latency sync error.
   // 0x8401009C: RW_SERVO_FAST_IO_MISSED_SAMPLE_ERR - Fast IO - Missed servo sample.
   // 0xC401009D: RW_MM_AASEEK_XFR_ERR - Disc Xfr - Media Manager's Anticipatory xfr error.
   // 0x8401009E: RW_WAIT_FOR_NRZ_SEQUENCER_TIMEOUT - When a reassigned sector is encountered, wait for the NRZ to finish the previous sector
   // 0x8401009F: RW_SEQUENCER_FAST_IO_SYNC_ERR - Fast IO Data Collection out of sync with sequencer
   // 0x840100A0: RW_CHANNEL_NOT_READY_REV_COUNT_EXHAUSTED - Disc Xfr - Channel not ready rev count exhausted.  Apply to LDPC LLI channels.
   // 0xC40100A1: RW_MM_AASEEK_SERVO_ERR - Disc Xfr - Media Manager's Anticipatory servo error.
   // 0xC40100A2: RW_MM_AASEEK_DISC_PAUSE_CONDITION - Disc Xfr - Media Manager's Anticipatory xfr error, disc pause condition exists
   // 0x040100A3: RW_BERP_INFINITE_LOOP_TERMINATED - No Description Added @@@
   // 0xC40100A4: RW_DISC_SEQ_BROWNOUT_DET - Disc Xfr - Brownout detected during write operation.
   // 0xC40100A5: SEQ_NRZ_XFR_DONE_TIMEOUT_AT_REAS_SEC - Disc Xfr - NRZ sequencer completion timeout error at reassigned sector.
   // 0x840100A6: RW_SEQ_READ_START_SGATE_TIMEOUT - Disc Xfr - Sequencer Servo gate timeout error during start of a sector read.
   // 0x840100A7: RW_SEQ_READ_HDR_EXP_SGATE_TIMEOUT - Disc Xfr - Sequencer header exception Servo gate timeout error on a sector read.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_MEDIA_MGR_SPINUP_ERR                            0x04010080
   #define RW_SEQ_DATA_FIELD_TIMEOUT                          (0x04010081 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MM_TDT_FIFO_CTR_ERR                             (0x04010082 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MM_SERVO_CTR_ERR                                (0x04010083 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MM_LATENCY_ERR                                  (0x04010084 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MM_INDEX_ERR                                    (0x04010085 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MM_SERVO_ERR                                    (0x04010086 | RW_RETRYABLE_ERR_TYPE)
   #define RW_CLEAR_MM_ERRORS_FAILED                          0x04010087
   #define RW_CLEAR_SERVO_INDUCED_MM_ERRORS_FAILED            0x04010088

#if WA_0174372_352870_RESEEK_AND_RETRY_SG_OVLP_HALT
   #define RW_SECTOR_WORD_COUNT_ENABLED_ON_SERVO              (0x04010089 | RW_RETRYABLE_ERR_TYPE)
#else
   #define RW_SECTOR_WORD_COUNT_ENABLED_ON_SERVO              0x04010089
#endif

   #define RW_SEQ_SERVO_GATE_TIMEOUT_01                       0x0401008A
   #define RW_SEQ_SERVO_GATE_TIMEOUT_02                       0x0401008B
   #define RW_SEQ_SERVO_GATE_TIMEOUT_03                       0x0401008C
   #define RW_SEQ_SERVO_GATE_TIMEOUT_04                       0x0401008D
   #define RW_SEQ_SERVO_GATE_TIMEOUT_05                       0x0401008E
   #define RW_SMART_HANDSHAKE_ERR                             0x0401008F
   #define RW_SMART_SEQ_SGATE_TIMEOUT_01                      0x04010090
   #define RW_SMART_SEQ_SGATE_TIMEOUT_02                      0x04010091
   #define RW_SMART_SEQ_SGATE_TIMEOUT_03                      0x04010092
   #define RW_SMART_SEQ_SGATE_TIMEOUT_04                      0x04010093

// #if !LONG_LATENCY_MODE
   #define RW_SMART_SEQ_SGATE_TIMEOUT_05                      0x04010094 // This error code is unreferenced.
// #endif
   #define RW_ASEEK_REQ_PULSE_SGATE_TIMEOUT                   0x04010095
   #define RW_SEQ_BVD_CHECK_TIMEOUT                           0x04010096

#if !SFT_FIRMWARE
   #define RW_SEQ_NRZ_XFR_DONE_TIMEOUT                        (0x04010097 | RW_RETRYABLE_ERR_TYPE )
#else
   #define RW_SEQ_NRZ_XFR_DONE_TIMEOUT                        0x04010097
#endif

   #define RW_SEQ_MEDIA_MGR_TIMEOUT                           (0x04010098 | RW_RETRYABLE_ERR_TYPE)
   #define RW_NRZ_XFR_MEDIA_MGR_ERR                           (0x04010099 | RW_RETRYABLE_ERR_TYPE)
   #define RW_DISC_SEQ_HANDSHAKE_ERR                          0x0401009A
   #define RW_MEDIUM_LATENCY_SYNC_ERR                         0x0401009B
   #define RW_SERVO_FAST_IO_MISSED_SAMPLE_ERR                 0x0401009C
   #define RW_MM_AASEEK_XFR_ERR                               (0x0401009D | RW_RETRYABLE_ERR_TYPE)
   #define RW_WAIT_FOR_NRZ_SEQUENCER_TIMEOUT                  0x0401009E
   #define RW_SEQUENCER_FAST_IO_SYNC_ERR                      0x0401009F
   #define RW_CHANNEL_NOT_READY_REV_COUNT_EXHAUSTED           (0x040100A0 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MM_AASEEK_SERVO_ERR                             (0x040100A1 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MM_AASEEK_DISC_PAUSE_CONDITION                  (0x040100A2 | RW_RETRYABLE_ERR_TYPE)
   #define RW_BERP_INFINITE_LOOP_TERMINATED                   0x040100A3

#if FE_0119973_400040_RW_BROWNOUT_DETECTION_SUPPORT_01
   #define RW_DISC_SEQ_BROWNOUT_DET                           (0x040100A4 | RW_RETRYABLE_ERR_TYPE)
#endif // #if FE_0119973_400040_RW_BROWNOUT_DETECTION_SUPPORT_01
#if INLINE_PARITY_SECTORS && RW_ENHANCED_INLINE_PARITY
   #define SEQ_NRZ_XFR_DONE_TIMEOUT_AT_REAS_SEC               (0x040100A5 | RW_RETRYABLE_ERR_TYPE)
#endif

   #define RW_SEQ_READ_START_SGATE_TIMEOUT                    0x040100A6
   #define RW_SEQ_READ_HDR_EXP_SGATE_TIMEOUT                  (0x040100A7 | RW_RETRYABLE_ERR_TYPE)

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/03 Errors.
   //***************************************************************************
   // 0x84030080: RW_DETECT_NEW_SERVO_FLAWS_FAILED - Detect of new servo flaws failed.
   // 0xC4030081: RW_BROWNOUT_FAULT - Disc Xfr - Brown-out(under voltage) detection fault.
   // 0xC4030082: RW_SHOCK_DETECT_FAULT - Disc Xfr - Shock event occurred.
   // 0xC4030083: RW_UEWG_FAULT - Disc Xfr - Unexpected Extended WGATE fault.
   // 0x84030084: RW_GATED_CHANNEL_FAULT - Disc Xfr - Channel detected fault during write.
   // 0x84030085: RW_DISC_LOCKED_CLOCK_FAULT - Disc Xfr - Disc Locked Clock fault detected.
   // 0xC4030086: RW_SWD_DVGAS_FAULT - Disc Xfr - Skip Write Detect Dvgas fault.
   // 0xC4030087: RW_SWD_RVGAS_FAULT - Disc Xfr - Skip Write Detect Rvgas fault.
   // 0xC4030088: RW_SWD_FVGAS_FAULT - Disc Xfr - Skip Write Detect Fvgas fault.
   //
   // The following indicate that the  Sum Threshold was exceeded and the
   // name indicates what the last SWD fault that occured was...
   //
   // 0xC4030089: RW_SWD_DVGAS_SUM_FAULT - Disc Xfr - Skip Write Detect Dvgas fault.
   // 0xC403008A: RW_SWD_RVGAS_SUM_FAULT - Disc Xfr - Skip Write Detect Rvgas fault.
   // 0xC403008B: RW_SWD_FVGAS_SUM_FAULT - Disc Xfr - Skip Write Detect Fvgas fault.
   // 0xC403008C: RW_DRIVE_FREE_FALL_EVENT_FAULT - Disc Xfr - Drive free-fall event occurred.
   // 0xC403008D: RW_LARGE_SHOCK_EVENT_FAULT - Disc Xfr - Large Shock event occured.
   // 0xC403008E: RW_OP_SHOCK_EVENT_FAULT - Disc Xfr - Op Shock event occured.
   // 0xC4030090: RW_WRITE_NRZ_PARITY_FAULT - Disc Xfr - NRZ Write Parity fault.
   // 0xC4030091: RW_TBG_UNLOCK_FAULT - Disc Xfr - Marvell 8830 TBG Unlock fault.
   // 0xC4030092: RW_WCLK_LOSS_FAULT - Disc Xfr - Marvell 8830 WClk Loss fault.
   // 0xC4030093: RW_EFD_WRITE_CONTACT_FAULT - Disc Xfr - EBMS Fault Detect(EFD) Contact fault during write.
   // 0xC4030094: RW_EFD_READ_CONTACT_FAULT  - Disc Xfr - EBMS Fault Detect(EFD) Contact fault during read.
   // 0xC4030095: RW_EFD_SWOT_FAULT          - Disc Xfr - EBMS Fault Detect(EFD) SWOT fault.
   // 0xC4030096: RW_SFG_UNLOCK_FAULT - Disc Xfr - SRC Marvell SFG Unlock fault.
   // 0xC4030097: RW_SERVO_DETECTED_LSI_HEATER_LOGIC_ERROR - Servo detected LSI Preamp Heater Logic Error
   // 0xC4030098: RW_EXT_VREG_FAULT - Disc Xfr - External (channel) Voltage Regulator(Vcore2) fault.
   // 0xC4030099: RW_TBG_SFG_UNLOCK_FAULT - Disc Xfr - SRC Marvell both TBG and SFG Unlock faults.
   // 0xC403009A: RW_EFD_OPEN_DETCR_FAULT - Disc Xfr - EBMS Fault Detect(EFD) open DETCR fault.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_DETECT_NEW_SERVO_FLAWS_FAILED                   0x04030080
   #define RW_BROWNOUT_FAULT                                  (0x04030081 | RW_RETRYABLE_ERR_TYPE)
   #define RW_SHOCK_DETECT_FAULT                              (0x04030082 | RW_RETRYABLE_ERR_TYPE)
   #define RW_UEWG_FAULT                                      (0x04030083 | RW_RETRYABLE_ERR_TYPE)
   #define RW_GATED_CHANNEL_FAULT                             0x04030084
   #define RW_DISC_LOCKED_CLOCK_FAULT                         0x04030085

#if RW_SKIP_WRITE_DETECT
   #define RW_SWD_DVGAS_FAULT                                 (0x04030086 | RW_RETRYABLE_ERR_TYPE)
   #define RW_SWD_RVGAS_FAULT                                 (0x04030087 | RW_RETRYABLE_ERR_TYPE)
   #define RW_SWD_FVGAS_FAULT                                 (0x04030088 | RW_RETRYABLE_ERR_TYPE)
   // The following indicate that the  Sum Threshold was exceeded and the
   // name indicates what the last SWD fault that occured was...
   #define RW_SWD_DVGAS_SUM_FAULT                             (0x04030089 | RW_RETRYABLE_ERR_TYPE)
   #define RW_SWD_RVGAS_SUM_FAULT                             (0x0403008A | RW_RETRYABLE_ERR_TYPE)
   #define RW_SWD_FVGAS_SUM_FAULT                             (0x0403008B | RW_RETRYABLE_ERR_TYPE)
#endif
#if DRIVE_FREE_FALL_PROTECTION_SUPPORT
   #define RW_DRIVE_FREE_FALL_EVENT_FAULT                     (0x0403008C | RW_RETRYABLE_ERR_TYPE)
#endif
   #define RW_LARGE_SHOCK_EVENT_FAULT                         (0x0403008D | RW_RETRYABLE_ERR_TYPE)
   #define RW_OP_SHOCK_EVENT_FAULT                            (0x0403008E | RW_RETRYABLE_ERR_TYPE)
   #define RW_TILT_DROP_EVENT_FAULT                           (0x0403008F | RW_RETRYABLE_ERR_TYPE)
#if ( MARVELL_READ_CHANNEL || SRC_9210_M || SRC_MARVELL )
   #define RW_WRITE_NRZ_PARITY_FAULT                          (0x04030090 | RW_RETRYABLE_ERR_TYPE)
   #define RW_TBG_UNLOCK_FAULT                                (0x04030091 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_WCLK_LOSS_FAULT                                 (0x04030092 | RW_CONDITIONAL_RETRY_OPTION)
#endif
#if RW_CONTACT_FAULT_DETECTION
   #define RW_EFD_WRITE_CONTACT_FAULT                         (0x04030093 | RW_RETRYABLE_ERR_TYPE)
   #define RW_EFD_READ_CONTACT_FAULT                          (0x04030094 | RW_RETRYABLE_ERR_TYPE)
   #define RW_EFD_SWOT_FAULT                                  (0x04030095 | RW_RETRYABLE_ERR_TYPE)
#endif
#if SRC_MARVELL
   #define RW_SFG_UNLOCK_FAULT                                (0x04030096 | RW_CONDITIONAL_RETRY_OPTION)
#endif
#if HWWA_0184623_403313_LSI2935_WEAK_WRITE_ISSUE
   // Originally this error code was 0x040300FF.
   #define RW_SERVO_DETECTED_LSI_HEATER_LOGIC_ERROR           (0x04030097 | RW_RETRYABLE_ERR_TYPE)
#endif
   #define RW_EXT_VREG_FAULT                                  (0x04030098 | RW_RETRYABLE_ERR_TYPE)
#if SRC_MARVELL
   #define RW_TBG_SFG_UNLOCK_FAULT                            (0x04030099 | RW_CONDITIONAL_RETRY_OPTION)
#endif
#if RW_CONTACT_FAULT_DETECTION
   #define RW_EFD_OPEN_DETCR_FAULT                            (0x0403009A | RW_RETRYABLE_ERR_TYPE)
#endif

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/09 Errors.
   //***************************************************************************
   // 0xC4090080: RW_SERVO_FAULT - Servo fault.
   // 0xC4090081: RW_WRITE_SERVO_UNSAFE_FAULT - Disc Xfr - Write during servo unsafe fault.
   // 0xC4090082: RW_EDAC_BLK_ADDR_ERR - Disc Xfr - EDAC block address error.
   // 0xC4090083: RW_SERVO_MDW_INFO_MISSING - Disc Xfr - Missing MDW information reported by servo detected.
   // 0xC4090084: RW_SERVO_CMD_TIMED_OUT - Servo command timed out.
   // 0xC4090085: RW_SEEK_TIMED_OUT - Seek operation timed out.
   // 0xC4090086: RW_SEEK_EXCEED_TIME_LIMIT - Seek operation has exceeded the recovery time limit
   // 0xC4090087: RW_SERVICE_DRIVE_FREE_FALL_CONDITION_TIMED_OUT - Servicing of free-fall condition timed out.
   // 0xC4090088: RW_SERVO_PRESSURE_UNSAFE_FAULT - The altitude has exceeded the limit.
   // 0xC409008A: RW_SUPER_BLK_MARKED_DIRTY - Super block has been marked dirty.
   // 0xC409008B: RW_SUPER_BLK_DATA_VERIFY_FAILED - Verify of super block data failed.
   // 0xC409008C: RW_SERVO_FATAL_ERROR_INDICATED - Servo has set the fatal error indication in seek cmd return parameters
   // 0xC409008D: RW_SUPER_PARITY_LONGWORD_XCHK_ERROR - Super parity crosscheck error (longword).
   // 0xC409008E: RW_SUPER_PARITY_LOW_WORD_XCHK_ERROR - Super parity crosscheck error (low 32-bits word).
   // 0xC409008F: RW_SUPER_PARITY_HIGH_WORD_XCHK_ERROR - Super parity crosscheck error (high 32-bits word).
   // 0xC4090090: RW_SUPER_PARITY_DATA_MISCOMPARE - Super parity data mis-compare error.
   // 0x84090091: RW_ATS_COMMANDED_SEEK_INVALID - A client commanded an ATS seek but conditions do not allow it.
   // 0x84090092: RW_ESP_REGENERATION_FAILED - Enhance Super parity regeneration failure.
   // 0x84090093: RW_REGENERATION_FAILED - Super parity regeneration failure.
   // 0x84090094: RW_FWIOC_OC_DECODER_TIMEOUT - FWIOC processing phase Reed-Solomon decoding timeout.
   // 0x84090095: RW_FWIOC_OC_DECODER_FAILED - FWIOC procesing phase Reed-Solomon decoding failure.
   // 0x84090096: RW_FWIOC_PREREAD_SAB_NOT_LOADED - FWIOC pre-read phase all sector equalized sample unavailable.
   // 0x84090097: RW_FWIOC_PREREAD_RECOVERY_TIME_EXCEEDED - Error recovery time exceeded during FWIOC pre-read.
   // 0x84090098: RW_FWIOC_PROCESSING_RECOVERY_TIME_EXCEEDED - Error recovery time exceeded during FWIOC processing.
   // 0x04090099: RW_FWIOC_FAILED_ON_SYNC_MARK_ERROR - Exit FWIOC due to sectors with sync mark error

   //</RW_SENSE_ERROR_CODES>

   #define RW_SERVO_FAULT                                     (0x04090080 | RW_RETRYABLE_ERR_TYPE)
   #define RW_WRITE_SERVO_UNSAFE_FAULT                        (0x04090081 | RW_RETRYABLE_ERR_TYPE)
   #define RW_EDAC_BLK_ADDR_ERR                               (0x04090082 | RW_RETRYABLE_ERR_TYPE)
   #define RW_SERVO_MDW_INFO_MISSING                          (0x04090083 | RW_RETRYABLE_ERR_TYPE)
   #define RW_SERVO_CMD_TIMED_OUT                             (0x04090084 | RW_RETRYABLE_ERR_TYPE)
   #define RW_SEEK_TIMED_OUT                                  (0x04090085 | RW_RETRYABLE_ERR_TYPE)
   #define RW_SEEK_EXCEED_TIME_LIMIT                          (0x04090086 | RW_RETRYABLE_ERR_TYPE)

#if DRIVE_FREE_FALL_PROTECTION_SUPPORT
   #define RW_SERVICE_DRIVE_FREE_FALL_CONDITION_TIMED_OUT     (0x04090087 | RW_RETRYABLE_ERR_TYPE)
#endif
#if PRESSURE_SENSOR_SUPPORT
   #define RW_SERVO_PRESSURE_UNSAFE_FAULT                     0x04090088
#endif
#if FE_0123426_387179_DUAL_STAGE_SEEK_RECOVERY
   #define RW_SERVO_PZT_FAULT                                 (0x04090089 | RW_RETRYABLE_ERR_TYPE)
#endif
#if INLINE_PARITY_SECTORS
   #define RW_SUPER_BLK_MARKED_DIRTY                          0x0409008A
   #define RW_SUPER_BLK_DATA_VERIFY_FAILED                    0x0409008B
#endif
#if SERVO_FATAL_ERROR_NOTIFICATION
   #define RW_SERVO_FATAL_ERROR_INDICATED                     0x0409008C
#endif
#if INLINE_PARITY_DISC_READ_SCAN
#if INLINE_PARITY_CROSSCHECK
   #define RW_SUPER_PARITY_LONGWORD_XCHK_ERROR                0x0409008D
   #define RW_SUPER_PARITY_LOW_WORD_XCHK_ERROR                0x0409008E
   #define RW_SUPER_PARITY_HIGH_WORD_XCHK_ERROR               0x0409008F
#else
   #define RW_SUPER_PARITY_DATA_MISCOMPARE                    0x04090090
#endif
#endif

   #define RW_ATS_COMMANDED_SEEK_INVALID                      0x04090091

#if RW_ENHANCED_INLINE_PARITY
   #define RW_ESP_REGENERATION_FAILED                         0x04090092
#endif
   #define RW_REGENERATION_FAILED                             0x04090093

#if RW_FWIOC_ERROR_RECOVERY
   #define RW_FWIOC_OC_DECODER_TIMEOUT                        0x04090094
   #define RW_FWIOC_OC_DECODER_FAILED                         0x04090095
   #define RW_FWIOC_PREREAD_SAB_NOT_LOADED                    0x04090096
   #define RW_FWIOC_PREREAD_RECOVERY_TIME_EXCEEDED            0x04090097
   #define RW_FWIOC_PROCESSING_RECOVERY_TIME_EXCEEDED         0x04090098
   #define RW_FWIOC_FAILED_ON_SYNC_MARK_ERROR                 0x04090099 // Exit FWIOC due to sectors with sync mark error

//#if ( FE_FWIOC_EXIT_ON_SYNC_MARK_ERROR_WA1 && ( FWIOC_FIX_ENHANCE_CODE_BATCH >= 1 ) )
   #define RW_FWIOC_FAILED_ON_SYNC_MARK_ERROR_PLUS_MULTIPLE_FAILED_SECTORS    0x0409009A // Exit FWIOC due to sectors with sync mark error
//#endif
#endif

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/11 Errors.
   //***************************************************************************
   // 0xC4110080: RW_INTERNAL_DATA_PATH_ERR - Disc Xfr - Read data has EDAC error but LDPC convergence, eg LDPC miscorrection.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_INTERNAL_DATA_PATH_ERR                          (0x04110080 | RW_RETRYABLE_ERR_TYPE)

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/15 Errors.
   //***************************************************************************
   // 0x84150180: RW_SERVO_SPINUP_FAILED - Spinup - Servo error encountered during drive spin-up.
   // 0x84150181: RW_SERVO_SPINDOWN_FAILED - Spindown - Servo error encountered during drive spin-up.
   // 0x84150182: RW_SPINDLE_FAILED - Spindle state doesn't allow reliable actuator operations.
   //           :                     This usually happens after unrecoverable servo operations.
   // 0x84150183: RW_UNRECOVERED_SEEK - Unrecovered seek error encountered (Error is unretryable).
   // 0xC4150183: RW_UNRECOVERED_SEEK - Unrecovered seek error encountered (Error is retryable).
   // 0x84150184: RW_SERVO_CMD_FAILED - Servo command failed.
   // 0xC4150185: RW_HEATER_CONTROL_FAILED - Servo heater timing failed.
   // 0x84150186: RW_SERVO_FREE_FALL_PROTECTION_CMD_FAILED - Servo Free-Fall Protection command failed.
   // 0x84150187: RW_SERVO_DISC_SLIP_FULL_TMFF_RECAL_FAILED - Servo Disc Slip Full TMFF recalibration failed.
   // 0x84150188: RW_SERVO_DISC_SLIP_HDSWITCH_TIMING_RECAL_FAILED - Servo Disc Slip Head Switch Timing recalibration failed.
   // 0x84150189: RW_SERVO_DISC_SLIP_HDSWITCH_TRACK_RECAL_FAILED - Servo Disc Slip Head Switch Track recalibration failed.
   // 0x8415018A: RW_SERVO_READ_HEAT_FAST_IO_FAILED - Servo read heat fast I/O command failed.
   // 0x8415018B: RW_G2P_MERGE_SPINUP_FAILED - Spin-up attempt during G2P merge process failed.
   // 0x8415018C: RW_PROCESS_USER_PLIST_SPINDOWN_FAILED - Spin-down attempt during PList processing failed.
   // 0x8415018D: RW_PROCESS_USER_PLIST_SPINUP_FAILED - Spin-up attempt during PList processing failed.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_SERVO_SPINUP_FAILED                                    0x04150180
   #define RW_SERVO_SPINDOWN_FAILED                                  0x04150181
   #define RW_SPINDLE_FAILED                                         0x04150182

#if RW_RETRIES_ON_UNRECOVERED_SEEK_ERRORS
   #define RW_UNRECOVERED_SEEK                                       (0x04150183 | RW_RETRYABLE_ERR_TYPE)
#else
   #define RW_UNRECOVERED_SEEK                                       0x04150183
#endif

   #define RW_SERVO_CMD_FAILED                                       0x04150184
   #define RW_HEATER_CONTROL_FAILED                                  (0x04150185 | RW_RETRYABLE_ERR_TYPE)

#if DRIVE_FREE_FALL_PROTECTION_SUPPORT
   #define RW_SERVO_FREE_FALL_PROTECTION_CMD_FAILED                  0x04150186
#endif
#if SERVO_DISC_SLIP_SUPPORT
   #define RW_SERVO_DISC_SLIP_FULL_TMFF_RECAL_FAILED                 0x04150187
   #define RW_SERVO_DISC_SLIP_HDSWITCH_TIMING_RECAL_FAILED           0x04150188
   #define RW_SERVO_DISC_SLIP_HDSWITCH_TRACK_RECAL_FAILED            0x04150189
#endif
#if RW_HEAT_ONLY_SEARCH
   #define RW_SERVO_READ_HEAT_FAST_IO_FAILED                         0x0415018A
#endif

#if DISC_SLIP_RECAL_AND_SAVE_TO_FLASH
   #define RW_SERVO_DISC_SLIP_RECAL_FAILED                           0x0415018B
#endif
   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/19 Errors.
   //***************************************************************************
   // 0x84190080: RW_FORMAT_RECOVER_SAVED_GROWN_DST_FAILED - Format - Recover of saved Grown DST file failed.
   // 0x84190081: RW_DEFECT_SCAN_INIT_DEFECT_LISTS_FAILED - Scan Defect - Recovery of saved Non-Resident DST failed.
   // 0x84190082: RW_CLEAR_SLIP_LIST_SAVE_RW_OPERATING_PARMS_FILE_FAILED - Clear R/W Slip List - Save of R/W Operating Parmaters file failed.
   // 0x84190083: RW_RESTORE_ALT_LIST_FILE_FROM_MEDIA_FAILED - Restore Alt List File From media - Failed restoration from media file.
   // 0x84190084: RW_SERVO_DISC_SLIP_PARMS_MEDIA_UPDATE_FAILED - Save of Servo Disc Slip Parms to media failed.
   // 0x84190085: RW_SERVO_DISC_SLIP_PARMS_MEDIA_READ_FAILED_01 - Read of Servo Disc Slip Parms from media failed.
   // 0x84190086: RW_SERVO_DISC_SLIP_PARMS_MEDIA_READ_FAILED_02 - Read of Servo Disc Slip Parms from media failed.
   // 0x84190087: RW_SERVO_DISC_SLIP_FILE_INVALID_FORMAT_REVISION - Servo Disc Slip file - invalid format revision.
   // 0x84190088: RW_GLIST_TO_PLIST_RECOVER_SAVED_GROWN_DST_FAILED - GList to PList - Recover of saved Grown DST file failed.
   // 0x84190089: RW_CLEAR_NON_RESIDENT_GROWN_DST_SAVE_TO_MEDIA_FAILED - Clear Non-resident Grown DST - Save to media failed.
   // 0x8419008A: RW_UNDO_TORN_WRITE_PROTECTION_SAVE_SYS_FILES_FAILED - Undo Torn Write Protection Reallocation - Saving of system files failed.
   // 0x8419008B: RW_UNDO_TORN_WRITE_PROTECTION_SERVO_FREE_FALL_FAILED - Undo Torn Write Protection Reallocation - Failed due to servo free fall condition.
   // 0x8419008C: RW_TORN_WRITE_PROTECTION_REAL_SERVO_FREE_FALL_FAILED - Torn Write Protection Reallocation - Failed due to servo free fall condition.
   // 0x8419008D: RW_CLEAR_SERVO_FLAW_LIST_SAVE_RW_OPERATING_PARMS_FILE_FAILED - Clear servo flaw List - Save of R/W Operating Parmaters file failed.
   // 0x8419008E: RW_FORMAT_RECOVER_RES_TEST_TRACKS_FAILED  - Format - Recover of Reserved Test Tracks Table failed.
   // 0x8419008F: RW_SERVO_DISC_SLIP_INSUFFICIENT_DIAG_BUFFER - Servo Disc Slip file - Unable to retrieve from Flash due to insufficient diag retrieval buffer space
   // 0x84190090: RW_FORMAT_VALID_PBA_FOR_MEDIA_CACHE_INSUFFICIENT  - Format - Require that the valid PBA in media cache partition should be larger than required media cache size
   //</RW_SENSE_ERROR_CODES>

   #define RW_FORMAT_RECOVER_SAVED_GROWN_DST_FAILED                  0x04190080

#if (DSTEST_ATA || ENHANCED_DST || DSTEST_SCSI)
   #define RW_DEFECT_SCAN_INIT_DEFECT_LISTS_FAILED                   0x04190081
#endif
#if F3_CERT_AND_DIAG
   #define RW_CLEAR_SLIP_LIST_SAVE_RW_OPERATING_PARMS_FILE_FAILED    0x04190082
   #define RW_RESTORE_ALT_LIST_FILE_FROM_MEDIA_FAILED                0x04190083
#endif
#if SERVO_DISC_SLIP_SUPPORT
   #define RW_SERVO_DISC_SLIP_PARMS_MEDIA_UPDATE_FAILED              0x04190084
   #define RW_SERVO_DISC_SLIP_PARMS_MEDIA_READ_FAILED_01             0x04190085
   #define RW_SERVO_DISC_SLIP_PARMS_MEDIA_READ_FAILED_02             0x04190086
   #define RW_SERVO_DISC_SLIP_FILE_INVALID_FORMAT_REVISION           0x04190087
#endif
#if F3_CERT_AND_DIAG
   #define RW_CLEAR_NON_RESIDENT_GROWN_DST_SAVE_TO_MEDIA_FAILED      0x04190089
#endif
#if F3_CERT_AND_DIAG
   #define RW_CLEAR_SERVO_FLAW_LIST_SAVE_RW_OPERATING_PARMS_FILE_FAILED 0x0419008D
#endif
#if FE_0211939_379594_H2SAT_SUPPORT
   #define RW_FORMAT_RECOVER_RES_TEST_TRACKS_FAILED                  0x0419008E
#endif
#if FE_0206180_514397_STORE_SERVO_DISC_SLIP_INFO_IN_FLASH
   #define RW_SERVO_DISC_SLIP_INSUFFICIENT_DIAG_BUFFER               0x8419008F
#endif
#if RW_MEDIA_CACHE_PARTITION_SUPPORT
   #define RW_FORMAT_VALID_PBA_FOR_MEDIA_CACHE_INSUFFICIENT          0x84190090
#endif

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/1C Errors.
   //***************************************************************************
   // 0x841C0081: RW_READ_PRIMARY_DEFECT_LISTS_SUPER_FILE_FOR_REPORTING - Format - Failure to read Primary Defect Lists Super file for reporting.
   // 0x841C0082: RW_PLIST_FILE_INVALID_ENTRY_CNT_01 - Format - Invalid entry count in Plist file.
   // 0x841C0083: RW_PLIST_ENTRY_INVALID_SYMBOL_EXTENT - Format - Invalid symbol extent value in Plist entry.
   // 0x841C0084: RW_PRIMARY_DEFECT_LIST_INVALID_OFFSET_SORT - Process Defect Lists - Sort error due to invalid offset.
   // 0x841C0085: RW_PRIMARY_DEFECT_LIST_INVALID_HEAD_SORT - Process Defect Lists - Sort error due to invalid head.
   // 0x841C0086: RW_PRIMARY_DEFECT_LIST_INVALID_CYL_SORT - Process Defect Lists - Sort error due to invalid cylinder.
   // 0x841C0087: RW_PRIMARY_DEFECT_FILES_UNRECOVERABLE - Process Defect Lists - Unable to recover the Primary Defect files.
   // 0x841C0088: RW_REASSIGN_SEEK_TO_DEFECT_FILES_FAILED - Reallocate Block - Failed to seek to defect files for reassign.
   // 0x841C0089: RW_UNDO_REASSIGN_SEEK_TO_DEFECT_FILES_FAILED - Reallocate Block - Failed to seek to defect files for undo-reassign.
   // 0x841C008A: RW_WRITE_SAVED_DEFECTS_REPORT_LISTS_FILE_FAILED - Format - Failure to write defects report lists file to media.
   // 0x841C008B: RW_READ_SAVED_DEFECTS_REPORT_LISTS_FILE_FAILED - Retrieve Defects Report List - Read of defects report file from media failed.
   // 0x841C008C: RW_SAVED_DEFECTS_REPORT_LISTS_DISC_FILE_INVALID_01 - Retrieve Defects Report List - An invalid defects report file is encountered.
   // 0x841C008D: RW_SAVED_DEFECTS_REPORT_LISTS_DISC_FILE_INVALID_02 - Retrieve Defects Report List - An invalid defects report file is encountered.
   // 0x841C008E: RW_FORMAT_RESTORE_RW_OPERATING_PARMS_FILE_FAILED - Format - Restore of R/W User Operating Parameters file failed.
   // 0x841C008F: RW_FORMAT_INVALID_PRIMARY_SERVO_FLAWS_DATA - Format - Invalid Primary Servo Flaws data encountered.
   // 0x841C0090: RW_SAVE_DEFECT_FILES_FAILED_DUE_TO_DATA_MISCOMPARE_ERR - Reallocate Block - Failed to save defect files due to miscompare error.
   // 0x841C0092: RW_PRIMARY_DEFECT_LIST_FILE_OVERFLOW_01 - Format - PList overflow error while merging PSFT and PList for reporting.
   // 0x841C0093: RW_FORMAT_MAX_ZONE_RECERTIFY_PASSES_EXCEEDED - Format - maximum certify passes of a zone exceeded.
   // 0x841C0094: RW_FORMAT_MAX_ZONE_REWRITE_PASSES_EXCEEDED - Format - maximum write passes of a zone exceeded.
   // 0x841C0095: RW_PRIMARY_SERVO_FLAWS_LIST_UNRECOVERABLE - Primary Servo Flaws data retrieval - Unable to read file on disc.
   // 0x841C0096: RW_PRIMARY_FLAWS_FILE_INVALID_ENTRY_CNT - Primary Servo Flaws data retrieval - Invalid entry count in file.
   // 0x841C0097: RW_DEFECTIVE_SECTORS_LIST_UNRECOVERABLE - Defective Sectors List data retrieval - Unable to read file on disc.
   // 0x841C0098: RW_DEFECTIVE_SECTORS_LIST_INVALID_FILE_HEADER - Defective Sectors List data retrieval - Invalid file header data.
   // 0x841C0099: RW_PLIST_FILE_INVALID_ENTRY_CNT_02 - PList data retrieval - Invalid entry count in Plist file.
   // 0x841C009A: RW_PRIMARY_DEFECTS_LIST_UNRECOVERABLE - PList data retrieval - Unable to read Plist file on disc.
   // 0x841C009B: RW_SYSTEM_FORMAT_CLIENT_LIST_INVALID_ENTRY_CNT - System Format - invalid entry count.
   // 0x841C009C: RW_PRIMARY_TA_LIST_UNRECOVERABLE - Primary TA data retrieval - Unable to read file on disc.
   // 0x841C009D: RW_PRIMARY_TA_LIST_INVALID_COUNT - Primary TA data retrieval - Invalid count.
   // 0x841C009E: RW_PRIMARY_TA_LIST_INVALID_SORT - Primary TA data retrieval - Invalid sort.
   // 0x841C009F: RW_CLIENT_DEFECT_LIST_ENTRY_NOT_IN_AUDIT_SPACE - Process Defect Lists - Defect doesn't exist in audit space.
   // 0x841C00A0: RW_SAVED_DEFECTS_REPORT_LISTS_ALL_ENTRIES_NOT_VALID - Retrieve Defects Report List - Not All Entries Available
   // 0x841C00A1: RW_FORMAT_UPDATE_DIRTY_SUPER_BLKS_INVALID_USER_LBA_RANGE - Format - Invalid user LBA range reported by the Parity Validity Table before update of dirty blocks.
   // 0x841C00A2: RW_FORMAT_UPDATE_DIRTY_SUPER_BLKS_INVALID_PARITY_TBL - Format - Invalid Parity Validity Table after clean of dirty blocks.
   // 0x841C00A3: RW_FORMAT_UPDATE_DIRTY_SUPER_BLKS_FAILED - Format - Clean of dirty blocks failed.
   // 0x841C00A4: RW_FORMAT_SAVE_PARITY_VALID_TBL_FAILED - Format - Save of Parity Validity Table to media failed.
   // 0x841C00A5: RW_DEFECTS_REPORT_LISTS_CANT_ADD_GROWN_DEFECT - Format - The Defects Report Lists is out of space, and can not encompass new grown defects.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_READ_PRIMARY_DEFECT_LISTS_SUPER_FILE_FOR_REPORTING     0x041C0081
   #define RW_PLIST_FILE_INVALID_ENTRY_CNT_01                        0x041C0082
   #define RW_PLIST_ENTRY_INVALID_SYMBOL_EXTENT                      0x041C0083
   #define RW_PRIMARY_DEFECT_LIST_INVALID_OFFSET_SORT                0x041C0084
   #define RW_PRIMARY_DEFECT_LIST_INVALID_HEAD_SORT                  0x041C0085
   #define RW_PRIMARY_DEFECT_LIST_INVALID_CYL_SORT                   0x041C0086
   #define RW_PRIMARY_DEFECT_FILES_UNRECOVERABLE                     0x041C0087
   #define RW_REASSIGN_SEEK_TO_DEFECT_FILES_FAILED                   0x041C0088
   #define RW_UNDO_REASSIGN_SEEK_TO_DEFECT_FILES_FAILED              0x041C0089
   #define RW_WRITE_SAVED_DEFECTS_REPORT_LISTS_FILE_FAILED           0x041C008A
   #define RW_READ_SAVED_DEFECTS_REPORT_LISTS_FILE_FAILED            0x041C008B
   #define RW_SAVED_DEFECTS_REPORT_LISTS_DISC_FILE_INVALID_01        0x041C008C
   #define RW_SAVED_DEFECTS_REPORT_LISTS_DISC_FILE_INVALID_02        0x041C008D
   #define RW_FORMAT_RESTORE_RW_OPERATING_PARMS_FILE_FAILED          0x041C008E
   #define RW_FORMAT_INVALID_PRIMARY_SERVO_FLAWS_DATA                0x041C008F
   #define RW_SAVE_DEFECT_FILES_FAILED_DUE_TO_DATA_MISCOMPARE_ERR    0x041C0090
   #define RW_PRIMARY_DEFECT_LIST_FILE_OVERFLOW_01                   0x041C0092
   #define RW_FORMAT_MAX_ZONE_RECERTIFY_PASSES_EXCEEDED              0x041C0093
   #define RW_FORMAT_MAX_ZONE_REWRITE_PASSES_EXCEEDED                0x041C0094
   #define RW_PRIMARY_SERVO_FLAWS_LIST_UNRECOVERABLE                 0x041C0095
   #define RW_PRIMARY_FLAWS_FILE_INVALID_ENTRY_CNT                   0x041C0096
   #define RW_DEFECTIVE_SECTORS_LIST_UNRECOVERABLE                   0x041C0097
   #define RW_DEFECTIVE_SECTORS_LIST_INVALID_FILE_HEADER             0x041C0098
   #define RW_PLIST_FILE_INVALID_ENTRY_CNT_02                        0x041C0099
   #define RW_PRIMARY_DEFECTS_LIST_UNRECOVERABLE                     0x041C009A
   #define RW_SYSTEM_FORMAT_CLIENT_LIST_INVALID_ENTRY_CNT            0x041C009B
   #define RW_PRIMARY_TA_LIST_UNRECOVERABLE                          0x041C009C
   #define RW_PRIMARY_TA_LIST_INVALID_COUNT                          0x041C009D
   #define RW_PRIMARY_TA_LIST_INVALID_SORT                           0x041C009E
   #define RW_CLIENT_DEFECT_LIST_ENTRY_NOT_IN_AUDIT_SPACE            0x041C009F
   #define RW_SAVED_DEFECTS_REPORT_LISTS_ALL_ENTRIES_NOT_VALID       0x041C00A0

#if INLINE_PARITY_SECTORS
   #define RW_FORMAT_UPDATE_DIRTY_SUPER_BLKS_INVALID_USER_LBA_RANGE  0x041C00A1
   #define RW_FORMAT_UPDATE_DIRTY_SUPER_BLKS_INVALID_PARITY_TBL      0x041C00A2
   #define RW_FORMAT_UPDATE_DIRTY_SUPER_BLKS_FAILED                  0x041C00A3
   #define RW_FORMAT_SAVE_PARITY_VALID_TBL_FAILED                    0x041C00A4
#endif

   #define RW_DEFECTS_REPORT_LISTS_CANT_ADD_GROWN_DEFECT             0x041C00A5

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/32/00 Errors.
   //***************************************************************************
   // 0x84320080: RW_PROCESS_FORMAT_PENDING_REALLOCATION_FAILED - Format - Processing of pending reallocation failed.
   // 0x84320081: RW_INSERT_DST_FAILED - Format - Failed to insert defect to DST.
   // 0x84320082: RW_DST_INSERT_PLIST_DEFECTS_FAILED - Format - Failed to insert PList defect to DST.
   // 0x84320083: RW_GROWN_DST_FULL_01 - Format - Grown DST file full.
   // 0x84320084: RW_GROWN_DST_FULL_02 - Format - Grown DST file full.
   // 0x84320085: RW_RESIDENT_DST_FULL - Format - Resident DST file full.
   // 0x84320086: RW_INSERT_FORMAT_GROWN_FLAW_DEFECTS_FAILED - Format - Failed to insert defective sectors assoicated w/grown servo flaw.
   // 0x84320088: RW_INSERT_SYSTEM_FLAW_DEFECTS_FAILED - Format System Partition - Failed to insert defective system sectors associated w/ grown servo flaw.
   // 0x8432008A: RW_SYSTEM_DEFECTS_FILE_FULL - Format System Parition - System Defects file full.
   // 0x8432008B: RW_CLIENT_DEFECT_INSERT_IN_DEFECT_LIST_ERR - Process Defect Lists - Failed to insert a client specified defect in the defect file.
   // 0x8432008C: RW_ASFT_MAX_FLAWS_PER_TRK_EXCEEDED_01 - ASFT - Max # of servo flaws per track exceeded (path #1).
   // 0x8432008D: RW_ASFT_MAX_FLAWS_PER_TRK_EXCEEDED_02 - ASFT - Max # of servo flaws per track exceeded (path #2).
   // 0x8432008E: RW_ASFT_FULL_01 - Defect Management - ASFT full (path #1).
   // 0x8432008F: RW_ASFT_FULL_02 - Defect Management - ASFT full (path #2).
   // 0x84320090: RW_ADD_PENDING_REAS_LBA_FAILED - Defect Management - Addition to Reassign Pending List failed.
   // 0x84320091: RW_INITIAL_REALLOCATION_NOT_ALLOWED - Reallocate Block - Resource is not available for a new reallocation.
   // 0x84320092: RW_ALTERNATE_NOT_AVAILABLE - Reallocate Block - No alternates available.
   // 0x84320093: RW_INSERT_POST_FORMAT_GROWN_FLAW_DEFECTS_FAILED - Reallocate Block - Failed to insert defective sectors associated w/grown servo flaw.
   // 0x84320094: RW_INSERT_COMPROMISED_DEFECTS_FAILED - Format - Failed to deallocate compromised defects.
   // 0x84320095: RW_INSERT_SYSTEM_COMPROMISED_DEFECTS_FAILED - Format System Partition - Failed to deallocate compromised.
   // 0x84320096: RW_DDT_INSERT_ENTRY_FAILED - Insertion of DDT entry failed.
   // 0x84320097: RW_CDDT_FILE_FULL - Compressed DDT file full.
   // 0x84320098: RW_INSERT_FORMAT_PRIMARY_FLAW_DEFECTS_FAILED - Format - Failed to insert defective sectors associated w/primary servo flaw.
   // 0x84320099: RW_DEFECTIVE_TRACKS_INSERT_GROWN_DEFECTS_FAILED - Defective Tracks List - Failed to insert grown defective sectors associated w/defective track.
   // 0x8432009A: RW_DEFECTIVE_TRACKS_INSERT_PRIMARY_DEFECTS_FAILED - Defective Tracks List - Failed to insert primary defective sectors associated w/defective track.
   // 0x8432009B: RW_DEFECTIVE_TRACKS_LIST_FULL - Defective Tracks List - Failed to add new entry to list.
   // 0x8432009D: RW_PARTIAL_REALLOCATION_NOT_ALLOWED - Reallocate Block - Resource is not available for a partial reallocation.
   // 0x8432009E: RW_BIPS_ALLOCATION_NOT_ALLOWED - BIPS - Not enough non-defective sectors to allocate for BIPS parity Sectors.
   // 0x8432009F: RW_BIPS_DDT_OPERATION_FAILED_01 - BIPS - BIPS defect DDT table operation failed.
   // 0x843200A0: RW_BIPS_DDT_OPERATION_FAILED_02 - BIPS - BIPS defect DDT table operation failed.
   // 0x843200A1: RW_DEALLOCATE_TRACK_INSERT_DST_FAILED - Format - Failed to add defective track to DST.
   // 0x843200A2: RW_ALTERNATE_NOT_AVAILABLE_02 - Format - Failed to allocate spare sectors.
   // 0x843200A3: RW_DEFECTS_PAD_FILL_MAX_NUM_SKIPPED_TRACKS_EXCEEDED - Pad/Fill Defects - # of skipped tracks exceed maximum allowed.
   // 0x843200A4: RW_ALTERNATE_NOT_AVAILABLE_03 - Format - Failed to allocate spare sectors.
   // 0x843200A5: RW_INSUFFICIENT_PBAS_FOR_REQUIRED_LBAS - Format - More LBAs than PBAs.
   // 0x843200A6: RW_ALTERNATE_NOT_AVAILABLE_04 - Format - Failed to allocate spare sectors.
   // 0x843200A7: RW_ALTERNATE_NOT_AVAILABLE_05 - Format - Failed to allocate spare sectors.
   // 0x843200A8: RW_ALTERNATE_NOT_AVAILABLE_06 - Format - Failed to allocate spare sectors.
   // 0x843200A9: RW_DDT_MAX_SLIP_EXCEEDED - Format - Excessive number of slips not supported by hardware.
   // 0x843200AA: RW_REALLOCATE_WITH_INVALID_HW_PARITY_DATA - Reallocation - Invalid HW parity data for reallocation of parity sectors.
   // 0x843200AB: RW_MEDIA_CACHE_PAD_PROTECT_USER_DATA_FAILED - Adding Guard band padding betwen user and media cache region failed.
   // 0x843200AC: RW_FEATURE_METADATA_BUDGET_WILL_BE_INCORRECT_AFTER_FORMAT - MC/ISP - Will not be able to save metadata after this format
   // 0x843200AD: RW_ALTERNATE_NOT_AVAILABLE_07 - Format - Failed to allocate spare sectors.
   // 0x843200AE: RW_ALTERNATE_NOT_AVAILABLE_08 - Format - Failed to allocate spare sectors.
   // 0x843200AF: RW_ALTERNATE_NOT_AVAILABLE_09 - Format - Failed to allocate spare sectors.
   // 0x843200B0: RW_ALTERNATE_NOT_AVAILABLE_0A - Format - Failed to allocate spare sectors.
   // 0x843200B1: RW_PARITY_SECS_SLIP_LIST_UPDATE_FAILED - Format - Failed to update parity sectors slip list.
   // 0x843200B2: RW_INVALID_TRACK_SECTOR_RANGE_01 - Format - Invalid track sector range encountered.
   // 0x843200B3: RW_INTERMEDIATE_SUPER_PARITY_MEDIA_CACHE_PAD_FAILED - Format - Intermediate super parity media cache pad failed.
   // 0x043200B4: RW_MEDIA_CACHE_DDT_VERIFICATION_FAILED - MC starting DDT entry not found.
   // 0x843200B5: RW_ALTERNATE_NOT_AVAILABLE_0B - Format - Failed to allocate spare sectors.
   // 0x843200B6: RW_ALTERNATE_NOT_AVAILABLE_0C - Format - Failed to allocate spare sectors during zone skipping.
   // 0x843200B7: RW_INVALID_ISO_BASED_PARITY_SUPER_BLK_SIZE - Format - ISO-Based super parity config size is invalid.
   // 0x843200B8: RW_ISO_BAND_ALIGNMENT_INSERT_PADDED_DEFECTS_FAILED - Format - Failed to insert padded defects for aligning ISO bands boundary.
   // 0x043200B9: RW_ISO_BAND_ALIGNMENT_TRK_ATTRIBUTES_CALC_FAILED - Format - Track attributes calculation failed during process of aligning ISO bands boundary.
   // 0x043200BA: RW_ISO_BAND_ALIGNMENT_TRK_LBA_RANGE_CALC_FAILED - Format - Track LBA range calculation failed during process of aligning ISO bands boundary.
   // 0x043200BB: RW_ISO_BAND_ALIGNMENT_PADDED_PBA_RANGE_INVALID - Format - Invalid padded PBA range found during process of aligning ISO bands boundary.
   // 0x043200BC: RW_ISO_BAND_ALIGNMENT_VERIFY_BAND_BOUNDARIES_FAILED - Format - Verification of ISO band boundaries failed.
   // 0x043200BD: RW_ISO_BAND_ALIGNMENT_START_WEDGE_TO_SECS_CALC_FAILED_01 - Format - Start wedge to Sectors calculation failed during alignment of ISO bands boundary.
   // 0x043200BE: RW_ISO_BAND_ALIGNMENT_START_WEDGE_TO_SECS_CALC_FAILED_02 - Format - Start wedge to Sectors calculation failed during alignment of ISO bands boundary.
   // 0x043200BF: RW_ISO_BAND_ALIGNMENT_END_WEDGE_TO_SECS_CALC_FAILED_01 - Format - End wedge to Sectors calculation failed during alignment of ISO bands boundary.
   // 0x043200C0: RW_ISO_BAND_ALIGNMENT_END_WEDGE_TO_SECS_CALC_FAILED_02 - Format - End wedge to Sectors calculation failed during alignment of ISO bands boundary.
   // 0x843200C1: RW_DIST_MEDIA_CACHE_PAD_PROTECT_USER_DATA_FAILED - Adding Guard band padding betwen user and distributed media cache region failed.
   // 0x043200C2: RW_FORMAT_USER_PARTITION_END_SUPER_BLK_INFO_CALC_FAILED - Format - Failed to calculate end User partition super block information.
   // 0x043200C3: RW_ADD_OVERLAY_MC_ZONE_GROUPS_PRIMARY_DEFECTS_FAILED - Format - Add primary defects for the overlay Media Cache zone groups failed.
   // 0x043200C4: RW_ADD_OVERLAY_MC_ZONE_GROUP_GROWN_DEFECTS_FAILED - Format - Add grown defects for the overlay Media Cache zone group failed.
   // 0x043200C5: RW_NON_OVERLAY_MC_ZONE_GROUPS_LBA_CAPACITY_NOT_MET - Format - LBA capacity of non-overlay Media Cache zone groups not met.
   // 0x043200C6: RW_OVERLAY_MC_ZONES_ALIGNMENT_ADD_PADDED_DEFECTS_FAILED - Format - Unable to add padded defects to align MC zones.
   // 0x043200C7: RW_ALTERNATE_NOT_AVAILABLE_IN_SFMT_MC_ZONES - Spare is not enough in MC zones during serial format.
   // 
   //</RW_SENSE_ERROR_CODES>

   #define RW_PROCESS_FORMAT_PENDING_REALLOCATION_FAILED             0x04320080
   #define RW_INSERT_DST_FAILED                                      0x04320081
   #define RW_DST_INSERT_PLIST_DEFECTS_FAILED                        0x04320082
   #define RW_GROWN_DST_FULL_01                                      0x04320083
   #define RW_GROWN_DST_FULL_02                                      0x04320084
   #define RW_RESIDENT_DST_FULL                                      0x04320085
   #define RW_INSERT_FORMAT_GROWN_FLAW_DEFECTS_FAILED                0x04320086
   #define RW_INSERT_SYSTEM_FLAW_DEFECTS_FAILED                      0x04320088
   #define RW_SYSTEM_DEFECTS_FILE_FULL                               0x0432008A
   #define RW_CLIENT_DEFECT_INSERT_IN_DEFECT_LIST_ERR                0x0432008B
   #define RW_ASFT_MAX_FLAWS_PER_TRK_EXCEEDED_01                     0x0432008C
   #define RW_ASFT_MAX_FLAWS_PER_TRK_EXCEEDED_02                     0x0432008D
   #define RW_ASFT_FULL_01                                           0x0432008E
   #define RW_ASFT_FULL_02                                           0x0432008F
   #define RW_ADD_PENDING_REAS_LBA_FAILED                            0x04320090
   #define RW_INITIAL_REALLOCATION_NOT_ALLOWED                       0x04320091
   #define RW_ALTERNATE_NOT_AVAILABLE                                0x04320092
   #define RW_INSERT_POST_FORMAT_GROWN_FLAW_DEFECTS_FAILED           0x04320093
   #define RW_INSERT_COMPROMISED_DEFECTS_FAILED                      0x04320094
   #define RW_INSERT_SYSTEM_COMPROMISED_DEFECTS_FAILED               0x04320095
   #define RW_DDT_INSERT_ENTRY_FAILED                                0x04320096
   #define RW_CDDT_FILE_FULL                                         0x04320097
   #define RW_INSERT_FORMAT_PRIMARY_FLAW_DEFECTS_FAILED              0x04320098
   #define RW_DEFECTIVE_TRACKS_INSERT_GROWN_DEFECTS_FAILED           0x04320099
   #define RW_DEFECTIVE_TRACKS_INSERT_PRIMARY_DEFECTS_FAILED         0x0432009A
   #define RW_DEFECTIVE_TRACKS_LIST_FULL                             0x0432009B
   #define RW_PARTIAL_REALLOCATION_NOT_ALLOWED                       0x0432009D
   #define RW_BIPS_ALLOCATION_NOT_ALLOWED                            0x0432009E
   #define RW_BIPS_DDT_OPERATION_FAILED_01                           0x0432009F
   #define RW_BIPS_DDT_OPERATION_FAILED_02                           0x043200A0
#if (RW_FORMAT_DEALLOCATE_TRACK_SWD_ERRORS || RW_FORMAT_DEALLOCATE_TRACK_MANY_SERVO_FLAWS_PER_TRACK)
   #define RW_DEALLOCATE_TRACK_INSERT_DST_FAILED                     0x043200A1
#endif
   #define RW_ALTERNATE_NOT_AVAILABLE_02                             0x043200A2
#if GLIST_TO_PLIST_PAD_AND_FILL_DEFECTS
   #define RW_DEFECTS_PAD_FILL_MAX_NUM_SKIPPED_TRACKS_EXCEEDED       0x043200A3
#endif

   #define RW_ALTERNATE_NOT_AVAILABLE_03                             0x043200A4
   #define RW_INSUFFICIENT_PBAS_FOR_REQUIRED_LBAS                    0x043200A5
   #define RW_ALTERNATE_NOT_AVAILABLE_04                             0x043200A6
   #define RW_ALTERNATE_NOT_AVAILABLE_05                             0x043200A7
   #define RW_ALTERNATE_NOT_AVAILABLE_06                             0x043200A8
   #define RW_DDT_MAX_SLIP_EXCEEDED                                  0x043200A9

#if INLINE_PARITY_SECTORS
   #define RW_REALLOCATE_WITH_INVALID_HW_PARITY_DATA                 0x043200AA
#endif

   #define RW_MEDIA_CACHE_PAD_PROTECT_USER_DATA_FAILED               0x043200AB
   #define RW_FEATURE_METADATA_BUDGET_WILL_BE_INCORRECT_AFTER_FORMAT 0x043200AC
   #define RW_ALTERNATE_NOT_AVAILABLE_07                             0x043200AD
   #define RW_ALTERNATE_NOT_AVAILABLE_08                             0x043200AE
   #define RW_ALTERNATE_NOT_AVAILABLE_09                             0x043200AF
   #define RW_ALTERNATE_NOT_AVAILABLE_0A                             0x043200B0
   #define RW_PARITY_SECS_SLIP_LIST_UPDATE_FAILED                    0x043200B1
   #define RW_INVALID_TRACK_SECTOR_RANGE_01                          0x043200B2
   #define RW_INTERMEDIATE_SUPER_PARITY_MEDIA_CACHE_PAD_FAILED       0x043200B3
#if (RW_MEDIA_CACHE_PARTITION_SUPPORT && INLINE_PARITY_SECTORS && INLINE_PARITY_TRACK_BASED_PARITY_SECTORS)
   #define RW_MEDIA_CACHE_DDT_VERIFICATION_FAILED                    0x043200B4
#endif
#if DISALLOW_SPARES_ON_USER_LAST_TRACK
   #define RW_ALTERNATE_NOT_AVAILABLE_0B                             0x043200B5
#endif
#if FE_0211489_406374_RW_FORMAT_ZONE_SKIP
   #define RW_ALTERNATE_NOT_AVAILABLE_0C                             0x043200B6
#endif
#if (RW_MEDIA_CACHE_PARTITION_SUPPORT && MC_DESPERADO_WITH_SP && INLINE_PARITY_ISO_AND_TRACK_BASED_PARITY_SECTORS)
   #define RW_INVALID_ISO_BASED_PARITY_SUPER_BLK_SIZE                0x043200B7
#endif
#if FE_0249561_008864_SMR_ISO_BAND_SIZE_SUPPORT
   #define RW_ISO_BAND_ALIGNMENT_INSERT_PADDED_DEFECTS_FAILED        0x043200B8
   #define RW_ISO_BAND_ALIGNMENT_TRK_ATTRIBUTES_CALC_FAILED          0x043200B9
   #define RW_ISO_BAND_ALIGNMENT_TRK_LBA_RANGE_CALC_FAILED           0x043200BA
   #define RW_ISO_BAND_ALIGNMENT_PADDED_PBA_RANGE_INVALID            0x043200BB
   #define RW_ISO_BAND_ALIGNMENT_VERIFY_BAND_BOUNDARIES_FAILED       0x043200BC
   #define RW_ISO_BAND_ALIGNMENT_START_WEDGE_TO_SECS_CALC_FAILED_01  0x043200BD
   #define RW_ISO_BAND_ALIGNMENT_START_WEDGE_TO_SECS_CALC_FAILED_02  0x043200BE
   #define RW_ISO_BAND_ALIGNMENT_END_WEDGE_TO_SECS_CALC_FAILED_01    0x043200BF
   #define RW_ISO_BAND_ALIGNMENT_END_WEDGE_TO_SECS_CALC_FAILED_02    0x043200C0
#endif
   #define RW_DIST_MEDIA_CACHE_PAD_PROTECT_USER_DATA_FAILED          0x043200C1
   #define RW_FORMAT_USER_PARTITION_END_SUPER_BLK_INFO_CALC_FAILED   0x043200C2
#if RW_OVERLAY_MEDIA_CACHE_ZONES_SUPPORT
   #define RW_ADD_OVERLAY_MC_ZONE_GROUPS_PRIMARY_DEFECTS_FAILED      0x043200C3
   #define RW_ADD_OVERLAY_MC_ZONE_GROUP_GROWN_DEFECTS_FAILED         0x043200C4
   #define RW_NON_OVERLAY_MC_ZONE_GROUPS_LBA_CAPACITY_NOT_MET        0x043200C5
   #define RW_OVERLAY_MC_ZONES_ALIGNMENT_ADD_PADDED_DEFECTS_FAILED   0x043200C6
#endif
#if FE_0342920_504520_NEW_SENSE_CODE_4_SFMT_MC_SPARE_NOT_AVAIL
   #define RW_ALTERNATE_NOT_AVAILABLE_IN_SFMT_MC_ZONES               0x043200C7
#endif
#if FE_0352598_504520_FAIL_SFMT_IF_UMP_LESS_THAN_50G
   #define RW_SFMT_FAIL_UMP_CAP_LESS_THAN_50G                        0x043200C8
#endif
   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/32/01 Errors.
   //***************************************************************************
   // 0x04320180: RW_SAVE_DEFECT_FILES_FAILED - Reallocate Block - Failed to save defect files.
   // 0x04320181: RW_PRIMARY_DEFECT_LIST_FILE_OVERFLOW_02 - Process Growth Defect List - PList file overflow error.
   // 0x84320182: RW_PRIMARY_SERVO_FLAW_TABLE_OVERFLOW - Process Defect Lists - PSFT file overflow error.
   // 0x84320183: RW_PRIMARY_DEFECT_FILES_UNWRITABLE - Process Defect Lists - Unable to write defect files.
   // 0x84320184: RW_OPERATING_PARAMETERS_FILE_UPDATE_ERROR - Process Defect Lists - Unable to update operating parms file.
   // 0x04320185: RW_PRIMARY_DEFECT_LIST_FILE_OVERFLOW_03 - Pad/Fill Defects - PList file overflow error.
   // 0x04320186: RW_PRIMARY_DEFECT_LIST_FILE_OVERFLOW_04 - Pad/Fill Defects - PList file overflow error.
   // 0x04320187: RW_SCAN_DEFECT_ADJ_SECS_REMOVE_DATA_SCRUB_LIST_FAILED - R/W Scan Defect Adjacent Sectors - Removing Data Scrub list entry failed.
   // 0x04320188: RW_SCAN_DEFECT_ADJ_SECS_MARK_PENDING_REASSIGN_FAILED - R/W Scan Defect Adjacent Sectors - Mark User LBA for pending reallocation failed.
   //
   //</RW_SENSE_ERROR_CODES>

#if RW_REPORT_HARDWARE_ERROR_ON_REASSIGNMENT_FAILURE
   #undef RW_SAVE_DEFECT_FILES_FAILED
   #define RW_SAVE_DEFECT_FILES_FAILED                               0x04320180
#endif
#if GLIST_TO_PLIST
   #define RW_PRIMARY_DEFECT_LIST_FILE_OVERFLOW_02                   0x04320181
   #define RW_PRIMARY_SERVO_FLAW_TABLE_OVERFLOW                      0x04320182
   #define RW_PRIMARY_DEFECT_FILES_UNWRITABLE                        0x04320183
#endif
   #define RW_OPERATING_PARAMETERS_FILE_UPDATE_ERROR                 0x04320184
#if GLIST_TO_PLIST_PAD_AND_FILL_DEFECTS
   #define RW_PRIMARY_DEFECT_LIST_FILE_OVERFLOW_03                   0x04320185
   #define RW_PRIMARY_DEFECT_LIST_FILE_OVERFLOW_04                   0x04320186
#endif
#if FE_0229304_008864_SCAN_DEFECT_ADJ_SECTORS_SUPPORT_ADDL_DEFECT_LISTS
#if RW_LIMIT_SOFT_REALLOCATION_ATTEMPTS
   #define RW_SCAN_DEFECT_ADJ_SECS_REMOVE_DATA_SCRUB_LIST_FAILED     0x04320187
#endif
   #define RW_SCAN_DEFECT_ADJ_SECS_MARK_PENDING_REASSIGN_FAILED      0x04320188
#endif

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/40 Errors.
   //***************************************************************************
   // 0x84400080: RW_MAX_TRK_REWRITE_DURING_CERT_RETRIES_EXCEEDED - Format - Exceeded maximum number of track rewrite during certify retries.
   // 0x84409400: RW_HRK_ERROR_ON_WRITE - SED - Hidden Root Key error on write
   //
   //</RW_SENSE_ERROR_CODES>

#if REWRITE_DURING_CERT_RETRY
   #define RW_MAX_TRK_REWRITE_DURING_CERT_RETRIES_EXCEEDED           0x04400080
#endif // REWRITE_DURING_CERT_RETRY

   #define RW_HRK_ERROR_ON_WRITE                                     0x04409400


   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/44 Errors.
   //***************************************************************************
   // 0x04440080: RW_HW_ERR_START_ERR_CODE - First error code of RW hardware errors.
   // 0xC4440080: RW_WRITE_PREAMP_UNSAFE_FAULT - Disc Xfr - Write during preamp unsafe fault.
   // 0x84440081: RW_READ_WRITE_CHANNEL_FAULT - Disc Xfr - Read channel fault.
   // 0x84440082: RW_SFF_FAULT - Disc Xfr - Small form factor fault.
   // 0xC4440083: RW_WRITE_SERVO_FIELD_FAULT - Disc Xfr - Write during servo field fault.
   // 0xC4440084: RW_MM_TPBA_FIFO_CTR_ERR - Disc Xfr - Media Manager's TPBA FIFO Counter error.
   // 0xC4440085: RW_MM_TPBA_FIFO_UNDRN_ERR - Disc Xfr - Media Manager's TPBA FIFO Underrun error.
   // 0xC4440086: RW_MM_DDT_FIFO_CTR_ERR - Disc Xfr - Media Manager's DDT FIFO Counter error.
   // 0x84440087: RW_MM_DDT_FIFO_UNDRN_ERR - Disc Xfr - Media Manager's DDT FIFO Underrun error.
   // 0x84440088: RW_MM_PARITY_ERR - Disc Xfr - Media Manager's Parity error.
   // 0x84440089: RW_MM_TDT_FIFO_UNDRN_ERR - Disc Xfr - Media Manager's TDT FIFO Underrun error.
   // 0xC444008A: RW_MM_SKIP_MASK_UNDRN_ERR - Disc Xfr - Media Manager's Skip Mask Underrun error.
   // 0x8444008B: RW_TEMPERATURE_INVALID - Get Temperature request resulted in invalid temperature.
   // 0x8444008C: RW_VOLTAGE_MARGIN_HW_NOT_SUPPORTED - Detected unsupported H/W in a Set Voltage Margin request.
   // 0x8444008E: RW_SMART_SEQ_INIT_BUFFER_NOT_READY - Super Sector - Initial buffer ready timeout error.
   // 0x8444008F: RW_EDAC_CORR_MEM_PARITY_ERR - Disc Xfr - Formatter EDAC correction memory parity error.
   // 0x84440090: RW_NX_RLL_ERR - Disc Xfr - NX - RLL error.
   // 0x84440091: RW_DISC_BUFR_PARITY_ERR - Disc Xfr - Disc Buffer parity error.
   // 0x84440092: RW_SEQ_EXE_SGATE_OVERLAP_ERR - Disc Xfr - Sequencer encountered an EXE/SGATE overlap error.
   // 0x84440093: RW_CR_UNDERRUN_ERR - Disc Xfr - Formatter Correction Buffer underrun error.
   // 0x84440094: RW_CR_OVERRUN_ERR - Disc Xfr - Formatter Correction Buffer overrun error.
   // 0x84440095: RW_FORMATTER_NRZ_INTF_ERR - Formatted detected NRZ interface protocol error.
   // 0x84440096: RW_MM_MX_OVERRUN_ERR - Disc Xfr - Media Manager's MX Overrun error.
   // 0x84440097: RW_MM_NX_OVERRUN_ERR - Disc Xfr - Media Manager's NX Overrun error.
   // 0x84440098: RW_MM_TDT_REQUEST_ERR - Disc Xfr - Meida Manager's TDT Request error.
   // 0x84440099: RW_MM_SST_OVERRUN_ERR - Disc Xfr - Media Manager's SST Overrun error.
   // 0x8444009A: RW_PZT_CALIBRATION_FAILED - Servo PZT calibration failed.
   // 0x8444009B: RW_SERVO_FAST_IO_DATA_UPDATE_TIMEOUT - Fast I/O - Servo data update timeout error.
   // 0x8444009C: RW_SERVO_FAST_IO_FIRST_WEDGE_DATA_AVAILABLE_TIMEOUT - Fast I/O - First wedge servo data timeout error.
   // 0x8444009D: RW_COLLECT_FAST_IO_DATA_WAIT_FOR_SEQUENCER_START_WEDGE_ERROR - During Fast IO data collection , wait for sequencer start wedge timeout.
   // 0x8444009E: RW_CORB_EDC_ERR -  CR memory EDC error.
   // 0x8444009F: RW_SP_DETECTED_EDC_ERR -  SP block detected an EDC error.
   // 0x844400A0: RW_WRITE_PREAMP_HTR_OPEN_SHORT_FAULT - Write preamp unsafe fault with short/open fault set
   // 0x844400A1: RW_CHANNEL_WRITE_BUFFER_ERROR - Memory buffer overflow or underflow, or parity error during write.
   // 0x844400A2: RW_CHANNEL_READ_BUFFER_ERROR - Memory buffer overflow or read data path FIFO underflow in legacy NRZ mode.
   // 0x844400A3: RW_CHANNEL_PFAULT_ERR - PFAULT input asserted during either read or write.
   // 0x844400A4: RW_CHANNEL_WRT_OVERLAP_ERR - SGATE, RGATE, or WGATE overlap.
   // 0x844400A5: RW_CHANNEL_SPLIT_ERR - Mismatch in split sector controls or sector size controls.
   // 0x844400A6: RW_CHANNEL_NO_CLOCK_ERR - WRT_CLK or NRZ_CLK is not running.
   // 0x844400A7: RW_CHANNEL_CALBLK_FAULT - SGATE, RGATE, or WGATE asserted during calibration.
   // 0x844400A8: RW_CHANNEL_RWBI_OUT_FAULT - RWBI changed during a read or write event.
   // 0x844400A9: RW_CHANNEL_MOLP - Mode overlap flag.
   // 0x844400AA: RW_CHANNEL_RPLO_FAULT - Inappropriate WPLO or RPLO behavior.
   // 0x844400AB: RW_CHANNEL_PREA_FLT - Write aborted.
   // 0x844400AC: RW_CHANNEL_BITCNTLATE - Bit count late.
   // 0x844400AD: RW_CHANNEL_SERVO_OVERLAP_ERR - Servo overlap error.
   // 0x844400AE: RW_CHANNEL_LAST_DATA_FLT - Last data fault.
   // 0x844400B0: RW_PES_THRESHOLD_TOO_LARGE - PES threshold in field is too far from the same value calculated in the factory
   // 0x844400B1: RW_NOT_ENOUGH_VALID_WEDGES_FOR_HR - not enough Harmonic Ratio samples were gathered
   // 0x844400B2: RW_HR_SAMPLE_SIGMA_TOO_LARGE - sigma of Harmonic Ratio samples after all discards exceeded the limit
   // 0x844400B3: RW_EBMS_NO_CONTACT_FOUND_AT_MIN_TREHSOLD - no EBMS contact fault, even at lowest threshold value
   // 0x844400B4: RW_EBMS_CONTACT_FOUND_AT_MAX_TREHSOLD - EBMS fault still detected at highest threshold value
   // 0x844400B5: RW_FORMATTER_DETECTED_BFI_ERR - Formatter detected BFI error, e.g. PBM_FF_XFR_EN dropped within a sector data transfer.
   // 0x844400B6: RW_FORM_FIFO_INTF_ERROR - Generic formatter fifo interface error.
   // 0x844400B7: RW_NRZ_LATENCY_COUNT_ERR - Disc Xfr - MX-DX data transfer size mismatch.
   // 0x844400B8: RW_CORB_XFR_ERR - Disc Xfr - Correction buffer active while DX timeout error, this error code is used to fix the hardware skip mask read xfr issue
   // 0x844400B9: RW_CHANNEL_RSM_FAULT - Seagate Iterative Decoder - Channel RSM fault
   // 0x844400BA: RW_CHANNEL_WSM_FAULT - Seagate Iterative Decoder - Channel WSM fault
   // 0x844400BB: RW_CHANNEL_BCI_FAULT - Seagate Iterative Decoder - Channel BCI fault
   // 0x844400BC: RW_CHANNEL_SRC_FAULT - Seagate Iterative Decoder - Channel SRC fault
   // 0x844400BD: RW_CHANNEL_SAB_FAULT - Seagate Iterative Decoder - Channel SAB fault
   // 0x844400BE: RW_CHANNEL_READ_GATE_OVERFLOW_ERR- Seagate Iterative Decoder - Channel read gate overflow error
   // 0xC44400C0: RW_CHANNEL_SMB_B_PARITY_ERROR - Seagate Iterative Decoder - Channel SMB Bus B parity error
   // 0xC44400C1: RW_CHANNEL_SMB_BUFFER_ERROR_ON_WRITE - Seagate Iterative Decoder -Channel SMB buffer error during write operation
   //           :                                        This error is due to SMB(SMall Buffer) write buffer overflow or SMB read buffer underflow error
   // 0xC44400C2: RW_CHANNEL_SOB_BUFFER_ERROR_ON_WRITE - Seagate Iterative Decoder -Channel SOB buffer error during write operation
   //           :            This error is due to SOB(SOfter Buffer) write buffer overflow or SOB read buffer underfow error
   // 0xC44400C3: RW_CHANNEL_SOB_PARITY_ERROR - Seagate Iterative Decoder - Channel SOB parity error
   // 0xC44400C4: RW_CHANNEL_SAB_BUFFER_ERROR - Seagate Iterative Decoder - Channel SAB buffer error
   // 0xC44400C5: RW_CHANNEL_SAB_BEND_ERROR - Seagate Iterative Decoder - Channel SAB bend error
   // 0xC44400C6: RW_CHANNEL_LLI_BFR_SYNC_ERROR - Seagate Iterative Decoder - Channel LLI buffer sync error
   // 0xC44400C7: RW_CHANNEL_LLI_DATA_LEN_ERROR_ON_WRITE - Seagate Iterative Decoder - Channel LLI data length error during write operation
   //           :                                          This error is due to LLI(Long Latency Interface) sector length error or
   //           :                                          LLI fragment length error
   // 0xC44400C8: RW_CHANNEL_LLI_FRAMING_ERROR_ON_WRITE - Seagate Iterative Decoder - Channel LLI framing error during write operation
   //           :                                         This error is due to WPLO-width error detected by LLI, WPLO error detected by
   //           :                                         LLI, or LLI sector framing error
   // 0xC44400C9: RW_CHANNEL_LLI_WRITE_STATUS_ERROR - Seagate Iterative Decoder - Channel LLI write status error
   // 0xC44400CA: RW_CHANNEL_RSM_GROSS_ERR - Seagate Iterative Decoder - Channel RSM Gross Error
   // 0xC44400CB: RW_CHANNEL_DECODER_MICROCODE_ERROR - Seagate Iterative Decoder - Channel decoder microcode error
   // 0xC44400CC: RW_CHANNEL_ENCODER_MICROCODE_ERROR - Seagate Iterative Decoder - Channel encoder microcode error
   // 0xC44400CD: RW_CHANNEL_NRZ_PARITY_ERROR - Seagate Iterative Decoder - Channel NRZ parity error
   // 0xC44400CE: RW_CHANNEL_SYM_PER_SEC_ERROR - Seagate Iterative Decoder - Channel Symbols per sector error (always masked for Bonanza)
   // 0xC44400CF: RW_CHANNEL_SMB_A_PARITY_ERROR - Seagate Iterative Decoder - Channel SMB Bus A parity error
   // 0xC44400D0: RW_CHANNEL_SMB_NRZ_PARITY_ERROR - Seagate Iterative Decoder - Channel SMB NRZ parity error
   // 0xC44400D1: RW_CHANNEL_SOB_BUFFER_ERROR_ON_READ  - Seagate Iterative Decoder -Channel SOB buffer error during read operation
   //                                                    This error is due to SOB write buffer overflow or SOB read buffer underfow error
   // 0xC44400D2: RW_CHANNEL_SMB_BUFFER_ERROR_ON_READ - Seagate Iterative Decoder -Channel SMB buffer error during read operation
   //           :                                       This error is due to SMB write buffer overflow or SMB read buffer underflow error
   // 0xC44400D3: RW_CHANNEL_LLI_DATA_LEN_ERROR_ON_READ - Seagate Iterative Decoder - Channel LLI data length error during read operation
   //           :                                         This error is due to LLI sector length error or LLI fragment length error
   // 0xC44400D4: RW_CHANNEL_LLI_FRAMING_ERROR_ON_READ - Seagate Iterative Decoder - Channel LLI framing error during read operation
   //           :                                        This error is due to LLI PLO length error.
   // 0x044400D9: RW_CHANNEL_WSM_GROSS_ERR - No Description Added @@@
   // 0x044400DA: RW_CHANNEL_ERF_BUFFER_ERROR - No Description Added @@@

   // 0x044400DB: RW_CHANNEL_PLL_LOST_LOCK_ERR - Read Channel PLL_LOST_LOCK	error

   // 0xC44400E0: RW_PREAMP_LOW_VOLTAGE_ERROR - No Description Added @@@
   // 0xC44400E1: RW_PREAMP_LOW_WRITE_DATA_FREQ_COMMON_ERROR  - No Description Added @@@
   // 0xC44400E2: RW_PREAMP_WRITE_HEAD_OPEN_ERROR - No Description Added @@@
   // 0xC44400E3: RW_PREAMP_WRITE_HEAD_SHORT_TO_GROUND_ERROR - No Description Added @@@
   // 0xC44400E4: RW_PREAMP_TA_SENSOR_OPEN_ERROR - No Description Added @@@
   // 0xC44400E5: RW_PREAMP_TEMPERATURE_ERROR - No Description Added @@@
   // 0xC44400E6: RW_PREAMP_WRITE_WITHOUT_HEAT_ERROR - No Description Added @@@
   // 0xC44400E7: RW_PREAMP_WRITER_OFF_IN_WRITE_ERROR - No Description Added @@@
   // 0xC44400E8: RW_PREAMP_WRITER_OUTPUT_BUF_ERROR - No Description Added @@@
   // 0xC44400E9: RW_PREAMP_LOW_WRITE_DATA_FREQ_HEAD_ERROR - No Description Added @@@
   // 0xC44400EA: RW_PREAMP_FOS_ERROR - No Description Added @@@
   // 0xC44400EB: RW_PREAMP_TA_OR_CONTACT_DET_ERROR - No Description Added @@@
   // 0xC44400EC: RW_PREAMP_SWOT_ERROR - No Description Added @@@
   // 0xC44400ED: RW_PREAMP_SERIAL_PORT_COM_ERROR - No Description Added @@@
   // 0xC44400EE: RW_CHANNEL_LLR_PIPE_STATE_ERROR - Seagate Iterative Decoder - Channel LLI pipe state error
   //
   // 0x044400F0: RW_CHANNEL_RDATA_VALID_OVERLAP_FAULT - Channel SRC Fault - Read-Data-Valid Signal Overlap error detected when RDATA_VALID
   //                                                                        from sector N-1 is overlapping with RDATA_VALID from sector N.
   // 0x84440130: RW_AR_DAC_TO_TGT_SQ_ROOT_OF_NEGATIVE_ERROR - The AR Sensor DAC to Target calculation encountered the need to take the square root of a negative value.
   // 0x84440131: RW_AR_BACKGROUND_TASK_FILE_OPEN__ERROR - The AR Sensor encountered an error when attempting to open the Background Task file.
   // 0x84440132: RW_AR_GENERAL_PURPOSE_FILE_OPEN_ERROR - The AR Sensor encountered an error when attempting to open the General Purpose Task file.
   // 0x84440133: RW_AR_BACKGROUND_TASK_FILE_SIZE_ERROR - The size of the Background Task file is inadequate to satisfy the AR Sensor's requirements.
   // 0x84440134: RW_AR_GENERAL_PURPOSE_FILE_SIZE_ERROR - The size of the General Purpose Task file is inadequate to satisfy the AR Sensor's requirements.
   // 0x84440135: RW_AR_INVALID_FAFH_PARM_FILE_AR_DESCRIPTOR_ERROR - The AR Sensor Descriptor in the FAFH Parameter File is invalid.
   // 0x84440136: RW_AR_INVALID_ITERATIVE_CALL_INDEX - The Iterative Call Index specified when invoking the AR Sensor exceeds the maximum supported value.
   // 0x84440137: RW_AR_PERFORM_TRACK_POSITION_REQ_ERROR - The AR Sensor encountered an error when performing a Track Position request.
   // 0x84440138: RW_AR_SET_CHANNEL_FREQ_ERROR - The AR Sensor encountered an error when attempting to set the read channel frequency.
   // 0x84440139: RW_AR_3RD_HARMONIC_EQUAL_0_ERROR - The 3rd Harmonic value measured by the AR Sensor was 0.
   // 0xC444013A: RW_CHANNEL_CAL_PROCESSOR_ALREADY_HALTED_ERROR - Read Channel Calibration Processor already halted error.
   // 0x8444013B: RW_HSC_INVALID_WRITE_PATTERN_ERROR - An invalid write pattern was specified Harmonic Sensor Circuitry data collection.
   // 0x8444013C: RW_HSC_DATA_COLLECTION_FILE_OPEN_ERROR - An error occurred when attempting to open the file to be used for Harmonic Sensor Circuitry data collection.
   // 0x8444013D: RW_HSC_DATA_LOW_FREQ_HARMONIC_STD_DEV_0_ERROR - The Standard Deviation of the Low Freq Amplitude data collected by the Harmonic Sensor Circuitry was zero.
   // 0x8444013E: RW_HSC_DATA_3RD_HARMONIC_STD_DEV_0_ERROR - The Standard Deviation of the 3rd Harmonic data collected by the Harmonic Sensor Circuitry was zero.
   // 0x8444013F: RW_HSC_DATA_SERVO_LOOP_CODE_ERROR - The Servo Loop Code returned at the completion of Harmonic Sensor Circuitry data collection was not 0.
   // 0xC4440140: RW_HSC_MAGNITUDE_OVERFLOW_ERROR - No Description Added @@@
   // 0x84440141: RW_MAX_FAST_IO_SAMPLES_EXCEEDED_ERROR - Fast I/O - Max samples per collection exceeded.
   // 0xC4440142: RW_COLLECT_FAST_IO_DATA_ERROR - Collect Fast IO data error.
   // 0xC4440143: RW_SET_FAST_IO_CONTROL_INFO_ERROR - Set Fast IO control info error.
   // 0xC4440144: RW_SET_FAST_IO_DATA_COLLECTION_PARAMETERS_ERROR - Set Fast IO data collection parameters error.
   // 0x84440160: RW_CHANNEL_LOSSLOCKR_FAULT  - Loss of lock on Rclock.
   // 0x04440161: RW_CHANNEL_BLICNT_FAULT - Baseline instability count fault
   // 0x04440162: RW_CHANNEL_LLI_ABORT_FAULT - LLI abort fault
   // 0x04440163: RW_CHANNEL_WG_FILLR_FAULT - Wedge fill read  fault (added for Floresta)
   // 0x04440164: RW_CHANNEL_WG_FILLW_FAULT - Wedge fill write fault (added for Floresta)
   // 0x04440165: RW_CHANNEL_CHAN_FAULT - Channel Ready/Soft channel fault
   // 0x04440166: RW_CHANNEL_FRAG_NUM_FAULT - Fragment number fault
   // 0x04440167: RW_CHANNEL_WTG_FAULT - Write-through gap timeout fault
   // 0x04440168: RW_CHANNEL_CTG_FAULT - CTG Type channel fault
   // 0x04440169: RW_CHANNEL_NRZCLR_FAULT - NZRCLR fault
   // 0x0444016A: RW_CHANNEL_SYNR_PCH_FAIL_FAULT - Read synthesizer prechange fail fault
   // 0x0444016B: RW_CHANNEL_SYNS_PCH_FAIL_FAULT - Servo synthesizer prechange fail fault
   // 0xC444016C: RW_CHANNEL_CAL_PROCESSOR_HALT_SERVO_ERROR - Servo Error detected prior to halting Calibration Processor.
   // 0xC444016D: RW_CHANNEL_CAL_PROCESSOR_UNABLE_TO_HALT_ERROR - Unable to Halt Calibration Processor.
   // 0xC444016E: RW_CHANNEL_CAL_PROCESSOR_ADC_CALS_ALREADY_DISABLED_ERROR - ADC Calibrations already disabled.
   // 0xC444016F: RW_CHANNEL_CAL_PROCESSOR_REQ_REG_ALREADY_SAVED - Calibration Processor Registers have already been saved.
   // 0xC4440170: RW_CHANNEL_CAL_PROCESSOR_REG_SAVE_ADDR_INVALID - Address where Calibration Processor Registers are to be saved is invalid.
   // 0xC4440171: RW_CHANNEL_CAL_PROCESSOR_SAVE_REG_ARRAY_TOO_SMALL - Array for saving Calibration Processor Register values is too small.
   // 0xC4440172: RW_CHANNEL_CAL_PROCESSOR_AR_SENSOR_REG_VALUES_INVALID - Calibration Processor Register values to be used for AR are invalid.
   // 0x04440173: RW_CHANNEL_SABT_DONE_FAULT - Synchronous abort complete fault
   // 0x04440174: RW_CHANNEL_PREA_CNT_FAULT - Preamble length fault
   // 0x04440175: RW_CHANNEL_TA_EVENT_FAULT - TA or media defect event fault
   // 0x04440176: RW_CHANNEL_PLLFLOR_FAULT - DPLL frequency overflow/underflow fault
   // 0x04440177: RW_CHANNEL_ZGR_FLG_FAULT - Zero gain threshold exceeded fault
   // 0x04440178: RW_CHANNEL_FREQ_FLG_FAULT - DPLL frequency deviation fault
   // 0x04440179: RW_CHANNEL_EVGA_FLOR_FAULT - Extended EVGA overflow/underflow fault
   // 0x04440180: RW_CHANNEL_VGA_FLOR_FAULT - Read VGA gain fault
   // 0x04440181: RW_CHANNEL_ACQ_FLG_FAULT - Acquire Peak Amplitude flag fault
   // 0x04440182: RW_CHANNEL_MDO_DET_FAULT - Massive drop-out fault
   // 0x04440183: RW_CHANNEL_SIG_SYNC_FAULT - Low Quality sync mark fault
   // 0x04440184: RW_CHANNEL_NPLD_ERR_FAULT - NPLD load error fault
   // 0x04440185: RW_CHANNEL_WR_CRC_FAULT - Write path memory fault status bit fault
   // 0x04440186: RW_CHANNEL_WRPO_FAULT - WRPO disabled fault
   // 0x04440187: RW_CHANNEL_PQ_FAULT - Preamble quality monitor fault
   // 0x04440188: RW_CHANNEL_RST_FLG_FAULT - Reset detection flag fault
   // 0x04440189: RW_CHANNEL_PCKT_WR_FAULT - Packet write fault
   // 0x0444018A: RW_CHANNEL_GATE_Q_UFL_FAULT - Gate command queue overflow fault
   // 0x0444018B: RW_CHANNEL_GATE_Q_OFL_FAULT - Gate command queue underflow fault
   // 0x0444018C: RW_CHANNEL_END_WS_FAULT - Ending write splice fault status fault
   // 0x0444018D: RW_CHANNEL_WTG_SRV_FAULT - Write-through gap servo collision fault
   // 0x0444018E: RW_CHANNEL_RDGATE_FAULT - Read Gate Fault
   // 0x8444018F: RW_HSC_DATA_PREAMP_GAIN_READ_ERROR - error reading the Preamp Gain register during an HSC operation.
   // 0x84440190: RW_HSC_DATA_PREAMP_GAIN_WRITE_ERROR - error writing the Preamp Gain register during an HSC operation.
   // 0x84440191: RW_CHANNEL_CAL_PROCESSOR_NOT_HALTED_ERROR - Read Channel Calibration Processor not halted.
   // 0x84440192: RW_CHANNEL_BACKGROUND_CALS_ALREADY_STOPPED_ERROR - Read Channel background calibrations already stopped.
   // 0x84440193: RW_CHANNEL_BACKGROUND_CALS_NOT_STOPPED_ERROR - Read Channel background calibrations not stopped.
   // 0x84440194: RW_CHANNEL_CAL_PROCESSOR_HALT_ERROR - Read Channel Calibration Processor halt error.
   // 0x84440195: RW_AR_SAVE_CAL_PROC_REGS_ERROR - Read Channel save AR Calibration Processor registers error.
   // 0x84440196: RW_AR_LOAD_CAL_PROC_REGS_ERROR - Read Channel load AR Calibration Processor registers error.
   // 0x84440197: RW_AR_RESTORE_CAL_PROC_REGS_ERROR - Read Channel restore AR Calibration Processor registers error.
   // 0xC4440198: RW_WRITE_MODULATION_CODE_FAIL0 - Markov Write Encode fail0
   // 0xC4440199: RW_WRITE_MODULATION_CODE_FAIL0 - Markov Write Encode fail1
   // 0x8444019a: RW_WRITE_MODULATION_CODE_FAIL  - All of other fails exception above two type of fails.
   // 0xC444019b: RW_FORMATTER_NRZ_INTF_PRAND_NYQ_ERR - Outer Code prand NYQ error
   // 0xC444019c: RW_FORMATTER_NRZ_INTF_PRAND_RUN_ERR - Outer Code prand run error
   // 0x044404FF: RW_HW_ERR_END_ERR_CODE - Last error code of RW hardware errors.

   // 0x84448100: RW_RDLONG_FROM_MEDIA_CACHE_HARDENED_LBA - Special case sense code for a MC unrecovered or hardened error during pre-clean for read long.

   //</RW_SENSE_ERROR_CODES>

   #define RW_HW_ERR_START_ERR_CODE                                  0x04440080

   #define RW_WRITE_PREAMP_UNSAFE_FAULT                              (0x04440080 | RW_RETRYABLE_ERR_TYPE)

#if !FE_0173863_352870_CHANNEL_FAULT_PARSER
   #define RW_READ_WRITE_CHANNEL_FAULT                               (0x04440081 | RW_RETRYABLE_ERR_TYPE)
#else
   #define RW_READ_WRITE_CHANNEL_FAULT                               0x04440081
#endif

   #define RW_SFF_FAULT                                              0x04440082
   #define RW_WRITE_SERVO_FIELD_FAULT                                (0x04440083 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MM_TPBA_FIFO_CTR_ERR                                   (0x04440084 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MM_TPBA_FIFO_UNDRN_ERR                                 (0x04440085 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MM_DDT_FIFO_CTR_ERR                                    (0x04440086 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MM_DDT_FIFO_UNDRN_ERR                                  0x04440087
   #define RW_MM_PARITY_ERR                                          0x04440088
   #define RW_MM_TDT_FIFO_UNDRN_ERR                                  0x04440089
   #define RW_MM_SKIP_MASK_UNDRN_ERR                                 (0x0444008A | RW_RETRYABLE_ERR_TYPE)
   #define RW_TEMPERATURE_INVALID                                    0x0444008B
   #define RW_VOLTAGE_MARGIN_HW_NOT_SUPPORTED                        0x0444008C

   #define RW_SMART_SEQ_INIT_BUFFER_NOT_READY                        0x0444008E
   #define RW_EDAC_CORR_MEM_PARITY_ERR                               0x0444008F
   #define RW_NX_RLL_ERR                                             0x04440090
   #define RW_DISC_BUFR_PARITY_ERR                                   0x04440091
   #define RW_SEQ_EXE_SGATE_OVERLAP_ERR                              0x04440092
   #define RW_CR_UNDERRUN_ERR                                        0x04440093

#if ( RW_BERP_ERROR_RECOVERY && ANTICIPATORY_TRACK_SEEK_DURING_XFR )
   // When both BERP and ATS2, RW_CR_OVERRUN_ERR may occur if a sector within ATS2
   // window is successfully recovered by BERP.  We just need retry on the error.
   // In a retry where ATS2 is disabled, the error will be gone.
   #define RW_CR_OVERRUN_ERR                                         (0x04440094 | RW_RETRYABLE_ERR_TYPE)
#else
   #define RW_CR_OVERRUN_ERR                                         0x04440094
#endif
   #define RW_FORMATTER_NRZ_INTF_ERR                                 (0x04440095 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MM_MX_OVERRUN_ERR                                      0x04440096
   #define RW_MM_NX_OVERRUN_ERR                                      0x04440097
   #define RW_MM_TDT_REQUEST_ERR                                     0x04440098
   #define RW_MM_SST_OVERRUN_ERR                                     0x04440099
   #define RW_PZT_CALIBRATION_FAILED                                 0x0444009A
#if MCT_FAST_IO
   #define RW_SERVO_FAST_IO_DATA_UPDATE_TIMEOUT                      0x0444009B
   #define RW_SERVO_FAST_IO_FIRST_WEDGE_DATA_AVAILABLE_TIMEOUT       0x0444009C
   #define RW_COLLECT_FAST_IO_DATA_WAIT_FOR_SEQUENCER_START_WEDGE_ERROR  0x0444009D
#endif // MCT_FAST_IO
   #define RW_CORB_EDC_ERR                                           0x0444009E
   #define RW_SP_DETECTED_EDC_ERR                                    (0x0444009F | RW_RETRYABLE_ERR_TYPE)

//#if ( REMOVED Flag: REPORT_PREAMP_HEATER_OPEN_SHORT_FAULT = 0 )
   #define  RW_WRITE_PREAMP_HTR_OPEN_SHORT_FAULT                     0x044400A0
//#endif

   // Vendor Channel/Analog Front-end component fault error codes
   #define RW_CHANNEL_WRITE_BUFFER_ERROR                             (0x044400A1 | RW_CONDITIONAL_RETRY_OPTION)

   #define RW_CHANNEL_READ_BUFFER_ERROR                              0x044400A2

   #define RW_CHANNEL_PFAULT_ERR                                     (0x044400A3 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_WRT_OVERLAP_ERR                                (0x044400A4 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_SPLIT_ERR                                      0x044400A5
   #define RW_CHANNEL_NO_CLOCK_ERR                                   0x044400A6
   #define RW_CHANNEL_CALBLK_FAULT                                   0x044400A7
   #define RW_CHANNEL_RWBI_OUT_FAULT                                 (0x044400A8 | RW_CONDITIONAL_RETRY_OPTION)

   #define RW_CHANNEL_MOLP                                           (0x044400A9 | RW_RETRYABLE_ERR_TYPE )

   #define RW_CHANNEL_RWPLO_FAULT                                    0x044400AA
   #define RW_CHANNEL_PREA_FLT                                       (0x044400AB | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_BITCNTLATE                                     (0x044400AC | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_SERVO_OVERLAP_ERR                              0x044400AD
   #define RW_CHANNEL_LAST_DATA_FLT                                  (0x044400AE | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_CLSN_FAULT                                     (0x044400AF | RW_CONDITIONAL_RETRY_OPTION)
#if RW_FAST_DPES_SENSOR
   #define  RW_PES_THRESHOLD_TOO_LARGE                               0x044400B0
#endif
#if RW_HARMONIC_RATIO_SENSOR
   #define  RW_NOT_ENOUGH_VALID_WEDGES_FOR_HR                        0x044400B1
   #define  RW_HR_SAMPLE_SIGMA_TOO_LARGE                             0x044400B2
#endif
#if RW_EBMS_SENSOR
   #define  RW_EBMS_NO_CONTACT_FOUND_AT_MIN_TREHSOLD                 0x044400B3
   #define  RW_EBMS_CONTACT_FOUND_AT_MAX_TREHSOLD                    0x044400B4
#endif

   #define RW_FORMATTER_DETECTED_BFI_ERR                             0x044400B5
   #define RW_FORM_FIFO_INTF_ERROR                                   0x044400B6
   #define RW_NRZ_LATENCY_COUNT_ERR                                  ( 0x044400B7 | RW_RETRYABLE_ERR_TYPE )


   // Iterative Channel digital back-end fault error codes
#if HWWA_0300323_387179_TEMP_WORKAROUND_FOR_PS_ISSUE_9282
   #define RW_CHANNEL_RSM_FAULT                                      ( 0x044400B9 | RW_RETRYABLE_ERR_TYPE )
#else
   #define RW_CHANNEL_RSM_FAULT                                      0x044400B9
#endif
   #define RW_CHANNEL_WSM_FAULT                                      (0x044400BA | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_BCI_FAULT                                      0x044400BB
#if !FE_0173863_352870_CHANNEL_FAULT_PARSER
   #define RW_CHANNEL_SRC_FAULT                                      (0x044400BC | RW_RETRYABLE_ERR_TYPE)
#else
   #define RW_CHANNEL_SRC_FAULT                                      0x044400BC
#endif

   #define RW_CHANNEL_SAB_FAULT                                      0x044400BD
   #define RW_CHANNEL_READ_GATE_OVERFLOW_ERR                         (0x044400BE | RW_RETRYABLE_ERR_TYPE)

   #define RW_CHANNEL_SMB_B_PARITY_ERROR                             (0x044400C0 | RW_CONDITIONAL_RETRY_OPTION)

   #define RW_CHANNEL_SMB_BUFFER_ERROR_ON_WRITE                      (0x044400C1 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_SOB_BUFFER_ERROR_ON_WRITE                      (0x044400C2 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_SOB_PARITY_ERROR                               (0x044400C3 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_SAB_BUFFER_ERROR                               (0x044400C4 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_SAB_BEND_ERROR                                 (0x044400C5 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_LLI_BFR_SYNC_ERROR                             (0x044400C6 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_LLI_DATA_LEN_ERROR_ON_WRITE                    (0x044400C7 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_LLI_FRAMING_ERROR_ON_WRITE                     (0x044400C8 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_LLI_WRITE_STATUS_ERROR                         (0x044400C9 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_RSM_GROSS_ERR                                  (0x044400CA | RW_RETRYABLE_ERR_TYPE)

   #define RW_CHANNEL_DECODER_MICROCODE_ERROR                        (0x044400CB | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_ENCODER_MICROCODE_ERROR                        (0x044400CC | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_NRZ_PARITY_ERROR                               (0x044400CD | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_SYM_PER_SEC_ERROR                              (0x044400CE | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_SMB_A_PARITY_ERROR                             (0x044400CF | RW_RETRYABLE_ERR_TYPE)
   #define RW_CHANNEL_SMB_NRZ_PARITY_ERROR                           (0x044400D0 | RW_RETRYABLE_ERR_TYPE)
   #define RW_CHANNEL_SOB_BUFFER_ERROR_ON_READ                       (0x044400D1 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_SMB_BUFFER_ERROR_ON_READ                       (0x044400D2 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_LLI_DATA_LEN_ERROR_ON_READ                     (0x044400D3 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_LLI_FRAMING_ERROR_ON_READ                      (0x044400D4 | RW_RETRYABLE_ERR_TYPE)
   #define RW_CHANNEL_WSM_GROSS_ERR                                  0x044400D9
   #define RW_CHANNEL_ERF_BUFFER_ERROR                               0x044400DA
   #define RW_CHANNEL_PLL_LOST_LOCK_ERR                              (0x044400DB | RW_RETRYABLE_ERR_TYPE)

   #define RW_PREAMP_LOW_VOLTAGE_ERROR                               (0x044400E0 | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_LOW_WRITE_DATA_FREQ_COMMON_ERROR                (0x044400E1 | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_WRITE_HEAD_OPEN_ERROR                           (0x044400E2 | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_WRITE_HEAD_SHORT_TO_GROUND_ERROR                (0x044400E3 | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_TA_SENSOR_OPEN_ERROR                            (0x044400E4 | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_TEMPERATURE_ERROR                               (0x044400E5 | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_WRITE_WITHOUT_HEAT_ERROR                        (0x044400E6 | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_WRITER_OFF_IN_WRITE_ERROR                       (0x044400E7 | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_WRITER_OUTPUT_BUF_ERROR                         (0x044400E8 | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_LOW_WRITE_DATA_FREQ_HEAD_ERROR                  (0x044400E9 | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_FOS_ERROR                                       (0x044400EA | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_TA_OR_CONTACT_DET_ERROR                         (0x044400EB | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_SWOT_ERROR                                      (0x044400EC | RW_RETRYABLE_ERR_TYPE)
   #define RW_PREAMP_SERIAL_PORT_COM_ERROR                           (0x044400ED | RW_RETRYABLE_ERR_TYPE)
   #define RW_CHANNEL_RSM_PIPE_STATE_ERROR                           (0x044400EE | RW_CONDITIONAL_RETRY_OPTION)
#if PROD_MISO_CODE_PORTING
   #define RW_CHANNEL_RSM_X_AVERAGE_DONE                             (0x044400EF | RW_RETRYABLE_ERR_TYPE)
#endif
   

#if ( MARVELL_READ_CHANNEL || SRC_MARVELL )
      #define RW_CHANNEL_RDATA_VALID_OVERLAP_FAULT                   (0x044400F0 | RW_CONDITIONAL_RETRY_OPTION)
      #define RW_CHANNEL_RD_VALID_GAP_FAULT                          (0x044400F1 | RW_CONDITIONAL_RETRY_OPTION)

   #define RW_CHANNEL_W_PARITY_NOT_RDY                               (0x044400F4 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_WRONG_SECTOR_LEN                               (0x044400F7 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_ENC_OVW_ERROR                                  (0x044400F8 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_ENC_EARLY_TERM_FAULT                           (0x044400F9 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_ITR_PARAM_ERROR                                (0x044400FA | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_MXP_WRITE_FAULT                                (0x044400FB | RW_CONDITIONAL_RETRY_OPTION)

      #define RW_CHANNEL_SYM_CNT_ERROR                               (0x044400FC | RW_CONDITIONAL_RETRY_OPTION)

   #define RW_CHANNEL_RD_INCOMPLETE_ERROR                            (0x044400FD | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_RD_DATA_VGA_ERROR                              (0x044400FE | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_RD_DATA_TA_ERROR                               (0x044400FF | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_RFM_WRONG_SEC_LENGTH                           (0x04440102 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_RFM_FIFO_UNDERFLOW                             (0x04440103 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_RFM_FIFO_OVERFLOW                              (0x04440104 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_W_RLL_PARAM_ERROR                              0x04440106
   #define RW_CHANNEL_W_ENC_OFLOW                                    0x04440107
   #define RW_CHANNEL_W_ENC_UFLOW                                    0x04440108
   #define RW_CHANNEL_W_ENC_MCONFIG_CRC                              0x04440109
   #define RW_CHANNEL_W_ENC_USER_BUF_CRC                             0x0444010A
   #define RW_CHANNEL_W_ENC_PARITY_BUF_CRC                           0x0444010B
   #define RW_CHANNEL_W_ENC_MATRIX_BUF_CRC                           0x0444010C
   #define RW_CHANNEL_W_ENC_ENCODE_BUF_CRC                           0x0444010D
   #define RW_CHANNEL_W_ENC_MCONFIG_NOT_RDY                          0x0444010E
   #define RW_CHANNEL_W_ENC_MCONFIG_OFLOW                            0x0444010F
   #define RW_CHANNEL_R_RLL_BUF_OFLOW_FAULT                          0x04440110
   #define RW_CHANNEL_R_RLL_PARAM_SETTING_FAULT                      0x04440111
   #define RW_CHANNEL_R_INTF_FAULT                                   0x04440112
   #define RW_CHANNEL_R_INTF_FAULT_RETRYABLE                         (0x04440112 | RW_RETRYABLE_ERR_TYPE )
   #define RW_CHANNEL_R_ITR_DEC_FAULT                                0x04440113

#endif // #if ( MARVELL_READ_CHANNEL || SRC_MARVELL )
#if FE_0162501_357610_VECTOR_MODE_FLAWSCAN_ERROR_THRESHOLD
   #define RW_CHANNEL_VECTOR_FLAW_ERRORS                             0x04440105
#endif

   #define RW_AR_DAC_TO_TGT_SQ_ROOT_OF_NEGATIVE_ERROR                0x04440130
   #define RW_AR_BACKGROUND_TASK_FILE_OPEN__ERROR                    0x04440131
   #define RW_AR_GENERAL_PURPOSE_FILE_OPEN_ERROR                     0x04440132
   #define RW_AR_BACKGROUND_TASK_FILE_SIZE_ERROR                     0x04440133
   #define RW_AR_GENERAL_PURPOSE_FILE_SIZE_ERROR                     0x04440134
   #define RW_AR_INVALID_FAFH_PARM_FILE_AR_DESCRIPTOR_ERROR          0x04440135
   #define RW_AR_INVALID_ITERATIVE_CALL_INDEX                        0x04440136
   #define RW_AR_PERFORM_TRACK_POSITION_REQ_ERROR                    0x04440137
   #define RW_AR_SET_CHANNEL_FREQ_ERROR                              0x04440138
   #define RW_AR_3RD_HARMONIC_EQUAL_0_ERROR                          0x04440139
   #define RW_CHANNEL_CAL_PROCESSOR_ALREADY_HALTED_ERROR             (0x0444013A | RW_RETRYABLE_ERR_TYPE)
   #define RW_HSC_INVALID_WRITE_PATTERN_ERROR                        0x0444013B
   #define RW_HSC_DATA_COLLECTION_FILE_OPEN_ERROR                    0x0444013C
   #define RW_HSC_DATA_LOW_FREQ_HARMONIC_STD_DEV_0_ERROR             0x0444013D
   #define RW_HSC_DATA_3RD_HARMONIC_STD_DEV_0_ERROR                  0x0444013E
   #define RW_HSC_DATA_SERVO_LOOP_CODE_ERROR                         0x0444013F
   #define RW_HSC_MAGNITUDE_OVERFLOW_ERROR                           (0x04440140 | RW_RETRYABLE_ERR_TYPE)
   #define RW_MAX_FAST_IO_SAMPLES_EXCEEDED_ERROR                     0x04440141
   #define RW_COLLECT_FAST_IO_DATA_ERROR                             (0x04440142 | RW_RETRYABLE_ERR_TYPE)
   #define RW_SET_FAST_IO_CONTROL_INFO_ERROR                         (0x04440143 | RW_RETRYABLE_ERR_TYPE)
   #define RW_SET_FAST_IO_DATA_COLLECTION_PARAMETERS_ERROR           (0x04440144 | RW_RETRYABLE_ERR_TYPE)
   #define RW_CHANNEL_LOSSLOCKR_FAULT                                (0x04440160 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_BLICNT_FAULT                                   (0x04440161 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_LLI_ABORT_FAULT                                (0x04440162 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_WG_FILLR_FAULT                                 (0x04440163 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_WG_FILLW_FAULT                                 (0x04440164 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_CHAN_FAULT                                     (0x04440165 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_FRAG_NUM_FAULT                                 (0x04440166 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_WTG_FAULT                                      (0x04440167 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_CTG_FAULT                                      (0x04440168 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_NRZCLR_FAULT                                   (0x04440169 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_SYNR_PCH_FAIL_FAULT                            (0x0444016A | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_SYNS_PCH_FAIL_FAULT                            (0x0444016B | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_CAL_PROCESSOR_HALT_SERVO_ERROR                 (0x0444016C | RW_RETRYABLE_ERR_TYPE)
   #define RW_CHANNEL_CAL_PROCESSOR_UNABLE_TO_HALT_ERROR             (0x0444016D | RW_RETRYABLE_ERR_TYPE)
   #define RW_CHANNEL_CAL_PROCESSOR_ADC_CALS_ALREADY_DISABLED_ERROR  (0x0444016E | RW_RETRYABLE_ERR_TYPE)
   #define RW_CHANNEL_CAL_PROCESSOR_REQ_REG_ALREADY_SAVED            (0x0444016F | RW_RETRYABLE_ERR_TYPE)
   #define RW_CHANNEL_CAL_PROCESSOR_REG_SAVE_ADDR_INVALID            (0x04440170 | RW_RETRYABLE_ERR_TYPE)
   #define RW_CHANNEL_CAL_PROCESSOR_SAVE_REG_ARRAY_TOO_SMALL         (0x04440171 | RW_RETRYABLE_ERR_TYPE)
   #define RW_CHANNEL_CAL_PROCESSOR_AR_SENSOR_REG_VALUES_INVALID     (0x04440172 | RW_RETRYABLE_ERR_TYPE)
   #define RW_CHANNEL_SABT_DONE_FAULT                                (0x04440173 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_PREA_CNT_FAULT                                 (0x04440174 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_TA_EVENT_FAULT                                 (0x04440175 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_PLLFLOR_FAULT                                  (0x04440176 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_ZGR_FLG_FAULT                                  (0x04440177 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_FREQ_FLG_FAULT                                 (0x04440178 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_EVGA_FLOR_FAULT                                (0x04440179 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_VGA_FLOR_FAULT                                 (0x04440180 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_ACQ_FLG_FAULT                                  (0x04440181 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_MDO_DET_FAULT                                  (0x04440172 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_SIG_SYNC_FAULT                                 (0x04440183 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_NPLD_ERR_FAULT                                 (0x04440184 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_WR_CRC_FAULT                                   (0x04440185 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_WRPO_FAULT                                     (0x04440186 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_PQ_FAULT                                       (0x04440187 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_RST_FLG_FAULT                                  (0x04440188 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_PCKT_WR_FAULT                                  (0x04440189 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_GATE_Q_UFL_FAULT                               (0x0444018A | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_GATE_Q_OFL_FAULT                               (0x0444018B | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_END_WS_FAULT                                   (0x0444018C | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_WTG_SRV_FAULT                                  (0x0444018D | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_CHANNEL_RDGATE_FAULT                                   (0x0444018E | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_HSC_DATA_PREAMP_GAIN_READ_ERROR                        0x0444018F
   #define RW_HSC_DATA_PREAMP_GAIN_WRITE_ERROR                       0x04440190
   #define RW_CHANNEL_CAL_PROCESSOR_NOT_HALTED_ERROR                 0x04440191
   #define RW_CHANNEL_BACKGROUND_CALS_ALREADY_STOPPED_ERROR          0x04440192
   #define RW_CHANNEL_BACKGROUND_CALS_NOT_STOPPED_ERROR              0x04440193
   #define RW_CHANNEL_CAL_PROCESSOR_HALT_ERROR                       0x04440194
   #define RW_AR_SAVE_CAL_PROC_REGS_ERROR                            0x04440195
   #define RW_AR_LOAD_CAL_PROC_REGS_ERROR                            0x04440196
   #define RW_AR_RESTORE_CAL_PROC_REGS_ERROR                         0x04440197
   #define RW_WRITE_MODULATION_CODE_FAIL0                            (0x04440198 | RW_RETRYABLE_ERR_TYPE)
   #define RW_WRITE_MODULATION_CODE_FAIL1                            (0x04440199 | RW_RETRYABLE_ERR_TYPE)
   #define RW_WRITE_MODULATION_CODE_FAIL                             (0x0444019a | RW_RETRYABLE_ERR_TYPE)
   #define RW_FORMATTER_NRZ_INTF_PRAND_NYQ_ERR                       (0x0444019b | RW_RETRYABLE_ERR_TYPE)
   #define RW_FORMATTER_NRZ_INTF_PRAND_RUN_ERR                       (0x0444019c | RW_RETRYABLE_ERR_TYPE)

   #define RW_HW_ERR_END_ERR_CODE                                    0x044404FF

#if FE_0116076_355860_MEDIA_CACHE
   #define RW_RDLONG_FROM_MEDIA_CACHE_HARDENED_LBA                   0x04448100
#endif

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/41/87 Errors.
   //***************************************************************************
   // 0x04418780: RW_IOEDC_ERROR_WITHOUT_IOECC_ERROR_ON_WRITE - Disc Xfr - IOEDC parity error on write.
   // 0x04418701: RW_IOEDC_ERROR_ON_WRITE_FDE - 04/8087, FRU 01 - FDE IOEDC Error on Write detected by the FDE logic
   // 0x04418781: RW_IOEDC_IOECC_PARITY_ERR_ON_WRITE - Disc Xfr - IOExC parity error on write.
   // 0x04418782: RW_IOECC_PARITY_ERROR_ON_WRITE - Disc Xfr - IOECC parity error on write.
   // 0x04418783: RW_WRITE_HALT_CORRECTABLE_IOECC_ERR -  Disc Xfr - IOECC error (correctable)
   //
   //</RW_SENSE_ERROR_CODES>

#if IOEDC_ERROR_REPLACE_80_TO_41                                     // Replace HARDWARE ERROR - DATA PATH FAILURE 80 with 41
   #define RW_IOEDC_ERROR_WITHOUT_IOECC_ERROR_ON_WRITE               (0x04418780 | RW_FORCED_RETRYABLE_ERR_TYPE)
   #define RW_IOEDC_ERROR_ON_WRITE_FDE                               (0x04418701 | RW_FORCED_RETRYABLE_ERR_TYPE)

#if BUFFER_IOECC
   #define RW_IOEDC_IOECC_PARITY_ERR_ON_WRITE                        (0x04418781 | RW_FORCED_RETRYABLE_ERR_TYPE)
   #define RW_IOECC_PARITY_ERROR_ON_WRITE                            (0x04418782 | RW_FORCED_RETRYABLE_ERR_TYPE)
   #define RW_WRITE_HALT_CORRECTABLE_IOECC_ERR                       (0x04418783 | RW_FORCED_RETRYABLE_ERR_TYPE)
#endif // BUFFER_IOECC

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/41/89 Errors.
   //***************************************************************************
   // 0x84418980: RW_IOEDC_PARITY_ERR_ON_READ - Disc Xfr - IOEDC parity error on read.
   //
   //</RW_SENSE_ERROR_CODES>
   #define RW_IOEDC_PARITY_ERR_ON_READ                               0x04418980

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/80/87 Errors.
   //***************************************************************************
   // 0x04808780: RW_IOEDC_ERROR_WITHOUT_IOECC_ERROR_ON_WRITE - Disc Xfr - IOEDC parity error on write.
   // 0x04808701: RW_IOEDC_ERROR_ON_WRITE_FDE - 04/8087, FRU 01 - FDE IOEDC Error on Write detected by the FDE logic
   // 0x04808781: RW_IOEDC_IOECC_PARITY_ERR_ON_WRITE - Disc Xfr - IOExC parity error on write.
   // 0x04808782: RW_IOECC_PARITY_ERROR_ON_WRITE - Disc Xfr - IOECC parity error on write.
   // 0x04808783: RW_WRITE_HALT_CORRECTABLE_IOECC_ERR -  Disc Xfr - IOECC error (correctable).
   //
   //</RW_SENSE_ERROR_CODES>

#else // #if IOEDC_ERROR_REPLACE_80_TO_41
#if ENABLE_HOST_LBA_IODEC_SEED_FOR_MEGACACHE
   #define RW_IOEDC_ERROR_WITHOUT_IOECC_ERROR_ON_WRITE               0x04808780
#else
   #define RW_IOEDC_ERROR_WITHOUT_IOECC_ERROR_ON_WRITE               (0x04808780 | RW_FORCED_RETRYABLE_ERR_TYPE)
#endif
   #define RW_IOEDC_ERROR_ON_WRITE_FDE                               (0x04808701 | RW_FORCED_RETRYABLE_ERR_TYPE)
#if BUFFER_IOECC
   #define RW_IOEDC_IOECC_PARITY_ERR_ON_WRITE                        (0x04808781 | RW_FORCED_RETRYABLE_ERR_TYPE)
   #define RW_IOECC_PARITY_ERROR_ON_WRITE                            (0x04808782 | RW_FORCED_RETRYABLE_ERR_TYPE)
   #define RW_WRITE_HALT_CORRECTABLE_IOECC_ERR                       (0x04808783 | RW_FORCED_RETRYABLE_ERR_TYPE)
#endif // BUFFER_IOECC

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/80/89 Errors.
   //***************************************************************************
   // 0x84808980: RW_IOEDC_PARITY_ERR_ON_READ - Disc Xfr - IOEDC parity error on read.
   //
   //</RW_SENSE_ERROR_CODES>
   #define RW_IOEDC_PARITY_ERR_ON_READ                               0x04808980

#endif // #if IOEDC_ERROR_REPLACE_80_TO_41 #else

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/1D Errors.
   //***************************************************************************
   // 0x8444E100: RW_FAILED_TO_REINITIALIZE_NVC_HOST - The NVC Header couldn't be written to disc after a format
   // 0x8444E200: RW_FAILED_TO_CLEAR_NVC_HEADER - The NVC Header couldn't be erased when transitioning from NVC FW to non-NVC FW
   // 0x8444E300: RW_FAILED_TO_WRITE_NVC_DATA_TO_DISC - The NVC synchronous event handler failed
   // 0x8444E400: RW_FAILED_TO_SET_NVC_HEADER - The NVC Header couldn't be initialized
   // 0x8444E500: RW_FAILED_TO_INTIALIZE_NVC_HOST - A clean NVC header could not be successfully written to disc
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_FAILED_TO_REINITIALIZE_NVC_HOST                        0x0444E100
   #define RW_FAILED_TO_CLEAR_NVC_HEADER                             0x0444E200
   #define RW_FAILED_TO_WRITE_NVC_DATA_TO_DISC                       0x0444E300
   #define RW_FAILED_TO_SET_NVC_HEADER                               0x0444E400
   #define RW_FAILED_TO_INITIALIZE_NVC_HOST                          0x0444E500

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x4/9y/nnnn Errors - NOTE: These errors are self test unique
   //                              where nnnn = servo loop code and y = 0 - f
   //***************************************************************************
   // 0x04900000: RW_SERVO_CMD_TIMED_OUT_WLOOPCODE - (0490nnnn) Servo command timed out with servo loop code appended.
   // 0x04910000: RW_SEEK_TIMED_OUT_WLOOPCODE - (0490nnnn) Seek operation timed out with servo loop code appended.
   // 0x04920000: RW_UNRECOVERED_SEEK_WLOOPCODE - (0490nnnn) Unrecovered seek error encountered with servo loop code appended.
   // 0x04930000: RW_SERVO_CMD_FAILED_WLOOPCODE - (0490nnnn) Servo command failed with servo loop code appended.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_SERVO_CMD_TIMED_OUT_WLOOPCODE                          0x04900000
   #define RW_SEEK_TIMED_OUT_WLOOPCODE                               0x04910000
   #define RW_UNRECOVERED_SEEK_WLOOPCODE                             0x04920000
   #define RW_SERVO_CMD_FAILED_WLOOPCODE                             0x04930000

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x5/24 Errors.
   //***************************************************************************
   // 0x05240001: RW_INVALID_CDB_ERROR - Invalid parameter in command descriptor block.
   // 0x0524F380: RW_G_TO_P_WHILE_FORMATTED_WITHOUT_PLIST - G->P operation requested while drive was formatted w/o PLIST.
   // 0x0524F381: RW_SERVO_FLAW_ALREADY_EXISTS - Add Primary Servo Flaw - Servo Flaw already exists in ASFT or PSFT.
   // 0x0524F382: RW_G_TO_P_PLIST_OVERLAP - G->P operation encountered a G-list entry that overlaps an existing P-list entry.
   // 0x0524F383: RW_G_TO_P_SERVO_FLAW_OVERLAP - G->P operation encountered a Growth Servo Flaw which overlapped an existing Primary defect Servo Flaw.
   // 0x0524F384: RW_DEFECTS_REPORT_LISTS_NOT_AVAILABLE - Defects report lists not available for retrieval.
   // 0x0524F385: RW_SERVO_FLAW_NOT_EXISTS - Remove Primary Servo Flaw - Servo Flaw doesn't exist in ASFT
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_INVALID_CDB_ERROR                                      0x05240001
#if GLIST_TO_PLIST
   #define RW_G_TO_P_WHILE_FORMATTED_WITHOUT_PLIST                   0x0524F380
#endif
#if GLIST_TO_PLIST_ADD_DEFECT_COMMAND
   #define RW_SERVO_FLAW_ALREADY_EXISTS                              0x0524F381
#endif
#if GLIST_TO_PLIST
   #define RW_G_TO_P_PLIST_OVERLAP                                   0x0524F382
   #define RW_G_TO_P_SERVO_FLAW_OVERLAP                              0x0524F383
#endif
   #define RW_SERVO_FLAW_NOT_EXISTS                                  0x0524F385

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x5/26 Errors.
   //***************************************************************************
   // 0x05260080: RW_INVALID_CYLINDER_ERR - Validate Sector Position - Invalid input cylinder.
   // 0x05260081: RW_INVALID_HEAD_ERR - Validate Sector Position - Invalid input head.
   // 0x05260082: RW_INVALID_SECTOR_ERR - Validate Sector Position - Invalid input sector.
   // 0x05260083: RW_INVALID_USER_LBA_01 - Perform Address Translation - Input LBA is invalid.
   // 0x05260084: RW_INVALID_USER_LBA_02 - Perform Address Translation - Input LBA is invalid.
   // 0x05260085: RW_INVALID_USER_LBA_03 - Perform Address Translation - Input LBA is invalid.
   // 0x05260086: RW_INVALID_SYSTEM_LBA - Perform Address Translation - Input LBA is invalid.
   // 0x05260087: RW_CLIENT_DEFECT_LIST_INVALID_SIZE - Format - Client defect list size is invalid.
   // 0x05260088: RW_CLIENT_DEFECT_LIST_INVALID_OFFSET_SORT - Process Defect Lists - Sort error due to invalid offset.
   // 0x05260089: RW_CLIENT_DEFECT_LIST_INVALID_HEAD_SORT - Process Defect Lists - Sort error due to invalid head.
   // 0x0526008A: RW_CLIENT_DEFECT_LIST_INVALID_CYL_SORT - Process Defect Lists - Sort error due to invalid cylinder.
   // 0x0526008B: RW_CLIENT_DEFECT_LIST_SYMBOL_EXTENT_INFO_ERR - Process Defect Lists - Failed to validate a client specified symbol extent info.
   // 0x0526008C: RW_CLIENT_DEFECT_LIST_SEC_EXTENT_INFO_ERR - Process Defect Lists - Failed to validate a client specified sector extent info.
   // 0x0526008D: RW_CLIENT_DEFECT_LIST_INVALID_TRACK - Process Defect Lists - Invalid track in client defect list entry.
   // 0x0526008E: RW_FTRK_INVALID_TRACK - Track Format - Input track is invalid.
   // 0x0526008F: RW_FTRK_INVALID_LBA - Track Format - First LBA of input track is invalid.
   // 0x05260090: RW_INVALID_READ_SERVO_DATA_BLOCK_COUNT - Read Servo Data Block Memory - Invalid length.
   // 0x05260091: RW_INVALID_READ_SERVO_PROGRAM_BLOCK_COUNT - Read Servo Program Block Memory - Invalid length.
   // 0x05260092: RW_INVALID_USER_PBA_01 - Perform Address Translation - Input PBA is invalid.
   // 0x05260093: RW_INVALID_SYMBOL_EXTENT_INFO - Perform Address Translation - Input symbol extent is invalid.
   // 0x05260094: RW_SUPER_SECTOR_INVALID_WEDGE_XFR_SIZE - Super Sector Transfer - Invalid wedge transfer size.
   // 0x05260095: RW_TRACK_ZLR_INVALID_PARTITION - Track ZLR Transfer - Invalid partition.
   // 0x05260096: RW_TRACK_ZLR_INVALID_LBA_RANGE - Track ZLR Transfer - Invalid LBA range on target track.
   // 0x05260097: RW_TRACK_ZLR_REALLOCATED_LBA_FOUND - Track ZLR Transfer - Reallocated LBA found on target track.
   // 0x05260098: RW_INVALID_USER_LBA_04 - Perform Address Translation - Input LBA is invalid.
   // 0x05260099: RW_INVALID_USER_LBA_05 - Perform Address Translation - Input LBA is invalid.
   // 0x0526009A: RW_CONVERT_SECTOR_TO_RLL_UNSUPPORTED_SECTOR_SIZE - Convert Sector to RLL Data - Unsupported sector size.
   // 0x0526009B: RW_ADD_SERVO_FLAW_INVALID_INPUT_ENTRY - Add Servo Flaw - Invalid input specified.
   // 0x0526009C: RW_ENABLE_SERVO_FREE_FALL_PROTECTION_FAILED_DRIVE_NOT_SPINNING - Invalid condition for enabling servo free fall protection (drive not spinning).
   // 0x0526009D: RW_DISABLE_SERVO_FREE_FALL_PROTECTION_FAILED_DRIVE_NOT_SPINNING - Invalid condition for disabling servo free fall protection (drive not spinning).
   // 0x0526009E: RW_DISABLE_SERVO_FREE_FALL_PROTECTION_FAILED_PROTECTION_ALREADY_DISABLED - Invalid condition for disabling servo free fall protection (protection already disabled).
   // 0x0526009F: RW_DISABLE_SERVO_FREE_FALL_PROTECTION_FAILED_PROTECTION_DEACTIVATED - Invalid condition for disabling servo free fall protection (protection already de-activated).
   // 0x052600A0: RW_DISABLE_SERVO_FREE_FALL_PROTECTION_FAILED_FREE_FALL_ACTIVE - Invalid condition for disabling servo free fall protection (free-fall condition is currently active).
   // 0x052600A1: RW_INVALID_DRIVE_FREE_FALL_CONTROL_OPTION - Invalid drive free-fall control option specified.
   // 0x052600A2: RW_CHECK_FREE_FALL_EVENT_FAILED_PROTECTION_NOT_FUNCTIONAL - Check free-fall event failed - protection not functional.
   // 0x052600A3: RW_SECTOR_XFR_INVALID_SECTOR_RANGE - Invalid sector range specified.
   // 0x052600A4: RW_UPDATE_DATA_SCRUB_LIST_INVALID_COUNT - Invalid count value specified for update.
   // 0x052600A5: RW_CHANNEL_MEMORY_INVALID_MEMORY_SELECT - Invalid channel memory select specified for access.
   // 0x052600A6: RW_CHANNEL_MEMORY_INVALID_BUFFER_INDEX - Invalid buffer index specified for read channel memory access.
   // 0x052600A7: RW_CHANNEL_MEMORY_INVALID_START_ADDR - Invalid start address specified for read channel memory access.
   // 0x052600A8: RW_CHANNEL_MEMORY_INVALID_XFR_LENGTH - Invalid transfer length specified for read channel memory access.
   // 0x052600A9: RW_INVALID_SECTOR_EXTENT_INFO - Invalid sector extent info
   // 0x052600AA: RW_TRK_SP_CALC_INVALID_PARTITION - Invalid partition specified for track Super Parity attributes calculation.
   // 0x052600AB: RW_TRK_SP_CALC_LBA_RANGE_INVALID - Target track does not have a valid LBA range.
   // 0x052600AC: RW_SP_XLATION_INVALID_USER_LBA_01 - Inline Super Parity translation - invalid User LBA.
   // 0x052600AD: RW_SP_XLATION_INVALID_DISC_LBA_01 - Inline Super Parity translation - invalid Disc LBA.
   // 0x052600AE: RW_SP_XLATION_INVALID_DISC_LBA_02 - Inline Super Parity translation - invalid Disc LBA.
   // 0x052600AF: RW_SP_XLATION_INVALID_DISC_LBA_03 - Inline Super Parity translation - invalid Disc LBA.
   // 0x052600B0: RW_SP_XLATION_INVALID_DISC_LBA_04 - Inline Super Parity translation - invalid Disc LBA.
   // 0x052600B1: RW_SP_XLATION_INVALID_SUPER_BLK_ADDR_01 - Inline Super Parity translation - invalid Super Block Address.
   // 0x052600B2: RW_SP_XLATION_INVALID_PARITY_LBA_01 - Inline Super Parity translation - invalid Parity LBA.
   // 0x052600B3: RW_BAND_XLATION_INVALID_INPUT_TYPE - Invalid input request for band translation.
   // 0x052600B4: RW_BAND_XLATION_INVALID_OUTPUT_TYPE - Invalid output request for band translation.
   // 0x052600B5: RW_BAND_XLATION_INVALID_INPUT_BAND_ID_01 - Invalid band input.
   // 0x052600B6: RW_BAND_XLATION_INVALID_INPUT_BAND_ID_02 - Invalid band input.
   // 0x052600B7: RW_BAND_XLATION_INVALID_INPUT_TRACK_POSITION - Band translation - Invalid input track position specified.
   // 0x052600B8: RW_BAND_XLATION_INVALID_INPUT_RAP_ZONE_OR_HEAD - Band translation - Invalid input RAP zone/head value(s) specified.
   // 0x052600B9: RW_INVALID_BAND_NUMBER_ERR - Invalid band number.
   // 0x052600BA: RW_INVALID_BAND_LBA_OFFSET_ERR - Invalid band lba offset.
   // 0x052600BB: RW_INVALID_USER_LBA_06 - Invalid user lba.
   // 0x052600BC: RW_CYL_DATA_CYL_POSITION_MISMATCH - The position request for seek and write/read are out of sync.
   // 0x052600BD: RW_INVALID_PARAMETER - No Description Added @@@
   // 0x052600BE: RW_FAFH_INVALID_PASSIVE_CLEARANCE - No Description Added @@@
   // 0x052600C2: RW_BAND_XLATION_INVALID_INPUT_LBA - Invalid input LBA specified for band translation.
   // 0x052600C3: RW_BAND_XLATION_INVALID_INPUT_PBA - Invalid input PBA specified for band translation.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_INVALID_CYLINDER_ERR                                                     0x05260080
   #define RW_INVALID_HEAD_ERR                                                         0x05260081
   #define RW_INVALID_SECTOR_ERR                                                       0x05260082
   #define RW_INVALID_USER_LBA_01                                                      0x05260083
   #define RW_INVALID_USER_LBA_02                                                      0x05260084
   #define RW_INVALID_USER_LBA_03                                                      0x05260085
   #define RW_INVALID_SYSTEM_LBA                                                       0x05260086
   #define RW_CLIENT_DEFECT_LIST_INVALID_SIZE                                          0x05260087
   #define RW_CLIENT_DEFECT_LIST_INVALID_OFFSET_SORT                                   0x05260088
   #define RW_CLIENT_DEFECT_LIST_INVALID_HEAD_SORT                                     0x05260089
   #define RW_CLIENT_DEFECT_LIST_INVALID_CYL_SORT                                      0x0526008A
   #define RW_CLIENT_DEFECT_LIST_SYMBOL_EXTENT_INFO_ERR                                0x0526008B
   #define RW_CLIENT_DEFECT_LIST_SEC_EXTENT_INFO_ERR                                   0x0526008C
   #define RW_CLIENT_DEFECT_LIST_INVALID_TRACK                                         0x0526008D
   #define RW_FTRK_INVALID_TRACK                                                       0x0526008E
   #define RW_FTRK_INVALID_LBA                                                         0x0526008F
   #define RW_INVALID_READ_SERVO_DATA_BLOCK_COUNT                                      0x05260090
   #define RW_INVALID_READ_SERVO_PROGRAM_BLOCK_COUNT                                   0x05260091
   #define RW_INVALID_USER_PBA_01                                                      0x05260092
   #define RW_INVALID_SYMBOL_EXTENT_INFO                                               0x05260093
   #define RW_SUPER_SECTOR_INVALID_WEDGE_XFR_SIZE                                      0x05260094
   #define RW_INVALID_USER_LBA_04                                                      0x05260098
   #define RW_INVALID_USER_LBA_05                                                      0x05260099
   #define RW_CONVERT_SECTOR_TO_RLL_UNSUPPORTED_SECTOR_SIZE                            0x0526009A

#if RW_UPDATE_ACTIVE_SERVO_FLAW_ENTRIES_APIS
   #define RW_ADD_SERVO_FLAW_INVALID_INPUT_ENTRY                                       0x0526009B
#endif
#if SERVO_FREE_FALL_PROTECTION_SUPPORT
   #define RW_ENABLE_SERVO_FREE_FALL_PROTECTION_FAILED_DRIVE_NOT_SPINNING              0x0526009C
   #define RW_DISABLE_SERVO_FREE_FALL_PROTECTION_FAILED_DRIVE_NOT_SPINNING             0x0526009D
   #define RW_DISABLE_SERVO_FREE_FALL_PROTECTION_FAILED_PROTECTION_ALREADY_DISABLED    0x0526009E
   #define RW_DISABLE_SERVO_FREE_FALL_PROTECTION_FAILED_PROTECTION_DEACTIVATED         0x0526009F
   #define RW_DISABLE_SERVO_FREE_FALL_PROTECTION_FAILED_FREE_FALL_ACTIVE               0x052600A0
#endif
#if DRIVE_FREE_FALL_PROTECTION_SUPPORT
   #define RW_INVALID_DRIVE_FREE_FALL_CONTROL_OPTION                                   0x052600A1
   #define RW_CHECK_FREE_FALL_EVENT_FAILED_PROTECTION_NOT_FUNCTIONAL                   0x052600A2
#endif
#if RW_SECTOR_XFR_SUPPORT
   #define RW_SECTOR_XFR_INVALID_SECTOR_RANGE                                          0x052600A3
#endif
#if (F3_CERT_AND_DIAG && RW_LIMIT_SOFT_REALLOCATION_ATTEMPTS)
   #define RW_UPDATE_DATA_SCRUB_LIST_INVALID_COUNT                                     0x052600A4
#endif

   #define RW_CHANNEL_MEMORY_INVALID_MEMORY_SELECT                                     0x052600A5
   #define RW_CHANNEL_MEMORY_INVALID_BUFFER_INDEX                                      0x052600A6
   #define RW_CHANNEL_MEMORY_INVALID_START_ADDR                                        0x052600A7
   #define RW_CHANNEL_MEMORY_INVALID_XFR_LENGTH                                        0x052600A8
   #define RW_INVALID_SECTOR_EXTENT_INFO                                               0x052600A9

//#if INLINE_PARITY_SECTORS
   #define RW_TRK_SP_CALC_INVALID_PARTITION                                            0x052600AA
   #define RW_TRK_SP_CALC_LBA_RANGE_INVALID                                            0x052600AB
   #define RW_SP_XLATION_INVALID_USER_LBA_01                                           0x052600AC
   #define RW_SP_XLATION_INVALID_DISC_LBA_01                                           0x052600AD
   #define RW_SP_XLATION_INVALID_DISC_LBA_02                                           0x052600AE
   #define RW_SP_XLATION_INVALID_DISC_LBA_03                                           0x052600AF
   #define RW_SP_XLATION_INVALID_DISC_LBA_04                                           0x052600B0
   #define RW_SP_XLATION_INVALID_SUPER_BLK_ADDR_01                                     0x052600B1
   #define RW_SP_XLATION_INVALID_PARITY_LBA_01                                         0x052600B2
//#endif // #if INLINE_PARITY_SECTORS

   #define RW_BAND_XLATION_INVALID_INPUT_TYPE                                          0x052600B3
   #define RW_BAND_XLATION_INVALID_OUTPUT_TYPE                                         0x052600B4
   #define RW_BAND_XLATION_INVALID_INPUT_BAND_ID_01                                    0x052600B5
   #define RW_BAND_XLATION_INVALID_INPUT_BAND_ID_02                                    0x052600B6
   #define RW_BAND_XLATION_INVALID_INPUT_TRACK_POSITION                                0x052600B7
   #define RW_BAND_XLATION_INVALID_INPUT_RAP_ZONE_OR_HEAD                              0x052600B8

#if RW_BAND_ACCESS_SUPPORT
   #define RW_INVALID_BAND_NUMBER_ERR                                                  0x052600B9
   #define RW_INVALID_BAND_LBA_OFFSET_ERR                                              0x052600BA
   #define RW_INVALID_USER_LBA_06                                                      0x052600BB
#endif
// if LOGICAL_DATA_CYLINDER_SUPPORT
   #define RW_CYL_DATA_CYL_POSITION_MISMATCH                                           0x052600BC
// endif
   #define RW_INVALID_PARAMETER                                                        0x052600BD
   #define RW_FAFH_INVALID_PASSIVE_CLEARANCE                                           0x052600BE

// #if FE_0211939_379594_H2SAT_SUPPORT
   #define RW_TST_TRK_DFCT_TBL_ADD_GROWN_DEFECT_PARAM_INVALID                          0x052600BF
   #define RW_TST_TRK_DFCT_TBL_ADD_GROWN_DEFECT_THRESHOLD_REACHED                      0x052600C0
   #define RW_TST_TRK_DFCT_TBL_ADD_GROWN_DEFECT_ALREADY_EXISTS                         0x052600C1
// #endif
   #define RW_BAND_XLATION_INVALID_INPUT_LBA                                           0x052600C2
   #define RW_BAND_XLATION_INVALID_INPUT_PBA                                           0x052600C3


   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal x9/80 Errors.
   //***************************************************************************
   // 0x09800082: RW_FW_ERR_START_ERR_CODE - First error code of RW firmware errors
   // 0x89800082: RW_UNSUPPORTED_FAULT - Unsupported fault.
   // 0x89800083: RW_TRACK_ADDR_FAULT - Track address fault.
   // 0x89800084: RW_SERVO_DISC_SYNC_ERR - Disc Xfr - Servo-Disc synchronization error.
   // 0x89800085: RW_UNKNOWN_ENDING_BLK_ADDR - Disc Xfr - End of transfer reached prematurely.
   // 0x89800086: RW_UNKNOWN_SEQ_TIMEOUT_ERR - Disc Xfr - Unexpected sequencer timeout error.
   // 0x89800087: RW_UNKNOWN_NRZ_XFR_ERR - Disc Xfr - Unknown error in the NRZ Transfer logic.
   // 0x89800088: RW_UNKNOWN_EDAC_ERR - Disc Xfr - Unknown EDAC error.
   // 0x89800089: RW_UNKNOWN_MM_ERR - Disc Xfr - Unknown Media Manager's error.
   // 0x8980008A: RW_INVALID_DISC_HALT - Disc Xfr - Invalid disc halt.
   // 0x8980008B: RW_UNEXPECTED_SEQ_HALT - Disc Xfr - Unexpected sequencer halt condition.
   // 0x8980008C: RW_UNEXPECTED_SMART_SEQ_HALT - Super Sector - Unexpected sequencer halt.
   // 0x8980008D: RW_UNKNOWN_SMART_SEQ_TIMEOUT_ERR - Super Sector - Unknown sequencer timeout error.
   // 0x8980008E: RW_UNKNOWN_NRZ_INTF_ERR - Disc Xfr - Unknown NRZ interface error.
   // 0x8980008F: RW_XFR_SOFT_HALTED - Disc Xfr - Disc was soft halted.
   // 0x89800090: RW_XFR_FAULT - Disc Xfr - Fault condition error.
   // 0x89800091: RW_CORR_BFR_COMPLETION_TIMEOUT - Disc Xfr - Correct Buffer Completion timeout error.
   // 0x89800094: RW_RECOVERED_SEEK - Seek - Recovered seek error encountered.
   // 0xC9800095: RW_FORCED_ER_BEFORE_ERROR_ENCOUNTERED - Forced to enter error recvoery before error is encountered.
   // 0x89800096: RW_RECOVERED_SERVO_CMD - Recovered servo command error.
   // 0x89800097: RW_PARTIAL_REALLOCATION_PERFORMED - Reallocate Block - Partial reallocation performed.
   // 0x89800098: RW_XFR_TRUNCATED - Disc Xfr - Transfer was truncated.
   // 0x89800099: RW_XFR_SATISFIED - Disc Xfr - Transfer completed.
   // 0x8980009A: RW_XFR_TRACK_SATISFIED - Disc Xfr - Track transfer completed.
   // 0x8980009B: RW_SCAN_DEFECT_ADJ_SECTORS_TIME_EXCEEDED - Scan Defect - Allocated scan time exceeded.
   // 0x8980009C: RW_IOEDC_IOECC_PARITY_ERR_ON_WRITE - Disc Xfr - IMPOSSIBLE - IOECC parity error on write
   // 0x8980009D: RW_IOECC_PARITY_ERROR_ON_WRITE - Disc Xfr - IMPOSSIBLE - IOECC parity error on write
   // 0x8980009E: RW_WRITE_HALT_CORRECTABLE_IOECC_ERR - Disc Xfr - IMPOSSIBLE - IOECC error (correctable)
   // 0x8980009F: RW_EDAC_HALTED_FOR_FW_ERASURE - EDAC stopped for FW erasure
   // 0x898000A0: RW_INVALID_BLOCK_FOR_UNMARK_PENDING_REALLOCATION - Reallocate Block - Input was not marked for pending reallocation.
   // 0x898000A1: RW_INPUT_LBA_NOT_FOUND_IN_RST - RST Mgr - Input LBA was not found in the RST.
   // 0x898000A2: RW_RESIDENT_DST_DOES_NOT_CONTAIN_TARGET_PBA_01 - DST Mgr - Input PBA was not found in the resident DST.
   // 0x898000A3: RW_RESIDENT_DST_DOES_NOT_CONTAIN_TARGET_PBA_02 - DST Mgr - Input PBA was not found in the resident DST.
   // 0x898000A4: RW_DST_SKOOTCH_FAILED_01 - DST Mgr - Skootch failed.
   // 0x898000A5: RW_DST_SKOOTCH_FAILED_02 - DST Mgr - Skootch failed.
   // 0x898000A6: RW_DST_INSERT_FAILED - DST Mgr - Insert failed.
   // 0x898000A7: RW_CORRECTION_BUFFER_ERR - Correction Buffer over-run, under-run, or EDC error.
   // 0x898000A8: RW_FORM_FIFO_ERROR - Form FIFO over/under run error due to workaround for LSI issue 2822.
   // 0x898000A9: RW_ACTIVE_POWER_TRANSITION_FAILED - Failed to transition to active power.
   // 0x898000AA: RW_MARK_BLOCK_LOGGED_PERFORMED - Input LBA was marked as logged.
   // 0x098000AB: RW_SERVO_FLAW_COAST_MAX_FLAWS_PER_TRK_EXCEEDED - Format - Max number of servo flaws per track exceeded in servo coast.
   // 0x098000AC: RW_FORMAT_WRITE_SERVO_UNSAFE_MULTIPLE_FLAWS_PER_TRK - Format - Write servo unsafe errors when the track already has multiple flaws.
   // 0x098000AD: RW_XFR_FORMATTER_PARITY_RAM_SYNC_ERROR - Disc Xfr - Formatter's parity RAM progress is not in sync with transfer.
   // 0x098000AE: RW_PARITY_XFR_REQ_RESOURCE_CONFLICT - Disc Xfr - Conflict of R/W request resource.
   // 0x098000AF: RW_SUPER_BLK_WRITE_REQ_RESOURCE_CONFLICT - Disc Xfr - Conflict of R/W request resource during attempt to write super block data.
   // 0x898000B0: RW_ALT_XFR_FORM_PARITY_RAM_SYNC_ERROR - Disc Xfr - Formatter's parity RAM progress is not in sync with alternate transfer.
   // 0x898000B1: RW_FORM_SP_RAM_INVALID_FOR_PARITY_SECS_UPDATE - Disc Xfr - Formatter's parity RAM is invalid for parity sectors update.
   // 0x898000B2: RW_FORM_SP_RAM_INVALID_FOR_PARITY_SECS_ALT_UPDATE - Disc Xfr - Formatter's parity RAM is invalid for parity sectors alternate-update.
   // 0x898000B3: RW_SUPER_BLK_READ_PARITY_SECS_NOT_REALLOCATED - Disc Xfr - Parity sectors read of expected reallocated sectors which were not reallocated.
   // 0x898000B4: RW_SUPER_BLK_WRITE_PARITY_SECS_NOT_REALLOCATED - Disc Xfr - Parity sectors write of expected reallocated sectors which were not reallocated.
   // 0x898000B5: RW_PVT_NOT_VALID_ON_SUCCESSFUL_FORMAT - Format - Parity Validity Table not showing all super blocks valid on successful format.
   // 0x898000B8: RW_SEC_DATA_REGEN_RESTART_FAILED - Sector Data Regeneration - Restart of transfer failed.
   // 0x898000B9: RW_FORMAT_DIRTY_SUPER_BLK_NOT_IN_PVT - Format - Dirty super block found on media - but not reported in PVT.
   // 0x898000BA: RW_SUPER_BLK_READ_NO_USER_SECTORS_AVAILABLE - Super Block Read - No user sectors available.
   // 0x898000BB: RW_FULL_REALLOCATION_SUPPORT_NOT_AVAILABLE_01 - Full R/W reallocation code support is not available.
   // 0x898000BC: RW_FULL_REALLOCATION_SUPPORT_NOT_AVAILABLE_02 - Full R/W reallocation code support is not available.
   // 0x898000BD: RW_FULL_REALLOCATION_SUPPORT_NOT_AVAILABLE_03 - Full R/W reallocation code support is not available.
   // 0x098000BE: RW_SUPER_BLK_DATA_RECOVERED - Super Block Read - Recovered Data using SuperC Block.
   // 0x898000BF: RW_ATIC_DATA_RECOVERED - ATIC DERPR Retry - Recovered Data using DERP ATIC retry.
   // 0x898000C0: RW_RECOVERED_SEEK_DUE_TO_PZT_CAL_REQUEST_ONLY - Seek - Recovered seek status due to PZT calibration request only.
   // 0x098000C1: RW_INTERMEDIATE_SUPER_PARITY_RECOVERED - Recovered Data using Intermediate Super Parity
   // 0x898000C4: RW_INVALID_LBA_FOR_UNDO_TORN_WRITE - Undo Torn Write Protection - Input LBA was not protected from torn write.
   // 0x898000C5: RW_SERVO_COPY_FORMATTER_XFR_NOT_HALTED - Servo Copy - Formatter transfer did not halt properly.
   // 0x898000C6: RW_DC_CALIBRATION_FAILED - Servo DC calibration failed.
   // 0x898000C7: RW_FORMAT_UPDATE_DIRTY_SUPER_BLKS_INVALID_BAND_LBA_RANGE - Format - Invalid band LBA range encountered during dirty super blocks update attempt
   // 0xC98000C8: RW_INVALID_XFR_SATISFIED - Difference between DDM and MM at the end of transfer
   // 0x898000C9: RW_FORM_FIFO_PTR_SYNC_LOSS_ERROR - Disc Xfr - Detect Formatter FIFO pointer synchronization loss error.
   // 0x898000CA: RW_FULL_REALLOCATION_SUPPORT_NOT_AVAILABLE_04 - Entire Reallocation support not available
   // 0x898000CB: RW_INVALID_BLOCK_FOR_UNMARK_DART_PENDING_REALLOCATION - Invalid input LBA for unmark DART pending realloc request.
   // 0x898000CC: RW_MARK_PENDING_DART_SKIPPED - Marking of Pending DART entry has been skipped.
   // 0x898000CD: RW_OUTER_CODE_RECOVERY_SCRATCH_BUFFER_INSUFFICIENT - Scratch Buffer used during Outer Code recovery is insufficient.
   // 0x098000CE: RW_FWIOC_RECOVERED - Recovered Data using FWIOC
   // 0x098000FF: RW_FW_ERR_END_ERR_CODE - Last error code of RW firmware errors
   //</RW_SENSE_ERROR_CODES>

   #define RW_FW_ERR_START_ERR_CODE                                  0x09800082

   #define RW_UNSUPPORTED_FAULT                                      0x09800082
   #define RW_TRACK_ADDR_FAULT                                       0x09800083
   #define RW_SERVO_DISC_SYNC_ERR                                    0x09800084
   #define RW_UNKNOWN_ENDING_BLK_ADDR                                0x09800085
   #define RW_UNKNOWN_SEQ_TIMEOUT_ERR                                0x09800086
   #define RW_UNKNOWN_NRZ_XFR_ERR                                    0x09800087
   #define RW_UNKNOWN_EDAC_ERR                                       0x09800088
   #define RW_UNKNOWN_MM_ERR                                         0x09800089
   #define RW_INVALID_DISC_HALT                                      0x0980008A
#if WA_0306620_503196_MAKE_RW_UNEXPECTED_SEQ_HALT_RETRYABLE
   #define RW_UNEXPECTED_SEQ_HALT                                    (0x0980008B | RW_RETRYABLE_ERR_TYPE)
#else
   #define RW_UNEXPECTED_SEQ_HALT                                    0x0980008B
#endif
   #define RW_UNEXPECTED_SMART_SEQ_HALT                              0x0980008C
   #define RW_UNKNOWN_SMART_SEQ_TIMEOUT_ERR                          0x0980008D
// #define RW_UNKNOWN_NRZ_INTF_ERR                                   0x0980008E
   #define RW_XFR_SOFT_HALTED                                        0x0980008F
   #define RW_XFR_FAULT                                              0x09800090

#if !SFT_FIRMWARE
   #define RW_CORR_BFR_COMPLETION_TIMEOUT                            (0x09800091 | RW_RETRYABLE_ERR_TYPE )
#else
   #define RW_CORR_BFR_COMPLETION_TIMEOUT                            0x09800091
#endif

   #define RW_RECOVERED_SEEK                                         0x09800094
   #define RW_FORCED_ER_BEFORE_ERROR_ENCOUNTERED                     (0x09800095 | RW_RETRYABLE_ERR_TYPE)
   #define RW_RECOVERED_SERVO_CMD                                    0x09800096
   #define RW_PARTIAL_REALLOCATION_PERFORMED                         0x09800097
   #define RW_XFR_TRUNCATED                                          0x09800098
   #define RW_XFR_SATISFIED                                          0x09800099
   #define RW_XFR_TRACK_SATISFIED                                    0x0980009A

#if DSTEST_ATA || ENHANCED_DST || DSTEST_SCSI
   #define RW_SCAN_DEFECT_ADJ_SECTORS_TIME_EXCEEDED                  0x0980009B
#endif // DSTEST_ATA || ENHANCED_DST || DSTEST_SCSI
#if ( ! BUFFER_IOECC )
   #define RW_IOEDC_IOECC_PARITY_ERR_ON_WRITE                        (0x0980009C | RW_FORCED_RETRYABLE_ERR_TYPE)
   #define RW_IOECC_PARITY_ERROR_ON_WRITE                            (0x0980009D | RW_FORCED_RETRYABLE_ERR_TYPE)
   #define RW_WRITE_HALT_CORRECTABLE_IOECC_ERR                       (0x0980009E | RW_FORCED_RETRYABLE_ERR_TYPE)
#endif

   #define RW_EDAC_HALTED_FOR_FW_ERASURE                             0x0980009F
   #define RW_INVALID_BLOCK_FOR_UNMARK_PENDING_REALLOCATION          0x098000A0
   #define RW_INPUT_LBA_NOT_FOUND_IN_RST                             0x098000A1
   #define RW_RESIDENT_DST_DOES_NOT_CONTAIN_TARGET_PBA_01            0x098000A2
   #define RW_RESIDENT_DST_DOES_NOT_CONTAIN_TARGET_PBA_02            0x098000A3
   #define RW_DST_SKOOTCH_FAILED_01                                  0x098000A4
   #define RW_DST_SKOOTCH_FAILED_02                                  0x098000A5
   #define RW_DST_INSERT_FAILED                                      0x098000A6

   #define RW_CORRECTION_BUFFER_ERR                                  ( 0x098000A7 | RW_RETRYABLE_ERR_TYPE )
   #define RW_FORM_FIFO_ERROR                                        (0x098000A8 | RW_FORCED_RETRYABLE_ERR_TYPE)
   #define RW_ACTIVE_POWER_TRANSITION_FAILED                         0x098000A9

   #define RW_MARK_BLOCK_LOGGED_PERFORMED                            0x098000AA

//#if RW_FORMAT_DEALLOCATE_TRACK_MANY_SERVO_FLAWS_PER_TRACK
   #define RW_SERVO_FLAW_COAST_MAX_FLAWS_PER_TRK_EXCEEDED            0x098000AB
   #define RW_FORMAT_WRITE_SERVO_UNSAFE_MULTIPLE_FLAWS_PER_TRK       0x098000AC
//#endif

#if INLINE_PARITY_SECTORS
   #define RW_XFR_FORMATTER_PARITY_RAM_SYNC_ERROR                    0x098000AD
   #define RW_SUPER_BLK_READ_REQ_RESOURCE_CONFLICT                   0x098000AE
   #define RW_SUPER_BLK_WRITE_REQ_RESOURCE_CONFLICT                  0x098000AF
   #define RW_ALT_XFR_FORM_PARITY_RAM_SYNC_ERROR                     0x098000B0
   #define RW_FORM_SP_RAM_INVALID_FOR_PARITY_SECS_UPDATE             0x098000B1
   #define RW_FORM_SP_RAM_INVALID_FOR_PARITY_SECS_ALT_UPDATE         0x098000B2
   #define RW_SUPER_BLK_READ_PARITY_SECS_NOT_REALLOCATED             0x098000B3
   #define RW_SUPER_BLK_WRITE_PARITY_SECS_NOT_REALLOCATED            0x098000B4
   #define RW_PVT_NOT_VALID_ON_SUCCESSFUL_FORMAT                     0x098000B5
   #define RW_SEC_DATA_REGEN_RESTART_FAILED                          0x098000B8
   #define RW_FORMAT_DIRTY_SUPER_BLK_NOT_IN_PVT                      0x098000B9
   #define RW_SUPER_BLK_READ_NO_USER_SECTORS_AVAILABLE               0x098000BA
#endif

   #define RW_FULL_REALLOCATION_SUPPORT_NOT_AVAILABLE_01             0x098000BB
   #define RW_FULL_REALLOCATION_SUPPORT_NOT_AVAILABLE_02             0x098000BC
   #define RW_FULL_REALLOCATION_SUPPORT_NOT_AVAILABLE_03             0x098000BD
   #define RW_SUPER_BLK_DATA_RECOVERED                               0x098000BE
   #define RW_ATIC_DATA_RECOVERED                                    0x098000BF
   #define RW_RECOVERED_SEEK_DUE_TO_PZT_CAL_REQUEST_ONLY             (0x098000C0 | RW_RETRYABLE_ERR_TYPE)
   #define RW_INTERMEDIATE_SUPER_PARITY_RECOVERED                    0x098000C1
#if SERVO_COPY_BUILD
   #define RW_SERVO_COPY_FORMATTER_XFR_NOT_HALTED                    0x098000C5
#endif
   #define RW_DC_CALIBRATION_FAILED                                  0x098000C6
#if (INLINE_PARITY_SECTORS && RW_SHINGLED_MEDIA_SUPPORT)
   #define RW_FORMAT_UPDATE_DIRTY_SUPER_BLKS_INVALID_BAND_LBA_RANGE  0x098000C7
#endif
   #define RW_INVALID_XFR_SATISFIED                                  (0x098000C8 | RW_RETRYABLE_ERR_TYPE)
   #define RW_FORM_FIFO_PTR_SYNC_LOSS_ERROR                          (0x098000C9 | RW_CONDITIONAL_RETRY_OPTION)
   #define RW_OUTER_CODE_RECOVERY_SCRATCH_BUFFER_INSUFFICIENT        0x098000CD
   #define RW_FWIOC_RECOVERED                                        0x098000CE

   #define RW_FW_ERR_END_ERR_CODE                                    0x098000FF

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal xB/FC/ Errors.
   //***************************************************************************
   // 0x0B0C0E01: RW_WRT_SEEK_TO_BAD_HEAD_ATTEMPTED - DiscXfr - RAID_REBUILD_ASSIST: Write transfer attempted a seek to a mapped out head.
   // 0x0B0C0E02: RW_WRT_ALTERNATE_BLK_MAPS_TO_BAD_HEAD - DiscXfr - RAID_REBUILD_ASSIST: Write transfer encountered a reallocated block on a mapped out head.
   // 0x0B110302: RW_READ_SEEK_TO_BAD_HEAD_ATTEMPTED - DiscXfr - RAID_REBUILD_ASSIST: Read transfer attempted a seek to a mapped out head.
   // 0x0B110303: RW_READ_ALTERNATE_BLK_MAPS_TO_BAD_HEAD - DiscXfr - RAID_REBUILD_ASSIST: Read transfer encountered a reallocated block on a mapped out head.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_WRT_SEEK_TO_BAD_HEAD_ATTEMPTED                         0x0B0C0E01
   #define RW_WRT_ALTERNATE_BLK_MAPS_TO_BAD_HEAD                     0x0B0C0E02
   #define RW_READ_SEEK_TO_BAD_HEAD_ATTEMPTED                        0x0B110302
   #define RW_READ_ALTERNATE_BLK_MAPS_TO_BAD_HEAD                    0x0B110303

   //<RW_SENSE_ERROR_CODES>
   //***************************************************************************
   // Internal xE/1D Errors.
   //***************************************************************************
   // 0x8E1D0080: RW_DATA_MISCOMPARE_01 - Disc Xfr - Data miscompare error.
   // 0x8E1D0081: RW_DATA_MISCOMPARE_02 - Disc Xfr - Data miscompare error at erasure correction.
   //
   //</RW_SENSE_ERROR_CODES>

   #define RW_DATA_MISCOMPARE_01                                     0x0E1D0080
   #define RW_DATA_MISCOMPARE_02                                     0x0E1D0081

   //<RW_SENSE_ERROR_CODES>
   //**************************************************************************
   // End of Error Codes
   //**************************************************************************
   //</RW_SENSE_ERROR_CODES>
   #define INVALID_RW_ERROR_CODE                                     0xFFFFFFFF

   // -----------------------------------------------------------------------------
   // Macro used for checking if a reallocated block error has been encountered.
      #define M_IsErrorDueToReallocatedBlock(ErrCode)    \
         ((ErrCode == RW_BLOCK_REALLOCATED_01) ||        \
          (ErrCode == RW_BLOCK_REALLOCATED_02) ||        \
       (ErrCode == RW_BLOCK_REALLOCATED_03))

   // -----------------------------------------------------------------------------
   // Macro used for checking if a reallocated block error has NOT been encountered.
      #define M_IsErrorNotDueToReallocatedBlock(ErrCode) \
         ((ErrCode != RW_BLOCK_REALLOCATED_01) &&        \
          (ErrCode != RW_BLOCK_REALLOCATED_02) &&        \
       (ErrCode != RW_BLOCK_REALLOCATED_03))

   // --------------------------------------------------------------------------
   // Macro used for checking if a read mis-compare error has been encountered.
   #define M_IsErrorDueToReadMisCompare(ErrCode)         \
         ((ErrCode == RW_DATA_MISCOMPARE_01) ||          \
          (ErrCode == RW_DATA_MISCOMPARE_02))

   // --------------------------------------------------------------------------
   // Macro used for checking if a sector sync timeout error has been encountered.
#if IDD_0109374_ALT_ON_SYNC_ERR_RECOVERY
   #define M_IsErrorDueToSectorSyncTimeout( ErrCode, RecoveryStatusFlags )         \
         ( ( ErrCode == RW_DATA_SYNC_TIMEOUT ) ||             \
           ( ErrCode == RW_DATA_SPLIT_SYNC_TIMEOUT ) ||       \
           ( RecoveryStatusFlags & RW_RECOVERY_SYNC_RECOVERY_APPLIED ) )
#else
   #define M_IsErrorDueToSectorSyncTimeout( ErrCode, ErrRecoveryInfo )      \
         ((ErrCode == RW_DATA_SYNC_TIMEOUT) ||           \
          (ErrCode == RW_DATA_SPLIT_SYNC_TIMEOUT))
#endif

   // --------------------------------------------------------------------------
   // Macro used for checking if write parity error caused by invalid SPRAM has been encountered.
   #define M_IsErrorDueToFormSPRAMInvalid(ErrCode)                           \
         ((ErrCode == RW_FORM_SP_RAM_INVALID_FOR_PARITY_SECS_UPDATE) ||      \
          (ErrCode == RW_FORM_SP_RAM_INVALID_FOR_PARITY_SECS_ALT_UPDATE))

#if RW_SKIP_WRITE_DETECT
   #define M_IsErrorDueToSkipWriteDetectFault( ErrCode )                                            \
   ( (( ErrCode & ~RW_ERROR_CODE_MASK) == ( RW_SWD_DVGAS_FAULT  & ~RW_ERROR_CODE_MASK )) ||         \
     (( ErrCode & ~RW_ERROR_CODE_MASK) == ( RW_SWD_RVGAS_FAULT  & ~RW_ERROR_CODE_MASK )) ||         \
     (( ErrCode & ~RW_ERROR_CODE_MASK) == ( RW_SWD_FVGAS_FAULT  & ~RW_ERROR_CODE_MASK )) ||         \
     (( ErrCode & ~RW_ERROR_CODE_MASK) == ( RW_SWD_DVGAS_SUM_FAULT  & ~RW_ERROR_CODE_MASK )) ||     \
     (( ErrCode & ~RW_ERROR_CODE_MASK) == ( RW_SWD_RVGAS_SUM_FAULT  & ~RW_ERROR_CODE_MASK )) ||     \
     (( ErrCode & ~RW_ERROR_CODE_MASK) == ( RW_SWD_FVGAS_SUM_FAULT  & ~RW_ERROR_CODE_MASK )) )

   #define M_IsRAWRequestDueToSWDFault( ErrCode ) ( (ErrCode == RW_SWD_DVGAS_FAULT_RAW_REQ ) ||     \
                                                    (ErrCode == RW_SWD_RVGAS_FAULT_RAW_REQ ) ||     \
                                                    (ErrCode == RW_SWD_FVGAS_FAULT_RAW_REQ ) ||     \
                                                    (ErrCode == RW_SWD_DVGAS_SUM_FAULT_RAW_REQ ) || \
                                                    (ErrCode == RW_SWD_RVGAS_SUM_FAULT_RAW_REQ ) || \
                                                    (ErrCode == RW_SWD_FVGAS_SUM_FAULT_RAW_REQ ) )
#else  // #if !RW_SKIP_WRITE_DETECT
   #define M_IsErrorDueToSkipWriteDetectFault( ErrCode ) ( FALSE )
   #define M_IsRAWRequestDueToSWDFault( ErrCode ) ( FALSE )
#endif  // #if RW_SKIP_WRITE_DETECT

#define M_IsErrorDueToServoOrSWDFault( ErrCode )                                \
( M_IsErrorDueToSkipWriteDetectFault( ErrCode ) ||                              \
  (( ErrCode & ~RW_ERROR_CODE_MASK) == ( RW_BROWNOUT_FAULT & ~RW_ERROR_CODE_MASK )) \
)

#if RW_CONTACT_FAULT_DETECTION
   #define M_IsErrorDueToEBMSFaultDetectFault( ErrCode )                                            \
   ( (( ErrCode & (~RW_ERROR_CODE_MASK)) == ( RW_EFD_WRITE_CONTACT_FAULT & (~RW_ERROR_CODE_MASK) )) || \
     (( ErrCode & (~RW_ERROR_CODE_MASK)) == ( RW_EFD_READ_CONTACT_FAULT  & (~RW_ERROR_CODE_MASK) )) || \
     (( ErrCode & (~RW_ERROR_CODE_MASK)) == ( RW_EFD_SWOT_FAULT  & (~RW_ERROR_CODE_MASK) ))  )

   #define M_IsRAWRequestDueToEFDFault( ErrCode ) ( (ErrCode == RW_EFD_WRITE_CONTACT_FAULT_RAW_REQ ) || \
                                                    (ErrCode == RW_EFD_SWOT_FAULT_RAW_REQ ) )

   #define M_IsErrorDueToEBMSFailure( ErrCode )   ( ErrCode == RW_EFD_OPEN_DETCR_FAULT )
#else  // #if RW_CONTACT_FAULT_DETECTION
   #define M_IsErrorDueToEBMSFaultDetectFault( ErrCode ) ( FALSE )
   #define M_IsRAWRequestDueToEFDFault( ErrCode )        ( FALSE )
   #define M_IsErrorDueToEBMSFailure( ErrCode )          ( FALSE )
#endif  // #if RW_CONTACT_FAULT_DETECTION #else

#if RW_READ_AFTER_WRITE
   // --------------------------------------------------------------------------
   // Macro used for checking if a Read After Write mode has been requested
   // by RW
   #if RW_CONTACT_FAULT_DETECTION
      #define M_IsErrorDueToRAWRequest(ErrCode) ( ( ErrCode == RW_READ_AFTER_WRITE_REQ )|| \
                                                  ( M_IsRAWRequestDueToSWDFault(ErrCode) )|| \
                                                  ( M_IsRAWRequestDueToEFDFault(ErrCode) ) )
   #else
      #define M_IsErrorDueToRAWRequest(ErrCode) ( ( ErrCode == RW_READ_AFTER_WRITE_REQ )|| \
                                                  ( M_IsRAWRequestDueToSWDFault(ErrCode)) )
   #endif

   // Macro used for checking RAW operation has been aborted
   #define M_IsRAWOperationStatusAborted(ErrCode) ( ( ErrCode == RW_REQUEST_ABORTED )|| \
                                                    ( ErrCode == RW_REQUEST_SOFT_ABORTED )|| \
                                                    ( ErrCode == RW_XFR_PARTITION_OVERFLOWED ) )
#else
   #define M_IsErrorDueToRAWRequest(ErrCode) ( FALSE )
   #define M_IsRawOperationStatusAborted(ErrCode) ( FALSE )
#endif // RW_READ_AFTER_WRITE

   // --------------------------------------------------------------------------
   // Macro used for checking if a RW hardware error has been encountered.
   #define M_IsHardwareRWError(ErrCode)                 \
         ( (( ErrCode & ~RW_SENSE_KEY_MASK) == ( RW_MM_NX_OVERRUN_ERR  & ~RW_SENSE_KEY_MASK ))? TRUE:FALSE)

   // --------------------------------------------------------------------------
   // Macro used for checking if an IOEDC/IOECC error has been encountered.
   #define M_IsErrorDueToIOEXCError(ErrCode)                                                                        \
   ( (( ErrCode & ~RW_ERROR_CODE_MASK) == ( RW_WRITE_HALT_CORRECTABLE_IOECC_ERR & ~RW_ERROR_CODE_MASK )) ||         \
     (( ErrCode & ~RW_ERROR_CODE_MASK) == ( RW_IOEDC_ERROR_WITHOUT_IOECC_ERROR_ON_WRITE & ~RW_ERROR_CODE_MASK )) || \
     (( ErrCode & ~RW_ERROR_CODE_MASK) == ( RW_IOEDC_IOECC_PARITY_ERR_ON_WRITE & ~RW_ERROR_CODE_MASK )) ||          \
     (( ErrCode & ~RW_ERROR_CODE_MASK) == ( RW_IOECC_PARITY_ERROR_ON_WRITE & ~RW_ERROR_CODE_MASK )) ||              \
     (( ErrCode & ~RW_ERROR_CODE_MASK) == ( RW_IOEDC_ERROR_ON_WRITE_FDE  & ~RW_ERROR_CODE_MASK )) )
#endif // RW_SCSI_SUPPORT

#if INLINE_PARITY_SECTORS
#define M_IsErrorDueToSuperParity( RecoveryStatusFlags )    \
           ( RecoveryStatusFlags & ( BIPS_BUFFER_XOR_RECOVERY_APPLIED ) )
#endif

// Macro used for checking if Error Code is either soft or hard aborted.
#define M_IsRwErrorCodeAborted(ErrCode)      ( ( ErrCode == RW_REQUEST_ABORTED ) ||    \
                                               ( ErrCode == RW_REQUEST_SOFT_ABORTED ) )

// -----------------------------------------------------------------------------
// Defined macros to determine if R/W error code is retryable/unretryable.
#define M_IsRWErrorRetryable(x)             M_BitIsSet( x, RW_RETRYABLE_ERR_TYPE )
#define M_IsRWErrorUnretryable(x)           M_BitIsClear( x, RW_RETRYABLE_ERR_TYPE )

// -----------------------------------------------------------------------------
// Defined macro to determine if R/W error code is related to a disc read scan error.
#if INLINE_PARITY_DISC_READ_SCAN
#if INLINE_PARITY_CROSSCHECK
#define M_IsRWErrorSuperParityReadDiscScanError(x)    (((x) == RW_SUPER_PARITY_LONGWORD_XCHK_ERROR) || \
                                                       ((x) == RW_SUPER_PARITY_LOW_WORD_XCHK_ERROR) || \
                                                       ((x) == RW_SUPER_PARITY_HIGH_WORD_XCHK_ERROR))
#else
#define M_IsRWErrorSuperParityReadDiscScanError(x)    ((x) == RW_SUPER_PARITY_DATA_MISCOMPARE)
#endif
#else
#define M_IsRWErrorSuperParityReadDiscScanError(x)    (FALSE)
#endif

// -----------------------------------------------------------------------------
// Defined macro to determine if R/W error code is related to invalid parity data.
#define M_IsRWErrorDueToInvalidParityData(x)          (((x) == RW_SUPER_BLK_MARKED_DIRTY) || \
                                                        M_IsRWErrorSuperParityReadDiscScanError(x))

// -----------------------------------------------------------------------------
// Defined macro to determine if R/W error code is related media read error.
#define M_IsRWErrorDueToMediaReadError(x)             (((x) == RW_EDAC_HW_UNCORR_ERR) || \
                                                       ((x) == RW_DATA_SYNC_TIMEOUT))

#define M_IsRWError(x)                                ( ! ( M_IsRwErrorCodeAborted( x ) || \
                                                          ( ( x ) == RW_NO_ERRORS ) ) )

#define M_IsRWHardwareErr(x)                                                  \
         ( ( ( (x) & ~RW_ERROR_CODE_MASK ) >= RW_HW_ERR_START_ERR_CODE ) &&   \
           ( ( (x) & ~RW_ERROR_CODE_MASK ) <= RW_HW_ERR_END_ERR_CODE ) )

#define M_IsRWFirmwareErr(x)                                                  \
         ( ( ( (x) & ~RW_ERROR_CODE_MASK ) >= RW_FW_ERR_START_ERR_CODE ) &&   \
           ( ( (x) & ~RW_ERROR_CODE_MASK ) <= RW_FW_ERR_END_ERR_CODE ) )

// -----------------------------------------------------------------------------
// Defined Request Status.

//<RW_STATUS_CODES>
//---------------------------------------------------------------------------------------------
// Read/Write Status Codes
//---------------------------------------------------------------------------------------------
// INSERT_TAGGED_DATA RW_SENSE_STATUS
//</RW_STATUS_CODES>

//<RW_SENSE_STATUS>
typedef enum
{
   // 0x0 RW_REQUEST_SATISFIED_WITH_RECOVERY - Request was satisfied with error recovery performed
   RW_REQUEST_SATISFIED_WITH_RECOVERY = 0,

   // 0x1 RW_REQUEST_SATISFIED - Request was satisfied (no error recovery performed)
   RW_REQUEST_SATISFIED = 1,

   // 0x2 RW_REQUEST_FAILED -Request was not satisfied
   RW_REQUEST_FAILED = 2

} rw_sense_status;
//</RW_SENSE_STATUS>

// -----------------------------------------------------------------------------
//<RW_SENSE>
// Returned sense information to be applied throughout the R/W system.
typedef struct rw_sense
{
   // Status is an enumeration indicating the success or failure of the R/W
   // operation attempted.
   // INSERT_LINK_TO_TAGGED_DATA RW_STATUS_CODES
   rw_sense_status         Status; //[e8]

   // ErrorCode indicates the failure type of the last R/W operation attempted.
   // INSERT_LINK_TO_TAGGED_DATA RW_SENSE_ERROR_CODES
   rw_error_code           ErrorCode;
} rw_sense;
//</RW_SENSE>
// -----------------------------------------------------------------------------
// R/W drive fault status type.
#if IP_HEADER_CONF_01
typedef tycc_rd_wt_fault_t  rw_drive_fault_status;
#else
typedef uint16  rw_drive_fault_status;
#endif
// -----------------------------------------------------------------------------
// R/W preamp fault status type.
typedef uint16  rw_preamp_fault_status;

// Defined Preamp fault bit flags.
// WARNING!! The following bit definitions (for TI 3945,LSI 8831 and
// newer preamps) might not be accurate for all preamps.For accurate
// information for each preamp, refer to the IO-Servo command
// protocol database.
#define LOW_SUPPLY_FAULT                     BIT0
#define LOW_WRITE_DATA_FREQ_COMMON_FAULT     BIT1
#define WRITE_HEAD_OPEN_FAULT                BIT2
#define WRITE_HEAD_SHORT_FAULT               BIT3
#define TA_SENSOR_OPEN_FAULT                 BIT4
#define THERMAL_FAULT                        BIT5
#define WRITE_MASTER_HEAT_OFF_FAULT          BIT6
#define WRITE_HTR_OPEN_SHORT_FAULT           BIT7
#define WRITER_OFF_BIT_FAULT                 BIT8
#define WR_OUTPUT_BUFFER_FAULT               BIT9
#define LOW_WRITE_FREQ_DATA_HEAD_FAULT       BIT10
#define FOS_FAULT                            BIT11
#define RD_HEATER_OPEN_SHORT_FAULT           BIT12
#define TA_OR_CONTACT_DETECT_FAULT           BIT13
#define SWOT_FAULT                           BIT14
#define SERIAL_PORT_COMM_FAULT               BIT15

// -----------------------------------------------------------------------------
// Defined Preamp fault bit flags.
#define CONTACT_DETECT_FAULT                 BIT6

// Defined Preamp fault status register
#define PREAMP_FAULT_STATUS_REGISTER            7

// R/W recovery status flags type.
typedef uint64   rw_recovery_status_flags;
//<RW_RECOVERY_STATUS_FLAGS>
// -----------------------------------------------------------------------------
// Read/Write Recovery Status Flags
// -----------------------------------------------------------------------------

// 0x00000001: BIT 0:  RW_RECOVERY_POS_TRK_OFF_APPLIED - Error was recovered w/positive track offset applied.
#define RW_RECOVERY_POS_TRK_OFF_APPLIED         BIT0

// 0x00000002: BIT 1:  RW_RECOVERY_NEG_TRK_OFF_APPLIED - Error was recovered w/negative track offset applied.
#define RW_RECOVERY_NEG_TRK_OFF_APPLIED         BIT1

// 0x00000004: BIT 2:  RW_RECOVERY_ECC_CORR_APPLIED - Error was recovered w/ECC correction applied.
#define RW_RECOVERY_ECC_CORR_APPLIED            BIT2

// 0x00000008: BIT 3:  RW_RECOVERY_SYNC_RECOVERY_APPLIED - Error was recovered w/sync mark recovery.
#define RW_RECOVERY_SYNC_RECOVERY_APPLIED       BIT3

// 0x00000010: BIT 4:  RW_RECOVERY_HIDDEN_RETRY_APPLIED - Error was recovered w/hidden retry applied.
#define RW_RECOVERY_HIDDEN_RETRY_APPLIED        BIT4

// 0x00000020: BIT 5:  RW_RECOVERY_GROWN_SERVO_FLAWS_EXIST - Grown servo flaws exist on current track..
#define RW_RECOVERY_GROWN_SERVO_FLAWS_EXIST     BIT5

// 0x00000040: BIT 6:  RW_RECOVERY_SERVO_FLAW_ASSOCIATED - Retried block is associated w/a servo flaw.
#define RW_RECOVERY_SERVO_FLAW_ASSOCIATED       BIT6

// 0x00000080: BIT 7:  RW_RECOVERY_NEW_SERVO_FLAWS_DETECTED - New servo flaws detected during recovery.
#define RW_RECOVERY_NEW_SERVO_FLAWS_DETECTED    BIT7

// 0x00000100: BIT 8:  RW_RECOVERY_TIME_EXCEEDED - Recovery time limit was exceeded.
#define RW_RECOVERY_TIME_EXCEEDED               BIT8

// 0x00000200: BIT 9:  RW_RECOVERY_LEVEL_EXCEEDED - Recovery level limit was exceeded.
#define RW_RECOVERY_LEVEL_EXCEEDED              BIT9

// 0x00000400: BIT 10: RW_RECOVERY_COUNT_EXCEEDED - Recovery count limit was exceeded.
#define RW_RECOVERY_COUNT_EXCEEDED              BIT10

// 0x00000800: BIT 11: RW_RECOVERED_SEEK_OCCURRED - Recovered seek error occurred.
#define RW_RECOVERED_SEEK_OCCURRED              BIT11

// 0x00001000: BIT 12: RW_RECOVERY_DID_ECC_NOT_FWEC - When FW Erasure correction was applied, normal ECC was actually used
//                                                this will be set along with RW_RECOVERY_ECC_CORR_APPLIED
#define RW_RECOVERY_DID_ECC_NOT_FWEC            BIT12

// 0x00002000: BIT 13: BIPS_BUFFER_XOR_RECOVERY_APPLIED - Error was recovered w/BIPS recovery applied.
#define BIPS_BUFFER_XOR_RECOVERY_APPLIED        BIT13

// 0x00004000: BIT 14: RW_READ_CONTINUOUS_EDAC_HU_ERR_OCCURRED - EDAC HU error occurred in read continuous transfer.
#define RW_READ_CONTINUOUS_EDAC_HU_ERR_OCCURRED BIT14

// 0x00008000: BIT 15: RW_APPROACHING_RECOVERY_TIME_LIMIT - When R/W has detected the recovery time limit is approaching,
//                                                      this bit will be set along with RW_RECOVERY_TIME_EXCEEDED
#define RW_APPROACHING_RECOVERY_TIME_LIMIT      BIT15

// 0x00010000: BIT 16: RW_RECOVERY_SERV_APPLIED - Error was recovered w/SERV recovery applied.
#define RW_RECOVERY_SERV_APPLIED                BIT16

// 0x00020000: BIT 17: RW_BERP_ERASURE_RECOVERY_APPLIED - Error was recovered w/BERP Erasure Correction recovery applied.
#define RW_BERP_ERASURE_RECOVERY_APPLIED        BIT17

// 0x00040000: BIT 18: RW_BERP_SLIDE_WIN_APPLIED - Error was recovered w/BERP Sliding Window recovery applied.
#define RW_BERP_SLIDE_WIN_APPLIED               BIT18

// 0x00080000: BIT 19: RW_BERP_EXT_ITERATIONS_RECOVERY_APPLIED - Error was recovered w/BERP Extended Iterations recovery applied.
#define RW_BERP_EXT_ITERATIONS_RECOVERY_APPLIED BIT19

// 0x00100000: BIT 20: RW_TA_RETRIES_RECOVERY_APPLIED - Error was recovered with TA Retries recovery applied.
#define RW_TA_RETRIES_RECOVERY_APPLIED          BIT20

// 0x00200000: BIT 21: RW_SUPER_BLK_DIRTY_MARKING_REQUIRED - Super block dirty marking is required.
#define RW_SUPER_BLK_DIRTY_MARKING_REQUIRED     BIT21

// 0x00400000: BIT 22: RW_SUPER_BLK_DIRTY_MARKING_ATTEMPTED - Super block dirty marking was attempted.
#define RW_SUPER_BLK_DIRTY_MARKING_ATTEMPTED    BIT22

// 0x00800000: BIT 23: RW_SUPER_BLK_DIRTY_MARKING_ATTEMPTED - Super block dirty marking was attempted.
#define RW_SUPER_BLK_PARITY_UPDATE_REQUIRED     BIT23

// 0x01000000: BIT 24: RW_SUPER_BLK_PARITY_ERROR_REC_PERFORMED - Super block parity sectors error recovery performed.
#define RW_SUPER_BLK_PARITY_ERROR_REC_PERFORMED BIT24

// 0x02000000: BIT 25: RW_RECOVERY_UDR_APPLIED - Error was recovered w/UDR recovery applied.
#define RW_RECOVERY_UDR_APPLIED                 BIT25

// 0x04000000: BIT 26: RW_HEAD_INSTABILITY_RECOVERY_APPLIED - Error was recovered w/Head instability recovery applied. Under Head Instability Retries for DERP 4.8.
#define RW_HEAD_INSTABILITY_RECOVERY_APPLIED    BIT26 // FE_0167032_411363_DERP_4_REV_8_INSTABILITY_RETRIES

// 0x04000000: BIT 26: RW_THERMAL_ANNEALING_RECOVERY_APPLIED - Error was recovered w/Thermal Annealing recovery applied. Under Head isntability retries under DERP5 and DERP4 not including 4.8 cahnges.
#define RW_THERMAL_ANNEALING_RECOVERY_APPLIED   BIT26 // FE_0226866_330051_INSTABILITY_THERMAL_ANNEALING_RETRY

// 0x08000000: BIT 27: RW_ATIC_RECOVERY_APPLIED - ATIC error recovery was applied.
#define RW_ATIC_RECOVERY_APPLIED                BIT27

// 0x10000000: BIT 28: RW_ISP_RECOVERY_APPLIED - Error was recovered w/Intermediate Super Parity recovery applied.
#define RW_ISP_RECOVERY_APPLIED                 BIT28

// 0x20000000: BIT 29: RW_BERP_LLR_SCALING_RECOVERY_APPLIED - Error was recovered w/BERP LLR Scaling recovery applied.
#define RW_BERP_LLR_SCALING_RECOVERY_APPLIED    BIT29

// 0x40000000: BIT 30: RW_SUPER_PARITY_RECOVERY_NO_RETRY - Error was recovered w/Inline parity recovery without any retries.
#define RW_SUPER_PARITY_RECOVERY_NO_RETRY       BIT30

// 0x80000000: BIT 31: RW_READ_VERIFY_ADJACENT_TRACK - adjacent track recovery applied.
#define RW_READ_VERIFY_ADJACENT_TRACK           BIT31

// 0x100000000: BIT 32: RW_READ_FULL_RECOVERY_RESUMED - Full recovery resumed after Super parity recovery.
#define RW_READ_FULL_RECOVERY_RESUMED           BIT32

#if RW_FWIOC_LITE
// 0x200000000: BIT 33: RW_IOC_LITE_ENTRY_VALID - IOC-Lite entry condition is valid.
#define RW_IOC_LITE_ENTRY_VALID                 BIT33
#endif

// 0x400000000: BIT 34: RW_FWIOC_BUFF_RECOVER_DATA_INVALID - Super parity recovery, FWIOC buffer data exist but invalid.
#define RW_FWIOC_BUFF_RECOVER_DATA_INVALID      BIT34
#if RW_MSMR_X_AVERAGE
// 0x200000000: BIT 34: RW_RECOVERY_X_AVERAGE_APPLIED - Error was recovered with X-Averaging recovery applied.
#define RW_RECOVERY_X_AVERAGE_APPLIED           BIT35
#else
#define RW_RECOVERY_X_AVERAGE_APPLIED           0
#endif

//</RW_RECOVERY_STATUS_FLAGS>
#if RW_MSMR_X_AVERAGE
#define RW_RECOVERY_ALGORITHMS_APPLIED   (RW_RECOVERY_POS_TRK_OFF_APPLIED |   \
                                          RW_RECOVERY_NEG_TRK_OFF_APPLIED |   \
                                          RW_RECOVERY_ECC_CORR_APPLIED |      \
                                          RW_RECOVERY_SYNC_RECOVERY_APPLIED | \
                                          RW_RECOVERY_HIDDEN_RETRY_APPLIED  | \
                                          RW_RECOVERY_SERV_APPLIED          | \
                                          RW_TA_RETRIES_RECOVERY_APPLIED            | \
                                          RW_BERP_ERASURE_RECOVERY_APPLIED          | \
                                          RW_BERP_SLIDE_WIN_APPLIED                 | \
                                          RW_BERP_EXT_ITERATIONS_RECOVERY_APPLIED   | \
                                          RW_RECOVERY_UDR_APPLIED                   | \
                                          RW_HEAD_INSTABILITY_RECOVERY_APPLIED      | \
                                          RW_ATIC_RECOVERY_APPLIED                  | \
                                          RW_BERP_LLR_SCALING_RECOVERY_APPLIED      | \
                                          RW_RECOVERY_X_AVERAGE_APPLIED )
#else
#define RW_RECOVERY_ALGORITHMS_APPLIED   (RW_RECOVERY_POS_TRK_OFF_APPLIED |   \
                                          RW_RECOVERY_NEG_TRK_OFF_APPLIED |   \
                                          RW_RECOVERY_ECC_CORR_APPLIED |      \
                                          RW_RECOVERY_SYNC_RECOVERY_APPLIED | \
                                          RW_RECOVERY_HIDDEN_RETRY_APPLIED  | \
                                          RW_RECOVERY_SERV_APPLIED          | \
                                          RW_TA_RETRIES_RECOVERY_APPLIED            | \
                                          RW_BERP_ERASURE_RECOVERY_APPLIED          | \
                                          RW_BERP_SLIDE_WIN_APPLIED                 | \
                                          RW_BERP_EXT_ITERATIONS_RECOVERY_APPLIED   | \
                                          RW_RECOVERY_UDR_APPLIED                   | \
                                          RW_HEAD_INSTABILITY_RECOVERY_APPLIED      | \
                                          RW_ATIC_RECOVERY_APPLIED                  | \
                                          RW_BERP_LLR_SCALING_RECOVERY_APPLIED)
#endif


// - Customer Unique
#if START_MOTOR_RECOVERED_ERROR_SUPPORTED
   #define RW_RECOVERY_STATUS_RESET_MASK    (~(RW_READ_CONTINUOUS_EDAC_HU_ERR_OCCURRED |  \
                                               RW_RECOVERED_SEEK_OCCURRED))
#else
   #define RW_RECOVERY_STATUS_RESET_MASK    (~RW_READ_CONTINUOUS_EDAC_HU_ERR_OCCURRED)
#endif

// -----------------------------------------------------------------------------
// R/W Servo Unsafe Fault Cause value type.
#if HWWA_0184623_403313_LSI2935_WEAK_WRITE_ISSUE
typedef uint32 rw_servo_unsafe_fault_cause;
#else  // #if HWWA_0184623_403313_LSI2935_WEAK_WRITE_ISSUE
typedef uint16 rw_servo_unsafe_fault_cause;
#endif // #if HWWA_0184623_403313_LSI2935_WEAK_WRITE_ISSUE #else

// -----------------------------------------------------------------------------
// R/W transfer error recovery information.
typedef struct rw_xfr_error_recovery_info
{
   block_addr                    LastRetryBlkAddr;          // Last block addr error recovery was performed on.
   track_position                FailedTrackPosition;       // Failed track position.
   rw_er_retry_step              RetryCount;                // Retry count performed.
   rw_recovery_status_flags      RecoveryStatusFlags;       // Recovery status flags.
   error_recovery_time           RecoveryTimeRemaining;     // Recovery time remaining after completion of request.
   rw_drive_fault_status         DriveFaultStatus;          // Drive fault status.
   rw_er_retry_level             RetryLevel;                // Retry level applied.
   rw_servo_unsafe_fault_cause   ServoUnsafeFaultCause;     // Servo Unsafe Fault cause value.

   rw_preamp_fault_status        PreampFaultStatus;         // Preamp fault status.
#if REPORT_SERVO_LOOP_CODE
   rw_servo_loop_code            ServoLoopCode;             // Retrieved servo loop code value.
#endif
#if TABLE_DRIVEN_DERP_READ_RETRIES
   rw_selected_retry_state       DerpRetryState;            // The last DERP retry state information in error recovery.
#endif
   chan_error                    ChannelFaultStatus;        // SRC fault status FE_0216031_357634_SHOW_SRC_FAULTS_IN_VERBOSE_ASCII_OUTPUT_MODE
   unsigned                      BERPApplied:1;             // TRUE - BERP was applied in last retry.
   unsigned                      InformationValid:1;        // TRUE - This information is valid and belongs to current error recovery retry.
   unsigned                      NoDiscXfrForcedHardened:1; // TRUE - Forced DISC_ONLY_XFR in Status to deal with a hardened error.
} rw_xfr_error_recovery_info;

// -----------------------------------------------------------------------------
// R/W transfer error recovery information.
typedef struct rw_super_sector_xfr_error_recovery_info
{
   // Drive fault status.
   rw_drive_fault_status         DriveFaultStatus;

   // Preamp fault status.
   rw_preamp_fault_status        PreampFaultStatus;

   // Starting data wedge accessed in transfer.
   servo_wedge                   XfrStartWedge;

   // Number of data wedges successfully transferred.
   servo_wedge                   NumSucessfulXfrWedges;

   // Number of data wedges successfully transferred in secondary transfer.
   servo_wedge                   NumSucessfulSecondaryXfrWedges;

   // Failed data wedge.
   servo_wedge                   FailedWedge;

   // Servo Unsafe Fault cause value.
   rw_servo_unsafe_fault_cause   ServoUnsafeFaultCause;

//#if ( FE_0216031_357634_SHOW_SRC_FAULTS_IN_VERBOSE_ASCII_OUTPUT_MODE )
   chan_error                    ChannelFaultStatus;     // SRC fault status
//#endif

} rw_super_sector_xfr_error_recovery_info;


#endif // #ifndef __INCLUDE_RW_SENSE_H

