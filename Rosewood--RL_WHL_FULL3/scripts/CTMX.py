#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Class to store and report Cycle Time Monitor (CTMX) information
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CTMX.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CTMX.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import time
import DbLog
import DBLogDefs
from Drive import objDut
import MessageHandler as objMsg
from Rim import objRimType

class CTMX:
   def __init__(self, type, state_subname = ''):
      """
      Create the CTMX object.  At the CTMX level, we will handle operation
      and state time-stamps.  Data will be saved in a dbLog format.
      """
      self.IsCustCfg = False

      if type == 'OPER':   # Create the Operation time stamp
         self.name = 'TESTER_TIMESTAMP'  #'TEST_TIME_BY_OPERATION'
         self.log = {
                    'OPERATION_START_TIME' : self.makeDateStr(time.time()),
                    'OP_NAME' : objDut.nextOper,
                    'EQUIP_ID' : HOST_ID,
                    'EQUIP_TYPE' : self.getEquipType(),
                    }
         scanTime = self.getScanTime()
         insertTime = self.getInsertTime()
         autoTime = self.getAutomationTime()
         if scanTime != 0:
            self.log['SCAN_TIME'] = self.makeDateStr(scanTime)
         if insertTime != 0:
            self.log['INSERT_TIME'] = self.makeDateStr(insertTime)
         if autoTime != 0:
            self.log['AUTOMATION_TIME'] = self.makeDateStr(autoTime)

      elif type == 'STATE':   # Create the State time stamp
         self.name = 'TEST_TIME_BY_STATE'
         memVals = objMsg.getMemVals(force = True)
         self.cpu_start = objMsg.getCpuEt(force = True)
         self.real_start = time.time()

         self.log = {
            'OPER' : objDut.nextOper,
            'STATE_NAME' : objDut.currentState + state_subname,
            'SEQ' : objDut.seqNum,
            'START_TIME' : self.makeDateStr(self.real_start),
            'SZ_START' : memVals.get('VSZ',''),
            'RSS_START' : memVals.get('RSS',''),
            }
         if testSwitch.FE_0154423_231166_P_ADD_POST_STATE_TEMP_MEASUREMENT:
            self.log['DRIVE_TEMP'] =  objDut.stateTemperatureData.get(objDut.currentState, '')


      # Special case to handle RMT2 operation.  This will create an XML parametric string
      #  to sent to the host, which will subsequently report the RMT2 operation if a gantry
      #  move occurs
      elif type == 'RMT':
         self.cpu_start = objMsg.getCpuEt(force = True)  # Correct oper END cpu elapsed time start
         opName = 'RMT2'
         equipID = HOST_ID
         equipType = self.getEquipType()
         autoTime = '%t'

         testTimeStamp = DBLogDefs.DbLogTableDefinitions.OracleTables.get('TESTER_TIMESTAMP')
         dbLogFields = testTimeStamp.get('fieldList')
         logNames = []
         logTypes = []
         for item in dbLogFields:
            logNames.append(item.getName())
            if item.getType() == 'V':
               logTypes.append('string')
            elif item.getType() == 'D':
               logTypes.append('date')

         XML = '<parametrics name="TESTER_TIMESTAMP" type="scalar"><column_names>' + \
               ','.join(logNames) + '</column_names><column_types>' + \
               ','.join(logTypes) + '</column_types><row_data>' + \
               ','.join((opName, equipID, equipType, '0', autoTime, '0,'*5)) + '0' + \
               '</row_data></parametrics>'

         # Send the request to the host
         if ConfigVars[CN].get('RMT2_ENABLED',1) == 1:  #Allow option to disable RMT2 event for development sites.
            RequestService( 'RegisterEvent', {"Unload":'RMT2', "Parametrics": "%s" % XML } )

   def getEquipType(self):
      if objRimType.isNeptuneRiser():
         objDut.EquipType = 'NEPTUNE2'
      else:   
         objDut.EquipType = 'GEMINI'
      objDut.driveattr['TEST_EQUIP'] = objDut.EquipType
      return objDut.EquipType

   def getScanTime(self):
      try:
         scanTime = HostItems.get('ScanTime',0)
      except NameError:  # in case HostItems is not exported by the CM
         scanTime = 0
      return scanTime

   def getInsertTime(self):
      try:
         insertTime = HostItems.get('InsertTime',0)
      except NameError:  # in case HostItems is not exported by the CM
         insertTime = 0
      return insertTime

   def getAutomationTime(self):
      try:
         automationTime = HostItems.get('AutomationTime',0)
      except NameError: # in case HostItems is not exported by the CM
         automationTime = 0
      return automationTime

   def makeDateStr(self, currTime):
      """
      Report the input time as a string of the format: "mm/dd/yyyy hh:mm:ss"
      """
      date = time.localtime(currTime)     # Get current time in a formatted tuple
      dateStr = "%02d/%02d/%04d %02d:%02d:%02d" % (date[1],date[2],date[0],date[3],date[4],date[5])
      return dateStr

   def endStamp(self):
      """Stamp the log with the operation/state ending time"""
      if self.IsCustCfg == True:
         return

      if self.name == 'TESTER_TIMESTAMP': #'TEST_TIME_BY_OPERATION':
         self.log['OPERATION_PF_TIME'] = self.makeDateStr(time.time())
      elif self.name == 'TEST_TIME_BY_STATE':
         memVals = objMsg.getMemVals()
         cpu_end = objMsg.getCpuEt(force = True)
         real_end = time.time()
         self.log['END_TIME'] = self.makeDateStr(real_end)
         self.log['ELAPSED_TIME'] = '%0.2f' % (real_end - self.real_start)
         self.log['CPU_ELAPSED_TIME'] = '%0.2f' % (cpu_end - self.cpu_start)
         self.log['SZ_END'] = memVals.get('VSZ','')
         self.log['RSS_END'] = memVals.get('RSS','')
         if testSwitch.FE_0154423_231166_P_ADD_POST_STATE_TEMP_MEASUREMENT:
            self.log['DRIVE_TEMP'] =  objDut.stateTemperatureData.get(objDut.currentState, '')

   def writeDbLog(self):
      """Write the CTMX info to DbLog"""

      if self.IsCustCfg == True:
         return

      objDut.dblData.Tables(self.name).addRecord(self.log)
