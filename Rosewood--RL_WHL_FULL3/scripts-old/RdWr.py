#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Read Write Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/16 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/RdWr.py $
# $Revision: #7 $
# $DateTime: 2016/11/16 17:46:21 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/RdWr.py#7 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP, paramExtractor
from State import CState
from Exceptions import CDblogDataMissing
import MessageHandler as objMsg
from Drive import objDut
from Utility import CUtility
import types, os, sys
from Process import CProcess
from Process import CCudacom
import Channel
from FSO import CFSO,dataTableHelper
from Servo import CServoOpti
from Servo import CServo
from SdatParameters import *
from math import log10, pow
from time import time
import struct
import PBIC
from MediaScan import CUserFlaw
import ScrCmds
from array import array
from PowerControl import objPwrCtrl
import binascii
from base_GOTF import CGOTFGrading
from StateTable import StateTable
import MathLib
from SIM_FSO import objSimArea

verbose = 0 # Set to a value greater than 0 for output in the log

class CRdWr(CProcess,CCudacom):
   def __init__(self, params = {}):
      CProcess.__init__(self)
      self.testZones = None
      self.headRange = None
      self.dut = objDut
      self.params = params
      self.objprocess = CProcess()

   def St(self,inPrm):
      inPrm = dict(inPrm)

      if 'ZONE_POS' in self.params:
         inPrm['ZONE_POSITION'] = self.params['ZONE_POS']

      if self.testZones == None or inPrm['test_num'] in [250]: # T250 dont need additional handling as T251
         stats = self.objprocess.St(inPrm)
      else:

         # Create disable flash update mask
         mword = {}
         mword['CWORD1'] = inPrm['CWORD1']
         if type(mword['CWORD1']) == types.TupleType:
            mword['CWORD1'] = mword['CWORD1'][0]

         if inPrm['test_num'] in [151, 251]:
            #Disable flash update if this is a by-zone/head update
            mword['CWORD1'] = mword['CWORD1'] | 0x0008
            if testSwitch.REDUCE_LOG_SIZE:
               inPrm['RESULTS_RETURNED'] = 0 # disable bucket table printing for CM load reduction

         if not self.headRange == None:
            inPrm['TEST_HEAD'] = self.headRange

         if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
            MaskList = self.oUtility.convertListToZoneBankMasks(self.testZones)
            for bank,list in MaskList.iteritems():
               if list:
                  inPrm ['BIT_MASK_EXT'], inPrm ['BIT_MASK'] = self.oUtility.convertListTo64BitMask(list)
                  inPrm ['ZONE_MASK_BANK'] = bank
                  stats = self.objprocess.St(inPrm)

         else:
            inPrm['BIT_MASK_EXT'], inPrm['BIT_MASK'] = self.oUtility.convertListTo64BitMask(self.testZones)
            stats = self.objprocess.St(inPrm)

      return stats


   def modRAP(self, offset, value, mask):
      rapOffPrm = {
         'test_num': 178,
         'prm_name': "Modify RAP Word %s to %s using mask %s" % (str(offset), str(value), str(mask)),
         'CWORD1': 0x0220,
         'RAP_WORD':(offset, value, mask)
      }
      self.St(rapOffPrm)
      pass


   def measCQM(self, basePrm = {}):
      if basePrm == {}:
         basePrm={
            #Test 151 - read channel optimization.
            #Null Opti- BER/CQM measure
            'test_num':151,
            'prm_name':'CQM BER Measure PRM_151',
            'timeout':1000,
            'spc_id':1,
            'CWORD1': 0x4008,
            "TARGET_TRK_WRITES" : (0x01,),
            "NUM_SAMPLES" : (0x02,),               # 1 might be sufficient
            #               regID start end step
            "REG_TO_OPT1" : (0x0,0x0,0x0,0x00,),   # REGID_TDTARG    (0x91,12,12,0x01,),
            "RESULTS_RETURNED" : (0x0F),
            "NON_DIS_WEDGES" : (50,),
            #"RW_MODE" : (0x0,),                   # Force Sync - currently required for Agere
            # Force reset of channel back to defaults between each bucket point.
            # This is done by forcing a zero seek.  Prevents failure do to railed taps.
            "SEEK_COUNT" : (1,),                   # Just needs to be non-zero, only one seek is performed.
            "TRGT_PRE_READS" : (0x00,),   # Training Reads (par value in sectors now) - set to zero
            #"RETRY_LIMIT" : (5,),         # Retries to perform on read errors.
            "PATTERNS" : (0xAA,0xFF,0xFF,),
            # Optional:
            "LIMIT32" : (0,0,),                    # Display TAP and CQM debug data (1,0,),
            "ZONE_POSITION": TP.ZONE_POS,
          }
      SetFailSafe()
      self.St(basePrm)
      ClearFailSafe()


   def writetrack(self, retries = 0):
      """
      Write the current track
      @return: Drive Status
      """
      writeRetryCnt = 0
      while writeRetryCnt <= retries:
         buf, errorCode = self.Fn(1355)
         if errorCode == 0:
            break
         writeRetryCnt += 1
      else:
         objMsg.printMsg("Failed to write track, %s retries attempted."% retries)
         objMsg.printMsg("writetrack err, errorCode= %s, sense data = %s " % (errorCode,binascii.hexlify(buf)),objMsg.CMessLvl.IMPORTANT)
      return buf                    # Return buffer contents only.


   def ber(self, targetBer, numRevs, TLevel, timeout = 60, printResult = 0):
      """
      Run the BER test, seek to target track using ActiveHead and ActiveCylinder and measure raw BER.
      @param targetBer: Target BER limit (times 10) to measure. Number of revs are calculated internally to meet the target BER.
      @param numRevs: Number of revs to read in the BER test. Will override the targetBer if numRevs is non-zero.
      @param TLevel: ECC Level (0 to 30 by 2's -- See TLEVEL define below in setEccLevel).
      @return: Bit Error Rate, Data Errors, Sync Errors, Other Errors, Sectors Per Rev, Sense Code, and failed sector if other error.
      """
      if ((TLevel % 2) != 0) or (TLevel > 30):
         objMsg.printMsg("Invalid TLevel Entered!")
         return
         buf = ReceiveBuffer(timeout,checkSRQ=0)

      buf, errorCode = self.Fn(1342, targetBer, numRevs, TLevel)
      result = struct.unpack("fLLLHHLLL",buf)
      other_errors = result[3:4]
      if printResult == 1:
         objMsg.printMsg("BER = %f " % (result[0:1]) + "Data Errors = %u " % (result[1:2]) + "Sync Errors = %u " % (result[2:3]) + \
         "Other Errors = %u " % (result[3:4]) + "Sectors per Rev = %u " % (result[4:5]) + "Sense Data = %x " % (result[6:7]))
      if other_errors[0] > 0:
         objMsg.printMsg("Failed Sector = %u" % (result[7:8]))
      return buf


   def setEccLevel(self, level=30):
      """
      Set Override ECC Level and enable override.
      @param level: Override ECC level 0..30 (default=30)
         DISABLE_ECC  = 0,           // T Level 0
         TLEVEL_2     = 2,           // T Level 2
         TLEVEL_4     = 4,           // T Level 4
         TLEVEL_6     = 6,           // T Level 6
         TLEVEL_8     = 8,           // T Level 8
         TLEVEL_10    = 10,          // T Level 10
         TLEVEL_12    = 12,          // T Level 12
         TLEVEL_14    = 14,          // T Level 14
         TLEVEL_16    = 16,          // T Level 16
         TLEVEL_18    = 18,          // T Level 18
         TLEVEL_20    = 20,          // T Level 20
         TLEVEL_22    = 22,          // T Level 22
         TLEVEL_24    = 24,          // T Level 24
         TLEVEL_26    = 26,          // T Level 26
         TLEVEL_28    = 28,          // T Level 28
         TLEVEL_30    = 30           // T Level 30
      @return: nothing
      """

      if ((level % 2) != 0) or (level > 30):
         objMsg.printMsg("Invalid TLevel Entered!  ECC Level not changed!")
      else:
         buf, errorCode = self.Fn(1334, level)
      return


   def displayBuffer(self, buf):
      """
      Print a binary string buffer to the string in "pretty" format- bit seperated hex
      """
      try:
         data = binascii.hexlify(buf)
         i1=0
         cnt=0
         objMsg.printMsg("   ")
         for i2 in range(2,len(data),2):
            objMsg.printMsg(data[i1:i2])
            i1=i2
            cnt+=1
            if cnt == 8 or cnt == 16 or cnt == 24:
               objMsg.printMsg("  ")
            if cnt == 32:
               cnt=0
               objMsg.printMsg("\n   ")
         objMsg.printMsg(data[i1:])
      except:
         pass


   def fillbuff(self,pattern):
      """
      Load pattern buffer into drive's dummy cache.
      @param pattern: Pattern to write
      @return: Error code
      """
      buf, errorCode = self.Fn(1214)
      if len(buf) > 0:
         self.displayBuffer(buf[0])
      return buf                    # Return buffer contents only.


class CRdWrOpti(CRdWr):
   def __init__(self, params = {}):
      self.params = params
      CRdWr.__init__(self, self.params)
      self.oChannel = Channel.CChannelAccess()
      self.oFSO = CFSO()


   def vgarOpti(self, inPrm, openThresholds = 0, measureCQM = 0):
      if openThresholds == 0:
         self.__retries(inPrm,4)
      else:
         oUtil = CUtility()
         self.St(oUtil.overRidePrm(inPrm, {"VGA_MAX" : (0x200,),"VGA_MIN" : (0x00,)}))
      if testSwitch.VgaPcFileFlashUpdate == 1:
         self.St({'test_num':178,'prm_name':"Recover SAP from PCFILE",'CWORD1':0x0421, 'timeout' : 100})
         try:
            self.St(MDWUncalSpinup)
         except:
            self.St({'test_num':1,'prm_name':"VGA Update spin-up",'CWORD1':1, 'MAX_START_TIME':3000})
      if measureCQM == 1:                       # Perform followup CQM measurement (default)
         self.measCQM()


   def vgarOptiByHead(self, inPrm, openThresholds = 0, measureCQM = 0):
      oUtil = CUtility()
      for head in range(self.dut.imaxHead):
         try:
            self.vgarOpti(oUtil.overRidePrm(inPrm,{'TEST_HEAD': head}),openThresholds, measureCQM = 0)
         except:
            objMsg.printMsg("Failed opti on head: %s" % head, objMsg.CMessLvl.IMPORTANT)
      if measureCQM == 1:                       # Perform followup CQM measurement (default)
         self.measCQM()


   def modifyForceUpdate(self, inPrm, ForceUpdate = True):
      return inPrm


   def findNonUpdatedZones(self,tableData):
      badZoneList = {}
      for row in tableData:
         if int(row['SAVE_OPTI_VAL']) == 0:
            tempList = badZoneList.get(int(row['HD_LGC_PSN']),[])
            tempList.append(int(row['DATA_ZONE']))
            badZoneList[int(row['HD_LGC_PSN'])] = tempList

      return badZoneList


   def extractListIndex(self,inList,index):
      return [i[index] for i in inList]


   def firRetry(self,head,zone,inPrm, maxRetries, tdtarginPrm):
      self.headRange = [head]
      self.testZones = zone
      oServo = CServo()
      maxRetries = maxRetries * len(zone)
      firRetryNum = 0
      while firRetryNum < maxRetries:

         #Perform zone reload seeks to reload the channel defaults
         # And since it will be faster to just perform a multi zone seek
         #objMsg.printMsg("Performing channel reload seeks.",objMsg.CMessLvl.VERBOSEDEBUG)
         #10% seek
         #oServo.rsk(int(self.dut.maxTrack[head]*0.10),head)
         #90% seek
         #oServo.rsk(int(self.dut.maxTrack[head]*0.90),head)

         #Initialize the results container
         try:
            firData = self.dut.dblData.Tables('P141_CQM').tableDataObj()

            startIndex = len(firData)
         except:
            startIndex = 0
         if testSwitch.virtualRun:
            startIndex = 0

         #Re-run TDTarg to reset channel for FIR adapt
         self.St(tdtarginPrm)

         #Run the Test
         inPrm = self.modifyForceUpdate(inPrm,False)
         self.St(inPrm)
         firData = self.dut.dblData.Tables('P141_CQM').tableDataObj()


         #Analyze the results
         tempBadZones = self.findNonUpdatedZones(firData[startIndex:])
         if len(tempBadZones.items()) == 0:
            #All zones opti'd
            break
         else:
            self.headRange = [head]
            #Increment the retry counter to reflect a zone being opti'd as we overallocated retries
            firRetryNum += len(self.testZones) - len(tempBadZones[head])

            self.testZones = tempBadZones[head]
            objMsg.printMsg("FIR not optimized in zones %s" % str(tempBadZones))
            #Increment retry counter for remaining opti zones
            firRetryNum += 1
      else:
         #Exahsted all retries
         self.St(tdtarginPrm)
         inPrm = self.modifyForceUpdate(inPrm,True)
         self.St(inPrm)


   def tapOpti(self, inPrm, maxRetries = 3, tdtarginPrm = None, measureCQM = 0):
      """
      Optimize TAP values
      AGERE FIR tap retries algorithm
         disable force update flag
         retryNum = 0
         for retryNum in maxRetries
            run fir opti
            if not SAVE_OPTI_VAL 1 for all zones
               modify zone mask for not-updated zones
               retryNum += 1
         Run TDTARG Opti
         Enable force update flag
         run fir opti
      """
      if not tdtarginPrm == None:
         backupPrm = CUtility().copy(inPrm)
         saveTestZones =  CUtility().copy(self.testZones)
         saveHeadRange =  CUtility().copy(self.headRange)

         #Initialize the results container
         try:
            firData = self.dut.dblData.Tables('P141_CQM').tableDataObj()

            startIndex = len(firData)
         except:
            startIndex = 0
         if testSwitch.virtualRun:
            startIndex = 0

         #Run the Test
         inPrm = self.modifyForceUpdate(inPrm,False)
         self.St(inPrm)
         firData = self.dut.dblData.Tables('P141_CQM').tableDataObj()


         #Analyze the results
         tempBadZones = self.findNonUpdatedZones(firData[startIndex:])
         del firData

         if not len(tempBadZones) == 0:
            objMsg.printMsg("FIR not optimized in zones %s" % str(tempBadZones))
            for head,badZones in tempBadZones.items():
               self.firRetry(head,badZones,inPrm,maxRetries,tdtarginPrm)

         #Reset the test zones for the full opti to use
         self.testZones = CUtility().copy(saveTestZones)
         self.headRange = CUtility().copy(saveHeadRange)
         #Clean up our temporary variables
         del tempBadZones, startIndex, saveTestZones, saveHeadRange
         inPrm = backupPrm
      else:
         self.St(inPrm)

      if measureCQM == 1:                       # Perform followup CQM measurement (default)
         self.measCQM()


   def concatenateTableObjects(self, master = {}, newData = {}):
      for key in newData:
         master.setdefault(key, []).extend(newData[key])
      return master


   def phastOptiRetry(self,head,zone,inPrm, maxRetries, zapFunc = None, zapECList = [10007], logReduction = False):
      self.headRange = [head]
      self.testZones = zone
      oServo = CServo()
      maxRetries = maxRetries * len(zone)
      if testSwitch.FE_0133029_231166_RAISE_MISS_DATA_EXC_PHAST_OPTI:
         #add 1 retry for the modify force update
         maxRetries += 1

      phastRetryNum = 0
      zappedTracks = False
      phastData = 0

      retdata = {}

      while phastRetryNum < maxRetries:

         #Initialize the results container
         if not logReduction or testSwitch.virtualRun:
            try:
               phastData = self.dut.dblData.Tables('P251_STATUS').tableDataObj()

               startIndex = len(phastData)
            except:
               startIndex = 0
         else:
            startIndex = 0

         if testSwitch.virtualRun:
            startIndex = 0

         #Run the Test
         if (phastRetryNum == maxRetries-1) and testSwitch.FE_0133029_231166_RAISE_MISS_DATA_EXC_PHAST_OPTI:
            #last retry so force the use test track to attempt to opti
            inPrm = self.modifyForceUpdate(inPrm,True)
         else:
            inPrm = self.modifyForceUpdate(inPrm,False)

         if testSwitch.FE_0133029_231166_RAISE_MISS_DATA_EXC_PHAST_OPTI:
            failData = None
            try:
               result = self.St(inPrm)
               failureCode = result[2]
            except ScriptTestFailure, (failData):
               failureCode = failData[0][2]
               pass #for now


            #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG
            try:
               if logReduction and not testSwitch.virtualRun:
                  phastData = self.dut.objSeq.SuprsDblObject['P251_STATUS']
                  retdata = self.concatenateTableObjects(retdata,self.dut.objSeq.SuprsDblObject)
               else:
                  phastData = self.dut.dblData.Tables('P251_STATUS').tableDataObj()
            except (KeyError, CDblogDataMissing):
               #if test didn't output any data
               if failData == None:
                  raise
               else:
                  raise ScriptTestFailure, failData

         else:
            SetFailSafe()
            result = self.St(inPrm)
            ClearFailSafe()

            failureCode = result[2]

            if logReduction and not testSwitch.virtualRun:
               phastData = self.dut.objSeq.SuprsDblObject['P251_STATUS']
               retdata = self.concatenateTableObjects(retdata,self.dut.objSeq.SuprsDblObject)
            else:
               phastData = self.dut.dblData.Tables('P251_STATUS').tableDataObj()

         #Analyze the results
         tempBadZones = self.findNonUpdatedZones(phastData[startIndex:])

         phastData = None
         if logReduction and not testSwitch.virtualRun:
            del self.dut.objSeq.SuprsDblObject['P251_STATUS']


         if len(tempBadZones.items()) == 0:
            #All zones opti'd
            break
         else:
            if (phastRetryNum == maxRetries-1) and testSwitch.FE_0133029_231166_RAISE_MISS_DATA_EXC_PHAST_OPTI:
               # Zones still failed on last retry
               objMsg.printMsg("REG not optimized in zones111 %s" % str(tempBadZones))
               if failData == None:
                  if testSwitch.virtualRun:
                     objMsg.printMsg("All opti retries exhausted and not all zones opti'd- Error ignored in VE: Check P251_STATUS in virtual.xml")
                     break
                  else:
                     ScrCmds.raiseException(10452, "All opti retries exhausted and not all zones opti'd")
               else:
                  raise ScriptTestFailure, failData

            if failureCode in zapECList and not zapFunc == None and not zappedTracks:
               if testSwitch.WA_SGP_SAVE_RAPNSAP_B4_OPTIZAP_RETRY:
                  oFSO = CFSO()
                  oFSO.saveRAPSAPtoFLASH()
               #Extract the failed heads for use in ZAP command
               zapFunc(self.testZones,tempBadZones.keys())
               zappedTracks = True

            self.headRange = [head]
            #Increment the retry counter to reflect a zone being opti'd as we overallocated retries
            phastRetryNum += len(self.testZones) - len(tempBadZones[head])

            self.testZones = tempBadZones[head]
            objMsg.printMsg("REG not optimized in zones222 %s" % str(tempBadZones))
            #Increment retry counter for remaining opti zones
            phastRetryNum += 1
      else:
         if testSwitch.FE_0133029_231166_RAISE_MISS_DATA_EXC_PHAST_OPTI:
            # We shouldn't get here if FE_0133029_231166_RAISE_MISS_DATA_EXC_PHAST_OPTI is enabled
            ScrCmds.raiseException(11044, "Not all zones optimized due to script logic error.")
         else:
            #Exahsted all retries
            inPrm = self.modifyForceUpdate(inPrm,True)
            self.St(inPrm)

      del phastData

      return retdata


   def phastOpti(self,inPrm,maxRetries = 3,measureCQM = 0, zapFunc = None, zapECList = [10007], logReduction = False, dataCollectionTables = []):
      backupPrm = CUtility().copy(inPrm)
      saveTestZones =  CUtility().copy(self.testZones)
      saveHeadRange =  CUtility().copy(self.headRange)
      retdata = {}
      try:
         #Initialize the results container
         if not logReduction or testSwitch.virtualRun:
            try:
               phastData = self.dut.dblData.Tables('P251_STATUS').tableDataObj()
               startIndex = len(phastData)
            except:
               startIndex = 0
         else:
            inPrm['stSuppressResults'] = ST_SUPPRESS__ALL | ST_SUPPRESS_RECOVER_LOG_ON_FAILURE
            inPrm['DblTablesToParse'] = ['P251_STATUS',] + dataCollectionTables
            startIndex = 0

         if "RESULTS_RETURNED" in self.params:
            inPrm['RESULTS_RETURNED'] = self.params["RESULTS_RETURNED"]

         if testSwitch.virtualRun:
            startIndex = 0

         if testSwitch.FE_0113290_231166_NPT_TARGETS_FROM_PARAM_FOR_T251:
            import nptFile
            if verbose:               
               objMsg.printMsg("Channel type is %s" % self.dut.channelType)
            nptObj = nptFile.nptObject()
            if (self.dut.channelType.find('SRC_COLUMBIA_M') > -1):  # if using Marvell channel
                for target in TP.NPT_Targets_Marvell:
                   # C0,  C1,  C2,   SMPAT,    O0,    O1,    O2,    O3,    O4,    O5,    O6,    O7,    O8,   THR
                   nptObj.addMarvellTarget(target[0], target[1], target[2], target[3], target[4], target[5], target[6], target[7], target[8], target[9], target[10], target[11], target[12], target[13])
            else:                                            # must be LSI
                for target in TP.NPT_Targets_156:
                   if testSwitch.FE_SGP_81592_SUPPORT_FOR_NPT_TGT_LIST_WITH_5_INPUTS:
                      nptObj.addIterativeTarget_New(target[0], target[1], target[2], target[3], target[4])
                   else:
                      if (self.dut.channelType.find('SRC_11K_M') > -1):
                         #objMsg.printMsg("11K target[0]  %s" % target[0])
                         #objMsg.printMsg("11K target[1]  %s" % target[1])
                         #objMsg.printMsg("11K target[2]  %s" % target[2])
                         #objMsg.printMsg("11K target[3]  %s" % target[3])
                         #objMsg.printMsg("11K target[4]  %s" % target[4])
                         nptObj.addIterativeTarget11K(target[0], target[1], target[2], target[3], target[4])
                      else:
                         #npt0, npt1, npt2, sync mark pattern
                         nptObj.addIterativeTarget(target[0], target[1], target[2], target[4])
            nptFile.fobj = nptObj.fobj
            fdata = nptObj.getValue()
            if verbose:
               if (self.dut.channelType.find('SRC_11K_M') > -1):
                  objMsg.printMsg("fdata %s" % fdata)
            nptFile.fileSize = len(fdata)
            RegisterResultsCallback(nptFile.processRequest21, 21, 0) # Re-direct 81 calls


         #Run the Test
         inPrm = self.modifyForceUpdate(inPrm,False)

         #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG
         if testSwitch.FE_0133029_231166_RAISE_MISS_DATA_EXC_PHAST_OPTI:
            failData = None
            try:
               result = self.St(inPrm)
               failureCode = result[2]
            except ScriptTestFailure, (failData):
               failureCode = failData[0][2]
               pass #for now


            #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG
            try:
               if logReduction and not testSwitch.virtualRun:
                  phastData = self.dut.objSeq.SuprsDblObject['P251_STATUS']
                  retdata = self.concatenateTableObjects(retdata,self.dut.objSeq.SuprsDblObject)
               else:
                  phastData = self.dut.dblData.Tables('P251_STATUS').tableDataObj()
            except (KeyError, CDblogDataMissing):
               #if test didn't output any data
               if failData == None:
                  raise
               else:
                  raise ScriptTestFailure, failData

         else:
            SetFailSafe()

            result = self.St(inPrm)

            ClearFailSafe()

            failureCode = result[2]
            #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG
            if logReduction and not testSwitch.virtualRun:
               phastData = self.dut.objSeq.SuprsDblObject['P251_STATUS']
               retdata = self.concatenateTableObjects(retdata,self.dut.objSeq.SuprsDblObject)
            else:
               phastData = self.dut.dblData.Tables('P251_STATUS').tableDataObj()

         #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG
         #Analyze the results
         tempBadZones = self.findNonUpdatedZones(phastData[startIndex:])
         del phastData
         if logReduction and not testSwitch.virtualRun:
            del self.dut.objSeq.SuprsDblObject['P251_STATUS']

         if not len(tempBadZones) == 0:

            if failureCode in zapECList and not zapFunc == None:
               if testSwitch.WA_SGP_SAVE_RAPNSAP_B4_OPTIZAP_RETRY:
                  oFSO = CFSO()
                  oFSO.saveRAPSAPtoFLASH()
               #Extract the failed heads for use in ZAP command
               zapFunc(saveTestZones,tempBadZones.keys())

            objMsg.printMsg("REG not optimized in zones333 %s" % str(tempBadZones))
            for head,badZones in tempBadZones.items():
               iret = self.phastOptiRetry(head,badZones,inPrm,maxRetries,zapFunc, zapECList)
               retdata = self.concatenateTableObjects(retdata,iret)
      finally:
         #Reset the test zones for the full opti to use
         self.testZones = CUtility().copy(saveTestZones)
         self.headRange = CUtility().copy(saveHeadRange)
         inPrm = backupPrm
         RegisterResultsCallback('', 21,) # Resume normal 21 calls

      #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG
      #Clean up our temporary variables
      del tempBadZones, startIndex, saveTestZones, saveHeadRange

      if measureCQM == 1:                       # Perform followup CQM measurement (default)
         self.measCQM()

      if not logReduction or testSwitch.virtualRun:
         #Delete file pointers
         self.dut.dblData.Tables('P251_STATUS').deleteIndexRecords(1)

         #Delete RAM objects
         self.dut.dblData.delTable('P251_STATUS')

      #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG
      return retdata


   def Writer_Reader_Gap_Calib(self, inPrm, measureCQM = 0, zapFromDut = 1):
      """
      Run test 176 - Writer to Reader Gap Calibration

      Further Documentation
      =====================
         U{Latest SF3 Test 176 Documentation <http://col-cert-01.am.ad.seagate.com/platform/Self Test Docs/docs/latest/Descriptions/test176.html>}

      Input Parameters
      ================
         @param inPrm: Test inputs are defined in the documentation listed above.
         @param measureCQM: Measure pre-post cqm for reference
         @param zapFromDut: Enable/Disable servo cal data from host file (prevents gap calibration read/writes)

      """
      execPrm = self.oUtility.copy(inPrm)

      if zapFromDut:
         try:
            CServoOpti().retrieveRWGapData(zapFromDut)
            gapOnDisc = True
         except:
            gapOnDisc = False
            if testSwitch.FE_0155812_007955_P_T176_DONT_RECAL_IF_POLYZAP_SAVED_TO_SAP:
               try:
                  if CServoOpti().polyZapEnabled():
                     if CServoOpti().polyZapResultsInSAP():
                        gapOnDisc = True
               except:
                  gapOnDisc = False

      else:
         gapOnDisc = False

      if type(execPrm.get('CWORD2',0x0000)) in [types.ListType,types.TupleType]:
         execPrm['CWORD2'] = execPrm['CWORD2'][0]

      if gapOnDisc:
         #Retrieve the gap-cal data from host
         execPrm['CWORD2'] = execPrm.get('CWORD2',0) | 0x0008
      else:
         #Save gap cal data to host
         execPrm['CWORD2'] = execPrm.get('CWORD2',0) | 0x0010

      if testSwitch.T176_AUTOFREQ == 1:
         buf, errorCode = self.Fn(1308, 0x06)
         if errorCode == 0:
            try:
               servoSynth = struct.unpack('>H',buf)[0]
            except:
               ScrCmds.raiseException(errorCode, "Failure during RW Gap call to cudacom 1308 read Cannel Reg06")
            objMsg.printMsg("servoSynth = 0x%x" % servoSynth)
            MDiv = servoSynth & 0xFF
            FDiv = (servoSynth >> 8) & 0x3F

            FreqUpdate = int(round(30 * (1 + MDiv + pow(2,-6) * FDiv) / 4, 0))
            objMsg.printMsg("Servo Freq = %s" % (FreqUpdate))
            execPrm['FREQUENCY'] = FreqUpdate
         else:
            ScrCmds.raiseException(errorCode, "Failure during RW Gap call to cudacom 1308 read Cannel Reg06")

      self.St(execPrm)

      if measureCQM == 1:                       # Perform followup CQM measurement (default)
         self.measCQM()

   def NPML(self, inPrm, measureCQM = 0):
      self.St(inPrm)
      if measureCQM == 1:                       # Perform followup CQM measurement (default)
         self.measCQM()

   def MRNL(self, inPrm, measureCQM = 0):
      self.St(inPrm)
      if measureCQM == 1:                       # Perform followup CQM measurement (default)
         self.measCQM()

   def preCompOpti(self, inPrm, channelReferenceForOffset = 'NOMF', measureCQM = 0):
      """
      Optimize write precompensation.
      Further Documentation
      =====================
         U{Test 151 Documentation <http://col-cert-01.am.ad.seagate.com/platform/Self Test Docs/docs/latest/Descriptions/test151.html>}

      Further Documentation
      =====================
         @param inPrm: MCT Test input
         @param channelReferenceForOffset: Set to '' for
            standard parameter passthrough. Or set to Channelregister name identified in channelRegs.py
            to use base offset calculated as OptiReg - BaseOffsetVal
      """
      if not channelReferenceForOffset == '':
         #Sample: "REG_TO_OPT1" : (regID,min,max,increment,)
         tmpPrm = {}
         tmpPrm = self.oUtility.copy(inPrm)
         baseOff = self.oChannel.rdChVal(channelReferenceForOffset, 15)
         objMsg.printMsg('%s: %s' % (channelReferenceForOffset,str(baseOff)), objMsg.CMessLvl.DEBUG)
         modReg = []
         modReg = [item for item in tmpPrm['REG_TO_OPT1']]
         modReg[1] = modReg[1] + baseOff
         modReg[2] = modReg[2] + baseOff
         tmpPrm.update({'REG_TO_OPT1': modReg})
      self.__retries(tmpPrm,3)
      if measureCQM == 1:                       # Perform followup CQM measurement (default)
         self.measCQM()

   def tdtargOpti(self, inPrm, measureCQM = 0):
      self.__retries(inPrm,3)
      if measureCQM == 1:                       # Perform followup CQM measurement (default)
         self.measCQM()

   def zfrOpti(self, inPrm, measureCQM = 0):
      self.__retries(inPrm,3)
      if measureCQM == 1:                       # Perform followup CQM measurement (default)
         self.measCQM()

   def findTargetSqueeze(self, inPrm, head = 0, errorRateRange = (-4.5,-6.5)):
      """
      Function will return the squeeze required to get a target squeezed error rate.
         Target is middle squeeze between limits.
      @param errorRateRange: Tuple of (minER, maxER) range
      """
      tempPrm = dict(inPrm)
      tempPrm['HEAD_RANGE'] = (head<<8) + head

      self.dut.dblParser.dblTableMaster.append('P167_ERR_SQUEEZE')
      self.St(tempPrm)
      squeezeData = self.dut.dblData.Tables('P167_ERR_SQUEEZE').tableDataObj()

      self.dut.dblData.Tables('P167_ERR_SQUEEZE').deleteIndexRecords(True)
      self.dut.dblData.delTable('P167_ERR_SQUEEZE')

      maxBERSqueeze = None
      minBERSqueeze = None

      for index, record in enumerate(squeezeData):
         #Top down search
         er = float(record['LOG10_ERR_RATE'])
         if er >= errorRateRange[1] and maxBERSqueeze == None and index > 0:
            maxBERSqueeze = int(squeezeData[index-1]['SQZ_AMT_SVO_CNT'])

         if er >= errorRateRange[0] and minBERSqueeze == None and index > 0:
            minBERSqueeze = int(squeezeData[index]['SQZ_AMT_SVO_CNT'])

      if None in [maxBERSqueeze,minBERSqueeze]:
         objMsg.printMsg("Failed to find ber range with squeeze. Settting squeeze to 0.")
         return 0
      else:
         return int(abs(maxBERSqueeze - minBERSqueeze)/2) + maxBERSqueeze
   def __retries(self, inPrm, maxRetries = 3):
      failed = 1
      retry = 0
      while failed == 1 and retry < maxRetries:
         try:
            self.St(inPrm)
            failed = 0
         except ScriptTestFailure, (failureData):
            ec = failureData[0][2]
            if ec in [11087, 11049, 11231]:
               raise
            retry +=1

   def ctffrOpti(self, inPrm, measureCQM = 0):#,lowRange, hiRange):
      #for head in range(objDut.imaxHead):
      #   maxZones = range(0,15,1)
      #   for zone in maxZones:
      #      #seek to zone
      #      fref = self.oChannel.getMask(self.oChannel.chRegs['FREF'])
      #      n1 = self.oChannel.getMask(self.oChannel.chRegs['N1'])
      #      m1 = self.oChannel.getMask(self.oChannel.chRegs['M1'])
      #      f1 = self.oChannel.getMask(self.oChannel.chRegs['F1'])
      #      znFreq = (fref/4) * (n1+1 + f1/8) / (n1+1)
      #      low = lowRange*znFreq
      #      hi = hiRange*znFreq
      #      reg = inPrm['REG_TO_OPT1']
      #      #example mask "REG_TO_OPT1" : (0x92,0x05,0x1A,0x01,)
      #
      #      reg[1] = self.decimalMask(low)
      #      reg[2] = self.decimalMask(hi)
      #
      #      inPrm.update({'TEST_HEAD':head,
      #                    'BIT_MASK':2**zone})
      #      inPrm.update(reg)
      self.__retries(inPrm,3)
      if measureCQM == 1:                       # Perform followup CQM measurement (default)
         self.measCQM()

   def decimalMask(self, value, decFieldWidth = 3):
      out = int(divmod(value,1)[0])<<decFieldWidth
      if value%1 > 0:
         out = out + int(1/divmod((value%1),1)[0])
      return out



