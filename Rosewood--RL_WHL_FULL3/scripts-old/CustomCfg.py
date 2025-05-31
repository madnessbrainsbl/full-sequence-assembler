#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2011, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: This is the main class to implement the Customer Configuration functionality.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/16 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CustomCfg.py $
# $Revision: #4 $
# $DateTime: 2016/12/16 00:51:36 $
# $Author: hengngi.yeo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CustomCfg.py#4 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from Test_Switches import testSwitch
from Process import CProcess
import FSO
from Drive import objDut
import ScrCmds
import MessageHandler as objMsg
import time, string, struct, re
from Exceptions import CRaiseException, BypassCustUniqueTest
from Rim import objRimType, theRim
from PIFHandler import DTDFileCreator, CPIFHandler
from CTMX import CTMX
from ICmdFactory import ICmd
import Utility
import types
import PIF
from PowerControl import objPwrCtrl
from IntfClass import CInterface, CIdentifyDevice
import CommitServices

DEBUG = 0

class WorkWeek:
   #----Initialize--------------#
   def __init__( self ):
      self.YYWW = ''
   #-------------------------
   def getWeekPoint( self ):
      """Compute for the Week Point"""
      if testSwitch.virtualRun:
         timeNow=time.mktime(time.strptime("1 1 2010", "%d %m %Y"))
      else:
         timeNow = time.time()
      timeLst = time.localtime( timeNow )
      wkDayPoint = 3
      timeWeekPoint = timeNow + ( wkDayPoint - timeLst[6] ) *3600*24
      weekPoint = time.localtime( timeWeekPoint )
      return weekPoint
   #-------------------------
   def getWorkWk( self, timeLst ):
      """return the work week"""
      ww = 1
      tmp = ( ( timeLst[7]-1 )/7 ) + 1
      ww = '%02d'%tmp
      return ww
   #-------------------------
   def GetWorkWeek( self ):
      """This is our method which users will call to return the yyww"""
      self.YYWW = ''
      tlist = self.getWeekPoint()
      self.YYWW = str( tlist[0] )[2:]
      self.YYWW += self.getWorkWk( tlist )
      return self.YYWW


class CCustomCfg(CProcess):
   def __init__(self):
      CProcess.__init__(self)
      self.dut = objDut

      if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
         ModuleFileName = "base_Motor"
      else:
         ModuleFileName = "base_SerialTest"

      # table of CAID functions
      self.dFuncs = {
                     'CAID_NOTFOUND'      : self.error,                     # didn't have an ID entry
                     'DELL_CONFIG_CODE'   : self.dellConfigCode,            # DellConfig Code
                     'DELL_DEVICE_ID'     : self.Dell_DeviceID,
                     'DISABLE_LACHECK'    : self.DisableLaCheck,
                     'HDA_SERIAL_NUM'     : self.getHDASN,
                     'IBM_SER_NUM'        : self.setIBMSN,                  # Returns the site numeric code
                     'RESET_LOG_PGS'      : self.ResetLogPages,
                     'RESET_MODE_PGS'     : self.ResetModePages,
                     'SMARTREADDATA'      : self.SMARTReadData,
                     'WRITE_DELL_PPID'    : self.writeDellPPID,             # DellPPID
                     'LENOVO_8S'          : self.Lenovo_8S_SN,              # Lenovo8S
                     'WRITE_SUN_MODEL'    : self.writeSunModelNum,          # Write sun model number to attr
                     'WRITE_WORK_DATE'    : self.writeWorkDate,             # Write WorkDate to attr
                     'WRITECAPHDCNT'      : self.writeHD_COUNT,             # write HD count to CAP
                     'WRITECAPPFMID'      : self.writePFM_ID,               # write PFM to CAP
                     'WRITECAPSN'         : self.writeCAPHDASN,             # write HDA SN to CAP
                     'WRITECAPWWN'        : self.writeWWN,                  # write WWN
                     'WRITECCDATA'        : self.writeCC_DATA,              # write CC data
                     }

      self.custScreens = {
                     'APPLE_ATI'          : "CustomerScreens.CAPPLEATI",
                     'APPLE_SCREENS'      : "CustomerScreens.CAppleScreen",
                     'APPLETHREAD'        : "CustomerScreens.CBluenunScanMulti",
                     'AVSCAN'             : "CustomerScreens.CAVScan",
                     'BLUENUN'            : "base_RssScreens.CSP_Apple",
                     'BLUENUN_SLIDE'      : "CustomerScreens.CBluenunSlide",
                     'BUTTERFLY'          : "CustomerScreens.CMuskieButterFly",
                     'CCT'                : "CustomerScreens.CCCTTest",
                     'KT_MQMV2'           : "CustomerScreens.CMuskieKTMQMV2",
                     'KT_RWK_MQM'         : "CustomerScreens.CMuskieRWKMQM",
                     'HP_MEAT_GRINDER'    : "CustomerScreens.CHPMeatGrinderScreen",
                     'HP_SCREEN'          : "CustomerScreens.CHPQCusTest",
                     'LENOVO_SCREEN'      : "CustomerScreens.CLenovoCusTest",
                     'NETAPP_SCREEN'      : "CustomerScreens.CNETAPP",
                     'NETAPP_WRTSAME'     : "CustomerScreens.CNETAPPWriteSame",
                     'NETAPP_MANTARAY'    : "CustomerScreens.CNETAPPMantaRay",
                     'RAND_IOPS'          : "CustomerScreens.CIopsScreen",
                     'SHARP_SCREEN'       : "CustomerScreens.CSharpTest",
                     'SONY_SCREEN'        : "CustomerScreens.CSonyScreenTest",
                     'SONY_FT2'           : "CustomerScreens.CSony_FT2Test",
                     'SUSTAIN_XFER_RATE'  : "CustomerScreens.CSTRTest",
                     'MICROSOFT_CACTUS'   : "CustomerScreens.CMicrosoftCactusTest",
                     }

      self.custContent = {
                     'AMPS_CHECK'                   : "base_IntfTest.CAMPSCheck",
                     'ATA_1.5SPEED'                 : "CustomerContent.CATASignalSpeed_1_5",
                     'ATA_3.0SPEED'                 : "CustomerContent.CATASignalSpeed_3_0",
                     'CHANGE_DEF'                   : "CustomerContent.CChangeDef",
                     'CHECK_2M'                     : "base_IntfTest.C2MZeroCheck",
                     'CHECK_20M'                    : "base_IntfTest.C20MZeroCheck",
                     'CHECK_400K'                   : "base_IntfTest.C400KZeroCheck",
                     'CHECKMERGEGLIST'              : "base_IntfTest.CCheckMergeGList",
                     'CFULL_PACK_DIAG_BER'          : "base_RssScreens.CFull_Pack_Diag_BER",
                     'DISPLAY_GLIST'                : "base_IntfTest.CDisplay_G_list",
                     'DRV_PAIRING'                  : "CustomerContent.CDrive_Pairing",
                     'KWAI'                         : "CustomerContent.CKwaiPrep",
                     'LOW_SPIN_CURRENT'             : "%s.CLowCurrentSpinUp" %ModuleFileName,
                     'NORMAL_SPIN_CURRENT'          : "%s.CNormalCurrentSpinUp" %ModuleFileName,
                     'POIS'                         : "CustomerContent.CPois",
                     'PACK_WRITE'                   : "base_IntfTest.CPackWrite",
                     'PWR_ON_IN_STDBY'              : "CustomerContent.CPois",
                     'POIS_DISABLED'                : "CustomerContent.CPois_Disable",
                     'RLISTCHECK'                   : "base_IntfTest.CCheckMergeGList_Apple",
                     'RESET_SMART'                  : "base_IntfTest.CClearSMART",
                     'RESET_DOS'                    : "base_IntfTest.CClearDOS",
                     'SECURED BASE (SD AND D)'      : "CustomerContent.CTCGPrep",
                     'SET_MP8_DISC'                 : "self.SetSasDiscBit",
                     'SET_WCE_OFF'                  : "self.SetWCEBitOff",
                     'SMART_DST_LONG'               : "base_IntfTest.CSmartDSTLong",
                     'TCG'                          : "CustomerContent.CTCGPrep",
                     'TCG OPAL 2 SED'               : "CustomerContent.CTCGPrep",
                     'Z_PI_FORMAT'                  : "CustomerContent.CPI_Format",
                     'ZERO_1M'                      : "base_IntfTest.C1MZeros",
                     'ZERO_2M'                      : "base_IntfTest.C2MZeros",
                     'ZERO_20M'                     : "base_IntfTest.C20MZeros",
                     'ZERO_400K'                    : "base_IntfTest.C400KZeros",
                     'ZERO_PATTERN'                 : "base_IntfTest.CZeroPattern",
                     'ZERO_VALIDATE'                : "base_IntfTest.CZeroValidate",
                     'ZERO_CHECK'                   : "base_IntfTest.CFullZeroCheck",
                     }

      if testSwitch.FE_0152759_231166_P_ADD_ROBUST_PN_SN_SEARCH_AND_VALIDATION:
         self.custContent['VALIDATE_SN']  = self.validateFIS_HDA_SN

