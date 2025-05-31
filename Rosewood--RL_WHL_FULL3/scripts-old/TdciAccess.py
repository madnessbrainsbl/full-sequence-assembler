#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: This file provides methods to 
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File:
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header:
# Level: 4
#-----------------------------------------------------------------------------------------#
from Constants import *
import MessageHandler as objMsg
import traceback
import ScrCmds
from Drive import objDut


retryCount = 0
MAX_RETRIES = 1000
cumulativeDelay = 0

MAX_RETRY_IDX = 0
DEF_DELAY_IDX = 1
sedDebug = 0

#TDCI error codes are documented https://docs.google.com/a/seagate.com/file/d/0Bwg6eKSgkhkMeXRKWGhMaVBXQk0/edit?usp=drive_web
Retry_Matrix = {
   #unique situations go here
   50001       : (0, 0), # Misc Host Exceptions- Check host logs
   50002       : (0, 0), # Invalid URL- Check host logs

   "Range":
      # start    [max retries, default retry]
      {  0     : (0, 0), #unknown
         10000 : (0, 0), #TDCI parameter error from script
         20000 : (4, 1200, 120, 600), #Other retries needed
         40000 : (0, 0), #unknown
         },
   }

sortedRetRange = sorted(Retry_Matrix["Range"].keys())

def getRetryTuple(errorCode, errorMsg, currentRetryCount):
   # Function returns the delay time or raises the error code as an exception

   retTuple = Retry_Matrix.get(errorCode, None)
   if retTuple == None:
      retTuple = sortedRetRange[0]
      for retRange in sortedRetRange:
         if errorCode < retRange:
            break
         else:
            retTuple = Retry_Matrix["Range"][retRange]

   if retTuple[MAX_RETRY_IDX] <= currentRetryCount:
      ScrCmds.raiseException(errorCode, errorMsg)
   
   if currentRetryCount+2 >= len(retTuple):
      return retTuple[DEF_DELAY_IDX]
   else:
      return retTuple[currentRetryCount+2]

def getCumulativeDelay (retryTuple):
   x = 0
   cumDelay = 0
   for x in xrange(retryTuple[MAX_RETRY_IDX]):

      if x+DEF_DELAY_IDX > len(retryTuple)-1:
         cumDelay += retryTuple[DEF_DELAY_IDX]
      else:
         cumDelay += retryTuple[x+DEF_DELAY_IDX]

   return cumDelay

def makeTDCICall( *args ):
   global retryCount
   global cumulativeDelay

   tdciFunction = args[0]
   retryCount = 0
   MAX_DELAY = 600

   
   reqTuple = tuple(list(args) + [ HOST_ID ])

   if 'getUniqueSCSAAssets' in args:
      reqTuple = tuple(list(args[0:4]) + [ HOST_ID ] + list(args[4:]))

   while 1:
      

      if sedDebug:
         objMsg.printMsg("TDCIServerRequest: %s" % (reqTuple,))

      method, returnValue = RequestService("TDCIServerRequest", reqTuple)

      objDut.driveattr.setdefault('TDCI_COMM_NUM', 0)
      objDut.driveattr['TDCI_COMM_NUM'] += 1

      # returnValue = {'EC': (22001, 'XmlRpcParseException: String index out of range: -1')}
      try:
         
         errorCode, errorMsg = returnValue['EC']
         if not errorCode:
            
            objMsg.printMsg('%s: %s - Error Code: %s - Error Message: %s - Retry: %s - prms: %s' % (method, tdciFunction, errorCode, errorMsg, retryCount, returnValue) )
            break

         delayTime = getRetryTuple(errorCode, errorMsg, retryCount)
         objMsg.printMsg('%s: %s - Error Code: %s - Error Message: %s - Retry: %s - Delay %s seconds' % ( method, tdciFunction, errorCode, errorMsg, retryCount, delayTime) )
         cumulativeDelay += delayTime
         ScriptPause(delayTime)
         retryCount += 1
      except:
         objMsg.printMsg(traceback.format_exc())
         objMsg.printMsg('%s: %s - EXCEPTION' % ( method, tdciFunction) )
         raise

      

   return method, returnValue
