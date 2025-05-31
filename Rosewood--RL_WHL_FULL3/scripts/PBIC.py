#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: This module holds all related classes and functions for performing optimizations
#              related to VBAR and format selection
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/28 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PBIC.py $
# $Revision: #9 $
# $DateTime: 2016/12/28 17:27:59 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PBIC.py#9 $
# Level: 34
#---------------------------------------------------------------------------------------------------------#

from Test_Switches import testSwitch
from Constants import *
import types, math, traceback, operator, struct
import ScrCmds
from TestParamExtractor import TP
from Temperature import CTemperature
from DesignPatterns import Singleton
import Utility
from Process import CProcess
import MessageHandler as objMsg
from Drive import objDut
import FSO
import os
import bisect
import lbacalc
import dbLogUtilities
from State import CState
import time
import SIM_FSO
import cPickle
from Utility import CUtility
from SIM_FSO import objSimArea


###########################################################################################################
###########################################################################################################

class CPBIC_data:

   """
   This dictionary is used for PBIC KPIV data collection
   
   """

   def __init__(self):
      self.dictType = 'All'  
      self.dut = objDut
      self.niblet = None
      self.kpivs = {}

      self.default = {'KPIV1':         9999,  
                      'KPIV2':         9999,  
                      'KPIV3':         9999,  
                      'KPIV4':         9999,  
                      'KPIV5':         9999,
                      'KPIV6':         9999,
                      'KPIV7':         9999, 
                      'KPIV8':         9999,
                      'KPIV9':         9999, 'KPIV10':        9999, 'KPIV11':        9999, 'KPIV12':            9999,
                      'KPIV13':        9999, 'KPIV14':        9999, 'KPIV15':        9999, 'KPIV16':            9999,
                      'KPIV17':        9999, 'KPIV18':        9999, 'KPIV19':        9999, 'KPIV20':            9999,
                      'KPIV21':        9999, 'KPIV22':        9999, 'KPIV23':        9999, 'KPIV24':            9999,
                      'KPIV13':        9999, 'KPIV25':        9999, 'KPIV26':        9999, 'KPIV27':            9999,
                      'KPIV28':        9999, 'KPIV29':        9999, 'KPIV30':        9999,                      }          
   #--------------------------------------------------------------------------------------------
   def getRecord(self, hd, zn):
      return self.kpivs.setdefault((hd,zn), self.default.copy())

   #--------------------------------------------------------------------------------------------
   def serialize(self):
      firstPass = True

      tableData = []  
      colHdrData = [] 

      for hd,zn in self.kpivs.keys():
         # Preset the leading items for this row of data.
         rowData = [hd, zn]
         # Grab the column header for this row of data.
         partialHdrData = self.kpivs[(hd,zn)].keys()

         if firstPass:
            # Set up the row of column header data.
            colHdrData = ['HD', 'ZN']
            colHdrData.extend(partialHdrData)

            # Capture a second copy of the column headers for reference.
            refHdrData = partialHdrData[:]
            sortedRefHdrData = partialHdrData[:]
            sortedRefHdrData.sort()
            firstPass = False

         # May have to reorder the row of data to match the order of other rows of
         # data, so the table is consistent and header labels match the underlying data.
         if partialHdrData != refHdrData and not testSwitch.skipVBARDictionaryCheck:
            # Make sure the same labels are present in both the reference and the row of data.
            partialHdrData.sort()
            if partialHdrData == sortedRefHdrData:
               # Build out the row of data in the proper order.
               for hdr in refHdrData:
                  rowData.extend([self.kpivs[(hd,zn)][hdr]])

            else:
               # Well this is unexpected, this row contains one or more different items,
               # or has items missing.
               objMsg.printMsg('Hd=%d, Zn=%d' % (hd,zn))
               objMsg.printMsg('Row Hdr Data %s' % partialHdrData)
               objMsg.printMsg('Ref Hdr Data %s' % sortedRefHdrData)
               ScrCmds.raiseException(11044, "Unexpected data in PBIC dictionary")

         else:
            # Wonderful, the data is already in the correct order, just copy it.
            rowData.extend(self.kpivs[(hd,zn)].values())

         # Add this new row entry to the end of the data table.
         tableData.append(rowData)

         #objMsg.printMsg('Data %d, %d : %s' % (hd,zn,rowData[2:]))

      serializedObjs = (tableData, colHdrData)
      return serializedObjs

   def unserialize(self, (tableData, colHdrData)):
      try:
         for rowData in tableData:
            (hd, zn) = rowData[:2]
            self.kpivs[(hd, zn)] = dict(zip(colHdrData[2:], rowData[2:]))
      except:
         objMsg.printMsg('PBIC SIM data not available')
         objMsg.printMsg(traceback.format_exc())                                                     

