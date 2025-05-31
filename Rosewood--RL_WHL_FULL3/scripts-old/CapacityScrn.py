#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Interface screening test states (blocks) to go in here
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/CapacityScrn.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/CapacityScrn.py#1 $
# Level: 2
#---------------------------------------------------------------------------------------------------------#

import time
import ScrCmds, re
from Process import CProcess
from Constants import *
from serialScreen import sptDiagCmds
#from PowerControl import objPwrCtrlATA   # Loke
from IntfClass import *
#from MessageHandler import objMsg
from State import CState

from base_IntfTest import *   # for objPwrCtrl - Loke

##############################################################################################################
##############################################################################################################
class CCapScrn(CProcess):
   """
   Test Purpose: Validate drive capacity and model no.
   Basic Algorithm:
   - Use serial port L command get the drive model and capacity
   - Interface "Identify" command, compare the model and capacity
   Failure: Fail on incorrect drive capacity or model no.
   """
   #---------------------------------------------------------------------------------------------------------#
   def __init__(self, dut, params=[]):
      self.dut = dut
   #---------------------------------------------------------------------------------------------------------#
   def CapScrnTest(self, drvInfoDict):
      """
      Execute function loop.
      @return result: Returns OK or FAIL
      """
      numLoops = drvInfoDict.get('LOOP',1)
      objMsg.printMsg('*'*20+" Capacity & Model No. Screen " + 20*'*')
      if numLoops > 1:
         objMsg.printMsg("NumLoops: %s" % numLoops)
      for loopCnt in range(numLoops):
         result = OK
         if numLoops > 1:
            objMsg.printMsg('Loop: ' + str(loopCnt+1) + '*'*5+"Capacity & Model No. Screen Test" + 20*'*')

         # ---------- Power Cycle ----------
         objPwrCtrl.powerCycle(5000)   # Loke
         objMsg.printMsg('GetDriveVoltsAndAmps() = %s'%`GetDriveVoltsAndAmps()`) # Loke

         # ---------- Identify Drive ----------
         ret = CIdentifyDevice().ID # read device settings with identify device
         self.IDmaxLBA = ret['IDDefaultLBAs'] # default for 28-bit LBA
         if ret['IDCommandSet5'] & 0x400:      # check bit 10
            #objMsg.printMsg('Get ID Data 48 bit LBA is supported')
            self.IDmaxLBA = ret['IDDefault48bitLBAs']
         drvCap = self.IDmaxLBA * 512 / 1000000000
         drvModel = ret['IDModel'].strip()       # Remove leading and trailing whitespaces
         drvSn = ret['IDSerialNumber'].strip()   # Remove leading and trailing whitespaces
         objMsg.printMsg('IdentifyDevice - Drive S/N: %s   Capacity: %dGB   Model: %s' % (drvSn,drvCap,drvModel))

         if testSwitch.virtualRun:  # Loke
            continue

         # ---------- Check drv s/n length ----------
         if len(drvSn) != 8:
             objMsg.printMsg('Invalid drv s/n length')
             result = 1
             break

         # ---------- Check drv s/n prefix ----------
         if drvSn[1:3].upper() not in drvInfoDict.keys():
             objMsg.printMsg('Invalid drv s/n prefix')
             result = 1
             break

         # ---------- Check drv capacity and model validity ----------
         for key in drvInfoDict.keys():
             if key[0:2] == 'ST': # Look for model no.
                 if drvModel.find(key) > -1: # Look for key as a sub string of model no. from IdentifyDevic. This sub string compare instead of full string
                 # compare is inserted to reduce the maintenance of StateTable for model no. checking. It was requested to check for only the 1st 5 or 6
                 # chars of the model string instead of the full model string. It has been highlighted that this will reduce the integrity/stringency of
                 # the model no. checking engine. (req by BengChai 6/Nov/07)
                     found = 1
                     if drvInfoDict[key] == drvCap:
                         result = OK
                         break
                     else:
                         objMsg.printMsg('Valid drv model %s but capacity mismatch!! Identify: %dGB   List: %dGB' %(drvModel,drvCap,drvInfoDict[key]))
                         result = 1
                         break
                 else:
                     found = 0
         if not found:
             objMsg.printMsg('Invalid drv model!! Not in list: %s' %drvInfoDict)
             result = 1
             break
         if result != OK:
             break
         result = ICmd.Standby(0)
         if result['LLRET'] != OK:
             objMsg.printMsg('Standby Mode 0 failed!')
             result = 1
             break

         result = ICmd.SetFeatures(0x85)
         if result['LLRET'] != OK:
             objMsg.printMsg('Disable Advance Power Management Failed!')
             result = 1
             break

         result = ICmd.Seek(0)      # Seek to LBA 0
         if result['LLRET'] != OK:
             objMsg.printMsg('Seek cmd Failed!')
             result = 1
             break

         # ---------- Check drv s/n and capacity against Serial Port ----------
         result, spDrvCap, spDrvModel, spDrvSn = self.serialGetDrvData()
         objMsg.printMsg('Serial Port - Drive S/N: %s   Capacity: %dGB' % (spDrvSn,spDrvCap))
         objMsg.printMsg('Serial Port - Drive Model: %s' % spDrvModel)
         if result == OK:
             if spDrvCap < drvCap: # Capacity read from S/P will be >= to that from IdentifyDevice (ref WeiKin 10/Oct/07)
                 objMsg.printMsg('Drive Capacity MISMATCH!!:')
                 objMsg.printMsg('IdentifyDevice: %dGB   S/P: %dGB' %(drvCap,spDrvCap))
                 result = 1
                 break
             
             if spDrvSn != drvSn:
                 objMsg.printMsg('Drive S/N MISMATCH!!:')
                 objMsg.printMsg('IdentifyDevice: %s   S/P: %s' %(drvSn,spDrvSn))
                 result = 1
                 break
             
             if spDrvModel != drvModel:
                 objMsg.printMsg('Drive Model no. MISMATCH!!:')
                 objMsg.printMsg('IdentifyDevice: %s   S/P: %s' %(drvModel,spDrvModel))
                 result = 1
                 break
         else:
             objMsg.printMsg('serialGetDrvData() fail')
             break

      if result != OK:
         ScrCmds.raiseException(13453, "Capacity & Model No. Screen")

      # ---------- Power Cycle back to 5V ----------
      objPwrCtrl.powerCycle() # Loke
      objMsg.printMsg('GetDriveVoltsAndAmps() = %s'%`GetDriveVoltsAndAmps()`) # Loke
      return result

   #---------------------------------------------------------------------------------------------------------#
   def serialGetDrvCap(self):
      ICmd.SetSerialTimeout(5000, 5000)
      # Need to issue Ctrl-Z after pwr cyc, otherwise the following cmds will not work
      ICmd.ClearSerialBuffer()
      result = ICmd.Ctrl( 'Z', '>' , 512)['LLRET']
      if result != OK:
          objMsg.printMsg('serialGetDrvCap(): Ctrl-Z fail')
          return 1,-1,''

      ICmd.ClearSerialBuffer()
      data = ICmd.Ctrl( 'L', 'PreampType:' , 512)
      result = data['LLRET']
      if result != OK:
          objMsg.printMsg('serialGetDrvCap(): Ctrl-L fail')
          return 1,-1,''

      #objMsg.printMsg('********** Ctrl-L **********')
      #objMsg.printMsg('%s' %data['DATA'])
      #objMsg.printMsg('****************************')

      # Get max LBA
      d = data['DATA']
      m = re.search('Lbas:', d)
      if m == None:  # knl 26Dec07
          objMsg.printMsg('CapScrn fail. Cannot read "Lbas:"')
          return 1,-1,''

      cap = d[m.end():].split(',')[0]
      cap = int(cap,16)
      
      # Get hda s/n
      d = data['DATA']
      m = re.search('HDA SN:', d)
      if m == None:  # knl 26Dec07
          objMsg.printMsg('CapScrn fail. Cannot read "HDA SN:"')
          return 1,-1,''

      hdasn = d[m.end():].split(',')[0]
      hdasn = hdasn.split()[0]

      return OK, (cap*512/1000000000), hdasn

   #---------------------------------------------------------------------------------------------------------#
   def serialGetDrvModel(self):
      ICmd.SetSerialTimeout(5000, 5000)
      ICmd.ClearSerialBuffer()
      result = ICmd.Ctrl( 'Z', '>' , 512)['LLRET']
      if result != OK:
          objMsg.printMsg('CapScrn - Ctrl-Z fail')
          return 1,''

      ICmd.ClearSerialBuffer()
      data = ICmd.SerialCommand( '/\r', 'T>' )
      result = data['LLRET']
      if result != OK:
          objMsg.printMsg('CapScrn - GotoLevel T fail')
          return 1,''

      ICmd.ClearSerialBuffer()
      data = ICmd.SerialCommand( 'F"InternalSeagateModelNumber"\r', 'T>' )
      result = data['LLRET']
      if result != OK:
          #objMsg.printMsg('CapScrn - Cmd T>F"ModelNumber" fail')
          objMsg.printMsg('CapScrn - Cmd T>F"InternalSeagateModelNumber" fail')
          return 1,''

      data = ICmd.GetBuffer(SBF, 0, 20*512)['DATA']
      m = re.search('ModelNumber =', data)
      if m == None:  # knl 26Dec07
          objMsg.printMsg('CapScrn fail. Cannot read "ModelNumber ="')
          return 1,''

      model = data[m.end():].split("'")[1]
      model = model.strip()
      
      return OK, model

   #---------------------------------------------------------------------------------------------------------#
   def serialGetDrvData(self):
      ICmd.SetSerialTimeout(5000, 5000)
      # Need to issue Ctrl-Z after pwr cyc, otherwise the following cmds will not work
      ICmd.ClearSerialBuffer()
      result = ICmd.Ctrl( 'Z', '>' , 512)['LLRET']
      if result != OK:
          objMsg.printMsg('CapScrn - Ctrl-Z fail')
          return 1,-1,-1,''

      ICmd.ClearSerialBuffer()
      data = ICmd.Ctrl( 'L', 'PreampType:' , 512)
      result = data['LLRET']
      if result != OK:
          objMsg.printMsg('CapScrn - Ctrl-L fail')
          return 1,-1,-1,''

      ICmd.ClearSerialBuffer()
      data2 = ICmd.SerialCommand( '/\r', 'T>' )
      result = data2['LLRET']
      if result != OK:
          objMsg.printMsg('CapScrn - GotoLevel T fail')
          return 1,-1,-1,''

      ICmd.ClearSerialBuffer()
      data2 = ICmd.SerialCommand( 'F"InternalSeagateModelNumber"\r', 'T>' )
      result = data2['LLRET']
      if result != OK:
          objMsg.printMsg('CapScrn - Cmd T>F"InternalSeagateModelNumber" fail')
          return 1,-1,-1,''
      data2 = ICmd.GetBuffer(SBF, 0, 20*512)['DATA']

      # Get max LBA
      d = data['DATA']
      m = re.search('Lbas:', d)
      if m == None:  # knl 26Dec07
          objMsg.printMsg('CapScrn fail. Cannot read "Lbas:"')
          return 1,-1,-1,''

      cap = d[m.end():].split(',')[0]
      cap = int(cap,16)
      
      # Get hda s/n
      d = data['DATA']
      m = re.search('HDA SN:', d)
      if m == None:  # knl 26Dec07
          objMsg.printMsg('CapScrn fail. Cannot read "HDA SN:"')
          return 1,-1,-1,''

      hdasn = d[m.end():].split(',')[0]
      hdasn = hdasn.split()[0]

      # Get Model number
      m = re.search('ModelNumber =', data2)
      if m == None:  # knl 26Dec07
          objMsg.printMsg('CapScrn fail. Cannot read "ModelNumber ="')
          return 1,-1,-1,''

      model = data2[m.end():].split("'")[1]
      model = model.strip()
      
      return OK, (cap*512/1000000000), model, hdasn

