#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: This module has code to create an npt file that the fw reads to set the NPT targets in the channel
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/nptFile.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/nptFile.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from cStringIO import StringIO
import struct

global fobj, fileSize
def processRequest21(requestData, *args, **kargs):
      """
      Results Callback for Block 21-> Request user file data block from host
      for download to drive
      requestData is a string from the UUT asking for a block from a file
      return a frame, raise an exception on error
      """
      requestKey = ord(requestData[0])
      # code 6 typically requests a block of data from the download file;  get_data_file()
      if requestKey == 21:
         blockSize = (int(ord(requestData[3]))<<8) + int(ord(requestData[2]))
         requestHI = requestData[5]
         requestLO = requestData[4]
         requestBlock = (int(ord(requestHI))<<8) + int(ord(requestLO))

       # look up the file size, and validate the block request
         #fileSize =  os.stat(fobj.name)[stat.ST_SIZE]

       # *Every* file has a last block called the runt block, and the runt block will be sized from 0 to (blockSize-1) (e.g. 0 to 511)
       # It is legal for the firmware to request the runt block, but no blocks beyond that.
       # If the firmware requests the runt block, we'll read a partial block from the file, and set the 'notAFullRead' flag in the response packet.
         runtBlock = fileSize / blockSize
         runtSize = fileSize % blockSize

       #print "Sending Block: %d of %d"%(requestBlock+1, runtBlock) #YWL:DBG

         if requestBlock < runtBlock:
            readSize = blockSize
            notAFullRead = chr(0)
         elif requestBlock == runtBlock:
            readSize = runtSize
            notAFullRead = chr(1)
         else:
            str = "processRequest21(): Request for block %s is beyond than last block %s." % (requestBlock,runtBlock)
            raise Exception, (11047,str)

         # read from their file
         #fileObj = self.dlfile[FILEOBJ]
         #fileObj = FileObj
         fobj.seek(requestBlock*blockSize)
         data = fobj.read(readSize)

         returnData = requestData[0] + notAFullRead + requestLO + requestHI + data

         SendBuffer(returnData)

