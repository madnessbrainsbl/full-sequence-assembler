#####################################################################
#
# $RCSfile:  $SED-Serial-Personalize.py
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/02 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $Revision: #4 $2.1.0
# $Date: 2016/11/02 $09/24/12
# $Author: chiliang.woo $brandon.haugrud
#
#####################################################################

###########################################################################
###############  SETUP TEST OPERATING OPTIONS AND SETUP  ##################
###########################################################################
import os
from PowerControl import objPwrCtrl

try:
   from Constants import *
   from Test_Switches import testSwitch
   from Drive import objDut as dut
except:
   CN = "file_cfg"
import time, traceback

#Global values that require input to download Bride, IV, IV file location from root location, and Target code#
BridgeCode = 'Bridge_BRV0.lod'
IVFile = 'IV_Della_SAS_A0_9B.trd'
IFFileLocation = os.path.join(UserDownloadsPath, CN) #'C:/var/merlin/dlfiles/file_cfg/' + IVFile
SignedSEDTarget = 'LTV0_signed.lod'
NonSEDTarget = 'F601_CFW.LOD'    #Used if we can get the Nuke to work Serially
unlockFile = None
MAX_PACKET_RETRIES = 250 #cumulative wait time would be 4.3 hours

import random, binascii, struct, base64, time, sys, string, os
if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
   from TdciAccess import makeTDCICall

######################################################################
##########  Contructors for the frames/packets being sent   ##########
######################################################################
trustedFuncID_ifSend = '\x01\x00'
trustedFuncID_ifRecv = '\x02\x00'
SP_packet = '\x01\x00'
ComID_packet = '\xFF\x07'
ComID_discovery = '\x01\x00'
SDBP_headerSend = trustedFuncID_ifSend + SP_packet + ComID_packet
FRAME_retrieve = trustedFuncID_ifRecv + SP_packet + ComID_packet
SED_discovery = trustedFuncID_ifRecv + SP_packet + ComID_discovery
SED_sendReceivePort = 0x08
DITS_sendReceivePort = 0x01

UIDmethod_CS1authenTable   = '\x00\x00\x00\x06\x00\x00\x00\x0C'
UIDmethod_CS2authenTable   = '\x00\x00\x00\x06\x00\x00\x00\x1C'
UIDmethod_CS1setTable      = '\x00\x00\x00\x06\x00\x00\x00\x07'
UIDmethod_CS2setTable      = '\x00\x00\x00\x06\x00\x00\x00\x17'
UIDmethod_CS1getTable      = '\x00\x00\x00\x06\x00\x00\x00\x06'
UIDmethod_CS2getTable      = '\x00\x00\x00\x06\x00\x00\x00\x16'
UIDmethod_removeACE        = '\x00\x00\x00\x06\x00\x00\x00\x0F' #ACE = Access Control Element
UIDmethod_addACE           = '\x00\x00\x00\x06\x00\x00\x00\x0E'
UIDmethod_smUID            = '\x00\x00\x00\x00\x00\x00\x00\xFF'

comPacket_extended_ENTPRSE =  '\x07\xFF\x00\x00'
comPacket_extended_OPAL = '\x07\xFF\x00\x00'
com_fillers = '\x00\x00\x00\x00'
min_Transfer = '\x00\x00\x00\x00'
filler_8bytesZero = com_fillers + com_fillers

sess_ENTPRSEsqNumber = '\x00\x00\x00\x01'
sess_OPALsqNumber = '\x00\x00\x00\x00'
#Used in function above to simplify packets
sess_ack = '\x00\x00\x00\x00\x00\x00\x00\x00'
endPacket = '\xF1\xF9\xF0\x00\x00\x00\xF1'   #Size 7

UID_startSession        =  '\x00\x00\x00\x00\x00\x00\xFF\x02'
UID_adminSP             =  '\x00\x00\x02\x05\x00\x00\x00\x01'
UID_lockingSP           =  '\x00\x00\x02\x05\x00\x01\x00\x01'
#UID_syncSession         =  '\x00\x00\x00\x00\x00\x00\xFF\x03'  #Do we need this ???
UID_authPSID            = '\x00\x00\x00\x09\x00\x01\xFF\x01'
UID_authMSID            = '\x00\x00\x00\x09\x00\x00\x84\x02'
UID_authSID             = '\x00\x00\x00\x09\x00\x00\x00\x06'
UID_authMkrSymK         = '\x00\x00\x00\x09\x00\x00\x00\x04'
UID_authMaintSymk       = '\x00\x00\x00\x09\x00\x01\xFF\x02'
UID_authActivateSymK    = '\x00\x00\x00\x09\x00\x01\xFF\x03'
UID_authEraseMstr       = '\x00\x00\x00\x09\x00\x00\x84\x01'
UID_prsnlzePSID         = '\x00\x00\x00\x0B\x00\x01\xFF\x01'
UID_prsnlzeMSID         = '\x00\x00\x00\x0B\x00\x00\x84\x02'
UID_prsnlzeSID          = '\x00\x00\x00\x0B\x00\x00\x00\x01'
UID_prsnlzeEraseMstr    = '\x00\x00\x00\x0B\x00\x00\x84\x01'
UID_retrDrvMSID         = '\x00\x00\x00\x0B\x00\x00\x84\x02'
UID_spUID               = '\x00\x00\x00\x00\x00\x00\x00\x01'
UID_securityStateCtrl   = '\x00\x01\x00\x03\x00\x00\x00\x00'
UID_makerSymK_AES256    = '\x00\x00\x00\x0F\x00\x01\x00\x01'
UID_maintSymK_AES256    = '\x00\x00\x00\x0F\x00\x01\xFF\x02'
UID_activateSymK_AES256 = '\x00\x00\x00\x0F\x00\x01\xFF\x03'
UID_diagLockingPort     = '\x00\x01\x00\x02\x00\x01\x00\x01'
UID_fwLockingPort       = '\x00\x01\x00\x02\x00\x01\x00\x02'
UID_udsLockingPort      = '\x00\x01\x00\x02\x00\x01\x00\x03'
UID_crossSegFwDnldPort  = '\x00\x01\x00\x02\x00\x01\x00\x0e'
UID_ieee1667Port        = '\x00\x01\x00\x02\x00\x01\x00\x0f'
UID_SetSOM0             = '\x00\x01\x00\x07\x00\x00\x00\x00'
UID_capPersisData       = '\x00\x00\x00\x06\xFF\xFF\x00\x02'
UID_getRandomNumber     = '\x00\x00\x00\x06\x00\x00\x06\x01'
UID_revertAdminSP       = '\x00\x00\x00\x06\x00\x00\x00\x11'
UID_MSIDGet             = '\x00\x00\x00\x08\x00\x00\x8c\x04'
UID_PSIDMakers_MSIDGet  = '\x00\x00\x00\x08\xff\xff\x00\x01'
UID_tper1024            = '\x00\x00\x00\x0C\x00\x01\x00\x05'
UID_tper2048            = '\x00\x00\x00\x0D\x00\x01\x00\x05'
UID_certData1024        = '\x00\x01\x00\x05\x00\x00\x00\x00'
UID_certData2048        = '\x00\x01\x00\x04\x00\x00\x00\x00'
UID_accessCtrlTbl       = '\x00\x00\x00\x07\x00\x00\x00\x00'
UID_storageTbl          = '\x00\x00\x80\x01\x00\x00\x00\x00'
UID_Makers_MSIDGetNew   = '\x00\x00\x00\x08\x00\x00\x00\x03'
UID_activateSDD         = '\x00\x00\x00\x06\xff\xff\x00\x05'
UID_activateISE         = '\x00\x00\x00\x06\xff\xff\x00\x06'
UID_activateSED         = '\x00\x00\x00\x06\xff\xff\x00\x07'
UID_activateFIPS        = '\x00\x00\x00\x06\xff\xff\x00\x08'

TYPE_CS1Pin            = '\x50\x49\x4E'
TYPE_CS1Key            = '\x4B\x65\x79'
TYPE_CS2Pin           = '\x03'

IVDownloadRetried = 0


# ===============================================================================
#Certificate Constructors.  They include their token types atom as the first byte
# ===============================================================================
cert_startRow  = '\xA8\x73\x74\x61\x72\x74\x52\x6F\x77'
rsa_startClm   = '\xAB\x73\x74\x61\x72\x74\x43\x6F\x6C\x75\x6D\x6E'
rsa_endClm     = '\xA9\x65\x6E\x64\x43\x6F\x6C\x75\x6D\x6E'
rsa_pubExp     = '\xA6\x50\x75\x5F\x45\x78\x70'
rsa_mod        = '\xA3\x4D\x6F\x64'
rsa_priveExp   = '\xA6\x50\x72\x5F\x45\x78\x70'
rsa_primeP     = '\xA1\x50'
rsa_primeQ     = '\xA1\x51'
rsa_primeExpP  = '\xA4\x44\x6D\x70\x31'
rsa_primeExpQ  = '\xA4\x44\x6D\x71\x31'
rsa_coeff      = '\xA4\x49\x71\x6D\x70'

startSndSession   = '\x00\x00\x00\x00'
startLckSPSession = '\x00\x00\x00\x01'
PSID_defaultPin = '\x56\x55\x54\x53\x52\x51\x50\x4F\x4E\x4D\x4C\x4B\x4A\x49\x48\x47\x46\x45\x44\x43\x42\x41\x39\x38\x37\x36\x35\x34\x33\x32\x31\x30'   #Size 32
MSID_defaultPin = '\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4A\x4B\x4C\x4D\x4E\x4F\x50\x51\x52\x53\x54\x55\x56'   # Size 32

dictSEDStates = {'00':'SETUP','81':'MANUFACTURE','80':'USE',
                 '01':'DIAGNOSTIC','FF':'FAIL'}


# ===============================
#         ERROR TYPES
# ===============================
dictMethodFailCodes = {'01':'NOT_AUTHORIZED','02':'READ_ONLY','03':'SP_BUSY',
                       '04':'SP_FAILED','05':'SP_DISABLED','06':'SP_FROZEN',
                       '07':'NO_SESSIONS_AVAILABLE','08':'INDEX_CONFLICT','09':'INSUFFICIENT_SPACE',
                       '0a':'INSUFFICIENT_ROWS','0b':'INVALID_COMMAND','0c':'INVALID_PARAMETER',
                       '0d':'INVALID_REFERENCE','0e':'INVALID_SECMSG_PROPERTIES','0f':'TPER_MALFUNCTION',
                       '10':'TRANSACTION_FAILURE','11':'RESPONSE_OVERFLOW','22':'INVALID_TEMPLATE',
                       '23':'SESSION_CLOSING','24':'CACHE_FULL','25':'CACHE_EMPTY','26':'CHALLENGED',
                       '27':'MEDIA_ERROR','28':'NOT_AUTHENTICATED','29':'SESSION_OPENING','2a':'LOCK_ERROR',
                       '2b':'SESSION_ENDING','2c':'CLOSE_WITHOUT_END','2d':'TIMER_ERROR','2e':'STACK_OVERFLOW',
                       '2f':'PACKET_ERROR','30':'INTERFACE_RESET','31':'DOWNLOAD_RESET','32':'INTERFACE_ENDING',
                       '33':'INVALID_STATE_TRANSITION','34':'GRAMMAR_VIOLATION','35':'GET_NOT_AUTHORIZED',
                       '36':'KEY_EXCHANGED'}
# ===============================
#         Vars for Parsing Data
# ===============================
dictUIDs = {
'UIDmethod_CS1authenTable'   : '\x00\x00\x00\x06\x00\x00\x00\x0C',
'UIDmethod_CS2authenTable'   : '\x00\x00\x00\x06\x00\x00\x00\x1C',
'UIDmethod_CS1setTable'      : '\x00\x00\x00\x06\x00\x00\x00\x07',
'UIDmethod_CS2setTable'      : '\x00\x00\x00\x06\x00\x00\x00\x17',
'UIDmethod_CS1getTable'      : '\x00\x00\x00\x06\x00\x00\x00\x06',
'UIDmethod_CS2getTable'      : '\x00\x00\x00\x06\x00\x00\x00\x16',
'UIDmethod_removeACE'        : '\x00\x00\x00\x06\x00\x00\x00\x0F',
'UIDmethod_addACE'           : '\x00\x00\x00\x06\x00\x00\x00\x0E',
'UIDmethod_smUID'            : '\x00\x00\x00\x00\x00\x00\x00\xFF',
'UID_startSession'        : '\x00\x00\x00\x00\x00\x00\xFF\x02',
'UID_adminSP'             : '\x00\x00\x02\x05\x00\x00\x00\x01',
'UID_lockingSP'           : '\x00\x00\x02\x05\x00\x01\x00\x01',
'UID_enableMaintSymK'     : '\x00\x00\x00\x09\x00\x01\xFF\x02',
'UID_authPSID'            : '\x00\x00\x00\x09\x00\x01\xFF\x01',
'UID_authMSID'            : '\x00\x00\x00\x09\x00\x00\x84\x02',
'UID_authSID'             : '\x00\x00\x00\x09\x00\x00\x00\x06',
'UID_authMkrSymK'         : '\x00\x00\x00\x09\x00\x00\x00\x04',
'UID_authMaintSymk'       : '\x00\x00\x00\x09\x00\x01\xFF\x02',
'UID_authEraseMstr'       : '\x00\x00\x00\x09\x00\x00\x84\x01',
'UID_prsnlzePSID'         : '\x00\x00\x00\x0B\x00\x01\xFF\x01',
'UID_prsnlzeMSID'         : '\x00\x00\x00\x0B\x00\x00\x84\x02',
'UID_prsnlzeSID'          : '\x00\x00\x00\x0B\x00\x00\x00\x01',
'UID_prsnlzeEraseMstr'    : '\x00\x00\x00\x0B\x00\x00\x84\x01',
'UID_retrDrvMSID'         : '\x00\x00\x00\x0B\x00\x00\x84\x02',
'UID_spUID'               : '\x00\x00\x00\x00\x00\x00\x00\x01',
'UID_securityStateCtrl'   : '\x00\x01\x00\x03\x00\x00\x00\x00',
'UID_makerSymK_AES256'    : '\x00\x00\x00\x0F\x00\x01\x00\x01',
'UID_maintSymK_AES256'    : '\x00\x00\x00\x0F\x00\x01\xFF\x02',
'UID_diagLockingPort'     : '\x00\x01\x00\x02\x00\x01\x00\x01',
'UID_fwLockingPort'       : '\x00\x01\x00\x02\x00\x01\x00\x02',
'UID_udsLockingPort'      : '\x00\x01\x00\x02\x00\x01\x00\x03',
'UID_crossSegFwDnldPort'  : '\x00\x01\x00\x02\x00\x01\x00\x0e',
'UID_ieee1667Port'        : '\x00\x01\x00\x02\x00\x01\x00\x0f',
'UID_SetSOM0'             : '\x00\x01\x00\x07\x00\x00\x00\x00',
'UID_capPersisData'       : '\x00\x00\x00\x06\xFF\xFF\x00\x02',
'UID_getRandomNumber'     : '\x00\x00\x00\x06\x00\x00\x06\x01',
'UID_revertAdminSP'       : '\x00\x00\x00\x06\x00\x00\x00\x11',
'UID_MSIDGet'             : '\x00\x00\x00\x08\x00\x00\x8c\x04',
'UID_PSIDMakers_MSIDGet'  : '\x00\x00\x00\x08\xff\xff\x00\x01',
'UID_tper1024'            : '\x00\x00\x00\x0C\x00\x01\x00\x05',
'UID_tper2048'            : '\x00\x00\x00\x0D\x00\x01\x00\x05',
'UID_certData1024'        : '\x00\x01\x00\x05\x00\x00\x00\x00',
'UID_certData2048'        : '\x00\x01\x00\x04\x00\x00\x00\x00',
'UID_accessCtrlTbl'       : '\x00\x00\x00\x07\x00\x00\x00\x00',
'UID_storageTbl'          : '\x00\x00\x80\x01\x00\x00\x00\x00',
'UID_Makers_MSIDGetNew'   : '\x00\x00\x00\x08\x00\x00\x00\x03'
}


OPAL = 'OPAL'
ENTERPRISE = 'ENTPRSE'

class SEDScriptVar:
    #'enableDebugstatMsg' used to statMsg the raw packets being sent to and from the drive for CM/Gemini setup while debugging.
    #Frames will only be shown if the showFrame value is set is sendPacket() and getPacket() and enableDebugstatMsg=1
    enableDebugstatMsg = 1
    enableCM = 1
    enableISE = 0
    driveType = ENTERPRISE   #Drive Types:  OPAL and ENTERPRISE
    interfaceType = 'SATA'
    coreSpec = 1          #Core Specs:   1 and 2
    masterSymKType = 2    #1: Triple Des     2:AES256
    secureBaseDriveType = 1
    activateSupport = 0 #Used to determine if activate method is supported
    activateType = 'SDD'
    currActiveConfig = ''
    suppActiveConfigTypes = []
    currentSecureState = 0x55
    tcgVersion = 1
    autoDetectRan = 0

    frame1Type = ''
    packetSaveSent1 = ''
    packetSaveRecev1 = ''
    frame2Type = ''
    packetSaveSent2 = ''
    packetSaveRecev2 = ''

    sessionNumber = ''
    global_fisMSID = ''
    global_fisPSID = ''
    global_driveMSID = ''

    preFrameLength = 0

    UIDmethod_authenTable = UIDmethod_CS1authenTable
    UIDmethod_setTable = UIDmethod_CS1setTable
    UIDmethod_getTable = UIDmethod_CS1getTable
    comPacket_extended = comPacket_extended_ENTPRSE
    sess_sqNumber = sess_ENTPRSEsqNumber

    TYPE_pin = TYPE_CS1Pin
    TYPE_key = TYPE_CS1Key

    COMPacket = com_fillers + comPacket_extended + com_fillers + min_Transfer
    PacketHeader = SDBP_headerSend + COMPacket    #Size 22

    def reInitCoreSpecRelatedVars(self):
        if self.coreSpec == 1:
            self.UIDmethod_authenTable = UIDmethod_CS1authenTable
            self.UIDmethod_setTable = UIDmethod_CS1setTable
            self.UIDmethod_getTable = UIDmethod_CS1getTable
            self.comPacket_extended = comPacket_extended_ENTPRSE
            self.sess_sqNumber = sess_ENTPRSEsqNumber
            self.TYPE_pin = TYPE_CS1Pin
            self.TYPE_key = TYPE_CS1Key
        elif self.coreSpec == 2:
            self.UIDmethod_authenTable = UIDmethod_CS2authenTable
            self.UIDmethod_setTable = UIDmethod_CS2setTable
            self.UIDmethod_getTable = UIDmethod_CS2getTable
            self.comPacket_extended = comPacket_extended_OPAL
            self.sess_sqNumber = sess_OPALsqNumber
            self.TYPE_pin = TYPE_CS2Pin
            self.TYPE_key = TYPE_CS2Pin


        self.COMPacket = com_fillers + self.comPacket_extended + com_fillers + min_Transfer
        self.PacketHeader = SDBP_headerSend + self.COMPacket    #Size 22

