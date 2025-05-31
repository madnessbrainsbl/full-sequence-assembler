#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/08 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PackageResolution.py $
# $Revision: #7 $
# $DateTime: 2016/11/08 01:38:34 $
# $Author: gang.c.wang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PackageResolution.py#7 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import re, ScrCmds, os, traceback, types, string
import MessageHandler as objMsg
from TestParamExtractor import TP
import Utility

DEBUG = 0

"""
   Each attribute is a package family which is associated from codeType keys
"""

if testSwitch.FE_0141300_231166_P_ADD_SUPPORT_FOR_STPA:
   packageFamilies = {
         'STP'  :  ['CFW', 'IMG','TPM','IMG_BIN',
                     'TXT_TPM', 'CAP', 'S_OVL', 'S_FLG','CFW_BIN'],
         'STPA' :  ['CFW2','IMG2', 'TPM2','IMG_BIN2',
                     'TXT_TPM2', 'CAP2', 'S_OVL2', 'S_FLG2'],
         'STPB' :  ['CFW3','IMG3','TPM3','IMG_BIN3',
                     'TXT_TPM3', 'CAP3', 'S_OVL3', 'S_FLG3'],
         'STPSC' : ['CFW4','IMG4', 'TPM4','IMG_BIN4',
                   'TXT_TPM4', 'CAP4', 'S_OVL4', 'S_FLG4'],            
         'RSSP' : ['RAP', 'BPI','BPI_TDK','BPI_RHO','RAPT','RAPT_TDK','RAPT_RHO','RAPA','RAPL', 'SIG'],
         'SFWP' : ['SFW','CMB','CMZ','SAP','LOF','RPS','COE','SVO_PRM','SVO_BIN','CTLR_BIN','SSCORE'],
         'SFWA' : ['SFW2','CMB2'],
         'SFWSC' : ['SFW3','CMB3','CMZ3','SAP3','LOF3','RPS3','COE3','SVO_PRM3','SVO_BIN3','CTLR_BIN3'],
         'SFWSCR': ['SFW4','CMB4','CMZ4','SAP4','LOF4','RPS4','COE4','SVO_PRM4','SVO_BIN4','CTLR_BIN4'],
         'TGTP' : ['TGT','OVL','CGN','SFWI','FLG','CXM'],
         'TGTA' : ['TGT2', 'OVL2', 'SFWI2','FLG2'],
         'TGTB' : ['TGT3', 'OVL3', 'ALL3', 'SFWI3','FLG3'],
         'TGTC' : ['TGT4', 'OVL4', 'SFWI4','FLG4'],
         'INCP' : ['INC', 'INC_BIN', 'IO_OVL'],
#CHOOI-18May17 OffSpec
         'TGTO' : ['TGT5'],
      }
else:
   packageFamilies = {
         'STP'  :  ['CFW', 'CFW_1','IMG','CFW_2','CFW_3','CFW_4','CFW_5','CFW_6','TPM','IMG_BIN',
                     'TXT_TPM', 'CAP', 'S_OVL', 'S_FLG','CFW_BIN'],
         'STPA' :  ['CFW2','IMG2', 'TPM2','IMG_BIN2',
                     'TXT_TPM2', 'CAP2', 'S_OVL2', 'S_FLG2'],
         'STPB' :  ['CFW3','IMG3','TPM3','IMG_BIN3',
                     'TXT_TPM3', 'CAP3', 'S_OVL3', 'S_FLG3'],
         'STPSC' : ['CFW4','IMG4', 'TPM4','IMG_BIN4',
                   'TXT_TPM4', 'CAP4', 'S_OVL4', 'S_FLG4'], 
         'RSSP' : ['RAP', 'BPI','BPI_TDK','BPI_RHO','RAPT','RAPT_TDK','RAPT_RHO','RAPA','RAPL', 'SIG'],
         'SFWP' : ['SFW','CMB','CMZ','SAP','LOF','RPS','COE','SVO_PRM','SVO_BIN','CTLR_BIN','SSCORE'],
         'SFWA' : ['SFW2','CMB2'],
         'SFWSC': ['SFW3','CMB3','CMZ3','SAP3','LOF3','RPS3','COE3','SVO_PRM3','SVO_BIN3','CTLR_BIN3'],
         'SFWSCR': ['SFW4','CMB4','CMZ4','SAP4','LOF4','RPS4','COE4','SVO_PRM4','SVO_BIN4','CTLR_BIN4'],
         'TGTP' : ['TGT','OVL','CGN','SFWI','FLG','CXM','TGTB','OVLB','IV'],
         'TGTA' : ['TGT2', 'OVL2', 'SFWI2','FLG2'],
         'TGTB' : ['TGT3', 'OVL3', 'ALL3', 'SFWI3','FLG3', 'IV3'],
         'TGTC': ['TGT4', 'OVL4', 'SFWI4', 'FLG4'],
         'INCP' : ['INC', 'INC_BIN', 'IO_OVL'],
#CHOOI-18May17 OffSpec
         'TGTO' : ['TGT5'],
      }

