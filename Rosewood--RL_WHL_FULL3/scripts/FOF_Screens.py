#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/27 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/FOF_Screens.py $
# $Revision: #5 $
# $DateTime: 2016/12/27 23:31:28 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/FOF_Screens.py#5 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds
from Codes import fwConfig
import re
import os
import types

DEBUG = 0
supressOutput = 1
#----------------------------------------------------------------------------------------------------------
class CServoUtil(CState):
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

      from Servo import CServoOpti
      self.oSrvOpti = CServoOpti()
      self.servoSymbolOffsetTableDict= {
         #Symbol                      Offset
         'u32_MaxCylinder'          :      2,
         'i16_Current2Out'          :     21,    # VCM Current2
         'eMotorState'              :     44,
         'i16_UnsafeFlag'           :     56,    # Unsafe Flag
         'u16_MaxHeadNumberSAP'     :     88,    # Max Head
         'u16_SeekModeSAP'          :    101,    # Seek Mode
         'i16_AgcFlyHeight'         :    110,    # AGC
         'i16_DemodPositionError'   :    112,    # PES
         'u16_pMrRangeBiasGainTableSymTab': 132,
         'SECTORS_PER_REV'          :    140,    # Wedge Per Track
         'ARC_TPI'                  :    142,  
         'u16_SAPVPD'               :    169,    # Product ID
         'u16_DemodDestinationHead' :    192,
         'u16_VcatParameters'       :    208,
         'GAIN_1_VCAT'              :    220,
         'GAIN_2_VCAT'              :    221,
         'u16_HeaterControl'        :    222,    # master heat enable/disable
         'u8_PhysicalHeadTable'     :    225,    # Logical head to phyical head map
         'sAcffData'                :    249,
      }
      self.symbolServoRamAddressDict = {}
      servosym = fwConfig[self.dut.driveattr['PART_NUM']]['SFWP'].replace('_','').replace('.zip','.SYM')
      servosym = servosym.replace('signed','')
      self.servosym = os.path.join(ScrCmds.getSystemDnldPath(),  servosym)
   #---------------------------------------------------------------------------------------------------------
   def getServoRamAddressByName(self,symbolName = ''):
      if symbolName not in self.symbolServoRamAddressDict.keys():
         try:
            servoSymFile = open(self.servosym,  'rb')
         except:
            self.servosym=self.servosym.replace('.SYM','.sym')
            try:
               servoSymFile = open(self.servosym,  'rb')
            except:
               try:
                  from  PackageResolution import PackageDispatcher
                  pd = PackageDispatcher(self.dut, 'CMB')
                  fileName = ''.join(pd.getFileName().split('_')[:2])
                  servosym = '%s.sym'%fileName
                  self.servosym = os.path.join(ScrCmds.getSystemDnldPath(), servosym)
                  servoSymFile = open(self.servosym,  'rb')
               except:
                  raise        
         data = servoSymFile.read()
         servoSymFile.close()
         lines = data.splitlines()
         symbolAddress = 0 
         for i in range(len(lines)):
            row = lines[i].split()
            if row[0] == symbolName:
               symbolAddress = int(row[1],16)
               break
         self.symbolServoRamAddressDict[symbolName] = symbolAddress
      else:
         symbolAddress =  self.symbolServoRamAddressDict[symbolName]
      return symbolAddress
   #---------------------------------------------------------------------------------------------------------
   def getServoRamDataBySymbolOffset(self,symbolName, accessType = 0, numLocs = None, supressOutput = supressOutput, paramName = ''):

      symbolOffset= self.servoSymbolOffsetTableDict[symbolName]
      cmd = {'test_num'               : 11, 
             'prm_name'               : 'GetSymbolViaOffset_%s' % symbolName,
             'SYM_OFFSET'             : symbolOffset, 
             'CWORD1'                 : 512,
             'ACCESS_TYPE'            : accessType, 
             'timeout'                : 10,
             'stSuppressResults'      : supressOutput,
             'DblTablesToParse'       : 'P011_SV_RAM_RD_BY_OFFSET'
             }

      if numLocs!=None:
         cmd['NUM_LOCS'] = numLocs       
      self.oSrvOpti.St(cmd)
      #cmdData = self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]
      cmdData = self.dut.objSeq.SuprsDblObject['P011_SV_RAM_RD_BY_OFFSET'][:]
     
      readData=map(lambda x: int(x['READ_DATA'],16), [i for i in cmdData]  )
      
      
      if DEBUG>0:
         objMsg.printMsg("Symbol %s (Offset : %d) Read Data : %s" % (symbolName,symbolOffset, str(readData)))
         
      if len(readData) == 1:
         return readData[0]
      else:
         return readData

   #-------------------------------------------------------------------------------------------------------
   def getServoRamDataByAddress(self, symbolAddress, accessType = 2, supressOutput = supressOutput, paramName = ''):
  
      self.oSrvOpti.St({ 'test_num'              : 11,
                        'prm_name'              : 'GetSymbolViaAddr'+ (paramName!='' and ('_'+paramName) or ''),
                        'START_ADDRESS'         : self.oSrvOpti.oUtility.ReturnTestCylWord(symbolAddress),
                        'END_ADDRESS'           : self.oSrvOpti.oUtility.ReturnTestCylWord(symbolAddress),
                        'timeout'               : 1000,
                        'CWORD1'                : 0x0001,
                        'ACCESS_TYPE'           : accessType,
                        'EXTENDED_MASK_VALUE'   : 0xFFFF,
                        'stSuppressResults'     : supressOutput,
                        'DblTablesToParse'      : 'P011_RW_SRVO_RAM_VIA_ADDR'                         
                        })

      #cmdData = self.dut.dblData.Tables('P011_RW_SRVO_RAM_VIA_ADDR').tableDataObj()[-1]
      cmdData = self.dut.objSeq.SuprsDblObject['P011_RW_SRVO_RAM_VIA_ADDR'][-1]
      readData = int(cmdData['SRVO_DATA'],16 )
 
      if DEBUG>1:
         objMsg.printMsg("Symbol Address 0x%08X Read Data : 0x%X" % (symbolAddress, readData))
      return readData
   #-------------------------------------------------------------------------------------------------------   
   def getServoRamDataByName(self, symbolName, accessType = 2, offset = 0, supressOutput = supressOutput):
      symbolAddress = self.getServoRamAddressByName(symbolName)
      if symbolAddress > 0:
         paramName = offset>0 and  '%s_Offset_%d' %(symbolName,offset) or symbolName 
         readData = self.getServoRamDataByAddress(symbolAddress + offset, accessType, supressOutput, symbolName)
      else:
         ScrCmds.raiseException(11044,"Can not find  symbol '%s' in the file '%s'" % (symbolName, self.servoSymbolFileFullPath))
         
      if DEBUG>0:
         objMsg.printMsg("Symbol %s Read Data : 0x%X" % (symbolName,readData))   
      return readData
   #-------------------------------------------------------------------------------------------------------   
   def setServoRamDataBySymbolOffset(self, symbolName, writeData, maskValue = 0, accessType=2, supressOutput = supressOutput, paramName = ''):
      if accessType == 1:
         maskValue = maskValue | 0xFFFFFF00
      elif accessType == 2:
         maskValue = maskValue | 0xFFFF0000
      elif accessType == 3:
         pass
      else:
         objMsg.printMsg("Invalid access type input '%s'" % accessType) 
         raise   
 
      symbolOffset= self.servoSymbolOffsetTableDict[symbolName]
      self.oSrvOpti.St({'test_num'               : 11, 
                       'prm_name'               : 'SetSymbolViaOffset_%s' % symbolName,
                       'SYM_OFFSET'             : symbolOffset,
                       'MASK_VALUE'             : maskValue & 0xFFFF,
                       'EXTENDED_MASK_VALUE'    : maskValue >> 16,
                       'WR_DATA'                : writeData,
                       'CWORD1'                 : 1024,               # 0x400
                       'ACCESS_TYPE'            : accessType, 
                       'timeout'                : 10,
                       'stSuppressResults'      : supressOutput,
                       'DblTablesToParse'       : 'P011_SV_RAM_RMW_BY_OFFSET'
                       })
      return PASS
   #-------------------------------------------------------------------------------------------------------
   def issueServoCmd(self, params, paramName = '', timeout = 60, supressOutput = supressOutput ):
      
      params = list(params) + [0] * (10-len(params))
      SetFailSafe()
      self.oSrvOpti.St({'test_num'            :11,
                       'prm_name'            : paramName,
                       'PARAM_0_4'           : params[0:5], 
                       'PARAM_5_9'           : params[5:10],
                       'timeout'             : timeout,
                       'DblTablesToParse'    : ['P011_DO_SERVO_CMD10'],
                       'stSuppressResults'   : supressOutput})    
      ClearFailSafe() 
      cmdStatus = int(self.dut.objSeq.SuprsDblObject['P011_DO_SERVO_CMD10'][-1]['CMD_STAT_HEX'],16)
      diagStatus = int(self.dut.objSeq.SuprsDblObject['P011_DO_SERVO_CMD10'][-1]['DIAG_HEX'],16)
      #servoData = self.dut.objSeq.SuprsDblObject['P011_SRVO_DIAG_RESP'][-1]
      servoData = self.dut.dblData.Tables('P011_SRVO_DIAG_RESP').tableDataObj()[-1] 
     
      keys = [i for i in servoData.keys() if re.search('[*]|\d+',str(i))]
      servoDataList = [ 0 ] * len(keys)
      for k in keys:
         if k == '*':
            servoDataList[0] = int(servoData[k],16)
         else:   
            servoDataList[k-4] = int(servoData[k],16)
      if DEBUG>0:
         msg = '\nServo Response Data:\nOffset : '+ ''.join(['%4d ' % i for i in xrange(len(servoDataList))]) + '\nData   : '   
         for i in xrange(len(servoDataList)):
            msg += '%04X ' % servoDataList[i] 
         objMsg.printMsg(msg+'\n')
      return cmdStatus,diagStatus,servoDataList
      
