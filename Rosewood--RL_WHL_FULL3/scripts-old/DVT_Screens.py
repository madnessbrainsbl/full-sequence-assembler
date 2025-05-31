#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Interface calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DVT_Screens.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DVT_Screens.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
import MessageHandler as objMsg
import time
import ScrCmds
from State import CState
from PowerControl import objPwrCtrl
from base_IntfTest import CCriticalEvents, CSmartDefectList
import SATA_SetFeatures
from Exceptions import CRaiseException
from ICmdFactory import ICmd
from IntfClass import CIdentifyDevice
from Rim import objRimType
import serialScreen, sptCmds

###########################################################################################################
class CVerifyDOS(CState):
   """
      Verify DOS can correct field based ATI issues. State can only run in CPC Cell
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      try:
         dosVerParams = TP.DosVerifyParams.copy()
      except:
         objMsg.printMsg("DosVerifyParams not found in TP using defaults.")
         dosVerParams = {}

      numRanges = dosVerParams.setdefault('numRangesPerHead',2) * self.dut.imaxHead

      startLBA = dosVerParams.setdefault('startLBA',65000)
      if testSwitch.FE_0127527_426568_STEPLBA_SET_BY_TEST_PARAMETER_IN_DOS_VERIFY:
         stepLBAvalue=getattr(TP,'stepLBAinCVerifyDOS',130000)
         stepLBA = dosVerParams.setdefault('stepLBA',stepLBAvalue)
      else:
         stepLBA = dosVerParams.setdefault('stepLBA',130000)
      numWrites = dosVerParams.setdefault('numWrites',10000)
      sctrCnt = dosVerParams.setdefault('sctrCnt',256)

      maxLBA = (stepLBA*numRanges) + startLBA
      max1BCount = dosVerParams.setdefault('max1BCount',50)
      maxPListErrors = dosVerParams.setdefault('maxPListErrors',50)
      maxGListErrors = dosVerParams.setdefault('maxGListErrors',0)
      timeout = dosVerParams.setdefault('timeout',100000*self.dut.imaxHead)
      spc_id = dosVerParams.setdefault('spc_id',1)

      dummyMax1B = numWrites*numRanges

      objMsg.printMsg("Verifying DOS Functionality with parameters:")
      data = '\n'.join(["%-20s:\t%s" % (key,value) for key,value in dosVerParams.iteritems()])
      objMsg.printMsg("\n%s" % data)

      #Get initialDefects
      pInitial, gInitial = self.getNumDefects(0)
      InitialnumECCounts = self.getNumCECounts(dummyMax1B)

      #Make sure we write zero pattern
      ICmd.ClearBinBuff(CPC_WRITE_BUFFER, exc = 1)

      if not objRimType.IOInitRiser():
         #initiators don't support concurrent spt and interface functionality
         if testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser():
            sptCmds.sendDiagCmd(CTRL_Z,altPattern='T>')
            sptCmds.sendDiagCmd(CTRL_D)
            sptCmds.sendDiagCmd(CTRL_T)
         else:
            ICmd.SerialCommand(CTRL_Z, 'T>', 1)
            ICmd.SerialCommand(CTRL_D, '0 0 1', 1)
            ICmd.SerialNoTimeout(CTRL_T, 1)
         time.sleep(5) #give the drive a couple secs to re-init interface

      ICmd.HardReset()
      ICmd.IdentifyDevice()
      #Setup Test conditions
      ICmd.SetRFECmdTimeout(timeout)
      SATA_SetFeatures.disable_WriteCache()
      SATA_SetFeatures.disable_ReadLookAhead()


      try:
         try:

            objMsg.printMsg("Writing LBA's %X-%X by %X %d times" % (startLBA, maxLBA, stepLBA, numWrites))
            #We write the ranges
            ICmd.SequentialWriteDMA(startLBA, maxLBA, stepLBA, sctrCnt, 0, 0, numWrites, exc = 1, timeout = timeout)
            ICmd.FlushCache(exc = 1, timeout = timeout)


            objMsg.printMsg("Reading LBA's %X-%X by %X" % (startLBA, maxLBA, stepLBA,))
            #We read the ranges checking for BBM's
            ICmd.SequentialReadDMA(startLBA, maxLBA, stepLBA, sctrCnt, 0, 0, 1, exc = 1, timeout = timeout)
            ICmd.FlushCache(exc = 1, timeout = timeout)

            data = []
            if (not objRimType.IOInitRiser() ):
               #initiators don't support concurrent spt and interface functionality
               subData = None
               while not subData == '':
                  ret = ICmd.GetSerialTail(2048)
                  subData = ret.get('DATA','')
                  data.append(subData)

               ICmd.SerialDone()

            #Get final num defects
            pFinal, gFinal = self.getNumDefects(1)
            FinalnumECCounts = self.getNumCECounts(dummyMax1B)

            glistGrowth = (gFinal - gInitial)
            plistGrowth = (pFinal - pInitial)
            EcGrowth = (FinalnumECCounts - InitialnumECCounts)

            curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
            self.dut.objSeq.curRegSPCID = spc_id
            self.dut.dblData.Tables('P_DOS_VERIFY').addRecord(
               {
               'SPC_ID': spc_id,
               'OCCURRENCE': occurrence,
               'SEQ': curSeq,
               'TEST_SEQ_EVENT': testSeqEvent,
               'NUM_GLIST_DEFECTS': glistGrowth,
               'NUM_PENDING_LIST_DEFECTS': plistGrowth,
               'NUM_DOS_CRITICAL_EVENTS': EcGrowth,
               })
            objMsg.printDblogBin(self.dut.dblData.Tables('P_DOS_VERIFY'))

            if (glistGrowth > maxGListErrors):
               ScrCmds.raiseException(10482, "Excessive G list growth: %d GTE %d" % (glistGrowth, maxGListErrors))
            elif (plistGrowth > maxPListErrors):
               ScrCmds.raiseException(10482, "Excessive P list growth: %d GTE %d" % (plistGrowth, maxPListErrors))
            elif (EcGrowth > max1BCount):
               ScrCmds.raiseException(10482, "Exessive DOS Events %d GTE %d" % (EcGrowth, max1BCount))
         except:
            objMsg.printMsg("SPT Data collected during dos verify:\n%s" % (''.join(data),))
            raise
      finally:
         try:
            SATA_SetFeatures.enable_ReadLookAhead()
            SATA_SetFeatures.enable_WriteCache()
         except:
            #incase drive not responding
            pass
         ICmd.SetRFECmdTimeout(TP.prm_IntfTest.get("Default ICmd Timeout", 180000))


   def getNumCECounts(self, max1BCount):
      #Dump critical events to view the x1B errors and apply spec in max1BCount
      from Exceptions import CDblogDataMissing

      key = 'CE_0x1b'
      CEDisplay = CCriticalEvents(self.dut, params = {'PARAM_NAME' : str({key:max1BCount})})
      CEDisplay.run()

      try:
         if testSwitch.BF_0150238_231166_P_FIX_DOS_VERIFY_1B_PARSE:
            dt = self.dut.dblData.Tables('CRITICAL_EVENT_LOG').chopDbLog(parseColumn = 'ERR_CODE', matchStyle = 'match' , matchName = '27',)
         else:
            dt = self.dut.dblData.Tables('CRITICAL_EVENT_LOG').chopDbLog(parseColumn = 'ERR_CODE', matchStyle = 'match' , matchName = key,)
         num1BCount = len(dt)
      except (CDblogDataMissing, KeyError, CRaiseException):
         num1BCount = 0

      return num1BCount


   def getNumDefects(self, spc_id):
      #Dump the number of defects and return P list and G list count
      self.curSeq,self.occurrence,self.testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      self.dut.objSeq.curRegSPCID = spc_id

      if testSwitch.BF_0143469_231166_P_DISABLE_G_LIST_ABSOLUTE_FAIL_DOS_VER:
         CNumDefs = CSmartDefectList(self.dut, params = {'failForLimits': 0})
      else:
         CNumDefs = CSmartDefectList(self.dut)
      CNumDefs.run()

      try:
         numPendDef = self.dut.dblData.Tables('P_PENDING_DEFECT_LIST').tableDataObj()[-1]['TOTAL_DFCTS_DRIVE']
      except:
         numPendDef = 0

      try:
         #This method in CSmartDefectList returns the count not the items
         numGrownErrors = self.dut.dblData.Tables('P_GROWN_DEFECT_LIST').tableDataObj()[-1]['ERR_LENGTH']
      except:
         numGrownErrors = 0

      return numPendDef, numGrownErrors


###########################################################################################################
class C4kReprep(CState):
   """
      Class that performs Full Pack Write using SequentialWriteDMAExt
         Error reporting is enabled.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import SATA_SetFeatures
      stepLBA = sctCnt = 256

      ICmd.HardReset()

      #Disable smart logging
      SATA_SetFeatures.disableLPSRMWLogging(clearLogs=True)

      id = CIdentifyDevice()

      objMsg.printMsg("DebugData buffer dump")
      objMsg.printBin(ICmd.GetBuffer(RBF,0,512)['DATA'][318:319])

      if ( id.ID['LPS_LogEnabled'] or id.ID['RMW_LogEnabled'] ):

         ScrCmds.raiseException(11044, "Failed to disable LPS and RMW logging!.")

      objMsg.printMsg("Logging Disable Successful")

      #Set 0's patt
      result = ICmd.ClearBinBuff(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(12657, "Failed to fill buffer for zero write")

      #Get max lba
      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1

      objMsg.printMsg("Now writing lba 0 to 0x%X" % maxLBA)
      #full pack write read
      result = ICmd.SequentialWRDMAExt(0, maxLBA, stepLBA, sctCnt)
      objMsg.printMsg('Full Pack Zero Write-Read - Result %s' %str(result))

      if result['LLRET'] != 0:
         ScrCmds.raiseException(12657, "Full Pack Zero Write-Read Failed")

      result = ICmd.FlushCache(exc=1)

      objMsg.printMsg('Full Pack Zero Write-Read flush - Result %s' %str(result))
      if result['LLRET'] != 0:
         ScrCmds.raiseException(12657, "Full Pack Zero Write-Read Failed")


class CTestDITS(CState):
   """
      Test DITS cmds
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      ICmd.HardReset()
      ICmd.SequentialWriteDMAExt(0,1)
      ICmd.UnlockFactoryCmds()
      ICmd.ClearFormatCorrupt()
      ICmd.GetPreampTemp()


if testSwitch.FE_0131249_231166_ASD_BUTTERFLY_PERF_SCRN:
   class CASDPerfVerification(CState):
      """
         Test DITS cmds
      """
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)
         self.dut = dut
      #-------------------------------------------------------------------------------------------------------
      def run(self):

         """This test measures the total time it takes to read access a fixed set of 1000 LBAs through the SATA interface.  The LBAs are accessed alternately from OD to ID moving towards the center of the LBA space (butterfly test).  Eight (8) sectors are read at a time with a step of 16000 LBAs.  The reason for the number of seeks is to ensure the cache does not contain valid data for the subsequent read.  Once the set of LBAs are read initially, execution is paused for 30 seconds while the drive pins the read LBAs.  After the pause, the same LBAs are re-read and timed.  If the 2nd set of reads is less than or equal to 10 seconds, the test Passes. If greater than 10 seconds, the test Fails. This test will have to be implemented after the TGTB download in CUT2 where the ASD/NVC F3 Build Target is loaded.
            Example of the first 6 loops out of 1000 (each set of reads are identical):

            Read 8 LBAs starting at LBA 0
            Read 8 LBAs starting at MAX LBA - 8
            Read 8 LBAs starting at LBA 16000
            Read 8 LBAs starting at MAX LBA - 8 - 16000
            Read 8 LBAs starting at LBA 32000
            Read 8 LBAs starting at MAX LBA - 8 - 32000
         """

         params = {
            'readSize': 8,
            'stepSize': 16000,
            'pause': 30,
            'spec': 10,
            'loops': 1000,
            }

         params.update(getattr(TP, 'ASDPerfVerification_prm',  {}))

         objMsg.printMsg("Running CASDPerfVerification with parameters:")
         objMsg.printDict(params)

         #Get max lba
         maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1

         #Set 0's patt
         result = ICmd.ClearBinBuff(WBF)

         loopList = []
         readSize = params['readSize'] #local so it is faster

         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)


         for trial in range(2):
            loopCnt = 0
            iterationCnt = 0
            startTime = time.time()

            if DEBUG:
               if trial == 0:
                  objMsg.printMsg("Baseline.")
               else:
                  objMsg.printMsg("Spec run.")

            odd = True
            startLBA1 = 0
            startLBA2 = maxLBA-params['stepSize']-readSize

            while loopCnt < params['loops']:
               if DEBUG:
                  objMsg.printMsg("Loop #%d" % loopCnt)

               #take it from the front of the list
               if odd:
                  startLBA1 = startLBA1 + (iterationCnt*params['stepSize'])
                  if startLBA1 > maxLBA:
                     startLBA1 = 0
                     startLBA2 = maxLBA
                     iterationCnt = 0
                     startLBA1 = startLBA1 + (iterationCnt*params['stepSize'])

                  startLBA = startLBA1
               else:
                  startLBA2 = startLBA2 - (iterationCnt*params['stepSize'])-readSize
                  if startLBA2 < 0:
                     iterationCnt = 0
                     startLBA1 = 0
                     startLBA2 = maxLBA
                     startLBA2 = startLBA2 - (iterationCnt*params['stepSize'])-readSize
                  startLBA = startLBA2

               odd = not odd

               if DEBUG:
                  objMsg.printMsg("Reading from 0x%X to 0x%X" % (startLBA, startLBA + readSize))

               ICmd.SequentialReadDMAExt(startLBA, startLBA + readSize, readSize, readSize, 0, 0, 1, exc = 1, timeout = 120)
               #ICmd.SeqReadDMAExtPerf(startLBA, startLBA + readSize, readSize, exc = 1, timeout = 120)

               #re-add it to the end- for circular buffer
               loopList.append(startLBA)

               loopCnt += 1
               iterationCnt += 1

            result = ICmd.FlushCache(exc=1)

            execTime = time.time()-startTime
            if trial == 0:
               mode = 'Baseline'
               spc_id = 1
            else:
               mode = 'Spec'
               spc_id = 2

            objMsg.printMsg("%s loop time %2.2f" % (mode, execTime))

            self.dut.dblData.Tables('P_ASD_PERFORMANCE_SCRN').addRecord(
               {
               'SPC_ID':               spc_id,
               'OCCURRENCE':           occurrence,
               'SEQ':                  curSeq,
               'TEST_SEQ_EVENT':       testSeqEvent,
               'TEST_MODE':            mode,
               'TEST_TIME':            execTime,
               })

            if trial == 0:
               objMsg.printMsg("Sleeping %d seconds." % (params['pause'],))
               time.sleep(params['pause'])

         objMsg.printDblogBin(self.dut.dblData.Tables('P_ASD_PERFORMANCE_SCRN'))
         if execTime > params['spec']:
            ScrCmds.raiseException(42163, "2nd set of read times for screen was %2.2f and was GTT spec of %2.2f" % (execTime, params['spec']))

if testSwitch.FE_0135930_231166_ADD_SMART_SRVO_ERR_SCRN:
   class CSmartServoErrorScrn(CState):
      """
         Verify Smart Servo Error Counters are below a threshold
      """
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)

      #-------------------------------------------------------------------------------------------------------
      def run(self):
         from SmartFuncs import smartAttrObj, smartFrameObj

         smartFrameObj.loadSmartFrames()

         for head, errors in enumerate(smartFrameObj.getSeekErrors()):
            objMsg.printMsg("Smart Frame for H%X indicates there were 0x%X seek errors" % (head, errors ))

            self.dut.driveattr['SMRT_SK_ERRS_H%X' % head] = errors
            errorLimit = getattr(TP, 'prm_SmartSeekErrorLimit', False)

            if errorLimit and errorLimit <= errors:
               ScrCmds.raiseException(10502, "Excessive smart seek errors reported on head 0x%X= 0x%X" % (head, errors))


class CVerify28BitLBA(CState):
      """
         Verify the 28bit lba value is railed if 48bit cap > rail value
      """
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)

      #-------------------------------------------------------------------------------------------------------
      def run(self):

         # Reload the defaults from power on- protect against volitility in measurement from previous download
         objPwrCtrl.powerCycle()

         oIdd = CIdentifyDevice()
         requiredVal = rail = 0x0FFFFFFF

         if oIdd.ID['IDDefault48bitLBAs'] <= rail:
            # Handle non extended drive or HPA/DCO set
            requiredVal = oIdd.ID['IDDefault48bitLBAs']

         if testSwitch.BF_0157252_231166_P_USE_NON_EXT_FIELD_28_BIT_VALIDATION:
            #validate the 28bit non-extended field
            if oIdd.ID['IDDefaultLBAs'] != requiredVal and not testSwitch.virtualRun:
               ScrCmds.raiseException(14760, "28Bit LBA is invalid for extended volume size. %X != %X" % (oIdd.ID['IDDefaultLBAs'] , requiredVal))
            else:
               objMsg.printMsg("28Bit LBA is valid for extended volume size. %X == %X" % (oIdd.ID['IDDefaultLBAs'] , requiredVal))
         else:
            #validate the 28bit non-extended field
            if oIdd.ID['IDCurLBAs'] != requiredVal and not testSwitch.virtualRun:
               ScrCmds.raiseException(14760, "28Bit LBA is invalid for extended volume size. %X != %X" % (oIdd.ID['IDCurLBAs'] , requiredVal))
            else:
               objMsg.printMsg("28Bit LBA is valid for extended volume size. %X == %X" % (oIdd.ID['IDCurLBAs'] , requiredVal))


class CVerifyMediaCache(CState):
      """
         Verify the media cache is valid
      """
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)

      #-------------------------------------------------------------------------------------------------------
      def run(self):
         if not testSwitch.extern.FE_0116076_355860_MEDIA_CACHE:
            if testSwitch.FE_0154003_231166_P_ALLOW_BYPASS_MC_CMDS_BASED_F3_FLAG and not testSwitch.virtualRun:
               objMsg.printMsg("FE_0116076_355860_MEDIA_CACHE in F3 is disabled... bypassing state")
               return
            else:
               objMsg.printMsg("FE_0116076_355860_MEDIA_CACHE not detected but FE_0154003_231166_P_ALLOW_BYPASS_MC_CMDS_BASED_F3_FLAG is false- running state.")
         import SCT_Cmd

         if testSwitch.FE_0147914_231166_P_ADD_SUPPORT_MC_INIT_DIAG:
            import serialScreen, sptCmds

            self.dut.driveattr['MC_VALID'] = 0

            try:
               SCT_Cmd.VerifyMC()
            except:
               oserial = serialScreen.sptDiagCmds()
               sptCmds.enableDiags()
               oserial.initMCCache()
               sptCmds.enableESLIP()

               #give drive time to re-init
               time.sleep(5)
               ICmd.HardReset()

               #if it passes this time then set valid
               objPwrCtrl.powerCycle()
               SCT_Cmd.VerifyMC()
               self.dut.driveattr['MC_VALID'] = 1

            else:
               self.dut.driveattr['MC_VALID'] = 1
               objMsg.printMsg("MC Verification passed")
         else:
            try:
               SCT_Cmd.VerifyMC()
            except:
               self.dut.driveattr['MC_VALID'] = 0
               raise
            else:
               self.dut.driveattr['MC_VALID'] = 1
               objMsg.printMsg("MC Verification passed")


class CVerifyUserSlipList(CState):
      """
         Query the user slip list count and fail if it has decreased. Utilizes the drive attribute SLIP_LIST_ENTRIES.
         REQUIRES: F3 code with diagnostics.
      """
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         params.setdefault('startup',1)
         self.params = params

         depList = []
         CState.__init__(self, dut, depList)

      #-------------------------------------------------------------------------------------------------------
      def run(self):
         oSerial = serialScreen.sptDiagCmds()
         if self.params['startup']:
            sptCmds.enableDiags()


         prev = self.dut.driveattr.get('SLIP_LIST_CNT', 0)
         resDict = oSerial.dumpUseSlipList(summaryOnly = True)
         
         if int(prev) > int(self.dut.driveattr.get('SLIP_LIST_CNT', 0)):
            ScrCmds.raiseException(10446, "SLIP_LIST_CNT decreased since last call. %s < %s" % (self.dut.driveattr.get('SLIP_LIST_CNT', 0), prev))

         if self.params['startup']:
            sptCmds.enableESLIP()