sedVar = SEDScriptVar()

#####################################################################################
################  END OF SETUP TEST OPERATING OPTIONS AND SETUPS  ###################
#####################################################################################

# ================================================================#
# ================================================================#
# =========  Start of SED FUNCTION for main functions ============#
# ================================================================#
# ================================================================#

#;###########################################################################
#;#########  Used to personalize the entire drive to defaults if   ##########
#;#########  currently using personalized FIS MSID values or to    ##########
#;#########  FIS MSID value if currently using defaults.  Does     ##########
#;#########  this for MSID, PSID, EraseMaster, and all the Bands   ##########
#;###########################################################################
def fullPersonalization(CORE_SPEC,CUSTOMER_OPTION,OPAL_SSC_SUPPORT,SYMK_KEY_TYPE,REPORTING_MODE,INTERFACE='SATA',TCG_VERSION=1,FEATURE_OPTIONS=0,ACTIVATE=0): #Similar to test 577 with code download when not using CM.  Excludes writing certifcates and includes SED format

    sedVar.global_fisPSID = ''

    match575SSCParamsToSPTest(coreSp=CORE_SPEC,opalSupp=OPAL_SSC_SUPPORT, symkKey=SYMK_KEY_TYPE, reportOp=REPORTING_MODE,custMode=CUSTOMER_OPTION,interfaceType=INTERFACE,activateMthd=ACTIVATE,tcgType=TCG_VERSION)

    objPwrCtrl.powerCycle( useESlip=1 ) 
    statMsg(msg = 'Beginning Drive Personalization',masterstatMsg = 1)
    SSCDriveVerify(binResponse = True)
    SEDdiscovery()
    authenStartSess()
    currState = getStateTable()
    if currState == '\x00':   #Used to know if drive has been personalized or not
        defaultMSID = 1
        persToDefMSID = 0
    else:
        defaultMSID = 1
        persToDefMSID = 0
    authenSIDSMaker(default = defaultMSID, firstRun = defaultMSID)
    authenSymK(firstRunDef = defaultMSID, makerSymK = 0, maintSymK = 1,symKType = sedVar.masterSymKType,activateSymK = 0) #firstRunDef should = 1 only on the very first personalization of the drive
    if currState != '\x81':
        if currState == '\x80' or currState == '\xFF':  #need to cycle through states drive can only get to Manufature State from Setup State
            changeStates(01)
        if currState == '\x80' or currState == '\xFF' or currState == '\x01':  # if wasn't in Diag state it is now and needs to go to Setup State
            changeStates(00)
        changeStates(81)
    if getStateTable(displayState = 0) != '\x81':
        abort(failVal = 14620, failStr = 'Was unable to change to Manufacture State to Personalize the Security Drive')
    personlizeSIDS(toDefault = persToDefMSID)

    if sedVar.secureBaseDriveType == 0 or sedVar.activateSupport == 1: #Write certificate(s) for all TCG1 products except SDnD and all TCG2 producuts if activate is supported
        if (TCG_VERSION == 1): #Write both certificates
            CustomRequestGetTDCertifiedKeyPairHandler(1,coreSpecType = sedVar.coreSpec)
            CustomRequestGetTDCertifiedKeyPairHandler(2,coreSpecType = sedVar.coreSpec)
        else:   #TCG2 Write only 2048 certificate
            CustomRequestGetTDCertifiedKeyPairHandler(2,coreSpecType = sedVar.coreSpec)

    personalizeSymK(makerSymK = 1, maintSymK = 0, activateSymK = 0)
    personalizeSymK(makerSymK = 0, maintSymK = 1, activateSymK = 0)
    if sedVar.activateSupport:
        authenSymK(firstRunDef = defaultMSID, makerSymK = 0, maintSymK = 0,symKType = sedVar.masterSymKType,activateSymK = 1)
        personalizeSymK(makerSymK = 0, maintSymK = 0, activateSymK = 1)

    if sedVar.activateSupport == 0:
        if sedVar.enableISE == 1 and sedVar.driveType != OPAL:
            setISE_ACE()
        if sedVar.secureBaseDriveType == 1:
            setSDD_ACE()
    else:
        TCGActivate(tcgType = sedVar.activateType)
        sedVar.autoDetectRan = 0
        SEDdiscovery()

    enableDisableFwLOR(lockPort = 0)
    lockUnlockFwPort(lockPort = 0)
    lockUnlockDiagPort(lockPort = 1)
    lockUnlockUDSPort(lockPort = 1)

    if sedVar.secureBaseDriveType == 1 and TCG_VERSION == 1:
        lockUnlockCrossSegFWDnldPort(lockPort = 1)
    if TCG_VERSION == 2:
        lockUnlockCrossSegFWDnldPort(lockPort = 1) #All TCG2 products support CSFW download port. 

    if ((FEATURE_OPTIONS & 4) == 4) and ((FEATURE_OPTIONS & 7) > 4):  #If we set the 3rd bit to indicate that we want to modify this port value we must also specify the setting for the port
        if sedVar.activateSupport and sedVar.secureBaseDriveType == 1:
            statMsg("Skip IEEE1667 setting for ActivateSDnD")
        else:
            enableDisableIEEE1667Port(lockPort = 0)

            if ((FEATURE_OPTIONS & 1) == 1):
                lockUnlockIEEE1667Port(lockPort = 0)  #Activate Port
            elif ((FEATURE_OPTIONS & 2) == 2):
                lockUnlockIEEE1667Port(lockPort = 1)  #Deactivate Port


    if sedVar.driveType == ENTERPRISE and TCG_VERSION == 1:
        closeSession()  #closing session if we need to start a locking sp session
        #Personalize EraseMaster and Bands
        authenStartSess(lockingSP = 1) #Open a new Locking SP Session for personlize of EraseMaster and Bands
        authenEraseMaster(fromDefValue = defaultMSID)
        personalizeEraseMaster(toDefValue = persToDefMSID)
        personalizeLockingBands(fromDefVal = defaultMSID, toDefVal = persToDefMSID)
        closeSession() #closing locking SP session

        authenStartSess()
        authenSIDSMaker(default = persToDefMSID, firstRun = 0)

        setSOM0()

    capturePersisData()

    if sedVar.interfaceType == 'SATA':
        getStateTable()
        revertAdminSP()  #Used to set the ATA Master Password, can be ran
        #Need to start session after revertAdminSP() closes it
        authenStartSess()
        authenSIDSMaker(default = 0, firstRun = 0)
        capturePersisData()  #Capture again after setting ATA Master Password

    closeSession()
    statMsg(msg = 'Sucessfully Completed Personalization',masterstatMsg = 1)

    #SerialFormatCertifyFactory()

#;###############################################################
#;#########  Used for customer verification of drive   ##########   ONLY USE FOR ENTERPRISE DRIVES!!! HASN'T BEEN DEVELOPED FOR OPAL
#;###############################################################
def securityConfigVerification(CORE_SPEC,CUSTOMER_OPTION,OPAL_SSC_SUPPORT,SYMK_KEY_TYPE,REPORTING_MODE,INTERFACE='SATA',TCG_VERSION=1,ACTIVATE=0):

    match575SSCParamsToSPTest(coreSp=CORE_SPEC,opalSupp=OPAL_SSC_SUPPORT, symkKey=SYMK_KEY_TYPE, reportOp=REPORTING_MODE,custMode=CUSTOMER_OPTION,interfaceType=INTERFACE,activateMthd=ACTIVATE,tcgType=TCG_VERSION)

    objPwrCtrl.powerCycle( useESlip=1 ) 
    statMsg(msg = 'Beginning Security Config Verification',masterstatMsg = 1)
    SSCDriveVerify(binResponse=True)
    SEDdiscovery()
    authenStartSess()
    authenSIDSMaker(default = 0, firstRun = 0, handleFail=1)
    currState = getStateTable()
    if currState != '\x80':
        changeStates(80)
        currState = getStateTable()
        if currState != '\x80':
            raise Exception('Drive is not in USE state.  Reprocess drive')
    if sedVar.driveType == ENTERPRISE:
        setSOM0()

    capturePersisData()
    #  Check Diag, FW, UDS, CSFW, ieee1667 port Locking and LOR
    checkPortLocking(UIDname=UID_diagLockingPort,configEnableLORPort=True,configEnablePortLocking=True)
    checkPortLocking(UIDname=UID_fwLockingPort,configEnableLORPort=False,configEnablePortLocking=False)
    dut.driveattr['DLP_SETTING'] = 'UNLOCKED'   #Passed means fw download port is unlocked as the checkPortLocking set to False
    checkPortLocking(UIDname=UID_udsLockingPort,configEnableLORPort=True,configEnablePortLocking=True)
    if (TCG_VERSION == 2):  #All TCG2 products support CSFW download port.
        checkPortLocking(UIDname=UID_crossSegFwDnldPort,configEnableLORPort=True,configEnablePortLocking=True)
    elif sedVar.secureBaseDriveType == 1:
       checkPortLocking(UIDname=UID_crossSegFwDnldPort,configEnableLORPort=True,configEnablePortLocking=True)

    if dut.driveattr['IEEE1667_INTF'] in [None,'NA','NONE','ACTIVATED']:
       checkPortLocking(UIDname=UID_ieee1667Port,configEnableLORPort=False,configEnablePortLocking=False)
    else:                                                                                                
       checkPortLocking(UIDname=UID_ieee1667Port,configEnableLORPort=False,configEnablePortLocking=True)

    #Check Band Configs
    if sedVar.driveType == ENTERPRISE:
        closeSession()

        authenStartSess(lockingSP = 1)
        authenEraseMaster(fromDefValue = 0)
        checkBandLockingValues(startAtBand = 0, endBand = 16,LOCK_ON_RESET=0,WRITE_LOCK_ENABLED=0,READ_LOCK_ENABLED=0,WRITE_LOCKED=1,READ_LOCKED=1,RANGE_LENGTH=0,RANGE_START=0)
        checkBandEnableValues(startAtBand = 0, endBand = 2,BAND_ENABLED=1)
        checkBandEnableValues(startAtBand = 2, endBand = 16,BAND_ENABLED=0)

        closeSession()

        authenStartSess()
        authenSIDSMaker(default = 0, firstRun = 0)
        setSOM0()

    lockUnlockDiagPort(lockPort = 0)
    lockUnlockDiagPort(lockPort = 1)
    #Verify SOM0 is set

    packet = getTable(UID = UID_SetSOM0)

    SOMstate = int(binascii.hexlify(packet[64:65]),16)   #SOM State is indexed into this packet

    if SOMstate != 0:
        failType = "Checking SOM State failed. Expected SOM State to be 0 but was actually %d" %SOMstate
        abort(failVal = 10158, failStr=failType)

    closeSession()
    statMsg(msg = 'Sucessfully Completed Security Config Verification',masterstatMsg = 1)



# ===================================================================
# statMsg statment types
# ===================================================================
def tMsg(msg):
  TraceMessage(msg)

def statMsg(msg,masterstatMsg = sedVar.enableDebugstatMsg):
    #TraceMessage(msg)
    if masterstatMsg == 1:
        if sedVar.enableCM == 0:
            ScriptComment(msg)
        else:
            ScriptComment(msg)

# ===================================================================
# getSID(...):
# Gets/generates a Secure ID (i.e. 'PSID' or 'MSID') that is statMsged
# on the drive label and stored internally on the drive in the EF_SID
# file.  It will also create the appropriate drive attribute in FIS.
# ===================================================================
def getSID(updateAttrs=1):  # actually is getMSID

  sidStatus = "1" # 0 = get exisiting SID from FIS
                  # 1 = calculate new SID
  sidLength = 32  # =32, per change to TCG Storage Architecture Core Spec for IBM only so far
  charChoices = ['H','U','7','C','J','9','T','5','R','B',\
                 'G','M','E','0','F','Z','4','8','Y','K',\
                 '2','L','V','D','S','1','A','W','3','Q',\
                 'X','6','P','N']
  sidStr = ''
  if DriveAttributes.has_key('TD_SID') and not DriveAttributes['TD_SID'] == 'NONE' :
    sidStr = DriveAttributes['TD_SID']
    statMsg("FIS TD_SID (PSID) from getSID")
    sidStatus = "0"
  else:
    random.shuffle(charChoices)
    random.seed()
    for i in range(0, sidLength):
      sidStr += charChoices[int(random.random() * 34)]
    if updateAttrs:
      statMsg("Virgin TD_SID")
      DriveAttributes['TD_SID'] = sidStr
      dut.driveattr['TD_SID'] = sidStr
    # RequestService("PutAttributes", ({"TD_SID": sidStr}, "FIN2"))
  return sidStatus,sidStr

# ===================================================================
# getMSIDfromAttributeMSID(...):
# ===================================================================
def getMSIDfromAttributeMSID(updateAttrs=1):

  sidStatus = "1" # 0 = get exisiting SID from FIS
                  # 1 = calculate new SID
  sidLength = 32  # =32, per change to TCG Storage Architecture Core Spec for IBM only so far
  charChoices = ['H','U','7','C','J','9','T','5','R','B',\
                 'G','M','E','0','F','Z','4','8','Y','K',\
                 '2','L','V','D','S','1','A','W','3','Q',\
                 'X','6','P','N']
  sidStr = ''
  if DriveAttributes.has_key('MSID') and testSwitch.FE_0199808_231166_P_SEND_MSID_TO_FIS:
    sidStr = DriveAttributes['MSID']
    statMsg("FIS MSID from getSID    = %s" % sidStr)
    sidStatus = "0"
  else:
    random.shuffle(charChoices)
    random.seed()
    for i in range(0, sidLength):
      sidStr += charChoices[int(random.random() * 34)]
    if updateAttrs:
       if testSwitch.FE_0199808_231166_P_SEND_MSID_TO_FIS:
          dut.driveattr['MSID'] = sidStr
          DriveAttributes['MSID'] = sidStr
  return sidStatus,sidStr

# ===================================================================
# CustomRequestGetTDCertifiedKeyPairHandler():
# customer handler for results key of 3X - Request Certified Key Pair
# ===================================================================
def CustomRequestGetTDCertifiedKeyPairHandler(cert_type, coreSpecType = sedVar.coreSpec):
  statMsg( "*** Request TD Certified Key Pair" )
  statMsg( "Entering Custom Request Mfg Key Auth handler - 38 - get certified TD key pair" )
  d = ['primeExponentP','primeExponentQ','crtCoefficient','montModulus','pubExp','montPrimeQ','montPrimeP','primeQ',
       'primeP','privExp','modulus','RSAPrivateKey','Certificate']
  if cert_type == 0:
   if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      import ScrCmds
      ScrCmds.raiseException(11044, "GetCertifiedKeyPair of cert_type 0 unsupported")
   else:
      statMsg("RequestService('GetCertifiedKeyPair',('HDASerialNumber','SIGN','1.2.3.4.5.6.7.8.9.0))")
      method,prms = RequestService("GetCertifiedKeyPair",(HDASerialNumber,'SIGN','1.2.3.4.5.6.7.8.9.0'))
  else:
    if cert_type == 1:
      key_type = 'RSA1024PubExp17'
      UID_certType = UID_certData1024
      UID_RSAType = UID_tper1024
      updateType = '1024'
    else:
      key_type = 'RSA2048PubExp65537'
      UID_certType = UID_certData2048
      UID_RSAType = UID_tper2048
      updateType = '2048'
    statMsg( "RequestService('`',('ser no.','SIGN','1.2.3.4.5.6.7.8.9.0))" )

    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
       name, prms = makeTDCICall('requestTDCertKeyPair', HDASerialNumber, 'SIGN', cert_type, key_type, '0')
    else:
       name, prms = RequestService('GetCertifiedTDKeyPair',(HDASerialNumber,'SIGN',2 ,key_type, '0',))

  statMsg("name: %s; prms: %s"%(name,prms,))

  if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
    statMsg("%s" %prms)
    #Format RSA values and Certificate
    keys={}
    for x in d:
      #if sedVar.enableDebugstatMsg == 1:
      #  statMsg("Current string is %s", % x)
      if prms.has_key(x):
        statMsg("field: %s"%x)
        responseString = prms[x]
        spEnableKeyString = binascii.b2a_hex(base64.b64decode(responseString))  #binary to ascii decoded string
        statMsg("x = %s" % spEnableKeyString)                                      #statMsg the ascii string
        spEnableKey = binascii.a2b_hex(spEnableKeyString)
        statMsg("x = %i bytes" % len(spEnableKey))                          #statMsg the length of the ascii string
        tempKey = spEnableKey               #Set the converted values in 'keys'.  Need this format to send the frame to the drive
        overall_len = len(spEnableKey)
        if tempKey[0] == '\x00':
            tempKey = tempKey[1:]
        keys[x] = tempKey
        displayFrame(keys[x])
      else:
        statMsg("key doesn't exist")                           #statMsg the ascii string


    if sedVar.enableDebugstatMsg == 1:
        statMsg("Prep before sending Cert/RSA Packets")



    #Personalize RSA/Cert Values
    rsaDictEntries = ['pubExp','modulus','privExp','primeP','primeQ','primeExponentP','primeExponentQ','crtCoefficient']
    if coreSpecType == 1:
        rsaDictNameType = {'pubExp':rsa_pubExp,'modulus':rsa_mod,'privExp':rsa_priveExp,'primeP':rsa_primeP,'primeQ':rsa_primeQ,
                            'primeExponentP':rsa_primeExpP,'primeExponentQ':rsa_primeExpQ,'crtCoefficient':rsa_coeff}
    elif coreSpecType == 2:
        rsaDictNameType = {'pubExp':'\x04','modulus':'\x05','privExp':'\x06','primeP':'\x07','primeQ':'\x08',
                            'primeExponentP':'\x09','primeExponentQ':'\x0A','crtCoefficient':'\x0B'}
    certificate = str(keys['Certificate'])
    #Calc how many packets to send
    certLength = len(certificate)
    if (certLength%370) == 0:
        iterations = certLength/370
    else:
        iterations = (certLength/370) + 1
    for i in range(0,iterations):
        if i == (iterations-1):
            certPacket = certificate[i*370:certLength]
        else:
            certPacket = certificate[i*370:((i+1)*370)]
        sessionType = 'Modify %s Cerficate Part %s' %(updateType, i)
        certFrame = prependAtom(preString = certPacket, cont = 1)
        certLocation = i*370
        hexCert = hex(certLocation)
        if((certLocation<15) or ((certLocation>255) and (certLocation<=4095))):
            certLocation = '0' + hexCert[2:]
        elif(certLocation<=256):
            certLocation = hexCert[2:]
        certLocationFinal = binascii.unhexlify(certLocation)
        certLocationFinal = prependAtom(preString = certLocationFinal, cont = 0)
        packet = createPacket(type = 'certificate', UID = UID_certType , mthdUID = sedVar.UIDmethod_setTable, credential = certFrame, location = certLocationFinal)
        sendPacket(frame = packet, m_type = sessionType)
        getPacket(m_type = sessionType,checkRcvStat = 1)

    for x in rsaDictEntries:
        if prms.has_key(x):
            rsaPacket = str(keys[x])
        else:
            statMsg("Key %s does not exist in RSA Packet Recieved for TDCI" %x)
        rsaFrame = prependAtom(preString = rsaPacket, cont = 0)
        sessionType = 'Modify %s RSA' %x
        packet = createPacket(type = 'RSA', UID = UID_RSAType , mthdUID = sedVar.UIDmethod_setTable, credential = rsaFrame, rsaType = rsaDictNameType[x])
        sendPacket(frame = packet, m_type = sessionType)
        getPacket(m_type = sessionType,checkRcvStat = 1)

  else:
    statMsg('[34]' + __name__ + "data from server is garbled")
    statMsg("Leaving Custom Request Certified Key Pair")

