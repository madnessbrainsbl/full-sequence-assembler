#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements a basic ICmd interface
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_ICmd.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_ICmd.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
import Constants
from Constants import *
from DesignPatterns import Singleton, Null
from Process import CProcess
import MessageHandler as objMsg
from Rim import objRimType

class base_ICmd(CProcess, Singleton):
   passThroughList = []
   directCallList = []
   aliasList = []

   def __init__(self, params = Null(), objPwrCtrl = Null()):
      Singleton.__init__(self)
      CProcess.__init__(self)
      self.params = params
      self.maxlba = None
      self.objPwrCtrl = objPwrCtrl
      self.IdentifyDeviceBuffer = ''

   def ClearIdentBuffer(self):
      self.IdentifyDeviceBuffer = ''

   def __getattribute__(self, name):
      aliasList = CProcess.__getattribute__(self,'aliasList')
      if name in aliasList:
         name = aliasList[name]

      try:
         return CProcess.__getattribute__(self, name)
      except AttributeError:
         if name in self.passThroughList:
            self.prmName = name
            return self.overridePrmCall
         elif name in self.directCallList or (hasattr(self.params, name) and not hasattr(Constants, name)):
            self.prmName = name
            return self.directCall
         else:
            raise

   # base class stub functions
   def getRimCodeVer(self):return ''



   def directCall(self, *args, **kwargs):
      tempPrm = dict(getattr(self.params,  self.prmName))

      if self.ovrPrms:
         tempPrm.update(self.ovrPrms)

      ret = self.St(tempPrm)

      self.ovrPrms = {}
      ret = self.translateStReturnToCPC(ret)

      return ret


   def translateStReturnToCPC(self, stat):
      import types      # IOMQM compatibility
      if type(stat) == types.DictType:
         objMsg.printMsg("Dictionary detected stat=%s" % (stat))
         return stat

      ataInfo = self.dumpATAInfo()

      if not 'LBA_UPPER' in ataInfo :
         #non 48 bit... params match so just pass on
         retDict = ataInfo
         for name in retDict:
            try:
               retDict[name] = int(retDict[name], 16)
            except:
               pass
         if testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser():
            retDict['LLRET']=stat[2]
      else:
         retDict = {
            'LLRET': stat[2],
            'ERR':   int(ataInfo['ERR_REG'],16),
            'STS':   int(ataInfo['STATUS'],16),
            'LBA':   int(ataInfo['LBA_UPPER'],16) + int(ataInfo['LBA_LOWER'],16),
            'SCNT':  int(ataInfo['SCNT'],16),
            'DEV':   int(ataInfo['DEV'],16),

            }
      retDict.update({
            'CYL':   (retDict['LBA']>> 8) & 0xFFFF,
            'HEAD':  retDict['LBA'] >> 24,
            'SCTR': retDict['LBA'] & 0xFF,
         })
      return retDict
   def directTranslateStReturnToCPC(self, stat, retDict):
      retDict['LLRET'] = stat[2]
      for name in retDict:
         try:
            retDict[name] = int(retDict[name], 16)
         except:
            pass
      return retDict

   #-------------------------------------------------------------------------------------------------------
   @classmethod
   def overridePrmCall(cls, STARTING_LBA, MAXIMUM_LBA, STEP_LBA = 256, BLKS_PER_XFR = 256, \
                         DATA_PATTERN0 = 0, STAMP_FLAG = 0, COMPARE_FLAG = 0, LOOP_COUNT = 1, timeout = 252000, exc = 1):
      pass


   #----------------------------------------------------------------------------
   def resetCustomerConfiguration(self):
      self.St(self.params.CurrentFwOptionsSettings)

      self.St(self.params.WrtDefaultFwOptions) # requisite test calls

      self.St(self.params.CurrentFwOptionsSettings)

   def GetSmartFrames(self):
      self.UnlockFactoryCmds()
      self.St(test_num = 638, CTRL_WORD1=0x0002, DFB_WORD_0 = 0x5201, DFB_WORD_1 = 0x0100, DFB_WORD_2 = 0x0300, timeout = 30, DblTablesToParse = ['P508_BUFFER',])
      if testSwitch.virtualRun:
         data = '9WM0ZXNN\x00\xc9\x00\x85G.\x01AA\x02\x06\x08\xc4\x1e\x00\x01HPG1    027JJ0NLX       \x01\x18\x01\x18\x01\x18\x11\x98\x04\x00\x00\x01\x00\x00\x00\x00\x01\x0f\x00dd\x00\x00\x00\x00\x00\x00\x00\x03\x03\x00\\\\\x00\x00\x00\x00\x00\x00\x00\x042\x00ddD\x00\x00\x00\x00\x00\x00\x053\x00dd\x00\x00\x00\x00\x00\x00\x00\x07\x0f\x00d\xfd\x13\x00\x00\x00\x00\x00\x00\t2\x00dd\x00\x00\x00\x00\x00\x00\x00\n\x13\x00dd\x00\x00\x00\x00\x00\x00\x00\x0c2\x00ddH\x00\x00\x00\x00\x00\x00\xb4;\x00dd\x00\x00\x00\x00\x00\x00\x00\xb82\x00dd\x00\x00\x00\x00\x00\x00\x00\xbb2\x00dd\x00\x00\x00\x00\x00\x00\x00\xbc2\x00d\xfd\x00\x00\x00\x00\x00\x00\x00\xbd:\x00dd\x00\x00\x00\x00\x00\x00\x00\xbe"\x00HE\x1c\x00\x1c\x1c\x00\x00\x00\xbf2\x00dd\x00\x00\x00\x00\x00\x00\x00\xc02\x00ddD\x00\x00\x00\x00\x00\x00\xc12\x00ddD\x00\x00\x00\x00\x00\x00\xc2"\x00\x1c(\x1c\x00\x00\x00\x18\x00\x00\xc3\x1a\x00dd\x00\x00\x00\x00i\x11\x01\xc43\x00dd\x00\x00\x00\x00\x00\x00\x00\xc5\x12\x00dd\x00\x00\x00\x00\x00\x00\x00\xc6\x10\x00dd\x00\x00\x00\x00\x00\x00\x00\xc7>\x00\xc8\xfd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe2X\x00\x9f\x00\x13\x00\x00>\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x08\x0fhhhhhhhh\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00:\x91\xfc\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00hhhhhhhh\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00:7\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00hhhhhhhh\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00:B\xfe\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00hhhhhhhh\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00:\xd8\t\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00hhhhhhhh\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00:\x91\x0b\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00hhhhhhhh\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00;\xa4\x12\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00hhhhhhhh\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00:n\x12\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00hhhhhhhh\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00:\x91\x14\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
      else:
         ret = self.dut.objSeq.SuprsDblObject['P508_BUFFER']
         data = self.extractBufferDblog(ret)
      return data

   def extractBufferDblog(self, buffDict):
      import re
      data = ''
      bcol = re.compile('B[\da-fA-F]')
      for row in buffDict:

         for key in sorted(row.keys()):
            if bcol.match(key):
               try:
                  data += chr(int(row[key],16))
               except:
                  objMsg.printMsg("Error: data:'%s' ; val: '%s', key: '%s'" % (data, row[key], key))
                  raise

      return data

   def ReadLenovo8S(self):
      self.SmartReadLogSec(0xDF, 1)
      ret = self.GetBuffer(RBF, 0, 512)
      
      return ret['DATA']

   def ConvertWRmode(self, wrCmd = None,):
      """
      Write/read mode:
      0 = write/read
      1 = read
      2 = write
      3 = read/write
      4 = read verify
      """
      if wrCmd == None:
         return 0
      wrmode = 0
      WRDMAExt = {
            'ReadDMAExt'    : 0x25,
            'WriteDMAExt'   : 0x35,
            'ReadVerifyExt' : 0x42,
                  }
      WRDMAExtNum = {
            'ReadDMAExt'    : 1,
            'WriteDMAExt'   : 2,
            'ReadVerifyExt' : 4,
                  }
      for key in WRDMAExt:
         if WRDMAExt[key] == wrCmd:
            wrmode = WRDMAExtNum[key]
            break
      return wrmode

