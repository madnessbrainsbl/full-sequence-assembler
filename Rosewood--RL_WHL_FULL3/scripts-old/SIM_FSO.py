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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SIM_FSO.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SIM_FSO.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
if __name__ == "__main__":
   import sys
   sys.path.append(os.path.join("Brinks"))
from Constants import *
import Utility, types

import MessageHandler as objMsg
from Drive import objDut
if PY_27:
   import hashlib
else:
   import md5
import os
import struct
from FSO import CFSO
import ScrCmds
try:    import cPickle as myPickle
except: import pickle as myPickle
from TestParamExtractor import TP

try: TraceMessage('')
except:
   def TraceMessage(sMsg):
      print sMsg

class Sim_Struct:
   """
   Class to define individual SIM file structures for use in the SIM file system
   """
   mctSize = 4
   def __init__(self, index, name, size):
      self.index = index
      self.name = name
      self.size = size
      self.__oUtility = Utility.CUtility()
   def __str__(self):
      return str(self.name)
   def mct(self):
      return self.__oUtility.convertStrToBinaryWords(self.name,padChar = '\x00',leftJustify = 1)[:self.mctSize]

class Sim_Area(object):
   """
   Class to define and maintain a list of SIM files managed by the process and self-test
   """
   if testSwitch.RW_4K_SYSTEM_DISC_SECTOR:
      sectorSize = 4096
   else:
      sectorSize = 512


   def __init__(self, sim_size = 1000*sectorSize, updateFunctionRef = None):
      self.size = sim_size
      self.SIM_LIST = {}
      self.ufr = updateFunctionRef
      self.initialized = False

   def __initializeObject__(self):
      if self.initialized == False:
         #call the self-update function
         f = self.ufr#getattr(super(Sim_Area, self),'ufr')
         #Set the self ref of the function to None to prevent recursion
         #setattr(super(Sim_Area, self),'initialized', True)
         self.initialized = True
         #update self
         f(self)
   if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
      def reinitializeObject(self, updateFunction, simDict, totalSimAreaAllocated):
         self.initialized = True
         updateFunction(self, simDict,totalSimAreaAllocated )

   def __getattr__(self,  name):
      self.__initializeObject__()

      return getattr(super(Sim_Area, self),name)


   def addSIMFile(self, name = None, fileStruct = None):
      if type(fileStruct) in [types.TupleType, types.ListType]:
         fileStruct = Sim_Struct(fileStruct[0], fileStruct[1], fileStruct[2])
      if fileStruct.size <= self.unusedSpace():
         if self.__unique__(fileStruct):
            if name == None:
               name = fileStruct.name
            self.SIM_LIST[name] = fileStruct
         else:
            raise Exception, "Non-Unique file definition"
      else:
         raise Exception, "SIM Area out of space"

   def __unique__(self, struct):
      for item in self.SIM_LIST.values():
         if item.index == struct.index or item.name == struct.name:
            return False
      return True

   def __getitem__(self, item):
      self.__initializeObject__()
      return self.SIM_LIST[item]

   def __iter__(self):
      for item in self.SIM_LIST.values():
         yield item
      raise StopIteration

   def numFiles(self):
      return len(self.SIM_LIST.keys())

   def unusedSpace(self):
      return self.size - self.usedSpace()

   def usedSpace(self):
      usage = 0
      for sim in self.SIM_LIST.values():
         try:

            usage += self.sectorUsage(sim.size)
         except TypeError: pass #Since there is only 1 exception case this is the lowest cost exec model
      return usage

   def sectorUsage(self, size):
      runt = size % self.sectorSize
      if runt > 0:
         runt = 1
      else:
         runt = 0
      return (size/self.sectorSize)*self.sectorSize + (runt * self.sectorSize)

   def maximizeUsage(self, item):
      free = self.unusedSpace()
      if free > 0:
         self.SIM_LIST[item].size += free

###########################################################################################################
# CSimpleSIMFile
#
# A simple wrapper for accessing SIM files easily in PF3.
# Supports checksum and filename verification, file length verification, and simple format versioning.
# Should be easy to use in both SF3 and PF3

# To use:
# 1. Allocate a new SIM file index in t231_pub.h
# 2. Add the new file to simDict
# 3. Use CSimpleSIMFile("FILE_NAME").read() to return the file contents in memory.
# 4. Use CSimpleSIMFile("FILE_NAME").write(data) to write file contents from memory.
###########################################################################################################

