#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: AFH Screens Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/06 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/RAP.py $
# $Revision: #2 $
# $DateTime: 2016/05/06 00:36:23 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/RAP.py#2 $
# Level: 3

#---------------------------------------------------------------------------------------------------------#
from Constants import *

import math, types, re, os, struct
import ScrCmds
from Process import CProcess

import Utility
import FSO
from TestParamExtractor import TP
from Drive import objDut   # usage is objDut
import MessageHandler as objMsg
import dbLogUtilities
from AFH_constants import *




#######################################################################################################################
#
#                  class:  ClassRAP
#
#        Original Author:  Michael T. Brady
#
#            Description:  Deal with PF3 to SF3 RAP access
#
#          Prerrequisite:  Correct T172/T178 support.
#
#######################################################################################################################


class ClassRAP(CProcess):
   TEMP_QUAL_RANGE = TP.TccCal_temp_range #Single sided range of temperatures to auto-load the afh-SIM data
   def __init__(self):
      CProcess.__init__(self)
      self.dut = objDut

      self.mFSO = FSO.CFSO()
      self.spcID = 1

      self.headList = range(objDut.imaxHead)   # note imaxHead is the number of heads

      # variables to initialize
      if (testSwitch.FE_0159597_357426_DSP_SCREEN == 1):
         stateTableName = self.dut.nextState
         if stateTableName == "AFH1_DSP":
            objMsg.printMsg("DSPTruthValue AFH2 is %x" % TD.Truth)
            self.headList = TD.Truth


      self.float_as_words = self.oUtility.float_as_words


   #######################################################################################################################
   #
   #               Function:  getTCC_fromRAP
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  Get the TCC data from the RAP through table P172_AFH_DH_TC_COEF
   #
   #          Prerrequisite:  Valid TCC values stored in the RAP.
   #
   #                  Input:  iHead - head number (int), heaterElement(string)  example ("WRITER_HEATER" or "READER_HEATER")
   #
   #                 Return:  returnTCCDataDict(dict) example returnTCCDataDict: {'THERMAL_CLR_COEF1': -0.25555565949999998, 'THERMAL_CLR_COEF2': 0.0, 'HOT_TEMP_DTH': 60.0, 'ADD_TCS_HOT_DTH': 0.0, 'COLD_TEMP_DTC': 28.0, 'ADD_TCS_COLD_DTC': 0.0}
   #
   #######################################################################################################################

   def getTCC_fromRAP(self, iHead, heaterElement):

      DEBUG_GET_TCC_FROM_RAP_FUNCTION = 1

      returnTCCDataDict = {}
      if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
         p172Tbl = dbLogUtilities.DBLogReader(self.dut, 'P172_AFH_DH_TC_COEF')
      else:
         p172Tbl = dbLogUtilities.DBLogReader(self.dut, 'P172_AFH_DH_TC_COEF_2')
      p172Tbl.ignoreExistingData()

      #Report coefficients
      RetrieveTcCoeff_prm = TP.Retrieve_TC_Coeff_Prm_172.copy()
      RetrieveTcCoeff_prm['spc_id'] = self.spcID + 1000
      self.St( RetrieveTcCoeff_prm )

      p172TblRow = p172Tbl.findRow({'HD_LGC_PSN': iHead, 'ACTIVE_HEATER': heaterElementTableLongNameToShortNameDict[heaterElement]})
      if p172TblRow:
         if not (heaterElement in returnTCCDataDict):
            returnTCCDataDict[ heaterElement ] = {}
         returnTCCDataDict[ heaterElement ]['THERMAL_CLR_COEF1'] = float(p172TblRow['THERMAL_CLR_COEF1'])
         returnTCCDataDict[ heaterElement ]['THERMAL_CLR_COEF2'] = float(p172TblRow['THERMAL_CLR_COEF2'])

         returnTCCDataDict[ heaterElement ]['dTc']  = float(p172TblRow['ADD_TCS_COLD_DTC'])
         returnTCCDataDict[ heaterElement ]['dTh']   = float(p172TblRow['ADD_TCS_HOT_DTH'])

         returnTCCDataDict[ heaterElement ]['COLD_TEMP_DTC']     = float(p172TblRow['COLD_TEMP_DTC'])
         returnTCCDataDict[ heaterElement ]['HOT_TEMP_DTH']      = float(p172TblRow['HOT_TEMP_DTH'])

      else:
         # should we hard fail here if no data is found since this would be unlikely and unexpected?!
         # I don't want to default to 0.0
         ScrCmds.raiseException(11044, "getTCC_fromRAP/ No data found for iHead: %s, heaterElement: %s" % (iHead, heaterElement))


      #
      if DEBUG_GET_TCC_FROM_RAP_FUNCTION: objMsg.printMsg("getTCC_fromRAP/ iHead: %s, heaterElement: %s, returnTCCDataDict: %s" % (iHead, heaterElement, returnTCCDataDict))
      return returnTCCDataDict


   #
   def SaveTCC_toRAP(self, head, tcc1, tcc2, heaterElement, tcc_DH_values,  Zones = [0,]):
      """
         #########################################################################################
         #
         #               Function:  SaveTCC
         #
         #        Original Author:  Michael T. Brady
         #
         #            Description:  save TCC values to RAP
         #
         #                  Input:  tcc1 and tcc2
         #
         #           Return Value:  None
         #
         #########################################################################################

      """

      # Update the AFH Temperature Correction Coefficients

      if testSwitch.AFH_IS_RAP_TCS_IN_ANGSTROMS == 1:
         localTCS_AngstromsScaler = 1.0
      else:
         localTCS_AngstromsScaler = 254.0


      TC_Coeff = TP.TC_Coeff_Prm_178_DH.copy()

      TC_Coeff['HEAD_RANGE'] = 2**head # Head mask of heads to update with input parms

      objMsg.printMsg("forceTcs2EqualZero == 1 so force 0 non-linear component", objMsg.CMessLvl.DEBUG)
      tcc2 = 0
      if not testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP:
         tcc1 = tcc1 / float(localTCS_AngstromsScaler)
      else:
         tcc1_org = tcc1
      
      float_as_words = self.oUtility.float_as_words

      for iZone in Zones:
         if testSwitch.extern.FE_0157745_387179_AFH_TCS_WARP: # and iZone != -1:
              keylist = TP.TCS_WARP_ZONES.keys()
              keylist.sort()
              zoneIndex = keylist.index(iZone)
              if isinstance(tcc1_org, float) or isinstance(tcc1_org, int):
                tcc1 = tcc1_org / float(localTCS_AngstromsScaler)
              if isinstance(tcc1_org,list):
                tcc1 = tcc1_org[iZone] / float(localTCS_AngstromsScaler)
                objMsg.printMsg("tcc1=%d %s" %(tcc1,str(tcc1_org)))
              readerDTC = tcc_DH_values["READER_HEATER"]['dTcR'][zoneIndex]
              readerDTH = tcc_DH_values["READER_HEATER"]['dThR'][zoneIndex]
              writerDTC = tcc_DH_values["WRITER_HEATER"]['dTcR'][zoneIndex]
              writerDTH = tcc_DH_values["WRITER_HEATER"]['dThR'][zoneIndex]
              zoneIndex = 2**zoneIndex
         else:             
              readerDTC = tcc_DH_values["READER_HEATER"]['dTc']
              readerDTH = tcc_DH_values["READER_HEATER"]['dTh']
              writerDTC = tcc_DH_values["WRITER_HEATER"]['dTc']
              writerDTH = tcc_DH_values["WRITER_HEATER"]['dTh']
              zoneIndex = 0 

         if heaterElement == "READER_HEATER":
            AFH_DH_READER_HEATER_AFH_COEF_ADAPTIVE_INDEX_UPDATE_TCC1_AND_DTC_AND_TCS_COLD_TEMP_DTC = 18
            TC_Coeff['C_ARRAY1'] = [ 0 ] + [ AFH_DH_READER_HEATER_AFH_COEF_ADAPTIVE_INDEX_UPDATE_TCC1_AND_DTC_AND_TCS_COLD_TEMP_DTC, 0,] + [ zoneIndex ] + \
                  float_as_words( tcc1 ) + float_as_words( readerDTC / float(localTCS_AngstromsScaler) ) + [ 0, int(round(tcc_DH_values["READER_HEATER"]['COLD_TEMP_DTC'])) ]
            self.St(TC_Coeff)

         if heaterElement == "READER_HEATER":
            AFH_DH_READER_HEATER_AFH_COEF_ADAPTIVE_INDEX_UPDATE_TCC2_AND_DTH_AND_TCS_HOT_TEMP_DTH  = 19
            TC_Coeff['C_ARRAY1'] = [ 0 ] + [ AFH_DH_READER_HEATER_AFH_COEF_ADAPTIVE_INDEX_UPDATE_TCC2_AND_DTH_AND_TCS_HOT_TEMP_DTH, 0, ] + [ zoneIndex ] + \
                  float_as_words( tcc2 / float(localTCS_AngstromsScaler) ) + float_as_words( readerDTH  / float(localTCS_AngstromsScaler)) + [ 0, int(round(tcc_DH_values["READER_HEATER"]['HOT_TEMP_DTH'])) ]
            self.St(TC_Coeff)

         if heaterElement == "WRITER_HEATER":
            AFH_DH_WRITER_HEATER_AFH_COEF_ADAPTIVE_INDEX_UPDATE_TCC1_AND_DTC_AND_TCS_COLD_TEMP_DTC = 28
            TC_Coeff['C_ARRAY1'] = [ 0 ] + [ AFH_DH_WRITER_HEATER_AFH_COEF_ADAPTIVE_INDEX_UPDATE_TCC1_AND_DTC_AND_TCS_COLD_TEMP_DTC, 0,] + [ zoneIndex ] + \
                  float_as_words( tcc1 ) + float_as_words( writerDTC  / float(localTCS_AngstromsScaler)) + [ 0, int(round(tcc_DH_values["WRITER_HEATER"]['COLD_TEMP_DTC'])) ]
            self.St(TC_Coeff)

         if heaterElement == "WRITER_HEATER":
            AFH_DH_WRITER_HEATER_AFH_COEF_ADAPTIVE_INDEX_UPDATE_TCC2_AND_DTH_AND_TCS_HOT_TEMP_DTH  = 29
            TC_Coeff['C_ARRAY1'] = [ 0 ] + [ AFH_DH_WRITER_HEATER_AFH_COEF_ADAPTIVE_INDEX_UPDATE_TCC2_AND_DTH_AND_TCS_HOT_TEMP_DTH, 0,] + [ zoneIndex ] + \
                  float_as_words( tcc2 / float(localTCS_AngstromsScaler) ) + float_as_words( writerDTH / float(localTCS_AngstromsScaler)) + [ 0, int(round(tcc_DH_values["WRITER_HEATER"]['HOT_TEMP_DTH'])) ]
            self.St(TC_Coeff)

      ##self.St({'test_num':172, 'prm_name': 'Retrieve TC Coefficient', "CWORD1" : (10), 'spc_id': 1, })


   #########################################################################################
   #
   #               Function:  initializeClearanceSettlingParams
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  Initialize the clearance settling parameters stored in the RAP
   #
   #                  Input:  None
   #
   #           Return Value:  None
   #
   #########################################################################################

   def initializeClearanceSettlingParams(self, ):

      AFH_CLEARANCE_SETTLING_CLEARANCE_F3_CODE_MASTER_ENABLE = 104

      for iHead in self.headList:
         if (testSwitchRef.extern.CLR_SETTLING_MAJ_REL_NUM >= 3):
            clearanceSettling_Prm_178Local = TP.clearanceSettling_Prm_178.copy()

            clearanceSettling_Prm_178Local['HEAD_RANGE'] = 2 ** iHead # Head mask of heads to update with input parms

            clearanceSettling_Prm_178Local['C_ARRAY1'] = [ 0, AFH_CLEARANCE_SETTLING_CLEARANCE_F3_CODE_MASTER_ENABLE,   0, 0 ] + \
                                                         [ 0,                                                      0,   0, 0 ] + \
                                                         [ 0, 0 ]

            self.St(clearanceSettling_Prm_178Local)

         clearanceSettlingFloat = TP.AFH_clearanceSettling_ParametersDict['CLR_SETTLING_CORRECTION_IN_ANGSTROMS']
         self.saveClearanceSettlingDataByHeadToRAP(iHead, clearanceSettlingFloat )

      #
      minClrSettlingCorrection = TP.AFH_clearanceSettling_ParametersDict['MIN_CLR_SETTLING_CORRECTION']
      clearanceSettlingDecay   = TP.AFH_clearanceSettling_ParametersDict['CLR_SETTLING_DECAY']

      self.saveClearanceSettlingDataByDriveToRAP(minClrSettlingCorrection, clearanceSettlingDecay)


   #########################################################################################
   #
   #               Function:  saveClearanceSettlingDataToRAP
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  save the clearance settling data to the RAP using test 178
   #
   #                  Input:  iHead(int)
   #
   #           Return Value:  None
   #
   #########################################################################################

   def saveClearanceSettlingDataByHeadToRAP(self, iHead, clearanceSettlingInt):

      # from rwapi_pub.h
      AFH_CLEARANCE_SETTLING_CLEARANCE_SETTLING_CORRECTION_BY_HEAD                                              = 100

      clearanceSettlingInt = int(clearanceSettlingInt)

      clearanceSettling_Prm_178Local = TP.clearanceSettling_Prm_178.copy()

      clearanceSettling_Prm_178Local['HEAD_RANGE'] = 2 ** iHead # Head mask of heads to update with input parms

      clearanceSettling_Prm_178Local['C_ARRAY1'] = [ 0, AFH_CLEARANCE_SETTLING_CLEARANCE_SETTLING_CORRECTION_BY_HEAD, 0, 0 ] + \
                                                   [ 0,                                                            0, 0, 0 ] + \
                                                   [ 0, clearanceSettlingInt ]

      self.St(clearanceSettling_Prm_178Local)

   #########################################################################################
   #
   #               Function:  initializeHCSParams
   #
   #        Original Author:  Ben T Cordova
   #
   #            Description:  save the HCS Curve data to the RAP using test 178
   #
   #                  Input:  hcsCoefs - a list of the HCS Curve coefficients per zone
   #                          system zone is last in the hcsCoefs list
   #
   #           Return Value:  None
   #
   #                  Notes:  Each datavalue is made positive and  multiplied by 1000
   #
   #########################################################################################

   def initializeHCSParams(self, preamp, aabtype, clr_Coeff):

      hcsCoefs = self.getHcsCoeff(clr_Coeff, preamp, aabtype)
      bakedHcsCoefs = []

      for coef in hcsCoefs:
         for hcsModificationFunctionEvalString in TP.hcsParamModificationOptions:
            coef = eval(hcsModificationFunctionEvalString % str(coef))
         bakedHcsCoefs.append(coef)

      for iZone in range(len(bakedHcsCoefs)):
         zone_mask_high = 0
         zone_mask_low = 0
         zone_mask1_high = 0
         zone_mask1_low = 0
         if iZone < 32:
            zone_mask_high, zone_mask_low = Utility.CUtility.ReturnTestCylWord(2**iZone)
         else:
            zone_mask1_high, zone_mask1_low = Utility.CUtility.ReturnTestCylWord(2**(iZone-32))
         paramsToUse = TP.prm_afhSetHCSCoefficient_178
         if iZone == len(bakedHcsCoefs) - 1:
            paramsToUse = TP.prm_afhSetHCSCoefficientAndSaveToRAP_178

         # now, save to RAP via t178
         self.St(paramsToUse,
                 HEAD_RANGE=int(len(self.headList)*'1'),  # do the same for all heads
                 BIT_MASK=(zone_mask_high,zone_mask_low),
                 BIT_MASK_EXT=(zone_mask1_high,zone_mask1_low),
                 HUMIDITY_COEF=bakedHcsCoefs[iZone])

   def getHcsCoeff(self, clr_Coeff, preamp, aabtype):
      if clr_Coeff.has_key(preamp) and clr_Coeff[preamp].has_key(aabtype) and clr_Coeff[preamp][aabtype].has_key('hcsCoefficients'):
         return clr_Coeff[preamp][aabtype]['hcsCoefficients']
      else:
         objMsg.printMsg('Drive failed for trying to index a preamp/aabtype that does not exist when trying to find hcsCoefficients', objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg('clr_Coeff  : %s' % str(clr_Coeff), objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg('preamp  : %s' % str(preamp), objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg('aabtype  : %s' % str(aabtype), objMsg.CMessLvl.IMPORTANT)

         ScrCmds.raiseException(14575, "Drive failed for trying to index a preamp/aabtype that does not exist when trying to find hcsCoefficients: (%s,%s)" % (str(preamp), str(aabtype)))

   def initializeTRiseValues(self, preamp, aabtype, clr_Coeff):
      """
                  Function:  initializeTRiseValues

           Original Author:  Ben T Cordova

               Description:  save the TRise Values to the RAP using test 178

                     Input:  A preamp key.  The TRise values should be contained within
                             the program's clearanc coefficient dictionary for this preamp

              Return Value:  None
      """

      TRiseValues = self.getTRiseValues(clr_Coeff, preamp, aabtype)
      if testSwitch.FE_0276246_231166_P_ENABLE_SET_OVS_RISE_TIME:
         OvsRiseValues = self.getOvsRiseValues(clr_Coeff, preamp, aabtype)
      bakedTRiseValues = []

      for val in TRiseValues:
         for TRiseValueModificationFunctionEvalString in TP.TRiseValueModificationOptions:
            val = eval(TRiseValueModificationFunctionEvalString % str(val))
         bakedTRiseValues.append(val)

      if testSwitch.FE_0270095_504159_SUPPORT_LOOPING_ZONE_T178:
         # Assuming Trise value is the same for all heads/zones
         paramsToUse = TP.prm_setTRiseAndSaveToRAP_178
         if testSwitch.FE_0276246_231166_P_ENABLE_SET_OVS_RISE_TIME:
            paramsToUse['OVS_RISE_TIME'] = OvsRiseValues[0]
            paramsToUse['CWORD4'] |= 0x2000
            self.St(paramsToUse,
            HEAD_RANGE   = Utility.CUtility.intToOnesMask( len( self.headList ) ),  # Do the same for all heads
            ZONE         = len(bakedTRiseValues) - 1,
            T_RISE       = bakedTRiseValues[0] )

      else:
         for iZone in range(len(bakedTRiseValues)):
            paramsToUse = TP.prm_setTRise_178
            if iZone == len(bakedTRiseValues) - 1:
               paramsToUse = TP.prm_setTRiseAndSaveToRAP_178

            # Now, save to RAP via t178

            zone_mask_high, zone_mask_low = Utility.CUtility.ReturnTestCylWord(2**iZone)
            if testSwitch.FE_0276246_231166_P_ENABLE_SET_OVS_RISE_TIME:
               paramsToUse['OVS_RISE_TIME'] = OvsRiseValues[iZone]
               paramsToUse['CWORD4'] |= 0x2000
               self.St(paramsToUse,
               HEAD_RANGE   = Utility.CUtility.intToOnesMask( len( self.headList ) ),  # Do the same for all heads
               BIT_MASK     = ( zone_mask_high, zone_mask_low ),
               T_RISE       = bakedTRiseValues[iZone] )

      #output the saved Trise values to dblog via t172
      self.St(TP.prm_outputTRiseValuesByHeadByZone_172)

   def getOvsRiseValues(self, clr_Coeff, preamp, aabtype):
      if clr_Coeff.has_key('ovsRiseTimeValues'):
         if  self.dut.numZones < len(clr_Coeff['ovsRiseTimeValues']) :
            return clr_Coeff['ovsRiseTimeValues'][0:self.dut.numZones]
         else:
            return clr_Coeff['ovsRiseTimeValues']
      else:
         objMsg.printMsg('Drive failed for trying to index a preamp/aabtype that does not exist when trying to find ovsRiseTimeValues', objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg('clr_Coeff  : %s' % str(clr_Coeff), objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg('preamp  : %s' % str(preamp), objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg('aabtype  : %s' % str(aabtype), objMsg.CMessLvl.IMPORTANT)

         ScrCmds.raiseException(14575, "Drive failed for trying to index a preamp/aabtype that does not exist when trying to find ovsRiseTimeValues: (%s,%s)" % (str(preamp), str(aabtype)))

   def getTRiseValues(self, clr_Coeff, preamp, aabtype):
      if clr_Coeff.has_key('triseValues'):
         if self.dut.numZones < len(clr_Coeff['triseValues']) :
            return clr_Coeff['triseValues'][0:self.dut.numZones]
         else:
            return clr_Coeff['triseValues']
      else:
         objMsg.printMsg('Drive failed for trying to index a preamp/aabtype that does not exist when trying to find triseValues', objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg('clr_Coeff  : %s' % str(clr_Coeff), objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg('preamp  : %s' % str(preamp), objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg('aabtype  : %s' % str(aabtype), objMsg.CMessLvl.IMPORTANT)

         ScrCmds.raiseException(14575, "Drive failed for trying to index a preamp/aabtype that does not exist when trying to find triseValues: (%s,%s)" % (str(preamp), str(aabtype)))