class CRdWrScreen(CRdWr):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self):
      CRdWr.__init__(self)
      self.oFSO = CFSO()
      self.oSrvOpti = CServoOpti()
      self.objProc = CProcess()
      self.oUtility = CUtility()
      self.oServo = CServo()
      self.objFs = CUserFlaw()
      self.dth = dataTableHelper()
      #self.oGOTF = CGOTFGrading()
      self.oChannelAccess=Channel.CChannelAccess()
      if self.dut.nextOper == "FNC2":
         zapFromDut = self.params.get('zapFromDut',1)
      else:
         zapFromDut = self.params.get('zapFromDut',0)
         
      if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
         from Opti_Read import CRdOpti
      else:
         from base_SerialTest import CRdOpti         
      oOptiCls = CRdOpti(self.dut, params = {'zapFromDut':zapFromDut})
   
   #-------------------------------------------------------------------------------------------------------
   def mrBiasHeadInstability(self, inPrm):
      """
      Find unstable heads using MRBias sweeps

      Further Documentation
      =====================
         U{Latest SF3 Test 195 Documentation <http://col-cert-01.am.ad.seagate.com/platform/Self Test Docs/docs/latest/Descriptions/test195.html>}
      Input Parameters
      ================
         @param inPrm: MCT test input dictionary
      """
      self.St(inPrm)

   if not testSwitch.FE_0121254_357260_SKIP_T163_IN_READ_SCRN:
      def servoErrorHeadInstabilityByZone(self, inPrm):
         """
         Find unstable heads using error counters in servo for
            -Timing Mark Detection
            -Incorrect Track ID
            -Write Unsafe

         Further Documentation
         =====================
            U{Latest SF3 Test 163 Documentation <http://col-cert-01.am.ad.seagate.com/platform/Self Test Docs/docs/latest/Descriptions/test163.html>}
         Input Parameters
         ================
            @param inPrm: Input dictionary of the form 'base':MCT test input dictionary,'TestZones'=[list of test zones]
         """
         #=== Init variables
         TrkRange = inPrm.get('TrkRange', 1000)
         testZones = inPrm.get('TestZones',[0,2])
         testHeads = xrange(self.dut.imaxHead)
         #=== Get zone table
         self.oFSO.getZoneTable()
         zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()

         #=== Loop thru heads and zones
         for head in testHeads:
            hdMsk = (head << 8) + head
            inPrm['base']['HEAD_RANGE'] = (hdMsk,) # Set head range
            ZthdOff = (self.dut.numZones) * head   # for zone tbl indexing
            for zone in testZones:
               #=== Get zone info
               Index = self.dth.getFirstRowIndexFromTable_byZone(zt, head, zone)
               startcyl = int(zt[Index]['ZN_START_CYL'])
               numcyl = int(zt[Index]['NUM_CYL'])               
               while Index+1< len(zt) and int(zt[Index]['ZN']) == int(zt[Index+1]['ZN']):
                  numcyl += int(zt[Index+1]['NUM_CYL']) 
                  Index += 1
               endcyl = startcyl + numcyl - 1
               #=== Start cyl is x tracks from ID
               if numcyl > TrkRange:
                  startcyl = endcyl - TrkRange
               #=== Execute test
               inPrm['base']['START_CYL'] = self.oUtility.ReturnTestCylWord(startcyl)
               inPrm['base']['END_CYL'] = self.oUtility.ReturnTestCylWord(endcyl)
               self.St(inPrm['base'])

      def servoErrorHeadInstability(self, inPrm):
         """
         Find unstable heads using error counters in servo for
            -Timing Mark Detection
            -Incorrect Track ID
            -Write Unsafe

         Further Documentation
         =====================
            U{Latest SF3 Test 163 Documentation <http://col-cert-01.am.ad.seagate.com/platform/Self Test Docs/docs/latest/Descriptions/test163.html>}
         Input Parameters
         ================
            @param inPrm: Input dictionary of the form 'base':MCT test input dictionary,'TestCyls'=[list of iterable's containing start and end cyls]
         """
         for cyl in inPrm['TestCyls']:
            if type(cyl[0]) == types.TupleType:
               inPrm['base']['START_CYL'] = cyl[0]
            else:
               inPrm['base']['START_CYL'] = self.oUtility.ReturnTestCylWord(cyl[0])

            if type(cyl[1]) == types.TupleType:
               inPrm['base']['END_CYL'] = cyl[1]
            else:
               inPrm['base']['END_CYL'] = self.oUtility.ReturnTestCylWord(cyl[1])

            self.St(inPrm['base'])
   
   #-------------------------------------------------------------------------------------------------------
   def otcMargin(self,inPrm):
      """
      Find the BER margin to offtrack events using servo offset squeeze implemented in test 167.

      Further Documentation
      =====================
         U{Latest SF3 Test 167 Documentation <http://col-cert-01.am.ad.seagate.com/platform/Self Test Docs/docs/latest/Descriptions/test167.html>}
      Input Parameters
      ================
         @param inPrm: Input dictionary of the form 'base':MCT test input dictionary,'TestCyls'=[list of iterable's containing start and end cyls]
      """

      #for cyl in inPrm['TestCyls']:
      #   if type(cyl) == types.TupleType:
      #      inPrm['base']['TEST_CYL'] = cyl
      #   else:
      #      inPrm['base']['TEST_CYL'] = self.oUtility.ReturnTestCylWord(cyl)
      #   self.St(inPrm['base'])
      self.St(inPrm)

   #-------------------------------------------------------------------------------------------------------
   def encroachmentMeasurement(self,inPrm):
      """
      Measure encroached ber using inPrm['base'] in each inPrm['ZONES'] for each inPrm['BAND_WRITES']
      """
      encroachParam = inPrm['base'].copy()
      if testSwitch.FE_0111521_399481_ARBITRARY_NUM_ZONES_IN_ENCROACH_MEASURE:
         inPrm['ZONES'] = [0, self.dut.numZones/2, self.dut.numZones-1]
      if testSwitch.auditTest:
         prm_auditTest_T50={'prm_name'    : "prm_auditTest_T50",
                           'BAND_SIZE' : 5,
                           'ZONE_POSITION': 180, # bias towards ID to make room for retries
                           'RETRY_COUNTER_MAX': 4,
                           'RETRY_INCR':10,
                           'timeout':900,}
         prm_auditTest_T50.update(getattr(TP, 'prm_auditTest_T50',{})) #make changes by program in testparameters.py
         encroachParam.update( prm_auditTest_T50)
      for head in xrange(self.dut.imaxHead):
         zoneCntr = 0
         for zone in inPrm['ZONES']:
            for bandWrites in inPrm['BAND_WRITES']:
               if testSwitch.FE_0119988_357260_MULTIPLE_T50_ZONE_POSITIONS:
                  zoneFailures = 0
                  allowedZoneFailures = getattr(TP, 't50AllowedZoneFailures', 1)
                  for position in inPrm['ZONE_POSITION']:
                     encroachParam['ZONE'] = zone
                     if testSwitch.FE_0133918_357260_USE_RETRY_PARMS_FOR_T50:
                        encroachParam['retryParms'] = inPrm['zoneRetryParms'][zoneCntr]  # zoneRetryParms should be a list of dictionaries containing retry parameter updates.  retryECList, retryCount and retryMode must also be specified in test parameters for this to work properly
                     encroachParam['TEST_HEAD'] = head
                     encroachParam['ZONE_POSITION'] = position
                     encroachParam['BAND_WRITES'] = bandWrites
                     if testSwitch.auditTest == 0 and not testSwitch.FE_0131646_357915_ALLOW_FAILURE_WHEN_RUNNING_MULTIPLE_T50_ZONE_POS:
                        self.St( encroachParam)
                     elif testSwitch.auditTest == 1 or testSwitch.FE_0131646_357915_ALLOW_FAILURE_WHEN_RUNNING_MULTIPLE_T50_ZONE_POS:
                        try:
                           self.St( encroachParam)
                        except ScriptTestFailure, (failureData):
                           ec = failureData[0][2]
                           if ec == 10482:
                              if testSwitch.auditTest == 1:
                                 objMsg.printMsg("AUDIT TEST:'No defect Free Band Found'...retry without flaw list check 1X",objMsg.CMessLvl.IMPORTANT)
                                 encroachParam['CWORD1'] = encroachParam['CWORD1'] | 0x04 # bit 2
                                 self.St(encroachParam)
                              elif testSwitch.FE_0131646_357915_ALLOW_FAILURE_WHEN_RUNNING_MULTIPLE_T50_ZONE_POS:
                                 zoneFailures += 1
                                 objMsg.printMsg("'No defect Free Band Found': head %s, zone %s, position %s.  Failures this zone: %s" % (head, zone, position, zoneFailures))
                                 if zoneFailures > allowedZoneFailures:
                                    raise
                           else:
                              raise
               else:
                  encroachParam['ZONE'] = zone
                  encroachParam['TEST_HEAD'] = head
                  encroachParam['BAND_WRITES'] = bandWrites
                  encroachParam['spc_id'] = inPrm.get('spc_id',1)
                  if testSwitch.auditTest ==0:
                     if testSwitch.FE_0138325_336764_P_DISABLE_FLAW_TABLE_CHK_AFTER_RETRY_T50_T51:
                        try:
                           self.St(encroachParam)
                        except ScriptTestFailure, (failureData):
                           ec = failureData[0][2]
                           if ec == 10468:
                              objMsg.printMsg("WRITE_SCRN retest:'No defect Free Band Found'...retry without flaw list check 1X",objMsg.CMessLvl.IMPORTANT)
                              encroachParam_bit2 = encroachParam.copy()
                              if type(encroachParam_bit2['CWORD1']) in [types.ListType,types.TupleType]:
                                 encroachParam_bit2['CWORD1'] = encroachParam_bit2['CWORD1'][0]
                              encroachParam_bit2['CWORD1'] |= 0x04 # bit 2
                              self.St(encroachParam_bit2)
                           else:
                              raise
                     else:
                        self.St(encroachParam)
                  elif testSwitch.auditTest==1:
                     try:
                        self.St( encroachParam)
                     except ScriptTestFailure, (failureData):
                        ec = failureData[0][2]
                        if ec == 10482:
                           objMsg.printMsg("AUDIT TEST:'No defect Free Band Found'...retry without flaw list check 1X",objMsg.CMessLvl.IMPORTANT)
                           encroachParam['CWORD1'] = encroachParam['CWORD1'] | 0x04 # bit 2
                           self.St( encroachParam)
                        else:
                           raise
                  if testSwitch.FE_0137948_336764_RETEST_T50_WITH_ZONE_POSITION_141 == 1:
                     try:
                        P050_tbl = self.dut.dblData.Tables('P050_ENCROACH_BER').tableDataObj()
                        if max([int(i['HARD_ERR_CNT']) for i in P050_tbl if (int(i['HD_PHYS_PSN']) == head and int(i['DATA_ZONE']) == zone)]):
                           objMsg.printMsg("Fail HARD_ERR_CNT detect at hd%s zone %s , retest with ZONE POSITION 141 "%(str(head),str(zone)))
                           encroachParam['ZONE_POSITION'] = 141
                           encroachParam['spc_id'] = 2
                           self.St( encroachParam)

                     except:
                        objMsg.printMsg("Unable to retrieve P050_ENCROACH_BER table data or P050_ENCROACH_BER table not found")
            zoneCntr += 1

      #=== Get table P050_ENCROACH_BER
      noExcept = True
      try:
         table = self.dut.dblData.Tables('P050_ENCROACH_BER').tableDataObj()
      except:
         objMsg.printMsg("Unable to retrieve P050_ENCROACH_BER table data")
         noExcept = False
      
      #data collection mode only
      if testSwitch.DB_0275227_480505_WRITE_SCRN_MONITORING_ONLY:
         noExcept = False

      #=== Check Failing criteria
      if noExcept:
         if inPrm.has_key('RRAW_CRITERIA'):
            #=== Form RRAW and OTF tables
            rrawTable = {}
            otfTable = {}
            self.formAtiTable(table, rrawTable, 'RRAW_BER', offset=3.61, testType = 'encroach')
            self.formAtiTable(table, otfTable, 'OTF_BER', offset=0.0, testType = 'encroach')
            objMsg.printMsg("T050 - RRAW TABLE - %s" %str(rrawTable))
            objMsg.printMsg("T050 - OTF TABLE - %s" %str(otfTable))
            #=== Check criteria
            self.checkAtiCriteria('RRAW', inPrm['RRAW_CRITERIA'], rrawTable, testType = 'encroach', testNo = 50)
            self.checkAtiCriteria('OTF', inPrm['OTF_CRITERIA'], otfTable, testType = 'encroach', testNo = 50)
   
   #-------------------------------------------------------------------------------------------------------
   def t51Diff(self, t51Table, spc_id):
      diffDict = {}
      for row in t51Table:
         colName = row["TRK_NUM"]
         if row['TEST_TYPE'] == 'baseline':
            suffix = 'BASELINE'
         else:
            suffix = 'ERASURE'
         newData = {
            'BITS_IN_ERROR_%s' % suffix      : row['BITS_IN_ERROR'],
            'BITS_IN_ERROR_BER_%s' % suffix  : row['BITS_IN_ERROR_BER'],
            'OTF_BER_%s' % suffix            : row['OTF_BER'],
            'NUM_WRT_%s' % suffix            : row['NUM_WRT'],
            'SCTR_READ_CNT_%s' % suffix         : row['SCTR_READ_CNT'],

            'DATA_ZONE'                      : row['DATA_ZONE'],
            'HD_LGC_PSN'                     : row['HD_LGC_PSN'],
            'HD_PHYS_PSN'                    : row['HD_PHYS_PSN'],

            'TRK_INDEX'                      : row['TRK_INDEX'],
            'TRK_NUM'                        : row['TRK_NUM'],
         }
         if colName in diffDict:
            diffDict[colName].update(newData)
         else:
            diffDict[colName] = newData

      for row in diffDict.values():
         row.update({
            'BITS_IN_ERROR_DELTA'      : round(float(row['BITS_IN_ERROR_ERASURE']) - float(row['BITS_IN_ERROR_BASELINE']), 2),
            'BITS_IN_ERROR_RATIO'      : round(
                                          ( float(row['BITS_IN_ERROR_ERASURE']) * float(row['SCTR_READ_CNT_BASELINE']) )
                                          / ( float(row['BITS_IN_ERROR_BASELINE']) * float(row['SCTR_READ_CNT_ERASURE']) ),
                                         4),
            'BITS_IN_ERROR_BER_DELTA'  : round(float(row['BITS_IN_ERROR_BER_BASELINE']) - float(row['BITS_IN_ERROR_BER_ERASURE']), 2),
            'OTF_BER_DELTA'            : round(float(row['OTF_BER_BASELINE']) - float(row['OTF_BER_ERASURE']), 2),
         })
      seq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

      for colName, row in sorted(diffDict.items()): # colName only used to facilitate sort
         self.dut.dblData.Tables('P051_ERASURE_BER_DELTAS').addRecord(
            {
            'SPC_ID'                      : spc_id,
            'OCCURRENCE'                  : occurrence,
            'SEQ'                         : seq,
            'TEST_SEQ_EVENT'              : testSeqEvent,
            'HD_LGC_PSN'                  : row['HD_LGC_PSN'],
            'HD_PHYS_PSN'                 : row['HD_PHYS_PSN'],
            'DATA_ZONE'                   : row['DATA_ZONE'],
            'TRK_INDEX'                   : row['TRK_INDEX'],
            'TRK_NUM'                     : row['TRK_NUM'],
            'NUM_WRT_BASELINE'            : row['NUM_WRT_BASELINE'],
            'NUM_WRT_ERASURE'             : row['NUM_WRT_ERASURE'],
            'SCTR_READ_CNT_BASELINE'      : row['SCTR_READ_CNT_BASELINE'],
            'SCTR_READ_CNT_ERASURE'       : row['SCTR_READ_CNT_ERASURE'],
            'BITS_IN_ERROR_BASELINE'      : row['BITS_IN_ERROR_BASELINE'],
            'BITS_IN_ERROR_ERASURE'       : row['BITS_IN_ERROR_ERASURE'],
            'BITS_IN_ERROR_DELTA'         : row['BITS_IN_ERROR_DELTA'],
            'BITS_IN_ERROR_RATIO'         : row['BITS_IN_ERROR_RATIO'],
            'BITS_IN_ERROR_BER_BASELINE'  : row['BITS_IN_ERROR_BER_BASELINE'],
            'BITS_IN_ERROR_BER_ERASURE'   : row['BITS_IN_ERROR_BER_ERASURE'],
            'BITS_IN_ERROR_BER_DELTA'     : row['BITS_IN_ERROR_BER_DELTA'],
            'OTF_BER_BASELINE'            : row['OTF_BER_BASELINE'],
            'OTF_BER_ERASURE'             : row['OTF_BER_ERASURE'],
            'OTF_BER_DELTA'               : row['OTF_BER_DELTA'],
            })

      if not testSwitch.FE_0146843_007955_P_DISABLE_PRINT_ERASE_DELTA:
         if not testSwitch.BF_0146418_231166_P_ONLY_PRINT_ERASE_DELTA_ONCE:
            objMsg.printDblogBin(self.dut.dblData.Tables('P051_ERASURE_BER_DELTAS'))
   
   #-------------------------------------------------------------------------------------------------------
   def runT51(self, atiParam):
      ec = 0 #pass
      try: self.St(atiParam)
      except ScriptTestFailure, (failureData):
         ec = failureData[0][2]
      return ec
   
   #-------------------------------------------------------------------------------------------------------
   def atiMeasurement(self,inPrm):
      """
      Measure adjacent track interferance ber using inPrm['base'] in each inPrm['ZONES'] for each inPrm['CENTER_TRACK_WRITES']
      *Note 2 update modes are supported...
      Either:
         define a listof CENTER_TRACK_WRITES and list of zones ZONE
            or
         define a parameter outside of base called PARAMS which is a list of dictionaries that define the
            updates to iterate through
      Optional:
         Calculate BER Prediction for 1 Million Writes, use BER data from a low number of writes(2000)
         and the BER data from a higher number of writes(10000), and calculate the BER for 1,000,000 writes
      """

      atiParam = paramExtractor.run(inPrm['base'].copy(), '', self.dut)
      if testSwitch.auditTest:
         prm_auditTest_T51={'prm_name'    : "prm_auditTest_T51",
                           'BAND_SIZE' : 5,
                           'ZONE_POSITION': 180, # bias towards ID to make room for retries
                           'RETRY_COUNTER_MAX': 4,
                           'RETRY_INCR':10,
                           'timeout':1800,
                           'MAX_TRK_HARD_ERRORS':(atiParam.get('MAX_TRK_HARD_ERRORS',100)),
                           }
         prm_auditTest_T51.update(getattr(TP, 'prm_auditTest_T51',{})) #make changes by program in testparameters.py
         atiParam.update( prm_auditTest_T51)

      test_head_list = range(self.dut.imaxHead)

      PBICFlag = 0
      if (self.dut.BG in ['SBS'] and len(ConfigVars[CN].get('PBICSwitches', '00000')) >= 1 and int(ConfigVars[CN].get('PBICSwitches', '00000')[0]) > 0) or \
         (self.dut.BG not in ['SBS'] and len(ConfigVars[CN].get('PBICSwitchesOEM', '00000')) >= 1 and int(ConfigVars[CN].get('PBICSwitchesOEM', '00000')[0]) > 0):
         PBICFlag = 1

      
      if testSwitch.PBIC_SUPPORT and PBICFlag == 1:         
         from PBIC import ClassPBIC
         objPBIC = ClassPBIC()
         test_head_list = objPBIC.PBIC_Control_bh()
      failedlen = []    
      for head in test_head_list:

         atiParam['TEST_HEAD'] = head
         spc_id = 0
         if 'ZONES' in inPrm:
            zoneCntr = 0
            for zone in inPrm['ZONES']:
               for bandWrites in inPrm['CENTER_TRACK_WRITES']:
                  atiParam['ZONE'] = zone
                  if testSwitch.extern.FE_0155590_443615_32_BIT_SUPPORT_FOR_NUMBER_WRITES:
                     atiParam['NUM_WRITES_32BIT'] = self.oUtility.ReturnTestCylWord(bandWrites)
                  else:
                     atiParam['CENTER_TRACK_WRITES'] = bandWrites
                  
                  if testSwitch.FE_0253166_504159_MERGE_FAT_SLIM:
                     if 'NUM_SUB_WRITES' in inPrm:
                        atiParam['NUM_SUB_WRITES'] = inPrm['NUM_SUB_WRITES']
                        atiParam['RD_TRKS_SUB_WRITES'] = inPrm['RD_TRKS_SUB_WRITES']
                 
                  #overwrite band size in atParam['band size']
                  if type(paramExtractor.run(inPrm['base'].copy(), '', self.dut)['BAND_SIZE']) == dict:
                     band_size_copy = paramExtractor.run(inPrm['base'].copy(), '', self.dut)['BAND_SIZE']
                     atiParam['BAND_SIZE'] = band_size_copy.get(zone, band_size_copy['default'])
                  
                  if 'SKIP_CENTER_TRK_WRT_AND_ZONE' in inPrm:
                     numWrtsToSkip = inPrm['SKIP_CENTER_TRK_WRT_AND_ZONE'][0]
                     zoneToSkip = inPrm['SKIP_CENTER_TRK_WRT_AND_ZONE'][1]
                     if numWrtsToSkip == bandWrites and zoneToSkip == zone:
                        continue

                  if testSwitch.FE_0132170_357915_USE_RETRY_PARMS_FOR_T51:
                     '''
                     zoneRetryParms should be a list of dictionaries containing retry parameter updates.  retryECList, 
                     retryCount and retryMode must also be specified in test parameters for this to work properly
                     '''
                     atiParam['retryParms'] = inPrm['zoneRetryParms'][zoneCntr]  
                  if testSwitch.auditTest ==0:
                     atiParamBK = self.oUtility.copy(atiParam)
                     #2 retries of different zone position
                     zonePosArRetry = [120, 80]
                     for retry in range(len(zonePosArRetry)+1):
                        try: 
                             startlen = len(self.dut.dblData.Tables('P051_ERASURE_BER').chopDbLog('SPC_ID', 'match', str(atiParam['spc_id'])))
                        except:
                             startlen = 0
                        ec = self.runT51(atiParam)
                        try:                         
                           endlen = len(self.dut.dblData.Tables('P051_ERASURE_BER').chopDbLog('SPC_ID', 'match', str(atiParam['spc_id'])))
                        except:
                             endlen = 0                           
                        if ec == 0: break #pass to continue
                        if ec == 10468:
                           if(startlen != endlen):
                              failedlen.append({'start': startlen, 'end' : endlen})
                           atiParam.update(atiParamBK) #copy back original param
                           #last retry with defect free band off
                           if retry == len(zonePosArRetry):
                              objMsg.printMsg("No defect Free Band Found : Retry without flaw table check")
                              atiParam['CWORD1'] = atiParam['CWORD1'] | 0x040 # bit6
                              ec = self.runT51(atiParam)
                              if ec > 0:
                                 ScrCmds.raiseException(ec, "Failed T51 in %s" % (self.dut.nextState))
                           else:
                              atiParam['ZONE_POSITION'] = zonePosArRetry[retry]
                              objMsg.printMsg("Retry at ZONE_POSITION %d in another direction" % (atiParam['ZONE_POSITION']))
                        else: ScrCmds.raiseException(ec, "Failed T51 in %s" % (self.dut.nextState))
                     atiParam.update(atiParamBK) #copy back original param
                  elif testSwitch.auditTest==1:
                     try: self.St(atiParam)
                     except ScriptTestFailure, (failureData):
                        ec = failureData[0][2]
                        if ec == 10482:
                           objMsg.printMsg("AUDIT TEST:'No defect Free Band Found'...retry without flaw list check 1X",objMsg.CMessLvl.IMPORTANT)
                           atiParam['CWORD1'] = atiParam['CWORD1'] | 0x040 # bit6
                           self.St(atiParam)
                        else: raise
                  if testSwitch.FE_0141706_399481_P_T51_DELTA_TABLE:
                     t51Table = self.dut.dblData.Tables('P051_ERASURE_BER').tableDataObj()
                     spc_id += 1
                     self.t51Diff(t51Table, spc_id)
            zoneCntr += 1

         elif 'PARAMS' in inPrm:
            for prmSet in inPrm['PARAMS']:
               atiParam.update(prmSet)
               if testSwitch.auditTest ==0:
                  if testSwitch.FE_0138325_336764_P_DISABLE_FLAW_TABLE_CHK_AFTER_RETRY_T50_T51:
                     try:
                        self.St(atiParam)
                     except ScriptTestFailure, (failureData):
                        ec = failureData[0][2]
                        if ec == 10482:
                           objMsg.printMsg("WRITE_SCRN retest:'No defect Free Band Found'...retry without flaw list check 1X",objMsg.CMessLvl.IMPORTANT)
                           atiParam_bit6 = atiParam.copy()
                           if type(atiParam_bit6['CWORD1']) in [types.ListType,types.TupleType]:
                              atiParam_bit6['CWORD1'] = atiParam_bit6['CWORD1'][0]
                           atiParam_bit6['CWORD1'] |= 0x040 # bit6
                           self.St(atiParam_bit6)
                        else:
                           raise
                  else:
                     self.St(atiParam)
               elif testSwitch.auditTest==1:
                  try:
                     self.St(atiParam)
                  except ScriptTestFailure, (failureData):
                     ec = failureData[0][2]
                     if ec == 10482:
                        objMsg.printMsg("AUDIT TEST:'No defect Free Band Found'...retry without flaw list check 1X",objMsg.CMessLvl.IMPORTANT)
                        atiParam['CWORD1'] = atiParam['CWORD1'] | 0x040 # bit6
                        self.St(atiParam)
                     else:
                        raise

      objMsg.printMsg("failedlen : %s" % failedlen)
      if not testSwitch.FE_0146843_007955_P_DISABLE_PRINT_ERASE_DELTA:
         if testSwitch.BF_0146418_231166_P_ONLY_PRINT_ERASE_DELTA_ONCE and testSwitch.FE_0141706_399481_P_T51_DELTA_TABLE:
            #only print out after all by head deltas are calculated
            objMsg.printDblogBin(self.dut.dblData.Tables('P051_ERASURE_BER_DELTAS'))

      if 0:
         try:
            (maxDiff, minDiff, diffData, entrySigVal) = self.dut.dblData.Tables('P051_ERASURE_BER').diffDbLog(diffItem='OTF_BER',entrySig='TEST_TYPE',sortOrder=['HD_LGC_PSN','DATA_ZONE', 'TRK_NUM'])
            for item in diffData:
               self.dut.dblData.Tables('P_DELTA_OTF').addRecord(
            {
            'HD_PHYS_PSN':          item.get('HD_PHYS_PSN'),
            'DATA_ZONE':            item.get('DATA_ZONE'),
            'SPC_ID':               self.dut.objSeq.curRegSPCID,
            'OCCURRENCE':           self.dut.objSeq.getOccurrence(),
            'SEQ':                  self.dut.objSeq.curSeq,
            'TEST_SEQ_EVENT':       self.dut.objSeq.getTestSeqEvent(0),
            'TRK_NUM':              item.get('TRK_NUM'),
            'DELTA_OTF':           item.get('difference')
            })

         except:
            objMsg.printMsg("Unable to retrieve P051_ERASURE_BER table data")

         objMsg.printDblogBin(self.dut.dblData.Tables('P_DELTA_OTF'))

      ##  Parse P051_ERASURE_BER and check failing criteria
      noExcept = True
      newtable = []
      ignore = 0
      try:
         spc_id_local = atiParam['spc_id']
         # if testSwitch.virtualRun and self.dut.nextState == 'WRITE_SCRN' : spc_id_local = 3000
         table = self.dut.dblData.Tables('P051_ERASURE_BER').chopDbLog('SPC_ID', 'match', str(spc_id_local))
         if len(failedlen) == 0 :
             newtable = table
         else:
             for idx, item in enumerate(table):
                 for flen in failedlen :
                     if (idx in range(flen['start'],(flen['end']))) :
                         ignore = 1
                         break
                 if ignore != 0:
                     ignore = 0
                 else :
                     newtable.append(item)
      except:
         objMsg.printMsg("Unable to retrieve P051_ERASURE_BER table data")
         noExcept = False

      #data collection mode only
      if testSwitch.DB_0275227_480505_WRITE_SCRN_MONITORING_ONLY:
         noExcept = False

      if noExcept:
         if TP.RRAW_CRITERIA_ATI_51:
            #=== Form RRAW and OTF tables
            rrawTable = {}
            bieBerTable = {}

            if inPrm.has_key('TEST_TYPE'):
               testtype = inPrm['TEST_TYPE']
            else:
               testtype = 'erasure'

            self.formAtiTable(newtable, rrawTable, 'RRAW_BER', offset=0.0, testType=testtype)
            self.formAtiTable(newtable, bieBerTable, 'BITS_IN_ERROR_BER', offset=0.0, testType=testtype)
            #=== Update DBLog
            self.updateAtiDbLog(rrawTable, berType='RRAW', testType=testtype)
            self.updateAtiDbLog(bieBerTable, berType='SOVA', testType=testtype)


            if testSwitch.FE_0253166_504159_MERGE_FAT_SLIM and 'NUM_SUB_WRITES' in inPrm:
               list_sub_write = [i for i in inPrm['NUM_SUB_WRITES'] ]
               list_sub_write.sort()
               dictlistforRrawTable = [{} for i in inPrm['NUM_SUB_WRITES']]
               dictlistforBieBerTable = [{} for i in inPrm['NUM_SUB_WRITES']]
               for num_write in list_sub_write:
                   if num_write >= 1:
                       testtype = 'erasure' + str(list_sub_write.index(num_write))
                       self.formAtiTable(newtable, dictlistforRrawTable[list_sub_write.index(num_write)], 'RRAW_BER', offset=0.0, testType=testtype)
                       self.formAtiTable(newtable, dictlistforBieBerTable[list_sub_write.index(num_write)], 'BITS_IN_ERROR_BER', offset=0.0, testType=testtype)
                       #=== Update DBLog
                       self.updateAtiDbLog(dictlistforRrawTable[list_sub_write.index(num_write)], berType='RRAW', testType=testtype)
                       self.updateAtiDbLog(dictlistforBieBerTable[list_sub_write.index(num_write)], berType='SOVA', testType=testtype)
            else: list_sub_write = []

            if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_ATI_MSG:
               self.printAtiDblog()

            #=== Check criteria
            if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE:
               if testSwitch.FE_0253166_504159_MERGE_FAT_SLIM and 'NUM_SUB_WRITES' in inPrm:
                  if TP.prm_SMR_zone_Fat_500['CENTER_TRACK_WRITES'][0] in inPrm['NUM_SUB_WRITES']:
                     idex = list_sub_write.index(TP.prm_SMR_zone_Fat_500['CENTER_TRACK_WRITES'][0])
                     testtype = 'erasure' + str(idex)
                     bieBerTable = dictlistforBieBerTable[idex]
                     rrawTable = dictlistforRrawTable[idex]
               self.checkAtiSteCriteriaWithWaterfall(rrawTable, bieBerTable, TEST_TYPE = testtype)
               for sub_writes in list_sub_write:
                  if sub_writes > 0:
                     if TP.prm_SMR_zone_Slim['CENTER_TRACK_WRITES'][0] in inPrm['NUM_SUB_WRITES']:
                        idex = list_sub_write.index(TP.prm_SMR_zone_Slim['CENTER_TRACK_WRITES'][0])
                        testtype = 'erasure' + str(idex)
                        bieBerTable = dictlistforBieBerTable[idex]
                        rrawTable = dictlistforRrawTable[idex]
                        self.checkSlimAtiSteCriteriaWithWaterfall(rrawTable, bieBerTable, TEST_TYPE = testtype)
            else:
               if testSwitch.FE_0253166_504159_MERGE_FAT_SLIM and 'NUM_SUB_WRITES' in inPrm:
                  if TP.prm_SMR_zone_Fat_500['CENTER_TRACK_WRITES'][0] in inPrm['NUM_SUB_WRITES']:
                     idex = list_sub_write.index(TP.prm_SMR_zone_Fat_500['CENTER_TRACK_WRITES'][0])
                     testtype = 'erasure' + str(idex)
                     bieBerTable = dictlistforBieBerTable[idex]
                     rrawTable = dictlistforRrawTable[idex]
               self.checkAtiSteCriteria('RRAW', TP.RRAW_CRITERIA_ATI_51, rrawTable, testType=testtype)
               self.checkAtiSteCriteria('SOVA', TP.BIE_BER_CRITERIA_ATI_51, bieBerTable, testType=testtype)
               for sub_writes in list_sub_write:
                  if sub_writes > 0:
                     if TP.prm_SMR_zone_Slim['CENTER_TRACK_WRITES'][0] in inPrm['NUM_SUB_WRITES']:
                        idex = list_sub_write.index(TP.prm_SMR_zone_Slim['CENTER_TRACK_WRITES'][0])
                        testtype = 'erasure' + str(idex)
                        bieBerTable = dictlistforBieBerTable[idex]
                        rrawTable = dictlistforRrawTable[idex]
                        self.checkAtiSteCriteria('RRAW', TP.RRAW_CRITERIA_ATI_51_SLIM, rrawTable, testType=testtype)
                        self.checkAtiSteCriteria('SOVA', TP.BIE_BER_CRITERIA_ATI_51, bieBerTable, testType=testtype)

      if inPrm.has_key('LIMITS') and inPrm['LIMITS']['CALCULATE_BER_PRED'] == 1:
         # Calculate BER Prediction data from the DB log
         Limits = inPrm.get('LIMITS', {})
         RP_Limit = Limits.get('RP_LIMIT', 4.500)
         OD_Limit = Limits.get('OD_LIMIT', 0.000)

         # L10_LNW=low num wrt, L10_HNW=high num wrt, L10_PNW=Predicted num wrt
         if testSwitch.FE_0160920_443615_NUM_WRITES_32BIT_FOR_PF3:
            if bandWrites > 0xFFFF:
               LNW = inPrm['PARAMS'][0]['NUM_WRITES_32BIT']
               HNW = inPrm['PARAMS'][-1]['NUM_WRITES_32BIT']
            else:
               LNW = inPrm['PARAMS'][0]['CENTER_TRACK_WRITES']
               HNW = inPrm['PARAMS'][-1]['CENTER_TRACK_WRITES']
         else:
            LNW = inPrm['PARAMS'][0]['CENTER_TRACK_WRITES']
            HNW = inPrm['PARAMS'][-1]['CENTER_TRACK_WRITES']
         PNW = Limits.get('PRED_NUM_WRITES', 1000000)
         L10_LNW = log10(float(LNW))
         L10_HNW = log10(float(HNW))
         L10_PNW = log10(float(PNW))
         MF = ((L10_PNW-L10_LNW) / (L10_HNW-L10_LNW))  # Multiplication Factor

         tableData = self.dut.dblData.Tables('P051_ERASURE_BER').tableDataObj()
         tableLength = len(tableData)
         numberOfHeads = self.dut.imaxHead
         numberOfZones = len(inPrm['PARAMS']) / 2
         numberOfTests = len(inPrm['PARAMS']) * numberOfHeads
         itemsPerTest  = tableLength / numberOfTests
         objMsg.printMsg("BER Table Length=%s NumTests=%s ItemsPerTest=%s NumHeads=%s NumZones=%s" % (tableLength,numberOfTests,itemsPerTest,numberOfHeads,numberOfZones))
         objMsg.printMsg("BER Low Num Writes=%s High Num Writes=%s Predicted Num Writes=%s" % (LNW, HNW, PNW))
         objMsg.printMsg("BER Calculation Log10-%s=%1.3f Log10-%s=%1.3f Log10-%s=%1.3f MF=%1.3f" % (LNW,L10_LNW,HNW,L10_HNW,PNW,L10_PNW,MF))
         objMsg.printMsg("BER Calculation RRAW Prediction Low Limit=%s OTF Delta High Limit=%s" % (RP_Limit,OD_Limit))
         objMsg.printMsg(" HEAD  ZONE  TRACK    R-LOW   R-HIGH   R-PRED   R-LIMIT   O-LOW    O-HIGH   O-DELTA  O-LIMIT")
         LNW_Values = {}   # Default dictionary for Low number of writes BER values
         HNW_Values = {}   # Default dictionary for High number of writes BER values

         # Fill the LNW/HNW dictionary's with BER data
         startData = 0
         endData = itemsPerTest
         for test in range(numberOfTests):
            testData = tableData[startData:endData]
            startData = startData + itemsPerTest
            endData = endData + itemsPerTest
            for item in range(len(testData)):
               HD = testData[item]['HD_LGC_PSN']; NW = testData[item]['NUM_WRT']; TN = testData[item]['TRK_NUM']
               TT = testData[item]['TEST_TYPE']; DZ = testData[item]['DATA_ZONE']; RB = testData[item]['RRAW_BER']
               OB = testData[item]['OTF_BER']
               if TT == 'erasure':
                  OB = testData[item - itemsPerTest]['OTF_BER']
               Key_String = str(test)+'_'+str(item)+'_'+str(LNW)
               ZONE_Key = 'ZONE_' + Key_String; HEAD_Key = 'HEAD_' + Key_String
               NWRT_Key = 'NWRT_' + Key_String
               Key_String = str(test)+'_'+str(item)+'_'+str(DZ)+'_'+str(HD)+'_'+str(NW)
               TRKN_Key = 'TRKN_' + Key_String; TYPE_Key = 'TYPE_' + Key_String
               RRAW_Key = 'RRAW_' + Key_String; OTF_Key  = 'OTF_' + Key_String
               objMsg.printMsg("T=%s I=%s Head=%s Zone=%s Track=%s Num_Wrt=%s T_Key=%s TN_Key=%s Z_KEY=%s H_KEY=%s R_KEY=%s O_KEY=%s" % \
                              (test,item,HD,DZ,TN,NW,TT,TRKN_Key,ZONE_Key,HEAD_Key,RRAW_Key,OTF_Key))
               if NW != HNW:
                  LNW_Values[ZONE_Key] = DZ
                  LNW_Values[HEAD_Key] = HD
                  LNW_Values[TYPE_Key] = TT
                  LNW_Values[NWRT_Key] = NW
                  LNW_Values[TRKN_Key] = TN
                  LNW_Values[RRAW_Key] = RB
                  LNW_Values[OTF_Key]  = OB
               else:
                  LNW_Values[ZONE_Key] = DZ
                  LNW_Values[HEAD_Key] = HD
                  LNW_Values[NWRT_Key] = NW
                  LNW_Values[TYPE_Key] = TT
                  HNW_Values[NWRT_Key] = NW
                  HNW_Values[TYPE_Key] = TT
                  HNW_Values[TRKN_Key] = TN
                  HNW_Values[RRAW_Key] = RB
                  HNW_Values[OTF_Key]  = OB

         # Calculate Prediction and check Pass Fail
         dataOffset = numberOfZones
         for Ltest in range(numberOfTests):
            Htest = Ltest + dataOffset
            for item in range(itemsPerTest):
               Key_String = str(Ltest)+'_'+str(item)+'_'+str(LNW)
               ZONE_Key = 'ZONE_' + Key_String; DZ = LNW_Values[ZONE_Key]
               HEAD_Key = 'HEAD_' + Key_String; HD = LNW_Values[HEAD_Key]
               NWRT_LNW_Key = 'NWRT_' + Key_String
               Key_String = '_'+str(item)+'_'+str(DZ)+'_'+str(HD)+'_'
               TRKN_LNW_Key = 'TRKN_'+str(Ltest)+Key_String+str(LNW); TYPE_LNW_Key = 'TYPE_'+str(Ltest)+Key_String+str(LNW)
               RRAW_LNW_Key = 'RRAW_'+str(Ltest)+Key_String+str(LNW); RRAW_HNW_Key = 'RRAW_'+str(Htest)+Key_String+str(HNW)
               OTF_LNW_Key  = 'OTF_'+str(Ltest)+Key_String+str(LNW); OTF_HNW_Key = 'OTF_'+str(Htest)+Key_String+str(HNW)
               objMsg.printMsg("T=%s I=%s H=%s Z=%s N_LNW=%s T_LNW=%s R_LNW=%s R_HNW=%s O_LNW=%s O_HNW=%s" % \
                              (Ltest,item,HD,DZ,NWRT_LNW_Key,TRKN_LNW_Key,RRAW_LNW_Key,RRAW_HNW_Key,OTF_LNW_Key,OTF_HNW_Key))
               objMsg.printMsg("LNW_Values[NWRT_LNW_Key]=%s LNW=%s LNW_Values[TYPE_LNW_Key]=%s" % \
                              (LNW_Values[NWRT_LNW_Key], LNW, LNW_Values[TYPE_LNW_Key]))
               if LNW_Values[NWRT_LNW_Key] == LNW and LNW_Values[TYPE_LNW_Key] == 'erasure':
                  TN = LNW_Values[TRKN_LNW_Key]
                  RL = LNW_Values[RRAW_LNW_Key]
                  RH = HNW_Values[RRAW_HNW_Key]
                  OL = LNW_Values[OTF_LNW_Key]
                  OH = HNW_Values[OTF_HNW_Key]
                  RP = (RL + (RH - RL) * MF)
                  OD = (OH - OL)
                  objMsg.printMsg("HD=%02d ZN=%02d TN=%s RL=%1.3f RH=%1.3f RP=%1.3f RLV=%1.3f OL=%1.3f OH=%1.3f OD=%1.3f OLV=%1.3f" % \
                                 (HD,DZ,TN,RL,RH,RP,RP_Limit,OL,OH,abs(OD),OD_Limit))
                  if RP < RP_Limit or abs(OD) > OD_Limit:
                     objMsg.printMsg("----------------------- BER Prediction FAILED ----------------------")
                     objMsg.printMsg("BER RRAW - Low Limit = %1.3f  Predicted = %1.3f" % (RP_Limit,RP))
                     objMsg.printMsg("BER OTF - High Limit = %1.3f  Delta = %1.3f" % (OD_Limit,abs(OD)))
                     ScrCmds.raiseException(14574, "Delta BER limit exceeded")