class CSimpleSIMFile:
   HEADER_FMT = "HBL16s"  #Key, Version, Length, Checksum
   KEY = 0xFACE
   VERSION = 1

   def __init__(self, sim_name):
      self.name = sim_name
      self.simRecord = objSimArea[self.name]
      self.oFSO = CFSO()
      self.filename = "%s.bin" % self.name    # Local file for writing
      self.filepath = os.path.join(ScrCmds.getSystemResultsPath(), ScrCmds.getFofFileName(0), self.filename)  # Path the file

   def checksum(self, data):
      if PY_27:
         oMD5 = hashlib.md5()
      else:
         oMD5 = md5.new()
      oMD5.update(data)
      oMD5.update(self.name) # Salt with the file name to prevent good reads from the wrong file
      checksum = oMD5.digest()
      return checksum

   def pack(self, data):
      """Pack the data payload into the file format"""
      # Prepend the header
      header = struct.pack(self.HEADER_FMT, self.KEY, self.VERSION, len(data), self.checksum(data))
      fdata = header + data

      # Verify the file fits in the allocated space
      if len(fdata) > self.simRecord.size:
         ScrCmds.raiseException(11044, "SIM File %s too big! %d > %d" % (self.name, len(fdata), self.simRecord.size))

      return fdata

   def unpack(self, fdata):
      """Unpack the data payload from the file format"""
      # Recover the header and the payload
      header_len = struct.calcsize(self.HEADER_FMT)
      header = fdata[:header_len]
      data = fdata[header_len:]

      # Parse the header
      key, ver, length, checksum = struct.unpack(self.HEADER_FMT, header)

      # Verify header integrity
      if key != self.KEY or ver != self.VERSION:
         msg = "SIM File %s header mismatch! key = %s (expected %s), version = %s (expected %s)" % (self.name, key, self.KEY, version, self.VERSION)
         objMsg.printMsg(msg)
         objMsg.printMsg("File Snippet: " + fdata[:80]) # To aid with root-causing file stompage
         ScrCmds.raiseException(14524, msg)

      # Recover the valid payload
      if len(data) > length:
         data = data[:length]

      # Verify checksum
      if self.checksum(data) != checksum:
         msg = "SIM File %s checksum mismatch" % self.name
         objMsg.printMsg(msg)
         objMsg.printMsg("File Snippet: " + fdata[:80]) # To aid with root-causing file stompage
         ScrCmds.raiseException(14524, msg)

      return data

   def read(self):
      """
      Read the SIM file from the drive and return the contents.
      Raises an exception if the file can't be read from the drive
      or the checksum doesn't match.
      """

      # Read from the drive into a PC File on the CM
      pcFilePath = self.oFSO.retrieveHDResultsFile(self.simRecord)

      # For VE, default to the write path to try to recover from there
      if testSwitch.virtualRun:
         pcFilePath = self.filepath

      # Read the PC File into memory
      fin = open(pcFilePath,'rb')
      fdata = fin.read()
      fin.close()

      # Recover the payload
      return self.unpack(fdata)

   def write(self, data):
      """
      Write the given data (string) to the SIM file on the drive.
      Raises an exception if the file can't be written to the drive for some reason.
      """

      # Format the data
      fdata = self.pack(data)

      # Write the data to a file
      # Must use GenericResultsFile because other file writes are prohibited
      fout = GenericResultsFile(self.filename)
      fout.open("wb")
      try:
         fout.write(fdata)
      finally:
         fout.close()

      # There is no way to query the file object for its path,
      # so we must assume that this path matches the GenericResultsFile object
      # Write the PC file to the drive
      self.oFSO.saveResultsFileToDrive(forceNew=1, filePath=self.filepath, fileType=self.simRecord, exec231=1)

   def clearCache(self):
      fobj = GenericResultsFile(self.filename)
      fobj.delete()

###########################################################################################################
###########################################################################################################

class CWrRd_ResFile:
   """
   Class to create and use a SIM file which holds general test data values from
   test and compare against values gathered later.  Since the initial values
   are saved in a SIM file, differences can be measured across operations.
   """

   def __init__(self, simFileName):
      """
      @type simFileName: String
      @param simFileName: Name of file defined in Constants.py objSimArea
      """
      self.recordName = str(simFileName).upper()  #Key is upper case by SIM File definition convention
