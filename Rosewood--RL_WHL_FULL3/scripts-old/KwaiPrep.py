#########################################################################
#
# $RCSfile: KwaiPrep.py,v $
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $Revision: #1 $
# $Date: 2016/05/05 $
# $Author: chiliang.woo $
#
#
##########################################################################

from Constants import *
import base64, random, os, time
import ScrCmds
import MessageHandler as objMsg
from TestParamExtractor import TP
import serialScreen, sptCmds
from PowerControl import objPwrCtrl
from Rim import objRimType

from ICmdFactory import ICmd

VENDOR_UNIQUE_PIO_WRITE  = -5
VENDOR_UNIQUE_PIO_READ   =  5

SET_XFER_MODE =  3
DEFAULT_PIO   =  0
ULTRA_DMA     =  0x45
WRITE_BUF     =  1
READ_BUF      =  2

OK            =  0            # Good Status
FAIL          = -1            # used to indicate function failed
TRUE          =  1
FALSE         =  0

TD_STATE_INITIALIZATION = 0x81    # This state allows re-run of the drive without having to 'unlock'
TD_STATE_OPERATIONAL    = 0x80    # This 'locks' the drive

#============================================================================================


ISSUE_USER_CARD         = 0x01    # Issuance card type for generic card
ISSUE_FDE_CARD          = 0x02    # Issuance card type for FDE card

RETURN_FCP              = 0x00    # used in file selection - Return FCP
DONT_RETURN_FCP         = 0x0C    # used in file selection - Don't Return FCP

APDU_PACKET_SECTOR_SIZE = 512     # this could change
CLAINS_LENGTH           = 2       # used to validate input to function

PROTOCOL_ID             = 0xF0    # Protocol ID for Trusted Send/Receive Commands (01 or F1 for Future products)

NEXT_RECORD_MODE        = 0x02    # P2 mode setting for Next Record mode in Update Record cmd
PREV_RECORD_MODE        = 0x03    # P2 mode setting for Previous Record mode in Update Record cmd
ABS_CURR_RECORD_MODE    = 0x04    # P2 mode setting for Absolute/Current Record mode in Update Record cmd

CCC_OrgNum              = [0x00, 0x01] # Prepends to Card Num for Card ID in EF_CCC
CCC_CardIDOffset        = 0x09    # Offset of Card Number in the EF_CCC file

ValidKeyPairListLen     = 132     # Key pair data for the drive keystore pool should be 132 (64 + 64 + 4) bytes

Manf3DESKeyOffset       = 4       # Offset past External TLV info to Manufacturing 3DES Key
InternalManf3DESKeyLen  = 16      # Number of pad bytes required to overwrite the Manf 3DES key in the file

#======================== Smart Card slots during installation ==============================
ADMIN    = 0   # Admin Card                   mandatory (card number = x0000)
CSP      = 1   # Cryptographic services Card  optional  (card number = x0001)
TEMPLATE = 2   # Template Card                mandatory (card number = xFFFE)
FEATURES = 3   # Drive Features Card          optional  (card number = x0003)
FDE      = 4   # Full Disc Encryption Card    optional  (card number = x0002; FDE template card = xFFFD)
USBFDE   = 5   # USB FDE Card                 optional  (card number = 5; Template: FFFA)
KEYTABLE = 255 # Public Key Table Card        mandatory
#============================================================================================

UnexpectedStatus = '*** U N E X P E C T E D  S T A T U S ***, Results: %s'
ErrStr = '*** E R R O R ***'
GoodStatus = '\x90\x00'
DATA  = 'DATA'
LLRET = 'LLRET'

PadData = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
# The 'default' SPE Key as a list - for use in UpdateBinary
SERIAL_ENABLE_3DES = [0x6D,0xC1,0x5E,0x4F,0x38,0x79,0x98,0xBF,0xF7,0x6B,0xE9,0x58,0x79,0x75,0xC8,0x07]
# The 'default' SPE Key as a string - for use in Unlocking the Serial Port
SERIAL_ENABLE_3DES_KEY   = '\x6D\xC1\x5E\x4F\x38\x79\x98\xBF\xF7\x6B\xE9\x58\x79\x75\xC8\x07'

DEFAULT_PIN = ['1','2','3','4','5','6','7','8','9','0','1','2','3','4','5','6','7','8','9','0',\
               '1','2','3','4','5','6','7','8','9','0','1','2','3','4','5']

# =================================================================================
# Identify the CLAINS (Class/Instructions) - Extracted from sc_clain.h in clamshell
# =================================================================================

RECOVERYERASEPREPARE      = 0xF0C8     # Seagate Proprietary
RECOVERYERASE             = 0xF0CA     # Seagate Proprietary
UPDATEBINARYDEVICEFILE    = 0xF0CE     # Seagate Proprietary
CHAINKEYPUT               = 0xF0D0     # Seagate Proprietary
ISSUECONFIRM              = 0xF0D2     # Seagate Proprietary
ISSUEEXTERNALAUTHENTICATE = 0xF0D4     # Seagate Proprietary
ISSUEGETCHALLENGE         = 0xF0D6     # Seagate Proprietary
ISSUEGETSIGNATURE         = 0xF0D8     # Seagate Proprietary
ISSUEGETSIGNATURECONTINUE = 0xF0DA     # Seagate Proprietary

GENERATESYMMETRICKEY      = 0xF0DC     # Seagate Proprietary
WARMRESET                 = 0xF0DE     # Seagate Proprietary
CLEARCARD                 = 0xF0E0     # Seagate Proprietary
ISSUECARD                 = 0xF0E2     # Seagate Proprietary
SYNCHRONIZE               = 0xF0E8     # Seagate Proprietary
SYNCHRONIZEALL            = 0xF0EA     #
TOGGLEDIRECTCARDWRITES    = 0xF0FA     # Seagate Proprietary

DIRECTCARDREAD            = 0xF0F4     # Seagate Proprietary
DIRECTCARDWRITE           = 0xF0F6     # Seagate Proprietary
INITSEACOS                = 0xF0F8     # Seagate Proprietary
ERASEALL                  = 0xF0EC     # Seagate Proprietary

EXTERNALAUTHENTICATE      = 0x0082     # GSC_IS Version 2.1
GETCHALLENGE              = 0x0084     # GSC_IS Version 2.1
INTERNALAUTHENTICATE      = 0x0088     # GSC_IS Version 2.1
MANAGESECURITYENV         = 0x0022     # GSC_IS Version 2.1
PERFORMSECURITYOP         = 0x002A     # GSC_IS Version 2.1
READBINARY                = 0x00B0     # GSC_IS Version 2.1
SELECTFILE                = 0x00A4     # GSC_IS Version 2.1
UPDATEBINARY              = 0x00D6     # GSC_IS Version 2.1
VERIFYPIN                 = 0x0020     # GSC_IS Version 2.1

FETCH                     = 0x8012     # ETSI TS 102 221
INCREASE                  = 0x8032     # ETSI TS 102 221
STATUS                    = 0x00F2     # ETSI TS 102 221
TERMINALRESPONSE          = 0x8014     # ETSI TS 102 221
CREATEFILE                = 0x00E0     # ETSI TS 102 222
TERMINATECARDUSAGE        = 0x00FE     # ETSI TS 102 222

CHANGEPIN                 = 0x0024     # ISO 7816-4
ENVELOPE                  = 0x00C2     # ISO 7816-4
READBINARYBERTLV          = 0x00B1     # ISO 7816-4
UPDATEBINARYBERTLV        = 0x00D7     # ISO 7816-4
READRECORD                = 0x00B2     # ISO 7816-4
UPDATERECORD              = 0x00DC     # ISO 7816-4
SEARCHBINARY              = 0x00A0     # ISO 7816-4
UNBLOCKPIN                = 0x002C     # ISO 7816-4
DEACTIVATE                = 0x0004     # ISO 7816-4
ACTIVATE                  = 0x0044     # ISO 7816-4

GENERATEASYMMETRICKEYPAIR = 0x0046     # ISO 7816-8

PEEK                      = 0xF0FC     # Debugging
NOP                       = 0xF0FE     # Debugging

# =================================================================================
# Establish the File definitions
# =================================================================================

MASTER_FILE              = 0x3F00

EF_DIR                   = 0x2F00
EF_ATR                   = 0x2F01
EF_ARR                   = 0x2F06
EF_USER                  = 0x2FDE
EF_ICCID                 = 0x2FE2

EF_PRKDF                 = 0x4401
EF_PUKDF                 = 0x4402
EF_SKDF                  = 0x4403
EF_AODF                  = 0x4404
EF_CDF                   = 0x4405

DF_CDE                   = 0x4944
EF_RSA1                  = 0x4945
EF_RSA2                  = 0x4946
EF_CERT1                 = 0x4947
EF_CERT1_TAMP            = 0x4948
EF_CERT2                 = 0x4949
EF_CERT2_TAMP            = 0x494A
EF_3DES                  = 0x494B
EF_CARDOWNER             = EF_CERT2_TAMP
EF_SID                   = 0x494C
EF_HOST_TO_DISK2         = 0x494F

DF_CIA                   = 0x5015
EF_CARDINFO              = 0x5032
EF_ODF                   = 0x5031

EF_PUBLICKEYS_TABLE      = 0x8F01
EF_CARD_STATUS           = 0x8F02
EF_LOG                   = 0x8F03
EF_REMAPPED_BOOT_SECTORS = 0x8F04

EF_CCC                   = 0xDB00

SLASH_DEV                = 0xFF00
EF_DIRECTCARDACCESS      = 0xFF01
EF_CLOCKS                = 0xFF02
EF_ENTROPY_SRC           = 0xFF03
EF_PRECALC_KEYS          = 0xFF04
EF_TD_STATE              = 0xFF05
EF_LBA_REMAPPING         = EF_TD_STATE
EF_DIAGLOCKS             = 0xFF06
EF_LBA_REMAPPING_BYPASS  = EF_DIAGLOCKS
EF_LOCK_ON_STARTUP       = 0xFF09
EF_CARD_CONTROL          = 0xFF0C

# =================================================================================
# Establish a Cross Reference dictionary to aid in displaying filenames for debug
# =================================================================================

FilenameXRef = {
MASTER_FILE:'MASTER_FILE',
SLASH_DEV:'SLASH_DEV',
EF_TD_STATE:'EF_TD_STATE',
DF_CDE:'DF_CDE',
EF_3DES:'EF_3DES',
EF_USER:'EF_USER',
EF_ARR:'EF_ARR',
EF_DIR:'EF_DIR',
EF_ATR:'EF_ATR',
EF_ICCID:'EF_ICCID',
EF_CCC:'EF_CCC',
EF_PUBLICKEYS_TABLE:'EF_PUBLICKEYS_TABLE',
EF_CARD_STATUS:'EF_CARD_STATUS',
EF_LOG:'EF_LOG',
DF_CIA:'DF_CIA',
EF_CARDINFO:'EF_CARDINFO',
EF_DIRECTCARDACCESS: 'EF_DIRECTCARDACCESS',
EF_ODF:'EF_ODF',
EF_PRKDF:'EF_PRKDF',
EF_PUKDF:'EF_PUKDF',
EF_SKDF:'EF_SKDF',
EF_AODF:'EF_AODF',
EF_CDF:'EF_CDF',
EF_DIAGLOCKS:'EF_DIAGLOCKS',
EF_CLOCKS:'EF_CLOCKS',
EF_ENTROPY_SRC :'EF_ENTROPY_SRC',
EF_PRECALC_KEYS:'EF_PRECALC_KEYS',
EF_RSA1:'EF_RSA1',
EF_RSA2:'EF_RSA2',
EF_CERT1:'EF_CERT1',
EF_CERT1_TAMP:'EF_CERT1_TAMP',
EF_CERT2:'EF_CERT2',
EF_CERT2_TAMP:'EF_CERT2_TAMP',
EF_SID:'EF_SID',
EF_HOST_TO_DISK2:'EF_HOST_TO_DISK2',
EF_CARD_CONTROL:'EF_CARD_CONTROL',
EF_REMAPPED_BOOT_SECTORS: 'EF_REMAPPED_BOOT_SECTORS',
EF_LBA_REMAPPING: 'EF_LBA_REMAPPING',
EF_LOCK_ON_STARTUP: 'EF_LOCK_ON_START',
EF_CARDOWNER: 'EF_CARDOWNER'
}

CardnameXref = {
'Admin':    'Admin Card',                    # Mandatory - Slot 0    card number 0
'CSC':      'CSP Card',                      # Optional  - Slot 1    card number 1
'Template': 'Template Card',                 # Mandatory - Slot 2    card number FFFE
'Features': 'Drive Features Card',           # Optional  - Slot 3    card number 3
'FDE':      'FDE Card',                      # Optional  - Slot 4    card number 2/5 (when Issued) -Template card number FFFD/FFFA
'Keytable': 'Public Key Table'               # Mandatory - Slot 255  card number ?
}

# =================================================================================
# Establish debug constants used in the process
# =================================================================================

DEBUG_VERIFY_WRT_BUF               = FALSE
DEBUG_VERIFY_DATA                  = FALSE
DEBUG_BYTECOUNT_0                  = FALSE
DEBUG_PASSTHROUGH_BYTECOUNT        = FALSE
DEBUG_REPORT_EXEC_TRUST_SEND       = FALSE
DEBUG_REPORT_SENDING_UPDATE_BINARY = FALSE
DEBUG_STEP_TRACE                   = TRUE
DEBUG_PROCESS                      = FALSE
DEBUG_VIEW_KEYPAIR_DATA            = FALSE
DEBUG_GENERATE_KEY_DATA            = FALSE
DEBUG_DISPLAY_FILE_SELECTION       = FALSE
DEBUG_DISPLAY_UPDATE_BINARY_DATA   = FALSE
DEBUG_DISPLAY_CARD_LOAD_APDU       = FALSE
DEBUG_DISPLAY_APDU                 = FALSE
DEBUG_DISPLAY_RSA1_TLV_DATA        = FALSE
DEBUG_DISPLAY_NONCE_INFO           = FALSE


