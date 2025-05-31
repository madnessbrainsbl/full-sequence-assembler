#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Interface calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SATA_SetFeatures.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SATA_SetFeatures.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from ICmdFactory import ICmd

def disable_WriteCache(exc = 1):
   #Disable Write Cache
   ICmd.SetFeatures(0x82, exc = exc)
def enable_WriteCache(exc = 1):
   #Enable Write Cache
   ICmd.SetFeatures(0x02, exc = exc)

def disable_ReadLookAhead(exc = 1):
   #Disable Read Look ahead
   ICmd.SetFeatures(0x55, exc = exc)
def enable_ReadLookAhead(exc = 1):
   #Enable Read Look ahead
   ICmd.SetFeatures(0xAA, exc = exc)

def disable_APM(exc = 1):
   #Disable Advanced Power management
   ICmd.SetFeatures(0x85, exc = exc)
def enable_APM(exc = 1):
   #Enable Advanced Power management
   ICmd.SetFeatures(0x05, exc = exc)

def disable_POIS(exc = 1):
   #Disable POIS (Power On In Standbye)
   ICmd.SetFeatures(0x86, exc = exc)
def enable_POIS(exc = 1):
   #Disable POIS (Power On In Standbye)
   ICmd.SetFeatures(0x06, exc = exc)

def disableLPSRMWLogging(clearLogs = False, exc = 1):
   if clearLogs:
      clrBit = 2
   else:
      clrBit = 0
   ICmd.SetFeatures(0x56, 0 | clrBit, 3, exc = exc)

def enableLPSRMWLogging(clearLogs = False, exc = 1):
   if clearLogs:
      clrBit = 2
   else:
      clrBit = 0
   ICmd.SetFeatures(0x56, 1 | clrBit, 3, exc = exc)
