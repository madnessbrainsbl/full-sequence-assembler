#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: The CodeVer module contains classes and functions pertaining to the storage and extraction of
#                 code revisions to and from the drive and FIS.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CodeVer.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CodeVer.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *

import re, time, traceback
from UserDict import UserDict
import MessageHandler as objMsg
from serialScreen import sptDiagCmds
from Rim import objRimType
from Drive import objDut
from FSO import CFSO

import sptCmds
import struct, string
import ScrCmds
from TestParamExtractor import TP
from ICmdFactory import ICmd
from PowerControl import objPwrCtrl

DEBUG = 0

class BaseCodeVersionInfo:
   """CodeVersionInfo: creates a code verion info container"""

   PRE_CODE_VER_FORMAT = ('SFCL','PROCCL')

   PF3_FORMAT = ('PACKAGE','BRANCH','CL',)

   CTRLL_REGEX = '\s*Package Version:*\s*(?P<PackageVersion>[\.a-zA-Z0-9\-]*)'

   if testSwitch.FE_0122186_354753_SUPPORT_FOR_SAS_REVISIONING:
      CTRLL_REGEX = CTRLL_REGEX + '\s*,[\s\S]*Controller FW Rev:*\s*(?P<ControllerFWRev>[\.a-zA-Z0-9\-]*)'

   CTRLL_REGEX = CTRLL_REGEX + '\s*,[\s\S]*Servo FW Rev:*\s*(?P<SFWVersion>[\.a-zA-Z0-9]*)'
   if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
      CTRLL_REGEX = CTRLL_REGEX + '\s*([\s\S]*TCG IV Version:*\s*(?P<IVVersion>[\.a-zA-Z0-9]*))*'

   format = {'FwRev': 1, 'Build Date': 2, 'UserId': 1,'ProdType': 1, 'CustomerRel': 1,'Changelist':1, 'Time': 1}

   #---------------------------
   def __init__( self, codeType='All' ):
      """__init__: creates a dictionary
       @type cmd: string
       @param cmd: takes in either all codes or a specific code, default is 'All'
      """
      self.dut = objDut

      self.ctrlL_Pat = re.compile(self.CTRLL_REGEX)


      self.p166 = dict(zip(self.PRE_CODE_VER_FORMAT, ['?',]*len(self.PRE_CODE_VER_FORMAT)))
      self.pf3 = dict(zip(self.PF3_FORMAT, ['?',]*len(self.PF3_FORMAT)))
      self.CODE_VER = self.SERVO_CODE = self.FIRMWARE_VER = '?'
      self.SPC_ID = 1
      if testSwitch.FE_0138491_231166_P_BYPASS_UNLK_FOR_TGTP_ON_DUT:
         self.AltF3_SAS_ID = None


   #---------------------------
   def updateF3Codes(self, packageOutput):

      if testSwitch.FE_0122186_354753_SUPPORT_FOR_SAS_REVISIONING and ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
         self.CODE_VER = packageOutput['ControllerFWRev']
      else:  # Interface is SATA
         self.CODE_VER = packageOutput['PackageVersion']
      self.FIRMWARE_VER = packageOutput['PackageVersion'][packageOutput['PackageVersion'].rfind('.')+1:]
      self.SERVO_CODE = packageOutput['SFWVersion']
      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
         if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
            # Can't get IV version from fw for SAS- use IV key filename
            from  PackageResolution import PackageDispatcher
            pd = PackageDispatcher(self.dut, codeType = 'OVL4')

            if testSwitch.virtualRun:
               self.IV_VER = ''
            else:
               self.IV_VER = pd.getFileName()
               if not self.IV_VER == None:
                  self.IV_VER = pd.getFileName().split('.')[0][-2:]
               else:
                  self.IV_VER = 'None'
         else:
            self.IV_VER = packageOutput['IVVersion']

      pDict = {'CODE_VER': self.CODE_VER,
               'FIRMWARE_VER': self.FIRMWARE_VER,
               'SERVO_CODE' : self.SERVO_CODE}

      if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
         self.dut.driveattr.pop('FIRMWARE_VER', None)
         pDict.pop('FIRMWARE_VER', None)
         DriveAttributes['FIRMWARE_VER'] = 'NONE'

         pDict['SCSI_FW_REV'] = DriveVars.get('PROD_REV', '?')

      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
         if not self.IV_VER == '' and not self.IV_VER == None:
            if testSwitch.FE_0175446_231166_P_IV_FILENAME_USAGE_SED:
               pDict.update({'IV_FILENAME':  self.IV_VER})
            else:
               pDict.update({'IV_SW_REV':  self.IV_VER})

      self.dut.driveattr.update(pDict)
      objMsg.printMsg("Attributes Saved for DCM Control")
      objMsg.printDict(pDict,objMsg.CMessLvl.IMPORTANT,colWidth=32)


   def syncF3DataSCSI(self):
      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.sptDiag:
         objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = 'force')
      packageOutput = {'PackageVersion': None, 'SFWVersion': None}
      import Process
      oProc = Process.CProcess()
      oProc.St({  'test_num': 514,
                  'prm_name': 'GetCodeInfo_514_prm',
                  'timeout': 30,
                  'spc_id': 12,
                  'ENABLE_VPD': 1,
                  'PAGE_CODE': 192,
                  'DblTablesToParse': ['P514_FIRMWARE_NUMBERS',]
                  })
      if testSwitch.virtualRun:
         ret = {'SCSI_FW_REV': 'F301', 'TMS_OR_SERVO_RAM_REV': '2009CB0A'}
      else:
         ret = self.dut.objSeq.SuprsDblObject['P514_FIRMWARE_NUMBERS'][0]

      packageOutput['ControllerFWRev'] = ret['SCSI_FW_REV']

      packageOutput['PackageVersion'] = ret['SCSI_FW_REV']
      packageOutput['SFWVersion'] = ret['TMS_OR_SERVO_RAM_REV']

      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
         if testSwitch.virtualRun:
            packageOutput['IVVersion'] = '0'

      if testSwitch.FE_0138491_231166_P_BYPASS_UNLK_FOR_TGTP_ON_DUT:
         oProc.St({  'test_num': 514,
                     'prm_name': 'GetCodeInfo_514_prm_alt',
                     'timeout': 30,
                     'spc_id': 12,
                     'PAGE_CODE': 0,
                     'DblTablesToParse': ['P514_STANDARD_INQUIRY',]
                     })
         if testSwitch.virtualRun:
            ret = {'VENDOR_ID': 'SEAGATE_', 'PRODUCT_ID': 'ST33000650SS____', 'SCSI_FW_REV': 'ZZ7L'}
         else:
            ret = self.dut.objSeq.SuprsDblObject['P514_STANDARD_INQUIRY'][0]

         self.AltF3_SAS_ID = ret['SCSI_FW_REV']

      self.updateF3Codes(packageOutput)


   #---------------------------
   def syncExtendedCommand(self):
      ##        Name              (offset,      length)
      cmdDef = {'PackageVersion': (0     , 31,  's'),
                'SFWVersion'    : (464   , 4,   's')}
      if testSwitch.FE_0122186_354753_SUPPORT_FOR_SAS_REVISIONING and ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
         cmdDef['ControllerFWRev'] = (0     , 31 , 's')
      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
         cmdDef['IVVersion'] = (496   , 5 , 's')

      packageOutput = {}
      buffNum = 11   #ATA feature bit 11
      mode = 5       #PIO Read

