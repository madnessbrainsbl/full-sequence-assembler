#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/10/13 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_Motor.py $
# $Revision: #5 $
# $DateTime: 2016/10/13 00:01:11 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_Motor.py#5 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds


#----------------------------------------------------------------------------------------------------------
class CLowCurrentSpinUp(CState):
   """
      Description: Class that will perform setting Low spindle current using Diag command for No I/O product
      Base: N/A
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import re
      import sptCmds
      from serialScreen import sptDiagCmds      

      oSerial = sptDiagCmds()                                       # Check status from CTRL_L
      ctr_l = oSerial.GetCtrl_L()
      if ctr_l.get('LowCurrentSpinUp') == 'enabled':
         objMsg.printMsg('Drive Low Current Spin Up Feature is already enabled.')
         return

      sptCmds.enableDiags()
      if testSwitch.virtualRun:
         cmd_result = """R8

         IAP DestnAddr: 80239000  IAP Length: 0410
         """
      else:
         cmd_result = sptCmds.sendDiagCmd('R8', timeout=10, printResult = True, stopOnError = True)

      mat = re.match("R8[\s\n]*IAP\s+DestnAddr:\s+(?P<ADDR>[\dA-Fa-f]+)\s+IAP\s+Length", cmd_result)

      DestnAddr = -1
      if mat:
         DestnAddr = int(mat.groupdict()['ADDR'],16)
      else:
         ScrCmds.raiseException(14049,'Set drive low current spin up failed.')

      objMsg.printMsg('DestnAddr is %s' %DestnAddr)

      Low_spin_addr = hex(DestnAddr + 0x201)

      sptCmds.sendDiagCmd("=%s,%s,FE,1"%(Low_spin_addr[2:6],Low_spin_addr[6:10]),timeout=10, printResult = True, stopOnError = True)   # returns "Adr 80239201 ( 80239201 ) = FE"
      sptCmds.sendDiagCmd('W3,,22',timeout=10, printResult = True, stopOnError = True)

      objPwrCtrl.powerCycle()
      sptCmds.enableDiags()
      if testSwitch.virtualRun:
         data= {'LowCurrentSpinUp': 'enabled'}
      else:
         data = oSerial.GetCtrl_L(force=True)  # refresh CTRL_L data
      if data.get('LowCurrentSpinUp') == 'enabled':
         objMsg.printMsg('Set drive low current spin up succeeded.')
      else:
         ScrCmds.raiseException(14049,'Set drive low current spin up failed.')

      objPwrCtrl.powerCycle()


#----------------------------------------------------------------------------------------------------------
class CNormalCurrentSpinUp(CState):
   """
      Description: Class that will perform setting Normal spindle current using Diag command for No I/O product
      Base: N/A
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import re
      import sptCmds
      from serialScreen import sptDiagCmds

      oSerial = sptDiagCmds()                                       # Check status from CTRL_L
      ctr_l = oSerial.GetCtrl_L()
      if ctr_l.get('LowCurrentSpinUp') == 'disabled':
         objMsg.printMsg('Drive Low Current Spin Up Feature is already disabled.')
         return

      sptCmds.enableDiags()
      if testSwitch.virtualRun:
         cmd_result = """R8

         IAP DestnAddr: 80239000  IAP Length: 0410
         """
      else:
         cmd_result = sptCmds.sendDiagCmd('R8', timeout=10, printResult = True, stopOnError = True)

      mat = re.match("R8[\s\n]*IAP\s+DestnAddr:\s+(?P<ADDR>[\dA-Fa-f]+)\s+IAP\s+Length", cmd_result)
      DestnAddr = -1
      if mat:
         DestnAddr = int(mat.groupdict()['ADDR'],16)
      else:
         ScrCmds.raiseException(14049,'Set drive normal current spin up failed.')
      objMsg.printMsg('DestnAddr is %s' %DestnAddr)

      Low_spin_addr = hex(DestnAddr + 0x201)
      sptCmds.sendDiagCmd("=%s,%s,FF,1"%(Low_spin_addr[2:6],Low_spin_addr[6:10]),timeout=10, printResult = True, stopOnError = True)
      sptCmds.sendDiagCmd('W3,,22',timeout=10, printResult = True, stopOnError = True)

      objPwrCtrl.powerCycle()
      sptCmds.enableDiags()

      if testSwitch.virtualRun:
         data= {'LowCurrentSpinUp': 'disabled'}
      else:
         data = oSerial.GetCtrl_L(force=True)     # refresh CTRL_L data
      if data.get('LowCurrentSpinUp') == 'disabled':
         objMsg.printMsg('Set drive low current spin up succeeded.')
      else:
         ScrCmds.raiseException(14049,'Set drive normal current spin up failed.')


      objPwrCtrl.powerCycle()