##      #CM file name = DriveSN_SIM-file-name, for pseudo-uniqueness
##      self.genResName = '%s_%s.bin' %(objDut.serialnum,simFileName)
      #Cannot get fancy with name, because some tests (T31) use fixed path and names
      self.genResName = str(simFileName)
      self.oFSO = CFSO()

      try:
         self.pcFolderName = objSimArea.SIM_LIST[simFileName].name
      except:  #Allow CM file IO, without need to have SIM file definition
         self.pcFolderName = str(simFileName)
      try:
         self.t231Index = objSimArea.SIM_LIST[simFileName].index
      except:
         self.t231Index = 65535  #(hopefully) illegal/undefined value, to prevent SIM file IO

      self.pickleProt = 2 #0 is ASCII, 2 is maximum compression

      self.pcFilePath = os.path.join(ScrCmds.getSystemPCPath(), self.pcFolderName, self.oFSO.getFofFileName(0))
      self.cmResultsPath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.genResName)

   def simToPcFile(self):
      """
      Pull the SIM file and place it in a pcfile.  Return the path
      to the pcfile.
      """
      record = objSimArea[self.recordName]
      if not testSwitch.virtualRun:
         try:  #If power loss recovery, no need to re-read SIM file
            path = objDut.objData.retrieve(self.recordName)
            objMsg.printMsg("Power-loss recovery. No SIM file read necessary", objMsg.CMessLvl.DEBUG)
         except:
            #Read SIM file, write to pcfiles folder on CM
            path = self.oFSO.retrieveHDResultsFile(record)
            objDut.objData.update({self.recordName:path})

      else:
         path = os.path.join('.', self.cmResultsPath)

      return path

   def retrieveData(self,sourceLoc='SIM'):
      """
      Read file from SIM/CM, and returns data
      """
      if sourceLoc.upper() == 'SIM':  #Assume retrieve from SIM
         origCMPath = self.simToPcFile()
      elif sourceLoc.upper() == 'PC' and not testSwitch.virtualRun:
         #Assume file already on CM in /var/merlin/pcfiles/<simName>
         origCMPath = self.pcFilePath
      else: #For VE and appending file prior to SIM write
         origCMPath = os.path.join('.', self.cmResultsPath)

      origData={}
      thisCmFile = open(origCMPath,'rb')
      origData = myPickle.load(thisCmFile)
      thisCmFile.close()

      return origData

   def saveDataToCM(self,dataDict, mode='wb'):
      """
      Take data, use marshall object to save it to CM file.
      Set mode='a' to append existing file
      """
      dataToSave=dict(dataDict) #avoid corrupting data passed in
      if 'a' in mode:
         #Unpickle orig data from CM, and append it - assume order does not matter
         origData = self.retrieveData(sourceLoc='CMA')
         dataToSave.update(origData)

      pickleFile = GenericResultsFile(self.genResName)
      pickleFile.open('wb')
      myPickle.dump(dataToSave, pickleFile, self.pickleProt)
      pickleFile.close()

   def pcFileToSim(self):
      """
      Transfer file from /var/merlin/pcfiles/<simName> to SIM area.
      Some tests are hard-coded to write data to this folder.
      """
      self.cmFileToSim(filePath=self.pcFilePath)

   def cmFileToSim(self,filePath=None):
      """
      Write the file to disc, using test 231.
      """
      record = objSimArea[self.recordName]

      # First, look for the generic results file that is created in MDW cals.  If
      #  that is not there, assume that we have a pcfile that can be written to disc
      if filePath == None:
         if os.path.exists(self.cmResultsPath):
            filePath = self.cmResultsPath
         elif os.path.exists(self.pcFilePath):
            filePath = self.pcFilePath
         else:
            ScrCmds.raiseException(11044, "SIM File does not exist")

      if not testSwitch.virtualRun:
         #Write data to drive SIM
         self.oFSO.saveResultsFileToDrive(1, filePath, 0, record, 1)

         #Verify data on drive SIM
         path = self.oFSO.retrieveHDResultsFile(record)
         file = open(path,'rb')
         try:
            file.seek(0,2)  # Seek to the end
            fileLength = file.tell()
         finally:
            file.close()
         objMsg.printMsg("Re-Read of drive SIM File %s had size %d" % (record.name,fileLength), objMsg.CMessLvl.DEBUG)
         if fileLength == 0:
            ScrCmds.raiseException(11044, "Drive SIM readback of 0 size.")

