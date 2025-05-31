#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Preamp_Screens.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Preamp_Screens.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
from Servo import CServo
import struct

#----------------------------------------------------------------------------------------------------------
class CPreampOHScreen(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not 'LSI5230' in self.dut.PREAMP_TYPE:
         objMsg.printMsg('not LSI5230 detected, so skip this state')
         return 0
      objMsg.printMsg('LSI5230 detected, measure over heating threshold')

      self.oServo = CServo()

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      self.oServo.St(TP.spinupPrm_2)

      # wsk to head 0, trk 0x200
      ret = self.oServo.wsk(0x200,0)
      objMsg.printMsg('seek to head:0, trk:0x200.')

      # initialize and read back preamp registers setting
      buf, errorCode = self.oServo.Fn(1330, 0x1F, 0x01, 1)  # write
      buf, errorCode = self.oServo.Fn(1329, 0x1F, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x3F = 0x%X.' % (bufBytes[0]))

      buf, errorCode = self.oServo.Fn(1330, 0x19, 0xC0, 1)  # write
      buf, errorCode = self.oServo.Fn(1329, 0x19, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x39 = 0x%X.' % (bufBytes[0]))

      buf, errorCode = self.oServo.Fn(1330, 0x1B, 0x00, 1)  # write
      buf, errorCode = self.oServo.Fn(1329, 0x1B, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x3B = 0x%X.' % (bufBytes[0]))

      buf, errorCode = self.oServo.Fn(1330, 0x1D, 0x21, 1)  # write
      buf, errorCode = self.oServo.Fn(1329, 0x1D, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x3D = 0x%X.' % (bufBytes[0]))

      buf, errorCode = self.oServo.Fn(1330, 0x1E, 0x20, 1)  # write
      buf, errorCode = self.oServo.Fn(1329, 0x1E, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x3E = 0x%X.' % (bufBytes[0]))

      # loop the threshold index
      Reg3CSettingList =    [0x24, 0x22, 0x20, 0x3E, 0x3C, 0x3A, 0x38, 0x36, 0x34, 0x32, 0x30]
      Reg3CSettingListTemp =[131, 126, 121, 116, 111, 106, 101, 96, 91, 86, 81]
      for i in range(len(Reg3CSettingList)):
         buf, errorCode = self.oServo.Fn(1330, 0x1C, Reg3CSettingList[i], 1)  # set reg3C
         buf, errorCode = self.oServo.Fn(1329, 0x1C, 1)                       # read
         bufBytes = struct.unpack('BB',buf)
         original_val = bufBytes[0]
         objMsg.printMsg('Set Preamp register 0x3C = 0x%X. temperature = %s' % (bufBytes[0],(str(Reg3CSettingListTemp[i]))))

         buf, errorCode = self.oServo.Fn(1330, 0x6, 0x0, 0)   # clr reg6
         buf, errorCode = self.oServo.Fn(1329, 0x6, 0)        # read
         bufBytes = struct.unpack('BB',buf)
         original_val = bufBytes[0]
         objMsg.printMsg('clear Preamp register 0x6 = %s.' % (str(bufBytes[0])))

         # do 0x400 wedge write
         #for j in range(0x400):
            #buf, errorCode = self.oServo.Fn(1283,6,0,-1,0x2004,0x0004,0xCCCC)  # write the track 0x400 times
         buf, errorCode = self.oServo.Fn(1373,0x400,0,1)
         objMsg.printMsg('self.oServo.Fn(1373,0x400,0,1)')

         buf, errorCode = self.oServo.Fn(1329, 0x6, 0) # read
         bufBytes = struct.unpack('BB',buf)
         original_val = bufBytes[0]
         objMsg.printMsg('Read Preamp register 0x6: 0x%X.' % (bufBytes[0]))
         objMsg.printMsg('Error Code: %s during reading preamp register.' % (str(errorCode)))

         if ((original_val & 0x20) != 0):   # check bit5 of register set
            objMsg.printMsg('Preamp over heat recorded at threshold = 0x%X.' % (Reg3CSettingList[i]))
            break
         #else:
         #   objMsg.printMsg('No Preamp over heat recorded at threshold = 0x%X.' % (Reg3CSettingList[i]))

      # revert registers setting
      buf, errorCode = self.oServo.Fn(1330, 0x1F, 0x01, 1)  #
      buf, errorCode = self.oServo.Fn(1329, 0x1F, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x3F = 0x%X.' % (bufBytes[0]))

      buf, errorCode = self.oServo.Fn(1330, 0x19, 0, 1)  #
      buf, errorCode = self.oServo.Fn(1329, 0x19, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x39 = 0x%X.' % (bufBytes[0]))

      buf, errorCode = self.oServo.Fn(1330, 0x1F, 0, 1)  #
      buf, errorCode = self.oServo.Fn(1329, 0x1F, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x3F = 0x%X.' % (bufBytes[0]))

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


#----------------------------------------------------------------------------------------------------------
class CPreampOHScreen_LG(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not 'LSI5230' in self.dut.PREAMP_TYPE:
         objMsg.printMsg('not LSI5230 detected, so skip this state')
         return 0
      objMsg.printMsg('LSI5230 detected, measure over heating threshold')

      self.oServo = CServo()

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      self.oServo.St(TP.spinupPrm_2)

      # wsk to head 0, trk 0x200
      ret = self.oServo.wsk(0x200,0)
      objMsg.printMsg('seek to head:0, trk:0x200.')

      # initialize and read back preamp registers setting
      buf, errorCode = self.oServo.Fn(1392, 0x1F, 0x01, 1)  # write
      buf, errorCode = self.oServo.Fn(1391, 0x1F, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x3F = 0x%X.' % (bufBytes[0]))

      buf, errorCode = self.oServo.Fn(1392, 0x19, 0xC0, 1)  # write
      buf, errorCode = self.oServo.Fn(1391, 0x19, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x39 = 0x%X.' % (bufBytes[0]))

      buf, errorCode = self.oServo.Fn(1392, 0x1B, 0x00, 1)  # write
      buf, errorCode = self.oServo.Fn(1391, 0x1B, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x3B = 0x%X.' % (bufBytes[0]))

      buf, errorCode = self.oServo.Fn(1392, 0x1D, 0x21, 1)  # write
      buf, errorCode = self.oServo.Fn(1391, 0x1D, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x3D = 0x%X.' % (bufBytes[0]))

      buf, errorCode = self.oServo.Fn(1392, 0x1E, 0x20, 1)  # write
      buf, errorCode = self.oServo.Fn(1391, 0x1E, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x3E = 0x%X.' % (bufBytes[0]))

      if testSwitch.FE_0191751_231166_P_172_DUMP_PREAMP:
         self.oServo.St(TP.dumpPreampRegs_172)

      # loop the threshold index
      Reg3CSettingList =    [0x24, 0x22, 0x20, 0x3E, 0x3C, 0x3A, 0x38, 0x36, 0x34, 0x32, 0x30]
      Reg3CSettingListTemp =[131, 126, 121, 116, 111, 106, 101, 96, 91, 86, 81]
      for i in range(len(Reg3CSettingList)):
         buf, errorCode = self.oServo.Fn(1392, 0x1C, Reg3CSettingList[i], 1)  # set reg3C
         buf, errorCode = self.oServo.Fn(1391, 0x1C, 1)                       # read
         bufBytes = struct.unpack('BB',buf)
         original_val = bufBytes[0]
         objMsg.printMsg('Set Preamp register 0x3C = 0x%X. temperature = %s' % (bufBytes[0],(str(Reg3CSettingListTemp[i]))))

         buf, errorCode = self.oServo.Fn(1392, 0x6, 0x0, 0)   # clr reg6
         buf, errorCode = self.oServo.Fn(1391, 0x6, 0)        # read
         bufBytes = struct.unpack('BB',buf)
         original_val = bufBytes[0]
         objMsg.printMsg('clear Preamp register 0x6 = %s.' % (str(bufBytes[0])))

         # do 0x400 wedge write
         #for j in range(0x400):
            #buf, errorCode = self.oServo.Fn(1283,6,0,-1,0x2004,0x0004,0xCCCC)  # write the track 0x400 times
         buf, errorCode = self.oServo.Fn(1373,0x400,0,1)
         objMsg.printMsg('self.oServo.Fn(1373,0x400,0,1)')

         buf, errorCode = self.oServo.Fn(1391, 0x6, 0) # read
         bufBytes = struct.unpack('BB',buf)
         original_val = bufBytes[0]
         objMsg.printMsg('Read Preamp register 0x6: 0x%X.' % (bufBytes[0]))
         objMsg.printMsg('Error Code: %s during reading preamp register.' % (str(errorCode)))

         if ((original_val & 0x20) != 0):   # check bit5 of register set
            objMsg.printMsg('Preamp over heat recorded at threshold = 0x%X.' % (Reg3CSettingList[i]))
            if testSwitch.FE_0191751_231166_P_172_DUMP_PREAMP:
               self.oServo.St(TP.dumpPreampRegs_172)

            break
         #else:
         #   objMsg.printMsg('No Preamp over heat recorded at threshold = 0x%X.' % (Reg3CSettingList[i]))

      # revert registers setting
      buf, errorCode = self.oServo.Fn(1392, 0x1F, 0x01, 1)  #
      buf, errorCode = self.oServo.Fn(1391, 0x1F, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x3F = 0x%X.' % (bufBytes[0]))

      buf, errorCode = self.oServo.Fn(1392, 0x19, 0, 1)  #
      buf, errorCode = self.oServo.Fn(1391, 0x19, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x39 = 0x%X.' % (bufBytes[0]))

      buf, errorCode = self.oServo.Fn(1392, 0x1F, 0, 1)  #
      buf, errorCode = self.oServo.Fn(1391, 0x1F, 1)        # read
      bufBytes = struct.unpack('BB',buf)
      original_val = bufBytes[0]
      objMsg.printMsg('Preamp register 0x3F = 0x%X.' % (bufBytes[0]))
      if testSwitch.FE_0191751_231166_P_172_DUMP_PREAMP:
         self.oServo.St(TP.dumpPreampRegs_172)

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


#-----------------------------------------------------------------------------------------------------------
class CPreampTempTrm(CState):
   """
      Over temperature fault trim
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oServo = CServo()
      self.READ_REG = 0x01
      self.WRITE_REG = 0x10
      self.POST_READ_REG = 0x02
      try:
         if self.dut.PREAMP_TYPE in ['TI7550','TI7551']:
            import time
            objMsg.printMsg('%s detected, optimize over temperature fault trim' %  (self.dut.PREAMP_TYPE))
            # park/unload the drive and wait 1s
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            self.oServo.St({'test_num':11, 'prm_name':'UnLoad','PARAM_0_4':(0x0E00, 0, 0, 0, 0),'timeout': 60})
            self.oServo.servocmd(0x226F,0x7C00,0x0FBC)       # turn on Negative Regulator
            time.sleep(10)

            self.UpdatePreampReg(self.READ_REG|self.WRITE_REG|self.POST_READ_REG, 0x01, 0, 0)
            self.UpdatePreampReg(self.READ_REG|self.WRITE_REG|self.POST_READ_REG, 0x09, 0, 0x0812)
            result = self.UpdatePreampReg(self.READ_REG|self.WRITE_REG|self.POST_READ_REG, 0x06, 0, 0)
            if result == 0x0001:
               raise
            time.sleep(120)
            self.UpdatePreampReg(self.READ_REG|self.WRITE_REG|self.POST_READ_REG, 0x7C, 0, 0)
            result = self.UpdatePreampReg(self.READ_REG|self.WRITE_REG|self.POST_READ_REG, 0x22, 0, 0x0124)
            if result != 0x0104:
               raise
            result = self.UpdatePreampReg(self.READ_REG, 0x23, 0, 0)
            N = result & 0x03FF
            Die_Temp = -42 + 0.215*N
            temp_spec = 60.5 - Die_Temp
            TmpTrim = self.search_TMPTRIM(temp_spec)
            objMsg.printMsg('TEMPTRM spec = %2.3f.' % (temp_spec))
            objMsg.printMsg('TEMPTRM = %d.' % (TmpTrim))
            self.UpdatePreampReg(self.READ_REG|self.WRITE_REG|self.POST_READ_REG, 0x09, 0, 0x0810)

            self.oServo.St(TP.spinupPrm_2)
            # wsk to head 0, trk 0x200
            ret = self.oServo.wsk(0x200,0)
            #objMsg.printMsg('seek to head:0, trk:0x200.')

            st([11], [], {'timeout': 1000, 'SYM_OFFSET': 431, 'ACCESS_TYPE': 1, 'CWORD1': 512, 'spc_id': 1})
            addr = int(str(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['RAM_ADDRESS']),16) + 4
            st([11], [], {'spc_id': 1, 'END_ADDRESS': ((addr>>16)&0xFFFF, (addr)&0xFFFF), 'ACCESS_TYPE': 2, 'START_ADDRESS': ((addr>>16)&0xFFFF, (addr)&0xFFFF), 'MASK_VALUE': 65295, 'timeout': 1000, 'WR_DATA': (TmpTrim <<4), 'CWORD1': 256})												
            st([178], [], {'timeout': 1000, 'CWORD1':0x420})

            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         else:
            objMsg.printMsg('skip to optimize over temperature fault trim, non %s detected' % (self.dut.PREAMP_TYPE))
      except:
         objMsg.printMsg('cannot proceed, exit test, just use default setting')
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

   #-------------------------------------------------------------------------------------------------------
   def search_TMPTRIM(self, temp_spec):
      TMPTRIM_list = [0, -5.5, -11, -16.5, -22, -27.5, -33, -38.5, 38.5, 33, 27.5, 22, 16.5, 11, 5.5]
      #return min(range(len(TMPTRIM_list)), key=lambda i: abs(TMPTRIM_list[i])-temp_spec)  # python2.4 does not support it
      closest_idex = 0
      for i in range(len(TMPTRIM_list)):
         if abs(TMPTRIM_list[i] - temp_spec) < abs(TMPTRIM_list[closest_idex] - temp_spec):
            closest_idex = i
      return closest_idex

   #-------------------------------------------------------------------------------------------------------
   def UpdatePreampReg(self, oper, addr, page, wr_data):
      ret = 12345
      if oper & self.READ_REG:
         buf, errorCode = self.oServo.Fn(1391, addr, page)            # read
         bufBytes = struct.unpack('BB',buf)
         #objMsg.printMsg('buf:%s, errorCode:%s' % (buf,errorCode))
         ret = bufBytes[0] + (bufBytes[1]<<8)
         objMsg.printMsg('READ register 0x%X = 0x%X.' % (addr,ret))

      if oper & self.WRITE_REG:
         buf, errorCode = self.oServo.Fn(1392, addr, wr_data, page)   # write

      if oper & self.POST_READ_REG:
         buf, errorCode = self.oServo.Fn(1391, addr, page)          # read
         bufBytes = struct.unpack('BB',buf)
         #objMsg.printMsg('buf:%s, errorCode:%s' % (buf,errorCode))
         ret = bufBytes[0] + (bufBytes[1]<<8)
         objMsg.printMsg('POST-READ register 0x%X = 0x%X.' % (addr,ret))
      return ret

