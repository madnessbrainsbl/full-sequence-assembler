#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/15 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Utility.py $
# $Revision: #4 $
# $DateTime: 2016/12/15 19:55:01 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Utility.py#4 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import types, struct, time, re
from Test_Switches import testSwitch
from DesignPatterns import Singleton

DEBUG = 0

class overRidePrmException (Exception):
   def __init__(self ,data):
      pass

class typeMismatchInDecendant (overRidePrmException):
   """Incorrect type passed to primary dictionary."""
   pass

class keyNotInParentDict (overRidePrmException) :
   """No matching key in primary dictionary."""
   pass


class staticDefaultDict(dict):
   """
   User defined dictionary superclass that provides for a user set default value.
   *This class should be used if the default value is to complex to be passed in
      or track using a standard .get or .setdefault dictionary call.
   """
   def __init__(self,initialValue,defaultValue = None):
      dict.__init__(self)
      for entry in initialValue:
         self[entry] = initialValue[entry]
      self.__defaultItem = defaultValue

   def get(self, key, default = None):
      #override default with our classes new default
      if default == None:
         default = self.__defaultItem

      return dict.get(self, key, default)

   def __getitem__(self,item):
      #override default with our classes new default
      try:
         return dict.__getitem__(self,item)
      except KeyError:
         return self.__defaultItem

class timoutCallback(object):
   """
   Callback class that will when called raise an exception if the allotted time has passed.
   erroFunc is the function to call with errorInfo when timer has elapsed.
      Timer starts at instantiation.
   """
   __slots__ = ['maxTime', 'errorFunc','errorInfo', 'timeout']

   def __init__(self, timeout, errorFunc, errorInfo):
      self.maxTime = time.time() + timeout
      self.timeout = timeout
      self.errorFunc = errorFunc
      self.errorInfo = errorInfo

   def resetTimeout(self):
      self.maxTime = time.time() + self.timeout

   def __call__(self, raiseError = True):
      """
      Evaluate the instances timeout status.
         Calls error func if timer expired and raiseError is True.
         Else
            Returns boolean eval of timer expired. (Expired = True)
      """
      if time.time() > self.maxTime:
         if raiseError:
            self.forceError()
         else:
            return True
      else:
         return False

   def forceError(self):
      if type(self.errorInfo) in [types.ListType,types.TupleType]:
         self.errorFunc(self.errorInfo[0],self.errorInfo[1])
      else:
         self.errorFunc(self.errorInfo)

class CSpcIdHelper(object):
   """
   Object to keep track of spc_id settings.  spdIdHelper is a dictionary with the
   key being the table/spc_id name and the value being the spc_id value.  This
   class assumes that spc_id's values are integers.
   """
   def __init__(self, dut):
      self.dut = dut
      spcHelper = getattr(self.dut, 'spcIdHelper', None)
      if spcHelper is None:
         self.dut.spcIdHelper = {}

      self.OpOffset = { # spc_id offsets for each operation
         'PRE2' : 10000,
         'CAL2' : 20000,
         'FNC2' : 30000,
         'CRT2' : 40000,
         'CMT2' : 50000,
         'FIN2' : 60000,
         'IOSC2': 70000,
         'AUD2' : 80000,
         'CUT2' : 90000,
         'BRO' : 100000,
         'STC' : 110000,
         'STS' : 130000,
      }

   def getSetIncrSpcId(self, spcIdName, startSpcId = 1, increment = 1, useOpOffset = 0):
      """
      This function will get the current spc_id for the given spcIdName.
      If there is no current spc_id for the given spcIdName, one will be set using
      the value given in startSpcId, and the operation offset will be added in if
      useOpOffset is set.  The current spc_id value will then be returned
      to the user, and the spc_id will be incremented by the amount given in the
      increment input for future usage.
      """
      curSpcId = self.getSpcId(spcIdName)
      if curSpcId == None:
         curSpcId = startSpcId
         if useOpOffset:
            curSpcId += self.OpOffset[self.dut.nextOper]
         self.setSpcId(spcIdName, curSpcId)

      self.incrementSpcId(spcIdName, increment)
      return curSpcId

   def getSpcId(self, spcIdName):
      spcIdHelper = getattr(self.dut, 'spcIdHelper')
      return spcIdHelper.get(spcIdName, None)

   def setSpcId(self, spcIdName, spcIdValue):
      self.dut.spcIdHelper[spcIdName] = spcIdValue

   def incrementSpcId(self, spcIdName, incrVal = 1):
      self.dut.spcIdHelper[spcIdName] += incrVal
      return self.dut.spcIdHelper[spcIdName]

   def incrementRevision(self, spcIdName, value = 100):
      """
      Round the spcId up to the nearest 'value' multiple.  This can be used to
      implement the major revision part of a major/minor spc_id revisioning system.
      Any integer may be used for 'value', but a power of 10 is recommended for
      clarity.
      """
      spcId = (self.getSpcId(spcIdName)/value + 1) * value
      self.setSpcId(spcIdName, spcId)
      return spcId