#CHOOI-19May17 OffSpec
#       if testSwitch.FE_0152007_357260_P_DCM_ATTRIBUTE_VALIDATION:
#          self.custAttrHandlers = {
#                         'BSNS_SEGMENT'       : self.autoValidateDCMAttrString,
#                         'TIME_TO_READY'      : self.autoValidateDCMAttrFloat,
#                         'SECURITY_TYPE'      : self.autoValidateDCMAttrString,
#                         'WWN'                : self.autoValidateWWNAttr,
#                         'ZERO_PTRN_RQMT'     : self.autoValidateZeroPattern,
#                         #'FDE_TYPE'           : self.autoValidateDCMAttrString,
#                         'USER_LBA_COUNT'     : self.autoValidateDCMAttrLBAs,
#                         }
# 
#          if testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
#             self.custAttrHandlers['ZERO_G_SENSOR'] = self.autoValidateZGS
#          if testSwitch.FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS:
#             self.custAttrHandlers.update({
#                         'DRV_MODEL_NUM'      : self.autoValidateDCMAttrString,
#                         'CUST_MODEL_NUM'     : self.autoValidateDCMAttrString,
#                         'CUST_MODEL_NUM2'    : self.autoValidateDCMAttrString,
#                         })
#             if testSwitch.BF_0157043_231166_P_DISABLE_DRV_MODEL_NUM_VALIDATION:
#                self.custAttrHandlers.pop('DRV_MODEL_NUM',0)
# 
#          self.custAttrHandlers.update({
#                         'CUST_TESTNAME'      : self.autoValidateDCMAttrString,
#                         })
# 
#          if testSwitch.WA_0159243_231166_P_FORCE_SET_FDE_TYPE_ATTR:
#              self.custAttrHandlers.update({
#                 'FDE_TYPE'           : self.autoValidateDCMAttrString,
#                 'SECURITY_TYPE'      : self.autoValidateDCMAttrString,})
# 
#       else:
#          self.custAttrHandlers = {
#                         }
      self.custAttrHandlers = {
                        }

      self.dcmScreens = {
                             'AP1' : 'APPLE_ATI',
                             'AP2' : 'BLUENUN',
                             'AP3' : 'BLUENUN_SLIDE',
                             'AP4' : 'APPLE_SCREENS',
                             'AP5' : 'APPLETHREAD',
                             'DE1' : 'WRITE_DELL_PPID',
                             'DL1' : 'DELL_DEVICE_ID',
                             'DV1' : 'AVSCAN',
                             'DV2' : 'DRV_PAIRING',
                             'DV3' : 'SMART_DST_LONG',
                             'LV1' : 'LENOVO_8S',
                             'MS1' : 'SUSTAIN_XFER_RATE',
                             'NT1' : 'NETAPP_MANTARAY',
                             'SC1' : 'LOW_SPIN_CURRENT',
                             'SD1' : 'ATA_1.5SPEED',
                             'SD2' : 'ATA_3.0SPEED',
                             'SD3' : 'WRITE_XFER',
                             'SU1' : 'WRITE_SUN_MODEL',
                             'SY1' : 'SONY_SCREEN',
                             #'SY1' : 'SONY_FT2',
                           }

      if testSwitch.WA_0168153_007955_USE_AP2_WITH_BLUENUNSLIDE:
         self.dcmScreens.pop('AP3')
         self.dcmScreens.update({'AP2' : 'BLUENUN_SLIDE'})

      self.dcmContents = {
                           'SECURITY_TYPE' : ['3DES DRIVE PAIRING SECURITY','ECHOSTAR ST10','SAGEM ST10', 'DVR PLATFORM',
                                              'FDE.2','FDE.3','FDE.3.5','FDE.4','NEARLINE SECURITY', 'SEACOS FDE',
                                              'TCG OPAL SSC 1.0 FDE', 'TCG ENTERPRISE SSC 1.0 FDE', 'TCG', 'DRV_PAIRING',
                                              'TCG OPAL 2 SED', 'SECURED BASE (SD AND D)'],
                           'FDE_TYPE'      : ['FDE BASE','OEM USB ENABLED','OEM USB ENABLED','INTERNAL USB ENABLED',
                                              'ATA ONLY', 'FDE BASE FIPS 140-2', 'OEM USB ENABLED FIPS 140-2', 'INTERNAL USB ENABLED FIPS 140-2',
                                              'ATA ONLY FIP140-2','KWAI'],
                           'POWER_ON_TYPE' : ['PWR_ON_IN_STDBY', 'POIS', 'POIS_DISABLED'],
                           'ZERO_PTRN_RQMT': {
                                              '10':['ZERO_400K','CHECK_400K'],
                                              '13':['ZERO_2M','CHECK_2M'],
                                              '15':['ZERO_20M','CHECK_20M'],
                                              '20':['PACK_WRITE', 'ZERO_CHECK'],
                                             },
                           'ZERO_PTRN_BEFORE' : [],                                  # Support extra tests before and
                           'ZERO_PTRN_AFTER'  : ['SMART_DST_LONG', 'RLISTCHECK',],   # after zero pattern check
                         }

      if testSwitch.NoIO:
         import SDI_Test
         self.custScreens.update({
                     'AVSCAN'             : SDI_Test.CAVScan,
                     #'BLUENUN'            : SDI_Test.CBluenunScanAuto, #replaced by Apple throughput test
                     'SONY_SCREEN'        : SDI_Test.CSonyScreenTest,
                     })

   def RunCustCfg(self, screenCls, runme, *args):
      self.dut.ctmxState.IsCustCfg = True
      ctmx = CTMX('STATE', '_' + screenCls)
      try:
         if screenCls in getattr(TP, 'Gantry_Ins_Prot_Screens', []):
            objMsg.printMsg('DisableCell for: %s' % screenCls)
            RequestService('DisableCell')

         runme(*args)
      finally:
         ctmx.endStamp()
         ctmx.writeDbLog()

         if screenCls in getattr(TP, 'Gantry_Ins_Prot_Screens', []):
            objMsg.printMsg('EnableCell for: %s' % screenCls)
            RequestService('EnableCell')

   def getCustomFunInst(self, function, *args, **kwargs):
      if function.split('.')[0] != 'self':
         exec('import ' + function.split('.')[0])
      functionInst = eval(function)(*args, **kwargs)

      return functionInst

   def ExecCAID(self,dCAID):
      sID = dCAID.get('ID','CAID_NOTFOUND')
      objMsg.printMsg('='*80)
      objMsg.printMsg( 'Executing CAID: %s for info: %s' %(dCAID.get('ID'),dCAID.get('Info')) )
      if self.dFuncs.has_key(sID):
         self.RunCustCfg(dCAID.get('ID'), self.dFuncs[sID], dCAID)
      else:
         self.error(dCAID)


   ######## CIF handlers

   # Main routine for users to execute all the customer config setups
   def ProcessCustomCfg(self,dCfg):
      self.non_dcm_screens = ''
      self.dcm_screens =  CPIFHandler().getDCMScreens()        # determine DCM screens
      if CommitServices.isTierPN( self.dut.partNum ):
         objMsg.printMsg("Don't run lCAIDS as tier drive.")
         return

      lCAIDS = dCfg.get('lCAIDS', [])
      #lCAIDS.append({'ID':'WRITE_WORK_DATE','Size':0,'Offset':0,})
      if testSwitch.FE_0198029_231166_P_WWN_BEG_AND_END:
         lCAIDS.append({'ID':'WRITECAPWWN','Size':0,'Offset':0,})

      if lCAIDS:
         for dCurCAID in lCAIDS:
            if not dCurCAID.get('ID',None) in self.dut.CustomCfgTestDone:
               self.ExecCAID(dCurCAID)
               self.dut.CustomCfgTestDone.append(dCurCAID.get('ID',None))
               self.dut.objData.update({'CustomCfgTestDone':self.dut.CustomCfgTestDone})
            if dCurCAID.get('ID',None) in ['WRITE_DELL_PPID','WRITE_SUN_MODEL']:
               self.saveScreenName(dCurCAID.get('ID',None))

            self.dut.objData.update({'DriveAttributes':self.dut.driveattr})

   def ProcessCustomScreens(self,dCfg):
      """These are states that implement screens"""

      if testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM:
         screens = dCfg.get('Screens',[])
         rwkMQM = self.SelectRWKMQM()
         for screenCls in screens:
            if screenCls in self.dut.CustomCfgTestDone:
               objMsg.printMsg('Not executing Screens: %s after powerloss recovery' % screenCls )
            elif screenCls == 'NETAPP_SCREEN_RWK' and DriveAttributes.get('PRIME','N') != 'N':
               objMsg.printMsg('Skip executing NETAPP_SCREEN_RWK since Prime drive detect')
            elif screenCls == 'KT_RWK_MQM' and rwkMQM == 'N':
               objMsg.printMsg('Skip executing KT_RWK_MQM since criteria of rework MQM detect')
            else:
               objMsg.printMsg('='*80)
               objMsg.printMsg( 'Executing Screens: %s' %screenCls )
               if screenCls in self.custScreens:
                  stateInst = self.getCustomFunInst(self.custScreens[screenCls], self.dut, params={})
                  self.RunCustCfg(screenCls, stateInst.run)
               # Handle 'DE1' and 'SU1' tests
               elif screenCls in self.dFuncs:
                  self.RunCustCfg(screenCls, self.dFuncs[screenCls], dCfg)
               elif testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM:
                  # Handle DCM screens placed in self.custContent. Examples are 'ATA_1.5SPEED' (SD1),
                  #'ATA_3.0SPEED' (SD2), and 'DRV_PAIRING' (DV2)
                  if screenCls in self.custContent:
                     stateInst = self.getCustomFunInst(self.custContent[screenCls], self.dut, params={})
                     self.RunCustCfg(screenCls, stateInst.run)
                  else:
                     objMsg.printMsg( 'Warning!!! Unsupported Screens: %s' %screenCls )

               self.saveScreenName (screenCls)
               self.dut.CustomCfgTestDone.append(screenCls)
               self.dut.objData.update({'CustomCfgTestDone':self.dut.CustomCfgTestDone, 'DriveAttributes':self.dut.driveattr})

            objMsg.printMsg('self.dut.CustomCfgTestDone: %s' % self.dut.CustomCfgTestDone)
      else:
         screens = dCfg.get('Screens',[])
         rwkMQM = self.SelectRWKMQM()
         for screenCls in screens:
            if screenCls == 'NETAPP_SCREEN_RWK' and DriveAttributes.get('PRIME','N') != 'N':
               objMsg.printMsg('Skip executing NETAPP_SCREEN_RWK since Prime drive detect')
            elif screenCls == 'KT_RWK_MQM' and rwkMQM == 'N':
               objMsg.printMsg('Skip executing KT_RWK_MQM since criteria of rework MQM detect')
            else:
               objMsg.printMsg('='*80)
               objMsg.printMsg( 'Executing Screens: %s' %screenCls )
               stateInst = self.getCustomFunInst(self.custScreens[screenCls], self.dut, params={})
               stateInst.run()
      if DEBUG:
         objMsg.printMsg("Customer Screens performed: %s" % (self.dut.driveattr['CUST_TESTNAME'],))

   def SelectRWKMQM(self):
      from ProcessControl import ReworkMQM

      partNum = DriveAttributes['PART_NUM']
      sbr = DriveAttributes['SUB_BUILD_GROUP']
      prime = DriveAttributes.get('PRIME', 'N')
      clrmExitDate = DriveAttributes.get('CLRM_EXIT_DATE', 'NONE')
      drvRwkComp = DriveAttributes.get('DRV_RWK_COMP', 'NONE')
      if testSwitch.FE_0162925_409401_P_ADD_MORE_ATTR_TO_CTRL_RWM_MQM:
         mediaRecycle = DriveAttributes.get('MEDIA_RECYCLE', 'NONE')
         linenum = DriveAttributes.get('LINE_NUM', 'NONE')
      if testSwitch.FE_0164090_409401_P_ADD_CRX_CNT_ATTR_TO_CTRL_RWK_MQM:
         crxcnt = DriveAttributes.get('CRX_CNT', 'NONE')

      if testSwitch.FE_0162925_409401_P_ADD_MORE_ATTR_TO_CTRL_RWM_MQM:
         rwkMQMAttrList = {'PN':partNum, 'PRIME':prime, 'SBR':sbr, 'CLRM_EXIT_DATE':clrmExitDate,'LINE_NUM':linenum, 'DRV_RWK_COMP':drvRwkComp, 'MEDIA_RECYCLE':mediaRecycle}
      else:
         rwkMQMAttrList = {'PN':partNum, 'PRIME':prime, 'SBR':sbr, 'CLRM_EXIT_DATE':clrmExitDate,'DRV_RWK_COMP':drvRwkComp}
      if testSwitch.FE_0164090_409401_P_ADD_CRX_CNT_ATTR_TO_CTRL_RWK_MQM:
         rwkMQMAttrList.update({'CRX_CNT':crxcnt})
      keyList = ReworkMQM.keys()
      keyList.sort()

      run_rwkMQM = False
      for key in keyList:
         for attribute in ReworkMQM[key]:
            if ReworkMQM[key][attribute] == '*':
               run_rwkMQM = True
            elif attribute == 'MEDIA_RECYCLE':
               evenChk = [rwkMQMAttrList['MEDIA_RECYCLE'][i:i+1] for i in range(1, len(rwkMQMAttrList['MEDIA_RECYCLE']), 2)]
               if ReworkMQM[key][attribute] in evenChk:
                  run_rwkMQM = True
               else:
                  run_rwkMQM = False
                  break
            elif ReworkMQM[key][attribute] == rwkMQMAttrList[attribute]:
               run_rwkMQM = True
            else:
               run_rwkMQM = False
               break
         if run_rwkMQM == True:
            objMsg.printMsg('Rework MQM Selected for "%s" criteria.'%key)
            if testSwitch.FE_0162716_395340_P_MQM_REWORK_FOR_PRE_ODT_SS:
               self.dut.driveattr['MQM_RW']  = 'Y'
            return 'Y'
         else:
            continue
      if run_rwkMQM == False:
         objMsg.printMsg('Rework MQM Not Selected for all criteria.')
         if testSwitch.FE_0162716_395340_P_MQM_REWORK_FOR_PRE_ODT_SS:
            self.dut.driveattr['MQM_RW']  = 'N'
         return 'N'

   def ProcessCustomContent(self,dCfg):
      """These are states that implement screens"""

      content = dCfg.get('Content',[])

      if str(self.dut.driveConfigAttrs.get('SECURITY_TYPE',(0,None))[1]).rstrip() == 'SECURED BASE (SD AND D)':
         testSwitch.IS_SDnD = 0

      content = ['PACK_WRITE', 'ZERO_CHECK']
      objMsg.printMsg("Content to execute: %s" % (content,))

      for contCls in content:
         objMsg.printMsg('='*80)

         if testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM:
            if (contCls in self.dut.CustomCfgTestDone) and (contCls not in self.dcm_screens):
               objMsg.printMsg('Not executing Content: %s after powerloss recovery' % contCls )
            else:
               objMsg.printMsg( 'Executing Content: %s' % contCls )
               stateInst = self.getCustomFunInst(self.custContent[contCls], self.dut, params={})
               self.RunCustCfg(contCls, stateInst.run)
               self.saveScreenName (contCls) # Update CUST_TESTNAME for DCM 'Screens' moved to 'Content' (i.e SMART_DST_LONG)
               self.dut.CustomCfgTestDone.append(contCls)
               self.dut.objData.update({'CustomCfgTestDone':self.dut.CustomCfgTestDone, 'DriveAttributes':self.dut.driveattr})

            objMsg.printMsg('self.dut.CustomCfgTestDone: %s' % self.dut.CustomCfgTestDone)
         else:
            objMsg.printMsg( 'Executing Content: %s' % contCls )
            if type(self.custContent[contCls]) == types.ClassType or not testSwitch.FE_0134690_231166_ALLOW_DCAID_IN_CONTENT:
               stateInst = self.getCustomFunInst(self.custContent[contCls], self.dut, params={})
               stateInst.run()
            else:
               self.custContent[contCls]()

   def screenCode(self, testname):
      '''Returns three-character test code based on testname.'''
      return [k for k,v in self.dcmScreens.iteritems() if v==testname][0]

   def contentCode(self, testname):
      return [k for k,v in self.dcmContents.iteritems() if v==testname][0]

   def getScreenAttrName(self, code):
      for attrName in [ 'CUST_TESTNAME', 'CUST_TESTNAME_2', 'CUST_TESTNAME_3' ]:
         if code in self.dut.driveConfigAttrs.get(attrName,('=',''))[1]:
            return attrName
      return 'INVALID_CUST_TEST'

   def getCustTestSupVal(self, attrName = 'CUST_TESTSUP'):
      return Utility.CUtility.stripBrackets( self.dut.driveConfigAttrs.get(attrName,('=',''))[1] )

   def getCustTestSupVal2(self):
      return self.getCustTestSupVal('CUST_TESTSUP_2')

   def getCustTestSupVal3(self):
      return self.getCustTestSupVal('CUST_TESTSUP_3')

   def saveScreenName(self, screenCls):
      ''' Save screen names to drive attribute.'''
      combined = self.dcmScreens.items()
      for code, codename in combined:
         if screenCls in codename:
            if not testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM:
               # Only record PIF screens in CUST_TESTNAME if DCM is not used
               self.dut.driveattr['CUST_TESTNAME'] = self.dut.cust_testname(code)
            else:
               if screenCls in self.dcm_screens:
                  if testSwitch.FE_0193449_231166_P_DL1_SUPPORT or testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
                     attrName = self.getScreenAttrName(self.screenCode(screenCls))
                     self.dut.driveattr[attrName] = self.dut.cust_testname(self.screenCode(screenCls) , attrName)
                     if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
                        if attrName in ['CUST_TESTNAME_2', 'CUST_TESTNAME_3' ]: #SUCUST_TESTNAME_2 & _3 are too long for FIS.
                           attrName = attrName[:13] + attrName[-1]
                        self.dut.driveattr['SU' + attrName] = self.dut.cust_testname(self.screenCode(screenCls) , 'SU' + attrName)
                  else:
                     self.dut.driveattr['CUST_TESTNAME'] = self.dut.cust_testname(self.screenCode(screenCls) )
               elif testSwitch.FE_0179998_231166_P_SUPPORT_DV3_AS_LAST_CONTENT and screenCls in self.dcm_contents:
                  if testSwitch.FE_0193449_231166_P_DL1_SUPPORT:
                     attrName = self.getScreenAttrName(self.contentCode(screenCls))
                     self.dut.driveattr[attrName] = self.dut.cust_testname(self.contentCode(screenCls) , attrName)
                     if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
                        if attrName in ['CUST_TESTNAME_2', 'CUST_TESTNAME_3' ]: #SUCUST_TESTNAME_2 & _3 are too long for FIS.
                           attrName = attrName[:13] + attrName[-1]
                        self.dut.driveattr['SU' + attrName] = self.dut.cust_testname(self.contentCode(screenCls) , 'SU' + attrName)
                  else:
                     self.dut.driveattr['CUST_TESTNAME'] = self.dut.cust_testname(self.contentCode(screenCls) )
               elif code not in self.non_dcm_screens:
                  # Do not mix DCM screens with PIF screens in the same attribute
                  self.non_dcm_screens += code
            break
      else:
         # Save unoffical DCM screens to a different attribute (PROC_CTRL16)
         self.non_dcm_screens += screenCls

      if self.non_dcm_screens:
         self.dut.driveattr['NON_DCM_SCREENS'] = self.non_dcm_screens

   if not testSwitch.FE_0185033_231166_P_MODULARIZE_DCM_COMMIT:
      def __parseAttrQualifiers(self,data):
         if 'FAILCODE' in data:
            return []
         return [req.split(':') for req in data] #name, relationship, value

   def getDCMModelNum(self):
      custModelNum = ''
      sunModelID = None


      if '[' not in self.dut.driveConfigAttrs.get('CUST_MODEL_NUM', ['', ''])[1]:
         objMsg.printMsg("Detected [] not supported in cust model num... disabling FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS.")
         testSwitch.FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS = 0


      custModelNumOverride = getattr(TP, 'CUST_MODEL_NUM_Override', {}).get(self.dut.partNum, None)
      if custModelNumOverride == None:
         custModelNum = self.dut.driveConfigAttrs.get("CUST_MODEL_NUM",(None,None))[1]

         if custModelNum == None:
            #Allow drive model num override of custmodel num
