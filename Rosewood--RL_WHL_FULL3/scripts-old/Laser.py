#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Test Parameters for Luxor programs - Grenada,
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Laser.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Laser.py#1 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
from ScrCmds import raiseException, CRaiseException
import struct
import Utility
import math
from Servo import CServoFunc
loop_count = 0
iop_saved  = 0
nothing = object() # a default value that will never conflict.

class CLaserInit(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = dict(params)
      depList = []
      CState.__init__(self, dut, depList)
      self.numHeads = self.dut.imaxHead
      self.numZones = self.dut.numZones
      from FSO import CFSO
      self.oFSO = CFSO()
      self.oSrvFunc = CServoFunc()
      if testSwitch.HAMR_LBC_ENABLED:
         self.dut.lbcEnabled = 1
      else:
         self.dut.lbcEnabled = 0


   #-------------------------------------------------------------------------------------------------------
   def run(self):

      self.oFSO.St(TP.prm_172_HamrPreampTable, spc_id=100)           #  Print initial laser current values
      self.ReadHamrServoDiag(spc_id=200)
      self.oFSO.St(TP.prm_172_HamrWorkingTable, spc_id=100)
      self.oFSO.St(TP.prm_172_HamrPreampTable, spc_id=100)
      self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').deleteIndexRecords(1)         #del file pointers
      self.dut.dblData.delTable('P011_SV_RAM_RD_BY_OFFSET', forceDeleteDblTable = 1)
      self.ReadHamrLbcSettings(spc_id=100)

      self.laser_bias_cal()                                                # Laser threshold current calibration
      self.oFSO.St(TP.prm_172_HamrPreampTable, spc_id=150)
      self.oFSO.St(TP.prm_172_HamrWorkingTable, spc_id=150)
      self.ReadHamrLbcSettings(spc_id=150)


      self.init_laser_cal()
      self.oFSO.saveRAPSAPtoFLASH()
      objPwrCtrl.powerCycle(5000,12000,10,30)

      self.oFSO.St(TP.prm_172_HamrWorkingTable, spc_id=100)
      self.oFSO.St(TP.prm_172_HamrPreampTable, spc_id=100)

      prm = TP.prm_172_display_AFH_adapts_summary.copy()
      prm['spc_id'] = 450     
      prm['CWORD1'] = 4
      self.oFSO.St(prm)

      prm = TP.prm_172_display_AFH_adapts_summary.copy()
      prm['spc_id'] = 455     
      prm['CWORD1'] = 52
      self.oFSO.St(prm)




   def init_laser_cal(self, SpcId=200, ErrorCode=10620):
      try:
         self.HamrLaserCal(TestMode='VGA', ErrCode=ErrorCode,minHtrDac=(TP.MinWrtHtClr,0,0,), spc_id=SpcId)
      except raiseException, e:
         if e.errCode == 14710 and retry < len(retry_list):
            SPFunc.ResetWriteTriplet(retry_list[retry])     # Update write triplet & re-run contact detect
         else:
            raiseException(e.errCode, e.errMsg)

   def ReadHamrLbcSettings(self, **kwargs):
      '''
      Read the HAMR LBC settings from RAP and SAP.

      SAP structure at symbol offset 568:          # Byte offset
         uint16   u16_MasterSwitch;                # 0
         uint8    u8_HardwareGain;                 # 2
         uint8    u8_HardwareLowPassFilter;        # 3
         float    fs_Kp;                           # 4
         float    fs_Ki;                           # 8

      '''
      SpcId = kwargs.get('spc_id', 1)
      self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').deleteIndexRecords(1)         #del file pointers
      self.dut.dblData.delTable('P011_SV_RAM_RD_BY_OFFSET', forceDeleteDblTable = 1)
      prm = TP.prm_011_RdLbcInfo.copy()
      prm['spc_id'] = SpcId
      self.oFSO.St(prm)
      LbcSapTbl = self.CrunchTable('P011_SV_RAM_RD_BY_OFFSET', 'RAM_ADDRESS', 'READ_DATA', [])

      ram_addrs = LbcSapTbl.keys()
      ram_addrs.sort()
      lbc_info = [hex(LbcSapTbl[addr])[2:] for addr in ram_addrs]
      
      for Hd in range(self.numHeads):
         for Zn in range(self.numZones):
            self.dut.dblData.Tables('P_HAMR_LBC_SETTINGS').addRecord({
                     'HD_LGC_PSN'               : Hd,
                     'DATA_ZONE'                : Zn,
                     'RAP_MASTER_SWITCH'        : 0,#ReadRapValue(HamrOfst + TS.HAMR_LBC_EN),
                     'SAP_MASTER_SWITCH'        : int(lbc_info[1]+lbc_info[0], 16),
                     'SAP_PD_HARDWARE_GAIN'     : int(lbc_info[2], 16),
                     'SAP_PD_LOW_PASS_FILTER'   : int(lbc_info[3], 16),
                     'SAP_LBC_KP'               : round(self.BytesToFloat(int(lbc_info[7]+lbc_info[6]+lbc_info[5]+lbc_info[4], 16)),5),
                     'SAP_LBC_KI'               : round(self.BytesToFloat(int(lbc_info[11]+lbc_info[10]+lbc_info[9]+lbc_info[8], 16)),5),
                     'RAP_MLCFCA'               : 0,#afhMlcfca,
                     'RAP_ITH_OFFSET'           : 0,#afhIthOffset,
                     'RAP_PD_TARGET'            : 0,#ReadRapValue(HamrOfst + TS.HAMR_PD_TGT),

            })
      objMsg.printDblogBin(self.dut.dblData.Tables('P_HAMR_LBC_SETTINGS'))

   def CheckMinClearance(self, **kwargs):
      HdMsk       = kwargs.get('hdMask',     0xFF)
      failSafe    = kwargs.get('failSafe',   False)
      MinHtrDac   = kwargs.get('minHtrDac',  (0,0,0,))   # Minimum DAC for applied WH/PH/RH
      printResults= kwargs.get('printResults',  True)   # Minimum DAC for applied WH/PH/RH
      SpcId       = kwargs.get('spc_id',     None)
      ZnMsk       = kwargs.get('znMask',     0x3FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF )  # Data zone mask (zones 0 - 149)

      # Read AFH information
      self.dut.dblData.Tables('P172_AFH_DH_WORKING_ADAPT').deleteIndexRecords(1)         #del file pointers
      self.dut.dblData.delTable('P172_AFH_DH_WORKING_ADAPT', forceDeleteDblTable = 1)

      prm = TP.prm_172_RdClr.copy()
      self.oFSO.St(prm)
      prm = TP.prm_172_PreampAdpt.copy()
      self.oFSO.St(prm)

      # Parse the working table data
      if 1: #proc.var.headType[:3] == 'RHO':
         HtrTblHdrs = ['WRITER_WRITE_HEAT','WRITER_PRE_HEAT','READER_READ_HEAT']    # RHO heads use dual heater mode
      else: 
         HtrTblHdrs = ['WRITER_WRITE_HEAT','WRITER_PRE_HEAT','WRITER_READ_HEAT']
      WrkngTbl = self.CrunchTable('P172_AFH_DH_WORKING_ADAPT', ['HD_LGC_PSN','DATA_ZONE'], HtrTblHdrs)
      # Check working heater DAC by head by zone
      for Hd, Zn in [(hd,zn) for hd in range(self.numHeads) for zn in range(self.numZones)]:
         if ((2**Hd) & HdMsk) and ((2**Zn) & ZnMsk):
            if (WrkngTbl[Hd,Zn][0] <= MinHtrDac[0]) or (WrkngTbl[Hd,Zn][1] <= MinHtrDac[1]) or (WrkngTbl[Hd,Zn][2] <= MinHtrDac[2]):
                  ScriptComment('Minimum Clearance Check Failed')
                  ScriptComment('(WrkngTbl[Hd,Zn][0] = %s  MinHtrDac[0] = %s '%(WrkngTbl[Hd,Zn][0],MinHtrDac[0]))
                  if failSafe: return 14710
                  RaiseException(14710, 'Min Clearance Failure')
      return 0
   #-------------------------------------------------------------------------------
   def ReadHamrServoDiag(self, **kwargs):
      '''
      Read the HAMR servo diagnostic information from SAP at symbol offset 567.
         float  fs_OutputAccumulator ;                            // Accumulate photodetector values
         float  fs_OutputAverage ;                                // Store photodetector average value
         float  fs_ErrorIntegral ;                                // Store control error
         uint16 u16_Status ;                          [0:1]       // Status variable, each bit has meaning
         uint16 u16_Unused1 ;                         [2:3]       // 16 bit pad
         ------------------------------------------------------------------
         uint32 u32_TrackForMaxiBias ;                [4:7]       // 20 bytes of HAMR diagnostics [16:35]
         uint32 u32_TrackForMaxiOp ;                  [8:11]
         uint32 u32_TrackForMaxiBiasAdjust ;          [12:15]
         uint8  u8_MaxCommandediBias ;                [16]
         uint8  u8_MaxCommandediOp ;                  [17]
         uint8  u8_MaxPositiveiBiasAdjust ;           [18]
         uint8  u8_MaxNegativeiBiasAdjust ;           [19]
         uint8  u8_MaxWHRM ;                          [20]
         uint8  u8_MaxWHWM ;                          [21]
         uint8  u8_MaxRHRM ;                          [22]
         uint8  u8_MaxRHWM ;                          [23]
         ------------------------------------------------------------------
         uint16 u16_NewMeasurement ;                  [24:25]      // Store new photodetector measurement
         uint16 u16_NewTestMeasurement ;              [26:27]      // Store secondary new photodetector measurement
         int16  i16_ControlEffort ;                   [28:29]      // Store computed laser bias current adjustment
         uint16 u16_CommandedThresholdCurrent ;       [30:31]      // Store commanded laser bias current
         uint16 u16_PhotodetectorTarget ;             [32:33]      // Store photodetector target value
         uint8  u8_MeasurementCounter ;               [34]         // Counter for number of photodetector measurements made

      '''
      SpcId = kwargs.get('spc_id', 1)

      self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').deleteIndexRecords(1)         #del file pointers
      self.dut.dblData.delTable('P011_SV_RAM_RD_BY_OFFSET', forceDeleteDblTable = 1)    #del RAM objects
      prm = TP.prm_011_RdHamrSvoDiag.copy()
      prm['spc_id'] = SpcId
      self.oFSO.St(prm)
      HamrDiagTbl = self.CrunchTable('P011_SV_RAM_RD_BY_OFFSET', 'RAM_ADDRESS', 'READ_DATA', [])
      ram_addrs = HamrDiagTbl.keys()
      ram_addrs.sort()
      diag_data = [hex(HamrDiagTbl[addr])[2:] for addr in ram_addrs]

      self.dut.dblData.Tables('P_HAMR_SERVO_LASER_CTRL').addRecord({
                        'OUTPUT_ACCUM'                : 0,  # round(BytesToFloat(int(diag_data[3]  + diag_data[2]  + diag_data[1] + diag_data[0], 16)),5),
                        'OUTPUT_AVG'                  : 0,  # round(BytesToFloat(int(diag_data[7]  + diag_data[6]  + diag_data[5] + diag_data[4], 16)),5),
                        'ERROR_INTEGRAL'              : 0,  # round(BytesToFloat(int(diag_data[11] + diag_data[10] + diag_data[9] + diag_data[8], 16)),5),
                        'STATUS'                      : int(diag_data[1]  + diag_data[0],  16),
                        'NEW_MSRMNT'                  : int(diag_data[25] + diag_data[24], 16),
                        'NEW_TEST_MSRMNT'             : int(diag_data[27] + diag_data[26], 16),
                        'CONTROL_EFFORT'              : int(diag_data[29] + diag_data[28], 16),
                        'CMD_THRSH_CURR'              : int(diag_data[31] + diag_data[30], 16),
                        'PD_TARGET'                   : int(diag_data[33] + diag_data[32], 16),
                        'MSRMNT_CNT'                  : int(diag_data[34], 16),
      })

      self.dut.dblData.Tables('P_HAMR_SERVO_DIAG_INFO').addRecord({
                        'MAX_IBIAS_CYL'         : int(diag_data[7]+diag_data[6]+diag_data[5]+diag_data[4], 16),
                        'MAX_IOP_CYL'           : int(diag_data[11]+diag_data[10]+diag_data[9]+diag_data[8], 16),
                        'MAX_IBIAS_ADJ_CYL'     : int(diag_data[15]+diag_data[14]+diag_data[13]+diag_data[12], 16),
                        'MAX_CMD_IBIAS'         : int(diag_data[16], 16),
                        'MAX_CMD_IOP'           : int(diag_data[17], 16),
                        'MAX_POS_IBIAS_ADJ'     : int(diag_data[18], 16),
                        'MAX_NEG_IBIAS_ADJ'     : int(diag_data[19], 16),
                        'MAX_WHRM'              : int(diag_data[20], 16),
                        'MAX_WHWM'              : int(diag_data[21], 16),
                        'MAX_RHRM'              : int(diag_data[22], 16),
                        'MAX_RHWM'              : int(diag_data[23], 16),
      })

   def PolyFit(self, DataDict, Order=2):
      '''
      Takes a dictionary containing data and finds a polynomial equation for the
      dictionary values as a function of the dictionary keys.
      @param <dictionary> DataDict - A dictionary of data measurements taken at each key.
         DataDict = { X0 :  Y0,
                      X1 :  Y1,
                      ...
                    }
      @param <integer>    Order    - Order of polynomial used to fit data.
      @return <tuple>     Coefs    - A tuple containing equation coefficients with
                                     highest order in position 0.
      '''
      numOfCols=0; numOfRows=0

      DataDict = dict([(x,y) for x,y in DataDict.items() if (type(x) in [int, float]) and (type(y) in [int, float])])

      N=0.0
      s1=0.0; s2=0.0; s3=0.0; s4=0.0
      t1=0.0; t2=0.0; t3=0.0
      for x in DataDict.keys():
         if DataDict[x]!=None:
            N=N+1
            s1=s1+x
            s2=s2+x**2
            s3=s3+x**3
            s4=s4+x**4
            t1=t1+float(DataDict[x])
            t2=t2+float(DataDict[x])*(x)
            t3=t3+float(DataDict[x])*(x**2)
      if Order==2:
         quadA=(N*s2*t3 - N*s3*t2 - s1*s1*t3 - s2*s2*t1 + s1*s2*t2 + s1*s3*t1)/(N*s2*s4 - N*s3*s3 - s1*s1*s4 - s2*s2*s2 + 2*s1*s2*s3)
         quadB=(N*s4*t2 - N*s3*t3 - s2*s2*t2 - s1*s4*t1 + s1*s2*t3 + s2*s3*t1)/(N*s2*s4 - N*s3*s3 - s1*s1*s4 - s2*s2*s2 + 2*s1*s2*s3)
         quadC=(s1*s3*t3 -s1*s4*t2 -s2*s2*t3 - s3*s3*t1 + s2*s3*t2 + s2*s4*t1)/(N*s2*s4 - N*s3*s3 - s1*s1*s4 - s2*s2*s2 + 2*s1*s2*s3)
         return (quadA, quadB, quadC)
      if Order==1:
         linA=(N*t2-s1*t1)/(N*s2-s1*s1)
         linB=(s2*t1-t2*s1)/(N*s2-s1*s1)
         return (linA, linB)
   #-------------------------------------------------------------------------------
   def InterpolatePolyFit(self, Rg, Coefs):
      '''
      Use a set of polynomial coefficients to interpolate data for all integer values
      that fall within a user-defined range
      @param <tuple>       Rg       - Range within which interpolation will be applied.
                                      Must contain two values in the form: (min, max).
      @param <tuple>       Coefs    - Polynomial Coefficients used for interpolation. Can
                                      be and size. Position 0 is the highest order coefficient.
      @return <dictionary> rtrnDict - A dictionary containing the interpolated data points.
      '''
      order = len(Coefs)-1
      if (len(Rg) != 2) or (Rg[0]>Rg[1]):
         RaiseException(11044, 'Invalid interpolation range. Rg=%s'%str(Rg))

      rtrnDict={}
      for x in range(Rg[0],Rg[1]+1):
         y = sum( [ Coefs[idx]*(x**(order-idx)) for idx in range(order+1) ] )
         rtrnDict[x] = y
      return rtrnDict

   #-------------------------------------------------------------------------------
   def ApplyCurveFit(self, msrdDta={}, **kwargs):
      dtaRng=(min(msrdDta.keys()),max(msrdDta.keys()))
      numOfCols=max([len(cols) for cols in msrdDta.values()])
      rtrnDict={}

      fitLoops=3           # Maximum number of outliers
      RmseDltaLimit=0.75   # Minimum improvement in curve fit error to be considered an outlier
      RmseLimit=1.0        # Minimum RMSE considered to be a good fit
      fitOrder=kwargs.get('fitOrder',2)
      if fitOrder not in [1,2]:
         RaiseException(11044, 'Curve fit to %s order polynomial is not supported'%fitOrder)

      for col in range(numOfCols):
         outliers=[]
         columnData = dict([ (x,ys[col],) for x, ys in msrdDta.iteritems() if len(ys)-1 >= col ])  # Select data for this column
         fltrDta = dict([ (x,y) for x,y in columnData.iteritems() if y!=None])                     # Remove bad data from dict.
         if len(fltrDta.keys()) <= fitOrder:
            ScriptComment('Too few data points in column %s to fit %s order polynomial'%(col, fitOrder))
            ScriptComment('msrdDta = %s'%str(msrdDta))
            ScriptComment('fltrDta = %s'%str(fltrDta))
            continue

         # Find a base value for RMSE
         baseFit = self.InterpolatePolyFit(dtaRng, self.PolyFit(fltrDta, Order=fitOrder))
         baseRMSE = math.sqrt(sum([(baseFit[zn]-fltrDta[zn])**2 for zn in fltrDta.keys()])/len(fltrDta.keys()))

         # Remove outliers
         for loop in range(fitLoops):        # Loop untill you have a good fit, or until you reach the max number of loops.
            outlier=-1; bestRMSE=9999
            if (baseRMSE < RmseLimit) or (len(fltrDta.keys())<fitOrder+1): break
            for x in fltrDta.keys():
               tempData = fltrDta.copy()
               tempData.pop(x)
               dataFit = self.InterpolatePolyFit(dtaRng, self.PolyFit(tempData, Order=fitOrder))  # Apply a curve fit for the filtered data over the entire data range
               RMSE = math.sqrt(sum([(dataFit[zn]-tempData[zn])**2 for zn in tempData.keys()])/len(tempData.keys()))
               if RMSE < bestRMSE:
                  bestRMSE = RMSE
                  outlier=x
            ScriptComment('Loop: %s  Outlier: %s  Base RMSE: %s  RMSE: %s'%(loop,outlier,baseRMSE,bestRMSE))
            if baseRMSE-bestRMSE>RmseDltaLimit and outlier!=-1:
               fltrDta.pop(outlier)
               ScriptComment('Outlier Removed: %s'%outlier)
               baseRMSE = bestRMSE
            else:
               break

         # Finally, apply curve fit to data set with outliers removed
         finalData = self.InterpolatePolyFit(dtaRng, self.PolyFit(fltrDta, Order=fitOrder))
         for zn, val in finalData.iteritems():
            if zn in rtrnDict.keys(): rtrnDict[zn].append(val)
            else: rtrnDict[zn]=[val]

      return rtrnDict

   def Listify(self, value):
      """Takes a list or non-list and returns either the list, or the length one list containing the value"""
      if isinstance(value, list):
         return value
      elif isinstance(value, tuple):
         return list(value)
      else:
         return [value]

   def BytesToFloat(self, int_type):
      '''
      Convert a 32-bit binary number (represented using an integer type) into a
      single precision floating point number.
      Ex. 0x3D4CCCCD --> 0.05
      '''
      temp = struct.pack('i', int_type)
      float_type = float(struct.unpack('f', temp)[0])

      return float_type

   #----------------------------------------------------------------------------
   def CrunchTable(self, dataTable, inputHeadings, outputHeadings, conditions={}, default=nothing):
      '''Get Data out of a dataTable and place into a dictionary.

      inputHeadings are the values of the table that will be used to key the output.
      - If this is a list or tuple, the keys of the output will be a coresponding tuple.

      outputHeadings are the values of the table that will be the values of the output.
      - If this is a list or tuple, the values of the output will be a coresponding list or tuple.

      conditions is a dictionary with keys equal to the heading, and values equal to the values
      allowed for that heading, the values can be either a value or list of values. Only rows of
      the dataTable that match all such pairs will be placed in the output dictionary.

      default can also be passed in to provide a return value if the dataTable doesn't actually exist.

      [ DEPRICATED:
      conditions are a set of heading/value pairs, only rows of the dataTable that match
      all such pairs will be placed in the output dictionary. ]

      Note: All values placed in the dataTable are passed to cm.CastDataType() before being entered
      into the table, this will convert strings that represent ints/floats to ints/floats.
      '''
      colDict = self.dut.dblData.Tables(dataTable).columnNameDict()
      objMsg.printMsg(" colDict %s "% (str(colDict) ))

      colCastDataType = colDict.copy()
      for heading in colCastDataType.keys():
         colCastDataType[heading] = '*'

      TableDataTypes = TP.pTableDataTypes.copy()

      if dataTable in TableDataTypes.keys():
         for col in TableDataTypes[dataTable].keys():
            colCastDataType[col] = TableDataTypes[dataTable][col]

      if isinstance(inputHeadings, (list, tuple)): # multiple inputs, key is a tuple
         inputFunc = lambda dataRow: tuple(self.CastDataType((dataRow[colDict[heading]], colCastDataType[heading])) for heading in inputHeadings)
      elif isinstance(inputHeadings, str): # single value
         inputFunc = lambda dataRow: self.CastDataType((dataRow[colDict[inputHeadings]],colCastDataType[inputHeadings]))
      else:
         raise TypeError('Invalid type for inputHeadings: %s'%type(inputHeadings))

      if isinstance(outputHeadings, (list, tuple)): # multiple outputs, maintain output type
         outType = type(outputHeadings) # maintain type
         outputFunc = lambda dataRow: outType(self.CastDataType((dataRow[colDict[heading]], colCastDataType[heading])) for heading in outputHeadings)
      elif isinstance(outputHeadings, str): # single value
         outputFunc = lambda dataRow: self.CastDataType((dataRow[colDict[outputHeadings]], colCastDataType[outputHeadings]))
      else:
         raise TypeError('Invalid type for outputHeadings: %s'%type(outputHeadings))

      if isinstance(conditions, list): # included for backward compatability - remove once everyone is using dicts
         for condition in conditions:
            if len(condition) != 2:
               raise ValueError('conditions must be a list of 2-tuples if it is a list')
         conditions = dict(conditions)
      objMsg.printMsg(" conditions %s "% (str(conditions) ))

      if isinstance(conditions, dict):
         matchConditions = lambda dataRow: not sum(self.CastDataType((dataRow[colDict[heading]], colCastDataType[heading])) not in self.Listify(value) for heading, value in conditions.items())
      else:
         raise TypeError('conditions must be a dictionary')

      return dict((inputFunc(dataRow), outputFunc(dataRow)) for dataRow in self.dut.dblData.Tables(dataTable).rowListIter() if matchConditions(dataRow))

   #----------------------------------------------------------------------------
   def GetTableInfo(self, tableName, row = None, col = None):

      try:
         table = self.dut.dblData.Tables( tableName ).tableDataObj()
         objMsg.printMsg(" table %s "% (str( table ) ))
         return self.CastDataType ( table[row][col] )
      except:
         objMsg.printMsg(" Exception: table %s "% (str(table) ))
         return None

   def convertStrToIntFloatStr(self, input):
      isHex   = lambda x:int(x,16)
      isInit  = lambda x:int(x,10)
      isFloat = lambda x:float(x)
      
      if not isinstance(input, str):
         return input
       
      if len(input)>2 and input[0:2] in ['0X','0x']:
         for start in range(3, len(input)):
            if input[start] != '0':
               break                    
         input = input[0:2] + input[start:len(input)]
      
      try:
         if input.isdigit():                               # int
            return isInit(input)
         else:
            return isHex(input)                            # hex?
      except:
         try:
            return isFloat(input)                          # float 
         except:       
            return input

   def CastDataType(self, value):
      if isinstance(value, tuple):
         value, valType = value
         TypeCast = { # dict of functions
            '*': lambda x: self.CastDataType(x), # use default CastDataType, for SPC_ID primarily
            'F': float,
            'H': lambda x: int(x, 16), # Hexadecimal
            'I': int,
            'V': str,
         }
         if valType not in TypeCast:
            RaiseException(11044, 'Invalid type (%s), not in %s'%(valType, list(TypeCast)))
         return TypeCast[valType](value)
      elif isinstance(value, str):
         try:
            return int(value)
         except:
            pass
         try:
            if value.startswith('0x') or value.startswith('0X'):
               return int(value, 16)
            else:
               raise AssertionError
         except:
            pass
       
         try:
            return float(value)
         except:
            pass
      return value

   #-------------------------------------------------------------------------------
   def SaveRestoreLaserDacs(self, SaveMode, **kwargs):
      DEBUG=0
      VALID_IOP=0

      # Get user inputs
      hdMask = kwargs.get('hdMask',0xFF)
      znMask = kwargs.get('znMask',0x3FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
      Multiplier = kwargs.get('Multiplier',1.0)
      saveToFlash       = kwargs.get('saveToFlash',   True)
      if SaveMode not in ['SAVE','RESTORE','INCREM']:
         raiseException(11044, 'Invalid test mode for save/restore function')
   
      # Read RAP
      #StrtOfst = TS.HamrRap28Offset - (TS.HamrRap28FrameSize*10)
      #BytLmt = TS.HamrRap28FrameSize*360

      #cm.pTables.pop('P172_RAP_TABLE',None)
      #self.dut.dblData.Tables('P172_RAP_TABLE').deleteIndexRecords(1)         #del file pointers
      #self.dut.dblData.delTable('P172_RAP_TABLE')
      #st([178], [], {'timeout': 600.0, 'LASER': [81, 0, 35], 'HEAD_RANGE': 1023, 'ZONE': 150, 'CWORD3': 7, 'BIT_MASK': (0, 1), 'CWORD2': 0, 'CWORD1': 512})

      """ Need to review
      self.oFSO.St(TP.prm_172_RdRap, Ofst32=StrtOfst, Lmt32=BytLmt, loadTables='P172_RAP_TABLE', suppressResults=not(DEBUG))

      for HdZn in [(hd,zn) for hd in range(self.numHeads) for zn in range(self.numZones) if (2**hd&hdMask) and (2**zn&znMask)]:
         # Calculate RAP offsets
         ReadFrames = 5*(SaveMode.upper() in ['RESTORE','INCREM'])
         SaveFrames = 5*(SaveMode.upper()=='SAVE')
         ReadRapOffset = TS.HamrRap28Offset + (TS.HamrRap28FrameSize*10*[HdZn[1],-1][HdZn[1]==35]) + (TS.HamrRap28FrameSize*(HdZn[0]+ReadFrames))
         SaveRapOffset = TS.HamrRap28Offset + (TS.HamrRap28FrameSize*10*[HdZn[1],-1][HdZn[1]==35]) + (TS.HamrRap28FrameSize*(HdZn[0]+SaveFrames))

         # Read Iop, Ith and IopRg from HAMR table
         Iop   = ReadRapValue(ReadRapOffset+TS.HAMR_IOP,     ReadRAP=False)
         IopRg = ReadRapValue(ReadRapOffset+TS.HAMR_IOP_RNG, ReadRAP=False)
         Ith   = ReadRapValue(ReadRapOffset+TS.HAMR_ITH,     ReadRAP=False)

         if SaveMode.upper()=='INCREM':
             Iop = int(Iop * Multiplier)
             if Iop > 255:
               IopRg = 1
               if proc.var.preampMfgr == 'TI': Iop = Iop - 125
               elif proc.var.preampMfgr == 'AGERE': Iop = Iop - 256
               else: raiseException(11044, 'Preamp Manufacturer Not Defined')

             # Sanity check for max value of Iop
             if Iop > 255: Iop = 255

         # Save laser settings for heads 0-4 to the RAP space reserved for heads 5-9
         if Iop not in [0x00,]:
            WriteRapValue(SaveRapOffset+TS.HAMR_IOP, Iop)
            VALID_IOP=1
         else: ScriptComment('Invalid IOP for Head %s Zone %s'%HdZn)


         if IopRg in [0, 1] and VALID_IOP: WriteRapValue(SaveRapOffset+TS.HAMR_IOP_RNG, IopRg)
         else: ScriptComment('Invalid IOP_RANGE for Head %s Zone %s'%HdZn)

         if Ith not in [0x00, 0xFF]: WriteRapValue(SaveRapOffset+TS.HAMR_ITH, Ith)
         else: ScriptComment('Invalid ITH for Head %s Zone %s'%HdZn)

      if saveToFlash:
         self.oFSO.St(TP.prm_178_SaveRapToFlash, suppressResults=True)

      if DEBUG:
         self.oFSO.St(TP.prm_172_RdRap, Ofst32=0x127C0, Lmt32=0x1C20)  # Read HAMR table from RAP
         self.GetLaserPowers()
      """
      #ScriptMessage('LASER DACS %sD'%SaveMode)
      objMsg.printMsg('LASER DACS %sD'%SaveMode)

   def SetLaserPowers(self, Ith, Iop, **kwargs):
      '''
      Using fixed offsets to index into RAP and write values for Ith and Iadd manually.
      @param <integer> Ith DAC value to set for laser threshold current.
      @param <integer> iAdd DAC value to set for laser add current.
      @param <integer> znMask A binary mask indicating which zones to save current dacs for.
                              A mask bit set to 1 means that laser values will be saved to RAP for that zone.
      @param <boolean> saveToFlash When set to False will update in RAM, when set to True, will save RAP to flash.
      @param <boolean> printMsg When set to False, messages will not be printed to result file.
      '''
      prm = TP.prm_178_WrtLsrCrnt.copy()

      # Check for input arguments
      if kwargs.get('head',None)!=None: hdMask=2**kwargs.get('head')
      elif kwargs.get('hdMask',None)!=None: hdMask=kwargs.get('hdMask')
      else: hdMask=0x00FF

      if kwargs.get('zone',None)!=None: 
         znMask=kwargs.get('zone') & 0x0FF
         znMask |= (znMask << 8 & 0xFF00)
      elif kwargs.get('znMask',None)!=None: znMask=kwargs.get('znMask')
      else: znMask=0x00FF

      if kwargs.get('printMsg',True):
         ScriptComment('\nUpdating laser current settings in RAP...')
         ScriptComment('Ith: %s\nIop: %s\nHdMask: %s\nZnMask: %s'%(Ith,Iop,hex(hdMask),hex(znMask)), writeTimestamp=0)

      # Check value of Ith. Do not update if invalid
      if (Ith == None):
         Ith = 0
         t178_Cwrd3 = 0x0003     # 0x04=I_THRESH, 0x02=I_OP_RANGE, 0x01=I_OP
      else:
         t178_Cwrd3 = 0x0007     # 0x04=I_THRESH, 0x02=I_OP_RANGE, 0x01=I_OP

      if (Ith < 0) or (Ith > TP.defaultLaserImax):
         raiseException(11044, 'Invalid value specified for I_TH: %s'%Ith)

      if kwargs.get('printMsg',True):
         ScriptComment('Cwrd3: %s'%hex(t178_Cwrd3), writeTimestamp=0)

      # Adjust Iop for Range Bit
      IopRg=0
      if Iop > 255:
         IopRg = 1

      # Sanity check for max value of Iop
      if Iop > 255: Iop = 255

      prm.update({
            'ZONE'              : znMask,
            'HEAD_RANGE'        : hdMask,
            'LASER'             : (Iop, IopRg, Ith),
            'CWORD3'            : t178_Cwrd3,
            })

      # Update Ith, Iop & IopRange
      self.oFSO.St(prm) 

      # Save RAP
      if kwargs.get('saveToFlash',0):
         self.oFSO.saveRAPSAPtoFLASH()
         if kwargs.get('printMsg',True): ScriptComment('Saving RAP to Flash...', writeTimestamp=0)

      if kwargs.get('printMsg',True): ScriptComment('RAP Update Complete!!', writeTimestamp=0)

   #----------------------------------------------------------------------------
   def laser_bias_cal(self):
      for Hd in range(self.numHeads):
         #AfhOfst = TP.AfhHdTblOfst + (Hd*TP.AfhHdTblFrmSz)
         #MfgOfst = TP.HamrTccMfgOfst + (Hd*TP.HamrTccMfgFrmSz)

         Ipd_25C = self.LaserBiasCal(Hd, spc_id=100, failSafe=True)
         objMsg.printMsg(" Ipd_25C %s "% (str(Ipd_25C) ))
         #if Ipd_25C!=None and proc.var.lbcEnabled and proc.var.rapFormatMinor==1 and not cm.GetConfigVar('ProcessForJHL', False) and (proc.var.headType not in ['RHO', 'RHO_Y6', 'RHO_K1', 'RHO_5W']):
         if Ipd_25C!=None and self.dut.lbcEnabled:
            # PD calibration passed, LBC enabled, RAP supports LBC, Not JHL process, Non-RHO head type
            objMsg.printMsg(" PD Gain Tuning ")
            LbcEnable = 1
            PdFilter = TP.LaserBiasParams['Fltr']                                   # Always use default filter setting
            MLCFCA = int(round(Ipd_25C))                                            # Inflection point in mA
            Ith = int(round( (Ipd_25C/TP.IthreshDac) + TP.LaserBiasParams['ThreshDacOfst'] ))

            PdGain, LbcGainKi = self.PdGainCalibration(Hd, Ith, Ipd_25C, spc_id=120) # Calibrate the PD and LBC gain settings
            PdTarget = self.MeasurePdTarget(Hd, PdGain, Ith, spc_id=130)

         else:    # LBC feature disabled or not supported
            ##proc.var.lbcEnabled = False
            objMsg.printMsg(" No PD Gain Tuning ")
            LbcEnable = 0; PdTarget = 0; LbcGainKi = 0;
            PdGain = TP.LaserBiasParams['Gain']
            PdFilter = TP.LaserBiasParams['Fltr']

            if Ipd_25C != None:
               MLCFCA = int(round(Ipd_25C))
               Ith = int(round( (Ipd_25C/TP.IthreshDac) + TP.LaserBiasParams['ThreshDacOfst'] )) # Convert to DACs for Ithresh. Subtract a fudge factor of 10 DAC (per Alfredo)
            else:
               MLCFCA = TP.LaserBiasParams['DfltLsrBias']                           # Default MLCFCA
               Ith = int(round( TP.LaserBiasParams['DfltLsrBias']/TP.IthreshDac))+TP.LaserBiasParams['ThreshDacOfst']  # Default I_TH (saved to RAP in DAC)

         ScriptComment('LBC Enabled: %s'%bool(LbcEnable))                        # Print settings to result file
         ScriptComment('MLCFCA: %s'%MLCFCA)
         ScriptComment('DBIAKAI: %s'%TP.LaserBiasParams['ThreshDacOfst'])
         ScriptComment('I_THRESH: %s'%Ith)
         ScriptComment('PD Gain: %s'%PdGain)
         ScriptComment('PD Filter: %s'%PdFilter)
         ScriptComment('PD Target: %s'%PdTarget)
         ScriptComment('LBC Ki: %s'%LbcGainKi)

         LbcGainKiBytes = self.FloatToBytes(LbcGainKi)                                    # Convert float type to 32-bit binary equivalent

         objMsg.printMsg('LbcGainKiBytes = %d' % (LbcGainKiBytes ))
         self.oSrvFunc.setServoSymbolRange( addrName ='LBC_GAIN', wrData = (LbcGainKiBytes&0xFFFF), offaddr = 8 )
         self.oSrvFunc.setServoSymbolRange( addrName ='LBC_GAIN', wrData = ((LbcGainKiBytes>>16)&0xFFFF), offaddr =10 )

         #self.oFSO.St(TP.prm_011_LbcGain, ExtdWrDta=PdGain,)                             # Save PD Gain setting to SAP
         prm = TP.prm_011_LbcGain.copy()
         prm['EXTENDED_WR_DATA'] = PdGain
         self.oFSO.St(prm)

         #self.oFSO.St(TP.prm_011_LbcFilter, ExtdWrDta=(PdFilter<<8),)                    # Save PD Filter setting to SAP
         prm = TP.prm_011_LbcFilter.copy()
         prm['EXTENDED_WR_DATA'] = (PdFilter<<8)
         self.oFSO.St(prm)

         #self.oFSO.St(TP.prm_011_LbcEnable, WrDta=LbcEnable)                             # Enable LBC in SAP
         prm = TP.prm_011_LbcEnable.copy()
         prm['WR_DATA'] = LbcEnable
         self.oFSO.St(prm)
         self.oFSO.saveRAPSAPtoFLASH()  

         # Program RAP...
         #Turn on LBC in RAP
         prm = TP.prm_178_hamr_mode.copy()
         prm['HAMR_MODE'] = int(LbcEnable)<<1
         self.oFSO.St(prm)

         prm = TP.prm_178_hamr_control.copy()
         prm['HAMR_CONTROL'] = int(LbcEnable)<<1
         self.oFSO.St(prm)

         #Set pd target output in RAP
         prm = TP.prm_178_hamr_pd_tgt_output.copy()
         prm['TARGET_PD_OUTPUT'] = int(round(PdTarget))
         self.oFSO.St(prm)

         #Display HAMR LBC setting in RAP
         self.oFSO.St(TP.prm_178_display_hamr_setting)

         self.SetMLCFCAandDBIATKAI(MLCFCA, int(TP.LaserBiasParams['ThreshDacOfst']))      # Update the MLCFCA and DBIAKAI to HAP.
         self.SetLaserPowers(Ith,0,hdMask=2**Hd)                                          # Update Ith in all zones
         self.oFSO.saveRAPtoFLASH()

         #Display HAMR LBC setting in RAP
         self.oFSO.St(TP.prm_178_display_hamr_setting)


   def SetLbcEnable(self, EnableLbc, **kwargs):
      '''
      Sets the LBC enable flags in RAP and SAP.

      @param <boolean> EnableLbc: Set to TRUE to enable LBC, set to FALSE to disable LBC.
      @param <boolean> saveToFlash: Set to False will update RAP and SAP in memory only,
                                    Set to True will save RAP and SAP to flash.
      @param <boolean> RapOnly: Set to TRUE will update the LBC enable flag in RAP only.
      @param <boolean> SapOnly: Set to TRUE will update the LBC enable flag in SAP only.
      SSDC: Currently no control of LBC in RAP yet.
      '''
      # Mask function input with LBC process flag
      EnableLbc &= self.dut.lbcEnabled

      # Update HAMR Preamp table in RAP
      if not kwargs.get('SapOnly',0):
         # Need to create Test 178 to program...
         #for Hd,Zn in [(hd,zn) for hd in range(proc.var.numHeads) for zn in range(self.numZones)]:
         #   HamrOfst = TP.HamrRap28Offset + (TP.HamrRap28FrameSize*[Zn,-1][Zn==35]*10) + (TP.HamrRap28FrameSize*Hd)
         #   WriteRapValue(HamrOfst + TP.HAMR_LBC_EN, int(EnableLbc)<<1)      # Enable LBC in all zones (bit 0x02)

         # Save RAP
         if kwargs.get('saveToFlash',0):
            self.oFSO.saveRAPtoFLASH()

      # Update LSB at symbol offset 568 in SAP
      if not kwargs.get('RapOnly',0):
         prm = TP.prm_011_LbcEnable.copy()
         prm['WR_DATA'] = int(EnableLbc)
         #self.oFSO.St(TP.prm_011_LbcEnable, WrDta=int(EnableLbc))
         self.oFSO.St(prm)

         # Save SAP
         if kwargs.get('saveToFlash',0):
            self.oFSO.saveSAPtoFLASH()

      ScriptComment('*\nSetting LBC enable flags to: %s\n*'%str(EnableLbc), writeTimestamp=0)


   #-------------------------------------------------------------------------------
   def SetMLCFCAandDBIATKAI(self, MLCFCA=0, DBIATKAI = 0):
      #st([178], [], {'C_ARRAY1': [0, 37, 0, 7, 0, 0, 0, 0, 13, 18], 'timeout': 600, 'CWORD1': (8704,), 'HEAD_RANGE': 0xff, 'CWORD2': (0,)})
      prm = TP.prm_178_set_MLCFCA_DBIATKAI.copy()
      prm['C_ARRAY1'][3] = 7              #region bit
      prm['C_ARRAY1'][8] = int(DBIATKAI)
      prm['C_ARRAY1'][9] = int(MLCFCA) 
      self.oFSO.St(prm)
      self.oFSO.saveRAPtoFLASH()

   def MeasureAllZoneBCI(self):
      self.dut.dblData.Tables('P172_ZONE_DATA').deleteIndexRecords(1)         #del file pointers
      self.dut.dblData.delTable('P172_ZONE_DATA')
      prm = TP.prm_172_RdZoneTable.copy()
      self.oFSO.St(prm) #self.oFSO.St(TP.prm_172_RdZoneTable, loadTables=['P172_ZONE_DATA'], spc_id=1, suppressResults=True)
      zoneTbl = self.CrunchTable('P172_ZONE_DATA', ['HD_LGC_PSN','DATA_ZONE'], ['PBA_TRK',],[('SPC_ID',1)])

      prm_250 = { 'test_num':250, 'RETRIES': 50, 'ZONE_POSITION': 198, 'spc_id': 22, 'MAX_ERR_RATE': -60, 'NUM_REGIONS_LIMIT':60,'TEST_HEAD': 255, 'NUM_TRACKS_PER_ZONE': 30, 'SKIP_TRACK': 200, 'TLEVEL': 0, 'MINIMUM': 8, 'ZONE_MASK_BANK': 0, 'timeout': 7200, 'ZONE_MASK_EXT': (0L, 0L), 'CWORD2': 0xc50, 'MAX_ITERATION': 65535, 'ZONE_MASK': (0L,2L), 'WR_DATA': 0, 'CWORD1': 385}

      self.oUtility = Utility.CUtility()
      
      for hd in range(0, self.numHeads) :
         for zn in range (0, self.numZones):
            testZones = [zn]
            prm_250['NUM_REGIONS_LIMIT'] = zoneTbl[(hd,zn)]
            MaskList = self.oUtility.convertListToZoneBankMasks(testZones)
            for bank, list in MaskList.iteritems():
               if list:
                  prm_250['ZONE_MASK_EXT'], prm_250['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(list)
                  if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                     prm_250['ZONE_MASK_BANK'] = bank
                  self.oFSO.St(prm_250) 

   #-------------------------------------------------------------------------------
   def GetLaserPowers(self,**kwargs):
      '''
      Displays the laser current DAC settings from RAP and the HAMR working table.
      Returns a dictionary containing the working laser DACs by head and zone.

      @param <integer> readFromWorkingTable   Default=False. Set to True, values will be read from the
                                              working laser table instead of DRAM.
      @param <integer> zone       Used when reading the laser currents for a single zone.
      @param <integer> znMask     A binary mask indicating which zones to read read data from.
                                  A mask bit set to 1 means that laser values will be returned
                                  for that zone.
      @param <boolean> printResults Set to False will disable printing the values read to the result file.
      @return <integer>,<integer>|<dictionary> If zone arg is passed in, return type is an integer pair.
      If znMask is passed in, return type is a dictionary. LpDict Contains the iThresh and iAdd
      value pair (as a tuple) indexed by head and zone.
      LpDict={
            Head : {
                     Zone : (iThresh, iAdd),
                     Zone : (iThresh, iAdd),
                     ...
                   }
            ...
          }
      '''
      #if cm.virtualMode: return (0,0)
      LpDict={}

      # Check for input arguments
      head = kwargs.get('head',None)
      if head!=None: hdMask=2**kwargs.get('head')
      elif kwargs.get('hdMask',None)!=None: hdMask=kwargs.get('hdMask')
      else: hdMask=0xFF

      zone = kwargs.get('zone',None)
      if zone!=None: znMask=2**kwargs.get('zone')
      elif kwargs.get('znMask',None)!=None: znMask=kwargs.get('znMask')
      else: znMask=0x3FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF  

      # Read HAMR tables
      self.dut.dblData.Tables('P172_PREAMP_HAMR_LASER').deleteIndexRecords(1)         #del file pointers
      self.dut.dblData.delTable('P172_PREAMP_HAMR_LASER')
      self.dut.dblData.Tables('P172_PREAMP_WORKING_LASER').deleteIndexRecords(1)         #del file pointers
      self.dut.dblData.delTable('P172_PREAMP_WORKING_LASER')
      prm = TP.prm_172_HamrPreampTable.copy()
      prm['spc_id'] = spc_id=kwargs.get('spc_id',None)
      self.oFSO.St(prm)

      prm = TP.prm_172_HamrWorkingTable.copy()
      prm['spc_id'] = spc_id=kwargs.get('spc_id',None)
      self.oFSO.St(prm)

      tableName = ['P172_PREAMP_HAMR_LASER', 'P172_PREAMP_WORKING_LASER'][kwargs.get('readFromWorkingTable', False)]
      HamrTbl = self.CrunchTable(tableName,('HD_LGC_PSN','DATA_ZONE'),('LASER_THRSHLD_CUR_DAC','LASER_OPERATING_CUR_DAC','CUR_RANGE_FLG'))

      # Read LDI values for each head/zone
      for Hd,Zn in [(hd,zn) for hd in range(self.numHeads) for zn in range(self.numZones) if (2**hd&hdMask) and (2**zn&znMask)]:

         # Get data from table
         Ithresh = HamrTbl[(Hd,Zn)][0]
         Iadd = HamrTbl[(Hd,Zn)][1]
         IaddRng = HamrTbl[(Hd,Zn)][2] & 0x01

         # Automatically apply range bit calculation to Iop
         Iadd = Iadd + (IaddRng*256)    # IaddRng is the 9th bit of Iop value, add 256 DAC Newly added

         # Add to return structure
         if Hd not in LpDict.keys(): LpDict[Hd]={}
         LpDict[Hd][Zn] = (Ithresh, Iadd)

      if head!=None and zone!=None:  # only read values for 1 head/zone
         return LpDict[head][zone][0], LpDict[head][zone][1]   # return Ithresh, Iadd
      else:
         return LpDict

   def GetLbcEnable(self):
      '''
      Reads the LBC enable flags in RAP and SAP. Returns true if LBC is enabled in
      both locations, else returns false.
      SSDC: For the moment just depend on SAP for LBC enable status.
      '''
      self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').deleteIndexRecords(1)         #del file pointers
      self.dut.dblData.delTable('P011_SV_RAM_RD_BY_OFFSET' , forceDeleteDblTable = 1)
      prm = TP.prm_011_RdLbcInfo.copy()
      prm['NUM_LOCS'] = 1
      self.oFSO.St(prm)
      #self.oFSO.St(TP.prm_011_RdLbcInfo, LocCnt=1, loadTables='P011_SV_RAM_RD_BY_OFFSET', suppressResults=True)
      LbcSapTbl = self.CrunchTable('P011_SV_RAM_RD_BY_OFFSET', 'RAM_ADDRESS', 'READ_DATA', [])

      ram_addrs = LbcSapTbl.keys()
      ram_addrs.sort()
      lbc_info = [hex(LbcSapTbl[addr])[2:] for addr in ram_addrs]

      lbc_sap_enable = int(lbc_info[1] + lbc_info[0], 16)

      lbc_rap_enable = lbc_sap_enable       # Temporary as we have not develop the command to display the RAP location of controlling the LBC.

      """
      if lbc_sap_enable:   # Don't need to do a bunch of RAP reads if SAP is disabled
         for Hd,Zn in [(hd,zn) for hd in range(self.numHeads) for zn in range(self.numZones)]:
            HamrOfst = TP.HamrRap28Offset + (TP.HamrRap28FrameSize*[Zn,-1][Zn==35]*10) + (TP.HamrRap28FrameSize*Hd)
            lbc_rap_enable = int(ReadRapValue(HamrOfst + TP.HAMR_LBC_EN) & 0x02) >> 1
            if not lbc_rap_enable: break  # Must be enabled in each zone
      else:
         lbc_rap_enable = 0
      """

      LbcEnabled = bool(lbc_sap_enable and lbc_rap_enable)
      ScriptComment('*\nCurrent LBC enable flags: SAP=%s RAP=%s --> LBC Enabled=%s\n*'%(bool(lbc_sap_enable),bool(lbc_rap_enable),LbcEnabled), writeTimestamp=0)
   

      return LbcEnabled


   def LaserBiasCal(self, Hd, **kwargs):
      #===== Define some math functions ===========================================
      Average    = lambda pts: float(sum(pts)/len(pts))
      DataCheck  = lambda data, val, wndw: len(set(data.keys()) & set(range(val-wndw,val+wndw+1))) > wndw*2
      Derivative = lambda data: dict([ (Iop, Average([ data[Iop]-data[Iop-1], data[Iop+1]-data[Iop] ]) ) for Iop in data.keys() if DataCheck(data, Iop, 1) ])
      MovingAvg  = lambda data, wndw: dict( [(Iop, Average([data[x] for x in range(Iop-wndw,Iop+wndw)])) for Iop in data.keys() if DataCheck(data, Iop, wndw) ])
      Sigmas     = lambda data, mean, sigma: dict([ (key, abs(val-mean)/sigma) for key,val in data.items() ])
      StdDev     = lambda data: math.sqrt(Average([(x-Average(data))**2 for x in data]))
      PrintPdErrMsg = lambda msg, fs: ScriptComment('<<< FAULT DETECTED - %s %s>>>'%(msg, ['','- FAIL SAFE ENABLED '][fs]))

      #----------------------------------------------------------------------------
      def MeasurePD(Hd, Zn, PdGain, **kwargs):
         ##########################################################################
         Incr              = kwargs.get('Incr',          TP.LaserBiasParams.get('Incr', 15))
         StdDevDlta        = kwargs.get('StdDevDlta',    TP.LaserBiasParams.get('StdDevDlta',1.5))
         TgtLdiRg          = kwargs.get('TgtLdiRg',      TP.LaserBiasParams['TgtLdiRg'])
         SpcId             = kwargs.get('spc_id',        TP.LaserBiasParams.get('spc_id',None))
         ZonePsn           = kwargs.get('ZnPsn',         TP.LaserBiasParams.get('ZnPsn', 100))
         ##########################################################################
         self.dut.dblData.Tables('P223_PHOTO_DIODE_DATA').deleteIndexRecords(1)         #del file pointers
         self.dut.dblData.delTable('P223_PHOTO_DIODE_DATA')
         IopMax = int(round( TgtLdiRg[1]/TP.IaddDac ))
         Iop=10; sig2=-1;                             #  Iop = 0 was causing an inflection , start at 10 to avoid

         objMsg.printMsg(" IopMax %d "% (IopMax ))
         objMsg.printMsg(" Iop %d "% (Iop ))

         #===== Sweep Iop and look for hook in PDV curve ==========================
         while Iop <= IopMax:
            #===== Sanity Check for script variables ==============================
            Incr = [Incr,15][Incr<1 or IopMax/Incr<2]
            IopLmt = min(Iop+Incr,IopMax)
            objMsg.printMsg("while: Incr %d "% (Incr ))
            objMsg.printMsg("while: IopLmt %d "% (IopLmt ))
            #===== Run T223 and collect PDV data ==================================
            prm = TP.prm_223_LaserIthCal.copy()
            prm.update({
                  'prm_name'        : 'P223_PHOTO_DIODE_DATA',
                  'spc_id'          : SpcId,
                  'TEST_HEAD'       : 255, #(Hd,Hd),
                  'ZONE_MASK_BANK'  : 0,
                  'ZONE_MASK_EXT'   : (0L, 0L),
                  'ZONE_MASK'       : (0L, 1L),  #'ZONE_MASK'        : T223_ZnMask,
                  'ZONE_POSITION'   : ZonePsn,
                  'PD_GAIN'         : (0, 100, PdGain),
                  'RANGE'           : (Iop, IopLmt),
                  #'HEAT_OVERRRIDE'  :5,          # for testing lc
                  })
            self.oUtility = Utility.CUtility()
            testZones = [Zn]
            objMsg.printMsg(" testZones %s "% (str(testZones) ))
            MaskList = self.oUtility.convertListToZoneBankMasks(testZones)
            objMsg.printMsg(" MaskList %s "% (str(MaskList) ))
            for bank, list in MaskList.iteritems():
               if list:
                  prm ['ZONE_MASK_EXT'], prm ['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(list)
                  if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                     prm ['ZONE_MASK_BANK'] = bank
                  self.oFSO.St(prm) #CProcess().St(prm_BPI_211)


            #===== Extract all T223 data ==========================================
            PdvTbl = self.CrunchTable('P223_PHOTO_DIODE_DATA', 'LASER_OPERATING_CUR_DAC', 'AVG_DIODE_VALUE', [('DATA_ZONE',Zn)])
            objMsg.printMsg(" PdvTbl %s "% (str(PdvTbl) ))
            if PdvTbl[max(PdvTbl.keys())] == 255:     # Stop sweeping if PDV saturates
               ScriptComment('PD signal saturated')
               break

            #===== Filter measurements until data has non-negative linear slope ===
            while len(PdvTbl)>max(Incr,10):   # This is to remove false triggers due to noise a low LDI.
               if self.PolyFit(PdvTbl,1)[0] >= 0: break
               PdvTbl.pop(min(PdvTbl.keys()))

            #===== Need a minimum of 10 data pts ==================================
            if len(PdvTbl.keys())<max(Incr,10) or IopLmt < (TgtLdiRg[0]/TP.IaddDac):
               Iop += Incr
               continue

            #===== Average of PD values should be above some min spec =============
            if Average(PdvTbl.values())<5:
               ScriptComment('Invalid PD data')
               break

            #===== Look for the inflection point in the PDV data ==================
            d1 = Derivative(PdvTbl)                                                             # Calculate the derivitave of photo diode voltage
            d2 = Derivative(d1)                                                                 # Calculate 2nd derivitive
            d2_abs_mean = Average([abs(x) for x in d2.values()])                                # Calculate the population mean
            d2_max = max(d2.values())                                                           # Find the max value of 2nd derivitive
            temp_inflect_pt = [key for key,val in d2.iteritems() if val >= d2_max][0]
            temp_pd_tbl = dict([ (iop,pdv) for iop,pdv in PdvTbl.iteritems() if iop <  temp_inflect_pt])
            ScriptComment('Inflection point candidate found at %s Iop DAC'%temp_inflect_pt)

            if ((temp_inflect_pt*TP.IaddDac) >= TgtLdiRg[0]) and ((temp_inflect_pt*TP.IaddDac) <= TgtLdiRg[1]) and len(temp_pd_tbl.keys())>2:
               m1 = self.PolyFit(temp_pd_tbl, Order=1)[0]                                            # Slope of the PD curve before the inflection point
               d2_thresh = (2*m1 + 1)/4                                                         # Calculate threshold of 2nd derivative to detect
               ScriptComment('m1=%s d2_thresh=%s'%(m1, d2_thresh))                           # slope change based on initial slope

               if ( d2_max > (3 * d2_abs_mean) ) and ( d2_max >= d2_thresh ):
                  inflect_pt = [key for key,val in d2.iteritems() if val >= d2_max][0]
                  return inflect_pt

            #===== Update Iop for next loop =================================
            Iop += Incr

         #===== If we get here, PDV cal has failed ================================
         ScriptComment('*** PDV Laser Cal Failed in Zone %s at Gain %s ***'%(Zn, PdGain))
         return None

      #----------------------------------------------------------------------------
      #############################################################################
      failSafe          = kwargs.get('failSafe',      False)
      PdGainLst         = kwargs.get('PdGainLst',   range(7,-1,-1))
      MaxCov            = kwargs.get('MaxCov',      TP.LaserBiasParams.get('MaxCov', 0.05))
      SpcId             = kwargs.get('spc_id',      TP.LaserBiasParams.get('spc_id',None))
      TgtLdiRg          = kwargs.get('TgtLdiRg',    TP.LaserBiasParams['TgtLdiRg'])
      ZnOrdr            = kwargs.get('ZnOrdr',      TP.LaserBiasParams['ZnOrdr'])
      FailZnSpec        = kwargs.get('FailZnSpec',  min(TP.LaserBiasParams.get('FailZnSpec', 2), len(ZnOrdr)))
      #############################################################################
      PdZnDta=[]; FinalPdv=None

      #===== Print Laser Cal Parameters ===========================================
      defaults = TP.LaserBiasParams
      defaults.update(kwargs)
      formatStr = "%22s %-20s : %s"
      objMsg.printMsg('Laser Bias Calibration')
      for prm, val in defaults.items():
         ScriptComment(formatStr%(' ', prm, str(val)), writeTimestamp=0)
      #objMsg.printMsg('')

      #===== Disable LBC during PD measurements ===================================
      DriveLbcEnabled = self.GetLbcEnable()
      ScriptComment('*\nIncoming LBC Enable Setting: "%s"\n*'%str(DriveLbcEnabled), writeTimestamp=0)
      if DriveLbcEnabled:
         ScriptComment('Disabling LBC for Laser Bias Calibration\n*', writeTimestamp=0)
         self.SetLbcEnable(False, saveToFlash=True)

      #===== Sweep gain settings in all test zones ================================
      for TstZn in ZnOrdr:
         for Gain in PdGainLst:   # Retry list for gain setting. Default from max to min (7-->0)
            InflectionPt = MeasurePD(Hd, TstZn, Gain, **kwargs)
            if (InflectionPt != None) and ((InflectionPt*TP.IaddDac) >= TgtLdiRg[0]) and ((InflectionPt*TP.IaddDac) <= TgtLdiRg[1]):
               PdZnDta.append(InflectionPt)
               break
         else:
            PdZnDta.append(-1)         # Exhausted all gain settings

         #===== Add p-table record ================================================
         self.dut.dblData.Tables('P_PHOTO_DIODE_SUMMARY').addRecord({
                                                            'SPC_ID'                : 1, #self.dut.objSeq.curRegSPCID,
                                                            'OCCURRENCE'            : self.dut.objSeq.getOccurrence(),
                                                            'SEQ'                   : self.dut.objSeq.curSeq,
                                                            'TEST_SEQ_EVENT'        : self.dut.objSeq.getTestSeqEvent(0),
                                                            'HD_PHYS_PSN'           : Hd,
                                                            'HD_LGC_PSN'            : Hd,
                                                            'DATA_ZONE'             : TstZn,
                                                            'PD_GAIN'               : Gain,
                                                            'IBIAS_LASER_CUR_DAC'   : PdZnDta[-1],
                                                            'IBIAS_LASER_CUR_MA'    : round(PdZnDta[-1]*TP.IaddDac,2),
                                                            })

      #===== Print p-table summary ================================================
      objMsg.printDblogBin(self.dut.dblData.Tables('P_PHOTO_DIODE_SUMMARY'))
      #ReadHamrServoDiag(spc_id=300) # Need review
      objPwrCtrl.powerCycle(5000,12000,10,30)  # Power cycle to restore IW settings after T223

      #===== Restore initial LBC setting ==========================================
      if DriveLbcEnabled:
         ScriptComment('*\nPD measurements complete. Restoring LBC Enable settings to: "%s"\n*'%str(DriveLbcEnabled), writeTimestamp=0)
         self.SetLbcEnable(DriveLbcEnabled, saveToFlash=True)

      #===== Reject bad data points based on COV ==================================
      PdZnDta = [x for x in PdZnDta if x>0]  # update fail spec to include outliers and failed zones
      if not PdZnDta:
         PrintPdErrMsg('PD cal failed in all zones', failSafe)
         if failSafe:
            return None
         else:
            raiseException(48556, 'PD cal failed in all zones')

      BaseCov = StdDev(PdZnDta)/Average(PdZnDta)
      ScriptComment('COV of data set = %s'%round(BaseCov,3))

      while len(PdZnDta) >= max(1, (len(ZnOrdr)-FailZnSpec)):
         if (BaseCov <= MaxCov): break
         MinCov=BaseCov; Outlier=-1
         for DataPt in PdZnDta:
            Temp = PdZnDta[:]
            Temp.remove(DataPt)
            TempCov = StdDev(Temp)/Average(Temp)
            if TempCov < MinCov:
               Outlier = DataPt
               MinCov = TempCov
         if Outlier != -1:
            PdZnDta.remove(Outlier)
            BaseCov = StdDev(PdZnDta)/Average(PdZnDta)
            ScriptComment('Removing Outlier Data Point %s --> COV = %s'%(Outlier,round(BaseCov,3)))
      else:
         PrintPdErrMsg('Zone Fail Limit Exceeded', failSafe)
         if failSafe:
            return None
         else:
            raiseException(48556, 'Zone Failure Limit Exceeded')

      FinalPdv = Average(PdZnDta)
      ScriptComment('PD Pick: %s'%FinalPdv)

      #===== Apply spec to final value ============================================
      if FinalPdv != None: # Make sure that final Ibias pick is within expected range
         if ((FinalPdv*TP.IaddDac) < TgtLdiRg[0]) or ((FinalPdv*TP.IaddDac) > TgtLdiRg[1]) or (FinalPdv==-1):
            PrintPdErrMsg('Final IBias value out of range', failSafe)
            if failSafe:
               return None
            else:
               raiseException(48556, 'Final IBias value out of range')
         else:
            ScriptComment('Calibration Complete!! IBias = %s mA (%s IOP DAC)'%(round(FinalPdv*TP.IaddDac,2),FinalPdv))
            return FinalPdv*TP.IaddDac

   def PdGainCalibration(self, Hd, Ith, InflectLdi, **kwargs):
      '''
      Calibrate the PD hardware gain and LBC controller gain settings.

      @param <integer> Hd = Logical head number to test
      @param <int> Ith = Ithresh setting used to determine sweep range (in Ith DACs)
      @param <float> InflectLdi = LDI setting where the inflection point in the PD curve occurrs (in mA)
      @param <bool> failSafe = FailSafe the PD Gain Calibration
      @param <float> MinPdSlopeSpec = Minimum allowable PD slope below the inflection point
      @param <integer> MaxLbcAdjust = Maximum amount that we assume LBC will adjust bias current in units of I_TH DACs

      @return <integer> PdGain = Calibrated gain value
      '''
      PrintPdErrMsg = lambda msg, fs: ScriptComment('<<< FAULT DETECTED - %s %s>>>'%(msg, ['','- FAIL SAFE ENABLED '][fs]))

      #############################################################################
      failSafe       = kwargs.get('failSafe',         False)
      LbcGainKiRg    = kwargs.get('LbcGainKiRg',      TP.LaserBiasParams.get('LbcGainKiRg', (0, 0.5)))
      MaxLbcAdjust   = kwargs.get('MaxLbcAdjust',     TP.LaserBiasParams.get('MaxLbcAdjust', 25))
      MinPdSlopeSpec = kwargs.get('MinPdSlopeSpec',   -0.5)
      PdFilter       = kwargs.get('PdFilter',         TP.LaserBiasParams.get('Fltr',3))
      PdGainRg       = kwargs.get('PdGainRg',         TP.LaserBiasParams.get('PdGainRg', (0, 7)))
      PdSaturation   = kwargs.get('PdSaturation',     255)
      SpcId          = kwargs.get('spc_id',           None)
      #############################################################################

      # Print input parameters
      formatStr = "%22s %-20s : %s"
      objMsg.printMsg('PD Gain Calibration')
      ScriptComment(formatStr%(' ', 'spc_id',         str(SpcId)),            writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'Hd',             str(Hd)),               writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'Ith',            str(Ith)),              writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'InflectLdi',     str(InflectLdi)),       writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'failSafe',       str(failSafe)),         writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'LbcGainKiRg',    str(LbcGainKiRg)),      writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'MaxLbcAdjust',   str(MaxLbcAdjust)),     writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'MinPdSlopeSpec', str(MinPdSlopeSpec)),   writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'PdFilter',       str(PdFilter)),         writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'PdGainRg',       str(PdGainRg)),         writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'PdSaturation',   str(PdSaturation)),     writeTimestamp=0)

      # Disable LBC during PD measurements
      DriveLbcEnabled = self.GetLbcEnable()
      ScriptComment('*\nIncoming LBC Enable Setting: "%s"\n*'%str(DriveLbcEnabled), writeTimestamp=0)
      if DriveLbcEnabled:
         ScriptComment('Disabling LBC for PD Hardware Gain Calibration\n*', writeTimestamp=0)
         self.SetLbcEnable(False, saveToFlash=True)

      InflectIop = int(round( InflectLdi/TP.IaddDac ))

      IthToIop = lambda ith: int(round( ith * TP.IthreshDac / TP.IaddDac ))     # Need a conversion from ITH DAC to IOP DAC since the ITH sweep in T223 is currently not functional
      StartIop = [IthToIop(Ith) - IthToIop(MaxLbcAdjust), 0][IthToIop(Ith) <= IthToIop(MaxLbcAdjust)]  # Set lower limit of 0
      EndIop = IthToIop(Ith) + IthToIop(MaxLbcAdjust)
      LbcGainKi=None; PdGainPick=None;
      ScriptComment('Inflection Iop = %s\nIop DAC Range = (%s, %s)'%(InflectIop, StartIop, EndIop), writeTimestamp=0)

      for PdGain in range(7,-1,-1):  # Sweep gain setting from high to low
         prm = TP.prm_172_HamrWorkingTable.copy()
         prm['spc_id'] = spc_id=kwargs.get('spc_id',None)
         self.oFSO.St(prm)
         prm_test223 = TP.prm_223_PhotoDetector.copy()
         prm_test223.update({
                  'prm_name'        : 'P223_PHOTO_DIODE_DATA',
                  'spc_id'          : SpcId,
                  'TEST_HEAD'       : 255,    #(Hd,Hd),
                  'TARGET_ITHRESH_CURRENT' : (0),
                  'ZONE_MASK_BANK'  : 0,
                  'ZONE_MASK_EXT'   : (0L, 0L),
                  'ZONE_MASK'       : (0L, 1L),  #'ZONE_MASK'        : T223_ZnMask,
                  'ZONE_POSITION'   : 100,
                  'PD_GAIN'         : (0, 100, PdGain),
                  'RANGE'           : (StartIop, EndIop),
                  })

         self.oUtility = Utility.CUtility()
         testZones = [70]
         MaskList = self.oUtility.convertListToZoneBankMasks(testZones)
         for bank, list in MaskList.iteritems():
            if list:
               prm_test223 ['ZONE_MASK_EXT'], prm_test223['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(list)
               if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                  prm_test223 ['ZONE_MASK_BANK'] = bank
               self.oFSO.St(prm_test223) 


         IopPdTbl = self.CrunchTable('P223_PHOTO_DIODE_DATA', 'LASER_OPERATING_CUR_DAC', 'AVG_DIODE_VALUE', [('GAIN',PdGain)])

         # Check for PD saturation
         if len([ pdv for pdv in IopPdTbl.values() if pdv >= PdSaturation ]) > 0:
            ScriptComment('*** PD Saturated at gain %s ***'%PdGain)
            continue

         # Convert Iop DACs to Ith DACs and separate data below and above inflection point
         IthPdLow = dict(tuple( [ (iop_dac*TP.IaddDac/TP.IthreshDac, pdv) for iop_dac, pdv in IopPdTbl.iteritems() if iop_dac < InflectIop ] ))
         IthPdHigh = dict(tuple( [ (iop_dac*TP.IaddDac/TP.IthreshDac, pdv) for iop_dac, pdv in IopPdTbl.iteritems() if iop_dac > InflectIop ] ))

         # Calculate the slope of the line before and after the PD infelction point - PDSlope = PDOutDAC/iBiasDAC
         PdSlopeLow = self.PolyFit(IthPdLow, Order=1)[0]
         PdSlopeHigh = self.PolyFit(IthPdHigh, Order=1)[0]
         ScriptComment('PD Slope Low = %s\nPD Slope High = %s'%(PdSlopeLow, PdSlopeHigh), writeTimestamp=0)

         # Apply spec to PD slope below inflection point
         if (PdSlopeLow < -0.5) or (PdSlopeHigh < (abs(PdSlopeLow)*3)):    # Probably need to add an RMSE spec here as well
            ScriptComment('*** PD slope out of spec ***')
            continue

         # Calculate the LBC controller gain from the linear PD slope after the inflection point --> LBCGainKi = 1 / ( X * PDSlope )
         LbcGainKi = 1./( 1.0 * PdSlopeHigh )
         PdGainPick = PdGain
         break

      else:
         # Failed to find gain setting that did not saturate
         objMsg.printMsg(" Photo Diode Gain Calibration Failed %s "% (str(failSafe) ))
         if failSafe:
            if DriveLbcEnabled:
               ScriptComment('*\nRestoring LBC Enable settings to: "%s"\n*'%str(DriveLbcEnabled), writeTimestamp=0)
               self.SetLbcEnable(DriveLbcEnabled, saveToFlash=True)
            return None, None
         else:
            raiseException(48556, 'Photo Diode Gain Calibration Failed')

      # Restore LBC Enable setting
      if DriveLbcEnabled:
         ScriptComment('*\nPD measurements complete. Restoring LBC Enable settings to: "%s"\n*'%str(DriveLbcEnabled), writeTimestamp=0)
         self.SetLbcEnable(DriveLbcEnabled, saveToFlash=True)

      # Apply spec to Ki gain calculated from PD signal
      if (LbcGainKi < min(LbcGainKiRg)) or (LbcGainKi > max(LbcGainKiRg)) or LbcGainKi==None:
         objMsg.printMsg("LBC Ki Gain Out Of Spec %s "% (str(failSafe) ))
         if failSafe:
            LbcGainKi = None
         else:
            raiseException(48556, 'LBC Ki Gain Out Of Spec')

      # Apply spec to PD hardware gain
      if (PdGainPick < min(PdGainRg)) or (PdGainPick > max(PdGainRg)) or (PdGainPick == None):
         objMsg.printMsg("PD Hardware Gain Out Of Spec %s "% (str(failSafe) ))
         if failSafe:
            PdGainPick = None
         else:
            raiseException(48556, 'PD Hardware Gain Out Of Spec')

      # Finished PD Gain Calibration
      fmtStr = '%12s%18s%13s'
      ScriptComment('\nP_LBC_PD_GAIN_CAL', writeTimestamp=0)
      ScriptComment(fmtStr%('HD_LGC_PSN','PD_HARDWARE_GAIN','LBC_GAIN_KI'), writeTimestamp=0)
      ScriptComment(fmtStr%(Hd, PdGainPick, round(LbcGainKi,5)), writeTimestamp=0)
      ScriptComment('\nPD Gain Calibration Complete')

      return PdGainPick, LbcGainKi

   def MeasurePdTarget(self, Hd, PdGain, Ith=None, **kwargs):
      '''
      Measure PD output DAC at a specified laser power and gain setting.

      @param <integer> Hd = Logical head to measure PD output.
      @param <integer> PdGain = PD hardware gain setting.
      @param <integer> Ith = Laser threshold current setting in I_TH DACs. Default
                             to value saved in RAP.

      @return <float> PdTarget = PDV output in PD DACs at the specified settings
      '''

      PrintPdErrMsg = lambda msg, fs: ScriptComment('<<< FAULT DETECTED - %s %s>>>'%(msg, ['','- FAIL SAFE ENABLED '][fs]))

      #############################################################################
      failSafe          = kwargs.get('failSafe',    False)
      PdTgtRg           = kwargs.get('PdTgtRg',     TP.LaserBiasParams.get('PdTgtRg', (0,255)))
      SpcId             = kwargs.get('spc_id',      None)
      Zn                = kwargs.get('Zn',          70)
      #############################################################################

      # Print input parameters
      formatStr = "%22s %-20s : %s"
      #InsertHeader('PD Target Measurement')
      ScriptComment('\nPD Target Measurement', writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'spc_id',   str(SpcId)),      writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'failSafe', str(failSafe)),   writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'Hd',       str(Hd)),         writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'Ith',      str(Ith)),        writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'PdGain',   str(PdGain)),     writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'PdTgtRg',  str(PdTgtRg)),    writeTimestamp=0)
      ScriptComment(formatStr%(' ', 'Zn',       str(Zn)),         writeTimestamp=0)

      # Disable LBC during PD measurements
      DriveLbcEnabled = self.GetLbcEnable()
      if DriveLbcEnabled:
         ScriptComment('*\nDisabling LBC for PD Target Measurement\n*', writeTimestamp=0)
         self.SetLbcEnable(False, saveToFlash=True)

      if Ith == None:
         Ith = self.GetLaserPowers(printResults=False)[Hd][Zn][0]

      ZoneMask = tuple([((2**Zn)>>(x*32))&0xFFFFFFFF for x in range(4)])

      self.dut.dblData.Tables('P223_PHOTO_DIODE_DATA').deleteIndexRecords(1)         #del file pointers
      self.dut.dblData.delTable('P223_PHOTO_DIODE_DATA')

      prm_test223 = TP.prm_223_PhotoDetector.copy()
      prm_test223.update({
               'prm_name'        : 'P223_PHOTO_DIODE_DATA',
               'spc_id'          : SpcId,
               'TEST_HEAD'       : 255,    #(Hd,Hd),
               'TARGET_ITHRESH_CURRENT' : (Ith),
               'ZONE_MASK_BANK'  : 0,
               'ZONE_MASK_EXT'   : (0L, 0L),
               'ZONE_MASK'       : (0L, 1L),  
               'ZONE_POSITION'   : 100,
               'PD_GAIN'         : (0, 100, PdGain),
               'RANGE'           : (0, 1),
               })

      self.oUtility = Utility.CUtility()
      testZones = [Zn]
      MaskList = self.oUtility.convertListToZoneBankMasks(testZones)
      for bank, list in MaskList.iteritems():
         if list:
            prm_test223['ZONE_MASK_EXT'], prm_test223['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(list)
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               prm_test223 ['ZONE_MASK_BANK'] = bank
            self.oFSO.St(prm_test223) 
      #self.oFSO.St(TP.prm_223_PhotoDetector, HdRg=(Hd,Hd), Gain=PdGain, TgtTstThrsh=(Ith), LsrCrrntRg=(0, 1), ZnMsk=ZoneMask, loadTables='P223_PHOTO_DIODE_DATA', spc_id=SpcId)

      PdTarget = self.GetTableInfo('P223_PHOTO_DIODE_DATA', 0, 'AVG_DIODE_VALUE')
      objMsg.printMsg(" Result: PdTarget %f "% (PdTarget))

      # Restore initial LBC Enable setting
      if DriveLbcEnabled:
         ScriptComment('*\nPD measurement complete. Restoring LBC Enable settings to: "%s"\n*'%str(DriveLbcEnabled), writeTimestamp=0)
         self.SetLbcEnable(DriveLbcEnabled, saveToFlash=True)

      # Verify PD Measurement did not fail
      if (PdTarget == None):
         objMsg.printMsg(" PD Target Measurement Failed %s "% (str(failSafe) ))
         if not failSafe:
            raiseException(48556, 'PD Target Measurement Failed')

      # Verify PD Target is within a valid range
      elif (PdTarget < min(PdTgtRg)) or (PdTarget > max(PdTgtRg)):
         objMsg.printMsg(" PD Target Out Of Spec %s "% (str(failSafe) ))
         if not failSafe:
            raiseException(48434, 'PD Target Out Of Spec')
         else:
            PdTarget = None

      return PdTarget

   def FloatToBytes(self, float_type):
      '''
      Convert a floating point number to its binary equivalent represented using
      an integer type.
      Ex. 0.05 --> 0x3D4CCCCD
      '''
      import struct
      temp = struct.pack('f', float_type)
      int_type = int(struct.unpack('i', temp)[0])
      return int_type

   def HamrLaserCal(self, TestMode, **kwargs):
      #if cm.virtualMode: return
      DEBUG = False

      global FullTrackWrites
      FullTrackWrites = 0
      #----------------------------------------------------------------------------
      def DltaBerMsmt(Hd, Zn, BerThrsh, Lmt10=(), SqzOfst=8, SqzWrites=1, WrtPtrn=()):
            if not Lmt10: Lmt10 =  TP.prm_229_NoSqueeze['Lmt10']# proc.ParmExtractor(TP.prm_229_NoSqueeze)['Lmt10']
            if not WrtPtrn: WrtPtrn = TP.prm_229_NoSqueeze['Pttrn'] #proc.ParmExtractor(TP.prm_229_NoSqueeze)['Pttrn']

            SqzBer=0.0; BerDlta=0.0
            NoSqzBer = SnglTrkBerMsmt(Hd, Zn, Lmt10, WrtPtrn)
            if NoSqzBer <= BerThrsh:
               SqzBer = SqzBerMsmt(Hd, Zn, Lmt10, SqzOfst, SqzWrites, WrtPtrn)
               BerDlta = SqzBer - NoSqzBer

            return NoSqzBer, SqzBer, BerDlta

      #----------------------------------------------------------------------------
      def FindCleanTrack(Hd,Zn):
            try:
               self.SetLaserPowers(0,0,head=Hd,zone=Zn,saveToFlash=False,printMsg=False)
               Lmt10Param = TP.prm_229_NoSqueeze['Lmt10'] #proc.ParmExtractor(TP.prm_229_NoSqueeze)['Lmt10']
               ZnPos = Lmt10Param[0]
               while ZnPos<200 and ZnPos>0:
                  NoSqzBer = SnglTrkBerMsmt(Hd,Zn,Lmt10Param)
                  if NoSqzBer > -1:
                     return Lmt10Param
                  else:
                     ZnPos-=1
                     Lmt10Param=list(Lmt10Param[1:])
                     Lmt10Param.insert(0,ZnPos)
                     Lmt10Param=tuple(Lmt10Param)
            except:
               ScriptComment('Unable to find unwritten track. Ok to continue.')

      #----------------------------------------------------------------------------
      def ReportFinalLaserData(ldiDict, msrdIntrp, PhysHd, LgcHd, SpcId):
            try:
               for zn, ldi in ldiDict.items():
                  Ith = [ldi[0],-1][type(ldi[0]) not in [int, float]]
                  Iop = [ldi[1],-1][type(ldi[1]) not in [int, float]]
                  Itotal = [(Ith*TP.IthreshDac)+(Iop*TP.IaddDac),-1][Iop<0]
                  self.dut.dblData.Tables('P_HAMR_LASER_CALIBRATION').addRecord({
                              'SPC_ID'                   : 1, #self.dut.objSeq.curRegSPCID,
                              'OCCURRENCE'               : self.dut.objSeq.getOccurrence(),
                              'SEQ'                      : self.dut.objSeq.curSeq,
                              'TEST_SEQ_EVENT'           : self.dut.objSeq.getTestSeqEvent(0),
                              'HD_PHYS_PSN'              : PhysHd,
                              'HD_LGC_PSN'               : LgcHd,
                              'DATA_ZONE'                : zn,
                              'MSRD_INTRPLTD'            : msrdIntrp,
                              'LASER_THRSHLD_CUR_DAC'    : Ith,
                              'LASER_OPERATING_CUR_DAC'  : Iop,
                              'LASER_TOTAL_CUR_MA'       : round(Itotal,2),
                  })
            except:
               ScriptComment('Unable to add record of laser cal data')
               ScriptComment('ldiDict = %s'%str(ldiDict))

      #----------------------------------------------------------------------------
      def SnglTrkBerMsmt(Hd,Zn,Lmt10=(),WrtPtrn=()):
            global FullTrackWrites

            T250_params = TP.prm_250_NoSqueeze.copy()# #T229_params = TP.prm_229_NoSqueeze.copy()#proc.ParmExtractor(TP.prm_229_NoSqueeze)

            NoSqzBer=0.0
            self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').deleteIndexRecords(1)         #del file pointers #self.dut.dblData.Tables('P229_ZN_CIRCUM_ERR_RATE').deleteIndexRecords(1)         #del file pointers
            self.dut.dblData.delTable('P250_ERROR_RATE_BY_ZONE') #self.dut.dblData.delTable('P229_ZN_CIRCUM_ERR_RATE')

            dtaZn = Zn #dtaZn = [Zn*2, Zn*2-1][Zn==35]

            self.oUtility = Utility.CUtility()
            testZones = [Zn]
            objMsg.printMsg(" testZones %s "% (str(testZones) ))
            MaskList = self.oUtility.convertListToZoneBankMasks(testZones)
            objMsg.printMsg(" MaskList %s "% (str(MaskList) ))
            for bank, list in MaskList.iteritems():
               if list:
                  T250_params['ZONE_MASK_EXT'], T250_params['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(list)
                  if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                     T250_params['ZONE_MASK_BANK'] = bank
                  SetFailSafe()
                  self.oFSO.St(T250_params)
                  ClearFailSafe()
            NoSqzBerTbl = self.CrunchTable('P250_ERROR_RATE_BY_ZONE', ('HD_LGC_PSN','DATA_ZONE'), 'RAW_ERROR_RATE',[]) #NoSqzBerTbl = self.CrunchTable('P229_ZN_CIRCUM_ERR_RATE', ('HD_LGC_PSN','DATA_ZONE'), 'ZONE_BER_MEAN',[])
            NoSqzBer = float(NoSqzBerTbl[(Hd,dtaZn)])

            FullTrackWrites += 6    # T229 FTW = 2 * WrtCnt * (1 + SqzWrtCnt + WrtGrdBnds)  <-- WrtGrdBnds = Cwrd1 & 0x10

            return NoSqzBer

      #----------------------------------------------------------------------------
      def SqzBerMsmt(Hd,Zn,Lmt10=(),SqzOfst=8,SqzWrites=1,WrtPtrn=()):
            global FullTrackWrites
            
            T250_params = TP.prm_250_Squeeze.copy()           #proc.ParmExtractor(TP.prm_229_Squeeze) #T229_params = TP.prm_229_Squeeze.copy()#proc.ParmExtractor(TP.prm_229_Squeeze)
            #if not Lmt10: Lmt10 = T229_params['Lmt10']
            #if not WrtPtrn: WrtPtrn = T229_params['Pttrn']
            SqzBer=0.0
            #cm.pTables.pop('P229_ZN_CIRCUM_ERR_RATE',None)
            self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').deleteIndexRecords(1)         #del file pointers #self.dut.dblData.Tables('P229_ZN_CIRCUM_ERR_RATE').deleteIndexRecords(1)         #del file pointers
            self.dut.dblData.delTable('P250_ERROR_RATE_BY_ZONE') #self.dut.dblData.delTable('P229_ZN_CIRCUM_ERR_RATE')
            dtaZn = Zn #dtaZn = [Zn*2, Zn*2-1][Zn==35]
            #ZoneMask = tuple([((2**dtaZn)>>(x*32))&0xFFFFFFFF for x in range(4)])
            #self.oFSO.St(TP.prm_229_Squeeze, HdRg=(Hd,Hd), ZnMsk=ZoneMask, Lmt10=Lmt10, Pttrn=WrtPtrn, SqzOfst=SqzOfst, SqzWrCnt=SqzWrites, loadTables='P229_ZN_CIRCUM_ERR_RATE', suppressResults=not(DEBUG), failSafe=True)
            self.oUtility = Utility.CUtility()
            testZones = [Zn]
            objMsg.printMsg(" testZones %s "% (str(testZones) ))
            MaskList = self.oUtility.convertListToZoneBankMasks(testZones)
            objMsg.printMsg(" MaskList %s "% (str(MaskList) ))
            for bank, list in MaskList.iteritems():
               if list:
                  T250_params['ZONE_MASK_EXT'], T250_params['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(list)
                  if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                     T250_params['ZONE_MASK_BANK'] = bank

                  SetFailSafe()
                  self.oFSO.St(T250_params)
                  ClearFailSafe()
            
            SqzBerTbl = self.CrunchTable('P250_ERROR_RATE_BY_ZONE', ('HD_LGC_PSN','DATA_ZONE'), 'RAW_ERROR_RATE',[]) #SqzBerTbl = self.CrunchTable('P229_ZN_CIRCUM_ERR_RATE', ('HD_LGC_PSN','DATA_ZONE'), 'ZONE_BER_MEAN',[])
            SqzBer = float(SqzBerTbl[(Hd,dtaZn)])

            FullTrackWrites += 12    # T229 FTW = 2 * WrtCnt * (1 + SqzWrtCnt + WrtGrdBnds)  <-- WrtGrdBnds = Cwrd1 & 0x10

            return SqzBer

      #----------------------------------------------------------------------------
      def AtiBerMsmt(Hd, Zn,):
            SqzBer=0.0
            self.dut.dblData.Tables('P051_ERASURE_BER').deleteIndexRecords(1)         #del file pointers
            self.dut.dblData.delTable('P051_ERASURE_BER')
            dtaZn = Zn #[Zn*2, Zn*2-1][Zn==35]
            prm = TP.prm_051_ATI.copy()
            prm.update({
               'ZONE'                       : Zn,
               'TEST_HEAD'                  : Hd,
            })
            self.oFSO.St(prm)  #self.oFSO.St(TP.prm_213_AtiCal, HdRg=(Hd,Hd), ZnMsk=ZoneMask, loadTables='P213_STE_SUMMARY', suppressResults=not(DEBUG), failSafe=True)
            SqzBerTbl = self.CrunchTable('P051_ERASURE_BER', ('HD_LGC_PSN','ZONE'), 'BITS_IN_ERROR_BER',[('NUM_WRT',prm['CENTER_TRACK_WRITES'])]) 
            objMsg.printMsg(" SqzBerTbl %s "% (str(SqzBerTbl) ))
            SqzBer = float(min(SqzBerTbl[(Hd,dtaZn)]))
            objMsg.printMsg(" SqzBer %s "% (str(SqzBer) ))

            return SqzBer

      #----------------------------------------------------------------------------
      def VgaLaserCal(Hd, Zn, kwargs):
            #######################################################################
            defaults          = TP.LaserCalParams
            BcktThrsh         = kwargs.get('BcktThrsh',     defaults['BcktThrsh'])
            CoarseIncr        = kwargs.get('CoarseIncr',    defaults['CoarseIncr'])
            DltaLmt           = kwargs.get('DltaLmt',       defaults['DltaLmt'])
            FineIncr          = kwargs.get('FineIncr',      defaults['FineIncr'])
            LsrCurRg          = kwargs.get('LsrCurRg',      defaults['LsrCurRg'])
            RtryCylIncr       = kwargs.get('RtryCylIncr',   defaults['RtryCylIncr'])
            RtryLmt           = kwargs.get('RtryLmt',       defaults['RtryLmt'])
            VgaOfstRg         = kwargs.get('VgaOfstRg',     defaults['VgaOfstRg'])
            SpcId             = kwargs.get('spc_id',        100)
            #######################################################################

            rtryCnt = 0
            #DebugPrint = proc.ParmExtractor(TP.prm_218_TA_LaserInit)['DbgPrt'][0]
            DebugPrint = 0
            LdiStepSz = (CoarseIncr<<8) | FineIncr

            

            #===== Find Test Cylinder =============================================
            #cm.pTables.pop('P172_ZONE_DATA',None)
            self.dut.dblData.Tables('P172_ZONE_DATA').deleteIndexRecords(1)         #del file pointers
            self.dut.dblData.delTable('P172_ZONE_DATA')
            prm = TP.prm_172_RdZoneTable.copy()
            self.oFSO.St(prm) #self.oFSO.St(TP.prm_172_RdZoneTable, loadTables=['P172_ZONE_DATA'], spc_id=1, suppressResults=True)
            zoneTbl = self.CrunchTable('P172_ZONE_DATA', ['HD_LGC_PSN','DATA_ZONE'], ['ZN_START_CYL','TRK_NUM',],[('SPC_ID',1)])
            testCyl = zoneTbl[(Hd,Zn)][0] + (zoneTbl[(Hd,Zn)][1]/2)
            objMsg.printMsg('VgaLaserCal:Hd %d Zn %d testCyl %d' % (Hd, Zn, testCyl))
            # Testing
            VgaOfstRg = 3000     # Testing
            LsrCurRg  = (25, 37) # Testing

            #===== Calculate Iop DAC Range ========================================
            Ith, Iop = self.GetLaserPowers(head=Hd, zone=Zn, printResults=False)
            IopDacRange = tuple([int((ldi-(Ith*TP.IthreshDac))/TP.IaddDac) for ldi in LsrCurRg])

           
            #===== Update T218 parameters =========================================
            #lsr_cal_param = proc.ParmExtractor(TP.prm_218_TA_LaserInit)
            lsr_cal_param = TP.prm_218_TA_LaserInit.copy()
            lsr_cal_param.update({
               'DELTA_LIMIT'                : DltaLmt,               #DltaLmt
               'TEST_HEAD'                  : 255,                   #(Hd,Hd),      # HdRg
               'RANGE'                      : IopDacRange,           # LsrCrrntRg
               'LASER_CURRENT_STEP_SIZE'    : LdiStepSz,             #LsrCrrntStepSz
               'SERVO_OFFSET_RANGE'         : (VgaOfstRg,int(VgaOfstRg*2.1)), # Rg
               'TARGET_ITHRESH_CURRENT'     : Ith,
               'PERCENT_LIMIT'              : BcktThrsh, #ThrshLmt
               'TARGET_CYLINDER'            : (testCyl>>16, testCyl),
               'DEBUG_PRINT'                : 0,
            })

            #===== Start T218 Cal =================================================
            while rtryCnt<=RtryLmt:
               if rtryCnt > 0:
                  DebugPrint = DebugPrint | 0x08   # Print all VGA sweeps durring retries

               self.oFSO.St(TP.spinupPrm_1)

               self.oFSO.St(lsr_cal_param)
               if 1:#testStat == 0: # Laser cal succeeded, return Iadd
                  Ithresh, Iadd = self.GetLaserPowers(head=Hd, zone=Zn, printResults=False)
                  return  Iadd
               else:
                  if rtryCnt>=RtryLmt:
                     ScriptComment('LASER CAL FAILED! - Maximum number of retries exceeded.')
                     return None
                  else:
                     objPwrCtrl.powerCycle(5000,12000,10,30)
                     testCyl=testCyl+RtryCylIncr
                     rtryCnt+=1

      #----------------------------------------------------------------------------
      def SqueezeLaserCal(Hd, Zn, kwargs):
            #######################################################################
            defaults          = TP.LaserCalParams
            FineIncr          = kwargs.get('FineIncr',      defaults['FineIncr'])
            LsrCurRg          = kwargs.get('LsrCurRg',      defaults['LsrCurRg'])
            MaxBerSpec        = kwargs.get('MaxBerSpec',    defaults['MaxBerSpec'])
            MaxBerThrsh       = kwargs.get('MaxBerThrsh',   defaults['MaxBerThrsh'])
            MaxDacDlta        = kwargs.get('MaxDacDlta',    defaults['MaxDacDlta'])
            SpcId             = kwargs.get('spc_id',        1)
            SqzPrcnt          = kwargs.get('SqzPrcnt',      defaults['SqzPrcnt'])
            SqzWrtCnt         = kwargs.get('SqzWrtCnt',     defaults['SqzWrtCnt'])
            WrtPttrn          = kwargs.get('WrtPttrn',      ())
            ZnPsn             = kwargs.get('ZnPsn',         defaults['ZnPsn'])
            #######################################################################
            objMsg.printMsg('SqueezeLaserCal: Zone %s'% str(Zn))
            #===== Initialize variables ===========================================
            dtaZn = Zn               #[Zn*2, Zn*2-1][Zn==35]
            Lmt10Param = 0 #Lmt10Param = tuple([[x,ZnPsn][Lmt10.index(x)==0] for x in Lmt10])
            BestSqz=0; FinalIop=0; SqzDltaQueue=[]; NoSqzBerBsln=0.0

            #===== Iop Sweep Variables ============================================
            Ith, Iop = self.GetLaserPowers(head=Hd, zone=Zn, printResults=False)
            IopMax = int((LsrCurRg[1]-(Ith*TP.IthreshDac))/TP.IaddDac)

            #===== Set IOP in DRAM RAP ======================================
            self.SetLaserPowers(None, Iop, head=Hd, zone=Zn, saveToFlash=False, printMsg=False)

            #===== Read working heater DAC ========================================
            self.dut.dblData.Tables('P172_AFH_DH_WORKING_ADAPT').deleteIndexRecords(1)         #del file pointers
            self.dut.dblData.delTable('P172_AFH_DH_WORKING_ADAPT')

            #===== Baseline BER at current LDI ====================================
            SqzBerBsln = SqzBerMsmt(Hd, Zn, Lmt10Param, int(round(SqzPrcnt*2.56)), SqzWrtCnt, WrtPttrn)    # 12 FTW

            WrkngTbl = self.CrunchTable('P172_AFH_DH_WORKING_ADAPT', ('HD_LGC_PSN','DATA_ZONE'), 'WRITER_WRITE_HEAT', [('SPC_ID',1)])
            physHdMap = self.CrunchTable('P172_AFH_DH_WORKING_ADAPT','HD_LGC_PSN','HD_PHYS_PSN')                                         # Logical to Physical head map

            if SqzBerBsln >=0:
               NoSqzBerBsln = SnglTrkBerMsmt(Hd, Zn, Lmt10Param, WrtPttrn)                      # 6 FTW
            FinalIop = Iop
            BaseIop = Iop
            BestSqz = SqzBerBsln



            #===== Add data to table ==============================================
            self.dut.dblData.Tables('P_FINE_LASER_CAL').addRecord({
            #cm.AddPtableRecord('P_FINE_LASER_CAL', spcId=SpcId, addRecord = {
                  'SPC_ID'                   : 1, #self.dut.objSeq.curRegSPCID,
                  'OCCURRENCE'               : self.dut.objSeq.getOccurrence(),
                  'SEQ'                      : self.dut.objSeq.curSeq,
                  'TEST_SEQ_EVENT'           : self.dut.objSeq.getTestSeqEvent(0),
                  'HD_PHYS_PSN'              : physHdMap[Hd],
                  'HD_LGC_PSN'               : Hd,
                  'DATA_ZONE'                : Zn,
                  'LASER_THRSHLD_CUR_DAC'    : Ith,
                  'LASER_OPERATING_CUR_DAC'  : Iop,
                  'WORKING_WRWH_DAC'         : WrkngTbl[(Hd,dtaZn)],
                  'SNGL_TRK_BER'             : NoSqzBerBsln,
                  'SQZ_TRK_BER'              : SqzBerBsln,
                  'BER_DELTA'                : SqzBerBsln-NoSqzBerBsln,
                  'SWEEP_MODE'               : 'BASELINE',
                  'LDI_UPDATE_FLAG'          : 0,
            })

            #===== Increasing Sweep of IOP ========================================
            if not( (NoSqzBerBsln<= -2.0 ) and (SqzBerBsln>=0) ):
               while Iop < IopMax:
                  #===== Set IOP in DRAM RAP ======================================
                  Iop+=FineIncr
                  self.SetLaserPowers(None, Iop, head=Hd, zone=Zn, saveToFlash=False, printMsg=False)

                  self.dut.dblData.Tables('P172_AFH_DH_WORKING_ADAPT').deleteIndexRecords(1)         #del file pointers
                  self.dut.dblData.delTable('P172_AFH_DH_WORKING_ADAPT')

                  #===== Measure BER ==============================================
                  SqzBer = SqzBerMsmt(Hd, Zn, Lmt10Param, int(round(SqzPrcnt*2.56)), SqzWrtCnt, WrtPttrn)     # 12 FTW

                  #===== Read working heater DAC ==================================
                  WrkngTbl = self.CrunchTable('P172_AFH_DH_WORKING_ADAPT', ('HD_LGC_PSN','DATA_ZONE'), 'WRITER_WRITE_HEAT', [('SPC_ID',1)])

                  #===== Check for best squeezed BER ==============================
                  LdiUpdate=0
                  if SqzBer < BestSqz:
                     BestSqz = SqzBer
                     FinalIop = Iop
                     LdiUpdate = 1

                  #===== Add data to table ========================================
                  self.dut.dblData.Tables('P_FINE_LASER_CAL').addRecord({
                        'SPC_ID'                   : 1, #self.dut.objSeq.curRegSPCID,
                        'OCCURRENCE'               : self.dut.objSeq.getOccurrence(),
                        'SEQ'                      : self.dut.objSeq.curSeq,
                        'TEST_SEQ_EVENT'           : self.dut.objSeq.getTestSeqEvent(0),
                        'HD_PHYS_PSN'              : physHdMap[Hd],
                        'HD_LGC_PSN'               : Hd,
                        'DATA_ZONE'                : Zn,
                        'LASER_THRSHLD_CUR_DAC'    : Ith,
                        'LASER_OPERATING_CUR_DAC'  : Iop,
                        'WORKING_WRWH_DAC'         : WrkngTbl[(Hd,dtaZn)],
                        'SNGL_TRK_BER'             : 1.0,
                        'SQZ_TRK_BER'              : SqzBer,
                        'BER_DELTA'                : SqzBer-BestSqz,    # Delta from best BER
                        'SWEEP_MODE'               : 'SQZ_INCR',
                        'LDI_UPDATE_FLAG'          : LdiUpdate,
                  })

                  #===== Make sure we do not exceed maximum allowed change in IOP =
                  if (SqzBer>MaxBerThrsh) and  (abs(Iop-BaseIop)>MaxDacDlta):
                     ScriptComment('Max IOP DAC change limit exceeded.')
                     break

                  #===== Stop increasing Iop if we exceed Min Clearance ===========
                  if WrkngTbl[(Hd,dtaZn)]<=0:
                     objMsg.printMsg('Min Clearance Reached')
                     break

                  #===== 
                  if SqzBer > 0:
                     NoSqzBer = SnglTrkBerMsmt(Hd, Zn, Lmt10Param, WrtPttrn)                      
                     if NoSqzBer  <=  -2.0: # On track must be reasonable good.
                        objMsg.printMsg('Iop too high for ATI.')
                        break

                  #===== Check for 3 consecutive measurments where squeeze BER is worse than best BER
                  if SqzBer<MaxBerThrsh: SqzDltaQueue.insert(0,SqzBer-BestSqz)
                  if len(SqzDltaQueue)>3: SqzDltaQueue.pop()
                  if len([x for x in SqzDltaQueue if x>0]) == len(SqzDltaQueue) and len(SqzDltaQueue)>=3: break

            #===== Decreasing Sweep of IOP ========================================
            Iop = FinalIop
            SqzDltaQueue=[]
            while (Iop-FineIncr) >= 0:
               #===== Set IOP in DRAM RAP ======================================
               Iop-=FineIncr
               self.SetLaserPowers(None, Iop, head=Hd, zone=Zn, saveToFlash=False, printMsg=False)

               self.dut.dblData.Tables('P172_AFH_DH_WORKING_ADAPT').deleteIndexRecords(1)                   #del file pointers
               self.dut.dblData.delTable('P172_AFH_DH_WORKING_ADAPT')

               #===== Measure BER ==============================================
               SqzBer = SqzBerMsmt(Hd, Zn, Lmt10Param, int(round(SqzPrcnt*2.56)), SqzWrtCnt, WrtPttrn)     # 12 FTW

               #===== Read working heater DAC =====================================
               WrkngTbl = self.CrunchTable('P172_AFH_DH_WORKING_ADAPT', ('HD_LGC_PSN','DATA_ZONE'), 'WRITER_WRITE_HEAT', [('SPC_ID',1)])

               #===== Check for best squeeze BER ==================================
               LdiUpdate=0
               if SqzBer < BestSqz:
                  BestSqz = SqzBer
                  FinalIop = Iop
                  LdiUpdate = 1

               #===== Add data to table ===========================================
               self.dut.dblData.Tables('P_FINE_LASER_CAL').addRecord({
               #cm.AddPtableRecord('P_FINE_LASER_CAL', spcId=SpcId, addRecord = {
                     'SPC_ID'                   : 1, #self.dut.objSeq.curRegSPCID,
                     'OCCURRENCE'               : self.dut.objSeq.getOccurrence(),
                     'SEQ'                      : self.dut.objSeq.curSeq,
                     'TEST_SEQ_EVENT'           : self.dut.objSeq.getTestSeqEvent(0),
                     'HD_PHYS_PSN'              : physHdMap[Hd],
                     'HD_LGC_PSN'               : Hd,
                     'DATA_ZONE'                : Zn,
                     'LASER_THRSHLD_CUR_DAC'    : Ith,
                     'LASER_OPERATING_CUR_DAC'  : Iop,
                     'WORKING_WRWH_DAC'         : WrkngTbl[(Hd,dtaZn)],
                     'SNGL_TRK_BER'             : 1.0,
                     'SQZ_TRK_BER'              : SqzBer,
                     'BER_DELTA'                : SqzBer-BestSqz,    # Delta from best BER
                     'SWEEP_MODE'               : 'SQZ_DECR',
                     'LDI_UPDATE_FLAG'          : LdiUpdate,
               })

               #===== Check for 3 consecutive measurments where squeeze BER is worse than best BER
               SqzDltaQueue.insert(0,SqzBer-BestSqz)
               if len(SqzDltaQueue)>3: SqzDltaQueue.pop()
               if len([x for x in SqzDltaQueue if x>0]) == len(SqzDltaQueue) and len(SqzDltaQueue)>=3: break

            #===== Print Table ====================================================
            #cm.WritePtable('P_FINE_LASER_CAL')
            objMsg.printDblogBin(self.dut.dblData.Tables('P_FINE_LASER_CAL'))
            ScriptComment('Iop Pick: %s'%FinalIop)
            ScriptComment('Best BER: %s'%BestSqz)

            #===== Check BER Spec =================================================
            if (BestSqz > MaxBerSpec) or (FinalIop<=FineIncr):
               ScriptComment('LASER CAL FAILED! - Minimum BER limit not met. Hd=%s Zn=%s BER=%s'%(Hd,Zn,BestSqz))
               return None
            else:
               self.SetLaserPowers(None, FinalIop, head=Hd, zone=Zn, saveToFlash=False, printMsg=False)
               return FinalIop

      #----------------------------------------------------------------------------
      def AtiLaserCal(Hd, Zn, kwargs):
            #######################################################################
            defaults          = TP.LaserCalParams
            FineIncr          = kwargs.get('FineIncr',      defaults['FineIncr'])
            LsrCurRg          = kwargs.get('LsrCurRg',      defaults['LsrCurRg'])
            MaxBerSpec        = kwargs.get('MaxBerSpec',    defaults['MaxBerSpec'])
            MaxBerThrsh       = kwargs.get('MaxBerThrsh',   defaults['MaxBerThrsh'])
            MaxDacDlta        = kwargs.get('MaxDacDlta',    defaults['MaxDacDlta'])
            SpcId             = kwargs.get('spc_id',        1)
            SqzPrcnt          = kwargs.get('SqzPrcnt',      defaults['AtiSqzPrcnt'])
            SqzWrtCnt         = kwargs.get('SqzWrtCnt',     defaults['AtiWrtCnt'])
            ZnPsn             = kwargs.get('ZnPsn',         defaults['ZnPsn'])
            #######################################################################
            #===== Initialize variables ===========================================
            dtaZn = [Zn*2, Zn*2-1][Zn==35]
            BestSqz=0; FinalIop=0; SqzDltaQueue=[]; NoSqzBerBsln=0.0;SqzBer=0;ImproveBer=0;DecBer=0

            #===== Iop Sweep Variables ============================================
            Ith, Iop = self.GetLaserPowers(head=Hd, zone=Zn, printResults=False)
            IopMax = int((LsrCurRg[1]-(Ith*TP.IthreshDac))/TP.IaddDac)

            #===== Set IOP in DRAM ================================================
            self.SetLaserPowers(None, Iop, head=Hd, zone=Zn, saveToFlash=False, printMsg=False)

            #===== Read working heater DAC ========================================
            self.dut.dblData.Tables('P172_AFH_DH_WORKING_ADAPT').deleteIndexRecords(1)         #del file pointers
            self.dut.dblData.delTable('P172_AFH_DH_WORKING_ADAPT')
            prm = TP.prm_172_display_AFH_adapts_summary.copy()
            prm['spc_id'] = 1     
            prm['CWORD1'] = 4
            self.oFSO.St(prm)
            WrkngTbl = self.CrunchTable('P172_AFH_DH_WORKING_ADAPT', ('HD_LGC_PSN','DATA_ZONE'), 'WRITER_WRITE_HEAT', [('SPC_ID',1)])
            physHdMap = self.CrunchTable('P172_AFH_DH_WORKING_ADAPT','HD_LGC_PSN','HD_PHYS_PSN')          # Logical to Physical head map

            #===== Baseline BER at current LDI ====================================
            SqzBerBsln = AtiBerMsmt(Hd, Zn,)
            FinalIop = Iop
            BaseIop = Iop
            BestSqz = SqzBerBsln

            #===== Add data to table ==============================================
            self.dut.dblData.Tables('P_FINE_LASER_CAL').addRecord({
            #cm.AddPtableRecord('P_FINE_LASER_CAL', spcId=SpcId, addRecord = {
                  'SPC_ID'                   : 1, #self.dut.objSeq.curRegSPCID,
                  'OCCURRENCE'               : self.dut.objSeq.getOccurrence(),
                  'SEQ'                      : self.dut.objSeq.curSeq,
                  'TEST_SEQ_EVENT'           : self.dut.objSeq.getTestSeqEvent(0),
                  'HD_PHYS_PSN'              : physHdMap[Hd],
                  'HD_LGC_PSN'               : Hd,
                  'DATA_ZONE'                : Zn,
                  'LASER_THRSHLD_CUR_DAC'    : Ith,
                  'LASER_OPERATING_CUR_DAC'  : Iop,
                  'WORKING_WRWH_DAC'         : WrkngTbl[(Hd,dtaZn)],
                  'SNGL_TRK_BER'             : NoSqzBerBsln,
                  'SQZ_TRK_BER'              : SqzBerBsln,
                  'BER_DELTA'                : SqzBerBsln-NoSqzBerBsln,
                  'SWEEP_MODE'               : 'BASELINE',
                  'LDI_UPDATE_FLAG'          : 0,
            })

            #===== Increasing Sweep of IOP ========================================
            if not( (NoSqzBerBsln<MaxBerThrsh) and (SqzBerBsln>=0) ):
               while Iop < IopMax:
                  #===== Set IOP in DRAM ==========================================
                  Iop+=FineIncr
                  self.SetLaserPowers(None, Iop, head=Hd, zone=Zn, saveToFlash=False, printMsg=False)

                  #===== Read working heater DAC ==================================
                  self.dut.dblData.Tables('P172_AFH_DH_WORKING_ADAPT').deleteIndexRecords(1)         #del file pointers
                  self.dut.dblData.delTable('P172_AFH_DH_WORKING_ADAPT')
                  prm = TP.prm_172_display_AFH_adapts_summary.copy()
                  prm['spc_id'] = 1     
                  prm['CWORD1'] = 4
                  self.oFSO.St(prm)
                  WrkngTbl = self.CrunchTable('P172_AFH_DH_WORKING_ADAPT', ('HD_LGC_PSN','DATA_ZONE'), 'WRITER_WRITE_HEAT', [('SPC_ID',1)])

                  #===== Measure BER after ATI ====================================
                  SqzBer = AtiBerMsmt(Hd, Zn)

                  #===== Check for best worst-side ATI BER ========================
                  LdiUpdate=0
                  if SqzBer < BestSqz:
                     BestSqz = SqzBer
                     FinalIop = Iop
                     LdiUpdate = 1

                  #===== Add data to table ========================================
                  self.dut.dblData.Tables('P_FINE_LASER_CAL').addRecord({
                  #cm.AddPtableRecord('P_FINE_LASER_CAL', spcId=SpcId, addRecord = {
                        'HD_PHYS_PSN'              : physHdMap[Hd],
                        'HD_LGC_PSN'               : Hd,
                        'DATA_ZONE'                : Zn,
                        'LASER_THRSHLD_CUR_DAC'    : Ith,
                        'LASER_OPERATING_CUR_DAC'  : Iop,
                        'WORKING_WRWH_DAC'         : WrkngTbl[(Hd,dtaZn)],
                        'SNGL_TRK_BER'             : 1.0,
                        'SQZ_TRK_BER'              : SqzBer,
                        'BER_DELTA'                : SqzBer-BestSqz,    # Delta from best BER
                        'SWEEP_MODE'               : 'SQZ_INCR',
                        'LDI_UPDATE_FLAG'          : LdiUpdate,
                  })

                  #===== Make sure we do not exceed maximum allowed change in IOP =
                  if (SqzBer>MaxBerThrsh) and  (abs(Iop-BaseIop)>MaxDacDlta):
                     ScriptComment('Max IOP DAC change limit exceeded.')
                     break

                  #===== Stop increasing Iop if we exceed Min Clearance ===========
                  if WrkngTbl[(Hd,dtaZn)]<=0:
                     objMsg.printMsg('Min Clearance Reached')
                     break

                  #===== Check for 3 consecutive measurments where squeeze BER is worse than best BER
                  if SqzBer<MaxBerThrsh: SqzDltaQueue.insert(0,SqzBer-BestSqz)
   ##               SqzDltaQueue.insert(0,SqzBer-BestSqz)
                  if len(SqzDltaQueue)>3: SqzDltaQueue.pop()
                  if len([x for x in SqzDltaQueue if x>0]) == len(SqzDltaQueue) and len(SqzDltaQueue)>=3: break

            #===== Decreasing Sweep of IOP ========================================
            Iop = FinalIop
            SqzDltaQueue=[]
            while (Iop-FineIncr) >= 0:
               #===== Set IOP in DRAM ==========================================
               Iop-=FineIncr
               self.SetLaserPowers(None, Iop, head=Hd, zone=Zn, saveToFlash=False, printMsg=False)

               #===== Read working heater DAC =====================================
               self.dut.dblData.Tables('P172_AFH_DH_WORKING_ADAPT').deleteIndexRecords(1)         #del file pointers
               self.dut.dblData.delTable('P172_AFH_DH_WORKING_ADAPT')
               prm = TP.prm_172_display_AFH_adapts_summary.copy()
               prm['spc_id'] = 1     
               prm['CWORD1'] = 4
               self.oFSO.St(prm)
               WrkngTbl = self.CrunchTable('P172_AFH_DH_WORKING_ADAPT', ('HD_LGC_PSN','DATA_ZONE'), 'WRITER_WRITE_HEAT', [('SPC_ID',1)])

               #===== Measure BER after ATI =======================================
               SqzBer = AtiBerMsmt(Hd, Zn,)

               #===== Check for best worst-side ATI BER ===========================
               LdiUpdate=0
               if SqzBer < BestSqz:
                  BestSqz = SqzBer
                  FinalIop = Iop
                  LdiUpdate = 1

               #===== Add data to table ===========================================
               self.dut.dblData.Tables('P_FINE_LASER_CAL').addRecord({
                     'SPC_ID'                   : 1, #self.dut.objSeq.curRegSPCID,
                     'OCCURRENCE'               : self.dut.objSeq.getOccurrence(),
                     'SEQ'                      : self.dut.objSeq.curSeq,
                     'TEST_SEQ_EVENT'           : self.dut.objSeq.getTestSeqEvent(0),
                     'HD_PHYS_PSN'              : physHdMap[Hd],
                     'HD_LGC_PSN'               : Hd,
                     'DATA_ZONE'                : Zn,
                     'LASER_THRSHLD_CUR_DAC'    : Ith,
                     'LASER_OPERATING_CUR_DAC'  : Iop,
                     'WORKING_WRWH_DAC'         : WrkngTbl[(Hd,dtaZn)],
                     'SNGL_TRK_BER'             : 1.0,
                     'SQZ_TRK_BER'              : SqzBer,
                     'BER_DELTA'                : SqzBer-BestSqz,    # Delta from best BER
                     'SWEEP_MODE'               : 'SQZ_DECR',
                     'LDI_UPDATE_FLAG'          : LdiUpdate,
               })

               #===== Check for 3 consecutive measurments where squeeze BER is worse than best BER
               SqzDltaQueue.insert(0,SqzBer-BestSqz)
               if len(SqzDltaQueue)>3: SqzDltaQueue.pop()
               if len([x for x in SqzDltaQueue if x>0]) == len(SqzDltaQueue) and len(SqzDltaQueue)>=3: break

            #===== Print Table ====================================================
            #cm.WritePtable('P_FINE_LASER_CAL')
            objMsg.printDblogBin(self.dut.dblData.Tables('P_FINE_LASER_CAL'))
            ScriptComment('Iop Pick: %s'%FinalIop)
            ScriptComment('Best BER: %s'%BestSqz)

            #===== Check BER Spec =================================================
            if (BestSqz > MaxBerSpec) or (FinalIop<=FineIncr):
               cm.ScriptComment('LASER CAL FAILED! - Minimum BER limit not met. Hd=%s Zn=%s BER=%s'%(Hd,Zn,BestSqz))
               return None
            else:
               self.SetLaserPowers(Ith, FinalIop, head=Hd, zone=Zn, saveToFlash=False, printMsg=False)
               return FinalIop

      #----------------------------------------------------------------------------
      def FineLaserCal(Hd, Zn, kwargs):
            #######################################################################
            defaults          = TP.LaserCalParams
            DeltaBerThrsh     = kwargs.get('DeltaBerThrsh', defaults['DeltaBerThrsh'])
            FineIncr          = kwargs.get('FineIncr',      defaults['FineIncr'])
            LsrCurRg          = kwargs.get('LsrCurRg',      defaults['LsrCurRg'])
            MaxBerSpec        = kwargs.get('MaxBerSpec',    defaults['MaxBerSpec'])
            MaxBerThrsh       = kwargs.get('MaxBerThrsh',   defaults['MaxBerThrsh'])
            SpcId             = kwargs.get('spc_id',        1)
            SqzPrcnt          = kwargs.get('SqzPrcnt',      defaults['SqzPrcnt'])
            SqzWrtCnt         = kwargs.get('SqzWrtCnt',     defaults['SqzWrtCnt'])
            WrtPttrn          = kwargs.get('WrtPttrn',      ())
            ZnPsn             = kwargs.get('ZnPsn',         defaults['ZnPsn'])
            #######################################################################
            dtaZn = [Zn*2, Zn*2-1][Zn==35]
            Lmt10 = list(proc.ParmExtractor(TP.prm_229_NoSqueeze)['Lmt10'])
            Lmt10Param = tuple([[x,ZnPsn][Lmt10.index(x)==0] for x in Lmt10])

            #===== Initial LDI and BER values =====================================
            IthBsln, IopBsln = self.GetLaserPowers(head=Hd, zone=Zn, printResults=False)
            NoSqzBerBsln, SqzBerBsln, BerDltaBsln = DltaBerMsmt(Hd, Zn, MaxBerThrsh, Lmt10Param, int(round(SqzPrcnt*2.56)), SqzWrtCnt, WrtPttrn)
            IopAdjFlg = not((BerDltaBsln>DeltaBerThrsh) and (NoSqzBerBsln<MaxBerSpec))    # 0 = decreasing sweep of Iop, 1 = increasing sweep of Iop

            #===== Define list of Iop DACs to sweep ===============================
            IopMax = int((LsrCurRg[1]-(IthBsln*TP.IthreshDac))/TP.IaddDac)
            if IopAdjFlg and (IopBsln<IopMax):            # Increasing Iop
               IopSweepLst = range(IopBsln+1, IopMax+1, FineIncr)
            elif not(IopAdjFlg):                                  # Decreasing Iop
               IopSweepLst = range(0, IopBsln, FineIncr)
               IopSweepLst.reverse()
            else:
               cm.ScriptComment('Iop DAC is out of range')
               return None

            #===== Read working heater DAC ========================================
            self.dut.dblData.Tables('P172_AFH_DH_WORKING_ADAPT').deleteIndexRecords(1)         #del file pointers
            self.dut.dblData.delTable('P172_AFH_DH_WORKING_ADAPT')
            prm = TP.prm_172_display_AFH_adapts_summary.copy()
            prm['spc_id'] = 1     
            prm['CWORD1'] = 4
            self.oFSO.St(prm)
            WrkngTbl = self.CrunchTable('P172_AFH_DH_WORKING_ADAPT', ('HD_LGC_PSN','DATA_ZONE'), 'WRITER_WRITE_HEAT', [('SPC_ID',1)])
            physHdMap = self.CrunchTable('P172_AFH_DH_WORKING_ADAPT','HD_LGC_PSN','HD_PHYS_PSN')          # Logical to Physical head map

            #===== Add data to table ==============================================
            self.dut.dblData.Tables('P_FINE_LASER_CAL').addRecord({
                  'SPC_ID'                   : 1, #self.dut.objSeq.curRegSPCID,
                  'OCCURRENCE'               : self.dut.objSeq.getOccurrence(),
                  'SEQ'                      : self.dut.objSeq.curSeq,
                  'TEST_SEQ_EVENT'           : self.dut.objSeq.getTestSeqEvent(0),
                  'HD_PHYS_PSN'              : physHdMap[Hd],
                  'HD_LGC_PSN'               : Hd,
                  'DATA_ZONE'                : Zn,
                  'LASER_THRSHLD_CUR_DAC'    : IthBsln,
                  'LASER_OPERATING_CUR_DAC'  : IopBsln,
                  'WORKING_WRWH_DAC'         : WrkngTbl[(Hd,dtaZn)],
                  'SNGL_TRK_BER'             : NoSqzBerBsln,
                  'SQZ_TRK_BER'              : SqzBerBsln,
                  'BER_DELTA'                : BerDltaBsln,
                  'SWEEP_MODE'               : 'FINE',
                  'LDI_UPDATE_FLAG'          : 0,
            })

            #===== Initialize variables ===========================================
            BestBer=NoSqzBerBsln
            BestBerDelta=BerDltaBsln
            FinalIop=IopBsln
            SqzDltaCnt=0

            #===== Sweep Iop for BER Improvement ==================================
            for IopDacVal in IopSweepLst:

               #===== Set LDI and measure BER =====================================
               self.SetLaserPowers(None, IopDacVal, head=Hd, zone=Zn, saveToFlash=False, printMsg=False)
               NoSqzBer, SqzBer, BerDlta = DltaBerMsmt(Hd, Zn, MaxBerThrsh, Lmt10Param, int(round(SqzPrcnt*2.56)), SqzWrtCnt, WrtPttrn)

               #===== Read working heater DAC =====================================
               self.dut.dblData.Tables('P172_AFH_DH_WORKING_ADAPT').deleteIndexRecords(1)         #del file pointers
               self.dut.dblData.delTable('P172_AFH_DH_WORKING_ADAPT')
               prm = TP.prm_172_display_AFH_adapts_summary.copy()
               prm['spc_id'] = 1     
               prm['CWORD1'] = 4
               self.oFSO.St(prm)
               WrkngTbl = self.CrunchTable('P172_AFH_DH_WORKING_ADAPT', ('HD_LGC_PSN','DATA_ZONE'), 'WRITER_WRITE_HEAT', [('SPC_ID',1)])
               WrkngHt = WrkngTbl[(Hd,dtaZn)]

               #===== Check for new optimal Iop ===================================
               LdiUpdate=0
               if IopAdjFlg:   # Increasing power
                  if NoSqzBer<BestBer and BerDlta<=DeltaBerThrsh and SqzBer<0:   # New optimal setting found
                     FinalIop=IopDacVal
                     BestBer=NoSqzBer
                     BestBerDelta=BerDlta
                     LdiUpdate=1
                  if BerDlta>DeltaBerThrsh and SqzBer<0: SqzDltaCnt+=1

               else:          # Backing off power
                  if SqzDltaCnt==0:
                     if BerDlta<BestBerDelta and NoSqzBer<MaxBerSpec:  # If we still meet the minimum BER and squeeze delta has improved, this is a better setting
                        FinalIop=IopDacVal
                        BestBer=NoSqzBer
                        BestBerDelta=BerDlta
                        LdiUpdate=1
                     if not(NoSqzBer<MaxBerSpec and BerDlta>DeltaBerThrsh): # If we meet the minimum BER but not the sqz delta, keep decreasing laser power
                        SqzDltaCnt+=1

                  elif SqzDltaCnt>=1: # We have already found the best LDI we can, this pass was just to collect data. Break out of loop.
                     SqzDltaCnt+=1

               #===== Add data to table ===========================================
               self.dut.dblData.Tables('P_FINE_LASER_CAL').addRecord({
                           'SPC_ID'                   : 1, #self.dut.objSeq.curRegSPCID,
                           'OCCURRENCE'               : self.dut.objSeq.getOccurrence(),
                           'SEQ'                      : self.dut.objSeq.curSeq,
                           'TEST_SEQ_EVENT'           : self.dut.objSeq.getTestSeqEvent(0),
                           'HD_PHYS_PSN'              : physHdMap[Hd],
                           'HD_LGC_PSN'               : Hd,
                           'DATA_ZONE'                : Zn,
                           'LASER_THRSHLD_CUR_DAC'    : IthBsln,
                           'LASER_OPERATING_CUR_DAC'  : IopDacVal,
                           'WORKING_WRWH_DAC'         : WrkngHt,
                           'SNGL_TRK_BER'             : NoSqzBer,
                           'SQZ_TRK_BER'              : SqzBer,
                           'BER_DELTA'                : BerDlta,
                           'SWEEP_MODE'               : 'FINE',
                           'LDI_UPDATE_FLAG'          : LdiUpdate,
               })

               #===== Stop laser cal if Iop exceeds Min Clearance =================
               if WrkngHt<=0 and IopAdjFlg:
                  objMsg.printMsg('Min Clearance Reached')
                  break

               if SqzDltaCnt > 1: break  # If we exceed the squeezed BER delta threshold more than once, break out of loop (temporary)

            #===== Print Table ====================================================
            #cm.WritePtable('P_FINE_LASER_CAL')
            objMsg.printDblogBin(self.dut.dblData.Tables('P_FINE_LASER_CAL'))
            ScriptComment('Iop Pick: %s'%FinalIop)
            ScriptComment('Best BER: %s'%BestBer)

            #===== Check BER Spec =================================================
            if (BestBer > MaxBerSpec) or (BestBerDelta > DeltaBerThrsh):
               cm.ScriptComment('LASER CAL FAILED! - Minimum BER limit not met. Hd=%s Zn=%s BER=%s'%(Hd,Zn,BestBer))
               return None
            else:
               return FinalIop

      #----------------------------------------------------------------------------
      def RunLaserCal(TestMode, **kwargs):
         ##########################################################################
         #setattr(proc.var,'TestMode',TestMode)
         defaults          = TP.LaserCalParams

         AplyCrvFit        = kwargs.get('AplyCrvFit',    defaults['AplyCrvFit'])
         ErrCode           = kwargs.get('ErrCode',       defaults['ErrCode'])
         failSafe          = kwargs.get('failSafe',      False)
         HdRg              = kwargs.get('HdRg',          (0,self.numHeads-1))
         MinHtrDac         = kwargs.get('minHtrDac',     (0,0,0,))   # Minimum DAC for applied WH/PH/RH
         saveToFlash       = kwargs.get('saveToFlash',   True)
         SpcId             = kwargs.get('spc_id',        1)
         ZnOrdr            = kwargs.get('ZnOrdr',        defaults['ZnOrdr'])
         FailZnSpec        = kwargs.get('FailZnSpec',    min([defaults['FailZnSpec'],len(ZnOrdr)]))
         ##########################################################################

         try:
            self.dut.dblData.Tables('P_HAMR_LASER_CALIBRATION').deleteIndexRecords(1)
            self.dut.dblData.delTable('P_HAMR_LASER_CALIBRATION')
         except:
            pass

         #===== Print Laser Cal Parameters ========================================
         defaults.update(kwargs)
         formatStr = "%22s %-20s : %s"
         objMsg.printMsg('Starting Laser Calibration')
         ScriptComment(formatStr%(' ', 'TestMode', TestMode), writeTimestamp=0)
         for prm, val in defaults.items():
            ScriptComment(formatStr%(' ', prm, str(val)), writeTimestamp=0)
         #objMsg.printMsg('')

         #===== Physical to Logical Head Map ======================================
         prm = TP.prm_172_RdZoneTable.copy()
         prm['spc_id'] = 1     
         self.oFSO.St(prm)
         #self.oFSO.St(TP.prm_172_RdZoneTable, loadTables=['P172_ZONE_DATA'], spc_id=1, suppressResults=True)
         physHdMap = self.CrunchTable('P172_ZONE_DATA','HD_LGC_PSN','HD_PHYS_PSN')

         #===== Read the starting laser DAC settings ==============================
         BaseLsrDacs = self.GetLaserPowers(printResults=False)
         objMsg.printMsg('BaseLsrDacs %s' % (str(BaseLsrDacs)))
         #===== Start Laser Cal ===================================================
         for hd in range(HdRg[0],HdRg[1]+1):
            msrdLdiPicks={}; intrpLdiPicks={}
            FailedZns=0
            for zn in ZnOrdr:
               if TestMode == 'VGA':
                  IopDAC = VgaLaserCal(hd, zn, kwargs)
                  FitOrdr = 1

               if TestMode == 'FINE':
                  IopDAC = FineLaserCal(hd, zn, kwargs)
                  FitOrdr = 2

               if TestMode == 'SQZ':
                  IopDAC = SqueezeLaserCal(hd, zn, kwargs)
                  FitOrdr = 2

               if TestMode == 'ATI':
                  IopDAC = AtiLaserCal(hd, zn, kwargs)
                  FitOrdr = 2

               if IopDAC == None:
                  FailedZns+=1
               if AplyCrvFit or IopDAC!=None:
                  msrdLdiPicks.update({zn : (BaseLsrDacs[hd][zn][0], IopDAC,)})

            #===== Spec Number of Failed Zones ====================================
            if (FailedZns >= FailZnSpec) and not failSafe:
               cm.RaiseTestException(ErrCode, 'Laser calibration failed on head %s'%hd)

            objMsg.printMsg("msrdLdiPicks %s "% (str(msrdLdiPicks) ))
            #===== Apply Curve Fit ================================================
            ReportFinalLaserData(msrdLdiPicks, 'M', physHdMap[hd], hd, SpcId)
            if AplyCrvFit:
               intrpLdiPicks = self.ApplyCurveFit(msrdLdiPicks,fitOrder=FitOrdr)
               objMsg.printMsg("1) intrpLdiPicks %s "% (str(intrpLdiPicks) ))
               intrpLdiPicks = dict([ (zn, (int(round(ldi[0])),int(round(ldi[1])),)) for zn, ldi in intrpLdiPicks.items() ]) # convert from float to int
               objMsg.printMsg("2) intrpLdiPicks %s "% (str(intrpLdiPicks) ))
               #if 8 in intrpLdiPicks.keys(): intrpLdiPicks.update({34 : intrpLdiPicks[8],})
               if 67 in intrpLdiPicks.keys(): intrpLdiPicks.update({150 : intrpLdiPicks[67],}) # System zone

               ReportFinalLaserData(intrpLdiPicks, 'I', physHdMap[hd], hd, SpcId)
            self.ReadHamrServoDiag(spc_id=400)
            #===== Save to RAP ====================================================
            for zn, ldi in [msrdLdiPicks,intrpLdiPicks][AplyCrvFit].items():
               self.SetLaserPowers(None, ldi[1], head=hd, zone=zn, printMsg=False)  # Update HAMR working table
            if saveToFlash:
               #self.oFSO.St(TP.prm_178_SaveRapToFlash, suppressResults=True)          # Save to RAP in flash
               self.oFSO.saveRAPtoFLASH()

            #===== Check Min Clearance ============================================
            self.CheckMinClearance(minHtrDac=MinHtrDac)                                                  # Fails for EC 14710 if we run out of clearance margin

         #===== Laser Cal Complete ================================================
         #cm.WritePtable('P_HAMR_LASER_CALIBRATION')
         objMsg.printDblogBin(self.dut.dblData.Tables('P_HAMR_LASER_CALIBRATION'))
         objMsg.printMsg('LASER CALIBRATION COMPLETE')

      #----------------------------------------------------------------------------
      #############################################################################
      #setattr(proc.var,'TestMode',TestMode)
      defaults          = TP.LaserCalParams

      AplyCrvFit        = kwargs.get('AplyCrvFit',    defaults['AplyCrvFit'])
      ErrCode           = kwargs.get('ErrCode',       defaults['ErrCode'])
      failSafe          = kwargs.get('failSafe',      False)
      HdRg              = kwargs.get('HdRg',          (0,self.numHeads-1))
      SaveRestore       = kwargs.get('SaveRestore',   True)
      saveToFlash       = kwargs.get('saveToFlash',   True)
      SpcId             = kwargs.get('spc_id',        1)
      ZnOrdr            = kwargs.get('ZnOrdr',        defaults['ZnOrdr'])
      #############################################################################
      ZnLst=[ZnOrdr, range(min(ZnOrdr),max(ZnOrdr)+1)][AplyCrvFit]
      TstZnMsk = sum([2**zn for zn in ZnLst])
      TstHdMsk = sum([2**hd for hd in range(HdRg[0],HdRg[1]+1)])

      #SavedConfigVar = cm.GetConfigVar('DisableTestCompleted',False)
      #cm.SetConfigVar('DisableTestCompleted', True)

      if SaveRestore:
         self.SaveRestoreLaserDacs('SAVE', hdMask=TstHdMsk, znMask=TstZnMsk, saveToFlash=saveToFlash)

      try:
         RunLaserCal(TestMode, **kwargs)
         ScriptComment('Total Full Track Writes: %s'%FullTrackWrites)
         #cm.SetConfigVar('DisableTestCompleted', SavedConfigVar)
         return FullTrackWrites

      except Exception, e:
         #ScriptComment(traceback.format_exc())
         ScriptComment('Exception Type: %s'%type(e))
         #cm.SetConfigVar('DisableTestCompleted', SavedConfigVar)

         #cm.WritePtable('P_FINE_LASER_CAL')
         objMsg.printDblogBin(self.dut.dblData.Tables('P_FINE_LASER_CAL'))
         #cm.WritePtable('P_HAMR_LASER_CALIBRATION')
         objMsg.printDblogBin(self.dut.dblData.Tables('P_HAMR_LASER_CALIBRATION'))
         ScriptComment('<< Laser Calibration Failed >>')

         if SaveRestore:
            self.SaveRestoreLaserDacs('RESTORE', hdMask=TstHdMsk, znMask=TstZnMsk, saveToFlash=saveToFlash)

class CLaserFinal(CLaserInit):

   def __init__(self, dut, params={}):
      self.params = dict(params)
      depList = []
      CState.__init__(self, dut, depList)
      self.numHeads = self.dut.imaxHead
      self.numZones = self.dut.numZones
      from FSO import CFSO
      self.oFSO = CFSO()
      self.oSrvFunc = CServoFunc()
      if testSwitch.HAMR_LBC_ENABLED:
         self.dut.lbcEnabled = 1
      else:
         self.dut.lbcEnabled = 0

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      objPwrCtrl.powerCycle(5000,12000,10,30)
      self.oSrvFunc.setOClim({},30,updateFlash = 1)
      self.HamrLaserCal(TestMode='SQZ', ErrCode=10182,minHtrDac=(TP.MinWrtHtClr,0,0,), spc_id=300)      # Run FLC1
      objMsg.printMsg(" HamrLaserCal Done!")
      
      if testSwitch.HAMR_FLC_ATI:                 #      not cm.GetConfigVar('ProcessForJHL', False):                # Skip ATI laser cal for JHL
         #proc.St(TP.prm_213_Ati, spc_id=20)
         self.HamrLaserCal(TestMode='ATI', ErrCode=10182,minHtrDac=(TP.MinWrtHtClr,0,0,), spc_id=350)   # Run FLC1
         #proc.St(TP.prm_213_Ati, spc_id=30)

      self.oSrvFunc.setOClim({},TP.defaultOCLIM,updateFlash = 1) 
      ###self.CollectPdData(spc_id=525)                                     # PD data collection
      objPwrCtrl.powerCycle(5000,12000,10,30)
      self.oFSO.St(TP.prm_172_HamrPreampTable, spc_id=300)                      # Report HAMR Laser DACs from RAP
      self.ReadHamrServoDiag(spc_id=700)

      prm = TP.prm_172_display_AFH_adapts_summary.copy()
      prm['spc_id'] = 550     
      prm['CWORD1'] = 4
      self.oFSO.St(prm)

      prm = TP.prm_172_display_AFH_adapts_summary.copy()
      prm['spc_id'] = 555     
      prm['CWORD1'] = 52
      self.oFSO.St(prm)
      
   def CollectPdData(self, **kwargs):
      '''
      Collect PD data at different hardware gain settings.
      '''
      SpcId = kwargs.get('spc_id', 100)

      # Disable LBC during PD measurements
      DriveLbcEnabled = self.GetLbcEnable()
      ScriptComment('*\nIncoming LBC Enable Setting: %s\n*'%str(DriveLbcEnabled), writeTimestamp=0)
      if DriveLbcEnabled:
         ScriptComment('Disabling LBC for PD data collection\n*', writeTimestamp=0)
         self.SetLbcEnable(False, saveToFlash=True)

      # Use head 0 zone 0 as LDI limit
      ldi_hd0 = self.GetLaserPowers(printResults=False)[0][0]
      iop_limit = int(round( (ldi_hd0[0]*TP.IthreshDac/TP.IaddDac) + ldi_hd0[1] ))

      # Collect data in same zones as IBias cal

      testZones = TP.LaserBiasParams.get('ZnOrdr', [0,70,148])

      # Measure PD curve at each gain setting
      try:
         for pd_gain in range(8):
            self.dut.dblData.Tables('P223_PHOTO_DIODE_DATA').deleteIndexRecords(1)         #del file pointers
            self.dut.dblData.delTable('P223_PHOTO_DIODE_DATA')

            prm_test223 = prm_223_PhotoDetector.copy()
            prm_test223.update({
                     'prm_name'        : 'P223_PHOTO_DIODE_DATA',
                     'spc_id'          : SpcId,
                     'TEST_HEAD'       : 255,    #(Hd,Hd),
                     'TARGET_ITHRESH_CURRENT' : (Ith),
                     'ZONE_MASK_BANK'  : 0,
                     'ZONE_MASK_EXT'   : (0L, 0L),
                     'ZONE_MASK'       : (0L, 1L),  
                     'ZONE_POSITION'   : 100,
                     'PD_GAIN'         : (0, 100, pd_gain),
                     'PD_FILTER'       : 3,
                     'RANGE'           : (10, iop_limit),
                     })
            self.oUtility = Utility.CUtility()
            
            MaskList = self.oUtility.convertListToZoneBankMasks(testZones)
            for bank, list in MaskList.iteritems():
               if list:
                  prm_test223 ['ZONE_MASK_EXT'], prm ['ZONE_MASK'] = self.oUtility.convertListTo64BitMask(list)
                  if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
                     prm_test223 ['ZONE_MASK_BANK'] = bank
                  self.oFSO.St(prm_test223) 
            pdTarget = self.GetTableInfo('P223_PHOTO_DIODE_DATA',0,'AVG_DIODE_VALUE')
            if pdTarget != None:
               if float( pdTarget ) >= 255.0: break
      except:
         ScriptComment(traceback.format_exc())
         ScriptComment('*** Exception thrown during PD data collection ***')

      # Power cycle to restore drive settings after T223
      objPwrCtrl.powerCycle(5000,12000,10,30)

      # Restore initial LBC Enable setting
      if DriveLbcEnabled:
         ScriptComment('*\nPD measurements complete. Restoring LBC Enable settings to %s\n*'%str(DriveLbcEnabled), writeTimestamp=0)
         self.SetLbcEnable(DriveLbcEnabled, saveToFlash=True)

class CMeasureBCI(CLaserInit):
   def __init__(self, dut, params={}):
      self.params = dict(params)
      depList = []
      CState.__init__(self, dut, depList)
      self.numHeads = self.dut.imaxHead
      self.numZones = self.dut.numZones
      from FSO import CFSO
      self.oFSO = CFSO()
      self.oSrvFunc = CServoFunc()
      if testSwitch.HAMR_LBC_ENABLED:
         self.dut.lbcEnabled = 1
      else:
         self.dut.lbcEnabled = 0
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.MeasureAllZoneBCI()
class CMeasureBer(CLaserInit):
   def __init__(self, dut, params={}):
      self.params = dict(params)
      depList = []
      CState.__init__(self, dut, depList)
      self.numHeads = self.dut.imaxHead
      self.numZones = self.dut.numZones
      from FSO import CFSO
      self.oFSO = CFSO()
      self.oSrvFunc = CServoFunc()
      if testSwitch.HAMR_LBC_ENABLED:
         self.dut.lbcEnabled = 1
      else:
         self.dut.lbcEnabled = 0
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oFSO.St({'test_num':250,'RETRIES': 50, 'ZONE_POSITION': 198, 'spc_id': 15, 'MAX_ERR_RATE': -60, 'TEST_HEAD': 255, 'NUM_TRACKS_PER_ZONE': 10, 'SKIP_TRACK': 20, 'TLEVEL': 0, 'MINIMUM': -22, 'ZONE_MASK_BANK': 0, 'timeout': 10000, 'ZONE_MASK_EXT': (33825L, 2114L), 'CWORD2': 0, 'MAX_ITERATION': 65535, 'ZONE_MASK': (4228L, 8703L), 'WR_DATA': 0, 'CWORD1': 2433})
      self.oFSO.St({'test_num':250,'RETRIES': 50, 'ZONE_POSITION': 198, 'spc_id': 15, 'MAX_ERR_RATE': -60, 'TEST_HEAD': 255, 'NUM_TRACKS_PER_ZONE': 10, 'SKIP_TRACK': 20, 'TLEVEL': 0, 'MINIMUM': -22, 'ZONE_MASK_BANK': 1, 'timeout': 10000, 'ZONE_MASK_EXT': (2114L, 4228L), 'CWORD2': 0, 'MAX_ITERATION': 65535, 'ZONE_MASK': (8456L, 16912L), 'WR_DATA': 0, 'CWORD1': 2433})
      self.oFSO.St({'test_num':250,'RETRIES': 50, 'ZONE_POSITION': 198, 'spc_id': 15, 'MAX_ERR_RATE': -60, 'TEST_HEAD': 255, 'NUM_TRACKS_PER_ZONE': 10, 'SKIP_TRACK': 20, 'TLEVEL': 0, 'MINIMUM': -22, 'ZONE_MASK_BANK': 2, 'timeout': 10000, 'ZONE_MASK_EXT': (0L, 0L), 'CWORD2': 0, 'MAX_ITERATION': 65535, 'ZONE_MASK': (48L, 33825L),'WR_DATA': 0, 'CWORD1': 2433})


class CLoopIopClr(CLaserInit):
   def __init__(self, dut, params={}):
      self.params = dict(params)
      depList = []
      CState.__init__(self, dut, depList)
      self.numHeads = self.dut.imaxHead
      self.numZones = self.dut.numZones
      from FSO import CFSO
      self.oFSO = CFSO()
      self.oSrvFunc = CServoFunc()
      if testSwitch.HAMR_LBC_ENABLED:
         self.dut.lbcEnabled = 1
      else:
         self.dut.lbcEnabled = 0
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      global loop_count
     
      loop_count = loop_count + 1
      objMsg.printMsg(" loop_count %s "% (str(loop_count) ))
      loop_to_inc_iop_list = [3, 6]

      tgt_wlr = [ 25, 20, 30, 25, 20, 30, 25, 20, 30 ]
      if loop_count in loop_to_inc_iop_list:
         Ith, Iop   = self.GetLaserPowers(head=0, zone=0, printResults=False)
         Iop        = Iop + 4
         if loop_count == 9:
            Iop = Iop - 8
         self.oFSO.St({'test_num':178,'timeout': 600, 'LASER': (Iop, 0, 0), 'CWORD1': (512,), 'ZONE': 0, 'CWORD3': 3, 'CWORD2': (0,), 'HEAD_RANGE': 1})
      self.oFSO.St({'test_num':178, 'TGT_WRT_CLR': (tgt_wlr[loop_count-1],), 'TGT_RD_CLR': (30,), 'TGT_MAINTENANCE_CLR': (45,), 'ZONE': 150, 'TGT_PREWRT_CLR': (30,), 'spc_id': 1, 'HEAD_RANGE': 65535, 'timeout': 600, 'CWORD2': 1920, 'CWORD1': 8708})
      self.oFSO.St({'test_num':178,'timeout': 600, 'CWORD1': 1568})

      if loop_count <= 9:
         self.dut.stateTransitionEvent = 'restartAtState'
         self.dut.nextState = 'EWAC_TEST'

class CSetOclim(CLaserInit):
   def __init__(self, dut, params={}):
      self.params = dict(params)
      depList = []
      CState.__init__(self, dut, depList)
      self.numHeads = self.dut.imaxHead
      self.numZones = self.dut.numZones
      from FSO import CFSO
      self.oFSO = CFSO()
      self.oSrvFunc = CServoFunc()
      if testSwitch.HAMR_LBC_ENABLED:
         self.dut.lbcEnabled = 1
      else:
         self.dut.lbcEnabled = 0
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oSrvFunc.setOClim({},30,updateFlash = 1)



