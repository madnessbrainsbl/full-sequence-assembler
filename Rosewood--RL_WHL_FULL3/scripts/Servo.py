#-----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                     #
#-----------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/08 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Servo.py $
# $Revision: #5 $
# $DateTime: 2016/11/08 00:12:47 $
# $Author: gang.c.wang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Servo.py#5 $
# Level: 3
#-----------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
import os, traceback, types
import ScrCmds
from Process import CProcess
from Process import CCudacom
from MediaScan import SeekType
from Drive import objDut
import MessageHandler as objMsg
from time import time
from FSO import CFSO
from  PackageResolution import PackageDispatcher
from StateTable import StateTable
from SIM_FSO import objSimArea
from PowerControl import objPwrCtrl
from Rim import objRimType
from Exceptions import CDblogDataMissing
import struct

class CServo(CProcess, CCudacom):

   def __init__(self):
      CProcess.__init__(self)
      self.dut = objDut

   def clearServoErrCntrs(self):
      """
      Use SF3 Test 159 to set all servo error counters to 0.
      """
      self.St({'test_num':159,'prm_name':"Clear Servo Error Log","CWORD1":5})

   def dumpServoErrCntrs(self, spcId=None):
      """
      Use SF3 Test 159 to read and print out all servo error counters.
      """
      self.St({'test_num':159,'prm_name':"Read Servo Error Log","CWORD1":1,'spc_id':spcId})

   def readServoFIFO(self):
      if testSwitch.FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN:
         self.dumpServoErrCntrs()
      else:
         self.St({'test_num':159,'prm_name':"Read Servo Error Log","CWORD1":1})
      self.St({'test_num':159,'prm_name':"Read Servo Error FIFO","CWORD1":0})
      if testSwitch.DUMP_SERVO_SYMBOL_TABLE_T159:
         self.St({'test_num':159,'prm_name':"Dump Servo Symbol Table","CWORD1":2})

   def esk(self, cylinder, head, mode = 'w', retries = 0):
      """
      Embedded Seek
      """
      args = [cylinder, head, mode]
      if not args or len(args) != 3:
         objMsg.printMsg("esk usage: esk(cylinder, head, mode(= 'r'|'w'|'f'))\n", objMsg.CMessLvl.VERBOSEDEBUG)
         return

      if type(args[0]) != type(1) or type(args[1]) != type(1) or  \
        type(args[2]) != type("") or args[2] not in ['r', 'w', 'f']:
         objMsg.printMsg( "esk usage: esk(cylinder, head, mode(= 'r'|'w'|'f'))\n", objMsg.CMessLvl.VERBOSEDEBUG)
         return

      dir = {'r': 0x15,
            'w': 0x25,
            'f': 0x05
            }
      mode = dir.get(args[2],0x15)
      mCylinder, lCylinder = self.oUtility.ReturnTestCylWord(args[0])
      eskRetryCnt = 0
      while eskRetryCnt <= retries:
         buf, errorCode = self.Fn(1243, lCylinder, mCylinder, args[1], mode)
         if errorCode == 0:
            break
         eskRetryCnt += 1
      else:
         objMsg.printMsg("Embedded Seek Failed - Retry Limit of %s exceeded" %retries)
      try:
         if errorCode != 0:
            ##objMsg.printMsg("esk error: 0x%X"%ord(buf), objMsg.CMessLvl.VERBOSEDEBUG)##GOT EXCEPT
            objMsg.printMsg("errorCode= %x" % (errorCode),objMsg.CMessLvl.IMPORTANT)
            result = struct.unpack("HHL",buf)
            objMsg.printMsg("Seek Status= %x" % (result[0:1]),objMsg.CMessLvl.IMPORTANT)
            objMsg.printMsg("Seek Sense= %x" % (result[2:3]),objMsg.CMessLvl.IMPORTANT)
      except:
         objMsg.printMsg("esk error: No response")
      return errorCode


   def setQuietSeek(self, quietSeek, setQSeekOn = 1):
      self.St(quietSeek['read'])
      if  setQSeekOn == (int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'], 16)&0x8)>>3:
         objMsg.printMsg("Quiet Seek = %d  - DONE" % setQSeekOn)
         return None
      else:
         if setQSeekOn == 1:
            self.St(quietSeek['enable'])
         elif setQSeekOn == 0:
            self.St(quietSeek['disable'])
         self.St(TP.saveSvoRam2Flash_178)
         self.St(quietSeek['read'])
         if  (int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'], 16)&0x8)>>3:
            objMsg.printMsg("Quiet Seek is ON")
         else:
            objMsg.printMsg("Quiet Seek is OFF")


   def wsk(self, cyl, head, retries = 0):
      """
      Write seek
      @param cyl: Target cylinder
      @param head: Target head
      @return: Status from drive
      """
      return self.esk(cyl, head, 'w', retries)


   def rsk(self, cyl, head, retries = 0):
      """
      Read seek
      @param cyl: Target cylinder
      @param head: Target head
      @return: Status from drive
      """
      return self.esk(cyl, head, 'r', retries)


   def mctSeek(self, seekBase, track = '', head = '', type = SeekType.writeSeek):
      #objMsg.printMsg("DEBUG1")
      if track == '':
         self.St(seekBase)
      else:
         if type == SeekType.writeSeek:
            sk = 2<<4
         elif type == SeekType.readSeek:
            sk = 1<<4
         #objMsg.printMsg("DEBUG2")
         seekBase.update({
            'CWORD1'    : seekBase['CWORD1'] | sk,
            'BIT_MASK'  : self.oUtility.ReturnTestCylWord(head),
            'START_CYL' : self.oUtility.ReturnTestCylWord(track),
            'END_CYL'   : self.oUtility.ReturnTestCylWord(track),
         })
         #objMsg.printMsg("DEBUG3")
         objMsg.printDict(seekBase)
         self.St(seekBase)

   def gethsc( self, cyl, head):
     """
     Generic embedded seek command. Display status and sense code from
     drive. Set cudacom globals (gHead, gCylinder, gZone) upon completion.
     @param cyl: Target cylinder
     @param head: Target head
     @displayOptions: 0: display only avg HSC value of the test track, 1 :display HSC of all wedge per test track
     @return: Error code, avg HSC value of the test track
     """
     mCylinder, lCylinder = self.oUtility.ReturnTestCylWord(cyl)
     buf, errorCode = self.Fn(1393, lCylinder, mCylinder, head)
     #buf, errorCode = __ReceiveResults()
     if not errorCode:
        result = struct.unpack(">H",buf)
        return result[0], errorCode 
     return errorCode, errorCode

class CServoFunc(CServo):
   """
      CServoFunc.py
      Description:   Holds output variables and functions for the
                     general function calls of the servo system
   """
   SERVO_TRACK_0_VALUE = 171 # servo track 0 value - 4 16-bit values for each head
   DEMOD_DEST_HEAD_OFFSET = 192 
   SINE_COEFF_OFFSET = 189
   CONTROLLER_MAP_OFFSET = 232
   SNO_FREQ_PHASE_DATA_OFFSET = 470
   SAMTOL_SYMBOL_OFFSET = 302
   ZONED_ACFF_SYMBOL_OFFSET = 239
   LVFF_ENABLE_SYMBOL_OFFSET = 239
   TORN_WRITE_PROTECTION_OFFSET = 485
   SP_LVFF_ENABLE_SYMBOL_OFFSET = 487
   E_PREAMP_BIAS_MODE = 450
   SCOPY_CONTROL_FEATURE = 649
   BIAS_OPTIONS = 450           # T186
   LBC_GAIN                 = 568
   ADAPTIVE_ANTI_NOTCH_SYMBOL_OFFSET = 239
   ADAPTIVE_ANTI_NOTCH_BIT = 4  # The bit that controls adaptive anti-notch status in ADAPTIVE_ANTI_NOTCH_SYMBOL_OFFSET
   if testSwitch.FE_0127082_426568_USE_FREEZE_RESTORE_FOR_ADAPTIVE_ANTINOTCH:
       ADAPTIVE_ANTI_NOTCH_BIT = 10  # The bit that controls adaptive anti-notch status in ADAPTIVE_ANTI_NOTCH_SYMBOL_OFFSET
   NUM_CHAN_REG_OFFSET = 343  # offest of u16_NumberOfChannelRegisterSettingsInSAP
   START_OF_CHAN_REG_OFFSET = 344 # offset of ChannelRegisterSettingsInSAP
   ZONED_ACFF_MASK = 0
   SAP_HEAD_TYPE = 239
   SAP_HEAD_TYPE_MASK = 7
   STRESS_CHANNEL_IN_FLAW_SCAN = 615
   RADIALTIMINGCOEFF_PRE2 = 165
   RADIALTIMINGCOEFF_CRT2 = 580
   if testSwitch.FE_0155771_395340_P_HDSTR_UPDATE_ZAP_DATA_ON_GHG_PROCESS:
      RRO_MODE_SYMBOL_OFFSET = 152  # RRO_MODE Address.
   SWOT_SENSOR = {
      'name' : 'SWOT_SENSOR',
      'offsetValue' : 222, # Servo symbol table offset containing the bit that controls the SWOT sensor
      'bit' : 2 # The bit that controls adaptive SWOT sensor status in SWOT_SENSOR_SYMBOL_OFFSET
   }
   ENABLE_HIGH_BW = {
      'name' : 'ENABLE_HIGH_BW',
      'offsetValue' : 239, # Servo symbol table offset (u16_Flags) containing the bit that controls the Servo Filter
      'bit' : 11 # The bit that controls whether to use a BW bandwidth filter for Servo
   }
   I32_RRO_POLY = {
      'name' : 'I32_RRO_POLY',
      'offsetValue' : 352, # Servo symbol table offset (u16_Flags) RETURNS ILLEGAL ADDR IF NOT POLY ZAP

   }
   U16_SAP_MISC_FLAGS = {
      'name' : 'U16_SAP_MISC_FLAGS',
      'offsetValue' : 239, # Servo symbol table offset (u16_Flags) 1 if results are in SAP

   }


   getSymbolViaAddrPrm_11 = {
                              'test_num'            :11,
                              'prm_name'            :'GetSymbolViaAddr',
                              'timeout'             :1000,
                              'spc_id'              :1,
                              'CWORD1'              :(0x0001),
                              'ACCESS_TYPE'         :(3),
                           }
   getServoSymbolPrm_11 = {
          'base': {
              'test_num'        :11,
              'prm_name'        :'getServoSymbolPrm',
              'timeout'         :1000,
              'spc_id'          :1,
              'CWORD1'          :(0x0200),
              'ACCESS_TYPE'     :(0),
                  },
          'SYM_OFFSET': {  'maxServoTrack'                     : (2),
                           'rpm'                               : (144),
                           'servoWedges'                       : (140),
                           'arcTPI'                            : (142),
                           'ostRatioAddr'                      : (234),
                           'ZONED_ACFF_SYMBOL_OFFSET'          : ZONED_ACFF_SYMBOL_OFFSET,
                           'SAP_HEAD_OFFSET'                   : SAP_HEAD_TYPE,
                           'LVFF_ENABLE_SYMBOL_OFFSET'         : LVFF_ENABLE_SYMBOL_OFFSET,
                           'SP_LVFF_ENABLE_SYMBOL_OFFSET'      : SP_LVFF_ENABLE_SYMBOL_OFFSET,
                           'E_PREAMP_BIAS_MODE'                : E_PREAMP_BIAS_MODE,
                           'SCOPY_CONTROL_FEATURE'             : SCOPY_CONTROL_FEATURE,
                           'BIAS_OPTIONS'                      : BIAS_OPTIONS,
                           'NUM_CHAN_REG_OFFSET'               : NUM_CHAN_REG_OFFSET,
                           'START_OF_CHAN_REG_OFFSET'          : START_OF_CHAN_REG_OFFSET,
                           'ADAPTIVE_ANTI_NOTCH_SYMBOL_OFFSET' : ADAPTIVE_ANTI_NOTCH_SYMBOL_OFFSET,
                           'SWOT_SENSOR'                       : SWOT_SENSOR['offsetValue'],
                           'ENABLE_HIGH_BW'                    : ENABLE_HIGH_BW['offsetValue'],
                           'I32_RRO_POLY'                      : I32_RRO_POLY['offsetValue'],
                           'U16_SAP_MISC_FLAGS'                : U16_SAP_MISC_FLAGS['offsetValue'],
                           'SAMTOL_SYMBOL_OFFSET'              : SAMTOL_SYMBOL_OFFSET,
                           'DEMOD_DEST_HEAD_OFFSET'            : DEMOD_DEST_HEAD_OFFSET,
                           'SINE_COEFF_OFFSET'                 : SINE_COEFF_OFFSET,
                           'CONTROLLER_MAP_OFFSET'             : CONTROLLER_MAP_OFFSET,
                           'SNO_FREQ_PHASE_DATA_OFFSET'        : SNO_FREQ_PHASE_DATA_OFFSET,
                           'SERVO_TRACK_0_VALUE'               : SERVO_TRACK_0_VALUE,
                           'TORN_WRITE_PROTECTION_OFFSET'      : TORN_WRITE_PROTECTION_OFFSET,
                           'STRESS_CHANNEL_IN_FLAW_SCAN'       : STRESS_CHANNEL_IN_FLAW_SCAN,
                           'LBC_GAIN'                          : LBC_GAIN,
                           'RADIALTIMINGCOEFF_PRE2'            : RADIALTIMINGCOEFF_PRE2,
                           'RADIALTIMINGCOEFF_CRT2'            : RADIALTIMINGCOEFF_CRT2,

          }
          }
   if testSwitch.FE_0155771_395340_P_HDSTR_UPDATE_ZAP_DATA_ON_GHG_PROCESS:
      getServoSymbolPrm_11['SYM_OFFSET'].update({'RRO_MODE_SYMBOL_OFFSET':RRO_MODE_SYMBOL_OFFSET})
   ReadPVDDataPrm_11 = {
         'test_num'        :11,
         'prm_name'        :'ReadPVDFeatures2Bit4',
         'timeout'         :1000,
         'spc_id'          :1,
         'CWORD1'          :(0x4000),
         'VPD_DATA'        : (0,5)

         }

   def __init__(self):
      CServo.__init__(self)

   def getMDWCalState(self, calDict):
      self.St(calDict['read'])
      calCompleteMask = calDict['CalCompleteMask']
      coarseVal = int(str(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA']),16)

      calRequired = (coarseVal & calCompleteMask) > 0 #If bit set then cal is required
      if not calRequired:self.setMDWCalState(1)   #process value tracks completion not un-completion
      else:self.setMDWCalState(0)
      return calRequired

   def MDWCalComplete(self):
      """Reset MDW Uncal bit"""
      self.St({'test_num':178,'prm_name':"Reset MDW Uncal bit",'MD_SYNC':4,'CWORD1':0x20,'timeout': 100, 'spc_id': 0})
      self.setMDWCalState(1)

   def enableFaskSeekMode(self):
      """Enable Fast seek mode using MD_SYNC = 2"""
      self.St({
         'test_num': 178,
         'prm_name': "Enable Fast Seeks",
         'CWORD1':0x20,
         'MD_SYNC': 2,
         'timeout':100,
           })


   def setOClim(self,inPrm = {}, oclim = 16, updateFlash = 0):
      """ Set OC_LIM for drive
      @param inPrm: Input parameter dictionary conforming to MCT documentation
      @param oclim: off-track limit for servo write fault threshold-> only used if inPrm = {}
      """
      if not inPrm == {}:
         self.St(inPrm)
      else:
         oclimVal =  int((oclim/100.0)*4096)
         oclimUpd = {'test_num':178,'prm_name':"Set AFH OCLIM_178","SET_OCLIM": oclimVal}
         if updateFlash == 1:
                     oclimUpd.update({"CWORD1":0x420})
         self.St(oclimUpd)

   def getOCLIM(self, oclimSAPOffset, percentTrackScaler = 4096.0):
      """
      Retrieve the oclim stored in the SAP
      """
      if testSwitch.FE_0111784_347506_USE_DEFAULT_OCLIM_FOR_FLAWSCAN:
         self.St({'test_num':11,'prm_name':'getOCLIM','CWORD1':0x200,'SYM_OFFSET':oclimSAPOffset})
      else:
         self.St({'test_num':11,'CWORD1':0x200,'SYM_OFFSET':oclimSAPOffset})
      oclimVal = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)

      return (oclimVal/percentTrackScaler) * 100

   def setOCLIM_byHead(self, oclimSAPOffset, iHead, OCLIMPercent):
      oclim_hex = int(round(4096.0 * OCLIMPercent/100.0))
      self.St({'test_num':11, 'prm_name':'setOCLIM_byHead', 'CWORD1':0x800, 'MASK_VALUE': 1 << iHead, 'SYM_OFFSET':oclimSAPOffset, 'WR_DATA': oclim_hex})

   def setreadOCLIM_allHeads(self, OCLIMPercent):
      oclimSAPOffset = 105
      self.setOCLIM_byHead(oclimSAPOffset, 0, OCLIMPercent)

   def setwriteOCLIM_byHead(self, iHead, OCLIMPercent):
      oclimSAPOffset = 42
      self.setOCLIM_byHead(oclimSAPOffset, iHead, OCLIMPercent)

   def get_CONTROLLER_MAP_addr(self):
      return self.readServoSymbolTable(['CONTROLLER_MAP_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

   def fetch_CONTROLLER_MAP_16(self):
      contmap_addr = self.get_CONTROLLER_MAP_addr()
      read16bitprm = self.getSymbolViaAddrPrm_11
      read16bitprm['ACCESS_TYPE'] = 2
      read16bitprm['EXTENDED_MASK_VALUE'] = 65535
      cont_byte1 = self.getValueFromServoRam(contmap_addr , read16bitprm)
      cont_byte2 = self.getValueFromServoRam(contmap_addr +2, read16bitprm)
      cont_byte3 = self.getValueFromServoRam(contmap_addr +4, read16bitprm)
      cont_byte4 = self.getValueFromServoRam(contmap_addr +6, read16bitprm)
      return cont_byte1, cont_byte2, cont_byte3, cont_byte4

   def set_cont_map(self,wrData_hi,wrData):
      contmap_addr = self.get_CONTROLLER_MAP_addr()
      selfprm = dict(self.getSymbolViaAddrPrm_11)
      selfprm['CWORD1'] = 0x02
      selfprm['ACCESS_TYPE'] = 2  # 16-bit access
      selfprm['WR_DATA'] = wrData
      #selfprm['EXTENDED_WR_DATA'] = (wrData_32bit >> 16)
      selfprm['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(contmap_addr+4)
      selfprm['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(contmap_addr+4)
      self.St(selfprm)
      ## write higher byte
      selfprm['WR_DATA'] = wrData_hi
      #selfprm['EXTENDED_WR_DATA'] = (wrData_32bit >> 16)
      selfprm['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(contmap_addr+6)
      selfprm['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(contmap_addr+6)
      self.St(selfprm)

   def get_SNO_PHASE_DATA_addr(self):
      return self.readServoSymbolTable(['SNO_FREQ_PHASE_DATA_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

   def set_sno_phase_data(self,wrData_hi,wrData,offset):
      sno_phase_data_addr = self.get_SNO_PHASE_DATA_addr()
      selfprm = dict(self.getSymbolViaAddrPrm_11)
      selfprm['CWORD1'] = 0x02
      selfprm['ACCESS_TYPE'] = 2  # 16-bit access
      selfprm['WR_DATA'] = wrData
      #selfprm['EXTENDED_WR_DATA'] = (wrData_32bit >> 16)
      selfprm['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(sno_phase_data_addr+offset)
      selfprm['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(sno_phase_data_addr+offset)
      self.St(selfprm)
      ## write higher byte
      selfprm['WR_DATA'] = wrData_hi
      #selfprm['EXTENDED_WR_DATA'] = (wrData_32bit >> 16)
      selfprm['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(sno_phase_data_addr+offset+2)
      selfprm['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(sno_phase_data_addr+offset+2)
      self.St(selfprm)

   def find_demod_hd(self):
      self.St(TP.spinup_D00_Prm)
      demodaddr = self.readServoSymbolTable(['DEMOD_DEST_HEAD_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)
      tmp_dict = self.getSymbolViaAddrPrm_11
      tmp_dict['ACCESS_TYPE'] = 2
      tmp_dict['EXTENDED_MASK_VALUE'] = 65535
      hdfound = self.getValueFromServoRam(demodaddr, tmp_dict)
      return (hdfound & 0x01)

   def get_SINE_COEFF_addr(self):
      return self.readServoSymbolTable(['SINE_COEFF_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

   def fetch_SINE_COEFF_16(self):
      coeff_addr = self.get_SINE_COEFF_addr()
      read16bitprm = self.getSymbolViaAddrPrm_11
      read16bitprm['ACCESS_TYPE'] = 2
      read16bitprm['EXTENDED_MASK_VALUE'] = 65535
      hd0_coeff = self.getValueFromServoRam(coeff_addr, read16bitprm)
      hd0_coeff_hi = self.getValueFromServoRam(coeff_addr+2, read16bitprm)
      hd1_coeff = self.getValueFromServoRam(coeff_addr+4, read16bitprm)
      hd1_coeff_hi = self.getValueFromServoRam(coeff_addr+6, read16bitprm)
      return hd0_coeff_hi, hd0_coeff, hd1_coeff_hi, hd1_coeff

   def fetch_SINE_COEFF_32(self):
      coeff_addr = self.get_SINE_COEFF_addr()
      read32bitprm = self.getSymbolViaAddrPrm_11
      hd0_coeff = self.getValueFromServoRam(coeff_addr, read32bitprm)
      hd1_coeff = self.getValueFromServoRam(coeff_addr+4, read32bitprm)
      return hd0_coeff, hd1_coeff
      
   def set_hd_coeff_32(self,tgthead,wrData_32bit):
      coeff_addr = self.get_SINE_COEFF_addr()
      selfprm = dict(self.getSymbolViaAddrPrm_11)
      selfprm['CWORD1'] = 0x02
      selfprm['ACCESS_TYPE'] = 2  # 16-bit access
      selfprm['WR_DATA'] = (0xFFFF & wrData_32bit)
      #selfprm['EXTENDED_WR_DATA'] = (wrData_32bit >> 16)
      selfprm['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr)
      selfprm['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr)
      if tgthead == 1:
         selfprm['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr+4)
         selfprm['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr)
      self.St(selfprm)
      ## write higher byte
      selfprm['WR_DATA'] = (wrData_32bit >> 16)
      #selfprm['EXTENDED_WR_DATA'] = (wrData_32bit >> 16)
      selfprm['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr+2)
      selfprm['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr+2)
      if tgthead == 1:
         selfprm['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr+4)
         selfprm['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr+4)
      self.St(selfprm)
   
   def set_hd_coeff(self,tgthead,wrData_hi,wrData):
      coeff_addr = self.get_SINE_COEFF_addr()
      selfprm = dict(self.getSymbolViaAddrPrm_11)
      selfprm['CWORD1'] = 0x02
      selfprm['ACCESS_TYPE'] = 2  # 16-bit access
      selfprm['WR_DATA'] = wrData
      #selfprm['EXTENDED_WR_DATA'] = (wrData_32bit >> 16)
      selfprm['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr)
      selfprm['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr)
      if tgthead:
         selfprm['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr+4)
         selfprm['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr+4)
      self.St(selfprm)
      ## write higher byte
      selfprm['WR_DATA'] = wrData_hi
      #selfprm['EXTENDED_WR_DATA'] = (wrData_32bit >> 16)
      selfprm['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr+2)
      selfprm['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr+2)
      if tgthead:
         selfprm['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr+6)
         selfprm['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(coeff_addr+6)
      self.St(selfprm)
   
   def getSAP_headAddress(self):
      return self.readServoSymbolTable(['SAP_HEAD_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

   def getSAP_headTypeEnum(self, sapHeadAddress = None):
      if not sapHeadAddress:
         sapHeadAddress = self.getSAP_headAddress()

      return ((1<<self.SAP_HEAD_TYPE_MASK) & self.getValueFromServoRam(sapHeadAddress, self.getSymbolViaAddrPrm_11)) >> self.SAP_HEAD_TYPE_MASK

   def setSAP_HeadType(self, headType = 'RHO'):
      if testSwitch.FE_0112851_007955_ADD_HWY_OPTION_TO_SETSAP_HEADTYPE:
         if not testSwitch.SET_HEAD_SUPPLIER_IN_SAP:
            return
         headEnum = {'RHO': 0,
                     'TDK': 1,
                     'HWY': 1,
         }
      else:
         if not testSwitch.SET_HEAD_SUPPLIER_IN_SAP:
            return
         headEnum = {'RHO': 0,
                     'TDK': 1,
         }

      headEnumVal = headEnum[headType]

      ScrCmds.insertHeader("Setting HEAD type in SAP to %s" % headType)

      objMsg.printMsg("\tSetting bit %d to %d." % (self.SAP_HEAD_TYPE_MASK, headEnumVal))

      addr = self.getSAP_headAddress()

      value = self.getSAP_headTypeEnum(addr)
      if not value == headEnumVal:

         wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
         wrSapAddr['CWORD1'] = 0x100
         wrSapAddr['ACCESS_TYPE'] = 1
         wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(addr)
         wrSapAddr['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(addr)
         wrSapAddr['WR_DATA'] = headEnumVal<<self.SAP_HEAD_TYPE_MASK

         wrSapAddr['MASK_VALUE'] = (1<<self.SAP_HEAD_TYPE_MASK) ^ 0xFFFF

         self.St(wrSapAddr)

         value = self.getSAP_headTypeEnum(addr)
         if not int(value) == self.getSAP_headTypeEnum(addr) and not testSwitch.virtualRun:
            ScrCmds.raiseException(10189, "Memory modification failed for ACFF")

         CFSO().saveSAPtoFLASH()
      else:
         objMsg.printMsg("SAP Head type already set to correct value.")


      ScrCmds.insertHeader("Setting HEAD type COMPLETE")


   def getZonedACFFEnableBit(self, acffAddress = None):
      if acffAddress == None:
         acffAddress = self.readServoSymbolTable(['ZONED_ACFF_SYMBOL_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

      acffBit = self.getValueFromServoRam(acffAddress, self.getSymbolViaAddrPrm_11) & 1 #lower word from return
      if testSwitch.virtualRun:
         acffBit = 1

      return acffBit

   def setZonedACFFHdstr(self, enable = True):
      modifiedVal = False

      if 'S' in StateTable[objDut[PortIndex].nextOper][objDut[PortIndex].nextState][OPT]:

         wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
         wrSapAddr['CWORD1'] = 0x100
         wrSapAddr['ACCESS_TYPE'] = 1

         if objDut[PortIndex].serialnum[1:3] in ['VY']: # 1 hd
            acffAddress = 0X04002E5E
         elif objDut[PortIndex].serialnum[1:3] in ['VM']: # 2 hd
            acffAddress = 0X04002EC0
         elif objDut[PortIndex].serialnum[1:3] in ['VN', 'VP']: # 3,4 hd
            acffAddress = 0X04002F88
         else:
            ScrCmds.raiseException(10189, "Get ACFF address failed")

         wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(acffAddress)
         wrSapAddr['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(acffAddress)
         wrSapAddr['WR_DATA'] = int(enable)
         #ACFF is the lowest bit in this ram address
         wrSapAddr['MASK_VALUE'] = 0xFFFE

         self.St(wrSapAddr)
         CFSO().saveSAPtoFLASH()
         modifiedVal = True

      return modifiedVal
   def setZonedACFF(self, enable = True):
      modifiedVal = False

      if 'S' in StateTable[self.dut.nextOper][self.dut.nextState][OPT] or self.dut.HDSTR_RECORD_ACTIVE == 'Y':
         return modifiedVal

      acffAddress = self.readServoSymbolTable(['ZONED_ACFF_SYMBOL_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

      if (not testSwitch.ACFF_DISABLE_RO_CAL_IN_SF3) and not (enable == self.getZonedACFFEnableBit(acffAddress)):

         wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
         wrSapAddr['CWORD1'] = 0x100
         wrSapAddr['ACCESS_TYPE'] = 1
         wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(acffAddress)
         wrSapAddr['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(acffAddress)
         wrSapAddr['WR_DATA'] = int(enable)
         #ACFF is the lowest bit in this ram address
         wrSapAddr['MASK_VALUE'] = 0xFFFE

         self.St(wrSapAddr)


         #self.St(TP.spindownPrm_2)
         #self.St(TP.spinupPrm_1)

         if not int(enable) == self.getZonedACFFEnableBit(acffAddress) and not testSwitch.virtualRun:
            ScrCmds.raiseException(10189, "Memory modification failed for ACFF")

         CFSO().saveSAPtoFLASH()
         modifiedVal = True
      return modifiedVal

   def getEPreampBiasModeBit(self, biasAddress = None):
      if biasAddress == None:
         biasAddress = self.readServoSymbolTable(['E_PREAMP_BIAS_MODE',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)
      return biasAddress

   def getScopyControlFeatureAdd(self, biasAddress = None):
      if biasAddress == None:
         biasAddress = self.readServoSymbolTable(['SCOPY_CONTROL_FEATURE',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)
      return biasAddress

   def getLVFFEnableBit(self, lvffAddress = None):
      if lvffAddress == None:
         lvffAddress = self.readServoSymbolTable(['LVFF_ENABLE_SYMBOL_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)
      lvffBit = (self.getValueFromServoRam(lvffAddress, self.getSymbolViaAddrPrm_11) & 0x0200) >> 9
      if testSwitch.virtualRun:
         lvffBit = 1
      return lvffBit

   def getSPLVFFEnableBit(self, splvffAddress = None):
      if splvffAddress == None:
         splvffAddress = self.readServoSymbolTable(['SP_LVFF_ENABLE_SYMBOL_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)
      splvffBit = (self.getValueFromServoRam(splvffAddress, self.getSymbolViaAddrPrm_11) & 0x0001)
      if testSwitch.virtualRun: splvffBit = 1
      return splvffBit
   
   def setePreampBiasMode(self, enable = True):
      modifiedVal = False


      biasAddress = self.readServoSymbolTable(['E_PREAMP_BIAS_MODE',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

      if not (enable == self.getEPreampBiasModeBit(biasAddress)):
         wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
         wrSapAddr['CWORD1']        = 0x100
         wrSapAddr['ACCESS_TYPE']   = 1
         wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(biasAddress)
         wrSapAddr['END_ADDRESS']   = self.oUtility.ReturnTestCylWord(biasAddress)
         wrSapAddr['WR_DATA']       = int(enable)
         wrSapAddr['MASK_VALUE'] = 0xFE
         self.St(wrSapAddr)

         wr2SapAddr = dict(self.getSymbolViaAddrPrm_11)
         wr2SapAddr['CWORD1']        = 0x1
         wr2SapAddr['ACCESS_TYPE']   = 1
         wr2SapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(biasAddress)
         wr2SapAddr['END_ADDRESS']   = self.oUtility.ReturnTestCylWord(biasAddress)
         self.St(wr2SapAddr)
         modifiedVal = True
      return modifiedVal

   def setScopyControlFeature(self, enable = True):
      modifiedVal = False
      biasAddress = self.readServoSymbolTable(['SCOPY_CONTROL_FEATURE',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

      if not (enable == self.getScopyControlFeatureAdd(biasAddress)):
         wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
         wrSapAddr['CWORD1']        = 0x100
         wrSapAddr['ACCESS_TYPE']   = 1
         wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(biasAddress)
         wrSapAddr['END_ADDRESS']   = self.oUtility.ReturnTestCylWord(biasAddress)
         wrSapAddr['WR_DATA']       = int(enable)
         wrSapAddr['MASK_VALUE'] = 0xFE
         self.St(wrSapAddr)

         wr2SapAddr = dict(self.getSymbolViaAddrPrm_11)
         wr2SapAddr['CWORD1']        = 0x1
         wr2SapAddr['ACCESS_TYPE']   = 1
         wr2SapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(biasAddress)
         wr2SapAddr['END_ADDRESS']   = self.oUtility.ReturnTestCylWord(biasAddress)
         self.St(wr2SapAddr)
         modifiedVal = True
      return modifiedVal

   def setBiasOption(self, biasOption):
      modifiedVal = False

      biasAddress = self.readServoSymbolTable(['BIAS_OPTIONS',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

      wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
      wrSapAddr['CWORD1']        = 0x100
      wrSapAddr['ACCESS_TYPE']   = 1
      wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(biasAddress)
      wrSapAddr['END_ADDRESS']   = self.oUtility.ReturnTestCylWord(biasAddress)
      wrSapAddr['WR_DATA']       = int( biasOption )
      wrSapAddr['MASK_VALUE'] = 0x7E
      self.St(wrSapAddr)

      wr2SapAddr = dict(self.getSymbolViaAddrPrm_11)
      wr2SapAddr['CWORD1']        = 0x1
      wr2SapAddr['ACCESS_TYPE']   = 1
      wr2SapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(biasAddress)
      wr2SapAddr['END_ADDRESS']   = self.oUtility.ReturnTestCylWord(biasAddress)
      self.St(wr2SapAddr)
      modifiedVal = True
      return modifiedVal

   def setLVFF(self, enable = True):
      modifiedVal = False

      if self.dut.HDSTR_RECORD_ACTIVE == 'Y':
         return modifiedVal

      lvffAddress = self.readServoSymbolTable(['LVFF_ENABLE_SYMBOL_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

      if not (enable == self.getLVFFEnableBit(lvffAddress)):
         wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
         wrSapAddr['CWORD1']        = 0x100
         wrSapAddr['ACCESS_TYPE']   = 2
         wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(lvffAddress)
         wrSapAddr['END_ADDRESS']   = self.oUtility.ReturnTestCylWord(lvffAddress)
         wrSapAddr['WR_DATA']       = int(enable) << 9
         wrSapAddr['MASK_VALUE'] = 0xFDFF
         self.St(wrSapAddr)
         if not int(enable) == self.getLVFFEnableBit(lvffAddress) and not testSwitch.virtualRun:
            ScrCmds.raiseException(10189, "Memory modification failed for LVFF")
         CFSO().saveSAPtoFLASH()
         modifiedVal = True
      return modifiedVal

   def setSPLVFF(self, enable = True):
      modifiedVal = False

      if self.dut.HDSTR_RECORD_ACTIVE == 'Y':
         return modifiedVal

      splvffAddress = self.readServoSymbolTable(['SP_LVFF_ENABLE_SYMBOL_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

      if not (enable == self.getSPLVFFEnableBit(splvffAddress)):
         wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
         wrSapAddr['CWORD1']        = 0x100
         wrSapAddr['ACCESS_TYPE']   = 2
         wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(splvffAddress)
         wrSapAddr['END_ADDRESS']   = self.oUtility.ReturnTestCylWord(splvffAddress)
         wrSapAddr['WR_DATA']       = 1
         wrSapAddr['MASK_VALUE'] = 0xFFFE
         self.St(wrSapAddr)
         if not int(enable) == self.getSPLVFFEnableBit(splvffAddress) and not testSwitch.virtualRun:
            ScrCmds.raiseException(10189, "Memory modification failed for LVFF")
         CFSO().saveSAPtoFLASH()
         modifiedVal = True
      return modifiedVal


   def getAntiNotchEnableBit(self, antiNotchAddress = None):
      if antiNotchAddress == None:
         antiNotchAddress = self.readServoSymbolTable(['LVFF_ENABLE_SYMBOL_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)
      antiNotchBit = (self.getValueFromServoRam(antiNotchAddress, self.getSymbolViaAddrPrm_11) >> self.ADAPTIVE_ANTI_NOTCH_BIT) & 1
      if testSwitch.virtualRun:
         antiNotchBit = 1
      return antiNotchBit

   def setAdaptiveAntiNotch(self, enable = True):
      modifiedVal = False

      if self.dut.HDSTR_RECORD_ACTIVE == 'Y':
         return modifiedVal

      antiNotchAddress = self.readServoSymbolTable(['ADAPTIVE_ANTI_NOTCH_SYMBOL_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

      if not (enable == self.getAntiNotchEnableBit(antiNotchAddress)):
         wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
         wrSapAddr['CWORD1']        = 0x100
         wrSapAddr['ACCESS_TYPE']   = 2
         wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(antiNotchAddress)
         wrSapAddr['END_ADDRESS']   = self.oUtility.ReturnTestCylWord(antiNotchAddress)
         wrSapAddr['WR_DATA']       = int(enable) << self.ADAPTIVE_ANTI_NOTCH_BIT
         wrSapAddr['MASK_VALUE'] = 0xFFFF - (1<<self.ADAPTIVE_ANTI_NOTCH_BIT)
         self.St(wrSapAddr)
         if not int(enable) == self.getAntiNotchEnableBit(antiNotchAddress) and not testSwitch.virtualRun:
            ScrCmds.raiseException(10189, "Memory modification failed for AdaptiveAntiNotch")
         CFSO().saveSAPtoFLASH()
         modifiedVal = True
      return modifiedVal

   def getServoSymbolData(self, addrName='LVFF_ENABLE_SYMBOL_OFFSET', bitMask=0xFFFF ):
      read16bitprm = self.getSymbolViaAddrPrm_11
      read16bitprm['ACCESS_TYPE'] = 2
      addr    = self.readServoSymbolTable((addrName,), self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, read16bitprm)
      databit = self.getValueFromServoRam(addr, read16bitprm)
      return ( databit & bitMask )

   def setServoSymbolData(self, addrName='LVFF_ENABLE_SYMBOL_OFFSET', wrData=0, validbit=0 ):
      modifiedVal = False
      if not validbit:
         return modifiedVal

      read16bitprm = self.getSymbolViaAddrPrm_11
      read16bitprm['ACCESS_TYPE'] = 2
      addr    = self.readServoSymbolTable((addrName,), self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, read16bitprm)
      databit = self.getValueFromServoRam(addr, read16bitprm)
      if (databit & validbit) != wrData:
         wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
         wrSapAddr['CWORD1']        = 0x100
         wrSapAddr['ACCESS_TYPE']   = 2
         wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(addr)
         wrSapAddr['END_ADDRESS']   = self.oUtility.ReturnTestCylWord(addr)
         wrSapAddr['WR_DATA']       = wrData
         wrSapAddr['MASK_VALUE'] = 0xFFFF - validbit
         self.St(wrSapAddr)
         databit = self.getValueFromServoRam(addr, self.getSymbolViaAddrPrm_11)
         if (databit & validbit) != wrData and not testSwitch.virtualRun:
            ScrCmds.raiseException(10189, "Memory modification failed for addr %s wrData=%04X" % (addrName,wrData))
         CFSO().saveSAPtoFLASH()
         modifiedVal = True

      return modifiedVal

   def getServoSymbolRange(self, addrName='SERVO_TRACK_0_VALUE', count=1, offset=2 ):
      addr    = self.readServoSymbolTable([addrName,],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)
      tmpParam = dict(self.getSymbolViaAddrPrm_11)
      tmpParam["CWORD1"] = 0x0080 # Read by range
      tmpParam['ACCESS_TYPE']   = 2
      tmpParam["START_ADDRESS"] = self.oUtility.ReturnTestCylWord(addr)
      tmpParam["END_ADDRESS"] = self.oUtility.ReturnTestCylWord(addr + (count * offset))
      self.St(tmpParam)

   def setServoSymbolRange(self, addrName='SERVO_TRACK_0_VALUE', wrData=0, count=1, offset=2, offaddr=0 ):
      staddr    = self.readServoSymbolTable([addrName,],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11) + offaddr
      wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
      wrSapAddr['CWORD1']        = 0x100 # Read / modify / write RAM
      wrSapAddr['ACCESS_TYPE']   = 2
      wrSapAddr['WR_DATA']       = wrData

      for addr in range(staddr, staddr + (count * offset), 2):
         wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(addr)
         wrSapAddr['END_ADDRESS']   = self.oUtility.ReturnTestCylWord(addr)
         self.St(wrSapAddr)
      CFSO().saveSAPtoFLASH()


   def getSapBitSetting(self, feature, featureAddress = None):
      if featureAddress == None:
         featureAddress = self.readServoSymbolTable([feature['name'],],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)
      featureBitSetting = (self.getValueFromServoRam(featureAddress, self.getSymbolViaAddrPrm_11) >> feature['bit']) & 1
      if testSwitch.virtualRun:
         featureBitSetting = 1
      return featureBitSetting

   def modifyServoSapBit(self, feature, enable = True):
      modifiedVal = False

      if self.dut.HDSTR_RECORD_ACTIVE == 'Y':
         return modifiedVal

      featureAddress = self.readServoSymbolTable([feature['name'],],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

      if not (enable == self.getSapBitSetting(feature, featureAddress)):
         wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
         wrSapAddr['CWORD1']        = 0x100
         wrSapAddr['ACCESS_TYPE']   = 2
         wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(featureAddress)
         wrSapAddr['END_ADDRESS']   = self.oUtility.ReturnTestCylWord(featureAddress)
         wrSapAddr['WR_DATA']       = int(enable) << feature['bit']
         wrSapAddr['MASK_VALUE'] = 0xFFFF - (1<<feature['bit'])
         self.St(wrSapAddr)
         if not int(enable) == self.getSapBitSetting(feature, featureAddress) and not testSwitch.virtualRun:
            ScrCmds.raiseException(10189, "Memory modification failed for %s" % feature['name'])
         CFSO().saveSAPtoFLASH()
         modifiedVal = True
      return modifiedVal

   if testSwitch.WA_0126043_426568_TOGGLE_SAPBIT_FOR_HIGH_BW_FILTER or testSwitch.WA_0129386_426568_DISABLE_LVFF_AFTER_ZAP_BASED_ON_PCBA_NUM:
      def PCBAsetting(self, pcba_nums, setCriteria):
         #used for VE
         if testSwitch.virtualRun == 1:
            DriveAttributes['PCBA_PART_NUM'] = '000000000'
         if DriveAttributes.has_key('PCBA_PART_NUM'):
            pwaAttr = DriveAttributes.get('PCBA_PART_NUM', None)
            if pwaAttr not in pcba_nums:
               if setCriteria == 'FILTER':
                  # if the part number is not in the list in test parameters the bit is set -> high BW filter
                  objMsg.printMsg("Enabling High Bandwidth Filter for Servo:")
                  self.modifyServoSapBit(self.ENABLE_HIGH_BW, True)
               elif setCriteria == 'LVFF':
                  # if the part number is not in the list in test parameters LVFF is enabled
                  objMsg.printMsg("Enabling LVFF after ZAP based on PCBA:")
                  self.setLVFF(enable=True)
            else:
               if setCriteria == 'FILTER':
                  # if the part number is in the list in test parameters the bit is not set -> low BW filter
                  objMsg.printMsg("Enabling Low Bandwidth Filter for Servo:")
                  self.modifyServoSapBit(self.ENABLE_HIGH_BW, False)
               elif setCriteria == 'LVFF':
                  # if the part number is in the list in test parameters LVFF is disabled
                  objMsg.printMsg("Disabling LVFF after ZAP based on PCBA:")
                  self.setLVFF(enable=False)
         else:
            #fails if no PCBA number assigned to the drive attributes
            ScrCmds.raiseException(10648,"DriveAttributes has no PCBA_PART_NUM key")

   def setSwotSensor(self, enable = True):
      self.modifyServoSapBit(self.SWOT_SENSOR, enable)

   def setChannelRegistersInSAP(self):
      """
      setChannelRegistersInSAP can be used to set channel register values by writing to the SAP.
      In order to use this functionality, you must have servo code which supports this ability, and
      SF3 switch FE_0115982_357915_SET_CHANNEL_REG_IN_SAP must be enabled.  The test parameter
      dictionary setChannelRegisterSettingsInSAP is used to control the registers and values that
      are written.
      """

      maxNumChanRegInSAP = 5  # The maximum number of channel register settings available in the SAP
      write16BitValuesToServoRam = {
         'test_num'      : 11,
         'prm_name'      : 'Write16BitValuesToServoRam',
         'timeout'       : 1000,
         'spc_id'        : 1,
         'CWORD1'        : (0x0002),
         'ACCESS_TYPE'   : (2), # 16 bit
         #'START_ADDRESS' : 0, # User must specify this value
         #'WR_DATA'       : 0, # User must specify this value
      }

      # Get the number of register settings from the test parameters
      regSettings = getattr(TP, 'setChannelRegisterSettingsInSAP', {})
      numChanTestParms = len(regSettings.keys())
      if numChanTestParms == 0:
         objMsg.printMsg("Test parameter setChannelRegisterSettingsInSAP does not exist, or specifies no channel registers to be written to SAP")
         return

      # Get the address of u16_NumberOfChannelRegisterSettingsInSAP
      numChanRegAddress = self.readServoSymbolTable(['NUM_CHAN_REG_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

      # If Servo does not support this feature, then do nothing
      if numChanRegAddress == 0xFFFF:
         objMsg.printMsg("Servo does not support ChannelRegisterSettingsInSAP Servo Symbol")
         return

      # Read the number of channel register settings
      numChanRegisters = self.getValueFromServoRam(numChanRegAddress, self.getSymbolViaAddrPrm_11)

      # Fail if we are trying to write more than maxNumChanRegInSAP sets of values
      if numChanTestParms > maxNumChanRegInSAP:
         ScrCmds.raiseException(11044, "TP.setChannelRegisterSettingsInSAP specifies %s registers, but servo SAP only supports %s" % (numChanTestParms,  maxNumChanRegInSAP))

      # If the number of parameters is different than the number of register settings in SAP, update u16_NumberOfChannelRegisterSettingsInSAP
      if numChanRegisters != numChanTestParms:
         write16BitValuesToServoRam['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(numChanRegAddress)
         write16BitValuesToServoRam['WR_DATA'] = numChanTestParms
         self.St(write16BitValuesToServoRam)

      # Get the starting address of ChannelRegisterSettingsInSAP
      chanRegAddress = self.readServoSymbolTable(['START_OF_CHAN_REG_OFFSET',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)

      # Write values to servo RAM. Start at the base address and write address 1, value 1, address 2, value, 2, etc
      write16BitValuesToServoRam['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(chanRegAddress)
      for address, value in regSettings.iteritems():
         write16BitValuesToServoRam['WR_DATA'] = address
         self.St(write16BitValuesToServoRam)

         chanRegAddress += 2
         write16BitValuesToServoRam['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(chanRegAddress)
         write16BitValuesToServoRam['WR_DATA'] = value
         self.St(write16BitValuesToServoRam)

         chanRegAddress += 2
         write16BitValuesToServoRam['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(chanRegAddress)

      # Save SAP to flash (with a reset)
      CFSO().saveSAPtoFLASH()

   def setCertDoneSap(self, enable = True):
      if enable:
         tmpstr = 'en'
         wrData = 0x0800
      else:
         tmpstr = 'dis'
         wrData = 0x0000
      objMsg.printMsg("%sabling Cert Done Bit in Sap..." % tmpstr)
      if self.setServoSymbolData('ZONED_ACFF_SYMBOL_OFFSET', wrData, 0x0800):
         objMsg.printMsg("Cert Done Bit %sabled." % tmpstr)
      else:
        objMsg.printMsg("Cert Done Bit already %sabled." % tmpstr)

   def getOCLIM_byHead(self, oclimSAPOffset, iHead):
      hdCnt = self.dut.imaxHead
      self.St({'test_num':11, 'prm_name': 'getOCLIM_byHead', 'CWORD1': 0x200, 'SYM_OFFSET': oclimSAPOffset, 'NUM_LOCS' : hdCnt - 1})
      oclim_hex = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-hdCnt + iHead]['READ_DATA'],16)
      return oclim_hex

   def getreadOCLIM_allHeads(self, percentTrackScaler = 4096.0):
      readoclimSAPOffset = 105
      oclim_hex = self.getOCLIM_byHead(readoclimSAPOffset, 0)
      OCLIMPercent = float(oclim_hex / percentTrackScaler) * 100
      if DEBUG == 1: objMsg.printMsg('getreadOCLIM_byHead/  All Heads, read  OCLIM: %s' % str(OCLIMPercent))
      return OCLIMPercent

   def getwriteOCLIM_byHead(self, iHead, percentTrackScaler = 4096.0):
      readoclimSAPOffset = 42
      oclim_hex = self.getOCLIM_byHead(readoclimSAPOffset, iHead)
      OCLIMPercent = float(oclim_hex / percentTrackScaler) * 100
      if DEBUG == 1: objMsg.printMsg('getwriteOCLIM_byHead/ iHead: %s, write OCLIM: %s' % (iHead, OCLIMPercent))
      return OCLIMPercent



   def checkOCLlimAllHds(self, percentTrackScaler = 4096.0):
      """
      Check OCLIM on all heads and raise failure if any are over the limit plus
      a margin or error or difference as specified by maxOCLIM.
      """
      if testSwitch.FE_0243459_348085_DUAL_OCLIM_CUSTOMER_CERT == 1:
         finalLim = TP.defaultOCLIM_customer + TP.maxOCLIM
      else:
         finalLim = TP.defaultOCLIM + TP.maxOCLIM
      sapOffset = TP.oclimSAPOffset
      hdCnt = self.dut.imaxHead

      # Read 16bit locations from the SAP--OCLIMs for all heads
      CProcess().St({'test_num':11, 'CWORD1':0x200, 'SYM_OFFSET':sapOffset, 'NUM_LOCS':hdCnt-1,})
      for head in range(self.dut.imaxHead):
         oclimVal = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-hdCnt+head]['READ_DATA'],16)
         oclim = (oclimVal/percentTrackScaler) * 100
         objMsg.printMsg("Head %s OCLIM: %s" % (head,oclim))
         if (not testSwitch.virtualRun) and oclim > finalLim:
            ScrCmds.raiseException(10119,{"data":"OCLIM Verification Failed","EXPECTED":finalLim,"VALUE":oclim})

   def getMaxCylServo(self, forceNewValue = 0):
      """Retrive Max Servo Cylinder"""

      if self.dut.maxServoTrack == None or forceNewValue:
         # Use Test #11 to populate servo ram with PVD FEATURES_2 data.
         self.St(TP.loadPVDFeatures2Prm_11)

         # Use Test #11 to read bit 4 of FEATURES_2 table in VPD.
         self.St(TP.ReadPVDFeatures2Bit4Prm_11)
         bit4 = int(str(self.dut.dblData.Tables('P011_RW_SRVO_RAM_VIA_ADDR').tableDataObj()[-1]['SRVO_DATA']),16)

         # Use Test #11 to get MaxCylinder from servo RAM
         # If V3Bar is supported, the value returned will be the address of MAX_CYL var in servo ram
         # if V3Bar is not supported, the value returned will be the actual MAX_CYL value.
         #
         self.St(TP.getMaxCylPrm_11)
         sMaxCyl = int(str(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA']),16)

         if bit4 & 0x0010:
            # if bit4 of FEATURES_2 table in VPD is set, V3BAR is supported
            objMsg.printMsg("Servo supports V3BAR")
            TP.getMaxCylViaAddrPrm_11["START_ADDRESS"] = self.oUtility.ReturnTestCylWord(sMaxCyl)
            TP.getMaxCylViaAddrPrm_11["END_ADDRESS"] = self.oUtility.ReturnTestCylWord(sMaxCyl)

            self.St(TP.getMaxCylViaAddrPrm_11)
            sMaxCyl = int(str(self.dut.dblData.Tables('P011_RW_SRVO_RAM_VIA_ADDR').tableDataObj()[-1]['SRVO_DATA']),16)

         else:
            objMsg.printMsg("Servo doesn't support V3BAR")

         self.dut.maxServoTrack = sMaxCyl
         return sMaxCyl

   def setMaxCylServo(self, newValue = 0):
      """Set Max Servo Cylinder"""

      if self.dut.maxServoTrack != None and newValue:
         # Use Test #11 to read bit 4 of FEATURES_2 table in VPD.
         self.St(TP.ReadPVDDataPrm_11)
         bit4 = int(str(self.dut.dblData.Tables('P011_RD_SRVO_VPD_VIA_WRD').tableDataObj()[-1]['SRVO_DATA']),16)

         # Use Test #11 to get MaxCylinder from servo RAM
         # If V3Bar is supported, the value returned will be the address of MAX_CYL var in servo ram
         # if V3Bar is not supported, the value returned will be the actual MAX_CYL value.
         #
         self.St(TP.getMaxCylPrm_11)
         sMaxCylAdr = int(str(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA']),16)

         if bit4 & 0x0010:
            # if bit4 of FEATURES_2 table in VPD is set, V3BAR is supported
            objMsg.printMsg("Servo supports V3BAR")
            TP.getMaxCylViaAddrPrm_11["START_ADDRESS"] = self.oUtility.ReturnTestCylWord(sMaxCylAdr)
            TP.getMaxCylViaAddrPrm_11["END_ADDRESS"] = self.oUtility.ReturnTestCylWord(sMaxCylAdr)

            self.St(TP.getMaxCylViaAddrPrm_11)
            sMaxCyl = int(str(self.dut.dblData.Tables('P011_RW_SRVO_RAM_VIA_ADDR').tableDataObj()[-1]['SRVO_DATA']),16)

            self.dut.maxServoTrack = sMaxCyl
            objMsg.printMsg("DBG: Current maxServoTrack % d" % sMaxCyl)
            
            wrSapAddr = dict(self.getSymbolViaAddrPrm_11)
            wrSapAddr['CWORD1'] = 0x100
            wrSapAddr['ACCESS_TYPE'] = 3
            wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(sMaxCylAdr)
            wrSapAddr['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(sMaxCylAdr)
            wrSapAddr['WR_DATA'] = newValue & 0xFFFF #self.oUtility.ReturnTestCylWord(newValue)
            wrSapAddr['EXTENDED_WR_DATA'] = newValue >> 16
               
            wrSapAddr['MASK_VALUE'] = 0x0000
            wrSapAddr['EXTENDED_MASK_VALUE'] = 0x0000
            self.St(wrSapAddr)
            CFSO().saveSAPtoFLASH()
            
            self.St(TP.getMaxCylViaAddrPrm_11)
            sMaxCyl = int(str(self.dut.dblData.Tables('P011_RW_SRVO_RAM_VIA_ADDR').tableDataObj()[-1]['SRVO_DATA']),16)
            self.dut.maxServoTrack = sMaxCyl
            objMsg.printMsg("DBG: New maxServoTrack % d" % sMaxCyl)
            return sMaxCyl
            
         else:
            objMsg.printMsg("Servo doesn't support V3BAR")
            return 0
      else:
         objMsg.printMsg("Max Cylinder not defined")
         return 0

   def getOSTRatio(self, ReadPVDDataPrm_11, getServoSymbolPrm_11, getSymbolViaAddrPrm_11):
      ScrCmds.insertHeader('Set Variable OST')
      MDW_TPI_MULTIPLIER_SHIFT = 2**14
      ostAddress = self.readServoSymbolTable(['ostRatioAddr',],ReadPVDDataPrm_11, getServoSymbolPrm_11, getSymbolViaAddrPrm_11)
      ostValue = self.getValueFromServoRam(ostAddress, getSymbolViaAddrPrm_11) & 0xFFFF #lower word from return
      objMsg.printMsg("Current SAP OST value is %s" % (ostValue,))

      ostValue = MDW_TPI_MULTIPLIER_SHIFT/float(ostValue)
      objMsg.printMsg("Converted OST value is %f" % (ostValue,))
      self.dut.OST = ostValue

      try:
         servoTPI = self.getMdwTPI()
      except:
         if testSwitch.FAIL_FOR_MDW_SN_VOST_UNAVAILABLE or testSwitch.FE_0118821_231166_USE_PGM_LVL_VOST_DEFAULT:
            raise
         else:
            objMsg.printMsg("Unable to retrieve MDW DISC SN. Failure turned off so SAP OST un-touched. Enable FAIL_FOR_MDW_SN_VOST_UNAVAILABLE to fail.")
            return

      self.dut.OST = servoTPI/float(self.dut.arcTPI)
      objMsg.printMsg("Calculated OST Ratio is %s" % (self.dut.OST,))

      sapOST = int(round(MDW_TPI_MULTIPLIER_SHIFT / float(self.dut.OST)))

      objMsg.printMsg("Saving SAP OST Value %s" % (sapOST,))

      wrSapAddr = dict(getSymbolViaAddrPrm_11)
      wrSapAddr['CWORD1'] = 0x002
      wrSapAddr['ACCESS_TYPE'] = 2
      wrSapAddr['START_ADDRESS'] = self.oUtility.ReturnTestCylWord(ostAddress)
      wrSapAddr['END_ADDRESS'] = self.oUtility.ReturnTestCylWord(ostAddress)
      wrSapAddr['WR_DATA'] = sapOST

      self.St(wrSapAddr)


   def getMdwTPI(self):
      mediaCode = DriveAttributes.get('MEDIA_DATE_CODE')
      try:
         if mediaCode:
            #RequestService returns a tuple of len 2 0th item is the function ID an the 1th item is the return value
            vostTuple = RequestService('GetTuple','OST_%s' % mediaCode)[1]
            if DEBUG:
               objMsg.printMsg("GetTuple: 'OST_%s' returned %s" % (mediaCode,vostTuple))
            if vostTuple == None:
               vostTuple = []
         else:
            vostTuple = []
      except:
         objMsg.printMsg("gettuple failed %s: %s" % (vostTuple, traceback.format_exc()))
         vostTuple = []


      mdwSN = DriveAttributes.get('DISC_SERIAL_NUM', None)

      if testSwitch.virtualRun:# or testSwitch.winFOF:
         mdwSN = '16268087ASXW6088204'

      if mdwSN == None:

         from MathLib import mode
         if len(vostTuple) > 0:
            servoTPI = mode(vostTuple)
            return servoTPI

      if mdwSN == None:
         if testSwitch.FE_0118821_231166_USE_PGM_LVL_VOST_DEFAULT:
            if hasattr(TP, 'prm_VOST_Default_TPI'):
               mdwSN = mdwSN = '0'*19
            else:
               ScrCmds.raiseException(14709, 'Retrieval of MDW TPI from FIS and Gemini local DB Failed')
         else:
            ScrCmds.raiseException(14709, 'Retrieval of MDW TPI from FIS and Gemini local DB Failed')

      mdwSN = mdwSN.upper()

      servoTPI = self.convertMDW_Char_To_TPI(mdwSN)

      self.updateOSTTuplespace(vostTuple, mediaCode, servoTPI)

      return servoTPI

   def updateOSTTuplespace(self, vostTuple, mediaCode, servoTPI):
      if mediaCode:
         try:
            #FIFO with element 0 as first
            if len(vostTuple) >= 100:
               del vostTuple[0]

            vostTuple.append(servoTPI)
            try:
               RequestService('PutTuple',('OST_%s' % mediaCode, vostTuple))
            except:
               objMsg.printMsg("Failed to set VOST tuplespace variable. %s" % traceback.format_exc())
         except:
            objMsg.printMsg("Unable to update OST tuplespace... \n%s" % traceback.format_exc())

   def convertMDW_Char_To_TPI(self,mdwSN):
      TPI_SCALE = 1000

      tpiOffset = getattr(TP,'VOST_TPI_OFFSET',150)
      tpiBase = 36
      tpiPick = int(mdwSN[17],tpiBase)
      tpiTableSel = ((int(mdwSN[16],tpiBase)>>2))*tpiBase

      if DEBUG >0 or testSwitch.FE_0118821_231166_USE_PGM_LVL_VOST_DEFAULT:
         objMsg.printMsg("DEBUG Info:\n\ttpiPick:%s\n\ttpiTableSel:%s" % (tpiPick, tpiTableSel))

      sTPI = (tpiPick + tpiTableSel + tpiOffset)* TPI_SCALE#convert to tpi from ktpi
      if testSwitch.FE_0118821_231166_USE_PGM_LVL_VOST_DEFAULT:
         if tpiPick == 0:
            if hasattr(TP, 'prm_VOST_Default_TPI'):
               sTPI = TP.prm_VOST_Default_TPI
               objMsg.printMsg("Using program default servo TPI.")
            else:
               ScrCmds.raiseException(14709, 'Retrieval of MDW TPI from FIS and Gemini local DB and TP.prm_VOST_Default_TPI failed!')

      if testSwitch.FE_0118821_231166_USE_PGM_LVL_VOST_DEFAULT:
         objMsg.printMsg("Servo TPI decoded: %d" % sTPI)

      return sTPI

   def getValueFromServoRam(self, address, getSymbolViaAddrPrm_11):
      tmpParam = dict(getSymbolViaAddrPrm_11)
      tmpParam["START_ADDRESS"] = self.oUtility.ReturnTestCylWord(address)
      tmpParam["END_ADDRESS"] = self.oUtility.ReturnTestCylWord(address)
      tmpParam.update({'DblTablesToParse'   : ['P011_RW_SRVO_RAM_VIA_ADDR']})

      self.St(tmpParam)
      if not testSwitch.virtualRun:
         return int(str(self.dut.objSeq.SuprsDblObject['P011_RW_SRVO_RAM_VIA_ADDR'][-1]['SRVO_DATA']),16)
      else:
         return int(str(self.dut.dblData.Tables('P011_RW_SRVO_RAM_VIA_ADDR').tableDataObj()[-1]['SRVO_DATA']),16)

   def readServoSymbolTable(self, symbolType, ReadPVDDataPrm_11, getServoSymbolPrm_11, getSymbolViaAddrPrm_11):
      """Read the servo symbol table."""

      # Use Test #11 to read bit 4 of FEATURES_2 table in VPD.
      if 'maxServoTrack' in symbolType:
         ReadPVDDataPrm_11.update({'DblTablesToParse'   : ['P011_RD_SRVO_VPD_VIA_WRD']})
         self.St(ReadPVDDataPrm_11)
         if not testSwitch.virtualRun:
            bit4 = int(str(self.dut.objSeq.SuprsDblObject['P011_RD_SRVO_VPD_VIA_WRD'][-1]['SRVO_DATA']),16)
         else:
            bit4 = int(str(self.dut.dblData.Tables('P011_RD_SRVO_VPD_VIA_WRD').tableDataObj()[-1]['SRVO_DATA']),16)
      else:
         bit4 = 0
         
      # Use Test #11 to get symbol offset value from servo RAM
      # FOR SYMOFFSET 2 ONLY:  If V3Bar is supported, the value returned will be the address of MAX_CYL var in servo ram
      # if V3Bar is not supported, the value returned will be the actual MAX_CYL value.
      #
      if testSwitch.virtualRun:
         SVRAMTbl = self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()
         
      symOffValue = []
      for type in symbolType:
         prm = getServoSymbolPrm_11['base']
         prm['SYM_OFFSET'] = getServoSymbolPrm_11['SYM_OFFSET'][type]
         prm.update({'DblTablesToParse'   : ['P011_SV_RAM_RD_BY_OFFSET']})
         if testSwitch.virtualRun:
            #objMsg.printMsg("prm_SYM_OFFSET = %d, type = %s" % (prm['SYM_OFFSET'],type))
            for entry in SVRAMTbl:
                vxml_SymOff = int(entry.get('SYM_OFFSET'))
                #objMsg.printMsg("xml_Stmofs = %d" % vxml_SymOff)
                if prm['SYM_OFFSET'] == vxml_SymOff:
                   vxml_data = entry.get('READ_DATA')
                   #objMsg.printMsg("RD_DATA = %s" % vxml_data)
                   symOffValue.append(int(vxml_data,16))
         else:
            self.St(prm)
            symOffValue.append(int(str(self.dut.objSeq.SuprsDblObject['P011_SV_RAM_RD_BY_OFFSET'][-1]['READ_DATA']),16))
            
         if bit4 & 0x0010 and prm['SYM_OFFSET'] == 2:
            # if bit4 of FEATURES_2 table in VPD is set, V3BAR is supported.  If we are trying to find maxCyl then symOffValue is an address
            objMsg.printMsg("Address returned from symbol table.  Read address now.")
            symOffValue[-1] = self.getValueFromServoRam(symOffValue[-1], getSymbolViaAddrPrm_11)

         objMsg.printMsg("Servo Symbol Table => %s = %s" % (type, symOffValue[-1]))

      if len(symOffValue) == 1:
         symOffValue = symOffValue[0] #if only one variable is passed in return int. instead of list

      return symOffValue

   def setSpinSpeed(self, inPrm):
      self.St(inPrm)

   def enableAutoSpin(self):
      """enable auto spin"""
      self.St({'test_num':11,'prm_name':"Enable auto spin",'timeout': 120, 'SYM_OFFSET': [101], 'MASK_VALUE': 0xBFFF, 'CWORD1': [1024], 'spc_id': 1, 'WR_DATA': 0, 'NUM_LOCS': 0})

   def disableAutoSpin(self):
      """disable auto spin"""
      self.St({'test_num':11,'prm_name':"Disable auto spin",'timeout': 120, 'SYM_OFFSET': [101], 'MASK_VALUE': 0xBFFF, 'CWORD1': [1024], 'spc_id': 1, 'WR_DATA': 0x4000, 'NUM_LOCS': 0})

   def UpdateNotchCoeff (self):
      prm_152 = {'test_num': 152,
                 'prm_name': 'Update 2-disc Notch Coeff Table in servo ram',
                 'timeout' : 1800,
                 'dlfile'  : (CN, PackageDispatcher(self.dut, 'COE').getFileName()),
                 'spc_id'  : 1,
                 'CWORD1'   : 0x0080,
                 }
      self.St(prm_152)

   def getServoChipID(self, ):
      RegStr = '0'
      if testSwitch.virtualRun:
         bit16mode = 1
         bit8mode = 1
      else:
         bit16mode = 1
         bit8mode = 0
         self.St({'test_num':11,'prm_name':'getServoChipID_16_Reg7F','PARAM_0_4':[0x126f, 0, 127, 0, 0] }) # servocmd, Param_0: 0x126F, 16bitRead; Param_2: 127, Reg7F

         tableName = 'P011_DO_SERVO_CMD'

         try:
            RegVal = int(str(self.dut.dblData.Tables(tableName).tableDataObj()[-1]['DIAG_HEX']),16)
         except CDblogDataMissing:
            #New table
            if testSwitch.BF_0163578_231166_P_FIX_DO_SERVO_CMD10_USAGE:
               tableName = 'P011_DO_SERVO_CMD10'
            else:
               raise

            RegVal = int(str(self.dut.dblData.Tables(tableName).tableDataObj()[-1]['DIAG_HEX']),16)

         RegStr = '0x%04X'%RegVal

         if RegVal & (0x00FF) == 0:
            bit16mode = 0
            bit8mode = 1
            self.St({'test_num':11,'prm_name':'getServoChipID_8_Reg7E','PARAM_0_4':[0x106f, 0, 126, 0, 0] }) # servocmd, Param_0: 0x106F, 8bitRead; Param_2: 126, Reg7E
            RegVal = int(str(self.dut.dblData.Tables(tableName).tableDataObj()[-1]['DIAG_HEX']),16)
            RegStr = '0x%02X'%RegVal

      if bit8mode == 1:
         if testSwitch.virtualRun:
            RegVal = 0x04
            RegStr = '0x%02X'%RegVal
         RegVal = RegVal & (0xC0)
         if RegVal == 0:
            SvoChipMfr = 'ST'
         elif RegVal == 0x80:
            SvoChipMfr = 'TI'
         else:
            SvoChipMfr = 'NA'
         bit8Str = SvoChipMfr + '_' + RegStr

      if bit16mode == 1:
         if testSwitch.virtualRun:
            RegVal = 0x0400
            RegStr = '0x%04X'%RegVal
         RegVal = RegVal & (0x0C00)
         if RegVal == 0:
            SvoChipMfr = 'ST'
         elif RegVal == 0x0400:
            SvoChipMfr = 'TI'
         else:
            SvoChipMfr = 'NA'
         bit16Str = SvoChipMfr + '_' + RegStr

      if testSwitch.BF_0147585_426568_P_FIX_SRVO_CNTRLR_ID_SPELLING:
         if testSwitch.virtualRun:
            self.dut.driveattr['SRVO_CNTRLR_ID'] = bit16Str + '_' + bit8Str + '_VirtualRun'
         else:
            self.dut.driveattr['SRVO_CNTRLR_ID'] = SvoChipMfr + '_' + RegStr
      else:
         if testSwitch.virtualRun:
            self.dut.driveattr['SRVO_CNTRLER_ID'] = bit16Str + '_' + bit8Str + '_VirtualRun'
         else:
            self.dut.driveattr['SRVO_CNTRLER_ID'] = SvoChipMfr + '_' + RegStr


   def polyZapEnabled(self):
      # Determine if poly zap is enabled
      try:
         i32RroPolyAddr = self.readServoSymbolTable(['I32_RRO_POLY',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)
      except:
         return 0

      if (i32RroPolyAddr & 0x0000FFFF) != 0xFFFF:
         return 1
      else:
         return 0   # illegal addr ( means not poly zap )


   def polyZapResultsInSAP(self):
      polyZapAddr = self.readServoSymbolTable(['U16_SAP_MISC_FLAGS',],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)
      resultsInSAP = self.getValueFromServoRam(polyZapAddr, self.getSymbolViaAddrPrm_11)
      if resultsInSAP & 0x1000:
         return 1
      return 0

   def ChangeServoChannelSetting(self, mode):
      if testSwitch.FE_0329412_340866_STRESS_CHANNEL_DURING_FLAW_SCAN:
         value = self.getServoSymbolData('STRESS_CHANNEL_IN_FLAW_SCAN', 0xFFFF)
         if value != 0xFFFF:
            self.setServoSymbolData('STRESS_CHANNEL_IN_FLAW_SCAN', mode, 0x0001) # change servo channel setting
            self.getServoSymbolData('STRESS_CHANNEL_IN_FLAW_SCAN', 0xFFFF)

   def get_TIMINGCOEFF_addr(self):
      return self.readServoSymbolTable(['RADIALTIMINGCOEFF_PRE2'],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)
   
   def get_TIMINGCOEFF1_addr(self):
      return self.readServoSymbolTable(['RADIALTIMINGCOEFF_CRT2'],self.ReadPVDDataPrm_11, self.getServoSymbolPrm_11, self.getSymbolViaAddrPrm_11)
   
   def fetch_TIMINGCOEFF_16(self, head):
      coeff_addr = self.get_TIMINGCOEFF_addr()
      coeff1_addr = self.get_TIMINGCOEFF1_addr()
      read16bitprm = self.getSymbolViaAddrPrm_11
      read16bitprm['ACCESS_TYPE'] = 2
      read16bitprm['EXTENDED_MASK_VALUE'] = 65535
      coeff_byte8 = self.getValueFromServoRam(coeff_addr +(8*(head+1)-1)*2, read16bitprm)
      coeff1_byte8 = self.getValueFromServoRam(coeff1_addr +(8*(head+1)-1)*2, read16bitprm)

      return coeff_byte8, coeff1_byte8

class CServoOpti(CServoFunc):
   """
   cServoOpti.py
   Description:   Holds optimization output variables and functions for the
                  calibration and optimizatio of the servo system
   """

   def __init__(self):
      CServoFunc.__init__(self)


   def doSNO(self,inPrm,notches):
      """Perform Servo Notch Optimization (SNO).
      inPrm:     A base parameter set which gets submitted to the SNO test.
      notches:   A list of parameter subsets to specify a particular notch and
                 frequency range to be used in each iteration of SNO invokation.
      Algorithm: The SNO test is invoked once for each notch listed in the
                 notches parameter.  Test parameters that are common to each
                 invokation of the SNO test are defined by the inPrm parameter.
      """
      for notch in notches:
         tmpDict = {}
         tmpDict.update(inPrm)
         tmpDict.update(notch)
         rangeOK, tmpDict['HEAD_RANGE'] = self.snoHdRngChk(tmpDict['HEAD_RANGE'])
         if rangeOK:
            try:
               self.St(tmpDict)
            except ScriptTestFailure, (failuredata):
               if not failuredata[0][2] in [10137]:
                  raise

   def snoHdRngChk(self,hdRange):
      """Perform range check on HEAD_RANGE parameter.
      Truncates range if outside existing heads
      """
      if (hdRange == 0xFFFF) or (hdRange == 0x00FF) or ((hdRange & 0x00FF) < self.dut.imaxHead):
         return 1,hdRange
      if ((hdRange & 0xFF00) >> 8) < self.dut.imaxHead:
         return 1,(hdRange & 0xFF00) + (self.dut.imaxHead - 1)
      else:
         return 0,hdRange

   def servoLinCal(self,inPrm, inPrm1, runReal = 1, sampling = 0):
      """Produce a cross track linearity table for the Servo System."""
      if runReal == 1:
         self.St(TP.spinupPrm_1)
         self.St(TP.vCatGoRealPrm_47)
         try:
            self.St(inPrm) #Servo Linearization
         except:
            if objRimType.IsHDSTRRiser():
               try:
                  objMsg.printMsg('Retry by PowerCycle() with ESlip for fixing EC11049 SP HDSTR')
                  time.sleep(60)
                  objPwrCtrl.powerCycle()
                  self.St(inPrm) #Servo Linearization
               except:
                  objMsg.printMsg('Retry again by PowerCycle() with ESlip for fixing EC11049 SP HDSTR')
                  time.sleep(60)
                  objPwrCtrl.powerCycle()
                  self.St(inPrm) #Servo Linearization
            else: raise
         if (sampling and self.dut.serialnum[-1] in ConfigVars[CN].get('DataCollectionMode', map(str, xrange(7)))) or \
            sampling == 0: # 0-6
            if testSwitch.FE_0338894_357001_T257_TEST_BY_DISC:
               for head in range(0,self.dut.imaxHead,2):
                  inPrm1['HEAD_RANGE'] =  (head<<8) + head  
                  self.St(inPrm1) #CRRO,IRRO data collection
            else:       
               self.St(inPrm1) #CRRO,IRRO data collection

         if not testSwitch.FE_0112728_357260_RUN_T193_IN_REAL_MODE:
            self.St(TP.vCatGoVirtualPrm_47)
      else:
         try:
            self.St(inPrm) #Servo Linearization
         except:
            if objRimType.IsHDSTRRiser():
               try:
                  objMsg.printMsg('Retry by PowerCycle() with ESlip for fixing EC11049 SP HDSTR')
                  time.sleep(60)
                  objPwrCtrl.powerCycle()
                  self.St(inPrm) #Servo Linearization
               except:
                  objMsg.printMsg('Retry again by PowerCycle() with ESlip for fixing EC11049 SP HDSTR')
                  time.sleep(60)
                  objPwrCtrl.powerCycle()
                  self.St(inPrm) #Servo Linearization
            else: raise


   #########################################################################################
   #
   #               Function:  servoLinCal_AFH
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  run Servo Linearization cal between test 135 AFH heater settings.
   #                          Legacy comments: """Produce a cross track linearity table for the Servo System."""
   #
   #
   #                  Input:
   #
   #           Return Value:
   #
   #########################################################################################

   def servoLinCal_AFH(self,Prm_150, iHead):

      Prm_150['HEAD_RANGE'] = 1 << iHead

      self.St(TP.vCatGoRealNoSAPPrm_47)
      self.St(Prm_150) #Servo Linearization
      self.St(TP.vCatOn_47)
      self.St(TP.enableHiBWController_Dual_AFH)

      # end of servoLinCal_AFH




   #requested by SP servo group
   def EnableAntiNotch(self,inPrm):
      """Enable Anti Notch."""
      self.St(inPrm) #Anti Notch mode



   def genDelayHeaders(self):
      delayHeader = 'DELAY_%s'
      CFSO().getZoneTable()

      #return the 'names' of the files but use a physical head reference for the logical heads populated
      return [delayHeader % str(self.dut.LgcToPhysHdMap[i]) for i in range(self.dut.imaxHead)]

   def retrieveRWGapData(self, zapFromDut = 1):
      oFSO = CFSO()
      ######################################
      #  Retrieve delay results from the system area (ETF) of the drive under test
      ######################################
      if zapFromDut == 0:
         ScrCmds.raiseException(11044, "Drive RW Gap SIM Data disabled by zapFromDut = 0")
      for name in self.genDelayHeaders():

         record = objSimArea[name]
         rwGapPath = os.path.join(ScrCmds.getSystemPCPath(), record.name,oFSO.getFofFileName(0))
         if not os.path.exists(rwGapPath):
            path = oFSO.retrieveHDResultsFile(record)
            FileName = open(path,'rb')
            try:
               FileName.seek(0,2)  # Seek to the end
               FileLength = FileName.tell()
            finally:
               FileName.close()
            objMsg.printMsg("Re-Read of drive SIM File %s had size %d" % (record.name,FileLength), objMsg.CMessLvl.DEBUG)
            if FileLength == 0:
               ScrCmds.raiseException(11044, "Drive RW Gap SIM Data readback of 0 size.")

   ######################################

   def saveRWGapData(self):
      oFSO = CFSO()
      ######################################
      #  Save All delay results to the system area (ETF) of the drive under test
      ######################################
      for name in self.genDelayHeaders():
         record = objSimArea[name]
         rwGapPath = os.path.join(ScrCmds.getSystemPCPath(), record.name,oFSO.getFofFileName(0))
         if os.path.exists(rwGapPath):
            #Write data to drive SIM
            objMsg.printMsg("Saving CM PC File %s to drive SIM" % record.name, objMsg.CMessLvl.DEBUG)
            oFSO.saveResultsFileToDrive(1,rwGapPath,0,record,1)
            #Verify data on drive SIM
            path = oFSO.retrieveHDResultsFile(record)
            FileName = open(path,'rb')
            try:
               FileName.seek(0,2)  # Seek to the end
               FileLength = FileName.tell()
            finally:
               FileName.close()
            objMsg.printMsg("Re-Read of drive SIM File %s had size %d" % (record.name,FileLength), objMsg.CMessLvl.DEBUG)
            if FileLength == 0:
               ScrCmds.raiseException(11044, "Drive RW Gap SIM Data readback of 0 size.")
      ######################################


   def genXferHeaders(self, head_range = 0xFF):
      xferHeader = 'xfrfnc_%s'
      CFSO().getZoneTable()
      if type(head_range) != int:
         starthead = head_range[0] >> 8
         endhead = head_range[0] & 0xFF
      else:
         starthead = head_range >> 8
         endhead = head_range & 0xFF
      if endhead >= self.dut.imaxHead:
         endhead = self.dut.imaxHead - 1
      return [xferHeader % str(self.dut.LgcToPhysHdMap[i]) for i in range(starthead, endhead + 1)]

   def chromeCal(self, inPrm):

      modVal = self.setZonedACFF(enable=False)
      modLVFF = self.setLVFF(enable=False)
      try:
         self.St(inPrm)
      except:
         if objRimType.IsHDSTRRiser():
            try:
               objMsg.printMsg('Retry by PowerCycle() with ESlip for fixing EC11049 SP HDSTR')
               time.sleep(60)
               objPwrCtrl.powerCycle()
               inPrm['timeout'] = inPrm['timeout']*2
               self.St(inPrm)
               inPrm['timeout'] = inPrm['timeout']/2
            except:
               objMsg.printMsg('Retry again by PowerCycle()with ESlip for fixing EC11049 SP HDSTR')
               time.sleep(60)
               objPwrCtrl.powerCycle()
               inPrm['timeout'] = inPrm['timeout']*2
               self.St(inPrm)
               inPrm['timeout'] = inPrm['timeout']/2
         else: raise
      if testSwitch.FE_0112728_357260_RUN_T193_IN_REAL_MODE:
         try:
            self.St(TP.vCatGoVirtualPrm_47)
         except:
            if objRimType.IsHDSTRRiser():
               try:
                  objMsg.printMsg('Retry by PowerCycle() with ESlip for fixing EC11049 SP HDSTR')
                  sleep(60)
                  objPwrCtrl.powerCycle()
                  inPrm['timeout'] = inPrm['timeout']*2
                  self.St(TP.vCatGoVirtualPrm_47)
                  inPrm['timeout'] = inPrm['timeout']/2
               except:
                  objMsg.printMsg('Retry again by PowerCycle()with ESlip for fixing EC11049 SP HDSTR')
                  sleep(60)
                  objPwrCtrl.powerCycle()
                  inPrm['timeout'] = inPrm['timeout']*2
                  self.St(TP.vCatGoVirtualPrm_47)
                  inPrm['timeout'] = inPrm['timeout']/2
            else: raise

      if modVal:
         self.setZonedACFF(enable = True)
      if modLVFF:
         self.setLVFF(enable = True)

   def zap(self, inPrm, zapFromDut = 1, consolidateOffLVFF_ACFF = 0):
      """Reduce repeatable runout to a specified level for all tracks"""
      execPrm = self.oUtility.copy(inPrm)
      hdstrProc = self.dut.HDSTR_RECORD_ACTIVE == 'Y'

      if testSwitch.ZFS:
         if type(execPrm.get('CWORD1',0x0000)) in [types.ListType,types.TupleType]:
            execPrm['CWORD1'] = execPrm['CWORD1'][0]
      else:
         if type(execPrm.get('CWORD2',0x0000)) in [types.ListType,types.TupleType]:
            execPrm['CWORD2'] = execPrm['CWORD2'][0]

      gapOnDisc = False
      if not hdstrProc and not testSwitch.SMR:
         try:
            self.retrieveRWGapData(zapFromDut)
            gapOnDisc = True
         except:
            objMsg.printMsg(traceback.format_exc())


      if testSwitch.ROSEWOOD7 or testSwitch.M11P_BRING_UP or testSwitch.M11P:
         if testSwitch.ZFS:
            #Gap data is on the drive sim so pull from there.
            execPrm['CWORD1'] = execPrm.get('CWORD1',0) | 0x0008
            execPrm['CWORD1'] = execPrm.get('CWORD1',0) & 0xFFFB
         else:
            #Gap data is on the drive sim so pull from there.
            execPrm['CWORD2'] = execPrm.get('CWORD2',0) | 0x0008
            execPrm['CWORD2'] = execPrm.get('CWORD2',0) & 0xFFEF
      else:
         if gapOnDisc or hdstrProc:
            if testSwitch.ZFS:
               #Gap data is on the drive sim so pull from there.
               execPrm['CWORD1'] = execPrm.get('CWORD1',0) | 0x0008
               execPrm['CWORD1'] = execPrm.get('CWORD1',0) & 0xFFFB
            else:
               #Gap data is on the drive sim so pull from there.
               execPrm['CWORD2'] = execPrm.get('CWORD2',0) | 0x0008
               execPrm['CWORD2'] = execPrm.get('CWORD2',0) & 0xFFEF

         if not gapOnDisc and not hdstrProc:
            if testSwitch.ZFS:
               #Gap data is not on the disc so let's save it to the pcfile
               execPrm['CWORD1'] = execPrm.get('CWORD1',0) | 0x0004
               execPrm['CWORD1'] = execPrm.get('CWORD1',0) & 0xFFF7
            else:
               #Gap data is not on the disc so let's save it to the pcfile
               execPrm['CWORD2'] = execPrm.get('CWORD2',0) | 0x0010
               execPrm['CWORD2'] = execPrm.get('CWORD2',0) & 0xFFF7

      if testSwitch.WA_SGP_DISABLE_USING_SRV_DATA_ON_DISC:
         xferOnCM = False
      else:
         xferOnCM = True

      for header in self.genXferHeaders(head_range = execPrm.get('HEAD_RANGE', 0xFF)):
         XFerFuncPath = os.path.join(ScrCmds.getSystemPCPath(), header ,CFSO().getFofFileName(0))
         xferOnCM = xferOnCM  and os.path.exists(XFerFuncPath)

      # xfer function file isn't on the HDA yet so we can't redirect the file stream for ST240
      #   *not sure if we should incase the xfer function is that much different in the ST240
      if not hdstrProc:
         if xferOnCM:
            if testSwitch.ZFS:
               execPrm['CWORD1'] = execPrm.get('CWORD1',0) | 0x0020
               execPrm['CWORD1'] = execPrm.get('CWORD1',0) & 0xFFEF
            else:
               execPrm['CWORD2'] = execPrm.get('CWORD2',0) | 0x0002
               execPrm['CWORD2'] = execPrm.get('CWORD2',0) & 0xFFFB
         else:
            if testSwitch.ZFS:
               execPrm['CWORD1'] = execPrm.get('CWORD1',0) | 0x0010
               execPrm['CWORD1'] = execPrm.get('CWORD1',0) & 0xFFDF
            else:
               execPrm['CWORD2'] = execPrm.get('CWORD2',0) | 0x0004
               execPrm['CWORD2'] = execPrm.get('CWORD2',0) & 0xFFFD
      else:
         if testSwitch.ZFS:
            execPrm['CWORD1'] = execPrm.get('CWORD1',0) & 0xFFCF
         else:
            execPrm['CWORD2'] = execPrm.get('CWORD2',0) & 0xFFFD & 0xFFFB
      
      # T275 handles LVFF and ZonedACFF enabling/disabling so no need to do it here
      if testSwitch.ZFS == 0:    
         if not consolidateOffLVFF_ACFF:
            modVal = self.setZonedACFF(enable=False)
            if not testSwitch.FE_0227602_336764_P_REDUCE_T11_TEST_LOOP_FOR_LA_CM_REDUCTION:
                modLVFF = self.setLVFF(enable=False)

      try: stats = self.St(execPrm) # ZAP
      except ScriptTestFailure, (failureData):
         ec = failureData[0][2]
         if ec == 10264:
            #Turn off all save options if incompatable
            if testSwitch.ZFS:
               execPrm['CWORD1'] = execPrm.get('CWORD1',0) & 0xFFC3
            else:
               execPrm['CWORD2'] = execPrm.get('CWORD2',0) & 0xFFE1
            self.St(execPrm)
         else: raise
      
      # T275 handles LVFF and ZonedACFF enabling/disabling so no need to do it here
      if testSwitch.ZFS == 0:    
         if not consolidateOffLVFF_ACFF:
            if modVal:
               self.setZonedACFF(enable = True)
            if not testSwitch.FE_0227602_336764_P_REDUCE_T11_TEST_LOOP_FOR_LA_CM_REDUCTION:
                if modLVFF:
                  self.setLVFF(enable = True)

   def bodeSensitivityScoring(self,sensPrm,sensMargins):
      """ sensitivity scoring algorithm -uses CL bode, test 152
       DOCs on TPE Wiki page-->
       http://col-tpecvs-01.am.ad.seagate.com/wiki/index.php/Bode_Sensitivity_Scoring
      """

      # In order to use the T282 Sensitivity Scoring method, which generates P152_BODE_SENSITIVE_SCORE
      # in SF3 FW, the OracleTables definitions MUST NOT contain the table definition, so it was removed.
      # If this Sensitivity Scoring method is used, the table must be added to OracleTables before we
      # attempt to add data to the table (below).  In addition, the table key must be added to the
      # processTableOverrides list, so the data will go to Oracle.  Though this implementation is a bit
      # unusual, it is necessary in order to support both Sensitivity Scoring methods (SF3 & PF3 based).
      import DbLogAlias
      from DBLogDefs import DbLogColumn
      DbLogAlias.DbLogTableDefinitions.OracleTables.update({
         'P152_BODE_SENSITIVE_SCORE':
         {
            'type': 'M',
            'fieldList': [
               DbLogColumn('HD_PHYS_PSN', 'N'),
               DbLogColumn('TRK_NUM', 'N'),
               DbLogColumn('SPC_ID', 'V'),
               DbLogColumn('OCCURRENCE', 'N'),
               DbLogColumn('SEQ', 'N'),
               DbLogColumn('TEST_SEQ_EVENT', 'N'),
               DbLogColumn('HD_LGC_PSN', 'N'),
               DbLogColumn('BODE_SENSITIVITY_FREQ', 'N'),
               DbLogColumn('BODE_SENSITIVITY_SCORE', 'N'),
               DbLogColumn('BODE_SENSITIVITY_LIMIT', 'N'),
               DbLogColumn('MARGIN_NUM', 'N'),
               DbLogColumn('BODE_SENSITIVITY_HEALTH', 'N'),
            ]
         },
      })
      DbLogAlias.processTableOverrides.extend('P152_BODE_SENSITIVE_SCORE')

      bodeSensScoringPrm_152  = self.oUtility.copy(sensPrm)
      prm_bodeSensScoringMargins = self.oUtility.copy(sensMargins)
      ######################## DBLOG Implementaion- Setup
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

      self.format_startTime = time()
      #########################
      if testSwitch.virtualRun:
         worstScoreHead = worstScoreTrk = worstScoreMargin = worstScoreFreq = 0
         worstScore = worstScoreLimit = minorHealth = 0.0
      freqStart = prm_bodeSensScoringMargins.get('SensitivityScoringFreqStart')
      freqStop = prm_bodeSensScoringMargins.get('SensitivityScoringFreqStop')
      gainStartIndex = prm_bodeSensScoringMargins.get('SensitivityScoringGainStartIndex')
      numMargins = prm_bodeSensScoringMargins.get('SensitivityScoringNumMargins')
      numGainPoints = prm_bodeSensScoringMargins.get('SensitivityScoringNumGainPoints')
      gainTrace = prm_bodeSensScoringMargins.get('SensitivityScoringCombinedGainTrace')
      minorHealthTH = prm_bodeSensScoringMargins.get('SensitivityScoringMinorHealthThreshold')
      for head in range(self.dut.imaxHead):
         hdMsk = (head << 8) + head
         bodeSensScoringPrm_152["HEAD_RANGE"] = (hdMsk)
         testLoc=[1,2,3] #loc0=5%, loc1=50%, loc2=95% of stroke
         maxCyl = self.dut.maxTrack[head]
         cylDelta = int(maxCyl * 0.05)
         for testposn in range(len(testLoc)):
            if testposn == 0 : testCyl = cylDelta
            if testposn == 1 : testCyl = maxCyl / 2
            if testposn == 2 : testCyl = maxCyl - cylDelta
            cylUpperWord,CylLowerWord = self.oUtility.ReturnTestCylWord(testCyl)
            bodeSensScoringPrm_152["START_CYL"] = cylUpperWord,CylLowerWord
            bodeSensScoringPrm_152["END_CYL"] = cylUpperWord,CylLowerWord
            bodeSensScoringPrm_152['FREQ_INCR'] = int(round(float(freqStop[numMargins-1] - freqStart[0]) /  float(numGainPoints)))
            bodeSensScoringPrm_152['FREQ_RANGE'] = (freqStart[0],(freqStop[numMargins-1]+ bodeSensScoringPrm_152['FREQ_INCR']* (numMargins-1)))#blm -take enuf data to handle (1 x-tra msmt per margin gap)
            if int(bodeSensScoringPrm_152['FREQ_RANGE'][1] > int((self.dut.rpm/60)* self.dut.servoWedges)): #invalid T250 parm if go past sample rate
               bodeSensScoringPrm_152['FREQ_RANGE'] = (freqStart[0],freqStop[numMargins-1])# go back to orig test parms freqStop
            if int((bodeSensScoringPrm_152['FREQ_RANGE'][1]-bodeSensScoringPrm_152['FREQ_RANGE'][0])/bodeSensScoringPrm_152['FREQ_INCR']) < (numGainPoints+(numMargins-1)): #make sure you always have enough msmt data including for the margin gaps
               bodeSensScoringPrm_152['FREQ_INCR'] = int(round(float(freqStop[numMargins-1] - freqStart[0]) /  float(numGainPoints)))-1 #decrease freq step size by 1 to get the num msmts raised
            bodeSensScoringPrm_152['DblTablesToParse'] = ['P152_BODE_GAIN_ONLY',]
            bodeSensScoringPrm_152['stSuppressResults'] = ST_SUPPRESS__ALL | ST_SUPPRESS_RECOVER_LOG_ON_FAILURE
############ do msmt
            try:
               self.St(bodeSensScoringPrm_152)
            except:
               if objRimType.IsHDSTRRiser():
                  try:
                     objMsg.printMsg('Retry by PowerCycle() with ESlip for fixing EC11049 SP HDSTR')
                     sleep(60)
                     objPwrCtrl.powerCycle()
                     self.St(bodeSensScoringPrm_152)
                  except:
                     objMsg.printMsg('Retry again by PowerCycle()with ESlip for fixing EC11049 SP HDSTR')
                     sleep(60)
                     objPwrCtrl.powerCycle()
                     self.St(bodeSensScoringPrm_152)
               else: raise
############ get table
            if testSwitch.virtualRun:
               #VE doesn't have isoparse data
               bodeMsmtTable = self.dut.dblData.Tables('P152_BODE_GAIN_ONLY').tableDataObj()
            else:
               bodeMsmtTable = self.oUtility.copy(self.dut.objSeq.SuprsDblObject['P152_BODE_GAIN_ONLY'])
            self.dut.objSeq.SuprsDblObject = {} #Clear the caller's object so when we exit the loop there are only local refs left to clean up

            for margin in range(numMargins):
               worstScore = 50 #set high to make sure
               fGap = 0
               fGapAdder = 0
               if (margin +1) == numMargins:
                  numMarginGainPts = numGainPoints - gainStartIndex[margin]
               else:
                  numMarginGainPts = gainStartIndex[margin+1] - gainStartIndex[margin]
               if ((margin +1) == numMargins) | (margin == 0) :
                  fGap = 0
               else: # if gaps between margins are > normal step size..you gotta deal with it
                  fGap = int(round(float(freqStart[margin+1] - freqStop[margin]) / float(bodeSensScoringPrm_152['FREQ_INCR'])))
               if fGap >=2: fGapAdder = fGap-1
               for point in xrange(numMarginGainPts):
                  gainDelta = gainTrace[gainStartIndex[margin] + point]/2048.0 \
                   - float(bodeMsmtTable[gainStartIndex[margin] + fGapAdder + point]['GAIN'])

                  if gainDelta < worstScore :
                     worstScoreHead = head
                     worstScoreTrk = testCyl
                     worstScoreMargin = margin + 1
                     worstScore = gainDelta
                     worstScoreFreq = int(bodeMsmtTable[gainStartIndex[margin] + point]['FREQUENCY'])
                     worstScoreLimit = gainTrace[gainStartIndex[margin] + point]/2048.0
               minorHealth = worstScore - (float(minorHealthTH[margin]) / 10.0)
               objMsg.printMsg('worst VALUES for each margin...head/track/margin/score/Freq/Limit/minorHealthScore ARE : %s \t%s \t%s \t%s \t%s \t%s \t%s' % \
                               (worstScoreHead,worstScoreTrk,worstScoreMargin,str(worstScore),worstScoreFreq,str(worstScoreLimit),str(minorHealth)),objMsg.CMessLvl.IMPORTANT)
               worstScore = self.oUtility.setDBPrecision(worstScore,5,3)
               worstScoreLimit = self.oUtility.setDBPrecision(worstScoreLimit,5,3)
               minorHealth = self.oUtility.setDBPrecision(minorHealth,5,3)
##### dblog init for each hd/zone/margin result ######################################
               self.dut.dblData.Tables('P152_BODE_SENSITIVE_SCORE').addRecord(
                         {
                         'HD_PHYS_PSN': self.dut.LgcToPhysHdMap[head],
                         'TRK_NUM': worstScoreTrk,
                         'SPC_ID': 1,
                         'OCCURRENCE': occurrence,
                         'SEQ': curSeq,
                         'TEST_SEQ_EVENT': testSeqEvent,
                         'HD_LGC_PSN': head,
                         'BODE_SENSITIVITY_FREQ':worstScoreFreq,
                         'BODE_SENSITIVITY_SCORE':worstScore,
                         'BODE_SENSITIVITY_LIMIT':worstScoreLimit,
                         'MARGIN_NUM':worstScoreMargin,
                         'BODE_SENSITIVITY_HEALTH':minorHealth,
                         })

      if testSwitch.FE_0129672_357260_DISPLAY_P152_BODE_SENSITIVE_SCORE_IN_LOG:
         objMsg.printDblogBin(self.dut.dblData.Tables('P152_BODE_SENSITIVE_SCORE'))

   def T37RPSDefaultDownload(self):
      """
      T37 RPS download. this option of calling test 37 pulls (from the host) the default RPS file (from the seek profile generated by servo)
      and downloads it to the ETF log. The bin RPS file for the proper mech config must be in the
      dlfile dir in the CMS system for the config. Purpose of this is to get a reasonable SP table on disk until
      T37 cal is tuned so that it can be run on individual units.
      future:control the default files by rev and have servo include in the release package (revs to match servo rls rev nums)
      """
      oFSO = CFSO()
      RPSFilename = PackageDispatcher(self.dut, 'RPS').getFileName()
      objMsg.printMsg("here is the RPS filename: %s" % RPSFilename)# blm

      try:
         filePath = ScrCmds.getSystemDnldPath() + os.sep + RPSFilename
         oFSO.request21File = open(filePath, 'r')
      except:
         objMsg.printMsg('RPS file not in dlfile directory', objMsg.CMessLvl.CRITICAL)
         objMsg.printMsg('default RPS file NOT DOWNLOADED TO ETF LOG, performance will suffer', objMsg.CMessLvl.CRITICAL)
         return -1

      RegisterResultsCallback(oFSO.processRequest21,[21],useCMLogic=0)# Re-direct 21 calls

      self.St({'test_num':37,'prm_name':"test37DefaultRPStoETFLog", 'CWORD1': 5}) #DL file from host and save to ETF
      RegisterResultsCallback('', 21,) # Resume normal 21 calls
      oFSO.request21File.close()

   def accousticMode(self, inPrm):
      """AccousticSeek"""
      self.St(inPrm) # accousticMode

   def zgsTest(self,inPrm):
       """ZGS Test"""
       self.St(inPrm) #zgs

class CServoScreen(CServo):
   """
   CServoScreen
   Description:   Holds servo performance and functionality screen functions.
   """
   def __init__(self):
      CServo.__init__(self)

   def NrroLinearityScreen(self, inPrm):

      for cyl in inPrm['trackList']:
         if type(cyl) == types.TupleType:
            inPrm['base']['TEST_CYL'] = cyl
         else:
            inPrm['base']['TEST_CYL'] = self.oUtility.ReturnTestCylWord(cyl)

         objMsg.printMsg("Now evalutating nrro Non-Linearity on track %s" % str(cyl),objMsg.CMessLvl.VERBOSEDEBUG)
         self.St(inPrm['base'])

   def servoScan(self, inPrm):
      """
      Validate servo scan times for different seek types
      """
      for scanType in inPrm['modes'].keys():
         objMsg.printMsg("Running servo scan in %s seek mode" % scanType, objMsg.CMessLvl.VERBOSEDEBUG)
         self.St(self.oUtility.overRidePrm(inPrm['base'],{'SEEK_TYPE':inPrm['modes'][scanType]}))


   def resonanceTest(self, inPrm):
      """
       Measure the resonance frequencies and amplitudes on heads at the specified cylinder.
       This information is used in the mechanical design process to determine resonance issues and compare design changes.
       It is used in the Failure Analysis process to determine which part is causing the resonance and therefore, which part to replace.
      """
      for locn in inPrm.keys():
         if testSwitch.BF_0127147_357552_REFERENCE_T180_PARAM_BY_STRING_NAME:
            #For T180, inPrm is a dict of dicts, that gets frozen when TestParameters is imported.
            # This change abstracts the call so any TP overrides are now referenced.
            # This fix will fail if 'prm_name' key removed from T180 TestParameters.py dictionaries.
            prmDict = eval('TP.' + inPrm[locn])
            self.St( prmDict )
         else:
            self.St( inPrm[locn] )

   def tunedSeek(self, inPrm):
      """
       Tuned seek test.  Loops through all of the parameters sets in the list.
      """
      for i in range(len(inPrm)):
         self.St(inPrm[i])

   def servoRetract(self, inPrm):
      """
       Excercise the servo actuator
      """
      self.St(inPrm)

#---------------------------------------------------------------------------------------------------------#
