#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PowerMode.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PowerMode.py#1 $
# Level:3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import time

#from Test_Switches import testSwitch
import DbLog
import ScrCmds
from Process import CProcess
import IntfClass
import MessageHandler as objMsg
from Rim import objRimType
from ICmdFactory import ICmd
from TestParamExtractor import TP

##############################################################################################################
##############################################################################################################
class powerModeException(Exception):
   def __init__(self,data):
      self.data = data

##############################################################################################################
##############################################################################################################
class CPowerModeTest(CProcess):
   """
   Test Purpose: Issue Idle, Idle Immediate, Standby, Standby Immediate, Sleep.
   Test Metrics: Check drive in correct APM mode and wake up after APM mode.
   - Basic Algorithm:
      - Issue ATA Idle command
      - Issue ATA Idle Immediate command
      - Issue ATA Standby command
      - Issue ATA Standby Immediate command
      - Issue ATA Sleep command
   Failure: Fail if not in the correct mode or if drive does not wake up.
   """
   #---------------------------------------------------------------------------------------------------------#
   def __init__(self, dut, params=[]):
      objMsg.printMsg('*'*20+"Power Mode Time init" + 20*'*')
      CProcess.__init__(self)
      self.idleMode      = ['Idle',          0xFF]
      self.idleImmedMode = ['Idle Immed',    0xFF]
      self.standbyMode   = ['Standby',       0x00]
      self.standbyImmed  = ['Standby Immed', 0x00]
      self.sleepMode     = ['Sleep',         0x00]

   #---------------------------------------------------------------------------------------------------------#
   def powerModeTest(self, numLoops=1):
      """
      Execute function loop.
      @return result: Returns OK or FAIL
      """
      objMsg.printMsg('*'*20+"Power Mode Test" + 20*'*')
      if numLoops > 1:
         objMsg.printMsg("NumLoops: %s" % numLoops)
      try:
         for loopCnt in range(numLoops):
            if numLoops > 1:
               objMsg.printMsg('Loop: ' + str(loopCnt+1) + '*'*5+"Power Mode Test" + 20*'*')
            self.powerMode(self.idleMode)
            self.powerMode(self.idleImmedMode)
            self.powerMode(self.standbyMode)
            self.powerMode(self.standbyImmed)
            self.powerMode(self.sleepMode)
         result = 0
      except powerModeException, M:
         ScrCmds.raiseException(13454, M.data)
      return result

   #---------------------------------------------------------------------------------------------------------#
   def powerMode(self, modeList=['Idle', 0xFF]):
      """
      Algorithm:
         Issue a Power Mode command, check the mode, wake up the drive.
         @param modeList: List with the test name and the expected mode value.
         Fails if drive not in correct mode.
         Fails if drive does not wake up.
      """
      if   modeList[0] == 'Idle':
         data = ICmd.Idle(5); time.sleep(5)
      elif modeList[0] == 'Idle Immed':
         data = ICmd.IdleImmediate()
      elif modeList[0] == 'Standby':
         data = ICmd.Standby(5); time.sleep(5)
      elif modeList[0] == 'Standby Immed':
         data = ICmd.StandbyImmed()
      elif modeList[0] == 'Sleep':
         data = ICmd.Sleep()

      result = data['LLRET']
      if data['LLRET'] == OK and modeList[0] != 'Sleep':
         data = ICmd.CheckPowerMode()
         if testSwitch.virtualRun or testSwitch.NoIO:
            data = {'LLRET':0,'STS':'80','SCNT': modeList[1]}
         objMsg.printMsg('In %s Mode CheckPowerMode() - data = %s' % (modeList[0], `data`))

         if data.has_key('SCNT') == 0:
            objMsg.printMsg('%s Failed - SCNT key not found - data = %s' % (modeList[0], `data`))
            raise powerModeException(data)

         if   modeList[0] == 'Idle':
            self.idleMode[0]      = data['SCNT']
         elif modeList[0] == 'Idle Immed':
            self.idleImmedMode[0] = data['SCNT']
         elif modeList[0] == 'Standby':
            self.standbyMode[0]   = data['SCNT']
         elif modeList[0] == 'Standby Immed':
            self.standbyImmed[0]  = data['SCNT']

         if int(data['SCNT']) != modeList[1]:
            objMsg.printMsg('%s Failed - status = 0x%x expected = 0x%x' % \
                           (modeList[0], int(data['SCNT']), modeList[1]))
            raise powerModeException(data)

      elif data['LLRET'] == OK and modeList[0] == 'Sleep':
         try:
            ICmd.SetIntfTimeout(5000)           # set 5sec timeout   
            data = ICmd.ReadSectorsExt(0,255)   # 48 bit PIO mode
         except: 
            data = {'LLRET':-1}
         ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"]*1000)
         
         if testSwitch.virtualRun:
            data = {'LLRET':-1,'STS':'80','SCNT': modeList[1]}

         objMsg.printMsg("Sleep Mode Seq Read data = %s" % str(data))
         if data['LLRET'] == OK and not testSwitch.NoIO: # Drive don't suppose to be ready when in Sleep mode, so fail it
            objMsg.printMsg('Failed - Drive Ready in Sleep Mode')
            raise powerModeException(data)
         else: # If drive doesn't response after Sleep cmd, then meaning its good
            data['LLRET'] = OK

      if data['LLRET'] == OK:
         if modeList[0] == 'Sleep': # A hard/soft reset is required to move drive out of Sleep mode

            if testSwitch.NoIO:
               objMsg.printMsg("NoIO power cycle instead of HardReset")
               from PowerControl import objPwrCtrl
               objPwrCtrl.powerCycle(5000,12000,10,10,baudRate=Baud38400,ataReadyCheck=False)
               import sptCmds
               sptCmds.enableDiags()
            else:
               data = ICmd.HardReset()
               objMsg.printMsg("HardReset data = %s" % str(data))

            if self.dut.driveattr['ATA_ReadyTimeout'] == 'USB':
               time.sleep(8)
            else:
               time.sleep(5)
            data = ICmd.ReadSectorsExt(0,255)
           
         if data['LLRET'] == OK or testSwitch.virtualRun:
            if modeList[0] == 'Sleep':
               self.sleepMode[0] = '0'
            objMsg.printMsg('Power Mode Passed Seq Read After %s' % modeList[0])
         else:
            objMsg.printMsg('Power Mode Failed Seq Read After %s' % modeList[0])
            raise powerModeException(data)

      else:
         objMsg.printMsg('Power Mode Failed %s - result = %d' %  (modeList[0], data['LLRET']))
         raise powerModeException(data)
