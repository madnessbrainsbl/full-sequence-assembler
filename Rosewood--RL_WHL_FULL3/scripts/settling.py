#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/settling.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/settling.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import types, os, time, random, re
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
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oFSO = CFSO()
      self.oFSO.getZoneTable()
      self.oRapTcc = CRapTcc()

      objMsg.printMsg("SETTLING START")
      st(178,{'CWORD1':0x208})   #save RAP

      objMsg.printMsg("MaxHead = %d   MaxUserZone = %d" % (self.dut.imaxHead, self.dut.numZones))

      self.g_heads = range(self.dut.imaxHead)
      self.g_zones = range(self.dut.numZones)
      #QH moved 2 zone specification until after HMSCap measurement in all zones

      target_writeclr = 15   # replace this with query to get current target write clearance
      target_readclr = 25    # replace this with query to get current target read clearance
      self.set_clearance(target_writeclr,target_readclr)  # remove this

     #QH added HMSCap collection


      squeeze = 0
      htr = 3
      for idx3 in [8]:
         for numsqueeze in [0]:
            for tlevel in [12,50]:
               for hd in self.g_heads:
                  for zn in self.g_zones:
                     #CCudacom().Fn(1339, 234, vscale, hd, zn)
                     self.g_spcid = idx3*2**24 + numsqueeze*2**16 + tlevel*2**8
                     self.measureHMSCapability(hd,zn,tlevel,8,0,numsqueeze,squeeze,htr)  #calls T211

      self.g_zones = [1,self.dut.numZones-2]

      idx1 = 0
      idx2 = 0
      for idx3 in [1,2,3,4]:
         for clr in [0,2,4,6,8,10,12,14,16,18]:
            self.set_clearance(target_writeclr+clr,target_readclr+clr)
            self.g_spcid = idx3*2**24 + idx2*2**16 + idx1*2**8 + clr
            self.measureBER2(50)

      self.set_clearance(target_writeclr,target_readclr)  # set clearance back for settling measurement

      for idx3 in [5,6]:    #[5,6]
         for idx2 in [30,60]:   #[30,90]
            self.unload_and_wait(idx2*60)
            for idx1 in range(30):  #range(30)
               for clr in [8,0]:
                  self.set_clearance(target_writeclr+clr,target_readclr+clr)
                  self.g_spcid = idx3*2**24 + idx2*2**16 + idx1*2**8 + clr
                  self.measureBER2(50)
               if idx1 > 10 :
                  time.sleep(3*(idx1-10))


      objMsg.printMsg("SETTLING END")


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


   def measureTpiCapability(self, hd, zn, tlevel=0, wrPower=None, numRepeats=1):
      parms = {'test_num'           : 211,
               'prm_name'           : 'MeasureTPI_211',
               'timeout'            : 120,
               'spc_id'             : self.g_spcid,
               'NUM_TRACKS_PER_ZONE': 6,
               'ZONE_POSITION'      : 198, # work around for FLASH_LED issues in st 211 originally 199
               'BPI_MAX_PUSH_RELAX' : 40,
               'CWORD1':0x6,}

      parms.update( {'ADJ_BPI_FOR_TPI': int(self.g_bpicap*100 - 105)} )

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
               'TLEVEL'             : 12,
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
               'ZONE_MASK'          : [zone_mask_low/65536,zone_mask_low%65536],
               'ZONE_MASK_EXT'          : [zone_mask_high/65536,zone_mask_high%65536],
               'WR_DATA'            : (0x00),         # 1 byte for data pattern if writing first
               'MAX_ERR_RATE'       : -60,
               'MINIMUM'            : -20,            # Minimum BER spec
               'CWORD1'             : 0x0007,}
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
               'ZONE_MASK'          : [zone_mask_low/65536,zone_mask_low%65536],
               'ZONE_MASK_EXT'          : [zone_mask_high/65536,zone_mask_high%65536],
               'WR_DATA'            : (0x00),         # 1 byte for data pattern if writing first
               'MAX_ERR_RATE'       : -60,
               'MINIMUM'            : -14,            # Minimum BER spec
               'CWORD1'             : 0x0803,}

      #parms.update( {'TLEVEL': tlevel} )
      parms.update( {'MAX_ITERATION': tlevel} )
      parms.update( {'ITERATIONS': 0} )


      for i in range(numRepeats):
         try:
           CProcess().St(parms)
         except:
           pass
      return 0

   def measureBER3(self, tlevel=0, wrPower=None, numRepeats=1):

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
               'ZONE_MASK'          : [zone_mask_low/65536,zone_mask_low%65536],
               'ZONE_MASK_EXT'          : [zone_mask_high/65536,zone_mask_high%65536],
               'WR_DATA'            : (0x00),         # 1 byte for data pattern if writing first
               'MAX_ERR_RATE'       : -60,
               'MINIMUM'            : -20,            # Minimum BER spec
               'CWORD1'             : 0x0803,}

      #parms.update( {'TLEVEL': tlevel} )
      parms.update( {'MAX_ITERATION': tlevel} )
      parms.update( {'ITERATIONS': 12} )


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

      #bitmask = 0
      #for zone in g_zones:
      #  bitmask += 2**zone
      bitmask_low = 0
      bitmask_high = 0
      for zone in g_zones:
         if zone < 32:
            bitmask_low += 2**zone
         else:
            bitmask_high += 2**(zone-32)
      headrange = 0
      for h in g_heads:
         headrange += 2**h

      parms = {'test_num'            : 178,
               #'BIT_MASK'            : [bitmask/65536, bitmask%65536],
               'BIT_MASK'            : [bitmask_low/65536, bitmask_low%65536],
               'BIT_MASK_EXT'        : [bitmask_high/65536, bitmask_high%65536],
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

      #zonebitmask = 0
      #for zone in self.g_zones:
      #   if zone == 0xff:
      #      zonebitmask = 0xffffffff
      #      break
      #   zonebitmask += 1 << zone
      #params['BIT_MASK'] = [zonebitmask / 65536, zonebitmask % 65536]
      zonebitmask_low = 0
      zonebitmask_high = 0
      for zone in self.g_zones:
         if zone == 0xff:
            zonebitmask_low = 0xffffffff
            zonebitmask_high = 0xffffffff
            break
         elif zone < 32:
            zonebitmask_low += 1<<zone
         else:
            zonebitmask_high += 1<<(zone - 32)
      params['BIT_MASK'] = [zonebitmask_low / 65536, zonebitmask_low % 65536]
      params['BIT_MASK_EXT'] = [zonebitmask_high / 65536, zonebitmask_high % 65536]
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

      #zonebitmask = 0
      #for zone in self.g_zones:
      #   if zone == 0xff:
      #      zonebitmask = 0xffffffff
      #      break
      #   zonebitmask += 1 << zone
      #params['BIT_MASK'] = [zonebitmask / 65536, zonebitmask % 65536]
      zonebitmask_low = 0
      zonebitmask_high = 0
      for zone in self.g_zones:
         if zone == 0xff:
            zonebitmask_low = 0xffffffff
            zonebitmask_high = 0xffffffff
            break
         elif zone < 32:
            zonebitmask_low += 1<<zone
         else:
            zonebitmask_high += 1<<(zone - 32)
      params['BIT_MASK'] = [zonebitmask_low / 65536, zonebitmask_low % 65536]
      params['BIT_MASK_EXT'] = [zonebitmask_high / 65536, zonebitmask_high % 65536]
      headmask = 0
      for h in self.g_heads:
            headmask += 1 << h
      params['HEAD_RANGE']=headmask

      params['MEASURED_HEAT_CLR']=heatclr
      params['MEASURED_WRT_HEAT_CLR']=whclr

      CProcess().St(params)
      self.updateHeaterSettings()

   # objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # power cycle to overcome the measurement (T211) exception
         #unload the heads
   def unload_and_wait(self,waittime=5):

      parms = {'test_num'           : 11,
               'prm_name'              : 'Unload_11',
               'PARAM_0_4'             : [0x0E00,0,0,0,0]}
      try:
        CProcess().St(parms)
      except:
        pass


      time.sleep(waittime)

      parms = {'test_num'           : 11,
               'prm_name'              : 'Load_11',
               'PARAM_0_4'             : [0x0F00,0,0,0,0]}

      try:
        CProcess().St(parms)
      except:
        pass





