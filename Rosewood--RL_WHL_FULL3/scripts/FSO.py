#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: FSO module holds all functions for file system access on the drive as well as CM level
#                 overrides/implementations.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/15 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/FSO.py $
# $Revision: #4 $
# $DateTime: 2016/12/15 23:34:49 $
# $Author: weichen.lau $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/FSO.py#4 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
import os, sys, re, types, traceback, operator
from Test_Switches import testSwitch
from Process import CProcess
import struct, binascii
import MessageHandler as objMsg
from Carrier import theCarrier
from Drive import objDut
import ScrCmds, time
import DBLogDefs, stat
from PowerControl import objPwrCtrl
from  PackageResolution import PackageDispatcher
import serialScreen, sptCmds
from sptCmds import objComMode
import CommitServices
import dbLogUtilities
from UPS import upsObj

DEBUG = 0

import Utility

class CFSO(CProcess):
   def __init__(self):
      CProcess.__init__(self)
      self.oUtility = Utility.CUtility()
      self.dut = objDut
      self.request21File = None
      self.dth = dataTableHelper()

   def binAppendFile(self, inputFiles, outputFile):
      """
      Binary appends the files in inputFiles <in sequence order> then writes them to outputFile
      @param inputFiles: Sequence containing paths of files in order to create output file.
      @param outputFile: Path to save new file to.
      """


      outputFile = GenericResultsFile(outputFile)
      outputFile.open('wb')
      try:
         if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE and testSwitch.virtualRun:
            pass
         else:
            for f in inputFiles:
               if type(f) == types.StringType:
                  outputFile.write(open(f,'rb').read())
               else:
                  outputFile.write(f.read())
      finally:
         outputFile.close()
      return outputFile

   def updateAdaptive(self,inPrm, iTimeout):
      """Update the CAP, RAP and/or SAP tables with new values from user input parameters or depopulate the SAP."""
      self.St(178,inPrm,timeout = iTimeout)

   def readRAP(self):
      self.St({'test_num':172, 'prm_name':'Read Binary RAP','CWORD1':0x0009,'timeout': 1000}) # Read RAP

   def readSAP(self):
      self.St({'test_num':172, 'prm_name':'Read Binary SAP','CWORD1':0x0000,'timeout': 1000}) # Read SAP

   def readMCandUMPInfo(self):
      self.St({'test_num':172, 'prm_name':'Read MC and UMP Info','CWORD1':57,'timeout': 1000})
      numMC = int(self.dut.dblData.Tables('P172_MISC_INFO').chopDbLog('DESCRIPTION', 'match', 'NumMediaCacheZonesFrames')[-1].get('VALUE'))
      umpStartZone = int(self.dut.dblData.Tables('P172_MISC_INFO').chopDbLog('DESCRIPTION', 'match', 'UMPStartZone')[-1].get('VALUE'))
      numUMPZonesPerHead = int(self.dut.dblData.Tables('P172_MISC_INFO').chopDbLog('DESCRIPTION', 'match', 'NumUMPZonesPerHead')[-1].get('VALUE'))
      return numMC, umpStartZone, numUMPZonesPerHead

   def updateUMP_MC_Zone(self, ump_start_zone, num_ump_zone, num_mc_zone):
      self.St({'test_num': 178, 'prm_name': 'Update UMP and MC Zone',
               'CWORD1':0x0220, 'UMP_START_ZONE': ump_start_zone,
               'NUM_UMP_ZONE': num_ump_zone, 'NUM_MC_ZONE': num_mc_zone,
               'timeout': 1200, 'spc_id': 1,})
      self.saveRAPtoFLASH()
      numMC, umpStartZone, numUMPZonesPerHead = self.readMCandUMPInfo()
      TP.UMP_ZONE[self.dut.numZones] = range(umpStartZone, umpStartZone + numUMPZonesPerHead) + [self.dut.numZones-1]
      TP.numMC = numMC
      TP.numUMP = len(TP.UMP_ZONE[self.dut.numZones])
      
      if testSwitch.FE_348085_P_NEW_UMP_MC_ZONE_LAYOUT:
         TP.MC_ZONE = range(umpStartZone + numUMPZonesPerHead, umpStartZone + numUMPZonesPerHead + numMC)
      elif testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
         TP.MC_ZONE = range(1,numMC+1,1)
      else:
         TP.MC_ZONE = range(umpStartZone - numMC, umpStartZone)

   def updateUMP_Zone(self, ump_start_zone, num_ump_zone):
      self.St({'test_num': 178, 'prm_name': 'Update UMP Zone',
               'CWORD1':0x0220, 'UMP_START_ZONE': ump_start_zone,
               'NUM_UMP_ZONE': num_ump_zone,
               'timeout': 1200, 'spc_id': 1,})
      self.saveRAPtoFLASH()
      numMC, umpStartZone, numUMPZonesPerHead = self.readMCandUMPInfo()
      TP.UMP_ZONE[self.dut.numZones] = range(umpStartZone, umpStartZone + numUMPZonesPerHead) + [self.dut.numZones-1]
      TP.numUMP = len(TP.UMP_ZONE[self.dut.numZones])

   def readServoTrackInfo(self):
      self.St({'test_num':172, 'prm_name':'Read Servo Track Info','CWORD1':58,'timeout': 1000})
      return int(str(self.dut.dblData.Tables('P172_MISC_INFO').tableDataObj()[-1]['VALUE'])) # returned value already in decimal

   def saveSAPtoFLASH(self):
      self.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})

   def saveRAPtoFLASH(self):
      if testSwitch.extern.COMPRESSED_ADAPTIVES:
         self.St({'test_num':178, 'prm_name':'Save RAP in RAM to FLASH', 'CWORD1':0x220, 'timeout': 1000})
      else:
         self.St({'test_num':178, 'prm_name':'Save RAP in RAM to FLASH', 'CWORD1':0x220,})

   def saveRAPSAPtoFLASH(self):
      if testSwitch.extern.COMPRESSED_ADAPTIVES:
         self.St({'test_num':178, 'prm_name':'Save RAP and SAP in RAM to FLASH', 'CWORD1':0x620, 'timeout': 1000})
      else:
         self.St({'test_num':178, 'prm_name':'Save RAP and SAP in RAM to FLASH', 'CWORD1':0x620,})

   def recoverSAPfromPCtoFLASH(self):
      try:
         self.St({'test_num':178, 'prm_name':'Recover SAP from PC to FLASH', 'timeout':120,'CWORD1':0x421})
      except ScriptTestFailure,(failureData):
         if failuredata[0][2] in [11049,11087]: #if it is time out failure, ignore it and continue the test
            objMsg.printMsg("Timeout failure!!!!! SOC BUG workaround 21...")
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10,baudRate=Baud115200, useESlip=1)
            pass
         else:
            raise
      self.St({'test_num':1, 'prm_name':'spinupPrm_1','timeout':100,"CWORD1" : (0x1,), "MAX_START_TIME" : (200,), "DELAY_TIME" : (50,),})

   if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
      def saveFlashImageToPCFile(self):
         """Save the flash image as a binary file in the pcfiles directory.  The binary can be converted to LOD for download or seaserialed as is"""
         self.St({'test_num':178, 'prm_name':'Save Flash to BIN file', 'CWORD4':0x1, 'timeout':600 })

         file = os.path.join(ScrCmds.getSystemPCPath(),'flashimg',self.getFofFileName(0))
         if not os.path.isfile(file) and not testSwitch.virtualRun:
            ScrCmds.raiseException(11044, "Image not found in PCFILES flashimg directory")

         return file

   def checkSimAllocated(self):
      '''Determine if the SIM area has been allocated'''

      #if no system area exists then SIM area does not exist
      if not self.dut.systemAreaPrepared:
         return 0

      #get the SIM area header record
      from SIM_FSO import objSimArea
      response = self.checkIndexExists(objSimArea['HEADER_RECORD'])


      if response == False:
         #the test 231 call the accesses the sim area failed.  assume sim area does not exist
         return 0
      else:
         simExists, SIM_Header, numSIMFiles = response
         #if the header record exists assume the rest of the sim area is initialized also since this
         #operation happens at the same time
         simAllocated = int(SIM_Header[(numSIMFiles*-1)+objSimArea['HEADER_RECORD'].index]['STATUS'],16) & 0x3
         return simAllocated

   def checkIndexExists(self, fileType):
      #Check and see if the drive's sim was written for this pass index


      if testSwitch.FE_0120780_231166_F3_SPT_RESULTS_ACCESS and (objComMode.getMode() != objComMode.availModes.mctBase) and (self.dut.f3Active == True):
         if testSwitch.extern.FE_0191285_496741_STRING_REPRESENTATION_OF_SIM_FILE:
            objMsg.printMsg("Checking if sim exists for filename %s" % (fileType.name))
         else:
            objMsg.printMsg("Checking if sim exists for index %d" % (fileType.index,))
         import serialScreen, sptCmds
         oserial = serialScreen.sptDiagCmds()
         oserial.enableDiags()
         headInfo, SIM_Header = oserial.getSPTResultsHeaderData(printResult = True)
         numSIMFiles = int(headInfo.get('ENTRIES', 0))
         sptCmds.enableESLIP()
         objMsg.printMsg("Parsed header Data: %s, %s" % (SIM_Header, numSIMFiles))
         if testSwitch.extern.FE_0191285_496741_STRING_REPRESENTATION_OF_SIM_FILE:
            simExists = 0
            for i in SIM_Header:
               if i['FILE_NAME'] == fileType.name:
                  simExists = int(i['STATUS'],16) & 0x20
                  break
            objMsg.printMsg("simExists: %s; fileName %s" % (simExists,fileType.name))
         else:
            simExists = int(SIM_Header[fileType.index]['STATUS'],16) & 0x20
            objMsg.printMsg("simExists: %s; index %d" % (simExists, int(SIM_Header[fileType.index]['STATUS'],16)))

      else:
         timeout = 2000
         SetFailSafe()
         stats = self.St({'test_num':231,
                          'prm_name':'Verify SIM written',
                          'CWORD1':0x04,
                          'timeout':timeout})
         ec = stats[2]
         ClearFailSafe()
         if ec != 0:
            return False

         #Number of sim files for reverse table lookup
         numSIMFiles = int(self.dut.dblData.Tables('P231_HEADER').tableDataObj()[-1]['ENTRIES'])

         SIM_Header = self.dut.dblData.Tables('P231_HEADER_INFO').tableDataObj()
         if testSwitch.extern.FE_0191285_496741_STRING_REPRESENTATION_OF_SIM_FILE:
            simExists = 0
            for i in reversed(SIM_Header): #need to reverse it so the latest table is parsed
               if i['FILE_NAME'] == fileType.name:
                  simExists = int(i['STATUS'],16) & 0x20
                  break
         else:
            simExists = int(SIM_Header[(numSIMFiles*-1)+fileType.index]['STATUS'],16) & 0x20

      return simExists, SIM_Header, numSIMFiles


   def retrieveHDResultsFile(self, fileType = None):
      """
      Retrieve the resusults file saved to the ETF from the drive.
      @param outputFlag: 1 to output to results file, 2 (default) to save to pcfile
      @return None if option 1; path to PC file if option 2
      @param fileType: File type to retrieve from the drive ['RES','AFH']
      U{Test 231 Documentation<http://col-cert-01.am.ad.seagate.com/platform/Self Test Docs/docs/latest/Descriptions/test231.html>}
      """
      if not testSwitch.FE_0120780_231166_F3_SPT_RESULTS_ACCESS and objComMode.getMode() != objComMode.availModes.mctBase:
         return None

      if fileType:
         timeout = 2000 #BF_0116156_231166_TMO_TO_FUNC_DEF_IN_RETRIEVEHDRESULTSFILE

         simExists, SIM_Header, numSIMFiles = self.checkIndexExists(fileType)

         if simExists:
            if testSwitch.FE_0120780_231166_F3_SPT_RESULTS_ACCESS and objComMode.getMode() != objComMode.availModes.mctBase:
               import serialScreen
               oserial = serialScreen.sptDiagCmds()
               oserial.enableDiags()
               sFile = "%s.bin" % str(fileType)
               oserial.getSPTResultsFile(fileType.index, sFile, printResult = True)
               sptCmds.enableESLIP()

               fPath = os.path.join(ScrCmds.getSystemResultsPath(),self.getFofFileName(0),sFile)
            else:
               SetFailSafe()

               prm_retrieve = {
                                'test_num':231,
                                'prm_name':'Retrieve Results file from HD',
                                'CWORD1':0x02,
                                'PASS_INDEX':fileType.index,
                                'FOLDER_NAME': fileType.mct(),
                                'timeout':timeout
                              }
               if testSwitch.extern.FE_0191285_496741_STRING_REPRESENTATION_OF_SIM_FILE:
                  if 'PASS_INDEX' in prm_retrieve:
                     del prm_retrieve['PASS_INDEX'] #remove index
               if testSwitch.UPS_PARAMETERS:
                  param.update({'FOLDER_NAME': fileType.name})

               stats = self.St(prm_retrieve)
               ec = stats[2]
               ClearFailSafe()
               if ec != 0:
                  ScrCmds.raiseException(ec,"Failed to Retrieve Results File!")

               fPath = os.path.join(ScrCmds.getSystemPCPath(), fileType.name, self.getFofFileName(0))
         else:
            if testSwitch.extern.FE_0191285_496741_STRING_REPRESENTATION_OF_SIM_FILE:
               objMsg.printMsg("*"*20 + "FileName: %s" % fileType.name)
               ScrCmds.raiseException(14524,{'msg':"SIM file not written",'FILE_NAME':fileType.name})
            else:
               objMsg.printMsg("*"*20 + "PASS_INDEX: %s\t" % fileType.index + "Status Retrieved: %s" % int(SIM_Header[(numSIMFiles*-1)+fileType.index]['STATUS'],16))
               ScrCmds.raiseException(14524,{'msg':"SIM file not written",'PASS_INDEX':fileType.index})

         return fPath

      else:
         ScrCmds.raiseException(11044,'Invalid ETF results file option chosen: %s' % str(fileType))

   def getFofFileName(self,file = 1):
      """
      Return the FOF file/folder name for the cell/tray/port index
      @param file: Default set to 1= return file name. 0 means return folder name
      """
      return ScrCmds.getFofFileName(file)

   def getFileLen(self, fPath):
      if not os.path.isfile(fPath):
         objMsg.printMsg("Missing File: %s" % fPath, objMsg.CMessLvl.DEBUG)
         ScrCmds.raiseException(FOFFileIsMissing,"Missing File: %s" % fPath)
      else:
         stSize = os.stat(fPath)[stat.ST_SIZE]
         if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
            objMsg.printMsg("File Size(%s): %s" % (fPath,str(stSize)), objMsg.CMessLvl.VERBOSEDEBUG)
         return stSize

   def saveResultsFileToDrive(self, forceNew = 0, filePath = '', fileSize = 0, fileType = None, exec231 = 0, fileObj = None):
      """
      Download a file to the drive using test 231.
      @param filePath: Path to file to download to the drive; Default is Gemini Results File
      @param fileSize: Length of file to download to drive; Default is for Gemini Results File
      @param fileType: File type to send to the drive see Constants.py->SIM File types
      U{Test 231 Documentation<http://col-cert-01.am.ad.seagate.com/platform/Self Test Docs/docs/latest/Descriptions/test231.html>}
      """
      global FileLength,FileObj
      FileLength = ''
      FileObj = ''

      if forceNew == 0:
         if testSwitch.extern.FE_0115432_231166_ADD_APPEND_TO_SPT_RESULTS_FILE_IN_231:
            if not self.checkIndexExists(fileType)[0]:
               objMsg.printMsg("No results file found on drive.", objMsg.CMessLvl.DEBUG)

               forceNew = 1
         else:
            try:

               hdResFile = self.retrieveHDResultsFile(fileType)
               objMsg.printMsg("Results file saved on CM to: %s" % str(hdResFile))

            except:
               objMsg.printMsg("No results file found on drive.", objMsg.CMessLvl.DEBUG)
               objPwrCtrl.powerCycle()
               forceNew = 1

      if not filePath == '':
         if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
            objMsg.printMsg("Downloading file %s to drive ..." % filePath, objMsg.CMessLvl.DEBUG)
         if forceNew == 0 and not testSwitch.extern.FE_0115432_231166_ADD_APPEND_TO_SPT_RESULTS_FILE_IN_231:
            FileName = self.binAppendFile([hdResFile,filePath],'out.tmp')
         else:
            FileName = filePath

         if testSwitch.extern.FE_0115432_231166_ADD_APPEND_TO_SPT_RESULTS_FILE_IN_231:
            if fileSize == 0:
               FileLength = self.getFileLen(FileName)
            else:
               FileLength = fileSize

         else:
            if not fileSize == 0 and not forceNew == 0:
               FileLength = args[1]
            else:
               FileLength = self.getFileLen(FileName)
         FileObj = open(FileName,"rb")
         objMsg.printMsg(  "File %s open OK" % FileName, objMsg.CMessLvl.VERBOSEDEBUG)
      elif fileObj and testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
         FileObj = fileObj
         if not fileSize:
            FileObj.seek(0,2)  # Seek to the end
            FileLength = FileObj.tell()
            FileObj.seek(0)
         else:
            FileLength = fileSize
      else:
         if forceNew == 0 and not testSwitch.extern.FE_0115432_231166_ADD_APPEND_TO_SPT_RESULTS_FILE_IN_231:
            ResultsFile.open('rb')
            FileName = self.binAppendFile([hdResFile,ResultsFile],'out.tmp')
            ResultsFile.close()
            FileName.open('rb')
            FileName.seek(0,2)  # Seek to the end
            FileLength = FileName.tell()
            FileName.seek(0)
            FileObj = FileName # pass the file object to processRequest16
         else:
            ResultsFile.open()
            ResultsFile.seek(0,2)  # Seek to the end
            FileLength = ResultsFile.tell()
            ResultsFile.seek(0)    # Seek to the start
            FileObj = ResultsFile  # pass the file object to processRequest16

      if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
         objMsg.printMsg(  "DL file len = %s" % FileLength, objMsg.CMessLvl.VERBOSEDEBUG)

      # intercept request key 16 from core code
      RegisterResultsCallback(self.processRequest16,[16,17],useCMLogic=0)

      if exec231 == 1:
         try:
            ec = 1
            retry = 4
            while ec !=0:
               SetFailSafe()
               if testSwitch.extern.FE_0115432_231166_ADD_APPEND_TO_SPT_RESULTS_FILE_IN_231 and forceNew == 0:
                  saveFileDict = {
                     'test_num':231,
                     'prm_name':"Appending file to drive",
                     'CWORD1':0x40,
                     'DL_FILE_LEN':(FileLength>>16, FileLength & 0x0000ffff),
                     'PASS_INDEX': fileType.index,
                     'FOLDER_NAME': fileType.mct(),
                     'timeout':2000}
                  if testSwitch.extern.FE_0191285_496741_STRING_REPRESENTATION_OF_SIM_FILE:
                     if 'PASS_INDEX' in saveFileDict: del saveFileDict['PASS_INDEX']
                  stats = self.St(saveFileDict)
               else:
                  saveFileDict =  {
                     'test_num':231,
                     'prm_name':"Saving file to drive",
                     'CWORD1':0x01,
                     'DL_FILE_LEN':(FileLength>>16, FileLength & 0x0000ffff),
                     'PASS_INDEX': fileType.index,
                     'FOLDER_NAME': fileType.mct(),
                     'timeout':2000}
                  if testSwitch.extern.FE_0191285_496741_STRING_REPRESENTATION_OF_SIM_FILE:
                     if 'PASS_INDEX' in saveFileDict: del saveFileDict['PASS_INDEX']
                  stats = self.St(saveFileDict)
               ec = stats[2]
               ClearFailSafe()
               if ec == 10451 and retry >= 0 and testSwitch.WA_0152247_231166_P_POWER_CYCLE_RETRY_SIM_ERRORS:
                  objPwrCtrl.powerCycle(useESlip = 1)
                  retry -=1
               else:
                  break

            if ec != 0:
               ScrCmds.raiseException(ec,"Failed to Save Results File!")

            self.dut.saveToDisc = 1
         except:
            #ReportErrorCode(self.dut.errCode) #Not needed if section of code doesn't raise MCT EC
            self.dut.saveToDisc = -1

      FileObj.close()

      #release the interception
      self.dut.setMyParser()


   def processRequest16(self,requestData,currentTemp,drive5,drive12,collectParametric):
      """
      Results Callback for Block 16-> download file to drive
      requestData is a string from the UUT asking for a block from a file
      return a frame, raise an exception on error

      """
      requestKey = ord(requestData[0])
      # code 6 typically requests a block of data from the download file;  get_data_file()
      #objMsg.printMsg("block request: %s" % requestKey)
      if requestKey == 16:
         blockSize = (int(ord(requestData[3]))<<8) + int(ord(requestData[2]))
         requestHI = requestData[5]
         requestLO = requestData[4]
         requestBlock = (int(ord(requestHI))<<8) + int(ord(requestLO))
         # look up the file size, and validate the block request
         #fileSize = self.getFileSize()
         fileSize = FileLength # a global from above

         # *Every* file has a last block called the runt block, and the runt block will be sized from 0 to (blockSize-1) (e.g. 0 to 511)
         # It is legal for the firmware to request the runt block, but no blocks beyond that.
         # If the firmware requests the runt block, we'll read a partial block from the file, and set the 'notAFullRead' flag in the response packet.
         runtBlock = fileSize / blockSize
         runtSize = fileSize % blockSize

         #objMsg.printMsg( "Sending Block: %d of %d"%(requestBlock+1, runtBlock) #YWL:DBG

         #if (self.ScriptEnv.DebugMode==2):
         #   objMsg.printMsg( "Sending results block: %d of %d"%(requestBlock+1, runtBlock)
         #   if (requestBlock+1 == runtBlock):
         #      objMsg.printMsg( "Sent Block: %d of %d. Waiting for Reset..."%(requestBlock+1, runtBlock)

         if requestBlock < runtBlock:
            readSize = blockSize
            notAFullRead = chr(0)
         elif requestBlock == runtBlock:
            readSize = runtSize
            notAFullRead = chr(1)
         else:
            str = "processRequest16(): Request for block %s is beyond than last block %s." % (requestBlock,runtBlock)
            ScrCmds.raiseException(11047,str)

         # read from their file
         #fileObj = self.dlfile[FILEOBJ]
         fileObj = FileObj
         fileObj.seek(requestBlock*blockSize)
         data = fileObj.read(readSize)

         returnData = requestData[0] + notAFullRead + requestLO + requestHI + data

         SendBuffer(returnData)


   def configFileObj(self, filePath):
      """
      Create self.fileObj, using the given path.  self.fileObj will be a binary file
      object opened for reading.
      """
      if os.path.exists(filePath):
         self.fileObj = open(filePath,"rb")
      else:
         ScrCmds.raiseException(11044, "Requested file %s does not exist" % filePath)

   def closeFileObj(self):
      self.fileObj.close()

   def processRequest81(self, requestData, *args, **kargs):
      """
      Yay!  More hoops to jump through!  This method can be used to intercept
      requests to read from a pcfile (Request Callback 81).  This method depends on
      self.fileObj existing.  Use the configFileObj method to set up self.fileObj
      """
      # Get the four byte BigEndian file address.
      readAddress = requestData[1:5]
      if not 4 == len(readAddress):
         ScrCmds.raiseException(11044, "Bad or Missing File Address: %s." % (`readAddress`,))
      readAddress = struct.unpack('>I',readAddress)[0]

      # Get the two byte BigEndian read count.
      readCount = requestData[5:7]
      if not 2 == len(readCount):
         ScrCmds.raiseException(11044, "Bad or Missing Read Count: %s." % (`readCount`,))
      readCount = struct.unpack('>H',readCount)[0]
      if readCount > 512:
         ScrCmds.raiseException(11044, "Read count of %s is greater than 512." % (readCount,))

      self.fileObj.seek(readAddress)
      data = self.fileObj.read(readCount) # Notice that this may read less than readCount.
      returnData = "%s\x00\x00%s" % (chr(81),data,)

      SendBuffer(returnData)

   def reportFWInfo(self, spc_id = 1):
      files = {'ALL':0xFD00}
      # Change this CWORD1 setting here!
      CWORD1 = files['ALL']
      CWORD1 = CWORD1 | 0x0080      # force display of block revision system info in test 166
      if testSwitch.FE_0313724_517205_DISPLAY_SOC_INFO:
            CWORD1 = CWORD1 | 0x0020      # force display of block revision system info in test 166
      files['ALL'] = CWORD1


      fFlag = 0

      for drFile in files.keys():
         try:
            self.St({'test_num':166,'CWORD1':files[drFile], 'timeout': 200, 'spc_id': spc_id}) #Save
         except :
            #Remove the invalid chars from the PCBA/HDA SN tables so oracle table can load
            #  upon population of these values in a later call
            try:self.dut.dblData.delTable('P166_HDA_PCBA_INFO')
            except:pass
            try:self.dut.dblData.delTable('P166_DRIVE_SERIAL_NUMBERS')
            except:pass
            objMsg.printMsg("Reporting %s revision info failed" % drFile, objMsg.CMessLvl.IMPORTANT)
            fFlag = 1

      try:


         try:
            rapInfo = self.dut.dblData.Tables('P166_RAP_REVISIONS').tableDataObj()
         except:
            rapInfo = self.dut.dblData.Tables('P166_RAP_REV').tableDataObj()

         self.dut.driveattr['RAP_REV'] = str(
         rapInfo[-1]['FORMAT_MAJOR'] + '.' +
         rapInfo[-1]['FORMAT_MINOR'] + '.' +
         rapInfo[-1]['CONTENT_MAJOR'] + '.' +
         rapInfo[-1]['CONTENT_MINOR']
                                         )

         servoInfo = self.dut.dblData.Tables('P166_SERVO_REV').tableDataObj()

         self.dut.driveattr['SERVO_INFO'] = str(
         servoInfo[-1]['CODE_MAJOR'] + '.' +
         servoInfo[-1]['CODE_MINOR'] + '_' +
         servoInfo[-1]['SAP_MAJOR'] + '.' +
         servoInfo[-1]['SAP_MINOR']
                                               )

         preampInfo = self.dut.dblData.Tables('P166_PREAMP_INFO').tableDataObj()

         if testSwitch.FE_0132082_231166_UPLOAD_PREAMP_REV:
            self.dut.driveattr['PREAMP_INFO'] = '_'.join((
               preampInfo[-1]['PREAMP_MFGR'],
               preampInfo[-1]['PREAMP_ID'],
               preampInfo[-1]['PREAMP_REV']
               ))
         else:
            self.dut.driveattr['PREAMP_INFO'] = str(
            preampInfo[-1]['PREAMP_MFGR'] + '_' +
            preampInfo[-1]['PREAMP_ID']
                                                   )
      except:
         objMsg.printMsg("Not all code versions received.\nException: %s" % traceback.format_exc(), objMsg.CMessLvl.IMPORTANT)

      try:
         try:
            hdaInfo = self.dut.dblData.Tables('P166_DRIVE_SERIAL_NUMBERS').tableDataObj()
            self.dut.driveattr['HDA_INFO'] = str(
               hdaInfo[-1]['HDA_SN'] + '_' +
               hdaInfo[-1]['PCBA_SN']
                                                   )
         except:
            hdaInfo = self.dut.dblData.Tables('P166_HDA_PCBA_INFO').tableDataObj()
            self.dut.driveattr['HDA_INFO'] = str(
               hdaInfo[-1]['HDA_SERIAL_NUM'] + '_' +
               hdaInfo[-1]['PCBA_SERIAL_NUM']
                                                   )

      except:
         pass

      from Channel import CChannelAccess
      ochan = CChannelAccess()

      ochan.setChannelType()
      ochan.setSOCType()

      if fFlag == 1:
         objPwrCtrl.powerCycle(5000,12000,10,10)

   def __setDutAttrs__(self):
      infoRef   = self.dut.dblData.Tables('P172_DRIVE_INFO')
      driveInfo = infoRef.tableDataObj()
      mxCyls    = self.dut.dblData.Tables('P172_MAX_CYL_VBAR').tableDataObj()

      try:
         self.dut.imaxHead = int(driveInfo[-1]['MAX_HEAD'])
         if testSwitch.FE_0169171_231166_MC_PART_B_SEP_TBL_PARSE:
            try:
               self.dut.numMCZones =  int(driveInfo[-1]['NUM_MEDIA_CACHE_ZONES'])
            except (KeyError, TypeError):
               self.dut.numMCZones = 0
         else:
            self.dut.numMCZones = 0
         self.dut.numZones = int(driveInfo[-1]['NUM_USER_ZONES']) - self.dut.numMCZones
         self.dut.systemZoneNum = self.dut.numZones + self.dut.numMCZones
      except:
         objMsg.printMsg("traceback: %s" % (traceback.format_exc(),))
         raise

      self.dut.maxTrack = []

      negIndex = len(mxCyls) - self.dut.imaxHead
      for iHead in range(self.dut.imaxHead):
         try:
            self.dut.maxTrack.append(int(mxCyls[iHead + negIndex]['MAX_CYL_DEC']))
         except ValueError:   # Hex value in decimal field
            self.dut.maxTrack.append(int(mxCyls[iHead + negIndex]['MAX_CYL_DEC'], 16))

      self.findSysAreaClosestDataZone()

      if DEBUG > 0:
         objMsg.printMsg("numZones: %s, sysZone: %s, nummcZones: %s" % (self.dut.numZones, self.dut.systemZoneNum, self.dut.numMCZones))
         objMsg.printMsg("MaxTrack:%s \t\nZoneTable:%s" % (self.dut.maxTrack,self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()))
         objMsg.printMsg("User-System Map: %s" % str(self.dut.systemAreaUserZones))

   def getWedgeTable(self, spc_id = 1):
      ## Retrieve the wedge info table from drive
      self.St({'test_num':172,'prm_name':'Retrieve Wedge Table Info','CWORD1':0x0038, 'spc_id':spc_id, 'timeout': 1000, })

   def getKFCI(self, spc_id = 1):
      self.St(TP.PRM_DISPLAY_ZONED_SERVO_RADIUS_KFCI_172, {'spc_id': spc_id})

   def getZoneTable(self, newTable = 0, delTables = 0, supressOutput = 1, spc_id = 1, prm_name = 'Retrieve Zone Table Info'):
      if self.dut.HDSTR_RECORD_ACTIVE == 'Y':
         objMsg.printMsg("SKIPPING getZoneTable( ) call due to HDSTR testing...")
         return
      supressOutput = 0
      try:
         if newTable == 0:
            if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
               objMsg.printMsg("Retrieving Zone Table information in quiet mode.", objMsg.CMessLvl.VERBOSEDEBUG)
            self.__setDutAttrs__()

      except:
         #objMsg.printMsg(traceback.format_exc())
         newTable = 1
         supressOutput = 0
         spc_id = 1

      if newTable:

         if delTables:
            def __safeDelete(tblName):
               try:
                  self.dut.dblData.Table(tblName).deleteIndexRecords( confirmDelete = 1)
                  self.dut.dblData.delTable(tblName)
               except:
                  pass
            for tableName in [TP.zone_table['table_name'], 'P172_DRIVE_INFORMATION', 'P172_MAX_CYL', 'P172_MAX_CYL_VBAR']:
               __safeDelete(tableName)
         self.getZnTblInfo(spc_id, supressOutput, prm_name)
         self.getMaxCylVbar(spc_id, supressOutput)

         self.__setDutAttrs__()

   def getAFHWorkingAdaptives( self, spc_id = -1, rowsToReturn = 16, supressOutput = ST_SUPPRESS__NONE, retrieveData = False, cword1 = 4 ):
      '''Display AFH working adaptives.  If FE_0255966_357263_T172_AFH_SUMMARY_TBL is enabled, use new table that allows
         for subset of data to be returned
      '''

      prm = {
         'test_num'          : 172,
         'prm_name'          : 'display_AFH_working_adapts_172',
         'timeout'           : 1800,
         'CWORD1'            : cword1,     #outputs P172_AFH_DH_WORKING_ADAPT
         'spc_id'            : spc_id,
         'stSuppressResults' : supressOutput
         }

      if cword1 == 4 and testSwitch.extern.FE_0255966_357263_T172_AFH_SUMMARY_TBL == 1:
         prm.update( {
            'CWORD1'    : 52,     #outputs P172_AFH_ADAPTS_SUMMARY
            'C_ARRAY1'  : [ rowsToReturn, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
            })

      if retrieveData:
         if prm['CWORD1'] == 52 and testSwitch.extern.FE_0255966_357263_T172_AFH_SUMMARY_TBL == 1:
            tableName = 'P172_AFH_ADAPTS_SUMMARY'
         elif testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
            tableName = 'P172_AFH_DH_WORKING_ADAPT'
         else:
            tableName = 'P172_AFH_WORKING_ADAPTS'

         prm.update( {'DblTablesToParse': [tableName]} )

      self.St( prm )

      data = []
      if retrieveData:
         #CM LOAD impact!!  Only use if absolutely needed!
         data = dbLogUtilities.DBLogReader(objDut, tableName, suppressed = True).getTableObj()

      return data

   def getAFHTargetClearances( self, spc_id = 1, supressOutput = ST_SUPPRESS__NONE, retrieveData = False ):
      '''Display AFH target clearances.  If FE_0255966_357263_T172_AFH_SUMMARY_TBL is enabled, use new table with
         reduced rows / columns.  Options provided to suppress output and retrieve the data (via ISO parse method).
         These options can be used in conjuntion with each other.

         NOTE:  retrieving data has CM Load impact and should only be used when necessary.
         NOTE:  get_clearances method in VBAR.py parses this data.  If another method needs to do the same, that method
                should be centralized into this file.
      '''
      prm = {
         'test_num'          : 172,
         'prm_name'          : 'display_AFH_target_clearance_172',
         'timeout'           : 1800,
         'CWORD1'            : 5,       #outputs P172_AFH_DH_CLEARANCE
         'spc_id'            : spc_id,
         'stSuppressResults' : supressOutput
         }

      if testSwitch.extern.FE_0255966_357263_T172_AFH_SUMMARY_TBL == 1:
         prm['CWORD1'] = 53            #outputs P172_AFH_TARGET_CLR

      if retrieveData:
         if testSwitch.extern.FE_0255966_357263_T172_AFH_SUMMARY_TBL == 1:
            tableName = 'P172_AFH_TARGET_CLEARANCE'
         elif testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT:
            tableName = 'P172_AFH_DH_CLEARANCE'
         else:
            tableName = 'P172_AFH_CLEARANCE'

         prm.update( {'DblTablesToParse': [tableName]} )

      self.St( prm )

      data = []
      if retrieveData:
         #CM LOAD impact!!  Only use if absolutely needed!
         data = dbLogUtilities.DBLogReader(objDut, tableName, suppressed = True).getTableObj()

      return data

   def getZnTblInfo(self, spc_id = 1, supressOutput = 1, prm_name = 'Retrieve Zone Table Info'):

      self.St({'test_num':172, 'prm_name':prm_name, 'CWORD1':TP.zone_table['cword1'], 'spc_id':spc_id, 'stSuppressResults': supressOutput,'timeout': 300, })

   def getMaxCylVbar(self, spc_id = 1, supressOutput = 1):
      self.St({'test_num':172,'prm_name':'Retrieve MaxCyl','CWORD1':0x0006, 'spc_id':spc_id, 'stSuppressResults': supressOutput,'timeout': 300, })

   def getWritePowers(self, spc_id = 1, supressOutput = 1):
      try:self.dut.dblData.delTable('P172_WRITE_POWERS')
      except:pass
      self.St({'test_num':172,'prm_name':"Retrieve WP's",'CWORD1':12, 'timeout':300, 'spc_id':spc_id, 'stSuppressResults': supressOutput})

   def findSysAreaClosestDataZone(self, head = None):
      """
      Find the closest user zone to the system area
         * If the system area is directly between 2 zones the lowest zone is returned

      @param head: Head to return the closest user zone for. If empty all heads are searched
      @return: Dictionary of heads and their system area's associated closest user zones.
      """
      resZoneTbl = self.dut.dblData.Tables(TP.zone_table['resvd_table_name']).tableDataObj()
      userZoneTbl = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()

      if head == None:
         heads = range(self.dut.imaxHead)
      else:
         if type(head) in [types.ListType,types.TupleType]:
            heads = head
         else:
            heads = (head,)

      for head in heads:
         systemZoneLoc = -1
         Index  = self.dth.getFirstRowIndexFromTable_byHead(resZoneTbl, head)
         sysAreaStart = int(resZoneTbl[Index]['ZN_START_CYL'])
         sysAreaEnd = sysAreaStart + int(resZoneTbl[Index]['TRK_NUM'])  - 1
         while Index+1< len(resZoneTbl) and int(resZoneTbl[Index+1]['HD_LGC_PSN']) == head:
            sysAreaEnd += int(resZoneTbl[Index+1]['TRK_NUM'])
            Index += 1

         for zone in range(self.dut.numZones):
            Index  = self.dth.getFirstRowIndexFromTable_byZone(userZoneTbl, head, zone)
            zoneStart = int(userZoneTbl[Index]['ZN_START_CYL'])
            zoneEnd = zoneStart + int(userZoneTbl[Index]['TRK_NUM'])  - 1
            while Index+1< len(userZoneTbl) and int(userZoneTbl[Index]['ZN']) == int(userZoneTbl[Index+1]['ZN']):
               zoneEnd += int(userZoneTbl[Index+1]['TRK_NUM'])
               Index += 1
            # If the system area is located inside this zone then add this zone
            if sysAreaStart >= zoneEnd:
               systemZoneLoc = zone

            # Exit if we've now passed the system area track map
            if sysAreaEnd <= zoneStart:
               if systemZoneLoc < 0:
                  systemZoneLoc = zone
               break

         # Now there should have a user zone associated with the head index
         self.dut.systemAreaUserZones[head] = systemZoneLoc

      return self.dut.systemAreaUserZones

   def trackToZone(self, iHead, track):
      ZONE_NOT_FOUND = -65535
      # return a zone for a given track location or -65535 for not finding any valid zone.
      if testSwitch.virtualRun == 1:
         zone = 0   # occassionally in VE we seek to a track not in the zone table.  Suppress this error
      else:
         zone = ZONE_NOT_FOUND # raise this error in a real process run
      zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
      ztlen = int(zt[len(zt)-1]['ZN']) - self.dut.numMCZones

      # -------------->  Error trapping to deal with common Failure modes for this section of code <-------------
      if (self.dut.numZones-1 != ztlen ):
         objMsg.printMsg("self.dut.numZones  : %s, int(zt[len(zt)-1]['ZN']): %s " % (self.dut.numZones, int(zt[len(zt)-1]['ZN'])))
         ScrCmds.raiseException(11200, "Drive failed for number of zones mismatch between zone table and self.dut.numZones")

      try:
         numHeads1 = int(zt[len(zt)-1]['HD_LGC_PSN']) + 1
      except:
         objMsg.printMsg('Please check the column heading referring to head number in P172_ZONE_TBL', objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg('If head number is not names HD_LGC_PSN then please update this in the DbLogAlias.py', objMsg.CMessLvl.IMPORTANT)
         ScrCmds.raiseException(10389, "Failed to find column name HD_LGC_PSN")

      znList = []

      for iZone in range(self.dut.numZones):
         Index  = self.dth.getFirstRowIndexFromTable_byZone(zt, iHead, iZone)
         startCyl = int(zt[Index]['ZN_START_CYL'])
         znList.append((iZone, startCyl))

      sys_zt = self.dut.dblData.Tables(TP.zone_table['resvd_table_name']).tableDataObj()

      Index  = self.dth.getFirstRowIndexFromTable_byHead(sys_zt, iHead)

      prevZone = -1
      while Index < len(sys_zt):
         if int(sys_zt[Index]['ZN']) == prevZone:
            Index+=1
            continue
         sysZoneStartTrack = int(sys_zt[Index]['ZN_START_CYL'])
         sysZone = int(sys_zt[Index]['ZN'])
         znList.append((sysZone, sysZoneStartTrack))
         prevZone = sysZone
         Index+=1

      znList = sorted(znList, key=operator.itemgetter(1))
      for ii in range(0, len(znList)):
         if track >= znList[ii][1]:
            zone = znList[ii][0]

      if DEBUG == 1:
         objMsg.printMsg("trackToZone/ Hd: %s, track: %s gave zone: %s" % (iHead, track, zone))

      #  -----------------------------------
      if zone != ZONE_NOT_FOUND:
         return zone
      else:
         objMsg.printMsg("trackToZone/ No zone found for Hd: %s, track: %s" % (iHead, track))
         objMsg.printMsg("trackToZone/ znList: %s" % (znList))

         for i in range(0, len(zt)):
            objMsg.printMsg("trackToZone/ zt[%s]  %s" % (i, zt[i]))
         for i in range(0, len(sys_zt)):
            objMsg.printMsg("trackToZone/ zt[%s]  %s" % (i, sys_zt[i]))
            ScrCmds.raiseException(11044, "trackToZone function failed.")
         self.getZoneTable(supressOutput = 0)



   def saveRCStoETF(self):
      """
      Save the RAP, CAP, SAP to the ETF.
      """
      files = {'SAP': 0x0410, 'RAP': 0x0210, 'CAP': 0x0110}
      self.RCS_PC_Base(files)

   def recoverRCSfromETF(self, updateFlash = False):
      """
      Save the RAP, CAP, SAP to the ETF.
      """
      files = {'SAP': 0x0402, 'RAP': 0x0202, 'CAP': 0x0102}
      if updateFlash:
         for key,val in files.items():
            files[key] = val | 0x20
      self.RCS_PC_Base(files)

   def saveRCStoPCFile(self):
      """
      Save the RAP, CAP, SAP to the PC.
         Data is transferred to the cm's PCFILE directory. From the drive.
      """
      files = {'SAP': 0x0408, 'RAP': 0x0208, 'CAP': 0x0108}
      self.RCS_PC_Base(files)

   def recovRCSfromPCFile(self):
      """
      Recover the RAP, CAP, SAP from the PC.
         Data is transferred to the hard drive from the PCFILE directory.
      """
      files = {'SAP': 0x0401, 'RAP': 0x0201, 'CAP': 0x0101}
      self.RCS_PC_Base(files)


   def RCS_PC_Base(self, files):
      for drFile in files.keys():
         try:
            self.St({'test_num':178,
                     'prm_name':'RCS_CMD',
                     'CWORD1':files[drFile],
                     'timeout' : 1000,
                     'spc_id': 1}
                     )

            #RCS recover leaves drive in invalid spin state.
            self.St({'test_num':1,
                    'prm_name':'spinupPrm_1',
                    'timeout':100,
                    "CWORD1" : (0x1,),
                    "MAX_START_TIME" : (200,),
                    "DELAY_TIME" : (50,),})
         except :
            objMsg.printMsg("RCS %s transfer failed" % drFile, objMsg.CMessLvl.IMPORTANT)


   def disableRVFF(self,inPrm,timeout):
      overPrm = TP.disableRVFF[self.dut.partNum[0:3]]
      #ScrCmds.objMsg.printMsg(overPrm)
      self.St(178,self.oUtility.overRidePrm(inPrm,overPrm),timeout=timeout)

   def mctPcbaSN(self):
      """
      Return the pcba serial number in MCT format
      """
      attrSN = DriveAttributes.get('PCBA_SERIAL_NUM', '1234567890')
      return self.oUtility.convertStrToBinaryWords(attrSN)

   def mctPcbaPartNum(self):
      """
      Return the pcba Part Number in MCT format
      """
      attrPN = DriveAttributes.get('PCBA_PART_NUM', '1234567890')

      import struct
      fillVal ='%10s' % attrPN
      fillVal = fillVal.zfill(10)
      return struct.unpack("5H", fillVal)

   def setFamilyInfo(self,familyInfo, famUpdate, depopMask = [], runDepop = 0, forceHdCount=0):
      """
      Set the required test 178 parameters in the RAP, CAP, SAP such as SN, family ID, hd_count
      @param familyInfo: dictionary w/ HD_COUNT, FAM_ID, PFM_ID etc as defined in test 178 documentation.
      @param famUpdate: Core parameter for this 178 call containing test name and timeout, spcid
      """
      # Get the familyInfo dictionary for the current PN
      try:
         if testSwitch.WA_0247335_348085_WATERFALL_WITH_10_DIGITS_PARTNUMBER:
            myFamilyInfo = familyInfo[self.dut.partNum[0:10]]
         else:
            if self.dut.partNum in familyInfo:
               myFamilyInfo = familyInfo[self.dut.partNum] # use full part num if exist
            else:
               myFamilyInfo = familyInfo[self.dut.partNum[0:6]] # otherwise, use the first 6-digit
      except:
         myFamilyInfo = familyInfo[self.dut.partNum[0:3]]

      if ConfigVars[CN].get('MEG_3H_SP', 0):
         #Fixup to the 3 head info... substitute the pull for sata or sas pn designator
         myFamilyInfo = familyInfo['9ZM%s73' % (self.dut.partNum[3],)]

      # Recover head count, either from VBAR or the default in the familyInfo structure
      if forceHdCount:
         hdCount = forceHdCount
      else:
         hdCount = myFamilyInfo['HD_COUNT'][0]

      if not testSwitch.TEST_86_DEPOP_SUPPORT:
         # Actually depop the heads if requested
         if len(depopMask) > 0 and runDepop:
            if testSwitch.FE_0151714_208705_IGNORE_HEAD_COUNT_FROM_DEPOP:
               self.depopHeads(depopMask)
            else:
               hdCount = self.depopHeads(depopMask)

      # Update dut for new head count
      objMsg.printMsg("Updating head count to %d" % hdCount)
      self.dut.driveattr['NUM_HEADS'] = hdCount
      self.dut.imaxHead = hdCount

      # Update the drive
      self.St({'test_num':178,'prm_name':'SAP_SN','MAX_HEAD':hdCount-1,'SAP_HDA_SN': (),'CWORD1':0x420})
      self.St({'test_num':178,'prm_name':'CAP_SN','CAP_HDA_SN': (),'CWORD1':0x120})
      self.St({'test_num':178,'prm_name':'PCBA_SN','CAP_PCBA_SN':self.mctPcbaSN(),'CWORD1':0x120})

      if testSwitch.FE_0136008_426568_WRITE_PCBA_PART_NUM_CAP  == 1:
         objMsg.printMsg("Writing PCBA Part Number")
         pcbaValue = self.mctPcbaPartNum()
         for index in range(0,len(pcbaValue)):
            data = pcbaValue[index]
            offset = index+12
            self.St({'test_num':178, 'prm_name':'PCBA_PART_NUM','CWORD1':0x120,'CAP_WORD':(offset,data,0xFFFF)})

      self.St({'test_num':178,'prm_name':'RAP_SN','RAP_HDA_SN': (),'CWORD1':0x220, 'timeout': 1000})


      if (( not testSwitch.FE_0114584_007955_DISABLE_WRITE_WWN_IN_SETFAMILYINFO ) and (ConfigVars[CN].get('SKIP_WWN',0) == 0) and ( not CommitServices.isTierPN( self.dut.partNum ) )) or testSwitch.forceNewWWN:
         if testSwitch.FE_0123752_405392_WRITE_WWN_ENHANCEMENT:
            dummyPNs = getattr(TP,'dummyPNs',[])            # 6 digits dummy PNs for development
            partnum = self.dut.driveattr['PART_NUM'][0:6]   # 6 digits part number

            if partnum in dummyPNs:
               objMsg.printMsg("Dummy partnum 6 digits %s, skipping setWWN()" %partnum)
            else:
               # Set WWN if required
               owwn = WriteWWN()
               owwn.setWWN()
         else:
            # Set WWN if required
            owwn = WriteWWN()
            owwn.setWWN()

      # Update the drive's family info
      params = famUpdate.copy()

      # Update with familyInfo defaults
      params.update(myFamilyInfo)

      # Update with the new head count
      params['HD_COUNT'] = hdCount

      # Update the PFM_ID
      if testSwitch.customerConfigInCAP:
         params.update({'PFM_ID':TP.Servo_Sn_Prefix_Matrix[self.dut.serialnum[1:3]]['PFM_ID']})
         objMsg.printMsg("PFM_ID updated to : %s based on serial number prefix entry" % str(params['PFM_ID']))

      if not testSwitch.FE_0176468_231166_P_REMOVE_PFM_ID_PF3_WRITE:
         objMsg.printMsg("Writing Common Servo PFM_ID Field")
         PFM_ID = TP.Servo_Sn_Prefix_Matrix[self.dut.serialnum[1:3]]['PFM_ID']
         #Byte 316:317 in the CAP store the common servo pfm_id location for ES/PS
         # since 178 uses word offsets the byte offset/2 = word offset... 158 starting byte
         if type(PFM_ID) in [types.TupleType, types.ListType]:
            PFM_ID = PFM_ID[0]
         PFM_ID = struct.unpack('>H', struct.pack('<H',  PFM_ID))[0]
         self.St({'test_num':178, 'prm_name':'Common Servo PFM_ID','CWORD1':0x120,'CAP_WORD':(158,PFM_ID,0xFFFF)})

      files = {'CAP': 0x0120}#, 'SAP':0x0420}
      if testSwitch.extern.FE_0124036_231166_ADD_SET_CAP_VALID_OPTION:
         cword4 = params.get('CWORD4', 0)
         if type(cword4) in (list, tuple):
            cword4 = cword4[0]
         cword4 |= 0x8
         params['CWORD4'] = cword4

      for drFile in files.keys():
         params.update({'CWORD1': files[drFile]})
         self.St(params)

      # Actually depop the heads if requested
      if testSwitch.TEST_86_DEPOP_SUPPORT and len(depopMask) > 0 and runDepop:
         hdCount = self.depopHeads(depopMask, staticDepop = True)

      #change partnumber
      if testSwitch.Depop_On_The_Fly:
         from PIF import nibletTable
         if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
            from WTF_Tools import CWTF_Tools
            oWaterfall = CWTF_Tools()
         else:
            from base_SerialTest import CWaterfallTest
            oWaterfall = CWaterfallTest(self.dut,{})

         partnum = oWaterfall.searchPN(self.dut.partNum)
         if self.dut.Waterfall_Req == "NONE":
            keyCounter = 0
         else:
            keyCounter = nibletTable[partnum]['Depop'].index(self.dut.Waterfall_Req + 'L' + self.dut.Niblet_Level)
         # oWaterfall.updateATTR(partnum, keyCounter)
         oWaterfall.buildClusterList(updateWTF = 1)

   def depopHeads(self, depopMask, staticDepop = True):
      """
      Issue 178 depop heads command.
      @param depopMask: List of physical heads to depop
      @param staticDepop:  Static depop or Depop on the fly?
      """
      # if not self.dut.objData.get('T86_FINISHED', False):
      if testSwitch.virtualRun and not testSwitch.WTFunitTest:
         self.dut.Depop_Done = 'NONE'
         return self.dut.imaxHead

      numPhysHds = self.dut.Servo_Sn_Prefix_Matrix[self.dut.serialnum[1:3]]['PhysHds']
      if max(depopMask) > numPhysHds -1 or len(depopMask) >= numPhysHds:
         ScrCmds.raiseException(11044, "Depop head # greater than physical head #.")

      # Kill the selected heads
      if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY:
         STATIC_DEPOP = 1
         DEPOP_OTF = 2
         depopPrm = {
            'test_num'     : 86,
            'prm_name'     : "Depop_Head_86",
            'CWORD1'       : DEPOP_OTF,
            'timeout'      : 6000,
            }

         if staticDepop:
            depopPrm['CWORD1'] = STATIC_DEPOP

         # Issue depop cmd
         hdCount = self.dut.imaxHead
         self.getLgcToPhysHdMap(hdCount)
         objMsg.printMsg("depopMask is %s" % depopMask)
         depopMask.sort()
         depopMask.reverse()

         for physicalHead in depopMask:
            if physicalHead in self.dut.LgcToPhysHdMap:
               # Depop the selected head
               logicalHead = self.dut.LgcToPhysHdMap.index(physicalHead)
               depopPrm['TEST_HEAD'] = logicalHead
               CProcess().St(depopPrm)

               objPwrCtrl.powerCycle(offTime=20, onTime=30, useESlip=1)
               # Only for if system zome is prepared
               if (self.dut.nextOper == 'PRE2' and self.dut.systemAreaPrepared) or (self.dut.nextOper in ['CAL2', 'FNC2']):
                  # If recover the system sector 0 (System Defect Table)
                  if (logicalHead == 0 or logicalHead == 1 ) and not staticDepop:
                     depopPrm['CWORD1'] = 0x08
                     CProcess().St(depopPrm)
                     objPwrCtrl.powerCycle(offTime=20, onTime=30, useESlip=1)

                  # If depopping head 0/1 insert guardband
                  if (logicalHead == 0 or logicalHead == 1 ) and not staticDepop and testSwitch.extern.FE_0152779_341216_DEALLOCATE_GUARD_BAND:
                     depopPrm['CWORD1'] = 0x10
                     CProcess().St(depopPrm)
                     objPwrCtrl.powerCycle(offTime=20, onTime=30, useESlip=1)

                  # If depopping head 0, rewrite the SIM files with the correct seeds
                  if (logicalHead == 0 or logicalHead == 1 ) and not staticDepop:
                     depopPrm['CWORD1'] = 0x04
                     CProcess().St(depopPrm)
                     objPwrCtrl.powerCycle(offTime=20, onTime=30, useESlip=1)



               # Reload the head count and head map
               self.getZoneTable(newTable = 1, delTables = 1)
               hdCount = self.dut.imaxHead
               self.getLgcToPhysHdMap(hdCount)
         self.dut.objData.update({'T86_FINISHED': True})
      else:
         if staticDepop:
            #  Remap the heads
            physHdList = range(numPhysHds)
            hdsEnabled = 0

            if testSwitch.FE_0159212_357260_P_USE_2601_FOR_STATIC_DEPOP:
               for hd in reversed(range(numPhysHds)):
                  if hd in depopMask:
                     objMsg.printMsg("Static Depop - Removing head: %s" %hd)
                     self.St({'test_num':11,'prm_name':'Depop','PARAM_0_4': (0x2601, hd, 0, 0, 0)})
                     physHdList.remove(hd)
            else:    # Use legacy - '2301' servo command for depop
               for hd in range(numPhysHds):
                  if hd in depopMask:
                     physHdList.remove(hd)
                  else:
                     hdsEnabled += 2**hd
               self.St({'test_num':11,'prm_name':'Depop','PARAM_0_4': (0x2301, hdsEnabled, 0, 0, 0)})

            self.saveSAPtoFLASH()
            hdCount = len(physHdList)
         else:
            ScrCmds.raiseException(11044, "Depop OTF not supported unless Test 86 support is enabled: TEST_86_DEPOP_SUPPORT")
      # else:
         # self.getZoneTable(newTable = 1, delTables = 1)
         # hdCount = self.dut.imaxHead
         # self.getLgcToPhysHdMap(hdCount)


      # Set head map and determine if depop worked
      if not testSwitch.virtualRun or testSwitch.WTFunitTest:
         self.getLgcToPhysHdMap(hdCount)
         for hd in depopMask:
            if hd in self.dut.LgcToPhysHdMap:
               objMsg.printMsg("Head %s was not depopped" %hd)
               ScrCmds.raiseException(11044, "Head remapping was unsuccessful.")


      if self.dut.Depop_Req != 'NONE': 
      # Update depop attributes
         self.dut.driveattr['DEPOP_DONE'] = 'DONE'    # This could be set to done from previous run or this current run
         self.dut.Depop_Done = 'DONE'                 # This tells us if we have depopped during this operation

      # Change partnumber
      self.dut.pn_backup = self.dut.driveattr['PART_NUM']
      from PIF import nibletTable
      if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
         from WTF_Tools import CWTF_Tools
         oWaterfall = CWTF_Tools()
      else:
         from base_SerialTest import CWaterfallTest
         oWaterfall = CWaterfallTest(self.dut,{})

      objMsg.printMsg("self.dut.partNum %s " %(str(self.dut.partNum)))
      partnum = oWaterfall.searchPN(self.dut.partNum)
      objMsg.printMsg("partnum %s " %(str(partnum)))
      for nibletkey in nibletTable[partnum]['Depop']:
         objMsg.printMsg("nibletkey %s " %(str(nibletkey)))
         if nibletkey.find('L')> -1:
            self.dut.Niblet_Level = nibletkey.split('L')[-1]
            break
      objMsg.printMsg("self.dut.Niblet_Level %s " %(str(self.dut.Niblet_Level)))
      objMsg.printMsg("self.dut.Waterfall_Req %s " %(str(self.dut.Waterfall_Req)))
      if self.dut.Niblet_Level == 'NONE':
         self.dut.Niblet_Level = '3'

      if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY == 1 and self.dut.Depop_Req != 'NONE':
         #depopReq = 'D' + `self.dut.imaxHead` + 'L' + self.dut.Niblet_Level
         # Update Waterfall Request attribute
         self.dut.Waterfall_Req = nibletkey[:2]
         keyCounter = nibletTable[partnum]['Depop'].index(nibletkey)
      elif self.dut.Waterfall_Req == "NONE":
         keyCounter = 0
      else:
         keyCounter = nibletTable[partnum]['Depop'].index(self.dut.Waterfall_Req + 'L' + self.dut.Niblet_Level)

      # oWaterfall.updateATTR(partnum, keyCounter)
      oWaterfall.buildClusterList(updateWTF = 1)

      if self.dut.Depop_Req == 'NONE':
         #Clear the local depop mask attrs
         self.dut.depopMask = []

      #Make sure PLR here doesn't kick us back into depop
      self.dut.objData.update({'depopMask':self.dut.depopMask})

      if testSwitch.FE_SGP_EN_REPORT_WTF_FAILURE and (self.dut.pn_backup != self.dut.driveattr['PART_NUM']):
         oWaterfall.WTF_Unyielded(ec=12169)

      return hdCount

   def getLgcToPhysHdMap(self, hdCount):
      """
      Read back the logical to physical head map from the SAP.  Assign the head map to DUT variable LgcToPhysHdMap
      """
      if testSwitch.virtualRun or testSwitch.WA_0141450_231166_DISABLE_LGC_PHYS_MAP_SUPP_SRVO:
         #P011_SV_RAM_RD_BY_OFFSET entries in virtual.xml are not guarenteed to have the right read_data for this function
         self.dut.LgcToPhysHdMap=range(hdCount)
         if testSwitch.BF_0156739_231166_P_FIX_NO_DEPOP_PHYS_MAP or testSwitch.WA_0141450_231166_DISABLE_LGC_PHYS_MAP_SUPP_SRVO:
            self.dut.PhysToLgcHdMap = self.getPhysToLgcHdMap()
         return

      self.St({'test_num':11,'prm_name':'Read Head Map','SYM_OFFSET': 225,'CWORD1':0x0200, 'ACCESS_TYPE': 0})
      hdData = self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()

      if hdData[-1]['READ_DATA'] == '0X0000FFFF': # depop not supported
         objMsg.printMsg("Depop feature not supported in servo code")
         self.dut.LgcToPhysHdMap = range(hdCount)
         if testSwitch.BF_0156739_231166_P_FIX_NO_DEPOP_PHYS_MAP:
            self.dut.PhysToLgcHdMap = range(hdCount)
         return

      try:
         startIndex = len(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj())
      except:
         startIndex = 0

      self.St({'test_num':11,'prm_name':'Read Head Map','SYM_OFFSET': 225,'NUM_LOCS': hdCount-1,'CWORD1':0x0200, 'ACCESS_TYPE': 1})
      hdData = self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()

      if hdData[startIndex]['READ_DATA'] == 'FF':
         objMsg.printMsg("Depop feature not supported in servo code")
         self.dut.LgcToPhysHdMap = range(hdCount)
         if testSwitch.BF_0156739_231166_P_FIX_NO_DEPOP_PHYS_MAP:
            self.dut.PhysToLgcHdMap = range(hdCount)
         return

      self.dut.LgcToPhysHdMap = []
      for row in hdData[startIndex:]:
         self.dut.LgcToPhysHdMap.append(int(row['READ_DATA'], 16))

      objMsg.printMsg("Physical Head Map = %s" % self.dut.LgcToPhysHdMap,objMsg.CMessLvl.DEBUG)
      if testSwitch.WA_0171802_395340_P_PHYSICAL_HEAD_ATTRIBUTE_UPDATE:
         self.dut.driveattr['HD_PHYS_PSN'] = self.dut.LgcToPhysHdMap
      self.dut.PhysToLgcHdMap = self.getPhysToLgcHdMap()

   def getPhysToLgcHdMap(self):
      """
      Returns the physical head index table for the logical head map retreived from servo
      """

      #Generate a list of invalid heads with length equal to the max physical head (could be > logical head table)
      # increment 1 so that the range is [0..maxhd]
      physMap = [INVALID_HD for i in range(max(self.dut.LgcToPhysHdMap)+1)]

      for index, physHd in enumerate(self.dut.LgcToPhysHdMap):
         physMap[physHd] = index

      return physMap


   def clearMDWuncal(self,inPrm,timeout=600,spc_id=0):
      overPrm = MDWuncal[self.dut.partNum[0:3]]
      #ScrCmds.objMsg.printMsg(overPrm)
      self.St(178,self.oUtility.overRidePrm(inPrm,overPrm),timeout=timeout)


   def setStateSpaceMode(self,inPrm,timeout=600,spc_id=0):
      overPrm = stateSpaceMode[self.dut.partNum[0:3]]
      #ScrCmds.objMsg.printMsg(overPrm)
      self.St(178,self.oUtility.overRidePrm(inPrm,overPrm),timeout=timeout)


   def readSymbolTable(self,fileName,printItems = 0):
      """Reads the tab delimited symbol file passed and parses the data. This function will return a tuple of dictionaries the 1st is a (symbol: offset) and second is a (offset: symbol).
      @type fileName: string
      @param fileName: Path & Name of symbol file to parse.
      @type printItems: integer
      @param printItems: Value > 0 will print out the symbols and offsets after parsed
      @ret: (SymbolKeyedDict, OffsetKeyedDict)
      """
      pat = "\[ *[0-9] *\]"
      symbol = open(fileName)
      numBlank = 0
      lSymbols = {}
      invSym = {}
      while 1:
         tempLine = symbol.readline()
         if tempLine == "":
            numBlank += 1
            if numBlank > 2:
               break
         iLine = tempLine.split("\t")
         if len(iLine)==3:
            if not iLine[0] == "":
               symName = iLine[1]
               symName = symName.replace("(","")
               symName = symName.replace(")","")
               symName = symName.replace("&","")
               symName = symName.strip()
               (symName,n) = re.subn(pat,"",symName)
               try:
                  lSymbols.update({symName:int(iLine[0])})
                  invSym.update({int(iLine[0]):symName})
               except:
                  pass
      symbol.close()
      invSym = {}
      if printItems >=1:
         for (k,v) in lSymbols.items():
            objMsg.printMsg("k=%s\tv=%s" % (k,v),objMsg.CMessLvl.DEBUG)
      return(lSymbols,invSym)


   def ftpPCFiles(self):
      """
      FTP's the pcfiles for this drive to the "Platform" ftp server set up on the host.
         *Note: User needs to set up the server on the host
         *This method uses static references to the PCFile directory and as such should be replaced by a 178 call to directly ftp the data from the drive in test.
      """
      fileList = ['rapdata','capdata','sapdata','contact']
      objMsg.printMsg("FTP'ing PCFiles to PCFile Server",objMsg.CMessLvl.DEBUG)
      for fileType in fileList:
         try:
            fileName = '%s_%s.bin' % (self.dut.serialnum, fileType)
            ftpFile = GenericResultsFile(fileName)
            ftpFile.open('wb')

            pcFile = open('/var/merlin/pcfiles/%s/%s' % (fileType,self.getFofFileName(0)),'rb')
            ftpFile.write(pcFile.read())
            pcFile.close()
            ftpFile.close()
            try:
               RequestService("SendGenericFile", ((fileName,), "Platform"))
            except:
               objMsg.printMsg("FTP of file: %s failed." % fileName, objMsg.CMessLvl.DEBUG)
         except:
            objMsg.printMsg("FTP of file: %s failed." % fileName, objMsg.CMessLvl.DEBUG)
            try:
               ftpFile.delete()
            except:
               pass

   if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE or testSwitch.FE_0155919_426568_P_FTP_CCV_FILE:
      def ftpFiles(self, files, altServerKey = "Platform", ftpSubDir = 'RestoreRecords'):
         """
             FTP's files to the "Platform"/* ftp server set up on the host.
                *Note: User needs to set up the server on the host
         """
         objMsg.printMsg("FTP'ing Files to Server",objMsg.CMessLvl.DEBUG)

         if type(files) != list:
            files = [files]

         if not testSwitch.virtualRun:
            ftpServers = RequestService('GetSiteconfigSetting','AltFtpServers')[1].get('AltFtpServers', {})

            if altServerKey not in ftpServers:
               objMsg.printMsg('Files not sent to FTP site!!.  Site Config not set up for server %s' %altServerKey)
            else:
               ftpPath = ftpServers[altServerKey]['Servers'][0] + ftpServers[altServerKey]['InitialDir']

            if ftpSubDir:
               RequestService("SetResultDir", ftpSubDir + "/") #set subdirectory to the Platform folder
               ftpPath += ftpSubDir

            objMsg.printMsg('FTPing file to %s' %ftpPath)

         try:
            for fileName in files:
               fileName = os.path.basename(fileName)
               objMsg.printMsg("FTP'ing %s" %fileName)


               method, error = RequestService("SendGenericFile", (fileName, altServerKey))

               if error:
                  objMsg.printMsg('Host Service %s - error:%s ' % (method, error))
                  objMsg.printMsg("FTP of file: %s failed." % fileName, objMsg.CMessLvl.DEBUG)
                  ScrCmds.raiseException(11044, "FTP failed")
         finally:
            if ftpSubDir:
               RequestService("SetResultDir", "")  #set subdirectory back to what it was

      def retrieveFtpFiles(self, files, altServerKey = 'Platform', ftpSubDir = 'RestoreRecords'):
         objMsg.printMsg('Retrieving file/s from FTP server')

         if type(files) != list:
            files = [files]

         objMsg.printMsg('Host version %s' %HostVersion)
         objMsg.printMsg('Host RPM 14.04-11 or greater required to retrieve file from FTP site')

         if not testSwitch.virtualRun:
            ftpServers = RequestService('GetSiteconfigSetting','AltFtpServers')[1].get('AltFtpServers', {})

            if altServerKey not in ftpServers:
               objMsg.printMsg('Files not retrieved from FTP site!!.  Site Config not set up for server %s' %altServerKey)
            else:
               ftpPath = ftpServers[altServerKey]['Servers'][0] + ftpServers[altServerKey]['InitialDir']

            if ftpSubDir:
               RequestService("SetResultDir", ftpSubDir + "/") #set subdirectory to the Platform folder
               ftpPath +=  '/' + ftpSubDir

            objMsg.printMsg('FTP retrieving file from %s' %ftpPath)

         try:
            for fileName in files:
               fileName = os.path.basename(fileName)
               objMsg.printMsg("FTP:  Retrieving %s" %fileName)

               fileObj = GenericResultsFile(fileName)
               fileObj.open('w')
               fileObj.close()

               method, error = RequestService('ReceiveGenericFile',(fileName, altServerKey))

               if error:
                  fileObj.delete()
                  objMsg.printMsg('Host Service %s - error:%s ' % (method, error))
                  objMsg.printMsg("FTP of file: %s failed." % fileName, objMsg.CMessLvl.DEBUG)
                  if error == 3:
                     objMsg.printMsg('File does not exist on FTP server', objMsg.CMessLvl.DEBUG)
                  ScrCmds.raiseException(11044, "FTP retrieval failed")
         finally:
            if ftpSubDir:
               RequestService("SetResultDir", "")  #set subdirectory back to what it was

         return True
   def processRequest21(self,requestData, *args, **kargs):
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
         fileSize =  os.stat(self.request21File.name)[stat.ST_SIZE]

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
            ScrCmds.raiseException(11047,str)

         # read from their file
         #fileObj = self.dlfile[FILEOBJ]
         #fileObj = FileObj
         self.request21File.seek(requestBlock*blockSize)
         data = self.request21File.read(readSize)

         returnData = requestData[0] + notAFullRead + requestLO + requestHI + data

         SendBuffer(returnData)

   #----------------------------------------------------------------------------
   def checkPwaSN(self):
      if testSwitch.checkSN == 1 and testSwitch.virtualRun == 0:
         if DriveAttributes.has_key("PCBA_SERIAL_NUM"):
            pwaAttr = DriveAttributes["PCBA_SERIAL_NUM"]
         else:
            ScrCmds.raiseException(10648,"DriveAttributes has no PCBA_SERIAL_NUM key")

         tableNames = [i[0] for i in self.dut.dblData.Tables()]
         if 'P166_HDA_PCBA_INFO' not in tableNames:
            self.St({'test_num':166},CWORD1=(0x0800),timeout=300)

         tableInfo = self.dut.dblData.Tables('P166_HDA_PCBA_INFO').tableDataObj()

         if tableInfo[0].has_key("PCBA_SERIAL_NUM"):
            pwaSN = tableInfo[0]["PCBA_SERIAL_NUM"]
         else:
            ScrCmds.raiseException(10648,"PCBA_SERIAL_NUM not found")

         lenPwaAttr = len(pwaAttr)
         lenPwaSN   = len(pwaSN)
         if (lenPwaAttr>lenPwaSN) or (pwaSN[(lenPwaSN-lenPwaAttr):] != pwaAttr):
            msg = "PCBA_SERIAL_NUM Mismatch - Attribute:%s  Drive:%s"%(pwaAttr,pwaSN)

            pwaSN = pwaSN.lstrip('0')  # remove leading zeros
            name,attr_of_pwa = RequestService("GetAttributes", (pwaSN,()) )   # Get FIS attrs belonging to this PCBA_NUM
            if not attr_of_pwa.has_key('HDA_SERIAL'):
               objMsg.printMsg("Fail to get Drive Serial Number from PCBA Attribute %s" %(attr_of_pwa,))
            else:
               actual_hda_sn = attr_of_pwa['HDA_SERIAL'].upper()[0:8]
               # Send Fail event to SN that was scanned by Host
               objMsg.printMsg("PCBA_SERIAL_NUM Mismatch - Attribute:%s  Drive:%s" % (pwaAttr,pwaSN))
               objMsg.printMsg("Actual HDA_SERIAL of drive:%s" % actual_hda_sn)
               ReportErrorCode(10648)
               RequestService('SendRun',(1,))                  # Report EC10648 for the scanned S/N

               objMsg.printMsg('Setting Host HDA SERIAL NUM to %s' % actual_hda_sn)
               name,data = RequestService("SetDriveSN", actual_hda_sn)       # Report EC10648 for the actual drive too

               HDASerialNumber = actual_hda_sn  # Change Host global

            ScrCmds.raiseException(10648 ,msg)
         else:
            objMsg.printMsg("PCBA_SERIAL_NUM Match - Attribute:%s  Drive:%s"%(pwaAttr,pwaSN))

   #----------------------------------------------------------------------------
   def checkHDASN(self):
      from Rim import objRimType
      import re
      if testSwitch.checkSN == 1:
         if objRimType.CPCRiser():
            self.St({'test_num':514},0x8000,0x0001,0x0080,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=80) # Serial Num
            tableInfo = self.dut.dblData.Tables('P514_MODEL_SN_FW_VER').tableDataObj()

            if tableInfo[0].has_key('HDA_SN'):
               hdaSN = tableInfo[0]['HDA_SN']
            else:
               ScrCmds.raiseException(10610,"HDA_SN not found")

         elif objRimType.IOInitRiser()  :
            self.St({'test_num':552},0x0002,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=1200) # SCSI Self Test
            tableInfo = self.dut.dblData.Tables('P552_DISPLAY_DRIVE_INFO').tableDataObj()

            if tableInfo[0].has_key('SERIAL_NUM'):
               hdaSN = tableInfo[0]['SERIAL_NUM']
            else:
               ScrCmds.raiseException(10610,"HDA_SN not found")

         lst = re.findall( '[0-9,a-z,A-Z]', hdaSN )
         if len(lst) < 8:
            objMsg.printMsg( 'DSN not valid')
            ScrCmds.raiseException(10610,"DSN not valid")
         if HDASerialNumber != hdaSN:
            objMsg.printMsg("HDA Serial Num Mismatch - HDASerialNumber:%s  Drive:%s" % (HDASerialNumber,hdaSN))
            ReportErrorCode(10610)
            RequestService('SendRun',(1,))                  # Report EC10648 for the scanned S/N

            objMsg.printMsg('Setting Host HDA SERIAL NUM to %s' % hdaSN)
            name,data = RequestService("SetDriveSN", hdaSN)       # Report EC10648 for the actual drive too
            ScrCmds.raiseException(10610,"HDA Serial Num Mismatch - HDASerialNumber:%s  Drive:%s"%(HDASerialNumber,hdaSN))
         else:
            objMsg.printMsg("HDA Serial Num Match - HDASerialNumber:%s  Drive:%s"%(HDASerialNumber,hdaSN))

   #----------------------------------------------------------------------------
   def validateDriveSN(self):
      from Rim import objRimType
      if self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.sptDiag, self.dut.sptActive.availModes.intBase] \
         and (objRimType.CPCRiser() or objRimType.IOInitRiser()):
         self.checkHDASN()
      else:
         self.checkPwaSN()

   def setMinorHealthBit(self, iHead, testNumber, errorCode, failDataString, spc_id):
      # set minor health
      # ------>  Add entry to DBLog table here to set minor health bit
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(191)
      self.dut.objSeq.curRegSPCID = 1
      self.dut.dblData.Tables('P_MINOR_FAIL_CODE').addRecord(
         {
         'HD_PHYS_PSN': self.dut.LgcToPhysHdMap[iHead],
         'ERROR_CODE':  errorCode,
         'SPC_ID': spc_id,
         'OCCURRENCE': occurrence,
         'SEQ':curSeq,
         'TEST_SEQ_EVENT': testSeqEvent,
         'HD_LGC_PSN':  iHead,
         'TEST_NUMBER': testNumber,
         'FAIL_DATA':   str(failDataString),
         })
      objMsg.printDblogBin(self.dut.dblData.Tables('P_MINOR_FAIL_CODE'))

   def getAuditTestRAPDict(self):
      """
      Audit test is a shortened test process based on an abbreviated RAP, that will still allow for interface testing.
      The RAP info is extracted from a dbLog table and stored in the drive object auditTestRAPDict, so is available for later use.
      maxLBA will need to be adjusted accordingly
      """
      if not testSwitch.virtualRun:
         CProcess().St({
            'test_num':172,
            'prm_name':'retrieve audit test tables',
            'CWORD1':28,
            'timeout': 200,
            'DblTablesToParse': ['P000_AUDIT_DRIVE_TABLE','P000_DRIVE_PBA_COUNT']
            })

         auditTestRAPTable = self.dut.objSeq.SuprsDblObject['P000_AUDIT_DRIVE_TABLE']
      else:
         auditTestRAPTable = self.dut.dblData.Tables('P000_AUDIT_DRIVE_TABLE').tableDataObj()

      localDict ={}
      for row in auditTestRAPTable:
         localDict.setdefault(int(row['HD_LGC_PSN']),[])
         head = int(row['HD_LGC_PSN'])
         localDict[head].append(((int(row['START_TRK'])),(int(row['END_TRK']))))
      self.dut.auditTestRAPDict = localDict # update the dut obj

      if not testSwitch.virtualRun:
         self.dut.numPBAs = int(self.dut.objSeq.SuprsDblObject['P000_DRIVE_PBA_COUNT'][-1]['DRIVE_NUM_PBAS'])
      #objMsg.printMsg("AUDIT TEST: here is the dict: %s"% (localDict.items()),objMsg.CMessLvl.IMPORTANT)# blm for debug

   #----------------------------------------------------------------------------
   def setParamCD(self,paramFileNameDict):
      ''' Register unique param_cd.h to CM based on operation.
         Declare following in TestParameters.py
         paramFileNameDict = {
            'st_param_cd.h' : ['PRE2','CAL2','FNC2'],
            'io_param_cd.h' : ['FIN2','CUT2']
         }
         Function called in Setup.initializeComponents()'''

      for paramFileName, operList in paramFileNameDict.items():
         if self.dut.nextOper in operList:
            objMsg.printMsg('Register %s to CM' % paramFileName)
            break
      else:
         objMsg.printMsg('Unique param File not found for %s use param_cd.h' % self.dut.nextOper)
         return

      configName,fileName = (CN,paramFileName)
      paramFileLoc =  os.path.join(ParamFilePath, configName, fileName)

      if not os.path.isfile(paramFileLoc):
         ScrCmds.raiseException(10326,'Missing param file %s' % fileName)

      fileObj = open(paramFileLoc,'r')
      paramCodeLines = fileObj.readlines()
      fileObj.close()

      tempParmXRef = {}
      parmXRef = {}
      for line in paramCodeLines:
         split = line.split()
         if len(split) >= 3:  # The line from the C header file should contain at least: #define ITEM value
            define,name,value = split[:3]
            if define == "#define":  # the first item in the line shall be "#define"
               if name.find("_PARM_") > 0:  # second parm must contain "_PARM_"
                  key,item = name.split("_PARM_")  # key is the name the user will put into their parm files
                  if item in ["C",'P']:        # item must be in ["C","P"] (code,parmCount,fileFlag)
                     value = int(value)
                     # get the entry for this key and add in the new attribute
                     attributes = tempParmXRef.get(key,{})
                     attributes[item] = value
                     # save back the new/updated attribute list
                     tempParmXRef[key] = attributes

      for k,v in tempParmXRef.items():
         parmXRef[k] = (v['C'],v['P'])
      if testSwitch.UPS_PARAMETERS:

         upsObj.RegisterParamsDictionary(parmXRef)
      else:
         try:
            RegisterParamsDictionary(parmXRef)
         except:
            objMsg.printMsg('CM Service RegisterParamsDictionary is available in RPM 14.3-0 or higher')

   #----------------------------------------------------------------------------
   def validateThermistorValue(self,min,max):

      self.St(TP.prm_172_HDA_temp)
      curTemp = DriveVars['Drive_Temperature_Deg_C']
      reqTemp, minTemp, maxTemp = TP.temp_profile[self.dut.nextOper]
      objMsg.printMsg("Drive Temp %d, req Temp is %d" % (curTemp, reqTemp))
      if curTemp<reqTemp-min or curTemp>reqTemp+max:
         ScrCmds.raiseException(14798, "Thermistor Failure" )


class CBinAsciiFileIO(CFSO):
   """
   Class to read a file from pcfiles folder on CM, and convert binary to hex or ascii chars.
   """
   def __init__(self, pcFileName):
      """
      @param prm186: T186 input to measure and return head mr resistances
      @param deltaLim: Integer. Absolute value of maximum allowed MR resistance change
      """
      CFSO.__init__(self)
      self.genResName = pcFileName

      self.binaryPath = os.path.join(ScrCmds.getSystemPCPath(), pcFileName, self.getFofFileName(0))
      self.genericBinPath = os.path.join(ScrCmds.getSystemResultsPath(), self.getFofFileName(0), self.genResName)

   def readBin2Hex(self, offsetBytes=0, bytesToRead=0):
      """Reads in binary data from file, converts to hex"""
      self.configFileObj(self.binaryPath)  #opens, creates self.fileObj

      self.fileObj.seek(offsetBytes)
      binData = self.fileObj.read(bytesToRead)
      self.closeFileObj()

      return binascii.hexlify(binData)

   def readBin2Chars(self, offsetBytes=0, bytesToRead=0):
      """Reads in binary data, converts to hex, returns ascii chars"""
      return self.oUtility.strBufferToBinString(self.readBin2Hex(offsetBytes,bytesToRead))


class CbinAP_IO:
   """
   Class to do IO to/from RAP in binary on CM. Saves CM memory, and a little test time.
   Use these methods to read/write contiguous bytes, words, longs.
   """

   def __init__(self,fileName):
      self.oFSO = CFSO()

      #Set up folder,file names and paths
      self.thisFileName = str(fileName).upper()
      if self.thisFileName == 'RAP':
         self.ctrlWordRead = 0x0208
         self.ctrlWordWrite = 0x0221

      self.pcFolderName = self.thisFileName.lower()+'data'  #e.g. rapdata,sapdata,capdata
      self.genResName = 'binary'+self.thisFileName
      self.pcFilePath = os.path.join(ScrCmds.getSystemPCPath(), self.pcFolderName, self.oFSO.getFofFileName(0))
      self.cmResultsPath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.genResName)

   def dutToCM(self):
      """
      Read RAP from dut, write to pcfiles folder on CM, then to results folder.
      """
      self.oFSO.RCS_PC_Base({self.thisFileName: self.ctrlWordRead})  #Save xAP to pcfiles folder on CM

      #Read in contents of binary RAP, write to alternate location
      genFile = GenericResultsFile(self.genResName)
      genFile.open('wb')
      pcFile = open(self.pcFilePath,'rb')
      genFile.write(pcFile.read())
      pcFile.close()
      genFile.close()

   def readFromRAP(self, fmtType='word', startByte=0, valsToRead=0):
      """
      Read and translate binary data from RAP, based on supplied arguments.

      @type fmtType: String
      @param fmtType: Size of values to read - byte, word, long.
      @type startByte: Integer
      @param startByte: Location in RAP in bytes to start read
      @type valsToRead: Integer
      @param valsToRead: Number of bytes,words,longs to read

      @return inData: List of numbers read from RAP
      """

      structFmt = '%dH' %valsToRead  #Default to word
      numBytes = valsToRead * 2
      if fmtType.lower() == 'byte':
         structFmt='%dB' %valsToRead
         numBytes = valsToRead
      elif fmtType.lower() == 'long':
         structFmt='%dL' %valsToRead
         numBytes = valsToRead * 4

      inFile = open(self.cmResultsPath,'rb')
      inFile.seek(startByte)

      import struct
      inData = list(struct.unpack(structFmt,inFile.read(numBytes)))
      inFile.close()

      return inData

   def writeToRAP(self, fmtType='word', startByte=0, inData=[]):
      """
      Take list of data, translate to binary, and write to RAP.

      @type fmtType: String
      @param fmtType: Size of values to read - byte, word, long.
      @type startByte: Integer
      @param startByte: Location in RAP in bytes to start read
      @type inData: List or Scalar
      @param inData: List of numbers to write into RAP
      """
      if type(inData) != types.ListType:
         inData = [inData]

      structFmt = '%dH' %len(inData)  #Default to word
      if fmtType.lower() == 'byte':
         structFmt='%dB' %len(inData)
      elif fmtType.lower() == 'long':
         structFmt='%dL' %len(inData)

      outFile = GenericResultsFile(self.genResName)
      outFile.open('r+b')  #open file for updating
      outFile.seek(startByte)

      import struct
      outFile.write(struct.pack(structFmt,*(x for x in inData)))

      outFile.close()

   def FlashRAP(self):
      """
      Send RAP from results folder on CM into FLASH on dut
      """
      self.oFSO.configFileObj(self.cmResultsPath)  # create the file object for processRequest81
      RegisterResultsCallback(self.oFSO.processRequest81, 81, 0) # Re-direct 81 calls

      self.oFSO.RCS_PC_Base({self.thisFileName: self.ctrlWordWrite}) #Transfer xAP from results folder on CM to FLASH

      RegisterResultsCallback('', 81,) # Resume normal 81 calls

