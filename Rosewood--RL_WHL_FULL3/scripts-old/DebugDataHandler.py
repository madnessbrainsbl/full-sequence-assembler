#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Handles all printing routines in common object that has global verbosity and formatting controls
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DebugDataHandler.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DebugDataHandler.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from cStringIO import StringIO
import binascii
from Test_Switches import testSwitch

DEBUG = 0

class debugMessageObject(object):

   def __init__(self):
      self.debugFile = GenericResultsFile('suppressedDataFile.bin')
      self.debugIndex = []
      self.clearDebugFile()

   def clearDebugFile(self):
      if DEBUG > 0:
         TraceMessage("Clearing debug file")
      #Clear out suppressed data from state if we passed.
      self.debugFile.open('wb')
      self.debugFile.write('')
      self.debugFile.close()

      self.debugIndex = []

   def writeDebugData(self, data):
      resultsPtr = ResultsFile.size()
      debugPtr = self.debugFile.size()
      dlen = len(data)

      self.debugFile.open('ab')
      try:
         self.debugFile.write(data)
      finally:
         self.debugFile.close()

      dbgTuple = (resultsPtr, dlen, debugPtr)
      self.debugIndex.append(dbgTuple)

      if DEBUG > 2:
         TraceMessage("Debug Tuple: %s" % (dbgTuple,))


   def flushDebugData(self):
      if len(self.debugIndex) == 0:
         return
      runNum = 10
      ResultsFile.open('rb')
      try:
         tmpFile = StringIO(ResultsFile.read())
      finally:
         ResultsFile.close()


      #Clear Binary Results file
      ResultsFile.open('wb')
      ResultsFile.write('')
      ResultsFile.close()

      #Setup debugFile
      self.debugFile.open('rb')

      Temp_RF_Pointer = 0

      for RF_Pointer, dataLength, DF_Pointer in self.debugIndex:

         RFDataLen = RF_Pointer - Temp_RF_Pointer
         if RFDataLen > 0:
            #Write up to the break point
            tmpFile.seek(Temp_RF_Pointer)
            resData = tmpFile.read(RFDataLen)
            WriteToResultsFile(resData)
            runNum = 10
            if DEBUG > 0:
               TraceMessage("Writing from original file from %d to %d @ %d" % (Temp_RF_Pointer, RF_Pointer, ResultsFile.size()))
               TraceMessage("\tLast 20 bytes: %s" % binascii.b2a_hex(resData[-20:]))

         #Write the debug data
         self.debugFile.seek(DF_Pointer)
         dbgData = self.debugFile.read(dataLength)
         WriteToResultsFile(dbgData)

         if DEBUG > 0:
            if runNum > 0:
               TraceMessage(binascii.b2a_hex(dbgData))
               runNum -= 1

            TraceMessage("Wrote %d bytes of data to binary file" % dataLength)
         if testSwitch.BF_0163631_340210_CORRECT_FILE_POS == 1:
            for tblIdx, TblAttrList in self.dut.dblParser.objDbLogIndex.indicies:
               for TblAttrs in TblAttrList:
                  if TblAttrs[0] >= RF_Pointer:
                     TblAttrs[0] = TblAttrs[0] + dataLength;
         #Increment RF_Pointer to next block
         Temp_RF_Pointer = RF_Pointer#RF_Pointer+1

      #Clean up the memory
      self.debugFile.close()
      tmpFile.close()
      self.clearDebugFile()