class CKwaiPrepTest:
   def __init__(self, dut):
      self.dut = dut
      self.KwaiVars = {}
      found = 0

      pnPtrn = [self.dut.partNum,                                   # 9HV123-456
                self.dut.partNum[:4] + "%-" + self.dut.partNum[7:], # 9HV1%-456
                self.dut.partNum[:3] + "%-" + self.dut.partNum[7:], # 9HV%-456
                self.dut.partNum[:6] + "-%",                        # 9HV123-%
                self.dut.partNum[:4] + "%-%",                       # 9HV1%-%
                self.dut.partNum[:3],                               # 9HV
               ]
      for pn in pnPtrn:
         if TP.pnList.has_key(pn):
            objMsg.printMsg('Selected Part Number = %s' % pn)
            self.KwaiVars.update(TP.pnList[pn])
            found = 1
            break

      # If cannot find then fail it
      if not found:
         ScrCmds.raiseException(12754, "Unable to get KwaiPrep settings")
      else:
         objMsg.printMsg('KwaiVars = %s'%self.KwaiVars)
         if hasattr(TP, 'FDEMatrix'):
            self.dut.driveattr['FDE_TYPE'] = self.FDEType(self.KwaiVars, TP.FDEMatrix)
         else:
            objMsg.printMsg("Unable to find FDEMatrix table in TestParameters.py.")
            self.dut.driveattr['FDE_TYPE'] = 'NONE'

      #============================================================================================
      # The following flags determine how the script will personalize the file system.            #
      # The first 7 are controlled from the Kwai-specific ConfigVars, the remaining 5 are not     #
      # normally used in a production environment (see comments below for production settings).   #
      #============================================================================================
      if self.KwaiVars['DefaultData'] == 'TRUE':
         self.DefaultData   = TRUE           # TRUE: uses default (fixed) values for Keys,Certificates,SID, and Serial Port Enable Key (I.E. E* drive)
      else:
         self.DefaultData   = FALSE          # FALSE: will get unique values for Keys,Certificates,SID, and Serial Port Enable Key (I.E. M2TD,CODY,etc)

      if self.KwaiVars['IssueFDECard'] == 'TRUE' and not self.DefaultData:       # If M2TD or CODY
         self.IssueFDECard  = TRUE           # TRUE:  causes the FDE card to be issued
      else:
         self.IssueFDECard  = FALSE          # FALSE: Will not issue the FDE card

      if self.KwaiVars.get('PreBoot','FALSE') == 'TRUE' and self.IssueFDECard:
         self.PREBOOT       = TRUE           # TRUE: Sets up the FDE card to re-map LBA's and installs image
      else:
         self.PREBOOT       = FALSE          # FALSE: No LBA re-mapping is done

      if self.KwaiVars.get('XF_Sectors','FALSE') == 'TRUE' and self.IssueFDECard:
         self.XF_SECTORS    = TRUE           # TRUE: FDE card XF space specified in sectors (I.E. M2TD)
      else:
         self.XF_SECTORS    = FALSE          # FALSE: FDE card XF space specified in bytes (I.E. CODY)

      if self.KwaiVars.get('USB_FDE','FALSE') == 'TRUE' and self.PREBOOT and self.IssueFDECard:
         self.USB_FDE_CARD  = TRUE           # TRUE: this is a USB version of the FDE card
      else:
         self.USB_FDE_CARD  = FALSE          # FALSE: not a USB FDE card

      if self.KwaiVars.get('ATA_Mode','FALSE') == 'TRUE':
         self.ATA_Mode      = TRUE           # TRUE: This is an ATA Mode drive
      else:
         self.ATA_Mode      = FALSE          # FALSE: Not an ATA Mode drive.

      if self.KwaiVars.get('LockOnStartBit','FALSE') == 'TRUE':
         self.LockOnStartBit  = TRUE           # TRUE: Set LockOnStartBit for BlackArmour drives
      else:
         self.LockOnStartBit  = FALSE          # FALSE: Do not set LockOnStartBit for BlackArmour drives

      self.SidLength  = 25                   # Sid is always 25 chars for platform drives

      # Admin Card Over-write data:
      self.SERIAL_OVERWRITE      = [0x30,0x42,0x30,0x1E,0x0C,0x05,0x33,0x44,0x45,0x53,0x32,0x03,0x02,0x07,0x80,0x30,0x11,\
                                     0x30,0x06,0x03,0x02,0x05,0x20,0x05,0x00,0x30,0x07,0x03,0x02,0x06,0x40,0x04,0x01,0x9E,\
                                     0x30,0x0A,0x04,0x00,0x03,0x02,0x01,0xE2,0x02,0x02,0x00,0x9E,0xA0,0x06,0x30,0x04,0x02,\
                                     0x02,0x00,0x80,0xA1,0x0C,0x30,0x0A,0x30,0x08,0x04,0x06,0x3F,0x00,0x49,0x44,0x49,0x4B]

      # CSP Card Over-write data:
      if testSwitch.Kwai_CSPCard_Enabled or not testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
         self.EF_SKDF_OverwriteData = [0x30,0x42,0x30,0x1E,0x0C,0x16,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,\
                                       0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0x03,0x02,0xFF,0xFF,0x30,0x00,\
                                       0x30,0x0A,0x04,0x00,0x03,0x02,0xFF,0xFF,0x02,0x02,0xFF,0xFF,0xA0,0x06,0x30,0x04,0x02,\
                                       0x02,0xFF,0xFF,0xA1,0x0C,0x30,0x0A,0x30,0x08,0x04,0x06,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

      # Drive Features Card Over-write data:
      self.EF_SKDF_Card3OverData = [0x30,0x40,0x30,0x1C,0x0C,0x14,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,\
                                     0xFF,0xFF,0xFF,0xFF,0x03,0x02,0xFF,0xFF,0x30,0x00,0x30,0x0A,0x04,0x00,0x03,0x02,0xFF,0xFF,0x02,0x02,0xFF,0xFF,\
                                     0xA0,0x06,0x30,0x04,0x02,0x02,0xFF,0xFF,0xA1,0x0C,0x30,0x0A,0x30,0x08,0x04,0x06,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

      self.TRUSTED_SEND_CMD     = 0x5E    # (5F: CODY DMA) Seagate Proprietary - used to send APDU data
      self.TRUSTED_RECEIVE_CMD  = 0x5C    # (5D: CODY DMA) Seagate Proprietary - used to receive APDU data

      #============================================================================================
      if self.KwaiVars['ENTROPY_ON'] == 'TRUE': # Entropy ON/OFF flag - TRUE for Production. (FALSE for TEST/DEBUG)
         self.ENTROPY_ON   = TRUE
      else:
         self.ENTROPY_ON   = FALSE

      if self.KwaiVars['ENABLE_SP'] == 'TRUE':  # FALSE for production - If TRUE, then leave serial port enabled - (TRUE for DEBUG/TEST!)
         self.ENABLE_SP   = TRUE
      else:
         self.ENABLE_SP   = FALSE

      if self.KwaiVars['STATE'] == 'OPERATIONAL': # This needs to be 'OPERATIONAL' for production - ('INIT' for DEBUG/TEST!)
         self.STATE   = TD_STATE_OPERATIONAL
      else:
         self.STATE   = TD_STATE_INITIALIZATION

      if self.KwaiVars['USE_EXISTING_SID'] == 'TRUE': # FALSE for Production - if TRUE, then use the existing SID (retrieved from FIS) - for Re-Processing!
         self.USE_EXISTING_SID   = TRUE
      else:
         self.USE_EXISTING_SID   = FALSE

      if self.KwaiVars['SBS'] == 'TRUE': # TRUE if SBS USB_FDE;  FALSE if ERD USB_FDE (External Reference Design) only has effect if USB_FDE_CARD is TRUE !!!
         self.SBS   = TRUE
      else:
         self.SBS   = FALSE

      if self.KwaiVars['REMOTE_ISSUANCE'] == 'TRUE': # TRUE if StepNexus; else FALSE
         self.REMOTE_ISSUANCE   = TRUE
      else:
         self.REMOTE_ISSUANCE   = FALSE

      if self.KwaiVars['WRITE_USER_IMAGE'] == 'TRUE':
         self.WRITE_USER_IMAGE   = TRUE
      else:
         self.WRITE_USER_IMAGE   = FALSE

      if self.KwaiVars['Random_PIN'] == 'TRUE':
         self.Random_PIN   = TRUE
      else:
         self.Random_PIN   = FALSE

      if self.KwaiVars['Check_Encryption'] == 'TRUE':  # This is now selectable
         self.Check_Encryption = TRUE
      else:
         self.Check_Encryption = FALSE

   #  ========================================================================================
   #  Check that the encryption block is working
   #  ========================================================================================
   def EncryptionBlkChk(self):
      from IntfClass import CIdentifyDevice
      import random
      DEBUG = 0
      oIdentifyDevice = CIdentifyDevice()
      # Get max LBA
      ret = oIdentifyDevice.ID                     # read device settings with identify device
      maxLBA = ret['IDDefaultLBAs'] - 1            # default for 28-bit LBA
      if ret['IDCommandSet5'] & 0x400:             # check bit 10
         maxLBA = ret['IDDefault48bitLBAs'] - 1
      data = ICmd.SetFeatures(0x03, 0x45)
      result = data['LLRET']
      if result == OK:
         objMsg.printMsg("Sanity Test - SetFeatures pass")
      else:
         objMsg.printMsg("Sanity Test - SetFeatures fail data = %s" % str(data))
      if result == OK:
         totalRep = 5 # No. of different data pattern to verify with
         for repStep in range(totalRep):
            # 1. Write a known ?pattern? to a set of randomly ?selected sectors?.
            #    - ?Pattern? is a single byte value repeated 512 times and is randomly selected from 0x00 to 0xFF
            #    - ?Selected sectors? contain the first LBA, the last LBA and some LBAs in between
            randsctr = hex(random.randint(0x01,0xfe))[2:] # Get a random no. from range including both end points
            if repStep == totalRep-1:
               randsctr = '00'
            elif repStep == totalRep-2:
               randsctr = 'ff'
            objMsg.printMsg("***** Sanity Test loop %d - data pattern = %s *****"%(repStep+1,randsctr))
            maxLBA = maxLBA - 1
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
               for loop in range(5):
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
                  if DEBUG:
                     objMsg.printMsg("***** Before Erase, %s - RdBuff = %s" % (sctr,ICmd.GetBuffer(2,0,512)))
            # 3. Force a change of encryption key (e.g by enhance erase)
            if result == OK: # Security Set Password
               data = ICmd.SecuritySetPassword(0x00,'00000000000000000000000000000001',0x00,0x00) # Cmp user pw, pw = 0x01, Security lvl = high, Master pw = NA
               result = data['LLRET']
               if result == OK:
                  objMsg.printMsg("Sanity Test - SecuritySetPassword pass")
               else:
                  objMsg.printMsg("Sanity Test - SecuritySetPassword fail data = %s" % str(data))
            if result == OK: # Security Erase Prepare
               data = ICmd.SecurityErasePrepare()
               result = data['LLRET']
               if result == OK:
                  objMsg.printMsg("Sanity Test - SecurityErasePrepare pass")
               else:
                  objMsg.printMsg("Sanity Test - SecurityErasePrepare fail data = %s" % str(data))
            if result == OK: # Security Erase Unit
               data = ICmd.SecurityEraseUnit(0x00,'00000000000000000000000000000001',0x01) # Cmp user pw, pw = 0x01, Enhanced erase
               result = data['LLRET']
               if result == OK:
                  objMsg.printMsg("Sanity Test - SecurityEraseUnit pass")
               else:
                  objMsg.printMsg("Sanity Test - SecurityEraseUnit fail data = %s" % str(data))
            # 4. Read back ?selected sectors? to verify the following
            #    i. Data in all sectors is different from the ?pattern?
            #       - Confirms that encryption is indeed turned on and that the key had been changed as expected
            if result == OK:
               ICmd.FillBuffByte(1,randsctr,0,512) # Fill write buffer with 512 bytes of pattern starting at offset 0
               ICmd.FillBuffByte(2,randsctr,0,512) # Fill read buffer with 512 bytes of pattern starting at offset 0
               for loop in range(5):
                  sctr = 'Sector %d' % (loop+1)
                  startLBA = LBA_dict[sctr]
                  data = ICmd.SequentialReadDMA(startLBA, startLBA+1, 1, 1, 0, 1)
                  result = data['LLRET']
                  if result != OK: # Data different meaning encryption is working
                     objMsg.printMsg("Sanity Test - %s SequentialReadDMA Pass (i.e. data changed)"%sctr)
                     result = OK
                  else:
                     objMsg.printMsg("Sanity Test - %s SequentialReadDMA fail data = %s" % (sctr,str(data)))
                     result = 1
                     break
                  if DEBUG:
                     objMsg.printMsg("***** After Erase, %s - RdBuff (LBA=0x%X) = %s" % (sctr,startLBA,ICmd.GetBuffer(2,0,512)))
            #    ii. Data in each sectors is unique (different)
            #        - This is a salting like behavior
            if result == OK:
               for i in range(1,6):
                  ICmd.ClearBinBuff(3) # Clear both write and read buffer
                  sctr1 = 'Sector %d' % (i)
                  startLBA1 = LBA_dict[sctr1]
                  data = ICmd.SequentialReadDMA(startLBA1, startLBA1+1, 1, 1, 0, 0) # Read back and put into Read Buffer, don't cmp
                  result = data['LLRET']
                  if result == OK:
                     ICmd.BufferCopy(1,0,2,0,512) # Copy to write buff (offset 0) from read buff (offset 0), total 512 bytes
                     for j in range(i+1,6):
                        sctr2 = 'Sector %d' % (j)
                        startLBA2 = LBA_dict[sctr2]
                        ICmd.ClearBinBuff(2) # Clear read buffer
                        data = ICmd.SequentialReadDMA(startLBA2, startLBA2+1, 1, 1, 0, 1)
                        result = data['LLRET']
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
                  if result != OK:
                     break
            #    iii. Every 16-bytes data block within a sector is unique (different)
            #         - This is a CBC like behavior (as opposed to ECB)
            if result == OK:
               objMsg.printMsg("Sanity Test - Comparing every 16 bytes in each sector.........")
               for i in range(1,6):
                  ICmd.ClearBinBuff(3) # Clear both write and read buffer
                  sctr = 'Sector %d' % (i)
                  startLBA = LBA_dict[sctr]
                  data = ICmd.SequentialReadDMA(startLBA, startLBA+1, 1, 1, 0, 0) # Read back and put into Read Buffer, don't cmp
                  result = data['LLRET']
                  if result == OK:
                  #---------------------------------------------------------------------------------------------------------------
                  # Workaround on CPC bug ICmd.BufferCopy(8,0,2,0,512)
                  # CPC unable to access ImgBuffer on Select Flag 0X08
                  #---------------------------------------------------------------------------------------------------------------
                     ReadBuffer = ICmd.GetBuffer(READ_BUF,0,512)
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
                              ScrCmds.raiseException(12753, "Sanity Test Fail Before KwaiPrep")
                           else:
                              if DEBUG:
                                 objMsg.printMsg("Comparing %s bytes %i:%i with %s bytes %i:%i. Pass" \
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
               for loop in range(5):
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
                  if DEBUG:
                     objMsg.printMsg("***** Rep step#1, %s - RdBuff = %s" % (sctr,ICmd.GetBuffer(2,0,512)))
            if result != OK:
               break
      if result:
         ScrCmds.raiseException(12753, "Sanity Test Fail Before KwaiPrep")
      else:
         objMsg.printMsg("Sanity Test - Passed")

   #  ========================================================================================
   #  XF sector Format
   #  ========================================================================================
   def XFFormat(self):
      objPwrCtrl.powerCycle(5000,12000,10,30) # Added pwr cyc to restore all congen settings to default
      # otherwise settings will be written to drive after format
      oSerial = serialScreen.sptDiagCmds()
      data = sptCmds.enableDiags(retries = 10, raiseException = 1)
      objMsg.printMsg("CTRL_Z data =\n%s"%data)
      data = sptCmds.sendDiagCmd('/\r', timeout = 150, raiseException = 1, altPattern='T>')
      objMsg.printMsg("/ data =\n%s"%data)
      data = sptCmds.sendDiagCmd('m0,20,,,,,,22\r', timeout = 300, loopSleepTime = 5, raiseException = 1, altPattern='T>')
      objMsg.printMsg("m0,20,,,,,,22 data =\n%s"%data)
      if "Successful" not in data:
         ScrCmds.raiseException(14797, "XF Format has Failed.")

      objMsg.printMsg('XFFormat - PowerCycle drive')
      objPwrCtrl.powerCycle(5000,12000,10,30)

   #  ========================================================================================
   #  Issue an ATA command to set the Master ATA Password to the script-generated SID
   #  ========================================================================================
   def SetMasterPassword(self, password):

      pwLen = len(password)
      for i in range(pwLen,32):
         password += ' '                 # pad with blanks to end of pw field

      identifier    = 0x01               # Select MASTER Password
      securityLevel = 0x00               # 0 = HIGH
      RevCode       = 0xFFFE             # Current revision in SeaCos F/W

      objMsg.printMsg('Setting Master ATA Password...')
      result = ICmd.SecuritySetPassword(identifier,password,securityLevel,RevCode)

      if result[LLRET]:
         objMsg.printMsg(UnexpectedStatus % result)
         Status = FAIL
      else:
         Status = OK

      return Status


   #  ========================================================================================
   #  For Serial commands, the return dictionary needs to be compatible with other commands.
   #  ========================================================================================
   def ResptoDict(self, resp):
      import types
      retd = {}  # Return Dictionary

      if type(resp) == types.IntType:
         retd[LLRET] = resp
      else:
         retd[LLRET] = resp[0]
         resplen = len(resp[1])
         if resplen > 1:
            retd[DATA] = resp[1][-2:]  # last 2 bytes are the status
         else:
            retd[DATA] = resp[1]
         if resplen == 20 or resplen == 35:      # 'Challenge' response length
            #import struct
            retd['CHALLENGE'] = resp[1][-10:-2]  # Extract the 8-byte challenge
            #objMsg.printMsg('Challenge data = %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x' % (struct.unpack('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',resp[1])))

      return retd

   #  ========================================================================================
   #  Trace a message to the CM's screen and the trace log
   #  ========================================================================================
   def trace(self, msg):
      ReportStatus(msg)
      TraceMessage(msg)

   #  ========================================================================================
   #     Build the Header portion of the APDU
   #
   #  INPUT:
   #     PktLen  - Overall length of the APDU packet in bytes - default is 512
   #     ApduLen - APDU (SeaCos) command length in bytes - defaults to 6
   #     CardNum - Card number, different than slot number, usually 0 - default is 0
   #
   #  RETURNS:
   #     The completed APDU header as a string (data is in big Endian format)
   #*****************************************************************************************
   #    This function will build the 10 byte APDU header in Big Endian format, and
   #    return it as a string.
   #
   #    Usage:  BuildApduHdr(ApduLen=6, PktLen=APDU_PACKET_SECTOR_SIZE, CardNum=0)
   #    where   PktLen  is the size of the APDU packet, less any required data
   #                    sectors. PktLen should equal the sector size.
   #            ApduLen is the length of the SeaCos command in bytes
   #            CardNum is the card the operation is to be performed on
   #  ========================================================================================
   def BuildApduHdr(self, CardNum, PktLen=APDU_PACKET_SECTOR_SIZE, ApduLen=6):

      ApduHdr = ''

      ApduHdr += chr((PktLen >> 24) & 0xFF)
      ApduHdr += chr((PktLen >> 16) & 0xFF)
      ApduHdr += chr((PktLen >> 8)  & 0xFF)
      ApduHdr += chr( PktLen        & 0xFF)     # 4 bytes of packet length (512)

      ApduHdr += chr((ApduLen >> 24) & 0xFF)
      ApduHdr += chr((ApduLen >> 16) & 0xFF)
      ApduHdr += chr((ApduLen >> 8)  & 0xFF)
      ApduHdr += chr( ApduLen        & 0xFF)    # 4 bytes of APDU length

      ApduHdr += chr((CardNum >> 8)  & 0xFF)
      ApduHdr += chr( CardNum        & 0xFF)    # 2 bytes of card number

      return ApduHdr                            # 10 bytes total


   #  ========================================================================================
   #     Build the APDU, complete with header
   #
   #  INPUT:
   #     Clain       - Class plus instruction, two byte value
   #     DataByteStr - String of data bytes to complete APDU, (P1, P2,Lc, etc.)
   #                   This data must be in the order it should be placed in the APDU
   #     PktLen      - Overall length of the APDU packet in bytes - default is 512
   #     ApduLen     - APDU (SeaCos) command length in bytes - defaults to 6
   #     CardNum     - Card number, different than slot number, usually 0 - default is 0
   #
   #  RETURNS:
   #     The completed 512 byte APDU as a string (data is in big Endian format)
   #
   #    This function will build the APDU in Big Endian format, and return it as a string.
   #    This string can be used in the IssueTrusted Send and IssueTrusted Receive functions.
   #
   #    Usage:  BuildApduHdr(ApduLen=6, PktLen=APDU_PACKET_SECTOR_SIZE, CardNum=0)
   #    where   Clains       is the two byte 'Class'/'Instruction' value
   #            DataByteList is a list of data bytes that fill out the body of the APDU.
   #                         It must include all data bytes, in the order they should appear
   #                         in the APDU, as specified in the SeaCos documentation.
   #            CardNum      is the card the operation is to be performed on
   #            PktLen       is the size of the APDU packet, less any required data
   #                         sectors. PktLen should equal the sector size.
   #            Pad          indicates whether the APDU should be padded out to the Packet
   #                         Sector Size.  Should only be necessary if adding data packets
   #                         to the end of the apdu, such as with cardload.
   #
   #  ========================================================================================
   def BuildApdu(self, Clains, DataByteList, CardNum, PktLen=APDU_PACKET_SECTOR_SIZE, Pad=0):

      # There is a minimum APDU length requirement of 5 bytes, determine the length so the header can be built
      ApduLen = max([5,len(DataByteList) + CLAINS_LENGTH])

      Apdu = self.BuildApduHdr(CardNum, PktLen, ApduLen)

      Apdu += chr((Clains >> 8) & 0xFF)
      Apdu += chr( Clains       & 0xFF)

      for x in DataByteList:
         Apdu += chr(x)

      if Pad:                              # Pad out the string with zeros to complete the APDU
         PadLen = APDU_PACKET_SECTOR_SIZE - len(Apdu)
         while PadLen > 0:
            Apdu += chr(0)
            PadLen -= 1

      return Apdu


   #  ========================================================================================
   #
   #    This function can be used to debug process development. It will dump the string in a
   #    hex dump format.  It was originally intended to dump APDUs and verify their construction.
   #    This function uses the trace function to dump the data to the trace log.
   #
   #    Usage:  DumpData(string, columns=4, columnwidth=4, limit=0)
   #    where   string       is a string containing the data to be dumped to the trace.
   #            columns      is the number of columns displayed across the screen.
   #            columnwidth  is the number of data bytes displayed in each column.
   #            limit        is the number of bytes to display.  Defaults to zero to dump the
   #                         the entire string.
   #            msg          is an optional message displayed ahead of the data
   #
   #  ========================================================================================
   def DumpData(self, string, columns=4, columnwidth=4, limit=0, msg=''):

      if msg != '':
         self.trace(msg)

      if columns < 1:
         columns = 1
      count = 0
      linenum = 1
      width = -1
      colwidth = -1
      datastr = "    0 |  "
      for x in string:
         if colwidth == (columnwidth-1):
            datastr += "  "
            colwidth = 0
         else:
            colwidth += 1

         if width == ((columns * columnwidth)-1):
            self.trace(datastr)
            if limit != 0:
               if count >= limit:
                  datastr = ""
                  break
            offset = (linenum * columns * columnwidth)
            if offset < 0x10:
               datastr = "    %X |  " % offset
            elif offset < 0x100:
               datastr = "   %X |  " % offset
            elif offset < 0x1000:
               datastr = "  %X |  " % offset
            elif offset < 0x10000:
               datastr = " %X |  " % offset
            else:
               datastr = "%X |  " % offset
            linenum = linenum + 1
            width = 0
         else:
            width += 1

         datastr = datastr + " "
         if ord(x) < 16:
            datastr = datastr + "0"
         datastr = datastr + "%X" % ord(x)
         count += 1

      if datastr != "":
         self.trace(datastr)

      DataDividerStr = ''
      DashCount = ((columnwidth * 3) * columns) + (columns * 2)   # + 10
      DataDividerStr = '-' * DashCount
      self.trace(DataDividerStr)


   #  ========================================================================================
   #  Generate The Card ID, based on the hda s/n, and the card number
   #  ========================================================================================
   def GenerateCardID(self, CardNum, RequiresOrgNum):

      if RequiresOrgNum:
         CardID = CCC_OrgNum
      else:
         CardID = []

      for character in HDASerialNumber[1:]:    # Card ID part 1 -> Drive S/N, less the first character
         CardID = CardID + [ord(character)]

      CardID = CardID + [CardNum]              # Card ID part 2 -> Card number

      return (CardID)


   #  ========================================================================================
   #  Retrieve 8 bytes of random data from the Linux entropy pool, which will subsequently   #
   #  be used to seed the Python random number generator.                                    #
   #  ========================================================================================
   def RandomSeed(self):

      try:
         fobj = open ('/dev/random','r')      # Linux Entropy Pool
         RandomNums = fobj.read(16)           # get 16 bytes (128 bits) from the pool
         fobj.close()
      except:
         objMsg.printMsg("No Entropy pool:  services->random must be enabled")
         SeedValue = 0
      else:
         SeedValue = 0
         for char in RandomNums:
            SeedValue += ord(char) * 611957      # multiply by a prime number and summ

      return SeedValue                        # final value is a large (10-digit) number


   #  ========================================================================================
   # This routine will generate the Secure ID (I.E. 'SID') that is to be printed on the drive
   # label and stored internally on the drive in the EF_SID file.  It will also create the
   # appropriate drive attributes on the network.
   #  ========================================================================================
   def GetSID(self, updateAttrs=1, override=0):

      # Possible SID characters: random ordering of 24 uppercase letters (No 'I' and No 'O' - per MS convention) and numerals 0 through 9
      CharChoices = ['H','U','7','C','J','9','T','5','R','B','G','M','E','0','F','Z','4',\
                      '8','Y','K','2','L','V','D','S','1','A','W','3','Q','X','6','P','N']
      SIDstr = ''          # Create an empty SID string to be filled with random characters

      if self.USE_EXISTING_SID and not override:       # Over-ride the Existing_SID flag
         if DriveAttributes.has_key('TD_SID'):    # see if it's in the attrs
            SIDstr = DriveAttributes['TD_SID']
            objMsg.printMsg("(Existing SID)")
         else:
            objMsg.printMsg("Could not retrieve SID from FIS !")
            ScrCmds.raiseException(14581, "Failed to retrieve TD_SID from FIS")
      else:
         # shuffle the list prior to seeding the random number generator - this ensures a unique SID
         # even if the 'RandomSeed' value is the same as a previous one.  Prevents duplicate SID's !!
         random.shuffle(CharChoices)
         seed = self.RandomSeed()
         if seed:
            random.seed(seed)                # seed the python random-number generator
         else:
            random.seed()                    # use the default python seed value

         # Generate a string of random characters
         for i in range(0, self.SidLength):
            # Generate a random number between 0 and 34, and use it to select a character from the choices list
            SIDstr += CharChoices[int(random.random() * 34)]     # random module generates a number between 0 and 1

         # Put the SID into attributes (and automatically send to the Host):
         if updateAttrs:
            self.UpdateAttributes(SIDstr)                   # FIS gets printable (ASCII) digits

      objMsg.printMsg("SID = %s" % SIDstr)
      return SIDstr


   #  ========================================================================================
   #  This updates the SID (SIDLO/SIDHI for E*; TD_SID for M2TD/CODY) drive attribute to FIS.
   #  ========================================================================================
   def UpdateAttributes(self, attrValue):
      self.dut.driveattr['TD_SID'] = attrValue

   #  ========================================================================================
   #  This routine will change the PIN from the default value, to the computed value.  This
   #  is more general, and replaces the 'UpdateBinary' method previously used.
   #  NewPin is the list of (ordinal) PIN (AKA 'SID') bytes to be written to the drive.
   #  ========================================================================================
   def ChangePin(self, NewPin, KeyRef=0x11, CardNum=ADMIN):       # NewPin = list of (ordinal) bytes of the new PIN (either 25 or 35 bytes)

      oldPin = []
      for i in range(0,self.SidLength):
         oldPin.append(ord(DEFAULT_PIN[i]))            # convert the default (old) PIN to ordinals

      if KeyRef == 0x11 and not self.DefaultData:   # KeyRef == x11
         PinData = oldPin + NewPin
         P1 = 0    # Exchange existing PIN with new PIN
      else:                                         # If NOT keyref 11
         P1 = 1    # Set PIN to new value
         PinData = NewPin

      ApduDataList = [P1,KeyRef,len(PinData)] + PinData           # P1:xfer type; P2:Key reference; Length of PIN; data bytes of PIN
      ApduString = self.BuildApdu(CHANGEPIN, ApduDataList, CardNum)    # Build the ChangePin APDU for the selected Card.
      if DEBUG_DISPLAY_APDU:
         self.DumpData(ApduString, 3, 10, len(ApduString), 'ChangePin APDU')

      if DEBUG_STEP_TRACE:
         self.trace('Sending ChangePIN')
      result = self.ExecuteSeaCosCmd(ApduString)                 # Issue the ChangePin command

      if result[DATA] != GoodStatus:
         objMsg.printMsg(UnexpectedStatus % result)
         objMsg.printMsg('ChangePin Status = %s' % (self.StatusStrToHexStr(result[DATA])))
         Status = FAIL
      else:
         Status= OK

      return Status


   #  ========================================================================================
   #  Verify the PIN (SID)
   #  ========================================================================================
   def VerifyPin(self, KeyRef=0x11, CardNum=ADMIN, Pin=None, useSerialPort=0):
      DataByteList = []

      if Pin:
         DataByteList = Pin
      else:
         for char in DEFAULT_PIN[:self.SidLength]:
            DataByteList.append(ord(char))

      # Build the APDU for VerifyPin command
      VerifyPIN = self.BuildApdu(VERIFYPIN, [0, KeyRef, len(DataByteList)] + DataByteList, CardNum)
      if DEBUG_DISPLAY_APDU:
         self.DumpData(VerifyPIN, 3, 10, len(VerifyPIN), 'VerifyPIN Apdu')

      if DEBUG_STEP_TRACE:
         self.trace('Sending VerifyPIN')
      result = self.ExecuteSeaCosCmd(Apdu=VerifyPIN, useSerialPort=useSerialPort)

      if result.has_key(DATA):
         if result[DATA] != GoodStatus:
            objMsg.printMsg('VerifyPin status = %s' % (self.StatusStrToHexStr(result[DATA])))
            if result[DATA] ==  '\x69\x86':
               Status = 0x6986
            else:
               objMsg.printMsg(UnexpectedStatus % result)
               Status = FAIL
         else:
            Status = OK
      elif result[LLRET]:
         objMsg.printMsg(UnexpectedStatus % result)
         Status = FAIL

      return Status


   #  ========================================================================================
   #  The ASN-1 length uses a technique of indicating how many bytes will be used to express
   #  the length of the data that follows.  If the length is less than 128 bytes, the protocol
   #  uses one byte to represent the length.  If the length is equal or greater than 128, the
   #  high order bit of the first length byte is set, and the remaining bits describe how many
   #  length bytes will follow.
   #  Ex  If the data being described was 130 bytes long, the length would be expressed with
   #      the following two bytes:  0x81  (0x80 -> length > 127, 0x01 -> 1 byte of length follows)
   #                                0x82  (0x82 -> length = 0x82 or 130 decimal)
   #  The Length bytes are expected in Big Endian format
   #  ========================================================================================
   def GetASN1Length(self, Length):

      IntegralLength = Length

      if IntegralLength < 128:                  # Single byte length path, ASN1 length
         return [IntegralLength]                # represented in a single byte
      else:                                     # Multiple byte length path, ASN1 length
         ASN1Length = []                        # representation requires two or more bytes
         bytecount = 0x80                       # Set high order bit of byte count to
         # indicate multiple byte length field
         while (IntegralLength > 0):
            bytecount += 1                            # Increment byte count for each byte
            # required to represent the length
            ASN1Length.append(IntegralLength & 0xFF)  # Add current low order byte of the
            # length to the ASN1 length array
            IntegralLength = IntegralLength >> 8      # Shift the bytes down one byte

         ASN1Length.append(bytecount)           # Now add the bytecount field into the array

         #  The ASN1Length byte array has been built in reverse order, so reverse it, in place,
         #  to get the normal ASN1 representation before returning the list to the caller.
         ASN1Length.reverse()
         return ASN1Length


   #  ========================================================================================
   #  If this function is successful, it will return a RSA key , a certificate, and a tampered
   #  certificate, all in a TLV binary format ready to load into the SeaCos file system.
   #  If it fails, a 'FAIL' msg will be returned
   #  ========================================================================================
   def GenerateKeyData(self, SerialNum, Type):

      #  Request Certified Key Pair - 'SIGN' signature key pair for RSA1
      #                             - 'ENCR' encryption key pair for RSA2
      objMsg.printMsg('------------ Request Certified Key Pairs ------------')
      version = self.KwaiVars['KWAI OID']
      # optional param:'includeTamperedCertificate' string will d/l the TamperedCertificate; otherwise not
      method,prms = RequestService('GetCertifiedKeyPair',(SerialNum,Type,version))

      if len(prms) == 0 or prms.get('EC',(0,'NA'))[0] != 0:
         RSA_TLV_data = 'FAIL'
         Certificate  = 'FAIL'
         TampCertificate = 'FAIL'
         objMsg.printMsg("%s : %s (%d)" % (ErrStr,prms.get('EC',(12383,'Default'))[1],prms.get('EC',(12383,'Default'))[0])) # Error from KCI server
         #failcode['Fin Kwai Prep'] = ('KCISrv',prms.get('EC',(12383,'Default'))[0])
         ScrCmds.raiseException(prms.get('EC',(12383,'Default'))[0], "Kwai Prep Failed")
      else:
         if DEBUG_VIEW_KEYPAIR_DATA:
            objMsg.printMsg('The data returned by the %s GetCertifiedKeyPair service request call:' % Type)
            for key in prms.keys():
               data = base64.decodestring(prms[key])
               self.trace("Decoded Data: %s  length: %d:" % (key,len(data)))
               self.DumpData(data, 4, 10)

         # See Trusted Drive Life Cycle Doc EF-RSA1 for details
         RSA_modulus      = base64.decodestring(prms['modulus'])         # RSA_MODULUS
         RSA_public_exp   = base64.decodestring(prms['pubExp'])          # RSA_PUBLIC_EXPONENT
         RSA_private_exp  = base64.decodestring(prms['privExp'])         # RSA_PRIVATE_EXPONENT
         RSA_factor_p     = base64.decodestring(prms['primeP'])          # RSA_FACTOR_P
         RSA_factor_q     = base64.decodestring(prms['primeQ'])          # RSA_FACTOR_Q
         PK_RSA_exp_p     = base64.decodestring(prms['primeExponentP'])  # PK_RSA_EXPONENT_P
         RSA_exp_q        = base64.decodestring(prms['primeExponentQ'])  # RSA_EXPONENT_Q
         RSA_Inv_q_mod_p  = base64.decodestring(prms['crtCoefficient'])  # RSA_INV_Q_MOD_P
         RSA_mont_modulus = base64.decodestring(prms['montModulus'])     # RSA_MONTGOMERY_N0
         RSA_mont_prime_p = base64.decodestring(prms['montPrimeP'])      # RSA_MONTGOMERY_P0
         RSA_mont_prime_q = base64.decodestring(prms['montPrimeQ'])      # RSA_MONTGOMERY_Q0

         RSA_TLV_data = [0x81]                                 # Tag RSA_MODULUS
         for element in self.GetASN1Length(len(RSA_modulus)):       # Length byte list
            RSA_TLV_data.append(element)
         for element in RSA_modulus:                           # RSA_MODULUS
            RSA_TLV_data.append(ord(element))

         if DEBUG_GENERATE_KEY_DATA:
            self.trace('RSA_TLV_data - added RSA_modulus of length %X' % len(RSA_modulus))
            DataString = ''
            for entry in RSA_TLV_data:
               DataString += chr(entry)
            self.DumpData(DataString, 4, 10)

         RSA_TLV_data.append(0x82)                             # Tag RSA_PUBLIC_EXPONENT
         for element in self.GetASN1Length(len(RSA_public_exp)):    # Length byte list
            RSA_TLV_data.append(element)
         for element in RSA_public_exp:                        # RSA_PUBLIC_EXPONENT
            RSA_TLV_data.append(ord(element))

         if DEBUG_GENERATE_KEY_DATA:
            self.trace('RSA_TLV_data - added RSA_public_exp of length %X' % len(RSA_public_exp))
            DataString = ''
            for entry in RSA_TLV_data:
               DataString += chr(entry)
            self.DumpData(DataString, 4, 10)

         RSA_TLV_data.append(0x83)                             # Tag RSA_PRIVATE_EXPONENT
         for element in self.GetASN1Length(len(RSA_private_exp)):   # Length byte list
            RSA_TLV_data.append(element)
         for element in RSA_private_exp:                       # RSA_PUBLIC_EXPONENT
            RSA_TLV_data.append(ord(element))

         if DEBUG_GENERATE_KEY_DATA:
            self.trace('RSA_TLV_data - added RSA_private_exp of length %X' % len(RSA_private_exp))
            DataString = ''
            for entry in RSA_TLV_data:
               DataString += chr(entry)
            self.DumpData(DataString, 4, 10)

         RSA_TLV_data.append(0x84)                             # Tag RSA_FACTOR_P
         for element in self.GetASN1Length(len(RSA_factor_p)):      # Length byte list
            RSA_TLV_data.append(element)
         for element in RSA_factor_p:                          # RSA_FACTOR_P
            RSA_TLV_data.append(ord(element))

         if DEBUG_GENERATE_KEY_DATA:
            self.trace('RSA_TLV_data - added RSA_factor_p of length %X' % len(RSA_factor_p))
            DataString = ''
            for entry in RSA_TLV_data:
               DataString += chr(entry)
            self.DumpData(DataString, 4, 10)

         RSA_TLV_data.append(0x85)                             # Tag RSA_FACTOR_Q
         for element in self.GetASN1Length(len(RSA_factor_q)):      # Length byte list
            RSA_TLV_data.append(element)
         for element in RSA_factor_q:                          # RSA_FACTOR_Q
            RSA_TLV_data.append(ord(element))

         if DEBUG_GENERATE_KEY_DATA:
            self.trace('RSA_TLV_data - added RSA_factor_q of length %X' % len(RSA_factor_q))
            DataString = ''
            for entry in RSA_TLV_data:
               DataString += chr(entry)
            self.DumpData(DataString, 4, 10)

         RSA_TLV_data.append(0x86)                             # Tag RSA_MONTGOMERY_N0
         for element in self.GetASN1Length(len(RSA_mont_modulus)):  # Length byte list
            RSA_TLV_data.append(element)
         for element in RSA_mont_modulus:                      # RSA_MONTGOMERY_N0
            RSA_TLV_data.append(ord(element))

         if DEBUG_GENERATE_KEY_DATA:
            self.trace('RSA_TLV_data - added RSA_mont_modulus of length %X' % len(RSA_mont_modulus))
            DataString = ''
            for entry in RSA_TLV_data:
               DataString += chr(entry)
            self.DumpData(DataString, 4, 10)

         RSA_TLV_data.append(0x87)                             # Tag PK_RSA_EXPONENT_P
         for element in self.GetASN1Length(len(PK_RSA_exp_p)):      # Length byte list
            RSA_TLV_data.append(element)
         for element in PK_RSA_exp_p:                          # PK_RSA_EXPONENT_P
            RSA_TLV_data.append(ord(element))

         if DEBUG_GENERATE_KEY_DATA:
            self.trace('RSA_TLV_data - added PK_RSA_exp_p of length %X' % len(PK_RSA_exp_p))
            DataString = ''
            for entry in RSA_TLV_data:
               DataString += chr(entry)
            self.DumpData(DataString, 4, 10)

         RSA_TLV_data.append(0x88)                             # Tag RSA_EXPONENT_Q
         for element in self.GetASN1Length(len(RSA_exp_q)):         # Length byte list
            RSA_TLV_data.append(element)
         for element in RSA_exp_q:                             # RSA_EXPONENT_Q
            RSA_TLV_data.append(ord(element))

         if DEBUG_GENERATE_KEY_DATA:
            self.trace('RSA_TLV_data - added RSA_exp_q of length %X' % len(RSA_exp_q))
            DataString = ''
            for entry in RSA_TLV_data:
               DataString += chr(entry)
            self.DumpData(DataString, 4, 10)

         RSA_TLV_data.append(0x89)                             # Tag RSA_INV_Q_MOD_P
         for element in self.GetASN1Length(len(RSA_Inv_q_mod_p)):   # Length byte list
            RSA_TLV_data.append(element)
         for element in RSA_Inv_q_mod_p:                       # RSA_INV_Q_MOD_P
            RSA_TLV_data.append(ord(element))

         if DEBUG_GENERATE_KEY_DATA:
            self.trace('RSA_TLV_data - added RSA_Inv_q_mod_p of length %X' % len(RSA_Inv_q_mod_p))
            DataString = ''
            for entry in RSA_TLV_data:
               DataString += chr(entry)
            self.DumpData(DataString, 4, 10)

         RSA_TLV_data.append(0x8A)                             # Tag RSA_MONTGOMERY_P0
         for element in self.GetASN1Length(len(RSA_mont_prime_p)):  # Length byte list
            RSA_TLV_data.append(element)
         for element in RSA_mont_prime_p:                      # RSA_MONTGOMERY_P0
            RSA_TLV_data.append(ord(element))

         if DEBUG_GENERATE_KEY_DATA:
            self.trace('RSA_TLV_data - added RSA_mont_prime_p of length %X' % len(RSA_mont_prime_p))
            DataString = ''
            for entry in RSA_TLV_data:
               DataString += chr(entry)
            self.DumpData(DataString, 4, 10)

         RSA_TLV_data.append(0x8B)                             # Tag RSA_MONTGOMERY_Q0
         for element in self.GetASN1Length(len(RSA_mont_prime_q)):  # Length byte list
            RSA_TLV_data.append(element)
         for element in RSA_mont_prime_q:                      # RSA_MONTGOMERY_Q0
            RSA_TLV_data.append(ord(element))

         if DEBUG_GENERATE_KEY_DATA:
            self.trace('RSA_TLV_data - added RSA_mont_prime_q of length %X' % len(RSA_mont_prime_q))
            DataString = ''
            for entry in RSA_TLV_data:
               DataString += chr(entry)
            self.DumpData(DataString, 4, 10)

         #  Now prepend a header, with Tag and overall structure length
         length_bytes = []
         for element in self.GetASN1Length(len(RSA_TLV_data)):      # Length byte list
            length_bytes.append(element)

         RSA_TLV_data_hdr = [0x7F,0x49] + length_bytes         # RSA1 Tag + Length of overall structure

         RSA_TLV_data = RSA_TLV_data_hdr + RSA_TLV_data        # Entire combined structure

         if DEBUG_GENERATE_KEY_DATA:
            self.trace('RSA_TLV_data - Prepended RSA1 Tag [7F,49] and ASN1 total length of %X' % len(RSA_TLV_data))
            DataString = ''
            for entry in RSA_TLV_data:
               DataString += chr(entry)
            self.DumpData(DataString, 4, 10)

      Certificate = base64.decodestring(prms['Certificate'])   #  Prepare Certificate

      #  Prepare Tampered Certificate - Currently not going to be loaded on the drive, so don't waste time with it
      #TampCertificate = base64.decodestring(prms['TamperedCertificate'])
      TampCertificate = 'FAIL'

      #  Return either null, or a TLV formatted RSA key, certificate, and tampered certificate
      #  in binary format; each ready to load into the SeaCos file system.
      return (RSA_TLV_data, Certificate, TampCertificate)


   #  ========================================================================================
   #  Convert a status string to hex characters
   #  ========================================================================================
   def StatusStrToHexStr(self, strStatus):

      strStatusHex = "0x"
      for char in strStatus:
         ordValue = ord(char)
         if ordValue < 10:
            strStatusHex = strStatusHex + '0'   # if the ord value is a single digit, add a leading 0
         strStatusHex = strStatusHex + '%X' % ordValue

      return (strStatusHex)


   #  ========================================================================================
   #
   #    This function will issue a PassThroughLBA command to set up the task file
   #    registers and execute a Trusted Send command.  The APDU data for the Trusted
   #    Send command must already exist in the write buffer on the interface. The
   #    interface watchdog timer is set to 20 seconds.
   #
   #    Usage: IssueTrustedSend(ApduStr, SectorCount=1, PktLen=512)
   #    where  ApduStr      is an APDU string built up by using the BuildApdu function
   #                        it may also include data appended to the APDU
   #           SectorCount  is the number of sectors to transfer, including data
   #           PktLen       is the size of the APDU packet, less any required data
   #                        sectors. PktLen should equal the sector size.
   #
   #  ========================================================================================
   def IssueTrustedSend(self, ApduStr, SectorCount=1, PktLen=512, useSerialPort=0):

      if not useSerialPort:       # Data is being sent through the ATA interface.
         TIMEOUT = 20000
         ICmd.SetIntfTimeout(TIMEOUT)
         if ApduStr != '':
            ICmd.FillBuffer(WRITE_BUF, 0, ApduStr)   # Move the APDU data to the Write buffer

   #---------------------------- DEBUG STUFF --------------------------------------------
            if DEBUG_VERIFY_WRT_BUF:
               result = ICmd.GetBuffer(WRITE_BUF, 0, len(ApduStr))
               self.trace('Write Buffer Data (%d bytes)' % len(ApduStr))
               self.DumpData(result[DATA], 4, 8)
         byte_count = SectorCount * PktLen
         if DEBUG_BYTECOUNT_0:
            if SectorCount == 33:
               byte_count = 0

         if DEBUG_REPORT_EXEC_TRUST_SEND:
            objMsg.printMsg('Executing Trusted Send')

         if DEBUG_PASSTHROUGH_BYTECOUNT:
            self.trace('byte_count = 0x%x' % byte_count)
   #------------------------ End DEBUG STUFF --------------------------------------------
         result = ICmd.PassThrough(VENDOR_UNIQUE_PIO_WRITE,self.TRUSTED_SEND_CMD,0,SectorCount,PROTOCOL_ID,byte_count)   # Issue the Trusted Send command
      else:                         # Data is being sent through the serial port

         #UseEchoCheck(1)            # each byte is echo'ed back, so turn on echocheck !!!
         try:
            #result = self.ResptoDict(SerialSend(ApduStr))     # Send the Apdu
            result = self.ResptoDict(PBlock(ApduStr))     # Send the Apdu
         except:
            result = {}
            result[LLRET] = -1
         #UseEchoCheck(0)            # Turn off Echo Check
      if result[LLRET] != OK:
         objMsg.printMsg('Failed Trusted Send, SectorCount: %d' % SectorCount)
         objMsg.printMsg('Trusted Send result: %s' % result)

      return result


   #  ========================================================================================
   #
   #    This function will issue a PassThroughLBA command to set up the task file
   #    registers and execute a Trusted Receive command.  The APDU data for the Trusted
   #    Receive command must already exist in the write buffer on the interface. The
   #    interface watchdog timer is set to 20 seconds.
   #
   #    Usage: IssueTrustedReceive(SectorCount=1, PktLen=512)
   #    where  SectorCount  is the number of sectors to transfer, including data
   #           PktLen       is the size of the APDU packet, less any required data
   #                        sectors. PktLen should equal the sector size.
   #
   #  ========================================================================================
   def IssueTrustedReceive(self, SectorCount=1, PktLen=512, useSerialPort=0):
      if not useSerialPort:
         ICmd.SetIntfTimeout(60000)   # Set the interface timeout value to 20 sec
         byte_count = SectorCount * PktLen

   #---------------------------- DEBUG STUFF --------------------------------------------
         if DEBUG_PASSTHROUGH_BYTECOUNT:
            self.trace('byte_count = 0x%x' % byte_count)
   #------------------------ End DEBUG STUFF --------------------------------------------

         result = ICmd.PassThrough(VENDOR_UNIQUE_PIO_READ,self.TRUSTED_RECEIVE_CMD,0,SectorCount,PROTOCOL_ID,byte_count)      # Issue Trusted Receive
      else:
         #result = self.ResptoDict(SerialWait(GoodStatus))   #  Get the response.
         time.sleep(5)
         data = GChar(0)
         #objMsg.printMsg('Trusted Receive, data = %s  len = %d' % (data,len(data)))
         if data[-2:] == GoodStatus:
            res = 0
         else:
            res = -1
         result = self.ResptoDict((res,data))   #  Get the response.
         #objMsg.printMsg('Trusted Receive, result = %s' % result)

      if result[LLRET] != OK:
         objMsg.printMsg('Failed Trusted Receive, SectorCount: %d' % SectorCount)
         objMsg.printMsg('Trusted Receive data: %s' % result)

      return result


   #  ========================================================================================
   #
   #    This function will write a card to the drive.  It is intended to be used to
   #    to create the Admin card, (card 0), and card 1.  It does so by executing a
   #    Trusted Send command through an IssueTrusted Send function call.  This function
   #    returns the typical results dictionary returned by typical IO function calls.
   #
   #    Usage: WriteCard(ApduStr, DataFile, DataFileSize=32)
   #    where  ApduStr      is an APDU string built up by using the BuildApdu function
   #           DataFile     is the file containing the card data.  Make sure the file is
   #                        listed in the config file and exists in the dlfiles directory.
   #           DataFileSize is the length of the data file in sectors
   #
   #  ========================================================================================
   def WriteCard(self, ApduStr, DataFile, DataFileSize=32):

      # Build a path to the secure card data files

      card_datafile = os.path.join(CN, DataFile)                       # Start by prepending the configuration name to the filenames
      card_datafile = os.path.join(UserDownloadsPath, card_datafile)   # then prepend the download path provided by the CM
      card_data_hdl = open(card_datafile, "r")                         # Create handles to the appropriate files
      data_str = card_data_hdl.read()                                  # Read the file information into a data buffer
      card_data_hdl.close()                                            # close the file handle

      # Build the APDU Packet into a string by concatenating the two data strings
      apdu_with_data = ApduStr + data_str

      # Execute the Card Write command to write card data and return status
      return self.ExecuteSeaCosCmd(apdu_with_data, DataFileSize+1)


   #  ========================================================================================
   #    This will Write an Image to the drive at the prescribed LBA, using the IFD method.
   #  ========================================================================================
   def WriteImage(self, ImageFile, Select=0, CardNum=ADMIN):
      if ImageFile == None or ImageFile.upper() == 'NONE':
         return OK
      from IntfClass import CIdentifyDevice
      Status = OK
      res = ICmd.SetFeatures(SET_XFER_MODE, ULTRA_DMA)    # IFD requires DMA mode
      if res[LLRET]:
         objMsg.printMsg("Set Features Failure.")
         Status = FAIL
      if Status != FAIL:
         res = ICmd.DeleteImageBuffers()
         if res[LLRET]:
            objMsg.printMsg("DeleteImageBuffers Failure.")
            Status = FAIL
      if Status != FAIL:
         # Issue an Identify Device command and determine whether 28 or 48 bit address mode is enabled.
         # Then set up the CPC accordingly - large buffers (5MB) for 48-bit mode, and not-so large (128K) buffers for 28-bit mode.
         # Note that the Images must be built such that the segments do not exceed 128K (in order to be compatible with both modes)!!!
         oIdentifyDevice = CIdentifyDevice()
         data = oIdentifyDevice.ID                   # read device settings with identify device
         if data['IDCommandSet5'] & 0x400:           # bit 10 TRUE - 48-bit LBA mode:
            objMsg.printMsg("48-bit LBA mode.")      # set up CPC for two 5MB buffers
            res = ICmd.InitImageBuffers(2,10240)     # This value is hard-coded in the CM's imagedl.c, so a smaller buffer won't work!
         else:                                       # bit 10 FALSE - 28-bit LBA mode:
            objMsg.printMsg("28-bit LBA mode.")      # CPC uses 2 buffers of 128K each
            res = ICmd.InitImageBuffers(2,256)
         if res[LLRET]:
            objMsg.printMsg("InitImageBuffers Failure - res = %s"%res)
            Status = FAIL
      if Status != FAIL:
         objMsg.printMsg("Writing Image %s..." % ImageFile)
         Verify = 1
         try:
            # Use the IFD call to download the Image to the CM.  If the image is in binary format (I.E. no '.0' file), then the CM will
            # throw a 'FOFFileIsMissing' exception, so catch that exception, and try the APDU method to download the image.
            # If the image is in IFD format, then it should just DMA the image without an exception - if the IFD gets an exception, then fail.
            DownloadImage(ImageFile)
         except FOFFileIsMissing:
            objMsg.printMsg("Using APDU method.....")
            Verify = 0
            Status = self.WritePreBootImage(ImageFile, CardNum)

         if Status != FAIL and Verify:
            # OK - download complete - now verify the Image.
            # NOTE: In order to get the MD5 value, CPC code must be at *least* version 2.112
            Status,md5 = self.VerifyImage(ImageFile)
            if Status != FAIL:
               if Select == 3:    # Pre-Boot Image
                  self.dut.driveattr['IFD_PBI_01_PN'] = ImageFile
                  self.dut.driveattr['IFD_PBI_01_HASH'] = md5
               elif Select == 4:  # User Image
                  self.dut.driveattr['IFD_IMG_01_PN'] = ImageFile
                  self.dut.driveattr['IFD_IMG_01_HASH'] = md5

         if Status != FAIL:
            res = ICmd.SetFeatures(SET_XFER_MODE, DEFAULT_PIO)     # SeaCos (currently) requires PIO mode
            if res[LLRET]:
               objMsg.printMsg(UnexpectedStatus % res)
               Status = FAIL
            # Now delete the CPC buffers so they won't interfere with subsequent script operations
            res = ICmd.DeleteImageBuffers()
            if res[LLRET]:
               objMsg.printMsg("DeleteImageBuffers Failure.")
               Status = FAIL
      return Status

   #  ========================================================================================
   #  This function will write the Specified Pre-Boot Image, using the UpdateBinaryBERTLV Apdu.
   #  ========================================================================================
   def WritePreBootImage(self, ImageFile, CardNum=2):

      # This gets the image after being D/L by IFD process
      Image_pathfile = os.path.join('/var/merlin/images', ImageFile)    # prepend the download path where Images are strored by the Host
      Image_datafile = os.path.join(Image_pathfile, ImageFile+'.bin')   # add the filename of the Image (The directory and filename are the same)

      Image_hdl = open(Image_datafile, "r")                             # then create a handle to the appropriate file.

      cntr = offset = 0
      sectors_to_xfer = 127                                             # Number of sectors (255 MAX)
      datalen = sectors_to_xfer * 512                                   # length of XF data transfer
      bytes = datalen
      Status = self.SelectFileExtd([MASTER_FILE, EF_REMAPPED_BOOT_SECTORS], CardNum)
      if Status != FAIL:
         while datalen == bytes:
            Status = OK
            ImageData = Image_hdl.read(bytes)                              # Read the file information 65,024 bytes at a time.
            datalen = len(ImageData)

            if datalen:
               cntr += 1

               # Create the TLV: p1, p2, length, tag, tag length, offset (I.E. the 'value')
               OffsetTLV = [0x00,0x00,0x06,0x54,0x04,(offset & 0xFF000000)>>24,(offset & 0x00FF0000)>>16,(offset & 0x0000FF00)>>8,(offset & 0x000000FF)]

               xfercnt = datalen + 0x200                         # bytes to transfer - includes the APDU length.
               # Build the APDU for UpdateBinaryBerTlv
               # Note that with "BLOCK MODE", XF data *must* begin on a 512-byte boundary, so PAD the APDU out to 512 bytes !!!!
               UpdateBerTlv = self.BuildApdu(UPDATEBINARYBERTLV, OffsetTLV, CardNum, xfercnt, Pad=1)

               Apdu_with_data = UpdateBerTlv + ImageData         # Append the XF Data to the (padded) Apdu

               if DEBUG_DISPLAY_APDU:
                  self.DumpData(UpdateBerTlv, 3, 10, len(UpdateBerTlv), 'UpdateBinaryBerTlv Apdu') # Only display the Apdu - *NOT* the XF data

               offset += datalen           # Increment the offset

               result = self.ExecuteSeaCosCmd(Apdu=Apdu_with_data, SectorCount=xfercnt/512)    # This takes ~ 175 milliseconds/sector (or 1 hr/9 MB Image)

#                if (cntr % 10) == 0:
#                   objMsg.printMsg("Count: %d - Bytes xfered: %d    " % (cntr,offset))
               if result[DATA] != GoodStatus:
                  objMsg.printMsg('UpdateBinaryBERTLV status = %s  count: %d' % (self.StatusStrToHexStr(result[DATA]),cntr))
                  Status = FAIL
                  break

         Image_hdl.close()

      return Status

   #  ========================================================================================
   #  This function will perform a verification of the IFD Image, and return the MD5 value.
   #  ========================================================================================
   def VerifyImage(self, Image):
      shfFile = Image + '.shf'
      Status = OK
      md5 = ''

      objMsg.printMsg("Verifying Image - %s" % Image)
      res = self.LoadFile(shfFile, shfFile, scrFileDir = ImageFilesPath +'/' + Image)    #  Load the .shf file to the CPC's file system
      if (res['LLRET'] != 0):
         objMsg.printMsg("Failed loading %s file!!" % shfFile)
         Status = FAIL

      if Status != FAIL:
         res = ICmd.VerifyIFDImage(shfFile)
         if (res['RESULT'].find("IEK_OK") == -1):
            objMsg.printMsg("Image Verify FAILED: %s" % res)
            Status = FAIL
         else:
            md5 = res['MD5']
            objMsg.printMsg("Image Verify PASSED!!  MD5 = %s" % md5)

      return Status,md5


   #  ========================================================================================
   #
   #    This function will retrieve the status of the last card operation by issuing
   #    a Trusted Receive command.  The status will always be a two byte value.  If
   #    more information is returned by the drive, it should be uploaded using the
   #    GetSeaCosData function. The function returns the typical dictionary
   #    associated with an IO command,including the status in the 'DATA' field.
   #
   #    Usage: ReadSeaCosStatus()
   #    Assumption: The status is at an offset of 10 in the buffer, and consists of 2 bytes
   #
   #  ========================================================================================
   def ReadSeaCosStatus(self, SectorCount=1, useSerialPort=0):

      result = self.IssueTrustedReceive(SectorCount=SectorCount, useSerialPort=useSerialPort)   # Issue Trusted Receive command to read the SeaCos status

      if result[LLRET] == OK:   # Check the status of the command
         # Everything OK - Read back one sector with the SeaCos Status
         # The status is the first two bytes following the APDU header (10 hdr bytes), expect 0x9000
         if not useSerialPort:          # If using ATA interface,
            result = self.GetSeaCosStatus()  # then get the SeacosStatus

         if result[LLRET] != OK:
            objMsg.printMsg('Failed to upload Status Data')

      else:   # Trouble with the Trusted Receive command
         objMsg.printMsg('Failed Trusted Receive Command, Result: %s' % result)

      return result


   #  ========================================================================================
   #
   #    This function will retrieve the two status bytes from the read buffer at an offset
   #    of 10.  The function returns the typical dictionary associated with an IO command,
   #    including the status in the 'DATA' field.  This function can be called after issuing
   #    a Trusted Receive command to retrieve the sector of data from the previous Trusted Send
   #    command and extract the status bytes.
   #
   #    Usage: GetSeaCosStatus()
   #
   #  ========================================================================================
   def GetSeaCosStatus(self):

      result = ICmd.GetBuffer(READ_BUF, 4, 4)
      if result[LLRET] != OK:
         objMsg.printMsg('Failed to upload Response Length Bytes')
      else:       # Determine the size of the data being returned
         response_length = self.GetResponseLength()
         if response_length != -1:
            result = ICmd.GetBuffer(READ_BUF, 10 + response_length - 2, 2)
            if result[LLRET] != OK:
               objMsg.printMsg('Status at Data offset %X is %s' % (10 + response_length - 2, self.StatusStrToHexStr(result[DATA])))
         else:
            result[LLRET] = -1

      return result


   #  ========================================================================================
   #
   #    This function will retrieve the response length, in bytes, of the data returned by
   #    the Trusted Receive command.  The return value is the integer responnse length.  A
   #    length of negative 1 indicates a failure.
   #
   #    Usage: GetResponseLength()
   #
   #  ========================================================================================
   def GetResponseLength(self):

      datasize = 0
      x = 1

      # Retrieve the data response length data from the read buffer, four bytes at offset of four
      result = ICmd.GetBuffer(READ_BUF, 4, 4)
      if result[LLRET] != OK:
         datasize = -1
         objMsg.printMsg('Failed to upload Response Length Bytes')
      else:         # Convert the string to an int to determine the size of the data being returned
         for character in result[DATA]:
            x += 1
            datasize = (datasize << 8) + ord(character)

      if datasize > 512:
         datasize = x                  # This prevents the CPC cell from choking if bad data returned in buffer

      return datasize


   #  ========================================================================================
   #
   #    This function will read the specified number of bytes of data from the read buffer
   #    at the specified offset.  The function returns the typical dictionary associated
   #    with an IO command, including the data in the 'DATA' field.  This function can
   #    be called after issuing a Trusted Receive command to read a sector of status data.
   #
   #    Usage: GetSeaCosData(offset=12, bytes=10)
   #    where  offset is the offset into the read buffer
   #           bytes  is the number of bytes to return in the 'DATA' field
   #
   #  ========================================================================================
   def GetSeaCosData(self, offset=12, bytes=10):

      result = ICmd.GetBuffer(READ_BUF, offset, bytes)   # Retrieve the data from the read buffer
      if result[LLRET] != OK:
         objMsg.printMsg('Failed to upload SeaCos Data')

      return result


   #  ========================================================================================
   #  Execute a given SeaCos Command
   #  ========================================================================================
   def ExecuteSeaCosCmd(self, Apdu, SectorCount=1, RtnSectorCount=1, PktLen=512, useSerialPort=0):

      result = self.IssueTrustedSend(Apdu, SectorCount, PktLen, useSerialPort)  # Issue the SeaCos Trusted Send command to send the APDU

      if result[LLRET] == OK:
         result = self.ReadSeaCosStatus(RtnSectorCount, useSerialPort)          # Issue the Trusted Receive command to get the command status back
         if result[LLRET] != OK:
            objMsg.printMsg('Unable to retrieve status, Results: %s' % result)
      else:
         objMsg.printMsg('Failed Trusted Send command, Results: %s' % result)
         if DEBUG_DISPLAY_APDU:
            self.DumpData(Apdu, 3, 10, len(Apdu), 'Dumping Failed APDU')

      return result


   #  ========================================================================================
   #  Perform a 'Get Challenge'
   #  ========================================================================================
   def GetChallenge(self, CardNum=ADMIN, useSerialPort=0):

      GetChallenge = self.BuildApdu(GETCHALLENGE, [0, 0, 8], CardNum)   # Build the APDU for Get Challenge
      if DEBUG_DISPLAY_APDU:
         self.DumpData(GetChallenge, 3, 10, len(GetChallenge), 'Get Challenge APDU')

      self.trace('Sending Get Challenge')
      result = self.ExecuteSeaCosCmd(Apdu=GetChallenge,useSerialPort=useSerialPort)      # Issue the Get Challenge command

      if result[LLRET] == OK and result[DATA] != GoodStatus:
         objMsg.printMsg('Get Challenge status = %s' % self.StatusStrToHexStr(result[DATA]))

      return result


   #  ========================================================================================
   #  Perform an external Authenticate
   #  ========================================================================================
   def ExtAuthenticate(self, DataByteList='', CardNum=ADMIN, KeyRef=0x9F, useSerialPort=0):

      ExtAuthenticate = self.BuildApdu(EXTERNALAUTHENTICATE, [0, KeyRef, 8] + DataByteList, CardNum)
      if DEBUG_DISPLAY_APDU:
         self.DumpData(ExtAuthenticate, 3, 10, len(ExtAuthenticate), 'External Authenticate Apdu')

      self.trace('Sending External Authenticate')
      result = self.ExecuteSeaCosCmd(Apdu=ExtAuthenticate,useSerialPort=useSerialPort)   # Issue the External Authenticate command

      if result[LLRET] == OK and result[DATA] != GoodStatus:
         objMsg.printMsg('External Authenticate Status = %s' % self.StatusStrToHexStr(result[DATA]))

      return result


   #  ========================================================================================
   #  Initialize SeaCos
   #  ========================================================================================
   def InitSeaCos(self):

      InitSeaCos = self.BuildApdu(INITSEACOS, '', CardNum=ADMIN)  # Build the APDU for Init SeaCos command
      if DEBUG_DISPLAY_APDU:
         self.DumpData(InitSeaCos, 3, 10, len(InitSeaCos), 'Init SeaCos Apdu')

      self.trace('Sending Init SeaCos')
      result = self.ExecuteSeaCosCmd(InitSeaCos)                # Issue the InitSeaCos command

      if result[DATA] != GoodStatus:
         objMsg.printMsg('Init SeaCos Status = %s' % self.StatusStrToHexStr(result[DATA]))
         if result[DATA] == '\x66\x00':
            objMsg.printMsg('Firmware and FILE SYSTEM versions do not match!')
            Status = FAIL
         else:
            objMsg.printMsg(UnexpectedStatus % result)
            Status = FAIL
      else:
         Status = OK

      return Status

   #  ========================================================================================
   #  Synchronize the specified card(s)
   #  ========================================================================================
   def Synchronize(self, CardNum=ADMIN, Level=0):

      if Level:
         Apdu = SYNCHRONIZEALL  # Commit *all* card images
      else:
         Apdu = SYNCHRONIZE         # Commit the *current* card image

      Synchronize = self.BuildApdu(Apdu, [0, 0, 0], CardNum)   # Build the APDU for Synchronize command
      if DEBUG_DISPLAY_APDU:
         self.DumpData(Synchronize, 3, 10, len(Synchronize), 'Synchronize Apdu')

      self.trace('Sending Synchronize')
      result = self.ExecuteSeaCosCmd(Synchronize)   # Issue the Synchronize command

      if result[DATA] != GoodStatus:
         objMsg.printMsg(UnexpectedStatus % result)
         objMsg.printMsg('Synchronize Status = %s' % (self.StatusStrToHexStr(result[DATA])))
         Status = FAIL
      else:
         Status = OK

      return Status

   #  ========================================================================================
   #  Do a warm reset
   #  ========================================================================================
   def WarmReset(self, CardNum=ADMIN, useSerialPort=0):

      WarmReset = self.BuildApdu(WARMRESET, [0, 0x0C, 0], CardNum)   # Build the APDU for WarmReset command
      if DEBUG_DISPLAY_APDU:
         self.DumpData(WarmReset, 3, 10, len(WarmReset), 'WarmReset Apdu')

      self.trace('Sending WarmReset ')
      result = self.ExecuteSeaCosCmd(Apdu=WarmReset,useSerialPort=useSerialPort)   # Issue the WarmReset command

      if result[LLRET] == OK and result[DATA] != GoodStatus:
         objMsg.printMsg('WarmReset Status = %s' % self.StatusStrToHexStr(result[DATA]))

      Status = OK
      if result.has_key(DATA):
         if result[DATA] != GoodStatus:
            objMsg.printMsg(UnexpectedStatus % result)
            objMsg.printMsg('WarmReset Status = %s' % (self.StatusStrToHexStr(result[DATA])))
            if result[DATA] == '\x69\x86':
               objMsg.printMsg('Status Indicates BAD or no File System Installed')
            Status = FAIL
      else:
         Status = FAIL

      return Status


   #  ========================================================================================
   # The Smart Cards that get written are described in a text file which is named by the F/W guys.
   # This function will open the text file and get the name of the card to install. The text file
   # format follows:
   # Admin:    fs0000.dat
   # CSC:      fs0001.dat
   # Template: fs0002.dat
   # Features: fs0003.dat
   # FDE:      fs0004.dat
   # Keytable: PublicKT.dat
   #  ========================================================================================
   def getCardFileName(self, CardFile):                    # CardFile is 'Admin' 'CSC', etc
      CardFileName = ''
      if self.KwaiVars.has_key('Card Doc PN'):            # ex: LC_3_3_rev2
         TextFileName = self.KwaiVars['Card Doc PN']
         # prepend the configuration name to the text file name
         textfile = os.path.join(CN, TextFileName + '.txt')    # configname/LC_3_3_rev2.txt
         # Next, prepend the download path provided by the CM
         datafile = os.path.join(UserDownloadsPath, textfile)
         # Create a file object to the appropriate file
         Fobj = open(datafile, "r")
         line = Fobj.readline()                      # read the first line
         while line != '#':
            line = line.split()                      # make a list of strings: ['Admin:', 'fs0000.dat']
            if line[0][0:-1].upper() == CardFile.upper():  # First item in list should be the File identifier ('Admin:', 'CSC:',etc)
               CardFileName = line[1]                # If they match, then get the file name (fs0000.dat, fs0001.dat, etc)
               break                                 # and exit
            else:
               line = Fobj.readline()                # Otherwise, keep looking
         objMsg.printMsg("Loading Card %s (%s)" % (CardFileName,CardnameXref[CardFile]))
         Fobj.close()
      else:
         objMsg.printMsg("'Card Doc PN' not specified in ConfigVars")
         ScrCmds.raiseException(12383, "Kwai Prep Failed")

      return CardFileName                            # return the file name ('fs0000.dat', 'fs0001.dat', etc OR '' if no ConfigVar entry)


   #  ========================================================================================
   #  CardSlot is any valid card SLOT number for the SeaCos system
   #  CardDataFile is a filename string, WITHOUT any directory information attached
   #  ========================================================================================
   def LoadCard(self, CardSlot, CardDataFile, Enabled=0):

      ApduDataList = [0,CardSlot,0,0x20]  # WORD CardNum, WORD Block Count (MSB first)

      ApduString = self.BuildApdu(DIRECTCARDWRITE, ApduDataList, 0, 0x4200, Pad=1)   # Build the CardLoad APDU
      if DEBUG_DISPLAY_CARD_LOAD_APDU:
         objMsg.printMsg('Dumping CardLoad APDU for card slot %d' % CardSlot)
         self.DumpData(ApduString, 4, 8)

      result = self.WriteCard(ApduString, CardDataFile, DataFileSize=32)   # Attempt to write the card data

      if result[LLRET] == OK and result[DATA] != GoodStatus:
         objMsg.printMsg('Cardload Status for card slot %d = %s' % (CardSlot, self.StatusStrToHexStr(result[DATA])))
         Status = FAIL
         if result[DATA] == '\x69\x82' and Enabled:
            objMsg.printMsg('Drive appears to have Kwai file system installed!')
         elif result[DATA] == '\x69\x86' and Enabled:
            objMsg.printMsg('Drive appears to be in the OPERATIONAL state!')
         else:
            objMsg.printMsg(UnexpectedStatus % result)
            objMsg.printMsg('LoadCard Status = %s' % (self.StatusStrToHexStr(result[DATA])))
      else:
         Status = OK

      return Status


   #  ========================================================================================
   #  CardNum is any valid card SLOT number for the SeaCos system
   #  CardCopy is 0 for the primary copy, 1 for the secondary copy
   #  ========================================================================================
   def DirectCardRead(self, CardSlot=0, CardCopy=0):

      ApduDataList = [0,CardSlot,0,0x20,0,CardCopy]  # WORD CardSlot, WORD Block Count (MSB first)

      ApduString = self.BuildApdu(DIRECTCARDREAD, ApduDataList, 0, 0x200)   # Build the DirectCardRead APDU
      if DEBUG_DISPLAY_APDU:
         objMsg.printMsg('Dumping Direct Card Read APDU for card slot %d' % CardSlot)
         self.DumpData(ApduString, 4, 8)

      result = self.ExecuteSeaCosCmd(ApduString, RtnSectorCount=33)   # Attempt the card dump

      if result[LLRET] == OK and result[DATA] != GoodStatus:
         objMsg.printMsg('Card Dump Status for card slot %d = %s' % (CardSlot, self.StatusStrToHexStr(result[DATA])))

      return result



   #  ========================================================================================
   #  Create a file on a (User) card
   #  ========================================================================================
   def CreateFile(self, FCP, CardNum):

      createfile = self.BuildApdu(CREATEFILE, [0, 0, len(FCP)] + FCP, CardNum)   # Build the APDU
      if DEBUG_DISPLAY_APDU:
         self.DumpData(createfile, 3, 10, len(createfile), 'Create File APDU')

      self.trace('Sending Create File for card %d' % CardNum)
      result = self.ExecuteSeaCosCmd(Apdu=createfile)         # Issue the command

      if result[LLRET] == OK and result[DATA] != GoodStatus:
         objMsg.printMsg(UnexpectedStatus % result)
         objMsg.printMsg('Create File status = %s' % self.StatusStrToHexStr(result[DATA]))
         Status = FAIL
      else:
         Status = OK

      return Status                                      # return the status

   #  ========================================================================================
   #    This function will unlock the admin card so the cards can be rewritten.  This involves
   #    a complicated procedure of creating and selecting files to get to the unlock bytes.
   #  ========================================================================================
   def UnlockCards(self):

      ApduString = self.BuildApdu(ERASEALL, '', 0)   # Build the APDU to invalidate the cards
      if DEBUG_DISPLAY_APDU:
         self.DumpData(ApduString, 3, 10, len(ApduString), 'Eraseall Cards APDU')

      self.trace('Sending EraseAll Cards command')
      result = self.ExecuteSeaCosCmd(ApduString)     # Issue the Invalidate Cards command

      # Report the status of the Invalidate Cards command
      if result[LLRET] == OK and result[DATA] != '\x62\x00':
         objMsg.printMsg('Eraseall Cards status = %s' % self.StatusStrToHexStr(result[DATA]))

      return result


   #  ========================================================================================
   #  This SelectFile routine defaults to the master file (0x3F00), with no return of the FCP
   #  Use 'TRUE' or 'FALSE' to select whether or not the FCP is returned.
   #  ========================================================================================
   def SelectFile(self, FileID=MASTER_FILE, CardNum=ADMIN, ReturnFCP='FALSE', useSerialPort=0):

      if ReturnFCP == 'FALSE':
         ReturnFCPSelection = DONT_RETURN_FCP
      else:
         ReturnFCPSelection = RETURN_FCP

      FileID_HiByte = FileID / 256
      FileID_LoByte = FileID % 256

      SelectFile = self.BuildApdu(SELECTFILE, [0, ReturnFCPSelection, 2, FileID_HiByte, FileID_LoByte], CardNum )
      if DEBUG_DISPLAY_FILE_SELECTION:
         DumpDataMsg = ('Select File %s (%X) APDU' % (FilenameXRef[FileID],FileID))
         self.DumpData(SelectFile, 3, 10, len(SelectFile),  DumpDataMsg)

      objMsg.printMsg('Selecting File --> %s' % (FilenameXRef[FileID]))
      result = self.ExecuteSeaCosCmd(SelectFile, useSerialPort=useSerialPort)   # Issue the Select File command

      if result[LLRET] == OK:
         if result[DATA] != GoodStatus:      # if not good status, display it
            objMsg.printMsg('Select File status for %s (%X) = %s' % (FilenameXRef[FileID],FileID,self.StatusStrToHexStr(result[DATA])))
         if ReturnFCPSelection == RETURN_FCP and not useSerialPort:
            if result[DATA] == GoodStatus:
               response_length = self.GetResponseLength()
               if response_length != -1:
                  ReadBinaryData = self.GetSeaCosData(offset=10, bytes=response_length-2)
                  if ReadBinaryData[LLRET] == OK:
                     self.DumpData(ReadBinaryData[DATA], msg='FCP Data:')
                  else:
                     self.trace('Unable to retrieve %s data from the buffer.' % FileID)
               else:
                  self.trace('Invalid Response Length')

      if result[DATA] != GoodStatus:
         objMsg.printMsg(UnexpectedStatus % result)
         objMsg.printMsg('Select File Status = %s' % (self.StatusStrToHexStr(result[DATA])))
         Status = FAIL
      else:
         Status = OK

      return Status


   #  ========================================================================================
   # This routine will call the SelectFile() routine multiple times to walk down through
   # a directory tree to get at a subdirectory file.  Note: For selection, directories and
   # files are treated the same way.
   #    Usage: SelectFileExtd(FileList)
   #    where  FileList is a list containing, in order, the directory names to get to the
   #           file, including the name of the file itself
   #  ========================================================================================
   def SelectFileExtd(self, FileList, CardNum, ReturnFCP='FALSE', useSerialPort=0):

      # Walk through the file chain, finally selecting the file itself
      Status = OK
      for file in FileList:
         Status = self.SelectFile(file, CardNum, ReturnFCP, useSerialPort)
         if Status == FAIL:
            break

      return Status


   #  ========================================================================================
   #  Perform an UpdateBinary command
   #  ========================================================================================
   def UpdateBinary(self, Data, Offset=0, CardNum=ADMIN, ReportStatus=FALSE, useSerialPort=0):

      # Build the APDU for Update Binary
      # Note:Data length must be limited to 256 bytes
      if Data:
         NumberOfBytes = len(Data)
      else:
         NumberOfBytes = 0

      APDUList = [Offset >> 8 & 0xFF, Offset & 0xFF, NumberOfBytes]
      if Data:
         for byte in Data:
            APDUList.append(byte)

      if NumberOfBytes > 256:   # Check for invalid Data length
         result = {}
         result[LLRET] = FAIL
         result[DATA] = 'Too Many Bytes in Data List'
         self.DumpData(APDUList, 3, 10, len(APDUList), 'APDU List with Data')
      else:
         UpdateBinary = self.BuildApdu(UPDATEBINARY, APDUList, CardNum)
         if DEBUG_DISPLAY_UPDATE_BINARY_DATA:
            self.DumpData(UpdateBinary, 3, 10, len(UpdateBinary), 'Update Binary APDU with Data')

         if DEBUG_REPORT_SENDING_UPDATE_BINARY:
            self.trace('Sending Update Binary')

         result = self.ExecuteSeaCosCmd(Apdu=UpdateBinary, useSerialPort=useSerialPort)      # Issue the Update Binary command

         if result[LLRET] == OK and (ReportStatus or result[DATA] != GoodStatus):
            objMsg.printMsg('Update Binary status = %s' % self.StatusStrToHexStr(result[DATA]))

      if result[DATA] != GoodStatus:
         objMsg.printMsg(UnexpectedStatus % result)
         objMsg.printMsg('UpdateBinary Status = %s' % (self.StatusStrToHexStr(result[DATA])))
         Status = FAIL
      else:
         Status = OK

      return Status


   #  ========================================================================================
   #  Perform an UpdateBinaryDeviceFile command
   #  ========================================================================================
   def UpdateBinaryDeviceFile(self, Data, Offset=0, CardNum=ADMIN):

      # Build the APDU for Update Binary Device File
      NumberOfBytes = len(Data)

      APDUList = [Offset >> 8 & 0xFF, Offset & 0xFF, NumberOfBytes]
      for byte in Data:
         APDUList.append(byte)

      UpdateBinaryDevice = self.BuildApdu(UPDATEBINARYDEVICEFILE, APDUList, CardNum)
      if DEBUG_DISPLAY_UPDATE_BINARY_DATA:
         self.DumpData(UpdateBinaryDevice, 3, 10, len(UpdateBinaryDevice), 'Update BinaryDevice APDU with Data')

      result = self.ExecuteSeaCosCmd(UpdateBinaryDevice)      # Issue the UpdateBinaryDeviceFile command

      if result[DATA] != GoodStatus:
         if result[DATA] == '\x62\x00':
            objMsg.printMsg("**WARNING** - Status indicates potential Serial-Port Security Issue!! - Ignoring")
            Status = OK
         else:
            objMsg.printMsg(UnexpectedStatus % result)
            objMsg.printMsg('UpdateBinaryDevice Status = %s' % (self.StatusStrToHexStr(result[DATA])))
            Status = FAIL
      else:
         Status = OK

      return Status


   #  ========================================================================================
   #  Update the specified record number with the specified data
   #  ========================================================================================
   def UpdateRecord(self, RecNum, Data, CardNum=ADMIN, Mode=ABS_CURR_RECORD_MODE):

      NumberOfBytes = len(Data)   # Note:Data length must be limited to 256 bytes
      APDUList = [RecNum,Mode,NumberOfBytes]
      for byte in Data:
         APDUList.append(byte)

      UpdateRecord = self.BuildApdu(UPDATERECORD, APDUList, CardNum)
      if DEBUG_DISPLAY_APDU:
         self.trace('APDUList = %s' % APDUList)
         self.DumpData(UpdateRecord, 3, 10, len(UpdateRecord), 'Update Record APDU')

      self.trace('Sending Update Record')
      result = self.ExecuteSeaCosCmd(UpdateRecord)   # Issue the Update Record command

      if result[DATA] != GoodStatus:
         objMsg.printMsg(UnexpectedStatus % result)
         objMsg.printMsg('Update Record Status = %s' % (self.StatusStrToHexStr(result[DATA])))
         Status = FAIL
      else:
         Status = OK

      return Status


   #  ========================================================================================
   #  Read the specified number of bytes at the specified offset on the specified card
   #  ========================================================================================
   def ReadBinary(self, NumberOfBytes, Offset=0, CardNum=ADMIN):

      ReadBinary = self.BuildApdu(READBINARY, [Offset >> 8 & 0xFF, Offset & 0xFF,NumberOfBytes], CardNum)
      if DEBUG_DISPLAY_APDU:
         self.DumpData(ReadBinary, 3, 10, len(ReadBinary), 'Read Binary APDU')

      self.trace('Sending Read Binary')
      result = self.ExecuteSeaCosCmd(ReadBinary)   # Issue the Read Binary command

      if result[LLRET] == OK:
         if result[DATA] != GoodStatus:       # display the status only if it's no good
            objMsg.printMsg('Read Binary status = %s' % self.StatusStrToHexStr(result[DATA]))
         elif DEBUG_VERIFY_DATA:
            response_length = self.GetResponseLength()
            if response_length != -1:
               ReadBinaryData = self.GetSeaCosData(offset=10, bytes=response_length-2)
               if ReadBinaryData[LLRET] == OK:
                  self.DumpData(ReadBinaryData[DATA], 3, 10, len(ReadBinaryData[DATA]), msg='Read Binary Data :')
               else:
                  self.trace('Unable to retrieve data from the buffer.')
            else:
               self.trace('Invalid Response Length')

      if result[DATA] != GoodStatus:
         objMsg.printMsg(UnexpectedStatus % result)
         objMsg.printMsg('ReadBinary Status = %s' % (self.StatusStrToHexStr(result[DATA])))
         Status = FAIL
      else:
         Status = OK

      return Status


   #  ========================================================================================
   #  Read the specified record on the specified card
   #  ========================================================================================
   def ReadRecord(self, RecordNum, Mode, RecordLength, CardNum=ADMIN):

      ReadRecord = self.BuildApdu(READRECORD, [RecordNum, Mode, RecordLength], CardNum)
      if DEBUG_DISPLAY_APDU:
         self.DumpData(ReadRecord, 3, 10, len(ReadRecord), 'Read Record APDU')

      self.trace('Sending Read Record for record %d' % RecordNum)
      result = self.ExecuteSeaCosCmd(ReadRecord)   # Issue the Read Binary command

      Status = OK
      if result[LLRET] == OK:
         if result[DATA] != GoodStatus:
            Status = FAIL
            objMsg.printMsg('Read Record status = %s' % self.StatusStrToHexStr(result[DATA]))
         else:
            response_length = self.GetResponseLength()
            if response_length != -1:
               results = self.GetSeaCosData(offset=10, bytes=response_length-2)
               if results[LLRET] == OK:
                  self.DumpData(results[DATA], msg='Read Record Data :')
               else:
                  self.trace('Unable to retrieve data from the buffer.')
                  Status = FAIL  # Command Unsuccessful
            else:
               self.trace('Invalid Response Length')
               Status = FAIL  # Invalid data length

      return Status


   #  ========================================================================================
   #  Authenticate the specified element on the specified card
   #  ========================================================================================
   def Authenticate(self, KeyType="Default", CardNum=ADMIN, Auth="KCI", useSerialPort=0, Secret=None):

      Status = OK  # Initialize Status so it can be checked against later

      result = self.GetChallenge(CardNum,useSerialPort)      # Send the Get Challenge command
      if result[LLRET] == OK:
         if result[DATA] == GoodStatus and not self.DefaultData or KeyType=="SPEK":
            if not useSerialPort:     # Going throuth the interface
               response_length = self.GetResponseLength()  # Get the SeaCos data from the Get Challenge command
               if response_length != -1:
                  result = self.GetSeaCosData(offset=10, bytes=response_length-2)
                  if result[LLRET] == OK:
                     EncodedNonce = base64.encodestring(result[DATA])
                     if DEBUG_DISPLAY_NONCE_INFO:
                        self.DumpData(result[DATA], 3, 8, msg='Challenge result')
                  else:
                     self.trace('%s : Failed to get data from buffer' % ErrStr)
                     Status = FAIL  # Command Unsuccessful
               else:
                  self.trace('%s : Invalid Response Length' % ErrStr)
                  Status = FAIL  # Invalid data length
            else:                    # Going through the Serial Port
               EncodedNonce = base64.encodestring(result['CHALLENGE'])

         elif result[DATA] != GoodStatus:
            objMsg.printMsg(UnexpectedStatus % result)
            Status = FAIL     # Unexpected command status in data field
      else:
         self.trace('%s : Bad Status from Get Challenge' % ErrStr)
         Status = FAIL

      objMsg.printMsg("Getting Authentication........")
      if KeyType == "SPEK":
         KeyRef = 0x9E       # SPEK Key Reference
      elif KeyType == "USER":
         KeyRef = 0x11     # User Card Key Reference
      else:
         KeyRef = 0x9F                       # MFG Key Reference
      if not self.DefaultData and KeyType == "SPEK":   # If authenticating against the (M2TD or CODY) Serial Port Unlock Key
         if Auth != "KCI": # Get authentication from Host
            method,prms = RequestService('EncryptResponse',(base64.encodestring(SERIAL_ENABLE_3DES_KEY),EncodedNonce))
            if len(prms) != 0:  # Host responses don't have the 'EC' key
               Response_str = base64.decodestring(prms)
               if DEBUG_DISPLAY_NONCE_INFO:
                  self.DumpData(Response_str, 3, 8, msg = 'Gemini SPEK Authentication Response')
            else:
               objMsg.printMsg("%s : Can't get SPEK Authentication data from Host" % ErrStr)                       # Error condition
               Status = FAIL
         else:             # Get authentication from KCI server
            method,prms = RequestService('ReqSPEAuth',(EncodedNonce, HDASerialNumber))
            if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
               if prms.has_key('AuthenticationResponse'):
                  Response_str = base64.decodestring(prms['AuthenticationResponse'])
                  if DEBUG_DISPLAY_NONCE_INFO:
                     self.DumpData(Response_str, 3, 8, msg = 'KCI SPEK Authentication Response')
               else:
                  objMsg.printMsg("%s : Can't get KCI SPEK Authentication data, Invalid dictionary key" % ErrStr)  # Error condition
                  Status = FAIL
            else:
               Status = FAIL
               objMsg.printMsg("%s : %s (%d)" % (ErrStr,prms.get('EC',(12383,'Default'))[1],prms.get('EC',(12383,'Default'))[0])) # Error from KCI server
               #failcode['Fin Kwai Prep'] = ('KCISrv',prms.get('EC',(12383,'Default'))[0])
               ScrCmds.raiseException(prms.get('EC',(12383,'Default'))[0], "Kwai Prep Failed")
      elif self.DefaultData and KeyType == "SPEK":      # If authenticating against the (E*) Serial Port Unlock Key
         method,prms = RequestService('EncryptResponse',(base64.encodestring(SERIAL_ENABLE_3DES_KEY),EncodedNonce))
         if len(prms):
            Response_str = base64.decodestring(prms)
         else:
            objMsg.printMsg("%s : Can't get Authentication Response from Host" % ErrStr)     # Error condition
            Status = FAIL
      elif KeyType == "USER":      # If authenticating against the USER Card, then provide the secret (PIN)
         method,prms = RequestService('EncryptResponse',(base64.encodestring(Secret),EncodedNonce))
         if len(prms):
            Response_str = base64.decodestring(prms)
         else:
            objMsg.printMsg("%s : Can't get Authentication Response from Host" % ErrStr)     # Error condition
            Status = FAIL
      elif not self.DefaultData and KeyType != "Default":        #  If Authenticating against the Manufacturing Key
      # NOTE: the PRODUCTION KCI server doesn't support the 'default' MANUFACTURING key at this time (the STAGING server does).
   #      if KeyType == "Default":
   #         method,prms = RequestService('ReqMfgAuth',(EncodedNonce,))                  # SN field empty for Default Manufacturing Key
   #      else:
         method,prms = RequestService('ReqMfgAuth',(EncodedNonce, HDASerialNumber))  # Provide SN for Drive Unique Manufacturing Key
         if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
            if prms.has_key('AuthenticationResponse'):
               Response_str = base64.decodestring(prms['AuthenticationResponse'])
               if DEBUG_DISPLAY_NONCE_INFO:
                  self.DumpData(Response_str, 3, 8, msg = 'KCI Authentication Response')
            else:
               objMsg.printMsg("%s : Can't get Manufacturing Key Authentication data, Invalid dictionary key" % ErrStr)      # Error condition
               Status = FAIL
         else:
            Status = FAIL
            objMsg.printMsg("%s : %s (%d)" % (ErrStr,prms.get('EC',(12383,'Default'))[1],prms.get('EC',(12383,'Default'))[0])) # Error from KCI server
            #failcode['Fin Kwai Prep'] = ('KCISrv',prms.get('EC',(12383,'Default'))[0])
            ScrCmds.raiseException(prms.get('EC',(12383,'Default'))[0], "Kwai Prep Failed")
      else:
         Response_str = '\x54\xE5\xA1\xC7\x51\xE3\xF3\xC9'    # This is the "default" MANUFACTURING key authentication response.

      if Status != FAIL:
         Response = []
         for element in Response_str:
            Response.append(ord(element))

         result = self.ExtAuthenticate(Response, CardNum, KeyRef, useSerialPort)
         if result[DATA] != GoodStatus:
            objMsg.printMsg(UnexpectedStatus % result)             # Error condition
            Status = FAIL

      return (Status)


   #  ========================================================================================
   #  Issue a Card using the developer IssueCard APDU
   #  ========================================================================================
   def IssueCard(self, Pin, CardType=ISSUE_FDE_CARD, SerialNumber=[1,2,3,4,5,6,7,5], XFSpace=128*1024*1024, CardNum=ADMIN):
      # NOTE: The CODY SeaCos F/W expects the XF space to be in *bytes*, and the M2TD SeaCos F/W expects the XF space in sectors !!!!!!!
      if self.XF_SECTORS:                      # If XF space specified in SECTORS (I.E. M2TD)
         XFSpace = XFSpace/1024           # then calculate the number of SECTORS needed - otherwise, it's in bytes

      P2 = 0
      IssueCardData = SerialNumber + [(XFSpace & 0xFF000000) >> 24,
                                       (XFSpace & 0x00FF0000) >> 16,
                                       (XFSpace & 0x0000FF00) >>  8,
                                       (XFSpace & 0x000000FF)]
      if Pin:
         issuecard = self.BuildApdu(ISSUECARD, [CardType, P2, len(IssueCardData+Pin)] + IssueCardData + Pin, CardNum)
      else:
         issuecard = self.BuildApdu(ISSUECARD, [CardType, P2, len(IssueCardData)] + IssueCardData, CardNum)

      if DEBUG_DISPLAY_APDU:
         self.DumpData(issuecard, 3, 10, len(issuecard), 'Issue Card APDU')

      objMsg.printMsg('Sending Issue Card for Card Type 0x%02x' % CardType)
      result = self.ExecuteSeaCosCmd(issuecard)    # Execute the IssueCard command

      if result[LLRET] == OK:                 # If the command completed, display the status
         if result[DATA] == GoodStatus:
            response_length = self.GetResponseLength()
            if response_length != -1:
               results = self.GetSeaCosData(offset=10, bytes=response_length-2)
               if results[LLRET] != OK:
                  self.trace('Unable to retrieve data from the buffer.')
               else:
                  CardNum = int(self.StatusStrToHexStr(results[DATA]),16)
                  objMsg.printMsg('Card# = %d' % CardNum)  # Card number is returned
            else:
               self.trace('Invalid Response Length')
      else:
         CardNum = 0

      if result[DATA] != GoodStatus:
         objMsg.printMsg(UnexpectedStatus % result)
         objMsg.printMsg('Issue Card status = %s' % self.StatusStrToHexStr(result[DATA]))
         Status = FAIL
      else:
         Status = OK

      return (Status,CardNum)


   #  ========================================================================================
   # Prepare the drive for Recovery Erase
   #  ========================================================================================
   def RecoveryErasePrepare(self, CardNum, mSID):

      Nonce = Status = 0
      state = GoodStatus
      ApduDataList = [0,0,len(mSID)] + mSID + [0x08]
      Recover = self.BuildApdu(RECOVERYERASEPREPARE, ApduDataList, CardNum)
      if DEBUG_DISPLAY_APDU:
         self.DumpData(Recover, 3, 10, len(Recover), 'Recovery Erase Prepare APDU')

      result = self.ExecuteSeaCosCmd(Recover)      # Issue the command

      if result[LLRET] == OK:                 # If the command completed, display the status
         if result[DATA] == GoodStatus or result[DATA] == '\x65\x81':
            response_length = self.GetResponseLength()
            if response_length != -1:
               data = self.GetSeaCosData(offset=10, bytes=response_length)
               if data[LLRET] == OK:
                  Nonce = data[DATA][:-2]     # random data
                  state = data[DATA][-2:]     # followed by 2 bytes of status
                  if result[DATA] == '\x65\x81':
                     Status = 0x6581
            else:
               self.trace('Invalid Response Length')
         elif result[DATA] == '\x6F\x00':
            objMsg.printMsg('This feature is not supported by the Firmware!') # Older versions of F/W do not support this
            Status = FAIL

      if state != GoodStatus and Nonce == 0:
         objMsg.printMsg('Erase Prep status = %s' % self.StatusStrToHexStr(result[DATA]))
         Status = FAIL
      elif Status != 0x6581 and result[DATA] != '\x6F\x00':    # x6581 = "Memory Problem" (I.E. disc error); x6F00 = "Unknown"
         Status = OK

      return Status,Nonce

   #  ========================================================================================
   # Prepare the drive for Recovery Erase
   #  ========================================================================================
   def RecoveryErase(self, CardNum, NonceList):

      ApduDataList = [0, 0, len(NonceList)] + NonceList
      Erase = self.BuildApdu(RECOVERYERASE, ApduDataList, CardNum)
      if DEBUG_DISPLAY_APDU:
         self.DumpData(Erase, 3, 10, len(Erase), 'Recovery Erase APDU')

      result = self.ExecuteSeaCosCmd(Erase)        # Issue the command

      # NOTE: Recovery Erase command does *not* return a status !!
      if result[LLRET] == OK:                 # If the command completed, display the status
         Status = OK
      else:
         Status = FAIL

      return Status

   #  ========================================================================================
   # (Debug) dump data to trace log if Card Load failure
   #  ========================================================================================
   def DebugDump(self, card):

      objMsg.printMsg('Attempting Data Dump on Card %d, Primary Copy' % card)
      result = self.DirectCardRead(card,0)
      if result[LLRET] == OK:
         if result[DATA] != GoodStatus:
            objMsg.printMsg(UnexpectedStatus % result)
         else:
            # Get the SeaCos data from the Card Dump command
            response_length = self.GetResponseLength()
            if response_length != -1:
               result = self.GetSeaCosData(offset=0, bytes=response_length+10)
               if result[LLRET] == OK:
                  self.DumpData(result[DATA], 4, 8)

   #  ========================================================================================
   #  ========================================================================================
   #  Main entry into the Kwai Drive Processing -  Called from IntFinal.py
   #  ========================================================================================
   #  ========================================================================================
   def KwaiPrep(self):

      global DEBUG_STEP_TRACE
      Enabled = 0

      objMsg.printMsg ('XF Sector Format before KwaiPrep...')
      self.XFFormat()
      if self.Check_Encryption:      # Note that this *must* be an FDE drive for the Encryption check to work !!
         objMsg.printMsg ('Checking encryption block engine before KwaiPrep...')
         self.EncryptionBlkChk()

      objMsg.printMsg ('KWAI Prep processing drive with flags:')
      if self.DefaultData:
         Msg = 'TRUE'
      else:
         Msg = 'FALSE'
      objMsg.printMsg ('DefaultData: '+Msg)
      objMsg.printMsg ('SID Length: %d Chars'%self.SidLength)
      if self.IssueFDECard:
         Msg = 'TRUE'
      else:
         Msg = 'FALSE'
      objMsg.printMsg ('IssueFDECard: '+Msg)
      if self.PREBOOT:
         Msg = 'TRUE'
      else:
         Msg = 'FALSE'
      objMsg.printMsg ('Pre-Boot: '+Msg)
      #################################################################################################################
      ###### THIS IS A SPECIAL REQUIREMENT..NEED TO DISABLE APM AND DO A SEEK WHEN DOING KWAIPREP, OTHERWISE WILL HAVE
      ###### HIGH FAILURE RATE ON ATA_WAIT_FOR_DRDY
      result = ICmd.SetFeatures(0x85)
      if result['LLRET'] != OK: # if failed to disable APM, don't fail immediately, try to continue
         objMsg.printMsg('Disable Advance Power Management Failed!')
      else:
         objMsg.printMsg('Disable Advance Power Management Pass!')
         result = ICmd.Seek(0)      # Seek to LBA 0
         if result['LLRET'] != OK:
            objMsg.printMsg('Seek cmd Failed!')
         else:
            objMsg.printMsg('Seek cmd Pass!')
      #################################################################################################################
      result = ICmd.SetFeatures(SET_XFER_MODE,DEFAULT_PIO)     # Put the drive in default PIO mode
      if result[LLRET] != OK:
         objMsg.printMsg('Failed SetFeatures - result = %s' % result)
         SeaCosStatus = FAIL
      else:
         CmdDividerLine = '-' * 80
         SeaCosStatus = OK
         objMsg.printMsg(CmdDividerLine)

   #*************************************************************************************************
   #----------------------- Load the File System on to the Drive ------------------------------------
   #*************************************************************************************************

      objMsg.printMsg('Loading File System...')

      if SeaCosStatus == OK:
         result = self.UnlockCards()      # Send Unlock Cards to erase any (all) existing cards
         if result.has_key(DATA) and result[DATA] == '\x69\x86':
            Enabled = 1

   #------- Load  CARD 0x0000 into slot 0 - Admin Card -------------------------------------------------------

         if (result[LLRET] == OK and SeaCosStatus != FAIL):
            SeaCosStatus = self.LoadCard(ADMIN, self.getCardFileName('Admin'),Enabled)
         else:
            SeaCosStatus = FAIL

   #------- Load  CARD 0x0001 into slot 1 - Cryptographic Services Card --------------------------------------

         if SeaCosStatus != FAIL and ( testSwitch.Kwai_CSPCard_Enabled or not testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT ):
            SeaCosStatus = self.LoadCard(CSP, self.getCardFileName('CSC'))

   #------- Load  CARD 0xFFFE into slot 2 - Template Card -----------------------------------------------

         if SeaCosStatus != FAIL:
            SeaCosStatus = self.LoadCard(TEMPLATE, self.getCardFileName('Template'))

   #------- Load  CARD 0x0003 into slot 3 - Drive Features Card --------------------------------------

         if SeaCosStatus != FAIL:
            SeaCosStatus = self.LoadCard(FEATURES, self.getCardFileName('Features'))

   #------- Load  CARD 0x0002 into slot 4 - Full Data Encryption (FDE) Card (only on FDE Drives) -----------

         if SeaCosStatus != FAIL and not self.DefaultData and not self.ATA_Mode:
            SeaCosStatus = self.LoadCard(FDE, self.getCardFileName('FDE'))

   #------- Load  Public Key Table into slot 255 -----------------------------------------------

         if SeaCosStatus != FAIL:
            SeaCosStatus = self.LoadCard(KEYTABLE, self.getCardFileName('Keytable'))

   #------- Set SeaCos to the 'Initialize' state --------------------------------------------

         if SeaCosStatus != FAIL:
            SeaCosStatus = self.InitSeaCos()

         # If this drive requires a User Image, do that before the LBA's get re-mapped.
         if SeaCosStatus != FAIL and self.WRITE_USER_IMAGE:
            objMsg.printMsg('Downloading Image to USER area.')
            SeaCosStatus = self.WriteImage(self.KwaiVars['UserImage'], Select=4)

   #
   # Default Manufacturing Key -> e6 d0 45 92 0e b6 ef ab 3b 34 7f d3 8f d6 cd d3    (04/02/04)
   # Default Manufacturing Key response -> 54 e5 a1 c7 51 e3 f3 c9
   #
   # 1. requestManufacturingKey( String driveSerialNumber )
   #    returns:
   #       a <base64> byte array with the derived drive unique manufacturing key.
   # 2. requestManufacturingAuthentication( Base64 nonce [, String driveSerialNumber] )
   #    returns:
   #       a <base64> byte array with the response to the authentication challenge, using:
   #          - the default manufacturing key if driveSerialNumber is absent or empty, or
   #          - the derived drive unique manufacturing key if driveSerialNumber is present and non-empty.
   #
   # (Excerpts from the GSC spec sections 5.1.2.1 and 5.1.2.2 are below.)
   #
   # The Get Challenge APDU produces an eight byte nonce. The External Authenticate, has to provide the cryptogram (response to challenge),
   # the algorithm identifier, and the key number. From Manuel, I understand that the key number will be zero (default), and SeaCOS will
   # pull the key from the keystore. So that leaves the algorithm.
   # We have a choice here between TripleDES-ECB and TripleDES-CBC. It seems that only the first is supported by SeaCOS.
   #
   # 5.1.2.2 Get Challenge APDU
   # This APDU is used to cause the smart card to generate a cryptographic challenge, e.g., a random number,
   # for use in the subsequent security related procedure such as EXTERNAL AUTHENTICATE. The smart card
   # saves a copy of the challenge internally until the completion of the security related procedure or an error
   # occurs.
   # The challenge is valid only for the next APDU in the same card session.
   # Command Message
   #    Function Code 0x05    CLA 0x00   INS 0x84   P1 0x00   P2 0x00   Lc Empty   Data Field Empty   Le Length in bytes of expected random challenge
   # Response Message
   #    Data Field returned in the Response Message
   #    If the APDU result indicates success, Le number of bytes will be available to read from the smart
   #    card, i.e., the 8-byte challenge.
   #
   # 5.1.2.1 External Authenticate APDU
   # This APDU is used in conjunction with the GET CHALLENGE APDU to authenticate a client application
   # to the smart card. GET CHALLENGE would be issued first to cause the smart card to issue a random
   # number, i.e., the challenge. The client application would encrypt the challenge and send the resultant
   # cryptogram to the smart card via the EXTERNAL AUTHENTICATE APDU. The smart card would then
   # decrypt it using the same algorithm as the client application and compare it to its internally stored copy of
   # the challenge. If the cryptograms match, the client application is authenticated to the smart card. If the
   # cryptograms do not match, the challenge is no longer valid.

   #*************************************************************************************************
   #----------- Default File System Load Complete - Get Drive Unique Manufacturing 3DES Key ---------
   #*************************************************************************************************

      if SeaCosStatus != FAIL:
         if not self.DefaultData:
            objMsg.printMsg('------------ Getting MANUFACTURING key ------------')
            method, prms = RequestService('ReqMfgKey', (HDASerialNumber,))
            if len(prms) and prms.get('EC',(0,'NA'))[0] == 0: #  Make sure that the service completed successfully
               if prms.has_key('manufacturingKey'):
                  #  Extract the key from the data and convert from base64 to binary
                  Manufacturing3DESKeystr = base64.decodestring(prms['manufacturingKey'])

                  Manufacturing3DESKey = []
                  for element in Manufacturing3DESKeystr:
                     Manufacturing3DESKey.append(ord(element))
               else:
                  objMsg.printMsg("%s : Failed to get Manufacturing 3DES Key, Invalid dictionary key" % ErrStr)     # Error condition
                  SeaCosStatus = FAIL
            else:
               SeaCosStatus = FAIL
               objMsg.printMsg("%s : %s (%d)" % (ErrStr,prms.get('EC',(12383,'Default'))[1],prms.get('EC',(12383,'Default'))[0])) # Error from KCI server
               #failcode['Fin Kwai Prep'] = ('KCISrv',prms.get('EC',(12383,'Default'))[0])
               ScrCmds.raiseException(prms.get('EC',(12383,'Default'))[0], "Kwai Prep Failed")
         else:
            objMsg.printMsg("Unique Mfg Key not required.")

   #----------------------------------------------------------------------------------------------------
   #  Perform Get Challenge / External Authenticate Sequence with existing default keys on the CSP card
   #----------------------------------------------------------------------------------------------------
         if testSwitch.Kwai_CSPCard_Enabled or not testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
            if SeaCosStatus != FAIL:
               if DEBUG_STEP_TRACE:
                  objMsg.printMsg('Get Challenge / External Authenticate ...')
               SeaCosStatus = self.Authenticate( "Default", CardNum=CSP )

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 2b: Select the DF-CDE EF-3DES file
   #----------------------------------------------------------------------------------------------------

            if SeaCosStatus != FAIL and not self.DefaultData:
               if DEBUG_STEP_TRACE:
                  self.trace('Loading Mfg Key to CSP Card.....')
               SeaCosStatus = self.SelectFileExtd([MASTER_FILE, DF_CDE, EF_3DES], CardNum=CSP)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 2c: Load the Drive Unique Manufacturing 3DES Key
   #----------------------------------------------------------------------------------------------------

            if SeaCosStatus != FAIL and not self.DefaultData:
               # Load the Drive Unique 3DES Key obtained in an earlier step
               if DEBUG_VERIFY_DATA:
                  SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0, CardNum=CSP)

               if SeaCosStatus != FAIL:
                  SeaCosStatus = self.UpdateBinary(Manufacturing3DESKey, Offset=Manf3DESKeyOffset, CardNum=CSP)

               if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
                  SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0, CardNum=CSP)

            elif SeaCosStatus != FAIL:
               objMsg.printMsg('Mfg Key NOT required for CSP Card.')

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 3a: Send Synchronize Command
   #----------------------------------------------------------------------------------------------------

            if SeaCosStatus != FAIL:
               objMsg.printMsg('Saving Changes.....')
               SeaCosStatus = self.Synchronize(CardNum=CSP)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 3b: Issue a Reset
   # NOTE: A reset will 'de-authenticate', so if this is an EchoStar drive, then
   # skip this step, so that step 4 will work.
   #----------------------------------------------------------------------------------------------------

            if SeaCosStatus != FAIL and not self.DefaultData:
               if DEBUG_STEP_TRACE:
                  self.trace('Reset to CSP Card.....')
               SeaCosStatus = self.WarmReset(CardNum=CSP)

            elif SeaCosStatus != FAIL:
               objMsg.printMsg('No Reset required on CSP Card.')

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 4a: Perform Get Challenge / External Authenticate
   # Sequence with new drive unique 3DES Manufacturing Key
   #----------------------------------------------------------------------------------------------------

            if SeaCosStatus != FAIL:
               objMsg.printMsg("****** Personalize CSP Card (1) ******")

            if SeaCosStatus != FAIL and not self.DefaultData:
               if DEBUG_STEP_TRACE:
                  self.trace('Authenticating.....')
               SeaCosStatus = self.Authenticate( "Unique", CardNum=CSP )
            elif SeaCosStatus != FAIL:
               objMsg.printMsg('No authentication required for CSP Card.')

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 4b: Replace default data in files listed in
   # Table 3 with appropriate data
   #----------------------------------------------------------------------------------------------------

            if SeaCosStatus != FAIL:
               if DEBUG_STEP_TRACE:
                  self.trace('Replacing default data on CSP Card.....')
               SeaCosStatus = self.SelectFileExtd([MASTER_FILE, EF_CCC], CardNum=CSP)

               if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
                  SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0, CardNum=CSP)

               if SeaCosStatus != FAIL:
                  CardID = self.GenerateCardID(CardNum=CSP, RequiresOrgNum=TRUE)
                  SeaCosStatus = self.UpdateBinary(CardID, Offset=CCC_CardIDOffset, CardNum=CSP)

               if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
                  SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0, CardNum=CSP)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 5a: Select the DF-CIA EF-SKDF file
   #----------------------------------------------------------------------------------------------------

            if SeaCosStatus != FAIL:
               objMsg.printMsg('Removing Mfg Key from CSP Card.....')
               SeaCosStatus = self.SelectFileExtd([MASTER_FILE, DF_CIA, EF_SKDF], CardNum=CSP)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 5b: Overwrite key reference 0x9F
   #----------------------------------------------------------------------------------------------------

            if SeaCosStatus != FAIL:
               if DEBUG_STEP_TRACE:
                  self.trace('Overwriting key reference 0x9F on CSP Card.....')
               SeaCosStatus = self.UpdateBinary(self.EF_SKDF_OverwriteData, Offset=0, CardNum=CSP)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 5c: Select the DF-CDE EF-3DES file
   #----------------------------------------------------------------------------------------------------

            if SeaCosStatus != FAIL:
               SeaCosStatus = self.SelectFileExtd([MASTER_FILE, DF_CDE, EF_3DES], CardNum=CSP)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 5d: Overwrite the Manufacturing 3DES key with 0xFF
   #----------------------------------------------------------------------------------------------------

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0x0, CardNum=CSP)

            if SeaCosStatus != FAIL:
               if DEBUG_STEP_TRACE:
                  self.trace('Overwrite Mfg Key on CSP Card.....')
               SeaCosStatus = self.UpdateBinary(PadData[0:InternalManf3DESKeyLen], Offset=Manf3DESKeyOffset, CardNum=CSP)

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0x0, CardNum=CSP)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 6a: Select the EF-ARR file
   #----------------------------------------------------------------------------------------------------

            if SeaCosStatus != FAIL:
               objMsg.printMsg('Customizing ACL on CSP Card.....')
               SeaCosStatus = self.SelectFileExtd([MASTER_FILE, EF_ARR], CardNum=CSP)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 6: Issue Update Record to update Access Rules based
   # on Table 12. NOTE: Record one must be done last as it limits access rights to this file. (EF-ARR)
   #----------------------------------------------------------------------------------------------------

            #  The following Record Data is based on the corresponding information in the
            #  LC_Tests-sec3.pen file as excerpted below:
            #     CARD CARD_NUMBER_CRYPTOGRAPHIC_SERVICES:
            #       UpdateRecord ( 0x02 , ABSOLUTE_RECORD ,
            #                      flatten { FCP_ACL_EXPANDED :
            #                      { ACL_AM_DO : ACL_AM_FILE_ACTIVATE | ACL_AM_FILE_DEACTIVATE  | ACL_AM_FILE_UPDATE },
            #                      { ACL_SC_DO_NEVER : },
            #                      { ACL_AM_DO : ACL_AM_FILE_READ },
            #                      { ACL_SC_DO_ALWAYS : }
            #                      } )

            #  Set record content for EF-CCC Rules
            if SeaCosStatus != FAIL:
               if DEBUG_STEP_TRACE:
                  self.trace('Updating Record 2.....')
               RecNumber = 2
               RecordData = [0xAB, 0x0A, 0x80, 0x01, 0x1A, 0x97, 0x00, 0x80, 0x01, 0x01, 0x90, 0x00]
               SeaCosStatus = self.UpdateRecord(RecNumber, RecordData, CardNum=CSP, Mode=ABS_CURR_RECORD_MODE)

            #  The following Record Data is based on the corresponding information in the
            #  LC_Tests-sec3.pen file as excerpted below:
            #     CARD CARD_NUMBER_CRYPTOGRAPHIC_SERVICES:
            #       UpdateRecord ( 0x03 , ABSOLUTE_RECORD ,
            #                      flatten { FCP_ACL_EXPANDED :
            #                      { ACL_AM_DO : ACL_AM_FILE_ACTIVATE | ACL_AM_FILE_DEACTIVATE },
            #                      { ACL_SC_DO_NEVER : },
            #                      { ACL_AM_DO : ACL_AM_FILE_READ },
            #                      { ACL_SC_DO_ALWAYS : },
            #                      { ACL_AM_DO : ACL_AM_FILE_UPDATE },
            #                      { ACL_SC_DO :
            #                      { ACL_SC_KEY_REFERENCE : KEYREF_PIN1 }
            #                      }
            #                      } )

            #  Set Record Content for EF-SKDF Access Rules
            if SeaCosStatus != FAIL:
               if DEBUG_STEP_TRACE:
                  self.trace('Updating Record 3.....')
               RecNumber = 3
               RecordData = [0xAB, 0x12, 0x80, 0x01, 0x18, 0x97, 0x00, 0x80, 0x01, 0x01,\
                                 0x90, 0x00, 0x80, 0x01, 0x02, 0xA4, 0x03, 0x83, 0x01, 0x01]
               SeaCosStatus = self.UpdateRecord(RecNumber, RecordData, CardNum=CSP, Mode=ABS_CURR_RECORD_MODE)

            #  The following Record Data is based on the corresponding information in the
            #  LC_Tests-sec3.pen file as excerpted below:
            #     CARD CARD_NUMBER_CRYPTOGRAPHIC_SERVICES:
            #       UpdateRecord ( 0x01 , ABSOLUTE_RECORD ,
            #                      flatten { FCP_ACL_EXPANDED :
            #                       { ACL_AM_DO : ACL_AM_FILE_ACTIVATE | ACL_AM_FILE_DEACTIVATE  | ACL_AM_FILE_UPDATE | ACL_AM_FILE_READ },
            #                       { ACL_SC_DO_NEVER : }
            #                       } )

            #  Set Record Content for EF-ARR and EF-3DES Access Rules
            if SeaCosStatus != FAIL:
               if DEBUG_STEP_TRACE:
                  self.trace('Updating Record 1.....')
               RecNumber = 1
               RecordData = [0xAB, 0x05, 0x80, 0x01, 0x1B, 0x97, 0x00]
               SeaCosStatus = self.UpdateRecord(RecNumber, RecordData, CardNum=CSP, Mode=ABS_CURR_RECORD_MODE)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 7a: Send Synchronize Command
   #----------------------------------------------------------------------------------------------------

            if SeaCosStatus != FAIL:
               objMsg.printMsg('Saving CSP Card Changes.....')
               SeaCosStatus = self.Synchronize(CardNum=CSP)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 7b: Issue Warm Reset
   #----------------------------------------------------------------------------------------------------

            if SeaCosStatus != FAIL:
               if DEBUG_STEP_TRACE:
                  self.trace('Reset to CSP Card.....')
               SeaCosStatus = self.WarmReset(CardNum=CSP)

            if SeaCosStatus != FAIL:
               objMsg.printMsg("****** Personalization of CSP Card complete ******")

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8a: Perform Get Challenge / External Authenticate
   # Sequence with existing default keys on Drive Features Card (3)
   #---------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            objMsg.printMsg("****** Personalize Drive Features Card (3) ******")
            if DEBUG_STEP_TRACE:
               objMsg.printMsg('Get Challenge / External Authenticate.....')
            SeaCosStatus = self.Authenticate( "Default", CardNum=FEATURES )

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8b: Select the DF-CDE EF-3DES file
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, DF_CDE, EF_3DES], CardNum=FEATURES)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8c: Load the Drive Unique Manufacturing 3DES Key
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL and not self.DefaultData:
            if DEBUG_STEP_TRACE:
               self.trace('Loading Mfg Key to Drive Features Card.....')
            if DEBUG_VERIFY_DATA:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0, CardNum=FEATURES)

            if SeaCosStatus != FAIL:
               SeaCosStatus = self.UpdateBinary(Manufacturing3DESKey, Offset=Manf3DESKeyOffset, CardNum=FEATURES)

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0, CardNum=FEATURES)

         elif SeaCosStatus != FAIL:
            objMsg.printMsg('No Mfg Key required for Card 3.')

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8d: Send Synchronize Command
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Saving Changes to Drive Features Card.....')
            SeaCosStatus = self.Synchronize(CardNum=FEATURES)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8e: Issue a Reset
   # NOTE: A reset will 'de-authenticate', so if this is an EchoStar drive, then
   # skip this step, so that step 10 will work.
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL and not self.DefaultData:
            if DEBUG_STEP_TRACE:
               self.trace('Reset to Drive Features Card.....')
            SeaCosStatus = self.WarmReset(CardNum=FEATURES)

         elif SeaCosStatus != FAIL:
            objMsg.printMsg('Reset skipped for Drive Features Card.')

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8f: Perform Get Challenge / External Authenticate
   # Sequence with new drive unique 3DES Manufacturing Key
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL and not self.DefaultData:
            if DEBUG_STEP_TRACE:
               self.trace('Autenticating Mfg Key.....')
            SeaCosStatus = self.Authenticate( "Unique", CardNum=FEATURES )
         elif SeaCosStatus != FAIL:
            objMsg.printMsg('No Authentication required for Drive Features Card.')

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8g: Replace default data in files listed in
   # Table 3 with appropriate data
   #----------------------------------------------------------------------------------------------------
         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Replacing Default Data on Drive Features Card.....')
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, EF_CCC], CardNum=FEATURES)

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0, CardNum=FEATURES)

            if SeaCosStatus != FAIL:
               objMsg.printMsg('HDASerialNumber = %s' % HDASerialNumber)
               CardID = self.GenerateCardID(CardNum=FEATURES, RequiresOrgNum=TRUE)
               SeaCosStatus = self.UpdateBinary(CardID, Offset=CCC_CardIDOffset, CardNum=FEATURES)

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0, CardNum=FEATURES)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8h: Select the DF-CIA EF-SKDF file
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, DF_CIA, EF_SKDF], CardNum=FEATURES)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8i: Overwrite key reference 0x9F
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Overwriting Key Reference 0x9F on Drive Features Card.....')
            SeaCosStatus = self.UpdateBinary(self.EF_SKDF_Card3OverData, Offset=0, CardNum=FEATURES)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8j: Select the DF-CDE EF-3DES file
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, DF_CDE, EF_3DES], CardNum=FEATURES)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8k: Overwrite the Manufacturing 3DES key with 0xFF
   #----------------------------------------------------------------------------------------------------

         if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
            SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0x0, CardNum=FEATURES)

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Overwriting Mfg Key on Drive Features Card.....')
            SeaCosStatus = self.UpdateBinary(PadData[0:InternalManf3DESKeyLen], Offset=Manf3DESKeyOffset, CardNum=FEATURES)

         if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
            SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0x0, CardNum=FEATURES)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8l: Select the EF-ARR file
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Updating Access Rules on Drive Features Card.....')
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, EF_ARR], CardNum=FEATURES)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8m: Issue Update Record to update Access Rules based
   # on Table 12. NOTE: Record one must be done last as it limits access rights to this file. (EF-ARR)
   #----------------------------------------------------------------------------------------------------

         #  The following Record Data is based on the corresponding information in the
         #  LC_Tests-sec3.pen file as excerpted below:
         #     CARD CARD_NUMBER_DRIVE_FEATURES:
         #       UpdateRecord ( 0x02 , ABSOLUTE_RECORD ,
         #                      flatten { FCP_ACL_EXPANDED :
         #                      { ACL_AM_DO : ACL_AM_FILE_ACTIVATE | ACL_AM_FILE_DEACTIVATE  | ACL_AM_FILE_UPDATE },
         #                      { ACL_SC_DO_NEVER : },
         #                      { ACL_AM_DO : ACL_AM_FILE_READ },
         #                      { ACL_SC_DO_ALWAYS : }
         #                      } )

         #  Set record content for EF-CCC Rules
         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Updating Record 2.....')
            RecNumber = 2
            RecordData = [0xAB, 0x0A, 0x80, 0x01, 0x1A, 0x97, 0x00, 0x80, 0x01, 0x01, 0x90, 0x00]
            SeaCosStatus = self.UpdateRecord(RecNumber, RecordData, CardNum=FEATURES, Mode=ABS_CURR_RECORD_MODE)

         #  The following Record Data is based on the corresponding information in the
         #  LC_Tests-sec3.pen file as excerpted below:
         #     CARD CARD_NUMBER_DRIVE_FEATURES:
         #       UpdateRecord ( 0x03 , ABSOLUTE_RECORD ,
         #                      flatten { FCP_ACL_EXPANDED :
         #                      { ACL_AM_DO : ACL_AM_FILE_ACTIVATE | ACL_AM_FILE_DEACTIVATE },
         #                      { ACL_SC_DO_NEVER : },
         #                      { ACL_AM_DO : ACL_AM_FILE_READ | ACL_AM_FILE_UPDATE },
         #                      { ACL_SC_DO_ALWAYS : }
         #                      }
         #                      } )
         #  Use Default Values for EF-SKDF Access Rules for Record #3


         #  The following Record Data is based on the corresponding information in the
         #  LC_Tests-sec3.pen file as excerpted below:
         #     CARD CARD_NUMBER_DRIVE_FEATURES:
         #       UpdateRecord ( 0x04 , ABSOLUTE_RECORD ,
         #                      flatten { FCP_ACL_EXPANDED :
         #                      { ACL_AM_DO : ACL_AM_FILE_ACTIVATE | ACL_AM_FILE_DEACTIVATE },
         #                      { ACL_SC_DO_NEVER : },
         #                      { ACL_AM_DO : ACL_AM_FILE_UPDATE },
         #                      { ACL_SC_DO_ALWAYS : },
         #                      { ACL_AM_DO : ACL_AM_FILE_READ },
         #                      { ACL_SC_DO :
         #                      { ACL_SC_KEY_REFERENCE : KEYREF_MASTER }
         #                      }
         #                      } )
         #  Use Default Values for EF-SKDF Access Rules for Record #4


         #  The following Record Data is based on the corresponding information in the
         #  LC_Tests-sec3.pen file as excerpted below:
         #     CARD CARD_NUMBER_DRIVE_FEATURES:
         #       UpdateRecord ( 0x01 , ABSOLUTE_RECORD ,
         #                      flatten { FCP_ACL_EXPANDED :
         #                       { ACL_AM_DO : ACL_AM_FILE_ACTIVATE | ACL_AM_FILE_DEACTIVATE  | ACL_AM_FILE_UPDATE | ACL_AM_FILE_READ },
         #                       { ACL_SC_DO_NEVER : }
         #                       } )

         #  Set Record Content for EF-ARR and EF-3DES Access Rules
         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Updating Record 1.....')
            RecNumber = 1
            RecordData = [0xAB, 0x05, 0x80, 0x01, 0x1B, 0x97, 0x00]
            SeaCosStatus = self.UpdateRecord(RecNumber, RecordData, CardNum=FEATURES, Mode=ABS_CURR_RECORD_MODE)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8o: Send Synchronize Command
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            objMsg.printMsg('Saving Changes to Drive Features Card.....')
            SeaCosStatus = self.Synchronize(CardNum=FEATURES)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 8p: Issue Warm Reset
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Reset to Drive Features Card.....')
            SeaCosStatus = self.WarmReset(CardNum=FEATURES)

         if SeaCosStatus != FAIL:
            objMsg.printMsg("****** Personalization of Drive Features Card complete ******")

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 9a: Perform Get Challenge / External Authenticate on
   # the Admin Card against the Default 3DES Manufacturing Key
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            objMsg.printMsg('****** Personalize Admin Card (0) ******')
            if DEBUG_STEP_TRACE:
               self.trace('Get Challenge / External Authenticate')
            SeaCosStatus = self.Authenticate( "Default", CardNum=ADMIN )

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 9b: Select the DF-CDE EF-3DES file
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, DF_CDE, EF_3DES], CardNum=ADMIN)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 9c: Load the Drive Unique Manufacturing 3DES Key
   #----------------------------------------------------------------------------------------------------

         if not self.DefaultData:
            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0, CardNum=ADMIN)

            if SeaCosStatus != FAIL:
               if DEBUG_STEP_TRACE:
                  self.trace('Loading Mfg 3DES Key to Admin Card.....')
               SeaCosStatus = self.UpdateBinary(Manufacturing3DESKey, Offset=Manf3DESKeyOffset, CardNum=ADMIN)

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0, CardNum=ADMIN)

         elif SeaCosStatus != FAIL:
            objMsg.printMsg('No Mfg Key required for Admin Card')

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 10a: Send Synchronize Command
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            objMsg.printMsg('Saving Changes to Admin Card.....')
            SeaCosStatus = self.Synchronize(CardNum=ADMIN)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 10b: Issue Warm Reset
   # NOTE: A reset will 'de-authenticate', so if this is an EchoStar drive, then
   # skip this step, so that step 11b will work.
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL and not self.DefaultData:
            if DEBUG_STEP_TRACE:
               self.trace('Reset to Admin Card.....')
            SeaCosStatus = self.WarmReset(CardNum=ADMIN)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 11a: Perform Get Challenge / External Authenticate
   # Sequence with new drive unique 3DES Manufacturing Key
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL and not self.DefaultData:
            if DEBUG_STEP_TRACE:
               self.trace('Get Challenge / External Authenticate.....')
            SeaCosStatus = self.Authenticate( "Unique", CardNum=ADMIN )
         elif SeaCosStatus != FAIL:
            objMsg.printMsg('No authentication required for Admin Card.')

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 11b: Replace default data in files listed in
   # Table 2 with appropriate data
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Replacing Default Data on Admin Card.....')
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, EF_CCC], CardNum=ADMIN)

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0, CardNum=ADMIN)

            if SeaCosStatus != FAIL:
               CardID = self.GenerateCardID(CardNum=ADMIN, RequiresOrgNum=TRUE)
               SeaCosStatus = self.UpdateBinary(CardID, Offset=CCC_CardIDOffset, CardNum=ADMIN)

               if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
                  SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0, CardNum=ADMIN)

         # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

         if SeaCosStatus != FAIL:
            SeaCosStatus = self.SelectFile(EF_CARD_STATUS, CardNum=ADMIN)        # Master file already in path, select EF_CARD_STATUS

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadRecord(RecordNum=1, Mode=ABS_CURR_RECORD_MODE, RecordLength=0x0E, CardNum=ADMIN)

            if SeaCosStatus != FAIL:
               if DEBUG_STEP_TRACE:
                  self.trace('Updating Record 1.....')
               #  Build the record 1 data for the Admin card (card 0)
               RecNumber = 1
               ADMIN_CARD_NUM = [0x00, 0x00]   # Binary data must be in little endian format
               IN_USE_STATUS  = [0x01, 0x00]   # little endian format - OPERATIONAL - IN USE
               CARD_ID = self.GenerateCardID(ADMIN,FALSE)
               RecordData = ADMIN_CARD_NUM + IN_USE_STATUS + CARD_ID + CCC_OrgNum

               SeaCosStatus = self.UpdateRecord(RecNumber, RecordData, CardNum=ADMIN, Mode=ABS_CURR_RECORD_MODE)
               if SeaCosStatus != FAIL:
                  if DEBUG_VERIFY_DATA:
                     SeaCosStatus = self.ReadRecord(RecordNum=1, Mode=ABS_CURR_RECORD_MODE, RecordLength=0x0E, CardNum=ADMIN)
                     if SeaCosStatus != FAIL:
                        SeaCosStatus = self.ReadRecord(RecordNum=2, Mode=ABS_CURR_RECORD_MODE, RecordLength=0x0E, CardNum=ADMIN)

                  if SeaCosStatus != FAIL:
                     if DEBUG_STEP_TRACE:
                        self.trace('Updating Record 2.....')
                     #  Build the record 2 data for the Admin card (card 0)
                     RecNumber = 2
                     CPS_CARD_NUM = [0x01, 0x00]   # Binary data must be in little endian format
                     RESERVED_STATUS  = [0x20, 0x00]
                     if testSwitch.Kwai_CSPCard_Enabled or not testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
                        RecordData = CPS_CARD_NUM + IN_USE_STATUS + self.GenerateCardID(CSP,FALSE) + CCC_OrgNum
                     else:
                        RecordData = CPS_CARD_NUM + RESERVED_STATUS + self.GenerateCardID(CSP,FALSE) + CCC_OrgNum
                     SeaCosStatus = self.UpdateRecord(RecNumber, RecordData, CardNum=ADMIN, Mode=ABS_CURR_RECORD_MODE)

                     if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
                        SeaCosStatus = self.ReadRecord(RecordNum=2, Mode=ABS_CURR_RECORD_MODE, RecordLength=0x0E, CardNum=ADMIN)

                     if SeaCosStatus != FAIL:
                        if DEBUG_STEP_TRACE:
                           self.trace('Updating Record 4.....')
                        #  Build the record 4 data - Drive Features Card
                        RecNumber = 4
                        CARD_ID = self.GenerateCardID(FEATURES,FALSE)
                        DRIVE_FEATURES_CARD = [0x03, 0x00]   # Binary data must be in little endian format
                        RecordData = DRIVE_FEATURES_CARD + IN_USE_STATUS + CARD_ID + CCC_OrgNum
                        SeaCosStatus = self.UpdateRecord(RecNumber, RecordData, CardNum=ADMIN)

                     # If this is an "ATA Mode" drive, then prevent the FDE card from being issued!
                     # Replace the Card Numbers of the template and FDE card with FF,FF (Invalid)
                     # for card slots 0xFD, and 0x02.
                     if self.ATA_Mode and SeaCosStatus != FAIL:
                        if DEBUG_STEP_TRACE:
                           self.trace('Updating Record 5.....')
                        RecordData = [0xFF,0xFF] + IN_USE_STATUS + self.GenerateCardID(0xFD,FALSE) + CCC_OrgNum  # Template card
                        SeaCosStatus = self.UpdateRecord(5,RecordData,CardNum=ADMIN)
                        if SeaCosStatus != FAIL:
                           if DEBUG_STEP_TRACE:
                              self.trace('Updating Record 6.....')
                           RecordData = [0xFF,0xFF] + IN_USE_STATUS + self.GenerateCardID(0x02,FALSE) + CCC_OrgNum  # FDE Card
                           SeaCosStatus = self.UpdateRecord(6,RecordData,CardNum=ADMIN)

                     # If USB FDE drive, then build records 5 and 6
                     # Note that there are 2 different versions of USB_FDE (SBS & ERD)
                     # If ATA_Mode, the records have already been updated, so don't update them here.
                     if self.USB_FDE_CARD and SeaCosStatus != FAIL:
                        if self.SBS and not self.ATA_Mode:
                           if DEBUG_STEP_TRACE:
                              self.trace('Updating Record 5.....')
                           RecordData = [0xFA, 0xFF, 0x08, 0x00] + self.GenerateCardID(0xFA,FALSE) + CCC_OrgNum     # SBS USB FDE Template Card
                           SeaCosStatus = self.UpdateRecord(5, RecordData, CardNum=ADMIN)
                           if SeaCosStatus != FAIL:
                              if DEBUG_STEP_TRACE:
                                 self.trace('Updating Record 6.....')
                              RecordData = [0x05, 0x00, 0x20, 0x00] +  self.GenerateCardID(0x05,FALSE) + CCC_OrgNum # USB FDE Card
                              SeaCosStatus = self.UpdateRecord(6, RecordData, CardNum=ADMIN)
                        elif not ATA_Mode:  # ERD  (External Reference Design) - requires different F/W & File system than SBS !!
                           if DEBUG_STEP_TRACE:
                              self.trace('Updating Record 5.....')
                           RecordData = [0xFD, 0xFF, 0x08, 0x00] + self.GenerateCardID(0xFD,FALSE) + CCC_OrgNum     # ERD USB FDE Template Card
                           SeaCosStatus = self.UpdateRecord(5, RecordData, CardNum=ADMIN)
                           if SeaCosStatus != FAIL:
                              if DEBUG_STEP_TRACE:
                                 self.trace('Updating Record 6.....')
                              RecordData = [0x02, 0x00, 0x20, 0x00] +  self.GenerateCardID(0x02,FALSE) + CCC_OrgNum # USB FDE Card
                              SeaCosStatus = self.UpdateRecord(6, RecordData, CardNum=ADMIN)
                        if SeaCosStatus != FAIL:
                           objMsg.printMsg('Saving Changes.....')
                           SeaCosStatus = self.Synchronize(CardNum=ADMIN, Level=1)  # Level=1 -->  SYNCHRONIZEALL
                        # Enable Direct Card Access in order to perform InitSeaCos
                        if SeaCosStatus != FAIL:
                           SeaCosStatus = self.SelectFileExtd([MASTER_FILE, SLASH_DEV, EF_DIRECTCARDACCESS], CardNum=ADMIN)
                        if SeaCosStatus != FAIL:
                           SeaCosStatus =  self.UpdateBinaryDeviceFile([0x00,0x08], Offset=0, CardNum=ADMIN)
                        if SeaCosStatus != FAIL:
                           SeaCosStatus = self.InitSeaCos()
                        #  Re-authenticate to the Admin card
                        if SeaCosStatus != FAIL:
                           if DEBUG_STEP_TRACE:
                              self.trace('Get Challenge / External Authenticate.....')
                           SeaCosStatus = self.Authenticate( "Unique", CardNum=ADMIN )

         # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

         if SeaCosStatus != FAIL and not self.ENABLE_SP:
            if DEBUG_STEP_TRACE:
               self.trace('Disable Serial Port.....')
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, SLASH_DEV, EF_DIAGLOCKS], CardNum=ADMIN)

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x02, Offset=0, CardNum=ADMIN)

            if SeaCosStatus != FAIL:
               DiagLockSettings = [0x00, 0x00]  # Bit 0: Serial Port Enablement - OFF
               # Bit 1: Direct Read/Writes of Extended files - OFF
               SeaCosStatus = self.UpdateBinaryDeviceFile(DiagLockSettings, Offset=0, CardNum=ADMIN)

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x02, Offset=0, CardNum=ADMIN)

         elif SeaCosStatus != FAIL and self.ENABLE_SP:
            objMsg.printMsg('Serial Port *NOT* dis-abled !')

         # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

         if SeaCosStatus != FAIL and self.REMOTE_ISSUANCE:
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, DF_CDE, EF_HOST_TO_DISK2], CardNum=ADMIN)
            if SeaCosStatus != FAIL:
               method,prms = RequestService('ReqWebIssuanceKey',(HDASerialNumber))        #  Call host services to get the key
            if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:                             #  Make sure that the service completed successfully
               #  Extract the key from the data and convert from base64 to binary
               IssuanceKeystr = base64.decodestring(prms['webIssuanceKey'])
               IssuanceKey = []
               for element in IssuanceKeystr:
                  IssuanceKey.append(ord(element))
            else:
               SeaCosStatus = FAIL
               #failcode['Fin Kwai Prep'] = ('KCISrv',prms['EC'][0])
               ScrCmds.raiseException(prms.get('EC',(12383,'Default'))[0], "Kwai Prep Failed")
               objMsg.printMsg('Failed to get Issuance Key')

            if SeaCosStatus != FAIL:
               objMsg.printMsg('Loading Remote Issuance Key to Admin card')
               SeaCosStatus = self.UpdateBinary(IssuanceKey, Offset=Manf3DESKeyOffset, CardNum=ADMIN)

         # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

   #@@
         if SeaCosStatus != FAIL and not self.DefaultData:
            if DEBUG_STEP_TRACE:
               self.trace('Loading drive key pool.....')
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, SLASH_DEV, EF_PRECALC_KEYS], CardNum=ADMIN)
            if SeaCosStatus != FAIL:
               keysNeeded = self.KwaiVars.get("Num_Key_Pairs",20)            # Number of Key pairs requested at a time
               if keysNeeded < 20:
                  number = keysNeeded
               else:
                  number = 20
               # Check the FIFO to see if there are already keys loaded. If so, and it's different than what we need,
               # flush the FIFO and reload keys, otherwise, if it's the same, don't load any, as this conserves keys.
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x04, Offset=0, CardNum=ADMIN)
               if SeaCosStatus != FAIL:
                  response_length = self.GetResponseLength()
                  if response_length != -1:
                     ReadBinaryData = self.GetSeaCosData(offset=10, bytes=response_length-2)
                     if ReadBinaryData[LLRET] == OK:
                        keysInPlace = ord(ReadBinaryData[DATA][1])
                        if keysInPlace != 0 and keysInPlace != keysNeeded:
                           if self.UpdateBinary(Data=0, Offset=0, CardNum=ADMIN) != FAIL:
                              objMsg.printMsg('Keystore FIFO Flushed !') # Re-load
                        elif keysInPlace == keysNeeded:
                           objMsg.printMsg('Keystore FIFO already contains %d keys!' % keysInPlace)
                           keysNeeded = 0  # Don't re-load

                        # Start requesting (any required) key pairs from the KCI and place them in the drive's key pool
                        keyPairsLoaded = 0
                        while keysNeeded > keyPairsLoaded:
                           objMsg.printMsg('--- Requesting %d Key Pairs from KCI Server ---' % (number))

                           method,prms = RequestService('GetKeyPair',(number))        #  Call host services to get the key pairs

                           cntr = 0
                           if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:                  #  Make sure that the service completed successfully
                              for key in prms.keys():           #  Step through each key pair
                                 #  check each key identifier to make sure it is actual keypair data and not Server Error Code information
                                 if key == 'EC':
                                    continue

                                 datastr = base64.decodestring(prms[key])           #  Decode the data from it's base 64 format

                                 #  Build the data string into a List of ordinals in preparation for Update Binary
                                 KeyPairList = []
                                 for character in datastr:
                                    KeyPairList += [ord(character)]

                                 #  Check the list for proper length, each piece of key pair data should be 132 bytes
                                 if len(KeyPairList) == ValidKeyPairListLen:
                                    SeaCosStatus = self.UpdateBinary(KeyPairList, Offset=0, CardNum=ADMIN)
                                    if SeaCosStatus != FAIL:
                                       keyPairsLoaded += 1
                                       cntr += 1
                                 else: # Something went wrong - data has an invalid length
                                    objMsg.printMsg('*** I N V A L I D  K E Y  P A I R  L E N G T H ***')
                                    objMsg.printMsg('Key pair length = %d, Expected length is %d' % (len(KeyPairList), ValidKeyPairListLen))
                                    self.DumpData(datastr, 3, 10, msg = key)
                                    SeaCosStatus = FAIL
                                    break

                              # Now report how many key pairs were loaded on the drive
                              objMsg.printMsg('%d Key pairs were successfully loaded on the drive (of %d required)' % (cntr, keyPairsLoaded))

                              if keyPairsLoaded < keysNeeded:
                                 number = keysNeeded - keyPairsLoaded

                              # Read back to verify that the Keys were in fact, loaded.
                              if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
                                 SeaCosStatus = self.ReadBinary(NumberOfBytes=4, Offset=0, CardNum=ADMIN)

                           else: # Where is our data ?
                              objMsg.printMsg("%s : %s (%d)" % (ErrStr,prms['EC'][1],prms['EC'][0]))               # Error from KCI server
                              SeaCosStatus = FAIL
                              #failcode['Fin Kwai Prep'] = ('KCISrv',prms['EC'][0])
                              ScrCmds.raiseException(prms.get('EC',(12383,'Default'))[0], "Kwai Prep Failed")
                              break

         elif SeaCosStatus != FAIL:
            objMsg.printMsg('Pool Keys NOT required.')

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   #@@
         # Generate RSA1, Certificate 1, and Tampered Certificate 1 data
         # NOTE: The 'staging' server has a different certification hierarchy than the 'production' server, so any drives
         # processed with certificates from the staging server will *NOT* be recognized as valid production drives by any
         # validation process (for instance, during any issuance) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
         if SeaCosStatus != FAIL and not self.DefaultData:
            if DEBUG_STEP_TRACE:
               self.trace('Getting Certified Key Pair, SIGNing.....')
            RSA_TLV_data, Certificate, TampCertificate = self.GenerateKeyData(HDASerialNumber, 'SIGN')

            if RSA_TLV_data == 'FAIL' or Certificate == FAIL:               # GenerateKeyData() failed - we're toast
               objMsg.printMsg('%s : GenerateKeyData() failed' % ErrStr)
               SeaCosStatus = FAIL
            else:
               if DEBUG_STEP_TRACE:
                  self.trace('Loading RSA 1.....')
               SeaCosStatus = self.SelectFileExtd([MASTER_FILE, DF_CDE, EF_RSA1], CardNum=ADMIN)
               if SeaCosStatus != FAIL:
                  if DEBUG_DISPLAY_RSA1_TLV_DATA:
                     objMsg.printMsg('RSA1 TLV data: %s' % RSA_TLV_data)

                  #  The data to be written here is too large to be written with a single update binary command
                  #  Issue two commands of 200 bytes each, then issue another command to transfer the remainder.

                  SeaCosStatus = self.UpdateBinary(RSA_TLV_data[:0xC8], Offset=0, CardNum=ADMIN)
                  if SeaCosStatus == FAIL:                     #  Unable to load RSA 1 - we're toast
                     objMsg.printMsg('%s : Unable to load part 1 of RSA 1' % ErrStr)
                  else:
                     SeaCosStatus = self.UpdateBinary(RSA_TLV_data[0xC8:0x190], Offset=0xC8, CardNum=ADMIN)
                     if SeaCosStatus == FAIL:                  #  Unable to load RSA 1 - we're toast
                        objMsg.printMsg('%s : Unable to load part 2 of RSA 1' % ErrStr)
                     else:
                        SeaCosStatus = self.UpdateBinary(RSA_TLV_data[0x190:], Offset=0x190, CardNum=ADMIN)
                        if SeaCosStatus == FAIL:               #  Unable to load RSA 1 - we're toast
                           objMsg.printMsg('%s : Unable to load part 3 of RSA 1' % ErrStr)

               # If the file Updates went ok, read back the data for viewing
               if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
                  SeaCosStatus = self.ReadBinary(NumberOfBytes = 0xC8, Offset=0, CardNum=ADMIN)
                  if SeaCosStatus != FAIL:
                     SeaCosStatus = self.ReadBinary(NumberOfBytes=0xC8, Offset=0xC8, CardNum=ADMIN)
                     if SeaCosStatus != FAIL:
                        SeaCosStatus = self.ReadBinary(NumberOfBytes=len(RSA_TLV_data) - 0x190, Offset=0x190, CardNum=ADMIN)

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

               if SeaCosStatus != FAIL:
                  if DEBUG_STEP_TRACE:
                     self.trace('Loading Certificate 1.....')
                  # MASTER_FILE,DF_CDE already in the path, select EF_CERT1
                  SeaCosStatus = self.SelectFile(EF_CERT1, CardNum=ADMIN)
                  if SeaCosStatus != FAIL:
                     CertificateList = []
                     for character in Certificate:
                        CertificateList += [ord(character)]

                     #  The data to be written here is again too large to be written with a single update binary command
                     #  Issue four commands of 200 bytes each, then issue another command to transfer the remainder.

                     SeaCosStatus = self.UpdateBinary(CertificateList[:0xC8], Offset=0, CardNum=ADMIN)
                     if SeaCosStatus == FAIL:                        #  Unable to load Certificate 1 - we're toast
                        objMsg.printMsg('%s : Unable to load part 1 of Certificate 1' % ErrStr)
                     else:
                        SeaCosStatus = self.UpdateBinary(CertificateList[0xC8:0x190], Offset=0xC8, CardNum=ADMIN)
                        if SeaCosStatus == FAIL:                     #  Unable to load Certificate 1 - we're toast
                           objMsg.printMsg('%s : Unable to load part 2 of Certificate 1' % ErrStr)
                        else:
                           SeaCosStatus = self.UpdateBinary(CertificateList[0x190:0x258], Offset=0x190, CardNum=ADMIN)
                           if SeaCosStatus == FAIL:                  #  Unable to load Certificate 1 - we're toast
                              objMsg.printMsg('%s : Unable to load part 3 of Certificate 1' % ErrStr)
                           else:
                              SeaCosStatus = self.UpdateBinary(CertificateList[0x258:0x320], Offset=0x258, CardNum=ADMIN)
                              if SeaCosStatus == FAIL:               #  Unable to load Certificate 1 - we're toast
                                 objMsg.printMsg('%s : Unable to load part 4 of Certificate 1' % ErrStr)
                              else:
                                 SeaCosStatus = self.UpdateBinary(CertificateList[0x320:], Offset=0x320, CardNum=ADMIN)
                                 if SeaCosStatus == FAIL:            #  Unable to load Certificate 1 - we're toast
                                    objMsg.printMsg('%s : Unable to load part 5 of Certificate 1' % ErrStr)

                  else:  # Unable to select the file
                     objMsg.printMsg(UnexpectedStatus % result)

                  # If the file Updates went ok, read back the data for viewing
                  if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
                     SeaCosStatus = self.ReadBinary(NumberOfBytes=0xC8, Offset=0, CardNum=ADMIN)
                     if SeaCosStatus != FAIL:
                        SeaCosStatus = self.ReadBinary(NumberOfBytes=0xC8, Offset=0xC8, CardNum=ADMIN)
                        if SeaCosStatus != FAIL:
                           SeaCosStatus = self.ReadBinary(NumberOfBytes=0xC8, Offset=0x190, CardNum=ADMIN)
                           if SeaCosStatus != FAIL:
                              SeaCosStatus = self.ReadBinary(NumberOfBytes=0xC8, Offset=0x258, CardNum=ADMIN)
                              if SeaCosStatus != FAIL:
                                 SeaCosStatus = self.ReadBinary(NumberOfBytes=len(Certificate) - 0x320, Offset=0x320, CardNum=ADMIN)

         elif SeaCosStatus != FAIL:
            objMsg.printMsg('Certificate 1 NOT Required.')

         # - - - - - - - Generate RSA2, Certificate 2, and Tampered Certificate 2 data - - - - - - - -
   #@@
         if SeaCosStatus != FAIL and not self.DefaultData:
            if DEBUG_STEP_TRACE:
               self.trace('Getting Certified Key Pair, ENCRypting.....')
            RSA_TLV_data, Certificate, TampCertificate = self.GenerateKeyData(HDASerialNumber, 'ENCR')

            if RSA_TLV_data == 'FAIL' or Certificate == FAIL:               # GenerateKeyData() failed - we're toast
               objMsg.printMsg('%s : GenerateKeyData() failed' % ErrStr)
               SeaCosStatus = FAIL
            else:
               if DEBUG_STEP_TRACE:
                  self.trace('Loading RSA 2.....')
               #  MASTER_FILE,DF_CDE already in the path, select EF_RSA2
               SeaCosStatus = self.SelectFile(EF_RSA2, CardNum=ADMIN)
               if SeaCosStatus != FAIL:
                  if DEBUG_DISPLAY_RSA1_TLV_DATA:
                     objMsg.printMsg('RSA1 TLV data: %s' % RSA_TLV_data)

                  #  The data to be written here is too large to be written with a single update binary command
                  #  Issue two commands of 200 bytes each, then issue another command to transfer the remainder.

                  SeaCosStatus = self.UpdateBinary(RSA_TLV_data[:0xC8], Offset=0, CardNum=ADMIN)
                  if SeaCosStatus == FAIL:                     #  Unable to load RSA 2 - we're toast
                     objMsg.printMsg('%s : Unable to load part 1 of RSA 2' % ErrStr)
                  else:
                     SeaCosStatus = self.UpdateBinary(RSA_TLV_data[0xC8:0x190], Offset=0xC8, CardNum=ADMIN)
                     if SeaCosStatus == FAIL:                  #  Unable to load RSA 2 - we're toast
                        objMsg.printMsg('%s : Unable to load part 2 of RSA 2' % ErrStr)
                     else:
                        SeaCosStatus = self.UpdateBinary(RSA_TLV_data[0x190:], Offset=0x190, CardNum=ADMIN)
                        if SeaCosStatus == FAIL:               #  Unable to load RSA 2 - we're toast
                           objMsg.printMsg('%s : Unable to load part 3 of RSA 2' % ErrStr)
               else:  # Failed to Select the File
                  objMsg.printMsg(UnexpectedStatus % result)

               # If the file Updates went ok, read back the data for viewing
               if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
                  SeaCosStatus = self.ReadBinary(NumberOfBytes=0xC8, Offset=0, CardNum=ADMIN)
                  if SeaCosStatus != FAIL:
                     SeaCosStatus = self.ReadBinary(NumberOfBytes=0xC8, Offset=0xC8, CardNum=ADMIN)
                     if SeaCosStatus != FAIL:
                        SeaCosStatus = self.ReadBinary(NumberOfBytes=len(RSA_TLV_data) - 0x190, Offset=0x190, CardNum=ADMIN)

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

               if SeaCosStatus != FAIL:
                  if DEBUG_STEP_TRACE:
                     self.trace('Loading Certificate 2.....')
                  #  MASTER_FILE,DF_CDE already in the path, select EF_CERT2
                  SeaCosStatus = self.SelectFile(EF_CERT2, CardNum=ADMIN)
                  if SeaCosStatus != FAIL:
                     CertificateList = []
                     for character in Certificate:
                        CertificateList += [ord(character)]

                     #  The data to be written here is again too large to be written with a single update binary command
                     #  Issue four commands of 200 bytes each, then issue another command to transfer the remainder.

                     SeaCosStatus = self.UpdateBinary(CertificateList[:0xC8], Offset=0, CardNum=ADMIN)
                     if SeaCosStatus == FAIL:                       #  Unable to load Certificate 2 - we're toast
                        objMsg.printMsg('%s : Unable to load part 1 of Certificate 2' % ErrStr)
                     else:
                        SeaCosStatus = self.UpdateBinary(CertificateList[0xC8:0x190], Offset=0xC8, CardNum=ADMIN)
                        if SeaCosStatus == FAIL:                    #  Unable to load Certificate 2 - we're toast
                           objMsg.printMsg('%s : Unable to load part 2 of Certificate 2' % ErrStr)
                        else:
                           SeaCosStatus = self.UpdateBinary(CertificateList[0x190:0x258], Offset=0x190, CardNum=ADMIN)
                           if SeaCosStatus == FAIL:                 #  Unable to load Certificate 2 - we're toast
                              objMsg.printMsg('%s : Unable to load part 3 of Certificate 2' % ErrStr)
                           else:
                              SeaCosStatus = self.UpdateBinary(CertificateList[0x258:0x320], Offset=0x258, CardNum=ADMIN)
                              if SeaCosStatus == FAIL:              #  Unable to load Certificate 2 - we're toast
                                 objMsg.printMsg('%s : Unable to load part 4 of Certificate 2' % ErrStr)
                              else:
                                 SeaCosStatus = self.UpdateBinary(CertificateList[0x320:], Offset=0x320, CardNum=ADMIN)
                                 if SeaCosStatus == FAIL:           #  Unable to load Certificate 2 - we're toast
                                    objMsg.printMsg('%s : Unable to load part 5 of Certificate 2' % ErrStr)
                  else:  # Unable to select the file
                     objMsg.printMsg(UnexpectedStatus % result)

                  # If the file Updates went ok, read back the data for viewing
                  if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
                     SeaCosStatus = self.ReadBinary(NumberOfBytes=0xC8, Offset=0, CardNum=ADMIN)
                     if SeaCosStatus != FAIL:
                        SeaCosStatus = self.ReadBinary(NumberOfBytes=0xC8, Offset=0xC8, CardNum=ADMIN)
                        if SeaCosStatus != FAIL:
                           SeaCosStatus = self.ReadBinary(NumberOfBytes=0xC8, Offset=0x190, CardNum=ADMIN)
                           if SeaCosStatus != FAIL:
                              SeaCosStatus = self.ReadBinary(NumberOfBytes=0xC8, Offset=0x258, CardNum=ADMIN)
                              if SeaCosStatus != FAIL:
                                 SeaCosStatus = self.ReadBinary(NumberOfBytes=len(Certificate) - 0x320, Offset=0x320, CardNum=ADMIN)

         elif SeaCosStatus != FAIL:
            objMsg.printMsg('Certificate 2 NOT Required.')

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   #@@
         if SeaCosStatus != FAIL:
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, DF_CDE, EF_SID], CardNum=ADMIN)  # Redundant
            if SeaCosStatus != FAIL and not self.DefaultData:
               if DEBUG_STEP_TRACE:
                  self.trace('Generating SID.....')
               SID = self.GetSID()
               if SID != '':
                  if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
                     SeaCosStatus = self.ReadBinary(NumberOfBytes=0x30, Offset=4, CardNum=ADMIN)

                  mSID = SID    # Save the mSID (mfg SID)
                  SIDList = []
                  SIDStr = ''
                  for char in SID:
                     SIDList += [ord(char)]
                     SIDStr += char

                  if SeaCosStatus != FAIL:
                     SeaCosStatus = self.VerifyPin(KeyRef=0x11)                # Verify the PIN @ ref 0x11
                     if SeaCosStatus != FAIL:
                        SeaCosStatus = self.ChangePin(SIDList)                 # Install the new PIN @ ref 0x11 (cSID)

                     if SeaCosStatus != FAIL:
                        SeaCosStatus = self.VerifyPin(KeyRef=0x12)             # Verify the backup PIN @ ref 0x12
                        if SeaCosStatus != FAIL:
                           SeaCosStatus = self.ChangePin(SIDList,0x12)         # Install the new backup PIN @ ref 0x12 (mSID)
                        if SeaCosStatus != FAIL:
                           SeaCosStatus = self.SetMasterPassword(SIDStr)       # Change the ATA Master Password to the SID

                     if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
                        SeaCosStatus = self.ReadBinary(NumberOfBytes=0x30, Offset=0, CardNum=ADMIN)
               else:                          # Couldn't generate a SID for some reason
                  SeaCosStatus = FAIL
            elif SeaCosStatus != FAIL:
               objMsg.printMsg('---- Unique SID NOT required - using Default. ----')
               SIDStr = ''
               SIDList = []
               for i in range(0,self.SidLength):
                  SIDStr += DEFAULT_PIN[i]
                  SIDList += [ord(DEFAULT_PIN[i])]
               self.UpdateAttributes(SIDStr)

               SeaCosStatus = self.ChangePin(SIDList)                 # Install the new PIN @ ref 0x11

         if SeaCosStatus != FAIL:
            objMsg.printMsg("****** Personalization of Admin Card complete ******")

   #----------------------------------------------------------------------------------------------------
   # De-Activate the Drive Features Card (on M2TD & CODY drives) to close a security hole.
   # Trusted Drive Life Cycle Doc Rev E Step 12.
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL and not self.DefaultData:
            objMsg.printMsg("De-Activating Drive Features Card....")
            if SeaCosStatus != FAIL:
               SeaCosStatus = self.SelectFileExtd([MASTER_FILE, SLASH_DEV, EF_CARD_CONTROL], CardNum=ADMIN)
               if SeaCosStatus != FAIL:
                  # Writing a 04 to an offset equal to the Card Number will de-activate the card. (0C will Terminate)
                  SeaCosStatus =  self.UpdateBinaryDeviceFile([0x04], Offset=FEATURES, CardNum=ADMIN)
                  if SeaCosStatus != FAIL:
                     objMsg.printMsg("****** Drive Features Card has been De-Activated ******")

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 13a: Select the DF-CIA EF-SKDF file
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            objMsg.printMsg('Update Mfg Key on Admin Card.....')
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, DF_CIA, EF_SKDF], CardNum=ADMIN)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 13a: Overwrite key reference 0x9F
   #----------------------------------------------------------------------------------------------------

         if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
            SeaCosStatus = self.ReadBinary(NumberOfBytes=0x30, Offset=0, CardNum=ADMIN)

         if SeaCosStatus != FAIL:
            objMsg.printMsg('Overwritting key reference 0x9F on Admin Card.....')
            SeaCosStatus = self.UpdateBinary(self.SERIAL_OVERWRITE, Offset=0, CardNum=ADMIN)

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x30, Offset=0, CardNum=ADMIN)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 13c: Select the DF-CDE EF-3DES file
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, DF_CDE, EF_3DES], CardNum=ADMIN)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 13d: Overwrite the Manufacturing 3DES key with the Serial
   # Port Enable Key
   #----------------------------------------------------------------------------------------------------

         if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
            SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0x0, CardNum=ADMIN)

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Installing Serial Port Enable Key to Admin Card.....')
            # For M2TD, the Serial Port Enable key is no longer fixed, but rather, it is a DERIVED (from the S/N) key.
            if not self.DefaultData:
               objMsg.printMsg('Getting unique Serial Port Enable key')
               method, prms = RequestService('ReqSPEKey', (HDASerialNumber,))
               if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:            #  Make sure the service completed successfully
                  if prms.has_key('serialPortEnableKey'):
                     # convert from base64 to binary and Extract the 3DES value from the data
                     SerialPortKeystr = base64.decodestring(prms['serialPortEnableKey'])
                     SerialPort3DESKey = []
                     for element in SerialPortKeystr:
                        SerialPort3DESKey.append(ord(element))
                  else:
                     objMsg.printMsg("%s : Failed to get Serial Port 3DES Key, Invalid dictionary key" % ErrStr)     # Error condition
                     SeaCosStatus = FAIL
               else:
                  SeaCosStatus = FAIL
                  objMsg.printMsg("%s : %s (%d)" % (ErrStr,prms.get('EC',(12383,'Default'))[1],prms.get('EC',(12383,'Default'))[0])) # Error from KCI server
                  #failcode['Fin Kwai Prep'] = ('KCISrv',prms.get('EC',(12383,'Default'))[0])
                  ScrCmds.raiseException(prms.get('EC',(12383,'Default'))[0], "Kwai Prep Failed")

               if SeaCosStatus != FAIL:
                  SeaCosStatus = self.UpdateBinary(SerialPort3DESKey, Offset=Manf3DESKeyOffset, CardNum=ADMIN)   # Use derived key
            else:
               objMsg.printMsg('Using Default Serial Port Enable key')
               SeaCosStatus = self.UpdateBinary(SERIAL_ENABLE_3DES, Offset=Manf3DESKeyOffset, CardNum=ADMIN)     # Use fixed key

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x1C, Offset=0x0, CardNum=ADMIN)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 14: Select the EF-ARR file
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Customizing ACL refs on Admin Card.....')
            #  Select file with FCP for debug
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, EF_ARR], CardNum=ADMIN, ReturnFCP='FALSE')

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 14: Issue Update Record to update Access Rules
   # based on Table 9 for record 2
   #----------------------------------------------------------------------------------------------------

         if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
            objMsg.printMsg('Read Record 1 prior to writing Record 2')
            SeaCosStatus = self.ReadRecord(RecordNum=1, Mode=ABS_CURR_RECORD_MODE, RecordLength=0x0E, CardNum=ADMIN)
            if SeaCosStatus != FAIL:
               objMsg.printMsg('Read Record 2 prior to writing Record 2')
               SeaCosStatus = self.ReadRecord(RecordNum=2, Mode=ABS_CURR_RECORD_MODE, RecordLength=0x0C, CardNum=ADMIN)

         #  The following Record Data is based on the corresponding information in the
         #  LC_Tests-sec3.pen file as excerpted below:
         #     CARD CARD_NUMBER_ADMINISTRATION:
         #       UpdateRecord ( 0x02 , ABSOLUTE_RECORD ,
         #                      flatten { FCP_ACL_EXPANDED :
         #                      { ACL_AM_DO : ACL_AM_FILE_ACTIVATE | ACL_AM_FILE_DEACTIVATE  | ACL_AM_FILE_UPDATE },
         #                      { ACL_SC_DO_NEVER : },
         #                      { ACL_AM_DO : ACL_AM_FILE_READ },
         #                      { ACL_SC_DO_ALWAYS : }
         #                      } )

         #  Set record content for EF-CCC Rules
         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Updating Record 2.....')
            RecNumber = 2
            RecordData = [0xAB, 0x0A, 0x80, 0x01, 0x1A, 0x97, 0x00, 0x80, 0x01, 0x01, 0x90, 0x00]
            SeaCosStatus = self.UpdateRecord(RecNumber, RecordData, CardNum=ADMIN, Mode=ABS_CURR_RECORD_MODE)

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               objMsg.printMsg('Read Record 1 after writing Record 2')
               SeaCosStatus = self.ReadRecord(RecordNum=1, Mode=ABS_CURR_RECORD_MODE, RecordLength=0x0E, CardNum=ADMIN)
               if SeaCosStatus != FAIL:
                  objMsg.printMsg('Read Record 2 after writing Record 2')
                  SeaCosStatus = self.ReadRecord(RecordNum=2, Mode=ABS_CURR_RECORD_MODE, RecordLength=0x0C, CardNum=ADMIN)

         #  The following Record Data is based on the corresponding information in the
         #  LC_Tests-sec3.pen file as excerpted below to DISABLE EF_CARD_CONTROL:
         #     CARD CARD_NUMBER_ADMINISTRATION:
         #       UpdateRecord ( 0x03 , ABSOLUTE_RECORD ,
         #                      flatten { FCP_ACL_EXPANDED :
         #                      { ACL_AM_DO : ACL_AM_FILE_ACTIVATE | ACL_AM_FILE_DEACTIVATE },
         #                      { ACL_SC_DO_NEVER : },
         #                      { ACL_AM_DO : ACL_AM_FILE_UPDATE },
         #                      { ACL_SC_DO_NEVER : },
         #                      { ACL_AM_DO : ACL_AM_FILE_READ },
         #                      { ACL_SC_DO_NEVER : }
         #                      } )
         #  Set record content for EF-CCC Rules

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Updating Record 3.....')
            RecNumber = 3
            RecordData = [0xAB, 0x12, 0x80, 0x01, 0x18, 0x97, 0x00, 0x80, 0x01, 0x02,\
                              0xA4, 0x03, 0x83, 0x01, 0x11, 0x80, 0x01, 0x01, 0x97, 0x00]
            SeaCosStatus = self.UpdateRecord(RecNumber, RecordData, CardNum=ADMIN, Mode=ABS_CURR_RECORD_MODE)


         #  The following Record Data is based on the corresponding information in the
         #  LC_Tests-sec3.pen file as excerpted below to ENABLE SERIAL_ACCESS:
         #     CARD CARD_NUMBER_ADMINISTRATION:
         #       UpdateRecord ( 0x04 , ABSOLUTE_RECORD ,
         #                      flatten { FCP_ACL_EXPANDED :
         #                      { ACL_AM_DO : ACL_AM_FILE_READ | ACL_AM_FILE_UPDATE },
         #                      { ACL_SC_DO:
         #                          { ACL_SC_DO:
         #                              { ACL_SC_DO_AND:
         #                                  { ACL_SC_KEY_REFERENCE : KEYREF_SID },
         #                                  { ACL_SC_KEY_REFERENCE : KEYREF_SERIAL_ENABLE}
         #                              }
         #                      }  } )
         #  Set record content for EF-CCC Rules

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Updating Record 4.....')
            RecNumber = 4
            RecordData = [0xAB, 0x0D, 0x80, 0x01, 0x03, 0xA4, 0x08, 0xAF, 0x06, 0x83, 0x01, 0x11, 0x83, 0x01, 0x9E]
            SeaCosStatus = self.UpdateRecord(RecNumber, RecordData, CardNum=ADMIN, Mode=ABS_CURR_RECORD_MODE)

   #----------------------------------------------------------------------------------------------------
   #  Turn on Entropy in the EF_Entropy_Src file so this feature can be tested.
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL and self.ENTROPY_ON:
            if DEBUG_STEP_TRACE:
               objMsg.printMsg('Enabling Entropy.....')
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, SLASH_DEV, EF_ENTROPY_SRC], CardNum=ADMIN)

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x02, Offset=0, CardNum=ADMIN)

            if SeaCosStatus != FAIL:
               SeaCosStatus = self.UpdateBinaryDeviceFile([0x00, 0x00], Offset=0, CardNum=ADMIN)

            if DEBUG_VERIFY_DATA and SeaCosStatus != FAIL:
               SeaCosStatus = self.ReadBinary(NumberOfBytes=0x02, Offset=0, CardNum=ADMIN)

         elif SeaCosStatus != FAIL:
            objMsg.printMsg('Entropy is turned OFF')


   #----------------------------------------------------------------------------------------------------
   # Issue the FDE Card
   #----------------------------------------------------------------------------------------------------
         if SeaCosStatus != FAIL and self.IssueFDECard:
            objMsg.printMsg('... Issue FDE Card ...')
            if self.Random_PIN:                   # unique SID
               objMsg.printMsg('Random Card-owner PIN')
               sid = self.GetSID(updateAttrs=0,override=1)
            else:
               objMsg.printMsg('Card-owner PIN is mSID')
               sid = mSID                 # use mSID
            if sid != '':
               CardOwner = []
               for i in range(16):
                  CardOwner += [ord(sid[i])]
            SeaCosStatus = self.IssueCard( Pin=CardOwner, CardType=ISSUE_FDE_CARD )[0]
         elif SeaCosStatus != FAIL:
            objMsg.printMsg("FDE Card was not Issued.")

   #----------------------------------------------------------------------------------------------------
   # Issue a USER Card (if USB_FDE drive)
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL and self.IssueFDECard and self.USB_FDE_CARD:
            objMsg.printMsg('Issue User Card ...')
            SeaCosStatus,card = self.IssueCard( Pin=SIDList[0:16], CardType=ISSUE_USER_CARD, XFSpace=0 ) # Cardowner Pin = 1st 16 bytes of mSID; no XF Space
            if SeaCosStatus != FAIL:
               SeaCosStatus = self.Authenticate( "USER", CardNum=card, Secret=SID[0:16] )
            if SeaCosStatus != FAIL:
               objMsg.printMsg('Personalizing User Card.....')
               # Set up the FCP TLV:
               fcp = [0x62, 0x18,                         # number of bytes for FCP (24)
                          0x82, 0x02, 0x01, 0x21,             # Transparent Elementary File (Shareable)
                          0x83, 0x02, 0x2F, 0xDE,             # file identifier
                          0x8A, 0x01, 0x05,                   # life cycle status byte (Operational_Activated)
                          0x80, 0x02, 0x00, 0x00,             # number of bytes (currently) in the file
                          0x81, 0x02, 0x1C, 0x00,             # number of bytes allocated to file (7K)
                          0x8B, 0x03, 0x2F, 0x06, 0x02]       # ACL reference (EF_ARR Record #2)
               SeaCosStatus = self.CreateFile(FCP=fcp, CardNum=card)  # Create the file
               if SeaCosStatus != FAIL:
                  SeaCosStatus = self.SelectFileExtd([MASTER_FILE, EF_USER], CardNum=card) # Select the newly created file
               if SeaCosStatus != FAIL:
                  SeaCosStatus = self.UpdateBinary([0x00], Offset=0, CardNum=card)  # set byte zero to 00 (SBS requirement)
               if SeaCosStatus != FAIL:
                  SeaCosStatus = self.SelectFileExtd([MASTER_FILE, EF_ARR], CardNum=card)
               if SeaCosStatus != FAIL:
                  objMsg.printMsg('Saving Changes.....')
                  SeaCosStatus = self.Synchronize(CardNum=ADMIN, Level=1)  # Level=1 -->  SYNCHRONIZEALL

   #----------------------------------------------------------------------------------------------------
   # Set up the FDE Card to enable 'PREBOOT' functionality
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL and self.PREBOOT:
            objMsg.printMsg("Enabling FDE card PRE-BOOT")
            if self.USB_FDE_CARD:
               card = USBFDE  # USB FDE card
            else:
               card = 2                  # TEMPLATE card for non-USB FDE
            SeaCosStatus = self.VerifyPin(KeyRef=0x11, CardNum=card, Pin=CardOwner)
            if SeaCosStatus != FAIL:
               PIN = SIDList + [0x20] * (32 - len(SIDStr))                  # pad the SID with blanks to 32 chars.
               SeaCosStatus = self.VerifyPin(KeyRef=0x01, CardNum=card, Pin=PIN) # Verify MASTER0
               if SeaCosStatus != FAIL:
                  # Set up the Passwords on the FDE card
                  if self.USB_FDE_CARD:                                          # If USB FDE: Master0 & User0 = SID
                     pw = mSID
                  else:
                     pw = 'administrator'                                   # else: MASTER0 = 'administrator'  USER0 = 'user'
                  newpin = []
                  PIN = pw + ' ' * (32 - len(pw))                           # pad with blanks to 32 chars.
                  for i in range(len(PIN)):
                     newpin += [ord(PIN[i])]
                  SeaCosStatus = self.ChangePin(newpin,0x01,CardNum=card)        # Install the new MASTER0 PIN @ ref 0x01
                  # If this is an SBS USB drive, then set the SECURE ERASE PIN to the mSID
                  if SeaCosStatus != FAIL and self.USB_FDE_CARD and self.SBS:
                     objMsg.printMsg("Installing SECURE_ERASE_PIN")
                     SeaCosStatus = self.ChangePin(newpin[0:self.SidLength],0x09,CardNum=card)     # Install the new SECURE_ERASE_PIN @ ref 0x09
                  # set the Lock-On-Start bit
                  if self.LockOnStartBit:
                     if SeaCosStatus != FAIL:
                        objMsg.printMsg("Setting Lock-On-Startup")
                        SeaCosStatus = self.SelectFileExtd([MASTER_FILE, SLASH_DEV, EF_LOCK_ON_STARTUP], CardNum=USBFDE)
                     if SeaCosStatus != FAIL:
                        SeaCosStatus = self.UpdateBinaryDeviceFile([0x01], Offset=0, CardNum=USBFDE)

                  # Now set the USER pw
                  if SeaCosStatus != FAIL:
                     if self.USB_FDE_CARD:
                        pw = mSID
                     else:
                        pw = 'user'
                     newpin = []
                     PIN = pw + ' ' * (32 - len(pw))                        # pad with blanks to 32 chars.
                     for i in range(len(PIN)):
                        newpin += [ord(PIN[i])]
                     SeaCosStatus = self.ChangePin(newpin,0x05,CardNum=card)     # Install the new USER0 PIN @ ref 0x05
               if SeaCosStatus != FAIL:
                  SeaCosStatus = self.SelectFileExtd([MASTER_FILE, SLASH_DEV, EF_LBA_REMAPPING], CardNum=card)
                  if SeaCosStatus != FAIL:
                     # Writing 0x01 to the EF_LBA_REMAPPING file causes the LBA address space to be re-mapped
                     # to the XF space of the FDE card.  writing a 0x00 will disable re-mapping.  Note that *two*
                     # writes are required if using DMA writes to the XF space (-OR- one write and a power cycle).
                     SeaCosStatus = self.UpdateBinaryDeviceFile([0x01], Offset=0, CardNum=card)
                     SeaCosStatus = self.UpdateBinaryDeviceFile([0x01], Offset=0, CardNum=card)
                     if SeaCosStatus != FAIL:
                        SeaCosStatus = self.WriteImage(self.KwaiVars['PreBootImage'], Select=3, CardNum=card)

         elif SeaCosStatus != FAIL:
            objMsg.printMsg("PRE-BOOT Image disabled.")

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 16: Select the Slash-Dev EF-TD-STATE file
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Setting Drive State.....')
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, SLASH_DEV, EF_TD_STATE], CardNum=ADMIN)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 17: Set TD_State to Operational
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:

   ##################################################################################################################
   # -------------------- STATE HAS TO BE SET TO 'OPERATIONAL' FOR THE PRODUCTION PROCESS --------------------------#
   ##################################################################################################################

            Msg = "State set to "
            if self.STATE == TD_STATE_OPERATIONAL:
               Msg = Msg + 'OPERATIONAL'
            else:
               Msg = Msg + 'INITIALIZED'
            objMsg.printMsg(Msg)
            SeaCosStatus = self.UpdateBinaryDeviceFile([self.STATE], CardNum=ADMIN)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 18: Select the EF-ARR file
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Updating Access Rules on Admin Card.....')
            SeaCosStatus = self.SelectFileExtd([MASTER_FILE, EF_ARR], CardNum=ADMIN, ReturnFCP='FALSE')   #  Select file with FCP for debug

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 19: Issue Update Record to update Access Rules
   # based on Table 9
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Updating Record 1.....')

         #  The following Record Data is based on the corresponding information in the
         #  LC_Tests-sec3.pen file as excerpted below:
         #     CARD CARD_NUMBER_ADMINISTRATION:
         #       UpdateRecord ( 0x01 , ABSOLUTE_RECORD ,
         #                      flatten { FCP_ACL_EXPANDED :
         #                       { ACL_AM_DO : ACL_AM_FILE_ACTIVATE | ACL_AM_FILE_DEACTIVATE  | ACL_AM_FILE_UPDATE | ACL_AM_FILE_READ },
         #                       { ACL_SC_DO_NEVER : }
         #                       } )

         #  Set Record Content for EF-ARR and EF-3DES Access Rules

            RecNumber = 1
            RecordData = [0xAB, 0x05, 0x80, 0x01, 0x1B, 0x97, 0x00]
            SeaCosStatus = self.UpdateRecord(RecNumber, RecordData, CardNum=ADMIN, Mode=ABS_CURR_RECORD_MODE)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 20a: Send Synchronize Command
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            objMsg.printMsg('Saving changes.....')
            SeaCosStatus = self.Synchronize(CardNum=ADMIN)

   #----------------------------------------------------------------------------------------------------
   # Trusted Drive Life Cycle Doc Rev E Step 20b: Issue Warm Reset
   #----------------------------------------------------------------------------------------------------

         if SeaCosStatus != FAIL:
            if DEBUG_STEP_TRACE:
               self.trace('Reset to Admin Card.....')
            SeaCosStatus = self.WarmReset(CardNum=ADMIN)

         if SeaCosStatus != FAIL:
            objMsg.printMsg('File System Personalization Complete.')
         CmdDividerLine = '-' * 80
         self.trace(CmdDividerLine)

   #----------------------------------------------------------------------------------------------------

      #EndTime('KWAI Prep', 'funcstart', 'funcfinish', 'functotal')
      objMsg.printMsg('Exiting KWAI Prep with SeaCos status: %d' % SeaCosStatus)
      if SeaCosStatus != FAIL:
         ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"]*1000)
         self.dut.driveattr['TD_FILESYS_ID'] = self.KwaiVars['Card Doc PN']
         self.dut.driveattr['FDE_DRIVE'] = 'FDE'
         objMsg.printMsg("FDE_DRIVE=%s" % self.dut.driveattr['FDE_DRIVE'])
         return OK
      else:
         #driveattr['failcode'] = failcode['Fin Kwai Prep']
         #return FAIL
         ScrCmds.raiseException(12383, "Kwai Prep Failed")


   #  ========================================================================================
   #  ========================================================================================
   #  Main entry into the Kwai Drive Unlock Processing -  Called from Process scripts to
   #  unlock the Serial Port - either through the Interface, or through the Serial Port itself.
   #  ========================================================================================
   #  ========================================================================================
   def UnlockSerialPort(self, viaSerialPort = 0):
      #################################################################################################################
      ###### THIS IS A SPECIAL REQUIREMENT..NEED TO DISABLE APM AND DO A SEEK WHEN DOING KWAIPREP, OTHERWISE WILL HAVE
      ###### HIGH FAILURE RATE ON ATA_WAIT_FOR_DRDY
      if objRimType.CPCRiser():
         result = ICmd.SetFeatures(0x85)
         if result['LLRET'] != OK: # if failed to disable APM, don't fail immediately, try to continue
            objMsg.printMsg('Disable Advance Power Management Failed!')
         else:
            objMsg.printMsg('Disable Advance Power Management Pass!')
            result = ICmd.Seek(0)      # Seek to LBA 0
            if result['LLRET'] != OK:
               objMsg.printMsg('Seek cmd Failed!')
            else:
               objMsg.printMsg('Seek cmd Pass!')
      #################################################################################################################
      SeaCosStatus = OK  # Initialize SeaCosStatus so it can be checked against later
      objMsg.printMsg('... Unlocking Serial Port ...')

      SeaCosStatus = self.WarmReset(CardNum=ADMIN, useSerialPort=viaSerialPort)

      if SeaCosStatus != FAIL:
         self.trace('... Select MF/SLASH-DEV/EF-DIAGLOCKS ...')
         SeaCosStatus = self.SelectFileExtd([MASTER_FILE, SLASH_DEV, EF_DIAGLOCKS], CardNum=ADMIN, useSerialPort=viaSerialPort)

      if SeaCosStatus != FAIL:
         # NOTE: If the drive has a unique SPEK, then authentication *must* come from the KCI server.
         # If the 'default' key is installed, then authentication must come from the Gemini Host.
         # So try the KCI server first, and if that fails, then try the Gemini host machine.  For EchoStar drives (TONKA/GALAXY),
         # the key is *always* (currently,anyway) fixed, so the Authenticate method will always use the Host machine to authenticate those.
         objMsg.printMsg('Authenticate Serial Port Enable key...')
         SeaCosStatus = self.Authenticate( KeyType="SPEK", CardNum=ADMIN, useSerialPort=viaSerialPort )  # Authenticate SPEK from KCI server
         if SeaCosStatus == FAIL and not self.DefaultData:
            objMsg.printMsg('Re-try Authenticate from Gemini (Default key)...')
            SeaCosStatus = self.Authenticate( KeyType="SPEK", CardNum=ADMIN, Auth="Gem", useSerialPort=viaSerialPort ) # Authenticate from Gemini Host

      if SeaCosStatus != FAIL:
         objMsg.printMsg('... Verify PIN ...')
         if DriveAttributes.has_key('TD_SID'):  # see if it's in the attrs
            SID = DriveAttributes['TD_SID']
         else:                                  # if not, use the default
            SID = DEFAULT_PIN[0:self.SidLength]
         objMsg.printMsg('Using SID:  %s' % SID)
         SIDList = []
         for char in SID:
            SIDList += [ord(char)]
         SeaCosStatus = self.VerifyPin(KeyRef=0x11, CardNum=ADMIN, Pin=SIDList, useSerialPort=viaSerialPort)

      if SeaCosStatus != FAIL:
         DiagLockSettings = [0x00, 0x02]  # Bit 1: Serial Port Enablement - ON
         # Bit 0: Direct Read/Writes of Extended files - OFF
         SeaCosStatus = self.UpdateBinary(DiagLockSettings, Offset=0, CardNum=ADMIN, useSerialPort=viaSerialPort)

      if SeaCosStatus != FAIL:
         objMsg.printMsg('Serial Port Unlocked.')
      else:
         objMsg.printMsg('Could not unlock Serial Port')
         ScrCmds.raiseException(14601, "Failed to unlock serial port")

      return SeaCosStatus

   #  ========================================================================================
   #  This method will remove the File System from a drive in the 'use' state using interface
   #  commands.  This method replaces the UnlockSerialPort() method (above) and serial commands
   #  (Z0,0,22) used to unlock and remove the file system.  What used to take several steps,
   #  can now be done with this single call (and in much less time).
   #  ========================================================================================
   def EraseFileSystem(self):

      SeaCosStatus = OK
      objMsg.printMsg('... Removing File System ...')

      if DriveAttributes.has_key('TD_SID'):  # see if it's in the attrs
         SID = DriveAttributes['TD_SID']
      else:                                  # if not, use the default
         SID = DEFAULT_PIN[0:self.SidLength]
      objMsg.printMsg('Using SID:  %s' % SID)
      SIDList = []
      for char in SID:
         SIDList += [ord(char)]

      SeaCosStatus = self.VerifyPin(Pin=SIDList)

      if SeaCosStatus == 0x6986:  # Already erased !!!
         objMsg.printMsg('File system already erased!')
         return OK
      elif SeaCosStatus != FAIL:
         SeaCosStatus,Nonce = self.RecoveryErasePrepare(ADMIN, SIDList)
      else:
         objMsg.printMsg('Verify Pin failed')

      Response = []
      if SeaCosStatus != 0x6581 and SeaCosStatus != FAIL:
         EncodedNonce = base64.encodestring(Nonce)
         # Encrypt the Nonce with the (derived) Serial Port Enable Key
         method,prms = RequestService('ReqSPEAuth',(EncodedNonce, HDASerialNumber))
         if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
            Response_str = base64.decodestring(prms['AuthenticationResponse'])

         for element in Response_str:
            Response.append(ord(element))

      elif SeaCosStatus == 0x6581:       # For 'Memory Problem' status, send the Nonce in plain text.
         objMsg.printMsg('Disc error - plain text Nonce')
         Nstr = self.StatusStrToHexStr(Nonce)[2:]
         count = 0
         for char in Nstr:    # Convert the Nonce string to a list of (UN-encrypted) integers
            if count == 0:
               x = int(char,16) * 16
               count += 1
            else:
               count = 0
               x = x + int(char,16)
               Response.append(x)

      if SeaCosStatus != FAIL:
         objMsg.printMsg('Erasing file sys, XF space....')
         SeaCosStatus = self.RecoveryErase(ADMIN, Response)

      if SeaCosStatus != FAIL:
         objMsg.printMsg('File system erased.')

      return SeaCosStatus

   #  ========================================================================================
   def LoadFile(self, srcFile, dstFile, doMD5=0, scrFileDir=''):

      if ConfigVars.has_key('CPC Reserve'):
         min_space = ConfigVars['CPC Reserve']
      else:
         min_space = 10000000

      fres = {}
      fres = ICmd.FreeSpace()
      freeSpace = int(fres['FREE'])

      objMsg.printMsg('\nFree Space :%s bytes\n'%(freeSpace))

      if min_space and (freeSpace < min_space):
         WriteToResultsFile('\nFree Space 1:%s bytes\n'%(freeSpace))
         ICmd.DeleteAllFiles()
         fres = {}
         fres = ICmd.FreeSpace()
         freeSpace = int(fres['FREE'])
         WriteToResultsFile('\nFree Space 2:%s bytes\n'%(freeSpace))
         #WriteToResultsFile('\nAfter Clear CPC Buffer - Free Space:%s bytes\n'%(freeSpace) + FileDir() + '\n')

      ID = self.ImageFileDir(srcFile,dstFile,scrFileDir)
      # objMsg.printMsg('LoadFile ImageFileDir=%s' % ID)

      # print ID

      if ID['RESULT'].find ('FS_OPENFORWRITE') >= 0:

      #if ID['LLRET'] != 0:   #  File does not exist
         try:
            print "Filling Buffer"
            ImageBufferStuff = self.FillImageBuffer(srcFile,dstFile,scrFileDir)
            print "*-*" * 500
            print ImageBufferStuff
            return ImageBufferStuff
            # return testLoadFile(srcFile,dstFile)
   #         fl = open(os.path.join(UserDownloadsPath,ConfigId[2],srcFile))
   #         data = fl.read()
   #         fl.close()
   #         return FillImageBuffer(dstFile,data)
         except:
            failure = "Failed opening %s file!!" % srcFile
            RES = {}
            RES['RESULT'] = failure
            RES['LLRET']  = -1
            try:
               fl.close()
            except:
               pass
            return RES
      return ID

   #  ========================================================================================
   def ImageFileDir(self, srcFile, dstFile, scrFileDir=''):
      #print "ConfigVars = ",ConfigVars
      #print "ConfigId = ",ConfigId
      if scrFileDir == '':
         print "UserDownloadsPath = ",UserDownloadsPath
         newFilename = UserDownloadsPath + '/' + ConfigId[2] + '/' + srcFile
      else:
         print scrFileDir
         newFilename = scrFileDir + '/' + srcFile
      #print "newFilename  -->> ",newFilename
      #print "ImageFileDir -->> ",srcFile

      size = os.path.getsize(newFilename)
      return ICmd.ImageFileDir(dstFile,size)

   #  ========================================================================================
   def FillImageBuffer(self, srcFile, dstFile, scrFileDir=''):

      try:     #  Try opening the file
         if scrFileDir == '':
            fl = open(os.path.join(UserDownloadsPath,ConfigId[2],srcFile))
         else:
            fl = open(os.path.join(scrFileDir,srcFile))
      except:  #  Failed opening the file
         failure = "Could not successfully open the %s file!!" % srcFile
         RES = {}
         RES['RESULT'] = failure
         RES['LLRET']  = -1
         try:
            fl.close()
         except:
            pass
         return RES

      sectOffset = 0
      dataLen    = 131072

      while dataLen == 131072:
         data = fl.read(131072)
         dataLen = len(data)
         #
         #  Transfer data to the Write Buffer in the NIOS, at specific Offset
         #
         if dataLen:
            ret = ICmd.BinaryTransfer(data,0,dstFile,sectOffset)
            sectOffset = sectOffset + 256

      try:     #  Try closing the file
         fl.close()
      except:
         objMsg.printMsg('Exception on try fl.close')
         pass

      if ret['LLRET'] == 0 and ret['RESULT'].find('_ACKNOWLEDGE') != -1:
         #
         #  Make sure the MD5's match.
         #
         ICmd.UpdateImageMD5(dstFile)  # Update the MD5 on the file in the NIOS

         ifd = ICmd.ImageFileDir(dstFile)  # Get MD5 information
         ifd['LLRET'] = 0
         # objMsg.printMsg('FillImageBuffer ImageFileDir=%s' % ifd)

         #
         #  Close the file on the CPC
         #
         #InterfaceCmd('FCloseFile',[dstFile]) # Removed 12-Aug-04 as per Steve Schumacher

         if ifd['LLRET'] == 0:
            filesMD5 = ifd['MD5']

            #
            #  Calculate the MD5 of the file on the CM
            #
            localMD5 = self.calcMD5(srcFile,scrFileDir)

            #
            #  Compare the MD5 CRC's
            #
            for i in range(0,16):
               if filesMD5[i] != localMD5[i]:
                  objMsg.printMsg('MD5 mismatch - filesMD5=%s localMD5=%s' %  (filesMD5[i], localMD5[i]))
                  self.DeleteImageFile(dstFile)       #  Remove the image file from the File System
                  objMsg.printMsg('MD5 mismatch - file deleted=%s' %  dstFile)
                  ifd['LLRET']  = -1
                  ifd['RESULT'] = 'MD5 CRC compare FAILED!!'
                  return ifd

         else:
            return ifd

      return ret

   #  ========================================================================================
   def DeleteImageFile(self, filename="None"):
      if filename == 'None':
         return ICmd.DeleteImageFile()          # Delete entire image buffer FAT (File Allocation Table)
      else:
         return ICmd.DeleteImageFile(filename)  # Delete a specific file out of the FAT

   #  ========================================================================================
   def calcMD5(self, srcFile, scrFileDir=''):
      #
      #  This function will open a file and calculate the MD5 crc on that file
      #  then pass the MD5 crc back to the requestor.
      #
      import md5
      m = md5.new()
      try:
         if scrFileDir == '':
            fl = open(os.path.join(UserDownloadsPath,ConfigId[2],srcFile))
         else:
            fl = open(os.path.join(scrFileDir,srcFile))
      except:
         return ''
      length = 512
      while length == 512:
         data = fl.read(512)
         m.update(data)
         length = len(data)
   #      print `data`
      fl.close()
      return m.digest()

   #  ========================================================================================
   def UnlockInterface(self):
      #################################################################################################################
      ###### THIS IS A SPECIAL REQUIREMENT..NEED TO DISABLE APM AND DO A SEEK WHEN DOING KWAIPREP, OTHERWISE WILL HAVE
      ###### HIGH FAILURE RATE ON ATA_WAIT_FOR_DRDY
      result = ICmd.SetFeatures(0x85)
      if result['LLRET'] != OK: # if failed to disable APM, don't fail immediately, try to continue
         objMsg.printMsg('Disable Advance Power Management Failed!')
      else:
         objMsg.printMsg('Disable Advance Power Management Pass!')
         result = ICmd.Seek(0)      # Seek to LBA 0
         if result['LLRET'] != OK:
            objMsg.printMsg('Seek cmd Failed!')
         else:
            objMsg.printMsg('Seek cmd Pass!')
      #################################################################################################################
      SeaCosStatus = OK  # Initialize SeaCosStatus so it can be checked against later
      objMsg.printMsg('... Verify PIN ...')
      if DriveAttributes.has_key('TD_SID'):  # see if it's in the attrs
         SID = DriveAttributes['TD_SID']
      else:                                  # if not, use the default
         SID = DEFAULT_PIN[0:self.SidLength]
      objMsg.printMsg('Using SID:  %s' % SID)
      SIDList = []
      for char in SID:
         SIDList += [ord(char)]
      for i in range(32-self.SidLength):     # Pad with space until SID is 32 characters
         SIDList += [32]
      SeaCosStatus = self.VerifyPin(KeyRef=0x01, CardNum=USBFDE, Pin=SIDList)

      if SeaCosStatus != FAIL:
         SeaCosStatus = self.SelectFileExtd([MASTER_FILE, SLASH_DEV, EF_LBA_REMAPPING_BYPASS], CardNum=USBFDE)
      if SeaCosStatus != FAIL:
         UnlockSettings = [0x01]
         SeaCosStatus = self.UpdateBinaryDeviceFile(UnlockSettings, Offset=0, CardNum=USBFDE)

      if SeaCosStatus != FAIL:
         objMsg.printMsg('Interface Unlocked.')
      else:
         objMsg.printMsg('***** WARNING: Could not unlock Interface! *****')

      return SeaCosStatus

   #-------------------------------------------------------------------------------
   def FDEType(self, kwai, fde_matrix):

      for fde, params in fde_matrix.iteritems():
         fde_type = fde
         for prop in params.items():
            if (fde=="Internal USB Enabled") and (prop[0]=='PreBootImage') \
                    and (not kwai[prop[0]]=='None') and (len(kwai[prop[0]])!=0):
               fde_type="Internal USB Enabled"
            elif not prop in kwai.items():
               fde_type = None
               break

         if not fde_type is None:
            return fde_type
      return None