#===============================================================================
   def formAtiTable(self, table, newTable, berType, offset=0.0, testType='erasure'):
      """
      Table format:
      newTable = {(hd,zn,trk): {'baseline'        : data1,
                                testType          : data2,
                                'delta'           : data3,
                                'deltapercentage' : data4,
                               }, ...
                 }
      """
      #=== Get 'baseline' and testType data
      if testType == 'encroach':   # T50
         for record in table:
            key = int(record['HD_PHYS_PSN']),\
                  int(record['DATA_ZONE']),\
                  int(record['TRK_NUM'])
            item = {record['TEST_TYPE']: float(record[berType]) - offset}
            newTable.setdefault(key,{}).update(item)
      else:   # T51
         for record in table:
            key = int(record['HD_PHYS_PSN']),\
                  int(record['DATA_ZONE']),\
                  int(record['TRK_NUM']),\
                  int(record['TRK_INDEX'])
            item = {record['TEST_TYPE']: float(record[berType]) - offset}
            newTable.setdefault(key,{}).update(item)
      #=== Calculate 'delta' and 'deltapercentage'
      # 1. delta = baseline - erasure
      # 2. deltapercentage = delta / baseline * 100
      # 3. If erasure > baseline, delta=deltapercentage=0
      # 4. If erasure ber is not available, erasure=delta=deltapercentage=None
      # 5. Add these keys and value to newTable.
      for key in newTable:
         if newTable[key].has_key(testType):
            newTable[key]['delta'] = newTable[key]['baseline'] - newTable[key][testType]
            # Take care of "ZeroDivisionError"
            try:
               newTable[key]['deltapercentage'] = newTable[key]['delta']/newTable[key]['baseline'] * 100
            except:
               newTable[key]['deltapercentage'] = None
            if newTable[key]['delta'] < 0:
               newTable[key]['delta'] = 0
               newTable[key]['deltapercentage'] = 0
         else:
            newTable[key][testType] = None
            newTable[key]['delta'] = None
            newTable[key]['deltapercentage'] = None

      if testSwitch.FE_0253166_504159_MERGE_FAT_SLIM and testType !='erasure':
         for key in newTable.keys():
             if newTable[key][testType] == None:
                newTable.pop(key)

#===============================================================================
   def updateAtiDbLog (self, table, berType, testType='erasure'):
      #=== Sort out table keys
      keys = table.keys()
      keys.sort()

      #=== Update dblog
      for key in keys:
         if testSwitch.DB_0275227_480505_WRITE_SCRN_MONITORING_ONLY and ('baseline' not in table.get(key)):
            continue

         self.dut.dblData.Tables('P_SIDE_ENCROACH_BER').addRecord(
            {
            'SPC_ID'              : self.dut.objSeq.curRegSPCID,
            'OCCURRENCE'          : self.dut.objSeq.getOccurrence(),
            'SEQ'                 : self.dut.objSeq.curSeq,
            'TEST_SEQ_EVENT'      : self.dut.objSeq.getTestSeqEvent(0),
            'HD_LGC_PSN'          : key[0],  # hd
            'HD_PHYS_PSN'         : key[0],  # hd
            'BASELINE_BER'        : table[key]['baseline'],
            'ERASURE_BER'         : table[key][testType],
            'DELTA_BER'           : table[key]['delta'],
            'DELTA_BER_PERCENTAGE': table[key]['deltapercentage'],
            'DATA_ZONE'           : key[1],  # zone
            'TRK_NUM'             : key[2],  # trk
            'WRT_TRK_AWAY_TUT_NDX': key[3],  # trk index
            'TYPE'                : berType,
            })


#===============================================================================
   def printAtiDblog(self, seq = None):
      #objMsg.printDblogBin(self.dut.dblData.Tables('P_SIDE_ENCROACH_BER'))
      # Print P_SIDE_ENCROACH_BER in table format
      if seq == None: seq = self.dut.objSeq.curSeq
      
      ScriptComment ("P51_SIDE_ENCROACH_BER:", writeTimestamp=0)
      ScriptComment ("HD_PHYS_PSN  DATA_ZONE  TRK_NUM  TRK_INDEX  BASELINE_BER  ERASURE_BER  DELTA_BER  DELTA_BER_PERCENTAGE  TYPE",
                     writeTimestamp=0)
      
      atiTable = self.dut.dblData.Tables('P_SIDE_ENCROACH_BER').chopDbLog('SEQ', 'match', seq)
      
      for rec in atiTable:
         if rec['ERASURE_BER'] == None:
            ScriptComment("%11d%11d%9d%11d%14.2f%13s%11s%22s%6s" %(rec['HD_PHYS_PSN'],rec['DATA_ZONE'],rec['TRK_NUM'],rec['WRT_TRK_AWAY_TUT_NDX'],
                          rec['BASELINE_BER'],rec['ERASURE_BER'],rec['DELTA_BER'],rec['DELTA_BER_PERCENTAGE'],
                          rec['TYPE']), writeTimestamp=0)
         elif rec['DELTA_BER_PERCENTAGE'] == None:
            ScriptComment("%11d%11d%9d%11d%14.2f%13.2f%11.2f%22s%6s" %(rec['HD_PHYS_PSN'],rec['DATA_ZONE'],rec['TRK_NUM'],rec['WRT_TRK_AWAY_TUT_NDX'],
                          rec['BASELINE_BER'],rec['ERASURE_BER'],rec['DELTA_BER'],rec['DELTA_BER_PERCENTAGE'],
                          rec['TYPE']), writeTimestamp=0)
         else:
            ScriptComment("%11d%11d%9d%11d%14.2f%13.2f%11.2f%22.2f%6s" %(rec['HD_PHYS_PSN'],rec['DATA_ZONE'],rec['TRK_NUM'],rec['WRT_TRK_AWAY_TUT_NDX'],
                          rec['BASELINE_BER'],rec['ERASURE_BER'],rec['DELTA_BER'],rec['DELTA_BER_PERCENTAGE'],
                          rec['TYPE']), writeTimestamp=0)

