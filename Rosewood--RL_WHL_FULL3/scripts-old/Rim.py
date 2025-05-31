#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: The Rim object is an abstraction of the cell RIM and implements methods to implement
#              to power on/off rim, download CPC/NIOS/Serial code etc.
#              Note that only once instance of rim must exist in the entire test environment.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Rim.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Rim.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import types
import ScrCmds
from RimTypes import intfTypeMatrix
import MessageHandler as objMsg

SATA_RiserBase = ['SATA',]
SAS_RiserBase = ['SAS',]

RISER_EXT_CONTROLLER_FIELD = 5
RISER_EXT_IO_RATE = 4
RISER_EXT_INTF_SUPP_START  = 2

RISER_INTF_SUPPORT_LOOKUP = {
'AT': 'PATA',
'ST': 'SATA',
'FC': 'FC',
'LC': 'FC',
'LW': 'FC',
'SS': 'SAS',
'SX': 'SAS/SATA',
'US': 'USB',
   }

RISER_BASE = RISER_INTF_SUPPORT_LOOKUP.get(riserExtension[RISER_EXT_INTF_SUPP_START:RISER_EXT_INTF_SUPP_START+2], None)

###########################################################################################################
###########################################################################################################
class CRimType:                                             # Class for handling various baseType/riserType/rimType tests
   def __init__(self):
      #if testSwitch.virtualRun == 1:
      #   self.baseType = ''
      #else:
      self.baseType = self.getBase(riserType)

      self.rimTypeMatrix = None

   #------------------------------------------------------------------------------------------------------#
   def getBase(self, riser, extension = riserExtension):                                 # Based on riserType - return appropriate baseType ('SATA','SAS' or 'FC')
      """
      Search through the intfTypeMatrix for matches to base types

      """
      # Create locals for speed
      rimType = DriveAttributes.get('RIM_TYPE','')
      if testSwitch.FE_0174482_231166_P_USE_INC_CODE_BY_SOC_TYPE:

         base = self.validateRiserTypeInBase(RISER_BASE)
         if base != None:
            return base


      for base in intfTypeMatrix.keys(): # SATA, SAS, FC

         intfTypeMatrix[base]['rimTypeMatrix']

         # Look for a match of current rim type in the rim type matrix for this base
         # This should have precedence as there can be multiple riser to rim matches
         found = False
         if rimType in ['?','']:    # Invalid rim type id's for beginning and end of testing or bench eval- trust user to set riser correct
            found = True
         else:
            for rims in intfTypeMatrix[base]['rimTypeMatrix'].values():
               if rimType in rims:
                  found = True

         if found:
            # Now confirm that the riser is also supported by this base- otherwise we are in the wrong base
            for riserTypes in intfTypeMatrix[base]['riserTypeMatrix'].values(): # Check serial only, initiator, cpc
               if (riser in riserTypes) or (riser + extension in riserTypes):
                  # Wwe have found a rim and riser match
                  objMsg.printMsg("RimType: %s, RiserType: %s, Extension: %s IS supported in base %s" % (rimType, riser, extension, base))
                  return base

         objMsg.printMsg("RimType: %s, RiserType: %s, Extension: %s NOT supported in base %s" % (rimType, riser, extension, base))

      ScrCmds.raiseException(11187, "ERROR: riserType : %s not found in SerialOnly/CPC list" % riser)

   def validateRiserTypeInBase(self, base):
      if not base in intfTypeMatrix:

         ScrCmds.raiseException(11187, "base %s not supported in process for riserExtension %s" % ( base, riserExtension))
      for riserTypes in intfTypeMatrix[base]['riserTypeMatrix'].values(): # Check serial only, initiator, cpc
         if (riserType in riserTypes) or (riserType + riserExtension in riserTypes):
            # Wwe have found a rim and riser match
            objMsg.printMsg("RiserType: %s, Extension: %s IS supported in base %s" % (riserType, riserExtension, base))
            return base
      return None

   #------------------------------------------------------------------------------------------------------#
   def NewRimType(self,NRTOperation, currentRimType ):                       # For given operation, return rimType
      if testSwitch.virtualRun == 1:
         return currentRimType
      else:
         if currentRimType in intfTypeMatrix[self.baseType]['rimTypeMatrix'][NRTOperation]:
            rimType = currentRimType
         else:
            rimType = intfTypeMatrix[self.baseType]['rimTypeMatrix'][NRTOperation][0]
         return rimType

   #----------------------------------------------------------------------------
   def NextRimType(self, partNum, curOper, curRimType):
      if testSwitch.virtualRun == 1:
         return curRimType
      else:
         if partNum[3] == '0':
            partNumPrefix = partNum[0:6]
         else:
            partNumPrefix = partNum[0:4]


         if self.rimTypeMatrix == None:
            rimTypeMatrix = self.rimTypeMatrix = RequestService('GetSiteconfigSetting','rim_types')[1]
         else:
            rimTypeMatrix = self.rimTypeMatrix


         if (type(rimTypeMatrix) == types.StringType and rimTypeMatrix  in ['Error or not supported','UnSupported']) or rimTypeMatrix['rim_types'] == 'Unknown':
            return self.NewRimType(curOper,curRimType)#Maintain backwards compatibility with RimTypes.py
         else:
            for partNumList in rimTypeMatrix['rim_types'].keys():
               if partNumPrefix in partNumList:
                  objMsg.printMsg("GetSiteconfigSetting for rim_types %s" % rimTypeMatrix['rim_types'][partNumList])
                  for rimType,operList in rimTypeMatrix['rim_types'][partNumList].items():
                     if curOper in operList:
                        return rimType
                  else:
                     ScrCmds.raiseException(11187, "Next rim type not found")
            else: #Maintain backwards compatibility with RimTypes.py
               return self.NewRimType(curOper,curRimType)

   #------------------------------------------------------------------------------------------------------#
   def SerialOnlyRiserList(self):                              # Return Serial riser list
      return intfTypeMatrix[self.baseType]['riserTypeMatrix']['SerialOnlyList']

   #------------------------------------------------------------------------------------------------------#
   def CPCRiserList(self):                                     # Return CPC riser list
      return intfTypeMatrix[self.baseType]['riserTypeMatrix']['CPCList']

   #------------------------------------------------------------------------------------------------------#
   def NIOSRiserList(self):                                    # Return NIOS riser list
      return intfTypeMatrix[self.baseType]['riserTypeMatrix']['NIOSList']

   #------------------------------------------------------------------------------------------------------#
   def IOInitRiserList(self):                                  # Return IO with Initiator riser list
      return intfTypeMatrix[self.baseType]['riserTypeMatrix']['IOInitList']

   #------------------------------------------------------------------------------------------------------#
   def SingleDensityRiserList(self):                           # Return Single density riser list
      return ["SCA", "FC", "FC4", "WIDE", "SAS", ]

   #------------------------------------------------------------------------------------------------------#
   def SerialOnlyRiser(self):                                  # Check if riserType in SerialOnly list (boolean)
      if testSwitch.FORCE_SERIAL_ICMD:
         return True

      return riserType in self.SerialOnlyRiserList() or (riserType + riserExtension) in self.SerialOnlyRiserList()

   #------------------------------------------------------------------------------------------------------#
   @classmethod
   def IsHDSTRRiser(cls):                                     # Check if riserType is HDSTR (For HDSTR SP TESTER)
      """
      Determine if riserType = 'HDSTR', it will return true for checking drive run on HDSTR_SP tester.
      """
      return (riserType == 'HDSTR')

   #------------------------------------------------------------------------------------------------------#
   @classmethod
   def IsPSTRRiser(cls):
      """ Returns if riser is PSTR or not"""
      return (len(riserType) > 5 and ((riserType[2:6] == 'SER0') or (riserType[2:6] == 'SER1')) )

   #------------------------------------------------------------------------------------------------------#
   @classmethod
   def IsPSTR_EIC(cls):
      """ Returns if riser is SEIC or not"""
      return (len(riserType) > 5 and ( riserType[2:6] == 'SER0') )

   #------------------------------------------------------------------------------------------------------#
   @classmethod
   def IsLowCostSerialRiser(cls):
      """
      Return True if riser is a serial only riser. This is true for serial port only configured systems like HDSTR
         or PSTR. These systems typically have a higher CM to slot ratio and little temperature control.
      """
      return ( cls.IsPSTRRiser() or cls.IsHDSTRRiser() )

   #------------------------------------------------------------------------------------------------------#
   def NoIO_CPCOTF(self):
      objMsg.printMsg("Checking NoIO CPC OTF")

      try:
         fwFile, Memo = CheckDownloadRequest()
         objMsg.printMsg("Check DL Request : Firmware File: [%s], Memo: [%s]" % (fwFile, `Memo`))

         #if fwFile in ("CPC_APP.nex", ):
         if len(fwFile) > 0:
            # Let the other tray download.
            response = DownloadRim(None, None, fwFile, ignoreFWSignature=1)
            objMsg.printMsg("DownloadRim response: [%s]" % (`response`))
            return 2
         else:
            return 0
      except IOError:
         if not testSwitch.NoIO:    # for SP IO, IOError warnings can be ignored
            raise
      except:
         if testSwitch.NoIO:
            import traceback
            objMsg.printMsg("Warning! NoIO CheckDownloadRequest Exception: %s" % (traceback.format_exc(),))
         else:
            raise
                 
      return 0                             

   #------------------------------------------------------------------------------------------------------#
   def CPCRiser(self, ReportReal = False):                                         # Check if riserType in CPCList (boolean)
      if testSwitch.FORCE_SERIAL_ICMD and ReportReal == False:
         return False

      return riserType in self.CPCRiserList() or (riserType + riserExtension) in self.CPCRiserList()

   #------------------------------------------------------------------------------------------------------#
   def CPCRiserNewSpt(self):
      CPC_SP_MOD_OPTIONS = ['41',]
      cpsSPTRiser= (riserType in self.CPCRiserList()) and (riserExtension[8:] in CPC_SP_MOD_OPTIONS)
      return cpsSPTRiser

   #------------------------------------------------------------------------------------------------------#
   def IOInitRiser(self):                                     # Check if riserType in IOInitList (boolean)
      return riserType in self.IOInitRiserList() or (riserType + riserExtension) in self.IOInitRiserList()

   #------------------------------------------------------------------------------------------------------#
   def SingleDensityRiser(self):                              # Check if riserType in SingleDensityRiserList (boolean)
      return riserType in self.SingleDensityRiserList() or (riserType + riserExtension) in self.SingleDensityRiserList()

   def isIoRiser(self):

      if testSwitch.FORCE_SERIAL_ICMD:
         return False

      if testSwitch.FE_0182188_231166_P_ALLOW_DETS_CE_LOG_CAPTURE:
         if DEBUG: objMsg.printMsg("riserExtension = %s" % riserExtension)
         
         if len(riserExtension) >= RISER_EXT_IO_RATE+1:
            if DEBUG: objMsg.printMsg("riserExtension[] = %s" % riserExtension[RISER_EXT_IO_RATE])
            return int(riserExtension[RISER_EXT_IO_RATE],16) > 0
         else:
            return False
      else:
         return True
   #------------------------------------------------------------------------------------------------------#
   def isNeptuneRiser(self):                                  # Check if riser is a Neptune (boolean)
      """
      Determine if the drive is in a Neptune2 oven by checking the riser extension.

      """
      return ((not riserExtension == '' and riserExtension[0] == 'N') and testSwitch.FE_0163145_470833_P_NEPTUNE_SUPPORT_PROC_CTRL20_21)

   #------------------------------------------------------------------------------------------------------#
   def isOptimusRiser(self):                                  # Check if riser is an Optimus (boolean)
      """
      Determine if the drive is in a Optimus oven by checking the riser extension.

      """
      return (not riserExtension == '' and riserExtension[0] == 'O')

   def getRiserSOCType(self):
      """
      Return the SOC riser type according to the SOC lookup matrix
      """
      socLookupMatrix = {
         'L': 'luxor',
         'K': 'skua',
         'T': 'banshee',
         'U': 'tui',
      }

      socType = socLookupMatrix.get(riserExtension[RISER_EXT_CONTROLLER_FIELD])

      #Need to accomodate the T = sata or sas...
      if socType == 'banshee' and RISER_BASE in ['SAS', 'FC']:
         socType = 'kahu'

      return socType


