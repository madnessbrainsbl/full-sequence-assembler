#-----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                     #
#-----------------------------------------------------------------------------------------#
# $RCSfile: ReliTCG.py $
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReliTCG.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReliTCG.py#1 $
# Level: 3
#-----------------------------------------------------------------------------------------#
from Constants import *
import base64, random, os, time, stat
import ScrCmds
#import MessageHandler as objMsg
from TestParamExtractor import TP
import serialScreen
#from PowerControl import objPwrCtrl
from Rim import objRimType
from Process import CProcess
from Drive import objDut
#from MessageHandler import objMsg      # DT SIC
import MessageHandler as objMsg

#RT110711: Use TCG.py
from TCG import *


###################################################################################################
#                                     UnlockDiagUDE                                               #
#                                                                                                 #
#     This function contains the commands to unlock the DIAG and UDE ports to allow for MFG       #
#     commands to be used while the drive remains in USE state.                                   #
###################################################################################################

#------------------------------------------------------------------------------------------------------#
def ReliUnlockDiagUDE():

   objMsg.printMsg('*'*75)
   objMsg.printMsg("TCG Drive UnlockDiagUDE")
   objMsg.printMsg('*'*75)
   oProcess = CProcess()

   #InitTCGState()
   
   oTCG.CheckFDEState()
   oTCG.UnlockDiagUDE()

   return 0

#------------------------------------------------------------------------------------------------------#
def InitTCGState():


   objMsg.printMsg("*** InitTCGState ")
   oProcess = CProcess()
      
   objMsg.printMsg("Running test 575 - Setting CS1.0/2.0 and EntSSC/OpalSSC support")
   prm_575_00 = {
         'test_num'        : 575,
         'prm_name'        : 'prm_575_00',
         "TEST_MODE"       : (0x0023,),      ##TestMode         (Prm[0] & 0xff)  
         #"CORE_SPEC"       : (self.CS),      ##OpalSSC          (Prm[0] & 0xff)  #CS2.0
         "CORE_SPEC"       : (0x0002,),      ##OpalSSC          (Prm[0] & 0xff)  #CS2.0
         #"SSC_VERSION"     : (self.SSC),     ##OpalSSC          (Prm[0] & 0xff)  #OpalSSC      
         "SSC_VERSION"     : (0x0001,),     ##OpalSSC          (Prm[0] & 0xff)  #OpalSSC      
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
   oProcess.St(prm_575_00,timeout=360) 
                                              
   objMsg.printMsg("*** InitTCGState Done!")

# DT Start - add discovery
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
   }
   oProcess.St(prm_575_01,timeout=360)
   objMsg.printMsg("*** T575 - Discovery Done!")

# DT end


   return 0


#prm_TCG={
#   'CORE_SPEC'       : (0x0002),      # 0x01 = Core Spec 1, 0x02 = Core Spec 2
#   'SSC_VERSION'     : (0x0001),      # 0x00 = ENT_SSC,  0x01 = OPAL_SSC
#   'FDE_TYPE'        : 'FDE Base',
#   'SECURITY_TYPE'   : 'TCG Opal SSC 1.0 FDE',                                
#}

