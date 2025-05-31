#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements the CPC ICmd interface
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CPC_ICmd.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CPC_ICmd.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
import Constants
from Constants import *
from base_ICmd import base_ICmd
from CPCRim import BaseCPCInit
from Utility import CUtility

import ScrCmds
import re
import MessageHandler as objMsg


class CPC_ICmd(base_ICmd):

   def __init__(self, params, objPwrCtrl):
      base_ICmd.__init__(self, params, objPwrCtrl)
      self.__func = ''
      self.aliasList = []
      self.ovrPrms = {}
      self.prmName = ''
      self.IdentifyDeviceBuffer = ''
      self.objPwrCtrl = objPwrCtrl

   def __getattribute__(self, name):
      aliasList = base_ICmd.__getattribute__(self,'aliasList')
      if name in aliasList:
         name = aliasList[name]

      try:
         return base_ICmd.__getattribute__(self, name)
      except AttributeError:
         if name in self.passThroughList:
            self.prmName = name
            return self.overridePrmCall
         elif name in self.directCallList or (hasattr(self.params, name) and not hasattr(Constants, name)):
            self.prmName = name
            return self.directCall
         else:
            self.__func = name
            return self.__ICmdWrapper

   def St(self, *args, **kwargs):
      if testSwitch.WA_0139515_231166_P_OVERRIDE_TO_8_PHYSICAL_TO_LOGICAL_BLOCKS_IN_CPC:
         stat = base_ICmd.St(self, *args, **kwargs)
         if (len(args) and args[0] == 514) or ('test_num' in kwargs and kwargs['test_num'] == 514):
            self.__fixLogicalToPhysicalSectorSize()
         return stat
      else:
         return base_ICmd.St(self, *args, **kwargs)

   def downloadIORimCode(self):
      pass

   def getRimCodeVer(self):
      """
      Get the rim code version for CPC
      """
      cpcCheckObj = BaseCPCInit()
      return float(cpcCheckObj.stripVer(cpcCheckObj.CPCVer))

   def GetIdentifyBuffer(self):
      """
      Retreive buffer from drive
      """
      retData = ICmd.GetBuffer(RBF,0,512)
      self.IdentifyDeviceBuffer = retData['DATA']
      return retData

   def SetRFECmdTimeout(self, timeout):
      SetRFECmdTimeout(timeout)


   def getATASpeed(self):

      if testSwitch.virtualRun:
         ATA_SignalSpeed = 2
      else:
         ATA_SignalSpeed = CUtility.numSwap(self.IdentifyDeviceBuffer[154:156])

      bitsSet = ATA_SignalSpeed & 0x6

      speedOptions = {0x2: 1.5,
                    0x4: 3.0,
                    0x6: 6.0}

      if speedOptions.has_key(bitsSet):
         objMsg.printMsg("CURRENT SIGNAL SPEED IS %s Gbps" %speedOptions[bitsSet])
         return speedOptions[bitsSet]
      else:
         objMsg.printMsg("Code does not support setting the signal speed (SCT-BIST commands)")
         return 0

   def dumpATAInfo(self):
      """
      Execute test 504 to retreive ata info from last cmd
      """

      self.St({'test_num': 504,
               'timeout':60,
               'DblTablesToParse' : ['P5XX_TFREG_LBA','P5XX_TFREGEXT'],
               'stSuppressResults' : ST_SUPPRESS__ALL, #| ST_SUPPRESS_RECOVER_LOG_ON_FAILURE,
               })
      if testSwitch.virtualRun:
         ret = {'ERR_REG': '0', 'STATUS': '0x50', 'LBA_UPPER': '0', 'LBA_LOWER': '0', 'SCNT': '0', 'DEV': '0'}
      else:
         if 'P5XX_TFREG_LBA' in self.dut.objSeq.SuprsDblObject:
            ret = self.dut.objSeq.SuprsDblObject['P5XX_TFREG_LBA'][-1].copy()
            del self.dut.objSeq.SuprsDblObject['P5XX_TFREG_LBA']
         else:
            ret = self.dut.objSeq.SuprsDblObject['P5XX_TFREGEXT'][-1].copy()
            del self.dut.objSeq.SuprsDblObject['P5XX_TFREGEXT']

      return ret



   def updateFISattrs_FW_ID(self):
      """
      Just used to update FW attributes prior to DataToDisc creation
      """
      self.IdentifyDevice()

   def WriteMIFDataToDisc(self, callback):
      """
      Write manufacturing information file to DUT using test 795 (cpc ver > 2.206) or 595 (cpc ver < 2.206)
      """
      cpcVer = self.getRimCodeVer()
      if cpcVer >= 2.206 or not int(cpcVer) == 2:
         #If we've passed the blockpoint or if this is an eval version (which they could recompile with changes.
         dtdTestNum = 795
      else:
         dtdTestNum = 595

      RegisterResultsCallback(callback ,63,0)
      try:
         ret = self.St({
               'test_num': dtdTestNum,
               'prm_name':"Send CCC data to drive",
               'timeout': 3600
            })
      finally:
         RegisterResultsCallback("",63)

      return ret

   def SetTransferRate(self, transferRate):
      """
      Set the drive transfer rate based on the integer part of the transfer rate.
      enum: 6, 3, 1 == 6gbps, 3gbps, 1.5gbps
      also 2, 4 for FC
      """
      self.St(self.params.TransferMode, INTERFACE_SPEED = transferRate)


   def __ICmdWrapper(self, *args, **kwargs):
      """
      Generic wrapper re-call for ICmd in ve/cm
      """
      try:
         #Call the object in ICmd
         stat = getattr(ICmd, self.__func)(*args, **kwargs)
         if testSwitch.WA_0139515_231166_P_OVERRIDE_TO_8_PHYSICAL_TO_LOGICAL_BLOCKS_IN_CPC:
            if self.__func in ['IdentifyDevice',]:
               self.__fixLogicalToPhysicalSectorSize()
         if testSwitch.FE_0152536_081849_P_AAU_FAULT_DETECTION_ENABLE and int(stat.get('AAU_FAULT','0')):
            cpcReset = str(CellIndex)+'_AAU'
            RequestService('PutTuple',(cpcReset,1,))
         return stat

      except Exception, e:
         if ' Expected ' in str(e):
            self.__CpcErrParse(e)
         else:
            raise

   def __fixLogicalToPhysicalSectorSize(self):
      if testSwitch.WA_0139515_231166_P_OVERRIDE_TO_8_PHYSICAL_TO_LOGICAL_BLOCKS_IN_CPC and self.getRimCodeVer() >= 2.235:
         self.St({'test_num':506, 'prm_name': 'SET logical blocks per physical to 8', 'ID_WORD106_OVERRIDE': 3, 'timeout': 60})

   def __CpcErrParse(self, excInst):
      """
      Parse and reassign error code from CPC based on response XML parse
      """
      err = str(excInst)

      try:
         func = getattr(excInst,  'FUNC',  repr(self.__func))
      except:
         errMat = re.search('FUNC="(.+)"\s*ERR="(.+)"', err)
         if errMat:
            func,err = errMat.groups()


      if 'ATA_DRIVEFAULT:Driver abort' in err and 'write' in func.lower():
         ScrCmds.raiseException(13412, "Write aborted in cmd %s" % func)
      elif '':
         ScrCmds.raiseException(13424, "ATA Ready error in cmd %s" % func)
      else:
         ScrCmds.raiseException(14001, "Generic ATA Error %s" % err)


   if testSwitch.FE_0144363_421106_P_TIMEOUT_SPEC_FOR_SMART_LONG_DST:
      def LongDST(self,TimeoutLimit = 0):
         """
         Execute long DST on DUT in polling mode
         """
         try:
            tempPrm = CUtility.copy(self.params.LongDST)
            if TimeoutLimit != 0:
               tempPrm['MAX_COMMAND_TIME'] = TimeoutLimit
            self.St(tempPrm)
         except:
            smartEnableOperData = self.SmartEnableOper()
            objMsg.printMsg("DST SmartEnableOper data: %s" % smartEnableOperData, objMsg.CMessLvl.IMPORTANT)
            if smartEnableOperData['LLRET'] != 0:
               ScrCmds.raiseException(13455, 'Failed Smart Enable Oper - During Long DST')
            DSTLogData = self.SmartReadLogSec(6, 1)               # 6=DST Log, 1=#DST Log Sectors
            objMsg.printMsg("DST SmartReadLogSec data: %s" % DSTLogData, objMsg.CMessLvl.IMPORTANT)
            ScrCmds.raiseException(13459, 'Failed Smart Long DST - Drive Self Test')
   else:
      def LongDST(self):
         """
         Execute long DST on DUT in polling mode
         """
         try:
            self.St(self.params.LongDST)
         except:
            smartEnableOperData = self.SmartEnableOper()
            objMsg.printMsg("DST SmartEnableOper data: %s" % smartEnableOperData, objMsg.CMessLvl.IMPORTANT)
            if smartEnableOperData['LLRET'] != 0:
               ScrCmds.raiseException(13455, 'Failed Smart Enable Oper - During Long DST')
            DSTLogData = self.SmartReadLogSec(6, 1)               # 6=DST Log, 1=#DST Log Sectors
            objMsg.printMsg("DST SmartReadLogSec data: %s" % DSTLogData, objMsg.CMessLvl.IMPORTANT)
            ScrCmds.raiseException(13459, 'Failed Smart Long DST - Drive Self Test')


   def ShortDST(self):
      """
      Execute short DST on DUT in polling mode
      """
      try:
         self.St(self.params.ShortDST)
      except:
         smartEnableOperData = self.SmartEnableOper()
         objMsg.printMsg("DST SmartEnableOper data: %s" % smartEnableOperData, objMsg.CMessLvl.IMPORTANT)
         if smartEnableOperData['LLRET'] != 0:
            ScrCmds.raiseException(13455, 'Failed Smart Enable Oper - During Short DST')
         DSTLogData = self.SmartReadLogSec(6, 1)               # 6=DST Log, 1=#DST Log Sectors
         objMsg.printMsg("DST SmartReadLogSec data: %s" % DSTLogData, objMsg.CMessLvl.IMPORTANT)
         ScrCmds.raiseException(13458, 'Failed Smart Short DST - Drive Self Test')

   def FillBuffer(self, buffFlag , byteOffset, data):
      return ICmd.FillBuffer(buffFlag , byteOffset, data)


   def WriteFinalAssemblyDate(self, weekstr):
      param4 = (ord(weekstr[0]) << 8) | (ord(weekstr[1]))
      param5 = (ord(weekstr[2]) << 8) | (ord(weekstr[3]))
      DriveAttributes["FINAL_ASSY_DATE"]= weekstr
      prm = self.params.WriteFinalAssemblyDate.copy()
      prm["FINAL_ASSEMBLY_DATE"] = (0,0,param4, param5)

      self.St(prm,TEST_FUNCTION=(0))  # Write Final assembly date
      self.St(prm,TEST_FUNCTION=(1))  # Read  Final assembly date
      self.St(prm,TEST_FUNCTION=(2))  # Compare Final assembly date


   def disable_WriteCache(self, exc = 1):
      #Disable Write Cache
      return self.SetFeatures(0x82, exc = exc)

   def enable_WriteCache(self, exc = 1):
      #Enable Write Cache
      return self.SetFeatures(0x02, exc = exc)

   if 1:    # CPC to use T510 instead of intrinsic functions, so that CCT dblogs can be displayed and sent to FIS
      def SequentialCCT(self, Cmd1, STARTING_LBA, MAXIMUM_LBA, BLKS_PER_XFR = 256, STEP_LBA = 256, \
                        minthd = 0, midthd = 0, maxthd = 0, COMPARE_FLAG = 0, Cmd2 = 0, exc = 1):
         objMsg.printMsg("CPC_ICmd.py SequentialCCT")
         backup = testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION
         try:
            testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION = 1
            from CPC_ICmd_TN import CPC_ICmd_TN
            import base_CPC_ICmd_TN_Params

            obj = CPC_ICmd_TN(params = base_CPC_ICmd_TN_Params, objPwrCtrl = self.objPwrCtrl)
            return obj.SequentialCCT(Cmd1, STARTING_LBA, MAXIMUM_LBA, BLKS_PER_XFR, STEP_LBA, minthd, midthd, maxthd, COMPARE_FLAG, Cmd2, exc)
         finally:
            testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION = backup

      def RandomCCT(self, Cmd1, STARTING_LBA, MAXIMUM_LBA, BLKS_PER_XFR = 256, CMDCNT = 1, \
                     minthd = 0, midthd = 0, maxthd = 0, COMPARE_FLAG = 0, Cmd2 = 0, exc = 1):                     
         objMsg.printMsg("CPC_ICmd.py RandomCCT")
         backup = testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION
         try:
            testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION = 1
            from CPC_ICmd_TN import CPC_ICmd_TN
            import base_CPC_ICmd_TN_Params

            obj = CPC_ICmd_TN(params = base_CPC_ICmd_TN_Params, objPwrCtrl = self.objPwrCtrl)
            return obj.RandomCCT(Cmd1, STARTING_LBA, MAXIMUM_LBA, BLKS_PER_XFR, CMDCNT, minthd, midthd, maxthd, COMPARE_FLAG, Cmd2, exc)
         finally:
            testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION = backup

   def SetProductID (self, PROD_ID = 0):
      prm506 = self.params.SetProductID
      prm506['PROD_ID'] = PROD_ID
      self.St(prm506)