if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
   packageFamilies['RSSP'].append( 'SIG' )

if testSwitch.FE_0334158_379676_P_RFWD_FFV_1_POINT_5:
   packageFamilies['TGTP'].append('SIGS')
   packageFamilies['TGTP'].append('RFWD15_TPM')

flagLookup = {
   'STP' :  'S_FLG',
   'TGTP' : 'FLG',
   'TGTA' : 'FLG2',
   'TGTB' : 'FLG3',
   'TGTC' : 'FLG4',
   'TGTO' : 'FLG5',  #CHOOI-18May17 OffSpec
}

if testSwitch.FE_0141300_231166_P_ADD_SUPPORT_FOR_STPA:
   flagLookup['STPA'] = 'S_FLG2'

if testSwitch.FE_0124012_231166_ALLOW_PF3_UNLK_CODE_ACCESS:
   UNLK_KEY = 'UNLK'
   if testSwitch.FE_0135186_357552_UNLOCK_BY_BUILD_TARGET:
      UNLK_NAME = getattr(TP,'unlockFileName', 'unlock_m.lod')
   else:
      UNLK_NAME = 'unlock_m.lod'

#Update package families with program specific values
packageFamilies.update(getattr(TP,'packageFamilies',{}))
SIC_BASE_TXT_TPM_NAME = getattr(TP,'SICBaseTxtTpmName', 'TXT_TPM_2.TXT')
SIC_BASE_BIN_NAME =  getattr(TP,'SICBaseBinName', 'SI2_2.bin')
HDALESS_TXT_NAME = getattr(TP,'HDALessTxtName', 'RY_Hybrid_SpecialTPM.txt')
HDALESS_BIN_NAME = getattr(TP,'HDALessBinName', 'RY_Hybrid_Headerless.BIN')

subListSupport = []
for key in packageFamilies:
   if key[:3] in ['TGT', 'SFW', 'STP'] and len(key) > 3 and not key[3] == 'P':
      subListSupport.extend(packageFamilies[key])
      subListSupport.append(key)
      if DEBUG > 0: objMsg.printMsg("subListSupport: %s" % subListSupport)

