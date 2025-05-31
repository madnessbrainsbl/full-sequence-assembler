#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2011, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: This module holds all related classes and functions for performing optimizations
#              related to Shingled VBAR and format selection
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/smr.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/smr.py#1 $
# Level: 34
#---------------------------------------------------------------------------------------------------------#

from Test_Switches import testSwitch
from Constants import *
import math, struct
import ScrCmds
from TestParamExtractor import TP
from Temperature import CTemperature
from DesignPatterns import Singleton
import Utility
from bpiFile import CBpiFile
from Process import CProcess
import MessageHandler as objMsg
from Drive import objDut
from PowerControl import objPwrCtrl
from PreAmp import CPreAmp
from State import CState
import VBAR
import FSO
import dbLogUtilities

SMR_ZONE_POS = 198

def addDbLogRow(tablename,datadict):
   objDut.dblData.Tables(tablename).addRecord(datadict)

def dumpDbLogTable(tablename):
   objMsg.printDblogBin(objDut.dblData.Tables(tablename))

def selectTable(tablename):
   if testSwitch.virtualRun:
      return objDut.dblData.Tables(tablename).tableDataObj()
   else:
      return objDut.objSeq.SuprsDblObject[tablename]

def calcBerFromSfrBieTargets(sfr,bie,codewordSizeInBits=5088):

   # prime estimate:  This will be a bit pessimistic because bie/codewordSize
   #   doesn't take into account the fact that there could be less than bie in error
   #
   def solveForSfr(p,bie,cws):

      p_x = (1-p)**cws
      sfr = 1-p_x
      for i in xrange(bie):
         p_x *= p/(1-p)*(cws-i)/(i+1)
         sfr -= p_x
      return sfr


   phat = (bie+.5)/codewordSizeInBits
   pstep = phat/10.0
   sfrhat = solveForSfr(phat,bie,codewordSizeInBits)
   eps = .00001
   prevsfr = sfrhat
   iteration = 0
   while abs(sfrhat - sfr)>eps and iteration <= 100:
      iteration+=1
      if sfrhat > sfr and pstep > 0:
         pstep *= -1/2.0
      elif sfrhat < sfr and pstep < 0:
         pstep *= -1/2.0
      phat += pstep
      prevsfr=sfrhat
      sfrhat = solveForSfr(phat,bie,codewordSizeInBits)

   return math.log10(phat)

def calcSfrBieTargetsFromBER(ber,codewordSizeInBits=5088):

   # we are aiming for a SFR in the 10-20% range.

   bie = 0
   sfr = 1

   p= 10**ber;

   p_x = (1-p)**codewordSizeInBits
   sfr = 1-p_x

   for i in xrange(codewordSizeInBits):
      if sfr < .20:
         break
      bie += 1
      p_x *= p/(1-p)*(codewordSizeInBits-i)/(i+1)
      sfr -= p_x
   return (sfr,bie)

