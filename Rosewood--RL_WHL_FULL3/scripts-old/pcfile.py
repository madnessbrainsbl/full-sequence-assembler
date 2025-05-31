#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: PCFile handler- re-utilized from cm code file of same name by stuartm
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/pcfile.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/pcfile.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

import os,struct
from Constants import *
import ScrCmds

# File messages
OPEN_FILE = chr(80)
READ_FILE = chr(81)
WRITE_FILE = chr(82)
CLOSE_FILE = chr(83)
DELETE_FILE = chr(84)

class PCFile:


   def __init__(self, userFile = None):
      self.pcfile = None
      self.userFile = userFile
      self.cellTray = ScrCmds.getFofFileName(1)

  #   C L O S E
   def close(self):
      self.pcfile = None


  #   _ _ E X T R A C T   F I L E   N A M E
   def __extractFileName(self, resultsData):

      # The firmware programmer refers to a file name, which we implement as a directory, containing a file for each cellTrayPort.
      # The request must contain an ASCII file name.

      fileName = resultsData[2:10].split("\000")[0]  # Typically: "rsvddata".
      if not fileName: raise FOFResultsProcessingFailure,"No File Name in Request"

      self.pcfile = os.path.join(ScrCmds.getSystemPCPath(), fileName , self.cellTray) # Typically: "/var/merlin/pcfiles/rsvddata/1.1.0".

      return self.pcfile

   def getPcFile(self, mode):
      if self.userFile:
         return self.userFile(mode)
      else:
         return open(self.pcfile, mode)


  #   P R O C E S S   R E Q U E S T

   def processRequest(self,resultsData):
      # Firmware is requesting access to a file in our file system.

      resultsKey = resultsData[0]   # Typically in (80,81,82,83,84).

      if OPEN_FILE==resultsKey: # open_PC_file() code 80

         # Write mode truncates the file.
         mode = resultsData[1:2]

         # The UUT provides a file name.
         self.pcfile = self.__extractFileName(resultsData)

         return "%s\x00\x00" % (OPEN_FILE,)

      elif WRITE_FILE==resultsKey: # write_PC_file() code 82

         if not self.pcfile: raise FOFResultsProcessingFailure,"Open the file before writing."

         # Get the two byte BigEndian write count.
         writeCount = resultsData[1:3]
         if not 2==len(writeCount): raise FOFResultsProcessingFailure,"Bad or Missing Write Count: %s." % (`writeCount`,)
         writeCount = struct.unpack('>H',writeCount)[0]
         if writeCount>512: raise FOFResultsProcessingFailure,"Write count of %s is greater than 512." % (writeCount,)

         self.getPcFile(mode = 'ab').write(resultsData[3:writeCount+3])
         #open(self.pcfile,"ab").write(resultsData[3:writeCount+3]) # Notice this writes either writeCount bytes _or_ the actual length of the write data - whichever is less.

         return  "%s\x00\x00" % (WRITE_FILE,)

      elif READ_FILE==resultsKey: # read_PC_file() code 81

         if not self.pcfile: raise FOFResultsProcessingFailure,"Open the file before reading."

         # Get the four byte BigEndian file address.
         readAddress = resultsData[1:5]
         if not 4==len(readAddress): raise FOFResultsProcessingFailure,"Bad or Missing File Address: %s." % (`readAddress`,)
         readAddress = struct.unpack('>I',readAddress)[0]

         # Get the two byte BigEndian read count.
         readCount = resultsData[5:7]
         if not 2==len(readCount): raise FOFResultsProcessingFailure,"Bad or Missing Read Count: %s." % (`readCount`,)
         readCount = struct.unpack('>H',readCount)[0]
         if readCount>512: raise FOFResultsProcessingFailure,"Read count of %s is greater than 512." % (readCount,)

         readFile = self.getPcFile(mode = 'rb')#open(self.pcfile,"rb")
         readFile.seek(readAddress)
         data = readFile.read(readCount) # Notice that this may read less than readCount.
         if not testSwitch.BF_0123842_231166_FILE_XFER_FIX_BNCH_MULTI_BLOCK:
            readFile.close()

         return "%s\x00\x00%s" % (READ_FILE,data,)

      elif CLOSE_FILE==resultsKey: # close_PC_file() code 83

         self.close()

         return  "%s\000\000" % (CLOSE_FILE,)

      elif DELETE_FILE == resultsKey: # delete_PC_file() code 84

         return "%s\000\000" % (DELETE_FILE,)

      else:
         raise FOFResultsProcessingFailure,"Invalid resultsKey: %s" % (`resultsKey`,)
