#-----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2002, All rights reserved                     #
#-----------------------------------------------------------------------------------------#

##############################################################################
#
# $RCSfile: ReliRamTest.py $
# $Revision: #1 $
# $Id: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReliRamTest.py#1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReliRamTest.py#1 $
#
##############################################################################

from ReliFunction import *
from ReliFailCode import *
from LBARegions import *
import MessageHandler as objMsg
import sys, os
import random




OK      = 0
FAIL    = -1
UNDEF   = 'UNDEF'
WBF     = 1  # Write  Buffer select on FillBuff*** commands
RBF     = 2  # Read   Buffer select on FillBuff*** commands
BWR     = 3  # Both Write and Read Buffer select on FillBuff*** commands
SBF     = 4  # Serial Buffer select on FillBuff*** commands


class CDramScreenTest:
   #----------------------------------------------------------------------------------------------------
   def __init__(self, maxLBA):

      self.oFC = CReliFailCode()       # DT
      
      self.data = {}
      self.failLLRET = 0
      self.failCode = 0
      self.failStatus = 0
      self.ZeroLBA = 200000
      self.XferRate = 0x45
      self.ConfigName = CN
      # create four virtual equal-sized 'zones'
      self.objLBARegions = CLBARegions(maxLBA)
      self.regions = self.objLBARegions.regions
      objMsg.printMsg( "-----------------------------CIT Dram Screen-----------------------------------------------" )
      #StartTime('Dram Screen Test', 'funcstart')
      objMsg.printMsg('Custom LBA Rd/Wr Regions: %s' % `self.regions`)
      
      #SetIntfTimeout(10000)
      #SetFeatures(0x55) # disable read look ahead
      #SetFeatures(0x02)['LLRET'] # enable write cache
   
   #----------------------------------------------------------------------------------------------------
   def run(self):
      result = OK
      driveattr = {}
      failure = 'IDT Ram Miscompare'    # default
      
#      if ConfigVars.has_key('CIT Dram Screen') == 0 or \
#            ConfigVars['CIT Dram Screen'][0] != 'ON' or \
#               len(ConfigVars['CIT Dram Screen']) < 2:
#         objMsg.printMsg('DRAM_SCREEN_TEST is Not ON Or Has < 2 params.  Dram Screen Test Not Run')
#         return OK
#      
#      product = ConfigVars['CIT Dram Screen'][1]
#      objMsg.printMsg('Run DramScreenTest Test For %s' % product)
#      
#      selectList = ['TONKA1','MERCURY','BOTH_TONKA', 'TONKA2', 'VENUS']
#      
#      if ConfigVars['CIT Dram Screen'][1] not in selectList and product != 'TONKA2':
#         objMsg.printMsg('%s Not In the List %s. Dram Screen Test Not Run' %(ConfigVars['CIT Dram Screen'][1], selectList))
#         return OK
      
      # this section controls the sequence for the test
      try:
         #if product in ['TONKA2', 'BOTH_TONKA']:           # Tonka 2
         #self.doRandomWRPIO()
         #if product in selectList: # Tonka 1 and MERCURY or Tonka 2 if needed
            #self.doWalkingBitSeqWRDMA() # commented out due to CPC issues
         self.doRandomWRDMA()
            
            # DT190809 Skip to avoid Buffer problem 13088
            #objMsg.printMsg('>>>>> Skip doRandomWRDMAExtBuffer !!!')
         self.doRandomWRDMAExtBuffer()
         self.doSeqWriteThenReadDMA()
            #self.doRandomWRDMAIncDecPattern()   ### not effective - kartik
            #self.doRandSeedSeqWRDMA()     ### not effective - kartik
            #self.doSeqWRDMARandScnt()     ### not effective - kartik
         driveattr['DramScrnattr'] = "PASS"

      except IOError:
         result = FAIL
         lastException, lastValue = sys.exc_info()[:2]
         objMsg.printMsg('Exception Traceback: %s - %s' % (lastException, lastValue))
         #driveattr['failcode'] = 12513 
         failure = 'Cit Not Buff_Cmp'   
         self.failCode = self.oFC.getFailCode(failure)
