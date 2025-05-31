#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# $RCSfile: ReliSmart.py $
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReliSmart.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReliSmart.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
#import time
#import re
import binascii, math, time
from Constants import *
#import ScrCmds
#from MessageHandler import objMsg      # DT SIC
import MessageHandler as objMsg



#import IntfClass




###########################################################################################################

                   


###########################################################################################################
###########################################################################################################
class CSmartCriticalEventF3:
   #---------------------------------------------------------------------------------------
   def __init__(self, logData, logSize):
      self.P_Msg = OFF      # Performance Message
      self.F_Msg = OFF      # Failure Message
      self.B_Msg = OFF      # Buffer Message
      self.D_Msg = ON       # Debug Message
      self.buffer = logData
      self.size = logSize # in sectors
      self.numCriticalEvents = 0
      self.eventList = []
      self.buildEventList()
   
   #---------------------------------------------------------------------------------------
   def buildEventList(self):
      numEvents = (self.size * 512) / 32
      for i in range(0, numEvents):
         event = self.getEvent(i)
         if self.check(event):
            if i == 0:
               objMsg.printMsg('Event #      Hr    Time Stamp Type  Flag         LBA      ERROR RecType RecRetry Command    Phy Cyl Log Hd Phy Sec Count NumTime Temp')
               objMsg.printMsg('--------- -----  ------------ ----  ----  ---------- ------ ------- -------- ------- ---------- ------ ------- ----- ------- ----')
            # DT051109 Change Error Code to Hex
            #objMsg.printMsg('Event%3d: %5d  %12d 0x%2X  %4d  %10d %10d %7X %8X %7X %10d %6d %7d %5d %7d %3dC' % \   
            objMsg.printMsg('Event%3d: %5d  %12d 0x%2X  %4d  %10d   %4X %7X %8X %7X %10d %6d %7d %5d %7d %3dC' % \
                   (i+1, event['TimeH'], event['Time'], event['Type'], event['Flag'], event['LBA'], event['Error'], \
                    event['RecType'], event['Retry'], event['Command'], event['PhyCyl'], event['LogHd'], \
                    event['PhySec'], event['Count'], event['NumTime'], event['Temp']))
            self.eventList.append(event)
            if event['Type'] in [0x2,0x3,0x7,0xB]:
               self.numCriticalEvents += 1
         else:
         	  break

   #---------------------------------------------------------------------------------------
   def getEvent(self, num):
      event = {}
      start = num * 32
      event['Type']   = ((ord(self.buffer[start]) & 0xFF))
      event['Flag']   = ((ord(self.buffer[start+1]) & 0xFF))
      event['TimeH']  = ((ord(self.buffer[start+2]) & 0xFF)) + ((ord(self.buffer[start+3]) & 0xFF) <<  8)
      event['Time']   = ((ord(self.buffer[start+4]) & 0xFF)) + ((ord(self.buffer[start+5]) & 0xFF) <<  8) + \
                        ((ord(self.buffer[start+6]) & 0xFF) << 16) + ((ord(self.buffer[start+7]) & 0xFF) << 24)
      event['LBA']    = ((ord(self.buffer[start+8]) & 0xFF)) + ((ord(self.buffer[start+9]) & 0xFF) <<  8) + \
                        ((ord(self.buffer[start+10]) & 0xFF) << 16) + ((ord(self.buffer[start+11]) & 0xFF) << 24)
      event['Error']  = ((ord(self.buffer[start+12]) & 0xFF)) + ((ord(self.buffer[start+13]) & 0xFF) <<  8) + \
                        ((ord(self.buffer[start+14]) & 0xFF) << 16) + ((ord(self.buffer[start+15]) & 0xFF) << 24)
      event['Temp']   = ((ord(self.buffer[start+16]) & 0xFF))
      event['RecType']= ((ord(self.buffer[start+17]) & 0xFF))
      event['Retry']  = ((ord(self.buffer[start+18]) & 0xFF))
      event['Command']= ((ord(self.buffer[start+19]) & 0xFF))
      event['PhyCyl'] = ((ord(self.buffer[start+20]) & 0xFF)) + ((ord(self.buffer[start+21]) & 0xFF) <<  8) + \
                        ((ord(self.buffer[start+22]) & 0xFF) << 16) + ((ord(self.buffer[start+23]) & 0xFF) << 24)
      event['LogHd']  = ((ord(self.buffer[start+24]) & 0xFF)) + ((ord(self.buffer[start+25]) & 0xFF) <<  8)
      event['PhySec'] = ((ord(self.buffer[start+26]) & 0xFF)) + ((ord(self.buffer[start+27]) & 0xFF) <<  8)
      event['Count']  = ((ord(self.buffer[start+28]) & 0xFF)) + ((ord(self.buffer[start+29]) & 0xFF) <<  8)
      event['NumTime']= ((ord(self.buffer[start+30]) & 0xFF))
      return event

   #---------------------------------------------------------------------------------------
   def check(self, event):
      flag = event['Type'] + event['Flag']  + event['TimeH']  + event['Time'] + event['LBA'] + \
             event['Error'] + event['Temp']  + event['RecType']  + event['Retry'] + event['Command'] + \
             event['PhyCyl'] + event['LogHd'] + event['PhySec'] + event['Count'] + event['NumTime']
      return flag

   #---------------------------------------------------------------------------------------
   def getEventCnt(self):
      nCnt = 0
      if len(self.eventList) != 0:
         nCnt = len(self.eventList)*32 # number of bytes
      if nCnt > 0 or self.D_Msg:
         objMsg.printMsg('RELIDATA - Critical Event Count in Bytes = %d' % nCnt)
      return nCnt

   #---------------------------------------------------------------------------------------
   def getCriticalEventCnt(self):
      return self.numCriticalEvents

