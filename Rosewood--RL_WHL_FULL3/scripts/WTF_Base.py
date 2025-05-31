#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Waterfall base module
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/09/28 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/WTF_Base.py $
# $Revision: #5 $
# $DateTime: 2016/09/28 23:49:05 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/WTF_Base.py#5 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import MessageHandler as objMsg
from ScrCmds import raiseException
from State import CState
from WTF_Tools import CWTF_Tools
from FSO import CFSO
from VBAR import CVBAR
from Utility import getVBARPrintDbgMsgFunction

printDbgMsg = getVBARPrintDbgMsgFunction()
verbose = 0       # Set to a value greater than 0 for various levels of debug output in the log.


#----------------------------------------------------------------------------------------------------------
class CWaterfallTest(CState, CWTF_Tools):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = ['AFH1']
      CState.__init__(self, dut, depList)

      # Initialize the SPC_ID
      from Utility import CSpcIdHelper
      CSpcIdHelper(self.dut).getSetIncrSpcId('P_VBAR_FORMAT_SUMMARY', startSpcId = 0, increment = 0, useOpOffset = 1)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oFSO = CFSO()
      self.dut.pn_backup = self.dut.driveattr['PART_NUM']
      printDbgMsg("CWaterfallTest: Begin with part number %s " %self.dut.pn_backup )
      self.buildClusterList()

      if self.dut.currentState in ['HMSC_DATA']:
         try:
            hms_table_start = len(self.dut.dblData.Tables('P_VBAR_HMS_ADJUST'))
         except: 
            hms_table_start = 0
      #
      if self.params.get('ENABLE_ZAP', 1):
         if testSwitch.FE_SGP_OPTIZAP_ADDED: #turn on the ZAP
            printDbgMsg("Waterfall: Tuning on ZAP")
            if testSwitch.ENABLE_T175_ZAP_CONTROL:
               self.oFSO.St(TP.zapPrm_175_zapOn)
            else:
               self.oFSO.St(TP.setZapOnPrm_011)
               self.oFSO.saveSAPtoFLASH()

      # call vbar from here
      if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_VBAR_MSG:
         objMsg.printMsg("calling vbar")
         for niblet in self.VbarNibletCluster:
            objMsg.printMsg("local vbar cluster: %s " % str(niblet))

      if verbose: #cut logs
         for niblet in TP.VbarNibletCluster:
            objMsg.printMsg(self.oFSO.oUtility.convertDictToPrintStr(niblet,'global vbar cluster',False,False))

      for i in xrange(len(TP.VbarPartNumCluster)):
         if TP.VbarPartNumCluster[i] == '': break
         objMsg.printMsg("TP.VbarPartNumCluster[%d]: %s " %(i, TP.VbarPartNumCluster[i]))

      oVbarTuning = CVbarTuning(self.dut,self.params)
      nibletIndex, vbarResult = oVbarTuning.run()
      oVbarTuning = None

      if not self.params.get('NO_DISABLE_ZAP', 0):
         printDbgMsg("Waterfall: Tuning off ZAP upon exiting")
         if testSwitch.ENABLE_T175_ZAP_CONTROL:
            self.oFSO.St(TP.zapPrm_175_zapOff)
         else:
            self.oFSO.St(TP.setZapOffPrm_011)
            if not testSwitch.BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL:
               self.oFSO.saveSAPtoFLASH()
      
      if self.params.get('HANDLE_WTF_EXT', 0) and \
         self.dut.currentState not in ['HMSC_DATA']:
         # Display vbar result
         self.keyCounter, self.nibletString = self.VbarNibletCluster[nibletIndex]

         objMsg.printMsg("From_Vbar")
         objMsg.printMsg("EC        : %s  nibletIndex: %s" % (vbarResult, nibletIndex))
         objMsg.printMsg("keyCounter: %s  nibletString: %s" % (self.keyCounter, self.nibletString))

         #update partnumber and WTF attributes
         self.updateWTF(vbarResult == 12169)

         self.updateATTR(self.partNum,self.keyCounter)

         if vbarResult == 0:
            # Update family info in the drive
            hdCount = TP.VbarNibletCluster[nibletIndex]['NUM_HEADS']
            self.oFSO.setFamilyInfo(TP.familyInfo,TP.famUpdatePrm_178, forceHdCount=hdCount)
            objMsg.printMsg("Waterfall vbar passed, exit")
            self.dut.VbarDone = 1   # for depop use

            if testSwitch.FE_SGP_EN_REPORT_WTF_FAILURE and ((self.dut.pn_backup != self.dut.driveattr['PART_NUM']) or self.dut.VbarRestarted) and not testSwitch.virtualRun:
               # if 500G OEM to 500G SBS waterfall, keep *EC48451/48452 as unyielded *EC48451/48452
               if testSwitch.EN_REPORT_SAME_CAPACITY_WTF and (self.dut.pn_backup[5] == self.dut.driveattr['PART_NUM'][5]):  #no capacity changed
                  if self.dut.driveattr['DESTROKE_REQ'] == 'DSD' or self.dut.driveattr['DESTROKE_REQ'] == 'DSD_NEW_RAP':
                     tmpEC = 48452        #destroke drive
                  else:
                     tmpEC = 48451
                  self.dut.driveattr["DNGRADE_ON_FLY"] = '%s_%s_%s'%(self.dut.nextOper, self.dut.pn_backup[-3:], str(tmpEC))
               else:
                  if self.dut.driveattr['DESTROKE_REQ'] == 'DSD' or self.dut.driveattr['DESTROKE_REQ'] == 'DSD_NEW_RAP':
                     tmpEC = 48453        #destroke drive
                  else:
                     tmpEC = 12168
               self.WTF_Unyielded(ec=tmpEC)

         elif vbarResult == 'DEPOP_RESTART':
            objMsg.printMsg('*'*100)
            objMsg.printMsg("DEPOP REQUESTED")
            objMsg.printMsg('*'*100)
            from OTF_Waterfall import WTFDisposition
            WTFDisposition(self.dut).run(WtfRequest =WTFDisposition.dispoEnum.DEPOP)

         #elif vbarResult == 91919 :
         elif vbarResult == 'RPM_RESTART':
            objMsg.printMsg('*'*100)
            objMsg.printMsg("RPM RESTART REQUESTED")
            objMsg.printMsg('*'*100)
            self.resetWTFAttr()
            from OTF_Waterfall import WTFDisposition
            WTFDisposition(self.dut).run(WtfRequest =WTFDisposition.dispoEnum.RPM_RESTART)

         else:
            objMsg.printMsg("ERROR: Waterfall vbar failed, exit")

            if testSwitch.FE_SGP_EN_REPORT_WTF_FAILURE and ((self.dut.pn_backup != self.dut.driveattr['PART_NUM']) or self.dut.VbarRestarted) and not testSwitch.virtualRun:
               # if 500G OEM to 500G SBS waterfall, keep *EC48451/48452 as unyielded *EC48451/48452
               if testSwitch.EN_REPORT_SAME_CAPACITY_WTF and (self.dut.pn_backup[5] == self.dut.driveattr['PART_NUM'][5]):  #no capacity changed
                  if self.dut.driveattr['DESTROKE_REQ'] == 'DSD' or self.dut.driveattr['DESTROKE_REQ'] == 'DSD_NEW_RAP':
                     tmpEC = 48452        #destroke drive
                  else:
                     tmpEC = 48451
               else:
                  if self.dut.driveattr['DESTROKE_REQ'] == 'DSD' or self.dut.driveattr['DESTROKE_REQ'] == 'DSD_NEW_RAP':
                     tmpEC = 48453        #destroke drive
                  else:
                     tmpEC = 12168
               self.WTF_Unyielded(ec=tmpEC)

            if not testSwitch.virtualRun:
               raiseException(vbarResult, "ERROR: VBAR failure, exit")


      if self.dut.currentState in ['HMSC_DATA']:
         from MathLib import stDev_standard, mean
         
         listHMScap = list(list() for i in xrange(self.dut.imaxHead))
         WkWrtEC = 14805

         try:
            colDict = self.dut.dblData.Tables('P_VBAR_HMS_ADJUST').columnNameDict()
            pHMSTbl = self.dut.dblData.Tables('P_VBAR_HMS_ADJUST').rowListIter(index=hms_table_start)
         except:
            objMsg.printMsg('WARNING...P_VBAR_HMS_ADJUST NOT FOUND')
            return

         objMsg.printMsg("testSwitch.ENABLE_HMSCAP_SCREEN = %d" % testSwitch.ENABLE_HMSCAP_SCREEN)
         objMsg.printMsg("MEAN_HMSCap_REQUIRED = %.3f" % TP.HMSCapScrnSpec['MEAN_HMSCap_REQUIRED'])
         objMsg.printMsg("MIN_HMSCap_REQUIRED = %.3f" % TP.HMSCapScrnSpec['MIN_HMSCap_REQUIRED'])
         objMsg.printMsg("StdDev_HMSCap_REQUIRED = %.3f" % TP.HMSCapScrnSpec['StdDev_HMSCap_REQUIRED'])

         # loop through table
         for row in pHMSTbl:
            listHMScap[int(row[colDict['HD_LGC_PSN']])].append(float(row[colDict['HMS_CAP']]))
         # loop through hd
         listMeanHMSbyHead = list()
         for hd in xrange(self.dut.imaxHead): 
            MinHMScap = min(listHMScap[hd])
            MeanHMScap = mean(listHMScap[hd])
            if testSwitch.FE_0368834_505898_P_MARGINAL_SOVA_HEAD_INSTABILITY_SCRN:
                listMeanHMSbyHead.append(round(MeanHMScap,3))
            StdDevHMScap = stDev_standard(listHMScap[hd])
            objMsg.printMsg("head: %d, listHMScap %s." % (hd, listHMScap[hd]))
            objMsg.printMsg("MeanHMScap = %.3f" % MeanHMScap)
            objMsg.printMsg("MinHMScap = %.3f" % MinHMScap)
            objMsg.printMsg("StdDevHMScap = %.3f" % StdDevHMScap)
            if MeanHMScap < TP.HMSCapScrnSpec['MEAN_HMSCap_REQUIRED'] and MinHMScap < TP.HMSCapScrnSpec['MIN_HMSCap_REQUIRED']:
               objMsg.printMsg("Hd %d fail HMS spec EC%d" % (hd, WkWrtEC+hd) )
               if not testSwitch.virtualRun and testSwitch.ENABLE_HMSCAP_SCREEN:
                  raiseException(48536, "HMS Capability Out Of Spec")
         if testSwitch.FE_0368834_505898_P_MARGINAL_SOVA_HEAD_INSTABILITY_SCRN:
            objMsg.printMsg("Save listMeanHMSbyHead = %s to HMSC_AVG" % str(listMeanHMSbyHead))
            self.dut.driveattr['HMSC_AVG'] = str(listMeanHMSbyHead)
      elif self.dut.currentState in ['VBAR_ZN_1D']:
         if not testSwitch.virtualRun and vbarResult != 0:
            raiseException(vbarResult, "ERROR: VBAR failure, exit")

