#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements the CPC interface using test numbers (instead of intrinsic functions)
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001-2011 Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CPC_ICmd_TN.py $
# $Revision: #2 $
# $DateTime: 2016/09/20 03:10:55 $
# $Author: phonenaing.myint $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CPC_ICmd_TN.py#2 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from base_Initiator_CMD import initCmd, PASS_RETURN, FAIL_RETURN
import ScrCmds, time, struct, random
import MessageHandler as objMsg
import types
from Utility import CUtility
import binascii, traceback
from Rim import objRimType

#---------------------------------------------------------------------------------------------------------#
lbaTuple = CUtility.returnStartLbaWords
wordTuple = CUtility.ReturnTestCylWord

class CPC_ICmd_TN(initCmd):
   def __init__(self, params, objPwrCtrl):
      initCmd.__init__(self,  params, objPwrCtrl)
      self.passThroughList = ['SequentialWriteDMAExt',
                      'SequentialReadDMAExt',
                      'SequentialWRDMAExt',
                      'SequentialReadVerifyExt',
                      'ReverseWriteDMAExt',
                      'ReverseReadDMAExt',
                      'ZeroCheck',
                      'SequentialWriteVerify',
                      ]
      self.directCallList =  [
                      'StandbyImmed',
                      'Standby',
                      'FlushCache',
                      'FlushCacheExt',
                      'FlushMediaCache',
                      'WriteMIFDataToDisc',
                      'UnlockFactoryCmds',
                      'ClearFormatCorrupt',
                      'LongDST',
                      'ShortDST',
                     ]
      self.aliasList = {
      'SequentialWrite'          : 'SequentialWriteDMAExt',
      'SequentialWRDMA'          : 'SequentialWRDMAExt',
      'SequentialWriteDMA'       : 'SequentialWriteDMAExt',
      'SequentialReadDMA'        : 'SequentialReadDMAExt',
      'SequentialReadVerify'     : 'SequentialReadVerifyExt',
      'RandomWrite'              : 'RandomWriteDMAExt', 
      'RandomWRDMA'              : 'RandomWRDMAExt',
      'ReadVerify'               : 'ReadVerifySects',
      'ReadVerifyExt'            : 'ReadVerifySectsExt',
      }

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


      patMode = kwargs.pop('PATTERN_MODE')
      if 'CWORD2' in kwargs:
         patMode = kwargs.pop('CWORD2')

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

   def __override538Parms(self, args, kwargs):
      if 'LBA' in kwargs:
         lba = kwargs.pop('LBA')
         if type(lba) == tuple:
            lba = CUtility.returnStartLba(lba)
         kwargs['LBA_HIGH'], kwargs['LBA_MID'], kwargs['LBA_LOW'] = \
            CUtility.convertLBANumber2LBARegister(lba)
      return args, kwargs

   def __override510Parms(self, args, kwargs):

      kwargs = self.__overrideBlks(kwargs)

      #new cpc style params
      if 'WRITE_READ_MODE' in kwargs:
         wrmode = kwargs.pop('WRITE_READ_MODE')
         kwargs.setdefault('CTRL_WORD1', 0)
         kwargs['CTRL_WORD1'] |= (wrmode & 7) << 4

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
      elif test == 538 :
         args, kwds = self.__override538Parms(args,kwds)
      elif test == 551 and testSwitch.FE_0122934_231166_551_SUPPORT_IN_INIT:
         args, kwds = self.__override551Parms(args, kwds)
      elif test == 549 :
         args, kwds = self.__override549Parms(args,kwds)

      return args, kwds

   def overridePrmCall(self, STARTING_LBA, MAXIMUM_LBA, STEP_LBA = None, BLKS_PER_XFR = 256, \
                          STAMP_FLAG = 0, COMPARE_FLAG = 0, LOOP_COUNT = 1, DATA_PATTERN0 = None, timeout = 252000, exc = 1, stSuppressResults = False):
      """
      Generic interface command handler: implements standard interface for most commands
      """

      tempPrm = dict(getattr(self.params, self.prmName)) #create a copy
      
      if tempPrm.has_key('CTRL_WORD1') and tempPrm['CTRL_WORD1'] & 0x200:
         reverseCmd = True
      else:
         reverseCmd = False

      #TODO: Add compare flag handling
      tempPrm.update({
            'timeout' : timeout,
            'STARTING_LBA' : lbaTuple(STARTING_LBA) ,
            'BLKS_PER_XFR' : BLKS_PER_XFR,
            })
      if reverseCmd:
         tempPrm['BLKS_PER_XFR'] = STEP_LBA

      if testSwitch.FE_0128343_231166_STEP_SIZE_SUPPORT_IF3:
         if STEP_LBA != None:
            tempPrm['STEP_SIZE'] = lbaTuple(STEP_LBA)

      if DATA_PATTERN0 == None:
         tempPrm.pop('DATA_PATTERN0',0)
         tempPrm.pop('DATA_PATTERN1',0)
         tempPrm.pop('PATTERN_LSW', 0)
         tempPrm.pop('PATTERN_MSW', 0)
      else:
         tempPrm['DATA_PATTERN0'] = wordTuple(DATA_PATTERN0)


      if COMPARE_FLAG:
         tempPrm.update(self.params.Bit_to_Bit_cmp)
         tempPrm['FILL_WRITE_BUFFER'] = 1
         COMPARE_FLAG = False

      if self.ovrPrms:
         tempPrm.update(self.ovrPrms)

      '''if testSwitch.BF_0127477_231166_FIX_MAX_LBA_PER_CMD_INIT:
         if reverseCmd:
            totalBlocksXfr = LOOP_COUNT * (STARTING_LBA - MAXIMUM_LBA + 1 )
         else:
            totalBlocksXfr = LOOP_COUNT * (MAXIMUM_LBA - STARTING_LBA + 1 )
      else:
         if reverseCmd:
            totalBlocksXfr = LOOP_COUNT * (STARTING_LBA - MAXIMUM_LBA)
         else:
            totalBlocksXfr = LOOP_COUNT * (MAXIMUM_LBA - STARTING_LBA)'''

      if reverseCmd:
         totalBlocksXfr = LOOP_COUNT * (STARTING_LBA - MAXIMUM_LBA + 1)
      else:
         totalBlocksXfr = LOOP_COUNT * (MAXIMUM_LBA - STARTING_LBA + 1)

      tempPrm['TOTAL_BLKS_TO_XFR64'] = lbaTuple(totalBlocksXfr)

      if LOOP_COUNT > 1:
         tempPrm['MAXIMUM_LBA']  = lbaTuple(MAXIMUM_LBA)


      '''if testSwitch.BF_0127880_231166_ALWAYS_TRUNCATE_MAXLBA_TO_HDA_VAL:


         if self.maxlba == 0:
            self.GetMaxLBA()

         if MAXIMUM_LBA > self.maxlba and 'MAXIMUM_LBA' in tempPrm:
            tempPrm['MAXIMUM_LBA']  = lbaTuple(self.maxlba)

         elif not 'MAXIMUM_LBA' in tempPrm and (totalBlocksXfr + STARTING_LBA) > self.maxlba:
            #No loops so total + start can't exceed max lba
            totalBlocksXfr = self.maxlba - STARTING_LBA
            tempPrm['TOTAL_BLKS_TO_XFR64'] = lbaTuple(totalBlocksXfr)'''

      tempPrm.update({
            'retryECList' : [10100, 11173,],
            'retryCount'  : 1,
            'retryMode'   : HARD_RESET_RETRY,
         })

      if stSuppressResults:
         tempPrm['stSuppressResults'] = stSuppressResults
      
      ec = None
      try:
         ret = self.St(tempPrm)
      except ScriptTestFailure, failureData:
         ret = [0,0,0,0,0]
         ec = failureData[0][2]
         raise

      self.ovrPrms = {}
      
      #ret = self.translateStReturnToCPC(ret, ec)
      ret = self.translateStReturnToCPC(ret)

      return ret

   def fillIdentifyBuffer(self, refreshBuffer):
      if (len(self.IdentifyDeviceBuffer) < 204) or refreshBuffer:
         self.IdentifyDevice()

   def GetMaxLBA(self, refreshBuffer=True):
      """
      Get Max LBA from drive and return in CPC style dict {'LLRET':OK, 'MAX48':xxxx,'MAX28':xxxx}
      """

      self.fillIdentifyBuffer(refreshBuffer)

      #if testSwitch.BF_0127880_231166_ALWAYS_TRUNCATE_MAXLBA_TO_HDA_VAL:
      self.maxlba = CUtility.numSwap(self.IdentifyDeviceBuffer[200:205])
      return { 'LLRET':OK,
               'MAX48': "%X" % self.maxlba,
               'MAX28': "%X" % CUtility.numSwap(self.IdentifyDeviceBuffer[120:124]),
          }
      #else:
      #   return { 'LLRET':OK,
      #               'MAX48': "%X" % CUtility.numSwap(self.IdentifyDeviceBuffer[200:205]),
      #               'MAX28': "%X" % CUtility.numSwap(self.IdentifyDeviceBuffer[120:124]),
      #          }

   def GetModelNum(self, refreshBuffer=True):
      self.fillIdentifyBuffer(refreshBuffer)
      #if testSwitch.BF_0125626_231166_FIX_BUGS_SATA_ICMD_1:
      return CUtility.strSwap(self.IdentifyDeviceBuffer[ 54: 94], stripWhitespace = False)
      #else:
      #   return CUtility.__strSwap(data[ 54: 94], stripWhitespace = False)


   def ZeroCheck(self, minLBA, maxLBA, scnt):
      prm = self.params.ZeroCheck.copy()

      prm['DATA_PATTERN0'] = (0,0)
      prm['STARTING_LBA'] = lbaTuple(minLBA)
      prm['TOTAL_BLKS_TO_XFR64'] = lbaTuple(maxLBA-minLBA)

      ret = self.St(prm)
      return self.translateStReturnToCPC(ret)

   def GetDriveSN(self):
      return CUtility.strSwap(self.IdentifyDeviceBuffer[ 20: 40])

   def St(self, *args, **kwargs):
      """
      Provides the st interface with CPC to SI parameter overrides
      """
      args, kwargs = self.__overrideTestParms(args, kwargs)

      return initCmd.St(self, *args, **kwargs)


   def HardReset(self, exc = 1):
      initCmd.HardReset(self)
      return {'LLRET':0,}

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

   def SmartOffLineImmed(self, subcmd):
      tempPrm = dict(self.params.SmartParameter)
      tempPrm.update({
            'FEATURES': 0xD4,
            'LBA_LOW': subcmd,
            'prm_name': "SmartOffLineImmed",
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN        

   def SmartEDAutoSave(self, feature):
      tempPrm = dict(self.params.SmartParameter)
      tempPrm.update({
            'FEATURES': 0xD2,
            'SECTOR_COUNT': feature,
            'prm_name': "SmartEDAutoSave",
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN    
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
      kwargs['ovPrm'] = ovPrm
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

   def SmartDisableOper(self, timeout = 300, exc = 1):
      self.HardReset()
      tempPrm = dict(self.params.SmartParameter)
      tempPrm.update({
            'FEATURES': 0xD9,
            'prm_name': "SmartDisableOper",
            'timeout': timeout,
         })                  
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN    

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
            'DblTablesToParse' : ['P5XX_TFREG_LBA','P5XX_TFREGEXT'],
            'stSuppressResults' : ST_SUPPRESS__ALL,
         })
      if testSwitch.virtualRun:
         return {'LLRET':0,'LBA': 0xc24f00}
      else:
         self.St(tempPrm)
         if testSwitch.virtualRun:
            ret = {'ERR_REG': '0', 'STATUS': '0x50', 'LBA_UPPER': '0', 'LBA_LOWER': '0', 'SCNT': '0', 'DEV': '0'}
         else:
            '''if testSwitch.FE_DBLog2 == 1:
               from DBLog2 import getRowFromTable
               ret = getRowFromTable( 'P5XX_TFREGEXT', -1 ).copy()
            else:
               if 'P5XX_TFREG_LBA' in self.dut.objSeq.SuprsDblObject:
                  ret = self.dut.objSeq.SuprsDblObject['P5XX_TFREG_LBA'][-1].copy()
                  del self.dut.objSeq.SuprsDblObject['P5XX_TFREG_LBA']
               else:
                  ret = self.dut.objSeq.SuprsDblObject['P5XX_TFREGEXT'][-1].copy()
                  del self.dut.objSeq.SuprsDblObject['P5XX_TFREGEXT']'''

            if 'P5XX_TFREG_LBA' in self.dut.objSeq.SuprsDblObject:
               objMsg.printMsg("Debug0: SuprsDblObject %s"%self.dut.objSeq.SuprsDblObject)
               ret = self.dut.objSeq.SuprsDblObject['P5XX_TFREG_LBA'][-1].copy()
               del self.dut.objSeq.SuprsDblObject['P5XX_TFREG_LBA']
            else:
               objMsg.printMsg("Debug1: SuprsDblObject %s"%self.dut.objSeq.SuprsDblObject)
               ret = self.dut.objSeq.SuprsDblObject['P5XX_TFREGEXT'][-1].copy()
               del self.dut.objSeq.SuprsDblObject['P5XX_TFREGEXT']

            if ret.has_key('LBA'):
               ret['LBA'] = int(ret['LBA'], 16)
            ret['LLRET'] = 0
            return ret

   def SmartCheck(self, timeout = 300, exc = 1):   
      try:
         self.SmartEnableOper()
         self.SmartReadData()
         self.SmartReturnStatus()
         return PASS_RETURN         
      except:      
         return FAIL_RETURN
		 
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
      tempPrm['BUFFER_LENGTH'] = (0x99,0xFFFF)

      if buffNum & WBF:
         tempPrm['CTRL_WORD1'] = (0x0000,)
         tempPrm['prm_name'] = 'Write Pattern to Write Buffer'
         status = self.St(tempPrm)
      if buffNum & RBF:
         tempPrm['CTRL_WORD1'] = (0x0001,)
         tempPrm['prm_name'] = 'Write Pattern to Read Buffer'
         status = self.St(tempPrm)

      return {'LLRET':OK}

   def FillBuffByte(self, buffFlag, data, byteOffset = 0, byteCount = None):
      tempPrm = dict(self.params.WritePatternToBuffer) #create a copy

      if len(data) > 16:
         data = data[:16]      #SI supports only 16 nibbles hex character   
   
      if len(data) > 8:   
         tempPrm['DATA_PATTERN0'] = wordTuple( int(data[:8], 16 ) << (32-(len(data[:8])*4)))
         tempPrm['DATA_PATTERN1'] = wordTuple( int(data[8:], 16 ) << (32-(len(data[8:])*4)))
      else:
         tempPrm['DATA_PATTERN0'] = wordTuple( int(data[:8], 16) << (32-(len(data)*4)))    
      
      tempPrm['BIT_PATTERN_LENGTH'] = len(data)*4
      tempPrm['BYTE_OFFSET'] = wordTuple(byteOffset)
            
      if byteCount == None:
         tempPrm['BUFFER_LENGTH'] = self.buffSize[buffFlag]
      else:
         tempPrm['BUFFER_LENGTH'] = wordTuple(byteCount)

      if buffFlag & WBF:
         tempPrm['CTRL_WORD1'] = (0x000C,)
         tempPrm['prm_name'] = 'Write Pattern to Write Buffer'
      if buffFlag & RBF:
         tempPrm['CTRL_WORD1'] = (0x000D,)
         tempPrm['prm_name'] = 'Write Pattern to Read Buffer'         

      try:
         status = self.St(tempPrm)    
         return PASS_RETURN 
      except:
         return FAIL_RETURN     


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
            return FAIL_RETURN
            
      return PASS_RETURN 
      
   def FillBuffRandom(self,  buffFlag, byteOffset, byteCount = None, exc = 1):
      """
      Fill the write buffer with random data
      """
      tempPrm = dict(self.params.WritePatternToBuffer) #create a copy

      tempPrm['BYTE_OFFSET'] = wordTuple(byteOffset)      
      tempPrm['PATTERN_TYPE'] = 1 #Random Pattern
      if byteCount == None:
         tempPrm['BUFFER_LENGTH'] = self.buffSize[buffFlag]
      else:
         tempPrm['BUFFER_LENGTH'] = wordTuple(byteCount)

      if buffFlag & WBF:
         tempPrm['CTRL_WORD1'] = (0x0000,)
         tempPrm['prm_name'] = 'Write RANDOM Pattern to Write Buffer'         
      if buffFlag & RBF:
         tempPrm['CTRL_WORD1'] = (0x0001,)
         tempPrm['prm_name'] = 'Write RANDOM Pattern to Read Buffer'
                  
      try:
         status = self.St(tempPrm)    
         return PASS_RETURN 
      except:
         return FAIL_RETURN     

   def FillBuffInc(self,  buffFlag, byteOffset, byteCount = None, exc = 1):
      """
      Fill the write buffer with random data
      """
      tempPrm = dict(self.params.WritePatternToBuffer) #create a copy

      tempPrm['BYTE_OFFSET'] = wordTuple(byteOffset)      
      tempPrm['PATTERN_TYPE'] = 2 #Increment Pattern
      if byteCount == None:
         tempPrm['BUFFER_LENGTH'] = self.buffSize[buffFlag]
      else:
         tempPrm['BUFFER_LENGTH'] = wordTuple(byteCount)

      if buffFlag & WBF:
         tempPrm['CTRL_WORD1'] = (0x0000,)
         tempPrm['prm_name'] = 'Write RANDOM Pattern to Write Buffer'         
      if buffFlag & RBF:
         tempPrm['CTRL_WORD1'] = (0x0001,)
         tempPrm['prm_name'] = 'Write RANDOM Pattern to Read Buffer'
                  
      try:
         status = self.St(tempPrm)    
         return PASS_RETURN 
      except:
         return FAIL_RETURN            
                        
   def FillBuffDec(self,  buffFlag, byteOffset, byteCount = None, exc = 1):
      """
      Fill the write buffer with random data
      """
      tempPrm = dict(self.params.WritePatternToBuffer) #create a copy

      tempPrm['BYTE_OFFSET'] = wordTuple(byteOffset)      
      tempPrm['PATTERN_TYPE'] = 3 #Decrement Pattern
      if byteCount == None:
         tempPrm['BUFFER_LENGTH'] = self.buffSize[buffFlag]
      else:
         tempPrm['BUFFER_LENGTH'] = wordTuple(byteCount)

      if buffFlag & WBF:
         tempPrm['CTRL_WORD1'] = (0x0000,)
         tempPrm['prm_name'] = 'Write RANDOM Pattern to Write Buffer'         
      if buffFlag & RBF:
         tempPrm['CTRL_WORD1'] = (0x0001,)
         tempPrm['prm_name'] = 'Write RANDOM Pattern to Read Buffer'
                  
      try:
         status = self.St(tempPrm)    
         return PASS_RETURN 
      except:
         return FAIL_RETURN            
            
   def FillBuffer(self, buffFlag , byteOffset, data):
      import binascii
      tempPrm = {
        'test_num':     508,
        'prm_name':     'WritePatternToBuffer',
        'timeout':      600,
        'CTRL_WORD1':   0x0,
        'PATTERN_TYPE': 0,
        'BUFFER_LENGTH': (0,8),
        'BYTE_OFFSET':  (0,0),
        'DATA_PATTERN0':(0,0),
        'DATA_PATTERN1':(0,0),
        'BYTE_PATTERN_LENGTH': (8),
        }

      dataSize = len(data)
      objMsg.printMsg("PN: dataSize: %s" % dataSize)
      objMsg.printMsg("PN: data: %s" % (data))

      bytesSent = 0
      rbyte = 0
      if buffFlag == 1:
         tempPrm['CTRL_WORD1'] = 0x0002
      elif buffFlag == 2:
         tempPrm['CTRL_WORD1'] = 0x0003

      while bytesSent < dataSize:
         rbyte = dataSize - bytesSent
         if rbyte > 8:
            tempdata = data[bytesSent: bytesSent + 8]
            tempPrm['BUFFER_LENGTH'] = (0,8)
         else:
            tempdata = data[bytesSent: bytesSent + rbyte] + (8 - rbyte) * '0' #zero padding
            tempPrm['BUFFER_LENGTH'] = (0, rbyte)

         w0 = int("0x" + binascii.hexlify(tempdata[0]) + binascii.hexlify(tempdata[1]),16)
         w1 = int("0x" + binascii.hexlify(tempdata[2]) + binascii.hexlify(tempdata[3]),16)
         w2 = int("0x" + binascii.hexlify(tempdata[4]) + binascii.hexlify(tempdata[5]),16)
         w3 = int("0x" + binascii.hexlify(tempdata[6]) + binascii.hexlify(tempdata[7]),16)         
         tempPrm['DATA_PATTERN0'] = (w0, w1)
         tempPrm['DATA_PATTERN1'] = (w2, w3)
         tempPrm['BYTE_OFFSET'] = (0, bytesSent + byteOffset)
         self.St(tempPrm)
         bytesSent = bytesSent + 8

      return {'LLRET':OK}

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

      if testSwitch.virtualRun: #PN: 07Mar2013
         DSTStatus = 0
      else:
         objMsg.printMsg("Debug: self.dut.dblData.Tables('P600_SELF_TEST_STATUS') %s"%self.dut.dblData.Tables('P600_SELF_TEST_STATUS'))
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
         return FAIL_RETURN      
   

   def ReadLong(self, lba, exc = 1):
      prm = self.params.ReadLong.copy()

      prm['LBA'] = CUtility.returnStartLbaWords( lba )
      prm['stSuppressResults'] = ST_SUPPRESS__ALL | ST_SUPPRESS_SUPR_CMT

      ret = self.St(prm)
      if exc:
         return {'LLRET': OK}
      else:
         return self.translateStReturnToCPC(ret)         

   def WriteLong(self, lba, exc = 1):
      prm = self.params.WriteLong.copy()

      prm['LBA'] = CUtility.returnStartLbaWords( lba )
      prm['stSuppressResults'] = ST_SUPPRESS__ALL | ST_SUPPRESS_SUPR_CMT

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
      prm["FINAL_ASSEMBLY_DATE"] = (0,0,param4, param5)

      self.St(prm,TEST_FUNCTION=(0))  # Write Final assembly date
      self.St(prm,TEST_FUNCTION=(1))  # Read  Final assembly date
      self.St(prm,TEST_FUNCTION=(2))  # Compare Final assembly date

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
         'BLKS_PER_XFR': BlksPerXfr,
         'WRITE_READ_MODE': xferType,
      })

      prm.update({'timeout': 600*(TotalBlksXfr/40000000+1),})

      try:
         ret = self.translateStReturnToCPC( self.St(prm) )
         if testSwitch.virtualRun:
            return {'LLRET': 0, 'SCNT': 0, 'HEAD': 0, 'ERR': 0, 'TXRATE': '100', 'DEV': 64, 'LBA': 4385491, 'STS': 80, 'SCTR': 211, 'ENDLBA': '625142446', 'CYL': 17130}
         else:
            data = self.dut.dblData.Tables('P641_DMAEXT_TRANSFER_RATE').tableDataObj()[-1]
            ret.update({'ENDLBA': data['END_LBA'], 'TXRATE': data['XFER_RATE_MB_PER_SEC'], 'LBA_CNT': data['LBA_CNT'], 'START_LBA': data['START_LBA'],})
            return ret
      except:      
         return FAIL_RETURN 

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
      stat = self.St(prm)
      ret = self.dut.objSeq.SuprsDblObject['P5XX_TFREG_CHS'][-1].copy()
      del self.dut.objSeq.SuprsDblObject['P5XX_TFREG_CHS']
      return self.directTranslateStReturnToCPC(stat, ret)
   
   def WriteBuffer(self, exc = 1):
      tempPrm = self.params.WriteBuffer.copy()
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN  

   def ReadBuffer(self, exc = 1):
      tempPrm = self.params.ReadBuffer.copy()
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN  

   def ExecDeviceDiag(self, exc = 1):
      tempPrm = self.params.ExecDeviceDiag.copy()
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN 

   def WriteSectors(self,lba,sectorCount, exc = 1):
      tempPrm = self.params.WriteSectors.copy()
      tempPrm.update({
            'SECTOR_COUNT': sectorCount,
            'LBA': CUtility.returnStartLbaWords( lba ),
         })         
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN        
      
   def ReadSectors(self,lba,sectorCount, exc = 1):   
      tempPrm = self.params.ReadSectors.copy()
      tempPrm.update({
            'SECTOR_COUNT': sectorCount,
            'LBA': CUtility.returnStartLbaWords( lba ),
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN        
      
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
         return FAIL_RETURN      
      
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
         return FAIL_RETURN    

   def ReadVerifySects(self,lba,sectorCount, exc = 1):
      tempPrm = self.params.ReadVerifySects.copy()
      tempPrm.update({
            'SECTOR_COUNT': sectorCount,
            'LBA': CUtility.returnStartLbaWords( lba ),
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN      

   def ReadVerifySectsExt(self,lba,sectorCount, exc = 1):
      tempPrm = self.params.ReadVerifySectsExt.copy()
      tempPrm.update({
            'SECTOR_COUNT'       : sectorCount,
            'LBA'                : CUtility.returnStartLbaWords( lba ),
            'stSuppressResults'  : ST_SUPPRESS__ALL | ST_SUPPRESS_SUPR_CMT
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN         
      
   def SetMultipleMode(self,sectorCount, exc = 1):
      tempPrm = self.params.SetMultipleMode.copy()
      tempPrm.update({
            'SECTOR_COUNT': sectorCount,
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN            
      
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
         return FAIL_RETURN               
            

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
         return FAIL_RETURN             


   def WriteDMALBA(self,lba,sectorCount, exc = 1):
      tempPrm = self.params.WriteDMALBA.copy()
      tempPrm.update({
            'SECTOR_COUNT': sectorCount,
            'LBA': CUtility.returnStartLbaWords( lba ),
         })         
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN              
            

   def ReadDMALBA(self,lba,sectorCount, exc = 1):
      tempPrm = self.params.ReadDMALBA.copy()
      tempPrm.update({
            'SECTOR_COUNT': sectorCount,
            'LBA': CUtility.returnStartLbaWords( lba ),
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN    


   def InitDeviceParms(self,maxHead,sctpertrack, exc = 1):
      tempPrm = self.params.InitDeviceParms.copy()
      tempPrm.update({
            'SECTOR_COUNT': sctpertrack,
            'HEAD': maxHead,     
         })
      try:   
         ret = self.St(tempPrm)         
         return PASS_RETURN          
      except:
         return FAIL_RETURN            
            

   def SecuritySetPassword(self,identifier,password,securityLevel,masterPWRevCode, exc = 1):
      """
      Set Security Password for KWAI Test
      """
            
      CtrlWord1 = str(int(identifier)) + str(int(securityLevel))      
      password = str(password)      
      
      masterRevByte1 = hex(masterPWRevCode & 0xff)[2:]
      masterRevByte2 = hex((masterPWRevCode & 0xff00) >> 8)[2:]
      masterRev = str(masterRevByte2 + masterRevByte1)      
      
      PasswordData = CtrlWord1 + password + masterRev

      self.ClearBinBuff()
      self.FillBuffer(WBF,0,PasswordData)
      self.GetBuffer(WBF,0,512)      
            
      tempPrm = self.params.SecuritySetPassword.copy()                  
      ret = self.translateStReturnToCPC(self.St(tempPrm))
      return ret          


   def SecurityEraseUnit(self,identifier,password,eraseMode, exc = 1):
      """
      Security Erase Unit for KWAI Test
      """            
      identifier = identifier & 0x1 #Bit 0
      eraseMode = (eraseMode & 0x1) << 1 #Bit1
      CtrlWord1 = identifier | eraseMode

      temp1 = hex(CtrlWord1 & 0xff)[2:]
      temp2 = hex((CtrlWord1 & 0xff00) >> 8)[2:]
      CtrlWord1 = str(temp1 + temp2)

      EraseUnit = str(CtrlWord1) + str(password)
            
      self.ClearBinBuff() 
      self.FillBuffer(WBF,0,EraseUnit)
      self.GetBuffer(WBF,0,512)       
           
      tempPrm = self.params.SecurityEraseUnit.copy()
      ret = self.translateStReturnToCPC(self.St(tempPrm))
      return ret      


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
         return FAIL_RETURN    
      

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
      self.SequentialWRDMAExt(minSeqLBA1, maxSeqLBA1-1, seqScnt1, seqScnt1, DATA_PATTERN0 = int(patData,16), COMPARE_FLAG = 1)
      self.HardReset()       
      self.FlushCache()      
      self.HardReset()
      self.IdleImmediate()       
      time.sleep(msDelay/100)            
      lastLBA = (maxSeqLBA1 - seqScnt1) - 1
      lastScnt = seqScnt1 #Where lastLBA and lastScnt are the LBA and sector count from the last command send during SequentialWRDMAExt().      
      self.SequentialReadDMAExt(lastLBA, lastLBA+lastScnt-1, lastScnt, lastScnt, DATA_PATTERN0 = int(patData,16), COMPARE_FLAG = 1) #ReadDMAExt( lastLBA, lastScnt )
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
         data.update(PASS_RETURN)
         return data    
      except:
         return FAIL_RETURN


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
         return FAIL_RETURN
      
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
         return FAIL_RETURN       


   def BluenunScan(self, start_lba, end_lba, sect_cnt, timeout, cmdPerSample=4, blueNunLogTmo=0, maxTotalRetry=0, maxGroupRetry=0, exc = 1):
      tempPrm = self.params.BluenunScan.copy()            
      
      CTRL_WORD1 = tempPrm["CTRL_WORD1"] | (blueNunLogTmo << 7)      

      tempPrm.update({      
              "CTRL_WORD1": CTRL_WORD1,
            "STARTING_LBA": lbaTuple(start_lba),
            "MAXIMUM_LBA" : lbaTuple(end_lba),
           "BLKS_PER_XFR" : sect_cnt,        
        "COMMAND_TIMEOUT" : wordTuple(timeout),
            "SAMPLE_SIZE" : cmdPerSample,            
           "TOTAL_RETRIES": maxTotalRetry,
           "GROUP_RETRIES": maxGroupRetry,     
         })
      try:         
         ret = self.St(tempPrm)
         data = self.dut.dblData.Tables('P639_BLUENUNSCAN').tableDataObj()[-1]          
         data.update(PASS_RETURN)
         return data    
      except:
         return FAIL_RETURN       

 
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
            return FAIL_RETURN


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

      try:
         self.dut.dblData.delTable('P_CCT_DISTRIBUTION', forceDeleteDblTable = 1)     #Clear P_CCT_DISTRIBUTION table before do CCT
      except:
         #except:  pass  
         objMsg.printMsg('Delete table P_CCT_DISTRIBUTION fail')

      self.UnlockFactoryCmds()
      try:
         ret = self.translateStReturnToCPC(self.St(ovPrm))
         if testSwitch.virtualRun:
            return {'LLRET': 0, 'LBA': '0x00000000746FD087', 'ERR': '0', 'RES': '', 'DEV': '64', 'SCNT': '0', 'RESULT': 'IEK_OK:No error', 'STS': '80', 'THR1': '0', 'THR2': '0', 'THR0': '0', 'CT': '69537'}
         else:
            data = self.dut.dblData.Tables('P_CCT_DISTRIBUTION').tableDataObj()
            for entry in data:
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
         return FAIL_RETURN


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
                  }
      WRDMAExtNum = {
            'ReadDMAExt' : 1,
            'WriteDMAExt': 2,
                  }
      for key in WRDMAExt:
         if WRDMAExt[key] == wrCmd:
            wrmode = WRDMAExtNum[key]
            break
      return wrmode


      
   def RandomCCT(self, Cmd1, STARTING_LBA, MAXIMUM_LBA, BLKS_PER_XFR = 256, CMDCNT = 1, \
                     minthd = 0, midthd = 0, maxthd = 0, COMPARE_FLAG = 0, Cmd2 = 0, exc = 1, spcid = None):                     
      if Cmd1 == 0x35 and Cmd2 == 0:                  
         tempPrm = self.params.RandomWriteDMAExt.copy()    
      elif Cmd1 == 0x25 and Cmd2 == 0:
         tempPrm = self.params.RandomReadDMAExt.copy()      
      elif Cmd1 in [0x35,0x25] and Cmd2 <> 0:
         tempPrm = self.params.RandomWRDMAExt.copy()      
               
      if spcid != None:
         tempPrm.update({'spc_id' : spcid})
      tempPrm.update({            
           "STARTING_LBA"      : lbaTuple(int(STARTING_LBA)),              
           "MAXIMUM_LBA"       : lbaTuple(int(MAXIMUM_LBA)),
           "BLKS_PER_XFR"      : BLKS_PER_XFR,        
           "CCT_BIN_SETTINGS"  : 0x3246, 
           "DATA_PATTERN0"     : (0,0),        
           "MAX_NBR_ERRORS"    : 0xFFFF, #Collect all data
           "RESET_AFTER_ERROR" : 1,
           "CCT_LBAS_TO_SAVE"  : 0x32,
           "MAX_COMMAND_TIME"  : 0x2710,
         })                           
      tempPrm['TOTAL_BLKS_TO_XFR64'] = lbaTuple(CMDCNT * tempPrm['BLKS_PER_XFR'])   
                                 
      args,tempPrm = self.__override510Parms(0,tempPrm)
      tempPrm['CTRL_WORD2'] |= 0x4000            #Enable CCT timing
      tempPrm['display_info'] = True

      try:         
         self.UnlockFactoryCmds()
         ret = self.St(tempPrm)                
         CCT_DATA = self.dut.dblData.Tables('P_CCT_DISTRIBUTION').tableDataObj()
         objMsg.printMsg("Debug: Random CCT CCT_DATA= %s" %str(CCT_DATA))         
         Thr0 = 0           
         Thr1 = 0         
         Thr2 = 0
         for item in CCT_DATA:                
            if item['TEST_SEQ_EVENT'] == self.dut.objSeq.getTestSeqEvent(510):                
               if int(item['BIN_THRESHOLD']) > minthd and int(item['BIN_THRESHOLD']) <= midthd:
                  Thr0 += int(item['BIN_ENTRIES'])        
               if int(item['BIN_THRESHOLD']) > midthd and int(item['BIN_THRESHOLD']) <= maxthd:
                  Thr1 += int(item['BIN_ENTRIES'])               
               if int(item['BIN_THRESHOLD']) > maxthd: 
                  Thr2 += int(item['BIN_ENTRIES'])
         return {'LLRET':0, 'THR0':Thr0, 'THR1':Thr1, 'THR2':Thr2}          
      except:
         return FAIL_RETURN   


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
         return FAIL_RETURN       


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
         return FAIL_RETURN       


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
         return FAIL_RETURN            


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
         return FAIL_RETURN       

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

   def IdleAPM_TTR(self, delay, minLba, maxLba, scnt, loopCnt, exc = 1):   
      # CPC Algo
      #Loop for loopCount
      #| | Delay ()
      #| | Lba = random (minLBA, maxLBA)
      #| | ReadDMA (lba, sectorCount) 	----- step1
      #| | lba = random (minLBA, maxLBA)
      #| | WriteDMA (lba, sectorCount)  ------ step2
      #| | FlushCache ()
      #| |_ ReadDMA (lba, sectorCount)  ------ step3            
      self.ClearBinBuff()       
      self.HardReset()
      for loop in range(loopCnt):      
         objMsg.printMsg('*'*10 + "Loop Count: %d" %loop + '*'*10) 
         try:                  
            time.sleep(delay)            
            Lba = random.randrange(minLba, maxLba)            
            self.ReadDMALBA(Lba,scnt)            
            Lba = random.randrange(minLba, maxLba)
            self.WriteDMALBA(Lba,scnt)              
            self.FlushCache()            
            self.ReadDMALBA(Lba,scnt)            
         except:
            return FAIL_RETURN       
      return PASS_RETURN                 



   def SequentialCCT(self, Cmd1, STARTING_LBA, MAXIMUM_LBA, BLKS_PER_XFR = 256, STEP_LBA = 256, \
                     minthd = 0, midthd = 0, maxthd = 0, COMPARE_FLAG = 0, Cmd2 = 0, exc = 1, spcid = None):                     
      if Cmd1 == 0x35 and Cmd2 == 0:                  
         tempPrm = self.params.SequentialWriteDMAExt.copy()    
      elif Cmd1 == 0x25 and Cmd2 == 0:
         tempPrm = self.params.SequentialReadDMAExt.copy()      
      elif Cmd1 == 0x42 and Cmd2 == 0:
         tempPrm = self.params.SequentialReadVerifyExt.copy()
      elif Cmd1 in [0x35,0x25] and Cmd2 <> 0:
         tempPrm = self.params.SequentialWRDMAExt.copy()      
               
      tempPrm.update({     
           "CCT_BIN_SETTINGS"    : 0x3246,       
           "STARTING_LBA"        : lbaTuple(int(STARTING_LBA)),                      
           "BLKS_PER_XFR"        : BLKS_PER_XFR,        
           "STEP_SIZE"           : lbaTuple(STEP_LBA), 
           "TOTAL_BLKS_TO_XFR64" : lbaTuple(int(MAXIMUM_LBA - STARTING_LBA+1)),
           "DATA_PATTERN0"       : (0,0),        
           "MAX_NBR_ERRORS"      : 0xFFFF, #Collect all data
           "RESET_AFTER_ERROR"   : 1, 
           "CCT_LBAS_TO_SAVE"    : 0x32,
           "MAX_COMMAND_TIME"    : 0x2710,     
         }) 
                        
      if spcid != None:
         tempPrm.update({'spc_id' : spcid})
                  
      args,tempPrm = self.__override510Parms(0,tempPrm)
      tempPrm['CTRL_WORD2'] |= 0x4000            #Enable CCT timing
      tempPrm['display_info'] = True

      try:         
         self.UnlockFactoryCmds()
         ret = self.St(tempPrm)                
         CCT_DATA = self.dut.dblData.Tables('P_CCT_DISTRIBUTION').tableDataObj()         
         Thr0 = 0           
         Thr1 = 0         
         Thr2 = 0
         for item in CCT_DATA:                
            if item['TEST_SEQ_EVENT'] == self.dut.objSeq.getTestSeqEvent(510):              
               if int(item['BIN_THRESHOLD']) > minthd and int(item['BIN_THRESHOLD']) <= midthd:
                  Thr0 += int(item['BIN_ENTRIES'])        
               if int(item['BIN_THRESHOLD']) > midthd and int(item['BIN_THRESHOLD']) <= maxthd:
                  Thr1 += int(item['BIN_ENTRIES'])               
               if int(item['BIN_THRESHOLD']) > maxthd: 
                  Thr2 += int(item['BIN_ENTRIES'])
         return {'LLRET':0, 'THR0':Thr0, 'THR1':Thr1, 'THR2':Thr2}          
      except:
         return FAIL_RETURN     


   def SeqDelayWR(self, startLba, endLba, scnt, minDelay, maxDelay, stepDelay, groupSize, BitMode = 48, modeRW = 1, exc = 1):
      tempPrm = self.params.SeqDelayWR.copy()            
            
      if modeRW:      
         tempPrm.update({
                  'WRITE_READ_MODE': modeRW})                  

      tempPrm.update({            
                   "STARTING_LBA" : lbaTuple(startLba),            
            "TOTAL_BLKS_TO_XFR64" : lbaTuple(int(endLba - startLba+1)),            
             "FIXED_SECTOR_COUNT" : scnt,        
             "MIN_DELAY_TIME"     : minDelay,  
             "MAX_DELAY_TIME"     : maxDelay,  
             "STEP_DELAY_TIME"    : stepDelay,               
             "GROUP_SIZE"         : groupSize,             
                  })
      try:         
         ret = self.St(tempPrm)
         return PASS_RETURN    
      except:
         return FAIL_RETURN           
            

   def SequentialWRCopy(self, startRdLBA, startWrLBA, rangeLBA, sectorCount, exc = 1):       
      tempPrm = self.params.SequentialWRCopy.copy()

      tempPrm.update({            
            "START_READ_LBA" : lbaTuple(startRdLBA),            
           "START_WRITE_LBA" : lbaTuple(startWrLBA),            
       "TOTAL_BLKS_TO_XFR64" : lbaTuple(rangeLBA),                     
       "FIXED_SECTOR_COUNT"  : sectorCount,
                  })
      try:         
         ret = self.St(tempPrm)
         return PASS_RETURN    
      except:
         return FAIL_RETURN  

   def TwoPointSeekTime(self, minLBA, maxLBA, nLoop, mode):
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

   def downloadIORimCode(self, forced = False):
      objMsg.printMsg("PN: In CPC_ICmd_TN.py DownloadIORimCode") #PN: cpcv3, merg
      pass

   def CommandLocation(self, *args, **kwargs):
      return ICmd.CommandLocation(*args, **kwargs)

   def PowerOnTiming(self, *args, **kwargs):
      return ICmd.PowerOnTiming(*args, **kwargs)

   def StatusCheck(self, *args, **kwargs):
      return ICmd.StatusCheck(*args, **kwargs)

   def ReceiveSerialCtrl(self, *args, **kwargs):
      return ICmd.ReceiveSerialCtrl(*args, **kwargs)
      
   def GetPwrOnSpinUpTime(self, *args, **kwargs):
      return ICmd.GetPwrOnSpinUpTime(*args, **kwargs)
      
   def NCQSequentialReadDMA(self, startLBA, endLBA, sectorCount, stepLBA):
      tempPrm = self.params.NCQSequentialReadDMA.copy()

      tempPrm.update({
         "MINIMUM_LBA" : lbaTuple(startLBA),
         "MAXIMUM_LBA" : lbaTuple(endLBA),
         "MIN_SECTOR_COUNT" : (sectorCount),
      })
      try:
         ret = self.St(tempPrm)
         return PASS_RETURN
      except:
         return FAIL_RETURN

   def NCQSequentialWriteDMA(self, startLBA, endLBA, sectorCount, stepLBA):
      tempPrm = self.params.NCQSequentialWriteDMA.copy()

      tempPrm.update({
         "MINIMUM_LBA" : lbaTuple(startLBA),
         "MAXIMUM_LBA" : lbaTuple(endLBA),
         "MIN_SECTOR_COUNT" : (sectorCount),
      })
      try:
         ret = self.St(tempPrm)
         return PASS_RETURN
      except:
         return FAIL_RETURN

   def NCQRandomReadDMA(self, startLBA, endLBA, minSectorCount, maxSectorCount, count):
      tempPrm = self.params.NCQRandomReadDMA.copy()

      tempPrm.update({
         "MINIMUM_LBA" : lbaTuple(startLBA),
         "MAXIMUM_LBA" : lbaTuple(endLBA),
         "MIN_SECTOR_COUNT" : (minSectorCount),
         "MAX_SECTOR_COUNT" : (maxSectorCount),
         "LOOP_COUNT" : (count),
      })
      try:
         ret = self.St(tempPrm)
         return PASS_RETURN
      except:
         return FAIL_RETURN

   def NCQRandomWriteDMA(self, startLBA, endLBA, minSectorCount, maxSectorCount, count):
      tempPrm = self.params.NCQRandomWriteDMA.copy()

      tempPrm.update({
         "MINIMUM_LBA" : lbaTuple(startLBA),
         "MAXIMUM_LBA" : lbaTuple(endLBA),
         "MIN_SECTOR_COUNT" : (minSectorCount),
         "MAX_SECTOR_COUNT" : (maxSectorCount),
         "LOOP_COUNT" : (count),
      })
      try:
         ret = self.St(tempPrm)
         return PASS_RETURN
      except:
         return FAIL_RETURN

   def ReadDMAExt(self, startLBA, sectorCount, errCode):
      return self.SequentialReadDMAExt(startLBA, startLBA + (sectorCount - 1), sectorCount, sectorCount)

   def SetProductID (self, PROD_ID = 0):
      prm506 = self.params.SetProductID
      prm506['PROD_ID'] = PROD_ID
      self.St(prm506)

   def getRimCodeVer(self):
      """
      Get the rim code version from CPC
      """
      tempPrm = {
         'test_num'              : 535,
         'prm_name'              : 'prm_535_CPCRev',
         'timeout'               : 30,
         'CTRL_WORD1'            : 0,
         'DblTablesToParse'      : ['P535_VERSION_INFO',],
         }

      self.St(tempPrm)

      if testSwitch.virtualRun:
         ret = ''
      else:
         ret = self.dut.objSeq.SuprsDblObject['P535_VERSION_INFO'][-1]['CPC_VERSION']

      objMsg.printMsg("RimCodeVer %s"% str(ret))
      return ret