###########################################################################################################
class CSmartDefect:
   #---------------------------------------------------------------------------------------
   def __init__(self, logData, logSize):
      self.P_Msg = OFF      # Performance Message
      self.F_Msg = OFF      # Failure Message
      self.B_Msg = OFF      # Buffer Message
      self.D_Msg = OFF      # Debug Message
      self.buffer = logData
      self.size = logSize # in sectors
      self.defectList = []
      self.buildDefectList()

   #---------------------------------------------------------------------------------------
   def buildDefectList(self):
      numDefects = ((self.size * 512) / 16) - 1
      revision = (ord(self.buffer[0]) & 0xFF) | ((ord(self.buffer[ 1]) & 0xFF) << 8)
      if self.D_Msg:
         objMsg.printMsg('RELIDATA - Defect Log Revision: %d' % revision)
      # step through event entries and display
      for i in range(1, numDefects+1):
         defect = self.getDefect(i)
         if self.check(defect):
           self.defectList.append(defect)
         else:
           break

   #---------------------------------------------------------------------------------------
   def getDefect(self, num):
      defect = {}
      start = num * 16
      defect['Radius']  = ((ord(self.buffer[start]) & 0xFF)) | ((ord(self.buffer[start+1]) & 0xFF) << 8)
      defect['Theta']   = ((ord(self.buffer[start+2]) & 0xFF)) | ((ord(self.buffer[start+3]) & 0xFF) << 8)
      defect['Head']    = ((ord(self.buffer[start+4]) & 0xFF))
      defect['Vendor']  = ((ord(self.buffer[start+5]) & 0xFF))
      defect['LBA']     = ((ord(self.buffer[start+6]) & 0xFF)) | ((ord(self.buffer[start+7]) & 0xFF) << 8) | \
                          ((ord(self.buffer[start+8]) & 0xFF) << 16) | ((ord(self.buffer[start+9]) & 0xFF) << 24)
      defect['Hours']   = ((ord(self.buffer[start+10]) & 0xFF)) | ((ord(self.buffer[start+11]) & 0xFF) <<  8)
      defect['Res']     = ((ord(self.buffer[start+12]) & 0xFF)) | ((ord(self.buffer[start+13]) & 0xFF) << 8) | \
                          ((ord(self.buffer[start+14]) & 0xFF) << 16) | ((ord(self.buffer[start+15]) & 0xFF) << 24)
      return defect

   #---------------------------------------------------------------------------------------
   def check(self, defect):
      flag = defect['Radius'] + defect['Theta'] + defect['Head'] + defect['LBA'] + defect['Hours']
      return flag

   #---------------------------------------------------------------------------------------
   def getDefectCnt(self):
      nCnt = 0
      if len(self.defectList) != 0:
         nCnt = len(self.defectList)*16 + 16 # number of bytes
      if nCnt > 0 or self.D_Msg:
         objMsg.printMsg('RELIDATA - Defect Count in Bytes = %d' % nCnt)
      return nCnt