#----------------------------------------------------------------------------------------------------------
class CDestrokeWaterfall(CWaterfallTest):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      objMsg.printMsg("CDestrokeWaterfall: Init ")
      self.dut = dut
      self.params = params
      CState.__init__(self, dut)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg('*'*100)
      objMsg.printMsg("DESTROKE WITH NEW RAP REQUESTED")
      objMsg.printMsg('*'*100)

      self.buildClusterList()
      for keyCounter, nibletString in self.VbarNibletCluster:
         if nibletString.find('320G') > -1:
            self.nibletString = nibletString
            self.keyCounter = keyCounter
            self.dut.Waterfall_Req = nibletString[3:5]
            break

      from PIF import nibletTable
      partNumNew = nibletTable[self.dut.partNum]['Part_num'][self.keyCounter]
      self.dut.partNum = partNumNew
      self.dut.driveattr['PART_NUM'] = self.dut.partNum

      if not testSwitch.FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ:
         from Setup import CSetup
         objSetup = CSetup()
         objSetup.buildFileList()  #update file list after update new partno
      else:
         self.dut.buildFileList()

      self.updateWTF()
      if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_VBAR_MSG:
         self.displayAttr()
      from OTF_Waterfall import WTFDisposition
      WTFDisposition(self.dut).run(WtfRequest =WTFDisposition.dispoEnum.DESTROKE)


