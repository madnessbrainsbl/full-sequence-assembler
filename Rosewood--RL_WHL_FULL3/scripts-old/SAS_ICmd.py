#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements the SATA Initiator interface
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SAS_ICmd.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SAS_ICmd.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
import Constants
from Constants import *
import ScrCmds
from Test_Switches import testSwitch
from Utility import CUtility
from base_Initiator_CMD import initCmd, PASS_RETURN
import binascii, struct, types, traceback
import MessageHandler as objMsg

from Drive import objDut
import PIF

dut = objDut

lbaTuple = CUtility.returnStartLbaWords
wordTuple = CUtility.ReturnTestCylWord

DEFAULT_BUFFER_SIZE = (0,512)


class SAS_ICmd(initCmd):
   def __init__(self, params, objPwrCtrl):
      initCmd.__init__(self,  params, objPwrCtrl)
      objMsg.printMsg("Using SAS_ICmd for ICmd resolution")
      self.tempBuffer = False

   def __getattribute__(self, name):
      aliasList = initCmd.__getattribute__(self,'aliasList')
      if name in aliasList:
         name = aliasList[name]

      try:
         return initCmd.__getattribute__(self, name)
      except AttributeError:
         if name in self.passThroughList:
            self.prmName = name
            return self.overridePrmCall
         elif name in self.directCallList or (hasattr(self.params, name) and not hasattr(Constants, name)):
            self.prmName = name
            return self.directCall
         else:
            raise

   def __overrideTestParms(self, args, kwargs):
      test = 0

      #combine the args/kwargs for dict types
      kwds = {}
      args = list(args)

      for arg in list(args):
         if type(arg) == types.IntType:
            test = arg
         elif type(arg) == types.DictionaryType:
            kwds.update(arg)
            del args[args.index(arg)]
      else:
         test = kwargs.get('test_num', 0)

      kwds.update(kwargs)

      if test == 0:
         test = kwds.get('test_num', 0)



      return args, kwds

   def St(self, *args, **kwargs):

      if testSwitch.BF_0142561_231166_P_FIX_STEP_LBA_SAS:
         args, kwargs = self.__overrideTestParms(args, kwargs)
         if kwargs.get('test_num', 0) == 510:
            # If TEST_EXE_TIME_SECONDS is set in initiator 510 will run until that TMO expires
            self.SetRFECmdTimeout(0)

      try:
         ret = initCmd.St(self, *args, **kwargs)
      except ScriptTestFailure, (failureData):
         if testSwitch.WA_0169134_470833_P_T538_EC10179_UNKNOWN_MODEL_NUMBER and failureData[0][2] in [11107, 10179]:
            st(507, TEST_FUNCTION = 1, UNKNOWN_MODEL_NUMBER =0x0003)
            ret = initCmd.St(self, *args, **kwargs)
         else:
            raise
      else:
         if testSwitch.BF_0142561_231166_P_FIX_STEP_LBA_SAS:
            if kwargs.get('test_num', 0) == 510:
               from TestParamExtractor import TP
               self.SetRFECmdTimeout(TP.prm_IntfTest["Default ICmd Timeout"])

      return ret


   def ZeroCheck(self, minLBA, maxLBA, scnt):
      prm = self.params.ZeroCheck.copy()

      prm['PATTERN_LSW'] = 0
      prm['PATTERN_MSW'] = 0
      prm['BLOCK_TRANSFER_COUNT'] = 0xFFFF & scnt

      prm['START_LBA34'] = lbaTuple(minLBA)
      prm['BLOCKS_TO_TRANS'] = wordTuple(maxLBA-minLBA)

      ret = self.St(prm)
      return self.translateStReturnToCPC(ret)

   def HardReset(self):
      pass

   def SetIntfTimeout(self, timeout = 30000):
      self.IntfTimeout = timeout
      timeout = int(timeout)
      prm = self.params.CommandTimeout.copy()
      prm['COMMAND_TIMEOUT_MS'] = timeout & 0xFFFF
      self.St(prm)



   def SetRFECmdTimeout(self, timeout = 600):
      timeout = int(timeout)
      prm = self.params.CommandTimeout.copy()
      prm['TEST_EXE_TIME_SECONDS'] = timeout
      self.St(prm)

   def SetFeatures(self, *args, **kwargs):
      #TODO: need mode sense commands here... do we intercept at SATA_SetFeatures layer?
      return { 'LLRET': 0,
               'ERR':   0,
               'STS':   0x50,
               'LBA':   0,
               'SCNT':  0,
               'DEV':   0,
               'CYL':   0,
               'HEAD':  0,
               'SCTR':  0,
            }

   def GetDriveSN(self, partNum = None, partNumOnlyValue = False):

      queryPrm =  self.params.IdentifyDevice.copy()
      queryPrm['PAGE_CODE'] = 0x80
      queryPrm['DblTablesToParse'] = ['P514_VPD_PAGE_DATA',]
      queryPrm['ENABLE_VPD'] = 1
      self.St(queryPrm)
      buff = []
      colNames = ['B%X' % i for i in range(16)]
      if not testSwitch.virtualRun:
         for row in self.dut.objSeq.SuprsDblObject['P514_VPD_PAGE_DATA']:
            for col in colNames:
               item = row[col]
               if item != None:
                  buff.append(item)
      else:
         return HDASerialNumber

      if testSwitch.BF_0151846_231166_P_SUPPORT_PN_BASED_SN_FIELD:

         if testSwitch.FE_0152759_231166_P_ADD_ROBUST_PN_SN_SEARCH_AND_VALIDATION:
            # First validate if the current PN value is printable
            def_offset = 4
            pnOffsetValue = ''

            defOffsetValue = CUtility.strBufferToBinString(''.join(buff))[def_offset:def_offset+SN_FIELD_WIDTH]
            pn_offset = CUtility.getRegex(partNum, getattr(PIF, 'SHIFTED_SN_MASK', {}) )
            if pn_offset != None:
               pnOffsetValue = CUtility.strBufferToBinString(''.join(buff))[pn_offset:pn_offset+SN_FIELD_WIDTH]

            if testSwitch.BF_0153991_231166_P_FIX_DEF_MATCH_PN_ROBUST_SEARCH:
               if not (pn_offset != None and objMsg.isPrintable(pnOffsetValue) and pnOffsetValue != ''):
                  if partNumOnlyValue and pn_offset != None:
                     # If we had a defined pn_offset and we have to match then fail
                     ScrCmds.raiseException(13420, "IdentifyDevice SerialNum mismatch")
                  elif partNumOnlyValue and pn_offset == None:
                     # If we have to match and there is no defined pn offset then we must match default
                     pnOffsetValue = defOffsetValue
                  else:
                     #This case is for restarts with older F3 code with a different offset
                     for pn, offset in getattr(PIF, 'SHIFTED_SN_MASK', {}).items():
                        pnOffsetValue = CUtility.strBufferToBinString(''.join(buff))[offset:offset+SN_FIELD_WIDTH]
                        if objMsg.isPrintable(pnOffsetValue) and pnOffsetValue != '':
                           break
                     else:
                        #try default offset
                        pnOffsetValue = defOffsetValue

               if not objMsg.isPrintable(pnOffsetValue) or pnOffsetValue == '':
                  # If none were printable we bail
                  ScrCmds.raiseException(13420, "Unable to locate valid serial nubmer in identify data")
            else:
               if not (pn_offset != None and objMsg.isPrintable(pnOffsetValue)):
                  if partNumOnlyValue and pn_offset != None:
                     # If we had a defined pn_offset and we have to match then fail
                     ScrCmds.raiseException(13420, "IdentifyDevice SerialNum mismatch")
                  elif partNumOnlyValue and pn_offset == None:
                     # If we have to match and there is no defined pn offset then we must match default
                     pnOffsetValue = defOffsetValue
                  else:
                     #This case is for restarts with older F3 code with a different offset
                     for pn, offset in getattr(PIF, 'SHIFTED_SN_MASK', {}).items():
                        pnOffsetValue = CUtility.strBufferToBinString(''.join(buff))[offset:offset+SN_FIELD_WIDTH]
                        if objMsg.isPrintable(pnOffsetValue):
                           break
                     else:
                        #try default offset
                        pnOffsetValue = defOffsetValue

               if not objMsg.isPrintable(pnOffsetValue):
                  # If none were printable we bail
                  ScrCmds.raiseException(13420, "Unable to locate valid serial nubmer in identify data")
            return pnOffsetValue


         else:
            def_offset = 4
            defaultOffsetValue = CUtility.strBufferToBinString(''.join(buff))[def_offset:def_offset+SN_FIELD_WIDTH]

            pn_offset = CUtility.getRegex(partNum, getattr(PIF, 'SHIFTED_SN_MASK', {}) )
            if pn_offset == None:
               pn_offset = def_offset

            pnOffsetValue = CUtility.strBufferToBinString(''.join(buff))[pn_offset:pn_offset+SN_FIELD_WIDTH]

            if objMsg.isPrintable(pnOffsetValue):
               return pnOffsetValue
            else:
               return defaultOffsetValue


      else:
         return CUtility.strBufferToBinString(''.join(buff))[4:12]


   def IdentifyDevice(self, exc = 1):
      #self.HardReset()
      self.IdentifyDeviceBuffer = '\x00'*512#[]

      buffer = []
      queryTypes = [(0, 'P514_STD_INQUIRY_DATA'),
                    (0xC0, 'P514_VPD_PAGE_DATA', {'ENABLE_VPD':1}),
                    #(0x80, 'P514_VPD_PAGE_DATA'),
                    #(0xC1, ''),
                    (0xC3, '')]

      queryPrm =  self.params.IdentifyDevice.copy()
      for query in queryTypes:
         queryPrm['PAGE_CODE'] = query[0]
         #if query[1] != '':
         #   queryPrm['DblTablesToParse']= [query[1],]
         if len(query) > 2:
            queryPrm.update(query[2])

         ret = self.St(queryPrm)



      # Enable this code if the drive needs to be formatted prior to any interface commands-
      #  Can happen early in a program or during large blockpoints where you only want to upgrade F3 code
      #self.ClearFormatCorrupt_1()
      #self.UnlockFactoryCmds()
      #self.ClearFormatCorrupt()
      #self.FormatDevice()


      if testSwitch.BF_0151846_231166_P_SUPPORT_PN_BASED_SN_FIELD:
         self.GetDriveSN(self.dut.partNum)
      else:
         self.GetDriveSN()
      self.getATASpeed()

      from TCG import CTCGPrepTest, LifeStates
      #try:
      if testSwitch.BF_0180787_231166_P_REMOVE_FDE_CALLBACKS_FOR_CHECKFDE:
         oTCG = CTCGPrepTest(dut)
         try:
            for retry in xrange(2):
               try:
                  oTCG.CheckFDEState()
                  break
               except:
                  #Probably not FDE or isn't prepped
                  self.dumpATAInfo()
                  objMsg.printMsg('Error in determining lifestate- #%d' % ( retry, ))
                  objMsg.printMsg("%s" % (traceback.format_exc(),))
                  self.spinUpDrive()
         finally:
            oTCG.RemoveCallback()

      else:
         for retry in xrange(2):
            try:
               CTCGPrepTest(dut).CheckFDEState()
               break
            except:
               #Probably not FDE or isn't prepped
               self.dumpATAInfo()
               objMsg.printMsg('Error in determining lifestate- #%d' % ( retry, ))
               objMsg.printMsg("%s" % (traceback.format_exc(),))
               self.spinUpDrive()



      try:
         self.GetMaxLBA()
      except:
         objMsg.printMsg("GetMaxLBA retreival failed: bypassing for now\n%s" % (traceback.format_exc(),))
         if testSwitch.WA_0145880_231166_P_FIX_INIT_HANG_BDG_DL:
            self.objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = False)  #Do spinup, sense, etc.
         self.maxlba = 0


      return PASS_RETURN

   def DisplayBadBlocks(self):
      self.UnlockFactoryCmds()

      self.St( self.params.DisplayBadBlocks )
      if testSwitch.virtualRun:
         return {'NUMBER_OF_TOTALALTS': 0, 'NUMBER_OF_PENDING_ENTRIES': 0}
      else:
         return {'NUMBER_OF_PENDING_ENTRIES': 0, 'NUMBER_OF_TOTALALTS':int(self.dut.objSeq.SuprsDblObject['P000_FLAW_COUNT'][-1]['NUMBER_OF_FLAWS'])}


   def MergeDefectLists(self, maxDefects = None, formatDrive = True, maxServoDefects = None):

      #Transfer the G list and ASFT
      prm = self.params.MergeDefectLists.copy()
      if maxDefects != None:
         prm['MAX_GLIST_ENTRIES'] = maxDefects

      if maxServoDefects != None:
         prm['MAX_SERVO_DEFECTS'] = maxServoDefects

      self.St(prm)

      #Transfer the skipped tracks
      if not testSwitch.WA_0143406_231166_DISABLE_SAS_SKIP_TRK_MERGE:
         prm = self.params.MergeDefectLists.copy()
         prm['SERVO_DEFECT_FUNCTION'] = 6
         prm['GLIST_OPTION'] = 4
         prm['prm_name'] = 'MergeDefectLists added skipped tracks.'
         self.St(prm)

      if formatDrive:
         #Set long TMO
         if testSwitch.FE_0146430_231166_P_ENABLE_CERTIFY_SAS_FMT:
            self.St(self.params.FormatDriveTimeout_Certify)
            self.St(self.params.FormatDrive_CertifyEnabled)
         else:
            self.St(self.params.FormatDriveTimeout)
            self.St(self.params.FormatDrive_CertifyDisabled)
         # Reset TMO
         self.SetIntfTimeout()
         self.SetRFECmdTimeout()

      return PASS_RETURN


   def updateFISattrs_FW(self):
      """
      Ensure we have the most current FW rev info in FIS DriveAttributes
      """

      prm_StdInquiry = self.params.IdentifyDevice.copy()
      prm_StdInquiry.update({'DblTablesToParse':['P514_STANDARD_INQUIRY'],})
      self.St(prm_StdInquiry)

      if testSwitch.virtualRun != 1:
         attrTable = self.dut.objSeq.SuprsDblObject['P514_STANDARD_INQUIRY'][-1]
         DriveAttributes["PROD_REV"] = attrTable['SCSI_FW_REV']
         DriveAttributes["SCSI_CODE"]= attrTable['SCSI_FW_REV']
         del self.dut.objSeq.SuprsDblObject['P514_STANDARD_INQUIRY']

   def updateFISattrs_Svo(self):
      """
      Ensure we have the most current servo rev info in FIS DriveAttributes
      """

      prm_FwServoInfo = self.params.IdentifyDevice.copy()
      prm_FwServoInfo.update({'ENABLE_VPD': 1,
                              'PAGE_CODE': 0x00c0,
                              'DblTablesToParse':['P514_FIRMWARE_NUMBERS'],})
      self.St(prm_FwServoInfo)

      if testSwitch.virtualRun != 1:
         attrTable = self.dut.objSeq.SuprsDblObject['P514_FIRMWARE_NUMBERS'][-1]
         svoCode = attrTable['TMS_OR_SERVO_RAM_REV'][-4:]
         DriveAttributes["SERVO_CODE"] = svoCode
         DriveAttributes["DOWNLOAD"]= "%s-%s" %(attrTable['SCSI_FW_REV'],svoCode)
         del self.dut.objSeq.SuprsDblObject['P514_FIRMWARE_NUMBERS']

   def updateFISattrs_FW_ID(self):
      """
      Just used to update FW attributes prior to DataToDisc creation
      """
      self.updateFISattrs_FW()
      self.updateFISattrs_Svo()


   def WriteMIFDataToDisc(self, callback):
      """
      Write manufacturing information file to DUT using test 795 (cpc ver > 2.206) or 595 (cpc ver < 2.206)
      """

      RegisterResultsCallback(callback ,6,0)
      try:
         ret = self.St(self.params.WriteMIFDataToDisc)
      finally:
         RegisterResultsCallback("",6)

      if testSwitch.BF_0147176_357552_P_PWRCYCLE_AFTER_CALLBACK_FOR_D_SENSE:
         #PwrCycle because callback may be interfering with ignore 11107 errors on initiator
         self.objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = True)  #Do spinup, sense, etc.

      return ret


   def dumpATAInfo(self):
      self.St({'test_num'           : 504,
               'timeout'            : 60,
               'prm_name'           : 'dumpATAInfo',
               'DblTablesToParse'   : ['P504_SENSE_DATA','P504_LAST_CMD_STATUS'],
               'stSuppressResults'  : ST_SUPPRESS__ALL,
               #'stSuppressResults' : ST_SUPPRESS__ALL | ST_SUPPRESS_RECOVER_LOG_ON_FAILURE,
               })

      ret = {'ERR_REG': '0', 'STATUS': '0x50', 'LBA_UPPER': '0', 'LBA_LOWER': '0', 'SCNT': '0', 'DEV': '0'}

      if not testSwitch.virtualRun:
         if 'P504_LAST_CMD_STATUS' not in self.dut.objSeq.SuprsDblObject:
            ret['STATUS'] = '0x50' #no last cmd?
         elif self.dut.objSeq.SuprsDblObject['P504_LAST_CMD_STATUS'][-1]['*'] == '0':
            ret['STATUS'] = '0x50'
         else:
            ret['STATUS'] = self.dut.objSeq.SuprsDblObject['P504_LAST_CMD_STATUS'][-1]['*']

      return ret

   def translateStReturnToCPC(self, stat):
      ataInfo = self.dumpATAInfo()

      retDict = {
         'LLRET': stat[2],
         'ERR':   int(ataInfo['ERR_REG'],16),
         'STS':   int(ataInfo['STATUS'],16),
         'LBA':   int(ataInfo['LBA_UPPER'],16) + int(ataInfo['LBA_LOWER'],16),
         'SCNT':  int(ataInfo['SCNT'],16),
         'DEV':   int(ataInfo['DEV'],16),

         }
      retDict.update({
            'CYL':   (retDict['LBA']>> 8) & 0xFFFF,
            'HEAD':  retDict['LBA'] >> 24,
            'SCTR': retDict['LBA'] & 0xFF,
         })
      return retDict


   #-------------------------------------------------------------------------------------------------------
   def overridePrmCall(self, STARTING_LBA, MAXIMUM_LBA, STEP_LBA = None, BLKS_PER_XFR = 256, \
                          STAMP_FLAG = 0, COMPARE_FLAG = 0, LOOP_COUNT = 1, DATA_PATTERN0 = 0, timeout = 252000, exc = 1):


      tempPrm = dict(getattr(self.params, self.prmName)) #create a copy

      #TODO: Add compare flag handling
      wordPattern = wordTuple(DATA_PATTERN0)
      totalBlocksXfr = LOOP_COUNT * (MAXIMUM_LBA - STARTING_LBA + 1 )

      if testSwitch.BF_0142561_231166_P_FIX_STEP_LBA_SAS:
         if STEP_LBA != None:
            # Need to reduce the total number of lba's by the sample rate
            totalBlocksXfr = (totalBlocksXfr*BLKS_PER_XFR)/STEP_LBA
            tempPrm['STEP_SIZE'] = lbaTuple(STEP_LBA)
      else:
         if STEP_LBA == None:
            STEP_LBA = 256

      tempPrm.update({
               'timeout' : timeout,
               'START_LBA34' : lbaTuple(STARTING_LBA) ,
               'NUMBER_LBA_PER_XFER' : wordTuple(BLKS_PER_XFR),
               'PATTERN_LSW': wordPattern[1],
               'PATTERN_MSW': wordPattern[0],
               'TOTAL_LBA_TO_XFER': lbaTuple(totalBlocksXfr),
               })
      if LOOP_COUNT > 1:
         tempPrm['END_LBA34'] = lbaTuple(MAXIMUM_LBA)

      if self.ovrPrms:
         tempPrm.update(self.ovrPrms)

      #tempPrm['MAXIMUM_LBA'] = lbaTuple(MAXIMUM_LBA)


      #if not tempPrm['test_num'] in [508, 514, 533, 528, 535]:
      #   self.HardReset()

      ret = self.St(tempPrm)
      self.ovrPrms = {}
      ret = self.translateStReturnToCPC(ret)

      return ret



   def FillBuffer(self, buffFlag , byteOffset, data):
      tempPrm = dict(self.params.WritePatternToBuffer) #create a copy
      if type(data) == type(''):
         data = int(binascii.hexlify(data),16)

      Pattern = wordTuple(data & 0xFFFFFFFFFFFFFFFF)
      tempPrm['PARAMETER_5'] = Pattern[0]
      tempPrm['PARAMETER_6'] = Pattern[1]

      tempPrm['PARAMETER_4'] = 0xFF80


      if buffFlag & WBF:
         tempPrm['PARAMETER_1'] = (0xFF00,)
         tempPrm['prm_name'] = 'Write 00 Pattern to Write Buffer'
         status = self.St(tempPrm)
      if buffFlag & RBF:
         tempPrm['PARAMETER_1'] = (0xFF01,)
         tempPrm['prm_name'] = 'Write 00 Pattern to Read Buffer'
         status = self.St(tempPrm)

      return self.translateStReturnToCPC(status)

   def FillBuffInc(self, buffFlag):
      tempPrm = dict(self.params.WriteInternalPatternToBuffer) #create a copy
      tempPrm['PARAMETER_4'] = 0x0002
      if buffFlag & WBF:
         tempPrm['PARAMETER_1'] = 0x0000
         tempPrm['prm_name'] = 'Write Incremental Pattern to Write Buffer'
         status = self.St(tempPrm)
      if buffFlag & RBF:
         tempPrm['PARAMETER_1'] = 0x0001
         tempPrm['prm_name'] = 'Write Incremental Pattern to Read Buffer'
         status = self.St(tempPrm)

      return self.translateStReturnToCPC(status)

   def FillBuffRandom(self, buffFlag ):
      tempPrm = dict(self.params.WritePatternToBuffer) #create a copy
      tempPrm['PARAMETER_4']  = 0x0001
      tempPrm['PARAMETER_5']  = 0x2C2C
      if buffFlag & WBF:
         tempPrm['PARAMETER_1'] = 0x0000
         tempPrm['prm_name'] = 'Write Random Pattern to Write Buffer'
         status = self.St(tempPrm)
      if buffFlag & RBF:
         tempPrm['PARAMETER_1'] = 0x0001
         tempPrm['prm_name'] = 'Write Random Pattern to Read Buffer'
         status = self.St(tempPrm)

      return self.translateStReturnToCPC(status)

   def RandomSeekTime(self,min_LBA, max_LBA, numSeeks, seekType = 28 , timeout= 3600, exc=0):
      tempPrm = dict(self.params.prm_549_RdmWrtSeek) #create a copy
      import serialScreen
      oSerial = serialScreen.sptDiagCmds()
      oSerial.enableDiags()

      data = oSerial.translateLBA(int(min_LBA))
      start_cyl=data['PHYSICAL_CYL']
      start_head =data['LOGICAL_HEAD']
      data = oSerial.translateLBA(int(max_LBA))
      end_cyl=data['PHYSICAL_CYL']
      end_head =data['LOGICAL_HEAD']

      head = start_head
      if start_cyl > end_cyl:
         temp_cyl  = end_cyl
         end_cyl   = start_cyl
         start_cyl = temp_cyl
         head = end_head


      param_head_mask = tempPrm['MAXIMUM_ERROR_COUNT'] & 0xE0FF
      param_head = 0x1F00 & int(head << 8)
      param_head = param_head | param_head_mask
      try:
         self.UnlockFactoryCmds()
      except:
         self.objPwrCtrl.powerCycle(offTime=20, onTime=35, ataReadyCheck = True)
      tempPrm['timeout']       = timeout
      tempPrm['START_CYL']     = wordTuple(start_cyl)
      tempPrm['END_CYL']       = wordTuple(end_cyl)
      tempPrm['SEEK_COUNT']    = numSeeks
      tempPrm['MAXIMUM_ERROR_COUNT']    = param_head
      tempPrm['HEAD_SELECTION']          = 0
      #tempPrm['stSuppressResults'] = ST_SUPPRESS__ALL | ST_SUPPRESS_RECOVER_LOG_ON_FAILURE
      self.St(self.params.prm_507_549)
      if exc ==0:
         status = self.St(tempPrm)
      else:
         try:
            status = self.St(tempPrm)
         except:
            pass
            return

      return self.translateStReturnToCPC(status)

   def RandomSeekTimeCyl(self,min_CYL, max_CYL, numSeeks, timeout= 3600, exc=0):

      tempPrm = dict(self.params.prm_549_RdmWrtSeek)     # Create a copy
      tempPrm['prm_name']              = 'prm_549_RdmWrtSeekCyl'
      tempPrm['timeout']               = timeout
      tempPrm['START_CYL']             = wordTuple(min_CYL)
      tempPrm['END_CYL']               = wordTuple(max_CYL)
      tempPrm['SEEK_COUNT']            = numSeeks
      tempPrm['MAXIMUM_ERROR_COUNT']   = 0x4500
      tempPrm['HEAD_SELECTION']        = 0

      self.objPwrCtrl.powerCycle(offTime=20, onTime=35, ataReadyCheck = True)
      self.St(self.params.prm_507_549)

      if exc ==0:
         status = self.St(tempPrm)
      else:
         try:
            status = self.St(tempPrm)
         except:
            return
      return self.translateStReturnToCPC(status)

   def WriteSectors(self, start_LBA, num_LBAs):
      """Write sectors to Disk."""
      maxLBA = start_LBA + num_LBAs
      result = self.SequentialWriteDMAExt(start_LBA, maxLBA)

      return result

   def ReadSectors(self, start_LBA, num_LBAs):
      """Read Sectors from Disk"""

      maxLBA = start_LBA + num_LBAs
      result = self.SequentialReadDMAExt(start_LBA, maxLBA)

      return result

   def BufferCopy(self, destBuffFlag, destOffset, srcBuffFlag, srcOffset, byteCount):
      tempPrm = dict(self.params.BufferCopy) #create a copy

      if destBuffFlag == WBF and srcBuffFlag == RBF:
         tempPrm['PARAMETER_1'] = 0x6 #Copy READ buffer to WRITE buffer
         tempPrm['PARAMETER_3'] = byteCount
         tempPrm['PARAMETER_2'] = destOffset

      if destBuffFlag == RBF and srcBuffFlag == WBF:
         tempPrm['PARAMETER_1'] = 0x7 #Copy WRITE buffer to READ buffer
         tempPrm['PARAMETER_3'] = byteCount
         tempPrm['PARAMETER_2'] = destOffset

      ret = self.St(tempPrm)
      return PASS_RETURN

   def DriveOperationSimulation(self, readWeight, writeWeight, seekWeight, numWrites, numLBAs):
      tempPrm = dict(self.params.SimulateWorkLoadSIOP) #create a copy
      param_head_mask = tempPrm['RW_CMD_WEIGHT'] & 0x00F0
      read_w  = 0xF000 & int(readWeight  << 12)
      write_w = 0x0F00 & int(writeWeight << 8)
      seek_w  = 0x000F & int(seekWeight)
      tempPrm['RW_CMD_WEIGHT'] = read_w | write_w | seek_w | param_head_mask
      tempPrm['TEST_PASS_COUNT'] = numWrites
      tempPrm['MAX_BLOCK_PER_CMD'] = numLBAs
      status = self.St(tempPrm)
      return self.translateStReturnToCPC(status)

   if testSwitch.BF_0150521_231166_P_RAW_SAS_MODEL_QUERY:
      def GetModelNum(self, useVendorField = False):
         self.St(self.params.prm_538_StandardInquiry)
         ret = self.GetBuffer(RBF)
         buffData = ret['DATA']

         if useVendorField:
            # Neeed "SEAGATE "
            return buffData[8:32]
         else:
            return buffData[16:32]
   else:
      def GetModelNum(self, useVendorField = False):

         queryPrm =  self.params.IdentifyDevice.copy()

         queryPrm['PAGE_CODE'] = 0 #0xC3
         queryPrm['DblTablesToParse']= ['P514_STANDARD_INQUIRY',]

         self.St(queryPrm)
         if testSwitch.BF_0143925_231166_P_FIX_SAS_CUST_MOD_VENDOR_FIELD:
            if not testSwitch.virtualRun:
               vend = self.dut.objSeq.SuprsDblObject['P514_STANDARD_INQUIRY'][-1]['VENDOR_ID']
               prod = self.dut.objSeq.SuprsDblObject['P514_STANDARD_INQUIRY'][-1]['PRODUCT_ID']

            else:
               vend = 'SEAGATE_'
               prod='ST33000650SS____'

            if testSwitch.FE_0144401_231166_P_SUPPORT_VEND_CMD_SEP:
               if useVendorField:
                  ret = vend+prod
               else:
                  ret = prod
            else:
               ret = vend+prod

            ret = ret.replace('_', ' ').rstrip()

         else:
            if not testSwitch.virtualRun:
               ret = self.dut.objSeq.SuprsDblObject['P514_STANDARD_INQUIRY'][-1]['PRODUCT_ID']
            else:
               ret = ''

            if testSwitch.BF_0142538_231166_P_FIX_UNDERBAR_MODEL_SAS:
               ret = ret.rstrip('_')

         return ret

   if testSwitch.FE_0142983_357552_ADD_SECTSIZE_TO_ICMD:
      def GetMaxLBA(self):
         from TCG import LifeStates
         if getattr(dut, 'LifeState', LifeStates['INVALID']) in [LifeStates['USE'], ]:
            return { 'LLRET': OK,
                     'MAX48': "%X" % self.maxlba,
                     'MAX28': "%X" % (self.maxlba & 0xFFFFFFF),
                   }

         sixteenByteSupport = True
         if self.maxlba == 0:

            try:
               if sixteenByteSupport:
                  self.St(self.params.GetMaxLBA)
               else:
                  self.St(self.params.GetMaxLBA_non16)
            except:
               if testSwitch.WA_0145880_231166_P_FIX_INIT_HANG_BDG_DL:
                  objMsg.printMsg("GetMaxLBA retreival failed: bypassing for now\n%s" % (traceback.format_exc(),))

                  self.objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = False)  #Do spinup, sense, etc.
                  self.maxlba = 0

                  return { 'LLRET': OK,
                     'MAX48': "%X" % self.maxlba,
                     'MAX28': "%X" % (self.maxlba & 0xFFFFFFF),
                   }
               else:
                  raise

            ret = ''
            if not testSwitch.virtualRun:
               for row in self.dut.objSeq.SuprsDblObject['P000_BUFFER_DATA']:
                  ret += row['*']
            else:
               if sixteenByteSupport:
                  ret = '01'+ '0'*18 + '0200'
               else:
                  ret = {'*':'\x01\x00\x00\x00\x00\x02\x00'}

            if sixteenByteSupport:
               maxlba = ret[0:20]
               maxlba = CUtility.strBufferToBinString(maxlba) #convert bin buffer to bin str
               maxlba = struct.unpack('>Q', maxlba[:struct.calcsize('Q')])[0] #now extract the lba

               sectSize = ret[20:24]
               sectSize = CUtility.strBufferToBinString(sectSize) #convert bin buffer to bin str
               sectSize = struct.unpack('>H', sectSize[:struct.calcsize('H')])[0] #now extract the sectSize

               if DEBUG:
                  objMsg.printMsg("setting maxlba to %X" % maxlba)
                  objMsg.printMsg("setting sector size to %d" % sectSize)

            else:
               maxlba = CUtility.numSwap(ret['*'][0:5])
               sectSize = CUtility.numSwap(ret['*'][5:7])

            self.maxlba = maxlba
            self.sectSize = sectSize

            if testSwitch.BF_0142777_231166_P_ADJ_MAX_SAS_LBA_FOR_COUNT:
               # SAS returns the max lba not the count with this command but the caller API is setup to mimic SATA
               #  and sata returns the count in id device so we need to mimic that API at the script level for commonality
               self.maxlba += 1

         return { 'LLRET': OK,
                  'MAX48': "%X" % self.maxlba,
                  'MAX28': "%X" % (self.maxlba & 0xFFFFFFF),
                }

   else:
      def GetMaxLBA(self):
         from TCG import LifeStates
         if getattr(dut, 'LifeState', LifeStates['INVALID']) in [LifeStates['USE'], ]:
            return { 'LLRET': OK,
                     'MAX48': "%X" % self.maxlba,
                     'MAX28': "%X" % (self.maxlba & 0xFFFFFFF),
                   }

         sixteenByteSupport = True
         if self.maxlba == 0:

            if sixteenByteSupport:
               self.St(self.params.GetMaxLBA)
            else:
               self.St(self.params.GetMaxLBA_non16)

            ret = ''
            if not testSwitch.virtualRun:
               for row in self.dut.objSeq.SuprsDblObject['P000_BUFFER_DATA']:
                  ret += row['*']
            else:
               if sixteenByteSupport:
                  ret = '01'+ '00'*20
               else:
                  ret = {'*':'\x01\x00\x00\x00\x00'}

            if sixteenByteSupport:
               maxlba = ret[0:20]
               maxlba = CUtility.strBufferToBinString(maxlba) #convert bin buffer to bin str

               maxlba = struct.unpack('>Q', maxlba[:struct.calcsize('Q')])[0] #now extract the lba
               if DEBUG:
                  objMsg.printMsg("setting maxlba to %X" % maxlba)
            else:
               maxlba = CUtility.numSwap(ret['*'][0:4])

            self.maxlba = maxlba

            if testSwitch.BF_0142777_231166_P_ADJ_MAX_SAS_LBA_FOR_COUNT:
               # SAS returns the max lba not the count with this command but the caller API is setup to mimic SATA
               #  and sata returns the count in id device so we need to mimic that API at the script level for commonality
               self.maxlba += 1

         return { 'LLRET': OK,
                  'MAX48': "%X" % self.maxlba,
                  'MAX28': "%X" % (self.maxlba & 0xFFFFFFF),
                }


   def SmartReturnStatus(self):

      self.St(self.params.SmartReturnStatus)
      if not testSwitch.virtualRun:
         if testSwitch.BF_0173040_470833_P_FIX_SAS_SIC_T518_HEADER_ISSUES:
            try:
               ret = self.dut.objSeq.SuprsDblObject['P518_MODE_SENSE_HEADER'][0].copy()
               data = CUtility.strBufferToBinString(ret['*'])
            except:
               ret = self.dut.objSeq.SuprsDblObject['P000_MODE_SENSE_HEADER'][0].copy()
               data = CUtility.strBufferToBinString(ret['*'][8:]) # P000 table includes "Header_:" before actual hex values
         else:
            ret = self.dut.objSeq.SuprsDblObject['P518_MODE_SENSE_HEADER'][0].copy()
            data = CUtility.strBufferToBinString(ret['*'])
      else:
         ret = PASS_RETURN
         data = '\x00\x00\x00\x00'



      fmt = 'BBBB'

      key, code, qual, fru = struct.unpack(fmt, data[0:struct.calcsize(fmt)] )

      if key == 1 and code == 0x5D:
         fru_description = { 0x04:"LBA Reassignment Exceeding Limits",
                             0x10:"Hardware/Medium Errors Exceeding Limits",
                             0x14:"Excessive Reassigns Exceeding limits",
                             0x16:"Servo Start Time Exceeding Limits",
                             0x31:"HDI Errors Exceeding Limits",
                             0x32:"Read Data Errors Exceeding Limits",
                             0x42:"Write Error Rate Exceeding Limits",
                             0x43:"Seek Error Rate Exceeding Limits",
                             0x5B:"Spin-up Retry Count Exceeding Limits",
                             0x75:"Bi-Variate Read-Seek Errors Exceeding Limits",
                           }
         ScrCmds.raiseException(13455, "Drive returned SMART threshold failure: FRU: %X = %s" % (fru, fru_description.get(fru, "Unknown FRU")))
      else:
         objMsg.printMsg("SMART status passed")

      return {'LLRET':OK, 'LBA' : 0xc24f00}


   def GetBuffer(self, Mode, ByteOffset = 0, BuffSize = 512):
      """
      Retreive buffer from drive
      """

      if self.tempBuffer: #other command provided buffer

         tBuff = self.tempBuffer
         self.tempBuffer = False #clear out tempbuffer

         return {'LLRET':OK, 'DATA': tBuff}

      tempPrm = dict(self.params.DisplayBufferData) #create a copy

      if Mode == RBF:
         buffVal = 5
      elif Mode == WBF:
         buffVal = 4


      uNibBytesRead = (BuffSize & 0xF0000)>>16
      lBytesRead =    (BuffSize & 0x0FFFF)

      uBitsByteOffset = (ByteOffset & 0xFF0000) >> 16

      tempPrm['PARAMETER_1'] = (uNibBytesRead<<8) + buffVal
      tempPrm['PARAMETER_2'] = 0xFFFF & ByteOffset
      tempPrm['PARAMETER_3'] = lBytesRead
      tempPrm['PARAMETER_4'] = uBitsByteOffset

      self.St(tempPrm)

      if not testSwitch.virtualRun:
         if testSwitch.FE_0142909_231166_P_SUPPORT_SAS_DRV_MODEL_NUM and 'P508_BUFFER' in self.dut.objSeq.SuprsDblObject:
            # format is different
            ret = self.dut.objSeq.SuprsDblObject['P508_BUFFER']
            data = initCmd.extractBufferDblog(self, ret)
         else:
            ret = self.dut.objSeq.SuprsDblObject['P000_BUFFER_DATA'][0].copy()
            data = self.extractBufferDblog(ret)
      else:
         data = ''


      return {'LLRET':OK, 'DATA':data}



   def SmartReadLogSec(self, smartSector, numSectors):
      self.St(self.params.UnlockFactoryCmds)
      inputSize = 512 * numSectors