#===============================================================================
   ##
   # Wrapper function around checkAtiSteCriteria
   # This function contain the logic to handle part number downgrade, mainly from OEM to SBS partnumber change
   ##
   def checkAtiSteCriteriaWithWaterfall(self, rrawTable, bieBerTable, TEST_TYPE = 'erasure'):
      origPartNum = self.dut.partNum
      origAttr = self.dut.driveattr["DNGRADE_ON_FLY"]
      origNiblet_Level=self.dut.Niblet_Level
      for i in xrange(5):
         downgrade_done = 0
         objMsg.printMsg("Checking ATI Criteria: PartNumber %s DNGRADE_ON_FLY %s" %(str(self.dut.partNum),str(self.dut.driveattr["DNGRADE_ON_FLY"]) ))
         #=== Load T51 criteria
         self.dut.driveattr['PART_NUM'] = self.dut.partNum
         objMsg.printMsg("RRAW_CRITERIA_ATI_51=%s " %(str(TP.RRAW_CRITERIA_ATI_51)))
         objMsg.printMsg("BIE_BER_CRITERIA_ATI_51=%s " %(str(TP.BIE_BER_CRITERIA_ATI_51)))
         try:
            self.checkAtiSteCriteria('RRAW', TP.RRAW_CRITERIA_ATI_51, rrawTable, testType = TEST_TYPE)
            self.checkAtiSteCriteria('SOVA', TP.BIE_BER_CRITERIA_ATI_51, bieBerTable, testType = TEST_TYPE)
            break
         except ScrCmds.CRaiseException, (failureData):
            if failureData[0][2] in [14635, 14861]:
               downgrade_done = CState(self.dut).downGradeOnFly(1,(failureData[0][2]))
            if not downgrade_done :
               self.dut.partNum = origPartNum
               self.dut.driveattr['PART_NUM'] = self.dut.partNum
               self.dut.Niblet_Level=origNiblet_Level
               self.dut.driveattr['NIBLET_LEVEL'] = self.dut.Niblet_Level
               objMsg.printMsg("Niblet_Level=%s"%str(self.dut.Niblet_Level))
               self.dut.driveattr["DNGRADE_ON_FLY"] = origAttr
               raise
   
   ##
   # Wrapper function around checkSlimAtiSteCriteria
   # This function contain the logic to handle part number downgrade, mainly from OEM to SBS partnumber change
   ##
   def checkSlimAtiSteCriteriaWithWaterfall(self, rrawTable, bieBerTable, TEST_TYPE = 'erasure'):
      origPartNum = self.dut.partNum
      origAttr = self.dut.driveattr["DNGRADE_ON_FLY"]
      origNiblet_Level=self.dut.Niblet_Level
      for i in xrange(5):
         downgrade_done = 0
         objMsg.printMsg("Checking ATI Criteria: PartNumber %s DNGRADE_ON_FLY %s" %(str(self.dut.partNum),str(self.dut.driveattr["DNGRADE_ON_FLY"]) ))
         #=== Load T51 criteria
         self.dut.driveattr['PART_NUM'] = self.dut.partNum
         objMsg.printMsg("RRAW_CRITERIA_ATI_51=%s " %(str(TP.RRAW_CRITERIA_ATI_51_SLIM)))
         objMsg.printMsg("BIE_BER_CRITERIA_ATI_51=%s " %(str(TP.BIE_BER_CRITERIA_ATI_51)))
         try:
            self.checkAtiSteCriteria('RRAW', TP.RRAW_CRITERIA_ATI_51_SLIM, rrawTable, testType = TEST_TYPE)
            self.checkAtiSteCriteria('SOVA', TP.BIE_BER_CRITERIA_ATI_51, bieBerTable, testType = TEST_TYPE)
            break
         except ScrCmds.CRaiseException, (failureData):
            if failureData[0][2] in [14635, 14861]:
               downgrade_done = CState(self.dut).downGradeOnFly(1,(failureData[0][2]))
            if not downgrade_done :
               self.dut.partNum = origPartNum
               self.dut.driveattr['PART_NUM'] = self.dut.partNum
               self.dut.Niblet_Level=origNiblet_Level
               self.dut.driveattr['NIBLET_LEVEL'] = self.dut.Niblet_Level
               objMsg.printMsg("Niblet_Level=%s"%str(self.dut.Niblet_Level))
               self.dut.driveattr["DNGRADE_ON_FLY"] = origAttr
               raise
               
   #For DDIS collect info
   def reportFailInfo(self,key,table,testType):
      failhead = set()
      ScriptComment ("P51_DDIS_INFO:", writeTimestamp=0)
      ScriptComment ("HD_LGC_PSN  FAIL_ZN  TRK_INDEX  BASELINE_BER  ERASURE_BER  FAIL_STATE",writeTimestamp=0)
      for i in key:
         self.dut.dblData.Tables('P51_DDIS_INFO').addRecord(
            {
            'SPC_ID'              : self.dut.objSeq.curRegSPCID,
            'OCCURRENCE'          : self.dut.objSeq.getOccurrence(),
            'SEQ'                 : self.dut.objSeq.curSeq,
            'TEST_SEQ_EVENT'      : self.dut.objSeq.getTestSeqEvent(0),
            'HD_LGC_PSN'          : i[0],  # hd
            'FAIL_ZN'             : i[1],
            'TRK_INDEX'           : i[3],
            'BASELINE_BER'        : table[i]['baseline'],
            'ERASURE_BER'         : table[i][testType],
            'FAIL_STATE'          : self.dut.nextState,

            })

         ScriptComment("%10d%10d%10d%14.2f%13s%19s" %(i[0],i[1],i[3],\
                             table[i]['baseline'],table[i][testType],self.dut.nextState),
                             writeTimestamp=0)
         failhead.add(i[0])
      return map(int, failhead)

   #-------------------------------------------------------------------------------------
   def checkAtiCriteria (self, berType, criteria, table, testType='erasure', testNo=51):
      #=== Print ATI criteria
      ScriptComment("\nD0%d_%s_CRITERIA:" %(testNo, berType), writeTimestamp=0)
      ScriptComment("%s%25s"%('NAME','VALUE'), writeTimestamp=0)
      criteriaList = ['baseline_limit','erasure_limit','delta_limit','deltapercentage_limit']
      for n in criteriaList:
         if criteria[n][0]:
            ScriptComment ("%-21s%9.2f" %(n,criteria[n][1]), writeTimestamp=0)
      ScriptComment("", writeTimestamp=0)

      #=== Check baseline and erasure limit
      failed = False
      if criteria['baseline_limit'][0]: # if criterion is enabled
         for key in table:
            if table[key]['baseline'] < criteria['baseline_limit'][1]:
               failed = True
               break
         if failed:
            if testSwitch.auditTest ==0:
               ScrCmds.raiseException(14635,"T0%d %s baseline failed." %(testNo, berType))
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s baseline failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)
      #=== Check erasure limit
      failed = False
      if criteria['erasure_limit'][0]:
         for key in table:
            if testType in table[key]:
               if (table[key][testType] < criteria['erasure_limit'][1] or table[key][testType] == None) and \
                  key[3] not in criteria.get('SKIP_CHK', []):
                  failed = True
                  break
         if failed:
            if testSwitch.auditTest ==0:
               ScrCmds.raiseException(14635,"T0%d %s erasure failed." %(testNo, berType))
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s erasure failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      #=== Check delta limit
      failed = False
      if criteria['delta_limit'][0]:
         for key in table:
            if table[key]['delta'] > criteria['delta_limit'][1] or table[key]['delta'] == None:
               failed = True
               break
         if failed:
            if testSwitch.auditTest ==0:
               ScrCmds.raiseException(14635,"T0%d %s delta failed." %(testNo, berType))
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s delta failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)
      #=== Check delta percentage limit
      failed = False
      if criteria['deltapercentage_limit'][0]:
         for key in table:
            if table[key]['deltapercentage'] > criteria['deltapercentage_limit'][1] or table[key]['deltapercentage'] == None:
               failed = True
               break
         if failed:
            if testSwitch.auditTest ==0:
               ScrCmds.raiseException(14635,"T0%d %s delta percentage failed." %(testNo, berType))
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s delta percentage failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

   def checkAtiSteCriteria (self, berType, criteria, table, testType='erasure', testNo=51):
      #=== Print ATI criteria
      ScriptComment("\nD0%d_%s_CRITERIA:" %(testNo, berType), writeTimestamp=0)
      ScriptComment("%s%25s"%('NAME','VALUE'), writeTimestamp=0)
      criteriaList = ['baseline_limit','erasure_limit','delta_limit','deltapercentage_limit']
      for n in criteriaList:
         if criteria[n][0]:
            ScriptComment ("ATI_%-21s%9.2f" %(n,criteria[n][1]), writeTimestamp=0)
         if criteria[n][2]:
            ScriptComment ("STE_%-21s%9.2f" %(n,criteria[n][3]), writeTimestamp=0)
      ScriptComment("", writeTimestamp=0)

      if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
         if berType == 'SOVA':
            failed = False
            berDropCount = 0
            if criteria['baseline_limit'][0] and criteria['erasure_limit'][0]:
               for key in table:
                  if (key[1] == 1) and (abs(key[3]) > 1) and (abs(key[3]) <= 20): # ump zone 1 / track index +/-2 ~ +/-20
                     if (table[key][testType] < criteria['erasure_limit'][1] or table[key][testType] == None) and \
                        (table[key]['baseline'] > criteria['baseline_limit'][1] or table[key]['baseline'] == None):
                        berDropCount += 1
                        if berDropCount > 2:
                           failed = True
                           break
                  if failed:
                     StrCmds.raiseException(14861,"ATI by Sova Failed")
      elif 0 and berType == 'SOVA':
         for key in table:
            if abs(key[3]) != 1:
               if (table[key][testType] < criteria['erasure_limit'][3] or table[key][testType] == None) and \
                  (table[key]['delta'] > criteria['delta_limit'][3] or table[key]['delta'] == None) :
                  ScrCmds.raiseException(14861,"STE by Sova Failed")
         return
      #=== Check baseline limit
      failtrack = []
      failed = False
      if criteria['baseline_limit'][0]: # if ATI criterion is enabled
         for key in table:
            if table[key]['baseline'] < criteria['baseline_limit'][1] and abs(key[3]) == 1:
               failed = True
               failtrack.append(key)
               #break
         if failed:
            if testSwitch.auditTest ==0:
               failhead = self.reportFailInfo(failtrack,table,testType)
               ScrCmds.raiseException(15001, "T0%d %s ATI baseline failed @ Head : %s" % (testNo, berType, str(failhead)))
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s baseline failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      failed = False
      if criteria['baseline_limit'][2]: # if STE criterion is enabled
         for key in table:
            if table[key]['baseline'] < criteria['baseline_limit'][3] and abs(key[3]) != 1:
               failed = True
               failtrack.append(key)
               #break
         if failed:
            if testSwitch.auditTest ==0:
               failhead = self.reportFailInfo(failtrack,table,testType)
               ScrCmds.raiseException(15001, "T0%d %s STE baseline failed @ Head : %s" % (testNo, berType, str(failhead)))
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s baseline failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      #=== Check erasure limit
      failed = False
      if criteria['erasure_limit'][2]: # if STE criterion is enabled
         for key in table:
            if testType in table[key]:
               if (table[key][testType] < criteria['erasure_limit'][3] or table[key][testType] == None) and \
               (key[3] not in criteria.get('SKIP_CHK', []) and abs(key[3]) != 1):
                  failed = True
                  failtrack.append(key)
                  #break
         if failed:
            if testSwitch.auditTest ==0:
               failhead = self.reportFailInfo(failtrack,table,testType)
               ScrCmds.raiseException(14861, "T0%d %s STE erasure failed @ Head : %s" % (testNo, berType, str(failhead)))
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s erasure failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      failed = False
      if criteria['erasure_limit'][0]: # if ATI criterion is enabled
         for key in table:
            if testType in table[key]:
               if (table[key][testType] < criteria['erasure_limit'][1] or table[key][testType] == None) and \
               (key[3] not in criteria.get('SKIP_CHK', []) and abs(key[3]) == 1):
                  failed = True
                  failtrack.append(key)
                  #break
         if failed:
            if testSwitch.auditTest ==0:
               failhead = self.reportFailInfo(failtrack,table,testType)
               ScrCmds.raiseException(14635, "T0%d %s ATI erasure failed @ Head : %s" % (testNo, berType, str(failhead)))
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s erasure failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      #=== Check delta limit
      failed = False
      if criteria['delta_limit'][0]:  # if ATI criterion is enabled
         for key in table:
            if (table[key]['delta'] > criteria['delta_limit'][1] or table[key]['delta'] == None) and  abs(key[3]) == 1:
               failed = True
               failtrack.append(key)
               #break
         if failed:
            if testSwitch.auditTest ==0:
               failhead = self.reportFailInfo(failtrack,table,testType)
               ScrCmds.raiseException(14635, "T0%d %s ATI delta failed @ Head : %s" % (testNo, berType, str(failhead)))
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s delta failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      failed = False
      if criteria['delta_limit'][2]: # if STE criterion is enabled
         for key in table:
            if (table[key]['delta'] > criteria['delta_limit'][3] or table[key]['delta'] == None) and  abs(key[3]) != 1:
               failed = True
               failtrack.append(key)
               #break
         if failed:
            if testSwitch.auditTest ==0:
               failhead = self.reportFailInfo(failtrack,table,testType)
               ScrCmds.raiseException(14861, "T0%d %s STE delta failed @ Head : %s" % (testNo, berType, str(failhead)))
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s delta failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      #=== Check delta percentage limit
      failed = False
      if criteria['deltapercentage_limit'][0]:  # if ATI criterion is enabled
         for key in table:
            if (table[key]['deltapercentage'] > criteria['deltapercentage_limit'][1] or table[key]['deltapercentage'] == None) and abs(key[3]) == 1:
               failed = True
               failtrack.append(key)
               #break
         if failed:
            if testSwitch.auditTest ==0:
               failhead = self.reportFailInfo(failtrack,table,testType)
               ScrCmds.raiseException(14635, "T0%d %s ATI delta percentage failed @ Head : %s" % (testNo, berType, str(failhead)))
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s delta percentage failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      failed = False
      if criteria['deltapercentage_limit'][2]: # if STE criterion is enabled
         objMsg.printMsg("criteria=%s" %criteria['deltapercentage_limit'][3])
         for key in table:
            if (table[key]['deltapercentage'] > criteria['deltapercentage_limit'][3] or table[key]['deltapercentage'] == None) and abs(key[3]) != 1:
               failed = True
               failtrack.append(key)
               break
         if failed:
            if testSwitch.auditTest ==0:
               failhead = self.reportFailInfo(failtrack,table,testType)
               ScrCmds.raiseException(14861, "T0%d %s STE delta percentage failed @ Head : %s" % (testNo, berType, str(failhead)))
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s delta percentage failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)



   def checkAtiSteCriteria_FMBW(self, berType, criteria, table, testType='erasure', testNo=51):
      #=== Print ATI criteria
      ScriptComment("\nD0%d_%s_CRITERIA:" %(testNo, berType), writeTimestamp=0)
      ScriptComment("%s%25s"%('NAME','VALUE'), writeTimestamp=0)
      criteriaList = ['baseline_limit','erasure_limit','delta_limit','deltapercentage_limit']
      for n in criteriaList:
         if criteria[n][0]:
            ScriptComment ("ATI_%-21s%9.2f" %(n,criteria[n][1]), writeTimestamp=0)
         if criteria[n][2]:
            ScriptComment ("STE_%-21s%9.2f" %(n,criteria[n][3]), writeTimestamp=0)
      ScriptComment("", writeTimestamp=0)
      if testSwitch.DB_0275227_480505_WRITE_SCRN_MONITORING_ONLY:
         return

      #=== Check baseline limit
      failed = False
      if criteria['baseline_limit'][0]: # if ATI criterion is enabled
         for key in table:
            if table[key]['baseline'] < criteria['baseline_limit'][1] and abs(key[3]) == 1:
               failed = True
               break
         if failed:
            if testSwitch.auditTest ==0:
               objMsg.printMsg("FMBW process ATI baseline failed.......................................................")
               self.dut.AutoWF_PRE2 = 1
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s baseline failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      failed = False
      if criteria['baseline_limit'][2]: # if STE criterion is enabled
         for key in table:
            if table[key]['baseline'] < criteria['baseline_limit'][3] and abs(key[3]) != 1:
               failed = True
               break
         if failed:
            if testSwitch.auditTest ==0:
               objMsg.printMsg("FMBW process STE baseline failed.......................................................")
               self.dut.AutoWF_PRE2 = 1
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s baseline failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      #=== Check erasure limit
      failed = False
      if criteria['erasure_limit'][0]: # if ATI criterion is enabled
         for key in table:
            if testType in table[key]:
               if (table[key][testType] < criteria['erasure_limit'][1] or table[key][testType] == None) and abs(key[3]) == 1:
                  failed = True
                  break
         if failed:
            if testSwitch.auditTest ==0:
               objMsg.printMsg("FMBW process ATI erasure failed.......................................................")
               self.dut.AutoWF_PRE2 = 1
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s erasure failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      failed = False
      if criteria['erasure_limit'][2]: # if STE criterion is enabled
         for key in table:
            if testType in table[key]:
               if (table[key][testType] < criteria['erasure_limit'][3] or table[key][testType] == None) and abs(key[3]) != 1:
                  failed = True
                  break
         if failed:
            if testSwitch.auditTest ==0:
               objMsg.printMsg("FMBW process STE erasure failed.......................................................")
               self.dut.AutoWF_PRE2 = 1
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s erasure failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      #=== Check delta limit
      failed = False
      if criteria['delta_limit'][0]:  # if ATI criterion is enabled
         for key in table:
            if (table[key]['delta'] > criteria['delta_limit'][1] or table[key]['delta'] == None) and  abs(key[3]) == 1:
               failed = True
               break
         if failed:
            if testSwitch.auditTest ==0:
               objMsg.printMsg("FMBW process ATI delta failed.......................................................")
               self.dut.AutoWF_PRE2 = 1
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s delta failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      failed = False
      if criteria['delta_limit'][2]: # if STE criterion is enabled
         for key in table:
            if (table[key]['delta'] > criteria['delta_limit'][3] or table[key]['delta'] == None) and  abs(key[3]) != 1:
               failed = True
               break
         if failed:
            if testSwitch.auditTest ==0:
               objMsg.printMsg("FMBW process STE delta failed.......................................................")
               self.dut.AutoWF_PRE2 = 1
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s delta failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      #=== Check delta percentage limit
      failed = False
      if criteria['deltapercentage_limit'][0]:  # if ATI criterion is enabled
         for key in table:
            if (table[key]['deltapercentage'] > criteria['deltapercentage_limit'][1] or table[key]['deltapercentage'] == None) and abs(key[3]) == 1:
               failed = True
               break
         if failed:
            if testSwitch.auditTest ==0:
               objMsg.printMsg("FMBW process ATI delta percentage failed.......................................................")
               self.dut.AutoWF_PRE2 = 1
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s delta percentage failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

      failed = False
      if criteria['deltapercentage_limit'][2]: # if STE criterion is enabled
         for key in table:
            if (table[key]['deltapercentage'] > criteria['deltapercentage_limit'][3] or table[key]['deltapercentage'] == None) and abs(key[3]) != 1:
               failed = True
               break
         if failed:
            if testSwitch.auditTest ==0:
               objMsg.printMsg("FMBW process STE delta percentag failed.......................................................")
               self.dut.AutoWF_PRE2 = 1
            elif testSwitch.auditTest ==1:
               objMsg.printMsg("AUDIT TEST:T0%d %s delta percentage failed...CONTINUE" % (testNo, berType),objMsg.CMessLvl.IMPORTANT)

   def createFailHDTable(self, headFailList):
      for x in range(0, len(headFailList)):
         hd = headFailList[x]
         self.dut.dblData.Tables('P_ERROR_RATE_STATUS').addRecord({
            'SPC_ID'              : 1, #self.dut.objSeq.curRegSPCID,
            'OCCURRENCE'          : self.dut.objSeq.getOccurrence(),
            'SEQ'                 : self.dut.objSeq.curSeq,
            'TEST_SEQ_EVENT'      : self.dut.objSeq.getTestSeqEvent(0),
            'HD_PHYS_PSN'         : hd,  # hd
            'HD_STATUS'           : str(10632),
         })
      if len(headFailList) > 0:
         objMsg.printMsg("self.dut.objSeq.curRegSPCID %s"  %(str(self.dut.objSeq.curRegSPCID)))
         objMsg.printDblogBin(self.dut.dblData.Tables('P_ERROR_RATE_STATUS'))
   
   def runT250(self, qserPrm, testZoneList=[]):
      ecAr = []
      MaskList = self.oUtility.convertListToZoneBankMasks(testZoneList)
      for bank, list in MaskList.iteritems():
         if list:
            qserPrm ['ZONE_MASK_EXT'], qserPrm ['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(list)
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT: 
               qserPrm ['ZONE_MASK_BANK'] = bank
            try: stats = self.St(qserPrm)
            except  ScriptTestFailure, (failureData):
               if failureData[0][2] not in ecAr:
                   ecAr.append(failureData[0][2])
      return ecAr

######
   def quickSymbolErrorRate(self, inPrm,flawListMask=0,spc_id=1,numRetries=0,spc_id_override=None,step_retry = 10,num_trk_after_fail=None,zapOTF=0,failchk=0):
      """
      Uses test 250 to extract SER data by zone by head.
      FAILING metric is the 0th item in the 'MODES' list
      READ_SCRN 1-->before flawscan SER,call the test with SPC_ID = 1, and set numRetries...any failure invokes retries
      READ_SCRN2-->after flawscan SER, use SPC_ID = 2 and also set numRetries, and set CWORD1 for scanflawlist option if desired
      optional:specify HD_PHYS_PSN for non zero Num_Violations, and/or SPC_ID in GOTF_table.xml.
      parms are here:prm_quickSER_250
      OUTPUT: THE FINAL TABLE FOR GRADING IS P_QUICK_ERR_RATE
      """
      qserPrm = inPrm.copy()

      #if type(qserPrm['CWORD1']) in [types.TupleType, types.ListType]:
      #   qserPrm['CWORD1'] = qserPrm['CWORD1'][0]

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      if testSwitch.auditTest:
         prm_auditTest_T250={'prm_name'    : "prm_auditTest_T250",
            'NUM_TRACKS_PER_ZONE' : 10,
            'ZONE_POSITION': 199, # bias further towards ID to make room for retries
            'RETRIES': 4,
            'SKIP_TRACK':10,}
         prm_auditTest_T250.update(getattr(TP, 'prm_auditTest_T250',{})) #make changes by program in testparameters.py
         qserPrm.update( prm_auditTest_T250)
         if spc_id == 1:
            flawListMask=0x100 # bit 8 limits num tracks to NUM_TRACKS_PER_ZONE
         objMsg.printMsg("AUDIT TEST: quickSymbolErrorRate- adjusting parms...copy prm_auditTest_T250 to TP file and modify if desired",objMsg.CMessLvl.IMPORTANT)
      writeMask = 1
      modes = qserPrm.pop('MODES',['SYMBOL'])
      numZones = len(qserPrm['TEST_ZONES'])
      testZoneList = qserPrm['TEST_ZONES']
      del qserPrm['TEST_ZONES'] #remove test zones
      startingZonePosn = qserPrm['ZONE_POSITION']
      rawBERLimit = qserPrm.pop('SER_raw_BER_limit')
      numFailedZonesLimit = qserPrm.pop('SER_num_failing_zones_rtry')

      fail_mode = modes[0]

      del qserPrm['checkDeltaBER_num_failing_zones']
      del qserPrm['max_diff']
      maxIterationLevels = qserPrm.pop('MAX_ITERATION',[-1,]*len(modes))
      minSpec = qserPrm['MINIMUM']

      SERCallIndex = 0
      if spc_id >= 2:
         if testSwitch.virtualRun:
            fullTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()

            for tableRows in xrange(len(fullTable)):
               
               if int(fullTable[tableRows]['SPC_ID']) < spc_id:
                  SERCallIndex +=1
         else: # normal operation
            try: SERCallIndex = len(self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj())
            except: pass

      for index,mode in enumerate(modes):

         if mode == 'SECTOR':
            modeMask = 0x4
         elif mode == 'SYMBOL':
            modeMask = 0#0xFFFB
         elif mode == 'SOVA':
            modeMask = 0x20
         elif mode == 'BITERR':
            modeMask = 0x800 #0x2 (not used) -> compensate the unconverging code word with equation; 0x800 -> compensate the unconverging codeword with eq. 1000 bits for one unconvergin codeword.
         else:
            modeMask = 0
         #check maxIterationLevels is list or scalar value
         if (type(maxIterationLevels) == type([]) and maxIterationLevels[index] > -1) or (maxIterationLevels> -1):
            if type(maxIterationLevels) == type([]):
               qserPrm['MAX_ITERATION'] = maxIterationLevels[index]
            else: qserPrm['MAX_ITERATION'] = maxIterationLevels
         else:
            qserPrm.pop('MAX_ITERATION',None)

         if flawListMask & 0x40 == 0x40:
            scanFlawList = 1 #if bit 6 is set, handle things differently
         else:
            scanFlawList = 0

         #if this isn't the metric for failure then lets make the spc_id invalid for the comparison.
         if mode == fail_mode:
            qserPrm['spc_id'] = spc_id
            qserPrm['MINIMUM'] = minSpec
         else:
            qserPrm['spc_id'] = spc_id + index + 1000
            qserPrm['MINIMUM'] = 0
            
         if self.dut.nextState in ['READ_SCRN2', 'SQZ_WRITE'] and testSwitch.SKIPZONE:
            qserPrm['MINIMUM'] = 0    # do not fail when auto dezone turn on
            
         if spc_id_override:
            qserPrm['spc_id'] = spc_id_override
         if 'NUM_SQZ_WRITES' in qserPrm and qserPrm['NUM_SQZ_WRITES']>0: #squeeze write
            adjacentWriteMask = 0x4000
         else:
            adjacentWriteMask = 0
         
         qserPrm['CWORD1'] = 0 | modeMask | writeMask | flawListMask | 0x180 | adjacentWriteMask #0x2 is the sample mode mask

         if zapOTF == 1:
            if type(qserPrm['CWORD1']) in [types.ListType,types.TupleType]:
               qserPrm['CWORD1'] = qserPrm['CWORD1'][0]
            qserPrm['CWORD1'] |= 0x8000
            qserPrm['TRACK_LIMIT'] = 0
            qserPrm['timeout'] = 5000 * self.dut.imaxHead
         
         ecAr = self.runT250(qserPrm, testZoneList)

### error code handling
         for ec in ecAr: #loop over ec
            if spc_id >= 2:
               if not scanFlawList:# since not checking the P-list etc, lets not fail the St() call
                  objMsg.printMsg('%s alt cyls retries should be invoked' \
                     % ("quickSymbolErrorRate: fatal errors during READ_SCRN2 T250 calls(no scanflawlist),"), objMsg.CMessLvl.IMPORTANT)
                  break
               if testSwitch.ENABLE_THERMAL_SHOCK_RECOVERY_V2 and failchk and ec in TP.RdScrn2_Retry_with_TSR['EC_Trigger']:
                     pass  # let calling routine handle the error
               elif ec == 10632:
                  headFailList = []
                  fullTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match',spc_id)
                  if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and spc_id == 2:
                     origPartNum = self.dut.partNum
                     for i in xrange(5):
                        if CState(self.dut).downGradeOnFly(1,ec) :
                           headFailList = []
                           objMsg.printMsg('%s SER_raw_BER_limit: %s' %(self.dut.CAPACITY_CUS, TP.prm_quickSER_250['SER_raw_BER_limit']))
                           for tableRows in xrange(len(fullTable)):
                              if int(fullTable[tableRows]['FAIL_CODE']) == ec :
                                 if float(fullTable[tableRows]['RAW_ERROR_RATE']) > TP.prm_quickSER_250['SER_raw_BER_limit']:
                                    if int(fullTable[tableRows]['HD_LGC_PSN']) not in headFailList:
                                       headFailList.append(int(fullTable[tableRows]['HD_LGC_PSN']))
                           objMsg.printMsg('headFailList: %s' %(headFailList))
                           if len(headFailList)== 0: break
                     if not len(headFailList)== 0 or origPartNum == self.dut.partNum :
                        self.createFailHDTable(headFailList)
                        ScrCmds.raiseException(ec, "Failed T250 in %s" % (self.dut.nextState))
                     else: pass
                  else:
                     for tableRows in xrange(len(fullTable)):
                        if int(fullTable[tableRows]['FAIL_CODE']) == 10632:
                           if int(fullTable[tableRows]['HD_LGC_PSN']) not in headFailList:
                              headFailList.append(int(fullTable[tableRows]['HD_LGC_PSN']))
                     self.createFailHDTable(headFailList)
                     ScrCmds.raiseException(ec, "Failed T250 in %s" % (self.dut.nextState))
               elif ec == 10482:
                  objMsg.printMsg("quickSymbolErrorRate: 'too many flaws' in %s --> ec = %s, alt cyls retries should be invoked" \
                     % (self.dut.nextState, ec), objMsg.CMessLvl.IMPORTANT)
               else:
                  ScrCmds.raiseException(ec, "Failed T250 in %s" % (self.dut.nextState))
            elif spc_id == 1:
               objMsg.printMsg('%s alt cyls retries should be invoked' \
                  % ('quickSymbolErrorRate: fatal errors during READ_SCRN 1 T250 calls, '), objMsg.CMessLvl.IMPORTANT)
               break
### end of error code handling
         
         if spc_id == 1 and 'S' in StateTable[self.dut.nextOper][self.dut.nextState][OPT]:
            writeMask = 0
            return

         if testSwitch.FE_0125530_399481_T250_RETRY_TO_IGNORE_BANDS_WITH_P_LIST_ENTRIES:
            T250_Retryparams = getattr(TP, 'T250_Retryparams',{})
            qserPrm['CWORD1'] = qserPrm['CWORD1'] & T250_Retryparams.get("CWORD1_mask", 0xFFBF)
            startingZonePosn = T250_Retryparams.get("startingZonePosn", 151)
            scanFlawList = T250_Retryparams.get("scanFlawList", 0)

         symbolData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match', spc_id)
         retryZoneListbyHead = [ [] for i in range(self.dut.imaxHead) ]
########### data loop
         for record in symbolData:
            head = int(record['HD_LGC_PSN'])
            zone = int(record['DATA_ZONE'])
            if scanFlawList:#if bit 6 is set, only retry on 10482 EC
               # only fail for 10482 "too many flaws"
               ec = int(record['FAIL_CODE'])
               if ec in [10482]:
                  objMsg.printMsg("quickSymbolErrorRate: failed T250 for 'too many flaws' in %s, head= %s, zone= %s FAIL_CODE = %s" \
                     % (self.dut.nextState, head, zone, ec))
                  retryZoneListbyHead[head].append(zone)
            else: # since not checking the P-list etc, retry on anything
               rawBer = float(record['RAW_ERROR_RATE'])
               if rawBer > float(rawBERLimit):
                  objMsg.printMsg("quickSymbolErrorRate: failing BER in %s (no scanflawlist), head= %s, zone= %s BER = %s, limit= %s" \
                     % (self.dut.nextState, head, zone, rawBer, rawBERLimit))
                  retryZoneListbyHead[head].append(zone)
########### head loop
         for head in xrange(self.dut.imaxHead):
            tableRetryStartIndex = len(symbolData)
            retryZoneList = retryZoneListbyHead[head]
            # objMsg.printMsg("H%d: retryZoneList = %s" % (head, retryZoneList))
            if len(retryZoneList) > numFailedZonesLimit:
               objMsg.printMsg("quickSymbolErrorRate: failing zones = %d, exceeds the numFailedZonesLimit = %s, skipping retries for head %d" \
                  % (len(retryZoneList), numFailedZonesLimit, head), objMsg.CMessLvl.IMPORTANT)
               continue
            if len(retryZoneList):
               objMsg.printMsg("quickSymbolErrorRate: entering RETRY BLOCK.. the starting retryZoneList for head %s is %s " \
                  % (head, retryZoneList), objMsg.CMessLvl.IMPORTANT)
               zonePosn = startingZonePosn
################ retry loop
               if testSwitch.auditTest:
                  mword = {}
                  mword['CWORD1'] = qserPrm['CWORD1']
                  if type(mword['CWORD1']) == types.TupleType:
                     mword['CWORD1'] = mword['CWORD1'][0]
                  mword['CWORD1'] = mword['CWORD1'] & 0xFFBF # mask out bit 6 -do not scanflawlist for retries
                  qserPrm.update({'CWORD1': mword['CWORD1'] })
                  scanFlawList = 0
                  numRetries = 3 # no scanflawlist, so give three PF3 retries
                  objMsg.printMsg("AUDIT TEST: quickSymbolErrorRate- retry loop-adjusting parms...do not scanflawlist,give 2 retries", objMsg.CMessLvl.IMPORTANT)
               retryIndexer = 0
               if (testSwitch.FE_0163943_470833_P_T250_ADD_RETRY_NO_FLAWLIST_SCAN and spc_id >= 2):
                  retryLoopRange = xrange(1, numRetries+2) # add an additional retry
               else:
                  retryLoopRange = xrange(1, numRetries+1)
               for retry in retryLoopRange:
                  zRtyList = retryZoneList
                  if (testSwitch.FE_0163943_470833_P_T250_ADD_RETRY_NO_FLAWLIST_SCAN and retry == (numRetries+1) and spc_id >= 2):
                     qserPrm.update({'CWORD1': (qserPrm['CWORD1'] & 0xFFBF) }) # mask out bit 6 - do not scan flawlist for this retry
                     scanFlawList = 0
                     objMsg.printMsg("quickSymbolErrorRate- additional retry without flawlist scan", objMsg.CMessLvl.IMPORTANT)
                  if testSwitch.virtualRun:
                     tableRetryStartIndex = 0
                  objMsg.printMsg("quickSymbolErrorRate RETRY LOOP: NOTE:pre flawscan call can retry for any T250 failure or low BER, post flawscan call will only retry for 10482 ec in T250(unless bit 6 not set)", objMsg.CMessLvl.VERBOSEDEBUG)
                  objMsg.printMsg("quickSymbolErrorRate RETRY LOOP: the retry num is %s ,the zones to be re-measured are %s" % (retry,zRtyList), objMsg.CMessLvl.IMPORTANT)
                  qserPrm['TEST_HEAD'] = ((head << 8) + head)# blm it s/b a head mask for sampled BER
                  if testSwitch.FE_0124358_391186_T250_ZONE_SWEEP_RETRIES:
                     if num_trk_after_fail != None:
                        qserPrm['NUM_TRACKS_PER_ZONE'] = num_trk_after_fail
                  if testSwitch.auditTest==0:
                     if testSwitch.FE_0124358_391186_T250_ZONE_SWEEP_RETRIES:
                        qserPrm['ZONE_POSITION'] = zonePosn-(step_retry*retry)
                     else:
                        qserPrm['ZONE_POSITION'] = zonePosn-(10*retry)

                  elif testSwitch.auditTest==1:
                     qserPrm['ZONE_POSITION'] = zonePosn-(50*retry)#scale the zone pos for small audit bands
                  ecAr = self.runT250(qserPrm, zRtyList)
                  for ec in ecAr:
                     if spc_id == 1: #read_scrn fail safe
                        objMsg.printMsg('%s ..continue with retries' \
                           % ('quickSymbolErrorRate RETRY LOOP : fatal errors during alt cyls T250 call in READ_SCRN 1'), objMsg.CMessLvl.IMPORTANT)
                        break
                     else:
                        if scanFlawList:
                           if ec == 10482:
                              objMsg.printMsg("quickSymbolErrorRate RETRY LOOP: 'too many flaws' in %s...continue with retries" \
                                 % (self.dut.nextState), objMsg.CMessLvl.IMPORTANT)
                           else:
                              ScrCmds.raiseException(ec, "Failed T250 in %s" % (self.dut.nextState))
                        else:
                           if ec == 10482:
                              objMsg.printMsg('quickSymbolErrorRate RETRY LOOP : fatal errors during alt cyls T250 call (no scanflawlist) in %s..continue with retries' \
                                 % (self.dut.nextState), objMsg.CMessLvl.IMPORTANT)
                           else:
                              ScrCmds.raiseException(ec, "Failed T250 in %s" % (self.dut.nextState))

                  symbolData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match', spc_id)
                  retryZoneList = []

                  if testSwitch.BF_0126008_7955_FIX_T250_ZONE_RETRY_LOOP:
                     for z in xrange(len(zRtyList)):
                        if spc_id >= 2:
                           if scanFlawList:
                              if (symbolData[tableRetryStartIndex + z]['FAIL_CODE']) == '10482': # only fail for 10482 "too many flaws"
                                 objMsg.printMsg("quickSymbolErrorRate RETRY LOOP: failed T250 for 'too many flaws' in %s, head= %s, zone= %s, zone posn(ticks)=%s, FAIL_CODE = %s" \
                                    % (self.dut.nextState, head, zRtyList[z], qserPrm['ZONE_POSITION'], symbolData[tableRetryStartIndex + z]['FAIL_CODE']), objMsg.CMessLvl.IMPORTANT)
                                 retryZoneList.append(int(symbolData[tableRetryStartIndex + z]['DATA_ZONE']))
                           else:
                              if float(symbolData[tableRetryStartIndex + z]['RAW_ERROR_RATE']) > float(rawBERLimit):
                                 objMsg.printMsg("quickSymbolErrorRate RETRY LOOP %s (no scanflawlist): failing BER, head= %s, zone= %s, zone posn(ticks)=%s, BER = %s, limit= %s" \
                                    % (self.dut.nextState, head, zRtyList[z], qserPrm['ZONE_POSITION'], symbolData[tableRetryStartIndex + z]['RAW_ERROR_RATE'], rawBERLimit), objMsg.CMessLvl.IMPORTANT)
                                 retryZoneList.append(int(symbolData[tableRetryStartIndex + z]['DATA_ZONE']))
                        elif spc_id ==1:
                           if float(symbolData[tableRetryStartIndex + z]['RAW_ERROR_RATE']) > float(rawBERLimit):
                              objMsg.printMsg("quickSymbolErrorRate RETRY LOOP READ_SCRN 1: failing BER, head= %s, zone= %s, zone posn(ticks)=%s, BER = %s, limit= %s" \
                                 % (head, zRtyList[z], qserPrm['ZONE_POSITION'], symbolData[tableRetryStartIndex + z]['RAW_ERROR_RATE'], rawBERLimit), objMsg.CMessLvl.IMPORTANT)
                              retryZoneList.append(int(symbolData[tableRetryStartIndex + z]['DATA_ZONE']))
                  else:
                     for z in xrange(len(zRtyList)):
                        if scanFlawList:
                           if (symbolData[tableRetryStartIndex + z + retryIndexer]['FAIL_CODE']) == '10482': # only fail for 10482 "too many flaws"
                              objMsg.printMsg("quickSymbolErrorRate RETRY LOOP: failed T250 for 'too many flaws' in %s, head= %s, zone= %s, zone posn(ticks)=%s, FAIL_CODE = %s" \
                                 % (self.dut.nextState, head, zRtyList[z], qserPrm['ZONE_POSITION'], symbolData[tableRetryStartIndex + z + retryIndexer]['FAIL_CODE']), objMsg.CMessLvl.IMPORTANT)
                              retryZoneList.append(int(symbolData[tableRetryStartIndex + z + retryIndexer]['DATA_ZONE']))
                        else:
                           if float(symbolData[tableRetryStartIndex + z + retryIndexer ]['RAW_ERROR_RATE']) > float(rawBERLimit):
                              objMsg.printMsg("quickSymbolErrorRate RETRY LOOP %s (no scanflawlist): failing BER, head= %s, zone= %s, zone posn(ticks)=%s, BER = %s, limit= %s" \
                                 % (self.dut.nextState, head, zRtyList[z], qserPrm['ZONE_POSITION'], symbolData[tableRetryStartIndex + z + retryIndexer]['RAW_ERROR_RATE'], rawBERLimit), objMsg.CMessLvl.IMPORTANT)
                              retryZoneList.append(int(symbolData[tableRetryStartIndex + z + retryIndexer]['DATA_ZONE']))
                     retryIndexer += (z+1)

                  if len(retryZoneList)==0:
                     objMsg.printMsg('quickSymbolErrorRate RETRY LOOP : the head appears to have passed-->break out of retry loop ',objMsg.CMessLvl.VERBOSEDEBUG)
                     break
                  if retry == numRetries:
                     objMsg.printMsg('quickSymbolErrorRate RETRY LOOP : end of retry loop because %s retries exhausted for this head '%(numRetries),objMsg.CMessLvl.VERBOSEDEBUG)
	#################
         #We don't need to re-write the tracks
         writeMask = 0

      if spc_id ==2:# grab only the second call data(for the fail_mode), then extract only the best BER for each hd/zone combo in prep for the P_QUICK_ERR_RATE table update
         if testSwitch.virtualRun:
            spc_id = str(spc_id)
         P250spc_id2Table = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match',spc_id)
         P250spc_id2FailModeTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('ERROR_RATE_TYPE', 'match',fail_mode,tbl = P250spc_id2Table)
         ##For SECTOR Mode
         if testSwitch.BF_0162624_409401_P_CHOP_P250_ERROR_RATE_BY_ZONE_WITH_SECTOR_VALUE_SPCID_2:
            SectorFlag = 0
            P250_ERROR_RATE = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
            for i in range(len(P250_ERROR_RATE)):
               if str(P250_ERROR_RATE[i]['ERROR_RATE_TYPE']) == "SECTOR":
                  SectorFlag = 1
            if SectorFlag:
               P250FailModeTable_SECTOR = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('ERROR_RATE_TYPE', 'match','SECTOR')
               for i in range(len(P250FailModeTable_SECTOR)):
                  P250spc_id2FailModeTable.append(P250FailModeTable_SECTOR[i])
         P250choppedTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLogLoop(testZoneList,colParse='RAW_ERROR_RATE',ColMatchStyle='min',tableName=P250spc_id2FailModeTable)
      elif spc_id ==1:# extract only the best BER for each hd/zone combo in prep,(for the fail_mode) for the P_QUICK_ERR_RATE table update
         if testSwitch.virtualRun: # for VE, we need to first extract spc_id =1 data
            spc_id = str(spc_id)
            VEP250spc_id1Table = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match',spc_id)
            P250FailModeTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('ERROR_RATE_TYPE', 'match',fail_mode,tbl = VEP250spc_id1Table)
         else: #normal path
            P250FailModeTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('ERROR_RATE_TYPE', 'match',fail_mode)
            ##For SECTOR Mode
            if testSwitch.FE_0153218_420281_P_CHOP_P250_ERROR_RATE_BY_ZONE_WITH_SECTOR_VALUE:
               SectorFlag = 0
               P250_ERROR_RATE = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
               for i in range(len(P250_ERROR_RATE)):
                  if str(P250_ERROR_RATE[i]['ERROR_RATE_TYPE']) == "SECTOR":
                     SectorFlag = 1
               if SectorFlag:
                  P250FailModeTable_SECTOR = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('ERROR_RATE_TYPE', 'match','SECTOR')
                  for i in range(len(P250FailModeTable_SECTOR)):
                     P250FailModeTable.append(P250FailModeTable_SECTOR[i])
         P250choppedTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLogLoop(testZoneList,colParse='RAW_ERROR_RATE',ColMatchStyle='min',tableName=P250FailModeTable)
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(250,spc_id)

      if type(spc_id) == str:
         spc_id = int(spc_id)

      if spc_id in [1, 2]:
         for data in xrange(len(P250choppedTable)):
            baseUpdate = {
            'HD_PHYS_PSN': P250choppedTable[data].get('HD_PHYS_PSN'),
            'TRK_NUM': P250choppedTable[data].get('START_TRK_NUM'),
            'SPC_ID': P250choppedTable[data].get('SPC_ID'),
            'OCCURRENCE': occurrence,
            'SEQ':curSeq,
            'TEST_SEQ_EVENT': testSeqEvent,
            'HD_LGC_PSN': P250choppedTable[data].get('HD_LGC_PSN'),
            'RBIT':self.oUtility.setDBPrecision((P250choppedTable[data].get('BITS_READ_LOG10')),4,2),
            'RRAW':self.oUtility.setDBPrecision((P250choppedTable[data].get('RAW_ERROR_RATE')),4,2), #leave sign negative
            'OTF':'', #null for now
            'HARD':'', #null for now
            'DATA_ZONE':P250choppedTable[data].get('DATA_ZONE'),
            }
            self.dut.dblData.Tables('P_QUICK_ERR_RATE').addRecord(baseUpdate)

      if spc_id ==1:
         objMsg.printMsg("quickSymbolErrorRate(first call,spc_id =1): saving P_QUICK_ERR_RATE table to marshall object ", objMsg.CMessLvl.VERBOSEDEBUG)
         self.dut.objData.update({'P_QUICK_ERR_RATE':self.dut.dblData.Tables('P_QUICK_ERR_RATE').tableDataObj()})

      if spc_id == 2 and (testSwitch.FE_0140444_336764_P_KOR_BER_SPEC_FOR_ORT or (testSwitch.FE_0164651_426568_P_DELTA_BER_MEAN_BY_HEAD and self.dut.nextState in ['READ_SCRN2'] )):
         P250_tbl = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
         if testSwitch.FE_0149136_409401_P_DELTA_BER_IMPROVEMENT:
            P250_tbl = self.dut.dblData.Tables('P_QUICK_ERR_RATE').tableDataObj()
         if (testSwitch.BF_0144381_336764_KEEP_LATEST_BER_IF_RE_TEST_PERFORM or testSwitch.FE_0164651_426568_P_DELTA_BER_MEAN_BY_HEAD):
            BER_spcid1 = {}
            BER_spcid2 = {}
            if testSwitch.BF_0172780_470833_P_USE_LGC_HD_INSTEAD_OF_PHYS_T250:
               head_psn_string = 'HD_LGC_PSN'
            else:
               head_psn_string = 'HD_PHYS_PSN'
            for hd in range(self.dut.imaxHead):
               BER_spcid1['Hd'+str(hd)] = {}
               BER_spcid2['Hd'+str(hd)] = {}
               for zone in range(self.dut.numZones):
                  if not testSwitch.FE_0149136_409401_P_DELTA_BER_IMPROVEMENT:
                     BER_spcid1['Hd'+str(hd)]['Zn'+str(zone)] = [float(P250_tbl[i]['RAW_ERROR_RATE']) for i in range(len(P250_tbl)) if int(P250_tbl[i]['SPC_ID']) == 1 and (int(P250_tbl[i][head_psn_string]) == hd) and (int(P250_tbl[i]['DATA_ZONE']) == zone)][-1]
                     BER_spcid2['Hd'+str(hd)]['Zn'+str(zone)] = [float(P250_tbl[i]['RAW_ERROR_RATE']) for i in range(len(P250_tbl)) if int(P250_tbl[i]['SPC_ID']) == 2 and (int(P250_tbl[i][head_psn_string]) == hd) and (int(P250_tbl[i]['DATA_ZONE']) == zone)][-1]
                  else:
                     BER_spcid1['Hd'+str(hd)]['Zn'+str(zone)] = [float(P250_tbl[i]['RRAW']) for i in range(len(P250_tbl)) if int(P250_tbl[i]['SPC_ID']) == 1 and (int(P250_tbl[i][head_psn_string]) == hd) and (int(P250_tbl[i]['DATA_ZONE']) == zone)][-1]
                     BER_spcid2['Hd'+str(hd)]['Zn'+str(zone)] = [float(P250_tbl[i]['RRAW']) for i in range(len(P250_tbl)) if int(P250_tbl[i]['SPC_ID']) == 2 and (int(P250_tbl[i][head_psn_string]) == hd) and (int(P250_tbl[i]['DATA_ZONE']) == zone)][-1]

               if testSwitch.FE_0164651_426568_P_DELTA_BER_MEAN_BY_HEAD:
                  #Fail drive if mean of delta BER by head > set value
                  meanDeltaBERLimitbyHead = getattr(TP,'meanDeltaBERLimitbyHead',-0.29)
                  delta_BER = []
                  if len(BER_spcid1['Hd'+str(hd)]) == len(BER_spcid2['Hd'+str(hd)]):
                     for i in range(len(BER_spcid1['Hd'+str(hd)])):
                        if BER_spcid2['Hd'+str(hd)]['Zn'+str(i)] < 0 and BER_spcid1['Hd'+str(hd)]['Zn'+str(i)] < 0 :
                           delta_BER.append(BER_spcid1['Hd'+str(hd)]['Zn'+str(i)]-BER_spcid2['Hd'+str(hd)]['Zn'+str(i)])
                     objMsg.printMsg("Mean of Delta BER limit for head %s is % s" % (str(hd), str(MathLib.mean(delta_BER))))
                     if MathLib.mean(delta_BER) <= meanDeltaBERLimitbyHead:
                        objMsg.printMsg("Mean of Delta BER limit exceeded for head %s" % hd)
                        ScrCmds.raiseException(14574, "Mean of Delta BER limit exceeded for head %s" % hd)
                  else:
                     objMsg.printMsg("Lenght between SPC_ID1 and SPC_ID2 not equal")
                     ScrCmds.raiseException(14574, "Length between SPC_ID1 and SPC_ID2 not equal")
            P250_BER_spcid1 = [BER_spcid1['Hd'+str(hd)]['Zn'+str(zone)] for hd in range(self.dut.imaxHead) for zone in range(self.dut.numZones)]
            P250_BER_spcid2 = [BER_spcid2['Hd'+str(hd)]['Zn'+str(zone)] for hd in range(self.dut.imaxHead) for zone in range(self.dut.numZones)]
         else:
            if not testSwitch.FE_0149136_409401_P_DELTA_BER_IMPROVEMENT:
               P250_BER_spcid1 = [float(P250_tbl[i]['RAW_ERROR_RATE']) for i in range(len(P250_tbl)) if int(P250_tbl[i]['SPC_ID']) == 1 ]
               P250_BER_spcid2 = [float(P250_tbl[i]['RAW_ERROR_RATE']) for i in range(len(P250_tbl)) if int(P250_tbl[i]['SPC_ID']) == 2 ]
            else:
               P250_BER_spcid1 = [float(P250_tbl[i]['RRAW']) for i in range(len(P250_tbl)) if int(P250_tbl[i]['SPC_ID']) == 1 ]
               P250_BER_spcid2 = [float(P250_tbl[i]['RRAW']) for i in range(len(P250_tbl)) if int(P250_tbl[i]['SPC_ID']) == 2 ]
         if testSwitch.FE_0164651_426568_P_DELTA_BER_MEAN_BY_HEAD:
            objMsg.printMsg("Passed Mean Delta BER Compare By Head")
         else:
            objMsg.printMsg("Por Print table")
            objMsg.printMsg(P250_tbl)
            objMsg.printMsg('BER_spcid1 = %s'% BER_spcid1)
            objMsg.printMsg('BER_spcid2 = %s'% BER_spcid2)
            objMsg.printMsg('P250_BER_spcid1 = %s'% P250_BER_spcid1)
            objMsg.printMsg('P250_BER_spcid2 = %s'% P250_BER_spcid2)
            delta_BER = []
            flag_mDelta = 0
            flag_mBER = 0

            #Fail drive if mean of delta BER >0.42
            meanDeltaBERLimit = getattr(TP,'meanDeltaBERLimit',0.46)
            if len(P250_BER_spcid1) == len(P250_BER_spcid2):
               for i in range(len(P250_BER_spcid1)):
                  delta_BER.append(abs(P250_BER_spcid1[i]-P250_BER_spcid2[i]))
               if MathLib.mean(delta_BER) > meanDeltaBERLimit:
                  objMsg.printMsg("Mean of Delta BER limit exceeded")
                  if testSwitch.FE_0142623_345963_P_CHK_DELTA_AND_BER_IN_SPEC:
                     flag_mDelta = 1
                  else:
                     ScrCmds.raiseException(14575, "Mean of Delta BER limit exceeded")
            else:
               objMsg.printMsg("Lenght between SPC_ID1 and SPC_ID2 not equal")
               ScrCmds.raiseException(14575, "Mean of Delta BER limit exceeded")

            #Fail drive if absolute of mean of BER at SPC_ID 2 < 4.71
            meanBERLimit = getattr(TP,'meanBERLimit',4.71)
            if len(P250_BER_spcid2):
               if MathLib.mean(P250_BER_spcid2) > meanBERLimit:
                  objMsg.printMsg("BER at SPC_ID 2 limit exceeded")
                  if testSwitch.FE_0142623_345963_P_CHK_DELTA_AND_BER_IN_SPEC:
                     flag_mBER = 1
                  else:
                     ScrCmds.raiseException(14575, "Mean of BER limit exceeded")
            else:
               objMsg.printMsg("BER at SPC_ID 2 is not exist")
               ScrCmds.raiseException(14575, "Mean of BER limit exceeded")

            #Fail drive if  mean(abs(deltaBER between spc_id1 and spc_id2)) > 0.42 and mean(abs(BER at spc_id2)) <4.71
            if testSwitch.FE_0142623_345963_P_CHK_DELTA_AND_BER_IN_SPEC:
               if flag_mDelta and flag_mBER:
                  ScrCmds.raiseException(14575, "Mean of Delta BER and Mean of BER limit exceeded")

   def ErrorRateMeasurement(self, inPrm, flawListMask=0,spc_id=1,numRetries=0, retryEC = [10482]):
      """
      Uses test 250 to extract SER data by zone by head.
      FAILING metric is the 0th item in the 'MODES' list
      READ_SCRN 1-->before flawscan SER,call the test with SPC_ID = 1, and set numRetries...any failure invokes retries
      READ_SCRN2-->after flawscan SER, use SPC_ID = 2 and also set numRetries, and set CWORD1 for scanflawlist option if desired
      optional:specify HD_PHYS_PSN for non zero Num_Violations, and/or SPC_ID in GOTF_table.xml.
      parms are here:prm_quickSER_250
      OUTPUT: THE FINAL TABLE FOR GRADING IS P_QUICK_ERR_RATE
      """
      qserPrm = inPrm.copy()

      writeMask = 1
      modes = qserPrm.pop('MODES',['SYMBOL'])
      numZones = len(qserPrm['TEST_ZONES'])
      testZoneList = qserPrm['TEST_ZONES']
      del qserPrm['TEST_ZONES'] #remove test zones
      startingZonePosn = qserPrm['ZONE_POSITION']
      rawBERLimit = qserPrm.pop('SER_raw_BER_limit')
      numFailedZonesLimit = qserPrm.pop('SER_num_failing_zones_rtry', 1)

      fail_mode = modes[0]

      if 'checkDeltaBER_num_failing_zones' in qserPrm:
         del qserPrm['checkDeltaBER_num_failing_zones']
      if 'max_diff' in qserPrm:
         del qserPrm['max_diff']
      maxIterationLevels = qserPrm.pop('MAX_ITERATION',[-1,]*len(modes))
      minSpec = qserPrm['MINIMUM']

      SERCallIndex = 0

      if testSwitch.virtualRun:
         fullTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
         for tableRows in xrange(len(fullTable)):
            if int(fullTable[tableRows]['SPC_ID']) < spc_id:
               SERCallIndex +=1
      else: # normal operation
         try: SERCallIndex = len(self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj())
         except: pass

      for index,mode in enumerate(modes):

         if mode == 'SECTOR':
            if testSwitch.VBAR_SFR_BY_ELT:
               modeMask = 0x04|0x020
            else:
               modeMask = 0x4
         elif mode == 'SYMBOL':
            modeMask = 0#0xFFFB
         elif mode == 'SOVA':
            modeMask = 0x100
         elif mode == 'BITERR':
            modeMask = 0x800 #0x2 (not used)-> compensate the unconverging code word with equation; 0x800 -> compensate the unconverging codeword with eq. 1000 bits for one unconvergin codeword.
         else:
            modeMask = 0

         #check maxIterationLevels is list or scalar value
         if (type(maxIterationLevels) == type([]) and maxIterationLevels[index] > -1) or (maxIterationLevels> -1):
            if type(maxIterationLevels) == type([]):
               qserPrm['MAX_ITERATION'] = maxIterationLevels[index]
            else: qserPrm['MAX_ITERATION'] = maxIterationLevels
         else:
            qserPrm.pop('MAX_ITERATION', None)

         if flawListMask & 0x40 == 0x40: scanFlawList = 1 #if bit 6 is set, handle things differently
         else: scanFlawList = 0

         #if this isn't the metric for failure then lets make the spc_id invalid for the comparison.
         if mode == fail_mode:
            qserPrm['spc_id'] = spc_id
            qserPrm['MINIMUM'] = minSpec
         else:
            qserPrm['spc_id'] = spc_id + index + 1000
            qserPrm['MINIMUM'] = 0

         if 'NUM_SQZ_WRITES' in qserPrm and qserPrm['NUM_SQZ_WRITES']>0: #squeeze write
            adjacentWriteMask = 0x4000
         else:
            adjacentWriteMask = 0

         if testSwitch.WO_T250_NODUMMYREAD_SF374013:
            qserPrm['CWORD1'] = 0 | modeMask | writeMask | flawListMask | adjacentWriteMask | 0x2 #0x2 is the sample mode mask
         else:
            qserPrm['CWORD1'] = 0 | modeMask | writeMask | flawListMask | adjacentWriteMask | 0x180 # T250_BER_WITH_DATA_ERRORS_BY_EQUATION 0x0002 should not be used.

         ecAr = self.runT250(qserPrm, testZoneList) #fail safe
         if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION and ecAr != []: # M10P raise exception
            raise ecAr
         symbolData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match', spc_id)
         retryZoneListbyHead = [ [] for i in range(self.dut.imaxHead) ]
########### data loop
         for record in symbolData:
            head = int(record['HD_LGC_PSN'])
            zone = int(record['DATA_ZONE'])
            if testSwitch.SKIPZONE:
               if (head, zone) in self.dut.skipzn:
                  objMsg.printMsg("head %s zone %s is skip zone, skipped retry" % (head, zone))
                  continue
            if scanFlawList: # if bit 6 is set, onle retry on 10482 EC
               ec = int(record['FAIL_CODE'])
               if ec in retryEC: # only fail for 10482 "too many flaws"
                  objMsg.printMsg("quickSymbolErrorRate: failed T250 for 'too many flaws' in %s, head= %s, zone= %s FAIL_CODE = %s" \
                     % (self.dut.nextState, head, zone, ec))
                  retryZoneListbyHead[head].append(zone)
            else: # since not checking the P-list etc, retry on anything
               rawBer = float(record['RAW_ERROR_RATE'])
               if rawBer > float(rawBERLimit):
                  objMsg.printMsg("quickSymbolErrorRate: failing BER in %s (no scanflawlist), head= %s, zone= %s BER = %s, limit= %s" \
                     % (self.dut.nextState, head, zone, rawBer, rawBERLimit))
                  retryZoneListbyHead[head].append(zone)
########### head retry loop
         # objMsg.printMsg("retryZoneListbyHead = %s" % (retryZoneListbyHead))
         for head in xrange(self.dut.imaxHead):
            tableRetryStartIndex = len(symbolData)
            retryZoneList = retryZoneListbyHead[head]
            if self.dut.nextState in ['READ_SCRN2D'] and head not in self.dut.TccChgByBerHeadList:
                objMsg.printMsg("head:%s no tcc change, so skip readscrn2D, use readscrn2C data" % head)
                continue

            if len(retryZoneList):
               objMsg.printMsg("quickSymbolErrorRate: entering RETRY BLOCK.. the starting retryZoneList for head %s is %s "% (head, retryZoneList), objMsg.CMessLvl.IMPORTANT)
               zonePosn = startingZonePosn
               if testSwitch.auditTest:
                  mword = {}
                  mword['CWORD1'] = qserPrm['CWORD1']
                  if type(mword['CWORD1']) == types.TupleType:
                     mword['CWORD1'] = mword['CWORD1'][0]
                  mword['CWORD1'] = mword['CWORD1'] & 0xFFBF # mask out bit 6 -do not scanflawlist for retries
                  qserPrm.update({'CWORD1': mword['CWORD1'] })
                  scanFlawList = 0
                  numRetries = 3 # no scanflawlist, so give three PF3 retries
                  objMsg.printMsg("AUDIT TEST: quickSymbolErrorRate- retry loop-adjusting parms...do not scanflawlist,give 2 retries",objMsg.CMessLvl.IMPORTANT)
               retryIndexer = 0
################ retry loop
               if (testSwitch.FE_0163943_470833_P_T250_ADD_RETRY_NO_FLAWLIST_SCAN and spc_id >= 2):
                  retryLoopRange = xrange(1, numRetries+2) # add an additional retry
               else:
                  retryLoopRange = xrange(1, numRetries+1)
               for retry in retryLoopRange:
                  zRtyList = retryZoneList
                  if (testSwitch.FE_0163943_470833_P_T250_ADD_RETRY_NO_FLAWLIST_SCAN and retry == (numRetries+1) and spc_id >= 2):
                     qserPrm.update({'CWORD1': (qserPrm['CWORD1'] & 0xFFBF) }) # mask out bit 6 - do not scan flawlist for this retry
                     scanFlawList = 0
                     objMsg.printMsg("quickSymbolErrorRate- additional retry without flawlist scan", objMsg.CMessLvl.IMPORTANT)
                  if testSwitch.virtualRun:
                     tableRetryStartIndex = 0
                  objMsg.printMsg("quickSymbolErrorRate RETRY LOOP: NOTE:pre flawscan call can retry for any T250 failure or low BER, post flawscan call will only retry for 10482 ec in T250(unless bit 6 not set)" ,objMsg.CMessLvl.VERBOSEDEBUG)
                  objMsg.printMsg("quickSymbolErrorRate RETRY LOOP: the retry num is %s ,the zones to be re-measured are %s"% (retry,zRtyList),objMsg.CMessLvl.IMPORTANT)
                  #qserPrm['ZONE_MASK'] = self.oUtility.ReturnTestCylWord(self.oUtility.setZoneMask(zRtyList))
                  qserPrm['TEST_HEAD'] = ((head << 8) + head)# blm it s/b a head mask for sampled BER
                  if testSwitch.auditTest == 0:
                     qserPrm['ZONE_POSITION'] = zonePosn - (10 * retry)
                  elif testSwitch.auditTest == 1:
                     qserPrm['ZONE_POSITION'] = zonePosn - (50 * retry) #scale the zone pos for small audit bands
                  self.runT250(qserPrm, zRtyList)
                  # symbolData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
                  symbolData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match', spc_id)
                  retryZoneList = []
                  # zRtyListNew = []
                  for z in xrange(len(zRtyList)):
                     if scanFlawList:
                        if int(symbolData[tableRetryStartIndex + z + retryIndexer]['FAIL_CODE']) in retryEC : # only fail for 10482 "too many flaws"
                           objMsg.printMsg("quickSymbolErrorRate RETRY LOOP %s: failed T250 for 'too many flaws', head= %s, zone= %s, zone posn(ticks)=%s, FAIL_CODE = %s" \
                              % (self.dut.nextState, head, zRtyList[z], qserPrm['ZONE_POSITION'], symbolData[tableRetryStartIndex + z + retryIndexer]['FAIL_CODE']), objMsg.CMessLvl.IMPORTANT)
                           retryZoneList.append(int(symbolData[tableRetryStartIndex + z + retryIndexer]['DATA_ZONE']))
                     else:
                        if float(symbolData[tableRetryStartIndex + z + retryIndexer ]['RAW_ERROR_RATE']) > float(rawBERLimit):
                           objMsg.printMsg("quickSymbolErrorRate RETRY LOOP %s (no scanflawlist): failing BER, head= %s, zone= %s, zone posn(ticks)=%s, BER = %s, limit= %s" \
                           % (self.dut.nextState, head, zRtyList[z], qserPrm['ZONE_POSITION'], symbolData[tableRetryStartIndex + z + retryIndexer]['RAW_ERROR_RATE'], rawBERLimit), objMsg.CMessLvl.IMPORTANT)
                           retryZoneList.append(int(symbolData[tableRetryStartIndex + z + retryIndexer]['DATA_ZONE']))
                        retryZoneList.append(int(symbolData[tableRetryStartIndex + z + retryIndexer]['DATA_ZONE']))
                  retryIndexer += (z+1)
                  if len(retryZoneList)==0:
                     objMsg.printMsg('quickSymbolErrorRate RETRY LOOP : the head appears to have passed-->break out of retry loop ',objMsg.CMessLvl.VERBOSEDEBUG)
                     break
                  if retry == numRetries:
                     objMsg.printMsg('quickSymbolErrorRate RETRY LOOP : end of retry loop because %s retries exhausted for this head '%(numRetries),objMsg.CMessLvl.VERBOSEDEBUG)
#################
         #We don't need to re-write the tracks
         writeMask = 0

      return


      if testSwitch.virtualRun:spc_id = str(spc_id)
      P250spc_id2Table = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match',spc_id)
      P250spc_id2FailModeTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('ERROR_RATE_TYPE', 'match',fail_mode,tbl = P250spc_id2Table)
      P250choppedTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLogLoop(testZoneList,colParse='RAW_ERROR_RATE',ColMatchStyle='min',tableName=P250spc_id2FailModeTable)
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(250,spc_id)
      zoneFailList = []
      for data in xrange(len(P250choppedTable)):
         baseUpdate = {
          'HD_PHYS_PSN': P250choppedTable[data].get('HD_PHYS_PSN'),
          'TRK_NUM': P250choppedTable[data].get('START_TRK_NUM'),
          'SPC_ID': P250choppedTable[data].get('SPC_ID'),
          'OCCURRENCE': occurrence,
          'SEQ':curSeq,
          'TEST_SEQ_EVENT': testSeqEvent,
          'HD_LGC_PSN': P250choppedTable[data].get('HD_LGC_PSN'),
          'RBIT':self.oUtility.setDBPrecision((P250choppedTable[data].get('BITS_READ_LOG10')),4,2),
          'RRAW':self.oUtility.setDBPrecision((P250choppedTable[data].get('RAW_ERROR_RATE')),4,2), #leave sign negative
          'OTF':'', #null for now
          'HARD':'', #null for now
          'DATA_ZONE':P250choppedTable[data].get('DATA_ZONE'),
          }
         self.dut.dblData.Tables('P_QUICK_ERR_RATE').addRecord(baseUpdate)
         if float(self.oUtility.setDBPrecision((P250choppedTable[data].get('RAW_ERROR_RATE')),4,2)) > float(rawBERLimit):
            if testSwitch.SKIPZONE:
               head = int(P250choppedTable[data].get('HD_PHYS_PSN'))
               zone = int(P250choppedTable[data].get('DATA_ZONE'))
               BER  = float(self.oUtility.setDBPrecision((P250choppedTable[data].get('RAW_ERROR_RATE')),4,2))
               #objMsg.printMsg("head %s zone %s BER %4.2f" %(head, zone, BER))
               if (head,zone) in self.dut.skipzn:
                  #objMsg.printMsg("head %s zone %s BER %4.2f is skip zone" %(head, zone, BER))
                  continue
            zoneFailList.append(P250choppedTable[data].get('DATA_ZONE'))
      if type(spc_id) == str: spc_id = int(spc_id)
      objMsg.printMsg("quickErrorRate: saving P_QUICK_ERR_RATE table to marshall object ", objMsg.CMessLvl.VERBOSEDEBUG)
      self.dut.objData.update({'P_QUICK_ERR_RATE':self.dut.dblData.Tables('P_QUICK_ERR_RATE').tableDataObj()})
      if testSwitch.BERScreen2_Enabled and (len(zoneFailList) > 0):
         ScrCmds.raiseException(10632,"Minimum Error rate not met on Zones %s" % zoneFailList)


   def BERFilter(self,inPrm):
      """
      Based on RAW data for every head every zone, filter some drive with heavy fluctuation...
      """
      STD_THRESHOLD =  inPrm.get('STD_THRESHOLD',0.5)
      FITSLOPE_THRESHOLD = inPrm.get('FITSLOPE_THRESHOLD',7.5)
      A_THRESHOLD =  inPrm.get('FIT_THRESHOLD',5)

      RawTable =  self.dut.dblData.Tables('P_QUICK_ERR_RATE').tableDataObj()

      objMsg.printMsg("BER SCREEN" )
      objMsg.printMsg("Failing criteria: STANDARD DEVIATION, FITSLOPE, A")
      objMsg.printMsg("%-10f %-10f %-10f" % (STD_THRESHOLD,FITSLOPE_THRESHOLD,A_THRESHOLD))


      testzones = inPrm.get('test_zones',[0,8,15])
      numofzone = len(testzones)
      tableofs = self.dut.imaxHead * numofzone
      imaxHead = self.dut.imaxHead

      for head in range(imaxHead):
         sum_ber = 0
         sum_stddeviation = 0
         for zone in range (numofzone):

            Raw = float(RawTable[tableofs + zone + head * numofzone] ['RRAW'])
            tracknum =   RawTable[tableofs + zone + head * numofzone] ['TRK_NUM']
            headnum = RawTable[tableofs + zone + head * numofzone] ['HD_LGC_PSN']
            zonenum = RawTable[tableofs + zone + head * numofzone] ['DATA_ZONE']
            sum_ber = sum_ber + Raw
            objMsg.printMsg("%-4d%-4d%-11d%-10f" % (zonenum,headnum,tracknum,Raw))

         averageber = sum_ber/numofzone
         objMsg.printMsg("Average BER: %-10f" % (averageber))

         for zone in range (numofzone):
            Raw = float(RawTable[tableofs + zone + head * numofzone] ['RRAW'])
            sum_stddeviation = sum_stddeviation + (averageber - Raw)* (averageber - Raw)
         stddeviation= sqrt(sum_stddeviation /(numofzone -1))
         objMsg.printMsg("Standard Deviation: %-10f" % (stddeviation))

         sum_XY = 0
         sum_Y = 0
         for zone in range (9):   #calculate zone 0-8
            Raw = float(RawTable[tableofs + zone + head * numofzone] ['RRAW'])
            XY = zone * Raw
            sum_XY = sum_XY + XY
            sum_Y = Raw + sum_Y

         objMsg.printMsg("xy,y: %-10f %-10f" % (sum_XY,sum_Y))

         a = 17*sum_Y/45 - sum_XY/15
         b = sum_XY/60 - sum_Y/15
         FittingSlope = stddeviation * b *100
         objMsg.printMsg("a, b, FittingSlope : %-10f %-10f %-10f" % (a,b,FittingSlope))

         if ( b >0 ):
            if (stddeviation > STD_THRESHOLD):
               if (FittingSlope > FITSLOPE_THRESHOLD):
                  if (a < A_THRESHOLD):
                     ScrCmds.raiseException(14621, "BER Screen Fail")

   def Average_QBER_byZone(self, inPrm):
      """
      Based on table P250_BER_BY_ZONE, average it and fail accoridingly
      """

      ######################## DBLOG Implementaion- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      self.format_startTime = time()
      ########################

      failed_AverageQBERLimit_list = []
      AverageQBERLimit = inPrm.get('AverageQBERLimit',0)

      RawTable =  self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()

      testzones = inPrm.get('TEST_ZONES', range(self.dut.numZones))
      tableofs  = inPrm.get('TABLE_OFFS', 0)
      numofzone = len(testzones)
      imaxHead = self.dut.imaxHead

      objMsg.printMsg("tableofs==%s"%(str(tableofs)))
      validBER = [ [] for i in range(self.dut.imaxHead) ]
      for row in range(self.dut.imaxHead * numofzone):
         head = int(RawTable[row+tableofs]['HD_LGC_PSN'])
         zone = int(RawTable[row+tableofs]['DATA_ZONE'])
         Raw = float(RawTable[row+tableofs]['RAW_ERROR_RATE'])
         if (Raw < 0):
            validBER[head].append(-Raw)

      for head in range(imaxHead):
         if validBER[head]:
            sumBER = sum(validBER[head])
            cntBER = len(validBER[head])
            avgBER = sumBER / cntBER
         else:
            sumBER = 0
            cntBER = 0
            avgBER = 0

         if avgBER <= AverageQBERLimit:
            failed_AverageQBERLimit_list.append((head, avgBER))

         objMsg.printMsg("Average BER: Hd%-2d  avgBER %-10f" % (head, avgBER))

         objDut.dblData.Tables('P_AVERAGE_ERR_RATE').addRecord(
            {
            'HD_PHYS_PSN':    self.dut.LgcToPhysHdMap[head],
            'SPC_ID':         1,
            'OCCURRENCE':     occurrence,
            'SEQ':            curSeq,
            'TEST_SEQ_EVENT': testSeqEvent,
            'HD_LGC_PSN':     head,
            'SUM_QBER':       sumBER,
            'CNT_QBER':       cntBER,
            'AVG_QBER':       avgBER,
            })
      objMsg.printDblogBin(self.dut.dblData.Tables('P_AVERAGE_ERR_RATE'))
      return failed_AverageQBERLimit_list

   def CollectVGA(self, inPrm, spc_id=1):

      ######################## DBLOG Implementaion- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0,spc_id)
      self.format_startTime = time()
      ########################


      testZone = inPrm.get('test_zone',0)

      for hd in range(self.dut.imaxHead):
         servovga = 0x1FF
         self.oFSO.getZoneTable()
         zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()

         Index = self.dth.getFirstRowIndexFromTable_byZone(zt, hd, testZone)
         teststartcyl=int(zt[Index]['ZN_START_CYL'])
         ret = self.oServo.wsk(teststartcyl,hd)
         #servovga = self.oChannel.readChannel(0x5E)
         #servovga = self.rdChVal(0x5E, 15)
         servovga = self.oChannelAccess.readChannel(0x5E)
         objMsg.printMsg("%-4d%-4d" % (hd,teststartcyl))
         objMsg.printMsg(servovga)

         self.dut.dblData.Tables('P_SERVOVGA').addRecord(
                           {
                           'HD_PHYS_PSN': self.dut.LgcToPhysHdMap[hd],
                           'SPC_ID': spc_id,
                           'OCCURRENCE': occurrence,
                           'SEQ':curSeq,
                           'TEST_SEQ_EVENT': testSeqEvent,
                           'HD_LGC_PSN': hd,
                           'TRK_NUM': teststartcyl,
                           'ZONE': testZone,
                           'SERVOVGA':(servovga),
                           })
      if spc_id == 1:
         objMsg.printMsg("collect VGA): saving P_SERVOVGA table to marshall object %s" %str(self.dut.dblData.Tables('P_SERVOVGA').tableDataObj()   ), objMsg.CMessLvl.VERBOSEDEBUG)
         self.dut.objData.update({'P_SERVOVGA':self.dut.dblData.Tables('P_SERVOVGA').tableDataObj()})

   def checkDeltaVGA (self, inPrm):
      """
      Calculate the VGA difference between the first and last runs of quickErrRate.
      Raise an error if the maximum difference is greater than the limit.
      """
      if testSwitch.virtualRun:
         return
      maxAllowedDiff = inPrm.get('max_vga_diff',30)


      ######################## DBLOG Implementaion- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      self.format_startTime = time()

      ########################
      if (not testSwitch.virtualRun) :
         haveRun1Data = 0
         SERVOVGATable = self.dut.dblData.Tables('P_SERVOVGA').tableDataObj()

         for data in xrange(len(SERVOVGATable)):
            if (int((SERVOVGATable[data].get('SPC_ID'))))==1:
               haveRun1Data = 1
            if haveRun1Data ==1:
               break
      # Calculate the difference
         if haveRun1Data ==0:
            objMsg.printMsg("checkDeltaVGA: the P_SERVOVGA table in RAM does not contain spc_id =1  data, must retrieve form host HDD", objMsg.CMessLvl.VERBOSEDEBUG)
            SERVOVGAFromDisk = self.dut.objData.retrieve('P_SERVOVGA')
            for data in xrange(len(SERVOVGAFromDisk)):
               baseUpdate = {
                'HD_PHYS_PSN': SERVOVGAFromDisk[data].get('HD_PHYS_PSN'),
                'SPC_ID': SERVOVGAFromDisk[data].get('SPC_ID'),
                'OCCURRENCE': SERVOVGAFromDisk[data].get('OCCURRENCE'),
                'SEQ':SERVOVGAFromDisk[data].get('SEQ'),
                'TEST_SEQ_EVENT': SERVOVGAFromDisk[data].get('TEST_SEQ_EVENT'),
                'HD_LGC_PSN': SERVOVGAFromDisk[data].get('HD_LGC_PSN'),
                'TRK_NUM': SERVOVGAFromDisk[data].get('TRK_NUM'),
                'ZONE': SERVOVGAFromDisk[data].get('ZONE'),
                'SERVOVGA':SERVOVGAFromDisk[data].get('SERVOVGA'),
                }
               self.dut.dblData.Tables('P_SERVOVGA').addRecord(baseUpdate)

      # Calculate the difference
      (maxDiff, minDiff, diffData, entrySigVal) = self.dut.dblData.Tables('P_SERVOVGA').diffDbLog(diffItem='SERVOVGA',entrySig='SEQ',sortOrder=['HD_LGC_PSN','ZONE'])

      # Check for failures

      headcnt = 0

      for item in diffData:
         self.dut.dblData.Tables('P_DELTAVGA').addRecord(
            {
            'HD_PHYS_PSN': self.dut.LgcToPhysHdMap[headcnt],
            'SPC_ID': 1,
            'OCCURRENCE': occurrence,
            'SEQ':curSeq,
            'TEST_SEQ_EVENT': testSeqEvent,
            'HD_LGC_PSN': headcnt,
            'DELTAVGA': item.get('difference'),
            })
         headcnt= headcnt + 1

      if maxDiff > maxAllowedDiff:
         objMsg.printMsg("DeltaVGA Screen limit exceeded.  VGA difference: %s; Limit: %s" % (maxDiff,maxAllowedDiff))
         ScrCmds.raiseException(14662, "DeltaVGA limit exceeded")




   def zap_FS_basic (self,start_hd,end_hd,start_cyl,end_cyl):
      """ do basic ZAP and analog data flawscan for a range of tracks/heads
      inputs: start_head, end_head, start_cyl, end_cyl

      """
      ###############set up for calls to ZAP and flawscan
      zap_fs_err = 0 # use this var to catch failing case from calling routine
      TP.prm_basic_AFS_CM_Read_109["HEAD_RANGE"] = (start_hd<<8) + end_hd
      TP.prm_basic_AFS_2T_Write_109["HEAD_RANGE"] = (start_hd<<8) + end_hd
      TP.zapbasic_175["HEAD_RANGE"] =(start_hd<<8) + end_hd
      upperWord,lowerWord = self.oUtility.ReturnTestCylWord(start_cyl)
      TP.prm_basic_AFS_CM_Read_109["START_CYL"] = (upperWord,lowerWord)
      TP.prm_basic_AFS_2T_Write_109["START_CYL"] = (upperWord,lowerWord)
      TP.zapbasic_175["START_CYL"] = (upperWord,lowerWord)
      upperWord,lowerWord = self.oUtility.ReturnTestCylWord(end_cyl)
      TP.prm_basic_AFS_CM_Read_109["END_CYL"] = (upperWord,lowerWord)
      TP.prm_basic_AFS_2T_Write_109["END_CYL"] = (upperWord,lowerWord)
      TP.zapbasic_175["END_CYL"] = (upperWord,lowerWord)
# call ZAP and flawscan
      try :
         self.oSrvOpti.zap(TP.zapbasic_175)
      except :
         objMsg.printMsg("an exception occurred during ZAP")
         zap_fs_err = 1

      if (zap_fs_err) == 0 and not (testSwitch.QBER_skip_flawscan_prep):
         try :
            self.objProc.St(TP.prm_basic_AFS_2T_Write_109) # analog flawscan write
         except:
            objMsg.printMsg("an exception occurred during flawscan write")
            zap_fs_err = 1
      if (zap_fs_err) == 0 and not (testSwitch.QBER_skip_flawscan_prep):
         try :
            self.objProc.St(TP.prm_basic_AFS_CM_Read_109) # analog flawscan read
         except:
            objMsg.printMsg("an exception occurred during flawscan read")
            zap_fs_err = 1

      return zap_fs_err

   def checkDeltaBER (self, inPrm, table = 'P_QUICK_ERR_RATE', metric = 'RRAW'):
      """
      Calculate the BER difference between the first and last runs of quickSymbolErrorRate or quickErrRate.
      Raise an error if the maximum difference is greater than the limit.
      """
      maxAllowedDiff = inPrm.get('max_diff')
      passingBER = inPrm.get('SER_raw_BER_limit')
      if (not testSwitch.virtualRun) and (table == 'P_QUICK_ERR_RATE'):
         haveRun1Data = 0
         QBERTable = self.dut.dblData.Tables('P_QUICK_ERR_RATE').tableDataObj()

         for data in xrange(len(QBERTable)):
            if (int((QBERTable[data].get('SPC_ID'))))==1:
               haveRun1Data = 1
            if haveRun1Data ==1:
               break
         if haveRun1Data ==0:
            try:
               objMsg.printMsg("checkDeltaBER: the P_QUICK_ERR_RATE table in RAM does not contain spc_id =1 (BER run 1) data, must retrieve from host HDD", objMsg.CMessLvl.VERBOSEDEBUG)
               QBERTableFromDisk = self.dut.objData.retrieve('P_QUICK_ERR_RATE')
               for data in xrange(len(QBERTableFromDisk)):
                  baseUpdate = {
                     'HD_PHYS_PSN': QBERTableFromDisk[data].get('HD_PHYS_PSN'),
                     'TRK_NUM': QBERTableFromDisk[data].get('TRK_NUM'),
                     'SPC_ID': QBERTableFromDisk[data].get('SPC_ID'),
                     'OCCURRENCE': QBERTableFromDisk[data].get('OCCURRENCE'),
                     'SEQ':QBERTableFromDisk[data].get('SEQ'),
                     'TEST_SEQ_EVENT': QBERTableFromDisk[data].get('TEST_SEQ_EVENT'),
                     'HD_LGC_PSN': QBERTableFromDisk[data].get('HD_LGC_PSN'),
                     'RBIT':QBERTableFromDisk[data].get('RBIT'),
                     'RRAW':QBERTableFromDisk[data].get('RRAW'),
                     'OTF':'', #null for now
                     'HARD':'', #null for now
                     'DATA_ZONE':QBERTableFromDisk[data].get('DATA_ZONE'),
                   }
                  self.dut.dblData.Tables('P_QUICK_ERR_RATE').addRecord(baseUpdate)
               haveRun1Data = 1
            except: pass
      if not testSwitch.virtualRun:
         if (haveRun1Data == 0):
            objMsg.printMsg("checkDeltaBER: the P_QUICK_ERR_RATE table cannot be find from host HDD. Abort", objMsg.CMessLvl.VERBOSEDEBUG)
            return
      # Calculate the difference
      if not testSwitch.FE_0149136_409401_P_DELTA_BER_IMPROVEMENT:
         (maxDiff, minDiff, diffData, entrySigVal) = self.dut.dblData.Tables(table).diffDbLog(diffItem=metric,entrySig='SEQ',sortOrder=['HD_LGC_PSN','DATA_ZONE'])
      else:
         (maxDiff, minDiff, diffData, entrySigVal) = self.dut.dblData.Tables(table).diffDbLog(diffItem=metric,entrySig='SPC_ID',sortOrder=['HD_LGC_PSN','DATA_ZONE'])

      if testSwitch.PRINT_TABLE_P_DELTA_RRAW:
         for item in diffData:
            if testSwitch.BF_0133147_208705_TABLE_MISSING_HEAD_DATA:
               hd_phys_psn = self.dut.LgcToPhysHdMap[int(item['HD_LGC_PSN'])]
               data_zone = item['DATA_ZONE']
               delta_rraw = item['difference']
            else:
               hd_phys_psn = item.get('HD_PHYS_PSN')
               data_zone = item.get('DATA_ZONE')
               delta_rraw = item.get('difference')

            self.dut.dblData.Tables('P_DELTA_RRAW').addRecord(
            {
               'HD_PHYS_PSN':          hd_phys_psn,
               'DATA_ZONE':            data_zone,
               'SPC_ID':               self.dut.objSeq.curRegSPCID,
               'OCCURRENCE':           self.dut.objSeq.getOccurrence(),
               'SEQ':                  self.dut.objSeq.curSeq,
               'TEST_SEQ_EVENT':       self.dut.objSeq.getTestSeqEvent(0),
               'DELTA_RRAW':           delta_rraw,
            })

         objMsg.printDblogBin(self.dut.dblData.Tables('P_DELTA_RRAW'))
      # Check for failures
      if maxDiff > maxAllowedDiff:
         # We have a BER degradation, but we will only fail if the minimum BER is unacceptable
         keyName = metric + "__SEQ_" + str(entrySigVal[-1])
###########allow n zones per hd to fail as defined in prm_quickSER_250..if not defined, lim =0
         numViolationsList=[]
         numAllowedFailingZones = inPrm.get('checkDeltaBER_num_failing_zones',0)
         testZoneList = inPrm.get('TEST_ZONES',inPrm.get('test_zones'))
         if testSwitch.auditTest ==1:
            numAllowedFailingZones = len(testZoneList) + 1
            objMsg.printMsg("AUDIT TEST: checkDeltaBER adjusting paramters to not fail...",objMsg.CMessLvl.IMPORTANT)
         for head in xrange(self.dut.imaxHead):
            numFailingZones = 0
            hdOffset = len(testZoneList) * head
            for z in xrange(len(testZoneList)): #chek limit on a per head basis
               try:
                  if (diffData[z + hdOffset]['difference'] > maxAllowedDiff) and (float(diffData[z + hdOffset][keyName]) > passingBER) and (float(diffData[z + hdOffset][keyName]) < 0):
                     numFailingZones += 1
                     objMsg.printMsg("delta BER failed for this hd/zone, head = %s, zone = %s, diff = %s, limit = %s" % (head,testZoneList[z],diffData[z + hdOffset]['difference'],maxAllowedDiff),objMsg.CMessLvl.IMPORTANT)
               except KeyError: break
               if numFailingZones > numAllowedFailingZones:
                  if testSwitch.auditTest ==0:
                     ScrCmds.raiseException(14574, "Delta BER limit exceeded for %s zone(s) on head %s.num zones allowed to fail = %s" % (numFailingZones,head,numAllowedFailingZones))
                  elif testSwitch.auditTest ==1:
                     objMsg.printMsg("AUDIT TEST: checkDeltaBER Delta BER limit exceeded, but allowing test to pass",objMsg.CMessLvl.IMPORTANT)# dont raise exception for auditTest

   def QBERFullStroke(self,ECClevel):
      """ run cudacom ber test for one rev on every track in ALL zones. sum errors and rbit, then compute the total BER for each zone.
      caller gives: ECClevel
      """
      ######################## DBLOG Implementaion- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      self.format_startTime = time()
      ########################
      erCalc = lambda totErrs,bits: abs(log10(float(totErrs)/float(bits)))

      imaxHead = self.dut.imaxHead

      for hd in range(imaxHead):
         self.oFSO.getZoneTable()
         zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()

         FatalCylList = []
         Index = self.dth.getFirstRowIndexFromTable_byHead(zt, hd)
         #calculate per row of record, instead of per zone
         while Index<len(zt) and int(zt[Index]['HD_LGC_PSN'])==hd:
            zone = int(zt[Index]['ZN'])
            objMsg.printMsg('zone loop start-ZONE =  %d' % zone)
            sc = int(zt[Index]['ZN_START_CYL'])
            ec = sc + int(zt[Index]['NUM_CYL']) - 1
            numTrksTested = 0
            totER = 0.0
            data_errs = 0
            sync_errs = 0
            rbit = 1.0 #need min of 1 for log(rbit)
            bits_track = int(zt[Index][TP.zone_table['trk_name']])*4096*8 # blm
            for cyl in xrange(sc,ec):
               other_errs = 0
               ret = self.oServo.wsk(cyl, hd, retries = 10)
               if ret == 0:
                  if struct.unpack(">L",self.writetrack(retries = 10))[0] == 128 :
                     ret = self.oServo.rsk(cyl, hd, retries = 10)
                     if ret == 0:
                        berMsmtBad = 0 # init
                        try:
                           buf = self.ber(90,1,ECClevel) # call ber test for each track
                        except:
                           objMsg.printMsg('exception during ber cudacom call at cyl = %d' % cyl, objMsg.CMessLvl.CRITICAL)
                           objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                           berMsmtBad = 1
                        if berMsmtBad == 0:
                           result = struct.unpack("fLLLLLLL",buf)
                           other_errs = result[3]
                           if other_errs == 0 :
                              data_errs += result[1]
                              sync_errs += result[2]
                              rbit += bits_track
                              numTrksTested += 1
                           else: # other_errs != 0
                              FatalCylList.append(str(cyl))
                        else: #berMsmtBad != 0
                           FatalCylList.append(str(cyl))
                     else: #ret != 0: (READ SEEK)
                        FatalCylList.append(str(cyl))
                  else: #struct.unpack(">L",self.writetrack(retries = 10))[0] != 128 :
                     FatalCylList.append(str(cyl))
               else: #ret != 0: (WRITE SEEK)
                  FatalCylList.append(str(cyl))
            if  (numTrksTested != 0):
               totErrs = data_errs + sync_errs
               if totErrs == 0 :
                  totER = erCalc( 0.5, rbit)
               else :
                  totER = erCalc( totErrs, rbit)
            objMsg.printMsg(" QBERFullStroke: EACH ZONES' total ER OUTPUTs are NEXT ::::::::::::::")
            objMsg.printMsg('HEAD NUM =  %d' % hd + '        ZONE NUM =  %d' % zone)
            objMsg.printMsg("ECClevel = %u " % (ECClevel) + " zoneER = %f " % (totER) +
                            "rbit = %f " % (log10(rbit)) +"num trks tested = %d" % (numTrksTested))
            rbit = self.oUtility.setDBPrecision(log10(rbit),11,7)
            BER = self.oUtility.setDBPrecision(totER,11,7)
            if ECClevel == 0:
               RRAW = BER
               OTF = 0
            elif ECClevel != 0: #must be OTF msmt
               OTF = BER
               RRAW = 0
##### dblog init for each hd/zone result ######################################
            self.dut.dblData.Tables('P_QUICK_ERR_RATE').addRecord(
               {
               'HD_PHYS_PSN': self.dut.LgcToPhysHdMap[hd],
               'TRK_NUM': int(zt[Index]['ZN_START_CYL']), # use 1st cyl
               'SPC_ID': 1,
               'OCCURRENCE': occurrence,
               'SEQ':curSeq,
               'TEST_SEQ_EVENT': testSeqEvent,
               'HD_LGC_PSN': hd,
               'RBIT':rbit,
               'RRAW':RRAW,
               'OTF':OTF,
               'HARD':'', #null for now
               'DATA_ZONE':zone,
               })
            Index+=1      
         objMsg.printMsg(" all zones complete on this head,CYLS THAT HAD EXCEPTIONS DURING CUDACOM CALLS FOLLOW :::")
         objMsg.printMsg("FOR HEAD NUM: %d " % hd + " FATAL CYLS: %s " % (FatalCylList))
######################## DBLOG Implementaion- Closure
      curTime = time()
      curSeq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      self.dut.dblData.Tables('TEST_TIME_BY_TEST').addRecord(
         {
         'SPC_ID': 1,
         'OCCURRENCE': occurrence,
         'SEQ': curSeq,
         'TEST_SEQ_EVENT': testSeqEvent,
         'TEST_NUMBER': 0,
         'ELAPSED_TIME': '%.2f' % (curTime-self.format_startTime),
         'PARAMETER_NAME':'P_QUICK_ERR_RATE',
         })

      # !!! MUST FIX THIS
      objMsg.printDblogBin(self.dut.dblData.Tables('P_QUICK_ERR_RATE'))

   def adjustForWIJITA(self, inPrm):
      self.St(inPrm)

   #----------------------------------------------------------------------------
   def STE_screen(self):
      dut = self.dut
      oProc = CProcess()

      write_cur={}
      orig_cur={}
      STE_fail=0
      STEHeadMask=0

      #Get current write current values
      try:
         self.dut.dblData.delTable('P172_WRITE_POWERS')
      except:
         pass

      reader = dbLogUtilities.DBLogReader(self.dut, 'P172_WRITE_POWERS', suppressed = True)
      reader.ignoreExistingData()

      prm = TP.prm_172_writepowers.copy()
      prm['DblTablesToParse'] = ['P172_WRITE_POWERS']
      oProc.St(TP.prm, spc_id=1)
      wp = reader.getTableObj()

      MAXHN=int(wp[len(wp)-1]['HD_PHYS_PSN'])
      MAXZN=int(wp[len(wp)-1]['DATA_ZONE'])
      for index in range(len(wp)):
         if write_cur.has_key(int(wp[index]['HD_PHYS_PSN'])):
            write_cur[int(wp[index]['HD_PHYS_PSN'])][int(wp[index]['DATA_ZONE'])]=int(wp[index]['WRT_CUR'])
            orig_cur[int(wp[index]['HD_PHYS_PSN'])][int(wp[index]['DATA_ZONE'])]=int(wp[index]['WRT_CUR'])
         else:
            write_cur[int(wp[index]['HD_PHYS_PSN'])]={}
            orig_cur[int(wp[index]['HD_PHYS_PSN'])]={}
            write_cur[int(wp[index]['HD_PHYS_PSN'])][int(wp[index]['DATA_ZONE'])]=int(wp[index]['WRT_CUR'])
            orig_cur[int(wp[index]['HD_PHYS_PSN'])][int(wp[index]['DATA_ZONE'])]=int(wp[index]['WRT_CUR'])

      oProc.St({'test_num':172}, CWORD1=(5),)
      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
         P172_AFH_CLEARANCE_tableName = 'P172_AFH_DH_CLEARANCE'
      else:
         P172_AFH_CLEARANCE_tableName = 'P172_AFH_CLEARANCE'

      ClrTable=self.dut.dblData.Tables( P172_AFH_CLEARANCE_tableName ).tableDataObj()

      orig_wrtclr=ClrTable[0]['WRT_CLRNC_TRGT']
      orig_preclr=ClrTable[0]['PRE_WRT_CLRNC_TRGT']
      if testSwitch.FE_0112188_345334_HEAD_RANGE_SUPPORT_10_HEADS :
         oProc.St({'test_num':178},CWORD1=(0x2220),  CWORD2=(0x100), HEAD_RANGE=(0x003FF), TGT_PREWRT_CLR=(int(orig_preclr)+TP.ClrDelta))
         oProc.St({'test_num':178},CWORD1=(0x2220),  CWORD2=(0x080), HEAD_RANGE=(0x003FF), TGT_WRT_CLR=(int(orig_wrtclr)+TP.ClrDelta))
      else:
         oProc.St({'test_num':178},CWORD1=(0x2220),  CWORD2=(0x100), HEAD_RANGE=(0x00FF), TGT_PREWRT_CLR=(int(orig_preclr)+TP.ClrDelta))
         oProc.St({'test_num':178},CWORD1=(0x2220),  CWORD2=(0x080), HEAD_RANGE=(0x00FF), TGT_WRT_CLR=(int(orig_wrtclr)+TP.ClrDelta))

      #Iw optimizing for STE -> Higher Clearance Sweep
      for hd in range(MAXHN+1):
         zone_mask_low = 0
         zone_mask_high = 0
         for zn in TP.STEzones:
            #if (2**zn) < 65536:
            #   zone_mask_low=(2**zn)
            #   zone_mask_high=0
            #else:
            #   zone_mask_low=0
            #   zone_mask_high=1
            if zn < 32:
               zone_mask_low |= (1 << zn)
            else:
               zone_mask_high |= (1 << (zn -32))
            while 1:
               #oProc.St(TP.prm_195_STE, HEAD_RANGE=(hd*256+hd),ZONE_MASK=(zone_mask_high,zone_mask_low),)
               oProc.St(TP.prm_195_STE, HEAD_RANGE=(hd*256+hd),ZONE_MASK=self.oUtility.ReturnTestCylWord(zone_mask_low),ZONE_MASK_EXT=self.oUtility.ReturnTestCylWord(zone_mask_high),)
               table=dut.dblData.Tables('P195_STE_SUMMARY').tableDataObj()
               STEmetric = float(table[len(table)-1]['LOG10_NORM_SUM_CSM_DIFF'])
               if STEmetric > TP.STEthresh:
                  STEHeadMask = STEHeadMask | (2**hd)
                  if write_cur[hd][zn] >= (TP.STEIwMin + TP.STEIwStep):
                     write_cur[hd][zn]-=TP.STEIwStep
                     #oProc.St(TP.prm_178_Iw_RAP,HEAD_RANGE=(2**hd),BIT_MASK=(zone_mask_high,zone_mask_low),WRITE_CURRENT=(write_cur[hd][zn]))
                     oProc.St(TP.prm_178_Iw_RAP,HEAD_RANGE=(2**hd),BIT_MASK=self.oUtility.ReturnTestCylWord(zone_mask_low), BIT_MASK_EXT = self.oUtility.ReturnTestCylWord(zone_mask_high),WRITE_CURRENT=(write_cur[hd][zn]))
                  else:
                     N=0
                     tempFOM=100
                     tempIw=16
                     for Iw in range(write_cur[hd][zn],orig_cur[hd][zn]+1,2):
                        if float(table[len(table)-(1+N)]['LOG10_NORM_SUM_CSM_DIFF']) < tempFOM:
                           tempFOM=float(table[len(table)-(1+N)]['LOG10_NORM_SUM_CSM_DIFF'])
                           tempIw=Iw
                        N+=1
                     write_cur[hd][zn]=tempIw
                     #oProc.St(TP.prm_178_Iw_RAP,HEAD_RANGE=(2**hd),BIT_MASK=(zone_mask_high,zone_mask_low),WRITE_CURRENT=(write_cur[hd][zn]))
                     oProc.St(TP.prm_178_Iw_RAP,HEAD_RANGE=(2**hd),BIT_MASK=self.oUtility.ReturnTestCylWord(zone_mask_low), BIT_MASK_EXT = self.oUtility.ReturnTestCylWord(zone_mask_high),WRITE_CURRENT=(write_cur[hd][zn]))
                     break
               else:
                  break
      if testSwitch.FE_0112188_345334_HEAD_RANGE_SUPPORT_10_HEADS :
         oProc.St({'test_num':178},CWORD1=(0x2220),  CWORD2=(0x100), HEAD_RANGE=(0x003FF), TGT_PREWRT_CLR=(int(orig_preclr)))
         oProc.St({'test_num':178},CWORD1=(0x2220),  CWORD2=(0x080), HEAD_RANGE=(0x003FF), TGT_WRT_CLR=(int(orig_wrtclr)))
      else:
         oProc.St({'test_num':178},CWORD1=(0x2220),  CWORD2=(0x100), HEAD_RANGE=(0x00FF), TGT_PREWRT_CLR=(int(orig_preclr)))
         oProc.St({'test_num':178},CWORD1=(0x2220),  CWORD2=(0x080), HEAD_RANGE=(0x00FF), TGT_WRT_CLR=(int(orig_wrtclr)))

      for hd in range(MAXHN+1):
         for zn in range(1,len(TP.STEzones)):
            orig_cur[hd][zn]=write_cur[hd][zn]
      #Iw optimizing for STE -> Original Clearance Sweep
      for hd in range(MAXHN+1):
         zone_mask_low = 0
         zone_mask_high = 0
         for zn in TP.STEzones:
            #if (2**zn) < 65536:
            #   zone_mask_low=(2**zn)
            #   zone_mask_high=0
            #else:
            #   zone_mask_low=0
            #   zone_mask_high=1
            if zn < 32:
               zone_mask_low |= (1 << zn)
            else:
               zone_mask_high |= (1 << (zn -32))
            while 1:
               #oProc.St(TP.prm_195_STE, spc_id=2, HEAD_RANGE=(hd*256+hd),ZONE_MASK=(zone_mask_high,zone_mask_low),)
               oProc.St(TP.prm_195_STE, spc_id=2, HEAD_RANGE=(hd*256+hd),ZONE_MASK=self.oUtility.ReturnTestCylWord(zone_mask_low),ZONE_MASK_EXT=self.oUtility.ReturnTestCylWord(zone_mask_high),)
               table=dut.dblData.Tables('P195_STE_SUMMARY').tableDataObj()
               STEmetric = float(table[len(table)-1]['LOG10_NORM_SUM_CSM_DIFF'])
               if STEmetric > TP.STEthresh:
                  STEHeadMask = STEHeadMask | (2**hd)
                  if write_cur[hd][zn] >= (TP.STEIwMin + TP.STEIwStep):
                     write_cur[hd][zn]-=TP.STEIwStep
                     #oProc.St(TP.prm_178_Iw_RAP,HEAD_RANGE=(2**hd),BIT_MASK=(zone_mask_high,zone_mask_low),WRITE_CURRENT=(write_cur[hd][zn]))
                     oProc.St(TP.prm_178_Iw_RAP,HEAD_RANGE=(2**hd),BIT_MASK=self.oUtility.ReturnTestCylWord(zone_mask_low), BIT_MASK_EXT = self.oUtility.ReturnTestCylWord(zone_mask_high),WRITE_CURRENT=(write_cur[hd][zn]))
                  else:
                     N=0
                     tempFOM=100
                     tempIw=16
                     for Iw in range(write_cur[hd][zn],orig_cur[hd][zn]+1,2):
                        if float(table[len(table)-(1+N)]['LOG10_NORM_SUM_CSM_DIFF']) < tempFOM:
                           tempFOM=float(table[len(table)-(1+N)]['LOG10_NORM_SUM_CSM_DIFF'])
                           tempIw=Iw
                        N+=1
                     write_cur[hd][zn]=tempIw
                     #oProc.St(TP.prm_178_Iw_RAP,HEAD_RANGE=(2**hd),BIT_MASK=(zone_mask_high,zone_mask_low),WRITE_CURRENT=(write_cur[hd][zn]))
                     oProc.St(TP.prm_178_Iw_RAP,HEAD_RANGE=(2**hd),BIT_MASK=self.oUtility.ReturnTestCylWord(zone_mask_low), BIT_MASK_EXT = self.oUtility.ReturnTestCylWord(zone_mask_high),WRITE_CURRENT=(write_cur[hd][zn]))
                     break
               else:
                  break

      #Use HeadMask to interpolate Iw changes
      for hd in range(MAXHN+1):
         if (STEHeadMask & (2**hd)) != 0:
            prevZn=0
            for znkey in range(1,len(TP.STEzones)):
               topZn=TP.STEzones[znkey]
               A=float(write_cur[hd][topZn]-write_cur[hd][prevZn])/(topZn-prevZn)
               B=float(write_cur[hd][topZn]-A*topZn)
               zone_mask_low = 0
               zone_mask_high = 0
               for zn in range(prevZn,topZn):
                  write_cur[hd][zn]=int(round(A*zn+B))
                  #if (2**zn) < 65536:
                  #   zone_mask_low=(2**zn)
                  #   zone_mask_high=0
                  #else:
                  #   zone_mask_low=0
                  #   zone_mask_high=1
                  if zn < 32:
                     zone_mask_low |= (1 << zn)
                  else:
                     zone_mask_high |= (1 << (zn -32))
                  #oProc.St(TP.prm_178_Iw_RAP,HEAD_RANGE=(2**hd),BIT_MASK=(zone_mask_high,zone_mask_low),WRITE_CURRENT=(write_cur[hd][zn]))
                  oProc.St(TP.prm_178_Iw_RAP,HEAD_RANGE=(2**hd),BIT_MASK=self.oUtility.ReturnTestCylWord(zone_mask_low), BIT_MASK_EXT = self.oUtility.ReturnTestCylWord(zone_mask_high),WRITE_CURRENT=(write_cur[hd][zn]))
               prevZn=topZn
      oProc.St({'test_num':178}, CWORD1=0x0220)
      oProc.St(TP.prm_172_writepowers, spc_id=2)

      return STEHeadMask

   def forceRezoneAfterATI(self, ec):
      if TP.stateRerunParams['states'].has_key('ATI_SCRN') and self.dut.nextState == 'ATI_SCRN':
         if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
            from VBAR import CUtilityWrapper
         else:
            from base_SerialTest import CUtilityWrapper
         if (ec in TP.stateRerunParams['states']['ATI_SCRN']) and (self.dut.CAPACITY_PN in TP.Native_Capacity) and (CUtilityWrapper(self.dut,{}).SearchLowerCapacityPn()!=0):
            objMsg.printMsg("ATI Failed for EC %d (%s) - Force Rezone to Lower Capacity" % (ec, self.dut.partNum))
            self.dut.Waterfall_Req = "REZONE"
            objMsg.printMsg("ATI Rezone new PartNum: %s" % (self.dut.partNum))
            objMsg.printMsg("ATI Rezone Waterfall_Req: %s " % (self.dut.Waterfall_Req ))
            self.dut.driveattr['DNGRADE_ON_FLY'] = '%s_%s_%s' % (self.dut.nextOper, self.dut.partNum[-3:], str(ec))
            objMsg.printMsg('DNGRADE_ON_FLY: %s' % (self.dut.driveattr['DNGRADE_ON_FLY']))

#---------------------------------------------------------------------------------------------------------#
class CRdScrn2File(CProcess):
   """
   Class to create and use a SIM file which holds RAW values from READ_SCRN2
   test and later use for TCC Cal using BER.
   """

   def __init__(self):
      """
      @param prm186: T186 input to measure and return head mr resistances
      @param deltaLim: Integer. Absolute value of maximum allowed MR resistance change
      """
      CProcess.__init__(self)
      pcFileName = 'rd_scrn2'
      self.genRdScn2Name = 'RdScn2'
      self.oFSO = CFSO()
      self.oUtility = CUtility()
      self.T231Index = 16
      self.dut = objDut

      self.RdScrn2_Path = os.path.join(ScrCmds.getSystemPCPath(), pcFileName, self.oFSO.getFofFileName(0))
      self.genericRdScrn2Path = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.genRdScn2Name)


   def My_InitAndAllocateSIM(self):
      oFSO = CFSO()
      from AFH_SIM import CAFH_Frames
      frm = CAFH_Frames()

      ######################################
      #  Initialize and Allocate the SPT results file headers
      ######################################
      initHeaderPrm_231 = {'test_num'  : 231,
               'prm_name'  : "Initialize SPT Results file header record",
               'CWORD1'    : 0x08,  #0x08 is init header record
               'PASS_INDEX': objSimArea['HEADER_RECORD'].index,
               'timeout'   : 120
      }
      baseName = "Allocate SPT Results file record: %s"
      allocateSpacePrm_231 = {'test_num'  : 231,
               'prm_name'  : baseName % '',
               'CWORD1'    : 0x10,  #0x10 is allocate space for index
               'PASS_INDEX': 1,
               'DL_FILE_LEN': 0,
               'timeout'   : 120
      }
      #Init Header Record
      frm.mFSO.St(initHeaderPrm_231)