class nptObject(object):
   __slots__ = ['targets', 'path', 'fobj', 'count']

   targets = []

   def __init__(self, path = None):
      self.path = path
      self.count = 0
      if self.path == None:
         self.fobj = StringIO()
      else:
         self.fobj = open(path,  'wb')

      #initialize the count
      self.updateCount()

   def updateCount(self):
      #Seek to start of file
      self.fobj.seek(0,0)
      self.fobj.write(struct.pack('H', self.count))
      
      #Seek to end of file
      self.fobj.seek(0,2)

   def addCuHdTarget(self, plmra, npt0, npt1, npt2, smCoeff, FilterA, FilterB, slope, mraLUT, Yideal, smPat):
      """Adds a full target definition to the npt target file"""
      self.fobj.write(struct.pack('B',plmra))
      self.fobj.write(struct.pack('b',npt0))
      self.fobj.write(struct.pack('b',npt1))
      self.fobj.write(struct.pack('b',npt2))
      self.fobj.write(struct.pack('8B',smCoeff[0], smCoeff[1], smCoeff[2], smCoeff[3], smCoeff[4], smCoeff[5], smCoeff[6], smCoeff[7]))
      self.fobj.write(struct.pack('b',FilterA))
      self.fobj.write(struct.pack('b',FilterB))
      self.fobj.write(struct.pack('8B',slope[0], slope[1], slope[2], slope[3], slope[4], slope[5], slope[6], slope[7]))
      self.fobj.write(struct.pack('8B',slope[8], slope[9], slope[10], slope[11], slope[12], slope[13], slope[14], slope[15]))
      self.fobj.write(struct.pack('8B',mraLUT[0], mraLUT[1], mraLUT[2], mraLUT[3], mraLUT[4], mraLUT[5], mraLUT[6], mraLUT[7]))
      self.fobj.write(struct.pack('8b',Yideal[0], Yideal[1], Yideal[2], Yideal[3], Yideal[4], Yideal[5], Yideal[6], Yideal[7]))
      self.fobj.write(struct.pack('H',smPat)) #was I
      self.fobj.write(struct.pack('H',0)) #pad


      self.count += 1
      self.updateCount()

   def addIterativeTarget(self, npt0, npt1, npt2, smPat):
      """Simple targets are those defined for Anaconda, Bonanza+ channels"""
      self.addCuHdTarget(0,  npt0,  npt1,  npt2,  [0]*8, 0, 0, [0]*16, [0]*8, [0]*8, smPat)

   def addIterativeTarget11K(self, npt0, npt1, npt2, npt3, npt4):
      """Simple targets are those defined for Marvell channels"""
      self.addMarvellTarget_11K(npt0, npt1, npt2, npt3, npt4, 0,0,0,0,0,0,0,0,0,0,0)


   def addMarvellTarget(self, npt0, npt1, npt2, smPat, offset0, offset1, offset2, offset3, offset4, offset5, offset6, offset7, offset8, smThreshold):
      """Adds a full target definition to the npt target file for the Marvell SRC_11K_M channel"""
      self.fobj.write(struct.pack('b',npt0))
      self.fobj.write(struct.pack('b',npt1))
      self.fobj.write(struct.pack('b',npt2))
      self.fobj.write(struct.pack('b',0))       # pad to keep on LWORD boundary
      self.fobj.write(struct.pack('L',smPat))
      self.fobj.write(struct.pack('H',smThreshold))
      self.fobj.write(struct.pack('9H',offset0, offset1, offset2, offset3, offset4, offset5, offset6, offset7, offset8))

      self.count += 1
      self.updateCount()

   def addMarvellTarget_11K(self, npt0, npt1, npt2, npt3, npt4, smPat, offset0, offset1, offset2, offset3, offset4, offset5, offset6, offset7, offset8, smThreshold):
      """Adds a full target definition to the npt target file for the Marvell 9200 channel"""
      self.fobj.write(struct.pack('b',npt0))
      self.fobj.write(struct.pack('b',npt1))
      self.fobj.write(struct.pack('b',npt2))
      self.fobj.write(struct.pack('b',npt3))
      self.fobj.write(struct.pack('b',npt4))
      self.fobj.write(struct.pack('b',0))       # pad to keep on LWORD boundary
      self.fobj.write(struct.pack('L',smPat))
      self.fobj.write(struct.pack('H',smThreshold))
      self.fobj.write(struct.pack('9H',offset0, offset1, offset2, offset3, offset4, offset5, offset6, offset7, offset8))

      self.count += 1
      self.updateCount()

   def addIterativeTarget_New(self, npt0, npt1, npt2, option, smPat):
      """Simple targets are those defined for Anaconda, Bonanza+ channels""" 
      """
         // First two bytes of the file indicate the number of targets to be processed.
         // Targets will be processed in sequential order.
         // Note that the file is constructed with two extra bytes following EACH NPT data structure.
      """
      """
         target count:  2 bytes
         npt structure:
               typedef struct npt_struct
               {
                  sint8         npt[3];                    // Target Noise Predictive Target
                  uint8         options;                   // 0 for 2 Taps, 1 for 3 Taps
                  uint16        smpatrn;                   // Sync Mark Pattern
                  uint16        modulo4_pad;               // Prevent possible compile time alignment issues, not valid data.
               } npt_struct;
         two extra bytes (optional)
      """      
      self.fobj.write(struct.pack('b',npt0)) #signed char
      self.fobj.write(struct.pack('b',npt1)) #signed char
      self.fobj.write(struct.pack('b',npt2)) #signed char
      self.fobj.write(struct.pack('B',option)) #	unsigned char
      self.fobj.write(struct.pack('H',smPat)) #unsigned short  2-byte smpatrn
      self.fobj.write(struct.pack('H', 0)) #unsigned short   2-byte  modulo4_pad
      self.fobj.write(struct.pack('H', 0)) #unsigned short   2-byte  two extra bytes after each npt target. i.e. end_of_record indicator
      self.count += 1
      self.updateCount()

   def getValue(self):
      """Return the data from the npttarget file"""
      if self.path == None:
         return self.fobj.getvalue()
      else:
         self.fobj.close()
         data = open(self.path,  'rb').read()
         self.fobj = open(self.path,  'ab')
         return data
