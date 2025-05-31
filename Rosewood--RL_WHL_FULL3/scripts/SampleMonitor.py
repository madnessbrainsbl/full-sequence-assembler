#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: SampleMonitor module.  Enables selective testing from a remotely configured server which
#              sets sample rates for processes that can be adjusted to provide as much or as little data
#              as required / needed.
#
# Owner: Dave Thorsvik
#
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SampleMonitor.py $
# $Revision: #1 $
# $Id: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SampleMonitor.py#1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SampleMonitor.py#1 $
# Level: ?
#---------------------------------------------------------------------------------------------------------#

import os
import types
import sys
import MessageHandler as objMsg
from State import CState
from Drive import objDut
from Test_Switches import testSwitch

################################################################################
################################################################################
class MKD: #Monitor Key Data
   """
   Class that holds the truth value extracted from the data the server returned.
   """
   pass

TD = MKD( )

################################################################################
################################################################################
class CSampMon:
   """
   Class that retrieves the sample monitor packet from host services.
   Determine if the drive under test will be directed to run a particular option
   within an operation or if it will be skipped.
   """

   #-------------------------------------------------------------------------------------------------------
   def ProcessSampleRequest(self, Operation, TestName, PartNum, SBR, HeadCount ):
      data = (0,'NoData')
      status = 'NotValid'
      CommException = False
      self.Truth = 0

      objMsg.printMsg("Operation is %s, TestName = %s, PN = %s, SBR = %s, Head Count = %s" % (Operation, TestName, PartNum, SBR, HeadCount))
      objMsg.printMsg("Trying RequestService( ) for SampleMonitor query.")

      try:
         # Operation is a string which helps ID the interaction with the server
         status, data = RequestService("GetSampleReq", (Operation, TestName, PartNum, SBR, HeadCount ) )
      except:
         if SBR == 'bench':
            CommException = False
         else:
            CommException = True

      if status != 'NotValid':
         objMsg.printMsg("status returned is % s" % status)

      SampMonStatus = data[0]
      if SBR == 'bench':
         self.Truth = 0x000001e
         objMsg.printMsg("Running VE.  Sample monitor simulating a run condition.")
         objMsg.printMsg("Run condition simulated with truth value of 1e.")
      else:
         if data[1] == 'NoData':
            objMsg.printMsg("1_Tuple returned %d in first position and %s in second position." % (data[0], data[1]))
            self.Truth = 0
         else:
            objMsg.printMsg("2_Tuple returned %d in first position and %s in second position." % (data[0], data[1]))
            self.Truth = int( data[1], 16)


      if SampMonStatus == 999999 or CommException == True :
         if CommException == True:
            objMsg.printMsg("RequestService generated an exception.")
         else:
            objMsg.printMsg("Host Services Sample Request returned no recommendation.")
            objMsg.printMsg("Action associated with jumpState taken.")
         self.ReturnedDirective = 'jumpState'

      else:
         objMsg.printMsg("Truth value = %x" % self.Truth)
         if self.Truth > 0:  #Truth value not 0, a sample monitor directed option will be taken.
            objMsg.printMsg("Sample monitor directing execution to action associated with pass.")

            # Setting the stateTransitionEvent to pass in the SDAT case will
            # cause the SDAT script execution to continue in the normal manner.
            # No states will be skipped.
            self.ReturnedDirective = 'pass'

         else:
            objMsg.printMsg("Sample monitor directed an alternate action.")
            self.ReturnedDirective = 'jumpState'

      return [self.ReturnedDirective, self.Truth]


#-------------------------------------------------------------------------------
   def ProcessSampleComplete (self, Operation, TestName, PartNum, SBR, HdCount):
      svcName = ''
      data = 0
      objMsg.printMsg("Sending Sample Complete through sample monitor.")

      try:
         # ScriptOperation is a string which helps ID the interaction with the server
         svcName, data = RequestService("PutSampleComplete", (Operation, TestName, PartNum, SBR, HdCount))
      except:
         if SBR == 'bench':
            objMsg.printMsg("VE running, sample complete can't be sent, assume success.")
         else:
            if svcName == "PutSampleComplete":
               objMsg.printMsg("Service recognized, but server returned error.")
               objMsg.printMsg("Data returned was %d" % data)
            else:
               objMsg.printMsg("Host services didn't recognize communication.")

      return data






################################################################################
################################################################################

class CGetSampMonForSDAT(CState, CSampMon ):
   """
   Class that acts as the interface to the sample monitor service for retrieving SDAT
   run directives.  Determine if the drive under test will be directed to run
   a particular option within an operation or if it will be skipped.
   """

   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut


   def run(self):
      # With ScriptOperation set to the correct state to pass to the server,
      # set other variables used to access the correct database.
      PartNum = self.dut.partNum
      SpecBldReq = self.dut.sbr
      ScriptOperation = self.dut.nextOper
      HdCount = ''
      TestName = ''

      StateInfo, TruthVal = self.ProcessSampleRequest(ScriptOperation, TestName,PartNum,SpecBldReq,HdCount)

      self.dut.stateTransitionEvent = StateInfo
      TD.Truth = TruthVal



################################################################################
################################################################################
class CGetSampMonForDSPScreen(CState, CSampMon):
   """
   Class that acts as the interface to the sample monitor service for retrieving
   Disc Separator Plate run directives.  Determine if the drive under test will
   be directed to run the DSP option within an operation or if it will be skipped.
   """

   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut

   def run(self):
      # With ScriptOperation set to the correct state to pass to the server,
      # set other variables used to access the correct database.
      PartNum = self.dut.partNum
      SpecBldReq = self.dut.sbr
      ScriptOperation = self.dut.nextOper
      HdCount = self.dut.imaxHead
      TestName = 'DSP'

      StateInfo, TruthVal = self.ProcessSampleRequest( ScriptOperation, TestName, PartNum, SpecBldReq, HdCount )
      
      self.dut.stateTransitionEvent = StateInfo
      #TruthVal = 0x11 #remove this for gemini run
      TD.Truth = TruthVal # need this in for final version

      if (testSwitch.FE_0159597_357426_DSP_SCREEN == 1):
         if TruthVal > 1:  #greater the 01 ie.11 is head 1 21 - head 2 
            objMsg.printMsg("TruthValue is %d" % TruthVal)
            TD.Truth = (TruthVal - 1) / 16
            objMsg.printMsg("DSPtruthValue is %d" % TD.Truth)
         else:
            if TruthVal == 1:
               TD.Truth = 0 #01 is head 0
               objMsg.printMsg("TruthValue1 is %d" % TruthVal)
               objMsg.printMsg("DSPTruthValue1 is %d" % TD.Truth)
  
            
          