#      record = objSimArea['RD_SCRN2']
#      allocateSpacePrm_231['PASS_INDEX'] = record.index
#      allocateSpacePrm_231['DL_FILE_LEN'] = frm.mFSO.oUtility.ReturnTestCylWord(record.size)
#      allocateSpacePrm_231['FOLDER_NAME'] = record.mct()
#      allocateSpacePrm_231['prm_name'] = baseName % record.name
#      frm.mFSO.St(allocateSpacePrm_231)

      #Allocate space for all records
      for record in objSimArea:
         if not record.index == 0: #Don't re-do the header record
            allocateSpacePrm_231['PASS_INDEX'] = record.index
            allocateSpacePrm_231['DL_FILE_LEN'] = frm.mFSO.oUtility.ReturnTestCylWord(record.size)
            allocateSpacePrm_231['FOLDER_NAME'] = record.mct()
            allocateSpacePrm_231['prm_name'] = baseName % record.name
            frm.mFSO.St(allocateSpacePrm_231)

   def Show_P172_AFH_HEATER(self, tcc_on = 0):
      from Process import CProcess
      oProcess = CProcess()
      if tcc_on == 0:
         cword1 = 4
         objMsg.printMsg("TCC Off")
      else:
         if testSwitch.KARNAK:  # Karnak using trunk code, the configure change
             cword1 = 42
         else:
             cword1 = 36
         objMsg.printMsg("TCC On")
      return self.oFSO.getAFHWorkingAdaptives(1, self.dut.numZones, retrieveData = True, cword1 = cword1)
   """

   ([172], [], {'timeout': 1800.0, 'spc_id': 10001, 'CWORD1': (4,)})
P172_AFH_DH_WORKING_ADAPT:
 HD_PHYS_PSN DATA_ZONE HD_LGC_PSN WRITER_PRE_HEAT WRITER_WRITE_HEAT WRITER_READ_HEAT READER_PRE_HEAT READER_WRITE_HEAT READER_READ_HEAT HTR_PWR_RNG_BIT WRT_CUR WRT_CUR_OVS_AMP WRT_CUR_OVS_DUR MR_BIAS_OFST
           0         0          0              64                56                0               0                 0              101               0       5               3               4            0
           0         1          0              63                54                0               0                 0               98               0       5               3               4            0
           0         2          0              60                54                0               0                 0               96               0       5               3               7            0

   P172_AFH_WORKING_ADAPTS:
   HD_PHYS_PSN DATA_ZONE HD_LGC_PSN PRE_HEAT WRT_HEAT RD_HEAT HTR_PWR_RNG_BIT WRT_CUR WRT_CUR_OVS_AMP WRT_CUR_OVS_DUR MR_BIAS_OFST
           0         0          0       92       81      92               0       7               4               3            0
           0         1          0       90       78      90               0       7               4               3            0
           0         2          0       87       77      87               0       7               4               3            0
           0         3          0       85       74      85               0       7               4               3            0
           0         4          0       84       73      84               0       7               4               3            0
           0         5          0       83       71      83               0       7               4               3            0
   """

   def Get_Current_WriteCD(self):
      """
      Gather writeCD from P135_FINAL_CONTACT table and return as list.
      """

      iMaxHead = self.dut.imaxHead
      numofzone = self.dut.numZones
      # Create an empty table and fill in with actual MR values from test 186
      WCD_List = [0,] * (iMaxHead * (numofzone+1))

      P135_CD_Tbl = []

      P135_CD_Tbl = self.dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()
      List_zone =  []

      for entry in P135_CD_Tbl:
         if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
           if entry.get('ACTIVE_HEATER') == 'W':
             WCD_List_Ofst = (int(entry.get('HD_LGC_PSN'))* numofzone) + int(entry.get('DATA_ZONE'))
             WCD_DAC = int(entry.get('WRT_CNTCT_DAC'))
         else:
            WCD_List_Ofst = (int(entry.get('HD_LGC_PSN'))* numofzone) + int(entry.get('DATA_ZONE'))
            WCD_DAC = int(entry.get('WRT_CNTCT_DAC'))
         if not (int(entry.get('DATA_ZONE')) in  List_zone):
            List_zone.append(int(entry.get('DATA_ZONE')))
         WCD_List[WCD_List_Ofst] = WCD_DAC

      objMsg.printMsg("Get_Current_WriteC %s %s" %(str(WCD_List), str(List_zone)))
      return WCD_List,  List_zone
   def Get_Current_WriteHeat(self, table_AFH_Heater):
      """
      Gather Heater Settings from P172_AFH_HEATER table and return as list.
      """

      iMaxHead = self.dut.imaxHead
      numofzone = self.dut.numZones
      # Create an empty table and fill in with actual MR values from test 186
      WHTR_List = [0,] * (iMaxHead * (numofzone+1))
      #WHTR_List_Total = (iMaxHead * (numofzone+1))
      #objMsg.printMsg("WHTR_List Total Entry = %d" % (WHTR_List_Total))
      for entry in table_AFH_Heater:
         WHTR_List_Ofst = (int(entry.get('HD_LGC_PSN'))* numofzone) + int(entry.get('DATA_ZONE'))
         if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
            WHTR_DAC = int(entry.get('WRITER_WRITE_HEAT'))
         else:
            #WHTR_DAC = int(entry.get('WRT_HEAT_DAC'))
            WHTR_DAC = int(entry.get('WRT_HEAT'))
         #objMsg.printMsg("WHTR_List Offset[%d] = %d" % (WHTR_List_Ofst, WHTR_DAC))
         WHTR_List[WHTR_List_Ofst] = WHTR_DAC

      return WHTR_List

   def Get_Current_ReadHeat(self, table_AFH_Heater):
      """
      Gather Heater Settings from P172_AFH_HEATER table and return as list.
      """
      iMaxHead = self.dut.imaxHead
      numofzone = self.dut.numZones
      # Create an empty table and fill in with actual MR values from test 186
      READHEAT_List = [0,] * (iMaxHead * (numofzone+1))

      for entry in table_AFH_Heater:
         if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
            READHEAT_List[(int(entry.get('HD_LGC_PSN'))* numofzone) + int(entry.get('DATA_ZONE'))] = int(entry.get('READER_READ_HEAT'))
         else:
            #READHEAT_List[(int(entry.get('HD_PHYS_PSN'))* numofzone) + int(entry.get('DATA_ZONE'))] = int(entry.get('RD_HEAT_DAC'))
            READHEAT_List[(int(entry.get('HD_LGC_PSN'))* numofzone) + int(entry.get('DATA_ZONE'))] = int(entry.get('RD_HEAT'))

      return READHEAT_List

   def Get_Current_PreHeat(self, table_AFH_Heater):
      """
      Gather Heater Settings from P172_AFH_HEATER table and return as list.
      """
      iMaxHead = self.dut.imaxHead
      numofzone = self.dut.numZones
      # Create an empty table and fill in with actual MR values from test 186
      PREHEAT_List = [0,] * (iMaxHead * (numofzone+1))

      for entry in table_AFH_Heater:
         if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
            PREHEAT_List[(int(entry.get('HD_LGC_PSN'))* numofzone) + int(entry.get('DATA_ZONE'))] = int(entry.get('WRITER_PRE_HEAT'))
         else:
            #PREHEAT_List[(int(entry.get('HD_PHYS_PSN'))* numofzone) + int(entry.get('DATA_ZONE'))] = int(entry.get('PRE_HEAT_DAC'))
            PREHEAT_List[(int(entry.get('HD_LGC_PSN'))* numofzone) + int(entry.get('DATA_ZONE'))] = int(entry.get('PRE_HEAT'))

      return PREHEAT_List


   def Show_P172_AFH_TC_COEF_2(self,spcID=1):
      from Process import CProcess
      oProcess = CProcess()
      RetrieveTcCoeff_prm = TP.Retrieve_TC_Coeff_Prm_172.copy()
      RetrieveTcCoeff_prm['spc_id'] = spcID
      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
         oProcess.St(RetrieveTcCoeff_prm)
      else:
         oProcess.St(RetrieveTcCoeff_prm)
   """
   P172_AFH_DH_TC_COEF:
   HD_PHYS_PSN HD_LGC_PSN ACTIVE_HEATER THERMAL_CLR_COEF1 THERMAL_CLR_COEF2 ADD_TCS_COLD_DTC ADD_TCS_HOT_DTH COLD_TEMP_DTC HOT_TEMP_DTH
           0          0             R     -0.0011786415      0.0000000000     0.0020651999   -0.0016774000            20           48
           0          0             W     -0.0005000000      0.0000000000     0.0004611000   -0.0022302000            20           48
           1          1             R     -0.0017380255      0.0000000000     0.0020651999   -0.0016774000            20           48
           1          1             W     -0.0005000000      0.0000000000     0.0004611000   -0.0022302000            20           48


   ([172], [], {'timeout': 100, 'spc_id': 1, 'CWORD1': 10})

                       CWORD1         10 (0x000a)
   P172_AFH_TC_COEF_2:
    HD_PHYS_PSN HD_LGC_PSN THERMAL_CLR_COEF1 THERMAL_CLR_COEF2 ADD_TCS_COLD_DTC ADD_TCS_HOT_DTC COLD_TEMP_DTC HOT_TEMP_DTH
              0          0     -0.0014310165      0.0000000000    -0.0009916000   -0.0033900000            20           48
              1          1     -0.0005000000      0.0000000000    -0.0009916000   -0.0033900000            20           48

   P172_AFH_DH_TC_COEF_2:
   HD_PHYS_PSN HD_LGC_PSN TCS_REGION ACTIVE_HEATER THERMAL_CLR_COEF1 THERMAL_CLR_COEF2 ADD_TCS_COLD_DTC ADD_TCS_HOT_DTH COLD_TEMP_DTC HOT_TEMP_DTH
           0          0          0             R     -0.0010441632      0.0000000000     0.0015922331   -0.0009224260            20           48
           0          0          0             W     -0.0001574809      0.0000000000     0.0005111895   -0.0005218855            20           48
           0          0          1             R     -0.0010065048      0.0000000000     0.0015988525   -0.0014325050            20           48
           0          0          1             W      0.0002936348      0.0000000000     0.0006699025   -0.0008499757            20           48
           0          0          2             R     -0.0011811024      0.0000000000     0.0014571093   -0.0012229475            20           48
           0          0          2             W     -0.0005751459      0.0000000000     0.0006518133   -0.0008871605            20           48
           0          0          3             R     -0.0009808295      0.0000000000     0.0011653424   -0.0009948848            20           48
           0          0          3             W      0.0001628480      0.0000000000     0.0006109742   -0.0009441903            20           48
           0          0          4             R     -0.0009192047      0.0000000000     0.0011246490   -0.0009430114            20           48
           0          0          4             W     -0.0000000000      0.0000000000     0.0005338927   -0.0009394275            20           48
           1          1          0             R     -0.0020540913      0.0000000000     0.0015922331   -0.0009224260            20           48
           1          1          0             W     -0.0016175963      0.0000000000     0.0005111895   -0.0005218855            20           48
           1          1          1             R     -0.0012529952      0.0000000000     0.0015988525   -0.0014325050            20           48
           1          1          1             W     -0.0019702159      0.0000000000     0.0006699025   -0.0008499757            20           48
           1          1          2             R     -0.0021071550      0.0000000000     0.0014571093   -0.0012229475            20           48
           1          1          2             W     -0.0017442651      0.0000000000     0.0006518133   -0.0008871605            20           48
           1          1          3             R     -0.0020061627      0.0000000000     0.0011653424   -0.0009948848            20           48
           1          1          3             W     -0.0022937357      0.0000000000     0.0006109742   -0.0009441903            20           48
           1          1          4             R     -0.0017767885      0.0000000000     0.0011246490   -0.0009430114            20           48
           1          1          4             W     -0.0025574155      0.0000000000     0.0005338927   -0.0009394275            20           48
           2          2          0             R     -0.0014412870      0.0000000000     0.0015922331   -0.0009224260            20           48
           2          2          0             W     -0.0006881214      0.0000000000     0.0005111895   -0.0005218855            20           48
           2          2          1             R     -0.0012632661      0.0000000000     0.0015988525   -0.0014325050            20           48
           2          2          1             W     -0.0001489209      0.0000000000     0.0006699025   -0.0008499757            20           48
           2          2          2             R     -0.0017391301      0.0000000000     0.0014571093   -0.0012229475            20           48
           2          2          2             W     -0.0012016426      0.0000000000     0.0006518133   -0.0008871605            20           48
           2          2          3             R     -0.0013026362      0.0000000000     0.0011653424   -0.0009948848            20           48
           2          2          3             W     -0.0002755908      0.0000000000     0.0006109742   -0.0009441903            20           48
           2          2          4             R     -0.0012735374      0.0000000000     0.0011246490   -0.0009430114            20           48
           2          2          4             W     -0.0002887137      0.0000000000     0.0005338927   -0.0009394275            20           48
           3          3          0             R     -0.0013471415      0.0000000000     0.0015922331   -0.0009224260            20           48
           3          3          0             W      0.0001369391      0.0000000000     0.0005111895   -0.0005218855            20           48
           3          3          1             R     -0.0003183840      0.0000000000     0.0015988525   -0.0014325050            20           48
           3          3          1             W      0.0004809991      0.0000000000     0.0006699025   -0.0008499757            20           48
           3          3          2             R     -0.0012204725      0.0000000000     0.0014571093   -0.0012229475            20           48
           3          3          2             W     -0.0004108172      0.0000000000     0.0006518133   -0.0008871605            20           48
           3          3          3             R     -0.0013916467      0.0000000000     0.0011653424   -0.0009948848            20           48
           3          3          3             W      0.0001403638      0.0000000000     0.0006109742   -0.0009441903            20           48
           3          3          4             R     -0.0013505648      0.0000000000     0.0011246490   -0.0009430114            20           48
           3          3          4             W     -0.0000000000      0.0000000000     0.0005338927   -0.0009394275            20           48


   tdk

   P172_AFH_TC_COEF_3:
   HD_PHYS_PSN HD_LGC_PSN TCS_REGION THERMAL_CLR_COEF1 THERMAL_CLR_COEF2 ADD_TCS_COLD_DTC ADD_TCS_HOT_DTC COLD_TEMP_DTC HOT_TEMP_DTH
           0          0          0     -0.0010000000      0.0000000000     0.1121823937   -0.2981031835            20           48
           0          0          1     -0.0010000000      0.0000000000     0.1498644352   -0.4046277106            20           48
           0          0          2     -0.0010000000      0.0000000000     0.1259925961   -0.3440445065            20           48
           0          0          3     -0.0010000000      0.0000000000     0.1371403188   -0.2366655171            20           48
           0          0          4     -0.0012385175      0.0000000000     0.1172693521   -0.1853450388            20           48
           1          1          0     -0.0010000000      0.0000000000     0.1121823937   -0.2981031835            20           48
           1          1          1     -0.0010000000      0.0000000000     0.1498644352   -0.4046277106            20           48
           1          1          2     -0.0010000000      0.0000000000     0.1259925961   -0.3440445065            20           48
           1          1          3     -0.0010000000      0.0000000000     0.1371403188   -0.2366655171            20           48
           1          1          4     -0.0014327279      0.0000000000     0.1172693521   -0.1853450388            20           48
           2          2          0     -0.0010000000      0.0000000000     0.1121823937   -0.2981031835            20           48
           2          2          1     -0.0010000000      0.0000000000     0.1498644352   -0.4046277106            20           48
           2          2          2     -0.0010000000      0.0000000000     0.1259925961   -0.3440445065            20           48
           2          2          3     -0.0010000000      0.0000000000     0.1371403188   -0.2366655171            20           48
           2          2          4     -0.0008832592      0.0000000000     0.1172693521   -0.1853450388            20           48
           3          3          0     -0.0010000000      0.0000000000     0.1121823937   -0.2981031835            20           48
           3          3          1     -0.0010000000      0.0000000000     0.1498644352   -0.4046277106            20           48
           3          3          2     -0.0010000000      0.0000000000     0.1259925961   -0.3440445065            20           48
           3          3          3     -0.0010000000      0.0000000000     0.1371403188   -0.2366655171            20           48
           3          3          4     -0.0010441632      0.0000000000     0.1172693521   -0.1853450388            20           48

   """

   def Get_Current_TCC1(self ,spcID=1):
      """
      Gather Heater Settings from P172_AFH_HEATER table and return as list.
      """
      iMaxHead = self.dut.imaxHead
      numofzone = self.dut.numZones
      # Create an empty table and fill in with actual MR values from test 186
      if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
         tcc1_List   = [0,]*iMaxHead
         tcc1_List_R = [0,]*iMaxHead
         tcc1_List_W = [0,]*iMaxHead
      else:
         tcc1_List     = [[0 for i in range(len(TP.TCS_WARP_ZONES))] for j in range(iMaxHead)]
         tcc1_List_R   = [[0 for i in range(len(TP.TCS_WARP_ZONES))] for j in range(iMaxHead)]
         tcc1_List_W   = [[0 for i in range(len(TP.TCS_WARP_ZONES))] for j in range(iMaxHead)]

      P172_AFH_DH_TC_COEF_Tbl   = []
      P172_AFH_TC_COEF_2_Tbl    = []

      P172_AFH_DH_TC_COEF_2_Tbl = []
      P172_AFH_TC_COEF_3_Tbl    = []
      #P172_HTR_Tbl = self.dut.dblData.Tables('P172_AFH_HEATER').tableDataObj()
      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT: # RHO
         if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
            P172_AFH_DH_TC_COEF_Tbl = self.dut.dblData.Tables('P172_AFH_DH_TC_COEF').tableDataObj()
            objMsg.printMsg("P172_AFH_DH_TC_COEF_Tbl %s" % (str(P172_AFH_DH_TC_COEF_Tbl)))
            for entry in P172_AFH_DH_TC_COEF_Tbl:
               if entry.get('ACTIVE_HEATER') == 'R':
                  tcc1_List_R[int(entry.get('HD_LGC_PSN'))] = float(entry.get('THERMAL_CLR_COEF1'))
               else:
                  tcc1_List_W[int(entry.get('HD_LGC_PSN'))] = float(entry.get('THERMAL_CLR_COEF1'))
         else:
            P172_AFH_DH_TC_COEF_2_Tbl = self.dut.dblData.Tables('P172_AFH_DH_TC_COEF_2').chopDbLog('SPC_ID', 'match',str(spcID))             #tableDataObj()
            #objMsg.printMsg("P172_AFH_DH_TC_COEF_2_Tbl %s" % (str(P172_AFH_DH_TC_COEF_2_Tbl)))
            for entry in P172_AFH_DH_TC_COEF_2_Tbl:
               if entry.get('ACTIVE_HEATER') == 'R':
                  tcc1_List_R[int(entry.get('HD_LGC_PSN'))][int(entry.get('TCS_REGION'))] = float(entry.get('THERMAL_CLR_COEF1'))
               else:
                  tcc1_List_W[int(entry.get('HD_LGC_PSN'))][int(entry.get('TCS_REGION'))] = float(entry.get('THERMAL_CLR_COEF1'))
      else:                                                                     # TDK
         if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
            P172_AFH_TC_COEF_2_Tbl = self.dut.dblData.Tables('P172_AFH_TC_COEF_2').tableDataObj()
            objMsg.printMsg("P172_AFH_TC_COEF_2_Tbl %s" % (str(P172_AFH_TC_COEF_2_Tbl)))
            for entry in P172_AFH_TC_COEF_2_Tbl:
               tcc1_List[int(entry.get('HD_LGC_PSN'))] = float(entry.get('THERMAL_CLR_COEF1'))
         else:
            P172_AFH_TC_COEF_3_Tbl = self.dut.dblData.Tables('P172_AFH_TC_COEF_3').tableDataObj()
            objMsg.printMsg("P172_AFH_TC_COEF_3_Tbl %s" % (str(P172_AFH_TC_COEF_3_Tbl)))
            for entry in P172_AFH_TC_COEF_3_Tbl:
               tcc1_List[int(entry.get('HD_LGC_PSN'))][int(entry.get('TCS_REGION'))] = float(entry.get('THERMAL_CLR_COEF1'))

      if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
         return tcc1_List_R, tcc1_List_W
      else:
         return tcc1_List

   def Save_RD_SCRN2_RAW(self, spcid=0):
      Array_RdScrn2_P250 = self.Gather_RD_SCRN2_RAW(spcid=spcid)
      self.arrayToFile(Array_RdScrn2_P250)
      self.fileToDisc()

   def Save_FineOpti_BER(self):
      Array_RdScrn2_P250 = self.Gather_FineOpti_BER()
      self.arrayToFile(Array_RdScrn2_P250)

   def Retrieve_FINEOPTI_RAW(self, dumpData = True):
      # Get the original resistance values
      ogPcPath = self.SimToPcFile()
      file = open(ogPcPath,'r')
      Array_FineOpti = array('f', file.read())
      List_FineOpti_phy_head = Array_FineOpti.tolist()
      List_FineOpti_log_head = []
      objMsg.printMsg("self.dut.LgcToPhysHdMap %s"%(str(self.dut.LgcToPhysHdMap)))

      iMaxHead = self.dut.imaxHead
      numofzone = self.dut.numZones
      for head in range(iMaxHead):
         physical_head = self.dut.LgcToPhysHdMap[head]
         objMsg.printMsg("physical_head %s"%(str(physical_head)))
         for izone in range(numofzone):
            List_FineOpti_log_head.append(List_FineOpti_phy_head[(physical_head*numofzone) + izone])
            if dumpData:
                objMsg.printMsg("FineOpti BER: H[%d] Zn[%d] RRAW=%4.2f" % (head, izone, List_FineOpti_phy_head[(physical_head*numofzone) + izone]))

      return List_FineOpti_log_head

   def Retrieve_RD_SCRN2_RAW(self, dumpData = 0):
      List_RdScrn2_log_head  = [[] for hd in xrange(self.dut.imaxHead)]

      for head in range(self.dut.imaxHead):
         physical_head = self.dut.LgcToPhysHdMap[head]
         List_RdScrn2_log_head[head] = self.Retrieve_RD_SCRN2_RAW_byPhyHd(physical_head, dumpData)

      return List_RdScrn2_log_head

   if testSwitch.virtualRun: #virtual run return dummy data 
      def Retrieve_RD_SCRN2_RAW_byPhyHd(self, physical_head=0, dumpData = 0):
         import dbLogUtilities
         List_RdScrn2_phy_head = []
         table_T250 = dbLogUtilities.DBLogReader(self.dut, 'P250_ERROR_RATE_BY_ZONE')
         rows = table_T250.getRows({'HD_PHYS_PSN': physical_head, 'SPC_ID' : TP.RdScrn2_SPC_ID})
         for row in rows:
            List_RdScrn2_phy_head.append(float(row['RAW_ERROR_RATE']))
         if dumpData:
            for izone in range(self.dut.numZones):
               objMsg.printMsg("PhyH%d Zn%d RRAW=%4.2f" % \
                  (physical_head, izone, List_RdScrn2_phy_head[izone]))
         return List_RdScrn2_phy_head
   else: 
      def Retrieve_RD_SCRN2_RAW_byPhyHd(self, physical_head=0, dumpData = 0):
         ogPcPath = self.SimToPcFile()
         file = open(ogPcPath,'r')
         Array_RdScrn2 = array('f', file.read())

         List_RdScrn2_phy_head = Array_RdScrn2.tolist()   # data by physical head

         if dumpData:
            for izone in range(self.dut.numZones):
               objMsg.printMsg("PhyH%d Zn%d RRAW=%4.2f" % (physical_head, izone, List_RdScrn2_phy_head[(physical_head*self.dut.numZones) + izone]))

         return List_RdScrn2_phy_head[physical_head*self.dut.numZones : (physical_head+1)*self.dut.numZones]
   
   def Gather_RD_SCRN2_RAW(self, dumpData = 0, spcid=0):
      """
      Gather MR values from P186_BIAS_CAL table and return as an array object.
      """
      if not spcid:
         RawTable =  self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
      else:
         RawTable = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match', str(spcid))
      numPhysHds = len(self.dut.PhysToLgcHdMap) # get number of physical head

      if dumpData:
         objMsg.printMsg("self.dut.PhysToLgcHdMap =%s" % str(self.dut.PhysToLgcHdMap ))
         objMsg.printMsg("numPhysHds =%s" % str(numPhysHds ))

      iMaxHead = numPhysHds  #self.dut.imaxHead
      numofzone = self.dut.numZones

      # Create an empty table and fill in with actual MR values from test 186
      tmp_List = [1,] * (iMaxHead * numofzone)

      for head in range(iMaxHead):
          for tableofs in range(len(RawTable)):
              if (RawTable[ tableofs ] ['ERROR_RATE_TYPE'].strip() !=  'SECTOR') and \
                 (RawTable[ tableofs ] ['ERROR_RATE_TYPE'].strip() !=  'BITERR') and \
                 (RawTable[ tableofs ] ['ERROR_RATE_TYPE'].strip() !=  'SYMBOL') : continue
              if int(RawTable[ tableofs ] ['SPC_ID']) !=  2 : continue
              if int(RawTable[ tableofs ] ['HD_PHYS_PSN']) !=  head : continue
              #if int(RawTable[ tableofs ] ['HD_LGC_PSN']) !=  head : continue

              myHead = int(RawTable[ tableofs ] ['HD_PHYS_PSN'])
              #myHead = int(RawTable[ tableofs ] ['HD_LGC_PSN'])
              myZone = int(RawTable[ tableofs ] ['DATA_ZONE'])
              myTrack = int(RawTable[ tableofs ] ['START_TRK_NUM'])
              mySPCID = int(RawTable[ tableofs ] ['SPC_ID'])
              myRRAW = float(RawTable[ tableofs ] ['RAW_ERROR_RATE'])

              if dumpData: objMsg.printMsg("H[%d] Zn[%d] Trk[%d] SPCID[%d] RRAW=%4.2f" % (myHead, myZone, myTrack, mySPCID, myRRAW))

              tmp_List[(myHead * numofzone) + myZone] = myRRAW

      tmp_Array = array('f', tmp_List)

      return tmp_Array

   def Gather_FineOpti_BER(self):
      """
      Gather Fine_opti BER from P250_ERROR_RATE_BY_ZONE and return as an array object.
      """
      RawTable =  self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
      numPhysHds = len(self.dut.PhysToLgcHdMap) # get number of physical head
      objMsg.printMsg("self.dut.PhysToLgcHdMap =%s" % str(self.dut.PhysToLgcHdMap ))
      objMsg.printMsg("numPhysHds =%s" % str(numPhysHds ))
      iMaxHead = numPhysHds #self.dut.imaxHead
      numofzone = self.dut.numZones

      # Create an empty table and fill in with actual MR values from test 186
      tmp_List = [0,] * (iMaxHead * numofzone)

      for head in range(iMaxHead):
          for tableofs in range(len(RawTable)):
              if (RawTable[ tableofs ] ['ERROR_RATE_TYPE'].strip() !=  'BITERR'): continue
              if self.dut.nextState != 'FINE_OPTI':  continue
              if int(RawTable[ tableofs ] ['SPC_ID']) !=  6 : continue
              if int(RawTable[ tableofs ] ['HD_PHYS_PSN']) !=  head : continue

              myHead = int(RawTable[ tableofs ] ['HD_PHYS_PSN'])
              myZone = int(RawTable[ tableofs ] ['DATA_ZONE'])
              myTrack = int(RawTable[ tableofs ] ['START_TRK_NUM'])
              mySPCID = int(RawTable[ tableofs ] ['SPC_ID'])
              myRRAW = float(RawTable[ tableofs ] ['RAW_ERROR_RATE'])

              objMsg.printMsg("H[%d] Zn[%d] Trk[%d] SPCID[%d] RRAW=%4.2f" % (myHead, myZone, myTrack, mySPCID, myRRAW))

              tmp_List[(myHead * numofzone) + myZone] = myRRAW

      tmp_Array = array('f', tmp_List)

      return tmp_Array

   def SimToPcFile(self):
      """
      Pull the MR resitance SIM file and place it in a pcfile.  Return the path
      to the pcfile.
      """
      record = objSimArea['RD_SCRN2']
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
      else:
         path = os.path.join('.', self.genericRdScrn2Path)
      return path

   def arrayToFile(self, array):
      """
      Write the array object to the pcfile
      """
      RdScrn2P250File = GenericResultsFile(self.genRdScn2Name)
      RdScrn2P250File.open('w')
      arStr = array.tostring()  # GenericResultsFile won't work with arrays, so we have to output to a string instead
      RdScrn2P250File.write(arStr)
      RdScrn2P250File.close()

   def fileToDisc(self):
      """
      Write the file containing MR resistance values to disc, using test 231.
      """
      record = objSimArea['RD_SCRN2']

      # First, look for the generic results file that is created in MDW cals.  If
      #  that is not there, assume that we have a pcfile that can be written to disc
      if os.path.exists(self.genericRdScrn2Path):
         filePath = self.genericRdScrn2Path
      elif os.path.exists(self.RdScrn2_Path):
      #if os.path.exists(self.RdScrn2_Path):
         filePath = self.RdScrn2_Path
      else:
         ScrCmds.raiseException(11044, "Read Screen2 P250 File does not exist")


      #Write data to drive SIM
      objMsg.printMsg("Saving Rd Scrn2 P250 File to drive SIM.  File Path: %s" % filePath, objMsg.CMessLvl.DEBUG)
      self.oFSO.saveResultsFileToDrive(1, filePath, 0, record, 1)

      #Verify data on drive SIM
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
         file = open(path,'rb')
         try:
            file.seek(0,2)  # Seek to the end
            fileLength = file.tell()
         finally:
            file.close()
         objMsg.printMsg("Re-Read of drive SIM File %s had size %d" % (record.name,fileLength), objMsg.CMessLvl.DEBUG)
         if fileLength == 0:
            ScrCmds.raiseException(11044, "Drive Rd Scrn2 P250 SIM readback of 0 size.")

