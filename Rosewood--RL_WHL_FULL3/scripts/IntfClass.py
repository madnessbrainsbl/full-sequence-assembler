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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/IntfClass.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/IntfClass.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import ScrCmds, re
from Rim import objRimType
import MessageHandler as objMsg
from Drive import objDut   # usage is objDut
from TestParamExtractor import TP
import binascii
import struct
import time
import PIF

from ICmdFactory import ICmd
from Utility import CUtility

DEBUG = 0

def HardReset(exc = 1):
   return ICmd.HardReset()

###########################################################################################################
###########################################################################################################
class CIdentifyDevice(object):
   """
      Determine device settings with Identify Device Command
   """
   instance = None                                       
   def __new__(self, *args, **kwargs):         
      if self.instance is None:
         self.instance = object.__new__(self, *args, **kwargs)      
         self.IdentifyDevice = None                # Create single instance for IdentifyDevice
      return self.instance   
   
   def __init__(self, refreshBuffer = True, force = True, sp_force = True):
      if self.IdentifyDevice is None or force or sp_force:
         from Drive import objDut
         self.dut = objDut
   
         if (sp_force):
            ICmd.ClearIdentBuffer()
         self.ID = ICmd.IdentifyDevice()
         self.setMultiMode = 8
         if self.ID['LLRET'] != OK:
            ScrCmds.raiseException(13420, "IdentifyDevice failed %s" % str(self.ID))
         else:
            objMsg.printMsg("Identify Device passed")
   
         self.__GB = ICmd.GetIdentifyBuffer()
   
   
         if self.__GB['LLRET'] != OK:
            ScrCmds.raiseException(13423, 'Read buffer failed %s' % str(self.__GB))
         else:
            objMsg.printMsg("Get Buffer passed")
   
         self.__parseBuffer(refreshBuffer)
         objMsg.printMsg("Identify Device buffer parsed %s" % str(self.ID))
   
         self.dut.IdDevice["Mid Cyl"] = (int) (self.ID['IDLogicalCyls'] / 2)
         self.dut.IdDevice["Max Cyl"] = self.ID['IDLogicalCyls'] - 1
         self.dut.IdDevice["LCyl"] = self.ID['IDLogicalCyls']
         self.dut.IdDevice["LHeads"] = self.ID['IDLogicalHeads']
         self.dut.IdDevice["LSectors"] = self.ID['IDLogicalSctrs']
         self.dut.IdDevice["Mid LBA"] = self.ID['IDDefaultLBAs'] / 2
         self.dut.IdDevice["Max LBA"] = self.ID['IDDefaultLBAs'] - 1
         self.dut.IdDevice["Max LBA Ext"] = self.ID['IDDefault48bitLBAs'] - 1
         self.dut.IdDevice["SATA Ver"] = self.ID['SATACapabilities']

         if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
            self.dut.IdDevice["IDSeaCosFDE"] = not ((self.ID['IDSeaCosFDE'] & 0X1010) ^ 0X1010)
            self.dut.IdDevice["FDE"] = (self.ID['IDReserved48'] & 0X4001) == 0x4001
         else:
            self.dut.IdDevice["FDE"] = not ((self.ID['FDE'] & 0X1010) ^ 0X1010)

         #Or with SDnD bit
         self.dut.IdDevice['FDE'] |= ( ( self.ID['IDReserved155'] & 0x8000 ) == 0x8000 )
         self.dut.IdDevice['IDModel'] = self.ID['IDModel']
         self.dut.IdDevice['IDSerialNumber'] = self.ID['IDSerialNumber']
         self.dut.IdDevice['ZGS'] = ( self.ID['IDCommandSet7'] & 0x20 ) >> 4
         self.dut.IdDevice['Physical Sector Size'],self.dut.IdDevice['Logical Sector Size'] = self.determineSectorSize()
         self.dut.IdDevice['UDMA Mode Supported'] = self.determineUDMAmode()
         self.dut.sptActive.setMode(self.dut.sptActive.availModes.intBase)
         
         self.IdentifyDevice = True
      else:
         objMsg.printMsg("Device already identified.")

   #-------------------------------------------------------------------------------------------------------
   def run(self):