class basePackage:
   """
   Base package handler- provides simple package functionality and resolution
   """
   def __init__(self, dut, codeType):
      self.dut = dut
      self.codeType = codeType
      self.flagFileName = None
      self.packageName = None

      if DEBUG > 0:
         objMsg.printMsg("codes: %s" % str(self.dut.codes))
      self.getDLFiles()

   def getDLFiles(self):
      self.dlFiles = os.listdir(ScrCmds.getSystemDnldPath())

   def setFlagFileName(self):
      """
      Sets the flag file name to be used to set dynamic switches
      """

      if self.packageName in flagLookup:
         flagKey = flagLookup[self.packageName]
         if self.dut.codes.has_key(flagKey):
            fileName = self.searchDir(ScrCmds.getSystemDnldPath(),self.dut.codes[flagKey])
            objMsg.printMsg("Using %s from Codes.py" % (fileName,))
         elif self.manifest.has_key(flagKey):
            fileName = self.searchDir(ScrCmds.getSystemDnldPath(),self.manifest[flagKey])
            if not (testSwitch.FE_0167407_357260_P_SUPPRESS_OVERLAY_FILE_INFO and flagKey in ['IO_OVL']):
               if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
                  objMsg.printMsg("Using %s from %s" % (fileName,self.manifestName))
         elif (not testSwitch.FE_0141300_231166_P_ADD_SUPPORT_FOR_STPA) and (self.packageName[0:3] == 'TGT' and self.manifest.has_key(flagKey[0:3])):
            fileName = self.searchDir(ScrCmds.getSystemDnldPath(),self.manifest[flagKey[0:3]])
            if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
               objMsg.printMsg("Using %s from %s" % (fileName,self.manifestName))
         elif testSwitch.FE_0141300_231166_P_ADD_SUPPORT_FOR_STPA and self.packageName in subListSupport and self.manifest.has_key(flagKey[0:3]):
            fileName = self.searchDir(ScrCmds.getSystemDnldPath(),self.manifest[flagKey[0:3]])
            if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
               objMsg.printMsg("Using %s from %s" % (fileName,self.manifestName))
         elif testSwitch.FE_0141300_231166_P_ADD_SUPPORT_FOR_STPA and flagKey in subListSupport and flagKey[0:3] == 'S_F' and self.manifest.has_key(flagKey[0:5]):
            fileName = self.searchDir(ScrCmds.getSystemDnldPath(),self.manifest[flagKey[0:5]])
            if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
               objMsg.printMsg("Using %s from %s" % (fileName,self.manifestName))
         else:
            objMsg.printMsg('WARNING: Can not locate external flag file for key %s in %s' % (flagKey, ScrCmds.getSystemDnldPath()), objMsg.CMessLvl.IMPORTANT)
            fileName = None

         if fileName:
            self.flagFileName = fileName

   def getFileName(self):
      """
      Code Resolution Priority
      1. If code available in dut.codes then return that
      2. Look for manifest if exists then search for matching code-type
      4. If no resolution return nothing
      """
      self.loadManifest()

      if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
         objMsg.printMsg("codeType %s " % (self.codeType))

      if not self.codeType in ['TGTB', 'OVLB'] :
         if self.codeType in subListSupport:
            if not self.dut.codes.has_key(self.codeType):
               self.codeType = self.codeType[0:-1]
         if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
            objMsg.printMsg("using sublist support ")
      else:
         objMsg.printMsg("not using sublist support ")
      
      if self.dut.codes.has_key(self.codeType) and not self.codeType in ['TGTB', 'OVLB']:
         objMsg.printMsg("Using Codes.py for translation.")
         if type(self.dut.codes[self.codeType]) in  [types.ListType, types.TupleType]:
            fileNameList = []
            for fileName in self.dut.codes[self.codeType]:
               fileNameList.append(self.searchDir(ScrCmds.getSystemDnldPath(),fileName))
            return fileNameList
         else:
            fileName = self.searchDir(ScrCmds.getSystemDnldPath(),self.dut.codes[self.codeType])
      elif self.manifest.has_key(self.codeType):
         fileName = self.searchDir(ScrCmds.getSystemDnldPath(),self.manifest[self.codeType])
         if not (testSwitch.FE_0167407_357260_P_SUPPRESS_OVERLAY_FILE_INFO and self.codeType in ['IO_OVL']):
            if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG:
               objMsg.printMsg("Using %s from %s" % (fileName,self.manifestName))
      elif testSwitch.FE_0124012_231166_ALLOW_PF3_UNLK_CODE_ACCESS and self.codeType == UNLK_KEY:
         fileName = self.searchDir( ScrCmds.getSystemDnldPath(), UNLK_NAME)
         objMsg.printMsg("Using %s from static UNLK_NAME" % (fileName,))
      elif self.codeType == 'INC_TPM':
         fileName = self.searchDir( ScrCmds.getSystemDnldPath(), SIC_BASE_TXT_TPM_NAME)
         objMsg.printMsg("Using %s from static SIC_BASE_TXT_TPM_NAME" % (fileName,)) 
      elif self.codeType == 'INC_BIN':
         fileName = self.searchDir( ScrCmds.getSystemDnldPath(), SIC_BASE_BIN_NAME)
         objMsg.printMsg("Using %s from static SIC_BASE_BIN_NAME" % (fileName,))      
      elif self.codeType == 'HDALESS_TPM':
         fileName = self.searchDir( ScrCmds.getSystemDnldPath(), HDALESS_TXT_NAME)
         objMsg.printMsg("Using %s from static HDALESS_TXT_NAME" % (fileName,))
      elif self.codeType == 'HDALESS_BIN':
         fileName = self.searchDir( ScrCmds.getSystemDnldPath(), HDALESS_BIN_NAME)
         objMsg.printMsg("Using %s from static HDALESS_BIN_NAME" % (fileName,))
      else:
         if not (testSwitch.FE_0167407_357260_P_SUPPRESS_OVERLAY_FILE_INFO and self.codeType in ['IO_OVL']):
            objMsg.printMsg('WARNING: Skipped download of %s since not specified in Codes.py!!' % (self.codeType,), objMsg.CMessLvl.IMPORTANT)
         fileName = None

      if fileName:
         self.setFlagFileName()
      return fileName

   def searchDir(self, path, fname):
      if os.path.exists(path):
         dirList = os.listdir(path)
         lowCaseDir = [s.lower() for s in dirList]
         try:
            retVal = dirList[lowCaseDir.index(fname.lower())]
         except:
            if testSwitch.winFOF == 1:
               retVal = ''
            else:
               raise
         return retVal
      else:
         raise Exception("File not found")

   def getManifestName(self):
      retVal = ''
      for packageName, values in packageFamilies.items():
         if DEBUG > 0:
            objMsg.printMsg("Looking for %s in %s:%s" % (self.codeType, packageName, str(values)))

         if (self.codeType in values) or (not testSwitch.GET_MANIFEST_FILE_BASED_ON_CODETYPE_ONLY and self.codeType == packageName):
            retVal = self.dut.codes.get(packageName, '')
            break

      self.packageName = packageName

      zipMultiPat = '(%s)(\.[zipZIP]{3})'
      mftMultiPat = '(%s)(\.[mftMFT]{3})'

      match = re.search(zipMultiPat % '\S*',retVal)
      retVal = ''
      if not match == None:
         baseFile = match.group(1)
         for fileName in self.dlFiles:
            if DEBUG:
               objMsg.printMsg("%s ?= %s" % (baseFile, fileName))
            if fileName.find(baseFile) > -1:
               mat2 = re.search(mftMultiPat % baseFile, fileName)
               if not mat2 == None:
                  retVal = fileName
                  break
      self.manifestName = retVal
      return retVal

   def loadManifest(self, manifestName = None):
      self.manifest = {}
      if manifestName == None:
         manifestName = self.getManifestName()
      try:
         if not manifestName == '':
            manifestPath = os.path.join(ScrCmds.getSystemDnldPath(), manifestName)
            if DEBUG > 0:
               objMsg.printMsg("Loading manifest %s" % manifestPath)
            maniData = open(manifestPath, 'r').read()
            outStr = ''
            for i in maniData.splitlines():
               outStr += i
            self.manifest = eval(outStr)
            
            
            if DEBUG > 0:
               objMsg.printMsg("Found manifest name: %s, %s" % (manifestName, self.manifest))
            
