#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/IntfTTR.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/IntfTTR.py#1 $
# Level:3
#---------------------------------------------------------------------------------------------------------#

import time
import DbLog
import ScrCmds
from Process import CProcess
import IntfClass
#from PowerControl import objPwrCtrlATA
from PowerControl import objPwrCtrl
from TestParameters import *
#from MessageHandler import objMsg
import MessageHandler as objMsg

##############################################################################################################
##############################################################################################################
class intfTTRException(Exception):
   def __init__(self,data):
      self.data = data
      
      objMsg.printMsg('intfTTRException')

##############################################################################################################
##############################################################################################################
class CIntfTTRTest(CProcess):
   """

   """
   #---------------------------------------------------------------------------------------------------------#
   def __init__(self, dut, params=[]):
      objMsg.printMsg('*'*20+"Interface TTR init" + 20*'*')
      CProcess.__init__(self)
      self.ttrLoop   = prm_IntfTTR["TTR_Loop"]   
      self.ttrLimit  = prm_IntfTTR["TTR_Limit"]      
      self.readyTime = 0

      if ConfigVars[CN]['BenchTop']:
         objMsg.printMsg('BenchTop TTR_Loop forced to 2')
         self.ttrLoop = 2

      objMsg.printMsg('TTR Limit: %d for %d Hdrs' % (self.ttrLimit,numHeads))
      objMsg.printMsg('Loop Count: %d' % self.ttrLoop)
   #---------------------------------------------------------------------------------------------------------#
   def intfTTRTest(self):
      """
      Execute function loop.
      @return result: Returns OK or FAIL
      """
      from Rim import objRimType
      result = 0
      max_ttr  =0
      if not objRimType.CPCRiser():
         objMsg.printMsg('Not IO Cell, Bypass TTR Test')
         return 0
      self.readyTime = 0
      objMsg.printMsg('*'*20+"Interface TTRTest" + 20*'*')
      if self.ttrLoop > 1:
         objMsg.printMsg("NumLoops: %s" % self.ttrLoop)
      try:
         for loopCnt in range(self.ttrLoop):
            if self.ttrLoop > 1:
               objMsg.printMsg('Loop: ' + str(loopCnt+1) + '*'*5+"Interface TTRTest" + 20*'*')
            objPwrCtrl.powerOff();
            objPwrCtrl.powerOn()
            self.readyTime += objPwrCtrl.readyTime
            if objPwrCtrl.readyTime > max_ttr:
               max_ttr = objPwrCtrl.readyTime 
            if objPwrCtrl.readyTime > self.ttrLimit:
               result = 1
         
      except Exception, M:
         #self.makeDBLOutput('ACCESS_TIME')
         ## objMsg.printMsg('makeDBLOutput complete')
         raise 
      self.readyTime = self.readyTime / ( self.ttrLoop * 1000.0) # in second
      self.makeDBLOutput()
      objMsg.printMsg('makeDBLOutput complete')
      if result:
         msg = "Max TTR = %s exceeds limit: %s" %(str(max_ttr), str(self.ttrLimit))
         ScrCmds.raiseException(13455, msg)
      return result


   #---------------------------------------------------------------------------------------------------------#
   def makeDBLOutput(self):
      SPC_ID = 0
      NUM_HEAD = 0
      #Calculate SPC_ID based on NUM_HEADS
      NUM_HEAD = int(DriveAttributes['NUM_HEADS'])
      if NUM_HEAD == 1 or NUM_HEAD == 2: SPC_ID = 1
      if NUM_HEAD == 3 or NUM_HEAD == 4: SPC_ID = 2

      self.dut.dblData.Tables('P001_TIME_TO_READY').addRecord( {
                                               'SPC_ID' : SPC_ID,
                                               'OCCURRENCE': self.dut.seqNum,     
                                               'SEQ' : self.dut.seqNum,
                                               'TEST_SEQ_EVENT': 1,                                                                                        
                                               'TIME': self.readyTime ,
                                            })
      self.dut.dblData.Tables('P_TTR').addRecord( {
                                               'SPC_ID' : SPC_ID,
                                               'OCCURRENCE': self.dut.seqNum,
                                               'SEQ' : self.dut.seqNum,
                                               'TEST_SEQ_EVENT': 1,
                                               'TTR': self.readyTime ,
                                            })