###########################################################################################################
class CSmartAttributes:
   SMART_NUMBER_ATTRIBUTES = 30
   SMART_FIRST_ATTRIBUTE = 2
   SMART_ATTRIB_SIZE = 12
   #---------------------------------------------------------------------------------------
   def __init__(self, smartBuffer):
      self.P_Msg = OFF      # Performance Message
      self.F_Msg = OFF      # Failure Message
      self.B_Msg = OFF      # Buffer Message
      self.D_Msg = OFF      # Debug Message
      self.buffer = smartBuffer
      self.attributeList = []
      self.getAttribute()
   #---------------------------------------------------------------------------------------
   def decodeAttribute(self, attribId):
      attPtr = self.SMART_FIRST_ATTRIBUTE
      # look for the specified attribute
      for i in range(self.SMART_NUMBER_ATTRIBUTES):
        if ord(self.buffer[attPtr]) & 0xFF == attribId:
          self.getAttributeAtLocation(i) # extract attribute data at specified location
          break
        attPtr += self.SMART_ATTRIB_SIZE

      return self.Attribute
   #---------------------------------------------------------------------------------------
   def getAttribute(self):
      self.attributeList.append((ord(self.buffer[430]) & 0xFF) + ((ord(self.buffer[431]) & 0xFF) << 8))
      self.attributeList.append((ord(self.buffer[432]) & 0xFF) + ((ord(self.buffer[433]) & 0xFF) << 8))
      self.attributeList.append((ord(self.buffer[444]) & 0xFF) + ((ord(self.buffer[445]) & 0xFF) << 8))
      self.attributeList.append((ord(self.buffer[446]) & 0xFF) + ((ord(self.buffer[447]) & 0xFF) << 8))
      self.attributeList.append((ord(self.buffer[452]) & 0xFF) + ((ord(self.buffer[453]) & 0xFF) << 8))
      for i in range(self.SMART_NUMBER_ATTRIBUTES):
          smart = self.getAttributeAtLocation(i) # extract attribute data at specified location
          if self.check(smart):
             self.attributeList.append(smart)
   #---------------------------------------------------------------------------------------
   def getAttributeAtLocation(self, attribLocation):
      # calculate location in data specified attribute starts
      self.Attribute = {}
      attPtr = self.SMART_FIRST_ATTRIBUTE + self.SMART_ATTRIB_SIZE * attribLocation

      #  extract parameters
      self.Attribute['Ident']       = ord(self.buffer[attPtr])    & 0xFF
      self.Attribute['Status']      = (ord(self.buffer[attPtr+1]) & 0xFF) +  ((ord(self.buffer[attPtr+2]) & 0xFF) << 8)
      self.Attribute['Nominal']     = ord(self.buffer[attPtr+3])  & 0xFF
      self.Attribute['Worst']       = ord(self.buffer[attPtr+4])  & 0xFF
      self.Attribute['RawData']     = {}
      self.Attribute['RawData'][0]  = ord(self.buffer[attPtr+5])  & 0xFF
      self.Attribute['RawData'][1]  = ord(self.buffer[attPtr+6])  & 0xFF
      self.Attribute['RawData'][2]  = ord(self.buffer[attPtr+7])  & 0xFF
      self.Attribute['RawData'][3]  = ord(self.buffer[attPtr+8])  & 0xFF
      self.Attribute['RawData'][4]  = ord(self.buffer[attPtr+9])  & 0xFF
      self.Attribute['RawData'][5]  = ord(self.buffer[attPtr+10]) & 0xFF
      self.Attribute['Reserved']    = ord(self.buffer[attPtr+11]) & 0xFF

      # build RawValue from the six RawData entries
      self.Attribute['RawValue']    = 0
      for i in range(6):
        value = ord(self.buffer[attPtr+5+i]) & 0xFF
        shift = i * 8
        self.Attribute['RawValue'] += value << shift

      # other information
      self.Attribute['Location']      = attribLocation
      self.Attribute['Index']         = attPtr
      self.Attribute['Version']       = (ord(self.buffer[0]) & 0xFF) + ((ord(self.buffer[1]) & 0xFF) << 8)

      return self.Attribute
   #---------------------------------------------------------------------------------------
   def check(self, smart):
      flag = smart['Ident'] + smart['Nominal'] + smart['Worst'] + smart['RawValue'] 
      return flag



###########################################################################################################