#-------------------------------------------------------------------------------
class Overlay_Handler:
   """
   Class for opening file pointers and managing overlay file requests (70) from self test.
   """

   def __init__(self, dut):

      # Set ourselves to not be valid support for overlays until we pass our initialization
      self.valid = False
      self.dut = dut
      self.overlayServiceTime = 0
      self.overlayFilePath = ""
      self.overlayFileObj = None
      self.overlayFileSize = 0
      self.overlayFileName = ''

      self.checkForOverlayKey()

   def checkForOverlayKey(self,overlayKey='S_OVL', overrideMap = False):

      if not overrideMap:
         overlayKey = getattr(TP,'overlayMap',overlayKey)

      try:
         self.overlayFileName =PackageDispatcher(self.dut, overlayKey).getFileName()
         self.valid = True
      except:
         self.valid = False

      if self.overlayFileName in ['',None] or self.valid == False:
         self.overlayFileName = False
         self.valid = False
         if not testSwitch.FE_0167407_357260_P_SUPPRESS_OVERLAY_FILE_INFO:
            objMsg.printMsg("Overlays not supported in config as %s file couldn't be located in config."%overlayKey, objMsg.CMessLvl.IMPORTANT)
      else:
         # Initialze the handler's objects
         try:
            self.init_handler()
            self.valid = True
         except:
            self.valid = False
            if not testSwitch.FE_0167407_357260_P_SUPPRESS_OVERLAY_FILE_INFO:
               objMsg.printMsg("Overlays not supported in config as %s file couldn't be located in config."%overlayKey, objMsg.CMessLvl.IMPORTANT)

   #----------------------------------------------------------------------------
   def downloadOverlay(self,overlayFileName):
      self.overlayFileName = overlayFileName
      try:
         self.overlayFileObj.close()
      except:
         #Might already be closed
         pass
      try:
         self.init_handler()
      except:
         objMsg.printMsg("ERROR - Overlay not loaded.", objMsg.CMessLvl.IMPORTANT)

   #----------------------------------------------------------------------------
   def init_handler(self):
      #Initialze the instance variables and open the overlay file for reading.
      overlayFilePath = os.path.join(ScrCmds.getSystemDnldPath(), self.overlayFileName)
      self.overlayFileObj = open(overlayFilePath,'rb')
      self.overlayFileSize = os.stat(overlayFilePath)[6]

      if not testSwitch.FE_0167407_357260_P_SUPPRESS_OVERLAY_FILE_INFO:
         if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
            objMsg.printMsg( "Overlay File %s loaded."%(self.overlayFileName))
      if DEBUG > 0:
         objMsg.printMsg( "FileName: %s of len %s"%(self.overlayFilePath,  self.overlayFileSize))#,objMsg.CMessLvl.DEBUG) #YWL:DBG

      # Ready to service overlay requests so register the callback with the CM
      RegisterResultsCallback(self.processOverlayRequest,[70,71],0)

   def __del__(self):

      try:
         self.overlayFileObj.close()
      except:
         #Might already be closed
         pass

   def addOverlayDblog(self):
      testNum = 8
      curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(testNum)
      self.dut.objSeq.curRegSPCID = 1

      memVals = objMsg.getMemVals()
      cpuElapsedTime = objMsg.getCpuEt()

      self.dut.dblData.Tables('TEST_TIME_BY_TEST').addRecord(
         {
         'SPC_ID': 1,
         'OCCURRENCE': occurrence,  # This mismatch needs to be addressed all over the code because the generating code is incorrect TODO
         'SEQ':curSeq,
         'TEST_SEQ_EVENT': testSeqEvent,
         'TEST_NUMBER': testNum,
         'ELAPSED_TIME': self.overlayServiceTime,
         'PARAMETER_NAME':"Overlay service time",
         'TEST_STATUS':0,
         'CELL_TEMP':"%0.1f" % (ReportTemperature()/10.0),
         'SZ': memVals.get('VSZ',''),
         'RSS': memVals.get('RSS',''),
         'CPU_ET': '%.2f' % cpuElapsedTime,
         })

   #----------------------------------------------------------------------------
   def processOverlayRequest(self,requestData,currentTemp,drive5,drive12,collectParametric):
      """
      Results Callback for Block 70-> download file to drive
      requestData is a string from the UUT asking for a block from a file
      return a frame, raise an exception on error
      """
      requestKey = ord(requestData[0])
      # code 70 requests a block of data from the overlay download file;
      if requestKey in [70,71]:
         startTime = time.time()
         blockSize = (int(ord(requestData[3]))<<8) + int(ord(requestData[2]))
         requestHI = requestData[5]
         requestLO = requestData[4]
         requestBlock = (int(ord(requestHI))<<8) + int(ord(requestLO))
         # look up the file size, and validate the block request

         # *Every* file has a last block called the runt block, and the runt block will be sized from 0 to (blockSize-1) (e.g. 0 to 511)
         # It is legal for the firmware to request the runt block, but no blocks beyond that.
         # If the firmware requests the runt block, we'll read a partial block from the file, and set the 'notAFullRead' flag in the response packet.
         runtBlock = self.overlayFileSize / blockSize
         runtSize = self.overlayFileSize % blockSize

         if DEBUG > 0:
            objMsg.printMsg( "Overlay Request: Sending Block: %d of %d"%(requestBlock+1, runtBlock))#,objMsg.CMessLvl.DEBUG) #YWL:DBG


         if requestBlock < runtBlock:
            readSize = blockSize
            notAFullRead = chr(0)
         elif requestBlock == runtBlock:
            readSize = runtSize
            notAFullRead = chr(1)
         else:
            str = "processOverlayRequest(): Request for block %s is beyond than last block %s." % (requestBlock,runtBlock)
            ScrCmds.raiseException(11047,str)

         self.overlayFileObj.seek(requestBlock*blockSize)
         data = self.overlayFileObj.read(readSize)

         returnData = requestData[0] + notAFullRead + requestLO + requestHI + data

         SendBuffer(returnData)
         self.overlayServiceTime += (time.time()-startTime)