#----------------------------------------------------------------------------------------------------------
class CHighRPMSpin(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.RUN_MOTOR_JITTER_SCRN or testSwitch.SEA_SWEEPER_RPM:  
         from Servo import CServoFunc
         self.oSrvFunc = CServoFunc()

      if testSwitch.RUN_MOTOR_JITTER_SCRN:
         #=== Run Motor Jitter Screening
         self.oSrvFunc.setSpinSpeed(TP.MotorJitterPrm_4)

      if testSwitch.SEA_SWEEPER_RPM:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=1, onTime=5, useESlip=1)
         #=== Spin at max RPM for pre-defined mins, restore to original RPM ===
         # Test revised to leave drive in better state for continued testing.
         # Time to spin at higher RPM is set in the parameters passed in the test call.
         if self.dut.BG in ['SBS']:
            changeRPMloops = self.params.get('changeRPMloops', 3) 
         else:
            changeRPMloops = getattr(TP, 'changeRPMloops', 1)
         changeRPMnominalDwell = getattr(TP, 'changeRPMnominalDwell', 0)

         import time
         for loop in range(changeRPMloops):
            time.sleep(changeRPMnominalDwell)
            self.oSrvFunc.setSpinSpeed(TP.maxRPM_spinup_spindownPrm_4_2)

         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=1, onTime=5, useESlip=1)