#Function to initialize SIM kept separate from class above - a little security
# to ensure do not accidentally erase prior SIM.
def initSimArea():

   oFSO = CFSO()
   ######################################
   #  Initialize and Allocate the SPT results file headers
   ######################################
   initHeaderPrm_231 = {'test_num'  : 231,
            'prm_name'  : "Initialize SPT Results file header record",
            'CWORD1'    : 0x08,  #0x08 is init header record
            'PASS_INDEX': objSimArea['HEADER_RECORD'].index,
            'timeout'   : 120
   }
   baseName = "Allocate SPT Results file record: %s"
   allocateSpacePrm_231 = {'test_num'  : 231,
            'prm_name'  : baseName % '',
            'CWORD1'    : 0x10,  #0x10 is allocate space for index
            'PASS_INDEX': 1,
            'DL_FILE_LEN': 0,
            'timeout'   : 120
   }
   if testSwitch.WA_0152247_231166_P_POWER_CYCLE_RETRY_SIM_ERRORS:
      initHeaderPrm_231.update({
               'retryECList'       : [10451],
               'retryCount'        : 3,
               'retryMode'         : POWER_CYCLE_RETRY,
               })
      allocateSpacePrm_231.update({
               'retryECList'       : [10451],
               'retryCount'        : 3,
               'retryMode'         : POWER_CYCLE_RETRY,
               })

   #Init Header Record
   oFSO.St(initHeaderPrm_231)
   #Allocate space for all records
   for record in objSimArea:
      if not record.index == 0: #Don't re-do the header record
         if testSwitch.extern.FE_0191285_496741_STRING_REPRESENTATION_OF_SIM_FILE:
            if 'PASS_INDEX' in allocateSpacePrm_231:
               del allocateSpacePrm_231['PASS_INDEX'] #dont need index
         else:
            allocateSpacePrm_231['PASS_INDEX'] = record.index
         allocateSpacePrm_231['DL_FILE_LEN'] = oFSO.oUtility.ReturnTestCylWord(record.size)
         allocateSpacePrm_231['FOLDER_NAME'] = record.mct()
         allocateSpacePrm_231['prm_name'] = baseName % record.name

         for retry in xrange(5):
            try:
               oFSO.St(allocateSpacePrm_231)
               break
            except:
               #Error lets retry
               pass
         else:
            #We didn't break so no tries were successful
            raise