#-------------------------------------------
class WorldWideName(CProcess):
   """
   WWN Managing Class
   Will implement WWN interfacing to host and CM for SAS, SATA, FC
   """
   FUNC_CALL = "GetWWN"
   #----Initialize--------------#
   def __init__( self ):
      self.WWN = ''
      CProcess.__init__(self)
   #-------------------------


   #-----------------------------------------------------------
   # Function id() returns WWN ID read from words 108:111 for
   # WWN read back purposes
   #-----------------------------------------------------------
   def id(self, data):
      """
      Function id() returns WWN ID read from words 108:111 for
      WWN read back purposes
      """
      self.str          =   str(data)
      self.drive_wwn    =   ''
      for i in xrange(0,len(self.str),2):
         s1 = "%02X%02X" % (ord(self.str[i + 1]), ord(self.str[i]))
         self.drive_wwn += s1
      return self.drive_wwn

   #-----------------------------------------------------------
   # Function verify() - compares the decoded WWN data from
   # word 108:111 to the drive attribute 'WW_SATA_ID'
   #-----------------------------------------------------------
   def verify(self, wwn64):
      """
      Function verify() - compares the decoded WWN data from
      word 108:111 to the drive attribute 'WW_SATA_ID'
      """
      objMsg.printMsg("******* WWN Readback Verification *******")

      self.dut      = objDut                           # get drive sata_id attrib
      self.sata_id  = self.dut.driveattr['WW_SATA_ID']
      self.wwn64    = self.validateWWN(wwn64)                     # validate WWN format

      if self.wwn64 == self.sata_id:
         objMsg.printMsg("******* WWN Readback Verification PASSED *******")
      else:
         msg = '******* WWN Readback Verification FAILED!!! *******\n'
         msg += ' ' * 22 + 'Expected SATA_ID : %s \n' %self.sata_id
         msg += ' ' * 22 + 'Readback SATA_ID : %s' %self.wwn64
         objMsg.printMsg(msg)
         ScrCmds.raiseException(10016, "Proc Operator-XX/3F91 WWN Mismatch")


   def validateWWN( self, WWN='' ):
      msg = "Checked WWN: %s ,for "%WWN
      if len( WWN ) == 16:
         msg += "Length of 16 Chars" + '- PASS'
      else:
         msg += "Length of 16 Chars %d - FAIL"%(len(WWN))
         ScrCmds.raiseException(12411,{'MSG':'Invalid WWN Len ' + msg,
                                            'WWN_LEN':len(WWN),
                                            'WWN':WWN})

      if WWN[0] == '5':
         msg += "First Character '5' - PASS"
      else:
         msg += "First Character '5' - %s - FAIL"%WWN[0]
         ScrCmds.raiseException(12411,{'MSG':'WWN Header Check Failed ' + msg,
                                       'WWN_LEN':len(WWN),
                                       'WWN':WWN})

      lst = re.findall( '[^0-9-A-F]', WWN )
      if not len( lst ):
         msg += "HEX values - PASS"
      else:
         msg += "HEX values - %s - FAIL"%`lst`
         ScrCmds.raiseException(12411,{'MSG':'RE Hex Content failed ' + msg,
                                       'WWN_LEN':len(WWN),
                                       'WWN':WWN})
      objMsg.printMsg(msg, objMsg.CMessLvl.IMPORTANT)
      return WWN
   #-------------------------
   def getWWN( self, Partnumber='',DriveSN='',retry=4 ):
      if testSwitch.winFOF == 1:
         self.WWN = "ABCDEF12"
         return self.WWN

      while retry >= 0:
         try:
            self.WWN = self.getWorldWideName( Partnumber, DriveSN )
            self.WWN = self.validateWWN(self.WWN)
         except:
            objMsg.printMsg("getWWN: Retries left %s..." % retry)
            retry -= 1
            time.sleep(30)       # Give it a little rest in case FIS having difficulties
         else:
            break
      else:
         if testSwitch.FE_0125501_357915_PRINT_WWN_FAILURE_INFO:
            objMsg.printMsg("getWWN failed. See the 'WWN - Architecture, Overview and Troubleshooting' page at wiki.seagate.com for further help")
         ScrCmds.raiseException(12411,{'MSG':'WWN Retries Exceeded ',
                                       'WWN_LEN':len(self.WWN),
                                       'WWN':self.WWN})
      return self.WWN
   #-------------------------
   def getWorldWideName( self, Partnumber='', DriveSN='' ):
      """
      Gets the unique WWN data from the WWN server
      """
      if not testSwitch.forceDummyPartNumWWN == '':
         Partnumber = testSwitch.forceDummyPartNumWWN
      wwn = RequestService("DCMServerRequest", ('GetSATA_WWNumber',(str(Partnumber), str(DriveSN))))
      wwn = ('GetWWN', wwn[1]['DATA'])
      if type( wwn ) == types.DictType or \
      wwn[1].find( "FAILCODE" ) != -1 or \
      wwn[1].find( "Error" ) != -1:
         if testSwitch.FE_0125501_357915_PRINT_WWN_FAILURE_INFO:
            objMsg.printMsg("WWN Failure: %s: %s" % (wwn[0], wwn[1])) # Output WWN failure information returned by Gemini (first entry in return tuple is function, second entry is the failure info)
         self.WWN = "NONE"
         ScrCmds.raiseException(12411,{'MSG':'WWN Host Req. Failed ',
                                       'WWN_LEN':len(wwn),
                                       'WWN':wwn})
      else:
         self.WWN  = wwn[1]

      return self.WWN