class CSmrMeasurements(CState,CProcess):
   """
   Description:  A class to perform measurements relevant to shingled
   """

   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      CProcess.__init__(self)

      self.formatScaler = None

   def run(self):
      self.loadFormatScaler()

      testZones = self.params.get('ZONES',[i*objDut.numZones/100 for i in [0,14,31,51,67,84,97]])
      testHeads = self.params.get('HEADS',range(objDut.imaxHead))
      backoff = self.params.get('BACKOFF',40)
      iteration = self.params.get('ITERATIONS',7)
      sova1ber = self.params.get('SOVA1BER',-2.3)

      for hd in testHeads:
         for zn in testZones:
            self.measureAZone(hd,zn,iteration,sova1ber,nbackoff=backoff)

      dumpDbLogTable('P_VBAR_SMR_MEASUREMENT')


   def loadFormatScaler(self):
      self.formatScaler = VBAR.CVbarFormatScaler()

   def measureBPI(self,hd,zn,overrideprm = {}):
      prm_BPI_211 = {'test_num'           : 211,
                     'prm_name'           : 'MeasureBPI_211',
                     'TEST_HEAD'          : hd,
                     'ZONE'               : zn,
                     'ZONE_POSITION'      : SMR_ZONE_POS, # work around for FLASH_LED issues in st 211 originally 199
                     'BPI_MAX_PUSH_RELAX' : 40,
                     'CWORD1'             : 0x0005, #Enable multi-track mode
                     'SET_OCLIM'          : 1228,
                     'timeout'            : 300,
                     'spc_id'             : 0,
                     'TARGET_SER'         : 15,
                     'DblTablesToParse'   : ['P211_BPI_CAP_AVG'],
                     }

      prm_BPI_211.update(overrideprm)
      try:
         self.St(prm_BPI_211)

         table = selectTable('P211_BPI_CAP_AVG')

         bpi = float(table[-1]['BPI_CAP_AVG'])
      except:
         bpi = 0

      return self.formatScaler.scaleBPI(hd,zn,bpi)

   def measureTPI(self,hd,zn,bpiForMeasurement=0,startSqz=1.0,sqzType='DSS',overrideprm={}):

      sqzTypeMap={'DSS':0,'IDSS':0x8000,'ODSS':0x4000}

      prm_TPI_211 = {'test_num'           : 211,
                     'prm_name'           : 'MeasureTPI_211',
                     'TEST_HEAD'          : hd,
                     'ZONE'               : zn,
                     'NUM_SQZ_WRITES'     : 6 + sqzTypeMap[sqzType],
                     'ZONE_POSITION'      : SMR_ZONE_POS,
                     'ADJ_BPI_FOR_TPI'    : bpiForMeasurement,
                     'START_OT_FOR_TPI'   : int((startSqz-1)*256) - 4,
                     'TPI_MAX_PUSH_RELAX' : 90,
                     'CWORD1'             : 0x0026,   #Enable multi-track mode
                     'CWORD2'             : 0,
                     'SET_OCLIM'          : 1228,
                     'TARGET_SER'         : 15,
                     'TLEVEL'             : 7,
                     'timeout'            : 600,
                     'spc_id'             : 0,
                     'DblTablesToParse'   : ['P211_RD_OFST_AVG', 'P211_TPI_CAP_AVG'],
                     'RESULTS_RETURNED'   : 0xF,
                     }

      if sqzType != 'DSS':
         prm_TPI_211['CWORD2'] |= 0x8

      prm_TPI_211.update(overrideprm)

      self.St(prm_TPI_211)
      table = selectTable('P211_TPI_CAP_AVG')
      tpi = float(table[-1]['TPI_CAP_AVG'])

      try:
         table = selectTable('P211_RD_OFST_AVG')
         read_offset = int(table[-1]['RD_OFST_AVG'])
      except:
         read_offset=0

      return self.formatScaler.scaleTPI(hd,zn,tpi),read_offset

   def measureHMS(self,hd,zn,bpiForMeasurement,overrideprm={}):
      prm_HMS_211 = {'test_num'           : 211,
                     'prm_name'           : 'MeasureHMS_211',
                     'TEST_HEAD'          : hd,
                     'ZONE'               : zn,
                     'ZONE_POSITION'      : SMR_ZONE_POS,
                     'NUM_TRACKS_PER_ZONE': 6,
                     'HMS_MAX_PUSH_RELAX' : 300,
                     'HMS_STEP'           : 5,
                     'ADJ_BPI_FOR_TPI'    : bpiForMeasurement,
                     'THRESHOLD'          : 90,
                     'CWORD1'             : 0x400C,
                     'SET_OCLIM'          : 1228,
                     'TARGET_SER'         : 5,
                     'TLEVEL'             : 7,
                     'NUM_SQZ_WRITES'     : 0,
                     'timeout'            : 600,
                     'spc_id'             : 0,
                     'DblTablesToParse'   : ['P211_HMS_CAP_AVG'],
                    }

      if testSwitch.FE_0172018_208705_P_ENABLE_HMS_2PT:
         prm_HMS_211.update({
                     'CWORD1'             : 0x600C,
                  })

      prm_HMS_211.update(overrideprm)

      try:
         self.St(prm_HMS_211)
         table = selectTable('P211_HMS_CAP_AVG')
         hmsc = float(table[-1]['HMS_CAP_AVG'])
      except:
         hmsc=0
      return hmsc

   def measureAZone(self,hd,zn,iterations=7,sova1ber=-2.3,nbackoff=6):
      # first measure the unsqueezed Error Rate
      if iterations > 0:
         target_level = {'TLEVEL':iterations,'TARGET_SER':15,'TPI_TLEVEL':iterations,'TPI_TARGET_SER':15}
      else:
         (sfrTarget,bieThresh)=calcSfrBieTargetsFromBER(sova1ber)
         target_level = {'TLEVEL':0,'TARGET_SER':int(round(sfrTarget*100,0)),'THRESHOLD':bieThresh,
                         'TPI_TLEVEL':0,'TPI_TARGET_SER':int(round(sfrTarget*100,0))}
      BPIc = self.measureBPI(hd,zn,target_level)
      unscaledBPIc = self.formatScaler.unscaleBPI(hd,zn,BPIc)
      (sfrTarget,bieThresh)=calcSfrBieTargetsFromBER(sova1ber)
      BPIcSova = self.measureBPI(hd,zn,{'TLEVEL':0,'TARGET_SER':int(round(sfrTarget*100,0)),'THRESHOLD':bieThresh})
      BPIpct = (unscaledBPIc-1)*100
      # next start backing off on BPI and measure the TPICapability
      startBpiBackOff = int(BPIpct)
      remainder = BPIpct - startBpiBackOff
      if remainder < 0:
         startBpiBackOff -= 2
      elif remainder < 0.5:
         startBpiBackOff -= 1

      numFlatMeas = 0
      tdata = []

      for sqzType in ('DSS','IDSS','ODSS'):
         bestoffset=0
         tpifeedforward = .55
         done = False
         BpiBackOff = startBpiBackOff
         while not done:
            curSeq,occurrence,testSeqEvent = objDut.objSeq.registerCurrentTest(0)
            target_level['READ_OFFSET']=bestoffset
            (tpic,bestoffset) = self.measureTPI(hd,zn,BpiBackOff,tpifeedforward,sqzType,overrideprm=target_level)
            # Go until the delta measurement is small or nbackoff is exceeded
            tdata.append((hd,zn,BPIc,sqzType,BpiBackOff,tpic))
            addDbLogRow('P_VBAR_SMR_MEASUREMENT', {
               'SPC_ID'          : 1,
               'OCCURRENCE'      : occurrence,
               'SEQ'             : curSeq,
               'TEST_SEQ_EVENT'  : testSeqEvent,
               'HD_PHYS_PSN'     : objDut.LgcToPhysHdMap[hd],
               'HD_LGC_PSN'      : hd,
               'DATA_ZONE'       : zn,
               'BPI_CAP'         : BPIc,
               'SOVA_CAP'        : BPIcSova,
               'SQZ_TYPE'        : ord(sqzType[0]),
               'MSRD_BPI'        : self.formatScaler.scaleBPI(hd,zn,1+BpiBackOff/100.0),
               'SQZ_CAP'         : tpic,
            })

            if tpic - tpifeedforward <= .0005:
               numFlatMeas += 1
            else:
               numFlatMeas = 0
            if BPIpct - BpiBackOff > nbackoff or (tpic >.5 and numFlatMeas >= 300):
               done = True

            BpiBackOff -= 1
            tpifeedforward = self.formatScaler.unscaleTPI(hd,zn,tpic)

      for d in tdata:
         objMsg.printMsg(d)




