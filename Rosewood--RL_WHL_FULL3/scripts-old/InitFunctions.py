#-----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                     #
#-----------------------------------------------------------------------------------------#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $file:$ CIOClass.py
# $Revision: #1 $
# $Date: 2016/05/05 $ 11/01/2006
# $Author: chiliang.woo $ Sharon Wang
# $Source:$
# Level:
#-----------------------------------------------------------------------------------------#
from Constants import *
from Drive import objDut
dut = objDut
from PowerControl import objPwrCtrl
import ScrCmds
from TestParamExtractor import TP
import MessageHandler as objMsg
from Process import CProcess
oProc = CProcess()

# Pre-format the DTD block with base patterns
# DTDformat is set up as follows:  [[start, end, value], ...]
# 'start' and 'end' indicate start and end bytes (inclusive) within the DTD block to write the data pattern given by 'value'

DTDformat=[[ 0 , 2047, 0x20],
           [ 258, 511, 0xFF],
           [ 762, 1023, 0xFF],
           [ 1522, 1535, 0xFF],
           [ 1794, 2047, 0xFF],
           [ 0, 0, 0xF0],
           [ 520, 520, 0xF0],
           [ 1280, 1280, 0xF0],
           [ 1536, 1536, 0x40]]

RIGHT = 1
DTDdictionary={'TMS FIRMWARE':(2),  # NOT FIXED: this data is set up in STPGPD in tests 301,159,514,544
            'SERVO_CODE':(2),       # NOT FIXED: this data is set up in STPGPD in tests 301,159,514,544
            'FIRMWARE':(18),        # NOT FIXED: this data is set up in STPGPD by the SCNDATA,tests 301,159,514,544
            'SCSI_CODE':(18),       # NOT FIXED: this data is set up in STPGPD by the SCNDATA,tests 301,159,514,544
            'CD_1':(34),
            'PCB_PN':(34),
            'PCBA_PART_NUM':(34),
            'PCB REV':(50),
            'PCBA_REV':(50),
            'CD_1_2':(50),
            'PCB SN':(66),
            'PCBA_SERIAL_NUM':(66),
            'CD_1_SER':(66),
            'PCB DATECODE':(82),
            'PCBA_DATECODE':(82),
            'CD_1_BLD':(82),
            'DRAM_VENDOR':(242),
            'PREAMP_LOT_1':(274,32,0,RIGHT),
            'CUST_SERIAL':(306),
            'CUST_REV':(326),
            'PPID':(306),
            'PART_NUM':(522),
            'HDA PN':(538),
            'HDA_CODE':(538),
            'MOD_PART':(538),
            'HSA_CODE':(554,1),
            'HSA_SERIAL_NUM':(554,10,0,RIGHT),
            'EB SN':(554,10,0,RIGHT),
            'EBLOCK':(554,10,0,RIGHT),
            'MOTOR_LOT':(570,6,1),
            'PREAMP_LOT_1':(586),
            'PREAMP_LOT_2':(602),
            'HEAD_LOT_UP':(618),
            'HEAD_LOT_DOWN':(634),
            'HEAD_LOT_RWK1':(650),
            'HEAD_LOT_RWK2':(666),
            'HEAD_LOT_RWK3':(682),
            'HEAD_LOT_RWK4':(698),
            'HEAD_LOT_RWK5':(714),
            'HEAD_LOT_RWK6':(1730),
            'HEAD_LOT_RWK7':(1746),
            'HEAD_LOT_RWK8':(1762),
            'HEAD_LOT_RWK9':(1778),
            'HEAD_LOT_RWK10':(1794),
            'EMC_PN':(1025),
            'EMC_REV':(1040),
            'IBM_SN':(1088,6,0),
            'CUST_SN':(1086,8,0,RIGHT),
            'DISC_1_LOT':[1330],
            'DISC_2_LOT':[1346],
            'DISC_3_LOT':[1362],
            'DISC_4_LOT':[1378],
            'DISC_5_LOT':[1394],
            'DISC_6_LOT':[1410],
            'DISC_7_LOT':[1426],
            'DISC_8_LOT':[1442],
            'DISC_9_LOT':[1458],
            'DISC_10_LOT':[1282],
            'DISC_11_LOT':[1298],
            'DISC_12_LOT':[1314]}

def powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=2, driveOnly=0, spinUp=True, postSpinDelay=20,initType='IF3'):
   """
   Wrapper function to control default power on/off times and spinup
   """
   objPwrCtrl.powerCycle(set5V=set5V,set12V=set12V,offTime=offTime,onTime=onTime,driveOnly=driveOnly)

   if spinUp == True:
      for ii in range(10):
         try:
            result = SpinUp(postSpinDelay,initType=initType)
            if result == FAIL:
               ScrCmds.raiseException('Interface type "%s" is not supported in IOClass.Spinup'%dut.drvIntf)
            else: break
         except:
            objPwrCtrl.powerCycle(set5V=set5V,set12V=set12V,offTime=offTime,onTime=onTime,driveOnly=driveOnly)

def SpinUp(delay=20,initType='IF3'):
   """
   Drive spinup by interface and bad sense code checks
   """
   if dut.drvIntf in ['SS', 'SAS']:            # SAS Interface
      if initType == 'IF3':
         oProc.St(TP.prm_517_RequestSense3, {'prm_name':'Standard Request Sense - With SpinUp'},SEND_TUR_CMDS_ONLY=(0x0001,))
         oProc.St(TP.prm_517_RequestSense_SD0D_Check) # SDOD CHECK AMK
         ScriptPause(20)
         oProc.St(TP.prm_517_RequestSense_Ready_Check)  # Checks for drive not ready conditions
         oProc.St(TP.prm_514_StdInquiryData)
      else:
         oProc.St({'test_num':517},0x0010,0x291A,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=300) #Spinup and SDOD Check
         ScriptPause(delay) # wait for drive to spinup

         # Fail for drive not ready (02/04), ETF recovery failure (04/1C), power on self test failure (04/42), or SMART trip (01/5D)
         oProc.St({'test_num':517},0x0000,0x0005,0x0002,0x04FF,0x0004,0x1CFF,0x0004,0x42FF,0x0001,0x5DFF,timeout=300)

   elif dut.drvIntf in ['FC','FCV']:    # FC Interface
      if initType == 'IF3':
         oProc.St(prm_608_PortLoginA)  # Clears LIP on Port A for login
         oProc.St(prm_608_PortLoginB)  # Clears LIP on Port B for login
         oProc.St(prm_517_RequestSense_Ready_Check)  # Checks for drive not ready conditions
         oProc.St(prm_514_StdInquiryData)
      else:
         oProc.St({'test_num':608},0x0000,0x0200,0x0001,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=300) # Clears LIP on Port A for login
         oProc.St({'test_num':608},0x1000,0x0200,0x0001,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=300) # Clears LIP on Port B for Login

         # Fail for drive not ready (02/04), ETF recovery failure (04/1C), power on self test failure (04/42), or SMART trip (01/5D)
         oProc.St({'test_num':517},0x0000,0x0005,0x0002,0x04FF,0x0004,0x1CFF,0x0004,0x42FF,0x0001,0x5DFF,timeout=300)
   else:
      ScrCmds.raiseException('Interface type "%s" is not supported in SubSeq.Spinup'%dut.drvIntf)

def SetTransferRate(transferRateDict={'SS':'3.0', 'FC':'2.0'},set5V=5000,set12V=12000,onTime=2,initType='IF3'):
   """
   Set interface transfer rate in Gb/s.
   Drive power on required? SS=No, FC=Yes
   Valid Modes:   SS   = 1.5, 3.0
                  FC   = 1.0, 2.0
   """

   for interface,transferRate in transferRateDict.iteritems():  # search for interface in transferRateDict and pull transferRate
      if dut.drvIntf == interface:
         break                             # found desired transferRate
   else:
      ScrCmds.raiseException('SetTransferRate missing input for interface type "%s"'%dut.drvIntf)


   if dut.drvIntf == 'SS' or (testSwitch.FE_0127531_231166_USE_EXPLICIT_INTF_TYPE and dut.drvIntf == 'SAS'):
      decoder = {'1.5' : 1, '3.0' : 3, '6.0' : None}
   elif dut.drvIntf == 'FC':
      decoder = {'1.0' : 1, '2.0' : 2}

   else:
      ScrCmds.raiseException('Interface type "%s" is not supported in IOClass SetTransferRate'%dut.drvIntf)

   if initType == 'IF3':
      if decoder[transferRate] != None:
         oProc.St(TP.prm_533_Set_XferRate,FC_SAS_TRANSFER_RATE=(decoder[transferRate],))
   else:
      oProc.St({'test_num':533},0x8000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,decoder[transferRate],timeout=300)


   if dut.drvIntf in ('FC'):  # spinup required for FC
      DriveOn(set5V,set12V,onTime)
      SpinUp()