#         if self.data.has_key('LBA') == 0: self.data['LBA'] = '0' 
#         if self.data.has_key('STS') == 0: self.data['STS'] = '00' 
#         if self.data.has_key('ERR') == 0: self.data['ERR'] = '00'           
#         if self.data.has_key('LLRET'): self.failLLRET = self.data['RESULT']   
#         self.testEndTime = time.time()
#         self.failStatus = ('STS%s-ERR%s' % (int(self.data['STS']), int(self.data['ERR']) ))
#         driveattr['IDT_FAIL_TTF'] = timetostring(self.testEndTime-self.testStartTime)
#         driveattr['IDT_FAIL_SEQ'] = failure
#         driveattr['IDT_FAIL_LBA'] = data['LBA']
#         driveattr['IDT_FAIL_CODE'] = self.failCode
#         driveattr['IDT_FAIL_LLRET'] = self.failLLRET
#         driveattr['IDT_FAIL_STATUS'] = self.failStatus


      except:
         result = FAIL
         lastException, lastValue = sys.exc_info()[:2]
         objMsg.printMsg('Exception Traceback: %s - %s' % (lastException, lastValue))
         objMsg.printMsg(`self.data`)
         #driveattr['failcode'] = failcode['Cit Not Buff_Cmp']
         #driveattr['failcode'] = 12513 
         failure = 'Cit Not Buff_Cmp'

         if self.data.has_key('RESULT'):
            if self.data['RESULT'].find('AAU_MISCOMPARE') >= 0:
               #driveattr['failcode'] = 12485 #self.failCodeDict['Cit Buff Miscompare']
               failure = 'Cit Buff Miscompare'
               
            elif self.data['RESULT'].find('AAU_BITMISCOMPARE') >= 0:
               #driveattr['failcode'] = 12705 #self.failCodeDict['Cit Bit Miscompare']
               failure = 'Cit Bit Miscompare'

         self.failCode = self.oFC.getFailCode(failure)
         objMsg.printMsg('Dram Screen Test Failed')
