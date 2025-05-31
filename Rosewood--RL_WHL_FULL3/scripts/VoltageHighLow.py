#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VoltageHighLow.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VoltageHighLow.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *

import time
import re

from TestParamExtractor import TP
import ScrCmds
from PowerControl import objPwrCtrl
import MessageHandler as objMsg
from ICmdFactory import ICmd

class CVoltageHighLow:
   def __init__(self):
      self.nominal_5v   = 5000
      self.nominal_12v  = 12000

      self.high_5v = 0.0
      self.low_5v = 0.0

      self.high_12v = 0.0
      self.low_12v = 0.0

   def voltageHighLowTest(self, margin_5v = 0, margin_12v = 0):
      start_time = time.time()
      if margin_5v == -1:
         nominal_5v = 0.0
      else:
         self.high_5v = self.nominal_5v + (self.nominal_5v  * margin_5v)
         self.low_5v       = self.nominal_5v  - (self.nominal_5v  * margin_5v)

      if margin_12v == -1:
         self.nominal_12v = 0.0
      else:
         self.high_12v     = self.nominal_12v + (self.nominal_12v * margin_12v)
         self.low_12v      = self.nominal_12v - (self.nominal_12v * margin_12v)

      self.f_nominal_5v = self.nominal_5v/1000
      self.f_high_5v = self.high_5v/1000
      self.f_low_5v = self.low_5v/1000

      self.f_nominal_12v = self.nominal_12v/1000
      self.f_high_12v = self.high_12v/1000
      self.f_low_12v = self.low_12v/1000
      ICmd.ClearBinBuff(BWR)

      for test_num in range(0, len(TP.prm_IntfTest["tests"])):
         test_name = TP.prm_IntfTest["tests"][test_num]

         re_pattern = re.compile("[HNL]-H")
         objMatch = re_pattern.match(test_name)
         if objMatch != None and objMatch.group() == test_name:
            volts12 = self.high_12v

         else:
            re_pattern = re.compile("[HNL]-L")
            objMatch = re_pattern.match(test_name)
            if objMatch != None and objMatch.group() == test_name:
               volts12 = self.low_12v

            else:
               re_pattern = re.compile("[HNL]-N")
               objMatch = re_pattern.match(test_name)
               if objMatch != None and objMatch.group() == test_name:
                  volts12 = self.nominal_12v
               else:
                  ScrCmds.raiseException(11044, "Unrecognized parameter %s" % test_name)

         re_pattern = re.compile("N-[HNL]")
         objMatch = re_pattern.match(test_name)
         if objMatch != None and objMatch.group() == test_name:
            volts5 = self.nominal_5v
         else:
            re_pattern = re.compile("H-[HNL]")
            objMatch = re_pattern.match(test_name)
            if objMatch != None and objMatch.group() == test_name:
               volts5 = self.high_5v
            else:
               re_pattern = re.compile("L-[HNL]")
               objMatch = re_pattern.match(test_name)
               if objMatch != None and objMatch.group() == test_name:
                  volts5 = self.low_5v
               else:
                  ScrCmds.raiseException(11044, "Unrecognized parameter %s" % test_name)

         objMsg.printMsg("TestName: %s 5V= %s 12V = %s" % (test_name, str(volts5), str(volts12)))
         if testSwitch.FE_0145513_357552_P_IF3_IGNORE_11107_ERRORS:
            objPwrCtrl.powerCycle(volts5, volts12, ataReadyCheck = True)
         else:
            objPwrCtrl.powerCycle(volts5, volts12, ataReadyCheck = False)

         msg = 'Sequential Write Read Mode=PIOMode LBA=0 Count=256'
         ICmd.HardReset()
         data = ICmd.SequentialWRDMA(0, 256, 256, 256, 0, 1)
         if data['LLRET'] == 0:
            objMsg.printMsg('%s: Passed' %msg)
         else:
            objMsg.printMsg('%s: Failed data: %s' %(msg, `data`))

            ecDict = {  'N-N': (12361,'Nom/Nom (5V/12V)'),
                        'N-H': (12362,'Nom/High (5V/12V)'),
                        'N-L': (12363,'Nom/Low (5V/12V)'),
                        'H-N': (12364,'High/Nom (5V/12V)'),
                        'H-H': (12365,'High/High (5V/12V)'),
                        'H-L': (12366,'High/Low (5V/12V)'),
                        'L-N': (12367,'Low/Nom (5V/12V)'),
                        'L-H': (12368,'Low/High (5V/12V)'),
                        'L-L': (12369,'Low/Low (5V/12V)'),
                     }
            ScrCmds.raiseException(ecDict[test_name][0],'Proc Final-Interface Voltage %s.' % ecDict[test_name][1])

         end_time = time.time()
         test_time = end_time - start_time

      if testSwitch.IOWriteReadRemoval:
         RWDict = []
         RWDict.append ('Read')
         RWDict.append (0)
         RWDict.append (256)
         RWDict.append ('VoltageHighLow')
         objMsg.printMsg('WR_VERIFY appended - %s' % (RWDict))
         TP.RWDictGlobal.append (RWDict)

