#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# $RCSfile: IntfClass.py,v $
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/IOEDC.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/IOEDC.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from Drive import objDut

import ScrCmds, struct
from Cell import theCell
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
from Exceptions import CRaiseException

import binascii, re, traceback, time
from ICmdFactory import ICmd
from Rim import objRimType


IOEDCErrorIncr = 'IOEDC Incremented'
IOEDCErrorUnRd = 'IOEDC Unreadable'
IOEDCErrorRdStsBad = 'IOEDC Readable Status Bad'
IOEDCErrorMaximumCount = "Maximum IOEDC count exceeded"
IOEDCUnsupported = 'IOEDC Unsupported'

#------------------------------------------------------------------
class ChkIOEDC(object):


   def __init__( self, ):
      self.dut = objDut
      self.attrNum = 0xB8
      self.IOEDCValues={'Current': 0, 'New':0}
      self.DescriptionofError = IOEDCErrorIncr
      self.error = False

      #Determine if IOEDC enabled
      self.IOEDCEnabled = self.Is_IOEDC()

      if self.IOEDCEnabled:
         self.IOEDCValues['Current']= self.ReadSmartAttrIOEDC()
         objMsg.printMsg("IOEDC Current Value: %s"%`self.IOEDCValues['Current']`)
      else:
         objMsg.printMsg(IOEDCUnsupported)
         self.DescriptionofError = IOEDCUnsupported


   def Is_IOEDC(self):
      '''Checking for IOEDC support'''

      IOEDCEnabled = False
      if objRimType.IOInitRiser():
         if testSwitch.BF_0124866_231166_FIX_IOEDC_ATTR_RETR:
            testSwitch.useASCII_IOEDC_CMD = 1
         else:
            return True

      if not testSwitch.useASCII_IOEDC_CMD:
         try:
            import sdbpCmds
            ret = sdbpCmds.getDriveBasicInformation()
            IOEDCEnabled = bool(ret.get('IoedcEnabled',0))
         except:
            objMsg.printMsg("Error during sdbp command for IOEDC detection: %s" % (traceback.format_exc(),))
            testSwitch.useASCII_IOEDC_CMD = True #try the diag version

      if testSwitch.useASCII_IOEDC_CMD:
         import sptCmds
         for retry in xrange(3):
            try:
               sptCmds.enableDiags()
               break
            except:
               objPwrCtrl.powerCycle()
         else:
            IOEDCEnabled = False

         if not testSwitch.BF_0124866_231166_FIX_IOEDC_ATTR_RETR:
            data = sptCmds.sendDiagCmd(CTRL_L,timeout = 5, altPattern="IOEDC", printResult = False, Ptype='PChar', raiseException = 0)

            if data.find('IOEDC enabled') > -1:
               IOEDCEnabled = True
            else:
               IOEDCEnabled = False
         else:
            try:
               data = sptCmds.sendDiagCmd(CTRL_L,timeout = 10, altPattern="IOEDC enabled", printResult = False, Ptype='PChar', raiseException = 1, loopSleepTime= 0)

               IOEDCEnabled = True
            except CRaiseException:
               IOEDCEnabled = False

         sptCmds.enableESLIP(suppressExitErrorDump = False)

      theCell.disableESlip()

      return IOEDCEnabled

   #------------------------------------------------------------------
   def checkIOEDC( self, data={}, maximumCount = -1):
      """Checks if IOEDC has been incremented
         returns False if hasn't been and True if has been and class stores error message
      """

      if not self.IOEDCEnabled:
         objMsg.printMsg(IOEDCUnsupported)
         self.error = True
         self.DescriptionofError = IOEDCErrorRdStsBad
         return self.error

      if data.get( 'RESULT', '' ) in ['AAU_MISCOMPARE','AAU_BITMISCOMPARE']:
         self.error = True
         return self.error

      self.error, retries, retryCnt = False,0,2

      commandStatus = int( data.get( 'STS', '80' ), 10 )

      if not commandStatus & 0x50: #Get completion status
         objPwrCtrl.powerCycle()
         ICmd.SmartEnableOper(exc=1)


      while retries <= retryCnt:
         self.IOEDCValues['New'] = self.ReadSmartAttrIOEDC()
         if self.IOEDCValues['New'] > -1:
            break
         retries +=1
      else:
         self.error = True
         self.DescriptionofError = IOEDCErrorRdStsBad
         return self.error

      objMsg.printMsg("IOEDC Values: %s"%`self.IOEDCValues`)

      if self.IOEDCValues['Current'] != self.IOEDCValues['New']:
         self.error = False
         self.DescriptionofError = IOEDCErrorIncr
      else:
         if not commandStatus & 0x50:
            self.DescriptionofError = IOEDCErrorRdStsBad
         else:
            self.IOEDCValues['Current'] = self.IOEDCValues['New']

      if maximumCount > -1 and self.IOEDCValues.get('New',0) > maximumCount:
         self.DescriptionofError = IOEDCErrorMaximumCount
         self.error = True

      return self.error

   #------------------------------------------------------------------
   @staticmethod
   def ReadSmartAttrIOEDC(attrNum = 0xB8 ):

      attrValue,attrOffset,attrsize,bytes = -1,2,12, 0
      #the attribute sector attribute secion is an array [currently 30 members]
      # of attribute structs defined as per below in core.h in F3 code
      # we pull the raw value for this IOEDC analysis
      """
         typedef struct attribute
         {
            // AttributeNum is the number of the attribute.
            uint8 AttributeNum;              //[u8]

            // FlagsLow is the low byte of the attribute flags.
            uint8 FlagsLow;                  //[u8]

            // FlagsHigh is the high byte of the attribute flags.
            uint8 FlagsHigh;                 //[u8]

            // Normalized is the scaled value of the attribute.
            uint8 Normalized;                //[u8]

            // WorstEver is the worst value yet seen.
            uint8 WorstEver;                 //[u8]

            // Raw is unscaled attribute data.
            uint8 Raw[7];                    //[u8,7]

         } attribute;

         RAW[0] and RAW[1] hold the current new count
      """

      if testSwitch.BF_0124866_231166_FIX_IOEDC_ATTR_RETR:
         AttributeNum = 0
         RawPtr = 5
         attrFmt = 'BBBBB7s'
         attrSize = struct.calcsize(attrFmt)
      else:
         for retry in xrange(3):
            try:
               ICmd.SmartEnableOper(exc=1)
               break
            except:
               ICmd.HardReset(exc=0)
               time.sleep(2)
               ICmd.IdentifyDevice(exc=0)
         else:
            raise

      sctr = ICmd.SmartReadData(exc=1)

      data = ICmd.GetBuffer(RBF, 0, 512)
      sctr = data.get('DATA','')#sctr['GETBUFFER']

      if testSwitch.virtualRun:
         return 0

      if testSwitch.BF_0124866_231166_FIX_IOEDC_ATTR_RETR:
         if sctr:
            for bytes in xrange(attrOffset,362,attrsize):
               attribute = struct.unpack(attrFmt, sctr[bytes:bytes+attrSize])
               if attribute[AttributeNum] == attrNum:

                  #Can't unpack 7 bytes so pad the extra value
                  normalized = attribute[RawPtr][0:struct.calcsize('>H')]
                  attrValue =struct.unpack('>H',normalized)[0]

                  break
      else:
         if sctr:
            sctr = re.findall( '[0-9-A-F-a-f]{2}',binascii.hexlify( sctr ) )
         if sctr:
            for bytes in xrange(attrOffset,362,attrsize):
               if int(sctr[bytes],16) == attrNum:
                  attrValue = int(''.join(sctr[bytes+5:bytes+5+6]), 16 )
                  break

      if attrValue == -1:
         objMsg.printMsg( "Unable to find IOEDC Attribute (0xB8) in the Log"  )
         objMsg.printMsg( "Buffer data" )
         objMsg.printBin(sctr)

      return attrValue

   #------------------------------------------------------------------
   def ParseErrorAndAssignCode(self, dictResult={}):
      ResultDictionary=\
         {
            'AAU_BITMISCOMPARE':'Cit SingleBitMis MIS1',     #Single Bit Miscompare MIS2
            'AAU_MISCOMPARE':'Cit MultiBitMis MIS2',         #Byte or Multi Byte Miscompare MIS1
         }

      if DEBUG > 0:
         objMsg.printMsg( "Recvd Dictionary for parsing: %s"%`dictResult` )

      CommandStatus= int( dictResult.get( 'STS', '81' ), 10 )
      ResultString = dictResult.get( 'RESULT', 'No Result Reported' ).split(':')[0]
      IOEDCResultString = self.DescriptionofError

      try:
         # Command Status where error bit is set
         if CommandStatus & 0x0001 or not (CommandStatus&0x50):
            if IOEDCResultString:
               ScrCmds.raiseException(12719)
            else:
               ScrCmds.raiseException(12720)

         # Command Status where error bit is not set
         elif not ( CommandStatus & 0x0001 ) or CommandStatus&0x50:
            if ResultString in ResultDictionary.keys(): #Take Care of MIS1 and MIS2
               ScrCmds.raiseException(12525, ResultDictionary[ResultString])
            else: #special case
               if IOEDCResultString in [IOEDCErrorIncr,] :
                  ScrCmds.raiseException(12718)
               elif IOEDCResultString in [IOEDCErrorRdStsBad,]:
                  ScrCmds.raiseException(12721)
               else:
                  msg = "Unable To find Fail Code for %s result" % IOEDCResultString
                  objMsg.printMsg( msg)
                  ScrCmds.raiseException(12525, msg)
         if IOEDCResultString in [IOEDCErrorRdStsBad, ]:
            ScrCmds.raiseException(12720)
         if ResultString in [ 'IEK_OK:No error', ] and int( dictResult.get( 'ERR_CNT' , '0' ) ) > 0:
            ScrCmds.raiseException(12720)
         if IOEDCResultString in [IOEDCErrorMaximumCount,]:
            ScrCmds.raiseException(12525, IOEDCErrorMaximumCount)

      except:
         objMsg.printMsg( "CIT Failed: %s-%s"%(ResultString, IOEDCResultString ) )
         raise

      return True