# ===================================================================
# CustomRequestGetSCSA_FactoryAsset():
# customer handler for results key of  -
# ===================================================================
def CustomRequestGetSCSA_FactoryAsset(dataPacket = ''):
  statMsg(msg = "*** Request SCSA Factory Asset")

  Payload1 = dataPacket[:20]
  Payload2 = dataPacket[20:]

# Must be exactly 20 bytes
#  Payload1 = "\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04"
# Must be exactly 60 bytes
# Payload2 = "\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04"

  if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
      method, prms = makeTDCICall( 'getUniqueSCSAAssets', HDASerialNumber, 1, '0', ('NONCE',Payload1), ('NONCE',Payload2))
  else:
      method,prms = RequestService('GetUniqueSCSAAssets',(HDASerialNumber, 1, '0', ('NONCE',Payload1), ('NONCE',Payload2)))

  #Length of data is 5440
  decodedResp = base64.b64decode(prms['SCSAAssetResponse'])
  return decodedResp

##############################################################################
##########   Used to statMsg response packets in an organized method  ##########
##############################################################################
def statMsgSedBin(binData,lineWidth=16,display=1):
    if testSwitch.virtualRun:
       display = 0
    chars = [binascii.hexlify(ch) for ch in binData]
    __statMsgSedBin(chars,lineWidth,manditoryDisplay=display)
    if display == 1 or sedVar.enableDebugstatMsg == 1:
        statMsg("\n")

def __statMsgSedBin(chars,lineWidth,manditoryDisplay=1):
    result = " "
    while chars:
        for group in range(lineWidth/8):
            charSet,chars = chars[:8],chars[8:]
            result = "%s%s " % (result," ".join(charSet),)
            if not chars: break
        result = "%s\n"%(result.strip(),)
    if manditoryDisplay == 1:  # Used to statMsg packets even if debug statMsg is off and packet fails.
        statMsg("%s"%result.strip())

####################################################################
displayFrame = statMsgSedBin
####################################################################

####################################################################################
##########   Used to Assign 575 Param Values to Serial Port Test Params   ##########
####################################################################################
def match575SSCParamsToSPTest(coreSp,opalSupp,symkKey,reportOp,custMode,interfaceType,activateMthd,tcgType):
    if coreSp == 0 or coreSp == 1:
        sedVar.coreSpec = 1
    elif coreSp == 2:
        sedVar.coreSpec = 2
    else:
        abort(failVal = 14513, failStr='Input paramter for CORE_SPEC is not valid')

    if opalSupp == 1:
        sedVar.driveType = OPAL
    elif opalSupp == 0:
        sedVar.driveType = ENTERPRISE
    else:
        abort(failVal = 14513, failStr='Input paramter for OPAL_SCC_SUPPORT is not valid')

    if symkKey == 1 or symkKey == 2:
        sedVar.masterSymKType = symkKey
    else:
        abort(failVal = 14513, failStr='Input paramter for SYMK_KEY_TYPE is not valid')

    if reportOp == 0 or reportOp == 1:
        sedVar.enableDebugstatMsg = reportOp
    else:
        sedVar.enableDebugstatMsg = 1

    if custMode == 0 or custMode == 1 or custMode == 4:  #custMode = 4 is FIPS and personalized like SED
        sedVar.enableISE = 0
        sedVar.secureBaseDriveType = 0
    elif custMode == 2:
        sedVar.enableISE = 0
        sedVar.secureBaseDriveType = 1
    elif custMode == 3:
        sedVar.enableISE = 1
        sedVar.secureBaseDriveType = 0
    else:
        abort(failVal = 14513, failStr='Input paramter for CUSTOMER_OPTION is not valid')
    if activateMthd == 1 and tcgType >= 2:  #Only Activate is only support for TCG2
        sedVar.activateSupport = 1

        if custMode < 2:
            sedVar.activateType = 'SED'
        elif custMode == 2:
            sedVar.activateType = 'SDD'
        elif custMode == 3:
            sedVar.activateType = 'ISE'
        elif custMode == 4:
            sedVar.activateType = 'FIPS'
        else:
            abort(failVal = 14513, failStr='Input paramter for CUSTOMER_OPTION is not valid')
    else:
        sedVar.activateSupport = 0

    if tcgType > 0 and tcgType <= 3:
        sedVar.tcgVersion = tcgType
    else:
        failMsg = "Input paramter for TCG_VERSION is not valid.  Input was given %d" %(tcgType)
        abort(failVal = 14513, failStr=failMsg)

    sedVar.interfaceType = interfaceType

    if sedVar.enableDebugstatMsg:
        statMsg("sedVar.enableISE %s" % (sedVar.enableISE,))
        statMsg("sedVar.secureBaseDriveType %s" % (sedVar.secureBaseDriveType,))
        statMsg("sedVar.driveType %s"           % (sedVar.driveType,))
        statMsg("sedVar.masterSymKType %s" % (sedVar.masterSymKType,))
        statMsg("sedVar.coreSpec %s" % (sedVar.coreSpec,))


    sedVar.reInitCoreSpecRelatedVars()

#############################################################################
##########   Used to spin the drive up and set BaudRate Serially   ##########
#############################################################################
def pwrCylSpinUp(baudRate=1228000,issueSpin=1):
    if sedVar.interfaceType == 'SAS':
        CTRL_Z  = '\x1A'
        DriveOff(5)
        DriveOn(5000,12000,5)
        ScriptPause(5)
        UseESlip(1)
        SetBaudRate(38400)
        SetESlipBaud(baudRate)

        if issueSpin==1:
            PChar(CTRL_Z)
         #   PChar(CTRL_Z)
            time.sleep(9)  #Need to allow time for drive to spin up before sending packets
        #    PChar(CTRL_T)

    else:
        DriveOff(5)
        DriveOn(5000,12000,10)
        #Send(' ')    #Doesn't work with Opal Drives and not necessary for PSG products
        #time.sleep(3)
        #get(size=1)
        #time.sleep(1)
        UseESlip(1)
        SetESlipBaud(baudRate)
        try:
            SetESlipBaud(baudRate)
        except:
            ScriptPause(5)
            SetESlipBaud(baudRate)
        time.sleep(5)

##################################################################
##########   Used to send packets/frames to the drive   ##########
##################################################################
def sendPacket(frame, m_type, showFrame = 1, ditsCommand = 0):
   if sedVar.enableDebugstatMsg == 0:   #Used to save last packets incase not statMsging debug and commands fail
      updateDebugPackets(data = frame, packType = m_type, sentPack = 1)
   if ditsCommand == 1:
      SendBuffer(frame, toAddress = DITS_sendReceivePort, fromAddress = DITS_sendReceivePort, checkSRQ = 0)
      dispFrame = frame[0:]
   else:
      SendBuffer(frame, toAddress = SED_sendReceivePort, fromAddress=SED_sendReceivePort, checkSRQ = 0)
      dispFrame = frame[6:]
      #dispFrame = frame[0:]   #Used to show more data in packet for debug for Asif
   if showFrame == 1:
      statMsg("Sent %s" % m_type)
      displayFrame(dispFrame)
   time.sleep(.2)  #Keep Drive from hanging up

##############################################################################################
##########   Used to retrieve packets/frames from the drive after sending request   ##########
##############################################################################################
def getPacket(m_type, showFrame = 1, checkRcvStat = 0, ditsCommand = 0, retrieveFrame = FRAME_retrieve, abortBadStatus = 1, ditsAbortBadStatus = 0, changeToAddressTo = DITS_sendReceivePort, rtnRawPacket = 0):
   startTime = time.time()
   time.sleep(2)
   if ditsCommand != 1:
      for getRetry in xrange(3):
         try:
            #retries for ascii data flushed
            for x in range(3):
               try:
                  SendBuffer(retrieveFrame, toAddress=SED_sendReceivePort, fromAddress=SED_sendReceivePort, checkSRQ=0)
                  break
               except:
                  statMsg("SendBuffer failed: %s" % traceback.format_exc())
            else:
               raise
            #if testSwitch.virtualRun:
            #    responseFrame = "\x02\x00\x01\x00\xff\x07\x00\x00\x00\x00\x07\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x28\xff\xff\xfc\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xfa\x00\x81\x00"
            #else:
            for x in xrange(3):
               try:
                  responseFrame = ReceiveBuffer(checkSRQ=0, fromAddress=SED_sendReceivePort, toAddress=SED_sendReceivePort, timeout=15, ignMismatch=0)
                  break
               except:
                  statMsg("ReceiveBuffer Failed: %s" % (traceback.format_exc(),))
            else:
               raise
            break
         except:
            statMsg("receive sequence failed: %s" % (traceback.format_exc(),))

      else:
         raise

      for i in xrange(0, MAX_PACKET_RETRIES ):   #Cycle through MAX_PACKET_RETRIES times in case the drive hasn't processed the 'ReceiveBuffer()' with valid data yet
         if (binascii.hexlify(responseFrame[25:26])) != '00':
            break
         else:
            statMsg("data from drive for retry(%d)\n%s" % (i, repr(responseFrame),))
            if i > 5:
               statMsg("Sending eslip reset to drive with C0's")
               PBlock('\xC0'*8)
            try:
               SendBuffer(retrieveFrame, toAddress=SED_sendReceivePort, fromAddress=SED_sendReceivePort, checkSRQ=0)
               time.sleep(i/2)
               responseFrame = ReceiveBuffer(checkSRQ=0, fromAddress=SED_sendReceivePort, toAddress=SED_sendReceivePort, timeout=15, ignMismatch=0)
            except:
               statMsg("SendBuffer/ReceiveBuffer failed: %s" % traceback.format_exc())
      else:
         #exhausted retries
         msg = 'Error occured in getPacket() when processing %s .  Response packet has a length of ZERO' % m_type
         statMsg(msg)
         statMsg("Receive Security Frame time: %d seconds" % ( time.time() - startTime ) )
         abort(failVal = 14619, failStr = msg)

      statMsg("Receive Security Frame time: %d seconds" % ( time.time() - startTime ) )

   if ditsCommand == 1:
       #if testSwitch.virtualRun:
       #    responseFrame = "\x02\x00\x01\x00\xff\x07\x00\x00\x00\x00\x07\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x28\xff\xff\xfc\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xfa\x00\x81\x00"
       #else:
       responseFrame = ReceiveBuffer(checkSRQ=0, fromAddress=DITS_sendReceivePort, toAddress=changeToAddressTo, timeout=15)

   if sedVar.enableDebugstatMsg == 0:
      updateDebugPackets(data = responseFrame, packType = m_type, recevPack=1)  #Udpate packets incase fails and not statMsging debug code
   if showFrame == 1:
      if sedVar.enableDebugstatMsg == 1:
         statMsg("Retrieved %s Packet" % m_type)
      if ditsCommand == 1:
         displayFrame(responseFrame[0:])
      else:
         displayFrame(responseFrame[6:])
   if ditsCommand == 0:
      #Check used to Verify Method Status is correct
      frameLength = len(responseFrame)
      if sedVar.enableDebugstatMsg == 1:
         statMsg("Analyzing frame: %s" % (binascii.hexlify(responseFrame),))
      for i in range(0, frameLength):
         if binascii.hexlify(responseFrame[frameLength-i-1:frameLength-i]) == 'f1':
            methodStatus = binascii.hexlify(responseFrame[frameLength-i-4:frameLength-i-3])
            if sedVar.enableDebugstatMsg == 1:
               statMsg("Extracting methodStatus from frameLength: %d" % (frameLength,))
            if methodStatus != '00':
               if sedVar.enableDebugstatMsg == 0:
                  if abortBadStatus == 0 and (m_type == 'Authenticating Default PSID' or m_type == 'Authenticating FIS PSID'): #Use this return case so that we know if PSID is failing to authenicate
                     return 11223344 #'BadPSID'
                  else:
                     statMsgPastCmdOnFail()
               statMsg('Bad Value Selected is %s' % methodStatus)
               badData = 'BAD METHOD STATUS RECIEVED FROM DRIVE: ' + dictMethodFailCodes[methodStatus]
               if abortBadStatus == 1:  #Could be used to reroute process or reauthenicate
                  abort(failVal = 10124, failStr = badData)
               else:
                  return badData
            else:
               break
      if checkRcvStat == 1:  #can be used for authenticate bands, SIDS and final MakerSymK, and change states
         if responseFrame[63:64] == '\x00': #Should return \x01 for passing status
            if abortBadStatus == 0 and (m_type == 'Authenticating Default PSID' or m_type == 'Authenticating FIS PSID'): #Use this return case so that we know if PSID is failing to authenicate
               return 11223344 #'BadPSID'
            if showFrame == 0:     ##statMsg this if error occured and didn't statMsg frame to begin with so we can see the return
               statMsg("Retrieved Bad %s Packet" % m_type)
               displayFrame(responseFrame[6:])
            if sedVar.enableDebugstatMsg == 0:
               statMsgPastCmdOnFail()
            if abortBadStatus == 1:  #Could be used to reroute process to try different SID value
               #if testSwitch.virtualRun:
               #    return responseFrame[63:64]
               #else:
               abort(failStr = 'Last receive frame returned a non-passing status')
            else:
               return responseFrame[63:64]
   if ditsCommand == 1 and rtnRawPacket == 0:
      senseData = binascii.b2a_hex(responseFrame[1:2]) + '/' + binascii.b2a_hex(responseFrame[2:3]) + '/' + binascii.b2a_hex(responseFrame[3:4]) + '/' + binascii.b2a_hex(responseFrame[11:12])
      if senseData != '00/00/00/00':
         if showFrame == 0:
            statMsg("Retrieved This Bad %s Packet" % m_type)
            displayFrame(responseFrame[0:])
         if senseData == '05/2c/00/03':
            badSenseStr = 'Need to Unlock Dits Commands.  BAD SENSE DATA IS:' + senseData
            tMsg('%s')
            abort(failVal = 10124, failStr = badSenseStr)
         else:
            badSenseStr = 'BAD SENSE DATA: ' + senseData

         if sedVar.enableDebugstatMsg == 0:
            statMsgPastCmdOnFail()

         if ditsAbortBadStatus == 1: #Used to handle error in seperate DITs command function
            abort(failVal = 10124, failStr = badSenseStr)
         else:
            return senseData
      else:
         if len(responseFrame) > 24:  #Required for SCSA packet of data to be returned
            return responseFrame
         else:
            return senseData
   if sedVar.enableDebugstatMsg == 0:   #Used if not in statMsging debugging statement to know drive passed.
      statMsg("Retrieved GOOD %s Packet" % m_type)
   return responseFrame[0:]


##############################################################################################
##########  Used to save variable in case there is an error and no debug statMsging   ##########
##############################################################################################
def updateDebugPackets(data,packType='Not Specified',sentPack=0,recevPack=0):

    if sentPack == 1:
        if sedVar.packetSaveSent1 == '':
            sedVar.packetSaveSent1 = data
            sedVar.frame1Type = packType
        else:
            sedVar.packetSaveSent2 = sedVar.packetSaveSent1
            sedVar.packetSaveSent1 = data
            sedVar.frame2Type = sedVar.frame1Type
            sedVar.frame1Type = packType
    else:
        if sedVar.packetSaveRecev1 == '':
            sedVar.packetSaveRecev1 = data
        else:
            sedVar.packetSaveRecev2 = sedVar.packetSaveRecev1
            sedVar.packetSaveRecev1 = data

########################################################################################
##########  Used to statMsg upto last 2 commands if fails and not debug statMsg.  ##########
########################################################################################
def statMsgPastCmdOnFail():
    if sedVar.packetSaveRecev2 != '':
        statMsg('Previous Sent Command Packet %s ' %sedVar.frame2Type,masterstatMsg=1)
        statMsgSedBin(binData = sedVar.packetSaveSent2,display=1)
        statMsg('Previous Received Command Packet %s ' %sedVar.frame2Type,masterstatMsg=1)
        statMsgSedBin(binData = sedVar.packetSaveRecev2,display=1)

    statMsg('SENT PACKET THAT CAUSED FAILURE %s' %sedVar.frame1Type,masterstatMsg=1)
    statMsgSedBin(binData = sedVar.packetSaveSent1,display=1)
    statMsg('RECEIVED PACKET FROM BAD SEND PACKET %s ' %sedVar.frame1Type,masterstatMsg=1)
    statMsgSedBin(binData = sedVar.packetSaveRecev1 ,display=1)

