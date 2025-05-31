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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_Initiator_CMD.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_Initiator_CMD.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from Test_Switches import testSwitch
from base_ICmd import base_ICmd
import ScrCmds
from Utility import CUtility
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import types
from random import randint
from Rim import theRim
import os
from sptCmds import objComMode
import base_BaudFunctions
from Cell import theCell
from Rim import objRimType
from Drive import objDut
dut = objDut

try:    import cPickle as myPickle
except: import pickle as myPickle

lbaTuple = CUtility.returnStartLbaWords
wordTuple = CUtility.ReturnTestCylWord

DEFAULT_BUFFER_SIZE = (0,256 * 512) # CPC has default 256 blocks buffer size
PASS_RETURN = {'LLRET':OK}
FAIL_RETURN = {'LLRET':NOT_OK}

speedLookup = {2: 1, #1.5Gbs
                     4: 3, #3.0Gbs
                     6: 6, #6.0Gbs
                     }

speedOptions = { 0x2: 1.5,
                 0x4: 3.0,
                 0x6: 6.0}

class initCmd(base_ICmd):
   passThroughList = ['SequentialWriteDMAExt',
                      'SequentialReadDMAExt',
                      'SequentialWRDMAExt',
                      'ZeroCheck',
                      'SequentialWriteVerify',
                      ]
   directCallList =  [
                      'StandbyImmed',
                      'Standby',
                      'FlushCache',
                      'WriteMIFDataToDisc',
                      'UnlockFactoryCmds',
                      'ClearFormatCorrupt',
                      'LongDST',
                      'ShortDST',
                     ]
   aliasList = {
      'SequentialWRDMA'          : 'SequentialWRDMAExt',
      'SequentialReadVerifyExt'  : 'SequentialReadDMAExt',
      'SequentialWriteDMA'       : 'SequentialWriteDMAExt',
      'SequentialReadDMA'        : 'SequentialReadDMAExt',
      'RandomWRDMA'              : 'RandomWRDMAExt',
      }


   def __init__(self, params, objPwrCtrl):
      base_ICmd.__init__(self,  params, objPwrCtrl)
      self.ovrPrms = {}
      self.IntfTimeout = 30000
      self.buffSize = {WBF: DEFAULT_BUFFER_SIZE,
                       RBF: DEFAULT_BUFFER_SIZE,
                       SBF: DEFAULT_BUFFER_SIZE,
                       }

      self.IdentifyDeviceBuffer = ''
      self.maxlba = 0


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
            raise


   def CRCErrorRetry(self, *args):
      return {'LLRET':0,'CRCCNT': 0, 'RETRY': 0}


   def DownloadInitiatorCode(self, *args, **kwargs):
      if objComMode.getMode() != objComMode.availModes.intBase:
         #MCT test so we need to talk to the drive
         theRim.EnableInitiatorCommunication(objComMode)

      return base_ICmd.St(self, *args, **kwargs)


   def St(self, *args, **kwargs):
      testNum = kwargs.get('test_num', False)
      if not testNum:
         testNum = args[0]
         if type(testNum) == types.DictionaryType:
            testNum = testNum['test_num']

      if objComMode.getMode() != objComMode.availModes.mctBase and testNum < 500:
         #MCT test so we need to talk to the drive
         theRim.DisableInitiatorCommunication(objComMode)
         objPwrCtrl.changeBaud(PROCESS_HDA_BAUD)
      elif objComMode.getMode() != objComMode.availModes.intBase:
         #Not MCT test and we aren't talking to the initiator
         objMsg.printMsg("Current mode %s" % (objComMode.getMode(),))
         try:
            theRim.EnableInitiatorCommunication(objComMode)
         except:
            if testSwitch.BF_0174032_231166_P_FULL_PWR_CYCLE_ENABLE_INIT_FAIL:
               objPwrCtrl.powerCycle(ataReadyCheck = False)
            else:
               raise
         try:
            if not objRimType.CPCRiser():
               self.HardReset()
         except:
            pass

         if not (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()):
            self.SetIntfTimeout(TP.prm_IntfTest.get("Default CPC Cmd Timeout", 30)*1000)
            self.SetRFECmdTimeout(TP.prm_IntfTest.get("Default ICmd Timeout", 600))
         if testSwitch.BF_0177886_231166_P_FIX_XFR_RATE_DIAG_TRANSITION:
            if theRim.initRimRequired:
               self.setMaxXferRate()
               theRim.initRimRequired = False


      if testNum in [504,506,507,508,510,514,535,538] and testSwitch.FE_0127479_231166_SUPPRESS_INFO_ONLY_TSTS: 
         if not DEBUG:
            if not kwargs.pop('display_info', False):
               if testNum not in [538, 514]:
                  kwargs['stSuppressResults'] = kwargs.get('stSuppressResults', 0) | ST_SUPPRESS__ALL | ST_SUPPRESS_SUPR_CMT
               else:
                  kwargs['stSuppressResults'] = kwargs.get('stSuppressResults', 0) | ST_SUPPRESS__ALL

      if testNum == 510:
         # If TEST_EXE_TIME_SECONDS is set in initiator 510 will run until that TMO expires
         self.SetRFECmdTimeout(0)
            
      ret = base_ICmd.St(self, *args, **kwargs)

      if testNum == 510:
         self.SetRFECmdTimeout(TP.prm_IntfTest["Default ICmd Timeout"])
                  
      return ret

   def dumpATAInfo(self):
      """
      Execute test 504 to retreive ata info from last cmd
      """
      if testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser():
         self.St({'test_num': 504,
                  'timeout':60,
                  'DblTablesToParse' : ['P5XX_TFREG_LBA','P5XX_TFREGEXT'],
                  'prm_name': 'dumpATAInfo',
                  'stSuppressResults' : ST_SUPPRESS__ALL, #| ST_SUPPRESS_RECOVER_LOG_ON_FAILURE,
                  })
      else:
         self.St({'test_num': 504,
                  'timeout':60,
                  'DblTablesToParse' : ['P5XX_TFREGEXT',],
                  'prm_name': 'dumpATAInfo',
                  'stSuppressResults' : ST_SUPPRESS__ALL, #| ST_SUPPRESS_RECOVER_LOG_ON_FAILURE,
                  })
      if testSwitch.virtualRun:
         ret = {'ERR_REG': '0', 'STATUS': '0x50', 'LBA_UPPER': '0', 'LBA_LOWER': '0', 'SCNT': '0', 'DEV': '0'}
      else:
         if testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser():
            if 'P5XX_TFREG_LBA' in self.dut.objSeq.SuprsDblObject:
               ret = self.dut.objSeq.SuprsDblObject['P5XX_TFREG_LBA'][-1].copy()
               del self.dut.objSeq.SuprsDblObject['P5XX_TFREG_LBA']
            else:
               ret = self.dut.objSeq.SuprsDblObject['P5XX_TFREGEXT'][-1].copy()
               del self.dut.objSeq.SuprsDblObject['P5XX_TFREGEXT']
         else:
            ret = self.dut.objSeq.SuprsDblObject['P5XX_TFREGEXT'][-1].copy()
            del self.dut.objSeq.SuprsDblObject['P5XX_TFREGEXT']
      return ret


   def GetIdentifyBuffer(self):
      """
      Return cpc style identify buffer created from class cache
      """
      return {'LLRET': OK, 'DATA': self.IdentifyDeviceBuffer}


   def GetBuffer(self, Mode, ByteOffset = 0, BuffSize = 512):
      """
      Retreive buffer from drive
      """

      tempPrm = dict(self.params.DisplayBufferData) #create a copy

      if testSwitch.BF_0139058_231166_P_FIX_SI_BUFFER_FILE_PARAM:
         if Mode & WBF:
            tempPrm['CTRL_WORD1'] = 14
            tempPrm['prm_name'] = 'Write Buffer to file'
         if Mode & RBF:
            tempPrm['CTRL_WORD1'] = 15
            tempPrm['prm_name'] = 'Read Buffer to file'
      else:
         if Mode & WBF:
            tempPrm['CTRL_WORD1'] = (0x000E,)
            tempPrm['prm_name'] = 'Write Buffer to file'
         if Mode & RBF:
            tempPrm['CTRL_WORD1'] = (0x000F,)
            tempPrm['prm_name'] = 'Read Buffer to file'

      tempPrm.update({'BYTE_OFFSET': wordTuple(ByteOffset),
                      'BUFFER_LENGTH':wordTuple(BuffSize)})

      stret = self.St(tempPrm)

      if not testSwitch.virtualRun:
         if (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()):
            data = open(os.path.join(ScrCmds.getSystemPCPath(), 'CPCFile', ScrCmds.getFofFileName(file = 0)), 'rb').read()
         else:
            try:
               data = open(os.path.join(ScrCmds.getSystemPCPath(), 'filedata', ScrCmds.getFofFileName(file = 0)), 'rb').read()
            except:
               data = open(os.path.join(ScrCmds.getSystemPCPath(), 'filedata', ScrCmds.getFofFileName(file = 1)), 'rb').read()
      else:
         data = '\x00'*16

      #Truncate to requested buffer size
      data = data[:BuffSize]

      stret = {'LLRET':0,'DATA': data}

      return stret


   def extractBufferDblog(self, buffDict):
      import re
      data = ''
      bcol = re.compile('B[\da-fA-F]')
      for row in buffDict:

         for key in sorted(row.keys()):
            if bcol.match(key):
               try:
                  data += chr(int(row[key],16))
               except:
                  objMsg.printMsg("Error: data:'%s' ; val: '%s', key: '%s'" % (data, row[key], key))
                  raise
      return data


   def PassThrough(self, *args, **kwargs):
      """Polymorphic access to passthrough"""
      numArgs = len(args) + len(kwargs.keys())
      if numArgs < 7:
         return self._passThroughLBA(*args, **kwargs)
      else:
         return self._passThroughCHS(*args, **kwargs)


   def _passThroughCHS(self, data_direction, drive_cmd, cylinder, head, sector, sector_count, features, byte_count = 0):
      """
      CHS version of passthrough command
      """
      prm = dict(self.params.SetFeaturesParameter)

      prm.update({
         'COMMAND': drive_cmd,
         'CYLINDER': cylinder,
         'FEATURES': features,
         'SECTOR': sector,
         'HEAD': 0x0F & head,
         'SECTOR_COUNT': sector_count,
         'PARAMETER_0': 0,
         })

      return self.translateStReturnToCPC( self.St(prm) )


   def _passThroughLBA(self, data_direction, drive_cmd, lba, sector_count, features, byte_count = 0):
      """
      LBA version of passthrough command
      """
      prm = dict(self.params.SetFeaturesParameter)

      prm.update({
         'COMMAND': drive_cmd,
         'LBA': lbaTuple(lba),
         'FEATURES': features,
         'SECTOR_COUNT': sector_count,
         'PARAMETER_0': 0x2000,
         })

      return self.translateStReturnToCPC( self.St(prm) )


   def SetTransferRate(self, transferRate):
      """
      Set the drive transfer rate based on the integer part of the transfer rate.
      enum: 6, 3, 1 == 6gbps, 3gbps, 1.5gbps
      also 2, 4 for FC
      """
      self.St(self.params.TransferMode, FC_SAS_TRANSFER_RATE = transferRate)

   def base_setMaxXferRate(self, speedLookup):
      retRate = None

      speedLookup = getattr(TP, 'prm_speedLookup_override',  speedLookup)

      for enum,rate in speedLookup:
         try:
            if testSwitch.FE_0125480_231166_ALLOW_SKIP_INVALID_XFER_SETTINGS:
               if rate > self.dut.driveattr.get('XFER_CAP', 99):
                  objMsg.printMsg("Skipping %2.2fGbs as drive attr indicates max xfer rate less" % (rate,))
                  continue
            objMsg.printMsg("Setting Transfer Rate to %2.2fGbs" % (rate,))

            if rate == 6 and testSwitch.WA_0177962_231166_P_PWR_CYC_6_GBS_XFR_RATE:
               self.objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = False)  #Do spinup, sense, etc.

            self.SetTransferRate(enum)

            self.St(self.params.TransferRate,  FC_SAS_TRANSFER_RATE = enum, TEST_OPERATING_MODE = 9, timeout = 100)

            self.dut.driveattr['XFER_CAP'] = rate
            retRate = rate
            break
         except ScriptTestFailure:
            objMsg.printMsg("Xfer rate not functional")
            st(504, TEST_FUNCTION =  0x0000, timeout = 35)
            st(604, RESET_OPTION = 0, timeout = 35)
         except FOFSerialTestTimeout:
            #self.powerOff(offTime = 10,  driveOnly = 0)
            #self.powerOn(set5V=5000, set12V=12000, onTime=10, baudRate=PROCESS_HDA_BAUD, useESlip=1,  driveOnly = 0,  readyTimeLimit = self.readyTimeLimit, ataReadyCheck = 0)
            self.objPwrCtrl.powerCycle(5000,12000,10,30, ataReadyCheck = False)  #Do spinup, sense, etc.

      return retRate

   def VerifyInterfaceSpeed(self):
      """
      Verify the maximum interface speed the drive is capable of and fail if < TP.prm_min_XferRate if defined
      """
      speedsToVerify = getattr(TP, 'prm_SATA_Speed_Verify_list', [6, 3, 1])
      speedsToVerify.sort(reverse = True) #sort them highest to lowest
      speed = speedsToVerify[-1] # Initialize to lowest rate
      for speedCheck in speedsToVerify:
         self.HardReset()
         try:
            self.St(self.params.TransferMode, FC_SAS_TRANSFER_RATE = speedCheck)
            self.St(self.params.TransferRate)
         except ScriptTestFailure:
            objPwrCtrl.powerCycle(ataReadyCheck = True)
         else:
            speed = speedCheck #Speed worked so update the setting
            break

      dut.driveattr['XFER_CAP'] = speed

      if speed < getattr(TP, 'prm_min_XferRate', 1):
         ScrCmds.raiseException(14037, "Min ATA speed setting %s not supported (max = %s)" % (getattr(TP, 'prm_min_XferRate', 1), speed))

      return speed


   def IdentifyDevice(self, exc = 1, force = False):
      """
      Identify the ATA device: collecting device information and setting maximum speed
      """

      # Clear out id buffer
      self.IdentifyDeviceBuffer = ''

      if testSwitch.WA_0139526_231166_P_HARD_RESET_PRIOR_IDENT:
         self.HardReset()

      ret = self.St( self.params.IdentifyDevice.copy())

      if testSwitch.virtualRun:
         buff = []
      else:
         buff = self.dut.objSeq.SuprsDblObject['P514_IDENTIFY_DEVICE_DATA']

      ret = self.translateStReturnToCPC( ret )

      for row in  buff:
         self.IdentifyDeviceBuffer += chr(int(row['VALUE'][0:2],16)) + chr(int(row['VALUE'][2:4],16))

      self.getATASpeed()

      return ret


   def setATASpeed(self, ATA_SignalSpeed):
      bitsSet = ATA_SignalSpeed & 0x6
      self.SetTransferRate(speedLookup[bitsSet])


   def getATASpeed(self):
      '''Check the current ATA Signaling Speed .  This supports 1.5, 3.0 and 6.0 Gbps'''

      speedLookup = {2: 1, #1.5Gbs
                  4: 3, #3.0Gbs
                  6: 6, #6.0Gbs
                  }

      speedOptions = { 0x2: 1.5,
                    0x4: 3.0,
                    0x6: 6.0}

      if testSwitch.virtualRun:
         ATA_SignalSpeed = 2
      else:
         ATA_SignalSpeed = CUtility.numSwap(self.IdentifyDeviceBuffer[154:156])

      bitsSet = ATA_SignalSpeed & 0x6

      if testSwitch.BF_0163846_231166_P_SATA_DNLD_ROBUSTNESS:
         if not bitsSet in speedLookup:
            objMsg.printMsg("Code does not support setting the signal speed (SCT-BIST commands)... Verifying max speed.")
            #bitsSet = CUtility.dictValLookup(speedLookup, self.VerifyInterfaceSpeed())
            return 0
         else:
            objMsg.printMsg("CURRENT SIGNAL SPEED IS %s Gbps" %speedOptions[bitsSet])
      else:
         if bitsSet in speedLookup:
            self.St(self.params.TransferMode, FC_SAS_TRANSFER_RATE=speedLookup[bitsSet])
            objMsg.printMsg("CURRENT SIGNAL SPEED IS %s Gbps" %speedOptions[bitsSet])
         else:
            objMsg.printMsg("Code does not support setting the signal speed (SCT-BIST commands)... Verifying max speed.")
            #bitsSet = CUtility.dictValLookup(speedLookup, self.VerifyInterfaceSpeed())
            return 0

      return speedOptions[bitsSet]


   def HardReset(self, exc = 1):
      """
      Send a hard reset command to the drive and wait for reset
      """
      self.params.HardReset[ 'stSuppressResults'] = ST_SUPPRESS__ALL
      self.St(self.params.HardReset)


   def SetRFECmdTimeout(self, timeout = 600):
      """
      Set the test card (initiator/cpc) timeout on command
      """
      if not (objRimType.CPCRiser() and testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #Do not set T510 TEST_RUN_TIME for non-intrinsic
         timeout = int(timeout)
         prm = self.params.CommandTimeout.copy()
         prm['TEST_RUN_TIME'] = timeout
         self.St(prm)


   def SetIntfTimeout(self, timeout = 30000):
      """
      Set the drive HBA inter-command timeout.
      """
      self.IntfTimeout = timeout
      timeout = int(timeout/1000.0)
      prm = self.params.CommandTimeout.copy()
      prm['COMMAND_TIMEOUT'] = wordTuple(timeout)
      self.St(prm)


   def GetIntfTimeout(self):
      """
      Retreive the currently set (local class value) interface command timeout
      """
      return {'TMO':self.IntfTimeout, 'LLRET':0}


   def setBuffSize(self, buffNum, size):
      """
      Set the buffer size for the masked buffers
      """
      if not type(size) in (types.TupleType, types.ListType):
         size = wordTuple(size)

      for buff in self.buffSize:
         if buffNum & buff:
            self.buffSize[buff] = size


   def MakeAlternateBuffer(self, buffNum, bufferSectorSize = 1, exc = 1):
      """
      Access method to setBuffSize
      """
      self.setBuffSize(buffNum,  bufferSectorSize*512)
      return PASS_RETURN


   def RestorePrimaryBuffer(self, buffNum):
      """
      Restore and clear the primary buffer sizes
      """
      self.setBuffSize(buffNum,  DEFAULT_BUFFER_SIZE)
      self.ClearBinBuff(buffNum)
      return PASS_RETURN


   def ClearBinBuff(self, buffNum = WBF, exc = 1):
      """
      Clear the buffers masked
      """
      return self.FillBuffer( buffNum , 0, '\x00')


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
      if timeout != None:
         self.SetRFECmdTimeout(timeout)

      self.disable_WriteCache()

      for loopCnt in xrange(loops):

         sLBA = randint(startLBA,  midLBA)

         self.SequentialWriteVerify(sLBA,  sLBA+scnt)

         self.SequentialReadDMAExt(singleLBA, singleLBA + scnt)

         randSectorCnt = randint(0, 0xFFFF)

         sLBA = randint(midLBA, endLBA)

         self.SequentialWriteVerify(sLBA, sLBA + randSectorCnt)

         #self.SequentialWriteDMAExt(midLBA, midLBA + randSectorCnt)
         #self.SequentialReadDMAExt(midLBA, midLBA + randSectorCnt)

      self.VerifyInterfaceSpeed()

      self.SequentialReadDMAExt(0, 0)


   def WriteTestMobile(self, startLBA, midLBA, endLBA, scnt, loops, seed = 0, ovPrm = None, exc = 1, timeout = None):
      """
      Perform the write mobile test as defined in CPC code (2.26 replicated)
      **WARNING**: 100-1000x slower than in CPC implementation due to command overhead
      """
      if ovPrm == None:
         ovPrm = {}

      tempOver = {
            'PATTERN_MODE': 0x80,
            #'RANDOM_SEED': seed,
      }

      if timeout != None:
         self.SetRFECmdTimeout(timeout)

      tempOver.update(ovPrm)

      for loopCnt in xrange(loops):

         self.ovrPrms = tempOver.copy()

         self.FillBufferRandom(seed)
         sLBA = randint(startLBA,  midLBA)

         self.RandomWRDMAExt(sLBA, sLBA + scnt, maxSectorCnt = 1000, compareFlag = 1)
         self.ovrPrms = tempOver.copy()

         self.SequentialReadDMAExt(startLBA, startLBA + scnt)

         randSectorCnt = randint(0, 0xFFFF)

         self.ovrPrms = tempOver.copy()

         sLBA = randint(midLBA, endLBA)
         self.FillBufferRandom(seed)
         self.RandomWRDMAExt(midLBA, midLBA + randSectorCnt, maxSectorCnt = 1000, compareFlag = 1)


   def FillBufferRandom(self, seed):
      """
      Fill the write buffer with random data
      """
      tempPrm = dict(self.params.WritePatternToBuffer) #create a copy

      tempPrm['CTRL_WORD1'] = (0x0000,)
      tempPrm['prm_name'] = 'Write RANDOM Pattern to Write Buffer'
      tempPrm['PATTERN_TYPE'] = 1
      tempPrm['RANDOM_SEED'] = seed

      return self.St(tempPrm)

   def FlushMediaCache(self):
      """
      Flush MediaCache - GIO ReliFunction.py #16
      """
      timeout = 10800
      self.HardReset()
      self.SetIntfTimeout(timeout * 1000)    # Command timeout

      tempPrm = dict(self.params.FlushMediaCache) #create a copy
      tempPrm.update({
         'timeout'     : timeout+600,    #CM timeout
         'FEATURES'    : (timeout/60),   #Purge durarion (mins)
         })
      stret = self.St(tempPrm)
      self.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"]*1000)
      return stret

   def ReadVerifyExt(self, startLBA, sectorCount):
      """
      Execute a ReadVerify command on the DUT
      """
      return self.SequentialReadDMAExt(startLBA, startLBA + sectorCount, COMPARE_FLAG = 1)

   #-------------------------------------------------------------------------------------------------------
   def overridePrmCall(self, STARTING_LBA, MAXIMUM_LBA, STEP_LBA = None, BLKS_PER_XFR = 256, \
                          STAMP_FLAG = 0, COMPARE_FLAG = 0, LOOP_COUNT = 1, DATA_PATTERN0 = None, timeout = 252000, exc = 1, stSuppressResults = False):
      """
      Generic interface command handler: implements standard interface for most commands
      """

      tempPrm = dict(getattr(self.params, self.prmName)) #create a copy

      #TODO: Add compare flag handling
      tempPrm.update({
            'timeout' : timeout,
            'STARTING_LBA' : lbaTuple(STARTING_LBA) ,
            'BLKS_PER_XFR' : BLKS_PER_XFR,
            })

      if COMPARE_FLAG and 'WRITE_READ_MODE' in tempPrm and tempPrm['WRITE_READ_MODE'] == 2:
         tempPrm['WRITE_READ_MODE'] = 0
         tempPrm['prm_name'] = 'SequentialWriteReadDMAExt'

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
         if 'DATA_PATTERN0' in tempPrm:
            tempPrm['ENABLE_HW_PATTERN_GEN'] = 1 # setting compare option (hareware comparison, not using WR/Rd buffer)
            # HW pattern generator comparisons are much faster than 551 buffer compares
            #  However 510 currently has an issue with filling the full write buffer- so use 551 for now
            tempPrm.update(self.params.Bit_to_Bit_cmp)
         else:
            tempPrm['COMPARE_OPTION'] = 0x01 # setting compare option (software comparison, using WR/Rd buffer)
         COMPARE_FLAG = False

      if self.ovrPrms:
         tempPrm.update(self.ovrPrms)

      totalBlocksXfr = LOOP_COUNT * (MAXIMUM_LBA - STARTING_LBA + 1 )
      tempPrm['TOTAL_BLKS_TO_XFR64'] = lbaTuple(totalBlocksXfr)

      if LOOP_COUNT > 1:
         tempPrm['MAXIMUM_LBA']  = lbaTuple(MAXIMUM_LBA)

      if self.maxlba == 0:
         self.GetMaxLBA()

      if MAXIMUM_LBA > self.maxlba and 'MAXIMUM_LBA' in tempPrm:
         tempPrm['MAXIMUM_LBA']  = lbaTuple(self.maxlba)

      elif not 'MAXIMUM_LBA' in tempPrm and (totalBlocksXfr + STARTING_LBA) > self.maxlba:
         #No loops so total + start can't exceed max lba
         totalBlocksXfr = self.maxlba - STARTING_LBA
         tempPrm['TOTAL_BLKS_TO_XFR64'] = lbaTuple(totalBlocksXfr)

      tempPrm.update({
            'retryECList' : [10100, 11173,],
            'retryCount'  : 1,
            'retryMode'   : HARD_RESET_RETRY,
         })

      if stSuppressResults:
         tempPrm['stSuppressResults'] = stSuppressResults

      ret = self.St(tempPrm)

      self.ovrPrms = {}
      ret = self.translateStReturnToCPC(ret)

      return ret


   def CompareBuffers(self, byteOffset, byteCount, buffFlag = 0, stSuppressResults = False, exc = 1):
      tempPrm = dict(self.params.CompareBuffers) #create a copy

      tempPrm['BUFFER_LENGTH'] = wordTuple(byteCount)
      tempPrm['BYTE_OFFSET'] = wordTuple(byteOffset)
      if stSuppressResults:
         tempPrm['stSuppressResults'] = stSuppressResults

      try:
         ret = self.St(tempPrm)
      except:
         objMsg.printMsg("RBF- FAILED")
         self.GetBuffer(RBF, byteOffset, byteCount)
         objMsg.printMsg("WBF")
         self.GetBuffer(WBF, byteOffset, byteCount)
         if exc:
            raise
         else:
            return FAIL_RETURN.copy()

      return PASS_RETURN


   def downloadIORimCode(self, forced = False):
      """
      Download the initiator code if different than requested via INC code key
      """
      from PackageResolution import PackageDispatcher
      try:
         base_BaudFunctions.sendBaudCmd(theCell.getBaud(), PROCESS_HDA_BAUD)
      except:
         theRim.powerCycleRim()
         base_BaudFunctions.sendBaudCmd(theCell.getBaud(), PROCESS_HDA_BAUD)
      op = PackageDispatcher(self.dut, 'INC')
      incCode = op.getFileName()

      if incCode in  ['',None, []]:
         if testSwitch.FailcodeTypeNotFound and not testSwitch.virtualRun:
            if testSwitch.FE_0153649_231166_P_ADD_INC_DRIVE_ATTR:
               DriveAttributes['SIC_VER'] = ''
            ScrCmds.raiseException(10326,'Code %s not found in codeType resolution.' % incCode)
         else:
            if testSwitch.FE_0153649_231166_P_ADD_INC_DRIVE_ATTR:
               DriveAttributes['SIC_VER'] = ''
            objMsg.printMsg("*"*20 + "Warning: Skipping %s Download" % incCode, objMsg.CMessLvl.IMPORTANT)
            return None
      dnldInitiatorPrms = ({'test_num':8,'prm_name':'DownLoad Init FW', 'dlfile' : (CN, incCode), 'timeout': 100, 'retryCount': 0},0,0,0,0,0,0,0,0,)

      retrylimit = 3
      for retry in xrange(retrylimit):
         try:
            if self.checkInitiatorRev(incCode) and not( forced or ConfigVars[CN].get('FORCE_INIT_DNLD', False)):
               objMsg.printMsg("The requested initiator code (%s) is on the initiator." % incCode)
               break

            if testSwitch.WA_0117940_231166_IGNORE_INIT_DL_MISMATCH and retry > 0:
               break
            objMsg.printMsg("Downloading initiator:  %s" % incCode)
            self.DownloadInitiatorCode(*dnldInitiatorPrms) # download initiator code
            break
         except:
            if retry != retrylimit-1:
               #Don't power cycle prior to failure
               theRim.powerCycleRim()
               base_BaudFunctions.sendBaudCmd(theCell.getBaud(), PROCESS_HDA_BAUD)
      else:
         raise

      if testSwitch.FE_0153649_231166_P_ADD_INC_DRIVE_ATTR:
         self.checkInitiatorRev(incCode)


      if testSwitch.FE_0178765_231166_P_SAVE_INITIATOR_INFO_FILE:
         self.createInitiatorPklFile()



   def createInitiatorPklFile(self):
      from Rim import RISER_BASE

      if testSwitch.FE_0205626_231166_P_VER_1_INIT_PKL_FILE:
         riserIntfLookup = {
            'AT': 'PATA',
            'ST': 'SATA',
            'FC': 'FC',
            'LC': 'FC',
            'LW': 'FC',
            'SS': 'SAS',
            'SX': 'SAS/SATA',
            'US': 'USB',
         }

      prm = self.params.InitiatorRev.copy()
      prm['DblTablesToParse'].append('P535_INTERFACE_CONT')
      if testSwitch.FE_0205626_231166_P_VER_1_INIT_PKL_FILE:
         prm['DblTablesToParse'].append('P535_INITR_INTERFACE_CHIP')
      self.St(prm)

      if testSwitch.virtualRun:
         fname = ''
         controller = 'Banshee'
      else:
         
         if testSwitch.FE_0205626_231166_P_VER_1_INIT_PKL_FILE and 'P535_INITR_INTERFACE_CHIP' in self.dut.objSeq.SuprsDblObject:
            controller = self.dut.objSeq.SuprsDblObject['P535_INITR_INTERFACE_CHIP'][-1]['CONTROLLER_NAME']
         elif 'P535_INTERFACE_CONT' in self.dut.objSeq.SuprsDblObject:
            fname = self.dut.objSeq.SuprsDblObject['P535_INITIATOR_RELEASE'][-1]['DOWNLOAD_FILE_NAME']
            controller = self.dut.objSeq.SuprsDblObject['P535_INTERFACE_CONT'][-1]['CONTROLLER']

      if not testSwitch.FE_0205626_231166_P_VER_1_INIT_PKL_FILE:
         if controller.find('Not_Recognized') > -1:
            controller = 'SKUA'

      if testSwitch.FE_0205626_231166_P_VER_1_INIT_PKL_FILE:
         initType = riserIntfLookup.get(riserExtension[2:4], None)
      else:
         initType = RISER_BASE

      pickleFile = GenericResultsFile('initiator_type.pkl')
      pickleFile.open('wb')
      initInfo = {'chip':controller,
                  'type': initType,
                  'RISER': riserType,
                  'EXT': riserExtension}
      if testSwitch.FE_0205626_231166_P_VER_1_INIT_PKL_FILE:
         initInfo['VERSION'] = 1

      myPickle.dump(initInfo, pickleFile, 2)
      pickleFile.close()


   def checkInitiatorRev(self, expectedRev):
      """Check the expected initiator rev against the actual"""
      CInit_Type = self.getRimCodeVer()
      if testSwitch.virtualRun:
         CInit_Type = expectedRev
      if testSwitch.FE_0153649_231166_P_ADD_INC_DRIVE_ATTR:
         #DriveAttributes['SIC_VER'] = CInit_Type
         DriveAttributes['SIC_VER'] = CInit_Type[:15]
      objMsg.printMsg("Current Initiator Code: %s        Requested Initiator Code: %s"%(CInit_Type,expectedRev))
      expectedRevs = expectedRev.split('_')[-1].split('.')[:3]
      for er in expectedRevs:
         if not er.upper() in CInit_Type:
            objMsg.printMsg("%s not found in %s" % (er.upper(),  CInit_Type))
            return False

      return True


   def getRimCodeVer(self):
      """
      Get the rim code from initiator
      """
      self.St(self.params.InitiatorRev)

      if testSwitch.virtualRun:
         ret = ''
      else:
         ret = self.dut.objSeq.SuprsDblObject['P535_INITIATOR_RELEASE'][-1]['DOWNLOAD_FILE_NAME']

      return ret


   def RandomWriteDMAExt(self, minLBA = 0, maxLBA = None, minSectorCnt = 256, maxSectorCnt = 256, loopCnt = 1, stampFlag = 0, compareFlag = 0, flushCacheFlag = 0):
      """
      Execute RandomWriteDMAExt on DUT
      """
      return self._randomOp(self.params.RandomWriteDMAExt, minLBA, maxLBA, minSectorCnt, maxSectorCnt, loopCnt = loopCnt, stampFlag = stampFlag, compareFlag = compareFlag, flushCacheFlag = flushCacheFlag)


   def RandomReadDMAExt(self, minLBA = 0, maxLBA = None, minSectorCnt = 256, maxSectorCnt = 256, loopCnt = 1, stampFlag = 0, compareFlag = 0, flushCacheFlag = 0):
      """
      Execute RandomReadDMAExt on DUT
      """
      return self._randomOp(self.params.RandomReadDMAExt, minLBA, maxLBA, minSectorCnt, maxSectorCnt, loopCnt = loopCnt, stampFlag = stampFlag, compareFlag = compareFlag, flushCacheFlag = flushCacheFlag)


   def RandomWRDMAExt(self, minLBA = 0, maxLBA = None, minSectorCnt = 256, maxSectorCnt = 256, loopCnt = 1, stampFlag = 0, compareFlag = 0, flushCacheFlag = 0):
      """
      Execute RandomWRDMAExt on DUT
      """
      return self._randomOp(self.params.RandomWRDMAExt, minLBA, maxLBA, minSectorCnt, maxSectorCnt, loopCnt = loopCnt, stampFlag = stampFlag, compareFlag = compareFlag, flushCacheFlag = flushCacheFlag)


   def _randomOp(self, basePrm, minLBA = 0, maxLBA = None, minSectorCnt = 256, maxSectorCnt = 256, loopCnt = 1, stampFlag = 0, compareFlag = 0, flushCacheFlag = 0):
      """
      Generic function to implement random ops
      """
      tempPrm = dict(basePrm)

      if maxLBA == None:
         maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1

      tempPrm.update({
               'STARTING_LBA' : lbaTuple(minLBA),
               'BLKS_PER_XFR': randint(minSectorCnt, maxSectorCnt),
               'MAXIMUM_LBA' : lbaTuple(maxLBA),
               #'TOTAL_BLKS_TO_XFR64' : lbaTuple(maxLBA - minLBA + 1),
               })

      tempPrm['TOTAL_BLKS_TO_XFR64'] = lbaTuple(loopCnt * tempPrm['BLKS_PER_XFR'])         

      if self.ovrPrms:
         tempPrm.update(self.ovrPrms)

      if not tempPrm['test_num'] in [508, 514, 533, 528, 535]:
         self.HardReset()

      ret = self.St(tempPrm)
      self.ovrPrms = {}
      ret = self.translateStReturnToCPC(ret)

      return ret


   def GetPreampTemp(self):
      """
      Get preamp temp from drive using DITS and display readback buffer
      """
      self.St(self.params.GetPreampTemp)
      self.St(self.params.DisplayBufferData)


   def Ctrl(self, cmd, matchStr = None):
      import sptCmds
      if objComMode.getMode() == objComMode.availModes.intBase:
         #Talking to initiator test so we need to talk to the drive
         sptCmds.enableDiags(10)
      data = sptCmds.sendDiagCmd(eval('CTRL_'+cmd), altPattern = matchStr)
      return {'LLRET':0,'DATA':data}

   def InterfaceCmdCount(self, reset):    # IOMQM
      pass

   def ClearSerialBuffer(self):           # IOMQM
      pass