#-------------------------------------------
class WriteWWN( WorldWideName ):
   WWN_TYPE = 1
   AttrName = ''
   def __init__(self, forceSetWWN = False):
      WorldWideName.__init__( self )
      self.dut = objDut

      self.AttrName = ''
      for (drvIntf,drvIntfList) in TP.WWN_INF_TYPE.items():
         if self.dut.drvIntf in drvIntfList:
            if (forceSetWWN or testSwitch.ALL_DRIVES_GET_WWN) and (ConfigVars[CN].get('SKIP_WWN',0) == 0):
               self.AttrName = drvIntf
            break
      else:
         if testSwitch.FE_0127531_231166_USE_EXPLICIT_INTF_TYPE:
            # no intf type found but force was set for WWN
            if (forceSetWWN or testSwitch.ALL_DRIVES_GET_WWN) and (ConfigVars[CN].get('SKIP_WWN',0) == 0):
               self.AttrName = drvIntf

      ScrCmds.trcBanner("Setting drive World Wide Name %s"% self.AttrName)

   def setWWN( self ):
      if CommitServices.isTierPN( self.dut.partNum ) and not testSwitch.forceNewWWN:
         objMsg.printMsg("Bypassing set WWN for tier PN.")
      else:
         if self.AttrName == '':
            objMsg.printMsg("WWN not enabled for this interface %s; Modify testparam: WWN_INF_TYPE" % self.dut.drvIntf , objMsg.CMessLvl.IMPORTANT)
            return
         elif self.dut.driveattr.get(self.AttrName,'NONE') == 'NONE' or testSwitch.forceNewWWN == 1:
            if not testSwitch.virtualRun:
               self.WWN = self.getWWN(self.dut.partNum, self.dut.serialnum)