##Workaround to make one zip file for dual RAP system
            if testSwitch.AGC_SCRN_DESTROKE_WITH_NEW_RAP and self.dut.driveattr['DESTROKE_REQ'] == 'DSD_NEW_RAP': 
                if  self.manifest.has_key('BPI_DSD') and self.manifest.has_key('RAPT_DSD'):
                    for key in self.manifest:
                        if re.search('(.bin)$',self.manifest[key],re.I):
                            self.manifest[key] = self.manifest['BPI_DSD']
                        elif re.search('(.lod)$',self.manifest[key],re.I):
                            self.manifest[key] = self.manifest['RAPT_DSD']
                

      except:
         objMsg.printMsg(traceback.format_exc())

   def getReleaseServoPrefix(self):
      releasedPrefix = ''

      # Read in the translation matrix
      releasedPrefix = self.dut.Servo_Sn_Prefix_Matrix.get(self.dut.serialnum[1:3], '')
      if type(releasedPrefix) == types.DictType:
         releasedPrefix= releasedPrefix.get('ServoCode','')  #maintain backwards compatibility with this dictionary

      if DEBUG > 0:
         objMsg.printMsg("Looking for SN prefix %s in %s" % (self.dut.serialnum[1:3],self.dut.Servo_Sn_Prefix_Matrix))
      # Report if we didn't find it
      if releasedPrefix == '':
         objMsg.printMsg("Released SN Prefix not found")

      return releasedPrefix