class CUtility(Singleton):
   """Utility class for general functions specific to code and system management.
      Not related to drive functionality.
   """

   @staticmethod
   def overRidePrm(initPrm, overPrms):
      """Overide dictionary parameter value w/ checks for key exists and parameter type."""
      kList = [k for k in overPrms.keys() if not k in initPrm.keys()]
      if ([]) != kList:
         raise keyNotInParentDict(kList)

      checkType = lambda i1,i2: type(i1)==type(i2)
      valList = [v for k,v in overPrms.items() if not checkType(v,initPrm[k])]
      if ([])!= valList:

         raise typeMismatchInDecendant(valList)
      initPrm.update(overPrms)
      return initPrm

   @staticmethod
   def ReturnTestCylWord(testCyl):
      upperWord = (testCyl & 0xFFFF0000) >> 16
      lowerWord = (testCyl & 0x0000FFFF)
      return (upperWord,lowerWord,)
   
   @staticmethod
   def convertZoneListtoZoneMask(zone_list):
      zone_mask_low = 0
      zone_mask_high = 0
      for zone in zone_list:
         if zone < 32:
            zone_mask_low |= (1<<zone)
         else:
            zone_mask_high |= (1<<(zone - 32))
      return [zone_mask_low, zone_mask_high]

   @staticmethod
   # Converts a list into a 64 bit mask. It is expected for the caller to understand what values are being passed in
   # whether there will be wrap around for the 64 bit mask.
   def convertListTo64BitMask(Lst):
      mask = 0L
      mask_3, mask_2, mask_1, mask_0 = 0,0,0,0
      for value in Lst:
         mask |= 1 << ( value % 64 )

      mask_0 =  mask & 0xFFFF
      mask_1 = (mask & (0xFFFF << 16)) >> 16
      mask_2 = (mask & (0xFFFF << 32)) >> 32
      mask_3 = (mask & (0xFFFF << 48)) >> 48

      zoneMaskHi = (mask_3, mask_2)
      zoneMaskLo = (mask_1, mask_0)
      return (zoneMaskHi, zoneMaskLo)
   
   @staticmethod
   def deMaskList( mask, maxVal = 16, base = 2):
      """
      Returns a list of numbers corresponding to the output components raised to base power in a mask
      Eg:
         [8,] = deMaskList(256)
      """
      vals = [base**i for i in xrange(maxVal)]

      retVals = []
      for index,val in enumerate(vals):
         if (mask & val)>0:
            retVals.append(index)

      return retVals

   @staticmethod
   def convertListToZoneBankMasks(Lst):
      if Lst:
         Banks = range(0, max(Lst)/64+1, 1)
         BankMasks = {}
         for Bank in Banks:
            BankMasks.setdefault(Bank,[])
         for value in Lst:
            Bank = value / 64
            BankMasks[Bank].append(value)
         return (BankMasks)
      return {}

   @staticmethod
   def converttoHeadRangeMask(low_head, high_head):
      return low_head << 8 | high_head
   
   @staticmethod
   def getUMPZone(zn_range):
      if testSwitch.extern.FE_0164615_208705_T211_STORE_CAPABILITIES and testSwitch.SMR:
         import SIM_FSO, cPickle, VBAR
         data = SIM_FSO.CSimpleSIMFile("VBAR_DATA").read()
         wpp, (tableData, colHdrData) = cPickle.loads(data)
         measAllZns = VBAR.CVbarMeasurement()
         measAllZns.unserialize((tableData, colHdrData))
         if not measAllZns.getRecord('TRACK_PER_BAND', 0, 0):
            return []
         #retrive track per band of each input zone
         zn_list = [zn for zn in zn_range if (measAllZns.getRecord('TRACK_PER_BAND', 0, zn)) == 1]
         return zn_list
      else:
         objMsg.printMsg("CVBAR_DATA not found or not SMR")
         return []

   @staticmethod
   def convertZoneListToZoneRange(zoneList):
      ''' Returns a list of zone ranges'''
      zoneList.sort()
      rangeList = []
      startZn = endZn = None
      for zn in zoneList:
         if startZn == None:  # Start first zone range
            startZn = endZn = zn
         elif zn != endZn + 1:  # End current zone range because of zone break
            rangeList.append([startZn, endZn])
            startZn = endZn = zn  
         else:
            endZn = zn
      if startZn != None: # Append final zone range (single zone and last range case)
         rangeList.append([startZn, endZn])
    
      return rangeList
   
   @staticmethod
   def reverseLbaWords(lbaSeq):
      maxShift = len(lbaSeq)-1
      val = 0
      for index, pos in enumerate(lbaSeq):
         val += pos << ((maxShift-index)*16)
      return val

   @classmethod
   def lbaMath(cls, *args, **kwargs):
      operation = kwargs.get('operation',  '+')
      intermediate = 0
      for arg in args:
         arg = cls.reverseLbaWords(arg)
         intermediate = eval("intermediate %s %s" % (operation, arg))
      return cls.returnStartLbaWords(intermediate)

   @staticmethod
   def returnStartLbaWords(startLBA):
      upperWord1 = (startLBA & 0xFFFF000000000000) >> 48
      upperWord2 = (startLBA & 0x0000FFFF00000000) >> 32
      lowerWord1 = (startLBA & 0x00000000FFFF0000) >> 16
      lowerWord2 = (startLBA & 0x000000000000FFFF)

      return (upperWord1,upperWord2,lowerWord1,lowerWord2,)

   @staticmethod
   def returnStartLba(startLBAWords):
      startLBA = (startLBAWords[0] << 48) + \
                 (startLBAWords[1] << 32) + \
                 (startLBAWords[2] << 16) + \
                  startLBAWords[3]

      return startLBA

   @staticmethod
   def convertLBANumber2LBARegister(LBA):
      """
         Converts LBA Number to LBA Register
         @type LBA: integer
         @param LBA: LBA number to be converted
         @return LBA_HIGH, LBA_MID, LBA_LOW: integer of LBA register
         Example:
            from Utility import CUtility
            LBA_HIGH, LBA_MID, LBA_LOW = CUtility.convertLBANumber2LBARegister(0xBA9876543210)
         Result:
            LBA_HIGH = 0xBA54
            LBA_MID  = 0x9832
            LBA_LOW  = 0x7610
      """
      LBA_HIGH = ((LBA & 0xFF0000000000) >> 32) + ((LBA & 0x000000FF0000) >> 16)
      LBA_MID  = ((LBA & 0x00FF00000000) >> 24) + ((LBA & 0x00000000FF00) >> 8)
      LBA_LOW  = ((LBA & 0x0000FF000000) >> 16) + (LBA & 0x0000000000FF)
      
      return LBA_HIGH, LBA_MID, LBA_LOW

   @staticmethod
   def reverseTestCylWord(testCylTuple):
      """
      Returns the long integer version of a test cylinder word tuple
      """
      return (testCylTuple[0] << 16) + testCylTuple[1]

   @classmethod
   def returnIntMantWord(cls, floatVal, mantissaScaler = 10**3):
      """
      Returns the (Integer,Mantissa*10^3) of the input float
      """
      if mantissaScaler == 10**3:
         return cls.float_as_words(floatVal)
      elif mantissaScaler == 10**6:
         fval = cls.float_as_words(floatVal)
         retVal = [fval[0],fval[1],0]

         return retVal
      else:
         return 0

   @staticmethod
   def float_as_words(dval, _little_endian=0):
      "Use struct.unpack to decode a double precision float into 2 words"
      tmp = list(struct.unpack('2H',struct.pack('f', dval)))
      if not _little_endian:
         tmp.reverse()

      return tmp                 # return as list

   @classmethod
   def copy(cls, val):
      from array import array, ArrayType

      inType = type(val)
      if inType in [types.ListType,types.TupleType]:
         outVal = map(cls.copy,val)
         if inType == types.TupleType:
            outVal = tuple(outVal)

      elif inType == types.DictType:
         outVal = {}
         for key,value in val.items():
            outVal[cls.copy(key)]= cls.copy(value)
      elif inType == ArrayType:
         outVal = array(val.typecode, val.tostring())
      else:
         outVal = val

      return outVal

   @staticmethod
   def setDBPrecision(val, width = 0, precision = 28):
      """
      Sets the output format of the value to conform to the corresponding database required specification.
      @param width: width of the total field definition. Leave at 0 to allow least chars to represent value
      @param precision: precision of decimal number returned. Rounding will be performed to reach required value.
      """
      strVal = "%" + str(width) + "." + str(precision) + "f"
      strVal = strVal % float(val)
      return  strVal.strip()

   @staticmethod
   def setZoneMask(zoneList):
      """
      Converts a list of zones into a zone masked value
      """
      zHex = 0
      for zone in zoneList:
         zHex = zHex | 2**zone
      return zHex

   @classmethod
   def setZoneMaskBlock(cls, zoneList):
      """
      Converts a list of zones into a 16 word zone mask block parm
      """
      words = 16
      ZoneMaskBlock = []

      zHex = cls.setZoneMask(zoneList)

      while (words > 0 ):
         ZoneMaskBlock.append( (zHex & 0xFFFF) )
         zHex = zHex >> 16
         words = words - 1
      ZoneMaskBlock.reverse()

      return tuple(ZoneMaskBlock)

   @staticmethod
   def deMaskList( mask, maxVal = 16, base = 2):
      """
      Returns a list of numbers corresponding to the output components raised to base power in a mask
      Eg:
         [8,] = deMaskList(256)
      """
      vals = [base**i for i in xrange(maxVal)]

      retVals = []
      for index,val in enumerate(vals):
         if (mask & val)>0:
            retVals.append(index)

      return retVals

   @staticmethod
   def convertTestHeadEncodedMask( mask):
      """
      Convert mask encoded test head range to a tuple of min/max head.
      Eg:
         (4,7) = convertTestHeadEncodedMask(0x4,0x7)
      """
      return ((mask & 0xFF00) >> 8, mask & 0xFF)

   @staticmethod
   def convertStrToBinaryWords( inStr, padChar = '0', leftJustify = 0):
      """
      Return string as a tuple of words in binary converted ascii
      """
      import MessageHandler as objMsg
      import struct

      if leftJustify == 1:
         fillVal ='%-12s' % inStr
      else:
         fillVal ='%12s' % inStr

      fillVal = fillVal.zfill(12)
      fillVal = fillVal.replace(' ', padChar)

      if DEBUG:
         objMsg.printMsg( '"%s"' % fillVal)
      return struct.unpack("6H", fillVal)

   #----------------------------------------------------------------------------
   @staticmethod
   def convertEndianStrHexChar(str, atomicElementSize = 8):
      """
         Convert from string of hexadecimal character to little-endian string of hexadecimal character.
         @type str: string
         @param str: string of hexadecimal character
         @type atomicElementSize: integer
         @param atomicElementSize: Atomic element size in bit. Only supported for 8, 16 and 32-bit.
         @return strHexChar: little-endian string of hexadecimal character
         Example:
            from Utility import CUtility
            str = "01234ABC"
            strHexChar = CUtility.convertEndianStrHexChar(str, 8)
         Result:
            strHexChar = "BC4A2301"
      """
      nibbleAES = atomicElementSize / 4

      import re
      key = "[0-9A-Fa-f]" * nibbleAES
      keyc = re.compile(key)
      return "".join(keyc.findall(str)[::-1])

   #----------------------------------------------------------------------------
   @staticmethod
   def safeDictDelete(attrList, inDict):
      for attr in attrList:
         inDict.pop(attr,None)
      return inDict

   @staticmethod
   def regexInIterable( value, inputList):
      import re
      if value == None:
         return False
      for item in inputList:
         if re.search(item,value):
            return True
      return False

   @staticmethod
   def dictValLookup(dictObj, value, default = False):
      """
      Lookup key for value- return 1st match or error if default not provided.
      """
      for key,val in dictObj.iteritems():
         if val == value:
            return key
      if default == False:
         raise KeyError
      else:
         return default

   @classmethod
   def lookupValInNestedDict(cls, lookupDict, detectionDict):
      """
      Returns the dictionary key if any attribute values in lookupDict match any regex patterns in the lists contained in the detectionDict values
      """
      attr = None
      for vendorName, detectionTypes in detectionDict.items():
         for detectionType,values in detectionTypes.items():
            value = lookupDict.get(detectionType)
            if DEBUG > 0:
               objMsg.printMsg("Looking for attr %s driveVal %s in re's %s" % (detectionType, value, values))
            if cls.regexInIterable(str(value),values):
               attr = vendorName
               break
         if attr:
            #we found the hga supplier
            break
      return attr

   @classmethod
   def convertDictToPrintStr(cls, dictionary, dictNameStr = "", justify = True, multiLine = True, rndOff = 4, offset = 0):
      """
      Returns a string that represents the sorted dictionary, with each key/value pair on its own line.  Values can be strings, floats, ints, lists, etc.
      Floats will be rounded based on the rndOff parameter, which is defaulted to 4 places past the decimal.  Any value lists that exist, where all the
      elements of that list are identical, will be represented in the output string in shorthand notation; [value]*number of elements.  If justify is set
      to True, the value data will be left justified to one more space than the maximum length of any key in the dictionary.  The offset will be used to
      tab nested dictionaries in the output, and is handled internally.  IT SHOULD NOT BE SET BY THE USER.  If multiLine is set to False, the dictionary
      will simply be displayed on one line, rather than one line per key.
      ex. objMsg.printMsg(converDictToPrintStr(dictionaryToPrint, 'OptionalName'))
      """
      outStr = ""
      if multiLine:
         offsetTabs = offset   # Offset to be used when dumping nested dictionaries in justified mode.
         newLine = '\n'
         separator = ':'
      else:
         offset = 0
         newLine = ', '
         separator = ''

      # If a name has been provided for the dictionary, encase it in '=' and add it to the output string.
      if dictNameStr != "":
         if multiLine == True:
            outStr = '='*15 + ' ' + dictNameStr + ' ' + '='*15 + newLine
         else:
            outStr = '%s = {' % dictNameStr
      else:
         if multiLine == True:
            outStr = '\n'
         else:
            outStr = '{'

      # If justification is requested, determine the maximum length of the longest key in the dictionary.
      if justify == True:
         maxWidth = 0
         for key in dictionary:
            if type(key) == str:
               maxWidth = max(maxWidth, len(key))
            else:
               maxWidth = max(maxWidth, len(str(key)))

      # Step through the dictionary, in sorted key order, building key/value pair strings.
      for key in sorted(dictionary.keys()):
         value = dictionary[key]
         # Limit the reported precision on float values to 4 digits.
         if type(value) == float:
            dataStr = '%s' % round(value,rndOff)

         # Condense lists if possible, (all values the same), otherwise, just limit precision.
         elif type(value) == list:
 #           if type(value[0]) in [float, int, str]:   # Is the list comprised of floats
               count = 1
               # Walk the list, checking to see if all values are the same.
               for item in value[1:]:
                  if item != value[0]:
                     break
                  else:
                     count += 1

               # If all values are the same, condense the list to [#.####]*length format.
               if count == len(value):
                  # Format the data.
                  if type(value[0]) == float:
                     dataStr = '%s' % round(value[0],4)
                  elif type(value[0]) == str:
                     dataStr = "'%s'" % value[0]
                  else:
                     dataStr = '%s' % value[0]
                  # Apply the shorthand list format to the formatted data.
                  dataStr = "[%s]*%d" % (dataStr,count)

               # Not all of the values were the same, so just limit reported precision.
               else:
                  dataStr = '['
                  for index in range (len(value)):
                     if type(value[index]) == float:
                        dataStr += '%s,' % round(value[index],4)
                     elif type(value[index]) == str:
                        dataStr += "'%s'," % value[index]
                     else:
                        dataStr += "%s," % str(value[index])
                  dataStr = dataStr.rstrip(',') + ']'

