#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: FDE TCG SATA Support
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/22 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File:
# $Revision: #4 $
# $DateTime: 2016/12/22 00:58:07 $
# $Author: hengngi.yeo $
# $Header:
# Level: 2
#-----------------------------------------------------------------------------------------#

from Constants import *
import base64, random, os, time, stat, string
import ScrCmds
import MessageHandler as objMsg
from TestParamExtractor import TP
import serialScreen
from PowerControl import objPwrCtrl
from Rim import objRimType
from Process import CProcess
from Cell import theCell

from Drive import objDut as dut

from ICmdFactory import ICmd
from State import CState
import math, types, re
import random
import binascii, struct
import sys
from Utility import CUtility
from Exceptions import CRaiseException
from PackageResolution import PackageDispatcher
if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
   from TdciAccess import makeTDCICall


testHardware = 1
DEBUG          = 0
if DEBUG:   REPORTING_MODE = (0x0001,)
else:       REPORTING_MODE = (0x0000,)

IEEE1667_Lookup = {
  'ACTIVATED'    : 0x0005,
  'DEACTIVATED'  : 0x0006,
   }

LifeStates = {
      'SETUP':    '00',
      'DIAG':     '01',
      'USE':      '80',
      'MFG':      '81',
      'INVALID':  'FF',
   }
LifeStatesLookup = CUtility.invertDict(LifeStates)

LifeStates_Bin = LifeStates.copy()
for k,v in LifeStates_Bin.values():
   LifeStates_Bin[k] = int(v,16)
UID_Table = {
   'FWDownload'      : 0x0001000200010002,
   'Diag'            : 0x0001000200010001,
   'UDS'             : 0x0001000200010003,
}

MSID_TYPE_Lookup = {
   'Use Default MSID'          : 0x00,
   'Use MSID from FIS'         : 0x01,
   'Use Saved MSID (DISABLED)' : 0x02,
   'Retrieve MSID from Drive'  : 0x04,
   'SED_OR_ISE'                : 0x08,  # bit on == ISE, bit off == SED
   }

CUSTOMER_OPTION_Lookup = {
   'SELF_ENCRYPTING_DRIVE'      : 0x01,
   'SECURED_DRIVE'              : 0x02,
   'INSTANT_SECURE_ERASE_DRIVE' : 0x03,
   'FIPS_SELF_ENCRYPTING_DRIVE' : 0x04,
   }

SetUseState = {
  'test_num'        : 577,
  'prm_name'        : 'SetUseState',
  "TEST_MODE"       : (0x0006,),   # Verify Personalization and Set Drive State
  "REPORTING_MODE"  : (0x8000,),
  "MSID_TYPE"       : (0x0001,),   # FIS's PSID
  "DRIVE_STATE"     : (0x0080,),
  "FW_PLATFORM"     : (0x0010,),
  "CERT_KEYTYPE"    : (0x0000,),
}
if testSwitch.FE_0180710_426568_P_PSID_MSYMK_AUTH_REQUIRED_FOR_SED_ACCESS:
   SetUseState["FW_PLATFORM"] = (0x0040,)

SetMfgState = {
  'test_num'        : 577,
  'prm_name'        : 'SetMfgState',
  "TEST_MODE"       : (0x0006,),   # Verify Personalization and Set Drive State
  "REPORTING_MODE"  : (0x8000,),
  "MSID_TYPE"       : (0x0001,),   # FIS's PSID
  "DRIVE_STATE"     : (0x0081,),
  "FW_PLATFORM"     : (0x0010,),
  "CERT_KEYTYPE"    : (0x0000,),
}
SetDiagState = {
  'test_num'        : 577,
  'prm_name'        : 'SetDiagState',
  "TEST_MODE"       : (0x0006,),   # Verify Personalization and Set Drive State
  "REPORTING_MODE"  : (0x8000,),
  "MSID_TYPE"       : 0x0001,   # FIS's PSID
  "DRIVE_STATE"     : (0x0001,),
  "FW_PLATFORM"     : (0x0010,),
  "CERT_KEYTYPE"    : (0x0000,),
}
SetSetupState = {
  'test_num'        : 577,
  'prm_name'        : 'SetSetupState',
  "TEST_MODE"       : (0x0006,),   # Verify Personalization and Set Drive State
  "REPORTING_MODE"  : (0x8000,),
  "MSID_TYPE"       : 0x0001,   # FIS's PSID
  "DRIVE_STATE"     : (0x0000,),
  "FW_PLATFORM"     : (0x0010,),
  "CERT_KEYTYPE"    : (0x0000,),
}

SDnD_T577_SetMFGState_Updates = {
  'MSID_TYPE'       : MSID_TYPE_Lookup['Use Default MSID'],
  'CUSTOMER_OPTION' : CUSTOMER_OPTION_Lookup['SECURED_DRIVE']
}

SDnD_T577_SetUSEState_Updates = {
  'MSID_TYPE'       : MSID_TYPE_Lookup['Retrieve MSID from Drive'],
  'CUSTOMER_OPTION' : CUSTOMER_OPTION_Lookup['SECURED_DRIVE']
}

if testSwitch.FE_0180710_426568_P_PSID_MSYMK_AUTH_REQUIRED_FOR_SED_ACCESS:
   SetMfgState["FW_PLATFORM"] = (0x0040,)

if testSwitch.BF_0160951_231166_P_ALLOW_SED_REP_INFO_RESP_CALLBACK:
   BUFFER_EXPECTED_RESPONSES = ('_INPROGRESS',  '_REPORT_INFO')
else:
   BUFFER_EXPECTED_RESPONSES = ('_INPROGRESS',)

def Is_SEDprm_AutoDetect():
   auto_detect = False

   if objRimType.SerialOnlyRiser() or testSwitch.NoIO: #In serial cell OR NoIO mode, don't care about RimCodeVer
      return False
   rim_ver = ICmd.getRimCodeVer()
   if objRimType.CPCRiser():
      try:
         float(rim_ver)
      except ValueError:
         objMsg.printMsg("Beta version detected, not a float value")
         rim_ver = rim_ver[:-1]
         objMsg.printMsg("Beta RimCodeVer %s" %rim_ver)

      if float(rim_ver) >= 2.254:
         auto_detect = True

   elif objRimType.IOInitRiser():
      Patt = re.compile('REL.SATA.(?P<SIC_VER>[\d]+).')
      Mat = Patt.search(rim_ver)
      if Mat:
         SIC = Mat.groupdict()['SIC_VER']
         if int(SIC) >= 688021:
            auto_detect = True

   return auto_detect

SEDprm_AutoDetect = Is_SEDprm_AutoDetect()

prm_575_SetCPCSupport = {
   'test_num'        : 575,
   'prm_name'        : 'prm_575_SetCPCSupport',
   "TEST_MODE"       : (0x0023,),      ##TestMode         (Prm[0] & 0xff)  
   "CORE_SPEC"       : (0x0002),       ##OpalSSC          (Prm[0] & 0xff)     #CS2.0
   "SSC_VERSION"     : (0x0001),       ##OpalSSC          (Prm[0] & 0xff)     #OpalSSC      
   "REPORTING_MODE"  : REPORTING_MODE, ##ReportingMode    (Prm[0] & 0x8000)
   "WHICH_SP"        : (0x0000,),      ##WhichSP          (Prm[1] & 0xff)
   "PASSWORD_TYPE"   : (0x0000,),      ##PasswordType     (Prm[2] & 0xff)
   "DRIVE_STATE"     : (0x0000,),      ##DriveState       (Prm[8] & 0xff)
   "UIDMSWU"         : (0x0000,),      ##UidLswu           Prm[4]
   "UIDMSWL"         : (0x0000,),      ##UidLswu           Prm[5]
   "UIDLSWU"         : (0x0000,),      ##UidLswu           Prm[6]
   "UIDLSWL"         : (0x0000,),      ##UidLswl           Prm[7]
   "CERT_TSTMODE"    : (0x0000,),      ##CertTestMode     (Prm[2] & 0xff)
   "CERT_KEYTYPE"    : (0x0000,),      ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
}

if SEDprm_AutoDetect:
   del prm_575_SetCPCSupport["SSC_VERSION"]
   prm_575_SetCPCSupport.update({"OPAL_SSC_SUPPORT" : 1})

#prm_575_03
prm_575_StartAdminSession = {
'test_num'        : 575,
'prm_name'        : 'prm_575_StartAdminSession',
"TEST_MODE"       : (0x0002,),       ##TestMode         (Prm[0] & 0xff)    = Start Session
"REPORTING_MODE"  : REPORTING_MODE,  ##ReportingMode    (Prm[0] & 0x8000)
"WHICH_SP"        : (0x0000,),       ##WhichSP          (Prm[1] & 0xff)
"PASSWORD_TYPE"   : (0x0000,),       ##PasswordType     (Prm[2] & 0xff)
"DRIVE_STATE"     : (0x0000,),       ##DriveState       (Prm[8] & 0xff)
"UIDMSWU"         : (0x0000,),       ##UidLswu           Prm[4]
"UIDMSWL"         : (0x0205,),       ##UidLswu           Prm[5]
"UIDLSWU"         : (0x0000,),       ##UidLswu           Prm[6]
"UIDLSWL"         : (0x0001,),       ##UidLswl           Prm[7]
"CERT_TSTMODE"    : (0x0000,),       ##CertTestMode     (Prm[2] & 0xff)
"CERT_KEYTYPE"    : (0x0000,),       ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
}

prm_575_AuthDefaultPSID = {
   'test_num'        : 575,
   'prm_name'        : 'prm_575_AuthDefaultPSID',
   "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
   "REPORTING_MODE"  : REPORTING_MODE,##ReportingMode    (Prm[0] & 0x8000)
   "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
   "PASSWORD_TYPE"   : (0x000A,),     ##PasswordType      (Prm[2] & 0xff)   = Default PSID
   "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
   "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
   "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
   "UIDLSWU"         : (0x0001,),     ##UidLswu           Prm[6]
   "UIDLSWL"         : (0xFF01,),     ##UidLswl           Prm[7]
   "CERT_TSTMODE"    : (0x0002,),     ##CertTestMode     (Prm[2] & 0xff)   = WRITE_RSA_KEYPAIR
   "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
}

prm_575_AuthPSID = {
   'test_num'        : 575,
   'prm_name'        : 'prm_575_AuthPSID',
   "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
   "REPORTING_MODE"  : REPORTING_MODE,##ReportingMode    (Prm[0] & 0x8000)
   "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
   "PASSWORD_TYPE"   : (0x0009,),     ##PasswordType      (Prm[2] & 0xff)   = PSID
   "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
   "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
   "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
   "UIDLSWU"         : (0x0001,),     ##UidLswu           Prm[6]
   "UIDLSWL"         : (0xFF01,),     ##UidLswl           Prm[7]
   "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
   "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
}

# prm_575_07
prm_575_AuthMSID = {
   'test_num'        : 575,
   'prm_name'        : 'prm_575_AuthMSID',
   "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
   "REPORTING_MODE"  : REPORTING_MODE,##ReportingMode    (Prm[0] & 0x8000)
   "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
   "PASSWORD_TYPE"   : (0x0002,),     ##PasswordType      (Prm[2] & 0xff)   = MSID
   "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
   "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
   "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
   "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
   "UIDLSWL"         : (0x0006,),     ##UidLswl           Prm[7]
   "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
   "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
}

prm_575_AuthMakerSymK_AES256_DefPSID  = {
   'test_num'        : 575,
   'prm_name'        : 'prm_575_AuthDefaultMakerSymK',
   "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
   "REPORTING_MODE"  : REPORTING_MODE,##ReportingMode    (Prm[0] & 0x8000)
   "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
   "PASSWORD_TYPE"   : (0x000C,),     ##PasswordType     (Prm[2] & 0xff)
   "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
   "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
   "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
   "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
   "UIDLSWL"         : (0x0004,),     ##UidLswl           Prm[7]
   "CERT_TSTMODE"    : (0x0001,),     ##CertTestMode     (Prm[2] & 0xff)   = WRITE_CERTIFICATION
   "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
}

prm_575_SetState = {
   'test_num'        : 575,
   'prm_name'        : 'prm_575_SetState',
   "TEST_MODE"       : (0x0008,),     ##TestMode         (Prm[0] & 0xff)   = Set State
   "REPORTING_MODE"  : REPORTING_MODE,##ReportingMode    (Prm[0] & 0x8000)
   "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
   "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)   = Default MSID
   "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
   "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
   "UIDMSWL"         : (0x0205,),     ##UidLswu           Prm[5]
   "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
   "UIDLSWL"         : (0x0001,),     ##UidLswl           Prm[7]
   "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
   "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
}

prm_575_ActivateSP = {
   'test_num'        : 575,
   'prm_name'        : 'prm_575_ActivateSP',
   "TEST_MODE"       : (0x0025,),   # ACTIVATE SP
   "REPORTING_MODE"  : REPORTING_MODE,
   "WHICH_SP"        : (0x0000,),   # Admin SP
   "PASSWORD_TYPE"   : (0x0002,),   #PasswordType      (Prm[2] & 0xff)
   "DRIVE_STATE"     : (0x0000,),   ##DriveState       (Prm[8] & 0xff)
   "UIDMSWU"         : (0x0000),    # UID of SP to be activated. Here is Locking SP.
   "UIDMSWL"         : (0x0205),
   "UIDLSWU"         : (0x0000),
   "UIDLSWL"         : (0x0002),
   "CERT_TSTMODE"    : (0x0000,),   ##CertTestMode     (Prm[2] & 0xff)
   "CERT_KEYTYPE"    : (0x0000,),   ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
}

# 575_15
prm_575_RevertSP = {
   'test_num'        : 575,
   'prm_name'        : 'prm_575_RevertSP',
   "TEST_MODE"       : (0x001E,),     ##TestMode         (Prm[0] & 0xff)      = Revert SP
   "REPORTING_MODE"  : REPORTING_MODE,##ReportingMode    (Prm[0] & 0x8000)
   "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
   "PASSWORD_TYPE"   : (0x0009,),     #PasswordType      (Prm[2] & 0xff)
   "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
   "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
   "UIDMSWL"         : (0x0006,),     ##UidLswu           Prm[5]
   "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
   "UIDLSWL"         : (0x0011,),     ##UidLswl           Prm[7]
   "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
   "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
}


prm_575_GetPortStatusTable = {
   'test_num'        : 575,
   'prm_name'        : 'prm_575_GetPortStatusTable',
   "TEST_MODE"       : (0x0005,),     ##TestMode         (Prm[0] & 0xff)  = Get Table
   "REPORTING_MODE"  : REPORTING_MODE,##ReportingMode    (Prm[0] & 0x8000)
   "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
   "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)
   "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
   "UIDMSWU"         : (0x0001,),     ##UidMSWU           Prm[4]
   "UIDMSWL"         : (0x0002,),     ##UidMSWL           Prm[5]
   "UIDLSWU"         : (0x0001,),     ##UidLSWU           Prm[6]
   "UIDLSWL"         : (0x0002,),     ##UidLSWl           Prm[7]
   "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
   "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
   "DblTablesToParse" : ('P57X_FRAME_DATA',),
}
if objRimType.CPCRiser():
   # With reporting mode set to 0, CPC will not return P57X_FRAME_DATA that
   # we need
   prm_575_GetPortStatusTable['REPORTING_MODE'] = (0x0001,)

writeSmartLogPage_538 = {
     'test_num': 538,
     'prm_name': "writeSmartLogPage_538",
     'PARAMETER_0': 0x2000,
     'FEATURES': 0x00,
     'COMMAND': 0x3F,
     'LBA_HIGH': 0x0000,
     'LBA_MID': 0x2459,
     'LBA_LOW': 0x00BE,
     'DEVICE' : 0x40,
     'SECTOR_COUNT': 1,
     'timeout': 2600,
}

import SED_Serial

if not objRimType.isIoRiser():
   #need to hyjack the sed serial api
   
   import base_BaudFunctions
   def statWrapper(*args, **kwargs):
      if 'msg' in kwargs:
         objMsg.printMsg(kwargs['msg'])
      else:
         objMsg.printMsg(args[0])
   SED_Serial.statMsg = statWrapper
   SED_Serial.SetESlipBaud = base_BaudFunctions.changeBaud

# ===================================================================
# getSID(...):
# Gets/generates a Secure ID (i.e. 'SID' or 'MSID') that is printed
# on the drive label and stored internally on the drive in the EF_SID
# file.  It will also create the appropriate drive attribute in FIS.
# ===================================================================
def getSID(updateAttrs=1):

   objMsg.printMsg("getSID")

   sidStatus = "1"   # 0 = get exisiting SID from FIS
                     # 1 = calculate new SID

   #sidLength = 25  # =25, per TCG Storage Architecture Core Spec
   sidLength = 32  # =32, per change to TCG Storage Architecture Core Spec for IBM only so far

   # Possible SID characters:
   # random ordering of 24 uppercase letters (No 'I' and No 'O') and
   # numerals 0 through 9
   # per TCG Storage Architecture Core SpecHDASerialNumber
   charChoices = ['H','U','7','C','J','9','T','5','R','B',\
                  'G','M','E','0','F','Z','4','8','Y','K',\
                  '2','L','V','D','S','1','A','W','3','Q',\
                  'X','6','P','N']

   # Create an empty SID string to be filled with random characters
   sidStr = ''

   if DriveAttributes.has_key('TD_SID') and not DriveAttributes['TD_SID'] == 'NONE' :
      sidStr = DriveAttributes['TD_SID']
      objMsg.printMsg("FIS TD_SID")
      sidStatus = "0"
   else:
      objMsg.printMsg("no TD_SID found @ FIS - calculating virgin TD_SID")

      # Shuffle the list prior to seeding the random number generator -
      # this ensures a unique SID even if the 'RandomSeed' value is the
      # same as a previous one.  Prevents duplicate SID's !!!
      random.shuffle(charChoices)
      # Seed the python random-number generator from an OS-specific
      # randomness source
      random.seed()

      # Generate a string of random characters
      for i in range(0, sidLength):
         # Generate a random number between 0 and 34, and use it to
         # select a character from the choices list
         # NOTE: random() generates a number between 0 and 1
         sidStr += charChoices[int(random.random() * 34)]

      # Put the SID into attributes (and automatically send to the Host)
      if updateAttrs:
         dut.driveattr['TD_SID'] = sidStr
         DriveAttributes['TD_SID'] = sidStr
         objMsg.printMsg("Virgin TD_SID")

   return sidStatus,sidStr

# ===================================================================
# generateSID(...):
# Generates a Secure ID (i.e. 'SID' or 'MSID' or 'PSID)
# ===================================================================
def generateSID():

  objMsg.printMsg("generateSID")

  sidStatus = "1" # 0 = get exisiting SID from FIS
                  # 1 = calculate new SID

  #sidLength = 25  # =25, per TCG Storage Architecture Core Spec
  sidLength = 32  # =32, per change to TCG Storage Architecture Core Spec for IBM only so far

  # Possible SID characters:
  # random ordering of 24 uppercase letters (No 'I' and No 'O') and
  # numerals 0 through 9
  # per TCG Storage Architecture Core SpecHDASerialNumber
  charChoices = ['H','U','7','C','J','9','T','5','R','B',\
                 'G','M','E','0','F','Z','4','8','Y','K',\
                 '2','L','V','D','S','1','A','W','3','Q',\
                 'X','6','P','N']

  # Create an empty SID string to be filled with random characters
  sidStr = ''

  # Shuffle the list prior to seeding the random number generator -
  # this ensures a unique SID even if the 'RandomSeed' value is the
  # same as a previous one.  Prevents duplicate SID's !!!
  random.shuffle(charChoices)
  # Seed the python random-number generator from an OS-specific
  # randomness source
  random.seed()

  # Generate a string of random characters
  for i in range(0, sidLength):
    # Generate a random number between 0 and 34, and use it to
    # select a character from the choices list
    # NOTE: random() generates a number between 0 and 1
    sidStr += charChoices[int(random.random() * 34)]

  objMsg.printMsg("MSID = %s" % sidStr)

  if testSwitch.FE_0199808_231166_P_SEND_MSID_TO_FIS:
     dut.driveattr['MSID'] = sidStr
     DriveAttributes['MSID'] = sidStr

  return sidStatus,sidStr