#######################################################################
##########  Used to get the length values need for the frame ##########
#######################################################################

def getFrameLengths(frame = ''):
    lengthTypes = {}
    framePad = '\x00'
    framePadNum = 0
    sedVar.preFrameLength = len(frame) + 36
    if sedVar.preFrameLength > 0:
        modTemp = (sedVar.preFrameLength) % 4
        if modTemp != 0:
            sedVar.preFrameLength = (sedVar.preFrameLength / 4)  #Rounds number down to whole number first
            sedVar.preFrameLength = ((sedVar.preFrameLength*4) + 4)
            framePadNum = 4 - modTemp
            for y in range(1,framePadNum):
                framePad = framePad + '\x00'

        #Finding length of string and prepending zeros so it's 4 bytes long.  tempLen = sedVar.preFrameLength
        lengthTypes['comPacketLength'] = str(hex(sedVar.preFrameLength)[2:]).zfill(8)
        lengthTypes['packetLength'] = str(hex(sedVar.preFrameLength - 24)[2:]).zfill(8)
        lengthTypes['subPacketLength'] = str(hex(sedVar.preFrameLength - 36 - framePadNum)[2:]).zfill(8)

        for x in lengthTypes:
            strCalc = lengthTypes[x]
            binStrLen = binascii.unhexlify(strCalc)
            lengthTypes[x] = binStrLen
        return lengthTypes, framePad

    else:
        abort(failVal = 11168, failStr = 'Frame length is not long enough.  Missing frame while constructing packet')

#######################################################################################
##########  Used to ensure correct format when converting numbers to strings ##########
#######################################################################################
def convertNumToStr(value,requiredBytes):
    if requiredBytes == 1:
        if value < 16:
            valueStr = '0' + str(hex(value)[2:])
        else:
            valueStr = str(hex(value)[2:])

    return binascii.unhexlify(valueStr)

###########################################################################
##########  Used to prepend correct Atom Type before information ##########
###########################################################################
def prependAtom(preDictionary = {},cont = 0, preString = ''):
    newRSADict = {}
    if preString == '':
        for x in preDictionary:
            dataLength = len(preDictionary[x])
            if dataLength <= 15:  #Short Atom
                if dataLength <= 2:
                    tempData, = struct.unpack('B',preDictionary[x])
                    if tempData <= 63:
                        return preDictionary[x]
                if cont == 0:
                    addAtom = (0x80 | (dataLength & 0x0F))
                else:
                    addAtom = (0xA0 | (dataLength & 0x0F))
            elif dataLength <= 2047: # Medium Atom
                if cont == 0:
                    addAtom = ((0xC0 | ((dataLength >> 8) & 0x0F)) << 8)
                else:
                    addAtom = ((0xD0 | ((dataLength >> 8) & 0x0F)) << 8)
                addAtom = addAtom + (dataLength & 0xFF)
            else: #Long Atom
                addAtom = 0xE2 << 24
                addAtom = addAtom + (dataLength & 0xFFFFFF)
            convertAtom = binascii.unhexlify(str(hex(addAtom)[2:]))
            newRSADict[x] = convertAtom + preDictionary[x]
        return newRSADict
    else:
        dataLength = len(preString)
        if dataLength <= 15:
            if dataLength <= 1:
                tempData, = struct.unpack('B',preString)
                if tempData <= 63:
                    return preString
            if cont == 0:
                addAtom = (0x80 | (dataLength & 0x0F))
            else:
                addAtom = (0xA0 | (dataLength & 0x0F))
        elif dataLength <= 2047: # Medium Atom
            if cont == 0:
                addAtom = ((0xC0 | ((dataLength >> 8) & 0x0F)) << 8)
            else:
                addAtom = ((0xD0 | ((dataLength >> 8) & 0x0F)) << 8)
            addAtom = addAtom + (dataLength & 0xFF)
        else: #Long Atom
            addAtom = (0xE2) << 24
            addAtom = addAtom + (dataLength & 0xFFFFFF)
        convertAtom = binascii.unhexlify(str(hex(addAtom)[2:]))
        dataString = str(convertAtom + preString)
        return dataString

#####################################################
##########   Used to download .LOD files   ##########
#####################################################
def downloadLOD(fileName,fileLocation=CN):
    st(8,0,0,0x0003,0x0000,0x0700,0,0,0,0,0,dlfile=(fileLocation,fileName),timeout=400)

###############################################################################
##########   Used to download the IV file and enter into Diag Mode   ##########
###############################################################################
def downloadIV(timeout=600):   #Similar to Test 578
    
     CTRL_Z  = '\x1A'
     PChar(CTRL_Z);
     ScriptPause(1);
     ScriptPause(5);
     PChar(CTRL_Z); readme();
     PBlock('C34F329A\r'); readme();
     data = ''
     retry = 10000
     while ('T>' not in data) and (retry > 0):
        PChar('\n')
        data += GChar()
        retry -=1

     PChar(CTRL_L); readme();

     if IVFile.lower().find('.lod') > -1:
        res = 'PASSED'
        try:
           PChar(CTRL_T); readme();
           ScriptPause(1);
           downloadLOD(IVFile)
        except:
           res = 'FAILED'
     else:
        PBlock('k\r');
        readme()

        res = downloadTRD(stream = open(os.path.join(IFFileLocation , IVFile) ,'rb'), fileName = IVFile, retry=200, timeout=timeout, reportErr=1)
     return res

#####################################################
##########   Used to download .LOD files   ##########
#####################################################
def fullInitCodeDwnld(codeList):
    global IVDownloadRetried

    #SetESlipBaud(1228000)
    objPwrCtrl.powerCycle( useESlip=1 ) #set5V=5000, set12V=12000, offTime=10, onTime=10,  ###pwrCylSpinUp()
    PBlock(CTRL_Z)
    PBlock(CTRL_L)
    statMsg(GChar())
    PBlock(CTRL_T)
    ScriptPause(2)
    SetESlipBaud(1228000)


    if 'UNLK' in codeList and IVDownloadRetried == 0:
       # assume 2 'UNLK's in download seq, one at index 0 & one after 'IV4'/'OVL4'
       downloadLOD(fileName = unlockFile)


    if IVDownloadRetried == 0:
       downloadLOD(fileName = BridgeCode)

    if IVDownloadRetried > 2:
       SetESlipBaud(38400)
    elif IVDownloadRetried > 1:
       SetESlipBaud(115200)
    else:
       SetESlipBaud(460800)
    result = downloadIV()
    if result == 'FAILED':
       IVDownloadRetried += 1
       if IVDownloadRetried > 3:
          abort(failVal = 14623, failStr = 'IV download failed after retries')
       statMsg('Retry IV download')
       fullInitCodeDwnld(codeList)   # Retry download IV

    asciiToEslipMode() #Switch back to Eslip mode
    SetESlipBaud(1228000)


    if codeList.count('UNLK') > 1:
       # assume 2 'UNLK's in download seq, one at index 0 & one after 'IV4'/'OVL4'
       downloadLOD(fileName = unlockFile)

    downloadLOD(fileName = SignedSEDTarget)

#####################################################
##########   Used to discover SED drive    ##########
#####################################################
def SEDdiscovery():
    discoveryData = getPacket(m_type = 'Discovery',retrieveFrame = SED_discovery)

    sedVar.autoDetectRan = 0
    if testSwitch.FE_0267840_440337_P_SERIAL_PORT_AUTO_DETECT:
        statMsg(msg = 'SP Auto Detect =1')
        parseDiscoveryInfo(dataPacket = discoveryData[6:])

#####################################################
##########   Verify SED type of Drive      ##########  --ONLY VALID FOR OPAL DRIVES
#####################################################
def SSCDriveVerify(binResponse = False):
##    if sedVar.driveType == OPAL:
##        sendCmd(CTRL_Z)
##        gotoLevel('t')
##        prodInfo = sendCmd(CTRL_L)
##        fileFound = prodInfo.find('TCG IV Version:')
##        if fileFound >=0:
##            return 1
##        else:
##            abort(failVal=10124,failStr='THIS IS NOT A SED DRIVE')
##    elif sedVar.driveType == ENTERPRISE:
    #ditsLockUnlock(lockPort = 1)
    ditsLockUnlock(lockPort = 0)
    setFDEPacket = '\x2F\x01\x01\x00\x00\x00\x00\x00'
    sessionType = 'Verify SED/non-SED Drive'
    sendPacket(frame = setFDEPacket, m_type = sessionType, ditsCommand = 1)
    ditsResponse = getPacket(m_type = sessionType, ditsCommand = 1, ditsAbortBadStatus = 0)

    if ditsResponse == '00/00/00/00':
        if not binResponse:
           return 'SSC Drive'
        else:
           return True
    elif ditsResponse in ('05/26/02/13','05/26/02/14'):  #Sense data for not support cmd
        if not binResponse:
           return 'non-SSC Drive'
        else:
           return False
    elif ditsResponse == '07/20/02/00':
        if not binResponse:
           return 'SSC Drive needs to be put into Setup State'
        else:
           return True
    else:
        if binResponse:
           return False
        else:
           response = 'Failed with unknown Error Type %s' %ditsResponse
           abort(failStr=response)

####################################################################################
##########   Gets PSID value from FIS if it hasn't already retrieved it   ##########
####################################################################################
def retrPsid(display = 1,forceUpdate = 0):   #Similar to Test 575, Mode:0x24
    if forceUpdate ==1:
        sidStatus,sedVar.global_fisPSID = getSID(updateAttrs = 1)
        if display == 1:
            statMsg('forceUpdate=1')

    if(sedVar.global_fisPSID in [None, '', 'NONE']):
        sidStatus,sedVar.global_fisPSID = getSID(updateAttrs = 1)
        if display == 1:
            statMsg('sedVar.global_fisPSID is None/ /NONE')

##############################################################################################
##########    Gets MSID value from Drive or FIS if it hasn't already retrieved it   ##########
##############################################################################################
def retrMsid(fromFIS = 0, display = 1):  #Similar to Test 575, Mode:0x10, 0x11
    if fromFIS ==1:
        if(sedVar.global_fisMSID == ''):
            sidStatus, sedVar.global_fisMSID = getMSIDfromAttributeMSID(updateAttrs = 1)
            if display == 1:
                statMsg('MSID retrieved from MSID attribute = %s' % sedVar.global_fisMSID)
            DriveAttributes['MSID'] = sedVar.global_fisMSID
        return sedVar.global_fisMSID
    else:
        if sedVar.global_driveMSID in ['', MSID_defaultPin]:
            sessionType = 'Get MSID from the Drive' #Need to be authenicate start session
            packet = createPacket(type = 'getDrvMsid', UID = UID_retrDrvMSID, mthdUID = sedVar.UIDmethod_getTable)
            sendPacket(frame = packet, m_type = sessionType, showFrame = 0)
            tempPacket = getPacket(m_type = sessionType, showFrame = 0,checkRcvStat = 1)
            if sedVar.driveType == ENTERPRISE:
                sedVar.global_driveMSID = tempPacket[72:104]
            else:
                sedVar.global_driveMSID = tempPacket[68:100]
            if display == 1:
                statMsg('Drive MSID Value is: %s' %sedVar.global_driveMSID)
            dut.driveattr['MSID'] = sedVar.global_driveMSID
            DriveAttributes['MSID'] = sedVar.global_driveMSID
            sedVar.global_fisMSID = sedVar.global_driveMSID
        return sedVar.global_driveMSID

###########################################
##########  Dits Unlock command  ##########
###########################################
def ditsLockUnlock(lockPort = 1):
    if lockPort == 1:
        packet = "\xFF\xFF\x01\x00\x9a\x32\x4f\x83"
        sessionType = 'Lock the Dits Port'
    else:
        packet = "\xFF\xFF\x01\x00\x9a\x32\x4f\x03"
        sessionType = 'Unlock the Dits Port'
    sendPacket(frame = packet, m_type = sessionType, ditsCommand = 1)
    getPacket(m_type = sessionType, ditsCommand = 1,checkRcvStat = 1)

###########################################
##########  Enable FIPS  mode #############
###########################################
def EnableFIPS(PartNum):

    #9401 0100 
    packet = "\x94\x01\x01\x00" + PartNum
    #packet = "\x94\x01" + PartNum
    statMsg('EnableFIPS: %s' %packet)

    sessionType = 'Enable FIPS Cmnd'
    sendPacket(frame = packet, m_type = sessionType, ditsCommand = 1)
    ScriptPause(5);
    getPacket(m_type = sessionType, ditsCommand = 1,checkRcvStat = 1)

#######################################
##########  Nuke IV command  ##########
#######################################
def ditsNukeCmd():  #Similar to Test 575, Mode:0x27
   # ditsLockUnlock(lockPort = 1)
    ditsLockUnlock(lockPort = 0)   #Unlock DITS before nuke
    sessionType = 'Nuke Firmware'
    nukePacket = '\x79\x01\x00\x00\x00\x00\x00\x00'
    sendPacket(frame = nukePacket, m_type = sessionType, ditsCommand = 1)
    getPacket(m_type = sessionType, ditsCommand = 1,checkRcvStat = 1)

###########################################
##########  Dits SCSA command  ##########
###########################################
def ditsSCSACmd(encrypted = 0):
    if encrypted not in [0,1]:
        abort(failVal = 10264,failStr='Invalid encryption value for ditsSCSACmd() subFunction 2')
    numZeros = 256
    assetPacket = ''
    #Step One of SCSA packet transfer including SCSA Subcommand 0
    cmdPacket = '\x3E\x01\x01\x00\x00\x00\x00'
    #Append 256 bytes of zero
    for i in range(0,numZeros):
        assetPacket += '\x00'
    assetCheckSum = calc_checksum_scsa(data = assetPacket, packetNum = 0)

    assetCheckSumStr = convertNumToStr(value = assetCheckSum,requiredBytes=1)

    packet = cmdPacket + assetCheckSumStr + '\x00\x00'  + struct.pack('<H', numZeros) + assetPacket
    sessionType = 'SCSA SubCmd Type Zero'
    sendPacket(frame = packet, m_type = sessionType, ditsCommand = 1)
    data = getPacket(m_type = sessionType, ditsCommand = 1,checkRcvStat = 1)

    #Send retrieved data to the server
    serverResp = CustomRequestGetSCSA_FactoryAsset(data[16:])

    #Send data to drive usinig SCSA Subcommand 1
    maxFrameSize = 492
    totalLength = len(serverResp)
    j=0
    cmdPacket = '\x3E\x01\x01\x00\x02\x00'
    
    for i in xrange(0, totalLength-1, maxFrameSize):
        print i
        partialPacket = serverResp[i:i+maxFrameSize]
        partialLen = len(partialPacket)

        lenFinalEncypt = (j & 0x3F) | (encrypted << 7)  #bit layout of byte 6... [5:0]-packetNum, [6]-last subPacket bit, [7]-encryption
        if (i+maxFrameSize) >= totalLength:
            lenFinalEncypt |= 0x40   #bit index 6 set for final packet

        lenFinalEncyptStr = convertNumToStr(value = lenFinalEncypt,requiredBytes=1)

        checkSum = calc_checksum_scsa(data = partialPacket ,packetNum=j)
        checkSumStr = convertNumToStr(value = checkSum,requiredBytes=1)

        packet = cmdPacket + lenFinalEncyptStr + checkSumStr + struct.pack('<H',partialLen) + struct.pack('<H',totalLength) + partialPacket
        sessionType = 'SCSA SubCmd Type Two with sending index %d' %(j)
        sendPacket(frame = packet, m_type = sessionType, ditsCommand = 1)
        data = getPacket(m_type = sessionType, ditsCommand = 1,checkRcvStat = 1)

        j+=1



##########  Dits Nuke command  ############
###########################################D
def nukeIV():
   # changeToSetupState()

    if sedVar.enableCM == 0:
        statMsg("Download " + BridgeCode)
        st(8,0,0,0x0003,0x0000,0x0700,0,0,0,0,0,dlfile=(CN,BridgeCode),timeout=400)

    ditsNukeCmd()

    if sedVar.enableCM == 0:   #Using CM needs to powercycle and use different download
        pwrCylSpinUp(issueSpin=0)   #Drive on and set Baud Rate
        statMsg("Download " + NonSEDTarget)
        st(8,0,0,0x0003,0x0000,0x0700,0,0,0,0,0,dlfile=(CN,NonSEDTarget),timeout=400) ## download the SED firmware.


##########################################################################################
##########   Used to Authenitcate both Standard and Locking SP Start Sessions   ##########
##########################################################################################
def authenStartSess(lockingSP = 0): #Similar to Test 575, Mode:0x02
    if lockingSP == 0:
        sessionType = 'Authenticate Start Session'
        packet = createPacket(type = 'authSess', srtSessType = startSndSession, UID = UID_adminSP)
    else:
        sessionType = 'Authenticate Locking SP Start Session'
        packet = createPacket(type = 'authSess', srtSessType = startLckSPSession, UID = UID_lockingSP)
    sendPacket(frame = packet, m_type = sessionType)
    sessNumPacket = getPacket(m_type = sessionType)
    sedVar.sessionNumber = sessNumPacket[91:92]

################################################
##########   Closes an open session   ##########
################################################
def closeSession():  #Similar to Test 575, Mode:0x03
    sessionType = 'Closing Session'
    packet = createPacket(type = 'closeSession')
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType)