#            else:
#               # Must be a list of dictionaries or tuples, or some such like that.
#               dataStr = str(value)  # Just 'str' the data and live with what we get.

         # Special case where the value of the current key is another dictionary.
         elif type(value) == dict:
            # Call convertDictToPrintStr method recursively in order to process nested dictionaries.
            dataStr = cls.convertDictToPrintStr(value,'',True,multiLine,rndOff,offset+2)

         elif type(value) == str:
            dataStr = "'" + str(value) + "'"  # Just dump the data as is.

         # Catch everything else.
         else:
            dataStr = str(value)  # Just dump the data as is.

         # Format the data and add it to the accumulating output string.
         if justify:
            # str(key) in case key is not already a string, it could be a tuple for instance.
            outStr += '\t'*offset + str(key).ljust(maxWidth+1) + separator + dataStr + newLine
         else:
            outStr += '\t'*offset + str(key) + ':' + dataStr + newLine

      # Clean up the end of the string if necessary.
      if multiLine != True:
         outStr = outStr.rstrip(', ') + '}'

      elif offset != 0:
         # This is clean up for nested dictionaries, (offset != 0), newlines should not be printed.
         outStr = outStr.rstrip('\n')

      return outStr

   @staticmethod
   def beval(condition, retIfTrue, retIfFalse):
      if condition:
         return retIfTrue
      else:
         return retIfFalse

   if testSwitch.FE_0121886_231166_FULL_SUN_MODEL_NUM:
      @staticmethod
      def getRegex(inputValue, regexDict):
         """
         Function searches the keys which are regex for the inputValue if found returns value at key
            Returns: None if not found
         """
         import re
         for key in regexDict:
            if re.search(key, inputValue):
               #found match
               return regexDict[key]
         return None #not found

   #------------------------------------------------------------------------------------------------------#
   @staticmethod
   def strSwap(str, stripWhitespace = True):
      """
         Utility used in parsing IdentifyDevice data
       """

      strLen=len(str)

      retStr  = ''

      if strLen%2 == 0:
         for i in range(0,strLen,2):
            retStr = retStr + str[i+1] + str[i]
      if stripWhitespace:
         retStr = retStr.strip()
      return retStr

   @staticmethod
   def numSwap(str):
      """
         Utility used in parsing IdentifyDevice data
       """
      strLen=len(str)
      num = 0
      if strLen <= 5:
         for i in range(0,strLen):
            num = num + (ord(str[i])<<(i*8))
      else:
         num = None
      return num

   @staticmethod
   def strBufferToBinString(buff):
      d2 = ''
      for d in xrange(0,len(buff), 2):
         d2+=chr(int(buff[d:d+2],16))
      return d2

   @staticmethod
   def byteSwap(inputArray):
      out = []
      for x in xrange(0, len(inputArray), 2):
         try:
            out.append(inputArray[x+1])
         except IndexError:
            out.append(0)
         out.append(inputArray[x])
      return out


   @classmethod
   def filterDictByKey(cls, theDict, keys, keyAction):
      """
      keys : list of keys
      keyAction is "keep" (keep only specified keys)
      or "toss" (toss only specified keys)
      filter out keys at the end of tree of dicts.
      """
      if keyAction not in ("keep", "toss",):
         ScrCmds.raiseException(11044, "Invalid keyAction: %s" % keyAction)
      for k, v in theDict.items():
         if type(v) == type({}):
            theDict[k] = cls.filterDictByKey(v, keys = keys, keyAction = keyAction)
         else:
            if k in keys:
               if keyAction == "toss":
                  theDict.pop(k)
            elif keyAction == "keep":
               theDict.pop(k)
      return theDict

   @classmethod
   def operateOnDictVals(cls, theDict, funcPtr, conditionFuncPtr = None):
      """
      val = funcPtr(val) for every val at the end of tree of dicts, if conditionFuncPtr(k,v) == True
      ex: operateOnDictVals(aDict, lambda x : int(x, 16),) to convert str to int
      ex: operateOnDictVals(aDict, lambda x : x + 4,) to increment by 4
      ex: operateOnDictVals(aDict, lambda x : x + 4, lambda k, v: k == "WrCur") to increment by 4, if key == WrCur
      """
      for k, v in theDict.items():
         if type(v) == type({}):
            theDict[k] = cls.operateOnDictVals(v, funcPtr, conditionFuncPtr)
         elif conditionFuncPtr == None or conditionFuncPtr(k,v):
            theDict[k] = funcPtr(v)
      return theDict

   @staticmethod
   def combineListOfHeadZoneDicts(listOfDicts, imaxHead, numZones):
      """
      Combine list of aDict[head][zone] type dicts
      {0: {0: {'WrCur': 9, 'WrDamp': 2,},
           1: {'WrCur': A',}, ....
      Eavch dict in list is assumed to have entry for every head/zone
      """
      returnDict = listOfDicts[0]
      for d in listOfDicts[1:]:
         [[returnDict[head][zone].update(d[head][zone]) for head in xrange(imaxHead) for zone in xrange(numZones)]]
      return returnDict


   @staticmethod
   def getCodeVersion( fileName ):
      import MessageHandler as objMsg
      import os, ScrCmds, re

      # A method to get the version of fileName
      if testSwitch.winFOF == 1:
         if os.path.exists( fileName ) == True:
            validFileName = fileName
         else:
            if os.path.exists( '..\scripts\%s' % ( fileName ) ) == True:
               validFileName = '..\scripts\%s' % ( fileName )
            else:
               if os.path.exists( '..\..\scripts\%s' % ( fileName ) ) == True:
                  validFileName = '..\..\scripts\%s' % ( fileName )
               else:
                  objMsg.printMsg('Failed to find %s to extract revision number' % ( fileName ), objMsg.CMessLvl.CRITICAL)
                  return -1
      else:
         if os.path.exists( ScrCmds.getSystemScriptsPath() + os.sep + fileName ) == True:
            validFileName = ScrCmds.getSystemScriptsPath() + os.sep + fileName
         else:
            objMsg.printMsg('Failed to find %s to extract revision number' % ( fileName ), objMsg.CMessLvl.CRITICAL)
            return -1

      fileObj = open(validFileName, 'r')


      revision = -1
      reg1 = '^(.?){0,100}(Revision: #)(?P<revision>([0-9]{1,6}))'

      iter_tmp = 0
      b = None
      reObj = re.compile(reg1)

      while (iter_tmp < 10) and (b == None):
         iter_tmp += 1
         b = reObj.search(fileObj.readline())

         if b != None:
            revision = b.group('revision')

      fileObj.close()
      objMsg.printMsg("%s revision: %s" % ( validFileName, revision), objMsg.CMessLvl.IMPORTANT)
      return(int(revision))

   @staticmethod
   def invertDict( inDict ):
      """
      Returns an inverted dictionary. Where key:val becomes val:key
         The with this transformation val,key alphabetic overwrites will occur if there are multiple val items in the dict
         The items are sorted by val prior to dict creation so the overwrite should be re-producable.
      """
      return dict(sorted([(val,key) for key,val in inDict.items()]))

   @staticmethod
   def intToOnesMask(val):
      """
      Converts an integer to a mask which, in binary, is the number of ones of the integer.
      Eg:
         0b11111 = intToOnesMask(5)
      """
      return ( 2 ** val ) - 1

   @staticmethod
   def stripBrackets(inStr):
      return inStr.strip('[]')

   @staticmethod
   def bracketize(inStr, width):
      fmtSpec = '[%-' + '%d' % width + 's]'
      return fmtSpec %  (inStr,)

   @staticmethod
   def mask_16bit(val):
      """ Converts signed to unsigned short integer. Mimics ctypes.c_uint16(val).value """
      return 0xffff & val