# ===================================================================
# CustomRequestSecureIDHandler():
# custom handler for results key of 32 - Request Secure ID (SID)
# ===================================================================
def CustomRequestSecureIDHandler():
  objMsg.printMsg("CustomRequestSecureIDHandler - Key 32")

  # Determine the PSID
  sidStatus,sid = getSID()
  objMsg.printMsg("PSID")

  if testHardware == 1:
    # Set up frame of data to send to initiator
    frame = sidStatus + sid + HDASerialNumber
    # frame = "\x22\x25\x00\x00" + sidStatus + sid + HDASerialNumber

    objMsg.printMsg("sending frame of data w/ PSID to the initiator")
    SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')

# ===================================================================
# CustomRequestSecureIDHandlerCPC():
# custom handler for results key of 43 - Request Secure ID (SID)
# ===================================================================
def CustomRequestSecureIDHandlerCPC():
   objMsg.printMsg("CustomRequestSecureIDHandlerCPC - Key 43")
   # Determine the PSID
   sidStatus,sid = getSID()
   objMsg.printMsg("PSID")

   if testHardware == 1:
      # Set up frame of data to send to initiator
      frame = struct.pack(">H",len(sidStatus + sid + HDASerialNumber)) + sidStatus + sid + HDASerialNumber
      # frame = "\x22\x25\x00\x00" + sidStatus + sid + HDASerialNumber

      objMsg.printMsg("sending frame of data w/ PSID to the CPC")
      SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')


# ===================================================================
# CustomRequestSecureHandlerGenerator():
# custom handler for results key of 44- Request Secure ID (SID)
# ===================================================================
def CustomRequestSecureHandlerGenerator():
   objMsg.printMsg("CustomRequestSecureHandlerGenerator - Key 44")
   #Determine the PSID
   sidStatus,sid = generateSID() #Always save to FIS
   objMsg.printMsg("MSID        = %s" % sid)

   if sid == DriveAttributes['TD_SID']:
      ScrCmds.raiseException(14862, "Error, MSID == PSID which is not allow")
   else:
      objMsg.printMsg("MSID not equal PSID")

   if testHardware == 1:
      # Set up frame of data to send to initiator
      frame = sidStatus + sid + HDASerialNumber
      # frame = "\x22\x25\x00\x00" + sidStatus + sid + HDASerialNumber

      objMsg.printMsg("sending frame of data w/ MSID to the initiator = %s" %frame)
      SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')

# ===================================================================
# CustomRequestSecureIDHandlerGeneratorCPC():
# custom handler for results key of 45 - Request Secure ID (SID)
# ===================================================================
def CustomRequestSecureHandlerGeneratorCPC():
   objMsg.printMsg("CustomRequestSecureHandlerGeneratorCPC - Key 45")
   # Determine the PSID
   sidStatus,sid = generateSID() #sidType 1 = MSID(default) 2 = PSID #Always Save PSID to FIS
   objMsg.printMsg("MSID        = %s" % sid)

   if sid == DriveAttributes['TD_SID']:
      ScrCmds.raiseException(14862, "Error, MSID == PSID which is not allow")
   else:
      objMsg.printMsg("MSID not equal PSID")

   if testHardware == 1:
      # Set up frame of data to send to initiator
      frame = struct.pack(">H",len(sidStatus + sid + HDASerialNumber)) + sidStatus + sid + HDASerialNumber
      # frame = "\x22\x25\x00\x00" + sidStatus + sid + HDASerialNumber

      objMsg.printMsg("sending frame of data w/ MSID to the CPC = %s" %frame)
      SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')

if testSwitch.FE_0154366_231166_P_FDE_OPAL_SUPPORT:
   # ===================================================================
   # CustomRequestKeyHandler():
   # customer handler for results key of 46,47 and 48 - Request uniqueKey
   # ===================================================================
   # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   # M2TD Cryptographic Infrastructure - KCI Interface Spec: Section 2.4
   # kjb @ 09/26/07
   # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def CustomRequestKeyHandler(transfer_type):
   ##  print "*** Request SerialPort Enable Key"
     stat = 1 # default = FAIL
   ##  print "Entering Custom Request Mfg Key Auth handler - 34 - unique key"
   ##
   ##  print "RequestService('ReqSPEKey',(", HDASerialNumber, "))"

     if transfer_type == 46:
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         method, prms = makeTDCICall('getUniqueKey', HDASerialNumber, 'DiagKey', 'AES256', '0')
       else:
         method,prms = RequestService('GetUniqueKey',(HDASerialNumber,'DiagKey','AES256','0'))
     if transfer_type == 47:
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         method, prms = makeTDCICall('getUniqueKey',  HDASerialNumber, 'DiagKey', 'AES256', '0')
       else:
         method,prms = RequestService('GetUniqueKey',(HDASerialNumber,'DiagKey','AES256','0'))
     if transfer_type == 48:
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         method, prms = makeTDCICall('getUniqueKey',  HDASerialNumber, 'DiagKey', '3DES', '0') # 'MfgKey'
       else:
         method,prms = RequestService('GetUniqueKey',(HDASerialNumber,'DiagKey','3DES','0')) # 'MfgKey'
     if transfer_type == 59:
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         method, prms = makeTDCICall('getUniqueKey',  HDASerialNumber, 'ActKey', 'AES256', '0')
       else:
         method,prms = RequestService('GetUniqueKey',(HDASerialNumber,'ActKey','AES256','0'))

     if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
       if prms.has_key('uniqueKey'):
         objMsg.printMsg("uniqueKey found in key dictionary")
         responseString = prms['uniqueKey']
         objMsg.printMsg("hex response string:  %s"% binascii.hexlify(base64.decodestring(responseString)))
         objMsg.printMsg("response from server  %s"% responseString)
         objMsg.printMsg("base64 decoded        %s"% base64.b64decode(responseString))
         uniqueKeyString = binascii.b2a_hex(base64.b64decode(responseString))
   ##      spEnableKeyString = binascii.b2a_hex(base64.b64decode(responseString))
   ##      if len(spEnableKeyString) != 32: # 32 chars = 16 bin-nibble-bytes
         objMsg.printMsg("Unique Key length =  %s"% len(uniqueKeyString))
   ##      else:
         objMsg.printMsg("sPort Enable Key = %s" % uniqueKeyString)
         iuniqueKey = binascii.a2b_hex(uniqueKeyString)
         objMsg.printMsg("sPort Enable Key = %s"% iuniqueKey)
         stat = 0

       else:
         objMsg.printMsg("entire return data from XML-RPC Server (dictionary) %s" % (prms))
         objMsg.printMsg('[34] ' + method + '"uniqueKey" not found in data from server')

     else:
       objMsg.printMsg('[34]' + method + "data from server is garbled")
     if testHardware:
       if not stat:
         frame = "\x22\x10\x00\x00" + iuniqueKey
       else:
         # If we could not get a key, the data length is 0 & no key is sent
         frame = "\x22\x00\x00\x00"

       objMsg.printMsg("sending frame of data w/ uniqueKey to the initiator")
       SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')
       objMsg.printMsg("Leaving Custom Request Mfg Key Auth handler - 46,47,48 - unique key")
       objMsg.printMsg(" ")

   # ===================================================================
   # CustomRequestDefaultManufacturingKeyAuthenticationHandler(...):
   # INPUTS:
   # * rcvData         : Random Challenge Value Data (from drive via initiator)
   # * HDASerialNumber : HDASerialNumber
   # RETURN(S):
   # * mfgAuthKey      : Manufacturing Autentication Key
   # custom handler for results key of 33 - Request Mfg. Key. Auth.
   # M2TD Cryptographic Infrastructure - KCI Interface Spec: Section 2.3
   # ===================================================================
   def CustomRequestDefaultManufacturingKeyAuthenticationHandler(rcvData, transfer_type): # RandomChallengeValueData
     stat = 1 # default = FAIL

     index = 0

     randomChallengeValue =  rcvData[index:]

     if transfer_type == 33:
       objMsg.printMsg("transfer type = 33")
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         ScrCmds.raiseException(11044, "Invalid key transfer type 33")
       method,prms = RequestService('ReqMfgAuth',(randomChallengeValue))
     elif transfer_type == 49:
       objMsg.printMsg("transfer type = 49")
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         method, prms = makeTDCICall( 'doDefaultKeyAuthentication', ('nonce',randomChallengeValue), HDASerialNumber, 'DiagKey', '3DES', '0')#'MfgKey'
       else:
         method,prms = RequestService('DoDefaultKeyAuthentication',(randomChallengeValue, HDASerialNumber,'DiagKey','3DES','0'))#'MfgKey'
     elif transfer_type == 50:
       objMsg.printMsg("transfer type = 50")
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         method, prms = makeTDCICall('doDefaultKeyAuthentication', ('nonce',randomChallengeValue), HDASerialNumber, 'DiagKey', 'AES256', '0')
       else:
         method,prms = RequestService('DoDefaultKeyAuthentication',(randomChallengeValue, HDASerialNumber,'DiagKey','AES256','0'))
     elif transfer_type == 51:
       objMsg.printMsg("transfer type = 51")
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         method, prms = makeTDCICall('doDefaultKeyAuthentication', ('nonce',randomChallengeValue), HDASerialNumber, 'DiagKey', 'AES256', '0')
       else:
         method,prms = RequestService('DoDefaultKeyAuthentication',(randomChallengeValue, HDASerialNumber,'DiagKey','AES256','0'))
     elif transfer_type == 60:
       objMsg.printMsg("transfer type = 60")
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         method, prms = makeTDCICall('doDefaultKeyAuthentication', ('nonce',randomChallengeValue), HDASerialNumber, 'ActKey','AES256','0')
       else:
         method,prms = RequestService('DoDefaultKeyAuthentication',(randomChallengeValue, HDASerialNumber,'ActKey','AES256','0'))

     if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
       if prms.has_key('AuthenticationResponse'):
         responseString = base64.b64decode(prms['AuthenticationResponse'])
         # tMsg("response from server    = %s" % responseString)
         mfgAuthKeyString = binascii.b2a_hex(responseString)
         objMsg.printMsg("HDA Serial Number = %s" % HDASerialNumber)
         objMsg.printMsg("Mfg.Auth.Key = %s" % mfgAuthKeyString)
         if len(mfgAuthKeyString) != 64: # 64 chars = 32 bin-nibble-bytes
           objMsg.printMsg("Mfg. Auth. Key = %i bytes, not 32 bytes" % len(mfgAuthKeyString))
         else:
           mfgAuthKey = binascii.a2b_hex(mfgAuthKeyString)
           stat = 0 # PASS
       else:
         objMsg.printMsg('[33]' + __name__ + '"AuthenticationResponse" not found in data from server')
     else:
       objMsg.printMsg('[33]' + __name__ + "data from server is garbled")

     if testHardware == 1:
       if not stat:
         frame = "\x21\x20\x00\x00"  + mfgAuthKey
       else:
         # If we could not get a key, the data length is 0 & no key is sent
         frame = "\x21\x00\x00\x00"

       objMsg.printMsg("sending frame of data w/ mfgAuthKey to the initiator")
       SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')
   ##    print"Leaving Custom Request Mfg Key Auth handler - 33 - default key"



   # ===================================================================
   # CustomRequestUniqueManufacturingKeyAuthenticationHandler(...):
   # customer handler for results key of 35 - SP Enable Key Authentication
   # ===================================================================
   # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   # M2TD Cryptographic Infrastructure - KCI Interface Spec: Section 2.5
   # kjb @ 10/04/07
   # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   def CustomRequestUniqueManufacturingKeyAuthenticationHandler(rcvData,transfer_type):
     #print "*** Request SerialPort Enable Key Authentication"
     stat = 1 # default = FAIL

     objMsg.printMsg("Entering handler for unique key authentication - get key")
     objMsg.printMsg("DATA IN-> from serial port enable key ")
     objMsg.printMsg(rcvData)


     ### # Jump over the 25 bytes of (binary) header information
     ### index = 25
     index = 0

     # Grab the Random Challenge Value (RCV) sent to us
     randomChallengeValue =  rcvData[index:]
     objMsg.printMsg("randomChallengeValue = %s" %randomChallengeValue )
     if transfer_type == 35:
       objMsg.printMsg("transfer type = 35")
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         ScrCmds.raiseException(11044, "Invalid key transfer type 35")
       method,prms = RequestService('ReqSPEAuth',(randomChallengeValue, HDASerialNumber))
     elif transfer_type == 52:
       objMsg.printMsg("transfer type = 52")
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         method, prms = makeTDCICall('doUniqueKeyAuthentication', ('nonce',randomChallengeValue), HDASerialNumber, 'DiagKey','3DES','0')
       else:
         method,prms = RequestService('DoUniqueKeyAuthentication',(randomChallengeValue, HDASerialNumber,'DiagKey','3DES','0')) #'MfgKey'
     elif transfer_type == 53:
       objMsg.printMsg("transfer type = 53")
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         method, prms = makeTDCICall('doUniqueKeyAuthentication', ('nonce',randomChallengeValue), HDASerialNumber, 'DiagKey','AES256','0')
       else:
         method,prms = RequestService('DoUniqueKeyAuthentication',(randomChallengeValue, HDASerialNumber,'DiagKey','AES256','0'))
     elif transfer_type == 54:
       objMsg.printMsg("transfer type = 54")
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         method, prms = makeTDCICall('doUniqueKeyAuthentication', ('nonce',randomChallengeValue), HDASerialNumber, 'DiagKey','AES256','0')
       else:
         method,prms = RequestService('DoUniqueKeyAuthentication',(randomChallengeValue, HDASerialNumber,'DiagKey','AES256','0'))
     elif transfer_type == 61:
       objMsg.printMsg("transfer type = 61")
       if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
         method, prms = makeTDCICall('doUniqueKeyAuthentication', ('nonce',randomChallengeValue), HDASerialNumber, 'ActKey','AES256','0')
       else:
         method,prms = RequestService('DoUniqueKeyAuthentication',(randomChallengeValue, HDASerialNumber,'ActKey','AES256','0'))

     if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
       if prms.has_key('AuthenticationResponse'):
         responseString = prms['AuthenticationResponse']
         spEnableAuthKeyString = binascii.b2a_hex(base64.b64decode(responseString))
         if len(spEnableAuthKeyString) != 64: # 64 chars = 32 bin-nibble-bytes
           objMsg.printMsg("SP Enable Auth. Key = %i bytes, not 32 bytes" % len(spEnableAuthKeyString))
         else:
           objMsg.printMsg("sPort Enable Auth. Key = %s" % spEnableAuthKeyString)
           spEnableAuthKey = binascii.a2b_hex(spEnableAuthKeyString)
           stat = 0 # PASS
       else:
         objMsg.printMsg('[35]' + method + '"serialPortEnableAuthKey" not found in data from server')
     else:
       objMsg.printMsg('[35]' + prms + "data from server is garbled")

     if testHardware == 1:
       if not stat:
         frame = "\x22\x10\x00\x00" + spEnableAuthKey
       else:
         # If we could not get a key, the data length is 0 & no key is sent
         frame = "\x22\x00\x00\x00"

       objMsg.printMsg("sending frame of data w/ spEnableAuthKey to the initiator")
       SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')
       objMsg.printMsg("Leaving handler for unique key authentication")




# ===================================================================
# CustomRequestManufacturingKeyAuthenticationHandler(...):
# INPUTS:
# * rcvData         : Random Challenge Value Data (from drive via initiator)
# * HDASerialNumber : HDASerialNumber
# RETURN(S):
# * mfgAuthKey      : Manufacturing Autentication Key
# custom handler for results key of 33 - Request Mfg. Key. Auth.
# M2TD Cryptographic Infrastructure - KCI Interface Spec: Section 2.3
# ===================================================================
def CustomRequestManufacturingKeyAuthenticationHandler(rcvData): # RandomChallengeValueData

  objMsg.printMsg("CustomRequestManufacturingKeyAuthenticationHandler - Key 33")

  stat = 1 # default = FAIL

  ### # Jump over the 25 bytes of (binary) header information
  ### index = 25
  index = 0

  # Grab the Random Challenge Value (RCV) sent to us
  objMsg.printMsg( "Entering Custom Request Mfg Key Auth handler - 33 - default key")
  randomChallengeValue =  rcvData[index:]

  objMsg.printMsg( "---A> RequestService('ReqMfgAuth = %s" % randomChallengeValue )
  if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
    ScrCmds.raiseException(11044, "Invalid key transfer ReqMfgAuth")
  method,prms = RequestService('ReqMfgAuth',(randomChallengeValue))  # Provide SN for Drive Unique Manufacturing Key
  objMsg.printMsg("method %s" % method)
  objMsg.printMsg("prms   %s" % prms)

  if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
    if prms.has_key('AuthenticationResponse'):
      responseString = base64.b64decode(prms['AuthenticationResponse'])
      objMsg.printMsg("response from server    = %s" % responseString)
      mfgAuthKeyString = binascii.b2a_hex(responseString)
      objMsg.printMsg("HDA Serial Number = %s" % HDASerialNumber)
      objMsg.printMsg("Mfg.Auth.Key = %s" % mfgAuthKeyString)
      if len(mfgAuthKeyString) != 64: # 64 chars = 32 bin-nibble-bytes
        objMsg.printMsg("Mfg. Auth. Key = %i bytes, not 32 bytes" % len(mfgAuthKeyString))
      else:
        mfgAuthKey = binascii.a2b_hex(mfgAuthKeyString)
        stat = 0 # PASS
    else:
      objMsg.printMsg("[33] AuthenticationResponse not found in data from server")
  else:
    objMsg.printMsg("[33] data from server is garbled")

  if testHardware == 1:
    if not stat:
      # BYTE[0]: resultsKey 33 (hex 21)
      # BYTE[1]: reqMfgAuth Key of 32 bytes (hex 20)
      # BYTE[2]: null 0x00
      # BYTE[3]: null 0x00
      # ((( data )))
      # frame = "\x21\x20\x00\x00"  + mfgAuthKeyString
      frame = "\x21\x20\x00\x00"  + mfgAuthKey
    else:
      # If we could not get a key, the data length is 0 & no key is sent
      frame = "\x21\x00\x00\x00"

    objMsg.printMsg("sending frame of data w/ mfgAuthKey to the initiator")
    objMsg.printMsg(" sending %d Bytes of data in frame" %(len(frame),))
    SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')
    objMsg.printMsg("Leaving Custom Request Mfg Key Auth handler - 33 - default key")

# ===================================================================
# CustomRequestSerialPortEnableKeyHandler():
# customer handler for results key of 34 - Request SP Enable Key
# ===================================================================
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# M2TD Cryptographic Infrastructure - KCI Interface Spec: Section 2.4
# kjb @ 09/26/07
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def CustomRequestSerialPortEnableKeyHandler():
  objMsg.printMsg("CustomRequestSerialPortEnableKeyHandler - Key 34")
  objMsg.printMsg( "*** Request SerialPort Enable Key")
  stat = 1 # default = FAIL
  objMsg.printMsg( "Entering Custom Request Mfg Key Auth handler - 34 - unique key")

  objMsg.printMsg( "RequestService('ReqSPEKey' %s" % HDASerialNumber)
  if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
    ScrCmds.raiseException(11044, "Invalid key transfer ReqSPEKey")
  method,prms = RequestService('ReqSPEKey',(HDASerialNumber)) # requestSerialPortEnableKey

  if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
    if prms.has_key('serialPortEnableKey'):
      responseString = prms['serialPortEnableKey']
      spEnableKeyString = binascii.b2a_hex(base64.b64decode(responseString))
      if len(spEnableKeyString) != 32: # 32 chars = 16 bin-nibble-bytes
        objMsg.printMsg("SP Enable Key = %i bytes, not 16 bytes" % len(spEnableKeyString))
      else:
        objMsg.printMsg("sPort Enable Key = %s" % spEnableKeyString)
        spEnableKey = binascii.a2b_hex(spEnableKeyString)
        stat = 0 # PASS
    else:
      objMsg.printMsg("[34] iserialPortEnableKey not found in data from server")
  else:
    objMsg.printMsg("[34] data from server is garbled")

  if testHardware:
    if not stat:
      # BYTE[0]: resultsKey 34 (hex 22)
      # BYTE[1]: spEnableKey length of 16 bytes (hex 10)
      # BYTE[2]: null 0x00
      # BYTE[3]: null 0x00
      # ((( data )))
      frame = "\x22\x10\x00\x00" + spEnableKey
    else:
      # If we could not get a key, the data length is 0 & no key is sent
      frame = "\x22\x00\x00\x00"

    objMsg.printMsg( "sending frame of data w/ spEnableKey to the initiator")
    SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')
    objMsg.printMsg("Leaving Custom Request Mfg Key Auth handler - 34 - unique key")