###########################################################################################
#CHOOI-25Sep15 OffSpec - Activate WWN with Teleplan WWN ID
               objMsg.printMsg("1. Original WWN: %s" % self.WWN , objMsg.CMessLvl.IMPORTANT)
               self.WWN = self.WWN[0:1] + '001F83' + self.WWN[7:]
               objMsg.printMsg("1. New WWN: %s" % self.WWN , objMsg.CMessLvl.IMPORTANT)
###########################################################################################
               status = self.WWN #RegisterDriveWWN(self.WWN)
               self.dut.driveattr[self.AttrName] = self.WWN
               objMsg.printMsg('setWWN %s %s %s' % (self.AttrName,self.WWN,status), objMsg.CMessLvl.IMPORTANT)
            else:
               ScrCmds.trcBanner('virtual run mode, skipping getWWN()')
         elif  self.dut.driveattr.get(self.AttrName,'NONE') != 'NONE':
            self.WWN = self.dut.driveattr.get(self.AttrName,'NONE')
###########################################################################################
#CHOOI-25Sep15 OffSpec - Activate WWN with Teleplan WWN ID
            objMsg.printMsg("2. Original WWN: %s" % self.WWN , objMsg.CMessLvl.IMPORTANT)
            self.WWN = self.WWN[0:1] + '001F83' + self.WWN[7:]
            objMsg.printMsg("2. New WWN: %s" % self.WWN , objMsg.CMessLvl.IMPORTANT)
            self.dut.driveattr[self.AttrName] = self.WWN