def AttributeUpload(initType='IF3'):
   #if testSwitch.virtualRun:
   #   return
   if initType == 'IF3':
      oProc.St(TP.prm_514_StdData)
      oProc.St(TP.prm_514_Firmware)
   else:
      oProc.St({'test_num':514},0x8000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=1800)  # FW, Servo Ram, Servo Rom Revs
      oProc.St({'test_num':514},0x8000,0x0001,0x00C0,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=1800)  # FW, Servo Ram, Servo Rom Revs

   DriveAttributes["DOWNLOAD"]  = DriveVars.get("DOWNLOAD",'?')
   DriveAttributes["PROD_REV"]  = DriveVars.get("PROD_REV",'?')
   DriveAttributes["SCSI_CODE"] = DriveVars.get("SCSI_CODE",'?')
   DriveAttributes["SERVO_CODE"]= DriveVars.get("SERVO_CODE",'?')

def CreateExceptionsList( driveAttributes):
   localAttributes={}
   for key,value in driveAttributes.items():
      if key == "EMC_PN": # IF THIS IS PRESENT, NEED TO SET 1024 TO 0X01
         i=0x01
         c=chr(i)
         localAttributes[key]=(c+value,-1)
         #localAttributes[key]=("-"+value,-1)

      elif key == "CUST_SN": # this should have precedence over IBM_SN
         localAttributes[key]=(value,0)
         if localAttributes.has_key("IBM_SN"): #delete IBM_SN IF PRESENT
            localAttributes["IBM_SN"]=("",0)

      elif key == "IBM_SN": # this should have lower precedence than CUST_SN
         if localAttributes.has_key("CUST_SN"):
            localAttributes[key]=("",0)
         else:
            localAttributes[key]=(value,0)

      elif key == "MOTOR_LOT":  # if less than 7 chars, should use all 6
         if len(value)<7:
            localAttributes[key]=(" "+value,0)

      elif key == "CD_1":  # before the '-' put the data at 34, after the '-' put data at 50
         dash = value.find("-")
         localAttributes[key]=(value[:dash],0)
         # if there is a dash then write the string after it to location 50
         localAttributes["CD_1_2"]=(value[dash+1:],0)

      #elif key == 'PREAMP_LOT_1' and partNum[-3:0] in ['041']:
      #    localAttributes[key]=(value,0)

   return localAttributes

def WriteDTDFile(fileName):
   # create the object that will help create the DTD file
   dtd = DataBlockSetup()

   dtd.formatBlock(DTDformat)

   # this will print to the screen;  it's only useful on a desktop system
   #dtd.printBlock()

   # call our function (see above) to create the dictionary of attributes that need to be treated as special cases.
   exceptionAttributes = CreateExceptionsList(DriveAttributes)

   # load the attributes and special-case attributes to the DTD block, following the formatting rules in our DTDdictionary (see definition above).
   dtd.loadDictionaryToBlock(data=DriveAttributes,exceptionData=exceptionAttributes,formats=DTDdictionary)

   # this will print to the screen;  it's only useful on a desktop system
   #dtd.printBlock()

   # write the DTD flock to a file.
   dtd.sendToFile(fileName)

def checkThermistor():
   """Read thermistor and PCBA temperatures.  Check for outlier measurements."""

   if testSwitch.virtualRun:
      return

   ScriptComment("======================    Check Thermister    ================================")

   oProc.St({'test_num':638},0x0001,0xFFFF,0x0100,0x9A32,0x4F03,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=3600)  #Platform Factory Unlock
   oProc.St({'test_num':638},0x0001,0x5001,0x0100,0x0000,0x0000,0x0000,0x0200,0x0001,0x0000,0x0000,timeout=1200)# Get converted temp.
   oProc.St({'test_num':508},0x8005,0x0000,0x0002,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=800) # Disp 2 bytes rd buf
   bufferData = DriveVars["Buffer Data"]
   FinTemp1 = bufferData[2:4]+bufferData[0:2]
   FinTemp1 = int(FinTemp1,16)/10.0
   dut.driveattr['TEMP_FIN1']= FinTemp1
   ScriptComment("==============================================================================")
   ScriptComment("The converted temperature is: %sc.     The spec range is 10c - 30c" %FinTemp1)
   ScriptComment("==============================================================================")
   if FinTemp1 <10 or FinTemp1 >30:                                # Spec range 10c-30c
      ScrCmds.raiseException(10279,'Drv Misc-Log Data Out of Spec')

   oProc.St({'test_num':638},0x0001,0x4F01,0x0100,0x1000,0x2F00,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=3600) # Display current PWA temp
   oProc.St({'test_num':508},0x8005,0x0026,0x0002,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=800) # Disp 2 bytes rd buf
   bufferData = DriveVars["Buffer Data"]
   FinTemp1 = bufferData[2:4]+bufferData[0:2]
   FinTemp1 = int(FinTemp1,16)/100.0
   dut.driveattr['TEMP_FIN2']= FinTemp1
   ScriptComment("===============================================================================")
   ScriptComment("The current PWA temperature is: %sc.   The spec range is 20c - 40c" %FinTemp1)
   ScriptComment("===============================================================================")
   if FinTemp1 <20 or FinTemp1 >40:                                # spec range 20c-40c
      ScrCmds.raiseException(10279,'Drv Misc-Log Data Out of Spec')