# ===================================================================4
# CustomRequestGetTDCertifiedKeyPairHandler():
# customer handler for results key of 3X - Request Certified Key Pair
# ===================================================================
def CustomRequestGetTDCertifiedKeyPairHandler(cert_type):
  objMsg.printMsg("CustomRequestGetTDCertifiedKeyPairHandler - Key [37,38,39]")
  objMsg.printMsg( "*** Request TD Certified Key Pair")
  objMsg.printMsg( "Entering Custom Request Mfg Key Auth handler - [37,38,39] - get certified TD key pair")

  d = ['primeExponentP','primeExponentQ','crtCoefficient','montModulus','pubExp','montPrimeQ','montPrimeP','primeQ',
       'primeP','privExp','modulus','RSAPrivateKey','Certificate']
  if cert_type == 0:
    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      ScrCmds.raiseException(11044, "GetCertifiedKeyPair of cert_type 0 unsupported")
    else:
      objMsg.printMsg( "RequestService('GetCertifiedKeyPair' HDASerialNumber =%s" %HDASerialNumber)
      method,prms = RequestService("GetCertifiedKeyPair",(HDASerialNumber,'SIGN','1.2.3.4.5.6.7.8.9.0'))
  else:
    if cert_type == 1:
      key_type = 'RSA1024PubExp17'
    else:
      key_type = 'RSA2048PubExp65537'

    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      name, prms = makeTDCICall('requestTDCertKeyPair', HDASerialNumber, 'SIGN', cert_type, key_type, '0')
    else:
      objMsg.printMsg( "RequestService('GetCertifiedTDKeyPair',('ser no.','SIGN','1.2.3.4.5.6.7.8.9.0))")
      name, prms = RequestService('GetCertifiedTDKeyPair',(HDASerialNumber,'SIGN',2 ,key_type, '0',))
    
  frame = "\x25\x00\x00\x00"
  objMsg.printMsg("sending answer to get_pc_file to the initiator")
  SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')

  if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
    objMsg.printMsg("prms        = %s" % prms)

    for x in d:
      if prms.has_key(x):
        responseString = prms[x]
        spEnableKeyString = binascii.b2a_hex(base64.b64decode(responseString))  #binary to ascii decoded string
        objMsg.printMsg("x = %i bytes" % len(spEnableKeyString))                           #print the length of the ascii string
        objMsg.printMsg("x = %s" % spEnableKeyString)                                      #print the ascii string
        spEnableKey = binascii.a2b_hex(spEnableKeyString)
        objMsg.printMsg("x = %i bytes" % len(spEnableKey))                           #print the length of the ascii string
        overall_len = len(spEnableKey)
        done = 0            #initialize done flag
        if overall_len > 512:
          frame = "\x01" + spEnableKey[:512]
          overall_len = overall_len - 512
          done = 0
        else:
          frame = "\x00" + spEnableKey[:512]
          done = 1
        SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')

        if done == 0:  ##not done
          if overall_len > 512:
            frame = "\x01" + spEnableKey[512:1024] #change index
            overall_len = overall_len - 512
            done = 0
          else:
            frame = "\x00" + spEnableKey[512:] #change index
            done = 1
          SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')
          if done == 0:  ##not done
            frame = "\x00" + spEnableKey[1024:]
            done = 1
            SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')
      else:
        objMsg.printMsg("key doesn't exist")                           #print the ascii string
  else:
    objMsg.printMsg("[37,38,39] data from server is garbled")
    objMsg.printMsg("Leaving CustomRequestGetTDCertifiedKeyPairHandler")

# =========================================================================
# CustomRequestGetTDCertifiedKeyPairHandlerCPC():
# customer handler for results key of 40,41,42 - Request Certified Key Pair
# =========================================================================
def CustomRequestGetTDCertifiedKeyPairHandlerCPC(cert_type):

  import struct
  objMsg.printMsg("CustomRequestGetTDCertifiedKeyPairHandlerCPC - Key [40,41,42]")
  objMsg.printMsg("*** Request TD Certified Key Pair (cert_type=%s)***" %cert_type)
  objMsg.printMsg("Entering Custom Request Mfg Key Auth handler - [40,41,42] - get certified TD key pair")

  d = ['primeExponentP','primeExponentQ','crtCoefficient','montModulus','pubExp','montPrimeQ','montPrimeP','primeQ',
       'primeP','privExp','modulus','RSAPrivateKey','Certificate']
  if cert_type == 0:
    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      ScrCmds.raiseException(11044, "GetCertifiedKeyPair of cert_type 0 unsupported")
    else:
      objMsg.printMsg("RequestService('GetCertifiedKeyPair',('%s','SIGN','1.2.3.4.5.6.7.8.9.0'))" %HDASerialNumber)
      method,prms = RequestService("GetCertifiedKeyPair",(HDASerialNumber,'SIGN','1.2.3.4.5.6.7.8.9.0'))
  else:
    if cert_type == 1:
      key_type = 'RSA1024PubExp17'
    else:
      key_type = 'RSA2048PubExp65537'

    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      name, prms = makeTDCICall('requestTDCertKeyPair', HDASerialNumber, 'SIGN', 2, key_type, '0')
    else:
      objMsg.printMsg("RequestService('GetCertifiedTDKeyPair',(%s,'SIGN',2,%s,'0'))"%(HDASerialNumber,key_type))
      name, prms = RequestService('GetCertifiedTDKeyPair',(HDASerialNumber,'SIGN',2 ,key_type, '0',))

  frame = "\x25\x00\x00\x00"
  objMsg.printMsg("sending answer to get_pc_file to the initiator")
  SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')

  if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
    objMsg.printMsg("prms   %s" % prms)

    for x in d:
      if prms.has_key(x):
        responseString = prms[x]
        spEnableKeyString = binascii.b2a_hex(base64.b64decode(responseString))  #binary to ascii decoded string
        objMsg.printMsg("x = %i bytes" % len(spEnableKeyString))                           #print the length of the ascii string
        objMsg.printMsg("x = %s" % spEnableKeyString)                                      #print the ascii string
        spEnableKey = binascii.a2b_hex(spEnableKeyString)
        objMsg.printMsg("x = %i bytes" % len(spEnableKey))                           #print the length of the ascii string
        overall_len = len(spEnableKey)
        done = 0            #initialize done flag
        if overall_len > 512:
          frame = struct.pack(">H",512) + "\x01"  + spEnableKey[:512]
          overall_len = overall_len - 512
          done = 0
        else:
          frame = struct.pack(">H",len(spEnableKey[:512])) + "\x00" + spEnableKey[:512]
          done = 1
        SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')

        if done == 0:  ##not done
          if overall_len > 512:
            frame = struct.pack(">H",512) + "\x01" + spEnableKey[512:1024] #change index
            overall_len = overall_len - 512
            done = 0
          else:
            frame = struct.pack(">H",len(spEnableKey[512:])) + "\x00" + spEnableKey[512:]
            done = 1
          SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')
          if done == 0:  ##not done
            frame = struct.pack(">H",len(spEnableKey[1024:])) + "\x00" + spEnableKey[1024:]
            done = 1
            SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')
      else:
        objMsg.printMsg("key doesn't exist")                           #print the ascii string
  else:
    objMsg.printMsg("[40,41,42] data from server is garbled")
    objMsg.printMsg("Leaving CustomRequestGetTDCertifiedKeyPairHandlerCPC")


# ===================================================================
# CustomRequestSerialPortEnableKeyAuthenticationHandler(...):
# customer handler for results key of 35 - SP Enable Key Authentication
# ===================================================================
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# M2TD Cryptographic Infrastructure - KCI Interface Spec: Section 2.5
# kjb @ 10/04/07
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def CustomRequestSerialPortEnableKeyAuthenticationHandler(rcvData):
  objMsg.printMsg("CustomRequestSerialPortEnableKeyAuthenticationHandler - Key 35")
  objMsg.printMsg("*** Request SerialPort Enable Key Authentication")
  stat = 1 # default = FAIL

  objMsg.printMsg( "Entering handler for unique key authentication - 35 get key")
  objMsg.printMsg( "DATA IN-> from serial port enable key ")
  objMsg.printMsg("rcvData        = %s" % rcvData)

  ### # Jump over the 25 bytes of (binary) header information
  ### index = 25
  index = 0

  # Grab the Random Challenge Value (RCV) sent to us
  randomChallengeValue =  rcvData[index:]

  if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
    ScrCmds.raiseException(11044, "ReqSPEAuth unsupported")

  objMsg.printMsg("---7> RequestService('ReqSPEAuth', randomChallengeValue = %s HDASerialNumber = %s"%(randomChallengeValue, HDASerialNumber))
  method,prms = RequestService('ReqSPEAuth',(randomChallengeValue, HDASerialNumber))

  if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
    if prms.has_key('AuthenticationResponse'):
      responseString = prms['AuthenticationResponse']
      spEnableAuthKeyString = binascii.b2a_hex(base64.b64decode(responseString))
      if len(spEnableAuthKeyString) != 64: # 64 chars = 32 bin-nibble-bytes
        objMsg.printMsg("SP Enable Auth. Key = %i bytes, not 32 bytes" % len(spEnableAuthKeyString))
      else:
        objMsg.printMsg("sPort Enable Auth. Key = %s" % spEnableAuthKeyString)
        spEnableAuthKey = binascii.a2b_hex(spEnableAuthKeyString)
        stat = 0 # PASS
    else:
      objMsg.printMsg("[35] serialPortEnableAuthKey not found in data from server")
  else:
    objMsg.printMsg("[35] data from server is garbled")

  if testHardware == 1:
    if not stat:
      # BYTE[0]: resultsKey 34 (hex 22)
      # BYTE[1]: spEnableAuthKey length of 16 bytes (hex 10)
      # BYTE[2]: null 0x00
      # BYTE[3]: null 0x00
      # ((( data )))
      frame = "\x22\x10\x00\x00" + spEnableAuthKey
    else:
      # If we could not get a key, the data length is 0 & no key is sent
      frame = "\x22\x00\x00\x00"

    objMsg.printMsg( "sending frame of data w/ spEnableAuthKey to the initiator")
    SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')
    objMsg.printMsg( "Leaving handler for unique key authentication - 35 get key")

def CustomRequestRandom32CharString(rcvData) :
  global RNs

  if DEBUG: objMsg.printMsg("Random Number = %s" % rcvData)
  try:
    RNs.append(rcvData)
  except NameError:
    pass

  frame = "\x37\x00\x00\x00"
  #SendBuffer(frame,expect=('_INPROGRESS',),tag='MSG')
  SendBuffer(frame,expect=BUFFER_EXPECTED_RESPONSES,tag='MSG')

  if DEBUG: objMsg.printMsg("Leaving handler for Random string generator")


# ===================================================================
# Definition of the generic "top-level" customer handler
# * add defaults so we can pass only data (in manual, non-initiator mode)
# ===================================================================
def customHandler(data,currentTemp=0,drive5=0,drive12=0,collectParametric=0):
  stat = 1 # default= FAIL

  # Get the resultsKey
  resultsKey = ord(data[0])

  if resultsKey == 32:
    CustomRequestSecureIDHandler()
  elif resultsKey == 33:
    CustomRequestManufacturingKeyAuthenticationHandler(base64.b64encode(binascii.a2b_hex(lastInitiatorData)))
  elif resultsKey == 34:
    CustomRequestSerialPortEnableKeyHandler()
  elif resultsKey == 35:
    CustomRequestSerialPortEnableKeyAuthenticationHandler(base64.b64encode(binascii.a2b_hex(lastInitiatorData)))
  elif resultsKey == 37:
    CustomRequestGetTDCertifiedKeyPairHandler(0)
  elif resultsKey == 38:
    CustomRequestGetTDCertifiedKeyPairHandler(1)
  elif resultsKey == 39:
    CustomRequestGetTDCertifiedKeyPairHandler(2)
  elif resultsKey == 40:
    CustomRequestGetTDCertifiedKeyPairHandlerCPC(0)
  elif resultsKey == 41:
    CustomRequestGetTDCertifiedKeyPairHandlerCPC(1)
  elif resultsKey == 42:
    CustomRequestGetTDCertifiedKeyPairHandlerCPC(2)
  elif resultsKey == 43:
    CustomRequestSecureIDHandlerCPC()
  elif resultsKey == 44:
    CustomRequestSecureHandlerGenerator()
  elif resultsKey == 45:
    CustomRequestSecureHandlerGeneratorCPC()
  ## Handlers 46 - 54 are part of the XMLRPC changes that reduce the number of unique RPCs.
  ## Below implemented if testSwitch.FE_0154366_231166_P_FDE_OPAL_SUPPORT:
  elif resultsKey == 46:    # MakerSymK AES256 unique key request
    CustomRequestKeyHandler(resultsKey)
  elif resultsKey == 47:    # MaintSymK AES256 unique key request
    CustomRequestKeyHandler(resultsKey)
  elif resultsKey == 48:    # MakerSymK 3DES unique key request
    CustomRequestKeyHandler(resultsKey)
  elif resultsKey == 59:    # Activation  unique key request - REQUEST_ACTIVATIONSYMK256_CRED
    CustomRequestKeyHandler(resultsKey)

  elif resultsKey == 49:    # This will be the 3DES key for default auth
    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      CustomRequestDefaultManufacturingKeyAuthenticationHandler(binascii.a2b_hex(lastInitiatorData),resultsKey)
    else:
      CustomRequestDefaultManufacturingKeyAuthenticationHandler(base64.b64encode(binascii.a2b_hex(lastInitiatorData)),resultsKey)
  elif resultsKey == 50:    # This will be the default maker AES256 auth
    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      CustomRequestDefaultManufacturingKeyAuthenticationHandler(binascii.a2b_hex(lastInitiatorData),resultsKey)
    else:
      CustomRequestDefaultManufacturingKeyAuthenticationHandler(base64.b64encode(binascii.a2b_hex(lastInitiatorData)),resultsKey)
  elif resultsKey == 51:    # This will be the unique maintsymk AES256 auth
    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      CustomRequestDefaultManufacturingKeyAuthenticationHandler(binascii.a2b_hex(lastInitiatorData),resultsKey)
    else:
      CustomRequestDefaultManufacturingKeyAuthenticationHandler(base64.b64encode(binascii.a2b_hex(lastInitiatorData)),resultsKey)

  elif resultsKey == 52:    # This will be the unique maker 3DES auth
    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      CustomRequestUniqueManufacturingKeyAuthenticationHandler(binascii.a2b_hex(lastInitiatorData),resultsKey)
    else:
      CustomRequestUniqueManufacturingKeyAuthenticationHandler(base64.b64encode(binascii.a2b_hex(lastInitiatorData)),resultsKey)
  elif resultsKey == 53:    # This will be the unique AES256 maker auth
    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      CustomRequestUniqueManufacturingKeyAuthenticationHandler(binascii.a2b_hex(lastInitiatorData),resultsKey)
    else:
      CustomRequestUniqueManufacturingKeyAuthenticationHandler(base64.b64encode(binascii.a2b_hex(lastInitiatorData)),resultsKey)
  elif resultsKey == 54:    # This will be the unique maintsymk AES256 auth
    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      CustomRequestUniqueManufacturingKeyAuthenticationHandler(binascii.a2b_hex(lastInitiatorData),resultsKey)
    else:
      CustomRequestUniqueManufacturingKeyAuthenticationHandler(base64.b64encode(binascii.a2b_hex(lastInitiatorData)),resultsKey)

  elif resultsKey == 55:    # This is for the random string generator
    CustomRequestRandom32CharString(lastInitiatorData)
  elif resultsKey == 60:    # REQUEST_ACTIVATIONSYMK256_CRED
    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      CustomRequestDefaultManufacturingKeyAuthenticationHandler(binascii.a2b_hex(lastInitiatorData),resultsKey)
    else:
      CustomRequestDefaultManufacturingKeyAuthenticationHandler(base64.b64encode(binascii.a2b_hex(lastInitiatorData)),resultsKey)
  elif resultsKey == 61:    # AUTH_ACTIVATION_AES256_UNIQUE
    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      CustomRequestUniqueManufacturingKeyAuthenticationHandler(binascii.a2b_hex(lastInitiatorData),resultsKey)
    else:
      CustomRequestUniqueManufacturingKeyAuthenticationHandler(base64.b64encode(binascii.a2b_hex(lastInitiatorData)),resultsKey)

  else:
    objMsg.printMsg("Unknown results key - resultsKey= %s" %resultsKey)

# ===================================================================
#
# data from initiator
#
# ===================================================================
def printInitiatorData(buf, *args, **kargs):
  objMsg.printMsg( "printInitiatorData ===2> %s"%binascii.a2b_hex(buf))

# ===================================================================
# CustomInitiatorDataFileNameHandler(...):
# INPUTS:
# * data         : fileName
# custom handler for results key of 80 - fileName of data from initator
# ===================================================================
def customInitiatorDataFileNameHandler(iData):
  stat = 1 # default = FAIL

  # Jump over the 3 bytes of (binary) header information
  index = 2
  # Grab the Random Challenge Value (RCV) sent to us
  fileName = iData[index:]

  objMsg.printMsg("===3> customInitiatorDataFileNameHandler = %s" % fileName)

  return fileName

# ===================================================================
# CustomInitiatorDataHandler(...):
# INPUTS:
# * data         : data
# custom handler for results key of 82 - data from initator
# ===================================================================
def customInitiatorDataHandler(iData):
  stat = 1 # default = FAIL

  # Jump over the 3 bytes of (binary) header information
  index = 3

  # Grab the Random Challenge Value (RCV) sent to us
  nonce = binascii.b2a_hex(iData[index:index+32])

  objMsg.printMsg("===8> Nonce from initiator = %s" % nonce)

  return nonce

# ===================================================================
# Definition of the generic "top-level" customer handler
# resultsKeys 80-85
# * add defaults so we can pass only data (in manual, non-initiator mode)
# ===================================================================
def customInitiatorHandler(data, *args, **kargs):
  stat = 1 # default= FAIL

  global lastInitiatorData

  objMsg.printMsg( "Entering File Handler ")
  objMsg.printMsg( "===4> %s"%(binascii.b2a_hex(data)))

  # Get the resultsKey
  resultsKey = ord(data[0])
  objMsg.printMsg( "===5> resultsKey: %s"%(hex(resultsKey)))

  if resultsKey == 80:
    lastInitiatorFileName = customInitiatorDataFileNameHandler(data)
  elif resultsKey == 82:
    lastInitiatorData = customInitiatorDataHandler(data)
  else:
    objMsg.printMsg("Got resultsKey :%s"%resultsKey)

  objMsg.printMsg( "Leaving customInitiatorHandler")