####################################################
##########   Used to authenicate a PSID   ##########
####################################################
def authenPSID(fromDefValue = 1,handleFail = 0):  #Similar to Test 575, Mode:0x01
    if fromDefValue == 1:
        sessionType = 'Authenticating Default PSID'
        psidPin = prependAtom(preString = PSID_defaultPin, cont = 1)
    else:
        sessionType = 'Authenticating FIS PSID'
        retrPsid()
        psidPin = prependAtom(preString = sedVar.global_fisPSID, cont = 1)
    packet = createPacket(type = 'authSymK2_Ers_Bnd_SIDS',UID = UID_authPSID, credential = psidPin, mthdUID = sedVar.UIDmethod_authenTable)
    sendPacket(frame = packet, m_type = sessionType, showFrame = 0)
    if handleFail == 0:
        getPacket(m_type = sessionType,checkRcvStat = 1,abortBadStatus = 1)
    else:
        failCode = getPacket(m_type = sessionType,checkRcvStat = 1,abortBadStatus = 0)

        if failCode == 11223344:   #BadPSID
            personalizePSID(toDefValue = 0, requireUpdate=1)
            sidStatus,sedVar.global_fisPSID = getSID(updateAttrs = 1)
            sessionType = 'Authenticating New FIS PSID'
            psidPin = prependAtom(preString = sedVar.global_fisPSID, cont = 1)
            packet = createPacket(type = 'authSymK2_Ers_Bnd_SIDS',UID = UID_authPSID, credential = psidPin, mthdUID = sedVar.UIDmethod_authenTable)
            sendPacket(frame = packet, m_type = sessionType, showFrame = 0)
            getPacket(m_type = sessionType,checkRcvStat = 1,abortBadStatus = 1)

####################################################
##########   Used to authenicate a MSID   ##########
####################################################
def authenMSID(fromDefValue = 1):   #Similar to Test 575, Mode:0x01
    if sedVar.driveType == ENTERPRISE:
        if fromDefValue == 1:
            sessionType = 'Authenticating Default MSID'
            msidPin = prependAtom(preString = MSID_defaultPin, cont = 1)
        else:
            sessionType = 'Authenticating FIS MSID'
            msid = retrMsid(fromFIS = 0)
            msidPin = prependAtom(preString = msid, cont = 1)
        packet = createPacket(type = 'authSymK2_Ers_Bnd_SIDS',UID = UID_authMSID, credential = msidPin, mthdUID = sedVar.UIDmethod_authenTable)
        sendPacket(frame = packet,m_type = sessionType)
        getPacket(m_type = sessionType,checkRcvStat = 1)

###################################################
##########   Used to authenicate a SID   ##########
###################################################
def authenSID(fromDefValue = 1):    #Similar to Test 575, Mode:0x01
    if fromDefValue == 1:
        sessionType = 'Authenticating Default SID'
        sidPin = prependAtom(preString = MSID_defaultPin, cont = 1)
    else:
        sessionType = 'Authenticating FIS SID'
        sid = retrMsid(fromFIS = 0)
        sidPin = prependAtom(preString = sid, cont = 1)
    packet = createPacket(type = 'authSymK2_Ers_Bnd_SIDS',UID = UID_authSID, credential = sidPin, mthdUID = sedVar.UIDmethod_authenTable)
    sendPacket(frame = packet,m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

#########################################################
##########   Used to authenicate to MakerSymK  ##########
#########################################################
def authenSymK(firstRunDef = 0, makerSymK = 0, maintSymK = 0,symKType = 2, activateSymK = 0):  #Similar to Test 575, Mode:0x01
    if makerSymK == 1:
        tempUID = UID_authMkrSymK
        sessionType = 'Authenticating MakerSymK Step One'
    elif maintSymK == 1:
        enabledMaintSymK = enableMainSymK()  # Need to Enable before authenticating
        if enabledMaintSymK == 1:
            tempUID = UID_authMaintSymk
            sessionType = 'Authenticating MaintSymK Step One'
    elif activateSymK and sedVar.activateSupport:
        tempUID = UID_authActivateSymK
        sessionType = 'Authenticating ActivationSymK Step One'

    if (maintSymK == 1 and enabledMaintSymK == 1) or makerSymK == 1 or activateSymK == 1:
        packet = createPacket(type = 'authSymKAmp1', UID = tempUID, mthdUID = sedVar.UIDmethod_authenTable)
        sendPacket(frame = packet, m_type = sessionType)
        responseFrame = getPacket(m_type = sessionType)

        responseFrame = responseFrame[65:97]
        statMsg("Hex Challange Value")
        displayFrame(responseFrame)
        statMsg("Challange Value = %s" %responseFrame)
        if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
           randomChallengeValue = responseFrame
        else:
           randomChallengeValue = base64.b64encode(responseFrame)
        statMsg("Confirm Send Challange Value %s" %randomChallengeValue)
        if makerSymK == 1:
            keyType = 'DiagKey'
        elif maintSymK == 1:
            keyType = 'MaintKey'
        elif activateSymK ==1:
            keyType =  'ActKey'

        if (firstRunDef  == 1):
            if symKType == 2:
                if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
                   method, prms = makeTDCICall( 'doDefaultKeyAuthentication', ('nonce',randomChallengeValue), HDASerialNumber, keyType, 'AES256', '0')
                else:
                   method,prms = RequestService('DoDefaultKeyAuthentication',(randomChallengeValue, HDASerialNumber,keyType,'AES256','0'))
            elif symKType == 1:
               if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
                  method, prms = makeTDCICall( 'doDefaultKeyAuthentication', ('nonce',randomChallengeValue), HDASerialNumber, 'DiagKey', '3DES', '0')
               else:
                  method,prms = RequestService('DoDefaultKeyAuthentication',(randomChallengeValue, HDASerialNumber,'DiagKey','3DES','0'))
        else:
            if symKType == 2:
               if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
                  method, prms = makeTDCICall( 'doUniqueKeyAuthentication', ('nonce',randomChallengeValue), HDASerialNumber, keyType, 'AES256', '0')
               else:
                  method,prms = RequestService('DoUniqueKeyAuthentication',(randomChallengeValue, HDASerialNumber,keyType,'AES256','0'))
            elif symKType == 1:
               if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
                  method, prms = makeTDCICall( 'doUniqueKeyAuthentication', ('nonce',randomChallengeValue), HDASerialNumber, 'DiagKey', '3DES', '0')
               else:
                  method,prms = RequestService('DoUniqueKeyAuthentication',(randomChallengeValue, HDASerialNumber,'DiagKey','3DES','0'))

        statMsg("method: %s; prms: %s"%(method,prms,))
        responseString = base64.b64decode(prms['AuthenticationResponse'])
        mfgAuthKeyString = binascii.b2a_hex(responseString)
        statMsg("HDA Serial Number = %s" % HDASerialNumber)
        statMsg("Mfg.Auth.Key = %s" %mfgAuthKeyString)

        sessionType = 'Authenticating SymK Step Two'
        makerString = prependAtom(preString = responseString,cont=1)
        packet = createPacket(type = 'authSymK2_Ers_Bnd_SIDS', UID = tempUID, credential = makerString, mthdUID = sedVar.UIDmethod_authenTable)
        sendPacket(frame = packet, m_type = sessionType)
        responseFrame = getPacket(m_type = sessionType,checkRcvStat = 1)

##############################################################
##########   Used to authnicate to all SID Values   ##########
##############################################################
def authenSIDSMaker(default = 1, firstRun = 1,handleFail=0):   #Similar to Test 575, Mode:0x01
    authenSymK(firstRunDef = firstRun, makerSymK = 1, maintSymK = 0, symKType = sedVar.masterSymKType) #firstRunDef should = 1 only on the very first personalization of the drive
    authenPSID(default, handleFail)
    if sedVar.driveType == ENTERPRISE:
        authenMSID(fromDefValue = default)
    authenSID(fromDefValue = default)

#################################################################
##########   Used to authenicate to the Erase Master   ##########
#################################################################
def authenEraseMaster(fromDefValue = 1):    #Similar to part Test 575
    if fromDefValue == 1:
        msidString = prependAtom(preString = MSID_defaultPin,cont=1)
    else:
        retrMsid(fromFIS = 0)  #If value already has been read from drive it will not read it
        msidString = prependAtom(preString = sedVar.global_fisMSID,cont=1)
    packet = createPacket(type = 'authSymK2_Ers_Bnd_SIDS', UID = UID_authEraseMstr, credential = msidString, mthdUID = sedVar.UIDmethod_authenTable)
    sessionType = 'Authenticating Erase Master'
    sendPacket(frame = packet,m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

#########################################################
##########   Used to authenicate a each band   ##########
#########################################################
def authenBand(band, bandUID, fromDefValue = 1):    #Similar to part Test 577
    if fromDefValue == 1:
        msidString = prependAtom(preString = MSID_defaultPin,cont=1)
    else:
        retrMsid(fromFIS = 0)  #If value already has been read from drive it will not read it
        msidString = prependAtom(preString = sedVar.global_fisMSID,cont=1)
    packet = createPacket(type = 'authSymK2_Ers_Bnd_SIDS', UID = bandUID, credential = msidString, mthdUID = sedVar.UIDmethod_authenTable)
    sessionType = 'Authenticate to Band %d' %(band)
    sendPacket(frame = packet,m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

####################################################################
##########   Used to verify which state the Drive is in   ##########
####################################################################
def getStateTable(dispFrames = 0, displayState = 1):    #Similar to Test 575, Mode:0x09
    sessionType = 'Get State Table'
    packet = createPacket(type = 'getTbl', UID=UID_securityStateCtrl)
    sendPacket(frame = packet, m_type = sessionType, showFrame = dispFrames)
    table = getPacket(m_type = sessionType, showFrame = dispFrames)
    if displayState == 1:
        statMsg("Drive is in %s State" %dictSEDStates[binascii.hexlify(table[64:65])])
    return table[64:65]

###########################################
##########   Generic Get Table   ##########
###########################################
def getTable(dispFrames = 1, UID = '', lookUpUID=1):
    if lookUpUID == 1:
        getTableType = dictUIDs.keys()[dictUIDs.values().index(UID)]
    else:
        getTableType = UID
    sessionType = 'Get' + getTableType + 'Table'
    packet = createPacket(type = 'getTbl', UID = UID)
    sendPacket(frame = packet, m_type = sessionType, showFrame = dispFrames)
    table = getPacket(m_type = sessionType, showFrame = dispFrames)
    return table

############################################
##########   Check Locking Port   ##########
############################################
def checkPortLocking(UIDname,configEnableLORPort = True, configEnablePortLocking = True):
    packet = getTable(dispFrames = 1, UID = UIDname)
    LORPort,LockingPort = parsePortLockingData(data = packet)
    statMsg("checkPortLocking: LORPort:%s LockingPort:%s" % (LORPort,LockingPort))

    sessionType = dictUIDs.keys()[dictUIDs.values().index(UIDname)]

    if configEnableLORPort:
        configLORPort = '\x00'
    else:
        configLORPort = '\xf1'

    if configEnablePortLocking:
        configPortLocking = '\x01'
    else:
        configPortLocking = '\x00'

    if LORPort != configLORPort:
        failMsg = "LOR PORT for %s not configured correctly. Specified configuration was for configEnableLORPort to be %s" %(sessionType,configEnableLORPort)
        abort(failVal = 12972, failStr = failMsg)

    if LockingPort != configPortLocking:
        failMsg = "PORT LOCKING for %s not configured correctly. Specified configuration was for configEnablePortLocking to be %s" %(sessionType,configEnablePortLocking)
        abort(failVal = 12973, failStr = failMsg)

#############################################################
##########   Used to change drive to a new state   ##########
#############################################################
def changeStates(newState):     #Similar to Test 575, Mode:0x08
    time.sleep(1)
    sessionType = ''
    currentState = getStateTable()
    if(newState == 00):
        sessionType = 'Change to Setup State'
        newState = '\x00'
        if(currentState == '\xFF' or currentState == '\x80'):
            failMsg = "Can't change from current state to Setup State"
            abort(failVal = 14620, failStr = failMsg)
    if(newState == 01):
        sessionType = 'Change to Diag State'
        newState = '\x01'
        if(currentState == '\x00' or currentState == '\x81'):
            failMsg = "Can't change from current state to Diag State"
            abort(failVal = 14620, failStr = failMsg)
    if(newState == 80):
        sessionType = 'Change to Use State'
        newState = '\x80'
        if(currentState == '\x00' or currentState == '\xFF' or currentState == '\x01'):
            failMsg = "Can only change to Use State from Manufacture State"
            abort(failVal = 14620, failStr = failMsg)
    if(newState == 81):
        sessionType = 'Change to Manufacture State'
        newState = '\x81'
        if(currentState == '\x80' or currentState == '\xFF' or currentState == '\x01'):
            failMsg = "Can only change to Manufacture State from Setup State"
            abort(failVal = 14620, failStr = failMsg)
    if(newState == 99):
        sessionType = 'Change to Fail State'
        newState = '\xFF'
        if(currentState == '\x00'):
            failMsg = "Can't change to Fail State from Setup State"
            abort(failVal = 14620, failStr = failMsg)
    if currentState == newState:
        currentState = displayFrame(currentState)
        statMsg("Set State ( %s )is the Same as Current State" %dictSEDStates[newState])
        return
    packet = createPacket(type = 'setStateTbl_SOM0', state = newState, mthdUID = sedVar.UIDmethod_setTable, UID = UID_securityStateCtrl)
    sendPacket(frame = packet, m_type = sessionType)
    time.sleep(6)     #Need to pause for a moment if changing states or drive will timeout
    getPacket(m_type = sessionType,checkRcvStat = 1)


#############################################################
##########   Used to get random number   ##########
#############################################################
def getRandomNumber():     #Similar to Test 575, Mode:0x28, but each time one random number only

   sessionType = 'Get Random Number'
   packet = createPacket(type = 'getRandomNumber', UID = UID_spUID, mthdUID =UID_getRandomNumber)
   sendPacket(frame = packet, m_type = sessionType)
   #time.sleep(1)
   returndata= getPacket(m_type = sessionType, checkRcvStat = 1)
   
   #To check TLV Tag=D0 , Len=20, 
   if (not returndata[63:64] == '\xD0') or (not returndata[64:65] == '\x20'): 
      abort(failStr='TLV failed, checked !!!')

   RandomNumber = returndata[65:97]
   return RandomNumber

##################################################################################
##########  Change state to Setup no matter what state the dirve is in  ##########
##################################################################################
def changeToSetupState():    #Similar to Test 577
    authenStartSess()
    currState = getStateTable()
    if currState != '\x00':
        defaultMSID = 0
    if currState != '\x00':
        authenSIDSMaker(default = defaultMSID, firstRun = defaultMSID, handleFail=1)
        if currState == '\x81':  #need to cycle through states drive can only get to Manufature State from Setup State
            changeStates(00)
            currState = getStateTable()
        if currState == '\x80' or currState == '\xFF':  # if wasn't in Diag state it is now and needs to go to Setup State
            changeStates(01)
            currState = getStateTable()
            changeStates(00)              
            currState = getStateTable()
        if currState == '\x01':
            changeStates(00)
            currState = getStateTable()
    closeSession()

#####################################################################
##########   Used to personalize a PSID with a new value   ##########
#####################################################################
def personalizePSID(toDefValue = 0, requireUpdate=0):    #Similar to Test 575, Mode:0x04
    if toDefValue == 1:
        psidPin = prependAtom(preString = PSID_defaultPin, cont = 1)

    else:
        retrPsid(forceUpdate=requireUpdate)
        psidPin = prependAtom(preString = sedVar.global_fisPSID, cont = 1)
    packet = createPacket(type='psnlzeSIDS_Bands_SymK2',UID=UID_prsnlzePSID,credential=psidPin,mthdUID=sedVar.UIDmethod_setTable, dataType = sedVar.TYPE_pin)
    sessionType = 'Personalize PSID'
    sendPacket(frame = packet, m_type = sessionType, showFrame = 0)
    getPacket(m_type = sessionType,checkRcvStat = 1)

#######################################################################
##########   Used to personalize the MSID with a new value   ##########
#######################################################################
def personalizeMSID(toDefValue = 0):    #Similar to Test 575, Mode:0x04
    if toDefValue == 1:
        msidPin = prependAtom(preString = MSID_defaultPin, cont = 1)
    else:
        retrMsid(fromFIS = 1)
        msidPin = prependAtom(preString = sedVar.global_fisMSID, cont = 1)
    packet = createPacket(type = 'psnlzeSIDS_Bands_SymK2', UID = UID_prsnlzeMSID, credential = msidPin, mthdUID = sedVar.UIDmethod_setTable, dataType = sedVar.TYPE_pin)
    sessionType = 'Personalize MSID'
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

######################################################################
##########   Used to personalize the SID with a new value   ##########
######################################################################
def personalizeSID(toDefValue = 0):     #Similar to Test 575, Mode:0x04
    if toDefValue == 1:
        msidPin = prependAtom(preString = MSID_defaultPin, cont = 1)
    else:
        retrMsid(fromFIS = 0)
        msidPin = prependAtom(preString = sedVar.global_fisMSID, cont = 1)
    packet = createPacket(type = 'psnlzeSIDS_Bands_SymK2', UID = UID_prsnlzeSID, credential = msidPin, mthdUID = sedVar.UIDmethod_setTable, dataType = sedVar.TYPE_pin)
    sessionType = 'Personalize SID'
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

#####################################################################
##########   Used personlaize MakerSymK with a new value   ##########
#####################################################################
def personalizeSymK(makerSymK = 0, maintSymK = 0, activateSymK = 0):      #Similar to Test 575, Mode:0x04
    if makerSymK == 1:
        keyType = 'DiagKey'
        sessionType = 'Personlize MakerSymK Step Two'
        tempUID = UID_makerSymK_AES256
    elif maintSymK == 1:
        keyType = 'MaintKey'
        sessionType = 'Personlize MaintSymK Step Two'
        tempUID = UID_maintSymK_AES256
    elif activateSymK:
        keyType =  'ActKey'
        sessionType = 'Personlize ActivationSymK Step Two'
        tempUID = UID_activateSymK_AES256

    if testSwitch.FE_0241189_231166_P_NEW_TDCI_API_RETRIES:
       method, prms = makeTDCICall( 'getUniqueKey', HDASerialNumber, keyType, 'AES256', '0')
    else:
       method,prms = RequestService('GetUniqueKey',(HDASerialNumber,keyType,'AES256','0'))
    statMsg("method: %s; prms: %s"%(method,prms,))

    if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
        if prms.has_key('uniqueKey'):
            statMsg("entire return data from XML-RPC Server (dictionary) %s" % (prms))
            statMsg("uniqueKey found in key dictionary")
            responseString = prms['uniqueKey']
            statMsg("hex response string: %s" %binascii.hexlify(base64.decodestring(responseString)))
            statMsg("response from server %s" % responseString)
            statMsg("base64 decoded %s" % base64.b64decode(responseString))
            uniqueKeyString = binascii.b2a_hex(base64.b64decode(responseString))
            statMsg("Unique Key length = %s" %len(uniqueKeyString))
            statMsg("sPort Enable Key = %s" %uniqueKeyString)
            symKUniqueKey = binascii.a2b_hex(uniqueKeyString)
            statMsg("sPort Enable Key = %s" %symKUniqueKey)
            stat = 0
        else:
            statMsg("entire return data from XML-RPC Server (dictionary) %s" %(prms))
            statMsg('[34] ' + method + '"uniqueKey" not found in data from server')
    symkKey = prependAtom(preString = symKUniqueKey, cont = 1)
    packet = createPacket(type = 'psnlzeSIDS_Bands_SymK2', credential = symkKey, mthdUID = sedVar.UIDmethod_setTable, UID = tempUID, dataType = sedVar.TYPE_key)
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

################################################################
##########   Used to personalize all the SID values   ##########
################################################################
def personlizeSIDS(toDefault = 0):
    personalizePSID(toDefValue = toDefault)
    personalizeMSID(toDefValue = toDefault)
    personalizeSID(toDefValue = toDefault)

##############################################################
##########   Used to personalize the Erase Master   ##########
##############################################################
def personalizeEraseMaster(toDefValue = 0):     #Similar to Test 575, Mode:0x04
    if toDefValue == 1:
        msidPin = prependAtom(preString = MSID_defaultPin, cont = 1)
    else:
        retrMsid(fromFIS = 0)
        msidPin = prependAtom(preString = sedVar.global_fisMSID, cont = 1)
    packet = createPacket(type = 'psnlzeSIDS_Bands_SymK2', UID = UID_prsnlzeEraseMstr, credential = msidPin, mthdUID = sedVar.UIDmethod_setTable, dataType = sedVar.TYPE_pin)
    sessionType = 'Personalize Erase Master'
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

#########################################################################
##########   Used to personalize a band to a different value   ##########
#########################################################################
def personalizeBand(band, bandUID, toDefValue = 0):     #Similar to Test 575, Mode:0x04
    if toDefValue == 1:
        msidPin = prependAtom(preString = MSID_defaultPin, cont = 1)
    else:
        retrMsid(fromFIS = 0)
        msidPin = prependAtom(preString = sedVar.global_fisMSID, cont = 1)
    packet = createPacket(type = 'psnlzeSIDS_Bands_SymK2', UID = bandUID, credential = msidPin, mthdUID = sedVar.UIDmethod_setTable, dataType = sedVar.TYPE_pin)
    sessionType = 'Personalize Band %d' %(band)
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

################################################################
##########   Enables/Disables Firmware Lock on Reset  ##########
################################################################
def enableDisableFwLOR(lockPort = 0):   #Similar to Test 575, Mode:0x15,0x2C
    if lockPort == 1:
        sessionType = 'Enable Lock FW Port on Reset'
        packet = createPacket(type = 'portLORLockingFW_Bnd', UID = UID_fwLockingPort, state = '\x00', mthdUID = sedVar.UIDmethod_setTable) #state=0 means Set LOR
    else:
        sessionType = 'Disable Lock FW Port on Reset'
        packet = createPacket(type = 'portLORLockingFW_Bnd', UID = UID_fwLockingPort, mthdUID = sedVar.UIDmethod_setTable) #state = null means Not Set LOR
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

################################################################
##########   Enables/Disables Firmware Port Locking   ##########
################################################################
def lockUnlockFwPort(lockPort = 0):     #Similar to Test 575, Mode:0x13,0x19
    if lockPort == 1:
        sessionType = 'Enable Lock FW Port'
        packet = createPacket(type = 'fwPortLocking', UID = UID_fwLockingPort, state = '\x01', mthdUID = sedVar.UIDmethod_setTable) #state=1  means lock
    else:
        sessionType = 'Disable Lock FW Port '
        packet = createPacket(type = 'fwPortLocking', UID = UID_fwLockingPort, state = '\x00', mthdUID = sedVar.UIDmethod_setTable) #state = 0 means unlock
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

################################################################
##########   Enables/Disables Firmware Port Locking   ##########
################################################################
def lockUnlockDiagPort(lockPort = 1):
    if lockPort == 1:
        sessionType = 'Enable Lock DIAG Port'
        packet = createPacket(type = 'fwPortLocking', UID = UID_diagLockingPort, state = '\x01', mthdUID = sedVar.UIDmethod_setTable) #state=1  means lock
    else:
        sessionType = 'Disable Lock DIAG Port '
        packet = createPacket(type = 'fwPortLocking', UID = UID_diagLockingPort, state = '\x00', mthdUID = sedVar.UIDmethod_setTable) #state = 0 means unlock
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

################################################################
##########   Enables/Disables Firmware Port Locking   ##########
################################################################
def lockUnlockUDSPort(lockPort = 1):
    if lockPort == 1:
        sessionType = 'Enable Lock UDS Port'
        packet = createPacket(type = 'fwPortLocking', UID = UID_udsLockingPort, state = '\x01', mthdUID = sedVar.UIDmethod_setTable) #state=1  means lock
    else:
        sessionType = 'Disable Lock UDS Port '
        packet = createPacket(type = 'fwPortLocking', UID = UID_udsLockingPort, state = '\x00', mthdUID = sedVar.UIDmethod_setTable) #state = 0 means unlock
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)


################################################################
##########   Enables/Disables Firmware Port Locking   ##########
################################################################
def lockUnlockCrossSegFWDnldPort(lockPort = 1):
    if lockPort == 1:
        sessionType = 'Enable Lock CSFW Port'
        packet = createPacket(type = 'fwPortLocking', UID = UID_crossSegFwDnldPort, state = '\x01', mthdUID = sedVar.UIDmethod_setTable) #state=1  means lock
    else:
        sessionType = 'Disable Lock CSFW RW Port '
        packet = createPacket(type = 'fwPortLocking', UID = UID_crossSegFwDnldPort, state = '\x00', mthdUID = sedVar.UIDmethod_setTable) #state = 0 means unlock
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

###################################################
##########   Lock/Unlock IEEE 1667 Port  ##########
###################################################
def lockUnlockIEEE1667Port(lockPort = 1):
    if lockPort == 1:
        sessionType = 'Enable Lock IEEE 1667 Port'
        packet = createPacket(type = 'fwPortLocking', UID = UID_ieee1667Port, state = '\x01', mthdUID = sedVar.UIDmethod_setTable) #state=1  means enable Port
    else:
        sessionType = 'Disable Lock IEEE 1667 Port '
        packet = createPacket(type = 'fwPortLocking', UID = UID_ieee1667Port, state = '\x00', mthdUID = sedVar.UIDmethod_setTable) #state = 0 means disable Port
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

#################################################################
##########   Enables/Disables IEEE 1667 Lock on Reset  ##########
#################################################################
def enableDisableIEEE1667Port(lockPort = 0):   #Similar to Test 575, Mode:0x15,0x2C
    if lockPort == 1:
        sessionType = 'Enable IEEE 1667 Port Lock on Reset'
        packet = createPacket(type = 'portLORLockingFW_Bnd', UID = UID_ieee1667Port, state = '\x00', mthdUID = sedVar.UIDmethod_setTable) #state=0 means Set LOR
    else:
        sessionType = 'Disable IEEE 1667 Port Lock on Reset'
        packet = createPacket(type = 'portLORLockingFW_Bnd', UID = UID_ieee1667Port, mthdUID = sedVar.UIDmethod_setTable) #state = null means Not Set LOR
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)


###################################################################################
##########   Enables/Disables bands 2 - 15 so they can be personalized   ##########
###################################################################################
def enableDisableBand(band, bandUID, enableBand = 1):   #Similar to Test 575, Mode:0x16,0x17(Modes are disabled in I/O code 6/4/12)
    if enableBand == 1:
        sessionType = 'Enable Band %d' %(band)
        packet = createPacket(type = 'enbleDisbleBand_MaintSymK', UID = bandUID, state = '\x01', mthdUID = sedVar.UIDmethod_setTable) #state=01 means enable Band
    else:
        sessionType = 'Disable Band %d' %(band)
        packet = createPacket(type = 'enbleDisbleBand_MaintSymK', UID = bandUID, state = '\x00', mthdUID = sedVar.UIDmethod_setTable) #state = 00 means disable band
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)

