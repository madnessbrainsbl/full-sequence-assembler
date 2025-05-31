#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Save and Restore Drive States
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SaveAndRestore.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SaveAndRestore.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

#Test Switches needed to run save and restore
#BF_0123842_231166_FILE_XFER_FIX_BNCH_MULTI_BLOCK
#BF_0139838_231166_P_FIX_CPCRISERNEWSPT_SEASERIAL
#FE_0150630_347506_AUTONOMOUSLY_LOCATE_MRRANGE_SIM_FILE
#FE_0134030_347506_SAVE_AND_RESTORE

from Constants import *
import types, os, time, re, cStringIO
from TestParamExtractor import TP
from Drive import objDut

import MessageHandler as objMsg
import Utility, traceback
from PowerControl import objPwrCtrl

import ScrCmds
from FSO import CFSO
from Process import CProcess
from Process import CCudacom
from sptCmds import objComMode
from Drive import objDut
import FileXferFactory
import zipfile

try:    import cPickle as myPickle
except: import pickle as myPickle


####CONSTANTS#######
DEBUG = 0

#self.dut attributes that will be restored
DUT_ATTRIBUTES_TO_RESTORE = ['partNum', 'WTF', 'Waterfall_Req', 'Waterfall_Done', 'Niblet_Level', 'Drv_Sector_Size', 'Depop_Req', 'Depop_Done']

#self.dut.driveattr attributes that will be restored
FIS_DRIVE_ATTRIBUTES_TO_RESTORE = ['WTF', 'WATERFALL_REQ', 'WATERFALL_DONE', 'NIBLET_LEVEL', 'DRV_SECTOR_SIZE', 'DEPOP_REQ', 'DEPOP_DONE']

