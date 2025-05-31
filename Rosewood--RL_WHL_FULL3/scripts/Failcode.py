#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Failcode.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Failcode.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import os, re
import ScrCmds, traceback

###########################################################################################################
###########################################################################################################

ecDescRe = re.compile('#define (\w{,})\s*(\w{,})\s*/\*+\s*\**\s*(.{,})\*')
ecXlateStore = {}


def searchEC_File(code, fileName):
   global ecXlateStore
   if code in ecXlateStore:
      return code, ecXlateStore[code]
   errCode, errMsg = code, None
   filePath = os.path.join(ScrCmds.getSystemParamsPath(), fileName)
   objFile = open(filePath, 'r')
   strCode = str(code)
   try:
      for line in objFile:
         if line.find(strCode) > -1 :

            m = ecDescRe.search(line)
            if m:
               try:
                  if len(m.group(2))==5:
                     errCode = int(m.group(2))
                     errMsg = m.group(3).strip()
                     break
               except:
                  pass
   finally:
      objFile.close()

   if (errMsg != None): ecXlateStore[code] = errMsg

   return errCode,errMsg

def getFailCodeAndDesc(code):
   errCode, errMsg = code, None
   fileName = 'codes.h'
   procFileName = 'proc_codes.h'

   #First try codes.h
   try:
      errCode,errMsg = searchEC_File(code,fileName)
   except:
      ScrCmds.statMsg("Exception in parsing codes.h\n%s" % traceback.format_exc())
   #If we didn't find the ec in codes.h lets try proc_codes.h
   if errMsg == None:
      try:
         errCode,errMsg = searchEC_File(code,procFileName)
      except:
         ScrCmds.statMsg("Exception in parsing proc_codes.h\n%s" % traceback.format_exc())

   # get failcode from table above if cannot find in codes.h
   if errMsg==None:
      errCode = code
      errMsg = 'Failcode not found in codes.h nor proc_codes.h'
   # return valid data
   return errCode, errMsg

def translateRwErrorCode(code):
   #Read in rw_sense.h
   code = code & 0x0FFFFFFF
   errCode, errMsg = code, None
   fileName = 'rw_sense.h'
   filePath = os.path.join(ScrCmds.getSystemParamsPath(), fileName)
   pat = '\s*#define\s*(?P<DESC>\S*)\s*.(?P<EC>0x[0-9,A-F]{8})\s*(\|\sMOVE_FRU_FLAG.)*'
   objFile = open(filePath, 'r')
   p = re.compile(pat)
   for line in objFile.readlines():
      found = p.search(line)
      if not found == None:
         data = found.groupdict()
         if int(data['EC'],16) == code:
            errMsg = data['DESC']

   # get failcode from table above if cannot find in codes.h
   if errMsg==None:
      errMsg = 'Failcode not found in codes.h'
   # return valid data
   return errCode, errMsg

if __name__ == '__main__':
   ec,emsg = translateRwErrorCode(0x0401008A)
   print("%s:%s" % (hex(ec),emsg))
###########################################################################################################
###########################################################################################################
#---------------------------------------------------------------------------------------------------------#
