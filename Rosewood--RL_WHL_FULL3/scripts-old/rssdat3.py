#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#--------------------------------------------------------------------------------------------------------#
# Description: hmscap and ber meaurements
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/rssdat3.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/rssdat3.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import types, os, time, re
from TestParamExtractor import TP

from State import CState
from Drive import objDut
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
from FSO import CFSO
if testSwitch.SPLIT_VBAR_FOR_CM_LA_REDUCTION:
   from VBAR_RAP import CRapTcc
else:   
   from VBAR import CRapTcc
from Process import CProcess
from Process import CCudacom


class CCapabilityVsParams(CState):

   """
   Description:
      Implements BPI and TPI capability measurements versus a number of parameters.
      TLevel,
      Clearance Target
      Write Power
   """
   def __init__(self,dut,params={}):
      self.params = params
      depList = []
      CState.__init__(self,dut,depList)
      self.g_heads = [0]
      self.g_zones = [0,15]
      self.g_spcid = 0
      self.g_bpicap = 1.0
   #------------------------------------------------------------------------------------------------------
   def run(self):
      self.oFSO = CFSO()
      self.oFSO.getZoneTable()
      self.oRapTcc = CRapTcc()
      st(178,{'CWORD1':0x208})   #save RAP


      objMsg.printMsg("MaxHead = %d   MaxUserZone = %d" % (self.dut.imaxHead, self.dut.numZones))

      self.g_heads = range(self.dut.imaxHead)
      self.g_zones = range(self.dut.numZones)
      #self.g_zones = [0,1,15,28]


      idx = 12
      targser = 5
      for tlevel in [50]:
         for numsqueeze in [6,100]:
            for side in [12]:
               numsq = numsqueeze
               if side == 13:
                  numsq = numsqueeze + 0x8000
               if side == 14:
                  numsq = numsqueeze + 0x4000

               for hd in self.g_heads:
                  for zn in self.g_zones:
                     self.g_spcid = side*2**24 + numsqueeze*2**16 + 0*2**8 + tlevel
                     self.measureTpiCapability(hd,zn,tlevel,targser, sqz_writes=numsq)



      # HMS Capability with squeeze
      htr = 3
      numsqueeze = 6
      squeeze = 0
      idx = 9

      for side in [9,10,11]:
        for tlevel in [50]:
           for squeeze in [0,8]:
              for numsqueeze in [1,100]:
                 for hd in self.g_heads:
                    for zn in self.g_zones:
                       self.g_spcid = side*2**24 + numsqueeze*2**16 + squeeze*2**8 + tlevel
                       numsq = numsqueeze
                       if side == 10:
                         numsq = numsqueeze + 0x8000
                       if side == 11:
                         numsq = numsqueeze + 0x4000
                       self.measureHMSCapability(hd,zn,tlevel,8,0,numsq,squeeze,htr)  #calls T211


      #st(178,{'CWORD1':0x201})   # to restore the RAP
      # HMScap vs iterations = idx = 2
      numsqueeze = 0
      squeeze = 0
      idx = 2
      htr = 3
      for idx in [2]:
         for tlevel in [12,50]:
            for hd in self.g_heads:
               for zn in self.g_zones:
                  #CCudacom().Fn(1339, 234, vscale, hd, zn)
                  self.g_spcid = idx*2**24 + 0*2**16 + 0*2**8 + tlevel
                  self.measureHMSCapability(hd,zn,tlevel,8,0,numsqueeze,squeeze,htr)  #calls T211



      for idx in [15]:
         for tlevel in [50]:
            self.g_spcid = idx*2**24 + 9*2**16 + tlevel*2**8;
            self.measureBER2(tlevel)                #calls T250



      st(178,{'CWORD1':0x201})   # to restore the RAP



   #-------------------------------------------------------------------------------------------------------
   def measureBpiCapability(self, hd, zn, tlevel=0, wrPower=None, numRepeats=1):
      parms = {'test_num'           : 211,
               'prm_name'           : 'MeasureBPI_211',
               'timeout'            : 120,
               'spc_id'             : self.g_spcid,
               'NUM_TRACKS_PER_ZONE': 6,
               'ZONE_POSITION'      : 198, # work around for FLASH_LED issues in st 211 originally 199
               'BPI_MAX_PUSH_RELAX' : 40,
               'CWORD1':0x5,}

      if wrPower != None:
         wc,ovs,ovd = wrPower
         parms.update({'WRITE_CURRENT':wc, 'DAMPING':ovs, 'DURATION':ovd})
      parms.update( {'TEST_HEAD': hd, 'ZONE': zn, 'TLEVEL': tlevel} )
      data = []
      for i in range(numRepeats):
         try:
            CProcess().St(parms)
         except:
            pass
         bpicapability = float(self.dut.dblData.Tables('P211_BPI_CAP_AVG').tableDataObj()[-1]['BPI_CAP_AVG'])
         data.append(bpicapability)
      self.g_bpicap = sum(data)/len(data)
      return 0

   def measureTpiCapability(self, hd, zn, tlevel=0, targser=15, wrPower=None, sqz_writes=6, numRepeats=1):
      parms = {'test_num'           : 211,
               'prm_name'           : 'MeasureTPI_211',
               'timeout'            : 2000,
               'spc_id'             : self.g_spcid,
               'NUM_TRACKS_PER_ZONE': 6,
               'TARGET_SER'         : 15,
               'TPI_TARGET_SER'     : 15,
               'ZONE_POSITION'      : 198, # work around for FLASH_LED issues in st 211 originally 199
               'CWORD1'             : 0x26,
               }

      #parms.update( {'ADJ_BPI_FOR_TPI': int(self.g_bpicap*100 - 105)} )
      parms.update( {'ADJ_BPI_FOR_TPI': 0} )

      if wrPower != None:
         wc,ovs,ovd = wrPower
         parms.update({'WRITE_CURRENT':wc, 'DAMPING':ovs, 'DURATION':ovd})

      parms.update( {'TEST_HEAD': hd, 'ZONE': zn, 'TPI_TLEVEL': tlevel, 'TARGET_SER': targser, 'NUM_SQZ_WRITES': sqz_writes,} )

      for i in range(numRepeats):
         try:
            CProcess().St(parms)
         except:
            pass
      return 0

   #-------------------------------------------------------------------------------------------------------

   def measureHMSCapability(self, hd, zn, tlevel=0, pctbpi=8, zonepos=0, numsqz=0, sqz=0, htr=3, wrPower=None, numRepeats=1):
      parms = {'test_num'           : 211,
               'prm_name'           : 'MeasureHMS_211',
               'timeout'            : 3000,
               'spc_id'             : self.g_spcid,
               'NUM_TRACKS_PER_ZONE': 6,
               'THRESHOLD'          : 0,
               'TARGET_SER'         : 1,
               'HMS_STEP'           : 1,
               'HMS_START'          : 20,
               'HMS_MAX_PUSH_RELAX' : 100,
               'NUM_SQZ_WRITES'     : numsqz,
               'START_OT_FOR_TPI'   : sqz,
               'ZONE_POSITION'      : 198, # work around for FLASH_LED issues in st 211 originally 199
               'TLEVEL'             : 2,
               'CWORD1'             : 0x6000|12,
               'CWORD2'             : htr,}

      #parms.update( {'ADJ_BPI_FOR_TPI': int(self.g_bpicap*100-100)+pctbpi-8} )     # uncomment when running prior to VBAR
      parms.update( {'ADJ_BPI_FOR_TPI': pctbpi-8} )
      parms.update( {'ZONE_POSITION': 198-zonepos*48} )

      if wrPower != None:
         wc,ovs,ovd = wrPower
         parms.update({'WRITE_CURRENT':wc, 'DAMPING':ovs, 'DURATION':ovd})
      parms.update( {'TEST_HEAD': hd, 'ZONE': zn, 'TLEVEL': tlevel} )


      for i in range(numRepeats):
         try:
            CProcess().St(parms)
         except:
            pass
      return 0

   #-------------------------------------------------------------------------------------------------------
   def measureBER(self, tlevel=0, wrPower=None, numRepeats=1):
      zone_mask_low = 0
      zone_mask_high = 0
      for zn in self.g_zones:
         if zn < 32:
            zone_mask_low |= (1 << zn)
         else:
            zone_mask_high |= (1 << (zn -32))

      #zmask = 0
      #for zone in self.g_zones:
      #   zmask += 2**zone

      hmask = 0
      nheads = 0
      for h in self.g_heads:
         hmask += 2**h
         nheads += 1

      parms = {'test_num'           : 250,
               'prm_name'           : 'MeasureBER_250',
               'timeout'            : 2500 * nheads,
               'spc_id'             : self.g_spcid,
               'ZONE_POSITION'      : 198,     # work around for FLASH_LED issues in st 211 originally 199
               'TEST_HEAD'          : 0xff,
               #'ZONE_MASK'          : [zmask/65536,zmask%65536],
               'ZONE_MASK'          : [zone_mask_low/65536,zone_mask_low%65536],
               'ZONE_MASK_EXT'      : [zone_mask_high/65536,zone_mask_high%65536],
               'WR_DATA'            : (0x00),         # 1 byte for data pattern if writing first
               'MAX_ERR_RATE'       : -100,
               'MINIMUM'            : -20,            # Minimum BER spec
               'NUM_TRACKS_PER_ZONE': 10,
               'CWORD1'             : 0x0107,}
      #parms.update( {'TLEVEL': tlevel} )
      parms.update( {'MAX_ITERATION': tlevel} )


      for i in range(numRepeats):
         try:
            CProcess().St(parms)
         except:
            pass
      return 0


   def measureROBER(self, tlevel=0, wrPower=None, numRepeats=1):

      zone_mask_low = 0
      zone_mask_high = 0
      for zn in self.g_zones:
         if zn < 32:
            zone_mask_low |= (1 << zn)
         else:
            zone_mask_high |= (1 << (zn -32))

      #zmask = 0
      #for zone in self.g_zones:
      #   zmask += 2**zone

      hmask = 0
      nheads = 0
      for h in self.g_heads:
         hmask += 2**h
         nheads += 1

      parms = {'test_num'           : 250,
               'prm_name'           : 'MeasureBER_250',
               'timeout'            : 2500 * nheads,
               'spc_id'             : self.g_spcid,
               'ZONE_POSITION'      : 198,     # work around for FLASH_LED issues in st 211 originally 199
               'TEST_HEAD'          : 0xff,
               #'ZONE_MASK'          : [zmask/65536,zmask%65536],
               'ZONE_MASK'          : [zone_mask_low/65536,zone_mask_low%65536],
               'ZONE_MASK_EXT'      : [zone_mask_high/65536,zone_mask_high%65536],               'WR_DATA'            : (0x00),         # 1 byte for data pattern if writing first
               'MAX_ERR_RATE'       : -100,
               'MINIMUM'            : -20,            # Minimum BER spec
               'NUM_TRACKS_PER_ZONE': 50,
               'CWORD1'             : 0x0117,}
      #parms.update( {'TLEVEL': tlevel} )
      parms.update( {'MAX_ITERATION': tlevel} )


      for i in range(numRepeats):
         try:
            CProcess().St(parms)
         except:
            pass
      return 0


   #-------------------------------------------------------------------------------------------------------
   def measureBER2(self, tlevel=0, wrPower=None, numRepeats=1):

      zone_mask_low = 0
      zone_mask_high = 0
      for zn in self.g_zones:
         if zn < 32:
            zone_mask_low |= (1 << zn)
         else:
            zone_mask_high |= (1 << (zn -32))

      #zmask = 0
      #for zone in self.g_zones:
      #   zmask += 2**zone

      hmask = 0
      nheads = 0
      for h in self.g_heads:
         hmask += 2**h
         nheads += 1

      parms = {'test_num'           : 250,
               'prm_name'           : 'MeasureBER_250',
               'timeout'            : 2500 * nheads,
               'spc_id'             : self.g_spcid,
               'ZONE_POSITION'      : 198,     # work around for FLASH_LED issues in st 211 originally 199
               'TEST_HEAD'          : 0xff,
               #'ZONE_MASK'          : [zmask/65536,zmask%65536],
               'ZONE_MASK'          : [zone_mask_low/65536,zone_mask_low%65536],
               'ZONE_MASK_EXT'      : [zone_mask_high/65536,zone_mask_high%65536],
               'WR_DATA'            : (0x00),         # 1 byte for data pattern if writing first
               'MAX_ERR_RATE'       : -90,
               'MINIMUM'            : -20,            # Minimum BER spec
               'NUM_TRACKS_PER_ZONE': 50,
               'CWORD1'             : 0x0903,}

      #parms.update( {'TLEVEL': tlevel} )
      parms.update( {'MAX_ITERATION': tlevel} )


      for i in range(numRepeats):
         try:
            CProcess().St(parms)
         except:
            pass
      return 0


   #-------------------------------------------------------------------------------------------------------
   def measureROBER2(self, tlevel=0, wrPower=None, numRepeats=1):

      zone_mask_low = 0
      zone_mask_high = 0
      for zn in self.g_zones:
         if zn < 32:
            zone_mask_low |= (1 << zn)
         else:
            zone_mask_high |= (1 << (zn -32))

      #zmask = 0
      #for zone in self.g_zones:
      #   zmask += 2**zone
      hmask = 0
      nheads = 0
      for h in self.g_heads:
         hmask += 2**h
         nheads += 1

      parms = {'test_num'           : 250,
               'prm_name'           : 'MeasureBER_250',
               'timeout'            : 2500 * nheads,
               'spc_id'             : self.g_spcid,
               'ZONE_POSITION'      : 198,     # work around for FLASH_LED issues in st 211 originally 199
               'TEST_HEAD'          : 0xff,
               #'ZONE_MASK'          : [zmask/65536,zmask%65536],
               'ZONE_MASK'          : [zone_mask_low/65536,zone_mask_low%65536],
               'ZONE_MASK_EXT'      : [zone_mask_high/65536,zone_mask_high%65536],
               'WR_DATA'            : (0x00),         # 1 byte for data pattern if writing first
               'MAX_ERR_RATE'       : -96,
               'MINIMUM'            : -20,            # Minimum BER spec
               'NUM_TRACKS_PER_ZONE': 50,
               'CWORD1'             : 0x0913,}

      #parms.update( {'TLEVEL': tlevel} )
      parms.update( {'MAX_ITERATION': tlevel} )


      for i in range(numRepeats):
         try:
            CProcess().St(parms)
         except:
            pass
      return 0


   #-------------------------------------------------------------------------------------------------------
   def set_write_pwr_idx(self, wrPowerIdx,head=0xff,zone=0xff):
      self.oRapTcc.updateWP(0,0,wrPowerIdx,setAllZonesHeads=1)
      self.updateHeaterSettings()
   #-------------------------------------------------------------------------------------------------------
   def setWritePower(self, wrPower):

      iw,iwo,iwod = wrPower

      bitmask = 0
      for zone in g_zones:
         bitmask += 2**zone

      headrange = 0
      for h in g_heads:
         headrange += 2**h

      parms = {'test_num'            : 178,
               'BIT_MASK'            : [bitmask/65536, bitmask%65536],
               'CWORD1'              : 512,
               'WRITE_CURRENT_OFFSET': [0, 0],
               'CWORD2'              : 0x7,
               'HEAD_RANGE'          : headrange,
               'WRITE_CURRENT'       : iw,
               'DAMPING'             : iwo,
               'DURATION'            : iwod,
               }

      CProcess().St(parms)
      self.updateHeaterSettings()
   #-------------------------------------------------------------------------------------------------------
   def updateHeaterSettings(self):
      t49_parms = {'test_num' : 49,     # force update of heaters
                   'CWORD1'   : 6,
                   }

      CProcess().St(t49_parms)

   def display_clearance(self):
      t172_parms = {'test_num' : 172,     # force update of heaters
                    'spc_id'   : self.g_spcid,
                    'CWORD1'   : 5,
                   }

      CProcess().St(t172_parms)

   def display_heat(self):
      t172_parms = {'test_num' : 172,     # force update of heaters
                    'spc_id'   : self.g_spcid,
                    'CWORD1'   : 4,
                   }

      CProcess().St(t172_parms)



   #-------------------------------------------------------------------------------------------------------

   def setOclim(self, oclim):

      InputOclim = oclim

      parms = {'test_num'            : 178,
               'CWORD1'              : 0x0400,
               'SET_OCLIM'           : InputOclim,
               'BIT_MASK': [1L, 65535],
               'HEAD_RANGE': [255],
              }

      CProcess().St(parms)

   def set_clearance(self,writeclr=None,readclr=None):
      params = {'test_num' : 178,
                'TGT_WRT_CLR': [23],
                'TGT_RD_CLR': [33],
                'spc_id': 1,
                'TGT_MAINTENANCE_CLR': [23],
                'BIT_MASK': [1L, 65535],
                'TGT_PREWRT_CLR': [23],
                'HEAD_RANGE': [255],
                'timeout': 600,
                'CWORD2': [1920],
                'CWORD1': [8708],
                }

      zonebitmask = 0
      for zone in self.g_zones:
         if zone == 0xff:
            zonebitmask = 0xffffffff
            break
         zonebitmask += 1 << zone
      params['BIT_MASK'] = [zonebitmask / 65536, zonebitmask % 65536]
      headmask = 0
      for h in self.g_heads:
         headmask += 1 << h
      params['HEAD_RANGE']=headmask

      if not writeclr == None:
         params['CWORD2']=0x580
         params['TGT_WRT_CLR']=writeclr
         params['TGT_MAINTENANCE_CLR']=writeclr
         params['TGT_PREWRT_CLR']=writeclr

      if not readclr == None:
         params['CWORD2'] |= 0x0200
         params['TGT_RD_CLR']=readclr

      CProcess().St(params)
      self.updateHeaterSettings()


   def set_passiveclearance(self,heatclr=150,whclr=150):
      params = {'test_num' : 178,
                'MEASURED_HEAT_CLR': [150],
                'MEASURED_WRT_HEAT_CLR': [150],
                'spc_id': 1,
                'TGT_MAINTENANCE_CLR': [23],
                'BIT_MASK': [1L, 65535],
                'TGT_PREWRT_CLR': [23],
                'HEAD_RANGE': [255],
                'timeout': 600,
                'CWORD2': [6144],
                'CWORD1': [8708],
                }

      zonebitmask = 0
      for zone in self.g_zones:
         if zone == 0xff:
            zonebitmask = 0xffffffff
            break
         zonebitmask += 1 << zone
      params['BIT_MASK'] = [zonebitmask / 65536, zonebitmask % 65536]
      headmask = 0
      for h in self.g_heads:
         headmask += 1 << h
      params['HEAD_RANGE']=headmask

      params['MEASURED_HEAT_CLR']=heatclr
      params['MEASURED_WRT_HEAT_CLR']=whclr

      CProcess().St(params)
      self.updateHeaterSettings()