def PerformHeadStabilitySequence():

   TraceMessage("PerformHeadStabilitySequence")

   powerCycle()

#  /*****************************************************************************/
#  VGA Mode
   try:
      oProc.St({'test_num':695},0x01A1,0xFFFF,0xFFFF,0x0046,0xFFFF,0x0001,0x0014,0xFFFF,0x000A,0x0000,timeout=7200,spc_id = 1) # VGA (VGA_CSM Table) - zone 0
   except:
      ReportErrorCode(0)
      powerCycle()
   try:
      oProc.St({'test_num':695},0x01A1,0xFFFF,0xFFFF,0x0046,0xFFFF,0x0100,0x0014,0xFFFF,0x000A,0x0000,timeout=7200,spc_id = 2) # VGA (VGA_CSM Table) - zone 8
   except:
      ReportErrorCode(0)
      powerCycle()
   try:
      oProc.St({'test_num':695},0x01A1,0xFFFF,0xFFFF,0x0046,0xFFFF,0x8000,0x0014,0xFFFF,0x000A,0x0000,timeout=7200,spc_id = 3) # VGA (VGA_CSM Table) - zone 15
   except:
      ReportErrorCode(0)
      powerCycle()

#  /*****************************************************************************/
#  Bias Mode
   try:
      oProc.St({'test_num':695},0x0100,0xFFFF,0xFFFF,0x0000,0xFFFF,0x0001,0x0010,0x03E8,0x001A,0x0000,timeout=7200,spc_id = 1) # Bias (CSM2 Table) - zone 0
   except:
      ReportErrorCode(0)
      powerCycle()
   try:
      oProc.St({'test_num':695},0x0100,0xFFFF,0xFFFF,0x0000,0xFFFF,0x0100,0x0010,0x03E8,0x001A,0x0000,timeout=7200,spc_id = 2) # Bias (CSM2 Table) - zone 8
   except:
      ReportErrorCode(0)
      powerCycle()
   try:
      oProc.St({'test_num':695},0x0100,0xFFFF,0xFFFF,0x0000,0xFFFF,0x8000,0x0010,0x03E8,0x001A,0x0000,timeout=7200,spc_id = 3) # Bias (CSM2 Table) - zone 15
   except:
      ReportErrorCode(0)
      powerCycle()


#  /*****************************************************************************/
#  VMM Mode
   try:
      oProc.St({'test_num':695},0x8002,0xFFFF,0xFFFF,0x0000,0xFFFF,0x0001,0x0014,0x0000,0x220A,0x0000,timeout=7200,spc_id = 1) # VMM (STRESS_CSM Table) - zone 0
   except:
      ReportErrorCode(0)
      powerCycle()
   try:
      oProc.St({'test_num':695},0x8002,0xFFFF,0xFFFF,0x0000,0xFFFF,0x0100,0x0014,0x0000,0x220A,0x0000,timeout=7200,spc_id = 2) # VMM (STRESS_CSM Table) - zone 8
   except:
      ReportErrorCode(0)
      powerCycle()
   try:
      oProc.St({'test_num':695},0x8002,0xFFFF,0xFFFF,0x0000,0xFFFF,0x8000,0x0014,0x0000,0x220A,0x0000,timeout=7200,spc_id = 3) # VMM (STRESS_CSM Table) - zone 15
   except:
      ReportErrorCode(0)
      powerCycle()

