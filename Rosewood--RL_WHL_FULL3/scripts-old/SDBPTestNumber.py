#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2011, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Executing SDBP Commands using Test Number (T538/T368)
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2012 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SDBPTestNumber.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SDBPTestNumber.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

import DITS, DETS

class CSDBPTestNumber(object):
   def __init__(self, dut):
      self.dut = dut

   # Enable Online Mode
   def enableOnlineModeRequests(self):
      DETS.CDETS.enableOnlineModeRequests()

   # Disable Online Mode
   def disableOnlineModeRequests(self):
      DETS.CDETS.disableOnlineModeRequests()

   # Unlock Factory Commands
   def unlockFactoryCmds(self):
      DITS.CDITS.unlockFactoryCmds()

   # Lock Factory Commands
   def lockFactoryCmds(self):
      DITS.CDITS.lockFactoryCmds()

   def getFirmwarePackageInfo(self):
      """
         Get F3 Firmware Package Info
         @return firmwarePackageInfo: string of characters
         Example result: "YA418A.SDM1.CA0568.0001SDM1"
      """
      dets = DETS.CDETS(self.dut)
      return dets.getBasicDriveInformation().getFirmwarePackageInfo()

   def getServoFirmwareRev(self):
      """
         Get servo firmware revision
         @return servoFirmwareRev: little-endian string of hexadecimal characters
         Example result: "A453"
      """
      dets = DETS.CDETS(self.dut)
      return dets.getBasicDriveInformation().getServoFirmwareRev()

   def getUDRStatus(self):
      """
         Get UDR status
         @return udr2Info: integer
         Example result: 0x00
         0x00: UDR2_RECOVERY_UNSUPPORTED indicates that UDR2 Recovery is not 
               supported by the firmware.
         0x01: UDR2_RECOVERY_DISABLED indicates that UDR2 recovery has been 
               disabled because the number PowerOn Life hours has exceeded the 
               LTTCPowerOnHours or because a write long has occurred.
         0x02: UDR2_RECOVERY_ENABLED indicates that UDR2 recovery is allowed 
               if all other retries have been exhausted.
      """
      dets = DETS.CDETS(self.dut)
      return int(dets.getBasicDriveInformation().getUdr2Info(), 16)

   def getJumperSetting(self):
      """
         Get jumper setting
         @return jumperSetting: integer
         Example result: 0x00
      """
      dets = DETS.CDETS(self.dut)
      return int(dets.getHardwareJumperSetting().getJumperInstalled(), 16)

   def getNumberOfUserZones(self):
      """
         Get total number of user zones in one drive
         @return numberOfUserZones: integer
         Example result: 96
      """
      dets = DETS.CDETS(self.dut)
      return int(dets.getRWZoneInformation().getNumUserZones(), 16)

   def getNumberOfUserZonesPerHead(self):
      """
         Get number of user zones per head
         @return numberOfUserZones: integer
         Example result: 24
      """
      return self.getNumberOfUserZones()/self.getHeadNum()

   def getHeadNum(self):
      """
         Get drive number of heads
         @return headNum: integer
         Example result: 4
      """
      driveTables = DITS.CDITSDriveTables(self.dut)
      return int(driveTables.getCAPTable().getHeadNum(), 16)

   def getDriveSN(self):
      """
         Get drive serial number
         @return driveSN: string of characters
         Example result: "W0Z006E0"
      """
      driveInformation = DITS.CDITSDriveInformation(self.dut)
      return driveInformation.getDriveSN()

   def getPcbaSN(self):
      """
         Get PCBA serial number
         @return pcbaSN: string of characters
         Example result: "0000S2148UJM"
      """
      driveInformation = DITS.CDITSDriveInformation(self.dut)
      return driveInformation.getPcbaSN()

