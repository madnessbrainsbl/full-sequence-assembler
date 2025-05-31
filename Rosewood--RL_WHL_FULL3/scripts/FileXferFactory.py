#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Process to DUT file handling factory
# $RCSfile: IntfClass.py,v $
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/FileXferFactory.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/FileXferFactory.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import ScrCmds

import types
import os, stat

import pcfile
import dlfile

REQUEST_HOST_FILE_BLOCK = 21
REQUEST_DRIVEFW_FILE_BLOCK = 6

# snippets from transfer_types.h
PCFILE_REQUEST_TYPES = (80, #OPEN file
                        81, #Read file
                        82, #write file
                        83, #close file
                        84, #delete file
                     )
DLFILE_REQUEST_TYPES = (   REQUEST_DRIVEFW_FILE_BLOCK, #Request file with attached TPM from host. EG test 8
                           16, 17, #Request, Send binary results file to host. EG. test 210, 237, 251, 37, 152
                           REQUEST_HOST_FILE_BLOCK, #generic dlfile block... typically if dlfile= param api is supported by test
                           23, #TPM
                           63, #Request MIF data
                           70, #SF3 Overlay
                           71, #IO Overlay
                     )

class FileXferFactory(object):

   def __init__(self, fileObj, requestTypes, useCMLogic = 0):

      self.fileObj = fileObj

      if type(requestTypes) not in [types.TupleType, types.ListType]:
         if testSwitch.BF_0123842_231166_FILE_XFER_FIX_BNCH_MULTI_BLOCK:
            requestTypes = [requestTypes,]
         else:
            requestTypes = (requestTypes,)
      if testSwitch.BF_0123842_231166_FILE_XFER_FIX_BNCH_MULTI_BLOCK:
         self.requestTypes = list(requestTypes)
      else:
         self.requestTypes = requestTypes

      self.handler = self.__idHandler()(userFileWrapper(self.fileObj))
      RegisterResultsCallback(self.processCallback, self.requestTypes, useCMLogic)

   def close(self):
      RegisterResultsCallback('', self.requestTypes, 1)


   def processCallback(self, requestData, currentTemp, drive5, drive12, collectParametric):
      SendBuffer(self.handler.processRequest(requestData))

      if testSwitch.WA_0262223_480505_FIX_QNR_CODE_DOWNLOAD_ISSUE_FOR_PSTR:
         if ord(requestData[0])==6 and self.handler.isLastProcessRequest(): # fixed QNR download issue for PSTR
            sleepTime = 0.5 # 0.05 # checkSRQ retry algorithm in CM code
            import time
            for i in range(8):
               time.sleep(sleepTime)
               sleepTime = sleepTime * 2
               if sleepTime > 6:
                  sleepTime = 6
               PBlock("Escape") # send any character for PSTR

   def __idHandler(self):
      for reqType in self.requestTypes:
         if reqType in PCFILE_REQUEST_TYPES:
            return pcfile.PCFile

         elif reqType in DLFILE_REQUEST_TYPES:
            return dlfile.DLFile

      else:
         ScrCmds.raiseException(11049, "Unknown request type entered!")



class userFileWrapper:
   GENERIC_FILE = 0
   MEM_FILE = 1
   SYS_FILE = 2

   def __init__(self, file_input):
      self.fObj = file_input
      self.ftype = self.__determineType(file_input)

      if self.ftype == self.GENERIC_FILE:
         self.fObj = GenericResultsFile(self.fObj)
      elif self.ftype == self.SYS_FILE:
         self.fObj = open(file_input)


   def name(self):
      if self.ftype == self.MEM_FILE:
         return repr(self.fObj)
      else:
         return self.fObj.name
   def size(self):
      if self.ftype == self.GENERIC_FILE:
         return self.fObj.size()
      elif self.ftype == self.MEM_FILE:
         return len(self.fObj.getvalue())
      else:
         return os.stat(self.fObj.name)[stat.ST_SIZE]


   def __determineType(self, file_input):
      if type(file_input) == types.StringType:
         if os.path.isfile(file_input):

            if ScrCmds.getSystemResultsPath() in file_input:
               return self.GENERIC_FILE
            else:
               return self.SYS_FILE
      else:
         if hasattr(file_input, 'getvalue'):
            return self.MEM_FILE
         elif hasattr(file_input,  'size'):
            return self.GENERIC_FILE
         else:
            return self.SYS_FILE

   def __call__(self, mode):
      if self.ftype == self.GENERIC_FILE:
         self.fObj.open(mode)
         return self.fObj
      elif self.ftype == self.SYS_FILE:
         return open(self.fObj.name, mode)
      elif self.ftype == self.MEM_FILE:
         return self.fObj