#import MessageHandler as objMsg
import traceback
class executionState:
   @staticmethod
   def save(dut, value=-1, level=0):
      tb = traceback.extract_stack()[-2+level]
      key = tb[0]+'_'+tb[2]
      if value < 0:
         current = tb[1]
      else:
         current = value
      state = dut.objData.get('EXEC_STATE', {})
      saved, count = state.get(key, (0, 1))
      #objMsg.printMsg("executionState save: current %d; saved %d" % (current, saved))
      if current == saved:
         count += 1
      else:
         count = 1
      state[key] = (current, count)
      dut.objData['EXEC_STATE'] = state
      #objMsg.printMsg("executionState save: %s, %d, x%d" % (key, current, count))
      
   @staticmethod
   def getLast(dut, level=0):
      tb = traceback.extract_stack()[-2+level]
      key = tb[0]+'_'+tb[2]
      state = dut.objData.get('EXEC_STATE', {})
      saved, count = state.get(key, (0, 1))
      #objMsg.printMsg("executionState load: %s, %d, x%d" % (key, saved, count))
      return state.get(key, (0, 1))
      
   @staticmethod
   def get(dut, level=0):
      tb = traceback.extract_stack()[-2+level]
      return tb[1]

def convertItemsToNumbers( inputList, base = 10):
   """
   Creates a copy of the simple input list and
      converts the list items that are base integers as strings
      to base int types.
   """

   inputList = list(inputList) #Create a copy and force to list in-case was tuple

   for index, item in enumerate(inputList):
      try:
         item = int(item, base)
         inputList[index] = item #if it was an int update the list
      except ValueError:
         #if it wasn't a base10 int
         continue

   return inputList




