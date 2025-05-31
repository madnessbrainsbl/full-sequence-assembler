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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_PRETest.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_PRETest.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl


#----------------------------------------------------------------------------------------------------------
class CSigmundInFactoryCal(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = dict(params)
      depList = []
      CState.__init__(self, dut, depList)
      self.numHeads = self.dut.imaxHead
      self.numZones = self.dut.numZones

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import CFSO
      self.oFSO = CFSO()

      prm = TP.sif_prm_322.copy()
      target_zone = [30]*self.numHeads
      self.oFSO.getZnTblInfo(spc_id = 1000, supressOutput = 0, prm_name = 'Zone table (Default)')
      self.oFSO.St({'test_num': 210,'prm_name': 'Capacity (Before SIF)','SCALED_VAL': 10000, 'timeout': 2200, 'spc_id': 2, 'CWORD1': 8})
      self.oFSO.St({'test_num':238,'MJOG_FOM_THRESHOLD': 800, 'SYNC_BYTE_CONTROL': 640, 'spc_id': 1, 'TARGET_TRK_WRITES': 3, 'THRESHOLD2': 435, 'timeout': 10000, 'MAX_ERROR': 100, 'THRESHOLD': 38, 'SET_OCLIM': 1228, 'INCREMENT': 6, 'NUM_SAMPLES': 2, 'NUM_ADJ_ERASE': 3, 'TEST_HEAD': (0,), 'CWORD2': 1, 'CWORD1': 24583, 'S_OFFSET': 0})
      
      try:
         p238MicrojogZeroSkewTble = self.dut.dblData.Tables('P238_MICROJOG_ZERO_SKEW').tableDataObj()
         for index in range(len(p238MicrojogZeroSkewTble)):
            head       = int(p238MicrojogZeroSkewTble[index]['HD_LGC_PSN'])
            zone       = int(p238MicrojogZeroSkewTble[index]['ZONE'])
            if zone == (self.numZones + 1): # second system zone
               target_zone[head] = self.numZones
            else:
               target_zone[head] = zone
      except:
         objMsg.printMsg("Unable to get P238_MICROJOG_ZERO_SKEW. Use default")
         target_zone = [30]*self.numHeads

      try:
         p176HdGapDeltaTble = self.dut.dblData.Tables('P176_HD_GAP_DELTA').tableDataObj()
      except:
         objMsg.printMsg("Unable to get P176_HD_GAP_DELTA")

      for index in range(len(p176HdGapDeltaTble)):
         head       = int(p176HdGapDeltaTble[index]['HD_LGC_PSN'])
         zone       = int(p176HdGapDeltaTble[index]['DATA_ZONE'])
         hd_gap_uin_float = float(p176HdGapDeltaTble[index]['HD_GAP_UIN'])

         if zone == target_zone[head]:
            prm['SIF_W2R_BY_HEAD_EXT'][head] = int(hd_gap_uin_float * 100)
      
      objMsg.printMsg(" prm['SIF_W2R_BY_HEAD_EXT'] %s "% (str(prm['SIF_W2R_BY_HEAD_EXT'])) )

      from  PackageResolution import PackageDispatcher
      from Drive import objDut
      try:
         SIGfilename = PackageDispatcher(objDut, 'SIG').getFileName()
         objMsg.printMsg("SIGfilename %s" % str(SIGfilename))
      except:
        SIGfilename = ''
        pass

      prm['dlfile'] = (CN,SIGfilename)

      self.oFSO.St(prm)

      objPwrCtrl.powerCycle(5000,12000,10,30)


#----------------------------------------------------------------------------------------------------------
class CSigmundInFactorySetFormat(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = dict(params)
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import CFSO
      self.oFSO = CFSO()

      # Run MDW ZONE OFFSET BOUNDARY CAL
      if testSwitch.FE_0184102_326816_ZONED_SERVO_SUPPORT:
         prmT73 = self.oFSO.oUtility.copy(TP.ZoneBoundaryCal_vcatOn_73)
         if (testSwitch.extern.FE_0297957_356996_T73_USE_FLOATING_POINT_FREQ == 1):
            if testSwitch.CHEOPSAM_LITE_SOC:
               prmT73['FREQ'] = 11980
            else:
               prmT73['FREQ'] = 11875
         self.oFSO.St(TP.spinupPrm_1)
         self.oFSO.St(prmT73)

      # Program bpi
      from VBAR import CReloadBPINominal
      oReloadBPINominal = CReloadBPINominal(self.dut, self.params)
      oReloadBPINominal.run()
      oReloadBPINominal = None # GC            
      #self.oFSO.St({'test_num': 210, 'prm_name': 'Set and Save SIF BPI to RAP', 'timeout': 1800, 'spc_id': 0, 'ZONE': 15163, 'HEAD_MASK': 3, 'BPI_GROUP_EXT': [140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140], 'CWORD2': 0, 'CWORD1': 257})
      self.oFSO.saveRAPtoFLASH()
      objPwrCtrl.powerCycle(5000,12000,10,30)
      
      #update system zone location as SIF will shift user zones
      self.oFSO.getZoneTable(newTable = 1, delTables = 1, supressOutput = 0, spc_id = 1001, prm_name = 'Zone table (SIF)')
      self.oFSO.St({'test_num': 210,'prm_name': 'Capacity (After SIF)','SCALED_VAL': 10000, 'timeout': 2200, 'spc_id': 3, 'CWORD1': 8})


#----------------------------------------------------------------------------------------------------------
class CRestoreSifBpiBinToPCFile(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = dict(params)
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.USE_TEST231_RETRIVE_BPI_PROFILE_FILE:
         from RdWr import CSifBpiBinFile
         oCSifBpiBinFile = CSifBpiBinFile()
         oCSifBpiBinFile.Retrieve_SifBpiBin_From_Disc()
      else:
         from Process import CProcess
         self.oProcess = CProcess()
         self.oProcess.St({'test_num': 210, 'prm_name': 'Restore SIF/BPI to PC files','timeout': 7200, 'CWORD3':0x04, })
         objPwrCtrl.powerCycle(5000,12000,10,30)


#----------------------------------------------------------------------------------------------------------
class CStoreSifBpiBinToDisc(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = dict(params)
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from RdWr import CSifBpiBinFile
      oCSifBpiBinFile = CSifBpiBinFile()
      oCSifBpiBinFile.Save_SifBpiBin_To_Disc()


#----------------------------------------------------------------------------------------------------------
class CReloadFormat(CState):

   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = dict(params)
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):

      from FSO import CFSO
      self.oFSO = CFSO()
      
      self.oFSO.St({'test_num':210,'timeout': 600, 'CWORD1': 32})
      mode = self.params.get('MODE', 'BOTH')
      prm = {'test_num':210,'spc_id': 0, 'timeout': 1800,
                        'ZONE'              : 0xFF,
                        'HEAD_MASK'         : 0xFF,
                        'CWORD2'            : 0x03B0,
                        'CWORD1'            : 0x0100,
                        }
      if mode in ['BPI', 'BOTH']:
         bpi_format = self.params.get('BPI', -1)
         if bpi_format == -1: # Load BPI File
            from bpiFile import CBpiFile
            self.bpiFile = CBpiFile(load_conf_file_only = 1)
            bpi_format = self.bpiFile.getNominalFormat()
         bpi = [bpi_format] * 16
         prm.update({
            'BPI_GROUP_EXT'      : bpi,
            'CWORD1'             : prm['CWORD1'] | 0x1,
            })
      if mode in ['TPI', 'BOTH']:
         tpi_format = self.params.get('TPI',1.0)
         tpi_format = int(float(1.0/tpi_format) * 32768)
         tpi = [tpi_format] * 16
         prm.update({
            'SHINGLED_DIRECTION': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'TRACKS_PER_BAND'   : [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            'TRK_GUARD_TBL'     : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'MICROJOG_SQUEEZE'  : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'TRK_PITCH_TBL'     : tpi,
            'CWORD1'            : prm['CWORD1'] | 0x2,
            })

      if not testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
         from PackageResolution import PackageDispatcher
         prm['dlfile'] = (CN, PackageDispatcher(self.dut, 'BPI').getFileName())

      self.oFSO.St(prm)
      self.oFSO.saveRAPSAPtoFLASH()
      self.oFSO.getZoneTable(newTable = 1, delTables = 1, supressOutput = 0, spc_id = 15)


#----------------------------------------------------------------------------------------------------------