#*************************************************
class CTCGPrepTest:
   def __init__(self, dut, params={}, SPMode = 0):
      self.dut = dut
      if testSwitch.FE_0143087_357552_BYPASS_SETUP_JUST_UNLOCK:
         self.params = params

      if testSwitch.NoIO or self.dut.certOper or SPMode:
         objMsg.printMsg("TCG_Init no need register call back for SP IO process or CERT operation")
      else:
         objMsg.printMsg("TCG_Init Register call back: customHandler")
         if testSwitch.FE_0154366_231166_P_FDE_OPAL_SUPPORT:
            RegisterResultsCallback(customHandler,range(32,62),useCMLogic=0)
         else:
            RegisterResultsCallback(customHandler,[32,33,34,35,36,37,38,39,40,41,42,43,44,45],useCMLogic=0)
         objMsg.printMsg("TCG_Init Register call back: customInitiatorHandler")
         RegisterResultsCallback(customInitiatorHandler, range(80,85), useCMLogic=1)

      self.prm_TCG = getattr(TP,"prm_TCG",{})
      # from CustomCfg import CCustomCfg
      # CustConfig = CCustomCfg()
      # CustConfig.getDriveConfigAttributes()
      self.CS  = getattr(TP,"prm_TCG",{}).get('CORE_SPEC', 0x0002)
      self.SSC = getattr(TP,"prm_TCG",{}).get('SSC_VERSION', 0x0001)
      self.MASTER_AUTHORITY = getattr(TP,"prm_TCG",{}).get('MASTER_AUTHORITY', 0x0001)
      self.MSID_OFFSET = getattr(TP,"prm_TCG",{}).get('MSID_OFFSET', 64)
      if testSwitch.FE_0146812_231166_P_ALLOW_DL_UNLK_BY_PN_TCG:
        self.DISABLE_LOCK_FW_ON_RESET = getattr(TP,"prm_TCG",{}).get('DISABLE_LOCK_FW_RST_PN', '')

        if (self.DISABLE_LOCK_FW_ON_RESET != '') and re.search(self.DISABLE_LOCK_FW_ON_RESET, self.dut.partNum):
          self.DISABLE_LOCK_FW_ON_RESET = True
        else:
          self.DISABLE_LOCK_FW_ON_RESET = False

      self.CHECK_ENCRYPTION = getattr(TP,"prm_TCG",{}).get('CHECK_ENCRYPTION', 0)
      self.CHECK_RNG = getattr(TP,"prm_TCG",{}).get('CHECK_RNG', 0)
      self.UNIFIED_F3 = getattr(TP,"prm_TCG",{}).get('UNIFIED_F3', 0)

      #if testSwitch.FE_0181344_231166_P_DELLA_FAMILY_SED_ENHANCEMENTS and self.SECURITY_TYPE == SECURED_DIAG_AND_DOWNLOAD:
         #self.SetUseState.update(SDnD_T577_SetUSEState_Updates)
         #self.SetMfgState.update(SDnD_T577_SetMFGState_Updates)

      self.MSID_PWD_TYPE = 0xC
      self.SECURITY_TYPE = self.getSecurityOrFDEType('SECURITY_TYPE', SECURED_DIAG_AND_DOWNLOAD)
      self.FDE_TYPE      = self.getSecurityOrFDEType('FDE_TYPE', 'FDE BASE')
      if self.SECURITY_TYPE == SECURED_DIAG_AND_DOWNLOAD:
         self.CUSTOMER_OPTION = CUSTOMER_OPTION_Lookup['SECURED_DRIVE']
      elif self.FDE_TYPE == ISE:
         self.CUSTOMER_OPTION = CUSTOMER_OPTION_Lookup[ISE]
      elif self.FDE_TYPE == FIPS_SED:
         self.CUSTOMER_OPTION = CUSTOMER_OPTION_Lookup['FIPS_SELF_ENCRYPTING_DRIVE']
      else:
         self.CUSTOMER_OPTION = CUSTOMER_OPTION_Lookup['SELF_ENCRYPTING_DRIVE']
      self.REPORTING_MODE = REPORTING_MODE
      self.ACTIVATE = testSwitch.FE_0385431_SED_ACTIVATION
      if testSwitch.IS_SDnD:
         self.SECURITY_TYPE = 'SECURED BASE (SD AND D)'
         self.CHECK_ENCRYPTION = 0
         self.CHECK_RNG = 0
         self.UNIFIED_F3 = 0
         self.CUSTOMER_OPTION = CUSTOMER_OPTION_Lookup['SECURED_DRIVE']

      if not self.SSC:  # 0 = EntSSC
         if FW_PLATFORM_FAM == 'DELLA':
            self.MSID_PWD_TYPE = 0xE
            self.SYMK_KEY_TYPE = 2
         elif FW_PLATFORM_FAM == 'CANNON':
            self.MSID_PWD_TYPE = 0xD
            self.SYMK_KEY_TYPE = 1
      elif self.SSC:    # 1 = OpalSSC
         self.MSID_PWD_TYPE = 0xE
         self.SYMK_KEY_TYPE = 2

      if testSwitch.FE_0225282_231166_P_TCG2_SUPPORT:
         self.TCG_VERSION = 2    
      else:
         self.TCG_VERSION = 1    
      
      if not objRimType.isIoRiser() or SPMode:

         SED_Serial.sedVar.enableISE = 0
         #SED_Serial.driveType = {OPAL_SSC:'OPAL', ENT_SSC:'TCG'}[self.SSC]   #Drive Types:  'OPAL' and 'TCG'
         SED_Serial.sedVar.driveType = 'OPAL'      #More
         SED_Serial.sedVar.coreSpec = self.CS      #Core Specs:   1 and 2
         SED_Serial.sedVar.masterSymKType = 2      #1: Triple Des     2:AES256
         SED_Serial.sedVar.secureBaseDriveType = 0 #need to setup detection for SD&D

         self.symkKey = 2           
         self.custMode = self.CUSTOMER_OPTION      

         objMsg.printMsg("custMode = %s" %(self.custMode))             

      objMsg.printMsg("CORE_SPEC   :%d, 0x01 = CoreSpec1, 0x02 = CoreSpec2" %self.CS)
      objMsg.printMsg("SSC_VERSION :%d, 0x00 = ENT_SSC,  0x01 = OPAL_SSC" %self.SSC)
      objMsg.printMsg("MASTER_AUTHORITY : %d, 0 = MSID, 1 = PSID Authentication" % self.MASTER_AUTHORITY)
      objMsg.printMsg("CHECK_ENCRYPTION :%d CHECK_RNG :%d " %(self.CHECK_ENCRYPTION,self.CHECK_RNG))   
      objMsg.printMsg("UNIFIED_F3 :%d " %(self.UNIFIED_F3))   
      objMsg.printMsg("TCG_VERSION :%d " %(self.TCG_VERSION))   
      objMsg.printMsg("SDnD :%d " %(testSwitch.IS_SDnD))   
      objMsg.printMsg("Activation :%d " %(self.ACTIVATE))   
      objMsg.printMsg("CUSTOMER_OPTION :%d (1=SED, 2= SDnD, 3=ISE, 4=FIPS)" %(self.CUSTOMER_OPTION))   

      #Setting the IEEE_1667
      self.IEEE_1667 = str(self.dut.driveConfigAttrs.get('IEEE1667_INTF', ('=',getattr(TP,"prm_TCG",{}).get('IEEE1667_INTF', 'NA') ))[1]).rstrip()
      #If SDnD, always set to deactivated as this is NA
      if self.IEEE_1667 in [None,'NA','NONE'] and testSwitch.IS_SDnD and testSwitch.SET_IEEE_1667_DEACTIVATED_IF_SDND_AND_NA:
         self.IEEE_1667 = 'DEACTIVATED'

      if testSwitch.FE_0234883_426568_P_IEEE1667_SUPPORT:
         if self.IEEE_1667 not in [None,'NA','NONE']:
            #If IEEE_1667 is "ACTIVATED" or "DEACTIVATED"
            if objRimType.isIoRiser():
               self.FEATURE_OPTION = (0x0000,0x0000,0x0000,IEEE1667_Lookup.get(self.IEEE_1667,'ACTIVATED'),)
            else:
               self.FEATURE_OPTION = IEEE1667_Lookup.get(self.IEEE_1667,'ACTIVATED')
         else:
            #No need to set
            if objRimType.isIoRiser():
               self.FEATURE_OPTION = (0x0000,0x0000,0x0000,0x0000)
            else:
               self.FEATURE_OPTION = 0

      objMsg.printMsg("IEEE1667 :%s " %(self.IEEE_1667))       
      if not objRimType.isIoRiser():   objMsg.printMsg("FEATURE_OPTION :%d " %(self.FEATURE_OPTION))       


   def fullInitCodeDwnld(self):
      if self.SSC == ENT_SSC:
         SED_Serial.sedVar.driveType = 'TCG'

      pd = PackageDispatcher(self.dut, 'TGT4')#bridge
      SED_Serial.BridgeCode = pd.getFileName()

      pd = PackageDispatcher(self.dut, 'OVL4')#IV
      SED_Serial.IVFile = pd.getFileName()


      pd = PackageDispatcher(self.dut, 'TGT2')#target
      SED_Serial.SignedSEDTarget = pd.getFileName()

      SED_Serial.fullInitCodeDwnld()
      if testSwitch.FE_0334158_379676_P_RFWD_FFV_1_POINT_5:
         self.SaveRFWDSigs()

   def SaveRFWDSigs(self):
      '''Save the RFWD SIGS file to FIS attributes when a drive downloads target
      code.  These attributes define what code is actually on the drive and are
      used later by CCV for RFWD.  The attributes are used to required to manage
      On-the-Fly config updates where no redownload of target code occurs.
      '''

      objMsg.printMsg("TCG.SaveRFWDSigs for RFWD")
      
      sigFilename = PackageDispatcher(self.dut, 'SIGS').getFileName()
      if sigFilename:  # check for RFWD enabled
         self.dut.driveattr['RFWD_SIGNATURE_1'] = sigFilename[0:32]
         self.dut.driveattr['RFWD_SIGNATURE_2'] = sigFilename[32:64]
         self.dut.driveattr['RFWD_SIGNATURE_3'] = sigFilename[64:]

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      #More
      if not objRimType.isIoRiser():
         objMsg.printMsg("TCGPrepTest run - return for serial port cell")
         return

      objMsg.printMsg("TCGPrepTest run")
      self.oProcess = CProcess()
      self.CheckFDEState()

      if self.dut.nextOper == "FNG2" or testSwitch.FE_0385431_MOVE_FINAL_LIFE_STATE_TO_END:
         return

      if not self.dut.LifeState == "00" and not testSwitch.virtualRun:
         objMsg.printMsg("Wrong, LifeState :%s which is not SETUP state" %self.dut.LifeState)
         ScrCmds.raiseException(14862, "Wrong, LifeState is not SETUP state")

   def unlockFwDlPortOnReset(self):
      if not testSwitch.BF_0147704_231166_P_ALWAYS_SET_LOR_FW_PORT_TCG:
         if not self.DISABLE_LOCK_FW_ON_RESET:
            return
      oProcess = CProcess()

      prm_575_03 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_03',
           "TEST_MODE"       : (0x0002,),       ##TestMode         (Prm[0] & 0xff) = Start Session
           "REPORTING_MODE"  : (0x8000,),       ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),       ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0000,),       ##PasswordType     (Prm[2] & 0xff)
           "DRIVE_STATE"     : (0x0000,),       ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0000,),       ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0205,),       ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0000,),       ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0001,),       ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),       ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),       ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Start Admin session")
      oProcess.St(prm_575_03,timeout=360)

      prm_575_06 = {
         'test_num'        : 575,
         'prm_name'        : 'prm_575_06',
         "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
         "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
         "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
         "PASSWORD_TYPE"   : (0x0001,),     #PasswordType      (Prm[2] & 0xff)   = UNIQUE_MAKERSYMK
         "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
         "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
         "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
         "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
         "UIDLSWL"         : (0x0004,),     ##UidLswl           Prm[7]
         "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
         "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      if self.SSC == 1 and testSwitch.FE_0154366_231166_P_FDE_OPAL_SUPPORT:
         prm_575_06['CERT_TSTMODE'] = 1
         prm_575_06['PASSWORD_TYPE'] = 0xE

      objMsg.printMsg("Authenticate to MakerSymk")
      oProcess.St(prm_575_06,timeout=360)

      prm_575_04 = {
         'test_num'        : 575,
         'prm_name'        : 'prm_575_04',
         "TEST_MODE"       : (0x0011,),     ##TestMode         (Prm[0] & 0xff)   = Get MSID From Drive
         "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
         "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
         "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)   = DEFAULT MSID
         "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
         "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
         "UIDMSWL"         : (0x0000,),     ##UidLswu           Prm[5]
         "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
         "UIDLSWL"         : (0x0000,),     ##UidLswl           Prm[7]
         "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
         "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Get MSID from Drive")
      oProcess.St(prm_575_04,timeout=360)
      
      prm_575_07 = {
         'test_num'        : 575,
         'prm_name'        : 'prm_575_07',
         "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
         "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
         "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
         "PASSWORD_TYPE"   : (0x0002,),     #PasswordType      (Prm[2] & 0xff)   = MSID
         "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
         "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
         "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
         "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
         "UIDLSWL"         : (0x0006,),     ##UidLswl           Prm[7]
         "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
         "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Authenticate to sid")
      oProcess.St(prm_575_07,timeout=360)


      prm_575_Get_FW_Port_Locking_Table = {
        'test_num': 575,
        'prm_name'        : 'prm_575_Get_FW_Port_Locking_Table',
        'timeout': 30,
      	"TEST_MODE"  : (0x05,),
      	"REPORTING_MODE"  : (0x8000,),
      	"WHICH_SP"  : (0x0000,),
      	"PASSWORD_TYPE"  : (0x0000,),
      	"DRIVE_STATE"  : (0x0000,),
      	"UIDMSWU"  : (0x0001,),
      	"UIDMSWL"  : (0x0002,),
      	"UIDLSWU"  : (0x0001,),
      	"UIDLSWL"  : (0x0002,),
      	"CERT_TSTMODE" : (0x0000,),
      	"CERT_KEYTYPE"    : (0x0000,),
      }

      prm_575_Disable_FW_Port_LOR = {
        'test_num': 575,
        'prm_name' : 'prm_575_Disable_FW_Port_LOR',
        'timeout': 30,
        "TEST_MODE"  : (0x15,),
        "REPORTING_MODE"  : (0x8000,),
        "UIDMSWU"  : (0x0001,),
        "UIDMSWL"  : (0x0002,),
        "UIDLSWU"  : (0x0001,),
        "UIDLSWL"  : (0x0002,),
      }
      if self.SSC == 1 and testSwitch.FE_0154366_231166_P_FDE_OPAL_SUPPORT:
         prm_575_Disable_FW_Port_LOR['PASSWORD_TYPE'] = 0xE
         prm_575_Get_FW_Port_Locking_Table['PASSWORD_TYPE'] = 0xE


      if testSwitch.BF_0147704_231166_P_ALWAYS_SET_LOR_FW_PORT_TCG:
         if not self.DISABLE_LOCK_FW_ON_RESET:
            prm_575_Disable_FW_Port_LOR['TEST_MODE'] = 0x19 #Lock FW port
            if testSwitch.BF_0149206_231166_P_SET_LOR_AND_UNLOCK_DL_PORT:
               prm_575_Disable_FW_Port_LOR['prm_name'] = 'prm_575_Lock_FW_Download_Port'
            else:
               prm_575_Disable_FW_Port_LOR['prm_name'] = 'prm_575_Enable_FW_Port_LOR'
         elif testSwitch.BF_0149206_231166_P_SET_LOR_AND_UNLOCK_DL_PORT:
            prm_575_Disable_FW_Port_LOR['prm_name'] = 'prm_575_UnLock_FW_Download_Port'
            prm_575_Disable_FW_Port_LOR['TEST_MODE'] = 0x13 #unlock FW port

      oProcess.St(prm_575_Disable_FW_Port_LOR)

      if testSwitch.BF_0149206_231166_P_SET_LOR_AND_UNLOCK_DL_PORT:
         if not self.DISABLE_LOCK_FW_ON_RESET: #So we want to lock fw port
            prm_575_Disable_FW_Port_LOR['TEST_MODE'] = 0x2C
            prm_575_Disable_FW_Port_LOR['prm_name'] = 'prm_575_Set_LOR'
         else:
            prm_575_Disable_FW_Port_LOR['TEST_MODE'] = 0x15
            prm_575_Disable_FW_Port_LOR['prm_name'] = 'prm_575_Clear_LOR'

         oProcess.St(prm_575_Disable_FW_Port_LOR)

      oProcess.St(prm_575_Get_FW_Port_Locking_Table)


      prm_575_12 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_12',
           "TEST_MODE"       : (0x0003,),      ##TestMode         (Prm[0] & 0xff)
           "REPORTING_MODE"  : (0x8000,),       ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),       ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0000,),       ##PasswordType     (Prm[2] & 0xff)
           "DRIVE_STATE"     : (0x0000,),       ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0000,),       ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0205,),       ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0000,),       ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0001,),       ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),       ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),       ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Close Admin session")
      oProcess.St(prm_575_12,timeout=360)

   #**********************************************************
   def TCGPrep(self):

      
      if not objRimType.isIoRiser():

         objMsg.printMsg("TCGPrep run - Serial Port Personalization")
         Y2backup = self.dut.SkipY2
         self.dut.SkipY2 = True    

         if self.CHECK_RNG:      # Note that this *must* be an FDE drive for the RNG check to work !!
            objMsg.printMsg ('Checking RNG engine before TCGPrep...')
            self.RNGBlkChkSPIO()
         
         SED_Serial.fullPersonalization(CORE_SPEC=self.CS,CUSTOMER_OPTION=self.custMode,OPAL_SSC_SUPPORT=self.SSC,\
                                        SYMK_KEY_TYPE=self.symkKey,REPORTING_MODE=self.REPORTING_MODE,TCG_VERSION=self.TCG_VERSION,FEATURE_OPTIONS = self.FEATURE_OPTION,ACTIVATE=self.ACTIVATE) 
         
         if not testSwitch.FE_0385431_MOVE_FINAL_LIFE_STATE_TO_END:
            self.dut.driveattr['IEEE1667_INTF'] = self.IEEE_1667
            SED_Serial.securityConfigVerification(CORE_SPEC=self.CS,CUSTOMER_OPTION=self.custMode,OPAL_SSC_SUPPORT=self.SSC,\
                                                  SYMK_KEY_TYPE=self.symkKey,REPORTING_MODE=self.REPORTING_MODE,TCG_VERSION=self.TCG_VERSION,ACTIVATE=self.ACTIVATE)

         self.dut.driveattr['TD_SID'] = DriveAttributes['TD_SID']
         self.dut.SkipY2 = Y2backup

         if testSwitch.virtualRun: return
         self.CheckFDEState()
         if not self.dut.LifeState == "80":
            if testSwitch.FE_0385431_MOVE_FINAL_LIFE_STATE_TO_END and self.dut.LifeState == "81":
               objMsg.printMsg("Okay, after personalization, LifeState :%s" %self.dut.LifeState)
            else: 
               objMsg.printMsg("Wrong, after personalization, LifeState :%s" %self.dut.LifeState)
               ScrCmds.raiseException(14862, "After personalization, LifeState is not correct")

         if self.SECURITY_TYPE == DRM_SCSA:
            SED_Serial.ditsLockUnlock(lockPort = 0)
            SED_Serial.ditsSCSACmd(encrypted = 1)

         return

      try:
        objMsg.printMsg("TCGPrep run")
        oProcess = CProcess()

        if self.UNIFIED_F3:      # Note that this *must* be an FDE drive for the Unified F3 to work !!
           objMsg.printMsg ('Unified F3 support before TCGPrep...')
           self.UnifiedF3()

        if self.CHECK_ENCRYPTION:      # Note that this *must* be an FDE drive for the Encryption check to work !!
           objMsg.printMsg ('Checking encryption block engine before TCGPrep...')
           self.EncryptionBlkChk()

        if self.CHECK_RNG:      # Note that this *must* be an FDE drive for the RNG check to work !!
           objMsg.printMsg ('Checking RNG engine before TCGPrep...')
           self.RNGBlkChkT575()

        objMsg.printMsg("Running test 575 - Get Properties")
        prm_575_02 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_02',
           "TEST_MODE"       : (0x0006,),      ##TestMode         (Prm[0] & 0xff)
           "REPORTING_MODE"  : (0x8000,),      ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),      ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0000,),      ##PasswordType     (Prm[2] & 0xff)
           "DRIVE_STATE"     : (0x0000,),      ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0000,),      ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0000,),      ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0000,),      ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0000,),      ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),      ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),      ##CertKeyType      ((Prm[2] & 0xff00) >> 8)

        }
        if testSwitch.FE_0154366_231166_P_FDE_OPAL_SUPPORT:
           prm_575_02.update({
               "CORE_SPEC"       : self.CS,
               "SSC_VERSION"     : self.SSC,
               "DEBUG_FLAG"      : 1,

           })
           if self.SSC==1:
              #alt rev code for opal
              prm_575_02["MASTER_PW_REV_CODE"] = 0xFFFE

        oProcess.St(prm_575_02,timeout=360)



        objMsg.printMsg("Running test 577 - Writing credentials - Setting MFG state - Default PSID")
        prm_577_01 = {
           'test_num'        : 577,
           'prm_name'        : 'prm_577_01',
           "TEST_MODE"       : (0x0005,),   # Personalize Drive and Set Drive State
           "REPORTING_MODE"  : (0x8000,),
           "MSID_TYPE"       : (0x0000,),   # Default PSID
           "DRIVE_STATE"     : (0x0081,),   # Set to MFG State
           "FW_PLATFORM"     : (0x0010,),
           "CERT_KEYTYPE"    : (0x0000,),
        }
        if SEDprm_AutoDetect:
           prm_577_01["TEST_MODE"] = (0x0025,)

        if testSwitch.FE_0225282_231166_P_TCG2_SUPPORT:
           prm_577_01["CUSTOMER_OPTION"]     = self.CUSTOMER_OPTION

        if testSwitch.FE_0234883_426568_P_IEEE1667_SUPPORT:
           #if self.IEEE_1667 not in [None,'NA']:
           #   prm_577_01["FEATURE_OPTION"] = (0x0000,0x0000,0x0000,IEEE1667_Lookup.get(self.IEEE_1667,'ACTIVATED'),)
           prm_577_01["FEATURE_OPTION"] = self.FEATURE_OPTION

        if testSwitch.IS_SDnD:
           prm_577_01.update(SDnD_T577_SetMFGState_Updates)

        oProcess.St(prm_577_01,timeout=3600)

        if testSwitch.FE_0146812_231166_P_ALLOW_DL_UNLK_BY_PN_TCG:
          self.unlockFwDlPortOnReset()


        #577 - Verification of credentials - Change to USE state - FIS's PSID
        prm_577_30 = {
           'test_num'        : 577,
           'prm_name'        : 'prm_577_30',
           "TEST_MODE"       : (0x0006,),   # Verify Personalization and Set Drive State
           "REPORTING_MODE"  : (0x8000,),
           "MSID_TYPE"       : (0x0001,),   # FIS's PSID
           "DRIVE_STATE"     : (0x0080,),
           "FW_PLATFORM"     : (0x0010,),
           "CERT_KEYTYPE"    : (0x0000,),
        }
        if SEDprm_AutoDetect:
           prm_577_30["TEST_MODE"] = (0x0026,)

        if testSwitch.FE_0225282_231166_P_TCG2_SUPPORT:
           prm_577_30["CUSTOMER_OPTION"]     = self.CUSTOMER_OPTION
        
        if testSwitch.IS_SDnD:
           prm_577_30.update(SDnD_T577_SetUSEState_Updates)
        
        if testSwitch.FE_0141467_231166_P_SAS_FDE_SUPPORT:
           if TP.prm_TCG['PREP_END_STATE'] == 'USE':
              objMsg.printMsg("Running test 577 - Verification of credentials - Change to USE state - FIS's PSID")
              oProcess.St(prm_577_30,timeout=3600)

           self.CheckFDEState()

           if not self.dut.LifeState == LifeStates[TP.prm_TCG['PREP_END_STATE']] and not testSwitch.virtualRun:
              msg = "After personalization, LifeState :%s which is not %s state" % (self.dut.LifeState, LifeStates[TP.prm_TCG['PREP_END_STATE']])
              objMsg.printMsg(msg)
              ScrCmds.raiseException(14862, msg)
        else:
           if not testSwitch.FE_0385431_MOVE_FINAL_LIFE_STATE_TO_END:
              objMsg.printMsg("Running test 577 - Verification of credentials - Change to USE state - FIS's PSID")
              oProcess.St(prm_577_30,timeout=3600)

           self.CheckFDEState()
           if not self.dut.LifeState == "80":
              if testSwitch.FE_0385431_MOVE_FINAL_LIFE_STATE_TO_END and self.dut.LifeState == "81":
                 objMsg.printMsg("Okay, after personalization, LifeState :%s" %self.dut.LifeState)
              else: 
                 if not testSwitch.virtualRun:
                    objMsg.printMsg("Wrong, after personalization, LifeState :%s" %self.dut.LifeState)
                    ScrCmds.raiseException(14862, "After personalization, LifeState is not correct")

        if testSwitch.virtualRun:
           sidStr = '0'*32
           dut.driveattr['TD_SID'] = sidStr
           DriveAttributes['TD_SID'] = sidStr

        if self.SECURITY_TYPE == DRM_SCSA:
           self.InterfaceSCSA()

      finally:
        if testSwitch.FE_0146812_231166_P_ALLOW_DL_UNLK_BY_PN_TCG:
          self.RemoveCallback()

   def RemoveCallback(self):
      objMsg.printMsg("Remove Register call back: customHandler")
      RegisterResultsCallback("",[32,33,34,35,36,37,38,39,40,41,42,43,44,45])
      objMsg.printMsg("Remove Register call back: customInitiatorHandler")
      RegisterResultsCallback("", range(80,85))

