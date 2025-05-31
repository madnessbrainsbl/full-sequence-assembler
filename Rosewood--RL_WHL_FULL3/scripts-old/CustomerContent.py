#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Customer Content
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CustomerContent.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CustomerContent.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from Test_Switches import testSwitch
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds, sptCmds
from Utility import CUtility
from ICmdFactory import ICmd
from Cell import theCell
from Rim import theRim
DEBUG = 0

###########################################################################################################
###########################################################################################################
class CKwaiPrep(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if self.dut.nextOper == "FNG2":
         objMsg.printMsg("Skipping SeaCos personalization for drive in FNG2")
         return

      from KwaiPrep import CKwaiPrepTest
      oKwaiPrep = CKwaiPrepTest(self.dut)
      from serialScreen import sptDiagCmds
      oSerial = sptDiagCmds()

      if not testSwitch.virtualRun:
         oKwaiPrep.KwaiPrep()
         objPwrCtrl.powerCycle(5000,12000,10,30)
         accumulator = oSerial.PChar(CTRL_Z)
         result = oSerial.error
         data = oSerial.promptRead(10,0,accumulator = accumulator)
         objMsg.printMsg("Data returned from CtrlZ command - data = %s" % data)
      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
         locFunc = oSerial.isSeaCosLocked
      else:
         locFunc = oSerial.isLocked

      if result == OK and locFunc(data) == False: # If serial port not locked after KwaiPrep
         objMsg.printMsg('Serial Port is NOT locked after KwaiPrep! Cannot find ?> or (1Ah)-Serial Port Disabled' )
         result = -1
      if result != OK:
         ScrCmds.raiseException(12383, "Kwai Prep Failed")

      if result == OK:                                               # Post KwaiPrep support for FDE drives
         self.dut.objData.update({'KwaiPrepDone': 1})
         DriveAttributes['TD_SID'] = self.dut.driveattr['TD_SID']    # Force update so that unlock will have new attr
         DriveAttributes['SECURITY_TYPE'] = self.CMSSecurityType(DriveAttributes.get("CMS_FAMILY",""))

         if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
            if not len(DriveAttributes['TD_SID']) == 25:
               objMsg.printMsg("Error, length of DriveAttributes['TD_SID'] is %s (not 25) for SeaCos SED drive" % (len(DriveAttributes['TD_SID'])))
               ScrCmds.raiseException(12383, "Error, length of DriveAttributes['TD_SID'] is not 25 for SeaCos SED drive")
            else:
               objMsg.printMsg("Ok, length of DriveAttributes['TD_SID'] is %s for SeaCos SED drive" % (len(DriveAttributes['TD_SID'])))

         DriveAttributes['FDE_TYPE'] = "FDE BASE"
         objPwrCtrl.powerCycle()

      return result

   #-------------------------------------------------------------------------------------------------------
   def CMSSecurityType(self, family):
      Security_Type = {
            'Echostar ST10'     : ['SUPERHAWKK', 'GALAXY'],
            'Sagem ST10'        : ['SUPERHAWKK'],
            'DVR Platform'      : ['ECHOSTAR', 'SAGEM'],
            'FDE.2'             : ['CODY'],
            'FDE.3'             : ['CROCKETT', 'CASEY'],
            'FDE.3.5'           : ['WYATT', 'HOLLIDAY'],
            'FDE.4'             : ['PHARAOH'],
            'Nearline Security' : ['MUSKIE']
            }
      for security_type, product_name in Security_Type.iteritems():
         if family in product_name:
            return security_type

      return "NONE"


###########################################################################################################
###########################################################################################################
class CTCGPrep(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      objMsg.printMsg("CTCGPrep: Starts")

      if not ConfigVars[CN].get('PRODUCTION_MODE',0) and testSwitch.FE_0246029_385431_SED_DEBUG_MODE:
         objMsg.printMsg("FE_0246029_385431_SED_DEBUG_MODE on, skip")
         return                        
      elif testSwitch.virtualRun:
         objMsg.printMsg("VE personalization not supported.")
         return

      from TCG import CTCGPrepTest
      oTCG = CTCGPrepTest(self.dut)

      try:
         oTCG.run()
         
         if self.dut.nextOper == "FNG2":
            if not self.dut.LifeStateName == "USE":
               objMsg.printMsg("Error, LifeStateName :%s for TCG FDE drive in FNG2" %self.dut.LifeStateName)
               ScrCmds.raiseException(14862, "Error, Drive is not in USE state for TCG FDE drive in FNG2")
            else:
               objMsg.printMsg("Ok, LifeStateName :%s. Skipping TCG personalization for drive in FNG2" %self.dut.LifeStateName)
               return

         oTCG.TCGPrep()

      finally:
         if testSwitch.BF_0180787_231166_P_REMOVE_FDE_CALLBACKS_FOR_CHECKFDE:
            oTCG.RemoveCallback()
         
      self.dut.objData.update({'TCGPrepDone': 1})
      self.dut.driveattr['FDE_DRIVE'] = 'FDE'

      from Rim import objRimType                 

      TCGBandTest = getattr(TP,"prm_TCG",{}).get('TCGBandTest', 1)
      if TCGBandTest and objRimType.isIoRiser() and not testSwitch.IS_SDnD:
         objMsg.printMsg("Running band test for TCG SED drive")
         objPwrCtrl.powerCycle(5000,12000,10,30)
         oTCG.TCGBandsTest()
         oTCG.ResetSOMState()

      if not len(DriveAttributes['TD_SID']) == 32:
         objMsg.printMsg("Error, length of DriveAttributes['TD_SID'] is %s (not 32) for TCG SED drive" % (len(DriveAttributes['TD_SID'])))
         ScrCmds.raiseException(14862, "Error, length of DriveAttributes['TD_SID'] is not 32 for TCG SED drive")
      else:
         objMsg.printMsg("Ok, length of DriveAttributes['TD_SID'] is %s for TCG SED drive" % (len(DriveAttributes['TD_SID'])))

      objPwrCtrl.powerCycle(5000,12000,10,30)

      if testSwitch.WA_0159243_231166_P_FORCE_SET_FDE_TYPE_ATTR:
        self.dut.driveattr['SECURITY_TYPE'] = str(self.dut.driveConfigAttrs.get('SECURITY_TYPE', ('=',getattr(TP,"prm_TCG",{}).get('SECURITY_TYPE', 'TCG Enterprise SSC 1.0 FDE') ))[1]).rstrip()
        self.dut.driveattr['FDE_TYPE'] = str(self.dut.driveConfigAttrs.get('FDE_TYPE', ('=',getattr(TP,"prm_TCG",{}).get('FDE_TYPE', 'FDE Base') ))[1]).rstrip()
      else:
         from IntfClass import CIdentifyDevice
         oIdentifyDevice = CIdentifyDevice(force = True)
         ret = CIdentifyDevice().ID 
         if testSwitch.IS_SDnD:
            self.dut.driveattr['FDE_TYPE'] = 'NONE'   
         else:
            if (int(ret['IDReserved159']) & 0x0001) == 0x0001 :   
               self.dut.driveattr['FDE_TYPE'] = 'FDE BASE FIPS 140-2'
            else:
               self.dut.driveattr['FDE_TYPE'] = getattr(TP,"prm_TCG",{}).get('FDE_TYPE', 'NONE')
         
         self.dut.driveattr['SECURITY_TYPE'] = oTCG.SECURITY_TYPE
         self.dut.driveattr['IEEE1667_INTF'] = oTCG.IEEE_1667
         objMsg.printMsg("FDE_TYPE = %s, SECURITY_TYPE = %s IEEE1667_INTF = %s" % (self.dut.driveattr['FDE_TYPE'],self.dut.driveattr['SECURITY_TYPE'], self.dut.driveattr['IEEE1667_INTF']))
         
      self.dut.driveattr['SED_LC_STATE'] = self.dut.LifeStateName
      objMsg.printMsg("CTCGPrep: End")

###########################################################################################################
###########################################################################################################
class CFinalPrep(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if not self.dut.driveattr['FDE_DRIVE'] == 'FDE':
         objMsg.printMsg("Not SED/SdnD drive, skip this")
         return     

      if not ConfigVars[CN].get('PRODUCTION_MODE',0) and testSwitch.FE_0246029_385431_SED_DEBUG_MODE:
         objMsg.printMsg("FE_0246029_385431_SED_DEBUG_MODE on, skip")
         return                        

      objMsg.printMsg("CFinalPrep: Starts")

      from TCG import CTCGPrepTest
      oTCG = CTCGPrepTest(self.dut)
      try:      
         oTCG.run()

         if self.dut.nextOper == "FNG2":
            if not self.dut.LifeStateName == "USE":
               objMsg.printMsg("Error, LifeStateName :%s for TCG FDE drive in FNG2" %self.dut.LifeStateName)
               ScrCmds.raiseException(14862, "Error, Drive is not in USE state for TCG FDE drive in FNG2")
            else:
               objMsg.printMsg("Ok, LifeStateName :%s. Skipping TCG personalization for drive in FNG2" %self.dut.LifeStateName)
               return

         oTCG.finalSEDPrep()
      finally:
         if testSwitch.BF_0180787_231166_P_REMOVE_FDE_CALLBACKS_FOR_CHECKFDE:
            oTCG.RemoveCallback()

      self.dut.driveattr['SED_LC_STATE'] = self.dut.LifeStateName
      objPwrCtrl.powerCycle(5000,12000,10,30)
      objMsg.printMsg("CFinalPrep: End")

###########################################################################################################
###########################################################################################################
class CChangeDef(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      objMsg.printMsg("CChangeDef: Starts")

      #Make sure dict defined in PIF, and partNum defined with prms
      import PIF
      if hasattr(PIF,'changeDefPrmDict') and PIF.changeDefPrmDict.has_key(self.dut.partNum):
         tmpPrms = PIF.changeDefPrmDict[self.dut.partNum]
      else:
         ScrCmds.raiseException(11044, "No Change Definition Prms specified")

      ICmd.scsiChangeDef(tmpPrms)

      objMsg.printMsg("CChangeDef: End")

###########################################################################################################
###########################################################################################################
class CPI_Format(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      #SCSI Spec shows Format Unit command (op code 4) Byte 1 bits 6,7 as "FMTPINFO"
      #But, T511 breaks this out into separate bits -
      #   T511 param "RTO_REQ" = lsb of SCSI cmd field FMTPINFO
      #   T511 param "FMTPINFO = msb of SCSI cmd field FMTPINFO

      objMsg.printMsg("CPI_Format: Starts")

      if self.dut.powerLossEvent and testSwitch.FE_0159866_395340_P_POWER_TRIP_AT_Z_PI_FORMAT_ON_CUT2:
         objMsg.printMsg("ClearFormatCorrupt")
         ICmd.ClearFormatCorrupt_1()
         self.dut.powerLossEvent = 0
         objPwrCtrl.powerCycle()

      #Make sure dict defined in PIF, and partNum defined with sector size
      import PIF
      if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:
         prottypeval = str(self.dut.driveConfigAttrs['FMT_PROT_TYPE'][1])
         CDB_FMTPINFO = 0  #Regular non-PI format command
         if prottypeval == 'TYPE_2':
            CDB_FMTPINFO = 3  #Type 2 PI format command
      elif hasattr(PIF,'ProtInfoTypeDict') and PIF.ProtInfoTypeDict.has_key(self.dut.partNum):
         CDB_FMTPINFO = PIF.ProtInfoTypeDict[self.dut.partNum].get('FMTPINFO',0)
      else:
         CDB_FMTPINFO = 0  #Regular non-PI format command

      if testSwitch.FE_0163769_357260_P_SKIP_FORMAT_OR_PACK_WRITE_IF_ZERO_PAT_DONE:
         if CDB_FMTPINFO == 0 and str(self.dut.driveattr.get('ZERO_PTRN_RQMT', DriveAttributes.get('ZERO_PTRN_RQMT',None))).rstrip() == '20':
            objMsg.printMsg('CPI_Format: ZERO_PTRN_RQMT == 20 detected - skipping non-PI format')
            return

      rtoREQ,fmtPInfo = CDB_FMTPINFO&0x1,(CDB_FMTPINFO>>1)&0x1

      if not ConfigVars[CN].get('GenerateCCV', 0):
         ICmd.runInitiatorFormat(fmtPInfo, rtoREQ)
         if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:
            if verifyRequired:
               from CCABuildCfg import updateCUST_TESTNAME
               updateCUST_TESTNAME('FV1')  # CCA - Format with Verify

      self.dut.driveattr['ZERO_PTRN_RQMT'] = "20"
      objMsg.printMsg("CPI_Format: End")


###########################################################################################################
###########################################################################################################
class CPois(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg('CPois()')

      enabled = self.params.get('ENABLED',1)

      if enabled:
         cmd = 0x06  #SET FEATURES ENABLE POIS
         cfVar = 'ON'
         attr = "PWR_ON_IN_STDBY"
      else:
         cmd = 0x86  #SET FEATURES DISABLE POIS
         cfVar = 'OFF'
         attr  = "POIS_DISABLED"


      from IntfClass import CIdentifyDevice
      theCell.enableESlip(sendESLIPCmd = True)
      oIdentifyDevice = CIdentifyDevice()

      if testSwitch.NoIO: #In SPIO mode, f/w takes care of the POIS enable/disable 
         #Get drive's f/w POIS status
         POIS_Status = 0 # (1 = POIS enabled, 0 = POIS disabled)
         if oIdentifyDevice.Is_POIS_Supported() and oIdentifyDevice.Is_POIS(): 
            POIS_Status = 1

         #Check against the DCM requirement
         if POIS_Status != enabled:
            ScrCmds.raiseException(13454, "POIS setting failed!")
         else:
            objMsg.printMsg("POIS setting on drive is correct.")

         # set power on config vars to properly spin up drive in POIS
         ConfigVars[CN].update({'Power On Set Feature':cfVar})

      else:
         if not oIdentifyDevice.Is_POIS_Supported():
            objMsg.printMsg("POIS not supported")
            ScrCmds.raiseException(13454, "POIS not supported in F3 code")

         data = ICmd.SetFeatures(cmd) # enable POIS
         
         if data['LLRET'] is NOT_OK:
            objMsg.printMsg("POIS completion: %s" % `data`)
            ScrCmds.raiseException(13454,"POIS SetFeatures(0x%2X) failed!" %cmd)
            
         # set power on config vars to properly spin up drive in POIS
         ConfigVars[CN].update({'Power On Set Feature':cfVar})

         # power cycle drive to verify spinup in POIS
         objPwrCtrl.powerCycle(5000,12000,10,30)

         oID = CIdentifyDevice(force = True)
         if not testSwitch.virtualRun:
            if enabled and oID.Is_POIS() != enabled:
               ScrCmds.raiseException(13454, "POIS enabled setting failed!")
            elif not enabled and oID.Is_POIS() is enabled:
               ScrCmds.raiseException(13454, "POIS disable setting failed!")  
         
         objMsg.printMsg("POIS SetFeatures(0x%2X) successful."%cmd)

      self.dut.driveattr['POWER_ON_TYPE']= attr

###########################################################################################################
###########################################################################################################
class CPois_Disable(CState):
   """
      Description: Class that will disable POIS (Power On In Standby)
   """            
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self, EnablePOIS = True):
      objMsg.printMsg("Disable POIS")
      oPOIS = CPois(self.dut,{'ENABLED':0}).run()  
            
###########################################################################################################
###########################################################################################################
class CDumpAsciiCELog(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import serialScreen
      oSerial = serialScreen.sptDiagCmds()

      sptCmds.enableDiags()

      if testSwitch.virtualRun:
         return

      sptCmds.gotoLevel('1')

      ScrCmds.insertHeader("START CE Log Dump")
      #Dump the critical event log
      CriticalEventLogData, summaryData, ceData = oSerial.getCriticalEventLog(30)
      self.evalCriticalLogCriteria(summaryData)

      #Dump the smart attributes
      CE_Attribute_Thresh_ignore_list = getattr(TP,'CE_Attribute_Thresh_ignore_list',['A',])
      CriticalEventLogData = oSerial.getCriticalEventAttributes(30,True, ignoreAttrList = CE_Attribute_Thresh_ignore_list)


      ScrCmds.insertHeader("END   CE Log Dump")

      CELogFileName = "%s_CE_Log.txt" % self.dut.serialnum
      CELogFile = GenericResultsFile(CELogFileName)
      CELogFile.open('w')
      try:
         CELogFile.write(CriticalEventLogData)
         CELogFile.close()
         if testSwitch.FtpPCFiles and not ConfigVars[CN].get('PRODUCTION_MODE',0):
            objMsg.printMsg("Retrieve file from ftp://col-tpecvs-01.colo.seagate.com/F3Opti/%s/%s" % (self.dut.nextOper, CELogFileName))
            try: RequestService("SendGenericFile", ((CELogFileName,), "Platform"))
            except:
               import traceback
               objMsg.printMsg("Error occurred during ftp of CE Log file:\n%s" % traceback.format_exc())

      finally:

         CELogFile.delete()

      objPwrCtrl.powerCycle(5000,12000,10,30)

   def evalCriticalLogCriteria(self, CELogSummaryCounts):
      inputErrDict = {}
      try:
         inputErrDictName = self.params['PARAM_NAME']       # Parameter name from StateTable.py, StateParams{}
         objMsg.printMsg("Test Parameters Name from the State Table - %s" % inputErrDictName, objMsg.CMessLvl.IMPORTANT)
      except:
         objMsg.printMsg("State Table CRITICAL_LOG -> PARAM_NAME - Not Found", objMsg.CMessLvl.IMPORTANT)

      try:
         inputErrDict = eval(self.params["PARAM_NAME"])     # from TP.py, prm_XXX2_CriticalEvents
      except:
         objMsg.printMsg("Critical Event Parameters - Not Found in Test Parameters", objMsg.CMessLvl.IMPORTANT)
         inputErrDict = {'EC_0x21':50, 'EC_0x22':50, 'EC_0x23':50, 'EC_0x43':50,}
         objMsg.printMsg("Script Default Error Limits - Update Test Parameters and State Table to Override", objMsg.CMessLvl.IMPORTANT)
      errDict = {}
      for key,val in inputErrDict.items():
         if key.find('EC_0x') > -1:
            key2 = int(key[5:],16)
            errDict[key2] = val

         else:
            errDict[key] = val

      for ec, limit in errDict.items():
         ecActual = CELogSummaryCounts.get(ec,0)
         if ecActual > limit:
            objMsg.printMsg("------------------- Failed Check Critical Logs --------------------------", objMsg.CMessLvl.IMPORTANT)
            failMessage = ("Failed Critical Events Error Code : %s Count=%s Limit=%s" % (ec, ecActual, limit) )
            ScrCmds.raiseException(13456, failMessage)
         elif ecActual > 0:
            objMsg.printMsg("Found %d entries of %s ec which is below limit of %d" % (ecActual, ec , limit))


###########################################################################################################
###########################################################################################################
class CATASignalSpeed_1_5(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self,):
      oSpeed = CSetATASignalSpeed(self.dut)
      oSpeed.run(1.5)


###########################################################################################################
###########################################################################################################
class CATASignalSpeed_3_0(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self,):
      oSpeed = CSetATASignalSpeed(self.dut)
      oSpeed.run(3.0)


###########################################################################################################
###########################################################################################################
class CSetATASignalSpeed(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self,reqSpeed = 'nominal'):
      """
        Set the ATA Signaling Speed using a smartLogWrite that issues an SCT-BIST command.  This does not
        actually write to the smart log so you should not expect to be able to read that smart log back.

        Use Identify Device Word 77 to determine the current signal speed, Word 76 to determine what the code supports,
        and Word 206 to determine if the code supports BIST (this word is not supported yet as of 1/29/2009)

        As of 6/1/09, it is no longer valid that if Word 77 is populated, then SCT BIST is supported.
      """
      objMsg.printMsg("Executing SetATASignalSpeed")
      from IntfClass import CIdentifyDevice

      speedOptions = {1.5        : 0x0100,   #this is the value that gets filled into 0x1c during buffer write
                      3.0        : 0x0200,
                      6.0        : 0x0400,
                      'nominal'  : 0x0000}   #resets to default native speed


      objMsg.printMsg('Attempting to set ATA Signaling Speed to %s' %reqSpeed)
      #get ID (word 77/76) data to determine what current speed we are set to
      oIdentifyDevice = CIdentifyDevice()
      currSpeed = oIdentifyDevice.getATASpeed()
      nativeSpeed = max(oIdentifyDevice.getSupportedATASpeeds())
      if reqSpeed == 'nominal':
         speed = speedOptions[nativeSpeed]
         objMsg.printMsg("Native (nominal) ATA speed = %s Gbps" %nativeSpeed)
      else:
         speed = speedOptions[reqSpeed]


      #Check to see if we are already at the requested speed.  If nominal, then speed needs to be reset to native speed.
      #if currSpeed == 0, then SCT reset not supported but F3 code should already be defaulted to native
      #if nominal and current speed > 0, check to see if we are already at the native speed.
      if (reqSpeed ==currSpeed and not testSwitch.FE_0143280_426568_P_SKIP_REQ_VS_CURRENT_SPEED_CHECK) or (reqSpeed == 'nominal' and currSpeed == 0)\
         or (reqSpeed == 'nominal' and currSpeed == nativeSpeed):
         if not testSwitch.virtualRun:
            objMsg.printMsg("ATA speed already at %s, skipping reset" %reqSpeed)
##            if reqSpeed == 1.5:
##               self.dut.driveattr['CUST_TESTNAME'] = 'SD1'
##            elif reqSpeed == 3.0:
##               self.dut.driveattr['CUST_TESTNAME'] = 'SD2'
            return
      elif testSwitch.WA_0130075_357260_SKIP_SPEED_CHECK:
         objMsg.printMsg("Skipping ATA Speed Check / Reset - (Descision based on flag: WA_0130075_357260_SKIP_SPEED_CHECK)")
         return
      elif currSpeed == 0:
         ScrCmds.raiseException(10207, "SCT-BIST not supported in F3 code")

      if testSwitch.NoIO:
         ICmd.SetATASpeed(speed)
      else:
         from math import floor
         # If the current RIM doesn't support the requested speed we need to fail and retry different cell.
         if max(theRim.getValidRim_IOSpeedList()) < floor(reqSpeed):
            objMsg.printMsg("Requested Speed %s not supported by this RIM" %reqSpeed)
            ScrCmds.raiseException(11044, "Requested ATA speed not supported by RIM")

         from IntfClass import CInterface
         oIntf = CInterface()

         oIntf.writeUniformPatternToBuffer('write')  #write one sector of zeros

         #update byteOffset 0 to indicate BIST command and update byteOffset 2 to indicate speed control mode
         oIntf.writeBytesToBuffer((0x0700, 0x0300))
         oIntf.writeBytesToBuffer((speed, 0x0000), byteOffset = (0, 0x1C))

         oIntf.displayBuffer('write')

         objMsg.printMsg("Issuing SCT-BIST command")
         oIntf.WriteOrReadSmartLog(0xe0,'write')
         ######################################

      objPwrCtrl.drvATASpeed = 0
	  
      if testSwitch.BF_0157147_231166_P_SET_XFER_PRIOR_LOCK_DOWN:
         # set the xfer rate prior to lockdown power cycle to keep test hardware and
         # drive in sync for the default xfer rate- important when SIC doesn't auto-negotiate speed
         ## Must be in [6, 6.0, 3, 1.5, 1.0, ...] it is converted to the integer part for 533
         if reqSpeed == 'nominal':
            ICmd.SetTransferRate(int(nativeSpeed))
         else:
            ICmd.SetTransferRate(int(reqSpeed))


      objPwrCtrl.powerCycle()

      #read ID data to check if requested speed was set
      oIdentifyDevice = CIdentifyDevice(force = True, sp_force = True)
      newSpeed = oIdentifyDevice.getATASpeed()

      # Don't fail if reqSpeed = 0 because 0 is resetting to nominal speed
      if (reqSpeed != 'nominal') and (reqSpeed != newSpeed) and not testSwitch.virtualRun:
         ScrCmds.raiseException(12412, "Failed to set ATA Signaling Speed")

      if newSpeed == 1.5:
         self.dut.driveattr['CUST_TESTNAME'] = 'SD1'
      elif newSpeed == 3.0:
         self.dut.driveattr['CUST_TESTNAME'] = 'SD2'


###########################################################################################################
###########################################################################################################
class CDrive_Pairing(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from IntfClass import CIdentifyDevice
      from IntfClass import CInterface
      self.oIntf = CInterface()

      self.oUtil = CUtility()
      oIdentifyDevice = CIdentifyDevice()
      dpSupported, encryptLoaded,encrptPassKeysLoaded = oIdentifyDevice.drivePairing()
      if not dpSupported:
         ScrCmds.raiseException(11043, "F3 code does not support drive pairing")

      if encrptPassKeysLoaded and not testSwitch.virtualRun:
         objMsg.printMsg('Drive Pairing Encryption keys and password previously loaded.  Can not re-load')
         self.dut.driveattr['SECURITY_TYPE'] = "3DES DRIVE PAIRING SECURITY"
         return

      if testSwitch.NoIO == 1:
         import sdbpCmds
         objMsg.printMsg('*** SERIAL PORT ***')
         objPwrCtrl.powerCycle()
         sptCmds.enableDiags
         sptCmds.enableESLIP()
         try:
            sdbpCmds.unlockDets()
         except:
            pass
      if not encryptLoaded:
         self.loadKeys(self.getDPesKeys(), 0x70)    #Load the encryption keys
      else:
         objMsg.printMsg('Encryption Keys already loaded')


      self.loadKeys(self.getPasswordKey(), 0x71) #Load the password key

      #read ID data to check if pairing set.  Currently not supported in F3
      objPwrCtrl.powerCycle()
      if testSwitch.NoIO:
         oIdentifyDevice = CIdentifyDevice(sp_force = True)
      else:
         oIdentifyDevice = CIdentifyDevice()
      dpSupported, encryptLoaded,encrptPassKeysLoaded = oIdentifyDevice.drivePairing()
      if encrptPassKeysLoaded:
         self.dut.driveattr['SECURITY_TYPE'] = "3DES DRIVE PAIRING SECURITY"
         objMsg.printMsg('Drive Pairing Complete')
      else:
         ScrCmds.raiseException(14001, "Drive Pairing not successful")

   def loadKeys(self,keys, cmd):
      if testSwitch.NoIO == 0:
         '''Load the 3 encryption keys by writing sector of data to buffer, then sending 0xf0 command'''
         self.updateRandomDataToBuffer()
         self.updateKeysToBuffer(keys)
         self.updateCRC32ToBuffer(keys)

         self.oIntf.displayBuffer('write')

      self.SndDrivePairingCmd(keys,cmd)

   def getDPesKeys(self):
      'First 24 bytes should be the 3 encrytion keys'
      #placeholder to generate keys

      key1 = 'EE55FA9C8F06DC9A'
      key2 = 'C0B1A2DE1E35BD07'
      key3 = '475902215D36EA70'
      return key1 + key2 + key3

   def getPasswordKey(self):
      'First 8 bytes should be the password keys'
      return 'A7DBF654FA64DDA6'

   def getRandomData(self):
      return 0x98769876  #placeholder to generate random data

   def updateRandomDataToBuffer(self):
      '''Fill whole buffer with random data.  Bytes 25-508 should be random data.  Other bytes will be overlayed with keys and CRC32'''
      dataPattern = self.oUtil.ReturnTestCylWord( self.getRandomData() )
      self.oIntf.writeUniformPatternToBuffer('write', dataPattern = dataPattern)  #write random patter to buffer

   def updateKeysToBuffer(self, keys):
      'First 24 bytes should be the 3 encrytion keys'

      byteOffset = 0
      for index in range(0,len(keys),16):
         key = keys[index:index + 16]
         dataPattern0 = self.oUtil.ReturnTestCylWord( int(key[:8],16) )
         dataPattern1 = self.oUtil.ReturnTestCylWord( int(key[8:],16) )

         self.oIntf.writeBytesToBuffer(dataPattern0, dataPattern1 = dataPattern1, byteOffset = (0, byteOffset))
         byteOffset += 8


   def updateCRC32ToBuffer(self,keys):
      '''Generate the current buffer which should be 24 bytes of encrytpion keys, 484 bytes of random data, 4 bytes of
      last 4 digits of drive serial number.  Use same CRC32 algorighm that the drive uses to calculate the CRC.  Replace
      last 4 bytes of buffer with the CRC32.  Update buffer'''

      import binascii

      #get key and random number
      randomData = self.getRandomData()

      #generate buffer
      keysAndCRClen = len(keys)/2 + 4
      rdmData  = hex(randomData).replace('0x','').replace('L','') * ((512-keysAndCRClen) / 4 ) #random data, 512 bytes - keys - sn
      sn       = binascii.hexlify(self.dut.serialnum[-4:]) # 4 bytes for serial num
      buffer     = keys + rdmData + sn

      buffNibbles = [buffer[i:i+2] for i in range(0,len(buffer),2)]

      if DEBUG > 0:
         objMsg.printMsg('Buffer Length = %s' %len(buffer))
         for i in range(0,len(buffer),32):
            objMsg.printMsg(buffer[i:i+8] + ' ' + buffer[i+8:i+16] + ' ' + buffer[i+16:i+24] + ' ' + buffer[i+24:i+32])

      #calculate CRC32
      crc = self.calcCRC32(buffNibbles)
      objMsg.printMsg('CRC32 = %8x' %crc)

      #update last 4 bytes of buffer with CRC32
      self.oIntf.writeBytesToBuffer(self.oUtil.ReturnTestCylWord(crc), byteOffset = (0, 508))

   def calcCRC32(self,buffer):
      '''Calculate the CRC32 with same algorithm the drive is using.  Refer to
      Seagate Drive Pairing Security with Secure Messaging spec for algorithm'''
      crcTable = self.generateCRCtable()

      crc = 0xFFFFFFFF
      for ch in buffer:
         chhx = int(ch,16)
         crc = (crc>>8) ^ crcTable[(crc^chhx) &0xff]

      return crc^0xFFFFFFFF

   def generateCRCtable(self):
      '''CRC table is based on this calculation
      crcTable= []
      poly = long(0xEDB88320)
      for i in xrange(256):
          crc = long(i)
          for i in xrange(8):
              if crc & 1L:   crc = (crc >> 1) ^ poly
              else:          crc = crc >> 1
          crcTable.append(crc & 0xFFFFFFFF)
      return crcTable'''


      return [0L,    1996959894L, 3993919788L, 2567524794L, 124634137L,  1886057615L,
      3915621685L, 2657392035L, 249268274L,  2044508324L, 3772115230L, 2547177864L,
      162941995L,  2125561021L, 3887607047L, 2428444049L, 498536548L,  1789927666L,
      4089016648L, 2227061214L, 450548861L,  1843258603L, 4107580753L, 2211677639L,
      325883990L,  1684777152L, 4251122042L, 2321926636L, 335633487L,  1661365465L,
      4195302755L, 2366115317L, 997073096L,  1281953886L, 3579855332L, 2724688242L,
      1006888145L, 1258607687L, 3524101629L, 2768942443L, 901097722L,  1119000684L,
      3686517206L, 2898065728L, 853044451L,  1172266101L, 3705015759L, 2882616665L,
      651767980L,  1373503546L, 3369554304L, 3218104598L, 565507253L,  1454621731L,
      3485111705L, 3099436303L, 671266974L,  1594198024L, 3322730930L, 2970347812L,
      795835527L,  1483230225L, 3244367275L, 3060149565L, 1994146192L, 31158534L,
      2563907772L, 4023717930L, 1907459465L, 112637215L,  2680153253L, 3904427059L,
      2013776290L, 251722036L,  2517215374L, 3775830040L, 2137656763L, 141376813L,
      2439277719L, 3865271297L, 1802195444L, 476864866L,  2238001368L, 4066508878L,
      1812370925L, 453092731L,  2181625025L, 4111451223L, 1706088902L, 314042704L,
      2344532202L, 4240017532L, 1658658271L, 366619977L,  2362670323L, 4224994405L,
      1303535960L, 984961486L,  2747007092L, 3569037538L, 1256170817L, 1037604311L,
      2765210733L, 3554079995L, 1131014506L, 879679996L,  2909243462L, 3663771856L,
      1141124467L, 855842277L,  2852801631L, 3708648649L, 1342533948L, 654459306L,
      3188396048L, 3373015174L, 1466479909L, 544179635L,  3110523913L, 3462522015L,
      1591671054L, 702138776L,  2966460450L, 3352799412L, 1504918807L, 783551873L,
      3082640443L, 3233442989L, 3988292384L, 2596254646L, 62317068L,   1957810842L,
      3939845945L, 2647816111L, 81470997L,   1943803523L, 3814918930L, 2489596804L,
      225274430L,  2053790376L, 3826175755L, 2466906013L, 167816743L,  2097651377L,
      4027552580L, 2265490386L, 503444072L,  1762050814L, 4150417245L, 2154129355L,
      426522225L,  1852507879L, 4275313526L, 2312317920L, 282753626L,  1742555852L,
      4189708143L, 2394877945L, 397917763L,  1622183637L, 3604390888L, 2714866558L,
      953729732L,  1340076626L, 3518719985L, 2797360999L, 1068828381L, 1219638859L,
      3624741850L, 2936675148L, 906185462L,  1090812512L, 3747672003L, 2825379669L,
      829329135L,  1181335161L, 3412177804L, 3160834842L, 628085408L,  1382605366L,
      3423369109L, 3138078467L, 570562233L,  1426400815L, 3317316542L, 2998733608L,
      733239954L,  1555261956L, 3268935591L, 3050360625L, 752459403L,  1541320221L,
      2607071920L, 3965973030L, 1969922972L, 40735498L,   2617837225L, 3943577151L,
      1913087877L, 83908371L,   2512341634L, 3803740692L, 2075208622L, 213261112L,
      2463272603L, 3855990285L, 2094854071L, 198958881L,  2262029012L, 4057260610L,
      1759359992L, 534414190L,  2176718541L, 4139329115L, 1873836001L, 414664567L,
      2282248934L, 4279200368L, 1711684554L, 285281116L,  2405801727L, 4167216745L,
      1634467795L, 376229701L,  2685067896L, 3608007406L, 1308918612L, 956543938L,
      2808555105L, 3495958263L, 1231636301L, 1047427035L, 2932959818L, 3654703836L,
      1088359270L, 936918000L,  2847714899L, 3736837829L, 1202900863L, 817233897L,
      3183342108L, 3401237130L, 1404277552L, 615818150L,  3134207493L, 3453421203L,
      1423857449L, 601450431L,  3009837614L, 3294710456L, 1567103746L, 711928724L,
      3020668471L, 3272380065L, 1510334235L, 755167117L]

   def SndDrivePairingCmd(self, keys, features):
      objMsg.printMsg("Issuing security drive pairing command:  Command 0xF0, Features %2X)" %features)
      if testSwitch.NoIO == 0:
         drivePr = ICmd.PassThrough(-1,0xF0,0x0,0x0,features)
         objMsg.printMsg("drivePr data: %s" % drivePr, objMsg.CMessLvl.IMPORTANT)

         if drivePr['LLRET'] != OK:
            ScrCmds.raiseException(14001, "Drive Pairing 0xF0 command Failed.  Features = %2X" %features)
      else: 
         # SP version
         import sdbpCmds
         import traceback

         try:
            objMsg.printMsg("SP drivePairing")
            data, error, dataBlock = sdbpCmds.drivePairing(features,keys)
         except:
            objMsg.printMsg("drivePairing failure=%s" % (traceback.format_exc(),))
            ScrCmds.raiseException(14001, "Drive Pairing command Failed.  Features = %2X" %features)

###########################################################################################################
###########################################################################################################
class CEnableLACheck(CState):
   """
      Enable Hitachi LA_Check mode
         Clear mode page 0x38, byte 0x14, bit 0
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      ICmd.enable_LA_CHECK()

###########################################################################################################
###########################################################################################################
class CDisableLACheck(CState):
   """
      Disable Hitachi LA_Check mode
         Set mode page 0x38, byte 0x14, bit 0
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      ICmd.disable_LA_CHECK()

###########################################################################################################
###########################################################################################################
class CPrepNonMCDrive(CState):
   """
      Performs the requisit clearing of drive tables and full pack preperation if the drive is transitioning
         from a MC enabled drive to one that isn't MC
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   def run(self):
      if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
         from Serial_SerFmt import CSerialFormat
      else:
         from base_SerialTest import CSerialFormat
      from base_SATACCVTest import CCleanupPostCCV


      if self.dut.MCDriveReprocess and testSwitch.Media_Cache:
         CCleanupPostCCV(self.dut, params = {'RESET_AMPS': 0}).run()
   
         fmtOptions = TP.formatOptionsChkMrgG.copy()
         fmtOptions.update({
            'spc_id'          : 2000,
            'forceFormat'     : 1,
            'collectBERdata'  : 0,
            })
   
         if testSwitch.BF_0194845_231166_P_EN_ESLIP_POST_FMT_NONMCPREP:
            curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

         CSerialFormat(self.dut, {'FORMAT_OPTIONS': str(fmtOptions)}).run()
         if testSwitch.BF_0194845_231166_P_EN_ESLIP_POST_FMT_NONMCPREP:
            sptCmds.enableESLIP()
      else:
         objMsg.printMsg("Drive isn't a MC reprocess drive- bypassing")