#CHOOI-19May17 OffSpec
#            custModelNum = self.dut.driveConfigAttrs.get('DRV_MODEL_NUM', 'INVALID')
            custModelNum = self.dut.driveConfigAttrs.get('DRV_MODEL_NUM', 'INVALID')[1]
      else:
         objMsg.printMsg("Overrode DCM 'CUST_MODEL_NUM' with TP value %s" % (custModelNumOverride,))
         custModelNum = custModelNumOverride


      PIFHandler = CPIFHandler()
      dPNum = PIFHandler.getPnumInfo(self.dut.partNum)                 # Get the dict of info for this partnum

      if 'WRITE_SUN_MODEL' in [i['ID'] for i in dPNum['lCAIDS']]:
         #ID if SUN PN

         objMsg.printMsg("Detected SUN model number update required")
         import PIF
         #Get the sun model number ID from PIF... for mat is SunModelId = {'PN':value}
         sunModelID = Utility.CUtility.getRegex(self.dut.partNum, PIF.SunModelId)
         if sunModelID == None:
            ScrCmds.raiseException(11049, "PIF.SunModelId not set up properly for SUN_MODEL_NUM")

         custModelNum = self.getSunModelNum(custModelNum, sunModelID)

      return custModelNum


   def SetFISModelNum(self):

#CHOOI-19Apr17 OffSpec
      self.dut.driveattr['DRV_MODEL_NUM'] = self.dut.IdDevice['IDModel'].strip()

#       rawModelNum = self.dut.IdDevice['IDModel']
#       justification = "LEFT"
#       if testSwitch.auditTest:
#          rawModelNum = "STFFFFAUDIT"
# 
#       model1, model2 = self.makeModelNumFisReady(rawModelNum)
# 
#       self.dut.driveattr['CUST_MODEL_NUM'] = model1
#       self.dut.driveattr['CUST_MODEL_NUM2'] = model2
# 
#       if testSwitch.BF_0183298_231166_P_FIX_DRV_MODEL_NUM_ECHO_OPT_ATTRVAL:
#          if 'DRV_MODEL_NUM' in self.dut.driveConfigAttrs:
#             self.dut.driveattr['DRV_MODEL_NUM'] = self.dut.driveConfigAttrs['DRV_MODEL_NUM'][1]
#          if 'DRV_MODEL_NUM2' in self.dut.driveConfigAttrs:
#             self.dut.driveattr['DRV_MODEL_NUM2'] = self.dut.driveConfigAttrs['DRV_MODEL_NUM2'][1]

   def SetFISModelJustification(self):
      # Valid justifications are "LEFT" or "RIGHT"
      justification = self.dut.driveConfigAttrs.get('CUST_MN_JUSTIFY', getattr(TP, 'driveModelJustification',{}).get(self.dut.partNum, ('=',"LEFT")))[1]
      self.dut.driveattr['CUST_MN_JUSTIFY'] = justification

#CHOOI-22Dec13 White Label Added
   def SetFISTPDrvSN(self):
      self.dut.driveattr['TP_DRV_SN'] = str(self.dut.IdDevice['IDSerialNumber'])

   def SetFISNumLbas(self):
      self.dut.driveattr['USER_LBA_COUNT'] = str(max(self.dut.IdDevice["Max LBA Ext"]+1, self.dut.IdDevice["Max LBA"]+1))

   def makeModelNumFisReady(self, rawModelNum):
      if testSwitch.FE_0185033_231166_P_MODULARIZE_DCM_COMMIT:
         if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
            #SAS
            intType = 'SAS'
         else:
            #SATA
            intType = 'SATA'
         model_1, model_2 = CommitServices.makeModelNumFisReady(rawModelNum, intType)
      else:
         if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
            #SAS
            if testSwitch.FE_0193449_231166_P_DL1_SUPPORT:
               model_1 = Utility.CUtility.bracketize(rawModelNum[0:24], 24)
               model_2 = '[]'
            else:
               model_1 = '[%-24s]' %  (rawModelNum[0:24],)
               model_2 = '[%s]' % ('',)
         else:
            #SATA
            if testSwitch.FE_0193449_231166_P_DL1_SUPPORT:
               model_1 = Utility.CUtility.bracketize(rawModelNum[0:30], 30)
               model_2 = Utility.CUtility.bracketize(rawModelNum[30:], 10)
            else:
               model_1 = '[%-30s]' %  (rawModelNum[0:30],)
               model_2 = '[%-10s]' % (rawModelNum[30:],)

      return model_1, model_2

   def updateDriveFISAttributes(self):
      #force update of info into interface and dut object
      from IntfClass import CIdentifyDevice
      oIntf = CIdentifyDevice()

#CHOOI-19Apr17 OffSpec - add  SetFISTPDrvSN
      self.SetFISTPDrvSN()
      self.SetFISModelNum()