#----------------------------------------------------------------------------------------------------------
class CSpinDipScreen(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Servo import CServoScreen 
      #===10x loop of T25(CWORD1=0x8080)
      self.oSrvScreen = CServoScreen()
      #lul_prm_025_temp = TP.lul_prm_025.copy()
      #lul_prm_025_temp['CWORD1'] = 0x700
      #lul_prm_025_temp['NUM_SAMPLES'] = 10
      if testSwitch.M11P_BRING_UP or testSwitch.M11P:
         SetFailSafe()
         self.oSrvScreen.servoRetract(TP.spin_dip_prm_025)
         ClearFailSafe()
      else:
         for i in range(2):
            try:
               self.oSrvScreen.servoRetract(TP.spin_dip_prm_025)
               break
            except ScriptTestFailure, failureData:
               if self.dut.BG in ['SBS'] and failureData[0][2] == 11164 and self.dut.objSeq.SuprsDblObject.has_key('P025_LOAD_UNLOAD_PARAMS'):
                  deltaRPM = 0
                  for entry in self.dut.objSeq.SuprsDblObject['P025_LOAD_UNLOAD_PARAMS']:
                     if entry['LOAD_STATUS_CODE'] == '2':
                        objMsg.printMsg('For EC11664, P025_LOAD_UNLOAD_PARAMS / LOAD_STATUS_CODE = 2')
                        ScrCmds.raiseException(14661,'For EC11664, P025_LOAD_UNLOAD_PARAMS / LOAD_STATUS_CODE = 2')
                     if 5456 - int(entry['LOAD_MIN_SPIN_SPEED']) > 20:
                        deltaRPM += 1
                  if deltaRPM <= 2 and i == 0:
                     continue            
               raise failureData
      try:
        self.rampDiscOffsetDetection()
      except: pass
        
      
   def rampDiscOffsetDetection(self):
      try:
         entries = self.dut.dblData.Tables('P025_UNLOAD_PROFILE').tableDataObj()
      except:
         return
      
      uldcurList = []
      uldvelList = []
      peakDetectDeltaList = [0.2, 0.3]
      slopeLimit = 0.15
      reportFailure = 0
      
      for entry in entries:
         uldcurList.append(float(entry['ULD_PROC_CUR']))
         uldvelList.append(float(entry['ULD_PROC_VEL']))
      
      objMsg.printMsg('Debug1: %s'%uldcurList)
      objMsg.printMsg('Debug2: %s'%uldvelList)
      
      maxUnloadCurrentIndex = uldcurList.index(max(uldcurList))
      uldcurList = uldcurList[:maxUnloadCurrentIndex+1]
      minUnloadCurrentIndex = uldcurList.index(min(uldcurList))
      uldcurList = uldcurList[minUnloadCurrentIndex - 70:minUnloadCurrentIndex+1]
      uldvelList = uldvelList[minUnloadCurrentIndex - 70:minUnloadCurrentIndex+1+3]
      
      objMsg.printMsg('maxUnloadCurrentIndex = %d'%maxUnloadCurrentIndex)
      objMsg.printMsg('minUnloadCurrentIndex = %d'%minUnloadCurrentIndex)
      objMsg.printMsg('Debug3: %s'%uldcurList)
      objMsg.printMsg('Debug4: %s'%uldvelList)
      
      for index in range(len(uldcurList) - 5):
         if uldcurList[index] > uldcurList[index+1] and \
            uldcurList[index+1] > uldcurList[index+2] and \
            uldcurList[index+2] > uldcurList[index+3] and \
            uldcurList[index+3] > uldcurList[index+4] and \
            uldcurList[index+4] > uldcurList[index+5]:
            if uldcurList[index+5] < 0 and uldcurList[index+5] - uldcurList[index] < -1:
               climbStartPointIndex = index
               break
      else:
         climbStartPointIndex = len(uldcurList) - 50         
      objMsg.printMsg('climbStartPointIndex = %d'%climbStartPointIndex)
      uldvelList = uldvelList[climbStartPointIndex:]
      objMsg.printMsg('Debug5: %s'%uldvelList)
      
      # Without MovingAverageFilter
      #for peakDetectDelta in peakDetectDeltaList:
      #   self.peakDetect(uldvelList, peakDetectDelta)
         
      # With MovingAverageFilter - Method1
      fileterdVelList = self.MovingAverageFilter(uldvelList)
      objMsg.printMsg('uldvelList: %s'%uldvelList)
      objMsg.printMsg('fileterdVelList: %s'%fileterdVelList)
      
      for peakDetectDelta in peakDetectDeltaList:
         self.peakDetect(fileterdVelList, peakDetectDelta, 'Filtered(Method1)')
         
      # With MovingAverageFilter - Method2
      #fileterdVelList = self.MovingAverageFilter2(uldvelList)
      #objMsg.printMsg('uldvelList: %s'%uldvelList)
      #objMsg.printMsg('fileterdVelList: %s'%fileterdVelList)
      #for peakDetectDelta in peakDetectDeltaList:
      #   peakInfo = self.peakDetect(fileterdVelList, peakDetectDelta, 'Filtered(Method2)')
      #   if len(peakInfo) == 1 and peakDetectDelta == 0.2:
      #      slope = (peakInfo[0][1] - fileterdVelList[0]) / (peakInfo[0][0])
      #      objMsg.printMsg('Slope(Filtered(Method2)): %s'%slope)
      
      self.dut.dblData.Tables('P025_UNLOAD_PROFILE').deleteIndexRecords(confirmDelete=1)
      self.dut.dblData.delTable('P025_UNLOAD_PROFILE')   
         
   def peakDetect(self, uldvelList, peakDetectDelta, mode = 'Non-Filtered'):
      posWithMaxVel = 0
      posWithMinVel = 0
      lookForMax = 1
      slope      = 0
      peakInfo   = []
      valleyInfo = []
      for index in range(len(uldvelList)):
         curVel = uldvelList[index]
         if index == 0:
            maxVel = curVel
            minVel = curVel
         else:
            if curVel > maxVel:
               maxVel = curVel
               posWithMaxVel = index
            elif curVel < minVel:
               minVel = curVel
               posWithMinVel = index
            
         if lookForMax:
            if curVel < maxVel - peakDetectDelta:
               peakInfo.append((posWithMaxVel, maxVel))
               minVel = curVel
               posWithMinVel = index
               lookForMax = 0
         else:
            if curVel > minVel + peakDetectDelta:
               valleyInfo.append((posWithMinVel, minVel))
               maxVel = curVel
               posWithMaxVel = index
               lookForMax = 1
      objMsg.printMsg('='*42)
      objMsg.printMsg('With peakDetectDelta = %s with mode = %s'%(peakDetectDelta, mode))
      objMsg.printMsg('Peaktab  (index, Vel): %s'%peakInfo)
      objMsg.printMsg('Valleytab(index, Vel): %s'%valleyInfo)
      
      twoPeaksDeltaValue = []
      twoPeaksDeltaTiming = []
      if len(peakInfo) >= 2:
         for i in range(len(peakInfo) - 1):
            twoPeaksDeltaValue.append(peakInfo[i+1][1] - peakInfo[i][1])
            twoPeaksDeltaTiming.append(peakInfo[i+1][0] - peakInfo[i][0])
      objMsg.printMsg('twoPeaksDeltaValue(%s - %s): %s'%(peakDetectDelta, mode, twoPeaksDeltaValue))
      objMsg.printMsg('twoPeaksDeltaTiming(%s - %s): %s'%(peakDetectDelta, mode, twoPeaksDeltaTiming))
      objMsg.printMsg('='*42)
      
      if len(peakInfo) == 1:
         slope = (peakInfo[0][1] - uldvelList[0]) / (peakInfo[0][0])
         
      ScriptComment('P_TABLE%2.1f:'%peakDetectDelta, writeTimestamp = 0)
      ScriptComment('DOUBLE_PEAKS SLOPE', writeTimestamp = 0)
      ScriptComment('%12s%6.3f'%(sum(twoPeaksDeltaValue), slope), writeTimestamp = 0)
                  
   def MovingAverageFilter(self, uldvelList, window = 3):
      fileterdVelList = [0] * len(uldvelList)
      
      for index in range(len(uldvelList)):
         tempSum = 0
         coutsNonZero = 0
         
         for windowIndex in range(window):
            if (index+1) > windowIndex:
               tempSum = tempSum + uldvelList[index - windowIndex]
               coutsNonZero += 1
         fileterdVelList[index] = tempSum / coutsNonZero
       
      return fileterdVelList
      
   def MovingAverageFilter2(self, uldvelList, window = 3):
      fileterdVelList = [0] * len(uldvelList)
      
      fileterdVelList[0] = (5.0 * uldvelList[0] + 2.0 * uldvelList[1] - uldvelList[2]) / 6.0
      for index in range(1, len(uldvelList)-1):
         fileterdVelList[index] = (uldvelList[index-1] + uldvelList[index] + uldvelList[index+1]) / 3.0
      fileterdVelList[-1] = (5.0 * uldvelList[len(uldvelList)-1] + 2.0 * uldvelList[len(uldvelList)-2] - uldvelList[len(uldvelList)-3]) / 6.0
       
      return fileterdVelList      
         
