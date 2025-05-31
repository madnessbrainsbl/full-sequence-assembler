#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Customer Screens
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/16 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CustomerScreens.py $
# $Revision: #7 $
# $DateTime: 2016/12/16 00:51:36 $
# $Author: hengngi.yeo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CustomerScreens.py#7 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
import ScrCmds
from IntfClass import CIdentifyDevice
import re,struct, traceback, time, random
from Rim import objRimType, theRim
from Test_Switches import testSwitch
from PowerControl import objPwrCtrl
from Drive import objDut
from ICmdFactory import ICmd
from Process import CProcess
import sptCmds
from Carrier import theCarrier
from Utility import CUtility
import SATA_SetFeatures
import CommitServices

DEBUG = 0

###########################################################################################################
class CDisableTempMSR(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut

      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from serialScreen import sptDiagCmds
      oSerial = sptDiagCmds()

      oSerial.enableDiags()
      oSerial.SetAppleTempTransmissionInAMPS(enable = False)
      sptCmds.enableESLIP()

###########################################################################################################
class CBluenunScanAuto(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut

      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      ## UDMASpeed = GetUDMASpeed('FIN_wrt_xfer')

      #Get ID data
      oIdentifyDevice = CIdentifyDevice()


      UDMASpeed = 100
      result = ICmd.SetFeatures(0x03,UDMASpeed)['LLRET']
      if result != OK:
         objMsg.printMsg('BlueNunScan Failed SetFeatures - Transfer Rate = UDMA-%d' % UDMASpeed)
      else:
         objMsg.printMsg('BlueNunScan Seq LBAs Passed SetFeatures - Transfer Rate = UDMA-%d' % UDMASpeed)

      start_lba  = 4

      end_lba = self.dut.IdDevice["Max LBA Ext"] ##ID_data['Max_48lba']

      prm_blueNunScanAuto  = getattr(TP, 'prm_blueNunScanAuto',{})

      cmdPerSample = prm_blueNunScanAuto.get('cmd_per_sample',4)
      sampPerReg = prm_blueNunScanAuto.get('Samples Per Reg',125)
      blueNunLogTmo = prm_blueNunScanAuto.get('BlueNun Log TMO',1)
      maxGroupRetry = prm_blueNunScanAuto.get('BlueNun Group Retries', 1)
      maxTotalRetry = prm_blueNunScanAuto.get('BlueNun Max Retries', 50000)
      autoMultiplier = prm_blueNunScanAuto.get('BlueNun Auto Multi', 12)
      if objRimType.IOInitRiser() or (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()):
         autoMultiplier = int(autoMultiplier *10) #CPC internally multiplies it by 10
      sect_cnt = prm_blueNunScanAuto.get('sect_cnt', 256)
      totalCmdTimeout = prm_blueNunScanAuto.get('timeout',14400)

      capacity = (end_lba-start_lba+1)*self.dut.IdDevice['Logical Sector Size']/1000000000
      errorLimit = capacity/3
      timeoutErrCountLimit = prm_blueNunScanAuto.get('ERROR_COUNT_LIMIT', errorLimit)
      maxTotalRetry = prm_blueNunScanAuto.get('BlueNun Max Retries', errorLimit*3)

      objMsg.printMsg('BlueNunAuto Read Start LBA=%d Max LBA=%d Sec Cnt=%d Multiplier=%d Cmds Per Sample=%d Samples/Reg=%d ErrCountLimit=%d maxTotRetry=%d maxGrpRetry=%d'  % \
                (start_lba, end_lba, sect_cnt, autoMultiplier, cmdPerSample, sampPerReg, timeoutErrCountLimit, maxTotalRetry, maxGroupRetry))

      #Increase the RFE timeout since blue nun could take some time
      ICmd.SetRFECmdTimeout(totalCmdTimeout)

      data = ICmd.BluenunAuto(start_lba, end_lba, sect_cnt, autoMultiplier, cmdPerSample, sampPerReg, blueNunLogTmo, maxTotalRetry, maxGroupRetry, timeout = totalCmdTimeout)
      objMsg.printMsg('Blue Nun Return Data: %s' % (data,))

      #Reset RFE command timeout to nominal
      ICmd.SetRFECmdTimeout(TP.prm_IntfTest["Default ICmd Timeout"])

      result = data['LLRET']
      timeoutErrCount = int(data.get('TOE',0))
      resultRecords = cmdPerSample * timeoutErrCount

      if result != OK:
         objMsg.printMsg('BlueNunAuto Test Failed (Non Parametric): %s' % repr(data))
         ScrCmds.raiseException(14520,"BlueNun Scan")
      else:

         #result of True means test passed
         #result of False means test failed
         if timeoutErrCount > timeoutErrCountLimit:
            result = False
            objMsg.printMsg('BlueNunScan Failed %s' % `data`)
         else:
            objMsg.printMsg('BlueNunScan Passed %s' % `data`)
            result = True

         #APPLE spec is that if this drive ever failed blue nun then it can
         #  NEVER commmit to apple so lets set the status to fail if it ever failed
         if self.dut.driveattr.get("BLUENUNSCAN",None) == 'FAIL' or result == False:
            if result == True:
               #  We set this to rerun_pass so people don't look at a drive that passed the current
               #     blueNun and wonder why the attribute still says fail
               #     RERUN_PASS still isn't shippable but just more informative
               self.dut.driveattr["BLUENUNSCAN"] = "RERUN_PASS"
            else:
               self.dut.driveattr["BLUENUNSCAN"] = "FAIL"

            #Make sure this is graded as failed
            result = False
            objMsg.printMsg('BlueNunScan Failed previously forcing failure.')
         else:
            self.dut.driveattr["BLUENUNSCAN"] = "PASS"
            result = True


         self.dumpBlueNunLog(data, resultRecords)

         #Update the scoring parametric table to score against
         self.dut.dblData.Tables('P_BLUE_NUN_SCORE').addRecord({
               'PASS': int(result)
            })
         #if result != OK:
         #ScrCmds.raiseException(14520,"BlueNun Scan")

   def dumpBlueNunLog(self, res, resultRecords):

      if not resultRecords:
         #no records to parse
         return

      import struct
      specm = res['SPECM']

      #Structure definitions
      littleEndian = "<"
      dataFmt = "L"

      #Pre calculate the specifiers to cut down on loop exec cost
      dataSize = struct.calcsize(dataFmt)
      numFields = 3 #lbaLSW, lbaMSW, timeout
      recordSize = numFields*dataSize
      recordFmt = littleEndian + (dataFmt*numFields)
      outputData = []

      #Get the blue nun scan log file from the CPC
      res = ICmd.GetFile('BluenunScanLog',0,recordSize * resultRecords,1)
      data = res['DATA']
      if len(data) == 0:
         #No data to parse
         return

      #for each record width in the returned data
      for recOffset in xrange(0,len(data), recordSize):
         #extract this record
         record = data[recOffset:recOffset+recordSize]

         try:
            #extract the components
            lbaLSW, lbaMSW, timeout = struct.unpack(recordFmt, record)

            #Add the dblog Data
            self.dut.dblData.Tables('P_BLUE_NUN_SCAN').addRecord({
               'LBA': "%d" % ((lbaMSW <<32) + lbaLSW,),#"%08X%08X" % (lbaMSW, lbaLSW),
               'CMD_TIME': timeout,
               'MAX_CMD_TIME': specm,
            })
         except struct.error:
            import traceback
            objMsg.printMsg("Error in dumpBlueNunLog: %s\nDATA:%s" % (traceback.format_exc(),data))
            objMsg.printBin(data)
      #Output the dblog data to the results file
      objMsg.printDblogBin(self.dut.dblData.Tables('P_BLUE_NUN_SCAN'))

###########################################################################################################
class CBluenunSlide(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut

      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      ## UDMASpeed = GetUDMASpeed('FIN_wrt_xfer')

      if testSwitch.BF_0196490_231166_P_FIX_TIER_SU_CUST_TEST_CUST_SCREEN:
         if 'AP2' in self.dut.driveattr.get('CUST_TESTNAME', DriveAttributes.get('CUST_TESTNAME', '')):
            objMsg.printMsg("Bypassing AP2 as already performed.")
            return

      if testSwitch.FE_0161626_231166_P_DISABLE_TEMP_MSR_BLUE_NUN:
         CDisableTempMSR(self.dut).run()


      #Get ID data
      oIdentifyDevice = CIdentifyDevice()

      if testSwitch.FE_0179705_231166_P_RUN_BLUE_NUN_AT_1_5G:
         UDMASpeed = 0x40+ 1
      else:
         UDMASpeed = 0x40+ self.dut.IdDevice['UDMA Mode Supported']

      result = ICmd.SetFeatures(0x03,UDMASpeed)['LLRET']
      if result != OK:
         objMsg.printMsg('BlueNunScan Failed SetFeatures - Transfer Rate = UDMA-%d' % UDMASpeed)
      else:
         objMsg.printMsg('BlueNunScan Seq LBAs Passed SetFeatures - Transfer Rate = UDMA-%d' % UDMASpeed)

      start_lba  = 4

      end_lba = self.dut.IdDevice["Max LBA Ext"] ##ID_data['Max_48lba']

      prm_blueNunScanSlide  = getattr(TP, 'prm_blueNunScanSlide',{})
      sect_cnt = prm_blueNunScanSlide.get('sect_cnt', 256)
      numEntriesAvgTimeList = prm_blueNunScanSlide.get('Size of average time list', 100)
      autoMultiplier = prm_blueNunScanSlide.get('BlueNun Auto Multi', 12.5)
      if objRimType.IOInitRiser() or (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()):
         autoMultiplier = int(autoMultiplier *10) #CPC internally multiplies it by 10
      regionSize = prm_blueNunScanSlide.get('Region size ', 3)
      regionLimit = prm_blueNunScanSlide.get('Errors per region allowed',1)
      enableLogging = prm_blueNunScanSlide.get('Enable Logging',1)
      cmdRetry = prm_blueNunScanSlide.get('Cmd Retries',1)
      totalRecoveredRetriesMultiplier = prm_blueNunScanSlide.get('Total Recovered Retries Multiplier',2)  #number of recovered slow reads allowed
      totalCmdTimeout = prm_blueNunScanSlide.get('timeout',max(5400*self.dut.imaxHead, 5400*3))

      objMsg.printMsg('-'*30+'\nBlueNunSlide Input Parameters\n Start LBA=%d\n Max LBA=%d\n Sec Cnt=%d\n Number of Reads for Spec Avg =%d\n Multiplier=%.1f\n Region Size (GB) = %d\n Region Limit= %d\n Enable Logging = %d\n Retries Per Cmd = %d\n ' % \
                (start_lba, end_lba, sect_cnt, numEntriesAvgTimeList, autoMultiplier, regionSize, regionLimit, enableLogging, cmdRetry))

      #Increase the RFE timeout since blue nun could take some time
      ICmd.SetRFECmdTimeout(totalCmdTimeout)

      data = ICmd.BluenunSlide(start_lba, end_lba, sect_cnt, numEntriesAvgTimeList, autoMultiplier, regionSize, regionLimit,enableLogging,cmdRetry)
      objMsg.printMsg('Blue Nun Return Data: %s' % (data,))

      #Reset RFE command timeout to nominal
      ICmd.SetRFECmdTimeout(TP.prm_IntfTest["Default ICmd Timeout"])


      result = data['LLRET']
      records= int(data.get('REC', 0))     #number of records in the log
      toe    = int(data.get('TOE', 0))     #number of unrecovered slow reads
      slowrd = int(data.get('SLOWRD', 0))  #number of reads including retries that exceeds avg of last 100 read * multiplier
      tlim   = int(data.get('TLIM', 0))    #number of unrecovered slow reads (TOE) allowed
      recoveredRetry = slowrd - toe        #number of slow reads that passed on second retry
      recoveredRetryLimit = tlim* totalRecoveredRetriesMultiplier

      objMsg.printMsg('-'*30+'\nBlueNunAuto Results:\n LLRET=%d\n Unrecovered Reads (TOE) =%d\n Unrecovered Reads Limit =%d\n Total Slow Reads=%d\n Recovered Reads =%d\n'% \
                (result, toe, tlim, slowrd, recoveredRetry))

      if records and not testSwitch.NoIO:
         self.dumpBlueNunLog(records)

      if result != OK:
         if toe > tlim :
            objMsg.printMsg('BlueNunScan Failed (Parametric) for unrecovered slow reads (TOE) exceeding limit (TLIM) %s' % `data`)
            blueNunPass = False
         else:
            objMsg.printMsg('BlueNunAuto Test Failed (Non Parametric): %s' % repr(data))
            if ( not CommitServices.isTierPN( self.dut.partNum ) ) and testSwitch.FE_0208720_470167_P_AUTO_DOWNGRADE_BLUENUN_FAIL_FOR_APPLE:
               try:
                  ScrCmds.raiseException(14520,"BlueNun Scan")
               except:
                  self.dut.CustomCfgTestDone = []
                  self.dut.failBluenun = True
                  self.dut.dblData.Tables('P_SCREENS_STATUS').addRecord(
                  {
                  'SCREEN' : 'BLUENUN_SLIDE', 
                  'STATUS': int(result)
                  })
                  objMsg.printDblogBin(self.dut.dblData.Tables('P_SCREENS_STATUS'))
                  return
            else:
               ScrCmds.raiseException(14520,"BlueNun Scan")
      #elif recoveredRetry > recoveredRetryLimit:   #chu son has decided not to fail drive for this limit at this time.  Maybe in the future
      #      objMsg.printMsg('BlueNunScan Failed (Parametric) for recovered reads (SLOWRD-TOE) exceeding total limit (TLIM*mult) %s' % `data`)
      #      blueNunPass = False
      else:
         objMsg.printMsg('BlueNunScan Passed %s' % `data`)
         blueNunPass = True


      #APPLE spec is that if this drive ever failed blue nun then it can
      #  NEVER commmit to apple so lets set the status to fail if it ever failed
      if not blueNunPass:
         self.dut.driveattr["BLUENUNSCAN"] = "FAIL"
      elif self.dut.driveattr.get("BLUENUNSCAN",None) in ['FAIL', 'RERUN_PASS']:
         #  We set this to rerun_pass so people don't look at a drive that passed the current
         #     blueNun and wonder why the attribute still says fail
         #     RERUN_PASS still isn't shippable but just more informative
         self.dut.driveattr["BLUENUNSCAN"] = "RERUN_PASS"

         objMsg.printMsg('BlueNunScan Failed on previous run.  Forcing failure.')
         blueNunPass = False
      else:
         self.dut.driveattr["BLUENUNSCAN"] = "PASS"

      #Update the scoring parametric table to score against
      self.dut.dblData.Tables('P_BLUE_NUN_SCORE').addRecord(
         {
         'PASS': int(blueNunPass)
         })

      if testSwitch.FE_0161626_231166_P_DISABLE_TEMP_MSR_BLUE_NUN:
         sptCmds.enableDiags()
         oSerial.resetAMPs()
         sptCmds.enableESLIP()


   def dumpBlueNunLog(self, records ):
      '''Display the data in the failure logs.  This shows reads that have exceeded the slow read spec'''
      import struct
      objMsg.printMsg('BlueNun_Slide Failure Data Log')
      objMsg.printMsg('Number of Records to display: %d' % records)

      if testSwitch.virtualRun:
         data = '\x04d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb3\x02\x00\x00\xf3\x03\x00\x00\x04d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb3\x02\x00\x00\xf3\x03\x00\x00'
      else:
         logSize = records * 20
         data = ""
         fileOffset = 0
         while True:
            res = ICmd.GetFile('BNSLog', fileOffset, logSize - fileOffset, 1)
            data = data + res['DATA']
            fileOffset = len(data)
            if len(data) >= logSize:
               break

         if DEBUG:
            objMsg.printMsg('dumpLogResult: %s' %str(res))
            objMsg.printBin(data)
            objMsg.printMsg('Data Len: %d' % len(data))

      log  = '\nRecord  Try LBA              Cmd Time Average\n'                       # table header
      log += '------ ---- ---------------- -------- -------\n'                         # header deliminter
      #       --rrrr llllllllllllllll --tttttt -aaaaaa

      dataFmt = "<L"                                                                   # data format
      dataSize = struct.calcsize( dataFmt )                                            # data size
      try:    # If we cannot read all records, display all that is valid (will be min of 102 records) and pass drive
         for i in range( records ):                                                    # for each record...

            lsdwOffset = i * 20                                                        # record offset (LSDW)
            msdwOffset = lsdwOffset + 4                                                # record offset (MSDW)
            regOffset  = msdwOffset + 4                                                # record offset (region)
            tmoOffset  = regOffset  + 4                                                # record offset (timeout)
            aveOffset  = tmoOffset  + 4                                                # record offset (average)

            lbaLSDW = struct.unpack( dataFmt, data[lsdwOffset:lsdwOffset + 4] ) [0]   # extract record
            lbaMSDW = struct.unpack( dataFmt, data[msdwOffset:msdwOffset + 4] ) [0]
            retry   = struct.unpack( dataFmt, data[regOffset:regOffset   + 4] ) [0]
            timeout = struct.unpack( dataFmt, data[tmoOffset:tmoOffset   + 4] ) [0]
            listAve = struct.unpack( dataFmt, data[aveOffset:aveOffset   + 4] ) [0]

            log = log + "  %3d  %4d %08X%08X   %6d  %6d\n" % (i,retry, lbaMSDW, lbaLSDW, timeout, listAve ) # add record to log

            #Add the dblog Data
            self.dut.dblData.Tables('P_BLUE_NUN_SCAN').addRecord(
               {
               'LBA': "%d" % ((lbaMSDW <<32) + lbaLSDW,),#"%08X%08X" % (lbaMSW, lbaLSW),
               'CMD_TIME': timeout,
               'MAX_CMD_TIME': listAve,
               })
      except:
         objMsg.printMsg("Error in dumpBlueNunLog: %s" % traceback.format_exc())
      log += '------ ---- ---------------- -------- -------\n'                         # end of log

      #objMsg.printDblogBin(self.dut.dblData.Tables('P_BLUE_NUN_SCAN'))
      objMsg.printMsg(log)


###########################################################################################################
class CIopsScreen(CState):
   """
      Write or Read the drive defined in FullPackReadWrite
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProcess = CProcess()

      oProcess.St( TP.set0Pattern_Prm_508 )
      oProcess.St( TP.randWrite_Prm_597 )
      oProcess.St( TP.randRead_Prm_597 )


###########################################################################################################
class CRandomSeekScreen(CState):
   """
      Random Seeks to aggravate the drive
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      base_prm_randomSeekPrm = {
      'spc_id': 1,
      'prm_name': "base_prm_randomSeekPrm",
      'execution_loops': 3,
      'seek_loops': 10000,
      'cmd_timeout': 1,
      }

      prm_randomSeekPrm = getattr(TP,'prm_randomSeekPrm', base_prm_randomSeekPrm)


      execution_loops = prm_randomSeekPrm['execution_loops']
      seek_loops = prm_randomSeekPrm['seek_loops']
      timeout = prm_randomSeekPrm['cmd_timeout'] * seek_loops


      try:

         ICmd.SetRFECmdTimeout(timeout)

         for loop in xrange(execution_loops):
            objMsg.printMsg("Executing loop %d of %d" % (loop, execution_loops))
            self.execRandomSeekScreen(seek_loops, timeout, )

      finally:
         ICmd.SetRFECmdTimeout(TP.prm_IntfTest["Default ICmd Timeout"])

   def execRandomSeekScreen(self, loops, timeout):

      maxLBA = self.dut.IdDevice['Max LBA Ext']

      ########################################################################################
      ScrCmds.insertHeader("Executing ButterflySeekTime")
      ret = ICmd.ButterflySeekTime(maxLBA/loops, timeout = timeout, exc = 1)
      objMsg.printDict(ret)

      ########################################################################################
      ScrCmds.insertHeader("RandomSeek")
      dummySectorCount = 8
      ret = ICmd.RandomSeek(0, maxLBA, loops, dummySectorCount, dummySectorCount, timeout = timeout, exc = 1)
      objMsg.printDict(ret)


###########################################################################################################
class CAVScan(CState):
   """AVScan: Object that reads CCT read log from test 510 and writes Smart log 0x80"""
   #--------------------

   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
      self.byteOffLst = []
      self.SmartData = ''
      self.LogSize = 512

      #--------------------
   def run (self):
      """AVScan: Reads CCT read log from test 510 and writes Smart log 0x80"""

      objMsg.printMsg("Start of AVScan", objMsg.CMessLvl.IMPORTANT)


      #self.failureCriteria = getattr(TP, 'AVScanFailureCriteria', {'write':[(100,3), (270,0)],'read':[(100,3), (270,0)]})
      self.failureCriteria = getattr(TP, 'AVScanFailureCriteria', {'read':[(270,0)],'write':[(400,0)]})  #per Nathan Abelien's AVSCAN pdf spec
      self.avscanLogBoundaries = getattr(TP, 'AVScanLogCriteria', [100,400])
      objMsg.printMsg("AVScan Failure Criteria : %s\n" %str(self.failureCriteria))
      objMsg.printMsg("AVScan Log Boundaries : %s" %str(self.avscanLogBoundaries))

      oCCTScan = CCCTTest(self.dut, params={}) # Setup CCT screen for AVSCAN.
      oCCTScan.run(AVSCAN = 1,failureCriteria = self.failureCriteria) # AVSCAN = 1 is meant to avoid confusing log messages.

      self.parseData()   #get CCT data from full pack read, bucketize it, and format it for smart
      if testSwitch.BF_0136370_231166_ADD_UNLOCK_PRIOR_TO_AVSCAN_UPDATES :
         ICmd.UnlockFactoryCmds()

      if self.dut.IsSDI:
         objMsg.printMsg("To Do!!! SDI skipping writeSmartData")
         objMsg.printMsg("SmartLog Read data...: %s" % self.SmartData)
         objMsg.printMsg("Actual Data : %s" % self.SmartData.upper())
      else:
         self.writeSmartData()  #write and verify to the smart log

   def parseData( self ):
      """_parseData: create a list that populates the different bytes """
      ErrCntTotal = self.CCTErrCnt()
      self.CCTErrAttr(ErrCntTotal)
      self._formatSmartData()
      
   def writeSmartData( self, smartLog=0x80,enableSmart=1 ):
      """_writeSmartData: write smart log with parsed data from Test 510"""

      if not len(self.SmartData):
         ScrCmds.raiseException(11044, 'No Smart Data found')

      if testSwitch.NoIO:
         numSectors = self.LogSize / 512
         ICmd.FillBufferDETS(WBF, 0, '\x00'* self.LogSize)
         ICmd.FillBufferDETS(WBF, 0, self.SmartData[:self.LogSize])
         ICmd.SmartWriteLogSec( smartLog, numSectors)

         ICmd.SmartReadLogSec( smartLog, numSectors)
         smartData = ICmd.GetBufferDETS(RBF, 0)['DATA'][:self.LogSize]
         locSmartData = smartData
      else:
         from IntfClass import CInterface
         oIntf = CInterface()

         oIntf.writeUniformPatternToBuffer('write')  #write 0's to buffer

         self._fillBuffer( self.SmartData ) #Fill the Buffer using FillBuffByte

         oIntf.displayBuffer('write')
         oIntf.WriteOrReadSmartLog(smartLog, 'write') #write smart data in buffer to smartLog

         if testSwitch.FE_0120910_347508_ADD_FILL_AND_WRITE_SMART_IN_WRITESMARTDATA:
            self._fillBuffer( self.SmartData ) #Fill the Buffer using FillBuffByte
            oIntf.displayBuffer('write')
            oIntf.WriteOrReadSmartLog(smartLog, 'write') #write smart data in buffer to smartLog

         objPwrCtrl.powerCycle(5000,12000,10,30)
         oIntf.writeUniformPatternToBuffer('read',dataPattern = (0x2020,0x2020))  #clear read buffer

         oIntf.WriteOrReadSmartLog(smartLog, 'read')  #read the smart log and put in buffer
         oIntf.displayBuffer('read')
         smartData = oIntf.writeBufferToFile()        #write the buffer to file to use for data check

         import binascii
         locSmartData = binascii.hexlify(smartData)[:self.LogSize]

      if DEBUG:
         objMsg.printMsg("SmartLog Read data: %s" % smartData)
         objMsg.printMsg("Actual Data : %s" % self.SmartData[:self.LogSize].upper())

      if locSmartData != self.SmartData[:self.LogSize] and not testSwitch.virtualRun:
         objMsg.printMsg("Smart Log 0x80 Read doesn't match what was supposed to be written", objMsg.CMessLvl.IMPORTANT)
         objMsg.printBin(locSmartData)
         objMsg.printBin(self.SmartData[:self.LogSize])
         ScrCmds.raiseException(11044, 'SmartLog 0x80 Write Failed')


   def _fillBuffer( self, data='' ):
      """_fillBuffer: fill buffer with converted ascii to binary"""
      if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:  
         blockSize ,cnt,offset,byte = 64,0,0,0
      elif objRimType.IOInitRiser() or (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()):  
         blockSize ,cnt,offset,byte = 8,0,0,0
      blkCnt =( len( data )/2)/blockSize #blocksize byte per block
      for cnt in range( 0,blkCnt ):
         if DEBUG:
            objMsg.printMsg( "Block Count in Fill Buff Byte: %d"%( cnt+1 ) )

         ICmd.FillBuffByte(WBF,data[byte:byte+( blockSize*2)] ,offset, blockSize) # Fill write buffer with 512 bytes of pattern starting at offset
         byte+=(blockSize*2)
         offset+=blockSize

      objMsg.printMsg("BinBuffer filled", objMsg.CMessLvl.IMPORTANT)

      getBufferData = ICmd.GetBuffer(1, 0, 512)
      objMsg.printMsg("GetWriteBuffer data: %s" % getBufferData, objMsg.CMessLvl.IMPORTANT)
      return 0
   #--------------------
   def _wordByteSwap( self, data='', x=2 ):
      """_byteSwap: swaps any string"""
      if len( data )%4:
         return data
      byteSwap,tmp,cnt='',[],0
      lst = re.findall( '[0-9-A-F-a-f]{%d}'%x,data)
      cnt = 0
      while cnt < len(lst):
         tmp.append( lst[cnt+1] )
         tmp.append( lst[cnt] )
         cnt += 2
      byteSwap = ''.join( tuple( tmp ) )
      return byteSwap
   #--------------------
   def _formatSmartData( self ):
      """_formatSmartData: create the smart data from the parsed test 510 data"""
      bytecnt,self.SmartData = 0,''

      if DEBUG:
         objMsg.printMsg( "self.byteOffLst: %s"%`self.byteOffLst` )
      self.byteOffLst.sort()

      for item in self.byteOffLst:
         offset, maxBytes, value = item
         while bytecnt != offset:
            bytecnt += 1
            self.SmartData += '00' # a byte is  two nibbles
            if bytecnt >= self.LogSize:
               break
         if bytecnt == offset:# and bytecnt < self.LogSize:
            cmd = '%0' + '%dx'%( maxBytes*2 )
            value = self._wordByteSwap(cmd%value)
            self.SmartData += value
            objMsg.printMsg( "ByteSwapped SmartLog Byte Offset: %04X  = %s"%( offset, value ) )
            bytecnt+=maxBytes
         if bytecnt >= self.LogSize:
            break

      if len( self.SmartData ) < (self.LogSize*2):
         self.SmartData+='0'*((self.LogSize*2)-len(self.SmartData) )
      if DEBUG:
         self._printSmartData( self.SmartData )
      return 0

   #--------------------
   def _printSmartData( self, data='', rows=16, cols=2 ):
      """_printSmartData: print smart data in readable form"""
      cnt,tmp=0,''
      while cnt < (self.LogSize*2):
         y = 0
         tmp+= '%04X : '%(cnt/2)
         while y < rows:
            tmp += ' '+data[cnt:cnt+cols]
            y+=1
            cnt+=cols
         tmp+='\n'
      lst = tmp.split( '\n' )
      objMsg.printMsg( "SmartLog 0x80 Output:" )
      for item in lst: objMsg.printMsg( "%s"%item )
      return

   #--------------------
   def CCTErrCnt(self):
      """Gets Test 510 CCT data for number of violations and bucketize appropriately"""
      CCT_DIST_TABLE = self.dut.dblData.Tables('P_CCT_DISTRIBUTION').tableDataObj()

      ErrCnt2 = 0
      ErrCnt1 = 0
      CriteriaCnt = 0

      #You want to find 100> CCT >= 270.  A bin threshold of 1 means bins are set up as 0 < CCT < 0.99999
      for record in CCT_DIST_TABLE:
         if int(record['SPC_ID']) == 4:              # read pass
            if int(record['BIN_THRESHOLD']) > self.avscanLogBoundaries[1]:
               ErrCnt2 += int(record['BIN_ENTRIES'])
            elif int(record['BIN_THRESHOLD']) > self.avscanLogBoundaries[0]:
               ErrCnt1 += int(record['BIN_ENTRIES'])

            if int(record['BIN_THRESHOLD']) in self.avscanLogBoundaries:
               if DEBUG:
                  objMsg.printMsg( "Found BIN : %s"% record['BIN_THRESHOLD'])
               CriteriaCnt += 1

      #A check to ensure TP are set up properly
      if CriteriaCnt < len(self.avscanLogBoundaries) and not testSwitch.virtualRun:
         ScrCmds.raiseException(11044, 'CCT bin not aligned with AVSCAN spec')


      self.byteOffLst.append( (0x02,2,1) )       #update offset,bytes,value list for log existence
      self.byteOffLst.append((0x4,2,ErrCnt1))
      self.byteOffLst.append((0x6,2,ErrCnt2))


      return ErrCnt1 + ErrCnt2



   def CCTErrAttr( self, ErrCntTotal ):
      """Log the worst 48 CCT from test 510 read.  Record violation number and LBA
         Error:  0 => CCT < 100ms, 1 => 100ms < CCT <= 270, 2 => CCT > 270"""

      byteOffs = 0x80 #starting point for writing error attributes

      CCT_MAX_CMD_TIMES_TABLE = self.dut.dblData.Tables('P_CCT_MAX_CMD_TIMES').tableDataObj()

      mxRank = 0

      for record in CCT_MAX_CMD_TIMES_TABLE:

         if int(record['SPC_ID']) == 4 and mxRank < 48:          #read pass
            if int(record['CMD_TIME']) > self.avscanLogBoundaries[1]:
               errAttr = 2
            elif int(record['CMD_TIME']) > self.avscanLogBoundaries[0]:
               errAttr = 1
            else:
               errAttr = 0

            if errAttr:
               self.byteOffLst.append( (byteOffs,2,errAttr) )
               self.byteOffLst.append( (byteOffs+2,6,int( record['LBA'],16 ) )  )
               byteOffs += 8

            mxRank = max(mxRank, int(record['CMD_RANK']))

      #A check to ensure TP are set up properly
      if mxRank +1 < ErrCntTotal and not testSwitch.virtualRun:
         objMsg.printMsg( "EXCEPTION: CCT error count [%s] is higher than the number of LBAs reported [%s]"% (ErrCntTotal,mxRank+1))
         ScrCmds.raiseException(11044, 'CCT error count greater than LBAs reported')


###########################################################################################################
class CSonyScreenTest(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      # 21/July/2016 SONY_SCREEN updated to the latest one from SONY Consumer Electronic (SCE)
      TestName = 'Sony Screen Test'
      
      objMsg.printMsg('******************** Start %s ******************'%TestName)
      objPwrCtrl.powerCycle(5000,12000,30,10)
      ICmd.SetIntfTimeout(60000)
      IntfTmo = ICmd.GetIntfTimeout()
      objMsg.printMsg('GetIntfTimeout() = %d  ms' % int(IntfTmo['TMO']) )

      ret = CIdentifyDevice().ID # read device settings with identify device
      IDmaxLBA = ret['IDDefaultLBAs'] # default for 28-bit LBA
      if ret['IDCommandSet5'] & 0x400:      # check bit 10
         IDmaxLBA = ret['IDDefault48bitLBAs']
      maxLBA = IDmaxLBA - 1
      if testSwitch.virtualRun:
         maxLBA = 1000000000

      result = OK

      ReadDMAExt    = 0x25              # read dma extended
      WriteDMAExt   = 0x35              # write dma extended
      ReadVerifyExt = 0x42              # Read Verify Ext

      minLBA = 0
      minLBAID = maxLBA - 15650224      
      maxLBAOD = minLBA + 9861632       

      rndScnt    = 64                   # block length (random)
      cmdCount   = 5000                 # random command count
      seqScnt    = 256                  # block length (sequential)

      if self.dut.IsSDI:
         seqScnt    = 7680              # SDI workaround

      seqStep    = seqScnt              # LBA step (sequential)
      fmtScnt    = 128                  # block length (format)
      interleave = 376121               # interleave
      fmtStep    = fmtScnt + interleave # LBA step (format)
      compare    = 1                    # compare flag

      thr0 = 350                        # minimum threshold (350ms)
      thr1 = 2000                       # middle threshold (2s)
      thr2 = 30000                      # maximum threshold (30s)
      thr0CumCount = 0
      thr0Count = 0
      thr1Count = 0
      thr2Count = 0

      criteria1 = 100                   # below 100 times of CCT > 350ms for any commands
      criteria2 = 0                     # CCT < 2s after one time retry 

      if result == OK:
         objMsg.printMsg('STEP 1.******************** Random Write/Read/Compare at MD 5000 times *****')
         from serialScreen import sptDiagCmds
         oSerial = sptDiagCmds()
         spcid = 1
         if DEBUG:
            objMsg.printMsg("MC before Random write")
            oSerial.enableDiags()
            oSerial.GetCtrl_A()
            objPwrCtrl.powerCycle(5000,12000,10,10)

         objMsg.printMsg('Start RAND WriteReadExtended: spcid=%d minLBA=%d maxLBA=%d rndScnt=%d LoopCnt=%d Compare=%d' %(spcid,maxLBAOD,minLBAID,rndScnt,cmdCount,compare,))
         data = ICmd.RandomCCT(WriteDMAExt, maxLBAOD, minLBAID, rndScnt, cmdCount, thr0, thr1, thr2, compare, ReadDMAExt, spcid = spcid)
         if testSwitch.virtualRun:
            data['THR0'] = '0'
            data['THR1'] = '0'
            data['THR2'] = '0' 

         if DEBUG:
            objMsg.printMsg("MC after Random write")
            oSerial.enableDiags()
            oSerial.GetCtrl_A()
            objPwrCtrl.powerCycle(5000,12000,10,10)

         objMsg.printMsg('RandomCCT returned data: %s' % data)
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('%s Random Write/Read Extended Failed, data = %s' % (TestName,data))
         else:
            thr0Count = int(data['THR0']); thr1Count = int(data['THR1']); thr2Count = int(data['THR2'])
            thr0CumCount += thr0Count
            objMsg.printMsg('Total num of CCT > %s = %s, Num of CCT > %s = %s' % (thr0, thr0CumCount, thr1, thr1Count))

            if thr0CumCount > criteria1: # Total num of CCT greater than 350ms has to be < 100 times
               result = -1
            elif thr1Count > criteria2: # When CCT is over 2s, retry the same cmd. Nevertheless CCT is over 2s again, fail the drive
               max_cmd_lst = []
               MAX_CMD = self.dut.dblData.Tables('P_CCT_MAX_CMD_TIMES').tableDataObj()
               for item in MAX_CMD:
                  if item['TEST_SEQ_EVENT'] == self.dut.objSeq.getTestSeqEvent(510):
                     if int(item['CMD_TIME']) > thr1:
                        max_cmd_lst.append(int(item['LBA']))

               objMsg.printMsg('Retry LBA list = %s' % (max_cmd_lst,))

               i = 1
               for lba in max_cmd_lst:
                  data = ICmd.RandomCCT( WriteDMAExt, lba, lba+1, rndScnt, 1, thr0, thr1, thr2, compare, ReadDMAExt, spcid = spcid)
                  result = data['LLRET']
                  if result != OK:
                     objMsg.printMsg('Random Write/Read Extended Failed, data = %s' % data)
                     break
                  else:
                     thr0Count = int(data['THR0']); thr1Count = int(data['THR1']); thr2Count = int(data['THR2'])
                     thr0CumCount += thr0Count
                     objMsg.printMsg('Retry #%s at LBA %s' % (i, lba))
                     i = i + 1
                     objMsg.printMsg('Total num of CCT > %s = %s, Num of CCT > %s = %s' % (thr0, thr0CumCount, thr1, thr1Count))
                     if thr0CumCount > criteria1 or thr1Count > criteria2:
                        objMsg.printMsg('Random wr/rd/compare fail the retry. Total num of CCT > 350ms = %s, Num of CCT > 2s = %s' % (thr0CumCount, thr1Count))
                        result = -1
                        break

               del max_cmd_lst
            else:
               objMsg.printMsg('Pass random wr/rd/compare at MD.')

      if result == OK:
         objMsg.printMsg('STEP 2.******************** Sequential Read Verify at ID *****')
         spcid = 2
         ICmd.ClearBinBuff(RBF)
         objMsg.printMsg('Start SeqRead Verify: minLBA=%d maxLBA=%d seqScnt=%d seqStep=%d Compare=0' %(minLBAID,maxLBA,seqScnt,seqStep,))
         data = ICmd.SequentialCCT( ReadVerifyExt,  minLBAID, maxLBA, seqScnt, seqStep, thr0, thr1, thr2, spcid = spcid)

         objMsg.printMsg('SequentialRead CCT returned data: %s' % data)
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('%s SeqRead ID Failed, data = %s' % (TestName,data))
         else:
            thr0Count = int(data['THR0']); thr1Count = int(data['THR1']); thr2Count = int(data['THR2'])
            thr0CumCount += thr0Count
            objMsg.printMsg('Total num of CCT > %s = %s, Num of CCT > %s = %s' % (thr0, thr0CumCount, thr1, thr1Count))

            if thr0CumCount > criteria1: # Total num of CCT greater than 350ms has to be < 100 times
               result = -1
            elif thr1Count > criteria2: # When CCT is over 2s, retry the same cmd. Nevertheless CCT is over 2s again, fail the drive
               max_cmd_lst = []
               MAX_CMD = self.dut.dblData.Tables('P_CCT_MAX_CMD_TIMES').tableDataObj()
               for item in MAX_CMD:
                  if item['TEST_SEQ_EVENT'] == self.dut.objSeq.getTestSeqEvent(510):
                     if int(item['CMD_TIME']) > thr1:
                        max_cmd_lst.append(int(item['LBA']))

               objMsg.printMsg('Retry LBA list = %s' % (max_cmd_lst,))

               i = 1
               for lba in max_cmd_lst:
                  data = ICmd.SequentialCCT( ReadVerifyExt,  lba, lba+1, seqScnt, seqStep, thr0, thr1, thr2, spcid = spcid)
                  result = data['LLRET']
                  if result != OK:
                     objMsg.printMsg('SeqRead ID Failed, data = %s' % data)
                     break
                  else:
                     thr0Count = int(data['THR0']); thr1Count = int(data['THR1']); thr2Count = int(data['THR2'])
                     thr0CumCount += thr0Count
                     objMsg.printMsg('Retry #%s at LBA %s' % (i, lba))
                     i = i + 1
                     objMsg.printMsg('Total num of CCT > %s = %s, Num of CCT > %s = %s' % (thr0, thr0CumCount, thr1, thr1Count))
                     if thr0CumCount > criteria1 or thr1Count > criteria2:
                        objMsg.printMsg('SeqRead fail the retry. Total num of CCT > 350ms = %s, Num of CCT > 2s = %s' % (thr0CumCount, thr1Count))
                        result = -1
                        break

               del max_cmd_lst
            else:
               objMsg.printMsg('Pass SeqRead at ID.')

      if result == OK:
         objMsg.printMsg('STEP 3.******************** Sequential Read Verify at OD *****')
         spcid = 3
         ICmd.ClearBinBuff(RBF)
         objMsg.printMsg('Start SeqRead Verify: minLBA=%d maxLBA=%d seqScnt=%d seqStep=%d Compare=0' %(minLBA,maxLBAOD,seqScnt,seqStep,))
         data = ICmd.SequentialCCT( ReadVerifyExt,  minLBA, maxLBAOD, seqScnt, seqStep, thr0, thr1, thr2, spcid = spcid)
         objMsg.printMsg('SequentialCCT returned data: %s' % data)
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('%s SeqRead OD Failed, data = %s' % (TestName,data))
         else:
            thr0Count = int(data['THR0']); thr1Count = int(data['THR1']); thr2Count = int(data['THR2'])
            thr0CumCount += thr0Count
            objMsg.printMsg('Total num of CCT > %s = %s, Num of CCT > %s = %s' % (thr0, thr0CumCount, thr1, thr1Count))

            if thr0CumCount > criteria1: # Total num of CCT greater than 350ms has to be < 100 times
               result = -1
            elif thr1Count > criteria2: # When CCT is over 2s, retry the same cmd. Nevertheless CCT is over 2s again, fail the drive
               max_cmd_lst = []
               MAX_CMD = self.dut.dblData.Tables('P_CCT_MAX_CMD_TIMES').tableDataObj()
               for item in MAX_CMD:
                  if item['TEST_SEQ_EVENT'] == self.dut.objSeq.getTestSeqEvent(510):
                     if int(item['CMD_TIME']) > thr1:
                        max_cmd_lst.append(int(item['LBA']))

               objMsg.printMsg('Retry LBA list = %s' % (max_cmd_lst,))

               i = 1
               for lba in max_cmd_lst:
                  data = ICmd.SequentialCCT( ReadVerifyExt,  lba, lba+1, seqScnt, seqStep, thr0, thr1, thr2, spcid = spcid)
                  result = data['LLRET']
                  if result != OK:
                     objMsg.printMsg('SeqRead OD Failed, data = %s' % data)
                     break
                  else:
                     thr0Count = int(data['THR0']); thr1Count = int(data['THR1']); thr2Count = int(data['THR2'])
                     thr0CumCount += thr0Count
                     objMsg.printMsg('Retry #%s at LBA %s' % (i, lba))
                     i = i + 1
                     objMsg.printMsg('Total num of CCT > %s = %s, Num of CCT > %s = %s' % (thr0, thr0CumCount, thr1, thr1Count))
                     if thr0CumCount > criteria1 or thr1Count > criteria2:
                        objMsg.printMsg('SeqRead fail the retry. Total num of CCT > 350ms = %s, Num of CCT > 2s = %s' % (thr0CumCount, thr1Count))
                        result = -1
                        break

               del max_cmd_lst
            else:
               objMsg.printMsg('Pass SeqRead at OD.')

      if result == OK:
         objMsg.printMsg('STEP 4.******************** SONY Format *****')
         spcid = 4
         ICmd.ClearBinBuff(RBF); ICmd.ClearBinBuff(WBF)
         objMsg.printMsg('Start SeqWrite Extended: minLBA=%d maxLBA=%d fmtScnt=%d fmtStep=%d Compare=0' %(minLBA,maxLBA,fmtScnt,fmtStep,))
         data = ICmd.SequentialCCT( WriteDMAExt, minLBA, maxLBA, fmtScnt, fmtStep, thr0, thr1, thr2, spcid = spcid )

         objMsg.printMsg('SequentialCCT returned data: %s' % data)
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('%s SeqRead OD Failed, data = %s' % (TestName,data))
         else:
            thr0Count = int(data['THR0']); thr1Count = int(data['THR1']); thr2Count = int(data['THR2'])
            thr0CumCount += thr0Count
            objMsg.printMsg('Total num of CCT > %s = %s, Num of CCT > %s = %s' % (thr0, thr0CumCount, thr1, thr1Count))

            if thr0CumCount > criteria1: # Total num of CCT greater than 350ms has to be < 100 times
               result = -1
            elif thr1Count > criteria2: # When CCT is over 2s, retry the same cmd. Nevertheless CCT is over 2s again, fail the drive
               max_cmd_lst = []
               MAX_CMD = self.dut.dblData.Tables('P_CCT_MAX_CMD_TIMES').tableDataObj()
               for item in MAX_CMD:
                  if item['TEST_SEQ_EVENT'] == self.dut.objSeq.getTestSeqEvent(510):
                     if int(item['CMD_TIME']) > thr1:
                        max_cmd_lst.append(int(item['LBA']))

               objMsg.printMsg('Retry LBA list = %s' % (max_cmd_lst,))

               i = 1
               for lba in max_cmd_lst:
                  data = ICmd.SequentialCCT( WriteDMAExt, lba, lba+1, fmtScnt, fmtStep, thr0, thr1, thr2, spcid = spcid )
                  result = data['LLRET']
                  if result != OK:
                     objMsg.printMsg('SeqRead OD Failed, data = %s' % data)
                     break
                  else:
                     thr0Count = int(data['THR0']); thr1Count = int(data['THR1']); thr2Count = int(data['THR2'])
                     thr0CumCount += thr0Count
                     objMsg.printMsg('Retry #%s at LBA %s' % (i, lba))
                     i = i + 1
                     objMsg.printMsg('Total num of CCT > %s = %s, Num of CCT > %s = %s' % (thr0, thr0CumCount, thr1, thr1Count))
                     if thr0CumCount > criteria1 or thr1Count > criteria2:
                        objMsg.printMsg('SeqRead fail the retry. Total num of CCT > 350ms = %s, Num of CCT > 2s = %s' % (thr0CumCount, thr1Count))
                        result = -1
                        break

               del max_cmd_lst
            else:
               objMsg.printMsg('Pass SONY Format.')

      if result == OK:
         objMsg.printMsg('STEP 5.******************** Standby/HW Reset ******************')
         result = ICmd.StandbyImmed()['LLRET']
         if result == OK:
            objPwrCtrl.powerCycle(5000,12000,10,10)
         if result == OK:
            result = ICmd.StandbyImmed()['LLRET']
         if result == OK:
            objPwrCtrl.powerCycle(5000,12000,10,10)
         if result == OK:
            result = ICmd.StandbyImmed()['LLRET']

      objMsg.printMsg('Set Interface Timeout to Default')
      ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"]*1000)
      IntfTmo = ICmd.GetIntfTimeout()
      objMsg.printMsg('GetIntfTimeout() = %d  ms' % int(IntfTmo['TMO']) )

      objMsg.printMsg('CCT Counts > 350msec: %d' % thr0CumCount)

      if result != OK:
         objMsg.printMsg('%s Failed' % (TestName))
         if thr0CumCount>100:
            objMsg.printMsg('More than 100 CCT counts > 350msec, Always Slow Performance')
         if thr1Count>0:
            objMsg.printMsg('More than 0 CCT counts > 2sec, Always Slow Performance')
         if thr2Count>0:
            objMsg.printMsg('More than 0 CCT counts > 30sec, Not Data Request')
         ScrCmds.raiseException(13373,"Sony screen test FAIL")
      else:
         objMsg.printMsg('******************** %s PASSED ******************'%TestName)
                  
      if testSwitch.IOWriteReadRemoval:
         RWDict = []
         RWDict.append ('Read')
         RWDict.append (minLBA)
         RWDict.append (maxLBA)
         RWDict.append ('Sony Screen')
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)

      objMsg.printMsg("Clear MC after SONY_Screen")
      oSerial.enableDiags()
      oSerial.initMCCache()
      objPwrCtrl.powerCycle(5000,12000,10,10) # Pwr cyc to revert drive back to default state

###########################################################################################################
class CHPQCusTest(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------     
   def returnStartLbaWords(self, startLBA):
      upperWord1 = (startLBA & 0xFFFF000000000000) >> 48
      upperWord2 = (startLBA & 0x0000FFFF00000000) >> 32
      lowerWord1 = (startLBA & 0x00000000FFFF0000) >> 16
      lowerWord2 = (startLBA & 0x000000000000FFFF)

      return (upperWord1,upperWord2,lowerWord1,lowerWord2,)      
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      TestName = 'HP Screen Test'
      objMsg.printMsg('******************** Start %s ******************'%TestName)
      objPwrCtrl.powerCycle(5000,12000,10,10)
      ICmd.SetIntfTimeout(60000)
      IntfTmo = ICmd.GetIntfTimeout()
      objMsg.printMsg('GetIntfTimeout() = %d  ms' % int(IntfTmo['TMO']) )

      self.ID = CIdentifyDevice().ID
      self.extmode = 0
      self.maxLBA = self.ID['IDDefaultLBAs'] # default for 28-bit LBA
      if self.ID['IDCommandSet5'] & 0x400:      # check bit 10
         self.maxLBA = self.ID['IDDefault48bitLBAs']
         self.extmode = 1
      self.maxLBA = self.maxLBA - 1

      for i in range(2):
         self.HiLowSeek(0, self.maxLBA, 50)
         self.FunnelSeek()
         self.TrkToTrkSeek(0, self.maxLBA, 0x1, 0x13141)
         self.SeqRandomSeekLba('Random')

      self.SeqWrtOrRd('20G Seq DMA Write', 0, 0, 0x2540BE4, 0x7F, 0)
      self.SeqWrtOrRd('20G Seq DMA Read', 1, 0, 0x2540BE4, 0x7F, 0)
      self.SeqWrtOrRd('5G Seq DMA Write', 0, self.maxLBA-0x9502F9, self.maxLBA, 0x7F, 0)
      self.SeqWrtOrRd('5G Seq DMA Read', 1, self.maxLBA-0x9502F9, self.maxLBA, 0x7F, 0)

      objMsg.printMsg('******************** %s PASSED ******************'%TestName)
      objPwrCtrl.powerCycle(5000,12000,10,10)
      ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"]*1000)
      IntfTmo = ICmd.GetIntfTimeout()
      objMsg.printMsg('GetIntfTimeout() = %d  ms' % int(IntfTmo['TMO']) )

   #-----------------------------------------------------------------------------------------#
   def SeqWrtOrRd(self, test_name, test_type, start_lba, end_lba, sect_cnt, test_seq):
      result = OK
      objMsg.printMsg('------------------------------%s------------------------------' % (test_name))
      step_lba = sect_cnt; stamp_flag = 0; comp_flag = 0; loop_cnt = 0
      if test_type == 0:
         if test_seq == 0:
            failCode = 12657
         else:
            failCode = 12664
      elif test_type == 1:
         if test_seq == 0:
            failCode = 12656
         else:
            failCode = 12653
      elif test_type == 2:
         failCode = 12674

      ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
      result = ICmd.SetFeatures(0x03, 0x45)['LLRET']
      if result != OK:
         objMsg.printMsg('%s Failed SetFeatures - Transfer Rate = UDMA-100' % test_name)
      else:
         objMsg.printMsg('%s Passed SetFeatures - Transfer Rate = UDMA-100' % test_name)

         if sect_cnt != -1 :
            if test_type == 0:
               objMsg.printMsg('%s Min LBA=%d Max LBA=%d Count=%d Stamp=%d' % (test_name, start_lba, end_lba, sect_cnt, stamp_flag))
               if self.extmode:
                  data = ICmd.SequentialWriteDMAExt(start_lba, end_lba, step_lba, sect_cnt, stamp_flag)
               else:
                  data = ICmd.SequentialWriteDMA(start_lba, end_lba, step_lba, sect_cnt, stamp_flag)
            elif test_type == 1:
               objMsg.printMsg('%s Min LBA=%d Max LBA=%d Count=%d Stamp=%d Comp=%d' % (test_name, start_lba, end_lba, sect_cnt, stamp_flag, comp_flag))
               if self.extmode:
                  data = ICmd.SequentialReadDMAExt(start_lba, end_lba, step_lba, sect_cnt, stamp_flag, comp_flag)
               else:
                  data = ICmd.SequentialReadDMA(start_lba, end_lba, step_lba, sect_cnt, stamp_flag, comp_flag)
            elif test_type == 2:
               objMsg.printMsg('%s Min LBA=%d Max LBA=%d Count=%d' % (test_name, start_lba, end_lba, sect_cnt))
               data = ICmd.SequentialReadVerify(start_lba,end_lba,sect_cnt,sect_cnt)
            result = data['LLRET']
            if result != OK:
               objMsg.printMsg('%s Failed data = %s' % (test_name,data))
            else:
               objMsg.printMsg('%s LBAs %d to %d Passed' % (test_name,start_lba,end_lba))
         else:
            import random
            if test_type == 0:
               objMsg.printMsg('%s Min LBA=%d Max LBA=%d Count=Random Stamp=%d' % (test_name, start_lba, end_lba, stamp_flag))
            else:
               objMsg.printMsg('%s Min LBA=%d Max LBA=%d Count=Random Stamp=%d Comp=%d' % (test_name, start_lba, end_lba, stamp_flag, comp_flag))
            random.seed(1)
            cur_lba = start_lba
            while cur_lba < end_lba:
               if loop_cnt == 1:
                  rand_sect = random.randrange(1, 64)
               elif loop_cnt <= 20:
                  rand_sect = 64
               elif loop_cnt > 20:
                  loop_cnt = 0
               if cur_lba + rand_sect > end_lba:
                  rand_sect = end_lba - cur_lba
               if test_type == 0:
                  #objMsg.printMsg('Write DMA LBA %d Sect %d' % (cur_lba,rand_sect))
                  data = ICmd.WriteDMALBA(cur_lba,rand_sect)
               elif test_type == 1:
                  #objMsg.printMsg('Read DMA LBA %d Sect %d' % (cur_lba,rand_sect))
                  data = ICmd.ReadDMALBA(cur_lba,rand_sect)
               elif test_type == 2:
                  #objMsg.printMsg('Read Verify LBA %d Sect %d' % (cur_lba,rand_sect))
                  data = ICmd.ReadVerifySects(cur_lba,rand_sect)
               result = data['LLRET']
               if result != OK:
                  objMsg.printMsg('%s Failed data = %s' % (test_name, data))
                  break
               else:
                  if test_seq == 0:
                     cur_lba = cur_lba + rand_sect
                  else:
                     cur_lba = cur_lba + random.randrange(1,10000)
               loop_cnt += 1

            if result == OK:
               objMsg.printMsg('%s LBAs %d to %d Passed' % (test_name,start_lba,end_lba))

      if result != OK:
         ScrCmds.raiseException(failCode,"%s FAIL"%test_name)

   #-------------------------------------------------------------------------------------------------------------#
   def HiLowSeek(self, nLowLBA, nHighLBA, nLoop):                   # Customer Type
      
      objMsg.printMsg('Hi-Low Seek from MinLBA=%d to MaxLBA=%d SeekCount=%d' % (nLowLBA, nHighLBA, nLoop))
      SeekLBA = {
         'test_num'           : 538,
         'prm_name'           : "SeekLBA",
         'timeout'            : 600,
         'FEATURES'           : 0,
         'SECTOR_COUNT'       : 1,
         'COMMAND'            : 0x42, #Read Verify Ext - Non Data
         'DEVICE'             : 0x40,
         'PARAMETER_0'        : 0x2000, #enables LBA mode cmd reg defs
          'stSuppressResults' : ST_SUPPRESS__ALL | ST_SUPPRESS_SUPR_CMT,         
      }
      oProc = CProcess()
      DisableScriptComment(0x0FF0)     # Suppress output
      result = OK
      for i in range(nLoop):
         if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:
            data = ICmd.Seek(nLowLBA)
            result = data["LLRET"]
         else:
            try:
               if objRimType.CPCRiser() and testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #CPC non-intrinsic require 'LBA_LOW', 'LBA_MID' and 'LBA_HIGH'
                  LBA_HIGH, LBA_MID, LBA_LOW = CUtility.convertLBANumber2LBARegister(nLowLBA)
                  SeekLBA['LBA_HIGH'] = LBA_HIGH
                  SeekLBA['LBA_MID'] = LBA_MID
                  SeekLBA['LBA_LOW'] = LBA_LOW
               else:
                  SeekLBA['LBA'] = self.returnStartLbaWords( nLowLBA )
               #st (538, SeekLBA)
               oProc.St(SeekLBA) 
            except:
               result = NOT_OK
         if result != OK:
            objMsg.printMsg("Hi-Low Seek %d failed! %s" %(nLowLBA, traceback.format_exc()))
            break
         
         if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:
            data = ICmd.Seek(nHighLBA)
            result = data["LLRET"]
         else:
            try:
               if objRimType.CPCRiser() and testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #CPC non-intrinsic require 'LBA_LOW', 'LBA_MID' and 'LBA_HIGH'
                  LBA_HIGH, LBA_MID, LBA_LOW = CUtility.convertLBANumber2LBARegister(nHighLBA)
                  SeekLBA['LBA_HIGH'] = LBA_HIGH
                  SeekLBA['LBA_MID'] = LBA_MID
                  SeekLBA['LBA_LOW'] = LBA_LOW
               else:
                  SeekLBA['LBA'] = self.returnStartLbaWords( nHighLBA )
               #st (538, SeekLBA) 
               oProc.St(SeekLBA) 
            except:
               result = NOT_OK            
         if result != OK:
            objMsg.printMsg("Hi-Low Seek %d failed! %s" %(nHighLBA, traceback.format_exc()))
            break
         
      DisableScriptComment(0)   
      if result != OK:
         ScrCmds.raiseException(13370,"Hi-Low Seek FAIL")

   #-------------------------------------------------------------------------------------------------------------#
   def FunnelSeek(self):                   # Customer Type

      minLBA = 0
      maxLBA = self.maxLBA
      interval = 0x26282
      result = OK

      objMsg.printMsg('Executing FunnelSeek. Loop count = %s, Seek count = %s.' %(maxLBA/interval,(maxLBA/interval)*2))      
      objMsg.printMsg('Funnel Seek block size = 1 , interval = %s' %interval)
      
      if objRimType.CPCRiser():
         loop = 0
         tSum = 0
         DisableScriptComment(0x0FF0)     # Suppress output
         while 1:
            tStart = time.time()
            loop += 1
            data = ICmd.Seek(minLBA)
            result = data["LLRET"]
            if result != OK:
               objMsg.printMsg("Funnel Seek %d failed! %s" %(minLBA, traceback.format_exc()))
               break
               
            data = ICmd.Seek(maxLBA)
            result = data["LLRET"]
            if result != OK:
               objMsg.printMsg("Funnel Seek %d failed! %s" %(maxLBA, traceback.format_exc()))
               break
                  
            if minLBA == self.maxLBA or maxLBA == 0:
               break
            minLBA += interval
            maxLBA -= interval
            if minLBA > self.maxLBA:
               minLBA = self.maxLBA
            if maxLBA < 0:
               maxLBA = 0
   
            tSum += (time.time()-tStart)  
   ##         objMsg.printMsg("Loop %s completed in %3.3f seconds" %(loop, time.time()-tStart))
         objMsg.printMsg("Average time per loop = %2.3f seconds." %(tSum/loop))
         
         DisableScriptComment(0)
         if result != OK:
            ScrCmds.raiseException(13371,"Funnel Seek FAIL")
      else:
         data = ICmd.FunnelSeek(minLBA,maxLBA,interval,1)
         if data['LLRET'] != OK:
            ScrCmds.raiseException(13371,"Funnel Seek FAIL")                                 

   #-------------------------------------------------------------------------------------------------------------#
   def TrkToTrkSeek(self, nMinLBA, nMaxLBA, nSecCnt,nStep):                   # Customer Type
      result = OK
      objMsg.printMsg('Track to Track seek from lba %d to lba %d, step %d, sector count %d'%(nMinLBA, nMaxLBA,nStep,nSecCnt))

      data = ICmd.SequentialSeek(nMinLBA,nMaxLBA,nStep,nSecCnt)
      objMsg.printMsg('Track to Track seek Data=%s' % data)
      result = data["LLRET"]
      if result != OK:
         ScrCmds.raiseException(13374,"Track to Track Seek FAIL")

   #---------------------------------------------------------------------------------------------#
   def SeqRandomSeekLba(self,type):
      start_time = time.time()
      result = OK
      ICmd.ClearBinBuff(RBF)
      objMsg.printMsg('-->%s Seek' % type)
      if type == 'Seq':
         startLBA = 0; endLBA = 32000; stepLBA = 256; sectorCount = 256
         data = ICmd.SequentialSeek(startLBA,endLBA,stepLBA,sectorCount)
         result = data['LLRET']
         if result == OK:
            objMsg.printMsg('Sequential Seek Passed')
         else:
            objMsg.printMsg('Sequential Seek Failed')
            objMsg.printMsg('data = %s' % data)
            failCode = 12695

      if type == 'Random':
         minLba = 0; maxLba = self.maxLBA; minSectCount = 1; maxSectCount = 1; count = 300
         data = ICmd.RandomSeek(minLba,maxLba,minSectCount,maxSectCount,count,stampFlag=0,compareFlag=0)
         result = data['LLRET']
         if result == OK:
            objMsg.printMsg('Random Seek Passed')
         else:
            objMsg.printMsg('Random Seek Failed')
            objMsg.printMsg('data = %s' % data)
            failCode = 12694

      end_time = time.time()
      min, sec = self.Cal_Min_Sec(start_time,end_time)
      objMsg.printMsg('%s Seek TestTime = %d:%d' % (type, min, sec))
      if result != OK:
         ScrCmds.raiseException(failCode,"%s Seek FAIL"%type)

   #-----------------------------------------------------------------------------------------#
   def Cal_Min_Sec(self,start_time,end_time):
      total_time = end_time - start_time
      test_time_min = int(total_time / 60)       # get min
      test_time_sec = total_time % 60            # get sec
      return test_time_min, test_time_sec


###########################################################################################################
class CCCTTest(CState):
   """
      Description: Class that will perform SMART reset and generic customer prep.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self, AVSCAN = 0, failureCriteria = []):
      
      if not hasattr(TP, 'prm_510_FPR_AVSCAN'):
         objMsg.printMsg("Skipping CCCTTest... AVSCAN parameter '%s' not found." %'prm_510_FPR_AVSCAN')
         return
      
      if self.dut.IsSDI:   # SDI workaround
         TP.prm_510_FPW_AVSCAN['BLKS_PER_XFR'] = 7680
         TP.prm_510_FPR_AVSCAN['BLKS_PER_XFR'] = 7680

      if not failureCriteria:
         failureCriteria = getattr(TP, 'CCTFailureCriteria', {'write':[],'read':[]})

      from Process import CProcess
      oProc = CProcess()
      if AVSCAN == 0:
         objMsg.printMsg("*"*40)
         objMsg.printMsg("Customer Screens: CCT Test")
         objMsg.printMsg("*"*40)

      import string,time,sys,traceback

      ICmd.HardReset()

      startIndex = self.getTableStartIndex()
      ICmd.SetIntfTimeout(TP.prm_510_FPR_AVSCAN['timeout'])
      IntfTmo = ICmd.GetIntfTimeout()
      objMsg.printMsg('GetIntfTimeout() = %d  ms' % int(IntfTmo['TMO']) )
      if AVSCAN and testSwitch.EnableAVScanCalmFeature:
         VibeLockWrap("CALM", oProc.St, TP.prm_510_FPW_AVSCAN)
      else:
         try:
            if testSwitch.NoIO:
               ICmd.CCT_510(TP.prm_510_FPW_AVSCAN)    # full pack write with CCT collection
            else:
               oProc.St(TP.prm_510_FPW_AVSCAN)    # full pack write with CCT collection
         except:
            objMsg.printMsg("prm_510_FPW_AVSCAN failure... %s" %traceback.format_exc())
            raise
            
      self.checkFailureLimits(startIndex, failureCriteria['write'])           


      startIndex = self.getTableStartIndex()
      ICmd.SetIntfTimeout(TP.prm_510_FPR_AVSCAN['timeout'])
      IntfTmo = ICmd.GetIntfTimeout()
      objMsg.printMsg('GetIntfTimeout() = %d  ms' % int(IntfTmo['TMO']) )
      if AVSCAN and testSwitch.EnableAVScanCalmFeature:
         VibeLockWrap("CALM", oProc.St, TP.prm_510_FPR_AVSCAN)
      else:
         try:   
            if testSwitch.NoIO:
               ICmd.CCT_510(TP.prm_510_FPR_AVSCAN)    # full pack read with CCT collection
            else:
               oProc.St(TP.prm_510_FPR_AVSCAN)    # full pack read with CCT collection
         except:
            objMsg.printMsg("prm_510_FPR_AVSCAN failure... %s" %traceback.format_exc())
            raise
               
      if testSwitch.EnableAVScanCheck: 
         self.PercentageCCTCheck(startIndex, failureCriteria['read'])       
      else:      
         self.checkFailureLimits(startIndex, failureCriteria['read'])      

      if testSwitch.CCT_RandomReads:
        ICmd.HardReset()
        if AVSCAN and testSwitch.EnableAVScanCalmFeature:
           VibeLockWrap("CALM", oProc.St, TP.prm_510_CCT)
        else:   
           oProc.St(TP.prm_510_CCT)    # random read with CCT collection
##           ICmd.St(TP.prm_510_CCT)    # random read with CCT collection

      ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"]*1000) #30 seconds
      IntfTmo = ICmd.GetIntfTimeout()
      objMsg.printMsg('GetIntfTimeout() = %d  ms' % int(IntfTmo['TMO']) )

      if testSwitch.CCT_SPC_BREAKOUT:
         self.getSPTbreakout()

   def getSPTbreakout(self):
   #############################################################
   # Section to break out CCT table for GOTF grading
   #############################################################

      CCT_TABLE = []
      CCT_SPC_2 = []
      CCT_SPC_3 = []
      CCT_SPC_15 = []

      CCT_TABLE = self.dut.dblData.Tables('P_CCT_MAX_CMD_TIMES').tableDataObj()

      objMsg.printMsg(str(CCT_TABLE))
      for record in range(len(CCT_TABLE)): #maybe typecast values into int
         self.occurance = self.dut.objSeq.registerCurrentTest(0)
         self.curSeq = self.dut.objSeq.getSeq()
         self.testSeqNum = self.dut.objSeq.getTestSeqEvent(0)
         objMsg.printMsg(str(CCT_TABLE[record]))
         if int(CCT_TABLE[record]['SPC_ID']) == 2:
            objMsg.printMsg("SPC_ID = 2")
            # add to CCT_SPC_2
            self.dut.dblData.Tables('CCT_SPC_2').addRecord(
                  {
                  'SPC_ID':'2',
                  'OCCURRENCE': self.occurance,
                  'SEQ': self.curSeq,
                  'TEST_SEQ_EVENT': self.testSeqNum,
                  'TEST_NUMBER':'0',
                  'CMD_TIME': CCT_TABLE[record]['CMD_TIME'],
                  })
         elif int(CCT_TABLE[record]['SPC_ID']) == 3:
            objMsg.printMsg("SPC_ID = 3")
            # add to CCT_SPC_3
            self.dut.dblData.Tables('CCT_SPC_3').addRecord(
                  {
                  'SPC_ID':'3',
                  'OCCURRENCE': self.occurance,
                  'SEQ': self.curSeq,
                  'TEST_SEQ_EVENT': self.testSeqNum,
                  'TEST_NUMBER':'0',
                  'CMD_TIME': CCT_TABLE[record]['CMD_TIME'],
                  })
         elif int(CCT_TABLE[record]['SPC_ID']) == 15:
            objMsg.printMsg("SPC_ID = 15")
            # add to CCT_SPC_15
            self.dut.dblData.Tables('CCT_SPC_15').addRecord(
               {
               'SPC_ID':'15',
               'OCCURRENCE': self.occurance,
               'SEQ': self.curSeq,
               'TEST_SEQ_EVENT': self.testSeqNum,
               'TEST_NUMBER':'0',
               'CMD_TIME': CCT_TABLE[record]['CMD_TIME'],
               })

      try:
         CCT_SPC_2 = self.dut.dblData.Tables('CCT_SPC_2').tableDataObj()
         objMsg.printMsg(str(CCT_SPC_2))
      except:
         objMsg.printMsg("No CCT_SPC_2 data")

      try:
         CCT_SPC_3 = self.dut.dblData.Tables('CCT_SPC_3').tableDataObj()
         objMsg.printMsg(str(CCT_SPC_3))
      except:
         objMsg.printMsg("No CCT_SPC_3 data")

      try:
         CCT_SPC_15 = self.dut.dblData.Tables('CCT_SPC_15').tableDataObj()
         objMsg.printMsg(str(CCT_SPC_15))
      except:
         objMsg.printMsg("No CCT_SPC_15 data")

   def getTableStartIndex(self):
      if testSwitch.virtualRun:
         return 0

      try:
         startIndex = len(self.dut.dblData.Tables('P_CCT_DISTRIBUTION').tableDataObj())
      except:
         startIndex = 0

      return startIndex

   def PercentageCCTCheck(self,startIndex,failureCriteria):   
        if not failureCriteria: return

        CCT_DIST_TABLE = self.dut.dblData.Tables('P_CCT_DISTRIBUTION').tableDataObj()[startIndex:]
        criteriaFound = 0      
        CumulativeBinEntries = {}    
        TotalBinEntries = 0            
        CriteriaBinEntries = 0   

        for record in CCT_DIST_TABLE:
            TotalBinEntries += int(record['BIN_ENTRIES'])
            for criteria in failureCriteria:
                if int(record['BIN_THRESHOLD']) == criteria[0]:
                   if DEBUG:
                      objMsg.printMsg( "Found BIN : %s"% record['BIN_THRESHOLD'])
                   criteriaFound += 1    
                if int(record['BIN_THRESHOLD']) <= criteria[0]:                
                   CriteriaBinEntries += int(record['BIN_ENTRIES'])
                   if int(record['BIN_THRESHOLD']) == criteria[0]:
                      CumulativeBinEntries[int(record['BIN_THRESHOLD'])] = CriteriaBinEntries                 
                   break

        for value in failureCriteria:        
           CheckLimit = int(round(TotalBinEntries*(value[1]/100)))           
           ActualValue = CumulativeBinEntries.get(value[0])
           if ActualValue < CheckLimit:
              objMsg.printMsg('Number of Command Completion Times <=%sms = %s.  Limit is %s (%s%% of (%s) TOTAL CCT)' %(value[0],ActualValue, CheckLimit,value[1],TotalBinEntries))
              if not testSwitch.virtualRun:
                 ScrCmds.raiseException(14035, 'Max CCT limit exceeded')
              else:
                 objMsg.printMsg('Disabling CCT failure in VE')

        if criteriaFound < len(failureCriteria):
            objMsg.printMsg('WARNING: Test 510 CCT bins not found in CCT_DISTRIBUTION table')
   def checkFailureLimits(self,startIndex,failureCriteria):
      if not failureCriteria:
         return

      CCT_DIST_TABLE = self.dut.dblData.Tables('P_CCT_DISTRIBUTION').tableDataObj()[startIndex:]

      errCounts = [0] * len(failureCriteria)
      criteriaFound = 0
      failureCriteria.sort(reverse=True)

      for record in CCT_DIST_TABLE:
         for index, criteria in enumerate(failureCriteria):
            if int(record['BIN_THRESHOLD']) == criteria[0]:
               if DEBUG:
                  objMsg.printMsg( "Found BIN : %s"% record['BIN_THRESHOLD'])
               criteriaFound += 1

            if int(record['BIN_THRESHOLD']) > criteria[0]:
               errCounts[index] += int(record['BIN_ENTRIES'])
               break

      for index, criteria in enumerate(failureCriteria):
         if errCounts[index] > criteria[1]:
            objMsg.printMsg('Number of Command Completion Times above %s = %s.  Limit is %s' %(criteria[0],errCounts[index], criteria[1]))
            if not testSwitch.virtualRun:
               ScrCmds.raiseException(14035, 'Max CCT limit exceeded')
            else:
               objMsg.printMsg('Disabling CCT failure in VE')


      if criteriaFound < len(failureCriteria):
         objMsg.printMsg('WARNING: Test 510 CCT bins not found in CCT_DISTRIBUTION table')


###########################################################################################################
class CLenovoCusTest(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------     
   def returnStartLbaWords(self, startLBA):
      upperWord1 = (startLBA & 0xFFFF000000000000) >> 48
      upperWord2 = (startLBA & 0x0000FFFF00000000) >> 32
      lowerWord1 = (startLBA & 0x00000000FFFF0000) >> 16
      lowerWord2 = (startLBA & 0x000000000000FFFF)

      return (upperWord1,upperWord2,lowerWord1,lowerWord2,)      
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      TestName = 'Lenovo Screen Test'
      objMsg.printMsg('******************** Start %s ******************'%TestName)
      objPwrCtrl.powerCycle(5000,12000,10,10)
      self.ID = CIdentifyDevice().ID
      self.extmode = 0
      self.maxLBA = self.ID['IDDefaultLBAs'] # default for 28-bit LBA
      if self.ID['IDCommandSet5'] & 0x400:      # check bit 10
         self.maxLBA = self.ID['IDDefault48bitLBAs']
         self.extmode = 1
      self.maxLBA = self.maxLBA - 1
      self.HiLowSeek(0, self.maxLBA, 50)
      self.FunnelSeek()
      self.RandomSeek(300)
      self.LinearVerify(0, 100187500, 0x4000)
      self.RandomSeek(300)
      self.VerifySMART()
      self.SmartDSTShort()
      self.SeqReadDmaLba('LEGEND', 0, 10191081, 0x1, 0x1)
      self.SeqReadDmaLba('LEGEND', 0, 99771800, 0x7F, 0x7F)
      objMsg.printMsg('******************** %s PASSED ******************'%TestName)
      objPwrCtrl.powerCycle(5000,12000,10,10)
   #-------------------------------------------------------------------------------------------------------------#
   def HiLowSeek(self, nLowLBA, nHighLBA, nLoop):                   # Customer Type
   
      objMsg.printMsg('Executing HiLowSeek. low LBA=%s, high LBA=%s, loop=%s' %(nLowLBA, nHighLBA, nLoop))
      ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
      ReadVerifySectsExt = {
         'timeout': 600,
         'FEATURES': 0,
         'SECTOR_COUNT': 1,
         'COMMAND': 0x42,
         #'LBA':0,
         'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
      }      
      DisableScriptComment(0x0FF0)     # Suppress output
      result = OK
      for i in range(nLoop):
         if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:            
            data = ICmd.ReadVerifyExt(nLowLBA, 1)
            result = data["LLRET"]
         else:
            # handle SI
            try:
               if objRimType.CPCRiser() and testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #CPC non-intrinsic require 'LBA_LOW', 'LBA_MID' and 'LBA_HIGH'
                  LBA_HIGH, LBA_MID, LBA_LOW = CUtility.convertLBANumber2LBARegister(nLowLBA)
                  ReadVerifySectsExt['LBA_HIGH'] = LBA_HIGH
                  ReadVerifySectsExt['LBA_MID'] = LBA_MID
                  ReadVerifySectsExt['LBA_LOW'] = LBA_LOW
               else: #SIC               
                  ReadVerifySectsExt['LBA'] = self.returnStartLbaWords( nLowLBA )#CUtility.returnStartLbaWords( nLowLBA )
               st (538, ReadVerifySectsExt) 
            except:
               result = NOT_OK
         if result != OK:
            objMsg.printMsg("Read Verify LBA %d failed! %s" %(nLowLBA, traceback.format_exc()))
            break

         if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:            
            data = ICmd.ReadVerifyExt(nHighLBA, 1)
            result = data["LLRET"]
         else:
            try:
               if objRimType.CPCRiser() and testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #CPC non-intrinsic require 'LBA_LOW', 'LBA_MID' and 'LBA_HIGH'
                  LBA_HIGH, LBA_MID, LBA_LOW = CUtility.convertLBANumber2LBARegister(nHighLBA)
                  ReadVerifySectsExt['LBA_HIGH'] = LBA_HIGH
                  ReadVerifySectsExt['LBA_MID'] = LBA_MID
                  ReadVerifySectsExt['LBA_LOW'] = LBA_LOW
               else: #SIC
                  ReadVerifySectsExt['LBA'] = self.returnStartLbaWords( nHighLBA )#CUtility.returnStartLbaWords( nHighLBA )
               st (538, ReadVerifySectsExt)
            except:
               result = NOT_OK
         if result != OK:
            objMsg.printMsg("Read Verify LBA %d failed! %s"% (nHighLBA, traceback.format_exc()))
            break
      
      DisableScriptComment(0)         
      if result != OK:
         ScrCmds.raiseException(13370,"Hi-Low Seek FAIL")
            
            
   #-------------------------------------------------------------------------------------------------------------#
   def FunnelSeek(self):                   # Customer Type

      minLBA = 0
      maxLBA = self.maxLBA
      interval = 0x13146
      result = OK
      
      objMsg.printMsg('Executing FunnelSeek. Loop count = %s, Seek count = %s.' %(maxLBA/interval,(maxLBA/interval)*2))      
      objMsg.printMsg('Funnel Seek block size = 1 , interval = 0x13146')
      if objRimType.CPCRiser():
         ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
         DisableScriptComment(0x0FF0)     # Suppress output 
         while 1:
            data = ICmd.ReadVerifyExt(minLBA, 1)
            result = data["LLRET"]
            if result != OK:
               objMsg.printMsg("Read Verify LBA %d failed! %s" %(minLBA, traceback.format_exc()))
               break

            data = ICmd.ReadVerifyExt(maxLBA, 1)
            result = data["LLRET"]
            if result != OK:
               objMsg.printMsg("Read Verify LBA %d failed! %s" %(maxLBA, traceback.format_exc()))
               break
                  
            if minLBA == self.maxLBA or maxLBA == 0:
               break
            minLBA += 0x13146
            maxLBA -= 0x13146
            if minLBA > self.maxLBA:
               minLBA = self.maxLBA
            if maxLBA < 0:
               maxLBA = 0
               
         DisableScriptComment(0)
         if result != OK:
            ScrCmds.raiseException(13371,"Funnel Seek FAIL")

      else:
         data = ICmd.FunnelSeek(minLBA,maxLBA,interval,1)
         if data['LLRET'] != OK:
            ScrCmds.raiseException(13371,"Funnel Seek FAIL")                                 
         
   #-------------------------------------------------------------------------------------------------------------#
   def RandomSeek(self, nLoop):                   # Customer Type
      objMsg.printMsg('Executing Random Seek. block size = 1, loop = %d'%nLoop)

      end_lba = self.maxLBA
      ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
      ReadVerifySectsExt = {
         'timeout': 600,
         'FEATURES': 0,
         'SECTOR_COUNT': 1,
         'COMMAND': 0x42,
         #'LBA':0,
         'PARAMETER_0': 0x2000 #enables LBA mode cmd reg defs
      }
      result = OK      
      for i in range(nLoop):
         random_lba = random.randint(0, end_lba)
         if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:
            data = ICmd.ReadVerifyExt(random_lba, 1)
            result = data["LLRET"]
         else:
            try:
               if objRimType.CPCRiser() and testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #CPC non-intrinsic require 'LBA_LOW', 'LBA_MID' and 'LBA_HIGH'
                  LBA_HIGH, LBA_MID, LBA_LOW = CUtility.convertLBANumber2LBARegister(random_lba)
                  ReadVerifySectsExt['LBA_HIGH'] = LBA_HIGH
                  ReadVerifySectsExt['LBA_MID'] = LBA_MID
                  ReadVerifySectsExt['LBA_LOW'] = LBA_LOW
               else: #SIC
                  ReadVerifySectsExt['LBA'] = CUtility.returnStartLbaWords( random_lba )
               st (538, ReadVerifySectsExt)
            except:
               result = NOT_OK
         if result != OK:
            objMsg.printMsg("Read Verify LBA %d failed! %s" %(random_lba, traceback.format_exc()))
            ScrCmds.raiseException(13372,"Random Seek FAIL")
            
   #-------------------------------------------------------------------------------------------------------------#
   def LinearVerify(self, nStartLBA, nEndLBA, nBlock):                   # Customer Type
      result = OK
      objMsg.printMsg('Linear Verify startlba = %d, endlba=%d, blockSize=%d'%(nStartLBA,nEndLBA, nBlock))
      ICmd.MakeAlternateBuffer(0x02, nBlock)
      ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
      data = ICmd.SequentialReadVerifyExt(nStartLBA,nEndLBA, nBlock,nBlock,0,0)
      ICmd.RestorePrimaryBuffer(0x02)
      objMsg.printMsg('Linear Verify data = %s'%`data`)
      result = data["LLRET"]
      if result != OK:
         objMsg.printMsg('SequentialReadVerifyExt failed data = %s'%`data`)
         ScrCmds.raiseException(13381,"Linear Verify FAIL")
   #---------------------------------------------------------------------------------------------#
   def SeqReadDmaLba(self,type,nStartLBA=0,nEndLBA = 0, nBlock = 256, nStep = 256):   # LEGEND
      end_lba = self.maxLBA
      min_lba = 0
      step_lba = 256
      sect_cnt = 256
      stamp_flag = 0
      comp_flag = 0
      if type == 'LEGEND':
         start_lba = nStartLBA
         if nEndLBA > self.maxLBA:
            end_lba = self.maxLBA
         else:
            end_lba = nEndLBA
         sect_cnt = nBlock
         step_lba = nStep
      elif type == 'IBM_OD':
         start_lba = 0
         end_lba = min_lba + 200000
      elif type == 'IBM_ID':
         start_lba = end_lba - 200000
      start_time = time.time()
      ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
      result = ICmd.SetFeatures(0x03, 0x45)['LLRET']
      if result != OK:
         objMsg.printMsg('Set Feature Failed')

      if result == OK:
         objMsg.printMsg('-->Seq DMA Read Test   %s, start_lba=%d, end_lba=%d, step_lba=%d, sect_cnt=%d, stamp_flag = %d, com_flag=%d' % (type, start_lba, end_lba, step_lba, sect_cnt, stamp_flag, comp_flag))
         data = ICmd.SequentialReadDMAExt(start_lba, end_lba, step_lba, sect_cnt, stamp_flag, comp_flag)
         result  = data['LLRET']
         if result == OK:
            objMsg.printMsg('Seq DMA Read Test Passed' )
         else:
            objMsg.printMsg('Seq DMA Read Test Failed !!!')
            objMsg.printMsg('data = %s' % data)

      end_time = time.time()
      min, sec = self.Cal_Min_Sec(start_time,end_time)
      objMsg.printMsg('Seq DMA Read TestTime = %d:%d' % (min, sec))
      if result != OK:
         ScrCmds.raiseException(12656,"Seq DMA Read Test FAIL")
   #-----------------------------------------------------------------------------------------#
   def Cal_Min_Sec(self,start_time,end_time):
      total_time = end_time - start_time
      test_time_min = int(total_time / 60)       # get min
      test_time_sec = total_time % 60            # get sec
      return test_time_min, test_time_sec
   #-----------------------------------------------------------------------------------------#
   def SmartDSTShort(self):
      oProcess = CProcess()
      objMsg.printMsg('Smart DST Short')
      #objPwrCtrl.powerCycle(5000,12000,10,30)
      #ICmd.HardReset()
      oProcess.St(TP.prm_638_Unlock_Seagate)
      try:
         oProcess.St(TP.prm_600_short)
      except:
         smartEnableOperData = ICmd.SmartEnableOper()
         objMsg.printMsg("DST SmartEnableOper data: %s" % smartEnableOperData, objMsg.CMessLvl.IMPORTANT)
         if smartEnableOperData['LLRET'] != 0:
            ScrCmds.raiseException(13455, 'Failed Smart Enable Oper - During Short DST')
         DSTLogData = ICmd.SmartReadLogSec(6, 1)               # 6=DST Log, 1=#DST Log Sectors
         objMsg.printMsg("DST SmartReadLogSec data: %s" % DSTLogData, objMsg.CMessLvl.IMPORTANT)

         ScrCmds.raiseException(13458, 'Failed Smart Short DST - Drive Self Test')

      #objPwrCtrl.powerCycle(5000,12000,10,30)
   #-------------------------------------------------------------------------------------------------------
   def VerifySMART(self):
      objMsg.printMsg('Verify Smart')
      smartEnableOperData = ICmd.SmartEnableOper()
      objMsg.printMsg("SmartEnableOper data: %s" % smartEnableOperData, objMsg.CMessLvl.IMPORTANT)
      if smartEnableOperData['LLRET'] != 0:
         ScrCmds.raiseException(13455, 'Failed Smart Enable Oper')

      CriticalLogData = ICmd.SmartReadLogSec(0xA1,1)

      smartReturnStatusData = ICmd.SmartReturnStatus()
      objMsg.printMsg("SmartReturnStatus data: %s" % smartReturnStatusData, objMsg.CMessLvl.IMPORTANT)
      objMsg.printMsg("SmartReturnStatus value: %x" % int(smartReturnStatusData['LBA']), objMsg.CMessLvl.IMPORTANT)
      if int(smartReturnStatusData['LBA']) != 0xc24f00:
         ScrCmds.raiseException(13455, 'Failed Smart Threshold Value')


###########################################################################################################
class CIntfTTR(CState):
   """
      Performs Power On to Interface Ready test.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
      
      self.readytimedata = []
      self.totalreadytime = 0      
   #-------------------------------------------------------------------------------------------------------
   def run(self):

#CHOOI-01June17 OffSpec
#      ttrLoop = 20
      ttrLoop = 5
      objMsg.printMsg('ATA Ready Limit =  %d Msec.' %objDut.readyTimeLimit)
      self.checkTTR(ttrLoop, **self.ttrData(ttrLoop))
           
   def ttrData(self, ttrLoop):
      ''' Collect TTR data'''

      if ConfigVars[CN].get('PRODUCTION_MODE',0):
         retry = 1
      else:
         retry = 2   # default retry

      for loopCnt in range(ttrLoop):
         objMsg.printMsg(20*'*' + " Loop"+ str(loopCnt+1) + ": Interface TTR Test " + 20*'*')
         if objRimType.CPCRiser():
            self.BasicCPCPowerCycle(retry = retry)

         elif objRimType.IOInitRiser():
            objPwrCtrl.initiatorDriveReadyPwrCycle(ttrMode=True)
            self.readytimedata.append(objPwrCtrl.readyTime)
            self.totalreadytime += objPwrCtrl.readyTime
         
      return dict(readytimedata=self.readytimedata, totalreadytime=self.totalreadytime)
   
   def BasicCPCPowerCycle(self, retry = 2):
      """ Mimic a drive only power cycle in CPC cell """
       
      err = 1; timeout = 30000
      spinUpFlag = objPwrCtrl.getSpinUpFlag()
      while retry:
         retry -= 1

         ICmd.StandbyImmed()
         
         # Power-off the drive
         theCarrier.powerOffPort(offTime=10, driveOnly=1)
            
         # Power-on the drive
         ICmd.PowerOnTiming(timeout+(10000), spinUpFlag)    # These 3 Commands must be together, Nothing in between
         theCarrier.powerOnPort(driveOnly=1)
         data = ICmd.StatusCheck()
         if data['LLRET'] != OK:  
            continue # do retry on power-on failure
            
         readyTime = int(data['SpinUpTm'])
         objPwrCtrl.logPowerOn_Information(readyTime,spinUpFlag,data)
         objPwrCtrl.incrementLifetimePowerCycleCounter()
         if readyTime <= objDut.readyTimeLimit:
            self.readytimedata.append(readyTime)
            self.totalreadytime += readyTime
            objMsg.printMsg('ATA Ready Passed in %d Msec.' %readyTime)
            err = 0
            break
         objMsg.printMsg('ATA Ready Failed in %d Msec.' %readyTime)

      else:
         ScrCmds.raiseException(13424,'ATA Ready Failed GetPowerOnTime Data = %s' % data)
      if err:
         ScrCmds.raiseException(13424,'ATA Ready Failed in %d Msec.  Limit = %d ' % (readyTime, objDut.readyTimeLimit))
             
   def checkTTR(self, ttrLoop, **kwargs):
      ''' Do TTR limit checking and grading.'''
      
      MaxTime, AvgTime = 0, 0
      if kwargs.get('totalreadytime',0) <= 0 and not testSwitch.virtualRun:
         ScrCmds.raiseException(10197, "Unable to read TTR value")      
      
      MaxTime, AvgTime = max(kwargs['readytimedata']), (kwargs.get('totalreadytime',0)/ttrLoop)
      objMsg.printMsg('Max Time = %2.3f sec, Average Time = %2.3f sec' %(MaxTime/1000.0, AvgTime/1000.0))
      
      if testSwitch.FE_0007406_402984_USE_INTFTTR_MAX_VALUE:
         self.dut.driveattr['TIME_TO_READY'] = MaxTime
         pTTR = MaxTime/1000.0
      else:
         self.dut.driveattr['FIN_READY_TIME'] = AvgTime
         pTTR = AvgTime/1000.0

      err = 0
      # RW72D - Max specs to fail if 3F/20 measurement.
      if testSwitch.NEW_TTR_SPEC_CHECK: 
         newMaxTime = 0
         FailTTRCount = 0
         FailCountAllowed = getattr(TP, 'MAX_SPTTR_COUNT_ALLOWED', 1)
         readydata = kwargs['readytimedata']
         for i in xrange(ttrLoop):
            if readydata[i] > objPwrCtrl.readyTimeLimit:
               FailTTRCount = FailTTRCount + 1
               objMsg.printMsg('Max TTR exceeds limit: (%s/%s) %smsec' %(FailTTRCount, FailCountAllowed, readydata[i]))
               if FailTTRCount >= FailCountAllowed:
                  msg = "Max TTR Count = %s exceeds limit: %smsec" %(str(FailCountAllowed), str(objPwrCtrl.readyTimeLimit))
                  err = 1
                  break
            else:
               newMaxTime = max(newMaxTime,readydata[i]) #MAX TIME_TO_READY shall exclude TTR > spec. limit
      elif MaxTime > objPwrCtrl.readyTimeLimit:
         msg = "Max TTR = %smsec exceeds limit: %smsec" %(str(MaxTime), str(objPwrCtrl.readyTimeLimit))
         err = 1

      if (err == 0) and testSwitch.NEW_TTR_SPEC_CHECK and (FailTTRCount != 0):
         # When drive didn't fail 3F/20, MAX TIME_TO_READY shall exclude TTR > spec. limit
         objMsg.printMsg('New Max Time = %2.3f sec, Average Time = %2.3f sec' %(newMaxTime/1000.0, AvgTime/1000.0))
         self.dut.driveattr['TIME_TO_READY'] = newMaxTime
         pTTR = newMaxTime/1000.0

      self.dut.dblData.Tables('P_TTR').addRecord({
                              'SPC_ID' : self.dut.objSeq.curRegSPCID,
                              'OCCURRENCE': self.dut.objSeq.getOccurrence(),
                              'SEQ' : self.dut.objSeq.curSeq,
                              'TEST_SEQ_EVENT': self.dut.objSeq.getTestSeqEvent(0),
                              'TTR': pTTR})
      if err:
         ScrCmds.raiseException(10197, msg)


###########################################################################################################
class CSP_TTR(CIntfTTR):
   """
      Performs Serial Port Power On to Serial Port Time to Ready test.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CIntfTTR.__init__(self, dut, depList)
      self.dut = dut


   #-------------------------------------------------------------------------------------------------------
   def ttrData(self, ttrLoop):

      objMsg.printMsg('CSP_TTR')
      from SerialCls import baseComm
      from Cell import theCell
      readytimedata,totalreadytime,MaxTime,AvgTime = [],0,0,0
      testSwitch.extern.CONGEN_SUPPORT = 1

      if objRimType.IOInitRiser():
         DisableStaggeredStart(True)
         objMsg.printMsg('DisableStaggeredStart for SI cells')

      from serialScreen import sptDiagCmds
      oSerial = sptDiagCmds()

      #oSerial.enableDiags()
      #oSerial = serialScreen.sptDiagCmds()
      oSerial.enableDiags()

      try:
         baudRate=Baud38400
         oSerial.gotoLevel('T')
         oSerial.sendDiagCmd('B%s' %baudRate, timeout=3, printResult=False, raiseException = 0, suppressExitErrorDump = 1)
         theCell.setBaud(baudRate)

         #Get TTR signature through CTRL_Y OR changing Congen setting
         CtrlY_TTR = False
         accumulator = baseComm.PChar(CTRL_Y)
         data = sptCmds.promptRead(10, accumulator = accumulator, altPattern = "status")
         del accumulator
         Mat = re.search('TOTAL\s*TTR\s*= (?P<TTR>[\dA-F]+)', data)
         if Mat:
            CtrlY_TTR = True
            objMsg.printMsg("Read TTR through CTRL_Y")
         else:
            try:
               oSerial.changeAMPS("DebugValue", 0xCAFE0100)
            except:
               pass
            objMsg.printMsg("CTRL_Y doesn't include TTR signature. Read TTR by changing Congen")

         for i in xrange(ttrLoop):
            baseComm.flush()
            DriveOff(pauseTime=8)
            DriveOn(pauseTime=0)

            if testSwitch.SMRPRODUCT:
               # delay longer to allow SMR drive to complete background tasks, otherwise longer TTR observed on next loop
               time.sleep(5)
            else:
               time.sleep(3)

            if CtrlY_TTR: #Only when Congen has been changed, we hv 'TTR' signature
               altPattern = None
            else:
               altPattern = "TTR ="

            for retry in xrange(5):
               try:
                  accumulator = baseComm.PChar(CTRL_Z)
                  data = sptCmds.promptRead(2, accumulator = accumulator, altPattern = altPattern)
                  del accumulator
                  break
               except:
                  objMsg.printMsg("TTR Loop=%s Retry=%s CTRL_Z traceback=%s" % (i, retry, `traceback.format_exc()`))
            else:
               raise

            if CtrlY_TTR:
               altPattern = "TTR ="
               accumulator = baseComm.PChar(CTRL_Y)
               data = sptCmds.promptRead(10, accumulator = accumulator, altPattern = altPattern)
               del accumulator

            #data = oSerial.sendDiagCmd(CTRL_Z, timeout=10, loopSleepTime = 1, altPattern = 'TTR  = [\dA-F]{8}', raiseException = 0, suppressExitErrorDump = 1)
            if i < 5:   # print only first 3 values...
               objMsg.printMsg('Power on data=%s' % `data`)
            iTTR = 0
            if testSwitch.virtualRun:
               iTTR = random.randint(2000,3000)

            Mat = re.search('TOTAL\s*TTR\s*= (?P<TTR>[\dA-F]+)', data) # ignore whitespaces with \s*

            if Mat:
               iTTR = int(Mat.groupdict()['TTR'], 16)
            else:
               objMsg.printMsg("Trying to read Apple TTR")
               Mat1 = re.search('TTR1 = (?P<TTR1>[\dA-F]+)', data)
               Mat2 = re.search('TTR2 = (?P<TTR2>[\dA-F]+)', data)
               if Mat1 and Mat2:
                  iTTR = int(Mat1.groupdict()['TTR1'], 16) + int(Mat2.groupdict()['TTR2'], 16)
            objMsg.printMsg('iSerialNum=%s iLoop=%s iTTR=%s' % (self.dut.serialnum, i+1, iTTR))

            if iTTR == 0:
               ScrCmds.raiseException(10197, "Unable to read SPTTR value")

            Offset = float(getattr(TP, 'SPTTR_OFFSET', 0))
            if Offset != 0:
               iTTR = int(iTTR + Offset)
               objMsg.printMsg('Offset=%s New iTTR=%s' % (Offset, iTTR))

            curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

            self.dut.dblData.Tables('P_TIME_TO_READY').addRecord(
            {
               'SPC_ID': 888,
               'OCCURRENCE':occurrence,
               'SEQ':curSeq,
               'TEST_SEQ_EVENT': testSeqEvent,
               'SET_3V': 0,
               'SET_5V': 0,
               'SET_12V': 0,
               'SENSE_VOLTAGE_3V': 0,
               'SENSE_VOLTAGE_5V': 0,
               'SENSE_VOLTAGE_12V': 0,
               'SENSE_CURRENT_3V': 0,
               'SENSE_CURRENT_5V': 0,
               'SENSE_CURRENT_12V': 0,
               'POWER_OPTIONS': 0,
               'DEVICE_ERROR_RGSTR': 0,
               'DEVICE_STATUS_RGSTR': 0,
               'SPIN_UP_TIME_TO_READY': iTTR,
            })
            readyTime = iTTR
            readytimedata.append(readyTime)
            totalreadytime += readyTime

            if i == 9:
               # to do - collect more data and change spec_max/spec_stddev below
               spec_max = 0
               spec_stddev = 0

               #objMsg.printMsg("PBIC check readytimedata: %s" % readytimedata)
               from MathLib import stDev_standard
               MaxTTR = max(readytimedata)
               StdDevTTR = stDev_standard(readytimedata)
               self.dut.driveattr['PROC_CTRL23'] = "TTR/%s/%.2f" % (MaxTTR, StdDevTTR)
               objMsg.printMsg("PBIC MaxTTR=%s StdDevTTR=%.2f spec_max=%s spec_stddev=%s" % (MaxTTR, StdDevTTR, spec_max, spec_stddev))

               if MaxTTR < spec_max and StdDevTTR < spec_stddev:
                  objMsg.printMsg("PBIC activated. Skipping the rest of TTR loops")
                  break
      except:
         objMsg.printMsg("SP_TTR Error : %s" % traceback.format_exc())


      # Reset AMPS
      objMsg.printMsg('oSerial.resetAMPs')

      if self.dut.SkipPCycle and not testSwitch.FE_0246029_385431_SED_DEBUG_MODE:
         objMsg.printMsg("CSP_TTR SkipPCycle")
      else:
         objPwrCtrl.powerCycle(5000,12000,10,30)

      oSerial.enableDiags()
      if not CtrlY_TTR:
         objMsg.printMsg('Reset AMPs after TTR test')
         oSerial.resetAMPs()
         objPwrCtrl.powerCycle(5000,12000,10,30)
      #objMsg.printDblogBin(self.dut.dblData.Tables('P_TTR'))
      objMsg.printDblogBin(self.dut.dblData.Tables('P_TIME_TO_READY'), spcId32 = 888)

      return dict(readytimedata=readytimedata, totalreadytime=totalreadytime)


###########################################################################################################
class CAPMIdle(CState):
   """
      Description: Class that will perform APMIdle test. IdleAPM_TTR is expected in CPC 2.216 onwards
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      imaxLBA = CIdentifyDevice().ID["IDDefault48bitLBAs"]

      loop = 20
      if ConfigVars[CN]['BenchTop']:
         loop = 2

      objMsg.printMsg('IdleAPM_TTR with loop : %d' % loop)
      for i in xrange(loop):
         objPwrCtrl.powerCycle(5000, 12000, 6, 0) # offtime 6sec; ontime 0 sec to let CPC perform delay
         result = ICmd.IdleAPM_TTR(7, 0, imaxLBA, 256, 10) # IdleAPM_TTR(delay,minLba,maxLba,scnt,loopCnt)
         if result['LLRET'] != OK:
            msg = 'Fail IdleAPM_TTR. Return data = %s' % result
            ScrCmds.raiseException(10072, msg)

###########################################################################################################
class CAppleScreen(CState):
   """
      Description:
         -Read Grown and Pending defect list from Smart log A8h and A9h
         -20 times of power cycle
         -Random seek for 5mins
         -Random write for 5mins per head
         -Random Write DMA Ext (35h) at first zone (for 30,000 counts)
         -Random Write DMA Ext (35h) at last zone (for 30,000 counts)
         -Random Write DMA Ext (35h) at 60% to 70% of drive LBA (for 30,000 counts)
         -Full pack IO read (ECC=10, fail on 1 error)
         -Read Grown and Pending defect list from Smart log A8h and A9h
          Compare for increase in Grown and Pending defect list entries.  
          Fail drive if any new entries/counts
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from base_IntfTest import CPowerCycleLoops, CRandomWrite

      ScrCmds.insertHeader("Apple Screen Test",headChar='#')
      CAppleScreens_CET(self.dut,params={}).displaydefectlists()
      CPowerCycleLoops(self.dut, params = {'LOOP_COUNT': 20}).run()           # 20 powerCycles
      CRandomSeekScreen(self.dut, params = {'LOOP_COUNT': 60000}).run()       # ~5 minutes of random seeks

      CRandomWrite(self.dut).run()
      CAppleScreens_CET(self.dut,params={}).run()
###########################################################################################################
class CBluenunScanMulti(CState):
   """
      Description: Perform new bluenunscan test updated as per Apple_test_process.ppt by Jack Lakey
      BluenunMulti support is expected in CPC 2.217 or newer

      Description: Perform new AppleThread test updated as per Apple_test_process.ppt by Jack Lakey
                   which is a true multi threaded function
      ApplThread support is expected in CPC 2.221 or newer
         AppleThread( QWORD skipSeqMaxLBA, DWORD skipSeqSCnt,
             DWORD lba0SCnt, DWORD lba0Delay,
             QWORD bounceMaxLBA, DWORD bounceSCnt,
             QWORD bounceSkipCnt, DWORD bouncePeriod )
         The AppleThread() function simultaneously executes three tests at the same time.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      defaultParams = {
         'span1'     : 0x1100000 * 6,  # 8.5GB * 6 for thread1
         'span3'     : 0x440000,       # 2GB for thread3
         'skip3'     : 0x4B000,        # 300kblocks
         '3threaded' : 1,              # 0 for emulation mode using ICmd.BluenunMulti, 1 for 3 threaded mode using ICmd.AppleThread
         }

      AppleThreadParams = getattr(TP, 'AppleThreadParams', defaultParams)
      span1    = AppleThreadParams['span1']
      span3    = AppleThreadParams['span3']
      skip3    = AppleThreadParams['skip3']
      
      if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:
         ThreeThreaded = AppleThreadParams['3threaded']
      elif objRimType.IOInitRiser() or (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()):
         ThreeThreaded = 0

      if testSwitch.FE_0161626_231166_P_DISABLE_TEMP_MSR_BLUE_NUN:
         from serialScreen import sptDiagCmds
         import sptCmds
         oSerial = sptDiagCmds()

         oSerial.enableDiags()
         oSerial.SetAppleTempTransmissionInAMPS(enable = False)
         sptCmds.enableESLIP()


      if DEBUG:
         span1 = span1 / 10

      if ThreeThreaded == 0:
         objMsg.printMsg('ICmd.BluenunMulti span1 = 0X%x span3 = 0X%x skip3 = 0X%x' % (span1, span3, skip3))
         result = ICmd.BluenunMulti(span1, 256, span3, skip3)
      else:
         objMsg.printMsg('ICmd.AppleThread span1 = 0X%x span3 = 0X%x skip3 = 0X%x' % (span1, span3, skip3))
         result = ICmd.AppleThread(span1, 256, 256, 2000, span3, 256, skip3, 1500)

      objMsg.printMsg("CBluenunMulti Result = %s" % result)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14520, "BlueNunMulti Scan")

      result = ICmd.SmartCheck()
      objMsg.printMsg("SmartCheck Result = %s" % result)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(14520, "Fail SmartCheck")


      if testSwitch.FE_0161626_231166_P_DISABLE_TEMP_MSR_BLUE_NUN:
         sptCmds.enableDiags()
         oSerial.resetAMPs()
         sptCmds.enableESLIP()



###########################################################################################################
class CSTRTest(CState):
   """
      Sustain transfer rate test for Microsoft
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
      self.DBLogData = {}    
       
   #---------------------------------------------------------------------------------------------------------#
   def doOffset(self, TPKey, OrgValue):
      ret = int(round(OrgValue + float(getattr(TP, TPKey, 0)))) #round off to the nearest integer
      objMsg.printMsg('MSSTR Offset... before=%s after=%s' % (OrgValue, ret))
      return ret
                   
   #-------------------------------------------------------------------------------------------------------
   def _getTransferRate(self, loopcount, zone, spcid, startLBA, TotalBlksXfr, BlksPerXfr, mode, nLowLimit = None, nUpLimit = None):
      ICmd.FlushCacheExt()

      if mode.lower() == 'read':
         data = ICmd.ReadDMAExtTransRate(startLBA, TotalBlksXfr, BlksPerXfr)

         if testSwitch.NoIO: # apply offset to align to interface data            
            if zone.lower() == 'od':      
               data['TXRATE'] = self.doOffset("CSTR_RDOD_OFFSET", int(data['TXRATE']))
            elif zone.lower() == 'id': 
               data['TXRATE'] = self.doOffset("CSTR_RDID_OFFSET", int(data['TXRATE']))

         objMsg.printMsg("ReadDMAExtTransRate (%10d, %d, %d), result = %s, TXRATE: %s, Limit: %s to %s"%(startLBA, TotalBlksXfr, BlksPerXfr, str(data.get('RESULT')), str(data.get('TXRATE')), str(nLowLimit), str(nUpLimit)))
      elif mode.lower() == 'write':
         data = ICmd.WriteDMAExtTransRate(startLBA, TotalBlksXfr, BlksPerXfr)

         if testSwitch.NoIO: # apply offset to align to interface data            
            if zone.lower() == 'od':      
               data['TXRATE'] = self.doOffset("CSTR_WROD_OFFSET", int(data['TXRATE']))
            elif zone.lower() == 'id': 
               data['TXRATE'] = self.doOffset("CSTR_WRID_OFFSET", int(data['TXRATE']))

         objMsg.printMsg("WriteDMAExtTransRate(%10d, %d, %d), result = %s, TXRATE: %s, Limit: %s to %s"%(startLBA, TotalBlksXfr, BlksPerXfr, str(data.get('RESULT')), str(data.get('TXRATE')), str(nLowLimit), str(nUpLimit)))

      if data['LLRET'] != OK:
         ScrCmds.raiseException(10161, "%s transfer rate ERROR"%mode)
      else:                              
         if not self.DBLogData.has_key(loopcount):
            self.DBLogData[loopcount] = {1:{"ID": [],"OD":[]},2:{"ID": [],"OD":[]}}        
         self.DBLogData[loopcount][spcid][zone] = [startLBA,TotalBlksXfr]
         self.DBLogData[loopcount][spcid][zone].append(int(data['TXRATE']))

      if nLowLimit != None and int(data['TXRATE']) < nLowLimit:
         return 1, ['L', int(data['TXRATE'])]

      if nUpLimit != None and int(data['TXRATE']) > nUpLimit:
         return 1, ['U', int(data['TXRATE'])]

      return 0, []
   #-------------------------------------------------------------------------------------------------------
   def _makeDBLOutput(self):
      for loopcnt,value in self.DBLOutput:      
         self.dut.dblData.Tables('P_SUSTAINED_TRANSFER_RATE').addRecord({
                                 'SPC_ID' : str(loopcnt),
                                 'OCCURRENCE': self.dut.objSeq.getOccurrence(),
                                 'SEQ' : self.dut.objSeq.curSeq,
                                 'TEST_SEQ_EVENT': self.dut.objSeq.getTestSeqEvent(0),
                                 'START_LBA': str(value[0]),
                                 'TOTAL_TEST_LBAS': value[1],
                                 'WRITE_XFER_RATE': value[2],
                                 'READ_XFER_RATE':  value[3]
                                 })                                                                  
      try:   objMsg.printDblogBin(self.dut.dblData.Tables('P_SUSTAINED_TRANSFER_RATE'))
      except: pass
   #-------------------------------------------------------------------------------------------------------
   def _printFailLog(self, failLog):
      objMsg.printMsg("failLog = %s" % failLog)
      objMsg.printMsg("Loop  ReadID   ReadOD   WriteID  WriteOD")
      objMsg.printMsg("========================================")
      for failList in failLog:
         listStr = "%3s" % failList[0]
         if (failList[1] == "ReadID"):  listStr += "%5s(%2d)" % (failList[2], failList[3])
         else: listStr += " " * 9
         if (failList[1] == "ReadOD"):  listStr += "%5s(%2d)" % (failList[2], failList[3])
         else: listStr += " " * 9
         if (failList[1] == "WriteID"): listStr += "%5s(%2d)" % (failList[2], failList[3])
         else: listStr += " " * 9
         if (failList[1] == "WriteOD"): listStr += "%5s(%2d)" % (failList[2], failList[3])
         else: listStr += " " * 9
         objMsg.printMsg("%s " % listStr)
      objMsg.printMsg("========================================")

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      if testSwitch.FE_0385813_385431_Enable_MSFT_CactusScreen:
         CMicrosoftCactusTest(self.dut, self.params).run() # Run Cactus Screen

      objPwrCtrl.powerCycle(5000, 12000, 10, 30)
      result = ICmd.FlushCache()
      if result['LLRET'] != OK:
         ScrCmds.raiseException(11044, "CSTRTest - Failed to flush cache")

      result = ICmd.ClearBinBuff(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(11044, "CSTRTest - Failed to fill buffer for zero write")

      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      testCap = TP.prm_microsoft.get('TEST_LBAS', 0x5000)   # 10M

      readOdLowLimit  = TP.prm_microsoft.get('READ_OD_LOW_LIMIT', None)
      readOdUpLimit   = TP.prm_microsoft.get('READ_OD_UP_LIMIT', None)
      readIdLowLimit  = TP.prm_microsoft.get('READ_ID_LOW_LIMIT', None)
      readIdUpLimit   = TP.prm_microsoft.get('READ_ID_UP_LIMIT', None)

      writeOdLowLimit = TP.prm_microsoft.get('WRITE_OD_LOW_LIMIT', None)
      writeOdUpLimit  = TP.prm_microsoft.get('WRITE_OD_UP_LIMIT', None)
      writeIdLowLimit = TP.prm_microsoft.get('WRITE_ID_LOW_LIMIT', None)
      writeIdUpLimit  = TP.prm_microsoft.get('WRITE_ID_UP_LIMIT', None)

      TestLoop = TP.prm_microsoft.get('LOOP', 15)        

      failLog = []
      ScrCmds.insertHeader("Perform OD Write %s times" %TestLoop,headChar='#')
      for i in range(TestLoop):
         result = self._getTransferRate(i,"OD",1,0, testCap, 256, 'write', writeOdLowLimit, writeOdUpLimit)
         if (result[0]): failLog.append([i + 1, 'WriteOD'] + result[1])
      if len(failLog) > 0:
         self._printFailLog(failLog)
         if testSwitch.virtualRun:
            ScrCmds.statMsg("(VE) Raise Exception: Microsoft Sustain Transfer Rate Test Failed!")
         else:
            ScrCmds.raiseException(10578, "Microsoft Sustain Transfer Rate Test Failed!")

      failLog = []
      ScrCmds.insertHeader("Perform OD Read %s times" %TestLoop,headChar='#')
      for i in range(TestLoop):
         result = self._getTransferRate(i,"OD",2,0, testCap, 256, 'read', readOdLowLimit, readOdUpLimit)
         if (result[0]): failLog.append([i + 1, 'ReadOD'] + result[1])
      if len(failLog) > 0:
         self._printFailLog(failLog)
         if testSwitch.virtualRun:
            ScrCmds.statMsg("(VE) Raise Exception: Microsoft Sustain Transfer Rate Test Failed!")
         else:
            ScrCmds.raiseException(10578, "Microsoft Sustain Transfer Rate Test Failed!")

      failLog = []
      ScrCmds.insertHeader("Perform ID Write %s times" %TestLoop,headChar='#')
      for i in range(TestLoop):
         result = self._getTransferRate(i,"ID",1,maxLBA - testCap, testCap, 256, 'write', writeIdLowLimit, writeIdUpLimit)
         if (result[0]): failLog.append([i + 1, 'WriteID'] + result[1])
      if len(failLog) > 0:
         self._printFailLog(failLog)
         if testSwitch.virtualRun:
            ScrCmds.statMsg("(VE) Raise Exception: Microsoft Sustain Transfer Rate Test Failed!")
         else:
            ScrCmds.raiseException(10578, "Microsoft Sustain Transfer Rate Test Failed!")

      failLog = []
      ScrCmds.insertHeader("Perform ID Read %s times" %TestLoop,headChar='#')
      for i in range(TestLoop):
         result = self._getTransferRate(i,"ID",2,maxLBA - testCap, testCap, 256, 'read', readIdLowLimit, readIdUpLimit)
         if (result[0]): failLog.append([i + 1, 'ReadID'] + result[1])
      if len(failLog) > 0:
         self._printFailLog(failLog)
         if testSwitch.virtualRun:
            ScrCmds.statMsg("(VE) Raise Exception: Microsoft Sustain Transfer Rate Test Failed!")
         else:
            ScrCmds.raiseException(10578, "Microsoft Sustain Transfer Rate Test Failed!")

      #DBlog Output
      try:
         self.DBLOutput = []       
         for loopcnt,item in self.DBLogData.items(): 
            self.DBLOutput.append([loopcnt*2+1, item[1]['OD'][:3] + item[2]['OD'][2:]]) #Write/Read 'OD'
            self.DBLOutput.append([loopcnt*2+2, item[1]['ID'][:3] + item[2]['ID'][2:]]) #Write/Read 'ID'
         self._makeDBLOutput()            
      except: pass      

      objPwrCtrl.powerCycle(5000, 12000, 10, 30)


###########################################################################################################
###########################################################################################################
class CMicrosoftCactusTest(CState):
   """
      Microsoft Cactus Test
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
      self.DBLogData = {}    

   #---------------------------------------------------------------------------------------------------------#
   def doOffset(self, TPKey, OrgValue):
      ret = int(round(OrgValue + float(getattr(TP, TPKey, 0)))) #round off to the nearest integer
      objMsg.printMsg('MSSTR Offset... before=%s after=%s' % (OrgValue, ret))
      return ret

   #-------------------------------------------------------------------------------------------------------
   def _getTransferRate(self, loopcount, zone, spcid, startLBA, TotalBlksXfr, BlksPerXfr, mode, nLowLimit = None, nUpLimit = None):
      ICmd.FlushCacheExt()

      if mode.lower() == 'read':
         data = ICmd.ReadDMAExtTransRate(startLBA, TotalBlksXfr, BlksPerXfr)
         objMsg.printMsg("ReadDMAExtTransRate (%10d, %d, %d), result = %s, TXRATE: %s, Limit: %s to %s"%(startLBA, TotalBlksXfr, BlksPerXfr, str(data.get('RESULT')), str(data.get('TXRATE')), str(nLowLimit), str(nUpLimit)))

      elif mode.lower() == 'write':
         data = ICmd.WriteDMAExtTransRate(startLBA, TotalBlksXfr, BlksPerXfr)
         objMsg.printMsg("WriteDMAExtTransRate(%10d, %d, %d), result = %s, TXRATE: %s, Limit: %s to %s"%(startLBA, TotalBlksXfr, BlksPerXfr, str(data.get('RESULT')), str(data.get('TXRATE')), str(nLowLimit), str(nUpLimit)))

      if data['LLRET'] != OK:
         ScrCmds.raiseException(10161, "%s transfer rate ERROR"%mode)
      else:                              
         if not self.DBLogData.has_key(loopcount):
            self.DBLogData[loopcount] = {1:{"ID": [],"OD":[]},2:{"ID": [],"OD":[]}}        
         self.DBLogData[loopcount][spcid][zone] = [startLBA,TotalBlksXfr]
         self.DBLogData[loopcount][spcid][zone].append(int(data['TXRATE']))

      if nLowLimit != None and int(data['TXRATE']) < nLowLimit:
         return 1, ['L', int(data['TXRATE'])]

      if nUpLimit != None and int(data['TXRATE']) > nUpLimit:
         return 1, ['U', int(data['TXRATE'])]

      return 0, []
   #-------------------------------------------------------------------------------------------------------
   def _makeDBLOutput(self):
      for loopcnt,value in self.DBLOutput:      
         self.dut.dblData.Tables('P_SUSTAINED_TRANSFER_RATE').addRecord({
                                 'SPC_ID' : str(loopcnt+100),
                                 'OCCURRENCE': self.dut.objSeq.getOccurrence(),
                                 'SEQ' : self.dut.objSeq.curSeq,
                                 'TEST_SEQ_EVENT': self.dut.objSeq.getTestSeqEvent(0),
                                 'START_LBA': str(value[0]),
                                 'TOTAL_TEST_LBAS': value[1],
                                 'WRITE_XFER_RATE': value[2],
                                 'READ_XFER_RATE':  value[3]
                                 })                                                                  
      try:   objMsg.printDblogBin(self.dut.dblData.Tables('P_SUSTAINED_TRANSFER_RATE'))
      except: pass
   #-------------------------------------------------------------------------------------------------------
   def _printFailLog(self, failLog):
      objMsg.printMsg("failLog = %s" % failLog)
      objMsg.printMsg("Loop  ReadID   ReadOD   WriteID  WriteOD")
      objMsg.printMsg("========================================")
      for failList in failLog:
         listStr = "%3s" % failList[0]
         if (failList[1] == "ReadID"):  listStr += "%5s(%2d)" % (failList[2], failList[3])
         else: listStr += " " * 9
         if (failList[1] == "ReadOD"):  listStr += "%5s(%2d)" % (failList[2], failList[3])
         else: listStr += " " * 9
         if (failList[1] == "WriteID"): listStr += "%5s(%2d)" % (failList[2], failList[3])
         else: listStr += " " * 9
         if (failList[1] == "WriteOD"): listStr += "%5s(%2d)" % (failList[2], failList[3])
         else: listStr += " " * 9
         objMsg.printMsg("%s " % listStr)
      objMsg.printMsg("========================================")

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      objMsg.printMsg("=== Microsoft Cactus Test ===")

      objPwrCtrl.powerCycle(5000, 12000, 10, 30)
      result = ICmd.FlushCache()
      if result['LLRET'] != OK:
         ScrCmds.raiseException(11044, "CMCactusTest - Failed to flush cache")

      result = ICmd.ClearBinBuff(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(11044, "CMCactusTest - Failed to fill buffer for zero write")

      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      testCap = TP.prm_microsoft_Cactus.get('TEST_LBAS', 0x5000)   # 10M

      readOdLowLimit  = TP.prm_microsoft_Cactus.get('READ_OD_LOW_LIMIT', None)
      readOdUpLimit   = TP.prm_microsoft_Cactus.get('READ_OD_UP_LIMIT', None)
      readIdLowLimit  = TP.prm_microsoft_Cactus.get('READ_ID_LOW_LIMIT', None)
      readIdUpLimit   = TP.prm_microsoft_Cactus.get('READ_ID_UP_LIMIT', None)

      writeOdLowLimit = TP.prm_microsoft_Cactus.get('WRITE_OD_LOW_LIMIT', None)
      writeOdUpLimit  = TP.prm_microsoft_Cactus.get('WRITE_OD_UP_LIMIT', None)
      writeIdLowLimit = TP.prm_microsoft_Cactus.get('WRITE_ID_LOW_LIMIT', None)
      writeIdUpLimit  = TP.prm_microsoft_Cactus.get('WRITE_ID_UP_LIMIT', None)

      OD_TestLoop = TP.prm_microsoft_Cactus.get('OD_LOOP', 15)        
      OD_StartLBA = (TP.prm_microsoft_Cactus.get('OD_StartLBA', 780)*10*testCap)       
      if OD_TestLoop:
         failLog = []
         ScrCmds.insertHeader("Perform OD Write %s times" %OD_TestLoop,headChar='#')
         for i in range(OD_TestLoop):
            result = self._getTransferRate(i,"OD",1,(OD_StartLBA+i*testCap), testCap, 256, 'write', writeOdLowLimit, writeOdUpLimit)
            if (result[0]): failLog.append([i + 1, 'WriteOD'] + result[1])
         if len(failLog) > 0:
            self._printFailLog(failLog)
            if testSwitch.virtualRun:
               ScrCmds.statMsg("(VE) Raise Exception: Microsoft Cactus Test Failed!")
            else:
               ScrCmds.raiseException(10578, "Microsoft Cactus Test Failed!")
         
         failLog = []
         ScrCmds.insertHeader("Perform OD Read %s times" %OD_TestLoop,headChar='#')
         for i in range(OD_TestLoop):
            result = self._getTransferRate(i,"OD",2,(OD_StartLBA+i*testCap), testCap, 256, 'read', readOdLowLimit, readOdUpLimit)
            if (result[0]): failLog.append([i + 1, 'ReadOD'] + result[1])
         
         if len(failLog) > 0:
            self._printFailLog(failLog)
            if testSwitch.virtualRun:
               ScrCmds.statMsg("(VE) Raise Exception: Microsoft Cactus Test Failed!")
            else:
               ScrCmds.raiseException(10578, "Microsoft Cactus Test Failed!")
      
      ID_TestLoop = TP.prm_microsoft_Cactus.get('ID_LOOP', 15)        
      ID_StartLBA = (TP.prm_microsoft_Cactus.get('ID_StartLBA', 820)*10*testCap)         
      if ID_TestLoop:
         failLog = []
         ScrCmds.insertHeader("Perform ID Write %s times" %ID_TestLoop,headChar='#')
         for i in range(ID_TestLoop):
            result = self._getTransferRate(i,"ID",1,(ID_StartLBA+i*testCap), testCap, 256, 'write', writeIdLowLimit, writeIdUpLimit)
            if (result[0]): failLog.append([i + 1, 'WriteID'] + result[1])
         if len(failLog) > 0:
            self._printFailLog(failLog)
            if testSwitch.virtualRun:
               ScrCmds.statMsg("(VE) Raise Exception: Microsoft Cactus Test Failed!")
            else:
               ScrCmds.raiseException(10578, "Microsoft Cactus  Test Failed!")

         failLog = []
         ScrCmds.insertHeader("Perform ID Read %s times" %ID_TestLoop,headChar='#')
         for i in range(ID_TestLoop):

            result = self._getTransferRate(i,"ID",2,(ID_StartLBA+i*testCap), testCap, 256, 'read', readIdLowLimit, readIdUpLimit)
            if (result[0]): failLog.append([i + 1, 'ReadID'] + result[1])
         if len(failLog) > 0:
            self._printFailLog(failLog)
            if testSwitch.virtualRun:
               ScrCmds.statMsg("(VE) Raise Exception: Microsoft Cactus Test Failed!")
            else:
               ScrCmds.raiseException(10578, "Microsoft Cactus Test Failed!")

      #DBlog Output
      try:
         self.DBLOutput = []       
         for loopcnt,item in self.DBLogData.items(): 
            self.DBLOutput.append([loopcnt*2+1, item[1]['OD'][:3] + item[2]['OD'][2:]]) #Write/Read 'OD'
            self.DBLOutput.append([loopcnt*2+2, item[1]['ID'][:3] + item[2]['ID'][2:]]) #Write/Read 'ID'
         self._makeDBLOutput()            
      except: pass    
      
      objPwrCtrl.powerCycle(5000, 12000, 10, 30)
      

###########################################################################################################
###########################################################################################################
class CAPPLEATI(CState):
   """
      Description: Class that will 10 minutes of random read/write testing.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      from Drive import objDut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = objDut


   #-------------------------------------------------------------------------------------------------------
   def SPAppleSMART(self):
      ScriptComment('=====================  SP Display and Check SMART     ===========================')
      if not testSwitch.BYPASS_N2_CMD: #/1N2 cmd not ready yet
         sptCmds.sendDiagCmd('/1N2', printResult = True)  #Update SMART  

      CriticalEventLogData = sptCmds.sendDiagCmd('/1N5', printResult = True)
      if testSwitch.virtualRun:
         CriticalEventLogData = \
            """
            Att
            Num  Flgs normlzd worst raw
             1   000F   64     64   00000000005000
             3   0003   63     63   00000000000000
             4   0032   64     64   0000000000001F
             5   0033   64     64   00000000000000
             7   000F   64     FD   0000000000033B
             9   0032   64     64   2A9C4200000000
             A   0013   64     64   00000000000000
             C   0032   64     64   0000000000001D
            B8   0032   64     64   00000000000000
            BB   0032   64     64   00000000000000
            BC   0032   64     64   00000000000000
            BD   003A   64     64   00000000000000
            BE   0022   4D     46   00000017150017
            BF   0032   64     64   00000000000000
            C0   0032   64     64   0000000000000C
            C1   0032   64     64   00000000000024
            C2   0022   17     28   00001500000017
            C5   0012   64     64   00000000000000
            C6   0010   64     64   00000000000000
            C7   003E   C8     C8   00000000000000
            F0   0000   64     64   14EF7700000000
            F1   0000   64     FD   00000003A8C800
            F2   0000   64     FD   00000003A80000
            FE   0032   64     64   00000000000000
             0   0000    0      0   00000000000000
             0   0000    0      0   00000000000000
             0   0000    0      0   00000000000000
             0   0000    0      0   00000000000000
             0   0000    0      0   00000000000000
             0   0000    0      0   00000000000000
             """

      CELogAttrs = self.oSerial.parseCEAttributes(CriticalEventLogData)
      #objMsg.printMsg('CELogAttrs=%s' % (`CELogAttrs`))

      CE05 = CELogAttrs['5']['raw'] & 0xFFFF #Smart attribute #5 (bytes[1:0]) -> G-List Entry
      CEC5 = CELogAttrs['C5']['raw'] & 0xFFFF #Smart attribute #197 (bytes[1:0]) -> P-List Entry
      CEC6 = CELogAttrs['C6']['raw'] & 0xFFFF

      objMsg.printMsg('Smart attribute 05, C5, C6 = %s %s %s' % (CE05, CEC5, CEC6))
      if CE05 or CEC5 or CEC6:
         objMsg.printMsg("SP Non zero value in the Cum Retired Sector counts or the Cum Pending Spare counts in the SMART Attribute")
         ScrCmds.raiseException(14553,"SP EXCEEDS_DRIVE_GLIST_LIMIT.")

   #-------------------------------------------------------------------------------------------------------
   def SPAppleATI(self):
      # serial port Apple ATI test, leveraged from SPMQM GIO.py doODTATI()
      objMsg.printMsg("Begin to run SP ATI test for Apple")
      from serialScreen import sptDiagCmds
      self.oSerial = sptDiagCmds()
      sptCmds.enableDiags()
      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)

      objMsg.printMsg("*****************Write last 2% capacity at ID********************")
      ICmd.ClearBinBuff()
      ICmd.FillBuffer(WBF, 0, '0000')
      start_lba = int(maxLBA*0.98)
      cmdLoop = 1
      if testSwitch.SMRPRODUCT:
         # use larger blocks per transfer, since SMR write in bands
         objMsg.printMsg("Use larger blocks per transfer to reduce test time, since SMR write in bands")
         data = ICmd.SequentialCmdLoop(0x35, start_lba, maxLBA, 0xFFFF, 0xFFFF, cmdLoop)
      else:
         data = ICmd.SequentialCmdLoop(0x35, start_lba, maxLBA, 1024, 1024, cmdLoop)
      objMsg.printMsg('data=%s' % str(data))
      if data['LLRET'] != OK:
         ScrCmds.raiseException(12657,"Seq DMA Write Test FAIL")

      self.SPAppleSMART()

      objMsg.printMsg("*****************Write 500K last 1% 1024 sector at ID*************************")
      ICmd.ClearBinBuff()
      ICmd.FillBuffer(WBF, 0, '0000')
      start_lba = int(maxLBA*0.99)

      cmdLoop = 500000
      if ConfigVars[CN]['BenchTop']:
         cmdLoop = cmdLoop/100
         objMsg.printMsg('benchtop cmdLoop=%s' % cmdLoop)

      if testSwitch.SMR:
         # ATI capability at slim track can be as low as 50 according to RSS.
         cmdLoop = 50
         objMsg.printMsg('ATI capability at slim track without DOS, cmdLoop=%s' % cmdLoop)
      data = ICmd.SequentialCmdLoop(0x35, start_lba, start_lba+1024, 1024, 1024, cmdLoop)
      objMsg.printMsg('data=%s' % str(data))
      if data['LLRET'] != OK:
         ScrCmds.raiseException(12657,"Seq DMA Write Test FAIL")

      self.SPAppleSMART()

      objMsg.printMsg("*****************Read last 3% capacity at ID********************")
      start_lba = int(maxLBA*0.97)     # read 1% more to verify written sectors
      data =ICmd.SequentialReadDMAExt(start_lba, maxLBA, 1024, 1024)
      if data['LLRET'] != OK:
         ScrCmds.raiseException(12656,"Seq DMA Read Test FAIL")

      self.SPAppleSMART()

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.NoIO:
         return self.SPAppleATI()

      objMsg.printMsg("Begin to run ATI test for Apple")

      oProc = CProcess()
      objPwrCtrl.powerCycle(5000,12000,10,10)
      ICmd.HardReset()  #issue hard reset to try to get drive to run
      try:
          oProc.St(TP.prm_638_Unlock_Seagate) # Unlock Seagate Access
      except:
          objPwrCtrl.powerCycle(5000,12000,10,10)
          oProc.St(TP.prm_638_Unlock_Seagate) # Unlock Seagate Access

      maxLBA = self.dut.IdDevice["Max LBA Ext"]
      objMsg.printMsg("*****************Write last 2% capacity at ID********************")
      result = ICmd.SetFeatures(0x82)['LLRET']
      if result == 0:
          objMsg.printMsg('Disable write cache Passed')
      else:
          objMsg.printMsg('Disable write cache Failed')
          ScrCmds.raiseException(14825, "Disable write cache Failed")
      ICmd.MakeAlternateBuffer(0x01, 1024)
      try:
          ICmd.ClearBinBuff(WBF)
          start_lba = int(maxLBA*0.98)
          data =ICmd.SequentialWriteDMAExt(start_lba, maxLBA, 1024, 1024, 0, 0)
          if data['LLRET'] != OK:
              objMsg.printMsg('return value is %s' % str(data))
              ScrCmds.raiseException(12657,"Seq DMA Write Test FAIL")
          ICmd.ClearBinBuff(WBF)
      finally:
          ICmd.RestorePrimaryBuffer(0x01)
      ICmd.SetFeatures(0x02)
          
      ScriptComment('=====================  Display and Check SMART     ===========================')
      oProc.St(TP.prm_538) # Read SMART sector
      oProc.St(TP.prm_508_Buff,CTRL_WORD1=(0X0005),BYTE_OFFSET=(0,0))        # Display read buff
      fG2P = 0
      for offset in range(2,362,12):
         if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:
            oProc.St(TP.prm_508_Buff,CTRL_WORD1=(0X8005),BYTE_OFFSET=(0,offset),BUFFER_LENGTH = (0,1))   #
            smartAttribID = DriveVars["Buffer Data"]
         elif objRimType.IOInitRiser() or (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()):
            data = ICmd.GetBuffer(RBF,offset,1)['DATA']
            smartAttribID = "%02X" % ord(data)
         objMsg.printMsg('smartAttribID: %s' %str(smartAttribID))

         if smartAttribID in ['05','C6','C5',]:
             if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:
                oProc.St(TP.prm_508_Buff,CTRL_WORD1=(0X8005),BYTE_OFFSET=(0,offset+5),BUFFER_LENGTH = (0,2))   #
                spareCount = DriveVars["Buffer Data"]
             elif objRimType.IOInitRiser() or (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()):
                data = ICmd.GetBuffer(RBF,offset+5,2)['DATA']
                spareCount = ''
                for i in data:
                  spareCount = spareCount + "%02X" % ord(i)
             objMsg.printMsg('spareCount: %s' %str(spareCount))

             if spareCount!= '0000':
                 objMsg.printMsg("Non zero value in the Cum Retired Sector counts or the Cum Pending Spare counts in the SMART Attribute")
                 ScrCmds.raiseException(14553,"EXCEEDS_DRIVE_GLIST_LIMIT.")


      objMsg.printMsg("*****************Write 500K last 1% 1024 sector at ID*************************")
      result = ICmd.SetFeatures(0x82)['LLRET']
      if result == 0:
          objMsg.printMsg('Disable write cache Passed')
      else:
          objMsg.printMsg('Disable write cache Failed')
          ScrCmds.raiseException(14825, "Disable write cache Failed")
      ICmd.MakeAlternateBuffer(0x01, 1024)
      try:
          ICmd.ClearBinBuff(WBF)
          start_lba = int(maxLBA*0.99)
          if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:
            data =ICmd.SequentialCmdLoop(0x35,start_lba, start_lba+1023,1024,1024,500000)
          elif objRimType.IOInitRiser() or (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()):
            data =ICmd.SequentialWriteDMAExt(start_lba, start_lba+1023,1024,1024,LOOP_COUNT=500000)
          if data['LLRET'] != OK:
              objMsg.printMsg('return value is %s' % str(data))
              ScrCmds.raiseException(12657,"Seq DMA Write Test FAIL")
          ICmd.ClearBinBuff(WBF)
      finally:
          ICmd.RestorePrimaryBuffer(0x01)
      ICmd.SetFeatures(0x02)

      objMsg.printMsg("*****************Read last 2% capacity at ID********************")
      ICmd.MakeAlternateBuffer(0x02, 1024)
      ICmd.ClearBinBuff(RBF)
      start_lba = int(maxLBA*0.98)
      data =ICmd.SequentialReadDMAExt(start_lba, maxLBA, 1024, 1024, 0, 0)
      if data['LLRET'] != OK:
          objMsg.printMsg('return value is %s' % str(data))
          ScrCmds.raiseException(12656,"Seq DMA Read Test FAIL")
      ICmd.RestorePrimaryBuffer(0x02)
     
      ScriptComment('=====================  Display and Check SMART     ===========================')
      oProc.St(TP.prm_538) # Read SMART sector
      oProc.St(TP.prm_508_Buff,CTRL_WORD1=(0X0005),BYTE_OFFSET=(0,0))        # Display read buff
      fG2P = 0
      for offset in range(2,362,12):
         if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:
            oProc.St(TP.prm_508_Buff,CTRL_WORD1=(0X8005),BYTE_OFFSET=(0,offset),BUFFER_LENGTH = (0,1))   #
            smartAttribID = DriveVars["Buffer Data"]
         elif objRimType.IOInitRiser() or (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()):
            data = ICmd.GetBuffer(RBF,offset,1)['DATA']
            smartAttribID = "%02X" % ord(data)
         objMsg.printMsg('smartAttribID: %s' %str(smartAttribID))

         if smartAttribID in ['05','C6','C5',]:
             if objRimType.CPCRiser() and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION:
                oProc.St(TP.prm_508_Buff,CTRL_WORD1=(0X8005),BYTE_OFFSET=(0,offset+5),BUFFER_LENGTH = (0,2))   #
                spareCount = DriveVars["Buffer Data"]
             elif objRimType.IOInitRiser() or (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()):
                data = ICmd.GetBuffer(RBF,offset+5,2)['DATA']
                spareCount = ''
                for i in data:
                  spareCount = spareCount + "%02X" % ord(i)
             objMsg.printMsg('spareCount: %s' %str(spareCount))

             if spareCount!= '0000':
                 objMsg.printMsg("Non zero value in the Cum Retired Sector counts or the Cum Pending Spare counts in the SMART Attribute")
                 ScrCmds.raiseException(14553,"EXCEEDS_DRIVE_GLIST_LIMIT.")

      ScriptComment('Pass Apple ATI Test')
################################################################################################################
###########################################################################################################
class CHPMeatGrinderScreen(CState):

   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oProc = CProcess()
      objPwrCtrl.powerCycle(5000,12000,10,30)
      ICmd.HardReset()

      oProc.St({'test_num':535},0)
      oProc.St({'test_num':533}, CTRL_WORD1 = 0x0001)              #  RESET
      oProc.St({'test_num':514}, CTRL_WORD1 = 1)

      """
      res = ICmd.ReceiveSerialCtrl(1)
      result = ICmd.SetFeatures(0x82,0x00)         ###### disable write cache ########
      if result['LLRET'] == OK:
         objMsg.printMsg("Write Cache disabled")
      else:
         objMsg.printMsg("Warning : Disable Write Cache Failed")

      res = ICmd.ReceiveSerialCtrl(0,100)
      objMsg.printMsg("Buffer data received from Disable Write Cache : \n\n %s"%res)
      """

      SetFailSafe()  # MLW dont want it to fail for now
      try:

         oProc.St(TP.T508_0000FFFF)  # Write pattern to the write buffer - fixed pattern 0000FFFF
         oProc.St(TP.T508_2)         # read and display write buffer
         #res = ICmd.ReceiveSerialCtrl(1)
         #result = ICmd.SetFeatures(0x82,0x00)         ###### MLW disable write cache ########
         #if result['LLRET'] == OK:
         #   objMsg.printMsg("Write Cache disabled")
         #else:
         #   objMsg.printMsg("Warning : Disable Write Cache Failed")
         #res = ICmd.ReceiveSerialCtrl(0,100)
         #objMsg.printMsg("Buffer data received from Disable Write Cache : \n\n %s"%res)
         oProc.St({'test_num':597}, spc_id = 1, timeout = 90000,  RANDOM_SEED = 620, MAXIMUM_LBA = (0, 0, 0, 0), MINIMUM_LBA = (0, 0, 0, 0),MIN_SECTOR_COUNT = 1, MAX_SECTOR_COUNT = 1, LOOP_COUNT = 0x4000, CTRL_WORD1 = 0x22, CTRL_WORD2 = 0)
         oProc.St({'test_num':508}, CTRL_WORD1 = 0, PATTERN_TYPE = 1)
         oProc.St(TP.T508_2)         # read and display write buffer
         oProc.St({'test_num':597}, spc_id = 1, timeout = 90000,  RANDOM_SEED = 620, MAXIMUM_LBA = (0, 0, 0, 0), MINIMUM_LBA = (0, 0, 0, 0),MIN_SECTOR_COUNT = 1, MAX_SECTOR_COUNT = 1, LOOP_COUNT = 0x4000, CTRL_WORD1 = 0x22, CTRL_WORD2 = 0)
         oProc.St(TP.T508_0000FFFF)  # Write pattern to the write buffer - fixed pattern 0000FFFF
         oProc.St(TP.T508_2)         # read and display write buffer
         oProc.St({'test_num':597}, spc_id = 1, timeout = 90000,  RANDOM_SEED = 620, MAXIMUM_LBA = (0, 0, 0, 0), MINIMUM_LBA = (0, 0, 0, 0),MIN_SECTOR_COUNT = 1, MAX_SECTOR_COUNT = 1, LOOP_COUNT = 0x4000, CTRL_WORD1 = 0x42, CTRL_WORD2 = 0)

      except:
         oProc.St({'test_num':504}, timeout = 3600)

      ClearFailSafe()  # dont want to fail for now, clearing...
####################################################################################
###########################################################################################################
class CNETAPP(CState):
   """
      NetApp
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProcess = CProcess()
      from serialScreen import sptDiagCmds
      self.oSerial = sptDiagCmds()
      self.oUtility = CUtility()

      self.DEBUG = 0

      if self.dut.driveattr.get('NETAPP_V3','NONE') != 'PASS' :
         self.getBasicDriveInfo()
         #temp 25
         self.dut.driveattr['NETAPP_V3'] = 'FAIL'
         self.PowerCycleTest()
         self.Intialization()

         ret = CIdentifyDevice().ID
         self.max_LLB = ret['IDDefaultLBAs'] - 1 # default for 28-bit LBA

         if ret['IDCommandSet5'] & 0x400:      # check bit 10
            objMsg.printMsg('Get ID Data 48 bit LBA is supported')
            self.max_LLB = ret['IDDefault48bitLBAs'] - 1

         if self.DEBUG:
            objMsg.printMsg('CIdentifyDevice data : %s' %str(ret))

         if self.max_LLB <= 0:
            self.max_LLB = 976773167
            objMsg.printMsg("Assign max_LLB to default : %d", self.max_LLB)

         objMsg.printMsg("The Maximum User LBA is : %08X       Drive Capacity - %dGB" %(self.max_LLB,(( self.max_LLB * 512 )/1000000000),))

         self.SeekTest_CHS()
         self.StaticDataCompareTest()

         self.DataCompareSIOPTest()

         self.ButterflyWriteTest()

#        #temp 20
#        self.ButterflyWriteTest();
#
#        #temp 10
#        self.ButterflyWriteTest();

         self.SystemReadyTest(3);

         self.StaticDataCompareTest()

         self.DataCompareSIOPTest()

         self.BandSeqRWCmpTest()

         self.StressedPinchTest()

         #temp 15
         self.DataCompareSIOPTest(caching = True)

         #temp 20
         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')

         #temp 25
         self.PowerCycleTest()
         self.Intialization()

         self.ButterflyWriteTest()

#        #temp 30
#        self.ButterflyWriteTest();
#
#        #temp 35
#        self.ButterflyWriteTest();

         #temp 40
         self.PowerCycleTest()
         self.Intialization()

         self.BandSeqRWCmpTest()

         self.DataErasureTest()

         self.SystemReadyTest(3)

         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')

         self.DataErasureTest2_CHS()

         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')

         self.PowerCycleTest()
         self.Intialization()

         #temp 40
         self.StressedPinchTest()

         #temp 35
         self.StaticDataCompareTest()

         #temp 31.66
         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')

         #temp 25
         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')

         self.DataErasureTest()

         self.BandSeqRWCmpTest()


         self.PowerCycleTest()
         self.Intialization()

#        self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')

         self.DataErasureTest2_CHS()

         self.StaticDataCompareTest()

         #temp 21.66
         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')

         #temp 15
         self.AdjacentPinch_CHS()

         #temp 10
         self.DataErasureTest()

         self.PowerCycleTest()
         self.Intialization()

#        self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')

         self.DataErasureTest2_CHS()

         self.PowerCycleTest()
         self.Intialization()

         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')

         self.SeekTest_CHS()

         self.ButterflyWriteTest()

#        #temp 15
#        self.ButterflyWriteTest();
#
#        #temp 20
#        self.ButterflyWriteTest();

         #temp 25
         self.DataCompareSIOPTest()

         #temp 30
         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')

         #temp 35
         self.AdjacentPinch_CHS()

         #temp 40
         self.SeekTest_CHS()

         self.StaticDataCompareTest()

         self.DataCompareSIOPTest()

         self.PowerCycleTest()
         self.Intialization()

         self.VerifyDiskTest()

         self.ButterflyWriteTest()

#        #temp 35
#        self.ButterflyWriteTest();
#
#        #temp 30
#        self.ButterflyWriteTest();

         #temp 25
         self.PowerCycleTest()
         self.Intialization()

         self.ZeroDisk()

         #SMART DST Long
         ICmd.LongDST()

         self.dut.driveattr['NETAPP_V3'] = 'PASS'

   def PowerCycleTest(self):
      ScrCmds.insertHeader('Power Cycle')
      objPwrCtrl.powerCycle(offTime=20, onTime=35, ataReadyCheck = True)

   def Intialization(self):
      ScrCmds.insertHeader("Unlock Seagate")
      try:
         ICmd.UnlockFactoryCmds()
      except:
         self.PowerCycleTest()

   def SeekTest_CHS(self,):
      #Now we don't put any spec in this test
      ScrCmds.insertHeader('NetApp : Full Seek test : BEGIN')
      sptCmds.enableDiags()
      starttime = time.time()

      seekType = int(TP.netapp_seekTest['seek_type'])
      loop_Seek = int(TP.netapp_seekTest['loop_Seek'])
      loop_Test = int(TP.netapp_seekTest['loop_Test'])

      objMsg.printMsg('SeekTest : seek_type : %d' % seekType)
      objMsg.printMsg('SeekTest : loop_Test : %d' % loop_Test)

      if testSwitch.virtualRun:
         loop_Seek  = 1;

      for i in range(loop_Test):
         for cur_hd in range(self.dut.imaxHead):
            objMsg.printMsg('NetApp Full Stroke Seek Head : %d' % cur_hd)
            sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                         #Set Test Space
            self.oSerial.gotoLevel('2')
            sptCmds.sendDiagCmd('S0,%x' % cur_hd,timeout = 30, printResult = False, raiseException = 0, stopOnError = False)              #Seek to test head
            self.oSerial.gotoLevel('3')
            sptCmds.sendDiagCmd('D999999999,2,5000',timeout = 300, printResult = True, raiseException = 0, stopOnError = False)    #Perform full strok seek

            objMsg.printMsg('NetApp Random Seek Head : %d' % cur_hd)
            sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                         #Set Test Space
            self.oSerial.gotoLevel('2')
            sptCmds.sendDiagCmd('S0,%x'% cur_hd,timeout = 30, printResult = False, raiseException = 0, stopOnError = False)              #Seek to test head
            self.oSerial.gotoLevel('3')
            sptCmds.sendDiagCmd('D0,%x,%x'%(seekType,loop_Seek),timeout = 300, printResult = True, raiseException = 0, stopOnError = False)            #Perform random seek

            if(self.DEBUG):
               objMsg.printMsg('SeekTest Head : %d, Time : %d' % (cur_hd, (time.time() - starttime)))

      total_time = time.time() - starttime
      sptCmds.enableESLIP()
      ScrCmds.insertHeader('Full Seek test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Full Seek test : END')

   def StaticDataCompareTest(self):
      ScrCmds.insertHeader('NetApp : Static Data Compare Test using DRAM Screen : BEGIN')
      starttime = time.time()

      TP.prm_DRamSettings.update({"StartLBA":0})                       #Target Write LBA : Start
      TP.prm_DRamSettings.update({"EndLBA":32})                        #Target Write LBA : End
      TP.prm_DRamSettings.update({"StepCount":32})                     #StepCount : 32LBA
      TP.prm_DRamSettings.update({"SectorCount":32})                   #SectorCount: 32LBA
      from DRamScreen import CDRamScreenTest
      oDRamScreen = CDRamScreenTest(self.dut)

      loop_Count = int(TP.netapp_staticDataCompare['loop_Count'])
      delay_time = int(TP.netapp_staticDataCompare['delay_time'])

      if testSwitch.virtualRun:
         loop_Count = 10
         delay_time = 0

      if(self.DEBUG):
         objMsg.printMsg('StaticDataCompareTest : loop_Count %d' % loop_Count)

      for i in range(loop_Count):
         oDRamScreen.dRamScreenTest()

         time.sleep(delay_time)

         if(self.DEBUG):
            objMsg.printMsg('StaticDataCompareTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Static Data Compare Test using DRAM Screen Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Static Data Compare Test using DRAM Screen : END')

   def ButterflyWriteTest(self):
      ScrCmds.insertHeader('NetApp : Butterfly Write Test : BEGIN')
      starttime = time.time()

      loop_count = loop_Count = int(TP.netapp_butterflyWriteTest['loop_Count'])
      step_rate = TP.netapp_butterflyWriteTest['step_rate']
      lba_size = TP.netapp_butterflyWriteTest['lba_size']
      run_time = int(TP.netapp_butterflyWriteTest['run_time']/ 4 * self.dut.imaxHead)

      block_size = 1024*32/lba_size
      (block_size_MSBs, block_size_LSBs) = self.UpperLower(block_size)

      objMsg.printMsg('loop_count : %d' %loop_count)
      objMsg.printMsg('step_rate : %d' %step_rate)
      objMsg.printMsg('run_time : %d Mins' %(run_time / 60))

      prm_506_SET_RUNTIME = {
         'test_num'          : 506,
         'prm_name'          : "prm_506_SET_RUNTIME",
         'spc_id'            :  1,
         "TEST_RUN_TIME"     :  run_time,
      }
      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         prm_510_BUTTERFLY = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_BUTTERFLY",
            'spc_id'            :  1,
            "CTRL_WORD1"        : (0x0422),                                        #Butterfly Sequencetioal Write;Display Location of errors
            "STARTING_LBA"      : (0,0,0,0),
            "BLKS_PER_XFR"      : (step_rate * block_size),                        #Need 32K write and seek 5*32K step, but cannot do that only write 5*32K.
            "OPTIONS"           : 0,                                               #Butterfly Converging
            "timeout"           :  3000,                                           #15 Mins Test Time
         }
      else:
         prm_510_BUTTERFLY = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_BUTTERFLY",
            'spc_id'            :  1,
            "CTRL_WORD1"        : (0x0422),                                        #Butterfly Sequencetioal Write;Display Location of errors
            "STARTING_LBA"      : (0,0,0,0),
            "BLKS_PER_XFR"      : (step_rate * block_size),                        #Need 32K write and seek 5*32K step, but cannot do that only write 5*32K.
            "OPTIONS"           : 0,                                               #Butterfly Converging
            "retryECList"       : [14016,14029],
            "retryMode"         : POWER_CYCLE_RETRY,
            "retryCount"        : 2,
            "timeout"           :  3000,                                           #15 Mins Test Time
         }

      numGB = (self.max_LLB * lba_size ) / (10**9)
      ScriptComment("The Maximum LBA is : %08X Drive Capacity - %dGB" %(self.max_LLB, numGB,))

      (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0) = self.oUtility.returnStartLbaWords(self.max_LLB - 1)

      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         for i in xrange(loop_count):
            failed = 1
            retry = 0
            while failed == 1 and retry <= TP.maxRetries_T510Butterfly:
               try:
                  self.oProcess.St(
                        prm_506_SET_RUNTIME,
                     )

                  self.oProcess.St(
                        prm_510_BUTTERFLY,
                        STARTING_LBA = (0, 0, 0, 0),
                        MAXIMUM_LBA  = (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0),
                     )
                  failed = 0

                  self.oProcess.St(
                        prm_506_SET_RUNTIME,TEST_RUN_TIME = 0,
                     )
               except ScriptTestFailure, (failureData):
                  ec = failureData[0][2]
                  if ec in [14016, 14029] and retry < TP.maxRetries_T510Butterfly:
                     objPwrCtrl.powerCycle(5000,12000,10,30)
                     retry += 1
                  else:
                     raise

            if(self.DEBUG):
               objMsg.printMsg('ButterflyWriteTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))
      else:
         for i in xrange(loop_count):
            self.oProcess.St(
                   prm_506_SET_RUNTIME,
                )

            self.oProcess.St(
                   prm_510_BUTTERFLY,
                   STARTING_LBA = (0, 0, 0, 0),
                   MAXIMUM_LBA  = (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0),
                )

            self.oProcess.St(
                   prm_506_SET_RUNTIME,TEST_RUN_TIME = 0,
                )

            if(self.DEBUG):
               objMsg.printMsg('ButterflyWriteTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Butterfly Write Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Butterfly Write Test : END')

   def UpperLower(self, FourByteNum):
      FourByteNum = FourByteNum & 0xFFFFFFFF                                   #chop off any more than 4 bytes
      MSBs = FourByteNum >> 16
      LSBs = FourByteNum & 0xFFFF
      return (MSBs, LSBs)

   def SystemReadyTest(self, power_cycle_count = 3):
      ScrCmds.insertHeader('NetApp : System Ready Test : BEGIN')
      starttime = time.time()

      for i in range(1,power_cycle_count +1):
         objMsg.printMsg("Power Cycle %d"% i)
         self.PowerCycleTest();

         time.sleep(90)

      total_time = time.time() - starttime
      ScrCmds.insertHeader('System Ready Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : System Ready Test : END')

   def ZeroDisk(self):
      ScrCmds.insertHeader('NetApp : Zero Disk Test : BEGIN')
      starttime = time.time()

      stepLBA = sctCnt = 256 # 48bit LBA addressing

      result = ICmd.ClearBinBuff(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, " Failed to fill buffer for zero write : %s" % str(result))

      SATA_SetFeatures.enable_WriteCache()

      objMsg.printMsg('Start Full Pack Zero Write')

      if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
         ICmd.St(TP.prm_638_Unlock_Seagate)
         ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialWrite',CTRL_WORD1=(0x22))
      else:
         result = ICmd.SequentialWriteDMAExt(0, self.max_LLB, stepLBA, sctCnt)
         objMsg.printMsg('Full Pack Zero Write - Result %s' %str(result))

         if result['LLRET'] != 0:
            ScrCmds.raiseException(10888, "Full Pack Zero Write Failed: %s" %str(result))

      ICmd.FlushCache()

      total_time = time.time() - starttime

      objPwrCtrl.powerCycle(offTime=20, onTime=35, ataReadyCheck = True)

      ScrCmds.insertHeader('Zero Disk Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Zero Disk Test : END')

   def VerifyDiskTest(self):
      ScrCmds.insertHeader('NetApp : Verify Disk Test : BEGIN')
      stepLBA = sctCnt = 256 # 48bit LBA addressing
      starttime = time.time()

      if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
         ICmd.St(TP.prm_638_Unlock_Seagate)
         ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialRead')
      else:
         result = ICmd.SequentialReadDMAExt(0, self.max_LLB, stepLBA, sctCnt)
         objMsg.printMsg('Full Pack Read - Result %s' %str(result))

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,"Full Pack Zero Read Failed : %s" %str(result))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Verify Disk Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : System Ready Test : END')

   def DataCompareSIOPTest(self, caching = False):
      ScrCmds.insertHeader('NetApp : Data Compare SIOP Test : BEGIN')
      starttime = time.time()

      if caching == False:
         #result = ICmd.SetFeatures(0x82) #diable write cache
         SATA_SetFeatures.disable_WriteCache()
         objMsg.printMsg('disable write cache')
         #if result['LLRET'] != OK:
         #   ScrCmds.raiseException(10888, "Failed Disable Write Cache Data : %s" %str(result))

      import random
      loop_count = loop_Count = int(TP.netapp_dataCompareSIOPTest['loop_Count'])
      stepLBA = sctCnt =TP.netapp_dataCompareSIOPTest['sector_count']
      delay_time = int(TP.netapp_staticDataCompare['delay_time'])

      lba_size = 512
      loop_Count = int(float(loop_Count) / 4 * self.dut.imaxHead)

      objMsg.printMsg('loop_count : %d' %loop_count)
      objMsg.printMsg('sector_count : %d' %sctCnt)
      objMsg.printMsg('delay_time : %d' %delay_time)

      if testSwitch.virtualRun:
         loop_count = 10
         delay_time = 0

      for i in range(loop_count):
         position_A = random.randrange(0, self.max_LLB - sctCnt)                    #Random A location
         position_B = random.randrange(0, self.max_LLB - sctCnt)                    #Random B location

         if i == 4000 or i == 0:                                               #Random new Data every 4000 loops
            objMsg.printMsg('Fill Random pattern at loop : %d' % (i))
            self.fillRandomBuff()

         result = ICmd.WriteSectors(position_A, sctCnt)                        #Write A

         if self.DEBUG:
            objMsg.printMsg('WriteSectors A: %s' %str(result))

         if result['LLRET'] != 0:
            ScrCmds.raiseException(10888, "Write data A error: %s" %str(result))

         result = ICmd.WriteSectors(position_B, sctCnt)                        #Write B

         if self.DEBUG:
            objMsg.printMsg('WriteSectors B: %s' %str(result))

         if result['LLRET'] != 0:
            ScrCmds.raiseException(10888, "Write data B error : %s" %str(result))

         result = ICmd.ReadSectors(position_A, sctCnt)                         #Read Sector A
         if self.DEBUG:
            objMsg.printMsg('Read A : %s' %str(result))

         if result['LLRET'] == OK:
            result = ICmd.CompareBuffers(0, sctCnt * lba_size)                 #Compare Buffer
            if self.DEBUG:
               objMsg.printMsg('CompareBuffers A result : %s' %str(result))
         else:
            ScrCmds.raiseException(10888,"Compare buffer Failed : %s" %str(result))

         if result['LLRET'] == OK:
            result = ICmd.GetBuffer(RBF, 0,  sctCnt * lba_size)                 #Get Read Buffer
            if self.DEBUG:
               objMsg.printMsg('GetBuffer A result : %s' %str(result))
         else:
            ScrCmds.raiseException(10888,"Get Buffer Failed: %s" %str(result))

         if result['LLRET'] == OK:
            result = ICmd.ReadVerifySects(position_A, sctCnt)                   #Read Verify Sector
            if self.DEBUG:
               objMsg.printMsg('ReadVerifySects A result : %s' %str(result))
         else:
            ScrCmds.raiseException(10888,"Read Verify Sectors A Failed : %s" %str(result))

         result = ICmd.ReadSectors(position_B, sctCnt)                          #Read Sector
         if self.DEBUG:
            objMsg.printMsg('Read B : %s' %str(result))

         if result['LLRET'] == OK:
            result = ICmd.CompareBuffers(0,  sctCnt * lba_size)                 #Compare Buffer
            if self.DEBUG:
               objMsg.printMsg('CompareBuffers B result : %s' %str(result))
         else:
            ScrCmds.raiseException(10888,"Compare buffer Failed : %s" %str(result))

         if result['LLRET'] == OK:
            result = ICmd.GetBuffer(RBF, 0, sctCnt * lba_size)                  #Get Read Buffer
            if self.DEBUG:
               objMsg.printMsg('GetBuffer B result : %s' %str(result))
         else:
            ScrCmds.raiseException(10888,"Get Buffer Failed : %s" %str(result))

         if result['LLRET'] == OK:
            result = ICmd.ReadVerifySects(position_B, sctCnt)                   #Read Verify Sector
            if self.DEBUG:
               objMsg.printMsg('ReadVerifySects B result : %s' %str(result))
         else:
            ScrCmds.raiseException(10888,"Read Verify Sectors B Failed: %s" %str(result))

         if not testSwitch.virtualRun:
            ScriptPause(delay_time)

         if(self.DEBUG):
            objMsg.printMsg('DataCompareSIOPTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

      if caching == False:
         result = ICmd.SetFeatures(0x02) #re-enable write cache

         if self.DEBUG:
            objMsg.printMsg('Compare result : %s' %str(result))

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,"Failed Enable Write Cache: %s" %str(result))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Data Compare SIOP Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Data Compare SIOP Test : END')

   def BandSeqRWCmpTest(self):
      ScrCmds.insertHeader('NetApp : Banded Sequential Write/Read Compare Test : BEGIN')
      starttime = time.time()

      increasing_step = int(TP.netapp_bandSeqRWCmpTest['increasing_step'])
      pattern_count =TP.netapp_bandSeqRWCmpTest['pattern_count']
      stepLBA =TP.netapp_bandSeqRWCmpTest['stepLBA']
      loop_Count =TP.netapp_bandSeqRWCmpTest['loop_Count']

      increasing_step = ((increasing_step * 4) / self.dut.imaxHead)

      objMsg.printMsg('increasing_step : %d' %increasing_step)
      objMsg.printMsg('pattern_count : %d' %pattern_count)
      objMsg.printMsg('stepLBA : %d' %stepLBA)
      objMsg.printMsg('loop_Count : %d' %loop_Count)

      SATA_SetFeatures.enable_WriteCache()

      if testSwitch.virtualRun:
         loop_Count = 1
         pattern_count = 1

      for iCount in range(loop_Count):
         for pattern in range(int(pattern_count)):
            if pattern == 0 :                                                     #Fill Write Buffer with (Incremental, Shifting bit, Counting,Random )
               self.fillIncrementalBuff()

            if pattern == 1 :
               self.fillShiftingBitBuff()

            if pattern == 2 :
               self.fillCountingBuff()

            if pattern == 3 :
               self.fillRandomBuff()

            blockSize = int((1024 * 1024 * 8) / 512)                                # ~ 8M data size
            sector_count = step_lba = stepLBA                                     #  32K xfer size
            Stamp = 0
            Compare = 0
            test_loop = 1

            count_step = 0
            for i in range(0,100,increasing_step):                                #Increasing about 2% per step
               targetLBA = int(self.max_LLB *(float(increasing_step) / 100) * count_step)              #Write Data Phase
               result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)

               count_step = count_step + 1

               if self.DEBUG:
                  objMsg.printMsg('Write - Step :  %d' % increasing_step)
                  objMsg.printMsg('Write - LBA :  %x' % targetLBA)
                  objMsg.printMsg('Write - Result :  %s' %str(result))

               if result['LLRET'] != OK:
                  objMsg.printMsg('Write - Step :  %d' % increasing_step)
                  objMsg.printMsg('Write - LBA :  %x' % targetLBA)
                  objMsg.printMsg('Write - blockSize :  %x' % blockSize)
                  objMsg.printMsg('Write - step_lba :  %d' % step_lba)
                  objMsg.printMsg('Write - sector_count :  %x' % sector_count)
                  objMsg.printMsg('Write - Loop :  %d' % i)
                  objMsg.printMsg('Write - max_LLB :  %d' % self.max_LLB)
                  ScrCmds.raiseException(10888, "Write Banded Data Failed : %s" %str(result))

            result = ICmd.BufferCopy(RBF,0,WBF,0,512)
            if result['LLRET'] != OK:
               ScrCmds.raiseException(10888,'BufferCopy Failed! : %s' % str(result))

            Compare = 1
            count_step = 0
            for i in range(0,100,increasing_step):                                 #Read Data Phase
               targetLBA = int(self.max_LLB *(float(increasing_step) / 100)* count_step)
               result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)

               count_step = count_step + 1

               if result['LLRET'] != OK:
                  objMsg.printMsg('Read - Step :  %d' % increasing_step)
                  objMsg.printMsg('Read - LBA :  %x' % targetLBA)
                  objMsg.printMsg('Read - blockSize :  %x' % blockSize)
                  objMsg.printMsg('Read - step_lba :  %d' % step_lba)
                  objMsg.printMsg('Read - sector_count :  %x' % sector_count)
                  objMsg.printMsg('Read - Loop :  %d' % i)
                  objMsg.printMsg('Read - max_LLB :  %d' % self.max_LLB)
                  ScrCmds.raiseException(10888, "Read Banded Data Failed : %s" %str(result))

               if self.DEBUG:
                  objMsg.printMsg('Read - Result %s' %str(result))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Banded Sequential Write/Read Compare Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Banded Sequential Write/Read Compare Test : END')

   def StressedPinchTest(self):
      ScrCmds.insertHeader('NetApp : Stressed Pinch Test : BEGIN')
      starttime = time.time()

      loop_Count = TP.netapp_stressedPinchTest['loop_Count']
      write_Loop = TP.netapp_stressedPinchTest['loop_Write']
      stepLBA =TP.netapp_stressedPinchTest['stepLBA']

      objMsg.printMsg('loop_Count : %d' %loop_Count)
      objMsg.printMsg('write_Loop : %d' %write_Loop)
      objMsg.printMsg('stepLBA : %d' %stepLBA)

      SATA_SetFeatures.enable_WriteCache()
      result = ICmd.FillBuffRandom(WBF)                                            #Fill Write Buffer with Random Data
      if result['LLRET'] != OK:
         if self.DEBUG:
            objMsg.printMsg('FillBuffRandom : %s' %str(result))
         ScrCmds.raiseException(11044, "Fill Random Pattern error")

      startLBA = 0;
      C1MB_to_LBA = int((1024 * 1024) / 512)
      C1MB = 1024 * 1024
      block_size = C1MB / 512
      write_Loop = 10

      for loop in range(loop_Count):
         targetLBA = int(self.max_LLB /2)                                            #Write to LBA (Max LBA/2) & verify (Max LBA/2).
         self.WriteRead(targetLBA, block_size, 'WC')

         targetLBA = int(self.max_LLB /2) + block_size                               #Write to LBA (Max LBA/2 + 1024Kb) & verify LBA (Max LBA/2 +1024Kbytes)

         self.WriteRead(targetLBA, block_size, 'WC')

         targetLBA = int(self.max_LLB /2) - block_size                               #Write to LBA (Max LBA/2 ? 1024Kb) & verify LBA (Max LBA/2 -1024Kbytes)
         self.WriteRead(targetLBA, block_size, 'WC')

         for i in range(0,write_Loop):
            targetLBA = int(self.max_LLB / 2 + C1MB_to_LBA)                         #Seek to random LBA in the range [(Max LBA/2 + 1024Kbytes) ? Max LBA]

            result = ICmd.RandomSeekTime(targetLBA, self.max_LLB, 10, seekType = 28, timeout = 600, exc=0)
            if self.DEBUG:
               objMsg.printMsg('RandomSeekTime 2: %s' %str(result))

            if result['LLRET'] != OK:
               ScrCmds.raiseException(11044, "Random Seek Error")

            targetLBA = int(self.max_LLB /2)                                        #Write to LBA (Max LBA/2) & verify (Max LBA/2).
            self.WriteRead(targetLBA, block_size, 'WC')

            targetLBA = int(self.max_LLB / 2)                                       #Seek to random LBA in the range [(Max LBA/2 + 1024Kbytes) ? Max LBA]

            result = ICmd.RandomSeekTime(0, targetLBA, 10, seekType = 28, timeout = 600, exc=0)
            if result['LLRET'] != OK:
               if self.DEBUG:
                  objMsg.printMsg('Read B : %s' %str(result))
               ScrCmds.raiseException(11044, "Random Seek Error")

            targetLBA = int(self.max_LLB /2)                                        #Write to LBA (Max LBA/2) & verify (Max LBA/2).
            self.WriteRead(targetLBA, block_size, 'W')

            targetLBA = int(self.max_LLB /2) + block_size                           #Read LBA (Max LBA/2 + 1024Kb)
            self.WriteRead(targetLBA, block_size, 'R')

            targetLBA = int(self.max_LLB /2) - block_size                           #Read LBA (Max LBA/2 ? 1024Kb)
            self.WriteRead(targetLBA, block_size, 'R')

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Stressed Pinch Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Stressed Pinch Test : END')

   def SimulateWorkLoadSIOPTest(self, mode = 'NONE'):
      ScrCmds.insertHeader('NetApp : Simulate WorkLoad SIOP Test %s : BEGIN' % mode)
      starttime = time.time()

      import random

      lba_size = TP.netapp_simulateWorkLoadSIOPTest['lba_size']
      run_time = TP.netapp_simulateWorkLoadSIOPTest['run_time']

      if testSwitch.virtualRun:
         run_time = 5

      if self.DEBUG:
         objMsg.printMsg('lba_size : %d' %lba_size)
         objMsg.printMsg('run_time : %d' %run_time)

      while(True):
         loop_random = random.randrange(1,100)
         for i in range(loop_random):
            if mode == 'FILE_SERVER':
               random_value = random.random()
               startLBA = 0
               targetLBA = 0
               stepLBA = 0
               lba_count = 0

               if random <= 0.1:                                               #random location
                  startLBA = int(random.randrange(int(self.max_LLB *0.01)), int(self.max_LLB))

               elif random <=(0.1 + 0.3):
                  startLBA = int(random.randrange(int(self.max_LLB *0.3), int(self.max_LLB *0.6)))

               else:
                  startLBA = int(random.randrange(int(self.max_LLB *0), int(self.max_LLB *0.1)))

               random_value = random.random()

               if random <= 0.3:                                               #random transfer size
                  lba_count = int(random.randrange(int(2 * (1024 /lba_size)), int(32 * 1024/ lba_size)))        #2KB - 32Kb

               else:
                  lba_count = int(random.randrange(int(32 * 1024/lba_size),  int(128 * 1024/ lba_size)))      #32KB - 128Kb

               random_value = random.random()

               if random <= 0.2:                                               #random RW mode. Read:Write ratio of 4:1
                  result = ICmd.WriteSectors(startLBA, lba_count)
                  if self.DEBUG:
                     objMsg.printMsg('WriteSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Write Failed %s" % str(result))

               else:
                  result = ICmd.ReadSectors(startLBA, lba_count)
                  if self.DEBUG:
                     objMsg.printMsg('ReadSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Read Failed %s" % str(result))

            elif mode == 'OLTP':

               random_value = random.random()
               startLBA = 0
               targetLBA = 0
               stepLBA = 0
               lba_count = 0

               if random <= 0.2:                                               #random location
                  startLBA = int(random.randrange(int(self.max_LLB *0.01), int(self.max_LLB)))

               elif random <=(0.2 + 0.3):
                  startLBA = int(random.randrange(int(self.max_LLB *0.1), int(self.max_LLB *0.3)))

               else:
                  startLBA = int(random.randrange(int(self.max_LLB * 0.3), int(self.max_LLB *0.6)))

               random_value = random.random()

               if random <= 0.3:                                               #random transfer size
                  lba_count = int(random.randrange( int(4 * 1024/ lba_size),  int(8 * 1024/ lba_size)))        #4KB - 8Kb

               else:
                  lba_count = int(random.randrange( int(1 * 1024/ lba_size),  int(4 * 1024/ lba_size)))          #1KB - 4Kb

               random_value = random.random()

               if random <= 0.2:                                               #random RW mode
                  result = ICmd.WriteSectors(startLBA, lba_count)
                  if self.DEBUG:
                     objMsg.printMsg('WriteSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Write Failed %s" % str(result))

               else:
                  result = ICmd.ReadSectors(startLBA, lba_count)

                  if self.DEBUG:
                     objMsg.printMsg('ReadSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Read Failed %s" % str(result))

         pause_time = random.randrange(1, 10)

         if not testSwitch.virtualRun:
            ScriptPause(pause_time)

         if((time.time() - starttime) > run_time):
            break

         if(self.DEBUG):
            objMsg.printMsg('SimulateWorkLoadSIOPTestt random %s Loop : %d, Time : %d' % (mode,i, (time.time() - starttime)))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Simulate WorkLoad SIOP  %s Time Usage : %d' % (mode, total_time))
      ScrCmds.insertHeader('NetApp : Simulate WorkLoad SIOP Test %s : END' % mode)

   def DataErasureTest(self):
      ScrCmds.insertHeader('NetApp : Data Erasure Test : BEGIN')
      starttime = time.time()

      lba_size = TP.netapp_dataErasureTest['lba_size']
      data_size = int((TP.netapp_dataErasureTest['data_size'] / 4) * self.dut.imaxHead)                            #2GB Data Size
      loop_Count = TP.netapp_dataErasureTest['loop_Count']
      pattern_count  = TP.netapp_dataErasureTest['pattern_count']

      result = ICmd.SetFeatures(0x03, 0x47)                                        # Set DMA Mode UDMA 7 (UDMA150)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888,'Set DMA Mode UDMA 7 Failed! : %s' % str(result))
      else:
         objMsg.printMsg('Set DMA Mode UDMA 7  : %s' % str(result))

      SATA_SetFeatures.enable_WriteCache()

      if testSwitch.virtualRun:
         loop_Count = 1
         pattern_count = 1

      for i in range(loop_Count):
         for pattern in range(pattern_count):
         #Fill Write Buffer with (Random , Incremental, Shifting bit, Counting):
            if pattern == 0 :                                                     #Fill Write Buffer with (Incremental, Shifting bit, Counting,Random )
               self.fillRandomBuff()

            if pattern == 1 :
               self.fillIncrementalBuff()

            if pattern == 2 :
               self.fillShiftingBitBuff()

            if pattern == 3 :
               self.fillCountingBuff()

            targetLBA =  int(self.max_LLB * 0.02)                                                #OD : 2% from OD
            self.ErasureTest(targetLBA,data_size,lba_size)

            targetLBA =  int(self.max_LLB * 0.5)                                                 #OD : 50% of total LBA
            self.ErasureTest(targetLBA,data_size,lba_size)

            targetLBA =  int(self.max_LLB * 0.98)                                                #ID : 2% from ID
            self.ErasureTest(targetLBA,data_size,lba_size)

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Data Erasure Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Data Erasure Test : END')

   def DataErasureTest2_CHS(self):
      ScrCmds.insertHeader('NetApp : Data Erasure Test 2 : BEGIN')
      sptCmds.enableDiags()
      starttime = time.time()

      lba_size = TP.netapp_dataErasureTest2['lba_size']
      loop_Count = TP.netapp_dataErasureTest2['loop_Count']
      loop_Write = TP.netapp_dataErasureTest2['loop_Write']

      for cur_hd in range(self.dut.imaxHead):
         od_cylinder = self.zones[cur_hd][0]
         md_cylinder = self.zones[cur_hd][int(self.dut.numZones / 2)]
         id_cylinder = self.zones[cur_hd][int(self.dut.numZones - 1)] - 1

         if testSwitch.FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK:
            for retry in range(3):
               try:
                  objMsg.printMsg('DataErasureTest2 Test Head %d ' % cur_hd)
                  sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                    #Fill random pattern

                  #write 1MB data to center of surface
                  sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space
                  sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
                  sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                  #Write/Read 1000 loops using diagnostic batch file
                  objMsg.printMsg('DataErasureTest2 Test Read/Write %d loops ' % loop_Write)
                  sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                       #Start Batch File
                  sptCmds.sendDiagCmd('*7,%x,1'% 2,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)              #Set Loop Count 1 to 10000
                  sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                        #Batch File Label - Label 2

                  sptCmds.sendDiagCmd('/2A8,%x,,%x' % (md_cylinder + 1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)         #Set Test Space
                  sptCmds.sendDiagCmd('/2A9,%x,,%x' % (id_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #From Mid +1 to Extreme ID
                  sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
                  sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
                  sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

                  sptCmds.sendDiagCmd('/2A8,%x,,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #Set Test Space
                  sptCmds.sendDiagCmd('/2A9,%x,,%x' % (md_cylinder -1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #From OD to MD
                  sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
                  sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
                  sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

                  sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                    #Decrement Loop Count 1 and Branch to Label 2 if not 0
                  sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                           #End Batch File
                  sptCmds.sendDiagCmd('B,0',timeout = 2400,printResult = False, raiseException = 1, stopOnError = False)                                        #Run Batch File

                  sptCmds.sendDiagCmd('/2AD',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Reset Test Space
                  sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Set Test Space
                  sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
                  sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 30, printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Read Verify 1 track
                  break

               except Exception, e:
                  if e[0][2] == 13426:
                     objMsg.printMsg('Fail from invalid track retry on next 100 track')
                     objMsg.printMsg('Retry at loop %d'%(retry+1))
                     od_cylinder +=100
                     md_cylinder +=100
                     id_cylinder -=100
                  else:
                     raise
         else:
            objMsg.printMsg('DataErasureTest2 Test Head %d ' % cur_hd)
            sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                    #Fill random pattern

            #write 1MB data to center of surface
            sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space
            sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
            sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

            #Write/Read 1000 loops using diagnostic batch file
            objMsg.printMsg('DataErasureTest2 Test Read/Write %d loops ' % loop_Write)
            sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                       #Start Batch File
            sptCmds.sendDiagCmd('*7,%x,1'% 2,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)              #Set Loop Count 1 to 10000
            sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                        #Batch File Label - Label 2

            sptCmds.sendDiagCmd('/2A8,%x,,%x' % (md_cylinder + 1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)         #Set Test Space
            sptCmds.sendDiagCmd('/2A9,%x,,%x' % (id_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #From Mid +1 to Extreme ID
            sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
            sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
            sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

            sptCmds.sendDiagCmd('/2A8,%x,,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #Set Test Space
            sptCmds.sendDiagCmd('/2A9,%x,,%x' % (md_cylinder -1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #From OD to MD
            sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
            sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
            sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

            sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                    #Decrement Loop Count 1 and Branch to Label 2 if not 0
            sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                           #End Batch File
            sptCmds.sendDiagCmd('B,0',timeout = 2400,printResult = False, raiseException = 1, stopOnError = False)                                        #Run Batch File

            sptCmds.sendDiagCmd('/2AD',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Reset Test Space
            sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Set Test Space
            sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
            sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 30, printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Read Verify 1 track

      total_time = time.time() - starttime
      sptCmds.enableESLIP()
      ScrCmds.insertHeader('Data Erasure Test 2 Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Data Erasure Test 2 : END')

   def ErasureTest(self,targetLBA, blockSize,lba_size):
      step_lba = sector_size = 256
      loopCount = 10000

      if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
         sta_LLB = int(targetLBA)
         sta3 = int((sta_LLB & 0xFFFF000000000000) >> 48)
         sta2 = int((sta_LLB & 0x0000FFFF00000000) >> 32)
         sta1 = int((sta_LLB & 0x00000000FFFF0000) >> 16)
         sta0 = int((sta_LLB & 0x000000000000FFFF))

         end_LLB = int(targetLBA+ blockSize)
         end3 = int((end_LLB & 0xFFFF000000000000) >> 48)
         end2 = int((end_LLB & 0x0000FFFF00000000) >> 32)
         end1 = int((end_LLB & 0x00000000FFFF0000) >> 16)
         end0 = int((end_LLB & 0x000000000000FFFF))

         tot_blks_to_xfr = int(blockSize)
         tot1 = int((tot_blks_to_xfr & 0x00000000FFFF0000) >> 16)
         tot0 = int((tot_blks_to_xfr & 0x000000000000FFFF))

         objMsg.printMsg('Sequential : sta_LLB=%s, end_LLB=%s, tot_blks_to_xfr=%s, sta3=%s, sta2=%s, sta1=%s, sta0=%s, end3=%s, end2=%s, end1=%s, end0=%s, tot1=%s, tot0=%s'\
                       %(sta_LLB,end_LLB,tot_blks_to_xfr,sta3,sta2,sta1,sta0,end3,end2,end1,end0,tot1,tot0))

      result = ICmd.Seek(targetLBA)      # Seek to LBA 0
      if result['LLRET'] != OK:
         objMsg.printMsg('Seek cmd Failed!')

      if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
         ICmd.St(TP.prm_638_Unlock_Seagate)
         ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialWrite',CTRL_WORD1=(0x22),STARTING_LBA=(sta3,sta2,sta1,sta0),MAXIMUM_LBA =(end3,end2,end1,end0),TOTAL_BLKS_TO_XFR =(tot1,tot0))
      else:
         result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_size)
         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,'SequentialWriteDMAExt Failed! : %s' % str(result))
         else:
            if self.DEBUG:
               objMsg.printMsg('Write Data Complete! : %s' % str(result))

      result = ICmd.RandomSeekTime(targetLBA, targetLBA + (self.max_LLB * 0.02 ), loopCount)  #Random Seek 10000 times ;targetLBA + 2G + 2%
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Random Seek Error : %s" % str(result))
      else:
         if self.DEBUG:
            objMsg.printMsg('Random Seek ! : %s' % str(result))

      result = ICmd.BufferCopy(RBF,0,WBF,0,512)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888,'BufferCopy Failed! : %s' % str(result))

      Compare = 1
      if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
         ICmd.St(TP.prm_638_Unlock_Seagate)
         ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialReadVer',CTRL_WORD1=(0x42),STARTING_LBA=(sta3,sta2,sta1,sta0),MAXIMUM_LBA =(end3,end2,end1,end0),TOTAL_BLKS_TO_XFR =(tot1,tot0))
      else:
         result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_size)
         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,'SequentialReadVerifyExt Failed! : %s' % str(result))
         else:
            if self.DEBUG:
               objMsg.printMsg('Read Verify Data Complete! ! : %s' % str(result))


   def AdjacentPinch_CHS(self):
      ScrCmds.insertHeader('NetApp : Adjacent Pinch : BEGIN')
      sptCmds.enableDiags()
      starttime = time.time()

      lba_size = TP.netapp_adjacentPinch['lba_size']
      loop_Count = TP.netapp_adjacentPinch['loop_Count']
      loop_Write = TP.netapp_adjacentPinch['loop_Write']
      C1MB_to_LBA = int((1024 * 1024) / lba_size)
      blockSize = (1024 * 1024 / lba_size)                                          #1M Block Size

      if self.DEBUG:
         objMsg.printMsg('loop_Count : %d' %loop_Count)
         objMsg.printMsg('loop_Write : %d' %loop_Write)
         objMsg.printMsg('C1MB_to_LBA : %d, blockSize : %d, lba_size : %d' % (C1MB_to_LBA, blockSize, lba_size))

      if testSwitch.virtualRun:
         loop_Count = 1
         loop_Write = 1

      sector = 0
      for i in range(loop_Count):
         for cur_hd in range(self.dut.imaxHead):
            objMsg.printMsg('AdjacentPinch OD Test Head : %d' % cur_hd)

            od_cylinder = self.zones[cur_hd][0]
            md_cylinder = self.zones[cur_hd][int(self.dut.numZones / 2)]
            id_cylinder = self.zones[cur_hd][int(self.dut.numZones -1 )] -1

            if testSwitch.FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK:
               for retry in range(3):
                  objMsg.printMsg('AdjacentPinch OD Test Head : %d' % cur_hd)
                  try:
                     sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
                     sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

                     sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     #Write/Read 1000 loops using diagnostic batch file

                     objMsg.printMsg('AdjacentPinch OD Test Read/Write %d loops ' % loop_Write)
                     sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
                     sptCmds.sendDiagCmd('*7,%x,1' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
                     sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

                     sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
                     sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
                     sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
                     sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
                     sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
                     sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

                     break
                  except Exception, e:
                     if e[0][2] == 13426:
                        objMsg.printMsg('Fail from invalid track retry on next 100 track')
                        objMsg.printMsg('Retry at loop %d'%(retry+1))
                        od_cylinder += 100
                     else:
                        raise

               for retry in range(3):
                  objMsg.printMsg('AdjacentPinch ID Test Head : %d' % cur_hd)
                  try:
                     sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
                     sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

                     sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     #Write/Read 1000 loops using diagnostic batch file

                     objMsg.printMsg('AdjacentPinch ID Test Read/Write 1000 loops ')
                     sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
                     sptCmds.sendDiagCmd('*7,%x,1'%loop_Write,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
                     sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

                     sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
                     sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
                     sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
                     sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
                     sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
                     sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

                     break
                  except Exception, e:
                     if e[0][2] == 13426:
                        objMsg.printMsg('Fail from invalid track retry on next 100 track')
                        objMsg.printMsg('Retry at loop %d'%(retry+1))
                        id_cylinder -=100
                     else:
                        raise
            else:
               sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
               sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               #Write/Read 1000 loops using diagnostic batch file

               objMsg.printMsg('AdjacentPinch OD Test Read/Write %d loops ' % loop_Write)
               sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
               sptCmds.sendDiagCmd('*7,%x,1' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
               sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
               sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
               sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

               objMsg.printMsg('AdjacentPinch ID Test Head : %d' % cur_hd)

               sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
               sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               #Write/Read 1000 loops using diagnostic batch file

               objMsg.printMsg('AdjacentPinch ID Test Read/Write 1000 loops ')
               sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
               sptCmds.sendDiagCmd('*7,%x,1'%loop_Write,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
               sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
               sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
               sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

      total_time = time.time() - starttime
      sptCmds.enableESLIP()
      ScrCmds.insertHeader('Adjacent Pinch Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Adjacent Pinch Test : END')


   def WriteRead(self,targetLBA, blockSize, mode = 'NONE'):
      Compare = 0;
      Stamp = 0
      test_loop = 1
      sector_count = step_lba = 256
      if mode.find('C') >= 0:
         Compare = 1

      if mode.find('W')>= 0:
         if self.DEBUG:
            objMsg.printMsg('SequentialWriteVerify : startLBA : %d,  endLBA: %d,, Stamp : %d, Compare : %d, test_loop : %d ' % (targetLBA, (targetLBA+ blockSize),Stamp, Compare, test_loop))

         result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)                               #write 1

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,'SequentialWriteDMAExt Failed! : %s' % str(result))

      if mode.find('R') >= 0:
         if self.DEBUG:
            objMsg.printMsg('SequentialReadVerifyExt : startLBA : %d,  endLBA: %d, Stamp : %d, Compare : %d, test_loop : %d ' % (targetLBA, (targetLBA+ blockSize),Stamp, Compare, test_loop))

         result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)                           #read

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,"SequentialReadVerifyExt Failed: %s" % str(result))

   def WriteRead_CHS(self, cylinder, head, sector, blockSize, mode = 'NONE'):
      Compare = 0;
      Stamp = 0
      test_loop = 1
      step_Cylinder = 1
      step_Head = 1
      step_Sector = 256
      verify_msg = ""
      if mode.find('C') >= 0:
         Compare = 1
         verify_msg = "Verify"

      if mode.find('W')>= 0:
         if self.DEBUG:
            msg = 'SequentialWrite%s  cylinder : %d,  head: %d, sector : %d, sector_cnt : %d ' % (verify_msg, cylinder, head, sector, sector+blockSize)

         if(Compare):
            result = ICmd.SequentialWriteVerify(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)
         else:
            result = ICmd.SequentialWriteDMA(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,'Sequential Write Failed! : %s' % str(result))

      if mode.find('R') >= 0:
         if self.DEBUG:
            msg = ('SequentialRead%s  cylinder : %d,  head: %d, sector : %d, sector_cnt : %d ' % (verify_msg, cylinder, head, sector, sector+blockSize))

         if(Compare):
            result = ICmd.SequentialReadVerify(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)
         else:
            result = ICmd.SequentialReadDMA(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,"SequentialReadDMA Failed: %s" % str(result))

      if self.DEBUG:
         objMsg.printMsg('WriteRead_CHS Result : %s : %s' % (str(result), msg))

   def fillIncrementalBuff(self):
      result = ICmd.FillBuffInc(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Fill Incremental Buffer Error")

      objMsg.printMsg('Fill Incremental Buffer Complete.')

   def fillRandomBuff(self):
      result = ICmd.FillBuffRandom(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Fill Random Buffer Error")

      objMsg.printMsg('Fill Random Buffer Complete.')

   def fillShiftingBitBuff(self):
      import array
      data_pattern = array.array('H')

      data  = 0xFFFF
      increment = False
      for i in xrange(0,0x20000 / 2, 2):
      #Prepare Shifting Bit Pattern (Total Buffer Size = 0x20000 byte)
         if (increment) :
            data = data + 1
         else:
            data = data -1

         if data == 0xFFFF or data == 0:
            increment = not increment

         data_pattern.insert(i, 0)
         data_pattern.insert(i + 1, data & 0xFFFF)

      write_buffer = ''.join([(chr(num >>8) + chr(num & 0xff)) for num in (data_pattern)])
      result = ICmd.FillBuffer(WBF,0,write_buffer)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Fill Shifting Bit Buffer Error")

      objMsg.printMsg('Fill Shifting Bit Buffer Complete.')

   def fillCountingBuff(self):
      import array
      data_pattern = array.array('H')

      init_value  = 0xFFFF
      for i in xrange(0,0x20000 / 2):                                                 #Prepare Counting Pattern (Total Buffer Size = 0x20000 byte)
         data = i
         data = data << 8
         data = data | (i + 1)
         data_pattern.insert(i + 1, data & 0xFFFF)

      write_buffer = ''.join([(chr(num >>8) + chr(num & 0xff)) for num in (data_pattern)])
      result = ICmd.FillBuffer(WBF,0,write_buffer)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Fill Counting Buffer Error")

      objMsg.printMsg('Fill Counting Buffer Complete.')


   def getBasicDriveInfo(self):
      self.oSerial.enableDiags()
      self.numCyls,self.zones = self.oSerial.getZoneInfo(printResult=True)

      objMsg.printMsg("Total cylinder %s" % str(self.numCyls) )
      objMsg.printMsg("Zone %s" % str(self.zones) )

      objMsg.printMsg("Max Hd %s" % str(self.dut.imaxHead) )
      objMsg.printMsg("Num Zone %s" % str(self.dut.numZones) )

   def  ShortTest(self):
      pass

############# NetApp V3 Short Test ######################

#        self.BandSeqRWCmpTest()                                     #Test time vary by head
#
#        self.SeekTest_CHS()                                         #Test time vary by head
#        self.AdjacentPinch_CHS()                                    #Test time vary by head
#        self.StaticDataCompareTest()                                #Test time fixed
#        self.DataCompareSIOPTest()                                  #Test time fixed
#        self.ButterflyWriteTest()                                   #Test time vary by head
#        self.SimulateWorkLoadSIOPTest(mode = 'OLTP')                #Test time fixed
#        self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')         #Test time fixed
#        self.DataErasureTest()                                      #Test time vary by head
#        self.DataErasureTest2_CHS()                                 #Test time vary by head
#
#        self.SystemReadyTest(3)
#
#        self.VerifyDiskTest()
#        self.ZeroDisk()


###########################################################################################################
class CNETAPPWriteSame(CState):
   """
      NetApp Write Same screening
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProcess = CProcess()
      from serialScreen import sptDiagCmds
      self.oSerial = sptDiagCmds()
      self.oUtility = CUtility()

      self.DEBUG = 0

      if self.dut.driveattr.get('NETAPP_V3','NONE') != 'PASS' :
         self.getBasicDriveInfo()
         #temp 25
         self.dut.driveattr['NETAPP_V3'] = 'FAIL'
         self.PowerCycleTest()
         self.Intialization()

         ret = CIdentifyDevice().ID
         self.max_LLB = ret['IDDefaultLBAs'] - 1 # default for 28-bit LBA

         if ret['IDCommandSet5'] & 0x400:      # check bit 10
            objMsg.printMsg('Get ID Data 48 bit LBA is supported')
            self.max_LLB = ret['IDDefault48bitLBAs'] - 1

         if self.DEBUG:
            objMsg.printMsg('CIdentifyDevice data : %s' %str(ret))

         if self.max_LLB <= 0:
            self.max_LLB = 976773167
            objMsg.printMsg("Assign max_LLB to default : %d", self.max_LLB)

         objMsg.printMsg("The Maximum User LBA is : %08X       Drive Capacity - %dGB" %(self.max_LLB,(( self.max_LLB * 512 )/1000000000),))

         self.SeekTest_CHS()
         self.StaticDataCompareTest()

         self.DataCompareSIOPTest()

         self.ButterflyWriteTest()

#        #temp 20
#        self.ButterflyWriteTest();
#
#        #temp 10
#        self.ButterflyWriteTest();

         self.SystemReadyTest(3);

         self.StaticDataCompareTest()

         self.DataCompareSIOPTest()

         self.BandSeqRWCmpTest()

         self.StressedPinchTest()

         #temp 15
         self.DataCompareSIOPTest(caching = True)

         #temp 20
         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')

         #temp 25
         self.PowerCycleTest()
         self.Intialization()

         self.ButterflyWriteTest()

#        #temp 30
#        self.ButterflyWriteTest();
#
#        #temp 35
#        self.ButterflyWriteTest();

         #temp 40
         self.PowerCycleTest()
         self.Intialization()

         self.BandSeqRWCmpTest()

         self.DataErasureTest()

         self.SystemReadyTest(3)

         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')

         self.DataErasureTest2_CHS()

         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')

         self.PowerCycleTest()
         self.Intialization()

         #temp 40
         self.StressedPinchTest()

         #temp 35
         self.StaticDataCompareTest()

         #temp 31.66
         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')

         #temp 25
         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')

         self.DataErasureTest()

         self.BandSeqRWCmpTest()


         self.PowerCycleTest()
         self.Intialization()

#        self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')

         self.DataErasureTest2_CHS()

         self.StaticDataCompareTest()

         #temp 21.66
         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')

         #temp 15
         self.AdjacentPinch_CHS()

         #temp 10
         self.DataErasureTest()

         self.PowerCycleTest()
         self.Intialization()

#        self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')

         self.DataErasureTest2_CHS()

         self.PowerCycleTest()
         self.Intialization()

         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')

         self.SeekTest_CHS()

         self.ButterflyWriteTest()

#        #temp 15
#        self.ButterflyWriteTest();
#
#        #temp 20
#        self.ButterflyWriteTest();

         #temp 25
         self.DataCompareSIOPTest()

         #temp 30
         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')

         #temp 35
         self.AdjacentPinch_CHS()

         #temp 40
         self.SeekTest_CHS()

         self.StaticDataCompareTest()

         self.DataCompareSIOPTest()

         self.PowerCycleTest()
         self.Intialization()

         self.VerifyDiskTest()

         self.ButterflyWriteTest()

#        #temp 35
#        self.ButterflyWriteTest();
#
#        #temp 30
#        self.ButterflyWriteTest();

         #temp 25
         self.PowerCycleTest()
         self.Intialization()

         self.ZeroDisk()

         #SMART DST Long
         ICmd.LongDST()

         self.dut.driveattr['NETAPP_V3'] = 'PASS'

   def PowerCycleTest(self):
      ScrCmds.insertHeader('Power Cycle')
      objPwrCtrl.powerCycle(offTime=20, onTime=35, ataReadyCheck = True)

   def Intialization(self):
      ScrCmds.insertHeader("Unlock Seagate")
      try:
         ICmd.UnlockFactoryCmds()
      except:
         self.PowerCycleTest()

   def SeekTest_CHS(self,):
      #Now we don't put any spec in this test
      ScrCmds.insertHeader('NetApp : Full Seek test : BEGIN')
      sptCmds.enableDiags()
      starttime = time.time()

      seekType = int(TP.netapp_seekTest['seek_type'])
      loop_Seek = int(TP.netapp_seekTest['loop_Seek'])
      loop_Test = int(TP.netapp_seekTest['loop_Test'])

      objMsg.printMsg('SeekTest : seek_type : %d' % seekType)
      objMsg.printMsg('SeekTest : loop_Test : %d' % loop_Test)

      if testSwitch.virtualRun:
         loop_Seek  = 1;

      for i in range(loop_Test):
         for cur_hd in range(self.dut.imaxHead):
            objMsg.printMsg('NetApp Full Stroke Seek Head : %d' % cur_hd)
            sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                         #Set Test Space
            self.oSerial.gotoLevel('2')
            sptCmds.sendDiagCmd('S0,%x' % cur_hd,timeout = 30, printResult = False, raiseException = 0, stopOnError = False)              #Seek to test head
            self.oSerial.gotoLevel('3')
            sptCmds.sendDiagCmd('D999999999,2,5000',timeout = 300, printResult = True, raiseException = 0, stopOnError = False)    #Perform full strok seek

            objMsg.printMsg('NetApp Random Seek Head : %d' % cur_hd)
            sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                         #Set Test Space
            self.oSerial.gotoLevel('2')
            sptCmds.sendDiagCmd('S0,%x'% cur_hd,timeout = 30, printResult = False, raiseException = 0, stopOnError = False)              #Seek to test head
            self.oSerial.gotoLevel('3')
            sptCmds.sendDiagCmd('D0,%x,%x'%(seekType,loop_Seek),timeout = 300, printResult = True, raiseException = 0, stopOnError = False)            #Perform random seek

            if(self.DEBUG):
               objMsg.printMsg('SeekTest Head : %d, Time : %d' % (cur_hd, (time.time() - starttime)))

      total_time = time.time() - starttime
      sptCmds.enableESLIP()
      ScrCmds.insertHeader('Full Seek test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Full Seek test : END')

   def StaticDataCompareTest(self):
      ScrCmds.insertHeader('NetApp : Static Data Compare Test using DRAM Screen : BEGIN')
      starttime = time.time()

      TP.prm_DRamSettings.update({"StartLBA":0})                       #Target Write LBA : Start
      TP.prm_DRamSettings.update({"EndLBA":32})                        #Target Write LBA : End
      TP.prm_DRamSettings.update({"StepCount":32})                     #StepCount : 32LBA
      TP.prm_DRamSettings.update({"SectorCount":32})                   #SectorCount: 32LBA
      from DRamScreen import CDRamScreenTest
      oDRamScreen = CDRamScreenTest(self.dut)

      loop_Count = int(TP.netapp_staticDataCompare['loop_Count'])
      delay_time = int(TP.netapp_staticDataCompare['delay_time'])

      if testSwitch.virtualRun:
         loop_Count = 10
         delay_time = 0

      if(self.DEBUG):
         objMsg.printMsg('StaticDataCompareTest : loop_Count %d' % loop_Count)

      for i in range(loop_Count):
         oDRamScreen.dRamScreenTest()

         time.sleep(delay_time)

         if(self.DEBUG):
            objMsg.printMsg('StaticDataCompareTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Static Data Compare Test using DRAM Screen Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Static Data Compare Test using DRAM Screen : END')

   def ButterflyWriteTest(self):
      ScrCmds.insertHeader('NetApp : Butterfly Write Test : BEGIN')
      starttime = time.time()

      loop_count = loop_Count = int(TP.netapp_butterflyWriteTest['loop_Count'])
      step_rate = TP.netapp_butterflyWriteTest['step_rate']
      lba_size = TP.netapp_butterflyWriteTest['lba_size']
      run_time = int(TP.netapp_butterflyWriteTest['run_time']/ 4 * self.dut.imaxHead)

      block_size = 1024*32/lba_size
      (block_size_MSBs, block_size_LSBs) = self.UpperLower(block_size)

      objMsg.printMsg('loop_count : %d' %loop_count)
      objMsg.printMsg('step_rate : %d' %step_rate)
      objMsg.printMsg('run_time : %d Mins' %(run_time / 60))

      prm_506_SET_RUNTIME = {
         'test_num'          : 506,
         'prm_name'          : "prm_506_SET_RUNTIME",
         'spc_id'            :  1,
         "TEST_RUN_TIME"     :  run_time,
      }

      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         prm_510_BUTTERFLY = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_BUTTERFLY",
            'spc_id'            :  1,
            "CTRL_WORD1"        : (0x0422),                                        #Butterfly Sequencetioal Write;Display Location of errors
            "STARTING_LBA"      : (0,0,0,0),
            "BLKS_PER_XFR"      : (step_rate * block_size),                        #Need 32K write and seek 5*32K step, but cannot do that only write 5*32K.
            "OPTIONS"           : 0,                                               #Butterfly Converging
            "timeout"           :  3000,                                           #15 Mins Test Time
         }
      else:
         prm_510_BUTTERFLY = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_BUTTERFLY",
            'spc_id'            :  1,
            "CTRL_WORD1"        : (0x0422),                                        #Butterfly Sequencetioal Write;Display Location of errors
            "STARTING_LBA"      : (0,0,0,0),
            "BLKS_PER_XFR"      : (step_rate * block_size),                        #Need 32K write and seek 5*32K step, but cannot do that only write 5*32K.
            "OPTIONS"           : 0,                                               #Butterfly Converging
            "retryECList"       : [14016,14029],
            "retryMode"         : POWER_CYCLE_RETRY,
            "retryCount"        : 2,
            "timeout"           :  3000,                                           #15 Mins Test Time
         }

      numGB = (self.max_LLB * lba_size ) / (10**9)
      ScriptComment("The Maximum LBA is : %08X Drive Capacity - %dGB" %(self.max_LLB, numGB,))

      (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0) = self.oUtility.returnStartLbaWords(self.max_LLB - 1)

      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         for i in xrange(loop_count):
            failed = 1
            retry = 0
            while failed == 1 and retry <= TP.maxRetries_T510Butterfly:
               try:
                  self.oProcess.St(
                        prm_506_SET_RUNTIME,
                     )

                  self.oProcess.St(
                        prm_510_BUTTERFLY,
                        STARTING_LBA = (0, 0, 0, 0),
                        MAXIMUM_LBA  = (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0),
                     )
                  failed = 0

                  self.oProcess.St(
                        prm_506_SET_RUNTIME,TEST_RUN_TIME = 0,
                     )
               except ScriptTestFailure, (failureData):
                  ec = failureData[0][2]
                  if ec in [14016, 14029] and retry < TP.maxRetries_T510Butterfly:
                     objPwrCtrl.powerCycle(5000,12000,10,30)
                     retry += 1
                  else:
                     raise

            if(self.DEBUG):
               objMsg.printMsg('ButterflyWriteTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))
      else:
         for i in xrange(loop_count):
            self.oProcess.St(
                   prm_506_SET_RUNTIME,
                )

            self.oProcess.St(
                   prm_510_BUTTERFLY,
                   STARTING_LBA = (0, 0, 0, 0),
                   MAXIMUM_LBA  = (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0),
                )

            self.oProcess.St(
                   prm_506_SET_RUNTIME,TEST_RUN_TIME = 0,
                )

            if(self.DEBUG):
               objMsg.printMsg('ButterflyWriteTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Butterfly Write Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Butterfly Write Test : END')

   def UpperLower(self, FourByteNum):
      FourByteNum = FourByteNum & 0xFFFFFFFF                                   #chop off any more than 4 bytes
      MSBs = FourByteNum >> 16
      LSBs = FourByteNum & 0xFFFF
      return (MSBs, LSBs)

   def SystemReadyTest(self, power_cycle_count = 3):
      ScrCmds.insertHeader('NetApp : System Ready Test : BEGIN')
      starttime = time.time()

      for i in range(1,power_cycle_count +1):
         objMsg.printMsg("Power Cycle %d"% i)
         self.PowerCycleTest();

         time.sleep(90)

      total_time = time.time() - starttime
      ScrCmds.insertHeader('System Ready Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : System Ready Test : END')

   def ZeroDisk(self):
      ScrCmds.insertHeader('NetApp : Zero Disk Test : BEGIN')
      starttime = time.time()

      SATA_SetFeatures.enable_WriteCache()

      oProcess = CProcess()
      objMsg.printMsg('Start Write Same')
      oProcess.St(TP.prm_510_CMDTIME,BLKS_PER_XFR=(0x5000))  # 'BLKS_PER_XFR': (0x5000) 20*1024=20K
      self.dut.driveattr['WRITE_SAME'] = 'PASS'

      total_time = time.time() - starttime

      objPwrCtrl.powerCycle(offTime=20, onTime=35, ataReadyCheck = True)

      ScrCmds.insertHeader('Zero Disk Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Zero Disk Test : END')

   def VerifyDiskTest(self):
      ScrCmds.insertHeader('NetApp : Verify Disk Test : BEGIN')
      stepLBA = sctCnt = 256 # 48bit LBA addressing
      starttime = time.time()

      if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
         ICmd.St(TP.prm_638_Unlock_Seagate)
         ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialRead')
      else:
         result = ICmd.SequentialReadDMAExt(0, self.max_LLB, stepLBA, sctCnt)
         objMsg.printMsg('Full Pack Read - Result %s' %str(result))

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,"Full Pack Zero Read Failed : %s" %str(result))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Verify Disk Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : System Ready Test : END')

   def DataCompareSIOPTest(self, caching = False):
      ScrCmds.insertHeader('NetApp : Data Compare SIOP Test : BEGIN')
      starttime = time.time()

      if caching == False:
         #result = ICmd.SetFeatures(0x82) #diable write cache
         SATA_SetFeatures.disable_WriteCache()
         objMsg.printMsg('disable write cache')
         #if result['LLRET'] != OK:
         #   ScrCmds.raiseException(10888, "Failed Disable Write Cache Data : %s" %str(result))

      import random
      loop_count = loop_Count = int(TP.netapp_dataCompareSIOPTest['loop_Count'])
      stepLBA = sctCnt =TP.netapp_dataCompareSIOPTest['sector_count']
      delay_time = int(TP.netapp_staticDataCompare['delay_time'])

      lba_size = 512
      loop_Count = int(float(loop_Count) / 4 * self.dut.imaxHead)

      objMsg.printMsg('loop_count : %d' %loop_count)
      objMsg.printMsg('sector_count : %d' %sctCnt)
      objMsg.printMsg('delay_time : %d' %delay_time)

      if testSwitch.virtualRun:
         loop_count = 10
         delay_time = 0

      for i in range(loop_count):
         position_A = random.randrange(0, self.max_LLB - sctCnt)                    #Random A location
         position_B = random.randrange(0, self.max_LLB - sctCnt)                    #Random B location

         if i == 4000 or i == 0:                                               #Random new Data every 4000 loops
            objMsg.printMsg('Fill Random pattern at loop : %d' % (i))
            self.fillRandomBuff()

         result = ICmd.WriteSectors(position_A, sctCnt)                        #Write A

         if self.DEBUG:
            objMsg.printMsg('WriteSectors A: %s' %str(result))

         if result['LLRET'] != 0:
            ScrCmds.raiseException(10888, "Write data A error: %s" %str(result))

         result = ICmd.WriteSectors(position_B, sctCnt)                        #Write B

         if self.DEBUG:
            objMsg.printMsg('WriteSectors B: %s' %str(result))

         if result['LLRET'] != 0:
            ScrCmds.raiseException(10888, "Write data B error : %s" %str(result))

         result = ICmd.ReadSectors(position_A, sctCnt)                         #Read Sector A
         if self.DEBUG:
            objMsg.printMsg('Read A : %s' %str(result))

         if result['LLRET'] == OK:
            result = ICmd.CompareBuffers(0, sctCnt * lba_size)                 #Compare Buffer
            if self.DEBUG:
               objMsg.printMsg('CompareBuffers A result : %s' %str(result))
         else:
            ScrCmds.raiseException(10888,"Compare buffer Failed : %s" %str(result))

         if result['LLRET'] == OK:
            result = ICmd.GetBuffer(RBF, 0,  sctCnt * lba_size)                 #Get Read Buffer
            if self.DEBUG:
               objMsg.printMsg('GetBuffer A result : %s' %str(result))
         else:
            ScrCmds.raiseException(10888,"Get Buffer Failed: %s" %str(result))

         if result['LLRET'] == OK:
            result = ICmd.ReadVerifySects(position_A, sctCnt)                   #Read Verify Sector
            if self.DEBUG:
               objMsg.printMsg('ReadVerifySects A result : %s' %str(result))
         else:
            ScrCmds.raiseException(10888,"Read Verify Sectors A Failed : %s" %str(result))

         result = ICmd.ReadSectors(position_B, sctCnt)                          #Read Sector
         if self.DEBUG:
            objMsg.printMsg('Read B : %s' %str(result))

         if result['LLRET'] == OK:
            result = ICmd.CompareBuffers(0,  sctCnt * lba_size)                 #Compare Buffer
            if self.DEBUG:
               objMsg.printMsg('CompareBuffers B result : %s' %str(result))
         else:
            ScrCmds.raiseException(10888,"Compare buffer Failed : %s" %str(result))

         if result['LLRET'] == OK:
            result = ICmd.GetBuffer(RBF, 0, sctCnt * lba_size)                  #Get Read Buffer
            if self.DEBUG:
               objMsg.printMsg('GetBuffer B result : %s' %str(result))
         else:
            ScrCmds.raiseException(10888,"Get Buffer Failed : %s" %str(result))

         if result['LLRET'] == OK:
            result = ICmd.ReadVerifySects(position_B, sctCnt)                   #Read Verify Sector
            if self.DEBUG:
               objMsg.printMsg('ReadVerifySects B result : %s' %str(result))
         else:
            ScrCmds.raiseException(10888,"Read Verify Sectors B Failed: %s" %str(result))

         if not testSwitch.virtualRun:
            ScriptPause(delay_time)

         if(self.DEBUG):
            objMsg.printMsg('DataCompareSIOPTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

      if caching == False:
         result = ICmd.SetFeatures(0x02) #re-enable write cache

         if self.DEBUG:
            objMsg.printMsg('Compare result : %s' %str(result))

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,"Failed Enable Write Cache: %s" %str(result))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Data Compare SIOP Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Data Compare SIOP Test : END')

   def BandSeqRWCmpTest(self):
      ScrCmds.insertHeader('NetApp : Banded Sequential Write/Read Compare Test : BEGIN')
      starttime = time.time()

      increasing_step = int(TP.netapp_bandSeqRWCmpTest['increasing_step'])
      pattern_count =TP.netapp_bandSeqRWCmpTest['pattern_count']
      stepLBA =TP.netapp_bandSeqRWCmpTest['stepLBA']
      loop_Count =TP.netapp_bandSeqRWCmpTest['loop_Count']

      increasing_step = ((increasing_step * 4) / self.dut.imaxHead)

      objMsg.printMsg('increasing_step : %d' %increasing_step)
      objMsg.printMsg('pattern_count : %d' %pattern_count)
      objMsg.printMsg('stepLBA : %d' %stepLBA)
      objMsg.printMsg('loop_Count : %d' %loop_Count)

      SATA_SetFeatures.enable_WriteCache()

      if testSwitch.virtualRun:
         loop_Count = 1
         pattern_count = 1

      for iCount in range(loop_Count):
         for pattern in range(int(pattern_count)):
            if pattern == 0 :                                                     #Fill Write Buffer with (Incremental, Shifting bit, Counting,Random )
               self.fillIncrementalBuff()

            if pattern == 1 :
               self.fillShiftingBitBuff()

            if pattern == 2 :
               self.fillCountingBuff()

            if pattern == 3 :
               self.fillRandomBuff()

            blockSize = int((1024 * 1024 * 8) / 512)                                # ~ 8M data size
            sector_count = step_lba = stepLBA                                     #  32K xfer size
            Stamp = 0
            Compare = 0
            test_loop = 1

            count_step = 0
            for i in range(0,100,increasing_step):                                #Increasing about 2% per step
               targetLBA = int(self.max_LLB *(float(increasing_step) / 100) * count_step)              #Write Data Phase
               result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)

               count_step = count_step + 1

               if self.DEBUG:
                  objMsg.printMsg('Write - Step :  %d' % increasing_step)
                  objMsg.printMsg('Write - LBA :  %x' % targetLBA)
                  objMsg.printMsg('Write - Result :  %s' %str(result))

               if result['LLRET'] != OK:
                  objMsg.printMsg('Write - Step :  %d' % increasing_step)
                  objMsg.printMsg('Write - LBA :  %x' % targetLBA)
                  objMsg.printMsg('Write - blockSize :  %x' % blockSize)
                  objMsg.printMsg('Write - step_lba :  %d' % step_lba)
                  objMsg.printMsg('Write - sector_count :  %x' % sector_count)
                  objMsg.printMsg('Write - Loop :  %d' % i)
                  objMsg.printMsg('Write - max_LLB :  %d' % self.max_LLB)
                  ScrCmds.raiseException(10888, "Write Banded Data Failed : %s" %str(result))

            result = ICmd.BufferCopy(RBF,0,WBF,0,512)
            if result['LLRET'] != OK:
               ScrCmds.raiseException(10888,'BufferCopy Failed! : %s' % str(result))

            Compare = 1
            count_step = 0
            for i in range(0,100,increasing_step):                                 #Read Data Phase
               targetLBA = int(self.max_LLB *(float(increasing_step) / 100)* count_step)
               result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)

               count_step = count_step + 1

               if result['LLRET'] != OK:
                  objMsg.printMsg('Read - Step :  %d' % increasing_step)
                  objMsg.printMsg('Read - LBA :  %x' % targetLBA)
                  objMsg.printMsg('Read - blockSize :  %x' % blockSize)
                  objMsg.printMsg('Read - step_lba :  %d' % step_lba)
                  objMsg.printMsg('Read - sector_count :  %x' % sector_count)
                  objMsg.printMsg('Read - Loop :  %d' % i)
                  objMsg.printMsg('Read - max_LLB :  %d' % self.max_LLB)
                  ScrCmds.raiseException(10888, "Read Banded Data Failed : %s" %str(result))

               if self.DEBUG:
                  objMsg.printMsg('Read - Result %s' %str(result))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Banded Sequential Write/Read Compare Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Banded Sequential Write/Read Compare Test : END')

   def StressedPinchTest(self):
      ScrCmds.insertHeader('NetApp : Stressed Pinch Test : BEGIN')
      starttime = time.time()

      loop_Count = TP.netapp_stressedPinchTest['loop_Count']
      write_Loop = TP.netapp_stressedPinchTest['loop_Write']
      stepLBA =TP.netapp_stressedPinchTest['stepLBA']

      objMsg.printMsg('loop_Count : %d' %loop_Count)
      objMsg.printMsg('write_Loop : %d' %write_Loop)
      objMsg.printMsg('stepLBA : %d' %stepLBA)

      SATA_SetFeatures.enable_WriteCache()
      result = ICmd.FillBuffRandom(WBF)                                            #Fill Write Buffer with Random Data
      if result['LLRET'] != OK:
         if self.DEBUG:
            objMsg.printMsg('FillBuffRandom : %s' %str(result))
         ScrCmds.raiseException(11044, "Fill Random Pattern error")

      startLBA = 0;
      C1MB_to_LBA = int((1024 * 1024) / 512)
      C1MB = 1024 * 1024
      block_size = C1MB / 512
      write_Loop = 10

      for loop in range(loop_Count):
         targetLBA = int(self.max_LLB /2)                                            #Write to LBA (Max LBA/2) & verify (Max LBA/2).
         self.WriteRead(targetLBA, block_size, 'WC')

         targetLBA = int(self.max_LLB /2) + block_size                               #Write to LBA (Max LBA/2 + 1024Kb) & verify LBA (Max LBA/2 +1024Kbytes)

         self.WriteRead(targetLBA, block_size, 'WC')

         targetLBA = int(self.max_LLB /2) - block_size                               #Write to LBA (Max LBA/2 ? 1024Kb) & verify LBA (Max LBA/2 -1024Kbytes)
         self.WriteRead(targetLBA, block_size, 'WC')

         for i in range(0,write_Loop):
            targetLBA = int(self.max_LLB / 2 + C1MB_to_LBA)                         #Seek to random LBA in the range [(Max LBA/2 + 1024Kbytes) ? Max LBA]

            result = ICmd.RandomSeekTime(targetLBA, self.max_LLB, 10, seekType = 28, timeout = 600, exc=0)
            if self.DEBUG:
               objMsg.printMsg('RandomSeekTime 2: %s' %str(result))

            if result['LLRET'] != OK:
               ScrCmds.raiseException(11044, "Random Seek Error")

            targetLBA = int(self.max_LLB /2)                                        #Write to LBA (Max LBA/2) & verify (Max LBA/2).
            self.WriteRead(targetLBA, block_size, 'WC')

            targetLBA = int(self.max_LLB / 2)                                       #Seek to random LBA in the range [(Max LBA/2 + 1024Kbytes) ? Max LBA]

            result = ICmd.RandomSeekTime(0, targetLBA, 10, seekType = 28, timeout = 600, exc=0)
            if result['LLRET'] != OK:
               if self.DEBUG:
                  objMsg.printMsg('Read B : %s' %str(result))
               ScrCmds.raiseException(11044, "Random Seek Error")

            targetLBA = int(self.max_LLB /2)                                        #Write to LBA (Max LBA/2) & verify (Max LBA/2).
            self.WriteRead(targetLBA, block_size, 'W')

            targetLBA = int(self.max_LLB /2) + block_size                           #Read LBA (Max LBA/2 + 1024Kb)
            self.WriteRead(targetLBA, block_size, 'R')

            targetLBA = int(self.max_LLB /2) - block_size                           #Read LBA (Max LBA/2 ? 1024Kb)
            self.WriteRead(targetLBA, block_size, 'R')

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Stressed Pinch Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Stressed Pinch Test : END')

   def SimulateWorkLoadSIOPTest(self, mode = 'NONE'):
      ScrCmds.insertHeader('NetApp : Simulate WorkLoad SIOP Test %s : BEGIN' % mode)
      starttime = time.time()

      import random

      lba_size = TP.netapp_simulateWorkLoadSIOPTest['lba_size']
      run_time = TP.netapp_simulateWorkLoadSIOPTest['run_time']

      if testSwitch.virtualRun:
         run_time = 5

      if self.DEBUG:
         objMsg.printMsg('lba_size : %d' %lba_size)
         objMsg.printMsg('run_time : %d' %run_time)

      while(True):
         loop_random = random.randrange(1,100)
         for i in range(loop_random):
            if mode == 'FILE_SERVER':
               random_value = random.random()
               startLBA = 0
               targetLBA = 0
               stepLBA = 0
               lba_count = 0

               if random <= 0.1:                                               #random location
                  startLBA = int(random.randrange(int(self.max_LLB *0.01)), int(self.max_LLB))

               elif random <=(0.1 + 0.3):
                  startLBA = int(random.randrange(int(self.max_LLB *0.3), int(self.max_LLB *0.6)))

               else:
                  startLBA = int(random.randrange(int(self.max_LLB *0), int(self.max_LLB *0.1)))

               random_value = random.random()

               if random <= 0.3:                                               #random transfer size
                  lba_count = int(random.randrange(int(2 * (1024 /lba_size)), int(32 * 1024/ lba_size)))        #2KB - 32Kb

               else:
                  lba_count = int(random.randrange(int(32 * 1024/lba_size),  int(128 * 1024/ lba_size)))      #32KB - 128Kb

               random_value = random.random()

               if random <= 0.2:                                               #random RW mode. Read:Write ratio of 4:1
                  result = ICmd.WriteSectors(startLBA, lba_count)
                  if self.DEBUG:
                     objMsg.printMsg('WriteSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Write Failed %s" % str(result))

               else:
                  result = ICmd.ReadSectors(startLBA, lba_count)
                  if self.DEBUG:
                     objMsg.printMsg('ReadSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Read Failed %s" % str(result))

            elif mode == 'OLTP':

               random_value = random.random()
               startLBA = 0
               targetLBA = 0
               stepLBA = 0
               lba_count = 0

               if random <= 0.2:                                               #random location
                  startLBA = int(random.randrange(int(self.max_LLB *0.01), int(self.max_LLB)))

               elif random <=(0.2 + 0.3):
                  startLBA = int(random.randrange(int(self.max_LLB *0.1), int(self.max_LLB *0.3)))

               else:
                  startLBA = int(random.randrange(int(self.max_LLB * 0.3), int(self.max_LLB *0.6)))

               random_value = random.random()

               if random <= 0.3:                                               #random transfer size
                  lba_count = int(random.randrange( int(4 * 1024/ lba_size),  int(8 * 1024/ lba_size)))        #4KB - 8Kb

               else:
                  lba_count = int(random.randrange( int(1 * 1024/ lba_size),  int(4 * 1024/ lba_size)))          #1KB - 4Kb

               random_value = random.random()

               if random <= 0.2:                                               #random RW mode
                  result = ICmd.WriteSectors(startLBA, lba_count)
                  if self.DEBUG:
                     objMsg.printMsg('WriteSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Write Failed %s" % str(result))

               else:
                  result = ICmd.ReadSectors(startLBA, lba_count)

                  if self.DEBUG:
                     objMsg.printMsg('ReadSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Read Failed %s" % str(result))

         pause_time = random.randrange(1, 10)

         if not testSwitch.virtualRun:
            ScriptPause(pause_time)

         if((time.time() - starttime) > run_time):
            break

         if(self.DEBUG):
            objMsg.printMsg('SimulateWorkLoadSIOPTestt random %s Loop : %d, Time : %d' % (mode,i, (time.time() - starttime)))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Simulate WorkLoad SIOP  %s Time Usage : %d' % (mode, total_time))
      ScrCmds.insertHeader('NetApp : Simulate WorkLoad SIOP Test %s : END' % mode)

   def DataErasureTest(self):
      ScrCmds.insertHeader('NetApp : Data Erasure Test : BEGIN')
      starttime = time.time()

      lba_size = TP.netapp_dataErasureTest['lba_size']
      data_size = int((TP.netapp_dataErasureTest['data_size'] / 4) * self.dut.imaxHead)                            #2GB Data Size
      loop_Count = TP.netapp_dataErasureTest['loop_Count']
      pattern_count  = TP.netapp_dataErasureTest['pattern_count']

      result = ICmd.SetFeatures(0x03, 0x47)                                        # Set DMA Mode UDMA 7 (UDMA150)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888,'Set DMA Mode UDMA 7 Failed! : %s' % str(result))
      else:
         objMsg.printMsg('Set DMA Mode UDMA 7  : %s' % str(result))

      SATA_SetFeatures.enable_WriteCache()

      if testSwitch.virtualRun:
         loop_Count = 1
         pattern_count = 1

      for i in range(loop_Count):
         for pattern in range(pattern_count):
         #Fill Write Buffer with (Random , Incremental, Shifting bit, Counting):
            if pattern == 0 :                                                     #Fill Write Buffer with (Incremental, Shifting bit, Counting,Random )
               self.fillRandomBuff()

            if pattern == 1 :
               self.fillIncrementalBuff()

            if pattern == 2 :
               self.fillShiftingBitBuff()

            if pattern == 3 :
               self.fillCountingBuff()

            targetLBA =  int(self.max_LLB * 0.02)                                                #OD : 2% from OD
            self.ErasureTest(targetLBA,data_size,lba_size)

            targetLBA =  int(self.max_LLB * 0.5)                                                 #OD : 50% of total LBA
            self.ErasureTest(targetLBA,data_size,lba_size)

            targetLBA =  int(self.max_LLB * 0.98)                                                #ID : 2% from ID
            self.ErasureTest(targetLBA,data_size,lba_size)

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Data Erasure Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Data Erasure Test : END')

   def DataErasureTest2_CHS(self):
      ScrCmds.insertHeader('NetApp : Data Erasure Test 2 : BEGIN')
      sptCmds.enableDiags()
      starttime = time.time()

      lba_size = TP.netapp_dataErasureTest2['lba_size']
      loop_Count = TP.netapp_dataErasureTest2['loop_Count']
      loop_Write = TP.netapp_dataErasureTest2['loop_Write']

      for cur_hd in range(self.dut.imaxHead):
         od_cylinder = self.zones[cur_hd][0]
         md_cylinder = self.zones[cur_hd][int(self.dut.numZones / 2)]
         id_cylinder = self.zones[cur_hd][int(self.dut.numZones - 1)] - 1

         if testSwitch.FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK:
            for retry in range(3):
               try:
                  objMsg.printMsg('DataErasureTest2 Test Head %d ' % cur_hd)
                  sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                    #Fill random pattern

                  #write 1MB data to center of surface
                  sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space
                  sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
                  sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                  #Write/Read 1000 loops using diagnostic batch file
                  objMsg.printMsg('DataErasureTest2 Test Read/Write %d loops ' % loop_Write)
                  sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                       #Start Batch File
                  sptCmds.sendDiagCmd('*7,%x,1'% 2,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)              #Set Loop Count 1 to 10000
                  sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                        #Batch File Label - Label 2

                  sptCmds.sendDiagCmd('/2A8,%x,,%x' % (md_cylinder + 1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)         #Set Test Space
                  sptCmds.sendDiagCmd('/2A9,%x,,%x' % (id_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #From Mid +1 to Extreme ID
                  sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
                  sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
                  sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

                  sptCmds.sendDiagCmd('/2A8,%x,,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #Set Test Space
                  sptCmds.sendDiagCmd('/2A9,%x,,%x' % (md_cylinder -1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #From OD to MD
                  sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
                  sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
                  sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

                  sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                    #Decrement Loop Count 1 and Branch to Label 2 if not 0
                  sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                           #End Batch File
                  sptCmds.sendDiagCmd('B,0',timeout = 2400,printResult = False, raiseException = 1, stopOnError = False)                                        #Run Batch File

                  sptCmds.sendDiagCmd('/2AD',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Reset Test Space
                  sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Set Test Space
                  sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
                  sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 30, printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Read Verify 1 track
                  break

               except Exception, e:
                  if e[0][2] == 13426:
                     objMsg.printMsg('Fail from invalid track retry on next 100 track')
                     objMsg.printMsg('Retry at loop %d'%(retry+1))
                     od_cylinder +=100
                     md_cylinder +=100
                     id_cylinder -=100
                  else:
                     raise
         else:
            objMsg.printMsg('DataErasureTest2 Test Head %d ' % cur_hd)
            sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                    #Fill random pattern

            #write 1MB data to center of surface
            sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space
            sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
            sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

            #Write/Read 1000 loops using diagnostic batch file
            objMsg.printMsg('DataErasureTest2 Test Read/Write %d loops ' % loop_Write)
            sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                       #Start Batch File
            sptCmds.sendDiagCmd('*7,%x,1'% 2,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)              #Set Loop Count 1 to 10000
            sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                        #Batch File Label - Label 2

            sptCmds.sendDiagCmd('/2A8,%x,,%x' % (md_cylinder + 1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)         #Set Test Space
            sptCmds.sendDiagCmd('/2A9,%x,,%x' % (id_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #From Mid +1 to Extreme ID
            sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
            sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
            sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

            sptCmds.sendDiagCmd('/2A8,%x,,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #Set Test Space
            sptCmds.sendDiagCmd('/2A9,%x,,%x' % (md_cylinder -1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #From OD to MD
            sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
            sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
            sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

            sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                    #Decrement Loop Count 1 and Branch to Label 2 if not 0
            sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                           #End Batch File
            sptCmds.sendDiagCmd('B,0',timeout = 2400,printResult = False, raiseException = 1, stopOnError = False)                                        #Run Batch File

            sptCmds.sendDiagCmd('/2AD',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Reset Test Space
            sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Set Test Space
            sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
            sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 30, printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Read Verify 1 track

      total_time = time.time() - starttime
      sptCmds.enableESLIP()
      ScrCmds.insertHeader('Data Erasure Test 2 Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Data Erasure Test 2 : END')

   def ErasureTest(self,targetLBA, blockSize,lba_size):
      step_lba = sector_size = 256
      loopCount = 10000

      if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
         sta_LLB = int(targetLBA)
         sta3 = int((sta_LLB & 0xFFFF000000000000) >> 48)
         sta2 = int((sta_LLB & 0x0000FFFF00000000) >> 32)
         sta1 = int((sta_LLB & 0x00000000FFFF0000) >> 16)
         sta0 = int((sta_LLB & 0x000000000000FFFF))

         end_LLB = int(targetLBA+ blockSize)
         end3 = int((end_LLB & 0xFFFF000000000000) >> 48)
         end2 = int((end_LLB & 0x0000FFFF00000000) >> 32)
         end1 = int((end_LLB & 0x00000000FFFF0000) >> 16)
         end0 = int((end_LLB & 0x000000000000FFFF))

         tot_blks_to_xfr = int(blockSize)
         tot1 = int((tot_blks_to_xfr & 0x00000000FFFF0000) >> 16)
         tot0 = int((tot_blks_to_xfr & 0x000000000000FFFF))

         objMsg.printMsg('Sequential : sta_LLB=%s, end_LLB=%s, tot_blks_to_xfr=%s, sta3=%s, sta2=%s, sta1=%s, sta0=%s, end3=%s, end2=%s, end1=%s, end0=%s, tot1=%s, tot0=%s'\
                       %(sta_LLB,end_LLB,tot_blks_to_xfr,sta3,sta2,sta1,sta0,end3,end2,end1,end0,tot1,tot0))

      result = ICmd.Seek(targetLBA)      # Seek to LBA 0
      if result['LLRET'] != OK:
         objMsg.printMsg('Seek cmd Failed!')

      if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
         ICmd.St(TP.prm_638_Unlock_Seagate)
         ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialWrite',CTRL_WORD1=(0x22),STARTING_LBA=(sta3,sta2,sta1,sta0),MAXIMUM_LBA =(end3,end2,end1,end0),TOTAL_BLKS_TO_XFR =(tot1,tot0))
      else:
         result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_size)
         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,'SequentialWriteDMAExt Failed! : %s' % str(result))
         else:
            if self.DEBUG:
               objMsg.printMsg('Write Data Complete! : %s' % str(result))

      result = ICmd.RandomSeekTime(targetLBA, targetLBA + (self.max_LLB * 0.02 ), loopCount)  #Random Seek 10000 times ;targetLBA + 2G + 2%
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Random Seek Error : %s" % str(result))
      else:
         if self.DEBUG:
            objMsg.printMsg('Random Seek ! : %s' % str(result))

      result = ICmd.BufferCopy(RBF,0,WBF,0,512)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888,'BufferCopy Failed! : %s' % str(result))

      Compare = 1
      if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
         ICmd.St(TP.prm_638_Unlock_Seagate)
         ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialReadVer',CTRL_WORD1=(0x42),STARTING_LBA=(sta3,sta2,sta1,sta0),MAXIMUM_LBA =(end3,end2,end1,end0),TOTAL_BLKS_TO_XFR =(tot1,tot0))
      else:
         result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_size)
         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,'SequentialReadVerifyExt Failed! : %s' % str(result))
         else:
            if self.DEBUG:
               objMsg.printMsg('Read Verify Data Complete! ! : %s' % str(result))


   def AdjacentPinch_CHS(self):
      ScrCmds.insertHeader('NetApp : Adjacent Pinch : BEGIN')
      sptCmds.enableDiags()
      starttime = time.time()

      lba_size = TP.netapp_adjacentPinch['lba_size']
      loop_Count = TP.netapp_adjacentPinch['loop_Count']
      loop_Write = TP.netapp_adjacentPinch['loop_Write']
      C1MB_to_LBA = int((1024 * 1024) / lba_size)
      blockSize = (1024 * 1024 / lba_size)                                          #1M Block Size

      if self.DEBUG:
         objMsg.printMsg('loop_Count : %d' %loop_Count)
         objMsg.printMsg('loop_Write : %d' %loop_Write)
         objMsg.printMsg('C1MB_to_LBA : %d, blockSize : %d, lba_size : %d' % (C1MB_to_LBA, blockSize, lba_size))

      if testSwitch.virtualRun:
         loop_Count = 1
         loop_Write = 1

      sector = 0
      for i in range(loop_Count):
         for cur_hd in range(self.dut.imaxHead):
            #objMsg.printMsg('AdjacentPinch OD Test Head : %d' % cur_hd)

            od_cylinder = self.zones[cur_hd][0]
            md_cylinder = self.zones[cur_hd][int(self.dut.numZones / 2)]
            id_cylinder = self.zones[cur_hd][int(self.dut.numZones -1 )] -1

            if testSwitch.FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK:
               for retry in range(3):
                  objMsg.printMsg('AdjacentPinch OD Test Head : %d' % cur_hd)
                  try:
                     sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
                     sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

                     sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     #Write/Read 1000 loops using diagnostic batch file

                     objMsg.printMsg('AdjacentPinch OD Test Read/Write %d loops ' % loop_Write)
                     sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
                     sptCmds.sendDiagCmd('*7,%x,1' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
                     sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

                     sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
                     sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
                     sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
                     sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
                     sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
                     sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

                     break
                  except Exception, e:
                     if e[0][2] == 13426:
                        objMsg.printMsg('Fail from invalid track retry on next 100 track')
                        objMsg.printMsg('Retry at loop %d'%(retry+1))
                        od_cylinder += 100
                     else:
                        raise

               for retry in range(3):
                  try:
                     objMsg.printMsg('AdjacentPinch ID Test Head : %d' % cur_hd)

                     sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
                     sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

                     sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     #Write/Read 1000 loops using diagnostic batch file
                     objMsg.printMsg('AdjacentPinch ID Test Read/Write 1000 loops ')
                     sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
                     sptCmds.sendDiagCmd('*7,%x,1'%loop_Write,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
                     sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

                     sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
                     sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
                     sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
                     sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                     sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
                     sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
                     sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

                     break
                  except Exception, e:
                     if e[0][2] == 13426:
                        objMsg.printMsg('Fail from invalid track retry on next 100 track')
                        objMsg.printMsg('Retry at loop %d'%(retry+1))
                        id_cylinder -=100
                     else:
                        raise

            else:
               objMsg.printMsg('AdjacentPinch OD Test Head : %d' % cur_hd)

               sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
               sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               #Write/Read 1000 loops using diagnostic batch file

               objMsg.printMsg('AdjacentPinch OD Test Read/Write %d loops ' % loop_Write)
               sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
               sptCmds.sendDiagCmd('*7,%x,1' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
               sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
               sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
               sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

               objMsg.printMsg('AdjacentPinch ID Test Head : %d' % cur_hd)
               sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
               sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               #Write/Read 1000 loops using diagnostic batch file

               objMsg.printMsg('AdjacentPinch ID Test Read/Write 1000 loops ')

               sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
               sptCmds.sendDiagCmd('*7,%x,1'%loop_Write,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
               sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
               sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
               sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

      total_time = time.time() - starttime
      sptCmds.enableESLIP()
      ScrCmds.insertHeader('Adjacent Pinch Test Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Adjacent Pinch Test : END')


   def WriteRead(self,targetLBA, blockSize, mode = 'NONE'):
      Compare = 0;
      Stamp = 0
      test_loop = 1
      sector_count = step_lba = 256
      if mode.find('C') >= 0:
         Compare = 1

      if mode.find('W')>= 0:
         if self.DEBUG:
            objMsg.printMsg('SequentialWriteVerify : startLBA : %d,  endLBA: %d,, Stamp : %d, Compare : %d, test_loop : %d ' % (targetLBA, (targetLBA+ blockSize),Stamp, Compare, test_loop))

         result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)                               #write 1

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,'SequentialWriteDMAExt Failed! : %s' % str(result))

      if mode.find('R') >= 0:
         if self.DEBUG:
            objMsg.printMsg('SequentialReadVerifyExt : startLBA : %d,  endLBA: %d, Stamp : %d, Compare : %d, test_loop : %d ' % (targetLBA, (targetLBA+ blockSize),Stamp, Compare, test_loop))

         result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)                           #read

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,"SequentialReadVerifyExt Failed: %s" % str(result))

   def WriteRead_CHS(self, cylinder, head, sector, blockSize, mode = 'NONE'):
      Compare = 0;
      Stamp = 0
      test_loop = 1
      step_Cylinder = 1
      step_Head = 1
      step_Sector = 256
      verify_msg = ""
      if mode.find('C') >= 0:
         Compare = 1
         verify_msg = "Verify"

      if mode.find('W')>= 0:
         if self.DEBUG:
            msg = 'SequentialWrite%s  cylinder : %d,  head: %d, sector : %d, sector_cnt : %d ' % (verify_msg, cylinder, head, sector, sector+blockSize)

         if(Compare):
            result = ICmd.SequentialWriteVerify(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)
         else:
            result = ICmd.SequentialWriteDMA(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,'Sequential Write Failed! : %s' % str(result))

      if mode.find('R') >= 0:
         if self.DEBUG:
            msg = ('SequentialRead%s  cylinder : %d,  head: %d, sector : %d, sector_cnt : %d ' % (verify_msg, cylinder, head, sector, sector+blockSize))

         if(Compare):
            result = ICmd.SequentialReadVerify(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)
         else:
            result = ICmd.SequentialReadDMA(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,"SequentialReadDMA Failed: %s" % str(result))

      if self.DEBUG:
         objMsg.printMsg('WriteRead_CHS Result : %s : %s' % (str(result), msg))

   def fillIncrementalBuff(self):
      result = ICmd.FillBuffInc(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Fill Incremental Buffer Error")

      objMsg.printMsg('Fill Incremental Buffer Complete.')

   def fillRandomBuff(self):
      result = ICmd.FillBuffRandom(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Fill Random Buffer Error")

      objMsg.printMsg('Fill Random Buffer Complete.')

   def fillShiftingBitBuff(self):
      import array
      data_pattern = array.array('H')

      data  = 0xFFFF
      increment = False
      for i in xrange(0,0x20000 / 2, 2):
      #Prepare Shifting Bit Pattern (Total Buffer Size = 0x20000 byte)
         if (increment) :
            data = data + 1
         else:
            data = data -1

         if data == 0xFFFF or data == 0:
            increment = not increment

         data_pattern.insert(i, 0)
         data_pattern.insert(i + 1, data & 0xFFFF)

      write_buffer = ''.join([(chr(num >>8) + chr(num & 0xff)) for num in (data_pattern)])
      result = ICmd.FillBuffer(WBF,0,write_buffer)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Fill Shifting Bit Buffer Error")

      objMsg.printMsg('Fill Shifting Bit Buffer Complete.')

   def fillCountingBuff(self):
      import array
      data_pattern = array.array('H')

      init_value  = 0xFFFF
      for i in xrange(0,0x20000 / 2):                                                 #Prepare Counting Pattern (Total Buffer Size = 0x20000 byte)
         data = i
         data = data << 8
         data = data | (i + 1)
         data_pattern.insert(i + 1, data & 0xFFFF)

      write_buffer = ''.join([(chr(num >>8) + chr(num & 0xff)) for num in (data_pattern)])
      result = ICmd.FillBuffer(WBF,0,write_buffer)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Fill Counting Buffer Error")

      objMsg.printMsg('Fill Counting Buffer Complete.')


   def getBasicDriveInfo(self):
      self.oSerial.enableDiags()
      self.numCyls,self.zones = self.oSerial.getZoneInfo(printResult=True)

      objMsg.printMsg("Total cylinder %s" % str(self.numCyls) )
      objMsg.printMsg("Zone %s" % str(self.zones) )

      objMsg.printMsg("Max Hd %s" % str(self.dut.imaxHead) )
      objMsg.printMsg("Num Zone %s" % str(self.dut.numZones) )

   def  ShortTest(self):
      pass

############# NetApp V3 Short Test ######################

#        self.BandSeqRWCmpTest()                                     #Test time vary by head
#
#        self.SeekTest_CHS()                                         #Test time vary by head
#        self.AdjacentPinch_CHS()                                    #Test time vary by head
#        self.StaticDataCompareTest()                                #Test time fixed
#        self.DataCompareSIOPTest()                                  #Test time fixed
#        self.ButterflyWriteTest()                                   #Test time vary by head
#        self.SimulateWorkLoadSIOPTest(mode = 'OLTP')                #Test time fixed
#        self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')         #Test time fixed
#        self.DataErasureTest()                                      #Test time vary by head
#        self.DataErasureTest2_CHS()                                 #Test time vary by head
#
#        self.SystemReadyTest(3)
#
#        self.VerifyDiskTest()
#        self.ZeroDisk()


###########################################################################################################
class CMuskieKTMQMV2(CState):
   """
   Korat MQM version 2
      1. Full Seek test Time Usage
      2. Static Data Compare Test using DRAM Screen Time Usage
      3. Data Compare SIOP Test Time Usage
      4. Butterfly Write Time Usage
      5. System Ready Test Time Usage
      6. Banded Sequential Write/Read Compare Test Time Usage
      7. Stressed Pinch Test Time Usage
      8. Simulate WorkLoad SIOP  OLTP Time Usage
      9. Simulate WorkLoad SIOP  FILE_SERVER Time Usage
      10.Adjacent Pinch Test Time Usage
      11.Data Erasure Test Time Usage
      12.Data Erasure Test 2 Time Usage
      13.Butterfly write in OD
      14.Butterfly write in MD
      15.Butterfly write in ID
      16.Verify Disk Test Time Usage
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProcess = CProcess()
      from serialScreen import sptDiagCmds
      self.oSerial = sptDiagCmds()

      self.oUtility = CUtility()

      import string,time,sys

      self.DEBUG = 0

      if 1:
         self.dut.driveattr['KT_MQMV2'] = 'FAIL'
         self.getBasicDriveInfo()
         #temp 25
         self.PowerCycleTest()
         self.Intialization()

         ret = CIdentifyDevice().ID
         self.max_LLB = ret['IDDefaultLBAs'] - 1 # default for 28-bit LBA

         if ret['IDCommandSet5'] & 0x400:      # check bit 10
            objMsg.printMsg('Get ID Data 48 bit LBA is supported')
            self.max_LLB = ret['IDDefault48bitLBAs'] - 1

         if self.DEBUG:
           objMsg.printMsg('CIdentifyDevice data : %s' %str(ret))

         if self.max_LLB <= 0:
            self.max_LLB = 976773167
            objMsg.printMsg("Assign max_LLB to default : %d", self.max_LLB)

         objMsg.printMsg("The Maximum User LBA is : %08X       Drive Capacity - %dGB" %(self.max_LLB,(( self.max_LLB * 512 )/1000000000),))


         self.SeekTest_CHS()
         self.PowerCycleTest()
         self.Intialization()

         self.StaticDataCompareTest()
         self.DataCompareSIOPTest()
         self.ButterflyWriteTest()
         self.SystemReadyTest(3)
         self.BandSeqRWCmpTest()

         self.PowerCycleTest()
         self.Intialization()

         self.StressedPinchTest()
         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')
         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')
         self.AdjacentPinch_CHS()
         self.DataErasureTest()

         self.PowerCycleTest()
         self.Intialization()

         self.DataErasureTest2_CHS()

         self.PowerCycleTest()
         self.Intialization()

         self.ButterflyIn(run_time = 3600, WR_MODE = 'Write', START_LBA = 'OD')
         self.ButterflyIn(run_time = 3600, WR_MODE = 'Write', START_LBA = 'MD')
         self.ButterflyIn(run_time = 3600, WR_MODE = 'Write', START_LBA = 'ID')

         self.PowerCycleTest()
         self.Intialization()
         self.VerifyDiskTest()

         self.dut.driveattr['KT_MQMV2'] = 'PASS'


   def PowerCycleTest(self):
       ScrCmds.insertHeader('Power Cycle')
       objPwrCtrl.powerCycle(offTime=20, onTime=35, ataReadyCheck = True)

   def Intialization(self):
       ScrCmds.insertHeader("Unlock Seagate")
       try:
         ICmd.UnlockFactoryCmds()
       except:
         self.PowerCycleTest()

   def SeekTest_CHS(self,):
       #Now we don't put any spec in this test
       ScrCmds.insertHeader('NetApp : Full Seek test : BEGIN')
       sptCmds.enableDiags()
       starttime = time.time()

       seekType = int(TP.netapp_seekTest['seek_type'])
       loop_Seek = int(TP.netapp_seekTest['loop_Seek'])
       loop_Test = int(TP.netapp_seekTest['loop_Test'])

       objMsg.printMsg('SeekTest : seek_type : %d' % seekType)
       objMsg.printMsg('SeekTest : loop_Test : %d' % loop_Test)

       if testSwitch.virtualRun:
          loop_Seek  = 1;

       for i in range(loop_Test):
          for cur_hd in range(self.dut.imaxHead):
              objMsg.printMsg('NetApp Full Stroke Seek Head : %d' % cur_hd)
              sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                         #Set Test Space
              self.oSerial.gotoLevel('2')
              sptCmds.sendDiagCmd('S0,%x' % cur_hd,timeout = 30, printResult = False, raiseException = 0, stopOnError = False)              #Seek to test head
              self.oSerial.gotoLevel('3')
              sptCmds.sendDiagCmd('D999999999,2,5000',timeout = 300, printResult = True, raiseException = 0, stopOnError = False)    #Perform full strok seek

              objMsg.printMsg('NetApp Random Seek Head : %d' % cur_hd)
              sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                         #Set Test Space
              self.oSerial.gotoLevel('2')
              sptCmds.sendDiagCmd('S0,%x'% cur_hd,timeout = 30, printResult = False, raiseException = 0, stopOnError = False)              #Seek to test head
              self.oSerial.gotoLevel('3')
              sptCmds.sendDiagCmd('D0,%x,%x'%(seekType,loop_Seek),timeout = 300, printResult = True, raiseException = 0, stopOnError = False)            #Perform random seek

              if(self.DEBUG):
                  objMsg.printMsg('SeekTest Head : %d, Time : %d' % (cur_hd, (time.time() - starttime)))

       total_time = time.time() - starttime
       sptCmds.enableESLIP()
       ScrCmds.insertHeader('Full Seek test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Full Seek test : END')

   def StaticDataCompareTest(self):
       ScrCmds.insertHeader('NetApp : Static Data Compare Test using DRAM Screen : BEGIN')
       starttime = time.time()

       TP.prm_DRamSettings.update({"StartLBA":0})                       #Target Write LBA : Start
       TP.prm_DRamSettings.update({"EndLBA":32})                        #Target Write LBA : End
       TP.prm_DRamSettings.update({"StepCount":32})                     #StepCount : 32LBA
       TP.prm_DRamSettings.update({"SectorCount":32})                   #SectorCount: 32LBA
       from DRamScreen import CDRamScreenTest
       oDRamScreen = CDRamScreenTest(self.dut)

       loop_Count = int(TP.netapp_staticDataCompare['loop_Count'])
       delay_time = int(TP.netapp_staticDataCompare['delay_time'])

       if testSwitch.virtualRun:
            loop_Count = 10
            delay_time = 0

       if(self.DEBUG):
           objMsg.printMsg('StaticDataCompareTest : loop_Count %d' % loop_Count)

       for i in range(loop_Count):
            oDRamScreen.dRamScreenTest()

            time.sleep(delay_time)

            if(self.DEBUG):
               objMsg.printMsg('StaticDataCompareTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

       total_time = time.time() - starttime
       ScrCmds.insertHeader('Static Data Compare Test using DRAM Screen Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Static Data Compare Test using DRAM Screen : END')

   def ButterflyIn(self, run_time = 60, WR_MODE = 'Write', loops = 1, START_LBA = 'OD'):

      objMsg.printMsg('Butterfly In %s %d loops start'%(WR_MODE,loops))
      if WR_MODE == 'Write':
         prm_510_CWORD1 = (0x0422)
      elif WR_MODE == 'Read':
         prm_510_CWORD1 = (0x0412)
      else:
         ScrCmds.raiseException(11044, "Invalid butterfly write read parameter")

      xLBA = self.max_LLB/5
      if START_LBA == 'OD':
         START_LBA = 0
         MAX_LBA = self.max_LLB
      elif START_LBA == 'MD':
         START_LBA = xLBA
         MAX_LBA = self.max_LLB - xLBA
      elif START_LBA == 'ID':
         START_LBA = xLBA*2
         MAX_LBA = self.max_LLB - xLBA*2
      else:
         ScrCmds.raiseException(11044, "Invalid butterfly starting LBA parameter")

      (str_3, str_2, str_1, str_0) = self.oUtility.returnStartLbaWords(START_LBA)
      (max_3, max_2, max_1, max_0) = self.oUtility.returnStartLbaWords(MAX_LBA)
      prm_506_Timed = {
         'test_num'          : 506,
         'prm_name'          : "prm_506_Timed",
         'spc_id'            :  1,
         "TEST_RUN_TIME"     :  run_time,
      }

      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         prm_510_ButterflyIn = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_ButterflyIn",
            'spc_id'            :  1,
            "CTRL_WORD1"        :  prm_510_CWORD1,               #Butterfly Sequencetioal Write or Read, Display Location of errors
            "STARTING_LBA"      : (str_3, str_2, str_1, str_0),
            "MAXIMUM_LBA"       : (max_3, max_2, max_1, max_0),
            "BLKS_PER_XFR"      : (0x10),                        #0x10 block per xfer same as SAS
            "OPTIONS"           : 0,                             #Converging
            "timeout"           :  6000,
            "MAX_NBR_ERRORS"    : 0,
         }
      else:
         prm_510_ButterflyIn = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_ButterflyIn",
            'spc_id'            :  1,
            "CTRL_WORD1"        :  prm_510_CWORD1,               #Butterfly Sequencetioal Write or Read, Display Location of errors
            "STARTING_LBA"      : (str_3, str_2, str_1, str_0),
            "MAXIMUM_LBA"       : (max_3, max_2, max_1, max_0),
            "BLKS_PER_XFR"      : (0x10),                        #0x10 block per xfer same as SAS
            "OPTIONS"           : 0,                             #Converging
            "retryECList"       : [14016,14029],
            "retryMode"         : POWER_CYCLE_RETRY,
            "retryCount"        : 2,
            "timeout"           :  6000,
            "MAX_NBR_ERRORS"    : 0,
         }

      prm_506_DefaultTimed = {
         'test_num'          : 506,
         'prm_name'          : "prm_506_DefaultTimed",
         'spc_id'            :  1,
         "TEST_RUN_TIME"     :  0,
      }
      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         for i in range(loops):
            objMsg.printMsg('Perform butterfly In %s loop %d'%(WR_MODE,loops+1))
            failed = 1
            retry = 0
            while failed == 1 and retry <= TP.maxRetries_T510Butterfly:
               try:
                  self.oProcess.St(prm_506_Timed)
                  self.oProcess.St(prm_510_ButterflyIn)
                  failed = 0
                  self.oProcess.St(prm_506_DefaultTimed)
               except ScriptTestFailure, (failureData):
                  ec = failureData[0][2]
                  if ec in [14016, 14029] and retry < TP.maxRetries_T510Butterfly:
                     objPwrCtrl.powerCycle(5000,12000,10,30)
                     retry += 1
                  else:
                     raise
            objPwrCtrl.powerCycle(5000,12000,10,30)
      else:
         for i in range(loops):
            objMsg.printMsg('Perform butterfly In %s loop %d'%(WR_MODE,loops+1))
            self.oProcess.St(prm_506_Timed)
            self.oProcess.St(prm_510_ButterflyIn)
            self.oProcess.St(prm_506_DefaultTimed)
            objPwrCtrl.powerCycle(5000,12000,10,30)

      objMsg.printMsg('Butterfly In %s %d loops complete'%(WR_MODE,loops))

   def ButterflyWriteTest(self):
      ScrCmds.insertHeader('NetApp : Butterfly Write Test : BEGIN')
      starttime = time.time()

      loop_count = loop_Count = int(TP.netapp_butterflyWriteTest['loop_Count'])
      step_rate = TP.netapp_butterflyWriteTest['step_rate']
      lba_size = TP.netapp_butterflyWriteTest['lba_size']
      run_time = int(TP.netapp_butterflyWriteTest['run_time']/ 4 * self.dut.imaxHead)

      block_size = 1024*32/lba_size
      (block_size_MSBs, block_size_LSBs) = self.UpperLower(block_size)

      objMsg.printMsg('loop_count : %d' %loop_count)
      objMsg.printMsg('step_rate : %d' %step_rate)
      objMsg.printMsg('run_time : %d Mins' %(run_time / 60))

      prm_506_SET_RUNTIME = {
         'test_num'          : 506,
         'prm_name'          : "prm_506_SET_RUNTIME",
         'spc_id'            :  1,
         "TEST_RUN_TIME"     :  run_time,
      }

      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         prm_510_BUTTERFLY = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_BUTTERFLY",
            'spc_id'            :  1,
            "CTRL_WORD1"        : (0x0422),                                        #Butterfly Sequencetioal Write;Display Location of errors
            "STARTING_LBA"      : (0,0,0,0),
            "BLKS_PER_XFR"      : (step_rate * block_size),                        #Need 32K write and seek 5*32K step, but cannot do that only write 5*32K.
            "OPTIONS"           : 0,                                               #Butterfly Converging
            "timeout"           :  3000,                                           #15 Mins Test Time
         }
      else:
         prm_510_BUTTERFLY = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_BUTTERFLY",
            'spc_id'            :  1,
            "CTRL_WORD1"        : (0x0422),                                        #Butterfly Sequencetioal Write;Display Location of errors
            "STARTING_LBA"      : (0,0,0,0),
            "BLKS_PER_XFR"      : (step_rate * block_size),                        #Need 32K write and seek 5*32K step, but cannot do that only write 5*32K.
            "OPTIONS"           : 0,                                               #Butterfly Converging
            "retryECList"       : [14016,14029],
            "retryMode"         : POWER_CYCLE_RETRY,
            "retryCount"        : 2,
            "timeout"           :  3000,                                           #15 Mins Test Time
         }

      numGB = (self.max_LLB * lba_size ) / (10**9)
      ScriptComment("The Maximum LBA is : %08X Drive Capacity - %dGB" %(self.max_LLB, numGB,))

      (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0) = self.oUtility.returnStartLbaWords(self.max_LLB - 1)

      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         for i in xrange(loop_count):
             failed = 1
             retry = 0
             while failed == 1 and retry <= TP.maxRetries_T510Butterfly:
               try:
                  self.oProcess.St(
                        prm_506_SET_RUNTIME,
                     )

                  self.oProcess.St(
                        prm_510_BUTTERFLY,
                        STARTING_LBA = (0, 0, 0, 0),
                        MAXIMUM_LBA  = (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0),
                     )
                  failed = 0

                  self.oProcess.St(
                        prm_506_SET_RUNTIME,TEST_RUN_TIME = 0,
                     )
               except ScriptTestFailure, (failureData):
                  ec = failureData[0][2]
                  if ec in [14016, 14029] and retry < TP.maxRetries_T510Butterfly:
                     objPwrCtrl.powerCycle(5000,12000,10,30)
                     retry += 1
                  else:
                     raise

             if(self.DEBUG):
               objMsg.printMsg('ButterflyWriteTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))
      else:
         for i in xrange(loop_count):
             self.oProcess.St(
                   prm_506_SET_RUNTIME,
                )

             self.oProcess.St(
                   prm_510_BUTTERFLY,
                   STARTING_LBA = (0, 0, 0, 0),
                   MAXIMUM_LBA  = (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0),
                )

             self.oProcess.St(
                   prm_506_SET_RUNTIME,TEST_RUN_TIME = 0,
                )

             if(self.DEBUG):
               objMsg.printMsg('ButterflyWriteTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Butterfly Write Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Butterfly Write Test : END')

   def UpperLower(self, FourByteNum):
       FourByteNum = FourByteNum & 0xFFFFFFFF                                   #chop off any more than 4 bytes
       MSBs = FourByteNum >> 16
       LSBs = FourByteNum & 0xFFFF
       return (MSBs, LSBs)

   def SystemReadyTest(self, power_cycle_count = 3):
       ScrCmds.insertHeader('NetApp : System Ready Test : BEGIN')
       starttime = time.time()

       for i in range(1,power_cycle_count +1):
           objMsg.printMsg("Power Cycle %d"% i)
           self.PowerCycleTest();

           time.sleep(90)

       total_time = time.time() - starttime
       ScrCmds.insertHeader('System Ready Test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : System Ready Test : END')

   def VerifyDiskTest(self):
       ScrCmds.insertHeader('NetApp : Verify Disk Test : BEGIN')
       stepLBA = sctCnt = 256 # 48bit LBA addressing
       starttime = time.time()

       if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
         ICmd.St(TP.prm_638_Unlock_Seagate)
         ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialRead')
       else:
         result = ICmd.SequentialReadDMAExt(0, self.max_LLB, stepLBA, sctCnt)
         objMsg.printMsg('Full Pack Read - Result %s' %str(result))

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,"Full Pack Zero Read Failed : %s" %str(result))

       total_time = time.time() - starttime
       ScrCmds.insertHeader('Verify Disk Test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : System Ready Test : END')

   def DataCompareSIOPTest(self, caching = False):
       ScrCmds.insertHeader('NetApp : Data Compare SIOP Test : BEGIN')
       starttime = time.time()

       if caching == False:
           #result = ICmd.SetFeatures(0x82) #diable write cache
           SATA_SetFeatures.disable_WriteCache()
           objMsg.printMsg('disable write cache')
           #if result['LLRET'] != OK:
           #    ScrCmds.raiseException(10888, "Failed Disable Write Cache Data : %s" %str(result))

       import random
       loop_count = loop_Count = int(TP.netapp_dataCompareSIOPTest['loop_Count'])
       stepLBA = sctCnt =TP.netapp_dataCompareSIOPTest['sector_count']
       delay_time = int(TP.netapp_staticDataCompare['delay_time'])

       lba_size = 512
       loop_Count = int(float(loop_Count) / 4 * self.dut.imaxHead)

       objMsg.printMsg('loop_count : %d' %loop_count)
       objMsg.printMsg('sector_count : %d' %sctCnt)
       objMsg.printMsg('delay_time : %d' %delay_time)

       if testSwitch.virtualRun:
          loop_count = 10
          delay_time = 0

       for i in range(loop_count):
          position_A = random.randrange(0, self.max_LLB - sctCnt)                    #Random A location
          position_B = random.randrange(0, self.max_LLB - sctCnt)                    #Random B location

          if i == 4000 or i == 0:                                               #Random new Data every 4000 loops
             objMsg.printMsg('Fill Random pattern at loop : %d' % (i))
             self.fillRandomBuff()

          result = ICmd.WriteSectors(position_A, sctCnt)                        #Write A

          if self.DEBUG:
               objMsg.printMsg('WriteSectors A: %s' %str(result))

          if result['LLRET'] != 0:
            ScrCmds.raiseException(10888, "Write data A error: %s" %str(result))

          result = ICmd.WriteSectors(position_B, sctCnt)                        #Write B

          if self.DEBUG:
               objMsg.printMsg('WriteSectors B: %s' %str(result))

          if result['LLRET'] != 0:
             ScrCmds.raiseException(10888, "Write data B error : %s" %str(result))

          result = ICmd.ReadSectors(position_A, sctCnt)                         #Read Sector A
          if self.DEBUG:
             objMsg.printMsg('Read A : %s' %str(result))

          if result['LLRET'] == OK:
             result = ICmd.CompareBuffers(0, sctCnt * lba_size)                 #Compare Buffer
             if self.DEBUG:
                objMsg.printMsg('CompareBuffers A result : %s' %str(result))
          else:
              ScrCmds.raiseException(10888,"Compare buffer Failed : %s" %str(result))

          if result['LLRET'] == OK:
             result = ICmd.GetBuffer(RBF, 0,  sctCnt * lba_size)                 #Get Read Buffer
             if self.DEBUG:
                objMsg.printMsg('GetBuffer A result : %s' %str(result))
          else:
              ScrCmds.raiseException(10888,"Get Buffer Failed: %s" %str(result))

          if result['LLRET'] == OK:
             result = ICmd.ReadVerifySects(position_A, sctCnt)                   #Read Verify Sector
             if self.DEBUG:
                objMsg.printMsg('ReadVerifySects A result : %s' %str(result))
          else:
             ScrCmds.raiseException(10888,"Read Verify Sectors A Failed : %s" %str(result))

          result = ICmd.ReadSectors(position_B, sctCnt)                          #Read Sector
          if self.DEBUG:
             objMsg.printMsg('Read B : %s' %str(result))

          if result['LLRET'] == OK:
             result = ICmd.CompareBuffers(0,  sctCnt * lba_size)                 #Compare Buffer
             if self.DEBUG:
                objMsg.printMsg('CompareBuffers B result : %s' %str(result))
          else:
              ScrCmds.raiseException(10888,"Compare buffer Failed : %s" %str(result))

          if result['LLRET'] == OK:
             result = ICmd.GetBuffer(RBF, 0, sctCnt * lba_size)                  #Get Read Buffer
             if self.DEBUG:
                objMsg.printMsg('GetBuffer B result : %s' %str(result))
          else:
              ScrCmds.raiseException(10888,"Get Buffer Failed : %s" %str(result))

          if result['LLRET'] == OK:
             result = ICmd.ReadVerifySects(position_B, sctCnt)                   #Read Verify Sector
             if self.DEBUG:
                objMsg.printMsg('ReadVerifySects B result : %s' %str(result))
          else:
             ScrCmds.raiseException(10888,"Read Verify Sectors B Failed: %s" %str(result))

          if not testSwitch.virtualRun:
             ScriptPause(delay_time)

          if(self.DEBUG):
               objMsg.printMsg('DataCompareSIOPTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

       if caching == False:
           result = ICmd.SetFeatures(0x02) #re-enable write cache

           if self.DEBUG:
                objMsg.printMsg('Compare result : %s' %str(result))

           if result['LLRET'] != OK:
               ScrCmds.raiseException(10888,"Failed Enable Write Cache: %s" %str(result))

       total_time = time.time() - starttime
       ScrCmds.insertHeader('Data Compare SIOP Test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Data Compare SIOP Test : END')

   def BandSeqRWCmpTest(self):
           ScrCmds.insertHeader('NetApp : Banded Sequential Write/Read Compare Test : BEGIN')
           starttime = time.time()

           increasing_step = int(TP.netapp_bandSeqRWCmpTest['increasing_step'])
           pattern_count =TP.netapp_bandSeqRWCmpTest['pattern_count']
           stepLBA =TP.netapp_bandSeqRWCmpTest['stepLBA']
           loop_Count =TP.netapp_bandSeqRWCmpTest['loop_Count']

           increasing_step = ((increasing_step * 4) / self.dut.imaxHead)

           objMsg.printMsg('increasing_step : %d' %increasing_step)
           objMsg.printMsg('pattern_count : %d' %pattern_count)
           objMsg.printMsg('stepLBA : %d' %stepLBA)
           objMsg.printMsg('loop_Count : %d' %loop_Count)

           SATA_SetFeatures.enable_WriteCache()

           if testSwitch.virtualRun:
              loop_Count = 1
              pattern_count = 1

           for iCount in range(loop_Count):
               for pattern in range(int(pattern_count)):
                  if pattern == 0 :                                                     #Fill Write Buffer with (Incremental, Shifting bit, Counting,Random )
                     self.fillIncrementalBuff()

                  if pattern == 1 :
                     self.fillShiftingBitBuff()

                  if pattern == 2 :
                     self.fillCountingBuff()

                  if pattern == 3 :
                     self.fillRandomBuff()

                  blockSize = int((1024 * 1024 * 8) / 512)                                # ~ 8M data size
                  sector_count = step_lba = stepLBA                                     #  32K xfer size
                  Stamp = 0
                  Compare = 0
                  test_loop = 1

                  count_step = 0
                  for i in range(0,100,increasing_step):                                #Increasing about 2% per step
                     targetLBA = int(self.max_LLB *(float(increasing_step) / 100) * count_step)              #Write Data Phase
                     result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)

                     count_step = count_step + 1

                     if self.DEBUG:
                        objMsg.printMsg('Write - Step :  %d' % increasing_step)
                        objMsg.printMsg('Write - LBA :  %x' % targetLBA)
                        objMsg.printMsg('Write - Result :  %s' %str(result))

                     if result['LLRET'] != OK:
                        objMsg.printMsg('Write - Step :  %d' % increasing_step)
                        objMsg.printMsg('Write - LBA :  %x' % targetLBA)
                        objMsg.printMsg('Write - blockSize :  %x' % blockSize)
                        objMsg.printMsg('Write - step_lba :  %d' % step_lba)
                        objMsg.printMsg('Write - sector_count :  %x' % sector_count)
                        objMsg.printMsg('Write - Loop :  %d' % i)
                        objMsg.printMsg('Write - max_LLB :  %d' % self.max_LLB)
                        ScrCmds.raiseException(10888, "Write Banded Data Failed : %s" %str(result))

                  result = ICmd.BufferCopy(RBF,0,WBF,0,512)
                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,'BufferCopy Failed! : %s' % str(result))

                  Compare = 1
                  count_step = 0
                  for i in range(0,100,increasing_step):                                 #Read Data Phase
                     targetLBA = int(self.max_LLB *(float(increasing_step) / 100)* count_step)
                     result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)

                     count_step = count_step + 1

                     if result['LLRET'] != OK:
                        objMsg.printMsg('Read - Step :  %d' % increasing_step)
                        objMsg.printMsg('Read - LBA :  %x' % targetLBA)
                        objMsg.printMsg('Read - blockSize :  %x' % blockSize)
                        objMsg.printMsg('Read - step_lba :  %d' % step_lba)
                        objMsg.printMsg('Read - sector_count :  %x' % sector_count)
                        objMsg.printMsg('Read - Loop :  %d' % i)
                        objMsg.printMsg('Read - max_LLB :  %d' % self.max_LLB)
                        ScrCmds.raiseException(10888, "Read Banded Data Failed : %s" %str(result))

                     if self.DEBUG:
                        objMsg.printMsg('Read - Result %s' %str(result))

           total_time = time.time() - starttime
           ScrCmds.insertHeader('Banded Sequential Write/Read Compare Test Time Usage : %d' % total_time)
           ScrCmds.insertHeader('NetApp : Banded Sequential Write/Read Compare Test : END')

   def StressedPinchTest(self):
       ScrCmds.insertHeader('NetApp : Stressed Pinch Test : BEGIN')
       starttime = time.time()

       loop_Count = TP.netapp_stressedPinchTest['loop_Count']
       write_Loop = TP.netapp_stressedPinchTest['loop_Write']
       stepLBA =TP.netapp_stressedPinchTest['stepLBA']

       objMsg.printMsg('loop_Count : %d' %loop_Count)
       objMsg.printMsg('write_Loop : %d' %write_Loop)
       objMsg.printMsg('stepLBA : %d' %stepLBA)

       SATA_SetFeatures.enable_WriteCache()
       result = ICmd.FillBuffRandom(WBF)                                            #Fill Write Buffer with Random Data
       if result['LLRET'] != OK:
         if self.DEBUG:
             objMsg.printMsg('FillBuffRandom : %s' %str(result))
         ScrCmds.raiseException(11044, "Fill Random Pattern error")

       startLBA = 0;
       C1MB_to_LBA = int((1024 * 1024) / 512)
       C1MB = 1024 * 1024
       block_size = C1MB / 512
       write_Loop = 10

       for loop in range(loop_Count):
           targetLBA = int(self.max_LLB /2)                                            #Write to LBA (Max LBA/2) & verify (Max LBA/2).
           self.WriteRead(targetLBA, block_size, 'WC')

           targetLBA = int(self.max_LLB /2) + block_size                               #Write to LBA (Max LBA/2 + 1024Kb) & verify LBA (Max LBA/2 +1024Kbytes)

           self.WriteRead(targetLBA, block_size, 'WC')

           targetLBA = int(self.max_LLB /2) - block_size                               #Write to LBA (Max LBA/2 ? 1024Kb) & verify LBA (Max LBA/2 -1024Kbytes)
           self.WriteRead(targetLBA, block_size, 'WC')

           for i in range(0,write_Loop):
               targetLBA = int(self.max_LLB / 2 + C1MB_to_LBA)                         #Seek to random LBA in the range [(Max LBA/2 + 1024Kbytes) ? Max LBA]

               result = ICmd.RandomSeekTime(targetLBA, self.max_LLB, 10, seekType = 28, timeout = 600, exc=0)
               if self.DEBUG:
                     objMsg.printMsg('RandomSeekTime 2: %s' %str(result))

               if result['LLRET'] != OK:
                 ScrCmds.raiseException(11044, "Random Seek Error")

               targetLBA = int(self.max_LLB /2)                                        #Write to LBA (Max LBA/2) & verify (Max LBA/2).
               self.WriteRead(targetLBA, block_size, 'WC')

               targetLBA = int(self.max_LLB / 2)                                       #Seek to random LBA in the range [(Max LBA/2 + 1024Kbytes) ? Max LBA]

               result = ICmd.RandomSeekTime(0, targetLBA, 10, seekType = 28, timeout = 600, exc=0)
               if result['LLRET'] != OK:
                 if self.DEBUG:
                     objMsg.printMsg('Read B : %s' %str(result))
                 ScrCmds.raiseException(11044, "Random Seek Error")

               targetLBA = int(self.max_LLB /2)                                        #Write to LBA (Max LBA/2) & verify (Max LBA/2).
               self.WriteRead(targetLBA, block_size, 'W')

               targetLBA = int(self.max_LLB /2) + block_size                           #Read LBA (Max LBA/2 + 1024Kb)
               self.WriteRead(targetLBA, block_size, 'R')

               targetLBA = int(self.max_LLB /2) - block_size                           #Read LBA (Max LBA/2 ? 1024Kb)
               self.WriteRead(targetLBA, block_size, 'R')

       total_time = time.time() - starttime
       ScrCmds.insertHeader('Stressed Pinch Test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Stressed Pinch Test : END')

   def SimulateWorkLoadSIOPTest(self, mode = 'NONE'):
       ScrCmds.insertHeader('NetApp : Simulate WorkLoad SIOP Test %s : BEGIN' % mode)
       starttime = time.time()

       import random

       lba_size = TP.netapp_simulateWorkLoadSIOPTest['lba_size']
       run_time = TP.netapp_simulateWorkLoadSIOPTest['run_time']

       if testSwitch.virtualRun:
           run_time = 5

       if self.DEBUG:
           objMsg.printMsg('lba_size : %d' %lba_size)
           objMsg.printMsg('run_time : %d' %run_time)

       while(True):
           loop_random = random.randrange(1,100)
           for i in range(loop_random):
               if mode == 'FILE_SERVER':
                  random_value = random.random()
                  startLBA = 0
                  targetLBA = 0
                  stepLBA = 0
                  lba_count = 0

                  if random <= 0.1:                                               #random location
                     startLBA = int(random.randrange(int(self.max_LLB *0.01)), int(self.max_LLB))

                  elif random <=(0.1 + 0.3):
                     startLBA = int(random.randrange(int(self.max_LLB *0.3), int(self.max_LLB *0.6)))

                  else:
                     startLBA = int(random.randrange(int(self.max_LLB *0), int(self.max_LLB *0.1)))

                  random_value = random.random()

                  if random <= 0.3:                                               #random transfer size
                     lba_count = int(random.randrange(int(2 * (1024 /lba_size)), int(32 * 1024/ lba_size)))        #2KB - 32Kb

                  else:
                     lba_count = int(random.randrange(int(32 * 1024/lba_size),  int(128 * 1024/ lba_size)))      #32KB - 128Kb

                  random_value = random.random()

                  if random <= 0.2:                                               #random RW mode. Read:Write ratio of 4:1
                     result = ICmd.WriteSectors(startLBA, lba_count)
                     if self.DEBUG:
                        objMsg.printMsg('WriteSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                     if result['LLRET'] != OK:
                        ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Write Failed %s" % str(result))

                  else:
                     result = ICmd.ReadSectors(startLBA, lba_count)
                     if self.DEBUG:
                        objMsg.printMsg('ReadSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                     if result['LLRET'] != OK:
                        ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Read Failed %s" % str(result))

               elif mode == 'OLTP':

                  random_value = random.random()
                  startLBA = 0
                  targetLBA = 0
                  stepLBA = 0
                  lba_count = 0

                  if random <= 0.2:                                               #random location
                     startLBA = int(random.randrange(int(self.max_LLB *0.01), int(self.max_LLB)))

                  elif random <=(0.2 + 0.3):
                     startLBA = int(random.randrange(int(self.max_LLB *0.1), int(self.max_LLB *0.3)))

                  else:
                     startLBA = int(random.randrange(int(self.max_LLB * 0.3), int(self.max_LLB *0.6)))

                  random_value = random.random()

                  if random <= 0.3:                                               #random transfer size
                     lba_count = int(random.randrange( int(4 * 1024/ lba_size),  int(8 * 1024/ lba_size)))        #4KB - 8Kb

                  else:
                     lba_count = int(random.randrange( int(1 * 1024/ lba_size),  int(4 * 1024/ lba_size)))          #1KB - 4Kb

                  random_value = random.random()

                  if random <= 0.2:                                               #random RW mode
                     result = ICmd.WriteSectors(startLBA, lba_count)
                     if self.DEBUG:
                        objMsg.printMsg('WriteSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                     if result['LLRET'] != OK:
                        ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Write Failed %s" % str(result))

                  else:
                     result = ICmd.ReadSectors(startLBA, lba_count)

                     if self.DEBUG:
                        objMsg.printMsg('ReadSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                     if result['LLRET'] != OK:
                        ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Read Failed %s" % str(result))

           pause_time = random.randrange(1, 10)

           if not testSwitch.virtualRun:
              ScriptPause(pause_time)

           if((time.time() - starttime) > run_time):
               break

           if(self.DEBUG):
               objMsg.printMsg('SimulateWorkLoadSIOPTestt random %s Loop : %d, Time : %d' % (mode,i, (time.time() - starttime)))

       total_time = time.time() - starttime
       ScrCmds.insertHeader('Simulate WorkLoad SIOP  %s Time Usage : %d' % (mode, total_time))
       ScrCmds.insertHeader('NetApp : Simulate WorkLoad SIOP Test %s : END' % mode)

   def DataErasureTest(self):
       ScrCmds.insertHeader('NetApp : Data Erasure Test : BEGIN')
       starttime = time.time()

       lba_size = TP.netapp_dataErasureTest['lba_size']
       data_size = int((TP.netapp_dataErasureTest['data_size'] / 4) * self.dut.imaxHead)                            #2GB Data Size
       loop_Count = TP.netapp_dataErasureTest['loop_Count']
       pattern_count  = TP.netapp_dataErasureTest['pattern_count']

       result = ICmd.SetFeatures(0x03, 0x47)                                        # Set DMA Mode UDMA 7 (UDMA150)
       if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,'Set DMA Mode UDMA 7 Failed! : %s' % str(result))
       else:
            objMsg.printMsg('Set DMA Mode UDMA 7  : %s' % str(result))

       SATA_SetFeatures.enable_WriteCache()

       if testSwitch.virtualRun:
          loop_Count = 1
          pattern_count = 1

       for i in range(loop_Count):
           for pattern in range(pattern_count):
                                                                                    #Fill Write Buffer with (Random , Incremental, Shifting bit, Counting):
              if pattern == 0 :                                                     #Fill Write Buffer with (Incremental, Shifting bit, Counting,Random )
                 self.fillRandomBuff()

              if pattern == 1 :
                 self.fillIncrementalBuff()

              if pattern == 2 :
                 self.fillShiftingBitBuff()

              if pattern == 3 :
                 self.fillCountingBuff()

              targetLBA =  int(self.max_LLB * 0.02)                                                #OD : 2% from OD
              self.ErasureTest(targetLBA,data_size,lba_size)

              targetLBA =  int(self.max_LLB * 0.5)                                                 #OD : 50% of total LBA
              self.ErasureTest(targetLBA,data_size,lba_size)

              targetLBA =  int(self.max_LLB * 0.98)                                                #ID : 2% from ID
              self.ErasureTest(targetLBA,data_size,lba_size)

       total_time = time.time() - starttime
       ScrCmds.insertHeader('Data Erasure Test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Data Erasure Test : END')

   def DataErasureTest2_CHS(self):
       ScrCmds.insertHeader('NetApp : Data Erasure Test 2 : BEGIN')
       sptCmds.enableDiags()
       starttime = time.time()

       lba_size = TP.netapp_dataErasureTest2['lba_size']
       loop_Count = TP.netapp_dataErasureTest2['loop_Count']
       loop_Write = TP.netapp_dataErasureTest2['loop_Write']

       for cur_hd in range(self.dut.imaxHead):
            od_cylinder = self.zones[cur_hd][0]
            md_cylinder = self.zones[cur_hd][int(self.dut.numZones / 2)]
            id_cylinder = self.zones[cur_hd][int(self.dut.numZones - 1)] - 1

            if testSwitch.FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK:
               for retry in range(3):
                  try:
                     objMsg.printMsg('DataErasureTest2 Test Head %d ' % cur_hd)
                     sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                    #Fill random pattern

                     #write 1MB data to center of surface
                     sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space
                     sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
                     sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     #Write/Read 1000 loops using diagnostic batch file
                     objMsg.printMsg('DataErasureTest2 Test Read/Write %d loops ' % loop_Write)
                     sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                       #Start Batch File
                     sptCmds.sendDiagCmd('*7,%x,1'% 2,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)              #Set Loop Count 1 to 10000
                     sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                        #Batch File Label - Label 2

                     sptCmds.sendDiagCmd('/2A8,%x,,%x' % (md_cylinder + 1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)         #Set Test Space
                     sptCmds.sendDiagCmd('/2A9,%x,,%x' % (id_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #From Mid +1 to Extreme ID
                     sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
                     sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
                     sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

                     sptCmds.sendDiagCmd('/2A8,%x,,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #Set Test Space
                     sptCmds.sendDiagCmd('/2A9,%x,,%x' % (md_cylinder -1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #From OD to MD
                     sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
                     sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
                     sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

                     sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                    #Decrement Loop Count 1 and Branch to Label 2 if not 0
                     sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                           #End Batch File
                     sptCmds.sendDiagCmd('B,0',timeout = 2400,printResult = False, raiseException = 1, stopOnError = False)                                        #Run Batch File

                     sptCmds.sendDiagCmd('/2AD',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Reset Test Space
                     sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Set Test Space
                     sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 30, printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Read Verify 1 track
                     break

                  except Exception, e:
                     if e[0][2] == 13426:
                        objMsg.printMsg('Fail from invalid track retry on next 100 track')
                        objMsg.printMsg('Retry at loop %d'%(retry+1))
                        od_cylinder +=100
                        md_cylinder +=100
                        id_cylinder -=100
                     else:
                        raise
            else:
               objMsg.printMsg('DataErasureTest2 Test Head %d ' % cur_hd)
               sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                    #Fill random pattern

               #write 1MB data to center of surface
               sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space
               sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
               sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               #Write/Read 1000 loops using diagnostic batch file
               objMsg.printMsg('DataErasureTest2 Test Read/Write %d loops ' % loop_Write)
               sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                       #Start Batch File
               sptCmds.sendDiagCmd('*7,%x,1'% 2,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)              #Set Loop Count 1 to 10000
               sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                        #Batch File Label - Label 2

               sptCmds.sendDiagCmd('/2A8,%x,,%x' % (md_cylinder + 1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)         #Set Test Space
               sptCmds.sendDiagCmd('/2A9,%x,,%x' % (id_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #From Mid +1 to Extreme ID
               sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
               sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
               sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

               sptCmds.sendDiagCmd('/2A8,%x,,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #Set Test Space
               sptCmds.sendDiagCmd('/2A9,%x,,%x' % (md_cylinder -1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #From OD to MD
               sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
               sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
               sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

               sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                    #Decrement Loop Count 1 and Branch to Label 2 if not 0
               sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                           #End Batch File
               sptCmds.sendDiagCmd('B,0',timeout = 2400,printResult = False, raiseException = 1, stopOnError = False)                                        #Run Batch File

               sptCmds.sendDiagCmd('/2AD',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Reset Test Space
               sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Set Test Space
               sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 30, printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Read Verify 1 track

       total_time = time.time() - starttime
       sptCmds.enableESLIP()
       ScrCmds.insertHeader('Data Erasure Test 2 Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Data Erasure Test 2 : END')

   def ErasureTest(self,targetLBA, blockSize,lba_size):
       step_lba = sector_size = 256
       loopCount = 10000

       if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
          sta_LLB = int(targetLBA)
          sta3 = int((sta_LLB & 0xFFFF000000000000) >> 48)
          sta2 = int((sta_LLB & 0x0000FFFF00000000) >> 32)
          sta1 = int((sta_LLB & 0x00000000FFFF0000) >> 16)
          sta0 = int((sta_LLB & 0x000000000000FFFF))

          end_LLB = int(targetLBA+ blockSize)
          end3 = int((end_LLB & 0xFFFF000000000000) >> 48)
          end2 = int((end_LLB & 0x0000FFFF00000000) >> 32)
          end1 = int((end_LLB & 0x00000000FFFF0000) >> 16)
          end0 = int((end_LLB & 0x000000000000FFFF))

          tot_blks_to_xfr = int(blockSize)
          tot1 = int((tot_blks_to_xfr & 0x00000000FFFF0000) >> 16)
          tot0 = int((tot_blks_to_xfr & 0x000000000000FFFF))

          objMsg.printMsg('Sequential : sta_LLB=%s, end_LLB=%s, tot_blks_to_xfr=%s, sta3=%s, sta2=%s, sta1=%s, sta0=%s, end3=%s, end2=%s, end1=%s, end0=%s, tot1=%s, tot0=%s'\
                        %(sta_LLB,end_LLB,tot_blks_to_xfr,sta3,sta2,sta1,sta0,end3,end2,end1,end0,tot1,tot0))

       result = ICmd.Seek(targetLBA)      # Seek to LBA 0
       if result['LLRET'] != OK:
           objMsg.printMsg('Seek cmd Failed!')

       if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
          ICmd.St(TP.prm_638_Unlock_Seagate)
          ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialWrite',CTRL_WORD1=(0x22),STARTING_LBA=(sta3,sta2,sta1,sta0),MAXIMUM_LBA =(end3,end2,end1,end0),TOTAL_BLKS_TO_XFR =(tot1,tot0))
       else:
          result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_size)
          if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,'SequentialWriteDMAExt Failed! : %s' % str(result))
          else:
             if self.DEBUG:
                objMsg.printMsg('Write Data Complete! : %s' % str(result))

       result = ICmd.RandomSeekTime(targetLBA, targetLBA + (self.max_LLB * 0.02 ), loopCount)  #Random Seek 10000 times ;targetLBA + 2G + 2%
       if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Random Seek Error : %s" % str(result))
       else:
          if self.DEBUG:
             objMsg.printMsg('Random Seek ! : %s' % str(result))

       result = ICmd.BufferCopy(RBF,0,WBF,0,512)
       if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,'BufferCopy Failed! : %s' % str(result))

       Compare = 1
       if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
          ICmd.St(TP.prm_638_Unlock_Seagate)
          ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialReadVer',CTRL_WORD1=(0x42),STARTING_LBA=(sta3,sta2,sta1,sta0),MAXIMUM_LBA =(end3,end2,end1,end0),TOTAL_BLKS_TO_XFR =(tot1,tot0))
       else:
         result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_size)
         if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,'SequentialReadVerifyExt Failed! : %s' % str(result))
         else:
             if self.DEBUG:
               objMsg.printMsg('Read Verify Data Complete! ! : %s' % str(result))


   def AdjacentPinch_CHS(self):
       ScrCmds.insertHeader('NetApp : Adjacent Pinch : BEGIN')
       sptCmds.enableDiags()
       starttime = time.time()

       lba_size = TP.netapp_adjacentPinch['lba_size']
       loop_Count = TP.netapp_adjacentPinch['loop_Count']
       loop_Write = TP.netapp_adjacentPinch['loop_Write']
       C1MB_to_LBA = int((1024 * 1024) / lba_size)
       blockSize = (1024 * 1024 / lba_size)                                          #1M Block Size

       if self.DEBUG:
           objMsg.printMsg('loop_Count : %d' %loop_Count)
           objMsg.printMsg('loop_Write : %d' %loop_Write)
           objMsg.printMsg('C1MB_to_LBA : %d, blockSize : %d, lba_size : %d' % (C1MB_to_LBA, blockSize, lba_size))

       if testSwitch.virtualRun:
          loop_Count = 1
          loop_Write = 1

       sector = 0
       for i in range(loop_Count):
          for cur_hd in range(self.dut.imaxHead):
              #objMsg.printMsg('AdjacentPinch OD Test Head : %d' % cur_hd)

              od_cylinder = self.zones[cur_hd][0]
              md_cylinder = self.zones[cur_hd][int(self.dut.numZones / 2)]
              id_cylinder = self.zones[cur_hd][int(self.dut.numZones -1 )] -1

              if testSwitch.FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK:
               for retry in range(3):
                objMsg.printMsg('AdjacentPinch OD Test Head : %d' % cur_hd)
                try:
                   sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
                   sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

                   sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
                   sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
                   sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
                   sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                   #Write/Read 1000 loops using diagnostic batch file

                   objMsg.printMsg('AdjacentPinch OD Test Read/Write %d loops ' % loop_Write)
                   sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
                   sptCmds.sendDiagCmd('*7,%x,1' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
                   sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

                   sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
                   sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
                   sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
                   sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
                   sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
                   sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

                   break
                except Exception, e:
                   if e[0][2] == 13426:
                      objMsg.printMsg('Fail from invalid track retry on next 100 track')
                      objMsg.printMsg('Retry at loop %d'%(retry+1))
                      od_cylinder += 100
                   else:
                      raise

               for retry in range(3):
                try:
                   objMsg.printMsg('AdjacentPinch ID Test Head : %d' % cur_hd)

                   sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
                   sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

                   sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
                   sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
                   sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
                   sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                   #Write/Read 1000 loops using diagnostic batch file

                   objMsg.printMsg('AdjacentPinch ID Test Read/Write 1000 loops ')
                   sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
                   sptCmds.sendDiagCmd('*7,%x,1'%loop_Write,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
                   sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

                   sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
                   sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
                   sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
                   sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
                   sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
                   sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

                   break
                except Exception, e:
                   if e[0][2] == 13426:
                      objMsg.printMsg('Fail from invalid track retry on next 100 track')
                      objMsg.printMsg('Retry at loop %d'%(retry+1))
                      id_cylinder -=100
                   else:
                      raise
              else:
               objMsg.printMsg('AdjacentPinch OD Test Head : %d' % cur_hd)

               sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
               sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               #Write/Read 1000 loops using diagnostic batch file

               objMsg.printMsg('AdjacentPinch OD Test Read/Write %d loops ' % loop_Write)
               sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
               sptCmds.sendDiagCmd('*7,%x,1' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
               sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
               sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
               sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

               objMsg.printMsg('AdjacentPinch ID Test Head : %d' % cur_hd)

               sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
               sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               #Write/Read 1000 loops using diagnostic batch file

               objMsg.printMsg('AdjacentPinch ID Test Read/Write 1000 loops ')
               sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
               sptCmds.sendDiagCmd('*7,%x,1'%loop_Write,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
               sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
               sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
               sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

       total_time = time.time() - starttime
       sptCmds.enableESLIP()
       ScrCmds.insertHeader('Adjacent Pinch Test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Adjacent Pinch Test : END')


   def WriteRead(self,targetLBA, blockSize, mode = 'NONE'):
       Compare = 0;
       Stamp = 0
       test_loop = 1
       sector_count = step_lba = 256
       if mode.find('C') >= 0:
          Compare = 1

       if mode.find('W')>= 0:
          if self.DEBUG:
              objMsg.printMsg('SequentialWriteVerify : startLBA : %d,  endLBA: %d,, Stamp : %d, Compare : %d, test_loop : %d ' % (targetLBA, (targetLBA+ blockSize),Stamp, Compare, test_loop))

          result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)                               #write 1

          if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,'SequentialWriteDMAExt Failed! : %s' % str(result))

       if mode.find('R') >= 0:
          if self.DEBUG:
              objMsg.printMsg('SequentialReadVerifyExt : startLBA : %d,  endLBA: %d, Stamp : %d, Compare : %d, test_loop : %d ' % (targetLBA, (targetLBA+ blockSize),Stamp, Compare, test_loop))

          result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)                           #read

          if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,"SequentialReadVerifyExt Failed: %s" % str(result))

   def WriteRead_CHS(self, cylinder, head, sector, blockSize, mode = 'NONE'):
       Compare = 0;
       Stamp = 0
       test_loop = 1
       step_Cylinder = 1
       step_Head = 1
       step_Sector = 256
       verify_msg = ""
       if mode.find('C') >= 0:
          Compare = 1
          verify_msg = "Verify"

       if mode.find('W')>= 0:
          if self.DEBUG:
              msg = 'SequentialWrite%s  cylinder : %d,  head: %d, sector : %d, sector_cnt : %d ' % (verify_msg, cylinder, head, sector, sector+blockSize)

          if(Compare):
               result = ICmd.SequentialWriteVerify(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)
          else:
               result = ICmd.SequentialWriteDMA(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)

          if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,'Sequential Write Failed! : %s' % str(result))

       if mode.find('R') >= 0:
          if self.DEBUG:
              msg = ('SequentialRead%s  cylinder : %d,  head: %d, sector : %d, sector_cnt : %d ' % (verify_msg, cylinder, head, sector, sector+blockSize))

          if(Compare):
               result = ICmd.SequentialReadVerify(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)
          else:
               result = ICmd.SequentialReadDMA(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)

          if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,"SequentialReadDMA Failed: %s" % str(result))

       if self.DEBUG:
              objMsg.printMsg('WriteRead_CHS Result : %s : %s' % (str(result), msg))

   def fillIncrementalBuff(self):
       result = ICmd.FillBuffInc(WBF)
       if result['LLRET'] != OK:
          ScrCmds.raiseException(10888, "Fill Incremental Buffer Error")

       objMsg.printMsg('Fill Incremental Buffer Complete.')

   def fillRandomBuff(self):
       result = ICmd.FillBuffRandom(WBF)
       if result['LLRET'] != OK:
          ScrCmds.raiseException(10888, "Fill Random Buffer Error")

       objMsg.printMsg('Fill Random Buffer Complete.')

   def fillShiftingBitBuff(self):
       import array
       data_pattern = array.array('H')

       data  = 0xFFFF
       increment = False
       for i in xrange(0,0x20000 / 2, 2):
                                                            #Prepare Shifting Bit Pattern (Total Buffer Size = 0x20000 byte)
          if (increment) :
              data = data + 1
          else:
              data = data -1

          if data == 0xFFFF or data == 0:
              increment = not increment

          data_pattern.insert(i, 0)
          data_pattern.insert(i + 1, data & 0xFFFF)

       write_buffer = ''.join([(chr(num >>8) + chr(num & 0xff)) for num in (data_pattern)])
       result = ICmd.FillBuffer(WBF,0,write_buffer)
       if result['LLRET'] != OK:
          ScrCmds.raiseException(10888, "Fill Shifting Bit Buffer Error")

       objMsg.printMsg('Fill Shifting Bit Buffer Complete.')

   def fillCountingBuff(self):
       import array
       data_pattern = array.array('H')

       init_value  = 0xFFFF
       for i in xrange(0,0x20000 / 2):                                                 #Prepare Counting Pattern (Total Buffer Size = 0x20000 byte)
          data = i
          data = data << 8
          data = data | (i + 1)
          data_pattern.insert(i + 1, data & 0xFFFF)

       write_buffer = ''.join([(chr(num >>8) + chr(num & 0xff)) for num in (data_pattern)])
       result = ICmd.FillBuffer(WBF,0,write_buffer)
       if result['LLRET'] != OK:
          ScrCmds.raiseException(10888, "Fill Counting Buffer Error")

       objMsg.printMsg('Fill Counting Buffer Complete.')

   def getBasicDriveInfo(self):
       self.oSerial.enableDiags()
       self.numCyls,self.zones = self.oSerial.getZoneInfo(printResult=True)

       objMsg.printMsg("Total cylinder %s" % str(self.numCyls) )
       objMsg.printMsg("Zone %s" % str(self.zones) )

       objMsg.printMsg("Max Hd %s" % str(self.dut.imaxHead) )
       objMsg.printMsg("Num Zone %s" % str(self.dut.numZones) )

   def  ShortTest(self):
        pass

###########################################################################################################
class CMuskieRWKMQM(CState):
   """
   Korat Rework MQM
      1. Full Seek test Time Usage
      2. Static Data Compare Test using DRAM Screen Time Usage
      3. Data Compare SIOP Test Time Usage
      4. Butterfly Write Time Usage
      5. System Ready Test Time Usage
      6. Banded Sequential Write/Read Compare Test Time Usage
      7. Stressed Pinch Test Time Usage
      8. Simulate WorkLoad SIOP  OLTP Time Usage
      9. Simulate WorkLoad SIOP  FILE_SERVER Time Usage
      10.Adjacent Pinch Test Time Usage
      11.Data Erasure Test Time Usage
      12.Data Erasure Test 2 Time Usage
      13.Butterfly write in OD
      14.Butterfly write in MD
      15.Butterfly write in ID
      16.Verify Disk Test Time Usage
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProcess = CProcess()
      from serialScreen import sptDiagCmds
      self.oSerial = sptDiagCmds()
      from ICmdFactory import ICmd

      self.oUtility = CUtility()

      import string,time,sys

      self.DEBUG = 0

      if 1:
         self.dut.driveattr['KT_RWK_MQM'] = 'FAIL'
         self.getBasicDriveInfo()
         #temp 25
         self.PowerCycleTest()
         self.Intialization()

         ret = CIdentifyDevice().ID
         self.max_LLB = ret['IDDefaultLBAs'] - 1 # default for 28-bit LBA

         if ret['IDCommandSet5'] & 0x400:      # check bit 10
            objMsg.printMsg('Get ID Data 48 bit LBA is supported')
            self.max_LLB = ret['IDDefault48bitLBAs'] - 1

         if self.DEBUG:
           objMsg.printMsg('CIdentifyDevice data : %s' %str(ret))

         if self.max_LLB <= 0:
            self.max_LLB = 976773167
            objMsg.printMsg("Assign max_LLB to default : %d", self.max_LLB)

         objMsg.printMsg("The Maximum User LBA is : %08X       Drive Capacity - %dGB" %(self.max_LLB,(( self.max_LLB * 512 )/1000000000),))


         self.SeekTest_CHS()
         self.PowerCycleTest()
         self.Intialization()

         self.StaticDataCompareTest()
         self.DataCompareSIOPTest()
         self.ButterflyWriteTest()
         self.SystemReadyTest(3)
         self.BandSeqRWCmpTest()

         self.PowerCycleTest()
         self.Intialization()

         self.StressedPinchTest()
         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')
         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')
         self.AdjacentPinch_CHS()
         self.DataErasureTest()

         self.PowerCycleTest()
         self.Intialization()

         self.DataErasureTest2_CHS()

         self.PowerCycleTest()
         self.Intialization()

         self.ButterflyIn(run_time = 3600, WR_MODE = 'Write', START_LBA = 'OD')
         self.ButterflyIn(run_time = 3600, WR_MODE = 'Write', START_LBA = 'MD')
         self.ButterflyIn(run_time = 3600, WR_MODE = 'Write', START_LBA = 'ID')

         self.PowerCycleTest()
         self.Intialization()
         self.VerifyDiskTest()

         self.dut.driveattr['KT_RWK_MQM'] = 'PASS'


   def PowerCycleTest(self):
       ScrCmds.insertHeader('Power Cycle')
       objPwrCtrl.powerCycle(offTime=20, onTime=35, ataReadyCheck = True)

   def Intialization(self):
       ScrCmds.insertHeader("Unlock Seagate")
       try:
         ICmd.UnlockFactoryCmds()
       except:
         self.PowerCycleTest()

   def SeekTest_CHS(self,):
       #Now we don't put any spec in this test
       ScrCmds.insertHeader('NetApp : Full Seek test : BEGIN')
       sptCmds.enableDiags()
       starttime = time.time()

       seekType = int(TP.netapp_seekTest['seek_type'])
       loop_Seek = int(TP.netapp_seekTest['loop_Seek'])
       loop_Test = int(TP.netapp_seekTest['loop_Test'])

       objMsg.printMsg('SeekTest : seek_type : %d' % seekType)
       objMsg.printMsg('SeekTest : loop_Test : %d' % loop_Test)

       if testSwitch.virtualRun:
          loop_Seek  = 1;

       for i in range(loop_Test):
          for cur_hd in range(self.dut.imaxHead):
              objMsg.printMsg('NetApp Full Stroke Seek Head : %d' % cur_hd)
              sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                         #Set Test Space
              self.oSerial.gotoLevel('2')
              sptCmds.sendDiagCmd('S0,%x' % cur_hd,timeout = 30, printResult = False, raiseException = 0, stopOnError = False)              #Seek to test head
              self.oSerial.gotoLevel('3')
              sptCmds.sendDiagCmd('D999999999,2,5000',timeout = 300, printResult = True, raiseException = 0, stopOnError = False)    #Perform full strok seek

              objMsg.printMsg('NetApp Random Seek Head : %d' % cur_hd)
              sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                         #Set Test Space
              self.oSerial.gotoLevel('2')
              sptCmds.sendDiagCmd('S0,%x'% cur_hd,timeout = 30, printResult = False, raiseException = 0, stopOnError = False)              #Seek to test head
              self.oSerial.gotoLevel('3')
              sptCmds.sendDiagCmd('D0,%x,%x'%(seekType,loop_Seek),timeout = 300, printResult = True, raiseException = 0, stopOnError = False)            #Perform random seek

              if(self.DEBUG):
                  objMsg.printMsg('SeekTest Head : %d, Time : %d' % (cur_hd, (time.time() - starttime)))

       total_time = time.time() - starttime
       sptCmds.enableESLIP()
       ScrCmds.insertHeader('Full Seek test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Full Seek test : END')

   def StaticDataCompareTest(self):
       ScrCmds.insertHeader('NetApp : Static Data Compare Test using DRAM Screen : BEGIN')
       starttime = time.time()

       TP.prm_DRamSettings.update({"StartLBA":0})                       #Target Write LBA : Start
       TP.prm_DRamSettings.update({"EndLBA":32})                        #Target Write LBA : End
       TP.prm_DRamSettings.update({"StepCount":32})                     #StepCount : 32LBA
       TP.prm_DRamSettings.update({"SectorCount":32})                   #SectorCount: 32LBA
       from DRamScreen import CDRamScreenTest
       oDRamScreen = CDRamScreenTest(self.dut)

       loop_Count = int(TP.netapp_staticDataCompare['loop_Count'])
       delay_time = int(TP.netapp_staticDataCompare['delay_time'])

       if testSwitch.virtualRun:
            loop_Count = 10
            delay_time = 0

       if(self.DEBUG):
           objMsg.printMsg('StaticDataCompareTest : loop_Count %d' % loop_Count)

       for i in range(loop_Count):
            oDRamScreen.dRamScreenTest()

            time.sleep(delay_time)

            if(self.DEBUG):
               objMsg.printMsg('StaticDataCompareTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

       total_time = time.time() - starttime
       ScrCmds.insertHeader('Static Data Compare Test using DRAM Screen Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Static Data Compare Test using DRAM Screen : END')

   def ButterflyIn(self, run_time = 60, WR_MODE = 'Write', loops = 1, START_LBA = 'OD'):

      objMsg.printMsg('Butterfly In %s %d loops start'%(WR_MODE,loops))
      if WR_MODE == 'Write':
         prm_510_CWORD1 = (0x0422)
      elif WR_MODE == 'Read':
         prm_510_CWORD1 = (0x0412)
      else:
         ScrCmds.raiseException(11044, "Invalid butterfly write read parameter")

      xLBA = self.max_LLB/5
      if START_LBA == 'OD':
         START_LBA = 0
         MAX_LBA = self.max_LLB
      elif START_LBA == 'MD':
         START_LBA = xLBA
         MAX_LBA = self.max_LLB - xLBA
      elif START_LBA == 'ID':
         START_LBA = xLBA*2
         MAX_LBA = self.max_LLB - xLBA*2
      else:
         ScrCmds.raiseException(11044, "Invalid butterfly starting LBA parameter")

      (str_3, str_2, str_1, str_0) = self.oUtility.returnStartLbaWords(START_LBA)
      (max_3, max_2, max_1, max_0) = self.oUtility.returnStartLbaWords(MAX_LBA)
      prm_506_Timed = {
         'test_num'          : 506,
         'prm_name'          : "prm_506_Timed",
         'spc_id'            :  1,
         "TEST_RUN_TIME"     :  run_time,
      }

      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         prm_510_ButterflyIn = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_ButterflyIn",
            'spc_id'            :  1,
            "CTRL_WORD1"        :  prm_510_CWORD1,               #Butterfly Sequencetioal Write or Read, Display Location of errors
            "STARTING_LBA"      : (str_3, str_2, str_1, str_0),
            "MAXIMUM_LBA"       : (max_3, max_2, max_1, max_0),
            "BLKS_PER_XFR"      : (0x10),                        #0x10 block per xfer same as SAS
            "OPTIONS"           : 0,                             #Converging
            "timeout"           :  6000,
            "MAX_NBR_ERRORS"    : 0,
         }
      else:
         prm_510_ButterflyIn = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_ButterflyIn",
            'spc_id'            :  1,
            "CTRL_WORD1"        :  prm_510_CWORD1,               #Butterfly Sequencetioal Write or Read, Display Location of errors
            "STARTING_LBA"      : (str_3, str_2, str_1, str_0),
            "MAXIMUM_LBA"       : (max_3, max_2, max_1, max_0),
            "BLKS_PER_XFR"      : (0x10),                        #0x10 block per xfer same as SAS
            "OPTIONS"           : 0,                             #Converging
            "retryECList"       : [14016,14029],
            "retryMode"         : POWER_CYCLE_RETRY,
            "retryCount"        : 2,
            "timeout"           :  6000,
            "MAX_NBR_ERRORS"    : 0,
         }

      prm_506_DefaultTimed = {
         'test_num'          : 506,
         'prm_name'          : "prm_506_DefaultTimed",
         'spc_id'            :  1,
         "TEST_RUN_TIME"     :  0,
      }
      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         for i in range(loops):
            objMsg.printMsg('Perform butterfly In %s loop %d'%(WR_MODE,loops+1))
            failed = 1
            retry = 0
            while failed == 1 and retry <= TP.maxRetries_T510Butterfly:
               try:
                  ICmd.St(prm_506_Timed)
                  ICmd.St(prm_510_ButterflyIn)
                  failed = 0
                  ICmd.St(prm_506_DefaultTimed)
               except ScriptTestFailure, (failureData):
                  ec = failureData[0][2]
                  if ec in [14016, 14029] and retry < TP.maxRetries_T510Butterfly:
                     objPwrCtrl.powerCycle(5000,12000,10,30)
                     retry += 1
                  else:
                     raise
            objPwrCtrl.powerCycle(5000,12000,10,30)
      else:
         for i in range(loops):
            objMsg.printMsg('Perform butterfly In %s loop %d'%(WR_MODE,loops+1))
            ICmd.St(prm_506_Timed)
            ICmd.St(prm_510_ButterflyIn)
            ICmd.St(prm_506_DefaultTimed)
            objPwrCtrl.powerCycle(5000,12000,10,30)

      objMsg.printMsg('Butterfly In %s %d loops complete'%(WR_MODE,loops))

   def ButterflyWriteTest(self):
      ScrCmds.insertHeader('NetApp : Butterfly Write Test : BEGIN')
      starttime = time.time()

      loop_count = loop_Count = int(TP.netapp_butterflyWriteTest['loop_Count'])
      step_rate = TP.netapp_butterflyWriteTest['step_rate']
      lba_size = TP.netapp_butterflyWriteTest['lba_size']
      run_time = int(TP.netapp_butterflyWriteTest['run_time']/ 4 * self.dut.imaxHead)

      block_size = 1024*32/lba_size
      (block_size_MSBs, block_size_LSBs) = self.UpperLower(block_size)

      objMsg.printMsg('loop_count : %d' %loop_count)
      objMsg.printMsg('step_rate : %d' %step_rate)
      objMsg.printMsg('run_time : %d Mins' %(run_time / 60))

      prm_506_SET_RUNTIME = {
         'test_num'          : 506,
         'prm_name'          : "prm_506_SET_RUNTIME",
         'spc_id'            :  1,
         "TEST_RUN_TIME"     :  run_time,
      }
      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         prm_510_BUTTERFLY = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_BUTTERFLY",
            'spc_id'            :  1,
            "CTRL_WORD1"        : (0x0422),                                        #Butterfly Sequencetioal Write;Display Location of errors
            "STARTING_LBA"      : (0,0,0,0),
            "BLKS_PER_XFR"      : (step_rate * block_size),                        #Need 32K write and seek 5*32K step, but cannot do that only write 5*32K.
            "OPTIONS"           : 0,                                               #Butterfly Converging
            "timeout"           :  3000,                                           #15 Mins Test Time
         }
      else:
         prm_510_BUTTERFLY = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_BUTTERFLY",
            'spc_id'            :  1,
            "CTRL_WORD1"        : (0x0422),                                        #Butterfly Sequencetioal Write;Display Location of errors
            "STARTING_LBA"      : (0,0,0,0),
            "BLKS_PER_XFR"      : (step_rate * block_size),                        #Need 32K write and seek 5*32K step, but cannot do that only write 5*32K.
            "OPTIONS"           : 0,                                               #Butterfly Converging
            "retryECList"       : [14016,14029],
            "retryMode"         : POWER_CYCLE_RETRY,
            "retryCount"        : 2,
            "timeout"           :  3000,                                           #15 Mins Test Time
         }

      numGB = (self.max_LLB * lba_size ) / (10**9)
      ScriptComment("The Maximum LBA is : %08X Drive Capacity - %dGB" %(self.max_LLB, numGB,))

      (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0) = self.oUtility.returnStartLbaWords(self.max_LLB - 1)

      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         for i in xrange(loop_count):
             failed = 1
             retry = 0
             while failed == 1 and retry <= TP.maxRetries_T510Butterfly:
               try:
                  ICmd.St(
                        prm_506_SET_RUNTIME,
                     )

                  ICmd.St(
                        prm_510_BUTTERFLY,
                        STARTING_LBA = (0, 0, 0, 0),
                        MAXIMUM_LBA  = (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0),
                     )
                  failed = 0

                  ICmd.St(
                        prm_506_SET_RUNTIME,TEST_RUN_TIME = 0,
                     )
               except ScriptTestFailure, (failureData):
                  ec = failureData[0][2]
                  if ec in [14016, 14029] and retry < TP.maxRetries_T510Butterfly:
                     objPwrCtrl.powerCycle(5000,12000,10,30)
                     retry += 1
                  else:
                     raise

             if(self.DEBUG):
               objMsg.printMsg('ButterflyWriteTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))
      else:
         for i in xrange(loop_count):
             ICmd.St(
                   prm_506_SET_RUNTIME,
                )

             ICmd.St(
                   prm_510_BUTTERFLY,
                   STARTING_LBA = (0, 0, 0, 0),
                   MAXIMUM_LBA  = (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0),
                )

             ICmd.St(
                   prm_506_SET_RUNTIME,TEST_RUN_TIME = 0,
                )

             if(self.DEBUG):
               objMsg.printMsg('ButterflyWriteTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

      total_time = time.time() - starttime
      ScrCmds.insertHeader('Butterfly Write Time Usage : %d' % total_time)
      ScrCmds.insertHeader('NetApp : Butterfly Write Test : END')

   def UpperLower(self, FourByteNum):
       FourByteNum = FourByteNum & 0xFFFFFFFF                                   #chop off any more than 4 bytes
       MSBs = FourByteNum >> 16
       LSBs = FourByteNum & 0xFFFF
       return (MSBs, LSBs)

   def SystemReadyTest(self, power_cycle_count = 3):
       ScrCmds.insertHeader('NetApp : System Ready Test : BEGIN')
       starttime = time.time()

       for i in range(1,power_cycle_count +1):
           objMsg.printMsg("Power Cycle %d"% i)
           self.PowerCycleTest();

           time.sleep(90)

       total_time = time.time() - starttime
       ScrCmds.insertHeader('System Ready Test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : System Ready Test : END')

   def VerifyDiskTest(self):
       ScrCmds.insertHeader('NetApp : Verify Disk Test : BEGIN')
       stepLBA = sctCnt = 256 # 48bit LBA addressing
       starttime = time.time()

       if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
         ICmd.St(TP.prm_638_Unlock_Seagate)
         ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialRead')
       else:
         result = ICmd.SequentialReadDMAExt(0, self.max_LLB, stepLBA, sctCnt)
         objMsg.printMsg('Full Pack Read - Result %s' %str(result))

         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,"Full Pack Zero Read Failed : %s" %str(result))

       total_time = time.time() - starttime
       ScrCmds.insertHeader('Verify Disk Test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : System Ready Test : END')

   def DataCompareSIOPTest(self, caching = False):
       ScrCmds.insertHeader('NetApp : Data Compare SIOP Test : BEGIN')
       starttime = time.time()

       if caching == False:
           #result = ICmd.SetFeatures(0x82) #diable write cache
           SATA_SetFeatures.disable_WriteCache()
           objMsg.printMsg('disable write cache')
           #if result['LLRET'] != OK:
           #    ScrCmds.raiseException(10888, "Failed Disable Write Cache Data : %s" %str(result))

       import random
       loop_count = loop_Count = int(TP.netapp_dataCompareSIOPTest['loop_Count'])
       stepLBA = sctCnt =TP.netapp_dataCompareSIOPTest['sector_count']
       delay_time = int(TP.netapp_staticDataCompare['delay_time'])

       lba_size = 512
       loop_Count = int(float(loop_Count) / 4 * self.dut.imaxHead)

       objMsg.printMsg('loop_count : %d' %loop_count)
       objMsg.printMsg('sector_count : %d' %sctCnt)
       objMsg.printMsg('delay_time : %d' %delay_time)

       if testSwitch.virtualRun:
          loop_count = 10
          delay_time = 0

       for i in range(loop_count):
          position_A = random.randrange(0, self.max_LLB - sctCnt)                    #Random A location
          position_B = random.randrange(0, self.max_LLB - sctCnt)                    #Random B location

          if i == 4000 or i == 0:                                               #Random new Data every 4000 loops
             objMsg.printMsg('Fill Random pattern at loop : %d' % (i))
             self.fillRandomBuff()

          result = ICmd.WriteSectors(position_A, sctCnt)                        #Write A

          if self.DEBUG:
               objMsg.printMsg('WriteSectors A: %s' %str(result))

          if result['LLRET'] != 0:
            ScrCmds.raiseException(10888, "Write data A error: %s" %str(result))

          result = ICmd.WriteSectors(position_B, sctCnt)                        #Write B

          if self.DEBUG:
               objMsg.printMsg('WriteSectors B: %s' %str(result))

          if result['LLRET'] != 0:
             ScrCmds.raiseException(10888, "Write data B error : %s" %str(result))

          result = ICmd.ReadSectors(position_A, sctCnt)                         #Read Sector A
          if self.DEBUG:
             objMsg.printMsg('Read A : %s' %str(result))

          if result['LLRET'] == OK:
             result = ICmd.CompareBuffers(0, sctCnt * lba_size)                 #Compare Buffer
             if self.DEBUG:
                objMsg.printMsg('CompareBuffers A result : %s' %str(result))
          else:
              ScrCmds.raiseException(10888,"Compare buffer Failed : %s" %str(result))

          if result['LLRET'] == OK:
             result = ICmd.GetBuffer(RBF, 0,  sctCnt * lba_size)                 #Get Read Buffer
             if self.DEBUG:
                objMsg.printMsg('GetBuffer A result : %s' %str(result))
          else:
              ScrCmds.raiseException(10888,"Get Buffer Failed: %s" %str(result))

          if result['LLRET'] == OK:
             result = ICmd.ReadVerifySects(position_A, sctCnt)                   #Read Verify Sector
             if self.DEBUG:
                objMsg.printMsg('ReadVerifySects A result : %s' %str(result))
          else:
             ScrCmds.raiseException(10888,"Read Verify Sectors A Failed : %s" %str(result))

          result = ICmd.ReadSectors(position_B, sctCnt)                          #Read Sector
          if self.DEBUG:
             objMsg.printMsg('Read B : %s' %str(result))

          if result['LLRET'] == OK:
             result = ICmd.CompareBuffers(0,  sctCnt * lba_size)                 #Compare Buffer
             if self.DEBUG:
                objMsg.printMsg('CompareBuffers B result : %s' %str(result))
          else:
              ScrCmds.raiseException(10888,"Compare buffer Failed : %s" %str(result))

          if result['LLRET'] == OK:
             result = ICmd.GetBuffer(RBF, 0, sctCnt * lba_size)                  #Get Read Buffer
             if self.DEBUG:
                objMsg.printMsg('GetBuffer B result : %s' %str(result))
          else:
              ScrCmds.raiseException(10888,"Get Buffer Failed : %s" %str(result))

          if result['LLRET'] == OK:
             result = ICmd.ReadVerifySects(position_B, sctCnt)                   #Read Verify Sector
             if self.DEBUG:
                objMsg.printMsg('ReadVerifySects B result : %s' %str(result))
          else:
             ScrCmds.raiseException(10888,"Read Verify Sectors B Failed: %s" %str(result))

          if not testSwitch.virtualRun:
             ScriptPause(delay_time)

          if(self.DEBUG):
               objMsg.printMsg('DataCompareSIOPTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

       if caching == False:
           result = ICmd.SetFeatures(0x02) #re-enable write cache

           if self.DEBUG:
                objMsg.printMsg('Compare result : %s' %str(result))

           if result['LLRET'] != OK:
               ScrCmds.raiseException(10888,"Failed Enable Write Cache: %s" %str(result))

       total_time = time.time() - starttime
       ScrCmds.insertHeader('Data Compare SIOP Test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Data Compare SIOP Test : END')

   def BandSeqRWCmpTest(self):
           ScrCmds.insertHeader('NetApp : Banded Sequential Write/Read Compare Test : BEGIN')
           starttime = time.time()

           increasing_step = int(TP.netapp_bandSeqRWCmpTest['increasing_step'])
           pattern_count =TP.netapp_bandSeqRWCmpTest['pattern_count']
           stepLBA =TP.netapp_bandSeqRWCmpTest['stepLBA']
           loop_Count =TP.netapp_bandSeqRWCmpTest['loop_Count']

           increasing_step = ((increasing_step * 4) / self.dut.imaxHead)

           objMsg.printMsg('increasing_step : %d' %increasing_step)
           objMsg.printMsg('pattern_count : %d' %pattern_count)
           objMsg.printMsg('stepLBA : %d' %stepLBA)
           objMsg.printMsg('loop_Count : %d' %loop_Count)

           SATA_SetFeatures.enable_WriteCache()

           if testSwitch.virtualRun:
              loop_Count = 1
              pattern_count = 1

           for iCount in range(loop_Count):
               for pattern in range(int(pattern_count)):
                  if pattern == 0 :                                                     #Fill Write Buffer with (Incremental, Shifting bit, Counting,Random )
                     self.fillIncrementalBuff()

                  if pattern == 1 :
                     self.fillShiftingBitBuff()

                  if pattern == 2 :
                     self.fillCountingBuff()

                  if pattern == 3 :
                     self.fillRandomBuff()

                  blockSize = int((1024 * 1024 * 8) / 512)                                # ~ 8M data size
                  sector_count = step_lba = stepLBA                                     #  32K xfer size
                  Stamp = 0
                  Compare = 0
                  test_loop = 1

                  count_step = 0
                  for i in range(0,100,increasing_step):                                #Increasing about 2% per step
                     targetLBA = int(self.max_LLB *(float(increasing_step) / 100) * count_step)              #Write Data Phase
                     result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)

                     count_step = count_step + 1

                     if self.DEBUG:
                        objMsg.printMsg('Write - Step :  %d' % increasing_step)
                        objMsg.printMsg('Write - LBA :  %x' % targetLBA)
                        objMsg.printMsg('Write - Result :  %s' %str(result))

                     if result['LLRET'] != OK:
                        objMsg.printMsg('Write - Step :  %d' % increasing_step)
                        objMsg.printMsg('Write - LBA :  %x' % targetLBA)
                        objMsg.printMsg('Write - blockSize :  %x' % blockSize)
                        objMsg.printMsg('Write - step_lba :  %d' % step_lba)
                        objMsg.printMsg('Write - sector_count :  %x' % sector_count)
                        objMsg.printMsg('Write - Loop :  %d' % i)
                        objMsg.printMsg('Write - max_LLB :  %d' % self.max_LLB)
                        ScrCmds.raiseException(10888, "Write Banded Data Failed : %s" %str(result))

                  result = ICmd.BufferCopy(RBF,0,WBF,0,512)
                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,'BufferCopy Failed! : %s' % str(result))

                  Compare = 1
                  count_step = 0
                  for i in range(0,100,increasing_step):                                 #Read Data Phase
                     targetLBA = int(self.max_LLB *(float(increasing_step) / 100)* count_step)
                     result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)

                     count_step = count_step + 1

                     if result['LLRET'] != OK:
                        objMsg.printMsg('Read - Step :  %d' % increasing_step)
                        objMsg.printMsg('Read - LBA :  %x' % targetLBA)
                        objMsg.printMsg('Read - blockSize :  %x' % blockSize)
                        objMsg.printMsg('Read - step_lba :  %d' % step_lba)
                        objMsg.printMsg('Read - sector_count :  %x' % sector_count)
                        objMsg.printMsg('Read - Loop :  %d' % i)
                        objMsg.printMsg('Read - max_LLB :  %d' % self.max_LLB)
                        ScrCmds.raiseException(10888, "Read Banded Data Failed : %s" %str(result))

                     if self.DEBUG:
                        objMsg.printMsg('Read - Result %s' %str(result))

           total_time = time.time() - starttime
           ScrCmds.insertHeader('Banded Sequential Write/Read Compare Test Time Usage : %d' % total_time)
           ScrCmds.insertHeader('NetApp : Banded Sequential Write/Read Compare Test : END')

   def StressedPinchTest(self):
       ScrCmds.insertHeader('NetApp : Stressed Pinch Test : BEGIN')
       starttime = time.time()

       loop_Count = TP.netapp_stressedPinchTest['loop_Count']
       write_Loop = TP.netapp_stressedPinchTest['loop_Write']
       stepLBA =TP.netapp_stressedPinchTest['stepLBA']

       objMsg.printMsg('loop_Count : %d' %loop_Count)
       objMsg.printMsg('write_Loop : %d' %write_Loop)
       objMsg.printMsg('stepLBA : %d' %stepLBA)

       SATA_SetFeatures.enable_WriteCache()
       result = ICmd.FillBuffRandom(WBF)                                            #Fill Write Buffer with Random Data
       if result['LLRET'] != OK:
         if self.DEBUG:
             objMsg.printMsg('FillBuffRandom : %s' %str(result))
         ScrCmds.raiseException(11044, "Fill Random Pattern error")

       startLBA = 0;
       C1MB_to_LBA = int((1024 * 1024) / 512)
       C1MB = 1024 * 1024
       block_size = C1MB / 512
       write_Loop = 10

       for loop in range(loop_Count):
           targetLBA = int(self.max_LLB /2)                                            #Write to LBA (Max LBA/2) & verify (Max LBA/2).
           self.WriteRead(targetLBA, block_size, 'WC')

           targetLBA = int(self.max_LLB /2) + block_size                               #Write to LBA (Max LBA/2 + 1024Kb) & verify LBA (Max LBA/2 +1024Kbytes)

           self.WriteRead(targetLBA, block_size, 'WC')

           targetLBA = int(self.max_LLB /2) - block_size                               #Write to LBA (Max LBA/2 ? 1024Kb) & verify LBA (Max LBA/2 -1024Kbytes)
           self.WriteRead(targetLBA, block_size, 'WC')

           for i in range(0,write_Loop):
               targetLBA = int(self.max_LLB / 2 + C1MB_to_LBA)                         #Seek to random LBA in the range [(Max LBA/2 + 1024Kbytes) ? Max LBA]

               result = ICmd.RandomSeekTime(targetLBA, self.max_LLB, 10, seekType = 28, timeout = 600, exc=0)
               if self.DEBUG:
                     objMsg.printMsg('RandomSeekTime 2: %s' %str(result))

               if result['LLRET'] != OK:
                 ScrCmds.raiseException(11044, "Random Seek Error")

               targetLBA = int(self.max_LLB /2)                                        #Write to LBA (Max LBA/2) & verify (Max LBA/2).
               self.WriteRead(targetLBA, block_size, 'WC')

               targetLBA = int(self.max_LLB / 2)                                       #Seek to random LBA in the range [(Max LBA/2 + 1024Kbytes) ? Max LBA]

               result = ICmd.RandomSeekTime(0, targetLBA, 10, seekType = 28, timeout = 600, exc=0)
               if result['LLRET'] != OK:
                 if self.DEBUG:
                     objMsg.printMsg('Read B : %s' %str(result))
                 ScrCmds.raiseException(11044, "Random Seek Error")

               targetLBA = int(self.max_LLB /2)                                        #Write to LBA (Max LBA/2) & verify (Max LBA/2).
               self.WriteRead(targetLBA, block_size, 'W')

               targetLBA = int(self.max_LLB /2) + block_size                           #Read LBA (Max LBA/2 + 1024Kb)
               self.WriteRead(targetLBA, block_size, 'R')

               targetLBA = int(self.max_LLB /2) - block_size                           #Read LBA (Max LBA/2 ? 1024Kb)
               self.WriteRead(targetLBA, block_size, 'R')

       total_time = time.time() - starttime
       ScrCmds.insertHeader('Stressed Pinch Test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Stressed Pinch Test : END')

   def SimulateWorkLoadSIOPTest(self, mode = 'NONE'):
       ScrCmds.insertHeader('NetApp : Simulate WorkLoad SIOP Test %s : BEGIN' % mode)
       starttime = time.time()

       import random

       lba_size = TP.netapp_simulateWorkLoadSIOPTest['lba_size']
       run_time = TP.netapp_simulateWorkLoadSIOPTest['run_time']

       if testSwitch.virtualRun:
           run_time = 5

       if self.DEBUG:
           objMsg.printMsg('lba_size : %d' %lba_size)
           objMsg.printMsg('run_time : %d' %run_time)

       while(True):
           loop_random = random.randrange(1,100)
           for i in range(loop_random):
               if mode == 'FILE_SERVER':
                  random_value = random.random()
                  startLBA = 0
                  targetLBA = 0
                  stepLBA = 0
                  lba_count = 0

                  if random <= 0.1:                                               #random location
                     startLBA = int(random.randrange(int(self.max_LLB *0.01)), int(self.max_LLB))

                  elif random <=(0.1 + 0.3):
                     startLBA = int(random.randrange(int(self.max_LLB *0.3), int(self.max_LLB *0.6)))

                  else:
                     startLBA = int(random.randrange(int(self.max_LLB *0), int(self.max_LLB *0.1)))

                  random_value = random.random()

                  if random <= 0.3:                                               #random transfer size
                     lba_count = int(random.randrange(int(2 * (1024 /lba_size)), int(32 * 1024/ lba_size)))        #2KB - 32Kb

                  else:
                     lba_count = int(random.randrange(int(32 * 1024/lba_size),  int(128 * 1024/ lba_size)))      #32KB - 128Kb

                  random_value = random.random()

                  if random <= 0.2:                                               #random RW mode. Read:Write ratio of 4:1
                     result = ICmd.WriteSectors(startLBA, lba_count)
                     if self.DEBUG:
                        objMsg.printMsg('WriteSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                     if result['LLRET'] != OK:
                        ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Write Failed %s" % str(result))

                  else:
                     result = ICmd.ReadSectors(startLBA, lba_count)
                     if self.DEBUG:
                        objMsg.printMsg('ReadSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                     if result['LLRET'] != OK:
                        ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Read Failed %s" % str(result))

               elif mode == 'OLTP':

                  random_value = random.random()
                  startLBA = 0
                  targetLBA = 0
                  stepLBA = 0
                  lba_count = 0

                  if random <= 0.2:                                               #random location
                     startLBA = int(random.randrange(int(self.max_LLB *0.01), int(self.max_LLB)))

                  elif random <=(0.2 + 0.3):
                     startLBA = int(random.randrange(int(self.max_LLB *0.1), int(self.max_LLB *0.3)))

                  else:
                     startLBA = int(random.randrange(int(self.max_LLB * 0.3), int(self.max_LLB *0.6)))

                  random_value = random.random()

                  if random <= 0.3:                                               #random transfer size
                     lba_count = int(random.randrange( int(4 * 1024/ lba_size),  int(8 * 1024/ lba_size)))        #4KB - 8Kb

                  else:
                     lba_count = int(random.randrange( int(1 * 1024/ lba_size),  int(4 * 1024/ lba_size)))          #1KB - 4Kb

                  random_value = random.random()

                  if random <= 0.2:                                               #random RW mode
                     result = ICmd.WriteSectors(startLBA, lba_count)
                     if self.DEBUG:
                        objMsg.printMsg('WriteSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                     if result['LLRET'] != OK:
                        ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Write Failed %s" % str(result))

                  else:
                     result = ICmd.ReadSectors(startLBA, lba_count)

                     if self.DEBUG:
                        objMsg.printMsg('ReadSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))

                     if result['LLRET'] != OK:
                        ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Read Failed %s" % str(result))

           pause_time = random.randrange(1, 10)

           if not testSwitch.virtualRun:
              ScriptPause(pause_time)

           if((time.time() - starttime) > run_time):
               break

           if(self.DEBUG):
               objMsg.printMsg('SimulateWorkLoadSIOPTestt random %s Loop : %d, Time : %d' % (mode,i, (time.time() - starttime)))

       total_time = time.time() - starttime
       ScrCmds.insertHeader('Simulate WorkLoad SIOP  %s Time Usage : %d' % (mode, total_time))
       ScrCmds.insertHeader('NetApp : Simulate WorkLoad SIOP Test %s : END' % mode)

   def DataErasureTest(self):
       ScrCmds.insertHeader('NetApp : Data Erasure Test : BEGIN')
       starttime = time.time()

       lba_size = TP.netapp_dataErasureTest['lba_size']
       data_size = int((TP.netapp_dataErasureTest['data_size'] / 4) * self.dut.imaxHead)                            #2GB Data Size
       loop_Count = TP.netapp_dataErasureTest['loop_Count']
       pattern_count  = TP.netapp_dataErasureTest['pattern_count']

       result = ICmd.SetFeatures(0x03, 0x47)                                        # Set DMA Mode UDMA 7 (UDMA150)
       if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,'Set DMA Mode UDMA 7 Failed! : %s' % str(result))
       else:
            objMsg.printMsg('Set DMA Mode UDMA 7  : %s' % str(result))

       SATA_SetFeatures.enable_WriteCache()

       if testSwitch.virtualRun:
          loop_Count = 1
          pattern_count = 1

       for i in range(loop_Count):
           for pattern in range(pattern_count):
                                                                                    #Fill Write Buffer with (Random , Incremental, Shifting bit, Counting):
              if pattern == 0 :                                                     #Fill Write Buffer with (Incremental, Shifting bit, Counting,Random )
                 self.fillRandomBuff()

              if pattern == 1 :
                 self.fillIncrementalBuff()

              if pattern == 2 :
                 self.fillShiftingBitBuff()

              if pattern == 3 :
                 self.fillCountingBuff()

              targetLBA =  int(self.max_LLB * 0.02)                                                #OD : 2% from OD
              self.ErasureTest(targetLBA,data_size,lba_size)

              targetLBA =  int(self.max_LLB * 0.5)                                                 #OD : 50% of total LBA
              self.ErasureTest(targetLBA,data_size,lba_size)

              targetLBA =  int(self.max_LLB * 0.98)                                                #ID : 2% from ID
              self.ErasureTest(targetLBA,data_size,lba_size)

       total_time = time.time() - starttime
       ScrCmds.insertHeader('Data Erasure Test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Data Erasure Test : END')

   def DataErasureTest2_CHS(self):
       ScrCmds.insertHeader('NetApp : Data Erasure Test 2 : BEGIN')
       sptCmds.enableDiags()
       starttime = time.time()

       lba_size = TP.netapp_dataErasureTest2['lba_size']
       loop_Count = TP.netapp_dataErasureTest2['loop_Count']
       loop_Write = TP.netapp_dataErasureTest2['loop_Write']

       for cur_hd in range(self.dut.imaxHead):
            od_cylinder = self.zones[cur_hd][0]
            md_cylinder = self.zones[cur_hd][int(self.dut.numZones / 2)]
            id_cylinder = self.zones[cur_hd][int(self.dut.numZones - 1)] - 1

            if testSwitch.FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK:
               for retry in range(3):
                  try:
                     objMsg.printMsg('DataErasureTest2 Test Head %d ' % cur_hd)
                     sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                    #Fill random pattern

                     #write 1MB data to center of surface
                     sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space
                     sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
                     sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                     #Write/Read 1000 loops using diagnostic batch file
                     objMsg.printMsg('DataErasureTest2 Test Read/Write %d loops ' % loop_Write)
                     sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                       #Start Batch File
                     sptCmds.sendDiagCmd('*7,%x,1'% 2,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)              #Set Loop Count 1 to 10000
                     sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                        #Batch File Label - Label 2

                     sptCmds.sendDiagCmd('/2A8,%x,,%x' % (md_cylinder + 1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)         #Set Test Space
                     sptCmds.sendDiagCmd('/2A9,%x,,%x' % (id_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #From Mid +1 to Extreme ID
                     sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
                     sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
                     sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

                     sptCmds.sendDiagCmd('/2A8,%x,,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #Set Test Space
                     sptCmds.sendDiagCmd('/2A9,%x,,%x' % (md_cylinder -1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #From OD to MD
                     sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
                     sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
                     sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

                     sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                    #Decrement Loop Count 1 and Branch to Label 2 if not 0
                     sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                           #End Batch File
                     sptCmds.sendDiagCmd('B,0',timeout = 2400,printResult = False, raiseException = 1, stopOnError = False)                                        #Run Batch File

                     sptCmds.sendDiagCmd('/2AD',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Reset Test Space
                     sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Set Test Space
                     sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
                     sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 30, printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Read Verify 1 track
                     break

                  except Exception, e:
                     if e[0][2] == 13426:
                        objMsg.printMsg('Fail from invalid track retry on next 100 track')
                        objMsg.printMsg('Retry at loop %d'%(retry+1))
                        od_cylinder +=100
                        md_cylinder +=100
                        id_cylinder -=100
                     else:
                        raise
            else:
               objMsg.printMsg('DataErasureTest2 Test Head %d ' % cur_hd)
               sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                    #Fill random pattern

               #write 1MB data to center of surface
               sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space
               sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
               sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               #Write/Read 1000 loops using diagnostic batch file
               objMsg.printMsg('DataErasureTest2 Test Read/Write %d loops ' % loop_Write)
               sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                       #Start Batch File
               sptCmds.sendDiagCmd('*7,%x,1'% 2,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)              #Set Loop Count 1 to 10000
               sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                        #Batch File Label - Label 2

               sptCmds.sendDiagCmd('/2A8,%x,,%x' % (md_cylinder + 1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)         #Set Test Space
               sptCmds.sendDiagCmd('/2A9,%x,,%x' % (id_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #From Mid +1 to Extreme ID
               sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
               sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
               sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

               sptCmds.sendDiagCmd('/2A8,%x,,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)             #Set Test Space
               sptCmds.sendDiagCmd('/2A9,%x,,%x' % (md_cylinder -1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #From OD to MD
               sptCmds.sendDiagCmd('/2A106' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                        #Random cylinder random sector
               sptCmds.sendDiagCmd('/2L,%x' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                           #Perform 10K Write
               sptCmds.sendDiagCmd('/2W' ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                            #Write Data for 1 sector

               sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                    #Decrement Loop Count 1 and Branch to Label 2 if not 0
               sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                           #End Batch File
               sptCmds.sendDiagCmd('B,0',timeout = 2400,printResult = False, raiseException = 1, stopOnError = False)                                        #Run Batch File

               sptCmds.sendDiagCmd('/2AD',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Reset Test Space
               sptCmds.sendDiagCmd('/2A0',timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                       #Set Test Space
               sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd),timeout = 30, printResult = self.DEBUG, raiseException = 0, stopOnError = True)             #Seek to MD (center track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 30, printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Read Verify 1 track

       total_time = time.time() - starttime
       sptCmds.enableESLIP()
       ScrCmds.insertHeader('Data Erasure Test 2 Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Data Erasure Test 2 : END')

   def ErasureTest(self,targetLBA, blockSize,lba_size):
       step_lba = sector_size = 256
       loopCount = 10000

       if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
          sta_LLB = int(targetLBA)
          sta3 = int((sta_LLB & 0xFFFF000000000000) >> 48)
          sta2 = int((sta_LLB & 0x0000FFFF00000000) >> 32)
          sta1 = int((sta_LLB & 0x00000000FFFF0000) >> 16)
          sta0 = int((sta_LLB & 0x000000000000FFFF))

          end_LLB = int(targetLBA+ blockSize)
          end3 = int((end_LLB & 0xFFFF000000000000) >> 48)
          end2 = int((end_LLB & 0x0000FFFF00000000) >> 32)
          end1 = int((end_LLB & 0x00000000FFFF0000) >> 16)
          end0 = int((end_LLB & 0x000000000000FFFF))

          tot_blks_to_xfr = int(blockSize)
          tot1 = int((tot_blks_to_xfr & 0x00000000FFFF0000) >> 16)
          tot0 = int((tot_blks_to_xfr & 0x000000000000FFFF))

          objMsg.printMsg('Sequential : sta_LLB=%s, end_LLB=%s, tot_blks_to_xfr=%s, sta3=%s, sta2=%s, sta1=%s, sta0=%s, end3=%s, end2=%s, end1=%s, end0=%s, tot1=%s, tot0=%s'\
                        %(sta_LLB,end_LLB,tot_blks_to_xfr,sta3,sta2,sta1,sta0,end3,end2,end1,end0,tot1,tot0))

       result = ICmd.Seek(targetLBA)      # Seek to LBA 0
       if result['LLRET'] != OK:
           objMsg.printMsg('Seek cmd Failed!')

       if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
          ICmd.St(TP.prm_638_Unlock_Seagate)
          ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialWrite',CTRL_WORD1=(0x22),STARTING_LBA=(sta3,sta2,sta1,sta0),MAXIMUM_LBA =(end3,end2,end1,end0),TOTAL_BLKS_TO_XFR =(tot1,tot0))
       else:
          result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_size)
          if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,'SequentialWriteDMAExt Failed! : %s' % str(result))
          else:
             if self.DEBUG:
                objMsg.printMsg('Write Data Complete! : %s' % str(result))

       result = ICmd.RandomSeekTime(targetLBA, targetLBA + (self.max_LLB * 0.02 ), loopCount)  #Random Seek 10000 times ;targetLBA + 2G + 2%
       if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Random Seek Error : %s" % str(result))
       else:
          if self.DEBUG:
             objMsg.printMsg('Random Seek ! : %s' % str(result))

       result = ICmd.BufferCopy(RBF,0,WBF,0,512)
       if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,'BufferCopy Failed! : %s' % str(result))

       Compare = 1
       if testSwitch.FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND:
          ICmd.St(TP.prm_638_Unlock_Seagate)
          ICmd.St(TP.prm_510_Sequential,prm_name='prm_510_SequentialReadVer',CTRL_WORD1=(0x42),STARTING_LBA=(sta3,sta2,sta1,sta0),MAXIMUM_LBA =(end3,end2,end1,end0),TOTAL_BLKS_TO_XFR =(tot1,tot0))
       else:
         result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_size)
         if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,'SequentialReadVerifyExt Failed! : %s' % str(result))
         else:
             if self.DEBUG:
               objMsg.printMsg('Read Verify Data Complete! ! : %s' % str(result))


   def AdjacentPinch_CHS(self):
       ScrCmds.insertHeader('NetApp : Adjacent Pinch : BEGIN')
       sptCmds.enableDiags()
       starttime = time.time()

       lba_size = TP.netapp_adjacentPinch['lba_size']
       loop_Count = TP.netapp_adjacentPinch['loop_Count']
       loop_Write = TP.netapp_adjacentPinch['loop_Write']
       C1MB_to_LBA = int((1024 * 1024) / lba_size)
       blockSize = (1024 * 1024 / lba_size)                                          #1M Block Size

       if self.DEBUG:
           objMsg.printMsg('loop_Count : %d' %loop_Count)
           objMsg.printMsg('loop_Write : %d' %loop_Write)
           objMsg.printMsg('C1MB_to_LBA : %d, blockSize : %d, lba_size : %d' % (C1MB_to_LBA, blockSize, lba_size))

       if testSwitch.virtualRun:
          loop_Count = 1
          loop_Write = 1

       sector = 0
       for i in range(loop_Count):
          for cur_hd in range(self.dut.imaxHead):
              #objMsg.printMsg('AdjacentPinch OD Test Head : %d' % cur_hd)

              od_cylinder = self.zones[cur_hd][0]
              md_cylinder = self.zones[cur_hd][int(self.dut.numZones / 2)]
              id_cylinder = self.zones[cur_hd][int(self.dut.numZones -1 )] -1

              if testSwitch.FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK:
               for retry in range(3):
                objMsg.printMsg('AdjacentPinch OD Test Head : %d' % cur_hd)
                try:
                   sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
                   sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

                   sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
                   sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
                   sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
                   sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                   #Write/Read 1000 loops using diagnostic batch file

                   objMsg.printMsg('AdjacentPinch OD Test Read/Write %d loops ' % loop_Write)
                   sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
                   sptCmds.sendDiagCmd('*7,%x,1' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
                   sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

                   sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
                   sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
                   sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
                   sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
                   sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
                   sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

                   break
                except Exception, e:
                   if e[0][2] == 13426:
                      objMsg.printMsg('Fail from invalid track retry on next 100 track')
                      objMsg.printMsg('Retry at loop %d'%(retry+1))
                      od_cylinder += 100
                   else:
                      raise

               for retry in range(3):
                try:
                   objMsg.printMsg('AdjacentPinch ID Test Head : %d' % cur_hd)

                   sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
                   sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

                   sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
                   sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
                   sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
                   sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

                   #Write/Read 1000 loops using diagnostic batch file

                   objMsg.printMsg('AdjacentPinch ID Test Read/Write 1000 loops ')
                   sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
                   sptCmds.sendDiagCmd('*7,%x,1'%loop_Write,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
                   sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

                   sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
                   sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
                   sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
                   sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

                   sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
                   sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
                   sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

                   break
                except Exception, e:
                   if e[0][2] == 13426:
                      objMsg.printMsg('Fail from invalid track retry on next 100 track')
                      objMsg.printMsg('Retry at loop %d'%(retry+1))
                      id_cylinder -=100
                   else:
                      raise
              else:
               objMsg.printMsg('AdjacentPinch OD Test Head : %d' % cur_hd)

               sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
               sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               #Write/Read 1000 loops using diagnostic batch file

               objMsg.printMsg('AdjacentPinch OD Test Read/Write %d loops ' % loop_Write)
               sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
               sptCmds.sendDiagCmd('*7,%x,1' % loop_Write ,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
               sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
               sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
               sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

               objMsg.printMsg('AdjacentPinch ID Test Head : %d' % cur_hd)

               sptCmds.sendDiagCmd('/2P1212',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                  #Fill random pattern
               sptCmds.sendDiagCmd('A0',timeout = 30, printResult = False, raiseException = 0, stopOnError = False)                                       #Set Test Space

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)          #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30, printResult = False, raiseException = 0, stopOnError = False)        #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = False, raiseException = 1, stopOnError = True)                          #Write 1 track

               #Write/Read 1000 loops using diagnostic batch file

               objMsg.printMsg('AdjacentPinch ID Test Read/Write 1000 loops ')
               sptCmds.sendDiagCmd('/6E',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     #Start Batch File
               sptCmds.sendDiagCmd('*7,%x,1'%loop_Write,timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)               #Set Loop Count 1 to 1000
               sptCmds.sendDiagCmd('@2',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      #Batch File Label - Label 2

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-2,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +1 trk  (center track)
               sptCmds.sendDiagCmd('/2W0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-3,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)            #Seek ExtremeOD trk  (upper track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('/2S%x,%x' % (id_cylinder-1,cur_hd),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          #Seek ExtremeOD +2 trk  (lower track)
               sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 1, stopOnError = True)                          #Write 1 track

               sptCmds.sendDiagCmd('*8,2,1',timeout = 30,altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                   #Decrement Loop Count 1 and Branch to Label 2 if not 0
               sptCmds.sendDiagCmd('|',timeout = 30,printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                          #End Batch File
               sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                                            #Run Batch File

       total_time = time.time() - starttime
       sptCmds.enableESLIP()
       ScrCmds.insertHeader('Adjacent Pinch Test Time Usage : %d' % total_time)
       ScrCmds.insertHeader('NetApp : Adjacent Pinch Test : END')


   def WriteRead(self,targetLBA, blockSize, mode = 'NONE'):
       Compare = 0;
       Stamp = 0
       test_loop = 1
       sector_count = step_lba = 256
       if mode.find('C') >= 0:
          Compare = 1

       if mode.find('W')>= 0:
          if self.DEBUG:
              objMsg.printMsg('SequentialWriteVerify : startLBA : %d,  endLBA: %d,, Stamp : %d, Compare : %d, test_loop : %d ' % (targetLBA, (targetLBA+ blockSize),Stamp, Compare, test_loop))

          result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)                               #write 1

          if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,'SequentialWriteDMAExt Failed! : %s' % str(result))

       if mode.find('R') >= 0:
          if self.DEBUG:
              objMsg.printMsg('SequentialReadVerifyExt : startLBA : %d,  endLBA: %d, Stamp : %d, Compare : %d, test_loop : %d ' % (targetLBA, (targetLBA+ blockSize),Stamp, Compare, test_loop))

          result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_count,Stamp, Compare, test_loop)                           #read

          if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,"SequentialReadVerifyExt Failed: %s" % str(result))

   def WriteRead_CHS(self, cylinder, head, sector, blockSize, mode = 'NONE'):
       Compare = 0;
       Stamp = 0
       test_loop = 1
       step_Cylinder = 1
       step_Head = 1
       step_Sector = 256
       verify_msg = ""
       if mode.find('C') >= 0:
          Compare = 1
          verify_msg = "Verify"

       if mode.find('W')>= 0:
          if self.DEBUG:
              msg = 'SequentialWrite%s  cylinder : %d,  head: %d, sector : %d, sector_cnt : %d ' % (verify_msg, cylinder, head, sector, sector+blockSize)

          if(Compare):
               result = ICmd.SequentialWriteVerify(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)
          else:
               result = ICmd.SequentialWriteDMA(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)

          if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,'Sequential Write Failed! : %s' % str(result))

       if mode.find('R') >= 0:
          if self.DEBUG:
              msg = ('SequentialRead%s  cylinder : %d,  head: %d, sector : %d, sector_cnt : %d ' % (verify_msg, cylinder, head, sector, sector+blockSize))

          if(Compare):
               result = ICmd.SequentialReadVerify(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)
          else:
               result = ICmd.SequentialReadDMA(cylinder, head, sector,cylinder, head, sector + blockSize,step_Cylinder, step_Head, step_Sector,blockSize,Stamp, Compare, test_loop)

          if result['LLRET'] != OK:
             ScrCmds.raiseException(10888,"SequentialReadDMA Failed: %s" % str(result))

       if self.DEBUG:
              objMsg.printMsg('WriteRead_CHS Result : %s : %s' % (str(result), msg))

   def fillIncrementalBuff(self):
       result = ICmd.FillBuffInc(WBF)
       if result['LLRET'] != OK:
          ScrCmds.raiseException(10888, "Fill Incremental Buffer Error")

       objMsg.printMsg('Fill Incremental Buffer Complete.')

   def fillRandomBuff(self):
       result = ICmd.FillBuffRandom(WBF)
       if result['LLRET'] != OK:
          ScrCmds.raiseException(10888, "Fill Random Buffer Error")

       objMsg.printMsg('Fill Random Buffer Complete.')

   def fillShiftingBitBuff(self):
       import array
       data_pattern = array.array('H')

       data  = 0xFFFF
       increment = False
       for i in xrange(0,0x20000 / 2, 2):
                                                            #Prepare Shifting Bit Pattern (Total Buffer Size = 0x20000 byte)
          if (increment) :
              data = data + 1
          else:
              data = data -1

          if data == 0xFFFF or data == 0:
              increment = not increment

          data_pattern.insert(i, 0)
          data_pattern.insert(i + 1, data & 0xFFFF)

       write_buffer = ''.join([(chr(num >>8) + chr(num & 0xff)) for num in (data_pattern)])
       result = ICmd.FillBuffer(WBF,0,write_buffer)
       if result['LLRET'] != OK:
          ScrCmds.raiseException(10888, "Fill Shifting Bit Buffer Error")

       objMsg.printMsg('Fill Shifting Bit Buffer Complete.')

   def fillCountingBuff(self):
       import array
       data_pattern = array.array('H')

       init_value  = 0xFFFF
       for i in xrange(0,0x20000 / 2):                                                 #Prepare Counting Pattern (Total Buffer Size = 0x20000 byte)
          data = i
          data = data << 8
          data = data | (i + 1)
          data_pattern.insert(i + 1, data & 0xFFFF)

       write_buffer = ''.join([(chr(num >>8) + chr(num & 0xff)) for num in (data_pattern)])
       result = ICmd.FillBuffer(WBF,0,write_buffer)
       if result['LLRET'] != OK:
          ScrCmds.raiseException(10888, "Fill Counting Buffer Error")

       objMsg.printMsg('Fill Counting Buffer Complete.')

   def getBasicDriveInfo(self):
       self.oSerial.enableDiags()
       self.numCyls,self.zones = self.oSerial.getZoneInfo(printResult=True)

       objMsg.printMsg("Total cylinder %s" % str(self.numCyls) )
       objMsg.printMsg("Zone %s" % str(self.zones) )

       objMsg.printMsg("Max Hd %s" % str(self.dut.imaxHead) )
       objMsg.printMsg("Num Zone %s" % str(self.dut.numZones) )

   def  ShortTest(self):
        pass

###########################################################################################################
class CMuskieButterFly(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProcess = CProcess()
      from serialScreen import sptDiagCmds
      self.oSerial = sptDiagCmds()

      self.DEBUG = 0

      self.getBasicDriveInfo()
      self.PowerCycleTest()
      self.Intialization()
      ret = CIdentifyDevice().ID
      self.max_LLB = ret['IDDefaultLBAs'] - 1 # default for 28-bit LBA
      if ret['IDCommandSet5'] & 0x400:      # check bit 10
         objMsg.printMsg('Get ID Data 48 bit LBA is supported')
         self.max_LLB = ret['IDDefault48bitLBAs'] - 1
      if self.DEBUG:
         objMsg.printMsg('CIdentifyDevice data : %s' %str(ret))
      if self.max_LLB <= 0:
         self.max_LLB = 976773167
         objMsg.printMsg("Assign max_LLB to default : %d", self.max_LLB)
      objMsg.printMsg("The Maximum User LBA is : %08X       Drive Capacity - %dGB" %(self.max_LLB,(( self.max_LLB * 512 )/1000000000),))
      self.ButterflyWriteTest()
      self.ButterflyWriteTest()
      self.ButterflyWriteTest()
      self.ButterflyWriteTest()

   def Intialization(self):
      self.PrintMessage("Unlock Seagate")
      try:
         self.oProcess.St(TP.prm_638_Unlock_Seagate) # Unlock Seagate Access
      except:
         self.PowerCycleTest()

   def getBasicDriveInfo(self):
      self.oSerial.enableDiags()
      self.numCyls,self.zones = self.oSerial.getZoneInfo(printResult=True)

      objMsg.printMsg("Total cylinder %s" % str(self.numCyls) )
      objMsg.printMsg("Zone %s" % str(self.zones) )

      objMsg.printMsg("Max Hd %s" % str(self.dut.imaxHead) )
      objMsg.printMsg("Num Zone %s" % str(self.dut.numZones) )

   def ButterflyWriteTest(self):
      self.PrintMessage('NetApp : Butterfly Write Test : BEGIN')
      starttime = time.time()

      loop_count = loop_Count = int(TP.netapp_butterflyWriteTest['loop_Count'])
      step_rate = TP.netapp_butterflyWriteTest['step_rate']
      lba_size = TP.netapp_butterflyWriteTest['lba_size']
      run_time = int(TP.netapp_butterflyWriteTest['run_time']/ 4 * self.dut.imaxHead)

      block_size = 1024*32/lba_size
      (block_size_MSBs, block_size_LSBs) = self.UpperLower(block_size)

      objMsg.printMsg('loop_count : %d' %loop_count)
      objMsg.printMsg('step_rate : %d' %step_rate)
      objMsg.printMsg('run_time : %d Mins' %(run_time / 60))

      prm_506_SET_RUNTIME = {
         'test_num'          : 506,
         'prm_name'          : "prm_506_SET_RUNTIME",
         'spc_id'            :  1,
         "TEST_RUN_TIME"     :  run_time,
      }

      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         prm_510_BUTTERFLY = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_BUTTERFLY",
            'spc_id'            :  1,
            "CTRL_WORD1"        : (0x0422),                                        #Butterfly Sequencetioal Write;Display Location of errors
            "STARTING_LBA"      : (0,0,0,0),
            "BLKS_PER_XFR"      : (step_rate * block_size),                        #Need 32K write and seek 5*32K step, but cannot do that only write 5*32K.
            "OPTIONS"           : 0,                                               #Butterfly Converging
            "timeout"           :  3000,                                           #15 Mins Test Time
         }
      else:
         prm_510_BUTTERFLY = {
            'test_num'          : 510,
            'prm_name'          : "prm_510_BUTTERFLY",
            'spc_id'            :  1,
            "CTRL_WORD1"        : (0x0422),                                        #Butterfly Sequencetioal Write;Display Location of errors
            "STARTING_LBA"      : (0,0,0,0),
            "BLKS_PER_XFR"      : (step_rate * block_size),                        #Need 32K write and seek 5*32K step, but cannot do that only write 5*32K.
            "OPTIONS"           : 0,                                               #Butterfly Converging
            "retryECList"       : [14016,14029],
            "retryMode"         : POWER_CYCLE_RETRY,
            "retryCount"        : 2,
            "timeout"           :  3000,                                           #15 Mins Test Time
         }

      numGB = (self.max_LLB * lba_size ) / (10**9)
      ScriptComment("The Maximum LBA is : %08X Drive Capacity - %dGB" %(self.max_LLB, numGB,))

      (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0) = self.UpperLower4(self.max_LLB - 1)

      if testSwitch.BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY:
         for i in xrange(loop_count):
            failed = 1
            retry = 0
            while failed == 1 and retry <= TP.maxRetries_T510Butterfly:
               try:
                  self.oProcess.St(
                        prm_506_SET_RUNTIME,
                     )

                  self.oProcess.St(
                        prm_510_BUTTERFLY,
                        STARTING_LBA = (0, 0, 0, 0),
                        MAXIMUM_LBA  = (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0),
                     )
                  failed = 0

                  self.oProcess.St(
                        prm_506_SET_RUNTIME,TEST_RUN_TIME = 0,
                     )
               except ScriptTestFailure, (failureData):
                  ec = failureData[0][2]
                  if ec in [14016, 14029] and retry < TP.maxRetries_T510Butterfly:
                     objPwrCtrl.powerCycle(5000,12000,10,30)
                     retry += 1
                  else:
                     raise

            if(self.DEBUG):
               objMsg.printMsg('ButterflyWriteTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))
      else:
         for i in xrange(loop_count):
            self.oProcess.St(
                   prm_506_SET_RUNTIME,
                )

            self.oProcess.St(
                   prm_510_BUTTERFLY,
                   STARTING_LBA = (0, 0, 0, 0),
                   MAXIMUM_LBA  = (max_blk_B3, max_blk_B2, max_blk_B1, max_blk_B0),
                )

            self.oProcess.St(
                   prm_506_SET_RUNTIME,TEST_RUN_TIME = 0,
                )

            if(self.DEBUG):
               objMsg.printMsg('ButterflyWriteTest Loop : %d, Time : %d' % (i, (time.time() - starttime)))

      total_time = time.time() - starttime
      self.PrintMessage('Butterfly Write Time Usage : %d' % total_time)
      self.PrintMessage('NetApp : Butterfly Write Test : END')

   def UpperLower(self, FourByteNum):
      FourByteNum = FourByteNum & 0xFFFFFFFF                                   #chop off any more than 4 bytes
      MSBs = FourByteNum >> 16
      LSBs = FourByteNum & 0xFFFF
      return (MSBs, LSBs)

   def UpperLower4(self, EightByteNum):
      EightByteNum = EightByteNum & 0xFFFFFFFFFFFFFFFF                         #chop off any more than 8 bytes
      Word3 = (EightByteNum >> (16 * 3)) & 0xFFFF
      Word2 = (EightByteNum >> (16 * 2)) & 0xFFFF
      Word1 = (EightByteNum >> (16 * 1)) & 0xFFFF
      Word0 = EightByteNum & 0xFFFF
      return (Word3, Word2,Word1,Word0)

   def PrintMessage(self, message):
      total_text = 120
      remain_text = total_text - len(message)
      objMsg.printMsg('-' * (remain_text/2) + ' ' + message + ' ' + '-' * (remain_text/2))

   def PowerCycleTest(self):
      self.PrintMessage('Power Cycle')
      objPwrCtrl.powerCycle(offTime=20, onTime=35, ataReadyCheck = True)


################################################################################################################
class CSharpTest(CState):
   """
      Description: Class that will implement the below test sequence:
            1.20x Power cycle with 10sec off time (Time not To Ready fail)
            2.20 minutes Random Write/Read/Compare with zero pattern, sector count = 64
            3.20x Power cycle with 10sec off time (Time not To Ready fail)
            4.Sequential Write DMA EXT.Sector count = 256.All surface.(like as AV_SCAN )
            5.Sequential Read DMA EXT.Sector count = 256.All surface.
   """
   def __init__(self, dut, params={}):
       self.params = params
       depList = []
       CState.__init__(self, dut, depList)
       self.dut = dut

   def run(self):

      set5V = 5000
      set12V = 12000
      try:
         for count in range(20):
            ScriptComment('===================STEP1. Sharp Screen - %d Loop powerCycle ===================' %(count+1))
            objPwrCtrl.powerCycle(set5V,set12V,10)

         ScriptComment('=================== STEP2. 20min  Read/write/compare with RandomWRDMAExt===================')
         ret = CIdentifyDevice().ID # read device settings with identify device
         IDmaxLBA = ret['IDDefaultLBAs'] # default for 28-bit LBA
         if ret['IDCommandSet5'] & 0x400:      # check bit 10
            IDmaxLBA = ret['IDDefault48bitLBAs']
         maxLBA = IDmaxLBA - 1
         minrndScnt = maxrndScnt = 64
         cmdCount = 150000
         compare =1

         ICmd.SetIntfTimeout(60000)
         IntfTmo = ICmd.GetIntfTimeout()
         objMsg.printMsg('GetIntfTimeout() = %d  ms' % int(IntfTmo['TMO']))

         data = ICmd.StandbyImmed()
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('Failed StandbyImmed')
            ScrCmds.raiseException(14036,'Failed StandbyImmed')

         ICmd.FlushCache()
         ICmd.ClearBinBuff(WBF)
         ICmd.ClearBinBuff(RBF)
         objMsg.printMsg('Start RandomWRDMAExt: minLBA=%d maxLBA=%d rndScnt=%d LoopCnt=%d Compare=%d' %(0,maxLBA,minrndScnt,cmdCount,compare,))
         data = ICmd.RandomWRDMAExt(0, maxLBA, minrndScnt, maxrndScnt, cmdCount, stampFlag=0,compareFlag= compare,FlushCache=1)
         objMsg.printMsg('RandomWRDMAExt returned data: %s' % data)
         result = data['LLRET']
         if result != OK:
            ScrCmds.raiseException(14036,'Failed RandomWRDMAExt')

         for count in range(20):
            ScriptComment('===================STEP3. Sharp Screen - %d Loop powerCycle ===================' %(count+1))
            objPwrCtrl.powerCycle(set5V,set12V,10)

         ScriptComment('===================STEP4. Sharp Screen - Sequential Write DMA EXT and Sequential Read DMA===================')
         oAVScan = CAVScan(self.dut,params={})
         oAVScan.failureCriteria = {'read':[(270,0)],'write':[(400,0)]}
         oAVScan.avscanLogBoundaries = [100,400]
         oAVScan.avscanLogCount = 3
         objMsg.printMsg("Sharp Failure Criteria : %s\n" %str(oAVScan.failureCriteria))
         objMsg.printMsg("Sharp Log Boundaries : %s" %str(oAVScan.avscanLogBoundaries))

         oCCTScan = CCCTTest(self.dut, params={})
         oCCTScan.run(AVSCAN = 1,failureCriteria = oAVScan.failureCriteria)

         oAVScan.parseData()


         if not (testSwitch.BF_0178766_231166_P_FIX_DCM_ATTRIBUTES_FOR_SONY_SHARP and testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM):
            if self.dut.driveattr['CUST_TESTNAME'] == "NONE":
               CustName = 'SHARP SIMULATION'
            else:
               CustName = self.dut.driveattr['CUST_TESTNAME']
               CustName += '_' + 'SHARP SIMULATION'
            self.dut.driveattr['CUST_TESTNAME'] = CustName
      except:
         ScrCmds.statMsg(traceback.format_exc())
         ScrCmds.raiseException(14036, 'Sharp Screen fail')

###########################################################################################################
###########################################################################################################
############# NetApp V3 Short Test ######################

#        self.BandSeqRWCmpTest()                                     #Test time vary by head
#
#        self.SeekTest_CHS()                                         #Test time vary by head
#        self.AdjacentPinch_CHS()                                    #Test time vary by head
#        self.StaticDataCompareTest()                                #Test time fixed
#        self.DataCompareSIOPTest()                                  #Test time fixed
#        self.ButterflyWriteTest()                                   #Test time vary by head
#        self.SimulateWorkLoadSIOPTest(mode = 'OLTP')                #Test time fixed
#        self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')         #Test time fixed
#        self.DataErasureTest()                                      #Test time vary by head
#        self.DataErasureTest2_CHS()                                 #Test time vary by head
#
#        self.SystemReadyTest(3)
#
#        self.ZeroDisk()


###########################################################################################################
class CNETAPPMantaRay(CState):
   """
      NetApp MantaRay Screen
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.DEBUG = 0

      if self.dut.driveattr.get('NETAPP_V3','NONE') != 'PASS' :
         self.dut.driveattr['NETAPP_V3'] = 'FAIL'

         self.getBasicDriveInfo()
         self.PowerCycleTest()
         self.Intialization()
         self.SeekTest_CHS()
         self.ButterflyWriteTest()
         self.SystemReadyTest(3)
         self.BandSeqRWCmpTest()
         self.StressedPinchTest()
         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')
         self.PowerCycleTest()
         self.Intialization()
         self.ButterflyWriteTest()
         self.PowerCycleTest()
         self.Intialization()
         self.BandSeqRWCmpTest()
         self.DataErasureTest()
         self.SystemReadyTest(3)
         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')
         self.DataErasureTest2_CHS()
         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')
         self.PowerCycleTest()
         self.Intialization()
         self.StressedPinchTest()
         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')
         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')
         self.DataErasureTest()
         self.BandSeqRWCmpTest()
         self.PowerCycleTest()
         self.Intialization()
         self.DataErasureTest2_CHS()
         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')
         self.AdjacentPinch_CHS()
         self.DataErasureTest()
         self.PowerCycleTest()
         self.Intialization()
         self.DataErasureTest2_CHS()
         self.PowerCycleTest()
         self.Intialization()
         self.SimulateWorkLoadSIOPTest(mode = 'OLTP')
         self.SeekTest_CHS()
         self.ButterflyWriteTest()
         self.SimulateWorkLoadSIOPTest(mode = 'FILE_SERVER')
         self.AdjacentPinch_CHS()
         self.SeekTest_CHS()
         self.PowerCycleTest()
         self.Intialization()
         self.ButterflyWriteTest()
         self.PowerCycleTest()
         self.Intialization()
         self.FullWriteScreen()                                                                    # Perform full-pack timed write in place of Zero Pattern write
         self.FullReadScreen()                                                                     # Perform read pass w/timing in place of DST Long

         self.dut.driveattr['NETAPP_V3'] = 'PASS'


   def PowerCycleTest(self):
      ScrCmds.insertHeader('Power Cycle')
      objPwrCtrl.powerCycle(offTime=20, onTime=35, ataReadyCheck = True)


   def Intialization(self):
      ScrCmds.insertHeader("Unlock Seagate")
      try:
         ICmd.UnlockFactoryCmds()
      except:
         self.PowerCycleTest()


   def SeekTest_CHS(self,):                                                                        # Currently no spec applied in this test
      ScrCmds.insertHeader('NetApp : Full Seek test : BEGIN')
      sptCmds.enableDiags()
      starttime = time.time()

      seekType = int(TP.netapp_seekTest['seek_type'])
      loop_Seek = int(TP.netapp_seekTest['loop_Seek'])
      loop_Test = int(TP.netapp_seekTest['loop_Test'])

      objMsg.printMsg('SeekTest : seek_type : %d' % seekType)
      objMsg.printMsg('SeekTest : loop_Test : %d' % loop_Test)

      if testSwitch.virtualRun or testSwitch.FE_0152991_426568_P_SHORT_NET_APP_SCREEN:
         loop_Seek  = 1
         loop_Test  = 1

      for loop in range(loop_Test):
         for cur_hd in range(self.dut.imaxHead):
            objMsg.printMsg('NetApp Full Stroke Seek Head : %d' % cur_hd)
            sptCmds.sendDiagCmd('A0', raiseException = 0, stopOnError = False)                     # Set Test Space
            sptCmds.gotoLevel('2')
            sptCmds.sendDiagCmd('S0,%x' % cur_hd, raiseException = 0, stopOnError = False)         # Seek to test head
            sptCmds.gotoLevel('3')
            sptCmds.sendDiagCmd('D999999999,2,5000',timeout = 300, printResult = True, raiseException = 0, stopOnError = False)           # Perform full strok seek

            objMsg.printMsg('NetApp Random Seek Head : %d' % cur_hd)
            sptCmds.sendDiagCmd('A0', raiseException = 0, stopOnError = False)                     # Set Test Space
            sptCmds.gotoLevel('2')
            sptCmds.sendDiagCmd('S0,%x'% cur_hd, raiseException = 0, stopOnError = False)          # Seek to test head
            sptCmds.gotoLevel('3')
            sptCmds.sendDiagCmd('D0,%x,%x'%(seekType,loop_Seek),timeout = 300, printResult = True, raiseException = 0, stopOnError = False) # Perform random seek

            if(self.DEBUG):
               objMsg.printMsg('SeekTest Head : %d, Time : %d' % (cur_hd, (time.time() - starttime)))

      sptCmds.enableESLIP()
      ScrCmds.insertHeader('Full Seek test Time Usage : %d' %(time.time() - starttime))
      ScrCmds.insertHeader('NetApp : Full Seek test : END')


   def ButterflyWriteTest(self):
      ScrCmds.insertHeader('NetApp : Butterfly Write Test : BEGIN')
      starttime = time.time()

      loop_count = int(TP.netapp_butterflyWriteTest['loop_Count'])
      run_time = TP.netapp_butterflyWriteTest['run_time']
      if testSwitch.FE_0152991_426568_P_SHORT_NET_APP_SCREEN:
         loop_count = 1
      objMsg.printMsg('loop_count : %d' %loop_count)
      objMsg.printMsg('run_time : %d Mins' %(run_time / 60))

      objPwrCtrl.powerCycle(5000,12000,10,30)

      try:
         WPrm = (ICmd.params.prm_510_BUTTERFLY).copy()
         WPrm['TOTAL_LBA_TO_XFER'] = TP.netapp_butterflyWriteTest['TOTAL_LBA_TO_XFER']
      except:
         WPrm = TP.prm_510_BUTTERFLY
         WPrm['TOTAL_BLKS_TO_XFR'] = TP.netapp_butterflyWriteTest['TOTAL_BLKS_TO_XFR']

      for loop in xrange(loop_count):
         ICmd.St(WPrm)
         if(self.DEBUG):
            objMsg.printMsg('ButterflyWriteTest Loop : %d, Time : %d' % (loop, (time.time() - starttime)))
         if time.time() - starttime >= run_time:
            break

      ScrCmds.insertHeader('Butterfly Write Time Usage : %d' %(time.time() - starttime))
      ScrCmds.insertHeader('NetApp : Butterfly Write Test : END')


   def SystemReadyTest(self, power_cycle_count = 3):
      ScrCmds.insertHeader('NetApp : System Ready Test : BEGIN')
      starttime = time.time()

      for cycle in range(1, power_cycle_count + 1):
         objMsg.printMsg("Power Cycle %d"% cycle)
         self.PowerCycleTest();
         time.sleep(90)

      ScrCmds.insertHeader('System Ready Test Time Usage : %d' %(time.time() - starttime))
      ScrCmds.insertHeader('NetApp : System Ready Test : END')


   def FullWriteScreen(self):
      ScrCmds.insertHeader('NetApp : Full Disk Write Test : BEGIN')
      starttime = time.time()

      self.enableWriteCache()

      objMsg.printMsg('Start Write Pass')
      try:
         WSamePrm = (ICmd.params.prm_510_CMDTIME_WR).copy()
      except:
         WSamePrm = TP.prm_510_CMDTIME_WR
      if testSwitch.FE_0174228_395340_P_AUTO_RETRY_FPW_R_NETAPP_MQM:
         try:
            ICmd.St(WSamePrm)
         except ScriptTestFailure,(failureData):
            objMsg.printMsg("ScriptTestFailure from prm_510_CMDTIME_WR")
            if failureData[0][2] in [11049]:
               objMsg.printMsg("Retry prm_510_CMDTIME_WR")
               objPwrCtrl.powerCycle()
               ICmd.St(WSamePrm)
            else:
               raise
         except:
            objMsg.printMsg("Retry prm_510_CMDTIME_WR")
            objPwrCtrl.powerCycle()
            ICmd.St(WSamePrm)
      else:
         ICmd.St(WSamePrm)

      self.dut.driveattr['WRITE_SAME'] = 'PASS'
      self.dut.driveattr['ZERO_PTRN_RQMT'] = '20'

      objPwrCtrl.powerCycle()

      ScrCmds.insertHeader('Write Pass Test Time Usage : %d' %(time.time() - starttime))
      ScrCmds.insertHeader('NetApp : Full Disk Write Test : END')


   def FullReadScreen(self):
      ScrCmds.insertHeader('NetApp : Full Disk Read Test : BEGIN')
      starttime = time.time()

      objMsg.printMsg('Start Read Pass')
      try:
         WSamePrm = (ICmd.params.prm_510_CMDTIME_RD).copy()
      except:
         WSamePrm = TP.prm_510_CMDTIME_RD
      if testSwitch.FE_0174228_395340_P_AUTO_RETRY_FPW_R_NETAPP_MQM:
         try:
            ICmd.St(WSamePrm)
         except ScriptTestFailure,(failureData):
            objMsg.printMsg("ScriptTestFailure from prm_510_CMDTIME_RD")
            if failureData[0][2] in [11049]:
               objMsg.printMsg("Retry prm_510_CMDTIME_RD")
               objPwrCtrl.powerCycle()
               ICmd.St(WSamePrm)
            else:
               raise
         except:
            objMsg.printMsg("Retry prm_510_CMDTIME_RD")
            objPwrCtrl.powerCycle()
            ICmd.St(WSamePrm)
      else:
         ICmd.St(WSamePrm)

      objPwrCtrl.powerCycle()

      ScrCmds.insertHeader('Read Pass Test Time Usage : %d' %(time.time() - starttime))
      ScrCmds.insertHeader('NetApp : Full Disk Read Test : END')


   def BandSeqRWCmpTest(self):
      ScrCmds.insertHeader('NetApp : Banded Sequential Write/Read Compare Test : BEGIN')
      starttime = time.time()

      increasing_step = int(TP.netapp_bandSeqRWCmpTest['increasing_step'])
      pattern_count =TP.netapp_bandSeqRWCmpTest['pattern_count']
      stepLBA =TP.netapp_bandSeqRWCmpTest['stepLBA']
      loop_Count =TP.netapp_bandSeqRWCmpTest['loop_Count']
      increasing_step = ((increasing_step * 5) / self.dut.imaxHead)

      objPwrCtrl.powerCycle()
      self.enableWriteCache()

      if testSwitch.virtualRun or testSwitch.FE_0152991_426568_P_SHORT_NET_APP_SCREEN:
         loop_Count = 1
         pattern_count = 1
         increasing_step = 50

      objMsg.printMsg('increasing_step : %d' %increasing_step)
      objMsg.printMsg('imaxHead : %d' %self.dut.imaxHead)
      objMsg.printMsg('pattern_count : %d' %pattern_count)
      objMsg.printMsg('stepLBA : %d' %stepLBA)
      objMsg.printMsg('loop_Count : %d' %loop_Count)

      for iCount in range(loop_Count):
         for pattern in range(int(pattern_count)):
            if pattern == 0 :                                                       # Fill Write Buffer with (Incremental, Shifting bit, Counting,Random )
               self.fillIncrementalBuff()
            elif pattern == 1 :
               self.fillShiftingBitBuff()
            elif pattern == 2 :
               self.fillCountingBuff()
            elif pattern == 3 :
               self.fillRandomBuff()

            blockSize = int((1024 * 1024 * 8) / 512)                                # ~ 8M data size
            sector_count = step_lba = stepLBA                                       # 32K xfer size
            Stamp = 0
            Compare = 0
            test_loop = 1

            for band in range(0,100,increasing_step):                               # Write Data Phase
               targetLBA = int(self.maxLBA * band / 100)
               result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+blockSize-1, step_lba, sector_count, Stamp, Compare, test_loop)

               if self.DEBUG or result['LLRET'] != OK:
                  objMsg.printMsg('Write - Step :  %d' % increasing_step)
                  objMsg.printMsg('Write - LBA :  %x' % targetLBA)
                  objMsg.printMsg('Write - blockSize :  %x' % blockSize)
                  objMsg.printMsg('Write - step_lba :  %d' % step_lba)
                  objMsg.printMsg('Write - sector_count :  %x' % sector_count)
                  objMsg.printMsg('Write - Loop :  %d' % band)
                  objMsg.printMsg('Write - maxLBA :  %d' % self.maxLBA)
                  objMsg.printMsg('Write - Result :  %s' %str(result))
               if result['LLRET'] != OK:
                  ScrCmds.raiseException(10888, "Write Banded Data Failed : %s" %str(result))

            result = ICmd.BufferCopy(RBF,0,WBF,0,512)
            if result['LLRET'] != OK:
               ScrCmds.raiseException(10888,'BufferCopy Failed! : %s' % str(result))

            Compare = 1
            for band in range(0,100,increasing_step):                               # Read Data Phase
               targetLBA = int(self.maxLBA * band / 100)
               result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+blockSize-1, step_lba, sector_count, Stamp, Compare, test_loop)

               if result['LLRET'] != OK:
                  objMsg.printMsg('Read - Step :  %d' % increasing_step)
                  objMsg.printMsg('Read - LBA :  %x' % targetLBA)
                  objMsg.printMsg('Read - blockSize :  %x' % blockSize)
                  objMsg.printMsg('Read - step_lba :  %d' % step_lba)
                  objMsg.printMsg('Read - sector_count :  %x' % sector_count)
                  objMsg.printMsg('Read - Loop :  %d' % band)
                  objMsg.printMsg('Read - maxLBA :  %d' % self.maxLBA)
                  ScrCmds.raiseException(10888, "Read Banded Data Failed : %s" %str(result))

               if self.DEBUG:
                  objMsg.printMsg('Read - Result %s' %str(result))

      ScrCmds.insertHeader('Banded Sequential Write/Read Compare Test Time Usage : %d' %(time.time() - starttime))
      ScrCmds.insertHeader('NetApp : Banded Sequential Write/Read Compare Test : END')


   def StressedPinchTest(self):
      ScrCmds.insertHeader('NetApp : Stressed Pinch Test : BEGIN')
      starttime = time.time()

      loop_Count = TP.netapp_stressedPinchTest['loop_Count']
      write_Loop = TP.netapp_stressedPinchTest['loop_Write']
      if testSwitch.FE_0152991_426568_P_SHORT_NET_APP_SCREEN:
         loop_Count = 1
         write_Loop = 1
      objMsg.printMsg('StressedPinchTest - loop_Count : %d' %loop_Count)
      objMsg.printMsg('StressedPinchTest - write_Loop : %d' %write_Loop)

      objPwrCtrl.powerCycle()
      self.enableWriteCache()

      self.fillRandomBuff()

      block_size = int((1024 * 1024) / 512)                          # Set block size to 1 MB
      midLBA = int(self.maxLBA /2)
      upperLBA = midLBA + block_size
      lowerLBA = midLBA - block_size

      if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
         from serialScreen import sptDiagCmds
         oSerial = sptDiagCmds()
         oSerial.enableDiags()
         lowSeek = oSerial.translateLBA(0)['PHYSICAL_CYL']
         midSeek = oSerial.translateLBA(int(midLBA))['PHYSICAL_CYL']
         upperSeek = oSerial.translateLBA(int(upperLBA))['PHYSICAL_CYL']
         maxSeek = oSerial.translateLBA(int(self.maxLBA))['PHYSICAL_CYL']
         try:
            self.UnlockFactoryCmds()
         except:
            objPwrCtrl.powerCycle(offTime=20, onTime=35, ataReadyCheck = True)
      else:
         lowSeek = 0
         midSeek = midLBA
         upperSeek = upperLBA
         maxSeek = self.maxLBA

      for loop in range(loop_Count):
         self.WriteRead(midLBA, block_size, 'WC')                    # Write to LBA (Max LBA/2) & verify (Max LBA/2).
         self.WriteRead(upperLBA, block_size, 'WC')                  # Write to LBA (Max LBA/2 + 1024Kb) & verify LBA (Max LBA/2 +1024Kbytes)
         self.WriteRead(lowerLBA, block_size, 'WC')                  # Write to LBA (Max LBA/2 ? 1024Kb) & verify LBA (Max LBA/2 -1024Kbytes)

         for i in range(0,write_Loop):
            self.RandomSeekTimed(upperSeek, maxSeek, 10000)          # Seeks to random LBAs in the range (Max LBA/2 + 1024Kbytes) to Max LBA
            self.WriteRead(midLBA, block_size, 'WC')                 # Write to LBA (Max LBA/2) & verify (Max LBA/2).
            self.RandomSeekTimed(lowSeek, midSeek, 10000)            # Seek to random LBA in the range 0 to (Max LBA/2)
            self.WriteRead(midLBA, block_size, 'W')                  # Write to LBA (Max LBA/2) & verify (Max LBA/2).
            self.WriteRead(upperLBA, block_size, 'R')                # Read LBA (Max LBA/2 + 1024Kb)
            self.WriteRead(lowerLBA, block_size, 'R')                # Read LBA (Max LBA/2 ? 1024Kb)

      ScrCmds.insertHeader('Stressed Pinch Test Time Usage : %d' %(time.time() - starttime))
      ScrCmds.insertHeader('NetApp : Stressed Pinch Test : END')


   def RandomSeekTimed(self, min, max, numSeeks):

      if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
         result = ICmd.RandomSeekTimeCyl(min, max, numSeeks, timeout = 120, exc=0)
      else:
         result = ICmd.RandomSeekTime(min, max, numSeeks, seekType = 28, timeout = 1800, exc=0)

      if result['LLRET'] != OK:
         if self.DEBUG:
            objMsg.printMsg('RandomSeekTime Range: %s - %s, Result: %s' %(min_LBA, max_LBA, str(result)))
         ScrCmds.raiseException(11044, "Random Seek Error")


   def SimulateWorkLoadSIOPTest(self, mode = 'NONE'):
      ScrCmds.insertHeader('NetApp : Simulate WorkLoad SIOP Test %s : BEGIN' % mode)
      starttime = time.time()

      import random
      from Rim import objRimType

      lba_size = TP.netapp_simulateWorkLoadSIOPTest['lba_size']
      run_time = TP.netapp_simulateWorkLoadSIOPTest['run_time']

      if testSwitch.virtualRun or testSwitch.FE_0152991_426568_P_SHORT_NET_APP_SCREEN:
         run_time = 5
      if self.DEBUG:
         objMsg.printMsg('lba_size : %d' %lba_size)
         objMsg.printMsg('run_time : %d' %run_time)

      while True:
         if mode == 'FILE_SERVER':
            if testSwitch.FE_0153302_426568_REPLACE_WORKLOAD_SIOP_W_T_597 and objRimType.IOInitRiser():
               ICmd.DriveOperationSimulation(4,1,0,30, int(128 * 1024/ lba_size) )
            else:
               random_value = random.random()
               startLBA = 0
               lba_count = 0

               if random_value <= 0.1:                                                                   # Random location
                  startLBA = long(random.randrange(long(self.maxLBA *0.01), long(self.maxLBA)))
               elif random_value <=(0.1 + 0.3):
                  startLBA = long(random.randrange(long(self.maxLBA *0.3), long(self.maxLBA *0.6)))
               else:
                  startLBA = long(random.randrange(int(self.maxLBA *0), long(self.maxLBA *0.1)))

               random_value = random.random()

               if random_value <= 0.3:                                                                   # Random transfer size
                  lba_count = long(random.randrange(long(2 * (1024 /lba_size)), long(32 * 1024/ lba_size))) # 2KB - 32Kb
               else:
                  lba_count = long(random.randrange(long(32 * 1024/lba_size),  long(128 * 1024/ lba_size))) # 32KB - 128Kb
               if testSwitch.FE_0152991_426568_P_SHORT_NET_APP_SCREEN:
                  lba_count = 1

               random_value = random.random()

               if random_value <= 0.2:                                                                   # Random RW mode. Read:Write ratio of 4:1
                  result = ICmd.WriteSectors(startLBA, lba_count)
                  if self.DEBUG:
                     objMsg.printMsg('WriteSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))
                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Write Failed %s" % str(result))

               else:
                  result = ICmd.ReadSectors(startLBA, lba_count)
                  if self.DEBUG:
                     objMsg.printMsg('ReadSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))
                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Read Failed %s" % str(result))

         elif mode == 'OLTP':
            if testSwitch.FE_0153302_426568_REPLACE_WORKLOAD_SIOP_W_T_597 and objRimType.IOInitRiser():
               ICmd.DriveOperationSimulation(4,1,0,30, int(4 * 1024/ lba_size))
            else:
               random_value = random.random()
               startLBA = 0
               lba_count = 0

               if random_value <= 0.2:                                                                   # Random location
                  startLBA = long(random.randrange(long(self.maxLBA *0.01), long(self.maxLBA)))
               elif random_value <=(0.2 + 0.3):
                  startLBA = long(random.randrange(long(self.maxLBA *0.1), long(self.maxLBA *0.3)))
               else:
                  startLBA = long(random.randrange(long(self.maxLBA * 0.3), long(self.maxLBA *0.6)))

               random_value = random.random()

               if random_value <= 0.3:                                                                   # Random transfer size
                  lba_count = int(random.randrange( int(4 * 1024/ lba_size),  int(8 * 1024/ lba_size)))  # 4KB - 8Kb
               else:
                  lba_count = int(random.randrange( int(1 * 1024/ lba_size),  int(4 * 1024/ lba_size)))  # 1KB - 4Kb

               if testSwitch.FE_0152991_426568_P_SHORT_NET_APP_SCREEN:
                  lba_count = 1
               random_value = random.random()

               if random_value <= 0.2:                                                                   # Random RW mode
                  result = ICmd.WriteSectors(startLBA, lba_count)
                  if self.DEBUG:
                     objMsg.printMsg('WriteSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))
                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Write Failed %s" % str(result))

               else:
                  result = ICmd.ReadSectors(startLBA, lba_count)
                  if self.DEBUG:
                     objMsg.printMsg('ReadSectors LBA : %d , LBA Count : %d , Byte : %d' % (startLBA, lba_count, (lba_size * lba_count)))
                  if result['LLRET'] != OK:
                     ScrCmds.raiseException(10888,"Simulate Work Load SIOP : Read Failed %s" % str(result))

         pause_time = random.randrange(1, 10)
         ScriptPause(pause_time)

         if(self.DEBUG):
            objMsg.printMsg('SimulateWorkLoadSIOPTest random %s, Time : %d' % (mode, (time.time() - starttime)))

         if ((time.time() - starttime) > run_time) or testSwitch.virtualRun:
            break

      ScrCmds.insertHeader('Simulate WorkLoad SIOP  %s Time Usage : %d' % (mode, (time.time() - starttime)))
      ScrCmds.insertHeader('NetApp : Simulate WorkLoad SIOP Test %s : END' % mode)


   def DataErasureTest(self):
      ScrCmds.insertHeader('NetApp : Data Erasure Test : BEGIN')
      starttime = time.time()

      lba_size = TP.netapp_dataErasureTest['lba_size']
      data_size = int((TP.netapp_dataErasureTest['data_size'] / 5) * self.dut.imaxHead)   # 2GB Data Size
      loop_Count = TP.netapp_dataErasureTest['loop_Count']
      pattern_count  = TP.netapp_dataErasureTest['pattern_count']

      result = ICmd.SetFeatures(0x03, 0x47)                                               # Set DMA Mode UDMA 7 (UDMA150)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888,'Set DMA Mode UDMA 7 Failed! : %s' % str(result))
      else:
         objMsg.printMsg('Set DMA Mode UDMA 7  : %s' % str(result))

      self.enableWriteCache()

      if testSwitch.virtualRun or testSwitch.FE_0152991_426568_P_SHORT_NET_APP_SCREEN:
         loop_Count = 1
         pattern_count = 1

      for i in range(loop_Count):
         for pattern in range(pattern_count):                                             # Fill Write Buffer with (Random , Incremental, Shifting bit, Counting):
            if pattern == 0 :                                                             # Fill Write Buffer with (Incremental, Shifting bit, Counting,Random )
               self.fillRandomBuff()
            if pattern == 1 :
               self.fillIncrementalBuff()
            if pattern == 2 :
               self.fillShiftingBitBuff()
            if pattern == 3 :
               self.fillCountingBuff()

            targetLBA =  int(self.maxLBA * 0.02)                                          # OD : 2% from OD
            self.ErasureTest(targetLBA,data_size,lba_size)

            targetLBA =  int(self.maxLBA * 0.5)                                           # OD : 50% of total LBA
            self.ErasureTest(targetLBA,data_size,lba_size)

            targetLBA =  int(self.maxLBA * 0.98)                                          # ID : 2% from ID
            self.ErasureTest(targetLBA,data_size,lba_size)

      ScrCmds.insertHeader('Data Erasure Test Time Usage : %d' %(time.time() - starttime))
      ScrCmds.insertHeader('NetApp : Data Erasure Test : END')


   def DataErasureTest2_CHS(self):
      ScrCmds.insertHeader('NetApp : Data Erasure Test 2 : BEGIN')
      sptCmds.enableDiags()
      starttime = time.time()

      loop_Write = TP.netapp_dataErasureTest2['loop_Write']

      if testSwitch.FE_0152991_426568_P_SHORT_NET_APP_SCREEN:
         loop_Write = 1
      for cur_hd in range(self.dut.imaxHead):
         od_cylinder = self.zones[cur_hd][0]
         md_cylinder = self.zones[cur_hd][int(self.dut.numZones / 2)]
         id_cylinder = self.zones[cur_hd][int(self.dut.numZones - 1)] - 1

         if testSwitch.FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK:
            retries = 3
         else:
            retries = 1
         for retry in range(retries):
            try:
               objMsg.printMsg('DataErasureTest2 Test Head %d ' % cur_hd)
               sptCmds.sendDiagCmd('/2P1212',raiseException = 0, stopOnError = False)                                                  # Fill random pattern

               #write 1MB data to center of surface
               sptCmds.sendDiagCmd('/2A0',raiseException = 0, stopOnError = False)                                                     # Set Test Space
               sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd), raiseException = 0)                                              # Seek to MD (center track)
               sptCmds.sendDiagCmd('/2W0,%x' % (0xffff))                                                                               # Write 1 track

               #Write/Read 1000 loops using diagnostic batch file
               objMsg.printMsg('DataErasureTest2 Test Read/Write %d loops ' % loop_Write)
               sptCmds.sendDiagCmd('/6E', altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)         # Start Batch File
               sptCmds.sendDiagCmd('*7,%x,1'% 2, altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)  # Set Loop Count 1 to 10000
               sptCmds.sendDiagCmd('@2', altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)          # Batch File Label - Label 2

               sptCmds.sendDiagCmd('/2A8,%x,,%x' % (md_cylinder + 1,cur_hd), altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False) # Set Test Space
               sptCmds.sendDiagCmd('/2A9,%x,,%x' % (id_cylinder,cur_hd), altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)     # From Mid +1 to Extreme ID
               sptCmds.sendDiagCmd('/2A106', altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                 # Random cylinder random sector
               sptCmds.sendDiagCmd('/2L,%x' % loop_Write, altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                    # Perform 10K Write
               sptCmds.sendDiagCmd('/2W', altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                    # Write Data for 1 sector

               sptCmds.sendDiagCmd('/2A8,%x,,%x' % (od_cylinder,cur_hd), altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)     # Set Test Space
               sptCmds.sendDiagCmd('/2A9,%x,,%x' % (md_cylinder -1,cur_hd), altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)  # From OD to MD
               sptCmds.sendDiagCmd('/2A106', altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                 # Random cylinder random sector
               sptCmds.sendDiagCmd('/2L,%x' % loop_Write, altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                    # Perform 10K Write
               sptCmds.sendDiagCmd('/2W', altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                    # Write Data for 1 sector

               sptCmds.sendDiagCmd('*8,2,1', altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)      # Decrement Loop Count 1 and Branch to Label 2 if not 0
               sptCmds.sendDiagCmd('|', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                             # End Batch File
               sptCmds.sendDiagCmd('B,0',timeout = 2400, stopOnError = False)                                                          # Run Batch File

               sptCmds.sendDiagCmd('/2AD', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                          # Reset Test Space
               sptCmds.sendDiagCmd('/2A0', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                          # Set Test Space
               sptCmds.sendDiagCmd('/2S%x,%x' % (md_cylinder,cur_hd), printResult = self.DEBUG, raiseException = 0)                    # Seek to MD (center track)
               sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff), printResult = self.DEBUG)                                                     # Read Verify 1 track
               break

            except Exception, e:
               if e[0][2] == 13426 and testSwitch.FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK:
                  objMsg.printMsg('Fail from invalid track retry on next 100 track')
                  objMsg.printMsg('Retry at loop %d'%(retry+1))
                  od_cylinder +=100
                  md_cylinder +=100
                  id_cylinder -=100
               else:
                  raise

      sptCmds.enableESLIP()
      ScrCmds.insertHeader('Data Erasure Test 2 Time Usage : %d' %(time.time() - starttime))
      ScrCmds.insertHeader('NetApp : Data Erasure Test 2 : END')


   def ErasureTest(self,targetLBA, blockSize,lba_size):
      step_lba = sector_size = 256
      loopCount = 10000

      if testSwitch.FE_0152991_426568_P_SHORT_NET_APP_SCREEN:
         loopCount = 1

      result = ICmd.Seek(targetLBA)      # Seek to LBA 0
      if result['LLRET'] != OK:
         objMsg.printMsg('Seek cmd Failed!')

      result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+ blockSize, step_lba, sector_size)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888,'SequentialWriteDMAExt Failed! : %s' % str(result))
      else:
         if self.DEBUG:
            objMsg.printMsg('Write Data Complete! : %s' % str(result))

      result = ICmd.RandomSeekTime(targetLBA, targetLBA + (self.maxLBA * 0.02 ), loopCount)           # Random Seek 10000 times ;targetLBA + 2G + 2%
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Random Seek Error : %s" % str(result))
      else:
         if self.DEBUG:
            objMsg.printMsg('Random Seek ! : %s' % str(result))

      result = ICmd.BufferCopy(RBF,0,WBF,0,512)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888,'BufferCopy Failed! : %s' % str(result))

      result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+ blockSize, step_lba, sector_size)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888,'SequentialReadVerifyExt Failed! : %s' % str(result))
      else:
         if self.DEBUG:
            objMsg.printMsg('Read Verify Data Complete! ! : %s' % str(result))


   def AdjacentPinch_CHS(self):
      ScrCmds.insertHeader('NetApp : Adjacent Pinch : BEGIN')
      sptCmds.enableDiags()
      starttime = time.time()

      loop_Count = TP.netapp_adjacentPinch['loop_Count']
      loop_Write = TP.netapp_adjacentPinch['loop_Write']

      if self.DEBUG:
         objMsg.printMsg('adj loop_Count : %d' %loop_Count)
         objMsg.printMsg('loop_Write : %d' %loop_Write)

      if testSwitch.virtualRun or testSwitch.FE_0152991_426568_P_SHORT_NET_APP_SCREEN:
         loop_Count = 1
         loop_Write = 1

      for loop in range(loop_Count):
         for cur_hd in range(self.dut.imaxHead):

            od_cylinder = self.zones[cur_hd][0]
            md_cylinder = self.zones[cur_hd][int(self.dut.numZones / 2)]
            id_cylinder = self.zones[cur_hd][int(self.dut.numZones - 1)] - 1


            if testSwitch.FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK:
               retries = 3
            else:
               retries = 1
            for retry in range(retries):
               objMsg.printMsg('AdjacentPinch OD Test Head : %d' % cur_hd)
               try:
                  sptCmds.sendDiagCmd('/2P1212', printResult = True, raiseException = 0, stopOnError = False)                                         # Fill random pattern
                  sptCmds.sendDiagCmd('A0', printResult = True, raiseException = 0, stopOnError = False)                                              # Set Test Space

                  sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd), printResult = True, raiseException = 0, stopOnError = False)               # Seek ExtremeOD +1 trk  (center track)
                  sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = True)                                                         # Write 1 track

                  sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd), printResult = True, raiseException = 0, stopOnError = False)                 # Seek ExtremeOD trk  (upper track)
                  sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = True)                                                         # Write 1 track

                  sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd), printResult = True, raiseException = 0, stopOnError = False)               # Seek ExtremeOD +2 trk  (lower track)
                  sptCmds.sendDiagCmd('/2Q0,%x' % (0xffff),timeout = 120, printResult = True)                                                         # Write 1 track

                  #Write/Read 1000 loops using diagnostic batch file

                  objMsg.printMsg('AdjacentPinch OD Test Read/Write %d loops ' % loop_Write)
                  sptCmds.sendDiagCmd('/6E', altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                     # Start Batch File
                  sptCmds.sendDiagCmd('*7,%x,1' % loop_Write , altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)   # Set Loop Count 1 to 1000
                  sptCmds.sendDiagCmd('@2', altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                      # Batch File Label - Label 2

                  sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+1,cur_hd), altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)   # Seek ExtremeOD +1 trk  (center track)
                  sptCmds.sendDiagCmd('/2W0,%x' % (0xffff), altPattern = '-', printResult = self.DEBUG)                                                           # Write 1 track

                  sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder,cur_hd), altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)     # Seek ExtremeOD trk  (upper track)
                  sptCmds.sendDiagCmd('/2R0,%x' % (0xffff), altPattern = '-', printResult = self.DEBUG)                                                           # Write 1 track

                  sptCmds.sendDiagCmd('/2S%x,%x' % (od_cylinder+2,cur_hd), altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)   # Seek ExtremeOD +2 trk  (lower track)
                  sptCmds.sendDiagCmd('/2R0,%x' % (0xffff),altPattern = '-', printResult = self.DEBUG)                                                            # Write 1 track

                  sptCmds.sendDiagCmd('*8,2,1', altPattern = '-', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                  # Decrement Loop Count 1 and Branch to Label 2 if not 0
                  sptCmds.sendDiagCmd('|', printResult = self.DEBUG, raiseException = 0, stopOnError = False)                                         # End Batch File
                  sptCmds.sendDiagCmd('B,0',timeout = 1200,printResult = True, raiseException = 0, stopOnError = False)                               # Run Batch File

                  break
               except Exception, e:
                  if e[0][2] == 13426 and testSwitch.FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK:
                     objMsg.printMsg('Fail from invalid track retry on next 100 track')
                     objMsg.printMsg('Retry at loop %d'%(retry+1))
                     od_cylinder += 100
                  else:
                     raise

      sptCmds.enableESLIP()
      ScrCmds.insertHeader('Adjacent Pinch Test Time Usage : %d' %(time.time() - starttime))
      ScrCmds.insertHeader('NetApp : Adjacent Pinch Test : END')


   def WriteRead(self,targetLBA, blockSize, mode = 'NONE', step_lba = 256, sector_count = 256, Stamp = 0, Compare = 0, test_loop = 1):

      if mode.find('C') >= 0:
         Compare = 1

      if mode.find('W')>= 0:
         if self.DEBUG:
            objMsg.printMsg('SequentialWriteVerify : startLBA : %d,  endLBA: %d,, Stamp : %d, Compare : %d, test_loop : %d ' % (targetLBA, (targetLBA+blockSize-1),Stamp, Compare, test_loop))
         result = ICmd.SequentialWriteDMAExt(targetLBA, targetLBA+blockSize-1, step_lba, sector_count,Stamp, Compare, test_loop)       # Write
         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,'SequentialWriteDMAExt Failed! : %s' % str(result))

      if mode.find('R') >= 0:
         if self.DEBUG:
            objMsg.printMsg('SequentialReadVerifyExt : startLBA : %d,  endLBA: %d, Stamp : %d, Compare : %d, test_loop : %d ' % (targetLBA, (targetLBA+blockSize-1),Stamp, Compare, test_loop))
         result = ICmd.SequentialReadVerifyExt(targetLBA, targetLBA+blockSize-1, step_lba, sector_count,Stamp, Compare, test_loop)     # Read
         if result['LLRET'] != OK:
            ScrCmds.raiseException(10888,"SequentialReadVerifyExt Failed: %s" % str(result))


   def fillIncrementalBuff(self):
      result = ICmd.FillBuffInc(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Fill Incremental Buffer Error")
      objMsg.printMsg('Fill Incremental Buffer Complete.')


   def fillRandomBuff(self):
      result = ICmd.FillBuffRandom(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Fill Random Buffer Error")
      objMsg.printMsg('Fill Random Buffer Complete.')


   def fillShiftingBitBuff(self):
      import array
      data_pattern = array.array('H')
      data  = 0xFFFF
      increment = -1

      for i in xrange(0,0x20000 / 2, 2):                          # Prepare Shifting Bit Pattern (Total Buffer Size = 0x20000 byte)
         data = data + increment

         if data == 0xFFFF or data == 0:
            increment = -increment

         data_pattern.insert(i, 0)
         data_pattern.insert(i + 1, data & 0xFFFF)

      write_buffer = ''.join([(chr(num >>8) + chr(num & 0xff)) for num in (data_pattern)])
      result = ICmd.FillBuffer(WBF,0,write_buffer)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Fill Shifting Bit Buffer Error")
      objMsg.printMsg('Fill Shifting Bit Buffer Complete.')


   def fillCountingBuff(self):
      import array
      data_pattern = array.array('H')

      for i in xrange(0,0x20000 / 2):                             # Prepare Counting Pattern (Total Buffer Size = 0x20000 byte)
         data = (i << 8) | (i + 1)
         data_pattern.insert(i + 1, data & 0xFFFF)

      write_buffer = ''.join([(chr(num >>8) + chr(num & 0xff)) for num in (data_pattern)])
      result = ICmd.FillBuffer(WBF,0,write_buffer)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(10888, "Fill Counting Buffer Error")
      objMsg.printMsg('Fill Counting Buffer Complete.')


   def getBasicDriveInfo(self):
      sptCmds.enableDiags()
      from serialScreen import sptDiagCmds
      oSerial = sptDiagCmds()
      self.numCyls, self.zones = oSerial.getZoneInfo(printResult=True)
      self.numCyls = self.numCyls[0]

      objPwrCtrl.powerCycle()
      self.maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)-1

      objMsg.printMsg("Total cylinders %s" % str(self.numCyls) )
      objMsg.printMsg("Number of Zones %s" % str(self.dut.numZones) )
      objMsg.printMsg("Zone table %s" % str(self.zones) )
      objMsg.printMsg("Max Head %s" % str(self.dut.imaxHead) )
      objMsg.printMsg("Max LBA %s" % str(self.maxLBA) )


   def enableWriteCache(self):
      if testSwitch.BF_0151111_231166_P_USE_ALL_INTF_CAPABLE_CACHE_CMD:
         ICmd.enable_WriteCache()
      else:
         if testSwitch.BF_0145549_231166_P_FIX_538_ATA_CMDS_SIC:
            SATA_SetFeatures.enable_WriteCache()
         else:
            ICmd.St(TP.enableWriteCache_538)

###########################################################################################################
class CAppleScreens_CET(CState):
   """
      Description: 
         1. Do Write DMA Ext at zone 0
         2. Do Write DMA Ext at about 60 to 70% of the drive LBA
         3. Do Write DMA Ext at last zone
         4. Do Full Pack IO Read
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.RandomWrite()
      self.FullPackRead()
      self.displaydefectlists()
      
   #-------------------------------------------------------------------------------------------------------
   def RandomWrite(self):
      
      SectorCount = 0x100
      LoopCount = 30000
      
      #Calculate Zone length and LBA Range
      #Zone Length = 8% of Max LBA Approx....Assuming MaxZones = 24 (MaxLBA/24)
      maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16)
      ZoneLength = int(maxLBA * 0.08)
      
      FirstZone_StartLBA = 0
      FirstZone_EndLBA = ZoneLength
      LastZone_StartLBA = maxLBA- ZoneLength
      LastZone_EndLBA = maxLBA - 0x100
      MidZone_StartLBA = int(maxLBA * 0.60) #60% of MaxLBA
      MidZone_EndLBA = int(maxLBA * 0.70) #70% of MaxLBA
      
      objMsg.printMsg(50*"#")
      objMsg.printMsg("Drive MaxLBA:%s ZoneLength(8%% of MaxLBA):%s" %(maxLBA,ZoneLength))
      objMsg.printMsg("SectorCount:%s Random LoopCount: %s" %(SectorCount,LoopCount))
      objMsg.printMsg("First Zone -> StartLBA:%s EndLBA:%s" %(FirstZone_StartLBA,FirstZone_EndLBA))
      objMsg.printMsg("Last Zone -> StartLBA:%s EndLBA:%s" %(LastZone_StartLBA,LastZone_EndLBA))
      objMsg.printMsg("60-70%% of MaxLBA -> StartLBA:%s EndLBA:%s" %(MidZone_StartLBA,MidZone_EndLBA))
      objMsg.printMsg(50*"#")
      
      #Clear buffer pattern to Zero
      objMsg.printMsg(".....Clear Write Buffer to Zero")
      result = ICmd.ClearBinBuff(WBF)
      if result['LLRET'] != OK:
         ScrCmds.raiseException(11044, "CAppleScreens_CET - Failed to fill buffer for zero write")
         
      #Random Write DMA Ext at zone 0
      objMsg.printMsg(".....Random Write DMA Ext at zone 0")
      res = ICmd.RandomWriteDMAExt(FirstZone_StartLBA,FirstZone_EndLBA,SectorCount,SectorCount,LoopCount)
      if res['LLRET'] != OK:
         ScrCmds.raiseException(12664, "CAppleScreens_CET - Failed Random Write DMA Ext")     

      #Random Write DMA Ext at about 60 to 70% of drive Max LBA
      objMsg.printMsg(".....Random Write DMA Ext at about 60% to 70% of drive Max LBA")
      res = ICmd.RandomWriteDMAExt(MidZone_StartLBA,MidZone_EndLBA,SectorCount,SectorCount,LoopCount)       
      if res['LLRET'] != OK:
         ScrCmds.raiseException(12664, "CAppleScreens_CET - Failed Random Write DMA Ext")     

      #Random Write DMA Ext at Last zone
      objMsg.printMsg(".....Random Write DMA Ext at Last zone")
      res = ICmd.RandomWriteDMAExt(LastZone_StartLBA,LastZone_EndLBA,SectorCount,SectorCount,LoopCount)       
      if res['LLRET'] != OK:
         ScrCmds.raiseException(12664, "CAppleScreens_CET - Failed Random Write DMA Ext")     

   #-------------------------------------------------------------------------------------------------------
   def FullPackRead(self):
      objMsg.printMsg(".....Perform Full Pack IO Read")
      oProc = CProcess()
      from Rim import objRimType
      prm_510_FPR= {
            'test_num'  : 510,
            'prm_name'  : "prm_510_FPR",
            'timeout'   : 252000,
            'spc_id'    : 1,
            "CTRL_WORD1"         : (0x10),
            "CTRL_WORD2"         : (0x2080),
            "STARTING_LBA"       : (0,0,0,0),
            "BLKS_PER_XFR"       : (0x100),
            "DATA_PATTERN0"      : (0x0000, 0x0000),
            "MAX_NBR_ERRORS"     : (0),}     #Fail on 1 Error
            #"ECC_CONTROL"        : (1),
            #"ECC_T_LEVEL"        : (0xA),   #ECC = 10
            #"DERP_RETRY_CONTROL" : (0x1E),} #Read Retry = 30

      if objRimType.CPCRiser():
         prm_510_FPR['TOTAL_BLKS_TO_XFR'] =  (0,0)# Full pack
      elif objRimType.IOInitRiser():
         prm_510_FPR['TOTAL_BLKS_TO_XFR64'] =  (0,0,0,0)# Full pack    
         
      try:
         ICmd.St(prm_510_FPR)                  
##         oProc.St(prm_510_FPR)
      except:
         objMsg.printMsg("Debug: prm_510_FPR failure... %s" %traceback.format_exc()) 
         raise                        
       
   #-------------------------------------------------------------------------------------------------------
   def displaydefectlists(self):
      #Display P-List and G-List
      ScrCmds.insertHeader("Display P-List and G-List",headChar='*')
      from base_IntfTest import CSmartDefectList
      CSmartDefectList(self.dut, params={}).run()    

###########################################################################################################
class CSony_FT2Test(CState):
   """
      Class that will perform Sony FT2 test.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
      self.writeReadMode = 0x00
      self.readMode = 0x10
      self.writeMode = 0x20
      self.sequential = 0x00
      self.random = 0x01
      from SPT_ICmd import SPT_ICmd
      self.oSPT_ICmd = SPT_ICmd()
  
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      import random
      from serialScreen import sptDiagCmds
      oSerial = sptDiagCmds()
      maxlba = int(ICmd.GetMaxLBA()['MAX48'],16)-1
      objMsg.printMsg("Maxlba = %s" % (maxlba,))

#     ScriptComment('================== Pre Sony Screen Cleanup - Full pack write and read ===================')
#     self.WriteRead(self.writeMode|self.sequential, 0, maxlba)
#     self.WriteRead(self.readMode|self.sequential, 0, maxlba)

      self.oSPT_ICmd.ClearBinBuff() 
      ScriptComment('================== Sony Screen - BDWR Screen ===================')
      DriveOff( 900 )                     
      objPwrCtrl.powerCycle(5000,12000,20,30)
      oSerial.enableDiags()
      oSerial.dumpReassignedSectorList(returnAltListLBAS = 1) #To check V4 entry before and after FT2 test

      ScriptComment('================== Sony Screen - Ran. Read with "0000" compare Test ===================') # OD Rand
      for loop in range(3): # random read 1000, do 3 times
         self.WriteRead(self.readMode|self.random, 0, 50000, 1000, compare = 1, BLKCNT= 0x10)

      ScriptComment('================== Sony Screen - Max_LBA Access Test ===================') #ID Seq
      self.WriteRead(self.readMode|self.sequential, maxlba-10000, maxlba)
      self.WriteRead(self.writeMode|self.sequential, maxlba-10000, maxlba)
      self.WriteRead(self.readMode|self.sequential, maxlba-10000, maxlba)

      ScriptComment('================== Sony Screen - Check The DCC ===================')
      self.oSPT_ICmd.IdentifyDevice()

      ScriptComment('================== Sony Screen - LBA Seq. W/R ===================') #OD Seq
      self.WriteRead(self.writeMode|self.sequential, 0, 150000)
      self.WriteRead(self.readMode|self.sequential, 0, 150000)

      ScriptComment('================== Sony Screen - ATW Test ===================')
      objMsg.printMsg("ATW at OD")
      od_SLBA = 2990*330
      od_ELBA = 3010*330
      od_MSLBA = 3000*330
      od_MELBA = 3001*330
      self.WriteRead(self.writeMode|self.sequential, od_SLBA, od_ELBA, pattern = 'CCCC')    
      for loop in range(1000): 
         objMsg.printMsg("OD loop: %s" % loop)
         self.WriteRead(self.writeMode|self.sequential, od_MSLBA, od_MELBA, pattern = 'CCCC') 
      self.WriteRead(self.readMode|self.sequential, od_SLBA, od_ELBA, pattern = 'CCCC')     

#     objMsg.printMsg("ATW at MD")
#     md_SLBA = maxlba/2-(10*310)
#     md_ELBA = maxlba/2+(10*310)
#     md_MSLBA = maxlba/2
#     md_MELBA = maxlba/2+310
#     self.WriteRead(self.writeMode|self.sequential, md_SLBA, md_ELBA, pattern = 'CCCC')
#     for loop in range(50):
#        objMsg.printMsg("MD loop: %s" % loop)
#        self.WriteRead(self.writeMode|self.sequential, md_MSLBA, md_MELBA, pattern = 'CCCC')
#     self.WriteRead(self.readMode|self.sequential, md_SLBA, md_ELBA, pattern = 'CCCC')
#
#     objMsg.printMsg("ATW at ID")
#     id_SLBA = maxlba-(5010*230)
#     id_ELBA = maxlba-(4990*230)
#     id_MSLBA = maxlba-(5000*230)
#     id_MELBA = maxlba-(4999*230)
#     self.WriteRead(self.writeMode|self.sequential, id_SLBA, id_ELBA, pattern = 'CCCC')
#     for loop in range(50):
#        objMsg.printMsg("ID loop: %s" % loop)
#        self.WriteRead(self.writeMode|self.sequential, id_MSLBA, id_MELBA, pattern = 'CCCC')
#     self.WriteRead(self.readMode|self.sequential, id_SLBA, id_ELBA, pattern = 'CCCC')

      self.WriteRead(self.writeMode|self.sequential, 2950*330, 3050*330)                   # OD cleanup
#     self.WriteRead(self.writeMode|self.sequential, maxlba/2-(50*310), maxlba/2+(50*310)) # MD cleanup
#     self.WriteRead(self.writeMode|self.sequential, maxlba-(5050*230), maxlba-(4950*230)) # ID cleanup
      self.WriteRead(self.readMode|self.sequential, 2950*330, 3050*330)                    # Verify OD cleanup
#     self.WriteRead(self.readMode|self.sequential, maxlba/2-(50*310), maxlba/2+(50*310))  #
#     self.WriteRead(self.readMode|self.sequential, maxlba-(5050*230), maxlba-(4950*230))  #

      ScriptComment('================== Sony Screen - Power On/Off Test 10 times (CSS Test) ===================')
      for loop in range(10):
         sec=random.randint(5,30)
         objPwrCtrl.powerCycle(offTime=sec)

      ScriptComment('================== Sony Screen - Random W/R 3.5K Times ===================') # MD Rand
      oSerial.enableDiags()
      self.WriteRead(self.writeReadMode|self.random, 20000000, maxlba-20000000, 3500, pattern = '12345678', compare = 1)#pattern1 =(0x90AB,0xCDEF),
      self.WriteRead(self.writeMode|self.sequential, 20000000, maxlba-20000000)

      ScriptComment('================== Sony Screen - ID Seq read  ===================') # ID Seq read
      self.WriteRead(self.readMode|self.sequential, maxlba-20000000, maxlba)

      ScriptComment('================== Sony Screen - OD Seq read  ===================') # OD Seq read
      self.WriteRead(self.readMode|self.sequential, 0, 19999999)

      ScriptComment('================== Sony Screen - DRAM Check(Data Compare Test) ===================')
      for loop in range(120):
         self.WriteRead(self.writeReadMode|self.sequential, 40000, 40000, pattern = 'Random', BLKCNT= 0x1)
      self.WriteRead(self.writeMode|self.sequential, 38000, 42000)
      self.WriteRead(self.readMode|self.sequential, 38000, 42000)

      ScriptComment('================== Sony Screen - Load/Unload Test 100 Times ===================')
      for loop in range(100):
         time.sleep(6)
         self.WriteRead(self.writeReadMode|self.random, 0, maxlba, 50)

      ScriptComment('================== Sony Screen - Ran. Write 100k ===================')
      #self.WriteRead(self.writeMode|self.random, 0, maxlba, 100000)
      self.WriteRead(self.writeMode|self.random, 0, maxlba, 1000) #For SMR change it to 1000

      ScriptComment('================== Sony Screen - 0x0000 Pattern & compare ===================') #OD seq read and compare
      self.WriteRead(self.readMode|self.sequential, 0, 23000, compare = 1)

      ScriptComment('================== Sony Screen - DST Short Test ===================')
      from GIO import CSmartDST_SPT
      CSmartDST_SPT(self.dut, params={}).DSTTest_IDE('SONY_FT2', 'Short')

      ScriptComment('================== Sony Screen -  Ran Read with "0000" Compare ===================')    #full surface rand read and compare
      self.WriteRead(self.readMode|self.random, 0, maxlba, 10000, compare = 1)

      ScriptComment('================== Sony Screen - ALL Zone Seq. Write and Read ===================')
      self.WriteRead(self.writeMode|self.sequential, 0, maxlba)
      self.WriteRead(self.readMode|self.sequential, 0, maxlba)

      ScriptComment('================== Sony Screen - ALIST Check ===================')
      reassignData, altListLBAs = oSerial.dumpReassignedSectorList(returnAltListLBAS = 1)

      if reassignData['NUMBER_OF_PENDING_ENTRIES']:
         objMsg.printMsg("%d Pending Entries found in the ALT list.  Need to perform writes at these locations" %reassignData['NUMBER_OF_PENDING_ENTRIES'])
         objMsg.printMsg('LBAs to write to: %s' % altListLBAs)
         for lba in altListLBAs:
          try:
             #oSerial.rw_LBAs(lba,lba,mode = 'W')
             self.WriteRead(self.writeMode|self.sequential, lba, lba)
          except:
             objMsg.printMsg('Unable to write to LBAs %s' % lba)
         reassignData = oSerial.dumpReassignedSectorList()
         if reassignData['NUMBER_OF_PENDING_ENTRIES']:
           ScrCmds.raiseException(10049, 'Warning Pending Entries still exist in the ALT list')

      ScriptComment('================== Sony Screen - SMART Setting ===================')
      objMsg.printMsg("Reset SMART")
      oSerial.sendDiagCmd('/1N1', printResult = True)
      objMsg.printMsg("Reset SMART PASS")
      if not testSwitch.NoIO: #switch to interface mode for subsequent IO tests
         objPwrCtrl.powerCycle()
  
   #-------------------------------------------------------------------------------------------------------
   def WriteRead(self, mode, startLBA, endLBA, cnt = 0, pattern = '00000000', compare = 0, BLKCNT= 0x100):      
      
      '''
      self.writeReadMode = 0x00
      self.readMode = 0x10
      self.writeMode = 0x20
      self.sequential = 0x00
      self.random = 0x01
      self.random_551 = 0x02
      '''
      if pattern == 'Random':
         pattern = hex(random.randint(0,0xFFFF))
         pattern = str(pattern)[2:]        

      self.oSPT_ICmd.FillBuffer(Pattern = pattern)

      if mode == 0x20:
         #Sequential Write (mode = 0x20)
         self.oSPT_ICmd.SequentialWriteDMAExt(STARTING_LBA = startLBA, MAXIMUM_LBA = endLBA, STEP_LBA = BLKCNT, BLKS_PER_XFR = BLKCNT)

      elif mode == 0x10:
         #Sequential Read  (mode = 0x10)
         self.oSPT_ICmd.SequentialReadDMAExt(STARTING_LBA = startLBA, MAXIMUM_LBA = endLBA, STEP_LBA = BLKCNT, BLKS_PER_XFR = BLKCNT, COMPARE_FLAG = compare)

      elif mode == 0x00:
         #Sequential WriteRead (mode = 0x00)
         self.oSPT_ICmd.SequentialWRDMAExt(STARTING_LBA = startLBA, MAXIMUM_LBA = endLBA, STEP_LBA = BLKCNT, BLKS_PER_XFR = BLKCNT, COMPARE_FLAG = compare)

      elif mode == 0x21:
         #Random Write (mode = 0x21)
         self.oSPT_ICmd.RandomWriteDMAExt(STARTING_LBA = startLBA, MAXIMUM_LBA = endLBA, MIN_SECTOR_CNT = BLKCNT, MAX_SECTOR_CNT = BLKCNT, LOOP_CNT = cnt)

      elif mode == 0x11:
         #Random Read  (mode = 0x11)
         self.oSPT_ICmd.RandomReadDMAExt(STARTING_LBA = startLBA, MAXIMUM_LBA = endLBA, MIN_SECTOR_CNT = BLKCNT, MAX_SECTOR_CNT = BLKCNT, LOOP_CNT = cnt, COMPARE_FLAG = compare)

      elif mode == 0x01:
         #Random WriteRead (mode = 0x01)
         self.oSPT_ICmd.RandomWRDMAExt(STARTING_LBA = startLBA, MAXIMUM_LBA = endLBA, MIN_SECTOR_CNT = BLKCNT, MAX_SECTOR_CNT = BLKCNT, LOOP_CNT = cnt, COMPARE_FLAG = compare)
