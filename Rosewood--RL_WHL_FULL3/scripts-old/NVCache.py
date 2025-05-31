#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: States and functions to support NVCache cert and support
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/NVCache.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/NVCache.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *

import DesignPatterns
import ScrCmds
import re

from State import CState
from Process import CProcess
from PowerControl import objPwrCtrl
import MessageHandler as objMsg
from Drive import objDut
import sptCmds
from TestParamExtractor import TP

dut = objDut

if testSwitch.FE_0117758_231166_NVCACHE_CAL_SUPPORT:
   class NVCacheDiagFuncs(object):

      @staticmethod
      def factoryBadClumpScan():

         sptCmds.gotoLevel('N')
         sptCmds.sendDiagCmd('B1', timeout = 300, printResult = True)

      @staticmethod
      def fieldBadClumpScan():
         objMsg.printMsg("Performing NVC Field Bad Clump Scan")

         sptCmds.gotoLevel('N')
         sptCmds.sendDiagCmd('B2', timeout = 300, printResult = True)

      @staticmethod
      def initializeFlashIO(initializeMode = 0):
         """
         initializeMode has 3 states as defined by documentation
         0 = entire subsystem
         1 = enables the flash bridge
         2 = uses psm todetect the flash hardware and load appropriate psm code
         """

         sptCmds.gotoLevel('N')
         sptCmds.sendDiagCmd('I%X' % initializeMode, timeout = 300, printResult = True)

      @staticmethod
      def getAsdBadClumpList():
         if testSwitch.FE_0188555_210191_NVC_SEQ_REV3:
            clumpPattern = 'Bad Clump count:\s*(?P<badclumpcnt>[0-9a-fA-F]+)'
            sptCmds.gotoLevel('O')
            result = sptCmds.sendDiagCmd('b0', timeout = 300, printResult = True)
            if testSwitch.virtualRun:
               result = """Erase Count:
                       Max     Min     Average
                       0000    0000    0000
               
               Combo Mode Num Valid LBA:
                       MLC             SLC
                       00000000        00000000
               
               Pinned Data:
                       Read    Write   Free
                       0000    0000    07FF
               
               Bad Clump count: 0010
               
               Bad Clump List:
               
               """
            try:
               p = re.compile(clumpPattern)
               m = p.search(result)
               badclumps = int(m.group('badclumpcnt'),16)
            except:
               ScrCmds.raiseException(13426, "Unable to parse CA command")
   
   
            dut.driveattr['NVC_DEFECT_CNT'] = badclumps
   
            objMsg.printMsg("Detected %d bad clumps." % badclumps)
   
            return badclumps
         
         
         
         else:
            clumpPattern = "(?P<ClumpNumber>[0-9a-fA-F]+):\s[0-9a-fA-F]+->[0-9a-fA-F]+->[0-9a-fA-F]+\s[0-9a-fA-F]+\s+(?P<ValidLBAs>[0-9a-fA-F]+)\s+[0-9a-fA-F]+"
            sptCmds.gotoLevel('O')
            result = sptCmds.sendDiagCmd('CB', timeout = 300, printResult = True)
            if testSwitch.virtualRun:
               result = """Clump Prev->Curr->Next 1stNode ValidLBAs EraseCnt
   
   0007: 1007->0007->0008 FFFF    0000      00000000
   """
            try:
               matches = re.findall(clumpPattern, result)
            except:
               ScrCmds.raiseException(13426, "Unable to parse CA command")
   
            if testSwitch.FE_0118679_231166_NVC_SEQ_REV2:
               matches = matches[:-1] #Last defect isn't valid
   
            dut.driveattr['NVC_DEFECT_CNT'] = len(matches)
   
            objMsg.printMsg("Detected %d bad clumps." % len(matches))
   
            return len(matches)

      @staticmethod
      def initializeCacheFileSystem():

         sptCmds.gotoLevel('O')
         sptCmds.sendDiagCmd('I', timeout = 300, printResult = True)

      @staticmethod
      def verifyIntegrityOfCFS(integrityTest = 0):
         """
         integrityTest has the following values
         0 - All tests (default)
         1 - Count nodes
         2 - Check for monotonic LBAs
         3 - Verify Tap Nodes vs Cache Nodes consistency"
         4 - Check physical clump linkages
         5 - Check for orphan clump nodes
         6 - Check for orphan cache nodes
         """

         sptCmds.gotoLevel('O')
         sptCmds.sendDiagCmd('v%X' % integrityTest, timeout = 300, printResult = True, loopSleepTime = 0.01)

      @staticmethod
      def eraseFlash():

         sptCmds.gotoLevel('N')

         sptCmds.sendDiagCmd('EDEADBEEF', timeout = 10000, altPattern="Erase successful", printResult = True)

      @staticmethod
      def verifyFlashCommand(*args, **kwargs):
         """
         Sequential argument list
         [start-clump] = first clump to operate upon (default 0)
         [clump-count] = number of clumps to operate upon (default to end of flash)
         [start-block] = first block offset to write in each clump (default 0)
         [end-block] = last block to write in each clump (default max blocks per clump)
         [total-loop-count] = total number of iterations to run the erase/write/read process (default 1)
         [read-loop-count] = number of times to perform read operation (default 1)
         [pattern] = data pattern to write (default = current clump number)
         """
         timeout = kwargs.pop('timeout', 300)

         sptCmds.gotoLevel('N')
         args = [hex(arg) for arg in args]

         sptCmds.sendDiagCmd('V%s' % ','.join(args), timeout = timeout)

      if testSwitch.FE_0118648_231166_ADD_NVC_TIMING_CAL:
         @staticmethod
         def initializeNVCTiming(printResult = True):
            """
            Increases the CFC clock speed to target value (145MB/s ref on Sphinx/Overton)
            Calibrates and displays the NVC timing values and saves them to IAP
            """
            if testSwitch.extern.FE_0118193_210712_OVERTOUN_TIMING_DIAGS == 0 and not testSwitch.virtualRun:
               import Exceptions
               raise Exceptions.CDependencyException, ('FE_0118648_231166_ADD_NVC_TIMING_CAL', 'FE_0118193_210712_OVERTOUN_TIMING_DIAGS')
            sptCmds.gotoLevel('N')
            if not testSwitch.WA_0150637_357260_P_SKIP_P1_1_IN_NVCACHE_INIT:
               sptCmds.sendDiagCmd("P1,1", timeout = 1000, printResult = printResult)
            sptCmds.sendDiagCmd("T1", timeout = 1000, printResult = printResult)

      if testSwitch.FE_0118679_231166_NVC_SEQ_REV2 or testSwitch.FE_0188555_210191_NVC_SEQ_REV3:
         @staticmethod
         def verifyNVCReadiness(printResult = True):
            sptCmds.gotoLevel('N')
            if not testSwitch.FE_NVC_SEQ_REV4:
               response = sptCmds.sendDiagCmd("m6,3601", timeout = 1000, printResult = printResult)
               if testSwitch.virtualRun:
                  response = """ Overtoun Word Data
                                 3601: 0010
                                 F3 N>
                                 """
               match = re.search('3601:\s*0+(?P<respCode>10)', response)
            else:
               # For program with direct attach PCBA (Raintree CL723129)
               response = sptCmds.sendDiagCmd("v", timeout = 1000, printResult = printResult)
               if testSwitch.virtualRun:
                  response = """ FlashID A7EC 7E94
                                 Flash Manufacturer: Samsung
                                 Flash Capacity = 00008 GB MLC
                                 Combo Mode

                                 NumberOfClumps = 	0x1000
                                 LBAsPerCluster = 	0x0010
                                 LBAsPerClumpMLC = 	0x1000
                                 LBAsPerClumpSLC = 	0x0800
                                 ClustersPerClumpMLC = 	0x0100
                                 ClustersPerClumpSLC = 	0x0080
                                 DefragClumpThresholdInSectors = 	0x0800
                                 UserSLCMaxSizeInClumps =        	0x0600
                                 NumberOfPotentiallyWrittenClusters = 	0x0002
                                 DefectListRevisionKey      	0x0001
                                 SLC Clumps                 	0x067C
                                 F3 N>
                                 """

               objMsg.printMsg("Look for 4 GB or 8 GB signature")
               match = re.search('Flash Capacity =\s*0+(?P<respCap>4|8)\s*GB', response)

               '''
               #For AngsanaH PCBA with Brooklyn chip
               response = sptCmds.sendDiagCmd("m6,0004", timeout = 1000, printResult = printResult)
               if testSwitch.virtualRun:
                  response = """ Flash Bridge Word Data
                                 0004: 0010 
                                 F3 N>
                                 """
               match = re.search('0004:\s*0+(?P<respCode>10)', response)
               '''

            if match:
               objMsg.printMsg("Validated NVC Readiness")
            else:
               ScrCmds.raiseException(13306, "Invalid response code returned from drive!\nResponse: %s" % response)


   class InitNVCacheWithDiags(CState):
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)

      def initializeNVCMedia(self):
         objMsg.printMsg("Initializing NVC Media")


         defectCnt = NVCacheDiagFuncs.getAsdBadClumpList()
         if defectCnt > getattr(TP, 'prm_max_NVC_defects', 160):
            ScrCmds.raiseException(13306, "NVC Defect Count %d GTT %d" % (defectCnt, getattr(TP, 'prm_max_NVC_defects', 160)))

         if not testSwitch.FE_0118679_231166_NVC_SEQ_REV2:
            NVCacheDiagFuncs.initializeFlashIO()
            NVCacheDiagFuncs.fieldBadClumpScan()


      def initializeNVCTiming(self):
         objMsg.printMsg("Initializing NVC Timing")
         if testSwitch.FE_0118648_231166_ADD_NVC_TIMING_CAL:
            NVCacheDiagFuncs.initializeNVCTiming()

      def initializeCacheFileSystem(self):
         objMsg.printMsg("Initializing NVC Cache File System")
         NVCacheDiagFuncs.initializeCacheFileSystem()


      #-------------------------------------------------------------------------------------------------------
      def run(self):
         if ConfigVars[CN].get("DISABLE_NVC_TEST", 0):
            objMsg.printMsg("NVC testing bypassed by ConfigVar DISABLE_NVC_TEST")
            return

         if self.params.get('SEASERIAL', False):
            from RawBootLoader import CFlashLoad
            ofls = CFlashLoad(binFileKey = 'ELKO_CFW_BIN')
            ofls.flashBoard()
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


         import sptCmds
         
         if testSwitch.DISABLE_NVCACHE_WHILE_TESTING and (not testSwitch.NoIO):
            sptCmds.enableDiags()
            from serialScreen import sptDiagCmds
            oSerial = sptDiagCmds()
            oSerial.resetAMPs()
            sptCmds.sendDiagCmd('F"CongenConfigurationState"',timeout = 1200, printResult = True)
            objPwrCtrl.powerCycle(5000,12000,10,30)
            
         sptCmds.enableDiags()

         try:
            sptCmds.gotoLevel('N')
         except:
            objMsg.printMsg("NVC Not present or supported.")
            return

         if testSwitch.FE_0118679_231166_NVC_SEQ_REV2:

            self.initializeNVCTiming()

            self.initializeCacheFileSystem()

            self.initializeNVCMedia()

            NVCacheDiagFuncs.verifyNVCReadiness()

            self.initializeCacheFileSystem()             # Re-init CFS
         elif testSwitch.FE_0188555_210191_NVC_SEQ_REV3:

            NVCacheDiagFuncs.verifyNVCReadiness() #m6, 3601 
            NVCacheDiagFuncs.initializeCacheFileSystem()  #level O, I
            NVCacheDiagFuncs.verifyIntegrityOfCFS(1) #level O, V1     

            from base_IntfTest import CNAND_WO_Restore
            oWORst = CNAND_WO_Restore(self.dut)
            oWORst.run()
         else:
            self.initializeNVCTiming()

            self.initializeNVCMedia()


            if self.params.get("FULL_RESCAN", False):
               #entire flash
               NVCacheDiagFuncs.verifyFlashCommand(0)
            else:
               #just 1 clump
               NVCacheDiagFuncs.verifyFlashCommand(0,1)

            NVCacheDiagFuncs.eraseFlash()

            self.initializeCacheFileSystem()


         sptCmds.enableESLIP()

         if self.params.get('SEASERIAL', False):
            from RawBootLoader import CFlashLoad
            ofls = CFlashLoad(binFileKey = 'CFW_BIN')
            ofls.flashBoard()
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
