#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: MediaScan module holds all media defect related classes and test implementations
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/10/19 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/MediaScan.py $
# $Revision: #2 $
# $DateTime: 2016/10/19 20:55:33 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/MediaScan.py#2 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from Process import CProcess
from Drive import objDut
import ScrCmds

import MessageHandler as objMsg
from TestParamExtractor import TP

###########################################################################################################
###########################################################################################################
class SeekType:
   readSeek = 0x15
   writeSeek = 0x25

###########################################################################################################
###########################################################################################################
class CServoFlaw(CProcess):
   def __init__(self):
      CProcess.__init__(self)
      self.dut = objDut

   def servoFlawScan(self,inPrm, seekType = SeekType.readSeek):
      inPrm.update({'SEEK_TYPE':seekType})
      self.St(inPrm)

###########################################################################################################
###########################################################################################################
class CUserFlaw(CProcess):
   """
      Description: User Area Flawscan class
   """
   def __init__(self, dut = None):
      CProcess.__init__(self)
      self.dut = objDut

   #-------------------------------------------------------------------------------------------------------
   def initSFT(self):
      """ init the servo flaw table """
      prm = {'test_num'    : 149,
             'prm_name'    : 'prm_INIT_SERV0_LIST_149',
             'timeout'     : 6000,
             'spc_id'      : 1,
             'CWORD1'      : 0x0002,}
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def initPList(self):
      """ init the primary defect list """
      prm = {'test_num'    : 149,
             'prm_name'    : 'prm_INIT_PLIST_149',
             'timeout'     : 3600,
             'spc_id'      : 1,
             'CWORD1'      : 0x0004,}
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def initTAList(self):
      """ init the TA list """
      prm = {'test_num'    : 149,
             'prm_name'    : 'prm_INIT_TA_LIST_149',
             'timeout'     : 3600,
             'spc_id'      : 1,
             'CWORD1'      : 0x0008,}
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def repSlipList(self, spcId = 1):
      """ Report the Slip List """
      prm = {'test_num'    : 107,
             'prm_name'    : 'prm_REPORT_SLIP_LIST_107',
             'timeout'     : 1800,
             'spc_id'      : spcId,
             'CWORD1'      : 0x0200,}
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def writeDbiToPList(self, spcId = 1):
      """ write DBI to PList """
      prm = {'test_num'    : 149,
             'prm_name'    : 'prm_WRITE_DBI_TO_PLIST_149',
             'timeout'     : 6000,
             'spc_id'      : spcId,
             'CWORD1'      : 0x0010,
             'CWORD2'      : 0x0040,}
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def writeSrvListToPList(self):
      """ write Servo List to PList """
      prm = {'test_num'    : 149,
             'prm_name'    : 'prm_WRITE_SRVLIST_TO_PLIST_149',
             'timeout'     : 6000,
             'spc_id'      : 1,
             'CWORD1'      : 0x0020,
             'CWORD2'      : 0x0040,}
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def xlateEvmDefectTypes(self):
      """ convert EVM Defect Types """
      prm = {'test_num'    : 149,
             'prm_name'    : 'prm_XLATE_EVM_DEFECT_TYPES_149',
             'timeout'     : 6000,
             'spc_id'      : 1,
             'CWORD1'      : 0x0080,
            }
      self.St(prm)
     
   #-------------------------------------------------------------------------------------------------------
   def writePListToSlipList(self, spcId = 1):
      """ write PList to Slip List """
      prm = {'test_num'    : 107,
             'prm_name'    : 'prm_WRITE_PLIST_TO_SLIP_LIST_107',
             'timeout'     : 6000,
             'spc_id'      : spcId,
             'CWORD1'      : 0x0100,
             }
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def repTAList(self):
      """ report the TA list """
      prm = {'test_num'    : 130,
             'prm_name'    : 'prm_REPORT_TA_LIST_130',
             'timeout'     : 5000,
             'spc_id'      : 1,
             'CWORD1'      : 0x0100,}
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def repPList(self):
      """ report the primary defect list """
      prm = {'test_num'    : 130,
             'prm_name'    : 'prm_REPORT_PLIST_130',
             'timeout'     : 1800,
             'spc_id'      : 1,
             'CWORD1'      : 0x0080,}
      if testSwitch.FE_0160361_220554_P_SET_T130_TIMEOUT_TO_3600_SECONDS:
         prm.update({'timeout' : 3600})
      if getattr(TP, 'setT130UserFlawListTimeout',  0):
         t130Timeout = getattr(TP,  'setT130UserFlawListTimeout', 1800)
         prm.update({'timeout' : t130Timeout})

      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def repServoFlaws(self, spcId = 1):
      """ report the servo flaw table """
      prm = {'test_num'    : 130,
             'prm_name'    : 'prm_REPORT_SERVO_LIST_130',
             'timeout'     : 1800,
             'spc_id'      : spcId,
             'CWORD1'      : 0x0040,}
      if testSwitch.FE_0160361_220554_P_SET_T130_TIMEOUT_TO_3600_SECONDS:
         prm.update({'timeout' : 3600})
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def repServoFlaws_T126(self, spcId = 1):
      """ report the servo flaw table """
      prm = {'test_num'    : 126,
             'prm_name'    : 'prm_REPORT_SERVO_LIST_126',
             'timeout'     : 1800,
             'spc_id'      : spcId,
             'CWORD1'      : 0x0002,
             'DblTablesToParse' : ['P126_SRVO_FLAW_REP'],}
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def initdbi(self):
      """ initialize & clear the dbilog """
      prm = {'test_num'    : 101,
             'prm_name'    : 'prm_INIT_DBI_101',
             'timeout'     : 600000,
             'spc_id'      : 1,}
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def repdbi(self, spcId = 1):
      """ Report the current dbilog """
      prm = {'test_num'    : 107,
             'prm_name'    : 'prm_REPORT_DBI_107',
             'timeout'     : 1800,
             'spc_id'      : spcId,}
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def repdbisummary(self):
      """ Display a summary report (ONLY) of verified errors per pass, and unique errors per pass """
      prm = {'test_num'      : 107,
             'prm_name'      : 'prm_REPORT_DBI_SUMMARY_107',
             'spc_id'        : 1,
             'REPORT_OPTION' : 0x02,}
      self.St(prm)

   #-------------------------------------------------------------------------------------------------------
   def runLULFlawscan(self, inPrm, mode = None, spc_id = 1):
      """
      Runs Load/Unload area defect scan and sets up representative data structures for performing differential analysis
      @param mode: None = do nothing, 1 = Set initial conditions, 2 = Calculate differences
      """
      if mode:
         try:
            startIndex = len(self.dut.dblData.Tables('P109_LUL_ERROR_COUNT').tableDataObj())
         except:
            self.dut.dblData.delTable('P109_LUL_ERROR_COUNT')
            startIndex = 0

         if testSwitch.virtualRun:
            startIndex = 0

      self.St(inPrm)

      if mode:
         lulData = self.dut.dblData.Tables('P109_LUL_ERROR_COUNT').tableDataObj()[startIndex:]
      else:
         return

      if mode == 1:
         #Set the objData for recovery later by the diff process
         self.dut.objData.update({'INITIAL_LUL_DATA':lulData})

      elif mode == 2:
         initLulData = self.dut.objData.retrieve('INITIAL_LUL_DATA')

         count = {}
         diff = {}

         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0,spc_id)

         if testSwitch.BF_0177502_357260_P_USE_HD_PHYS_PSN_FOR_LUL_SCAN_COMPARE:
            for head in self.dut.LgcToPhysHdMap:
               objMsg.printMsg("Initial: %s\nFinal: %s" % (initLulData, lulData))
               hd = str(head)
               headInitial = self.dut.dblData.Tables('P109_LUL_ERROR_COUNT').chopDbLog('HD_PHYS_PSN', 'match', matchName = hd, tbl = initLulData)
               headFinal = self.dut.dblData.Tables('P109_LUL_ERROR_COUNT').chopDbLog('HD_PHYS_PSN', 'match', matchName = hd)
               objMsg.printMsg("Initial: %s\nFinal: %s" % (headInitial, headFinal))

               count[head] = int(headFinal[-1]['DEFECT_COUNT'])
               diff[head] = int(headFinal[-1]['DEFECT_COUNT']) - int(headInitial[-1]['DEFECT_COUNT'])

               self.dut.dblData.Tables('P_LUL_DEFECT_DIFF_HD').addRecord(
                        {
                        'HD_PHYS_PSN'        : head,
                        'SPC_ID'             : spc_id,
                        'OCCURRENCE'         : occurrence,
                        'SEQ'                : curSeq,
                        'TEST_SEQ_EVENT'     : testSeqEvent,
                        'DEFECT_COUNT'       : count[head],
                        'DEFECT_COUNT_DIFF'  : diff[head]
                        })
         else:
            for head in range(self.dut.imaxHead):
               objMsg.printMsg("Initial: %s\nFinal: %s" % (initLulData, lulData))
               hd = str(head)
               headInitial = self.dut.dblData.Tables('P109_LUL_ERROR_COUNT').chopDbLog('HD_LGC_PSN', 'match', matchName = hd, tbl = initLulData)
               headFinal = self.dut.dblData.Tables('P109_LUL_ERROR_COUNT').chopDbLog('HD_LGC_PSN', 'match', matchName = hd)
               objMsg.printMsg("Initial: %s\nFinal: %s" % (headInitial, headFinal))

               count[head] = int(headFinal[-1]['DEFECT_COUNT'])
               diff[head] = int(headFinal[-1]['DEFECT_COUNT']) - int(headInitial[-1]['DEFECT_COUNT'])

               self.dut.dblData.Tables('P_LUL_DEFECT_DIFF_HD').addRecord(
                        {
                        'HD_PHYS_PSN'        : self.dut.LgcToPhysHdMap[head],
                        'SPC_ID'             : spc_id,
                        'OCCURRENCE'         : occurrence,
                        'SEQ'                : curSeq,
                        'TEST_SEQ_EVENT'     : testSeqEvent,
                        'DEFECT_COUNT'       : count[head],
                        'DEFECT_COUNT_DIFF'  : diff[head]
                        })

         totalCount = sum(count.values())
         totalDefects = sum(diff.values())

         self.dut.dblData.Tables('P_LUL_DEFECT_DIFF_DRIVE').addRecord(
                     {
                     'SPC_ID'             : spc_id,
                     'OCCURRENCE'         : occurrence,
                     'SEQ'                : curSeq,
                     'TEST_SEQ_EVENT'     : testSeqEvent,
                     'DEFECT_COUNT'       : totalCount,
                     'DEFECT_COUNT_DIFF'  : totalDefects
                     })
         objMsg.printDblogBin(self.dut.dblData.Tables('P_LUL_DEFECT_DIFF_HD'))
         objMsg.printDblogBin(self.dut.dblData.Tables('P_LUL_DEFECT_DIFF_DRIVE'))

      else:
         ScrCmds.raiseException(11044,"Invalid LUL flawscan mode set: %s" % (mode,))


   #-------------------------------------------------------------------------------------------------------
   def checkSpareSpace(self):
      """Ensures SCSI drives have available slip space for G-List merge in field re-format."""
      #From T130 help: "SCALED_VAL scales the drive capacity to allocate sectors for
      # spares, BIPS, etc. This should be same value as Test 210 SCALED_VAL."

      prm_T130_CHK_AVAIL_SLIPS = {
         'test_num'                 : 130,
         'prm_name'                 : 'prm_T130_CHK_AVAIL_SLIPS',
         'timeout'                  : 600,
         'spc_id'                   : 1,
         'CWORD1'                   : (0x4080,),
         #'SCALED_VAL'               : (9900,), #Need to obtain from VBAR
         'SLIP_LIMIT_PERCENT'       : (95,), #Slip space no fuller than this
      }

      #Here, we pick this value up by traversing VBAR's way of generating it.
      nibPartNum = self.dut.partNum[:7]
      try:
         import PIF
         nibTableNative = PIF.nibletTable[nibPartNum]['Native'][0]
         nibTableCapacity = PIF.nibletTable[nibPartNum]['Capacity'][0]
      except:
         objMsg.printMsg("PIF nibletTable undefined for part number: %s" %nibPartNum)
         ScrCmds.raiseException(11044,"PIF nibletTable undefined")

      nibletLibKey = self.dut.serialnum[1:3] +'_'+ nibTableNative +'_'+ nibTableCapacity
      try:
         #T130 takes integer
         scaledVal_VBAR = int(PIF.nibletLibrary[nibletLibKey]['PBA_TO_LBA_SCALER'] * 10000)
      except:
         objMsg.printMsg("No PBA_TO_LBA_SCALER defined in PIF or WaterfallNiblets for key: %s" %nibletLibKey)
         ScrCmds.raiseException(11044,"VBAR PBA_TO_LBA_SCALER undefined")

      prm_T130_CHK_AVAIL_SLIPS.update({'SCALED_VAL':scaledVal_VBAR})

      self.St(prm_T130_CHK_AVAIL_SLIPS)

   #-------------------------------------------------------------------------------------------------------
   def saveSListToPcFile(self):
      """ Save the servo flaw table to pcfile"""
      prm = {'test_num'    : 149,
             'prm_name'    : 'prm_SAVE_SLIST_TO_PCFILE_149',
             'timeout'     : 6000,
             'spc_id'      : 1,
             'CWORD1'      : 0x0800,
             'CWORD2'      : 0x0600,
             }
      self.St(prm)      

   #-------------------------------------------------------------------------------------------------------
   def restoreSListFromPcFile(self):
      """ Restore the servo flaw table from pcfile"""
      prm = {'test_num'    : 149,
             'prm_name'    : 'prm_RESTORE_SLIST_FROM_PCFILE_149',
             'timeout'     : 6000,
             'spc_id'      : 1,
             'CWORD1'      : 0x0800,
             'CWORD2'      : 0x0200,
             }
      self.St(prm)


###########################################################################################################
###########################################################################################################