###########################################################################################################
###########################################################################################################
objRimType = CRimType()                                     # Class object for RimType
if not testSwitch.virtualRun:
   objMsg.printMsg("Rim.py testSwitch.NoIO=%s testSwitch.SI_SERIAL_ONLY=%s" % (testSwitch.NoIO, testSwitch.SI_SERIAL_ONLY))
   if objRimType.SerialOnlyRiser() or (testSwitch.SI_SERIAL_ONLY and testSwitch.NoIO):
      from SerialRim import SerialRim
      theRim = SerialRim(objRimType)

      if testSwitch.NoIO:
         if objRimType.CPCRiser(ReportReal = True):
            objMsg.printMsg("CPC OTF support for NoIO")
            theRim.Unlock = objRimType.NoIO_CPCOTF

   elif objRimType.CPCRiser():
      from CPCRim import CPCRim
      theRim = CPCRim(objRimType)
   elif objRimType.IOInitRiser():
      from IORim import IORim
      theRim = IORim(objRimType)
   else:
      from baseRim import baseCRim
      theRim = baseCRim(objRimType) # create carrier instance,power on cell/carrier
else:
   class rimObj(object):

      def __getattribute__(self, name):
         if objRimType.CPCRiser():
            from CPCRim import CPCRim
            obj = CPCRim(objRimType)
         elif objRimType.SerialOnlyRiser():
            from SerialRim import SerialRim
            obj = SerialRim(objRimType)
         elif objRimType.IOInitRiser():
            from IORim import IORim
            obj = IORim(objRimType)
         else:
            from baseRim import baseCRim
            obj = baseCRim(objRimType) # create carrier instance,power on cell/carrier

         return obj.__getattribute__(name)
   theRim = rimObj()


TraceMessage('Rim Instance Created %d' % PortIndex)