###################################################################################################
#                                     CheckFDEState                                               #
#                                                                                                 #
#     This function contains the commands to check the life state of the TCG FDE drive            #
#                                                                                                 #
###################################################################################################
   def CheckFDEState(self, checkLifeState = "NONE", SPMode = 0):

      objMsg.printMsg("*** CheckDriveFDEState ")
      if not objRimType.isIoRiser() or SPMode:
         
         SED_Serial.match575SSCParamsToSPTest(coreSp=self.CS,opalSupp=self.SSC, symkKey=self.symkKey, reportOp=self.REPORTING_MODE,custMode=self.custMode,interfaceType='SATA',activateMthd=self.ACTIVATE,tcgType=self.TCG_VERSION)

         try: 
            SED_Serial.SSCDriveVerify(binResponse = True)
            SED_Serial.SEDdiscovery()
            self.OpenAdminSession(SPMode)
            self.dut.LifeState = binascii.hexlify(SED_Serial.getStateTable())
            objMsg.printMsg("Drive is in %s state" %(self.dut.LifeState))
            self.CloseAdminSession(SPMode)
         except:
            objMsg.printMsg("Failed checking fde state, retry ")   
            DriveOff(5)
            DriveOn(5000,12000,10)
            import sptCmds
            sptCmds.enableESLIP(retries = 0, timeout = 1, printResult = False) #enable ESlip on drive
            UseESlip(1) #enable ESlip on cell

            objMsg.printMsg("sleep 30 seconds.....")  
            time.sleep(30) # wait for 30 seconds
            objMsg.printMsg("after sleep 30 seconds")

            SED_Serial.SSCDriveVerify(binResponse = True)
            SED_Serial.SEDdiscovery()
            self.OpenAdminSession(SPMode)
            self.dut.LifeState = binascii.hexlify(SED_Serial.getStateTable())
            objMsg.printMsg("Drive is in %s state" %(self.dut.LifeState))
            self.CloseAdminSession(SPMode)
      else:
         oProcess = CProcess()

         objMsg.printMsg("Running test 575 - Setting CS1.0/2.0 and EntSSC/OpalSSC support")
      
         prm_575_SetCPCSupport["CORE_SPEC"]        = self.CS
         if not SEDprm_AutoDetect:
            prm_575_SetCPCSupport["SSC_VERSION"]      = self.SSC
         prm_575_SetCPCSupport["MASTER_AUTHORITY"] = self.MASTER_AUTHORITY

         if testSwitch.FE_0225282_231166_P_TCG2_SUPPORT:
            prm_575_SetCPCSupport["TCG_VERSION"]      = self.TCG_VERSION

         if testSwitch.FE_0154366_231166_P_FDE_OPAL_SUPPORT:
            if self.SSC == 1:
               prm_575_SetCPCSupport["MAINTSYMK_SUPP"]=1
               prm_575_SetCPCSupport["SYMK_KEY_TYPE"]=2
               prm_575_SetCPCSupport["MASTER_PW_REV_CODE"]=0xFFFE
         
         if DEBUG:
            # DEBUG_FLAG is used to force specify PSID Support, (a new properlly named 
            # parameter is in the works for that,)  this is due to a difference in how 
            # test 577 Starts between CPC and Sata Initiaotr.
            prm_575_SetCPCSupport['DEBUG_FLAG'] = 1

         if testSwitch.FE_0141467_231166_P_SAS_FDE_SUPPORT:
            prm_575_SetCPCSupport["MSID_OFFSET"] = self.MSID_OFFSET           ##Set MSID offset into data structure for initiator

         oProcess.St(prm_575_SetCPCSupport,timeout=360)

         objMsg.printMsg("*** T575 - Discovery ")
         prm_575_01 = {
            'test_num'        : 575,
            'prm_name'        : 'prm_575_01',
            "TEST_MODE"       : (0x0007,),     ##TestMode         (Prm[0] & 0xff)
            "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
            "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
            "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)     0 - Default
            "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
            "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
            "UIDMSWL"         : (0x0205,),     ##UidLswu           Prm[5]
            "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
            "UIDLSWL"         : (0x0001,),     ##UidLswl           Prm[7]
            "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
            "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
            "DblTablesToParse": ['P575_DEVICE_DISC_DATA',]          ##Parse out dblog data
         }
         oProcess.St(prm_575_01,timeout=360)

         if testSwitch.virtualRun:
           if not hasattr(self.dut,  'LifeState'):
             self.dut.LifeState = '00'
         else:
           self.dut.LifeState = self.dut.objSeq.SuprsDblObject['P575_DEVICE_DISC_DATA'][-1]['LIFE_CYCLE_STATE']

      objMsg.printMsg("self.dut.LifeState :%s" %self.dut.LifeState)

      if testSwitch.FE_0141467_231166_P_SAS_FDE_SUPPORT:
         objMsg.printMsg("Drive is in %s state." % LifeStatesLookup.get(self.dut.LifeState, 'INVALID'))
         if not LifeStatesLookup.has_key(self.dut.LifeState):
            if testSwitch.BF_0157429_231166_P_FIX_LOCKED_SED_DRV_INIT:
               self.dut.driveattr['TD_SID']='NONE'
               DriveAttributes['TD_SID']='NONE'
               self.dut.driveattr['FDE_DRIVE'] = 'NONE'
            else:
               objPwrCtrl.powerCycle()

         if testSwitch.WA_0174645_231166_P_PWR_CYCLE_ALL_ON_INVALID_SED and objRimType.isIoRiser():
            if self.dut.LifeState == 'FF' or not (LifeStatesLookup.has_key(self.dut.LifeState)):
               objPwrCtrl.powerCycle(ataReadyCheck = True)
      else:
         for tempState in LifeStates:
            if LifeStates[tempState] == self.dut.LifeState:
               self.dut.LifeStateName = tempState
               objMsg.printMsg("Drive is in %s (self.dut.LifeStateName) state" %self.dut.LifeStateName)
               break

         if not checkLifeState == "NONE":
            if not self.dut.LifeStateName == checkLifeState:
               objMsg.printMsg("Fail, checking for %s state but current LifeState is %s" %(checkLifeState, self.dut.LifeState))
               ScrCmds.raiseException(14862, "Fail, checking for %s state but current LifeState is %s" %(checkLifeState, self.dut.LifeState))

         if self.dut.LifeState == "FF":
            objPwrCtrl.powerCycle()

   def OpenAdminSession(self, SPMode = 0):

      objMsg.printMsg("Open Admin session")

      if not objRimType.isIoRiser() or SPMode:
         SED_Serial.authenStartSess()
         return

      oProcess = CProcess()

      prm_575_03 = {
        'test_num'        : 575,
        'prm_name'        : 'prm_575_03',
        "TEST_MODE"       : (0x0002,),       ##TestMode         (Prm[0] & 0xff) = Start Session
        "REPORTING_MODE"  : (0x8000,),       ##ReportingMode    (Prm[0] & 0x8000)
        "WHICH_SP"        : (0x0000,),       ##WhichSP          (Prm[1] & 0xff)
        "PASSWORD_TYPE"   : (0x0000,),       ##PasswordType     (Prm[2] & 0xff)
        "DRIVE_STATE"     : (0x0000,),       ##DriveState       (Prm[8] & 0xff)
        "UIDMSWU"         : (0x0000,),       ##UidLswu           Prm[4]
        "UIDMSWL"         : (0x0205,),       ##UidLswu           Prm[5]
        "UIDLSWU"         : (0x0000,),       ##UidLswu           Prm[6]
        "UIDLSWL"         : (0x0001,),       ##UidLswl           Prm[7]
        "CERT_TSTMODE"    : (0x0000,),       ##CertTestMode     (Prm[2] & 0xff)
        "CERT_KEYTYPE"    : (0x0000,),       ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Start Admin session")
      oProcess.St(prm_575_03,timeout=360)

      prm_575_06 = {
        'test_num'        : 575,
        'prm_name'        : 'prm_575_06',
        "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
        "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
        "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
        "PASSWORD_TYPE"   : (0x0001,),     #PasswordType      (Prm[2] & 0xff)   = UNIQUE_MAKERSYMK
        "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
        "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
        "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
        "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
        "UIDLSWL"         : (0x0004,),     ##UidLswl           Prm[7]
        "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
        "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      if self.SSC == 1 and testSwitch.FE_0154366_231166_P_FDE_OPAL_SUPPORT:
         prm_575_06['PASSWORD_TYPE'] = 14

      objMsg.printMsg("Authenticate to MakerSymk")
      oProcess.St(prm_575_06,timeout=360)

      prm_575_04 = {
        'test_num'        : 575,
        'prm_name'        : 'prm_575_04',
        "TEST_MODE"       : (0x0011,),     ##TestMode         (Prm[0] & 0xff)   = Get MSID From Drive
        "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
        "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
        "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)   = DEFAULT MSID
        "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
        "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
        "UIDMSWL"         : (0x0000,),     ##UidLswu           Prm[5]
        "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
        "UIDLSWL"         : (0x0000,),     ##UidLswl           Prm[7]
        "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
        "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Get MSID from Drive")
      oProcess.St(prm_575_04,timeout=360)      

      prm_575_07 = {
        'test_num'        : 575,
        'prm_name'        : 'prm_575_07',
        "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
        "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
        "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
        "PASSWORD_TYPE"   : (0x0002,),     #PasswordType      (Prm[2] & 0xff)   = MSID
        "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
        "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
        "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
        "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
        "UIDLSWL"         : (0x0006,),     ##UidLswl           Prm[7]
        "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
        "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Authenticate to sid")
      oProcess.St(prm_575_07,timeout=360)

      prm_575_psid_from_fis = {
         'test_num'        : 575,
         'prm_name'        : 'prm_575_psid_from_fis',
         'TEST_MODE'       : 0x0024,                  # TestMode         (Prm[0] & 0xff)   = Authenticate
         'REPORTING_MODE'  : 0x8000,                  # ReportingMode    (Prm[0] & 0x8000)
         'WHICH_SP'        : 0x0000,                  # WhichSP          (Prm[1] & 0xff)
         'PASSWORD_TYPE'   : 0x000A,                  # PasswordType     (Prm[2] & 0xff)   = DEFAULT PSID
         'DRIVE_STATE'     : 0x0000,                  # DriveState       (Prm[8] & 0xff)
         'UIDMSWU'         : 0x0000,                  # UidLswu           Prm[4]
         'UIDMSWL'         : 0x0009,                  # UidLswu           Prm[5]
         'UIDLSWU'         : 0x0001,                  # UidLswu           Prm[6]
         'UIDLSWL'         : 0xff01,                  # UidLswl           Prm[7]
         'CERT_TSTMODE'    : 0x0000,                  # CertTestMode     (Prm[2] & 0xff)
         'CERT_KEYTYPE'    : 0x0000,                  # CertKeyType      ((Prm[2] & 0xff00) >> 8)
         }
      objMsg.printMsg('Get PSID from FIS')
      oProcess.St(prm_575_psid_from_fis,timeout=360)

      psid_auth = {
        'test_num'        : 575,
        'prm_name'        : 'psid_auth',
        "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
        "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
        "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
        "PASSWORD_TYPE"   : (0x0009,),     #PasswordType      (Prm[2] & 0xff)   = MSID
        "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
        "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
        "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
        "UIDLSWU"         : (0x0001,),     ##UidLswu           Prm[6]
        "UIDLSWL"         : (0xff01,),     ##UidLswl           Prm[7]
        "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
        "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Authenticate to psid")
      oProcess.St(psid_auth,timeout=360)

   def CloseAdminSession(self, SPMode = 0):
      objMsg.printMsg("Close Admin session")

      if not objRimType.isIoRiser() or SPMode:
         SED_Serial.closeSession()
         return

      oProcess = CProcess()
      prm_575_12 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_12',
           "TEST_MODE"       : (0x0003,),      ##TestMode         (Prm[0] & 0xff)
           "REPORTING_MODE"  : (0x8000,),       ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),       ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0000,),       ##PasswordType     (Prm[2] & 0xff)
           "DRIVE_STATE"     : (0x0000,),       ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0000,),       ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0205,),       ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0000,),       ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0001,),       ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),       ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),       ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
        }
      objMsg.printMsg("Close Admin session")
      oProcess.St(prm_575_12,timeout=360)
