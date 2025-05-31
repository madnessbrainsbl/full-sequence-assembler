#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: ScriptCheckSums Module provides package verification using md5 check sums
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ScriptCheckSums.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ScriptCheckSums.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

from Test_Switches import testSwitch
from Constants import *
if PY_27:
   import hashlib
else:
   try:
      import sha
   except:
      # md5 and sha have the same interface although sha is preferred
      #WinFOF 2.4- doesn't support the sha module so this is provided for bench execution.
      import md5 as sha

import os, sys, traceback
import re, time
from stat import S_IREAD

DEBUG = 0

try:
   ScriptComment("")
except:
   def ScriptComment(arg):
      print str(arg)


class md5Checker:
   FILE_BASED_CHK = 1
   LINE_BASED_CHK = 2

   def __init__(self,chkSumPath = r"C:\var\merlin\scripts\bench", chkSumFile = "md5Sums.txt", checkSumMode = LINE_BASED_CHK, makeReadOnly = 1):
      self.chkSumPath = chkSumPath
      self.chkSumFile = chkSumFile
      self.filePat = re.compile(".*\.py\Z")
      self.fileChkSums = {}
      self.checkSumMode = checkSumMode
      self.makeReadOnly = makeReadOnly
      self.ignoreCheckSumList = ['rptextractors.py', 'dex.py',
                                 'writeresultsfunctions.py', 'Codes.py',
                                 'resultshandlers.py', 'viewerextractors.py',
                                 'TSE_FW_param.py', 'TSE_FW_support.py', 'cudacom.py',
                                 'parametricextractors.py', 'tabledictionary.py', 'parseresults.py',
                                 'RimTypes.py','StateTable.py','PIF.py','TableSuppress.py']

   def createCheckSums(self):

      filelist = os.listdir(self.chkSumPath)
      for chkFile in filelist:
         if self.filePat.match(chkFile):
            if PY_27:
               md5sum = hashlib.md5()
            else:
               md5sum = sha.new()
            if self.checkSumMode == self.FILE_BASED_CHK:
               md5sum = self.accumulateFileCheckSum(md5sum,os.path.join(self.chkSumPath,chkFile))
            elif self.checkSumMode == self.LINE_BASED_CHK:
               md5sum = self.accumulateLineBasedCheckSum(md5sum,os.path.join(self.chkSumPath,chkFile))
            else:
               raise Exception, "Unsupported Checksum Mode %s" % self.checkSumMode

            self.fileChkSums[chkFile] = str(md5sum.hexdigest())

   def accumulateFileCheckSum(self,md5Item, filePath):
      md5Item.update(open(filePath,'r').read())
      return md5Item

   def accumulateLineBasedCheckSum(self,md5Item,filePath):
      commentPat = re.compile("\A#.*")
      fileObj = open(filePath,'r')
      try:
         for line in fileObj:
            if not commentPat.search(line):
               md5Item.update(line.strip())
            else:
               if DEBUG > 1:
                  print "Ignoring line: %s" % line
      finally:
         fileObj.close()
      return md5Item

   def createCheckSumFile(self):
      outFile = open(os.path.join(self.chkSumPath, self.chkSumFile),'w')
      try:
         for key,value in self.fileChkSums.items():
            fileChksum = "%s=%s" % (key,value)
            if DEBUG > 0:
               print fileChksum
            outFile.write(fileChksum + "\n")
      finally:
         outFile.close()
         if self.makeReadOnly:
            os.chmod(os.path.join(self.chkSumPath, self.chkSumFile),S_IREAD)

   def verifyCheckSumFile(self):

      chkSumPat = re.compile("(?P<file>\S*)=(?P<chksum>\S*)")
      tempCheckSums = {}
      misMatch = []

      try:

         inFile = open(os.path.join(self.chkSumPath,self.chkSumFile),'r')

         try:
            for line in inFile:
               match = chkSumPat.search(line)
               if match:
                  resDict = match.groupdict()
                  tempCheckSums[resDict['file']] = resDict['chksum']
         finally:
            inFile.close()

         for key,value in self.fileChkSums.items():
            if not value == tempCheckSums.get(key,0):
               if not key in self.ignoreCheckSumList:
                  misMatch.append(key)
               if DEBUG > 0:
                  ScriptComment("Mismatch on %s; %s != %s" % (key,value,tempCheckSums.get(key,0)))

      except IOError:
         misMatch = self.fileChkSums.keys()
         misMatch.append(traceback.format_exc())

      return misMatch



if __name__ == "__main__":
   myChecker = md5Checker(chkSumPath = os.getcwd(),makeReadOnly = 0)
   myChecker.createCheckSums()
   myChecker.createCheckSumFile()
   resp = myChecker.verifyCheckSumFile()
   if len(resp) > 0:
      raise Exception
##   def timeIt(inFunc):
##      startTime = time.time()
##      ret = inFunc()
##      eTime = time.time()-startTime
##      print "Function (%s) time: %f" % (str(inFunc),eTime)
##      return eTime,ret
##   sumTime = []
##   test_range = 1
##   for x in xrange(test_range):
##      myChecker = md5Checker()
##      fTime, ret = timeIt(myChecker.createCheckSums)
##      timeIt(myChecker.createCheckSumFile)
##      timeIt(myChecker.verifyCheckSumFile)
##
##
##      myChecker = md5Checker(checkSumMode = md5Checker.LINE_BASED_CHK)
##      lTime, ret = timeIt(myChecker.createCheckSums)
##      timeIt(myChecker.createCheckSumFile)
##      timeIt(myChecker.verifyCheckSumFile)
##      lineCost = (lTime-fTime)*100/fTime
##      sumTime.append(lineCost)
##   totCost = sum(sumTime)/float(len(sumTime))
##   print "Line based cost = %0.2f%s" % (totCost,"%")
##   """
##   Simulations show a 253% increase in implementation time for line based calculation... .25 seconds average.
##   """