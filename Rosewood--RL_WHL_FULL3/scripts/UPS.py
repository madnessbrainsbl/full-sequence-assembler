#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2015, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/UPS.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/UPS.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import * #pylint: disable=W0614
from Drive import objDut
import MessageHandler as objMsg
from Process import CProcess
from TestParamExtractor import TP

class UPS(CProcess):

   UPS_CALLBACK = 4

   def setupUPS(self):

      self.resetUPS()

      objMsg.printMsg("Attempting UPS Setup")

      if testSwitch.virtualRun:

         objMsg.printMsg("Setting UPS for VE")
         self.dut.UPSTests = set(range(0,9999))
         self.dut.UPSTests.discard(0)
         self.dut.UPSTests.discard(8)
         if testSwitch.COMMON_EDG_AFH:
            self.dut.UPSTests.discard(135)

         try:
            from ParameterTables import parmXRef
         except ImportError:
            objMsg.printMsg("Could not import parmXRef. Try the '-U' make option")
            return

         self.dut.parmXRef = parmXRef
         self.RegisterParamsDictionary(self.dut.parmXRef)

         return

      RegisterResultsCallback(self.RequestUploadParameterSystem, self.UPS_CALLBACK, 0) # called during TP.prm_000_GetParams

      try:
         self.St(TP.prm_000_GetParams) # populates self.dut.parmXRef
      except ScriptTestFailure, (failureData):

         # Test 0 doesn't exist

         try:
            ec = failureData[0][2]
         except (TypeError, IndexError):
            ec = 0

         if ec != 10253:
            # no idea what happened
            raise failureData

         # Unregister callback number 4
         RegisterResultsCallback("", self.UPS_CALLBACK, 0)

         objMsg.printMsg("UPS Not Supported by the Drive")

         # Returning here doesn't setup self.dut.UPSTests so
         # the system knows there's no UPS and we're good to continue
         return

      self.RegisterParamsDictionary(self.dut.parmXRef)

      self.St(TP.prm_166_GetTestList)
      testsAvailable =  self.dut.objSeq.SuprsDblObject['P166_TESTS_AVAILABLE']
      self.dut.UPSTests = set([int(r['TEST_NUM']) for r in testsAvailable])
      self.dut.UPSTests.discard(0)
      self.dut.UPSTests.discard(8)
      if testSwitch.COMMON_EDG_AFH:
         self.dut.UPSTests.discard(135)

      objMsg.printMsg("UPS Tests Sucessfully Registered")

   def RequestUploadParameterSystem(self, requestData, *args, **kargs):
      requestKey = ord(requestData[0])
      if requestKey == 4:
         requestData = requestData[3:-2]
         # if the format of data is "<name1>,<cnt1><name2>,<cnt2>" then use the logic below

         requestData = requestData.split(",")
         for item in requestData:
            key = item[2:]
            if key:
                                    #         code,         data-type,                stat-dyn,        count
               self.dut.parmXRef[key] = (self.dut.parmCode, ord(item[0])&0x07, ord(item[0])&0x10 == 0x10, ord(item[1]))
               self.dut.parmCode += 1
               if ConfigVars[CN].get('ShowparmXRef', 0):
                  objMsg.printMsg("%24s:  %s" % (key, self.dut.parmXRef[key],))

         SendBuffer("\007\000\000")
      else:
         str = "Unsupported requestKey in UploadParameterSystemRequest==>", requestKey
         raise FOFParameterError, str

   def resetUPS(self):
      objMsg.printMsg("Resetting UPS")
      self.dut.parmCode = 0
      self.dut.parmXRef = {}
      self.dut.UPSTests = set()
      self.UnRegisterParamsDictionary()

   @staticmethod
   def RegisterParamsDictionary(parmXRef):
      RegisterParamsDictionary(parmXRef) #pylint: disable=E0602
      objMsg.printMsg("parmXRef Registered")

   @staticmethod
   def UnRegisterParamsDictionary():
      RegisterParamsDictionary(None) #pylint: disable=E0602
      objMsg.printMsg("parmXRef Unregistered")

upsObj = UPS()