class CRestoreBase(CProcess,CCudacom):

   def __init__(self, restoreStateName, baseline, operationName, fileNameBase = None):
      CProcess.__init__(self)
      self.dut = objDut

      self.oFSO = CFSO()
      self.localData = {}
      self.stateDescription = {}


      if fileNameBase: #user passes in file name
          self.baseFileName = 'RESTORE.%s.%s' %(HDASerialNumber, fileNameBase.upper())
          self.restoreStateName = fileNameBase.split('.')[-1]
      else:            #construct file name by pieces
         if restoreStateName:
            self.restoreStateName = restoreStateName.upper()
         elif self.dut.localRestoreSet:
            self.restoreStateName = self.dut.localRestoreSet[-1].upper()
            objMsg.printMsg('STATE_NAME was not set by user in StateTable restore params.  Using last saved state %s' %self.restoreStateName)
         else:
            objMsg.printMsg('Error:  No restore point available.  save local restore point OR set STATE_NAME & BASELINE in StateTable params to use baseline or ')
            ScrCmds.raiseException(11044, "Restore point unavailable")

         self.baseFileName = 'RESTORE.%s.%s.%s.%s' %(HDASerialNumber, baseline.upper(), operationName.upper(), self.restoreStateName)


   def printStateDescription(self):
      objMsg.printMsg('***STATE DESCRIPTION***')
      for key,value in self.stateDescription.items():
         objMsg.printMsg('**  %s : %s' %(key,value))

   def generateMD5(self, data):
      '''Generate an MD5 value'''
      import md5
      md5Obj = md5.new()
      md5Obj.update(data)
      return str(md5Obj.hexdigest())

   def checkFileLength(self,path):
      '''Check the length of the file by using the tell() method'''

      fileObj = open(path,'rb')
      try:
         fileObj.seek(0,2)  # Seek to the end
         fileLength = fileObj.tell()
      finally:
         fileObj.close()

      return fileLength

   def createResultsDirFile(self, filename, fileContents):
      #save file to results directory
      try:
         mftFile = GenericResultsFile(filename)
         mftFile.open('wb')
         mftFile.write(fileContents)
      finally:
         mftFile.close()

      #return full path where file resides
      return mftFile.name

   def createZip(self, baseFileName, fileCollection):
      '''Create a zip of restore files and include a manifest file'''

      zipFileName =  baseFileName.upper() + '.ZIP'
      objMsg.printMsg('\nCreating zip - %s\n ' %zipFileName)

      #Create zip file
      myzipFile = GenericResultsFile(zipFileName)
      myzipFile.open('w')
      zipObj = zipfile.ZipFile(myzipFile, 'w', zipfile.ZIP_DEFLATED)

      #add the files to the zip
      manifest = {}
      try:
         for fileType, filePath in fileCollection.items():
            if filePath == None:
               #some files will not exist if there is no system area present.  Add the keys to the manifest for tracking.
               objMsg.printMsg('%s - No file to add' %fileType)
               manifest[fileType] = None
            else:
               extension = os.path.splitext(filePath)[-1].upper()
               if not extension: extension = '.BIN'  # files in pcfiles folder do not have an extension

               fileName = baseFileName + '.' + fileType + extension
               fileName = fileName.upper()
               manifest[fileType] = fileName

               objMsg.printMsg('%s - Adding %s as %s' %(fileType, filePath, fileName))
               if not testSwitch.virtualRun:
                  zipObj.write(filePath, fileName)

               #delete files in the results directory to save space
               if ScrCmds.getSystemResultsPath() in filePath:
                  objMsg.printMsg('%s - Deleting %s from results directory' %(fileType, filePath))
                  fObj = GenericResultsFile(os.path.basename(filePath))
                  fObj.delete()

         #add the manifest
         objMsg.printMsg('Adding manifest as %s' %baseFileName + '.MFT')
         zipObj.writestr(baseFileName + '.MFT', repr(manifest))
      finally:
         zipObj.close()
         myzipFile.close()

      objMsg.printMsg('Zip creation complete')
      return zipFileName

   def extractZip(self, zipFileName):
      '''Extract all files in a zip that resides in the results directory'''

      objMsg.printMsg('Extracting zip %s' %zipFileName)

      import zipfile

      if testSwitch.virtualRun:
         #myzipFile = r'..\results\bench\%s' %zipFileName
         return
      else:
        myzipFile = GenericResultsFile(zipFileName)
        myzipFile.open('r')

      zipObj = zipfile.ZipFile(myzipFile, 'r')

      for filename in zipObj.namelist():
         objMsg.printMsg('Extracting %s' %filename)

         if DEBUG:
            path = os.path.join(ScrCmds.getSystemResultsPath(),self.oFSO.getFofFileName(0),filename)
            isfile = os.path.isfile(path)
            objMsg.printMsg('is file?  %s' %isfile)

         # Don't handle directories directly (i.e. prune)
         if not filename.endswith('/'):
            try:
               fp = GenericResultsFile(filename)
               fp.open('wb')
               fp.write(zipObj.read(filename))
            finally:
               fp.close()

            if DEBUG:
               isfile = os.path.isfile(path)
               objMsg.printMsg('is file?  %s' %isfile)

   def retrievePrimaryDefectFile(self):
      '''Get the primary defect file off the drive and save it in the pcfiles directory'''

      objMsg.printMsg('Save Primary Defect:  Retrieving Primary Defect File from the drive')

      #show summary of ta list, s list and plist.
      if DEBUG:
         self.reportPrimaryDefectFileLogs()

      #power cycle to clear out the memory buffer.  there is a problem otherwise
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


      #Retrieve the primary defect file.  The file is about ~4MB
      params = {'test_num':130, 'prm_name':'Save Primary Defect File to PCFile','CWORD2':0xc008, 'CWORD3':0x0004, 'timeout':4000 }

      #Without this flag, the dblog data dumps tons (~12MB) of data into the results file.
      #Suppress the output because it generates MB worth of data
      if not testSwitch.extern.FE_0110957_398021_DISABLE_TBL_DISPLAY:
         objMsg.printMsg('You should enable SF3 flag FE_0110957_398021_DISABLE_TBL_DISPLAY.  It will significantly reduce test time')
         params.update({'stSuppressResults':1})
         objMsg.printMsg('Save Primary Defect:  Suppressing output becuase FE_0110957_398021_DISABLE_TBL_DISPLAY is not enabled.')
         objMsg.printMsg('Save Primary Defect:  Params = %s' %params)

      self.St(params)

      return os.path.join(ScrCmds.getSystemPCPath(),'filedata',self.oFSO.getFofFileName(0))

   def retrieveDbiLog(self):
      '''Get the DBI Log off the drive and save it in the pcfiles directory'''

      #show summary of dbi log.  this will report 10113 if log has not been created yet
      if DEBUG:
         self.reportDbiLog()

      #power cycle to clear out the memory buffer.  there is a problem with the last 15 bytes of the file showing junk leftover in the buffer
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      #retrieve the dbilog
      self.St({'test_num':130, 'prm_name': 'Save DBI Log to PCFile', 'CWORD2':0x8100, 'CWORD3':0x0004, 'timeout':1000})
      return os.path.join(ScrCmds.getSystemPCPath(),'DBIlog',self.oFSO.getFofFileName(0))


   def reportDbiLog(self):
      '''Report the current DBI Log.  You must have initialized the log first'''

      """ Report the current dbilog """
      repdbi = {'test_num'    : 107,
             'prm_name'    : 'Report Current DBI Log',
             'timeout'     : 1800,
             'spc_id'      : 1,}
      self.St(repdbi)

   def reportPrimaryDefectFileLogs(self):
      '''Report the current Primary Defect file tables - PList, TAList, SList.'''

      """ report the servo flaw table """
      prm = {'test_num'    : 130,
             'prm_name'    : 'Report Servo Flaw Table',
             'timeout'     : 1800,
             'spc_id'      : 1,
             'CWORD1'      : 0x40,}
      self.St(prm)

      """ report the TA flaw table """
      prm = {'test_num'    : 130,
             'prm_name'    : 'Report TA Flaw Table',
             'timeout'     : 1800,
             'spc_id'      : 1,
             'CWORD1'      : 0x100,}
      self.St(prm)

      """ report the PLIST flaw table """
      prm = {'test_num'    : 130,
             'prm_name'    : 'Report pLIST Flaw Table',
             'timeout'     : 1800,
             'spc_id'      : 1,
             'CWORD1'      : 0x80,}
      self.St(prm)

   def checkSystemAreaInit(self):
      '''Check to see if the system area has been initialized by reading a value in the CAP that tracks this'''

      objMsg.printMsg('\nCHECK SYSTEM INITIALIZATION\n')

      #dump the cap
      self.St({'test_num': 172, 'prm_name': 'Dump the CAP','CWORD1': 1, 'timeout':30})

      if testSwitch.virtualRun:
         return 1

      #Check offset 0x00E1 in the CAP.  If it is set to 'ff' the system area is disabled.  If it is set to 'fe' it is enabled
      #Loop through the dblog data, starting from the end, until we find row 0x00E0.  Then pull out the value from coloumn 1.
      n = 0
      while 1:
         n+= -1
         address = self.dut.dblData.Tables('P172_CAP_TABLE').tableDataObj()[n]['ADDRESS']
         address = int('0x' + address, 16)

         if address == 0x00e0:
            systemAreaValue = self.dut.dblData.Tables('P172_CAP_TABLE').tableDataObj()[n]['1']
            objMsg.printMsg('System Area Value = %s' %systemAreaValue)
            if systemAreaValue == 'ff':
               objMsg.printMsg('System area is disabled')
               return 0
            elif systemAreaValue == 'fe':
               objMsg.printMsg('System area is enabled')
               return 1
            else:
               ScrCmds.raiseException(11044, "System area init check failed")
            break

   def initFlawlists(self):
      """ initialize & clear the logs in primary defect file (TAList, PList, SList) """
      prm = {'test_num'    : 149,
             'prm_name'    : 'Init Primary Defect File',
             'timeout'     : 600,
             'spc_id'      : 1,
             'CWORD1'      : 0xE,}
      self.St(prm)


      self.reportPrimaryDefectFileLogs()

      """ initialize & clear the dbilog """
      prm = {'test_num'    : 101,
             'prm_name'    : 'Init DBI Log',
             'timeout'     : 600000,
             'spc_id'      : 1,}
      self.St(prm)

      self.reportDbiLog()