class servo_Package(basePackage):
   def __init__(self, dut, codeType, manifestKey = None):
      basePackage.__init__(self,dut,codeType)
      if testSwitch.FE_0156514_357260_P_SERVO_FILES_IN_MANIFEST:
         self.releasePackage_template = '\S*?(?P<fname>%s)\S*?(?P<fsuff>sfw|SFW|cmb|CMB|cmz|CMZ|sap|SAP|lof|LOF|rps|RPS|coe|COE|svo_bin|SVO_BIN)?\.[zipZIPlodLODbinBIN]{3}'
      else:
         self.releasePackage_template = '(?P<fhead>\S+?)?_?(?P<fname>%s[0-9a-fA-F]{0,4})_?(?P<fsuff>\S{3})?\.[zipZIPlodLOD]{3}'
      self.f3ServoPackage_template = '(?P<buildTarg>\w{4})\.(?P<custCfg>\w{4})\.(?P<servoRev>%s[0-9a-fA-F]{0,4})\.(?P<fsuff>\S{3})\.[zipZIPlodLOD]{3}'
      if manifestKey == None:
         self.manifestKey = 'SFWP'
      else:
         self.manifestKey = manifestKey

      if self.manifestKey[:3] in ['TGT']:
         self.f3Manifest = 1
      else:
         self.f3Manifest = 0

   def getZipName(self, zipFileName):
      if DEBUG > 0:
         objMsg.printMsg("zipFile is %s" % os.path.splitext(zipFileName)[0])
      return os.path.splitext(zipFileName)[0]

   def getFileName(self):
      """
      1. Is the package key a zip? then go to 4 else next
      2. codeType is SFWI? Yes goto 4 else next
      3. return filename from manifest
      4. Get release servo prefix from SN translation matrix
      5. Search Servo Package zips/manifests for *match candadite return if found else next
      6. Search for zipName_codeType.LOD and return if exists else next
      7. Return '' (None, with BF_0163537_010200_CONSISTENT_PKG_RES_NO_FILE_FOUND_RESPONSE)
      """

      #Handle the explicit definition
      if not self.dut.codes.get(self.codeType,'') == '':
         fileName = self.dut.codes.get(self.codeType, '')
         objMsg.printMsg("Using Codes.py for translation.")
         if testSwitch.BF_0163537_010200_CONSISTENT_PKG_RES_NO_FILE_FOUND_RESPONSE:
            if fileName == '':
               fileName = None
         return fileName

      #Check if there is a non-list zip and/or an associated manifest
      if type(self.dut.codes.get(self.manifestKey,None)) in [types.StringType]:
         if DEBUG > 0:
            objMsg.printMsg("Looking for servo manifest.")
         manifestName = self.getManifestName()
         if DEBUG > 0:
            objMsg.printMsg("manifestName found %s" % manifestName)
         #Check if there is a manifest... do nothing
         if manifestName == '':
            if DEBUG > 0:
               objMsg.printMsg("No servo manifest found... modifying %s:%s to %s:%s" % (self.manifestKey,self.dut.codes[self.manifestKey],self.manifestKey,str([self.dut.codes[self.manifestKey]]) ))
            #Make the servo.zip into a list so it is handled propperly
            self.dut.codes[self.manifestKey] = [self.dut.codes[self.manifestKey]]

      if self.codeType in subListSupport:
         adjCodeType = self.codeType[0:-1]
      else:
         adjCodeType = self.codeType


      if type(self.dut.codes.get(self.manifestKey,'')) in [types.ListType, types.TupleType]:
         #Handle zip list recursion
         if DEBUG > 0:
            objMsg.printMsg("Looking in ZIP list resolution")
         fileName = self.servoListOptionHandler(self.dut.codes.get(self.manifestKey, []))
         if not (testSwitch.FE_0167407_357260_P_SUPPRESS_OVERLAY_FILE_INFO and self.manifestKey in ['IO_OVL']):
            objMsg.printMsg("Using %s from %s" % (fileName, self.manifestKey))
      elif type(self.dut.codes.get(adjCodeType,'')) in [types.ListType, types.TupleType]:
         #Handle zip list recursion
         if DEBUG > 0:
            objMsg.printMsg("Looking in ZIP list resolution")
         fileName = self.servoListOptionHandler(self.dut.codes.get(adjCodeType, []))
      else:
         #Handle manifest file specification
         if DEBUG > 0:
            objMsg.printMsg("Looking in manifest resolution")
         self.loadManifest()
         fileName = self.servoListOptionHandler(self.manifest.get(adjCodeType,[]))
      if testSwitch.BF_0163537_010200_CONSISTENT_PKG_RES_NO_FILE_FOUND_RESPONSE:
         if fileName == '':
            fileName = None
      return fileName

   def servoListOptionHandler(self, servoList):
      """
      Search for the servo package in the input servoList.  If self.f3Manifest == 0, search using
      the servo release code naming convention.  Otherwise, search using the F3 package servo
      code naming convention.
      """
      fileName = ''
      if type(servoList) in [types.StringType]:
         servoList = [servoList]
      if self.f3Manifest == 0:
         baseRe = self.releasePackage_template
      else:
         baseRe = self.f3ServoPackage_template
      #Ignore null/empty lists
      if len(servoList) > 0:
         for zipPackage in servoList:
            #eg. Looking for a D047 rev inside of mackD047.zip
            if DEBUG > 0:
               objMsg.printMsg("Searching in %s for %s" % (zipPackage, baseRe % self.getReleaseServoPrefix()))

            searchRe = baseRe % self.getReleaseServoPrefix()
            match = re.search(searchRe,zipPackage)
            if not match == None:
               if DEBUG > 0:
                  objMsg.printMsg("Found correct package... %s" % zipPackage)
               if testSwitch.FE_0156514_357260_P_SERVO_FILES_IN_MANIFEST:
                  if zipPackage[-3:] in ['LOD','lod','BIN','bin']:
                     return zipPackage                   # Return now if we already have exact fiel from manifest (not another zip or mft)
               zipName = self.getZipName(zipPackage)
               fileName = self.resolveFileType(zipName)
               if self.f3Manifest == 0:
                  objMsg.printMsg("Using %s from %s" % (fileName, zipName))
               break
            else:
               fileName = ''
         else:
            if not testSwitch.BF_0112487_208705_MUST_FIND_CORRECT_SERVO:
               # return test code if exists
               fileName = self.resolveFileType(self.getZipName(servoList[0]))
               objMsg.printMsg("*" * 10 + "Using 0th item for %s code resolution" % self.codeType + "*" * 10, objMsg.CMessLvl.IMPORTANT)
               objMsg.printMsg("Using %s from %s" % (fileName, str(servoList[0])))

         #Verify that the resolved file is in the available dlfiles
         dlFileIndex = self.ItemInUpperStrList(self.dlFiles,fileName)
         if dlFileIndex != -1:
            fileName = self.dlFiles[dlFileIndex]
         else:
            #Look for primary and codeType match with servo release prefix
            fileName = self.regexDirSearch(zipPackage, self.getReleaseServoPrefix())
            if fileName == '' and not testSwitch.BF_0112487_208705_MUST_FIND_CORRECT_SERVO:
               #Look for primary and codeType match w/o servo release prefix if enabled
               fileName = self.regexDirSearch(zipPackage, '')
               if fileName == '':
                  objMsg.printMsg("DLFile not found.")
            elif fileName == '' and testSwitch.BF_0157044_231166_P_NEW_SERVO_PREFIX_DEPOP_RE_MATCH:
               #Create the package name we would like to see and search for it
               if self.f3Manifest:
                  #if it is F3 the pattern is like GR50.CCD9.D668.SFW.LOD
                  relpat = '(\w{4}\.\w{4}\.)(?P<REL_PREFIX>\w{0,4})(\.\S{3}\.[zipZIPlodLOD]{3})'
               else:
                  #if not the pattern is like Servo_grenada3dB568.lod
                  relpat = '(.+_\w*)(?P<REL_PREFIX>[A-F0-9]{4})(.*\.\w+)'
               relMatch = re.compile(relpat)
               relPrefix = self.getReleaseServoPrefix()
               for zipPackage in servoList:
                  match = relMatch.search(zipPackage)
                  if match:
                     #grab last 2 chars like in B851... 51
                     if testSwitch.FE_0157407_231166_P_USE_SINGLE_CHAR_SVO_REL_PREFIX:
                        replPat = "%s%s" % (relPrefix[0], match.groupdict()['REL_PREFIX'][1:])
                     else:
                        replPat = "%s%s" % (relPrefix, match.groupdict()['REL_PREFIX'][2:])

                     tempZipPackage = re.sub(relpat, '\g<1>%s\g<3>' % replPat, zipPackage)
                     for item in self.dlFiles:
                        if item == tempZipPackage:
                           fileName = tempZipPackage
                           break
                  if fileName != '':
                     break

      if fileName == '' and testSwitch.BF_0112487_208705_MUST_FIND_CORRECT_SERVO:
         objMsg.printMsg("DLFile not found.")

      return fileName

   def regexDirSearch(self,zipPackage, servoPrefix):
      match = re.search(self.releasePackage_template % servoPrefix,zipPackage)
      if not match == None:
         zipDict = match.groupdict()
         for key,value in zipDict.items():
            if type(value) == types.StringType:
               zipDict[key] = string.upper(value)

         for item in self.dlFiles:
            match = re.search(self.releasePackage_template % servoPrefix,item)
            if not match == None:
               codeDict = match.groupdict()
               for key,value in codeDict.items():
                  if type(value) == types.StringType:
                     codeDict[key] = string.upper(value)
               if codeDict['fsuff'] == self.codeType and \
                  codeDict['fname'] == zipDict['fname']:
                  return item
      return ''

   def ItemInUpperStrList(self, inList, value = None):
      """
      Returns upper case string list if value is not entered otherwise returns case insensitive matched index. If item not found then -1 is returned
      """
      outList = []

      if DEBUG > 0:
         objMsg.printMsg("Searching the file list for %s" % value)
      for item in inList:
         if type(item) == types.StringType:
            outList.append(item.upper())
         else:
            outList.append(item)
      if DEBUG > 0:
         objMsg.printMsg("inList is: %s" % inList)
         objMsg.printMsg("outList is: %s" % outList)
      if value == None:
         return outList
      else:
         if inList.count(value) > 0:
            return inList.index(value)
         else:
            if type(value) == types.StringType:
               value = value.upper()
            if outList.count(value) > 0:
               return outList.index(value)
            else:
               return -1

   def resolveFileType(self, baseName):
      """
      Resolves codeType request into file suffix key
      """
      fileNameTemplate = "%(baseName)s%(suffix)s.LOD"

      if DEBUG > 0:
         objMsg.printMsg("Looking for %s in %s" % (self.codeType,packageFamilies[self.manifestKey]))
      if self.codeType in ['SFWI', 'SFWI2', 'SFWI3', 'SFW2', 'CMB2']:
         suffix = ''
      elif self.codeType in packageFamilies[self.manifestKey]:
         suffix = '_' + self.codeType.upper()
      else:
         return ''
      if DEBUG > 0:
         objMsg.printMsg("Returning full path name %s" % (fileNameTemplate % {'baseName':baseName, 'suffix': suffix}))
      return fileNameTemplate % {'baseName':baseName, 'suffix': suffix}


