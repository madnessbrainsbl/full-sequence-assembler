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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/driveStateMarshall.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/driveStateMarshall.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import ScrCmds
import MessageHandler as objMsg
try:    import cPickle as myPickle
except: import pickle as myPickle

from sys import version
ver = version.split()[0].split('.')
useHelper = False
if int(ver[0]) <= 2 and int(ver[1]) <= 4:
   objMsg.printMsg('Python %s cell detected, add array.array support for pickle' % version)
   useHelper = True
   from array import array, ArrayType
   import copy_reg
      
   def unpickle_array(data):
      # objMsg.printMsg('unpickling an array instance...')
      return array(data[0], data[1:])
      
   def pickle_array(arr):
      # objMsg.printMsg('pickling an array instance...')
      return unpickle_array, ("%s%s" % (arr.typecode, arr.tostring()),)

###########################################################################################################
###########################################################################################################
class CSaveMarshall:
   def __init__(self, driveSerialNumber, saveProtocol=2):
      """
      initPickleObject:
      Creates the cPickle objects needed for serialization of dictionaries to disc for power-loss recovery, lower memory footprint, and intra-class utilization.
      @type driveSerialNumber: string
      @param driveSerialNumber: Serial Number of drive
      @type saveProtocol: integer
      @param saveProtocol: cPickle Protocol used to serialize the object. Default is 2 (maximum compression, 0 is human readable ASCII)
      """
      self.marshallObject = {}
      self.driveSN = driveSerialNumber
      self.pickleProt = saveProtocol

      self.initializing = 1 #used for state machine
      self.states = {'merged': 'self.passExec()',  'unMerged': 'self.mergeDiscToLocal()'}
      self.currentState = self.states['merged']
      self.initializing = 0 #used for state machine

      #Create generic results file
      self.pickleFile = GenericResultsFile('%s_serialize.log' % self.driveSN)


      #BF_0114617_231166_FIX_OBJDATA_RECURSION_ISSUES_IN_VE
      if testSwitch.virtualRun:
         self.__initFile()
      else:
         try:
            self.recover(1)
         except:
            self.__initFile()



      objMsg.printMsg('Creating generic marshalling file succeeded')

   #------------------------------------------------------------------------------------------------------#
   def __initFile(self):
      try:
         self.pickleFile.open('wb')
         self.pickleFile.write('')
      finally:
         self.pickleFile.close()

   #------------------------------------------------------------------------------------------------------#
   def __openPckl(self, mode='a'):
      #try:
      self.pickleFile.open(mode)
      #except:
      #   #print "Probably a local system... so let's overload for running on winFOF"
      #   self.pickleFile = open('%s_serialize.log' % self.driveSN, mode)
   def passExec(self):
      pass

   #------------------------------------------------------------------------------------------------------#
   def mergeDiscToLocal(self):
      """
      Merges the marshalling object w/ out of sync items saved to disc-only for active memory savings. Controlled by the self.currentState value machine
      """
      if self.initializing:
         return

      mLoc = self.recover(0)

      keyList = [k for k in mLoc.keys() if not self.marshallObject.has_key(k)]

      for indKey in keyList:
         self.marshallObject.update({indKey:mLoc[indKey]})

      self.currentState = self.states["merged"]

   #------------------------------------------------------------------------------------------------------#
   def __releaseLocal(self,itemName):
      """
      __releaseLocal:
      Deletes the named key structure from the active memory.
      @type itemName: string
      @param itemName: Primary key to release from the active memory structure.
      """
      del self.marshallObject[itemName]
      self.currentState = self.states["unMerged"]

   #------------------------------------------------------------------------------------------------------#
   def recover(self, replace=1):
      """
      recover:
      retrieves the full cPickled dictionary from the disc.
      @type replace: bool
      @param replace: Identifies whether or not the active memory version will be replaced by the disc copy. Default is 1 (Replace)
      """
      if useHelper:
         copy_reg.pickle(ArrayType, pickle_array, unpickle_array)
      self.__openPckl('rb')
      try:
         if replace:
            self.marshallObject = myPickle.load(self.pickleFile)
            return self.marshallObject
         else:
            mLoc = myPickle.load(self.pickleFile)
            return mLoc
      finally:
         self.pickleFile.close()

   #------------------------------------------------------------------------------------------------------#
   def serialize(self):
      """
      Serialize:
      Forces a dump of the active data dictionary to disc.
      Does not release items from active memory. Overwrites disc copy.
      """
      if useHelper:
         copy_reg.pickle(ArrayType, pickle_array, unpickle_array)
      eval(self.currentState) # Will execute the active state syncronization function.
      try:
         self.__openPckl('wb')
         #if testSwitch.winFOF == 0:
         myPickle.dump(self.marshallObject, self.pickleFile, self.pickleProt)
         #else:
         #   objMsg.printMsg("Ignoring pickle in winFOF", objMsg.CMessLvl.CRITICAL)
      finally:
         self.pickleFile.close()

   #------------------------------------------------------------------------------------------------------#
   def update(self, inDict, releaseMemory = 1):
      """
      Updates the local active memory structure w/ passed dictionary or creates a new primary key. Also calls serialize to save the state information.
      """
      self.marshallObject.update(inDict)
      self.serialize()
      if releaseMemory == 1:
         for key in inDict.keys():
            self.__releaseLocal(key)

   #------------------------------------------------------------------------------------------------------#
   def retrieve(self, itemName, updateLocal=1):
      """
      retrieve:
      Gets the value dictionary from the key specified from the cPickled object on the disc.
      @type itemName: string
      @param itemName: Primary key to update from the active memory structure.
      @type updateLocal: bool
      @param updateLocal: Identifies whether or not to update the active memory version of the key'd object. Default is 0 (Don't update)
      """
      if updateLocal:
         eval(self.currentState)
         return self.marshallObject[itemName]
      else:
         mLoc = self.recover(0)
         return mLoc[itemName]

#---------------------------------------------------------------------------------------------------------#

   def __setitem__(self,key,value):
      """Allows dut.objData[<key>]=<value> method"""
      self.update({key:value})

   def __getitem__(self,key):
      """Allows calling dut.objData[<key>] method"""
      return self.retrieve(key)

   def __getattr__(self,name):
      """Allows calling dut.objData.get(<key>,<default>) and all other dict methods methods"""
      eval(self.currentState)
      value = self.marshallObject.__getattribute__(name)
      self.serialize()
      return value