class CFineTuneSqueezeOffset(CState,CProcess):

   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      CProcess.__init__(self)

   def run(self):
      self.prm_OFST_236 = {'test_num' : 236,
                           'prm_name' : 'FineTuneSqzOfst',
                           'HEAD_MASK': 0x3FF,
                           'ZONE_MASK': (0xFFFF,0xFFFF),
                           'ZONE_MASK_EXT': (0xFFFF,0xFFFF),
                           'CWORD3'   : 1,
                           'ZONE_POSITION':198,
                           'BANDSIZE' : 1,
                           'timeout'  : 60000*50,
                          }
      if self.params.get('ON_TCC', 0):
         self.prm_OFST_236.update({'CWORD1'   : 0x800})
      if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
         self.prm_OFST_236.update({'CWORD1': 0x1401, 'MAX_RANGE': 30, 'NORMAL_STEP': 3})
         if testSwitch.FAST_2D_VBAR_TESTTRACK_CONTROL:
            self.prm_OFST_236.update({'CWORD1': self.prm_OFST_236['CWORD1'] | 0x0002})
      if not testSwitch.extern.SFT_TEST_0236:
         objMsg.printMsg("Read Centering Test Not Supported in this SF3 - skipping")
         return
      
      #turn on the zap after turning off in vbar_otc
      from Servo import CServoOpti
      oSrvOpti = CServoOpti()
      oSrvOpti.St(TP.setZapOnPrm_011)
      if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
         oSrvOpti.St({'test_num':178, 'prm_name':'Save SAP in RAM to FLASH', 'CWORD1':0x420})
        
      testZones = self.retrieveVBAR_info(range(self.dut.numZones)) #return test zone, skipping UMP zone
      if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
         MaskList = Utility.CUtility().convertListToZoneBankMasks(testZones)
         for bank, list in MaskList.iteritems():
            if list:
               self.prm_OFST_236['ZONE_MASK_EXT'], self.prm_OFST_236['ZONE_MASK'] = \
                  Utility.CUtility().convertListTo64BitMask(list)
               self.prm_OFST_236['ZONE_MASK_BANK'] = bank
               self.St(self.prm_OFST_236)
      else:
         znMaskExt, znMask = Utility.CUtility().convertListTo64BitMask(testZones)
         self.prm_OFST_236.update({'ZONE_MASK'     : znMask,         
                                    'ZONE_MASK_EXT' : znMaskExt,})
         self.St(self.prm_OFST_236)
      
      save = self.params.get('SAVE', 1) 
      # save to flash
      if save == 1:
         self.St({'test_num':178,'CWORD1':0x220,})
      
   def retrieveVBAR_info(self, zn_range):
      if testSwitch.extern.FE_0164615_208705_T211_STORE_CAPABILITIES:
         import SIM_FSO, cPickle
         data = SIM_FSO.CSimpleSIMFile("VBAR_DATA").read()
         wpp, (tableData, colHdrData) = cPickle.loads(data)
         self.measAllZns = VBAR.CVbarMeasurement()
         self.measAllZns.unserialize((tableData, colHdrData))
         #retrive track per band of each input zone
         zn_list = [ zn for zn in zn_range if (self.measAllZns.getRecord('TRACK_PER_BAND', 0, zn)) > 1 ]
         return zn_list
      else:
         objMsg.printMsg("CVBAR_DATA not found")
         return zn_range
      
