#---------------------------------------------------------------------------------------------------------#
# Description: Serial Format Module
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/15 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Serial_SerFmt.py $
# $Revision: #6 $
# $DateTime: 2016/12/15 23:34:49 $
# $Author: weichen.lau $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Serial_SerFmt.py#6 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import re
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds

if testSwitch.FE_0151342_007955_P_CREATE_P_FMT_T250_RAW_ERROR_RATE_DELTA_TABLE:
   createdRawErrorRateDeltaTable = 0
   createTableOnSecondPass = 0


#----------------------------------------------------------------------------------------------------------
class CSerialFormat(CState):
   """
      Description: Class that will perform serial diagnostic user and system area format of drive.
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def __deltaERRScreen(self):
      try:
         data = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').tableDataObj()
      except:
         objMsg.printMsg('Attention!!! Table P_FORMAT_ZONE_ERROR_RATE is not found')
         return
      maxDeltaBitVsHead = 0
      maxDeltaBitVsOTF = 0
      for entry in data:
         if maxDeltaBitVsHead < abs(float(entry['BITS_READ_LOG10']) - float(entry['HARD_ERROR_RATE'])):
            maxDeltaBitVsHead = abs(float(entry['BITS_READ_LOG10']) - float(entry['HARD_ERROR_RATE']))
         if maxDeltaBitVsOTF < abs(float(entry['BITS_READ_LOG10']) - float(entry['OTF_ERROR_RATE'])):
            maxDeltaBitVsOTF = abs(float(entry['BITS_READ_LOG10']) - float(entry['OTF_ERROR_RATE']))
      if maxDeltaBitVsHead > 0.9:
         self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['QSFM_1'])
      if maxDeltaBitVsOTF > 1.2:
         self.dut.driveattr['PROC_CTRL30'] = '0X%X' % (int(self.dut.driveattr.get('PROC_CTRL30', '0'),16) | TP.Proc_Ctrl30_Def['QSFM_2'])
   #-------------------------------------------------------------------------------------------------------   
   def __OTFScreen(self):
      from MathLib import mean
      data = []
      OTF_list = {}
      try:
         data = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').tableDataObj()

      except:
         objMsg.printMsg('Attention!!! Table P_FORMAT_ZONE_ERROR_RATE is not found')
         return True

      for entry in data:
         OTF_list.setdefault(entry['HD_LGC_PSN'], []).append(float(entry['OTF_ERROR_RATE']))
      for hd in OTF_list:
         avg_OTF = mean(OTF_list[hd])
         if avg_OTF < 7.4 and not (testSwitch.IS_2D_DRV == 0 and self.dut.BG in ['SBS']):
            ScrCmds.raiseException(14651,"Head Avg OTF_ERROR_RATE < 7.4")
         if avg_OTF < 8.2 and (self.dut.partNum[-3:] not in TP.RetailTabList):
            ScrCmds.raiseException(42170,"Head Avg OTF_ERROR_RATE < 8.2 and downgrade")

      #for entry in data:
      #   if float(entry['OTF_ERROR_RATE']) <= 7.0 or float(entry['RAW_ERROR_RATE']) < 4.0:
      #      objMsg.printMsg('Warning!!! Detect OTF_ERROR_RATE or RAW_ERROR_RATE is out of spec!')
      #      objMsg.printMsg('OTF_ERROR_RATE is %s, RAW_ERROR_RATE is %s' % (str(entry['OTF_ERROR_RATE']), str(entry['RAW_ERROR_RATE'])))
      #      return False
      return True
   
   #-------------------------------------------------------------------------------------------------------
   if testSwitch.FE_0137099_220554_P_OTF_DELTA_SCRN_IN_FMT:
      def __deltaOTFScreen(self):

         data = []
         otf = []
         otf_head = []

         try:
            data = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').tableDataObj()
         except:
            objMsg.printMsg('Attention!!! Table P_FORMAT_ZONE_ERROR_RATE is not found')
            return True

         # loop on table entries to create a 2D list head_otf with head and otf for each zone
         for entry in data:
            otf.append([entry['HD_PHYS_PSN'],float(entry['OTF_ERROR_RATE'])])

         index = 0               # reset counter

         # loop on all heads and calculate the min, max and delta OTF for each head
         for head in xrange(self.dut.imaxHead):
            otf_head = list(otf[index:(self.dut.numZones + index)])
            maxotf = max(otf_head)[1]
            minotf = min(otf_head)[1]
            deltaotf = maxotf - minotf
            index = index + self.dut.numZones
            self.dut.dblData.Tables('P_DELTA_OTF_2').addRecord(
               {
               'SPC_ID':               self.dut.objSeq.curRegSPCID,
               'OCCURRENCE':           self.dut.objSeq.getOccurrence(),
               'SEQ':                  self.dut.objSeq.curSeq,
               'TEST_SEQ_EVENT':       self.dut.objSeq.getTestSeqEvent(0),
               'HD_PHYS_PSN':          head,
               'DELTA_OTF':            deltaotf
               })

         return True

   #-------------------------------------------------------------------------------------------------------
   if testSwitch.FE_0145405_426568_P_ENC_WR_SCRN_VS_RE_FORMAT_RAW_DELTA:
      def __deltaErrRateTable(self, base_spc_id, new_spc_id ):
         """
            Description: Generate table P_DELTA_ERROR_RATE
               - Populate with P_FORMAT_ZONE_ERROR_RATE data between 2 measurements
               - SPC_ID for current format is used as current measurement
               - ErrRateDeltaTable contains SPC_ID of measurement to compare against
         """

         try:
            fmtBERdata = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').tableDataObj()
         except:
            objMsg.printMsg('Attention!!! Table P_FORMAT_ZONE_ERROR_RATE is not found')
            return

         seq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

         fmtBERdata = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').tableDataObj()
         zoneList = ()
         baseBERdata = {}
         for item in fmtBERdata:
            if int(item['SPC_ID']) == base_spc_id:
               if not baseBERdata.has_key(item['HD_PHYS_PSN']):
                  baseBERdata[item['HD_PHYS_PSN']] = {}
               baseBERdata[item['HD_PHYS_PSN']][item['DATA_ZONE']] = item
               if item['DATA_ZONE'] not in zoneList:
                  zoneList += (item['DATA_ZONE'],)


         for item in fmtBERdata:
            if int(item['SPC_ID']) == new_spc_id:
               if baseBERdata.has_key(item['HD_PHYS_PSN']) and baseBERdata[item['HD_PHYS_PSN']].has_key(item['DATA_ZONE']):
                  self.dut.dblData.Tables('P_DELTA_ERROR_RATE').addRecord(
                     {
                     'SPC_ID'                      : new_spc_id,
                     'OCCURRENCE'                  : occurrence,
                     'SEQ'                         : seq,
                     'TEST_SEQ_EVENT'              : testSeqEvent,
                     'HD_PHYS_PSN'                 : item['HD_PHYS_PSN'],
                     'HD_LGC_PSN'                  : item['HD_LGC_PSN'],
                     'DATA_ZONE'                   : item['DATA_ZONE'],
                     'BITS_READ_LOG10'             : item['BITS_READ_LOG10'],
                     'HARD_ERROR_RATE'             : item['HARD_ERROR_RATE'],
                     'HARD_ERROR_DELTA'            : float(baseBERdata[item['HD_PHYS_PSN']][item['DATA_ZONE']]['HARD_ERROR_RATE']) - float(item['HARD_ERROR_RATE']),
                     'OTF_ERROR_RATE'              : item['OTF_ERROR_RATE'],
                     'OTF_ERROR_DELTA'             : float(baseBERdata[item['HD_PHYS_PSN']][item['DATA_ZONE']]['OTF_ERROR_RATE']) - float(item['OTF_ERROR_RATE']),
                     'RAW_ERROR_RATE'              : item['RAW_ERROR_RATE'],
                     'RAW_ERROR_DELTA'             : float(baseBERdata[item['HD_PHYS_PSN']][item['DATA_ZONE']]['RAW_ERROR_RATE']) - float(item['RAW_ERROR_RATE']),
                     })

         objMsg.printDblogBin(self.dut.dblData.Tables('P_DELTA_ERROR_RATE'))
         return

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      '''
      FormatOptions applied in CSerialFormat():
         formatType            (Default = '')   : Type of format being performed - for reporting purposes only
         forceFormat           (Default = 0)    : Perform format regardless of conditions
         noPowerCycle          (Default = 0)    : Disable powerCycles before / after serial format
         msdScreens            (Default = [])   : msd screens to perform (options: 1, 2)
         dumpDefectLists       (Default = 0)    : Display defect lists prior to format
         skipGListCheck        (Default = 0)    : Skip the initial G-List check and merge
         otfScreen             (Default = 0)    : Perform format if __OTFScreen() indicates
         nonResidentFlawLimit  (Default = None) : Apply check of non-resident flaw list, raise exception of limit exceeded
                                                ( NOTE: Non-resident flaws following format with ReFormat are already in slip list)
         collectBERdata        (Default = 1)    : Collect and report BER data from format operation

      (NOTE: Additional FormatOptions are passed directly to formatUserPartition())
      '''

      from serialScreen import sptDiagCmds
      import sptCmds
      from CodeVer import theCodeVersion

      FormatOptions = eval(self.params['FORMAT_OPTIONS'])

      if FormatOptions.get('otfScreen', 0) and self.__OTFScreen() and not getattr(TP, 'bgSTD',0):
         return

      if self.dut.nextOper is 'FIN2':
         FormatOptions['noPowerCycle'] = 1   # for 3-tier FIN2 TCG serial format
      else:
         theCodeVersion.ChkUSB()
         if self.dut.driveattr['USB_INTF'] == 'Y':
            self.dut.driveattr['USB_DRIVE'] = "USB"
         else:
            self.dut.driveattr['USB_DRIVE'] = "NONUSB"

      if not FormatOptions.get('noPowerCycle',0):
         objPwrCtrl.powerCycle(useESlip=1)
      oSerial = sptDiagCmds()
      sptCmds.enableDiags()
      if FormatOptions.get('quickDFSformat', 0):
         sptCmds.sendDiagCmd('m0,6,2,,,,,22',timeout = 600, printResult = True)

      if FormatOptions.get('Init_MediaCache', 0):
         objMsg.printMsg("Initialize Media Cache table")
         oSerial.initMCCache()
         sptCmds.gotoLevel('T')

      # Disable shock sensor before Serial format
      if testSwitch.FE_0111141_007955_SERIAL_FMT_SET_SHOCK_SENSOR:
         try:
            ShockSensorString = getattr(TP, 'DisableShockSensor')
            oSerial.EnableDisableShockSensor(ShockSensorString)
         except:
            pass
      if testSwitch.FE_0120498_231166_DISABLE_SWD_IN_FORMAT:
         oSerial.disableSWD()

      if testSwitch.FORCE_LOWER_BAUD_RATE:
         oSerial.syncBaudRate(Baud38400)

      if FormatOptions.get('dumpDefectLists', 0):
         oSerial.dumpNonResidentGList()
         oSerial.dumpReassignedSectorList()

      if not FormatOptions.get('skipGListCheck', 0):
         formatNeeded = oSerial.CheckNumEntriesInGList()
         if testSwitch.BF_0136108_231166_P_INCL_ASFT_IN_FORMAT_REQ:
            asftCount = oSerial.dumpActiveServoFlaws()
            formatNeeded += asftCount['Total Entries']
         if self.dut.powerLossEvent and self.dut.objData.get('SFT',0):  # Check Serial Format Marker if PLR
            formatNeeded = 0xFFFF                                        # Force format if power hit during format occured
      else:
         formatNeeded = 0xFFFF

      DoneSkipZone = 0
      agbUsed_SMR = False
      if testSwitch.SKIPZONE and not testSwitch.virtualRun:
         DoneSkipZone = oSerial.skipZone()

      ############ Display zone table for debug purposes
      if not testSwitch.REDUCE_LOG_SIZE:
         # Display zone table using 2>x cmd for FA purposes
         objMsg.printMsg("Display zntbl using 2>x cmd")
         oSerial.syncBaudRate(Baud38400)        # lower baudrate to prevent any data loss
         sptCmds.gotoLevel('2')
         sptCmds.sendDiagCmd('x',timeout = 1000, printResult = True)
         objPwrCtrl.powerCycle(useESlip=1)
         sptCmds.enableDiags()
         sptCmds.gotoLevel('T')
      
      if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
         sptCmds.gotoLevel('T')
         CMD = 'm0,406,2,,,,,22'
         result = sptCmds.sendDiagCmd(CMD, timeout = 1000)
         objMsg.printMsg  ("\nQuick Format for SMR gap calculation %s\n%s" % (CMD,result))
         
      ############ Performing quick format when AGB is enabled ####################
      if testSwitch.ADAPTIVE_GUARD_BAND and not testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
         sptCmds.gotoLevel('T')
         # m0,106,2 : Reset guard band.
         # m0,106,3 : Keep old guard band.
         if (testSwitch.SKIPZONE and DoneSkipZone == 1):
            CMD = 'm0,106,3,,,,,22' # quick format command for zone remap and guard band setting.
         else:
            CMD = 'm0,106,2,,,,,22'

         result = sptCmds.sendDiagCmd(CMD, timeout = 1000)
         objMsg.printMsg  ("\nQuick Format %s\n%s" % (CMD,result))
         
         ### check AGB used ###
         if testSwitch.SMR and (re.search("Whole zone 0 is allocated as guard band", result) == None):
            objMsg.printMsg("AGB used")
            agbUsed_SMR = True
         
         startTrkDataPat = "Start Track"
         startTrkData={}
         startTrkData['HD_PHYS_PSN']=[]
         startTrkData['START_TRACK']=[]
         for line in result.splitlines():
            #objMsg.printMsg  ("line: %s" % line)
            match = re.search(startTrkDataPat, line)
            #objMsg.printMsg  ("match.group0: %s" % match.group(0))
            if match:
               hd_data = line.split()[1]
               startTrkData['HD_PHYS_PSN'].append(int(hd_data))
               trk_dec = int(line.split()[7], 16)
               startTrkData['START_TRACK'].append(trk_dec)
            #else:
               #objMsg.printMsg  ("\nNo Start Track found. Next Line.")
         objMsg.printMsg  ("startTrkData: %s" % startTrkData)
         #startTrkData: {'HD_PHYS_PSN': [0, 1], 'START_TRACK': [3075, 3120]}

         if(len(startTrkData['HD_PHYS_PSN'])>0):
             # Dblog Implementation
             try:
                self.dut.dblData.delTable('P_AGB_STARTTRACK', forceDeleteDblTable = 1)
             except:
                pass
             try:
                for i in range(len(startTrkData['HD_PHYS_PSN'])):
                   self.dut.dblData.Tables('P_AGB_STARTTRACK').addRecord({
                            'SPC_ID'              : self.dut.objSeq.curRegSPCID,
                            'OCCURRENCE'          : self.dut.objSeq.getOccurrence(),
                            'SEQ'                 : self.dut.objSeq.curSeq,
                            'TEST_SEQ_EVENT'      : self.dut.objSeq.getTestSeqEvent(0),
                            'HD_PHYS_PSN'         : int(startTrkData['HD_PHYS_PSN'][i]),  # hd
                            'START_TRACK'         : int(startTrkData['START_TRACK'][i]),   # Start track
                            })

                objMsg.printDblogBin(self.dut.dblData.Tables('P_AGB_STARTTRACK'),spcId32 = self.dut.objSeq.curRegSPCID)
             except:
                pass

         if( testSwitch.TRUNK_BRINGUP ):
               #objPwrCtrl.powerCycle(useESlip=1)
               #oSerial = sptDiagCmds()
               #sptCmds.enableDiags()

               sptCmds.gotoLevel('C')
               # C>U8 to initialize media chche
               result = sptCmds.sendDiagCmd('U8', timeout = 3000)
               objMsg.printMsg  ("\nInitialize media chech table %s\n%s" % (CMD,result))

         if( testSwitch.ROSEWOOD7 ):
               objPwrCtrl.powerCycle(useESlip=1)
               sptCmds.enableDiags()
               sptCmds.gotoLevel('T')
               CMD = 'm0,106,2,,,,,22'
               result = sptCmds.sendDiagCmd(CMD, timeout = 1000)
               objMsg.printMsg("\nSecond Quick Format %s\n%s" % (CMD, result))


      if formatNeeded or FormatOptions.get('forceFormat', 0):
         # 'Screen2' : Change SMTRESH detect SM errors in Serial Format more aggressively
         if 'Screen2' in FormatOptions.get('msdScreens', []):
            oSerial.mediaSyncDefectScreen2()
         # 'Screen1' : Changes Phase Update Gain slower to detect MSD type defects during format
         if 'Screen1' in FormatOptions.get('msdScreens', []):
            oSerial.mediaSyncDefectScreen()

         if (formatNeeded != 0xFFFF) and (formatNeeded != 0):   # Run the G->P list merge if needed only
            oSerial.mergeG_to_P()

         if testSwitch.FE_305538_P_ENABLE_CTF_IN_SERIAL_FORMAT or self.dut.BG in ['SBS']: # enable CTF during serial format
            sptCmds.gotoLevel('7')
            result = sptCmds.sendDiagCmd('t1,4D', timeout = 300)
            objMsg.printMsg('Read channel register 4D:\n%s' % (result))
            result = sptCmds.sendDiagCmd('s1,4D,C088', timeout = 300)
            objMsg.printMsg('Program bit 7-4 of channel register to 8:\n%s' % (result))
            result = sptCmds.sendDiagCmd('t1,4D', timeout = 300)
            objMsg.printMsg('Read channel register 4D:\n%s' % (result))

         if testSwitch.FE_305538_P_CHANGE_OCLIM_IN_SERIAL_FORMAT: # tighten OCLIM during serial format
            sptCmds.gotoLevel('5')
            for hd in xrange(self.dut.imaxHead):
               CMD = 'w2A,,%X,%d' % (TP.SerFmt_OCLIM, hd * 2)
               result = sptCmds.sendDiagCmd(CMD, timeout = 300)
               objMsg.printMsg('Program Hd%d OCLIM to %d%%:\n%s' % (hd, (TP.SerFmt_OCLIM/4096.0*100), result))
               CMD = 'r2A,,%d' % (hd * 2)
               result = sptCmds.sendDiagCmd(CMD, timeout = 300)
               objMsg.printMsg('Read Hd%d OCLIM:\n%s' % (hd, result))

         objMsg.printMsg('*****Issuing %s *****' %FormatOptions.get('formatType', ''))
         self.dut.objData['SFT'] = 1         # Set Serial Format Marker for PLR handling
         if FormatOptions.get('ifFailDoDisplayG', 0):
            try:
               oSerial.formatUserPartition(FormatOptions)
            except:
               if testSwitch.BF_0163420_231166_P_UTILIZE_SERIAL_CMD_FOR_SERIAL_FMT_G_LIST:
                  oSerial.dumpNonResidentGList()
               else:
                  from base_IntfTest import CDisplay_G_list
                  CDisplay_G_list(self.dut, params = {}).run()
               raise
         else:
            oSerial.formatUserPartition(FormatOptions)

         if testSwitch.FE_305538_P_ENABLE_CTF_IN_SERIAL_FORMAT or testSwitch.FE_305538_P_CHANGE_OCLIM_IN_SERIAL_FORMAT or self.dut.BG in ['SBS']: # power cycle to restore back original settings
            objPwrCtrl.powerCycle(useESlip=1)
            sptCmds.enableDiags()

            if testSwitch.FE_305538_P_ENABLE_CTF_IN_SERIAL_FORMAT or self.dut.BG in ['SBS']: # enable CTF during serial format
               sptCmds.gotoLevel('7')
               result = sptCmds.sendDiagCmd('t1,4D', timeout = 300)
               objMsg.printMsg('Read channel register 4D:\n%s' % (result))

            if testSwitch.FE_305538_P_CHANGE_OCLIM_IN_SERIAL_FORMAT: # tighten OCLIM during serial format
               sptCmds.gotoLevel('5')
               for hd in xrange(self.dut.imaxHead):
                  CMD = 'r2A,,%d' % (hd * 2)
                  result = sptCmds.sendDiagCmd(CMD, timeout = 300)
                  objMsg.printMsg('Read Hd%d OCLIM:\n%s' % (hd, result))

         self.dut.objData['SFT'] = 0         # Clear Serial Format Marker
         gListEntries = oSerial.CheckNumEntriesInGList()
         if (FormatOptions.get('nonResidentFlawLimit', None) != None) and (gListEntries > FormatOptions['nonResidentFlawLimit']) and not testSwitch.virtualRun:
            ScrCmds.raiseException(10049, "G-list count of %s exceeds the limit of %s" % (gListEntries, reformatLimit))

      else:
         objMsg.printMsg('*****Bypassing %s - Conditions not met*****' %FormatOptions.get('formatType', ''))

      if testSwitch.FE_0120498_231166_DISABLE_SWD_IN_FORMAT:
         oSerial.enableSWD()
      # Re-Enable shock sensor After Serial format
      if testSwitch.FE_0111141_007955_SERIAL_FMT_SET_SHOCK_SENSOR:
         try:
            ShockSensorString = getattr(TP, 'EnableShockSensor')
            oSerial.EnableDisableShockSensor(ShockSensorString)
         except:
            pass
      if self.dut.nextOper == "FNC2":
         if oSerial.BGMS_EnabledInCode():
            oSerial.changeAMPS("BGMS_ENABLE", 0, mask = 1)
            oSerial.changeAMPS("BGMS_PRESCAN", 0, mask = 1)
      if not FormatOptions.get('noPowerCycle',0) or testSwitch.FORCE_LOWER_BAUD_RATE or FormatOptions.get('msdScreens', []) != []:
         objPwrCtrl.powerCycle(useESlip=1)

      if testSwitch.FE_0137099_220554_P_OTF_DELTA_SCRN_IN_FMT:
         self.__deltaOTFScreen()
      if self.params.get('DUMP_P_LIST', False):
         from MediaScan import CUserFlaw
         self.objFs = CUserFlaw()
         self.objFs.repPList() # dump p-list to host (result file)
      if FormatOptions.get('ErrRateDeltaSpcId', None):
         self.__deltaErrRateTable(FormatOptions.get('ErrRateDeltaSpcId'),FormatOptions.get('spc_id'))


      if testSwitch.FE_0151342_007955_P_CREATE_P_FMT_T250_RAW_ERROR_RATE_DELTA_TABLE:

         global createdRawErrorRateDeltaTable
         global createTableOnSecondPass

         if createTableOnSecondPass:
            createRawErrorRateDeltaTable = 1
         else:
            if formatNeeded != 0:
               createTableOnSecondPass = 1

            if createTableOnSecondPass == 0 and createdRawErrorRateDeltaTable == 0:
               createRawErrorRateDeltaTable = 1
            else:
               createRawErrorRateDeltaTable = 0

         if not testSwitch.virtualRun and createRawErrorRateDeltaTable:

            try:
               fmtData = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').tableDataObj()
               P250_tbl = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
            except:
               objMsg.printMsg('!!! Tables P_FORMAT_ZONE_ERROR_RATE, P250_ERROR_RATE_BY_ZONE - not found')

            curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

            maxSeq = 0
            for record in range(len(fmtData)):
               if int(fmtData[record]['SEQ']) > maxSeq:
                  maxSeq = int(fmtData[record]['SEQ'])

            T250Record = -1

            for record in range(len(fmtData)): #maybe typecast values into int
               try:
                  if ( int(fmtData[record]['SEQ']) == maxSeq and int(fmtData[record]['SPC_ID']) == 1):
                     T250Record += 1
                     if int(P250_tbl[T250Record]['SPC_ID']) == 1:
                        fmtRawErrorRate = float(fmtData[record]['RAW_ERROR_RATE'])
                        T250RawErrorRate = float(P250_tbl[T250Record]['RAW_ERROR_RATE'])
                        absT250RawErrorRate = abs(T250RawErrorRate)
                        rawErrRateDelta = absT250RawErrorRate - fmtRawErrorRate

                        self.dut.dblData.Tables('P_FMT_T250_RAW_ERROR_RATE_DELTA').addRecord(
                           {
                              'SPC_ID': -1,
                              'OCCURRENCE' : occurrence,
                              'SEQ' : curSeq,
                              'TEST_SEQ_EVENT' : testSeqEvent,
                              'HD_PHYS_PSN' : self.dut.LgcToPhysHdMap[int(fmtData[record]['HD_PHYS_PSN'])],
                              'HD_LGC_PSN' : int(fmtData[record]['HD_PHYS_PSN']),
                              'DATA_ZONE' : int(fmtData[record]['DATA_ZONE']),
                              'T250_RAW_ERROR_RATE' : T250RawErrorRate,
                              'FMT_RAW_ERROR_RATE'  : fmtRawErrorRate,
                              'RAW_ERROR_RATE_DELTA': rawErrRateDelta,
                           })
               except:
                  pass
            objMsg.printDblogBin(self.dut.dblData.Tables('P_FMT_T250_RAW_ERROR_RATE_DELTA'))
            createdRawErrorRateDeltaTable = 1
      if testSwitch.FE_0156020_231166_P_UPLOAD_USER_SLIP_LIST_TBL:
         sptCmds.enableDiags()
         oSerial.dumpUseSlipList()

      if testSwitch.FE_0128912_7955_CREATE_FORMAT_ZONE_ERROR_RATE_EXT_TABLE and not testSwitch.virtualRun:
         fmtZoneErrorRate = self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE').tableDataObj()
         curSeq,occurrence,testSeqEvent = self.dut.objSeq.registerCurrentTest(0)

         for record in range(len(fmtZoneErrorRate)): #maybe typecast values into int
            if int(fmtZoneErrorRate[record]['ECC_LEVEL']) == TP.reformatOptions['TLevel']:            # 2nd pass only
               bitsReadLog10 = float(fmtZoneErrorRate[record]['BITS_READ_LOG10'])
               hardErrorRate = float(fmtZoneErrorRate[record]['HARD_ERROR_RATE'])
               bitsRdLog10MinusHrdErrRate = bitsReadLog10 - hardErrorRate

               self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE_EXT').addRecord(
                  {
                     'SPC_ID': -1,
                     'OCCURRENCE' : occurrence,
                     'SEQ' : curSeq,
                     'TEST_SEQ_EVENT' : testSeqEvent,
                     'HD_PHYS_PSN' : self.dut.LgcToPhysHdMap[int(fmtZoneErrorRate[record]['HD_PHYS_PSN'])],
                     'HD_LGC_PSN' : int(fmtZoneErrorRate[record]['HD_PHYS_PSN']),
                     'DATA_ZONE' : int(fmtZoneErrorRate[record]['DATA_ZONE']),
                     'BITSRDLOG10_MINUS_HARDERRRATE': bitsRdLog10MinusHrdErrRate,
                  })
         objMsg.printDblogBin(self.dut.dblData.Tables('P_FORMAT_ZONE_ERROR_RATE_EXT'))

      if testSwitch.ANGSANAH:
         if oSerial.GetZoneRemapStatus(getCTRL_L = True):
            objMsg.printMsg('Zone Remap Detected')
            #ScrCmds.raiseException(48463,"Downgrade on Zone Remap")

      theCodeVersion.updateCodeRevisions()
            
      if testSwitch.ENABLE_DOWNGRADE_ON_ZONE_REMAP and (self.dut.partNum[-3:] not in TP.RetailTabList):
         if ( oSerial.GetZoneRemapStatus(getCTRL_L = True) and not testSwitch.SMR )or agbUsed_SMR:
            objMsg.printMsg('Downgrade on Zone Remap Required')
            ScrCmds.raiseException(48463,"Downgrade on Zone Remap")

      if testSwitch.YARRAR:
         self.__OTFScreen()
      if testSwitch.IS_2D_DRV == 0 and self.dut.BG in ['SBS'] and ConfigVars[CN].get('FormatWWriteOnly', 1) == 0:
         self.__deltaERRScreen()
