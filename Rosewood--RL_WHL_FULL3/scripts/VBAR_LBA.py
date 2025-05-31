#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Vbar LBA Tools Module
#  - Contains various LBA related functions
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VBAR_LBA.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/VBAR_LBA.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from Drive import objDut
import MessageHandler as objMsg
from FSO import CFSO


#----------------------------------------------------------------------------------------------------------
class CVBAR_LBA(object):
   """
      Base class for waterfall tools
   """
   def __init__(self):
      self.dut = objDut
      self.mFSO = CFSO()
   
   #-------------------------------------------------------------------------------------------------------
   def sendMaxLBACmdBySectorSize(self, lbas, sector_size):
      # This call will silently fail if invoked without the proper flag set true
      prm = {
               'test_num'    : 178,
               'prm_name'    : 'Set Max LBA',
               'timeout'     : 1800,
               'CWORD1'      : 0x260,
               'SECTOR_SIZE' : sector_size,
               'NUM_LBAS'    : self.mFSO.oUtility.ReturnTestCylWord(lbas & 0xFFFFFFFF),
            }

      if testSwitch.extern.LBA_WIDER_THAN_32_BITS:
         prm['NUM_LBAS_HI'] = self.mFSO.oUtility.ReturnTestCylWord((lbas>>32) & 0x0000FFFF)

      self.mFSO.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def sendMaxLBACmd(self, lbas, offset):
      prm = {
               'test_num' : 178,
               'prm_name' : 'Set Max LBA',
               'timeout'  : 1800,
               'CWORD1'   : 0x260,
               'OFFSET'   : offset,
               'NUM_LBAS' : self.mFSO.oUtility.ReturnTestCylWord(lbas & 0xFFFFFFFF),
            }

      if testSwitch.extern.LBA_WIDER_THAN_32_BITS:
         prm['NUM_LBAS_HI'] = self.mFSO.oUtility.ReturnTestCylWord((lbas>>32) & 0x0000FFFF)

      self.mFSO.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def setMaxLBAForAudit(self):
      # TODO: test
      if not testSwitch.virtualRun:
         numPBAs = self.dut.numPBAs
      else:
         colDict = self.dut.dblData.Tables('P000_DRIVE_PBA_COUNT').columnNameDict()
         row = self.dut.dblData.Tables('P000_DRIVE_PBA_COUNT').rowListIter(index=len(self.dut.dblData.Tables('P000_DRIVE_PBA_COUNT'))-1).next()
         numPBAs = float(row[colDict['DRIVE_NUM_PBAS']])

      max_lba_val = int(0.998*numPBAs)# allow for spares
      self.sendMaxLBACmd(max_lba_val, 0)

   #-------------------------------------------------------------------------------------------------------
   def setMaxLBA(self, niblet=None):
      if niblet:
         media_cache_capacity = niblet.settings['MEDIA_CACHE_CAPACITY']
         if testSwitch.FE_0308542_348085_P_DESPERADO_3:
            copy_forward_overhead = niblet.settings['COPY_FORWARD_OVERHEAD']
         capacity    = niblet.settings['DRIVE_CAPACITY']
         if testSwitch.FE_0125707_340210_CAP_FROM_BPIFILE:
            capacity_4K = niblet.settings['NumHeads'] * niblet.settings['CapacityTarget4K'] * self.bpiFile.getNominalCapacity()
         else:
            capacity_4K = niblet.settings['NumHeads'] * niblet.settings['CapacityTarget4K'] * TP.VbarCapacityGBPerHead
         capacity -= media_cache_capacity
         capacity_4K -= media_cache_capacity
         if testSwitch.FE_0308542_348085_P_DESPERADO_3:
            capacity -= copy_forward_overhead
            capacity_4K -= copy_forward_overhead
      else:
         if testSwitch.FE_0125707_340210_CAP_FROM_BPIFILE:
            capacity    = self.numHeads * self.bpiFile.getNominalCapacity()
            capacity_4K = self.numHeads * self.bpiFile.getNominalCapacity()
         else:
            capacity    = self.numHeads * TP.VbarCapacityGBPerHead
            capacity_4K = self.numHeads * TP.VbarCapacityGBPerHead

      if testSwitch.FE_0139240_208705_P_IMPROVED_MAX_LBA_CALC :
         import lbacalc
         # Use the INTERFACE attribute to determine SAS vs SATA
         if self.dut.drvIntf in TP.WWN_INF_TYPE.get('WW_SAS_ID', []) or self.dut.drvIntf == 'SAS':
            # SAS
            sectorsizes = [(512, capacity), (520, capacity), (524, capacity), (528, capacity), (4096, capacity_4K)]
            lbafunc = lbacalc.sasCapToLba
         else:
            # SATA
            sectorsizes = [(512, capacity), (4096, capacity_4K)]
            lbafunc = lbacalc.sataCapToLba

         # Send the max LBA values to the drive
         for sectorsize, cap in sectorsizes:
            if testSwitch.BF_0144913_208705_P_SET_CAPACITY_NOT_MAX_LBA:
               # F3 actually expects capacity, rather than max LBA, else format issues  can be encountered
               max_lba_val = lbafunc(cap, sectorsize)
            else:
               max_lba_val = lbafunc(cap, sectorsize) - 1
            self.sendMaxLBACmdBySectorSize(max_lba_val, sectorsize)
      else:
         # Set for 512 sectors
         max_lba_val = self.IDEMAMaxLBA_512(capacity)
         self.sendMaxLBACmdBySectorSize(max_lba_val, 512)

         # Set for 4K sectors
         if testSwitch.SGP_4K_MAX_LBA_CALCULATION:
            max_lba_val = int(max_lba_val/8)
         else:
            max_lba_val = self.IDEMAMaxLBA_4K(capacity_4K)

         try:
            self.sendMaxLBACmdBySectorSize(max_lba_val, 4096)
         except ScriptTestFailure:
            objMsg.printMsg("WARNING: second update to SetMAXLBA fails - Possibly 512 sector size. Moving on...")

         if testSwitch.FE_0131645_208705_MAX_LBA_FOR_SAS :
            # This section is attempting to add 520, 524, and 528 byte sector entries into the RAP for SAS drives
            # Given the urgency of the change, I've elected to just make an incremental change to get drives
            # through the process.  Long term, how we manage capacity both in the niblet and in the max LBA fields
            # in the RAP needs to be improved, so there's less hard-coding and implicit assumptions in this section
            # of the code.
            for sector_size in (520, 524, 528):
               max_lba_val = self.IDEMAMaxLBA(capacity, sector_size)
               self.sendMaxLBACmdBySectorSize(max_lba_val, sector_size)

   #-------------------------------------------------------------------------------------------------------
   # General function to generate the IDEMA max LBA for a given capacity
   if not testSwitch.FE_0139240_208705_P_IMPROVED_MAX_LBA_CALC :
      #----------------------------------------------------------------------------------------------------
      def IDEMAMaxLBA(self, capacity, sector_size):
         num_lbas = int((97696368 + 1953504 * (capacity - 50.0)) / (sector_size / 512.0) + 1) # always round up
         return num_lbas - 1 # return the max LBA

      #----------------------------------------------------------------------------------------------------
      def IDEMAMaxLBA_4K(self, capacity):
         return int(round((((97696368 + (1953504 * (capacity - 50.0)))+7)/8)+1))

      #----------------------------------------------------------------------------------------------------
      def IDEMAMaxLBA_512(self, capacity):
         return int(round(97696368 + (1953504 * (capacity - 50.0))))