###########################################################################################
            if not testSwitch.virtualRun:
               status = self.WWN #RegisterDriveWWN(self.WWN)
               objMsg.printMsg('setWWN %s %s %s' % (self.AttrName,self.WWN,status), objMsg.CMessLvl.IMPORTANT)
            else:
               ScrCmds.trcBanner('virtual run mode, skipping RegisterDriveWWN()')

         self.writeCAPWWN()


   def writeCAPWWN( self):
      """
      Writes WWN to the drive using test 178 or spt command.
      """
      if testSwitch.FE_0114521_007955_WRITE_WWN_USING_F3_DIAG:
         if ( not CommitServices.isTierPN( self.dut.partNum ) ):
            if self.dut.sptActive.getMode() in [self.dut.sptActive.availModes.sptDiag, self.dut.sptActive.availModes.intBase]:
               # if drive has interface code use J cmd to write WWN
               oSerial = serialScreen.sptDiagCmds()

               if testSwitch.FE_0198029_231166_P_WWN_BEG_AND_END:
                  objPwrCtrl.powerCycle(5000,12000,10,30)
                  sptCmds.enableDiags()
                  wwnNodeName = oSerial.getCapValue(6)
                  if self.WWN not in wwnNodeName.replace(' ', '') or testSwitch.virtualRun:

                     oSerial.setCAPValue("NODE_NAME_VALIDATION_KEY",1,saveToFlash = False)

                     if testSwitch.virtualRun and self.WWN == '':
                        self.WWN = '5000C500026000EE'
                     oSerial.setCAPValue("NODE_NAME",int(self.WWN,16),saveToFlash = True)
                  else:
                     objMsg.printMsg("WWN already written to CAP.")
               else:
                  sptCmds.enableDiags()
                  oSerial.setCAPValue("NODE_NAME_VALIDATION_KEY",1,saveToFlash = False)

                  if testSwitch.virtualRun and self.WWN == '':
                     self.WWN = '5000C500026000EE'
                  oSerial.setCAPValue("NODE_NAME",int(self.WWN,16),saveToFlash = True)

               objPwrCtrl.powerCycle(5000,12000,10,30)
            else:
               self.St({'test_num'  :178,
                        'prm_name'  :'Set CAP WWN-178',
                        'CWORD1'    :0x0020,
                        'WWN'       :(),}
                      )
      else:
         self.St({'test_num'  :178,
                  'prm_name'  :'Set CAP WWN-178',
                  'CWORD1'    :0x0020,
                  'WWN'       :(),}
                )


   def setSerialIntfWWN( self, WWN):
      WWN = eval('0x' + WWN)
      self.St({'test_num'  :178,
               'prm_name'  :'Set SATA/SAS WWN-178',
               'CWORD1'    :0x0020,
               'WWN_USER'       :self.oUtility.ReturnTestCylWord(WWN),}
             )


