#-------------------------------------------------------------------------------
# Property of Seagate Technology, Copyright 2006, All rights reserved
#-------------------------------------------------------------------------------
# Description: This is a CCA_CCV (Critical Customer Attribute) CCV process.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CCA_CCV.py $
# $Revision: #1 $
# $Change: 1047653 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CCA_CCV.py#1 $
# Level: 1
#-------------------------------------------------------------------------------

# STOP HALT STOP HALT STOP HALT STOP HALT STOP HALT STOP HALT STOP HALT
#         SSS         TTTTTTTTTTT             OOO          PPPPPP
#      SS     SS          TT               OO     OO       PP    PPP
#     SS                  TT             OO         OO     PP       PP
#      SS                 TT             OO         OO     PP    PPP
#        SSS              TT             OO         OO     PPPPPP
#            SS           TT             OO         OO     PP
#              SS         TT             OO         OO     PP
#     SS     SS           TT               OO     OO       PP
#        SSS              TT                  OOO          PP
# STOP HALT STOP HALT STOP HALT STOP HALT STOP HALT STOP HALT STOP HALT
# STOP HALT STOP HSTAD HALT FERMA STOP ALTO HALT STANNA STOP HALT STOP

# Please DO NOT make any changes to this file.  All changes need to go through
# the commonality team responsible for this process.

################################################################################
versionHistory = {
   '1.0' :  ['11/28/2011','Initial release for CCA_CCV'],
   '2.0' :  ['01/04/2012','First official release to mass production'],
   '2.01':  ['01/20/2012','SED testing improvements, CFG now used for Fujitsu',
            'Minimum initiator rev IR.413515 required for new SED tests'],
   '2.02':  ['02/10/2012','Minor Changes:  Clear_EWLM allow 0000 or 0001 value',
            'ResetRecovery allow for 0000 or 005E response',
            'Remove unnecessary displays of SED ports in SEDUnlockDiagUDS'],
   '2.03':  ['03/02/2012','Add SD_LA2 for higher capacity Hitatchi LA check',
            'Change import CustomCfg_Share.py to CCABuildCfg.py',
            'Add TIME To Ready Testing',
            'Handle final Seatrack setting of ZERO_PRTN_RQMT',
            'Replace most DriveAttributes[ with self.dut.driveattr[',
            'Remove unused import of comMode and IO_TestParameters',
            'Add 2nd USD clear before SMART Clear to sync up',
            'Create self.WR_powerCycle() to hanlde LCO/TCO differences'],
   '2.10':  ['07/13/2012','Reorder the authentication basics in',
            'handlersandAuthenticate so that ISE drive will run.',
            'Replace conditional D_SENSE after T537 with always run',
            'Add pull of initiator rev value - used for conditional checks'
            'Add SOM check and ISE verify - initiator rev minimum 439877',
            'Add T529 max_head option on servo check for LCO products',
            'Add DELLA SED support to SetSSC and MakerSymK'],
   '2.12':  ['07/26/2012','Add Fujitsu Config Code CAP method for Della'],
}

from Test_Switches import testSwitch
from Constants import *
import ScrCmds
from State import CState
from Drive import objDut
import MessageHandler as objMsg

from Process import CProcess
oProc = CProcess()
import CCACCV_TestParameters as IO_TP
from PowerControl import objPwrCtrl

from CCABuildCfg import CCustomCfg, buildTestCCADict, updateCUST_TESTNAME

if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:
   from TestParamExtractor import TP

CustConfig = CCustomCfg()


historyRev = max(versionHistory.keys())
objMsg.printMsg('%s CCA_CCV.py %s %s %s' % ('-'*20,historyRev,versionHistory[historyRev][0], "-" * 20))
for value in versionHistory[historyRev][1:]:
   objMsg.printMsg(value)
objMsg.printMsg('')


