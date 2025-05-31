#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: SWD Tuning Module
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/09/29 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PCBA_Base.py $
# $Revision: #2 $
# $DateTime: 2016/09/29 22:58:46 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PCBA_Base.py#2 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
import re
from State import CState
import MessageHandler as objMsg
import traceback
from PowerControl import objPwrCtrl
import ScrCmds


#----------------------------------------------------------------------------------------------------------
class CCheckPCBA_SN(CState):
   """
      Class that will read PCBA_SN and compare against FIS attribute
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.pcba_sn = ''
      self.hda_serial_num = ''

      try:
         self.runme()
      except:
         from Rim import objRimType
         from Setup import CSetup
         mc_connected = CSetup().IsMCConnected()
         objMsg.printMsg("mc_connected=%s" % mc_connected)

         if testSwitch.WA_REMOVE_PCBA_SN_CHK_FRM_STATE_TABLE_DURING_EM_PHASE:
            objMsg.printMsg("Warning! PCBA_SN_CHK disabled during EM Phase. Traceback=%s" % (traceback.format_exc(),))
         elif (mc_connected or objRimType.IsPSTRRiser() or ConfigVars[CN].get('PRODUCTION_MODE',0)) and not testSwitch.virtualRun:
            objMsg.printMsg("PCBA SN mismatch with FIS attribute!!")

            name,attr_of_pwa = RequestService("GetAttributes", (self.pcba_sn,()))
            objMsg.printMsg("HostService(GetAttributes): %s" %(attr_of_pwa,))
            if attr_of_pwa.has_key('HDA_SERIAL'):
               actual_hda_sn = attr_of_pwa['HDA_SERIAL'].upper()[0:8]
               if len(self.hda_serial_num) == 0 and len(actual_hda_sn) == 8:
                  self.hda_serial_num = actual_hda_sn
                  
               if actual_hda_sn != self.hda_serial_num:
                  objMsg.printMsg('HDA SN from drive: %s != HDA SN from FIS: %s'%(self.hda_serial_num, actual_hda_sn))
            
            if len(self.hda_serial_num) > 0:
               self.dut.driveattr['MISMATCH'] = self.hda_serial_num
               RequestService("SetDriveSN", self.hda_serial_num)
               objMsg.printMsg("ReportErrorCode 11178 to drive %s"%self.hda_serial_num)
               ReportErrorCode(11178)
               RequestService('SendRun',(0,))
               RequestService("SetDriveSN", self.dut.serialnum)
               ScrCmds.raiseException(11178, "After SetDriveSN - Wrong PCBA serial number")
            else:
               raise
         else:
            objMsg.printMsg("Warning! Non-Neptune2 PCBA SN checking failed. Traceback=%s" % (traceback.format_exc(),))

   #-------------------------------------------------------------------------------------------------------
   def runme(self):
      if not DriveAttributes.has_key("PCBA_SERIAL_NUM"):
         ScrCmds.raiseException(11178, "FIS DriveAttributes has no PCBA_SERIAL_NUM key")

      self.pcba_sn = self.dut.objData.get('pcba_sn_boot', '')
      self.hda_serial_num = self.dut.objData.get('hda_sn_boot', '')
      
      if self.dut.objData.get('pcba_sn_boot', '0000') == DriveAttributes["PCBA_SERIAL_NUM"]:
         objMsg.printMsg("Boot PCBA SN match with FIS attribute")
         return
      elif self.dut.objData.get('pcba_sn_boot', '0000') == '' and int(DriveAttributes.get('PCBA_CYCLE_COUNT', 0)) > 1 and \
         self.dut.driveattr.get('AUTO_SEASERIAL', None) == 'PASS':  # Drive cannot get PCBA SN and already ran auto serial
         objMsg.printMsg("WARNING: Auto seaserial drive no pcba sn.")
         return
      elif (self.dut.objData.get('pcba_sn_boot', '0000') not in ['', '0000']) and self.dut.objData.get('pcba_sn_boot', '0000') != DriveAttributes["PCBA_SERIAL_NUM"]:
         ScrCmds.raiseException(11178, "DriveAttributes PCBA_SERIAL_NUM not matching drive PCBA SN")

      try:
         if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
            objMsg.printMsg("SF3 CCheckPCBA_SN")
            self.pcba_sn, self.hda_serial_num = self.read_pcba_sn_sf3()
         else:
            objMsg.printMsg("F3 CCheckPCBA_SN")
            self.pcba_sn, self.hda_serial_num = self.read_pcba_sn_f3()
      except:
         try:     # retry with power cycle
            objMsg.printMsg("First PCBA reading failed. Traceback=%s" % (traceback.format_exc(),))
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            self.pcba_sn, self.hda_serial_num = self.read_pcba_sn_sf3()
         except:
            objMsg.printMsg("Second PCBA reading failed. Traceback=%s" % (traceback.format_exc(),))
            objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

            try:
               self.pcba_sn, self.hda_serial_num = self.read_pcba_sn_f3()
            except:
               objMsg.printMsg("Third PCBA reading failed. Traceback=%s" % (traceback.format_exc(),))

               self.pcba_sn = ''
               self.hda_serial_num = ''
               from RawBootLoader import CFlashLoad
               ofls = CFlashLoad()

               bootfiles = getattr(TP, 'PCBA_SN_BOOT_FILES', [])
               for file in bootfiles:
                  try:
                     pcba_sn_boot, hda_sn_boot = ofls.GetBootPCBASN(file)
                     pcba_sn_boot = pcba_sn_boot.lstrip('0')                # trim string left 0 character
                     objMsg.printMsg("Read pcba_sn_boot = %s hda_sn_boot = %s" % (pcba_sn_boot, hda_sn_boot))

                     if len(pcba_sn_boot) > 0:
                        self.dut.objData.update({'pcba_sn_boot': pcba_sn_boot})
                        self.dut.objData.update({'hda_sn_boot': hda_sn_boot})
                        self.pcba_sn = pcba_sn_boot
                        self.hda_serial_num = hda_sn_boot
                        objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
                        break
                  except:
                     objMsg.printMsg("GetBootPCBASN failed: %s" % (traceback.format_exc(),))

      if self.pcba_sn == '':
         try:
            listfail = TP.SKIP_PCBA_SN_FAILCODE
         except:
            listfail = [10566,]

         OldFailcode = int(DriveAttributes.get('FAIL_CODE', '0'))
         OldFailstate = DriveAttributes.get('FAIL_STATE', '')
         OldFailstr = DriveAttributes.get('FAIL_STATE', '') + "_" + DriveAttributes.get('FAIL_CODE', '0')
         objMsg.printMsg("TP.SKIP_PCBA_SN_FAILCODE=%s OldFailcode=%s OldFailstate=%s OldFailstr=%s" % (listfail, OldFailcode, OldFailstate, OldFailstr))
      
         if OldFailcode in listfail or OldFailstate in listfail or OldFailstr in listfail:
            objMsg.printMsg("Skip PCBA SN check for previously fail drive")
            return
         ScrCmds.raiseException(11178, "Unable to read drive PCBA SN")

      if self.pcba_sn !=  DriveAttributes["PCBA_SERIAL_NUM"]:
         ScrCmds.raiseException(11178, "DriveAttributes PCBA_SERIAL_NUM not matching drive PCBA SN")

      self.dut.objData.update({'pcba_sn_boot': self.pcba_sn})  # Keep a copy in case power loss

   #-------------------------------------------------------------------------------------------------------
   def read_pcba_sn_f3(self):
      pcba_sn = ''
      hda_serial_num = ''
      import sptCmds
      sptCmds.enableDiags(retries = 1)
      res = sptCmds.sendDiagCmd('J,2', timeout = 10, printResult = True)

      Match = re.search('\s*PCBA Serial Number:*\s*(?P<PCBA_SN>[\.a-zA-Z0-9]{8,})', res)
      if Match:
         pcba_sn = Match.group('PCBA_SN')
         if len(pcba_sn) > 8:
            pcba_sn = pcba_sn[-8:].upper()
         objMsg.printMsg("Found F3 pcba_sn=%s" % pcba_sn)


      res = sptCmds.sendDiagCmd('J,1', timeout = 10, printResult = True)
      Match = re.search('\s*HDA Serial Number:*\s*(?P<HDA_SN>[\.a-zA-Z0-9\-]{8})', res)
      if Match:
         hda_serial_num = Match.group('HDA_SN').upper()
         objMsg.printMsg("Found F3 hda_serial_num=%s" % hda_serial_num)

      if len(pcba_sn) == 0:
         ScrCmds.raiseException(11178,"read_pcba_sn_f3 - unable to read PCBA_SERIAL_NUM")

      return pcba_sn, hda_serial_num

   #-------------------------------------------------------------------------------------------------------
   def read_pcba_sn_sf3(self):
      pcba_sn = ''
      hda_serial_num = ''

      tableNames = [i[0] for i in self.dut.dblData.Tables()]
      if 'P166_HDA_PCBA_INFO' not in tableNames:
         from Process import CProcess
         oProc = CProcess()
         oProc.St({'test_num':166, 'DblTablesToParse':['P166_HDA_PCBA_INFO']},CWORD1=(0x0800),timeout=30)
         tableInfo = self.dut.objSeq.SuprsDblObject['P166_HDA_PCBA_INFO'][0]
      else:
         tableInfo = self.dut.dblData.Tables('P166_HDA_PCBA_INFO').tableDataObj()[0]
      objMsg.printMsg("P166_HDA_PCBA_INFO tableInfo=%s" % tableInfo)

      
      tmp_sn = tableInfo.get("PCBA_SERIAL_NUM", "")
      if len(tmp_sn) > 8 and not "NOT_SET" in tmp_sn:
         pcba_sn = tmp_sn[-8:]
         hda_serial_num = tableInfo.get("HDA_SERIAL_NUM", "")
         objMsg.printMsg("Found SF3 pcba_sn=%s hda_serial_num=%s" % (pcba_sn, hda_serial_num))         

      if len(pcba_sn) == 0:
         ScrCmds.raiseException(11178,"read_pcba_sn_sf3 - unable to read PCBA_SERIAL_NUM")

      return pcba_sn, hda_serial_num