###########################################################################################################
########  Base Helper Functions- Provided here for solitary import capability  ############################
def InitTrustedDL(dut, mode = 'ATA'):
   from Cell import theCell
   from Carrier import theCarrier

   result = OK
   comm_pass = 0
   useSerialPort = 1

   if not testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
      try:
         objMsg.printMsg("Trying to use normal Power Cycle.")
         if mode == 'ATA':
            objPwrCtrl.powerCycle(5000, 12000, 10, 30)
         else:
            objPwrCtrl.powerCycle(5000, 12000, 10, 30, useESlip=1)
      except:
         # As the default, FDE drive with locked Serial Port works with
         # 38400 bauds rate and no way to change it. Try to use basic Power
         # Cycle instead.
         objMsg.printMsg("Failed on normal Power Cycle. Trying to use basic Power Cycle.")
         theCarrier.powerOffPort(10)
         theCarrier.powerOnPort(5000, 12000, 30)
         objMsg.printMsg("Set Cell baud rate to %s." % DEF_BAUD)
         theCell.setBaud(DEF_BAUD)

   oSerial = serialScreen.sptDiagCmds()
   objMsg.printMsg("Waiting for Drive Serial Port to be ready.")
   oSerial.waitForReady(10)

   objMsg.printMsg("Checking is the drive locked.")
   data = sptCmds.execOnlineCmd(CTRL_Z, timeout = 10, waitLoops = 100)
   objMsg.printMsg("Data returned from Ctrl-Z command:\n%s" % data)
   if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
      lockFunc = oSerial.isSeaCosLocked
   else:
      lockFunc = oSerial.isLocked

   if data.find(">")>-1 and data.find("?>") == -1 and (data.find("&>") == -1 or testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT ):
      comm_pass = 1
      objMsg.printMsg( 'Drive does not need Serial Port Unlocking' )
      if mode == 'ATA':
         objPwrCtrl.powerCycle(5000,12000,10,30)
      else:
         objPwrCtrl.powerCycle(5000,12000,10,30, useESlip=1)
      return OK
   elif lockFunc(data) == True:
      objMsg.printMsg("Drive is locked: SeaCos.")
      sedType = "SeaCos"

      if self.dut.nextOper == "FNG2":
         objMsg.printMsg("Ok, drive is locked for SeaCos drive in FNG2, no need unlocking")
         self.dut.objData.update({'KwaiPrepDone': 1})
         objPwrCtrl.powerCycle(5000,12000,10,30)
         return sedType, OK

      #from KwaiPrep import *
      comm_pass = 1
      objMsg.printMsg( 'Kwai Serial Port Unlock required for Locked Drive' )
      if objRimType.CPCRiser():
         useSerialPort = 0
      oKwaiPrep = CKwaiPrepTest(dut)
      objMsg.printMsg( 'useSerialPort = %d' %useSerialPort )
      result = oKwaiPrep.UnlockSerialPort(useSerialPort)
      if result == OK:
         data = sptCmds.execOnlineCmd(CTRL_Z, timeout = 10, waitLoops = 100)
         objMsg.printMsg("After unlocking, drive returns data = \n%s " % data)

         data = sptCmds.sendDiagCmd('/\r', timeout = 10, raiseException = 1, altPattern = "T>")
         objMsg.printMsg("/ data = %s" % data)

         objMsg.printMsg( 'Erasing Security Sector on Drive' )
         data = sptCmds.sendDiagCmd("Z6,0,22\r", timeout = 10, raiseException = 1, altPattern = "Z6,0,22", suppressExitErrorDump = 1)
         objMsg.printMsg('T>Z6,0,22 data = %s' % data[:0xFF])
         time.sleep(45)

         data = sptCmds.execOnlineCmd(CTRL_Z, timeout = 10, waitLoops = 100)
         objMsg.printMsg("After Erasing Security Sector, drive returns data = \n%s " % data)
         # checking if the Erasing Security Sector has done successfully
         if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
            if mode == 'ATA':
               objPwrCtrl.powerCycle(5000, 12000, 10, 30)
            else:
               if dut.driveattr['FDE_DRIVE'] == 'FDE':
                  fdePowerCycle()
               else:
                  objPwrCtrl.powerCycle(5000, 12000, 10, 30, useESlip=1)
         else:
            try:
               objMsg.printMsg("Trying to use normal Power Cycle.")
               if mode == 'ATA':
                  objPwrCtrl.powerCycle(5000, 12000, 10, 30)
               else:
                  objPwrCtrl.powerCycle(5000, 12000, 10, 30, useESlip=1)
            except:
               # As the default, FDE drive with locked Serial Port works with
               # 38400 bauds rate and no way to change it. Try to use basic Power
               # Cycle instead.
               objMsg.printMsg("Failed on normal Power Cycle. Trying to use basic Power Cycle.")
               theCarrier.powerOffPort(10)
               theCarrier.powerOnPort(5000, 12000, 30)
               objMsg.printMsg("Set Cell baud rate to 38400.")
               theCell.setBaud(DEF_BAUD)

         objMsg.printMsg("Waiting for Drive Serial Port to be ready.")
         oSerial.waitForReady(10)
         if lockFunc() == True:
            result = -1

   elif testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT and oSerial.isTCGLocked(data) == True:
      objMsg.printMsg("Drive is locked: TCG.")
      sedType = "TCG"
      comm_pass = 1
      result = -1
   if comm_pass == 0:
      objMsg.printMsg( 'The drive is communicating, but did not return a ' + \
                       'T>, F>, ?> prompt, and (1Ah)-Serial Port Disabled' )
      if mode == 'ATA':
         objPwrCtrl.powerCycle(5000,12000,10,30)
      else:
         objPwrCtrl.powerCycle(5000,12000,10,30, useESlip=1)
      result = -1

   if result == OK:
      objMsg.printMsg('T>Z6,0,22 command completed successfully')
      oKwaiPrep.XFFormat()
      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
         objMsg.printMsg("FDE: Reset all existing FDE drive attributes.")
         dut.resetFDEAttributes()
      else:
         dut.driveattr['FDE_DRIVE'] = 'NONE'
         dut.driveattr['TD_SID'] = 'NONE'
         dut.driveattr['IFD_PBI_01_PN'] = 'NONE'
         dut.driveattr['IFD_PBI_01_HASH'] = 'NONE'
         dut.driveattr['TD_FILESYS_ID'] = 'NONE'

      objMsg.printMsg("FDE_DRIVE=%s" % dut.driveattr['FDE_DRIVE'])

      if mode == 'ATA':
         objPwrCtrl.powerCycle(5000, 12000, 10, 30)
      else:
         objPwrCtrl.powerCycle(5000, 12000, 10, 30, useESlip = 1)
   else:
      objMsg.printMsg('InitTrustedDL did not complete successfully.')
      result = -1

   return sedType, result

###########################################################################################################
if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
   def fdePowerCycle():
      # Turn on the drive without changing baud rate.
      from Carrier import theCarrier
      from Cell import theCell
      theCarrier.powerOffPort(10)
      theCarrier.powerOnPort(5000, 12000, 30)
      sptCmds.disableAPM()
      objPwrCtrl.incrementLifetimePowerCycleCounter()
      # Set Cell baud rate to 38400. This is the default baud rate for Locked
      # Serial Port FDE Drive and only using this baud rate we can unlock the
      # serial port.
      objMsg.printMsg("Set Cell baud rate to %s." % DEF_BAUD)
      theCell.setBaud(DEF_BAUD)

###########################################################################################################

#*************************************************************************************************
# END END END END END END END END END END END END END END END END END END END END END END END END
# END END END END END END END END END END END END END END END END END END END END END END END END
#*************************************************************************************************
#
