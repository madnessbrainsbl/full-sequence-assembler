#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Implements the CPC ICmd interface
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SPT_ICmd.py $
# $Revision: #8 $
# $DateTime: 2016/12/28 18:08:20 $
# $Author: phonenaing.myint $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SPT_ICmd.py#8 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import ScrCmds, serialScreen, sptCmds
import re, random, time, math, traceback
import MessageHandler as objMsg
from Drive import objDut
from Serial_ICmd import Serial_ICmd

resPat = re.compile('Batch File 00 (PASSED|FAILED)')

#DEBUG = True
DEBUG = False

# SDI
from Utility import CUtility
lbaTuple = CUtility.returnStartLbaWords
wordTuple = CUtility.ReturnTestCylWord

if testSwitch.YARRAR:
   POWER_MODE_STANDBY = '/5p84'
   POWER_MODE_SLEEP   = '/5p85'
else:
   POWER_MODE_STANDBY = '/5p85'
   POWER_MODE_SLEEP   = '/5p86'

class SPT_ICmd(Serial_ICmd):

   def __init__(self, params = {}, objPwrCtrl = None):
      Serial_ICmd.__init__(self, params, objPwrCtrl)
      self.dut = objDut
      self.params = params
      self.oSerial = serialScreen.sptDiagCmds()
      self.dut.driveattr['MC Offset'] = 0

   #---------------------------------------------------------------------------------------------------------#
   def ChkBatchReturn(self, res):
      return re.search('Batch File 00 PASSED',res) and not re.search('Invalid Diag',res)

   #---------------------------------------------------------------------------------------------------------#
   def Y2Y1Cmd(self, lba, COMPARE_FLAG = 0, SEDOption = 0):
      try:
         self.dut.driveattr['PROC_CTRL13'] = str(int(self.dut.driveattr['PROC_CTRL13']) + 1)
      except:
         self.dut.driveattr['PROC_CTRL13'] = 1

      objMsg.printMsg('Y2Y1Cmd to recover lba:%s' % (lba))
      sptCmds.sendDiagCmd("/FY2,,,,10000000018", printResult = DEBUG)
      
      try:
         self.BatchRead(lba, 1, COMPARE_FLAG = COMPARE_FLAG, SEDOption = SEDOption)
         # To do - may be able to return here if Y2 is able to recover
      except:
         objMsg.printMsg("Ignoring Y2 Read Exception: %s" % `traceback.format_exc()`)

      if COMPARE_FLAG:
         self.ClearBinBuff()

      sptCmds.sendDiagCmd("/FY1", printResult = True)

      try:
         self.BatchRead(lba, 1, COMPARE_FLAG = COMPARE_FLAG, SEDOption = SEDOption)
         objMsg.printMsg("Y1 read recovered!")
      except:
         objMsg.printMsg("Y1 Read Exception: %s" % (traceback.format_exc(),))
         raise

   #---------------------------------------------------------------------------------------------------------#
   def DoY2Y1Retry(self, res, COMPARE_FLAG = 0, SEDOption = 0):

      udecount = 0
      for line in res.splitlines():
         lst = line.split()
         if len(lst) > 6 and lst[:3] == ['Next', 'User', 'LBA']:
            udecount = udecount + 1
            if udecount > 100:
               objMsg.printMsg("udecount more than 100")
               ScrCmds.raiseException(12346, "Too many bad sectors, there are more than 100")

            lba = lst[3]
            self.Y2Y1Cmd(lba, COMPARE_FLAG = COMPARE_FLAG, SEDOption = SEDOption)

      if udecount > 0:
         objMsg.printMsg('Restoring Y2 Cmd')
         sptCmds.sendDiagCmd("/FY2,,,,10000000018", printResult = True)

   #---------------------------------------------------------------------------------------------------------#
   def DoG2P_Merge(self, res):
      
      LBAlst = []
      udecount = 0
      #Collecting a list of bad Drive LBAs

      EndLBA = self.dut.driveattr['Max LBA'] - 1
      EndLBA = self.GetLBACeil(EndLBA)
      objMsg.printMsg("Max Disc LBA = 0x%x" %(EndLBA))

      for line in res.splitlines():
         lst = line.split()
         if DEBUG:
            objMsg.printMsg("lst %s" % (lst,))
         if len(lst) > 6 and lst[:3] == ['Next', 'User', 'LBA']:
            udecount = udecount + 1
            if udecount > 100:
               objMsg.printMsg("udecount more than 100")
               raise

            for loop in range(-4,5): #pad +/- 4LBA
               padding_lba = int(lst[3], 16) + loop
               if (padding_lba >= 0 and padding_lba <= EndLBA):
                  padLBA = "%X" % padding_lba
                  if padLBA in LBAlst:
                     objMsg.printMsg("%s already in the record" % padLBA)
                  else:
                     objMsg.printMsg("%s add in the record" %padLBA)
                     LBAlst.append("%s" % padLBA) 
                  if DEBUG:
                     objMsg.printMsg("Num of bad LBA %d, LBAlst %s" % (len(LBAlst),LBAlst))

      #Push LBAs into V4(Altr) list
      self.oSerial.gotoLevel('2')
      for i in range(len(LBAlst)):          
         cmd = 'F%X,A1'% int(LBAlst[i],16)
         self.oSerial.sendDiagCmd(cmd, timeout=10, printResult = DEBUG)

      #Do one time merging
      if len(LBAlst) != 0:
         objMsg.printMsg("Merging now..")
         retries = self.params.get('G2P_retries', 2)
         for i in range(retries+1):
            try:
               self.oSerial.gotoLevel('T')
               self.oSerial.sendDiagCmd('V4', printResult = True)
               G2P_Time = 1800*(i+1)
               self.oSerial.sendDiagCmd('m0,6,3,,,,,22', timeout = G2P_Time, printResult = True)
               break
            except:
               objMsg.printMsg('G2P Failed, rerun!')
               objPwrCtrl.powerCycle(5000,12000,10,30)
               self.oSerial.enableDiags()
         else:
            ScrCmds.raiseException(12346, "G2P FAIL")
      else:
         objMsg.printMsg("No merging to do..")

      if len(LBAlst) > 0: #if G2P merging done, write over the same logical zone again 
         result = {'LLRET':'WRAGAIN'}
      else:
         result = PASS_RETURN
      return result
   #---------------------------------------------------------------------------------------------------------#
   def BatchRead(self, lba, translen, COMPARE_FLAG = 0, SEDOption = 0):

      DEBUG = True      # True for now...

      CreateBatch = '/6E0'
      RunBatch = 'B0,0'

      self.oSerial.sendDiagCmd(CreateBatch,altPattern="-", printResult = DEBUG)
      self.oSerial.sendDiagCmd("/A", altPattern="-", printResult = DEBUG)
      self.oSerial.sendDiagCmd("*f,1,0,%s" % lba, altPattern="-", printResult = DEBUG)
      self.oSerial.sendDiagCmd("*f,1,1,%s" % translen, altPattern="-", printResult = DEBUG)

      if COMPARE_FLAG:
         cmd = "q4,0,1,%x\r|" % SEDOption
      else:
         cmd = "q1,0,1,%x\r|" % SEDOption

      self.oSerial.sendDiagCmd(cmd,altPattern="6>", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(RunBatch,timeout = 60,altPattern=resPat, printResult = True) 

      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN
      else:
         raise

   #---------------------------------------------------------------------------------------------------------#
   def GetLBACeil(self, MAXIMUM_LBA):
      return int(math.ceil((MAXIMUM_LBA + self.dut.driveattr['MC Offset'])/8.0))

   def GetBuffer(self, Mode, ByteOffset = 0, BuffSize = 512):
      """
      Retreive buffer from drive
      """
      if not self.dut.IsSDI:
         objMsg.printMsg('Non SDI does not support GetBuffer')
         return PASS_RETURN

      objMsg.printMsg("SPT_ICmd GetBuffer")
      from base_SATA_ICmd_Params import DisplayBufferData

      tempPrm = dict(DisplayBufferData) #create a copy

      if testSwitch.BF_0139058_231166_P_FIX_SI_BUFFER_FILE_PARAM:
         if Mode & WBF:
            tempPrm['CTRL_WORD1'] = 14
            tempPrm['prm_name'] = 'Write Buffer to file'
         if Mode & RBF:
            tempPrm['CTRL_WORD1'] = 15
            tempPrm['prm_name'] = 'Read Buffer to file'
      else:
         if Mode & WBF:
            tempPrm['CTRL_WORD1'] = (0x000E,)
            tempPrm['prm_name'] = 'Write Buffer to file'
         if Mode & RBF:
            tempPrm['CTRL_WORD1'] = (0x000F,)
            tempPrm['prm_name'] = 'Read Buffer to file'

      tempPrm.update({'BYTE_OFFSET': wordTuple(ByteOffset),
                      'BUFFER_LENGTH':wordTuple(BuffSize)})

      stret = self.St(tempPrm)

      if not testSwitch.virtualRun:
         if (testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and objRimType.CPCRiser()):
            data = open(os.path.join(ScrCmds.getSystemPCPath(), 'CPCFile', ScrCmds.getFofFileName(file = 0)), 'rb').read()
         else:
            try:
               data = open(os.path.join(ScrCmds.getSystemPCPath(), 'filedata', ScrCmds.getFofFileName(file = 0)), 'rb').read()
            except:
               data = open(os.path.join(ScrCmds.getSystemPCPath(), 'filedata', ScrCmds.getFofFileName(file = 1)), 'rb').read()
      else:
         data = '\x00'*16

      #Truncate to requested buffer size
      data = data[:BuffSize]

      stret = {'LLRET':0,'DATA': data}

      return stret

   def FillBuffByte(self, buffFlag, data, byteOffset=0, byteCount = None):
      """
      FillBuffByte's input according to CPC spec is a string indicating the buffer bytes to write... so input here for data is
      '0000' for a binary \x00\x00 written to the log
      """
      if not self.dut.IsSDI:
         objMsg.printMsg('Non SDI does not support FillBuffByte')
         return PASS_RETURN

      import struct

      objMsg.printMsg("SPT_ICmd FillBuffByte")
      from base_SATA_ICmd_Params import WritePatternToBuffer

      tempPrm = dict(WritePatternToBuffer) #create a copy
      tempPrm.pop('DATA_PATTERN0',0)
      tempPrm.pop('DATA_PATTERN1',0)

      if testSwitch.BF_0145286_231166_P_FIX_MOBILE_SCREENS:
         if type(data) != types.StringType:
            data = "%X" % data

      data = int(data, 16)
      tempPrm['BYTE_PATTERN_LENGTH'] = len(str(data))
      tempPrm['DtaPttrn'] = data

      tempPrm['BYTE_OFFSET'] = wordTuple(byteOffset)
      if byteCount == None:
         #remove buffer length- forces full bufer update
         tempPrm.pop('BUFFER_LENGTH')
      else:
         byteCount = max([byteCount, 8])
         tempPrm['BUFFER_LENGTH'] = wordTuple(byteCount)

      if buffFlag & WBF:
         tempPrm['CTRL_WORD1'] = (0x0000,)
         tempPrm['prm_name'] = 'Write Pattern to Write Buffer'
         status = self.St(tempPrm)
      if buffFlag & RBF:
         tempPrm['CTRL_WORD1'] = (0x0001,)
         tempPrm['prm_name'] = 'Write Pattern to Read Buffer'
         status = self.St(tempPrm)

      return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def ClearBinBuff(self, Buffer = WBF):
      if self.dut.IsSDI:
         objMsg.printMsg('SDI does not support ClearBinBuff')
         return PASS_RETURN

      try:
         self.oSerial.sendDiagCmd('/2P0000,0000', timeout=10)
      except:
         sptCmds.enableDiags()
         self.oSerial.sendDiagCmd('/2P0000,0000', timeout=30)

      objMsg.printMsg('ClearBinBuffer...')
      return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def BufferStatus(self, Buffer = WBF):
      self.oSerial.sendDiagCmd('/2P0000,0000')
      data = re.split('\n',self.oSerial.execOnlineCmd('?'))
      BufferSize = 0
      for i in data:
        if re.search('Diag Rd Buf',i):
           BufferSize = int(re.split("\(",re.split("\)",i)[0])[1],16)
           objMsg.printMsg('Diagnostic Buffer Size: %s Sectors' %BufferSize)    
      self.dut.driveattr['DiagBufferSize'] = BufferSize              
      return BufferSize     
   #---------------------------------------------------------------------------------------------------------#
   def FillBuffRandom(self, Buffer = WBF):
      self.oSerial.sendDiagCmd('/2P1212')
      objMsg.printMsg('FillBuffRandom...')
   #---------------------------------------------------------------------------------------------------------#
   def FillBuffer(self, Buffer = WBF, Offset = 0, Pattern = '00000000'):
      self.oSerial.gotoLevel('2')
      Pattern_Length = len(Pattern)   
      if Pattern_Length > 8: Pattern = Pattern[:8]
      if Pattern_Length > 4:
         Command = 'P' + Pattern[Pattern_Length-4:] + ',' + Pattern[:Pattern_Length-4] + ',' + ('%x'%int(hex(Pattern_Length*4),16)) + ',1'
      else:   
         Command = 'P' + Pattern + ',,' +  ('%x'%int(hex(Pattern_Length*4),16)) + ',1'
      self.oSerial.sendDiagCmd(Command)
      objMsg.printMsg('FillBuffer - Pattern : %s' %Pattern)
   #---------------------------------------------------------------------------------------------------------#
   def SPGetMaxLBA(self):
      self.oSerial.gotoLevel('C')
      self.dut.driveattr['MC Offset'] = 0
      try:
         LBAPattern = 'Host LBA -> Max of the Host LBA\s+:\s(?P<HOST_LBA>[a-fA-F\d]+)'
         MCOffsetPattern = 'MC Offset -> MC user partition in Host LBA\s+:\s(?P<MC_OFFSET>[a-fA-F\d]+)'
         data = self.oSerial.sendDiagCmd('U')
         match = re.search(LBAPattern,data)
         match1 = re.search(MCOffsetPattern,data)
         maxLBA = int(match.groupdict()['HOST_LBA'],16)
         MCOffset = int(match1.groupdict()['MC_OFFSET'],16)
         self.dut.driveattr['MC Offset'] = MCOffset        
         objMsg.printMsg('4K Drive - MAX_LBA: %s MC_OFFSET:%s' %(maxLBA,MCOffset))
      except:
         maxLBA = int(ICmd.GetMaxLBA()['MAX48'],16) - 1
         objMsg.printMsg("ICmd.GetMaxLBA: %s" % maxLBA)

      self.dut.driveattr['Max LBA'] = maxLBA
      return maxLBA
   #---------------------------------------------------------------------------------------------------------#
   def SequentialWriteDMAExt(self, STARTING_LBA, MAXIMUM_LBA, STEP_LBA = 256, BLKS_PER_XFR = 256, printResult = True, G2P_Merge = False):

      if DEBUG: objMsg.printMsg('SequentialWriteDMAExt' )  
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          STARTING_LBA = (STARTING_LBA + self.dut.driveattr['MC Offset'])/8
          MAXIMUM_LBA = self.GetLBACeil(MAXIMUM_LBA)
          STEP_LBA = STEP_LBA / 8
          BLKS_PER_XFR = BLKS_PER_XFR / 8
      
      timeout = min(max((MAXIMUM_LBA - STARTING_LBA), 30), 36000) #Assume 1 sec per LBA
                                                                  #Use 10hrs as max value
      if BLKS_PER_XFR == STEP_LBA: 
         BLKS_PER_XFR = 0xFFFF
         STEP_LBA = 0xFFFF
      
      TotalBlks = (MAXIMUM_LBA - STARTING_LBA)
      
      Command = 'q2'

      if self.dut.driveattr['FDE_DRIVE'] == 'FDE' and not testSwitch.IS_SDnD:
         SEDOption = 0x8000                  
      else:
         SEDOption = 0
      G2P_Merge = int(bool(G2P_Merge))
      if G2P_Merge:
         DiagErrorsToIgnore = ['00005004', ]
      else:
         DiagErrorsToIgnore = []

      if DEBUG: objMsg.printMsg('SEDOption|G2P_Merge= %x' % (SEDOption|G2P_Merge))          

      BuildBatch_1a = '/AAD\r' + \
                      '*f,2,1,%x,%x,%x,%x,%x,0,%x\r' %(STARTING_LBA,MAXIMUM_LBA,BLKS_PER_XFR,STEP_LBA,STARTING_LBA,TotalBlks) + \
                      '*f,6,6,2,3,7\r'
      BuildBatch_1b = '@1\r' + \
                      '%s,5,3,%x\r' %(Command,(SEDOption | G2P_Merge)) + \
                      '*f,3,1,5,5,4\r'

      BuildBatch_2a = '*f,3,1,6,5,3\r' + \
                      '*f,6,6,3,5,2\r' + \
                      '*f,6,6,2,6,2\r' + \
                      '*f,6,5,1,5,2\r' + \
                      '@2\r'
      BuildBatch_2b = '*f,3,2,3,2,5\r' + \
                      '%s,5,3,%x\r' %(Command,(SEDOption | G2P_Merge)) + \
                      '@3\r' + \
                      '|'            

      #Set Test Space
      CreateBatch = '/6E0' 
      RunBatch = 'B0,0'

      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-", printResult = DEBUG)                      
      res = self.oSerial.sendDiagCmd(BuildBatch_1a,altPattern="-", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(BuildBatch_1b,altPattern="-", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(BuildBatch_2a,altPattern="-", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(BuildBatch_2b,altPattern="6>", printResult = DEBUG)
      if DEBUG:   
         PrintBatch = 'D0,0'
         res = self.oSerial.sendDiagCmd(PrintBatch,altPattern="6>", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat, printResult = (DEBUG or G2P_Merge), DiagErrorsToIgnore = DiagErrorsToIgnore) 
      if printResult:
         objMsg.printMsg('SequentialWrite:"STARTING_LBA-%x MAXIMUM_LBA-%x BLKS_PER_XFR-%x STEP_LBA-%x" Command:"%s" Result: "%s"' %(STARTING_LBA,MAXIMUM_LBA,BLKS_PER_XFR,STEP_LBA,Command,res[res.rfind('Batch File'):]))          
                    
      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         if G2P_Merge:
            result = self.DoG2P_Merge(res)
         else:
            result = PASS_RETURN                      
      else:
         result = FAIL_RETURN

      return result            
   #---------------------------------------------------------------------------------------------------------#
   def SequentialReadDMAExt(self, STARTING_LBA, MAXIMUM_LBA, STEP_LBA = 256, BLKS_PER_XFR = 256, STAMP_FLAG = 0, COMPARE_FLAG = 0, printResult = True, Y2Y1_Retry = False):
      if DEBUG: objMsg.printMsg('SequentialReadDMAExt' )          
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          STARTING_LBA = (STARTING_LBA + self.dut.driveattr['MC Offset'])/8
          MAXIMUM_LBA = self.GetLBACeil(MAXIMUM_LBA)
          STEP_LBA = STEP_LBA / 8
          BLKS_PER_XFR = BLKS_PER_XFR / 8

      timeout = min(max((MAXIMUM_LBA - STARTING_LBA), 30), 36000) #Assume 1 sec per LBA
                                                                  #use 5hrs as max value(3.3 times full pack write/read time).

      if BLKS_PER_XFR == STEP_LBA: 
         BLKS_PER_XFR = 0xFFFF
         STEP_LBA = 0xFFFF

      if COMPARE_FLAG:
         Command = 'q4'
      else:
         Command = 'q1'

      if self.dut.driveattr['FDE_DRIVE'] == 'FDE' and not testSwitch.IS_SDnD and COMPARE_FLAG :
         SEDOption = 0x8000
      else:
         SEDOption = 0

      if testSwitch.SP_RETRY_WORKAROUND:     # temporary using a switch
         Y2Y1_Retry = True

      Y2Y1_Retry = int (bool(Y2Y1_Retry))

      if Y2Y1_Retry:    # attempt to recover using Y2/Y1 retry
         DiagErrorsToIgnore = ['00005003', ]
      else:
         DiagErrorsToIgnore = []

      if DEBUG: objMsg.printMsg('SEDOption= %x' %SEDOption)          

      TotalBlks = (MAXIMUM_LBA - STARTING_LBA)

      BuildBatch_1a = '/AAD\r' + \
                   '*f,2,1,%x,%x,%x,%x,%x,0,%x\r' %(STARTING_LBA,MAXIMUM_LBA,BLKS_PER_XFR,STEP_LBA,STARTING_LBA,TotalBlks) + \
                   '*f,6,6,2,3,7\r' + \
                   '@1\r'

      BuildBatch_1b = '%s,5,3,%x\r' %(Command,(SEDOption | Y2Y1_Retry)) + \
                   '*f,3,1,5,5,4\r' + \
                   '*f,3,1,6,5,3\r'

      BuildBatch_2a = '*f,6,6,3,5,2\r' + \
                   '*f,6,6,2,6,2\r' + \
                   '*f,6,5,1,5,2\r' + \
                   '@2\r'

      BuildBatch_2b = '*f,3,2,3,2,5\r' + \
                   '%s,5,3,%x\r' %(Command,(SEDOption | Y2Y1_Retry)) + \
                   '@3\r' + \
                  '|'            

      #Set Test Space
      CreateBatch = '/6E0' 
      RunBatch = 'B0,0'

      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-", printResult = DEBUG)                      
      res = self.oSerial.sendDiagCmd(BuildBatch_1a,altPattern="-", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(BuildBatch_1b,altPattern="-", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(BuildBatch_2a,altPattern="-", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(BuildBatch_2b,altPattern="6>", printResult = DEBUG)
      if DEBUG:   
         PrintBatch = 'D0,0'
         res = self.oSerial.sendDiagCmd(PrintBatch,altPattern="6>", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat, printResult = (DEBUG or Y2Y1_Retry), DiagErrorsToIgnore = DiagErrorsToIgnore)  
      if printResult:
         objMsg.printMsg('SequentialRead:"STARTING_LBA-%x MAXIMUM_LBA-%x BLKS_PER_XFR-%x STEP_LBA-%x" Command:"%s" Result:"%s"' %(STARTING_LBA,MAXIMUM_LBA,BLKS_PER_XFR,STEP_LBA,Command,res[res.rfind('Batch File'):]))          

      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         if Y2Y1_Retry:
            self.DoY2Y1Retry(res, COMPARE_FLAG, SEDOption)

         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN

      return result            
          
   #---------------------------------------------------------------------------------------------------------#
   def SequentialWRDMAExt(self, STARTING_LBA, MAXIMUM_LBA, STEP_LBA = 256, BLKS_PER_XFR = 256, STAMP_FLAG = 0, COMPARE_FLAG = 0, timeout = 0):

      if DEBUG: objMsg.printMsg('SequentialWRDMAExt' )  

      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          STARTING_LBA = (STARTING_LBA + self.dut.driveattr['MC Offset'])/8
          MAXIMUM_LBA = self.GetLBACeil(MAXIMUM_LBA)
          STEP_LBA = STEP_LBA / 8
          BLKS_PER_XFR = BLKS_PER_XFR / 8

      if not timeout:
         timeout = min(max((MAXIMUM_LBA - STARTING_LBA), 30), 27000) #Assume 1 sec per LBA
                                                #Use 7hrs as max value(4.7 times 500G full pack write/read time).

      if BLKS_PER_XFR == STEP_LBA: 
         BLKS_PER_XFR = 0xFFFF
         STEP_LBA = 0xFFFF

      if COMPARE_FLAG:
         Command_1 = 'q2'
         Command_2 = 'q4'
      else:
         Command_1 = 'q2'
         Command_2 = 'q1'

      if self.dut.driveattr['FDE_DRIVE'] == 'FDE' and not testSwitch.IS_SDnD:
         SEDOption = 0x8000                  
      else:
         SEDOption = 0
      TotalBlks = (MAXIMUM_LBA - STARTING_LBA)

      BuildBatch_1 = '/AAD\r' + \
                   '*f,2,1,%x,%x,%x,%x,%x,0,%x\r' %(STARTING_LBA,MAXIMUM_LBA,BLKS_PER_XFR,STEP_LBA,STARTING_LBA,TotalBlks) + \
                   '*f,6,6,2,3,7\r' + \
                   '@1\r' + \
                   '%s,5,3,%x\r' % (Command_1, SEDOption) + \
                   '%s,5,3,%x\r' % (Command_2, SEDOption) 
      BuildBatch_2 = '*f,3,1,5,5,4\r' + \
                   '*f,3,1,6,5,3\r' + \
                   '*f,6,6,3,5,2\r' + \
                   '*f,6,6,2,6,2\r' + \
                   '*f,6,5,1,5,2\r' + \
                   '@2\r' 
      BuildBatch_3 = '*f,3,2,3,2,5\r' + \
                   '%s,5,3,%x\r' % (Command_1, SEDOption) + \
                   '%s,5,3,%x\r' % (Command_2, SEDOption) + \
                   '@3\r'  + \
                  '|'            
      
      #Set Test Space
      CreateBatch = '/6E0' 
      RunBatch = 'B0,0'

      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-", printResult = DEBUG)                      
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="-", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(BuildBatch_3,altPattern="6>", printResult = DEBUG)
      if DEBUG:   
         PrintBatch = 'D0,0'
         res = self.oSerial.sendDiagCmd(PrintBatch,altPattern="6>", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat, printResult = DEBUG)  
      objMsg.printMsg('SequentialWR:"STARTING_LBA-%x MAXIMUM_LBA-%x BLKS_PER_XFR-%x STEP_LBA-%x" Command:"%s" Result: "%s"' %(STARTING_LBA,MAXIMUM_LBA,BLKS_PER_XFR,STEP_LBA,(Command_1 + ',' + Command_2),res[res.rfind('Batch File'):]))          
            
      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN

      return result            

   #---------------------------------------------------------------------------------------------------------#
   def ReverseWriteDMAExt(self, STARTING_LBA, MAXIMUM_LBA, BLKS_PER_XFR = 256, COMPARE_FLAG = 0):
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          STARTING_LBA = (STARTING_LBA + self.dut.driveattr['MC Offset'])/8
          MAXIMUM_LBA = self.GetLBACeil(MAXIMUM_LBA)
          BLKS_PER_XFR = BLKS_PER_XFR / 8
      
      timeout = min(max((STARTING_LBA - MAXIMUM_LBA), 30), 18000) #Assume 1 sec per LBA
                                                         #Use 5hrs as max value(3.3 times 500G full pack write/read time).

      BLKS_PER_XFR = 0xFFFF
      STEP_LBA = 0xFFFF

      TotalBlks = (STARTING_LBA - MAXIMUM_LBA)

      Command = 'q2'
      BuildBatch_1 = '/AAD\r' + \
                   '*f,2,1,%x,%x,%x,%x,%x,0,%x\r' %(MAXIMUM_LBA,STARTING_LBA,BLKS_PER_XFR,STEP_LBA,STARTING_LBA,TotalBlks) + \
                   '*f,6,6,2,3,7\r' + \
                   '@1\r' + \
                   '*f,3,2,5,5,4\r' + \
                   '%s,5,3\r' %Command + \
                   '*f,3,1,6,1,3\r'
      BuildBatch_2 = '*f,6,6,2,6,5\r' + \
                   '*f,6,6,1,5,1\r' + \
                   '@2\r' + \
                   '*f,3,2,3,5,1\r' + \
                   '%s,1,3\r' %Command + \
                   '@3\r' + \
                  '|'            

      #Set Test Space
      CreateBatch = '/6E0' 
      RunBatch = 'B0,0'

      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")                      
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat)  
      objMsg.printMsg('ReverseWrite:"STARTING_LBA-%x MAXIMUM_LBA-%x BLKS_PER_XFR-%x Command:"%s" Result: "%s"' %(STARTING_LBA,MAXIMUM_LBA,BLKS_PER_XFR,Command,res[res.rfind('Batch File'):]))          

      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN

      return result            
          
   #---------------------------------------------------------------------------------------------------------#
   def ReverseReadDMAExt(self, STARTING_LBA, MAXIMUM_LBA, BLKS_PER_XFR = 256, COMPARE_FLAG = 0, printResult=True):
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          STARTING_LBA = (STARTING_LBA + self.dut.driveattr['MC Offset'])/8
          MAXIMUM_LBA = self.GetLBACeil(MAXIMUM_LBA)
          BLKS_PER_XFR = BLKS_PER_XFR / 8
      
      timeout = min(max((STARTING_LBA - MAXIMUM_LBA), 30), 18000) #Assume 1 sec per LBA
                                                         #Use 5hrs as max value(3.3 times 500G full pack write/read time).

      BLKS_PER_XFR = 0xFFFF
      STEP_LBA = 0xFFFF

      if COMPARE_FLAG:
         Command = 'q4'
      else:
         Command = 'q1'       

      TotalBlks = (STARTING_LBA - MAXIMUM_LBA)

      BuildBatch_1 = '/AAD\r' + \
                   '*f,2,1,%x,%x,%x,%x,%x,0,%x\r' %(MAXIMUM_LBA,STARTING_LBA,BLKS_PER_XFR,STEP_LBA,STARTING_LBA,TotalBlks) + \
                   '*f,6,6,2,3,7\r' + \
                   '@1\r' + \
                   '*f,3,2,5,5,4\r' + \
                   '%s,5,3\r' %Command + \
                   '*f,3,1,6,1,3\r'
      BuildBatch_2 = '*f,6,6,2,6,5\r' + \
                   '*f,6,6,1,5,1\r' + \
                   '@2\r' + \
                   '*f,3,2,3,5,1\r' + \
                   '%s,1,3\r' %Command + \
                  '|'            

      #Set Test Space
      CreateBatch = '/6E0' 
      RunBatch = 'B0,0'

      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")                      
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat)  
      if printResult:
         objMsg.printMsg('ReverseRead:"STARTING_LBA-%x MAXIMUM_LBA-%x BLKS_PER_XFR-%x" Command:"%s" Result: "%s"' %(STARTING_LBA,MAXIMUM_LBA,BLKS_PER_XFR,Command,res[res.rfind('Batch File'):]))          

      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN

      return result            
           
   #---------------------------------------------------------------------------------------------------------#
   def RandomWriteDMAExt(self, STARTING_LBA, MAXIMUM_LBA, MIN_SECTOR_CNT = 256, MAX_SECTOR_CNT = 256, LOOP_CNT = 1, COMPARE_FLAG = 0):
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          STARTING_LBA = (STARTING_LBA + self.dut.driveattr['MC Offset'])/8
          MAXIMUM_LBA = self.GetLBACeil(MAXIMUM_LBA)
          MIN_SECTOR_CNT = MIN_SECTOR_CNT / 8
          MAX_SECTOR_CNT = MAX_SECTOR_CNT / 8
          SECTOR_CNT = max(MIN_SECTOR_CNT,MAX_SECTOR_CNT)
      
      timeout = min(max((SECTOR_CNT * LOOP_CNT), 30), 36000) #Assume 1 sec per LBA
                                                    #Use 10hrs as max value(5X 250000 random loops(~2hrs) with sec256.).
         
      Command = 'q2'
      if self.dut.driveattr['FDE_DRIVE'] == 'FDE' and not testSwitch.IS_SDnD:
         SEDOption = 0x8000                  
      else:
         SEDOption = 0
      #Set Test Space
      CreateBatch = '/6E0'
      BuildBatch = '/AAD\r' + \
                   '*f,2,1,%x,%x,%x,1,%x\r' %(STARTING_LBA,MAXIMUM_LBA,SECTOR_CNT,LOOP_CNT) + \
                   '@1\r'  + \
                   '*f,8,6,1,2\r' + \
                   '%s,6,3,%x\r' % (Command,SEDOption) + \
                   '*f,4,4\r' + \
                   '*f,6,5,1,4,5\r' + \
                   '|'
      RunBatch = 'B0,0'
                      
      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")                      
      res = self.oSerial.sendDiagCmd(BuildBatch,altPattern="6>")
      if DEBUG:   
         PrintBatch = 'D0,0'
         res = self.oSerial.sendDiagCmd(PrintBatch,altPattern="6>", printResult = DEBUG)
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat)  
      objMsg.printMsg('RandomWrite:STARTING_LBA-%x MAXIMUM_LBA-%x MIN_SECTOR_CNT-%x MAX_SECTOR_CNT-%x LOOP_CNT-%x" Command:"%s" Result:"%s"' 
                     %(STARTING_LBA,MAXIMUM_LBA,MIN_SECTOR_CNT,MAX_SECTOR_CNT,LOOP_CNT,Command,res[res.rfind('Batch File'):]))          
      
      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN

      return result            
           
   #---------------------------------------------------------------------------------------------------------#
   def RandomReadDMAExt(self, STARTING_LBA, MAXIMUM_LBA, MIN_SECTOR_CNT = 256, MAX_SECTOR_CNT = 256, LOOP_CNT = 1, COMPARE_FLAG = 0):
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          STARTING_LBA = (STARTING_LBA + self.dut.driveattr['MC Offset'])/8
          MAXIMUM_LBA = self.GetLBACeil(MAXIMUM_LBA)
          MIN_SECTOR_CNT = MIN_SECTOR_CNT / 8
          MAX_SECTOR_CNT = MAX_SECTOR_CNT / 8
          SECTOR_CNT = max(MIN_SECTOR_CNT,MAX_SECTOR_CNT)
      
      timeout = min(max((SECTOR_CNT * LOOP_CNT), 30), 36000) #Assume 1 sec per LBA
                                                 #Use 10hrs as max value(5X 250000 random loops(~2hrs) with sec256.).
      if COMPARE_FLAG or (self.dut.driveattr['FDE_DRIVE'] == 'FDE' and not testSwitch.IS_SDnD): #if read_verify or SED option is required, still use A>q cmd, otherwise use A>R
         if COMPARE_FLAG:
            Command = 'q4'
         else:
            Command = 'q1'

         if self.dut.driveattr['FDE_DRIVE'] == 'FDE' and not testSwitch.IS_SDnD:
            SEDOption = 0x8000                  
         else:
            SEDOption = 0

         #Set Test Space
         CreateBatch = '/6E0'
         BuildBatch = '/AAD\r' + \
                      '*f,2,1,%x,%x,%x,1,%x\r' %(STARTING_LBA,MAXIMUM_LBA,SECTOR_CNT,LOOP_CNT) + \
                      '@1\r'  + \
                      '*f,8,6,1,2\r' + \
                      '%s,6,3,%x\r' % (Command,SEDOption) + \
                      '*f,4,4\r' + \
                      '*f,6,5,1,4,5\r' + \
                      '|'
         RunBatch = 'B0,0'
      else:
         Command = 'R,%x\r' %SECTOR_CNT

         #Set Test Space
         CreateBatch = '/6E0'
         BuildBatch = '/AAD\r' + \
                      'AB,%x\r' %STARTING_LBA + \
                      'AC,%x\r' %MAXIMUM_LBA  + \
                      'A100\r' + \
                      'L0,%x\r' %LOOP_CNT + \
                      '%s\r' %Command + \
                      '|' 
         RunBatch = 'B0,0'
                      
      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")                      
      res = self.oSerial.sendDiagCmd(BuildBatch,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat)  
      objMsg.printMsg('RandomRead:STARTING_LBA-%x MAXIMUM_LBA-%x MIN_SECTOR_CNT-%x MAX_SECTOR_CNT-%x LOOP_CNT-%x" Command:"%s" Result:"%s"' 
                     %(STARTING_LBA,MAXIMUM_LBA,MIN_SECTOR_CNT,MAX_SECTOR_CNT,LOOP_CNT,Command,res[res.rfind('Batch File'):]))          

      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN

      return result            
            
   #---------------------------------------------------------------------------------------------------------#
   def RandomWRDMAExt(self, STARTING_LBA, MAXIMUM_LBA, MIN_SECTOR_CNT = 256, MAX_SECTOR_CNT = 256, LOOP_CNT = 1, COMPARE_FLAG = 0):
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          STARTING_LBA = (STARTING_LBA + self.dut.driveattr['MC Offset'])/8
          MAXIMUM_LBA = self.GetLBACeil(MAXIMUM_LBA)
          MIN_SECTOR_CNT = MIN_SECTOR_CNT / 8
          MAX_SECTOR_CNT = MAX_SECTOR_CNT / 8
          SECTOR_CNT = max(MIN_SECTOR_CNT,MAX_SECTOR_CNT)
      
      timeout = min(max((SECTOR_CNT * LOOP_CNT), 30), 54000) #Assume 1 sec per LBA
                                                             #Use 15hrs as max value(5X 250000 random loops(~2hrs) with sec256.)
      
      if COMPARE_FLAG:
         Command_1 = 'q2'
         Command_2 = 'q4'
      else:
         Command = 'q3'         

      if self.dut.driveattr['FDE_DRIVE'] == 'FDE' and not testSwitch.IS_SDnD:
         SEDOption = 0x8000                  
      else:
         SEDOption = 0

      #Set Test Space
      CreateBatch = '/6E0'
      if COMPARE_FLAG:
         BuildBatch = '/AAD\r' + \
                      '*f,2,1,%x,%x,%x,1,%x\r' %(STARTING_LBA,MAXIMUM_LBA,SECTOR_CNT,LOOP_CNT) + \
                      '@1\r'  + \
                      '*f,8,6,1,2\r' + \
                      '%s,6,3,%x\r' % (Command_1, SEDOption) + \
                      '%s,6,3,%x\r' % (Command_2, SEDOption) + \
                      '*f,4,4\r' + \
                      '*f,6,5,1,4,5\r' + \
                      '|'
      else:
         BuildBatch = '/AAD\r' + \
                      '*f,2,1,%x,%x,%x,1,%x\r' %(STARTING_LBA,MAXIMUM_LBA,SECTOR_CNT,LOOP_CNT) + \
                      '@1\r'  + \
                      '*f,8,6,1,2\r' + \
                      '%s,6,3,%x\r' % (Command, SEDOption) + \
                      '*f,4,4\r' + \
                      '*f,6,5,1,4,5\r' + \
                      '|'
      RunBatch = 'B0,0'
                      
      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")                      
      res = self.oSerial.sendDiagCmd(BuildBatch,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat)  

      if COMPARE_FLAG:
         cmd = (Command_1 + ',' + Command_2)
      else:
         cmd = Command
      objMsg.printMsg('RandomWR:STARTING_LBA-%x MAXIMUM_LBA-%x MIN_SECTOR_CNT-%x MAX_SECTOR_CNT-%x LOOP_CNT-%x" Command:"%s" Result:"%s"' 
                        %(STARTING_LBA,MAXIMUM_LBA,MIN_SECTOR_CNT,MAX_SECTOR_CNT,LOOP_CNT,cmd,res[res.rfind('Batch File'):]))  

      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN

      return result            
           
   #-------------------------------------------------------------------------------------------------------
   def WeakWrite(self, rangeLimits, scnt, udmaSpeed, pattern, count):
      '''
      FillBytePatternStr( pattern )
      SetFeatures( 0x03, udmaSpeed )
      
      Loop 0..12
      |  SequentialWriteDMAExt( seqLBA[x], seqLBA[x + 1], scnt )
      |_ x += 2
      
      Loop 0..12
      |  SequentialReadDMAExt( minSeqLBA[x], maxSeqLBA[x + 1], scnt )
      |  ReverseReadDMAExt( minSeqLBA[x], maxSeqLBA[x + 1], scnt ) 
      |_ x += 2 
      '''
      timeout = min(max(count, 30), 18000)           # Set min timeout as 30s.

      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
         temp = []
         for i in rangeLimits:
            temp.append(i/8)
         rangeLimits = temp
         count = count / 8
              
      #Create Batch File
      CreateBatch = '/6E0' 
      BuildBatch_1 ='*f,2,1,%x,%x,%x,%x,%x,%x,%x,%x\r' %(rangeLimits[0],rangeLimits[2],rangeLimits[4],rangeLimits[6],rangeLimits[8],rangeLimits[10],rangeLimits[12], rangeLimits[14])     + \
                    '*f,2,9,%x,%x,%x,%x\r' %(rangeLimits[16],rangeLimits[18],rangeLimits[20],rangeLimits[22])     + \
                    '*f,2,E,2,%x\r' %count      + \
                    '/2P0000,0000\r'            + \
                    'P%s,%s,20,1\r' %(pattern,pattern)                      + \
                    '/A\r'                                                  + \
                       'q2,1,F\r'  + \
                       'q2,2,F\r'
      BuildBatch_2 =   'q2,3,F\r'  + \
                       'q2,4,F\r'  + \
                       'q2,5,F\r'  + \
                       'q2,6,F\r'  + \
                       'q2,7,F\r'  + \
                       'q2,8,F\r'  + \
                       'q2,9,F\r'  + \
                       'q2,A,F\r'
      BuildBatch_3 =   'q2,B,F\r'  + \
                       'q2,C,F\r'  + \
                       'q1,1,F\r'  + \
                       'q1,1,F\r'  + \
                       'q1,2,F\r'  + \
                       'q1,2,F\r'  + \
                       'q1,3,F\r'  + \
                       'q1,3,F\r'
      BuildBatch_4 =   'q1,4,F\r'  + \
                       'q1,4,F\r'  + \
                       'q1,5,F\r'  + \
                       'q1,5,F\r'  + \
                       'q1,6,F\r'  + \
                       'q1,6,F\r'  + \
                       'q1,7,F\r'  + \
                       'q1,7,F\r'
      BuildBatch_5 =   'q1,8,F\r'  + \
                       'q1,8,F\r'  + \
                       'q1,9,F\r'  + \
                       'q1,9,F\r'  + \
                       'q1,A,F\r'  + \
                       'q1,A,F\r'  + \
                       'q1,B,F\r'  + \
                       'q1,B,F\r'  + \
                       'q1,C,F\r'  + \
                       'q1,C,F\r'  + \
                    '|'     
      RunBatch = "B0,0"
      
      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_3,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_4,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_5,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat)

      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN
                   
      return result

   #-------------------------------------------------------------------------------------------------------
   def SeqDelayWR(self, startLBA, endLBA, sectCnt, minDelay, maxDelay, stepDelay, GrpCnt, DelayStepLba, DelayWrtLoop):
      '''
      Lba = start LBA
      	Delay = minDelay
      	CmdCount = 0
      	While (lba <= last LBA)
      	|  Write (lba, scnt )
      	|  CmdCount ++
      	|  If (CmdCount > groupSize)
      	|	   CmdCount = 0
      	|	   Delay += stepDelay
      	|  If (Delay > maxDelay) 
         |  	Delay = minDelay
      	|_ Lba += scnt
      '''
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          startLBA = (startLBA + self.dut.driveattr['MC Offset'])/8
          endLBA = self.GetLBACeil(endLBA)
          DelayStepLba = (DelayStepLba + self.dut.driveattr['MC Offset'])/8
          sectCnt = sectCnt / 8
      
      timeout = min(max((endLBA - startLBA), 30), 15*DelayWrtLoop) #Assume 1 sec per LBA
                                                          #Use 15s(4.2X GIO) as max value for each loop(1000X 2700s in GIO).
      
      #Create Batch File
      CreateBatch = '/6E0' 
      BuildBatch_1 ='*f,2,8,0,0,%x,%x,%x,%x,0,0\r' %(startLBA,endLBA,DelayStepLba,DelayWrtLoop)                + \
                    '@5\r' + \
                    '*f,2,1,%x,0,%x,%x,%x,%x,%x\r' %(minDelay,minDelay,sectCnt,stepDelay,maxDelay,GrpCnt)     + \
                    '*f,8,8,A,B\r' + \
                    '*f,3,1,9,8,C\r' + \
                    '/A\r'                                                  + \
                    '@1\r'                                                     + \
                    '*f,6,2,2,8,9\r'                                           + \
                       '*f,7,3\r'                                              + \
                       'q2,8,4\r'
      BuildBatch_2 = '*f,4,2\r'                                              + \
                       '*f,6,5,3,2,7\r'                                        + \
                          '*f,1,2,0\r'                                         + \
                          '*f,3,1,3,3,5\r'                                     + \
                       '@3\r'                                                  + \
                       '*f,6,5,4,3,6\r'                                        + \
                          '*f,1,3,1\r'
      BuildBatch_3 =    '@4\r' + \
                        '*f,3,1,8,8,4\r'                                      + \
                    '*3,1\r'                                                 + \
                    '@2\r'                                                     + \
                    '*f,4,F\r' + \
                    '*f,6,5,5,F,D\r' + \
                    '|'     
      RunBatch = "B0,0"
      
      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_3,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat,printResult=False)       
         
      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN
      
      return result
   #-------------------------------------------------------------------------------------------------------
   def WriteTestSim2(self, minLBA, midLBA, maxLBA, singleLBA, fixedScnt, testCount, dataPat, multiSPB=0):
      '''
      FillBytePatternStr( dataPat )
      SetMultiple( multiSPB )
      
      Loop testCount
      |  WriteMultiple( randOD, fixedScnt )
      |  FlushCache
      |  ReadMultiple(randOD, fixedScnt)
      |  BufferCompare( compareFlag )
      |  ReadMultiple( singleLBA, fixedScnt)
      |  WriteMultiple( randID, randScnt )
      |  FlushCache
      |  ReadMultiple(randID, randScnt)
      |_ BufferCompare( compareFlag )
      
      SetFeatures( udmaSpeed )
      SequentialReadDMA( 0, maxLBA, fixedScnt )
      '''
      startlba = 0 
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          minLBA = (minLBA + self.dut.driveattr['MC Offset'])/8
          midLBA = (midLBA + self.dut.driveattr['MC Offset'])/8
          maxLBA = self.GetLBACeil(maxLBA)
          singleLBA = (singleLBA + self.dut.driveattr['MC Offset'])/8
          startlba = (startlba + self.dut.driveattr['MC Offset'])/8
          fixedScnt = fixedScnt / 8
      else:
          startlba = 0    
         
      timeout = min(max(testCount, 30), 18000) #Assume 1 sec per LBA
      seqScnt = 0xFFFF  #mimic low level rw subsystem
      
      #Create Batch File
      CreateBatch = '/6E0' 
      BuildBatch_1 ='*f,2,1,%x,%x,%x,%x,%x,%x,8,100,0,8\r' %(minLBA,midLBA,maxLBA,singleLBA,fixedScnt,testCount)     + \
                    '*f,2,B,0,0,0,%x\r' %seqScnt                               + \
                    '/2P0000,0000\r'                                           + \
                    'P%s,%s,20,1\r' %(dataPat,dataPat)                         + \
                    '/A\r'                                                     + \
                    '@1\r'                                                     + \
                       '*f,8,B,1,2\r'
      BuildBatch_2 =   'q2,B,5\r'                                                 + \
                       'q4,B,5\r'                                                 + \
                       'q1,4,5\r'                                                 + \
                       '*f,8,C,2,3\r'                                             + \
                       '*f,8,D,7,8\r'  + \
                       '*f,3,4,D,D,A\r' + \
                       'q2,C,D\r'      + \
                       'q4,C,D\r'      
      BuildBatch_3 ='*f,4,9\r'     + \
                    '*f,6,4,1,9,6\r'     + \
                    'AB,%x\r' %startlba  + \
                    'AC,%x\r' %maxLBA    + \
                    'q1,,E,10\r'         + \
                    '|'   
      RunBatch = "B0,0"
      
      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_3,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat)    

      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN

      return result
   #-------------------------------------------------------------------------------------------------------
   def SequentialCmdLoop(self, cmd, STARTING_LBA, MAXIMUM_LBA, BLKS_PER_XFR, STEP_LBA, cmdLoop, testLoop = 1):
      if cmd == 0x35: cmdchar = 'q2'
      if cmd == 0x25: cmdchar = 'q1'

      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          STARTING_LBA = (STARTING_LBA + self.dut.driveattr['MC Offset'])/8
          MAXIMUM_LBA = self.GetLBACeil(MAXIMUM_LBA)
          if STEP_LBA: STEP_LBA = STEP_LBA / 8
          BLKS_PER_XFR = BLKS_PER_XFR / 8

      timeout = min(max((MAXIMUM_LBA - STARTING_LBA) *  cmdLoop, 30), 36000) #Assume 1 sec per LBA. 30<=timeout<=36000
                                                                             #Use 10hrs as max value(6X 500G full pack write/read time).
      
      #Set Test Space
      CreateBatch = '/6E0'
      BuildBatch_1 = '/A\r' + \
                   '*f,2,1,%x,%x,%x,%x,%x,0\r' %(STARTING_LBA,MAXIMUM_LBA,BLKS_PER_XFR,STEP_LBA,STARTING_LBA) + \
                   '@1\r' + \
                   'L0,%x\r' %cmdLoop  + \
                   '%s,5,3\r' %cmdchar + \
                   '*f,3,1,5,5,4\r' + \
                   '*f,3,1,6,5,3\r'
      BuildBatch_2 = '*f,6,6,3,5,2\r' + \
                   '*f,6,6,2,6,2\r' + \
                   '*f,6,5,1,5,2\r' + \
                   '@2\r' + \
                   '*f,3,2,3,2,5\r' + \
                   'L0,%x\r' %cmdLoop  + \
                   '%s,5,3\r' %cmdchar + \
                   '@3\r'           + \
                  '|'            
      RunBatch = 'B0,0'
                      
      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")                      
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat)
      objMsg.printMsg('SequentialCmdLoop:Cmd-%s STARTING_LBA-%x MAXIMUM_LBA-%x BLKS_PER_XFR-%x STEP_LBA-%x cmdLoop-%x" Result:"%s"' 
                     %(cmd,STARTING_LBA,MAXIMUM_LBA,BLKS_PER_XFR,STEP_LBA,cmdLoop,res[res.rfind('Batch File'):]))

      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN

      return result      
   
   #-------------------------------------------------------------------------------------------------------
   def OSCopySim1(self, minLBA, maxLBA, scnt, Pattern):
      '''
      FillBytePatternStr( pattern )
      SetFeatures( udmaSpeed )
      SequentialWriteDMAExt( minLBA, maxLBA, scnt )
      FlushCache()
      '''
      self.ClearBinBuff() 
      self.FillBuffer(1,0,Pattern)
      result = self.SequentialWriteDMAExt(minLBA,maxLBA,scnt,scnt)
      return result
   #-------------------------------------------------------------------------------------------------------
   def OSCopySim2(self, minLBA, maxLBA, scnt):
      '''
      SetFeatures( udmaSpeed )
      SequentialReadDMAExt( minLBA, maxLBA, scnt )
      FlushCache()
      '''
      result = self.SequentialReadDMAExt(minLBA,maxLBA,scnt,scnt)  
      return result
   #-------------------------------------------------------------------------------------------------------
   def OSCopySim3(self, minLBA, maxLBA, scnt, udmaSpeed = 0x45):
      '''
      SmartReturnStatus()
      SetFeatures( udmaSpeed )
      ReverseReadDMAExt( minLBA, maxLBA, scnt )
      '''
      result = self.ReverseReadDMAExt(maxLBA, minLBA, scnt)   
      return result

   #-------------------------------------------------------------------------------------------------------
   def LowDutyRead(self,minRandLBA,maxRandLBA,minSeqLBA,minRevLBA,maxRevLBA,fixedScnt,loop,pattern,delay):
      '''
      FillBytePatternStr( pattern )
      SetFeatures( 0x03, udmaSpeed )
      nextSeqLBA = minSeqLBA
      
      Loop loop
      |  ReadDMAExt( minRandLBA..maxRandLBA, fixedScnt )
      |  wait delay
      |  WriteDMAExt( minRandLBA..maxRandLBA, fixedScnt )
      |  wait delay
      |  ReadDMAExt( nextSeqLBA, randScnt )
      |  wait delay
      |_ nextSeqLBA += randScnt
      
      ReverseReadDMAExt( minRevLBA..maxRevLBA, fixedScnt )
      Where randScnt is a random value between 1 and 256.  The LBA used by WriteDMAExt() is the same as the previous ReadDMAExt().
      '''
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          minRandLBA = (minRandLBA + self.dut.driveattr['MC Offset'])/8
          maxRandLBA = self.GetLBACeil(maxRandLBA)
          minSeqLBA = (minSeqLBA + self.dut.driveattr['MC Offset'])/8
          fixedScnt = fixedScnt / 8
      
      fixedScnt = 0xFFFF  #mimic low level rw subsystem
         
      timeout = min(max((maxRandLBA-minRandLBA) * loop, 30), 120 * loop) #Assume 1 sec per LBA, timeout too long if use original method.
                                                                #Dec.09.2013. From log, estimate cost 0.2min for 1 loop, for insurance plus 10, take 2mins as 1 loop.
      TotalBlks = (maxRandLBA - minRandLBA)
      #Create Batch File
      nextSeqLBA = minSeqLBA
      CreateBatch = '/6E0' 
      BuildBatch_1 ='*f,2,1,0,0,%x,%x,%x,%x\r' %(fixedScnt,nextSeqLBA,loop,delay)     + \
                    '*f,2,7,8,100,8,0,0,%x,%x\r' %(minRandLBA,TotalBlks) + \
                    '/2P0000,0000\r'                                           + \
                    'P%s,%s,20,1\r' %(pattern,pattern)                         + \
                    '/TO5\r'        + \
                    '/AAD\r'          + \
                    '@1\r'
      BuildBatch_2 =  'q1,C,D,0\r'  + \
                      '*f,7,6\r'    + \
                      'q2,C,D,0\r'  + \
                      '*f,7,6\r'
      BuildBatch_3  = '*f,8,B,7,8\r'  + \
                     '*f,3,4,B,B,9\r' + \
                     'q1,4,B\r'                  + \
                     '*f,7,6\r'    + \
                     '*f,3,1,4,4,B\r'         + \
                    '*f,4,A\r'     + \
                    '*f,6,5,1,A,5\r' + \
                  '|'            
      RunBatch = "B0,0"

      
      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_3,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat)

      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN

      if result['LLRET'] == OK:
         res = self.ReverseReadDMAExt(maxRevLBA, minRevLBA, fixedScnt)
         if res['LLRET'] != OK:
            result = FAIL_RETURN
         else:
            result = PASS_RETURN
                
      return result
   #-------------------------------------------------------------------------------------------------------
   def ReadTestSim(self,minSeqLBA,maxSeqLBA,wrtScnt,rdScnt,minRandLBA,maxRandLBA,loop,randSubLoops,pattern):
      '''
      FillBytePatternStr( pattern )
      SequentialWriteDMAExt( minSeqLBA, maxSeqLBA, wrtScnt )
      FlushCache
      SequentialReadDMAExt(minSeqLBA, maxSeqLBA, rdScnt, compareFlag = TRUE )
      
      Loop randLoops
      |  randScnt = rand( 1..256 )
      |_ RandomReadDMAExt( minRandLBA..maxRandLBA, randScnt, randSubLoops )
      Where randScnt is a random value between 1 and 256.  The loop is repeated randLoops / randSubLoops times.  In other words, a loop counter is incremented by randSubLoops each time through the loop until is equals randLoops.
      '''        
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          minRandLBA = (minRandLBA + self.dut.driveattr['MC Offset'])/8
          maxRandLBA = self.GetLBACeil(maxRandLBA)

      # SMR drives requires longer timeout, since it writes in bands. Since this algor with 3000 loops takes ~4800s, use 9000s timeout instead.
      if testSwitch.SMRPRODUCT:
         timeout = loop * 3
      else:
         timeout = min(max(loop, 30), 18000) #Assume 1 sec per LBA

      self.ClearBinBuff()
      self.FillBuffer(1,0,pattern)      
      res = self.SequentialWriteDMAExt(minSeqLBA, maxSeqLBA, wrtScnt, wrtScnt, False)
      if res['LLRET'] != OK:
         return FAIL_RETURN
      res = self.SequentialReadDMAExt(minSeqLBA, maxSeqLBA, rdScnt, rdScnt, 0, 1, False)
      if res['LLRET'] != OK:
         return FAIL_RETURN

      #Create Batch File
      CreateBatch = '/6E0'
      BuildBatch_1 ='*f,2,1,%x,%x,%x,%x\r' %(minRandLBA,maxRandLBA,loop,randSubLoops)     + \
                    '*f,2,5,8,100,0,8,0,0,0,0\r' + \
                    '/A\r'         + \
                    '@1\r'            + \
                       '*f,8,7,5,6\r'    + \
                       '*f,3,4,7,7,8\r' + \
                       '*f,1,D,0\r'
      BuildBatch_2 =   '@2\r'               + \
                          '*f,8,C,1,2\r'     + \
                          'q1,C,7\r'         + \
                       '*f,4,D\r'            + \
                       '*f,4,E\r'              + \
                       '*f,6,5,2,D,4\r'     + \
                    '*f,6,5,1,E,3\r'        + \
                    '|'   
      RunBatch = "B0,0"

      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat,printResult=True)  

      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN

      return result

   #-------------------------------------------------------------------------------------------------------
   def FileCopySim1(self, minLBA1, maxLBA1, scnt1, minLBA2, patData1, patData2):
      '''
      The ReadTestSim1() function executes the following algorithm.
      FillWriteBuffer1( patData1 )
      FillWriteBuffer2( patData2 )
      
      SetFeatures( udmaSpeed )
      
      lba1 = minLBA1
      lba2 = minLBA2
      
      Loop lba1 < maxLBA1
      |  select WriteBuffer #1
      |  ReadDMAExt( lba1, scnt1 )
      |  WriteDMAExt(lba1, scnt1 )
      |
      |  select WriteBuffer #2
      |  ReadDMAExt( lba2, randScnt )
      |  WriteDMAExt(lba2, randScnt )
      |
      |  lba1 += scnt1
      |_ lba2 += randScnt
      The total number of sectors transferred in the lba2 range is saved.  This value may be automatically recalled by FileCopySim2().
      '''
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          minLBA1 = (minLBA1 + self.dut.driveattr['MC Offset'])/8
          maxLBA1 = self.GetLBACeil(maxLBA1)
          minLBA2 = (minLBA2 + self.dut.driveattr['MC Offset'])/8
          scnt1 = scnt1 / 8
      
      timeout = min(max((maxLBA1 -  minLBA1) * 8, 30), 18000) #Assume 1 sec per LBA
      scnt1 = 0x20 #Changed from 1 to 256 with reference to GIO package - T653

      #Create Batch File
      CreateBatch = '/6E0'
      BuildBatch_1 ='*f,2,1,%x,%x,%x,%x\r' %(minLBA1,maxLBA1,scnt1,minLBA2)     + \
                    '*f,2,5,8,100,0,8,0,0,0,0\r' + \
                    '/2P0000,0000\r'                                           + \
                    '@1\r'            + \
                       '/2P%s,%s,20,1\r' %(patData1,patData1)                         + \
                       '/A\r'
      BuildBatch_2 =   'q1,1,3\r'        + \
                       'q2,1,3\r'        + \
                       '/2P%s,%s,20,1\r' %(patData2,patData2)                         + \
                       '/A\r'            
      BuildBatch_3 =   '*f,8,7,5,6\r'    + \
                       '*f,3,4,7,7,8\r' + \
                       '*f,3,1,9,9,7\r' + \
                       'q1,4,7\r'        + \
                       'q2,4,7\r'        + \
                    '*f,3,1,1,1,3\r'         + \
                    '*f,3,1,4,4,7\r'         + \
                    '*f,6,3,1,1,2\r'        + \
                    '*f,f,9\r' + \
                    '|'   
      RunBatch = "B0,0"

      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_3,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat)  

      if testSwitch.virtualRun:
         return PASS_RETURN
      
      index = res.find('INDEX 9= ')
      self.TSCNT = int(res[index+8:index+17].strip(),16)    
      
      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN                      
      else:
         result = FAIL_RETURN      
      
      return result   

   #-------------------------------------------------------------------------------------------------------
   def FileCopySim2(self, minLBA1, maxLBA1, scnt1, minLBA2, maxLBA2, scnt2):
      '''
         The ReadTestSim2() function executes the following algorithm.
         Setup large buffers
         ...SetFeatures( udmaSpeed )
         ...SequentialReadDMAExt( minLBA1, maxLBA1, scnt1 )
         ...ReverseReadDMAExt( minLBA1, maxLBA1, scnt1 )
         ...SequentialReadDMAExt( minLBA2, maxLBA2, scnt2 )
         ...ReverseReadDMAExt( minLBA2, maxLBA2, scnt2 )
         Restore default buffers
         It is assumed that FileCopySim2() was preceded by FileCopySim1() and a timed power cycle.  
         If the supplied value for maxLBA1 is 0 the total sector count value (TSCNT) is added to minLBA1 for the maximum value in range #1.  
         TSCNT is set by FileCopySim1() and is always cleared after this test.
      '''
      if maxLBA1 == 0:
         maxLBA1 = minLBA1 + self.TSCNT

      result = self.SequentialReadDMAExt( minLBA1, maxLBA1, scnt1 , scnt1)
      
      if result['LLRET'] == OK:
         result = self.ReverseReadDMAExt( maxLBA1, minLBA1, scnt1)

      if result['LLRET'] == OK:   
         result = self.SequentialReadDMAExt( minLBA2, maxLBA2, scnt2 , scnt2)

      if result['LLRET'] == OK:
         result = self.ReverseReadDMAExt( maxLBA2, minLBA2, scnt2)
          
      return result   

   #-------------------------------------------------------------------------------------------------------
   def ReadDMAExtTransRate(self,startLBA,totalBlksXfr,sectorCount):
      '''
      The ReadDMAExtTransRate () function measures the transfer rate for DMA read including seek time over the LBA range specified. 
      ReadDMAExt cmd is used for operation.
      '''
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          startLBA = (startLBA + self.dut.driveattr['MC Offset'])/8
          totalBlksXfr = totalBlksXfr / 8
          sectorCount = sectorCount / 8
          SectorSize = 4096
      else:
          SectorSize = 512

      timeout = min(max(totalBlksXfr, 30), 18000) #Assume 1 sec per LBA
                                                  #30 <= timeout <= 18000

      FixedScnt = 0xFFFF
      EndLBA =  startLBA + totalBlksXfr

      #Create Batch File
      CreateBatch = '/6E0'
      BuildBatch_1 =  '*f,2,1,%x,%x\r' %(startLBA,totalBlksXfr) + \
                     '/TO5\r'            + \
                     '/AAD\r'
      BuildBatch_2 = '*f,a\r'          + \
                     'q1,1,2,0\r'        + \
                     '*f,a,2\r'        + \
                     '*f,f,2\r' + \
                     '|'   
      RunBatch = "B0,0"

      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat)  

      if testSwitch.SMRPRODUCT:
         # for Chengai, drive will print LBAStart, Length and LBAEnd.
         # e.g
         # Executing Batch File 00
         # Simplified Formatted ASCII Output Mode selected
         # 00000000 0000000000004158 0000000000004158 INDEX 2=    82863
         # Batch File 00 PASSED
         # 4158 is the actual transfer length, because A>q cmd write/read in bands
         try:
            length = re.search("Simplified Formatted ASCII Output Mode selected(\s+[a-fA-F\d]+ [a-fA-F\d]+ [a-fA-F\d]+)", res).group(1).split()[1]
            totalBlksXfr = int(length,16)
            objMsg.printMsg('SMR totalBlksXfr (Disc LBA): %d' %(totalBlksXfr))
         except:
            objMsg.printMsg("Warning! SMR totalBlksXfer Exception: %s" % (traceback.format_exc(),))

      TotalBytes = totalBlksXfr * SectorSize
      index = res.find('INDEX 2= ')
      cct = int(res[index+8:index+17].strip(),16)    
      TxRate = TotalBytes / cct
      
      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN.copy()          
         result.update({'TXRATE':TxRate, 'CCT':cct, 'ENDLBA':EndLBA})           
      else:
         result = FAIL_RETURN      
      
      return result
      
   #-------------------------------------------------------------------------------------------------------
   def WriteDMAExtTransRate(self,startLBA,totalBlksXfr,sectorCount):
      '''
      The WriteDMAExtTransRate () function measures the transfer rate for DMA write including seek time over the LBA range specified. 
      WriteDMAExt cmd is used for operation.
      '''
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          startLBA = (startLBA + self.dut.driveattr['MC Offset'])/8
          totalBlksXfr = totalBlksXfr / 8
          sectorCount = sectorCount / 8
          SectorSize = 4096
      else:
          SectorSize = 512

      timeout = min(max(totalBlksXfr, 30), 18000) #Assume 1 sec per LBA
                                                  #30 <= timeout <= 18000
      FixedScnt = 0xFFFF
      EndLBA =  startLBA + totalBlksXfr      
      
      #Create Batch File
      CreateBatch = '/6E0'
      BuildBatch_1 =  '*f,2,1,%x,%x\r' %(startLBA,totalBlksXfr) + \
                     '/TO5\r'            + \
                     '/AAD\r'
      BuildBatch_2 = '*f,a\r'          + \
                     'q2,1,2,0\r'        + \
                     '*f,a,2\r'        + \
                     '*f,f,2\r' + \
                     '|'   
      RunBatch = "B0,0"

      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat)  
      
      if testSwitch.SMRPRODUCT:
         # for Chengai, drive will print LBAStart, Length and LBAEnd.
         # e.g
         # Executing Batch File 00
         # Simplified Formatted ASCII Output Mode selected
         # 00000000 0000000000004158 0000000000004158 INDEX 2=    82863
         # Batch File 00 PASSED
         # 4158 is the actual transfer length, because A>q cmd write/read in bands
         try:
            length = re.search("Simplified Formatted ASCII Output Mode selected(\s+[a-fA-F\d]+ [a-fA-F\d]+ [a-fA-F\d]+)", res).group(1).split()[1]
            totalBlksXfr = int(length,16)
            objMsg.printMsg('SMR totalBlksXfr (Disc LBA): %d' %(totalBlksXfr))
         except:
            objMsg.printMsg("Warning! SMR totalBlksXfer Exception: %s" % (traceback.format_exc(),))

      TotalBytes = totalBlksXfr * SectorSize
      index = res.find('INDEX 2= ')
      cct = int(res[index+8:index+17].strip(),16)    
      TxRate = TotalBytes / cct

      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN.copy()                      
         result.update({'TXRATE':TxRate, 'CCT':cct, 'ENDLBA':EndLBA})           
      else:
         result = FAIL_RETURN      
      
      return result      
   
   #---------------------------------------------------------------------------------------------------------#
   def SequentialWriteDMAExt_EUP(self, STARTING_LBA, MAXIMUM_LBA, STEP_LBA = 256, BLKS_PER_XFR = 256, WrtLoop = 5000, TotalBlks = 200000, printResult = True):
      if int(self.dut.DRV_SECTOR_SIZE) == 4096:
          STARTING_LBA = (STARTING_LBA + self.dut.driveattr['MC Offset'])/8
          MAXIMUM_LBA = self.GetLBACeil(MAXIMUM_LBA)
          STEP_LBA = STEP_LBA / 8
          BLKS_PER_XFR = BLKS_PER_XFR / 8
          TotalBlks = TotalBlks / 8
      
      timeout = min(max(WrtLoop * TotalBlks, 30), 25200) #Assume 1 sec per LBA
                                                         #30<timeout<25200(3.6X GIO), (5000X 7000s in GIO)
      Command = 'q2'
      BuildBatch_1 = '/AAD\r' + \
                   '*f,2,8,%x,%x,%x,0,0\r' %(STARTING_LBA,MAXIMUM_LBA,WrtLoop)+ \
                   '@4\r' + \
                   '*f,2,1,0,0,%x,%x,0,0,%x\r' %(BLKS_PER_XFR,STEP_LBA,TotalBlks) + \
                   '*f,8,1,8,9\r' + \
                   '*f,3,1,5,1,C\r' + \
                   '*f,3,1,2,1,7\r' + \
                   '*f,6,6,2,3,7\r'
      BuildBatch_2 = '@1\r' + \
                   '%s,5,3\r' %Command + \
                   '*f,3,1,5,5,4\r' + \
                   '*f,3,1,6,5,3\r' + \
                   '*f,6,6,3,5,2\r' + \
                   '*f,6,6,2,6,2\r' + \
                   '*f,6,5,1,5,2\r' + \
                   '@2\r'
      BuildBatch_3 = '*f,3,2,3,2,5\r' + \
                   '%s,5,3\r' %Command + \
                   '@3\r' + \
                   '*f,4,B\r' + \
                   '*f,6,5,4,B,A\r' + \
                  '|'            

      #Set Test Space
      CreateBatch = '/6E0' 
      RunBatch = 'B0,0'

      res = self.oSerial.sendDiagCmd(CreateBatch,altPattern="-")                      
      res = self.oSerial.sendDiagCmd(BuildBatch_1,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_2,altPattern="-")
      res = self.oSerial.sendDiagCmd(BuildBatch_3,altPattern="6>")
      res = self.oSerial.sendDiagCmd(RunBatch,timeout,altPattern=resPat) 
      if printResult:
         objMsg.printMsg('SequentialWrite_EUP:"STARTING_LBA-%x MAXIMUM_LBA-%x BLKS_PER_XFR-%x STEP_LBA-%x" Command:"%s" Result: "%s"' %(STARTING_LBA,MAXIMUM_LBA,BLKS_PER_XFR,STEP_LBA,Command,res[res.rfind('Batch File'):]))          
                    
      if self.ChkBatchReturn(res) or testSwitch.virtualRun:
         result = PASS_RETURN
      else:
         result = FAIL_RETURN

      return result            
 
   #---------------------------------------------------------------------------------------------------------#
   def ZeroCheck(self, startLBA, endLBA, sectCnt):
      self.ClearBinBuff() 
      return self.SequentialReadDMAExt(startLBA, endLBA, sectCnt, sectCnt, STAMP_FLAG = 0,COMPARE_FLAG = 1)

   #---------------------------------------------------------------------------------------------------------#
   def Seek(self, lba):
      sptCmds.enableDiags()
      self.oSerial.seekLBA(lba)
      return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def HardReset(self, exc = 1):
      objMsg.printMsg('SPT HardReset')
      if self.dut.SkipPCycle:
         objMsg.printMsg("HardReset SkipPCycle")
         sptCmds.enableDiags()
      else:
         from PowerControl import objPwrCtrl
         objPwrCtrl.powerCycle(5000,12000,10,10,baudRate=Baud38400,ataReadyCheck=False)
         sptCmds.enableDiags()
         self.ClearBinBuff()
         self.FillBuffer(1,0,"0000")
         self.oSerial.gotoLevel('T')

      return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def FlushCache(self):
      objMsg.printMsg("SPT_ICmd Dummy FlushCache")
      return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def FlushCacheExt(self):
      objMsg.printMsg("SPT_ICmd Dummy FlushCacheExt")
      return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def FlushMediaCache(self):
      objMsg.printMsg("SPT_ICmd Dummy FlushMediaCache")
      return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def MakeAlternateBuffer(self, *args, **kwargs):
      objMsg.printMsg("SPT_ICmd Dummy MakeAlternateBuffer")
      return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def RestorePrimaryBuffer(self, *args, **kwargs):
      objMsg.printMsg("SPT_ICmd Dummy RestorePrimaryBuffer")
      return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def GetIntfTimeout(self, *args, **kwargs):   # SDI
      objMsg.printMsg("SPT_ICmd Dummy GetIntfTimeout")
      return {'LLRET': 0, 'TMO': '30000', 'RES': '', 'RESULT': 'IEK_OK:No error', 'CT': '0'}

   #---------------------------------------------------------------------------------------------------------#
   def SetFeatures(self, *args, **kwargs):   # SDI
      objMsg.printMsg("SPT_ICmd SetFeatures")
      if self.dut.IsSDI:
         from base_SATA_ICmd_Params import SetFeaturesParameter
         tempPrm = dict(SetFeaturesParameter)
         #order the arguments are entered
         orderedKeyList = ['FEATURES',
                           'SECTOR_COUNT',
                           'SECTOR',
                           'CYLINDER',]

         for index, arg in enumerate(args):
            tempPrm[orderedKeyList[index]] = arg

         return self.translateStReturnToCPC(self.St(tempPrm))

      else:
         return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def IdentifyDevice(self, exc = 1):
      """
      Identify the ATA device: collecting device information using SDI/SPT
      """
      if not self.dut.IsSDI:
         if self.IdentifyDeviceBuffer == '':
            self.IdentifyDeviceBuffer = self.oSerial.getIdentifyBuffer(0, 0xFF)
            self.IdentifyDeviceBuffer += self.oSerial.getIdentifyBuffer(0x100, 0x1FF)

         return PASS_RETURN
         #return Serial_ICmd.IdentifyDevice(exc = exc)

      prm_514_Identify = {
         #"Ctrl1Wrd" : (0x0000,),
         "Ctrl1Wrd" : (0x8003,),
         "Ctrl2Wrd" : (0x0000,),
         "DrvVar" : (0x0000,),
         "DbgFlag" : (0x0000,),
         "PgCode" : (  0x00,),
         "TstFunc" : (0x0000,),
         }
      
      self.IdentifyDeviceBuffer = ''

      try:     
         self.dut.dblData.delTable('P514_IDENTIFY_DEVICE_DATA', forceDeleteDblTable = 1)
      except:
         objMsg.printMsg("delTable P514 Exception: %s" % (traceback.format_exc(),))

      try:     
         self.dut.dblData.Tables('P514_IDENTIFY_DEVICE_DATA').deleteIndexRecords(1)
      except:
         objMsg.printMsg("deleteIndexRecords P514 Exception: %s" % (traceback.format_exc(),))

      ret = st(514, prm_514_Identify, timeout=120)
      ID_TABLE = self.dut.dblData.Tables('P514_IDENTIFY_DEVICE_DATA').tableDataObj()

      for row in ID_TABLE:
         self.IdentifyDeviceBuffer += chr(int(row['VALUE'][0:2],16)) + chr(int(row['VALUE'][2:4],16))

      if len(self.IdentifyDeviceBuffer) != 512:
         objMsg.printMsg("IdentifyDeviceBuffer len not 512 but %s" % len(self.IdentifyDeviceBuffer))
         raise

      return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def BluenunAuto(self, start_lba, end_lba, sect_cnt, autoMultiplier, cmdPerSample, sampPerReg, blueNunLogTmo, maxTotalRetry, maxGroupRetry, timeout, exc = 1):

      BluenunAuto = {
         'test_num'              :639,
         'prm_name'              :'BluenunAuto',
         'timeout'               : 120000,   
         'spc_id'                : 1,   
         'CTRL_WORD1'            : (0x1), #0x1 - BlueNunAuto   
         'STARTING_LBA'          : (0,0,0,0),
         'MAXIMUM_LBA'           : (0,0,0,0),
      }

      tempPrm = BluenunAuto.copy()
            
      CTRL_WORD1 = tempPrm["CTRL_WORD1"] | (blueNunLogTmo << 7)      
      
      tempPrm.update({            
              "CTRL_WORD1": CTRL_WORD1,
            "STARTING_LBA": lbaTuple(start_lba),
            "MAXIMUM_LBA" : lbaTuple(end_lba),
           "BLKS_PER_XFR" : sect_cnt,        
             "MULTIPLIER" : autoMultiplier,
            "SAMPLE_SIZE" : cmdPerSample,            
            "NUM_SAMPLES" : sampPerReg,            
           "TOTAL_RETRIES": maxTotalRetry,
           "GROUP_RETRIES": maxGroupRetry,     
         "COMMAND_TIMEOUT": wordTuple(timeout),      
         })



      try:
         ret = self.St(tempPrm)
         data = self.dut.dblData.Tables('P639_BLUENUNSCAN').tableDataObj()[-1]
         data.update(PASS_RETURN)
         return data
      except:
         objMsg.printMsg("BluenunAuto Exception: %s" % traceback.format_exc())
         return FAIL_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def __CCTTest(self, thr0, thr1, thr2, ovPrm = None, exc = 1, timeout = None):
      """
      Extend threshold number(>thr0, >thr1, >thr2) into return value
      """
      RetThr0, RetThr1, RetThr2 = 0, 0, 0         #Set default return value
      CCTSetting = 0
      #IRSATA.251779.BAN20.SI.4C.251779.INC.LOD code fixed issue
      #[thr0, thr1, thr2] = [(i*1000) for i in [thr0, thr1, thr2]]       #For fix SI bug, CPC was counting CCT in millisecond, and SI in usec
      minThresh = min(thr0, thr1, thr2)
      maxThresh = max(thr0, thr1, thr2)
      binStep = int(minThresh/5)                       #Divide bin step
      totalBin = min(int(maxThresh/binStep), 50)       #max bin number = 50
      if binStep > 0xFF:
         CCTSetting |= 0xFF
      else:
         CCTSetting |= binStep & 0xFF
      CCTSetting |= (totalBin & 0xFF)<<8
      ovPrm.update({
            'CCT_BIN_SETTINGS' : (CCTSetting),
               })

      try:     
         self.dut.dblData.delTable('P_CCT_DISTRIBUTION', forceDeleteDblTable = 1)     #Clear P_CCT_DISTRIBUTION table before do CCT
      except:  
         objMsg.printMsg('Delete table P_CCT_DISTRIBUTION fail')

      #self.UnlockFactoryCmds()


      try:
         ret = self.St(ovPrm)
         objMsg.printMsg('ret=%s' % `ret`)
         ret = self.translateStReturnToCPC(st)
         objMsg.printMsg('ret2=%s' % `ret`)
         if testSwitch.virtualRun:
            return {'LLRET': 0, 'LBA': '0x00000000746FD087', 'ERR': '0', 'RES': '', 'DEV': '64', 'SCNT': '0', 'RESULT': 'IEK_OK:No error', 'STS': '80', 'THR1': '0', 'THR2': '0', 'THR0': '0', 'CT': '69537'}
         else:
            data = self.dut.dblData.Tables('P_CCT_DISTRIBUTION').tableDataObj()
            for entry in data:
               if int(entry['BIN_THRESHOLD']) >= thr0:
                  RetThr0 += int(entry['BIN_ENTRIES'])
               if int(entry['BIN_THRESHOLD']) >= thr1:
                  RetThr1 += int(entry['BIN_ENTRIES'])
               if int(entry['BIN_THRESHOLD']) >= thr2:
                  RetThr2 += int(entry['BIN_ENTRIES'])
            ret.update({
                  'THR0': RetThr0,
                  'THR1': RetThr1,
                  'THR2': RetThr2,
                        })
            return ret
      except:
         objMsg.printMsg("__CCTTest Exception: %s" % traceback.format_exc())
         return FAIL_RETURN.copy()

   #---------------------------------------------------------------------------------------------------------#
   def __ConvertWRmode(self, wrCmd = None,):
      """
      Write/read mode:
      0=write/read
      1=read
      2=write
      3=read/write
      """
      if wrCmd == None:
         return 0
      wrmode = 0
      WRDMAExt = {
            'ReadDMAExt' : 0x25,
            'WriteDMAExt': 0x35,
          'ReadVerifyExt': 0x42,
                  }
      WRDMAExtNum = {
            'ReadDMAExt' : 1,
            'WriteDMAExt': 2,
          'ReadVerifyExt': 4,
                  }
      for key in WRDMAExt:
         if WRDMAExt[key] == wrCmd:
            wrmode = WRDMAExtNum[key]
            break
      return wrmode

   #---------------------------------------------------------------------------------------------------------#
   def Idle(self, Delay = 0):
      if self.dut.IsSDI:
         objMsg.printMsg('SDI Idle')
         from base_SATA_ICmd_Params import Idle
         tempPrm = Idle.copy()
         return self.translateStReturnToCPC(self.St(tempPrm))

      objMsg.printMsg('SPT Idle Delay=%s' % Delay)
      if not testSwitch.YARRAR:  # 5>p command not supported by YarraR
         sptCmds.enableDiags()
         self.oSerial.sendDiagCmd('/5p82', printResult=True)
      time.sleep(Delay)
      return {'LLRET':OK, 'SCNT': 0xFF}

   #---------------------------------------------------------------------------------------------------------#
   def IdleImmediate(self):
      if self.dut.IsSDI:
         objMsg.printMsg('SDI IdleImmediate')
         from base_SATA_ICmd_Params import IdleImmediate
         tempPrm = IdleImmediate.copy()
         return self.translateStReturnToCPC(self.St(tempPrm))

      objMsg.printMsg('SPT IdleImmediate')
      return self.Idle()

   #---------------------------------------------------------------------------------------------------------#
   def Standby(self, Delay = 0):
      if self.dut.IsSDI:
         objMsg.printMsg('SDI Standby')
         from base_SATA_ICmd_Params import Standby
         tempPrm = Standby.copy()
         return self.translateStReturnToCPC(self.St(tempPrm))

      objMsg.printMsg('SPT Standby Delay=%s' % Delay)
      if not testSwitch.YARRAR:
         self.oSerial.sendDiagCmd(POWER_MODE_STANDBY, printResult=True)
      time.sleep(Delay)
      return {'LLRET':OK, 'SCNT': 0x00}

   #---------------------------------------------------------------------------------------------------------#
   def StandbyImmed(self):
      if self.dut.IsSDI:
         objMsg.printMsg('SDI StandbyImmed')
         from base_SATA_ICmd_Params import StandbyImmed
         tempPrm = StandbyImmed.copy()
         return self.translateStReturnToCPC(self.St(tempPrm))

      objMsg.printMsg('SPT StandbyImmed')
      return self.Standby()

   #---------------------------------------------------------------------------------------------------------#
   def Sleep(self, Delay = 0):
      if self.dut.IsSDI:
         objMsg.printMsg('SDI Sleep')
         from base_SATA_ICmd_Params import Sleep
         tempPrm = Sleep.copy()
         return self.translateStReturnToCPC(self.St(tempPrm))

      objMsg.printMsg('SPT Sleep')
      if not testSwitch.YARRAR:
         self.oSerial.sendDiagCmd(POWER_MODE_SLEEP, printResult=True)
      return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def CheckPowerMode(self):
      objMsg.printMsg('SPT CheckPowerMode')
      return PASS_RETURN

   #---------------------------------------------------------------------------------------------------------#
   def ReadSectorsExt(self, startLBA, endLBA, sectCnt = 256):
      self.ClearBinBuff() 
      return self.SequentialReadDMAExt(startLBA, endLBA, sectCnt, sectCnt, STAMP_FLAG = 0, COMPARE_FLAG = 0)

   #---------------------------------------------------------------------------------------------------------#
   def IdleAPMTest(self, apmDrive, minLBA, maxLBA, loopTime, apmMinWait, apmMaxWait, napmWait, udmaSpeed = None, mode2848 = None, bytePattern = "0x00", lulWait = None):

      if apmDrive or testSwitch.virtualRun:   # applies to APM drives
         objMsg.printMsg('SPT IdleAPMTest APM not supported')
         return PASS_RETURN
      else:
         objMsg.printMsg('SPT IdleAPMTest non-APM mode')

         startTime = time.time()
         while True:
            if time.time() - startTime > loopTime:
               break

            sptCmds.enableDiags()
            self.StandbyImmed()
            time.sleep(napmWait)
            self.ClearBinBuff()
            self.FillBuffer(1,0,bytePattern)

            res = self.SequentialWriteDMAExt(minLBA, maxLBA, 256, 256, False)
            if res['LLRET'] != OK:
               return FAIL_RETURN
            res = self.SequentialReadDMAExt(minLBA, maxLBA, 256, 256, 0, 1, False)
            if res['LLRET'] != OK:
               return FAIL_RETURN

            self.IdleImmediate()
            time.sleep(napmWait)
            res = self.SequentialWriteDMAExt(minLBA, maxLBA, 256, 256, False)
            if res['LLRET'] != OK:
               return FAIL_RETURN

            self.Sleep()
            time.sleep(napmWait)
            self.HardReset()

            res = self.SequentialWriteDMAExt(minLBA, maxLBA, 256, 256, False)
            if res['LLRET'] != OK:
               return FAIL_RETURN
            res = self.SequentialReadDMAExt(minLBA, maxLBA, 256, 256, 0, 1, False)
            if res['LLRET'] != OK:
               return FAIL_RETURN

         return PASS_RETURN


ICmd = SPT_ICmd()

import Rim
if Rim.objRimType.CPCRiser():
   from CPC_ICmd import CPC_ICmd
   import base_CPC_ICmd_Params

   class CPC_SPT_ICmd(SPT_ICmd, CPC_ICmd):

      def __init__(self, params = {}, objPwrCtrl = None):
         CPC_ICmd.__init__(self, base_CPC_ICmd_Params, objPwrCtrl)
         SPT_ICmd.__init__(self, params, objPwrCtrl)

elif Rim.objRimType.IOInitRiser() and Rim.objRimType.baseType in Rim.SATA_RiserBase:
   from SATA_ICmd import SATA_ICmd

   class SATA_SPT_ICmd(SPT_ICmd, SATA_ICmd):

      def __init__(self, params = {}, objPwrCtrl = None):
         objMsg.printMsg("class SATA_SPT_ICmd")

         SATA_ICmd.__init__(self, params, objPwrCtrl)
         SPT_ICmd.__init__(self, params, objPwrCtrl)