class CSkipZnFile(CProcess):
   """
   Class to create and use a SIM file which holds SkipZone from PRE_SKIPZN
   """

   def __init__(self):
      CProcess.__init__(self)
      pcFileName = 'skip_zn'
      self.genSkipZnName = 'SkipZn'
      self.oFSO = CFSO()
      self.oUtility = CUtility()
      self.T231Index = 24
      self.dut = objDut

      self.SkipZn_Path = os.path.join(ScrCmds.getSystemPCPath(), pcFileName, self.oFSO.getFofFileName(0))
      self.genericSkipZnPath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.genSkipZnName)

   def Save_SKIPZN(self, Skznlist):
      skipznToSim  = []
      for i in range(len(Skznlist)):
         skipznToSim.append(((Skznlist[i][0] & 0xff) <<8 | (Skznlist[i][1] & 0xff)))   # head, zone
      objMsg.printMsg("skipznToSim: %s" % skipznToSim)

      Array_SkipZn = array('H', skipznToSim)
      self.arrayToFile(Array_SkipZn)
      self.fileToDisc()

   def Retrieve_SKIPZN(self, dumpData = 0):
      ogPcPath = self.SimToPcFile()
      file = open(ogPcPath,'r')
      Array_Skipzn = array('H', file.read())
      List_Skipzn = Array_Skipzn.tolist()
      FinalSkzn = []

      if dumpData:
         objMsg.printMsg("List_Skipzn =  %s"%(List_Skipzn))

      for i in range(len(List_Skipzn)):
         head = List_Skipzn[i] >> 8
         zone = List_Skipzn[i] & 0x00FF
         FinalSkzn.append((head,zone))
      objMsg.printMsg("FinalSkzn =  %s"%(FinalSkzn))

      return FinalSkzn

   def SimToPcFile(self):
      """
      Pull the SIM file and place it in a pcfile.  Return the path to the pcfile.
      """
      record = objSimArea['PRE_SKIPZN']
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
      else:
         path = os.path.join('.', self.genericSkipZnPath)
      return path

   def arrayToFile(self, array):
      SkipZnFile = GenericResultsFile(self.genSkipZnName)
      SkipZnFile.open('w')
      arStr = array.tostring()  # GenericResultsFile won't work with arrays, so we have to output to a string instead
      SkipZnFile.write(arStr)
      SkipZnFile.close()

   def fileToDisc(self):
      record = objSimArea['PRE_SKIPZN']

      # First, look for the generic results file that is created in MDW cals.  If
      #  that is not there, assume that we have a pcfile that can be written to disc
      if os.path.exists(self.genericSkipZnPath):
         filePath = self.genericSkipZnPath
      elif os.path.exists(self.SkipZn_Path):
         filePath = self.SkipZn_Path
      else:
         ScrCmds.raiseException(11044, "Skip Zone File does not exist")

      #Write data to drive SIM
      objMsg.printMsg("Saving Skip Zone File to drive SIM. File Path: %s" % filePath, objMsg.CMessLvl.DEBUG)
      self.oFSO.saveResultsFileToDrive(1, filePath, 0, record, 1)

      #Verify data on drive SIM
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
         file = open(path,'rb')
         try:
            file.seek(0,2)  # Seek to the end
            fileLength = file.tell()
         finally:
            file.close()
         objMsg.printMsg("Re-Read of drive SIM File %s has size %d" % (record.name,fileLength), objMsg.CMessLvl.DEBUG)
         if fileLength == 0:
            ScrCmds.raiseException(11044, "Drive Skip Zone SIM readback of 0 size.")

