#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Classes to setup the executable scripts, err handling and dnld codes for a particular config
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/15 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Setup.py $
# $Revision: #22 $
# $DateTime: 2016/12/15 19:55:01 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Setup.py#22 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import os,sys,time, traceback, re, types, struct
from Drive import objDut
import Codes
from Rim import objRimType, theRim

import ScrCmds
import FSO, Utility
import MessageHandler as objMsg

try:
   from tabledictionary import tableHeaders, tableRevision
   tableDictSupport = 1
except:
   from parametricdictionary import tableHeaders, tableRevision
   import parametricdictionary
   tableDictSupport = 0
from CTMX import CTMX
from PowerControl import objPwrCtrl
from TestParamExtractor import TP

if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
   import base_RecoveryTest


#**********************************************************************************************************
#**********************************************************************************************************
class CSetup(object):
   #------------------------------------------------------------------------------------------------------#
   def __init__(self, refStartTime = 0):
      self.dut = objDut
      self.genExcept = ''

      self.startRef = self.createStartStateData()
      self.dut.GOTFRetest = {}
      self.dut.RetestLastErr = None
      self.dut.RetestPN = None
      self.dut.SubNextState = ""    # test module within one test state

   #------------------------------------------------------------------------------------------------------#
   def initializeComponents(self):
      # DriveAttributes['SF3CODE'] = '8C'
      # DriveAttributes['DEPOP_REQ'] = 'NONE'
      # DriveAttributes['DEPOP_DONE'] = 'NONE'
      # DriveAttributes['WATERFALL_REQ'] = 'NONE'
      # DriveAttributes['NIBLET_STRING'] = 'NONE'
      # DriveAttributes['WTF'] = 'D0R0'
      ScrCmds.insertHeader("Initializing Components")
      # Initialize components
      from CodeVer import theCodeVersion

      from Carrier import theCarrier
      from Cell import theCell


      try:
         try:
            try:
               theRim.initRim()
            except:
               ScrCmds.statMsg("Retry initRim")
               theRim.initRim()
            theCell.initCell()
            theCarrier.initCarrier()
            theCarrier.YS() # yield script at start of test to init all port(s)
            TP.setDut(self.dut)
            self.dut.initializeDut()
         except:
            self.dut.initializeDut()   # fix DriveAttribute errors during rim/cell init failures
            raise

         if testSwitch.FE_0131335_220554_NEW_AUD_LODT_FLOW:
            if self.dut.ExtraOper:
               ScrCmds.statMsg("Jump over initializeComponents - Should run LODT/AUD flow")
               return
         else:
            if self.dut.LODT:
               ScrCmds.statMsg("Jump over initializeComponents - Should run LODT flow")
               return
         theCell.enableDynamicRimType()
         self.dut.statesExec[self.dut.nextOper] = []
         self.dut.statesSkipped[self.dut.nextOper] = []
         self.oFileSysObj = FSO.CFSO()
         self.oFileSysObj.setParamCD(getattr(TP,'paramFileNameDict',{}))
         theCodeVersion.updatePF3Code()
         #self.PRE2DriveAttrReset() # reset attr at begining of PRE2 - knl 16Apr08
         self.PreOpCheck()          #Pre operation checks such as proqual and FNG2 check
         self.packageControl()

         if not self.dut.powerLossEvent:  self.DriveAttrTag(mode='start') # User controlled attribute stamping. Definition in PIF.py

         ScrCmds.statMsg('Testing from OPERATION: %s, STATE: %s' % (self.dut.nextOper, self.dut.nextState))
         self.writeHeader()

         #Enable early temp validation and ramping w/o wait in case request service takes a while
         if not getattr(TP,'temp_profile',{self.dut.nextOper:0}).get(self.dut.nextOper,0) == 0 and \
            not ConfigVars[CN].get('BenchTop',0) == 1 and not objRimType.IsPSTRRiser():
            theCell.setFanSpeed(self.dut.nextOper)
            if int(DriveAttributes.get('3TempMove_ENABLE','0')) == 0  and ConfigVars[CN].get('DYNAMIC_RIM_TYPE',0) == 0:
               if not testSwitch.virtualRun and not testSwitch.winFOF and testSwitch.FE_0163145_470833_P_NEPTUNE_SUPPORT_PROC_CTRL20_21:
                  tcData = GetTempCtrlData()
                  posRate,negRate = struct.unpack(">2h",tcData[40:44])
                  ScrCmds.statMsg("Before posRate=%s negRate=%s" % (posRate,negRate))
                  ScrCmds.statMsg("Current cell temperature is "+str(ReportTemperature()/10.0)+"C.")
                  if objRimType.isNeptuneRiser():
                     SetTemperatureLimits(positiveRampRate=30, negativeRampRate=20)

                     if hasattr(TP,'ThermalCoefficients'):
                        cms_family = DriveAttributes.get('CMS_FAMILY', '')
                        ScrCmds.statMsg("CMS Family=%s" % (cms_family))
                        TC = 'NONE'

                        for key in TP.ThermalCoefficients:
                           if DEBUG:   ScrCmds.statMsg("Key=%s Value=%s" % (key,TP.ThermalCoefficients[key]))
                           if cms_family in TP.ThermalCoefficients[key]:
                              TC = key
                              break

                        if not TC == 'NONE':
                           ScrCmds.statMsg("Thermal Coefficient=%s" % (TC))

                           if TC == 'SFF5mmTC' :
                              ScrCmds.statMsg('Setting Thermal Coefficient (%s) for 5mm Product' %(TC))
                              SetThermalCoefficients(SFF5mmTC)
                           elif TC == 'MobileTC' :
                              ScrCmds.statMsg('Setting Thermal Coefficient (%s) for Mobile Product' %(TC))
                              SetThermalCoefficients(MobileTC)
                           elif TC == 'CutoutTC' :
                              ScrCmds.statMsg('Setting Thermal Coefficient (%s) for SKDC Product' %(TC))
                              SetThermalCoefficients(CutoutTC)
                           elif TC == 'EnterpriseTC' :
                              ScrCmds.statMsg('Setting Thermal Coefficient (%s) for Enterprise Product' %(TC))
                              SetThermalCoefficients(EnterpriseTC)
                           elif TC == 'CoverSealTC' :
                              ScrCmds.statMsg('Setting Thermal Coefficient (%s) for Product with cover seal' %(TC))
                              SetThermalCoefficients(CoverSealTC)
                           else:
                              ScrCmds.statMsg("Undefinied Thermal Coefficient (%s), Using default Thermal Coefficient" %(TC))
                        else:
                           ScrCmds.statMsg("Using default Thermal Coefficient")
                     else:
                        ScrCmds.statMsg("TP.ThermalCoefficients not found, using default Thermal Coefficient")

               RampToTempNoWait(TP.temp_profile[self.dut.nextOper][0]*10)
               ScrCmds.statMsg("Starting ramp to %d w/o wait." % (TP.temp_profile[self.dut.nextOper][0],))
               if not testSwitch.virtualRun and not testSwitch.winFOF and testSwitch.FE_0163145_470833_P_NEPTUNE_SUPPORT_PROC_CTRL20_21:
                  tcData = GetTempCtrlData()
                  posRate,negRate = struct.unpack(">2h",tcData[40:44])
                  ScrCmds.statMsg("After posRate=%s negRate=%s" % (posRate,negRate))

      finally:
         # Exec request service anyway so we log the error under the correct oper
         self.callRequestService()

         if testSwitch.FORCE_IO_FIN2:
            ScrCmds.statMsg('Setting IOFIN2_PENDING = NONE')
            DriveAttributes["IOFIN2_PENDING"] = "NONE"

         ScrCmds.insertHeader("Initializing Components Complete")

   #------------------------------------------------------------------------------------------------------#
   def setup(self):
      if testSwitch.FE_0131335_220554_NEW_AUD_LODT_FLOW:
         if self.dut.ExtraOper:
            ScrCmds.statMsg("Jump over setup - Should run LODT/AUD flow")
            return
      else:
         if self.dut.LODT:
            ScrCmds.statMsg("Jump over setup - Should run LODT flow")
            return
      self.checkOperation()

      if testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
         self.dut.buildFileList()  # for dictionary style codes.py file
      else:
         self.buildFileList()      # for dictionary style codes.py file
      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT and self.dut.driveattr['ORG_TIER'] == 'NONE' and self.dut.nextOper == 'PRE2':
         import CommitServices
         if CommitServices.isTierPN( self.dut.partNum ):
            self.dut.driveattr['ORG_TIER'] = CommitServices.getTab( self.dut.partNum )
            ScrCmds.statMsg("ORG_TIER = %s" % self.dut.driveattr['ORG_TIER'])

      if testSwitch.FE_0122824_231166_ADD_LATENT_SETUP_TO_DUT:

         DEF_FLG_OPER_RESOLUTION = {
            'PRE2'   : 'STP',
            'CAL2'   : 'STP',
            'FNC'    : 'STP',
            'FNC2'   : 'STP',
            'SPSC2'  : 'TGTP',
            'FIN2'   : 'TGTP',
            'BRO'    : 'TGTP',
            'STC'    : 'TGTP',
            'CMT2'   : 'TGTP',
            'IOSC2'  : 'TGTP',
            'AUD2'   : 'TGTP',
            'CUT2'   : 'TGTP',
            'TODT'   : 'TGTP',
            }

         DEF_FLG_OPER_RESOLUTION.update({'CRT2' : 'STP'})
         DEF_FLG_OPER_RESOLUTION.update({'SDAT2' : 'STP'})

         from  PackageResolution import PackageDispatcher
         pd = PackageDispatcher(self.dut, DEF_FLG_OPER_RESOLUTION.get(self.dut.nextOper,  'STP'))
         fileName = pd.getFileName()
         if pd and pd.flagFileName:
            testSwitch.importExternalFlags(pd.flagFileName)

         self.dut.setup()
      self.dut.controlship()
      from PowerControl import objPwrCtrl
      objPwrCtrl.CheckInitiator()

      # if testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM:
         # #Update singleton with cfg handler
         # from PIFHandler import CPIFHandler
         # from CustomCfg import CCustomCfg
         # CPIFHandler(CustConfig = CCustomCfg())

      if not testSwitch.FE_0135432_426568_REMOVE_CALL_TO_RWK_YIELD_MANAGER:
         if self.dut.nextOper == 'PRE2':
            self.rwkYieldMonitor()

      finDict = self.createFinalTestTimeByStateDict(startDict = self.startRef, endDict = self.createEndStateData())
      self.dut.dblData.Tables('TEST_TIME_BY_STATE').addRecord(finDict)

   def createStartStateData(self):
      memVals = objMsg.getMemVals()

      return {
         'START_TIME' : time.time(),
         'SZ_START' : memVals.get('VSZ',''),
         'RSS_START' : memVals.get('RSS',''),
         'CPU_TIME': objMsg.getCpuEt(force = True),
         'SZ_END': 0,
         'RSS_END': 0,
      }

   def createEndStateData(self):
      memVals = objMsg.getMemVals()

      return {
         'OPER' : self.dut.nextOper,
         'CPU_TIME': objMsg.getCpuEt(force = True),
         'SZ_END': memVals.get('VSZ',''),
         'RSS_END': memVals.get('RSS',''),
         'END_TIME': time.time(),
      }

   def createFinalTestTimeByStateDict(self, segment = "START", seq = -1, startDict = None, endDict = None):

      def createDateStr(tempTime):
         date = time.localtime(tempTime)     # Get current time in a formatted tuple
         return "%02d/%02d/%04d %02d:%02d:%02d" % (date[1],date[2],date[0],date[3],date[4],date[5])


      return {
         'OPER' : self.dut.nextOper,
         'STATE_NAME' : segment,
         'SEQ' : seq,
         'START_TIME' : createDateStr(startDict['START_TIME']),
         'END_TIME': createDateStr(endDict['END_TIME']),
         'ELAPSED_TIME': endDict['END_TIME'] - startDict['START_TIME'],
         'SZ_START' : startDict['SZ_START'],
         'RSS_START' : startDict['RSS_START'],
         'CPU_ELAPSED_TIME':  '%0.2f' % (endDict['CPU_TIME'] - startDict['CPU_TIME']),
         'SZ_END': endDict['SZ_END'],
         'RSS_END': endDict['RSS_END'],
      }

   #------------------------------------------------------------------------------------------------------#
   def checkOperation(self):
      if self.dut.nextOper not in self.dut.operList:
         ScrCmds.raiseException(11187, "Operation %s not found in operList" % str(self.dut.nextOper))

      if (self.dut.nextOper is 'IDT2') and not (objRimType.CPCRiser(ReportReal = True) or objRimType.IOInitRiser()):
         RequestService('SetOperation',("*%s" % self.dut.nextOper,))
         ScrCmds.raiseException(11187, "IDT2 Oper not allowed in Serial Only cell")

      # Block IO operation from running in serial cells during bench test
      if objRimType.SerialOnlyRiser() and not self.dut.certOper and testSwitch.NoIO == 0:
         ScrCmds.raiseException(11187, "%s operation  not supported to run in serial cells!" %self.dut.nextOper)

      if testSwitch.proqualCheck:
         # If operation is not PRE2 and if there is more than 1 operation in the list and
         # if current operation is NOT the 1st operation in the list
         # then check if ALL the previous Operations has been completed and PASS
         if (not self.dut.nextOper == "SCOPY") and (len(self.dut.operList) > 1) and (self.dut.operList.index(self.dut.nextOper)):
            for oper in self.dut.operList[:self.dut.operList.index(self.dut.nextOper)]:
               if oper in ["SDAT2",] and testSwitch.BF_0171907_470833_IGNORE_SDAT2_IN_PROQUAL_CHK:
                  continue
               if (oper == "SCOPY" or oper == "STS") and self.dut.driveattr['SCOPY_TYPE'] == 'MDW':
                  ScrCmds.statMsg('%s skipped, %s_TEST_DONE = %s' % (oper, oper, DriveAttributes.get('%s_TEST_DONE' % oper.upper(), 'NONE')))
               elif not DriveAttributes.get('%s_TEST_DONE'%oper.upper(),'NONE') == "PASS":
                  pass
                  #ScrCmds.raiseException(10382, "Invalid Operation, drive did not complete %s, %s_TEST_DONE = %s" % (oper, oper, DriveAttributes.get('%s_TEST_DONE'%oper.upper(),'NONE')))
               else:
                  ScrCmds.statMsg('%s_TEST_DONE = %s' % (oper,DriveAttributes.get('%s_TEST_DONE'%oper.upper(),'NONE')))
            else:
               ScrCmds.statMsg('Operation: %s, Proqual OK' % str(self.dut.nextOper))
         elif self.dut.nextOper == "CCV2":
            if not (DriveAttributes.get('FIN2_TEST_DONE','NONE') == "PASS" and (DriveAttributes.get('IDT_TEST_DONE','NONE') == "PASS" or DriveAttributes.get('GIO_TEST_DONE','NONE') == "PASS")):
               ScrCmds.raiseException(10382, "For CCV2 Operation, drive did not complete prior operations. FIN2_TEST_DONE %s, IDT_TEST_DONE %s" % (DriveAttributes.get('FIN2_TEST_DONE','NONE'), DriveAttributes.get('IDT2_TEST_DONE','NONE')))
            else:
               CLN2_cmpl = DriveAttributes.get('CLN2_TEST_DONE','NONE') #FIN2 -> IDT2 -> CLN2 -> CCV2
               if CLN2_cmpl != 'NONE' and CLN2_cmpl != "PASS":
                  ScrCmds.raiseException(10382, "For CCV2 Operation, drive did not complete prior operation. CLN2_TEST_DONE %s" % (CLN2_cmpl, ))
               else:
                  objMsg.printMsg("Drive completed prior operations. Run CCV2")

   #------------------------------------------------------------------------------------------------------#

   if not testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
      #objMsg.printMsg("Debug using default  buildFileList")

      def cleanCodesDictCmsWilds(self):
         """
         Procedure to clean the Codes.fwConfig CMS wildcards
            and convert them to regex values
         """
         for key,value in Codes.fwConfig.items():
            if key.find('%') > -1:
               Codes.fwConfig[Utility.convertCmsWildCardToRe(key)] = value
               del Codes.fwConfig[key]


      def buildFileList(self):
         internalPN = self.dut.partNum
         if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
            self.cleanCodesDictCmsWilds()
         objMsg.printMsg("Codes.fwConfig = \n%s" % (Codes.fwConfig,))
         # TT: ENH-00254: select codes based on full p/n rather than base p/n
         try:
            fwCodeConfig = Codes.fwConfig
            #if testSwitch.AGC_SCRN_DESTROKE_WITH_NEW_RAP and self.dut.driveattr['DESTROKE_REQ'] == 'DSD_ID':
            ''' Dual rap files selection is handled in the PackageResolution.py
            if testSwitch.AGC_SCRN_DESTROKE_WITH_NEW_RAP and \
               self.dut.driveattr['DESTROKE_REQ'] == 'DSD_NEW_RAP':
               fwCodeConfig = Codes.fwConfigDSD
            '''
            if DriveAttributes.get('SF3CODE','NONE') == '8C':     #auto detect family is 8C
               fwCodeConfig['1RK172-995']['INCP'] = Codes.fwConfig8C['1RK172-995']['INCP']
               fwCodeConfig['1RK172-995']['RSSP'] = Codes.fwConfig8C['1RK172-995']['RSSP']
               fwCodeConfig['1RK172-995']['STP']  = Codes.fwConfig8C['1RK172-995']['STP']
               fwCodeConfig['1RK172-995']['STPB'] = Codes.fwConfig8C['1RK172-995']['STPB']
               fwCodeConfig['1RK172-995']['SFWP'] = Codes.fwConfig8C['1RK172-995']['SFWP']
               fwCodeConfig['1RK172-995']['TGTB'] = Codes.fwConfig8C['1RK172-995']['TGTB']
               fwCodeConfig['1RK172-995']['TGTP'] = Codes.fwConfig8C['1RK172-995']['TGTP']

               fwCodeConfig['1RK17C-995']['INCP'] = Codes.fwConfig8C['1RK17C-995']['INCP']
               fwCodeConfig['1RK17C-995']['RSSP'] = Codes.fwConfig8C['1RK17C-995']['RSSP']
               fwCodeConfig['1RK17C-995']['STP']  = Codes.fwConfig8C['1RK17C-995']['STP']
               fwCodeConfig['1RK17C-995']['STPB'] = Codes.fwConfig8C['1RK17C-995']['STPB']
               fwCodeConfig['1RK17C-995']['SFWP'] = Codes.fwConfig8C['1RK17C-995']['SFWP']
               fwCodeConfig['1RK17C-995']['TGTB'] = Codes.fwConfig8C['1RK17C-995']['TGTB']
               fwCodeConfig['1RK17C-995']['TGTP'] = Codes.fwConfig8C['1RK17C-995']['TGTP']
               
               fwCodeConfig['1RK17D-995']['INCP'] = Codes.fwConfig8C['1RK17D-995']['INCP']
               fwCodeConfig['1RK17D-995']['RSSP'] = Codes.fwConfig8C['1RK17D-995']['RSSP']
               fwCodeConfig['1RK17D-995']['STP']  = Codes.fwConfig8C['1RK17D-995']['STP']
               fwCodeConfig['1RK17D-995']['STPB'] = Codes.fwConfig8C['1RK17D-995']['STPB']
               fwCodeConfig['1RK17D-995']['SFWP'] = Codes.fwConfig8C['1RK17D-995']['SFWP']
               fwCodeConfig['1RK17D-995']['TGTB'] = Codes.fwConfig8C['1RK17D-995']['TGTB']
               fwCodeConfig['1RK17D-995']['TGTP'] = Codes.fwConfig8C['1RK17D-995']['TGTP']

               fwCodeConfig['1RK171-995']['INCP'] = Codes.fwConfig8C['1RK171-995']['INCP']
               fwCodeConfig['1RK171-995']['RSSP'] = Codes.fwConfig8C['1RK171-995']['RSSP']
               fwCodeConfig['1RK171-995']['STP']  = Codes.fwConfig8C['1RK171-995']['STP']
               fwCodeConfig['1RK171-995']['STPB'] = Codes.fwConfig8C['1RK171-995']['STPB']
               fwCodeConfig['1RK171-995']['SFWP'] = Codes.fwConfig8C['1RK171-995']['SFWP']
               fwCodeConfig['1RK171-995']['TGTB'] = Codes.fwConfig8C['1RK171-995']['TGTB']
               fwCodeConfig['1RK171-995']['TGTP'] = Codes.fwConfig8C['1RK171-995']['TGTP']
               
               fwCodeConfig['1RK17A-995']['INCP'] = Codes.fwConfig8C['1RK17A-995']['INCP']
               fwCodeConfig['1RK17A-995']['RSSP'] = Codes.fwConfig8C['1RK17A-995']['RSSP']
               fwCodeConfig['1RK17A-995']['STP']  = Codes.fwConfig8C['1RK17A-995']['STP']
               fwCodeConfig['1RK17A-995']['STPB'] = Codes.fwConfig8C['1RK17A-995']['STPB']
               fwCodeConfig['1RK17A-995']['SFWP'] = Codes.fwConfig8C['1RK17A-995']['SFWP']
               fwCodeConfig['1RK17A-995']['TGTB'] = Codes.fwConfig8C['1RK17A-995']['TGTB']
               fwCodeConfig['1RK17A-995']['TGTP'] = Codes.fwConfig8C['1RK17A-995']['TGTP']
               
               fwCodeConfig['1R8174-995']['INCP'] = Codes.fwConfig8C['1R8174-995']['INCP']
               fwCodeConfig['1R8174-995']['RSSP'] = Codes.fwConfig8C['1R8174-995']['RSSP']
               fwCodeConfig['1R8174-995']['STP']  = Codes.fwConfig8C['1R8174-995']['STP']
               fwCodeConfig['1R8174-995']['STPB'] = Codes.fwConfig8C['1R8174-995']['STPB']
               fwCodeConfig['1R8174-995']['SFWP'] = Codes.fwConfig8C['1R8174-995']['SFWP']
               fwCodeConfig['1R8174-995']['TGTB'] = Codes.fwConfig8C['1R8174-995']['TGTB']
               fwCodeConfig['1R8174-995']['TGTP'] = Codes.fwConfig8C['1R8174-995']['TGTP']
               
               fwCodeConfig['1R817G-995']['INCP'] = Codes.fwConfig8C['1R817G-995']['INCP']
               fwCodeConfig['1R817G-995']['RSSP'] = Codes.fwConfig8C['1R817G-995']['RSSP']
               fwCodeConfig['1R817G-995']['STP']  = Codes.fwConfig8C['1R817G-995']['STP']
               fwCodeConfig['1R817G-995']['STPB'] = Codes.fwConfig8C['1R817G-995']['STPB']
               fwCodeConfig['1R817G-995']['SFWP'] = Codes.fwConfig8C['1R817G-995']['SFWP']
               fwCodeConfig['1R817G-995']['TGTB'] = Codes.fwConfig8C['1R817G-995']['TGTB']
               fwCodeConfig['1R817G-995']['TGTP'] = Codes.fwConfig8C['1R817G-995']['TGTP']
               
               fwCodeConfig['1R8172-995']['INCP'] = Codes.fwConfig8C['1R8172-995']['INCP']
               fwCodeConfig['1R8172-995']['RSSP'] = Codes.fwConfig8C['1R8172-995']['RSSP']
               fwCodeConfig['1R8172-995']['STP']  = Codes.fwConfig8C['1R8172-995']['STP']
               fwCodeConfig['1R8172-995']['STPB'] = Codes.fwConfig8C['1R8172-995']['STPB']
               fwCodeConfig['1R8172-995']['SFWP'] = Codes.fwConfig8C['1R8172-995']['SFWP']
               fwCodeConfig['1R8172-995']['TGTB'] = Codes.fwConfig8C['1R8172-995']['TGTB']
               fwCodeConfig['1R8172-995']['TGTP'] = Codes.fwConfig8C['1R8172-995']['TGTP']
               
               fwCodeConfig['1R817C-995']['INCP'] = Codes.fwConfig8C['1R817C-995']['INCP']
               fwCodeConfig['1R817C-995']['RSSP'] = Codes.fwConfig8C['1R817C-995']['RSSP']
               fwCodeConfig['1R817C-995']['STP']  = Codes.fwConfig8C['1R817C-995']['STP']
               fwCodeConfig['1R817C-995']['STPB'] = Codes.fwConfig8C['1R817C-995']['STPB']
               fwCodeConfig['1R817C-995']['SFWP'] = Codes.fwConfig8C['1R817C-995']['SFWP']
               fwCodeConfig['1R817C-995']['TGTB'] = Codes.fwConfig8C['1R817C-995']['TGTB']
               fwCodeConfig['1R817C-995']['TGTP'] = Codes.fwConfig8C['1R817C-995']['TGTP']
               
               fwCodeConfig['1R817D-995']['INCP'] = Codes.fwConfig8C['1R817D-995']['INCP']
               fwCodeConfig['1R817D-995']['RSSP'] = Codes.fwConfig8C['1R817D-995']['RSSP']
               fwCodeConfig['1R817D-995']['STP']  = Codes.fwConfig8C['1R817D-995']['STP']
               fwCodeConfig['1R817D-995']['STPB'] = Codes.fwConfig8C['1R817D-995']['STPB']
               fwCodeConfig['1R817D-995']['SFWP'] = Codes.fwConfig8C['1R817D-995']['SFWP']
               fwCodeConfig['1R817D-995']['TGTB'] = Codes.fwConfig8C['1R817D-995']['TGTB']
               fwCodeConfig['1R817D-995']['TGTP'] = Codes.fwConfig8C['1R817D-995']['TGTP']
               
               fwCodeConfig['1R8171-995']['INCP'] = Codes.fwConfig8C['1R8171-995']['INCP']
               fwCodeConfig['1R8171-995']['RSSP'] = Codes.fwConfig8C['1R8171-995']['RSSP']
               fwCodeConfig['1R8171-995']['STP']  = Codes.fwConfig8C['1R8171-995']['STP']
               fwCodeConfig['1R8171-995']['STPB'] = Codes.fwConfig8C['1R8171-995']['STPB']
               fwCodeConfig['1R8171-995']['SFWP'] = Codes.fwConfig8C['1R8171-995']['SFWP']
               fwCodeConfig['1R8171-995']['TGTB'] = Codes.fwConfig8C['1R8171-995']['TGTB']
               fwCodeConfig['1R8171-995']['TGTP'] = Codes.fwConfig8C['1R8171-995']['TGTP']
               
               fwCodeConfig['1R817A-995']['INCP'] = Codes.fwConfig8C['1R817A-995']['INCP']
               fwCodeConfig['1R817A-995']['RSSP'] = Codes.fwConfig8C['1R817A-995']['RSSP']
               fwCodeConfig['1R817A-995']['STP']  = Codes.fwConfig8C['1R817A-995']['STP']
               fwCodeConfig['1R817A-995']['STPB'] = Codes.fwConfig8C['1R817A-995']['STPB']
               fwCodeConfig['1R817A-995']['SFWP'] = Codes.fwConfig8C['1R817A-995']['SFWP']
               fwCodeConfig['1R817A-995']['TGTB'] = Codes.fwConfig8C['1R817A-995']['TGTB']
               fwCodeConfig['1R817A-995']['TGTP'] = Codes.fwConfig8C['1R817A-995']['TGTP']

            if HDASerialNumber[1:4] in ['ESK']:
               fwCodeConfig['1RK172-995']['SFWP'] = fwCodeConfig['1RK171-995']['SFWP']
               fwCodeConfig['1RK172-995']['SFWP'] = fwCodeConfig['1RK171-995']['SFWP']
               fwCodeConfig['1RK17C-995']['SFWP'] = fwCodeConfig['1RK171-995']['SFWP']
               fwCodeConfig['1RK17C-995']['SFWP'] = fwCodeConfig['1RK171-995']['SFWP']
               fwCodeConfig['1RK17D-995']['SFWP'] = fwCodeConfig['1RK171-995']['SFWP']
               fwCodeConfig['1RK17D-995']['SFWP'] = fwCodeConfig['1RK171-995']['SFWP']
               
            if testSwitch.FE_0145180_357260_P_BROKER_PROCESS:
               try:
                  self.codeDictToSearch = fwCodeConfig[self.dut.partNum]
               except:
                  self.codeDictToSearch = fwCodeConfig['broker']
            elif testSwitch.FE_0149593_357260_SEAGATE_THERMAL_CHAMBER:
               self.codeDictToSearch = fwCodeConfig['STCstc']
            elif testSwitch.FE_SGP_AUTO_SF3_CODEDL_SELECTION_VIA_HGA_SUPPLIER:
               if (fwCodeConfig[self.dut.partNum].has_key('STPT')) and (self.dut.HGA_SUPPLIER == 'TDK'):
                  ScrCmds.statMsg("Adding STP for Single Heater Code TDK heads")
                  fwCodeConfig[self.dut.partNum]['STP'] = fwCodeConfig[self.dut.partNum]['STPT']
                  #testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT = 0
                  #del Codes.fwConfig[self.dut.partNum]['STPT']
               elif (fwCodeConfig[self.dut.partNum].has_key('STPR')) and (self.dut.HGA_SUPPLIER == 'RHO'):
                  ScrCmds.statMsg("Adding STP for Dual Heater Code RHO heads")
                  fwCodeConfig[self.dut.partNum]['STP'] = fwCodeConfig[self.dut.partNum]['STPR']
                  #testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT = 1
                  #del Codes.fwConfig[self.dut.partNum]['STPR']
               elif not testSwitch.virtualRun == 1:
                  ScrCmds.raiseException(10345, "FwConfig: PN=%s not found in Codes.py" % (self.dut.partNum,))
               self.codeDictToSearch = fwCodeConfig[self.dut.partNum]
            else:
               if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
                  objMsg.printMsg("Looking for %s" % internalPN)
                  #tierPN, tier = CommitServices.convertPNtoTier(self.dut.partNum)
                  self.codeDictToSearch = Utility.getSortedRegexMatch(internalPN, Codes.fwConfig)
                  #self.codeDictToSearch.update(Utility.getSortedRegexMatch(tierPN, Codes.fwConfig))
               else:
                  self.codeDictToSearch = fwCodeConfig[self.dut.partNum]

         except:
            if not testSwitch.virtualRun == 1:
               ScrCmds.raiseException(10345, "FwConfig: PN=%s not found in Codes.py" % (self.dut.partNum,))
            else:
               self.codeDictToSearch = {'TPM':'dummy'}

         self.buildCustomFWList()

         if testSwitch.FE_0174482_231166_P_USE_INC_CODE_BY_SOC_TYPE:
            #Add SOC type to the codeDictToSearch
            socFiles = getattr(Codes, 'socFiles', False)
            if socFiles:
               incCode = socFiles.get(objRimType.getRiserSOCType(), False)
               if incCode:
                  self.codeDictToSearch['INCP'] = incCode
               else:
                  objMsg.printMsg("INC Code type of %s not supported in Codes.py" % (objRimType.getRiserSOCType(),))
            else:
               objMsg.printMsg("No socFiles dict in Codes.py")

         missingFileList = [] # list of missing dnld and support files

         # check if missing firmware files, append files to config list
         for codeType,codeFileName in self.codeDictToSearch.items(): # iterate through dictionary
            #For furture scale-ability we will assume handling for all types being a list.
            if not type(codeFileName) in [types.ListType, types.TupleType]:
               #Convert base file to an iterable so iteration is the same.
               codeFileList = [codeFileName]
            else:
               codeFileList = list(codeFileName)
            self.dut.codes[codeType] = codeFileList

            #Iterate over all files in the codetype list
            for codesFileName in codeFileList:
               #Zip files are expanded upon config preperation in the CM so we can't look for a physical version of them
               zipMultiPat = '(%s)(\.[zipZIP]{3})'
               zipMatch = re.search(zipMultiPat % '\S*',codesFileName)
               if zipMatch == None:
                  for fileName in self.getAlternateFileNames(codesFileName):
                     filePath = os.path.join(ScrCmds.getSystemDnldPath(), fileName)
                     if os.path.isfile(filePath) and fileName in os.listdir(ScrCmds.getSystemDnldPath()):
                        fileIndex = self.dut.codes[codeType].index(codesFileName)
                        self.dut.codes[codeType][fileIndex] = fileName
                        break
                  else:
                     missingFileList.append(codesFileName)

         # check if missing support dlfile files
         try:
            for dlType,dlFile in Codes.dlConfig.items():
               for fileName in self.getAlternateFileNames(dlFile):
                  filePath = os.path.join(ScrCmds.getSystemDnldPath(), fileName)
                  if os.path.isfile(filePath) and fileName in os.listdir(ScrCmds.getSystemDnldPath()):
                     self.dut.codes[dlType] = fileName
                     break
               else:
                  self.dut.codes[dlType] = fileName
                  missingFileList.append(dlFile)
         except:
            pass

         ScrCmds.insertHeader("Firmware for PN %s" % self.dut.partNum)
         codeTypeList = self.dut.codes.keys()
         codeTypeList.sort()
         for codeType in codeTypeList:
            #Convert single item lists back to string item to insure backwards compatibilty with packageResolution.
            if type(self.dut.codes[codeType]) in [types.ListType, types.TupleType] and len(self.dut.codes[codeType]) == 1:
               self.dut.codes[codeType] = self.dut.codes[codeType][0]
            ScrCmds.statMsg("%15s: %s" %(codeType,self.dut.codes[codeType]))
         ScrCmds.insertHeader("")

         # check if missing common files
         for file in Codes.commonFiles:
            if os.path.splitext(file)[1] != '.py':
               filePath1 = os.path.join(ScrCmds.getSystemParamsPath(), file)
               filePath2 = os.path.join(ScrCmds.getSystemDnldPath(), file)
               if not (os.path.isfile(filePath1) or os.path.isfile(filePath2)):
                  missingFileList.append(file)

         # raise exception if any listed file is missing
         if len(missingFileList) > 0:
            ScrCmds.statMsg('Missing file(s):')
            ScrCmds.statMsg(`missingFileList`)
            if testSwitch.winFOF == 1 or testSwitch.virtualRun == 1:   #Ignore missing files if winFOF
               ScrCmds.statMsg("winFOF mode active ignoring missing files...")
            else:
               ScrCmds.raiseException(10326, "1 or more Listed files are missing %s" % str(missingFileList))

         # DCM check
         objMsg.printMsg('PRODUCTION_MODE = %s.' %ConfigVars[CN].get('PRODUCTION_MODE',0))
         # if not objDut.certOper or ConfigVars[CN].get('PRODUCTION_MODE',0):
            # from CustomCfg import CCustomCfg
            # pass
            # #CCustomCfg().getDriveConfigAttributes(failInvalidDCM=True)   # Ensure driveConfigAttrs is populated

   #----------------------------------------------------------------------------
   def buildCustomFWList(self):
      if testSwitch.buildCustomFW:


         if self.dut.capacity == None:
            if not testSwitch.virtualRun:
               ScrCmds.raiseException(11044, "Capacity not defined for SBR %s" % self.dut.sbr)
            else:
               self.dut.capacity = ConfigVars[CN].get('CapacityTarget',400)

         ScrCmds.statMsg('%s %s %s %s' % (self.dut.HGA_SUPPLIER,self.dut.imaxHead,self.dut.capacity,self.dut.preampVendor))
         for key in self.codeDictToSearch.keys():
            if type(self.codeDictToSearch[key]) == types.DictType:
               for keyList,codeName in self.codeDictToSearch[key].items():
                  headList,hgaVendor,preampVendor,capacitySpec = keyList
                  if hgaVendor in [self.dut.HGA_SUPPLIER,None]:
                     if self.dut.imaxHead in headList or headList == () and capacitySpec in [self.dut.capacity, None] and \
                        preampVendor in [self.dut.preampVendor,None]:
                        self.codeDictToSearch[key] = codeName
                        break
               else:
                  ScrCmds.raiseException(11044, "Firmware selection failed")

   #----------------------------------------------------------------------------
   def getAlternateFileNames(self,codesFileName):
      '''Load alternate file names into a list to be parsed by buildFileList'''
      alternateFileNameList = []
      if type(codesFileName) in [types.ListType, types.TupleType]:
         for item in codesFileName:
            alternateFileNameList.extend(self.getAlternateFileNames(item))
      else:
         baseName,fileExt = os.path.splitext(codesFileName)
         alternateFileNameList.append('%s%s'% (baseName.upper(),fileExt.lower()))
         alternateFileNameList.append('%s%s'% (baseName.lower(),fileExt.upper()))
         alternateFileNameList.append(codesFileName.upper())
         alternateFileNameList.append(codesFileName.lower())
         alternateFileNameList.append(codesFileName)

      return alternateFileNameList

   #------------------------------------------------------------------------------------------------------#
   def writeHeader(self):
      ReportDriveSN(self.dut.serialnum)
      ReportStatus(self.dut.serialnum)

      ScrCmds.insertHeader("HDA TEST Config Info")
      ScrCmds.statMsg("CM Rev    : " + CMCodeVersion)
      ScrCmds.statMsg("Host Rev  : " + HostVersion)
      ScrCmds.statMsg("EQP_ID    : " + HOST_ID)
      ScrCmds.statMsg("SLT       : " + str(CellNumber))
      ScrCmds.statMsg("Product   : " + str(ConfigId[1]))
      ScrCmds.statMsg("Config    : " + str(ConfigId[2]))
      ScrCmds.statMsg("SCN       : " + str(self.dut.partNum))
      ScrCmds.statMsg("Serial No : " + str(self.dut.serialnum))
      ScrCmds.statMsg("SBR       : " + str(self.dut.sbr))
      ScrCmds.statMsg("Rim Type  : " + str(self.dut.rimType))
      ScrCmds.insertHeader("")

   #------------------------------------------------------------------------------------------------------#
   def callRequestService(self):
      if testSwitch.FE_0131335_220554_NEW_AUD_LODT_FLOW:
         if self.dut.ExtraOper:
            ScrCmds.statMsg("Jump over callRequestService - Should run LODT/AUD flow")
            return
      else:
         if self.dut.LODT:
            ScrCmds.statMsg("Jump over callRequestService - Should run LODT flow")
            return
      try:
         oper = getattr(self.dut, 'nextOper', None)
         if oper == None:
            self.dut.nextOper =   DriveAttributes.get('SET_OPER',  DriveAttributes.get('VALID_OPER',  'PRE2'))

         evalOpType = self.dut.nextOper
         if self.dut.evalMode.upper() == 'ON':
            ScrCmds.statMsg('Eval mode in ON')
            evalOpType = '*' + self.dut.nextOper
         ScrCmds.statMsg('RequestService for %s' % self.dut.nextOper)
         if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
            self.handleIRecoveryAttr()
            if (self.IR_REOPER_VALUE == 'RUNNING' and self.dut.nextOper == self.IR_BF_OPER_VALUE) or (self.IR_SAMEOPER_VALUE == "RUNNING"):
               if base_RecoveryTest.IR_XprefixWhenStartOriginalFailOper:
                  RequestService('SetResultDir', ('X' + self.dut.nextOper[0:4],))
                  RequestService('SetOperation', ('X' + evalOpType[0:4],)) # Set station name
                  self.dut.IR_StartLastOperUseToFail = True
                  DriveAttributes['IR_SAMEOPER']     = 'RUNNING'
               else:
                  RequestService('SetResultDir', (self.dut.nextOper,))
                  RequestService('SetOperation', (evalOpType,)) # Set station name
               DriveAttributes['IR_RE_OPER']  = 'DONE'
               DriveAttributes['IR_BF_OPER']  = 'NONE'
               DriveAttributes['IR_BF_EC']    = 'NONE'
               DriveAttributes['IR_BF_STATE'] = 'NONE'
               DriveAttributes['IR_BF_TEST']  = 'NONE'


            elif self.IR_REOPER_VALUE == 'RUNNING':
               RequestService('SetResultDir', ('X' + self.dut.nextOper[0:4],))
               RequestService('SetOperation', ('X' + evalOpType[0:4],)) # Set station name
            else:
               RequestService('SetResultDir', (self.dut.nextOper,))
               RequestService('SetOperation', (evalOpType,)) # Set station name
         else:
            RequestService('SetResultDir', (self.dut.nextOper,))
            RequestService('SetOperation', (evalOpType,)) # Set station name
         if self.sendParametricData() and not ConfigVars[CN].get('DISABLE_FIS_UPLOAD',0):
            RequestService('SendParametrics', (1,))
         else:
            ScrCmds.statMsg('SendParametrics DISABLED')

         cnfgFromLastOper = DriveAttributes.get('CMS_CONFIG',CN)

         if cnfgFromLastOper != CN:
            ScrCmds.statMsg('Config changed.  Config From Last Operation = %s' %cnfgFromLastOper)

         DriveAttributes['CMS_CONFIG'] = CN            # Update Attributes with Config Name

         tmp = ConfigVars[CN].get('use_CMS_Name',CN)

         if self.dut.nextOper not in ['PRE2','FNC2','FIN2']:
            DriveAttributes['%s_SCRIPT_REV'%self.dut.nextOper] = tmp
         elif self.dut.nextOper in self.dut.operList:
            DriveAttributes['%s_SCRIPT_REV'%self.dut.nextOper[:3]] = tmp   #Re-use ST10 attributes

         if not ConfigVars[CN].get('DISABLE_FIS_UPLOAD',0):
            RequestService('SendStartEvent', 1)           # Send the Start Event to FIS with CN Attribute
      except:
         ScrCmds.statMsg('RequestService for %s failed' % getattr(self.dut, 'nextOper', DriveAttributes.get('SET_OPER',  DriveAttributes.get('VALID_OPER'))))

   if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
      #----------------------------------------------------------------------------
      def handleIRecoveryAttr(self):
         attrName  = 'IR_RE_OPER'
         attrName2 = 'IR_BF_OPER'
         attrName3 = 'IR_SAMEOPER'

         attrName4 = 'IR_STATUS'
         attrName5 = 'IR_BF_OPER'
         attrName6 = 'IR_BF_EC'
         attrName7 = 'IR_VERSION'
         if not testSwitch.virtualRun:
            if ConfigVars[CN].get('BenchTop', 0) == 0: #if in real production use RequestService to get more update Attributes
               name,returnedData = RequestService('GetAttributes', (attrName,attrName2,attrName3,attrName4,attrName5,attrName6,attrName7))
               objMsg.printMsg("iRecovery : GetAttributes %s,%s,%s,%s,%s,%s and %s result = name : %s, data : %s" %(attrName,attrName2,attrName3,attrName4,attrName5,attrName6,attrName7,`name`,`returnedData`))
            else:
               name,returnedData    = ('GetAttributes',{attrName: DriveAttributes.get(attrName,'UNKNOWN'),attrName2:DriveAttributes.get(attrName2,'UNKNOWN'),attrName3:DriveAttributes.get(attrName3,'UNKNOWN'),attrName4:DriveAttributes.get(attrName4,'UNKNOWN'),attrName5:DriveAttributes.get(attrName5,'UNKNOWN'),attrName6:DriveAttributes.get(attrName6,'UNKNOWN'),attrName7:DriveAttributes.get(attrName7,'UNKNOWN')})
         else:
            name,returnedData = ('GetAttributes',{attrName: 'UNKNOWN',attrName2:'UNKNOWN',attrName3:'UNKNOWN',attrName4:'UNKNOWN',attrName5:'UNKNOWN',attrName6:'UNKNOWN',attrName7:'UNKNOWN'})

         self.IR_REOPER_VALUE   = returnedData.get(attrName ,'UNKNOWN')
         self.IR_BF_OPER_VALUE  = returnedData.get(attrName2,'UNKNOWN')
         self.IR_SAMEOPER_VALUE = returnedData.get(attrName3,'UNKNOWN')
         self.IR_STATUS_VALUE   = returnedData.get(attrName4,'UNKNOWN')
         self.IR_BF_OPER_VALUE  = returnedData.get(attrName5,'UNKNOWN')
         self.IR_BF_EC_VALUE    = returnedData.get(attrName6,'UNKNOWN')
         self.IR_VERSION_VALUE  = returnedData.get(attrName7,'UNKNOWN')

         try:
            self.IR_BF_EC_VALUE = int(self.IR_BF_EC_VALUE)        # Avoid strang string
         except:
            self.IR_BF_EC_VALUE = base_RecoveryTest.IR_ErrorCode

         self.local_ir_status_val = getattr(self.dut,'ir_status','NONE')

         try:
            self.IR_VERSION_VALUE = int(self.IR_VERSION_VALUE)
         except:
            self.IR_VERSION_VALUE = base_RecoveryTest.IR_DefaultVersion
   #------------------------------------------------------------------------------------------------------#
   def validateOper(self,nextOperIndex,restartFlags):
      """
      Validates next operation. Returns operation operIndex, rimType, and restartFlags status.
      """
      from Cell import theCell
      for operIndex in range(nextOperIndex,len(self.dut.operList)):
         nextOper = self.dut.operList[operIndex]

         if self.dut.chamberType in ['B2D','MANUAL']:
            if objRimType.IsHDSTRRiser() or objRimType.IsPSTRRiser():
               rimType = objRimType.NextRimType(self.dut.partNum,nextOper,DriveAttributes.get('RIM_TYPE',''))
            else :
               rimType = '?'
         else:
            rimType = objRimType.NextRimType(self.dut.partNum,nextOper,DriveAttributes.get('RIM_TYPE',''))

         #Check if test process is in fail safe mode.
         if self.dut.driveattr.get('FAIL_SAFE','NONE') == 'Y':
            if nextOper not in ConfigVars[CN].get('RUN_OPER_ON_FAIL',[]):  #Only valiadate operations in the RUN_OPER_ON_FAIL list.
               continue

         #--- HDSTR ------------------------------------------------------------
         if self.dut.nextOper == getattr(TP,'Pre_Hdstr_Oper','PRE2') and self.dut.HDSTR_PROC == 'Y':
            ScrCmds.statMsg("HDSTR Detected setting next oper to HDT.")
            #
            #  Allow HDSTR simulation in Gemini
            #
            if self.dut.HDSTR_IN_GEMINI == 'Y':
               #nextOp = 'FNC'
               restartFlags.update({"doRestart":1,"sendRun":4})
            else:
               #nextOp = 'HDT'
               #need to include FNC in Operations list for returning drive.
               DriveAttributes['SET_OPER'] = 'HDT'  #Sorter C in factory looks for this attribute.
               restartFlags.update({"doRestart":0,"sendRun":1})
               DriveAttributes['VALID_OPER'] = 'HDT'
               # Pharaoh uses HDT state, i.e. PRE2 -> HDT -> FNC -> CRT2; other programs do not, i.e. CAL2 -> FNC -> FNC2 -> CRT2
            if not testSwitch.FE_0124465_391186_HDSTR_SHARE_FNC_FNC2_STATES:
               self.dut.driveattr['OPER_INDEX'] = nextOperIndex+1
               if testSwitch.FE_0154919_420281_P_SUPPORT_SIO_TEST_RIM_TYPE_55:
                  rimType = objRimType.NextRimType(self.dut.partNum,'HDT',DriveAttributes.get('RIM_TYPE',''))
            else:
               self.dut.driveattr['OPER_INDEX'] = nextOperIndex
               if testSwitch.FE_0154919_420281_P_SUPPORT_SIO_TEST_RIM_TYPE_55:
                  rimType = objRimType.NextRimType(self.dut.partNum,'HDT',DriveAttributes.get('RIM_TYPE',''))

            return operIndex, rimType, restartFlags
         #--- FNC --------------------------------------------------------------
         elif nextOper == 'FNC' and not self.dut.HDSTR_PROC == 'Y' and (self.dut.chamberType == 'GEMINI' or objRimType.IsHDSTRRiser()):
            #If we aren't a hdstr drive skip FNC as next oper
            ScrCmds.statMsg("No HDSTR Proc... Skipping FNC.")
            continue
         #----FNC2 -------------------------------------------------------------
         elif nextOper == 'FNC2' and (self.dut.HDSTR_PROC == 'Y' or self.dut.driveattr.get('ST240_PROC','NONE')== 'C' or self.dut.nextOper == 'FNC'):
            #Skip FNC2 operation if HDSTR drive
            ScrCmds.statMsg("HDSTR Proc... Skipping FNC2.")
            continue
         #--- SDAT2 ------------------------------------------------------------
         #elif nextOper == 'SDAT2':

            #initialize in case there are errant paths
            #selected = False

            #insert the sample monitor request here
            # basically the same as CGetSampMonForSDAT but the StateInfo
            # and jump state isn't needed
            #if testSwitch.FE_0159477_350037_SAMPLE_MONITOR:
               #from SampleMonitor import CSampMon

               #self.CSampMon = CSampMon( )
               #PartNum = self.dut.partNum
               #SpecBldReq = self.dut.sbr
               #HdCount = self.dut.imaxHead
               # This is for sdat on fail, a record is desired otherwise continue
               #if ( self.dut.errCode != 0 ):
                  #Change the test name to SDAT_F for sample rates on failure
                  #StateInfo, TruthVal = self.CSampMon.ProcessSampleRequest('SDAT2', 'SDAT_F', PartNum, SpecBldReq, HdCount)
               #else:
                  #StateInfo, TruthVal = self.CSampMon.ProcessSampleRequest('SDAT2', 'SDAT', PartNum, SpecBldReq, HdCount)

               # as long as a value other than 0 was returned for the truth value
               # sample monitor should be run
               #if TruthVal:
                  #selected = True
               #else:
                  #selected = False
               #drive attribute needs to be updated for the truth value
               #DriveAttributes['SAMP_MON_TRUTH'] = TruthVal

            #else:
               #from re import search, error

               # The sn selection criteria is a regex list of sn matches
               # Examples of selection lists for configvars
               #   ['E',]        -> All SN's ending in 'E'
               #   ['E.',]       -> All SN's ending in E and any char after that... ie. EA, E1, E2...
               #   ['A.E',]      -> All SN's ending in A (any char) E... A1E, A2E, AZE...
               #   ['Z.', 'A.',] -> All SN's ending in Z(any char) or A(any char)... Z1, ZA, A1, AA..

               #snList = ConfigVars[CN].get('SDAT SNList', [])

               #try:
                  #Create a binary list of if the pattern matches any of the sequences
                  #  then take the bool(max) which will be false if no matches or true if any do
                  #selected = bool(max([int(not search(li,self.dut.serialnum[-len(li):]) == None) for li in snList]))
               #except error:
                  #objMsg.printMsg("Error in regex evaluation of %s- SDAT selection bypassed!!!" % (snList,), objMsg.CMessLvl.CRITICAL)
               #except ValueError:
                  #if len(snList) == 0:
                     #no selection criteria
                     #selected = False
                  #else:
                     #raise

               #check snList length 1st so we don't except if it is []
               #if len(snList) and snList[0] == 'ALL':
                  #selected = True

            #if not self.dut.mdwCalComplete:
               #selected = False

            #if selected:
               #if (nextOper in getattr(TP,'HDSTRNEXTRUN',[])) and (objRimType.IsHDSTRRiser()):
                  #ScrCmds.statMsg('Go to Gemini to run %s'%TP.HDSTRNEXTRUN)
                  #self.dut.driveattr['SET_OPER'] = nextOper
                  #restartFlags.update({"doRestart":0,"sendRun":4}) # sendRun=4 => use local attrs on restart
                  #DriveAttributes['OPER_INDEX'] = operIndex
                  #return operIndex, rimType, restartFlags
               #else:
                  #restartFlags.update({"doRestart":1,"restartOnFail":1,"sendRun":4})# run SDAT
                  #return operIndex, rimType, restartFlags
            #else:
               #if self.dut.driveattr.get('FAIL_SAFE','NONE') == 'Y':
                  #restartFlags.update({'doRestart':0,'sendRun':1})
                  #return operIndex, rimType, restartFlags
               #else:
                  #continue

         elif nextOper == 'CMT2':
            if self.dut.driveattr['FAIL_SAFE'] == 'Y' and self.dut.nextOperOverride != 'CMT2':
               restartFlags.update({'doRestart':0,'sendRun':1})
               return operIndex, rimType, restartFlags
            if self.dut.driveattr['CMT2_TEST_DONE'] != 'NONE':
               restartOpers = self.dut.operList[self.dut.operList.index('CMT2'):]

               if testSwitch.proqualCheck: # Initialise xxxx_TEST_DONE if Proqual check is turn On for current and all subsequent operations
                  pq_attr_reset = {}
                  for oper in restartOpers:
                     pq_attr_reset['%s_TEST_DONE'%oper.upper()] = 'NONE'

                  DriveAttributes.update(pq_attr_reset)

            self.dut.driveattr['FAIL_SAFE'] = 'N'
            restartFlags.update({'doRestart':1,"restartOnFail":1,'sendRun':4})
            return operIndex, rimType, restartFlags

         # 3-tier re-CRT2 from FIN2 downgrade.
         elif nextOper == 'CRT2' and testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
            if self.dut.nextOperOverride == 'CRT2':
               restartOpers = self.dut.operList[self.dut.operList.index('CRT2'):]
               if testSwitch.proqualCheck: # Initialise xxxx_TEST_DONE if Proqual check is turn On for current and all subsequent operations
                  pq_attr_reset = {}
                  for oper in restartOpers:
                     pq_attr_reset['%s_TEST_DONE'%oper.upper()] = 'NONE'
                  DriveAttributes.update(pq_attr_reset)

               self.dut.driveattr['FAIL_SAFE'] = 'N'
               restartFlags.update({'doRestart':1,"restartOnFail":1,'sendRun':4})
               return operIndex, rimType, restartFlags
            else:
               restartFlags.update({"doRestart":1,"sendRun":4})
               return operIndex, rimType, restartFlags

         elif nextOper == 'CUT2' and testSwitch.FE_0180513_007955_COMBINE_CRT2_FIN2_CUT2 and not testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
            #if testSwitch.FE_0180513_007955_COMBINE_CRT2_FIN2_CUT2 is enabled then there is no transitional
            #    CUT2 oper- only a fresh start
            #Don't return though since IDT2 could be next...etc
            continue
         #--- B2D2 -------------------------------------------------------------
         elif nextOper == 'B2D2' and self.dut.chamberType == 'GEMINI':
            if testSwitch.WA_0169062_470167_P_GET_CURRENT_B2D2_RIMTYPE:
               rimType = objRimType.NextRimType(self.dut.partNum,nextOper,DriveAttributes.get('RIM_TYPE',''))
            else:
               if (operIndex+1) < len(self.dut.operList):
                  rimType = objRimType.NextRimType(self.dut.partNum,self.dut.operList[operIndex+1],DriveAttributes.get('RIM_TYPE',''))
            if testSwitch.FE_0164089_395340_P_B2D2_SELECTION_FEATURE:
               self.dut.driveattr['RESUME_MFG_EVAL'] = DriveAttributes.get('MFG_EVAL','?')
               self.dut.driveattr['MFG_EVAL'] = 'MIRKWOOD'
               self.dut.driveattr['SET_OPER'] = self.dut.driveattr['VALID_OPER'] = nextOper
            restartFlags.update({'doRestart':0,'sendRun':1})
            return operIndex, rimType, restartFlags
         #----TODT -------------------------------------------------------------
         elif nextOper == 'TODT':
            if 'ALL' in getattr(TP,'TODT_PN','NONE') or self.dut.partNum in getattr(TP,'TODT_PN','NONE'):
               restartFlags.update({'doRestart':0,'sendRun':1})
               self.dut.driveattr['MFG_EVAL'] = '?'
               self.dut.driveattr['SET_OPER'] = 'OTG'
               self.dut.driveattr['TODT'] = 'P'
               return operIndex, rimType, restartFlags
            else:
               #Skip TODT operation TODT not select in TODT_PN list in TestParameters.py
               ScrCmds.statMsg("No TODT require... Skipping TODT.")
               continue
         #--- ODT2 -------------------------------------------------------------
         elif nextOper in ['ODT2','IDT2']:
            if testSwitch.FE_0134422_336764_GIO_DYNAMIC_RIMTYPE_SUPPORT:
               changeRimType = 0
               ScrCmds.statMsg("Ramp Temp SN List = %s" %  SN50CList)
               if self.dut.serialnum[-1:] in SN50CList:
                  ScrCmds.statMsg("Change Rimtype for support IDT2 50C")
                  changeRimType = 1

            if testSwitch.FE_0151675_231166_P_SUPPORT_SINGLE_DIAG_INIT_SHIP:
               restartIDT = self.dut.isSupposedToRunGIO()
               if restartIDT:
                  ScrCmds.statMsg('GIO_Selection - Demand Check = Pass - Run Drive')
                  DriveAttributes['RESUME_MFG_EVAL'] = DriveAttributes.get('MFG_EVAL','?')
                  DriveAttributes['MFG_EVAL'] = '?'

                  if restartIDT == 2:
                     self.dut.driveattr['IDT_TEST_METHOD'] = 'FORCED'
                  else:
                     self.dut.driveattr['IDT_TEST_METHOD'] = 'SELECT'

                  if testSwitch.FE_0134422_336764_GIO_DYNAMIC_RIMTYPE_SUPPORT:
                     if changeRimType:
                        from RimTypes import intfTypeMatrix
                        rimType = intfTypeMatrix['SATA']['rimTypeMatrix']['IDT2_DY'][0]
                        theCell.setCellRimType(rimType,50,1)
                        self.dut.driveattr['GIO_EVAL'] = ConfigVars[CN]['GIO_EvalName']
                  restartFlags.update({'doRestart':1,'sendRun':4,'configEval':ConfigVars[CN]['GIO_EvalName']})
                  return operIndex, rimType, restartFlags
               else:
                  ScrCmds.statMsg('GIO_Selection - Demand Check = Fail - Do Not Run Drive')
                  continue


            else:
               run_ODT = False
               if ConfigVars[CN].get('GIO_Selection') in [None, 'OFF'] and ConfigVars[CN].get('GIO_Attr','OFF') == 'ON':
                  #Define GIO_AttrValue in PIF.py as below
                  #GIO_AttrValue = {
                  #    'Condition 1'   :   {'HSA_REV':'C'},
                  #    'Condition 2'   :   {'HSA_REV':['B', 'C']},
                  #    'Condition 3'   :   {'FOF_PROCESS_TIME':('>', 5),'HSA_REV':'B'},
                  #    }

                  from PIF import GIO_AttrValue

                  attrList = []
                  for condition, attrSet in GIO_AttrValue.items():
                     attrList.extend(attrSet.keys())

                  name, fisAttrList = RequestService('GetAttributes', tuple(attrList)) # Get drive attribute in real-time

                  for condition, attrSet in GIO_AttrValue.items():
                     for name, values in attrSet.items():
                        if type(values) == types.StringType and fisAttrList.get(name,'?') == values:
                           run_ODT = True
                        elif type(values) in [types.ListType, types.TupleType]:
                           try:
                              run_ODT = eval('%s %s %s' % (fisAttrList.get(name,'?'), values[0], values[1]))
                           except:
                              if fisAttrList.get(name,'?') in values:
                                 run_ODT = True
                              else:
                                 run_ODT = False

                           if not run_ODT:
                              ScrCmds.statMsg('Donot meet requirement for %s(Required: %s, Actual: %s)'%(name, values, fisAttrList.get(name,'?')))
                              break
                        else:
                           ScrCmds.statMsg('Donot meet requirement for %s(Required: %s, Actual: %s)'%(name, values, fisAttrList.get(name,'?')))
                           run_ODT = False
                           break
                     if run_ODT:
                        ScrCmds.statMsg('GIO_Attr - Need run SCF2 because of GIO_AttrValue/PIF.py is set')
                        break
               elif ConfigVars[CN].get('GIO_Selection') not in [None, 'OFF']:
                  ConfigVars[CN]['GIO_EvalName'] = ConfigVars[CN].get('GIO_EvalName','GIO_TEST')
                  ScrCmds.statMsg('GIO_EvalName = %s GIO_Selection = %s' % \
                                 (ConfigVars[CN]['GIO_EvalName'], ConfigVars[CN]['GIO_Selection']))
                  if testSwitch.FE_0158668_395340_P_UPDATE_OPER_ATTR_FOR_ODT_TES:
                     self.dut.driveattr['SET_OPER'] = self.dut.driveattr['VALID_OPER'] = 'ODT2'
                  if ConfigVars[CN]['GIO_Selection'] == 'FORCED':
                     run_ODT = True
                     ScrCmds.statMsg('GIO_Selection - Demand Check = FORCED - Run Drive')

                     if testSwitch.FE_0221365_402984_RESTORE_OVERLAY:
                        objPwrCtrl.EnablePowerCycle()    # Enable power cycle disabled from SDOD
                        self.recoverOverlay()   # recover overlay during before MQM

                     self.dut.driveattr['IDT_TEST_METHOD'] = 'FORCED'

                  elif ConfigVars[CN].get('GIO_Selection') in ['SELECT', 'ON']:
                     from IDTSelect import IDTSelect
                     Demand = IDTSelect()
                     restartIDT = Demand.DemandCheck('IDT')      # Check Demand table, to turn the test on/off
                     if restartIDT == 1:
                        run_ODT = True
                        self.dut.driveattr['IDT_TEST_METHOD'] = 'SELECT'
                        ScrCmds.statMsg('GIO_Selection - Demand Check = Pass - Run Drive')
                        if testSwitch.FE_0134422_336764_GIO_DYNAMIC_RIMTYPE_SUPPORT:
                           if changeRimType:
                              from RimTypes import intfTypeMatrix
                              rimType = intfTypeMatrix['SATA']['rimTypeMatrix']['IDT2_DY'][0]
                              theCell.setCellRimType(rimType,50,1)
                              self.dut.driveattr['GIO_EVAL'] = ConfigVars[CN]['GIO_EvalName']
                     else:
                        ScrCmds.statMsg('GIO_Selection - Demand Check = Fail - Do Not Run Drive')
                        continue

               if run_ODT:
                  self.dut.driveattr['RESUME_MFG_EVAL'] = DriveAttributes.get('MFG_EVAL','?')
                  self.dut.driveattr['MFG_EVAL']  = '?'
                  self.dut.driveattr['SCF2_TEST'] = 'Y'
                  restartFlags.update({'doRestart':1,'sendRun':4,'configEval':ConfigVars[CN]['GIO_EvalName']})
                  return operIndex, rimType, restartFlags
               else:
                  ScrCmds.statMsg('GIO_Selection ConfigVar Not Found or Set OFF - Do Not Run Drive')
                  continue
         #--- FNG2 -------------------------------------------------------------
         elif nextOper == 'FNG2' and testSwitch.FNG2_Mode == 1 :
            ScrCmds.statMsg('Pass FNG2. Setting PROC_CTRL99=PASS')
            self.dut.driveattr['PROC_CTRL99'] = "PASS"
            restartFlags.update({'doRestart':1,'sendRun':4})
            return operIndex, rimType, restartFlags
         #SP HDSTR
         #elif (((nextOper == 'CRT2') or (nextOper =='SPSC2')) and (riserType == 'HDSTR')):
         elif ((nextOper == getattr(TP,'HDSTRNEXTRUN','')) and (objRimType.IsHDSTRRiser())):
            ScrCmds.statMsg('Go to Gemini to run %s'%TP.HDSTRNEXTRUN)
            self.dut.driveattr['SET_OPER'] = nextOper
            restartFlags.update({"doRestart":0,"sendRun":4}) # sendRun=4 => use local attrs on restart
            self.dut.driveattr['OPER_INDEX'] = nextOperIndex
            return operIndex, rimType, restartFlags
         elif nextOper == 'CAL2' and testSwitch.FE_0158386_345172_HDSTR_SP_PRE2_IN_GEMINI and self.dut.HDSTR_SP2_PROC =='Y':
            ScrCmds.statMsg('Go to HDSTR_SP to run CAL2')
            self.dut.driveattr['OPER_INDEX'] = nextOperIndex
            self.dut.driveattr['VALID_OPER'] = 'CAL'
            self.dut.driveattr['SET_OPER'] = 'CAL'
            rimType = 'HDSTR'
            restartFlags.update({"doRestart":0,"sendRun":1})
            return operIndex, rimType, restartFlags
         #----CCV2 -------------------------------------------------------------
         elif nextOper == 'CCV2' and testSwitch.FE_0164158_460646_P_ENABLE_RUN_CCV2_BY_SETOPER_ATTR:
            self.dut.driveattr['FAIL_SAFE'] = '?'
            restartFlags = {'doRestart':0,'sendRun':1}
            return operIndex, rimType, restartFlags
         else:
            restartFlags.update({'doRestart':1,'sendRun':4})
            return operIndex, rimType, restartFlags
      else:
         self.dut.driveattr['FAIL_SAFE'] = '?'
         restartFlags = {'doRestart':0,'sendRun':1}
         return operIndex, rimType, restartFlags
   #----------------------------------------------------------------------------
   def setNextOper(self,restartFlags={}):
      if testSwitch.FE_0131335_220554_NEW_AUD_LODT_FLOW:
         if self.dut.ExtraOper:
            ScrCmds.statMsg("Jump over callRequestService - Should run LODT/AUD flow")
            return
      else:
         if self.dut.LODT:
            ScrCmds.statMsg("Jump over callRequestService - Should run LODT flow")
            return

      if self.dut.nextOper == "FIN2" and DriveAttributes.get('IOFIN2_PENDING', 'NONE') == "2": # Phone, set IOFIN2_PENDING = NONE at the end of FIN2. 
         ScrCmds.statMsg('Setting IOFIN2_PENDING = NONE')
         DriveAttributes["IOFIN2_PENDING"] = "NONE"
      if self.dut.errCode == 0:
         #Really if we are in this method then ec should be 0 but lets be sure
         self.dut.driveattr['%s_TEST_DONE' % self.dut.nextOper] = "PASS"
         if self.dut.nextOper in ['FIN2'] and \
            ((int(ConfigVars[ConfigId[2]].get('SPMQM_ENABLE','0')) and self.dut.AABType not in ['501.42']) or \
            (int(ConfigVars[ConfigId[2]].get('LCT_SPMQM_ENABLE','0')) and self.dut.AABType in ['501.42'])):
            self.dut.driveattr['MQM_TEST_DONE'] = "PASS"

         if not self.dut.nextOper == 'SDAT2':
            #Don't update FINAL_PASS_OPER to SDAT2 as it isn't a valid shippable state and can be run on failure
            self.dut.driveattr['FINAL_PASS_OPER'] = self.dut.nextOper

         if not self.dut.nextOper in ConfigVars[CN].get('RUN_OPER_ON_FAIL',[]):
            self.dut.driveattr['FAIL_SAFE'] = 'N'

         self.DriveAttrTag(mode='end')
      else:
         if restartFlags.get('forceCellChange', 0):
            ScrCmds.statMsg("forceCellChange detected...")
            return restartFlags

         if testSwitch.FE_0161256_395340_P_CLEAR_MFG_EVAL_FOR_PASSER_OR_FAILED and ConfigVars[CN].get('CLEAR_MFG_EVAL','OFF') == 'ON':
               self.dut.driveattr['MFG_EVAL']  = '?'
         if self.dut.errCode == 11891 or self.dut.errCode == 11887:
            self.dut.driveattr['FAIL_SAFE'] = 'N'
         else:
            self.dut.driveattr['FAIL_SAFE'] = 'Y'

      if self.dut.nextOperOverride != None:
         try:
            nextOperIndex = self.dut.operList.index(self.dut.nextOperOverride)
         except:
            msg = "Oper in nextOperOverride %s not in StateTable OperList" % self.dut.nextOperOverride
            ScrCmds.raiseException(11044, msg)
      else:
         nextOperIndex = int(self.dut.driveattr['OPER_INDEX']) + 1
      if nextOperIndex < len(self.dut.operList):
         curRimType = DriveAttributes.get('RIM_TYPE','')
         nextOperIndex, rimType, restartFlags = self.validateOper(nextOperIndex,restartFlags)
         if restartFlags.get('doRestart') == 0:
            self.dut.driveattr['FAIL_SAFE'] = '?'
            if testSwitch.FE_0154919_420281_P_SUPPORT_SIO_TEST_RIM_TYPE_55:
               if objRimType.IsHDSTRRiser():
                  nextOper = self.dut.operList[nextOperIndex]
                  if nextOper != 'CRT2':
                     rimType = curRimType
               elif (testSwitch.FE_0158386_345172_HDSTR_SP_PRE2_IN_GEMINI and self.dut.operList[nextOperIndex] == 'CAL2' and self.dut.HDSTR_SP2_PROC == 'Y'):
                  nextOper = 'CAL'
                  rimType = curRimType
               elif testSwitch.FE_0164089_395340_P_B2D2_SELECTION_FEATURE and self.dut.operList[nextOperIndex] in ['B2D2']:
                  nextOper = self.dut.operList[nextOperIndex]
               else:
                  nextOper = '?'
                  if self.dut.HDSTR_PROC == 'Y':
                     ScrCmds.statMsg('Run HDT for change RimType')
                  else:
                     rimType = curRimType
            else:
               if objRimType.IsHDSTRRiser():
                  nextOper = self.dut.operList[nextOperIndex]
                  if nextOper != 'CRT2':
                     rimType = curRimType
               elif (testSwitch.FE_0158386_345172_HDSTR_SP_PRE2_IN_GEMINI and self.dut.operList[nextOperIndex] == 'CAL2' and self.dut.HDSTR_SP2_PROC == 'Y'):
                  nextOper = 'CAL'
               elif testSwitch.FE_0164089_395340_P_B2D2_SELECTION_FEATURE and self.dut.operList[nextOperIndex] in ['B2D2']:
                  nextOper = self.dut.operList[nextOperIndex]
               else:
                  nextOper = '?'
               if objRimType.IsHDSTRRiser() and nextOper == 'CRT2':
                  ScrCmds.statMsg('go to GEMINI to run CRT2 with CRT2 Rimtype (%s)' % (rimType))
               else:
                  rimType = curRimType
         else:
            nextOper = self.dut.operList[nextOperIndex]
            self.dut.driveattr['OPER_INDEX'] = nextOperIndex
            if testSwitch.FE_0143876_421106_P_HDSTR_OR_GEMINI_PROCESS_WITH_DRIVE_ATTR:
               if self.dut.nextOper == 'PRE2' and self.dut.HDSTR_PROC == 'Y':
                  DriveAttributes['SET_OPER'] = nextOper
            else:
               if self.dut.nextOper == 'PRE2' and ConfigVars[CN].get("Hdstr Process", 'N') == 'Y':
                  DriveAttributes['SET_OPER'] = nextOper

            if self.dut.nextOper in ['CRT2', 'FIN2']:
               if self.dut.driveattr.get('ST240_PROC', 'N') == 'Y':   # clear attr ST240_PROC
                  DriveAttributes['ST240_PROC'] = 'N'
                  self.dut.driveattr['ST240_PROC'] = 'N'

         if testSwitch.FE_0143876_421106_P_HDSTR_OR_GEMINI_PROCESS_WITH_DRIVE_ATTR:
            if self.dut.driveattr.get("ST240_PROC", "N") == 'Y' and self.dut.nextOper == 'PRE2':
               restartFlags.update({"doRestart":0,"sendRun":4})
            elif self.dut.nextOper == 'PRE2' and self.dut.HDSTR_PROC == 'Y':
               restartFlags.update({"doRestart":0,"sendRun":4})
         else:
            if self.dut.driveattr.get("ST240_PROC", "N") == 'Y' and self.dut.nextOper == 'PRE2':
               restartFlags.update({"doRestart":0,"sendRun":4})
            elif self.dut.nextOper == 'PRE2' and ConfigVars[CN].get("Hdstr Process", 'N') == 'Y':
               restartFlags.update({"doRestart":0,"sendRun":4})

         try:
            from PIF import NO_IO_CFG, IO_RIM_CUSTOMER
            ScrCmds.statMsg("PIF NO_IO_CFG: %s" % NO_IO_CFG)
            ScrCmds.statMsg("nextOper=%s self.dut.nextOper=%s self.dut.partNum=%s" % (nextOper, self.dut.nextOper, self.dut.partNum))

            if nextOper in NO_IO_CFG['NO_IO_OPER'] and (self.dut.partNum[-3:] in NO_IO_CFG['NO_IO_TAB'] or "*" in NO_IO_CFG['NO_IO_TAB']):
               if self.dut.nextOper in NO_IO_CFG['NO_IO_OPER']:
                  ScrCmds.statMsg("Current oper same as next oper, use same RimType")
                  rimType = DriveAttributes['RIM_TYPE']
               else:
                  if self.MoveToIORim(): #For SONY/Panasonic drives move to IO slots
                     rimdict = IO_RIM_CUSTOMER['IO_RIMTYPE']
                     ScrCmds.statMsg("This is SONY/Panasonic customers. rimdict %s" % (rimdict,))
                     
                  else:
                     rimdict = NO_IO_CFG['NO_IO_RIMTYPE']
                     ScrCmds.statMsg("This is other OEM/SBS customers. rimdict %s" % (rimdict,))
                  from Cell import theCell
                  for rt in rimdict:
                     stat = theCell.askHostForTwoMove(rt, ambivalent=0)
                     if stat[1][1] > 0 or ConfigVars[CN].get('BenchTop',0):
                        rimType = rt
                        ScrCmds.statMsg("Found rimType: %s" % rimType)
                        break
         except:
            if not ConfigVars[CN].get('PRODUCTION_MODE',0):
               ScrCmds.statMsg("NO_IO Traceback: %s" % `traceback.format_exc()`)

         if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
            if getattr(self.dut,'irReOper',False) == True:
               nextOperIndex                    = self.dut.operList.index(self.dut.nextOperOverride)
               nextOper                         = self.dut.operList[nextOperIndex]
               self.dut.driveattr['OPER_INDEX'] = nextOperIndex
               DriveAttributes['SET_OPER']      = nextOper
               rimType                          = objRimType.NextRimType(self.dut.partNum,nextOper,DriveAttributes.get('RIM_TYPE',''))
               ScrCmds.statMsg('iRecovery Override : Next oper: %s Index: %s  rimType: %s  restartFlags: %s' %(nextOper, nextOperIndex, rimType, restartFlags))

         if (not nextOper in getattr(TP,'PSTROperList')) and objRimType.IsPSTRRiser():
             objMsg.printMsg('Next operation %s is not allow to run in PSTR, set doRestart = 0' % nextOper)
             restartFlags['doRestart'] = 0

         if nextOper == 'CRT2' and ConfigVars[CN].get('LCBET',0) == 1:
            restartFlags.update({'doRestart':0,'sendRun':4})

         ScrCmds.statMsg('Next oper: %s Index: %s  rimType: %s  restartFlags: %s' % (nextOper, nextOperIndex, rimType, restartFlags))
         DriveAttributes['RIM_TYPE'] = rimType
         self.dut.driveattr['RIM_TYPE'] = DriveAttributes['RIM_TYPE']

         if nextOper == "MQM2" and \
            ((int(ConfigVars[CN].get('SPMQM_ENABLE', 0)) and self.dut.AABType not in ['501.42']) or \
            (int(ConfigVars[CN].get('LCT_SPMQM_ENABLE', 0)) and self.dut.AABType in ['501.42'])): #for MQM2 operation, update unique drive attribute
            DriveAttributes['OPERATION_AFT'] = 'MQM2_PENDING'
            objMsg.printMsg("Updated unique drive attribute for MQM2 oper! %s" % (DriveAttributes['OPERATION_AFT'],))
         else:
            DriveAttributes['OPERATION_AFT'] = ''

         return restartFlags
      else:
         if testSwitch.FE_0161256_395340_P_CLEAR_MFG_EVAL_FOR_PASSER_OR_FAILED:
            self.dut.driveattr['MFG_EVAL']  = '?'
         self.dut.driveattr['FAIL_SAFE'] = '?'
         if self.holdDriveEval()["holdDrive"] == 0 and self.dut.errCode == 0:

            if not testSwitch.FE_0127046_231166_DONT_SET_RIM_Q_ON_LAST_OPER:
               DriveAttributes['RIM_TYPE'] = '?'
               self.dut.driveattr['RIM_TYPE'] = DriveAttributes['RIM_TYPE']
         restartFlags.update({'doRestart':0,'sendRun':1})
         ScrCmds.statMsg('Index: %s  restartFlags: %s' % (nextOperIndex, restartFlags))
         return restartFlags
   #------------------------------------------------------------------------------------------------------#
   def MoveToIORim(self):

      from CustomCfg import CCustomCfg
      from PIF import IO_RIM_CUSTOMER

      # if self.dut.driveConfigAttrs == None:
         # CCustomCfg().getDriveConfigAttributes(partNum = self.dut.partNum, force = True, failInvalidDCM = True)

      dcmscreens = []
      for name in self.dut.driveConfigAttrs.keys(): 
         if name == 'CUST_TESTNAME':
            value = self.dut.driveConfigAttrs[name][1]
            dcmscreens = [value[i*3:(i*3 )+3] for i in xrange(len(value)/3)]
            break
      ScrCmds.statMsg("CustScreens %s IO_RIM_CUSTOMER %s" % (dcmscreens, IO_RIM_CUSTOMER))
      iorim = False
      for i in dcmscreens:
         for j in IO_RIM_CUSTOMER['CUSTOMER_SCREEN']:
            if i == j:
               iorim = True
               break
         if iorim == True:
            break
      return iorim

   #------------------------------------------------------------------------------------------------------#
   def GetLogServer(self):
      # CMS_FAMILY is updated during PWA state
      cms_family = DriveAttributes.get('CMS_FAMILY', '')

      try:
         name, data = RequestService('GetSiteconfigSetting', 'AltFtpServers')
         ScrCmds.statMsg('name = %s data = %s' % (name, data))
         if data['AltFtpServers'].get('Auto_LogServer', 'None') != 'None':
            log_server = 'Auto_LogServer'
         elif data['AltFtpServers'].get(cms_family + '_LogServer', 'None') != 'None':
            log_server = cms_family + '_LogServer'
         else:
            log_server = 'LogServer'
      except:
         log_server = 'LogServer'

      return log_server

   #------------------------------------------------------------------------------------------------------#
   def SaveResultFile(self):
      try:
         if not ConfigVars[CN].get("SAVE_RESULT", 0):
            return 0

         #log_server = self.GetLogServer()

         res_file_name = "%s.%s" % (HDASerialNumber, self.dut.nextOper[0:3])
         from zipfile import ZipFile,ZIP_DEFLATED
         zip_file_path = '/result'
         try: zip_file_path = '/' + CN + '/' + DriveAttributes["SUB_BUILD_GROUP"] + zip_file_path
         except: pass

         # if log_server == 'Auto_LogServer':
            # zip_file_path = '/' + DriveAttributes.get('CMS_FAMILY', "CMS_FAMILY") + "/sp" + zip_file_path

         zip_file_name = "%s.%s.zip" % (HDASerialNumber, self.dut.nextOper[0:3])
         zipCapLog = GenericResultsFile(zip_file_name)
         zipCapLog.open('w')
         z = ZipFile(zipCapLog, mode="w", compression=ZIP_DEFLATED)
         z.write(os.path.join(ScrCmds.getSystemResultsPath(),"%s.rp1" % FSO.CFSO().getFofFileName(1)), res_file_name)
         z.close()
         zipCapLog.close()

         RequestService('SetResultDir',(zip_file_path,))
         #RequestService('SendGenericFile',(zip_file_name, log_server))
         RequestService('SetResultDir',("",))
         zipCapLog.delete()
         ScrCmds.statMsg('SaveResultFile Zip File %s/%s created' % (zip_file_path, zip_file_name))
      except:
         ScrCmds.statMsg('SaveResultFile fail. Traceback=%s' % traceback.format_exc())

   #------------------------------------------------------------------------------------------
   def SaveRunHistory(self, testtime, failcode, isCarrier = 0):
      '''
      Creates file with the following content to enable ease of data/yield crunching by Yield Report Generator
         SUB_BUILD_GROUP  HDASerialNumber  OPR  Failcode  CN  failureState  CellNumber  MODEL_NUM
         CellNumber_TrayIndex_PortIndex  CurrentTime  TestTime  BirthTime
      '''
      def TimeToString(testtime):
         '''
         Convert testtime in s to HH:MM:SS string (HH can be more than 2 characters)
         '''
         h = testtime / 3600
         m = ((testtime / 60) % 60)
         s = testtime % 60
         timestring = '%02d:%02d:%02d' % (h, m, s)
         return timestring

      def LongTimeStr(timestr=""):
         """
         Convert time string to compatible Windows/Linux format
         Eg Wed Jun  7 13:49:24 2006 to Wed Jun 07 13:49:24 2006
         In Linux, 7 is not prepended with 0 but in Windows, 7 is prepended with 0
         """
         longtimestr = ''
         try:
            s1 = timestr.split()
            if len(s1[2]) == 1:
               s1[2] = '0'+ s1[2]
            longtimestr = str.join(" ", s1)
         except:
            longtimestr = ''
         return longtimestr

      try:
         if not ConfigVars[CN].get("SAVE_RUNHIST", 0):
            return 0

         log_server = self.GetLogServer()

         operation =  self.dut.nextOper[0:3]
         file_path = ''
         file_path = file_path + CN +'/'
         file_path = file_path + str(DriveAttributes["SUB_BUILD_GROUP"])

         # if log_server == 'Auto_LogServer':
            # file_path = DriveAttributes.get('CMS_FAMILY', "CMS_FAMILY") + "/sp/" + file_path

         drvSN = HDASerialNumber
         file_name =  "%s.%s"%(drvSN,operation)

         file = GenericResultsFile(file_name)
         file.open('w')
         strFailcode =  str(failcode)
         if(str(failcode) == '0'):
            strFailcode = 'PASS'

         his = DriveAttributes["SUB_BUILD_GROUP"] + '  ' + drvSN + '  ' + operation + '  ' +  strFailcode
         his = his + '  ' +  CN + '  ' +  self.dut.failureState + '  '+ str(CellNumber) + '  ' + DriveAttributes.get('MODEL_NUM', 'NONE')
         his = his + '  ' + str(CellNumber)+ '_' +  str(TrayIndex)+ '_' +str(PortIndex) + '  ' + LongTimeStr(time.ctime(time.time())) + '  ' + TimeToString(testtime) +  '  ' + LongTimeStr(time.ctime(self.dut.birthtime))
         his = his + '  ' + str(DriveAttributes.get('PART_NUM','NONE')).strip()[:6]
         file.write(his)
         file.close()

         RequestService('SetResultDir',(file_path,))
         RequestService('SendGenericFile',(file_name, log_server))
         RequestService('SetResultDir',("",))
         file.delete()
         ScrCmds.statMsg('SaveRunHistory Create File %s/%s' %(file_path,file_name))
      except:
         ScrCmds.statMsg('SaveRunHistory fail. Traceback=%s' % traceback.format_exc())

   #----------------------------------------------------------------------------
   def CheckGeminiShutdown(self):
      flag = 0
      if ConfigVars[CN].get('ALLOW_SHUTDOWN', 'OFF') == 'ON':
         geminiShutdown = RequestService('GetSiteconfigSetting','GEMINI_SHUTDOWN_ENABLE')[1].get('GEMINI_SHUTDOWN_ENABLE', 'OFF')
         ScrCmds.statMsg('Gemini Shutdown Enable: %s' % geminiShutdown)

         if geminiShutdown == 'ON':
            allow_oper = ConfigVars[CN].get('ALLOW_OP', ['PRE2', 'CAL2', 'FNC2', 'SDAT2', 'CRT2', 'FIN2', 'CUT2'])
            if self.dut.nextOper in allow_oper:
               ScrCmds.statMsg('This Gemini will shutdown, update doRestart to 0')
               flag = 1
            else:
               ScrCmds.statMsg('Current oper: %s is not in the OP_ALLOW_GEMINI_SHUTDOWN:%s' % (self.dut.nextOper, allow_oper))
         else:
            ScrCmds.statMsg('ALLOW_SHUTDOWN or GEMINI_SHUTDOWN_ENABLE is OFF, return')

      return flag
   #------------------------------------------------------------------------------------------------------#
   def end(self,restartFlags=None):
      ''' Final end process '''
      if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
         self.handleIRecoveryAttr()
         if not testSwitch.virtualRun:
            self.handleIRecoveryStatus()
      if restartFlags == None:
         restartFlags = {"doRestart":0,"sendRun":1}
      ScrCmds.statMsg('Status in  Setup %d'%self.dut.Status_GOTF)
      if testSwitch.FE_0131335_220554_NEW_AUD_LODT_FLOW:
         if self.dut.nextOper is 'IDT2' and testSwitch.FE_0221365_402984_RESTORE_OVERLAY:
            objPwrCtrl.EnablePowerCycle()    # Enable power cycle disabled from SDOD
            self.recoverOverlay()
         if self.dut.ExtraOper:
            restartFlags = self.getCSTRestartFlag()
            ReportRestartFlags(restartFlags) # sendRun=1 uses FIS attrs on restart
            return restartFlags
      else:
         if self.dut.LODT:
            restartFlags = self.getCSTRestartFlag()
            ReportRestartFlags(restartFlags) # sendRun=1 uses FIS attrs on restart
            return restartFlags
      self.autoRegUpdate(self.dut.errCode, "%s;%s" % (self.dut.errMsg, self.genExcept))
      
      # Request from Process for OEM / SBS Yield tracking
      if self.dut.driveattr.get('DNGRADE_ON_FLY') in ['SBS'] and self.dut.BG not in ['SBS'] and self.dut.nextOper in ['PRE2']:
         self.dut.driveattr['DNGRADE_ON_FLY'] = 'NONE'
         
      #if self.dut.nextState == 'COMPLETE' and self.dut.Status_GOTF and testSwitch.FE_0120913_347508_FAIL_STATE_INFO_CHANGES: # reset state of drive to 'INIT' if it completed all operations successfully (no power loss)
      if self.dut.nextState == 'COMPLETE':
         self.dut.driveattr["NEXT_STATE"] = 'INIT'
         if int(DriveAttributes.get("LOOPER_COUNT", "0")) >= 1:
            ScrCmds.statMsg('LOOPER_COUNT >= 1, forcing NEXT_STATE=INIT')
            DriveAttributes['NEXT_STATE'] = 'INIT'    # in PRODUCTION_MODE, driveattr["NEXT_STATE"] gets deleted

         self.dut.driveattr['FAIL_STATE'] = 'NONE'
         self.dut.driveattr['FAIL_CODE']  = self.dut.errCode # update failcode attribute to FIS
         self.dut.driveattr['FAIL_TEST']  = self.dut.failTest
      else:

         if self.dut.failureState is 'SPMQM':
            self.dut.driveattr['FAIL_STATE'] = self.dut.spmqm_module # send SPMQM fail module
         else:
            self.dut.driveattr['FAIL_STATE'] = self.dut.failureState # send state_name where test failed
         self.dut.driveattr['FAIL_CODE']  = self.dut.errCode # update failcode attribute to FIS
         self.dut.driveattr['FAIL_TEST']  = self.dut.failTest
         if testSwitch.AutoFA_IDDIS_Enabled:
            self.dut.driveattr['FAIL_OPER']  = self.dut.nextOper

      if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
         if ConfigVars[CN].get('BenchTop', 0):
            ScrCmds.statMsg('IR_RE_OPER = %s, irReOper = %s, IR_StartLastOperUseToFail = %s' % (DriveAttributes.get('IR_RE_OPER','NONE'),getattr(self.dut,'irReOper',False),getattr(self.dut,'IR_StartLastOperUseToFail',False) == True))
         # Calculate IR Test time #########################################
         if getattr(self.dut,'irReOper',False) == True: #IR re-oper attribute detected at first time.
            self.dut.driveattr['TEST_TIME']        = '%.2f' % (time.time() - self.dut.birthtime)
            self.dut.driveattr['BUFFER_TEST_TIME']    = self.dut.driveattr['TEST_TIME']
            ScrCmds.statMsg('iRecovery : Re-Oper detected TEST_TIME and BUFFER_TEST_TIME = %s' % (self.dut.driveattr['TEST_TIME']))
         elif ((DriveAttributes.get('IR_RE_OPER','NONE') == 'RUNNING') and (getattr(self.dut,'irReOper',False) != True)) or \
         (getattr(self.dut,'IR_StartLastOperUseToFail',False) == True): #X-oper detected or IR running in re-oper operation (X-oper)
            try:
               IR_CUM_TEST_TIME = DriveAttributes.get('BUFFER_TEST_TIME',0)
            except:
               IR_CUM_TEST_TIME = 0 # To avoid string sent from system
            IR_TEST_TIME                           = '%.2f' % (time.time() - self.dut.birthtime)
            self.dut.driveattr['TEST_TIME']        = '%.2f' % (float(IR_TEST_TIME) + float(IR_CUM_TEST_TIME))
            self.dut.driveattr['BUFFER_TEST_TIME'] = self.dut.driveattr['TEST_TIME']
            self.dut.driveattr['IR_TEST_TIME']     = IR_TEST_TIME
            ScrCmds.statMsg('iRecovery : Re-Oper detected TEST_TIME = %s, BUFFER_TEST_TIME = %s, IR_TEST_TIME = %s' % (self.dut.driveattr['TEST_TIME'],self.dut.driveattr['TEST_TIME'],self.dut.IR_TEST_TIME ))
         else: #Normal case (no IR re-oper detected)
            self.dut.driveattr['TEST_TIME'] = '%.2f' % (time.time() - self.dut.birthtime)
            ScrCmds.statMsg('Current Operation Test Time = %s' % self.dut.driveattr['TEST_TIME'])
      else:
         self.dut.driveattr['TEST_TIME'] = '%.2f' % (time.time() - self.dut.birthtime)
      if testSwitch.FE_0155956_336764_P_SEND_OPER_TES_TIME_AS_ATTRIBUTE:
         self.dut.driveattr['%s_TEST_TIME'%self.dut.nextOper]  = '%.2f' % (time.time() - self.dut.birthtime)

      if testSwitch.FE_0129273_336764_ENABLE_MFG_EVAL_CTRL and ConfigVars[CN].get('Constant Config Eval',False):
         if ('IDT2' in self.dut.operList and self.dut.nextOper == self.dut.operList[len(self.dut.operList)-2]) or (self.dut.nextOper == self.dut.operList[len(self.dut.operList)-1]):    # last operation
            self.dut.driveattr['MFG_EVAL']  =  '?'
         elif 'IDT2' not in self.dut.operList and self.dut.nextOper == self.dut.operList[len(self.dut.operList)-1]:
            self.dut.driveattr['MFG_EVAL']  =  '?'
         elif self.dut.errCode:
            self.dut.driveattr['MFG_EVAL']  =  '?'
         else:
            self.dut.driveattr['MFG_EVAL']  =  ConfigVars[CN].get('Constant Config Eval','?')

      #For factory FIS failure pareto report breakdown (DO NOT REMOVE)
      self.dut.driveattr['TEST_CODE']     = self.dut.failTest
      self.dut.driveattr['TEST_SEQ']      = str(self.dut.failureState)[:6]  # More descriptive and accurate. FIS limits 6 alphanumeric chars.
      self.dut.driveattr['TEST_SEQ_EVENT']= self.dut.failTestInfo['tstSeqEvt']

      self.dut.driveattr.setdefault('TDCI_COMM_NUM', 0)
      self.dut.driveattr['TDCI_COMM_LIFE'] = int(self.dut.driveattr['TDCI_COMM_LIFE']) + int(self.dut.driveattr['TDCI_COMM_NUM'])

      x = 1
      attrtemp = []
      drvQAtk = self.dut.driveattr['DRV_QA_TRK']
      while x<=5:
        index = 'QA_CTRL' + `x`
        if self.dut.driveattr[index] not in ['NONE']:
          attrtemp.append(self.dut.driveattr[index])
        else:
          if drvQAtk not in ['NONE']:
            drvQAlist = list(drvQAtk)
            attrtemp.append(drvQAlist[x-1])
            self.dut.driveattr[index] = drvQAlist[x-1]
          else:
            attrtemp.append('0')
            self.dut.driveattr[index] = '0'
        x = x + 1
      self.dut.driveattr['DRV_QA_TRK'] = ''.join(attrtemp)
      pgName = ConfigVars[CN].get('PackageControl','UNFY')
      if self.dut.errCode == 0:
         # Process use it to control if the drive with LCT go thrugh the PCO that have actions for OD Erasure/ID offtrack write
         if self.dut.nextOper in ['PRE2']:
            self.dut.driveattr['QA_CTRL100'] = 'P1'
         elif self.dut.nextOper in ['FIN2'] and DriveAttributes.get('QA_CTRL100') in ['P1', 'P1F1']:
            self.dut.driveattr['QA_CTRL100'] = 'P1F1'
            
         #Passed set reconfig on next oper
         if self.dut.nextOper in ['FIN2',] and int(ConfigVars[CN].get('REC_ATTR_CNTRL', 0)) == 1:
            self.dut.driveattr['RECONFIG'] = 1
         elif self.dut.nextOper in ['FIN2',] and int(ConfigVars[CN].get('REC_ATTR_CNTRL', 0)) == 0:
            self.dut.driveattr['RECONFIG'] = 0

         DriveAttributes['DR_REPLUG_CNT'] = 0
         if not testSwitch.FE_0131335_220554_NEW_AUD_LODT_FLOW:
            pat = r'\b%s\w*L\b'%ConfigVars[CN].get('LODT_SBR_PREFIX', 'WU')
            # If drive is with LODT SBR, need set LODT = RUN.
            # Then VMI will onhold this drive. Diag key rework code 3507 to run LODT
            if ConfigVars[CN].get('LODT_ENABLE', 0) and objRimType.CPCRiser(ReportReal = True):
               operList = self.dut.operList
               try:     ignoreOperList = TP.ignoreOperList
               except:   ignoreOperList = ['ODT2', 'IDT2']
               for oper in ignoreOperList:   # IDT2/ODT2 will run QA package.Ignore these two operations
                  if oper in operList:
                     operList.remove(oper)
               # Set LODT to RUN at the last operation of process scripts
               if self.dut.nextOper == operList[-1] and re.search(pat,DriveAttributes.get('SUB_BUILD_GROUP', ''),re.IGNORECASE):
                  self.dut.driveattr['LODT'] = 'RUN'

         if ConfigVars[CN].get('PRODUCTION_MODE',0):
            i, package_control = 1,{}
            # package_control = {'PRE2':1, 'FNC2':2, 'CRT2':3, 'CMT2':4, 'FIN2':5, 'CUT2':'P'}
            for oper in self.dut.operList:
               #if oper == 'SDAT2':
                  #continue
               package_control[oper], i = i, i + 1
            if self.dut.operList[-1] == 'IDT2':
               package_control[self.dut.operList[-2]] = 'P'
            else:
               package_control[self.dut.operList[-1]] = 'P'
            # for pass drive, change ALLONE with specified ID
            self.dut.driveattr['ALLONE'] = '%s%s'%(pgName, package_control[self.dut.nextOper])
      else:
         self.dut.driveattr["NEXT_STATE"] = '?'       # all failures should have NEXT_STATE reset
         if ConfigVars[CN].get('PRODUCTION_MODE',0):
            self.dut.driveattr['ALLONE'] = '%s0'%pgName

      if objRimType.CPCRiser() and not objRimType.CPCRiserNewSpt():
         # Reset the eslip retry counter for the next operation
         try:
            from ICmdFactory import ICmd
            self.dut.driveattr['ESLIP_RTY_COUNT']   = ICmd.EslipRetry()['ERTRYCNT']
            ScrCmds.statMsg('ESLIP retry count reported: %s' % self.dut.driveattr['ESLIP_RTY_COUNT'])
         except:
            pass

      try:
         RMT2obj = CTMX('RMT')  # Sent RMT2 RequestService call to the host
         self.dut.ctmxOp.endStamp() # Close and write CTMX table entry for this operation
         self.dut.ctmxOp.writeDbLog()
      except:
         pass

      #create_P_EVENT_SUMMARY_TABLE(self,errCode=0,failTest='',failV5='',failV12='',failTemp='', failState = '', failData = ''):
      self.create_P_EVENT_SUMMARY_TABLE( self.dut.errCode,
                                         self.dut.failV5,
                                         self.dut.failV12,
                                         self.dut.failTemp,
                                         self.dut.failData,
                                       )

      run_IDDIS = False
      if testSwitch.AutoFA_IDDIS_Enabled and (restartFlags.get('restartOnFail',0) != 1) and len(self.dut.GOTFRetest) == 0:
         if self.dut.errCode not in TP.EC_BYPASS_DDIS:
            iddis_PN_list =ConfigVars[CN].get('IDDIS_PN',[])
            iddis_PN_in_lss_server = (DriveAttributes['PART_NUM'] in iddis_PN_list or DriveAttributes['PART_NUM'][0:3] in iddis_PN_list or 'ALL' in iddis_PN_list)
            cms_support_run_IDDIS = False
            if ConfigVars[CN].has_key('DDIS_Select'):
               if ConfigVars[CN]['DDIS_Select'] in ['FORCED', 'ON' ,'SELECT']:
                  if ConfigVars[CN].has_key('DDIS_EvalName') and ConfigVars[CN]['DDIS_EvalName']:
                     cms_support_run_IDDIS = True
                  else:
                     ScrCmds.statMsg('DDIS_EvalName is not exist or valid')
               else:
                  ScrCmds.statMsg('DDIS_Select is disabled')
            else:
               ScrCmds.statMsg('CMS does not have DDIS_Select')
            if self.dut.errCode != 0 and iddis_PN_in_lss_server and cms_support_run_IDDIS:
               CPU_time = objMsg.getCpuEt(force = True),
               Sz = objMsg.getMemVals(force = True).get('VSZ','0')
               objMsg.printMsg('IDDIS_start CPU_time: %s\tSZ: %s'%(CPU_time,Sz))
               from DbLogAlias import dbLogTableAliases
               for tableName in dbLogTableAliases:
                  try:
                     self.dut.dblData.Tables(tableName).tableDataObj()
                  except:
                     pass
               CPU_time = objMsg.getCpuEt(force = True),
               Sz = objMsg.getMemVals(force = True).get('VSZ','0')
               objMsg.printMsg('IDDIS_EndReadTable CPU_time: %s\tSZ: %s'%(CPU_time,Sz))
               self.writeDBLogToFile()
               CPU_time = objMsg.getCpuEt(force = True),
               Sz = objMsg.getMemVals(force = True).get('VSZ','0')
               objMsg.printMsg('IDDIS_end CPU_time: %s\tSZ: %s'%(CPU_time,Sz))
               run_IDDIS = True

      if testSwitch.BF_0133084_231166_DYNAMIC_ATTR_PARAM_REDUCTION:
         self.writeParametricData() # DBLog parametric dump to XML results file
      else:
         self.writeParametricData() # DBLog parametric dump to XML results file
         if not (self.dut.errCode == 11891 or self.dut.errCode == 11887):
            self.dut.updateFISAttr()   # update all FIS attributes in one go

      #self.SaveResultFile()      # Save result files onto local
      #self.SaveRunHistory(time.time() - self.dut.birthtime, self.dut.errCode) # save run history log

      if self.dut.forceMove:
         restartFlags.update({"forceCellChange":1})

      restartFlags.update(self.handleIDTSlot(restartFlags))

      restartFlags.update(self.holdDriveEval())

      #restartFlags.update(self.checkSdatRestart())

      if ConfigVars[CN].get('ALLOW_HOLD_RESTART',1) == 1 and restartFlags.get('doRestart',0) == 1 and restartFlags.get('holdDrive',0) == 1:
         #RPM 14.01-11 will not allow holdDrives do perform restarts.  Need to disable holdDrive to allow restart.
         restartFlags['holdDrive'] = 0
      if ConfigVars[CN].get('DISABLE_FIS_UPLOAD',0):
         restartFlags.update({"sendRun":0}) # sendRun=4 => use local attrs on restart
         ScrCmds.statMsg('Set sendRun = 0 to disable sending of FIS EVENT')

      if len(self.dut.GOTFRetest) > 0:
         ScrCmds.statMsg('GOTF Retest begin : %s' % self.dut.GOTFRetest)
         evalOpType = self.dut.GOTFRetest.get('NO_YIELD_REPORT', "") + self.dut.nextOper
         self.dut.GOTFRetest.pop('NO_YIELD_REPORT', None)
         RequestService('SetOperation', (evalOpType,))
         DriveAttributes.update(self.dut.GOTFRetest)

         if self.dut.RetestPN != None:
            pnbackup = DriveAttributes['PART_NUM']
            DriveAttributes['PART_NUM'] = self.dut.RetestPN
            ScrCmds.statMsg('PART_NUM attr: %s' % DriveAttributes['PART_NUM'])

         RequestService('SendRun',(1,))
         ReportErrorCode(0)               # needed or Gemini will not auto restart

         if self.dut.RetestPN != None:
            DriveAttributes['PART_NUM'] = pnbackup
         restartFlags = {'doRestart': 1, 'sendRun': 0}
      else:

         ScrCmds.statMsg('self.dut.errCode: %s' % self.dut.errCode)
         ScrCmds.statMsg('self.dut.operList: %s' % self.dut.operList)
         ScrCmds.statMsg('self.dut.nextOper: %s' % self.dut.nextOper)

         if (self.dut.errCode != 0 or self.dut.operList[-1] == self.dut.nextOper) and self.dut.nextOper != "CCV2":
            ScrCmds.statMsg('LOOPER_COUNT set to 0 for fail drive or last operation')
            DriveAttributes['LOOPER_COUNT'] = '0'

      if testSwitch.AutoFA_IDDIS_Enabled and (restartFlags.get('restartOnFail',0) != 1) and len(self.dut.GOTFRetest) == 0:
         if run_IDDIS:
            DriveAttributes['RESUME_MFG_EVAL'] = DriveAttributes.get('MFG_EVAL','?')
            DriveAttributes['MFG_EVAL'] = '?'
            restartFlags = {'doRestart':1,'sendRun':4,"restartOnFail":1,'configEval':ConfigVars[CN]['DDIS_EvalName']}


      DriveOff(10)

      if testSwitch.SEND_OPERATION_METRICS:
         cpuET = objMsg.getCpuEt(force = True)
         cpuMetric = round(cpuET/float(self.dut.driveattr['TEST_TIME']),6)
         DriveAttributes['CPU_METRIC'] = cpuMetric

         memMetric = objMsg.getMemVals(force = True)
         DriveAttributes['SZ'] = memMetric.get('VSZ', '?')
         DriveAttributes['RSS'] = memMetric.get('RSS', '?')

      holdDriveEC = ConfigVars[CN].get('holdDriveEC',[])
      if self.dut.errCode in holdDriveEC:
         ScrCmds.statMsg('HOLD DRIVE !')
         restartFlags.update({'holdDrive':1})
      else:
         ScrCmds.statMsg('DO NOT HOLD DRIVE !')
      ScrCmds.statMsg('restartFlags: %s' % restartFlags)

      import DbLog
      finDict = self.createFinalTestTimeByStateDict(segment = "END", seq = self.dut.seqNum , startDict = self.startRef, endDict = self.createEndStateData())
      tmpDb = DbLog.DbLog(self.dut)
      tmpDb.setOracleMode(1)
      tmpDb.Tables('TEST_TIME_BY_STATE').addRecord(finDict)
      TTBSStr = str(tmpDb.Tables('TEST_TIME_BY_STATE'))
      XmlResultsFile.open('rb')

      XmlResultsFile.seek(-1, 2) #Seek to end -1
      val = XmlResultsFile.read(1)
      for x in xrange(50): #give it 50 tries to find the xml termination
         if val == '<': #1 step forward
            break

         XmlResultsFile.seek(-2, 1) #2 steps back
         val = XmlResultsFile.read(1)
      else:
         ScrCmds.raiseException(11044, "Invalid XML file: Can not find < for xml termination.")

      pos = XmlResultsFile.tell()
      XmlResultsFile.close()

      #cur byte should now be '<'
      XmlResultsFile.open('rb')
      data = XmlResultsFile.read(pos-1)

      XmlResultsFile.close()
      XmlResultsFile.open('wb')
      XmlResultsFile.write(data)
      del data
      XmlResultsFile.write(TTBSStr)
      XmlResultsFile.write('</parametric_dblog>')
      XmlResultsFile.close()

      self.dut.dblData.Tables('TEST_TIME_BY_STATE').addRecord(finDict)
      ScrCmds.statMsg(self.dut.dblData.Tables('TEST_TIME_BY_STATE'))    # Log Service compatibility

      if ConfigVars[CN].get('RELOAD_CONFIG',1) == 0:
         if not (ConfigVars[CN].get('ADG_ENABLE', 0) and self.dut.errCode != 0):
            if restartFlags.get('sendRun', 0) != 0:
               RequestService('SendRun', restartFlags['sendRun'])
               ScrCmds.statMsg('SendRun: %s' % restartFlags['sendRun'])
            restartFlags['sendRun'] = 2
      if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
         if not testSwitch.virtualRun:
            self.handleIRerror()

      if self.CheckGeminiShutdown():
         restartFlags['doRestart'] = 0
      ReportRestartFlags(restartFlags) # sendRun=1 uses FIS attrs on restart

      #ADG - autodiag
      # if ConfigVars[CN].get('ADG_ENABLE', 0):
         # if self.dut.errCode != 0:
            # cnt =int(DriveAttributes.get('DEBUG_CNT',0))
            # objMsg.printMsg('debug cnt is %d' % int(cnt))
            # RequestService('SendRun', 1)
            # restartFlags.update({"doRestart":1,"sendRun":3})
            # ReportRestartFlags(restartFlags)
            # retry = 0
            # time.sleep(180)
            # while(retry < 5): #total wait time 15 minutes
               # if testSwitch.BF_0124078_347508_PHARAOH_MASS_PRO_ADG_SETUP:
                  # name, data = RequestService('GetAttributes', ('RESTART_REQ', 'DEBUG_CNT'))
                  # if data['RESTART_REQ'] not in ['UNKNOWN', 'NONE', '']:
                     # #If ADG requests a restart
                     # restartFlags['sendRun'] = 5
                     # if ConfigVars[CN].get('RELOAD_CONFIG',1) == 0:
                        # restartFlags['sendRun'] = 2

                     # #refresh local Attr as ADG recommand
                     # ADGAttr =('RIM_TYPE', 'DEPOP_REQ','VALID_OPER','SET_OPER','SUB_BUILD_GROUP','PART_NUM','BUILD_GROUP','DRIVE_RIDE','REWORK_CODE')
                     # name, ADGdata = RequestService('GetAttributes', ADGAttr)
                     # tempdict={}
                     # for key in ADGAttr:
                        # if ADGdata[key] !='UNKNOWN':
                           # tempdict[key]=ADGdata[key]
                     # DriveAttributes.update(tempdict)

                     # #Force restart
                     # restartFlags["doRestart"] = 1

                     # ReportErrorCode(0) #to prevent unload
                     # ReportRestartFlags(restartFlags) # sendRun=1 uses FIS attrs on restart
                     # break
                  # #Debug is complete since cnt was incremented
                  # if data['DEBUG_CNT'] !='UNKNOWN' and int(data['DEBUG_CNT']) >cnt:
                     # objMsg.printMsg('ADG already update attributes, exit waiting')
                     # break
               # else:
                  # name, data = RequestService('GetAttributes', ('RESTART_REQ', 'DEPOP_REQ',))
                  # if data['RESTART_REQ'] != 'UNKNOWN' or data['DEPOP_REQ'] != 'UNKNOWN': # FIS attributes not defined - not likely
                     # if data['RESTART_REQ'] != 'NONE' or data['DEPOP_REQ'] != 'NONE':
                        # if data['RESTART_REQ'] != '' or data['RESTART_REQ'] != '':
                           # restartFlags.update({"doRestart":1,"sendRun":0})
                           # RequestService('SendRun', 1)
                           # if ConfigVars[CN].get('RELOAD_CONFIG',1) == 0:
                              # restartFlags['sendRun'] = 2

                  # else:
                     # #refresh local Attr as ADG recommand
                     # ADGAttr =('RIM_TYPE', 'DEPOP_REQ','VALID_OPER','SET_OPER','SUB_BUILD_GROUP','PART_NUM','BUILD_GROUP','DRIVE_RIDE','REWORK_CODE')
                     # name, ADGdata = RequestService('GetAttributes', ADGAttr)
                     # tempdict={}
                     # for key in ADGAttr:
                        # if ADGdata[key] !='UNKNOWN':
                           # tempdict[key]=ADGdata[key]
                     # DriveAttributes.update(tempdict)
                     # restartFlags.update({"doRestart":1,"sendRun":5})

                     # ReportErrorCode(0) #to prevent unload
                     # ReportRestartFlags(restartFlags) # sendRun=1 uses FIS attrs on restart
                     # break
               # if data['DEBUG_CNT'] !='UNKNOWN' and int(data['DEBUG_CNT']) >cnt:
                  # objMsg.printMsg('ADG already update attributes, exit waiting')
                  # break
               # time.sleep(180) # wait for 3 mins
               # retry += 1

      if testSwitch.virtualRun:
         try:
            from performanceProfile import createOperationProfile
            createOperationProfile(self.dut)
         except:
            pass
         if self.dut.nextOper =='CUT2':
            # CParamSummaryCreation does a deepcopy of every single parameter
            # and then modifies the copied parameter.
            # So, create the parameter summary at the very end of VE process
            # in order to avoid future inadvertant param changes affecting VE
            # As of 2010-11 the deepcopy method has no side effects, copy did
            # however, which is why deepcopy is instead used.
            from TestParamExtractor import CParamSummaryCreation
            CParamSummaryCreation().run()

      return restartFlags

   #----------------------------------------------------------------------------------------------------------#
   def checkCM_LoadAvg(self):
      import random
      checkLoadAvg = 0
      lastTimeSleep = 0
      sumSleepTime = 0
      try:
         CmLoadSpec = map(float,ConfigVars[CN].get('CmLoadSpec',[10.0,10.0,10.0]))  # spec for 1, 5 and 15 min CM load averages from /proc/loadavg.
         CmLoadTimeLimit = int(ConfigVars[CN].get('CmLoadTimeLimit',5))           # total accumulated sleep time limit

         while checkLoadAvg:
            loadAVG = map(float,GetLoadAverage())
            objMsg.printMsg("CM Load average = %s"%str(GetLoadAverage()))
            objMsg.printMsg("One minute CM load average = %3.2f" %(loadAVG[0]))
            objMsg.printMsg("Load limit = %2.1f" %CmLoadSpec[2])

            if loadAVG[0] >= CmLoadSpec[2]:
               sleepTime = 5
               objMsg.printMsg("Sleep Time = %d minutes"%(sleepTime))
               time.sleep(sleepTime*60) # sleep time 5 minutes
               sumSleepTime += sleepTime
               lastTimeSleep = 1
            else:
               break

            if lastTimeSleep:
               lastTimeSleep = 0
               sleepTime = 1
               objMsg.printMsg("Sleeping for %d minute."%(sleepTime))
               time.sleep(sleepTime*60)
               sumSleepTime += sleepTime
               loadAVG = map(float,GetLoadAverage())

               objMsg.printMsg("Load average = %f"%(loadAVG[0]))
               if loadAVG[0] <= CmLoadSpec[2]:
                  objMsg.printMsg("CM Load is less than spec, so continue test")
                  checkLoadAvg = 0

            if checkLoadAvg == 1 and (sumSleepTime >= CmLoadTimeLimit):
               checkLoadAvg = 0
               objMsg.printMsg("Sleep time is over limit : %s mins, So Continue test" %sumSleepTime)
      except:
         objMsg.printMsg("CM_LoadAvg feature not supported %s" %traceback.format_exc())

   if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
      #------------------------------------------------------------------------------------------------------#
      def handleIRecoveryStatus(self):
         '''info'''
         strBuf = ""
         objMsg.printMsg("iRecovery : self.dut.PendingMerge2_IR_RUN_LIST : %s" %(self.dut.PendingMerge2_IR_RUN_LIST))
         IR_EC_PendingMergeList = [e for e in self.dut.PendingMerge2_IR_RUN_LIST.split('/') if (len(e)>0 and e != 'NEVER')]
         for i in range(1,len(IR_EC_PendingMergeList)+1):
            strBuf = strBuf + IR_EC_PendingMergeList[i-1] +'/'
            if i%iRecovery_RUN_LIST_perAttr == 0 and i > 0:
               cmd    = 'DriveAttributes["IR_RUN_LIST_%s"] = "%s"' %(self.dut.IR_RUN_LIST_startIndex,strBuf[0:-1])
               objMsg.printMsg("iRecovery : Sending EC that IR used to perform")
               objMsg.printMsg(cmd)
               exec(cmd)
               strBuf = ""
               self.dut.IR_RUN_LIST_startIndex = self.dut.IR_RUN_LIST_startIndex + 1
         if strBuf != "":
            cmd    = 'DriveAttributes["IR_RUN_LIST_%s"] = "%s"' %(self.dut.IR_RUN_LIST_startIndex,strBuf[0:-1])
            objMsg.printMsg("iRecovery : Sending EC that IR use to perform")
            objMsg.printMsg(cmd)
            exec(cmd)
            strBuf = ""
         else:
            if self.dut.IR_RUN_LIST_startIndex == 0:
               cmd = 'DriveAttributes["IR_RUN_LIST_0"] = "NEVER"'
               objMsg.printMsg("iRecovery : Sending EC that IR use to perform")
               objMsg.printMsg(cmd)
               exec(cmd)


         DriveAttributes['IR_RUN_CNT'] = self.dut.IR_RUN_CNT

         if self.dut.nextOper == 'CUT2' and self.dut.errCode == 0 and (self.IR_STATUS_VALUE == 'PASS' or self.local_ir_status_val == 'PASS'):
            DriveAttributes['IR_EFFECTIVE'] = 'Y'
         elif self.dut.errCode != 0 and (self.IR_STATUS_VALUE in ['PASS','FAIL','EXCURSION'] or self.local_ir_status_val in ['PASS','FAIL','EXCURSION']) and getattr(self.dut,'irReOper',False) == False and getattr(self.dut,'irReplug',False) == False:
            DriveAttributes['IR_EFFECTIVE'] = 'N'
         if base_RecoveryTest.IR_XprefixWhenStartOriginalFailOper and getattr(self.dut,'IR_StartLastOperUseToFail',False):
            objMsg.printMsg('iRecovery : Set Operation back to %s'%self.dut.nextOper)
            RequestService('SetOperation',(self.dut.nextOper,))
            DriveAttributes['IR_SAMEOPER']   = 'DONE'
            DriveAttributes['IR_ACTIVE']     = 'Y'
            DriveAttributes['IR_FAIL_EC']    = DriveAttributes.get('IR_FAIL_EC'  ,'NONE')
            DriveAttributes['IR_FAIL_OPER']  = DriveAttributes.get('IR_FAIL_OPER','NONE')
            DriveAttributes['IR_CMS_CONFIG'] = self.dut.driveattr['CMS_CONFIG']
         if base_RecoveryTest.IR_ReportFirstEC:
            if self.dut.errCode != 0 and getattr(self.dut,'irReOper',False) == False and self.IR_REOPER_VALUE == 'RUNNING':
               if base_RecoveryTest.IR_HybridReportEC:
                  if self.IR_BF_OPER_VALUE != self.dut.nextOper:
                     objMsg.printMsg('iRecovery : Fail during Re-Oper report original ErrorCode')
                     RequestService('SetOperation',('X'+ self.dut.nextOper,))
                     ReportErrorCode(self.dut.errCode)
                     #Send attributes and parametrics
                     RequestService('SendRun', 1)
                     #Reset to the primary operation
                     ReportOper = self.IR_BF_OPER_VALUE
                     ReportEC   = base_RecoveryTest.IR_ErrorCode
                     RequestService('SetOperation', (ReportOper,)) # Set station name
                     DriveAttributes['IR_ACTIVE']     = 'Y'
                     DriveAttributes['IR_FAIL_EC']    = DriveAttributes.get('IR_FAIL_EC'  ,'NONE')
                     DriveAttributes['IR_FAIL_OPER']  = DriveAttributes.get('IR_FAIL_OPER','NONE')
                     DriveAttributes['IR_CMS_CONFIG'] = self.dut.driveattr['CMS_CONFIG']
               else :
                  objMsg.printMsg('iRecovery : Fail during Re-Oper report original ErrorCode')
                  RequestService('SetOperation',('X'+ self.dut.nextOper,))
                  ReportErrorCode(self.dut.errCode)
                  #Send attributes and parametrics
                  RequestService('SendRun', 1)
                  #Reset to the primary operation
                  ReportOper = self.IR_BF_OPER_VALUE
                  ReportEC   = self.IR_BF_EC_VALUE
                  RequestService('SetOperation', (ReportOper,)) # Set station name
                  DriveAttributes['IR_ACTIVE']     = 'Y'
                  DriveAttributes['IR_FAIL_EC']    = DriveAttributes.get('IR_FAIL_EC'  ,'NONE')
                  DriveAttributes['IR_FAIL_OPER']  = DriveAttributes.get('IR_FAIL_OPER','NONE')
                  DriveAttributes['IR_CMS_CONFIG'] = self.dut.driveattr['CMS_CONFIG']
         else:
            if self.dut.errCode != 0 and self.IR_REOPER_VALUE == 'RUNNING' and getattr(self.dut,'irReOper',False) == False and getattr(self.dut,'irReplug',False) == False:
                  objMsg.printMsg('iRecovery : Fail during Re-Oper report last ErrorCode')
                  RequestService('SetOperation',(self.dut.nextOper,))
         if self.dut.PendingMerge2_IR_NAME_LIST != '': # Perform iRecovery in current running oper.
            for IR_NAME in self.dut.PendingMerge2_IR_NAME_LIST.split('/') :
               if len(IR_NAME) > 2:
                  nextIRVersion = IR_NAME[0:2]
                  if nextIRVersion != base_RecoveryTest.IR_DefaultName[0:2]:   # Indicated that detect integer in current IR_NAME.
                     try:
                        if self.IR_VERSION_VALUE in ['N',base_RecoveryTest.IR_DefaultVersion]: # Have no version
                           self.IR_VERSION_VALUE = int(nextIRVersion)
                        elif int(nextIRVersion) > int(self.IR_VERSION_VALUE):
                           self.IR_VERSION_VALUE = int(nextIRVersion)
                     except:
                        self.IR_VERSION_VALUE = 'NAME_ERROR'
                        break
            DriveAttributes['IR_VERSION'] = self.IR_VERSION_VALUE

      #------------------------------------------------------------------------------------------------------#
      def handleIRerror(self):
         if self.IR_REOPER_VALUE == 'RUNNING' and self.dut.errCode != 0 and getattr(self.dut,'irReOper',False) == False:
            objMsg.printMsg("Report IR failure, Try to report new EC first")
            if base_RecoveryTest.IR_ReportFirstEC:
               if base_RecoveryTest.IR_HybridReportEC:
                  if self.IR_BF_OPER_VALUE != self.dut.nextOper:
                     objMsg.printMsg("Report IR error")
                     ReportErrorCode(base_RecoveryTest.IR_ErrorCode)
                     DriveAttributes['IR_ACTIVE']     = 'Y'
                     DriveAttributes['IR_FAIL_EC']    = DriveAttributes.get('IR_FAIL_EC'  ,'NONE')
                     DriveAttributes['IR_FAIL_OPER']  = DriveAttributes.get('IR_FAIL_OPER','NONE')
                     DriveAttributes['IR_CMS_CONFIG'] = self.dut.driveattr['CMS_CONFIG']
               else:
                  objMsg.printMsg("Report IR original failure")
                  ReportEC = self.IR_BF_EC_VALUE
                  ReportErrorCode(ReportEC)
                  DriveAttributes['IR_ACTIVE']     = 'Y'
                  DriveAttributes['IR_FAIL_EC']    = DriveAttributes.get('IR_FAIL_EC'  ,'NONE')
                  DriveAttributes['IR_FAIL_OPER']  = DriveAttributes.get('IR_FAIL_OPER','NONE')
                  DriveAttributes['IR_CMS_CONFIG'] = self.dut.driveattr['CMS_CONFIG']
            if base_RecoveryTest.IR_HybridReportEC:
               DriveAttributes['IR_ADG_DISPOSE'] = 'DONE'
            DriveAttributes['IR_RE_OPER']        = 'DONE'
            DriveAttributes['FAIL_OPER']         = self.dut.nextOper
            DriveAttributes['IR_BF_OPER']        = 'NONE'
            DriveAttributes['IR_BF_EC']          = 'NONE'
            DriveAttributes['IR_BF_STATE']       = 'NONE'
            DriveAttributes['IR_BF_TEST']        = 'NONE'

   #------------------------------------------------------------------------------------------------------#
   def sendParametricData(self):
      """
      @return: Returns flag=1 if drive is selected to send parametric data
      """
      flag = 0

      try:
         hsa_coh_dict         = ConfigVars[CN].get('SEND_PARAM_HSA_COH',  {}    )
         sub_build_grp_list   = ConfigVars[CN].get('SEND_PARAM_SBR_CHAR', []    )    # List of chars to match with 5th char of SUB_BUILD_GROUP
         serial_num_list      = ConfigVars[CN].get('SEND_PARAM_SN_CHAR',  ['ALL',] ) # List of s/n char to match with last 2 chars of HDASerialNumber

         attr_HSA_COH         = DriveAttributes.get('HSA_COH','')
         attr_SUB_BUILD_GROUP = DriveAttributes.get('SUB_BUILD_GROUP','')

         try:
            from PIF import SEND_PARAM_PART_NUM
            partnum_list  = SEND_PARAM_PART_NUM
         except:
            partnum_list  = []


         # (2) 1st char of HSA_COH = 'O'
         # (3) 6th char of HSA_COH = 'S'
         # (4) 1st-5th char of HSA_COH in the list
         hsa_coh_match = 0
         ScrCmds.statMsg("Drive HSA : %s - SEND_PARAM_HSA_COH : %s" % (attr_HSA_COH, hsa_coh_dict))
         try:
            for key in hsa_coh_dict:
               charStart,charSize = key
               startPoint = charStart - 1
               endPoint   = charStart + charSize - 1
               hsa_coh_chars = attr_HSA_COH[startPoint:endPoint]

               msg = "Drive HSA : %s - Char Start Positon:%s / Size:%s - " % (attr_HSA_COH, charStart, charSize)
               if hsa_coh_chars in hsa_coh_dict[key]:
                  msg += "%s in %s - HSA_COH Match" % (hsa_coh_chars, hsa_coh_dict[key])
                  ScrCmds.statMsg(msg)
                  hsa_coh_match = 1
                  ###############################################break
               else:
                  msg += "%s not in %s - HSA_COH do not Match" % (hsa_coh_chars, hsa_coh_dict[key])
                  ScrCmds.statMsg(msg)
         except:
            hsa_coh_match = 0
            ScrCmds.statMsg("HSA_COH Exception")


         # (1) 7th or 8th char of SerialNum in selected list
         # (5) 5th char of SUB_BUILD_GROUP in selected list
         # (6) PartNum
         if ('ALL' in serial_num_list) or \
            (len(attr_HSA_COH) == 5 and attr_HSA_COH[0] == 'O') or \
            (len(attr_HSA_COH) == 6 and attr_HSA_COH[0] == 'O' and attr_HSA_COH[5] == 'S') or \
            (HDASerialNumber[6] in serial_num_list) or \
            (HDASerialNumber[7] in serial_num_list) or \
            hsa_coh_match or \
            (len(attr_SUB_BUILD_GROUP) > 4 and attr_SUB_BUILD_GROUP[4] in sub_build_grp_list) or \
            (self.dut.partNum in partnum_list):
            flag = 1

      except:
         flag = 1
      if flag == 1 and testSwitch.FE_0143655_345172_P_SPECIAL_SBR_ENABLE and self.dut.spSBG.sp_SBG:
         if self.dut.spSBG.spSBGParametrics:   #SBR Control By script => Parametric.
            ScrCmds.statMsg("Special SBR Condition 1 -Enable load drive parametric (100%).")
            TP.parametric_no_load = []
         else:
            ScrCmds.statMsg("Special SBR Condition 1 -Disable load drive parametric (100%).")
            ScrCmds.statMsg('SendParametrics DISABLED')

      try:
         if self.dut.evalMode.upper() == 'ON':
            ScrCmds.statMsg("Drive SN       : %10s - SEND_PARAM_SN_CHAR  : %s" % (HDASerialNumber, serial_num_list))
            ScrCmds.statMsg("Drive SBR      : %10s - SEND_PARAM_SBR_CHAR : %s" % (attr_SUB_BUILD_GROUP, sub_build_grp_list))
            #ScrCmds.statMsg("Drive HSA      : %10s - SEND_PARAM_HSA_COH  : %s" % (attr_HSA_COH, hsa_coh_dict))
            ScrCmds.statMsg("Drive PART_NUM : %10s - SEND_PARAM_PART_NUM : %s" % (self.dut.partNum, partnum_list[0:5]))
            ScrCmds.statMsg("Drive PARM     : %s" % (flag, ))
      except:
         pass

      return flag

   if testSwitch.AutoFA_IDDIS_Enabled:
      def saveIDDISDBlog(self, FileNo,data,MAX_TUPLE_SIZE = 1024*384L):
         dblog_filename = 'dbl_%s_%s' % (HDASerialNumber,str(FileNo))
         objMsg.printMsg("%s,len(data):%s"%(dblog_filename,len(str(data))))
         if len(str(data)) > MAX_TUPLE_SIZE:
            objMsg.printMsg("DBLog Saved Failed,data is too big.")
            return 1
         RequestService('PutTuple',(dblog_filename, data))
         objMsg.printMsg("DBLog %s Saved Successfully."%dblog_filename)
         return 0
      #------------------------------------------------------------------------------------------------------#
      def writeDBLogToFile(self):
         MAX_TUPLE_SIZE = 1024*384L
         FileNo = 0
         mydata = self.dut.dblData.getAllTableDataList()
         AddRecordTables = {}
         for table in getattr(TP,'IDDISTables', ['P_SIDE_ENCROACH_BER','TEST_TIME_BY_STATE']):
            try:
               AddRecordTables[table] = self.dut.dblData.Tables(table).tableDataList()
            except:
               objMsg.printMsg('Debug: fail. Traceback=%s' % traceback.format_exc())
         if AddRecordTables:
            mydata.update(AddRecordTables)
         saveDict = {}
         CPU_time = objMsg.getCpuEt(force = True),
         Sz = objMsg.getMemVals(force = True).get('VSZ','0')
         objMsg.printMsg('IDDIS_getTable CPU_time: %s\tSZ: %s'%(CPU_time,Sz))
         if len(str(mydata)) <= MAX_TUPLE_SIZE:
            isFail = self.saveIDDISDBlog(FileNo+1,mydata)
            if not isFail:
                FileNo += 1
         else:
           mydata = sorted(mydata.items(),key = lambda x:len(str({x[0]:x[1]})))
           mydata = [(item[0],item[1],len(str({item[0]:item[1]}))) for item in mydata]
           #for dt in mydata:
                #objMsg.printMsg("%s,%s"%(dt[0],dt[2]))

           CPU_time = objMsg.getCpuEt(force = True),
           Sz = objMsg.getMemVals(force = True).get('VSZ','0')
           objMsg.printMsg('IDDIS_SortedTable CPU_time: %s\tSZ: %s'%(CPU_time,Sz))
           filelen = 0
           indexlist = []
           for index,value in enumerate(mydata):
               if filelen + value[2] <= MAX_TUPLE_SIZE:
                   indexlist.append(index)
                   filelen += value[2]
               else:
                   if len(indexlist) and filelen:
                       saveDict = {}
                       for item in indexlist:
                           saveDict[mydata[item][0]] = mydata[item][1]
                       else:
                           isFail = self.saveIDDISDBlog(FileNo+1,saveDict)
                           if not isFail:
                              FileNo += 1
                       if value[2] > MAX_TUPLE_SIZE:
                           saveDict = {value[0]:[]}
                           filelen = len(str(saveDict))
                           for item in value[1]:
                               if filelen + len(str(item)) <= MAX_TUPLE_SIZE:
                                   saveDict[value[0]].append(item)
                                   filelen += len(str(item))+2
                               else:
                                   isFail = self.saveIDDISDBlog(FileNo+1,saveDict)
                                   if not isFail:
                                       FileNo += 1
                                   saveDict = {value[0]:[item]}
                                   filelen = len(str(saveDict))
                           else:
                               isFail = self.saveIDDISDBlog(FileNo+1,saveDict)
                               if not isFail:
                                   FileNo += 1
                               indexlist = []
                               filelen = 0
                       else:
                           if index == len(mydata)-1:
                              isFail = self.saveIDDISDBlog(FileNo+1,{value[0]:value[1]})
                              if not isFail:
                                   FileNo += 1
                           else:
                               filelen = value[2]
                               indexlist = [index]
                   elif value[2] > MAX_TUPLE_SIZE:
                           saveDict = {value[0]:[]}
                           filelen = len(str(saveDict))
                           for item in value[1]:
                               if filelen + len(str(item)) <= MAX_TUPLE_SIZE:
                                   saveDict[value[0]].append(item)
                                   filelen += len(str(item))+2
                               else:
                                   isFail = self.saveIDDISDBlog(FileNo+1,saveDict)
                                   if not isFail:
                                       FileNo += 1
                                   saveDict = {value[0]:[item]}
                                   filelen = len(str(saveDict))
                           else:
                               isFail = self.saveIDDISDBlog(FileNo+1,saveDict)
                               if not isFail:
                                   FileNo += 1
                               indexlist = []
                               filelen = 0
         del saveDict
         del mydata
         objMsg.printMsg("Total %s DBLog Files Saved."%FileNo)
         if FileNo:
            objMsg.printMsg("All DBLog Saved Successfully.")
            DriveAttributes['DBLOGCNT'] = FileNo
         try:
            try:
               P159_FIFO = self.dut.FIFO
            except:
               P159_FIFO = []
            ERRMSG = {'errMsg':self.dut.errMsg,'P159_FIFO':P159_FIFO}
            ERRMSG.update( getattr(self.dut, 'iDDIS_Info', {}))
            self.saveIDDISDBlog('ERRMSG',ERRMSG)
            objMsg.printMsg("self.dut.errMsg Saved Successfully.")
         except:
            objMsg.printMsg("Saved Fail6.")
         CPU_time = objMsg.getCpuEt(force = True),
         Sz = objMsg.getMemVals(force = True).get('VSZ','0')
         objMsg.printMsg('IDDIS_ForMydata CPU_time: %s\tSZ: %s'%(CPU_time,Sz))


   #------------------------------------------------------------------------------------------------------#
   def writeParametricData(self):
      try:
         self.dut.overlayHandler.addOverlayDblog()

         #Save dblIndexes for reset and debug
         self.dut.dblParser.objDbLogIndex.streamIndexFile()
      except:
         pass

      # Import self-test table definitions for parametric upload to oracle
      sys.path.append(ScrCmds.getSystemParamsPath())

      mediaMapValid = False
      driveInfoFound = False
      zoneTableFound = False
      if self.dut.nextOper == 'FNC2' or self.dut.nextOper == 'PRE2':
         for tables in self.dut.stateDBLogInfo.values():
            tables = set(tables)
            if not driveInfoFound and 'P172_DRIVE_INFO' in tables:
               driveInfoFound = True
            if not zoneTableFound and TP.zone_table['table_name'] in tables:
               zoneTableFound = True
            if not mediaMapValid and tables.intersection(('P107_VERIFIED_FLAW_LENGTH', 'P126_SRVO_FLAW_REP', \
                                                          'P130_PLIST_DETAILED', 'P130_SYS_SLIST_DETAILED')):
               mediaMapValid = True
            if driveInfoFound and zoneTableFound and mediaMapValid:
               break

      if driveInfoFound and zoneTableFound and mediaMapValid:
         DriveAttributes['MEDIA_MAP'] = 'TRUE'
      else:
         DriveAttributes['MEDIA_MAP'] = 'FALSE'

      # Import process table definitions for parametric upload to oracle
      from DBLogDefs import DbLogTableDefinitions
      # Define dblog offsets into the table definitions
      dblogDefOffset = 1
      dblogDefTableNameOffset = 0
      # Initialize the list of table names to include in the parametric output with self-test tables
      paramNames = [item[dblogDefOffset][dblogDefTableNameOffset] for item in tableHeaders.items()]
      # Add the process table names that go to oracle
      for procTable in DbLogTableDefinitions.OracleTables.keys():
         paramNames.append(procTable)

      try:
         # 'VOLUME_CONFIG_FLAG'  : '_VOL'
         volume_config_flag = ConfigVars[CN].get('VOLUME_CONFIG_FLAG', '')
         configName = CN
         # 'SEND_TABLE_SN_INDEX' : [7, 8]
         # 'SEND_TABLE_SN_CHAR'  : ['A', 'K']
         sn_index_list = ConfigVars[CN].get('SEND_TABLE_SN_INDEX', [])
         sn_char_list  = ConfigVars[CN].get('SEND_TABLE_SN_CHAR',  [])

         # Not the volume config. Send 'TEST_TIME_BY_TEST' table
         if (not volume_config_flag) or (configName.find(volume_config_flag) < 0):
            send_table = 1
         else:
            send_table = 0
            for index in sn_index_list:
               if HDASerialNumber[index-1] in sn_char_list:
                  send_table = 1
                  break
      except:
         send_table = 1

      try:
         if self.dut.evalMode.upper() == 'ON':
            ScrCmds.statMsg("Config Name : %s - VOLUME_CONFIG_FLAG : %s" % (configName, volume_config_flag))
            ScrCmds.statMsg("Drive SN    : %s - SEND_TABLE_SN_INDEX : %s - SEND_TABLE_SN_CHAR : %s" % (HDASerialNumber, sn_index_list, sn_char_list))
            ScrCmds.statMsg("Drive Table TEST_TIME_BY_TEST send_table : %s" % (send_table, ))
      except:
         pass

      # Import the tables we don't want to load to oracle for this program
      parametric_no_load = getattr(TP,'parametric_no_load',[])
      tableNameList = [x[0] for x in parametric_no_load]
      if (not send_table) and ('TEST_TIME_BY_TEST' not in tableNameList):
         ScrCmds.statMsg("Original Parametric Table %s will not be updated into FIS." % (parametric_no_load,))
         parametric_no_load.append(('TEST_TIME_BY_TEST',0))
         ScrCmds.statMsg("Modified Parametric Table %s will not be updated into FIS." % (parametric_no_load,))

      # Remove the tables that we don't want to upload to oracle for this program
      if testSwitch.BF_0144790_231166_P_FIX_GOTF_DBL_REGRADE_DUP_ROWS:
         #remove the tables marked for deletion
         # this includes regrade tables from prior oper.
         self.dut.dblData.removeMarkedForDeleteTables()

      self.dut.noLoad = []
      for nLoadTable in parametric_no_load:
         self.dut.noLoad.append(nLoadTable[0])
         if nLoadTable[0] in paramNames:
            del paramNames[paramNames.index(nLoadTable[0])]
      objMsg.printMsg("parametric_no_load = %s" % self.dut.noLoad, objMsg.CMessLvl.IMPORTANT)

      if not (testSwitch.WA_0115021_231166_DISABLE_WRITING_RESULTS_FILE_TO_DUT or (
         testSwitch.BF_0138112_231166_P_RESET_SOM_STATE_IN_ENDTEST and self.dut.TCG_locked)):
         if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase and self.dut.systemAreaPrepared \
            and not self.dut.f3Active:  # Only try if mct is Active
            try:
               # Use test 231 to save the results file to the dut
               objMsg.printMsg("Saving Results to drive.", objMsg.CMessLvl.DEBUG)
               from SIM_FSO import objSimArea
               self.oFileSysObj.saveResultsFileToDrive(forceNew = (not self.dut.appendHDResultsFile),filePath = '', fileSize = 0, fileType = objSimArea['SPT_RESULTS_FILE'], exec231 = 1)
            except:
               objMsg.printMsg("Save Results to drive failed!", objMsg.CMessLvl.IMPORTANT)
            ReportErrorCode(self.dut.errCode)

      objMsg.printMsg("Begin parametric data dump.\n", objMsg.CMessLvl.IMPORTANT)
      self.writeParametrcDataToResultsFile()

      # objMsg.printMsg("Checking Load Avg before run Dex")
      # self.checkCM_LoadAvg()

      self.runDex()
      #RequestService('SendParametrics', (1,)) # send parametrics to FIS

      xmlFileSize = XmlResultsFile.size()
      ScrCmds.statMsg('XmlResultsFile Size: %s' % xmlFileSize)
      self.dut.driveattr['XMLRPC_BYTES'] = str(xmlFileSize)

      if self.dut.productionFileLimits == None:
         self.dut.productionFileLimits = ScrCmds.getSystemMaximumFileSizes()
      maxResultsFileSize, DefaultMaxEventSize, parametricFileMargin = self.dut.productionFileLimits
      if xmlFileSize > DefaultMaxEventSize:
         ScrCmds.statMsg(80 * "*")
         ScrCmds.statMsg(20 * "*" + "WARNING: FIS XML File size exceeds factory limit of %d" % DefaultMaxEventSize)
         ScrCmds.statMsg(80 * "*")

      indexSize = self.dut.dblParser.objDbLogIndex.indexFile.size()
      ScrCmds.statMsg("DbLog Index File Size: %d" % indexSize)
      self.dut.driveattr['DBLINDEX_BYTES'] = indexSize

      resultFileSize = ResultsFile.size()
      ScrCmds.statMsg('ResultsFile Size: %s' % resultFileSize)
      self.dut.driveattr['RSLT_FILE_BYTES'] = resultFileSize


   def writeParametrcDataToResultsFile(self):
      ##### Write XML data to results file
      try:
         if not testSwitch.virtualRun:
            # run STPGPD to generate T-tables for FC4 and SAS initiator cells
            import XmlResults
            mrf = XmlResults.XmlResults()
            mrf.addInstance('parametric_dblog', self.dut.dblData)
            if testSwitch.XML_SUM_IN_RESULTS_FILE == 1:
               objMsg.printMsg(str(mrf))
            if testSwitch.FtpPCFiles == 1 and not ConfigVars[CN].get('PRODUCTION_MODE',0):
               #Initialize file info

               sendFileName = "%s_%s.xml" % (HDASerialNumber, self.dut.nextOper)
               zipFileName = "%s_%s.zip" % (HDASerialNumber, self.dut.nextOper)
               #create xml file
               resFile = GenericResultsFile(sendFileName)
               resFile.open('w')
               resFile.write(str(mrf))
               resFile.close()

               #Create zip file
               try:
                  import zipfile
                  import zlib
                  zipSupported = 1
                  myzipFile = GenericResultsFile(zipFileName)
                  myzipFile.open('w')
                  zipObj = zipfile.ZipFile(myzipFile, 'w', zipfile.ZIP_DEFLATED)
                  zipObj.write(resFile.name, sendFileName)
                  zipObj.close()
                  #zipObj.testzip()
                  myzipFile.close()
               except ImportError:  #if CM doesn't support zip tools
                  zipSupported = 0

               #Save the xml zip file to the xml folder on the Platform server
               try:
                  RequestService('SetResultDir', 'XML')
                  try:
                     if zipSupported == 1:
                        RequestService("SendGenericFile", ((zipFileName,), "Platform"))
                     else:
                        RequestService("SendGenericFile", ((sendFileName,), "Platform"))
                  except:
                     objMsg.printMsg("XML 2ndary upload failed: \n%s" % traceback.format_exc())
                  #Clean up after ourselves by deleting files and reseting results directory
                  resFile.delete()
                  if zipSupported == 1:
                     myzipFile.delete()
               finally:
                  RequestService('SetResultDir', self.dut.nextOper)
            del mrf
      except:
         objMsg.printMsg("Failed to output dblog to results file", objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg("Traceback: %s" % traceback.format_exc())

   #------------------------------------------------------------------------------------------------------#
   def runDex(self):
      import ParamDbLogXmlOptimizer
      import parseresults, resultshandlers
      import time

      objMsg.printMsg("Running Dex %s" % time.ctime())
      if testSwitch.virtualRun:
         open(os.path.join(ScrCmds.getSystemResultsPath(),"%s.rp1" % FSO.CFSO().getFofFileName(1)),'w').write("")

      paramLoc = ScrCmds.getSystemParamsPath()

      #Set the dex output file to the Gemini XmlResultsFile
      resultshandlers.XmlResultsFile = XmlResultsFile
      parseresults.ResultsParser.createHandlers(paramResultsOnly=1,errorCodeFile=os.path.join(paramLoc,"codes.h"),\
                                                procErrorCodeFile=os.path.join(paramLoc,"proc_codes.h"),\
                                                messagesFile=os.path.join(paramLoc,"messages.h"))
      if testSwitch.virtualRun:
         stat, msg = 0,''
      else:
         stat,msg = parseresults.ResultsParser.processResultsFile(os.path.join(ScrCmds.getSystemResultsPath(),"%s.rp1" % FSO.CFSO().getFofFileName(1)))
      #Delete the handler which will close the file and write the end tag (</parametric_dblog>)
      del parseresults.ResultsParser.resultsHandlers

      try:
         objMsg.printMsg("Optimizing Dex output. %s" % time.ctime())
         if testSwitch.virtualRun:
            #clear out previous data
            XmlResultsFile.open('w')
            XmlResultsFile.write('')

         # objMsg.printMsg("Checking Load Avg before run Optimizing Dex")
         # self.checkCM_LoadAvg()
         # Get all of the SF3-generated data indicies to optimize the results file
         tableDict = ParamDbLogXmlOptimizer.accumulateDbLogIndicies(XmlResultsFile)

         # Get the process tables
         processTables = self.processOverrideDexTables()

         # Prioritize tables
         oDexOpti = ParamDbLogXmlOptimizer.dexOpti(processTables, tableDict, XmlResultsFile)
         oDexOpti.prioritizeTables()

         if testSwitch.BF_0133084_231166_DYNAMIC_ATTR_PARAM_REDUCTION:
            # Increase the size of the parametricFileMargin by the cumulative attribute size
            from math import log, ceil

            #PER_ATTR = 46 Each row has a fixed length component for xml encoding len('<row num=""><name></name><value></value></row>')
            # rownum needs a log base 10 to account for the increasing text size of the row num = "x" x variable
            oDexOpti.parametricFileMargin = 1000 #base amount for xml payload- current calculated value (7/2010) is 651 but leave room for expansion

            oDexOpti.parametricFileMargin = sum([46 + ceil(log(i+1,10)) + len(item[0]) + len(str(item[1])) for i, item in enumerate(DriveAttributes.items())])
            # parametricFileMargin +PER_ATTR*3 + numerical size *3 + XMLRPC_BYTES (12) + DBLINDEX_BYTES(14) + RSLT_FILE_BYTES(15)
            # parametricFileMargin += (46*3) + (8*3)+ 12 + 14 + 15
            oDexOpti.parametricFileMargin += 203

            objMsg.printMsg("New parametricFileMargin calculated from drive attributes is %d." % oDexOpti.parametricFileMargin)



         # Build the dbLog xml file
         objMsg.printMsg("Writing optimized Dex data to results file. %s" % time.ctime())
         oDexOpti.writeFinalDblogFile('xmlSwap.xml')

      except:
         stat, msg = 1, traceback.format_exc()

      if stat:
         objMsg.printMsg("***** DEX Error:  %s; %s " % (stat,msg))
      else:
         objMsg.printMsg("***** DEX was successful *****")




   #------------------------------------------------------------------------------------------------------#
   def processOverrideDexTables(self):
      from DbLogAlias import OracleTableOverrides, reverseTableHeaders, processTableOverrides

      locOverrides = processTableOverrides
##    Temporary disable the below 1st loop... need to re-evaluate this commented out block upon re-implementation
##       Review TPE-0003531 for reason to disable below
##      #Extend OracleTableOverrides with process dblog tables not in tabledictionary
##      for table in DbLogTableDefinitions.OracleTables.keys():
##         if not table in reverseTableHeaders and not table in locOverrides:
##            locOverrides.append(table)
##
##      #Add to be deleted tables to the override list
##      for table in self.dut.noLoad:
##         if not table in locOverrides:
##            locOverrides.append(table)

      # Use the built-in set type to enforce unique list items
      locOverrides = set(locOverrides)
      locOverrides = list(locOverrides)

      return locOverrides

   #------------------------------------------------------------------------------------------------------#
   def execute(self):

      if testSwitch.FE_0131335_220554_NEW_AUD_LODT_FLOW:
         if self.dut.ExtraOper:
            ScrCmds.statMsg("Jump over initializeComponents - Should run LODT/AUD flow")
            return
      else:
         if self.dut.LODT:
            ScrCmds.statMsg("Jump over initializeComponents - Should run LODT flow")
            return

      # objMsg.printMsg("Checking Load Avg before starting StateMachine")
      # self.checkCM_LoadAvg()
      # Setup dblog parsing required
      self.dut.setMyParser()

      # Register long running callback services
      self.dut.overlayHandler =  FSO.Overlay_Handler(self.dut)


      self.dut.ctmxOp = CTMX('OPER')   # Create CTMX Operation entry

      # trigger state machine

      import StateMachine
      try:
         StateMachine.CStateMachine(self.dut)
      finally:
         try:
            self.startRef = self.createStartStateData()
         except:
            pass
         try:
            objMsg.printDblogBin(self.dut.dblData.Tables('P_GOTF_TABLE_SUMMARY'))
            if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase and \
               not (testSwitch.BF_0138112_231166_P_RESET_SOM_STATE_IN_ENDTEST and self.dut.TCG_locked):
               logdata = self.dut.dblData.Tables('P_GOTF_TABLE_SUMMARY').tableDataObj()

               tableAdded = []
               from base_GOTF import CDblFile
               objDblFile = CDblFile()
               for record in logdata:
                  if record['DBLOG_TABLE'] not in tableAdded:
                     tableAdded.append(record['DBLOG_TABLE'])
                     objDblFile.writeDblToFile(record['DBLOG_TABLE'])
               objDblFile.saveDbltoDisc()
            #prototype for reading back  DBLOG data
            #import DbLog
            #mdbl = DbLog.DbLog(self.dut)
            #objDblFile.readGOTFdblFile(mdbl)
            #objMsg.printMsg("mdbl %s" % str(mdbl))
         except:
            #ignore missing data
            pass


   #----------------------------------------------------------------------------
   def autoRegUpdate(self, failureData = 'PASS', traceback = ''):
      #try:
      #Update Automated Regression if enabled...
      if testSwitch.autoRegression == 1:
         aRegRes = Utility.resObj(self.dut.serialnum, ConfigVars[CN].get("chglist",'unk'), self.dut.nextOper, str(failureData), str(traceback))
         ScrCmds.statMsg(aRegRes.fname())
         resFile = GenericResultsFile(aRegRes.fname())
         resFile.open('w')
         resFile.write(str(aRegRes))
         resFile.close()
         RequestService("SendGenericFile", ((aRegRes.fname(),), "AutoRegResults"))
         resFile.delete()

         sendFileName = HDASerialNumber + '_' +  str(ConfigVars[CN]['chglist']) + '.txt'

         resFile = GenericResultsFile(sendFileName)

         resFile.open('w')
         txtResults = open('/var/merlin/txtresults/%2.2d-%s-%s.txt' % (int(CellIndex),TrayIndex,PortIndex)).read()
         resFile.write(txtResults)
         resFile.close()
         RequestService("SendGenericFile", ((sendFileName,), "PlatformCertResults"))
         resFile.delete()
      #except:
      #  pass

   #----------------------------------------------------------------------------
   def xLateInvalidXMLChars(self,value):
      invalidChars = (
      ("==>", ""),
      (">=","IS GREATER THAN OR EQUAL TO"),
      ("<=","IS LESS THAN OR EQUAL TO"),
      ('>', "IS GREATER THAN"),
      ("<", "IS LESS THAN"),
      )

      for repString in invalidChars:
         value = value.replace(repString[0],repString[1])

      return value

   #----------------------------------------------------------------------------
   def create_P_EVENT_SUMMARY_TABLE(self,errCode=0,failV5='',failV12='',failTemp='',failData = ''):
      import parseresults
      j = re.compile('[,\n]') # commas and newline characters
      fail_data = j.sub(" ", str(failData)) # replace commas and newline characters in failData

      runTime = '%.2f' % ((time.time() - self.dut.birthtime)/3600.0)
      fail_data = self.xLateInvalidXMLChars(fail_data)

      maxFailDataLen = 253

      self.dut.dblData.Tables('P_EVENT_SUMMARY').addRecord(
                     {
                     'OCCURRENCE': 1,
                     'SEQ': '99',
                     'TEST_SEQ_EVENT': 1,
                     'RUN_TIME':runTime,
                     'SLOT':CellNumber,
                     'COMPLETION_CODE':errCode,
                     'FAILING_SEQ':self.dut.failTestInfo['seq'],
                     'FAILING_TEST':self.dut.failTestInfo['test'],
                     'FAILING_SEQ_VER':'',
                     'FAILING_PORTID':'',
                     'FAILING_EVENT':self.dut.curTestInfo['testPriorFail'],
                     #Occurrence of failing test in the current sequence. May appear off by one, however, temperature
                     #ramp is registered as test 0.
                     'FAILING_SQ_EVT': self.dut.failTestInfo['occur'],
                     'FAILING_TST_EVT':'',
                     'FAILING_TS_EVT':self.dut.failTestInfo['tstSeqEvt'],
                     'FAILING_5V':failV5,
                     'FAILING_12V':failV12,
                     'FAILING_TEMP':failTemp,
                     'SUB_BUILD_GROUP':self.dut.sbr,
                     'EQUIP_ID':HOST_ID,
                     'CM_VERSION':CMCodeVersion,
                     'HOST_VER':HostVersion,
                     'CONFIG_NAME':CN,
                     'CONFIG_VER':CV,
                     'DEX_VER':parseresults.VERSION,
                     'PWR_LOSS_CNT':'',
                     'PARAM_DICTIONARY_VER':tableRevision,
                     'FAIL_STATE':self.dut.failTestInfo['state'],
                     'FAIL_DATA':fail_data[:maxFailDataLen],  #limit failData to 4000 characters -2 for quotes
                     'FAIL_PARAMETER_NAME': self.dut.failTestInfo['param'],
                     })
      ScrCmds.statMsg(self.dut.dblData.Tables('P_EVENT_SUMMARY'))

   #------------------------------------------------------------------------------------------------------#
   def validateEC(self,EC,EM):
      """
      raise exception,and return bad errCode in errMsg if EC not 5 chars
      """
      try:
         ECstring=str(EC)
         if len(ECstring)==5:
            errCode,errMsg=EC,EM
         else:
            raise

      except:
         errCode,errMsg = 14521,'<invalid_errCode> %s  </invalid_errCode>' % EC
      return errCode,errMsg
      #------------------------------------------------------------------------------------------------------#
   def errHandler(self, errType='test',failureData=()):
      # init to default system generic failcode
      flags = {}
      flags.update(self.holdDriveEval())
      ReportRestartFlags(flags)

      RequestService("SendParametrics", (1,))  # Send parametric data for all failures

      self.dut.errCode  = GenericErrorCode
      self.dut.errMsg   = None
      self.dut.failTest = 0
      self.dut.failTemp = 0
      self.dut.failV12  = 0
      self.dut.failV5   = 0
      self.dut.testTime = 0.0

      try:
         self.genExcept = str(getattr(self.dut, 'genExcept', self.genExcept))#str(traceback.format_stack(f = None,limit=5))
         ScrCmds.statMsg('General Exception Dump: %s' % self.genExcept)
         if errType == 'raise':
            ScrCmds.statMsg('<<< RAISE EXCEPTION OCCURED >>>')
            TraceMessage('failureData %s' % `failureData`)
            self.dut.errCode  = failureData[0][2]#.errCode
            self.dut.errMsg   = failureData[0][0]#failureData.errMsg
            self.dut.failTemp = failureData[1]    #  this data is present in failureData for 'test' errType,  'script' errType does not have these results
            self.dut.failV12  = failureData[2][0]  #  this data is present in failureData for 'test' errType,  'script' errType does not have these results
            self.dut.failV5   = failureData[2][1]
            self.dut.testTime = time.time() - self.dut.birthtime
            self.dut.failTest = self.dut.objSeq.curRegTest
         elif errType == 'test':
            # ((test_name ,test_number, test_status, test_time), current_temp, (voltages))
            ScrCmds.statMsg('<<< TEST FAILURE OCCURED >>>')
            try:
               self.dut.errCode  = self.dut.failureData[0][2]     #  this data is present in failureData for 'test' errType,  'script' errType does not have these results
               self.dut.errMsg   = self.dut.failureData[0][0]     #  this data is present in failureData for 'test' errType,  'script' errType does not have these results
               self.dut.testTime = self.dut.failureData[0][3]     #  this data is present in failureData for 'test' errType,  'script' errType does not have these results
               self.dut.failTest = self.dut.failureData[0][1] #  this data is present in failureData for 'test' errType,  'script' errType does not have these results
               self.dut.failTemp = self.dut.failureData[1]    #  this data is present in failureData for 'test' errType,  'script' errType does not have these results
               self.dut.failV12  = self.dut.failureData[2][0]  #  this data is present in failureData for 'test' errType,  'script' errType does not have these results
               self.dut.failV5   = self.dut.failureData[2][1]   #  this data is present in failureData for 'test' errType,  'script' errType does not have these results

               if self.dut.failTest == 0:
                  try:
                     self.dut.failTest = int(re.search('.*__st\((?P<st>[0-9]+).*', self.dut.failureData[0][0]).groupdict()['st'])
                  except:
                     pass

               if self.dut.errCode == 10124:
                  self.TranslateEC()

               if self.dut.errCode == 38912:
                  # 38912 is a check sum mismatch during f/w download - scsi sense code 0x05269800
                  self.dut.errCode = 14615

               if self.dut.errCode >= 39000 and self.dut.errCode <= 40000:
                  #TPM Error codes are sense codes and not FOF registered- raise a generic EC and load up the actual sense to msg and fail data
                  self.dut.errMsg = ScrCmds.getFailureMessage(self.dut.errCode,  self.dut.errMsg)
                  self.dut.errCode = 14844

               if self.dut.errCode in [11049, 11044, 11087]:
                  if not testSwitch.virtualRun: #Trap table could be defined all the time but is invalid
                     tableNames = [i[0] for i in self.dut.dblData.Tables()]
                     if 'P000_ASSERT_TRAP' in tableNames:
                        self.dut.errCode = 14667   #Assign failcode if timeout caused by trap code
                        self.dut.errMsg =  self.dut.dblData.Tables('P000_ASSERT_TRAP').tableDataObj()

            except:
               objMsg.printMsg("Error in TEST FAILURE HANDLING! failuredata: %s:\n%s" % (self.dut.failureData, traceback.format_exc()))
               self.errHandler('script')
               return
         elif errType == 'script':
            ScrCmds.statMsg('<<< SCRIPT FAILURE OCCURED >>>')

            if testSwitch.virtualRun == 0:
               traceBackList = self.genExcept.split('\n')
               stackLen = len(traceBackList)
               stackIndex = 0
               for stackInfo in traceBackList: #traceback.extract_stack():
                  if stackInfo.find('runState') != -1:
                     self.dut.failTestInfo['stackInfo'] = ''
                     for index in range(stackIndex+1,stackLen-2):
                        stackInfo = traceBackList[index].split('%s/script/'%CN)[-1]
                        if self.dut.failTestInfo['stackInfo'] == '':
                           self.dut.failTestInfo['stackInfo'] = '%s' % stackInfo
                        else:
                           self.dut.failTestInfo['stackInfo'] = '%s;  %s' % (self.dut.failTestInfo['stackInfo'],stackInfo)
                     break
                  stackIndex += 1

            self.dut.errCode,self.dut.errMsg = ScrCmds.translateErrCode(self.dut.errCode)
            self.dut.testTime = time.time() - self.dut.birthtime
            self.dut.failTest = self.dut.objSeq.curRegTest
            (mV3,mA3),(mV5,mA5),(mV12,mA12)  = GetDriveVoltsAndAmps()
            try:

               self.dut.failTemp = '%.1f' % (int(ReportTemperature())/10.0)
               self.dut.failV12  = float('%.3f' % (mV12/1000.0))
               self.dut.failV5   = float('%.3f' % (mV5/1000.0))
            except:
               self.dut.failTemp = '0.0'
               self.dut.failV12 = '0.0'
               self.dut.failV5 = '0.0'
               ScrCmds.statMsg("Exception in converting fail(VT)")

         if self.dut.errCode in [11087,11049,11231,11168,14029] and testSwitch.virtualRun != 1 and \
            (testSwitch.FE_0139892_231166_P_SEARCH_FLED_FAIL_PROC and self.dut.flashLedSearch_endTest):
            try:
               ScrCmds.statMsg("Searching for FLASH LED's")
               flashAddr = DriveVars.get('RW_FLASH_LED_ADDR','')
               flashCode = DriveVars.get('RW_FLASH_LED_CODE','')

               if flashAddr == '' and flashCode == '':
                  import sptCmds

                  flashAddr, flashCode = sptCmds.flashLEDSearch(120)
                  ScrCmds.statMsg("Completed Searching for FLASH LED's")

               if not flashAddr == '' and not flashCode == '':
                  self.dut.errCode = 11231
                  self.dut.errMsg = {"FLASH_LED_CODE":flashCode,"FLASH_LED_ADDR":flashAddr}
            except:
               ScrCmds.statMsg("FLASH LED Search failed: Exception")

      finally:
         self.dut.errCode,self.dut.errMsg = self.validateEC(self.dut.errCode,self.dut.errMsg)
         ScriptComment('self.dut.errCode %s' % self.dut.errCode)

         #CHOOI-05Sep15 Modify Start
         if (self.dut.errCode == 11044) and ("P166_PREAMP_INFO" in self.dut.errMsg):
            self.dut.errCode = 10554
            ScriptComment('self.dut.errCode %s' % self.dut.errCode)
         #CHOOI-05Sep15 Modify End

         self.dut.driveattr['TEST_TIME']  = '%.2f' % (time.time() - self.dut.birthtime)
         if testSwitch.FE_0155956_336764_P_SEND_OPER_TES_TIME_AS_ATTRIBUTE:
            self.dut.driveattr['%s_TEST_TIME'%self.dut.nextOper]  = '%.2f' % (time.time() - self.dut.birthtime)
         self.dut.driveattr['FAIL_STATE'] = getattr(self.dut, 'failureState', 'NA') # send state_name where test failed
         if getattr(self.dut, 'failureState', 'NA') == 'NA':
            self.dut.failureState = 'NA'
         self.dut.driveattr['FAIL_CODE']  = getattr(self.dut, 'errCode', 11044) # update failcode attribute to FIS
         self.dut.driveattr['FAIL_TEST']  = getattr(self.dut, 'failTest', 0)
         self.dut.driveattr['MFG_EVAL'] = '?'       # CHOOI-28Oct11 reset MFG_EVAL
         
#CHOOI-15Jul17 OffSpec
         if DriveAttributes['PART_NUM'][7:10] in ['ELB','LEB','PLB']:
            DriveAttributes['PART_NUM'] = DriveAttributes['PART_NUM'][0:7] + 'GLB'
         elif DriveAttributes['PART_NUM'][7:10] in ['E99','9E9','P99']:
            DriveAttributes['PART_NUM'] = DriveAttributes['PART_NUM'][0:7] + '899'

         ### FAIL_PSN  start ###
         self.dut.driveattr['FAIL_PSN'] = "-1"
         try:
            failHeads = 0
            try:
               data_Table = self.dut.dblData.Tables("P_FAILING_HEAD").tableDataObj()
            except:
               data_Table = []
            if len(data_Table):
               failHeadList = [int(rowData['FAILED_HEAD']) for rowData in data_Table if str(rowData['FAIL_CODE']) == str(self.dut.driveattr['FAIL_CODE'])]
               failHeadList = list(set(failHeadList))
               failHeads = sum(2**i for i in failHeadList if i >= 0)

            if failHeads == 0:
               RegCom=re.compile(r'@\s+Head\s+:\s+\[(?P<HD>.*)]')
               match = RegCom.search(self.dut.errMsg)
               if match:
                  failHeads = sum(2**int(i) for i in (match.groupdict()['HD']).split(',') if i not in ['',None])

            if failHeads:
               self.dut.driveattr['FAIL_PSN'] = str(failHeads)
         except:
            objMsg.printMsg("Error in FAIL_PSN Setting! \n%s" %  traceback.format_exc())
         objMsg.printMsg("FAIL_PSN = %s" %  self.dut.driveattr['FAIL_PSN'])
         ### FAIL_PSN  end ###
         
         self.dut.updateFISAttr() # update all FIS attributes in one go

         ScrCmds.statMsg('Script/Test Failure: %s' % str(self.dut.errCode))

         from Failcode import getFailCodeAndDesc
         self.dut.errCode, stdMsg = getFailCodeAndDesc(self.dut.errCode)

         if self.dut.errMsg == None or (self.dut.errMsg == "stats = st") or (self.dut.errMsg == "st"):
            self.dut.errMsg = stdMsg # if errmsg was not specified by scripter, then use the standard msg from codes.h

         ScrCmds.statMsg('-'*64)
         ScrCmds.statMsg('| %-10s%-50s |' % ('ErrCode', 'ErrMsg'))
         ScrCmds.statMsg('| %-10s%-50s |' % (self.dut.errCode, stdMsg))
         ScrCmds.statMsg('-'*64)

         ScrCmds.statMsg('='*64)
         ScrCmds.statMsg('Error Dump:')
         ScrCmds.statMsg(self.dut.errMsg)
         ScrCmds.statMsg('='*64)
         self.dut.failData = str(self.dut.errMsg)
         ReportStatus('%s --- %s --- %s' % (self.dut.nextOper, self.dut.failureState, stdMsg)) # display fail state on GUI cell status window

         # If the EC indicates a bad drive then
         if objRimType.IsPSTRRiser():
            restartFlags = {}
            ScrCmds.statMsg('PSTR - no need to check for forceReplug')
         elif not testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
            if self.dut.replugECMatrix.has_key(self.dut.errCode) and \
               (self.dut.failureState in self.dut.replugECMatrix[self.dut.errCode] or self.dut.failTestInfo['test'] in self.dut.replugECMatrix[self.dut.errCode] or len(self.dut.replugECMatrix[self.dut.errCode]) == 0) and \
               ConfigVars[CN].get('ReplugEnabled',0) and not ConfigVars[CN].get('BenchTop',0) == 1:
               restartFlags = self.forceReplug(self.dut.errCode)
               ScrCmds.statMsg('self.dut.errCode: %s' % self.dut.errCode)
               ScrCmds.statMsg('self.dut.replugECMatrix.has_key(self.dut.errCode): %s' % self.dut.replugECMatrix.has_key(self.dut.errCode))
               ScrCmds.statMsg('self.dut.curTestInfo[test]: %s' % self.dut.curTestInfo['test'])
               ScrCmds.statMsg('self.dut.failTestInfo: %s' % self.dut.failTestInfo)
               if self.dut.AFHCleanUp and testSwitch.FE_0160713_409401_P_ADD_AFH_CLEAN_UP_AT_AUTO_REPLUG_FOR_DRIVE_FAIL_AFTER_AFH4:
                  if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
                     from base_AFH import CCleanUpBadPattern
                  else:
                     from base_SerialTest import CCleanUpBadPattern
                  oCleanUpBadPattern = CCleanUpBadPattern(self.dut,{})
                  oCleanUpBadPattern.run()
            else:
               restartFlags = {}
         else: #testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT = 1
            if getattr(self.dut,'irReplug',False) == True and getattr(self.dut,'irIgnore',False) == False:
               restartFlags = self.forceReplug(self.dut.errCode,recoveryMode = 1) # recoveryMode = 1, Represent iRecovery Re-plug
            elif getattr(self.dut,'irReOper',False) == True and getattr(self.dut,'irIgnore',False) == False:
               restartFlags = self.forceReplug(self.dut.errCode,recoveryMode = 2) # recoveryMode = 2, Represent iRecovery Re-Oper (Restart at any Oper)
            elif self.dut.replugECMatrix.has_key(self.dut.errCode) and (self.dut.failTestInfo['test'] in self.dut.replugECMatrix[self.dut.errCode] or len(self.dut.replugECMatrix[self.dut.errCode]) == 0) and \
               ConfigVars[CN].get('ReplugEnabled',0) and not ConfigVars[CN].get('BenchTop',0) == 1:
               restartFlags = self.forceReplug(self.dut.errCode)
               ScrCmds.statMsg('self.dut.errCode: %s' % self.dut.errCode)
               ScrCmds.statMsg('self.dut.replugECMatrix.has_key(self.dut.errCode): %s' % self.dut.replugECMatrix.has_key(self.dut.errCode))
               ScrCmds.statMsg('self.dut.curTestInfo[test]: %s' % self.dut.curTestInfo['test'])
               ScrCmds.statMsg('self.dut.failTestInfo: %s' % self.dut.failTestInfo)
               if self.dut.AFHCleanUp and testSwitch.FE_0160713_409401_P_ADD_AFH_CLEAN_UP_AT_AUTO_REPLUG_FOR_DRIVE_FAIL_AFTER_AFH4:
                  if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
                     from base_AFH import CCleanUpBadPattern
                  else:
                     from base_SerialTest import CCleanUpBadPattern
                  oCleanUpBadPattern = CCleanUpBadPattern(self.dut,{})
                  oCleanUpBadPattern.run()
            else:
               restartFlags = {}
         if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
            self.handleIRecoveryAttr()
         if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT and (base_RecoveryTest.IR_ReportFirstEC and self.IR_REOPER_VALUE == 'RUNNING' and getattr(self.dut,'irReOper',False) != True):
            if base_RecoveryTest.IR_HybridReportEC:
               if  self.IR_BF_OPER_VALUE != self.dut.nextOper:
                  ReportErrorCode(base_RecoveryTest.IR_ErrorCode)
                  DriveAttributes['IR_ACTIVE']     = 'Y'
                  DriveAttributes['IR_FAIL_EC']    = DriveAttributes.get('IR_FAIL_EC'  ,'NONE')
                  DriveAttributes['IR_FAIL_OPER']  = DriveAttributes.get('IR_FAIL_OPER','NONE')
                  DriveAttributes['IR_CMS_CONFIG'] = self.dut.driveattr['CMS_CONFIG']
            else:
               ReportEC = self.IR_BF_EC_VALUE
               ReportErrorCode(ReportEC)
               DriveAttributes['IR_ACTIVE']     = 'Y'
               DriveAttributes['IR_FAIL_EC']    = DriveAttributes.get('IR_FAIL_EC'  ,'NONE')
               DriveAttributes['IR_FAIL_OPER']  = DriveAttributes.get('IR_FAIL_OPER','NONE')
               DriveAttributes['IR_CMS_CONFIG'] = self.dut.driveattr['CMS_CONFIG']

         else:
            ReportErrorCode(self.dut.errCode)

         #Global Fail Safe feature allows Test Process to continue to next operation.
         if self.dut.restartOnFail == 1:
            restartFlags.update({'restartOnFail':1})

         return restartFlags

   #------------------------------------------------------------------------------------------------------#
   if not testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
      def forceReplug(self,errCode):
         #Replug drive in new cell
         restartFlags = {}
         if int(DriveAttributes.get('DR_REPLUG_CNT',0)) < ConfigVars[CN].get('DRIVE_REPLUG_LIMIT',3)-1 and \
            not ConfigVars[CN].get('BenchTop',0) == 1:

            try:
               opername = TP.replugECMatrix['SEND_NEW_OPER'] + self.dut.nextOper
            except:
               opername = 'MTS'

            RequestService('SetResultDir', (opername,))
            RequestService('SetOperation', (opername,)) # Set station name
            restartFlags={"doRestart":1,"sendRun":4,"forceCellChange":1,"restartOnFail":1}
            DriveAttributes['DR_REPLUG_CNT'] =  int(DriveAttributes.get('DR_REPLUG_CNT',0)) + 1
            ScrCmds.statMsg('Replug drive to new cell, retry attempt: %s of %s. OperName=%s' % (DriveAttributes['DR_REPLUG_CNT'],ConfigVars[CN].get('DRIVE_REPLUG_LIMIT',3), opername))

            if testSwitch.FE_0149328_345963_P_SET_OPER_FOR_MTS:
               DriveAttributes['SET_OPER'] = self.dut.nextOper
         else:
            DriveAttributes['DR_REPLUG_CNT'] = 0

         ReportErrorCode(int(errCode))
         return restartFlags
   else: #testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT = 1
      def forceReplug(self,errCode,recoveryMode = 0):
         #Replug drive in new cell
         restartFlags = {}
         sendMTS = False
         if recoveryMode == 0: # recoveryMode = 0, Normal Re-plug
            if int(DriveAttributes.get('DR_REPLUG_CNT',0)) < ConfigVars[CN].get('DRIVE_REPLUG_LIMIT',3)-1 and \
               not ConfigVars[CN].get('BenchTop',0) == 1:
               DriveAttributes['DR_REPLUG_CNT'] =  int(DriveAttributes.get('DR_REPLUG_CNT',0)) + 1
               ScrCmds.statMsg('Replug drive to new cell, retry attempt: %s of %s' % (DriveAttributes['DR_REPLUG_CNT'],ConfigVars[CN].get('DRIVE_REPLUG_LIMIT',3)) )
               if testSwitch.FE_0149328_345963_P_SET_OPER_FOR_MTS:
                  DriveAttributes['SET_OPER'] = self.dut.nextOper
               sendMTS = True
            else:
               DriveAttributes['DR_REPLUG_CNT'] = 0
         elif recoveryMode == 1:  # recoveryMode = 1, Represent iRecovery Re-plug
            irRePlugLimit = base_RecoveryTest.MAX_DRIVE_REPLUG.get(self.dut.nextOper,base_RecoveryTest.MAX_DRIVE_REPLUG.get('DEFAULT',0))

            attrName = 'IR_REPLUG_CNT'
            if not testSwitch.virtualRun:
               name, returnedData = RequestService('GetAttributes', (attrName))
               objMsg.printMsg("iRecovery : GetAttributes %s result = name : %s, data : %s" %(attrName,`name`,`returnedData`))
            else:
               name,returnedData = ('GetAttributes',{attrName: 'UNKNOWN'})

            IR_REPLUG_CNT_VALUE = returnedData.get(attrName ,0)
            try:
               IR_REPLUG_CNT_VALUE = int(IR_REPLUG_CNT_VALUE)
            except:
               IR_REPLUG_CNT_VALUE = 0

            if IR_REPLUG_CNT_VALUE < irRePlugLimit:
               replugCounter = IR_REPLUG_CNT_VALUE + 1
               DriveAttributes['IR_REPLUG_CNT']  =  replugCounter
               ScrCmds.statMsg('iRecovery : Replug drive to new cell, retry attempt: %s of %s' % (replugCounter,irRePlugLimit))
               DriveAttributes['IR_REPLUG_STAT'] = 'WAIT'
               DriveAttributes['SET_OPER']       = self.dut.nextOper
               sendMTS = True
            else:
               ScrCmds.statMsg('iRecovery : Replug drive to new cell, retry limit exceed')
         elif recoveryMode == 2: # recoveryMode = 2, Represent iRecovery Re-Oper (Restart at any Oper)
            sendMTS = True
            # Just send MTS for iRecovery Re-Oper.
            # Determining destination Oper will determined by setNextOper() function.

         if sendMTS:
            RequestService('SetResultDir', ('MTS',))
            RequestService('SetOperation', ('MTS',)) # Set station name
            restartFlags={"doRestart":1,"sendRun":4,"forceCellChange":1,"restartOnFail":1}
            self.dut.forceReplug = 'Y'
         ReportErrorCode(int(errCode))
         return restartFlags

   #------------------------------------------------------------------------------------------------------#
   def holdDriveEval(self):
      """
      @return: Returns "holdDrive" dictionary w/ 1 if either of below is true.
         - ConfigVars['holdDrive'] = 1
         - DriveAttributes['MTS_HOLD_DRIVE'] = 'Y'
      """
      flags = {}
      attrHold = DriveAttributes.get('MTS_HOLD_DRIVE','N')
      configHold = ConfigVars[CN].get('holdDrive',0)
      if (attrHold == 'Y' or configHold == 1) and self.dut.chamberType not in ['B2D','SP240']:
         flags["holdDrive"] = 1
      else:
         flags["holdDrive"] = 0


      return flags

   #------------------------------------------------------------------------------------------------------#
   def raiseException(self, errCode, errMsg=''):
      ScrCmds.statMsg("errorCode: %s" % errCode)
      ReportErrorCode(errCode)
      failureData = [errMsg, 999, errCode]

      ScrCmds.statMsg('%s' % errMsg)
      raise ScriptTestFailure, failureData

   #------------------------------------------------------------------------------------------------------#
   def reportRestart(self, doRestart,sendRun,forceCellChange=0):
      try:                                   #  NEW way to send runs and restart
         flags = {}
         flags["doRestart"]=doRestart
         flags["sendRun"]=sendRun
         flags["forceCellChange"] = forceCellChange
         flags.update(self.holdDriveEval())
         ReportRestartFlags(flags)
         ScrCmds.statMsg("doRestart= %s   sendRun = %s  forceCellChange = %s "  % (doRestart,sendRun,forceCellChange))
      except:
         ScrCmds.statMsg("Restart Failed doRestart= %s   sendRun = %s  forceCellChange = %s" % (doRestart,sendRun,forceCellChange))
   #------------------------------------------------------------------------------------------------------#
   def replugForTempMove(self, failureData):
      #errorCode, nextRimType = failureData
      # Need to assign a new error code
      #errorCode = 10606

      ReportErrorCode(0)                        # Clear error code
      RequestService('SetResultDir',('MTS',))
      RequestService('SetOperation',('MTS',))    # Set station name to MTS
      RequestService('SendStartEvent', 1)

      if testSwitch.FE_0149328_345963_P_SET_OPER_FOR_MTS:
         DriveAttributes['SET_OPER'] = self.dut.nextOper

      #DriveAttributes['PROC_CTRL63'] = 'EC%s' % (errorCode, )
      #ReportErrorCode(errorCode)
      RequestService('SendRun',(1,))       # Send MTS PASS Event with result file

      ReportErrorCode(0)

      flags = {}
      flags["doRestart"]       = 1
      flags["sendRun"]         = 0
      flags["forceCellChange"] = 1
      ReportRestartFlags(flags)


   #------------------------------------------------------------------------------------------------------#

   #------------------------------------------------------------------------------------------------------#
   def PreOpCheck(self):
      """ reset attr at begining of PRE2 - knl 16Apr08 """

      #if self.dut.scanTime != 0 or self.dut.nextOper == 'PRE2' or ConfigVars[CN]['BenchTop']:
      if self.dut.scanTime != 0 or self.dut.nextOper == 'PRE2':
         DriveAttributes['LOOPER_COUNT'] = '0'
         ScrCmds.statMsg('LOOPER_COUNT set to 0 for fresh load drives/PRE2')

      if testSwitch.FNG2_Mode == 1:
         if self.dut.nextOper == 'CUT2':
            ScrCmds.statMsg('Start CUT2. Setting PROC_CTRL99=NONE')
            #self.dut.driveattr['PRO_CTRL99'] = 'NONE'
            DriveAttributes['PROC_CTRL99'] = 'NONE'

         if self.dut.nextOper == 'FNG2' and DriveAttributes['PROC_CTRL99'] != "TVMPASS" and DriveAttributes['PROC_CTRL99'] != "PASS":
            ScrCmds.raiseException(11187, "Start of FNG2 operation but PRO_CTRL99 != TVMPASS or PASS")

      if testSwitch.proqualCheck and (not self.dut.nextOper == "SCOPY"): # Initialise xxxx_TEST_DONE if Proqual check is turn On for current and all subsequent operations
         pq_attr_reset = {}
         for oper in self.dut.operList[self.dut.operList.index(self.dut.nextOper):]:
            self.dut.prevOperStatus['%s_TEST_DONE' %oper.upper()] = DriveAttributes.get('%s_TEST_DONE' %oper.upper(), 'NONE')
            pq_attr_reset['%s_TEST_DONE'%oper.upper()] = 'NONE'

         if self.dut.nextOper == 'PRE2' and 'CRT2_TEST_DONE' not in pq_attr_reset: # to ensure CRT2_TEST_DONE is reset to NONE when re-PRE2 even if someone hack the operList
            self.dut.prevOperStatus['CRT2_TEST_DONE'] = DriveAttributes.get('CRT2_TEST_DONE', 'NONE')
            pq_attr_reset['CRT2_TEST_DONE'] = 'NONE'

         ScrCmds.statMsg('Initialising %s attributes to NONE at start of %s' % (pq_attr_reset.keys(), self.dut.nextOper))
         DriveAttributes.update(pq_attr_reset)


   #------------------------------------------------------------------------------------------------------#
   def PRE2DriveAttrReset(self):
      if self.dut.nextOper == 'CRT2' and self.dut.scanTime != 0:
         attrname = 'COMMIT_DONE'
         self.dut.driveattr[attrname] = 'NONE'
         DriveAttributes[attrname] = 'NONE'
         ScrCmds.statMsg(attrname + ' set to NONE for CRT2 reflow')

      if self.dut.nextOper in ['PRE2','SCOPY']:
         dPRE2_attr_reset = {
               'BSNS_SEGMENT'    :'NONE',
               'CUST_SCORE'      :'NONE',
               'DRIVE_SCORE'     :'NONE',
               'CTU_SCORE'       :'NONE',
               'CTU_TEST_DONE'   :'NONE',
               'BLUENUNSCAN'     :'NONE',
               'CST_TEST_DONE'   :'NONE',
               'IDT_TEST_DONE'   :'NONE',
               'OBA_TEST_DONE'   :'NONE',
               'CODE_VER'        :'NONE',
               'FIRMWARE_VER'    :'NONE',
               'SERVO_CODE'      :'NONE',
               'JUMPER_SET'      :'NONE',
               'ODT_TEST_DONE'   :'NONE',
               'ODTV_TEST_DONE'  :'NONE',
               'ORIT_TEST_DONE'  :'NONE',
               'ORT_TEST_DONE'   :'NONE',
               'IDT_TEST_DONE'   :'NONE',
               'OBA_TEST_DONE'   :'NONE',
               'EOBA_TEST_DONE'  :'NONE',
               'CUST_TESTNAME'   :'NONE',
               'CUST_TESTNAME_2' :'NONE',
               'CUST_TESTNAME_3' :'NONE',
               'SUCUST_TESTNAME' :'NONE',
               'SUCUST_TESTNAME2':'NONE',
               'SUCUST_TESTNAME3':'NONE',
               'WTF_CTRL'        :'NONE',
               'CMT2_TEST_DONE'  :'NONE',
               'COMMIT_DONE'     :'NONE',
               'ZERO_G_SENSOR'   :'NONE',
               'ZERO_PTRN_RQMT'  :'NONE',
               'FIN_READY_TIME'  :'NONE',
               'CUST_TESTNAME'   :'NONE',
               'NON_DCM_SCREENS' :'NONE',
               'SECURITY_TYPE'   :'NONE',
               'FDE_TYPE'        :'NONE',
               'IEEE1667_INTF'   :'NONE',
               'DLP_SETTING'     :'NA',
               'SED_LC_STATE'    :'NA',
               'POWER_ON_TYPE'   :'NONE',
               'GOTF_BEST_SCORE' :'NONE',
               'GOTF_BIN_CTQ'    :'NONE',
               'GOTF_BIN_BEST'   :'NONE',
               'TODT_TEST_DONE'  :'NONE',
               'EQAT2_TEST_DONE' :'NONE',
               'TODT'            :'N',
               'ODT_TEST_LOOPS'  :'0',
               'TODT_LOOPS'      :'0',
               'FIRMWARE_VER '   :'?',
               'SCSI_CODE '      :'?',
               'C6_SCRN'         :'NONE',
               'C5_SCRN'         :'NONE',
               'PROC_CTRL10'     :'NONE',
               'PROC_CTRL19'     :'0',
               'RECONFIG'        :0,
               'PRE2_FINAL_TEMP' :'NONE',
               'PROC_CTRL25'     :'0',
               'PROC_CTRL30'     :'0',
               'PROC_CTRL9'      :'0',
               'PROC_CTRL6'      :'0',
               'MISMATCH '       :'NONE',
               'OPS_CAUSE'       :'NONE',
               'GIO_TEST_DONE'   :'NONE',
               'TDCI_COMM_LIFE'  :0,
               'NOSHIP'          :'NONE',
               }
         if testSwitch.FE_0365343_518226_SPF_REZAP_BY_HEAD:
            dPRE2_attr_reset.update({
                  'SPF_CUR_HEAD' :0,
               })
         if testSwitch.FE_0359619_518226_REAFH2AFH3_BYHEAD_SCREEN:
            dPRE2_attr_reset.update({
                  'RE_AFH2_HEAD' :'0',
               })
         if int(DriveAttributes.get('DR_REPLUG_CNT',0)) == 0 :
            dPRE2_attr_reset.update({
                  'DNGRADE_ON_FLY'    :'NONE',
               })

         if testSwitch.FE_0158690_395340_P_UADATE_ATTR_PRE2_DATE_TIME:
            dPRE2_attr_reset['PRE2_DATE_TIME'] = time.strftime("%Y%m%d", time.localtime())

         if testSwitch.FE_0166720_407749_P_SENDING_ATTR_BPI_TPI_INFO_FOR_ADG_DISPOSE:
            dPRE2_attr_reset.update({
                  'BPI_CAP_MIN'  : 'NONE',
                  'BPI_CAP_AVG'  : 'NONE',
                  'TPI_CAP_MIN'  : 'NONE',
                  'TPI_CAP_AVG'  : 'NONE',
               })
         if testSwitch.AGC_SCRN_DESTROKE or testSwitch.AGC_SCRN_DESTROKE_FOR_SBS:
            dPRE2_attr_reset.update({
                  'DESTROKE_REQ' :'NONE',
               })
         if testSwitch.FE_0212759_409401_P_RESET_SCN_ATTR:
            dPRE2_attr_reset.update({
                  'SCN_TEST_DONE':'NONE',
               })
         if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
            dPRE2_attr_reset.update({
                  'FN_PN'        :'NONE',
                  'ORG_TIER'     :'NONE',
               })
         if testSwitch.PBIC_SUPPORT:
            dPRE2_attr_reset.update({
                  'PBIC_STATUS'  :'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                  'FIN2_PBIC_CTRL':'NONE',
               })
         if testSwitch.FE_0318342_402984_CHECK_HDA_FW:
            dPRE2_attr_reset.update({
                  'HDA_FW'       :'NONE',
               })
         if testSwitch.FE_305538_P_T297_WPE_SCREEN:
            dPRE2_attr_reset.update({
               'WPE_UIN'         : '',
            })
         if testSwitch.FE_0368834_505898_P_MARGINAL_SOVA_HEAD_INSTABILITY_SCRN:
            dPRE2_attr_reset.update({
               'HMSC_AVG'        : '',
            })

         ScrCmds.statMsg('Setting %s attributes to NONE at PRE2' % dPRE2_attr_reset.keys())
         self.dut.driveattr.update(dPRE2_attr_reset)
         DriveAttributes.update(dPRE2_attr_reset)
         self.dut.driveattr['CMT2_TEST_DONE'] = 'NONE'

      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         #Reset ZERO_PATRN_RQMT at beginning of CRT2 Oper in Tiered flow
         if self.dut.nextOper in ['CRT2']:
            csm_attr_reset = {
                  'ZERO_PTRN_RQMT'  :'NONE',
                  }
            DriveAttributes.update(csm_attr_reset)
            self.dut.driveattr.update(csm_attr_reset)

      #Reset selective CSM drive attributes for drive decon support
#CHOOI-20Jul17 OffSpec
#      if self.dut.nextOper in ['CMT2', 'FIN2', 'CUT2', 'TODT']:
      if self.dut.nextOper in ['CMT2', 'FIN2', 'TODT']:
         csm_attr_reset = {
               'ZERO_PTRN_RQMT'  :'NONE',
               'CUST_TESTNAME'   :'NONE',
               'CUST_TESTNAME_2'  :'NONE',
               'CUST_TESTNAME_3'  :'NONE',
               'SUCUST_TESTNAME'   :'NONE',
               'SUCUST_TESTNAME2'  :'NONE',
               'SUCUST_TESTNAME3'  :'NONE',
               'SECURITY_TYPE'   :'NONE',
               'FDE_TYPE'        :'NONE',
               'DLP_SETTING'     :'NA',
               'SED_LC_STATE'    :'NA',
               'NON_DCM_SCREENS' :'NONE',
               'TODT_TEST_DONE'  :'NONE',
               'EQAT2_TEST_DONE' :'NONE',
               'ODT2_TEST_DONE'  :'NONE',
               'CCV2_TEST_DONE'  :'NONE',
               'CST2_TEST_DONE'  :'NONE',
               'CST_TEST_DONE'   :'NONE',
               'C6_SCRN'         :'NONE',
               'C5_SCRN'         :'NONE',
               }
         if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
            csm_attr_reset.pop('CUST_TESTNAME')

            if not self.dut.resetCustConfigAttr:
               csm_attr_reset.pop('CUST_TESTNAME', 0)
               csm_attr_reset.pop('CUST_TESTNAME_2', 0)
               csm_attr_reset.pop('CUST_TESTNAME_3', 0)
               csm_attr_reset.pop('SUCUST_TESTNAME', 0)
               csm_attr_reset.pop('SUCUST_TESTNAME2', 0)
               csm_attr_reset.pop('SUCUST_TESTNAME3', 0)

         if self.dut.nextOper in ['FIN2']:
            ID_MODEL_reset ={
               'CUST_MODEL_NUM'  :'NONE',
               'DRV_MODEL_NUM'   :'NONE',
               }
            csm_attr_reset.update(ID_MODEL_reset)
         if (testSwitch.FE_0155867_395340_P_FIRST_ODT_SEQUENT_TEST_FOR_SAS or testSwitch.FE_0164370_395340_P_FIRST_ODT_SEQUENT_TEST_FOR_SATA) and self.dut.nextOper in ['CUT2']:
            csm_attr_reset['MQM_TEST_DONE'] = 'NONE'
            csm_attr_reset['MQM_RW'] = 'NONE'

         if testSwitch.FE_0118167_405392_RESET_RELIABILITY_ATTRIBUTE_TO_NONE:
            reli_attr_reset = {
               'ODT_TEST_DONE'   :'NONE',
               'OBA_TEST_DONE'   :'NONE',
               'IDT_TEST_DONE'   :'NONE',
               }
            csm_attr_reset.update(reli_attr_reset)

         if testSwitch.FE_0212759_409401_P_RESET_SCN_ATTR and self.dut.nextOper == 'FIN2':
            reli_attr_reset = {
                  'SCN_TEST_DONE'    :'NONE',
               }
            csm_attr_reset.update(reli_attr_reset)
         #reset the reconfig attr if not in a backend oper
         if self.dut.nextOper not in ['FIN2', 'TODT', 'IDT2', 'CST2']:
            csm_attr_reset['RECONFIG'] = 0

         if not self.dut.powerLossEvent:
            DriveAttributes.update(csm_attr_reset)
            self.dut.driveattr.update(csm_attr_reset)

      #Reset selective CSM drive attributes for drive decon support
      if self.dut.nextOper in ['TODT']:
         csm_attr_reset = {
               'TODT'  :'C',
               }

      #Reset selective CSM drive attributes for drive decon support
      if self.dut.nextOper in ['CCV2'] and testSwitch.FE_0173503_357260_CLEAR_CCV_ATTRIUBUTES_IN_CCV2:
         csm_attr_reset = {
               'ZERO_PTRN_RQMT'  :'NONE',
               'CCV2_TEST_DONE'  :'NONE',
               }
         DriveAttributes.update(csm_attr_reset)
         self.dut.driveattr.update(csm_attr_reset)

      csm_attr_reset_all_oper = {
         #'DR_REPLUG_FLAG'  :  'NONE',
         #'CCVTEST'         :  'NONE',
         'TDCI_COMM_NUM'   :       0,
      }
      DriveAttributes.update(csm_attr_reset_all_oper)
      self.dut.driveattr.update(csm_attr_reset_all_oper)

   #------------------------------------------------------------------------------------------------------#
   def DriveAttrTag(self,mode='start'):
      import PIF

      attr_reset = {}

      if mode=='start':
         dict = getattr(PIF,'startTag',{})

         # Moved from PRE2DriveAttrReset
         if self.dut.nextOper == 'PRE2':
            from StateMachine import CLongAttr
            attr_reset.update(CLongAttr().EncodeAttr(""))

      else:
         dict = getattr(PIF,'endTag',{})

      if not dict.has_key(self.dut.nextOper):
         if mode=='start':
            if testSwitch.FE_0147919_426568_P_SKIP_PRE2DRIVEATTRRESET_IF_PLR:
               if not self.dut.stateTransitionEvent == 'procStatePowerLoss':
                  self.PRE2DriveAttrReset()  # Backward compatibility request
            else:
               self.PRE2DriveAttrReset()  # Backward compatibility request

      else:
         for attr in dict[self.dut.nextOper]:
            if len(dict[self.dut.nextOper][attr])== 2:
               #Conditional
               for attr2 in dict[self.dut.nextOper][attr][1]:
                  if DriveAttributes.get(attr2,'?')in dict[self.dut.nextOper][attr][1][attr2]:
                     attr_reset[attr]=dict[self.dut.nextOper][attr][0]
            else:
               #No condition
               attr_reset[attr]=dict[self.dut.nextOper][attr][0]

      ScrCmds.statMsg('Tagging %s attributes at %s %s' % (attr_reset.keys(),self.dut.nextOper,mode))
      self.dut.driveattr.update(attr_reset)
      DriveAttributes.update(attr_reset)

   #------------------------------------------------------------------------------------------------------#
   def TranslateEC(self):
      ScrCmds.statMsg("TranslateEC %s" %self.dut.errCode)
      try:
         data = DriveVars["SENSE_DATA"] # get drivevar data from test 504 param 1 set to 0x8000 init code bqd14,bqf14 or later
         ScrCmds.statMsg("Data " + data )
         if data:
            data = data.upper()    # set everything to uppercase
            data = data.split()    # split the sense data string at every space
            sense_key = '0' + data[2][1:]   # Sense Key is lower 4 bits of byte 2
            ScrCmds.statMsg(ParamFilePath)
            fName = os.path.join(ParamFilePath,CN,'flt_cnvt.txt')     #ConfigVars["current"]["FileListName"]
            ScrCmds.statMsg(fName)
            if os.path.isfile(fName) == 1:
               fd = open(fName, 'r')  # open flt_cnvt.txt
               ScriptComment("File " + fName + " is opened")
               buf = fd.readlines()   # read flt_cnvt.txt
               fd.close()
               if buf:
                  for line in buf:   # go thru every line one by one in flt_cnvt looking for a match
                     try:             # the 'for line in buf' cycles thru the whole try except for each line in flt_cnvt until match is found
                        line = line.upper()  # change all to uppercase
                        line = line.split()  # split flt_cnvt lines up at every space in the line -- now  each chunk of the line is called line 1,line 2 etc.
                        # 10124 10001 01 03 ?? 10   /* Svo Flt-01/03XX10 Write Fault Servo */ (10124 is line 0 ,10001 is line 1, 01 is line 2 etc.)
                        if str(self.dut.errCode) == str(line[0]) and (str(line[2])=='??' or str(line[2])==str(sense_key)) and (str(line[3])=='??' or str(line[3])==str(data[12])) and (str(line[4])=='??' or str(line[4])==str(data[13])) and (str(line[5])=='??' or str(line[5])==str(data[14])):
                           self.dut.errCode = line[1]
                           ScrCmds.statMsg("new error code is %s" %self.dut.errCode)
                           break                # atoi is something to turn it into an interger
                     except:
                        ScrCmds.statMsg("Check format of flt.cnvt.txt")
               else:
                  ScrCmds.statMsg("Path " + fName + " not found")
      except:
         ScrCmds.statMsg("TranslateEC failed")
   #------------------------------------------------------------------------------------------------------#
   def packageControl(self):
      if testSwitch.FE_0126095_405392_FORCE_CHECK_PCBA_CYCLE_COUNT:
         #Factroy has a PCBA_CYCLE_COUNT contorl to protect quality,all PCBA which already recycled more than 10 loops need be RTV or scrapped.
         if int(DriveAttributes.get('PCBA_CYCLE_COUNT', 0)) > ConfigVars[CN].get('PCBACycleCount', 10):
            ScrCmds.raiseException(13393, "PCBA_CYCLE_COUNT > %d"%ConfigVars[CN].get('PCBACycleCount', 10))

      if not ConfigVars[CN].get('PRODUCTION_MODE',0):
         return

      if not testSwitch.FE_0126095_405392_FORCE_CHECK_PCBA_CYCLE_COUNT:
         #Factroy has a PCBA_CYCLE_COUNT contorl to protect quality,all PCBA which already recycled more than 10 loops need be RTV or scrapped.
         if int(DriveAttributes.get('PCBA_CYCLE_COUNT', 0)) > ConfigVars[CN].get('PCBACycleCount', 10):
            ScrCmds.raiseException(13393, "PCBA_CYCLE_COUNT > %d"%ConfigVars[CN].get('PCBACycleCount', 10))

      i, package_control, vo = 0, {}, self.dut.nextOper

      #if vo == 'SDAT2':
         #return    # not all drives need run with SDAT2. So skip check in SDAT2

      for oper in self.dut.operList:     # package_control = {'PRE2':0, 'FNC2':0, 'CRT2':0, 'CMT2':0, 'FIN2':0, 'CUT2':0}
         #if oper == 'SDAT2':
            #continue
         package_control[oper], i = i, i + 1

      rerun_oper = getattr(TP,'rerun_oper',['CRT2', 'CMT2', 'FIN2'])
      pgName = ConfigVars[CN].get('PackageControl','UNFY')

      # Allow drives rerun from some speceified operation for ADG
      #if (vo in rerun_oper) and (DriveAttributes.get('ALLONE','UNFY0') == (pgName + '0') or DriveAttributes.get('ALLONE','') == (pgName + 'P')):
      DriveAttributes['ALLONE'] = '%s%d'%(pgName, package_control[vo])

      if vo == 'PRE2':
         DriveAttributes['ALLONE'] = '%s%d'%(pgName, package_control[vo])

      # Only allow drive that is with last operation pass to run into current operation
      if DriveAttributes.get('ALLONE','') != '%s%d'%(pgName, package_control[vo]):
         ScrCmds.raiseException(13392, "%s: The drive cannot run into this operation"%vo)
   #------------------------------------------------------------------------------------------------------#
   def getCSTRestartFlag(self):
      """
      @return: Returns updated "restartFlags" if drive is selected.
      """
      flags = {}

      ScrCmds.statMsg('*'*64)
      cstName = ConfigVars[CN].get('GIO_EvalName','GIO_CST')
      ScrCmds.statMsg('GIO_EvalName = %s' % cstName)
      flags = {'doRestart':1,'sendRun':0,'configEval':cstName}
      ScrCmds.statMsg('*'*64)

      return flags
   #------------------------------------------------------------------------------------------------------#
   def rwkYieldMonitor(self):
      """
      This function will send attribute 'DRV_COMP_TRK' and 'DRV_RWK_COMP' for rework yield monitor
      It inherits from ST10
      Example ?C Prime
                DRV_COMP_TRK = PPPPP  DRV_RWK_COMP = PPPPPP
      Example ?C Rework (RTV Recycle HSA_ RTV DISC_Prime MBA_Recycle VCM_Semi HDA for DISC change)
                DRV_COMP_TRK = RRPRR  DRV_RWK_COMP = SRPLPD
      Current attributes are:
            DRV_RWK_HSA
            DRV_RWK_MEDIA
            DRV_RWK_MBA
            DRV_RWK_LVCM
            DRV_RWK_UVCM
            DRV_RWK_HDA
            DRV_RWK_COMP
            DRV_COMP_TRK
      """
      init_dict = {}

      #DRV_RWK_HSA
      hsa_rwk = int(DriveAttributes.get('HSA_RWK_CNT', 0))
      hsa_rcl = int(DriveAttributes.get('HSA_RECYCLE', 0))
      if hsa_rwk == 0 and hsa_rcl == 1:
         init_dict['DRV_RWK_HSA'] = 'P'
      elif hsa_rwk == 0 and hsa_rcl > 1:
         init_dict['DRV_RWK_HSA'] = 'L'
      elif DriveAttributes.get('HSA_FW',"00") != "00" and hsa_rwk > 0 and hsa_rcl > 1:
         init_dict['DRV_RWK_HSA'] = 'R'
      elif DriveAttributes.get('HSA_FW',"00") == "00" and hsa_rwk > 0 and hsa_rcl > 1:
         init_dict['DRV_RWK_HSA'] = 'S'
      else:
         init_dict['DRV_RWK_HSA'] = 'P'

      #DRV_RWK_MEDIA
      defVal = '0'*10
      try:
         if testSwitch.BF_0131992_409401_DISC_RECYCLE_FROM_NUMHEAD:
            mediaRecycleCriticalVals = [int(DriveAttributes.get('MEDIA_RECYCLE', defVal)[i]) for i in range(1, self.dut.imaxHead+1, 2)]
         else:
            mediaRecycleCriticalVals = [int(DriveAttributes.get('MEDIA_RECYCLE', defVal)[i]) for i in [1,3,5,7,9]]
      except:
         #Invalid attrs
         objMsg.printMsg("Invalid attribute value detected for 'MEDIA_RECYCLE' for Component Recycle Tracking")
         if testSwitch.BF_0131992_409401_DISC_RECYCLE_FROM_NUMHEAD:
            mediaRecycleCriticalVals = [int(defVal[i]) for i in range(1, self.dut.imaxHead+1, 2)]
         else:
            mediaRecycleCriticalVals = [int(defVal[i]) for i in [1,3,5,7,9]]
      mediaRecycleCritical_CTZ = [i==0 for i in mediaRecycleCriticalVals] == [True,]*len(mediaRecycleCriticalVals)
      mediaRecycleCritical_GTZ = [i>0 for i in mediaRecycleCriticalVals] == [True,]*len(mediaRecycleCriticalVals)

      #Create disc recycle logic comparators for max 5 discs
      discRecycle_CT1 = True
      discRecycle_GT1 = True
      if testSwitch.BF_0131992_409401_DISC_RECYCLE_FROM_NUMHEAD:
         numDisc = int(round(float(self.dut.imaxHead)/2))
      else:
         numDisc = 4
      for discNum in range(0,numDisc):
         discRecVal = DriveAttributes.get('DISC_%d_RECYCLE' % (discNum +1), False)
         if testSwitch.BF_0131166_399481_CONVERT_DISC_RECYCLE_ATTR_TO_INT:
            discRecVal = int(discRecVal)
         if discRecVal:
            #BF_0117742_231166_FIX_GTZ_REFERENCE_IN_REVA_REC_COMP
            discRecycle_GT1 = discRecycle_GT1 & (discRecVal > 1)
            discRecycle_CT1 = discRecycle_CT1 & (discRecVal == 1)


      if mediaRecycleCritical_CTZ and discRecycle_CT1:
         init_dict['DRV_RWK_MEDIA'] = 'P'
      elif mediaRecycleCritical_CTZ and discRecycle_GT1:
         init_dict['DRV_RWK_MEDIA'] = 'L'
      elif mediaRecycleCritical_GTZ and discRecycle_CT1:
         init_dict['DRV_RWK_MEDIA'] = 'R'
      elif mediaRecycleCritical_GTZ and discRecycle_GT1:
         init_dict['DRV_RWK_MEDIA'] = 'S'

      #DRV_RWK_MBA

      if int(DriveAttributes.get('MTR_CYCLE_CNT',0)) == 1 and DriveAttributes.get('MOTOR_DATE_CODE','0000') != '0000':
         init_dict['DRV_RWK_MBA'] = 'P'
      elif int(DriveAttributes.get('MTR_CYCLE_CNT',0)) > 1 or DriveAttributes.get('MOTOR_DATE_CODE',None) == '0000':
         init_dict['DRV_RWK_MBA'] = 'L'

      #DRV_RWK_LVCM and DRV_RWK_UVCM
      defVal = [None,]*20
      try:
         lvcmMag_Z = DriveAttributes.get('MAGNET_LOT_BOT', defVal)[11:19] == "00000000"
         lvcmMag_Nines = DriveAttributes.get('MAGNET_LOT_BOT', defVal)[11:19] == "99999999"
      except:
         #Invalid attrs
         objMsg.printMsg("Invalid attribute value detected for 'MAGNET_LOT_BOT' for Component Recycle Tracking")
         lvcmMag_Z = False
         lvcmMag_Nines = False

      if lvcmMag_Nines:
         init_dict['DRV_RWK_LVCM'] = 'M'
      elif lvcmMag_Z:
         init_dict['DRV_RWK_LVCM'] = 'L'
      else:
         init_dict['DRV_RWK_LVCM'] = 'P'

      try:
         uvcmMag_Z = DriveAttributes.get('MAGNET_LOT_TOP', defVal)[11:19] == "00000000"
         uvcmMag_Nines = DriveAttributes.get('MAGNET_LOT_TOP', defVal)[11:19] == "99999999"
      except:
         #Invalid attrs
         objMsg.printMsg("Invalid attribute value detected for 'MAGNET_LOT_TOP' for Component Recycle Tracking")
         uvcmMag_Z = False
         uvcmMag_Nines = False

      if uvcmMag_Nines:
         init_dict['DRV_RWK_UVCM'] = 'M'
      elif uvcmMag_Z:
         init_dict['DRV_RWK_UVCM'] = 'L'
      else:
         init_dict['DRV_RWK_UVCM'] = 'P'

      #DRV_RWK_HDA
      crx_cnt = int(DriveAttributes.get("CRX_CNT", 0))
      proc_ctrl8 = DriveAttributes.get("PROC_CTRL8")

      if crx_cnt > 1 and proc_ctrl8 in ['H', 'D', 'V', 'C']:
         init_dict['DRV_RWK_HDA'] = proc_ctrl8
      elif proc_ctrl8 not in ['H', 'D', 'V', 'C']:
         init_dict['DRV_RWK_HDA'] = 'O'


      #DRV_COMP_TRK
      if init_dict.get('DRV_RWK_LVCM', 'P') == 'P' and init_dict.get('DRV_RWK_UVCM', 'P') == 'P':
         vcmJoint = 'P'
      else:
         vcmJoint = 'R'

      hda = [init_dict.get(val, 'P') for val in ['DRV_RWK_HSA', 'DRV_RWK_MEDIA', 'DRV_RWK_MBA', vcmJoint]]
      if hda == (['P',] * len(hda)):
         hda.append('P')
      else:
         hda.append('R')

      init_dict['DRV_COMP_TRK'] = ''.join(hda)
      if testSwitch.BF_0122926_231166_FIX_DRV_COMP_TRK_NON_PRIME:
         # DRV_COMP_TRK only has P=Prime and R= Rework. L == Rework/recycle so replace
         init_dict['DRV_COMP_TRK'] = init_dict['DRV_COMP_TRK'].replace('L', 'R')

      #DRV_RWK_COMP
      init_dict['DRV_RWK_COMP'] = ''.join([init_dict.get(val, 'P') for val in ['DRV_RWK_HSA', 'DRV_RWK_MEDIA', 'DRV_RWK_MBA', 'DRV_RWK_LVCM', 'DRV_RWK_UVCM', 'DRV_RWK_HDA']])


      ScrCmds.statMsg('Rwk Yield Monitor: %s'%init_dict)
      DriveAttributes.update(init_dict)

   #------------------------------------------------------------------------------------------------------#
   def IsMCConnected(self):
      """
      Function checks siteconfig setting if drive is running on Gemini system.
      Returns boolean value. Gemini = 1, Benchtop = 0.
      """
      if testSwitch.virtualRun:
         return 1
      mc_connected = RequestService('GetSiteconfigSetting','MC_connected')
      mc_connected = mc_connected[1].get('MC_connected',1)
      return mc_connected

   #------------------------------------------------------------------------------------------------------#
   def recoverOverlay(self):
      """
      Recovers wiped drive overlay prior to GIO and MQM.
      """
      ScrCmds.statMsg("Checking drive overlay.")

      if self.dut.driveattr.get('FDE_DRIVE') is 'FDE':
         ScrCmds.statMsg("Overlay code recovery not needed for TCG drives.")
         return

      import serialScreen


      objPwrCtrl.powerOn()

      oSerial = serialScreen.sptDiagCmds()
      flashLED, ovlWiped = oSerial.IsOvlWiped()
      if flashLED:
         objPwrCtrl.powerCycle()

      try:
         ec = 14690
         if not testSwitch.virtualRun:
            f3Code = oSerial.getPackageVersion()                                          # Get drive F3 code version
         else:
            f3Code = DriveAttributes.get('CODE_VER')
         ScrCmds.statMsg("F3 code detected : %s" % (f3Code ))

         if f3Code != DriveAttributes.get('CODE_VER'):
            ScrCmds.statMsg("F3 CODE MISMATCH! Drive code version = %s, FIS CODE_VER = %s" %(f3Code, DriveAttributes.get('CODE_VER')))
            ScrCmds.raiseException(ec, "F3 Code Mismatch Error")
         elif not ovlWiped:                                                               # Do not download code if OVL is not wiped and F3 code is correct
            ScrCmds.statMsg("Correct F3 code present on drive.")
            return

         # Verify F3 code file exists
         f3File = os.path.join(UserDownloadsPath, CN, str(f3Code + ".zip").upper())
         if not os.path.isfile(f3File):
            f3Alias = getattr(TP,'f3Alias', {})
            newCode = f3Code.split('.')[3][4:7]                                           # Do code lookup during code mismatch for HP
            if f3Alias.get(newCode) is None:
               ScrCmds.raiseException(ec, "Missing F3 code")

            newCode = f3Code.split('.')[3].replace(newCode, f3Alias.get(newCode))
            f3Code = f3Code.split('.')[:3]
            f3Code.append(newCode)
            f3Code = ".".join(f3Code)

         ScrCmds.statMsg("Recovering F3 code %s" %f3Code)
         fwConfig = Codes.fwConfig.get(self.dut.partNum)
         fwConfig.update({'TGTP': (f3Code + ".zip")})

         self.buildFileList()                                                             # Package list check

         if not objRimType.isIoRiser() or testSwitch.NoIO:
            theCell.enableESlip(sendESLIPCmd = True)
            objPwrCtrl.changeBaud(PROCESS_HDA_BAUD)
            self.dut.sptActive.setMode(self.dut.sptActive.availModes.mctBase,determineCodeType = True)
            if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
               from Serial_Download import CDnldCode
            else:
               from base_SerialTest import CDnldCode
            oDnldCode = CDnldCode(self.dut, {'CODES' : ['TGT','OVL']})
         else:
            from base_IntfTest import CDnlduCode
            objPwrCtrl.powerCycle(5000,12000,10,30)
            dnldCls = CDnlduCode(dut =self.dut, params = {'CODES': ['TGT','OVL']})        # Download TGTP with diags
            dnldCls.run()
            del dnldCls

      except:
         ScrCmds.statMsg("<<< Error downloading code! >>> %s" %traceback.format_exc())
         RequestService('SetOperation',("*%s" % self.dut.nextOper,))                      # Send unyielded oper failure
         ScrCmds.raiseException(ec)

   def handleIDTSlot(self, restartFlags):
      """ Ensure drive is in IO cell when running GIO operation """
      try:
         nextOper = self.dut.operList[self.dut.operList.index(self.dut.nextOper)+1]
      except:
         nextOper = None

      if (nextOper is 'IDT2') and (self.dut.driveattr['RISER_TYPE'] in objRimType.SerialOnlyRiserList()) and (ConfigVars[CN].get('GIO_Selection') not in [None, 'OFF']):
         from Cell import theCell
         allow_move, idle_slot = theCell.askHostForTwoMove('57')[1]      # Check for IO slot availability
         if allow_move:
            objMsg.printMsg("Moving drive to IO cell for %s operation." %nextOper)
            restartFlags.update({"doRestart":1,"sendRun":4,"forceCellChange":1})
         else:
            objMsg.printMsg("No IO cell available for %s." %nextOper)

      return restartFlags