def factorial(n):
   #returns the factorial of the whole integer input n
   if n == 1:
      return n
   else:
      return n * factorial(n-1)

class permutations(object):
   """
   Generator object to return all (ordered) permutations of the input set
   """
   def __init__(self, *args):
      self.permutVals = list(args)
      self.master = []
      self.level = 0

      #allow list inputs or arguments to be input
      if len(args) == 1:
         if type(args[0]) in (tuple, list):
            self.permutVals = args[0]
         else:
            self.permutVals = [args[0],]



   def __iter__(self):

      self.level = 0
      Value = list(self.permutVals)
      N = len(self.permutVals)
      #self.makeFactorialSets(indicies, len(self.permutVals)-1, 0)
      yield Value
      for index in xrange(factorial(N)-1):
         i = N-1 #counter

         def swap(a, b):
            t = Value[b]
            Value[b] = Value[a]
            Value[a] = t

         while (Value[i-1] >= Value[i]):
            i = i-1

         j = N

         while (Value[j-1] <= Value[i-1]):
            j = j-1

         # swap values at positions (i-1) and (j-1)
         swap(i-1, j-1)
         i += 1
         j = N
         while (i < j):
            swap(i-1, j-1)
            i += 1
            j -=1

         yield Value

      raise StopIteration





class xmlHelper:
   def __init__(self):
      pass
   def tagWrap(self,tag, val):
      return self.startTag(tag) + str(val) + self.endTag(tag)

   def startTag(self,input):
      return "<" + str(input) + ">"

   def endTag(self,input):
      return "</" + str(input) + ">"

   def dictToXML(self,inDict):
      outStr = ''
      for key,val in inDict.items():
         outStr += str(self.tagWrap(key,val))
      return outStr

   def xmlHeader(self, version = 1.0):
      if version == 1.0:
         header = '<?xml version="1.0"?>'
      else:
         header = 'Unavailable'
      return header