class CFormatOutput:
   def formatStatusString(self,status,formatStr='%s'):
      """
      Description:  formate the PassFail status output                  
                    status - status after spec check
                              = True  print 'Fail'
                              = False print ' ' 
                    formatStr - format of string          
      """
      return  formatStr % (status==True and 'Fail' or ' ')
   #------------------------------------------------------------------------------------------------------------
   def formatSpecString(self,specData=None,formatStr='%s'):
      """
      Description:  formate the spec output
                    formatStr -  format of string
                    specData  -  spec value,  can be integer, floate, list, tuple 
                                 if spec = None, will print ' '
                                 if spec is range, print min and max value
      """
      if type(specData) in (types.ListType, types.TupleType):
         if specData!=None:
            output = formatStr % (specData[0],specData[1]) 
         else:
            output = ' '* len(formatStr % (0,0)) 
      else:  
         if specData!=None:
            output = formatStr % specData 
         else:
            try:
               output = ' ' * len(formatStr % 0)   # example : when spec = None , format = '%.1f'
            except:   
               output = ' ' * len(formatStr % (0,0)) # example : when spec = None , format = '%.1f/%.1f'  
      return output
   #------------------------------------------------------------------------------------------------------------   
   def formatLoadUnloadWithoutDemodSyncOutput(self,dataDict,tableName):
      """
      Description : output Non-Demod Sync load unload data as Dblog format
      Parameteer  : dataDict - load/unload current, velocity, motor speed dip, Bemf gain, Bemf Residual error
                    tableName - like P_LOAD_WITH_DEMOD_SYNC
      """
      output  = '\n%s:\n' % tableName.upper()
      output += ' PEAK_CURRENT PEAK_VELOCITY MAX_MOTOR_DIP_ERROR BEMF_CAL_GAIN BEMF_RESIDUAL_ERROR\n'
      output += ' %(LulPeakCurrent)12.2f %(LulPeakVelocity)13.2f %(MaxMotorSpeedDipError)19.1f %(BemfCalGain)13d %(BemfResidualError)19d\n' % dataDict
      output += '\n'
      return output
   #------------------------------------------------------------------------------------------------------------
   def formatMrResistanceOutput(self,mrRes,lgcToPhysHdMap):
      """ 
      Descritption : output MR resistance as Dblog format
      Parameter    : mrRes - MR resistance of all heads  
      """
      output = "\nP_MR_RESISTANCE:\n"
      output += ' LGC_HD PHYS_HD RESISTANCE\n'
      for lgcHd in xrange(len(mrRes)):
         output+=' %6d %7d %10.1f\n' % (lgcHd,lgcToPhysHdMap[lgcHd],mrRes[lgcHd])
      output += '\n'
      return output
      