###################################################################################################
#                                     UnlockDiagUDE                                               #
#                                                                                                 #
#     This function contains the commands to unlock the DIAG and UDE ports to allow for MFG       #
#     commands to be used while the drive remains in USE state.                                   #
###################################################################################################
   def UnlockDiagUDE(self, internalCall = False, SPMode = 0):
      """
      Unlocks the diagnostic ports in RAM. If internalCall is set True it won't remove the callback handlers.
      """

      if not objRimType.isIoRiser() or SPMode:
         
         objMsg.printMsg("*** UnlockDiagUDE SP Mode")

         SED_Serial.match575SSCParamsToSPTest(coreSp=self.CS,opalSupp=self.SSC, symkKey=self.symkKey, reportOp=self.REPORTING_MODE,custMode=self.custMode,interfaceType='SATA',activateMthd=self.ACTIVATE,tcgType=self.TCG_VERSION)

         try:
            SED_Serial.SSCDriveVerify(binResponse = True)
            self.OpenAdminSession(SPMode)
            if self.dut.nextOper in ['FIN2', 'CUT2', 'FNG2', 'CCV2']:
               SED_Serial.authenSIDSMaker(default = 0, firstRun = 0)  
            else:
               SED_Serial.authenSIDSMaker(default = 0, firstRun = 0, handleFail=1)  #allow new TD_SID
            SED_Serial.lockUnlockDiagPort(lockPort = 0)
            SED_Serial.lockUnlockUDSPort(lockPort = 0) 
            self.CloseAdminSession(SPMode)
         except:
            objMsg.printMsg("*** UnlockDiagUDE SP Mode - retry")
            try:
               self.CloseAdminSession(SPMode)
            except:
               pass
            SED_Serial.SSCDriveVerify(binResponse = True)
            self.OpenAdminSession(SPMode)
            if self.dut.nextOper in ['FIN2', 'CUT2', 'FNG2', 'CCV2']:
               SED_Serial.authenSIDSMaker(default = 0, firstRun = 0)  
            else:
               SED_Serial.authenSIDSMaker(default = 0, firstRun = 0, handleFail=1)  #allow new TD_SID
            SED_Serial.lockUnlockDiagPort(lockPort = 0)
            SED_Serial.lockUnlockUDSPort(lockPort = 0) 
            self.CloseAdminSession(SPMode)    

         return

      try:
        objMsg.printMsg("*** UnlockDiagUDE ")
        oProcess = CProcess()

        prm_575_03 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_03',
           "TEST_MODE"       : (0x0002,),       ##TestMode         (Prm[0] & 0xff) = Start Session
           "REPORTING_MODE"  : (0x8000,),       ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),       ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0000,),       ##PasswordType     (Prm[2] & 0xff)
           "DRIVE_STATE"     : (0x0000,),       ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0000,),       ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0205,),       ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0000,),       ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0001,),       ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),       ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),       ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
        }
        objMsg.printMsg("Start Admin session")
        oProcess.St(prm_575_03,timeout=360)

        prm_575_06 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_06',
           "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
           "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0001,),     #PasswordType      (Prm[2] & 0xff)   = UNIQUE_MAKERSYMK
           "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0004,),     ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
        }
        if self.SSC == 1 and testSwitch.FE_0154366_231166_P_FDE_OPAL_SUPPORT:
           prm_575_06['PASSWORD_TYPE'] = 14

        objMsg.printMsg("Authenticate to MakerSymk")
        oProcess.St(prm_575_06,timeout=360)

        prm_575_04 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_04',
           "TEST_MODE"       : (0x0011,),     ##TestMode         (Prm[0] & 0xff)   = Get MSID From Drive
           "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)   = DEFAULT MSID
           "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0000,),     ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0000,),     ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
        }
        objMsg.printMsg("Get MSID from Drive")
        oProcess.St(prm_575_04,timeout=360)

        prm_575_07 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_07',
           "TEST_MODE"       : (0x0001,),     ##TestMode         (Prm[0] & 0xff)   = Authenticate
           "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0002,),     #PasswordType      (Prm[2] & 0xff)   = MSID
           "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0009,),     ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0006,),     ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
        }
        objMsg.printMsg("Authenticate to sid")
        oProcess.St(prm_575_07,timeout=360)

        #Temporary workaround due to SI behavior
        if not DEBUG:
           objMsg.printMsg("Workaround - running test 575 - Setting REPORTING_MODE")
           prm_575_SetCPCSupport['REPORTING_MODE'] = (0x0001,)
           oProcess.St(prm_575_SetCPCSupport,timeout=360) 

        prm_575_08 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_08',
           "TEST_MODE"       : (0x0013,),     ##TestMode         (Prm[0] & 0xff)   = Unlock FW Port
           "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)
           "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0001,),     ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0002,),     ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0001,),     ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0001,),     ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
        }
        objMsg.printMsg("Unlock Diag port")
        oProcess.St(prm_575_08,timeout=360)

        prm_575_09 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_09',
           "TEST_MODE"       : (0x0005,),     ##TestMode         (Prm[0] & 0xff)
           "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)
           "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0001,),     ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0002,),     ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0001,),     ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0001,),     ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
        }
        objMsg.printMsg("Get Diag unlock table")
        oProcess.St(prm_575_09,timeout=360)

        prm_575_10 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_10',
           "TEST_MODE"       : (0x0013,),     ##TestMode         (Prm[0] & 0xff)
           "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)
           "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0001,),     ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0002,),     ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0001,),     ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0003,),     ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
        }
        objMsg.printMsg("Unlock UDS port")
        oProcess.St(prm_575_10,timeout=360)

        prm_575_11 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_11',
           "TEST_MODE"       : (0x0005,),     ##TestMode         (Prm[0] & 0xff)
           "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0000,),     #PasswordType      (Prm[2] & 0xff)
           "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0001,),     ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0002,),     ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0001,),     ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0003,),     ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
        }
        objMsg.printMsg("Get UDS unlock table")
        oProcess.St(prm_575_11,timeout=360)

        objMsg.printMsg("Get FWDownload status table")
        self.dut.driveattr['DLP_SETTING'] = self.CheckPortStatus('FWDownload')

        #Temporary workaround due to SI behavior
        if not DEBUG:
           objMsg.printMsg("Workaround - running test 575 - Setting REPORTING_MODE")
           prm_575_SetCPCSupport['REPORTING_MODE'] = (0x0000,)
           oProcess.St(prm_575_SetCPCSupport,timeout=360) 
        prm_575_12 = {
           'test_num'        : 575,
           'prm_name'        : 'prm_575_12',
           "TEST_MODE"       : (0x0003,),      ##TestMode         (Prm[0] & 0xff)
           "REPORTING_MODE"  : (0x8000,),       ##ReportingMode    (Prm[0] & 0x8000)
           "WHICH_SP"        : (0x0000,),       ##WhichSP          (Prm[1] & 0xff)
           "PASSWORD_TYPE"   : (0x0000,),       ##PasswordType     (Prm[2] & 0xff)
           "DRIVE_STATE"     : (0x0000,),       ##DriveState       (Prm[8] & 0xff)
           "UIDMSWU"         : (0x0000,),       ##UidLswu           Prm[4]
           "UIDMSWL"         : (0x0205,),       ##UidLswu           Prm[5]
           "UIDLSWU"         : (0x0000,),       ##UidLswu           Prm[6]
           "UIDLSWL"         : (0x0001,),       ##UidLswl           Prm[7]
           "CERT_TSTMODE"    : (0x0000,),       ##CertTestMode     (Prm[2] & 0xff)
           "CERT_KEYTYPE"    : (0x0000,),       ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
        }
        objMsg.printMsg("Close Admin session")
        oProcess.St(prm_575_12,timeout=360)

        objMsg.printMsg("UnlockDiagUDE DONE")
      finally:
         if testSwitch.FE_0146812_231166_P_ALLOW_DL_UNLK_BY_PN_TCG:
            if not internalCall:
               self.RemoveCallback()


###################################################################################################
#                                     CheckPortStatus                                             #
#                                                                                                 #
#     This function contains the commands to check the port status                                #
#     Input: Port = Port Name to be checked                                                       #
#            reqPortStatus = expected staus, such as 'LOCKED', 'UNLOCKED' and ''(Don't care)      #
#     Return: Port Status ('LOCKED' or 'UNLOCKED')                                                #
#     Note  : called SetCPCSupport to set 'REPORTING_MODE' (temporary workaround due to SI bug)   #
###################################################################################################
   def CheckPortStatus(self, Port, reqPortStatus = '' ):

      curPortStatus = 'None'
      objMsg.printMsg("*** CheckPortStatus for %s Port, reqPortStatus = %s" %(Port,reqPortStatus))
      oProcess = CProcess()
      prm_575_GetPortStatusTable["prm_name"] = 'prm_575_Get' + Port + 'PortStatusTable'
      prm_575_GetPortStatusTable["UIDMSWU"] = (UID_Table[Port]>>48) & 0xFFFF
      prm_575_GetPortStatusTable["UIDMSWL"] = (UID_Table[Port]>>32) & 0xFFFF
      prm_575_GetPortStatusTable["UIDLSWU"] = (UID_Table[Port]>>16) & 0xFFFF
      prm_575_GetPortStatusTable["UIDLSWL"] = (UID_Table[Port]) & 0xFFFF

      oProcess.St(prm_575_GetPortStatusTable,timeout=360)

      ret = self.dut.objSeq.SuprsDblObject['P57X_FRAME_DATA']
      if DEBUG:   objMsg.printMsg("ret = %s" % ret)

      import re
      col = re.compile('[\d]')
      data = []

      for row in ret:

         if DEBUG:   objMsg.printMsg("row = %s" % row)
         data1 = []
         data2 = []

         for key in sorted(row.keys()):
            if col.match(key):
               if len(key) == 1:
                  data1.append(row[key])
               else:
                  data2.append(row[key])

         data3 = data1 + data2
         if DEBUG:   objMsg.printMsg("data3 = %s" % data3)
         data.append(data3)

      if DEBUG:   objMsg.printMsg("Extracted data = %s" % data)
      else:       objMsg.printMsg("Extracted data")
      finalData = []
      for row in data:
         objMsg.printMsg("Row = %s" % row)
         finalData = finalData + row

      if DEBUG:   objMsg.printMsg("Consolidated data = %s" % finalData)

      finalData = "".join(finalData)
      if DEBUG:   objMsg.printMsg("Final consolidated data = %s" % finalData)

      if len(re.findall(r"F203\w\wF3",finalData)) > 1:
         ScrCmds.raiseException(14862, "Fail, more than one set of lock/unlock status found")

      for m in re.finditer(r"F203\w\wF3",finalData):
         objMsg.printMsg("%02d-%02d: %s" % (m.start(), m.end(), m.group(0)))
         if finalData[(m.start()+4):(m.start()+6)] == '00':
            curPortStatus = 'UNLOCKED'
         else:
            curPortStatus = 'LOCKED'

      objMsg.printMsg("Current port status: %s" % curPortStatus)

      if not reqPortStatus == '' and not reqPortStatus == curPortStatus:
         ScrCmds.raiseException(14862, "Fail, curPortStatus (%s) not equal to reqPortStatus (%s)" %(curPortStatus,reqPortStatus))

      return curPortStatus



###################################################################################################
#                                     TCGBandsTest                                                #
#                                                                                                 #
#     This function checks whether the the TCG bands related features such as band creation,      #
#     locking and unlocking are working.                                                          #
###################################################################################################

   def TCGBandsTest(self):

      objMsg.printMsg("TCGBandsTest")

      oProcess = CProcess()

      if testSwitch.NSG_TCG_OPAL_PROC:
         objMsg.printMsg("Start Admin session")
         oProcess.St(prm_575_StartAdminSession,timeout=360)

         objMsg.printMsg("Authenticate to MSID")
         oProcess.St(prm_575_AuthMSID,timeout=360)

         objMsg.printMsg("Activate Locking SP before band test")
         oProcess.St(prm_575_ActivateSP,timeout=3600)

         self.CloseAdminSession()

      objMsg.printMsg("Create band 1 - 1000h starting at LBA 0")
      prm_574_01 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_01',
         "WR_FUNCTION"        : (0x00,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "TEST_MODE"          : (0x0002,),   ##TestMode,
         "BANDMASTER"         : (0x0001,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x1000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
      }
      oProcess.St(prm_574_01,timeout=3600)

      objMsg.printMsg("Band 0 locked")
      prm_574_02 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_02',
         "WR_FUNCTION"        : (0x00,),     ##WriteReadFunction, - Configure
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "TEST_MODE"          : (0x0001,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster, - Band 0
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x00ff,),   ##LockingEnables - Locked
      }
      oProcess.St(prm_574_02,timeout=3600)

      objMsg.printMsg("Band 1 unlocked")
      prm_574_03 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_03',
         "WR_FUNCTION"        : (0x00,),     ##WriteReadFunction,       0x00 = configure mode only
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "TEST_MODE"          : (0x0001,),   ##TestMode,                0x0001 = configure band
         "BANDMASTER"         : (0x0001,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),      ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0000,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
      }
      oProcess.St(prm_574_03,timeout=3600)

      objMsg.printMsg("Write 10h blocks to lba 1001 - in band 0 - should fail")
      prm_574_04 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_04',
         "WR_FUNCTION"        : (0x05,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0000,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x1001,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0010,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0004,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x07,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x20,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x02,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_04,timeout=3600)

      objMsg.printMsg("Read 10h blocks to lba 1001 - in band 0 - should fail")
      prm_574_05 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_05',
         "WR_FUNCTION"        : (0x06,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0000,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x1001,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0010,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0004,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x07,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x20,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x02,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_05,timeout=3600)

      objMsg.printMsg("Write 10h blocks to lba 0 - in band 1 - should pass")
      prm_574_06 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_06',
         "WR_FUNCTION"        : (0x05,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0000,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0010,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0000,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x00,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x00,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x00,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_06,timeout=3600)

      objMsg.printMsg("Read 10h blocks from lba 0 - in band 1 - should pass")
      prm_574_07 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_07',
         "WR_FUNCTION"        : (0x06,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0000,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0010,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0000,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x00,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x00,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x00,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_07,timeout=3600)

      objMsg.printMsg("Write read 10h blocks to lba 0 - in band 1 - should pass")
      prm_574_08 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_08',
         "WR_FUNCTION"        : (0x07,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0000,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0010,),   ##transferLength,
         "PATTERN_MSW"        : (0x1234,),   ##PatternHi,
         "PATTERN_LSW"        : (0x4321,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0000,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x00,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x00,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x00,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_08,timeout=3600)


      #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      objMsg.printMsg("Change band 1 - 2000h starting at LBA 0")

      prm_574_09 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_09',
         "WR_FUNCTION"        : (0x00,),     ##WriteReadFunction, 0x00 -> configure mode only
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "TEST_MODE"          : (0x0002,),   ##TestMode,       2 = Create band
         "BANDMASTER"         : (0x0001,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x2000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
      }
      oProcess.St(prm_574_09,timeout=3600)

      objMsg.printMsg("Band 1 locked")
      prm_574_10 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_10',
         "WR_FUNCTION"        : (0x00,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "TEST_MODE"          : (0x0001,),   ##TestMode, 1 = Configure band
         "BANDMASTER"         : (0x0001,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x00ff,),   ##LockingEnables = Lock
      }
      oProcess.St(prm_574_10,timeout=3600)

      objMsg.printMsg("Write read 10h blocks to lba 0 - in band 1 - should fail")
      prm_574_11 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_11',
         "WR_FUNCTION"        : (0x07,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0000,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0010,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0004,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x07,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x20,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x02,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_11,timeout=3600)

      objMsg.printMsg("Write read 10h blocks to lba 2001 - in band 0 - should fail")
      prm_574_12 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_12',
         "WR_FUNCTION"        : (0x07,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0000,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x2001,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0010,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0004,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x07,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x20,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x02,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_12,timeout=3600)

      objMsg.printMsg("Band 1 unlocked")
      prm_574_13 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_13',
         "WR_FUNCTION"        : (0x00,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "TEST_MODE"          : (0x0001,),   ##TestMode, 1 = Configure band
         "BANDMASTER"         : (0x0001,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables = unlock
      }
      oProcess.St(prm_574_13,timeout=3600)

      objMsg.printMsg("Write read 10h blocks to lba 0 - in band 1 - should pass")
      prm_574_14 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_14',
         "WR_FUNCTION"        : (0x07,),     ##WriteReadFunction,  #YHN: use 7 to be consistent with the above
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0000,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0010,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0000,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x00,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x00,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x00,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_14,timeout=3600)

      objMsg.printMsg("Write 10h blocks to lba 0 - in band 1 @ lba 0x1ffa to cross into band 0 - should fail")
      prm_574_16 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_16',
         "WR_FUNCTION"        : (0x07,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0000,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x1ffa,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0010,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0004,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x05,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x24,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x00,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_16,timeout=3600)


      #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      objMsg.printMsg("Crypto erase of band 1")
      prm_574_17 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_17',
         "WR_FUNCTION"        : (0x00,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0001,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0008,),   ##TestMode,  8 = Erase band
         "BANDMASTER"         : (0x0001,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0000,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0000,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x00,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x00,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x00,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_17,timeout=3600)

      objMsg.printMsg("Read 10h blocks to lba 0 - in band 1 - should pass")
      prm_574_18 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_18',
         "WR_FUNCTION"        : (0x02,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0000,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0010,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0000,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x00,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x00,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x00,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_18,timeout=3600)

      #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      objMsg.printMsg("Remove band 1 - 0h starting at LBA 0")
      prm_574_21 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_21',
         "WR_FUNCTION"        : (0x00,),     ##WriteReadFunction, 0x00 -> configure mode only
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "TEST_MODE"          : (0x0002,),   ##TestMode,       2 = Create band
         "BANDMASTER"         : (0x0001,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
      }
      oProcess.St(prm_574_21,timeout=3600)

      objMsg.printMsg("Band 0 unlocked")
      prm_574_22 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_22',
         "WR_FUNCTION"        : (0x00,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "TEST_MODE"          : (0x0001,),   ##TestMode, 1 = Configure band
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables = unlock
      }
      oProcess.St(prm_574_22,timeout=3600)

      objMsg.printMsg("Read 10h blocks to lba 0 - in band 0 - should pass")
      prm_574_18 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_18',
         "WR_FUNCTION"        : (0x02,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,- Band 0
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0000,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x0000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0010,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0000,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x00,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x00,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x00,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_18,timeout=3600)

      objMsg.printMsg("Read 10h blocks to lba 3000 - in band 0 - should pass")
      prm_574_23 = {
         'test_num'           : 574,
         'prm_name'           : 'prm_574_23',
         "WR_FUNCTION"        : (0x02,),     ##WriteReadFunction,
         "REPORTING_MODE"     : (0x8000,),   ##ReportingMode,
         "CLEAR_SESSION"      : (0x0000,),   ##ClearSession,
         "DIAG_MODE"          : (0x0000,),   ##DiagMode,
         "TEST_MODE"          : (0x0000,),   ##TestMode,
         "BANDMASTER"         : (0x0000,),   ##WhichBandMaster,
         "START_LBA_H"        : (0x0000,),   ##StartLBAHi,
         "START_LBA_L"        : (0x3000,),   ##StartLBALo,
         "BAND_SIZE_H"        : (0x0000,),   ##BandSizeHi,
         "BAND_SIZE_L"        : (0x0000,),   ##BandSizeLo,
         "LOCK_ENABLES"       : (0x0000,),   ##LockingEnables
         "TRANSFER_LENGTH"    : (0x0010,),   ##transferLength,
         "PATTERN_MSW"        : (0x0000,),   ##PatternHi,
         "PATTERN_LSW"        : (0x0000,),   ##PatternLo,
         "STATUS_MISCOM_EXP"  : (0x0000,),   ##ReportingMode,
         "EXP_SENSE_BYTE2"    : (0x00,),     ##ExpectedSenseByte2,
         "EXP_SENSE_BYTE12"   : (0x00,),     ##ExpectedSenseByte12,
         "EXP_SENSE_BYTE13"   : (0x00,),     ##ExpectedSenseByte13
      }
      oProcess.St(prm_574_23,timeout=3600)

      objMsg.printMsg("*** TCGBandsTest END ***")


