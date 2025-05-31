#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/08 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_RssScreens.py $
# $Revision: #14 $
# $DateTime: 2016/12/08 01:18:29 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_RssScreens.py#14 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
import ScrCmds, Process
from PowerControl import objPwrCtrl
from RdWr import CRdWr, CRdWrScreen
from Servo import CServo
import time, traceback, re
import serialScreen, sptCmds
from FSO import CFSO
import Utility
from ICmdFactory import ICmd

DEBUG = 0

###########################################################################################################
###########################################################################################################
class CtimedPackActivity(CState):
   """
      Class that will perform a time based sequential write.
      Input parameters
         WR_TIME: time in hours for writing
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oServ = CServo()
      self.oRdWr = CRdWr()
      CFSO().getZoneTable()

      startTime = time.time()
      writeTime = self.params.get('TIME', 2*60*60)

      cmdFunc = eval("self.%s" % self.params.get('CMD_TYPE', 'write'))

      abort = 0
      while time.time()-startTime < writeTime:
         cyl = 0
         while cyl <= max(self.dut.maxTrack):
            for head in range(self.dut.imaxHead):
               if (time.time()-startTime) > writeTime:
                  objMsg.printMsg("Loop time exceeded %s aborting write." % str(writeTime))
                  abort = 1
                  break
               if cyl <= self.dut.maxTrack[head]:
                  if DEBUG > 0:
                     mod = 1
                  else:
                     mod = 1000
                  if cyl % mod == 0:
                     objMsg.printMsg("H:%s\tT:%s\tt:%.2f" % (str(head), str(cyl), time.time()-startTime))
                  cmdFunc(cyl, head, mod)
            #End of head loop
            #Move on to next cylinder
            cyl += 1
            if abort:
               break
         #End of cyl loop
      #End of time loop

   def read(self, cyl, head, mod = 100):
      if cyl % mod == 0:
         printBER = 1
      else:
         printBER = 0
      self.oServ.rsk(cyl, head)
      self.oRdWr.ber(90, 1, 16, timeout = 120, printResult = printBER)

   def write(self, cyl, head, mod = 100):
      self.oServ.wsk(cyl, head)
      self.oRdWr.writetrack()

###########################################################################################################
###########################################################################################################
class CWriteMobile(CState):
   """
      Wrapper State to run CWriteMobile in CPC
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      defaultParams = {'bands':[
                                 {'startLBA': 0, 'endLBA':0x3FFFFF, 'midLBA':0xF423F, 'sectorCount':63, 'loops':5000, 'seed': 1},
                              ],
                       'retries': 1,
                       'timeout': 30*60,
      }

      prm = getattr(TP,'writeMobile_prm',defaultParams)
      ICmd.CRCErrorRetry(IO_CRC_RETRY_VAL)
      ICmd.SetRFECmdTimeout(prm['timeout']*1.1)

      for params in prm['bands']:
         for retry in xrange(prm['retries']):
            try:
               objMsg.printMsg("Running WriteMobile with Settings:")
               objMsg.printDict(params)
               if testSwitch.FE_0000132_347508_PHARAOH_WRITE_MOBILE_MODIFICATION:
                  res = ICmd.WriteTestSim2(params['startLBA'], params['midLBA'], params['endLBA'],0,params['sectorCount'], params.get('loops',1),0X00)
               else:
                  res = ICmd.WriteTestMobile(params['startLBA'], params['midLBA'], params['endLBA'], params['sectorCount'], params.get('loops',1), params.get('seed',1), exc = 1, timeout = prm['timeout'])
               objMsg.printMsg("Call Results from CM: %s" % (res,))
               break
            except:
               objMsg.printMsg("WriteTestMobile Failed:\n%s" % traceback.format_exc())
         else:
            ScrCmds.raiseException(13063, "Write Mobile test failed all retries.\n%s" % traceback.format_exc())

      ICmd.SetRFECmdTimeout(TP.prm_IntfTest["Default ICmd Timeout"])


###########################################################################################################
###########################################################################################################
class CTempVerifyScreen(CState):
   """
      Class that will perform an F3 Diagnostic mode long dst
      Input parameters:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess

      cellTemp = (ReportTemperature()/10.0)

      tempDeltaSpec = self.params.get('MAX_DELTA_TEMP',8)

      defaultParams = {
           'test_num'            : 235,
           'prm_name'            : 'prm_Temp_Verify_235',
           'timeout'             : 300,
           "TEMPERATURE_COEF "   : (cellTemp+tempDeltaSpec,cellTemp-tempDeltaSpec),
           "DELAY_TIME"          : 1000,
           "RETRY_LIMIT"         : 3
      }

      oProc = CProcess()
      oProc.St(defaultParams)

class CSPT_Power_Cycle(CState):
   """
      Class that will perform an F3 Diagnostic mode power on ready check for F3 code
      Input parameters: LOOPS is the number of power cycle loops to perform
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      loops = self.params.get("LOOPS", 1)
      for lCount in xrange(loops):
         objPwrCtrl.powerCycleTiming_SPT(set5V=5000, set12V=12000, offTime=10, onTime=0)

###########################################################################################################
###########################################################################################################
class CLongDST(CState):
   """
      Class that will perform an F3 Diagnostic mode long dst
      Input parameters:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import serialScreen
      timeout = getattr(TP, 'LONG_DST_TIMEOUT', 1*60*60*(self.dut.imaxHead+1))
      oSerial = serialScreen.sptDiagCmds()

      sptCmds.enableDiags()

      oSerial.smartDST(timeout, mode = "LONG")

###########################################################################################################
class CShortDST(CState):
   """
      Class that will perform an F3 Diagnostic mode long dst
      Input parameters:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import serialScreen
      timeout = getattr(TP,'SHORT_DST_TIMEOUT', 1*60*60*(self.dut.imaxHead+1))
      oSerial = serialScreen.sptDiagCmds()

      sptCmds.enableDiags()

      oSerial.smartDST(timeout, mode = "SHORT")

###########################################################################################################
###########################################################################################################
class CSPT_Zone_Beatup(CState):
   """
      Class that will perform an F3 Diagnostic mode beatup (write-read-read) of a list of zones.
      Input parameters:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      import serialScreen

      ZoneBeatupParams = {
         'RETRIES': '6,5,5,A',
         'MAX_FLAWS': 100,
         'TIMEOUT': 1*60*60*(self.dut.imaxHead+1), # default 1 hour per zone... nominal + 3 sigma is 10min
         'ZONES':[0,1,15,16],
         'MARGIN_WRITE_CLR': None
      }

      ZoneBeatupParams.update(eval(self.params.get('PARAMETER','{}')))

      zoneTimeout = self.params.get('TIMEOUT',ZoneBeatupParams['TIMEOUT'])
      retrySettings = self.params.get('RETRIES', ZoneBeatupParams['RETRIES'])
      maxFlaws = self.params.get('MAX_FLAWS', ZoneBeatupParams['MAX_FLAWS'])
      zones = self.params.get('ZONES', ZoneBeatupParams['ZONES'])
      marginWriteClearance = self.params.get('MARGIN_WRITE_CLR',ZoneBeatupParams['MARGIN_WRITE_CLR'])


      oSerial = serialScreen.sptDiagCmds()

      sptCmds.enableDiags()

      if marginWriteClearance:
         oSerial.marginClearanceTarget(marginWriteClearance)

      oSerial.initDefectLog()

      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('Y%s' % retrySettings, printResult = True)

      oSerial.setZeroPattern()

      oSerial.setErrorLogging()

      numCyls, zoneList = oSerial.getZoneInfo(printResult = True)
      objMsg.printMsg("zoneList: %s" % (zoneList,))
      numHeads = len(numCyls)
      for head in xrange(numHeads):
         zoneRanges = self.getZoneRanges(numCyls,zoneList,zones,head)
         for zRange in zoneRanges:
            oSerial.sequentialGenericCommand(zoneTimeout, 'Q', commandName = 'write-read-read', startCyl = zRange[0], numLoops = zRange[1]-zRange[0], byHead = True, head = head, loopSleepTime = 10)

      errors = oSerial.getActiveErrorLog()
      if len(errors) > maxFlaws:
         msg = "Excessive defects found during SPT Zone Beatup: %d/%d" % (len(errors) , maxFlaws)
         if testSwitch.virtualRun:
            objMsg.printMsg("VE failure turned off %s" % msg)
         else:
            ScrCmds.raiseException(10049, msg)

      if marginWriteClearance:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


   def getZoneRanges(self, numCyls, zoneList, zones, head):
      zoneRanges = []
      if testSwitch.virtualRun:
         return zoneRanges
      for zone in zones:
         try:
            zoneRange = (zoneList[head][zone],zoneList[head][zone+1])
         except KeyError:
            zoneRange = (zoneList[head][zone],numCyls[head])
         zoneRanges.append(zoneRange)
      return zoneRanges

###########################################################################################################
###########################################################################################################
class CFull_Pack_Diag_BER(CState):
   """
      Class that will perform an F3 Diagnostic mode full pack operation (read or write depending on parameters).
      Input parameters:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      import serialScreen

      fullPackDefParams = {
         'RETRIES': '6,5,5,A',
         'MAX_FLAWS': 100,
         'TIMEOUT': 1*60*60*(self.dut.imaxHead+1), # default 1 hour per surface... nominal + 3 sigma is 40min
         'MODE':'READ',
         'MARGIN_WRITE_CLR': None
      }

      fullPackDefParams.update(eval(self.params.get('PARAMETER','{}')))

      fullPackTimeout = self.params.get('TIMEOUT',fullPackDefParams['TIMEOUT'])
      retrySettings = self.params.get('RETRIES', fullPackDefParams['RETRIES'])
      maxFlaws = self.params.get('MAX_FLAWS', fullPackDefParams['MAX_FLAWS'])
      mode = self.params.get('MODE', fullPackDefParams['MODE'])
      marginWriteClearance = self.params.get('MARGIN_WRITE_CLR',fullPackDefParams['MARGIN_WRITE_CLR'])

      oSerial = serialScreen.sptDiagCmds()

      sptCmds.enableDiags()

      if marginWriteClearance:
         oSerial.marginClearanceTarget(marginWriteClearance)

      oSerial.initDefectLog()

      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('Y%s' % retrySettings, printResult = True)

      oSerial.setErrorLogging()

      if mode == 'READ':
         oSerial.readFullPack(timeout = fullPackTimeout, loopSleepTime = 10)
      else:
         oSerial.writeFullPack(timeout = fullPackTimeout, loopSleepTime = 10)

      errors = oSerial.getActiveErrorLog()
      if len(errors) > maxFlaws:
         msg = "Excessive defects found during FullPack Cmd: %d/%d" % (len(errors) , maxFlaws)
         if testSwitch.virtualRun:
            objMsg.printMsg("VE failure turned off %s" % msg)
         else:
            ScrCmds.raiseException(10049, msg)

      if marginWriteClearance:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

###########################################################################################################
###########################################################################################################
class CFull_Pack_SDBP(CState):
   """
      Class that will perform an F3 SDBP mode full pack operation (read or write depending on parameters).
      **Note this code HANGS during read/write on current F3 and is a prototype/placeholder for future SDBP development. F3 is working on the issue
      Input parameters:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      import serialScreen

      fullPackDefParams = {
         'RETRIES': {'maxWriteRetryLevelAllowed': False,
                     'maxReadRetryLevelAllowed': False,
                     'selectedRetryStep': False,
                     'maxWriteRetryCount': 5,
                     'maxReadRetryCount': 5,
                     'selectedOtfEccSetting': 0xA},
         'MAX_FLAWS': 100,
         'TIMEOUT': 1*60*60*(self.dut.imaxHead+1), # default 1 hour per surface... nominal + 3 sigma is 40min
         'MODE':'READ',
         'MARGIN_WRITE_CLR': None
      }

      fullPackDefParams.update(eval(self.params.get('PARAMETER','{}')))

      fullPackTimeout = self.params.get('TIMEOUT',fullPackDefParams['TIMEOUT'])
      retrySettings = self.params.get('RETRIES', fullPackDefParams['RETRIES'])
      maxFlaws = self.params.get('MAX_FLAWS', fullPackDefParams['MAX_FLAWS'])
      mode = self.params.get('MODE', fullPackDefParams['MODE'])
      marginWriteClearance = self.params.get('MARGIN_WRITE_CLR',fullPackDefParams['MARGIN_WRITE_CLR'])

      import sdbpCmds

      sdbpCmds.unlockDets()
      sdbpCmds.unlockDits()

      sdbpCmds.setRetries(**retrySettings)



#      rwOptsPacket = sdbpCmds.rwOptionsPacket([1,0,0,1,1,1,1])
      rwOptsPacket = sdbpCmds.rwOptionsPacket([1,0,0,1,0,0,0])

      #sdbpCmds.setTargetTrack(0,0)

      if mode == 'READ':
         sdbpCmds.seekTrack(sdbpCmds.READ_SEEK)
         sdbpCmds.setSeqRndSpace([1,1]) #Set all heads all cyls
         sdbpCmds.readTrack(rwOptsPacket, fullPackTimeout)
      else:
         #sdbpCmds.seekTrack(sdbpCmds.WRITE_SEEK)
         #objMsg.printMsg(sdbpCmds.getDriveGeometry())
         #sdbpCmds.setTargetSectorAndXferLen(0,1000)
         sdbpCmds.setDefaultTestSpace()
         sdbpCmds.setTargetAddressMode_LBA()
         sdbpCmds.setSeqRndSpace([1,1]) #Set all heads all cyls
         objMsg.printMsg("Issuing write command")
         sdbpCmds.writeTrack(rwOptsPacket, fullPackTimeout)

#      errors = oSerial.getActiveErrorLog()
#      if len(errors) > maxFlaws:
#         msg = "Excessive defects found during FullPack Cmd: %d/%d" % (len(errors) , maxFlaws)
#         if testSwitch.virtualRun:
#            objMsg.printMsg("VE failure turned off %s" % msg)
#         else:
#            ScrCmds.raiseException(10049, msg)

      if marginWriteClearance:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

###########################################################################################################
###########################################################################################################
class CMeasure_Throughput(CState):
   """
      Class that will perform an F3 Diagnostic mode throughput measurement
      Input parameters:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      import serialScreen
      oSerial = serialScreen.sptDiagCmds()
      sptCmds.enableDiags()

      basePrm = dict(TP.SampleThroughput_prm)

      if self.params:
         basePrm.update(self.params)

      retries = basePrm.pop('RETRIES',None)
      if retries:
         sptCmds.gotoLevel('2')
         sptCmds.sendDiagCmd('Y%s' % retries, printResult = True)

      oSerial.measureThroughPut(**basePrm)


class CEvaluateSlidingWindowCriteria:
   def __init__(self):
      pass

   def getTrackRange(self, defStack):
      """
      Returns the number of tracks in the defStack defect list
      """
      if len(defStack) < 2:
         return 0
      return (max(defStack) - min(defStack))+1

   def getNumDefects(self, defStack):
      """
      Returns the number of defects in the defStack
      """
      return len(defStack)

   def reduceStackDepth(self, defStack, depth):
      """
      Reduces a list/stack to items within a certain numerical range-depth
      """
      #we want to consider higher order numbers first
      defStack = list(defStack)
      defStack.sort()

      while self.getTrackRange(defStack) >= depth:
         del defStack[0]
         if len(defStack) == 0:
            break

      return defStack

   def prepDefectList(self, defectList):
      """
      In place modification of input defectList
      """
      #make a copy
      #defectList = list(defectList)

      for defect in defectList:
         defect['SECTOR_PHYS'] = int(defect['SECTOR_PHYS'],16)
         defect['TRK_LGC_NUM'] = int(defect['TRK_LGC_NUM'],16)

      def getTrackVal(row):
         return row['TRK_LGC_NUM']
      defectList.sort(key = getTrackVal)
      #return defectList

   def evaluateSlidingWindowCriteria(self, defectList, trackRange = 50, numDefectLimit = 10):
      """
      Evaluates a defect list (list of dicts) for an overlapping track rang that has number defects exceeding a limit.
      """
      evalStack = []

      self.prepDefectList(defectList)

      for index,defect in enumerate(defectList):
         sector,track = defect['SECTOR_PHYS'] ,defect['TRK_LGC_NUM']
         evalStack.append(track)

         evalStack = self.reduceStackDepth(evalStack,trackRange)

         numDefects = self.getNumDefects(evalStack)

         evalTrackRange = self.getTrackRange(evalStack)

         msg = "(%d defects out of %d tracks) in actual %d tracks evaluated against limit of %d" % (numDefects, trackRange, evalTrackRange, numDefectLimit)
         if DEBUG > 0:
            objMsg.printMsg(msg)

         if numDefects > numDefectLimit and evalTrackRange <= trackRange and evalTrackRange > 0:
            import ScrCmds
            if testSwitch.virtualRun:
               objMsg.printMsg("VE on so failure mechanism disabled")
               objMsg.printMsg(msg + " failed at %s" % (defect,))
            else:
               ScrCmds.raiseException(10049, msg + " failed at %s" % (defect,))