class resObj(xmlHelper):
   nameTag = 'REGRESULT'
   snTag = 'SERIAL_NUM'
   changeListTag = 'CHNGLIST'
   operTag = 'OPERATION'
   resTag = 'RESULT'
   traceTag = 'TRACEBACK'

   def __init__(self, serialNum, changeList, operation, result, traceback = ''):
      xmlHelper.__init__(self)
      self.serialNum = serialNum
      self.changeList = str(changeList)
      self.result = result
      self.operation = operation
      self.traceback = traceback
      self.traceback =self.traceback.replace('>','').replace('<','')

   def __str__(self):
      out = ''
      out = self.tagWrap(self.nameTag,
                         self.tagWrap(self.snTag,self.serialNum) +
                         self.tagWrap(self.changeListTag, self.changeList) +
                         self.tagWrap(self.operTag,self.operation) +
                         self.tagWrap(self.resTag,self.result) +
                         self.tagWrap(self.traceTag, self.traceback)
                        )
      return out

   def __repr__(self):
      out = self.__str__()
      return out

   def fname(self):
      return self.serialNum + "_" + self.operation + "_" + self.changeList + ".XML"

def getSortedRegexMatch( matchString, reOptions):
   """
   Returns a single resultant type based on the item type of the values of reOptions.
      The precidence for replacement is that the longest match of the re is used as the value in
      the result.
   """
   matches = []

   #Look for a simple regex match last...
   for tempPnMatch in reOptions:
      #Force a fully matched PN
      pnMatch = tempPnMatch
      try:

         regVal = re.compile(pnMatch)
      except re.error:
         objMsg.printMsg("Script Error in resolving regex for %s" % pnMatch)
         continue
      mMatch = regVal.search(matchString)
      if mMatch:
         matches.append((mMatch,reOptions[tempPnMatch]))

   oSpan = [(eval("mat.span()[1]"),pn) for mat,pn in matches]
   oSpan.sort()

   evalType = type(oSpan[0][1])
   if evalType == types.ListType:
      #item is [matchLen, []]
      retval = []
      for span, value in oSpan:
         retval.extend(value)
      retval = list(set(retval))

   elif evalType == types.DictType:
      #item is [matchLen, {}]
      retval = {}
      for span, value in oSpan:
         retval.update(value)
   else:
      ScrCmds.raiseException(11044, "Unknown resolution type for getSortedRegexMatch = %s" % evalType)

   return retval