###########################################################################################################
###########################################################################################################
class CPBIC:

   """
   This Class saves KPIV data to drive and load the KPIV data from drive 
      
   """
   def __init__(self, params={}):
   
      self.dut = objDut
      self.oUtility = Utility.CUtility()
      self.spcIdHlpr = Utility.CSpcIdHelper(self.dut)

      if self.dut.nextState in ['PBIC_DATA_LD']:
         self.loadData()
      if self.dut.nextState in ['PBIC_DATA_SV','PBIC_DATA_SV_PRE2','PBIC_DATA_SV_CAL2']:
         self.saveData()
      
   def loadData(self):

      self.kpivAllZns = CPBIC_data()
     
      if self.dut.pbic_znkpivs:
         self.kpivAllZns.kpivs = self.dut.pbic_znkpivs
         self.dut.pbic_znkpivs = self.kpivAllZns.kpivs

      if self.dut.nextOper == 'PRE2':
         oper_list = [ ]
      if self.dut.nextOper == 'CAL2':
         oper_list = ['PRE2']
      if self.dut.nextOper == 'FNC2':
         oper_list = ['PRE2', 'CAL2']
      if self.dut.nextOper == 'CRT2':
         oper_list = ['PRE2', 'CAL2', 'FNC2']
      if self.dut.nextOper == 'FIN2':
         oper_list = ['PRE2', 'CAL2', 'FNC2', 'CRT2']

      for Operation in oper_list:

         FileName = "PBIC_DATA_" + Operation

         objMsg.printMsg("FileName------------- %s" % FileName )       

         data = SIM_FSO.CSimpleSIMFile(FileName).read()     #CCCYYY
         wpp, (tableData, colHdrData) = cPickle.loads(data)

         self.kpivAllZns.unserialize((tableData, colHdrData))
         
         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

         tablename = 'P_PBIC_KPIV_' + Operation  
         spcId = self.spcIdHlpr.getSpcId(tablename)

         for hd,zn in [(hd, zn) for hd in range(self.dut.imaxHead) for zn in range(self.dut.numZones)]:
            dblog_record = {
                     'SPC_ID'          : spcId,
                     'OCCURRENCE'      : occurrence,
                     'SEQ'             : curSeq,
                     'TEST_SEQ_EVENT'  : testSeqEvent,
                     'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[hd],
                     'DATA_ZONE'       : zn,
                     'HD_LGC_PSN'      : hd,
                     'KPIV1'           : round(self.kpivAllZns.getRecord(hd, zn)['KPIV1'], 4),
                     'KPIV2'           : round(self.kpivAllZns.getRecord(hd, zn)['KPIV2'], 4),
                     'KPIV3'           : round(self.kpivAllZns.getRecord(hd, zn)['KPIV3'], 4),
                     'KPIV4'           : round(self.kpivAllZns.getRecord(hd, zn)['KPIV4'], 4),
                     'KPIV5'           : round(self.kpivAllZns.getRecord(hd, zn)['KPIV5'], 4),
                     'KPIV6'           : round(self.kpivAllZns.getRecord(hd, zn)['KPIV6'], 4),
                     'KPIV7'           : round(self.kpivAllZns.getRecord(hd, zn)['KPIV7'], 4),
                     'KPIV8'           : round(self.kpivAllZns.getRecord(hd, zn)['KPIV8'], 4),
                     'KPIV9'           : round(self.kpivAllZns.getRecord(hd, zn)['KPIV9'], 4),
                     'KPIV10'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV10'], 4),
                     'KPIV11'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV11'], 4),
                     'KPIV12'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV12'], 4),
                     'KPIV13'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV13'], 4),
                     'KPIV14'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV14'], 4),
                     'KPIV15'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV15'], 4),
                     'KPIV16'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV16'], 4),
                     'KPIV17'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV17'], 4),
                     'KPIV18'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV18'], 4),
                     'KPIV19'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV19'], 4),
                     'KPIV20'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV20'], 4),
                     'KPIV21'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV21'], 4),
                     'KPIV22'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV22'], 4),
                     'KPIV23'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV23'], 4),
                     'KPIV24'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV24'], 4),
                     'KPIV25'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV25'], 4),
                     'KPIV26'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV26'], 4),
                     'KPIV27'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV27'], 4),
                     'KPIV28'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV28'], 4),
                     'KPIV29'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV29'], 4),
                     'KPIV30'          : round(self.kpivAllZns.getRecord(hd, zn)['KPIV30'], 4),
                  }
            self.dut.dblData.Tables(tablename).addRecord(dblog_record)
         objMsg.printDblogBin(self.dut.dblData.Tables(tablename), spcId)

   def saveData(self):
      self.kpivAllZns = CPBIC_data()

      self.dut.pbic_znkpivs = self.kpivAllZns.kpivs  

      if self.dut.nextOper == 'PRE2':      

         for hd,zn in [(hd, zn) for hd in range(self.dut.imaxHead) for zn in range(self.dut.numZones)]:

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV1'] = self.dut.MRR_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV MRR_BH missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV2'] = self.dut.CUR_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV CUR_BH missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV3'] = self.dut.FINALGAIN_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV FINALGAIN_BH missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV4'] = self.dut.BIASCUR_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV BIASCUR_BH missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV5'] = self.dut.MAXPKPK_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV MAXPKPK_BH missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV6'] = self.dut.EWAC_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV EWAC_BH missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV7'] = self.dut.WPEN_BH[hd]+self.dut.WPEP_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV WPE missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV8'] = self.dut.OW_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV OW_BH missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV9'] = self.dut.EBN_BH[hd]+self.dut.EBP_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV EB missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV10'] = self.dut.RCLR0_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV RCLR0_BH missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV11'] = self.dut.RCLR0_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('PRE2 KPIV RCLR0_BZ missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV12'] = self.dut.RCLR1_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV RCLR1_BH missing !!! ')
               pass               
               
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV13'] = self.dut.RCLR1_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('PRE2 KPIV RCLR1_BZ missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV14'] = self.dut.WCLR_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV WCLR_BH missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV15'] = self.dut.WCLR_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('PRE2 KPIV WCLR_BZ missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV16'] = self.dut.BNSH_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV BNSH_BH missing !!! ')
               pass     
          
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV17'] = self.dut.RAMP_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV RAMP_BH missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV18'] = self.dut.TRK0_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV TRK0_BH missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV19'] = self.dut.ECCEN_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV ECCEN_BH missing !!! ')
               pass

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV20'] = self.dut.BDFCONS_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV BDFCONS_BH missing !!! ')
               pass 
               
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV21'] = self.dut.MT10_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV MT10_BH missing !!! ')
               pass 

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV22'] = self.dut.MT50_BH[hd]
            except:
               objMsg.printMsg('PRE2 KPIV MT50_BH missing !!! ')
               pass 
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV23'] = self.dut.HDOFFSET_O[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('PRE2 KPIV HDOFFSET_O missing !!! ')
               pass 
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV24'] = self.dut.HDOFFSET_S[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('PRE2 KPIV HDOFFSET_S missing !!! ')
               pass 
    
      if self.dut.nextOper == 'CAL2':      

         for hd,zn in [(hd, zn) for hd in range(self.dut.imaxHead) for zn in range(self.dut.numZones)]:

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV1'] = self.dut.BPIM_BH[hd]
            except:
               objMsg.printMsg('CAL2 KPIV BPIM_BH missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV2'] = self.dut.BPIM_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('CAL2 KPIV BPIM_BZ missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV3'] = self.dut.TPIM_BH[hd]
            except:
               objMsg.printMsg('CAL2 KPIV TPIM_BH missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV4'] = self.dut.TPIM_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('CAL2 KPIV TPIM_BZ missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV5'] = self.dut.BPIC_BH[hd]
            except:
               objMsg.printMsg('CAL2 KPIV BPIC_BH missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV6'] = self.dut.BPIC_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('CAL2 KPIV BPIC_BZ missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV7'] = self.dut.TPIC_BH[hd]
            except:
               objMsg.printMsg('CAL2 KPIV TPIC_BH missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV8'] = self.dut.TPIC_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('CAL2 KPIV TPIC_BZ missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV9'] = self.dut.BPICQ_BH[hd]
            except:
               objMsg.printMsg('CAL2 KPIV BPICQ_BH missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV10'] = self.dut.TPICQ_BH[hd]
            except:
               objMsg.printMsg('CAL2 KPIV TPICQ_BH missing !!! ')
               pass                  

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV11'] = self.dut.HMSC_BH[hd]
            except:
               objMsg.printMsg('CAL2 KPIV HMSC_BH missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV12'] = self.dut.HMSC_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('CAL2 KPIV HMSC_BH_BZ missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV13'] = self.dut.HMSM_BH[hd]
            except:
               objMsg.printMsg('CAL2 KPIV HMSM_BH missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV14'] = self.dut.HMSM_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('CAL2 KPIV HMSM_BZ missing !!! ')
               pass
               
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV15'] = self.dut.OW1_BH[hd]
            except:
               objMsg.printMsg('CAL2 KPIV OW1_BH missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV16'] = self.dut.OWQ1_BH[hd]
            except:
               objMsg.printMsg('CAL2 KPIV OWQ1_BH missing !!! ')
               pass 
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV17'] = self.dut.MAXPKPK_BH[hd]
            except:
               objMsg.printMsg('CAL2 KPIV MAXPKPK_BH missing !!! ')
               pass
            
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV18'] = self.dut.NetCap
            except:
               objMsg.printMsg('CAL2 KPIV NetCap missing !!! ')
               pass             
  

      if self.dut.nextOper == 'FNC2':  
  
         for hd,zn in [(hd, zn) for hd in range(self.dut.imaxHead) for zn in range(self.dut.numZones)]:
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV1'] = self.dut.ER_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV ER_BH missing !!! ')
               pass  
                                  
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV2'] = self.dut.ER_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('FNC2 KPIV ER_BZ missing !!! ')
               pass 
                      

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV3'] = self.dut.ERQ_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV ERQ_BH missing !!! ')
               pass 
               
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV4'] = self.dut.RRO_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV RRO_BH missing !!! ')
               pass        

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV5'] = self.dut.NRRO_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV NRRO_BH missing !!! ')
               pass        

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV6'] = self.dut.ER2_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV ER2_BH missing !!! ')
               pass                     

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV7'] = self.dut.ER2_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('FNC2 KPIV ER2_BZ missing !!! ')
               pass        

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV8'] = self.dut.ER2Q_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV ER2Q_BH missing !!! ')
               pass
                       
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV9'] = self.dut.RAWRO_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV RAWRO_BH missing !!! ')
               pass  

            ############### Flawscan ###############################################

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV10'] = self.dut.REGFLAW_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV REGFLAW_BH missing !!! ')
               pass        

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV11'] = self.dut.VLAW_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV VLAW_BH missing !!! ')
               pass    

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV12'] = self.dut.TAFLAW_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV TAFLAW_BH missing !!! ')
               pass                     
            
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV13'] = self.dut.TOTALTA_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV TOTALTA_BH missing !!! ')
               pass        

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV14'] = self.dut.VERFW_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV VERFW_BH missing !!! ')
               pass        

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV15'] = self.dut.VERFW_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('FNC2 KPIV VERFW_BZ missing !!! ')
               pass        

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV16'] = self.dut.UNVERFW_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV UNVERFW_BH missing !!! ')
               pass       

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV17'] = self.dut.UNVERFW_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('FNC2 KPIV UNVERFW_BZ missing !!! ')
               pass
               
            ############### Flawscan End ##########################################  

            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV18'] = self.dut.SQZER_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV SQZER_BH missing !!! ')
               pass  
                                  
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV19'] = self.dut.SQZER_BZ[hd*self.dut.numZones+zn]
            except:
               objMsg.printMsg('FNC2 KPIV SQZER_BZ missing !!! ')
               pass 
               
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV20'] = self.dut.SQZERQ_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV SQZERQ_BH missing !!! ')
               pass               
            
            try:
               self.kpivAllZns.getRecord(hd, zn)['KPIV21'] = self.dut.SQZERMax_BH[hd]
            except:
               objMsg.printMsg('FNC2 KPIV SQZERMax_BH missing !!! ')
               pass
                   
 
      objs = ( self.dut.wrPwrPick, self.kpivAllZns.serialize() )
      data = cPickle.dumps(objs, 2)
     
      filename = "PBIC_DATA_" + self.dut.nextOper

      SIM_FSO.CSimpleSIMFile(filename).write(data)

   def run(self):
      return 