#CHOOI-19Apr17 OffSpec
#      self.SetFISModelJustification()
      self.SetFISNumLbas()

   def autoValidateZGS(self, attrName = 'ZERO_G_SENSOR'):
      ZGS = self.dut.IdDevice['ZGS']
      driveattr_ZGS = self.dut.driveattr['ZERO_G_SENSOR']

      if not (str(self.dut.driveConfigAttrs.get('ZERO_G_SENSOR',(0,'NA'))[1]).rstrip() == 'NA' and testSwitch.FE_0157486_357260_P_DO_NOT_CHECK_ZGS_BIT_IF_DCM_SAYS_NA):
         if ZGS and (driveattr_ZGS == "0" or driveattr_ZGS == "NA"):
            objMsg.printMsg('Error: ZGS = 1 but DriveAttribute ZERO_G_SENSOR = 0/NA')
            ScrCmds.raiseException(14761, "ZGS = 1 but DriveAttribute ZERO_G_SENSOR = 0/NA")
         elif not ZGS and driveattr_ZGS == "1":
            objMsg.printMsg('Error: ZGS = 0 but DriveAttribute ZERO_G_SENSOR = 1')
            if not testSwitch.BF_0122964_231166_NO_FAIL_FOR_ZGS_AVAIL_NOT_NEED:
               ScrCmds.raiseException(14761, "ZGS = 0 but DriveAttribute ZERO_G_SENSOR = 1")
      self.autoValidateDCMAttrString('ZERO_G_SENSOR')

   def getDriveConfigAttributes(self, partNum = None, force = False, failInvalidDCM = False):
      if partNum is None:
         partNum = self.dut.partNum                             # use default PN
      if partNum == self.dut.oldPN and not force:
         return self.dut.driveConfigAttrs                       # same DCM data
      else:
         self.dut.oldPN = self.dut.partNum
         force = True

      if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:
         from CCABuildCfg import buildTestCCADict
         buildTestCCADict()
      elif self.dut.driveConfigAttrs in [None,{}] or force == True:
         if testSwitch.FE_0185033_231166_P_MODULARIZE_DCM_COMMIT:
            self.dut.driveConfigAttrs = CommitServices.getDriveConfigAttributes(partNum = partNum, failInvalidDCM = True)
         else:
            self.dut.driveConfigAttrs = {}
            data = ''
            for i in xrange(4):
               if ConfigVars[CN].get('DCC_PRE_RELEASE', 0):
                  data = RequestService("DCMServerRequest",("GetLatest_DriveConfigAttributes",(partNum,)))[1]
               else:
                  data = RequestService("DCMServerRequest", ("GetDriveConfigAttributes",(partNum,)))[1]
               data = data.get('DATA', {'FAILCODE':data.get('EC',(99999,''))[0]})
               if 'FAILCODE' in data:
                  objMsg.printMsg("'data' from RequestService('GetDriveConfigAttributes'): %s" % data)
                  if i < 3:
                     sleepTime = i*600 + 60
                     objMsg.printMsg("Sleep %s" % sleepTime)
                     time.sleep(sleepTime)
               else:
                  break
            else:
               if (ConfigVars[CN].get('PRODUCTION_MODE',0) and testSwitch.FE_0173503_357260_P_RAISE_EXCEPTION_IF_UNABLE_TO_READ_DCM) or failInvalidDCM:
                  ScrCmds.raiseException(14761, "Custom Drive Attributes - DCM not supported in Host/FIS.")
            if DEBUG:
               objMsg.printMsg("'data' from RequestService('GetDriveConfigAttributes'): %s" % data) #Seeing what is returned by the DCM can be helpful for debug
            if testSwitch.virtualRun:
               if testSwitch.FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS:
                  custModel = getattr(TP, 'veModelNum','ST3500410AS')
                  custModel1, custModel2 = self.makeModelNumFisReady(custModel)
                  #'CUST_MN_JUSTIFY:=:RIGHT',
                  data = ['STATUS:=:PASS',
                          'CUST_MN_JUSTIFY:=:LEFT', 'CUST_MODEL_NUM:=:%s' % custModel1, 'CUST_MODEL_NUM2:=:%s' % custModel2,
                          'DRV_MODEL_NUM:=:%s' % getattr(TP, 'veModelNum','ST3500410AS'),
                          'TC_LABEL_BLK_PN:=:100545501',
                          'USER_LBA_COUNT:=:312581808',
                          'SERVER_ERROR:=:NO ERROR',
                          'ZERO_PTRN_RQMT:=:20',]
                          #'CUST_TESTNAME:=:SD3NT1',
                          #'SECURITY_TYPE:=:TCG',]
               else:
                  custModel = getattr(TP, 'veModelNum','ST3500410AS')
                  data = ['STATUS:=:PASS',
                          'CUST_MN_JUSTIFY:=:LEFT',
                          'CUST_MODEL_NUM:=:%s' % custModel,
                          'DRV_MODEL_NUM:=:%s' % getattr(TP, 'veModelNum','ST3500410AS'),
                          'TC_LABEL_BLK_PN:=:100545501',
                          'USER_LBA_COUNT:=:312581808',
                          'SERVER_ERROR:=:NO ERROR',
                          'ZERO_PTRN_RQMT:=:10']

               # Debug
               data.extend(['CUST_TESTNAME:=:AP1DV3'])   # DCM Screens

            #Quick PCO checkout
            if not ConfigVars[CN].get('PRODUCTION_MODE',1) and ConfigVars[CN].get('QUICK_PCO_CHECKOUT',0):
               from Setup import CSetup
               mc_connected = CSetup().IsMCConnected()
               if DEBUG:   objMsg.printMsg("mc_connected=%s" % mc_connected)

               if not mc_connected:
                  objMsg.printMsg('Quick_PCO_Checkout = 1')
                  data = ['STATUS:=:PASS',
                          'SED_LC_STATE:=:USE',
                          'DLP_SETTING:=:UNLOCKED',
                          #'SECURITY_TYPE:=:SECURED BASE (SD AND D)',
                          'ZERO_PTRN_RQMT:>:13',
                          'SERVER_ERROR=NO ERROR']
            else:
               if DEBUG:    objMsg.printMsg('Quick_PCO_Checkout = 0')

            objMsg.printMsg("%s DCM data = %s" %(partNum,data ))

            try:
               #Parse the response from the host
               results = self.__parseAttrQualifiers(data)
               #if we received valid data then we set variables.
               if len(results) > 0:
                  results = self.validateResults(results)
                  num = 0
                  for name, relationship, value in results:
                     if name == 'SERVO_CODE':
                        # DCM server will response multiple 'SERVO_CODE' attribute, thus append index number to give unique key in dictionary
                        num += 1
                        name += "%d" %num

                     self.dut.driveConfigAttrs[name] = (relationship, value)
               else:
                  raise # no DCM data
            except:
               import traceback
               objMsg.printMsg("Results from parseAttrs: %s" % (data,),objMsg.CMessLvl.VERBOSEDEBUG)
               objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
               objMsg.printMsg("Custom Drive Attributes not supported in Host/FIS.")
               if (ConfigVars[CN].get('PRODUCTION_MODE',0) and testSwitch.FE_0173503_357260_P_RAISE_EXCEPTION_IF_UNABLE_TO_READ_DCM) or failInvalidDCM:
                  ScrCmds.raiseException(14761, "Custom Drive Attributes - DCM not supported in Host/FIS.")

      if DEBUG:
         objMsg.printMsg("self.dut.driveConfigAttrs=%s" %(self.dut.driveConfigAttrs))
      return self.dut.driveConfigAttrs

   if not testSwitch.FE_0185033_231166_P_MODULARIZE_DCM_COMMIT:
      def validateResults(self, results):  #Handle invalid entry appended by host e.g 'SERVER_ERROR=NO ERROR'
         for dcmEntry in results:
            if len(dcmEntry) != 3:
               dcmParams = dcmEntry[0].split("=")
               if len(dcmParams) == 2:     #name, value
                  results[results.index(dcmEntry)]=[dcmParams[0], '=', dcmParams[1]]
               else:
                  ScrCmds.raiseException(11044, "Invalid DCM data : %s " %dcmEntry)
         return results


   def ProcessCustomAttributeRequirements(self):
      if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:  #CCV will now handle this
         return
      #Looks for attribute handlers retreived from GetDriveConfigAttributes host service
      if testSwitch.FE_0180513_007955_COMBINE_CRT2_FIN2_CUT2:
         self.getDriveConfigAttributes(force = True)
      else:
         self.getDriveConfigAttributes()

      self.RunCustCfg("CUST_ATTR", self.getDriveConfigAttributes)

      if testSwitch.FE_0152007_357260_P_DCM_ATTRIBUTE_VALIDATION:
         if testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
            objMsg.printMsg("Forcing update of current drive attribute values.")
            self.updateDriveFISAttributes()
         objMsg.printMsg('Validating Customer Required Attributes')
         for name in self.dut.driveConfigAttrs:
            if name in self.custAttrHandlers:
               self.custAttrHandlers[name](name)
         if testSwitch.FE_0198029_231166_P_WWN_BEG_AND_END and 'WWN' not in self.dut.driveConfigAttrs:
            self.autoValidateWWNAttr('WWN')
      else:
         for name, val in self.dut.driveConfigAttrs.items():
            relationship, value = val
            if name in self.custAttrHandlers:
               self.custAttrHandlers[name]=(relationship,value)

   def autoValidateCustTestNames(self, attrName):
      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         #get the superset
         if attrName in ['CUST_TESTNAME_2', 'CUST_TESTNAME_3' ]: #SUCUST_TESTNAME_2 & _3 are too long for FIS.
            SUattrName = attrName[:13] + attrName[-1]
            proc_list = CPIFHandler.createTestList(self.dut.driveattr.get('SU' + SUattrName, DriveAttributes.get('SU' + SUattrName, '')))
         else:
            proc_list = CPIFHandler.createTestList(self.dut.driveattr.get('SU' + attrName, DriveAttributes.get('SU' + attrName, '')))
         #get the requirements from FIS for this customer
         cust_list = CPIFHandler.createTestList(self.dut.driveConfigAttrs.get(attrName,('=',''))[1])

         if testSwitch.BF_0196490_231166_P_FIX_TIER_SU_CUST_TEST_CUST_SCREEN:
            #clear out the value to re-create it from the 'SU' version
            self.dut.driveattr[attrName] = ''

         #create the attribute as the intersection of the superset and the requirements
         for code in set(proc_list).intersection(cust_list):
            self.dut.driveattr[attrName] = self.dut.cust_testname(code , attrName)

      self.autoValidateDCMAttrString(attrName)

   def autoValidateDCMAttrString(self, attrName):
      if ConfigVars[CN].get('DIS_VALID_BG', 0) and attrName == 'BSNS_SEGMENT':
         objMsg.printMsg("ConfigVar DIS_VALID_BG is enabled.... bypassing BSNS_SEGMENT validation.")
      else:
         if attrName in self.dut.driveConfigAttrs:
            self.autoValidateDCMAttr(attrName, str(self.dut.driveConfigAttrs[attrName][1]).rstrip(),\
                                         str(self.dut.driveattr.get(attrName, DriveAttributes.get(attrName,None))).rstrip() )

   def autoValidateDCMAttrFloat(self, attrName):
      if self.dut.driveattr.get(attrName, DriveAttributes.get(attrName, None)) == None:
         msg = "Missing drive attribute value!\nAttrName:%s" % (attrName)
         ScrCmds.raiseException(11201, msg)
      else:
         self.autoValidateDCMAttr(attrName, float(str(self.dut.driveConfigAttrs[attrName][1]).rstrip()),\
                                               float(str(self.dut.driveattr.get(attrName, DriveAttributes.get(attrName, None))).rstrip()) )

   def autoValidateDCMAttrLBAs(self, attrName):
      if testSwitch.BF_0166991_231166_P_USE_PROD_MODE_DEV_PROD_HOSTSITE_FIX:
         prodMode = ConfigVars[CN]['PRODUCTION_MODE']
      else:
         prodMode = RequestService('GetSiteconfigSetting','CMSHostSite')[1].get('CMSHostSite','NA') not in ['LCO']

      if (ConfigVars[CN].get('numHeads',0) != 0) and (not prodMode):
         objMsg.printMsg('NON-STANDARD HEAD COUNT DETECTED : SKIPPING USER_LBA_COUNT DCM ATTRIBUTE CHECK!')
      else:
         if not ConfigVars[CN].get('SKIP_LBA_CHECK', 0):
            self.autoValidateDCMAttr(attrName, float(str(self.dut.driveConfigAttrs[attrName][1]).rstrip()),\
                                            float(str(self.dut.driveattr.get(attrName, DriveAttributes.get(attrName, None))).rstrip()) )

   def autoValidateDCMAttr(self, attrName, dcmVal, attrVal):
      rel = self.dut.driveConfigAttrs[attrName][0].rstrip()
      if rel == '=':
         rel = '=='
      if not eval('attrVal' + rel + 'dcmVal'):
         msg = "Invalid DCM attribute found in validation!\nAttrName:%s\nAttrValue:%s\nAttrRequirement:%s" % (attrName, attrVal, dcmVal)
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(14761, msg)
         else:
            objMsg.printMsg("VE WARNING!!!-> %s" % msg)
      else:
         objMsg.printMsg("Validated attribute %s: %s %s %s" % (attrName, attrVal, rel, dcmVal) )

   def autoValidateZeroPattern(self, attrName):
      if testSwitch.FE_0185033_231166_P_MODULARIZE_DCM_COMMIT and testSwitch.BF_0196490_231166_P_FIX_TIER_SU_CUST_TEST_CUST_SCREEN:
         if CommitServices.isTierPN( self.dut.partNum ):
            objMsg.printMsg("Don't run Zero pattern/verify as tier drive.")
            return
      attrVal = str(self.dut.driveattr.get(attrName, DriveAttributes.get(attrName, None))).rstrip()
      dcmVal = str(self.dut.driveConfigAttrs[attrName][1]).rstrip()
      if dcmVal == 'NA':
         objMsg.printMsg("Skipping ZERO_PTRN_RQMT check - DCM indicated Not Applicable")
      if attrVal not in ['None','','NONE'] and dcmVal not in ['None','','NONE'] and int(attrVal) >= int(dcmVal):
         self.dut.driveattr[attrName] = dcmVal
         objMsg.printMsg("Validated attribute %s: %s %s %s" % (attrName, attrVal, '>=', dcmVal) )
      else:
         msg = "Invalid DCM attribute found in validation!\nAttrName:%s\nAttrValue:%s\nAttrRequirement:%s" % (attrName, attrVal, dcmVal)
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(14761, msg)
         else:
            objMsg.printMsg("VE WARNING!!!-> %s" % msg)

   def autoValidateWWNAttr(self, attrName):
      if testSwitch.FE_0198029_231166_P_WWN_BEG_AND_END:
         if ( CommitServices.isTierPN( self.dut.partNum ) ):
            objMsg.printMsg("WWN not validated for TIER.")
            return

         attrLookupFallback = {'SAS': ('=', 'WW_SAS_ID'), 'SATA': ('=','WW_SATA_ID')}[DriveAttributes.get('INTERFACE','SATA')]
         wwAttrName = str(self.dut.driveConfigAttrs.get(attrName, attrLookupFallback)[1]).rstrip()
      else:
         wwAttrName = str(self.dut.driveConfigAttrs[attrName][1]).rstrip()
      if not self.autoValidatesAttrExists(wwAttrName):
         msg = "Invalid DCM attribute found in validation! WWN attribute :%s does not exist" % wwAttrName
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(14761, msg)
         else:
            objMsg.printMsg("VE WARNING!!!-> %s" % msg)
      else:
         objMsg.printMsg("Validated WWN attribute %s exists" % wwAttrName )

   def autoValidatesAttrExists(self, attrName):
      return str(self.dut.driveattr.get(attrName, DriveAttributes.get(attrName,None))).rstrip() not in ['None','','NONE']


   def autoValidateHDAFw(self, attrName):
      """ Verify HDA, F3, servo IV codes """

      import serialScreen
      oSerial = serialScreen.sptDiagCmds()
      HDA = int(oSerial.GetCtrl_L(printResult=False)['Heads'])
      if HDA and HDA < 3:
         HDA = '1D'
      elif HDA >= 3:
         HDA = '2D'

      F3 = self.dut.driveattr.get('CODE_VER').split(".")[0]
      Servo = self.dut.driveattr.get('SERVO_CODE')
      IV = self.dut.driveattr.get('IV_SW_REV')
      HDAFwAttr = "%s/%s/%s/%s" %(HDA,F3,Servo,IV)

      self.dut.driveattr['HDA_FW'] = HDAFwAttr
      try:
         dcmVal = str(self.dut.driveConfigAttrs[attrName][1]).rstrip()
         self.autoValidateDCMAttr(attrName, dcmVal, HDAFwAttr)
      except KeyError:
         objMsg.printMsg("Skipping DCM attribute validation: No information for validation of %s" %attrName)


   ############### CAID Handlers
   # SMARTReadData - Check SMART attribute data
   def SMARTReadData(self,dCAID):

      if testSwitch.NoIO:
         objMsg.printMsg('SMARTReadData not supported in NoIO')
         return

      import math
      if DEBUG:
         objMsg.printMsg('Start SMARTReadData dCAID=%s' % `dCAID`)
      data = self.ReadSmartAttrIO()
      if testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM:
         data_th = self.ReadSmartThreshold()

      dict = dCAID.copy()
      dict.pop("ID")

      for i in dict:
         if i == "ATTR":   # SMART Attribute check
            for tmptup in dict[i]:
               iAttr = self.GetSmartAttrIO(data, tmptup[0], tmptup[3])
               evalstr = "%s %s %s" % (iAttr, tmptup[1], tmptup[2])
               result = eval(evalstr)
               objMsg.printMsg("ATTR idx=%s 'drive vs setting' evalstr='%s' result=%s" % (tmptup[0], evalstr, result))
               if result != True:
                  ScrCmds.raiseException(10467, "Fail SMART attr check drive=%s setting=%s" % (iAttr, tmptup[2]))

         # SMART Attribute checks against Raw Data
         if (i == "ATTR_RAW") and testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM:
            for tmptup in dict[i]:
               iAttr = self.GetSmartAttrIO(data, tmptup[0], tmptup[3])[2]
               if isinstance(tmptup[2], str):
                  if "THRESHOLD" in tmptup[2]:
                     iTh = tmptup[2].replace("THRESHOLD", str(self.GetSmartThreshold(data_th, tmptup[0])))
                  else:
                     iTh = tmptup[2]
               else:
                  iTh = tmptup[2]
               evalstr = "%s %s %s" % (iAttr, tmptup[1], iTh)
               result = eval(evalstr)
               objMsg.printMsg("ATTR idx=%s 'drive vs setting' evalstr='%s' result=%s" % (tmptup[0], evalstr, result))
               if result != True:
                  ScrCmds.raiseException(10467, "Fail SMART attr check drive=%s setting=%s" % (iAttr, tmptup[2]))

         # SMART Attribute checks against Nominal
         elif (i == "ATTR_N") and testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM:
            for tmptup in dict[i]:
               iAttr = self.GetSmartAttrIO(data, tmptup[0])[0]
               if isinstance(tmptup[2], str):
                  if "THRESHOLD" in tmptup[2]:
                     iTh = tmptup[2].replace("THRESHOLD", str(self.GetSmartThreshold(data_th, tmptup[0])))
                  else:
                     iTh = tmptup[2]
               else:
                  iTh = tmptup[2]
               evalstr = "%s %s %s" % (iAttr, tmptup[1], iTh)
               result = eval(evalstr)
               objMsg.printMsg("ATTR idx=%s 'drive vs setting' evalstr='%s' result=%s" % (tmptup[0], evalstr, result))
               if result != True:
                  ScrCmds.raiseException(10467, "Fail SMART attr check drive=%s setting=%s" % (iAttr, tmptup[2]))

         # SMART offset check (unsigned short little-endian format)
         elif i == "WORDOFFSET":
            for tmptup in dict[i]:
               sValue = data[int(tmptup[0]) : int(tmptup[1])]
               iValue = struct.unpack("<H", sValue)[0]
               evalstr = "%s %s %s" % (iValue, tmptup[2], tmptup[3])
               result = eval(evalstr)
               objMsg.printMsg("WORDOFFSET offset=%s:%s 'drive vs setting' evalstr='%s' result=%s" % (tmptup[0], tmptup[1], evalstr, result))
               if result != True:
                  ScrCmds.raiseException(10467, "Fail SMART offset check drive=%s setting=%s" % (iValue, tmptup[3]))

         else:
            ScrCmds.raiseException(11044, "Invalid CAID data or command=%s" % i)

   # SMARTReadData - Read 512 bytes from CPC ICmd.SmartReadData()
   def ReadSmartAttrIO(self):
      data = ICmd.SmartEnableOper()
      if data['LLRET'] != 0:
         ScrCmds.raiseException(10467, "Fail SmartEnableOper. Data=%s" % data)

      data = ICmd.SmartReadData()
      if data['LLRET'] != 0:
         ScrCmds.raiseException(10467, "Fail SmartReadData. Data=%s" % data)

      data = ICmd.GetBuffer(RBF, 0, 512)
      if data['LLRET'] != 0:
         ScrCmds.raiseException(10467, "Fail SmartReadData GetBuffer. Data=%s" % data)

      data = data['DATA']
      if testSwitch.virtualRun:
         data = '\n\x00\x01\x0f\x00dd\x00\x00\x00\x00\x00\x00\x00\x03\x03\x00dd\x00\x00\x00\x00\x00\x00\x00\x042\x00dd\x07\x00\x00\x00\x00\x00\x00\x053\x00dd\x00\x00\x00\x00\x00\x00\x00\x07\x0f\x00d\xfd\x00\x00\x00\x00\x00\x00\x00\t2\x00dd\x00\x00\x00\x00\x00\x00\x00\n\x13\x00dd\x00\x00\x00\x00\x00\x00\x00\x0c2\x00dd\x07\x00\x00\x00\x00\x00\x00\xb82\x00dd\x00\x00\x00\x00\x00\x00\x00\xbb2\x00dd\x00\x00\x00\x00\x00\x00\x00\xbc2\x00d\xfd\x00\x00\x00\x00\x00\x00\x00\xbd:\x00dd\x00\x00\x00\x00\x00\x00\x00\xbe"\x00IH\x1b\x00\x1b\x1b\x00\x00\x00\xbf2\x00dd\x00\x00\x00\x00\x00\x00\x00\xc02\x00dd\x02\x00\x00\x00\x00\x00\x00\xc12\x00dd\x07\x00\x00\x00\x00\x00\x00\xc2"\x00\x1b(\x1b\x00\x00\x00\x1b\x00\x00\xc3\x1a\x00dd\x00\x00\x00\x00\x00\x00\x00\xc5\x12\x00dd\x00\x00\x00\x00\x00\x00\x00\xc6\x10\x00dd\x00\x00\x00\x00\x00\x00\x00\xc7>\x00\xc8\xfd\x00\x00\x00\x00\x00\x00\x00\xf0\x00\x00d\xfd\x00\x00\x00\x00\xca\x9f\x00\xf1\x00\x00d\xfd\x00\x00\x00\x00\x00\x00\x00\xf2\x00\x00d\xfd\x00\x00\x00\x00\x00\x00\x00\xfe2\x00dd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00s\x03\x00\x01\x00\x02\x78\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xdf\xd8\xc2\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\xa9\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x005\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd6'
      if DEBUG:
         objMsg.printMsg("SmartReadData buffer data=%s" % `data`)

      return data

   # SmartReadThresh - Read 512 bytes from CPC ICmd.SmartReadThresh()
   def ReadSmartThreshold(self):
      data = ICmd.SmartEnableOper()
      if data['LLRET'] != 0:
         ScrCmds.raiseException(10467, "Fail SmartEnableOper. Data=%s" % data)

      data = ICmd.SmartReadThresh()
      if data['LLRET'] != 0:
         ScrCmds.raiseException(10467, "Fail SmartReadThresh. Data=%s" % data)

      data = ICmd.GetBuffer(RBF, 0, 512)
      if data['LLRET'] != 0:
         ScrCmds.raiseException(10467, "Fail SmartReadData GetBuffer. Data=%s" % data)

      data = data['DATA']
      if testSwitch.virtualRun:
         data = '\x01\x00\x01\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05$\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x1e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\na\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb8c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbe-\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xac'
      if DEBUG:
         objMsg.printMsg("SmartReadData buffer data=%s" % `data`)

      return data

   # SMARTReadData - Returns SMART attribute based on index
   def GetSmartAttrIO(self, data, idx, bytelen = 6):
      StartAttr = 2        # start of SMART attribute offset
      BytesPerAttr = 12    # each attr occupies 12 bytes
      MaxAttr = 30         # total of 30 attr defined for now

      for i in xrange(StartAttr, BytesPerAttr * MaxAttr, BytesPerAttr):
         OneAttr = data[i: i + BytesPerAttr]
         AttrIdx = ord(OneAttr[0:1])

         if AttrIdx == idx:
            AttrStatus = (OneAttr[1:3])
            AttrNom = ord(OneAttr[3:4])
            AttrWorst = ord(OneAttr[4:5])

            if bytelen >= 6:
               AttrRaw = (OneAttr[5:11]) + '\x00\x00'
               iRaw = struct.unpack("<Q", AttrRaw)
            else:       # bytelen = 4
               AttrRaw = (OneAttr[5:9])
               iRaw = struct.unpack("<L", AttrRaw)

            objMsg.printMsg("SMART: Idx=%s Nor=%s Worst=%s Raw=%s Raw=%s" % (hex(AttrIdx), hex(AttrNom), hex(AttrWorst), `AttrRaw`, hex(iRaw[0])))
            if testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM:
               return AttrNom, AttrWorst, iRaw[0]
            else:
               return iRaw[0]


      ScrCmds.raiseException(10467, "Unable to find SMART Attribute index=%s" % idx)

   # Get SMART Threshold value based on SMART attribute number.
   def GetSmartThreshold(self, data, idx):
      StartAttr = 2        # start of SMART attribute offset
      BytesPerAttr = 12    # each attr occupies 12 bytes
      MaxAttr = 30         # total of 30 attr defined for now

      for i in xrange(StartAttr, BytesPerAttr * MaxAttr, BytesPerAttr):
         OneAttr = data[i: i + BytesPerAttr]
         AttrIdx = ord(OneAttr[0:1])

         if AttrIdx == idx:
            thresholdValue = ord(OneAttr[1:2])

            objMsg.printMsg("SMART: Idx=%s ThVal(Hex)=%s ThVal(Dec)=%s" % (hex(AttrIdx), hex(thresholdValue), thresholdValue))
            return thresholdValue

      ScrCmds.raiseException(10467, "Unable to find SMART Threshold index=%s" % idx)

   # Write the world wide name  note: use test 172 to display WWN
   def writeWWN(self,dCAID):
      """ Write the world wide name  note: use test 172 to display WWN """
      objMsg.printMsg( ' Writing WWN' )
      if testSwitch.FE_0198029_231166_P_WWN_BEG_AND_END:
         oIntf = CIdentifyDevice()
         if oIntf.ID['IDWorldWideName'] == self.dut.driveattr.get(str(self.dut.driveConfigAttrs.get('WWN', (0,'WW_SATA_ID'))[1]).rstrip(), ''):
            objMsg.printMsg("WWN already set in drive")
            return
         else:
            #Manually force WWN intf to update
            owwn = FSO.WriteWWN(forceSetWWN=True)
            owwn.setWWN()
      else:
            #Manually force WWN intf to update
            owwn = FSO.WriteWWN(forceSetWWN=True)
            owwn.setWWN()

   # Write the HDA SN to the CAP   - note: use test 166 to display HDA sn
   def writeCAPHDASN(self,dCAID):
      """ Write the HDA SN to the CAP   - note: use test 166 to display HDA sn """
      objMsg.printMsg( ' Writing CAP HDA SN')
      capUpdate_prm = TP.CAPUpdate_CAP_SN_Prm_178.copy()
      capUpdate_prm['prm_name'] = 'CAP_SN'
      self.St( capUpdate_prm )

   if testSwitch.FE_0121886_231166_FULL_SUN_MODEL_NUM:
      def getSunModelNum(self, modelNumberBase, modelCode):
         ww = WorkWeek()
         YYWW = ww.GetWorkWeek()
         NUM_MODEL_NUM_CHARS = 40
         SERIAL_NUM_IN_MODEL_NUM_OFFSET = 10
         NUM_SERIAL_NUM_IN_MODEL_NUM_CHARS = 5

         modelSN = self.dut.serialnum[-NUM_SERIAL_NUM_IN_MODEL_NUM_CHARS:]

         modelNum = [' ']*NUM_MODEL_NUM_CHARS

         modelNum[NUM_MODEL_NUM_CHARS - SERIAL_NUM_IN_MODEL_NUM_OFFSET:NUM_MODEL_NUM_CHARS - SERIAL_NUM_IN_MODEL_NUM_OFFSET + NUM_SERIAL_NUM_IN_MODEL_NUM_CHARS] = modelSN


         for idx, char in enumerate('SEAGATE' + ' ' + modelNumberBase + ' ' + YYWW + modelCode):
            modelNum[idx] = char

         return ''.join(modelNum)


   def writeSunModelNum(self,dCAID):
      objMsg.printMsg("Writing Sun Model Num to attr...\n")
      if testSwitch.FE_0121886_231166_FULL_SUN_MODEL_NUM:
         self.dut.driveattr['SUN_MODEL_NUM'] =  self.dut.driveConfigAttrs.get('CUST_MODEL_NUM', self.dut.driveattr.get('CUST_MODEL_NUM', DriveAttributes['CUST_MODEL_NUM']))
      else:
         ww = WorkWeek()
         YYWW = ww.GetWorkWeek()
         self.dut.driveattr['SUN_MODEL_NUM'] = YYWW

      if testSwitch.FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS:
         self.writeWorkDate(dCAID)

   #-------------------------------------------
   def writeWorkDate(self,dCAID=None):
      from Cell import theCell
      #ww = WorkWeek()
      #YYWW = ww.GetWorkWeek()

      if testSwitch.NoIO:
         objMsg.printMsg("WRITE_WORK_DATE not supported in NoIO.")
         return

      if testSwitch.virtualRun:
         timeNow=time.mktime(time.strptime("1 1 2010", "%d %m %Y"))
      else:
         timeNow=time.time()

      today=time.localtime(timeNow)

      objMsg.printMsg("Final Assembly Date Today :    %s"%(time.asctime(today)))

      weekDayPoint = 3
      timeWeekPoint = timeNow + (weekDayPoint-today[6])*3600*24
      weekPoint = time.localtime(timeWeekPoint)
      objMsg.printMsg("Final Assembly Date WeekPoint: %s"%(time.asctime(weekPoint)))

      week = (weekPoint[7]-1)/7 +1
      year = weekPoint[0]%100
      weekstr = "%02d%02d"%(year,week)

      #      return weekstr
      ##-------------------------
      #      weekstr = GetFinalAssyDate()
      objMsg.printMsg("Final Assembly Date Weekstr:   %s"%(weekstr))
      ICmd.WriteFinalAssemblyDate(weekstr)



   def getDellPPID(self,forcegetPPID=False):
      """
      Retrieve the Dell PPID from current attrs or FIS DCM Web service
      """
      PPID = self.dut.driveattr.get('DISC_CUST_SN',None)

      #CHOOI-30Dec15 Added start
      if PPID != None and ('STCSO' not in PPID):
         objMsg.printMsg("1-PPID: %s"% (PPID))  #Debug
         PPID = None
      #CHOOI-30Dec15 Added End

      #Only get a new PPID if we don't already have one
      if PPID == None or forcegetPPID:

         # If either wasn't assigned at PWA then we need to request service for them
         CUST_SERIAL = self.dut.driveattr.get('CUST_SERIAL', False)
         CUST_REV = self.dut.driveattr.get('CUST_REV', False)

         #CHOOI-30Dec15 Added Start
         if CUST_SERIAL and ('STCSO' not in CUST_SERIAL):
            objMsg.printMsg("1-CUST_SERIAL: %s"% (CUST_SERIAL)) #debug
            CUST_SERIAL = False
            CUST_REV = False
         #CHOOI-30Dec15 Added End

         if not CUST_SERIAL or not CUST_REV or forcegetPPID:

            # Host request for dell PPID
            PPIDRetries = 4
            while PPIDRetries >= 0:
               retVal = RequestService("DCMServerRequest", ('GetDell_PPIDCode',(self.dut.serialnum, self.dut.driveattr['PART_NUM'])))
               retVal = ('GetDellPPID', retVal[1]['DATA'])
               if retVal[1]['Status'] == 'PASS':
                  break
               time.sleep(30)
               PPIDRetries -= 1

            if testSwitch.virtualRun or ConfigVars[CN].get('F_DELLPPID_GEN', 0):

               retVal = ('GetDellPPID', {'Status': 'PASS', 'PPIDRev': 'CUST_REV=A00', 'FailMessage': '', 'FailCode': '', 'PPIDCode': 'CUST_SERIAL=-SG-012348-54321-822-0004'})


               # Check to see if we have a unit-test override
               try:
                  uiVal = self.reqSvcOverride
                  #Since getattr is overriden to return St not None we need to check the type

                  if not type(uiVal) == types.TupleType:
                     fail = 1
                  else:
                     fail = 0
               except:
                  fail = 1

               # Disable the override if the above tests fail
               if fail == 1:
                  uiVal = None

               if not uiVal == None:
                  retVal = uiVal
                  self.reqSvcOverride = None

            try:
               if retVal[1]['Status'] == 'PASS':
                  PPIDCode = retVal[1].get('PPIDCode','')
                  CUST_SERIAL = self.dut.driveattr['CUST_SERIAL'] =  PPIDCode[PPIDCode.find('=')+1:]

                  PPIDRev = retVal[1].get('PPIDRev','')
                  CUST_REV = self.dut.driveattr['CUST_REV'] = PPIDRev[PPIDRev.find('=')+1:]
               else:
                  ScrCmds.raiseException(retVal[1]['FailCode'], retVal[1]['FailMessage'])

            except CRaiseException:
               raise
            except:
               ScrCmds.raiseException(11201,"DELL PPID RequestService failed: %s" % str(retVal))
         else:
            CUST_SERIAL = self.dut.driveattr["CUST_SERIAL"]
            CUST_REV = self.dut.driveattr["CUST_REV"]

         # DELL PPID consists of 23 chars
         # CUSTOMER Serial Number + Customer Rev
         PPID = CUST_SERIAL + CUST_REV

         #CHOOI-30Dec15 Debugging
         objMsg.printMsg("2-CUST_SERIAL : %s"% (CUST_SERIAL)) #debug
         objMsg.printMsg("2-CUST_REV    : %s"% (CUST_REV)) #debug
         objMsg.printMsg("2-PPID        : %s"% (PPID)) #debug

      if PPID == None:
         ScrCmds.raiseException(11201,"Missing PPID CUST_SERIAL and/or CUST_REV attribute")
      else:
         PPID = string.replace(PPID,'-','') # remove all "-"

      #A space is added on the end since it is saved in byte swapped format and the 23rd char needs a pad byte to swap with... space is the pad byte
      PPID = PPID.strip() + " "

      # DELL Spec 23 chars and we add 1 to allow 23rd char to be byte swapped with a pad byte... 0x20 (space)
      if len(PPID) != 24:
         ScriptComment("The full PPID length is incorrect. Should be 24 characters.  Check CUST_SERIAL or CUST_REV attributes.")
         ScrCmds.raiseException(10158,"Dell PPID length is incorrect.")

      return PPID


   def writeDellPPID(self,dCAID, PPID_Verify_Only = 0):

      if self.dut.nextOper == "FNG2":
         PPID_Verify_Only = 1

      if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:  # CCA CCV now handles this
         return

      if testSwitch.NoIO:
         import serialScreen, sptCmds
         sptCmds.enableDiags()
         oSer = serialScreen.sptDiagCmds()

      if testSwitch.FE_0136017_357552_DELL_PPID_FOR_SAS:
         #Must do this for SAS, then return
         from CCV_CustUniq_IF3 import oCDell_PPID
         if testSwitch.FE_0162672_357260_P_FORCE_GET_PPID:
            oCDell_PPID.CustomerInfo(forcegetPPID='ON')        # Verifies and write DELL PPID type attributes - bypasses all others
         else:
            oCDell_PPID.CustomerInfo()                         # Verifies and write DELL PPID type attributes - bypasses all others
         return

      if not PPID_Verify_Only:

         ScriptComment("Dell PPID Write and Verify")
         if testSwitch.FE_0162672_357260_P_FORCE_GET_PPID:
            PPID = self.getDellPPID(forcegetPPID=True)
         else:
            PPID = self.getDellPPID()

         if testSwitch.NoIO:
            ScriptComment("SP Write Dell PPID.")
            PPID = PPID[:23]  #diagnostic cmd L>W supports 23 bytes Write PPID only
            objMsg.printMsg("PPID = '%s'"% (PPID))
            oSer.writePPID(writePPID = PPID)
         else:
            from IntfClass import CInterface
            oIntf = CInterface()

            ScriptComment("IO Write Dell PPID")
            ICmd.SmartEnableOper()

            if testSwitch.BF_0136370_231166_ADD_UNLOCK_PRIOR_TO_AVSCAN_UPDATES :
               ICmd.UnlockFactoryCmds()
            oIntf.writeUniformPatternToBuffer('write', dataPattern = (0x2020, 0x2020))

            #fill buffer with PPID data
            sPPID = ''.join(Utility.CUtility.byteSwap(PPID))
            ICmd.FillBuffer( WBF,  0,  sPPID)

            ICmd.SmartWriteLogSec(0x9A, 1)
            oIntf.displayBuffer('write')  #display write buffer

            oIntf.writeUniformPatternToBuffer('read', dataPattern = (0x1122, 0x3344), dataPattern1 = (0x5566, 0x7788)) #write pattern to read buffer
            oIntf.displayBuffer('read') #display read buffer

      else:
         if self.dut.nextOper == "FNG2":
            PPID = DriveAttributes.get('DISC_CUST_SN', "NONE").strip() + " "
            ScriptComment("Dell PPID Verify=%s" % PPID)
         else:
            PPID = self.dut.driveattr.get('CUST_SERIAL', DriveAttributes.get('CUST_SERIAL','NONE')) + self.dut.driveattr.get('CUST_REV', DriveAttributes.get('CUST_REV','NONE'))


      if testSwitch.NoIO:
         ScriptComment("SP Read Dell PPID")
         read_PPID = oSer.getPPID()
         objMsg.printMsg("oSer.getPPID()  read_PPID: '%s'    PPID: '%s'"% (read_PPID, PPID))

      else:
         ScriptComment("IO Read Dell PPID")

         ICmd.SmartReadLogSec(0x9A, 1)
         oIntf.displayBuffer('read')       #display read buffer with smart log data

         bD1 = oIntf.writeBufferToFile(numBytes = 24) #write buffer data to file

         if not testSwitch.virtualRun:
            read_PPID = ''.join(Utility.CUtility.byteSwap( bD1 ))[:len(PPID)] #truncate to same length as some buffer functions are ' ' padded
         else:
            read_PPID = PPID

      ScriptComment("read_PPID value from SMART Log Page 9A:  %s"%(read_PPID))

      if (read_PPID[:23] != PPID[:23]):
         ScriptComment("read_PPID: '%s'    does not match PPID: '%s'"% (read_PPID, PPID))
         ScrCmds.raiseException(10158,"Incorrect data.")
      else:
         ScriptComment("PPID value has been verified to be written to SMART Log Page 9A.")
         self.dut.driveattr['DISC_CUST_SN'] = read_PPID.strip()
         if PPID_Verify_Only:
            return 1


   def dellConfigCode(self,dCAID):
      #Config Code adjustment=========================================================================
      HDVendor = self.HeadType()
      if DriveAttributes.has_key('CONFIG_CODE'):
         if HDVendor != 'NONE':
            DriveAttributes['CONFIG_CODE'] = str(HDVendor)+DriveAttributes['CONFIG_CODE'][1:]
         if len(DriveAttributes['CONFIG_CODE']) == 4:
            DriveAttributes['CONFIG_CODE'] = DriveAttributes['CONFIG_CODE'][0:-1] + '1'
         elif len(DriveAttributes['CONFIG_CODE']) == 3:
            DriveAttributes['CONFIG_CODE'] = DriveAttributes['CONFIG_CODE'] + '1'
      else:
         ScrCmds.raiseException(11201,"Missing CONFIG_CODE attribute")

   # This function will return value of Head vendor for support Config code attribute.
   def HeadType(self):
      objMsg.printMsg("Head_type: %s" % self.dut.HGA_SUPPLIER)
      return {'RHO':1,'TDK':2,'HWY':3}[self.dut.HGA_SUPPLIER]

   # Write the product family id (from CIF file) to the CAP    note: use test 172 to display PFMID
   def writePFM_ID(self,dCAID):
      sPFM_ID = dCAID.get('Info')
      objMsg.printMsg( ' Writing PFM_ID - family ID: %s' %sPFM_ID )

      capUpdate_prm = TP.CAPUpdate_Prm_178.copy()
      capUpdate_prm['prm_name'] = 'PFM_ID'
      capUpdate_prm['PFM_ID'] = sPFM_ID
      self.St( capUpdate_prm )

   # Write the number of logical heads to CAP based on partnumber  note: use test 172 to display HD Count
   def writeHD_COUNT(self,dCAID):

      objMsg.printMsg(' Writing CAP Logical Head count from dut.imaxHead')
      tHdCount = self.dut.imaxHead
      capUpdate_prm = TP.CAPUpdate_Prm_178.copy()
      capUpdate_prm['prm_name'] = 'CAP_HDCOUNT'
      capUpdate_prm['HEAD_COUNT'] = tHdCount
      self.St( capUpdate_prm )


   def setIBMSN(self,dCAID=None):
      pass

   def getHDASN(self,dCAID=None):
      return self.dut.serialnum

   #-----------------------------------------------------------------------------
   def __SendCccAttributes(self, data,currentTemp,drive5,drive12,collectParametric):

      key,pad,blockSize,blockNum = struct.unpack(">2B2H",data[0:6])
      if DEBUG > 0:
         objMsg.printMsg("key: %d, pad: %d, blocksize: %d, blocknum: %d " %(key,pad,blockSize,blockNum,))

      #if (blockNum*blockSize)+blockSize > self.dtdFilePtr.size()

      runtBlock = self.dtdFilePtr.size() / blockSize

      if blockNum < runtBlock:
         readSize = blockSize
         notAFullRead = 0
      elif blockNum == runtBlock:
         if DEBUG > 0:
            objMsg.printMsg("Sending Runt Block")
         runtSize = self.dtdFilePtr.size() % blockSize
         readSize = runtSize
         notAFullRead = 1


      s1 = struct.pack(">2BH",63,notAFullRead,blockNum)

      self.dtdFilePtr.open('rb')
      #increment to the requested block
      self.dtdFilePtr.seek(blockNum*blockSize)

      #Read in the block data
      blockData = self.dtdFilePtr.read(readSize)
      self.dtdFilePtr.close()

      frame = s1 + blockData
      if DEBUG > 0:
         objMsg.printMsg("frame:")
         objMsg.printBin(frame)
      SendBuffer(frame,expect=('_INPROGRESS',),tag='MSG')

   def caidCallbackFunc(self,attr,default):
      if attr in self.dFuncs:
         #Return the dFunc with that name... must support a None dCAID
         return self.dFuncs[attr](None)
      else:
         if testSwitch.FE_0136005_357552_USE_ALL_FIS_ATTRS_FOR_DTD_CREATION:
            return self.dut.driveattr.get(attr,DriveAttributes.get(attr,default))
         else:
            return self.dut.driveattr.get(attr,default)

   def writeCC_DATA(self,dCAID):

      if testSwitch.FE_0136005_357552_USE_ALL_FIS_ATTRS_FOR_DTD_CREATION:
         ICmd.updateFISattrs_FW_ID()

      dtdObj = DTDFileCreator(dCAID['Info'],self.caidCallbackFunc)
      dtdObj.applyAttrSpec()
      self.dtdFilePtr = dtdObj.dtdFile

      ICmd.UnlockFactoryCmds()

      if not (( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS')):
         #In SAS MIF is init'd inside of the 595 call
         formatMIF = TP.formatMIF_Prm_638.copy()
         displayMIF = TP.displayMIF_Prm_638.copy()

         self.St(formatMIF)
         if DEBUG > 0:
            self.St(displayMIF)


      ICmd.WriteMIFDataToDisc(self.__SendCccAttributes)



      if DEBUG > 0:
         self.St(displayMIF)
         objMsg.printMsg("Display MIF from disc.")

         self.dtdFilePtr.open('rb')
         try:
            objMsg.printBin(self.dtdFilePtr.read())
         finally:
            self.dtdFilePtr.close()

   def error(self,dCAID):
      objMsg.printMsg( ' Error - CAID: %s not found' %dCAID.get('ID') )
      ScrCmds.raiseException(11044,"Invalid CAID data or command: %s" %dCAID.get('ID'))


   ## ----------- Write and Verify the Dell DeviceID label ---------------------------------------------------
   def Dell_DeviceID(self,dCAID):
      import string
      if testSwitch.FE_0193449_231166_P_DL1_SUPPORT:
         if 'DL1' in self.dut.driveattr.get(self.getScreenAttrName('DL1'), ''):
            objMsg.printMsg("DELL_DEVICE_ID DL1 already complete.")
            return

      import binascii

      ScriptComment("Dell DeviceID Write and Verify")

      if testSwitch.FE_0193449_231166_P_DL1_SUPPORT:

         deviceid = self.getCustTestSupVal2()
         if deviceid == '':
            objMsg.printMsg("No DeviceID, pls check PartNum.")
            ScrCmds.raiseException(10158,"Dell DeviceID miss out.")
      else:
         if testSwitch.virtualRun:
            DD = {self.dut.partNum: "  100030"}
         else:
            #DD = TP.DellDeviceID
            DD = getattr(TP,"DellDeviceID",{})

         if self.dut.partNum[0:10] in DD.keys():
            deviceid = DD[self.dut.partNum[0:10]]
            ScriptComment("PartNum - %s, device ID - %s" % (self.dut.partNum[0:10],deviceid))
         else:
            ScriptComment("No DeviceID, pls check PartNum.")
            ScrCmds.raiseException(10158,"Dell DeviceID miss out.")

      # Read byte 0 and byte 1 from Log Page
      self.St({'test_num':538, 'prm_name':'Read SMART log page 0x99', 'PARAMETER_0':0x2000, 'FEATURES':0xD5, 'COMMAND':0xB0, 'LBA_MID':0x4F, 'LBA_LOW':0x99, 'LBA_HIGH':0xC2, 'SECTOR_COUNT':1, 'timeout':2600}) # Read SMART log page 0x99
      self.St({'test_num':508, 'prm_name':'T508 read buffer', 'CTRL_WORD1':(0x0005), 'BYTE_OFFSET':(0,0), 'BUFFER_LENGTH':(0,512), 'timeout':360 })  # Read and display the read buffer
      self.St({'test_num':508, 'prm_name':'T508 read buffer', 'CTRL_WORD1':0x8005, 'BYTE_OFFSET':(0,0x0), 'BUFFER_LENGTH':(0,2), 'timeout':3600}) # Get DeviceID from SMART log page 0x99
      dID1 = DriveVars["Buffer Data"]
      dID = binascii.unhexlify(dID1)
      if len(dID)!= 2:
         ScriptComment("Miss out Byte 0 and Byte 1")
         byte0 = 'w'
         byte1 = '0'
      else:
         byte0 = dID[0]
         byte1 = dID[1]
      ScriptComment("Read DeviceID value from SMART Log Page 99: Byte0 - %s Byte1 - %s"%(byte0,byte1))

      DeviceID = byte0 + byte1 + deviceid.rjust(8) + " "*6
      ScriptComment("DeviceID value - %s"% DeviceID)

      if len(DeviceID) != 16:
         ScriptComment("The full DeviceID length is incorrect. Should be 16 characters.")
         ScrCmds.raiseException(10158,"Dell DeviceID length is incorrect.")

      # Write all "0x20" to write buffer, then write the DeviceID values
      self.St({'test_num':508, 'prm_name':'Write pattern to Write Buffer', 'CTRL_WORD1':0x0000, 'BYTE_OFFSET':(0,0), 'BUFFER_LENGTH':(0,1280), 'PATTERN_TYPE':(0), 'DATA_PATTERN0':(0x2020, 0x2020), 'DATA_PATTERN1':(0x2020, 0x2020), 'BYTE_PATTERN_LENGTH':(8), 'timeout':360})  # Write pattern to the Write Buffer
      w0 = int("0x" + binascii.hexlify(DeviceID[0]) + binascii.hexlify(DeviceID[1]),16)
      w1 = int("0x" + binascii.hexlify(DeviceID[2]) + binascii.hexlify(DeviceID[3]),16)
      w2 = int("0x" + binascii.hexlify(DeviceID[4]) + binascii.hexlify(DeviceID[5]),16)
      w3 = int("0x" + binascii.hexlify(DeviceID[6]) + binascii.hexlify(DeviceID[7]),16)
      self.St({'test_num':508, 'prm_name':'T508 read buffer', 'CTRL_WORD1':(0x0002), 'BYTE_OFFSET':(0,0), 'BUFFER_LENGTH':(0,8), 'PATTERN_TYPE':(0), 'DATA_PATTERN0':(w0, w1), 'DATA_PATTERN1':(w2, w3), 'BYTE_PATTERN_LENGTH':(8), 'timeout':360})  # Write Parameters
      w0 = int("0x" + binascii.hexlify(DeviceID[8]) + binascii.hexlify(DeviceID[9]),16)
      w1 = int("0x" + binascii.hexlify(DeviceID[10]) + binascii.hexlify(DeviceID[11]),16)
      w2 = int("0x" + binascii.hexlify(DeviceID[12]) + binascii.hexlify(DeviceID[13]),16)
      w3 = int("0x" + binascii.hexlify(DeviceID[14]) + binascii.hexlify(DeviceID[15]),16)
      self.St({'test_num':508, 'prm_name':'T508 read buffer', 'CTRL_WORD1':(0x0002), 'BYTE_OFFSET':(0,8), 'BUFFER_LENGTH':(0,8), 'PATTERN_TYPE':(0), 'DATA_PATTERN0':(w0, w1), 'DATA_PATTERN1':(w2, w3), 'BYTE_PATTERN_LENGTH':(8), 'timeout':360})  # Write Parameters
      self.St({'test_num':508, 'prm_name':'T508 read buffer', 'CTRL_WORD1':(0x0004), 'BYTE_OFFSET':(0,0), 'BUFFER_LENGTH':(0,512), 'timeout':360 })  # Read and display the write buffer
      self.St({'test_num':538, 'prm_name':'Write SMART log page 0x99', 'PARAMETER_0':0x2000, 'FEATURES':0xD6, 'COMMAND':0xB0, 'LBA_MID':0x4F, 'LBA_LOW':0x99, 'LBA_HIGH':0xC2, 'SECTOR_COUNT':1, 'timeout':2600}) # Write SMART log page 0x99

      self.St({'test_num':508, 'prm_name':'T508 read buffer', 'CTRL_WORD1':0x0001, 'BYTE_OFFSET':(0,0), 'BUFFER_LENGTH':(0,1280), 'PATTERN_TYPE':(0), 'DATA_PATTERN0':(0x1122, 0x3344), 'DATA_PATTERN1':(0x5566, 0x7788), 'BYTE_PATTERN_LENGTH':(8), 'timeout':360})  # Write pattern to the Read Buffer
      self.St({'test_num':508, 'prm_name':'T508 read buffer', 'CTRL_WORD1':(0x0005), 'BYTE_OFFSET':(0,0), 'BUFFER_LENGTH':(0,512), 'timeout':360 })  # Read and display the read buffer

      self.St({'test_num':538, 'prm_name':'Read SMART log page 0x99', 'PARAMETER_0':0x2000, 'FEATURES':0xD5, 'COMMAND':0xB0, 'LBA_MID':0x4F, 'LBA_LOW':0x99, 'LBA_HIGH':0xC2, 'SECTOR_COUNT':1, 'timeout':2600}) # Read SMART log page 0x99
      self.St({'test_num':508, 'prm_name':'T508 read buffer', 'CTRL_WORD1':(0x0005), 'BYTE_OFFSET':(0,0), 'BUFFER_LENGTH':(0,512), 'timeout':360 })  # Read and display the read buffer


      # Read and Verify DeviceID value from Log Page matches original data.
      if testSwitch.virtualRun:
         return
      self.St({'test_num':508, 'prm_name':'T508 read buffer', 'CTRL_WORD1':0x8005, 'BYTE_OFFSET':(0,0x0), 'BUFFER_LENGTH':(0,16), 'timeout':3600}) # Get DeviceID from SMART log page 0x99
      bD1 = DriveVars["Buffer Data"]
      bD = binascii.unhexlify(bD1)
      device_ID = bD[0]+bD[1]+bD[2]+bD[3]+bD[4]+bD[5]+bD[6]+bD[7]+bD[8]+bD[9]+bD[10]+bD[11]+bD[12]+bD[13]+bD[14]+bD[15]
      ScriptComment("device_ID value from SMART Log Page 99:  %s"%(device_ID))

      if device_ID != DeviceID:
         ScriptComment("device_ID: %s    does not match DeviceID: %s"% (device_ID, DeviceID))
         ScrCmds.raiseException(10158,"Incorrect data.")
      else:
         ScriptComment("DeviceID value has been verified to be written to SMART Log Page 99.")
         DriveAttributes['DISC_CUST_DEVICEID'] = device_ID
         if testSwitch.FE_0193449_231166_P_DL1_SUPPORT:
            self.dut.driveattr['CUST_TESTSUP_2'] = Utility.CUtility.bracketize(device_ID, 8)

   def ResetModePages(self,dCAIDS):
      """Reset mode pages back to default on SAS."""
      ICmd.resetCustomerConfiguration()

   def ResetLogPages(self,dCAIDS):
      """Clear out log pages on SAS."""
      ICmd.clearLogPages()

   def DisableLaCheck(self,dCAIDS):
      """Disable the Hitachi LaCheck feature (SAS)"""
      ICmd.disable_LA_CHECK()

   def SetSasDiscBit(self):
   # Note no dCAID arg, since this is referenced by custContent, not dFuncs.
      """Certain SAS customers (e.g. HP) require DISContinuity bit (mode page 8, byte 2, bit 4)
         set on shipped drives. A Mode Page Reset clears this bit, so this call needs to
         happen after any mode page resets."""
      objPwrCtrl.powerCycle()                # Powercycle to reload saved mode pages
      ICmd.setModePage8_DISC()

   def SetWCEBitOff(self):
   # Note no dCAID arg, since this is referenced by custContent, not dFuncs.
      """Certain SAS customers (e.g. HP) require WCE (Write Cache Enable)  bit (mode page 8, byte 2, bit 2)
         disabled on shipped drives. A Mode Page Reset clears this bit, so this call needs to
         happen after any mode page resets."""
      objPwrCtrl.powerCycle()                # Powercycle to reload saved mode pages
      ICmd.setModePage8_WCE_0()

   def CheckReconfig(self, pn):
      """ Verify if drive reconfiguration is allowed."""
      reconfigOperList = getattr(TP,'reconfigOperList',['FNC2','CRT2','MQM2','FIN2','CUT2'])
      if not objDut.nextOper in reconfigOperList:
         return
      elif not hasattr(PIF,"Reconfig_Niblet_Check"):
         ScrCmds.raiseException(14207,"'Reconfig_Niblet_Check' table not found in PIF!")
      try:
         nibletLevel = int(DriveAttributes.get('NIBLET_LEVEL',0))
      except:  # handle 'NONE' value
         nibletLevel = 0
      if testSwitch.virtualRun:
         nibletLevel = 3

      nibletReconfigPIF = PIF.Reconfig_Niblet_Check
      for pnMatch in nibletReconfigPIF:
         regVal = re.compile(pnMatch)
         if regVal.search(pn):
            nibletReconfigValue = int(nibletReconfigPIF[pnMatch])
            objMsg.printMsg("%s reconfig niblet found." %pnMatch)
            break
      else:
         nibletReconfigValue = 3
         objMsg.printMsg("%s reconfig niblet value not found! Use default value = %s." %(pn, nibletReconfigValue))

      msg = "%s NIBLET_LEVEL = %s. Reconfig niblet level = %s. %s."
      if nibletReconfigValue > nibletLevel:
         ScrCmds.raiseException(10253, msg %(pn, nibletLevel, nibletReconfigValue, "FAILED" ))
      objMsg.printMsg(msg % (pn, nibletLevel, nibletReconfigValue, "PASSED" ))


   if testSwitch.FE_0152759_231166_P_ADD_ROBUST_PN_SN_SEARCH_AND_VALIDATION:
      def validateFIS_HDA_SN(self, dut = None, params = {}):
         """
         Force validation of SN
         """
         if objRimType.IOInitRiser():
            hdaSN = ICmd.GetDriveSN(self.dut.partNum, partNumOnlyValue = True)
         else:
            hdaSN = self.dut.IdDevice['IDSerialNumber']
         sysSN = self.dut.serialnum

         if sysSN != hdaSN and not testSwitch.virtualRun:
            ScrCmds.raiseException(13420, "IdentifyDevice SerialNum mismatch: ID: %s != SYS: %s" % (hdaSN, sysSN,))

   def getLenovoSN(self):
      objMsg.printMsg("DCMServer Request for Lenovo_SN.  SN: %s    Part Number:  %s"%(HDASerialNumber, self.dut.partNum))
      HostRetries = 4
      while HostRetries >= 0:
         if testSwitch.virtualRun:
            retVal = ['a',{'EC': [0,0,0],
                      'DATA': ['CUST_SERIAL:=:8S5XX1L23456S1UB4200000']}]
         else:
            retVal = RequestService("DCMServerRequest", ("GetLenovo_SN",(self.dut.serialnum, self.dut.partNum)))

         ec = retVal[1]['EC'][0]
         if ec == 0:
            break
         else:

            time.sleep(30)
         HostRetries -= 1
      else:
         ScrCmds.raiseException(11044, 'Host Communication Error: %s' % (retVal,))

      for val in retVal[1]['DATA']:
         if val.startswith('CUST_SERIAL'):
            CUST_SERIAL = val.split(':=:',1)[1]
            self.dut.driveattr['CUST_SERIAL'] = CUST_SERIAL
            return CUST_SERIAL
      else:
         ScrCmds.raiseException(11044, 'No CUST_SERIAL found in %s' % (retVal,))


   def Lenovo_8S_SN(self,dut, params={}):

      import serialScreen, sptCmds

      if 'LV1' in self.dut.driveattr.get(self.getScreenAttrName('LV1'), ''):
         objMsg.printMsg("Lenovo LV1 already complete.")
         return

      custSerial = self.getLenovoSN().strip()
      objMsg.printMsg("custSerial: %s, custSerial[0:2]: %s" % (custSerial,custSerial[0:2]))
      nonProductionSite = False
      if custSerial[0:2] != '8S':
         nonProductionSite = True

      sptCmds.enableDiags()

      oSer = serialScreen.sptDiagCmds()
      oSer.setCAPValue('LENOVO_8S', custSerial)
      oSer.saveSegmentToFlash(0) # save cap

      objMsg.printMsg("###### Readback Lenovo8S ######")
      sptCmds.sendDiagCmd(CTRL_T) # switch to Eslip mode
      logData = ICmd.ReadLenovo8S()
      objMsg.printMsg("Lenovo8S Log DF:")
      objMsg.printBin(logData)

      df_custSerial = logData[20:50].strip()
      df_newcustSer = logData[110:140].strip()
      objMsg.printMsg("org_sn: %s new_sn: %s" %(df_custSerial, df_newcustSer))

      if nonProductionSite:
         objMsg.printMsg("Lenovo non production site code triggered!")
         df_custSerial = df_custSerial[:len(custSerial)]
         df_newcustSer = df_newcustSer[:len(custSerial)]

      if df_custSerial != custSerial:
         ScrCmds.raiseException(10158, "Lenovo Cust serial mismatch ('%s' != '%s')" % (df_custSerial, custSerial))


      if df_newcustSer != custSerial:
         ScrCmds.raiseException(10158, "Lenovo Cust serial 'new' mismatch (%s != %s)" % (df_newcustSer , custSerial))

      objMsg.printMsg("Lenovo 8S Validated %s" % (custSerial,))
