#-----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                     #
#-----------------------------------------------------------------------------------------#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#-------------------------------------------------------------------------------
# Description: Adaptive Essential Guarantee Items Scan
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/adaptivePrmVeri.py $
# $Revision: #1 $
# $Change: 1047653 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/adaptivePrmVeri.py#1 $
# Level: Product
#-----------------------------------------------------------------------------------------#

import types, os, time, re
from Constants          import *
from TestParamExtractor import TP
from Test_Switches      import testSwitch
from Servo              import CServoFunc
from PowerControl       import objPwrCtrl
import MessageHandler   as objMsg
import Utility
import ScrCmds


###########################################################################################################
###########################################################################################################
class SP_Aegis:
   """
      Serial port version of Adaptive Essential Guarantee Items Scan
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut       = dut
      self.params    = params
      depList        = []
      self.oSrvFunc  = CServoFunc()

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not ConfigVars[CN].get('AEGIS_SCREEN', 0) or not testSwitch.FE_0266393_305538_AEGIS_SCREEN:
         ScriptComment('AEGIS is NOT enabled')
         return
      # MUST have powercycle @ beginning to reload everything remain in RAM
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      results = []
      # special checks
      if hasattr(TP, 'svoRules'):
         results.extend(self.spSvoRamChk())
      if hasattr(TP, 'afhClrRules'):
         results.extend(self.spAfhClrChk())

      if results:
         # print & fail
         failFlg = False
         for item, data, fail in results:
            self.dut.dblData.Tables('P_SP_AEGIS_SUMMARY').addRecord({
                        'SPC_ID'    : 1,
                        'ITEM'      : item[:24],
                        'DATA'      : str(data)[:32],
                        'STATUS'    : {True: 'FAIL', False: 'PASS'}[bool(fail)],
            })
            if fail:
               failFlg = True
         objMsg.printDblogBin(self.dut.dblData.Tables('P_SP_AEGIS_SUMMARY'))

         if failFlg and not testSwitch.virtualRun:
            ScrCmds.raiseException(48681, 'Drive Setup Incorrectly.')

   #----------------------------------------------------------------------------
   def spSvoRamChk(self):
      """
      perform a single test 11 to check servo ram item.
      @return: wrapped tuple, ((item, value, fail or not), ...)
      """
      ret = []
      for item, SymOfstName, LocCnt, bitMsk, criterion in TP.svoRules:
         ScriptComment('Servo RAM check: %s' % item)
         if testSwitch.virtualRun:
            value = criterion
         else:
            value = self.oSrvFunc.getServoSymbolData(addrName=SymOfstName, bitMask = bitMsk)
         ret.append((item, '0x%04X' % value, str(value) != str(criterion)))

      return ret

   #----------------------------------------------------------------------------
   def spAfhClrChk(self):
      """
      AFH Clearance Check, perform T172 and read data from P172_AFH_DH_CLEARANCE
      @return: wrapped tuple, ((item, value, fail or not), ...)
      """
      ScriptComment('AFH Clearance Check')

      try:
         tbldata = self.dut.dblData.Tables('P172_AFH_DH_CLEARANCE').tableDataObj()
      except:
         ScriptComment('Cannot get existing P172_AFH_DH_CLEARANCE...')
         self.oSrvFunc.St({'test_num': 172, 'prm_name':'AFH_CLEARANCE', 'timeout':200, 'spc_id': 0, 'CWORD1':0x5,})
         tbldata = self.dut.dblData.Tables('P172_AFH_DH_CLEARANCE').tableDataObj()

      ret = []
      for desc, rowName, rapOfSt, criterion in TP.afhClrRules:
         data  = [int(row[rowName]) for row in tbldata]
         fail  = Utility.any(str(datum) != str(criterion) for datum in data)
         datum = '[%s-%s]' % (min(data), max(data))
         ret.append((rowName, datum, fail))

      return ret



################################################################################
'''
class IO_AEGIS(State):
   #----------------------------------------------------------------------------
   @staticmethod
   def run():
      import IOLib
      if cfg.featureEnabled == False:
         ScriptComment('adaptivePrmVeri is NOT enabled')
         return

      oProc = CProcess()
      # MUST have powercycle @ beginning to reload everything remain in RAM
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      IOLib.SEDAuthUnlocks()              # Temp unlock for SED

      results = []
      # special checks

      if TP.ProductName in ['IRONMAN',]:
         oProc.dnldCode(codeType='INC_AP', timeout=600)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         IOLib.SEDAuthUnlocks()              # Temp unlock for SED

      results.extend(ioSvoRamChk())
      results.extend(ioAfhClrChk())

      # print & fail
      failFlg = False
      cm.AddScriptTable('P_IO_AEGIS_SUMMARY', 'ITEM DATA STATUS', (25,32,6))

      for item, data, fail in results:
         cm.AddPtableRecord('P_IO_AEGIS_SUMMARY', spcId=1,
            addRecord = {
               'ITEM'   : item[:24],
               'DATA'   : str(data)[:32],
               'STATUS' : {True: 'FAIL', False: 'PASS'}[bool(fail)]
            })
         if fail:
            failFlg = True
      if failFlg and not testSwitch.virtualRun:
         ScrCmds.raiseException(48681, 'Drive Setup Incorrectly.')

      if TP.ProductName in ['IRONMAN',]:
         oProc.dnldCode(codeType='INC', timeout=600)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
         IOLib.SEDAuthUnlocks()              # Temp unlock for SED

   #----------------------------------------------------------------------------
   def fail(self):
      import IOFunctions as IOFunc
      IOFunc.CommonFailProc()
'''

#----------------------------------------------------------------------------
'''
def ioSvoRamChk():
   """
   perform a single test 611 to check servo ram item.
   @return: wraped tuple, ((item, value, fail or not), ...)
   """
   ret = []
   for item, SymblOfst, LocCnt, bitMsk, criterion in cfg.svoRules:
      criterion = proc.ParmExtractor(criterion)

      ScriptComment('Servo RAM check: %s' % item)
      # Back up original table and clear its all data
      try:
         backup, cm.pTables['P611_READ_SERVO_RAM']['DATA'] =\
            cm.pTables['P611_READ_SERVO_RAM']['DATA'], []
      except KeyError:  # if original table not exist
         backup = []

      proc.St(
         {'test_num': 611,
          'prm_name': item,
          'timeout': 600,
          'TEST_OPERATING_MODE': (0x0001,),
          'TABLE_INDEX': SymblOfst,
          'OFFSET_VALUE': LocCnt * 2,
          'loadTables': 'P611_READ_SERVO_RAM',  # table contain data
         })
      if testSwitch.virtualRun:
         value = criterion
      else:
         value = cm.GetTableInfo('P611_READ_SERVO_RAM',
                              row=-1, col='RETURNED_DATA')  # get table

      value &= (bitMsk ^ 0xFFFF)
      ret.append((item, '0x%04X' % value, value != criterion))

      # Recover original table & clean backup
      backup, cm.pTables['P611_READ_SERVO_RAM']['DATA'] = [], backup

   return ret
'''

#----------------------------------------------------------------------------
'''
def ioAfhClrChk():
   """
   AFH Clearance Check, perform T172 and read data from P508_BUFFER,
    P508_BUFFER_DATA
   @return: wraped tuple, ((item, value, fail or not), ...)
   """
   # headType = objDut.HGA_SUPPLIER
   # headType = cm.GetDriveAttribute('HGA_SUPPLIER')
   # if headType:
   #    proc.var.headType = headType

   ScriptComment('AFH Clearance Check')

   # Interface Identify
   # if cm.drvIntf == 'SAS':
   #    tblLoad = 'P508_BUFFER'
   #    addrHeader = 'LINE'
   #    hexHeader = 'B0,B1,B2,B3,B4,B5,B6,B7,B8,B9,BA,BB,BC,BD,BE,BF'.split(',')
   # elif cm.drvIntf == 'SATA':
   #    tblLoad = 'P508_BUFFER_DATA'
   #    addrHeader = 'ADDRESS'
   #    hexHeader = '00,01,02,03,04,05,06,07,08,09,0A,0B,0C,0D,0E,0F'.split(',')
   # else:
   #    ScrCmds.raiseException(11107, 'Drive type is not supported on this Line')

   # Back up original table and clear its all data
   try:
      backup, cm.pTables[tblLoad]['DATA'] = cm.pTables[tblLoad]['DATA'], []
   except KeyError:  # if original table not exist
      backup = []

   proc.St(
      {  # dump the whole RAP into read buffer without display
         'ATTRIBUTE': 'drvIntf',
         'BASE': {
            'test_num': 638,
            'prm_name': 'prm_638_DumpRAP',
            'timeout': 600,
         },
         'SAS': {
            'REPORT_OPTION': (0x0001,),
            'PARAMETER_0': (0x4B01,),
            'PARAMETER_1': (0x0200,),
            'PARAMETER_2': (0x0000,),
         },
         'SATA': {
            'CTRL_WORD1': (0x0001,),
            'DFB_WORD_0': (0x4B01,),
            'DFB_WORD_1': (0x0100,),
            'DFB_WORD_2': (0x0000,),
         },
      })
   proc.St(
      {  # display read buffer (truncate only clearance info)
         'ATTRIBUTE': 'drvIntf',
         'BASE': {
            'test_num': 508,
            'prm_name': 'prm_508_DisplayBuffer',
            'timeout': 600,
            'loadTables': tblLoad,  # table contain data
         },
         'SAS': {
            'PARAMETER_1': (0x0005,),
            'PARAMETER_2': (cfg.afhRapInit,),
            'PARAMETER_3': (cfg.afhHdOfst * self.dut.imaxHead,),
         },
         'SATA': {
            'CTRL_WORD1': (0x0005,),
            'BYTE_OFFSET': (0x0000, cfg.afhRapInit,),
            'BUFFER_LENGTH': (0x0000, cfg.afhHdOfst * self.dut.imaxHead,),
         },
      })
   if testSwitch.virtualRun:
      tbl = cfg.bufferData
   else:
      tbl = proc.CrunchTable(tblLoad, addrHeader, hexHeader)

   ret = []
   for rowName, entryOfSt, criterion in proc.ParmExtractor(cfg.afhClrRules):
      data = []
      # per Rory, RAP save all !!!!logical!!!! head clearance
      for hd in xrange(self.dut.imaxHead):
         ofst = cfg.afhHdOfst * hd + entryOfSt
         data.append(tbl[ofst / 16][ofst % 16])
      fail = Utility.any(datum != criterion for datum in data)
      ret.append((rowName, data, fail))

   # Recover original table & clean backup
   backup, cm.pTables[tblLoad]['DATA'] = [], backup

   return ret
'''