###########################################################################################################
class ClassPBIC(CProcess):

   def __init__(self):
      CProcess.__init__(self)
      self.dut = objDut

      self.mFSO = FSO.CFSO()
      self.spcID = 1
      
   #######################################################################################################################
   #
   #            Function:  PBIC_Controler
   #
   #            Description:  apply control rule to the KPIVs from previous operation
   #
   #######################################################################################################################

   def PBIC_Controler(self, operation ='',head =0, zone =0, KPIV_name=9999, LOWER_LIMIT =0, LOWER_LIMIT_ENABLE = 0, UPPER_LIMIT=0, UPPER_LIMIT_ENABLE =0):

      tablename = 'P_PBIC_KPIV_' + operation

      tableData = self.dut.dblData.Tables(tablename).tableDataObj()

      for row in tableData:
         if (int(row['HD_PHYS_PSN']) == self.dut.LgcToPhysHdMap[head]) and (int(row['DATA_ZONE']) == zone):
            KPIV = float(row[KPIV_name])

            objMsg.printMsg("Head:%d, KPIV NAME:  %s, = %f, LOWER_LIMIT = %f, UPPER_LIMIT = %f" % (head,KPIV_name, KPIV, LOWER_LIMIT, UPPER_LIMIT))

      Enable_Test = 1

      if LOWER_LIMIT_ENABLE == 1 and UPPER_LIMIT_ENABLE == 0:
         if KPIV > LOWER_LIMIT:
            Enable_Test = 1
         else:
            Enable_Test = 0

      if LOWER_LIMIT_ENABLE == 0 and UPPER_LIMIT_ENABLE == 1:
         if KPIV < UPPER_LIMIT:
            Enable_Test = 1
         else:
            Enable_Test = 0

      if LOWER_LIMIT_ENABLE == 1 and UPPER_LIMIT_ENABLE == 1:
         if KPIV < UPPER_LIMIT and KPIV > LOWER_LIMIT:
            Enable_Test = 1
         else:
            Enable_Test = 0

      return Enable_Test    

   #######################################################################################################################
   #
   #            Function:  test_data_FOM
   #
   #            Description:  function to get 2nd level KPIV (FOM) based on 2nd order curve fitting R_sqr
   #
   #######################################################################################################################

   def test_data_FOM(self,dataList):

      #######################################
      # DUT KPIVs
      #######################################
      #from PBIC import ClassPBIC
      #objPBIC = ClassPBIC()
      #FOM = objPBIC.test_data_FOM(test_data) 
      #######################################


      finalList = []
      finalList.extend(dataList)
      filterList = []
      filterList.extend(dataList)

      N=0
      s1=0
      s2=0
      s3=0
      s4=0
      t1=0
      t2=0
      t3=0

      for index in range(len(dataList)):
         N=N+1
         s1=s1+index
         s2=s2+index*index
         s3=s3+index*index*index
         s4=s4+index*index*index*index
         t1=t1+float(filterList[index])
         t2=t2+index*float(filterList[index])
         t3=t3+index*index*float(filterList[index])
      d=N*s2*s4 - N*s3*s3 - s1*s1*s4 - s2*s2*s2 + 2*s1*s2*s3
      A=(N*s2*t3 - N*s3*t2 - s1*s1*t3 - s2*s2*t1 + s1*s2*t2 + s1*s3*t1)/d
      B=(N*s4*t2 - N*s3*t3 - s2*s2*t2 - s1*s4*t1 + s1*s2*t3 + s2*s3*t1)/d
      C=(s1*s3*t3 -s1*s4*t2 -s2*s2*t3 - s3*s3*t1 + s2*s3*t2 + s2*s4*t1)/d
      #apply equation to all values
      for index in range(len(dataList)):
         finalList[index]=A*index*index+B*index+C

      R_sqr= 0
      SS_e = 0
      SS_t = 0 
      y_ave=0

      try:
         y_ave = sum(dataList)/float(len(dataList))
         
         for index in range(len(dataList)):
            SS_e= SS_e+ (finalList[index]-dataList[index])*(finalList[index]-dataList[index])

         for index in range(len(dataList)):
            SS_t= SS_t+ (dataList[index]-y_ave)*(dataList[index]-y_ave)         
      
         R_sqr = 1- SS_e/SS_t

      except:
         pass

      return finalList,R_sqr


   #######################################################################################################################
   #
   #            Function:  KPIV_collection
   #
   #            Description:  KPIV data collection from STATEs
   #
   #######################################################################################################################

   def KPIV_collection(self):
      if self.dut.currentState in ['VBAR_ADC_REPORT2']:
         try:
            ADCSummary = self.dut.dblData.Tables('P_VBAR_ADC_SUMMARY').tableDataObj()
         except:
            objMsg.printMsg('KPIV_collection - Table P_VBAR_ADC_SUMMARY is not found')
            ADCSummary = []
            
         for entry in ADCSummary:
            if int(entry['SPC_ID']) == 400 and entry['PARAMETER_NAME'] == 'Net':
               self.dut.NetCap = entry['DRV_CAPACITY']
         
         objMsg.printMsg("PBIC_KPIV: self.dut.NetCap = %s" % str(self.dut.NetCap))

      ###########################################################################

      if self.dut.currentState in ['SERIAL_FMT']:
         from MathLib import mean
         P_FORMAT_data = []
         try:
            P_FORMAT_data = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').tableDataObj()
         except:
            objMsg.printMsg('KPIV_collection - Table P_FORMAT_ZONE_ERROR_RATE is not found')

            if ConfigVars[CN].get('BenchTop', 0):
               P_FORMAT_data = P_FORMAT_ZONE_ERROR_RATE


         P250_ERROR_data = []
         try:
            # READ_SCRN2H
            P250_ERROR_data = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match', '16')
         except:
            objMsg.printMsg('KPIV_collection - Table P250_ERROR_RATE_BY_ZONE is not found')

            if ConfigVars[CN].get('BenchTop', 0):
               P250_ERROR_data = P250_ERROR_RATE_BY_ZONE


         if len(P_FORMAT_data) > 0 and len(P250_ERROR_data) > 0:
            OTF_list = []
            for entry in P_FORMAT_data:
               OTF_list.append(float(entry['OTF_ERROR_RATE']))

            RAW_list = []
            for entry in P250_ERROR_data:
               RAW_list.append(float(entry['RAW_ERROR_RATE']))

            objMsg.printMsg('Mean OTF_ERROR_RATE = %s' % mean(OTF_list))
            objMsg.printMsg('Mean RAW_ERROR_RATE = %s' % mean(RAW_list))

            #if mean(OTF_list) < 10.6 and mean(RAW_list) > -3.37:  # Loke debug
            if mean(OTF_list) < 10.6 and mean(RAW_list) > -2.37:
               objMsg.printMsg('Set FIN2_PBIC_CTRL=1')
               self.dut.driveattr['FIN2_PBIC_CTRL'] = "1"
         else:
            objMsg.printMsg('Invalid P_FORMAT_data=%s or P250_ERROR_data=%s' % (P_FORMAT_data, P250_ERROR_data))
   
      ###########################################################################

      if self.dut.currentState in ['HEAD_CAL']:

         try:
            try:
               tableData = self.dut.dblData.Tables('P186_BIAS_CAL2').tableDataObj()
            except:
               tableData = self.dut.dblData.Tables('P321_BIAS_CAL2').tableDataObj()

            for column_name in ['MRE_RESISTANCE','NEW_CURRENT']: 
               kpiv_data = {}                                                                                                    
               for row in tableData:
                  hd = int(row['HD_LGC_PSN'])
                  key = hd
                  try:
                     data = float(row[column_name])
                     kpiv_data.setdefault(key,[]).append(data)
                  except: pass
               for key in kpiv_data.keys():
                  if len(kpiv_data[key]) > 0:
                     avg_hd = sum(kpiv_data[key])/len(kpiv_data[key])
                  
                     if column_name in ['MRE_RESISTANCE']: 
                        self.dut.MRR_BH.append(avg_hd)
                     if column_name in ['NEW_CURRENT']: 
                        self.dut.CUR_BH.append(avg_hd)

            objMsg.printMsg("PBIC_KPIV: self.dut.MRR_BH %s" % str(self.dut.MRR_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.CUR_BH %s" % str(self.dut.CUR_BH))

            tableData = self.dut.dblData.Tables('P177_GAIN_DATA').tableDataObj()

            for column_name in ['FINAL_GAIN', 'BIAS_CURRENT']: 
               kpiv_data = {}                                                                                                    
               for row in tableData:
                  hd = int(row['HD_LGC_PSN'])
                  key = hd
                  try:
                     data = float(row[column_name])
                     kpiv_data.setdefault(key,[]).append(data)
                  except: pass
               for key in kpiv_data.keys():
                  if len(kpiv_data[key]) > 0:
                     avg_hd = sum(kpiv_data[key])/len(kpiv_data[key])
                  
                     if column_name in ['FINAL_GAIN']: 
                        self.dut.FINALGAIN_BH.append(int(avg_hd))
                     if column_name in ['BIAS_CURRENT']: 
                        self.dut.BIASCUR_BH.append(int(avg_hd))

            objMsg.printMsg("PBIC_KPIV: self.dut.FINALGAIN_BH %s" % str(self.dut.FINALGAIN_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.BIASCUR_BH %s" % str(self.dut.BIASCUR_BH))
         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass

      ###########################################################################
    

      if self.dut.currentState in ['MDW_CAL']:
         try:
            tableData = self.dut.dblData.Tables('P185_TRK_0_V3BAR_CALHD').tableDataObj()

            for column_name in ['RAMP_CYL','TRK_0_CYL']: 
               kpiv_data = {}            
               for row in tableData:                                                                   
                  hd = int(row['HD_LGC_PSN'])
                  key = hd
                  try:
                     data = float(row[column_name])
                     kpiv_data.setdefault(key,[]).append(data)
                  except: pass
               for key in kpiv_data.keys():
                  if len(kpiv_data[key]) > 0:
                     avg_hd = sum(kpiv_data[key])/len(kpiv_data[key])
                  
                     if column_name in ['RAMP_CYL']: 
                        self.dut.RAMP_BH.append(int(avg_hd))
                     if column_name in ['TRK_0_CYL']: 
                        self.dut.TRK0_BH.append(int(avg_hd))

            objMsg.printMsg("PBIC_KPIV: self.dut.RAMP_BH %s" % str(self.dut.RAMP_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.TRK0_BH %s" % str(self.dut.TRK0_BH))     

            tableData = self.dut.dblData.Tables('P047_ECCENTRICITY').tableDataObj()

            ECCEN_list = []
            for row in tableData:                                                                   
               ECCEN_list.append(  float(row['ECCENTRICITY'])    )

            for hd in range(0,self.dut.imaxHead):
               self.dut.ECCEN_BH.append(  ECCEN_list[int(hd/2)]    )

            objMsg.printMsg("PBIC_KPIV: self.dut.ECCEN_BH %s" % str(self.dut.ECCEN_BH))         
            
         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 

         try:
            from MathLib import Fit_2ndOrder
            org_test_trk = []
            org_trk_skew = []
            index_trk = [0,10000,20000,30000,40000,50000,60000,70000,80000,90000,100000,110000,120000,130000,140000,150000,160000,170000,180000,190000,200000,210000,220000,230000,240000,250000,260000,270000,280000,290000,300000,310000,320000,330000,340000,350000,360000,370000,380000,390000,400000,410000,420000,435000]
            index_trk_skew = [] 
            try:
                tableData = self.dut.dblData.Tables('P189_HD_SKEW_DETAILS2').tableDataObj()
            except:
                objMsg.printMsg("P189_HD_SKEW_DETAILS2 cannot be retrieved !" )
                pass
            for row in tableData:
               if (int(row['HD_LGC_PSN']) == 0) :
                  org_test_trk.append(  int(row['PHYS_TRK'])  )
                  org_trk_skew.append(  int(row['DC_SKEW'])  )
            objMsg.printMsg('org_test_trk %s' % org_test_trk)
            objMsg.printMsg('org_trk_skew %s' % org_trk_skew)                  
            ######### Curve Fit and Oupt the Index Track Data########################
            # for debug
            #org_test_trk = [9100,14403,19706,25009,30312,35615,40918,46221,51524,56827,62130,67433,72736,78039,83342,88645,93948,99251,104554,109857,115160,120463,125766,131069,136372,141675,146978,152281,157584,162887,168190,173493,178796,184099,189402,194705,200008,205311,210614,215917,221220,226523,231826,237129,242432,247735,253038,258341,263644,268947,274250,279553,284856,290159,295462,300765,306068,311371,316674,321977,327280,332583,337886,343189,348492,353795,359098,364401,369704,375007,380310,385613,390916,396219,401522,406825,412128,417431,422734,428037]
            #org_trk_skew = [-2042,-2081,-1988,-1961,-1866,-1845,-1817,-1762,-1704,-1627,-1551,-1529,-1476,-1446,-1380,-1316,-1312,-1205,-1199,-1124,-1036,-1005,-931,-873,-826,-746,-713,-655,-591,-524,-482,-395,-342,-267,-205,-147,-72,-19,24,87,159,242,320,386,444,526,592,662,747,833,944,1010,1084,1166,1212,1342,1423,1464,1593,1670,1761,1866,1982,2083,2192,2295,2396,2501,2603,2716,2850,2949,3079,3209,3322,3460,3603,3727,3874,4042]
            # Get 2nd order polynomial
            a, b, c = Fit_2ndOrder(org_test_trk, org_trk_skew)
            if a == -1 and b == -1 and c == -1:
               objMsg.printMsg('Unable to filter by 2nd order')
            else:
               for targettrk in index_trk:
                 fittedData = (a * targettrk * targettrk) + (b * targettrk) + c
                 index_trk_skew.append(fittedData)             
            objMsg.printMsg('index_trk %s' % index_trk)
            objMsg.printMsg('index_trk_skew %s' % index_trk_skew) 

            Cos_SkewAngle = [0.95881621,0.961435054,0.963989244,0.966477354,0.968897863,0.971249153,0.973529494,0.975737036,0.977869799,0.979925659,0.981902336,0.983797378,0.985608142,0.987331779,0.98896521,0.990505107,0.991947859,0.993289551,0.994525927,0.995652354,0.996663778,0.997554682,0.998319029,0.998950205,0.999440948,0.999783273,0.999968386,0.999986579,0.999827123,0.999478131,0.998926411,0.998157296,0.997154445,0.995899612,0.994372391,0.992549904,0.990406451,0.987913105,0.98503723,0.981741935,0.977985423,0.973720247,0.968892432,0.960458828]
            Sin_SkewAngle = [0.284027244,0.275032064,0.265941228,0.256751873,0.247460967,0.23806529,0.228561425,0.21894574,0.20921438,0.199363243,0.189387966,0.179283906,0.16904612,0.158669337,0.148147941,0.137475938,0.126646931,0.115654084,0.104490093,0.093147144,0.081616871,0.069890318,0.05795788,0.04580926,0.033433402,0.020818434,0.007951593,-0.005180843,-0.018593647,-0.032302724,-0.046325211,-0.060679584,-0.075385766,-0.090465254,-0.105941247,-0.121838782,-0.138184882,-0.1550087,-0.17234168,-0.190217699,-0.208673218,-0.227747403,-0.247482232,-0.278422053]
            Hd_ofs_p  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            b1_list   = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            b2_list   = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            a11_list  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            a12_list  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            a22_list  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            for index in range(len(index_trk)):
               Hd_ofs_p[index] = index_trk_skew[index]*Cos_SkewAngle[index]
               a11_list[index] = Cos_SkewAngle[index] *Cos_SkewAngle[index]
               a12_list[index] = Sin_SkewAngle[index] *Cos_SkewAngle[index]
               a22_list[index] = Sin_SkewAngle[index] *Sin_SkewAngle[index]
            objMsg.printMsg('Hd_ofs_p %s' % Hd_ofs_p)
            for index in range(len(index_trk)):
               b1_list[index] = Hd_ofs_p[index]*Cos_SkewAngle[index]
               b2_list[index] = Hd_ofs_p[index]*Sin_SkewAngle[index]
            objMsg.printMsg('b1_list %s' % b1_list)
            objMsg.printMsg('b2_list %s' % b2_list) 
            b1_sum = 0
            b2_sum = 0
            a11_sum = 0
            a12_sum = 0            
            a22_sum = 0 
            for b1 in b1_list:
               b1_sum = b1_sum + b1 
            b1_sum = b1_sum - b1_list[0] - b1_list[1] - b1_list[2] -- b1_list[43]    
            for b2 in b2_list:
               b2_sum = b2_sum + b2
            b2_sum = b2_sum - b2_list[0] - b2_list[1] - b2_list[2] -- b2_list[43] 
            for a11 in a11_list:
               a11_sum = a11_sum + a11
            a11_sum = a11_sum - a11_list[0] - a11_list[1] - a11_list[2] -- a11_list[43]             
            for a12 in a12_list:
               a12_sum = a12_sum + a12
            a12_sum = a12_sum - a12_list[0] - a12_list[1] - a12_list[2] -- a12_list[43]
            for a22 in a22_list:
               a22_sum = a22_sum + a22
            a22_sum = a22_sum - a22_list[0] - a22_list[1] - a22_list[2] -- a22_list[43] 
            OOO = (a22_sum*b1_sum - a12_sum*b2_sum)/(a11_sum*a22_sum - a12_sum*a12_sum)
            SSS = (a12_sum*b1_sum - a11_sum*b2_sum)/(a12_sum*a12_sum - a22_sum*a11_sum)
            OOO = OOO/520000*1000   #Rosewood 520k TPI
            SSS = SSS/520000*1000   #Rosewood 520k TPI
            self.dut.HDOFFSET_O.append(float('%.2f' %OOO))
            self.dut.HDOFFSET_S.append(float('%.2f' %SSS))
            objMsg.printMsg('b1_sum:%d' % b1_sum)
            objMsg.printMsg('b2_sum:%d' % b2_sum)
            objMsg.printMsg('a11_sum:%d' % a11_sum)
            objMsg.printMsg('a12_sum:%d' % a12_sum)
            objMsg.printMsg('a22_sum:%d' % a22_sum)
            objMsg.printMsg('SSS:%f' % SSS)
            objMsg.printMsg('OOO:%f' % OOO)
         except:
            objMsg.printMsg("Head offset PBIC_KPIV data not found !!!" )
            pass 
      ###########################################################################
             
      if self.dut.currentState in ['SERVO_OPTI']:
         try:
            if len(self.dut.BDFCONS_BH) == 0:
               tableData = self.dut.dblData.Tables('P136_BDRAG_FCONS').tableDataObj()
               for hd in range(0,self.dut.imaxHead):
                  for row in tableData:
                     if (int(row['SPC_ID']) == 12) :
                        self.dut.BDFCONS_BH.append(  int(row['BDRAG_FCONS'])  )

               objMsg.printMsg("PBIC_KPIV: self.dut.BDFCONS_BH %s" % str(self.dut.BDFCONS_BH))
         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass     

      ###########################################################################


      if self.dut.currentState in ['PES_SCRN']:
         try:
            tableData = self.dut.dblData.Tables('P033_PES_HD2').tableDataObj()

            for column_name in ['NRRO','RRO','RAW_RO']:
               T033_hd_data = {}            

               for row in tableData:
                  hd = int(row['HD_LGC_PSN'])
                  key = hd
                  try:
                     data = float(row[column_name])
                     T033_hd_data.setdefault(key,[]).append(data)
                  except: pass
               for key in T033_hd_data.keys():
                  if len(T033_hd_data[key]) > 0:
                     avg_hd = sum(T033_hd_data[key])/len(T033_hd_data[key])
                  
                     if column_name in ['NRRO']: 
                        self.dut.NRRO_BH.append(float('%.2f' %avg_hd))
                     if column_name in ['RRO']: 
                        self.dut.RRO_BH.append(float('%.2f' %avg_hd))
                     if column_name in ['RAW_RO']: 
                        self.dut.RAWRO_BH.append(float('%.2f' %avg_hd))

            objMsg.printMsg("PBIC_KPIV: self.dut.RRO_BH %s" % str(self.dut.RRO_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.NRRO_BH %s" % str(self.dut.NRRO_BH))
            objMsg.printMsg("PBIC_KPIV: self.dut.RAWRO_BH %s" % str(self.dut.RAWRO_BH))
         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass
      ###########################################################################

      if self.dut.currentState in ['AFH2']:
         try:
            if len(self.dut.RCLR0_BZ) == 0:
               tableData = self.dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()

               for column_name in ['WRT_CLR', 'RD_CLR']: 

                  #--------BY ZONE kpiv--------
            
                  for hd in range(0,self.dut.imaxHead):
                     for zn in range(self.dut.numZones):
                        for row in tableData:
                           if (int(row['SPC_ID']) == 20000) and (int(row['HD_LGC_PSN']) == hd) and (int(row['DATA_ZONE']) == zn) and (str(row['MSRD_INTRPLTD'])) =='I':

                              if (column_name in ['WRT_CLR']) and (float(row['WRT_CLR']) != 0): 
                                 self.dut.WCLR_BZ.append(float(str(row[column_name])))
                              if column_name in ['RD_CLR']:
                                 if float(row['WRT_CLR']) == 0:
                                    self.dut.RCLR0_BZ.append(float(str(row[column_name])))
                                 else:   
                                    self.dut.RCLR1_BZ.append(float(str(row[column_name])))

                  #--------BY HEAD kpiv--------
            
               for hd in range(0,self.dut.imaxHead):
                  kpiv_data1 = []
                  kpiv_data2 = []
                  kpiv_data3 = []
                  for zn in range(self.dut.numZones):
                     kpiv_data1.append( self.dut.WCLR_BZ[hd*self.dut.numZones +zn] )
                     kpiv_data2.append(self.dut.RCLR0_BZ[hd*self.dut.numZones +zn] )
                     kpiv_data3.append(self.dut.RCLR1_BZ[hd*self.dut.numZones +zn] )
                  self.dut.WCLR_BH.append(  sum(kpiv_data1)/len(kpiv_data1) )
                  self.dut.RCLR0_BH.append( sum(kpiv_data2)/len(kpiv_data2) )
                  self.dut.RCLR1_BH.append( sum(kpiv_data3)/len(kpiv_data3) )

               objMsg.printMsg("PBIC_KPIV: self.dut.RCLR0_BZ %s" % str(self.dut.RCLR0_BZ)) 
               objMsg.printMsg("PBIC_KPIV: self.dut.RCLR0_BH %s" % str(self.dut.RCLR0_BH)) 
               objMsg.printMsg("PBIC_KPIV: self.dut.RCLR1_BZ %s" % str(self.dut.RCLR1_BZ)) 
               objMsg.printMsg("PBIC_KPIV: self.dut.RCLR1_BH %s" % str(self.dut.RCLR1_BH))
               objMsg.printMsg("PBIC_KPIV: self.dut.WCLR_BZ %s" % str(self.dut.WCLR_BZ)) 
               objMsg.printMsg("PBIC_KPIV: self.dut.WCLR_BH %s" % str(self.dut.WCLR_BH)) 

            if len(self.dut.BNSH_BH) == 0:
               tableData = self.dut.dblData.Tables('P_AFH_DH_BURNISH_CHECK').tableDataObj()
               for column_name in ['DELTA_BURNISH_CHECK']: 

                  #--------BY HEAD kpiv--------
                
                  for hd in range(0,self.dut.imaxHead):
                     kpiv_data = []
                     for row in tableData:
                        if (int(row['HD_LGC_PSN']) == hd):
                           kpiv_data.append(float(row[column_name]))
                     avg_hd = sum(kpiv_data)/len(kpiv_data)
                     self.dut.BNSH_BH.append(avg_hd)
               objMsg.printMsg("PBIC_KPIV: self.dut.BNSH_BH %s" % str(self.dut.BNSH_BH)) 
         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 
      ###########################################################################


      if self.dut.currentState in ['READ_SCRN']:
         try:
            objMsg.printMsg("PBIC KPIV data collection === ")
            #try:
            #   objMsg.printDblogBin(self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE'))
            #except:
            #   objMsg.printMsg("P250_ERROR_RATE_BY_ZONE print failed. ")
            #   pass   

            tableData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
            column_name = 'RAW_ERROR_RATE'
            T250_zn_data = {}
            T250_hd_data = {}

            #--------BY ZONE kpiv--------
            
            for hd in range(0,self.dut.imaxHead):
               for zn in range(self.dut.numZones):
                  for row in tableData:
                     if (int(row['SPC_ID']) == 1) and(int(row['HD_LGC_PSN']) == hd) and (int(row['DATA_ZONE']) == zn):                     
                         self.dut.ER_BZ.append(float(row[column_name]))

            #--------BY HEAD kpiv--------

            for row in tableData:
               hd = int(row['HD_LGC_PSN'])
               zn = int(row['DATA_ZONE'])
               key = hd
               try:
                  data = float(row[column_name])
                  T250_hd_data.setdefault(key,[]).append(data)
               except: pass
            for key in T250_hd_data.keys():
               if len(T250_hd_data[key]) > 0:
                  avg_hd = sum(T250_hd_data[key])/len(T250_hd_data[key])
                  self.dut.ER_BH.append(float('%.2f' %avg_hd))

            #--------2nd level kpiv--------
            
            
            for hd in range(self.dut.imaxHead):
               kpiv_dataList = []
               for zn in range(self.dut.numZones):
                  kpiv_dataList.append(self.dut.ER_BZ[hd*self.dut.numZones + zn])               

               objMsg.printMsg("kpiv_dataList0 %s" % str(kpiv_dataList))
          
               kpiv_dataList,FOM = self.test_data_FOM(kpiv_dataList) 
               self.dut.ERQ_BH.append((float(FOM)))
               objMsg.printMsg("kpiv_dataList1 %s" % str(kpiv_dataList))
               objMsg.printMsg("kpiv_dataList1 FOM %f" % FOM)    

            objMsg.printMsg("PBIC_KPIV: self.dut.ER_BZ %s" % str(self.dut.ER_BZ)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.ER_BH %s" % str(self.dut.ER_BH)) 

         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 

      ###########################################################################



      if self.dut.currentState in ['READ_SCRN2']:
         try:
            objMsg.printMsg("PBIC KPIV data collection === ")

            tableData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
            column_name = 'RAW_ERROR_RATE'
            T250_zn_data = {}
            T250_hd_data = {}

            #--------BY ZONE kpiv--------
            
            for hd in range(0,self.dut.imaxHead):
               for zn in range(self.dut.numZones):
                  for row in tableData:
                     if (int(row['SPC_ID']) == 2) and (int(row['HD_LGC_PSN']) == hd) and (int(row['DATA_ZONE']) == zn):
                        self.dut.ER2_BZ.append(float(row[column_name]))

            #--------BY HEAD kpiv--------

            for row in tableData:
               hd = int(row['HD_LGC_PSN'])
               zn = int(row['DATA_ZONE'])
               key = hd
               try:
                  data = float(row[column_name])
                  T250_hd_data.setdefault(key,[]).append(data)
               except: pass
            for key in T250_hd_data.keys():
               if len(T250_hd_data[key]) > 0:
                  avg_hd = sum(T250_hd_data[key])/len(T250_hd_data[key])
                  self.dut.ER2_BH.append(float('%.2f' %avg_hd))

            #--------2nd level kpiv--------
            
            for hd in range(self.dut.imaxHead):
               kpiv_dataList = []
               for zn in range(self.dut.numZones):
                  kpiv_dataList.append(self.dut.ER2_BZ[hd*self.dut.numZones + zn])               

               objMsg.printMsg("kpiv_dataList0 %s" % str(kpiv_dataList))
          
               kpiv_dataList,FOM = self.test_data_FOM(kpiv_dataList) 
               self.dut.ER2Q_BH.append((float(FOM)))
               objMsg.printMsg("kpiv_dataList1 %s" % str(kpiv_dataList))
               objMsg.printMsg("kpiv_dataList1 FOM %f" % FOM)    

            objMsg.printMsg("PBIC_KPIV: self.dut.ER2_BZ %s" % str(self.dut.ER2_BZ)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.ER2_BH %s" % str(self.dut.ER2_BH)) 

         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 



      if self.dut.currentState in ['SQZ_WRITE']:
         try:
            objMsg.printMsg("PBIC KPIV data collection === ")

            tableData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
            column_name = 'RAW_ERROR_RATE'
            T250_zn_data = {}
            T250_hd_data = {}

            #--------BY ZONE kpiv--------
            
            for hd in range(0,self.dut.imaxHead):
               for zn in range(self.dut.numZones):
                  for row in tableData:
                     if (int(row['SPC_ID']) == 3) and (int(row['HD_LGC_PSN']) == hd) and (int(row['DATA_ZONE']) == zn):
                        self.dut.SQZER_BZ.append(float(row[column_name]))

            #--------BY HEAD kpiv--------

            for row in tableData:
               hd = int(row['HD_LGC_PSN'])
               zn = int(row['DATA_ZONE'])
               key = hd
               try:
                  data = float(row[column_name])
                  T250_hd_data.setdefault(key,[]).append(data)
               except: pass
            for key in T250_hd_data.keys():
               if len(T250_hd_data[key]) > 0:
                  avg_hd = sum(T250_hd_data[key])/len(T250_hd_data[key])
                  self.dut.SQZER_BH.append(float('%.2f' %avg_hd))
                  self.dut.SQZERMax_BH.append(max(T250_hd_data[key]))

            #--------2nd level kpiv--------
            
            for hd in range(self.dut.imaxHead):
               kpiv_dataList = []
               for zn in range(self.dut.numZones):
                  kpiv_dataList.append(self.dut.SQZER_BZ[hd*self.dut.numZones + zn])               

               objMsg.printMsg("kpiv_dataList0 %s" % str(kpiv_dataList))
          
               kpiv_dataList,FOM = self.test_data_FOM(kpiv_dataList) 
               self.dut.SQZERQ_BH.append((float(FOM)))
               objMsg.printMsg("kpiv_dataList1 %s" % str(kpiv_dataList))
               objMsg.printMsg("kpiv_dataList1 FOM %f" % FOM)    

            objMsg.printMsg("PBIC_KPIV: self.dut.SQZER_BZ %s" % str(self.dut.SQZER_BZ)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.SQZER_BH %s" % str(self.dut.SQZER_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.SQZERMax_BH %s" % str(self.dut.SQZERMax_BH))             

         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 
            
      if self.dut.currentState in ['SQZ_WRITE2']:
         try:
            objMsg.printMsg("PBIC KPIV data collection === ")

            tableData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SEQ', 'match', self.dut.seqNum-1)
            T250_hd_data = {}

            #--------BY HEAD kpiv--------

            for row in tableData:
               hd = int(row['HD_LGC_PSN'])
               try:
                  data = float(row['RAW_ERROR_RATE'])
                  T250_hd_data.setdefault(hd,[]).append(data)
               except: pass
            for key in T250_hd_data.keys():
               if len(T250_hd_data[key]) > 0:
                  avg_hd = sum(T250_hd_data[key])/len(T250_hd_data[key])
                  self.dut.SQZER_BH.append(float('%.2f' %avg_hd))
                  self.dut.SQZERMax_BH.append(max(T250_hd_data[key]))

            objMsg.printMsg("PBIC_KPIV: self.dut.SQZER_BH %s" % str(self.dut.SQZER_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.SQZERMax_BH %s" % str(self.dut.SQZERMax_BH))             

         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass

      ###########################################################################


      if self.dut.currentState in ['D_FLAWSCAN','SPF']:
       
         try: 
            
            if len(self.dut.VLAW_BH) == 0:


               tableData = self.dut.dblData.Tables('P107_VERIFIED_FLAWS').tableDataObj()

               for column_name in ['VRFD_FLAWS', 'REG_FLAWS', 'TA_FLAWS']: 

                  #--------BY ZONE kpiv--------
                  for hd in range(0,self.dut.imaxHead):           
                     for row in tableData:
                        if int(row['HD_LGC_PSN']) == hd:
                           self.dut.REGFLAW_BH.append(int(row['REG_FLAWS']) )
                           self.dut.VLAW_BH.append(int(row['VRFD_FLAWS']) )
                           self.dut.TAFLAW_BH.append(int(row['TA_FLAWS']) )


               objMsg.printMsg("PBIC_KPIV: self.dut.REGFLAW_BH %s" % str(self.dut.REGFLAW_BH)) 
               objMsg.printMsg("PBIC_KPIV: self.dut.VLAW_BH %s" % str(self.dut.VLAW_BH)) 
               objMsg.printMsg("PBIC_KPIV: self.dut.TAFLAW_BH %s" % str(self.dut.TAFLAW_BH)) 


            if len(self.dut.TOTALTA_BH) == 0:

               tableData = self.dut.dblData.Tables('P134_TA_SUM_HD2').tableDataObj()

               #--------BY HEAD kpiv--------

               for hd in range(0,self.dut.imaxHead):
                  kpiv_data = []
                  for column_name in ['AMP0_CNT', 'AMP1_CNT', 'AMP2_CNT', 'AMP3_CNT', 'AMP4_CNT', 'AMP5_CNT', 'AMP6_CNT', 'AMP7_CNT']: 
                     for row in tableData:
                        if (int(row['HD_LGC_PSN']) == hd):
                           kpiv_data.append(float(row[column_name]))


                  self.dut.TOTALTA_BH.append( sum(kpiv_data) )

               objMsg.printMsg("PBIC_KPIV: self.dut.TOTALTA_BH %s" % str(self.dut.TOTALTA_BH)) 

            if len(self.dut.TOTALTA_BH) == 0:

               tableData = self.dut.dblData.Tables('P140_FLAW_COUNT').tableDataObj()


            if len(self.dut.VERFW_BZ) == 0:

               tableData = self.dut.dblData.Tables('P140_FLAW_COUNT').tableDataObj()
            

               for column_name in ['VERIFIED_FLAW_COUNT', 'UNVERIFIED_FLAW_COUNT']: 

                  #--------BY ZONE kpiv--------
            
                  for hd in range(0,self.dut.imaxHead):
                     for zn in range(self.dut.numZones):
                        for row in tableData:
                           if int(row['HD_LGC_PSN']) == hd and int(row['DATA_ZONE']) == zn :
                              if column_name in ['VERIFIED_FLAW_COUNT']: 
                                 self.dut.VERFW_BZ.append(float(str(row[column_name])))
                              if column_name in ['UNVERIFIED_FLAW_COUNT']: 
                                 self.dut.UNVERFW_BZ.append(float(str(row[column_name])))

                  #--------BY HEAD kpiv--------
            
               for hd in range(0,self.dut.imaxHead):
                  kpiv_data1 = []
                  kpiv_data2 = []
                  for zn in range(self.dut.numZones):
                     kpiv_data1.append( self.dut.VERFW_BZ[hd*self.dut.numZones +zn] )
                     kpiv_data2.append(self.dut.UNVERFW_BZ[hd*self.dut.numZones +zn] )

                  self.dut.VERFW_BH.append(  sum(kpiv_data1)/len(kpiv_data1) )
                  self.dut.UNVERFW_BH.append( sum(kpiv_data2)/len(kpiv_data2) )

               objMsg.printMsg("PBIC_KPIV: self.dut.VERFW_BH %s" % str(self.dut.VERFW_BH)) 
               objMsg.printMsg("PBIC_KPIV: self.dut.VERFW_BZ %s" % str(self.dut.VERFW_BZ)) 
               objMsg.printMsg("PBIC_KPIV: self.dut.UNVERFW_BH %s" % str(self.dut.UNVERFW_BH)) 
               objMsg.printMsg("PBIC_KPIV: self.dut.UNVERFW_BZ %s" % str(self.dut.UNVERFW_BZ))
         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 
      
      ###########################################################################

      if self.dut.currentState in ['HMSC_DATA']:
         try:

            tableData = self.dut.dblData.Tables('P_VBAR_HMS_ADJUST').tableDataObj()

            for column_name in ['HMS_CAP', 'HMS_MRGN']: 


               #--------BY ZONE kpiv--------
            
               for hd in range(0,self.dut.imaxHead):
                  for zn in range(self.dut.numZones):
                     for row in tableData:
                        if (int(row['HD_LGC_PSN']) == hd) and (int(row['DATA_ZONE']) == zn):
                           if column_name in ['HMS_CAP']: 
                              self.dut.HMSC_BZ.append(float(row[column_name]))
                           if column_name in ['HMS_MRGN']: 
                              self.dut.HMSM_BZ.append(float(row[column_name]))

               #--------BY HEAD kpiv--------
            
               for hd in range(0,self.dut.imaxHead):
                  vbar_hd_data = []
                  for row in tableData:
                     if (int(row['HD_LGC_PSN']) == hd):
                        vbar_hd_data.append(float(row[column_name]))
                  avg_hd = sum(vbar_hd_data)/len(vbar_hd_data)
                        
                  if column_name in ['HMS_CAP']: 
                     self.dut.HMSC_BH.append(avg_hd)
                  if column_name in ['HMS_MRGN']: 
                     self.dut.HMSM_BH.append(avg_hd)

            objMsg.printMsg("PBIC_KPIV: self.dut.HMSC_BZ %s" % str(self.dut.HMSC_BZ)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.HMSC_BH %s" % str(self.dut.HMSC_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.HMSM_BZ %s" % str(self.dut.HMSM_BZ)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.HMSM_BH %s" % str(self.dut.HMSM_BH))
         
         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass  
         
      
      ###########################################################################

      if self.dut.currentState in ['VBAR_ZN','VBAR_FMT_PICKER']:
         try:    
            tableData = self.dut.dblData.Tables('P_VBAR_FORMAT_SUMMARY').tableDataObj()
            for column_name in ['BPI_CAP','TPI_CAP','BPI_MRGN','TPI_MRGN']: 

               #--------BY ZONE kpiv--------
            
               for hd in range(0,self.dut.imaxHead):
                  for zn in range(self.dut.numZones):
                     for row in tableData:
                        if (int(row['HD_LGC_PSN']) == hd) and (int(row['DATA_ZONE']) == zn):
                           if column_name in ['BPI_CAP']: 
                              self.dut.BPIC_BZ.append(float(row[column_name]))
                           if column_name in ['TPI_CAP']: 
                              self.dut.TPIC_BZ.append(float(row[column_name]))
                           if column_name in ['BPI_MRGN']: 
                              self.dut.BPIM_BZ.append(float(row[column_name]))
                           if column_name in ['TPI_MRGN']: 
                              self.dut.TPIM_BZ.append(float(row[column_name]))

               #--------BY HEAD kpiv--------
            
               for hd in range(0,self.dut.imaxHead):
                  vbar_hd_data = []
                  for row in tableData:
                     if (int(row['HD_LGC_PSN']) == hd):
                        vbar_hd_data.append(float(row[column_name]))
                  avg_hd = sum(vbar_hd_data)/len(vbar_hd_data)
                        
                  if column_name in ['BPI_CAP']: 
                     self.dut.BPIC_BH.append(avg_hd)
                  if column_name in ['TPI_CAP']: 
                     self.dut.TPIC_BH.append(avg_hd)
                  if column_name in ['BPI_MRGN']: 
                     self.dut.BPIM_BH.append(avg_hd)
                  if column_name in ['TPI_MRGN']: 
                     self.dut.TPIM_BH.append(avg_hd) 

            objMsg.printMsg("PBIC_KPIV: self.dut.BPIC_BZ %s" % str(self.dut.BPIC_BZ)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.BPIC_BH %s" % str(self.dut.BPIC_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.TPIC_BZ %s" % str(self.dut.TPIC_BZ)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.TPIC_BH %s" % str(self.dut.TPIC_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.BPIM_BZ %s" % str(self.dut.BPIM_BZ)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.BPIM_BH %s" % str(self.dut.BPIM_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.TPIM_BZ %s" % str(self.dut.TPIM_BZ)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.TPIM_BH %s" % str(self.dut.TPIM_BH)) 
         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 

      ###########################################################################

      if self.dut.currentState in ['LIN_SCREEN1','LIN_SCREEN2']:
       
         if len(self.dut.MAXPKPK_BH) == 0:

            try:
               try:
                  tableData = self.dut.dblData.Tables('P150_GAIN_SUM').tableDataObj()
               except:
                  tableData = self.dut.dblData.Tables('P150_GAIN_SUM2').tableDataObj()
            
               for hd in range(0,self.dut.imaxHead):
                  for row in tableData:
                     if int(row['HD_LGC_PSN']) == hd: 
                        self.dut.MAXPKPK_BH.append(float(row['MAX_PK_PK']))

               objMsg.printMsg("PBIC_KPIV: self.dut.MAXPKPK_BH %s" % str(self.dut.MAXPKPK_BH))
            except:
               objMsg.printMsg("PBIC_KPIV data not found !!!" )
               pass  


      ###########################################################################
            
  
      if self.dut.currentState in ['WEAK_WR_OW2']:

         kpiv_data = []
         try:
            tableData = self.dut.dblData.Tables('P337_OVERWRITE').tableDataObj()
            for column_name in ['OVERWRITE']: 

               #--------BY HEAD kpiv--------
             
               for hd in range(0,self.dut.imaxHead):
                  kpiv_data = []
                  for row in tableData:
                     if (int(row['HD_LGC_PSN']) == hd):
                        kpiv_data.append(float(row[column_name]))
                  avg_hd = sum(kpiv_data)/len(kpiv_data)


                  self.dut.OW_BH.append(avg_hd)



            objMsg.printMsg("PBIC_KPIV: self.dut.OW_BH %s" % str(self.dut.OW_BH)) 
         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 

      ###########################################################################
  
      if self.dut.currentState in ['WEAK_WR_OW1']:

         kpiv_data = []
         try:
            tableData = self.dut.dblData.Tables('P337_OVERWRITE').tableDataObj()
            for column_name in ['OVERWRITE']: 

               #--------BY HEAD kpiv--------
             
               for hd in range(0,self.dut.imaxHead):
                  kpiv_data = []
                  for row in tableData:
                     if (int(row['HD_LGC_PSN']) == hd):
                        kpiv_data.append(float(row[column_name]))
                  avg_hd = sum(kpiv_data)/len(kpiv_data)
                  self.dut.OW1_BH.append(avg_hd)

            objMsg.printMsg("PBIC_KPIV: self.dut.OW1_BH %s" % str(self.dut.OW1_BH)) 
         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 
            
      ###########################################################################


      if self.dut.currentState in ['EWAC_TEST']:

         kpiv_data = []
         try:
                    
            tableData = self.dut.dblData.Tables('P069_EWAC_SUMMARY').tableDataObj()
            for column_name in ['EWAC_UIN']: 

               #--------BY HEAD kpiv--------
             
               for hd in range(0,self.dut.imaxHead):
                  kpiv_data = []
                  for row in tableData:
                     if (int(row['HD_LGC_PSN']) == hd):
                        kpiv_data.append(float(row[column_name]))
                  avg_hd = sum(kpiv_data)/len(kpiv_data)
                  self.dut.EWAC_BH.append(avg_hd)


            objMsg.printMsg("PBIC_KPIV: self.dut.EWAC_BH %s" % str(self.dut.EWAC_BH))

         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 

            
      
      ###########################################################################

      if self.dut.currentState in ['WPE_TEST']:
    
         kpiv_data = [] 
                
         try:
            tableData = self.dut.dblData.Tables('P069_WPE_SUMMARY').tableDataObj()

            for column_name in ['WPE_NEG','WPE_POS']: 

               #--------BY HEAD kpiv--------
             
               for hd in range(0,self.dut.imaxHead):
                  kpiv_data = []
                  for row in tableData:
                     if (int(row['HD_LGC_PSN']) == hd):
                        kpiv_data.append(float(row[column_name]))
                  avg_hd = sum(kpiv_data)/len(kpiv_data)
                  
                  if column_name in ['WPE_NEG']: 
                     self.dut.WPEN_BH.append(avg_hd)
                  if column_name in ['WPE_POS']: 
                     self.dut.WPEP_BH.append(avg_hd)

            objMsg.printMsg("PBIC_KPIV: self.dut.WPEN_BH %s" % str(self.dut.WPEN_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.WPEP_BH %s" % str(self.dut.WPEP_BH))         

         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 

         ###########################################################################

      if self.dut.currentState in ['MT50_10_MEASURE']:
    
         kpiv_data = [] 
                
         try:
            tableData = self.dut.dblData.Tables('P269_MT50_RESULT_DATA').tableDataObj()

            for column_name in ['MT50_WIDTH', 'MT10_WIDTH']: 

               #--------BY HEAD kpiv--------
             
               for hd in range(0,self.dut.imaxHead):
                  kpiv_data = []
                  for row in tableData:
                     if (int(row['HD_LGC_PSN']) == hd):
                        kpiv_data.append(float(row[column_name]))
                  avg_hd = sum(kpiv_data)/len(kpiv_data)
                  
                  if column_name in ['MT50_WIDTH']: 
                     self.dut.MT50_BH.append(avg_hd)
                  if column_name in ['MT10_WIDTH']: 
                     self.dut.MT10_BH.append(avg_hd)

            objMsg.printMsg("PBIC_KPIV: self.dut.MT50_BH %s" % str(self.dut.MT50_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.MT10_BH %s" % str(self.dut.MT10_BH))         

         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 

         ###########################################################################

      if self.dut.currentState in ['ERASE_BAND']:
    
         kpiv_data = [] 
                
         try:
            tableData = self.dut.dblData.Tables('P270_EB_RESULT_DATA').tableDataObj()

            for column_name in ['EB_NEG_WIDTH', 'EB_POS_WIDTH']: 

               #--------BY HEAD kpiv--------
             
               for hd in range(0,self.dut.imaxHead):
                  kpiv_data = []
                  for row in tableData:
                     if (int(row['HD_LGC_PSN']) == hd):
                        kpiv_data.append(float(row[column_name]))
                  avg_hd = sum(kpiv_data)/len(kpiv_data)
                  
                  if column_name in ['EB_NEG_WIDTH']: 
                     self.dut.EBN_BH.append(avg_hd)
                  if column_name in ['EB_POS_WIDTH']: 
                     self.dut.EBP_BH.append(avg_hd)

            objMsg.printMsg("PBIC_KPIV: self.dut.EBN_BH %s" % str(self.dut.EBN_BH)) 
            objMsg.printMsg("PBIC_KPIV: self.dut.EBP_BH %s" % str(self.dut.EBP_BH))         

         except:
            objMsg.printMsg("PBIC_KPIV data not found !!!" )
            pass 

   #######################################################################################################################
   #
   #            Function:  PBIC_Control_bh
   #
   #            Description:  by head PBIC controller for PBCI states.
   #
   #######################################################################################################################

   def PBIC_Control_bh(self):

      pbic_head_list = []
      zone = 0

      ###########################################################################

      if self.dut.nextState in ['INTRA_BAND_SCRN','INTER_BAND_SCRN_500','INTER_BAND_SCRN','WRITE_SCRN','WRITE_SCRN_10K','SMR_WRITE_SCRN']:
         try:
            for head in xrange(self.dut.imaxHead):
               objMsg.printMsg("Head:%d, KPIV NAME:  %s, = %f, LOWER_LIMIT = %f, UPPER_LIMIT = %f" % (head,'KPIV18', self.dut.SQZER_BH[head], 0, TP.ATI_ER_AVG_BH_lim))
               objMsg.printMsg("Head:%d, KPIV NAME:  %s, = %f, LOWER_LIMIT = %f, UPPER_LIMIT = %f" % (head,'KPIV21', self.dut.SQZERMax_BH[head], 0, TP.ATI_ER_MAX_BH_lim))
                  
               if self.PBIC_Controler( 'CAL2',  head, zone, 'KPIV1', TP.ATI_BPIM_BH_lim, 1) or self.PBIC_Controler('CAL2',head, zone, 'KPIV3', TP.ATI_TPIM_BH_lim, 1):
                  if self.dut.SQZER_BH[head] < TP.ATI_ER_AVG_BH_lim:
                     if self.dut.SQZERMax_BH[head] < TP.ATI_ER_MAX_BH_lim:
                        objMsg.printMsg("PBIC bypass test for head %d"% head )                     
                        continue
               pbic_head_list.append(head)

            ############################
            # update PBIC status attri 
            ############################
            x = 0
            #if len(pbic_head_list) != self.dut.imaxHead:
            for head in pbic_head_list:
               x = 2**int(head) + x
               #objMsg.printMsg("PBIC status %d  "% (x) )
               #a = str(x)
            self.dut.driveattr['PBIC_STATUS'] = '%X%s'%(x, self.dut.driveattr['PBIC_STATUS'][1:])
            #objMsg.printMsg("self.dut.driveattr['PBIC_STATUS']xxxxxaaaxxxxx %s" % str(self.dut.driveattr['PBIC_STATUS']))
               
         except:
            pbic_head_list = range(self.dut.imaxHead)
            objMsg.printMsg("PBIC controller exception ! ------------------------------------------")

         if testSwitch.PBIC_DATA_COLLECTION_MODE and \
            ((self.dut.BG in ['SBS'] and len(ConfigVars[CN].get('PBICSwitches', '00000')) >= 1 and int(ConfigVars[CN].get('PBICSwitches', '00000')[0]) == 1) or \
            (self.dut.BG not in ['SBS'] and len(ConfigVars[CN].get('PBICSwitchesOEM', '00000')) >= 1 and int(ConfigVars[CN].get('PBICSwitchesOEM', '00000')[0]) == 1)):
            pbic_head_list = range(self.dut.imaxHead)
            objMsg.printMsg("PBIC data collection mode------------------------------------------")
      elif self.dut.nextOper in ['CRT2'] and self.dut.nextState in ['INTRA_BAND_SCRN2','INTER_BAND_SCRN2','SMR_WRITE_SCRN2','WRITE_SCRN2']:
         try:
            for head in xrange(self.dut.imaxHead):
               objMsg.printMsg("Head:%d, KPIV NAME:  %s, = %f, LOWER_LIMIT = %f, UPPER_LIMIT = %f" % (head,'SQZER_BH', self.dut.SQZER_BH[head], 0, TP.ATI_ER_AVG_BH_lim))
               objMsg.printMsg("Head:%d, KPIV NAME:  %s, = %f, LOWER_LIMIT = %f, UPPER_LIMIT = %f" % (head,'SQZERMax_BH', self.dut.SQZERMax_BH[head], 0, TP.ATI_ER_MAX_BH_lim))
            
               if self.PBIC_Controler( 'CAL2',  head, zone, 'KPIV1', TP.ATI_BPIM_BH_lim, 1) and self.PBIC_Controler('CAL2',head, zone, 'KPIV3', TP.ATI_TPIM_BH_lim, 1) and \
                  self.dut.SQZER_BH[head] < TP.ATI_ER_AVG_BH_lim and self.dut.SQZERMax_BH[head] < TP.ATI_ER_MAX_BH_lim:
                  objMsg.printMsg("PBIC bypass test for head %d"% head )                     
                  continue
               pbic_head_list.append(head)

            ############################
            # update PBIC status attri 
            ############################
            x = 0
            #if len(pbic_head_list) != self.dut.imaxHead:
            for head in pbic_head_list:
               x = 2**int(head) + x
               #objMsg.printMsg("PBIC status %d  "% (x) )
               #a = str(x)
            self.dut.driveattr['PBIC_STATUS'] = self.dut.driveattr['PBIC_STATUS'][:1] + '%d'%x + self.dut.driveattr['PBIC_STATUS'][2:]                                                
            #objMsg.printMsg("self.dut.driveattr['PBIC_STATUS']xxxxxaaaxxxxx %s" % str(self.dut.driveattr['PBIC_STATUS']))
               
         except:
            pbic_head_list = range(self.dut.imaxHead)
            objMsg.printMsg("PBIC controller exception ! ------------------------------------------")

         if testSwitch.PBIC_DATA_COLLECTION_MODE and \
            ((self.dut.BG in ['SBS'] and len(ConfigVars[CN].get('PBICSwitches', '00000')) >= 2 and int(ConfigVars[CN].get('PBICSwitches', '00000')[1]) == 1) or \
            (self.dut.BG not in ['SBS'] and len(ConfigVars[CN].get('PBICSwitchesOEM', '00000')) >= 2 and int(ConfigVars[CN].get('PBICSwitchesOEM', '00000')[1]) == 1)):
            pbic_head_list = range(self.dut.imaxHead)
            objMsg.printMsg("PBIC data collection mode------------------------------------------")
      else:
         pbic_head_list = range(self.dut.imaxHead)

      return pbic_head_list

######################################################################################
#########################    BY DRIVE CONTROLLER          #############################
######################################################################################

   def PBIC_Control_bd(self):
      pbic_test_on = 1

      if self.dut.nextState in ['ADV_SWEEP']:
         if self.PBIC_Controler( 'CAL2',  0, 0, 'KPIV18', 0, 0 , TP.VbarCapacityGBPerHead * self.dut.imaxHead, 1):
            objMsg.printMsg("PBIC KPIV NAME:  %s, < %f" % ('Net Capacity', TP.VbarCapacityGBPerHead * self.dut.imaxHead))
            pbic_test_on = 1
         else:
            objMsg.printMsg("PBIC bypass test KPIV NAME:  %s, >= %f" % ('Net Capacity', TP.VbarCapacityGBPerHead * self.dut.imaxHead))
            pbic_test_on = 0
            
         self.dut.driveattr['PBIC_STATUS'] = self.dut.driveattr['PBIC_STATUS'][:2] + '%d'%pbic_test_on + self.dut.driveattr['PBIC_STATUS'][3:]
         if testSwitch.PBIC_DATA_COLLECTION_MODE and \
            ((self.dut.BG in ['SBS'] and len(ConfigVars[CN].get('PBICSwitches', '00000')) >= 3 and int(ConfigVars[CN].get('PBICSwitches', '00000')[2]) == 1) or \
             (self.dut.BG not in ['SBS'] and len(ConfigVars[CN].get('PBICSwitchesOEM', '00000')) >= 3 and int(ConfigVars[CN].get('PBICSwitchesOEM', '00000')[2]) == 1)):
           objMsg.printMsg("PBIC data collection mode------------------------------------------")
           pbic_test_on = 1
         
      ###########################################################################

      if self.dut.nextState in ['SP_WR_TRUPUT', 'SP_RD_TRUPUT', 'SP_WR_TRUPUT2', 'SP_RD_TRUPUT2']:     # Loke
         objMsg.printMsg("PBIC PBIC_Control_bd FIN2 throughput FIN2_PBIC_CTRL=%s" % self.dut.driveattr['FIN2_PBIC_CTRL'])

         if self.dut.driveattr['FIN2_PBIC_CTRL'] == "1":
            if testSwitch.PBIC_DATA_COLLECTION_MODE and \
               ((self.dut.BG in ['SBS'] and len(ConfigVars[CN].get('PBICSwitches', '00000')) >= 4 and int(ConfigVars[CN].get('PBICSwitches', '00000')[3]) == 1) or \
                (self.dut.BG not in ['SBS'] and len(ConfigVars[CN].get('PBICSwitchesOEM', '00000')) >= 4 and int(ConfigVars[CN].get('PBICSwitchesOEM', '00000')[3]) == 1)):
               PbicRes = '3'
            else:
               pbic_test_on = 0
               PbicRes = '1'
         else:
            if testSwitch.PBIC_DATA_COLLECTION_MODE and \
               ((self.dut.BG in ['SBS'] and len(ConfigVars[CN].get('PBICSwitches', '00000')) >= 4 and int(ConfigVars[CN].get('PBICSwitches', '00000')[3]) == 1) or \
                (self.dut.BG not in ['SBS'] and len(ConfigVars[CN].get('PBICSwitchesOEM', '00000')) >= 4 and int(ConfigVars[CN].get('PBICSwitchesOEM', '00000')[3]) == 1)):
               PbicRes = '0'
            else:
               PbicRes = '2'

         objMsg.printMsg("Before PBIC_STATUS=%s" % self.dut.driveattr['PBIC_STATUS'])
         self.dut.driveattr['PBIC_STATUS'] = self.dut.driveattr['PBIC_STATUS'][:3] + PbicRes + self.dut.driveattr['PBIC_STATUS'][4:]
         objMsg.printMsg("After PBIC_STATUS=%s" % self.dut.driveattr['PBIC_STATUS'])

         return pbic_test_on

      ###########################################################################

      return pbic_test_on