###################################################################################
##########   Lock/Unlock RW Locks 0 - 15 so they can be personalized   ##########
###################################################################################
def setRwAndLorBandLocking(band, bandUID, adjustLOR = 1, setLORBands = 1):
    if adjustLOR == 1:
        if setLORBands == 1:
            sessionType = 'Set Band %d LOR Lock' %(band)
            packet = createPacket(type = 'portLORLockingFW_Bnd', UID = bandUID, mthdUID = sedVar.UIDmethod_setTable, state = '\x00')  #\x00 means Set Lock
        else:
            sessionType = 'Do Not Set Band %d LOR Lock' %(band)
            packet = createPacket(type = 'portLORLockingFW_Bnd', UID = bandUID, mthdUID = sedVar.UIDmethod_setTable, state = '')  # null means don't set lock
        sendPacket(frame = packet, m_type = sessionType)
        getPacket(m_type = sessionType,checkRcvStat = 1)

    sessionType = 'Set Band %d RW Locks' %(band)
    packet = createPacket(type = 'bandRWLocking', UID = bandUID, mthdUID = sedVar.UIDmethod_setTable)
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType,checkRcvStat = 1)


###################################################################################
##########   Enables/Disables MaintSymk    ########################################
###################################################################################
def enableMainSymK():   #Similar to Test 575, Mode:0x2A
    sessionType = 'Enable MaintSymK'
    packet = createPacket(type = 'enbleDisbleBand_MaintSymK', UID = UID_authMaintSymk, mthdUID = sedVar.UIDmethod_setTable, state = '\x01')
    sendPacket(frame = packet, m_type = sessionType)
    statusPacket = getPacket(m_type = sessionType,checkRcvStat = 0)
    if statusPacket[63:64] == '\x00':
        symKEnabled = 0
    else:
        symKEnabled = 1
    return symKEnabled

###################################################################################
##########   Set ISE fo PSID is Master Authority ##################################
###################################################################################
def setISE_ACE():     #Similar to part of Test 577
    sessionType = 'Set ISE by Removing MSID Access Control Element'
    packet = createPacket(type = 'modifyACE', UID = UID_MSIDGet, mthdUID = UIDmethod_removeACE)
    sendPacket(frame = packet, m_type = sessionType)
    statusPacket = getPacket(m_type = sessionType,checkRcvStat = 0)

    sessionType = 'Set ISE by Adding PSID Access Control Element'
    packet = createPacket(type = 'modifyACE', UID = UID_PSIDMakers_MSIDGet, mthdUID = UIDmethod_addACE)
    sendPacket(frame = packet, m_type = sessionType)
    statusPacket = getPacket(m_type = sessionType,checkRcvStat = 0)

#########################################################################
##########  Use to Activate different types of Secure Drives ############
#########################################################################
def TCGActivate(tcgType = 'SDD'):
    SEDdiscovery()

    if not sedVar.autoDetectRan:
        abort(failVal = 10253, failStr='Auto-Detect must be ran before activation is allowed')

    if tcgType not in sedVar.suppActiveConfigTypes:
        failMsg = 'Activation Type %s is not supported' %tcgType
        abort(failVal = 10253, failStr=failMsg)

    if tcgType == 'SDD':
        activateUID = UID_activateSDD
        sedVar.enableISE = 0
        sedVar.secureBaseDriveType = 1
    elif tcgType == 'ISE':
        activateUID = UID_activateISE
        sedVar.enableISE = 1
        sedVar.secureBaseDriveType = 0
    elif tcgType == 'SED':
        activateUID = UID_activateSED
        sedVar.enableISE = 0
        sedVar.secureBaseDriveType = 0
    elif tcgType == 'FIPS':
        activateUID = UID_activateFIPS
        sedVar.enableISE = 0
        sedVar.secureBaseDriveType = 0
    else:
        sessionType = 'Activation Type %s does not exist' %tcgType
        abort(failVal = 10468, failStr=sessionType)

    sessionType = 'Activate TCG Type %s' %tcgType
    packet = createPacket(type = 'activateMethod', mthdUID = activateUID)
    sendPacket(frame = packet, m_type = sessionType)
    ScriptPause(2)
    statusPacket = getPacket(m_type = sessionType,checkRcvStat = 0)

    authenStartSess()
    authenSIDSMaker(default = 0, firstRun = 0)

###################################################################################
##########   Set SDD for Makers as Master Authority ##################################
###################################################################################
def setSDD_ACE():     #Similar to part of Test 577
    sessionType = 'Set SDD by Removing MSID Access Control Element'
    packet = createPacket(type = 'modifyACE', UID = UID_MSIDGet, mthdUID = UIDmethod_removeACE)
    sendPacket(frame = packet, m_type = sessionType)
    statusPacket = getPacket(m_type = sessionType,checkRcvStat = 0)

    sessionType = 'Set SDD by Adding Makers as Access Control Element'
    packet = createPacket(type = 'modifyACE', UID = UID_Makers_MSIDGetNew, mthdUID = UIDmethod_addACE)
    sendPacket(frame = packet, m_type = sessionType)
    statusPacket = getPacket(m_type = sessionType,checkRcvStat = 0)

###########################################################################
##########   Set to SOM 0 State    ########################################
###########################################################################
def setSOM0():  #Similar to Test 575, Mode:0x1A
    sessionType = 'Set SOM State to SOM 0'
    packet = createPacket(type = 'setStateTbl_SOM0', UID = UID_SetSOM0, mthdUID = sedVar.UIDmethod_setTable, state = '\x00')
    sendPacket(frame = packet, m_type = sessionType)
    getPacket(m_type = sessionType, checkRcvStat = 0)

###########################################################################
##########   Capture Persistant Data    ###################################
###########################################################################
def capturePersisData():    #Similar to Test 575, Mode:0x1D
    sessionType = 'Capture persistant data'
    packet = createPacket(type = 'capturePersistData_revert', UID = UID_spUID, mthdUID =UID_capPersisData)
    sendPacket(frame = packet, m_type = sessionType)
    time.sleep(4)
    getPacket(m_type = sessionType, checkRcvStat = 0)

###########################################################################
##########   Revert Drive/Set ATA Master Password    #################
###########################################################################
def revertAdminSP():      #Note: After performing revertAdminSP() session is automatically closed.
    sessionType = 'Revert Admin SP'
    packet = createPacket(type = 'capturePersistData_revert', UID =UID_spUID, mthdUID = UID_revertAdminSP)
    sendPacket(frame = packet, m_type = sessionType)
    time.sleep(16)  #Required so drive won't fail
    getPacket(m_type = sessionType, checkRcvStat = 0)


#######################################################################
##########   Used to personalize each of the Locking Bands   ##########
#######################################################################
def personalizeLockingBands(fromDefVal = 1, toDefVal = 0, startAtBand = 99, endBand = 99):  #Similar to part of Test 577  #if Bands aren't specified it does all of them
    if startAtBand < 99:
        if startAtBand <= 16:
            firstBand = startAtBand
        else:
            statMsg("Beginning Band was set to %d which is out of Locking SP Band Range.  Set to 16" %startAtBand)
            firstBand = 16
    else:
        firstBand = 0

    if endBand < 99:
        if endBand <= 16:
            lastBand = endBand
        else:
            statMsg("End band was set to %d which is out of Locking SP Band Range.  Set to 16" %endBand)
            lastBand = 16
    else:
        lastBand = 16

    for i in range (firstBand,lastBand):  #used for the 16 bands
        k = hex(i+1)
        if(i<15):
            j = '0' + k[2:]
        else:
            j = k[2:]
        bandMastAuthUid    = '\x00\x00\x00\x09\x00\x00\x80' + binascii.unhexlify(j)
        bandMastWriteUid   = '\x00\x00\x00\x0B\x00\x00\x80' + binascii.unhexlify(j)
        bandMastLockingUid = '\x00\x00\x08\x02\x00\x00\x00' + binascii.unhexlify(j)   #Last byte changes with each band. Band 0 = \x01, Band 1 = \x02....
        if i>1:     ##Need to enable bands for bands 2 and on
            enableDisableBand(band = i, bandUID = bandMastAuthUid, enableBand = 1)

        authenBand(band = i, fromDefValue = fromDefVal, bandUID = bandMastAuthUid )
        setRwAndLorBandLocking(band = i, bandUID = bandMastLockingUid, adjustLOR = 1, setLORBands = 1)
        personalizeBand(toDefValue = toDefVal, bandUID = bandMastWriteUid, band = i)
        if i>1:    ##Need to disable bands for band 2 and on since enabled earlier.
            enableDisableBand(band = i, bandUID = bandMastAuthUid, enableBand = 0)

