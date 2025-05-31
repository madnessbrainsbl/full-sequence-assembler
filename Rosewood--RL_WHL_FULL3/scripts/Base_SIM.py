#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Base_SIM Module to store base inherited classes for creating a CM/drive-safe serializeable container.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Base_SIM.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Base_SIM.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import types, ScrCmds, struct, binascii
import MessageHandler as objMsg
if PY_27:
   import hashlib
else:
   import md5

DEBUG = 0

class baseDataFileComponent:
   """
   Base class for data file components.
   Usage: Inherit/implement this class for use in implementing data file items that need read/write/accessor properties.
   """
   def __init__(self, value, name, formatMask = 0):
      """
      Init Params
      @param value: initializing setter for value
      @param name: for getter retrieval
      @param formatMask: Set to override auto-detection of value format for binary conversion.
      """
      self.value = value
      self.offset = 0
      self.byteLen = 1
      self.name = name
      if formatMask == 0:
         self.format = self.getFormat()
      else:
         self.format = formatMask
      self.binLen()

   def getFormat(self):
      """
      Returns auto-detected format based on class's value property.
      """
      inVal = self.value

      if type(inVal) == types.IntType:
         if inVal <= 0xFF:
            return 'B'
         elif inVal <= 0xFFFF:
            return 'H'
         elif inVal <= 0xFFFFFFFF:
            return 'L'
         elif inVal > 0xFFFFFFFF:
            return 'Q'
      elif type(inVal) == types.FloatType:
         return 'f'
      #else:
      #   ScrCmds.raiseException(11044, 'Value to big for SIM: %s' % str(self.value))


   def binLen(self):
      """
      Returns length of value property when converted to binary data.
      """
      self.byteLen = struct.calcsize(self.format)
      return self.byteLen

   def readStream2(self, startOff, fstream):
      """
      Function reads the item's value from the input stream based on the item's format property.
      *Assumes file stream pointer already at file offset for reading of the item.
      """
      #fstream.seek(startOff + startOff)
      data = fstream.read(self.binLen())
      if DEBUG == 1:
         objMsg.printMsg("%s:%s<%s>" % (self.name, binascii.hexlify(data), self.format))
         #print(fstream.tell())
      try:
         val = struct.unpack(self.format, data)
         if type(val) == types.TupleType:
            self.value = val[0]
         else:
            self.value = val
      finally:
         if DEBUG == 1:
            objMsg.printMsg("%s:%s<%s>" % (self.name, self.value, self.format))

      return self.value

   def writeStream2(self, fstream):
      """
      Function writes the item's value to the input stream based on the item's format property.
      *Assumes file stream pointer already at file offset for writing of the item.
      """
      if DEBUG == 1:
         objMsg.printMsg("writeStream2/ %s:%s<%s>" % (self.name, self.value, self.format))
         #print(fstream.tell())
      fstream.write(struct.pack(self.format, self.value))    # This is THE function which actually writes data down to the SIM file.

class baseDataFrame:
   """
   Base class for implementing a "frame" or group of information in a data file.
   It is made up of data file item classes to maintain propper read/write stream operations.
   """
   def __init__(self):
      self.frameItems = []
      self.frameStart = 0

   def __del__(self):
      del self.frameItems[:]      

   def addItems(self, items):
      """
      Adds a list of baseDataFileComponent's to the frame class for storage/serialization.
      """
      if not type(items) == types.ListType:
         items = [items]

      for item in items:
         if testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION or type(item) == types.InstanceType:
            self.frameItems.append(item)
         else:
            ScrCmds.raiseException(11044, "Invalid frame content; %s:%s" % (str(item), type(item)))

   def get(self, name, default = None):
      """
      Get Accessor Method.
      """
      for item in self.frameItems:
         if DEBUG == 1:
            ScriptComment("%s: %s"% (item.name, name))
         if item.name == name:
            return item.value
      return default

   def __getitem__(self, key, default = None):
      """
      Get item by name method for default accessor
      """
      return self.get(key, default)

   def set(self, name, value):
      """
      Value set function for name based value access
      @param name: Name of item you want to set value to.
      @param value: Value to set item to.
      """
      for item in self.frameItems:
         if item.name == name:
            item.value = value

   def __setitem__(self, key, value):
      self.set(key, value)

   def __str__(self):
      outStr = ""
      for item in self.frameItems:
         outStr += "%s: %s," % (str(item.name), str(item.value))
      return outStr

   def frameSize(self):
      """
      Function returns the binary size of the frame based on the container's item sizes.-No overhead assumed
      """
      size = 0
      for item in self.frameItems:
         size += item.byteLen
      return size

   def readStream(self, fstream):
      """
      Read items from input stream and set the frames items to the read in values.
      @param fstream: Input stream. Should be at frame's offset into stream already.
      """
      strOff = self.frameStart
      for item in self.frameItems:
         item.readStream2(strOff, fstream)
         strOff += item.binLen()

   def writeStream(self, fstream):
      """
      Write items to input stream and write the frames items to the output stream.
      @param fstream: Output stream. Should be at frame's offset into stream already.
      """
      for item in self.frameItems:
         item.writeStream2(fstream)
         
   def bufferStream(self ):
      """
      Write items to input stream and write the buffer items to the output stream.
      @param fstream: Output stream. Should be at frame's offset into stream already.
      """
      data = ""
      for item in self.frameItems:
         data+=struct.pack(item.format,item.value)
      return data

class baseSIMFile:
   """
   Base class for implementing an automated read/write serializable binary file for general use or implementation into the F3 SIM file system.
   """
   def __init__(self):
      self.fileSize = 0
      self.frames = {}
      self.crcFormat = 'L'
      self.md5Format = '32s'

   def addFrame(self, data):
      """
      Add a base SIM frame to the class.
      """
      self.frames.append(data)

   def reloadFromDisc(self, path):
      """
      Base class. Override.
      """
      pass

   def writeToDisc(self, path):
      """
      Base class. Override.
      """
      pass


   def append_md5sum(self, fstream):
      """
      Append md5sum onto passed fstream.
      """
      md5sum = self.generate_md5sum(fstream, -1)
      pack_md5sum = struct.pack(self.md5Format, md5sum)

      # append the md5sum 32 byte value onto the end of the SIM binary file.
      try:
         fstream.close()
      except:
         pass
      fstream.open('ab')
      fstream.write(pack_md5sum)
      fstream.close()

   def generate_md5sum(self, fstream, size):
      """
      Generates md5sum.
      """
      fstream.open('rb')
      fstream.seek(0, 0)

      if size == -1:
         data = fstream.read()
      else:
         data = fstream.read(size)

      fstream.close()

      if PY_27:
         md5Obj = hashlib.md5()
      else:
         md5Obj = md5.new()
      md5Obj.update(data)
      return str(md5Obj.hexdigest())


   def getFile_md5sum(self, fstream):
      """
      Decrypt md4sum encoded fstream.
      """
      fstream.open('rb')
      fstream.seek(-32, 2)
      data = fstream.read()
      data2 = struct.unpack(self.md5Format, data)[0]
      fstream.close()
      return str(data2)



   def returnFileSize(self, fstream):
      """
      Return File Size.
      """
      fstream.open('rb')
      fstream.seek(0, 2)
      file_len = fstream.tell()
      fstream.close()
      return str(file_len)


#---------------------------------------------------------------------------------------------------------#