class CFOFScreen(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      depList = []
      CState.__init__(self, dut, depList)

      self.scriptInfo = \
      {
         'PrePretest Rev'           : '1.0',
         'PrePretest SW Date'       : '2016.3.4',
      }
      objMsg.printMsg('*** PrePretest Script Rev=%s Dated[%s]' % (self.scriptInfo['PrePretest Rev'], self.scriptInfo['PrePretest SW Date']))
      self.servoUtil = CServoUtil(self.dut)
      self.formatOutput = CFormatOutput()
   #-------------------------------------------------------------------------------------------------------
   def getMotorFailureCode(self): 
      
      motorFailureCodeDecodeDict = {        
               0x00  :  'NO_MOTOR_FAILURE',
               0x01  :  'CLOCK_PERIOD_MAX_FAIL',
               0x02  :  'CLOCK_PERIOD_MIN_FAIL',
               0x03  :  'CLOCK_CAL_TIMEOUT_FAIL',
               0x04  :  'CURRENT_LIMITER_CAL_FAIL',
               0x05  :  'RPL_MEASURE_FAIL',
               0x06  :  'RPL_DECISION_FAIL',
               0x07  :  'RPA_CURRENT_SENSE_1_FAIL',
               0x08  :  'RPA_CURRENT_SENSE_2_FAIL',
               0x09  :  'RPA_RAMP_UP_FAIL',
               0x10  :  'ACCEL_SPEED_FAIL (accelerate to "flying speed")',
               0x11  :  'ACCEL_SPEED_FAIL (accelerate to "up to speed")',
               0x12  :  'ACCEL_TIME_FAIL (accelerate to "flying speed")',
               0x13  :  'ACCEL_TIME_FAIL (accelerate to "up to speed")',
               0x14  :  'ACCEL_MOTOR_INTERRUPT_LOST',
               0x20  :  'COMM_TACH_MISMATCH',
               0x21  :  'COMM_TACH_SPEED_FAIL',
               0x22  :  'COMM_TACH_TIMEOUT',
               0x23  :  'COMM_TACH_OVERSPEED',
               0x30  :  'AT_SPEED_FAIL',
               0x40  :  'POWER_DEVICE_FAULT_FAIL',
               0x41  :  'failure due to spindle Underspeed fault',
               0x42  :  'failure due to early over temperature warning ( EOTW )',
               0x43  :  'failure due to over temperature shutdown ( OTSD )',
               0x44  :  'failure due to over current ( OC )',
              }
      motorFailureCode = self.servoUtil.getServoRamDataByName('u16_MotorFailureCode',accessType = 2)
      motorFailureCodeDecode = motorFailureCodeDecodeDict.get(motorFailureCode & 0xFF,'Unknown')   
      return motorFailureCode,motorFailureCodeDecode

   def getMotorState(self): 
         motorStateDecodeDict = {        
               0x00  :  'MOTOR_STOPPED',
               0x05  :  'AT_SPEED_SENSOR_MODE',
               0x06  :  'AT_SPEED_EMBEDDED_MODE',
               0x0E  :  'IDLE3_MODE',
               0x10  :  'AWAKE0_FAULT',
               0x11  :  'CLOCK_CAL_MEASURE',
               0x12  :  'CURRENT_LIMITER_CAL',
               0x13  :  'ACTUATOR_BUZZ',
               0x14  :  'RPL_DELAY',
               0x1D  :  'RPL_COAST',
               0x17  :  'RPL_MEASURE',
               0x18  :  'RPA_RAMP_UP',
               0x19  :  'LINEAR_RAMP',
               0x2A  :  'ACCELERATE',
               0x3B  :  'HAND_OFF_TIMING_SYNC',
               0x4B  :  'RESTART_TIMING_SYNC',
               0x6B  :  'UP_TO_SPEED_COMM_TACH',
               0x7B  :  'AT_SPEED_COMM_TACH',
               0x8B  :  'IDLE_COMM_TACH',
               0x8C  :  'INIT_STOP',
               0x9C  :  'COMMAND_STOP',
               0xAC  :  'STARTFAIL_STOP',
               0xBC  :  'SPEEDFAIL_STOP',
               0xCC  :  'TACHFAIL_STOP',
             }  
         motorState = self.servoUtil.getServoRamDataBySymbolOffset("eMotorState",accessType=1)      
         motorStateDecode = motorStateDecodeDict.get(motorState,'Unknown')
         return motorState,motorStateDecode
         
   def checkMotor(self):
      
      # motor spin down/spin up motor
      cmdStatus,diagStatus,servoData = self.servoUtil.issueServoCmd([0x000],paramName='SpinDownMotor_000', timeout = 120, supressOutput = 0)
      #then spin up motor 
      cmdStatus,diagStatus,servoData = self.servoUtil.issueServoCmd([0x300],paramName='SpinUpMotor_300', timeout = 120, supressOutput = 0)
      motorState, motorStateDecode = self.getMotorState()
      motorFailureCode, motorFailureCodeDecode = self.getMotorFailureCode()
      objMsg.printMsg('--------------  Check Start Motor Only  ----------------')
      objMsg.printMsg('       eMotorState : 0x%02X (%s)' % (motorState, motorStateDecode)) 
      objMsg.printMsg('Motor Failure Code : 0x%04X (LowBytes : %s)' % (motorFailureCode, motorFailureCodeDecode ) ) 
      objMsg.printMsg('')
      if motorFailureCode == 0x1705 or motorFailureCode == 0x1809:
         ScrCmds.raiseException(11247, 'Motor check failed , diag error = %s' %str(motorFailureCode))
   
   def getLoadUnloadErrorCode(self):
      lulErrorCodeDecodeDict = {
               0x01  :  'LOAD_UNLOAD_ERROR_DEFAULT',
               0x02  :  'LOAD_HEADS_NO_ERROR',
               0x03  :  'MOTOR_NOT_AT_SPEED',
               0x04  :  'LOAD_HEADS_BEMF_CAL_FAILURE',
               0x05  :  'LOAD_HEADS_TIMEOUT_FAILURE',
               0x06  :  'LOAD_HEADS_FREE_FALL_FAILURE',
               0x07  :  'LOAD_HEADS_DWELL_SEEK_FAILURE',
               0x08  :  'LOAD_HEADS_DEMOD_SYNC_FAILURE',
               0x09  :  'LOAD_HEADS_CONTROL_OVERFLOW',
               0x10  :  'LOAD_HEADS_UNLATCH_FAILURE',
               0x0A  :  'LOAD_HEADS_SENSOR_TEST_FAILURE',
               0x0B  :  'LOAD_HEADS_SPIN_SPEED_UNSAFE',
               0x0D  :  'LOAD_HEADS_THERMAL_SHUTDOWN',
               0x11  :  'UNLOAD_HEADS_NO_ERROR',
               0x12  :  'UNLOAD_HEADS_BEMF_CAL_FAILURE',
               0x13  :  'UNLOAD_HEADS_TIMEOUT',
               0x14  :  'UNLOAD_HEADS_ID_SLAM_FAILURE',
           }
         
      lulErrorCode = self.servoUtil.getServoRamDataByName('eLoadUnloadErrorCode',accessType=2)      
      lulErrorCodeDecode = lulErrorCodeDecodeDict.get(lulErrorCode,'Unknown')
      return lulErrorCode,lulErrorCodeDecode   
      #-------------------------------------------------------------------------------------------------------
   def _checkLoadUnloadStatus(self, servoData, specDict, testHead=None, testState = '', title = '' ):

      passFailStatus = PASS        
      title = title!='' and title or testState      
      lulPeakCurrentLimit        = specDict.get('LulPeakCurrentLimit',None)
      lulPeakVelocityLimit       = specDict.get('LulPeakVelocityLimit',None)
      maxMotorSpeedDipErrorLimit = specDict.get('MaxMotorSpeedDipErrorLimit',None)
      bemfCalGainLimit           = specDict.get('BemfCalGainLimit',None)      
      bemfResidualErrorLimit     = specDict.get('BemfResidualErrorLimit',None) 
      
      lulErrorCode, lulErrorCodeDecode = self.getLoadUnloadErrorCode()     
      
      status = {}      
      status['LulPeakCurrent']        = lulPeakCurrentLimit!=None and abs(servoData['LulPeakCurrent']) > abs(lulPeakCurrentLimit) or False
      status['LulPeakVelocity']       = lulPeakVelocityLimit!=None and abs(servoData['LulPeakVelocity']) > abs(lulPeakVelocityLimit) or False
      status['MaxMotorSpeedDipError'] = maxMotorSpeedDipErrorLimit!=None and abs(servoData['MaxMotorSpeedDipError']) > abs(maxMotorSpeedDipErrorLimit) or False
      status['BemfCalGain']           = bemfCalGainLimit!=None and abs(servoData['BemfCalGain']) > abs(bemfCalGainLimit) or False
      status['BemfResidualError']     = bemfResidualErrorLimit!=None and abs(servoData['BemfResidualError']) > abs(bemfResidualErrorLimit) or False
      # only check eLoadUnloadErrorCode for load head with demod sync test. 
      if testHead != None:
         status['LoadUnloadErrorCode']   = lulErrorCodeDecode != 'UNLOAD_HEADS_NO_ERROR'   # eLoadUnloadErrorCode != 11
      else:
         status['LoadUnloadErrorCode']   = False
      
      # print message
      objMsg.printMsg('-'*20 + ' ' + title + ' ' + '-'*20)
      objMsg.printMsg('             Variable    %10s %10s %10s'  %('Measure','Limit','Status') )    
      objMsg.printMsg('    LulPeakCurrent(mA) : %10.2f %10s %10s' % (
                                                     servoData['LulPeakCurrent'],
                                                     self.formatOutput.formatSpecString(lulPeakCurrentLimit,'%10.2f'), 
                                                     self.formatOutput.formatStatusString(status['LulPeakCurrent']),                                                     
                                                     ))
      objMsg.printMsg('  LulPeakVelocity(IPS) : %10.2f %s %10s' % (
                                                     servoData['LulPeakVelocity'],
                                                     self.formatOutput.formatSpecString(lulPeakVelocityLimit,'%10.2f'), 
                                                     self.formatOutput.formatStatusString(status['LulPeakVelocity']),                                                       
                                                     ))
      objMsg.printMsg(' MaxMotorDipError(RPM) : %10.1f %s %10s' % (
                                                   servoData['MaxMotorSpeedDipError'],
                                                   self.formatOutput.formatSpecString(maxMotorSpeedDipErrorLimit,'%10d'), 
                                                   self.formatOutput.formatStatusString(status['MaxMotorSpeedDipError']),                                                    
                                                   ))
      objMsg.printMsg('           BemfCalGain : %10d %s %10s' % ( 
                                                   servoData['BemfCalGain'],
                                                   self.formatOutput.formatSpecString(bemfCalGainLimit,'%10d'), 
                                                   self.formatOutput.formatStatusString(status['BemfCalGain']) ,                                                                                                    
                                                  ))                                                  
      objMsg.printMsg('  BemfCalResidualError : %10d %s %10s' % ( 
                                                   servoData['BemfResidualError'],
                                                   self.formatOutput.formatSpecString(bemfResidualErrorLimit,'%10d'), 
                                                   self.formatOutput.formatStatusString(status['BemfResidualError']),                                                                                                                                                    
                                                  ))
                                                  
      objMsg.printMsg('  LoadUnloadErrorCode  :  %10s (%s) %s' % ( 
                                                   '0x%02X' % lulErrorCode,
                                                    lulErrorCodeDecode,
                                                    self.formatOutput.formatStatusString(status['LoadUnloadErrorCode']),
                                                   ))

      objMsg.printMsg('')
      diagRespList = [] 
      diagRespDict = {}
      if status['BemfCalGain'] == True:
         passFailStatus = FAIL
         diagRespList.append({'PotentialCause' : 'PCBA_BEMF_GAIN'  ,
                              'TestState'      : testState,
                              'FailReason'     : 'BemfCalGain = %.1f > limit %.1f ' % (servoData['BemfCalGain'],
                                                                                       bemfCalGainLimit),
                              'HeadList'       : [], 
                              'Severity'       : 1
                             })                           
                             
      elif status['LulPeakCurrent'] == True:
         passFailStatus = FAIL
         diagRespList.append({'PotentialCause' : 'HSA_STUCK_ON_RAMP'  ,
                              'TestState'      : testState,
                              'FailReason'     : 'Abs(LulPeakCurrent) = %.1f > limit %.1f' % (abs(servoData['LulPeakCurrent']),
                                                                                              abs(lulPeakCurrentLimit)),
                              'HeadList'       : [],
                              'Severity'       : 1
                             })
                    
      elif status['MaxMotorSpeedDipError'] == True:
         passFailStatus = FAIL
         diagRespList.append({'PotentialCause' : 'HDI_SPIN_DIP',
                              'TestState'      : testState,
                              'FailReason'     : 'MaxMotorSpeedDipError = %.1f > limit %.1f ' % (servoData['MaxMotorSpeedDipError'],
                                                                                                 maxMotorSpeedDipErrorLimit),
                              'HeadList'       : [],
                              'Severity'       : 1
                             })                    
      elif servoData['LoadUnloadErrorCode'] == 0x7: # 0x07 - LOAD_HEADS_DEMOD_SYNC_FAILURE
         passFailStatus = FAIL
         diagRespList.append({'PotentialCause' : 'HEAD_DEMOD_SYNC',
                              'TestState'      : testState,
                              'FailReason'     : 'LoadUnloadErrorCode = 0x%02X (%s)' % (servoData['LoadUnloadErrorCode'],
                                                                                        lulErrorCodeDecode),
                              'HeadList'       : testHead!=None and [testHead] or [],
                              'Severity'       : 1
                             }) 
      return passFailStatus,diagRespList,diagRespDict
   def getLoadUnloadHeadData(self, servoCmd, paramName = '', timeout = 120, supressOutput = 0):

      BemfCalGain_IDX          = 1
      BemfResidualError_IDX    = 3
      LulPeakCurrent_IDX       = 5
      MaxMotorDipError_IDX     = 6
      LulPeakVelocity_IDX      = 7
      LoadUnloadErrorCode_IDX  = 9
      
      lulPeakCurrent        = 0 
      lulPeakVelocity       = 0
      maxMotorDipRPMError   = 0
      bemfResidualError     = 0
      bemfCalGain           = 0
      
      filteredMicroAmpPerBit = self.signed(self.servoUtil.getServoRamDataByName('i16_FilteredMicroAmpPerBit'))
      rpmGainCounts = self.signed(self.servoUtil.getServoRamDataByName('i16_RPMGainCounts'))  
      desiredCommCycleTime = self.signed(self.servoUtil.getServoRamDataByName('u16_DesiredCommCycleTime'))
      bitsPerIps = self.signed(self.servoUtil.getServoRamDataByName('i16_BitsPerIps'))
      
      cmdStatus, diagStatus, servoData = self.servoUtil.issueServoCmd(servoCmd,  paramName, timeout, supressOutput)

      # calculate load/unload peak current
      lulPeakCurrent = self.signed(servoData[LulPeakCurrent_IDX])*filteredMicroAmpPerBit*1.0/1000
      
      # calculate max motor dip error during load / unlaod         
      
      desiredMotorRPM = rpmGainCounts*1E6*1.0 / desiredCommCycleTime                              # unit is RPM,  target motor speed
      maxMotorDipTimeError = self.signed(servoData[MaxMotorDipError_IDX]) # unit is comm cycle time
      minMotorRPM = rpmGainCounts*1E6*1.0 / ( desiredCommCycleTime + maxMotorDipTimeError)        # unit is RPM,  actual min motor speed
      maxMotorDipRPMError = desiredMotorRPM - minMotorRPM                                         # unit is RPM,  speed error 
      
      # calculate load / unlaod peak velocity      
      lulPeakVelocity = self.signed(servoData[LulPeakVelocity_IDX])*1.0/bitsPerIps
      
      # calculate BEMF residual error 
      bemfResidualError = self.signed(servoData[BemfResidualError_IDX])
     
      # calculate BEMF cal gain
      bemfCalGain = servoData[BemfCalGain_IDX]
     
      respData = {}
      respData['LulPeakCurrent']        = lulPeakCurrent
      respData['LulPeakVelocity']       = lulPeakVelocity
      respData['MaxMotorSpeedDipError'] = maxMotorDipRPMError
      respData['BemfResidualError']     = bemfResidualError
      respData['BemfCalGain']           = bemfCalGain
      respData['LoadUnloadErrorCode']   = servoData[LoadUnloadErrorCode_IDX]      
      return cmdStatus, respData

   def checkHeadLoadWithoutDemodSync(self):
      BemfCalGain_IDX = 1
      BemfResidualError_IDX = 3
      LulPeakCurrent_IDX  = 5
      MaxMotorDipError_IDX = 6
      LulPeakVelocity_IDX = 7
      LoadUnloadErrorCode_IDX = 9
      filteredMicroAmpPerBit = self.signed(self.servoUtil.getServoRamDataByName('i16_FilteredMicroAmpPerBit'))
      rpmGainCounts = self.signed(self.servoUtil.getServoRamDataByName('i16_RPMGainCounts'))  
      desiredCommCycleTime = self.signed(self.servoUtil.getServoRamDataByName('u16_DesiredCommCycleTime'))
      bitsPerIps = self.signed(self.servoUtil.getServoRamDataByName('i16_BitsPerIps'))
      
      cmdStatus, servoData  = self.getLoadUnloadHeadData([0xF00,0], paramName = 'LoadHeadNonDemodSync_F00_0', timeout = 120, supressOutput = 0)
      #cmdStatus, diagStatus, servoData = self.issueServoCmd([0xF00,0], paramName = 'LoadHeadNonDemodSync_F00_0', timeout = 120, supressOutput = 0)

      specDict = {'LulPeakCurrentLimit'        :  -400, 
                  'MaxMotorSpeedDipErrorLimit' :  109,
                  'BemfCalGainLimit'           :  21000,
                 }
      passFailStatus,diagRespList,diagRespDict = self._checkLoadUnloadStatus(servoData, specDict, testState = 'CheckLoadHeadNonDemodSync', title = 'Load Head Without Demod Sync')
      ScriptComment(self.formatOutput.formatLoadUnloadWithoutDemodSyncOutput(servoData,'P_LOAD_HEAD_NONE_DEMOD_SYNC'), writeTimestamp = 0)
      import time
      time.sleep(10)
      motorState, motorStateDecode = self.getMotorState()
      objMsg.printMsg('--------------  Check Motor State Only  ----------------')
      objMsg.printMsg('       eMotorState : 0x%02X (%s)' % (motorState, motorStateDecode)) 
      if motorState == 0x00:
         ScrCmds.raiseException(14661, 'MotorState = 0(MOTOR_STOPPED) After Loading Head')
      if passFailStatus == FAIL:
         self.servoUtil.issueServoCmd([0xE00,0], paramName = 'UnloadHead_E00', timeout = 120, supressOutput = 0)
         if diagRespList[0]['PotentialCause'] == 'HDI_SPIN_DIP':
            ScrCmds.raiseException(11164, 'Head load failed')         
         ScrCmds.raiseException(14660, 'Head load failed')
      return cmdStatus
      
   def checkUnloadHead(self,):
      specDict = {'LulPeakCurrentLimit'        :  330,                                       
                  'MaxMotorSpeedDipErrorLimit' :  109,
                  'BemfCalGainLimit'           :  30000,}
      cmdStatus, servoData  = self.getLoadUnloadHeadData([0xE00,0], paramName= 'SpinDownMotor_E00', timeout = 120, supressOutput = 0)
      passFailStatus,diagRespList,diagRespDict = self._checkLoadUnloadStatus(servoData, specDict, testState = 'CheckUnloadHead', title = 'Spin Down Motor') 
      ScriptComment(self.formatOutput.formatLoadUnloadWithoutDemodSyncOutput(servoData,'P_UNLOAD_HEAD'), writeTimestamp = 0)
      if passFailStatus == FAIL:
         ScrCmds.raiseException(14665, 'Unload head failed')
      return cmdStatus
   def getMrResistance(self):
      import math
      MR_VOLTAGE_BIAS_IDX  = 5
      MR_RESISTANCE_IDX    = 6
      MR_CURRENT_BIAS_IDX  = 7
      mrResistacneList     = []
      mrVoltBiasList       = []
      mrCurrentBiasList    = []
      supressOutput = 0
      for lgcHead in xrange(self.dut.imaxHead):
         # set logical head to u16_DemodDestinationHead,  the servo code will auto convert it to physical head and set to preamp register 
         self.servoUtil.setServoRamDataBySymbolOffset('u16_DemodDestinationHead', lgcHead, maskValue = 0x0, accessType = 2, supressOutput = supressOutput) 
         cmdStatus, diagStatus, servoData = self.servoUtil.issueServoCmd([0x700,0x0,0x0,0x0],  paramName='Demod Reset', timeout = 60, supressOutput = supressOutput)
         cmdStatus, diagStatus, servoData = self.servoUtil.issueServoCmd([0x22F,0x0,0x0,0x0],  paramName='Measure Hd%d MR Res' % lgcHead, timeout = 60, supressOutput = supressOutput)
  
         mrResistance  = servoData[MR_RESISTANCE_IDX] & 0x0FFF
         mrVoltBias    = servoData[MR_VOLTAGE_BIAS_IDX] * 1.0 / math.pow(2,8)
         mrCurrentBias = servoData[MR_CURRENT_BIAS_IDX] * 1.0 / math.pow(2,14)
         # MR resistance = 0 & volt bias = 0 means the head does not exist, igore the data
         # must scan all heads, because for 4 heads drives, maybe physical head 0 is dummy head (balance plate instead of)
         if mrResistance>0 and mrVoltBias >0:
            mrResistacneList.append(mrResistance)
            mrVoltBiasList.append(mrVoltBias)
            mrCurrentBiasList.append(mrCurrentBias)
           
      dataRespDict = {}
      dataRespDict['MrResistance']  =  mrResistacneList  
      dataRespDict['MrVoltBias']    =  mrVoltBiasList  
      dataRespDict['MrCurrentBias'] =  mrCurrentBiasList  
      
      #   we need to update the numHeads according to the count of head with valid MR resistance 
      #
      #       For one Rosewoood7 1D drive that failed after download IMG_BIN.BIN. 
      #    u16_MaxHeadNumberSAP is 4 but actually only have 2 physical head, we only can get 2 valid  
      #    MR resistance value (other 2 heads' MR resistance is 0), like as below
      #
      #    --------------------------- Measure Head MR Resistance -------------------------------
      #             Logical Head           H0          H1          H2          H3         Spec
      #      MR Resistance (ohm) :      367.0       406.0         0.0 *       0.0 *     (200/800)
      #      MR Volage Bias (mV) :       99.0       109.5         0.0         0.0  
      #     MR Current Bias (mA) :      0.270       0.270       0.270       0.270  

      if self.dut.imaxHead != len(dataRespDict['MrResistance']):
         self.dut.imaxHead = len(dataRespDict['MrResistance'])
         objMsg.printMsg("Update drive's numHeads to %d" % self.dut.imaxHead )          
      return cmdStatus,dataRespDict

      
   def checkMrResistance(self, specDict = {}, enableDumpPreamp = False):
      passFailStatus = PASS
      cmdStatus,dataRespDict = self.getMrResistance()      

      physicalHeadTableAddr = self.servoUtil.getServoRamDataBySymbolOffset( 'u8_PhysicalHeadTable', accessType = 0, supressOutput = 0)
      if physicalHeadTableAddr & 0xFFFF != 0xFFFF:  # INVALID_SERVO_SYMBOL = 0x0000FFFF
         lgcToPhysHdMap = self.servoUtil.getServoRamDataBySymbolOffset( 'u8_PhysicalHeadTable', accessType = 1, numLocs = self.dut.imaxHead - 1, supressOutput = 0)
      else:
         lgcToPhysHdMap = range(self.dut.imaxHead)
     
      MrResistanceLimitRange = TP.mrBiasCal_321.get('RESISTANCE_RANGE', (200, 800))
      headStatusList = [ MrResistanceLimitRange!=None and self.isOutOfRange(res,MrResistanceLimitRange) or False for res in dataRespDict['MrResistance']]
      objMsg.printMsg('----------------- Measure Head MR Resistance ------------------')
      objMsg.printMsg('          Logical Head   %s       Spec'   % ''.join([('H%d  ' % i).rjust(12) for i in xrange(self.dut.imaxHead)]))  
      objMsg.printMsg('   MR Resistance (ohm) : %s     %s' 
                      % (''.join(['%10.1f %s' % (dataRespDict['MrResistance'][i],headStatusList[i] and '*' or ' ') for i in xrange(self.dut.imaxHead)]),
                         MrResistanceLimitRange!=None and '(%d/%d)' % (MrResistanceLimitRange[0],MrResistanceLimitRange[1]) or ' '))
      objMsg.printMsg('   MR Volage Bias (mV) : %s'   % ''.join(['%10.1f  ' % i for i in dataRespDict['MrVoltBias']]))
      objMsg.printMsg('  MR Current Bias (mA) : %s'   % ''.join(['%10.3f  ' % i for i in dataRespDict['MrCurrentBias']]))
      objMsg.printMsg('')
      try:
         ScriptComment(self.formatOutput.formatMrResistanceOutput(dataRespDict['MrResistance'],lgcToPhysHdMap),writeTimestamp=0)
      except: pass
      
      if sum(headStatusList)>0:
         ScrCmds.raiseException(14663, 'Resistance check fail') 
         
      return cmdStatus
   def run(self):
      if testSwitch.virtualRun:
         return
      self.checkMotor()
      self.checkMrResistance()
      for i in range(10):
         self.checkHeadLoadWithoutDemodSync()
         self.checkUnloadHead()
      self.checkMotor()
      self.checkMrResistance()
      
   def signed(self, value):
      if value > 0x7FFF:
         value = -(0xFFFF- value+1)
      return value
   def isOutOfRange(self,value,range):
      """
      Description : check if the value is out of range or not
      Parameter   : value - float/integer data need to check         
                    range - a list/tuple with min and max limit.  like as (minLimit, maxlimit)
      Return      : True  - out of limit range
                    False - within limit range  
      """
      return value<min(range) or value>max(range) and True or False