class CPopulateSqueezeOffset(CState,CProcess):

   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      CProcess.__init__(self)


   def getSqueezeOffset(self,hd,zn,sqzType='IDSS',overrideprm={}):

      sqzTypeMap={'DSS':0,'IDSS':0x8000,'ODSS':0x4000}

      prm_TPI_211 = {'test_num'           : 211,
                     'prm_name'           : 'MeasureTPI_211',
                     'TEST_HEAD'          : hd,
                     'ZONE'               : zn,
                     'NUM_SQZ_WRITES'     : 6 + sqzTypeMap[sqzType],
                     'ZONE_POSITION'      : SMR_ZONE_POS,
                     'ADJ_BPI_FOR_TPI'    : 0,
                     'START_OT_FOR_TPI'   : 0,
                     'CWORD1'             : 0x0026,   #Enable multi-track mode
                     'CWORD2'             : 0x0008,   # Collect read offset
                     'SET_OCLIM'          : 1228,
                     'TARGET_SER'         : 15,
                     'TLEVEL'             : 7,
                     'timeout'            : 600,
                     'spc_id'             : 0,
                     'DblTablesToParse'   : ['P211_RD_OFST_AVG'],
                     }

      prm_TPI_211.update(overrideprm)

      try:
         self.St(prm_TPI_211)
         table = selectTable('P211_RD_OFST_AVG')
         read_offset = int(table[-1]['RD_OFST_AVG'])
      except:
         read_offset = 0

      return read_offset  # Reported in signed Q8

   def writeReadOffsetToRap(self,heads,zn,offsets):
      prm_210 = {'test_num': 210,
                 'prm_name': 'Update SqueezeOffsets To Drive',
                 'timeout' : 1800,
                 'spc_id'  : 0,
                 'CWORD1'  : 0x8000,
                 'ZONE'    : zn*256 + zn,
                 'HEAD_MASK' : 0,
                 'RD_SCALE_FACTORS' : [0]*16
                 }


      offsetFactor = self.params.get('FACTOR',0.5)
      for hd,offset in zip(heads,offsets):
         prm_210['HEAD_MASK'] |= (1<<hd)
         prm_210['RD_SCALE_FACTORS'][hd]=int(offset*offsetFactor)

      self.St(prm_210)

   def run(self):

      testZones = self.params.get('ZONES',range(objDut.numZones))
      testHeads = self.params.get('HEADS',range(objDut.imaxHead))
      closestSysZone = FSO.CFSO().findSysAreaClosestDataZone(testHeads)

      for zn in testZones:
         offsets=[]
         for hd in testHeads:
            if zn > closestSysZone[hd]:
               sqztype = 'ODSS'
            else:
               sqztype = 'IDSS'
            offsets.append(self.getSqueezeOffset(hd,zn,sqztype))
         self.writeReadOffsetToRap(testHeads,zn,offsets)

      # save rap to flash
      FSO.CFSO().saveRAPtoFLASH()