###################################################################################################
#                                     ResetSOMState                                               #
#                                                                                                 #
#     This function contains the commands to reset the drive to SOM0 state                        #
###################################################################################################
   def GetSOMState(self):
      oProcess = CProcess()
      GetSOM0 = {
         'test_num'        : 575,
         'prm_name'        : 'prm_575_15',
         "TEST_MODE"       : (0x001B,),     ##TestMode         (Prm[0] & 0xff)
         "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
         "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
         "PASSWORD_TYPE"   : (0x0002,),     #PasswordType      (Prm[2] & 0xff)
         "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
         "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
         "UIDMSWL"         : (0x0000,),     ##UidLswu           Prm[5]
         "UIDLSWU"         : (0x0007,),     ##UidLswu           Prm[6]
         "UIDLSWL"         : (0x0001,),     ##UidLswl           Prm[7]
         "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
         "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
      }
      objMsg.printMsg("Get drive SOM State")
      SetFailSafe()
      try:
         if not objRimType.isIoRiser():
            SED_Serial.getStateTable()
         else:
            oProcess.St(GetSOM0,timeout=360)
      except:
         pass
      ClearFailSafe()

   def ResetSOMState(self):

      objMsg.printMsg("*** ResetSOMState ")

      if not testSwitch.NSG_TCG_OPAL_PROC:
         self.dut.TCGComplete = True

         objPwrCtrl.powerCycle()
         oProcess = CProcess()
         self.OpenAdminSession()

         SetSOM0 = {
            'test_num'        : 575,
            'prm_name'        : 'prm_575_15',
            "TEST_MODE"       : (0x001E,),     ##TestMode         (Prm[0] & 0xff)
            "REPORTING_MODE"  : (0x8000,),     ##ReportingMode    (Prm[0] & 0x8000)
            "WHICH_SP"        : (0x0000,),     ##WhichSP          (Prm[1] & 0xff)
            "PASSWORD_TYPE"   : (0x0002,),     #PasswordType      (Prm[2] & 0xff)
            "DRIVE_STATE"     : (0x0000,),     ##DriveState       (Prm[8] & 0xff)
            "UIDMSWU"         : (0x0000,),     ##UidLswu           Prm[4]
            "UIDMSWL"         : (0x0006,),     ##UidLswu           Prm[5]
            "UIDLSWU"         : (0x0000,),     ##UidLswu           Prm[6]
            "UIDLSWL"         : (0x0011,),     ##UidLswl           Prm[7]
            "CERT_TSTMODE"    : (0x0000,),     ##CertTestMode     (Prm[2] & 0xff)
            "CERT_KEYTYPE"    : (0x0000,),     ##CertKeyType      ((Prm[2] & 0xff00) >> 8)
         }
         objMsg.printMsg("Reset drive to SOM0")
         oProcess.St(SetSOM0,timeout=360)

         objMsg.printMsg("ResetSOMState DONE")

         if testSwitch.BF_0138112_231166_P_RESET_SOM_STATE_IN_ENDTEST:
            self.dut.TCG_locked = True

      else:
         oProcess = CProcess()
         objMsg.printMsg("Start Admin session")
         oProcess.St(prm_575_StartAdminSession,timeout=360)

         #gy
         objMsg.printMsg("Authenticate to PSID")
         oProcess.St(prm_575_AuthPSID,timeout=360)

         objMsg.printMsg("Reset drive to SOM0 (RevertSP) ")
         oProcess.St(prm_575_RevertSP,timeout=360)

         objMsg.printMsg("ResetSOMState DONE")

###################################################################################################
#                                    EncryptionBlkChk                                             #
#                                                                                                 #
#     This function check that the encryption block is working                                    #
###################################################################################################
   def EncryptionBlkChk(self):

      objMsg.printMsg("*** EncryptionBlkChk")
      oProcess = CProcess()
      from IntfClass import CIdentifyDevice
      import random
      result = OK

      # Get max LBA
      oIdentifyDevice = CIdentifyDevice()
      ret = oIdentifyDevice.ID                     # read device settings with identify device
      maxLBA = ret['IDDefaultLBAs'] - 1            # default for 28-bit LBA
      if ret['IDCommandSet5'] & 0x400:             # check bit 10
         maxLBA = ret['IDDefault48bitLBAs'] - 1

      self.ChangeLifeState("MFG")

      if testSwitch.PROC_TCG_SIMPLIFIED_EBC:
         totalRep = 1      #No. of different data pattern (loop) to verify with
         totalSec = 2      #No. of sectors tested
      else:
         totalRep = 5      #No. of different data pattern (loop) to verify with
         totalSec = 5      #No. of sectors tested

      if result == OK:
         for repStep in range(totalRep):
            # 1. Write a known ?pattern? to a set of randomly ?selected sectors?.
            #    - ?Pattern? is a single byte value repeated 512 times and is randomly selected from 0x00 to 0xFF
            #    - ?Selected sectors? contain the first LBA, the last LBA and some LBAs in between
            randsctr = hex(random.randint(0x01,0xfe))[2:] # Get a random no. from range including both end points

            if not testSwitch.PROC_TCG_SIMPLIFIED_EBC:
               if repStep == totalRep-1: randsctr = '00'
               elif repStep == totalRep-2: randsctr = 'ff'

            objMsg.printMsg("***** Sanity Test loop %d - data pattern = %s *****"%(repStep+1,randsctr))
            maxLBA = maxLBA - 1

            if not testSwitch.PROC_TCG_SIMPLIFIED_EBC:
               LBA1 = 0
               LBA2 = random.randint(0x00,maxLBA/3)
               LBA3 = random.randint(maxLBA/3,(maxLBA/3)*2)
               LBA4 = random.randint((maxLBA/3)*2,maxLBA)
               LBA5 = maxLBA
               LBA_dict = { "Sector 1" : LBA1,
                            "Sector 2" : LBA2,
                            "Sector 3" : LBA3,
                            "Sector 4" : LBA4,
                            "Sector 5" : LBA5,}

            else:
               LBA1 = 0
               LBA2 = random.randint((maxLBA/3)*2,maxLBA)
               LBA_dict = { "Sector 1" : LBA1,
                            "Sector 2" : LBA2,}

            ICmd.ClearBinBuff(3) # Clear both write and read buffer
            ICmd.FillBuffByte(1,randsctr,0,512) # Fill write buffer with 512 bytes of pattern starting at offset 0
            objMsg.printMsg("Fill Buffer")
            if DEBUG:
               objMsg.printMsg("***** randsctr = %s" % randsctr)
               objMsg.printMsg("***** Initial WrBuff = %s" % ICmd.GetBuffer(1,0,512))
            # 2. Read back the ?selected sectors? to verify that the data is the same as what was written
            #    - On success, we confidently conclude that the encryption is either turned off or encryption is
            #      turned on and working correctly
            if result == OK:
               for loop in range(totalSec):     
                  sctr = 'Sector %d' % (loop+1)
                  startLBA = LBA_dict[sctr]
                  ICmd.ClearBinBuff(2) # Clear read buffer
                  data = ICmd.SequentialWRDMA(startLBA, startLBA+1, 1, 1, 0, 1)
                  result = data['LLRET']
                  objMsg.printMsg("Sanity Test - %s LBA = 0x%X"%(sctr,startLBA))
                  if result == OK:
                     objMsg.printMsg("Sanity Test - %s Write/Read DMA pass"%sctr)
                  else:
                     objMsg.printMsg("Sanity Test - %s Write/Read DMA fail data = %s" % (sctr,str(data)))
                     break
                  if DEBUG: objMsg.printMsg("***** Before Key Change, %s - RdBuff = %s" % (sctr,ICmd.GetBuffer(2,0,512)))
            # 3. Force a change of encryption key
            # Transit from MFG to Setup and from SETUP to MFG, this will generate a new encryption key.
            if result == OK:
               self.ChangeLifeState("SETUP")
               self.ChangeLifeState("MFG")
            # 4. Read back ?selected sectors? to verify the following
            #    i. Data in all sectors is different from the ?pattern?
            #       - Confirms that encryption is indeed turned on and that the key had been changed as expected
            if result == OK:
               ICmd.FillBuffByte(1,randsctr,0,512) # Fill write buffer with 512 bytes of pattern starting at offset 0
               ICmd.FillBuffByte(2,randsctr,0,512) # Fill read buffer with 512 bytes of pattern starting at offset 0
               for loop in range(totalSec):     
                  sctr = 'Sector %d' % (loop+1)
                  startLBA = LBA_dict[sctr]
                  try: 
                     data = ICmd.SequentialReadDMA(startLBA, startLBA+1, 1, 1, 0, 1)
                     result = data['LLRET']
                  except:
                     result = NOT_OK
                     objMsg.printMsg("Sanity Test - data change which is expected")
                  
                  if result != OK: # Data different meaning encryption is working
                     objMsg.printMsg("Sanity Test - %s SequentialReadDMA Pass (i.e. data changed)"%sctr)
                     result = OK
                  else:
                     objMsg.printMsg("Sanity Test - %s SequentialReadDMA fail data = %s" % (sctr,str(data)))
                     result = 1
                     break
                  if DEBUG: objMsg.printMsg("***** After Key Change, %s - RdBuff (LBA=0x%X) = %s" % (sctr,startLBA,ICmd.GetBuffer(2,0,512)))
            #    ii. Data in each sectors is unique (different)
            #        - This is a salting like behavior
            if result == OK:
               for i in range(1,(totalSec+1)):
                  ICmd.ClearBinBuff(3) # Clear both write and read buffer
                  sctr1 = 'Sector %d' % (i)
                  startLBA1 = LBA_dict[sctr1]
                  data = ICmd.SequentialReadDMA(startLBA1, startLBA1+1, 1, 1, 0, 0) # Read back and put into Read Buffer, don't cmp
                  result = data['LLRET']
                  if result == OK:
                     ICmd.BufferCopy(1,0,2,0,512) # Copy to write buff (offset 0) from read buff (offset 0), total 512 bytes
                     for j in range(i+1,(totalSec+1)):      
                        sctr2 = 'Sector %d' % (j)
                        startLBA2 = LBA_dict[sctr2]
                        ICmd.ClearBinBuff(2) # Clear read buffer
                        try:
                           data = ICmd.SequentialReadDMA(startLBA2, startLBA2+1, 1, 1, 0, 1)
                           result = data['LLRET']
                        except:
                           result = NOT_OK
                           objMsg.printMsg("Sanity Test - miscompare which is expected")
                        
                        if DEBUG:
                           objMsg.printMsg("Sanity Test - Comparing Sector %d with Sector %d data = %s" % (i,j,str(data)))
                           objMsg.printMsg("***** %s - LBA=0x%X = %s" % (sctr1,startLBA1,ICmd.GetBuffer(1,0,512)))
                           objMsg.printMsg("***** %s - LBA=0x%X = %s" % (sctr2,startLBA2,ICmd.GetBuffer(2,0,512)))
                        if result != OK:
                           objMsg.printMsg("Sanity Test - Comparing Sector %d with Sector %d Pass (i.e. each sector data is different)"%(i,j))
                           result = OK
                        else:
                           objMsg.printMsg("Sanity Test - Comparing Sector %d with Sector %d fail data = %s" % (i,j,str(data)))
                           objMsg.printMsg("***** %s - LBA=0x%X = %s" % (sctr1,startLBA1,ICmd.GetBuffer(1,0,512)))
                           objMsg.printMsg("***** %s - LBA=0x%X = %s" % (sctr2,startLBA2,ICmd.GetBuffer(2,0,512)))
                           result = 1
                           break
                  else:
                     objMsg.printMsg("Sanity Test - Fail to read Sector %d"%i)
                  if result != OK: break
            #    iii. Every 16-bytes data block within a sector is unique (different)
            #         - This is a CBC like behavior (as opposed to ECB)
            if result == OK:
               objMsg.printMsg("Sanity Test - Comparing every 16 bytes in each sector.........")
               for i in range(1,(totalSec+1)):
                  ICmd.ClearBinBuff(3) # Clear both write and read buffer
                  sctr = 'Sector %d' % (i)
                  objMsg.printMsg("%s" %sctr)
                  startLBA = LBA_dict[sctr]
                  data = ICmd.SequentialReadDMA(startLBA, startLBA+1, 1, 1, 0, 0) # Read back and put into Read Buffer, don't cmp
                  result = data['LLRET']

                  if result == OK:
                  #---------------------------------------------------------------------------------------------------------------
                  # Workaround on CPC bug ICmd.BufferCopy(8,0,2,0,512)
                  # CPC unable to access ImgBuffer on Select Flag 0X08
                  #---------------------------------------------------------------------------------------------------------------
                     ReadBuffer = ICmd.GetBuffer(RBF,0,512)
                     SectorData = str(ReadBuffer['DATA'])              # Get 512 bytes from Read Buffer

                     n = 0
                     for j in xrange(0,512,16):
                        n += 1
                        d1 = SectorData[j:n*16]
                        for k in xrange(n,32):                          # Compare 16 byte to the rest of the data and so on

                           d2 = SectorData[k*16:(k+1)*16]
                           if d1 == d2:
                              msg = "Sanity Test - %s, 16-bytes compare bytes %i:%i vs %i:%i fail data = %s." \
                                       %(sctr,j,n*16,n*16,(n+1)*16, `d1`)
                              objMsg.printMsg(msg)
                              ScrCmds.raiseException(14862, "Sanity Test Fail Before TCGPrep")
                           else:
                              if DEBUG: objMsg.printMsg("Comparing %s bytes %i:%i with %s bytes %i:%i. Pass" \
                                               %(sctr,j,n*16,sctr,k*16,(k+1)*16))

            # 5. As in Step #1, write the same ?pattern? to the ?selected sectors? and read back to verify that the data is
            #    the same as that written
            #    - Up to this point, we are quite confident that the encryption block is working correctly
            if result == OK:
               ICmd.ClearBinBuff(3) # Clear both write and read buffer
               ICmd.FillBuffByte(1,randsctr,0,512) # Fill write buffer with 512 bytes of pattern starting at offset 0
               if DEBUG:
                  objMsg.printMsg("***** Rep step#1, randsctr = %s" % randsctr)
                  objMsg.printMsg("***** Rep step#1, WrBuff = %s" % ICmd.GetBuffer(1,0,512))
               for loop in range(totalSec):           
                  sctr = 'Sector %d' % (loop+1)
                  startLBA = LBA_dict[sctr]
                  ICmd.ClearBinBuff(2) # Clear read buffer
                  data = ICmd.SequentialWRDMA(startLBA, startLBA+1, 1, 1, 0, 1)
                  result = data['LLRET']
                  if result == OK:
                     objMsg.printMsg("Sanity Test - Rep step#1, %s Write/Read DMA pass"%sctr)
                  else:
                     objMsg.printMsg("Sanity Test - Rep step#1, %s Write/Read DMA fail data = %s" % (sctr,str(data)))
                     break
                  if DEBUG: objMsg.printMsg("***** Rep step#1, %s - RdBuff = %s" % (sctr,ICmd.GetBuffer(2,0,512)))
            if result != OK: break

      if testSwitch.virtualRun: result = OK
      if result: ScrCmds.raiseException(14862, "EncryptionBlkChk Fail Before TCGPrep")
      else:
         self.ChangeLifeState("SETUP")
         objMsg.printMsg("*** EncryptionBlkChk - Passed")


###################################################################################################
#                                    UnifiedF3                                                    #
#                                                                                                 #
#     This function will toggle the following                                                     #
#     1. FIPS bit                                                                                 #
#     2. Drive model number                                                                       #
###################################################################################################
   def UnifiedF3(self):

      objMsg.printMsg("*** UnifiedF3")
      oProcess = CProcess()

      pn = self.dut.partNum[0:6]
      objMsg.printMsg("UnifiedF3 - PartNum: %s" % (pn))
      pn = "%x"%ord(pn[0]) + "%x"%ord(pn[1]) + "%x"%ord(pn[2]) + "%x"%ord(pn[3]) + "%x"%ord(pn[4]) + "%x"%ord(pn[5])
      objMsg.printMsg("UnifiedF3 - PartNum: %s" % (pn))

      self.ChangeLifeState("MFG")

      objMsg.printMsg("UnifiedF3 - Send the Unlock Diagnostics cmd - write")
      ICmd.ClearBinBuff(3) # Clear both write and read buffer
      res = ICmd.PutBuffByte(WBF, '0100010008000000FFFF01009A324F03', 0)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14862, "Filling buffer for Smart Write Cmd failed.")
      if DEBUG:
         objMsg.printMsg("DEBUG WrBuff = %s" % ICmd.GetBuffer(WBF,0,512))
         objMsg.printMsg("DEBUG RdBuff = %s" % ICmd.GetBuffer(RBF,0,512))

      try:
         oProcess.St(writeSmartLogPage_538)
      except:
         objMsg.printMsg('WriteSmartLog rerun!')
         ICmd.HardReset()
         oProcess.St(writeSmartLogPage_538)

      objMsg.printMsg("UnifiedF3 - Send the Enable FIPS mode cmd")
      ICmd.ClearBinBuff(3) # Clear both write and read buffer

      writebuffer = '010001000A00000094010100' + pn
      objMsg.printMsg("UnifiedF3 - Write buffer : %s" %writebuffer)

      res = ICmd.PutBuffByte(WBF, writebuffer, 0)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(14862, "Filling buffer for Smart Write Cmd failed.")
      if DEBUG:
         objMsg.printMsg("DEBUG WrBuff = %s" % ICmd.GetBuffer(WBF,0,512))
         objMsg.printMsg("DEBUG RdBuff = %s" % ICmd.GetBuffer(RBF,0,512))

      try:
         oProcess.St(writeSmartLogPage_538)
      except:
         objMsg.printMsg('WriteSmartLog rerun!')
         ICmd.HardReset()
         oProcess.St(writeSmartLogPage_538)

      self.ChangeLifeState("SETUP")
      objMsg.printMsg("*** UnifiedF3 - Done")

###################################################################################################
#                                    RNGBlkChkSmart                                               #
#                                                                                                 #
#     This function check that the RNG block from SMART is working                                #
###################################################################################################
   def RNGBlkChkSmart(self):

      objMsg.printMsg("*** RNG Block Checking using SMART")

      numChallenge = getattr(TP,"prm_TCG",{}).get('numChallenge', 152)
      lenRandomNum = getattr(TP,"prm_TCG",{}).get('lenRandomNum', 16)
      ReadData = ''
      sList = ''

      from IntfClass import CInterface
      oIntf = CInterface()
      self.ChangeLifeState("MFG")

      for n in range(numChallenge):

         objMsg.printMsg("***** RNGBlkChk Test loop %d *****"%(n))

         if n < 2:
            objPwrCtrl.powerCycle()
            ICmd.ClearBinBuff(3) # Clear both write and read buffer
            res = ICmd.PutBuffByte(WBF, '04000200', 0)
            if res['LLRET'] != OK:
               ScrCmds.raiseException(14862, "Filling buffer for Smart Write Cmd failed.")
            if DEBUG:
               objMsg.printMsg("DEBUG WrBuff = %s" % ICmd.GetBuffer(WBF,0,512))
               objMsg.printMsg("DEBUG RdBuff = %s" % ICmd.GetBuffer(RBF,0,512))

         oIntf.WriteOrReadSmartLog(0x24, 'write')  #write to log 24
         oIntf.WriteOrReadSmartLog(0x24, 'read')   #read smart log

         ReadBuffer = ICmd.GetBuffer(RBF,0,lenRandomNum)
         objMsg.printMsg("After read, ReadBuffer = %s" % ReadBuffer)

         sList1 = ''
         for n in range(len(ReadBuffer['DATA'])):
            ibyte = ord(ReadBuffer['DATA'][n])
            sValue = '%02X' % (ibyte)
            sList1 = sList1 + sValue
            if DEBUG: objMsg.printMsg("n = %s sValue = %s" % (n,sValue))

         sList = sList + sList1

         if DEBUG: objMsg.printMsg("sList1 = %s" % sList1)
         if DEBUG: objMsg.printMsg("sList = %s" % sList)
         if DEBUG: objMsg.printMsg("After read, len(sList) = %s" % len(sList))

      j = 0
      k = 0
      l = 0
      objMsg.printMsg("Checking whether the data is random")
      while j < numChallenge:
        sChallenge1 = sList[j*lenRandomNum*2:j*lenRandomNum*2 + lenRandomNum*2]
        objMsg.printMsg("Loop %d sChallenge1 %s" % (j,sChallenge1))
        k = j + 1
        l = 0
        while l < (numChallenge - 1) - j:
          sChallenge2 = sList[k*lenRandomNum*2:k*lenRandomNum*2 + lenRandomNum*2]
          if DEBUG: objMsg.printMsg("sChallenge2 %s loop %d" % (sChallenge2, k))
          if sChallenge1 == sChallenge2:
            objMsg.printMsg("Fail, non random data from RNG")
            ScrCmds.raiseException(14862, "Fail, non random data from RNG")

          k += 1
          l += 1
        j += 1

      j = 0
      while j < numChallenge:
         sChallenge1 = sList[j*lenRandomNum*2:j*lenRandomNum*2 + lenRandomNum*2]
         if j < 2:
            sType = 'ENTR'
         else:
            sType = 'FIPS'
         self.dut.dblData.Tables('P_ENC_CHALLENGE_LOG').addRecord({
                           'ROW_NUM': j,
                           'CHALLENGE_TYPE': sType,
                           'CHALLENGE_RANDOM_DATA': sChallenge1,
                           'CHALLENGE_BITS': 'NA',

                           })
         j += 1

      objMsg.printDblogBin(self.dut.dblData.Tables('P_ENC_CHALLENGE_LOG'))
      self.ChangeLifeState("SETUP")