#----------------------------------------------------------------------------------------------------------
class CDepopWaterfall(CWaterfallTest):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("CDepopWaterfallTest: Run ")
      self.dut.pn_backup = self.dut.driveattr['PART_NUM']
      self.buildClusterList()
      if testSwitch.virtualRun :return
      if not testSwitch.virtualRun and self.dut.depopMask != []:
         for hd in self.dut.depopMask:
             if hd in self.dut.LgcToPhysHdMap:
                objMsg.printMsg("Physical Heads: %s, Depop Mask %s" %(self.dut.LgcToPhysHdMap, self.dut.depopMask))
                raiseException(12150, "ERROR: DepopReq not fulfilled before VBAR")
      # call vbar from here

      for niblet in self.VbarNibletCluster:
         objMsg.printMsg("local vbar cluster: %s " % str(niblet))

      from VBAR import CNiblet
      from VBAR_LBA import CVBAR_LBA
      oVBAR_LBA = CVBAR_LBA()
      self.oFSO = CFSO()
      Index = 0
      nibletIndex = 0xFF      
      for niblet in TP.VbarNibletCluster:
         objMsg.printMsg(self.oFSO.oUtility.convertDictToPrintStr(niblet,'global vbar cluster',False,False))
         objMsg.printMsg("global vbar cluster: %s " %niblet)
         objMsg.printMsg("index: %d target_capacity: %d " %(Index,TP.VbarNibletCluster[Index]['DRIVE_CAPACITY']))
         self.objNiblet = CNiblet(niblet)
         #self.objPicker = CPicker(self.objNiblet,measAllZns,limits)
         #drive_capacity = float(self.objPicker.getCapacityFromDrive())
         drive_capacity = float(CVBAR().getCapacityFromDrive())
         objMsg.printMsg("drive_capacity %f" % ((drive_capacity)))
         objMsg.printMsg("target_capacity %d" % ((TP.VbarNibletCluster[Index]['DRIVE_CAPACITY'])))
         if drive_capacity > TP.VbarNibletCluster[Index]['DRIVE_CAPACITY']:
            #objTPIBPIPicker = CTPIBPIPicker()
            #objTPIBPIPicker.objNiblet = CNiblet(niblet)
            #niblet.settings['DRIVE_CAPACITY'] = TP.VbarNibletCluster[Index]['DRIVE_CAPACITY']
            oVBAR_LBA.setMaxLBA()
            nibletIndex = Index
            objMsg.printMsg("Found capacity match!!!!!!! nibletIndex: %d" % (nibletIndex))
            break
         Index = Index + 1


      if nibletIndex == 0xFF:
         objMsg.printMsg("No capacity match!!!!!!!")
         return 1
      self.keyCounter, self.nibletString = self.VbarNibletCluster[nibletIndex]
      #self.keyCounter = self.VbarNibletCluster[nibletIndex*2]
      #self.nibletString = self.VbarNibletCluster[(nibletIndex*2)+1]

      objMsg.printMsg("nibletIndex: %s" % (nibletIndex))
      objMsg.printMsg("keyCounter: %s  nibletString: %s" % (self.keyCounter, self.nibletString))

      #update partnumber and WTF attributes
      self.updateWTF()
      self.updateATTR(self.partNum,self.keyCounter)
      self.oFSO.setFamilyInfo(TP.familyInfo,TP.famUpdatePrm_178,self.dut.depopMask)
      return 0