#     self.St(self.params.SmartReadLogSecSize)
#     data = self.dut.objSeq.SuprsDblObject['P000_BUFFER_DATA'][0].copy()
#
#
#
#     objMsg.printMsg("User input %X size" % inputSize)
#     frameSize = CUtility.strBufferToBinString(data['*'][0:8])
#     frameSize = struct.unpack('<L', frameSize)[0]
#
#     maxSize = CUtility.strBufferToBinString(data['*'][8:16])
#     maxSize = struct.unpack('<L', maxSize)[0]
      maxSize = 0xFF

      if inputSize > maxSize:
         inputSize = maxSize

#     if not inputSize % frameSize == 0:
#        inputSize = (inputSize / frameSize) * frameSize
#        if inputSize == 0:
#           inputSize = frameSize


#     objMsg.printMsg("Debug: %s" % (data['*'],))
#     objMsg.printMsg("Debug: %s" % (data['*'][8:16],))
#     objMsg.printMsg("DebugframeSize: %X" % (frameSize,))

      objMsg.printMsg("DebuginputSize: %X" % (inputSize,))
      objMsg.printMsg("DebugmaxSize: %X" % (maxSize,))



      modPrm = self.params.SmartReadLogSec.copy()

      #inputSize += 4 # Add the dsb header size 2x uint16

      #Have to swap the bytes as a word to send to the drive
      #alloc1, alloc2 = struct.unpack('HH', struct.pack('<L',inputSize))

      modPrm['TRANSFER_LENGTH']= inputSize
      modPrm['PARAMETER_2']= struct.unpack('>H',struct.pack('BB', 0x35, inputSize)) #smart log 0x35/ transfer length
      #modPrm['PARAMETER_6'] = alloc1
      #modPrm['PARAMETER_7'] = alloc2


      stat = self.St(modPrm)
      if not testSwitch.virtualRun:
         ret = self.dut.objSeq.SuprsDblObject['P000_BUFFER_DATA']
         self.tempBuffer = self.extractBufferDblog(ret)
      else:
         self.tempBuffer = ''

      return self.translateStReturnToCPC(stat)

   def extractBufferDblog(self, buffDict):

      data = ''

      for row in buffDict:
         try:
            data += CUtility.strBufferToBinString(row['*'])
         except:
            objMsg.printMsg("Error: data:'%s' ; val: '%s', key: '%s'" % (data, row['*'], '*'))
            raise

      return data


   if testSwitch.FE_0134083_231166_UPDATE_SMART_AND_UDS_INIT:
      def ClearSmart(self):
         """
         Initialize the smart sectors and perform basic head amplitude measurements for SAS SMART req.
         """
         if testSwitch.FE_0166634_231166_SAS_SMART_FH_TRACK_INIT:
            self.UnlockFactoryCmds()
         self.St(self.params.ClearSmart)
         self.St(self.params.ClearSmartPredictiveCounters)
         self.St(self.params.InitSmartHeadAmp)
         if testSwitch.FE_0166634_231166_SAS_SMART_FH_TRACK_INIT:
            self.St(self.params.InitAltTone)


      def ClearUDS(self):
         """
         Clears the UDS counters
         """
         objMsg.printMsg("Clear UDS")
         self.ClearBinBuff()
         # Load Write Buffer to clear UDS
         self.St({'test_num':508,'prm_name':'Clear UDS 01',
                  'PARAMETER_1': 0x0002,
                  'PARAMETER_2': 0x0000,
                  'PARAMETER_3': 0x00FF,
                  'PARAMETER_4': 0x0000,
                  'PARAMETER_5': 0x0000,
                  'PARAMETER_6': 0x0000,
                  'PARAMETER_7': 0x0600,
                  'PARAMETER_8': 0x0600,
                  'PARAMETER_9': 0x0800,
                  'PARAMETER_10': 0x0000,
                  'timeout'    : 600
                  })
         # Load Write Buffer to clear UDS
         self.St({'test_num':508,'prm_name':'Clear UDS 02',
                  'PARAMETER_1': 0x0002,
                  'PARAMETER_2': 0x0008,
                  'PARAMETER_3': 0x00FF,
                  'PARAMETER_4': 0x0000,
                  'PARAMETER_5': 0x0000,
                  'PARAMETER_6': 0x0000,
                  'PARAMETER_7': 0x0800,
                  'PARAMETER_8': 0x0100,
                  'PARAMETER_9': 0x0119,
                  'PARAMETER_10':0x0906,
                  'timeout'    : 600
                  })
         # Display Write Buffer
         self.St({'test_num':508,'prm_name':'SMART Display Write Buffer',
            'PARAMETER_1': 0x0004,
            'PARAMETER_2': 0x0000,
            'PARAMETER_3': 0x0020,
            'PARAMETER_4': 0x0000,
            'PARAMETER_5': 0x0000,
            'PARAMETER_6': 0x0000,
            'PARAMETER_7': 0x0000,
            'PARAMETER_8': 0x0000,
            'PARAMETER_9': 0x0000,
            'PARAMETER_10': 0x0000,
            'timeout'    : 600
            })

         # Unlock for Platform
         self.UnlockFactoryCmds()

         # Set Buffer sizes to maximum
         self.St({'test_num':599,'prm_name':'Set Max Buffer',
            'PARAMETER_1': 0x0006,
            'PARAMETER_2': 0x0000,
            'PARAMETER_3': 0x0000,
            'PARAMETER_4': 0x0000,
            'PARAMETER_5': 0x0000,
            'PARAMETER_6': 0x0000,
            'PARAMETER_7': 0x0000,
            'PARAMETER_8': 0x0000,
            'PARAMETER_9': 0x0000,
            'PARAMETER_10': 0x0000,
            'timeout'    : 600
            })
         # Manually issue Send Factory Command
         self.St({'test_num':599,'prm_name':'Send Factory Command',
            'PARAMETER_1': 0x0001,
            'PARAMETER_2': 0xE000,
            'PARAMETER_3': 0x0000,
            'PARAMETER_4': 0x1000,
            'PARAMETER_5': 0x2459,
            'PARAMETER_6': 0x0000,
            'PARAMETER_7': 0x0200,
            'PARAMETER_8': 0x0000,
            'PARAMETER_9': 0x0000,
            'PARAMETER_10': 0x0000,
            'timeout'    : 600
            })
         # Manually issue Receive Factory Command
         self.St({'test_num':599,'prm_name':'Receive Factory Command',
            'PARAMETER_1': 0x0001,
            'PARAMETER_2': 0xE100,
            'PARAMETER_3': 0x0000,
            'PARAMETER_4': 0x2800,
            'PARAMETER_5': 0x2459,
            'PARAMETER_6': 0x0000,
            'PARAMETER_7': 0x0200,
            'PARAMETER_8': 0x0000,
            'PARAMETER_9': 0x0000,
            'PARAMETER_10': 0x0000,
            'timeout'    : 600
            })

         objMsg.printMsg("Verify UDS Power Cycle count has been cleared")

         self.St({'test_num':638,'prm_name':'Get SMART SRAM Frame',
            'TEST_FUNCTION' : (0x0000,),
            'WRITE_SECTOR_CMD_ALL_HDS' : (0x0000,),
            'SCSI_COMMAND' : (0x0000,),
            'LONG_COMMAND' : (0x0000,),
            'ATTRIBUTE_MODE' : (0x0000,),
            'REPORT_OPTION' : (0x0001,),
            'BYPASS_WAIT_UNIT_RDY' : (0x0000,),
            'PARAMETER_0' : (0x5201,),
            'PARAMETER_1' : (0x0100,),
            'PARAMETER_2' : (0x0300,),
            'PARAMETER_3' : (0x0000,),
            'PARAMETER_4' : (0x0000,),
            'PARAMETER_5' : (0x0000,),
            'PARAMETER_6' : (0x0000,),
            'PARAMETER_7' : (0x0000,),
            'PARAMETER_8' : (0x0000,),
            'timeout':600,
            })

         self.St({'test_num':508,'prm_name':'Verify value of 2 or less for bytes 8,9 (UDS Power Cycle Count)',
            'PARAMETER_1': 0x0009,
            'PARAMETER_2': 0x0008,
            'PARAMETER_3': 0x0002,
            'PARAMETER_4': 0x0000,
            'PARAMETER_5': 0x0000,
            'PARAMETER_6': 0x0000,
            'PARAMETER_7': 0x0000,
            'PARAMETER_8': 0x0002,
            'PARAMETER_9': 0x0000,
            'PARAMETER_10': 0x0000,
            'timeout'    :600
            })


   def Seek(self, lba, exc = 1):

      prm = self.params.Seek.copy()
      lbaWords = struct.unpack('>HHHH', struct.pack('Q',lba))
      #lbaWords = CUtility.returnStartLbaWords( lba )
      objMsg.printMsg('LBA WORDS:')
      objMsg.printMsg(lba)
      objMsg.printMsg(lbaWords)
      prm['PARAMETER_2'] = lbaWords[0]
      prm['PARAMETER_3'] = lbaWords[1]
      prm['PARAMETER_4'] = lbaWords[2]
      prm['PARAMETER_5'] = lbaWords[3]

      prm['stSuppressResults'] = ST_SUPPRESS__ALL

      try:
         ret = self.St(prm)
      except:
         self.objPwrCtrl.powerCycle(offTime=20, onTime=35, ataReadyCheck = True)
         ret = self.St(prm)
      if exc:
         return {'LLRET': OK}
      else:
         return self.translateStReturnToCPC(ret)

   def WriteFinalAssemblyDate(self, weekstr):
      param4 = (ord(weekstr[0]) << 8) | (ord(weekstr[1]))
      param5 = (ord(weekstr[2]) << 8) | (ord(weekstr[3]))
      DriveAttributes["FINAL_ASSY_DATE"]= weekstr
      prm = self.params.WriteFinalAssemblyDate.copy()
      prm["CURRENT_MONTH_YEAR"] = param4
      prm["CURRENT_DAY_WEEK"] = param5

      self.St(prm,TEST_FUNCTION=(0))  # Write Final assembly date
      self.St(prm,TEST_FUNCTION=(1))  # Read  Final assembly date
      self.St(prm,TEST_FUNCTION=(2))  # Compare Final assembly date


   def getTest638Data(self):
      """After executing Test 638, this function uses BYTES field returned by 638
         to read that much from read buffer"""
      if not testSwitch.virtualRun:
         bytesRead = int(self.dut.objSeq.SuprsDblObject['P638_INCOMING_DATA_SIZE'][-1]['BYTES'],16)
      else:
         bytesRead = 1024

      tempPrm = self.params.DisplayRdBuffer.copy() #T508 to read initiator read buffer
      tempPrm.update({'PARAMETER_3' : bytesRead})
      self.St(tempPrm)

      return ''  #Placeholder for future improvement - actually pass back data read

   def resetCustomerConfiguration(self):
      self.St(self.params.CurrentFwOptionsSettings)
      objMsg.printMsg("Resetting Mode Pages values to default")

      if testSwitch.FE_0149739_357552_P_FMT_PI_SKIP_MP3_RESET:
         tempPrm = self.params.WrtDefaultFwOptions.copy()
         #Make sure dict defined in PIF, and partNum defined
         import PIF
         if hasattr(PIF,'ProtInfoTypeDict') and PIF.ProtInfoTypeDict.has_key(self.dut.partNum):
            #Bypass setting mode page 3 back to default if drive formatted with PI. This is because
            #  format with PI changes sector size in mode page 3 to add PI bytes. This may not be
            #  default, and for some customers (IBM) who have STRICT bit set, T537 will fail, since
            #  trying to reset a non-changeable field.
            tempPrm.update({'MODE_COMMAND':(0x0002,), 'MODE_PAGES_BYPASSED_1':(0x0003,)})

         self.St(tempPrm)
      else:
         self.St(self.params.WrtDefaultFwOptions) # requisite test calls

      if testSwitch.WA_0135289_357552_DSENSE_BIT_NOT_DEFAULT_ON_34_BIT_LBA:
         #D_Sense in Control Mode Page required to be set on 34-LBA space.
         # Use PowerControl spinup commands to set it. FULL power cycle (drive
         # and initiator) is required.
         self.objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = True)  #Do spinup, sense, etc.

      self.St(self.params.CurrentFwOptionsSettings)
   
   if testSwitch.BF_0173040_470833_P_FIX_SAS_SIC_T518_HEADER_ISSUES:
      def getModePageData(self, pageNo):
         self.St(self.params.getModePages)
         retStruct = { 'data': '',
                       'page': 0,
                       'length': 0,
                       }
   
         if testSwitch.virtualRun:
            pages = [{'*': '00810AC814FF00000005002710'}]
            headerIDSize = 2 # example: 00
         else:
            try:
               pages = self.dut.objSeq.SuprsDblObject['P518_MODE_PAGE_DATA']
               objMsg.printMsg("518 data: %s"%pages)
               headerIDSize = 2 # example: 00
            except:
               pages = self.dut.objSeq.SuprsDblObject['P000_MODE_PAGE_DATA']
               objMsg.printMsg("000 data: %s"%pages)
               headerIDSize = 8 #example: Page_01:
         index = 0 #used to grab additional page data, if needed
         for page in pages:
            headerID = page['*'][:headerIDSize]
            if not (headerID == '________' or headerID == '01'): # underscores or '01' indicates the line is additional data for the previous page number
               pageNum = int(page['*'][headerIDSize:headerIDSize+2],16) #grab the page number (first two characters, hex)
               length = int(page['*'][headerIDSize+2:headerIDSize+4],16) #grab the length (second two characters, hex)
               data = page['*'][headerIDSize+4:] #remainder is the data
               if length > 0x30: # if length is over 0x30, data appears on two lines and must be combined
                  additionalData = pages[index+1]
                  data += additionalData['*'][headerIDSize+4:]
               pageData = CUtility.strBufferToBinString(data)
               if pageNum == pageNo:
                  retStruct = { 'data': pageData, #need to grab data correctly if on multiple lines of output
                                'page': pageNum,
                                'length': length,
                              }
                  break
            index += 1
         return retStruct
   else:
      def getModePageData(self, pageNo):
         self.St(self.params.getModePages)
         retStruct = { 'data': '',
                       'page': 0,
                       'length': 0,
                       }
   
         if testSwitch.virtualRun:
            pages = [{'*': '00810AC814FF00000005002710'}]
         else:
            pages = self.dut.objSeq.SuprsDblObject['P518_MODE_PAGE_DATA']
         for page in pages:
            data = CUtility.strBufferToBinString(page['*'])
   
            headerFormat = 'BB'
            id_byte = data[0]
            data = data[1:]
            header = data[:struct.calcsize(headerFormat)]
            pageData = data[struct.calcsize(headerFormat):]
            pageNum, length = struct.unpack(headerFormat, header)
            if pageNum == pageNo:
               retStruct = { 'data': pageData,
                             'page': pageNum,
                             'length': length,
                             }
         return retStruct

   def setSectorSize(self, sectorSize=512):
      """Write sector size to mode page block descriptor."""
      param6 = (sectorSize >> 8) | 0x0E00
      param7 = (sectorSize & 0x00ff) | 0x0F00
      PageData=(0x00FF,0x01FF,0x02FF,0x03FF,0x04FF,0x05FF,0x06FF,0x07FF,0x08FF,0x09FF,0x0A00,0x0B00,0x0C00,0x0D00,param6,param7,)

      tmpPrm = self.params.setShippingSectorSize.copy()
      tmpPrm.update({'PAGE_BYTE_AND_DATA34' : PageData})
      self.St(tmpPrm)

   if testSwitch.FE_0141083_357552_PI_FORMAT_SUPPORT:
      def runInitiatorFormat(self, fmtPInfo=0, rtoREQ=0):
         """Run format on initiator card. Both params=0 means normal (non-PI) format."""
         self.St(self.params.prm_506_FormatTimeout)

         tempPrm = self.params.prm_511_SAS_Format.copy()
         tempPrm.update({'FMT_P_INFO' : fmtPInfo, 'RTO_REQ' : rtoREQ})

         self.St(tempPrm)

   else:
      def runInitiatorFormat(self):
         """Run format on initiator card"""
         self.St(self.params.prm_506_FormatTimeout)
         self.St(self.params.prm_511_SAS_Format)

   def spinUpDrive(self):
      SetFailSafe()
      try:
         self.St(self.params.spinup_517)  #clear sense
         self.St(self.params.prm_517_RequestSense5)
      finally:
         ClearFailSafe()

   def clearLogPages(self):
      """Display, then clear log pages on SAS"""
      self.St(self.params.prm_503_LogPage_2)
      self.St(self.params.prm_503_LogPage_3)
      self.St(self.params.prm_503_LogPage_6)
      self.St(self.params.prm_503_LogPage_3E)
      self.St(self.params.prm_503_LogPage_3E_Spec1)
      self.St(self.params.prm_503_LogPage_2_Spec2)
      self.St(self.params.prm_503_ClrLogPg6)
      self.St(self.params.prm_503_ClrLogPg3A)
      self.St(self.params.prm_503_ClrLogPgs)

   def scsiChangeDef(self, inPrms={}):
      """Issue SCSI Change Definition Command."""
      self.UnlockFactoryCmds()
      tmpPrm = self.params.prm_538_ChangeDefCMD.copy()
      tmpPrm.update(inPrms)
      self.St(tmpPrm)

   def disableBGMS(self):
      """Disable Prescan and BGMS"""
      try:
         self.St(self.params.prm_518_Disable_PrescanBGMS)
      except:
         prm_518_Disable_PrescanBGMS_HP = self.params.prm_518_Disable_PrescanBGMS.copy()
         prm_518_Disable_PrescanBGMS_HP.update({
            'prm_name' : 'prm_518_Disable_PrescanBGMS_HP',
            'PAGE_BYTE_AND_DATA34' : (0x0004,0x0002,0x0005,0x0000,0x0006,0x00FF,0x0007,0x00FF,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,),
            })
         self.St(prm_518_Disable_PrescanBGMS_HP)

   def disable_WriteCache(self, exc = 1):
      # Disable Write Cache
      prm = self.params.WriteCache_Prm.copy()
      prm['prm_name']               = 'Disable Write Cache'
      prm["PAGE_BYTE_AND_DATA34"]   = (0x0220,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,)
      return self.St(prm)

   def enable_WriteCache(self, exc = 1):
      # Enable Write Cache
      prm = self.params.WriteCache_Prm.copy()
      prm['prm_name']               = 'Enable Write Cache'
      prm["PAGE_BYTE_AND_DATA34"]   = (0x0221,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,)
      return self.St(prm)

   def disable_LA_CHECK(self, exc = 1):
      # Disable LA_Check (Hitachi Mode)
      prm = self.params.WriteCache_Prm.copy()
      prm['prm_name']               = 'Disable LA Check'
      prm['PAGE_CODE']              = 0x38
      prm["SAVE_MODE_PARAMETERS"]   = 0x0001
      prm['MODE_SENSE_OPTION']      = 3      # Read back saved values
      prm["PAGE_BYTE_AND_DATA34"]   = (0x1401,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,)
      return self.St(prm)

   def enable_LA_CHECK(self, exc = 1):
      # Enable LA_Check (Hitachi Mode)
      prm = self.params.WriteCache_Prm.copy()
      prm['prm_name']               = 'Enable LA Check'
      prm['PAGE_CODE']              = 0x38
      prm["SAVE_MODE_PARAMETERS"]   = 0x0001
      prm['MODE_SENSE_OPTION']      = 3      # Read back saved values
      prm["PAGE_BYTE_AND_DATA34"]   = (0x1400,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,)
      return self.St(prm)

   def setMaxXferRate(self):

      speedLookup = [(4, 6), #6.0Gbs
                     (2, 3), #3.0Gbs
                     (1, 1.5), #1.5Gbs
                     ]

      rate = self.base_setMaxXferRate(speedLookup)

      if rate == None:
         self.objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = False)  #Do spinup, sense, etc.
         #self.powerOff(offTime = 10,  driveOnly = 0)
         #self.powerOn(set5V=5000, set12V=12000, onTime=10, baudRate=PROCESS_HDA_BAUD, useESlip=1,  driveOnly = 0,  readyTimeLimit = self.readyTimeLimit, ataReadyCheck = 0)
      return rate
