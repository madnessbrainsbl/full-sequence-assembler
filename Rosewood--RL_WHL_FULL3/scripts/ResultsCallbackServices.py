#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Classes to setup the executable scripts, err handling and dnld codes for a particular config
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ResultsCallbackServices.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ResultsCallbackServices.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import MessageHandler as objMsg

import time, traceback, binascii

DEBUG = 1
REQUEST_CURRENT_DATE = 31

FAIL_RESP = '\x00\x00\x00'

# Results callback for REQUEST_CURRENT_DATE handling
def Register_REQUEST_CURRENT_DATE_handler():
   RegisterResultsCallback(processREQUEST_CURRENT_DATE, REQUEST_CURRENT_DATE, useCMLogic=0)

def processREQUEST_CURRENT_DATE(requestData,currentTemp= 0,drive5 = 0,drive12= 0,collectParametric = 1):
   """
   Process request callback for time request REQUEST_CURRENT_DATE = 31 that returns the
      current integer value of seconds from EPOCH to drive and date_time

      taken from core_datetime.h
      typedef struct date_and_time
         {
            uint16 Year;    // no rules
            uint8  Month;   // 1-12
            uint8  Day;     // 1-31
            uint8  Hour;    // 0-23
            uint8  Minute;  // 0-59
            uint8  Second;  // 0-59
         } date_and_time;
   """
   resultsKey = 0
   try:
      resultsKey = ord(requestData[0])
   except:
      traceback.print_exc()
      objMsg.printMsg("Error in attempting results key parsing for %s" % (requestData,))


   if DEBUG:
      objMsg.printMsg("Got request for %d" % (resultsKey,))

   if resultsKey == REQUEST_CURRENT_DATE:
      refTime = time.time()

      date = time.localtime(refTime)

      if DEBUG:
         objMsg.printMsg("time:%d" % refTime)
         objMsg.printMsg("date:%02d/%02d/%04d %02d:%02d:%02d" % (date[1],date[2],date[0],date[3],date[4],date[5]))

      resp = struct.pack('B',  REQUEST_CURRENT_DATE, )
      resp += struct.pack('Q', int(refTime))
      resp += struct.pack('HBBBBB', *date[0:6])

      if DEBUG:
         objMsg.printMsg("Returning %s" % (binascii.hexlify(resp),))
      SendBuffer(resp)

   else:
      SendBuffer(FAIL_RESP)
      objMsg.printMsg("Invalid resultsKey: %s" % (repr(resultsKey),))