#CHOOI-18May17 OffSpec
      if testSwitch.OOS_Code_Enable == 1:  #CHOOI-02May14
         objPwrCtrl.powerCycle(5000,12000,10,30)
      else:
         ICmd.HardReset()
#      ICmd.HardReset()

      stat = ICmd.IdentifyDevice()
      ICmd.ClearBinBuff()


      dataBuffer = ICmd.PassThrough( mode, 0xEC, 0x2097, 0xa0, 0xdb, 0, buffNum, 0 )

      objMsg.printDict(dataBuffer)
      if dataBuffer['LLRET'] == -1:
         ScrCmds.raiseException(10609,"Extended Mode command 0xEC for page 11 extended ID data failed.")

      dataBuffer = ICmd.GetBuffer( 0x2, 0, 0x200 )
      if testSwitch.virtualRun:
         dummyData = {'PackageVersion':"CA09C2.SDM1.00059638.0Y00.03",
                      'SFWVersion': "2C03"}
         if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
            dummyData['IVVersion']  = ""
         if testSwitch.FE_0122186_354753_SUPPORT_FOR_SAS_REVISIONING:
            dummyData['ControllerFWRev']  = "01081639"
         data = ['\x00',]*512
         for key, vals in cmdDef.items():
            data[vals[0]:vals[0]+vals[1]] = struct.pack("%d%s" % (vals[1],vals[2]), dummyData[key])
         dataBuffer['DATA'] = ''.join(data)
         objMsg.printBin(dataBuffer['DATA'],16)

      if DEBUG > 0:
         objMsg.printMsg(str(dataBuffer))
         objMsg.printMsg("Buffer Number %d" % buffNum)
         objMsg.printMsg("BINARY")
         objMsg.printBin(dataBuffer['DATA'],16)
         objMsg.printMsg("ASCII_REP")
         objMsg.printBinAscii(dataBuffer['DATA'],16)

      for key in cmdDef.keys():
         pckData = dataBuffer['DATA'][cmdDef[key][0]:cmdDef[key][0]+cmdDef[key][1]]

         try:
            packageOutput[key] = objMsg.cleanASCII(''.join(struct.unpack(cmdDef[key][2]*cmdDef[key][1],pckData)))
            packageOutput[key] = packageOutput[key].strip()
         except:
            objMsg.printMsg(traceback.format_exc())
            objMsg.printMsg("Failure Info: Buffer[%s]; Format[%s]" % (pckData,cmdDef[key][2]*cmdDef[key][1]))

      self.updateF3Codes(packageOutput)


   #---------------------------
   def ChkUSBReconfig(self):
      attr = self.dut.driveattr.get('USB_DRIVE', 'NONE')
      objMsg.printMsg("ChkUSBReconfig USB_DRIVE=%s" % attr)

      if attr == "NONUSB" or attr == 'NONE':
         return   # reconfig always allowed for nonUSB

      self.ChkUSB()
      if self.dut.driveattr['USB_INTF'] == 'N':
         ScrCmds.raiseException(14735, "USB to NONUSB reconfig not allowed")

   #---------------------------
   def ChkUSB(self):
      self.dut.driveattr['USB_INTF'] = 'N'
      if getattr(TP, 'USB_IDENTIFIER', '') == '':    # if USB_IDENTIFIER not specified, we assume it's never USB so that we don't have to issue CTRL_L command
         return

      self.syncF3Code()

      if testSwitch.FE_0122186_354753_SUPPORT_FOR_SAS_REVISIONING and ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
         CodeVersion = theCodeVersion.CODE_VER
      else:
         try:
            CodeVersion = string.split(theCodeVersion.CODE_VER,'.')[1].strip()[:2]
         except:
            objMsg.printMsg("Failed to read CODE_VER traceback=%s" % traceback.format_exc())
            if testSwitch.COTTONWOOD:
               theCodeVersion.CODE_VER = "CW0000.SSSS.AAAAAA.0000"
               CodeVersion = string.split(theCodeVersion.CODE_VER,'.')[1].strip()[:2]
               objMsg.printMsg("COTTONWOOD - forced CodeVersion=%s" % CodeVersion)
               return
            else:
               throw

      if CodeVersion in getattr(TP, 'USB_IDENTIFIER', 'BS'):  # USB code detected
         self.dut.driveattr['USB_INTF'] = 'Y'

      sptCmds.enableESLIP(printResult = False)
      objMsg.printMsg("ChkUSB CodeVersion=%s USB_INTF=%s" % (CodeVersion, self.dut.driveattr['USB_INTF']))

   #---------------------------
   def syncF3Code(self):
      #F3 code is detected so lets get the revs

      if testSwitch.NoIO:
         objMsg.printMsg("NoIO Force syncCTRL_L")
         self.syncCTRL_L()
      elif testSwitch.BF_0145392_231166_P_CHECK_COMM_MODE_SYNCSF3_SATA:
         if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.intBase and  \
            ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SATA_ID', []) or self.dut.drvIntf == 'SATA' ) and not \
            getattr(objPwrCtrl, 'certOper', False):
            self.syncExtendedCommand()

         elif self.dut.sptActive.getMode() == self.dut.sptActive.availModes.intBase and objRimType.IOInitRiser() and ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ) :
            self.syncF3DataSCSI() #for SAS/FC
         else:
            self.syncCTRL_L()
      else:
         if (self.dut.sptActive.getMode() == self.dut.sptActive.availModes.intBase and objRimType.CPCRiser()) or \
            ( ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SATA_ID', []) or self.dut.drvIntf == 'SATA' ) and objRimType.IOInitRiser()) and \
            self.dut.sptActive.getMode() == self.dut.sptActive.availModes.intBase:
            self.syncExtendedCommand()

         elif self.dut.sptActive.getMode() == self.dut.sptActive.availModes.intBase and objRimType.IOInitRiser() and ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ) :
            self.syncF3DataSCSI() #for SAS/FC
         else:
            self.syncCTRL_L()


   #---------------------------
   def updateCodeRevisions(self):