class servo_mft_package(basePackage):
   def __init__(self, dut, codeType, manifestKey = None):
      basePackage.__init__(self,dut,codeType)
      self.releasePackage_mft_template = '(?P<fhead>\S+?)?_?(?P<fname>%s[0-9a-fA-F]{0,4})_?(?P<fsuff>\S{3})?\.[mftMFT]{3}'
      #self.releasePackage_zip_template = '(?P<fhead>\S+?)?_?(?P<fname>%s[0-9a-fA-F]{0,4})_?(?P<fsuff>\S{3})?\.[zipZIP]{3}'

   def getManifestName(self):
      retVal = ''
      mftSearchRe = self.releasePackage_mft_template % self.getReleaseServoPrefix()

      if DEBUG:
         objMsg.printMsg("codes %s" % str(self.dut.codes))
      for packageName, values in packageFamilies.items():
         if DEBUG > 0:
            if DEBUG:
               objMsg.printMsg("getmanifestname overloaded Looking for codetype %s in %s:%s" % (self.codeType, packageName, str(values)))
         if (self.codeType in values) or (self.codeType == packageName):
            retVal = self.dut.codes.get(packageName, '')
            break

      self.packageName = packageName
      if DEBUG:
         objMsg.printMsg("packageName %s, retVal %s" % (str(packageName), str(retVal)))
      mftName = re.sub("\.[zipZIP]{3}", ".mft", retVal)
      match = re.search(mftSearchRe,mftName)
      if DEBUG:
         objMsg.printMsg("mftSearchRe %s, mftName %s" % (str(mftSearchRe), str(mftName)))
      if match == None:
         for fileName in self.dlFiles:
            mat2 = re.search(mftSearchRe, fileName)
            if not mat2 == None:
               mftName = fileName
               if DEBUG:
                  objMsg.printMsg("mftName %s" % (mftName))
               break

      self.manifestName = mftName
      if DEBUG:
         objMsg.printMsg("self.manifestName %s" % (mftName))
      return mftName