################################################################################
class Cust_Verify(CState):
   def __init__(self, dut, params=[]):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   def run(self):

      import string

      if testSwitch.virtualRun:
         objMsg.printMsg("**WARNING**WARNING**WARNING**" * 5)
         objMsg.printMsg("VIRTFLAG SET - Virtual run          " * 4)
         objMsg.printMsg("**WARNING**WARNING**WARNING**" * 5)

      self.FW_PLATFORM_FAM = 'CANNON'
      if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:
         self.FW_PLATFORM_FAM = getattr(TP,"prm_TCG",{}).get('FW_PLATFORM', 'CANNON')

      buildTestCCADict()
      if not testSwitch.virtualRun:
         self.WR_powerCycle()
      oProc.St(IO_TP.prm_535_DrivevarInitiatorRev,TEST_FUNCTION=(0x8800,))	# Get Initiator Code Rev with store as DriveVars["Initiator Code"]
      self.initchglistno = string.split(DriveVars.get("Initiator Code",'1-1'),'-')[1]
      objMsg.printMsg("Initiator Change List Number:  %s"%self.initchglistno)

      self.SpinUp()
      self.CCV_commonstart()
      self.verifyWWN()
      self.set_verifyLifeState()
      self.set_verifySEDTables()
      self.set_verifyCust_TestName()
      self.getModelNumber()
      self.verifySerialNumber()
      self.set_verifyModeSense()
      self.verifyDataPattern()
      self.CCV_commonend()

      CustConfig.ProcessCustomAttributeRequirements()
      if not testSwitch.virtualRun:
         objMsg.printMsg("="*80)
         objMsg.printMsg("Part Number:  %s"%objDut.partNum)
         objMsg.printMsg("PROD_REV:  %s        SERVO_CODE:  %s"%(DriveVars["PROD_REV"], DriveVars["SERVO_CODE"][-4:]))
         objMsg.printMsg("Serial Number:  %s"%HDASerialNumber)
         objMsg.printMsg("*"*80)
      objMsg.printMsg("%s"%objDut.DCMCCA_overwrite)
      objMsg.printMsg("* * * CCA_CCV testing completed * * *")

      if testSwitch.virtualRun:
         objMsg.printMsg("**WARNING**WARNING**WARNING**" * 5)
         objMsg.printMsg("VIRTFLAG SET - Virtual run          " * 4)
         objMsg.printMsg("**WARNING**WARNING**WARNING**" * 5)

      if objDut.Eng_Bypass == 'ENG_EVAL_BYPASS':
         objMsg.printMsg("*"*80)
         objMsg.printMsg("\nWARNING:  ENG_EVAL_BYPASS:  USER_LBA_COUNT testing is bypassed.\n")
         objMsg.printMsg("*"*80)


   def CCV_commonstart(self):
      '''This function contains scripts for a common starting process that all customers use.
      This testing includes:
      1.  FC Port Bypass Check
      2.  Standard Inquiry (Test 514) display and C0 VPD Inquiry Display
      3.  Display SAV, DEF and CHG Mode sense
      4.  Verify 0 growth defects and 0 servo defects
      5.  Clear SMART and UDS, Power OFF/ON then Verify UDS Power cycle counter is less than 2
      6.  Clear EWLM (Enhanced Workload Management Log)
      7.  512 single LBA Random Read only
      8.  Send/Receive Diagnostics
      9.  Reset Recovery response
      9.  ETFLOG data check
      10. Secondary Flash Container Check for products that Kahu or Kahu+ chips
      11. TIME TO READY Test
      '''

      testHeader("Common Start Process")
      if testSwitch.virtualRun:
         return
      self.PortBypassCheck()
      oProc.St(IO_TP.prm_514_StdInquiryData)  # Std Inquiry Data
      oProc.St(IO_TP.prm_514_FwServoInfo)  # Vital Data
      oProc.St(IO_TP.prm_518_DisplayCurrentMps)  # Display Modepages
      oProc.St(IO_TP.prm_518_DisplayChangeableMps)  # Changeable Modepages
      oProc.St(IO_TP.prm_518_DisplayDefaultMps)  # Default Modepages
      oProc.St(IO_TP.prm_518_DisplaySavedMps)  # Display SAV Mode Sense
      oProc.St(IO_TP.prm_529_CheckGrowthDefects)  # Verify 0 growth defects before starting testing
      if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:
         oProc.St(IO_TP.prm_529_CheckServoDefects, MAX_HEAD = getattr(TP, 'prod_max_head', 0))  # Verify 0 servo defects before starting testing
      else:
         oProc.St(IO_TP.prm_529_CheckServoDefects)  # Verify 0 servo defects before starting testing
      self.Clear_SMARTandUDS()
      self.Clear_EWLM()
      oProc.St(IO_TP.prm_510_RandomRead,{'prm_name':'512 Single LBA Random Read'},NUMBER_LBA_PER_XFER=(0x0000,0x0001,),	TOTAL_LBA_TO_XFER=(0x0000,0x0000,0x0000,0x0200,))
      self.SendSelfTestDiag()
      self.ResetRecovery()
      self.ETFLOG_20xx_check()
      self.SecFLASHcheck()
      oProc.St(IO_TP.prm_528_PwrCycle)
      self.dut.driveattr["TIME_TO_READY"] = float(self.dut.dblData.Tables('P528_TIMED_PWRUP').tableDataObj()[-1]['POWERUP_TIME']) *1000
      self.WR_powerCycle()  # required to clean up after Test 528
      self.SpinUp()


   def CCV_commonend(self):
      '''This function contains scripts for a common finishing process that all customers use.
      This testing includes:
      1.  Clear logging
      2.  Verify 0 growth defects and 0 servo defects
      3.  Attribute Upload and load 'prod_rev' attribute into "SCSI_CODE" per AMK request
      4.  Manufacturing Control Initializtion
      5.  Clear SMART Max Temp value
      6.  Power off drive
      '''

      testHeader("Common Ending Process")
      if testSwitch.virtualRun:
         return
      oProc.St(IO_TP.prm_538_ClearLogging)  # Clear logging threshold values
      oProc.St(IO_TP.prm_538_ClearLogging, {'prm_name':'Clear cumulative log'},COMMAND_WORD_2=(0x4000,))  # Clear logging cumulative values
      oProc.St(IO_TP.prm_529_CheckGrowthDefects)  # Verify 0 growth defects
      if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:
         oProc.St(IO_TP.prm_529_CheckServoDefects, MAX_HEAD = getattr(TP, 'prod_max_head', 0))  # Verify 0 servo defects before starting testing
      else:
         oProc.St(IO_TP.prm_529_CheckServoDefects)  # Verify 0 servo defects before starting testing
      oProc.St(IO_TP.prm_514_StdInquiryData, TEST_FUNCTION=(0x8000,))  # DriveVar option set
      oProc.St(IO_TP.prm_514_FwServoInfo, TEST_FUNCTION=(0x8000,))  # FW, Servo Ram, Servo Rom Revs
      # Send the data back up to the network
      self.dut.driveattr["DOWNLOAD"]= DriveVars.get("DOWNLOAD",'?')
      self.dut.driveattr["PROD_REV"]= DriveVars.get("PROD_REV",'?')
      #AMK Requested Change to have the Standard Inquiry bytes 20-23 Hex be in "SCSI_CODE"
      self.dut.driveattr["SCSI_CODE"]= DriveVars["PROD_REV"]  # Need SCSI_CODE to be customer inquiry rev
      self.dut.driveattr["SERVO_CODE"]= DriveVars["SERVO_CODE"][-4:]  # only want last four characters
      self.PortBypassCheck()
      self.MC_initialize()
      self.Clear_SMART_hightemp()
      DriveOff(20)
      oProc.St(IO_TP.prm_506_CmdTimeout,{'prm_name':'CCV Done'})  # Only purpose is to display CCV Done for Cell Status
      RimOff()


   def Oracle_FinalAssembly(self):
      '''This function will verify of the Oracle Final Assembly Date value
      against the value written to the drive during base I/O testing and as
      found in Seatrack attribute "FINAL_ASSY_DATE".
      This value is reflected by the Oracle code in Standard Inquiry,
      bytes 24-27 Hex.
      '''

      import binascii

      #Verification of the Final Assembly Date in Standard Inquiry
      if DriveAttributes.has_key('FINAL_ASSY_DATE'):
         finalassy = DriveAttributes["FINAL_ASSY_DATE"]
         oProc.St(IO_TP.prm_638_StandardInquiryData)	# Read Standard Inquiry Data
         oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Read Final Assembly Date'},PARAMETER_2=(0x0024,),PARAMETER_3=(0x0004,))  # Get Final Assembly Date, offset 24h, 4h bytes
         bufferData = DriveVars["Buffer Data"]
         drvfnassy = binascii.unhexlify(bufferData)
         if drvfnassy == finalassy :
            objMsg.printMsg("Final Assembly Date on drive matches the attribute: " + finalassy)
         else :
            objMsg.printMsg("*** Final Assembly Date does not match. ***")
            objMsg.printMsg("SeaTrack Attribute:  %s      does not match value on drive:  %s"%(finalassy,drvfnassy))
            ScrCmds.raiseException(10150,"FINAL_ASSY_DATE attribute does not match the Final Assembly Date written on the drive.")
      else:
         ScrCmds.raiseException(11201,"Missing FINAL_ASSY_DATE attribute")


   def Customer_change_def(self, chadef='NULL'):
      '''This function contains the scripts to issue a 0x40 Change Definition
      Feature for Customer unique configuration managment.  This includes
      issuing the Change Def command followed by a reset and a Power OFF/ON
      with the support commands to get the drive ready again.
      It is expected the full 10 bytes command is passed into this function.
      (ex. '40000135013034090000')
      '''

      objMsg.printMsg("Change Def command read from CCA = %s"%(chadef))
      param1 = int("0x"+chadef[0:4],16)   # parse chadef into parameter inputs for test 508
      param2 = int("0x"+chadef[4:8],16)     # then turn into integer 16(hexadecimal) for test 508 to accept
      param3 = int("0x"+chadef[8:12],16)
      param4 = int("0x"+chadef[12:16],16)
      param5 = int("0x"+chadef[16:20],16)
      oProc.St(IO_TP.prm_538_ChangeDef,{'prm_name':'Change Definition %s'%chadef},COMMAND_WORD_1=param1,COMMAND_WORD_2=param2,COMMAND_WORD_3=param3,COMMAND_WORD_4=param4,COMMAND_WORD_5=param5)
      oProc.St(IO_TP.prm_599_BusDeviceReset)	# Bus Device Reset Message with wait til ready
      oProc.St(IO_TP.prm_538_SpinDown)	# Spin Down
      self.WR_powerCycle()
      self.SpinUp()


   def IBM_FRUandDate(self, fru='NULL'):
      '''This function contains the scripts to verify the IBM unique FRU value,
      Inquiry bytes 114-125, matches the expected CCA value.  Also, the IBM
      Date of Manufacture reflected in Standard Inquiry bytes 102 - 106,
      66 - 6A in hex, is also validated.  Currently this value is generated
      from the ETF LOG date found in the ETF LOG information page.  In the
      future this value may be derived from the CAP file.
      NOTE:  This Date of Manufacture scripts will read up the year field
      from the ETFLOG DIF and verify the same last two digits of the year
      are present in bytes 102-103 of Inquiry.  If this partial value is
      present, then it is assumed that the full value is there as well.
      '''

      import binascii

      word1 = binascii.hexlify(fru)
      objMsg.printMsg("IBM FRU value:  %s (%s)"%(fru,word1))
      oProc.St(IO_TP.prm_638_StandardInquiryData)	# Read Standard Inquiry Data
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display 0-7Fh Inquiry bytes'},PARAMETER_2=(0x0000,),PARAMETER_3=(0x0080,))
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get FRU value from bytes 72h-7Dh'},PARAMETER_2=(0x0072,),PARAMETER_3=(0x000C,))
      bufferData = DriveVars["Buffer Data"]
      drv_fru = str(binascii.unhexlify(bufferData)).strip()  # make ASCII, remove spaces
      if fru == drv_fru.upper():
         objMsg.printMsg("The IBM FRU value has been verified to be:  %s"%fru);
      else:
         objMsg.printMsg("The IBM FRU value from the drive:  %s  (%s)     does not match the CCA value:  %s"%(drv_fru,bufferData,fru));
         ScrCmds.raiseException(10158,"IBM FRU value does not match the expected value.")

      objMsg.printMsg("- - - - - Standard Inquiry Date of Manufacture field verify - - - - -")
      oProc.St(IO_TP.prm_638_StandardInquiryData)	# Read Standard Inquiry Data
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display 0-6Bh Inquiry bytes'},PARAMETER_2=(0x0000,),PARAMETER_3=(0x006b,))
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Year value from Date of Manufacturing'},PARAMETER_2=(0x0066,),PARAMETER_3=(0x0002,))
      bufferData = DriveVars["Buffer Data"]
      date_year = binascii.unhexlify(bufferData)  # make ASCII

      oProc.St(IO_TP.prm_638_PlatformFactoryUnlock)	#Platform Factory Unlock
      oProc.St(IO_TP.prm_638_ReadDIF)  # Read DIF file
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display 18h DIF bytes'},PARAMETER_2=(0x0000,),PARAMETER_3=(0x0018,))
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Year value from ETFLOG Date'},PARAMETER_2=(0x0016,),PARAMETER_3=(0x0002,))
      bufferData = DriveVars["Buffer Data"]
      ETFLOG_year = binascii.unhexlify(bufferData)  # make ASCII

      objMsg.printMsg("IBM Date of Manufacture year is: = %s     ETFLOG year is: = %s"%(date_year,ETFLOG_year))
      if date_year == ETFLOG_year:
         objMsg.printMsg("IBM Date of Manufacture year is the same as the ETFLOG date year");
      else:
         objMsg.printMsg("* * * - FAIL - * * *")
         objMsg.printMsg("IBM Date of Manufacture year is **NOT** the same as the ETFLOG date year");
         ScrCmds.raiseException(10158,"IBM Date of Manufacture year is **NOT** the same as the ETFLOG date year")


   def Fujitsu_ConfigCode(self, cfg_code='NULL'):
      '''This function contains the commands to write and verify the Customer
      Config Code.  In older products, this value is to be written to
      ETFLOG DIF, bytes 44,45 using the D1 command.  Starting with Della
      products, this value is to be written to CAP, bytes 330,331 using
      Test 555.  Also for Della, it is required that the CAP header file is
      predefined as the variable "FinalAssemblyDate_CAP_HDR".   After writing
      the value, the drive will be power cycled, before verifing the value in
      Inquiry.  The value will be reflected in Standard Inquiry
      bytes 49,50 (31,32 in hex).
      '''

      import binascii

      if cfg_code == 'NULL':
         ScrCmds.raiseException(14886,"* * * Process Setup Problem:  Missing parameter for 'cfg_code'.")
      if len(cfg_code) != 2:
         ScrCmds.raiseException(14886,"* * * Process Setup Problem:  'cfg_code' value can only be 2 characters in length.  Current value is:  %s     len = (%s)"%(cfg_code,len(cfg_code)))

      word1 = binascii.hexlify(cfg_code)
      objMsg.printMsg("Setting config code value to:  %s (%s)"%(word1,cfg_code))
      P7 = int("0x"+word1,16)
      if self.FW_PLATFORM_FAM == 'DELLA':
         oProc.St(IO_TP.prm_555_WrtCapValue,WRITE_XFR_LENGTH=(0x0002,),MODIFY_APM_BYTE_NUM=(0x014A,),PARAMETER_0=P7,dlfile=(CN,TP.FinalAssemblyDate_CAP_HDR))  # Write CAP
      else:
         oProc.St(IO_TP.prm_508_WRT_pattern_to_WBuff)  # Write all 00's to Write Buffer
         oProc.St(IO_TP.prm_508_WRT_pattern_to_RBuff)  # Write all 00's to Read Buffer
         oProc.St(IO_TP.prm_638_PlatformFactoryUnlock)	#Platform Factory Unlock
         oProc.St(IO_TP.prm_638_ReadDIF)  # Read DIF file
         oProc.St(IO_TP.prm_508_Copy_RBuff_to_WBuff)  # Copy read to write buffer
         oProc.St(IO_TP.prm_508_Disp_WBuff, {'prm_name':'Display 30h bytes WBuff'},PARAMETER_2=(0x0000,),PARAMETER_3=(0x0030,))
         oProc.St(IO_TP.prm_508_WRT_bytes_to_WBuff, {'prm_name':'Write 2 bytes to WBuff'}, PARAMETER_2=(0x002C,),PARAMETER_3=(0x0002,), PARAMETER_7=P7)
         oProc.St(IO_TP.prm_508_Disp_WBuff, {'prm_name':'Display 30h bytes WBuff'},PARAMETER_2=(0x0000,),PARAMETER_3=(0x0030,))
         oProc.St(IO_TP.prm_638_WriteDIF)  # Write DIF file
      self.WR_powerCycle()
      self.SpinUp()
      oProc.St(IO_TP.prm_638_StandardInquiryData)	# Read Standard Inquiry Data
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display 0-40h Inquiry bytes'},PARAMETER_2=(0x0000,),PARAMETER_3=(0x0040,))
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Customer Config Code value from bytes 31h-32h'},PARAMETER_2=(0x0031,),PARAMETER_3=(0x0002,))
      bufferData = DriveVars["Buffer Data"]
      if word1.upper() == bufferData.upper():
         objMsg.printMsg("The Customer Config Code value has been verified to be:  %s  (%s)"%(bufferData,cfg_code));
      else:
         objMsg.printMsg("The Customer Config Code value from the drive:  %s       does not match the 'CFG' CCA value:  %s (%s)"%(bufferData,word1,cfg_code));
         ScrCmds.raiseException(10158,"Customer Config Code value does not match the expected value.")


   def set_verifyModeSense(self):
      '''This function is used to set and verify the shipping customer mode
      sense requirements based on the CCA "SHIP_MODE_SENSE" input.  Included
      in this function is the call to pull the final Read Capacity information
      in which to generate Seatrack attributes from.
      '''

      userlba = long(str(self.dut.driveConfigAttrs['USER_LBA_COUNT'][1]).strip())
      if userlba == 0:  # Special Engineering Evaluation setting
         (drvLLB,drvblocksize,drvprottype) = self.get_ReadCapacityInfo()  # get drive values
         userlba = drvLLB + 1
      modesenseReq = str(self.dut.driveConfigAttrs['SHIP_MODE_SENSE'][1]).strip()
      modesenseReport = {
                     'SD'        : "Saved Equal Default",
                     'SD_WCD'    : "Saved Equal Default and Write Cache Disabled",
                     'SD_RC'     : "Saved Equal Default and Reduce Capacity",
                     'SD_WCD_RC' : "Saved Equal Default, Write Cache Disabled and Reduce Capacity",
                     'SD_LA'     : "Saved Equal Default and Hitachi LA Check Disabled page 38, byte 0x10, bit 0",
                     'SD_LA2'    : "Saved Equal Default and Hitachi LA Check Disabled page 38, byte 0x14, bit 0"
                     }
      if modesenseReq not in modesenseReport:
         ScrCmds.raiseException(14886,"Mode Sense value:  %s, not found in set_verifyModeSense function."%modesenseReq)

      testHeader("Set and Verify Mode Sense:  " + modesenseReport[modesenseReq])
      if testSwitch.virtualRun:
         self.verifyReadCap()
         self.dut.driveattr["SHIP_MODE_SENSE"]= modesenseReq
         return


      #Force drive to Max Capacity
      PageData=(0x00FF,0x01FF,0x02FF,0x03FF,0x04FF,0x05FF,0x06FF,0x07FF,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,)
      oProc.St(IO_TP.prm_518_ModeSelect_Save, {'prm_name':'Max Capacity'},MODIFICATION_MODE=(0x0001,),PAGE_BYTE_AND_DATA34=(PageData))

      #Force drive to Saved equal Default Mode page settings
      ##Automatically manage Page 3 bypassing if needed.  This is to handle
      ##situations where the drive is in PI format or the sector size is not
      ##the default size.
      if self.InDefaultSectorSize():  # Yes, drive is in default sector size
         oProc.St(IO_TP.prm_537_Set_SAV_To_DEF)  # Set Saved Modes Sense to Default
         page3bypass = False
      else:
         oProc.St(IO_TP.prm_537_Set_SAV_To_DEF,MODE_COMMAND=(0x0002,),MODE_PAGES_BYPASSED_1=(0x0003,))  # SAV=DEF, except page 3
         page3bypass = True
      self.check_setD_SENSE()  # T537 will clear DSENSE, so must put back if needed

      PageBypassList = []  # List of mode pages (and subpages) to be bypassed per input for Test 1501.
      if page3bypass:
         PageBypassList.append(0x0300)

      PageBypassList.append(0x1902)  # Always bypass this page 19, subpage 02, as it has variable data and not necessary

      #Currently only one mode select is needed to handle the various requirements
      #so only setting PAGE_MOD_DATA_1 (mdsel1) at this time.
      #The mode selects can be done bitwise, but the compare is still by byte
      #Format of mdsel1 = page, subpage, byte, value of byte
      mdsel1 = (0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,)  # 1st mode page adjustment reset
      if modesenseReq == "SD":
         pass
      elif modesenseReq == "SD_WCD":
         self.DisableWriteCache()
         mdsel1 = (0x0008, 0x0000, 0x0002, 0x0010,)  # 1st mode page adjustment
      elif modesenseReq == "SD_RC":
         self.ReduceCapDrive(userlba)
      elif modesenseReq == "SD_WCD_RC":
         self.ReduceCapDrive(userlba)
         self.DisableWriteCache()
         mdsel1 = (0x0008, 0x0000, 0x0002, 0x0010,)  # 1st mode page adjustment
      elif modesenseReq == "SD_LA":
         self.DisableLACheck("byte0x10")
         mdsel1 = (0x0038, 0x0000, 0x0010, 0x0001,)  # 1st mode page adjustment
      elif modesenseReq == "SD_LA2":  # Customer has moved this byte in newer products
         self.DisableLACheck("byte0x14")
         mdsel1 = (0x0038, 0x0000, 0x0014, 0x0001,)  # 1st mode page adjustment
      else:
         ScrCmds.raiseException(14886,"Mode Sense value:  %s, not found in set_verifyModeSense function."%modesenseReq)

      #Setup for skip pages or set to 0xffff
      SkipPageParm = ['FIRST_SKIPPED_PAGE', 'SECOND_SKIPPED_PAGE', 'THIRD_SKIPPED_PAGE', 'FOURTH_SKIPPED_PAGE', 'FIFTH_SKIPPED_PAGE']
      PageBypassList.extend([0xFFFF]*(5-len(PageBypassList)))

      if len(PageBypassList) > 5:
         ScrCmds.raiseException(14886,"PageBypassList is too large.  Length is:  %s:  Values:  %s"%(len(PageBypassList),PageBypassList))
      elif len(PageBypassList) == 0:
         pass
      else:
         PageBypassParm = dict(zip(SkipPageParm, PageBypassList))

      oProc.St(IO_TP.prm_1501_SavEqDef,PageBypassParm,PAGE_MOD_DATA_1=mdsel1)

      self.verifyReadCap()
      self.dut.driveattr["SHIP_MODE_SENSE"]= modesenseReq


   def InDefaultSectorSize(self):
      '''This function will check mode page 3 sector size bytes 12,13 of the
      SAV and DEF and report if the drive is in the default sector size or not.
      '''

      oProc.St(IO_TP.prm_638_ReadDefaultModesense,PARAMETER_1=0x8300)	# Read Page 3 DEF
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get sector size'},PARAMETER_2=(0x001C,),PARAMETER_3=(0x0002,))
      DEFssize = DriveVars["Buffer Data"]
      oProc.St(IO_TP.prm_638_ReadSavedModesense,PARAMETER_1=0xC300)	# Read Page 3 SAV
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get sector size'},PARAMETER_2=(0x001C,),PARAMETER_3=(0x0002,))
      SAVssize = DriveVars["Buffer Data"]
      if SAVssize == DEFssize:
         objMsg.printMsg("Drive is in default sector size:  %s"%DEFssize)
         result = True
      else:
         objMsg.printMsg("Drive IS NOT in default sector size.  DEFAULT:  %s      SAVED:  %s"%(DEFssize,SAVssize))
         result = False
      return(result)


   def DisableWriteCache(self):
      '''This function will issue a bitwise mode select to disable write cache.
      '''

      oProc.St(IO_TP.prm_518_ModeSelect_Save, {'prm_name':'Disable Write Cache'},PAGE_CODE=(0x0008,),DATA_TO_CHANGE=(0x0001,),PAGE_BYTE_AND_DATA34=(0x0220,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,))  # Set page8, byte2, bit 2 = 0


   def DisableLACheck(self, bytetochange):
      '''This function will issue a bitwise mode select to disable LA check.
      '''

      if bytetochange == "byte0x10":
         oProc.St(IO_TP.prm_518_ModeSelect_Save, {'prm_name':'Disable LA Check'},PAGE_CODE=(0x0038,),DATA_TO_CHANGE=(0x0001,),PAGE_BYTE_AND_DATA34=(0x1001,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,))  # Set page38, byte0x10, bit 0 = 1
      else:
         oProc.St(IO_TP.prm_518_ModeSelect_Save, {'prm_name':'Disable LA Check'},PAGE_CODE=(0x0038,),DATA_TO_CHANGE=(0x0001,),PAGE_BYTE_AND_DATA34=(0x1401,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,))  # Set page38, byte0x14, bit 0 = 1

   def ReduceCapDrive(self,userlba):
      '''This function is used to reduce the capacity of the drive based on the
      input received.  A precheck is made first to verify the value requested
      is actually a reduced value from maximum.  This is done to protect against
      an accidental change in the user lba CCA value resulting in the shipping
      of incorrect capacity drives.
      '''

      (drvLLB,drvblocksize,drvprottype) = self.get_ReadCapacityInfo()  # get drive values
      if userlba == (drvLLB+1):
         ScrCmds.raiseException(14886,"Invalid CCA setup.  Capacity can not be reduced to requested value as it is already the maxiumum value.")
      param0 = (userlba>>56) | 0x0000
      param1 = ((userlba>>48) &0x00ff) | 0x0100
      param2 = ((userlba>>40) &0x0000ff) | 0x0200
      param3 = ((userlba>>32) &0x000000ff) | 0x0300
      param4 = ((userlba>>24) &0x00000000ff) | 0x0400
      param5 = ((userlba>>16) &0x0000000000ff) | 0x0500
      param6 = ((userlba>>8)  &0x000000000000ff) | 0x0600
      param7 = ((userlba)     &0x00000000000000ff) | 0x0700
      PageData=(param0,param1,param2,param3,param4,param5,param6,param7,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,)
      oProc.St(IO_TP.prm_518_ModeSelect_Save, {'prm_name':'Reduce Capacity'},MODIFICATION_MODE=(0x0001,),PAGE_BYTE_AND_DATA34=(PageData))
      (drvLLB,drvblocksize,drvprottype) = self.get_ReadCapacityInfo()  # get drive values
      if userlba != (drvLLB+1):
         ScrCmds.raiseException(14886,"Drive failed to set to required Reduced Capacity.  Required:  %s    Received:  %s"%(userlba,drvLLB+1))


   def ETFLOG_20xx_check(self):
      '''This function contains scripts to verify that the ETF LOG Date year field contains a value
      equal to or greater than 2009 up to 2099.  This essentially verifies a valid value was
      written.
      '''

      import binascii

      testHeader("Verify ETFLOG data value")
      oProc.St(IO_TP.prm_638_ReadDIF)  # Read DIF file
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display ETFLOG Date Year'},PARAMETER_2=(0x0014,),PARAMETER_3=(0x0004,))  # Get ETFLOG date year, offset 14h, 4h bytes
      bufferData = DriveVars["Buffer Data"]
      etflog_year = binascii.unhexlify(bufferData)  # make ASCII
      objMsg.printMsg("ETFLOG Year is = %s"%(etflog_year))
      if int(etflog_year) < 2009:
         ScrCmds.raiseException(10158,"ETFLOG Date Year is not greater than 2009")


   def SendSelfTestDiag(self):
      '''This function issues the 1D Self Test Diagnostic to the drive.
      '''

      testHeader("Self Test Diagnostics")
      oProc.St(IO_TP.prm_506_CmdTimeout)  # Extra timeout for larger Cache size drives for Send/Receive Diagnostics
      oProc.St(IO_TP.prm_552_SSCITest)  # Self Diagnostic SelfTest
      try:
         oProc.St(IO_TP.prm_538_SendDiagnostic)  # Send Self Test Diagnostics
      except:
         oProc.St(IO_TP.prm_538_ReceiveDiagnostic)  # Receive Diagnostics
         oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display Read Buffer'},PARAMETER_3=(0x0060,))  # Display 60h bytes
         ScrCmds.raiseException(10158,"Self Test Diagnostic Command Failed")


   def ResetRecovery(self):
      '''This function issues a reset to the drive, expects 06/29 on first
      Request Sense command and a 00/00 on the second.
      '''

      testHeader("Reset Recovery")
      oProc.St(IO_TP.prm_538_Rezero)	# Rezero Drive
      oProc.St(IO_TP.prm_599_BusDeviceReset)	# Bus Device Reset Message with wait til ready
      oProc.St(IO_TP.prm_538_RequestSense)  # Request Sense
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Sense Key'},PARAMETER_2=(0x0002,),PARAMETER_3=(0x0001,))
      sensekey = DriveVars["Buffer Data"]
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Additional Sense'},PARAMETER_2=(0x000C,),PARAMETER_3=(0x0001,))
      addsensekey = DriveVars["Buffer Data"]
      if sensekey == "06" and addsensekey == "29":
         objMsg.printMsg("Request sense return:  %s  %s"%(sensekey,addsensekey))
      else:
         ScrCmds.raiseException(10150,"Incorrect Sense data after reset.  Expected '06'  '29'     Received:  %s  %s"%(sensekey,addsensekey))
      oProc.St(IO_TP.prm_538_RequestSense)  # Request Sense
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Sense Key'},PARAMETER_2=(0x0002,),PARAMETER_3=(0x0001,))
      sensekey = DriveVars["Buffer Data"]
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Additional Sense'},PARAMETER_2=(0x000C,),PARAMETER_3=(0x0001,))
      addsensekey = DriveVars["Buffer Data"]
      if sensekey == "00" and addsensekey == "00":
         objMsg.printMsg("Request sense return:  %s  %s"%(sensekey,addsensekey))
      elif sensekey == "00" and addsensekey == "5E":  # Power saver feature
         objMsg.printMsg("Request sense return:  %s  %s"%(sensekey,addsensekey))
      else:
         ScrCmds.raiseException(10150,"Incorrect Sense data after 2nd Request Sense.  Expected '00'  '00'     Received:  %s  %s"%(sensekey,addsensekey))


   def Clear_SMARTandUDS(self):
      '''This is a platform based test function for clearing the SMART and UDS counters prior to
      drive shipment to the customer.
      '''

      testHeader("Clear SMART and UDS")
      oProc.St(IO_TP.prm_564_DispCumulativeSmart)  # Display Cumulative SMART Values
      self.UDS_Clear()  # Need once before SMART Clear or HeadAmp will restore old data
      oProc.St(IO_TP.prm_638_FormatSmartFrames)  # Format SMART Frames
      oProc.St(IO_TP.prm_638_ClearSmartCounters)  # Clear SMART Counters
      oProc.St(IO_TP.prm_638_HeadAmpMeasurements)  # Do head amp measurements for SMART
      self.UDS_Clear()  # Need once again after SMART Clear
      oProc.St(IO_TP.prm_538_SpinDown) # Spin Down
      self.WR_powerCycle()
      self.SpinUp()
      objMsg.printMsg("Verify UDS Power Cycle count has been cleared")
      oProc.St(IO_TP.prm_564_DispCumulativeSmart)  # Display Cumulative SMART Values
      oProc.St(IO_TP.prm_508_WRT_pattern_to_RBuff)  # Write all 00's to Read Buffer
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display 10h bytes RBuff'},PARAMETER_3=(0x0010,))
      oProc.St(IO_TP.prm_638_GetSmartSramFrame)  # Get SMART SRAM Frame
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display 10h bytes RBuff'},PARAMETER_3=(0x0010,))
      oProc.St(IO_TP.prm_508_Byte_RangeCheck, {'prm_name':'Check bytes 8-9 for value less than 2'},PARAMETER_2=(0x0008,),PARAMETER_8=(0x0002,))


   def UDS_Clear(self):
      '''This is a platform based test function for clearing the UDS counters prior to
      drive shipment to the customer.
      '''

      oProc.St(IO_TP.prm_508_WRT_pattern_to_WBuff)  # Write all 00's to Write Buffer
      oProc.St(IO_TP.prm_508_Disp_WBuff, {'prm_name':'Display 20h bytes WBuff'},PARAMETER_3=(0x0020,))
      oProc.St(IO_TP.prm_508_WRT_bytes_to_WBuff, {'prm_name':'Write 8 bytes to WBuff'}, PARAMETER_2=(0x0000,), PARAMETER_7=(0x0600,), PARAMETER_8=(0x0600,),PARAMETER_9=(0x0800,),)  # Write bytes to set up UDS clear, offset 0
      oProc.St(IO_TP.prm_508_WRT_bytes_to_WBuff, {'prm_name':'Write 8 bytes to WBuff'}, PARAMETER_2=(0x0008,), PARAMETER_7=(0x0800,), PARAMETER_8=(0x0100,),PARAMETER_9=(0x0119,),PARAMETER_10=(0x0906,))  # Write bytes to set up UDS clear, offset 8
      oProc.St(IO_TP.prm_508_Disp_WBuff, {'prm_name':'Display 20h bytes WBuff'},PARAMETER_3=(0x0020,))
      oProc.St(IO_TP.prm_638_PlatformFactoryUnlock)  # Unlock for Platform
      oProc.St(IO_TP.prm_599_SetMaxBuffer)  # Set Buffer sizes to maximum
      oProc.St(IO_TP.prm_599_SendFactoryCommand)  # Manually issue Send Factory Command
      oProc.St(IO_TP.prm_599_ReceiveFactoryCommand)  # Manually issue Receive Factory Command


   def verifySerialNumber(self):
      '''This function compares the "HDASerialNumber" to the serial number found in the Inquiry
      Vital Product Page 80.  A special SunMicro format check will also be attempted before failing
      to handle the unique SunMicro feature where the VPD Page 80 Seagate Serial number value is shifted out,
      starting at byte 18 Hex instead of the standard 4 bytes.
      '''

      import binascii

      testHeader("Verfiy Serial Number")
      sernum =  HDASerialNumber  # Get HDA serial number (in ASCII)
      if testSwitch.virtualRun:
         DRVsernum1 = DRVsernum2 = sernum
      else:
         oProc.St(IO_TP.prm_538_ReadSerialNumPage)  # Read Drive S/N page
         oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Serial Number from offset 4h'},PARAMETER_2=(0x0004,),PARAMETER_3=(0x0008,))  # Get Serial Num, offset 4h, 8h bytes
         bufferData = DriveVars["Buffer Data"]
         DRVsernum1 = binascii.unhexlify(bufferData)  # make ASCII
         oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Serial Number from offset 18h'},PARAMETER_2=(0x0018,),PARAMETER_3=(0x0008,))  # Get Serial Num, offset 18h, 8h bytes
         bufferData = DriveVars["Buffer Data"]
         DRVsernum2 = binascii.unhexlify(bufferData)  # make ASCII
      if DRVsernum1 == sernum:
         objMsg.printMsg("Drive Serial number read from drive is = %s     Drive Serial number in test = %s"%(DRVsernum1,sernum))
      elif DRVsernum2 == sernum:
         objMsg.printMsg("Drive Serial number read from drive (special offset) is = %s     Drive Serial number in test = %s"%(DRVsernum2,sernum))
      else:
         objMsg.printMsg("Drive Serial being tested is:  %s"%sernum)
         objMsg.printMsg("Drive Serial number read from byte 04h offset of drive is = %s"%DRVsernum1)
         objMsg.printMsg("Drive Serial number read from byte 18h offset of drive is = %s"%DRVsernum2)
         ScrCmds.raiseException(10150,"Drive Serial Number does not match the Serial Number written on the drive.")


   def verifyDataPattern(self):
      '''This function does a quick verification of the data pattern written on
      the drive to ensure it matches the data pattern requirement defined by CCA
      ZERO_PTRN_RQMT.  A sampling of LBAs within the requirement range
      are verified for compliance.
      '''

      import random

      patternreq = str(self.dut.driveConfigAttrs.get('ZERO_PTRN_RQMT',[0,'NA'])[1]).rstrip()

      userlba = long(str(self.dut.driveConfigAttrs['USER_LBA_COUNT'][1]).strip())
      if userlba == 0:  # Special Engineering Evaluation setting
         (drvLLB,drvblocksize,drvprottype) = self.get_ReadCapacityInfo()  # get drive values
         userlba = drvLLB + 1
      maxlba = userlba-1
      blocksize = int(str(self.dut.driveConfigAttrs['BYTES_PER_SCTR'][1]).strip())

      zeroPatternLookup = {
         'NA' : ('Not Applicable (means none allowed)',   0),
         '1'  : ('Block 0 Only',                          1),
         '10' : ('First and Last 400K LBAs*',             400000),
         '12' : ('First and Last 1 Million LBAs (512MB)', 1048576),
         '13' : ('First and Last 2 Million LBAs',         2097152),
         '15' : ('First and Last 20 Million LBAs',        20971520),
         '20' : ('Full Pack',                             0),}
      try:
         pattLabel, pattLBArange = zeroPatternLookup[patternreq]
      except:
         ScrCmds.raiseException(14886,"Zero Pattern Write Validate - DCM ZERO_PTRN_RQMT: %s not supported'"%patternreq)

      testHeader("Verfiy Data Pattern:  " + pattLabel + " ")
      if testSwitch.virtualRun:
         self.dut.driveattr['ZERO_PTRN_RQMT'] = patternreq
         return

      if patternreq == 'NA':
         objMsg.printMsg("Skipping ZERO_PTRN_RQMT check - DCM indicated Not Applicable")
         self.dut.driveattr['ZERO_PTRN_RQMT'] = patternreq
         return

      self.test508CompCheck()  # Verifies Test 508 compare is functioning correctly
      #Pre-condition Write Buffer with all 00's
      oProc.St(IO_TP.prm_508_WRT_pattern_to_WBuff,{'prm_name':'Write 00 pattern to Write Buffer'},PARAMETER_3=blocksize)  # Write all 00's to Write Buffer

      if patternreq == '1':  # Block 0 Only
         self.Verify_all_00s(0,blocksize)
      elif patternreq in ['10', '12', '13', '15']:  # Split range requirements
         self.splitLBArangecheck(pattLBArange,maxlba,blocksize)
      elif patternreq == '20':  # Full Pack
         self.Verify_all_00s(maxlba,blocksize)
         for cnt in range(0, maxlba, maxlba/20):
            self.Verify_all_00s(cnt,blocksize)
         for cnt in range(1, 21):
            self.Verify_all_00s(random.randrange(maxlba),blocksize)
      self.dut.driveattr['ZERO_PTRN_RQMT'] = patternreq


   def splitLBArangecheck(self,lba_range,maxlba,blocksize):
      '''This function is used as the driver for the lba selections for
      first/last data pattern requirements
      '''

      import random

      self.Verify_all_00s(maxlba,blocksize)
      self.Verify_all_00s(lba_range-1,blocksize)
      self.Verify_all_00s(maxlba-lba_range+1,blocksize)
      #Inner range for increment
      for cnt in range(0, lba_range, lba_range/10):
         self.Verify_all_00s(cnt,blocksize)
      #Outer range for increment
      for cnt in range(maxlba-lba_range+1, maxlba, lba_range/10):
         self.Verify_all_00s(cnt,blocksize)
      #Inner range for random
      for cnt in range(1, 11):
         self.Verify_all_00s(random.randrange(lba_range),blocksize)
      #Outer range for random
      for cnt in range(1, 11):
         self.Verify_all_00s(random.randrange(maxlba-lba_range+1,maxlba),blocksize)


   def Verify_all_00s(self,lba,blocksize):
      '''This function is used to verify an all 00s data pattern on one block.
      '''

      from Process import CProcess
      oProc = CProcess()

      objMsg.printMsg("Verify all 00s data on LBA:  %s (0x%012X)"%(lba,lba))
      cmw2 = (lba & 0xFFFF000000000000) >> 48
      cmw3 = (lba & 0x0000FFFF00000000) >> 32
      cmw4 = (lba & 0x00000000FFFF0000) >> 16
      cmw5 = (lba & 0x000000000000FFFF)
      oProc.St(IO_TP.prm_538_ReadLBA,{'prm_name':'Read LBA'},COMMAND_WORD_2=cmw2,COMMAND_WORD_3=cmw3,COMMAND_WORD_4=cmw4,COMMAND_WORD_5=cmw5,COMMAND_WORD_7=(0x0001,))
      try:
         oProc.St(IO_TP.prm_508_CompareW2RBuffer,PARAMETER_3=(blocksize))  # Compare read buffer and write buffer
      except:
         oProc.St(IO_TP.prm_508_Disp_RBuff,PARAMETER_3=(blocksize))  # Display read buffer
         oProc.St(IO_TP.prm_508_Disp_WBuff,PARAMETER_3=(blocksize))  # Display write buffer
         ScrCmds.raiseException(10158,"Data Pattern Compare Failure")


   def test508CompCheck(self):
      '''The following is a check is to verify initiator code Test 508 compare function is working.
      The Write and Read buffers are forced to be different and the compare is expected to fail.
      Then the Write and Read buffer are forced to be the same and the compare should pass.
      '''

      blocksize = 32
      oProc.St(IO_TP.prm_508_WRT_pattern_to_RBuff,{'prm_name':'Write 00 pattern to Read Buffer'}, PARAMETER_3=blocksize)
      oProc.St(IO_TP.prm_508_WRT_pattern_to_WBuff,{'prm_name':'Write 00 pattern to Write Buffer'},PARAMETER_3=blocksize)
      oProc.St(IO_TP.prm_508_WRT_bytes_to_RBuff,{'prm_name':'Write pattern to Read Buffer'},PARAMETER_2=(0x0007,),PARAMETER_3=(0x0001,),PARAMETER_7=(0xff00,))
      try:
         oProc.St(IO_TP.prm_508_CompareW2RBuffer,PARAMETER_3=(blocksize))  # Compare read buffer and write buffer
         oProc.St(IO_TP.prm_508_Disp_RBuff,PARAMETER_3=(blocksize))  # Display read buffer
         oProc.St(IO_TP.prm_508_Disp_WBuff,PARAMETER_3=(blocksize))  # Display write buffer
         ScrCmds.raiseException(10158,"Diff Data Pattern Compare Failure.  Indicates Test 508 Compare function is not working.")
      except:
         objMsg.printMsg("Buffer Difference Testing verified.")

      oProc.St(IO_TP.prm_508_WRT_bytes_to_RBuff,{'prm_name':'Write pattern to Read Buffer'},PARAMETER_2=(0x0007,),PARAMETER_3=(0x0001,),PARAMETER_7=(0x0000,))
      try:
         oProc.St(IO_TP.prm_508_CompareW2RBuffer,PARAMETER_3=(blocksize))  # Compare read buffer and write buffer
         objMsg.printMsg("Buffer Same Testing verified.")
      except:
         oProc.St(IO_TP.prm_508_Disp_RBuff,PARAMETER_3=(blocksize))  # Display read buffer
         oProc.St(IO_TP.prm_508_Disp_WBuff,PARAMETER_3=(blocksize))  # Display write buffer
         ScrCmds.raiseException(10158,"Same Data Pattern Compare Failure.  Indicates Test 508 Compare function is not working.")


   def MC_initialize(self):
      '''This function contains the factory command to initialize the Manufacture Control command.
      It uses the Manufacture Control Diagnostic command 0x0163.  There are two bits currently
      available.  The firmware plan is that the factory should always issue both bit 0 and 1,
      allowing the customer firmware to determine if it would actually use the settings.
      BER (bit 0) - BGMS First Run Status - used to set the first BGMS interrupt at 5ms
      instead of 500ms
      FW  (bit 1) - First Write Status - used to know when the customer has issue the first
      write to the drive.
      '''

      testHeader("Initialize Manufacture Control settings to value of 03")
      oProc.St(IO_TP.prm_638_PlatformFactoryUnlock)	# Unlock for Platform
      oProc.St(IO_TP.prm_638_ManufactureControlInitialize)	# Manufacture Control Initialize


   def Clear_EWLM(self):
      '''This function is used to check the data for the EWLM (Enhanced
      Workload Management Log) to verify it is cleared.  If it is not clear
      then attempt to clear it.  If the commands to clear fail, it is assume the
      firmware code does not support this command.  If the command to clear
      did not fail, the data is verified to be clear.
      '''

      testHeader("Clear EWLM")
      # Use to unlock the Hidden Log pages
      oProc.St(IO_TP.prm_508_WRT_pattern_to_WBuff,{'prm_name':'Write 00 pattern to Write Buffer 20h'},PARAMETER_3=(0x0020,))  # Write all 00's to Write Buffer
      oProc.St(IO_TP.prm_508_Disp_WBuff, {'prm_name':'Display 20h bytes WBuff'},PARAMETER_3=(0x0020,))
      oProc.St(IO_TP.prm_508_WRT_bytes_to_WBuff, {'prm_name':'Write 8 bytes to WBuff'}, PARAMETER_2=(0x0000,), PARAMETER_7=(0x0600,), PARAMETER_8=(0x0008,),PARAMETER_9=(0xFFF0,),PARAMETER_10=(0x0304,))  # Load Write Buffer to Unlock Log Select P1
      oProc.St(IO_TP.prm_508_WRT_bytes_to_WBuff, {'prm_name':'Write 8 bytes to WBuff'}, PARAMETER_2=(0x0008,), PARAMETER_7=(0x3397,), PARAMETER_8=(0x0000,),PARAMETER_9=(0x0000,),PARAMETER_10=(0x0000,))  # Load Write Buffer to Unlock Log Select P2
      oProc.St(IO_TP.prm_508_Disp_WBuff, {'prm_name':'Display 20h bytes WBuff'},PARAMETER_3=(0x0020,))
      oProc.St(IO_TP.prm_538_ClearLogging, {'prm_name':'Unlock Hidden Log pages'},COMMAND_WORD_1=(0x4C00,),COMMAND_WORD_2=(0x4000,))  # Unlock Hidden Log pages

      # Get listing of all pages supported from Log page 0
      oProc.St(IO_TP.prm_538_GetLogPage)  # Get Log Page 0
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display Read Buffer'},PARAMETER_3=(0x0030,))  # Display 30h bytes
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Read Buffer Data'},PARAMETER_2=(0x0003,),PARAMETER_3=(0x0001,))  # Get number of additional Log 0 bytes
      bufferData = DriveVars["Buffer Data"]
      objMsg.printMsg("Log 0 additional bytes (byte 3):  %s"%bufferData)
      add_bytes = int("0x"+str(bufferData),16)
      objMsg.printMsg("add_bytes Log 0 additional bytes (byte 3):  %s"%add_bytes)

      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Read Buffer Data'},PARAMETER_2=(0x0004,),PARAMETER_3=add_bytes)  # Get all pages supported
      bufferData = DriveVars["Buffer Data"]
      objMsg.printMsg("Supported Log pages:")
      pages_found = ""
      page0x36_found = "No"
      for n in range(0,add_bytes):
         page = "%s%s"%(bufferData[n*2],bufferData[(n*2)+1])
         pages_found = pages_found + page + ", "
         if page == "36":
            page0x36_found = "Yes"
      objMsg.printMsg("%s"%pages_found[:-2])
      if page0x36_found == "Yes":
         objMsg.printMsg("Log Page 0x36 found")
         oProc.St(IO_TP.prm_538_GetLogPage,{'prm_name':'Get Log Page 0x36'},COMMAND_WORD_2=(0x7600,),COMMAND_WORD_4=(0x00FA,),COMMAND_WORD_5=(0x0000,))
         oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Read Buffer Data'},PARAMETER_2=(0x0002,),PARAMETER_3=(0x0002,))  # Get number of additional page 0x36 bytes
         bufferData = DriveVars["Buffer Data"]
         objMsg.printMsg("Page 0x36 additional bytes (byte 2,3):  %s"%bufferData)
         add_bytes = int("0x"+str(bufferData),16)
         oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display Read Buffer'},PARAMETER_3=(add_bytes+4))  # Display Read Buffer
         oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Read Buffer Data'},PARAMETER_2=(0x001C,),PARAMETER_3=(0x0002,))
         last_parm_code = DriveVars["Buffer Data"]
         objMsg.printMsg("Get EWLM Last Parameter Code (byte 24,25):  %s"%last_parm_code)
         if last_parm_code != "0000":
            objMsg.printMsg("EWLM data not cleared")
            objMsg.printMsg("------------------------------------------------------------")
            objMsg.printMsg("EWLM Control: Clear Log")
            oProc.St(IO_TP.prm_638_PlatformFactoryUnlock)	# Platform Unlock Command
            try:
               oProc.St(IO_TP.prm_638_EWLM_ControlClearLog)  # EWLM Control: Clear Log
               EWLM_cmd = "Yes"
            except ScriptTestFailure, failureData:
               ec_code = failureData[0][2]
               EWLM_cmd = "No"
               oProc.St(IO_TP.prm_504_SenseAndDriveData)	# Display Sense, Last Cmd, Cyl, Hd, Sec, LBA
               oProc.St(IO_TP.prm_517_RequestSense_Ready_Check)  # Checks for drive not ready conditions
            if EWLM_cmd == "Yes":
               oProc.St(IO_TP.prm_538_GetLogPage,{'prm_name':'Get Log Page 0x36'},COMMAND_WORD_2=(0x7600,),COMMAND_WORD_4=(0x00FA,),COMMAND_WORD_5=(0x0000,))
               oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get Read Buffer Data'},PARAMETER_2=(0x001C,),PARAMETER_3=(0x0002,))
               last_parm_code = DriveVars["Buffer Data"]
               objMsg.printMsg("Get EWLM Last Parameter Code (byte 24,25):  %s"%last_parm_code)
               if (last_parm_code != "0000") and (last_parm_code != "0001"):
                  objMsg.printMsg("Attempt failed to clear EWLM data.")
                  ScrCmds.raiseException(10150,"EWLM Last Parameter Code (byte 24,25) is not cleared.")
               else:
                  objMsg.printMsg("EWLM data cleared and verified to be %s"%last_parm_code)
            else:
               objMsg.printMsg("EWLM Control: Clear Log Command Failed with: EC%s   - Command not supported.  OK to proceed"%ec_code)
         else:
            objMsg.printMsg("EWLM data verified to be 0x0000")
      else:
         objMsg.printMsg("Log Page 0x36 NOT found.  OK to proceed.")


   def verifyReadCap(self):
      '''This function will pull the Read Capacity data from the drive, verify
      the User LBA count post to the appropriate attributes.
      As a feature for early Gen processes, User LBA count verification can
      be bypassed if the USER_LBA_COUNT is set to '0'.
      '''
      ##NOTE:  The logical block value returned from a SAS Read Capacity
      ##command is the "Last" Logical Block value.  This value is one less that
      ##what a customer would define as the number of "user logical blocks".

      testHeader("Get Read Capacity")
      userlba = str(self.dut.driveConfigAttrs['USER_LBA_COUNT'][1]).strip()
      blocksize = str(self.dut.driveConfigAttrs['BYTES_PER_SCTR'][1]).strip()
      prottypeval = str(self.dut.driveConfigAttrs['FMT_PROT_TYPE'][1]).strip()
      prot_type = {'0':'TYPE_0', '1':'TYPE_1', '3':'TYPE_2', '5':'TYPE_3'}
      if testSwitch.virtualRun:
         #Customer Configuration Attributes
         prot_type_flip = dict((v,k) for k,v in prot_type.iteritems())
         prot_val = prot_type_flip[prottypeval]
         drvLLB,drvblocksize,drvprottype = (long(userlba)-1),int(blocksize),int(prot_val)
      else:
         (drvLLB,drvblocksize,drvprottype) = self.get_ReadCapacityInfo()  # get drive values
      objMsg.printMsg("From Drive:   Last Logical Block: %X (%d)    Block Size: %X (%d)    Protection Settings: %02X (%d)"%(drvLLB,drvLLB,drvblocksize,drvblocksize,drvprottype,drvprottype))
      drvCap = int(( drvLLB * drvblocksize )/1000000000)
      objMsg.printMsg("Drive Capacity - %dGB"%drvCap)
      objMsg.printMsg("User LBA Count:  %X (%d)"%(drvLLB+1,drvLLB+1))

      if userlba == '0':  # Special Engineering Evaluation setting
         self.dut.driveattr["USER_LBA_COUNT"]= userlba
         objDut.Eng_Bypass = 'ENG_EVAL_BYPASS'
      elif long(userlba) != (drvLLB+1):
         ScrCmds.raiseException(14886,"Drive failed to verify required User LBA Count.  Required:  %s    Received:  %s"%(long(userlba),drvLLB+1))
      else:
         self.dut.driveattr["USER_LBA_COUNT"]= drvLLB+1
      self.dut.driveattr["BYTES_PER_SCTR"]= drvblocksize
      self.dut.driveattr["FMT_PROT_TYPE"]= prot_type[str(drvprottype)]


   def verifyWWN(self):
      '''This function compares the World Wide Number attribute, either
      "WW_FC_ID" or "WW_SAS_ID" to what is actually on the drive in both the
      ETFLOG and CAP.  The WWN from the drive is obtained from the ETFLOG Drive
      Information File bytes 3E-45 hex.  The WWN from the CAP is obtained from
      bytes 24-2B hex.
      '''

      testHeader("Verify WWN")
      wwAttrName = str(self.dut.driveConfigAttrs["WWN"][1]).rstrip()
      #Check for invalid WWN attribute per I/O type
      if objDut.drvIntf in ['FC','FCV'] and wwAttrName == "WW_FC_ID": pass
      elif objDut.drvIntf in ['SS','AS','NS','SAS'] and wwAttrName == "WW_SAS_ID": pass
      elif objDut.drvIntf in ['SATA'] and wwAttrName == "WW_SATA_ID":
         ScrCmds.raiseException(14886,"This process is not for a SATA drive.")
      else:
         ScrCmds.raiseException(14886,"Invalid WWN CCA value:  %s    for drvIntf:  %s"%(wwAttrName,objDut.drvIntf))

      if testSwitch.virtualRun: return

      wwn = DriveAttributes.get(wwAttrName,None)
      oProc.St(IO_TP.prm_638_PlatformFactoryUnlock)	# Platform Unlock Command
      oProc.St(IO_TP.prm_638_ReadDIF)  # Read DIF file
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display DIF WWN'},PARAMETER_2=(0x003e,),PARAMETER_3=(0x0008,))  # Get WWN, offset 3eh, 8h bytes
      ETF_wwn = DriveVars["Buffer Data"]
      oProc.St(IO_TP.prm_638_ReadFLASHCAP)  # Read FLASH CAP
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display CAP WWN'},PARAMETER_2=(0x0024,),PARAMETER_3=(0x0008,))  # Get WWN, offset 24h, 8h bytes
      CAP_wwn = DriveVars["Buffer Data"]
      objMsg.printMsg("WWN attribute = %s     ETF LOG WWN = %s     CAP WWN = %s"%(wwn,ETF_wwn,CAP_wwn))
      if wwn != ETF_wwn :
         ScrCmds.raiseException(10150,"ETF LOG WWN does not match the WWN attribute.")
      if wwn != CAP_wwn :
         ScrCmds.raiseException(10150,"CAP WWN does not match the WWN attribute.")


   def set_verifyLifeState(self):
      '''This function sets and verifies the drive LifeState for all drives
      including non-SED, which should be a "NA".
      '''

      testHeader("Set and Verify Life State")
      CCALifeState = str(self.dut.driveConfigAttrs.get('SED_LC_STATE',[0,'NA'])[1]).strip()
      if testSwitch.virtualRun:
         self.dut.driveattr["SED_LC_STATE"]= CCALifeState
         return

      DrvLifeState = self.getLifeState()
      if DrvLifeState == CCALifeState:
         objMsg.printMsg("Drive is already in the correct shipping '%s' LifeState."%DrvLifeState)
      elif DrvLifeState == 'MFG' and CCALifeState == 'USE':
         objMsg.printMsg("Converting drive from 'MFG' to 'USE' LifeState.")
         self.handlersandAuthenticate("OFF")  # Authenticate setup
         oProc.St(IO_TP.prm_577_SEDSetUse)
         self.SEDUnlockDiagUDS()  # If SED drive in "USE" mode, unlock DIAG port
      else:
         ScrCmds.raiseException(14886,"Invalid LifeState condition.  Drive is in %s Mode.    It can not be set to %s mode in this process."%(DrvLifeState,CCALifeState))

      #Verify the LifeState to the CCA
      DrvLifeState =  self.getLifeState()
      if DrvLifeState != CCALifeState:
         ScrCmds.raiseException(10150,"LifeState does not match.  Drive:  %s      CCA(SED_LC_STATE):  %s"%(DrvLifeState,CCALifeState))
      self.dut.driveattr["SED_LC_STATE"]= DrvLifeState


   def getLifeState(self):
      '''This function is used to return the LifeState value.
      '''

      if testSwitch.virtualRun:
         LifeState_val = str(self.dut.driveConfigAttrs.get('SED_LC_STATE',[0,'NA'])[1]).strip()
      else:
         try:
            LifeState='FF'  ## None SED/Virgin Drive
            oProc.St(IO_TP.prm_575_Discovery)	# Discovery
            oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display Read Buffer 20h'},PARAMETER_3=(0x0020,))
            oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get LifeState'},PARAMETER_2=(0x0011,),PARAMETER_3=(0x0001,))
            LifeState = DriveVars["Buffer Data"]
         except:
            objMsg.printMsg("Discovery Failed - Non SED drives")
            pass
         LifeState_con = {'00':'SETUP', '01':'DIAG', '80':'USE', '81':'MFG', 'FF':'NA'}
         LifeState_val =  LifeState_con[LifeState]
         objMsg.printMsg("SED LifeState: %s (%s)" %(LifeState_val,LifeState))
      return LifeState_val


   def set_verifySEDTables(self):
      '''This function is used to set and verify the various features in the
      FW, DIAG and UDS tables.  This function will issue a capture if the
      firmware locking port is changed.
      '''

      CCALifeState = str(self.dut.driveConfigAttrs.get('SED_LC_STATE',[0,'NA'])[1]).strip()
      CCADLP_SETTING = str(self.dut.driveConfigAttrs.get('DLP_SETTING',[0,'NA'])[1]).strip()
      CCAFDE_TYPE = str(self.dut.driveConfigAttrs.get('FDE_TYPE',[0,'NA'])[1]).strip()
      if CCALifeState != "USE":  # Not a SED drive or is in MFG mode
         self.dut.driveattr["DLP_SETTING"]= CCADLP_SETTING
         self.dut.driveattr["FDE_TYPE"]= CCAFDE_TYPE
         return

      testHeader("Set and Verify SED Table Features")
      if testSwitch.virtualRun:
         DriveDLPvalue = self.getFWLockPort()
         self.dut.driveattr["DLP_SETTING"]= DriveDLPvalue
         return
      oProc.St(IO_TP.prm_538_SpinDown) # Spin Down
      self.WR_powerCycle()
      self.SpinUp("OFF")  # DO NOT UNLOCK the UDS and DIAG ports option
      DriveDLPvalue = self.getFWLockPort()
      if DriveDLPvalue == CCADLP_SETTING:
         objMsg.printMsg("FW Locking Port value is set correctly to %s" %DriveDLPvalue)
      elif DriveDLPvalue == "LOCKED" and CCADLP_SETTING == "UNLOCKED":
         objMsg.printMsg("Unlock DL port process")
         self.handlersandAuthenticate()  # Authenticate setup
         oProc.St(IO_TP.prm_575_GetFWUnlockTable)          # Get FW unlock table
         oProc.St(IO_TP.prm_575_UnlockDLPort)              # Unlock DL port
         oProc.St(IO_TP.prm_575_GetFWUnlockTable)          # Get FW unlock table
         oProc.St(IO_TP.prm_575_DisableResetLock)          # Disable lock on reset
         oProc.St(IO_TP.prm_575_GetFWUnlockTable)          # Get FW unlock table
         oProc.St(IO_TP.prm_575_FDE_CapturePersistentData) # Capture
         oProc.St(IO_TP.prm_575_CloseSession)              # close session
      elif DriveDLPvalue == "UNLOCKED" and CCADLP_SETTING == "LOCKED":
         objMsg.printMsg("Lock DL port process")
         self.handlersandAuthenticate()  # Authenticate setup
         oProc.St(IO_TP.prm_575_GetFWUnlockTable)          # Get FW unlock table
         oProc.St(IO_TP.prm_575_UnlockDLPort)              # Unlock DL port
         oProc.St(IO_TP.prm_575_GetFWUnlockTable)          # Get FW unlock table
         oProc.St(IO_TP.prm_575_SetResetLock)              # Set lock on reset
         oProc.St(IO_TP.prm_575_GetFWUnlockTable)          # Get FW unlock table
         oProc.St(IO_TP.prm_575_FDE_CapturePersistentData) # Capture
         oProc.St(IO_TP.prm_575_CloseSession)              # close session
      else:
         objMsg.printMsg("* * * - FAIL - * * *")
         objMsg.printMsg("DriveDLPSetting:  %s    CCA_DLPSetting:  %s"%(DriveDLPvalue,CCADLP_SETTING))
         objMsg.printMsg("Currently do not have the capability to change from the current drive state to the expected state.")
         ScrCmds.raiseException(14886,"MFG Process issue.  Can not change to these states.")

      objMsg.printMsg("Begin Feature Verify")
      self.WR_powerCycle()
      self.SpinUp("OFF")  # DO NOT UNLOCK the UDS and DIAG ports option

      objMsg.printMsg("Verify ISE or non-ISE")
      # Must not authenticate to MakerSYMK or PSID to run this special check
      oProc.St(IO_TP.prm_575_SetSSC1MT)
      oProc.St(IO_TP.prm_575_StartAdminSession)  # start admin session
      if int(self.initchglistno) >= 439877:  # minimum initiator code needed to support
         if CCAFDE_TYPE in ['SED BASE ISE']:
            oProc.St(IO_TP.prm_575_GetMsidFromDrive,ISE_VERSION=0x0001,)  # Get MSID as ISE
         else:
            oProc.St(IO_TP.prm_575_GetMsidFromDrive,ISE_VERSION=0x0000,)  # Get MSID as ISE
      else:  # allows use of older initiator codes before ISE_VERSION was defined
         oProc.St(IO_TP.prm_575_GetMsidFromDrive)  # Get MSID as non-ISE
      self.dut.driveattr["FDE_TYPE"]= CCAFDE_TYPE
      oProc.St(IO_TP.prm_575_CloseSession)	        # close session

      objMsg.printMsg("Verify DL port process")
      self.handlersandAuthenticate()  # Authenticate setup
      for table in ["DIAG", "FW", "UDS"]:
         tabletype = {'DIAG':0x01, 'FW':0x02, 'UDS':0x03}
         table_val =  tabletype[table]
         objMsg.printMsg("Table Type: %s (%02X)" %(table,table_val))
         p_lock = 0x0001  # default - check for port locked
         r_lock = 0x0001  # default - check for lock on reset
         if table == "FW":
            if CCADLP_SETTING == "UNLOCKED":
               p_lock = 0x0000  # Unlock DLP
               r_lock = 0x0000  # Disable Lock on Reset
         try:
            oProc.St(IO_TP.prm_575_CheckPort_states,UIDLSWL=table_val,PORT_LOCKED=p_lock,LOCK_ON_RESET=r_lock)  # Verify table
         except:
            objMsg.printMsg("Table Type: %s (%02X)" %(table,table_val))
            objMsg.printMsg("SED table values are incorrect.  Expected values:  PORT_LOCKED=%04x    LOCK_ON_RESET=%04x   " %(p_lock,r_lock))
            ScrCmds.raiseException(10150,"SED table values are incorrect.")
      oProc.St(IO_TP.prm_575_CloseSession)	        # close session
      self.dut.driveattr["DLP_SETTING"]= CCADLP_SETTING

      objMsg.printMsg("Verify Band Enables and Values")
      oProc.St(IO_TP.prm_575_FDE_StartLockingSession,timeout=30)
      oProc.St(IO_TP.prm_575_FDE_Check_band_values,timeout=30)
      oProc.St(IO_TP.prm_575_FDE_Check_band_enables,timeout=30)
      oProc.St(IO_TP.prm_575_FDE_CloseLockingSession,timeout=30)

      objMsg.printMsg("Set and Verify SOM value")
      oProc.St(IO_TP.prm_575_StartAdminSession)  # start admin session
      SOM_value = self.GetSOM()
      if SOM_value not in ['00','01','02']:
         objMsg.printMsg("Drive does not support SOM.")
      else:
         objMsg.printMsg("Attempt to set drive to SOM 0")
         oProc.St(IO_TP.prm_575_AuthenticateToMakerSymK)  # authenticate to maker sym k
         oProc.St(IO_TP.prm_575_FDE_GetPSIDfromFIS)  # Get PSID from FIS
         oProc.St(IO_TP.prm_575_FDE_AuthPSID)  # authenticate to PSID
         oProc.St(IO_TP.prm_575_SetSOM0)  # Set to SOM 0
         SOM_value = self.GetSOM()
         if SOM_value != '00':
            ScrCmds.raiseException(10158,"SOM miscompare.  Drive returned:  %s    Expected '00' value"%SOM_value)
         objMsg.printMsg("Drive will ship in SOM value of:  %s"%SOM_value)
      oProc.St(IO_TP.prm_575_CloseSession)	        # close session

      self.SEDUnlockDiagUDS(UDSskip=1)  # Temporary Unlock DIAG port to continue testing
      self.check_setD_SENSE()  # Need for SED drives that require D_SENSE


   def getFWLockPort(self):
      '''This function will return the state of the Firmware Locking Port.  If
      the port locking byte is '00', the function returns the port is
      'UNLOCKED'.  Else the port is considered 'LOCKED'.
      '''

      import string

      if testSwitch.virtualRun:
         return str(self.dut.driveConfigAttrs.get('DLP_SETTING',[0,'NA'])[1]).strip()

      self.handlersandAuthenticate(authent = "ON")  # Authenticate also required
      oProc.St(IO_TP.prm_575_GetFWUnlockTable)          # Get FW unlock table
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display Read Buffer offset 40h'},PARAMETER_2=(0x0040,),PARAMETER_3=(0x0040,))
      bufferData = DriveVars["Buffer Data"]
      objMsg.printMsg("Buffer data:  %s"%bufferData)
      portlocked_offset = string.find(bufferData,"506F72744C6F636B6564")  # Search for "PortLocked" value
      objMsg.printMsg("PortLocked found at offset: %04x"%portlocked_offset)
      if portlocked_offset == -1:
         ScrCmds.raiseException(14886,"-1 value returned for portlocked_offset.  Should not happen.")
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display Read Buffer 90h'},PARAMETER_3=(0x0090,))
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get PortLocked byte value'},PARAMETER_2=((portlocked_offset/2)+ 10 + 0x0040,),PARAMETER_3=(0x0001,))
      portlocked_byte = DriveVars["Buffer Data"]
      objMsg.printMsg("portlocked_byte: %s"%portlocked_byte)
      oProc.St(IO_TP.prm_575_CloseSession)	        # close session
      if portlocked_byte == "00":
         return("UNLOCKED")
      else:
         return("LOCKED")


   def handlersandAuthenticate(self, authent = "ON"):
      '''This function contains the commands for handler and to Authenticate
      if needed.
      '''

      from SelfEncryption import SED
      oSED = SED()

      if self.FW_PLATFORM_FAM == 'DELLA':
         self.MSID_PWD_TYPE = 0xE
         self.SYMK_KEY_TYPE = 2
      elif self.FW_PLATFORM_FAM == 'CANNON':
         self.MSID_PWD_TYPE = 0xD
         self.SYMK_KEY_TYPE = 1

      RegisterResultsCallback(oSED.customHandler,[32,33,34,35,37,38,39,43,44,45,46,47,48,49,50,51,52,53,54],useCMLogic=0)
      RegisterResultsCallback(oSED.customInitiatorHandler, range(80,85), useCMLogic=1)
      oProc.St(IO_TP.prm_575_SetSSC1MT, SYMK_KEY_TYPE=self.SYMK_KEY_TYPE)

      if authent == "ON":
         oProc.St(IO_TP.prm_575_StartAdminSession)  # start admin session
         oProc.St(IO_TP.prm_575_AuthenticateToMakerSymK,PASSWORD_TYPE=self.MSID_PWD_TYPE)  # authenticate to maker sym k
         oProc.St(IO_TP.prm_575_FDE_GetPSIDfromFIS)  # Get PSID from FIS
         oProc.St(IO_TP.prm_575_FDE_AuthPSID)  # authenticate to PSID
         oProc.St(IO_TP.prm_575_GetMsidFromDrive)  # Get MSID from Drive
         oProc.St(IO_TP.prm_575_AuthenticateToMSID)  # authenticate to MSID
         oProc.St(IO_TP.prm_575_AuthenticateToSID)  # authenticate to SID


   def SEDUnlockDiagUDS(self, UDSskip = 0):
      '''This function contains the commands to unlock the DIAG and UDS ports to allow for MFG
      commands to be used while the drive remains in USE state.  The USD set can
      be skipped by passing in USDskip to something other than 0, default.
      '''

      objMsg.printMsg("Unlock DIAG and UDS port process")
      self.handlersandAuthenticate()
      oProc.St(IO_TP.prm_575_UnlockDiagPort)  # Unlock Diag port
      if UDSskip == 0:
         oProc.St(IO_TP.prm_575_UnlockUdsPort)  # Unlock UDS port
      oProc.St(IO_TP.prm_575_CloseSession)  # close session


   def GetSOM(self):
      '''This function will get the SOM (Security Operating Mode) from a drive.
      It assumes the session is already open and will not close the session.
      '''
      oProc.St(IO_TP.prm_575_FDE_GetSOM)
      oProc.St(IO_TP.prm_508_Disp_RBuff, PARAMETER_1 = 0x8005, PARAMETER_2=(0x003A,),PARAMETER_3=(0x0001,))  # Get SOM state, offset 58
      bufData = DriveVars["Buffer Data"]
      objMsg.printMsg("SOM value is:  %s"%bufData)
      return bufData


   def set_verifyCust_TestName(self):
      '''This function will set and/or verify the features required for various
      settings of the CFG, CUST_TESTNAME, CUST_TESTNAME_2 and CUST_TESTNAME_3
      CCA.  Upon successful completion of a function the Seatrack attributes
      are written.  Not all customer unique test features are set during the
      CCV process, but the ones that are will be done here.

      The features currently supported by this function for CFG are:
         Fujitsu config code Write and Verify

      The features currently supported by this function for CUST_TESTNAME are:
         DE1 = Dell SAS PPID Write and Verify
      Note:  This attribute can have a string of customer unique tests.
      Each will be 3 characters in length, alphabetical in a continuous string.
      As example:  'DE1FU1PL1'

      The features currently supported by this function for CUST_TESTNAME_2 are:
         IB1 = IBM Inquiry FRU value and Date of Manufacturing verify
         OR1 = Oracle (SunMicro) Final Assembly Date Requirement

      The features currently supported by this function for CUST_TESTNAME_3 are:
         PL1 = Maximum Plist requirement
         CD1 = Change Definition Command
      '''
      from CustUniq_IF3 import oCDell_PPID

      testHeader("Customer Unique Testing Features")
      cfg_code_att = str(self.dut.driveConfigAttrs.get('CFG',[0,'NA'])[1]).strip()
      cust_testname_att  = str(self.dut.driveConfigAttrs.get('CUST_TESTNAME',[0,'NA'])[1]).strip()
      cust_testname_att2 = str(self.dut.driveConfigAttrs.get('CUST_TESTNAME_2',[0,'NA'])[1]).strip()
      cust_testsup2_att2 = str(self.dut.driveConfigAttrs.get('CUST_TESTSUP_2',[0,'NA'])[1]).strip()
      cust_testname_att3 = str(self.dut.driveConfigAttrs.get('CUST_TESTNAME_3',[0,'NA'])[1]).strip()
      cust_testsup3_att3 = str(self.dut.driveConfigAttrs.get('CUST_TESTSUP_3',[0,'NA'])[1]).strip()

      if testSwitch.virtualRun:
         self.dut.driveattr['CFG'] = cfg_code_att
         self.dut.driveattr['CUST_TESTNAME'] = cust_testname_att
         self.dut.driveattr['CUST_TESTNAME_2'] = cust_testname_att2
         self.dut.driveattr['CUST_TESTSUP_2'] = cust_testsup2_att2
         self.dut.driveattr['CUST_TESTNAME_3'] = cust_testname_att3
         self.dut.driveattr['CUST_TESTSUP_3'] = cust_testsup3_att3
         return

      #Fujitsu config code Write and Verify
      if cfg_code_att != 'NA':
         testHeader("Fujitsu config code Write and Verify")
         self.Fujitsu_ConfigCode(cfg_code_att)
         self.dut.driveattr['CFG'] = cfg_code_att

      #Dell SAS PPID Write and Verify
      if 'DE1' in cust_testname_att:
         testHeader("Dell PPID Write and Verify")
         ### Even though the Test 595 is correctly set to write all attributes, it will not
         ### correctly write the "PREAMP_LOT_1" to both locations (274 and 586).
         ### It will do one, but not the other.  But STP160 does not have this issue.
         ### To work around this for now, redo the CustomerInfo, which will write the 274
         ### PREAMP_LOT_1
         oCDell_PPID.CustomerInfo(forcegetPPID='ON') # Verifies and write DELL PPID type attributes
         oCDell_PPID.verify_DEll_VPD_DC() # Verifies Dell PPID data
         updateCUST_TESTNAME('DE1')

      #Change Definition Command
      if cust_testname_att3 == 'CD1':
         testHeader("Change Definition Command")
         self.Customer_change_def(cust_testsup3_att3)
         self.dut.driveattr['CUST_TESTNAME_3'] = cust_testname_att3
         self.dut.driveattr['CUST_TESTSUP_3'] = cust_testsup3_att3

      #IBM Default Inquiry FRU value and Date of Manufacturing verify
      #NOTE:  The Change Definiation Command check (CD1) above should always
      #come before this one.  This is incase IBM runs with a non default
      #shipping Change Def, which will affect the FRU value
      if cust_testname_att2 == 'IB1':
         testHeader("IBM Default Inquiry FRU value and Date of Manufacturing verify")
         self.IBM_FRUandDate(cust_testsup2_att2)
         self.dut.driveattr['CUST_TESTNAME_2'] = cust_testname_att2
         self.dut.driveattr['CUST_TESTSUP_2'] = cust_testsup2_att2

      #Oracle (SunMicro) Final Assembly Date Requirement
      if cust_testname_att2 == 'OR1':
         testHeader("Oracle (SunMicro) Final Assembly Date Requirement")
         self.Oracle_FinalAssembly()
         self.dut.driveattr['CUST_TESTNAME_2'] = cust_testname_att2
         self.dut.driveattr['CUST_TESTSUP_2'] = cust_testsup2_att2

      #Maximum Plist requirement
      if cust_testname_att3 == 'PL1':
         testHeader("Maximum Plist requirement")
         objMsg.printMsg("Test 530 PList Limit set to:  %s"%cust_testsup3_att3)
         max_value = long(cust_testsup3_att3)
         max_value_p = int(max_value/10)
         oProc.St(IO_TP.prm_530_Check_PList_size,{'prm_name':'P-list (sector mode) limit = ' + str(max_value)},MAX_DEFECTIVE_SECTORS=max_value_p)
         self.dut.driveattr['CUST_TESTNAME_3'] = cust_testname_att3
         self.dut.driveattr['CUST_TESTSUP_3'] = cust_testsup3_att3


   def getModelNumber(self):
      '''This function gets the drive Model Number, which is defined as a
      combination of the VENDOR INDENTIFICATION (bytes 8-15) and the PRODUCT
      INDENTIFICATION (bytes 16-31) fields from Standard Inquiry.
      '''

      testHeader("Get Model Number")
      CCAmodelnum = str(self.dut.driveConfigAttrs['CUST_MODEL_NUM'][1]).strip()
      if testSwitch.virtualRun:
         self.dut.driveattr["CUST_MODEL_NUM"] = CCAmodelnum
      else:
         DRVmodelnum = self.get_ModelNumbers()
         self.dut.driveattr["CUST_MODEL_NUM"] = '[%s]' % DRVmodelnum
         self.dut.driveattr["CUST_MODEL_NUM2"] = '?'  # In case drive used to be SATA

   def SecFLASHcheck(self):
      '''This function is only used on drives that have dual FLASH containers.  This will be drives
      that use the Kahu or KahuPlus interface controler chip.  This test is used to verify that the
      primary and secondary FLASH containers are the same.
      '''

      testHeader("Dual Flash Container Check")
      # Get listing of all pages supported from Log page 0
      oProc.St(IO_TP.prm_638_StandardInquiryData,{'prm_name':'Read VPD page C3'},PARAMETER_0=(0x1201,),PARAMETER_1=(0xC300,),PARAMETER_2=(0x3000,))
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display 0-30h Inquiry bytes'},PARAMETER_3=(0x0030,))
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Get byte 30 (Interface Chip)'},PARAMETER_2=(0x001e,),PARAMETER_3=(0x0001,))
      bufferData = DriveVars["Buffer Data"]
      objMsg.printMsg("Interface Chip byte 30 value is:  %s"%bufferData)
      if (bufferData != "13") and (bufferData != "1B") :
         objMsg.printMsg("This drive type does not have a secondary FLASH container")
         return
      else:
         if (bufferData == "13"):
            objMsg.printMsg("Kahu type drive found.")
         if (bufferData == "1B"):
            objMsg.printMsg("KahuPlus type drive found.")


      oProc.St(IO_TP.prm_638_PlatformFactoryUnlock)	# Platform Unlock Command
      oProc.St(IO_TP.prm_638_ReadFLASHCAP,PARAMETER_2=(0x0301,))  # Read FLASH CAP, get byte count
      oProc.St(IO_TP.prm_508_Disp_RBuff,PARAMETER_2=(0x0004,),PARAMETER_3=(0x0004,))
      bufferData = DriveVars["Buffer Data"]
      CAP_bytes = "%s%s%s%s%s%s%s%s"%(bufferData[6],bufferData[7],bufferData[4],bufferData[5],bufferData[2],bufferData[3],bufferData[0],bufferData[1])
      C_byte_h = int("0x"+"%s%s%s%s"%(bufferData[6],bufferData[7],bufferData[4],bufferData[5]),16)
      C_byte_l = int("0x"+"%s%s%s%s"%(bufferData[2],bufferData[3],bufferData[0],bufferData[1]),16)

      oProc.St(IO_TP.prm_638_ReadFLASHCAP,{'prm_name':'Read FLASH SAP'},PARAMETER_2=(0x0304,))  # Read FLASH SAP, get byte count
      oProc.St(IO_TP.prm_508_Disp_RBuff,PARAMETER_2=(0x0004,),PARAMETER_3=(0x0004,))
      bufferData = DriveVars["Buffer Data"]
      SAP_bytes = "%s%s%s%s%s%s%s%s"%(bufferData[6],bufferData[7],bufferData[4],bufferData[5],bufferData[2],bufferData[3],bufferData[0],bufferData[1])
      S_byte_h = int("0x"+"%s%s%s%s"%(bufferData[6],bufferData[7],bufferData[4],bufferData[5]),16)
      S_byte_l = int("0x"+"%s%s%s%s"%(bufferData[2],bufferData[3],bufferData[0],bufferData[1]),16)

      oProc.St(IO_TP.prm_638_ReadFLASHCAP,{'prm_name':'Read FLASH RAP'},PARAMETER_2=(0x0300,))  # Read FLASH RAP, get byte count
      oProc.St(IO_TP.prm_508_Disp_RBuff,PARAMETER_2=(0x0004,),PARAMETER_3=(0x0004,))
      bufferData = DriveVars["Buffer Data"]
      RAP_bytes = "%s%s%s%s%s%s%s%s"%(bufferData[6],bufferData[7],bufferData[4],bufferData[5],bufferData[2],bufferData[3],bufferData[0],bufferData[1])
      R_byte_h = int("0x"+"%s%s%s%s"%(bufferData[6],bufferData[7],bufferData[4],bufferData[5]),16)
      R_byte_l = int("0x"+"%s%s%s%s"%(bufferData[2],bufferData[3],bufferData[0],bufferData[1]),16)

      oProc.St(IO_TP.prm_638_ReadFLASHCAP,{'prm_name':'Read FLASH ALL'},PARAMETER_2=(0x0115,),REPORT_OPTION=(0x0001,),SECTOR_SIZE=0x0200,TRANSFER_LENGTH=0x0400,TRANSFER_MODE=1,CMD_DFB_LENGTH=16)
      oProc.St(IO_TP.prm_508_Copy_RBuff_to_WBuff,PARAMETER_1=(0x0806,),PARAMETER_3=(0x0000,))  # Copy Read to Write buffer

      ##No drive should ever fail this tests, since the exact copy of FLASH should be in both Write and Read Buffers
      oProc.St(IO_TP.prm_508_CompareW2RBuffer,{'prm_name':'Compare Read to Write'},PARAMETER_1=(0x0808,),PARAMETER_3=(0x0000,))
      ##oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'Display Entire FLASH contents'},PARAMETER_1=(0x0805,),PARAMETER_3=(0x0000,),timeout=3600,)


      # Find valid directory in either first or second container
      # Primary flash begins at byte 0 and secondary at 0x40000.  The offset to the table index is 0x20.
      dir_FLASH = 0x00000  # first container FLASH offset
      h_offset = dir_FLASH >> 16
      l_offset = dir_FLASH & 0xffff
      oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'Dump FLASH directory'},PARAMETER_1=(0x8005,),PARAMETER_2=l_offset,PARAMETER_3=(0x0050,),PARAMETER_4=h_offset)
      oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'Get byte 0 of FLASH directory'},PARAMETER_1=(0x8005,),PARAMETER_2=l_offset,PARAMETER_3=(0x0001,),PARAMETER_4=h_offset)
      index_value = DriveVars["Buffer Data"]
      if index_value == "FF":
         objMsg.printMsg("Invalid FLASH directory in first container.  Trying second container.")
         dir_FLASH = 0x40000  # second container FLASH offset
         h_offset = dir_FLASH >> 16
         l_offset = dir_FLASH & 0xffff
         oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'Dump FLASH directory'},PARAMETER_1=(0x8005,),PARAMETER_2=l_offset,PARAMETER_3=(0x0050,),PARAMETER_4=h_offset)
         oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'Get byte 0 of FLASH directory'},PARAMETER_1=(0x8005,),PARAMETER_2=l_offset,PARAMETER_3=(0x0001,),PARAMETER_4=h_offset)
         index_value = DriveVars["Buffer Data"]
         if index_value == "FF":
            objMsg.printMsg("Invalid FLASH directory in second container as well.  This should not occur.  No FLASH directory found.")
            ScrCmds.raiseException(14886,"No valid FLASH directory found.")

      # Get directory offset
      dir_FLASH = dir_FLASH + 28  # temporarily Add 28 bytes to base value to locate directory offset value
      h_offset = dir_FLASH >> 16
      l_offset = dir_FLASH & 0xffff
      oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'Read Buffer'},PARAMETER_1=(0x8005,),PARAMETER_2=l_offset,PARAMETER_3=(0x0001,),PARAMETER_4=h_offset)
      bufferData = DriveVars["Buffer Data"]
      dir_offset = int("0x"+"%s%s"%(bufferData[0],bufferData[1]),16)
      dir_FLASH = dir_FLASH - 28  # remove temporary offset value, to get back to base value

      CAP_index = "04"
      SAP_index = "05"
      RAP_index = "06"
      byte_index = 0
      index_value = "FF"
      while index_value != "00":  # "00" is directory termination
         byte_offset = dir_FLASH + dir_offset + byte_index
         h_offset = byte_offset >> 16
         l_offset = byte_offset & 0xffff
         oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'Read Buffer'},PARAMETER_1=(0x8005,),PARAMETER_2=l_offset,PARAMETER_3=(0x0001,),PARAMETER_4=h_offset)
         index_value = DriveVars["Buffer Data"]
         if index_value == CAP_index:
            objMsg.printMsg("CAP_index found")
            oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'Read Buffer'},PARAMETER_1=(0x8005,),PARAMETER_2=l_offset,PARAMETER_3=(0x0004,),PARAMETER_4=h_offset)
            bufferData = DriveVars["Buffer Data"]
            CAP_offset = "%s%s%s%s%s%s"%(bufferData[6],bufferData[7],bufferData[4],bufferData[5],bufferData[2],bufferData[3])
            C_off_h = int("0x"+'%s%s'%(bufferData[6],bufferData[7]),16)
            C_off_l = int("0x"+'%s%s%s%s'%(bufferData[4],bufferData[5],bufferData[2],bufferData[3]),16)
         if index_value == SAP_index:
            objMsg.printMsg("SAP_index found")
            oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'Read Buffer'},PARAMETER_1=(0x8005,),PARAMETER_2=l_offset,PARAMETER_3=(0x0004,),PARAMETER_4=h_offset)
            bufferData = DriveVars["Buffer Data"]
            SAP_offset = "%s%s%s%s%s%s"%(bufferData[6],bufferData[7],bufferData[4],bufferData[5],bufferData[2],bufferData[3])
            S_off_h = int("0x"+'%s%s'%(bufferData[6],bufferData[7]),16)
            S_off_l = int("0x"+'%s%s%s%s'%(bufferData[4],bufferData[5],bufferData[2],bufferData[3]),16)
         if index_value == RAP_index:
            objMsg.printMsg("RAP_index found")
            oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'Read Buffer'},PARAMETER_1=(0x8005,),PARAMETER_2=l_offset,PARAMETER_3=(0x0004,),PARAMETER_4=h_offset)
            bufferData = DriveVars["Buffer Data"]
            RAP_offset = "%s%s%s%s%s%s"%(bufferData[6],bufferData[7],bufferData[4],bufferData[5],bufferData[2],bufferData[3])
            R_off_h = int("0x"+'%s%s'%(bufferData[6],bufferData[7]),16)
            R_off_l = int("0x"+'%s%s%s%s'%(bufferData[4],bufferData[5],bufferData[2],bufferData[3]),16)
         byte_index = byte_index+4

      # Need to shift due to the 8 byte header that is prior to the data.
      CAP_plus = (C_off_h << 16) + C_off_l + 8  # Shift 8 bytes due to header
      C_off_h = CAP_plus >> 16
      C_off_l = CAP_plus & 0xffff
      SAP_plus = (S_off_h << 16) + S_off_l + 8  # Shift 8 bytes due to header
      S_off_h = SAP_plus >> 16
      S_off_l = SAP_plus & 0xffff
      RAP_plus = (R_off_h << 16) + R_off_l + 8  # Shift 8 bytes due to header
      R_off_h = RAP_plus >> 16
      R_off_l = RAP_plus & 0xffff


      objMsg.printMsg("FLASH directory found at:  %08x"%dir_FLASH)
      objMsg.printMsg("---------- Offset values with the 8 byte header --------")
      objMsg.printMsg("CAP h-l:  %04x%04x  "%(C_off_h,C_off_l))
      objMsg.printMsg("SAP h-l:  %04x%04x  "%(S_off_h,S_off_l))
      objMsg.printMsg("RAP h-l:  %04x%04x  "%(R_off_h,R_off_l))
      objMsg.printMsg("CAP bytes h-l:  %04x%04x  "%(C_byte_h,C_byte_l))
      objMsg.printMsg("SAP bytes h-l:  %04x%04x  "%(S_byte_h,S_byte_l))
      objMsg.printMsg("RAP bytes h-l:  %04x%04x  "%(R_byte_h,R_byte_l))


      p4a = C_off_h  # Primary container offset h
      p4b = C_off_h + 0x4  # Secondary container offset 0x40000
      try:
         p1 = (C_byte_h << 8) | 0x0008  # Test 508 Compare W-R buffer
         oProc.St(IO_TP.prm_508_CompareW2RBuffer,{'prm_name':'CAP container check'},PARAMETER_1=p1,PARAMETER_2=C_off_l,PARAMETER_3=C_byte_l,PARAMETER_4=p4a,PARAMETER_5=C_off_l,PARAMETER_6=p4b)
      except:
         p1 = (C_byte_h << 8) | 0x0005  # Test 508 Display R buffer
         oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'CAP 1st container display'},PARAMETER_1=p1,PARAMETER_2=C_off_l,PARAMETER_3=C_byte_l,PARAMETER_4=p4a)
         oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'CAP 2nd container display'},PARAMETER_1=p1,PARAMETER_2=C_off_l,PARAMETER_3=C_byte_l,PARAMETER_4=p4b)
         ScrCmds.raiseException(14882,"Primary CAP does not match Secondary CAP")


      p4a = S_off_h  # Primary container offset h
      p4b = S_off_h + 0x4  # Secondary container offset 0x40000
      try:
         p1 = (S_byte_h << 8) | 0x0008  # Test 508 Compare W-R buffer
         oProc.St(IO_TP.prm_508_CompareW2RBuffer,{'prm_name':'SAP container check'},PARAMETER_1=p1,PARAMETER_2=S_off_l,PARAMETER_3=S_byte_l,PARAMETER_4=p4a,PARAMETER_5=S_off_l,PARAMETER_6=p4b)
      except:
         p1 = (S_byte_h << 8) | 0x0005  # Test 508 Display R buffer
         oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'SAP 1st container display'},PARAMETER_1=p1,PARAMETER_2=S_off_l,PARAMETER_3=S_byte_l,PARAMETER_4=p4a)
         oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'SAP 2nd container display'},PARAMETER_1=p1,PARAMETER_2=S_off_l,PARAMETER_3=S_byte_l,PARAMETER_4=p4b)
         ScrCmds.raiseException(14884,"Primary SAP does not match Secondary SAP")


      p4a = R_off_h  # Primary container offset h
      p4b = R_off_h + 0x4  # Secondary container offset 0x40000
      try:
         p1 = (R_byte_h << 8) | 0x0008  # Test 508 Compare W-R buffer
         oProc.St(IO_TP.prm_508_CompareW2RBuffer,{'prm_name':'RAP container check'},PARAMETER_1=p1,PARAMETER_2=R_off_l,PARAMETER_3=R_byte_l,PARAMETER_4=p4a,PARAMETER_5=R_off_l,PARAMETER_6=p4b)
      except:
         p1 = (R_byte_h << 8) | 0x0005  # Test 508 Display R buffer
         oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'RAP 1st container display'},PARAMETER_1=p1,PARAMETER_2=R_off_l,PARAMETER_3=R_byte_l,PARAMETER_4=p4a)
         oProc.St(IO_TP.prm_508_Disp_RBuff,{'prm_name':'RAP 2nd container display'},PARAMETER_1=p1,PARAMETER_2=R_off_l,PARAMETER_3=R_byte_l,PARAMETER_4=p4b)
         ScrCmds.raiseException(14883,"Primary RAP does not match Secondary RAP")

      objMsg.printMsg("CAP-RAP-SAP Primary and Secondary Containers are identical.")


   def Clear_SMART_hightemp(self):
      '''This function is used clear the Hottest Temperature Measurement prior to shipment.
      The infomraion is found in SMART file 53, page 117h, bytes 10,11 (decimal).
      DITs command 0x163, bit 3 will be set to clear this data.  The value will be cleared
      but, you will not be able to view the change.  You can view the effect of the command
      on a subsequent run using the commands that are commented out below.
      '''

      ##oProc.St(IO_TP.prm_508_WRT_bytes_to_WBuff, {'prm_name':'Write 8 bytes to WBuff'}, PARAMETER_2=(0x0000,), PARAMETER_7=(0x0600,), PARAMETER_8=(0x0008,),PARAMETER_9=(0xfff0,),PARAMETER_10=(0x0304,))  # Write bytes to set up Log Unlock
      ##oProc.St(IO_TP.prm_508_WRT_bytes_to_WBuff, {'prm_name':'Write 8 bytes to WBuff'}, PARAMETER_2=(0x0008,), PARAMETER_7=(0x3397,), PARAMETER_8=(0x0000,),PARAMETER_9=(0x0000,),PARAMETER_10=(0x0000,))  # Write bytes to set up Log Unlock, offset 8
      ##oProc.St(IO_TP.prm_538_GetLogPage,{'prm_name':'Log Page Select'},COMMAND_WORD_1=(0x4C00,),COMMAND_WORD_2=(0x4000,),COMMAND_WORD_3=(0x0000,),COMMAND_WORD_4=(0x0000,),COMMAND_WORD_5=(0x0C00,),COMMAND_WORD_6=(0x0000,))  #
      ##oProc.St(IO_TP.prm_538_GetLogPage,{'prm_name':'Get Log page 117h'},TRANSFER_OPTION=(0x0001,),SUPRESS_RESULTS=(0x0000,),COMMAND_WORD_1=(0x4D00,),COMMAND_WORD_2=(0x7000,),COMMAND_WORD_3=(0x0001,),COMMAND_WORD_4=(0x1700,),COMMAND_WORD_5=(0x1A00,),COMMAND_WORD_6=(0x0000,))  # Get Log page 117h

      testHeader("Clear SMART HIGH temperature value")
      oProc.St(IO_TP.prm_638_PlatformFactoryUnlock)	# Unlock for Platform
      oProc.St(IO_TP.prm_638_ManufactureControlInitialize,PARAMETER_2=(0x0800,))	# Clear HIGH SMART Temp


   def SpinUp(self,UnlockforSED = "ON"):
      '''This function is used to powerup and spinup the drive, depending on I/O type.
      For SED drives in "USE" mode, if UnlockforSED = "ON" then will unlock the
      DIAG and UDS ports after the spin up, else that is skipped.
      '''

      testHeader("Spin Up")
      if testSwitch.virtualRun:
         return
      if objDut.drvIntf in ['FC','FCV']:
         oProc.St(IO_TP.prm_608_PortLoginA)  # Clears LIP on Port A for login
         oProc.St(IO_TP.prm_608_PortLoginB)  # Clears LIP on Port B for login
         oProc.St(IO_TP.prm_517_RequestSense_Init_Check)
      elif objDut.drvIntf in ['SS','AS','NS','SATA','SAS']:
         (ident_field) = self.get_ModelNumbers()  # Pre-spin up model numbers
         oProc.St(IO_TP.prm_517_RequestSense)
         oProc.St(IO_TP.prm_517_RequestSense_Init_Check)
         (ident_field1) = self.get_ModelNumbers()  # Post-spin up model numbers
         objMsg.printMsg("Pre-spinup model number:   %s"%ident_field)
         objMsg.printMsg("Post-spinup model number:  %s"%ident_field1)
         if ident_field != ident_field1:
            objMsg.printMsg("***** Pre and Post Spinup model numbers do not match. *****")
            ScrCmds.raiseException(10150,"Pre and Post Spinup model numbers do not match.")
      else:
         ScrCmds.raiseException(11107,'Drive type is not supported on this Line')
      oProc.St(IO_TP.prm_514_StdInquiryData)
      oProc.St(IO_TP.prm_514_StdInquiryData,TEST_FUNCTION=(0x9000,))  # Port B
      oProc.St(IO_TP.prm_514_FwServoInfo)  # FW, Servo Ram, Servo Rom Revs
      oProc.St(IO_TP.prm_517_RequestSense_Ready_Check)  # Checks for drive not ready conditions
      ScriptPause(20)  # Ensure drive is ready

      if (self.getLifeState() == "USE"):
         if UnlockforSED == "ON":
            self.SEDUnlockDiagUDS()  # If SED drive in "USE" mode, unlock DIAG port
            self.check_setD_SENSE()
      else:
         self.check_setD_SENSE()


   def PortBypassCheck(self):
      '''This function is used to verify the port bypass feature functions.
      '''

      testHeader("FC Port Bypass Check")
      if objDut.drvIntf in ['FC','FCV']:
         objMsg.printMsg("Port Bypass Test - FC only - - - - - - - - - -")
         self.WR_powerCycle(True)  # Voltage Margins to catch marginal drives
         self.SpinUp()
         oProc.St(IO_TP.prm_605_PortBypassTest)  # Both ports are checked automatically
         self.WR_powerCycle()  # Need to reset the voltage margins
         self.SpinUp()
      else:
         objMsg.printMsg("Bypass Test - This is not a FC drive - - - - - - - - - -")


   def get_ReadCapacityInfo(self):
      '''This function is used to return the Last Logical Block, block size and
      Protection Information of a drive from the 16 byte Read Capacity Command.
      '''

      import struct
      import binascii

      oProc.St(IO_TP.prm_538_ReadCapacity,COMMAND_WORD_1=(0x9E10,),COMMAND_WORD_7=(0x0020,),TRANSFER_LENGTH=(0x0020,))  # 16 byte Read Capacity
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Display Read Buffer 20h'},PARAMETER_3=(0x0020,))
      bufferData = DriveVars["Buffer Data"]
      y = binascii.unhexlify(bufferData)
      LLB, blockSize, Prot = struct.unpack(">QLB",y[:13])
      return (LLB,blockSize,Prot)


   def get_ModelNumbers(self):
      '''This function is used return the combined fields of the Vendor Identification Field, bytes 8-15
      and the Product Identification Field es 16-31 an of Standard Inquiry.
      '''

      import struct
      import binascii
      import string

      oProc.St(IO_TP.prm_638_StandardInquiryData,BYPASS_WAIT_UNIT_RDY=(0x0001,))	# Read Standard Inquiry Data
      oProc.St(IO_TP.prm_508_Disp_RBuff, {'prm_name':'Identify Fields'},PARAMETER_2=(0x0008,),PARAMETER_3=(0x0018,))  # Get both Vendor and Product Identification Fields, offset 08h, 0x18h bytes
      bufferData = DriveVars["Buffer Data"]
      ident_field = binascii.unhexlify(bufferData)  # make ASCII

      return (ident_field)


   def check_setD_SENSE(self):
      '''D_SENSE handling for drives that require D_SENSE, but do not have it
      turned on, as initiator will fail with 11107 in that situation.
      '''

      try:
         oProc.St(IO_TP.prm_538_RequestSense,TRANSFER_OPTION=(0x0000,))  # D_SENSE check
      except ScriptTestFailure, (failuredata):
         if failuredata[0][2] in [11107]:
            #If T538 failed for EC11107, need to set D_Sense for 34-LBA space in Control Mode Page
            oProc.St(IO_TP.prm_507_D_Sense) #Always skip failing for 11107
            oProc.St(IO_TP.prm_538_RequestSense,TRANSFER_OPTION=(0x0000,))  # Must have xfer option set to 0
         else:
            raise


   def WR_powerCycle(self, margined=False):
      '''This is a wrapper function to handle differences of TCO and LCO
      powerCycle script function.
      '''

      if margined:
         volt5 = 4700; volt12 = 12720
      else:
         volt5 = 5000; volt12 = 12000
      if testSwitch.FE_0181878_007523_CCA_CCV_PROCESS_LCO:
         self.dut.TCGComplete = True  # prevent powercycle functions from unlocking drive
         objPwrCtrl.powerCycle(volt5,volt12,10,30, ataReadyCheck=False)
      else:
         objPwrCtrl.powerCycle(volt5,volt12,20,30)


