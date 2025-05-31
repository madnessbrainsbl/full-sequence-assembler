#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PreAmp.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PreAmp.py#1 $
# Level:3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from Process import CProcess
from Drive import objDut
import MessageHandler as objMsg

class CPreAmp(CProcess):

   class PREAMP_HEATER_MODES:
      """
      Basic class for setting required bits to apply heater mode.
      """
      LO_VAL = "LO_POWER"
      HI_VAL = "HI_POWER"

      HI_MASK = 0xE220
      LO_MASK = 0x722F
      __HI_SEC = 0x8000

      def __init__(self):
         pass
      def LO(self, base):
         return base & self.LO_MASK
      def HI(self, base):
         return base & self.HI_MASK | self.__HI_SEC

   def __init__(self):
      CProcess.__init__(self)
      self.dut = objDut

   def preAmpGainAccess(self,inPrm,iTimeout):
      #Provide a head amplitude measurement procedure that can be used by SP240 to select an optimal preamp gain setting, for storage in the SAP.
      self.St(177,inPrm,timeout = iTimeout) #Programmable Preamp Gain


   def heaterResistanceMeasurement(self, inPrm, masterHeatPrm, initialHeatState = 0):
      """
      Provide heater resistance measurement for all heads at 1-2 cyls for various heater settings as defined in the input parameter
      @param inPrm: Drive Firmware Parameter input
      """
      from AFH import CAFH
      CAFH().setMasterHeat(masterHeatPrm,1)
      self.St(inPrm)
      if initialHeatState == 0:
         CAFH().setMasterHeat(masterHeatPrm,0)

   def getPreAmpType(self):
      import ScrCmds
      import traceback

      tableNames = [i[0] for i in self.dut.dblData.Tables()]
      if 'P166_PREAMP_INFO' not in tableNames:
         try:
            self.St({'test_num':166,'CWORD1':0x1000, 'timeout': 200})
         except:
            objMsg.printMsg(traceback.format_exc())
      preamp_ID = int(self.dut.dblData.Tables('P166_PREAMP_INFO').tableDataObj()[-1]['PREAMP_ID'], 16)


      try:
         preamp_rev = int(self.dut.dblData.Tables('P166_PREAMP_INFO').tableDataObj()[-1]['PREAMP_REV'], 16)
      except:
         preamp_rev = None

      if self.dut.dblData.Tables('P166_PREAMP_INFO').tableDataObj()[-1].has_key('MFR'):
         mfr = self.dut.dblData.Tables('P166_PREAMP_INFO').tableDataObj()[-1]['MFR']
      else:
         mfr = str(self.dut.dblData.Tables('P166_PREAMP_INFO').tableDataObj()[-1]['PREAMP_MFGR']) #New parametric preamp links
      objMsg.printMsg('PREAMP MANUFACTURER: %s, PREAMP ID: 0x%X' % (mfr, preamp_ID,))

      try:
         preamp_type = TP.PreAmpTypes[mfr.upper()][preamp_ID][0]
         objMsg.printMsg('PREAMP_TYPE AS PER CONFIG TABLE: %s' % (preamp_type,))
      except:
         ScrCmds.raiseException(10554, "Unknown preamp type")

      return (preamp_type,mfr,preamp_ID,preamp_rev)

   def setPreAmpHeaterMode(self,basePrm, mode = PREAMP_HEATER_MODES.LO_VAL):
      import types
      #Determine the cword imput type
      if type(basePrm['CWORD1']) == types.TupleType:
         defVal =basePrm['CWORD1'][0]
      else:
         defVal =basePrm['CWORD1']

      #Switch table to apply correct heater setting based on input
      if mode == self.PREAMP_HEATER_MODES().LO_VAL:
         defVal = self.PREAMP_HEATER_MODES().LO(defVal)
      elif mode == self.PREAMP_HEATER_MODES().HI_VAL:
         defVal = self.PREAMP_HEATER_MODES().HI(defVal)
      basePrm.update({"CWORD1":defVal})

      #Tell the drive what mode it should be in **** Doesn't save to RAP on it's own
      self.St(basePrm)