# For Sigmund In Factory to store and restore the bpi_by-head.bin to and from system area by Test 231.
class CSifBpiBinFile(CProcess):
   """
   Class to create and use a SIM file which holds bpi.bin from Sigmund in factory
   """

   def __init__(self):
      CProcess.__init__(self)
      pcFileName = objSimArea['SIF'].name
      self.genSifName = objSimArea['SIF'].name
      self.oFSO = CFSO()
      self.oUtility = CUtility()
      self.dut = objDut

      self.sif_Path = os.path.join(ScrCmds.getSystemPCPath(), pcFileName, self.oFSO.getFofFileName(0))
      self.genericSifPath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.genSifName)

   def Save_SifBpiBin_To_Disc(self):
      self.fileToDisc()

   def Retrieve_SifBpiBin_From_Disc(self):
      ogPcPath = self.SimToPcFile()


   def SimToPcFile(self):
      """
      Pull the SIM file and place it in a pcfile.  Return the path to the pcfile.
      """
      record = objSimArea['SIF']
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
      else:
         path = os.path.join('.', self.genericSifPath)
      return path

   def arrayToFile(self, array):
      SkipZnFile = GenericResultsFile(self.genSifName)
      SkipZnFile.open('w')
      arStr = array.tostring()  # GenericResultsFile won't work with arrays, so we have to output to a string instead
      SkipZnFile.write(arStr)
      SkipZnFile.close()

   def fileToDisc(self):
      record = objSimArea['SIF']

      # First, look for the generic results file that is created in SIF_CAL.  If
      #  that is not there, assume that we have a pcfile that can be written to disc
      if os.path.exists(self.genericSifPath):
         filePath = self.genericSifPath
      elif os.path.exists(self.sif_Path):
         filePath = self.sif_Path
      else:
         ScrCmds.raiseException(11044, "Sif Bpi bin File does not exist")

      #Write data to drive SIM
      objMsg.printMsg("Saving Sif Bpi.bin File to drive SIM. File Path: %s" % filePath, objMsg.CMessLvl.DEBUG)
      self.oFSO.saveResultsFileToDrive(1, filePath, 0, record, 1)

      #Verify data on drive SIM
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
         file = open(path,'rb')
         try:
            file.seek(0,2)  # Seek to the end
            fileLength = file.tell()
         finally:
            file.close()
         objMsg.printMsg("Re-Read of drive SIM File %s has size %d" % (record.name,fileLength), objMsg.CMessLvl.DEBUG)
         if fileLength == 0:
            ScrCmds.raiseException(11044, "Drive Skip Zone SIM readback of 0 size.")

class CAdjBpiFile(CProcess):
   """
   Class to create and use a SIM file which hold ADJ_BPI_FOR_TPI file
   """

   def __init__(self):
      CProcess.__init__(self)
      pcFileName = objSimArea['ADJ_BPI_TPI_FILE'].name
      self.genAdj_BPI_Name = objSimArea['ADJ_BPI_TPI_FILE'].name
      self.oFSO = CFSO()
      self.oUtility = CUtility()
      self.dut = objDut

      self.adj_Bpi_Path = os.path.join(ScrCmds.getSystemPCPath(), pcFileName, self.oFSO.getFofFileName(0))
      self.genericAdjBpiPath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.genAdj_BPI_Name)

   def SimToPcFile(self):
      """
      Pull the SIM file and place it in a pcfile.  Return the path to the pcfile.
      """
      record = objSimArea['ADJ_BPI_TPI_FILE']
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
      else:
         path = os.path.join('.', self.genAdj_BPI_Name)
      return path

   def arrayToFile(self, array):
      adj_bpiFile = GenericResultsFile(self.genAdj_BPI_Name)
      adj_bpiFile.open('w')
      arStr = array.tostring()  # GenericResultsFile won't work with arrays, so we have to output to a string instead
      adj_bpiFile.write(arStr)
      adj_bpiFile.close()

   def fileToDisc(self):
      record = objSimArea['ADJ_BPI_TPI_FILE']

      # First, look for the generic results file that is created in SIF_CAL.  If
      #  that is not there, assume that we have a pcfile that can be written to disc
      if os.path.exists(self.genericAdjBpiPath):
         filePath = self.genericAdjBpiPath
      elif os.path.exists(self.adj_Bpi_Path):
         filePath = self.adj_Bpi_Path
      else:
         ScrCmds.raiseException(11044, "Adj Bpi File does not exist")

      #Write data to drive SIM
      objMsg.printMsg("Saving ADJ_BPI_FOR_TPI to drive SIM. File Path: %s" % filePath, objMsg.CMessLvl.DEBUG)
      self.oFSO.saveResultsFileToDrive(1, filePath, 0, record, 1)

      #Verify data on drive SIM
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
         file = open(path,'rb')
         try:
            file.seek(0,2)  # Seek to the end
            fileLength = file.tell()
         finally:
            file.close()
         objMsg.printMsg("Re-Read of drive SIM File %s has size %d" % (record.name,fileLength), objMsg.CMessLvl.DEBUG)
         if fileLength == 0:
            ScrCmds.raiseException(11044, "Drive Skip Zone SIM readback of 0 size.")
            
#---------------------------------------------------------------------------------------------------------#
class CBPIPMAXFile(CProcess):
   """
   Class to create and use a SIM file which hold BPIP_MAX file
   """
   
   def __init__(self):
      CProcess.__init__(self)
      pcFileName = objSimArea['BPIP_MAX_FILE'].name
      self.genBPIPMAXName = objSimArea['BPIP_MAX_FILE'].name
      self.oFSO = CFSO()
      self.oUtility = CUtility()
      self.dut = objDut
      self.BPIPMAX_Path = os.path.join(ScrCmds.getSystemPCPath(), pcFileName, self.oFSO.getFofFileName(0))
      self.genericBPIPMAXPath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.genBPIPMAXName)
      
   def Save_BPIPMAX(self, BPIP_MAX_list):
      tmp_Array = array('f', BPIP_MAX_list)
      self.arrayToFile(tmp_Array)
      self.fileToDisc()
      
   def Retrieve_BPIPMAX(self):
      ogPcPath = self.SimToPcFile()
      file = open(ogPcPath,'r')
      tmp_Array = array('f', file.read())
      List_BPIPMAX = tmp_Array.tolist()
      objMsg.printMsg("Retrieved BPIP_MAX_list %s" %(List_BPIPMAX))
      
   def SimToPcFile(self):
      """
      Pull the SIM file and place it in a pcfile.  Return the path to the pcfile.
      """
      record = objSimArea['BPIP_MAX_FILE']
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
      else:
         path = os.path.join('.', self.genBPIPMAXName)
      return path
   
   def arrayToFile(self, array):
      BPIPMAXFile = GenericResultsFile(self.genBPIPMAXName)
      BPIPMAXFile.open('w')
      arStr = array.tostring()  # GenericResultsFile won't work with arrays, so we have to output to a string instead
      BPIPMAXFile.write(arStr)
      BPIPMAXFile.close()
      
   def fileToDisc(self):
      record = objSimArea['BPIP_MAX_FILE']
      
      # First, look for the generic results file that is created in SIF_CAL.  If
      #  that is not there, assume that we have a pcfile that can be written to disc
      if os.path.exists(self.genericBPIPMAXPath):
         filePath = self.genericBPIPMAXPath
      elif os.path.exists(self.BPIPMAX_Path):
         filePath = self.BPIPMAX_Path
      else:
         ScrCmds.raiseException(11044, "BPIP_MAX File does not exist")
         
      # Write data to drive SIM
      objMsg.printMsg("Saving BPIP_MAX to drive SIM. File Path: %s" % filePath, objMsg.CMessLvl.DEBUG)
      self.oFSO.saveResultsFileToDrive(1, filePath, 0, record, 1)
      
      # Verify data on drive SIM
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
         file = open(path,'rb')
         try:
            file.seek(0,2)  # Seek to the end
            fileLength = file.tell()
         finally:
            file.close()
         objMsg.printMsg("Re-Read of drive SIM File %s has size %d" % (record.name,fileLength), objMsg.CMessLvl.DEBUG)
         if fileLength == 0:
            ScrCmds.raiseException(11044, "Drive BPIP_MAX SIM readback of 0 size.")

#---------------------------------------------------------------------------------------------------------#
class CNOMFREQFile(CProcess):
   """
   Class to create and use a SIM file which hold NOM_FREQ file
   """
   
   def __init__(self):
      CProcess.__init__(self)
      pcFileName = objSimArea['NOM_FREQ_FILE'].name
      self.genNOMFREQName = objSimArea['NOM_FREQ_FILE'].name
      self.oFSO = CFSO()
      self.oUtility = CUtility()
      self.dut = objDut
      self.NOMFREQ_Path = os.path.join(ScrCmds.getSystemPCPath(), pcFileName, self.oFSO.getFofFileName(0))
      self.genericNOMFREQPath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.genNOMFREQName)
      
   def Save_NOMFREQ(self, NOM_FREQ_list):
      tmp_Array = array('L', NOM_FREQ_list)  # 'L' 4 bytes
      self.arrayToFile(tmp_Array)
      self.fileToDisc()
      
   def Retrieve_NOMFREQ(self):
      ogPcPath = self.SimToPcFile()
      file = open(ogPcPath,'r')
      tmp_Array = array('L', file.read())
      List_NOMFREQ = tmp_Array.tolist()
      objMsg.printMsg("Retrieved NOM_FREQ_list %s" %(List_NOMFREQ))
      
   def SimToPcFile(self):
      """
      Pull the SIM file and place it in a pcfile.  Return the path to the pcfile.
      """
      record = objSimArea['NOM_FREQ_FILE']
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
      else:
         path = os.path.join('.', self.genNOMFREQName)
      return path
   
   def arrayToFile(self, array):
      NOMFREQFile = GenericResultsFile(self.genNOMFREQName)
      NOMFREQFile.open('w')
      arStr = array.tostring()  # GenericResultsFile won't work with arrays, so we have to output to a string instead
      NOMFREQFile.write(arStr)
      NOMFREQFile.close()
      
   def fileToDisc(self):
      record = objSimArea['NOM_FREQ_FILE']
      
      # First, look for the generic results file that is created in SIF_CAL.  If
      #  that is not there, assume that we have a pcfile that can be written to disc
      if os.path.exists(self.genericNOMFREQPath):
         filePath = self.genericNOMFREQPath
      elif os.path.exists(self.NOMFREQ_Path):
         filePath = self.NOMFREQ_Path
      else:
         ScrCmds.raiseException(11044, "NOM_FREQ File does not exist")
         
      # Write data to drive SIM
      objMsg.printMsg("Saving NOM_FREQ to drive SIM. File Path: %s" % filePath, objMsg.CMessLvl.DEBUG)
      self.oFSO.saveResultsFileToDrive(1, filePath, 0, record, 1)
      
      # Verify data on drive SIM
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
         file = open(path,'rb')
         try:
            file.seek(0,2)  # Seek to the end
            fileLength = file.tell()
         finally:
            file.close()
         objMsg.printMsg("Re-Read of drive SIM File %s has size %d" % (record.name,fileLength), objMsg.CMessLvl.DEBUG)
         if fileLength == 0:
            ScrCmds.raiseException(11044, "Drive NOM_FREQ SIM readback of 0 size.")

