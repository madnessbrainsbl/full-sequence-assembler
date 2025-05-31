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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/FDE.py $
# $Revision: 4
# $DateTime: 11/27/07
# $Author: Sharon Wang
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/FDE.py#1 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import math, types, re, os
import random
import Setup
from Drive import objDut
import ScrCmds
import binascii, struct, base64, time
import sys

# *** GLOBALS
global lastInitiatorData
lastInitiatorData = 0x0
global lastInitiatorFileName
lastInitiatorFileName = ""


class CFDE_Seq:
   def __init__(self):
      pass

   #----------------------------------------------------------------------------
   def ESGSaveResults(self,data,currentTemp,drive5,drive12,collectParametric):
      # Save to a file in the STP format
      import struct,array,time

      size = len(data) + 10
      currentTime = time.time()
      v5 = (drive5/1000.0 - 5.0)/0.014668 + 86  # per STP report generator file c_rep.cpp
      v12 = (drive12/1000.0 - 12.0)/0.0324774 + 115  # per STP report generator file c_rep.cpp
      if v5 < 0: v5 = 0  # rpt gen does not handle negative values here
      if v12 < 0: v12 = 0  # rpt gen does not handle negative values here
      rptTemp = currentTemp/10 # convert decivolts to volts; Centigrade

      # WRITE THESE VALUES INTO A BINARY STRING
      str1 = struct.pack('<HLbbbb',size,currentTime,v5,v12,collectParametric,rptTemp)

      # SET HI BIT IN TEST NUMBER IF THIS IS PARTIAL RESULTS
      block_code = data[0]

      char_1 = ord(data[1])
      if '\003'==block_code:
         char_1 = char_1 | 0x80

      # WE DON'T SAVE THE FIRST BYTE OF DATA
      data = chr(char_1) + data[2:]

      # CREATE AN ARRAY OF BYTES SO WE CAN WRITE IT TO THE FILE
      str2 = (array.array('B',data)).tostring()

      str3 = "\000"  # ALIGNMENT BYTE

      WriteToResultsFile(str1+str2+str3)

   #----------------------------------------------------------------------------
   def getSID(self,updateAttrs=1):
      '''getSID(...): Gets/generates a Secure ID (i.e. 'SID' or 'MSID') that is printed
      on the drive label and stored internally on the drive in the EF_SID
      file.  It will also create the appropriate drive attribute in FIS.'''

      sidStatus = "1" # 0 = get exisiting SID from FIS
                    # 1 = calculate new SID

      sidLength = 32  # =25, per TCG Storage Architecture Core Spec


      # Possible SID characters:
      # random ordering of 34 uppercase letters (No 'I' and No 'O') and
      # numerals 0 through 9
      # per TCG Storage Architecture Core Spec
      charChoices = ['H','U','7','C','J','9','T','5','R','B',\
                   'G','M','E','0','F','Z','4','8','Y','K',\
                   '2','L','V','D','S','1','A','W','3','Q',\
                   'X','6','P','N']


      # Create an empty SID string to be filled with random characters
      sidStr = ''

      if DriveAttributes.has_key('TD_SID') and len(DriveAttributes['TD_SID']) == 32:
         sidStr = DriveAttributes['TD_SID']
         ScrCmds.statMsg("FIS SID = %s\n" % sidStr)
         sidStatus = "0"
      elif not DriveAttributes.has_key('TD_SID') or len(DriveAttributes['TD_SID']) != 32:
         ScrCmds.statMsg("no SID found @ FIS Server - calculating virgin SID\n")

         # Shuffle the list prior to seeding the random number generator -
         # this ensures a unique SID even if the 'RandomSeed' value is the
         # same as a previous one.  Prevents duplicate SID's !!!
         random.shuffle(charChoices)
         # Seed the python random-number generator from an OS-specific
         # randomness source
         random.seed()


         # Generate a string of random characters
         for i in range(0, sidLength):
            # Generate a random number between 0 and 34, and use it to
            # select a character from the choices list
            # NOTE: random() generates a number between 0 and 1
            sidStr += charChoices[int(random.random() * 34)]

         # Put the SID into attributes (and automatically send to the Host)
         if updateAttrs:
            DriveAttributes['TD_SID'] = sidStr
            ScrCmds.statMsg("virgin SID = %s\n" % sidStr)

      return sidStatus,sidStr

   #----------------------------------------------------------------------------
   def CustomRequestSecureIDHandler(self):
      '''custom handler for resultsKey=32 - Request Secure ID (SID)'''
      # Determine the MSID
      sidStatus,sid = self.getSID()
      # ScrCmds.statMsg("SID = %s\n" % sid)

      # Set up frame of data to send to initiator
      frame = sidStatus + sid + HDASerialNumber.upper()
      # frame = "\x22\x25\x00\x00" + sidStatus + sid + HDASerialNumber.upper()

      ScrCmds.statMsg("sending frame of data w/ SID to the initiator\n")
      SendBuffer(frame)



      # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
      # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      # NOTE! this function has not been checked-out yet (kjb 11/18/07)
      # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
      # ===================================================================
      # CustomRequestManufacturingKeyHandler():
      # customer handler for resultsKey=XX - Request Mfg. Key
      # ===================================================================
      # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      # M2TD Cryptographic Infrastructure - KCI Interface Spec: Section 2.2
      # kjb @ 11/18/07
   #----------------------------------------------------------------------------
   def CustomRequestManufacturingKeyHandler(self):
      ScrCmds.statMsg("*** Request Manufacturing Key\n")
      stat = 1 # default = FAIL

      ScrCmds.statMsg("-> RequestService('ReqMfgKey',(%s))\n" %(HDASerialNumber.upper()))
      method,prms = RequestService('ReqMfgKey',(HDASerialNumber.upper())) # requestManufacturingKey
      # ScrCmds.statMsg("method: %s\n" % method)
      # ScrCmds.statMsg("prms: %s\n" % prms)

      if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
         if prms.has_key('manufacturingKey'):
            responseString = prms['manufacturingKey']
            # ScrCmds.statMsg "response from server         ", responseString
            # ScrCmds.statMsg "base64 decoded               ", base64.b64decode(responseString)
            mfgKeyString = binascii.b2a_hex(base64.b64decode(responseString))
            if len(mfgKeyString) != 32: # 32 chars = 16 bin-nibble-bytes
               ScrCmds.statMsg("Mfg. Key = %i bytes, not 16 bytes\n" % len(mfgKeyString))
            else:
               ScrCmds.statMsg("Mfg. Key = %s\n" % mfgKeyString)
               mfgKey = binascii.a2b_hex(mfgKeyString)
               stat = 0 # PASS
         else:
            ScrCmds.statMsg('[rKey=XX] "manufacturingKey" not found in data from server\n')
      else:
         ScrCmds.statMsg("[rKey=XX] data from server is garbled\n")

      if not stat:
         # BYTE[0]: resultsKey XX (hex XX)
         # BYTE[1]: mfgKey length of 16 bytes (hex 10)
         # BYTE[2]: null 0x00
         # BYTE[3]: null 0x00
         # ((( data )))
         frame = "\x22\x10\x00\x00" + mfgKey
      else:
         # If we could not get a key, the data length is 0 & no key is sent
         frame = "\x22\x00\x00\x00"

      ScrCmds.statMsg("sending frame of data w/ mfgKey to the initiator\n")
      SendBuffer(frame)
      # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
      # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      # NOTE! the above function has not been checked-out yet
      # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>



   # ===================================================================
   # CustomRequestManufacturingAuthenticationHandler(...):
   # ((( Bob S. says this is MakerSymK something blah-blah-blah... )))
   # INPUTS:
   # * rcvData         : Random Challenge Value Data (from drive via initiator)
   # * HDASerialNumber : HDASerialNumber
   # RETURN(S):
   # * mfgAuthKey      : Manufacturing Authentication Key
   # custom handler for resultsKey=33 - Request Mfg. Auth.
   # M2TD Cryptographic Infrastructure - KCI Interface Spec: Section 2.3
   #----------------------------------------------------------------------------
   def CustomRequestManufacturingAuthenticationHandler(self,nonce): # nonce=RandomChallengeValue
      stat = 1 # default = FAIL

      index = 0

      # Grab the Random Challenge Value (RCV) sent to us
      # this assignment is done only incase nonce is embeded in a data-chunk
      # i.e. nonce data passed to function() is "header+nonce+junk"
      #      rCV = nonce[startByte:stopByte], or,
      #      rCV = nonce[startByte:startByte+32]

      #randomChallengeValue = nonce[index:]
      randomChallengeValue = base64.b64encode(binascii.a2b_hex(nonce))
      TraceMessage("nonce: %s" %nonce)
      TraceMessage("randomChallengeValue: %s" %randomChallengeValue)
      TraceMessage("type of nonce: %s" % type(nonce))

      #
      # DANGER!!!   DANGER!!!   DANGER!!!   DANGER!!!   DANGER!!!   DANGER!!!   DANGER!!!   DANGER!!!
      # This Handler ('ReqMfgAuth') needs to support RCW w/ & w/o hdaSerialNumber
      # DANGER!!!   DANGER!!!   DANGER!!!   DANGER!!!   DANGER!!!   DANGER!!!   DANGER!!!   DANGER!!!
      #
      # ScrCmds.statMsg("-> RequestService('ReqMfgAuth',(%s, %s))\n" % (randomChallengeValue, HDASerialNumber.upper()))
      # method,prms = RequestService('ReqMfgAuth',(randomChallengeValue, HDASerialNumber.upper()))  # Provide SN for Drive Unique Manufacturing Key
      ScrCmds.statMsg("-> RequestService('ReqMfgAuth',(%s))\n" % (randomChallengeValue))
      #***************
      #TraceMessage("RequestService: %s" % RequestService('ReqMfgAuth',("f7352bbecac210a94912cc8d867aa62e66c8796c0ad464d977fa53b0d06fcf18",)))
      method,prms = RequestService('ReqMfgAuth',(randomChallengeValue))  # Provide SN for Drive Unique Manufacturing Key
      #***************
      TraceMessage("method: %s" % method)
      TraceMessage("prms: %s" % prms)

      # ScrCmds.statMsg("method %s\n" % method)
      # ScrCmds.statMsg("prms   %s\n" % prms)

      if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
         if prms.has_key('AuthenticationResponse'):
            responseString = base64.b64decode(prms['AuthenticationResponse'])
            # ScrCmds.statMsg("response from server    = %s\n" % responseString)
            mfgAuthKeyString = binascii.b2a_hex(responseString)
            ScrCmds.statMsg("HDA Serial Number = %s\n" % HDASerialNumber.upper())
            ScrCmds.statMsg("Mfg.Auth.Key = %s\n" % mfgAuthKeyString)
            if len(mfgAuthKeyString) != 64: # 64 chars = 32 bin-nibble-bytes
               ScrCmds.statMsg("Mfg. Auth. Key = %i bytes, not 32 bytes\n" % len(mfgAuthKeyString))
            else:
               mfgAuthKey = binascii.a2b_hex(mfgAuthKeyString)
               stat = 0 # PASS
         else:
           ScrCmds.statMsg('[rKey=33] "AuthenticationResponse" not found in data from server\n')
      else:
         ScrCmds.statMsg("[rKey=33] data from server is garbled\n")

      if not stat:
         # BYTE[0]: resultsKey 33 (hex 21)
         # BYTE[1]: reqMfgAuth Key=32 bytes (hex 20)
         # BYTE[2]: null 0x00
         # BYTE[3]: null 0x00
         # ((( data )))
         frame = "\x21\x20\x00\x00"  + mfgAuthKey
      else:
         # If we could not get a key, the data length is 0 & no key is sent
         frame = "\x21\x00\x00\x00"

      ScrCmds.statMsg("sending frame of data w/ mfgAuthKey to the initiator\n")
      SendBuffer(frame)



   # ===================================================================
   # CustomRequestSerialPortEnableKeyHandler():
   # customer handler for resultsKey=34 - Request SP Enable Key
   # ===================================================================
   # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   # M2TD Cryptographic Infrastructure - KCI Interface Spec: Section 2.4
   # kjb @ 09/26/07
   #----------------------------------------------------------------------------
   def CustomRequestSerialPortEnableKeyHandler(self):
      ScrCmds.statMsg("*** Request SerialPort Enable Key\n")
      stat = 1 # default = FAIL

      ScrCmds.statMsg("-> RequestService('ReqSPEKey',(%s))\n" %(HDASerialNumber.upper()))
      method,prms = RequestService('ReqSPEKey',(HDASerialNumber.upper())) # requestSerialPortEnableKey
      # ScrCmds.statMsg("method: %s\n"  % method)
      # ScrCmds.statMsg("prms: %s\n" % prms)

      if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
         if prms.has_key('serialPortEnableKey'):
            responseString = prms['serialPortEnableKey']
            # ScrCmds.statMsg "response from server         ", responseString
            # ScrCmds.statMsg "base64 decoded               ", base64.b64decode(responseString)
            spEnableKeyString = binascii.b2a_hex(base64.b64decode(responseString))
            if len(spEnableKeyString) != 32: # 32 chars = 16 bin-nibble-bytes
               ScrCmds.statMsg("SP Enable Key = %i bytes, not 16 bytes\n" % len(spEnableKeyString))
            else:
               ScrCmds.statMsg("sPort Enable Key = %s\n" % spEnableKeyString)
               spEnableKey = binascii.a2b_hex(spEnableKeyString)
               stat = 0 # PASS
         else:
           ScrCmds.statMsg('[rKey=34] "serialPortEnableKey" not found in data from server\n')
      else:
         ScrCmds.statMsg("[rKey=34] data from server is garbled\n")

      if not stat:
         # BYTE[0]: resultsKey 34 (hex 22)
         # BYTE[1]: spEnableKey length of 16 bytes (hex 10)
         # BYTE[2]: null 0x00
         # BYTE[3]: null 0x00
         # ((( data )))
         frame = "\x22\x10\x00\x00" + spEnableKey
      else:
         # If we could not get a key, the data length is 0 & no key is sent
         frame = "\x22\x00\x00\x00"

      ScrCmds.statMsg("sending frame of data w/ spEnableKey to the initiator\n")
      SendBuffer(frame)

   # ===================================================================
   # CustomRequestSerialPortEnableAuthenticationHandler(...):
   # customer handler for resultsKey=35 - SP Enable Authentication
   # ===================================================================
   # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   # M2TD Cryptographic Infrastructure - KCI Interface Spec: Section 2.5
   # kjb @ 10/04/07
   #----------------------------------------------------------------------------
   def CustomRequestSerialPortEnableAuthenticationHandler(self,nonce):
      ScrCmds.statMsg("*** Request SerialPort Enable Authentication\n")
      stat = 1 # default = FAIL

      index = 0

      # Grab the Random Challenge Value (RCV) sent to us
      # this assignment is done only incase nonce is embeded in a data-chunk
      # i.e. nonce data passed to function() is "header+nonce+junk"
      #      rCV = nonce[startByte:stopByte], or,
      #      rCV = nonce[startByte:startByte+32]
      randomChallengeValue = base64.b64encode(binascii.a2b_hex(nonce[index:]))
      #randomChallengeValue = nonce[index:]

      ScrCmds.statMsg("-> RequestService('ReqSPEAuth',(%s, %s))\n" %(randomChallengeValue, HDASerialNumber.upper()))
      method,prms = RequestService('ReqSPEAuth',(randomChallengeValue, HDASerialNumber.upper()))
      # ScrCmds.statMsg("method: %s\n" % method)
      # ScrCmds.statMsg("prms: %s\n" % prms)

      if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
         if prms.has_key('AuthenticationResponse'):
            responseString = prms['AuthenticationResponse']
            # ScrCmds.statMsg "response from server         ", responseString
            # ScrCmds.statMsg "base64 decoded               ", base64.b64decode(responseString)
            spEnableAuthKeyString = binascii.b2a_hex(base64.b64decode(responseString))
            if len(spEnableAuthKeyString) != 64: # 64 chars = 32 bin-nibble-bytes
               ScrCmds.statMsg("SP Enable Auth. Key = %i bytes, not 32 bytes\n" % len(spEnableAuthKeyString))
            else:
               ScrCmds.statMsg("sPort Enable Auth. Key = %s\n" % spEnableAuthKeyString)
               spEnableAuthKey = binascii.a2b_hex(spEnableAuthKeyString)
               stat = 0 # PASS
         else:
           ScrCmds.statMsg('[rKey=35] "serialPortEnableAuthKey" not found in data from server\n')
      else:
         ScrCmds.statMsg("[rKey=35] data from server is garbled\n")

      if not stat:
         # BYTE[0]: resultsKey 35 (hex 22)
         # BYTE[1]: spEnableAuthKey length of 16 bytes (hex 10)
         # BYTE[2]: null 0x00
         # BYTE[3]: null 0x00
         # ((( data )))
         frame = "\x22\x10\x00\x00" + spEnableAuthKey
      else:
         # If we could not get a key, the data length is 0 & no key is sent
         frame = "\x22\x00\x00\x00"

      ScrCmds.statMsg("sending frame of data w/ spEnableAuthKey to the initiator\n")
      SendBuffer(frame)

   #----------------------------------------------------------------------------
   def CustomHandler(self,data,currentTemp=0,drive5=0,drive12=0,collectParametric=0):
      '''Definition of the generic "top-level" customer handler
      Custom Handler for resultsKeys/fileXferTypes
      * add defaults so we can pass only data (in manual, non-initiator mode)'''
      stat = 1 # default= FAIL

      # ScrCmds.statMsg "\n"
      ScrCmds.statMsg ("===> %s\n" % binascii.b2a_hex(data))

      # Get the resultsKey (a.k.a. Bob's fileXferType)
      resultsKey = ord(data[0])
      TraceMessage("resultsKey: %s" %resultsKey)

      # ScrCmds.statMsg("resultsKey: %s\n" % resultsKey)

      if resultsKey == 32:
         self.CustomRequestSecureIDHandler()
         # elif resultsKey == XX:
         #     self.CustomRequestManufacturingKeyHandler()
      elif resultsKey == 33:
         self.CustomRequestManufacturingAuthenticationHandler(lastInitiatorData)
      elif resultsKey == 34:
         self.CustomRequestSerialPortEnableKeyHandler()
      elif resultsKey == 35:
         self.CustomRequestSerialPortEnableAuthenticationHandler(lastInitiatorData)
      elif resultsKey == 37:
         self.CustomRequestGetCertifiedKeyPairHandler()
      else:
         # ScrCmds.statMsg("OMG!  Eeek!\n")
         exceptMsg = "ABORT! unexpected resultsKey" # @ + this_file_name + ":" + this_function_name + "()"
         raise StandardError, exceptMsg

   #----------------------------------------------------------------------------
   def customInitiatorDataFileNameHandler(self, iData):
      '''INPUTS:
         * iData         : fileName (for file containing data from initiator)
         custom handler for resultsKey=80 - fileName of data from initiator'''
      stat = 1 # default = FAIL

      # Jump over the 3 bytes of (binary) header information
      index = 3

      # Grab the Random Challenge Value (RCV) sent to us
      # fileName = binascii.b2a_hex(iData[index:])
      fileName = iData[index:]

      ScrCmds.statMsg("-> Initiator Data FileName = %s\n" % fileName)

      return fileName

   #----------------------------------------------------------------------------
   def customInitiatorDataHandler(self, iData):
      '''INPUTS:
         * iData         : data (from initiator)
         custom handler for resultsKey=82 - data from initiator'''
      stat = 1 # default = FAIL

      # Jump over the 3 bytes of (binary) header information
      index = 3

      # Grab the Random Challenge Value (RCV) sent to us
      # NOTE!  this "Handler" currently returns only 32 bytes of data
      nonce = binascii.b2a_hex(iData[index:index+32])

      ScrCmds.statMsg("-> Nonce [from initiator/drive]=%s\n" % nonce)

      return nonce

   #----------------------------------------------------------------------------
   def customInitiatorHandler(self, data, *args, **kargs):
      '''Definition of the generic "top-level" customer handler
      resultsKeys 80 & 82
      add defaults so we can pass only data (in manual, non-initiator mode)'''
      #this_function_name = sys._getframe().f_code.co_name
      #this_file_name = sys._getframe().f_code.co_filename

      stat = 1 # default= FAIL

      global lastInitiatorData

      # ScrCmds.statMsg "\n"
      # ScrCmds.statMsg "===> %s\n" % binascii.b2a_hex(data)

      # Get the resultsKey
      resultsKey = ord(data[0])
      ScrCmds.statMsg ("===> resultsKey: %s\n" % hex(resultsKey))

      if resultsKey == 80:
         lastInitiatorFileName = self.customInitiatorDataFileNameHandler(data)
      elif resultsKey == 82:
         lastInitiatorData = self.customInitiatorDataHandler(data)
      else:
         # ScrCmds.statMsg("OMG!  Eeek!\n")
         exceptMsg = "ABORT! unexpected resultsKey" # @ + this_file_name + ":" + this_function_name + "()"
         raise StandardError, exceptMsg

   #----------------------------------------------------------------------------
   def CustomRequestGetCertifiedKeyPairHandler(self):
      #print "*** Request Certified Key Pair"
      stat = 1 # default = FAIL
      #print "Entering Custom Request Mfg Key Auth handler - 37 - get certified key pair"

      d = ['primeExponentP','primeExponentQ','crtCoefficient','montModulus','pubExp','montPrimeQ','montPrimeP','primeQ',
         'primeP','privExp','modulus','RSAPrivateKey','Certificate']

      #print "RequestService('GetCertifiedKeyPair',(ZG7F02M','SIGN','1.2.3.4.5.6.7.8.9.0))"
      #method,prms = RequestService("GetCertifiedKeyPair",('8ZG7F02M','SIGN','1.2.3.4.5.6.7.8.9.0'))
      method,prms = RequestService("GetCertifiedKeyPair",(HDASerialNumber,'SIGN','1.2.3.4.5.6.7.8.9.0'))
      frame = "\x25\x00\x00\x00"
      #print "sending answer to get_pc_file to the initiator"
      SendBuffer(frame)

      if len(prms) and prms.get('EC',(0,'NA'))[0] == 0:
         #print prms

         for x in d:
            if prms.has_key(x):
               second_transfer_len = 0
               responseString = prms[x]
               spEnableKeyString = binascii.b2a_hex(base64.b64decode(responseString)) #binary to ascii decoded string
               ScrCmds.statMsg("x = %i bytes" % len(spEnableKeyString))             #print the length of the ascii string
               ScrCmds.statMsg("x = %s" % spEnableKeyString)                           #print the ascii string
               spEnableKey = binascii.a2b_hex(spEnableKeyString)
               overall_len = len(spEnableKey)
               if overall_len > 512:
                  second_transfer_len = overall_len - 512
                  frame = spEnableKey[:512]
               else:
                  frame = spEnableKey
               SendBuffer(frame)
               if second_transfer_len:
                  frame = spEnableKey[512:]
                  SendBuffer(frame)
            else:
             ScrCmds.statMsg("key doesn't exist")                           #print the ascii string
      else:
         statMsg('[34]' + __name__ + "data from server is garbled")
