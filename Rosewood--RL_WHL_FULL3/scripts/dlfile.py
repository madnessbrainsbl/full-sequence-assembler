#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: DLFile handler- re-utilized from cm code file of same name by stuartm
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/dlfile.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/dlfile.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
import sys,os.path,stat,types
from Constants import *
import ScrCmds

FILE = 0
FILESIZE = 1
FILEOBJ = 2

class DLFile:

   def __init__(self, userFile):
      # prefix the path to the file


#     if not os.path.isfile(file):
#        msg = "%-7s FileIsMissing  %s" % (CellIndex,dfile,)
#
#        raise FOFFileIsMissing,msg

      fileObj = userFile('rb')
      fileSize = userFile.size() #os.stat(dfile)[stat.ST_SIZE]

      # this object stores file name, file size, and file object
      self.dlfile = (userFile.name(),fileSize,fileObj)

      self.isLastBlock = 0 # variable for check download last block

   def getFileSize(self):
      return self.dlfile[FILESIZE]

   def processRequest(self,requestData):
      # requestData is a string from the UUT asking for a block from a file
      # return a frame, raise an exception on error

      if not self.dlfile:
        msg = "%-7s FileIsMissing  Drive requests, but no dlfile." % (CellIndex,)

        raise FOFFileIsMissing,msg

      requestKey = ord(requestData[0])
      # code 6 typically requests a block of data from the download file;  get_data_file()
      if requestKey in [6]:
         blockSize = (int(ord(requestData[2]))<<8) + int(ord(requestData[3]))
         requestHI = requestData[4]
         requestLO = requestData[5]
         requestBlock = (int(ord(requestHI))<<8) + int(ord(requestLO))
      elif requestKey in [21,23,24,25]:
         blockSize = (int(ord(requestData[3]))<<8) + int(ord(requestData[2]))
         requestHI = requestData[5]
         requestLO = requestData[4]
         requestBlock = (int(ord(requestHI))<<8) + int(ord(requestLO))
      elif requestKey in [7]:
         blockSize = (int(ord(requestData[6]))<<8) + int(ord(requestData[7]))
         request24 = requestData[2]
         request16 = requestData[3]
         requestHI = requestData[4]
         requestLO = requestData[5]
         requestBlock = (int(ord(request24))<<24) + (int(ord(request16))<<16) + (int(ord(requestHI))<<8) + int(ord(requestLO))
      else:
         str = "Unsupported requestKey in dlfile.processRequest==>",requestKey
         raise FOFParameterError,str

      # look up the file size, and validate the block request
      fileSize = self.getFileSize()

      # *Every* file has a last block called the runt block, and the runt block will be sized from 0 to (blockSize-1) (e.g. 0 to 511)
      # It is legal for the firmware to request the runt block, but no blocks beyond that.
      # If the firmware requests the runt block, we'll read a partial block from the file, and set the 'notAFullRead' flag in the response packet.
      runtBlock = fileSize / blockSize
      runtSize = fileSize % blockSize

      if requestBlock < runtBlock:
         readSize = blockSize
         notAFullRead = chr(0)
      elif requestBlock == runtBlock:
         readSize = runtSize
         notAFullRead = chr(1)
      else:
         str = "dlfile.processRequest(): Request for block %s is beyond than last block %s." % (requestBlock,runtBlock)
         raise FOFParameterError,str

      # read from their file
      fileObj = self.dlfile[FILEOBJ]
      fileObj.seek(requestBlock*blockSize)
      data = fileObj.read(readSize)

      if requestBlock == runtBlock or (requestBlock+1 == runtBlock and runtSize == 0):
         self.isLastBlock = 1 # check last block
      else:
         self.isLastBlock = 0

      #print "dlfile:  requestHI: x%02X  requestLO: x%02X" % (ord(requestHI),ord(requestLO),)

      # construct the return block
      if 6 == requestKey:
         returnData = requestData[0] + notAFullRead + requestHI + requestLO + data
      elif 7 == requestKey:
         returnData = chr(6) + notAFullRead + request24 + request16 + requestHI + requestLO + data
      else:
         returnData = requestData[0] + notAFullRead + requestLO + requestHI + data

      return returnData

   def isLastProcessRequest(self):
      return self.isLastBlock