#CHOOI-27Jan15 OffSpec
      if testSwitch.OOS_Code_Enable == 1:  #CHOOI-02May14
         self.syncExtendedCommand()
      elif self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.sptDiag, self.dut.sptActive.availModes.intBase]:
         self.syncF3Code()
         objDut.f3Active = 1 
      else:
         #MCT is detected so let's get SF3 revs
         self.syncP166()
         objDut.f3Active = 0

   #---------------------------
   def updatePF3Code(self):
      try:
         from Constants import PF3_Changlist, PF3_Branch, PFE_RELEASE_NOTES, PF3_BUILD_TARGET
      except:
         objMsg.printMsg(traceback.format_exc())
         PF3_Changlist = "?"
         PF3_Branch    = "?"
         PFE_RELEASE_NOTES = "Non-Official Release"
         if testSwitch.FE_0118796_231166_OUTPUT_PF3_BUILD_TARGET:
            PF3_BUILD_TARGET = "?"

      headerID = "*" * 20
      objMsg.printMsg(headerID + " PF3 Release Code info" + headerID, objMsg.CMessLvl.IMPORTANT)
      objMsg.printMsg("Branch Location:\t%s" % PF3_Branch,objMsg.CMessLvl.IMPORTANT)
      objMsg.printMsg("CL:\t%s" % PF3_Changlist,objMsg.CMessLvl.IMPORTANT)
      if testSwitch.FE_0118796_231166_OUTPUT_PF3_BUILD_TARGET:
         objMsg.printMsg("Build Target:\t%s" % PF3_BUILD_TARGET,objMsg.CMessLvl.IMPORTANT)
      objMsg.printMsg("Release Notes:\t%s" % PFE_RELEASE_NOTES,objMsg.CMessLvl.IMPORTANT)
      objMsg.printMsg("*" * (20+10+30), objMsg.CMessLvl.DEBUG)

      if PF3_Branch.find('/') != -1:
         self.pf3['BRANCH'] = PF3_Branch.split('/')[-1]
      else:
         self.pf3['BRANCH'] = '?'
      self.pf3['CL'] = PF3_Changlist
      self.pf3['PACKAGE'] = PFE_RELEASE_NOTES
      self.__updatePF3Attr()

   #---------------------------
   def __updatePF3Attr(self):
      for key in self.PF3_FORMAT:
         attrKey = 'PF3_%s' % key
         self.dut.driveattr[attrKey] = self.pf3.get(key,'?')


   #---------------------------
   def syncP166(self):
      mFSO = CFSO()
      mFSO.reportFWInfo(spc_id = self.SPC_ID)
      self.SPC_ID += 1
      self.SERVO_CODE = self.dut.driveattr['SERVO_INFO'][0:4]
      objMsg.printMsg("syncP166, SERVO_CODE: %s" % self.SERVO_CODE )

      try:
         codeInfo = self.dut.dblData.Tables('P166_SELFTEST_REV').tableDataObj()
         self.p166.update({'SFCL': str(codeInfo[-1]['CHANGE_LIST']), 'PROCCL': CN})
         objMsg.printMsg(self.dut.dblData.Tables('P166_SELFTEST_REV'))
      except:

         #Delete the old table- ignore if we can't
         try:self.dut.dblData.delTable('P166_SELFTEST_REV')
         except:pass

         codeInfo = self.dut.dblData.Tables('P166_SELFTEST_PACKAGENAME').tableDataObj()
         self.p166.update({'SFCL': str(codeInfo[-1]['PACKAGE_NAME']), 'PROCCL': str(codeInfo[-1]['CHANGE_LIST'])})
         objMsg.printMsg(self.dut.dblData.Tables('P166_SELFTEST_PACKAGENAME'))

      self.__updateSF3Attr()

   def __updateSF3Attr(self):
      self.dut.driveattr['PRE_CODE_VER'] = ".".join([self.p166.get(key,'') for key in self.PRE_CODE_VER_FORMAT])


   #---------------------------
   def syncCTRL_L(self):
      ctrlLRetries = 4

      sptCmds.enableDiags(10)

      objMsg.printMsg("sending CTRL_L command")
      res = sptCmds.sendDiagCmd(CTRL_L, altPattern = self.ctrlL_Pat,stopOnError = True, Ptype = 'PChar', DiagErrorsToIgnore = 'Invalid Diag Cmd', raiseException = 0)

      if testSwitch.BF_0135400_231166_FIX_CTRL_L_ESLIP_TRANSITION:
         sptCmds.enableESLIP()
      if testSwitch.virtualRun:
         res = \
            """
            YarraR.SATA.Mule.LuxorM93.OEM.5K4
            Product FamilyId: 5F, MemberId: 0A
            HDA SN: W0V00KL3, RPM: 5408, Wedges: 100, Heads: 2, OrigHeads: 0, Lbas: 000007470C08, PreampType: D0 45
            Bits/Symbol: C, Symbols/UserSector: BE7, Symbols/SystemSector: 195
            PCBA SN: 0000S2245WLJ, Controller: LUXORM93_1_1(FFFF)(FF-FF-FF-FF), Channel: MARVELL_9311, PowerAsic: MCKINLEY MOBILE PLUS Rev 15, BufferBytes: 1000000
            Package Version: YR028A.SDM1.BA0008., Package P/N: ---------, Package Global ID: 00080603,
            Package Build Date: 04/03/2012, Package Build Time: 19:22:12, Package CFW Version: YR02.SDM1.00441373.00080603,
            Package SFW1 Version: A836, Package SFW2 Version: ----, Package SFW3 Version: ----, Package SFW4 Version: ----
            Controller FW Rev: 00080001, CustomerRel: 0001, Changelist: 00441373, ProdType: YR02.SDM1, Date: 04/03/2012, Time: 192212, UserId: 00080603
            Servo FW Rev: 4ADA
            TCG IV Version: n/a
            Package BPN: 0
            RAP FW Implementation Key: 16, Format Rev: 5D02, Contents Rev: 80 04 04 05
            Features:
            - Quadradic Equation AFH enabled
            - VBAR with adjustable zone boundaries enabled
            - Volume Based Sparing enabled
            - IOEDC enabled
            - IOECC enabled
            - DERP Read Retries enabled v. 4.0.00.0000000000000000
            - LTTC-UDR2 enabled 
            - SuperParity disabled
            """

      patMat = self.ctrlL_Pat.search(res)
      if patMat == None:
         objMsg.printMsg(res, objMsg.CMessLvl.VERBOSEDEBUG)
         ScrCmds.raiseException(11044,{"ERR":'Failed to parse Code Revision',"DATA":res})
      else:
         codeDict = patMat.groupdict()
         self.updateF3Codes(codeDict)
#---------------------------------------------------------------------------------------------------#

###########################################################################################################
###########################################################################################################

theCodeVersion = BaseCodeVersionInfo()

###########################################################################################################
###########################################################################################################

if __name__ == '__main__':
   theCodeVersion.updateCodeRevisions()
