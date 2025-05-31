#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: All script defined custom exceptions go in here
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Exceptions.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Exceptions.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
from Constants import *
#**********************************************************************************************************
#**********************************************************************************************************
class CStateException:
   """
      Use this exception for state machine control failures and to exit from state machine gracefully
   """
   pass

class CRaiseException(Exception):
   '''info'''
   args = []
   def __init__(self,exceptionTuple):
      self.failureData = exceptionTuple
      self.args = self.failureData

   def __str__(self):
      return `self.failureData`

   def __args__(self):
      return self.failureData

   def __getitem__(self, key):
      return self.args[key]


class CDependencyException(CRaiseException):
   """Dependency Exception
      Usage: raise CDependencyException, ('x', 'y')
   """
   def __init__(self, processFlag, externFlag):
      (mV3,mA3),(mV5,mA5),(mV12,mA12)  = GetDriveVoltsAndAmps()
      chamberTemp = ReportTemperature()/10.0
      voltages = (mV12/1000.0, mV5/1000.0)
      errInfo = ("%s requires %s" % (processFlag, externFlag), 0, 11049, 0)
      failureData = (errInfo, chamberTemp, voltages)
      CRaiseException.__init__(self, failureData)

class CReplugException(Exception):
   '''info'''
   def __init__(self,data):
      Exception.__init__(self,data)


class CFlashCorruptException(Exception):
   '''info'''
   def __init__(self,data):
      Exception.__init__(self,data)

class CDblogDataMissing(Exception):
   pass

class CReplugForTempMove(CRaiseException):
   '''Replug for drives which want to ramp temp in another proper slot'''
   pass

class BaudRateRejected(CRaiseException):
   '''Drive rejected baud rate'''
   pass

class SeaSerialRequired(CRaiseException):
   '''Process detected that a seaserial is required'''
   pass

class EndOfPackException(Exception):
   '''Process detected that the cmd reached end of pack/disc.'''
   pass

class InvalidTrackException(Exception):
   '''Process detected that an invalid track cmd was issued'''
   pass

class ExcessiveDieTempException(CRaiseException):
   '''Die temp exceeded pre-set maximum and potentially damaged part.'''
   pass
class BypassCustUniqueTest(Exception):
   '''Bypass the currently scheduled screen due to state logic.'''
   pass
