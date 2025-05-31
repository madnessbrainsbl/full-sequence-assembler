#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements the SATA Initiator interface
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/09/20 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SATA_ICmd.py $
# $Revision: #2 $
# $DateTime: 2016/09/20 03:10:55 $
# $Author: phonenaing.myint $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SATA_ICmd.py#2 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from base_Initiator_CMD import initCmd, PASS_RETURN, FAIL_RETURN
import ScrCmds, time, struct
import MessageHandler as objMsg
import types
from Utility import CUtility
from TestParamExtractor import TP

#---------------------------------------------------------------------------------------------------------#
lbaTuple = CUtility.returnStartLbaWords
wordTuple = CUtility.ReturnTestCylWord



class SATA_ICmd(initCmd):
   def __init__(self, params, objPwrCtrl):
      initCmd.__init__(self,  params, objPwrCtrl)


   def __overrideBlks(self, kwargs):
      if kwargs.get('TOTAL_BLKS_TO_XFR', False) == (0,0) or kwargs.get('TOTAL_BLKS_TO_XFR64', False) == (0, 0, 0, 0):
         kwargs.pop('TOTAL_BLKS_TO_XFR',0)
         kwargs.pop('TOTAL_BLKS_TO_XFR64',0)

         kwargs['MAXIMUM_LBA'] = (0xffff,0xffff,0xffff,0xffff)

      return kwargs

   def __override551Parms(self, args, kwargs):

      kwargs = self.__overrideBlks(kwargs)

      #new cpc style params
      if 'WRITE_READ_MODE' in kwargs:
         wrmode = kwargs.pop('WRITE_READ_MODE')
         kwargs.setdefault('CTRL_WORD1', 0)
         kwargs['CTRL_WORD1'] |= (wrmode & 3) << 4

      # If we are doing write/read mode
      if ( (kwargs['CTRL_WORD1'] >>4) & 3 ) == 0:
         kwargs['CTRL_WORD1'] |= 1 #enable fast mode
      else:
         kwargs['CTRL_WORD1'] &= 0xFFFE #disable fast mode

      patMode = None
      if 'PATTERN_MODE' in kwargs:
         patMode = kwargs.pop('PATTERN_MODE')
      if 'CWORD2' in kwargs:
         patMode = kwargs.pop('CWORD2')
      if patMode:
         patMode &= 0x83 # mask off all but pattern bits
      kwargs.setdefault('PATTERN_TYPE', 0)

      # need to fixup the 510 pattern types to 551 like
      kwargs['PATTERN_TYPE'] |= {0x80  : 0, # fixed pattern
                                 2     : 2, # Incremental pattern
                                 1     : 1, # Random pattern
                                 None  : 0, # def fixed pattern
                                 }[patMode]


      return args, kwargs

   def __override549Parms(self, args, kwargs):
      if 'START_CYL' in kwargs:
         start = kwargs.pop('START_CYL')
         kwargs['MINIMUM_LOCATION'] =  lbaTuple(CUtility.reverseTestCylWord(start))

      if 'END_CYL' in kwargs:
         end = kwargs.pop('END_CYL')
         kwargs['MAXIMUM_LOCATION'] =  lbaTuple(CUtility.reverseTestCylWord(end))
         if kwargs['MAXIMUM_LOCATION'] == (0,0,0xffff, 0xffff):
            #old maximum- triggers different determining step factors in intiator for test
            kwargs['MAXIMUM_LOCATION'] = (0xffff,0xffff,0xffff,0xffff)

      if 'CYLINDER_INCREMENT' in kwargs:
         stepSize = kwargs.pop('CYLINDER_INCREMENT')
         if type(stepSize) in [types.TupleType, types.ListType]:
            stepSize = stepSize[0]
         kwargs['STEP_SIZE'] =  lbaTuple(stepSize)


      return args, kwargs




   def __override510Parms(self, args, kwargs):

      kwargs = self.__overrideBlks(kwargs)

      #new cpc style params
      if 'WRITE_READ_MODE' in kwargs:
         wrmode = kwargs.pop('WRITE_READ_MODE')
         kwargs.setdefault('CTRL_WORD1', 0)
         kwargs['CTRL_WORD1'] |= (wrmode & 3) << 4

      if 'PATTERN_MODE' in kwargs:
         patMode = kwargs.pop('PATTERN_MODE')
         kwargs.setdefault('CTRL_WORD2', 0)
         kwargs['CTRL_WORD2'] |= patMode
         if (patMode & 0x80) == 0x80:
            kwargs['CTRL_WORD2'] |= 0x2000 #always use 32bit patterns...

      if 'DATA_PATTERN0' not in kwargs:
         kwargs['CTRL_WORD2'] |= 4

      if 'ACCESS_MODE' in kwargs:
         accmode = kwargs.pop('ACCESS_MODE')
         kwargs['CTRL_WORD1'] |= accmode

      return args, kwargs


   def __override597Parms(self, args, kwargs):
      kwargs['test_num'] = 645
      if kwargs.get('MAXIMUM_LBA', 0) in [0, [0,0,0,0], (0,0,0,0)]:
         kwargs.pop('MAXIMUM_LBA', 0)
      kwargs['MULTIPLIER'] = kwargs.pop('TEST_PASS_MULTIPLIER', 0)
      kwargs['LOOP_COUNT'] = kwargs.pop('TEST_PASS_COUNT', 1)
      kwargs['MAX_SECTOR_COUNT'] = kwargs.pop('MAX_BLOCK_PER_CMD',256)

      return args, kwargs


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

      #execute the test handlers
      if test == 510:
         args, kwds = self.__override510Parms(args, kwds)
      elif test == 551:
         args, kwds = self.__override551Parms(args, kwds)
      elif test == 598 :
         kwds.update({'ENABLE_HW_PATTERN_GEN': 1,
                      'DATA_PATTERN0'        : ( 0x0, 0x0 ),
                      'PATTERN_TYPE'         :  0x0000,
                      })
      elif test == 549 :
         args, kwds = self.__override549Parms(args,kwds)
      elif test == 597 and testSwitch.FE_0140980_231166_P_SUPPORT_TAG_Q_SI_0_QD:
         #test 597 isn't supported in banshee 2.0 initiators... 645 is a 0 que depth version of that
         args, kwds = self.__override597Parms(args,kwds)

      return args, kwds


   def fillIdentifyBuffer(self, refreshBuffer):
      if (len(self.IdentifyDeviceBuffer) < 204) or refreshBuffer:
         self.IdentifyDevice()

   def GetMaxLBA(self, refreshBuffer=True):
      """
      Get Max LBA from drive and return in CPC style dict {'LLRET':OK, 'MAX48':xxxx,'MAX28':xxxx}
      """

      self.fillIdentifyBuffer(refreshBuffer)
      self.maxlba = CUtility.numSwap(self.IdentifyDeviceBuffer[200:205])
      return { 'LLRET':OK,
               'MAX48': "%X" % self.maxlba,
               'MAX28': "%X" % CUtility.numSwap(self.IdentifyDeviceBuffer[120:124]),
               }


   def GetModelNum(self, useVendorField = False, refreshBuffer=True):
      self.fillIdentifyBuffer(refreshBuffer)
      return CUtility.strSwap(self.IdentifyDeviceBuffer[ 54: 94], stripWhitespace = False)


   def ZeroCheck(self, minLBA, maxLBA, scnt):
      prm = self.params.ZeroCheck.copy()

      prm['DATA_PATTERN0'] = (0,0)
      prm['STARTING_LBA'] = lbaTuple(minLBA)
      prm['TOTAL_BLKS_TO_XFR64'] = lbaTuple(maxLBA-minLBA)
      prm['failSafe'] = 1
      ret = self.St(prm)
      return self.translateStReturnToCPC(ret)

   def GetDriveSN(self, partNum = None, partNumOnlyValue = False):
      return CUtility.strSwap(self.IdentifyDeviceBuffer[ 20: 40])

   def St(self, *args, **kwargs):
      """
      Provides the st interface with CPC to SI parameter overrides
      """
      args, kwargs = self.__overrideTestParms(args, kwargs)

      if kwargs.get('test_num', 0) == 510:
         # If TEST_EXE_TIME_SECONDS is set in initiator 510 will run until that TMO expires
         self.SetRFECmdTimeout(0)

      ret = initCmd.St(self, *args, **kwargs)

      if kwargs.get('test_num', 0) == 510:
         self.SetRFECmdTimeout(TP.prm_IntfTest["Default ICmd Timeout"])

      return ret


   def HardReset(self, exc = 1):
      initCmd.HardReset(self)

   def SmartReadLogSec(self, logAddr, sectorCount):
      tempPrm = dict(self.params.SmartParameter)
      tempPrm.update({
            'FEATURES': 0xD5,
            'SECTOR_COUNT': sectorCount,
            'LBA_LOW': logAddr,
            'prm_name': "SmartReadLogSec",
         })
      self.St(tempPrm)
      return {'LLRET':0}#self.translateStReturnToCPC(self.St(tempPrm))

   def SmartWriteLogSec(self, logAddr, sectorCount):
      tempPrm = dict(self.params.SmartParameter)
      tempPrm.update({
            'FEATURES': 0xD6,
            'SECTOR_COUNT': sectorCount,
            'LBA_LOW': logAddr,
            'prm_name': "SmartWriteLogSec",
         })
      self.St(tempPrm)
      return {'LLRET':0}#self.translateStReturnToCPC(self.St(tempPrm))

   def WriteTestSim2(self, startLBA, midLBA, endLBA, singleLBA, scnt, loops, seed = 0, ovPrm = None, exc = 1, timeout = None):
      """
      CPC Alg
      Loop testCount
            |  WriteMultiple( rand OD, fixed scnt )
            |  FlushCache
            |  ReadMultiple( rand OD, fixed scnt )
            |  BufferCompare( compareFlag )
            |  ReadMultiple( singleLBA, fixed scnt )
            |  WriteMultiple( rand ID, rand scnt )
            |  FlushCache
            |  ReadMultiple( rand ID, rand scnt )
            |_ BufferCompare( compareFlag )
      SetFeatures( udmaSpeed )
      SequentialReadDMA( 0, maxLBA, fixesScnt )
      """
      self.HardReset()
      tempPrm = self.params.WriteTestSim2.copy()
      tempPrm.update({
            #"COMPARE_OPTION" : (0x00,),
       #"MULTI_SECTORS_BLOCK" : (0x07,),
                "LOOP_COUNT" : loops,
        "FIXED_SECTOR_COUNT" : scnt,
                "SINGLE_LBA" : wordTuple(singleLBA),
                   "MAX_LBA" : wordTuple(endLBA),
                   "MID_LBA" : wordTuple(midLBA),
                   "MIN_LBA" : wordTuple(startLBA),

         })
      return self.translateStReturnToCPC(self.St(tempPrm))

   def WriteTestMobile(self, *args, **kwargs):
      ovPrm = kwargs.get('ovPrm',{})
      tovPrm = {
               #'ENABLE_HW_PATTERN_GEN': 0,
            }
      tovPrm.update(ovPrm)
      kwargs['ovPrm'] = tovPrm
      return initCmd.WriteTestMobile(self, *args, **kwargs)

   def SmartEnableOper(self, timeout = 300, exc = 1):
      self.HardReset()
      tempPrm = dict(self.params.SmartParameter)
      tempPrm.update({
            'FEATURES': 0xD8,
            'prm_name': "SmartEnableOper",
            'timeout': timeout,
         })
      self.St(tempPrm)
      return PASS_RETURN

   def SmartReadData(self, timeout = 300, exc = 1):
      tempPrm = dict(self.params.SmartParameter)
      tempPrm.update({
            'FEATURES': 0xD0,
            'prm_name': "SmartReadData",
            'timeout': timeout,
         })
      self.St(tempPrm)
      return PASS_RETURN

   def SmartReadThresh(self):
      tempPrm = dict(self.params.SmartParameter)
      tempPrm.update({
            'FEATURES': 0xD1,
            'prm_name': "SmartReadThreshold",
         })
      return self.translateStReturnToCPC(self.St(tempPrm))  

   def SmartReturnStatus(self, timeout = 300, exc = 1):
      self.HardReset()
      tempPrm = dict(self.params.SmartParameter)
      tempPrm.update({
            'FEATURES': 0xDA,
            'prm_name': "SmartReturnStatus",
            'timeout': timeout,
         })
      if testSwitch.virtualRun:
         return {'LLRET':0,'LBA': 0xc24f00}
      else:
         return self.translateStReturnToCPC(self.St(tempPrm))

   def SmartCheck(self, timeout = 300, exc = 1):   
      try:
         self.SmartEnableOper()
         self.SmartReadData()
         self.SmartReturnStatus()
         return PASS_RETURN         
      except:      
         return FAIL_RETURN.copy()
		 
   #-------------------------------------------------------------------------------------------------------
   def SetFeatures(self, *args, **kwargs):
      self.HardReset()
      tempPrm = dict(self.params.SetFeaturesParameter)
      #order the arguments are entered
      orderedKeyList = ['FEATURES',
                        'SECTOR_COUNT',
                        'SECTOR',
                        'CYLINDER',]

      for index, arg in enumerate(args):
         tempPrm[orderedKeyList[index]] = arg


      return self.translateStReturnToCPC(self.St(tempPrm))


   def BufferCopy(self, destBuffFlag, destOffset, srcBuffFlag, srcOffset, byteCount):
      tempPrm = dict(self.params.BufferCopy) #create a copy

      if destBuffFlag == WBF:
         tempPrm['CTRL_WORD1'] = 0x6 #Copy READ buffer to WRITE buffer
         tempPrm['BUFFER_LENGTH'] = wordTuple(byteCount)
         tempPrm['BYTE_OFFSET'] = wordTuple(destOffset)

      if destBuffFlag == RBF:
         tempPrm['CTRL_WORD1'] = 0x7 #Copy WRITE buffer to READ buffer
         tempPrm['BUFFER_LENGTH'] = wordTuple(byteCount)
         tempPrm['BYTE_OFFSET'] = wordTuple(destOffset)

      ret = self.St(tempPrm)
      return PASS_RETURN

   def ClearBinBuff(self, buffNum = WBF, exc = 1):
      tempPrm = dict(self.params.WritePatternToBuffer) #create a copy
      tempPrm['DATA_PATTERN0'] = (0,0)

      if testSwitch.BF_0133850_372897_REMOVE_BUFFER_LENGTH_IN_CLEARBUFFER:
         tempPrm.pop('BUFFER_LENGTH', (0, 512))   # Default is whole buffer
      else:
         tempPrm['BUFFER_LENGTH'] = (0x99,0xFFFF)

         ver = self.getRimCodeVer()
         ver = [v for v in ver.split('.') if v.isdigit()][0]
         if int(ver) >= 754878: #SIC 754878 onwards, read/write max buffer length has been readjusted
            tempPrm['BUFFER_LENGTH'] = (0x98,0xFFFF)         

      if buffNum & WBF:
         tempPrm['CTRL_WORD1'] = (0x0000,)
         tempPrm['prm_name'] = 'Write Pattern to Write Buffer'
         status = self.St(tempPrm)
      if buffNum & RBF:
         tempPrm['CTRL_WORD1'] = (0x0001,)
         tempPrm['prm_name'] = 'Write Pattern to Read Buffer'
         status = self.St(tempPrm)

      return {'LLRET':OK}

   def FillBuffByte(self, buffFlag, data, byteOffset=0, byteCount = None):
      """
      FillBuffByte's input according to CPC spec is a string indicating the buffer bytes to write... so input here for data is
      '0000' for a binary \x00\x00 written to the log
      """
      tempPrm = dict(self.params.WritePatternToBuffer) #create a copy

      if testSwitch.BF_0145286_231166_P_FIX_MOBILE_SCREENS:
         if type(data) != types.StringType:
            data = "%X" % data

      data = CUtility.strBufferToBinString(data)

      data = data[:8] #max bytepattern len is 8 bytes for SI
      tempPrm['BYTE_PATTERN_LENGTH'] = len(data)

      #expand pattern to full 8 bytes for extraction
      data = data + ''.join(['\x00' for i in range(0,8-len(data) )])
      dataWords = struct.unpack('>HHHH',  data)
      #first 4 bytes
      tempPrm['DATA_PATTERN0'] = dataWords[0:2]
      #second 4 bytes
      tempPrm['DATA_PATTERN1'] = dataWords[2:]

      tempPrm['BYTE_OFFSET'] = wordTuple(byteOffset)
      if byteCount == None:
         #remove buffer length- forces full bufer update
         tempPrm.pop('BUFFER_LENGTH')
      else:
         byteCount = max([byteCount, 8])
         tempPrm['BUFFER_LENGTH'] = wordTuple(byteCount)


      if buffFlag & WBF:
         tempPrm['CTRL_WORD1'] = (0x0000,)
         tempPrm['prm_name'] = 'Write Pattern to Write Buffer'
         status = self.St(tempPrm)
      if buffFlag & RBF:
         tempPrm['CTRL_WORD1'] = (0x0001,)
         tempPrm['prm_name'] = 'Write Pattern to Read Buffer'
         status = self.St(tempPrm)

      return PASS_RETURN


   def PutBuffByte(self, buffFlag, data, byteOffset):
      tempPrm = dict(self.params.WritePatternToBuffer) #create a copy

      if buffFlag & WBF:
         tempPrm['CTRL_WORD1'] = (0x100C,)
         tempPrm['prm_name'] = 'Write Pattern to Write Buffer'
      if buffFlag & RBF:
         tempPrm['CTRL_WORD1'] = (0x100D,)
         tempPrm['prm_name'] = 'Write Pattern to Read Buffer'

      maxNibbles = 16 # SI maximum is 16 nibbles
      for idx, chunk in enumerate([data[i:i+maxNibbles] for i in xrange(0, len(data), maxNibbles)]):
         tempPrm['BYTE_OFFSET'] = wordTuple(byteOffset + (idx * (maxNibbles / 2)))
      
         if len(chunk) > 8:
            tempPrm['DATA_PATTERN0'] = wordTuple( int(chunk[:8], 16 ) << (32-(len(chunk[:8])*4)))
            tempPrm['DATA_PATTERN1'] = wordTuple( int(chunk[8:], 16 ) << (32-(len(chunk[8:])*4)))
         else:
            tempPrm['DATA_PATTERN0'] = wordTuple( int(chunk[:8], 16) << (32-(len(chunk)*4)))    
         
         tempPrm['BIT_PATTERN_LENGTH'] = len(chunk)*4
         tempPrm['BUFFER_LENGTH'] = wordTuple(len(chunk))

         try:
            self.St(tempPrm)
         except:
            return FAIL_RETURN.copy()
            
      return PASS_RETURN 
      
   def FillBuffer(self, buffFlag , byteOffset, data):
      tempPrm = dict(self.params.WritePatternToBuffer) #create a copy

      dataSize = len(data)

      bytesSent = 0

      import FileXferFactory
      import cStringIO
      payLoadSize = 8000000


      while bytesSent < dataSize:

         tempPrm['BYTE_OFFSET'] = wordTuple(byteOffset + bytesSent)

         memFile = cStringIO.StringIO(data[bytesSent : bytesSent + payLoadSize])
         if DEBUG:
            objMsg.printMsg("Sending Buffer to drive")
            objMsg.printBin(data[bytesSent : bytesSent + payLoadSize])

         ff = FileXferFactory.FileXferFactory(memFile, FileXferFactory.REQUEST_DRIVEFW_FILE_BLOCK, 0)
         tempPrm['BUFFER_LENGTH'] = wordTuple(min(payLoadSize, len(data[bytesSent : bytesSent + payLoadSize])))

         if buffFlag & WBF:
            tempPrm['CTRL_WORD1'] = (0x000A,)
            tempPrm['prm_name'] = 'Write Pattern to Write Buffer'
            status = self.St(tempPrm)
         if buffFlag & RBF:
            tempPrm['CTRL_WORD1'] = (0x000B,)
            tempPrm['prm_name'] = 'Write Pattern to Read Buffer'
            status = self.St(tempPrm)

         ff.close()

         bytesSent += payLoadSize #get next 4 bytes.. 2 words

      return {'LLRET':OK}


   def FillBuffInc(self, buffFlag):
      tempPrm = dict(self.params.WritePatternToBuffer)   # Create local copy
      tempPrm['BUFFER_LENGTH']   = (0x0000, 0x0000)      # Whole buffer
      tempPrm['PATTERN_TYPE']    = 0x0002                # Incrementing pattern

      if buffFlag & WBF:
         tempPrm['CTRL_WORD1']   = 0x0000
         tempPrm['prm_name']     = 'Write Pattern to Write Buffer'
         status = self.St(tempPrm)

      if buffFlag & RBF:
         tempPrm['CTRL_WORD1']   = 0x0001
         tempPrm['prm_name']     = 'Write Pattern to Read Buffer'
         status = self.St(tempPrm)

      return {'LLRET':OK}


   def FillBuffRandom(self, buffFlag):
      tempPrm = dict(self.params.WritePatternToBuffer)   # Create local copy
      tempPrm['BUFFER_LENGTH']   = (0x0000, 0x0000)      # Whole buffer
      tempPrm['PATTERN_TYPE']    = 0x0001                # Random pattern

      if buffFlag & WBF:
         tempPrm['CTRL_WORD1']   = 0x0000
         tempPrm['prm_name']     = 'Write Pattern to Write Buffer'
         status = self.St(tempPrm)

      if buffFlag & RBF:
         tempPrm['CTRL_WORD1']   = 0x0001
         tempPrm['prm_name']     = 'Write Pattern to Read Buffer'
         status = self.St(tempPrm)

      return {'LLRET':OK}


   if testSwitch.FE_0144363_421106_P_TIMEOUT_SPEC_FOR_SMART_LONG_DST:
      def LongDST(self,TimeoutLimit = 0):
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

         if testSwitch.BF_0134600_372897_DST_TEST_BUG_FIX_IN_SI  and (not testSwitch.virtualRun):
            DSTStatus = self.dut.dblData.Tables('P600_SELF_TEST_STATUS').tableDataObj()[-1]['SELF_TEST_STATUS']
            if int(DSTStatus) != 0:
               objMsg.printMsg("DST SELF_TEST_STATUS: %s" % DSTStatus, objMsg.CMessLvl.IMPORTANT)
               smartEnableOperData = self.SmartEnableOper()
               objMsg.printMsg("DST SmartEnableOper data: %s" % smartEnableOperData, objMsg.CMessLvl.IMPORTANT)
               if smartEnableOperData['LLRET'] != 0:
                  ScrCmds.raiseException(13455, 'Failed Smart Enable Oper - During Long DST')
               DSTLogData = self.SmartReadLogSec(6, 1)               # 6=DST Log, 1=#DST Log Sectors
               objMsg.printMsg("DST SmartReadLogSec data: %s" % DSTLogData, objMsg.CMessLvl.IMPORTANT)
               ScrCmds.raiseException(13459, 'Failed Smart Long DST - Drive Self Test')
   else:
      def LongDST(self):
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

         if testSwitch.BF_0134600_372897_DST_TEST_BUG_FIX_IN_SI  and (not testSwitch.virtualRun):
            DSTStatus = self.dut.dblData.Tables('P600_SELF_TEST_STATUS').tableDataObj()[-1]['SELF_TEST_STATUS']
            if int(DSTStatus) != 0:
               objMsg.printMsg("DST SELF_TEST_STATUS: %s" % DSTStatus, objMsg.CMessLvl.IMPORTANT)
               smartEnableOperData = self.SmartEnableOper()
               objMsg.printMsg("DST SmartEnableOper data: %s" % smartEnableOperData, objMsg.CMessLvl.IMPORTANT)
               if smartEnableOperData['LLRET'] != 0:
                  ScrCmds.raiseException(13455, 'Failed Smart Enable Oper - During Long DST')
               DSTLogData = self.SmartReadLogSec(6, 1)               # 6=DST Log, 1=#DST Log Sectors
               objMsg.printMsg("DST SmartReadLogSec data: %s" % DSTLogData, objMsg.CMessLvl.IMPORTANT)
               ScrCmds.raiseException(13459, 'Failed Smart Long DST - Drive Self Test')

   def ShortDST(self):
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

      if testSwitch.BF_0134600_372897_DST_TEST_BUG_FIX_IN_SI and (not testSwitch.virtualRun):
         DSTStatus = self.dut.dblData.Tables('P600_SELF_TEST_STATUS').tableDataObj()[-1]['SELF_TEST_STATUS']
         if int(DSTStatus) != 0:
            objMsg.printMsg("DST SELF_TEST_STATUS: %s" % DSTStatus, objMsg.CMessLvl.IMPORTANT)
            smartEnableOperData = self.SmartEnableOper()
            objMsg.printMsg("DST SmartEnableOper data: %s" % smartEnableOperData, objMsg.CMessLvl.IMPORTANT)
            if smartEnableOperData['LLRET'] != 0:
               ScrCmds.raiseException(13455, 'Failed Smart Enable Oper - During Long DST')
            DSTLogData = self.SmartReadLogSec(6, 1)               # 6=DST Log, 1=#DST Log Sectors
            objMsg.printMsg("DST SmartReadLogSec data: %s" % DSTLogData, objMsg.CMessLvl.IMPORTANT)
            ScrCmds.raiseException(13458, 'Failed Smart Short DST - Drive Self Test')

   def Seek(self, *args, **kwargs):
      """Polymorphic access to SEEK"""
      numArgs = len(args) + len(kwargs.keys())
      if numArgs < 2:
         return self._Seek_LBA(*args, **kwargs)
      else:
         return self._Seek_CHS(*args, **kwargs)
      
   def _Seek_LBA(self, lba, exc = 1):
      prm = self.params.Seek_LBA.copy()

      prm['LBA'] = CUtility.returnStartLbaWords( lba )
      prm['stSuppressResults'] = ST_SUPPRESS__ALL | ST_SUPPRESS_SUPR_CMT

      ret = self.St(prm)
      if exc:
         return {'LLRET': OK}
      else:
         return self.translateStReturnToCPC(ret)         

   def _Seek_CHS(self, Cylinder, Head, Sector, exc = 1):
      tempPrm = self.params.Seek_CHS.copy()      
      tempPrm.update({            
            "CYLINDER" : Cylinder,            
            "HEAD" : Head,            
            "SECTOR" : Sector,              
                  })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN.copy()      
   
   def WriteFinalAssemblyDate(self, weekstr):
      param4 = (ord(weekstr[0]) << 8) | (ord(weekstr[1]))
      param5 = (ord(weekstr[2]) << 8) | (ord(weekstr[3]))
      DriveAttributes["FINAL_ASSY_DATE"]= weekstr
      prm = self.params.WriteFinalAssemblyDate.copy()
      prm["FINAL_ASSEMBLY_DATE"] = (0,0,param4, param5)

      self.St(prm,TEST_FUNCTION=(0))  # Write Final assembly date
      self.St(prm,TEST_FUNCTION=(1))  # Read  Final assembly date
      self.St(prm,TEST_FUNCTION=(2))  # Compare Final assembly date

   if testSwitch.FE_0133768_372897_DMAEXTTRANSRATE_TEST_WITH_T641:
      def ReadDMAExtTransRate(self, startLBA, TotalBlksXfr, BlksPerXfr = 256, exc = 1):
         return self.__baseXFERRate(0,  startLBA, TotalBlksXfr, BlksPerXfr, exc = exc)

      def WriteDMAExtTransRate(self, startLBA, TotalBlksXfr, BlksPerXfr = 256, exc = 1):
         return self.__baseXFERRate(1,  startLBA, TotalBlksXfr, BlksPerXfr, exc)

      def __baseXFERRate(self, xferType, startLBA, TotalBlksXfr, BlksPerXfr = 256, exc = 1):
         prm = self.params.DMAExtTransRate.copy()
         xferRateId = {0:'Read', 1:'Write'}
         prm.update({
            'prm_name' : "%sDMAExtTransRate" % xferRateId[xferType],
            'STARTING_LBA': lbaTuple(startLBA),
            'TOTAL_BLKS_TO_XFR64': lbaTuple(TotalBlksXfr),
            'DATA_PATTERN0': (0,0),
            'BLKS_PER_XFR': BlksPerXfr,
            'WRITE_READ_MODE': xferType,
         })
         if 1:    # enabled for both write and read
            prm.update({'ENABLE_HW_PATTERN_GEN': 1,})

         try:     self.dut.dblData.delTable('P641_DMAEXT_TRANSFER_RATE', forceDeleteDblTable = 1)     #Clear P_CCT_DISTRIBUTION table before do CCT
         except:  objMsg.printMsg('Delete table P641_DMAEXT_TRANSFER_RATE fail')
         try:
            ret = self.translateStReturnToCPC( self.St(prm) )
            if testSwitch.virtualRun:
               return {'LLRET': 0, 'SCNT': 0, 'HEAD': 0, 'ERR': 0, 'TXRATE': '100', 'DEV': 64, 'LBA': 4385491, 'STS': 80, 'SCTR': 211, 'ENDLBA': '625142446', 'CYL': 17130}
            else:
               data = self.dut.dblData.Tables('P641_DMAEXT_TRANSFER_RATE').tableDataObj()
               for entry in data:
                  ENDLBA = entry['END_LBA']
                  TXRATE = entry['XFER_RATE_MB_PER_SEC']
                  LBA_CNT = entry['LBA_CNT']
                  START_LBA = entry['START_LBA']

               ret.update({
                  'ENDLBA': ENDLBA,
                  'TXRATE': TXRATE,
                  'LBA_CNT': LBA_CNT,
                  'START_LBA': START_LBA,
                         })
               return ret
         except:
            return FAIL_RETURN.copy()
   else:
      def ReadDMAExtTransRate(self, startLBA, TotalBlksXfr, BlksPerXfr = 256, exc = 1):
         return self.__baseXFERRate(1,  startLBA, TotalBlksXfr, BlksPerXfr, exc = exc)

      def WriteDMAExtTransRate(self, startLBA, TotalBlksXfr, BlksPerXfr = 256, exc = 1):
         return self.__baseXFERRate(2,  startLBA, TotalBlksXfr, BlksPerXfr, exc)

      def __baseXFERRate(self, xferType, startLBA, TotalBlksXfr, BlksPerXfr = 256, exc = 1):
         prm = self.params.DMAExtTransRate.copy()
         xferRateId = {1:'Read', 2:'Write'}
         prm.update({
            'prm_name' : "%sDMAExtTransRate" % xferRateId[xferType],
            'WRITE_READ_MODE': xferType,
            'FILL_WRITE_BUFFER': 1,
            'PATTERN_TYPE': 0x80,
            'DATA_PATTERN': (0,0),
            'TOTAL_BLKS_TO_XFR64': lbaTuple(TotalBlksXfr),
            'MAX_NBR_ERRORS': 0,
         })

         ret = self.St(prm)

         return {'LLRET': OK, 'TXRATE': 0, 'RESULT': 0}

   def Standby(self, timerPeriod = 0, exc= 1):
      prm = self.params.Standby.copy()

      prm['SECTOR_COUNT'] = timerPeriod
      return self.translateStReturnToCPC( self.St(prm) )

   def disable_WriteCache(self, exc = 1):
      #Disable Write Cache
      return self.SetFeatures(0x82, exc = exc)

   def enable_WriteCache(self, exc = 1):
      #Enable Write Cache
      return self.SetFeatures(0x02, exc = exc)

   def Idle(self, timerPeriod = 0, exc = 1):
      prm = self.params.Idle.copy()
      prm['SECTOR_COUNT'] = timerPeriod      
      ret = self.St(prm)
      return self.translateStReturnToCPC(ret)                
      
   def CheckPowerMode(self, exc = 1):
      prm = self.params.CheckPowerMode.copy()
      ret = self.St(prm)
      return self.translateStReturnToCPC(ret)

   def ExecDeviceDiag(self, exc = 1):
      tempPrm = self.params.ExecDeviceDiag.copy()
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN.copy() 

      
   def WriteSectorsExt(self,lba,sectorCount, exc = 1):
      tempPrm = self.params.WriteSectorsExt.copy()
      tempPrm.update({
            'SECTOR_COUNT': sectorCount,
            'LBA': CUtility.returnStartLbaWords( lba ),     
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN.copy()      
      
   def ReadSectorsExt(self,lba,sectorCount, exc = 1):   
      tempPrm = self.params.ReadSectorsExt.copy()
      tempPrm.update({
            'SECTOR_COUNT': sectorCount,
            'LBA': CUtility.returnStartLbaWords( lba ),     
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN.copy()    

   def SetMultipleMode(self,sectorCount, exc = 1):
      tempPrm = self.params.SetMultipleMode.copy()
      tempPrm.update({
            'SECTOR_COUNT': sectorCount,
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN.copy()            
      
   def WriteMultiple(self,lba,sectorCount, exc = 1):
      tempPrm = self.params.WriteMultiple.copy()
      tempPrm.update({
            'SECTOR_COUNT': sectorCount,
            'LBA': CUtility.returnStartLbaWords( lba ),
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN.copy()               
            

   def ReadMultiple(self,lba,sectorCount, exc = 1):
      tempPrm = self.params.ReadMultiple.copy()
      tempPrm.update({
            'SECTOR_COUNT': sectorCount,
            'LBA': CUtility.returnStartLbaWords( lba ),
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN.copy()             

   def SystemTrackWriteSim(self, lba, scnt, sctrPerBlock, pattern, exc = 1, timeout = None):
      """
      Using T654
      """
      objMsg.printMsg('*'*20+'SystemTrackWriteSim'+'*'*20) 
      tempPrm = self.params.SystemTrackWriteSim.copy()
      tempPrm.update({
                  'LBA'                : CUtility.returnStartLbaWords(lba),
                  'SECTOR_COUNT'       : scnt,
                  'DATA_PATTERN0'      : wordTuple(int((pattern*2)[:8], 16)),
                  'MULTI_SECTORS_BLOCK': sctrPerBlock })
                  
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN.copy()    
      

   def LoadTestFileSim(self, minSeqLBA1, maxSeqLBA1, seqScnt1, minSeqLBA2, maxSeqLBA2, seqScnt2, minRandLBA2, maxRandLBA2, \
                       randScnt, randCount, minSeqLBA3, maxSeqLBA3, seqScnt3, patData, udmaSpeed, msDelay , exc =1, timeout = None):
      """
      CPC Alg
      -FillBytePatternStr( patData )
      -SetFeatures( udmaSpeed )
      -SequentialWRDMAExt( minSeqLBA1, maxSeqLBA1, seqScnt1,compare = True )
      -FlushCache()
      -IdleImmediate
      -Wait( msDelay )
      -ReadDMAExt( lastLBA, lastScnt )
      -CompareBuffer ( 0, lastScnt * 512, Write buffer ) ---To compare the current readbuffer with the writebuffer. You can choose other suitable functions as you like.
      -SequentialReadDMAExt( minSeqLBA2, maxSeqLB2, seqScnt2)
      -RandomReadDMAExt( minRandLBA, maxRandLBA, randScnt, randCnt )
      -SequentialReadDMAExt( minSeqLBA3, maxSeqLB3, seqScnt3 )
      """

      objMsg.printMsg('*'*20+'LoadTestFileSim'+'*'*20)
      if timeout != None:
         self.SetRFECmdTimeout(timeout)

      self.FillBuffByte(WBF,patData,0,512*seqScnt1)             
      self.SetFeatures(0x3,udmaSpeed)
      self.SequentialWRDMAExt(minSeqLBA1, maxSeqLBA1-1, seqScnt1, seqScnt1, DATA_PATTERN0 = int(patData), COMPARE_FLAG = 1)  
      self.HardReset()       
      self.FlushCache()      
      self.HardReset()
      self.IdleImmediate()       
      time.sleep(msDelay/100)            
      lastLBA = (maxSeqLBA1 - seqScnt1) - 1
      lastScnt = seqScnt1 #Where lastLBA and lastScnt are the LBA and sector count from the last command send during SequentialWRDMAExt().      
      self.SequentialReadDMAExt(lastLBA, lastLBA+lastScnt-1, lastScnt, lastScnt, DATA_PATTERN0 = int(patData), COMPARE_FLAG = 1) #ReadDMAExt( lastLBA, lastScnt )
      self.SequentialReadDMAExt(minSeqLBA2, maxSeqLBA2-1, seqScnt2, seqScnt2)      
      self.RandomReadDMAExt( minRandLBA2, maxRandLBA2-1, randScnt, randScnt, randCount )
      self.SequentialReadDMAExt( minSeqLBA3, maxSeqLBA3-1, seqScnt3 ,seqScnt3)            
            
      return PASS_RETURN
      
   def BluenunSlide(self, start_lba, end_lba, sect_cnt, numEntriesAvgTimeList, autoMultiplier, regionSize,
                    regionLimit, enableLogging, cmdRetry, exc = 1):
      tempPrm = self.params.BluenunSlide.copy()

      CTRL_WORD1 = tempPrm["CTRL_WORD1"] | (cmdRetry << 4)
      CTRL_WORD1 = CTRL_WORD1 | (enableLogging << 6)
      CTRL_WORD1 = CTRL_WORD1 | (regionLimit << 7)

      CTRL_WORD2 = tempPrm["CTRL_WORD2"] | (numEntriesAvgTimeList)
      CTRL_WORD2 = CTRL_WORD2 | (regionSize << 8)

      autoMultiplier = int(autoMultiplier*10)
      tempPrm.update({
             "CTRL_WORD1" : CTRL_WORD1,
             "CTRL_WORD2" : CTRL_WORD2,
           "STARTING_LBA" : lbaTuple(start_lba),
            "MAXIMUM_LBA" : lbaTuple(end_lba),
           "BLKS_PER_XFR" : sect_cnt,
             "MULTIPLIER" : autoMultiplier,
         })
      try:
         ret = self.St(tempPrm)
         data = self.dut.dblData.Tables('P639_BLUENUNSLIDE').tableDataObj()[-1]
         return {'LLRET':0,'DATA':data}
      except:
         return FAIL_RETURN.copy()


   def BluenunMulti(self, span1, sect_cnt, span3, skip3 , exc = 1):
      tempPrm = self.params.BluenunMulti.copy()

      tempPrm.update({
            "MAXIMUM_LBA" : lbaTuple(span1),
           "BLKS_PER_XFR" : sect_cnt,
          "BLUENUN_SPAN3" : lbaTuple(span3),
          "BLUENUN_SKIP3" : wordTuple(skip3),
         })
      try:
         ret = self.St(tempPrm)
         return PASS_RETURN
      except:
         return FAIL_RETURN.copy()
      
   def BluenunAuto(self, start_lba, end_lba, sect_cnt, autoMultiplier, cmdPerSample, sampPerReg, blueNunLogTmo, maxTotalRetry, maxGroupRetry, timeout, exc = 1):
      tempPrm = self.params.BluenunAuto.copy()            
            
      CTRL_WORD1 = tempPrm["CTRL_WORD1"] | (blueNunLogTmo << 7)      
      
      tempPrm.update({            
              "CTRL_WORD1": CTRL_WORD1,
            "STARTING_LBA": lbaTuple(start_lba),
            "MAXIMUM_LBA" : lbaTuple(end_lba),
           "BLKS_PER_XFR" : sect_cnt,        
             "MULTIPLIER" : autoMultiplier,
            "SAMPLE_SIZE" : cmdPerSample,            
            "NUM_SAMPLES" : sampPerReg,            
           "TOTAL_RETRIES": maxTotalRetry,
           "GROUP_RETRIES": maxGroupRetry,     
         "COMMAND_TIMEOUT": wordTuple(timeout),      
         })
      try:       
         ret = self.St(tempPrm)
         data = self.dut.dblData.Tables('P639_BLUENUNSCAN').tableDataObj()[-1]          
         data.update(PASS_RETURN)
         return data    
      except:
         return FAIL_RETURN.copy()       



   def BufferCompareTest(self, startLba, totalBlks, loopcnt, bufflen, exc = 1):
      prm = self.params.BufferCompareTest.copy()
      prm.update(
         {
         'TEST_FUNCTION'         : 0x10 ,
         'STARTING_LBA'          : lbaTuple(startLba),
         'TOTAL_BLKS_TO_XFR64'   : lbaTuple(totalBlks),
         'BUFFER_LENGTH'         : wordTuple(bufflen),
         'LOOP_COUNT'            : loopcnt,
         })
      try:
         self.St(prm)
         return PASS_RETURN
      except:
         if exc:
            raise
         else:
            return FAIL_RETURN.copy()


   def updateFISattrs_FW_ID(self):
      """
      Just used to update FW attributes prior to DataToDisc creation
      """
      self.IdentifyDevice()

   def WriteMIFDataToDisc(self, callback):
      """
      Write manufacturing information file to DUT using test 795 (cpc ver > 2.206) or 595 (cpc ver < 2.206)
      """

      RegisterResultsCallback(callback ,63, 0)
      try:
         ret = self.St(self.params.WriteMIFDataToDisc)
      finally:
         RegisterResultsCallback("",63)

      return ret

   def __CCTTest(self, thr0, thr1, thr2, ovPrm = None, exc = 1, timeout = None):
      """
      Extend threshold number(>thr0, >thr1, >thr2) into return value
      """
      RetThr0, RetThr1, RetThr2 = 0, 0, 0         #Set default return value
      CCTSetting = 0
      #IRSATA.251779.BAN20.SI.4C.251779.INC.LOD code fixed issue
      #[thr0, thr1, thr2] = [(i*1000) for i in [thr0, thr1, thr2]]       #For fix SI bug, CPC was counting CCT in millisecond, and SI in usec
      minThresh = min(thr0, thr1, thr2)
      maxThresh = max(thr0, thr1, thr2)
      binStep = int(minThresh/5)                       #Divide bin step
      totalBin = min(int(maxThresh/binStep), 50)       #max bin number = 50
      if binStep > 0xFF:
         CCTSetting |= 0xFF
      else:
         CCTSetting |= binStep & 0xFF
      CCTSetting |= (totalBin & 0xFF)<<8
      ovPrm.update({
            'CCT_BIN_SETTINGS' : (CCTSetting),
               })

      try:     self.dut.dblData.delTable('P_CCT_DISTRIBUTION', forceDeleteDblTable = 1)     #Clear P_CCT_DISTRIBUTION table before do CCT
      #except:  pass
      except:  objMsg.printMsg('Delete table P_CCT_DISTRIBUTION fail')

      self.UnlockFactoryCmds()
      try:
         ret = self.translateStReturnToCPC(self.St(ovPrm))
         if testSwitch.virtualRun:
            return {'LLRET': 0, 'LBA': '0x00000000746FD087', 'ERR': '0', 'RES': '', 'DEV': '64', 'SCNT': '0', 'RESULT': 'IEK_OK:No error', 'STS': '80', 'THR1': '0', 'THR2': '0', 'THR0': '0', 'CT': '69537'}
         else:
            data = self.dut.dblData.Tables('P_CCT_DISTRIBUTION').tableDataObj()
            for entry in data:
               if entry['TEST_SEQ_EVENT'] == self.dut.objSeq.getTestSeqEvent(510):
                  if int(entry['BIN_THRESHOLD']) >= thr0:
                     RetThr0 += int(entry['BIN_ENTRIES'])
                  if int(entry['BIN_THRESHOLD']) >= thr1:
                     RetThr1 += int(entry['BIN_ENTRIES'])
                  if int(entry['BIN_THRESHOLD']) >= thr2:
                     RetThr2 += int(entry['BIN_ENTRIES'])
            ret.update({
                  'THR0': RetThr0,
                  'THR1': RetThr1,
                  'THR2': RetThr2,
                        })
            return ret
      except:
         return FAIL_RETURN.copy()


   def __ConvertWRmode(self, wrCmd = None,):
      """
      Write/read mode:
      0=write/read
      1=read
      2=write
      3=read/write
      """
      if wrCmd == None:
         return 0
      wrmode = 0
      WRDMAExt = {
            'ReadDMAExt' : 0x25,
            'WriteDMAExt': 0x35,
          'ReadVerifyExt': 0x42,
                  }
      WRDMAExtNum = {
            'ReadDMAExt' : 1,
            'WriteDMAExt': 2,
          'ReadVerifyExt': 4,
                  }
      for key in WRDMAExt:
         if WRDMAExt[key] == wrCmd:
            wrmode = WRDMAExtNum[key]
            break
      return wrmode

   def RandomCCT(self, wrCmd, startLBA, endLBA, scnt, loopCnt, thr0, thr1, thr2, COMPARE_FLAG=0, wrCmd2 = None, ovPrm = None, exc = 1, timeout = None, spcid = None):
      """
      CPC Alg
      """
      self.HardReset()
      objMsg.printMsg('wrCmd=%s, startLBA=%s, endLBA=%s, scnt=%s, loopCnt=%s, thr0=%s, thr1=%s, thr2=%s, COMPARE_FLAG=%s, wrCmd2 = %s, ovPrm = None, exc = 1, timeout = None' %
                      (wrCmd, int(startLBA), int(endLBA), int(scnt), int(loopCnt), thr0, thr1, thr2, COMPARE_FLAG, wrCmd2,))
      tempPrm = self.params.RandomCCT.copy()
      tempPrm.update({
            'STARTING_LBA' : lbaTuple(int(startLBA)),
            'BLKS_PER_XFR': int(scnt),
            'MAXIMUM_LBA' : lbaTuple(int(endLBA)),
            'TOTAL_BLKS_TO_XFR64' : lbaTuple(int(loopCnt) * int(scnt)),
               })
      tempPrm['display_info'] = True               
      if spcid != None:
         tempPrm.update({'spc_id' : spcid})
      wrmode  = self.__ConvertWRmode(wrCmd)
      wrmode2 = self.__ConvertWRmode(wrCmd2)
      objMsg.printMsg('RandomCCT wrmode = %s, wrmode2 = %s' % (wrmode, wrmode2))
      tempPrm['CTRL_WORD1'] &= 0x0F
      if wrmode == wrmode2 or wrCmd2 == None:
         tempPrm['CTRL_WORD1'] |= (wrmode & 7) << 4
      elif wrmode==1 and wrmode2==2:
         tempPrm['CTRL_WORD1'] |= (3 & 3) << 4
      elif wrmode==2 and wrmode2==1:
         tempPrm['CTRL_WORD1'] |= (0 & 3) << 4
      ret = self.__CCTTest(thr0, thr1, thr2, tempPrm)

      return ret

   def SequentialCCT(self, wrCmd, startLBA, endLBA, scnt, step, thr0, thr1, thr2, COMPARE_FLAG=0, wrCmd2 = None, ovPrm = None, exc = 1, timeout = None, spcid = None):
      """
      CPC Alg
      """
      self.HardReset()
      objMsg.printMsg('wrCmd=%s, startLBA=%s, endLBA=%s, scnt=%s, step=%s, thr0=%s, thr1=%s, thr2=%s, COMPARE_FLAG=%s, wrCmd2 = %s, ovPrm = None, exc = 1, timeout = None' %
                      (wrCmd, int(startLBA), int(endLBA), int(scnt), int(step), thr0, thr1, thr2, COMPARE_FLAG, wrCmd2,))
      tempPrm = self.params.SequentialCCT.copy()
      tempPrm.update({
            'STARTING_LBA' : lbaTuple(int(startLBA)),
             'BLKS_PER_XFR': int(scnt),
               "STEP_SIZE" : lbaTuple(step), 
     "TOTAL_BLKS_TO_XFR64" : lbaTuple(int(endLBA - startLBA)),
               })
      tempPrm['display_info'] = True
      if spcid != None:
         tempPrm.update({'spc_id' : spcid})
      wrmode  = self.__ConvertWRmode(wrCmd)
      wrmode2 = self.__ConvertWRmode(wrCmd2)
      objMsg.printMsg('SequentialCCT wrmode = %s, wrmode2 = %s' % (wrmode, wrmode2))
      tempPrm['CTRL_WORD1'] &= 0x0F
      if wrmode == wrmode2 or wrCmd2 == None:
         tempPrm['CTRL_WORD1'] |= (wrmode & 7) << 4
      elif wrmode==1 and wrmode2==2:
         tempPrm['CTRL_WORD1'] |= (3 & 3) << 4
      elif wrmode==2 and wrmode2==1:
         tempPrm['CTRL_WORD1'] |= (0 & 3) << 4
      ret = self.__CCTTest(thr0, thr1, thr2, tempPrm)

      return ret

   def TwoPointSeekTime(self, minLBA, maxLBA, nLoop, mode= 0):
      prm = self.params.TwoPointSeekTime.copy()

      prm['MINIMUM_LOCATION'] = lbaTuple(minLBA)
      prm['MAXIMUM_LOCATION'] = lbaTuple(maxLBA)
      prm['STEP_SIZE'] =  lbaTuple(maxLBA-minLBA)
      prm['NUM_SEEKS'] = nLoop

      self.St(prm)


      if not testSwitch.virtualRun:
         buff = self.dut.objSeq.SuprsDblObject['P549_IO_SK_TIME']
         buffVals = {
               'SnSkMinTm':buff[-1]['MIN_SEEK'],
               'SnSkMaxTm':buff[-1]['MAX_SEEK'],
               'SnSkAvgTm':buff[-1]['AVG_SEEK'],
               }
      else:
         buffVals = {'SnSkMinTm':0,'SnSkMaxTm':0,'SnSkAvgTm':0}

      retDict = PASS_RETURN.copy()
      retDict.update(buffVals)
      return retDict

   def ButterflySeekTime(self, stepsize, timeout, exc = 1):
      tempPrm = self.params.ButterflySeekTime.copy()            

      tempPrm.update({            
               "timeout": timeout,
            "STEP_SIZE" : lbaTuple(stepsize),
                  })
      try:         
         ret = self.St(tempPrm)
         return PASS_RETURN    
      except:
         return FAIL_RETURN.copy()       

   def ButterflySeek(self, minlba, maxlba, steplba, timeout, exc = 1):
      tempPrm = self.params.ButterflySeekTime.copy()            

      tempPrm.update({            
               "timeout": timeout,               
      "MINIMUM_LOCATION": lbaTuple(minlba),   
      "MAXIMUM_LOCATION": lbaTuple(maxlba),               
            "STEP_SIZE" : lbaTuple(steplba),
                  })
      try:         
         ret = self.St(tempPrm)         
         return PASS_RETURN    
      except:
         return FAIL_RETURN.copy()   
      
   def RandomSeekTime(self, minLBA, maxLBA, numSeeks, seekType = 28, timeout = 600, exc = 0):
      prm = self.params.RandomSeekTime.copy()

      prm['MINIMUM_LOCATION']    = lbaTuple(int(minLBA))
      prm['MAXIMUM_LOCATION']    = lbaTuple(int(maxLBA))
      prm['STEP_SIZE']           = lbaTuple(int(maxLBA-minLBA))
      prm['NUM_SEEKS']           = numSeeks
      prm['timeout']             = timeout

      self.St(prm)

      if not testSwitch.virtualRun:
         buff = self.dut.objSeq.SuprsDblObject['P549_IO_SK_TIME']
         buffVals = {
               'SnSkMinTm':buff[-1]['MIN_SEEK'],
               'SnSkMaxTm':buff[-1]['MAX_SEEK'],
               'SnSkAvgTm':buff[-1]['AVG_SEEK'],
               }
      else:
         buffVals = {'SnSkMinTm':0,'SnSkMaxTm':0,'SnSkAvgTm':0}

      retDict = PASS_RETURN.copy()
      retDict.update(buffVals)
      return retDict

   def SequentialSeek(self, startlba, endlba, steplba, sectorcount, exc = 1):
      tempPrm = self.params.SequentialSeek.copy()            

      tempPrm.update({            
            "MINIMUM_LOCATION" : lbaTuple(startlba),            
            "MAXIMUM_LOCATION" : lbaTuple(endlba),            
                   "STEP_SIZE" : lbaTuple(steplba),              
                  })
      try:         
         ret = self.St(tempPrm)
         data = self.dut.dblData.Tables('P549_IO_SK_TIME').tableDataObj()[-1]     
         data.update(PASS_RETURN)
         return data
      except:
         return FAIL_RETURN.copy()            

   def RandomSeek(self, startlba, endlba, minseccnt, maxseccnt, loopcount, stampFlag=0, compareFlag=0, timeout = None, exc = 1):
      tempPrm = self.params.RandomSeek.copy()            

      tempPrm.update({            
            "MINIMUM_LOCATION" : lbaTuple(startlba),            
            "MAXIMUM_LOCATION" : lbaTuple(endlba),            
                   "NUM_SEEKS" : loopcount,              
                  })
      try:         
         ret = self.St(tempPrm)
         data = self.dut.dblData.Tables('P549_IO_SK_TIME').tableDataObj()[-1]     
         data.update(PASS_RETURN)
         return data    
      except:
         return FAIL_RETURN.copy()      

   def FunnelSeek(self, startlba, endlba, steplba, sectorcount, exc = 1):
      tempPrm = self.params.FunnelSeek.copy()            

      tempPrm.update({            
            "MINIMUM_LOCATION" : lbaTuple(startlba),            
            "MAXIMUM_LOCATION" : lbaTuple(endlba),            
                   "STEP_SIZE" : lbaTuple(steplba),     
                "SECTOR_COUNT" : sectorcount          
                  })
      try:         
         ret = self.St(tempPrm)
         data = self.dut.dblData.Tables('P549_IO_SK_TIME').tableDataObj()[-1]     
         data.update(PASS_RETURN)
         return data    
      except:
         return FAIL_RETURN.copy()     

   def WriteSectors(self, start_LBA, num_LBAs):
      """Write sectors to Disk."""
      result = self.SequentialWriteDMAExt(start_LBA, start_LBA + num_LBAs)
      return result


   def ReadSectors(self, start_LBA, num_LBAs, *args, **kwargs):
      """Read Sectors from Disk"""
      result = self.SequentialReadDMAExt(start_LBA, start_LBA + num_LBAs)
      return result

   def setMaxXferRate(self):

      speedLookup = [
                        (6, 6), #6.0Gbs
                        (3, 3), #3.0Gbs
                        (1, 1.5), #1.5Gbs
                        ]
      rate = self.base_setMaxXferRate(speedLookup)

      #if rate == None:
      #   self.objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = False)  #Do spinup, sense, etc.
      #   #self.powerOff(offTime = 10,  driveOnly = 0)
      #  #self.powerOn(set5V=5000, set12V=12000, onTime=10, baudRate=PROCESS_HDA_BAUD, useESlip=1,  driveOnly = 0,  readyTimeLimit = self.readyTimeLimit, ataReadyCheck = 0)
      return rate