#         if self.data.has_key('LBA') == 0: self.data['LBA'] = '0' 
#         if self.data.has_key('STS') == 0: self.data['STS'] = '00' 
#         if self.data.has_key('ERR') == 0: self.data['ERR'] = '00'           
#         if self.data.has_key('LLRET'): self.failLLRET = self.data['RESULT']   
#         self.testEndTime = time.time()
#         self.failStatus = ('STS%s-ERR%s' % (int(self.data['STS']), int(self.data['ERR']) ))
#         driveattr['IDT_FAIL_TTF'] = timetostring(self.testEndTime-self.testStartTime)
#         driveattr['IDT_FAIL_SEQ'] = failure
#         driveattr['IDT_FAIL_LBA'] = data['LBA']
#         driveattr['IDT_FAIL_CODE'] = self.failCode
#         driveattr['IDT_FAIL_LLRET'] = self.failLLRET
#         driveattr['IDT_FAIL_STATUS'] = self.failStatus
      # DT
      #return result
      return result, self.data, failure
   #----------------------------------------------------------------------------------------------------
   def doRandomWRPIO(self):
      objMsg.printMsg('***** Random Write Read PIO *****')
      for self.patternfile in ConfigVars[CN]['CIT T2 Patt']:

         filename = os.path.join(UserDownloadsPath, self.ConfigName, self.patternfile)
         #objMsg.printMsg('UserDownloadPath=%s, filename=%s, patternfile=%s' % (UserDownloadsPath, filename, patternfile))

         self.patternfile = open(filename,'rb')
         try:
            patdata = self.patternfile.read()
            objMsg.printMsg('Filling Buffer With Pattern File :%s' % filename)
            ICmd.ClearBinBuff(WBF)
            ICmd.FillBuffer(WBF, 0, patdata)
         finally:
            self.patternfile.close()

         #startLBA, endLBA = self.objLBARegions.getRandRegion() # get one of the zones randomly
         #startLBA = 0; endLBA = ConfigVars[CN]['Fin ZeroLBAs']
         startLBA = 0; endLBA = self.ZeroLBA
         minScnt = 254; maxScnt = 256; loopCnt = 250
         feature_modes = [0x08, 0x09]     #PIO mode 0 and mode 1
         piomodes = {0x08:'PIO Mode 0', 0x09:'PIO Mode 1'}
         for mode in feature_modes:
            objMsg.printMsg('Feature Mode is 0x%02X' % mode)
            if ICmd.SetFeatures(0x03, mode)['LLRET'] != OK: # set PIO mode
               raise
            objMsg.printMsg('Set Feature in DramScreenTest to 0x%02X  %s  Passed' % (mode, piomodes[mode]))
            objMsg.printMsg('Start RAND WriteRead PIO: startLBA=%s endLBA=%s minScnt=%d maxScnt=%d loopCnt=%d Compare=1, Stamp=0' % (startLBA, endLBA, minScnt, maxScnt, loopCnt))
            ICmd.ClearBinBuff(RBF)
            self.data = ICmd.RandomWriteReadLBA(startLBA, endLBA, minScnt, maxScnt, loopCnt, stampFlag=0, compareFlag=1)
            if self.data['LLRET'] != OK:
               raise
   
   #----------------------------------------------------------------------------------------------------
   def doRandomWRDMA(self):
      objMsg.printMsg('***** Random Write Read DMA *****')
      ICmd.SetFeatures(0x03, self.XferRate) # set DMA transfer rate
      #startLBA, endLBA = self.objLBARegions.getRandRegion() # get one of the zones randomly
      #startLBA = 0; endLBA = ConfigVars[CN]['Fin ZeroLBAs'] - 256
      startLBA = 0; endLBA = self.ZeroLBA - 256
      minScnt = 250; maxScnt = 256; loopCnt = 500
      #-------------------------------------------------------------------------------------------------
      for self.patternfile in ConfigVars[CN]['CIT Dram Screen'][2:]:
         filename = os.path.join(UserDownloadsPath, self.ConfigName, self.patternfile)
         objMsg.printMsg('UserDownloadPath=%s, filename=%s, pattern=%s' % (UserDownloadsPath, filename, self.patternfile))
         #try:
         self.patternfile = open(filename,'rb')
         patdata = self.patternfile.read()
         self.patternfile.close()
         objMsg.printMsg('Filling Buffer With Pattern File :%s' % filename)
         ICmd.ClearBinBuff(WBF)
         ICmd.FillBuffer(WBF, 0, patdata)
         #finally:
         self.patternfile.close()
         #---------------------------------------------------------------------------------------------
         ICmd.ClearBinBuff(RBF)
         objMsg.printMsg('Start RAND WriteRead DMA: startLBA=%s endLBA=%s minScnt=%d maxScnt=%d loopCnt=%d Compare=1, Stamp=0' % (startLBA, endLBA, minScnt, maxScnt, loopCnt))
         self.data = ICmd.RandomWRDMAExt(startLBA, endLBA, minScnt, maxScnt, loopCnt, stampFlag=0, compareFlag=1)
         if self.data['LLRET'] != OK:
            raise
   
   #----------------------------------------------------------------------------------------------------
   def doSeqWriteThenReadDMA(self):
      objMsg.printMsg('***** Sequential First Write Then Read DMA *****')
      ICmd.SetFeatures(0x03, self.XferRate) # set DMA transfer rate
      #-------------------------------------------------------------------------------------------------
      for self.patternfile in ConfigVars[CN]['CIT Dram Screen'][2:]:
         filename = os.path.join(UserDownloadsPath, self.ConfigName, self.patternfile)
         try:
            self.patternfile = open(filename,'rb')
            patdata = self.patternfile.read()
            self.patternfile.close()
            objMsg.printMsg('Filling Buffer With Pattern File :%s' % filename)
            ICmd.ClearBinBuff(WBF)
            ICmd.FillBuffer(WBF, 0, patdata)
         finally:
            self.patternfile.close()
            
         for (locn, zone) in self.regions.items():
            objMsg.printMsg('Zone %s ----' % `zone`)
            random.seed() # this seeds with current time
            startLBA = random.randint(*zone)
            if startLBA > 200000:
               startLBA = 0 
            endLBA = min(startLBA+64*1024, zone[1])
            if endLBA > 200000:
               endLBA = 200000
            stepLBA = sectCnt = 256
            objMsg.printMsg('Start Write DMA: startLBA=%s endLBA=%s stampFlag=0' % (startLBA, endLBA))
            self.data = ICmd.SequentialWriteDMAExt(startLBA, endLBA, stepLBA, sectCnt, stampFlag=0)
            if self.data['LLRET'] != OK:
               raise
            ICmd.ClearBinBuff(RBF)
            objMsg.printMsg('Start Read DMA: startLBA=%s endLBA=%s compareFlag=1 stampFlag=0' % (startLBA, endLBA))
            self.data = ICmd.SequentialReadDMAExt(startLBA, endLBA, stepLBA, sectCnt, stampFlag=0, compareFlag=1)
            if self.data['LLRET'] != OK:
               raise
   
   #----------------------------------------------------------------------------------------------------
   def doWalkingBitSeqWRDMA(self):
      # Walking bit patterns implemented by Schumacher
      ICmd.SetFeatures(0x03, self.XferRate) # set DMA transfer rate
      objMsg.printMsg('***** Walking Bit Pattern Seq Write Read DMA *****')
      for (locn, zone) in self.regions.items():
         objMsg.printMsg('Zone %s ----' % `zone`)
         random.seed()
         startLBA = random.randint(*zone)
         endLBA   = min(startLBA+64*1024, zone[1])
         minScnt  = 250
         maxScnt  = 256
         for pattern in [0xFFFFFFFEL, 0x00000001L,]:
            objMsg.printMsg('Start SEQ WriteRead DMA Roll LBA: startLBA=%s endLBA=%s minScnt=%s maxScnt=%s pattern=%08X compareFlag=1' % (startLBA, endLBA, minScnt, maxScnt, pattern))
            ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF) # clear write and read buffers since we are supplying pattern directly to CPC2 API
            self.data = ICmd.SeqWRDMARollPattern(startLBA, endLBA, minScnt, maxScnt, pattern, compareFlag=1)
            if self.data['LLRET'] != OK:
               raise
   
   #----------------------------------------------------------------------------------------------------
   def doRandomWRDMAExtBuffer(self):
      # OK try this now --- karthik -- inputs from Chu Son
      objMsg.printMsg('***** Random Write Read DMA (Extended Buffer Size) *****')
      ICmd.SetFeatures(0x03, self.XferRate) # set DMA transfer rate
      try:
         # DT140909 Reduce buffer size
         #buff_size_sectors = 16*1024 # the maximum we can go for RBF or WBF is 15MB
         buff_size_sectors = 512  
         objMsg.printMsg('>>> Make Alt Buffer size (sectors): %d' % buff_size_sectors)
         ICmd.MakeAlternateBuffer(0x03, buff_size_sectors) # set buffer size
         #startLBA = 0; endLBA = ID_data['Max_48lba']-1; loopCnt = 250
         #startLBA = 0; endLBA = ConfigVars[CN]['Fin ZeroLBAs'] - 256; loopCnt = 250
         startLBA = 0; endLBA = self.ZeroLBA - 256; loopCnt = 250
         ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
         ICmd.FillBuffRandom(WBF)
         objMsg.printMsg('Start RAND WriteRead DMA: startLBA=%s endLBA=%s BuffSize=%d LoopCnt=%d Compare=1 Stamp=0 FlushCache=0' % (startLBA, endLBA, buff_size_sectors, loopCnt))
         self.data = ICmd.RandomWRDMAExt(startLBA, endLBA, buff_size_sectors, buff_size_sectors, loopCnt, stampFlag=0, compareFlag=1, flushCache=0)
         if self.data['LLRET'] != OK:
            raise
      finally:
         objMsg.printMsg('Restore Primary Buffer')
         ICmd.RestorePrimaryBuffer(WBF)

   #----------------------------------------------------------------------------------------------------
   def doRandSeedSeqWRDMA(self):
      objMsg.printMsg('***** Random Seed Sequential Write Read DMA *****')
      ICmd.SetFeatures(0x03, self.XferRate) # set DMA transfer rate
      import binascii
      for (locn, zone) in self.regions.items():
         objMsg.printMsg('Zone %s ----' % `zone`)
         random.seed()
         st = startLBA = random.randint(*zone)
         endLBA = min(startLBA+64*1024/16, zone[1])
         end = 0 # init
         while end < endLBA:
            stepLBA  = sectCnt = 256 #random.randint(200, 256)
            end = st + sectCnt
            # generate pattern equal to size of sectcount
            pattern = ''
            for i in range(0, sectCnt*512):
               random.seed(st+i) # seed with lba number
               pattern += '%02X' % random.randint(0, 255)
            ICmd.ClearBinBuff(WBF)
            ICmd.FillBuffer(WBF, 0, binascii.unhexlify(pattern)) # fill write buffer with pattern
            ICmd.ClearBinBuff(RBF) # clear read buffer
            objMsg.printMsg('Start SEQ WriteRead DMA (Random LBA Seed): startLBA=%s endLBA=%s sectCnt=%s pattLen=%d Compare=1, Stamp=0' % (st, end, sectCnt, len(pattern)))
            self.data = ICmd.SequentialWRDMAExt(st, end, stepLBA, sectCnt, stampFlag=0, compareFlag=1)
            if self.data['LLRET'] != OK:
               raise
            st = end
   
   #----------------------------------------------------------------------------------------------------
   def doSeqWRDMARandScnt(self):
      objMsg.printMsg('***** Sequential Write Read DMA (Random Sector Count) *****')
      ICmd.SetFeatures(0x03, self.XferRate) # set DMA transfer rate
      for (locn, zone) in self.regions.items():
         objMsg.printMsg('Zone %s ----' % `zone`)
         random.seed()
         startLBA = random.randint(*zone)
         endLBA = min(startLBA+64*1024, zone[1])
         minScnt = 253;  maxScnt = 256
         ICmd.ClearBinBuff(WBF); ICmd.FillBuffRandom(WBF)
         ICmd.ClearBinBuff(RBF) # clear read buffer
         objMsg.printMsg('Start SEQ WriteRead DMA Random Sct Cnt: startLBA=%s endLBA=%s minScnt=%s maxScnt=%s Compare=1, Stamp=0' % (startLBA, endLBA, minScnt, maxScnt))
         self.data = ICmd.SeqWRDMARandScnt(startLBA, endLBA, minScnt, maxScnt, compareFlag=1)
         if self.data['LLRET'] != OK:
            raise

   #----------------------------------------------------------------------------------------------------
   def doRandomWRDMAIncDecPattern(self):
      objMsg.printMsg('***** Random Write Read DMA (Inc Dec Pattern) *****')
      ICmd.SetFeatures(0x03, self.XferRate) # set DMA transfer rate
      for seq in ['INC', 'DEC',]:
         startLBA = 0; endLBA = ID_data['Max_48lba']-1
         minScnt = 250; maxScnt = 256; loopCnt = 250
         ICmd.ClearBinBuff(WBF); ICmd.ClearBinBuff(RBF)
         if seq=='INC':
            ICmd.FillBuffInc(WBF)
         else:
            ICmd.FillBuffDec(WBF)
         objMsg.printMsg('Start RAND WriteRead DMA %s Pattern: startLBA=%s endLBA=%s minScnt=%s maxScnt=%s loopCnt=%d Compare=1 Stamp=0 FlushCache=0' % (seq, startLBA, endLBA, minScnt, maxScnt, loopCnt))
         self.data = ICmd.RandomWRDMAExt(startLBA, endLBA, minScnt, maxScnt, loopCnt, stampFlag=0, compareFlag=1, flushCache=0)
         if self.data['LLRET'] != OK:
            raise
   
   #----------------------------------------------------------------------------------------------------
   def __del__(self):
      self.objLBARegions.clearWriteZero() # clear to zeros before exiting
      ICmd.SetFeatures(0xAA) # enable read-look-ahead feature
      #EndTime('Dram Screen Test', 'funcstart', 'funcfinish', 'functotal')


#*************************************************************************************************************
#*************************************************************************************************************