def checkCacheSize(expectedCacheSize=8200576, percentLimit=2.0):
   """
   Default cache size is 8MB.  Drive will fail if the cache size is not within +/- percentLimit of expectedCacheSize.
   """
   TraceMessage("checkCacheSize")

   if testSwitch.virtualRun: # DriveVar usage breaks virtual execution
      return

   oProc.St({'test_num':538},0x0000,0x3C03,0x0000,0x0000,0x0000,0x0400,0x0200,0x0001,0x0000,0x0000,timeout=60) # Read Cache Size
   oProc.St({'test_num':508},0x8005,0x0000,0x0008,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=60)
   bufferData = DriveVars["Buffer Data"]
   cacheSize = int(bufferData[2:8],16)
   objMsg.printMsg("Cache Size = %s "%cacheSize)
   if cacheSize > expectedCacheSize*(1+percentLimit/100.0) or cacheSize < expectedCacheSize*(1-percentLimit/100.0):
      ScrCmds.raiseException(10171,'Cache Size is not within %s%% of the expected size.  Expected size = %s '%(percentLimit,expectedCacheSize)) # EC 10171=Drv PCBA -DRAM Verify Failed

def Clear_SMARTandUDS():
   """
   This is a platform based test function for clearing the SMART and UDS counters prior to
   drive shipment to the customer.

   Copied from Cust_Verify in CCVTest.py because Cust_Verify is setup as a CState
   making it unaccessable to IO testing outside of Cust_Verify.
   """
   ScriptComment("Clear SMART and UDS")
   oProc.St({'test_num':564,'prm_name':'Disp Cumulative SMART'},0x00FF,0xFF1E,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0x30FF,0xFFFF,timeout=600,spc_id=7) # Display Cumulative SMART Values
   oProc.St({'test_num':508,'prm_name':'SMART Write 0 Write Buffer'},0x0000,0x0000,0x0020,0xFF80,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Write all 00's to Write Buffer
   oProc.St({'test_num':508,'prm_name':'SMART Display Write Buffer'},0x0004,0x0000,0x0020,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Display Write Buffer
   oProc.St({'test_num':508,'prm_name':'Clear UDS 01'},0x0002,0x0000,0x00FF,0x0000,0x0000,0x0000,0x0600,0x0600,0x0800,0x0000,timeout=600) # Load Write Buffer to clear UDS
   oProc.St({'test_num':508,'prm_name':'Clear UDS 02'},0x0002,0x0008,0x00FF,0x0000,0x0000,0x0000,0x0800,0x0100,0x0119,0x0906,timeout=600) # Load Write Buffer to clear UDS
   oProc.St({'test_num':508,'prm_name':'SMART Display Write Buffer'},0x0004,0x0000,0x0020,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Display Write Buffer
   oProc.St({'test_num':638,'prm_name':'Platform Factory Unlock'},0x0001,0xFFFF,0x0100,0x9A32,0x4F03,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Unlock for Platform
   oProc.St({'test_num':599,'prm_name':'Set Max Buffer'},0x0006,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Set Buffer sizes to maximum
   oProc.St({'test_num':599,'prm_name':'Send Factory Command'},0x0001,0xE000,0x0000,0x1000,0x2459,0x0000,0x0200,0x0000,0x0000,0x0000,timeout=600) # Manually issue Send Factory Command
   oProc.St({'test_num':599,'prm_name':'Receive Factory Command'},0x0001,0xE100,0x0000,0x2800,0x2459,0x0000,0x0200,0x0000,0x0000,0x0000,timeout=600) # Manually issue Receive Factory Command
   oProc.St({'test_num':638,'prm_name':'Format SMART Frames'},0x0001,0x5201,0x0100,0x0800,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Format SMART Frames
   oProc.St({'test_num':638,'prm_name':'Clear SMART Counters'},0x0001,0x5201,0x0100,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Clear SMART Counters
   oProc.St({'test_num':638,'prm_name':'Head amp measurements'},0x0001,0x5201,0x0100,0x0a00,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Do head amp measurements for SMART
   oProc.St({'test_num':538,'prm_name':'Spin Down'},0x0000,0x1B00,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=1800) # Spin Down
   powerCycle()
   oProc.St({'test_num':535,'prm_name':'Initiator info'},0x0002,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=1200) # Display Initiator Code Rev
   oProc.St({'test_num':514,'prm_name':'FW Servo info'},0x8000,0x0001,0x00C0,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # FW, Servo Ram, Servo Rom Revs
##   if self.FDEdrive == "on":  # Only run on Hurricane FDE
##      Drv_FDE_mode = self.get_drvFDEmode()
##      if Drv_FDE_mode == "80":
##         ScriptComment("Drive is in USE mode.  Will Unlock ports.  OK to proceed with CCV.")
##         self.UnlockDiagUDE()
   ScriptComment("Verify UDS Power Cycle count has been cleared")
   oProc.St({'test_num':564,'prm_name':'Disp Cumulative SMART'},0x00FF,0xFF1E,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0x30FF,0xFFFF,timeout=600,spc_id=8) # Display Cumulative SMART Values
   oProc.St({'test_num':508,'prm_name':'SMART Write 0 Read Buffer'},0x0001,0x0000,0x0010,0xFF80,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Write all 00's to Read Buffer
   oProc.St({'test_num':508,'prm_name':'SMART Display Read Buffer'},0x0005,0x0000,0x0010,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Display Read Buffer
   oProc.St({'test_num':638,'prm_name':'Get SMART SRAM Frame'},0x0002,0x5201,0x0100,0x0300,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Get SMART SRAM Frame
   oProc.St({'test_num':508,'prm_name':'SMART Display Read Buffer'},0x0005,0x0000,0x0010,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=600) # Display Read Buffer
   oProc.St({'test_num':508,'prm_name':'Verify UDS PowerCycle Count'},0x0009,0x0008,0x0002,0x0000,0x0000,0x0000,0x0000,0x0002,0x0000,0x0000,timeout=600) # Verify value of 2 or less for bytes 8,9 (UDS Power Cycle Count)


##def SpinUp_np(set5V=5000,set12V=12000,onTime = 30,baudRate=390000):
##   from Process import CProcess
##   oProc = CProcess()
##   if objDut.partNum[3:6] in ['004','007']:
##      oProc.St(prm_608_PortLoginA)  # Clears LIP on Port A for login
##      oProc.St(prm_608_PortLoginB)  # Clears LIP on Port B for login
##      oProc.St(prm_517_RequestSense_Ready_Check)  # Checks for drive not ready conditions
##      oProc.St(prm_514_StdInquiryData)
##   elif objDut.partNum[3:6] == "066":
##      for i in range(10):
##         try:
##            oProc.St(prm_517_RequestSense, {'prm_name':'Standard Request Sense - With SpinUp'},SEND_TUR_CMDS_ONLY=(0x0001,))
##            oProc.St(prm_517_RequestSense_SD0D_Check) # SDOD CHECK AMK
##            ScriptPause(20)
##            oProc.St(prm_517_RequestSense_Ready_Check)  # Checks for drive not ready conditions
##            oProc.St(prm_514_StdInquiryData)
##            break
##         except:
##            objPwrCtrl.powerCycle(set5V,set12V,10,onTime,baudRate)
##   else:
##      ScrCmds.raiseException(11107,'Clear Unit Attention failed')
##
##
##def IF3_SetTransferMode(transferMode,L_V=5000,H_V=12000,DELAY=30):
##   from Process import CProcess
##   oProc = CProcess()
##
##   if transferMode == '1':
##      oProc.St(IOTP.prm_533_Set_XferRate)       #oProc.St({'test_num':533},0x8000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0001,timeout=300) # 1.5 Gbits/s
##      objPwrCtrl.powerOn(L_V,H_V,DELAY,useESlip=1)
##      SpinUp_np()
##
##   elif transferMode == '3':
##      oProc.St(IOTP.prm_533_Set_XferRate,FC_SAS_TRANSFER_RATE=(0x0003,))#oProc.St({'test_num':533},0x8000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0003,timeout=300) # 3 Gbits/s
##      oProc.St(IOTP.prm_506_60s)                #oProc.St({'test_num':506},0x0000,0x003C,0x0000,0x0000,0x0000,0x0000,0x0000,0x003C,0x0000,0x0000,timeout=1200) # change i/o back to 60s
##      ###oProc.St({'test_num':638},0x0010,0x1b00,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=1200) # spin down
##      objPwrCtrl.powerOff(20)
##      objPwrCtrl.powerOn(L_V,H_V,DELAY,useESlip=1)
##      SpinUp_np()
##   elif transferMode == '6':
##      oProc.St(IOTP.prm_506_60s)                #oProc.St({'test_num':506},0x0000,0x003C,0x0000,0x0000,0x0000,0x0000,0x0000,0x003C,0x0000,0x0000,timeout=1200) # change i/o back to 60s
##      ###oProc.St({'test_num':638},0x0010,0x1b00,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,timeout=1200) # spin down
##      objPwrCtrl.powerOff(20)
##      objPwrCtrl.powerOn(L_V,H_V,DELAY,useESlip=1)
##      SpinUp_np()
##   else:
##      pass