class PackageDispatcher(object):
   """
   Class handles dispatching the codeType request to the correct package handler
   """
   def __init__(self,dut, codeType = None, codeVersion = None, regex = True):
      self.dut = dut
      self.codeType = codeType
      self.packageHandler = None

      if not self.codeType == None:
         self.id_HandlerBasedOnCodeType()
      elif not codeVersion == None:
         self.id_HandlerBasedOnCodeVer(codeVersion, regex = regex)

   def __getattr__(self, name):
      try:
         return getattr(self.packageHandler, name)
      except AttributeError:
         return getattr(super(PackageDispatcher, self), name)

   def __setattr(self, name, value):
      if hasattr(self.packageHandler, name):
         setattr(self.packageHandler, name, value)
      else:
         setattr(super(PackageDispatcher, self), name, value)

   def id_HandlerBasedOnCodeVer(self, codeVersion, regex = True):
      #Lookup the package key based on the codeversion
      packageKey = self.getPackageTypeFromCodeVersion(codeVersion, regex)

      #Set the executable segment type as the codeType
      self.codeType = packageFamilies.get(packageKey,(None,))[0]
      if DEBUG:
         objMsg.printMsg("codeType %s" % (self.codeType,))


      #Set the packageHandler to basePackage. Servo isn't supported yet
      self.packageHandler = basePackage(self.dut, self.codeType)
      self.packageHandler.loadManifest()

   def id_HandlerBasedOnCodeType(self):
      if self.codeType in packageFamilies['SFWP']:
         #Handle servo code key download requests
         if testSwitch.BF_0165681_340210_SERVO_MFT_SN_PREFIX_CHK:
            if DEBUG:
               objMsg.printMsg("using servo mft package handler %s" % str(self.codeType))
            self.packageHandler = servo_mft_package(self.dut, self.codeType)
         else:
            if testSwitch.FE_0116894_357268_SERVO_SUPPLIED_TEST_PARMS:
               self.packageHandler = basePackage(self.dut, self.codeType)
            else:
               self.packageHandler = servo_Package(self.dut, self.codeType)
      elif self.codeType == 'SFWI':
         #Handle interface servo codes.. use interface manifest as translation
         self.packageHandler = servo_Package(self.dut, self.codeType, 'TGTP')
      elif self.codeType == 'SFWI2':
         #Handle interface servo codes.. use interface manifest as translation
         self.packageHandler = servo_Package(self.dut, self.codeType, 'TGTA')
      elif self.codeType == 'SFWI3':
         #Handle interface servo codes.. use interface manifest as translation
         self.packageHandler = servo_Package(self.dut, self.codeType, 'TGTB')
      elif self.codeType == 'SFWI4' :
         #Handle interface servo codes.. use interface manifest as translation
         self.packageHandler = servo_Package(self.dut, self.codeType, 'TGTC')
