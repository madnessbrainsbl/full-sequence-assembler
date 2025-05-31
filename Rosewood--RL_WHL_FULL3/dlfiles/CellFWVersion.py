##############################################################################
#
# CellFWVersion.py  - This file describes the versions of all files required for the gemini cell
#
# Author: Jeff Siegle
#
# $RCSfile: CellFWVersion.py,v $
# $Revision: 1.33 $
# $Id: CellFWVersion.py,v 1.33 2007/09/19 21:10:06 hermosaj Exp $
# $Date: 2007/09/19 21:10:06 $
# $Author: hermosaj $
# $Source: /usr/local/cvsroot/PSG_CellFirmware/CellFWVersion.py,v $
#
##############################################################################

cellFWRevs = \
{
  'Fin CPC Ver'      : '3.307',
  #'Fin CPC Ver B3'   : '2.040',  This is never used, only here for info.  CPC_APP_2040.nex is required at this time to reflash
  'Fin CPC BOOT VER' : '4',
  # 'Fin CPC FLASH'  : '001',
  # 'Fin CPC USB1'   : '2001',
  # 'Fin CPC USB2'   : '2001',

  'Fin Nios Ver'     : '4.026',
  # 'Fin FPGA Ver'   : '303',
  # RFE_FPGA_RBF     : '3_14',
  # RFE_NIOS_NEX     : '4.023',
  # RFE_PIPE_RBF     : '1',
  # RFE_USB1_CFG     : '1000',
  # RFE_USB2_CFG     : '1000',
}

cellFWNames = \
{
  'Fin CPC APP'   : 'CPC_APP.nex',
  'Fin CPC APP B3': 'CPC_APP_B3.nex',
  'Fin CPC BOOT'  : 'CPC_BOOT.nex',
  'Fin CPC FLASH' : 'CPC_FLASH.nex',
  'Fin CPC USB1'  : 'CPC_USB1.cfg',
  'Fin CPC USB2'  : 'CPC_USB2.cfg',
  'Fin RFE NIOS'  : 'RFE_NIOS.nex',
  'Fin FPGA Ver'  : 'RFE.rbf',
  'Fin RFE FPGA'  : 'RFE_FPGA.rbf',
  'Fin RFE USB1'  : 'RFE_USB1.cfg',
  'Fin RFE USB2'  : 'RFE_USB2.cfg',
  # NIOS_RIM.srec,
  # RFE_PIPE.rbf,
}