#----------------------------------------------------------------------------------------------------------
class CVbarTuning(CState):
   """
      Description:
         VBAR (Variable Bit Aspect Ratio) Optimization Routines for head/zone write power settings
         and head bpi & tpi formats (for both single and multiple heads)
         This routine runs the iVBAR (integrated VBAR)
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oFSO = CFSO()
      self.oFSO.getZoneTable() # get number of heads and zones on drive

      if testSwitch.WA_0111716_007955_POWERCYCLE_AT_VBAR_START:
         from PowerControl import objPwrCtrl
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      # run ivbar routine now
      oVbar = CVBAR(self.params)
      nibletIndex, vbarResult = oVbar.run()  #vbarResult = EC
      oVbar = None # Allow Garbage Collection
      
      self.oFSO.getZoneTable(newTable = self.params.get('REFRESH_ZONE_TBL', True), delTables = 0, supressOutput = 0)
      if self.params.get('REFRESH_ZONE_TBL', False):
         from Servo import CServoFunc
         self.oSrvFunc = CServoFunc()
         self.dut.maxServoTrack = self.oSrvFunc.readServoSymbolTable(['maxServoTrack'], 
                                                                     TP.ReadPVDDataPrm_11, 
                                                                     TP.getServoSymbolPrm_11, 
                                                                     TP.getSymbolViaAddrPrm_11 )
         self.oSrvFunc = None # Allow Garbage Collection
      self.oFSO = None       

      return nibletIndex, vbarResult