class dataTableHelper:
   def __init__(self):
      pass

   def getRowFromTable(self, tbl, iHead, iZone, zoneFieldName = 'ZN', headFieldName = 'HD_LGC_PSN'):
      try:    startIndex = len(tbl) - ( (int(tbl[len(tbl) - 1][zoneFieldName]) + 1) * (int(tbl[len(tbl) - 1][headFieldName]) + 1) )
      except:
         if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
              physicalHead = int(tbl[len(tbl) - 1]['HD_PHYS_PSN'])
              logicalHead = objDut.PhysToLgcHdMap[physicalHead]
              startIndex = len(tbl) - ( (int(tbl[len(tbl) - 1][zoneFieldName]) + 1) * (logicalHead                           + 1) )
         else:
              startIndex = len(tbl) - ( (int(tbl[len(tbl) - 1][zoneFieldName]) + 1) * (int(tbl[len(tbl) - 1]['HD_PHYS_PSN']) + 1) )
      Index = startIndex + ((int(tbl[len(tbl) - 1][zoneFieldName]) + 1) * iHead) + iZone

      try:    tbl[Index]
      except: objMsg.printMsg("getRowFromTable/ Index into table Failed! Hd: %s, zn: %s, tbl[-1]: %s" % (iHead, iZone, tbl[-1]))
      return tbl[Index]

   def getFirstRowIndexFromTable_byHead(self, tbl, iHead, headFieldName = 'HD_LGC_PSN'):
      try:
         Index = len(tbl) -1
         while int(tbl[Index][headFieldName]) != iHead : Index-=1 #ignore unwanted headnum
         while Index>=0 and int(tbl[Index][headFieldName]) == iHead : Index-=1 #search through till first row
         return Index+1 #found
      except: objMsg.printMsg("getFirstRowIndexFromTable_byHead Failed! Hd: %s, tbl[-1]: %s" % (iHead, tbl[-1]))
      #should not come here
      raise Exception, "getFirstRowIndexFromTable_byHead Failed! Hd: %s, zn: %s, tbl[-1]: %s" % (iHead, iZone, tbl[-1])

   def getFirstRowIndexFromTable_byZone(self, tbl, iHead, iZone, zoneFieldName = 'ZN', headFieldName = 'HD_LGC_PSN'):
      try:
         Index = self.getFirstRowIndexFromTable_byHead( tbl, iHead, headFieldName)
         lenoftbl = len(tbl)
         while Index < lenoftbl:
            if int(tbl[Index][zoneFieldName]) == iZone:
               return Index
            Index += 1
      except: objMsg.printMsg("getFirstRowOfZoneFromTable/ Index into table Failed! Hd: %s, zn: %s, tbl[-1]: %s" % (iHead, iZone, tbl[-1]))
      #should not come here
      raise Exception, "getFirstRowOfZoneFromTable2/ Index into table Failed! Hd: %s, zn: %s, tbl[-1]: %s" % (iHead, iZone, tbl[-1])

   def getRowFromTable_byHead(self, tbl, iHead):
      try:     startIndex = len(tbl) - (int(tbl[len(tbl) - 1]['HD_LGC_PSN']) + 1)
      except:
         if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
               physicalHead = int(tbl[len(tbl) - 1]['HD_PHYS_PSN'])
               logicalHead = objDut.PhysToLgcHdMap[physicalHead]
               startIndex = len(tbl) - (logicalHead                           + 1)
         else:
               startIndex = len(tbl) - (int(tbl[len(tbl) - 1]['HD_PHYS_PSN']) + 1)
      Index = startIndex + iHead

      try:    tbl[Index]
      except: objMsg.printMsg("getRowFromTable_byHead/ Index into table Failed! Hd: %s, tbl[-1]: %s" % (iHead, tbl[-1]))
      return tbl[Index]

   def getRowFromTable_byTable(self, tbl):
      startIndex = len(tbl) - 1
      Index = startIndex + 0

      try:    tbl[Index]
      except: objMsg.printMsg("getRowFromTable_byTable/ Index into table Failed! tbl: %s" % str(tbl))
      return tbl[Index]

#---------------------------------------------------------------------------------------------------------#
