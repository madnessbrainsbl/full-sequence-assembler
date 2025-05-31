# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#--------------------------------------------------------------------------------------------------------#
# Description: Copy Targets to adjacent zones,  Pete Harllee
##---------------------------------------------------------------------------------------------------------#


from Constants import *
import types, os, time, re, struct
from TestParamExtractor import TP

if testSwitch.FE_0116894_357268_SERVO_SUPPLIED_TEST_PARMS:
   from TestParamExtractor import setSrvoOverrides

from State import CState
from Drive import objDut
from Process import CCudacom
from Process import CProcess
import MessageHandler as objMsg
from Channel import CChannelAccess
if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
   from VBAR_Zones import CVbarTestZones
else:
   from VBAR import CVbarTestZones
import ScrCmds

class CCopyTargets(CState):
   """Copy targets from WP zones to all other zones."""
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
      self.data={}
      self.regIdsToCopy = []


   def run(self):
      self.oCudacom = CCudacom()
      self.oTestZones = CVbarTestZones()
      oProc = CProcess()
      CChannelAccess().setChannelType()


      if (self.dut.channelType.find('SRC_COLUMBIA_M') > -1):


         # TARGETS and TAP 3
         self.regIdsToCopy = [0xc2, 0xc3, 0xc4, 0x33]

         #SMPATTERN HI/Lo nom and SMthresh
         self.regIdsToCopy.extend([0xb3, 0xb4, 0xc8, 0x9A, ])

         #SM OFFSETS
         self.regIdsToCopy.extend([0xb7, 0xb8, 0xb9, 0xba, 0xbb, 0xbc, 0xbd, 0xbe, 0xbf])

      else:
         self.regIdsToCopy = [145,138,0xc2,0xc3,0xc4]

         if testSwitch.extern.FE_0155563_208705_FIX_DUPLICATE_REGIDS:
            # When FE_0155563_208705_FIX_DUPLICATE_REGIDS is removed,
            # please move this line of code up into the __init__ method
            # extern flags can't be referenced in __init__
            self.regIdsToCopy = [145,138,0xc8,0xc2,0xc3,0xc4]


      oProc.St({'test_num' : 255,'prm_name' : 'Show Opti'})
      objMsg.printMsg("Reading target data...")
      self.getRapData()
      objMsg.printMsg("Writing target data...")
      self.copyRapDataToOtherZones()
      oProc.St({'test_num' : 255,'prm_name' : 'Show Opti'})
      oProc.St({'test_num' : 178,'prm_name' : 'save Flash','CWORD1'   : 0x220,})

   def getRapData(self):
      for hd in range(self.dut.imaxHead):
         self.data[hd] = {}
         for zn in self.oTestZones.getTestZones():
            self.data[hd][zn] = {}
            for regid in self.regIdsToCopy:
               self.data[hd][zn][regid] = self.getRegId(regid, hd, zn)

   def copyRapDataToOtherZones(self):
      for hd in range(self.dut.imaxHead):
         for targetZone in range(self.dut.numZones):
            if targetZone not in self.oTestZones.getTestZones():
               sourceZone = self.oTestZones.getTestZnforZn(targetZone)
               for regid in self.regIdsToCopy:
                  self.writeRegId(regid, hd, targetZone, self.data[hd][sourceZone][regid])

   def getRegId(self,regId,head,zone):
      buf,errorCode = self.oCudacom.Fn(1336, regId, head, zone, retries=10)
      result = struct.unpack("HH",buf)
      return result[0]

   def writeRegId(self,regId,head,zone,value):
      buf,errorCode = self.oCudacom.Fn(1339, regId, value, head, zone, retries=10)
      result = struct.unpack("H",buf)
      if result[0] != 1:   # 1 is PASS
         ScrCmds.raiseException(11044, 'Write Channel RAM cudacom failed!')