#CHOOI-18May17 OffSpec
      elif self.codeType == 'SFWI5' :
         #Handle interface servo codes.. use interface manifest as translation
         self.packageHandler = servo_Package(self.dut, self.codeType, 'TGTO')
      else:
         self.packageHandler = basePackage(self.dut, self.codeType)

#   def getFileName(self):
#      return self.packageHandler.getFileName()

   def requiredListItems(self, reqItems, searchedList):
      if testSwitch.FE_0127049_231166_CONV_PCKG_ITEMS_NUMBERS:
         #Convert any integers to true integers to get rid of 00's if there or any formatting gems
         reqItems = Utility.convertItemsToNumbers(reqItems)
         searchedList = Utility.convertItemsToNumbers(searchedList)

      if DEBUG:
         objMsg.printMsg("looking for %s in %s" % (reqItems, searchedList))
      for item in reqItems:
         if not item in searchedList:
            #one item not found
            return False

      #found all items
      return True

   def getPackageTypeFromCodeVersion(self, codeversion, regex = True):
      """
      Looks through manifest files to find the appropriate package type.
      1. Get regex for codeversion
      2. Search for manifest match to rev
      3. reverse lookup the package type based on manifest id in Codes.py
      4. set the class packageHandler to the appropriate implementation

      TODO: servo lookup isn't currently supported because it doesn't have a manifest file.
      """
      try:
         patt = re.compile(codeversion, re.I)
      except re.error:
         if testSwitch.virtualRun:
            # VE has code_ver invalid or ? sometimes and this causes the compile to fail
            return None
         else:
            raise

      if testSwitch.FE_0126871_231166_ROBUST_PCK_COMP_SEARCH and not regex:
         reqItems = codeversion.split('.')

      #Search the Package_Name in *.mft files based on Codes.py
      for packageKey, mftName in self.dut.codes.items(): 
         try:
            if DEBUG:
               objMsg.printMsg("packageKey: %s mftName: %s" % (packageKey, mftName))

            if testSwitch.FE_0126871_231166_ROBUST_PCK_COMP_SEARCH and not regex:
               if self.requiredListItems(reqItems,  mftName.replace("_",  ".").split('.')):
                  #found all required items
                  break
            else:
               stripped_mftName = os.path.splitext(mftName)[0].upper()
               if patt.search(stripped_mftName):
                  break
         except:
            if testSwitch.BF_0125115_231166_FIX_SVO_F3_PKG_MFT_LOOKUP:
               if type(mftName) == list:
                  for item in mftName:
                     stripped_item = os.path.splitext(item)[0].upper()
                     if patt.search(stripped_item):
                        break
                  else:
                     #if we didn't find it in the internal loop skip the break below
                     continue
                  #if we found it in the internal loop we will get here
                  break
               else:
                  objMsg.printMsg("Invalid mft '%s' or mftName '%s'" % (mftName, mft))
            else:
               raise

      else:
         objMsg.printMsg("Unable to find package key for file manifest for code on drive!", objMsg.CMessLvl.CRITICAL)
         return None

      return packageKey