############################################################
##########   Used to retrieve band locking data   ##########
############################################################
def checkBandLockingValues(startAtBand = 0, endBand = 16,LOCK_ON_RESET=0,WRITE_LOCK_ENABLED=0,READ_LOCK_ENABLED=0,WRITE_LOCKED=1,READ_LOCKED=1,RANGE_LENGTH=0,RANGE_START=0):

    if startAtBand < 16:
        firstBand = startAtBand
    else:
        statMsg("Beginning Band was set to %d which is out of Locking SP Band Range.  Set to 16" %startAtBand)
        firstBand = 16

    if endBand <= 16:
        lastBand = endBand
    else:
        statMsg("End band was set to %d which is out of Locking SP Band Range.  Set to 16" %endBand)
        lastBand = 16

    for i in range (firstBand,lastBand):  #used for the 16 bands
        k = hex(i+1)
        if(i<15):
            j = '0' + k[2:]
        else:
            j = k[2:]
        bandMastLockingUid = '\x00\x00\x08\x02\x00\x00\x00' + binascii.unhexlify(j)   #Last byte changes with each band. Band 0 = \x01, Band 1 = \x02....
        packet = getTable(UID = bandMastLockingUid, lookUpUID = 0)
        RangeStartKey,RangeLengthKey,ReadLockEnabledKey,WriteLockEnabledKey,ReadLockedKey,WriteLockedKey,LockOnResetKey = parseBandLockingData(data = packet, checkLocking=1)

        if RANGE_START != RangeStartKey:
            raise Exception("Band: %d has a Range Start of %d and we specified we expect it to be %d" %(i,RangeStartKey,RANGE_START))
        if RANGE_LENGTH != RangeLengthKey:
            raise Exception("Band: %d has a Range Length of %d and we specified we expect it to be %d" %(i,RangeLengthKey,RANGE_LENGTH))
        if READ_LOCK_ENABLED != ReadLockEnabledKey:
            raise Exception("Band: %d has a Read Locked Enabled Value of %d and we specified we expect it to be %d" %(i,ReadLockEnabledKey,READ_LOCK_ENABLED))
        if WRITE_LOCK_ENABLED != WriteLockEnabledKey:
            raise Exception("Band: %d has a Write Lock Enabled Value of %d and we specified we expect it to be %d" %(i,WriteLockEnabledKey,WRITE_LOCK_ENABLED))
        if READ_LOCKED != ReadLockedKey:
            raise Exception("Band: %d has a Read Locked Value of %d and we specified we expect it to be %d" %(i,ReadLockedKey,READ_LOCKED))
        if WRITE_LOCKED != WriteLockedKey:
            raise Exception("Band: %d has a Write Locked Value of %d and we specified we expect it to be %d" %(i,WriteLockedKey,WRITE_LOCKED))
        if LOCK_ON_RESET != LockOnResetKey:
            raise Exception("Band: %d has a Lock On Reset Value of %d and we specified we expect it to be %d" %(i,LockOnResetKey,LOCK_ON_RESET))


############################################################
##########   Used to retrieve band locking data   ##########
############################################################
def checkBandEnableValues(startAtBand = 0, endBand = 16,BAND_ENABLED=0):

    if startAtBand < 16:
        firstBand = startAtBand
    else:
        statMsg("Beginning Band was set to %d which is out of Locking SP Band Range.  Set to 16" %startAtBand)
        firstBand = 16

    if endBand <= 16:
        lastBand = endBand
    else:
        statMsg("End band was set to %d which is out of Locking SP Band Range.  Set to 16" %endBand)
        lastBand = 16

    for i in range (firstBand,lastBand):  #used for the 16 bands
        k = hex(i+1)
        if(i<15):
            j = '0' + k[2:]
        else:
            j = k[2:]
        bandMastAuthUid    = '\x00\x00\x00\x09\x00\x00\x80' + binascii.unhexlify(j)
        packet = getTable(UID = bandMastAuthUid, lookUpUID = 0)
        EnabledKey = parseBandLockingData(data = packet,checkEnable=1)

        if BAND_ENABLED != EnabledKey:
            raise Exception("Band: %d has a Band Enabled Value of %d and we specified we expect it to be %d" %(i,EnabledKey,BAND_ENABLED))


#############################################################
##########   Used to Parse out Port Locking data   ##########
#############################################################
def parsePortLockingData(data=''):

    LockName_LockOnReset = '\x4c\x6f\x63\x6b\x4f\x6e\x52\x65\x73\x65\x74'
    LockName_PortLocked = '\x50\x6f\x72\x74\x4c\x6f\x63\x6b\x65\x64'

    LockType_FWDownload = '\x46\x57\x44\x6f\x77\x6e\x6c\x6f\x61\x64'
    LockType_Diagnostics = '\x44\x69\x61\x67\x6e\x6f\x73\x74\x69\x63\x73'
    LockType_UDS = '\x55\x44\x53'
    LockType_CSFW = '\x43\x53\x46\x57\x44\x6f\x77\x6e\x6c\x6f\x61\x64'
    LockType_ieee1667= '\x12\x41\x63\x74\x69\x76\x61\x74\x69\x6f\x6e\x49\x45\x45\x45\x31\x36\x36\x37'

    breakOuterLoop = 0
    index = 0
    dataLength = len(data)
    if sedVar.driveType == ENTERPRISE and sedVar.coreSpec == 1:
        for index in range(0,dataLength):
            if data[index:index+len(LockName_LockOnReset)] == LockName_LockOnReset:
                LORkey = data[index+12:index+13]
            if data[index:index+len(LockName_PortLocked)] == LockName_PortLocked:
                LockPortkey = data[index+10:index+11]

    elif sedVar.driveType == OPAL and sedVar.coreSpec == 2:
        for index in range(0,dataLength):
            if breakOuterLoop ==1:
                break
            if (data[index:index+len(LockType_FWDownload)] == LockType_FWDownload) or (data[index:index+len(LockType_Diagnostics)] == LockType_Diagnostics) or (data[index:index+len(LockType_UDS)] == LockType_UDS) or (data[index:index+len(LockType_CSFW)] == LockType_CSFW) or (data[index:index+len(LockType_ieee1667)] == LockType_ieee1667):
                
                nameColumn = data[index-2:index-1]
                for tempIndx in range(index,dataLength):
                    if (data[tempIndx:tempIndx+2] == '\xf3\xf2'):
                        tempNameColumn = binascii.a2b_hex('0' + str(int(binascii.hexlify(nameColumn),16)+1))
                        if data[tempIndx+2:tempIndx+3] == tempNameColumn:
                            nameColumn = binascii.a2b_hex('0' + str(int(binascii.hexlify(nameColumn),16) + 1))
                            LORkey = data[tempIndx+4:tempIndx+5]
                    elif (data[tempIndx:tempIndx+3] == '\xf1\xf3\xf2'):
                        tempNameColumn = binascii.a2b_hex('0' + str(int(binascii.hexlify(nameColumn),16)+1))
                        if data[tempIndx+3:tempIndx+4] == tempNameColumn:
                            LockPortkey = data[tempIndx+4:tempIndx+5]
                            breakOuterLoop = 1
                            break

    return LORkey,LockPortkey

#############################################################
##########   Used to Parse out Band Locking data   ##########   Not Applicable to Opal currently
#############################################################
def parseBandLockingData(data='', checkEnable=0,checkLocking=0):

    LockName_LockOnReset = '\x4c\x6f\x63\x6b\x4f\x6e\x52\x65\x73\x65\x74'
    LockName_RangeStart = '\x52\x61\x6e\x67\x65\x53\x74\x61\x72\x74'
    LockName_RangeLength = '\xab\x52\x61\x6e\x67\x65\x4c\x65\x6e\x67\x74\x68'
    LockName_ReadLockEnabled = '\x52\x65\x61\x64\x4c\x6f\x63\x6b\x45\x6e\x61\x62\x6c\x65\x64'
    LockName_WriteLockEnabled = '\x57\x72\x69\x74\x65\x4c\x6f\x63\x6b\x45\x6e\x61\x62\x6c\x65\x64'
    LockName_ReadLocked = '\x52\x65\x61\x64\x4c\x6f\x63\x6b\x65\x64'
    LockName_WriteLocked = '\x57\x72\x69\x74\x65\x4c\x6f\x63\x6b\x65\x64'
    LockName_Enabled = '\x45\x6e\x61\x62\x6c\x65\x64'

    index = 0
    if sedVar.driveType == ENTERPRISE and sedVar.coreSpec == 1:
        if checkEnable == 1:
            while index < len(data):
                if data[index:index+len(LockName_Enabled)] == LockName_Enabled:
                    index = index + len(LockName_Enabled)
                    EnabledKey = int(binascii.hexlify(data[index:index+1]),16)
                    return EnabledKey
                index = index + 1

        if checkLocking == 1:
            while index < len(data):
                if data[index:index+len(LockName_RangeStart)] == LockName_RangeStart:
                    index = index + len(LockName_RangeStart)
                    RangeStartKey = int(binascii.hexlify(data[index:index+1]),16)

                elif data[index:index+len(LockName_RangeLength)] == LockName_RangeLength:
                    index = index + len(LockName_RangeLength)
                    RangeLengthKey = int(binascii.hexlify(data[index:index+1]),16)

                elif data[index:index+len(LockName_ReadLockEnabled)] == LockName_ReadLockEnabled:
                    index = index + len(LockName_ReadLockEnabled)
                    ReadLockEnabledKey = int(binascii.hexlify(data[index:index+1]),16)

                elif data[index:index+len(LockName_WriteLockEnabled)] == LockName_WriteLockEnabled:
                    index = index + len(LockName_WriteLockEnabled)
                    WriteLockEnabledKey = int(binascii.hexlify(data[index:index+1]),16)

                elif data[index:index+len(LockName_ReadLocked)] == LockName_ReadLocked:
                    index = index + len(LockName_ReadLocked)
                    ReadLockedKey = int(binascii.hexlify(data[index:index+1]),16)

                elif data[index:index + len(LockName_WriteLocked)] == LockName_WriteLocked:
                    index = index + len(LockName_WriteLocked)
                    WriteLockedKey = int(binascii.hexlify(data[index:index+1]),16)

                elif data[index:index + len(LockName_LockOnReset)] == LockName_LockOnReset:
                    index = index + len(LockName_LockOnReset) + 1   #Have to add 1 since there is a 'Start List' around the data
                    LockOnResetKey = int(binascii.hexlify(data[index:index+1]),16)
                index = index+1
            return RangeStartKey,RangeLengthKey,ReadLockEnabledKey,WriteLockEnabledKey,ReadLockedKey,WriteLockedKey,LockOnResetKey

#############################################################
##########   Used to Parse The Discovery Data      ##########
############################################################
def parseDiscoveryInfo(dataPacket):

    #Enable Debug stat Message so we always print parsed drive type data
    originalStatMsg = sedVar.enableDebugstatMsg
    if not originalStatMsg:
        sedVar.enableDebugstatMsg = 1


    sedVar.suppActiveConfigTypes = []  #Make sure it's cleared since we only append into it
    discovPacketLen = int(binascii.b2a_hex(dataPacket[0:4]),16)
    sedVar.currentSecureState = int(binascii.b2a_hex(dataPacket[17:18]),16)
    statMsg("Drive is state is 0x%x" %(sedVar.currentSecureState))
    statMsg("Discovery length 0x%x" %(discovPacketLen))
    
    #Determine if we can find TCG Version and TCG Type
    tcgVersionDetect = int(binascii.b2a_hex(dataPacket[25:26]),16)
    if tcgVersionDetect != 0:
        if tcgVersionDetect % 2:  #7,9,11 for Opal
            sedVar.coreSpec = 2
            sedVar.driveType = OPAL
        else:
            sedVar.coreSpec = 1
            sedVar.driveType = ENTERPRISE

        if tcgVersionDetect <= 7:
            sedVar.tcgVersion = 1
        elif tcgVersionDetect <= 9:
            sedVar.tcgVersion = 2
        elif tcgVersionDetect <= 11:
            sedVar.tcgVersion = 3
        else:
            statMsg("TCG Version not found, being reported as %d" %(tcgVersionDetect))

        statMsg("TCG Version: %d, TCG Type: %s, TCG Corespec: %d" %(sedVar.tcgVersion,sedVar.driveType,sedVar.coreSpec))

    indexLocation = 0x30
    while indexLocation in range(0x30,discovPacketLen):
        featureDesc = int(binascii.b2a_hex(dataPacket[indexLocation:indexLocation+2]),16)
        subPackLen = int(binascii.b2a_hex(dataPacket[indexLocation+3:indexLocation+4]),16)

        #Case Statements to Parse Data
        if featureDesc == 0x0001:
            statMsg("TPER Feature Parsed")
        elif featureDesc == 0x0002:
            statMsg("LOCKING Feature Parsed")
        elif featureDesc == 0x0003:
            statMsg("GEOMETRY Feature Parsed")
        elif featureDesc == 0x0004:
            statMsg("SECURE MESSAGE Feature Parsed")
        elif featureDesc == 0xC001:  #BJH  NEED TO ADD SUPPORT FOR ALL PORTS
            statMsg("LOGICAL Port Feature Parsed")
        elif featureDesc == 0xC002:
            sedVar.enableISE = 1    
            statMsg("ISE Feature Parsed")
        elif featureDesc == 0xC003:
            sedVar.secureBaseDriveType = 1  
            statMsg("SDD Feature Parsed")
        elif featureDesc == 0xC004:
            sedVar.activateSupport = 1
            statMsg("ACTIVATION Feature Parsed")

            featureVersion = int(binascii.b2a_hex(dataPacket[indexLocation+2:indexLocation+3]),16) >> 4

            if featureVersion == 0x01:   #Activation Version field not yet included
                activationVersion = int(binascii.b2a_hex(dataPacket[indexLocation+4:indexLocation+5]),16)

                if activationVersion == 0x1:
                    subFeatureIndx = 4
                else:
                    subFeatureIndx = 0

                featureFound = 2 #Set to 2 for first loop to indicate currently activated type
                while subFeatureIndx in range(0,subPackLen):
                    config = ''
                    activationConfig = int(binascii.b2a_hex(dataPacket[indexLocation+4+subFeatureIndx:indexLocation+8+subFeatureIndx]),16)
                    if activationConfig == 0xFFFF0005:
                        config = 'SDD'
                    elif activationConfig == 0xFFFF0006:
                        config = 'ISE'
                    elif activationConfig == 0xFFFF0007:
                        config = 'SED'
                    elif activationConfig == 0xFFFF0008:
                        config = 'FIPS'
                    else:
                        featureFound = 0

                    if featureFound == 2:  #Set to 2 on first loop
                        sedVar.currActiveConfig = config
                        statMsg("%s is the Current Activated Config" %(config))
                    elif featureFound:
                        sedVar.suppActiveConfigTypes.append(config) #Add type to array if supported but not on first active config since they will duplicate otherwise
                    else:
                        statMsg('Activation Type found 0x%x and is not valid' %(activationConfig))

                    featureFound = 1
                    subFeatureIndx += 4

                statMsg("ACTIVATION types supported are %s" %(str(sedVar.suppActiveConfigTypes).strip('[]')))

        elif featureDesc == 0x0100:
            if not tcgVersionDetect:
                sedVar.coreSpec = 1
                sedVar.driveType = ENTERPRISE
            sedVar.enableISE = 0
            sedVar.secureBaseDriveType = 0
            statMsg("ENTERPRISE SSC Feature Parsed")
        elif featureDesc == 0x0200:
            if not tcgVersionDetect:
                sedVar.coreSpec = 2
                sedVar.driveType = OPAL
            statMsg("OPAL SSC Feature Parsed")
        elif featureDesc == 0x0201:
            if not tcgVersionDetect:
                sedVar.coreSpec = 2
                sedVar.driveType = OPAL
            statMsg("OPAL SSC SINGLE USER Feature Parsed")
        elif featureDesc == 0x0202:
            if not tcgVersionDetect:
                sedVar.coreSpec = 2
                sedVar.driveType = OPAL
            statMsg("OPAL SSC 202 Feature Parsed")
        elif featureDesc == 0x0203:
            if not tcgVersionDetect:
                sedVar.coreSpec = 2
                sedVar.driveType = OPAL
            sedVar.enableISE = 0
            sedVar.secureBaseDriveType = 0
            statMsg("OPAL SSC V2 Feature Parsed")
        else:
            statMsg("Feature Descripter 0x%x not found" %(featureDesc))

        indexLocation = indexLocation + subPackLen + 4

    #Turn off debug message if not originally turned on
    if not originalStatMsg:
        sedVar.enableDebugstatMsg = 0

    sedVar.autoDetectRan = 1
    sedVar.reInitCoreSpecRelatedVars()


##########   Functions to support the IV download  ##########
#############################################################
def get(size=0):
    data = GChar(readSize = size)
    return data

def put(data, timeout=3):
    PBlock(data)
    size = len(data)
    return size

def calc_crc(data, crc=0):
    crc = binascii.crc_hqx(data,crc)
    return (crc & 0xffff)

def calc_checksum(data, checksum=0):
    return (sum(map(ord, data)) + checksum) % 256

def calc_checksum_scsa(data, packetNum):
    checkSum = 0
    dataLen = len(data)
    for i in range(0,dataLen):
        checkSum ^= (int(binascii.b2a_hex(data[i:i+1]),16) ^ (dataLen * packetNum)) % 256

    return checkSum

def abort(IVFileXfr=0,failVal=11044,failStr='',raiseException = 1):
    CAN = chr(0x18) #Used to send 'cancel' to drive for YMODEM protocol on abort
    if IVFileXfr == 1:
        for counter in xrange(0, 2):
            put(CAN)
    if sedVar.enableCM == 1:
        if raiseException:
           raise Exception(failVal,failStr)
        else:
           statMsg("%s"%failStr)

    else:
        failString = 'Fail Code:' + str(failVal)+ '-' + failStr
        if raiseException:
           raise Exception(failString)
        else:
           statMsg("%s"%failString)