###################################################################################################
#                                    RNGBlkChkSPIO                                                #
#                                                                                                 #
#     This function check that the RNG block is working                                           #
###################################################################################################
   def RNGBlkChkSPIO(self):

      objMsg.printMsg("*** SPIO RNG Block Check")

      numChallenge = getattr(TP,"prm_TCG",{}).get('numChallenge', 152)
      lenRandomNum = 32
      sList = ''    

      for n in range(numChallenge):

         objMsg.printMsg("***** RNGBlkChk Test loop %d *****"%(n))

         if n < 2:
            objPwrCtrl.powerCycle( useESlip=1 ) 
            self.OpenAdminSession()
         
         sList1 = binascii.hexlify(SED_Serial.getRandomNumber())
         if DEBUG: objMsg.printMsg("After read, sList1 = %s" % sList1)
         
         sList = sList + sList1 

         if DEBUG: objMsg.printMsg("sList1 = %s" % sList1)
         if DEBUG: objMsg.printMsg("sList = %s" % sList)
         if DEBUG: objMsg.printMsg("After read, len(sList) = %s" % len(sList))

      j = 0
      k = 0
      l = 0
      objMsg.printMsg("Checking whether the data is random")
      while j < numChallenge:
        sChallenge1 = sList[j*lenRandomNum*2:j*lenRandomNum*2 + lenRandomNum*2]
        objMsg.printMsg("Loop %d sChallenge1 %s" % (j,sChallenge1))
        k = j + 1
        l = 0
        while l < (numChallenge - 1) - j:
          sChallenge2 = sList[k*lenRandomNum*2:k*lenRandomNum*2 + lenRandomNum*2]
          if DEBUG: objMsg.printMsg("sChallenge2 %s loop %d" % (sChallenge2, k))
          if sChallenge1 == sChallenge2:
            objMsg.printMsg("Fail, non random data from RNG")
            ScrCmds.raiseException(14862, "Fail, non random data from RNG")

          k += 1
          l += 1
        j += 1

      j = 0
      while j < numChallenge:
         sChallenge1 = sList[j*lenRandomNum*2:j*lenRandomNum*2 + lenRandomNum*2]
         if j < 2:
            sType = 'ENTR'
         else:
            sType = 'FIPS'
         self.dut.dblData.Tables('P_ENC_CHALLENGE_LOG').addRecord({
                           'ROW_NUM': j,
                           'CHALLENGE_TYPE': sType,
                           'CHALLENGE_RANDOM_DATA': sChallenge1,
                           'CHALLENGE_BITS': 'NA',

                           })
         j += 1

      objMsg.printDblogBin(self.dut.dblData.Tables('P_ENC_CHALLENGE_LOG'))
      self.CloseAdminSession()
      objMsg.printMsg("*** SPIO RNG Block Check - Done")


###################################################################################################
#                                    RNGBlkChkT575                                                #
#                                                                                                 #
#     This function check that the RNG block from T575 is working                                 #
###################################################################################################
   def RNGBlkChkT575(self):

      objMsg.printMsg("*** RNG Block Check using T575")

      # Variable to store array of random numbers
      RNs = []
      global RNs

      numChallenge = getattr(TP,"prm_TCG",{}).get('numChallenge', 152)
      numRnEntr = 2
      prm_575_GenerateRandom32byteStrings = {
         'test_num'        : 575,
         'prm_name'        : 'prm_575_GenerateRandom32byteStrings',
         "TEST_MODE"       : (0x0028,),
         "REPORTING_MODE"  : (0x0000,),
         "LOOP_COUNT"      : (numChallenge,),
      }

      oProcess = CProcess()
      # Getting the first two sets of random numbers
      prm_575_GenerateRandom32byteStrings["LOOP_COUNT"] = (0x0001,)
      for x in range(0, numRnEntr):
         objPwrCtrl.powerCycle()
         objMsg.printMsg("Start Admin session")
         oProcess.St(prm_575_StartAdminSession, timeout = 30)
         oProcess.St(prm_575_GenerateRandom32byteStrings, timeout = 30)

      # Getting the the rest of random numbers
      prm_575_GenerateRandom32byteStrings["LOOP_COUNT"] = (numChallenge - numRnEntr,)
      oProcess.St(prm_575_GenerateRandom32byteStrings, timeout = 120)

      self.CloseAdminSession()

      #objMsg.printMsg("Close Admin session")
      #oProcess.St(prm_575_CloseAdminSession, timeout = 30)

      # Checking for randomness
      if numChallenge != len(RNs):
         errMsg = "Total collected RNs (%s) is not equal numChallenge (%s)" % (len(RNs), numChallenge)
         if testSwitch.virtualRun:
            del RNs
            return
         ScrCmds.raiseException(14862, errMsg)
      objMsg.printMsg("Checking whether the data is random")
      for x in range(numChallenge):
         for y in range(x + 1, numChallenge):
            if RNs[x] == RNs[y]:
               objMsg.printMsg("Random numbers %s and %s are the same" % (x, y))
               ScrCmds.raiseException(14862, "Fail, non random data from RNG")

      # Updating parametric table
      for x in range(0, numRnEntr):
         self.dut.dblData.Tables('P_ENC_CHALLENGE_LOG').addRecord({
            'ROW_NUM': x,
            'CHALLENGE_TYPE': 'ENTR',
            'CHALLENGE_RANDOM_DATA': RNs[x],
            'CHALLENGE_BITS': 'NA',
         })
      for x in range(numRnEntr, numChallenge):
         self.dut.dblData.Tables('P_ENC_CHALLENGE_LOG').addRecord({
            'ROW_NUM': x,
            'CHALLENGE_TYPE': 'FIPS',
            'CHALLENGE_RANDOM_DATA': RNs[x],
            'CHALLENGE_BITS': 'NA',
         })
      objMsg.printDblogBin(self.dut.dblData.Tables('P_ENC_CHALLENGE_LOG'))

      del RNs
      objMsg.printMsg("*** RNG Block Check using T575 - Done")

###################################################################################################
#                               ChangeLifeState                                                   #
#                                                                                                 #
#     This function change the life state of the drive                                            #
###################################################################################################
   def ChangeLifeState(self, LifeStateName):

      objMsg.printMsg("ChangeLifeState to %s" %LifeStateName)
      LifeState = 'NONE'

      for tempState in LifeStates:
         if tempState == LifeStateName:
            LifeState = LifeStates[tempState]
            objMsg.printMsg("LifeState = %s" %LifeState)   # Life State in hex (ASCII) form
            break

      if LifeState == 'NONE':
         ScrCmds.raiseException(14862, "No such LifeState: %s to be set" %LifeStateName)
      else:
         tempLifeState = string.atoi(LifeState,16)
         objMsg.printMsg("tempLifeState = %d" %tempLifeState)

      prm_575_SetState["DRIVE_STATE"] = tempLifeState

      oProcess = CProcess()
      objMsg.printMsg("Start Admin session")
      oProcess.St(prm_575_StartAdminSession,timeout=360)
      objMsg.printMsg("Authenticate to PSID using default PSID")
      oProcess.St(prm_575_AuthDefaultPSID,timeout=360)
      objMsg.printMsg("Authenticate to MakerSymK AES256 Def PSID")
      oProcess.St(prm_575_AuthMakerSymK_AES256_DefPSID,timeout=360)

      objMsg.printMsg("Set drive state to %s State" %LifeState)
      oProcess.St(prm_575_SetState,timeout=360)

      self.CloseAdminSession()

      if not testSwitch.virtualRun:
         self.CheckFDEState(LifeStateName)

###################################################################################################
#                                     InitTrustedTCG                                              #
#                                                                                                 #
#     This function checks whether the TCG drive is in SETUP state, if not it will reset to       #
#     SETUP state using Test 577                                                                  #
###################################################################################################
   def InitTrustedTCG(self):

      objMsg.printMsg("InitTrustedTCG")

      if not ConfigVars[CN].get('PRODUCTION_MODE',0) and testSwitch.FE_0246029_385431_SED_DEBUG_MODE:
         objMsg.printMsg("FE_0246029_385431_SED_DEBUG_MODE on, skip")
         return                        

      oProcess = CProcess()
      try:

         self.CheckFDEState()

         if self.dut.nextOper == "FNG2":
            if not self.dut.LifeStateName == "USE":
               objMsg.printMsg("Error, LifeStateName :%s for TCG FDE drive in FNG2" %self.dut.LifeStateName)
               ScrCmds.raiseException(14862, "Error, Drive is not in USE state for TCG FDE drive in FNG2")
            else:
               objMsg.printMsg("Ok, LifeStateName :%s for TCG FDE drive in FNG2, no need reset" %self.dut.LifeStateName)
               self.dut.objData.update({'TCGPrepDone': 1})
               objPwrCtrl.powerCycle()
               return

         # PLR support
         if self.dut.objData.retrieve('TCGPrepDone') == 1:
            objMsg.printMsg("TCGPrepDone = 1, return")
            return

         if self.dut.LifeState == "00":
            objMsg.printMsg("Drive is already in SETUP state - OK")
            if testSwitch.FE_0146812_231166_P_ALLOW_DL_UNLK_BY_PN_TCG:
               self.dut.driveattr['TD_SID']='NONE'
               DriveAttributes['TD_SID']='NONE'
               self.dut.driveattr['FDE_DRIVE'] = 'NONE'
               if testSwitch.BF_0157429_231166_P_FIX_LOCKED_SED_DRV_INIT:
                  return
         else:
            if self.dut.LifeState == "01":
               objMsg.printMsg("Drive is in DIAG state.")
            elif self.dut.LifeState == "80":
               if testSwitch.FE_0143087_357552_BYPASS_SETUP_JUST_UNLOCK:
                  objMsg.printMsg("Drive is in USE state.")
               else:
                  objMsg.printMsg("Drive is in USE state.  Reset to SETUP state")
            elif self.dut.LifeState == "81":
               #For NSG, testSwitch.FE_0143087_357552_BYPASS_SETUP_JUST_UNLOCK = 0
               if testSwitch.FE_0143087_357552_BYPASS_SETUP_JUST_UNLOCK:
                  objMsg.printMsg("Drive is in MFG state.")
               else:
                  objMsg.printMsg("Drive is in MFG state.  Reset to SETUP state.")
                  try:
                     if not self.dut.driveattr['FDE_DRIVE'] == 'FDE': #meaning drive set to MFG before personalization started
                        if not objRimType.isIoRiser():
                           objMsg.printMsg("Change the drive to SETUP state")
                           self.changeSEDState(00,default=1,firstRun=1)
                        else:
                           self.ChangeLifeState("SETUP")

                        self.CheckFDEState("SETUP")
                        return
                  except:
                     try:
                        objMsg.printMsg("Change drive to SETUP state failed, redownload codes.")
                        if not objRimType.isIoRiser():
                           theCell.enableESlip(sendESLIPCmd = True)
                           objPwrCtrl.changeBaud(PROCESS_HDA_BAUD)
                           self.dut.sptActive.setMode(self.dut.sptActive.availModes.mctBase,determineCodeType = True)
                           if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
                              from Serial_Download import CDnldCode
                           else:
                              from base_SerialTest import CDnldCode
                           oDnldCode = CDnldCode(self.dut,{'CODES':getattr(TP, 'TCG_DNLD_SEQ', ['TGTB','OVLB','IV', 'TGT','OVL','CXM']),})
                        else:
                           from base_IntfTest import CDnlduCode
                           oDnldCode = CDnlduCode(self.dut,{'CODES':getattr(TP, 'TCG_DNLD_SEQ', ['TGTB','OVLB','IV', 'TGT','OVL','CXM']),})

                        oDnldCode.run()
                        self.CheckFDEState("SETUP")
                        return
                     except:
                        objMsg.printMsg("Reset drive to SETUP state using change state failed, will try T577 for reset.")
                        if not objRimType.isIoRiser():
                           objPwrCtrl.powerCycle( useESlip=1 ) 
                        else:
                           objPwrCtrl.powerCycle()
            else:
               objMsg.printMsg("Drive is in INVALID state.  Abort unlock- Drive needs IV.")
               if testSwitch.BF_0157429_231166_P_FIX_LOCKED_SED_DRV_INIT:
                  self.dut.driveattr['TD_SID']='NONE'
                  DriveAttributes['TD_SID']='NONE'
                  self.dut.driveattr['FDE_DRIVE'] = 'NONE'
               else:
                  objPwrCtrl.powerCycle()
               return

            if testSwitch.FE_0143087_357552_BYPASS_SETUP_JUST_UNLOCK:
               if self.params.has_key('bypassSedSetup') and self.params['bypassSedSetup'] == True \
                        and self.dut.LifeState in ["80","81"]:
                  #Just unlock ports (if necessary) and return
                  objMsg.printMsg("Bypassing SED Setup")
                  if self.dut.LifeState == "80":
                     self.UnlockDiagUDE()
                  self.dut.objData.update({'TCGPrepDone': 1})
                  return

            if not objRimType.isIoRiser():
               objMsg.printMsg("Change the drive state")
               SED_Serial.changeToSetupState()
            else:
               objMsg.printMsg("Running test 577 - Reset Drive State to Setup - FIS's PSID")
               prm_577_RESET = {
                  'test_num'        : 577,
                  'prm_name'        : 'prm_577_RESET',
                  "TEST_MODE"       : (0x0008,),   # Reset Drive State to Setup
                  "REPORTING_MODE"  : (0x8000,),
                  "MSID_TYPE"       : (0x0001,),   # FIS's PSID
                  "DRIVE_STATE"     : (0x0000,),   # Setup
                  "FW_PLATFORM"     : (0x0010,),
                  "CERT_KEYTYPE"    : (0x0000,),
               }
               if testSwitch.FE_0141467_231166_P_SAS_FDE_SUPPORT:
                  for retry in xrange(3):
                     try:
                        oProcess.St(prm_577_RESET,timeout=3600)
                        break
                     except:
                        pass
                  else:
                     raise
               else:
                  oProcess.St(prm_577_RESET,timeout=3600)

            self.CheckFDEState()
            if not self.dut.LifeState == "00":
               objMsg.printMsg("After reset, LifeState :%s which is not SETUP state" %self.dut.LifeState)
               if not testSwitch.virtualRun:
                  ScrCmds.raiseException(14862, "After reset, LifeState is not SETUP state")

            self.dut.resetFDEAttributes()

            if self.dut.nextOper == "CRT2":
               objMsg.printMsg("CRT2 operation, skip code download")
               return

            objMsg.printMsg("Need to re-download Codes here")

            if not testSwitch.BF_0149206_231166_P_SET_LOR_AND_UNLOCK_DL_PORT:
               try:

                  if not objRimType.isIoRiser():
                     theCell.enableESlip(sendESLIPCmd = True)
                     objPwrCtrl.changeBaud(PROCESS_HDA_BAUD)
                     self.dut.sptActive.setMode(self.dut.sptActive.availModes.mctBase,determineCodeType = True)
                     if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
                        from Serial_Download import CDnldCode
                     else:
                        from base_SerialTest import CDnldCode
                     oDnldCode = CDnldCode(self.dut,{'CODES':getattr(TP, 'TCG_DNLD_SEQ', ['TGTB','OVLB','IV', 'TGT','OVL','CXM']),})
                  else:
                     from base_IntfTest import CDnlduCode
                     oDnldCode = CDnlduCode(self.dut,{'CODES':getattr(TP, 'TCG_DNLD_SEQ', ['TGTB','OVLB','IV', 'TGT','OVL','CXM']),})

                  oDnldCode.run()

                  objMsg.printMsg("Need to reset SMART here")
                  from base_IntfTest import CClearSMART
                  oClearSmart = CClearSMART(self.dut)
                  oClearSmart.run()

                  if objRimType.isIoRiser():
                     self.CheckFDEState()

                  ICmd.HardReset()
               except CRaiseException, e_inst:
                  if testSwitch.FE_0146821_231166_P_ALLOW_FDE_UNLK_SKIP_MISS_CODES:
                     if e_inst.args[0][2] != 10326: #catch missing file
                        raise
                  else:
                     raise
      finally:
          if testSwitch.FE_0146812_231166_P_ALLOW_DL_UNLK_BY_PN_TCG:
            self.RemoveCallback()

   def getSecurityOrFDEType(self, typeStr, defaultResult):
      # get the result out of test parameters
      result = self.prm_TCG.get(typeStr, defaultResult)

      # override with drive config attribute if exists
      driveConfigAttr = self.dut.driveConfigAttrs.get(typeStr, None)
      if driveConfigAttr:
         result = driveConfigAttr[1]

      return str(result).rstrip()

   def changeSEDState(self,newState,default=0,firstRun=0):  
      if not objRimType.isIoRiser():
         self.OpenAdminSession()
         SED_Serial.authenSIDSMaker(default = default, firstRun = firstRun)   #SED_Serial.authenSIDSMaker(default = 1, firstRun = 1) for drive that have not personalized.
         SED_Serial.changeStates(newState)
         self.CloseAdminSession()

   def finalSEDPrep(self):

      if not objRimType.isIoRiser():

         Y2backup = self.dut.SkipY2
         self.dut.SkipY2 = True
         SED_Serial.securityConfigVerification(CORE_SPEC=self.CS,CUSTOMER_OPTION=self.custMode,OPAL_SSC_SUPPORT=self.SSC,\
                                               SYMK_KEY_TYPE=self.symkKey,REPORTING_MODE=self.REPORTING_MODE,TCG_VERSION=self.TCG_VERSION,ACTIVATE=self.ACTIVATE)
         self.dut.SkipY2 = Y2backup

         if testSwitch.virtualRun: return
         self.CheckFDEState()
         if not self.dut.LifeState == "80":
            objMsg.printMsg("Wrong, after personalization, LifeState :%s" %self.dut.LifeState)
            ScrCmds.raiseException(14862, "After personalization, LifeState is not correct")
      else: 
         #577 - Verification of credentials - Change to USE state - FIS's PSID
         prm_577_30 = {
            'test_num'        : 577,
            'prm_name'        : 'prm_577_30',
            "TEST_MODE"       : (0x0006,),   # Verify Personalization and Set Drive State
            "REPORTING_MODE"  : (0x8000,),
            "MSID_TYPE"       : (0x0001,),   # FIS's PSID
            "DRIVE_STATE"     : (0x0080,),
            "FW_PLATFORM"     : (0x0010,),
            "CERT_KEYTYPE"    : (0x0000,),
         }
         if SEDprm_AutoDetect:
            prm_577_30["TEST_MODE"] = (0x0026,)

         if testSwitch.FE_0225282_231166_P_TCG2_SUPPORT:
            prm_577_30["CUSTOMER_OPTION"]     = self.CUSTOMER_OPTION

         if testSwitch.IS_SDnD:
            prm_577_30.update(SDnD_T577_SetUSEState_Updates)

         objMsg.printMsg("Running test 577 - Verification of credentials - Change to USE state - FIS's PSID")
         oProcess = CProcess()
         oProcess.St(prm_577_30,timeout=3600)

         self.CheckFDEState()
         if not self.dut.LifeState == "80":
            if not testSwitch.virtualRun:
               objMsg.printMsg("Wrong, after personalization, LifeState :%s" %self.dut.LifeState)
               ScrCmds.raiseException(14862, "After personalization, LifeState is not correct")

   def InterfaceSCSA(self):
      prm_575_FDE_SCSA_Process = {'test_num'        : 575,
                                  'prm_name'        : 'prm_575_FDE_SCSA_Process',
                                  'timeout'         : 300,
                                   "TEST_MODE"      : 0x004B,
                                   "REPORTING_MODE" : 0x0001,
                                  }

      self.oProcess.St(prm_575_FDE_SCSA_Process)
   