###########################################################################################################
class CCapacityScreen(CState):
   def __init__(self, dut, params=[]):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      oCapScrn = CCapScrn(self.dut)
      oCapScrn.CapScrnTest(self.params)


class CServoFlaw(CState):
   '''
   KokChoon See: David and Steven want to check or keep track no. of entries in the Servo Flaw List  
   before sending the drives to Reliabilty for testing. 
   This is for temporary modules and will be remove in future.
   '''
   def __init__(self, dut, params=[]):
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from TestParameters import *
      objMsg.printMsg('CServoFlaw run')

      result = ICmd.SetFeatures(0x85)
      if result['LLRET'] != OK:
          objMsg.printMsg('Disable Advance Power Management Failed!')
          ScrCmds.raiseException(14640, "APM fail")

      result = ICmd.Seek(0)      # Seek to LBA 0
      if result['LLRET'] != OK:
          objMsg.printMsg('Seek cmd Failed!')
          ScrCmds.raiseException(14640, "Seek fail")

      ICmd.SetSerialTimeout(5000, 5000)
      ICmd.ClearSerialBuffer()
      result = ICmd.Ctrl( 'Z', '>' , 512)['LLRET']
      if result != OK:
          objMsg.printMsg('CServoFlaw - Ctrl-Z fail')
          return 1,''

      ICmd.ClearSerialBuffer()
      data = ICmd.SerialCommand( '/\r', 'T>' )
      result = data['LLRET']
      if result != OK:
          objMsg.printMsg('CServoFlaw - GotoLevel T fail')
          return

      ICmd.ClearSerialBuffer()

      for i in range(numHeads):
         ServoFlawListCmd = 'V8,%d,0,1\n' % i
         data = ICmd.SerialCommand(ServoFlawListCmd, 'T>')
         result = data['LLRET']
         if result != OK:
            objMsg.printMsg('CServoFlaw - cmd %s failed' % `ServoFlawListCmd`)
            return

         data = ICmd.GetBuffer(SBF, 0, 512)['DATA']
         objMsg.printMsg('CServoFlaw - command=%s data=\n%s' % (`ServoFlawListCmd`, data))

      objPwrCtrl.powerCycle() # Loke

