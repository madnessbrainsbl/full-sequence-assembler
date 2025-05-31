#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Interface Command Factory object. Returns the requisite object to execute the propper IOCmd
#              based on RimType
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Serial_ICmd.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Serial_ICmd.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import Rim, traceback
import ScrCmds
import MessageHandler as objMsg
from base_Initiator_CMD import PASS_RETURN, FAIL_RETURN
from base_ICmd import base_ICmd
import serialScreen, sptCmds
import sdbpCmds, sdbpComm
import MathLib
import base_BaudFunctions
from Drive import objDut as dut
from Utility import CUtility
import struct

USE_SDBP = False

class Serial_ICmd(base_ICmd):
   """
   Class implements methods to perform some interface equivalent commands over the serial port- for ease of use/conversion
   """
   aliasList = {}

   def __init__(self, params, objPwrCtrl):
      base_ICmd.__init__(self,  params, objPwrCtrl)
      objMsg.printMsg("Using Serial_ICmd for ICmd resolution")
      self.oSerial = serialScreen.sptDiagCmds()

      self.baudSet = False
      self.diagMode = False
      self.readBuffer = ''
      self.writeBuffer = ''
      self.IntfTimeout = 30000


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
            objMsg.printMsg("%s not implemented- attempting bypass" % name)
            #return self.dummyCall
            raise

   def dummyCall(self, *args, **kwargs):
      return PASS_RETURN

   #stubbed functions
   def disable_WriteCache(self, exc = 1): return PASS_RETURN
   def enable_WriteCache(self, exc = 1): return PASS_RETURN
   def downloadIORimCode(self, forced = False): return PASS_RETURN
   def SetRFECmdTimeout(self, timeout = 600): return PASS_RETURN
   def SetIntfTimeout(self, timeout = 30000): return PASS_RETURN
   def CRCErrorRetry(self, *args):  return {'LLRET':0,'CRCCNT': 0, 'RETRY': 0}

   def GetMaxLBA(self, refreshBuffer = None):
      if self.IdentifyDeviceBuffer == '':
         self.IdentifyDevice()
      else:
         objMsg.printMsg("Warning! Sending cached SP ID Data")

      self.maxlba = CUtility.numSwap(self.IdentifyDeviceBuffer[200:205])
      return { 'LLRET':OK,
               'MAX48': "%X" % self.maxlba,
               'MAX28': "%X" % CUtility.numSwap(self.IdentifyDeviceBuffer[120:124]),
               }


   def IdentifyDevice(self, exc = 1):
      """
      Identify the ATA device: collecting device information using SPT
      """
      if self.IdentifyDeviceBuffer == '':
         self.__SetupCommMode()
         if USE_SDBP:
            self.IdentifyDeviceBuffer = sdbpCmds.serialIdent()
         else:
            #self.IdentifyDeviceBuffer = self.oSerial.getIdentifyBuffer()
            self.IdentifyDeviceBuffer = self.oSerial.getIdentifyBuffer(0, 0xFF)
            self.IdentifyDeviceBuffer += self.oSerial.getIdentifyBuffer(0x100, 0x1FF)

      return PASS_RETURN

   def __SetupSDBPCmd(self, multisrq_enable = True):
      if not self.baudSet:
         from PowerControl import objPwrCtrl
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=5, onTime=5, baudRate=PROCESS_HDA_BAUD, useESlip=1)
         self.baudSet = True

      sptCmds.enableESLIP()

      try:
         sdbpCmds.unlockDits()
         sdbpCmds.unlockDets()
      except:
         from PowerControl import objPwrCtrl
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=5, onTime=5, baudRate=PROCESS_HDA_BAUD, useESlip=1)
         self.baudSet = True
         sdbpCmds.unlockDits()
         sdbpCmds.unlockDets()

      if multisrq_enable:
         sdbpComm.enableESLIPDiags()

   def __SetupDiagMode(self):
      if not self.diagMode:
         sptCmds.enableDiags()

   def __SetupCommMode(self, sdbpForce = False, multisrq_enable = True):
      if USE_SDBP or sdbpForce:
         Y2backup = dut.SkipY2
         try:
            dut.SkipY2 = True
            self.__SetupSDBPCmd(multisrq_enable)
         finally:
            dut.SkipY2 = Y2backup
      else:
         self.__SetupDiagMode()

   def GetIdentifyBuffer(self):
      resp = PASS_RETURN.copy()
      resp['DATA'] = self.IdentifyDeviceBuffer
      return resp
      
   def DisplayBadBlocks(self, exc = 1):
      """
      Returns the Glist count
      """
      resp = PASS_RETURN.copy()
      self.__SetupCommMode()
      altListTotals, AltListLBAS = self.oSerial.dumpReassignedSectorList(1)
      glistCount = 0
      for lba in AltListLBAS:
         if lba['STATUS'] & 1 == 1:
            glistCount += 1
      
      resp['NUMBER_OF_TOTALALTS'] = glistCount
      return resp

   def GetPendingDefects(self):
      """
      Returns the pending defect count and items
      """
      self.__SetupCommMode()
      altListTotals, AltListLBAS = self.oSerial.dumpReassignedSectorList(1)
      PListCount = altListTotals['NUMBER_OF_PENDING_ENTRIES']
      if testSwitch.virtualRun:
         PListCount = 0 # nominal ve has 2
      PendingLbaList = []
      for lba in AltListLBAS:
         if lba['STATUS'] & 1 == 0:
            PendingLbaList.append(lba)
      return PListCount, PendingLbaList

   def SmartEnableOper(self):
      """NOP for Serial"""
      return PASS_RETURN

   def SmartReadData(self, exc = 1):
      """
      Returns the smart attribute data as list of dicts ** different than interface version at this point
         TODO: abstract at different level?
      """
      local_SDBP = True # or USE_SDBP

      if not testSwitch.BF_0188020_231166_P_ESLIP_MODE_TRANSITION_FIN2_SPTONLY:
         global USE_SDBP
         USE_SDBP = local_SDBP = True
         
      self.__SetupCommMode(local_SDBP)
      if local_SDBP:
         smartAttributeData = sdbpCmds.getRawSmartAttrLog()  #getSmartAttributes()
      else:
         smartAttributeData = self.oSerial.getSmartAttribute(-1, True, None, True)

      
      return smartAttributeData

   def GetBufferDETS( self, Mode, ByteOffset = 0, BuffSize = 512 ):

      if Mode == RBF:

         return {'LLRET':0, 'DATA': self.readBuffer[ByteOffset:BuffSize]}
      else:
         return {'LLRET':0, 'DATA': self.writeBuffer[ByteOffset:BuffSize]}

   @staticmethod
   def insertData(buff, offset, data):
      dataLen = len(data)
      out = buff[:offset] + data + buff[offset+dataLen:]
      return out

   def FillBufferDETS( self, Mode,  ByteOffset,  data):
      if Mode == RBF:
         self.readBuffer = self.insertData(self.readBuffer, ByteOffset, data)
         return self.readBuffer
      else:
         self.writeBuffer =self.insertData(self.writeBuffer, ByteOffset, data)
         return self.writeBuffer


   def SmartReadLogSec(self, logAddr, sectorCount):

      self.readBuffer = ''

      global USE_SDBP
      prev = USE_SDBP
      USE_SDBP = True
      #USE_SDBP = False

      self.__SetupCommMode(sdbpForce = True)

      self.readBuffer = sdbpCmds.readLogExtended(logAddr, blockXferLen = sectorCount)


      USE_SDBP = prev


      return {'LLRET':0}#self.translateStReturnToCPC(self.St(tempPrm))

   def SmartWriteLogSec(self, logAddr, sectorCount):
      global USE_SDBP
      prev = USE_SDBP
      USE_SDBP = True
      #USE_SDBP = False

      self.__SetupCommMode(sdbpForce = True)

      numBytes = sectorCount*512
      dummyBuffer = '\xff' * numBytes
      #copy into dummy buffer- easier than the alternate length truncations needed for differing buffer
      #   sizes otherwise
      dummyBuffer = self.insertData(dummyBuffer, 0, self.writeBuffer[:numBytes])


      error = sdbpCmds.writeSmartLog(logAddr, dummyBuffer)
      USE_SDBP = prev

      return {'LLRET':error}#self.translateStReturnToCPC(self.St(tempPrm))

   def HardReset(self, exc = 1):
      """
      Dummy function for hard reset
      """
      pass

   def ClearSmartAndUDS(self):
      """
      Call command to clear smart and UDS
      """
      global USE_SDBP
      prev = USE_SDBP
      USE_SDBP = True
      #USE_SDBP = False
      self.__SetupCommMode()
      objMsg.printMsg("Clear SMART")
      sdbpCmds.clearSmart()
      try:
         objMsg.printMsg("Clear UDS")
         sdbpCmds.clearSmartTimerUDS()
      except:
         objMsg.printMsg("UDS Smart Reset not supported: \n%s" % (traceback.format_exc(),))
      #self.oSerial.SmartCmd({'options': [1, 0x23, 0x25,], 'initFastFlushMediaCache': 1}, 1)
      USE_SDBP = prev

   def translateStReturnToCPC(self, stat):
      """
      Dummy function to translate return from CPC non functional for serial cell
      """
      return PASS_RETURN

   def resetCustomerConfiguration(self):
      """
      NOP
      """
      pass

   def LongDST(self, timeout, exc = 1):
      global USE_SDBP
      prev = USE_SDBP
      USE_SDBP = False
      self.__SetupCommMode()
      self.oSerial.smartDST(timeout, 'LONG')
      USE_SDBP = prev

   def UnlockFactoryCmds(self, exc = 1):
      """
      May be used explicitly in the future. For now would just cause complications
      """
      pass
      #self.__SetupCommMode()


   def truncateMaxInputLBA(self, MAXIMUM_LBA):
      """
      Truncates a max lba input to max host lba.
      **Input is Host LBA
      """
      self.GetMaxLBA()
      return min([MAXIMUM_LBA, self.maxlba])

   def convertHostToDiscLBA(self, hostLBA):
      """
      Convert host lba to disc lba. DETS uses disc lbas so this is a helper function
      """
      discLBA = hostLBA
      sectorSizePhys, sectorSizeLgc = dut.IdDevice['Physical Sector Size'],dut.IdDevice['Logical Sector Size']
      if sectorSizeLgc != sectorSizePhys:
         discLBA = hostLBA * (sectorSizeLgc / float(sectorSizePhys))

      return discLBA

   def SequentialWRDMAExt(self, STARTING_LBA, MAXIMUM_LBA, STEP_LBA = None, BLKS_PER_XFR = 256, \
                          STAMP_FLAG = 0, COMPARE_FLAG = 0, LOOP_COUNT = 1, DATA_PATTERN0 = None, timeout = 252000, exc = 1, stSuppressResults = False):
      """
      Use DETS to perform a sequential write dma extended procedure on the drive
         **Templated with SequentialWRDMAExt
      """
      global USE_SDBP
      prev = USE_SDBP
      USE_SDBP = True
      self.__SetupCommMode()

      objMsg.printMsg("SequentialWRDMAExt(%s, %s, %s, %s, %s, %s, %s, %s)" % (STARTING_LBA, MAXIMUM_LBA, STEP_LBA , BLKS_PER_XFR , STAMP_FLAG , COMPARE_FLAG , LOOP_COUNT , DATA_PATTERN0))
      
      MAXIMUM_LBA = self.truncateMaxInputLBA(MAXIMUM_LBA)

      #DETS uses disc lba's so we need to account for the user specified host lba counts
      MAXIMUM_LBA = self.convertHostToDiscLBA(MAXIMUM_LBA)
      STARTING_LBA = self.convertHostToDiscLBA(STARTING_LBA)
      
      for loop in xrange(LOOP_COUNT):
         sdbpCmds.setDefaultTestSpace()
         
         sdbpCmds.setTargetAddressMode_LBA()
         
         sdbpCmds.setMinMaxLBA(STARTING_LBA, MAXIMUM_LBA)
         if DATA_PATTERN0 == None and STAMP_FLAG == 0:
            sdbpCmds.setBufferPattern(sdbpCmds.ZERO_BUFFER_PATTERN)
         elif STAMP_FLAG:
            sdbpCmds.setBufferPattern(sdbpCmds.INCREMENTING_BUFFER_PATTERN)
         else:
            sdbpCmds.setBufferPattern(sdbpCmds.USER_BUFFER_PATTERN, DATA_PATTERN0[:16], len(DATA_PATTERN0[:16]))
   
         #objMsg.printMsg("going to write timeout: %d" % timeout)
         sdbpCmds.writeTestSpace(timeout = timeout )
         if COMPARE_FLAG:
            sdbpCmds.readCompareTestSpace(timeout = timeout)

      USE_SDBP = prev


   def SequentialReadDMAExt(self, STARTING_LBA, MAXIMUM_LBA, STEP_LBA = None, BLKS_PER_XFR = 256, \
                          STAMP_FLAG = 0, COMPARE_FLAG = 0, LOOP_COUNT = 1, DATA_PATTERN0 = None, timeout = 252000, exc = 1, stSuppressResults = False):
      """
      Use DETS to perform a sequential read dma extended procedure on the drive
         **Templated with SequentialReadDMAExt
      """
      global USE_SDBP
      prev = USE_SDBP
      USE_SDBP = True
      self.__SetupCommMode()

      objMsg.printMsg("SequentialReadDMAExt(%s, %s, %s, %s, %s, %s, %s, %s)" % (STARTING_LBA, MAXIMUM_LBA, STEP_LBA , BLKS_PER_XFR , STAMP_FLAG , COMPARE_FLAG , LOOP_COUNT , DATA_PATTERN0))

      sectorSizePhys, sectorSizeLgc = dut.IdDevice['Physical Sector Size'],dut.IdDevice['Logical Sector Size']
      
      response = sdbpCmds.getDriveBasicInformation()

      MAXIMUM_LBA = self.truncateMaxInputLBA(MAXIMUM_LBA)

      #DETS uses disc lba's so we need to account for the user specified host lba counts
      MAXIMUM_LBA = self.convertHostToDiscLBA(MAXIMUM_LBA)
      STARTING_LBA = self.convertHostToDiscLBA(STARTING_LBA)

      for loop in xrange(LOOP_COUNT):
         sdbpCmds.setDefaultTestSpace()
         
         sdbpCmds.setTargetAddressMode_LBA()
         
         sdbpCmds.setMinMaxLBA(STARTING_LBA, MAXIMUM_LBA)
         if DATA_PATTERN0 == None and STAMP_FLAG == 0:
            sdbpCmds.setBufferPattern(sdbpCmds.ZERO_BUFFER_PATTERN)
         elif STAMP_FLAG:
            sdbpCmds.setBufferPattern(sdbpCmds.INCREMENTING_BUFFER_PATTERN)
         else:
            sdbpCmds.setBufferPattern(sdbpCmds.USER_BUFFER_PATTERN, DATA_PATTERN0[:16], len(DATA_PATTERN0[:16]))
   
         if COMPARE_FLAG:
            sdbpCmds.readCompareTestSpace(timeout = timeout)
         else:
            sdbpCmds.readTestSpace(timeout = timeout )

      USE_SDBP = prev

   def ClearBinBuff (self, buffNum = WBF, exc = 1):
      global USE_SDBP
      prev = USE_SDBP
      USE_SDBP = True
      self.__SetupCommMode()

      sdbpCmds.setBufferPattern(sdbpCmds.ZERO_BUFFER_PATTERN)

      USE_SDBP = prev
      return PASS_RETURN

   def ReadLenovo8S(self):
      self.__SetupCommMode(sdbpForce = True, multisrq_enable = False)
      sn = sdbpCmds.readLogExtended(0xDF, blockOffset = 0, blockXferLen = 1, logSpecific = 0)
      sn = sn.strip()
      return sn

   def ReadPPID (self):
      ''' Command reads smart log but functionality only for PPID
      '''
      self.__SetupCommMode(sdbpForce = True)
      PPID = sdbpCmds.readPPID()
      return PPID

   def WritePPID (self, writePPID):
      '''Command writes smart log but functionality only for PPID
      '''
      self.__SetupCommMode(sdbpForce = True)
      sdbpCmds.writePPID(writePPID = writePPID)

   def CCV_SetupCommMode(self, sdbpForce = False, multisrq_enable = True): 
      '''To call a private method
      '''
      self.__SetupCommMode(sdbpForce, multisrq_enable)

   def SetATASpeed(self, speed):
      cmdLookup = [0x0000, 0x0100, 0x0200, 0x0400, ]

      try:
         iCmd = cmdLookup.index(speed)
      except:
         objMsg.printMsg("Warning, speed=%s may be invalid. Forcing to 0" % speed)
         iCmd = 0

      if 1:    # DETS method
         objMsg.printMsg("SetATASpeed DETS=%s" % speed)
         self.__SetupCommMode(sdbpForce = True)
         sdbpCmds.setATASpeed(iCmd)
      else:    # ASCII diag method
         cmd = "/5b3,%s" % iCmd
         objMsg.printMsg("SetATASpeed ASCII diag cmd=%s" % cmd)
         sptCmds.enableDiags()
         sptCmds.gotoLevel('T')
         sptCmds.sendDiagCmd(cmd, printResult=True)


   def getATASpeed(self):

      speedLookup = [
               (6.0, 8), #6.0Gbs
               (3.0, 4), #3.0Gbs
               (1.5, 2), #1.5Gbs
               ]

      drvATASpeed = dut.IdDevice['SATA Ver']
      objMsg.printMsg("Serial_ICmd.py - drvATASpeed = %s" % drvATASpeed)

      for rate, bitmask in speedLookup:
         if (drvATASpeed & bitmask):
            objMsg.printMsg("Serial_ICmd.py - Serial ATA capabilities %s Gbps" % rate)
            return rate
         
      return 0

   @staticmethod
   def extractNumBinsAndSize(CCT_BIN_SETTINGS):
      numBins = CCT_BIN_SETTINGS >> 8
      binSize_ms = CCT_BIN_SETTINGS & 0xFF

      return numBins, binSize_ms


   def CCT_510(self, parameter):
      """
      Function that executes the CCT test emulating 510 CCT and outputs P_CCT_MAX_CMD_TIMES and P_CCT_DISTRIBUTION
      """
      
      numBins, binSize_ms = self.extractNumBinsAndSize( parameter['CCT_BIN_SETTINGS'] )
      cctLbasSave = parameter.get('CCT_LBAS_TO_SAVE', 5)

      startLBA = CUtility.reverseLbaWords( parameter['STARTING_LBA'] )
      endLba = parameter.get('MAXIMUM_LBA', None)
      if endLba == None:
         totalXfr = CUtility.reverseLbaWords( parameter.get('TOTAL_BLKS_TO_XFR64', parameter.get('TOTAL_BLKS_TO_XFR', 0)) )
         
         if totalXfr == 0:
            endLba = int(self.GetMaxLBA()['MAX48'], 16) - 1
         else:
            endLba = startLBA + totalXfr
      else:
         endLba = CUtility.reverseLbaWords( endLba )

      sectCnt = max( parameter['BLKS_PER_XFR'], 1024 * 4 )

      #currently not handled
      stepSize = parameter.get('STEP_SIZE', sectCnt)

      self.__SetupCommMode(sdbpForce = True)

      curSeq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      wrmode  = {2:1}.get( ( parameter['CTRL_WORD1']>>4 ) & 7, 0) #translates the ata command to a cpc mode... max internally is 1

      data = sdbpCmds.lbaSequentialTiming(wrmode, startLBA, endLba, sectCnt, timeout = parameter.get('timeout', self.IntfTimeout ))
      if testSwitch.virtualRun:
         data = [(0, sectCnt, 10000), (sectCnt, sectCnt, 20000)]
      
      spc_id = parameter.get('spc_id', 1)
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(510)
      self.makeCCT_DistributionTbl(data, binSize_ms, numBins, curSeq, occurrence, testSeqEvent, spc_id)

      self.makeCCTMaxCmdTimes(data, cctLbasSave, curSeq, occurrence, testSeqEvent, spc_id)

      return PASS_RETURN

   def makeCCTMaxCmdTimes(self, data, numberOfLbas, curSeq, occurrence, testSeqEvent, spc_id):
      
      data.sort( key = lambda x: x[2], reverse = True) #sort by command time so highest is first

      

      for index, item in enumerate(data):

         self.dut.dblData.Tables('P_CCT_MAX_CMD_TIMES').addRecord({
            'SPC_ID'             : spc_id,
            'OCCURRENCE'         : occurrence,
            'SEQ'                : curSeq,
            'TEST_SEQ_EVENT'     : testSeqEvent,
            'CMD_RANK'  :  index,
            'CMD_TIME'  :  item[2]/1000.0,  # time is stored internally as usec
            'LBA'       :  item[0],         # oth index is the start lba of the region
            })
         #we have output our last item
         if index == numberOfLbas-1: #subtract one since index starts at 0
            break

      try:
         objMsg.printDblogBin( self.dut.dblData.Tables('P_CCT_MAX_CMD_TIMES') )
      except:
         objMsg.printMsg( traceback.format_exc() )
         objMsg.printMsg( self.dut.dblData.Tables('P_CCT_MAX_CMD_TIMES') )

   def makeCCT_DistributionTbl(self, data, binStep, totalBin, curSeq = 0, occurrence = 0, testSeqEvent = 0, spc_id = 0):
      #bin the data... spt data is in usec and ata was msec so we have to convert
      binnedData = sdbpCmds.binData( [ i[2] for i in data ] , binStep * 1000, totalBin )
      for index, item in enumerate(binnedData):
         self.dut.dblData.Tables('P_CCT_DISTRIBUTION').addRecord({
                                                                  'SPC_ID'             : spc_id,
                                                                  'OCCURRENCE'         : occurrence,
                                                                  'SEQ'                : curSeq,
                                                                  'TEST_SEQ_EVENT'     : testSeqEvent,
                                                                  'CCT_BIN_NUM': index,
                                                                  'BIN_THRESHOLD': (binStep * index) + binStep,
                                                                  'BIN_ENTRIES': item,
                                                                    }) 

      try:
         objMsg.printDblogBin( self.dut.dblData.Tables('P_CCT_DISTRIBUTION') )
      except:
         objMsg.printMsg( traceback.format_exc() )
         objMsg.printMsg( self.dut.dblData.Tables('P_CCT_DISTRIBUTION') )



   def SequentialCCT(self, wrCmd, startLBA, endLBA, sectCnt, stepSize, thr0, thr1, thr2, COMPARE_FLAG=0, wrCmd2 = None, ovPrm = None, exc = 1, timeout = None):
      objMsg.printMsg('wrCmd=%s, startLBA=%s, endLBA=%s, sectCnt=%s, stepSize=%s, thr0=%s, thr1=%s, thr2=%s, COMPARE_FLAG=%s, wrCmd2 = %s, ovPrm = None, exc = 1, timeout = None' %
                      (wrCmd, int(startLBA), int(endLBA), int(sectCnt), int(stepSize), thr0, thr1, thr2, COMPARE_FLAG, wrCmd2,))


      sdbpComm.NEW_ESLIP_DIAG = False
      self.__SetupCommMode(sdbpForce = True)

      RetThr0, RetThr1, RetThr2 = 0, 0, 0         #Set default return value
      CCTSetting = 0
      #IRSATA.251779.BAN20.SI.4C.251779.INC.LOD code fixed issue
      #[thr0, thr1, thr2] = [(i*1000) for i in [thr0, thr1, thr2]]       #For fix SI bug, CPC was counting CCT in millisecond, and SI in usec
      minThresh = min(thr0, thr1, thr2)
      maxThresh = max(thr0, thr1, thr2)
      binStep = int(minThresh/5)                       #Divide bin step
      totalBin = min(int(maxThresh/binStep), 50)       #max bin number = 50

      wrmode  = {2:1}.get(self.ConvertWRmode(wrCmd), 0) #translates the ata command to a cpc mode... max internally is 1

      curSeq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

      data = sdbpCmds.fullPackSequentialTiming( wrmode, startLBA, endLBA, sectCnt, stepSize, timeout = timeout )

      self.makeCCT_DistributionTbl(data, binStep, totalBin)

      return PASS_RETURN


   
   ############################################### Start of Bluenun Methods ################################################
   
   def BluenunSlide(self, startLBA, endLBA, sectCnt, numEntriesAvgTimeList, autoMultiplier, regionSize, regionLimit, enableLogging, cmdRetry):
      #
      #  Based on SIC BluenunSlide test
      #
     
      wrCmd = 0x25                                      # ReadDMAExt
      wrmode  = {2:1}.get(self.ConvertWRmode(wrCmd), 0) #translates the ata command to a cpc mode... max internally is 1

      AvgCctListSize = 100


      
      totalLBA    = endLBA - startLBA + 1                     
      totalBytes  = totalLBA * 512                              
      totalGB     = totalBytes / 1073741824             # Bytes in a GigaByte, as defined in SIC code                          
      testRegions = totalGB / regionSize       
      slowReadLimit   = testRegions * regionLimit
      slowReadLog = []
      regionSizeHostLbas = (regionSize * 1073741824)/512
      

      srCount = 0
      toe = 0
      
	   
      #### prefill list with first 100 reads ####
      slba = startLBA 
      elba = (sectCnt * AvgCctListSize) + slba
          

      self.__SetupCommMode(sdbpForce = True)

      res = sdbpCmds.lbaSequentialTiming(wrmode, slba, elba, XferLenInHostBlks = sectCnt, ErrorFlag = 0, timeout = 30)

      cctList = [i[2] for i in res]                                           
      #### End prefill list ####

     
      slba =  res.pop()[0] + sectCnt                                           # start after end of list


      while slba < totalLBA:                                                   # span of min to max LBA
         elba = min(totalLBA, slba + regionSizeHostLbas)                       # how far will this read take us
         if elba <= totalLBA:														          # dont read beyond the end of the region
            
            rc = sdbpCmds.lbaSequentialTiming(wrmode, slba, elba, XferLenInHostBlks = sectCnt, ErrorFlag = 0, timeout = 5000)     # timed read

            newCct = rc[0][2]                                                  # get the 3rd item in 1st tuple which is a read of sectCnt

            self.checkCurrentAverage(slowReadLog, cctList, slba, 0, newCct, autoMultiplier)    # region = 0
                                                                             

            if self.timeGreaterThanAverage(cctList, newCct):                   # check time against average
               srCount += 1
               toe += 1                                                        # add another to the count

            #cctList = self.addTime(cctList, newCct)                            # add this time to the list
            self.addTime(cctList, newCct)                            # add this time to the list
           
                                                                  
         slba = elba + 1                                                       # start of next read

      if self.checkSlowReadLimit(slowReadLog, toe, slowReadLimit):
         toe, srCount = self.retrySlowReads( wrmode, cctList, slowReadLog, srCount, toe, sectCnt, cmdRetry )
                    
            
      returndata = {'LLRET': 0, 'REC': len(slowReadLog), 'TOE': toe, 'SLOWRD': srCount, 'TLIM': slowReadLimit}            
      
      return returndata



   def retrySlowReads(self, wrmode, cctList, slowReadLog, srCount, toe, sectCnt, cmdRetry):
      for record in slowReadLog:
         if record['retries'] < cmdRetry:
            lba = record['lba']
            elba = lba
            slba = lba - (20 * sectCnt)       # 20 preceding reads, same as SIC
            res = sdbpCmds.lbaSequentialTiming(wrmode, slba, elba, XferLenInHostBlks = sectCnt, ErrorFlag = 0, timeout = 30)
            newCct = res[0][2]
            if self.timeGreaterThanAverage(cctList, newCct):
               srCount += 1
            else:
               toe -= 1	
            record['retries'] += 1
      return (toe, srCount)	



   ###@staticmethod
   def timeGreaterThanAverage(self, cctList, newCct):
      #
      # Compares the current read (newCct) against the average of the last 100 reads
      #
      return newCct > MathLib.mean(cctList)         


   def checkCurrentAverage(self, slowReadLog, cctList, lba, region, newCct, autoMultiplier):
      average = MathLib.mean(cctList) * autoMultiplier
      overLimit = (average * 10) > average
      if overLimit:
         self.addRecordToSlowReadLog(slowReadLog, lba, region, newCct, average, autoMultiplier)


   ### @staticmethod
   def addRecordToSlowReadLog(self, slowReadLog, lba, region, newCct, average, multiplier):
      record = {}
      record['lba'] = lba
      record['region'] = region
      record['average'] = average/multiplier
      record['retries'] = 0

      slowReadLog.append(record)

  
   ### @staticmethod
   def addTime(self, cctList, newCct):
      #
      # remove the oldest time from list and add new time to end of list
      # to create a sliding window of averages
      #
      cctList.pop(0)                     
      cctList.append(newCct)
      

      
   def checkSlowReadLimit(self, slowReadLog, toe, slowReadLimit):
      return toe <= slowReadLimit
      
   
   ############################################  End of Bluenun methods ###########################################


   def getCAPSettings (self, ParmID = None, printResult = 0):
      ''' Get Cap Value as specified by paramter ID
      '''

      self.__SetupCommMode(sdbpForce = True)
      data = 512*'0'
      ValDict = {0x00:[0,'L',"ValidationKey"],
                 0x01:[4,'8s',"HDASerialNum"],
                 0x02:[12,'12s',"PCBASerialNum"],
                 0x03:[24,'10s',"PCBAPartNum"],
                 0x04:[34,'B',"HeadCount"],
                 0x05:[35,'B',"NodeNameValidKey"],
                 0x06:[36,'8s',"NodeName"],
                 0x07:[44,'B',"ProdFamID"],
                 0x08:[45,'B',"ProdFamMemID"],
                 0x09:[46,'6s',"PCBABuildCode"],
                 0x0A:[52,'140s',"ASCII-Info"],
                 0x0B:[192,'14s',"FirmwareKey"],
                 0x0C:[206,'H',"FirmwareChecksum"],
                 0x0D:[208,'8s',"DateOfMfg"],
                 0x0E:[216,'B',"Destroked Buf Size Index"],
                 0x0F:[217,'4s',"FinalMfgOperation"],
                 0x10:[221,'4s',"FinalMfgErrCode"],
                 0x11:[225,'B',"SysAreaPrepState"],
                 0x12:[226,'B',"SptAutoRunDelay"],
                 0x13:[227,'B',"ReservedBytes"],
                 0x14:[510,'H',"Checksum"],
                 0x15:[228,'40s',"ExtModelNum"],
                 0x16:[268,'40s',"IntModelNum"],
                 0x17:[308,'Q',"IDEMACapacity"],
                }
      if ParmID == None:
         value = {}
         for parmIdVal in ValDict.keys():
            _, _, dataBlock = sdbpCmds.getCAPsettings(ParmID = parmIdVal)
            if not testSwitch.virtualRun:
               data = dataBlock[1:]
            value[ValDict[parmIdVal][2]] = struct.unpack(ValDict[parmIdVal][1],data[ValDict[parmIdVal][0]:(ValDict[parmIdVal][0] + struct.calcsize(ValDict[parmIdVal][1]))])
         if printResult:
            objMsg.printMsg("All Cap Values : %s" %(value))
         return value
      else:
         _, _, dataBlock = sdbpCmds.getCAPsettings(ParmID = ParmID)
         if not testSwitch.virtualRun:
            data = dataBlock[1:]
         paramID = struct.unpack('B',dataBlock[8])
         try:
            if ParmID in ValDict.keys():
               value = struct.unpack(ValDict[ParmID][1],data[ValDict[ParmID][0]:(ValDict[ParmID][0] + struct.calcsize(ValDict[ParmID][1]))])
               if type(value) == tuple:
                  value = value[0]
         except:
            objMsg.printMsg("Error in function get CAP settings")
         return value