class CSMRDataGather(CState,CProcess):

   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      CProcess.__init__(self)

      self.data = {}
      self.bpiFile = CBpiFile()

   def run(self):
      testZones = self.params.get('ZONES',range(objDut.numZones))
      testHeads = self.params.get('HEADS',range(objDut.imaxHead))
      formatsToTest = self.params.get('FORMATS',range(self.bpiFile.getNumBpiFormats()))

      for formatNum in formatsToTest:
         self.loadFormat(formatNum)
         for hd in testHeads:
            for zn in testZones:
               self.takeMeasurements(hd,zn,formatNum)


   def takeMeasurements(self,hd,zn,formatNum):
      self.opti()
      prevdata = self.data.get((hd,zn,formatNum-1),{'SQZCDSS':1.0,'SQZCODSS':1.0,'SQZCIDSS':1.0})
      bpic = self.getbpicap(hd,zn)
      sqzcdss = self.gettpicap(hd,zn,'DSS',prevdata['SQZCDSS'])
      sqzcodss = self.gettpicap(hd,zn,'ODSS',prevdata['SQZCODSS'])
      sqzcidss = self.gettpicap(hd,zn,'IDSS',prevdata['SQZCIDSS'])
      hmsc = self.gethmscap(hd,zn)

      data={}
      data['HEAD']=hd
      data['ZONE']=zn
      data['FORMAT']=formatNum
      data['SQZCDSS']=sqzcdss
      data['SQZCODSS']=sqzcodss
      data['SQZCIDSS']=sqzcidss
      data['BPIC']=bpic
      data['HMSC']=hmsc

      self.data[(hd,zn,formatNum)]=data

      objMsg.printMsg("%d %d %d %f %f %f %f %f" % (hd,zn,formatNum,bpic,sqzcdss,sqzcodss,sqzcidss,hmsc))

   def opti(self):
      pass

   def getbpicap(self,hd,zn):
      prm_BPI_211 = {'test_num'           : 211,
                     'prm_name'           : 'MeasureBPI_211',
                     'TEST_HEAD'          : hd,
                     'ZONE'               : zn,
                     'ZONE_POSITION'      : SMR_ZONE_POS, # work around for FLASH_LED issues in st 211 originally 199
                     'BPI_MAX_PUSH_RELAX' : 60,
                     'CWORD1'             : 0x0005, #Enable multi-track mode
                     'SET_OCLIM'          : 1228,
                     'timeout'            : 300,
                     'spc_id'             : 0,
                     'TARGET_SER'         : 15,
                     }

      self.St(prm_BPI_211)

      return 0.0

   def gettpicap(self,hd,zn,sqzType='DSS',startSqz=1.0):

      sqzTypeMap={'DSS':0,'IDSS':0x8000,'ODSS':0x4000}


      prm_TPI_211 = {'test_num'           : 211,
                     'prm_name'           : 'MeasureTPI_211',
                     'TEST_HEAD'          : hd,
                     'ZONE'               : zn,
                     'NUM_SQZ_WRITES'     : 6 + sqzTypeMap[sqzType],
                     'ZONE_POSITION'      : SMR_ZONE_POS,
                     'ADJ_BPI_FOR_TPI'    : 0,
                     'START_OT_FOR_TPI'   : int((startSqz-1)*256) - 4,
                     'TPI_MAX_PUSH_RELAX' : 90,
                     'CWORD1'             : 0x0026,   #Enable multi-track mode
                     'CWORD2'             : 0,
                     'SET_OCLIM'          : 1228,
                     'TARGET_SER'         : 15,
                     'TLEVEL'             : 7,
                     'timeout'            : 600,
                     'spc_id'             : 0,
                     'RESULTS_RETURNED'   : 0x0,
                     }

      if sqzType != 'DSS':
         prm_TPI_211['CWORD2'] |= 0x8

      if testSwitch.extern.FE_0157099_211428_T211_OFFSET_READ_SUPPORT:
         table = dbLogUtilities.DBLogReader(self.dut, 'P211_TPI_CAP_AVG2')
      else:
         table = dbLogUtilities.DBLogReader(self.dut, 'P211_TPI_CAP_AVG')

      table.ignoreExistingData()

      self.St(prm_TPI_211)

      row = table.findRow({'HD_LGC_PSN':hd, 'DATA_ZONE':zn})
      if row:
         tpi = float(row['TPI_CAP_AVG'])
      else:
         tpi = 0.0

      return tpi

   def gethmscap(self,hd,zn):
      prm_HMS_211 = {'test_num'           : 211,
                     'prm_name'           : 'MeasureHMS_211',
                     'TEST_HEAD'          : hd,
                     'ZONE'               : zn,
                     'ZONE_POSITION'      : SMR_ZONE_POS,
                     'NUM_TRACKS_PER_ZONE': 6,
                     'HMS_MAX_PUSH_RELAX' : 300,
                     'HMS_STEP'           : 5,
                     'ADJ_BPI_FOR_TPI'    : 0,
                     'THRESHOLD'          : 90,
                     'CWORD1'             : 0x400C,
                     'SET_OCLIM'          : 1228,
                     'TARGET_SER'         : 5,
                     'TLEVEL'             : 7,
                     'NUM_SQZ_WRITES'     : 0,
                     'timeout'            : 600,
                     'spc_id'             : 0,
                    }

      if testSwitch.FE_0172018_208705_P_ENABLE_HMS_2PT:
         prm_HMS_211.update({
                     'CWORD1'             : 0x600C,
                  })

      self.St(prm_HMS_211)

      return 0.0

   def loadFormat(self,formatNum):
      prm_210 = {'test_num': 210,
                 'prm_name': 'Update Formats To Drive',
                 'timeout' : 1800,
                 'dlfile'  : (CN, self.bpiFile.bpiFileName),
                 'spc_id'  : 0,
                 'BPI_GROUP_EXT' : (formatNum,)*16,
                 'ZONE' : 0xff,
                 'HEAD_MASK' : 0xff,
                 'CWORD1' : 0x101,
                 }

      self.St(prm_210)
