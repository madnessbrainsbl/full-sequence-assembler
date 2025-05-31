#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_Preamp.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_Preamp.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from State import CState
import MessageHandler as objMsg


#----------------------------------------------------------------------------------------------------------
class CDETCRPreampSetup(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.FE_0135335_342029_P_DETCR_TP_SUPPORT:
         from TestParamExtractor import TP
         from Process import CProcess
         self.oProc = CProcess()

         objMsg.printMsg("Starting DETCR")
         objMsg.printMsg("mfr = %s" % self.dut.PREAMP_MFR)
         T186prm={}
         T186prm.update(TP.prm_186_0001)
         if self.dut.HGA_SUPPLIER == 'RHO':
            if testSwitch.FE_0134663_006800_P_T186_TDK_HEAD_SUPPORT:
               T186prm["HD_TYPE"]=(0,)
            if str(self.dut.PREAMP_MFR).find("TI")!= -1:
               T186prm["INPUT_VOLTAGE"]=(250,)
            else:
               T186prm["INPUT_VOLTAGE"]=(200,)
         elif self.dut.HGA_SUPPLIER in ['TDK','HWY']:
            if testSwitch.FE_0134663_006800_P_T186_TDK_HEAD_SUPPORT:
               T186prm["HD_TYPE"]=(1,)
            T186prm["INPUT_VOLTAGE"]=(150,)
         else:
            import ScrCmds 
            ScrCmds.raiseException(11044, "Preamp info N/A to set T186 Input voltage")
         self.oProc.St(T186prm) ##Kent: Disabled because servo code not support
         if testSwitch.FE_0139634_399481_P_DETCR_T134_T94_CHANGES and testSwitch.extern.FE_0134663_006800_T094_DETCR_CAL_REV2:
            self.oProc.St(TP.prm_094_0003)
         else:
            self.oProc.St(TP.prm_094_0002)
         objMsg.printMsg("End of DETCR")


#----------------------------------------------------------------------------------------------------------
class CdumpPreampRegs(CState):
   """
   Class that dumps preamp register values via cudacom.
   startReg & endReg ( default 0, 32 )can be controlled thru state params.
   """

   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.dut = dut
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CProcess, CCudacom
      self.oProc = CProcess()
      self.oCudacom = CCudacom()
      
      startReg = self.params.get('startReg', 0) # default to zero
      endReg   = self.params.get('endReg', 32) # default to 32
      buf, errorCode = self.oCudacom.Fn(1332,startReg,endReg)
      self.oCudacom.displayMemory(buf)
      if testSwitch.FE_0191751_231166_P_172_DUMP_PREAMP:
         from TestParamExtractor import TP
         self.oProc.St(TP.dumpPreampRegs_172)


#----------------------------------------------------------------------------------------------------------
class CDumpPreamp(CState):

   """
      Class made for calling method that dump preamp registers
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from Process import CCudacom
      self.oOudacom = CCudacom()

      if self.dut.PREAMP_TYPE in ['LSI5231','TI7550', 'LSI5830','AVAGO5831','AVAGO5832','TI7551']:
         buf, errorCode = self.oOudacom.Fn(1332, 0, 127)
         self.oOudacom.DumpMemory(buf, 0, 2)
      else:
         objMsg.printMsg('address   0  1  2  3     4  5  6  7     8  9  A  B     C  D  E  F')
         addressoffset = 0
         for i in (range(0,64)):
            if (i % 16 == 0):
               dispstr = '%08X' %(addressoffset)
               addressoffset += 0x10
            if (i < 32):
               if testSwitch.ANGSANAH:
                  buf, errorCode = self.oOudacom.Fn(1391, i, 0) # read 1st page
               else:
                  buf, errorCode = self.oOudacom.Fn(1329, i, 0) # read 1st page
            else:
               if testSwitch.ANGSANAH:
                  buf, errorCode = self.oOudacom.Fn(1391, i, 1) # read 2nd page
               else:
                  buf, errorCode = self.oOudacom.Fn(1329, i, 1) # read 2nd page
            bufBytes = struct.unpack('BB',buf)
            dispstr = '%s %02x' %(dispstr, bufBytes[0])
            if (i % 4 == 3):  dispstr = '%s   ' %(dispstr)
            if (i % 16 == 15):
               objMsg.printMsg(dispstr)
               dispstr = ""