################################################################################
class CCVFailProc(CState):
   """Put in your fail sequence code in this class' run() method"""
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   #----------------------------------------------------------------------------
   def run(self):
      import Utility
      oUtil = Utility.CUtility()

      objMsg.printMsg('<<< Test failure Handling >>>')
      if not testSwitch.virtualRun:
         objMsg.printMsg("="*80)
         objMsg.printMsg("Part Number:  %s"%objDut.partNum)
         objMsg.printMsg("Serial Number:  %s"%HDASerialNumber)
         objMsg.printMsg("*"*80)

      if testSwitch.virtualRun:
         self.exitStateMachine() # this will throw exception to be handled by top level code in Setup.py

      self.dut.driveattr['FIN2_FULL_TEST'] = 'NONE'
      try:
         tmpFailData = oUtil.copy(self.dut.failureData)  #Because we want a value copy and it has to be deep/nested
         noFailData = 0
      except:
         noFailData = 1
      SetFailSafe()
      try:
         oProc.St(IO_TP.prm_504_SenseAndDriveData)	# Display Sense, Last Cmd, Cyl, Hd, Sec, LBA
      except:
         pass
      ClearFailSafe()
      if noFailData == 0:
         self.dut.failureData = tmpFailData
      try:
         oProc.St(IO_TP.prm_538_SpinDown)	# Spin Down
         DriveOff(10)
      except:
         DriveOff(10)
      """
      We want to raise an exception below so that the calling method (Setup.py) can report error to
      host and do other standard failure actions like run STPGPD, send parametric data, run DBLog etc.
      NOTE: It is possible to simply handle failure at this level, if that is what you want,
            then comment out the following line and add your failure handling code.
      """
      self.exitStateMachine() # this will throw exception to be handled by top level code in Setup.py



def testHeader(testname = ''):

   if testSwitch.virtualRun:
      hmsg = "*****Virtual Run*****" * 3
   else:
      hmsg = "-" * 60
   objMsg.printMsg("CCV--" + testname + "  " + hmsg)



################ Force failure stopper ########################################
#      ScrCmds.raiseException(11075,"MFG Process FORCE FAILURE")
################ Force failure stopper ########################################