def initSimObject(simObject):
   #Constant Index Defines for SIM File types
   import math
   
   AFHFile_SIZE_IN_BYTES = int(math.ceil(objDut.numZones/60.0) * (128000/4) * TP.numHeads)
   
   if testSwitch.M11P or testSwitch.M11P_BRING_UP:
      VBARDATA_SIZE_IN_BYTES = int(550000 * TP.numHeads)
   else:
      VBARDATA_SIZE_IN_BYTES = int(math.ceil(objDut.numZones/30.0) * 25000 * TP.numHeads)
   
   if testSwitch.RSS_TARGETLIST_GEN:
      sizeofNpt = 15360
   else: sizeofNpt = 1536
   if testSwitch.KARNAK:
      sizeofADAPT_FS_PRM = 0x3A980
   else: sizeofADAPT_FS_PRM = 38912
      
   sif_bpi_size = TP.bpi_bin_size
   objMsg.printMsg('sif_bpi_size: %s' % str(sif_bpi_size))

   if testSwitch.extern.FE_0191285_496741_STRING_REPRESENTATION_OF_SIM_FILE:
      #just increment index, index is not important as 'filename' is unique index instead
      simDict = {
                        # 'pf3_filename' : ( index, 'filename', filesiz),
                        'HEADER_RECORD':     (0, 'HEAD_REC', 1024),
                        'SPT_RESULTS_FILE':  (1, 'SptReslt', 274735),
                        'AFH_SIM_FILE':      (2, 'AFHFile',  AFHFile_SIZE_IN_BYTES),
                        'VBAR_FORMATS':      (3, 'VBARFmts',  20000),
                        'DELAY_0':           (4, 'delay_0', 1536),
                        'DELAY_1':           (5, 'delay_1', 1536),
                        'DELAY_2':           (6, 'delay_2', 1536),
                        'DELAY_3':           (7, 'delay_3', 1536),
                        'DELAY_4':           (8, 'delay_4', 1536),
                        'DELAY_5':           (9, 'delay_5', 1536),
                        'DELAY_6':           (10, 'delay_6', 1536),
                        'DELAY_7':           (11, 'delay_7', 1536),
                        'MR_RES':            (12, 'mr_res', 40),
                        'SPT_BPI':           (13, 'bpi', 1024),
                        'GOTF_DBLOG':        (14, 'gotf_dbl', 200000),
                        'ADAPT_FS_PRM':      (15, 'adapt_fs', sizeofADAPT_FS_PRM),
                        'NPT_TGT_FILE':      (16, 'NptTgt', sizeofNpt),
                        'MRR_RANGE'   :      (17, 'mrr_rng', 120),
                        'DELAY_8':           (18, 'delay_8', 1536),
                        'DELAY_9':           (19, 'delay_9', 1536),
                        'VBAR_DATA':         (20, 'VBARDATA', VBARDATA_SIZE_IN_BYTES),
                        'RD_SCRN2':          (22, 'rd_scrn2', 2048),
                        'HSC_TCC':           (23, 'hsc_tcc', 1024),
                        'VBAR_FORMAT0':      (24, 'vfmt0',   1024),
                        'VBAR_FORMAT1':      (25, 'vfmt1',   1024),
                        'PRE_SKIPZN':        (26, 'skip_zn', 8194),
                        'ADAPT_FS_THRESHOLD':(27, 'adaptfst', 2048),
                        'WPC_RANGE':         (28, 'wpc_rg', 4096),
                        'SLIM_AFS_THRES':    (30, 'SLIM_AFS', 2048),
                        'FAT_AFS_THRES':     (31, 'FAT_AFS', 2048),
                        'SIF':               (35, 'sif', sif_bpi_size),
                        'PBIC_DATA_PRE2':    (36, 'pbica', 200000),
                        'PBIC_DATA_CAL2':    (37, 'pbicb', 200000),
                        'PBIC_DATA_FNC2':    (38, 'pbicc', 200000),
                        'PBIC_DATA_CRT2':    (39, 'pbicd', 200000),
                        'ADJ_BPI_TPI_FILE':  (40, 'ADJ_BPI', 10000),
         }
      if testSwitch.FE_0319957_356688_P_STORE_BPIP_MAX_IN_SIM:
         simDict.update({         
         'BPIP_MAX_FILE'      : (41, 'BPIP_MAX', 4096),           # SPT_BPIP_MAX
         'NOM_FREQ_FILE'      : (42, 'NOM_FREQ', 4096),           # SPT_NOM_FREQ
         })
   else:
      simDict={
                        'HEADER_RECORD'      : (0, 'HEAD_REC', 1024),            # SPT_HEADER_RECORD
                        'SPT_RESULTS_FILE'   : (1, 'SptReslt', 274735),          # SPT_RESULTS_FILE
                        'AFH_SIM_FILE'       : (2, 'AFHFile',  AFHFile_SIZE_IN_BYTES),          # SPT_AFH_FILE
                        'VBAR_FORMATS'       : (3, 'VBARFmts',  20000),          # SPT_BPI_FORMAT_NUMBERS_FILE
                        'DELAY_0'            : (4, 'delay_0', 1536),             # SPT_DELAY_0
                        'DELAY_1'            : (5, 'delay_1', 1536),             # SPT_DELAY_1
                        'DELAY_2'            : (6, 'delay_2', 1536),             # SPT_DELAY_2
                        'DELAY_3'            : (7, 'delay_3', 1536),             # SPT_DELAY_3
                        'DELAY_4'            : (8, 'delay_4', 1536),             # SPT_DELAY_4
                        'DELAY_5'            : (9, 'delay_5', 1536),             # SPT_DELAY_5
                        'DELAY_6'            : (10, 'delay_6', 1536),            # SPT_DELAY_6
                        'DELAY_7'            : (11, 'delay_7', 1536),            # SPT_DELAY_7
                        'MR_RES'             : (12, 'mr_res', 40),               # SPT_MR_RESISTANCE
                        'SPT_BPI'            : (13, 'bpi', 1024),                # SPT_BPI_FILE
                        'GOTF_DBLOG'         : (14, 'gotf_dbl', 200000),         # SPT_DBLOG_DATA
                        'ADAPT_FS_PRM'       : (15, 'adapt_fs_prm', sizeofADAPT_FS_PRM), # SPT_ADAPT_FS_PARMS
                        'NPT_TGT_FILE'       : (16, 'NptTgt', sizeofNpt),        # SPT_NPT_TARGET
                        'MRR_RANGE'          : (17, 'mrr_rng', 120),             # SPT_MR_RES_RANGE
                        'DELAY_8'            : (18, 'delay_8', 1536),            # SPT_DELAY_8
                        'DELAY_9'            : (19, 'delay_9', 1536),            # SPT_DELAY_9
                        'VBAR_DATA'          : (20, 'VBARDATA', VBARDATA_SIZE_IN_BYTES),   # SPT_LIST_FS_PARMS
                        'ADAPT_FS_THRESHOLD' : (21, 'adaptfsthre', 2048),        # SPT_VBAR_DATA
                        'RD_SCRN2'           : (22, 'rd_scrn2', 2048),           # SPT_ADAPT_FS_THRESHOLD
                        'ADJ_BPI_TPI_FILE'   : (40, 'ADJ_BPI',  10000),          # SPT_T211_ADJ_BPI_FOR_TPI
                        }

      if testSwitch.HSC_BASED_TCS_CAL:
         simDict.update({
         'HSC_TCC'            : (23, 'hsc_tcc', 1024),
         })
         
      if testSwitch.SKIPZONE:
         simDict.update({
         'PRE_SKIPZN'        :(24, 'skip_zn', 8194),
         })

      if testSwitch.FE_0168920_322482_ADAPTIVE_THRESHOLD_FLAWSCAN_LSI:
         if testSwitch.TRUNK_BRINGUP or testSwitch.ROSEWOOD7: # might need to cleanup this portion
            simDict.update({
            'SLIM_AFS_THRES' : (30, 'slim_afs', 2048),                           # SPT_SLIM_TRK_AFS_THRES_BHBZ
            'FAT_AFS_THRES'  : (31, 'fat_afs', 2048),                            # SPT_FAT_TRK_AFS_THRES_BHBZ
            })            
         else:
            simDict.update({
            'SLIM_AFS_THRES' : (29, 'slim_afs', 2048),
            'FAT_AFS_THRES'  : (30, 'fat_afs', 2048),
            })         

      if testSwitch.FE_0251897_505235_STORE_WPC_RANGE_IN_SIM:
         simDict.update({
         'WPC_RANGE'    :   (28, 'wpc_rg', 4096),
         })

      if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         simDict.update({
         'SIF'               :(35, 'sif', sif_bpi_size),
         })

      if testSwitch.PBIC_SUPPORT:
         simDict.update({
         'PBIC_DATA_PRE2'        :(36, 'pbica', 200000 ),
         })
         simDict.update({
         'PBIC_DATA_CAL2'        :(37, 'pbicb', 200000 ),
         })
         simDict.update({
         'PBIC_DATA_FNC2'        :(38, 'pbicc', 200000 ),
         })
         simDict.update({
         'PBIC_DATA_CRT2'        :(39, 'pbicd', 200000 ),
         })
      if testSwitch.FE_0319957_356688_P_STORE_BPIP_MAX_IN_SIM:
         simDict.update({         
         'BPIP_MAX_FILE'      : (41, 'BPIP_MAX', 4096),           # SPT_BPIP_MAX
         'NOM_FREQ_FILE'      : (42, 'NOM_FREQ', 4096),           # SPT_NOM_FREQ
         })
   try:
      from pgm_SIM import totalSimAreaAllocated,updateToSimDef   #Allow for a file to override base SIM
   except:
      totalSimAreaAllocated = 64000*512
      updateToSimDef = {}

   simDict.update(updateToSimDef)

   simObject.size = totalSimAreaAllocated
   for thisKey in simDict.keys():
      #Provide mechanism to remove/replace default entries above, since indices limited to 0-14
      if simDict[thisKey] == ():
         simDict.pop(thisKey)
      else:
         simObject.addSIMFile(thisKey,simDict[thisKey])

   simObject.maximizeUsage('SPT_RESULTS_FILE')

objSimArea = Sim_Area( updateFunctionRef = initSimObject)

if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
   def reinitSimObject(simObject, simDict, totalSimAreaAllocated):
      #Constant Index Defines for SIM File types

      simObject.SIM_LIST = {}
      simObject.size = totalSimAreaAllocated
      for thisKey in simDict.keys():
         #Provide mechanism to remove/replace default entries above, since indices limited to 0-14
         if simDict[thisKey] == ():
            simDict.pop(thisKey)
         else:
            simObject.addSIMFile(thisKey,simDict[thisKey])

      simObject.maximizeUsage('SPT_RESULTS_FILE')

if __name__ == "__main__":
   objSimArea = buildSimObj()
   TraceMessage("Unused space: %s" % objSimArea.unusedSpace())
   TraceMessage("Used space: %s" % objSimArea.usedSpace())
   TraceMessage("%10s %10s %10s" % ("Name", "Size", "Sector Bytes"))
   for sim in objSimArea.SIM_LIST.values():
      TraceMessage("%10s %10s %10s" % (sim.name, sim.size, objSimArea.sectorUsage(sim.size)))