class CSetRestorePoint(CRestoreBase):
   """
     Description: Class that will provide base functionality to set the drive to a restore point
     Params: NONE
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, restoreStateName, baseline, operationName, fileNameBase ):
      CRestoreBase.__init__(self, restoreStateName, baseline, operationName, fileNameBase)

      self.manifest = {}
      self.manifestFilePath = None

   def run(self):

      objMsg.printMsg("Restoring drive to %s state." %self.restoreStateName)

      if testSwitch.virtualRun:
         objMsg.printMsg("Virtual Execution mode...can not execute restore in VE")
         return

      #Locate the zip.  It could be in results dir, dlfiles dir or on the ftp site.
      self.locateRestoreFiles()

      #load the state description
      self.loadStateDescription(self.manifest['DESCRIPTION'])

      #restore PF3 data
      self.loadPF3data(self.manifest['PF3'])

      #restore the flash
      self.loadFlashImg(self.manifest['FLASHIMG'])

      #re-initialize setup variables
      if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
         from Serial_Init import CInit_DriveInfo
      else:
         from base_SerialTest import CInit_DriveInfo
      oDrvInfo = CInit_DriveInfo(self.dut)
      oDrvInfo.run()

      #initialize system area if needed and set self.dut.systemAreaPrepared variable
      self.initializeSystemArea()

      #check to see if system area is prepped
      if self.dut.systemAreaPrepared:

         #restore sim area
         self.loadSimFile(self.manifest['SIM'])


         #init/clear the flaw lists.  We need to do this because we can not clear system area on GR50 right now!!
         self.initFlawlists()

         ''' There are still SF3 problems with restoring these flawlist files so let us skip for now

         #restore DBILog
         if self.manifest['DBILOG']:
            self.loadDbiLog(self.manifest['DBILOG'])
         else:
            objMsg.printMsg('\nSKIPPED DBILOG:  Restore state does not have DBILog\n')

         #restore Plist, TAlist, Slist
         self.loadPrimaryDefectFile(self.manifest['PRIM_DEFECT'])
         '''
      else:
         objMsg.printMsg('\nSKIPPING RESTORATION OF SIM AREA, DBILOG and PRIMARY DEFECT FILE:  Restore state does not have a system area\n')

      self.cleanUpRestoreFiles()

   def loadFlashImg(self, filePath):
      '''Restore the flash to a previously saved BIN file'''
      objMsg.printMsg('\nRESTORING FLASH\n')

      #Seaserial the saved flash image back onto the drive
      from RawBootLoader import CFlashLoad
      ofls = CFlashLoad(binFilePath = filePath)

      objMsg.printMsg("RESTORE FLASH:  Seaserialing %s" %filePath)

      retries = 0
      while 1:
         try:
            if not testSwitch.virtualRun:
               ofls.flashBoard()

            break
         except:
            objMsg.printMsg("RESTORE FLASH:  Flashing board failed: %s" % (traceback.format_exc(),))
            retries = retries + 1
            if retries >2:
               raise

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      self.oFSO.reportFWInfo()

      #Put CFW and S_OVL from this run back onto the drive since flash image may contain different self test code
      objMsg.printMsg("RESTORE FLASH:  Loading CFW and S_OVL from this config")
      if testSwitch.SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION:
         from Serial_Download import CDnldCode
      else:
         from base_SerialTest import CDnldCode

      dl = CDnldCode(self.dut, {'CODES': ['CFW', 'S_OVL'],})
      dl.run()

   def initializeSystemArea(self):
       '''Check to see if the system area should be initialized.  If it should, initialize it'''
       from base_SerialTest import CWriteETF
       oEFT =  CWriteETF(self.dut,{})

       objMsg.printMsg('\nCHECKING SYSTEM AREA INITIALIZATION...\n')

       if self.checkSystemAreaInit():
          #check to see if system area is prepped
          #objMsg.printMsg("RESTORE SYSTEM AREA:  Clearing system area")

          #THIS IS NOT WORKING ON GR50!!!!!!!!!  Instead clear sim files and flawlists in upcoming steps
          #oEFT.clearSystemArea()
          if testSwitch.BF_0178254_321126_SAVE_SYS_AREA_STATUS_IN_DRIVEATTR:
             self.dut.setSystemAreaState(1)
          else:
             self.dut.systemAreaPrepared = 1
       else:
          objMsg.printMsg("RESTORE SYSTEM AREA:  Restore state does not have prepped system area")
          if testSwitch.BF_0178254_321126_SAVE_SYS_AREA_STATUS_IN_DRIVEATTR:
             self.dut.setSystemAreaState(0)
          else:
             self.dut.systemAreaPrepared = 0

   def loadSimFile(self, simFilePath):
      '''Restore SIM area to a previously saved SIM area'''
      from SIM_FSO import objSimArea, initSimArea, reinitSimObject

      objMsg.printMsg('\nRESTORING SIM AREA...\n')

      simFile = open(simFilePath, 'rb').read()

      storedMd5 = simFile[-32:]
      simFile = simFile[:-32]
      generatedMD5 = self.generateMD5(simFile)
      if storedMd5 != generatedMD5:
         objMsg.printMsg('RESTORE SIM:  The MD5 value, %s,  does not match the calculated value of %s' %(storedMd5,generatedMD5))
         ScrCmds.raiseException(11044, "SIM file MD5 incorrect value")
      else:
         simRestore = myPickle.loads(simFile)

      #check to see if sim area is allocated
      if simRestore['simInitialized']:
         #re-initialize the python sim object
         objMsg.printMsg('RESTORE SIM:  Re-initializing SIM area')
         objSimArea.reinitializeObject(reinitSimObject, simRestore['simAllocation'], simRestore['totalAllocatedArea'])

         #re-initialize the drive sim area
         initSimArea()
      else:
         #Since we just cleared the system area, the sim area should not be initialized
         objMsg.printMsg("RESTORE SIM:  Restore state does not have initialized SIM area")
         return

      #write files to sim area
      for simKey, fileContents in simRestore['files'].items():
         objMsg.printMsg('RESTORE SIM:  Writing SIM file to SIM area - %s' %simKey)

         fileType = objSimArea[simKey]

         memFile = cStringIO.StringIO(fileContents)#[bytesSent : bytesSent + payLoadSize])

         self.oFSO.saveResultsFileToDrive(1, fileType = fileType, fileObj = memFile, exec231 = 1)

         #retrieve the file from the drive to make sure it was written properly
         path = self.oFSO.retrieveHDResultsFile(fileType)
         reReadFileLength = self.checkFileLength(path)

         objMsg.printMsg("RESTORE SIM:  Re-Read of drive SIM File had size %d" % (reReadFileLength))
         if reReadFileLength != len(fileContents):
            ScrCmds.raiseException(11044, "Re-read Sim file is incorrect size")

         rereadContents = open(path, 'rb').read()
         if rereadContents != fileContents:
           ScrCmds.raiseException(11044, "SIM file does not match what was written")


      #re-sync pf3 afh variables
      if 'AFH_SIM_FILE' in simRestore['files'].keys():
         objMsg.printMsg('Restoring the PF3 AFH frame data based on the AFH SIM file')
         from AFH_SIM import CAFH_Frames
         frm = CAFH_Frames()
         frm.clearFrames()
         frm.readFramesFromDRIVE_SIM()
         frm.display_frames()

         if frm.dPesSim.DPES_FRAMES == [] and not testSwitch.virtualRun:
            objMsg.printMsg('RESTORE SIM:  After Writing to the Sim File and then reading the same file back again no data was found!!!')
            ScrCmds.raiseException(11044,"DRIVE_SIM data not Found.")

   def loadStateDescription(self, filePath):

      objMsg.printMsg('\nLOAD THE STATE DESCRIPTION\n')

      descriptFile = open(filePath, 'rb').read()

      #check the MD5
      storedMd5 = descriptFile[-32:]
      descriptFile = descriptFile[:-32]
      generatedMD5 = self.generateMD5(descriptFile)
      if storedMd5 != generatedMD5:
         objMsg.printMsg('RESTORE PF3:  The MD5 value, %s,  does not match the calculated value of %s' %(storedMd5,generatedMD5))
         ScrCmds.raiseException(11044, "PF3 file MD5 incorrect value")
      else:
         self.stateDescription = myPickle.loads(descriptFile)

      self.printStateDescription()

   def loadPF3data(self, filePath):
      '''Restore selected PF3 data back to previously saved state'''
      objMsg.printMsg('\nRESTORE PF3 DATA\n')

      pf3File = open(filePath, 'rb').read()

      #check the MD5
      storedMd5 = pf3File[-32:]
      pf3File = pf3File[:-32]
      generatedMD5 = self.generateMD5(pf3File)
      if storedMd5 != generatedMD5:
         objMsg.printMsg('RESTORE PF3:  The MD5 value, %s,  does not match the calculated value of %s' %(storedMd5,generatedMD5))
         ScrCmds.raiseException(11044, "PF3 file MD5 incorrect value")
      else:
         pf3Data = myPickle.loads(pf3File)

      #Load the self.dut.objData
      self.loadObjData(pf3Data['OBJDATA'])

      #Load the self.dut. attribute data
      self.loadDutAttributes(pf3Data['DUT'])

      #Load local save/restore data
      self.localData = pf3Data['LOCAL']


      #Load self.dut.driveattr data
      if 'driveattr' in pf3Data['DUT']  and pf3Data['DUT']['driveattr'] != 'PICKLE_ERROR_FOUND':
         self.loadFISDriveAttributes(pf3Data['DUT']['driveattr'])
      else:
         objMsg.printMsg('RESTORE PF3:  The self.dut.driveattr was not saved')
         ScrCmds.raiseException(11044, "Can not restore FIS Drive Attribute")

   def loadDutAttributes(self,dutDict):
      '''Restore selected PF3 self.dut attributes'''

      objMsg.printMsg('RESTORE PF3:  self.dut attributes to be restored => %s' %DUT_ATTRIBUTES_TO_RESTORE)

      for attr in DUT_ATTRIBUTES_TO_RESTORE:
         if attr in dutDict:
            if dutDict[attr] == 'PICKLE_ERROR_FOUND':
               #when saving dut attributes, the instances, classes, methods, etc can not be pickled and saved
               objMsg.printMsg('RESTORE PF3:  Can not restore self.dut.%s because it could not be pickled and saved' %attr)
               ScrCmds.raiseException(11044, "DUT attribute can not be restored")
            else:
               objMsg.printMsg('RESTORE PF3:  Updating self.dut.%s from %s to %s' %(attr, getattr(self.dut, attr, '(Attribute does not exist)'), dutDict[attr]))
               setattr(self.dut, attr, dutDict[attr])

         else:
            objMsg.printMsg('RESTORE PF3:  Can not restore self.dut.%s because it was not saved in the baseline run' %attr)
            ScrCmds.raiseException(11044, "DUT attribute can not be restored")

      objMsg.printMsg('RESTORE PF3:  self.dut attributes restore complete')

   def loadFISDriveAttributes(self,driveAttrDict):
      '''Restore selected FIS attributes back to self.dut.driveattr'''

      objMsg.printMsg('RESTORE PF3:  FIS Drive Attributes (self.driveattr) to be restored => %s' %FIS_DRIVE_ATTRIBUTES_TO_RESTORE)

      for attr in FIS_DRIVE_ATTRIBUTES_TO_RESTORE:
         if attr in driveAttrDict:
            if driveAttrDict[attr] == 'PICKLE_ERROR_FOUND':
               #when saving dut attributes, the instances, classes, methods, etc can not be pickled and saved
               objMsg.printMsg('Can not restore self.dut.%s because it could not be pickled and saved' %attr)
               ScrCmds.raiseException(11044, "DUT attribute can not be restored")
            else:
               objMsg.printMsg('Updating self.driveattr.%s to %s' %(attr, driveAttrDict[attr]))
               self.dut.driveattr[attr] = driveAttrDict[attr]
               objMsg.printMsg(self.dut.driveattr[attr])
         else:
            objMsg.printMsg('Can not restore self.driveattr.%s because it was not saved in the baseline run' %attr)
            ScrCmds.raiseException(11044, "FIS drive attribute can not be restored")
      objMsg.printMsg('self.dut.driveattr attributes restore complete')

   def loadObjData(self,objData):
      '''Load the objData which is data saved throughout the process that is stored both in memory in a pickled file on the CM.
         It is possible the active memory object does not have all the data that the disc copy has.  To date, this feature
         does not seem to be used.  Currently, the save routine is not saving the active memory copy since it is the same as the
         disc copy
      '''
      objMsg.printMsg('RESTORE PF3:  Restoring Marshall Object...')
      tmpDict = self.dut.objData.marshallObject.copy()

      activeMemory = objData['ActiveMemory']
      discCopy = objData['Disc']

      #save the data to the file on disc
      try:
         self.dut.objData.pickleFile.open('wb')
         myPickle.dump(discCopy, self.dut.objData.pickleFile, self.dut.objData.pickleProt)
      finally:
         self.dut.objData.pickleFile.close()

      #set the object in memory
      if activeMemory:
         self.dut.objData.marshallObject = activeMemory
         self.dut.objData.currentState = self.dut.objData.states["unMerged"]
      else:
         #this will recover the data from the disc copy that we just saved
         self.dut.objData.marshallObject = discCopy
         self.dut.objData.currentState = self.dut.objData.states["merged"]

      #we don't want to overwrite these attributes.  We should be okay without this though because they get resaved in StateMachine
      #self.dut.objData.update({'NEXT_OPER': self.dut.nextOper, 'NEXT_STATE': self.dut.nextState, 'SEQ_NUM': self.dut.seqNum,})
      #self.dut.objData.update({'STATE_DBLOG_INFO':self.dut.stateDBLogInfo})
      #self.dut.objData.update({'DriveAttributes':self.dut.driveattr})

      self.dut.recoverProcessData()

   def loadDbiLog(self, filePath):
      '''Restore the DBI Log.  The system area must exist and init_fs must be run.'''
      objMsg.printMsg('\nRESTORING DBILOG...\n')
      objMsg.printMsg('RESTORE DBILOG:  Loading DBILog from %s' %filePath)

      #Load the file into memory
      sourcefile = open(filePath, 'rb').read()

      objMsg.printMsg('RESTORE DBILOG:  DBILog File has size of %s' %len(sourcefile))
      memFile = cStringIO.StringIO(sourcefile)
      ff = FileXferFactory.FileXferFactory(memFile, FileXferFactory.PCFILE_REQUEST_TYPES, 0)

      #Make the test call to restore the dbi log to the drive
      self.St({'test_num':130, 'prm_name': 'Download DBILog','CWORD2':0x0100, 'timeout':1000})
      ff.close()


      objMsg.printMsg('RESTORE DBILOG:  Retrieving DBILOG from the drive')
      dbiLogPath = self.retrieveDbiLog()

      retrievedFile = open(dbiLogPath,'rb').read()

      objMsg.printMsg('RESTORE DBILOG:  Retrieved File has size of %s' %len(retrievedFile))

      if sourcefile != retrievedFile:
         objMsg.printMsg('RESTORE DBILOG:  Retrieved DBILog does not match original DBILog')
         ScrCmds.raiseException(11044, "DBILog not properly restored")
      else:
         objMsg.printMsg('RESTORE DBILOG: File successfully loaded')

   def loadPrimaryDefectFile(self, filePath):
      '''Restore primary defect file to the drive.  The drive system area must be initialized'''
      objMsg.printMsg('\nRESTORING PRIMARY DEFECT FILE...\n')

      objMsg.printMsg('RESTORE PRIMARY DEFECT:  Loading Plist, TAlist, Slist from %s' %filePath)

      #st the call below used to restore the primary defect file expects a file with the name 1499.bin to
      #reside in the directory that is specified in the dlfile parameter.  in our case it is suppose to be
      #in the results directory.  we need to create a dummy file so we can pass this validation.  the real
      #primary defect file will be loaded into memory and passed to the drive by overriding the processRequest.
      fakeFlawPath = os.path.join(ScrCmds.getSystemResultsPath(),self.oFSO.getFofFileName(0),'1499.bin')
      if not os.path.isfile(fakeFlawPath):
         self.createResultsDirFile('1499.bin', '')

      #Load the file into memory
      sourcefile = open(filePath, 'rb').read()
      objMsg.printMsg('RESTORE PRIMARY DEFECT:  File to be restored has size of %s' %len(sourcefile))
      memFile = cStringIO.StringIO(sourcefile)
      ff = FileXferFactory.FileXferFactory(memFile, FileXferFactory.DLFILE_REQUEST_TYPES, 0)

      #Make the test call to restore the primary defect file
      self.St({'test_num' :149, 'prm_name': 'Download Primary Defect File', 'CWORD2':0x30, 'FILE_ID':1499, 'BLOCK':[0,0,0x594], 'dlfile':(CN,fakeFlawPath), 'timeout':300})

      ff.close()

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)


      objMsg.printMsg('RESTORE PRIMARY DEFECT:  Retrieving file from the drive to do comparison with uploaded file')
      flawListPath = self.retrievePrimaryDefectFile()

      retrievedFile = open(flawListPath,'rb').read()

      if sourcefile != retrievedFile:
         objMsg.printMsg('RESTORE PRIMARY DEFECT:  Retrieved DBILog does not match original DBILog')
         ScrCmds.raiseException(11044, "DBILog not properly restored")
      else:
         objMsg.printMsg('RESTORE PRIMARY DEFECT:  File successfully loaded to drive')


   def locateRestoreFiles(self):
      '''
        Find the restore zip file.
        This file can reside in the results directory if it was created during the same process.
        It could reside in the dlfiles directory either zipped or unzipped if it was included with the config
        It could reside on the FTP server if it was created in a baseline process.
        Look for it in this order - results dir, dlfiles dir zipped, dlfiles dir unzipped (look for manifest), ftp server
      '''

      zipFileName       = self.baseFileName + '.ZIP'
      mftFileName       = self.baseFileName + '.MFT'

      objMsg.printMsg('Looking for %s' %zipFileName)

      zipPath = os.path.join(ScrCmds.getSystemResultsPath(),self.oFSO.getFofFileName(0), zipFileName) #results dir
      zipPathDL = os.path.join(ScrCmds.getSystemDnldPath(), zipFileName)                              #dlfiles dir zipped
      mftPathDL = os.path.join(ScrCmds.getSystemDnldPath(), mftFileName)                              #dlfiles dir unzipped

      if os.path.isfile(zipPath):  #same process save/restore
         objMsg.printMsg('Zip found in results directory')
      elif os.path.isfile(zipPathDL):  #user uploaded files to dlfiles directory in config as zip of zips
         objMsg.printMsg('Zip found in dlfiles directory.  Copying zip to results directory')

         #copy it to the results dir because that is the only place we can unzip
         self.oFSO.binAppendFile([zipPathDL], zipFileName)

      elif os.path.isfile(mftPathDL):  #user uploaded files to dlfiles directory in config as single zip
         objMsg.printMsg('Zip found and already extracted in dlfiles directory')

         #leave files where they are and point to the dlfiles directory to get them
         self.manifestFilePath = mftPathDL

      elif testSwitch.FtpRestoreRecords:
            try:
               self.oFSO.retrieveFtpFiles(zipFileName)
               objMsg.printMsg('Retrieved zip from FTP site')
            except:
               objMsg.printMsg('Error: %s' % traceback.format_exc())
               objMsg.printMsg('Error in retrieving %s from FTP site' %zipFileName)
               ScrCmds.raiseException(11044, "Restore point not available")
      else:
         objMsg.printMsg('Restore zip file %s does not exist in results or dlfiles directory or on FTP site' %zipFileName)
         ScrCmds.raiseException(11044, "Restore point not available")

      #if we found the manifest file, it is because the zip was found unzipped in dlfiles dir.
      #Otherwise, the zip should be in results dir by now and needs to be unzipped and manifest needs to be located
      if not self.manifestFilePath:
         self.extractZip(zipFileName)

         mftPath = os.path.join(ScrCmds.getSystemResultsPath(),self.oFSO.getFofFileName(0), mftFileName)
         if os.path.isfile(mftPath):
            self.manifestFilePath = mftPath
         else:
            objMsg.printMsg('Error:  Manifest file of restore zip does not exist %s' %mftPath)
            ScrCmds.raiseException(11044, "Restore point not available")

      #load the manifest file into memory
      self.manifest = self.loadManifest()


   def loadManifest(self):
      '''Load the manifest from the restore zip file'''

      objMsg.printMsg('Loading manifest - %s' %self.manifestFilePath)

      fileContents = open(self.manifestFilePath, 'rb').read()

      manifest = eval(fileContents)

      for key, filename in manifest.items():
         #keys could contain a value of None if the file was not saved (i.e. the system area does not exist so do not save sim)
         if filename:
            manifest[key] = os.path.join(os.path.dirname(self.manifestFilePath), filename)

         objMsg.printMsg('%s - %s' %(key, manifest[key]))
      return manifest

   def cleanUpRestoreFiles(self):
      '''Delete the files that were extracted from the zip in order to conserve space in the results directory'''

      objMsg.printMsg('Cleaning up restore files in the results directory')
      for fileType, filePath in self.manifest.items():
         if filePath and os.path.isfile(filePath) and ScrCmds.getSystemResultsPath() in filePath:
            objMsg.printMsg('%s - Deleting %s from results directory' %(fileType, filePath))
            fObj = GenericResultsFile(os.path.basename(filePath))
            fObj.delete()


      #delete the manifest file if it exists in the results directory
      if os.path.isfile(self.manifestFilePath) and ScrCmds.getSystemResultsPath() in self.manifestFilePath:
         objMsg.printMsg('MFT - Deleting %s from results directory' %self.manifestFilePath)
         fObj = GenericResultsFile(os.path.basename(self.manifestFilePath))
         fObj.delete()

      #reset the manifest values
      self.manifest = {}
      self.manifestFilePath = None

class CCreateRestorePoint(CRestoreBase):
   """
     Description: Class that will saves the necessary pieces required to create a restore point
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, restoreStateName, baseline, operationName):
      CRestoreBase.__init__(self, restoreStateName, baseline, operationName)
      self.systemAreaPrepared = None

   def run(self):
      '''Save the necessary pieces to recreate a drive state'''

      #check to make sure sf3 code is on the drive
      if objComMode.getMode() != objComMode.availModes.mctBase:
         objMsg.printMsg('F3 code is on the drive.  Can not save drive state')
         return

      fileCollector = {}

      #clear the stateState data
      self.localData = {}

      #save the flash img
      fileCollector['FLASHIMG'] = self.saveFlashImage()

      #save whether or not the system area is initialized
      self.systemAreaPrepared = self.checkSystemAreaInit()

      if self.systemAreaPrepared != self.dut.systemAreaPrepared :
         objMsg.printMsg('Warning:  self.dut.systemAreaPrepared does not match CAP value')

      #save SIM files
      fileCollector['SIM'] = self.saveSIMFiles()

      #save DBIlog
      fileCollector['DBILOG'] = self.saveDbiLog()


      #save primary defect file
      fileCollector['PRIM_DEFECT'] = self.savePrimaryDefectFile()

      #save PF3 data.  Keep this step last in case we want to save any local data from this class
      fileCollector['PF3'] = self.savePF3data()

      #save the state description
      fileCollector['DESCRIPTION'] = self.saveDescription()


      #----------
      #If this state has already been saved off once during this process, append a REC# onto it
      if self.restoreStateName in self.dut.localRestoreSet:
         self.restoreStateName += '-REC'
         n = 0
         while 1:
            n += 1
            if self.restoreStateName + str(n) not in self.dut.localRestoreSet:
               self.restoreStateName += str(n)
               break

      #create zip file
      zipName = self.createZip(self.baseFileName, fileCollector)

      #ftp records
      if testSwitch.FtpRestoreRecords == 1:
         #files = self.dut.localRestoreSet[self.restoreStateName].values()
         self.oFSO.ftpFiles(zipName)

      self.dut.localRestoreSet.append(self.restoreStateName)

   def saveFlashImage(self):
      '''
         Save the flash image off the drive and store it in PCFILES/flashimg directory.
         Move it to the results directory so we can rename it
      '''
      objMsg.printMsg('\nSAVING FLASH IMAGE\n')

      #Save the flash image using 178
      flashBinaryLocation = self.oFSO.saveFlashImageToPCFile()

      objMsg.printMsg('Save Flash: File successfully saved to %s' %flashBinaryLocation)
      return flashBinaryLocation

   def saveSIMFiles(self):
      '''
         Save the SIM files off the drive (except the results file).
         Create a python dictionary to store the files and information about the SIM area.
         Pickle this dictionary and save it to a file in the results directory
      '''

      objMsg.printMsg('\nSAVING SIM FILES\n')

      #save system area SIM files
      simDescriptor = self.setupSimFile()
      pcklFile = myPickle.dumps(simDescriptor)

      #generate md5
      md5Value = self.generateMD5(pcklFile)
      objMsg.printMsg('Save Sim:  MD5 = %s' %md5Value)
      pcklFile += md5Value

      outFilePath = self.createResultsDirFile('sim.p', pcklFile)

      objMsg.printMsg('Save SIM: File successfully saved to output folder %s' %outFilePath)
      return outFilePath

   def setupSimFile(self):
      '''Create a pickled dictionary that contains all necessary SIM area data including the SIM files'''
      from SIM_FSO import objSimArea

      objMsg.printMsg('Creating SIM Restore File')

      simDescriptor = {
                     'totalAllocatedArea'    : 0 ,
                     'systemAreaPrepped'    : self.systemAreaPrepared,
                     'simInitialized'        : 0,   #does header record exist yet
                     'simAllocation'         : {},  #same as simDict in sim_fso
                     'simTable'              : None,#latest 231 dblog table
                     'files'                 : {},  #retrieved sim files store by simKey
                     }

      if not self.systemAreaPrepared and not testSwitch.virtualRun:
         #dut variable initially set by fis attribute so bench process may not always reflect true state
         objMsg.printMsg('Save SIM:  System Area not prepped.')
         return None


      response = self.oFSO.checkIndexExists(objSimArea['HEADER_RECORD'])
      if response == False:
         objMsg.printMsg('Test 231 call failed.  There is no access to the system area')
         return None
      else:
         simExists, SIM_Header, numSIMFiles = response
         simAllocated = int(SIM_Header[(numSIMFiles*-1)+objSimArea['HEADER_RECORD'].index]['STATUS'],16) & 0x3


      #save the P231_Header_Info table without the dblog class referenences
      tmpList = []
      for row in SIM_Header:
         tmpDict = {}
         for key, value in row.items():
            tmpDict[key] = value
         tmpList.append(tmpDict)
      simDescriptor['simTable'] = tmpList
      simDescriptor['totalAllocatedArea'] = objSimArea.size

      if not simAllocated and not testSwitch.virtualRun:
         objMsg.printMsg('Save SIM:  SIM Area not allocated.')
         return simDescriptor
      else:
         objMsg.printMsg('Save SIM:  SIM Area is allocated.')
         simDescriptor['simInitialized'] = 1


      for simKey, simStruct in objSimArea.SIM_LIST.items():
         #build up the sim dictionary
         simDescriptor['simAllocation'][simKey] = (simStruct.index, simStruct.name, simStruct.size)

         status     = int(SIM_Header[(numSIMFiles*-1)+int(simStruct.index)]['STATUS'], 16)
         if status & 0x20 and simKey not in ['SPT_RESULTS_FILE', 'HEADER_RECORD']:
            #get the file length from the sim table
            fileLength = int(SIM_Header[(numSIMFiles*-1)+int(simStruct.index)]['FILE_LENGTH'])

            #retrieve the file
            if not testSwitch.virtualRun:
               objMsg.printMsg('Retrieving %s file from SIM area on drive' %simKey)
               pcfilesPath = self.oFSO.retrieveHDResultsFile(objSimArea[simKey])

               retrievedFile = open(pcfilesPath,'rb').read()

               #verify it is the same file length as what it says in the table
               if fileLength != len(retrievedFile):
                  ScrCmds.raiseException(11044, "Retrieve SIM file size does not match size reported in P231_HEADER")
               else:
                  objMsg.printMsg('Save SIM:  Verified correct file size retrieved -- %s ' %len(retrievedFile))
                  simDescriptor['files'][simKey] = retrievedFile

      objMsg.printMsg('Save SIM:  Finished retrieving SIM files -- %s ' %simDescriptor['files'].keys())

      return simDescriptor

   def savePrimaryDefectFile(self):
      '''
         Save the primary defect file off the drive and store it in PCFILES/flashimg directory.
         Move it to the results directory so we can rename it
      '''
      objMsg.printMsg('\nSAVING PRIMARY DEFECT FILE\n')

      if not self.systemAreaPrepared:
         #dut variable initially set by fis attribute so bench process may not always reflect true state
         objMsg.printMsg('Save Primary Defect::  System Area not prepped. No flawlists exist')
         return None
      else:
         flawListPath = self.retrievePrimaryDefectFile()

         if not testSwitch.virtualRun:
            retrievedFile = open(flawListPath,'rb').read()
            objMsg.printMsg('Save Primary Defect: Retrieved File has size of %s' %len(retrievedFile))

      objMsg.printMsg('Save Primary Defect:  File successfully saved to output folder %s' %flawListPath)
      return flawListPath

   def saveDbiLog(self):
      '''
         Save the dbilog off the drive and store it in PCFILES/flashimg directory.
         Move it to the results directory so we can rename it
      '''
      objMsg.printMsg('\nSAVING DBILOG\n')


      if not self.systemAreaPrepared:
         #dut variable initially set by fis attribute so bench process may not always reflect true state
         objMsg.printMsg('Save DBILog:  System Area not prepped. No flawlists exist')
         return None
      else:

         objMsg.printMsg('Save DBILog:  Retrieving DBILOG from the drive')
         try:
            dbiLogPath = self.retrieveDbiLog()
         except ScriptTestFailure, (failuredata):
            objMsg.printMsg('Error: %s' % (traceback.format_exc(),))

            #10113 error code means return no or bad dbi log.  Assume it hasn't been created yet.
            if failuredata[0][2] in [10113]:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
               #outFilePath = self.createResultsDirFile(outputFileName, 'NO_DATA')
               objMsg.printMsg('Save DBILog:  Could not retrieve DBILOG.  Must run INIT_FS first')
               return None
            else:
               raise

         if not testSwitch.virtualRun:
            retrievedFile = open(dbiLogPath,'rb').read()
            objMsg.printMsg('Save DBILog:  Retrieved File has size of %s' %len(retrievedFile))


         objMsg.printMsg('Save DBILog:  File successfully saved to output folder %s' %dbiLogPath)
         return dbiLogPath

   def saveDescription(self):

      self.stateDescription['SBR'] = self.dut.sbr
      self.stateDescription['Operation'] = self.dut.nextOper
      self.stateDescription['Last State Ran'] = self.dut.lastState
      self.stateDescription['State Sequence Number'] = self.dut.seqNum
      self.stateDescription['Completed States'] = self.dut.statesExec[self.dut.nextOper]
      self.stateDescription['Date Created'] = time.strftime("%c")
      self.stateDescription['System Area Prepared'] = self.systemAreaPrepared

      self.printStateDescription()

      pcklFile = myPickle.dumps(self.stateDescription)

      #generate md5
      md5Value = self.generateMD5(pcklFile)
      objMsg.printMsg('Save State description:  MD5 = %s' %md5Value)
      pcklFile += md5Value

      #save file to results directory
      outFilePath = self.createResultsDirFile('description.p', pcklFile)
      objMsg.printMsg('Save State Description: File successfully saved to output folder %s' %outFilePath)
      return outFilePath



   def savePF3data(self):
      '''
         Save the pertinent PF3 data such as the dut object into a pickled file.
      '''
      pf3Data = {}
      objMsg.printMsg('\nSAVING PF3 DATA\n')

      #save self.dut attributes
      pf3Data['DUT'] = self.saveDUTAttributes()
      pf3Data['LOCAL'] = self.localData

      pf3Data['OBJDATA'] = {}
      pf3Data['OBJDATA']['ActiveMemory'], pf3Data['OBJDATA']['Disc'] = self.saveObjData()

      pcklFile = myPickle.dumps(pf3Data)

      #generate md5
      md5Value = self.generateMD5(pcklFile)
      objMsg.printMsg('Save PF3:  MD5 = %s' %md5Value)
      pcklFile += md5Value

      #save file to results directory
      outFilePath = self.createResultsDirFile('pf3.p', pcklFile)
      objMsg.printMsg('Save PF3: File successfully saved to output folder %s' %outFilePath)
      return outFilePath

   def saveDUTAttributes(self):
      objMsg.printMsg('Saving the self.dut attributes...')

      #make a copy of the attributes of the dut object
      tmpDict = getattr(self.dut,'__dict__').copy()

      #determine which attributes can be pickled and which cannot.  Since Gemini operates in restricted mode we
      #cannot access __dict__ therefore instances, classes cannot be pickled without manipulation.  Since we would
      #need to manual determine how to pickle each attribute on an individual basis let's make it easy and just don't
      #save those attributes.
      dutDict = {}
      for attr, attrVal in tmpDict.items():
         dutDict[attr] = attrVal
         try:
            pcklFile = myPickle.dumps(dutDict)
         except:
            objMsg.printMsg('Could not save %s because %s type can not be pickled.' %(attr, type(attrVal)))
            dutDict[attr] = 'PICKLE_ERROR_FOUND'

      return dutDict

   def saveObjData(self, saveActiveMemory = 0):
      '''Save the self.dut.objData marshall object.  There is the copy that is in memory and there is the copy that
         is pickled and written to the CM.  To save space, it is defaulted to only save the copy on disc since these
         copies are normally synced anyway'''

      objMsg.printMsg('Saving the self.dut.objData file...')

      #save the copy in memory
      activeMemory = None
      if saveActiveMemory:
         activeMemory = self.dut.objData.marshallObject
         #retrieve the disc copy
         discCopy = self.dut.objData.recover(replace = 0)
         return activeMemory, discCopy
      else:
         #sync the memory copy with what it on disc
         self.dut.objData.serialize()
         #retrieve the disc copy
         discCopy = self.dut.objData.recover(replace = 0)
         return None, discCopy