#CHOOI-18May17 OffSpec
#      self.check_dutID_syID()
      self.Is_FDE()

   #------------------------------------------------------------------------------------------------------#
   def __numSwap(self, str):
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

   #------------------------------------------------------------------------------------------------------#
   def __strSwap(self, str , stripWhitespace = True):
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
   #------------------------------------------------------------------------------------------------------#
   def __parseBuffer(self, refreshBuffer):
      """
         Parse the data and place into dictionary
      """
      from FSO import WorldWideName as WWN

      data = self.__GB['DATA']   #  Get the data

      self.ID['LLRET'] = 0     #  Store the Low Level Return
      self.ID['IDConfiguration'    ] = self.__numSwap(data[  0:  2])
      self.ID['IDLogicalCyls'      ] = self.__numSwap(data[  2:  4])
      self.ID['IDReserved2'        ] = self.__numSwap(data[  4:  6])
      self.ID['IDLogicalHeads'     ] = self.__numSwap(data[  6:  8])
      self.ID['IDObsolete4'        ] = self.__numSwap(data[  8: 10])
      self.ID['IDObsolete5'        ] = self.__numSwap(data[ 10: 12])
      self.ID['IDLogicalSctrs'     ] = self.__numSwap(data[ 12: 14])
      self.ID['IDVendorUnique7'    ] = self.__numSwap(data[ 14: 16])
      self.ID['IDVendorUnique8'    ] = self.__numSwap(data[ 16: 18])
      self.ID['IDVendorUnique9'    ] = self.__numSwap(data[ 18: 20])
      if (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()) or objRimType.IOInitRiser():
         if testSwitch.BF_0151846_231166_P_SUPPORT_PN_BASED_SN_FIELD:
            self.ID['IDSerialNumber'     ] = ICmd.GetDriveSN(self.dut.partNum)
         else:
            self.ID['IDSerialNumber'     ] = ICmd.GetDriveSN()
      else:
         self.ID['IDSerialNumber'     ] = self.__strSwap(data[ 20: 40])
      self.ID['IDObsolete20'       ] = self.__numSwap(data[ 40: 42])
      self.ID['IDObsolete21'       ] = self.__numSwap(data[ 42: 44])
      self.ID['IDRWLongVendorBytes'] = self.__numSwap(data[ 44: 46])
      self.ID['IDFirmwareRev'      ] = self.__strSwap(data[ 46: 54])
      if (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()) or objRimType.IOInitRiser():
         if testSwitch.FE_0144401_231166_P_SUPPORT_VEND_CMD_SEP:

            useVendorField = (re.search( getattr(PIF,  'PN_USE_VEND_FIELD',  '!.*'), self.dut.partNum) != None )

            self.ID['IDModel'            ] = ICmd.GetModelNum(useVendorField = useVendorField, refreshBuffer=refreshBuffer)
         else:
            self.ID['IDModel'            ] = ICmd.GetModelNum(refreshBuffer=refreshBuffer)

         if testSwitch.NoIO or testSwitch.FE_0121886_231166_FULL_SUN_MODEL_NUM:
            self.ID['IDModel'            ] = self.ID['IDModel'].strip()


      else:
         if testSwitch.FE_0121886_231166_FULL_SUN_MODEL_NUM:
            self.ID['IDModel'            ] = self.__strSwap(data[ 54: 94], stripWhitespace = False)
         else:
            self.ID['IDModel'            ] = self.__strSwap(data[ 54: 94])
      self.ID['IDRWMultIntrPerSctr'] = self.__numSwap(data[ 94: 96])
      self.ID['IDReserved48'       ] = self.__numSwap(data[ 96: 98])
      self.ID['IDCapabilities'     ] = self.__numSwap(data[ 98:100])
      self.ID['IDReserved50'       ] = self.__numSwap(data[100:102])
      self.ID['IDPIOTransTime'     ] = self.__numSwap(data[102:104])
      self.ID['IDVendorUnique52'   ] = self.__numSwap(data[104:106])
      self.ID['IDCurParmsValid'    ] = self.__numSwap(data[106:108])
      self.ID['IDCurLogicalCyls'   ] = self.__numSwap(data[108:110])
      self.ID['IDCurLogicalHds'    ] = self.__numSwap(data[110:112])
      self.ID['IDCurLogicalSctrs'  ] = self.__numSwap(data[112:114])

      self.ID['IDMultipleSctrs'    ] = self.__numSwap(data[118:120])

      if (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()) or objRimType.IOInitRiser():
         mxLBA = ICmd.GetMaxLBA(refreshBuffer=refreshBuffer)
         self.ID['IDDefaultLBAs'      ] = int(mxLBA['MAX28'],16)
         self.ID['IDCurLBAs'          ] = int(mxLBA['MAX28'],16)
         self.ID['IDDefault48bitLBAs' ] = int(mxLBA['MAX48'],16)
         del mxLBA
      else:
         self.ID['IDDefault48bitLBAs' ] = self.__numSwap(data[200:205]) #48bit ATA8
         self.ID['IDDefaultLBAs'      ] = self.__numSwap(data[120:124]) #non extended ATA8
         self.ID['IDCurLBAs'          ] = self.__numSwap(data[114:118]) # 28bit ATA8
      self.ID['IDAddSupported'     ] = self.__numSwap(data[138:140])    # Word 69, bit 4. SED or Sagemcom.
      self.ID['SATACapabilities'   ] = self.__numSwap(data[152:154])
      self.ID['IDATAATAPIMajorVer' ] = self.__numSwap(data[160:162])
      self.ID['IDATAATAPIMinorVer' ] = self.__numSwap(data[162:164])
      self.ID['IDCommandSet1'      ] = self.__numSwap(data[164:166])
      self.ID['IDCommandSet2'      ] = self.__numSwap(data[166:168])
      self.ID['IDCommandSet3'      ] = self.__numSwap(data[168:170])
      self.ID['IDCommandSet4'      ] = self.__numSwap(data[170:172])
      self.ID['IDCommandSet5'      ] = self.__numSwap(data[172:174])
      self.ID['IDCommandSet6'      ] = self.__numSwap(data[174:176])
      self.ID['IDUDMASupportedMode'] = self.__numSwap(data[176:178])
      self.ID['IDCurrAPMValue'     ] = self.__numSwap(data[182:184])
      self.ID['IDHardwareResetRes' ] = self.__numSwap(data[186:188])

      self.ID['IDWorldWideName'    ] = WWN().id(data[216:224])
      self.ID['ExtendedPowerCond'  ] = self.__numSwap(data[238:240])
      self.ID['IDCommandSet7'      ] = self.__numSwap(data[238:240])                      # Bit 5 = Zero Gravity Sensor
      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
         self.ID['IDSeaCosFDE'        ] = self.__numSwap(data[300:302])

      self.ID['FDE'                ] = self.__numSwap(data[300:302])
      self.ID['SCTBIST_Supported'  ] = self.__numSwap(data[412:414])                     # Word 206 bit 7
      self.ID['ATASignalSpeedSupport'] = self.__numSwap(data[152:154])                    # Word 76 bit 1-2
      self.ID['ATA_SignalSpeed'    ] = self.__numSwap(data[154:156])                      # Word 77 bit 0-3
      self.ID['DrivePairing'       ] = self.__numSwap(data[312:314])                      # Word 156
      self.ID['LPS_LogEnabled'     ] = (self.__numSwap(data[318:319]) & 0x400) == 0x400   # Word 159 bit 10
      self.ID['RMW_LogEnabled'     ] = (self.__numSwap(data[318:319]) & 0x200) == 0x200   # Word 159 bit 9
      self.ID['IDReserved159'      ] = self.__numSwap(data[318:320]) #word 159
      self.ID['POIS_Supported'     ] = self.__numSwap(data[166:168])                      # Word 83 bit 5
      self.ID['POIS_Enabled'       ] = self.__numSwap(data[172:174])                      # Word 86 bit 5
      self.ID['LogToPhysSectorSize'] = self.__numSwap(data[212:214])                      # Word 106
      self.ID['LogicalSectorSize'  ] = self.__numSwap(data[234:238])                      # Word 117-118 Only populated if size greater than 512
      self.ID['IDReserved155'      ] = self.__numSwap(data[310:312])                      # Word 155 bit 15 indicates if SDnD
      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
         self.ID['IDReserved243'      ] = self.__numSwap(data[486:488])                   # Word 243 for TCG
      self.ID['MediaCacheEnabled'  ] = self.__numSwap(data[318:320]) #word 159 bit 6, value of 1 indicate MC on and value of 0 indicate MC off
      self.ID['MediaCacheSupport'  ] = self.__numSwap(data[412:414]) #word 206 SCTFeaturesEnabled bit 13=MC access via SCT is supported. 1=supported; 0=unsupported

      # from IOMQM
      self.ID['IDQDepth'           ] = self.__numSwap(data[150:152])    # DT word 75 QDepth
      self.ID['IDSATACapabilities' ] = self.__numSwap(data[152:154])
      self.ID['IDSeaCOSCmdsSupport'] = self.__numSwap(data[300:302])    # DT
      self.ID['IDMediaCacheEnabled'] = self.__numSwap(data[318:320])    # DT word 159 Media Cache
      self.ID['IDLogSectPerPhySect'] = self.__numSwap(data[212:214])    # DT
      self.ID['IDLogInPhyIndex'    ] = self.__numSwap(data[418:420])    # DT word 209    

   #------------------------------------------------------------------------------------------------------#
   def check_dutID_syID(self):
      """
         Parse the data and place into dictionary
      """
      data = {'LLRET':OK}

      ID_CheckList = [self.ID['IDSerialNumber']]
      Sy_CheckList = [self.dut.serialnum]

      if len(ID_CheckList) != len(ID_CheckList):
         data = {'LLRET':-1}

      if testSwitch.virtualRun:
         ID_CheckList = Sy_CheckList

      if data['LLRET'] == OK and not testSwitch.FE_0145180_357260_P_BROKER_PROCESS:
         for i in range(len(ID_CheckList)):
            if ID_CheckList[i] != Sy_CheckList[i]:
               objMsg.printMsg('ID: %s != SYS: %s' % (ID_CheckList[i], Sy_CheckList[i]))
               if ConfigVars[CN].get('BenchTop',0):
                  objMsg.printMsg("Warning: IdentifyDevice SerialNum mismatch!")
               else:
                  self.dut.driveattr['MISMATCH'] = ID_CheckList[i]
                  RequestService("SetDriveSN", ID_CheckList[i])
                  objMsg.printMsg("ReportErrorCode 11178 to drive %s"%ID_CheckList[i])
                  ReportErrorCode(11178)
                  RequestService('SendRun',(0,))
                  RequestService("SetDriveSN", self.dut.serialnum)
                  ScrCmds.raiseException(11178, "IdentifyDevice SerialNum mismatch")
            else:
               objMsg.printMsg("SYS Vs ID SerialNum Matched")

      return data

   #---------------------------------------------------------------------------------------------------------#
   def Is_SeaCosFDE(self):
      if self.dut.IdDevice['IDSeaCosFDE']:
         objMsg.printMsg("Seacos FDE Drive Found")
         return True
      else:
         objMsg.printMsg("Not SeaCos FDE Drive")
         return False

   #-------------------------------------------------------------------------------------------------------
   def Is_FDE(self):
      from TCG import CTCGPrepTest, LifeStates
      if ( self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS' ):
         #from TCG import CTCGPrepTest, LifeStates
         if testSwitch.BF_0180787_231166_P_REMOVE_FDE_CALLBACKS_FOR_CHECKFDE:
            oTCG = CTCGPrepTest(dut)
         try:
            if testSwitch.BF_0180787_231166_P_REMOVE_FDE_CALLBACKS_FOR_CHECKFDE:
               for retry in xrange(3):
                  try:
                     oTCG.CheckFDEState()
                     break
                  except:
                     objMsg.printMsg('Error in determining lifestate- #%d' % ( retry, ))
                     ICmd.spinUpDrive()
            else:
               for retry in xrange(3):
                  try:
                     CTCGPrepTest(dut).CheckFDEState()
                     break
                  except:
                     objMsg.printMsg('Error in determining lifestate- #%d' % ( retry, ))
                     ICmd.spinUpDrive()

         except:
            pass

         if testSwitch.BF_0180787_231166_P_REMOVE_FDE_CALLBACKS_FOR_CHECKFDE:
            oTCG.RemoveCallback()
         if testSwitch.virtualRun:
            self.dut.IdDevice['FDE'] = False
         else:
            self.dut.IdDevice['FDE'] = getattr(self.dut, 'LifeState', LifeStates['INVALID']) != LifeStates['INVALID']

      if self.dut.IdDevice['FDE']:
         if self.ID['IDAddSupported'] & 0x0010 == 0x0010:
            objMsg.printMsg("FDE Drive Found")
            return True
         elif self.ID['IDReserved155'] & 0x8000  == 0x8000 :
            objMsg.printMsg("SDnD Drive Found")
            return True
         else:
            objMsg.printMsg("Sagemcom Found")
            return False
      else:
         objMsg.printMsg("Not FDE Drive")
         return False

   def Is_POIS(self):
      '''Determine if POIS (Power On In Standby) is enabled on the drive)'''
      if testSwitch.virtualRun:
         self.ID['POIS_Enabled'] = 32

      if self.ID['POIS_Enabled'] & 0x20:
         objMsg.printMsg("Drive is in POIS mode")
         return True
      else:
         objMsg.printMsg("POIS not enabled on drive")
         return False
   def Is_POIS_Supported(self):
      '''Determine if the code supports POIS'''
      if testSwitch.virtualRun:
         self.ID['POIS_Supported'] = 32

      if self.ID['POIS_Supported'] & 0x20:
         return True
      else:
         objMsg.printMsg("POIS not supported")
         return False

   def getSupportedATASpeeds(self):
      '''Check the current ATA Signaling Speed .  This supports 1.5, 3.0 and 6.0 Gbps'''

      mask = 0x6
      if testSwitch.virtualRun:
         self.ID['ATASignalSpeedSupport'] = 4

      bitsSet = self.ID['ATASignalSpeedSupport'] & mask

      speedOptions = {  0x2: 1.5,
                          0x4: 3.0,
                          0x6: 6.0}
      if testSwitch.WA_0122875_231166_NOM_SPEED_TP_OVERRIDE:
         speedOptions = getattr(TP, 'prm_speed_options_override',  speedOptions)
      supportedSpeeds = []
      for speed in speedOptions:
         if speed & mask:
            supportedSpeeds.append(speedOptions[speed])

      if DEBUG:
         objMsg.printMsg("Supported ATA speeds (Gbps)= %s" %str(supportedSpeeds))
      return supportedSpeeds

   def getATASpeed(self):
      '''Check the current ATA Signaling Speed .  This supports 1.5, 3.0 and 6.0 Gbps'''
      return ICmd.getATASpeed()

   def drivePairing(self):
      '''Determine if the code supports POIS'''
      if testSwitch.virtualRun:
         self.ID['DrivePairing'] = 0x09

      if self.ID['DrivePairing'] & 0x1:
         supported = True
      else:
         objMsg.printMsg("CE Security Drive Pairing feature not supported")
         supported = False

      if self.ID['DrivePairing'] & 0x10:
         objMsg.printMsg('Drive Pairing Encryption Keys Loaded')
         encryptLoaded = True
      else:
         encryptLoaded = False

      if self.ID['DrivePairing'] & 0x8:
         objMsg.printMsg('Drive Pairing Password Key Loaded')
         encrptPassKeysLoaded = True
      else:
         encrptPassKeysLoaded = False

      return supported, encryptLoaded, encrptPassKeysLoaded

   def determineSectorSize(self):
      '''Determine the physical and logical sector size'''
      sectorSizeLgc, sectorSizePhys  = 512, 512

      #if byte 14 is set and byte 15 is not set then 106 data is valid
      if self.ID['LogToPhysSectorSize'] & 0x4000 and not self.ID['LogToPhysSectorSize'] & 0x8000:
         if DEBUG:
            objMsg.printMsg("Word 106 data is valid")

         #if byte 12 set, logical size > than 512 and its size can be read from word 117-118
         if self.ID['LogToPhysSectorSize'] & 0x1000:
            sectorSizeLgc = self.ID['LogicalSectorSize']

         #if byte 13 set, device has multiple logical sectors per physical sector
         if self.ID['LogToPhysSectorSize'] & 0x2000:         #if true bytes 3:0 are valid
            if DEBUG:
               objMsg.printMsg("Device has multiple logical sectors per physical sector")

            sectorPower = self.ID['LogToPhysSectorSize'] & 0xF
            sectorSizePhys = sectorSizeLgc * 2**sectorPower
         else:
            sectorSizePhys = sectorSizeLgc


      else:
         #standard 512 byte drives will probably not have anything set in word 106 since it is consider optional
         if DEBUG:
            objMsg.printMsg("Word 106 data is invalid.  Setting sector size to 512")

      if DEBUG:
         objMsg.printMsg("Sector Size Phys = %s" %sectorSizePhys)
         objMsg.printMsg("Sector Size Lgc  = %s" %sectorSizeLgc)

      return sectorSizePhys, sectorSizeLgc

   def determineUDMAmode(self):
      '''Determine if the UDMA mode supported by the device'''
      if testSwitch.virtualRun:
         self.ID['IDUDMASupportedMode'] = 0x7f

      for mode in range(6,0,-1):
         if 2**mode & self.ID['IDUDMASupportedMode']:
            if DEBUG:
               objMsg.printMsg('UDMA mode %s and below supported by device' %mode)
            return mode
      else:
         return 0

   def getMaxLBA(self):
      """
      Get drive maximum LBA. This function will handle 48-bit or 24-bit LBA
      length.
      @rtype:  integer
      @return: drive maximum LBA
      """
      # 48-bit LBA length
      if self.ID['IDCommandSet5'] & 0x400:
         return self.dut.IdDevice["Max LBA Ext"]
      # 24-bit LBA length
      else:
         return self.dut.IdDevice["Max LBA"]

   def Is_MediaCache(self):
      '''Determine if Media Cache is enabled on the drive'''
      # or use sendDiagCmd('''F"MediaCacheControl"''')

      objMsg.printMsg("MediaCache Support, Word206=%s" % self.ID['MediaCacheSupport'])

      if self.ID['MediaCacheSupport'] & 0x2000:
         if self.ID['MediaCacheEnabled'] & 0x40:
            objMsg.printMsg("MediaCache Enabled, Word159=%s" % self.ID['MediaCacheEnabled'])
            return True
         else:
            objMsg.printMsg("MediaCache Disabled, Word159=%s" % self.ID['MediaCacheEnabled'])
            return False
      else:
         return None

class CInterface:
   """
   Use interface or CPC test calls
   """
   def __init__(self):
      self.dut = objDut
      from Process import CProcess
      self.oProc = CProcess()


   def writeZerosToSmartLog(self,smartLog, sctrCnt = 1,sctrSize = 512,):
      '''Fill the smart log will all zeros'''

      objMsg.printMsg('Writing zeros to Smart Log %2X' %smartLog)
      ICmd.UnlockFactoryCmds()

      self.writeUniformPatternToBuffer('write')  #write 0's to buffer
      self.displayBuffer('write')
      self.WriteOrReadSmartLog(smartLog, 'write') #write 0's in buffer to smartLog
      self.writeUniformPatternToBuffer('read',dataPattern = (0x2020,0x2020))  #clear read buffer

      self.WriteOrReadSmartLog(smartLog, 'read')  #read the smart log and put in buffer
      self.displayBuffer('read')                  #display the smart log dat that is in the buffer
      smartData = self.writeBufferToFile()        #write the buffer to file to use for data check

      expectedOutput = '\x00'*sctrCnt*sctrSize #output should be 0's.

      if expectedOutput != smartData and not testSwitch.virtualRun:
         objMsg.printMsg("Zero pattern not written successfully to SMART log %2X" %smartLog)
         objMsg.printBin(smartData)
         objMsg.printBin(expectedOutput)
         ScrCmds.raiseException(10251,"Smart Log does not contain all zeros")

      else:
         objMsg.printMsg('Smart Log %2X write completed' %smartLog)



   def writeUniformPatternToBuffer(self, buffer, numBytes = 512, dataPattern = (0x0000, 0x0000), dataPattern1 = ()):
      'Write the same 8 byte pattern across the entire buffer length.  Write to the read or write buffer'

      bufferSelection = {'write': WBF, 'read': RBF}
      databuff = list(dataPattern)
      databuff.extend(dataPattern1)

      try:
         data = struct.pack('>' +'H'*len(databuff), *databuff) #Scale up buffer len to 512
      except:
         objMsg.printMsg("databuff '%s'" % (databuff,))
         raise

      if len(data) <= 4:
         ICmd.FillBuffByte( bufferSelection[buffer], binascii.hexlify(data), 0)
      else:

         data = data * (numBytes/len(data))
         ICmd.FillBuffer( bufferSelection[buffer],  0,  data)


   def writeBytesToBuffer(self, dataPattern0 , dataPattern1 = (), byteOffset = (0,0)):
      'Write the selected byte offsets to the buffer buffer.  Write to the write buffer'


      databuff = list(dataPattern0)
      databuff.extend(dataPattern1)
      try:
         data = struct.pack('>' +'H'*len(databuff), *databuff)
      except:
         objMsg.printMsg("databuff '%s'" % (databuff,))
         raise


      ICmd.FillBuffer( WBF,  CUtility.reverseTestCylWord(byteOffset),  data)


   def displayBuffer(self, buffer , numBytes = 512, byteOffset = (0,0), sendToFile = False):

      bufferSelection = {'write': WBF, 'read': RBF}
      ret = ICmd.GetBuffer(bufferSelection[buffer], CUtility.reverseTestCylWord(byteOffset), numBytes)
      objMsg.printBin(ret['DATA'])
      return ret




   def writeBufferToFile(self, numBytes = 512,):
      '''Write the Buffer to the DriveVars variable so that the data can be used in the process.
      You can only capture 64 bytes of data per 508 test call'''
      from Utility import CUtility
      oUtility = CUtility()

      objMsg.printMsg('Start of writing buffer to file')
      bufferData = ''
      if objRimType.IOInitRiser():
         blockSize = 512
      else:
         blockSize = 64

      blocks = numBytes/blockSize + (numBytes%blockSize > 0)  #get number of 64 byte blocks and round up
      for block in range(blocks):
         byteOffset = oUtility.ReturnTestCylWord(blockSize*block)
         xferBytes = min(blockSize, numBytes - blockSize*block)
         bufferData += self.displayBuffer('read',numBytes = xferBytes,byteOffset = byteOffset, sendToFile = True)['DATA']

      objMsg.printMsg('End of writing buffer to file')

      return bufferData


   def WriteOrReadSmartLog(self, smartLog, action, sctrCnt = 1):
      '''Read or write to the desire smart log'''

      smartSelection = {'write': 0xD6, 'read': 0xD5}

      WrtRdSmartLogPage_538 = {
           'test_num': 538,
           'prm_name': "%sSmartLogPage_538" %action,
           'PARAMETER_0': 0x2000,
           'FEATURES': smartSelection[action],
           'COMMAND': 0xB0,
           'LBA_MID': 0x4F,
           'LBA_LOW': smartLog,
           'LBA_HIGH': 0xC2,
           'SECTOR_COUNT': sctrCnt,
           'timeout': 2600,
           }
      try:
         self.oProc.St(WrtRdSmartLogPage_538)
      except:
         objMsg.printMsg('WriteOrReadSmartLog rerun!')
         ICmd.HardReset()
         self.oProc.St(WrtRdSmartLogPage_538)

   def retrieiveSmartAttributes(self):
      '''Retrieve all attributes from the SMART Attributes log includes some Word Offsets'''

      #read the smart log
      data = self.readSmartAttrs()

      #parse the log to get the attributes
      smartAttrs = {}
      smartAttrs['ATTRIBUTES']  = self.getSmartAttrs(data)

      #get the word offset attributes
      smartAttrs['WORDOFFSETS'] = self.getSmartAttrsByteOffsets(data)
      return smartAttrs
   def getSmartAttrs(self, data):
      '''Find the Smart Attributes in the log and return their raw value'''
      attrs = {}
      StartAttr = 2        # start of SMART attribute offset
      BytesPerAttr = 12    # each attr occupies 12 bytes
      MaxAttr = 30         # total of 30 attr defined for now


      for i in xrange(StartAttr, BytesPerAttr * MaxAttr, BytesPerAttr):
         OneAttr = data[i: i + BytesPerAttr]
         AttrIdx = ord(OneAttr[0:1])
         #AttrStatus = (OneAttr[1:3])
         #AttrNom = ord(OneAttr[3:4])
         #AttrWorst = ord(OneAttr[4:5])

         AttrRaw = (OneAttr[5:11]) + '\x00\x00'
         iRaw = struct.unpack("<Q", AttrRaw)

         #attrs[AttrIdx] = {'Status': AttrStatus, 'Norm': AttrNom, 'Worst': AttrWorst, 'RawValue': iRaw[0]}
         attrs[AttrIdx] = iRaw[0]

      return attrs

   def getSmartAttrsByteOffsets(self, data):
      '''Index into the SMART attribute data by byteOffset'''
      attrs = {}

      #add new bytes of interest here
      wordOffsets = [(410,2),  #Spare Count when Last reset Smart
                    (412,2)]   #Pending Spare Count when last reset Smart

      for byteOffset, numBytes in wordOffsets:
         sValue = data[byteOffset:byteOffset+numBytes]
         attrs[byteOffset] = struct.unpack("<H", sValue)[0]

      return attrs

   def readSmartAttrs(self):
      '''Read the SMART Attribute log and return the data'''
      self.smartEnableOper()

      sctr = ICmd.SmartReadData(exc=1)

      data = ICmd.GetBuffer(RBF, 0, 512)
      sctr = data.get('DATA','')

      if testSwitch.virtualRun:
         sctr = '\n\x00\x01\x0f\x00dd\x00\x00\x00\x00\x00\x00\x00\x03\x03\x00dd\x00\x00\x00\x00\x00\x00\x00\x042\x00dd\x07\x00\x00\x00\x00\x00\x00\x053\x00dd\x00\x00\x00\x00\x00\x00\x00\x07\x0f\x00d\xfd\x00\x00\x00\x00\x00\x00\x00\t2\x00dd\x00\x00\x00\x00\x00\x00\x00\n\x13\x00dd\x00\x00\x00\x00\x00\x00\x00\x0c2\x00dd\x07\x00\x00\x00\x00\x00\x00\xb82\x00dd\x00\x00\x00\x00\x00\x00\x00\xbb2\x00dd\x00\x00\x00\x00\x00\x00\x00\xbc2\x00d\xfd\x00\x00\x00\x00\x00\x00\x00\xbd:\x00dd\x00\x00\x00\x00\x00\x00\x00\xbe"\x00IH\x1b\x00\x1b\x1b\x00\x00\x00\xbf2\x00dd\x00\x00\x00\x00\x00\x00\x00\xc02\x00dd\x02\x00\x00\x00\x00\x00\x00\xc12\x00dd\x07\x00\x00\x00\x00\x00\x00\xc2"\x00\x1b(\x1b\x00\x00\x00\x1b\x00\x00\xc3\x1a\x00dd\x00\x00\x00\x00\x00\x00\x00\xc5\x12\x00dd\x00\x00\x00\x00\x00\x00\x00\xc6\x10\x00dd\x00\x00\x00\x00\x00\x00\x00\xc7>\x00\xc8\xfd\x00\x00\x00\x00\x00\x00\x00\xf0\x00\x00d\xfd\x00\x00\x00\x00\xca\x9f\x00\xf1\x00\x00d\xfd\x00\x00\x00\x00\x00\x00\x00\xf2\x00\x00d\xfd\x00\x00\x00\x00\x00\x00\x00\xfe2\x00dd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00s\x03\x00\x01\x00\x02\x1d\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xdf\xd8\xc2\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\xa9\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x005\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd6'

      return sctr

   def smartEnableOper(self):
      for retry in xrange(3):
         try:
            ICmd.SmartEnableOper()
            break
         except:
            ICmd.HardReset(exc=0)
            time.sleep(2)
            ICmd.IdentifyDevice(exc=0)
      else:
         raise
   def DoMediaCache(self, action):
      '''Media Cache Control, eg enable/disable/init media cache'''

      RestoreATA_TMO = False
      objMsg.printMsg("SCT MC action=%s" % action)
      self.writeUniformPatternToBuffer('write')  #write one sector of zeros

      if action == "disable":    #To issue SCT Disable MC command Option 2
         self.writeBytesToBuffer((0x07C0, 0x0401))  # (action code, function code)
         self.writeBytesToBuffer((0x0200, 0x0000), byteOffset = (0, 0x04))  # offset into 4th byte position and set it to 0x0002 for option 2
      elif action == "enable":   #To issue SCT Enable MC command
         self.writeBytesToBuffer((0x07C0, 0x0301))
      elif action == "init":     #To issue SCT init MC command
         RestoreATA_TMO = True
         ICmd.SetIntfTimeout(10*60*1000)   # 10 mins, Chengai takes ~10mins 
         self.writeBytesToBuffer((0x04C0, 0x0000))
      else:
         ScrCmds.raiseException(14842, "Invalid Media Cache Control!")

      self.displayBuffer('write')

      try:
         self.WriteOrReadSmartLog(0xe0,'write')
      finally:
         if RestoreATA_TMO == True:
            ICmd.SetIntfTimeout(TP.prm_IntfTest["Default CPC Cmd Timeout"]*1000)