######################################################################
##########  downloadTRD IV file using the YMODEM protocol   ##########
######################################################################
def downloadTRD(stream, fileName, retry=100, timeout=600, reportErr=1):
    SOH     = chr(0x01)
    STX     = chr(0x02)
    EOT     = chr(0x04)
    ACK     = chr(0x06)
    NAK     = chr(0x15)
    CAN     = chr(0x18)
    CRC     = chr(0x43)
    CPMEOF  = chr(0x1A)

    # initialize protocol
    packet_size = 1024
    nullString = ''
    for i in xrange(0,packet_size):
        nullString = nullString + '\x00'
    error_count = 0
    crc_mode = 0
    cancel = 0
    firstRun = 1
    while True:
        retrieve = get(size=1)
        if retrieve:
            if retrieve == NAK:
                crc_mode = 0
                statMsg("CRC Mode: %d" %crc_mode)
                break
            elif retrieve == CRC:
                crc_mode = 1
                statMsg("CRC Mode: %d" %crc_mode)
                break
            elif retrieve == CAN:
                if cancel:
                    abort(IVFileXfr=1, failVal = 14623, failStr = 'Received Cancel while initalizing YMODEM Protocol', raiseException = 0)
                    return 'FAILED'
                else:
                    cancel = 1
        error_count += 1
        if error_count >= retry:
            abort(IVFileXfr=1, failVal = 14623, failStr = 'Unable to initialize IV transfer', raiseException = 0)
            return 'FAILED'

    # send data
    error_count = 0
    packet_size = 1024
    sequence = 0
    statMsg("Starting to transfer the IV file",masterstatMsg=1)
    startTime = time.time()
    while True:
        #ScriptPause(.1)   #Temp fix for IV download issue.
        if firstRun == 1:
            totalLength = '2097152'   #Decimal total for 0x200000
            data = fileName
            data = data + '\x00' + str(totalLength)
            fileNameLength = len(data)
            for i in range(0,(packet_size-fileNameLength)):
                data = data + '\x00'
        else:
            data = stream.read(packet_size)
            fileLength = len(data)
            if (fileLength != packet_size):
                if fileLength > 0:
                    for i in range(0,(packet_size - fileLength)):
                        data = data + CPMEOF
                else:
                    statMsg("Last Packet Received")
                    break
        if firstRun != 0:
            data = data.ljust(packet_size, '\xff')
            if crc_mode:
                crc = calc_crc(data)
            else:
                crc = calc_checksum(data)
        if (time.time() - startTime) > timeout:   # 10 minute limit
           return 'FAILED'

        # emit packet
        while True:
            preCheck = chr(0xff - sequence)
            if crc_mode:
                crc = calc_crc(data)
                crc1 = chr(crc >> 8)
                crc1 = crc1 + chr(crc & 0xff)
            else:
                crc = calc_checksum(data)
                crc1 = chr(crc)
            string1 = STX + chr(sequence) + preCheck + data + crc1
            put(data = string1)
            retrieve = get(size=1)
            if retrieve == ACK:
                if sequence == 0x0 or sequence == 0xFF:
                    retrieve1 = get(size=1)
                    break
                break
            if retrieve == NAK:
                error_count += 1
                if error_count >= retry:
                    # too many retries, abort transfer
                    abort(IVFileXfr=1, failVal = 14623, failStr = 'YMODEM protocol error: Excessive NAKs', raiseException = 0)
                    return 'FAILED'

            # protocol error
            if error_count >= retry:
                abort(IVFileXfr=1, failVal = 14623, failStr = 'YMODEM protocol error', raiseException = 0)
                return 'FAILED'

            if (time.time() - startTime) > timeout:   # 10 minute limit
               return 'FAILED'


        firstRun = 0
        # keep track of sequence
        sequence = (sequence + 1) % 0x100


    # end of transmission
    put(EOT)
    for endTrans in range(0,11):
        retrieve = get(1)
        if endTrans == 10:
            abort(IVFileXfr=1, failVal = 14623, failStr = 'FAILED for not receiving ACK for EOT after 10 tries', raiseException = 0)
            return 'FAILED'
        elif retrieve == NAK:
            put(EOT)
        elif retrieve == ACK:
            break
        else:
            put(EOT)
    retrieve1 = get(1)
    if (retrieve1 == CRC) or (retrieve1 == NAK):
        if crc_mode:
            crc = calc_crc(nullString)
            crc1 = chr(crc >> 8)
            crc1 = crc1 + chr(crc & 0xff)
        else:
            crc = calc_checksum(data)
            crc1 = chr(crc)
        string1 = STX + '\x00\xff' + nullString + crc1
        put(string1)
        retrieve = get()
        statMsg('Completed IV download Successfully',masterstatMsg=1)
    else:
        abort(IVFileXfr=1, failVal = 14623, failStr = 'FAILED IV Download for YMODEM end protocol failure', raiseException = 0)
        retrieve = 'FAILED'
    return retrieve

####################################################################################################
##########  Defined Functions to be used for Serial Formating the Drive and F3 Diag Cmds  ##########
####################################################################################################
def asciiToEslipMode():
    CTRL_T = '\x14'
    PChar(CTRL_T);
    ScriptPause(1);
    readme();   # to get command prompt

def readme1():
  data=''
  while 1:
    ScriptPause(60);
    buf=GChar()
    if not buf: break
    else: data+= buf
    statMsg(data.replace("\r", ""))

def readme():
   data=''
   loopStartTime = time.time()
   while 1:
      charIn=GChar(readSize=1)
      data+= charIn
      loopTime = time.time() - loopStartTime
      if loopTime > 2: break
      #if loopTime > 5: break
#      if sedVar.enableDebugstatMsg == 1:
        #statMsg('%s' %data.replace("\r",""))
   if DEBUG:statMsg(data,masterstatMsg = 1) #.replace("\r", "")

def SerialFormatCertifyFactory():
   CTRL_Z  = '\x1A'
   PChar(CTRL_Z);             # spin up drive
   ScriptPause(10);           # allow drive to spin up
   PChar(CTRL_Z); readme();   # to get command prompt
   PBlock('C34F329A\r');      # unlock

   PBlock('m0,0,3,A,5,8,,22\r');  # format with certify
   ScriptPause(1); readme1()      # get progress

def GetSN():
   CTRL_Z  = '\x1A'
   PChar(CTRL_Z);             # spin up drive
   ScriptPause(10);           # allow drive to spin up
   PChar(CTRL_Z); readme();   # to get command prompt
   PBlock('C34F329A\r');      # unlock

   PBlock('J,1\r'); readme(); # read HDA SN

# This was Sumit's
def testfn():
   CTRL_Z  = '\x1A'

   PBlock('J,1\r'); ScriptPause(1); readme()     # read HDA SN
   PBlock('\x2f2\r'); ScriptPause(1); readme()   # Change to level 2
   PBlock('X0\r'); ScriptPause(5); readme()      # Display Track Information

   # Read logical sector 23 on logical cylinder 45 head 1
   PBlock('A0\r'); ScriptPause(1); readme()
   PBlock('S45,1\r'); ScriptPause(1); readme()
   PBlock('R23\r'); ScriptPause(1); readme()
   PBlock('B\r'); ScriptPause(10); readme()

def sendCmd(cmd, maxTmo = 30, delayTime = 0.2, noRespAbort = -1, echo = None):
   if DEBUG: statMsg("Sending %s" % cmd)
   PBlock(cmd + '\n')
   time.sleep(0.2)
   if echo:
      echo = cmd
   return waitPrompt(maxTmo, delayTime, noRespAbort, echo)

def gotoLevel(level):
   PBlock("/" + level + "\n")
   time.sleep(0.1)
   statMsg(GChar())

def waitPrompt(maxTmo = 30, delayTime = 0.2, noRespAbort = -1, echo = None):
   res = ''
   startTime = time.time()
   tmp = ''
   noResp = noRespAbort
   while res.find('>') == -1:
      tmp = GChar()
      res += tmp
      if DEBUG > 1 and len(tmp) > 0: statMsg("recv: %s" % tmp)

      # Remove the echo
      if echo and echo in res:
         res = res[res.find(echo)+len(echo):]
         echo = None

      if noResp == 0:
         statMsg("triggered no response abort")
         break
      else:
         if len(tmp) == 0:
            if DEBUG > 1: statMsg("noresp %d len res %d" % ( noResp, len(res)))
            noResp -= 1
         else:
            noResp = noRespAbort #reset to max

      if time.time() > startTime + maxTmo:
         raise Exception, "Timeout in prompt wait"
      else:
         if delayTime > 0: time.sleep(delayTime)


   #Remove the echo check

   #if DEBUG and len(res) > 0: statMsg "recv: %s" % res
   return res

####################################################################################
##########   Used to create all of the packets being send to the drive.   ##########
####################################################################################
def createPacket(type, credential = '', UID = '', mthdUID = '',  rsaType = '',state = '', band = '', srtSessType = '', location = '', dataType = ''):
    #displayFrame(credential)
    packet = ''
    padding = '\x00\x00\x00'
    dictLen = {}
    comPacketLength = '\x00\x00\x00\x00'
    packetLength = '\x00\x00\x00\x00'
    subPacketLength = '\x00\x00\x00\x00'
    sessionPacket = '\xFF\xFF\xFC' + sedVar.sessionNumber + '\x31\x32\x33\x34' + sedVar.sess_sqNumber + sess_ack  # Size 20
    if sedVar.coreSpec == 1:
        if type == 'closeSession':
            packet = '\xFA'
        if type == 'authSymK2_Ers_Bnd_SIDS':
            packet = '\xF8\xA8' + UID_spUID + '\xA8' + mthdUID + '\xF0\xA8' + UID + '\xF2\xA9\x43\x68\x61\x6C\x6C\x65\x6E\x67\x65' + credential + '\xF3' + endPacket
        if type == 'psnlzeSIDS_Bands_SymK2':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF0\xF2\xAB\x73\x74\x61\x72\x74\x43\x6F\x6C\x75\x6D\x6E\xA3' + dataType + '\xF3\xF2\xA9\x65\x6E\x64\x43\x6F\x6C\x75\x6D\x6E\xA3' + dataType + '\xF3\xF1\xF0\xF0\xF2\xA3' + dataType + credential + '\xF3\xF1\xF1' + endPacket
        if type == 'authSymKAmp1':
            packet = '\xF8\xA8' + UID_spUID + '\xA8' + mthdUID + '\xF0\xA8' + UID + endPacket
        if type == 'getTbl':
            packet = '\xF8\xA8' + UID + '\xA8' + sedVar.UIDmethod_getTable + '\xF0\xF0\xF1' + endPacket
        if type == 'setStateTbl_SOM0':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF0\xF1\xA1' + state + endPacket
        if type == 'authSess':
            sessionPacket = filler_8bytesZero + srtSessType + filler_8bytesZero  # Size 20
            packet = '\xF8\xA8' + UIDmethod_smUID + '\xA8' + UID_startSession + '\xF0\x84\x31\x32\x33\x34\xA8' + UID + '\x01' + endPacket
        if type == 'enbleDisbleBand_MaintSymK':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF0\xF1\xF0\xF0\xF2\xA7\x45\x6E\x61\x62\x6C\x65\x64' + state + '\xF3\xF1\xF1' + endPacket
        if type == 'getDrvMsid':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF0\xF2\xAB\x73\x74\x61\x72\x74\x43\x6F\x6C\x75\x6D\x6E\xA3\x50\x49\x4E\xF3\xF2\xA9\x65\x6E\x64\x43\x6F\x6C\x75\x6D\x6E\xA3\x50\x49\x4E\xF3\xF1' + endPacket
        if type == 'portLORLockingFW_Bnd':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF0\xF1\xF0\xF0\xF2\xAB\x4C\x6F\x63\x6B\x4F\x6E\x52\x65\x73\x65\x74\xF0' + state + '\xF1\xF3\xF1\xF1' + endPacket
        if type == 'fwPortLocking':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF0\xF2\xAB\x73\x74\x61\x72\x74\x43\x6F\x6C\x75\x6D\x6E\xAA\x50\x6F\x72\x74\x4C\x6F\x63\x6B\x65\x64\xF3\xF2\xA9\x65\x6E\x64\x43\x6F\x6C\x75\x6D\x6E\xAA\x50\x6F\x72\x74\x4C\x6F\x63\x6B\x65\x64\xF3\xF1\xF0\xF0\xF2\xAA\x50\x6F\x72\x74\x4C\x6F\x63\x6B\x65\x64' + state + '\xF3\xF1\xF1' + endPacket
        if type == 'bandRWLocking':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF0\xF2\xAB\x73\x74\x61\x72\x74\x43\x6F\x6C\x75\x6D\x6E\xAF\x52\x65\x61\x64\x4C\x6F\x63\x6B\x45\x6E\x61\x62\x6C\x65\x64\xF3\xF2\xA9\x65\x6E\x64\x43\x6F\x6C\x75\x6D\x6E\xAB\x57\x72\x69\x74\x65\x4C\x6F\x63\x6B\x65\x64\xF3\xF1\xF0\xF0\xF2\xAF\x52\x65\x61\x64\x4C\x6F\x63\x6B\x45\x6E\x61\x62\x6C\x65\x64\x00\xF3\xF2\xD0\x10\x57\x72\x69\x74\x65\x4C\x6F\x63\x6B\x45\x6E\x61\x62\x6C\x65\x64\x00\xF3\xF2\xAA\x52\x65\x61\x64\x4C\x6F\x63\x6B\x65\x64\x01\xF3\xF2\xAB\x57\x72\x69\x74\x65\x4C\x6F\x63\x6B\x65\x64\x01\xF3\xF1\xF1' + endPacket
        if type == 'capturePersistData_revert':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0' + endPacket
        if type == 'getRandomNumber':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0' + '\x20' + endPacket
        if type == 'modifyACE':
            packet = '\xF8\xA8' + UID_accessCtrlTbl + '\xA8' + mthdUID + '\xF0\xA8' + UID_retrDrvMSID + '\xA8' + sedVar.UIDmethod_getTable +  '\xA8' + UID + endPacket
        if type == 'certificate':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF0\xF2' + cert_startRow + location + '\xF3\xF1' + credential + endPacket
        if type == 'RSA':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF0\xF2' + rsa_startClm +  rsaType + '\xF3\xF2' + rsa_endClm + rsaType + '\xF3\xF1\xF0\xF0\xF2' + rsaType + credential + '\xF3\xF1\xF1' +  endPacket
        if type == 'activateMethod':
            packet = '\xF8\xA8' + UID_spUID + '\xA8' + mthdUID + '\xF0' + endPacket
        if packet == '':
            raise Exception('Inital Send Packet was unable to be created.  Double check the session type is specified in the function, createPacket(). ')
    elif sedVar.coreSpec == 2:
        if type == 'closeSession':
            packet = '\xFA'
        if type == 'authSymK2_Ers_Bnd_SIDS':
            packet = '\xF8\xA8' + UID_spUID + '\xA8' + mthdUID + '\xF0\xA8' + UID + '\xF2\x00' + credential + '\xF3' + endPacket
        if type == 'psnlzeSIDS_Bands_SymK2':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF2\x01\xF0\xF2\x03' + credential + '\xF3\xF1\xF3' + endPacket
        if type == 'authSymKAmp1':
            packet = '\xF8\xA8' + UID_spUID + '\xA8' + mthdUID + '\xF0\xA8' + UID + endPacket
        if type == 'getTbl':
            packet = '\xF8\xA8' + UID + '\xA8' + sedVar.UIDmethod_getTable + '\xF0\xF0\xF1' + endPacket
        if type == 'setStateTbl_SOM0':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF2\x01\xA1' + state + '\xF3' +endPacket
        if type == 'authSess':
            sessionPacket = filler_8bytesZero + srtSessType + filler_8bytesZero  # Size 20
            packet = '\xF8\xA8' + UIDmethod_smUID + '\xA8' + UID_startSession + '\xF0\x84\x31\x32\x33\x34\xA8' + UID + '\x01' + endPacket
        if type == 'enbleDisbleBand_MaintSymK':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF2\x01\xF0\xF2\x05' + state + '\xF3\xF1\xF3' + endPacket
        if type == 'getDrvMsid':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF0\xF2\x03\x03\xF3\xF2\x04\x03\xF3\xF1' + endPacket
        if type == 'portLORLockingFW_Bnd':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF2\x01\xF0\xF2\x02\xF0' + state + '\xF1\xF3\xF1\xF3' + endPacket
        if type == 'fwPortLocking':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF2\x01\xF0\xF2\x03' + state + '\xF3\xF1\xF3' + endPacket
        #if type == 'bandRWLocking':
        #    packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF0\xF2\xAB\x73\x74\x61\x72\x74\x43\x6F\x6C\x75\x6D\x6E\xAF\x52\x65\x61\x64\x4C\x6F\x63\x6B\x45\x6E\x61\x62\x6C\x65\x64\xF3\xF2\xA9\x65\x6E\x64\x43\x6F\x6C\x75\x6D\x6E\xAB\x57\x72\x69\x74\x65\x4C\x6F\x63\x6B\x65\x64\xF3\xF1\xF0\xF0\xF2\xAF\x52\x65\x61\x64\x4C\x6F\x63\x6B\x45\x6E\x61\x62\x6C\x65\x64\x00\xF3\xF2\xD0\x10\x57\x72\x69\x74\x65\x4C\x6F\x63\x6B\x45\x6E\x61\x62\x6C\x65\x64\x00\xF3\xF2\xAA\x52\x65\x61\x64\x4C\x6F\x63\x6B\x65\x64\x01\xF3\xF2\xAB\x57\x72\x69\x74\x65\x4C\x6F\x63\x6B\x65\x64\x01\xF3\xF1\xF1' + endPacket
        if type == 'capturePersistData_revert':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0' + endPacket
        if type == 'getRandomNumber':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0' + '\x20' + endPacket
        if type == 'modifyACE':
            packet = '\xF8\xA8' + UID_accessCtrlTbl + '\xA8' + mthdUID + '\xF0\xA8' + UID_retrDrvMSID + '\xA8' + sedVar.UIDmethod_getTable +  '\xA8' + UID + endPacket
        if type == 'certificate':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF2\x00' + location + '\xF3\xF2\x01' + credential + '\xF3' + endPacket
        if type == 'RSA':
            packet = '\xF8\xA8' + UID + '\xA8' + mthdUID + '\xF0\xF2\x01\xF0\xF2' +  rsaType + credential + '\xF3\xF1\xF3' +  endPacket
        if type == 'activateMethod':
            packet = '\xF8\xA8' + UID_spUID + '\xA8' + mthdUID + '\xF0' + endPacket
        if packet == '':
            raise Exception('Inital Send Packet was unable to be created.  Double check the session type is specified in the function, createPacket(). ')

    dictLen, calcPadding = getFrameLengths(frame = packet)
    packetFinal = sedVar.PacketHeader + dictLen['comPacketLength'] + sessionPacket + dictLen['packetLength'] + filler_8bytesZero + dictLen['subPacketLength'] + packet + calcPadding
    return packetFinal

def SEDSerAuthUnlocks(DiagUnlock=True, UDSUnlock=False, EndSession=True):
   """Ability to Authenticate, Unlock DIAG and/or Unlock UDS ports.
   This only lasts until the next power cycle or reset
   """

   if testSwitch.virtualRun:
      return

   authenStartSess()
   lifecycle = binascii.hexlify(getStateTable())
   ScriptComment("get State Table: %s"%lifecycle)
   if lifecycle != "80":  # If not in USE (80)
      closeSession()
      return
   authenSIDSMaker(default = 0, firstRun = 0)
   if DiagUnlock:
      # Unlock Diag port
      lockUnlockDiagPort(lockPort = 0)

   if UDSUnlock:
      # Unlock UDS port
      lockUnlockUDSPort(lockPort = 0)

   if EndSession:
      # close session
      closeSession()