###########################################################################################################
###########################################################################################################
class CEncroachedWrites(CState):
   """
      Class that will perform an F3 Diagnostic mode write and read passes
      Defects encountered will be logged and merged to the P-List
      Input parameters:
         WRITE_RETRIES
         READ_RETRIES
         MAX_FLAWS
         WRITE_LOOPS
         WINDOW_RANGE
         MAX_DEFECTS_WINDOW
         if FE_0129198_399481_BIE_THRESH_IN_ENCROACHED_WRITES:
            BIE_THRESH
            ITER_CNT
            ITER_LOAD
         if FE_0130977_399481_ENCROACHED_SCREEN_VERIFY_ERRORS:
            VERIFY_WRITES
            VERIFY_READS
            REPEAT_COUNT_FOR_VERIFY
            VERIFY_BIE_THRESH
   """
   #------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.seperatorVal = "*"*40
      self.verbose = False
      self.shortTest = False

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from serialScreen import sptDiagCmds
      self.oSerial = sptDiagCmds()

      objPwrCtrl.changeBaud(Baud38400)
      sptCmds.enableDiags()
      self.numCyls, self.zones = self.oSerial.getZoneInfo(printResult = self.verbose) # properly set self.dut.imaxHead, and get relevant data

      self.fullPackTimeout = (getattr(TP, 'EncroachedCmdTimeout', 60*60*(self.dut.imaxHead+1))) * self.dut.imaxHead  # 60min/head for a read or write pack
      self.WriteRetries = self.params.get('WRITE_RETRIES', '2,8,8,4')
      self.ReadRetries = self.params.get('READ_RETRIES', '6,5,8,4')
      self.encroachedLoopCount = self.params.get('WRITE_LOOPS', getattr(TP,'EncroachedCmdLoopWrites',1))
      self.maxFlaws = self.params.get('MAX_FLAWS', getattr(TP,'maxFlaws',-1))
      self.maxWindowRangeInTracks = self.params.get('WINDOW_RANGE', getattr(TP,'maxWindowRangeInTracks',50)) #-1 to disable
      self.maxDefectsInWindow = self.params.get('MAX_DEFECTS_WINDOW', getattr(TP,'maxDefectsInWindow',10))
      if testSwitch.FE_0129198_399481_BIE_THRESH_IN_ENCROACHED_WRITES:
         self.BIE_Thresh = self.params.get('BIE_THRESH', 0x00)
         self.IterCnt = self.params.get('ITER_CNT', None)
         self.iter_load = self.params.get('ITER_LOAD', 0x00)
      if testSwitch.WA_0129851_399481_ENCROACHED_SCREEN_ERROR_FILTERING:
         self.RWERRS_TO_FILTER = self.params.get('RWERRS_TO_FILTER' , [])
      if testSwitch.FE_0130977_399481_ENCROACHED_SCREEN_VERIFY_ERRORS:
         self.verifyWriteCount = self.params.get('VERIFY_WRITES' , 0)
         self.verifyReadCount = self.params.get('VERIFY_READS' , 0)
         self.repeatCountForVerify  = self.params.get('REPEAT_COUNT_FOR_VERIFY' , 0)
         self.Verify_BIE_Thresh = self.params.get('VERIFY_BIE_THRESH', None)
         self.verifyLBAtoAnOriginalLBADistance = self.params.get('VERIFY_LBA_DISTANCE', None)

      objMsg.printMsg(self.seperatorVal)
      objMsg.printMsg("Initializing slips")
      sptCmds.gotoLevel('T')
      sptCmds.sendDiagCmd('m0,6,,,,,,22',timeout = 12000, printResult = True)
      if testSwitch.FE_0129198_399481_BIE_THRESH_IN_ENCROACHED_WRITES and self.BIE_Thresh:
         self.oSerial.setupBIEThresh(self.BIE_Thresh, self.iter_load, printResult = True)

      self.oSerial.dumpNonResidentGList()
      self.oSerial.dumpReassignedSectorList()


      self.performWRsequences()
      if testSwitch.FE_0129198_399481_BIE_THRESH_IN_ENCROACHED_WRITES and self.BIE_Thresh:
         self.oSerial.disableBIEDetector(printResult = True)
      self.oSerial.dumpNonResidentGList()
      self.oSerial.dumpReassignedSectorList()

      if testSwitch.ENC_WRT_G_TO_P:
         self.oSerial.mergeG_to_P()
         objMsg.printMsg("Re-Initializing slips")
         sptCmds.gotoLevel('T')
         sptCmds.sendDiagCmd('m0,6,,,,,,22',timeout = 12000, printResult = True, loopSleepTime = 5)
         if testSwitch.WA_0129851_399481_ENCROACHED_SCREEN_ERROR_FILTERING:
            self.oSerial.dumpNonResidentGList()
            self.oSerial.dumpReassignedSectorList()
      objPwrCtrl.changeBaud(Baud390000)

   #-------------------------------------------------------------------------------------------------------
   def setRetries(self, mode = 'R'):
      if mode == 'R':
         retries = self.ReadRetries
      elif mode == 'W':
         retries = self.WriteRetries
      sptCmds.gotoLevel('T')
      sptCmds.sendDiagCmd('O0')      # Data output mode = Quiet Mode
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('Y%s' % retries, printResult = True)
      if testSwitch.FE_0129198_399481_BIE_THRESH_IN_ENCROACHED_WRITES and self.IterCnt != None:
         sptCmds.sendDiagCmd('D%X' % self.IterCnt, printResult = True)
      sptCmds.gotoLevel('T')
      sptCmds.sendDiagCmd('O')       # Data output mode =    Formatted ASCII Mode

   #-------------------------------------------------------------------------------------------------------
   def wrAllTrksCHS(self, mode = 'R', option = 'All'):

      if self.shortTest:
         objMsg.printMsg("Screening tracks 0 to 1000 only.")
         self.oSerial.setCylinderRangeAllHeads(0, 1000)
      evenCylsAllHeads = "A13"
      oddCylsAllHeads = "A23"
      objMsg.printMsg(self.seperatorVal)
      if mode == 'R':
         objMsg.printMsg("Performing sequential read pass on %s tracks." % option)
      elif mode == 'W':
         objMsg.printMsg("Performing sequential write pass on %s tracks." % option)
      else:
         ScrCmds.raiseException(11044, "Invalid mode requested")

      self.setRetries(mode)
      sptCmds.gotoLevel('2')
      if not self.shortTest:
         sptCmds.sendDiagCmd('AD')               # Reset test space to default (full pack)
      if option == 'Even':
         sptCmds.sendDiagCmd(evenCylsAllHeads)   # Set test space to even tracks only, all heads
      elif option == 'Odd':
         sptCmds.sendDiagCmd(oddCylsAllHeads)    # Set test space to odd tracks only, all heads
      sptCmds.sendDiagCmd('S0,0')                # Seek to start
      sptCmds.sendDiagCmd('L51')                 # Loop: do not disaply errors, continue on error, stop at end of test space
      # Send command (Write or Read): continue on error
      sptCmds.sendDiagCmd('%s,,,,1' % mode, timeout = self.fullPackTimeout, printResult = True, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 30)

   #-------------------------------------------------------------------------------------------------------
   def wr_rd_LBA(self, mode = 'R', span = 0, position = 'ALL', option = 'SEQ', duration = 0):
      spanLBAs = 0x200000                             # span is given in GBtytes
      objMsg.printMsg(self.seperatorVal)

      self.setRetries(mode)
      startLBA, endLBA = self.oSerial.getLBARange()
      if position == 'ID':
         startLBA = endLBA - span*spanLBAs
      elif position == 'OD':
         endLBA = startLBA + span*spanLBAs

      if option == 'SEQ':
         self.oSerial.rw_LBAs(startLBA = startLBA, endLBA = endLBA, mode = mode, timeout = self.fullPackTimeout, printResult = True, loopSleepTime = 5)
      elif option == 'RAND':
         self.oSerial.randLBAs(startLBA = startLBA, endLBA = endLBA, mode = mode, duration = duration)
      else:
         ScrCmds.raiseException(11044, "wr_rd_LBAs: Invalid option requested")

   if testSwitch.FE_0130977_399481_ENCROACHED_SCREEN_VERIFY_ERRORS:

      #-------------------------------------------------------------------------------------------------------
      @staticmethod
      def rwCurrentTestSpaceCHS(mode, loops, timeout = 120, printResult = False):
         sptCmds.sendDiagCmd('L11,%X' % (loops,), printResult = printResult) # Loop: do not display errors, continue on error
         sptCmds.sendDiagCmd('%s,,,,1'% (mode,), timeout = timeout, printResult = printResult, DiagErrorsToIgnore = ['00003010', '00005003', '00005004'], loopSleepTime = 0.5)

      #-------------------------------------------------------------------------------------------------------
      @staticmethod
      def segregateTestTracks(testTrackList):
         """
         In: a list of tracks to be tested. [0,1,2,3,5,7,8,9,11,13,15,16,17,29]
         Out: two lists consiting of the input tracks, ([0, 2, 5, 7, 9, 11, 13, 15, 17, 29], [1, 3, 8, 16])
            split up such that no two tracks are adjacent
            Tracks are kept in first list unless they must be removed to second list,
            in order to maximize number of tracks that can be tested via adjacent writes
            without overwriting the test track itself.
            The more sparse the input tracks, the more tracks will be put in the a list.
         """
         a = []
         b = []
         previous = None
         for track in testTrackList:
            if previous != None and track == previous + 1 :
               b.append(track)
               previous = None
            else:
               a.append(track)
               previous = track
         return a, b

      #-------------------------------------------------------------------------------------------------------
      @staticmethod
      def createAdjacentTrackList(testTrackList, maxTrack):
         """
         return sorted set of tracks adjacent to testTracks, within [0, maxTrack]
         """
         adjacentTracks = set([])
         [adjacentTracks.update([track-1,track+1]) for track in testTrackList]
         return filter(lambda trk: trk > 0 and trk < maxTrack, sorted(adjacentTracks))

      #-------------------------------------------------------------------------------------------------------
      @staticmethod
      def compressTrackSpans(trackList):
         """
         return a list of (start, end) spans from a list on integers
         """
         out = []
         if trackList:
            start = trackList[0]
            last = trackList[0] - 1
            for i in trackList:
               if i == last + 1:
                  last = i
               else:
                  out.append((start,last))
                  start = i
                  last = i
            else:
               out.append((start,last))
         return out

      #-------------------------------------------------------------------------------------------------------
      @staticmethod
      def checkCloseToExisting(existingList = [], newList = [], withinRange = 1):
         """
         Return values from newList only if they fall within withinRange of
         values in withinRange.
         Both lists must consist solely of ints
         """
         expandedSet = set()
         for existingValue in existingList:
            expandedSet.update([existingValue + i for i in xrange(-withinRange, withinRange)])
         return [item for item in newList if item in expandedSet]

      #-------------------------------------------------------------------------------------------------------
      @staticmethod
      def getTestTrackPerHeadFromD10Log(loggedErrors, hdCount):
         """return dict, with hdNum as keys, and sorted list of unique tracks to be tested"""
         head_testTrack_Dict = {}
         for headNum in xrange(hdCount):
            head_testTrack_Dict.setdefault(headNum, set())
         for entry in loggedErrors:
            head_testTrack_Dict[int(entry["HD_LGC_PSN"], 16)].add(int(entry["TRK_LGC_NUM"], 16))
         for headNum, trackSet in head_testTrack_Dict.items():
            head_testTrack_Dict.__setitem__(headNum, sorted(list(trackSet)))

         return head_testTrack_Dict

      #-------------------------------------------------------------------------------------------------------
      @staticmethod
      def makeEmptyTestData(hdCount):
         """Empty structure to contain lists of tracks to read and write"""
         testData= {}
         perHeadData = {
                        "testTracks"            :  [],
                        "adjacentTracks"        :  [],
                        "adjacentTrackRanges"   :  [],
                     },
         for testSetNum in xrange(2):
            testData.__setitem__(testSetNum, {})
            for headNum in xrange(hdCount):
               testData[testSetNum].setdefault(headNum, {})

         return testData

      #-------------------------------------------------------------------------------------------------------
      def createTestTrackAndAdjacentTrackRangeData(self, head_testTrack_Dict):
         testTrackData = self.makeEmptyTestData(self.dut.imaxHead)
         for headNum, trackList in head_testTrack_Dict.items():
            # split up track so that no two test tracks are adjacent
            a, b = self.segregateTestTracks(trackList)
            testTrackData[0][headNum]["testTracks"], testTrackData[1][headNum]["testTracks"] = a, b
            # make lists of unique, sorted, tracks which are adjacent to each set of test tracks
            aWriteTracks, bWriteTracks = map(self.createAdjacentTrackList, (a, b), [self.numCyls[headNum]] * 2)
            # from adjacent track lists, compress them to spans if possible, and make list of spans
            # that covers all adjacent tracks, given the above segregation spans won't cover more than two tracks.
            testTrackData[0][headNum]["adjacentTrackRanges"] = self.compressTrackSpans(aWriteTracks)
            testTrackData[1][headNum]["adjacentTrackRanges"] = self.compressTrackSpans(bWriteTracks)
         return testTrackData

      #-------------------------------------------------------------------------------------------------------
      def generateVEData(self):
         baseEntryStr = """{
         'Count'        : '0001',
         'DIAGERR'      : '00005003',
         'HD_LGC_PSN'   : '%.1X',
         'LBA'          : '00002756E909',
         'PBA'          : '000027704814',
         'RWERR'        : '%.8X',
         'SECTOR_LGC'   : '0090',
         'SECTOR_PHYS'  : '0090',
         'SFI'          : '0004C5CE',
         'TRK_LGC_NUM'  : '%.8X',
         'TRK_PHYS_NUM' : '000222D9',
         'WDG'          : '0089'}
         """
         baseEntryStr = re.sub("[ \t\n\r]+", "", baseEntryStr,) # clean out whitespace to prevent indentation errors in eval statement
         outData = []
         outData.extend([eval(baseEntryStr % (0, int(err, 16), 55)) for err in self.RWERRS_TO_FILTER])
         outData.extend([eval(baseEntryStr % (headNum, 43110081, track)) for track in [0,1,2,3,5,7,8,9,11,13,15,16,17,20,29] for headNum in xrange(self.dut.imaxHead)])
         return outData

      #-------------------------------------------------------------------------------------------------------
      def analyzeErrorLogAndQualifyLBAsToAlt(self, newLoggedErrors, originalLBAs):
         originalLBASet = set(originalLBAs)
         newLoggedErrorsCount = len(newLoggedErrors)
         sumPerLBADict = {}
         newLBASet = set()
         for entry in newLoggedErrors:
            key = entry["LBA"]
            if key in newLBASet:
               sumPerLBADict[key] += int(entry["Count"], 16)
            else:
               newLBASet.add(key)
               sumPerLBADict[key] = int(entry["Count"], 16)
         newLBACount = len(newLBASet)
         originalLBACount = len(originalLBASet)
         sumList = sorted(list(set(sumPerLBADict.values())))
         objMsg.printMsg("Original LBA Error Count: %d, verified LBA Count %d" % (originalLBACount, newLBACount,))
         objMsg.printMsg("Error Per LBA Counts Found: %s" % str(sumList))
         LBASetPerCount = {}
         for cnt in sumList:
            LBASetPerCount.__setitem__(cnt, set())
         for LBA, errCnt in sumPerLBADict.items():
            LBASetPerCount[errCnt].add(LBA)
         LBAsToAdd = set()
         objMsg.printMsg("Number of original LBAs that did not repeat: %d" % len(originalLBASet - newLBASet))
         objMsg.printMsg("Number of new LBAs that were not original: %d" % len(newLBASet - originalLBASet))

         # print table of original, and new lba verify counts, RptCnt being the number of times the LBA was marked as an error
         objMsg.printMsg("RptCnt   Orig    New")
         for errCnt, LBASet in sorted(LBASetPerCount.items()):
            objMsg.printMsg("%6d %6d %6d" % (errCnt, len(set.intersection(originalLBASet, LBASet)), len(LBASet - originalLBASet),) )
            if errCnt >= self.repeatCountForVerify:
               LBAsToAdd.update(LBASet)
         """
         for errCnt, LBASet in sorted(LBASetPerCount.items()):
            objMsg.printMsg("Number of original LBAs that repeated %d times: %d" % (errCnt, len(set.intersection(originalLBASet, LBASet))) )
            objMsg.printMsg("Number of new LBAs that repeated %d times: %d" % (errCnt, len(LBASet - originalLBASet)))
            if errCnt >= self.repeatCountForVerify:
               LBAsToAdd.update(LBASet)
         """
         if self.verifyLBAtoAnOriginalLBADistance != None:
            # filter out LBAs that don't fall within a certain distance from an original LBA, measured  in number of LBAs
            preFilterLBAs = LBAsToAdd
            preFilterLen = len(preFilterLBAs)
            originalLBAs_ints = sorted([int(i, 16) for i in originalLBAs])
            LBAsToAdd_ints = sorted([int(i, 16) for i in LBAsToAdd])
            LBAsToAdd  = self.checkCloseToExisting(existingList = originalLBAs_ints, newList = LBAsToAdd_ints, withinRange = self.verifyLBAtoAnOriginalLBADistance)
            LBAsToAdd = set(["%.12X" % lba for lba in LBAsToAdd])
            objMsg.printMsg("Number of LBAs filtered out : %d" % (preFilterLen - len(LBAsToAdd),))
            objMsg.printMsg("LBAs filtered out : %s" % str(preFilterLBAs - LBAsToAdd))

         objMsg.printMsg("Number of LBAs verified for alting: %d" % len(LBAsToAdd))
         objMsg.printMsg("originalLBASet:\n%s" % str(originalLBASet))
         objMsg.printMsg("newLBASet:\n%s" % str(newLBASet))
         objMsg.printMsg("LBAsToAdd:\n%s" % str(LBAsToAdd))
         return sorted(list(LBAsToAdd))

      #-------------------------------------------------------------------------------------------------------
      def verifyErrors(self, loggedErrors):
         originalLBAs = [dictEntry["LBA"] for dictEntry in loggedErrors]
         # create sorted list of tracks to test, by head
         head_testTrack_Dict =  self.getTestTrackPerHeadFromD10Log(loggedErrors, self.dut.imaxHead)
         # create two groups of test track and adjacent track lists
         testTrackData = self.createTestTrackAndAdjacentTrackRangeData(head_testTrack_Dict)
         if self.Verify_BIE_Thresh:
            self.oSerial.setupBIEThresh(self.Verify_BIE_Thresh, self.iter_load, printResult = True)
         self.oSerial.initDefectLog(maxNumberDefects = 10000, printResult = self.verbose)
         self.oSerial.setErrorLogging(enable = True, printResult = self.verbose)
         self.setRetries("W")
         self.oSerial.enableRWStats()
         for testSetNum in sorted(testTrackData.keys()):  # testSetNum are 0 and 1
            # write all adjacent tracks
            objMsg.printMsg("Validating tracks on group %d" % (testSetNum,))
            ##self.setRetries("W")
            sptCmds.gotoLevel('2')
            for headNum, trackDatas in sorted(testTrackData[testSetNum].items()):
               for trackRangeTuple in trackDatas["adjacentTrackRanges"]:
                  fromTrk, toTrk = trackRangeTuple
                  objMsg.printMsg("Writing track 0x%X = %d to track 0x%X = %d, on head 0x%X, write loops: %d" % (fromTrk, fromTrk, toTrk, toTrk, headNum, self.verifyWriteCount))
                  self.oSerial.setCylinderRangeSingleHead(fromTrk, toTrk, headNum, printResult = self.verbose)
                  self.rwCurrentTestSpaceCHS(mode = "W", loops = self.verifyWriteCount, printResult = self.verbose)
            # read all test tracks
            ##self.setRetries("R")
            for headNum, trackDatas in sorted(testTrackData[testSetNum].items()):
               for testTrack in trackDatas["testTracks"]:
                  objMsg.printMsg("Reading track 0x%X = %d, on head 0x%X, read loops: %d" % (testTrack, testTrack, headNum, self.verifyReadCount))
                  self.oSerial.setCylinderRangeSingleHead(testTrack, testTrack, headNum, printResult = self.verbose)
                  self.rwCurrentTestSpaceCHS(mode = "R", loops = self.verifyReadCount, printResult = self.verbose)
         newLoggedErrors = self.oSerial.getActiveErrorLog()
         if testSwitch.virtualRun:
            newLoggedErrors = self.generateVEData()
         if self.RWERRS_TO_FILTER:
            newLoggedErrors = self.oSerial.filterListofDicts(newLoggedErrors, 'RWERR', self.RWERRS_TO_FILTER, include = False)
         LBAsToAdd = self.analyzeErrorLogAndQualifyLBAsToAlt(newLoggedErrors, originalLBAs)
         return LBAsToAdd

   #end if testSwitch.FE_0130977_399481_ENCROACHED_SCREEN_VERIFY_ERRORS:

   if testSwitch.WA_0129851_399481_ENCROACHED_SCREEN_ERROR_FILTERING:
      #-------------------------------------------------------------------------------------------------------
      def filterLoggederrorsAndAddToV4List(self):
         sptCmds.gotoLevel('L')
         sptCmds.sendDiagCmd('E0', printResult = True) # turn off error logging
         if testSwitch.virtualRun and testSwitch.FE_0130977_399481_ENCROACHED_SCREEN_VERIFY_ERRORS:
            loggedErrors = self.generateVEData()
         else:
            loggedErrors = self.oSerial.getActiveErrorLog()
         initialLogLength = len(loggedErrors)
         loggedErrors = self.oSerial.filterListofDicts(loggedErrors, 'RWERR', self.RWERRS_TO_FILTER, include = False)
         filteredLogLength = len(loggedErrors)
         objMsg.printMsg("Number of errors filtered out : %d" % (initialLogLength - filteredLogLength,))
         if testSwitch.FE_0130977_399481_ENCROACHED_SCREEN_VERIFY_ERRORS and self.verifyReadCount and self.verifyWriteCount:
            LBAsToAdd = self.verifyErrors(loggedErrors)
         else:
            LBAsToAdd = sorted(list(set([dictEntry["LBA"] for dictEntry in loggedErrors]))) # to match data returned by verifyErrors(), to avoid mismatch with number of items in V4 list
         sptCmds.gotoLevel('2')
         objMsg.printMsg("Placing %d LBAs on Alternated Sector List" % len(LBAsToAdd))
         if testSwitch.WA_0133429_399481_RETRY_ALT_LBA_IN_ENC_WR_SCRN:
            numLBAsToAdd = len(LBAsToAdd)
            for LBA in LBAsToAdd:
               for retry in xrange(2):
                  try:
                     sptCmds.sendDiagCmd('F%s,A1'%(LBA,))
                     break
                  except:
                     objMsg.printMsg("Warning, failed to alt LBA : %s" % LBA)
                     objPwrCtrl.powerCycle(baudRate = Baud38400, useESlip = 1)
                     sptCmds.enableDiags()
                     sptCmds.gotoLevel("2")
               else:
                  sptCmds.sendDiagCmd('F%s,A1'%(LBA,))

            self.oSerial.dumpNonResidentGList()
            if testSwitch.FE_0134462_399481_DUMP_V4_ALLOW_DIAG_NOT_TO_FAIL:
               altListTotals = self.oSerial.dumpReassignedSectorList(raiseException = 0)
            else:
               altListTotals = self.oSerial.dumpReassignedSectorList()

            if testSwitch.virtualRun:
               numberOfAltsFound = numLBAsToAdd
            else:
               numberOfAltsFound = altListTotals["NUMBER_OF_TOTALALTS"]
            objMsg.printMsg("%d LBAs found on Alternated Sector List" % numberOfAltsFound)
            objMsg.printMsg("altListTotals : %s" % str(altListTotals))
            if numberOfAltsFound != numLBAsToAdd:
               ScrCmds.raiseException(11044, "Number of LBAs to Alt : %d != %d LBAs found on Alternated Sector List" % (numLBAsToAdd, numberOfAltsFound,))

         else:
            [sptCmds.sendDiagCmd('F%s,A1'%(LBA,)) for LBA in LBAsToAdd]

            self.oSerial.dumpNonResidentGList()
            self.oSerial.dumpReassignedSectorList()
         return loggedErrors

   #-------------------------------------------------------------------------------------------------------
   def performWRsequences(self):
      from Drive import objDut               # Usage is objDut[PortIndex]
      if testSwitch.FE_0129198_399481_BIE_THRESH_IN_ENCROACHED_WRITES:
         self.oSerial.initDefectLog(maxNumberDefects = 10000, printResult = self.verbose)
      else:
         self.oSerial.initDefectLog(printResult = self.verbose)
      self.oSerial.setErrorLogging(enable = True, printResult = self.verbose)    # Enable error looging for all operations
      if testSwitch.FE_0129198_399481_BIE_THRESH_IN_ENCROACHED_WRITES:
         self.oSerial.enableRWStats()

      objMsg.printMsg(self.seperatorVal)
      objMsg.printMsg("Performing Encroached Write Sequence")
      objMsg.printMsg(self.seperatorVal)
      sptCmds.gotoLevel('2')
      self.wrAllTrksCHS(mode = 'W', option = 'Even',)          # Write Even Tracks
      for loopCnt in range(self.encroachedLoopCount):
         self.wrAllTrksCHS(mode = 'W', option = 'Odd')         # Write Odd Tracks
      if DEBUG > 0:
         self.oSerial.injectDefect(0, 0x15000, 100, 0)
      self.wrAllTrksCHS(mode = 'R', option = 'Even')           # Read Even Tracks
      self.wrAllTrksCHS(mode = 'W', option = 'Even')           # Write Even Tracks
      if DEBUG > 0:
         self.oSerial.injectDefect(0, 0x15000, 100, 0)
      self.wrAllTrksCHS(mode = 'R', option = 'Odd')            # Read Odd Tracks
      #self.wr_rd_LBA(mode = 'W', span = 20, position = 'OD')   # Write First 20GB
      #self.wr_rd_LBA(mode = 'R', span = 20, position = 'OD')   # Read First 20GB
      #self.wr_rd_LBA(mode = 'W', span = 20, position = 'OD', option = 'RAND', duration = 10) # Rand Write First 20GB for 10 minutes
      #self.wr_rd_LBA(mode = 'R', span = 20, position = 'OD')   # Read First 20GB
      #self.wr_rd_LBA(mode = 'W', span = 20, position = 'ID')   # Write Last 20GB
      #self.wr_rd_LBA(mode = 'R', span = 20, position = 'ID')   # Read Last 20GB
      #self.wr_rd_LBA(mode = 'W', span = 20, position = 'ID', option = 'RAND', duration = 10) # Rand Write First 20GB for 10 minutes
      #self.wr_rd_LBA(mode = 'R', span = 20, position = 'ID')   # Read Last 20GB
      if testSwitch.FE_0129198_399481_BIE_THRESH_IN_ENCROACHED_WRITES:
         self.oSerial.getZoneBERData(spc_id=self.params.get('spc_id', 1))

      if testSwitch.WA_0129851_399481_ENCROACHED_SCREEN_ERROR_FILTERING:
         totFlawsFound = self.filterLoggederrorsAndAddToV4List()
      else:
         totFlawsFound = self.oSerial.addActiveErrorsToClientList()

      self.oSerial.initDefectLog()

      if testSwitch.virtualRun:
         totFlawsFound = [{'SECTOR_PHYS': '046A', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E2F', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '0419'},
{'SECTOR_PHYS': '046B', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E30', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '041A'},
{'SECTOR_PHYS': '046C', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E31', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '041B'},
{'SECTOR_PHYS': '046D', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E32', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '041C'},
{'SECTOR_PHYS': '046E', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E33', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '041D'},
{'SECTOR_PHYS': '046F', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E34', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '041E'},
{'SECTOR_PHYS': '0470', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E35', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '041F'},
{'SECTOR_PHYS': '0471', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E36', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '0420'},
{'SECTOR_PHYS': '0472', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E37', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '0421'},
{'SECTOR_PHYS': '0473', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E38', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '0422'},
{'SECTOR_PHYS': '0474', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E39', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '0423'},
{'SECTOR_PHYS': '0475', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E3A', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '0424'},
{'SECTOR_PHYS': '0476', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E3B', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '0425'},
{'SECTOR_PHYS': '0477', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E3C', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '0426'},
{'SECTOR_PHYS': '0478', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '057E1E3D', 'TRK_LGC_NUM': '0000E89C', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000E89C', 'SECTOR_LGC': '0427'},
{'SECTOR_PHYS': '036C', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '05803EBD', 'TRK_LGC_NUM': '0000E904', 'RWERR': '43110081', 'TRK_PHYS_NUM': '0000E904', 'SECTOR_LGC': '036C'},
{'SECTOR_PHYS': '02C3', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '090EFFC7', 'TRK_LGC_NUM': '0001B39E', 'RWERR': '43110081', 'TRK_PHYS_NUM': '0001B5C4', 'SECTOR_LGC': '02C3'},
{'SECTOR_PHYS': '0440', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B519', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '042B'},
{'SECTOR_PHYS': '0441', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B51A', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '042C'},
{'SECTOR_PHYS': '0446', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B51F', 'TRK_LGC_NUM': '00008607', 'RWERR': '43110081', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0431'},
{'SECTOR_PHYS': '0447', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B520', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0432'},
{'SECTOR_PHYS': '0448', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B521', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0433'},
{'SECTOR_PHYS': '0449', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B522', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0434'},
{'SECTOR_PHYS': '044A', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B523', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0435'},
{'SECTOR_PHYS': '044B', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B524', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0436'},
{'SECTOR_PHYS': '044C', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B525', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0437'},
{'SECTOR_PHYS': '044D', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B526', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0438'},
{'SECTOR_PHYS': '044E', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B527', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0439'},
{'SECTOR_PHYS': '044F', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B528', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '043A'},
{'SECTOR_PHYS': '0450', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B529', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '043B'},
{'SECTOR_PHYS': '0451', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B52A', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '043C'},
{'SECTOR_PHYS': '0452', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B52B', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '043D'},
{'SECTOR_PHYS': '0453', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B52C', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '043E'},
{'SECTOR_PHYS': '0454', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B52D', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '043F'},
{'SECTOR_PHYS': '0455', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B52E', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0440'},
{'SECTOR_PHYS': '0456', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B52F', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0441'},
{'SECTOR_PHYS': '0457', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B530', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0442'},
{'SECTOR_PHYS': '0458', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B531', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0443'},
{'SECTOR_PHYS': '0459', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B532', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0444'},
{'SECTOR_PHYS': '045A', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B533', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0445'},
{'SECTOR_PHYS': '045B', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B534', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0446'},
{'SECTOR_PHYS': '045C', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B535', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0447'},
{'SECTOR_PHYS': '045D', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B536', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0448'},
{'SECTOR_PHYS': '045E', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B537', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0449'},
{'SECTOR_PHYS': '045F', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B538', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '044A'},
{'SECTOR_PHYS': '0460', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B539', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '044B'},
{'SECTOR_PHYS': '0461', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B53A', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '044C'},
{'SECTOR_PHYS': '0462', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B53B', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '044D'},
{'SECTOR_PHYS': '0463', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B53C', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '044E'},
{'SECTOR_PHYS': '0464', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B53D', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '044F'},
{'SECTOR_PHYS': '0465', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B53E', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0450'},
{'SECTOR_PHYS': '0466', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B53F', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0451'},
{'SECTOR_PHYS': '0467', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B540', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0452'},
{'SECTOR_PHYS': '0468', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B541', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0453'},
{'SECTOR_PHYS': '0469', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '0352B542', 'TRK_LGC_NUM': '00008607', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '00008607', 'SECTOR_LGC': '0454'},
{'SECTOR_PHYS': '043A', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '046D81B4', 'TRK_LGC_NUM': '0000B6ED', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000B6ED', 'SECTOR_LGC': '0403'},
{'SECTOR_PHYS': '043B', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '046D81B5', 'TRK_LGC_NUM': '0000B6ED', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000B6ED', 'SECTOR_LGC': '0404'},
{'SECTOR_PHYS': '043C', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '046D81B6', 'TRK_LGC_NUM': '0000B6ED', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000B6ED', 'SECTOR_LGC': '0405'},
{'SECTOR_PHYS': '043D', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '046D81B7', 'TRK_LGC_NUM': '0000B6ED', 'RWERR': 'C4090082', 'TRK_PHYS_NUM': '0000B6ED', 'SECTOR_LGC': '0406'},
{'SECTOR_PHYS': '0269', 'DIAGERR': '00005003', 'HD_LGC_PSN': '0', 'LBA': '052E57BB', 'TRK_LGC_NUM': '0000D9C1', 'RWERR': '43110081', 'TRK_PHYS_NUM': '0000D9C1', 'SECTOR_LGC': '0269'},]

      self.oSerial.populateScreenDefectTable(data = totFlawsFound, screenName = self.dut.nextState, spc_id = 1)

      if self.maxFlaws > -1:
         objMsg.printMsg("\nTotal RW errors logged:%d" % (len(totFlawsFound)))
         if len(totFlawsFound) > self.maxFlaws:
            msg = "Excessive defects found during EncroachedWriteScreen: %d/%d" % (len(totFlawsFound) , self.maxFlaws)
            if testSwitch.virtualRun:
               objMsg.printMsg("VE failure turned off: %s" % msg)
            else:
               ScrCmds.raiseException(10049, msg)

      if self.maxWindowRangeInTracks > -1:
         if self.maxFlaws == -1:
            #Only output this if we didn't above
            objMsg.printMsg("\nTotal RW errors logged:%d" % (len(totFlawsFound)))
         myWindowCriteria = CEvaluateSlidingWindowCriteria()
         myWindowCriteria.evaluateSlidingWindowCriteria(totFlawsFound,self.maxWindowRangeInTracks,self.maxDefectsInWindow)


###########################################################################################################
###########################################################################################################
class CRandomWriteAdjacentRead(CState):
   """
      Class that will perform an F3 Diagnostic mode full pack read.
      Input parameters:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      import serialScreen
      self.oSerial = serialScreen.sptDiagCmds()
      sptCmds.enableDiags()

      defaultParams = { 'startLBA':0,
                        'endLBA':  0x3567e00,
                        'stepLBA': 0x2ab980,
                        'loops' :  500,
                        'numLBAsPerXfer': 1000,
                        'maxOTFDelta': 9,
                        'maxRAWDelta': 9,
                        'maxDefects': 100,
                        'retrySettings': '6,5,5,A'}

      prm_RW_AR = getattr(TP, 'prm_RandomWritesAdjacentReads', defaultParams)

      startLBA = prm_RW_AR['startLBA']
      endLBA = prm_RW_AR['endLBA']
      seperation = prm_RW_AR['stepLBA']
      loops = prm_RW_AR['loops']
      lbasPerXfer = prm_RW_AR['numLBAsPerXfer']
      retrySettings = prm_RW_AR['retrySettings']

      randomLBAList = self.generateLBAList(startLBA, endLBA, seperation)
      tracksToReadList = map(self.oSerial.translateLBA, randomLBAList)

      objMsg.printMsg("LBA's to Write:%s" % ','.join(map(str,randomLBAList)))
      objMsg.printMsg("Center Tracks: %s" % ','.join(map(str,tracksToReadList)))

      if testSwitch.virtualRun:
         return


      retDict = self.oSerial.dumpNonResidentGList()
      #initialDefects = retDict['numEntries']
      self.oSerial.initDefectLog()
      initialDefects = 0

      objMsg.printMsg("Setting Retries")
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('Y%s' % retrySettings)

      objMsg.printMsg("Calculating Baseline BER")
      baseline = self.getRWStats(tracksToReadList, baseline = True)

      self.oSerial.setErrorLogging()


      objMsg.printMsg("Writing LBA List")
      self.writeLBAList(randomLBAList, lbasPerXfer, loops)

      objMsg.printMsg("Calculating Post Write BER")
      difference = self.getRWStats(tracksToReadList)

      diffs = []
      for index, row in enumerate(baseline):
         diffs.append(self.calculateDifferenceInDictValues(row, difference[index]))

      objMsg.printMsg("Differential BER")
      objMsg.printMsg(','.join(map(str,diffs[0].keys())))
      for row in diffs:
         objMsg.printMsg(','.join(map(str,row.values())))


      postDefects = len(self.oSerial.getActiveErrorLog()) #retDict['numEntries']

      retDict = self.oSerial.dumpNonResidentGList()
      self.oSerial.dumpReassignedSectorList()

      addedDefects = postDefects - initialDefects

      objMsg.printMsg("%d new defects found during screen." % addedDefects)
      if addedDefects > 0 and addedDefects < prm_RW_AR['maxDefects']:
         self.oSerial.mergeG_to_P()
         self.dut.stateTransitionEvent = 'reFormat'
      elif addedDefects >= prm_RW_AR['maxDefects']:
         ScrCmds.raiseException(13422, "Max defects allowed exceeded %d >= %d" % (addedDefects , prm_RW_AR['maxDefects']))

      for row in diffs:
         if row['OTF'] > prm_RW_AR['maxOTFDelta']:
            ScrCmds.raiseException(13422, "OTF Delta violated %d > %d on head %d" % (addedDefects , prm_RW_AR['maxOTFDelta'], row['HD_LGC_PSN']))
         elif row['RRAW'] > prm_RW_AR['maxRAWDelta']:
            ScrCmds.raiseException(13422, "OTF Delta violated %d > %d on head %d" % (addedDefects , prm_RW_AR['maxOTFDelta'], row['HD_LGC_PSN']))

   def calculateDifferenceInDictValues(self, dict1, dict2):
      outDict = {}
      for key in dict1.keys():
         outDict[key] = dict1[key] - dict2[key]

      return outDict

   def writeLBAList(self, lbaList, numLBAsPerXfer, loops, modulusPrint = 50):
      from random import shuffle
      lbaList = list(lbaList)

      for loopCnt in xrange(loops):
         if loopCnt % modulusPrint == 0:
            objMsg.printMsg("Loop %d writes" % loopCnt)
         shuffle(lbaList)
         for lba in lbaList:
            self.oSerial.rw_LBAs(startLBA = lba, endLBA = lba+numLBAsPerXfer-1, mode = 'W', timeout = 60, loopSleepTime = 0.1)

   def getRWStats(self, trackList, trackBand = 2, baseline = False):
      self.oSerial.zeroBERCounters()
      self.oSerial.enableRWStats()

      sptCmds.gotoLevel('2')
      self.oSerial.setStateSpace('A0')
      for trackDict in trackList:

         for x in range(2*trackBand):
            self.oSerial.seekTrack(trackDict['LOGICAL_CYL']-trackBand + x, trackDict['LOGICAL_HEAD'])
            if baseline:
               sptCmds.sendDiagCmd('W', timeout = 100, stopOnFailedRW = True, loopSleepTime = .1)

            sptCmds.sendDiagCmd('R,,,,1', timeout = 100, loopSleepTime = .1)

      return self.oSerial.getHeadBERData(printResult = True)

   def generateLBAList(self, startLBA, endLBA, LBAStep = 5000):
      from random import shuffle
      #tr = tracks range
      tr = range(startLBA, endLBA, LBAStep)
      shuffle(tr)
      return tr


###########################################################################################################
###########################################################################################################
class CATMarginDefectZones(CState):
   """
      Class that will perform an F3 Diagnostic mode full pack read.
      Input parameters:
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import serialScreen
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      self.oSerial = serialScreen.sptDiagCmds()
      sptCmds.enableDiags()

      defaultParams = { 'retryLevel':'6,5,5,A',
                        'EncroachedCmdTimeout':60*40*(self.dut.imaxHead+1),
                        'IncrementalTrackTimeout': 3,
                        'numAdjacentWrites':1,
                        'EncroachedPadRange':50,
                        'ReverseWriteBreakPoint':0x10000}
      self.ATMarginParams = defaultParams

      self.ATMarginParams.update(getattr(TP,'ATMarginParam',{}))

      self.fullPackTimeout = self.ATMarginParams['EncroachedCmdTimeout']
      self.incrementalTrackTimeout = self.ATMarginParams['IncrementalTrackTimeout']
      seperatorVal = "*"*40

      objMsg.printMsg(seperatorVal)
      objMsg.printMsg("Initializing slips")
      sptCmds.gotoLevel('T')
      sptCmds.sendDiagCmd('m0,6,,,,,,22',timeout = 1200, printResult = True)

      Plist = self.oSerial.getPList(500, printResult = False)
      plistGrps = self.oSerial.genRangeGroups(Plist,self.ATMarginParams['EncroachedPadRange'])

      self.initializeDefectListLogging()

      for head in plistGrps:
         for start,end in plistGrps[head]:
            if self.ATMarginParams['ReverseWriteBreakPoint'] <= start:
               reverseWrites = True
            else:
               reverseWrites = False
            self.ATMarginZone(head, start, end, reverseWrites)

      self.dumpDefectList()

   def initializeDefectListLogging(self):
      seperatorVal = "*"*40
      objMsg.printMsg(seperatorVal)
      objMsg.printMsg("Setting up error logging")
      sptCmds.gotoLevel('L')
      sptCmds.sendDiagCmd('c10,0,0,240000', printResult = True)
      sptCmds.sendDiagCmd('E10')
      sptCmds.sendDiagCmd('i10')
      sptCmds.sendDiagCmd('I')
      sptCmds.sendDiagCmd('E0')

   def setErrorLogging(self, enable = True):

      sptCmds.gotoLevel('L')
      if enable:
         objMsg.printMsg("Enable error logging.")
         sptCmds.sendDiagCmd('E10')
      else:
         objMsg.printMsg("Disable error logging.")
         sptCmds.sendDiagCmd('E0')

   def ATMarginZone(self, head, startTrack,endTrack, reverseWrites = False):

      seperatorVal = "*"*40
      objMsg.printMsg(seperatorVal)
      if reverseWrites:
         reverseString = " in reverse write mode"
      else:
         reverseString = ""

      objMsg.printMsg("AT margining head %d range %x-%x%s" % (head, startTrack, endTrack, reverseString))
      timeout = self.incrementalTrackTimeout* (endTrack-startTrack)

      if reverseWrites:
         evenCylsCurHead = "A52"
         oddCylsCurHead = "A62"
      else:
         evenCylsCurHead = "A12"
         oddCylsCurHead = "A22"

      loopTestSpace = "L1,%d" % ((endTrack-startTrack)+1)
      debugPrint = False

      def seekStartRange():
         if reverseWrites:
            sptCmds.sendDiagCmd('S%x,%x' % (endTrack,head), printResult = debugPrint)
         else:
            sptCmds.sendDiagCmd('S%x,%x' % (startTrack,head), printResult = debugPrint)

      def writeTracks(evenTracks = True):
         if debugPrint:
            objMsg.printMsg(seperatorVal)

         if evenTracks:
            if debugPrint:
               objMsg.printMsg("Write Even Tracks")
            cyls = evenCylsCurHead
         else:
            #odd tracks
            if debugPrint:
               objMsg.printMsg("Write Odd Tracks")
            cyls = oddCylsCurHead

         sptCmds.gotoLevel('2')
         sptCmds.sendDiagCmd('AD',printResult = debugPrint)
         sptCmds.sendDiagCmd(cyls,printResult = debugPrint)
         seekStartRange()
         sptCmds.sendDiagCmd(loopTestSpace, printResult = debugPrint)
         sptCmds.sendDiagCmd('W',timeout = timeout, printResult = debugPrint)

      def readTracks(evenTracks = True):
         if debugPrint:
            objMsg.printMsg(seperatorVal)

         if evenTracks:
            if debugPrint:
               objMsg.printMsg("Read even tracks")
            cyls = evenCylsCurHead
         else:
            #Odd tracks
            if debugPrint:
               objMsg.printMsg("Read odd tracks")
            cyls = oddCylsCurHead

         sptCmds.gotoLevel('2')
         sptCmds.sendDiagCmd(cyls,printResult = debugPrint)
         sptCmds.sendDiagCmd("Y%s" % self.ATMarginParams['retryLevel'])
         seekStartRange()
         sptCmds.sendDiagCmd(loopTestSpace,printResult = debugPrint)
         sptCmds.sendDiagCmd('R',timeout = timeout, printResult = debugPrint)

      ################ Start actual algorithm

      self.initializeDefectListLogging()
      self.setErrorLogging(enable = False)
      writeTracks(evenTracks = True)

      for x in xrange(self.ATMarginParams['numAdjacentWrites']):
         writeTracks(evenTracks = False)

      self.setErrorLogging(enable = True)

      readTracks(evenTracks = True)

      self.oSerial.addActiveErrorsToClientList()
      self.initializeDefectListLogging()

      self.setErrorLogging(enable = False)

      for x in xrange(self.ATMarginParams['numAdjacentWrites']):
         writeTracks(evenTracks = True)

      self.setErrorLogging(enable = True)

      readTracks(evenTracks = False)

      self.oSerial.addActiveErrorsToClientList()
      self.initializeDefectListLogging()

   def dumpDefectList(self):
      seperatorVal = "*"*40
      objMsg.printMsg(seperatorVal)
      objMsg.printMsg("Exec D10 defect processing")
      sptCmds.gotoLevel('L')
      sptCmds.sendDiagCmd('E0',printResult = True)
      res = sptCmds.sendDiagCmd('D10', printResult = True)
      logErrors, shortErrors = self.oSerial.parseErrorLog(res)

      ######################## DBLOG Implementaion- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      ########################

      for row in logErrors:
         for key,val in row.items():
            row[key] = int(val,16)
         rec = {
            'SPC_ID': 0,
            'OCCURRENCE': occurrence,
            'SEQ':curSeq,
            'TEST_SEQ_EVENT': testSeqEvent,
         }
         rec.update(dict(row))
         self.dut.dblData.Tables('P_ENC_LOG_DEF').addRecord(rec)

      if logErrors:
         objMsg.printDblogBin(self.dut.dblData.Tables('P_ENC_LOG_DEF'))
      else:
         objMsg.printMsg("No Defects found:\n%s" % res)

###########################################################################################################
###########################################################################################################
class CWrite_Screens(CState):
   """
      Class that will perform a time based sequential write.
      Input parameters
         WR_TIME: time in hours for writing
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.oUtility = Utility.CUtility()
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      try:
          self.runme()
      except ScrCmds.CRaiseException, exceptionData:
          # Trigger downgrade for screen failure
          if exceptionData[0][2] in [14836, 14635, 15001, 14861]:
             if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, exceptionData[0][2]):
                 objMsg.printMsg('EC%s, downgrade to %s as %s' % (exceptionData[0][2], self.dut.BG, self.dut.partNum))
             else:
                 raise exceptionData
          else:
              raise exceptionData
         
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if self.dut.BG in ['SBS'] and self.dut.nextState in ['INTRA_BAND_SCRN2','INTER_BAND_SCRN2','WRITE_SCRN2', 'SMR_WRITE_SCRN2',\
                                                           'INTRA_BAND_SCRN','INTER_BAND_SCRN_500','INTER_BAND_SCRN','SMR_WRITE_SCRN','WRITE_SCRN','WRITE_SCRN_10K']:
         return
      oRdScrn = CRdWrScreen()
      if (testSwitch.MR_RESISTANCE_MONITOR and 0):
         try:
             Process.CProcess().St(TP.PresetAGC_InitPrm_186_break)
         except:
              pass
      if self.params.get('ZAP_ON_OFF', 0):
         Process.CProcess().St(TP.zapPrm_175_zapOn)

      if self.dut.nextState in ['WRITE_SCRN']:
         if testSwitch.FE_0174019_426568_P_PRINT_BERP_SETTING_IN_LOG:
            if testSwitch.extern.PROD_PREVENT_BERP_FROM_STARTING:
               objMsg.printMsg('Running Write Screen with BERP disabled')
            else:
               objMsg.printMsg('Running Write Screen with BERP Enabled')
         if testSwitch.RUN_EAW_IN_WRITESCREEN:
            if testSwitch.FE_0147072_007955_P_EAW_USE_T240_IN_PLACE_OF_T234:
               oEAW = CEAW_T240_Screen(self.dut,self.params)
               oEAW.run()
            else:
               oEAW = CEAW_Screen(self.dut,self.params)
               oEAW.run()
      if not testSwitch.FE_0191830_320363_P_DISABLE_T50_51_IN_WRITE_SCREEN:
         CFSO().getZoneTable()
         oProc = Process.CProcess()
         # Read in number of retries for Test 50/51. If program does not have the NUM_RETRIES
         # Parameter, make the number of retries 0
         try: NumRetries = int(TP.T50T51RetryParams.get('NUM_RETRIES', 0))
         except: NumRetries = 0
         objMsg.printMsg( "Number of Retries for Test 51 is %s \n" %str(NumRetries) )
         ### Get input parameter from state table, please refer to stateparam
         temp_ATI_51 = self.oUtility.copy(eval(self.params['input_dict']))

         RetryFlag = 1 # Initialise the flag
         if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE:
            try:
               #=== Run ati
               oRdScrn.atiMeasurement(temp_ATI_51)
            except ScriptTestFailure, (failureData):
               oRdScrn.forceRezoneAfterATI(failureData[0][2])
               raise
            except ScrCmds.CRaiseException, (failureData):
               oRdScrn.forceRezoneAfterATI(failureData[0][2])
               raise
         else:
            for i in range(NumRetries+1):
               if RetryFlag == 1:
                  objMsg.printMsg("Performing ATI Testing")
                  RetryFlag = 0 # Start with a clean slate
                  try:
                     oRdScrn.atiMeasurement(temp_ATI_51)
                  except ScriptTestFailure, (failure51Data):
                     if failure51Data[0][2] in [10522] and (NumRetries - i) > 0:
                        objMsg.printMsg("EC:10522 - Retrying ATI Test (51). Num Retries left %s \n" %str(NumRetries - i))
                        RetryFlag = 1 # EC 10522 - Try once more
                        time.sleep(10) # wait for 10 seconds
                     else:
                        ScrCmds.raiseException(failure51Data[0][2], "Test 51 NumRetries left:%s \n" %str(NumRetries - i))

         if testSwitch.FE_0320123_505235_P_MIN_ERASURE_BER_SCREEN and self.dut.nextState in ['INTER_BAND_SCRN','SMR_WRITE_SCRN'] and \
            not (self.dut.BG in ['SBS'] and testSwitch.IS_2D_DRV == 0 and self.dut.HGA_SUPPLIER in ['RHO']):
            from dbLogUtilities import DBLogCheck
            dblchk = DBLogCheck(self.dut)
            if dblchk.checkComboScreen(TP.Min_Erasure_Ber_Screen_Spec) == FAIL:
               ScrCmds.raiseException(14836, "Failed for min erasure BER screen! @ Head : %s" % str(dblchk.failHead))
            else:
               objMsg.printMsg('Min erasure BER screen PASS!')

         if testSwitch.FE_0324384_518226_P_CRT2_1K_COMBO_SPEC_SCREEN and self.dut.nextState in ['INTER_BAND_SCRN', 'SMR_WRITE_SCRN']:
            from dbLogUtilities import DBLogCheck
            dblchk = DBLogCheck(self.dut)
            if dblchk.checkComboScreen(TP.CRT2_1K_COMBO_Screen_Spec) == FAIL:
               ScrCmds.raiseException(14836, "Failed for CRT2 1K COMBO SPEC SCREEN! @ Head : %s" % str(dblchk.failHead))
            else:
               objMsg.printMsg('CRT2 1K COMBO SPEC SCREEN PASS!')   

         if self.dut.nextState in ['WRITE_SCRN_10K'] and self.dut.BG not in ['SBS']:
            from dbLogUtilities import DBLogCheck
            dblchk = DBLogCheck(self.dut, 'FNC2 10K STE Screen', verboseLevel=1)
            if dblchk.checkComboScreen(TP.FNC2_10K_STE_Screen_Spec) == FAIL:
               ScrCmds.raiseException(14836, "Failed for FNC2 10K STE Screen! @ Head : %s" % str(dblchk.failHead))
            else:
               objMsg.printMsg('FNC2 10K STE Screen PASS!')   
               
         if testSwitch.COMBO_SPEC_SCRN and self.dut.nextState in ['WRITE_SCRN']:
            self.combo_Spec_Scrn()

         if testSwitch.DOS_THRESHOLD_BY_ATI and self.dut.nextState in ['WRITE_SCRN']:
            self.updateAdaptiveDOS()

         if testSwitch.FE_0112902_007955_ISOLATED_PARSE_MILLIONW_PREDICTIN_TABLE:
            prm_ATI = self.oUtility.copy(temp_ATI_51['base'])
            prm_ATI['DblTablesToParse']=['P051_MILLIONW_PREDICTIN',]
            oProc.St(prm_ATI)

         if testSwitch.WIJITA_ADJ == 1:
            oRdScrn.adjustForWIJITA(TP.WIJITAAdj_227)
         if testSwitch.auditTest: # delete any tables you dont want graded by GOTF
            try:
               self.dut.dblData.Tables('P051_ERASURE_BER').deleteIndexRecords(1)#del file pointers
               self.dut.dblData.delTable('P051_ERASURE_BER')#del RAM objects
            except:
               pass
         if (testSwitch.MR_RESISTANCE_MONITOR and 0):
            try:
               Process.CProcess().St(TP.PresetAGC_InitPrm_186_break)
            except:
               pass

         if testSwitch.WA_0112781_007955_CREATE_P051_MILLIONW_PREDICTIN_EXT:
            if not testSwitch.FE_0112902_007955_ISOLATED_PARSE_MILLIONW_PREDICTIN_TABLE:
               P051_MILLIONW_PRED = self.dut.dblData.Tables('P051_MILLIONW_PREDICTIN').tableDataObj()

            else:
               if testSwitch.virtualRun:
                  #VE doesn't have isoparse data
                  P051_MILLIONW_PRED = self.dut.dblData.Tables('P051_MILLIONW_PREDICTIN').tableDataObj()

               else:
                  P051_MILLIONW_PRED = self.dut.objSeq.SuprsDblObject['P051_MILLIONW_PREDICTIN']
               self.dut.objSeq.SuprsDblObject = {} #Clear the caller's object so there are only local refs left to clean up

            curSeq = self.dut.objSeq.getSeq()
            testSeqNum = self.dut.objSeq.getTestSeqEvent(0)
            for record in range(len(P051_MILLIONW_PRED)): #maybe typecast values into int
               absTrackIndex = abs(int(P051_MILLIONW_PRED[record]['TRK_INDEX']))
               rawBer10k = float(P051_MILLIONW_PRED[record]['RRAW_BER10K'])
               rawBer = float(P051_MILLIONW_PRED[record]['RRAW_BER'])
               calRaw = (( rawBer10k - rawBer )/ rawBer)  # (raw 10K wrt - raw ber 1 write )/ raw ber 1 write
               self.dut.dblData.Tables('P051_MILLIONW_PREDICTIN_EXT').addRecord(
                  {
                     'SPC_ID': -1,
                     'SEQ': curSeq,
                     'TEST_SEQ_EVENT': testSeqNum,
                     'ABS_TRACK_INDEX': absTrackIndex,
                     'RRAW_BER10K': rawBer10k,
                     'RRAW_BER': rawBer,
                     'CAL_RRAW': calRaw,
                  })
            objMsg.printDblogBin(self.dut.dblData.Tables('P051_MILLIONW_PREDICTIN_EXT'))
      if self.params.get('ZAP_ON_OFF', 0):
         Process.CProcess().St(TP.zapPrm_175_zapOff)
   #-------------------------------------------------------------------------------------------------------
   def updateAdaptiveDOS(self):
      head_ATI_list = {}
      residual = 0.0001
      inPrm = TP.prm_setDOSATISTEThreshold_by_ATI.copy()
      rap_prm = inPrm['C_ARRAY1']
      NeedToScanThreshold = float(TP.prm_AdaptiveDOS_Table['NeedToScanThreshold'])
      lookup_table = TP.prm_AdaptiveDOS_Table['ATI_Threshold_Table'].copy()
      trk_index_list = TP.prm_AdaptiveDOS_Table['TRK_INDEX']
      table = self.dut.dblData.Tables('P051_ERASURE_BER').chopDbLog('TEST_TYPE', 'match','erasure')
      num_write = int(table[0]['NUM_WRT'])

      for row in table:
         if int(row['TRK_INDEX']) in trk_index_list:
            head_ATI_list.setdefault(row['HD_LGC_PSN'], []).append(float(row['RRAW_BER']))
      for hd in head_ATI_list:
         hd_worst_OTF = min(head_ATI_list[hd])
         for threshold in lookup_table:
            min_OTF = lookup_table[threshold][num_write][0]
            max_OTF = lookup_table[threshold][num_write][1]
            if (hd_worst_OTF - min_OTF) > residual and (max_OTF - hd_worst_OTF) > residual:
               a = int(round(NeedToScanThreshold / threshold))
               ATIThresholdScalar = 0
               while a != 1:
                  a >>= 1
                  ATIThresholdScalar += 1
               rap_prm[-1] = ATIThresholdScalar
         inPrm.update({'C_ARRAY1': rap_prm})
         inPrm.update({'HEAD_RANGE': 1<<int(hd)})
         Process.CProcess().St(inPrm)

      Process.CProcess().St({'test_num':178, 'prm_name':'Save RAP in RAM to FLASH', 'CWORD1': 544}) #save RAP
      Process.CProcess().St(TP.prm_getDOSATISTEThreshold)
   #-------------------------------------------------------------------------------------------------------

   def combo_Spec_Scrn(self):
      # GMD/NMD combo spec screen
      if (self.dut.partNum[-3:] in TP.RetailTabList) or (self.dut.partNum[5:6] != '2'):
         objMsg.printMsg("*** PartNum %s skipping Combo Spec Scrn ***" % self.dut.partNum)
         return

      origPartNum = self.dut.partNum
      stat = 0
      OTFDict=[]
      flaws=[]
      headvendor = str(self.dut.HGA_SUPPLIER)

      objMsg.printMsg('COMBO_SPEC_SCRN_FAIL_ENABLE=%d' % (testSwitch.COMBO_SPEC_SCRN_FAIL_ENABLE))
      if headvendor == 'RHO':    # 'RHO' vrfy flaw and delta burnish
         flawLIMIT  = TP.flawLIMIT     #439
         deltaLimit = TP.deltaLimit    #0.023
         objMsg.printMsg('*' * 30 + ' RHO: combo_Flaw_Burnish_scrn ' + '*' * 30, objMsg.CMessLvl.VERBOSEDEBUG)
         objMsg.printMsg("Combo spec: 'VRFD_FLAWS' >= %d   and 'Delta Burnish' >= %f" % (flawLIMIT, deltaLimit))

         # delta burnish attr from AFH2
         deltaBurnish = DriveAttributes.get('DELTA_BURNISH','NONE').split('_')
         objMsg.printMsg("deltaBurnish= %s" % (deltaBurnish))     # debug

      else:          # 'TDK' vrfy flaw and erasure otf
         flawLIMIT = TP.flawLIMIT   #563
         OTFLimit  = TP.OTFLimit    #5.4
         objMsg.printMsg('*' * 30 + ' TDK: combo_Flaw_OTF_scrn ' + '*' * 30, objMsg.CMessLvl.VERBOSEDEBUG)
         objMsg.printMsg("Combo spec: 'VRFD_FLAWS' >= %d   and 'OTF_BER' <= %f" % (flawLIMIT, OTFLimit))

         try:
            erasureData=self.dut.dblData.Tables('P051_ERASURE_BER').chopDbLog('TEST_TYPE', 'match', 'erasure0')
            # get OTF BER
            for item in erasureData:
               if(item['TEST_TYPE']=='erasure0' and float(item['OTF_BER'])<=OTFLimit):
                  objMsg.printMsg("    Hd= %s   and ZN= %s   and OTF_BER= %f" %(item['HD_PHYS_PSN'],item['DATA_ZONE'],float(item['OTF_BER'])))     # debug
                  if item['HD_PHYS_PSN'] not in OTFDict:
                     OTFDict.append(item['HD_PHYS_PSN'])
         except:
            if testSwitch.COMBO_SPEC_SCRN_FAIL_ENABLE:
               ScrCmds.raiseException(11044, 'P051_ERASURE_BER data was not found')
            else:
               objMsg.printMsg('P051_ERASURE_BER data was not found')
               pass

      try:
         flawData=self.dut.dblData.Tables('P107_VERIFIED_FLAWS').tableDataObj()
         # get vrfy flaw
         for record in flawData:
            if (int(record['VRFD_FLAWS']) >= flawLIMIT):
               objMsg.printMsg("    Hd= %s  has VRFD_FLAWS= %s  >=  limit %d" %(record['HD_PHYS_PSN'],int(record['VRFD_FLAWS']),flawLIMIT))     # debug
               if record['HD_PHYS_PSN'] not in flaws:
                  flaws.append(record['HD_PHYS_PSN'])
      except:
         if testSwitch.COMBO_SPEC_SCRN_FAIL_ENABLE:
            ScrCmds.raiseException(11044, 'P107_VERIFIED_FLAWS data was not found')
         else:
            objMsg.printMsg('P107_VERIFIED_FLAWS data was not found')
            pass

      # if flaws exceeded for one head
      for item in flaws:
         if headvendor == 'RHO':
            # check delta burnish for the head
            delta = float(deltaBurnish[int(item)])
            if delta >= deltaLimit:
               objMsg.printMsg("    Hd= %d  Delta Burnish=%f" %(int(item), delta))     # debug
               objMsg.printMsg("Flaw count and Delta Burnish exceeded for Hd %d  " %int(item))     # debug
               stat = 1
         else:             # TDK
            # check worst OTF for the head
            if item in OTFDict:
               objMsg.printMsg("Flaw count and OTF exceeeded for hd %d" %int(item))     # debug
               stat = 1

      if stat == 1:     # failed spec
         try:
            if headvendor == 'RHO':
               objMsg.printMsg("combo_Flaw_Burnish_scrn *** Failed *** ")
               ScrCmds.raiseException(14836, "Failed Combo Spec Scrn - RHO Flaw-Burnish")
            else:             # TDK
               objMsg.printMsg("combo_Flaw_OTF_scrn     *** Failed *** ")
               ScrCmds.raiseException(14836, "Failed Combo Spec Scrn - TDK Flaw-OTF")
         except ScrCmds.CRaiseException, (failureData):
            if not testSwitch.COMBO_SPEC_SCRN_FAIL_ENABLE:
               pass
               return
            #=== Combo scrn failure: If drive is 500G OEM, waterfall to 500G SBS.
            if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE:
               if not self.downGradeOnFly(0, 14836):
                  raise
               return
            else:
               raise
      else:
         objMsg.printMsg("Combo Spec Scrn - Passed")

###########################################################################################################
###########################################################################################################
class CEncroachment_Screens(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.oUtility = Utility.CUtility()

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.FE_0111793_347508_PHARAOH_TTR:
         return
      oRdScrn = CRdWrScreen()
      try: NumRetries = int(TP.T50T51RetryParams.get('NUM_RETRIES', 0))
      except: NumRetries = 0
      objMsg.printMsg( "Number of Retries for Test 50 is %s \n" %str(NumRetries) )
      RetryFlag = 1 # Initialise the flag
      prm = self.oUtility.copy(TP.prm_Encroachment_50)
      for i in range(NumRetries+1):
         if RetryFlag == 1:
            objMsg.printMsg("Performing Encroachment Testing")
            RetryFlag = 0 # Start with a clean slate
            try: oRdScrn.encroachmentMeasurement(prm)
            except ScriptTestFailure, (failure50Data):
               if failure50Data[0][2] in [10522, 10468] and (NumRetries - i) > 0:
                  RetryFlag = 1 # EC 10522 - Try once more
                  time.sleep(10) # wait for 10 seconds
                  if prm['base']['ZONE_POSITION'] < 10:
                     prm['base']['ZONE_POSITION'] = 190 + prm['base']['ZONE_POSITION']
                  else:
                     prm['base']['ZONE_POSITION'] = prm['base']['ZONE_POSITION'] - 10
                  objMsg.printMsg("EC:%d - Retrying Encroachment Test (50) with new zone position %d. Num Retries left %s \n" % \
                     (failure50Data[0][2], prm['base']['ZONE_POSITION'], str(NumRetries - i)))
               else:
                  ScrCmds.raiseException(failure50Data[0][2], "Test 50 NumRetries left:%s \n" %str(NumRetries - i))

###########################################################################################################
###########################################################################################################
if testSwitch.FE_0138323_336764_P_T234_EAW_KOR_RETRY_SUPPORT:
   class CEAW_Screen(CState):
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)
      #-------------------------------------------------------------------------------------------------------
      def run(self):
         if testSwitch.FE_0112213_357260_DISABLE_EAW:
            objMsg.printMsg('Skipping Erase After Write T234 calls - DISABLED by PF3 Flag')
         elif testSwitch.auditTest and testSwitch.WA_0123631_399481_SKIP_T234_T252_DURING_AUDIT:
            objMsg.printMsg('Skipping Erase After Write AuditTest T234 calls - DISABLED by PF3 Flag')
         else:
            objMsg.printMsg("Performing EAW Testing")
            from Process import CProcess
            oProc = CProcess()
            oProc.St(TP.prm_Erase_afterWrite_234)
            eraseAfterWr = TP.prm_Erase_afterWrite_234.copy()
            for retry in range(3):
               startZone = eraseAfterWr['ZONE']
               if retry != 0:
                  eraseAfterWr.update({'ZONE' : startZone + 1})
               try:
                  eraseAfterWr.update({'ZONE_POSITION' : 100})
                  oProc.St(eraseAfterWr)
                  break
               except ScriptTestFailure, (failureData):
                  if failureData[0][2] == 10476:
                     try:
                        eraseAfterWr.update({'ZONE_POSITION' : 150})

                        oProc.St(eraseAfterWr)
                        break
                     except ScriptTestFailure, (failureData):
                        if failureData[0][2] == 10476:
                           if retry < 2:
                              pass
                           else:
                              raise
                        else:
                           raise
                  else:raise

            if testSwitch.FE_0129491_357260_GENERATE_T234_CHUNK_DELTA_TABLE and (TP.prm_Erase_afterWrite_234['CWORD1']&0x0002):
               # Only attempt if CWORD2, bit 1 is set - only BER2 (BIE) method generates required table.
               seq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

               T234EAWLog = self.dut.dblData.Tables('P234_EAW_ERROR_RATE2').tableDataObj()
               objMsg.printMsg('Building T234 Delta BER Table')

               for row in T234EAWLog:
                  self.dut.dblData.Tables('P_234_BER_CHUNK_DELTA').addRecord(
                     {
                     'SPC_ID'                      : 1,
                     'OCCURRENCE'                  : occurrence,
                     'SEQ'                         : seq,
                     'TEST_SEQ_EVENT'              : testSeqEvent,
                     'HEAD'                        : row['HD_PHYS_PSN'],
                     'ZONE'                        : row['DATA_ZONE'],
                     'DEGAUSS'                     : row['DEGAUSS'],
                     'BASELINE_BER_CHUNK1'         : row['BASELINE_BER_CHUNK1'],
                     'DELTA_BER_CHUNK1'            : float(row['BASELINE_BER_CHUNK1']) - float(row['EAW_BER_CHUNK1']),
                     'BASELINE_BER_CHUNK2'         : row['BASELINE_BER_CHUNK2'],
                     'DELTA_BER_CHUNK2'            : float(row['BASELINE_BER_CHUNK2']) - float(row['EAW_BER_CHUNK2']),
                     'BASELINE_BER_CHUNK3'         : row['BASELINE_BER_CHUNK3'],
                     'DELTA_BER_CHUNK3'            : float(row['BASELINE_BER_CHUNK3']) - float(row['EAW_BER_CHUNK3']),
                     })

               objMsg.printDblogBin(self.dut.dblData.Tables('P_234_BER_CHUNK_DELTA'))

elif not testSwitch.FE_0133706_357260_T234_EAW_RETRY_SUPPORT:
   class CEAW_Screen(CState):
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)
      #-------------------------------------------------------------------------------------------------------
      def run(self):
         if testSwitch.FE_0112213_357260_DISABLE_EAW:
            objMsg.printMsg('Skipping Erase After Write T234 calls - DISABLED by PF3 Flag')
         elif testSwitch.auditTest and testSwitch.WA_0123631_399481_SKIP_T234_T252_DURING_AUDIT:
            objMsg.printMsg('Skipping Erase After Write AuditTest T234 calls - DISABLED by PF3 Flag')
         else:
            objMsg.printMsg("Performing EAW Testing")
            from Process import CProcess
            oProc = CProcess()

            if testSwitch.FE_0145164_357260_P_MULTIPLE_ZONES_FOR_EAW and TP.prm_Erase_afterWrite_234.has_key('ZONES'):
               prmEAW234 = TP.prm_Erase_afterWrite_234.copy()
               prmEAW234.pop('ZONES')
               for zone in TP.prm_Erase_afterWrite_234['ZONES']:
                  prmEAW234['ZONE'] = zone
                  oProc.St(prmEAW234)
            else:
               #oProc.St(TP.prm_Erase_afterWrite_234)
               import Channel, struct
               from Process import CCudacom
               self.oOudacom = CCudacom()
               """
               Read Preamp register
               @param Address: Preamp register to read
               @param Page: Page select. Default zero, non zero value selects second page.
               @return: Error code
               """
               if testSwitch.virtualRun: return

               buf, errorCode = self.oOudacom.Fn(1329, 0xB, 0) # read
               bufBytes = struct.unpack('BB',buf)
               original_val = bufBytes[0]
               objMsg.printMsg('Read original Preamp register 0xB: %s.' % (str(bufBytes[0])))
               objMsg.printMsg('Error Code: %s during reading preamp register.' % (str(errorCode)))

               run_eaw_scrn = self.params.get('RUN_EAW_SCRN_TLEVEL10', 0)
               EAWprm = TP.prm_Erase_afterWrite_234.copy()
               testZones = EAWprm.pop('testZones',[0,22])
               testRegs = EAWprm.pop('testRegs',[0])

               if 0:
                ####################################
                # Interim for Data Collection only #
                ####################################
                  for regSetting in [0x1F, 0x19]:
                      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                      TP.prm_Erase_afterWrite_234.update({'spc_id': regSetting})
                      buf, errorCode = self.oOudacom.Fn(1330, 0xB, regSetting, 0)  # write
                      buf, errorCode = self.oOudacom.Fn(1329, 0xB, 0) # read
                      bufBytes = struct.unpack('BB',buf)
                      objMsg.printMsg('Read Preamp register 0xB: %s.' % (str(bufBytes[0])))
                      objMsg.printMsg('Error Code: %s during reading preamp register.' % (str(errorCode)))
                      for TestZone in testZones:
                          TP.prm_Erase_afterWrite_234.update({'ZONE': TestZone})
                          SetFailSafe()
                          try:
                              oProc.St(TP.prm_Erase_afterWrite_234)
                          except:
                              pass
                          ClearFailSafe()
                  objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                ####################################
                # Interim for Data Collection end #
                ####################################

               for regSetting in testRegs:#[0, 0x39]:
                  regRValue = regSetting

                  if regSetting:
                      objMsg.printMsg('*********************************************.')
                      objMsg.printMsg('Write Preamp register 0xB with value %s ***.' % regSetting)
                      objMsg.printMsg('*********************************************.')
                      buf, errorCode = self.oOudacom.Fn(1330, 0xB, 0x39, 0)  # write

                  buf, errorCode = self.oOudacom.Fn(1329, 0xB, 0) # read
                  bufBytes = struct.unpack('BB',buf)
                  regRValue = str(bufBytes[0])
                  objMsg.printMsg('Read Preamp register 0xB: %s.' % (regRValue))
                  objMsg.printMsg('Error Code: %s during reading preamp register.' % (str(errorCode)))
                  EAWprm['spc_id'] = regRValue
                  ZonePosition = EAWprm['ZONE_POSITION']

                  if run_eaw_scrn:
                     for TestZone in testZones:
                        EAWprm['ZONE'] = TestZone
                        for retry in range(2):
                           ## set back Zone position in case retry
                           EAWprm.update({'ZONE_POSITION' : ZonePosition})
                           if retry != 0:
                              EAWprm.update({'ZONE' : TestZone + 1})
                           try:
                              oProc.St(EAWprm)  # calling Test 234
                              if retry:
                                 objMsg.printMsg('DBG: EAW PASS')
                              break
                           except ScriptTestFailure, (failure234Data):
                              if failure234Data[0][2] == 10476:
                                 try:
                                    EAWprm.update({'ZONE_POSITION' : 130})
                                    objMsg.printMsg('DBG: Change Zone Position and EAW Retry')
                                    oProc.St(EAWprm)
                                    break
                                 except ScriptTestFailure, (failure234Data):
                                    if retry:
                                       raise
                                    else:
                                       objMsg.printMsg('DBG: EAW Retry')
                                       pass
                              elif retry:
                                 raise
                              objMsg.printMsg('DBG: EAW Retry')
                              pass

                  else:
                     oProc.St(TP.prm_Erase_afterWrite_234_2)

               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

            if testSwitch.FE_0129491_357260_GENERATE_T234_CHUNK_DELTA_TABLE and (TP.prm_Erase_afterWrite_234['CWORD1']&0x0002):
               # Only attempt if CWORD2, bit 1 is set - only BER2 (BIE) method generates required table.
               seq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

               T234EAWLog = self.dut.dblData.Tables('P234_EAW_ERROR_RATE2').tableDataObj()
               objMsg.printMsg('Building T234 Delta BER Table')

               for row in T234EAWLog:
                  self.dut.dblData.Tables('P_234_BER_CHUNK_DELTA').addRecord(
                     {
                     'SPC_ID'                      : 1,
                     'OCCURRENCE'                  : occurrence,
                     'SEQ'                         : seq,
                     'TEST_SEQ_EVENT'              : testSeqEvent,
                     'HEAD'                        : row['HD_PHYS_PSN'],
                     'ZONE'                        : row['DATA_ZONE'],
                     'DEGAUSS'                     : row['DEGAUSS'],
                     'BASELINE_BER_CHUNK1'         : row['BASELINE_BER_CHUNK1'],
                     'DELTA_BER_CHUNK1'            : float(row['BASELINE_BER_CHUNK1']) - float(row['EAW_BER_CHUNK1']),
                     'BASELINE_BER_CHUNK2'         : row['BASELINE_BER_CHUNK2'],
                     'DELTA_BER_CHUNK2'            : float(row['BASELINE_BER_CHUNK2']) - float(row['EAW_BER_CHUNK2']),
                     'BASELINE_BER_CHUNK3'         : row['BASELINE_BER_CHUNK3'],
                     'DELTA_BER_CHUNK3'            : float(row['BASELINE_BER_CHUNK3']) - float(row['EAW_BER_CHUNK3']),
                     })

               objMsg.printDblogBin(self.dut.dblData.Tables('P_234_BER_CHUNK_DELTA'))

else:
   class CEAW_Screen(CState):
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)
      #-------------------------------------------------------------------------------------------------------
      def run(self):
         if testSwitch.FE_0112213_357260_DISABLE_EAW:
            objMsg.printMsg('Skipping Erase After Write T234 calls - DISABLED by PF3 Flag')
         elif testSwitch.auditTest and testSwitch.WA_0123631_399481_SKIP_T234_T252_DURING_AUDIT:
            objMsg.printMsg('Skipping Erase After Write AuditTest T234 calls - DISABLED by PF3 Flag')
         else:
            objMsg.printMsg("Performing EAW Testing")
            from Process import CProcess
            oProc = CProcess()

            defaultEAWLimits = {
               'Limits'       : None ,
               'RetryCount'   : 0,
               }

            prmEAW234 = TP.prm_Erase_afterWrite_234.copy()
            EAWLimits = getattr(TP,'prm_EAW_Limits',defaultEAWLimits)
            retryCount = EAWLimits['RetryCount']

            while retryCount >= 0:

               if testSwitch.FE_0145164_357260_P_MULTIPLE_ZONES_FOR_EAW and TP.prm_Erase_afterWrite_234.has_key('ZONES'):
                  prmEAW234.pop('ZONES')
                  for zone in TP.prm_Erase_afterWrite_234['ZONES']:
                     prmEAW234['ZONE'] = zone
                     oProc.St(prmEAW234)
               else:
                  oProc.St(prmEAW234)

               seq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
               T234EAWLog = self.dut.dblData.Tables('P234_EAW_ERROR_RATE2').tableDataObj()
               objMsg.printMsg('Building T234 Delta BER Table')
               for row in T234EAWLog:
                  if int(row['SPC_ID']) == int(prmEAW234['spc_id']):
                     self.dut.dblData.Tables('P_234_BER_CHUNK_DELTA').addRecord(
                        {
                        'SPC_ID'                      : row['SPC_ID'],
                        'OCCURRENCE'                  : occurrence,
                        'SEQ'                         : seq,
                        'TEST_SEQ_EVENT'              : testSeqEvent,
                        'HEAD'                        : row['HD_PHYS_PSN'],
                        'ZONE'                        : row['DATA_ZONE'],
                        'DEGAUSS'                     : row['DEGAUSS'],
                        'BASELINE_BER_CHUNK1'         : row['BASELINE_BER_CHUNK1'],
                        'DELTA_BER_CHUNK1'            : float(row['BASELINE_BER_CHUNK1']) - float(row['EAW_BER_CHUNK1']),
                        'BASELINE_BER_CHUNK2'         : row['BASELINE_BER_CHUNK2'],
                        'DELTA_BER_CHUNK2'            : float(row['BASELINE_BER_CHUNK2']) - float(row['EAW_BER_CHUNK2']),
                        'BASELINE_BER_CHUNK3'         : row['BASELINE_BER_CHUNK3'],
                        'DELTA_BER_CHUNK3'            : float(row['BASELINE_BER_CHUNK3']) - float(row['EAW_BER_CHUNK3']),
                        })

               objMsg.printDblogBin(self.dut.dblData.Tables('P_234_BER_CHUNK_DELTA'))

               if EAWLimits['Limits']:
                  deltaTable = self.dut.dblData.Tables('P_234_BER_CHUNK_DELTA').tableDataObj()
                  needRetry = False
                  for criteria in EAWLimits['Limits']:
                     for row in deltaTable:
                        if int(row['SPC_ID']) == int(prmEAW234['spc_id']):
                           rowFailed = True
                           for test in EAWLimits['Limits'][criteria]:
                              rowFailed = rowFailed and eval("row[EAWLimits['Limits'][criteria][test]['Parameter']]" \
                                 + EAWLimits['Limits'][criteria][test]['Test']\
                                 + "EAWLimits['Limits'][criteria][test]['Limit']")
                           if rowFailed:
                              objMsg.printMsg('EAW Screen: Sample meets retry criteria check:')
                              for test in EAWLimits['Limits'][criteria]:
                                 objMsg.printMsg('   Column: %s, Value: %s, Test: %s' % (str(EAWLimits['Limits'][criteria][test]['Parameter']), \
                                             str(row[EAWLimits['Limits'][criteria][test]['Parameter']]), \
                                             EAWLimits['Limits'][criteria][test]['Test'] + str(EAWLimits['Limits'][criteria][test]['Limit'])))
                           needRetry = needRetry or rowFailed

                  if needRetry:
                     if retryCount > 0:
                        objMsg.printMsg('EAW Screen - Failed one or more retry criteria checks - Perfoming retest')
                        prmEAW234['spc_id'] += 1
                     else:
                        objMsg.printMsg('EAW Screen - Failed retry criteria checks - Retries exhausted')
                        ScrCmds.raiseException(10468, "EAW Screen: Chunk Delta Check failed")
                  else:
                     objMsg.printMsg('EAW Screen - Passed retry criteria check - continue without rerty')
                     retryCount = 0

               retryCount -= 1

         if testSwitch.FE_0146862_357260_P_ENABLE_T240_EAW_SCREEN:
            oProc.St(TP.prm_EraseAfterWrite_240)

############################################################################################################
############################################################################################################

class CEAW_T240_Screen(CState):   ###### EAW Screen using T240 ######
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      # Disabling CEAW_T240_Screen will be done in StateTable with FE_0112213_357260_DISABLE_EAW
      # This not yet an independent STATE, it's rather part of WRITE_SCRN state
      objMsg.printMsg("Performing EAW Testing")
      from Process import CProcess
      self.oProc = CProcess()

      defaultEAWSettings = {
         'LoopCount'   : 1,
         }

      prmEAW240 = TP.prm_EraseAfterWrite_240.copy()
      EAWLimits = getattr(TP,'prm_EAWSettings',defaultEAWSettings)
      loopCount = EAWLimits['LoopCount']

      if prmEAW240.has_key('ZONES'):
         zones = prmEAW240.pop('ZONES')
         for zone in zones:
            prmEAW240['ZONE'] = zone
            self.runT240(prmEAW240, loopCount)
      else:
         self.runT240(prmEAW240, loopCount)

   def runT240(self, prmEAW240, loopCount):
      for loop in range(loopCount):
         self.oProc.St(prmEAW240)


###########################################################################################################
###########################################################################################################
class CCold_Write_Screen(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.auditTest and testSwitch.WA_0123631_399481_SKIP_T234_T252_DURING_AUDIT:
         objMsg.printMsg('Skipping Cold Write AuditTest T252 calls - DISABLED by PF3 Flag')
      else:
         oProc = Process.CProcess()
         if testSwitch.FE_0124492_399481_SINGLE_T252_CALL_IN_COLD_WRITE_SCREEN:
            coldWriteParams = TP.prm_Cold_Write_252
         else:
            coldWriteParams = TP.prm_Cold_Write_252['base']
         if testSwitch.auditTest:
            prm_auditTest_T252={'prm_name'    : "prm_auditTest_T252",
                               'ZONE_POSITION': 198,} # bias towards ID to make more room for retries
            # blm FUTURE:for T252 precond,we really need to be able to set "skip track" and "num retries"..NOW HARDCODED AT 20 AND 10.
            prm_auditTest_T252.update(getattr(TP, 'prm_auditTest_T252',{})) #make changes by program in testparameters.py
            coldWriteParams.update( prm_auditTest_T252)
            objMsg.printMsg("AUDIT TEST: CCold_Write_Screen- adjusting parms...copy prm_auditTest_T252 to TP file and modify if desired",objMsg.CMessLvl.IMPORTANT)
         if testSwitch.FE_0124492_399481_SINGLE_T252_CALL_IN_COLD_WRITE_SCREEN:
            coldWriteParams['HEAD_RANGE'] = self.dut.imaxHead - 1
            if testSwitch.auditTest ==0:
               oProc.St(coldWriteParams)
            elif testSwitch.auditTest==1:
               try:
                  oProc.St(coldWriteParams)
               except ScriptTestFailure, (failureData):
                  ec = failureData[0][2]
                  if ec == 10476: #for T252 return of 10476 --> WRT/RD:DFCTS:TOO MANY DEFECTS OR SEEKS
                     objMsg.printMsg("AUDIT TEST:'No defect Free Band Found'...retry without flaw list check",objMsg.CMessLvl.IMPORTANT)
                     coldWriteParams['CWORD1'] = coldWriteParams.get('CWORD1',0)| 0x02 # bit 1
                     oProc.St(coldWriteParams)
                  else:
                     raise
         else:
            for zone in TP.prm_Cold_Write_252["ZONES"]:
               for head in xrange(self.dut.imaxHead):
                  coldWriteParams['ZONE'] = zone
                  coldWriteParams['TEST_HEAD'] = head
                  if testSwitch.auditTest ==0:
                     oProc.St(coldWriteParams)
                  elif testSwitch.auditTest==1:
                     try:
                        oProc.St(coldWriteParams)
                     except ScriptTestFailure, (failureData):
                        ec = failureData[0][2]
                        if ec == 10476: #for T252 return of 10476 --> WRT/RD:DFCTS:TOO MANY DEFECTS OR SEEKS
                           objMsg.printMsg("AUDIT TEST:'No defect Free Band Found'...retry without flaw list check",objMsg.CMessLvl.IMPORTANT)
                           coldWriteParams['CWORD1'] = coldWriteParams.get('CWORD1',0)| 0x02 # bit 1
                           oProc.St(coldWriteParams)
                        else:
                           raise

         if testSwitch.FE_0138624_357260_P_CREATE_COLD_WRITE_DELTA_TABLE:
            """
            Calculates delta between cold (first sector) and hot write error rate data
             - Data from P252_FIRST_SCTR_COLD_WRT
             - Generates temporary P_COLD_WRITE_DELTA table for Grading use only
             Parameters:
             - None
            """
            seq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
            coldWRTLog = self.dut.dblData.Tables('P252_FIRST_SCTR_COLD_WRT').tableDataObj()
            baseColdData = {}

            objMsg.printMsg('Building Base Cold Write table')
            for item in coldWRTLog:
               if not baseColdData.has_key(item['HD_PHYS_PSN']):
                  baseColdData[item['HD_PHYS_PSN']] = {}
               baseColdData[item['HD_PHYS_PSN']][item['TEST_TYPE']] = item

            objMsg.printMsg('Building Cold Write Delta table')
            for head in baseColdData:
               self.dut.dblData.Tables('P_COLD_WRITE_DELTA').addRecord(
                  {
                  'SPC_ID'                      : 1,
                  'OCCURRENCE'                  : occurrence,
                  'SEQ'                         : seq,
                  'TEST_SEQ_EVENT'              : testSeqEvent,
                  'HEAD'                        : baseColdData[head]['COLD']['HD_PHYS_PSN'],
                  'BITS_READ'                   : baseColdData[head]['COLD']['BITS_READ_CNT'],
                  'HARD_ERROR_RATE'             : baseColdData[head]['COLD']['HARD_ERROR_RATE'],
                  'HARD_ERROR_DELTA'            : float(baseColdData[head]['HOT']['HARD_ERROR_RATE']) - float(baseColdData[head]['COLD']['HARD_ERROR_RATE']),
                  'SOFT_ERROR_RATE'             : baseColdData[head]['COLD']['SOFT_ERROR_RATE'],
                  'SOFT_ERROR_DELTA'            : float(baseColdData[head]['HOT']['HARD_ERROR_RATE']) - float(baseColdData[head]['COLD']['HARD_ERROR_RATE']),
                  'OTF_ERROR_RATE'              : baseColdData[head]['COLD']['OTF_ERROR_RATE'],
                  'OTF_ERROR_DELTA'             : float(baseColdData[head]['HOT']['OTF_ERROR_RATE']) - float(baseColdData[head]['COLD']['OTF_ERROR_RATE']),
                  'RAW_ERROR_RATE'              : baseColdData[head]['COLD']['RAW_ERROR_RATE'],
                  'RAW_ERROR_DELTA'             : float(baseColdData[head]['HOT']['RAW_ERROR_RATE']) - float(baseColdData[head]['COLD']['RAW_ERROR_RATE']),
                  })

            objMsg.printDblogBin(self.dut.dblData.Tables('P_COLD_WRITE_DELTA'))


###########################################################################################################
###########################################################################################################
class CTI_ATE_Screen(CState):
   """
      CT1 -  Custom Test :
         Test Description:
            Initial Set Up:
            Read Mode with GPCC test default values in all registers.
            Load Reg 15  with 0x04 ( WrtOff = 1)
            Load Reg17  with 0x10  (WRFLTCNTL  = 1)
         Do the following for all heads
            Clear FCODE  register 7 by writing 00.
            Switch to head "n".
            Delay 50 uSecs.
            Read & Check if   FCODE Register is  00.

   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      self.verbose = True

   def screenHead(self, head):
      sptCmds.gotoLevel('7')
      sptCmds.sendDiagCmd('s0,7,0', printResult = self.verbose) #Clear FCODE register

      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('H%d' % head, printResult = self.verbose) #switch to head

      sptCmds.gotoLevel('7')
      sptCmds.sendDiagCmd('s0,9,2', printResult = self.verbose) #???
      time.sleep(0.03) #Spec is 2ms but we need to be > 2ms and with python resolution we need this min of 0.03
      sptCmds.sendDiagCmd('t0,7', altPattern = "Preamp Reg 07 = 00", printResult = self.verbose, loopSleepTime = 1)

   def initScreen(self):
      sptCmds.gotoLevel('7')
      sptCmds.sendDiagCmd('s0,21,10', printResult = self.verbose) #Set WRFLTCTR
      sptCmds.sendDiagCmd('s0,f,44', printResult = self.verbose) #Set WRTOFF

   def run(self):
      sptCmds.enableDiags()
      self.initScreen()

      for head in xrange(self.dut.imaxHead):
         try:
            self.screenHead(head)
         except:
            ScrCmds.raiseException(14803, "TI ATE screening failed for head %d" % (head,))

      try:
         sptCmds.enableESLIP()
      except:
         objPwrCtrl.powerCycle()

###########################################################################################################
###########################################################################################################
class CSerial_Truput(CState):
   """
      Class that will perform an F3 Diagnostic mode throughput measurement
      Updated to Level 2 'T': Rev 0014.0000
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.TruputParams = {}
      self.retry = 0
      self.FullReadRemoval = False
      self.TruputLst = []
      self.IDmaxLBA = 0
      self.dblogname = 'P598_ZONE_XFER_RATE'
      self.MaxTransfLen = -1
      self.OFWFailure = 0
      self.oUtility = Utility.CUtility()

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if self.dut.BG in ['SBS'] and self.dut.nextState in ['SP_WR_TRUPUT', 'SP_RD_TRUPUT']:
         return
      if self.dut.BG not in ['SBS'] and self.dut.nextState in ['SP_WR_TRUPUT2', 'SP_RD_TRUPUT2']:
         return
      try:
         if hasattr(TP, 'temperatureLoggingList'):
            if TP.temperatureLoggingList.get('FIN2'):
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10)
         self.runtruput()
         if self.dut.SkipPCycle:
            objMsg.printMsg("runtruput SkipPCycle...")
         else:
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10)
      except:
         msg = "runtruput traceback=%s" % traceback.format_exc()
         objMsg.printMsg(msg)
         raise

   #-------------------------------------------------------------------------------------------------------
   def runtruput(self):
      oSerial = serialScreen.sptDiagCmds()
      oSerial.enableDiags()

      if self.retry >= 0:
         oSerial.syncBaudRate(Baud38400)

      cmdDict = oSerial.getCommandVersion('2', 'T')
      objMsg.printMsg('2>T rev=%s' % (`cmdDict`))
      if cmdDict['majorRev'] < 14:
         ScrCmds.raiseException(10345, "CSerial_Truput needs Level 2 'T': Rev 14 or above. Current rev=%s" % cmdDict['majorRev'])

      Factor = oSerial.GetPhysicalLogicalSectorSize()
      if testSwitch.SMRPRODUCT:
         objMsg.printMsg("Factor=%s" % (Factor))
      else:
         AveSecTrack, RawSecTrack = oSerial.GetSecTrack()
         MaxSectors = 0xFFF00 - 1   # firmware code limit
         self.MaxTransfLen = int(MaxSectors / Factor / max(RawSecTrack))
         objMsg.printMsg("Factor=%s self.MaxTransfLen=%s RawSecTrack data=%s" % (Factor, self.MaxTransfLen, `RawSecTrack`))

      oSerial.setZeroPattern(printResult = True)

      sptCmds.gotoLevel('2')
      cmd, rwTracing, timeout = self.GetCmd()
      if rwTracing == True:
         oSerial.ToggleRwTracing(error = False, command = True, retry = False)
         sptCmds.sendDiagCmd("T0,,,,,1", timeout=timeout, printResult=False)  # workaround to load truput overlay to memory, ignore all outputs

      ###################### send thruput command ######################
      LiveSensorDet = False
      shockPatterns = ['OPShock', 'LargeShock']
      if testSwitch.FE_0283639_402984_TURN_OFF_THRUPUT_RAW_AND_LARGE_SHOCK_DETECT:
         shockPatterns = ['OPShock']
      for i in xrange(3):  # retries
         try:
            OPShock = False
            if testSwitch.SMRPRODUCT:
               # Temperature monitoring before Read throughput test
               if self.dut.currentState == 'SP_RD_TRUPUT' and not (testSwitch.M11P or testSwitch.M11P_BRING_UP):
                  from Temperature import CTemperature
                  oTemp = CTemperature()
                  SOCtemp = oTemp.getDeviceTemp(devSelect=3)
                  HDAtemp = oTemp.getDeviceTemp(devSelect=2)
                  cellTemp = "%0.1f" % (ReportTemperature()/10.0)
                  objMsg.printMsg("Before ReadThroughput Test: SOC temperature = %s degC, HDA temperature = %s degC, Cell temperature = %s" % (SOCtemp, HDAtemp, cellTemp))   
                  self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
                           {
                           'SPC_ID'       : 5,
                           'OCCURRENCE'   : 1,
                           'SEQ'          : self.dut.seqNum+1,
                           'TEST_SEQ_EVENT': 0,
                           'STATE_NAME'   : self.dut.nextState,
                           'DRIVE_TEMP'   : HDAtemp,
                           'CELL_TEMP'    : cellTemp,
                           'ELEC_TEMP'    : SOCtemp,
                           })
                  sptCmds.gotoLevel('2')
               data = sptCmds.sendDiagCmd(cmd, timeout=timeout, printResult=True) # print result for eval purposes
               if self.dut.currentState == 'SP_RD_TRUPUT' and not (testSwitch.M11P or testSwitch.M11P_BRING_UP):
                  SOCtemp = oTemp.getDeviceTemp(devSelect=3)
                  HDAtemp = oTemp.getDeviceTemp(devSelect=2)
                  cellTemp = "%0.1f" % (ReportTemperature()/10.0)
                  objMsg.printMsg("After ReadThroughput Test: SOC temperature = %s degC, HDA temperature = %s degC, Cell temperature = %s" % (SOCtemp, HDAtemp, cellTemp))   
                  self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
                           {
                           'SPC_ID'       : 5,
                           'OCCURRENCE'   : 2,
                           'SEQ'          : self.dut.seqNum+1,
                           'TEST_SEQ_EVENT': 0,
                           'STATE_NAME'   : self.dut.nextState,
                           'DRIVE_TEMP'   : HDAtemp,
                           'CELL_TEMP'    : cellTemp,
                           'ELEC_TEMP'    : SOCtemp,
                           })
                  
                  hotSOC_criteria = TP.hotSOC_temp_crt
                  objMsg.printMsg("SOC temp screening criteria %s degC, SOCtemp %s degC, Drivetemp %s degC" % (hotSOC_criteria, SOCtemp, HDAtemp))
                  if (SOCtemp - HDAtemp) > hotSOC_criteria:
                     objMsg.printMsg("Drive's SOC temp is very hot, %s degC!! Potential bad TIM contact or Fast SOC.", (SOCtemp))
                     ScrCmds.raiseException(12179,"Very hot SOC temp detected.")
                  else:
                     objMsg.printMsg("Pass SOC temp screening!!")

            else:
               data = sptCmds.sendDiagCmd(cmd, timeout=timeout, printResult=False)
            if testSwitch.virtualRun:
               data = TP.truput_ve_data_pass      # good data
            if DEBUG:
               objMsg.printMsg('cmd=%s data=%s' % (cmd, `data`))  # raw data is needed for data collection

            for shock in shockPatterns:         # detect shock events
               if shock in data:
                  OPShock = True
                  ScrCmds.raiseException(10569,"Serial Truput OPShock detected")
            if 'LS PFS= 2000' in data: #RW CT requested to look for live sensor activation in throughput test
               LiveSensorDet = True
               ScrCmds.raiseException(10578,"Serial Truput LS PFS detected.")
            if 'error' in data:
               ScrCmds.raiseException(10578,"Zone write or read error detected.")

            self.TruputLst, rwLst = oSerial.ProcessTruputData(data)
            break
         except:
            objMsg.printMsg("truput test traceback=%s" % traceback.format_exc())
            if OPShock:
               objMsg.printMsg("OPShock detected!")
               raise
            if LiveSensorDet:
               objMsg.printMsg("LiveSensor detected!")
               raise
      else:
         ScrCmds.raiseException(10578, "Unable to run serial truput test")

      rwMode = self.TruputParams.get('rwMode', 0)
      for i in xrange(len(self.TruputLst)):
         self.TruputLst[i]['rwMode'] = rwMode

      if DEBUG:
         objMsg.printMsg("Original self.TruputLst=%s" % self.TruputLst)

      if Factor > 1:
         for i in xrange(len(self.TruputLst)):
            NewLBA = int(self.TruputLst[i]['StartLBA'], 16) * Factor
            self.TruputLst[i]['StartLBA'] = "%X" % NewLBA

            NewLBA = int(self.TruputLst[i]['EndLBA'], 16) * Factor
            if testSwitch.SMRPRODUCT: #to follow IO EndLBA definition
               if (NewLBA >= 7):
                  NewLBA = NewLBA - 7
            self.TruputLst[i]['EndLBA'] = "%X" % NewLBA

         if DEBUG:
            objMsg.printMsg("After multiple log sector conversion self.TruputLst=%s" % self.TruputLst)

      if 0: # remove conversion to correlate to H2Bench data instead of CPC IO.
         objMsg.printMsg("MB to MiB conversion")
         Conversion = (1.024 * 1.024)
         try:
            for i in xrange(len(self.TruputLst)):
               try:
                  NewDataRate = float(self.TruputLst[i]['Cal_Truput']) / Conversion
                  self.TruputLst[i]['Cal_Truput'] = "%.3f" % NewDataRate
                  NewDataRate = float(self.TruputLst[i]['Truput']) / Conversion
                  self.TruputLst[i]['Truput'] = "%.3f" % NewDataRate
               except ValueError:
                  objMsg.printMsg("Error: TruputLst[%s] = %s" %(i,self.TruputLst[i]))
                  raise

            if DEBUG:
               objMsg.printMsg("After MB to MiB conversion self.TruputLst=%s" % self.TruputLst)
         except:
            ScrCmds.raiseException(10443, "Throughput conversion error")

      # get sector track info (to calculate end lba for full read removal)
      if self.FullReadRemoval == True:
         if (len(AveSecTrack) % len(self.TruputLst)):
            ScrCmds.raiseException(14025, "Unable to run serial truput test. AveSecTrack and TruputLst len mismatch")

         sTrackLen = getattr(TP, 'prm_sp_wr_truput', {}).get("transfLen", '8')
         TrackLen = int(sTrackLen, 16)

         lbaFactor = 1.2      # assume 20% more LBA written

         for i in xrange(len(self.TruputLst)):
            sEnd = int(self.TruputLst[i]['StartLBA'], 16) + int(TrackLen * AveSecTrack[i] * lbaFactor * Factor)
            objMsg.printMsg("sEnd=%s Hex=%X TrackLen=%s AveSecTrack=%s" % (sEnd, sEnd, TrackLen, AveSecTrack[i]))
            self.TruputLst[i]['EndLBA'] = "%X" % sEnd

         objMsg.printMsg("Full read removal self.TruputLst=%s" % self.TruputLst)

      data = oSerial.getIdentifyBuffer(0, 0xFF) # Get maxLBA with serial /HI cmd
      data += oSerial.getIdentifyBuffer(0x100, 0x1FF)
      self.IDmaxLBA = self.oUtility.numSwap(data[200:205]) # Get IDDefault48bitLBAs

      if self.FullReadRemoval == False and not testSwitch.virtualRun:
         self.PutDbLog()
         if hasattr(TP,'prm_598_spec'):

            if self.dut.SkipPCycle:
               objMsg.printMsg("prm_598_spec SkipPCycle")
            else:
               objPwrCtrl.powerCycle()

            from base_IntfTest import CZoneXferTest
            oTruput = CZoneXferTest(self.dut, self.params)
            oTruput.IDmaxLBA = self.IDmaxLBA
            self.params["XFER_TYPE"] = "{'spc_id' : %d}" % self.TruputParams.get('spc_id', 0)
            try:
               oTruput.DataThroughput_Check(self.dblogname)
            except ScrCmds.CRaiseException, (failureData):
               ec = failureData[0][2]
               raise (failureData)
            except:     # catch generic exceptions not raised by ScrCmds.CRaiseException
               ScrCmds.raiseException(14001, "Undefined error.")
         if self.OFWFailure:
            ScrCmds.raiseException(48176, 'Potential Offtrack write failure')

      # clean up LBAs that are larger than maxlba or measured thruput is 0 (invalid)
      for i in self.TruputLst[:]:
         if int(i['StartLBA'], 16) >= self.IDmaxLBA or (float(i['Truput']) <= 0):
            if DEBUG:
               objMsg.printMsg("Removing %s as lba larger than maxlba" % i)
            self.TruputLst.remove(i)

      if (self.TruputParams.get('rwMode', 0) == 1): # for write only
         objMsg.printMsg('Appending test range for WR_VERIFY...')
         for i in self.TruputLst:
            RWDict = []
            RWDict.append ('Read')
            RWDict.append (int(i['StartLBA'], 16))
            RWDict.append (int(i['EndLBA'], 16) )
            RWDict.append ('CSerial_Truput')
            if DEBUG:
               objMsg.printMsg('CSerial_Truput WR_VERIFY appended - %s' % (RWDict))
            TP.RWDictGlobal.append (RWDict)

      if testSwitch.EnableDebugLogging_T598:
         #sptCmds.enableDiags()
         oSerial.quickDiag()
         oSerial.gotoLevel('T')
         oSerial.dumpReassignedSectorList()
         oSerial.gotoLevel('1')
         oSerial.getCriticalEventLog()

   def PutDbLog(self):
      iMaxZone = int(self.TruputLst[-1]['Zone'], 16) + 1
      iMaxHead = int(self.TruputLst[-1]['Head'], 16) + 1

      Invalid = -1
      Truput = [Invalid] * iMaxZone
      Cal_Truput = [Invalid] * iMaxZone
      Ratio = [Invalid] * iMaxZone
      StartLBA = [Invalid] * iMaxZone
      EndLBA = [Invalid] * iMaxZone

      OFWXferRatio = eval(self.params.get('OFWXferRatio', '0.0'))
      def GetData(old, new, AllowZero = False, ChkMin = True):
         ret = old
         if ChkMin == True:
            oper = min
         else:
            oper = max
         if AllowZero == True and new == 0:
            ret = 0
         elif new > 0:
            if old == Invalid:
               ret = new
            else:
               ret = oper(old, new)
         return ret

      if not testSwitch.FE_0314630_402984_FIX_SERIAL_ZONE_AVG_CAL:    # Use old method of getting zone average

         def GetAve(old, new):
            if new <= 0:      # if new is invalid, no change
               return old
            if old <= 0:
               return new
            return (old + new) / 2

         for i in self.TruputLst:
            tmpzone = int(i['Zone'], 16)
            Truput[tmpzone] = GetAve(Truput[tmpzone], float(i['Truput']))
            Cal_Truput[tmpzone] = GetAve(Cal_Truput[tmpzone], float(i['Cal_Truput']))
            Ratio[tmpzone] = GetAve(Ratio[tmpzone], float(i['Ratio']))

            #Truput[tmpzone] = GetData(Truput[tmpzone], float(i['Truput']), AllowZero = False, ChkMin = True)
            #Cal_Truput[tmpzone] = GetData(Cal_Truput[tmpzone], float(i['Cal_Truput']), AllowZero = False, ChkMin = True)
            #Ratio[tmpzone] = GetData(Ratio[tmpzone], float(i['Ratio']), AllowZero = False, ChkMin = True)

            if (float(i['Truput']) > 0): # if thruput is invalid, no change
               StartLBA[tmpzone] = GetData(StartLBA[tmpzone], int(i['StartLBA'], 16), AllowZero = True, ChkMin = True)
               EndLBA[tmpzone] = GetData(EndLBA[tmpzone], int(i['EndLBA'], 16), AllowZero = True, ChkMin = False)

      else:    # New method to get average thruput

         def getAverage(truputdata):
            """ Returns a list of average zones per head
            Ex: [Zn0, Zn1, .. Zn]
            Where: Zn = average zone data for all the heads
            """
            try:
               # reconstruct data to make zone the key and head data the values in the list to simplify zone data averaging
               dict_by_zone = {}
               for zn in xrange(iMaxZone):
                  l = []
                  for zone_info in truputdata.values():
                     l.append(zone_info[zn])
                  l = [x for x in l if x > 0]   # filter zero values
                  dict_by_zone[zn] = l

               # populate invalid data with -1 otherwise get the average zone value
               #return [float(sum(zone_data)/len(zone_data)) if len(zone_data)>0 else -1 for zone_data in dict_by_zone.values()]
               list_by_zone = []
               for zone_data in dict_by_zone.values():
                  if len(zone_data)>0:
                     list_by_zone.append(float(sum(zone_data)/len(zone_data)))
                  else:
                     list_by_zone.append(-1)
               return list_by_zone

            except IndexError:
               ScrCmds.raiseException(14554, "Throughput data integrity error")


         # create temporary containers
         truput_dict = {}           # truput head data per zone
         caltruput_dict = {}        # caltruput head data per zone
         ratio_dict = {}            # ratio data per zone
         temp_list_truput = []
         temp_list_caltruput = []
         temp_list_ratio = []
         prev_head = 0
         next_head = 0
         tmphead = 0

         for line_data in self.TruputLst:
            tmpzone = int(line_data['Zone'], 16)
            next_head = int(line_data['Head'], 16)
            if next_head != prev_head:    # detect head info change to clear temp truput list
               tmphead = next_head
               prev_head = next_head
               temp_list_truput = []
               temp_list_caltruput = []
               temp_list_ratio = []
            else:
               tmphead = prev_head

            # get 'Throughput' data
            truput = float(line_data['Truput'])
            if truput > 0:
               StartLBA[tmpzone] = GetData(StartLBA[tmpzone], int(line_data['StartLBA'], 16), AllowZero = True, ChkMin = True)
               EndLBA[tmpzone] = GetData(EndLBA[tmpzone], int(line_data['EndLBA'], 16), AllowZero = True, ChkMin = False)
            temp_list_truput.append(truput)
            truput_dict[tmphead] = temp_list_truput

            # get 'CalThruput' data
            caltruput = float(line_data['Cal_Truput'])
            temp_list_caltruput.append(caltruput)
            caltruput_dict[tmphead] = temp_list_caltruput

            # get 'Ratio' data
            ratio = float(line_data['Ratio'])
            temp_list_ratio.append(ratio)
            ratio_dict[tmphead] = temp_list_ratio
            
            if tmpzone in [140, 141, 142, 143, 144, 145]:
               if caltruput > 0.0 and ratio < OFWXferRatio:
                  objMsg.printMsg('Zn: %d, ratio: %s < %sMB/s'%(tmpzone, ratio, OFWXferRatio))
                  self.OFWFailure = 1

         Truput = getAverage(truput_dict)
         Cal_Truput = getAverage(caltruput_dict)
         Ratio = getAverage(ratio_dict)

      Offset = self.TruputParams.get('TruputOffset', [])
      if len(Offset) == 2:
         FirstValidZone = -1
         LastValidZone = -1
         MinLBA = self.IDmaxLBA
         MaxLBA = 0

         objMsg.printMsg('StartLBA=%s' % StartLBA)
         for i in xrange(iMaxZone):
            if StartLBA[i] < self.IDmaxLBA and Truput[i] > 0:
               if StartLBA[i] < MinLBA:
                  FirstValidZone = i
                  MinLBA = StartLBA[i]
               if StartLBA[i] > MaxLBA:
                  LastValidZone = i
                  MaxLBA = StartLBA[i]
         self.dut.iLastValidZone = LastValidZone + 1
         objMsg.printMsg('MinLBA=%s MaxLBA=%s' % (MinLBA,MaxLBA))

         objMsg.printMsg("SP Truput offset=%s" % Offset)
         objMsg.printMsg("FirstValidZone=%s LastValidZone=%s" % (FirstValidZone, LastValidZone))
         objMsg.printMsg("Before Truput=%s" % (Truput))

         if FirstValidZone >= 0:
            Truput[FirstValidZone] = float(Truput[FirstValidZone]) + float(Offset[0])
            Ratio[FirstValidZone] = "%.3f" % (float(Truput[FirstValidZone]) / float(Cal_Truput[FirstValidZone]))
         if LastValidZone >= 0:
            Truput[LastValidZone] = float(Truput[LastValidZone]) + float(Offset[-1])
            Ratio[LastValidZone] = "%.3f" % (float(Truput[LastValidZone]) / float(Cal_Truput[LastValidZone]))

         objMsg.printMsg("After Truput=%s" % (Truput))

      curSeq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      for i in xrange(iMaxZone):
         if StartLBA[i] < self.IDmaxLBA and Truput[i] > 0:
            self.dut.dblData.Tables(self.dblogname).addRecord({
               'SPC_ID': self.TruputParams.get('spc_id', 0),
               'OCCURRENCE': occurrence,
               'SEQ': curSeq,
               'TEST_SEQ_EVENT': testSeqEvent,

               'DATA_ZONE': str(i),
               'DATA_RATE': str(Truput[i]),
               'CALC_RATE': str(Cal_Truput[i]),
               'RATIO': str(Ratio[i]),

               'START_LBA': '%X' % StartLBA[i],
               'END_LBA': '%X' %  EndLBA[i],
               'LBAS_XFERED': (EndLBA[i] - StartLBA[i]), # note, this must be numeral

               'TIME': str(0),
               'STATUS': str(0),
               'PARAMETER_1': str(0),
               'LBA_AT_MIN_TIME': str(0),
               'LBA_AT_MAX_TIME': str(0),
               'MIN_TIME_PER_XFER': str(0),
               'MAX_TIME_PER_XFER': str(0),
            })

      objMsg.printDblogBin(self.dut.dblData.Tables(self.dblogname), spcId32 = self.TruputParams.get('spc_id', 0))


   def GetCmd(self):
      defaultParams = {
         'rwMode'       :  0,       # 0=Read 1=write
         'zoneNumber'   :  None,    # None=All Zones
         'headNumber'   :  None,    # None=All Heads
         'cylSkew'      :  '',      # Default cyl skew
         'headSkew'     :  '',      # Default head skew
         'zoneSkew'     :  '',      # Default zone skew
         'skewStepSize' :  '',      # Default skew step size
         'transfLen'    :  '8',     # Transfer Length In Tracks (default 8)
         'transfOffset' :  '',      # Transfer Offset In Tracks
         'maxRetries'   :  '',      # Max Number of Retries
         'rwTracing'    :  False,   # Enable read write tracing
         'SkipWrBefRd'  :  1,       # bit 14: set=skip write for read throughput test, cleared=write before read
         'LimitTxLen'   :  True,    # If transfLen exceeds drive, use MaxTransfLen automatically
         'timeout'      :  1800,    # Max timeout
         }

      self.TruputParams = getattr(TP, 'TruputParams', defaultParams)
      if self.params.get('XFER_TYPE', 0):
         self.TruputParams = eval(self.params["XFER_TYPE"])

      rwMode      = self.TruputParams.get('rwMode', 0)
      zoneNumber  = self.TruputParams.get('zoneNumber', None)
      headNumber  = self.TruputParams.get('headNumber', None)
      cylSkew     = self.TruputParams.get('cylSkew', '')
      headSkew    = self.TruputParams.get('headSkew', '')
      zoneSkew    = self.TruputParams.get('zoneSkew', '')
      skewStepSize= self.TruputParams.get('skewStepSize', '')

      if self.FullReadRemoval == True:    # for full read removal, force min transfer len
         tmpLen = "1"
      else:
         tmpLen = self.TruputParams.get('transfLen', '8')

         if testSwitch.PBIC_SUPPORT and \
            ((self.dut.BG in ['SBS'] and len(ConfigVars[CN].get('PBICSwitches', '00000')) >= 4 and int(ConfigVars[CN].get('PBICSwitches', '00000')[3]) > 0) or\
             (self.dut.BG not in ['SBS'] and len(ConfigVars[CN].get('PBICSwitchesOEM', '00000')) >= 4 and int(ConfigVars[CN].get('PBICSwitchesOEM', '00000')[3]) > 0)):
            objMsg.printMsg("CSerial_Truput PBIC check")
            from PBIC import ClassPBIC
            objPBIC = ClassPBIC()
            pbic_test_enabled = objPBIC.PBIC_Control_bd()
            if pbic_test_enabled == 0:
               objMsg.printMsg("PBIC: before tmpLen=%s" % tmpLen)
               tmpLen = "%X" % (int(tmpLen, 16) / 2)
               objMsg.printMsg("PBIC: after tmpLen=%s" % tmpLen)


      transfOffset= self.TruputParams.get('transfOffset', '')
      maxRetries  = self.TruputParams.get('maxRetries', '')
      rwTracing   = self.TruputParams.get('rwTracing', False)
      SkipWriteBeforeRead = self.TruputParams.get('SkipWrBefRd', 1)
      LimitTxLen = self.TruputParams.get('LimitTxLen', True)
      timeout     = self.TruputParams.get('timeout', 1800)

      if LimitTxLen == True and not testSwitch.SMRPRODUCT:
         tmpLen = "%X" % min(self.MaxTransfLen, int(tmpLen, 16))
         objMsg.printMsg("transfLen=%s" % tmpLen)

      if zoneNumber == None:
         zoneNumber = 0
         AllZones = 1
      if headNumber == None:
         headNumber = 0
         AllHeads = 1
      if (testSwitch.TRUNK_BRINGUP & testSwitch.M10P) or testSwitch.ROSEWOOD7 or testSwitch.M11P or testSwitch.M11P_BRING_UP:
         options = zoneNumber | (AllZones<<16) | (headNumber<<8) | (AllHeads<<17) | (rwMode << 15) | (SkipWriteBeforeRead << 14)
      else:
         options = zoneNumber | (AllZones<<7) | (headNumber<<8) | (AllHeads<<11) | (rwMode << 15) | (SkipWriteBeforeRead << 14)

      cmd = "T%X,%s,%s,%s,%s,%s,%s,%s" % (options, cylSkew, headSkew, zoneSkew, skewStepSize, tmpLen, transfOffset, maxRetries)
      return cmd, rwTracing, timeout

###########################################################################################################
###########################################################################################################
class CQBERFullZone(CState):
   """
      Class made only for calling QBER test that runs on every cyl
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from RdWr import CRdWrScreen
      oRdWr = CRdWrScreen()
      SetFailSafe()
      oRdWr.QBERFullStroke(ECClevel = 0) # RRAW BER
      oRdWr.QBERFullStroke(ECClevel = 6) # OTF BER T-level 10
      ClearFailSafe()

###########################################################################################################
###########################################################################################################
class CGetDriveStats(CState):
   '''
      get/check drive degradation
   '''
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      defaultParams = \
         {  'LimitDeltaRaw': 5.0,
            'LimitDeltaOTF': 5.0,
            'LimitDeltaRMR': 5.0,
            'LimitDeltaVGA': 80.0,
            'timeout' : 30,
         }
      prm_DriveStats = getattr(TP, 'prm_DriveStats', defaultParams)
      LimitDeltaRaw = prm_DriveStats['LimitDeltaRaw']
      LimitDeltaOTF = prm_DriveStats['LimitDeltaOTF']
      LimitDeltaRMR = prm_DriveStats['LimitDeltaRMR']
      LimitDeltaVGA = prm_DriveStats['LimitDeltaVGA']
      timeout = prm_DriveStats['timeout']

      ########## 1. Get RAW/OTF data ##########
      # "Rd/Wr stats"
      try:
         OldHeadData = self.dut.objData.retrieve('HeadBERData')
         cmds = [(CTRL_W, 'L>'), ('`', 'L>'), ]
      except KeyError:
         OldHeadData = []
         cmds = [(CTRL_W, 'L>'), ('iFFFD', 'L>'), ('`', 'L>'), ]

      if DEBUG:
         objMsg.printMsg("OldHeadData=%s" % OldHeadData)

      import serialScreen
      oSerial = serialScreen.sptDiagCmds()
      sptCmds.enableDiags()

      oSerial.getZoneInfo(printResult = True)   # update head information
      sptCmds.gotoLevel('L')

      data = ''
      for cmd, resp in cmds:
         data = sptCmds.sendDiagCmd(cmd, timeout=timeout, altPattern=resp, printResult=True)
         if DEBUG:
            objMsg.printMsg("Sent cmd=%s Data=%s" % (`cmd`, `data`))

      HeadTablePat = "^Hd\s*(?P<HD_PHYS_PSN>\d+)\s*(?P<RBIT>[\d\.]+)\s*(?P<HARD>[\d\.]+)\s*(?P<SOFT>[\d\.]+)\s*(?P<OTF>[\d\.]+)\s*(?P<RRAW>[\d\.]+)\s*(?P<RSYM>[\d\.]+)?\s+(?P<SYM>[\d.]+)?\s+(?P<WBIT>[\d.]+)\s+(?P<WHRD>[\d\.]+)\s+(?P<WRTY>[\d\.]+)"
      headComp = re.compile(HeadTablePat)
      NewHeadData = []

      for line in data.splitlines():
         match = headComp.search(line)
         if match:
            NewHeadData.append(oSerial.convDictItems(match.groupdict(), float))

      if DEBUG:
         objMsg.printMsg("NewHeadData=%s" % NewHeadData)
         objMsg.printMsg("self.dut.imaxHead=%s" % self.dut.imaxHead)

      if len(NewHeadData) != self.dut.imaxHead:
         ScrCmds.raiseException(13422, "Fail reading RAW/OTF numHeads mismatch")

      if not OldHeadData == []:     # do a compare of old and new
         for i in xrange(self.dut.imaxHead):
            DeltaRaw = abs(OldHeadData[i]['RRAW'] - NewHeadData[i]['RRAW'])
            if DEBUG:
               objMsg.printMsg("Hd=%s DeltaRaw=%f" % (i+1, DeltaRaw))
            if DeltaRaw > LimitDeltaRaw:
               ScrCmds.raiseException(13422, "Fail delta RAW")

            DeltaOTF = abs(OldHeadData[i]['OTF'] - NewHeadData[i]['OTF'])
            objMsg.printMsg("Hd=%s DeltaOTF=%f" % (i+1, DeltaOTF))
            if DeltaOTF > LimitDeltaOTF:
               ScrCmds.raiseException(13422, "Fail delta OTF")
      else:
         self.dut.objData.update({'HeadBERData': NewHeadData})

      ########## 2. Get RMR ##########
      try:
         OldRMRData = self.dut.objData.retrieve('RMRData')
      except KeyError:
         OldRMRData = []

      if DEBUG:
         objMsg.printMsg("OldRMRData=%s" % OldRMRData)

      sptCmds.gotoLevel('7')
      cmd = "X"
      data = sptCmds.sendDiagCmd(cmd, timeout=timeout, altPattern='7>', printResult=True)
      if DEBUG:
         objMsg.printMsg("Sent cmd=%s Data=%s" % (`cmd`, `data`))

      NewRMRData = []
      pat = re.compile('Head (\S+).*Resistance (\S+)')
      for line in data.splitlines():
         m = pat.search(line)
         if m:
            d = {}
            d['RMR'] = int(m.group(2), 16)
            NewRMRData.append(d)

      if DEBUG:
         objMsg.printMsg("NewRMRData=%s" % NewRMRData)

      if not OldRMRData == []:     # do a compare of old and new
         for i in xrange(self.dut.imaxHead):
            DeltaRMR = abs(OldRMRData[i]['RMR'] - NewRMRData[i]['RMR'])
            objMsg.printMsg("Head=%s DeltaRMR=%f" % (i+1, DeltaRMR))

            if DeltaRMR > LimitDeltaRMR:
               ScrCmds.raiseException(13422, "Fail delta RMR")
      else:
         self.dut.objData.update({'RMRData': NewRMRData})

      ########## 3. Get VGA ##########
      try:
         OldVGAData = self.dut.objData.retrieve('VGAData')
      except KeyError:
         OldVGAData = []

      if DEBUG:
         objMsg.printMsg("OldVGAData=%s" % OldVGAData)

      data = ''
      for i in xrange(3):
         try:
            sptCmds.gotoLevel('4')
            data = sptCmds.sendDiagCmd('k0,0,0', timeout=timeout, altPattern='4>', printResult=True)
            objMsg.printMsg("Retry=%s VGA data=%s" % (i, `data`))
            if data.find('Rev 0: ') > -1 and data.find('\r\nF3 4>') > -1:
               break
         except:
            objMsg.printMsg("Exception VGA data=%s" % (`data`))
            objMsg.printMsg("Traceback=%s" % traceback.format_exc())
            data = ''
            time.sleep(3)
      else:
         ScrCmds.raiseException(13422, "Fail reading VGA")

      NewVGAData = []
      m = re.search('Rev 0: ', data)      # begin string
      n = re.search('\r\nF3 4>', data)    # end string
      if m and n:
         r = data[m.end(): n.start()].split()
         lst = []
         for i in r:
            lst.append(int(i))

         d = {}
         d['VGA_MIN'] = min(lst)
         d['VGA_MAX'] = max(lst)
         d['VGA_AVE'] = sum(lst)/len(lst)
         NewVGAData.append(d)

      if DEBUG:
         objMsg.printMsg("NewVGAData=%s" % NewVGAData)

      if not OldVGAData == []:     # do a compare of old and new
         DeltaVGAMin = abs(OldVGAData[0]['VGA_MIN'] - NewVGAData[0]['VGA_MIN'])
         DeltaVGAMax = abs(OldVGAData[0]['VGA_MAX'] - NewVGAData[0]['VGA_MAX'])
         DeltaVGAAve = abs(OldVGAData[0]['VGA_AVE'] - NewVGAData[0]['VGA_AVE'])
         objMsg.printMsg("DeltaVGA Min Max Ave=%f %f %f. Limit=%f" % (DeltaVGAMin, DeltaVGAMax, DeltaVGAAve, LimitDeltaVGA))

         if DeltaVGAMin > LimitDeltaVGA or DeltaVGAMax > LimitDeltaVGA or DeltaVGAAve > LimitDeltaVGA:
            ScrCmds.raiseException(13422, "Fail delta VGA")
      else:
         self.dut.objData.update({'VGAData': NewVGAData})


###########################################################################################################
###########################################################################################################
class CThermistorCheck(CState):
   '''
      get/check drive degradation
   '''
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      defaultParams = \
         {  'min_temp': 20,
            'max_temp': 55,
         }
      prm_thermistor_check = getattr(TP, 'prm_thermistor_check', defaultParams)
      min_temp = prm_thermistor_check['min_temp']
      max_temp = prm_thermistor_check['max_temp']

      from Temperature import CTemperature
      thermistor = CTemperature().getF3Temp()
      objMsg.printMsg("thermistor data=%s" % thermistor)

      if thermistor < min_temp or thermistor > max_temp:
         ScrCmds.raiseException(13422, "Fail thermistor check")

###########################################################################################################
###########################################################################################################
class CLoadUnload(CState):
   '''
      hard/soft load/unload current check
   '''
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def get_current(self, data, factor):
      current = -1
      m = re.search('Bemf Cal Retries', data)       # begin string
      n = re.search('Load/Unload Peak Current', data)    # end string
      if m and n:
         s = (data[m.end(): n.start()]).strip()
         current = float(s) * factor

      return current

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      defaultParams = \
         {
            'timeout'       : 30,      # serial timeout in s
            'loop'          : 2,       # 120 loops takes about 100 mins
            'factor'        : 0.0203,  # get current factor (info from Eric Lee/TheinWin Zaw)
            'current_limit' : 500.0,   # 500 mA current limit that should not exceed limit_count
            'limit_count'   : 5,       # fail if more than 3 counts above limit
            'current_min'   : 35.0,    # fail if any value less than this
            'current_max'   : 800.0,   # fail if any value above this
         }
      prm_lul = getattr(TP, 'prm_lul_check', defaultParams)
      timeout        = prm_lul['timeout']
      loop           = prm_lul['loop']
      factor         = prm_lul['factor']
      current_limit  = prm_lul['current_limit']
      limit_count    = prm_lul['limit_count']
      current_min    = prm_lul['current_min']
      current_max    = prm_lul['current_max']

      import serialScreen
      oSerial = serialScreen.sptDiagCmds()
      hlul = []
      slul = []

      objMsg.printMsg("########## Hard load unload ##########")
      for i in xrange(loop):
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         sptCmds.enableDiags()
         sptCmds.gotoLevel('T')
         data = sptCmds.sendDiagCmd("O4", timeout=timeout, altPattern='T>', printResult=True)
         sptCmds.gotoLevel('3')
         data = sptCmds.sendDiagCmd("b1", timeout=timeout, altPattern='3>', printResult=True)

         current = self.get_current(data, factor)
         if DEBUG:
            objMsg.printMsg("Sent Data=%s" % (`data`))
            objMsg.printMsg("current = %f mA" % current)

         hlul.append(current)

      objMsg.printMsg("########## Soft load unload ##########")
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      for i in xrange(loop):
         sptCmds.enableDiags()
         sptCmds.gotoLevel('2')
         data = sptCmds.sendDiagCmd("Z", timeout=timeout, altPattern='2>', printResult=True)
         data = sptCmds.sendDiagCmd("U", timeout=timeout, altPattern='2>', printResult=True)
         if DEBUG:
            objMsg.printMsg("Data=%s" % (`data`))

         sptCmds.gotoLevel('T')
         data = sptCmds.sendDiagCmd("O4", timeout=timeout, altPattern='T>', printResult=True)

         sptCmds.gotoLevel('3')
         data = sptCmds.sendDiagCmd("b1", timeout=timeout, altPattern='3>', printResult=True)

         current = self.get_current(data, factor)
         if DEBUG:
            objMsg.printMsg("Sent Data=%s" % (`data`))
            objMsg.printMsg("current = %f mA" % current)

         slul.append(current)

      hlul_count     = 0
      slul_count     = 0
      objMsg.printMsg("Current values: hlul=%s slul=%s" % (hlul, slul))
      for i in hlul:
         if i < current_min or i > current_max:
            ScrCmds.raiseException(13422, "Fail hard load unload min max")
         if i > current_limit:
            hlul_count += 1

      for i in slul:
         if i < current_min or i > current_max:
            ScrCmds.raiseException(13422, "Fail soft load unload min max")
         if i > current_limit:
            slul_count += 1

      if hlul_count > limit_count:
         ScrCmds.raiseException(13422, "Fail hard load unload count")
      if slul_count > limit_count:
         ScrCmds.raiseException(13422, "Fail soft load unload count")

      if min(hlul) < current_min:
         ScrCmds.raiseException(13422, "Fail hard load unload min")
      if min(slul) < current_min:
         ScrCmds.raiseException(13422, "Fail soft load unload min")

      if max(hlul) > current_max:
         ScrCmds.raiseException(13422, "Fail hard load unload max")
      if max(slul) > current_max:
         ScrCmds.raiseException(13422, "Fail soft load unload max")

###########################################################################################################
class CEAW_Beatup(CState):
   """
      Class that performs EAW BEATUP Test in CPC
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.dut.driveattr['BOB_SCRIPT'] = 'NONE'
      oSerial = serialScreen.sptDiagCmds()

      sptCmds.enableDiags()
      startLBA_List = []
      Test_track=[]
      IwHead=[]
      ber_spc_id=9
      IwPlus=1

      #Collect baseline BER
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('I,3',printResult = True)
      sptCmds.sendDiagCmd('PAAAA,AAAA', printResult = True)
      sptCmds.sendDiagCmd('A0',printResult = True)
      for head in range(self.dut.imaxHead):
         objMsg.printMsg('Write background')
         Retry = 0
         while Retry < 21:
            try:
               trk = 0x25+250*Retry
               sptCmds.gotoLevel('2')
               sptCmds.sendDiagCmd('S%X,%X' %(trk,head), printResult = True)
               sptCmds.sendDiagCmd('W',printResult = True)

               #Correct Write current for each head.
               sptCmds.gotoLevel('7')
               if testSwitch.virtualRun:
                  res = "t0,4\n\nPreamp Reg 04 = A3\n\nF3 7>"
               else:
                  res = sptCmds.sendDiagCmd('t0,4',printResult = True)
               res = res.replace('\n','')
               patt = "Preamp Reg 04 = (?P<WRITE_CURRENT>[0-9A-Fa-f])"
               match = re.search(patt, res)
               if match:
                  Iw = int(match.groupdict()['WRITE_CURRENT'], 16)
                  objMsg.printMsg("Hd:%s, Iw is : %s" %(head,Iw))
                  IwHead.append(Iw)

               sptCmds.sendDiagCmd('R',printResult = True)
               Test_track.append(trk)
               break
            except:
               Retry += 1
         else:
            ScrCmds.raiseException(10888,"Write Background Failed!")
      oSerial.enableRWStats(printResult = True)
      objMsg.printMsg("Iw List : %s" %IwHead)
      objMsg.printMsg("Test Track List : %s" %Test_track)
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('A0',printResult = True)
      for head in range(self.dut.imaxHead):
         sptCmds.sendDiagCmd('S%X,%X' %(Test_track[head],head), printResult = True)
         sptCmds.sendDiagCmd('L1,14',printResult = True)
         sptCmds.sendDiagCmd('R',printResult = True)
      oSerial.getZoneBERData(spc_id = ber_spc_id, printResult = False)
      for head in range(self.dut.imaxHead):
         trackInfo = oSerial.getTrackInfo(Test_track[head],head)
         startLBA_List.append(trackInfo['FIRST_LBA'])
      objMsg.printMsg("StartLBA List : %s" %startLBA_List)

      #Increase write current by step from default value.
      sptCmds.gotoLevel('7')
      for head in range(self.dut.imaxHead):
         if (IwHead[head]+IwPlus)>15:
            Itemp=15
         else:
            Itemp=IwHead[head]+IwPlus
         sptCmds.sendDiagCmd('I%X,3,%X,0,0' %(Itemp,head), printResult = True)

      try:
        sptCmds.sendDiagCmd(CTRL_R, timeout = 10, Ptype='PChar') #For changed online mode to switch form Diag mode to IO mode.
      except:
        pass

      ICmd.HardReset()
      data = ICmd.IdentifyDevice()
      if data['LLRET'] != OK:
         ScrCmds.raiseException(13420, "IdentifyDevice failed %s" % str(data))
      else:
         objMsg.printMsg("Identify Device passed")

      result = ICmd.SetFeatures(0x02)['LLRET']  # Enable Write cache
      if result != OK:
         objMsg.printMsg('Failed SetFeatures - Eable Write Cache')

      DO_READS_MOD_100 = 1
      for lba in startLBA_List:

         startLBA = lba*8
         endLBA = startLBA+(204*8)
         stepLBA_1 = sectorCount = 8
         test_loop = 50000
         stepLBA_2 = 40

         ICmd.FlushCache();

         pattern="B"
         result = ICmd.FillBuffByte(WBF, pattern)['LLRET']
         if result != OK:
            objMsg.printMsg('Failed to Fill 0x%2X Data' %pattern)

         objMsg.printMsg('SequentialWrite %d loop at StartLBA : %s, EndLBA : %s by %s LBA' %(test_loop, startLBA, endLBA, stepLBA_2))


         if DO_READS_MOD_100:
            for loop in xrange(test_loop/100):
              result = ICmd.SequentialWriteDMAExt(startLBA, endLBA, stepLBA_2, sectorCount,0, 0, 100)
              ICmd.FlushCache();
              if result['LLRET'] != OK:
                 ScrCmds.raiseException(10888,"SequentialWrite Beatup Failed! : %s" % str(result))


              objMsg.printMsg("SequentialRead at loop: %d " %(loop))
              result = ICmd.SequentialReadDMAExt(startLBA, endLBA, stepLBA_1, sectorCount,0)
              if result['LLRET'] != OK:
                 ScrCmds.raiseException(10888,"SequentialRead Failed! : %s" % str(result))

         else:
            result = ICmd.SequentialWriteDMAExt(startLBA, endLBA, stepLBA_2, sectorCount,0, 0, test_loop)
            ICmd.FlushCache();
            if result['LLRET'] != OK:
               ScrCmds.raiseException(10888,"SequentialWrite Beatup Failed! : %s" % str(result))

            objMsg.printMsg("SequentialRead")
            result = ICmd.SequentialReadDMAExt(startLBA, endLBA, stepLBA_1, sectorCount,0)
            if result['LLRET'] != OK:
               ScrCmds.raiseException(10888,"SequentialRead Failed! : %s" % str(result))

      #BER after EAW test
      sptCmds.enableDiags()
      oSerial.enableRWStats(printResult = True)
      objMsg.printMsg("Test Track List : %s" %Test_track)
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('A0',printResult = True)
      for head in range(self.dut.imaxHead):
        sptCmds.sendDiagCmd('S%X,%X' %(Test_track[head],head), printResult = True)
        sptCmds.sendDiagCmd('L1,14',printResult = True)
        sptCmds.sendDiagCmd('R',printResult = True)
      oSerial.getZoneBERData(spc_id = ber_spc_id, printResult = False)
      #Clean track
      objMsg.printMsg('Clean Trk')
      sptCmds.sendDiagCmd('A0',printResult = True)
      sptCmds.gotoLevel('2')
      sptCmds.sendDiagCmd('P0000,0000', printResult = True)
      for head in range(self.dut.imaxHead):
         sptCmds.sendDiagCmd('S%X,%X' %(Test_track[head],head), printResult = True)
         sptCmds.sendDiagCmd('W',printResult = True)
      objMsg.printMsg('EAW Beatup passed')
      self.dut.driveattr['BOB_SCRIPT'] = 'PASS'

###########################################################################################################
class CSP_Apple(CState):
   """

   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut.failBluenun = False


   def SetBlueNunFail(self, value = True):
      self.dut.CustomCfgTestFailure = 'BLUENUN_SLIDE'
      if not self.dut.failBluenun:
         #only set to new value if prev value was false (passing)
         self.dut.failBluenun = value

         self.dut.dblData.Tables('P_BLUE_NUN_SCORE').addRecord(
                        {
                        'FAIL': int(self.dut.failBluenun)
                        })
         objMsg.printDblogBin(self.dut.dblData.Tables('P_BLUE_NUN_SCORE'))

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if 1:
            DEBUG = 1
            objMsg.printMsg('Start CSP_Apple')
            prm_Apple_PerformanceScreens = TP.prm_Apple_PerformanceScreens
            objMsg.printMsg("Performing Serial Port Apple Screen with parameters %s" % (prm_Apple_PerformanceScreens,))

            if testSwitch.virtualRun:
               tabledata = [{'STATUS': '0', 'DATA_RATE': '105.24865', 'OCCURRENCE': 1, 'SPC_ID': 1, 'START_LBA': '0',       'LBAS_XFERED': '2171446', 'RATIO': '0.96', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '212236',   'CALC_RATE': '106.73273', 'DATA_ZONE': '0',  'SEQ': 1, 'LBA_AT_MIN_TIME': '100E23',    'LBA_AT_MAX_TIME': '20027A',  'MAX_TIME_PER_XFER': '52991', 'TIME': '20689794', 'MIN_TIME_PER_XFER': '379'},
                            {'STATUS': '0', 'DATA_RATE': '103.21940', 'OCCURRENCE': 1, 'SPC_ID': 1, 'START_LBA': '200DBB0', 'LBAS_XFERED': '2177923', 'RATIO': '0.96', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '2221733',  'CALC_RATE': '107.05519', 'DATA_ZONE': '1',  'SEQ': 1, 'LBA_AT_MIN_TIME': '200E2A2',   'LBA_AT_MAX_TIME': '220DEA9', 'MAX_TIME_PER_XFER': '71229', 'TIME': '10302705', 'MIN_TIME_PER_XFER': '379'},
                            {'STATUS': '0', 'DATA_RATE': '105.83213', 'OCCURRENCE': 1, 'SPC_ID': 2, 'START_LBA': '0',        'LBAS_XFERED': '2171446', 'RATIO': '0.97', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '212236',   'CALC_RATE': '106.73273', 'DATA_ZONE': '0',  'SEQ': 2, 'LBA_AT_MIN_TIME': '3022F8',   'LBA_AT_MAX_TIME': '195CE',    'MAX_TIME_PER_XFER': '23740', 'TIME': '10211448', 'MIN_TIME_PER_XFER': '428'},
                            {'STATUS': '0', 'DATA_RATE': '104.22791', 'OCCURRENCE': 1, 'SPC_ID': 2, 'START_LBA': '200DBB0',  'LBAS_XFERED': '2177923', 'RATIO': '0.97', 'PARAMETER_1': '0', 'TEST_SEQ_EVENT': 1, 'END_LBA': '2221733',  'CALC_RATE': '107.05519', 'DATA_ZONE': '1',  'SEQ': 2, 'LBA_AT_MIN_TIME': '20CD709',  'LBA_AT_MAX_TIME': '200DC2F',  'MAX_TIME_PER_XFER': '15191', 'TIME': '10203016', 'MIN_TIME_PER_XFER': '362'}]
            else:
               try:
                  tabledata = self.dut.dblData.Tables('P598_ZONE_XFER_RATE').tableDataObj()
               except:
                  ScrCmds.raiseException(14537, "No valid data in P598_ZONE_XFER_RATE")

            objMsg.printMsg('self.dut.iLastValidZone=%s' % self.dut.iLastValidZone)
            if DEBUG > 0:
               objMsg.printMsg('tabledata=%s' % tabledata)

            #create a spec by zone for read and write so we can handle all screens in 1 loop- pick the lowest value per zone..etc

            zone_spec_w = []
            zone_spec_r = []
            for dataZone in range( self.dut.iLastValidZone ):
               spec_w = 0
               spec_r = 0
               for zoneSet in prm_Apple_PerformanceScreens['MIN_ZONE_SPEC']:
                  if dataZone == zoneSet[0]:
                     spec_w = spec_r = zoneSet[1]
                     break

               try:
                  r_val_min = prm_Apple_PerformanceScreens['MIN_MAX_READ'][dataZone][0]
                  w_val_min = prm_Apple_PerformanceScreens['MIN_MAX_WRITE'][dataZone][0]
                  r_val_max = prm_Apple_PerformanceScreens['MIN_MAX_READ'][dataZone][1]
                  w_val_max = prm_Apple_PerformanceScreens['MIN_MAX_WRITE'][dataZone][1]
               except:
                  r_val_min = 0
                  w_val_min = 0
                  r_val_max = 0xFFFF
                  w_val_max = 0xFFFF

               #objMsg.printMsg('zone_spec_r.append=%s %s' % (max(r_val_min, spec_r ), r_val_max))
               #objMsg.printMsg('zone_spec_w.append=%s %s' % (max(w_val_min, spec_w ), w_val_max))

               zone_spec_r.append( ( max(r_val_min, spec_r ), r_val_max ) )
               zone_spec_w.append( ( max(w_val_min, spec_w ), w_val_max ) )

            objMsg.printMsg("Checking against specs zone_spec_w= %s" % (zone_spec_w,))
            objMsg.printMsg("Checking against specs zone_spec_r= %s" % (zone_spec_r,))
            #create a place-holder for the R and W data to calc later R,W
            readToWriteThreshold = [[0,0] for i in range( self.dut.iLastValidZone ) ]
            for row in tabledata:

               dataZone = int(row['DATA_ZONE'])
               dataRate = float(row['DATA_RATE'])

               if DEBUG: objMsg.printMsg("spc_id = '%s' for dataZone %d" % ( row['SPC_ID'],dataZone) )
               if int(row['SPC_ID']) == 1:
                  #write
                  spec = zone_spec_w[dataZone]
                  readToWriteThreshold[dataZone][1] = dataRate
               elif int(row['SPC_ID']) == 2:
                  #read
                  spec = zone_spec_r[dataZone]
                  readToWriteThreshold[dataZone][0] = dataRate
               else:
                  continue

               #Evaluate the spec
               if DEBUG: objMsg.printMsg("AppleSpec if: zone spec zone %d %f < %f < %f" % ( dataZone, spec[0], dataRate, spec[1] ) )
               if dataRate < spec[0] or dataRate > spec[1]:
                  objMsg.printMsg("AppleSpec: zone spec zone %d %f < %f < %f" % ( dataZone, spec[0], dataRate, spec[1] ) )
                  self.SetBlueNunFail()
                  import CommitServices
                  if not (testSwitch.FE_0208720_470167_P_AUTO_DOWNGRADE_BLUENUN_FAIL_FOR_APPLE and not CommitServices.isTierPN(self.dut.partNum)):
                     ScrCmds.raiseException(14520, "Failed zone spec zone %d %f < %f < %f" % ( dataZone, spec[0], dataRate, spec[1] ) )
                     #objMsg.printMsg("Warning! Failed zone spec zone %d %f < %f < %f" % ( dataZone, spec[0], dataRate, spec[1] ) )


            defRWSpec = prm_Apple_PerformanceScreens['MIN_R_TO_W']['default']
            for dataZone, zoneVal in enumerate(readToWriteThreshold):
               if DEBUG: objMsg.printMsg("AppleSpec: dz=%s, zv=%s" % (dataZone,zoneVal))
               if zoneVal == [0,0]:
                  continue #non spec'd zone
               spec = prm_Apple_PerformanceScreens['MIN_R_TO_W'].get(dataZone, defRWSpec)
               calcVal = 100*abs(zoneVal[0]-zoneVal[1])/float(zoneVal[1])
               objMsg.printMsg("Failed if R-W/W spec zone %d %f > %f" % ( dataZone, calcVal, spec ))
               if calcVal > spec:
                  self.SetBlueNunFail(True)
                  import CommitServices
                  if not (testSwitch.FE_0208720_470167_P_AUTO_DOWNGRADE_BLUENUN_FAIL_FOR_APPLE and not CommitServices.isTierPN(self.dut.partNum)):
                     ScrCmds.raiseException(14520, "Failed R-W/W spec zone %d %f > %f" % ( dataZone, calcVal, spec ) )

            if not self.dut.failBluenun:
               self.dut.driveattr["BLUENUNSCAN"] == "PASS"
               self.SetBlueNunFail(False)

            #oCustomCfg.saveScreenName('BLUENUN_SLIDE')

###########################################################################################################
class CSOCTemp(CState):
   """
   Monitor SOC, HDA and cell temperature
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("SOC Temperature Test")
      sptCmds.enableDiags()
      from Temperature import CTemperature
      oTemp = CTemperature()


      if not testSwitch.virtualRun:
         readtime = 900 #15 mins
         idletime = 300 #5 mins
         interval = 30 #update SOC and HDA temp every 30 sec
      else: # VE timing
         readtime = 1
         idletime = 0
         interval = 1

      numReadloop = int(readtime/interval)
      numIdleloop = int(idletime/interval)

      objMsg.printMsg("Readtime = %d sec, Idletime = %d sec, Update Interval = %d sec, numReadloop = %d, numIdleloop = %d" %(readtime, idletime, interval, numReadloop, numIdleloop))

      objMsg.printMsg("###########################")
      objMsg.printMsg("Cooling down a drive...")
      objMsg.printMsg("###########################")
      #Before Drive off, read SOC and HDA temperature
      SOCtemp = oTemp.getDeviceTemp(devSelect=3)
      HDAtemp = oTemp.getDeviceTemp(devSelect=2)
      cellTemp = "%0.1f" % (ReportTemperature()/10.0)
      objMsg.printMsg('Before Drive off: SOC temperature = %s degC, HDA temperature = %s degC, Cell temperature = %s' % (SOCtemp, HDAtemp, cellTemp))   
      self.updateDBlog(1, 1, SOCtemp, HDAtemp, cellTemp)

      objPwrCtrl.powerOff(offTime = 10)
      time.sleep(600) #sleep 10 mins
      objPwrCtrl.powerOn(set5V = 5000, set12V = 12000, onTime = 10, baudRate = 38400, useESlip = 1)
      sptCmds.enableDiags()

      #After Drive on, read SOC and HDA temperature
      SOCtemp = oTemp.getDeviceTemp(devSelect=3)
      HDAtemp = oTemp.getDeviceTemp(devSelect=2)
      cellTemp = "%0.1f" % (ReportTemperature()/10.0)
      objMsg.printMsg('After Drive on: SOC temperature = %s degC, HDA temperature = %s degC, Cell temperature = %s' % (SOCtemp, HDAtemp, cellTemp))   
      self.updateDBlog(1, 2, SOCtemp, HDAtemp, cellTemp)
         
      objMsg.printMsg("###########################")
      objMsg.printMsg("Sequential read at OD...")
      objMsg.printMsg("###########################")
      loop = 0
      while loop < numReadloop:
         if not testSwitch.virtualRun:
            #Have to do sequential read as follow, can be interrupted by Carriage Return (with ref from LiNa)
            #Normal A>R0,9999999 can't be interrupted by Ctrl+Z or CR
            sptCmds.sendDiagCmd('/A')
            sptCmds.sendDiagCmd('AB,0') #define LBA range
            sptCmds.sendDiagCmd('AC,300000') #end LBA in Hex. A 30sec sequential OD read will read ~4GB data. Reduce target address to 0x300000 (~12GB).
            if not ( testSwitch.M11P or testSwitch.M11P_BRING_UP):   #Not support M11P
               sptCmds.sendDiagCmd('S0') #seek to LBA0
            sptCmds.sendDiagCmd('L') #looping
            try:
               sptCmds.sendDiagCmd('R,ffff',timeout = interval) #start reading the defined LBA range
            except:
               pass

            try:
               sptCmds.sendDiagCmd(CR, altPattern = 'Next User LBA') #interrupt the read with 'Enter'
            except:
               pass
         else:
            time.sleep(interval)

         loop = loop + 1
         #Read SOC and HDA temperature
         SOCtemp = oTemp.getDeviceTemp(devSelect=3)
         HDAtemp = oTemp.getDeviceTemp(devSelect=2)     # Francis
         cellTemp = "%0.1f" % (ReportTemperature()/10.0)

         objMsg.printMsg('Read temp #%d, SOC temperature = %s degC, HDA temperature = %s degC, Cell temperature = %s' % (loop, SOCtemp, HDAtemp, cellTemp))
         self.updateDBlog(2, loop, SOCtemp, HDAtemp, cellTemp)

      objMsg.printMsg("###########################")
      objMsg.printMsg("Drive Idling...")
      objMsg.printMsg("###########################")
      loop = 0
      while loop < numIdleloop:
         time.sleep(interval)
         loop = loop + 1
         #Read SOC and HDA temperature
         SOCtemp = oTemp.getDeviceTemp(devSelect=3)
         HDAtemp = oTemp.getDeviceTemp(devSelect=2)
         cellTemp = "%0.1f" % (ReportTemperature()/10.0)

         objMsg.printMsg('Read temp #%d, SOC temperature = %s degC, HDA temperature = %s degC, Cell temperature = %s' % (loop, SOCtemp, HDAtemp, cellTemp))
         self.updateDBlog(3, loop, SOCtemp, HDAtemp, cellTemp)

   #-------------------------------------------------------------------------------------------------------

   def updateDBlog(self, spcid, loop, SOCtemp, HDAtemp, cellTemp):

      self.dut.dblData.Tables('P_TEMPERATURES').addRecord(
               {
               'SPC_ID'       : spcid,
               'OCCURRENCE'   : loop,
               'SEQ'          : self.dut.seqNum+1,
               'TEST_SEQ_EVENT': 0,
               'STATE_NAME'   : self.dut.nextState,
               'DRIVE_TEMP'   : HDAtemp,
               'CELL_TEMP'    : cellTemp,
               'ELEC_TEMP'    : SOCtemp,
               })