#-----------------------------------------------------------------------------------------#
#----------------------------------   End of File   --------------------------------------#
##############################################################################
# $Log: CellFWVersion.py,v $
# Revision 1.33  2007/09/19 21:10:06  hermosaj
# Change version from 2.114 to 2.116
#
# Revision 1.32  2007/07/24 20:37:05  hermosaj
# Changed version to 2.114 which is the last released version since 2.110
#
# Revision 1.31  2007/03/13 22:19:19  hermosaj
# Steve
# Fix NVCSetPowerMode() and NVCReturnFromPowerMode() to call correct routines in the interface driver.
# Fix all Non-volatile Cache commands to return the correct status.
# Give access to the random number generator to CTestFunc class.  This provides access to the numbered tests.
# Add total command to CQueueComposite class.  This lets the user know exactly how many queued commands were generated.
# Removed CPC batch file control to make stack space for other commands. CPC versions 2.108 and 2.109 were created but not distributed to mark points in this change.
# ReadTransferRate() and WriteTransferRate() now return task final file registers.
#
# Brandon
# Resolved a duplicate Define error in Table_cd.h for P509 and P510_ERROR_RATE by adding _CPC to the end of the names.
# Changed use of P509_ERROR_RATE to reflect the new name of P509_ERROR_RATE_CPC in testfunc.cpp
# Updated table_mask.h to reflect the new table names.
# Changed define value of Parameter ZONE in ParmTable to use an already existing parameter of that name and clear a duplicate definition error
# Added support for the Drive  Var "Buffer Data" to test508 in testfunc.cpp and made all Drive Var reporting Parameter controlled.
#
# Todd
# Added support for VBAR in Test598().
# SeaTrack attribute support now available for numbered tests.
# Fixed TIPS compiling warnings in TestFunc.
#
# Farzad
# ESLIP:
# While waiting for ACK also check for NAK, and exit with ESLP_GOT_NAK error if drive sends NAK.
# Implement error retries for ACK / SRQ timeout and NAK errors.  Default retries = 2.
# Add intrinsic functions for ESLIP:
# ESync() to resync the drive ESlip receiver.  Sends a bunch of END chars to the drive.
# EslipRetry() to set the error retry limits and return the total count.
# For EReceive command, use shorter hard coded timeouts (10secs) after receiving SRQ.
# Fix CaptureServoData command checksum failure.  Extend the servo data EOB match string from "4>" to "\r\n4>" to prevent false detection or potential mixup with checksum string.
# Add support for Science Park firmware type (9) in DownloadDriveFirmware command.  Merge in Science Park changes from Rasid.
#
# Revision 1.30  2007/01/08 21:07:31  dsv
# - CPC 2107
# Provide NVC LBA and Range Length as optional input parameters to NVCAddLBA and NVCRemoveLBA commands.  If LBA and range length are not provided as input parameters or rangeLength is set to zero, the command assumes that the write buffer is already setup with proper LBA range entries and does not modify the write buffer.  Otherwise, (if rangeLength > 0) the command will setup the write buffer with the NVC LBA Range entries.
# Modified NVCAddLBA, NVCRemoveLBA, NVCQuery, and NVCQueryMisses commands to run VU (vendor unique) mode.
# Modified NVCQuery to run in device to host data xfer mode.
# Set sector count for NVCQueryMisses command to 1.
# Add intrinsic function NVCErase (B6h/DFh).
#
# Revision 1.29  2006/12/08 21:52:33  dsv
# - Added CPC 2.106
# Steve
# Add intrinsic function PutBuffByte().  This allows the user to put single values in specific locations of the read and write buffers.
# Restore primary buffers at the end of DeleteImageBuffers().  Better cleanup.
# Moved the XMLParser modules to a library.  This reduces the size of the length of the command line arguments so CPC can continue to be built on computers using Windows 2000.
# Add intrinsic InterfaceSpeed().  This reports the negotiated SATA interface speed.
# Changed the intrinsic function NVCQuery() parameter, blockCount from a BYTE to a WORD.  This allows larger block counts.
# Fix the order of the input parameters for intrinsic function NVCQuery().  Bug fix.
# Add access functions for the SATA2 hardware SControl and SStatus registers.  This will be used for a new feature that allows control of the negotiated SATA2 speed.
# Changed the intrinsic function NVCQuery() to be a non-data command.  Bug fix.
# Add intrinsic functions NVCSetPowerMode(), NVCReturnFromPowerMode().  New nonvolatile cache commands.
# Changed NAK for NEXTBUFF command to return the name of the file that it was looking for.  Debug feature.
# Add external verify flag parameter to ManagedDriveCopy().  Preparation for new feature to enhanced performance of Silver Image Copy.
#
# Rasid
# Add intrinsic function CrescendoSeekTime().
#
# Farzad
# Add reliability intrinsic function IdleAPMTest.  This is a power mode test for both APM and non-APM type drives.  APM type is an input parameter.
# In reliability intrinsic function SonyMicroVaultFuncTest change timed loop to count loop.
# Create new ESlip class to contain all ESLIP specific methods and objects.  Move ESLIP specific code from CSerial to ESlip class.
# In ESend, do not "Grant" SRQ.
# Check for and service the final interrupt in PATA PIO write command.
# Last interrupt from PIO write commands was not being processed.  If the interrupt occurred before the expectInterruptFlag was turned off, then the IRQ message would remain unserviced in the mail box and the subsequent interrupt mode command would fail for invalid status (ATA_WAIT_FOR_DRDY).  Failure was observed after several minutes of SequentialWR test on PATA drives.
# In IdleAPMTest(), insert a Set Features command between Hard Reset and Write DMA to restore the UDMA speed.  Also, make the non-APM mode byte pattern another optional input parameter.  Change default pattern from F0F0 to B5B5.
#
# Don
# Added code to DataReport for reporting test 535 results
#
# Revision 1.28  2006/10/31 20:34:33  dsv
# - Added CPC_2103:
# Farzad
# Add reliability intrinsic function IdleAPMTest.  This is a power mode test for both APM and non-APM type drives.  APM type is an input parameter.
# In reliability intrinsic function SonyMicroVaultFuncTest change timed loop to count loop.
# Create new ESlip class to contain all ESLIP specific methods and objects.  Move ESLIP specific code from CSerial to ESlip class.
# In ESend, do not "Grant" SRQ.
#
# Steve
# Change Base64 class to count decoded characters.  This is used for decoding ESLIP commands.
# Add access in SATA2 driver for SStatus and SControl registers.  These will be used to monitor/control SATA connection speed.
#
# Revision 1.27  2006/10/18 21:46:28  dsv
#  - Added CPC 2.102
# Rashid
# Change serial driver to only fill the FIOF 8 bytes before flushing.  The delay is reduced from 1ms to 125ns.
#
# Steve
# Add option to PXMLParser class to get the decoded size of content.  This is used by ESLIP intrinsic functions.
# Add memory pool to be used for default read and write buffers.  This increases the amount of memory available in the store pool used for temperary storage as the program runs.  It also creates a mechanism that could be used for increasing the number of tray threads.  In doing this a problem was also fixed where two memory pools overlaped.  As a result the file system size was reduced to 59MB.
# Use virtual memory address when creating the AAU buffer.  This should increase reliability of AAU calls.
# Add BYTESWAP() macro.
# Rename changeError() to CPC2PlatformError().  This increases readability of the code.
#
# Revision 1.26  2006/09/28 20:03:29  dsv
# - Added CPC 2.101
#
# Revision 1.25  2006/09/15 16:28:37  dsv
# - Added CPC 2.100
# Steve
# Add intrinsic function SetIFDCmdSize().  This allows the user to force the use of 28-bit or 48-bit commands regardless of segment size.
# Add check to serial ISR to detect soft SRQ character from the drive when the store flag is disabled.
#
# Rasid
# Fix DownloadDriveFirmware() so step result is valid.
#
# Revision 1.24  2006/09/12 19:58:11  dsv
# - Added CPC 2.099
#
# Revision 1.23  2006/09/01 15:16:29  dsv
# - Version CPC 2.98
#
# Revision 1.22  2006/07/27 15:46:22  dsv
# - Added CPC 2.097
#
# Revision 1.21  2006/07/18 14:30:59  dsv
# Added CPC 2096 version
#
# Revision 1.20  2006/07/06 20:39:49  rtm
# CPC version 2.095
#
# Revision 1.19  2006/04/26 14:12:17  rtm
# CPC Version 2.094
#
# Revision 1.18  2006/04/19 14:52:47  rtm
# NIOS version 4.026
#
# Revision 1.17  2006/04/19 14:22:11  rtm
# CPC version 2.093
#
# Revision 1.16  2006/03/01 21:29:44  rtm
# CPC version 2.092
#
# Revision 1.15  2006/02/17 17:24:27  rtm
# # CPC Version 2.090
#
# Revision 1.14  2006/02/03 17:56:45  rtm
# CPC cersion 2.089
#
# Revision 1.13  2006/01/12 23:12:14  rtm
# CPC Version 2.088
#
# Revision 1.12  2006/01/03 23:45:32  rtm
# CPC Version 2.086
#
# Revision 1.11  2005/12/20 23:57:49  rtm
# Nios version 4.024 and CPC version 2.084
#
# Revision 1.10  2005/11/23 20:58:37  rtm
# Changed version to reflect the correct version of CPC for the Tag
#
# Revision 1.9  2005/11/21 22:29:43  rtm
# Added CPC_APP_B3.nex filename
#
# Revision 1.7  2005/10/27 17:29:00  rtm
# New NIOS release 4.023
#
# Revision 1.6  2005/10/26 21:51:38  gcl
# rolling CPC_App to 2.078
#
# Revision 1.5  2005/10/25 21:53:33  gcl
# Python can be picky sometimes ... moved dictionary entries to the 1st column, instead of the 2nd column
#
# Revision 1.4  2005/10/25 21:45:10  gcl
# Rewrite of file to put entries in Dictionary form
#
# Revision 1.3  2005/10/19 17:05:42  sieglej
# Initial entry with header/footer
#
#
