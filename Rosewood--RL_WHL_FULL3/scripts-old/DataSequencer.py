#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Class to sequence DBLOG data for event vectors
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/08 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DataSequencer.py $
# $Revision: #2 $
# $DateTime: 2016/11/08 00:12:47 $
# $Author: gang.c.wang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DataSequencer.py#2 $
# Level:3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import MessageHandler as objMsg

DEBUG = 0

class CDataSequencer:
   def __init__(self, dut):
      self.dut = dut

      try:
         self.__testEventList = self.dut.objData.retrieve('testEventList')
      except:
         self.__testEventList = {}
      #Needs tobe in the numeric order shown below
      self.__testOff = 1
      self.__occurOff = 0

      self.curSeq = self.getSeq()
      self.occurrence = 1
      self.testSeqEvent = 1

      self.curRegTest = 0
      self.curRegSPCID = 1
      self.suppressresults = 0

      self.tablesToParse = []
      if testSwitch.virtualRun:
         class CMockSuprsDbl(object):
            def __init__(self, dut):
               self.dut = dut
               self.data = {}
               
            def __getitem__(self, key):
               self.data[key] = self.dut.dblData.Tables(key).tableDataObj()
               return self.data[key]
               
            def __contains__(self, key):
               if self.data.has_key(key):
                  return True
               try:
                  self.data[key] = self.dut.dblData.Tables(key).tableDataObj()
                  return True
               except:
                  return False
               
            def get(self, key, default=None):
               return self.__getitem__(key)
               
            def clear(self):
               self.data.clear()
               
            def copy(self):
               return self.data.copy()
            
         self.SuprsDblObject = CMockSuprsDbl(self.dut)
      else:
         self.SuprsDblObject = {}

   def __findOccur(self,test):
      try:
         searchList = self.__testEventList.get(self.curSeq,0)
         if len(self.__testEventList.items()) > 0:
            if len(searchList) > 0:
               for count in range(len(searchList)-1,-1,-1):
                  if DEBUG==1:
                     objMsg.printMsg("Currently looking at index: %s for test=%s" % (str(count),test))
                  if len(searchList[count]) > 0:
                     if searchList[count][self.__testOff] == test:
                        return searchList[count][self.__occurOff]
               else:
                  return 0
            else:
               #self.__testEventList[self.curSeq].append([])
               return 0
         else:
            return 0
      finally:
         if DEBUG == 1:
            objMsg.printMsg(str(self.__testEventList))

   def registerCurrentTest(self, test, spc_id = 1):
      tmpEvent = []
      if not self.curSeq == self.getSeq() or len(self.__testEventList.items()) == 0:
         self.curSeq = self.getSeq()
         self.__testEventList.update({self.curSeq:[]})

      self.testSeqEvent = self.__findOccur(test)+1
      tmpEvent.append(self.testSeqEvent)
      tmpEvent.append(test)

      self.__testEventList[self.curSeq].append(tmpEvent)

      self.curRegTest = test
      self.curRegSPCID = spc_id

      self.occurrence = self.getOccurrence()
      return (self.dut.seqNum,self.occurrence,self.testSeqEvent)

   def getOccurrence(self):

      #Return 1 if the list is empty
      try:
         self.occurrence = max(1,len(self.__testEventList[self.curSeq]))
      except:
         self.occurrence = max(1,len(self.__testEventList.get(self.curSeq,[])))
      return self.occurrence

   def getSeq(self):
      return self.dut.seqNum

   def setSeq(self, seqNumber):
      self.dut.seqNum = seqNumber

   def getTestSeqEvent(self,test):
      self.testSeqEvent = self.__findOccur(test)
      return self.testSeqEvent

   def resetCounters(self):
      '''Currently not used.  Call during Virtual Execution after each operation.'''
      self.dut.seqNum = 0
      self.__testEventList = {}


###########################################################################################################
###########################################################################################################
#---------------------------------------------------------------------------------------------------------#