def convertCmsWildCardToRe(inVal):
   """
   % is the wildcard for CMS but re requires a different syntax for python
   """
   return inVal.replace("%", "\S+")
   
def getPrintDbgMsgFunction():
   def __dummyFunc(*args, **kwargs): pass
   if testSwitch.CM_REDUCTION_REDUCE_PRINTMSG:
      return __dummyFunc
   else:
      import MessageHandler as objMsg
      return objMsg.printMsg

def getVBARPrintDbgMsgFunction():
   def __dummyFunc(*args, **kwargs): pass
   if testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_VBAR_MSG:
      return __dummyFunc
   else:
      import MessageHandler as objMsg
      return objMsg.printMsg
   
def getTripletPrintDbgMsgFunction():
   def __dummyFunc(*args, **kwargs): pass
   if testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_TRIPLET_MSG:
      return __dummyFunc
   else:
      import MessageHandler as objMsg
      return objMsg.printMsg
   
def getChannelPrintDbgMsgFunction():
   def __dummyFunc(*args, **kwargs): pass
   if testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_CHANNEL_MSG:
      return __dummyFunc
   else:
      import MessageHandler as objMsg
      return objMsg.printMsg
   
if __name__ == "__main__":
   """
   Copy test code
   """
   m  = [[0], 50, [1, 2, 3]]
   j = {1:2,3:4,5:[3,5,3]}
   oUt = CUtility()
   print("Initial")
   print("m = %s" % str(m))
   print("j = %s" % str(j))
   print("------")
   print("Copy m->p; j->v")
   p = oUt.copy(m)
   v = oUt.copy(j)
   print("Modify m & j")
   m[1] = 100
   j.update({1:100,5:[3,100,3]})
   print("------")

   print("m and p should not equal")
   print("m = %s" % str(m))
   print("p = %s" % str(p))
   print("v and j should not equal")
   print("j = %s" % str(j))
   print("v = %s" % str(v))

#----------------------------------------------------------------------------
# "all" built-in function is not supported until Python 2.7.
# Older version of Python require the try/except.
# Definition: Return True if all elements of the iterable are true (or if the iterable is empty).
try:
   all = all  # Python 2.5 introduce this
except NameError:
   def all(iterable):
      for element in iterable:
         if not element:
            return False
      return True

#----------------------------------------------------------------------------
# "any" built-in function is not supported until Python 2.7.
# Older version of Python require the try/except.
# Definition: Return True if any element of the iterable is true. If the iterable is empty, return False
try:
   any = any
except NameError:
   def any(iterable):
      for element in iterable:
         if element:
            return True
      return False