#---------------------------------------------------------------------------------------------------------#
class CMrResFile(CProcess):
   """
   Class to create and use a SIM file which holds MR resistance values from
   test and compare against values gathered later.  Since the initial values
   are saved in a SIM file, differences can be measured across operations.
   """

   def __init__(self, prm186, deltaLim, simKeyName='MR_RES'):
      """
      @param prm186: T186 input to measure and return head mr resistances
      @param deltaLim: Integer. Absolute value of maximum allowed MR resistance change
      """
      CProcess.__init__(self)
      if not testSwitch.extern.FE_0125575_357552_SAVE_GMR_RES_RANGE_TO_SIM:
         pcFileName = objSimArea[simKeyName].name
         self.genResName = objSimArea[simKeyName].name
         self.oFSO = CFSO()
         self.t231Index = 12

         self.mrResPath = os.path.join(ScrCmds.getSystemPCPath(), pcFileName, self.oFSO.getFofFileName(0))
         self.genericMRResPath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.genResName)
         self.prm186 = prm186
         if getattr(TP, 'bgSTD', 0) == 1:
            self.deltaMRLim = deltaLim*2
         else:
            self.deltaMRLim = deltaLim

      else:
         self.oFSO = CFSO()

         self.simRecord = objSimArea[simKeyName]
         self.mrResPath = os.path.join(ScrCmds.getSystemPCPath(), self.simRecord.name, self.oFSO.getFofFileName(0))
         self.genericMRResPath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.simRecord.name)

         self.prm186 = prm186
         if getattr(TP, 'bgSTD', 0) == 1:
            self.deltaMRLim = deltaLim*2
         else:
            self.deltaMRLim = deltaLim

   def saveToGenResFile(self):
      """
      Gather MR values and save them to a SIM file.  This method assumes
      that T186 has already been run.
      """
      mrArray = self.gatherMRValues()
      self.arrayToFile(mrArray)

   def diffMRValues(self, mrOGfromSIM = True):
      """
      Get the original MR values from the SIM file, and compare those with the
      current MR values.  If the difference is too large, raise an error.
      """
      if testSwitch.RUN_VBIAS_T186:
         CServoOpti().setePreampBiasMode(enable = True)    # switch to Current Bias mode

      # Get the original resistance values
      if mrOGfromSIM:                        # Pull previous MR vaules from SIM file
         ogPcPath = self.simToPcFile()
         file = open(ogPcPath,'r')
         mrArrayOG = array('f', file.read())
      else:                                  # No need to pull from SIM - just collect data from table
         mrArrayOG = self.gatherMRValues()
      mrListOG = mrArrayOG.tolist()

      # Run T186 and collect current MR resistance values
      self.St(self.prm186)
      mrArrayNew = self.gatherMRValues()
      mrListNew = mrArrayNew.tolist()

      objMsg.printMsg("Original MR resitances by head: %s" % mrListOG)
      objMsg.printMsg("Current MR resitances by head: %s" % mrListNew)

      # Difference the values
      mrDiff = []
      mrDiffPercent = []
      #Both the current and reference should be a #physical heads reference
      # but we should only diff for valid current logical heads
      for head in xrange(self.dut.imaxHead):
         physHead = self.dut.LgcToPhysHdMap[head]
         mrDiff.append(mrListNew[physHead] - mrListOG[physHead])
         mrDiffPercent.append(float(((mrListNew[physHead] - mrListOG[physHead]) / mrListOG[physHead]) * 100))
         self.dut.dblData.Tables('P_DELTA_MRE').addRecord(
                           {
                           'HD_PHYS_PSN': physHead,
                           'SPC_ID': 1,
                           'OCCURRENCE':  self.dut.objSeq.getOccurrence(),
                           'SEQ':self.dut.objSeq.getSeq(),
                           'TEST_SEQ_EVENT': self.dut.objSeq.getTestSeqEvent(0),
                           'HD_LGC_PSN': head,
                           'DELTA_MRE': mrDiffPercent[-1],
                           })
      objMsg.printDblogBin(self.dut.dblData.Tables('P_DELTA_MRE'))

      if 1: #not testSwitch.FE_0117031_007955_CREATE_P186_BIAS_CAL2_MRE_DIFF:
         # This Raises error if over the deltaMTLim limit. Does not use GOTF
         mrDiff = [abs(item) for item in mrDiff]  #Get absolute values of differences
         mrDiffPercent = [abs(item) for item in mrDiffPercent]
         if max(mrDiff) > self.deltaMRLim or max(mrDiffPercent) > TP.mrDeltaLimPercent : #Disty 50, OEM 25
            objMsg.printMsg("Calculated MR resistance percentage differences: %s" % mrDiffPercent)
            objMsg.printMsg("Calculated MR resistance absolute differences: %s" % mrDiff)
            if (not testSwitch.SKIP_MR_RESISTANCE_CHECK): #Karnak has the problem T186 hang at first
                ScrCmds.raiseException(14599, "Delta MR resistance over limit")

      if getattr(TP, 'mrComboScreenDeltaFNC2Percent', {}):
         objMsg.printMsg("MR Combo spec: FNC2-PRE2 delta > %s and P215_TA_DFCT_TRK_CNT > %s" % (TP.mrComboScreenDeltaFNC2Percent, TP.mrComboScreenDFCT_TRK_CNT))
         defectTrack = eval(self.dut.driveattr['DFCT_TRK'])
         for head in xrange(self.dut.imaxHead):
            physHead = self.dut.LgcToPhysHdMap[head]
            abspercentDiff = abs(float(((mrListNew[physHead] - mrListOG[physHead]) / mrListOG[physHead]) * 100))
            if abspercentDiff > TP.mrComboScreenDeltaFNC2Percent and defectTrack[head] > TP.mrComboScreenDFCT_TRK_CNT:
               if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 14599):
                  objMsg.printMsg('Failed MR combo spec, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
               else:
                  ScrCmds.raiseException(14599, "Failed MR combo spec @ Head : [%s]" % str(physHead))
               
      if getattr(TP, 'mrComboScreenPRE2', {}):
         objMsg.printMsg("MR Combo spec: PRE2 < %s and CRT2-PRE2 delta > %s" % (TP.mrComboScreenPRE2, TP.mrComboScreenDeltaCRT2))
         for head in xrange(self.dut.imaxHead):
            physHead = self.dut.LgcToPhysHdMap[head]
            percentDiff = float(((mrListNew[physHead] - mrListOG[physHead]) / mrListOG[physHead]) * 100)
            if (not testSwitch.SKIP_MR_RESISTANCE_CHECK) and mrListOG[physHead] < TP.mrComboScreenPRE2 and percentDiff > TP.mrComboScreenDeltaCRT2:
               ScrCmds.raiseException(14599, "Failed MR combo spec @ Head : [%s]" % str(physHead))

      else:
         #this uses GOTF support to raise the error instead of the deltaMTLim. Must have GOTF support written
         for item in xrange(len(mrDiff)):

            curSeq = self.dut.objSeq.getSeq()
            testSeqNum = self.dut.objSeq.getTestSeqEvent(0)
            mrDiffVal = mrDiff[item]

            if testSwitch.FE_0173493_347506_USE_TEST321	and testSwitch.extern.SFT_TEST_0321:
               mreDiffTableName = 'P321_BIAS_CAL2_MRE_DIFF'
            else:
               mreDiffTableName = 'P186_BIAS_CAL2_MRE_DIFF'


            self.dut.dblData.Tables(mreDiffTableName).addRecord(
               {
                  'SPC_ID': -1,
                  'SEQ': curSeq,
                  'TEST_SEQ_EVENT': testSeqNum,
                  'MRE_DIFF_VAL':   mrDiffVal,
               })

         objMsg.printDblogBin(self.dut.dblData.Tables(mreDiffTableName))

      if testSwitch.RUN_VBIAS_T186:
         CServoOpti().setePreampBiasMode(enable = False)   # switch back to Voltage Bias mode

   def simToPcFile(self):
      """
      Pull the MR resitance SIM file and place it in a pcfile.  Return the path
      to the pcfile.
      """
      if not testSwitch.extern.FE_0125575_357552_SAVE_GMR_RES_RANGE_TO_SIM:
         record = objSimArea['MR_RES']
      if not testSwitch.virtualRun:
         if not testSwitch.extern.FE_0125575_357552_SAVE_GMR_RES_RANGE_TO_SIM:
            path = self.oFSO.retrieveHDResultsFile(record)
         else:
            path = self.oFSO.retrieveHDResultsFile(self.simRecord)
      else:
         path = os.path.join('.', self.genericMRResPath)
      return path

   def createMrArray(self, biasTbl=[], CAL2Table=1):
      """
      Create an empty table and fill in with actual MR values from test 186
      """
      mrList = [0 for i in range(self.dut.Servo_Sn_Prefix_Matrix.get(self.dut.serialnum[1:3],{'PhysHds':self.dut.imaxHead,})['PhysHds'])]

      for entry in biasTbl:
         if CAL2Table and entry.get('TEST_MODE') == 'MAX':  # Do not gather 'MAX' values reported by T186
            continue
         else:
            mrList[int(entry.get('HD_PHYS_PSN'))] = float(entry.get('MRE_RESISTANCE'))
            self.dut.driveattr['MR_RES_%d' % int(entry.get('HD_PHYS_PSN'))] = round(float(entry.get('MRE_RESISTANCE')),2)
      mrArray = array('f', mrList)

      del biasTbl
      return mrArray

   def gatherMRValues(self):
      """
      Gather MR values from P186_BIAS_CAL table and return as an array object.
      """
      if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
         biasTbl = self.dut.dblData.Tables('P321_BIAS_CAL2').tableDataObj()
         CAL2Table = 1
      else:
         try:
            biasTbl = self.dut.dblData.Tables('P186_BIAS_CAL2').tableDataObj()
            CAL2Table = 1
         except:
            biasTbl = self.dut.dblData.Tables('P186_BIAS_CAL').tableDataObj()
            CAL2Table = 0

      return self.createMrArray(biasTbl,CAL2Table)

   def arrayToFile(self, array):
      """
      Write the array object to the pcfile
      """
      if not testSwitch.extern.FE_0125575_357552_SAVE_GMR_RES_RANGE_TO_SIM:
         mrResFile = GenericResultsFile(self.genResName)
      else:
         mrResFile = GenericResultsFile(self.simRecord.name)
      mrResFile.open('w')
      arStr = array.tostring()  # GenericResultsFile won't work with arrays, so we have to output to a string instead
      mrResFile.write(arStr)
      mrResFile.close()

   def fileToDisc(self):
      """
      Write the file containing MR resistance values to disc, using test 231.
      """
      if not testSwitch.extern.FE_0125575_357552_SAVE_GMR_RES_RANGE_TO_SIM:
         record = objSimArea['MR_RES']

      # First, look for the generic results file that is created in MDW cals.  If
      #  that is not there, assume that we have a pcfile that can be written to disc
      if os.path.exists(self.genericMRResPath):
         filePath = self.genericMRResPath
      elif os.path.exists(self.mrResPath):
         filePath = self.mrResPath
      else:
         ScrCmds.raiseException(11044, "MR Resistance File does not exist")

      #Write data to drive SIM
      objMsg.printMsg("Saving MR Res File to drive SIM.  File Path: %s" % filePath, objMsg.CMessLvl.DEBUG)
      if not testSwitch.extern.FE_0125575_357552_SAVE_GMR_RES_RANGE_TO_SIM:
         self.oFSO.saveResultsFileToDrive(1, filePath, 0, record, 1)
      else:
         self.oFSO.saveResultsFileToDrive(1, filePath, 0, self.simRecord, 1)

      #Verify data on drive SIM
      if not testSwitch.virtualRun:
         if not testSwitch.extern.FE_0125575_357552_SAVE_GMR_RES_RANGE_TO_SIM:
            path = self.oFSO.retrieveHDResultsFile(record)
         else:
            path = self.oFSO.retrieveHDResultsFile(self.simRecord)
         file = open(path,'rb')
         try:
            file.seek(0,2)  # Seek to the end
            fileLength = file.tell()
         finally:
            file.close()

         if not testSwitch.extern.FE_0125575_357552_SAVE_GMR_RES_RANGE_TO_SIM:
            objMsg.printMsg("Re-Read of drive SIM File %s had size %d" % (record.name,fileLength), objMsg.CMessLvl.DEBUG)
         else:
            objMsg.printMsg("Re-Read of drive SIM File %s had size %d" % (self.simRecord.name,fileLength), objMsg.CMessLvl.DEBUG)

         if fileLength == 0:
            ScrCmds.raiseException(11044, "Drive MR Resistance SIM readback of 0 size.")

   def retrieveData(self,sourceLoc='SIM'):
      """
      Read file from SIM/CM, and returns data
      """
      if sourceLoc.upper() == 'SIM':  #Assume retrieve from SIM
         origCMPath = self.simToPcFile()
      elif sourceLoc.upper() == 'PC' and not testSwitch.virtualRun:
         #Assume file already on CM in /var/merlin/pcfiles/<simName>
         #origCMPath = self.mrResPath
         origCMPath = self.genericMRResPath
      else: #For VE
         origCMPath = os.path.join('.', self.genericMRResPath)

      thisCmFile = open(origCMPath,'r')
      mrSimArray = array('f', thisCmFile.read())
      thisCmFile.close()

      return mrSimArray.tolist()

   def retrieveDataAutonomously(self):
      """
         Determines where the mr resistance files exists and returns it.
         First it checks for a SIM file on the drive.  If not found it looks in
         """

      #check to see if SIM file exists
      simExists = False
      if self.dut.systemAreaPrepared:
         if testSwitch.extern.FE_0125575_357552_SAVE_GMR_RES_RANGE_TO_SIM:
            record = self.simRecord
         else:
            record = objSimArea['MR_RES']

         response = self.oFSO.checkIndexExists(record)
         if response != False:
            simExists, SIM_Header, numSIMFiles = response

      if simExists:
         #if the SIM file exists on the drive, read it to the pcfiles folder
         origCMPath = self.oFSO.retrieveHDResultsFile(record)
      elif os.path.isfile(self.genericMRResPath):
         #if the SIM file didn't exist, then next look for the file in the results directory
         origCMPath = self.genericMRResPath
      else:
         #the file does not exist on drive or in results directory...this must be a baseline run
         objMsg.printMsg('Resistance file not found on drive or in results directory on CM')
         return None

      objMsg.printMsg('Resistance file path is %s' %origCMPath)

      thisCmFile = open(origCMPath,'r')
      mrSimArray = array('f', thisCmFile.read())
      thisCmFile.close()

      return mrSimArray.tolist()


#---------------------------------------------------------------------------------------------------------#
class CMrResRange(CMrResFile):
   """
   Class to track range (max-min) of MR resitance. Inherits from CMrResFile, and uses same
   SIM File and I/O methods used there.
   """

   def __init__(self, prm186, rangeLimits):
      """
      @param prm186: T186 input to measure and return head mr resistances.
      @param rangeLimits: Percent change in baseline (100 means double).
      """
      CMrResFile.__init__(self, prm186, rangeLimits, simKeyName='MRR_RANGE')

      #Number heads servo code was built for. No reduced-heads shenanigans here.
      self.svoMaxHeads = self.dut.Servo_Sn_Prefix_Matrix.get(self.dut.serialnum[1:3],{'PhysHds':self.dut.imaxHead})['PhysHds']

   def compareMaxAndMins(self, oldRangeData=[], newMrResData=[]):
      """
      Compare old and new values, find new max and mins
      """
      if len(oldRangeData) < 3*self.dut.imaxHead:
         ScrCmds.raiseException(11044 ,"No baseline MR Ressistance saved into SIM")

      newRangeData = list(oldRangeData)

      for logicalHead in xrange(self.dut.imaxHead): # imaxHead is logical head count.
         # De-popped drives may start and end with different head counts.
         physHead = self.dut.LgcToPhysHdMap[logicalHead]

         #Check MIN first
         if newMrResData[physHead] < oldRangeData[self.svoMaxHeads + physHead]:
            newRangeData[self.svoMaxHeads + physHead] = newMrResData[physHead]

         #Check MAX
         if newMrResData[physHead] > oldRangeData[2*self.svoMaxHeads + physHead]:
            newRangeData[2*self.svoMaxHeads + physHead] = newMrResData[physHead]

      return newRangeData

   def updateResRangeData(self, optionsList=[]):
      """
      Function to run T186, collect data and update file on CM with new
      baseline or update maxes and mins. optionsList dictates whether
      to save baseline, where to read data from, write data to, etc.
      """
      # Run T186 and collect current MR resistance values
      self.St(self.prm186)


      if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
         biasCalTableName = 'P321_BIAS_CAL2'
      else:
         biasCalTableName = 'P186_BIAS_CAL2'

      #Cannot use gatherMRValues() here, since dealing with many T186 calls, not just 1
      if not testSwitch.virtualRun:
         T186_Data = self.dut.objSeq.SuprsDblObject[biasCalTableName]
      else:
         currSpcId = self.prm186.get('spc_id', self.prm186.get('SPC_ID', None))
         T186_Data = self.dut.dblData.Tables(biasCalTableName).chopDbLog('SPC_ID','match',currSpcId)

      newMrResList = self.createMrArray(T186_Data).tolist()

      oldRangeData = self.retrieveDataAutonomously()

      if 'saveBaselineOnly' in optionsList or oldRangeData == None:
         #could not find any old data in results dir or in SIM file.  this is a baseline run
         objMsg.printMsg('Saving data as the baseline.')
         newMRR_toSave = []
         #Save 3 sets of data - baseline, min, max
         newMRR_toSave.extend(newMrResList); newMRR_toSave.extend(newMrResList); newMRR_toSave.extend(newMrResList)
      else:
         objMsg.printMsg('Comparing new resistance data to previous data')
         newMRR_toSave = self.compareMaxAndMins(oldRangeData,newMrResList)

      rangeArray = array('f', newMRR_toSave)

      #save to PC File on CM
      self.arrayToFile(rangeArray)

      if self.oFSO.checkSimAllocated():
         #Before completing oper, save CM file to SIM on drive
         objMsg.printMsg('SIM area is allocated.  Saving MR measurements to disc')
         self.fileToDisc()
      else:
         objMsg.printMsg('SIM area is not allocated, therefore can not save measurements to disc')

   def printData_checkLimits(self, optionsList=[]):
      """
      Function to print out MR resistance range data and compare to
      limits. P/F status is returned to calling function.
      """
      # Retrieve data from PC file
      simRangeData  = self.retrieveData(sourceLoc='PC')

      resRngData = {}; resRngData['baseRes'] = {}
      resRngData['minRes'] = {}; resRngData['maxRes'] = {}
      resRngData['rngPcnt'] = {}; resRngData['hdStatus'] = {}
      drivePass = 1  #0 means fail
      failhead = []

      objMsg.printMsg('')
      if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
         objMsg.printMsg('P321_SCRIPT_DATA2:')
      else:
         objMsg.printMsg('P186_SCRIPT_DATA2:')
      objMsg.printMsg('HD_PHYS_PSN HD_LGC_PSN MAX_RES MIN_RES BASE_RES PCNT_RANGE HD_STATUS')

      for logicalHead in xrange(self.dut.imaxHead): # imaxHead is logical head count.
         # De-popped drives may start and end with different head counts.
         physHead = self.dut.LgcToPhysHdMap[logicalHead]

         resRngData['baseRes'][physHead] = baseRes = simRangeData[physHead]
         resRngData['minRes'][physHead] = minRes = simRangeData[self.svoMaxHeads+physHead]
         resRngData['maxRes'][physHead] = maxRes = simRangeData[2*self.svoMaxHeads+physHead]

         resRngData['rngPcnt'][physHead] = mrresPcnt = round(100*(maxRes - minRes) / baseRes,2)

         if mrresPcnt > self.deltaMRLim:  #Actually range limit - name "deltaMRLim" inherited from CMrResFile
            resRngData['hdStatus'][physHead] = 0
            drivePass = 0
            failhead.append(physHead)

         else:
            resRngData['hdStatus'][physHead] = 1

         objMsg.printMsg('%11d %10d %7.1f %7.1f %8.1f %10.2f %9d' %(physHead,logicalHead,maxRes,minRes,baseRes,mrresPcnt,resRngData['hdStatus'][physHead]))

      objMsg.printMsg('')

      if 'printTableForXml' in optionsList:
         thisSpcId = 52140
         #Populate P_TA_DWELL_SUMRY_HD table in oracle ****************************
         thisSeq,thisOccur,thisTSE = self.dut.objSeq.registerCurrentTest(test=0, spc_id=thisSpcId)
         for logicalHead in xrange(self.dut.imaxHead):
            physHead = self.dut.LgcToPhysHdMap[logicalHead]
            self.dut.dblData.Tables('P_TA_DWELL_SUMRY_HD').addRecord(
                {'HD_PHYS_PSN': physHead,
                'DWELL_GRPNG_ID': 0,
                'SPC_ID': thisSpcId,
                'OCCURRENCE': thisOccur,
                'SEQ' : thisSeq,
                'TEST_SEQ_EVENT': thisTSE,
                'DWELL_GRPNG_AMP_MAX': 0,
                'DWELL_GRPNG_AMP_MIN': 0,
                'HD_LGC_PSN': logicalHead,
                'TA_DWELL_CNT': 0,
                'DWELL_TIME': 0,
                'SURF_PASS_FAIL_ELIGIBLE': 0,
                'RES_HD_STATUS': resRngData['hdStatus'][physHead],
                'RES_START': round(float(resRngData['minRes'][physHead]),1),
                'RES_END': round(float(resRngData['maxRes'][physHead]),1),
                'RES_DELTA': round(float(resRngData['rngPcnt'][physHead]),2),
                'BER_HD_STATUS': resRngData['hdStatus'][physHead],
                'BER_START': 0,
                'BER_END': 0,
                'BER_DELTA': 0,
                'HD_STATUS': drivePass,
                })
         objMsg.printDblogBin(self.dut.dblData.Tables('P_TA_DWELL_SUMRY_HD'), thisSpcId)

      #Return to calling function, and decide whether to post failure there or not
      return drivePass, failhead

#==============================================================================================
class CProgRdChanTrg(CRdWrOpti):
   """
   Class to set up programmable read channel targets.
   """

   def __init__(self):
      CRdWrOpti.__init__(self)
      self.oServ = CServo()
      self.oFSO = CFSO()
      self.DEBUG = 0  # If non-zero, output extra debug info\
      self.P250_Table_name = 'P250_ERROR_RATE_BY_ZONE'
      self.P250_ALT_Table_name = 'P250_ERROR_RATE'
      self.p251TblName = 'P251_BEST_FITNESS_POINT2'
      self.p251TblNameAlt = 'P251_BEST_FITNESS_POINT'
      self.dth = dataTableHelper()
      #Load controller type
      self.oFSO.reportFWInfo()


   def setTargets(self, inPrm,zapFunc = None, zapECList = [10007], head=None):
      """
      Main method to set the best read channel target (npt)
      """

      #Set the class variables for zapping if necessary
      self.zapFunc = zapFunc
      self.zapECList = zapECList

      # Unpack the test data
      self.setNPT_156 = inPrm.get('setNPT_156')
      self.tdtarg_OptiPrm_251 = inPrm.get('tdtarg_OptiPrm_251')
      self.eccLevel = inPrm.get('berECCLevel')
      self.berRetryLim = inPrm.get('berRetryLim')
      self.berRetryStep = inPrm.get('berRetryStep')
      self.defaultZoneMeasure = inPrm.get('defaultZoneMeasure',9)

      # Get the test method (by drive, head, or head/zone)
      self.testMethod = TP.prm_ProgRdChanTarget.get('testMethod')

      # Get the zone table
      self.oFSO.getZoneTable()

      if self.DEBUG:
         zt = self.dut.dblData.Tables(TP.zone_table['table_name']).chopDbLog('TEST_SEQ_EVENT', 'max')
         objMsg.printMsg("Chopped zone table length is %s" % len(zt))
         objMsg.printMsg("Chopped zone table used in targ opti is %s" % zt)

      # Get the targets list from the RAP package
      nptList = self.getTargets()

      # If the RAP package doesn't support TDTARG opti, skip this entire function
      if nptList == None:

         return

      # Calculate the number of targets that we have
      numTargs = len(nptList)
      objMsg.printMsg("Performing TDTARGR opti using %s targets" % numTargs)

      # Build the empty data dictionary (targData)
      if self.testMethod == 'HdZn':
         zones = inPrm.get('defaultZoneMeasure',range(self.dut.numZones))
      elif self.testMethod == 'Hd':
         zones = [self.defaultZoneMeasure,]

      if head is None:
         heads = self.heads = range(self.dut.imaxHead)
      else:
         heads = [head]

      self.zones = zones

      self.targDataIdx = {}
      self.targData = []
      idx = 0
      for hd in heads:
         for zn in zones:
            self.targData.append({})
            self.targDataIdx['Hd' + str(hd) + 'Zn' + str(zn)] = idx
            idx += 1

      tempDbLog = []
      dbLogIdx = 0
      defaultBER = 0

      # Save RAP to pcfile
      self.St({
            'test_num'    : 178,
            'prm_name'    : 'Save RAP to PCFile',
            'timeout'     : 3600,
            'spc_id'      : 0,
            'CWORD1'      : 0x208,
            })

      #Build a dummy filled ber struct for filling by measurement data
      berStruct = [[[defaultBER for zone in range(self.dut.numZones)] for head in heads] for tgt in range(numTargs)]

      #Targets Loop
      for self.curTgtIdx in range(numTargs):
         # To save time, load target and opti all heads/zones at once
         self.curZn = -1
         self.curHd = -1

         # Load NPT target (T156)
         self.setNPT(nptList[self.curTgtIdx])

         # Opti TDTARGR and adapt FIR and NPML taps
         self.sweepAndAdapt(zones = zones)

         #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG

         #Get the optimized target opti data
         tdtarg = self.getTargetOptiData()

         #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG

         berStruct = self.measureBER(heads, zones, berStruct, self.curTgtIdx)

         #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG

         # Gather BER data on all heads/zones
         curSeq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

         # Gather BER data on all heads/zones
         for self.curHd in heads:
            for self.curZn in zones:
               self.curMsmt = {"Head" : self.curHd,
                               "Zone" : self.curZn,
                               "TgtIndex" : self.curTgtIdx,
                               "NPT" : nptList[self.curTgtIdx],
                               "dblIdx" : dbLogIdx,  # Keep track of what measurements match up with dbLog entries for easy setting of FINAL_NPT_FLAG later
                               }

               # Calculate BER at ID-most portion of test area
               self.curMsmt["BER"] = self.calcBER(berStruct)
               # Output current BER measurement for data usage
               if not testSwitch.NPT_LOG_REDUCTION or self.DEBUG:
                  objMsg.printMsg("NPT Opti: NPT: %s; Measured BER at head %s zone %s: %s" % (self.curMsmt.get("NPT"), self.curHd, self.curZn, self.curMsmt.get("BER")), objMsg.CMessLvl.VERBOSEDEBUG)


               for entry in tdtarg:  # Pick off last measurement data for head and zone we care about
                  if entry['HD_LGC_PSN'] == str(self.curHd):
                     if entry['DATA_ZONE'] == str(self.curZn):
                        # Fill in the data
                        if self.DEBUG:
                           objMsg.printMsg("OPTI_VAL, head %s zone %s is %s" % (self.curHd, self.curZn, entry['OPTI_VAL']))
                        tempDbLog.append(
                        {
                           'SPC_ID' : 1,
                           'OCCURRENCE' : occurrence,
                           'SEQ' : curSeq,
                           'TEST_SEQ_EVENT' : testSeqEvent,
                           'HD_PHYS_PSN' : self.dut.LgcToPhysHdMap[self.curHd],
                           'DATA_ZONE' : self.curZn,
                           'HD_LGC_PSN' : self.curHd,
                           'TARG_T0' : nptList[self.curTgtIdx][0],
                           'TARG_T1' : nptList[self.curTgtIdx][1],
                           'TARG_T2' : nptList[self.curTgtIdx][2],
                           'TDTARGR' : entry['OPTI_VAL'],
                           'RAW_ERROR_RATE' : self.curMsmt.get("BER"),
                           'FINAL_NPT_FLAG' : 0,
                        })
                        self.curMsmt["TDTARG"] = int(entry['OPTI_VAL']) # Save opti'd tdtarg value

                        dbLogIdx += 1
                        # If BER is the best, so far, for this test area save the data
                        itemName = 'Hd%sZn%s' % (self.curHd, self.curZn)

                        index = self.targDataIdx.get(itemName)
                        if self.curMsmt.get("BER") < self.targData[index].get("BER", 1) or testSwitch.virtualRun: # For VE, force setting a target, so the code won't choke later
                           objMsg.printMsg("New Best BER found: head %s zone %s; BER: %s" % (self.curHd, self.curZn, self.curMsmt.get("BER")), objMsg.CMessLvl.VERBOSEDEBUG)
                           self.curMsmt = self.firSettings(self.curMsmt, mode = 'get')
                           self.targData[index] = self.curMsmt
                        break

         # Restore RAP from pc file
         self.St({
               'test_num'    : 178,
               'prm_name'    : 'Restore RAP from PCFile',
               'timeout'     : 3600,
               'spc_id'      : 0,
               'CWORD1'      : 0x201,
               })

      objMsg.printMsg("Finished gathering target data on %s targets" % numTargs)

      # Load the best NPTs and opti'ed TDTARG values
      for testItem in self.targData:
         self.curHd = testItem.get("Head")
         self.curZn = testItem.get("Zone")
         self.curTgtIdx = testItem.get("TgtIndex")
         NPT = testItem.get("NPT")
         BER = testItem.get("BER")
         if testSwitch.BF_0115022_220554_ENSURE_BER_HAS_A_VALUE_DURING_TARGET_OPTI and BER == None:
            ScrCmds.raiseException(10402, "Rd Misc-Read Error")
         if BER < 0:
            self.setNPT(NPT)
            # Re-apply original FIR settings
            self.firSettings(testItem, mode = 'set')

      # Re-adapt FIR and NPML taps for all zones
      objMsg.printMsg("Performing Final TDTARG, FIR and NPML opti")
      if self.testMethod == 'Hd':
         zones = range(self.dut.numZones)
      self.sweepAndAdapt(finalSetting = 1, zones = zones)
      self.oFSO.saveRAPSAPtoFLASH()

      # Output the info in a readable table:
      objMsg.printMsg("Final NPT settings:")
      for testItem in self.targData:
         self.curHd = testItem.get("Head")
         self.curZn = testItem.get("Zone")
         self.curTgtIdx = testItem.get("TgtIndex")
         NPT = testItem.get("NPT")
         BER = testItem.get("BER")
         if self.curZn == self.defaultZoneMeasure and self.testMethod == 'Hd':
            if BER < 0:
               objMsg.printMsg("Head: %s; NPT: %s; Measured BER: %s" % (self.curHd, NPT, BER))
            else:
               objMsg.printMsg("Head: %s; No valid track to measure BER found.  Leave at default NPT" % self.curHd)
         else:
            if BER < 0:
               objMsg.printMsg("Head: %s; Zone: %s; NPT: %s; Measured BER: %s" % (self.curHd, self.curZn, NPT, BER))
            else:
               objMsg.printMsg("Head: %s; Zone: %s; No valid track to measure BER found.  Leave at default NPT" % (self.curHd, self.curZn))
         tempDbLog[testItem.get("dblIdx")]["FINAL_NPT_FLAG"] = 1  # Set FINAL_NPT_FLAG for the best NPT pick

      # Commit temporary dbLog data to dbLog
      for entry in tempDbLog:
         self.dut.dblData.Tables('P_NPT_OPTI_AGERE').addRecord(entry)

      objMsg.printDblogBin(self.dut.dblData.Tables('P_NPT_OPTI_AGERE'))

      try:
         self.oFSO.closeFileObj()
      except:
         pass


   def getTdTargCudacom(self):
      tdtarg = []
      for self.curHd in self.heads:
         for self.curZn in self.zones:
            msmtData = {'tdtarg':None}
            msmtData = self.firSettings(msmtData, mode = 'get', updatePrms = ['tdtarg',])
            tdtarg.append({'HD_LGC_PSN':str(self.curHd),'DATA_ZONE':str(self.curZn),'OPTI_VAL':msmtData['tdtarg']})
      if self.DEBUG:
         objMsg.printMsg('Data returned from tdtarg: %s' % (tdtarg,))
      return tdtarg

   def getTargetOptiData(self, swapTable = False):
      # Collect dbLog data
      tdtarg = []

      try:
         if testSwitch.NPT_LOG_REDUCTION:
            #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG
            tdtarg = self.getTdTargCudacom()
            #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG
         else:
            tdtarg = self.getTdTargCudacom()
      except:
         import traceback
         objMsg.printMsg('Error: %s' % (traceback.format_exc(),))
         if swapTable == False:
            tdtarg = self.getTargetOptiData(swapTable = True)
         else:
            tdtarg = [{'HD_LGC_PSN':str(self.curHd),'DATA_ZONE':str(self.curZn),'OPTI_VAL':-1},]

      if not (testSwitch.NPT_LOG_REDUCTION or (ConfigVars[CN].get('8HD_Override',0) == 1)):
         try:

            #Delete file pointers
            self.dut.dblData.Tables('P251_STATUS').deleteIndexRecords(1)
            self.dut.dblData.Tables(self.p251TblName).deleteIndexRecords(1)

            #Delete RAM objects
            self.dut.dblData.delTable('P251_STATUS')
            self.dut.dblData.delTable(self.p251TblName)
         except:
            pass

      if self.DEBUG:
         objMsg.printMsg("TDTARG values are %s" % tdtarg)
      tdtarg.reverse()

      return tdtarg


   def getTargets(self):
      """
      Retrieve the targets list from the dlfiles directory
      """
      print self.dut.channelType
      if self.dut.channelType in ["AGERE_ANACONDA", "SRC_EMMA"] or self.dut.channelType.find('BONANZA') > -1:
         targets = getattr(TP,'NPT_Targets_156')
      else:
         # Set up objects to support Request Callback 81
         sys.path.append(ScrCmds.getSystemDnldPath())
         targPath = os.path.join(ScrCmds.getSystemDnldPath(), 'parsedNPT.bin')
         try:
            self.oFSO.configFileObj(targPath)  # create the file object for processRequest81
         except:
            objMsg.printMsg("TDTARGR opti not supported by this RAP package.  Skipping target opti.")
            try:
               self.oFSO.closeFileObj()
            except:
               pass
            return None

         try:
            from npt_targets import targets
         except:
            targets = None
         del sys.path[-1]

      return targets

   def setNPT(self, npt):
      """
      Use self.curTgtIdx to load the read channel target (NPT)
      """
      # Use T156 to set the NPT

      testParms = self.setNPT_156

      # create 0x0m0n where m is the starting head and n is the ending head
      if self.curHd != -1:
         testParms['HEAD_RANGE'] = (self.curHd*(1<<8)+self.curHd)
      if self.curZn != -1:
         testParms['ZONE_MASK'] = ((1<<self.curZn)/(1<<16), (1<<self.curZn)%(1<<16))
         testParms['ZONE_MASK_EXT'] = ((1<<self.curZn)/(1<<16)/(1<<16)/(1<<16), (1<<self.curZn)/(1<<16)/(1<<16))

      if testSwitch.NPT_LOG_REDUCTION:
         testParms['stSuppressResults'] = ST_SUPPRESS__ALL

      if self.dut.channelType in ["AGERE_ANACONDA", "SRC_EMMA"] or self.dut.channelType.find('BONANZA') > -1:
         testParms['PATTERNS'] = npt[0:3]
         testParms['CWORD1'] = testParms['CWORD1'] | (npt[3]<<2)
         testParms['SYNC_BYTE_CONTROL'] = npt[4]
         self.St(testParms)
      else:
         testParms['PATTERNS'] = npt
         RegisterResultsCallback(self.oFSO.processRequest81, 81, 0) # Re-direct 81 calls
         self.St(testParms)
         RegisterResultsCallback('', 81,) # Resume normal 81 calls

   def sweepAndAdapt(self, finalSetting = 0, zones = []):
      """
      Sweep TDTARGR values and adapt FIR and NPML
      """

      #zoneMask = self.oUtility.ReturnTestCylWord(self.oUtility.setZoneMask(zones))
      zone_mask_low = 0
      zone_mask_high = 0
      for zn in zones:
         if zn < 32:
            zone_mask_low |= (1 << zn)
         else:
            zone_mask_high |= (1 << (zn -32))
      self.optiData = {}

      tdtarg_OptiPrm_251_cpy = dict(self.tdtarg_OptiPrm_251)
      if finalSetting:  # Perform a dummy read to save FIR and NPML values
         tdtarg_OptiPrm_251_cpy["REG_TO_OPT1"] = (0x0,0x01,0x01,0x01)
         tdtarg_OptiPrm_251_cpy["REG_TO_OPT1_EXT"] = (0x0,0x0,0x3c)

      #tdtarg_OptiPrm_251_cpy['BIT_MASK'] = zoneMask
      tdtarg_OptiPrm_251_cpy['BIT_MASK'] = self.oUtility.ReturnTestCylWord(zone_mask_low)
      tdtarg_OptiPrm_251_cpy['BIT_MASK_EXT'] = self.oUtility.ReturnTestCylWord(zone_mask_high)

      if not self.dut.SOCType in ['TETON_4.0', 'YEHTI_1.0']:
         #Clear bit 15 if 1 of the above SOC's is in use- TPE-0004058... remove this code once TETON retired
         tdtarg_OptiPrm_251_cpy["REG_TO_OPT1"] = list(tdtarg_OptiPrm_251_cpy["REG_TO_OPT1"])
         tdtarg_OptiPrm_251_cpy["REG_TO_OPT1"][0] = tdtarg_OptiPrm_251_cpy["REG_TO_OPT1"][0] & (0xFFFF - 2**15)

      try:
         if (ConfigVars[CN].get('8HD_Override',0) == 1):
            parseData = []
         else:
            parseData = ['P251_BEST_FITNESS_POINT2', 'P251_BEST_FITNESS_POINT2']
         #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG
         self.optiData = self.phastOpti(tdtarg_OptiPrm_251_cpy,3,0,self.zapFunc,self.zapECList, logReduction = testSwitch.NPT_LOG_REDUCTION, dataCollectionTables = parseData)
      except:
         if finalSetting:
            raise
         else:
            objMsg.printMsg("Ignoring opti failure when not in final setting as some NPT targets will lead to un-opti able zones.")

      self.headRange = None


   def firSettings(self, msmtData, mode = 'get', updatePrms = None):
      """
      Get (mode='get') or set (mode='set') FIR tap settings.  In 'get' mode, data
      will be gathered and added to msmtData.  In 'set' mode, data will be pulled
      from msmtData and applied to the FIR taps.
      """
      # Agere channel tap registers
      taps = {
         'tap1_2' : 137,
         'tap3_5' : 138,
         'tap6_7' : 139,
         'tap8_9' : 140,
         'tapX'   : 141,
         'tdtarg' : 145,
         }

      if updatePrms == None:
         tapKeys = taps.keys()
      else:
         tapKeys = updatePrms

      if mode == 'get':
         for tap in tapKeys:
            buf,errorCode = self.Fn(1336, taps[tap], self.curHd, self.curZn)
            if errorCode == 0:
               if not testSwitch.virtualRun:
                  msmtData[tap] = struct.unpack("HH",buf)[0] # struct.unpack always returns a tuple, but we know only one value is returned, so grab that value instead of the whole tuple
               else:
                  msmtData[tap] = taps[tap] # Dummy value to allow VE to run
               if self.DEBUG:
                  objMsg.printMsg("RAP register %s (head %s zone %s) value read: %s" % (taps[tap], self.curHd, self.curZn, msmtData[tap]))
            else:
               ScrCmds.raiseException(errorCode, "Failure during target opti call to cudacom 1336 (read RAP) for register %s" % taps[tap])
      elif mode == 'set':
         for tap in tapKeys:
            buf,errorCode = self.Fn(1339, taps[tap], msmtData[tap], self.curHd, self.curZn)
            if self.DEBUG:
               objMsg.printMsg("RAP register %s (head %s zone %s) value written: %s" % (taps[tap], self.curHd, self.curZn, msmtData[tap]))
            if errorCode != 0:
               ScrCmds.raiseException(errorCode, "Failure during target opti call to cudacom 1339 (write RAP) for register %s" % taps[tap])

      return msmtData

   def calcBER(self, berStruct):
      return berStruct[self.curTgtIdx][self.curHd][self.curZn]

   def measureBER(self, heads, zones, berStruct, tgtIndex):
      objMsg.printMsg("Getting error rate for target %d" % tgtIndex)
      berStruct = self.calcBER_250_SER(heads, zones, berStruct, tgtIndex)
      return berStruct

   def zeroMeasurement(self, heads, zones, berStruct, tgtIndex):
      for head in heads:
         for zone in zones:
            berStruct[tgtIndex][head][zone] = 0
      return berStruct

   def calcBER_250_SER(self, heads, zones, berStruct, tgtIndex):
      # Pick the last (ID-most) cylinder in the zone or on the drive

      zone_mask_low = 0
      zone_mask_high = 0
      for zn in zones:
         if zn < 32:
            zone_mask_low |= (1 << zn)
         else:
            zone_mask_high |= (1 << (zn -32))
      #zoneMask = self.oUtility.setZoneMask(zones)

      nptMeasPrm = dict(TP.prm_ProgRdChanTarget_250)

      #nptMeasPrm['ZONE_MASK'] = self.oUtility.ReturnTestCylWord(zoneMask)
      nptMeasPrm['ZONE_MASK'] = self.oUtility.ReturnTestCylWord(zone_mask_low)
      nptMeasPrm['ZONE_MASK'] = self.oUtility.ReturnTestCylWord(zone_mask_high)
      nptMeasPrm['TEST_HEAD'] = (min(heads) << 8) + max(heads)


      if testSwitch.NPT_LOG_REDUCTION:
         nptMeasPrm['stSuppressResults'] = ST_SUPPRESS__ALL | ST_SUPPRESS_RECOVER_LOG_ON_FAILURE
         nptMeasPrm['DblTablesToParse'] = [self.P250_Table_name, self.P250_ALT_Table_name]
         startIndex = 0
      else:
         try:
            startIndex = len(self.get_250_tableData())
         except:
            #No data available
            startIndex = 0

      if testSwitch.virtualRun:
         #No new data population in VE
         startIndex = 0


      #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG

      try:
         SetFailSafe()
         self.St(nptMeasPrm)
         ClearFailSafe()
         symbolData = self.get_250_tableData()
      except:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         symbolData = []


      if symbolData == []:
         self.zeroMeasurement(heads, zones, berStruct, tgtIndex)
         return berStruct

      #objMsg.printMsg(objMsg.getMemVals()) #MGM DEBUG
      for row in symbolData[startIndex:]:
         berStruct[tgtIndex][int(row['HD_LGC_PSN'])][int(row['DATA_ZONE'])] = float(str(row['RAW_ERROR_RATE']).replace('"','')) #raw only for now

      if not testSwitch.NPT_LOG_REDUCTION:
         #Remove the references to the file
         self.dut.dblData.Tables(self.P250_Table_name).deleteIndexRecords(confirmDelete = 1)
         #Remove the ram copy
         self.dut.dblData.delTable(self.P250_Table_name)

      del symbolData


      return berStruct

   def get_250_tableData(self):
      try:
         if testSwitch.NPT_LOG_REDUCTION:

            symbolData = self.dut.objSeq.SuprsDblObject.get(self.P250_Table_name, None)

            if symbolData == None:
               temp = self.P250_Table_name
               self.P250_Table_name = self.P250_ALT_Table_name
               self.P250_ALT_Table_name = temp
               del temp
               symbolData = self.dut.objSeq.SuprsDblObject.get(self.P250_Table_name)

            del self.dut.objSeq.SuprsDblObject[self.P250_Table_name]

         else:
            symbolData = self.dut.dblData.Tables(self.P250_Table_name).tableDataObj()

      except:
         objMsg.printMsg("symbolData extraction failure: %s" % traceback.format_exc())
         try:
            self.dut.dblData.delTable(self.P250_Table_name)
            self.P250_Table_name = self.P250_ALT_Table_name
            symbolData = self.dut.dblData.Tables(self.P250_Table_name).tableDataObj()

         except:
            objMsg.printMsg("symbolData extraction failure: %s" % traceback.format_exc())
            symbolData = []
      return symbolData

   def calcBER_Cudacom(self, heads, zones, berStruct, tgtIndex):
      """
      Measure and save BER using ber CudaCom function
      """

      # Get the latest zone data entered in the zone table
      zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()

      for head in heads:
         for zone in zones:

            Index = self.dth.getFirstRowIndexFromTable_byZone(zt, head, zone)
            sc = int(zt[Index]['ZN_START_CYL'])
            ec = sc + int(zt[Index]['NUM_CYL']) - 1
            while Index+1< len(zt) and zt[Index]['ZN'] == zt[Index+1]['ZN']:
               ec += int(zt[Index+1]['NUM_CYL']) 
               Index += 1         

            testCyl=ec

            berStruct[tgtIndex][head][zone] = self.getBER_with_Retries(head, testCyl, zone)

      return berStruct


   def getBER_with_Retries(self, curHd, testCyl, zone):

      if self.DEBUG != 0:
         objMsg.printMsg("Attempting to measure BER at hd %s Cyl %s (zone %s)" % (curHd, testCyl, zone))

      retryLim = self.berRetryLim
      retryStep = self.berRetryStep
      retries = 0
      ber = 0
      while retries <= retryLim:
         fatal_errs = 0

         # Seek to the write position of the cylinder
         self.oServ.wsk(testCyl, curHd)

         buf = self.writetrack() # returns status only
         try:
            write_trk_status = struct.unpack(">L",buf) # dbl word, byte swapped
         except:
            #Handle string sense codes
            write_trk_status = buf

         if write_trk_status[0] != 128 :
            fatal_errs += 1
            objMsg.printMsg("Prep area: this hd/zn has failed for a write error")
            objMsg.printMsg("Prep area: fatal error count = %d" % fatal_errs)
            prep_err = 1

         # Seek to the read position of the cylinder
         self.oServ.rsk(testCyl, curHd)

         # Measure BER
         buf = self.ber(90, 1, self.eccLevel, printResult = 0)
         result = struct.unpack("fLLLLLLL",buf)
         ber = result[0]
         data_errs = result[1]
         sync_errs = result[2]
         fatal_errs = result[3]

         if fatal_errs != 0 :
            objMsg.printMsg("Hd: %s; Cyl: %s has failed for an OTHER (fatal) error during the BER msmt" % (self.curHd, testCyl))
            testCyl -= retryStep
            retries += 1
         else:
            break

      if retries > retryLim:  # We can't get a BER measurement
         objMsg.printMsg("Out of retries.  Set BER to 0 for this target")
         ber = 0

      return ber


#---------------------------------------------------------------------------------------------------------#
class CWpcRangeFile(CProcess):
   """
   Class to create and use a SIM file which holds WPC range from TRIPLET_OPTI
   """

   def __init__(self):
      CProcess.__init__(self)
      pcFileName = 'wpc_range'
      self.genWpcRangeName = 'WpcRange'
      self.oFSO = CFSO()
      self.oUtility = CUtility()
      self.T231Index = 28
      self.dut = objDut

      self.wpcRange_Path = os.path.join(ScrCmds.getSystemPCPath(), pcFileName, self.oFSO.getFofFileName(0))
      self.genericWpcRangePath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.genWpcRangeName)

   def Save_WpcRange(self, TripletWpcTable, directSave=False):
      
      if directSave:
         WPC_table = TripletWpcTable
      else:
         WPC_table = {}
         for index in range(len(TripletWpcTable)):
            hd = int(TripletWpcTable[index]['HD_PHYS_PSN'])
            zn = int(TripletWpcTable[index]['DATA_ZONE'])
            WPC_table[hd,zn] = int(TripletWpcTable[index]['WPC'])
            
      self.DictToFile(WPC_table)
      self.FileToDisc()

   def DictToFile(self, dict):
      import cPickle
      file = GenericResultsFile(self.genWpcRangeName)
      file.open('w')
      file.write(cPickle.dumps(dict))
      file.close()

   def FileToDisc(self):
      record = objSimArea['WPC_RANGE']

      # First, look for the generic results file that is created in TRIPLET_OPTI cals. 
      # If that is not there, assume that we have a pcfile that can be written to disc
      if os.path.exists(self.genericWpcRangePath):
         filePath = self.genericWpcRangePath
      elif os.path.exists(self.wpcRange_Path):
         filePath = self.wpcRange_Path
      else:
         ScrCmds.raiseException(11044, "WPC range file does not exist")

      #Write data to drive SIM
      objMsg.printMsg("Saving WPC range file to drive SIM file path: %s" % filePath, objMsg.CMessLvl.DEBUG)
      self.oFSO.saveResultsFileToDrive(1, filePath, 0, record, 1)

      #Verify data on drive SIM
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
         file = open(path,'rb')
         try:
            file.seek(0,2)  # Seek to the end
            fileLength = file.tell()
         finally:
            file.close()
         objMsg.printMsg("Re-Read of drive SIM file %s has size %d" % (record.name,fileLength), objMsg.CMessLvl.DEBUG)
         if fileLength == 0:
            ScrCmds.raiseException(11044, "Drive WPC range SIM readback of 0 size.")

   def Retrieve_WpcRange(self):
      import cPickle
      path = self.SimToPcFile()
      file = open(path, 'r')
      try:
         WPC_table = cPickle.loads(file.read())
      except:
         WPC_table = {}
      file.close()
      #objMsg.printMsg("WPC_table = %s" % str(WPC_table))
      return WPC_table

   def SimToPcFile(self):
      """
      Pull the SIM file and place it in a pcfile.  Return the path to the pcfile.
      """
      record = objSimArea['WPC_RANGE']
      if not testSwitch.virtualRun:
         path = self.oFSO.retrieveHDResultsFile(record)
      else:
         path = os.path.join('.', self.genericWpcRangePath)
      return path
