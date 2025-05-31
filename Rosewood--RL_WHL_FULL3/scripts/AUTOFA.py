#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2013, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Serial Port Operation Module for Mack. Contains all test classes (blocks) that support
#              state machine implementation of the manufacturing test process.
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AUTOFA.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AUTOFA.py#1 $
# Level: 2
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import MessageHandler as objMsg
from Servo import CServo, CServoOpti, CServoFunc, CServoScreen
import Utility
import types, time, sys, re, traceback
import ScrCmds, sptCmds
from State import CState
from Process import CProcess
from FSO import CFSO
from TestParameters import *
from PowerControl import objPwrCtrl
from sptCmds import comMode
from Rim import objRimType
from TestParamExtractor import TP
import serialScreen
import re, MathLib
import Utility
from Codes import fwConfig
import os

###########################################################################################################
#
#         Auto FA Function support
#
###########################################################################################################

#failHead = -1

class CDiagSF3Mode:
   """
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      self.funlist = [
                      ['InitAutoFA',dict()],
                      ['V5Check',dict()],
                      ['PCBACheck',dict()],
                      ['PreampCheck', dict()],
                      #['DrvTempCheck', dict()],
                      ['SpinUpCheck', dict()],
                      ['MRCheck', dict()],
                      ['HeadLULCheck', dict()],
                      #['HdMediaChk',dict()],
                      ['PreampFaultChk', dict()],
                     # ['AGC_SCRN', dict()],

                      ['headSwitch', dict()],
                      ['PES_Check',dict()],
                      ['BERVsWrtHeater',dict()],
                      ['BERVsClearance', dict()],
                      ['AGC_SCRN', dict()],
                      ['DeltaMRChk', dict()],
                      ['DeltaVGA', dict()],
                      ['CollectServoCnt', dict()],
                      ['InstabilityTest', dict()],
                      ['BERCheck', dict()],
                      ['BodeCheck', dict()],
                     ]
      if testSwitch.ANGSANAH:
         funlist.insert(1,['BERcollect' ,dict()])

      self.objProc = CProcess()
      self.oUtility = Utility.CUtility()
      self.RRO_List = params['RRO_List']
      self.NRRO_List = params['NRRO_List']
      self.RAW_RO_List = params['RAW_RO_List']
      self.symaddr = {}
      self.minspeed = 0
      self.failHead = []
      self.failMedia = []
      self.SupressOutput = 0
      if not testSwitch.ANGSANAH:
         servosym = fwConfig[self.dut.driveattr['PART_NUM']]['SFWP'].replace('_','').replace('.zip','.sym')
      else:
         servosym = ''.join(re.split('_|\.',fwConfig[self.dut.driveattr['PART_NUM']]['SFWP'])[:2])+".sym"
      self.ServoSymfilePath = os.path.join(ScrCmds.getSystemDnldPath(),  servosym)
   #-------------------------------------------------------------------------------------------------------
   def Supress_Output(self):
      self.SupressOutput = 1
   #-------------------------------------------------------------------------------------------------------
   def ClearSupressOutput(self):
      if self.SupressOutput == 1:
         self.SupressOutput = 0
   #-------------------------------------------------------------------------------------------------------   
   def DumpLoopCode(self):
      
      self.GetSymbolOffsetValue("LoopCode",43,2,report=1)
      self.GetSymbolOffsetValue("AGC Fly Height",110,2,report=1)
      
   #------------------------------------------------------------------------------------------------------- 
   def GetServoSectorError(self,ServoName="None",SymOffset=0,NumLoc=0):
      ServoCollection = {}
      self.objProc.St({'test_num':11, 'prm_name':ServoName,'SYM_OFFSET': SymOffset, 'CWORD1':512, 'timeout':10, 'NUM_LOCS': NumLoc,'stSuppressResults': self.SupressOutput,'DblTablesToParse':['P011_SV_RAM_RD_BY_OFFSET']})
      for hd in range(NumLoc+1):
         ServoCollection.setdefault(ServoName,{})[hd] = int(self.dut.objSeq.SuprsDblObject['P011_SV_RAM_RD_BY_OFFSET'][-1-NumLoc+hd]['READ_DATA'],16)

      return ServoCollection
   #-------------------------------------------------------------------------------------------------------   
   ServoSectorErrorSymbolDict= {
      'Agc BpFilter Trip Error'          : 231,
      'Agc Delta Trip'                   : 57,
      'Agc Running Average Trip Error'   : 29,
      'Lv Detected Shock'                : 106,
      'Observer Sector Error'            : 7,
      'Observer Sector Error Velocity'   : 167,
      'Pes Detected Shock'               : 250,
      'Predicted Offtrack'               : 251,
      'False Predicted Offtrack'         : 252,
      'Rro Parity Error'                 : 259,
      'Timing Mark Not Detected'         : 37,
      'Timing Mark Not Detected Velocity': 167,
      'Unsafe Error Ontrack'             : 109
   }   
   #-------------------------------------------------------------------------------------------------------
   def DumpServoErrorCount(self,dumpOption=1, InitError={}):
      ServoCollection = {}
     
      for ServoError in self.ServoSectorErrorSymbolDict:
         ServoCollection.update(self.GetServoSectorError(ServoError,self.ServoSectorErrorSymbolDict[ServoError],self.dut.imaxHead-1))

      if (dumpOption & 0x1):
         objMsg.printMsg("-" *60)
         objMsg.printMsg("Auto FA:%35s        Hd0      Hd1" % 'Servo Sector Error')
         for ServoError in self.ServoSectorErrorSymbolDict:
            if (self.dut.imaxHead == 2):
               objMsg.printMsg("        %35s   %8d %8d" %(ServoError, ServoCollection[ServoError][0],ServoCollection[ServoError][1])) # temporary hard coded to 2 header
            else:
               objMsg.printMsg("        %35s   %8d" %(ServoError, ServoCollection[ServoError][0])) # temporary hard coded to 1 header

         objMsg.printMsg("-" *60)
         
      if (dumpOption & 0x2):
         objMsg.printMsg("Auto FA:%35s        Hd0      Hd1" % 'Delta Servo Sector Error')
         for ServoError in self.ServoSectorErrorSymbolDict:
            if (self.dut.imaxHead == 2):
               objMsg.printMsg("        %35s   %8d %8d" %(ServoError, (ServoCollection[ServoError][0]-InitError[ServoError][0]),(ServoCollection[ServoError][1]-InitError[ServoError][1]))) # temporary hard coded to 2 header
            else:
               objMsg.printMsg("        %35s   %8d" %(ServoError, (ServoCollection[ServoError][0]-InitError[ServoError][0])))# temporary hard coded to 1 header
      return ServoCollection
   def InitAutoFA(self,**args):
      self.Supress_Output()
      self.DumpLoopCode()
      self.DumpServoErrorCount()
      self.ClearSupressOutput()
   #-------------------------------------------------------------------------------------------------------
   def BERcollect(self, **args):
      if testSwitch.RUN_T250_3_TIMES_ON_FAILED_DRIVES:
         if self.dut.failureData[0][2] in [13404, 13406] and self.dut.nextOper in ['PRE2']:
           PrintSumtable = 1
           self.objProc.St(TP.setZapOnPrm_011)  #ZAP ON
           t250prm = {'test_num':250,'RETRIES': 50, 'prm_name':'RUN_T250','ZONE_POSITION': 198, 'spc_id': 9011, 'MAX_ERR_RATE': -90, 'TEST_HEAD': 255, 'NUM_TRACKS_PER_ZONE': 10, 'SKIP_TRACK': 200, 'TLEVEL': 0, 'MINIMUM': -22, 'ZONE_MASK_EXT': (0L, 0), 'CWORD1': 387, 'timeout': 2000, 'CWORD2': (4,), 'MAX_ITERATION': 208, 'ZONE_MASK': (16900L, 2066), 'WR_DATA': 0}
           spcid = [9011,9012,9013]
           
           for i in spcid:
              t250prm['spc_id'] = i
              try:
                 self.objProc.St(t250prm)
              except ScriptTestFailure, (failureData):
                 if failureData[0][2] in [10632]:
                    pass
                 else:
                    PrintSumtable = 0
           self.objProc.St(TP.setZapOffPrm_011)
           if PrintSumtable:
              testzone = [1,4,11,18,25,30]
              ber = {}
              for zn in testzone:
                 ber[zn] = 1.0
              RawSovaErrRate = [[ber.copy() for i in range(self.dut.imaxHead)] for j in range(3)]
              k = 0
              for j in spcid:
                 
                 p250ErrRateTbl = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').chopDbLog('SPC_ID', 'match',str(j))
                 for entry in p250ErrRateTbl:
                    
                    iZone = int(entry.get('DATA_ZONE'))
                    iHead = int(entry.get('HD_LGC_PSN'))               
                    RawSovaErrRate[k][iHead][iZone] = round(float(entry.get('RAW_ERROR_RATE')),3)
                 k += 1
              #objMsg.printMsg("entry = %s" %RawSovaErrRate)
              ScriptComment('AUTOFA_DBS_MTRIX_BY_ZONE' , writeTimestamp = 0)
              ScriptComment('%-17s%-17s%-17s%-17s%-17s%-17s%-17s%-17s'%('HEAD', 'ZONE', 'BER1', 'BER2','BER3','MIN','MAX','MEAN'), writeTimestamp = 0)
              for hd in  xrange(self.dut.imaxHead):
                 for zn in testzone:
                    berList = [1.0]*(len(spcid))
                    for k in xrange(len(spcid)):
                       berList[k] = RawSovaErrRate[k][hd][zn]
                    ScriptComment('%-17s%-17s%-17s%-17s%-17s%-17s%-17s%-17s'%(hd, zn, berList[0], berList[1], berList[2], min(berList), max(berList), round(sum(berList)/len(berList),3)),writeTimestamp = 0)

   #-------------------------------------------------------------------------------------------------------  
   def V5Check(self,**args):
      
      try:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      except:
         #if self.dut.EOS:
         #   self.dut.driveattr['POTENTIAL_CAUSE'] = 'EOS'
         (mV3,mA3),(mV5,mA5),(mV12,mA12)  = GetDriveVoltsAndAmps()
         objMsg.printMsg('AUTOFA: - 3V: (%d mV, %d mA)  5V: (%d mV, %d mA)  12V: (%d mV, %d mA)'%(mV3,mA3,mV5,mA5,mV12,mA12))
         if mV5 < 3000:
            self.dut.driveattr['POTENTIAL_CAUSE'] = 'EOS'
         return 1

      return 0
   #-------------------------------------------------------------------------------------------------------
   def PCBACheck(self,**args):
      try:
         self.objProc.St({'test_num':166,'CWORD1':0x800, 'timeout': 200,'stSuppressResults': self.SupressOutput,'DblTablesToParse':['P000_DRIVE_VAR_TABLE']})
      except:
         pass

   def SpinUpCheck(self,**args):

      self.objProc.St({'test_num':11,'prm_name':'SpinUp with Head in Ramp','PARAM_0_4':(768, 0, 0, 0, 0), 'timeout':120})
      self.getSymbolValue(name=['u16_MotorFailureCode'])

      if self.cmdstatcheck(11247) == 11247:
         self.dut.driveattr['POTENTIAL_CAUSE'] = 'COMP_NO_SPIN'
         return 1
      return 0
   #-------------------------------------------------------------------------------------------------------

   def PreampCheck(self, **args):

      self.objProc.St({'test_num':166,'prm_name':'Get Preamp','CWORD1':0x1000, 'timeout': 200})
      try:
         preamp_data = self.dut.dblData.Tables('P166_PREAMP_INFO').tableDataObj()[-1:]
      except:
         objMsg.printMsg('Auto FA:Attention!!! The table: P166_PREAMP_INFO does not exist')
         return 0
      PREAMP_MFGR = preamp_data[0].get('PREAMP_MFGR', 'N')
      PRE_AMP_VENDOR = int(DriveAttributes.get('PRE_AMP_VENDOR', 0))
      if not testSwitch.virtualRun:
         objMsg.printMsg('PRE_AMP_VENDOR:%d, PREAMP_MFGR:%s' % (PRE_AMP_VENDOR,PREAMP_MFGR))
         if (PRE_AMP_VENDOR in [1,6] and PREAMP_MFGR == 'TI') or (PRE_AMP_VENDOR == 3 and PREAMP_MFGR == 'LSI'):
            pass
         else:
            self.dut.driveattr['POTENTIAL_CAUSE'] = 'J1_PIN'
            return 1
      return 0

   #--------------------------------------------------------------------------------------------------------
   def DrvTempCheck(self, **args):

      certTemp = args.get('certTemp',0)
      if certTemp:
         self.objProc.St({'test_num':172, 'prm_name':'CERT TEMP', 'timeout': 200, 'CWORD1': (18,)})
         drive_temp_C = DriveVars['Cert_Temperature_Deg_C']

      else:
         self.objProc.St({'test_num':172, 'prm_name':'HDA TEMP', 'timeout': 200, 'CWORD1': (17,)})
         drive_temp_C = DriveVars['Drive_Temperature_Deg_C']

      if (drive_temp_C >= 127) or (drive_temp_C <= -128):
         self.dut.driveattr['POTENTIAL_CAUSE'] = 'PCBA'
         return 1
      objMsg.printMsg('Drive Temperature %s' %str(drive_temp_C))
      return 0

   #--------------------------------------------------------------------------------------------------------
   def MRCheck(self, **args):

      get_MR_Values_186={
         'test_num':186,
         'prm_name':'get_MR_Values_186',
         'timeout':600,
         'spc_id' : 1,
         'CWORD1' : (0x1002,),
         }
      try:
         self.objProc.St(get_MR_Values_186)
         biasTbl = self.dut.dblData.Tables('P186_BIAS_CAL2').tableDataObj()
         for entry in biasTbl[-self.dut.imaxHead:]:
            if float(entry['MRE_RESISTANCE']) < 100 or float(entry['MRE_RESISTANCE']) > 1000:
               objMsg.printMsg('Auto FA:CFM - HDC on Head %s'%entry['HD_PHYS_PSN'])
               self.failHead = list(str(entry['HD_PHYS_PSN']))
               self.dut.driveattr['POTENTIAL_CAUSE'] = 'HDC'
               raise
      except:
         return 1
      return 0

   #--------------------------------------------------------------------------------------------------------
   def HeadLULCheck(self, **args):

      OriginPGain = {}

      # load head without demon syc
      self.objProc.St({'test_num':11, 'prm_name':'Load','PARAM_0_4':(0x0F00, 0, 0, 0, 0),'timeout': 60})
      LoadPotentialCause = self.DisplayLoadProfile()
      if self.cmdstatcheck(14664) == 14664 or LoadPotentialCause:
         self.dut.driveattr['POTENTIAL_CAUSE'] = 'HEAD_LOAD_FAIL'
         if LoadPotentialCause:
            self.dut.driveattr['POTENTIAL_CAUSE'] = LoadPotentialCause
         objMsg.printMsg('Auto FA: Load Head Check fail')
         return 1
      objMsg.printMsg('Auto FA: Load Head Check pass')
      self.CheckRampState(AccessType = 1)
      # Unload head
      self.objProc.St({'test_num':11, 'prm_name':'UnLoad','PARAM_0_4':(0x0E00, 0, 0, 0, 0),'timeout': 60})
      self.DisplayUnLoadProfile()
      if self.cmdstatcheck(14665) == 14665:
         self.dut.driveattr['POTENTIAL_CAUSE'] = 'LOAD_HEAD_RETRACTED'
         objMsg.printMsg('Auto FA: UnLoad Head Check fail')
         return 1
      objMsg.printMsg('Auto FA: UnLoad Head Check pass')
      data = self.MRCheck()
      if data:
         objMsg.printMsg('Auto FA: MRR Check fail')
         return data
      else:
         objMsg.printMsg('Auto FA: MRR Check pass')
         self.CheckRampState(AccessType = 1)
         self.objProc.St({'test_num':11, 'prm_name':'UnLoad','PARAM_0_4':(0x0E00, 0, 0, 0, 0),'timeout': 60})

      for head in range(self.dut.imaxHead):
         objMsg.printMsg('Auto FA: Head = %d LoadUnLoadCheck' %head)
         # Set demon destination head
         self.objProc.St({'test_num':11, 'prm_name':"Demod Destination Head", 'ACCESS_TYPE': (2,), 'SYM_OFFSET': (192,), 'timeout': 10, 'WR_DATA': head, 'CWORD1': (1024,) })
         # Set seek destination head
         self.objProc.St({'test_num':11, 'prm_name':"Demod Destination Head", 'ACCESS_TYPE': (2,), 'SYM_OFFSET': (22,), 'timeout': 10, 'WR_DATA': head, 'CWORD1': (1024,) })
         OriginPGain[head] = self.GetPreampGain(head,report = 1)
         if OriginPGain[head] == 15:
            retryPGain = []
         else:
            retryPGain = [ i for i in xrange(OriginPGain[head]+4,15,4)]
            if 15 not in retryPGain:
               retryPGain.append(15)

         self.objProc.St({'test_num':11, 'prm_name':'Load','PARAM_0_4':(0x0F00, 1, 0, 0, 0),'timeout': 60})
         LoadPotentialCause = self.DisplayLoadProfile()
         if self.cmdstatcheck(14664) == 14664 or LoadPotentialCause:
            for loop in range(len(retryPGain)):
               objMsg.printMsg('Auto FA: HEAD LOAD UNLOAD retry with PGain = %d' %retryPGain[loop])
               self.SetPreampGain(head,retryPGain[loop])
               self.objProc.St({'test_num':11, 'prm_name':'Load','PARAM_0_4':(0x0F00, 1, 0, 0, 0),'timeout': 60})
               LoadPotentialCause = self.DisplayLoadProfile()
               if self.cmdstatcheck(14664) == 14664 or LoadPotentialCause:
                  continue
               else:
                  self.dut.driveattr['POTENTIAL_CAUSE'] = 'LOW_PREAMP_GAIN_HEAD'+str(head)
                  self.failHead= list(str(head))
                  objMsg.printMsg('Auto FA: Load Head with Sync Check fail')
                  return 1
            else:
               self.dut.driveattr['POTENTIAL_CAUSE'] = 'DEMOD_SYNC_FAIL_HEAD'+str(head)
               self.failHead =list(str(head))
               objMsg.printMsg('Auto FA: Load Head with Sync Check fail')
               return 1
         objMsg.printMsg('Auto FA: Load Head with Sync Check pass')
         self.CheckRampState(AccessType = 1)
         
         self.objProc.St({'test_num':11, 'prm_name':'UnLoad','PARAM_0_4':(0x0E00, 0, 0, 0, 0),'timeout': 60})
         self.DisplayUnLoadProfile()
         if self.cmdstatcheck(14665) == 14665:
            self.dut.driveattr['POTENTIAL_CAUSE'] = 'LOAD_HEAD_RETRACTED'
            objMsg.printMsg('Auto FA: UnLoad Head Check fail')
            return 1           
         objMsg.printMsg('Auto FA: UnLoad Head Check pass')
      self.objProc.St(TP.spindownPrm_2)
      return 0
   #--------------------------------------------------------------------------------------------------------
   def CheckRampState(self,AccessType,usestate = None):
      OnRamp = {'ON':1, 'OFF':0}
      if usestate != None and usestate not in OnRamp.keys():
         usestate = None
      address = self.GetAddrViaVars(symname='eLULState')
      ReadData= self.GetValuefromServoRam(address,AccessType)
      if usestate:
         state = OnRamp[usestate]
         if ReadData ^ state:
            return 1
         else:
            return 0
         
      if ReadData == 0:
         return 1
      elif ReadData == 1:
         objMsg.printMsg('Auto FA: HEAD_LOAD_ON_DISK')
      else:
         objMsg.printMsg('Auto FA:Attention!!! Ramp state = %s not equal to 1 or 0' %ReadData)
      return 0
   #--------------------------------------------------------------------------------------------------------
   def GetAddrViaVars(self,symname = ''):
      value = 0
      if self.symaddr.get(symname,None):
         return self.symaddr[symname]
 
      sym = open(self.ServoSymfilePath,  'rb')
      data = sym.read()
      sym.close()
      symline = data.split('\r\n')
     
      for l in range(len(symline)):
            if list(symline[l].split())[0] == symname:
               value = list(symline[l].split())[1]
               break
      self.symaddr[symname] = int(value,16)
      return int(value,16)
      
   #--------------------------------------------------------------------------------------------------------

   
   def LoadServoCalCheck(self, **args):
      Retry = 0
      PGain = 11
      Status = {}
      changedPG = 0
      failhead = []
      for head in range(self.dut.imaxHead):
         if Retry > 0:
            orgPGain = self.GetPreampGain(head)
         for loop in range(Retry+1):
            self.objProc.St({'test_num':11, 'prm_name':"Demod Destination Head", 'ACCESS_TYPE': (2,), 'SYM_OFFSET': (192,), 'timeout': 10, 'WR_DATA': head, 'CWORD1': (1024,),'stSuppressResults': self.SupressOutput}) 
            self.objProc.St({'test_num':11, 'prm_name':"Demod Destination Head", 'ACCESS_TYPE': (2,), 'SYM_OFFSET': (22,), 'timeout': 10, 'WR_DATA': head, 'CWORD1': (1024,) })
            self.objProc.St({'test_num':11, 'prm_name':"Demod Sync", 'PARAM_0_4': (0x100, 0, 0, 0, 0), 'timeout': 60,'stSuppressResults': self.SupressOutput})
            DemodHead = self.GetSymbolOffsetValue("Read Demod Head",192,2)
            LoopCode = self.GetSymbolOffsetValue("LoopCode",43,2)
            if ((LoopCode ==0x00 ) and (DemodHead == head)):
               objMsg.printMsg('Auto FA: Loop Code %d Actual Demod Head %d Expected Head %d ==> PASS' % (LoopCode , DemodHead,head))
               Status[head] = 0
               break
            else:
               objMsg.printMsg('Auto FA: Loop Code %d Actual Demod Head %d Expected Head %d ==> FAIL' % (LoopCode , DemodHead,head))
               
               if (Retry > 0) and (loop != Retry):
                  # Spin Up the Motor
                  objMsg.printMsg('Auto FA:Retry %d with motor spin up on ramp' %loop)
                  self.objProc.St({'test_num':11,'prm_name':'SpinUp with Head in Ramp','PARAM_0_4':(768, 0, 0, 0, 0), 'timeout':120,'stSuppressResults': self.SupressOutput})
                  # Load
                  self.objProc.St({'test_num':11, 'prm_name':'Load','PARAM_0_4':(0x0F00, 1, 0, 0, 0),'timeout': 60,'stSuppressResults': self.SupressOutput})
                  # Delay
                  time.sleep(10)
                  self.SetPreampGain(head,PGain)  
                  if PGain != orgPGain:
                     changedPG = 1
               else:
                  Status[head] = 1
         if changedPG:
            self.SetPreampGain(head,orgPGain)

      #unload head
      self.objProc.St({'test_num':11, 'prm_name':'UnLoad','PARAM_0_4':(0x0E00, 0, 0, 0, 0),'timeout': 60})
      for hd in Status.keys():
         if Status[hd]:
            failhead.append(str(hd))
      if len(failhead)>0:
         self.dut.driveattr['POTENTIAL_CAUSE'] = 'SEEK_CAL_FAIL_HEAD'
         self.failHead = failhead
         return 1
      else:
         return 0

   #---------------------------------------------------------------------------------------------------------
   def HdMediaChk(self, **args):

      try:
        self.objProc.St({'test_num':177,'prm_name':'prm_177','spc_id': 1, 'THRESHOLD2': (150,), 'HEAD_RANGE': (255,), 'timeout': 1800.0, 'THRESHOLD': (55,), 'TEST_CYL': (0, 9000), 'CWORD1': (4101,)})
      except:
        pass
      pCause,failHead,failMedia=self.HeadMediaCheck()
      if (pCause[0:4] != 'NONE'):
         self.failHead = failHead
         self.failMedia = failMedia
         self.dut.driveattr['POTENTIAL_CAUSE'] = pCause
         self.exit = 1
         return
    #---------------------------------------------------------------------------------------------------------
   def DemodSync(self,head=0,PGain=11,Retry=2):
      DemodHead = -1
      LoopCode = -7
      SupressOutput = 1
      PassFailStatus=1

      objMsg.printMsg('AD:Demod Sync Check at head %d ' %head)

      for loop in range (Retry):
         # Set Demon Destination Head
         self.objProc.St({'test_num':11, 'prm_name':"Demod Destination Head", 'ACCESS_TYPE': (2,), 'SYM_OFFSET': (192,), 'timeout': 10, 'WR_DATA': head, 'CWORD1': (1024,),'stSuppressResults': SupressOutput}) #,'stSuppressResults': supressOutput})
         # Demod Sync with 0x400
         self.objProc.St({'test_num':11, 'prm_name':"Demod Sync", 'PARAM_0_4': (0x400, 0, 0, 0, 0), 'timeout': 60,'stSuppressResults': SupressOutput})
         DemodHead = self.GetSymbolOffsetValue("Read Demod Head",192,1,2)
         LoopCode = self.GetSymbolOffsetValue("LoopCode",43,1,2)

         if ((LoopCode ==0x3F ) and (DemodHead == head)):
            PassFailStatus=1
            objMsg.printMsg('AD:Loop Code %d Actual Demod Head %d Expected Head %d ==> PASS' % (LoopCode , DemodHead,head))
            break
         else:
            objMsg.printMsg('AD:Loop Code %d Actual Demod Head %d Expected Head %d ==> FAIL' % (LoopCode , DemodHead,head))
            PassFailStatus=0
            if (Retry > 1):
               # Spin Up the Motor
               objMsg.printMsg('AD:Retry %d with motor spin up on ramp' %loop)
               self.objProc.St({'test_num':11,'prm_name':'SpinUp with Head in Ramp','PARAM_0_4':(768, 0, 0, 0, 0), 'timeout':120,'stSuppressResults': SupressOutput})
               # Load
               objMsg.printMsg('AD:Load Head')
               self.objProc.St({'test_num':11, 'prm_name':'Load','PARAM_0_4':(0x0F00, 1, 0, 0, 0),'timeout': 60,'stSuppressResults': SupressOutput})
               # Delay
               time.sleep(10)
               self.SetPreampGain(head,PGain)  #Set the default Preamp Gain to 11 (average for YARRABP is 11)
      return PassFailStatus

     #--------------------------------------------------------------------------------------------------------
   def ClearServoErrorCount(self):
      SupressOutput = 1
      for ServoError in self.ServoSectorErrorSymbolDict:
         self.objProc.St({'test_num':11, 'prm_name':ServoError,'SYM_OFFSET': self.ServoSectorErrorSymbolDict[ServoError], 'CWORD1':2048, 'WR_DATA': (0,),'timeout':10,'stSuppressResults': SupressOutput, 'MASK_VALUE': (3,)})
     #--------------------------------------------------------------------------------------------------------
   def FatalDemodCheck(self, testTracks=[100],goodHead=0,zone=3, numTestTracks = 1 ):

      if testSwitch.virtualRun:
         return
      #Initialize the
      objMsg.printMsg('AD:Test tracks %s'%(testTracks))
      skCntErr = [[0 for x in range(zone)] for y in range(self.dut.imaxHead)]
      self.ClearServoErrorCount()
      InitError=self.DumpServoErrorCount(0)


      for hd in range (self.dut.imaxHead):
         zonePos = 0
         #Demod on test Head to prevent head switch
         self.objProc.St({'test_num':11, 'prm_name':"Demod Destination Head", 'ACCESS_TYPE': (2,), 'SYM_OFFSET': (192,), 'timeout': 10, 'WR_DATA': hd, 'CWORD1': (1024,),'stSuppressResults': 1}) #,'stSuppressResults': supressOutput})
         self.objProc.St({'test_num':11, 'prm_name':"Demod Sync", 'PARAM_0_4': (0x400, 0, 0, 0, 0), 'timeout': 60,'stSuppressResults': 1})
         DemodHead = self.GetSymbolOffsetValue("Read Demod Head",192,1,2)
         if (DemodHead==hd):
            objMsg.printMsg('AD: Demod Head %d == Expected Head %d '%(DemodHead,hd))
         else:
            objMsg.printMsg('AD: Demod Head %d != Expected Head %d '%(DemodHead,hd))
         time.sleep(5)
         #
         for trk in testTracks:
            toterr=0
            #err=self.oServ.rsk(trk,goodHead)
            for tstrks in range(trk, trk+100*numTestTracks,100):
               err=self.oServ.rsk(tstrks,hd)
               if (err != 0):
                  toterr += 1
                  err=self.oServ.rsk(tstrks,goodHead)
                  if (err != 0):
                     objMsg.printMsg('AD: Error seek encounter on known good Track %d/Hd%d' %(tstrks,goodHead))
            skCntErr[hd][zonePos]=toterr
            zonePos+=1
      InitError=self.DumpServoErrorCount(2,InitError)

      return skCntErr
   #--------------------------------------------------------------------------------------------------------
   def findGoodTestTrack(self, hd=0,numzone=3,ignoreerr=0):
      tstTracks=[]
      goodtrks=[]
      self.oServ = CServo()
      status = 0
      GoodTrack=0
      objMsg.printMsg('Max Test Track %d '% min(self.dut.maxTrack))
      minTrack = 2000
      maxTrack = min(self.dut.maxTrack) - 20000
      TestRange = (maxTrack - minTrack)/(numzone-1)

      for pos in range (numzone):
         tstTracks.append(minTrack + TestRange*pos)

      for track in tstTracks:
         #objMsg.printMsg('Seek Track %d on hd %d '%(track, hd))
         err = self.oServ.rsk(track, hd)
         objMsg.printMsg('AD:rsk err: %d on hd %d track %d'%(err, hd, track))
         if (err==0 or ignoreerr == 1):
            goodtrks.append(track)
      return (goodtrks)
   #--------------------------------------------------------------------------------------------------------
   def HeadMediaCheck(self):
      if testSwitch.virtualRun:
         return 'NONE', -1, -1
      objMsg.printMsg('AutoFA:==== Head Demod Sync Check Start ====' )
      OriginPGain=[13 for x in range(self.dut.imaxHead)]
      HeadPFStatus=[1 for x in range(self.dut.imaxHead)]
      PassStatus =[1 for x in range(self.dut.imaxHead)]
      for head in range(self.dut.imaxHead):
         OriginPGain[head]=self.GetPreampGain(head)  #Set the default Preamp Gain to 13
         HeadPFStatus[head]=self.DemodSync(head)

      goodHead = 0
      for head in range(self.dut.imaxHead):
         Status='PASS'
         if (HeadPFStatus[head] == 0):
            Status = 'FAIL'
         else:
            goodHead = head
         objMsg.printMsg('AD:Head %d Demod Sync %s' %(head,Status))
      objMsg.printMsg('AD:Head Demod Sync Status %s' %HeadPFStatus)

      failHead = -1
      failMedia = -1
      fhead = []
      PotentialCause='NONE'
      if (HeadPFStatus != PassStatus):
         # Try to seek to 5 location to validate the head is bad
         testZone=5
         testTracks = self.findGoodTestTrack(goodHead,testZone)
         SkCntErr= self.FatalDemodCheck(testTracks,goodHead,testZone)
         objMsg.printMsg('AD:Total Seek Error %s' %(SkCntErr))
         failHdMsg=''
         failHead=-1
         for head in range(self.dut.imaxHead):
            failZoneCount=0
            for zone in range (testZone):
               if (SkCntErr[head][zone] == 0):
                  objMsg.printMsg('AD:Head %d PASS final Demod Sync' %head)
                  break
               else:
                  failZoneCount+=1
            if (failZoneCount == testZone):
               objMsg.printMsg('AD:Head %d FAIL final Demod Sync' %head)
               if (len(failHdMsg)>0):
                  failHdMsg+='&'
               failHdMsg+=str(head)
               fhead.append(str(head))
               
         if (len(fhead)>0):
            failHead=fhead
            PotentialCause = 'HEAD_H%s' %(failHdMsg)
            VgasAvg=self.CheckVGAS()
            #if (VgasAvg[failHead] < 200):
            #   PotentialCause = 'MEDIA_MDW-S%d_ALL' %(failHead)

      if (PotentialCause[0:4] == 'NONE'):
      # This is test to check the media MDW issue if Head has no prroblems
         objMsg.printMsg('AD:==== MEDIA MDW Check Start ====' )
         testZone = 5
         numTracks=10
         self.ClearServoErrorCount()
         testTracks = self.findGoodTestTrack(goodHead,testZone,1)
         SkCntErr=self.FatalDemodCheck(testTracks,goodHead,testZone,numTracks)
         objMsg.printMsg('AD:Total Seek Error for %d test tracks  => %s' %(numTracks,SkCntErr))
         # Following is new add portion to prevent over reject on bad track seek issue. his is
         BadHead=0
         DPGain=11
         for hd in range(self.dut.imaxHead):
            totFailZone = 0
            for zone in range (testZone):
               if (SkCntErr[head][zone] > numTracks*0.7):
                  totFailZone+=1
            if (totFailZone == testZone):     # If all zone failed to seek
               self.SetPreampGain(hd,DPGain)  #Set the default Preamp Gain to 11 (average for YARRABP is 11)
               BadHead+=1
         if (BadHead > 0):
            SkCntErr=self.FatalDemodCheck(testTracks,goodHead,testZone,numTracks)
            objMsg.printMsg('AD:Total Seek Error after Retry with higher default Pream Gain %d for %d test tracks  => %s' %(DPGain,numTracks,SkCntErr))

         failMsg=''
         for head in range(self.dut.imaxHead):
            totFailZone=0
            for zone in range (testZone):
               if (SkCntErr[head][zone] > numTracks*0.7):
                  failMedia=list(str(head))
                  totFailZone+=1
                  if (zone == 0):
                     failMsg+='OD'
                  elif (zone == testZone-1):
                     failMsg+='ID'
                  else:
                     failMsg+='MD'

            if (failMedia != -1):
               if (totFailZone < testZone-2):
                  PotentialCause = 'MEDIA_MDW-S%d_%s' % (failMedia,failMsg)
                  fmedia=[]
                  totidmedia=0
                  totodmedia=0
                  for head in range(self.dut.imaxHead):
                     if ( SkCntErr[head][0] > 0 ):
                        totodmedia+=1
                     if ( SkCntErr[head][testZone-1] > 0 ):
                        totidmedia+=1
                  if (totodmedia == self.dut.imaxHead or totidmedia == self.dut.imaxHead ):
                     failHead = -1
                     for head in range(self.dut.imaxHead):
                        fmedia.append(str(head))
                     failMedia=fmedia
                     PotentialCause = 'MEDIA_MDW-SALL_%s' % (failMsg)
                  
                  break
               else:
                  failHead = failMedia
                  failMedia = -1
                  PotentialCause = 'HEAD_USHD'
                  VgasAvg=self.CheckVGAS()
                  #if (VgasAvg[failMedia] < 200):
                  #   PotentialCause = 'MEDIA_MDW-S%d_ALL' %(failMedia)
                  break

         # if can't find bad media and observed minor seek error
         if (self.ec != 0 and PotentialCause[0:4] == 'NONE'):
            fineZones =5
            for head in range(self.dut.imaxHead):
               for zone in range (testZone):
                  if (SkCntErr[head][zone] > 0):
                     if (zone == 0):
                        startTrack = 1000
                     else:
                        startTrack = testTracks[zone-1]
                     SkCntErr[head][zone]=self.findBadBand(startTrack,testTracks[zone],head,goodHead)
                     if (SkCntErr[head][zone]):
                        PotentialCause = 'MEDIA_MDW-S%d_%s' % (head,'MD')
                        objMsg.printMsg('AD:Total Fine Seek Error for %d test tracks  => %s' %(numTracks,SkCntErr))
                        break

            objMsg.printMsg('AD:Total Fine Seek Error for %d test tracks  => %s' %(numTracks,SkCntErr))

      for head in range(self.dut.imaxHead):
         self.SetPreampGain(head,OriginPGain[head])  #to restore to the original Preamp Gain setting for the following test

      # Demod Sync to known good head to prevent the residue seek error to cause the following test to fail
      self.objProc.St({'test_num':11, 'prm_name':"Demod Destination Head", 'ACCESS_TYPE': (2,), 'SYM_OFFSET': (192,), 'timeout': 10, 'WR_DATA': goodHead, 'CWORD1': (1024,),'stSuppressResults': 1}) #,'stSuppressResults': supressOutput})
      # Demod Sync with 0x400
      self.objProc.St({'test_num':11, 'prm_name':"Demod Sync", 'PARAM_0_4': (0x400, 0, 0, 0, 0), 'timeout': 60,'stSuppressResults': 1})

      return PotentialCause,failHead,failMedia
   #---------------------------------------------------------------------------------------------------------
   def PreampFaultChk(self, **args):

      #objMsg.printMsg('-----------Auto FA Exec PreampFaultChk SF3 Mode----------')
      import binascii

      from Process import CCudacom
      from RdWr import CRdWr
      self.oCudacom = CCudacom()
      self.oServ = CServo()
      self.oRdWr = CRdWr()
      fail = 0

      PreampReg = [[0 for x in range(32)] for y in range(self.dut.imaxHead)]
      self.objProc.St(TP.masterHeatPrm_11['read'])
      MasterHeater=int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
      if (MasterHeater == 0):
         self.objProc.St(TP.masterHeatPrm_11['enable'])

      try:
         self.objProc.St(TP.spinupPrm_2)
         #self.objProc.St({'test_num':1, 'prm_name':'spinupPrm_1','timeout':100,"CWORD1" : (0x0,), "MAX_START_TIME" : (200,), "DELAY_TIME" : (50,),})
         for head in range(self.dut.imaxHead):
            self.oServ.wsk(2000, head)
            self.oRdWr.writetrack()
            buf, errorCode = self.oCudacom.Fn(1332,0,32)
            self.oCudacom.displayMemory(buf)
            data = binascii.hexlify(buf)
            # ========================= Fault Defination ==========================================
            # Low Supply Fault                  : Reg5 D0
            # Write Head Open                   : Reg6 D2 and is masked by setting Reg5 D2
            # Write Head Short to GND           : Reg6 D3 and is masked by setting Reg5 D3
            # TA Short/Open Fault               : Reg6 D4
            # Over Temperature                  : Reg6 D5 and is masked by setting Reg5 D5
            # Write without Heat                : Reg6 D6 and is masked by setting Reg5 D6
            # Write Heater Low or High Current  : Reg6 D7

            # WTOFFINRD bit set in Write mode   : Reg8 D0
            # Write Current Low in Output Driver: Reg8 D1 and is masked by setting Reg7 D1
            # Write Data Frequency too Low      : Reg8 D2 and is masked by setting Reg7 D2(Head)/Reg6 D1 and is masked by setting Reg5 D1(Common Point)
            # FOS                               : Reg8 D3 and is masked by setting Reg7 D3
            # Read Heater Low or High Current   : Reg8 D4
            # CD/TA Fault                       : Reg8 D5
            # SW                                : Reg8 D6
            # Serial Interface                  : Reg8 D7.

            # Write Input Path Open             : Reg30 D0
            for Reg in range (32):
               PreampReg[head][Reg]=int(data[Reg*2:Reg*2+2],16)
            objMsg.printMsg('H%d Preamp Reg %s' %(head,PreampReg[head]))
            if (PreampReg[head][6] and 0x04):
               self.dut.driveattr['POTENTIAL_CAUSE'] = 'PREAMP_STG_H%d' %(head)
               objMsg.printMsg('H%d Preamp Short To Ground ' %head)
               self.failHead=list(str(head))
               fail = 1
            elif (PreampReg[head][6] and 0x02):
               self.dut.driveattr['POTENTIAL_CAUSE'] = 'PREAMP_OPEN_H%d' %head
               objMsg.printMsg('H%d Write Head OPEN ' %head)
               self.failHead=list(str(head))
               fail = 1
            if (PreampReg[head][8] and 0x08):
               self.dut.driveattr['POTENTIAL_CAUSE'] = 'PREAMP_FOS_H%d' %head
               objMsg.printMsg('H%d Preamp FOS error ' %head)
               self.failHead=list(str(head))
               fail =1
      except:
         pass
      if (MasterHeater == 0):
         self.objProc.St(TP.masterHeatPrm_11['disable'])

      for head in range(self.dut.imaxHead):
         objMsg.printMsg('H%d Preamp Fault Reg6 %X Reg8 %X ' %(head, PreampReg[head][6],PreampReg[head][8]))
      if fail:
         objMsg.printMsg('POTENTIAL CAUSE %s Fail Head %d' %(self.dut.driveattr['POTENTIAL_CAUSE'],self.failHead))
         return 1
      else:
         return 0

   #---------------------------------------------------------------------------------------------------------
   def AGC_SCRN(self, **args):
      TrackFromID = 0x100

      #objMsg.printMsg('-----------Auto FA Exec AGC_SCRN SF3 Mode----------')
      SetFailSafe()
      try:
         oSrvFunc   = CServoFunc()
         oSrvOpti = CServoOpti()
         oUtil = Utility.CUtility()

         CFSO().getZoneTable()
         iTrack = min(self.dut.maxTrack)- TrackFromID
         self.data_AGCScrn = {}
         fail_head = 0
         for head in range(self.dut.imaxHead):
            self.data_AGCScrn[head]=[]
            iTrack = self.dut.maxTrack[head]- 100
            Temp_pesMeasurePrm_83_agc01 = TP.pesMeasurePrm_83_agc01.copy()
            Temp_pesMeasurePrm_83_agc01.update({'TEST_HEAD': head})
            Temp_pesMeasurePrm_83_agc01.update({'END_CYL':  oUtil.ReturnTestCylWord(iTrack)})
            Temp_pesMeasurePrm_83_agc01.update({'TEST_CYL': oUtil.ReturnTestCylWord(iTrack-101)})
            Temp_pesMeasurePrm_83_agc01.update({'AGC_MINMAX_DELTA': 10000})
            for i in range(2):
               try:
                  oSrvFunc.St(Temp_pesMeasurePrm_83_agc01)
               except:
                  iTrack -= 25410
                  objMsg.printMsg("AD: AGC SCREEN EXCEPTION")
                  Temp_pesMeasurePrm_83_agc01.update({'END_CYL':  oUtil.ReturnTestCylWord(iTrack)})
                  Temp_pesMeasurePrm_83_agc01.update({'TEST_CYL': oUtil.ReturnTestCylWord(iTrack-101)})
                  objMsg.printMsg(traceback.format_exc(),objMsg.CMessLvl.IMPORTANT)
                  continue

               self.get_AGCdata()
               break

         oSrvFunc.St(TP.spinupPrm_1)
         objMsg.printMsg("HEAD\tTRACK\tDELTA_AGC")
         hdList = []
         for head in range(self.dut.imaxHead):
            for index in range(len(self.data_AGCScrn[head])):
               objMsg.printMsg("%s\t%s\t%s" % (head,self.data_AGCScrn[head][index]['Track'],self.data_AGCScrn[head][index]['Delta_AGC']))
               if self.data_AGCScrn[head][index]['Delta_AGC'] > 150:
                  self.dut.driveattr['POTENTIAL_CAUSE'] = 'ID_MOTOR_HUB_DENT'
                  hdList.append(str(head))
         if len(hdList) > 0:
            self.failHead = list(set(hdList))
            return 1
      except:
         objMsg.printMsg("AD: AGC SCREEN EXCEPTION")
         objMsg.printMsg(traceback.format_exc(),objMsg.CMessLvl.IMPORTANT)
      ClearFailSafe()
      return 0

   def headSwitch(self, **args):
      if not self.dut.mdwCalComplete:
         return 0
      self.objProc.St(TP.spinupPrm_1)
      self.oServ = CServo()
      for hd in range(self.dut.imaxHead):
         tstTracks = [2000, self.dut.maxTrack[hd] / 2, self.dut.maxTrack[hd] - 20000]
         fail = 0
         for cyl in tstTracks:
            err = self.oServ.rsk(cyl, hd)
            objMsg.printMsg('AD:rsk err: %d on hd %d track %d'%(err, hd, cyl))
            if err:
               fail = 1
            else:
               fail = 0
            if fail:
               self.dut.driveattr['POTENTIAL_CAUSE'] = 'HDC'
               self.failHead = list(str(hd))
               objMsg.printMsg('AD:CFM - Cannot seek on surface %d'%hd)
               return 1
      return 0
   #---------------------------------------------------------------------------------------------------------
   def PES_Check(self, **args):
      if not self.dut.mdwCalComplete:
         return 0
      oSrvFunc   = CServoFunc()
      oUtil = Utility.CUtility()
      pesMeasurePrm_33 = oUtil.copy(TP.pesMeasurePrm_33)
      pesMeasurePrm_33['DblTablesToParse'] = 'P033_PES_HD2'
      pesMeasurePrm_33.update({'NUM_SAMPLES':  0})
      tstTracks = [2000, min(self.dut.maxTrack) / 2, min(self.dut.maxTrack) - 3000]
      for track in tstTracks:
         oSrvFunc.St(oUtil.overRidePrm(pesMeasurePrm_33,
                                        {'TEST_CYL':oUtil.ReturnTestCylWord(track),
                                         'END_CYL' :oUtil.ReturnTestCylWord(track),
                                        }
                                       )
                      )
      try:
         entries = self.dut.dblData.Tables('P033_PES_HD2').tableDataObj()[-self.dut.imaxHead*3:]
      except:
         objMsg.printMsg('AD:Attention!!! Table P033_PES_HD2 is not found')
         return 0

      for entry in entries:
         Hd = int(entry['HD_PHYS_PSN'])
         if Hd not in self.RRO_List.keys():
            self.RRO_List[Hd] = []
            self.NRRO_List[Hd] = []
            self.RAW_RO_List[Hd] = []
         self.RRO_List[Hd].append(float(entry['RRO']))
         self.NRRO_List[Hd].append(float(entry['NRRO']))
         self.RAW_RO_List[Hd].append(float(entry['RAW_RO']))
         if float(entry['RAW_RO']) > 20:
            objMsg.printMsg('AD:P033_PES_HD2 - RAW_RO > 20, jump out CInitialFA')
            return 1
      return 0
   def FindZone(self,quietMode=0):
      from Process import CCudacom
      import binascii
      self.oCudacom = CCudacom()
      buf, errorCode = self.oCudacom.Fn(1204)
      hZone = binascii.hexlify(buf)
      zone = int(hZone, 16)
      objMsg.printMsg('AD:Zone %d' % zone)
      return zone
   def BERVsWrtHeater(self):
      from Process import CCudacom
      import re, MathLib,math
      import binascii

      #if self.dut.driveattr.get('POTENTIAL_CAUSE') not in [None, 'NONE'] or self.exit:
      #   return

      if self.dut.errCode not in [13404,14559,14867,10632,10463,10219] or not self.dut.mdwCalComplete:
         return 0

      self.prm_AutoFAAnalysi_250 = {
         'test_num':250,
         'RETRIES': 50,
         'ZONE_POSITION': 198,
         'spc_id': 8,
         'MAX_ERR_RATE': -90,
         'ZONE_MASK': (65535, 65535),
         'NUM_TRACKS_PER_ZONE': 10,
         'SKIP_TRACK': 200,
         'TLEVEL': 0,
         'MINIMUM': -17,
         'PERCENT_LIMIT': 255,
         'timeout': 6000,
         'MAX_ITERATION': 1797,
         'TEST_HEAD': 255,
         'WR_DATA': 0,
         'CWORD1': 1475
         }
      objMsg.printMsg('AD:-->BER Vs Heater Check')
      SuppressOutput = 1
      oSrvFunc   = CServoFunc()
      oUtil = Utility.CUtility()
      self.oCudacom = CCudacom()
      self.oServ = CServo()
      testZone=0
      tstTracks=[5000, min(self.dut.maxTrack)/ 2, min(self.dut.maxTrack) - 20000]
      PreampReg = [[0 for x in range(32)] for y in range(self.dut.imaxHead)]


      T250_Prm = oUtil.copy(self.prm_AutoFAAnalysi_250)
      #T250_Prm.update({'CWORD1': 387})
      T250_Prm.update({'spc_id': 9000})
      T250_Prm.update({'MAX_ERR_RATE': -70})
      T250_Prm.update({'CWORD2': 0})
      T250_Prm.update({'MINIMUM': -1})
      T250_Prm.update({'prm_name': 'ErrorRate'})
      T250_Prm.update({'stSuppressResults': SuppressOutput})
      T250_Prm.update({'DblTablesToParse': ['P250_ERROR_RATE_BY_ZONE']})
      try:
         SetFailSafe()
         self.objProc.St(T250_Prm)
         ClearFailSafe()

      except:
         pass

      #self.objProc.St(TP.spindownPrm_2)
      #objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # prevent T50 hang

      TargetHeater = [[0 for x in range(len(tstTracks))] for y in range(self.dut.imaxHead)]
      testZones = [[-1 for x in range(len(tstTracks))] for y in range(self.dut.imaxHead)]
      InitWH = [0 for y in range(self.dut.imaxHead)]
      ErrByTgt = {}
      zoneNum=0
      StartWriteHeat = 10
      IntialWrtHeater =10
      for cyl in tstTracks:
         for head in range(self.dut.imaxHead):
            self.oServ.wsk(cyl, head)
            objMsg.printMsg('AD:Cyl %s' %(cyl))
            buf, errorCode = self.oCudacom.Fn(1332,0,32)
            #self.oCudacom.displayMemory(buf)
            data = binascii.hexlify(buf)
            for Reg in range (32):
               PreampReg[head][Reg]=int(data[Reg*2:Reg*2+2],16)
            #objMsg.printMsg('AD:H%d Preamp Reg %s' %(head,PreampReg[head]))
            testZone=self.FindZone(1)
            testZones[head][zoneNum]=testZone
            TargetHeater[head][zoneNum]=PreampReg[head][14]
            objMsg.printMsg('AD:Test Zones H%d Zone %d' %(head,zoneNum))
            zoneMask = 2**testZone
            T250_Prm.update({'ZONE_MASK': (zoneMask>> 16, zoneMask & 0xFFFF)})
            T250_Prm.update({'TEST_HEAD': (head << 8 | head)})
            loops=0

            if (TargetHeater[head][0] - StartWriteHeat > 15):
               InitWH[head] = TargetHeater[head][0] - 15
            else:
               InitWH[head] = StartWriteHeat
            IntialWrtHeater=InitWH[head]
            for writeheater in range (IntialWrtHeater, PreampReg[head][14],1):
            #for writeheater in range (IntialWrtHeater,IntialWrtHeater+4,1 ):
               self.objProc.St({'test_num':178,'prm_name': 'ChangeWriteHeater','WRITE_HEAT': writeheater, 'BIT_MASK': (zoneMask>> 16, zoneMask & 0xFFFF), 'CWORD1': 0x4200, 'timeout': 600.0, 'CWORD2': 0x820,'stSuppressResults': SuppressOutput, 'CWORD3': 0, 'HEAD_RANGE': 2**head})
               try:
                  SetFailSafe()
                  self.objProc.St(T250_Prm)
                  ClearFailSafe()
               except:
                  pass
               #ErrRateData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
               ErrRateData = self.dut.objSeq.SuprsDblObject['P250_ERROR_RATE_BY_ZONE']
               #for head in xrange(self.dut.imaxHead):
               hdOffset = head
               #objMsg.printMsg('Error Rate %f' % float(ErrRateData[SERCallIndex  + hdOffset]['RAW_ERROR_RATE']))
               Zone= int(ErrRateData[0]['DATA_ZONE'])
               #objMsg.printMsg('Zone %d Err %f' % (int(self.dut.objSeq.SuprsDblObject['P250_ERROR_RATE_BY_ZONE'][-1]['DATA_ZONE']),
               #                                float(self.dut.objSeq.SuprsDblObject['P250_ERROR_RATE_BY_ZONE'][-1]['RAW_ERROR_RATE'])))
               #objMsg.printMsg('Loop %d Hd %d Zone %d - %f ' % (writeheater,head,Zone,float(ErrRateData[SERCallIndex]['RAW_ERROR_RATE'])))
               ErrByTgt.setdefault(writeheater, {}).setdefault(head, {})[Zone] = float(ErrRateData[0]['RAW_ERROR_RATE'])
               loops+=1
               #SERCallIndex = len(self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj())
         zoneNum+=1


      #objMsg.printMsg(' testZones %s' %testZones)
      #objMsg.printMsg(' TargetHeater %s' %TargetHeater)
      #objMsg.printMsg(' IntialWrtHeater %s' %IntialWrtHeater)

       # To calculate the average of the data
      AvgErrRate = [[0 for x in range(len(tstTracks))] for y in range(self.dut.imaxHead)]
      AvgObject = [[0 for x in range(len(tstTracks))] for y in range(self.dut.imaxHead)]

      for hd in range(self.dut.imaxHead):
         IntialWrtHeater=InitWH[hd]
         for zn in range (len(ErrByTgt[IntialWrtHeater][hd])):
            for loops in range (IntialWrtHeater,TargetHeater[hd][zn]):
               AvgObject[hd][zn] += loops

      for hd in range(self.dut.imaxHead):
         IntialWrtHeater=InitWH[hd]
         for zn in range (len(ErrByTgt[IntialWrtHeater][hd])):
            for wh in range (IntialWrtHeater,max(TargetHeater[hd])):
               try:
                  zoneNum=testZones[hd][zn]
                  AvgErrRate[hd][zn] += float(ErrByTgt[wh][hd][zoneNum])
               except:
                  pass
      RSqr = [[0 for x in range(len(TargetHeater[0]))] for y in range(self.dut.imaxHead)]
      Slopes = [[0 for x in range(len(TargetHeater[0]))] for y in range(self.dut.imaxHead)]
      for hd in range (self.dut.imaxHead):
         IntialWrtHeater=InitWH[hd]
         for zn in range (len(ErrByTgt[IntialWrtHeater][hd])):
            NomSum = 0
            DenomXSum=0
            DenomYSum = 0
            for wh in range(IntialWrtHeater,TargetHeater[hd][zn]):
               znNum=testZones[hd][zn]
               #objMsg.printMsg('AD: wh %f AvgObj %f TargetHeater %f InitWrtHEater %f ErrByTgt %f Avg Err %f' %(wh,AvgObject[hd][zn],TargetHeater[hd][zn],IntialWrtHeater,ErrByTgt[wh][hd][znNum],AvgErrRate[hd][zn]))
               XiMinusXAvg = wh-AvgObject[hd][zn]/float(TargetHeater[hd][zn]-IntialWrtHeater)
               YiMinusYAvg = ErrByTgt[wh][hd][znNum]-AvgErrRate[hd][zn]/float(TargetHeater[hd][zn]-IntialWrtHeater)
               #objMsg.printMsg('AD: Head %d Zone %d Average %f - %f' %(hd,zn,XiMinusXAvg,YiMinusYAvg))
               NomSum += XiMinusXAvg * YiMinusYAvg
               DenomXSum += XiMinusXAvg*XiMinusXAvg
               DenomYSum += YiMinusYAvg*YiMinusYAvg
               #objMsg.printMsg('NormSum %f  DenomXSum %f DenomYSum %f' %(NomSum,DenomXSum,DenomYSum))
            RSqr[hd][zn]=NomSum/(math.sqrt(DenomXSum)*math.sqrt(DenomYSum))
            Slopes[hd][zn]=NomSum/DenomXSum
      #objMsg.printMsg('AD: AVG %s \n %s \n RSquare %s \n Slope %s' %(AvgErrRate,AvgObject,RSqr,Slopes))

      for hd in range(self.dut.imaxHead):
         IntialWrtHeater=InitWH[hd]
         headerStr='AD: HD  WRT_HT  '
         for zn in range (len(ErrByTgt[IntialWrtHeater][hd])):
            headerStr+='   Z%02d_BER' %testZones[hd][zn]
         objMsg.printMsg('AD:%s' %headerStr)
         #for entry in range (len(ErrByTgt)):
         for wh in range (IntialWrtHeater,max(TargetHeater[hd])):
            outStr='%3d %5d    ' %(hd,wh)
            for zn in range (len(ErrByTgt[IntialWrtHeater][hd])):
               try:
                  zoneNum=testZones[hd][zn]
                  outStr += (' %10.6f' %(float(ErrByTgt[wh][hd][zoneNum]) ))
               except:
                  outStr += ('           ')
                  pass
            objMsg.printMsg('AD:%s' %outStr)
         headerStr='AD:    RSquare  '
         for zn in range (len(ErrByTgt[IntialWrtHeater][hd])):
            headerStr+=' %10.6f' %RSqr[hd][zn]
         objMsg.printMsg('%s' %headerStr)
         headerStr='AD:    Slope    '
         for zn in range (len(ErrByTgt[IntialWrtHeater][hd])):
            headerStr+=' %10.6f' %Slopes[hd][zn]
         objMsg.printMsg('%s' %headerStr)

      return 0
   def RSquare(self, ErrorRate,ObjectData):
      import re, MathLib,math
      TotLps = len(ErrorRate)
      TotHd = len(ErrorRate[0])
      TotZone= len(ErrorRate[0][0])
      # To calculate the average of the data
      AvgErrRate = [[0 for x in range(TotZone)] for y in range(TotHd)]
      AvgObject = [0 for x in range(TotHd)]
      #objMsg.printMsg('AD:Tot Head %d Total Zones %d Total Loops %d' % (TotHd,TotZone,TotLps))
      for head in range(TotHd):
         for zone in range (TotZone):
            for loops in range (TotLps):
               #objMsg.printMsg('AD:Error Rate Hd %d  Zone %d : %f' %(head,zone,ErrorRate[loops][head][zone]))
               AvgErrRate[head][zone] += ErrorRate[loops][head][zone]
      #objMsg.printMsg('AD: Average %s %s ' %(  AvgErrRate,AvgObject))
      for head in range (TotHd):
         for loops in range (TotLps):
            #objMsg.printMsg('AD:ObjData %d' %ObjectData[loops])
            AvgObject[head] += ObjectData[loops]
      #objMsg.printMsg('AD: Average %s %s ' %(  AvgErrRate,AvgObject))
      RSqr = [[0 for x in range(TotZone)] for y in range(TotHd)]
      Slopes = [[0 for x in range(TotZone)] for y in range(TotHd)]

      for zone in range (TotZone):
         for head in range (TotHd):
            NomSum = 0
            DenomXSum=0
            DenomYSum = 0
            for loops in range(TotLps):
               XiMinusXAvg = ObjectData[loops]-AvgObject[head]/float(TotLps)
               YiMinusYAvg = ErrorRate[loops][head][zone]-AvgErrRate[head][zone]/float(TotLps)
               #objMsg.printMsg('AD: Head %d Zone %d Average %f - %f' %(head,zone,XiMinusXAvg,YiMinusYAvg))
               NomSum += XiMinusXAvg * YiMinusYAvg
               DenomXSum += XiMinusXAvg*XiMinusXAvg
               DenomYSum += YiMinusYAvg*YiMinusYAvg
            RSqr[head][zone]=NomSum/(math.sqrt(DenomXSum)*math.sqrt(DenomYSum))
            Slopes[head][zone]=NomSum/DenomXSum
      BERMsg=''
      for loops in range(TotLps):
          BERMsg+=('   BER@CLR%02d' % (ObjectData[loops]))
      #objMsg.printMsg('AD: RSquare %s ' %RSqr)
      objMsg.printMsg('HEAD  ZONE%s    RSquare    Slope' %BERMsg)
      for hd in range(TotHd):
         for zn in range(TotZone):
            ber =''
            for loops in range (TotLps):
               ber += ('%12.6f' % ErrorRate[loops][hd][zn] )
            objMsg.printMsg('%2d %6d %s %12.6f %12.6f' % (hd,zn,ber,RSqr[hd][zn],Slopes[hd][zn]))
   def BERVsClearance(self):
      '''
      if self.dut.driveattr.get('POTENTIAL_CAUSE') not in [None, 'NONE'] or self.exit:
         return
      '''

      if self.dut.errCode not in [13404,14559,14867,10632,10463,10219] or not self.dut.mdwCalComplete:
         return 0

      objMsg.printMsg('AD:-->BER Vs Clearance Check')
      oSrvFunc   = CServoFunc()
      oUtil = Utility.CUtility()

      SuppressOutput = 1

      T250_Prm = oUtil.copy(self.prm_AutoFAAnalysi_250)
      #T250_Prm.update({'CWORD1': 387})
      T250_Prm.update({'spc_id': 9000})
      T250_Prm.update({'MAX_ERR_RATE': -70})
      T250_Prm.update({'CWORD2': 0})
      T250_Prm.update({'MINIMUM': -1})
      T250_Prm.update({'prm_name': 'ErrorRate'})
      T250_Prm.update({'stSuppressResults': SuppressOutput})
      T250_Prm.update({'DblTablesToParse': ['P250_ERROR_RATE_BY_ZONE']})

      # To Collect the baseline Error Rate
      tot_Loops = 3
      tot_Zones = self.dut.numZones
      #objMsg.printMsg('AD:number zones %d' %(tot_Zones))
      BaseLineErrRate = {}

      self.ClearServoErrorCount()


      for Loops in range (0,tot_Loops):
         try:
            SetFailSafe()
            self.objProc.St(T250_Prm)
            ClearFailSafe()
         except:
            pass
         #ErrRateData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
         ErrRateData = self.dut.objSeq.SuprsDblObject['P250_ERROR_RATE_BY_ZONE']
         #objMsg.printMsg('AD:Error Rate %s' %(ErrRateData))
         #objMsg.printMsg('AD:Error Rate %s' %(ErrRateData[0]['RAW_ERROR_RATE']))
         for head in xrange(self.dut.imaxHead):
            hdOffset = head * tot_Zones
            for zone in xrange(tot_Zones):
               #objMsg.printMsg('AD:Error Rate Hd %d  Zone %d : %f' %( head, zone,float(ErrRateData[SERCallIndex + zone + hdOffset]['RAW_ERROR_RATE'])))
               #objMsg.printMsg('AD:Suppress Error Rate Hd %d  Zone %d headOffset %d ' %( head, zone,hdOffset))
               #objMsg.printMsg('AD:Suppress Error Rate Hd %d  Zone %d : %f' %( head, zone,float(ErrRateData[zone + hdOffset]['RAW_ERROR_RATE'])))
               BaseLineErrRate.setdefault(Loops, {}).setdefault(head, {})[zone] = float(ErrRateData[ zone + hdOffset]['RAW_ERROR_RATE'])

      InitError=self.DumpServoErrorCount()
      meanStdevList = [0.0 for i in range(self.dut.imaxHead)]
      meanDeltaList = [0.0 for i in range(self.dut.imaxHead)]
      countList = [0 for i in range(self.dut.imaxHead)]
      for hd in range(self.dut.imaxHead):
         StdevList = [0.0 for j in range(self.dut.numZones)]
         DeltaList = [0.0 for j in range(self.dut.numZones)]
         for zn in range(self.dut.numZones):
            ber1 = BaseLineErrRate[0][hd][zn]
            ber2 = BaseLineErrRate[1][hd][zn]
            ber3 = BaseLineErrRate[2][hd][zn]
            StdevList[zn] = MathLib.stDev_standard([ber1, ber2, ber3])
            DeltaList[zn] = max(ber1, ber2, ber3) - min(ber1, ber2, ber3)
            if DeltaList[zn] > 0.1:
               countList[hd] = countList[hd] + 1
            meanStdevList[hd] = MathLib.mean(StdevList)
            meanDeltaList[hd] = MathLib.mean(DeltaList)
      objMsg.printMsg('AD:HEAD ZONE         BER1         BER2         BER3         STDEV          DELTA   AVG_STDEV_HD   AVG_DELTA_HD  COUNT')
      for hd in range(self.dut.imaxHead):
         for zn in range(self.dut.numZones):
            ber1 = BaseLineErrRate[0][hd][zn]
            ber2 = BaseLineErrRate[1][hd][zn]
            ber3 = BaseLineErrRate[2][hd][zn]
            objMsg.printMsg('AD:%2d %6d %12.6f %12.6f %12.6f  %12.6f   %12.6f   %12.6f   %12.6f   %3d' % (hd,zn,ber1,ber2,ber3,MathLib.stDev_standard([ber1, ber2, ber3]),
                                                                                                       max(ber1, ber2, ber3) - min(ber1, ber2, ber3),
                                                                                                       meanStdevList[hd],
                                                                                                       meanDeltaList[hd],
                                                                                                       countList[hd]))
      objMsg.printMsg('\n\n')
      # Save the Original Target Clerance
      self.objProc.St({'test_num':172,'prm_name': 'DisplayTargetClearance','timeout': 1200, 'spc_id': 5000, 'CWORD1': 5})
      try:
         OrigWrtClr=int(self.dut.dblData.Tables('P172_AFH_DH_CLEARANCE').tableDataObj()[-1]['WRT_HEAT_TRGT_CLRNC'],10)
         OrigRdClr=int(self.dut.dblData.Tables('P172_AFH_DH_CLEARANCE').tableDataObj()[-1]['READ_HEAT_TRGT_CLRNC'],10)
      except:
         OrigWrtClr=int(self.dut.dblData.Tables('P172_AFH_CLEARANCE').tableDataObj()[-1]['WRT_HEAT_TRGT_CLRNC'],10)
         OrigRdClr=int(self.dut.dblData.Tables('P172_AFH_CLEARANCE').tableDataObj()[-1]['READ_HEAT_TRGT_CLRNC'],10)
      objMsg.printMsg('AD:Original Write Target %d Read Target %d' %(OrigWrtClr,OrigRdClr))

      tot_Loops = 10
      tot_Zones = self.dut.numZones
      ErrByClr = {}
      TargetClearance = [0 for x in range(tot_Loops)]

      for Loops in range (0,tot_Loops):
         # Change target clearance , from 1A to 51A , check BER margin original settings for bench FA
         # Change start clearance is from 5A , step of 5A - revised 20130322
         target_wh = 5 + (Loops)*5
         target_rd = 5 + (Loops)*5
         spc = 5100 + target_wh
         TargetClearance[Loops]= target_wh

         # CWORD1=8708 --->  10001000000100 (Bit 13 for AFH , Bit 2 for FLASH) ;  CWORD2=1920 --->  11110000000
         # CWORD1=544 --->  1000100000 (Bit 13 for AFH , Bit 2 for FLASH) ;  CWORD2=1920 --->  11110000000
         # CWORD1=0X4200 (16896) --->  100001000000000  (Bit 14 for Pre-Amp) ;  CWORD2=0X820(2080) --->  100000100000
         # Change target clearance
         objMsg.printMsg('AD:Change Target Clearance Write Target %d Read Target %d' %(target_wh,target_rd))
         self.objProc.St({'test_num':178, 'prm_name': 'ChangeTargetClearance','TGT_WRT_CLR': (target_wh,), 'TGT_RD_CLR': (target_rd,), 'spc_id': spc, 'TGT_MAINTENANCE_CLR': (15,), 'BIT_MASK': (65535, 65535), 'TGT_PREWRT_CLR': (15,), 'HEAD_RANGE': 65535, 'timeout': 600, 'CWORD2': 1920, 'CWORD1': 8708,'stSuppressResults': SuppressOutput })
         self.objProc.St({'test_num':178, 'prm_name': 'SaveToFlash','timeout': 600, 'CWORD1': 544,'stSuppressResults': SuppressOutput})
         self.objProc.St({'test_num':172,'prm_name': 'DisplayTargetClearance','timeout': 1200, 'spc_id': spc, 'CWORD1': 5,'stSuppressResults': SuppressOutput})
         # Print write power
         self.objProc.St({'test_num':172,'prm_name': 'WritePower','timeout': 100, 'spc_id': spc, 'CWORD1': 12,'stSuppressResults': SuppressOutput})
         # Print working heater
         self.objProc.St({'test_num':172,'prm_name': 'WorkingHeater','timeout': 1200, 'spc_id': spc, 'CWORD1': 4,'stSuppressResults': SuppressOutput})
         # Print temperature
         self.objProc.St({'test_num':172,'prm_name': 'Temperature','timeout': 1200, 'spc_id': spc, 'CWORD1': 17,'stSuppressResults': SuppressOutput})

         try:
            SetFailSafe()
            self.objProc.St(T250_Prm)
            ClearFailSafe()
         except :
            pass
         ErrRateData = self.dut.objSeq.SuprsDblObject['P250_ERROR_RATE_BY_ZONE']
         #ErrRateData = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
         for head in xrange(self.dut.imaxHead):
            hdOffset = head * tot_Zones
            for zone in xrange(tot_Zones):
               #objMsg.printMsg('AD:Error Rate Hd %d  Zone %d : %f' %( head, zone,float(ErrRateData[SERCallIndex + zone + hdOffset]['RAW_ERROR_RATE'])))
               #objMsg.printMsg('AD:Suppress Error Rate Hd %d  Zone %d : %f' %( head, zone,float(ErrRateData[zone + hdOffset]['RAW_ERROR_RATE'])))
               ErrByClr.setdefault(Loops, {}).setdefault(head, {})[zone] = float(ErrRateData[ zone + hdOffset]['RAW_ERROR_RATE'])
      objMsg.printMsg('Clearance Error Rate %s' %ErrByClr)
      # Restore the target Clearance
      self.objProc.St({'test_num':178, 'prm_name': 'ChangeTargetClearance','TGT_WRT_CLR': (OrigWrtClr,), 'TGT_RD_CLR': (OrigRdClr,), 'spc_id': 5001, 'TGT_MAINTENANCE_CLR': (15,), 'BIT_MASK': (65535, 65535), 'TGT_PREWRT_CLR': (15,), 'HEAD_RANGE': 65535, 'timeout': 600, 'CWORD2': 1920, 'CWORD1': 8708,'stSuppressResults': SuppressOutput })
      self.objProc.St({'test_num':178, 'prm_name': 'SaveToFlash','timeout': 600, 'CWORD1': 544,'stSuppressResults': SuppressOutput})
      self.objProc.St({'test_num':172,'prm_name': 'DisplayTargetClearance','timeout': 1200, 'spc_id': 5001, 'CWORD1': 5,'stSuppressResults': SuppressOutput})
      #objMsg.printMsg('Clearance Error Rate %s' %ErrByClr)
      self.RSquare(ErrByClr,TargetClearance)
      #self.objProc.St(TP.spindownPrm_2)
      #objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # prevent T50 hang
      return 0

   def DeltaMRChk(self):
      if not self.dut.mdwCalComplete:
         return 0
     # objMsg.printMsg('-----------Auto FA Exec DeltaMRChk SF3 Mode----------')
      objMsg.printMsg('AD:Tables: %s'%self.dut.dblData.dblTables(), iMsgLevel = 1)
      get_MR_Values_186={
         'test_num':186,
         'prm_name':'get_MR_Values_186',
         'timeout':600,
         'spc_id' : 1,
         'CWORD1' : (0x1002,),
         }
      if 'P186_BIAS_CAL2' in self.dut.dblData.dblTables().keys():
         biasTbl = self.dut.dblData.Tables('P186_BIAS_CAL2').tableDataObj()
         biasNew = []
         biasOld = []
         if len(biasTbl) > self.dut.imaxHead:
            for entry in biasTbl[0:self.dut.imaxHead]:
               biasOld.append(entry['MRE_RESISTANCE'])
            for entry in biasTbl[-self.dut.imaxHead:]:
               biasNew.append(entry['MRE_RESISTANCE'])
            objMsg.printMsg('AD:deltaMRChk - Old MRE_RESISTANCE: %s'%biasOld)
            objMsg.printMsg('AD:deltaMRChk - New MRE_RESISTANCE: %s'%biasNew)
            for index in range(self.dut.imaxHead):
               if eval('%s - %s > 100'%(biasNew[index], biasOld[index])):
                  objMsg.printMsg('AD:CFM - USHD on Head %d'%index)
                  self.dut.driveattr['POTENTIAL_CAUSE'] = 'HEAD_USHD'
                  self.failHead = list(str(index))
                  return 1
         else:
            from RdWr import CMrResFile

            oMrRes = CMrResFile(get_MR_Values_186, 100)
            try:
               oMrRes.diffMRValues(0)
            except ScrCmds.CRaiseException,exceptionData:
               if exceptionData[0][2] in [14599]:
                  objMsg.printMsg('AD:14599 exception !!!')
                  self.dut.driveattr['POTENTIAL_CAUSE'] = 'HEAD_USHD'
                  self.failHead = oMrRes.getFailHead()
                  return 1
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
            except Exception, e:
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      return 0
   #---------------------------------------------------------------------------------------------------------
   def DeltaVGA(self):
      if not self.dut.mdwCalComplete:
         return 0
      from RdWr import CRdWrScreen
      oRdWr = CRdWrScreen()

      try:
         oRdWr.CollectVGA(self.prm_DeltaVGA,  spc_id=2)
         oRdWr.checkDeltaVGA(self.prm_DeltaVGA)
      except ScrCmds.CRaiseException,exceptionData:
         if exceptionData[0][2] in [14662]:
            self.dut.driveattr['POTENTIAL_CAUSE'] = 'HEAD_USHD'
            entries = self.dut.dblData.Tables('P186_BIAS_CAL2').tableDataObj()
            for entry in entries:
               if entry['DELTAVGA'] > self.prm_DeltaVGA.get('max_vga_diff',30):
                  self.failHead = list(str(entry['HD_PHYS_PSN']))
                  return 1
                  #break
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      except Exception, e:
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      return 0
   #---------------------------------------------------------------------------------------------------------
   def get_AGCdata(self):
      head = int(self.dut.dblData.Tables('P083_AGC').tableDataObj()[-1]['HD_LGC_PSN'])
      test_cyl = int(self.dut.dblData.Tables('P083_AGC').tableDataObj()[-1]['TRK_NUM'])
      agc_val = int(self.dut.dblData.Tables('P083_AGC').tableDataObj()[-1]['DELTA_MA_AGC'])
      self.data_AGCScrn[int(head)].append({'Head'            : head,
                                 'Track'           : test_cyl,
                                 'Delta_AGC'       : agc_val,
                                 })
   #---------------------------------------------------------------------------------------------------------
   def CollectServoCnt(self):
      if not 1:
         return
      from MediaScan import CServoFlaw
      oServoFlaw = CServoFlaw()
      try:
         oServoFlaw.servoFlawScan(TP.prm_126_read_sft)
      except:
         objPwrCtrl.powerCycle(5000,12000,10,10)
      return 0
    #---------------------------------------------------------------------------------------------------------
   def InstabilityTest(self):
      if not self.dut.mdwCalComplete:
         return 0

      base_phastOptiPrm_251 = {
         'test_num'           : 251,
         'prm_name'           : 'base_phastOptiPrm_251',
         'timeout'            : 2000,
         'spc_id'             : 1,
         'BIT_MASK'           : (0, 7),
         'CWORD1'             : 0x0038,
         "ZONE_POSITION"      : 198,
         'REG_TO_OPT1'        : (135, 0, 0, 1),
         'REG_TO_OPT2'        : (146, 35, 55, 3),
         'REG_TO_OPT2_EXT'    : (0, 0, 1),
         'REG_TO_OPT3'        : (37, 21, 32, 1),
         'REG_TO_OPT4'        : (145, 9, 13, 1),       # LAULC  TD TARGET
         'REG_TO_OPT5'        : (146, 35, 55, 3),
         'REG_TO_OPT5_EXT'    : (0, 0, 1),
         'REG_TO_OPT6'        : (37, 21, 32, 1),
         'REG_TO_OPT7'        : (145, 9, 13, 1),       # LAULC
         'REG_TO_OPT8'        : (155, 0, 31, -1),
         'REG_TO_OPT8_EXT'    : (0, 0, 0x3C ),
         'RESULTS_RETURNED'   : 7,
         'SET_OCLIM'          : 819,
         }
      prm_Instability_195 = {
         'test_num':195,
         'prm_name':'prm_Instability_195',
         'spc_id':1,
         'timeout':2000,
         'CWORD1': 32770,
         'NORM_STDEV_BY_AVG': 20,
         'ZONE_POSITION': 198,
         'NUM_FAIL_ZONE_LIMIT': 3,
         'DELTA_LIMIT': (32000,),
         'NUM_READS': 1,
         'AVG_NORM_STDEV_BY_HEAD': 8,
         'RANGE2': (0, 57, 3, 0),
         'AC_ERASE': (),
         'THRESHOLD2': 0,
         'THRESHOLD': (25,),
         'ZONE_MASK_EXT': (0, 0),
         'RETRY_LIMIT': 5,
         'ZONE_MASK': (32767, 0),
         'MAX_BLOCK_COUNT': (0, 30)

         }
      prm_395 = {
         'test_num':395,
         'prm_name' : 'prm_395',
         'SCALED_VAL': 1000,
         'FREQUENCY': 1000,
         'ZONE_POSITION': 198,
         'spc_id': 1,
         'DELTA_LIMIT': 0,
         'SLOPE_LIMIT': 180,
         'THRESHOLD2': 30,
         'MAXIMUM': 50,
         'TARGET_COEF': -80,
         'MINIMUM': 5,
         'ZONE_MASK_EXT': (0, 0),
         'HEAD_RANGE': 255,
         'timeout': 3600,
         'OFFSET': 0,
         'THRESHOLD': 5,
         'ZONE_MASK': (32767, 0),
         'RETRY_LIMIT': 4,
         'CWORD1': 21,
         'stSuppressResults' : ST_SUPPRESS__ALL,
         }
      try:

         nIndex = 0
         self.objProc.St(prm_395)
         self.objProc.St(prm_Instability_195)
##         entries = self.dut.objSeq.SuprsDblObject['P195_INSTABILITY_SUM']
##         for entry in entries:
##            if int(entry['TA_THRSHLD']) in [8, 12] and int(entry['TOTAL_EP_CNT']) > 2000:
##               objMsg.printMsg('P195_INSTABILITY_SUM - TA_THRSHLD = 8 or 12 and TOTAL_EP_CNT > 2000')
##               objMsg.printMsg('CFM - USHD on Head %d'%int(entry['HD_LGC_PSN']))
##               self.failHead = int(entry['HD_PHYS_PSN'])
##               self.dut.driveattr['POTENTIAL_CAUSE'] = 'USHD'
##               return
      except:
         objMsg.printMsg(traceback.format_exc(),objMsg.CMessLvl.IMPORTANT)
         objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) # prevent T50 hang

     #---------------------------------------------------------------------------------------------------------
   def BERCheck(self):
      if not self.dut.mdwCalComplete:
         return 0
      objMsg.printMsg('-----------Auto FA Exec BERCheck SF3 Mode----------')

      try:
         entries = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
      except:
         objMsg.printMsg('AutoFA:Cannot find table P250_ERROR_RATE_BY_ZONE/P_FORMAT_ZONE_ERROR_RATE. Skip BER check')
         return 0

      orgBer = {}
      for entry in entries:
         if orgBer.has_key(int(entry['HD_PHYS_PSN'])) == 0:
            orgBer[int(entry['HD_PHYS_PSN'])] = [str(entry['RAW_ERROR_RATE'])]
         else:
            orgBer[int(entry['HD_PHYS_PSN'])].append(str(entry['RAW_ERROR_RATE']))

      objMsg.printMsg('AutoFA:-->BER Check, Org BER at Zone0 by Head: %s'%orgBer)

      for head, values in orgBer.items():   # Ber by hd, orgBer should save all hd all zone ber value.
            nCnt = 0
            for raw in values:
               if eval('%s > -2.3'%raw):
                  nCnt = nCnt + 1
            if nCnt >= 2:
               objMsg.printMsg('AD:Hd: %d more than 2 zones with BER > -2.3'%head)
               objMsg.printMsg('AD:CFM - USHD on Head %d'%head)
               self.dut.driveattr['POTENTIAL_CAUSE'] = 'USHD1'
               self.failHead = list(str(head))
               return 1
      return 0

   def BodeCheck(self):
      if not self.dut.mdwCalComplete:
         return 0
      #objMsg.printMsg('-----------Auto FA Exec BodeCheck SF3 Mode----------')
      headList = []
      if 1: #try:
         try:
            self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').deleteIndexRecords(1)
            self.dut.dblData.delTable('P152_BODE_GAIN_PHASE')
         except:
            pass
         self.objProc.St(TP.doBodePrm_152_S_OD)
         tlogdata = self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').tableDataObj()
         suminfo = {}
         Gain  = []
         Phase = []
         for head in range(self.dut.imaxHead):
            suminfo[head] = {}
            for frequency in range(4):
               suminfo[head][frequency] = {}
               suminfo[head][frequency]['GAIN'] = []
            for entry in tlogdata:
               if  int(entry['HD_PHYS_PSN']) == head and int(entry['FREQUENCY']) >= 2300 and int(entry['FREQUENCY']) <= 2600:
                  suminfo[int(entry['HD_PHYS_PSN'])][0]['GAIN'].append(float(entry['GAIN']))
               if  int(entry['HD_PHYS_PSN']) == head and int(entry['FREQUENCY']) >= 4000 and int(entry['FREQUENCY']) <= 5000:
                  suminfo[int(entry['HD_PHYS_PSN'])][1]['GAIN'].append(float(entry['GAIN']))
               if int(entry['HD_PHYS_PSN']) == head and (int(entry['FREQUENCY']) > 8000 and int(entry['FREQUENCY']) <= 23000):
                  suminfo[int(entry['HD_PHYS_PSN'])][2]['GAIN'].append(float(entry['GAIN']))
               if int(entry['HD_PHYS_PSN']) == head and (int(entry['FREQUENCY']) >= 500 and int(entry['FREQUENCY']) <= 8000):
                  suminfo[int(entry['HD_PHYS_PSN'])][3]['GAIN'].append(float(entry['GAIN']))
               if self.dut.HGA_SUPPLIER =='TDK' and int(entry['HD_PHYS_PSN']) == 1:
                  if (int(entry['FREQUENCY']) > 2275 and  int(entry['FREQUENCY']) < 2725):
                     Gain.append(float(entry['GAIN']))
                  if  (int(entry['FREQUENCY']) > 20275 and  int(entry['FREQUENCY']) < 20725):
                     Phase.append(float(entry['PHASE']))


            #for head in range(self.dut.imaxHead):
            if max(suminfo[head][0]['GAIN']) >= 13.0 or max(suminfo[head][1]['GAIN']) >= 13.0 or\
               max(suminfo[head][2]['GAIN']) >= 5.0 or max(suminfo[head][3]['GAIN']) >= 14.0:
               headList.append(str(head))

            if Gain and Phase:
               maxGain = max(Gain)
               minPhase = min(Phase)
               if maxGain > 11.3 and minPhase <= -1.3:
                  headList.append('1')




         if len(headList) > 0:
            self.failHead = list(set(headList))
            self.dut.driveattr['POTENTIAL_CAUSE'] = 'HEAD_RESONANCE'
            return 1

      '''
      except:
         objMsg.printMsg('AutoFA:CFM-T152 fail or cannot find Table P152_BODE_GAIN_PHASE')
         #self.exit = 1
         try:
            self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').deleteIndexRecords(1)
            self.dut.dblData.delTable('P152_BODE_GAIN_PHASE')
         except:
            pass
         return 1
      '''
      try:
         self.dut.dblData.Tables('P152_BODE_GAIN_PHASE').deleteIndexRecords(1)
         self.dut.dblData.delTable('P152_BODE_GAIN_PHASE')
      except:
         pass
      return 0



   #---------------------------------------------------------------------------------------------------------
   def cmdstatcheck(self, ErrorCode=11247):
      try:
         cmd_data = self.dut.dblData.Tables('P011_DO_SERVO_CMD').tableDataObj()[-1:]
      except:
         objMsg.printMsg('Auto FA:Attention!!! The table: P011_DO_SERVO_CMD10 does not exist')
         return

      for entry in cmd_data:
         if entry.has_key(15):
            if int(entry[15]) != 1:
               return ErrorCode
         else:
            if int(entry['CMD_STAT_HEX']) != 1:
               return ErrorCode

   #---------------------------------------------------------------------------------------------------------
   def DisplayLoadProfile(self,unload=0, checkspec = 1):
      SPINDLE_RPM = 5408
      K_RPM_CNT = 167000000;
      VEL_BITS_PER_IPS = TP.lul_prm_025['SCALED_VAL'][0]
      K_DAC = 32768
      K_PA = TP.lul_prm_025['GAIN2'][0]
      
      objMsg.printMsg('********Display Parameters********')
      objMsg.printMsg('Auto:SPINDLE_RPM           : %10d' % SPINDLE_RPM)
      objMsg.printMsg('Auto:K_RPM_CNT             : %10d' % K_RPM_CNT)
      objMsg.printMsg('Auto:VEL_BITS_PER_IPS      : %10d' % VEL_BITS_PER_IPS)
      objMsg.printMsg('Auto:K_DAC                 : %10d' % K_DAC)
      objMsg.printMsg('Auto:K_PA                  : %10d' % K_PA)
      objMsg.printMsg('**********************************')

      servo_data = self.dut.dblData.Tables('P011_SRVO_DIAG_RESP').tableDataObj()[-1:]
      if testSwitch.virtualRun:
         servo_data = [{'OCCURRENCE': 19, 'SPC_ID': -1, 7: '0000', 8: '0000', 9: 'e03f', 10: '0001', 11: 'ffa9', 12: '0000', 13: '0001', 14: '0000', 15: '0000', 16: '0000', 17: '0000', 18: '0000', 19: '0000', 20: 'f42b', 21: '3d9e', 22: 'e41f', 23: 'a93c', 24: 'bf30', 25: '58b5', 26: '8000', 27: '45a6', 28: '1ea1', 29: '1bc8', 30: 'e6f3', 5: '632f', 32: '3d88', 33: 'd128', 34: 'c1f4', 35: 'abe2', 6: 'fffc', 'SEQ': 9, '*': '0b0a', 31: 'c57f', 'TEST_SEQ_EVENT': 17}]
      objMsg.printMsg('ServoDiagData %s' % (servo_data))
      LulPeakCurrent = float(self.signed(int(servo_data[0][9],16))* K_PA / K_DAC)
      LoadMinSpinSpeed = float(K_RPM_CNT/float(K_RPM_CNT/SPINDLE_RPM + self.signed(int(servo_data[0][10],16))))
      LULPeakVelocity = float(self.signed(int(servo_data[0][11],16))*1000/float(VEL_BITS_PER_IPS))
      BemfResidualError = int(servo_data[0][7],16)

      objMsg.printMsg('Load Time           : %10d' % self.signed(int(servo_data[0]['*'],16)))      
      objMsg.printMsg('Bemf Cal Gain       : %10d' % self.signed(int(servo_data[0][5],16)))
      objMsg.printMsg('Bemf Cal Offset     : %10d' % self.signed(int(servo_data[0][6],16)))
      objMsg.printMsg('BemfCalResidualError: %10d' % BemfResidualError)
      objMsg.printMsg('Bemf Cal Gain       : %10d' % self.signed(int(servo_data[0][8],16)))    
      objMsg.printMsg('LulPeakCurrent      : %10.2f mA  (-213.33 <-> -155)' %LulPeakCurrent)
      objMsg.printMsg('LoadMinSpinSpeed    : %10.2f RPM (min 5405)' %LoadMinSpinSpeed)

      if unload:
         objMsg.printMsg('UnLoadPeakVelocity     : %10.2f IPS (-4.94 <-> -4.28)' %LULPeakVelocity)
      else:
         if self.minspeed == 0 or LoadMinSpinSpeed < self.minspeed:
            self.minspeed = LoadMinSpinSpeed
         objMsg.printMsg('MinLoadSpinSpeed    : %10.2f RPM (min 5405)' %self.minspeed)
         objMsg.printMsg('LULPeakVelocity     : %10.2f IPS (-4.94 <-> -4.28)' %LULPeakVelocity)
      objMsg.printMsg('Load Head Retries   : %10d' % int(servo_data[0][12],16))
      objMsg.printMsg('LoadUnloadErrorCode : %10d' % int(servo_data[0][13],16))
      if checkspec:
         if ( LulPeakCurrent == -666):
            return 'HSALIFTED'
         elif ( LoadMinSpinSpeed < 5403):
            return 'SPINDIP'
         elif (LulPeakCurrent < -300):
            return 'FOF_PROC'
         elif (LulPeakCurrent > -80):
            return 'J1_PIN/PCB'
         elif ( BemfResidualError > 0):
            return 'HSABemf'
         else:
            return None

      objMsg.printMsg('Auto FA:LoadUnLoad Profile normal')
      return None
   #---------------------------------------------------------------------------------------------------------
   def DisplayUnLoadProfile(self):
      self.DisplayLoadProfile(unload =1,checkspec = 0)
   #---------------------------------------------------------------------------------------------------------      
   def signed(self, value):
      if value > 0x7FFF:
         value = -(0xFFFF- value+1)
      return value
   #---------------------------------------------------------------------------------------------------------
   def GetSymbolOffsetValue(self,ServoName="None",SymOffset=0,AccessType=2,report = 0):
      self.objProc.St({'test_num':11, 'prm_name':ServoName,'SYM_OFFSET': SymOffset, 'CWORD1':512,'ACCESS_TYPE':AccessType, 'timeout':10,'stSuppressResults': self.SupressOutput,'DblTablesToParse':['P011_SV_RAM_RD_BY_OFFSET']})
      if not testSwitch.virtualRun:
         ReadData=int(self.dut.objSeq.SuprsDblObject['P011_SV_RAM_RD_BY_OFFSET'][-1]['READ_DATA'],16)
      else:
         ReadData = 1
      if report:
         objMsg.printMsg("Auto FA:%s = 0x%X" % (ServoName,ReadData))
      return ReadData
   #---------------------------------------------------------------------------------------------------------
   def GetValuefromServoRam(self, address, accesstype = 2):
      wrSapAddr = dict(TP.getSymbolViaAddrPrm_11)
      wrSapAddr['ACCESS_TYPE'] = accesstype
      wrSapAddr['DblTablesToParse'] = 'P011_RW_SRVO_RAM_VIA_ADDR'
      #wrSapAddr['stSuppressResults'] = 1
      wrSapAddr["START_ADDRESS"] = self.oUtility.ReturnTestCylWord(address)
      wrSapAddr["END_ADDRESS"] = self.oUtility.ReturnTestCylWord(address)
      self.objProc.St(wrSapAddr)   
      readdata = int(self.dut.objSeq.SuprsDblObject['P011_RW_SRVO_RAM_VIA_ADDR'][-1]['SRVO_DATA'],16)
      return readdata
   #--------------------------------------------------------------------------------------------------------- 
   
   def SetValuetoServoRam(self, address, data, accesstype = 2):
      wrSapAddr = dict(TP.getSymbolViaAddrPrm_11)
      wrSapAddr['ACCESS_TYPE'] = accesstype
      wrSapAddr['DblTablesToParse'] = 'P011_RW_SRVO_RAM_VIA_ADDR'
      #wrSapAddr['stSuppressResults'] = 1
      wrSapAddr["START_ADDRESS"] = self.oUtility.ReturnTestCylWord(address)
      wrSapAddr["END_ADDRESS"] = self.oUtility.ReturnTestCylWord(address)
      wrSapAddr['WR_DATA'] = data
      wrSapAddr['CWORD1'] = 0x2
      self.objProc.St(wrSapAddr)   
     
   #--------------------------------------------------------------------------------------------------------- 
   def GetPreampGain(self,hd = 0,report = 0):
      
      MrBiasTblAddress =self.GetSymbolOffsetValue("MR BIAS SYMBOL TAB Address",132,3)
      # Read Address Data 
      if not testSwitch.virtualRun:
         HdPreampGain = self.GetValuefromServoRam(MrBiasTblAddress+hd*2,2)
         HdPreampGain = (HdPreampGain & 0x0F00)>>8
      else:
         HdPreampGain = 9
      
      if report:objMsg.printMsg("Auto FA:Preamp Gain = %d" % HdPreampGain)
      return HdPreampGain

   #---------------------------------------------------------------------------------------------------------
   
   def SetPreampGain(self,hd = 0,DefaultPreampGain=11):
      
      #objMsg.printMsg("Set Preamp Gain to %d" % DefaultPreampGain)
      DefaultPreampGain = DefaultPreampGain << 8
      MrBiasTblAddress =self.GetSymbolOffsetValue("MR BIAS SYMBOL TAB Address",132,3)
      # Get PreAMP gain from given address

      # Read Address Data 
      if not testSwitch.virtualRun:
         HdPreampGain = self.GetValuefromServoRam(MrBiasTblAddress+hd*2,2)
      else:
         HdPreampGain = 0xF0FF
      self.SetValuetoServoRam(MrBiasTblAddress+hd*2, (HdPreampGain & 0xF0FF)|DefaultPreampGain, 2)
   #---------------------------------------------------------------------------------------------------------
   ##Sequence
   ## Based on the servo code version and load the respective Symbol file in (laplace5mm54_A8D2.zip => laplace5mm54A8D2.sym)
   ## Read the given variable name address
   ##
   def getSymbolAddress(self, symname=['i16_SerpentIndex']):
   # same as cmd_Getsymaddress
   # return address for cmd_GetSvoRam
         import sys
         import os, struct
         add=-1
         value = []
         para = []
         sym = open(self.ServoSymfilePath,  'rb')
         data = sym.read()
         sym.close()
         symline = data.split('\r\n')

         for l in range(len(symline)):
            if list(symline[l].split())[0] in symname:
               value.append(list(symline[l].split())[1])
            if len(value) == len(symname):
               break
         objMsg.printMsg( "SymName: %s, Address: %s "% (symname,value))

         for i in range(len(value)):
               add = int(value[i],16)
         return add
   def getsramviaadd(self, Address=0):
      self.objProc.St({'test_num':11, 'END_ADDRESS': self.oUtility.ReturnTestCylWord(Address), 'ACCESS_TYPE': 2, 'START_ADDRESS': self.oUtility.ReturnTestCylWord(Address), 'timeout': 1000, 'EXTENDED_MASK_VALUE': 65535, 'CWORD1': 1})

      entry = self.dut.dblData.Tables('P011_RW_SRVO_RAM_VIA_ADDR').tableDataObj()[-1]
      ReadData=int(entry['SRVO_DATA'],16)

      return ReadData

   ## Get the Symbol Value from the given address
   def getSymbolValue(self, name=['i16_SerpentIndex'],AccessType=2):
      try:
         address = self.getSymbolAddress(name)
         ReadData= self.getsramviaadd(address)
         objMsg.printMsg('%s : 0x%X' %(name,ReadData))
         return ReadData
      except:
         objMsg.printMsg("Can't Get Address")
         return -1
   
   def run(self):
      #global failHead
      CommandTuple = self.funlist
      for command in CommandTuple:
         objMsg.printMsg("----------------Auto FA Start %s - SF3 Mode----------------" % command[0])
         if getattr(self, command[0])(**command[1]):
            objMsg.printMsg("DION Auto FA: %s fail\r\n" % command[0])
            objMsg.printMsg("----------------Auto FA End %s - SF3 Mode----------------\r\n" % command[0])
            #failHead = self.failHead
            #pass
            #return
         objMsg.printMsg("Auto FA: %s pass" % command[0])
         objMsg.printMsg("----------------Auto FA End %s - SF3 Mode----------------\r\n" % command[0])

class CDiagF3Mode:
   """
   """
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      self.funlist = [
                       ['V5Screen',dict()],
                       ['IOEDCCheck',dict()],
                       ['MRResChk',dict()],
                       ['headSwitch',dict()],
                       ['BERCheck',dict()],
                       ['WriteInduceServoError',dict()],


                     ]
      from serialScreen import sptDiagCmds
      self.oSerial = sptDiagCmds()
      self.failHead = []
      self.failMedia = []
   #-------------------------------------------------------------------------------------------------------
   def V5Screen(self,**args):
      objMsg.printMsg('-----------Auto FA Exec V5Screen F3 Mode----------')

      try:
         objPwrCtrl.powerCycle()
      except:
         objMsg.printMsg('AutoFA:No Communication !!!')
         try:
            objMsg.printMsg('AutoFA:Force power on after no Communication !!!')
            objPwrCtrl.powerOn(ataReadyCheck= False)                    # Force power on in case drive fail not ATA ready and power off.
         except:
            objMsg.printMsg('AutoFA:Exception: Force power on after no Communication !!!')
         if self.dut.EOS:
            self.dut.driveattr['POTENTIAL_CAUSE'] = 'EOS'
         (mV3,mA3),(mV5,mA5),(mV12,mA12)  = GetDriveVoltsAndAmps()
         objMsg.printMsg('AutoFA:CFM - 3V: (%d mV, %d mA)  5V: (%d mV, %d mA)  12V: (%d mV, %d mA)'%(mV3,mA3,mV5,mA5,mV12,mA12))
         if mV5 < 3000:
            self.dut.driveattr['POTENTIAL_CAUSE'] = 'EOS'
         return 1
      #*****************Enable diag mode*******************

      try:
         self.oSerial.enableDiags()
      except:
         objMsg.printMsg('AutoFA:No response when entering diag mode')
         if getattr(self.dut, "EOS",0):#self.dut.EOS:
            self.dut.driveattr['POTENTIAL_CAUSE'] = 'EOS'
            return 1
      return 0

   #-------------------------------------------------------------------------------------------------------
   def IOEDCCheck(self,**args):
      try:
         from CustomCfg import CCustomCfg
         custConfig = CCustomCfg()
         objPwrCtrl.powerCycle(5000,12000,10,30)
         custConfig.SMARTReadData(TP.prm_SmtIOEDC.get('lCAIDS', {}))
      except:
         self.dut.driveattr['POTENTIAL_CAUSE'] = 'COMP_PCBA'
         return 1
      return 0
   #-------------------------------------------------------------------------------------------------------
   def MRResChk(self):
      self.oSerial.enableDiags()
      self.oSerial.gotoLevel('7')
      try:
         data = self.oSerial.sendDiagCmd('X', printResult = True)
         data = data.split('\r\n')
         for entry in data:
            nIndex = entry.find('Head')
            if nIndex > -1 and (int(entry[-4:], 16) < 100 or int(entry[-4:], 16) > 1000):
               objMsg.printMsg('AutoFA:CFM - %s'%entry)
               self.failHead = list(str(entry[nIndex+5:nIndex+7]))
               self.dut.driveattr['POTENTIAL_CAUSE'] = 'EOS'
               return 1
      except:
         flashAddr, flashCode = sptCmds.flashLEDSearch(120)
         objMsg.printMsg("AD:Completed Searching for FLASH LED's")
         if not flashAddr == '' and not flashCode == '':
            self.dut.driveattr['POTENTIAL_CAUSE'] = 'FLASHLED'
            return 1
      return 0
   #-------------------------------------------------------------------------------------------------------
   def headSwitch(self):
      objMsg.printMsg('-----------Auto FA Exec headSwitch F3 Mode----------')

      self.oSerial.enableDiags()
      self.oSerial.syncBaudRate(Baud38400)
      numCyls,zones = self.oSerial.getZoneInfo(printResult=True)
      self.oSerial.gotoLevel('2')
      for hd in range(self.dut.imaxHead):
         tstTracks = [0x100, 0x4E8]
         fail = 0
         for cyl in tstTracks:
            try:
               self.oSerial.sendDiagCmd('S%X,%d'%(cyl, hd), printResult = True,DiagErrorsToIgnore = ['00003003'])
            except:
               fail = 1
         if fail:
            self.dut.driveattr['POTENTIAL_CAUSE'] = 'HDC'
            self.failHead = list(str(hd))
            objMsg.printMsg('AutoFA:CFM - Cannot seek on surface %d'%hd)
            return 1
      return 0
   #-------------------------------------------------------------------------------------------------------
   def BERCheck(self):

      try:
         entries = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
      except:
         objMsg.printMsg('AD:Cannot find table P250_ERROR_RATE_BY_ZONE/P_FORMAT_ZONE_ERROR_RATE. Skip BER check')
         return 0

      orgBer = {}
      for entry in entries:
         if orgBer.has_key(int(entry['HD_PHYS_PSN'])) == 0:
            orgBer[int(entry['HD_PHYS_PSN'])] = [str(entry['RAW_ERROR_RATE'])]
         else:
            orgBer[int(entry['HD_PHYS_PSN'])].append(str(entry['RAW_ERROR_RATE']))

      objMsg.printMsg('AD:-->BER Check, Org BER at Zone0 by Head: %s'%orgBer)
      self.oSerial.enableDiags()
      for hd in range(self.dut.imaxHead):
         self.oSerial.enableRWStats(2)
         cmdList = ['/2', 'S2000,%d'%hd, 'A2', 'P0,0', 'L1,400', 'Q']
         for cmd in cmdList:
            try:
               self.oSerial.sendDiagCmd(cmd, timeout = 180, printResult = True)
            except:
               break
      else:
         for hd in range(self.dut.imaxHead):
            data = self.oSerial.getHeadBERData()
            objMsg.printMsg('AutoFA:BER: %s'%data)
            for entry in data:
               if int(entry['HD_PHYS_PSN']) == hd and abs(float(entry['RRAW'])) > 0.0 and abs(float(orgBer[int(entry['HD_PHYS_PSN'])][0])) > 0.0 and abs(float(entry['RRAW'])) < 4.5 and abs(float(entry['RRAW']))-abs(float(orgBer[int(entry['HD_PHYS_PSN'])][0])) > 0.5:
                  try:
                     objMsg.printMsg('AutoFA:Hd: %d BER drop 1.0. Q: %s(4.5), T250: %s'%(hd, entry['RRAW'], orgBer[int(entry['HD_PHYS_PSN'])]))
                  except:
                     pass
                  objMsg.printMsg('AutoFA:CFM - USHD on Head %s'%entry['HD_PHYS_PSN'])
                  self.dut.driveattr['POTENTIAL_CAUSE'] = 'HEAD_USHD'
                  self.failHead = int(entry['HD_PHYS_PSN'])
                  return 1
      return 0
   #--------------------------------------------------------------------------------------------------------
   def CalculateServoErrorDelta(self,InitServoData,LastServoData,Pattern):
      HdDelta=[]
      Patterns=Pattern + r'\s+(?P<Head0>[\dA-Fa-f]+)\s+(?P<Head1>[\dA-Fa-f]+)\s+(?P<Head2>[\dA-Fa-f]+)\s+(?P<Head3>[\dA-Fa-f]+)'
      SearchPat = re.compile(Patterns)
      InitSearch = SearchPat.search(InitServoData)
      if InitSearch:
         HdDelta.append(int(InitSearch.groupdict()['Head0'],16))
         HdDelta.append(int(InitSearch.groupdict()['Head1'],16))
         HdDelta.append(int(InitSearch.groupdict()['Head2'],16))
         HdDelta.append(int(InitSearch.groupdict()['Head3'],16))

      LastSearch = SearchPat.search(LastServoData)
      if LastSearch:
         HdDelta[0] = (int(LastSearch.groupdict()['Head0'],16)-HdDelta[0])
         HdDelta[1] = (int(LastSearch.groupdict()['Head1'],16)-HdDelta[1])
         HdDelta[2] = (int(LastSearch.groupdict()['Head2'],16)-HdDelta[2])
         HdDelta[3] = (int(LastSearch.groupdict()['Head3'],16)-HdDelta[3])
      objMsg.printMsg("AD:%40s     %s" % (Pattern, HdDelta))
      return HdDelta
   #--------------------------------------------------------------------------------------------------------
   def WriteInduceServoError(self):
      self.oSerial.enableDiags()
      self.oSerial.gotoLevel('2')
      numCyls, zoneList = self.oSerial.getZoneInfo(printResult = True)
      testzn =[0,len(zoneList[0])/2,len(zoneList[0])-1]
      for hd in range(self.dut.imaxHead):
         for zone in testzn:
            testTrk = zoneList[hd][zone]+100
            self.oSerial.gotoLevel('2')
            self.oSerial.sendDiagCmd('S%X,%d'%(testTrk, hd), printResult = True,DiagErrorsToIgnore = ['00003003'])
            self.oSerial.sendDiagCmd('A0', printResult = False)
            self.oSerial.sendDiagCmd('W', timeout = 300, printResult = True, stopOnError = False)
            self.oSerial.gotoLevel('4')
            Initdata = self.oSerial.sendDiagCmd('s', printResult = True)
            self.oSerial.gotoLevel('2')
            self.oSerial.sendDiagCmd('L1,50', printResult = False)
            self.oSerial.sendDiagCmd('W', timeout = 300, printResult = True, stopOnError = False)
            self.oSerial.gotoLevel('4')
            Lastdata=self.oSerial.sendDiagCmd('s', printResult = True)
            self.CalculateServoErrorDelta(Initdata,Lastdata,r'Rro Parity Error')
            self.CalculateServoErrorDelta(Initdata,Lastdata,r'Timing Mark Not Detected')
            self.CalculateServoErrorDelta(Initdata,Lastdata,r'Unsafe Error Ontrack')
            self.CalculateServoErrorDelta(Initdata,Lastdata,r'Agc Running Average Trip Error')
            self.CalculateServoErrorDelta(Initdata,Lastdata,r'Predicted Offtrack')
      return 0

   #---------------------------------------------------------------------------------------------------------


   def DumpServoErrorLog(self, **args):
      objMsg.printMsg('-----------Auto FA Exec DumpServoErrorLog F3 Mode----------')
      return
   #---------------------------------------------------------------------------------------------------------

   def run(self):
      CommandTuple = self.funlist
      for command in CommandTuple:
         objMsg.printMsg("----------------Auto FA Start %s - F3 Mode----------------" % command[0])
         if getattr(self, command[0])(**command[1]):
            return

class CAutoFA:
   """
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      self.dut = dut
      self.scriptInfo = \
      {
         'AUTOFA Script Rev'           : 'A1D_DDIS_1.3',
         'AUTOFA SW Date'              : '2013.12.20',
      }
      self.params['RRO_List'] = {}
      self.params['NRRO_List'] = {}
      self.params['RAW_RO_List'] = {}
      self.dut.driveattr['AUTOFA_REV'] = self.scriptInfo['AUTOFA Script Rev']
      self.failHead = []
      self.failMedia = []
   #-------------------------------------------------------------------------------------------------------
   def runDiagWithSF3Mode(self):
      objSF3Mode = CDiagSF3Mode(self.dut, self.params)
      try:
         objSF3Mode.run()
      finally:
         if type(objSF3Mode.failHead) == types.ListType: self.failHead = list(set(objSF3Mode.failHead))
         if type(objSF3Mode.failMedia) == types.ListType: self.failMedia = list(set(objSF3Mode.failMedia))
   #-------------------------------------------------------------------------------------------------------
   def runDiagWithF3Mode(self):
      objF3Mode = CDiagF3Mode(self.dut, self.params)
      try:
         objF3Mode.run()
      finally:
         if type(objF3Mode.failHead) == types.ListType: self.failHead = list(set(objF3Mode.failHead))
         if type(objF3Mode.failMedia) == types.ListType: self.failMedia = list(set(objF3Mode.failMedia))
   #-------------------------------------------------------------------------------------------------------
   def ec10007Map(self):
      value = 'None'
      try:
         entries = self.dut.dblData.Tables('P_TRACK').tableDataObj()
      except:
         objMsg.printMsg("Attention:Table P_TRACK not exist!!!")
         return value
      head = []
      for entry in entries:
         head.append(str(entry['HEAD']))
      if len(head) > 0:
         self.failHead = list(set(head))
   #-------------------------------------------------------------------------------------------------------
   def ec10119Map(self):
      value = 'HEAD_USHD'

      try:
         entries = self.dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()
         lastEntries = self.dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()[-1]
      except:
         objMsg.printMsg("Attention:Table P135_FINALI_CONTACT not exist!!!")
         return value

      head = []
      for entry in entries:
         if int(entry['ERROR_CODE']) == 42197:
            head.append(str(entry['HD_PHYS_PSN']))
         if int(lastEntries['ERROR_CODE']) == 14841:
            head.append(str(lastEntries['HD_PHYS_PSN']))
      if len(head) > 0:
         self.failHead = list(set(head))
      return value

   def ec10136Map(self):
      value = 'HEAD_USHD'
      if self.dut.failureState == 'SERVO_OPTI' and self.dut.nextOper == 'PRE2':
        try:
           entries = self.dut.dblData.Tables('P000_BDRAG_STATUS').tableDataObj()
        except:
           objMsg.printMsg("Attention:Table P000_BDRAG_STATUS not exist!!!")
           return value

        head = []
        for entry in entries:
           if int(entry['FAIL_CODE']) == 10136:
              head.append(str(entry['HD_PHYS_PSN']))
        if len(head) > 0:
         self.failHead = list(set(head))
      return value

   def ec10266Map(self):
      value = 'HEAD_USHD'

      if self.dut.failureState == 'AGC_JOG' and self.dut.nextOper == 'PRE2':
          try:
             entries = self.dut.dblData.Tables('P238_MICROJOG_HD_STATUS').tableDataObj()
          except:
             objMsg.printMsg("Attention:Table P238_MICROJOG_HD_STATUS not exist!!!")
             return value

          head = []
          for entry in entries:
             if int(entry['STATUS_CODE']) in [10266,10267] :
                head.append(str(entry['HD_PHYS_PSN']))
          if len(head) > 0:
             self.failHead = list(set(head))
      return value
   
   def ec10279Map(self):
      value = 'NONE'
      if self.dut.nextOper in ['CRT2']:
         value = 'REPRE2'
      return value
   
   def ec10218Map(self):
      value = 'NONE'
      if self.dut.nextOper in ['PRE2', 'FNC2']:
         value = 'FOFPROC_SPINDIP'
      return value

   def ec10280Map(self):
      value = 'MEDIA_TA_Defect'
      try:
         entries = self.dut.dblData.Tables('P107_VERIFIED_FLAWS').tableDataObj()
      except :
         objMsg.printMsg("Attention:Table P107_VERIFIED_FLAWS not exist!!!")
         return value

      media = []
      for entry in entries:
         if int(entry['TA_FLAWS']) > 1024 :
            media.append(str(entry['HD_PHYS_PSN']))

      if len(media) > 0:
         self.failMedia = list(set(media))
      return value

   def ec10289Map(self):
      value = 'HEAD_USHD'
      try:
         entries = self.dut.dblData.Tables('P150_GAIN_SUM').tableDataObj()
      except:
         objMsg.printMsg("Attention:Table P150_GAIN_SUM not exist!!!")
         return value

      head = []
      for entry in entries:
         if float(entry['MAX_PK_PK']) > 6 and (entry['PK_PK_FAIL'] == '*'):
            head.append(str(entry['HD_PHYS_PSN']))

      if len(head) > 0:
         self.failHead = list(set(head))
      return value


   def ec10291Map(self):
      value = 'MEDIA_Scratch'
      if self.dut.failureState == 'D_FLAWSCAN' and self.dut.nextOper == 'FNC2':
          media=[]
          try:
            entries = self.dut.dblData.Tables('P117_MEDIA_SCREEN').tableDataObj()
          except:
            objMsg.printMsg("Attention:Table P117_MEDIA_SCREEN not exist!!!")
            return value
          for entry in entries:
             if entry['SCREEN_PF_FLAG'] =='F' :
                media.append(str(entry['HD_PHYS_PSN']))
          if len(media) > 0:
            self.failMedia= list(set(media))
      return value

   def ec10292Map(self):
      value = 'MEDIA_TA_Defect'
      media=[]
      try:
        entries = self.dut.dblData.Tables('P134_TA_DETCT_TRIPAD').tableDataObj()
      except:
        objMsg.printMsg("Attention:Table P134_TA_DETCT_TRIPAD not exist!!!")
        return value
      for entry in entries:
        if float(entry['TA_WIDTH_TRKS']) > 100:
          media.append(str(entry['HD_PHYS_PSN']))
      if len(media) > 0:
        self.failMedia= list(set(media))
      return value

   def ec10293Map(self):
      value = 'REPRE2'
      if self.dut.failureState == 'D_FLAWSCAN' and self.dut.nextOper == 'FNC2':
         media = []
         try:
            entries = self.dut.dblData.Tables('P215_TA_DFCT_TRK_CNT').tableDataObj()
         except:
            objMsg.printMsg('Attention:Table P215_TA_DFCT_TRK_CNT not exist!!!')
            return value
         for entry in entries:
            if int (entry['DFCT_TRK']) > 200:
               media.append(str(entry['HD_LGC_PSN']))
         if len(media) > 0:
            value = 'MEDIA_DEFECT'
            self.failMedia = list(set(media))
      return value

   def ec10304Map(self):
      value = 'MEDIA_DEFECT/Scratch'
      if self.dut.failureState == 'D_FLAWSCAN' and self.dut.nextOper == 'FNC2':
          media=[]
          try:
            ScratchLengthLimit = TP.prm_filterExcessiveScratches_01['SCRATCH_LENGTH_LIMIT']
            entries = self.dut.dblData.Tables('P117_MEDIA_SCREEN').tableDataObj()
          except:
            objMsg.printMsg("Attention:Table P117_MEDIA_SCREEN not exist!!!")
            return value
          for entry in entries:
             if int(entry['SCRATCH_LENGTH']) > ScratchLengthLimit:
                media.append(str(entry['HD_PHYS_PSN']))
          if len(media) > 0:
            self.failMedia= list(set(media))
      return value
   def ec10352Map(self):
       value = 'HDC'
       if self.dut.failureState == 'RW_GAP_CAL_02' and self.dut.nextOper == 'PRE2':
          try:
             entries = self.dut.dblData.Tables('P_FAULT').tableDataObj()
             entries1 = self.dut.dblData.Tables('P_TRACK').tableDataObj()
          except:
             objMsg.printMsg("Attention:Table P_FAULT or P_TRACK not exist!!!")
             return value
          if len(entries) == len(entries1):
              head = []
              for index in range(0,len(entries)):
                 if str(entries[index]['FAULT_MESSAGE_SOURCE']) == 'ZAP_NORM_RD_CMD_FAILED' and int(entries[index]['FAULT_CODE']) == 10352 \
                   and str(entries[index]['FAULT_MESSAGE']) == 'Svo ZAP-Normalize rd cmd failed (SF2/3 T175)':
                    head.append(str(entries1[index]['HEAD']))
              if len(head) > 0:
                 self.failHead = list(set(head))
                 self.failMedia = list(set(head))
       return value

   def ec10482Map(self):
      value = 'MEDIA_DEFECT'
      if self.dut.failureState == 'D_FLAWSCAN' and self.dut.nextOper == 'FNC2':
          media=[]
          try:
            ScratchLengthLimit = TP.prm_filterExcessiveScratches_01['SCRATCH_LENGTH_LIMIT']
            entries = self.dut.dblData.Tables('P117_MEDIA_SCREEN').tableDataObj()
          except:
            objMsg.printMsg("Attention:Table P117_MEDIA_SCREEN not exist!!!")
            return value
          for entry in entries:
             if int(entry['SCRATCH_LENGTH']) > ScratchLengthLimit:
                media.append(str(entry['HD_PHYS_PSN']))
          if len(media) > 0:
            self.failMedia= list(set(media))
      return value
   def ec10463Map(self):
      valueHead = 'NONE'
      valueMedia = 'NONE'
      value = 'NONE'
      head = []
      media = []
      if self.ec not in [10463,10504,10414,10502]:
         return
      for hd in self.params['RRO_List'].keys():
         if len(self.params['RRO_List'][hd])==0 or len(self.params['NRRO_List'][hd])==0 or len(self.params['RAW_RO_List'][hd])==0:
            break
         if max(self.params['RRO_List'][hd])>=4.5 or max(self.params['NRRO_List'][hd])>=4.5 or max(self.params['RAW_RO_List'][hd])>=4.5:
            head.append(str(hd))
            valueHead = 'HEAD_USHD'
         elif min(self.params['RRO_List'][hd])<4.5 or min(self.params['NRRO_List'][hd])<4.5 or min(self.params['RAW_RO_List'][hd])<4.5:
            media.append(str(hd))
            valueMedia = 'MEDIA_DEFECT'

      self.failMedia= list(set(media))
      self.failHead= list(set(head))
      if valueHead not in ['NONE'] and valueMedia not in ['NONE']:
         value = valueHead
      elif valueHead not in ['NONE'] and valueMedia  in ['NONE']:
         value = valueHead
      elif valueHead  in ['NONE'] and valueMedia not in ['NONE']:
         value = valueMedia
      
      if self.ec in [10502] and self.dut.nextOper == 'PRE2' and self.dut.failureState == 'MDW_CAL' and int(self.dut.failTestInfo['test']) == 189 and value == 'NONE' :
         value = 'MEDIA_MDW'
         try:
            entries = self.dut.dblData.Tables('P_TRACK').tableDataObj()
         except:
            objMsg.printMsg("Attention:Table P_TRACK not exist!!!")
            return value
         head = []
         for entry in entries:
            head.append(str(entry['HEAD']))
         if len(head) > 0:
            self.failHead = list(set(head))
         return value
      return value

   def ec10468Map(self):
      value = 'HEAD_USHD'

      try:
         entries = self.dut.dblData.Tables('P234_EAW_ERROR_RATE2').tableDataObj()
      except:
         return value

      head = []
      for entry in entries:
         if int(entry['FAIL_CODE']) == 10468:
            value = 'HEAD_USHD'
            head.append(str(entry['HD_PHYS_PSN']))
      try:
         if len(head) == 0:
            try:
               entries = self.dut.dblData.Tables('P000_DRIVE_OP_FAILURE').tableDataObj()
            except:
               return value
            for entry in entries:
               head.append(str(entry['HD_PHYS_PSN']))
      except:
         pass

      if len(head) > 0:
         self.failHead = list(set(head))
      return value

   def ec10503Map(self):
      value = 'MEDIA_DEFECT'
      if self.dut.failTestInfo['state'] !='D_FLAWSCAN':
         return 'NONE'
      try:
         entries = self.dut.dblData.Tables('P126_SRVO_FLAW_HD').tableDataObj()
      except:
         return value

      media = []
      for entry in entries:
         if int(entry['SKIP_TRACKS'])>900:
            media.append(str(entry['HD_PHYS_PSN']))

      if len(media) > 0:
         self.failMedia = list(set(media))
      return value

   def ec10506Map(self):
       value = 'NONE'
       if self.dut.failureState == 'DEFECT_LIST' and self.dut.nextOper == 'FIN2':
          self.oSerial = serialScreen.sptDiagCmds()
          self.oSerial.quickDiag()
          reassignData,head = self.oSerial.dumpReassignedSectorList(getHeadbyBBM = True)
          if reassignData['NUMBER_OF_BBMs'] == 0:
             value = 'RePRE2'
          else:
             value = 'Defect list'
             if head:
               self.failHead = list(set(head))
       return value
   def ec10510Map(self):
      value = 'HEAD_USHD'

      try:
         entries = self.dut.dblData.Tables('P140_UNVER_HD_TOTAL').tableDataObj()
      except:
         objMsg.printMsg("Attention:Table P140_UNVER_HD_TOTAL not exist!!!")
         return value

      head = []
      for entry in entries:
         if int(entry['UNVER']) > 6553500:
            head.append(str(entry['HD_PHYS_PSN']))
      if len(head) > 0:
         self.failHead = list(set(head))
      return value

   def ec10522Map(self):
      value = 'HEAD_USHD'
      if self.dut.failTestInfo['test'] != 51 or self.dut.failTestInfo['state'] !='WRITE_SCRN':
         return value
      try:
         entries = self.dut.dblData.Tables('P000_DRIVE_OP_FAILURE').tableDataObj()
      except:
         objMsg.printMsg("Attention:Table P000_DRIVE_OP_FAILURE not exist!!!")
         return value

      head = []
      for entry in entries:
         if entry['SENSE_CODE'] == 'c4090081':
            head.append(str(entry['HD_PHYS_PSN']))
      if len(head) > 0:
         self.failHead = list(set(head))
      return value
   def ec10548Map(self):
      value = 'HEAD_USHD'
      head = []
      for hd in self.params['RRO_List'].keys():
         if len(self.params['RRO_List'][hd])==0 or len(self.params['NRRO_List'][hd])==0 or len(self.params['RAW_RO_List'][hd])==0:
            break
         if max(self.params['RRO_List'][hd])>=5 or max(self.params['NRRO_List'][hd])>=5 or max(self.params['RAW_RO_List'][hd])>=5:
            head.append(str(hd))

      if len(head) > 0:
         self.failHead = list(set(head))
      return value
   def ec10578Map(self):
      value = 'HEAD_USHD'
      spc_id = ''
      if self.dut.failureState == 'WRITE_XFER':
        spc_id = '1'
      elif self.dut.failureState == 'READ_XFER':
        spc_id = '2'

      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=0)
      from IntfClass import CIdentifyDevice
      ret = CIdentifyDevice().ID
      IDmaxLBA = ret['IDDefaultLBAs']
      if ret['IDCommandSet5'] & 0x400:
         IDmaxLBA = ret['IDDefault48bitLBAs']
      DriveCap = str((IDmaxLBA * self.dut.IdDevice['Logical Sector Size'])/1000000000)
      objMsg.printMsg('DriveCap:%s'%str(DriveCap))


      try:
         entries = self.dut.dblData.Tables('P598_ZONE_XFER_RATE').tableDataObj()
      except:
         objMsg.printMsg("Attention:Table P598_ZONE_XFER_RATE not exist!!!")
         return value

      try:
         entries1 = self.dut.dblData.Tables('P598_ZONE_XFER_RATE_CHS').tableDataObj()
      except:
         objMsg.printMsg("Attention:Table P598_ZONE_XFER_RATE_CHS not exist!!!")
         return value


      flagZone = []
      if str(entries[0]['SPC_ID']) == spc_id  and str(entries[-1]['SPC_ID']) == spc_id:
         DBLog_dict = {int(entries[0]['DATA_ZONE']):float(entries[0]['DATA_RATE']),int(entries[-1]['DATA_ZONE']):float(entries[-1]['DATA_RATE'])}
         if (DBLog_dict[int(entries[0]['DATA_ZONE'])] < 80 and DriveCap in ['500','250']) or (DBLog_dict[int(entries[0]['DATA_ZONE'])] < 64 and DriveCap in ['320']):
            flagZone.append(int(entries[0]['DATA_ZONE']))
         if (DBLog_dict[int(entries[-1]['DATA_ZONE'])] < 40 and DriveCap in ['500','250']) or (DBLog_dict[int(entries[-1]['DATA_ZONE'])] < 32 and DriveCap in ['320']):
            flagZone.append(int(entries[-1]['DATA_ZONE']))

      DBLog_RatioDict = {}
      for entry in entries:
        if str(entry['SPC_ID']) == spc_id:
           DBLog_RatioDict[int(entry['DATA_ZONE'])] = float(entry['RATIO'])
           if DBLog_RatioDict[int(entry['DATA_ZONE'])] < 0.8:
              flagZone.append(int(entry['DATA_ZONE']))


      weakHead= []
      if flagZone:
        flagZone = list(set(flagZone))
        for datazone in flagZone:
           for entry1 in entries1:
              if datazone == int(entry1['ZONE']):
                weakHead.append(int(entry1['WEAK_HEAD']))
                continue
        if weakHead and ((float(sum(weakHead)))/len(weakHead) == 1 or (float(sum(weakHead)))/len(weakHead) == 0):
           self.failHead = list(set(weakHead))
        else:
           allHead = []
           for hd in range (0,self.dut.imaxHead):
              allHead.append(str(hd))
           self.failHead = allHead
      return value

   def ec10623Map(self):
      value = 'MEDIA_DEFECT'
      if self.dut.failureState == 'D_FLAWSCAN' and self.dut.nextOper == 'FNC2':
        try:
           entries = self.dut.dblData.Tables('P033_PES_HD2').tableDataObj()[-self.dut.imaxHead:]
        except:
           objMsg.printMsg("Attention:Table P033_PES_HD2 not exist!!!")
           return value

        head = []
        for entry in entries:
          if float(entry['RRO']) > 7 or float(entry['NRRO']) > 8:
            head.append(str(entry['HD_PHYS_PSN']))

        if len(head) > 0:
          self.failHead = list(set(head))
          value = 'HEAD_USHD'
      return value
   def ec10632Map(self):
      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         value = 'NONE'
         try:
            entries = self.dut.dblData.Tables('P_ERROR_RATE_STATUS').tableDataObj()
         except:
            return value

         head = []
         for entry in entries:
            if int(entry['HD_STATUS']) == 10632:
               value = 'HEAD_USHD'
               head.append(str(entry['HD_PHYS_PSN']))

         if len(head) > 0:
            self.failHead = list(set(head))
         return value
      else:
         value = 'HEAD_USHD'
         self.failHead = getattr(self.dut,'AutoFAFailHead',-1)
         return value

   def ec10806Map(self):
      value = 'NONE'
      if self.dut.failureState == 'MDW_CAL' and self.dut.nextOper == 'PRE2' and self.dut.failTestInfo['test'] == 189:
         value = 'REPRE2'
      return value

   def ec11049Map(self):
      value = 'NONE'
      if self.dut.nextOper in ['CRT2']:
         value = 'COMP_PCBA'
         return value
      try:
         if self.dut.failureState == 'MDW_CAL' and self.dut.nextOper == 'PRE2':
            entries = self.dut.dblData.Tables('P193_CRRO_MEASUREMENT2').tableDataObj()
            for entry in entries:
               if float(entry['MABS_FCRRO']) > 10 :
                  value = 'ID_Motor hub'
            return value

         elif self.dut.failureState == 'ZAP':
            head = []
            entries = self.dut.dblData.Tables('P175_ZAP_AUDIT_STATS').tableDataObj()
            for entry in entries:
               if float(entry['MEAN_MABSRRO']) > 10 and "AUDIT_TYPE" == "POST":
                  head.append(str(entry['HD_PHYS_PSN']))
            if len(head) > 0:
               self.failHead = list(set(head))
               value = 'HEAD_USHD'
            return value

         elif self.dut.failureState == 'D_FLAWSCAN' and self.dut.nextOper == 'FNC2':
            head = []
            entries = self.dut.dblData.Tables('P109_UNSAFE_SUMMARY').tableDataObj()
            for entry in entries:
               if int(entry['PES_ERR_CNT']) > 0:
                  head.append(str(entry['HD_PHYS_PSN']))
            if len(head) > 0:
               self.failHead = list(set(head))
               value = 'HEAD_USHD'
            return value

         else:
            return value

      except:
         return value


   def ec11087Map(self):
      value = 'NONE'
      if self.dut.nextOper in ['CRT2']:
         value = 'COMP_PCBA'
      else:
         value = 'MEDIA_MDW'
      return value

   def ec11119Map(self):
      value = 'NONE'
      if self.dut.failureState == 'D_FLAWSCAN' and self.dut.nextOper == 'FNC2': 
         value = 'REPRE2'
      return value

   def ec11126Map(self):
      value = 'HEAD_USHD'
      head = []
      try:
         entries = self.dut.dblData.Tables('P195_SUMMARY').tableDataObj()
      except:
         objMsg.printMsg("Attention:Table P195_SUMMARY not exist!!!")
         return value 
      for entry in entries:
         if int(entry['HD_STATUS']) == 11126:
            head.append(str(entry['HD_PHYS_PSN']))
      if len(head) > 0:
         self.failHead = list(set(head))
      return value 

   def ec11186Map(self):
      value = 'HEAD_USHD'
      if len(self.dut.BurnishFailedHeads) > 0:
         self.failHead = self.dut.BurnishFailedHeads
      return value

   def ec11215Map(self):
      value = 'MEDIA_MDW'
      try:
        entries = self.dut.dblData.Tables('P047_FAIL_STATUS').tableDataObj()
      except:
        objMsg.printMsg("Attention:Table P047_FAIL_STATUS not exist!!!")
        return value

      media = []
      for entry in entries:
         if int(entry['FAIL_CODE']) == 11215:
            media.append(str(entry['HD_PHYS_PSN']))
      if len(media) > 0:
         self.failMedia = list(set(media))
      return value

   def ec11224Map(self):
      value = 'HEAD_USHD'
      if self.dut.failureState == 'LIN_SCREEN1' and self.dut.nextOper == 'PRE2':
          try:
             entries = self.dut.dblData.Tables('P150_GAIN_SUM').tableDataObj()
          except:
             objMsg.printMsg("Attention:Table P150_Gain_Sum not exist!!!")
             return value

          head = []
          for entry in entries:
             if str(entry['CORR_GAIN_FAIL']) == '*':
                head.append(str(entry['HD_PHYS_PSN']))
          if len(head) > 0:
             self.failHead = list(set(head))
      return value
   def ec13459Map(self):
       value = 'NONE'
       if self.dut.failureState == 'MQM' and self.dut.nextOper == 'FIN2':
          self.oSerial = serialScreen.sptDiagCmds()
          self.oSerial.quickDiag()
          reassignData,head = self.oSerial.dumpReassignedSectorList(getHeadbyBBM = True)
          if reassignData['NUMBER_OF_BBMs'] == 0:
             value = 'RePRE2'
          else:
             value = 'Defect list'
             if head:
               self.failHead = list(set(head))
       return value
   def ec14567Map(self):
      value = 'HEAD_USHD'
      if self.dut.failureState == 'AFH1' or self.dut.failureState == 'AFH2':
        try:
           entries = self.dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()
        except:
           objMsg.printMsg("Attention:Table P135_FINALI_CONTACT not exist!!!")
           return value

        head = []
        for entry in entries:
           if int(entry['ERROR_CODE']) == 14567:
              head.append(str(entry['HD_PHYS_PSN']))
        if len(head) > 0:
           self.failHead = list(set(head))
      return value
   def ec14612Map(self):
      value = 'HDC'
      self.failHead = getattr(self.dut, 'AutoFAFailHead',-1)
      return value

   def ec14635Map(self):
      value = 'HEAD_USHD'
      if self.dut.failureState == 'WRITE_SCRN':
          try:
             entries = self.dut.dblData.Tables('P51_SIDE_ENCROACH_BER').tableDataObj()
          except:
             objMsg.printMsg("Attention:Table P51_SIDE_ENCROACH_BER not exist!!!")
             return value
    
          head = []
          for entry in entries:
            if float(entry['ERASURE_BER']) < 4.7:
              head.append(str(entry['HD_PHYS_PSN']))
          if len(head) > 0:
            self.failHead = list(set(head))
      return value

   def ec14663Map(self):
      value = 'HEAD_MRE'
      if self.dut.failTestInfo['test'] != 186 or self.dut.failTestInfo['state'] !='FOF_SCRN':
         return value
      try:
         entries = self.dut.dblData.Tables('P186_BIAS_CAL2').tableDataObj()
      except:
         objMsg.printMsg("Attention:Table P186_BIAS_CAL2 not exist!!!")
         return value

      head = []
      for entry in entries:
         if float(entry['MRE_RESISTANCE']) <80 or float(entry['MRE_RESISTANCE'])>1500:
            head.append(str(entry['HD_PHYS_PSN']))

      if len(head) > 0:
         self.failHead = list(set(head))
      return value

   def ec14670Map(self):
      value = 'HEAD_USHD'
      if self.dut.failTestInfo['state'] !='MDW_CAL':
         return 'NONE'
      try:
         entries = self.dut.dblData.Tables('P185_TRK_0_V3BAR_CALHD').tableDataObj()
      except:
         objMsg.printMsg("Attention:Table P185_TRK_0_V3BAR_CALHD not exist!!!")
         return value

      head = []
      for entry in entries:
         if entry['TRK_DC_OFST']== '0':
            head.append(str(entry['HD_PHYS_PSN']))

      if len(head) > 0:
         self.failHead = list(set(head))
      return value
   def ec14539Map(self):
     if self.dut.nextOper == 'FNC2':
        value = 'RerunPRE2'
        return value

   def ec14703Map(self):
      value = 'HEAD_USHD'
      if self.dut.failureState in ['AFH1','AFH2','AFH4'] and self.dut.nextOper in ['PRE2','CRT2']:
        try:
           entries = self.dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()
        except:
           objMsg.printMsg("Attention:Table P135_FINALI_CONTACT not exist!!!")
           return value
        head = []
        for entry in entries:
           if int(entry['ERROR_CODE']) == 14703:
              head.append(str(entry['HD_LGC_PSN']))
        if len(head) > 0:
           self.failHead = list(set(head))
      return value

   def ec14722Map(self):
     if self.dut.nextOper == 'CRT2':
        value = 'RerunPRE2'
        return value

   def ec14841Map(self):
      value = 'HEAD_USHD'

      try:
         entries = self.dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()
      except:
         objMsg.printMsg("Attention:Table P135_FINALI_CONTACT not exist!!!")
         return value

      head = []
      for entry in entries:
         if int(entry['ERROR_CODE']) == 14841:
            value = 'HEAD_USHD'
            head.append(str(entry['HD_PHYS_PSN']))
      if len(head) > 0:
         self.failHead = list(set(head))
      return value
   def ec14861Map(self):
      value = 'HEAD_USHD'
      if self.dut.failureState == 'WRITE_SCRN':
          try:
             entries = self.dut.dblData.Tables('P51_SIDE_ENCROACH_BER').tableDataObj()
          except:
             objMsg.printMsg("Attention:Table P51_SIDE_ENCROACH_BER not exist!!!")
             return value

          head = []
          for entry in entries:
             if float(entry['ERASURE_BER']) < 5 or float(entry['DELTA_BER']) > 5 or float(entry['DELTA_BER_PERCENTAGE']) > 30 :
                head.append(str(entry['HD_PHYS_PSN']))
          if len(head) > 0:
             self.failHead = list(set(head))
      return value

   def ec14866Map(self):
      value = 'HEAD_USHD'
      if self.dut.failTestInfo['test'] != 135:
         return 'NONE'
      head = []
      try:
         head.append(self.dut.dblData.Tables('P135_FINAL_CONTACT').tableDataObj()[-1]['HD_PHYS_PSN'])
      except:
         objMsg.printMsg("Attention:Table P135_FINAL_CONTACT not exist!!!")
         return value

      if len(head) > 0:
         self.failHead =list(set(head))
      return value

   def ecForT250(self):
      value = 'HEAD_USHD'
      try:
         entries = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()
      except:
         objMsg.printMsg("Attention:Table P250_ERROR_RATE_BY_ZONE not exist!!!")
         return value

      head = []
      for entry in entries:
         if float(entry['RAW_ERROR_RATE']) > -2.3:
            head.append(str(entry['HD_PHYS_PSN']))
      if len(head) > 0:
         self.failHead = list(set(head))
      return value
   def formatErrMap(self):
      value = 'NONE'
      serialformat_err = 0
      if self.errMsg != 'NONE':
         try:
            list_err=self.errMsg.split(':')
            serialformat_err = int(list_err[-1], 16)
         except:
            objMsg.printMsg('AD:CFM - Get serial format error exception!')
      objMsg.printMsg('AD:CFM - serial format err is %x' % serialformat_err)
      if serialformat_err != 0:
         if serialformat_err == 0x84320097:
            value = 'HEAD_USHD'
         elif serialformat_err in [0x843200A6, 0x843200A7, 0x843200A8]:
            value = 'MEDIA_DEFECT'
         elif serialformat_err == 0x84320082:
            value = 'MEDIA_DEFECT'
      elif getattr(self.dut, 'serialformat_err',0) != 0:
         if self.dut.serialformat_err == 0x84320097:
            value = 'HEAD_USHD'
         elif self.dut.serialformat_err in [0x843200A6, 0x843200A7, 0x843200A8]:
            value = 'MEDIA_DEFECT'
         elif self.dut.serialformat_err == 0x84320082:
            value = 'MEDIA_DEFECT'
      try:
         self.doBERByZone()
      except:
         ScrCmds.statMsg('AD: Debug: fail. Traceback=%s' % traceback.format_exc())
      return value
   def doBERByZone(self):
      objPwrCtrl.powerCycle()
      oSerial = serialScreen.sptDiagCmds()
      sptCmds.enableDiags()

      # ** Display Zone Table and collect last cyl of the zone **
      numCyls,zones = oSerial.getZoneInfo(True)

      for hd in zones.keys():
          track = zones[hd]
          for zn in track.keys():
              if zn==0:
                 continue
              LastTrack = track[zn]-1
              objMsg.printMsg("last cyl of the head[%d]zone[%d] is %X" % (hd, zn-1, LastTrack))
          objMsg.printMsg("last cyl of the head[%d]zone[%d] is %X" % (hd, zn, numCyls[hd]))

      #**Turn On BER collection **
      results=sptCmds.execOnlineCmd(CTRL_W, timeout = 20, waitLoops = 100)
      objMsg.printMsg('Turn on BER collection '+ str(results))

      #**Enable Error logging
      sptCmds.gotoLevel('L')
      sptCmds.sendDiagCmd("E1", timeout = 1000, altPattern = None, printResult = True)

      #**For each head, and each zone, do Q from last 100 tracks of the zone
      zoneStatus = {}
      for hd in zones.keys():
         zoneStatus[hd] = []
         track = zones[hd]
         sptCmds.gotoLevel('2')
         sptCmds.sendDiagCmd('A2', timeout = 500, altPattern = None, printResult = True)
         for zn in track.keys():
            if(zn==0):
               continue
            zoneStatus[hd].append(0)
            LastTrack = track[zn]-1
            StartTrack = LastTrack-100
            for i in range(2):
               try:
                  sptCmds.gotoLevel('2')
                  sptCmds.sendDiagCmd("P0000,0000", timeout = 500, altPattern = None, printResult = True)
                  sptCmds.sendDiagCmd("S%X,%d"%(StartTrack,hd) ,timeout = 1000,printResult = True)
                  sptCmds.sendDiagCmd("L,30" ,timeout = 1000,printResult = True)
                  sptCmds.sendDiagCmd("Q", timeout = 500, printResult = True, stopOnError = 0)
                  zoneStatus[hd][-1] = 1
                  break
               except:
                  if i == 0:
                     StartTrack = LastTrack-500
         else:
            StartTrack = numCyls[hd]-100
            zoneStatus[hd].append(0)
            for i in range(2):
               try:
                  sptCmds.sendDiagCmd("P0000,0000", timeout = 500, altPattern = None, printResult = True)
                  sptCmds.sendDiagCmd("S%X,%d"%(StartTrack,hd) ,timeout = 1000,printResult = True)
                  sptCmds.sendDiagCmd("L,30" ,timeout = 1000,printResult = True)
                  sptCmds.sendDiagCmd("Q", timeout = 500, printResult = True, stopOnError = 0)
                  zoneStatus[hd][-1] = 1
                  break
               except:
                  if i == 0:
                     StartTrack-=400

      #**Display Zone BER summary
      information=oSerial.getZoneBERData()
      objPwrCtrl.powerCycle()
   def errPotentialMap(self, ec, oper = 'CERT'):
      errDict = {
         # CERT
         'CERT':
         {
            10007 : self.ec10007Map,
            10119 : self.ec10119Map,
            10136 : self.ec10136Map,
            10137 : 'HEAD_RESONANCE',#self.ec10137Map,,
            10218 : self.ec10218Map,
            10219 : self.formatErrMap,
            10266 : self.ec10266Map,
            10267 : self.ec10266Map,
            10279 : self.ec10279Map,
            10280 : self.ec10280Map,
            10289 :  self.ec10289Map,
            10291 : self.ec10291Map,#'MEDIA1',
            10292 : self.ec10292Map,#'MEDIA_TA',
            10293 : self.ec10293Map,
            10304 : self.ec10304Map,#'MEDIA1',
            10352 : self.ec10352Map,
            10414 : self.ec10463Map,
            10463 : self.ec10463Map,
            10468 : self.ec10468Map,
            10481 : 'HEAD_USHD',
            10482 : self.ec10482Map,#'MEDIA',
            10502 : self.ec10463Map,
            10503 : self.ec10503Map,
            10504 : self.ec10463Map,
            10510 : self.ec10510Map,
            10522 : self.ec10522Map,
            10548 : self.ec10548Map,
            10591 : 'HDC',
            10622 : 'COMP_MOTOR_HUB',
            #10623 : self.ec10623Map,
            10632 : self.ec10632Map,
            #10641 : 'HEAD_USHD',
            10806 : self.ec10806Map,
            11049 : self.ec11049Map,
            11087 : self.ec11087Map,
            11119 : self.ec11119Map,
            11126 : self.ec11126Map,
            11178 : 'COMP_PCBACORUPT',
            11186 : self.ec11186Map,
            11215 : self.ec11215Map,#'MEDIA_MDW',
            11224 : self.ec11224Map,#'HEAD_USHD',
            11294 : 'MEDIA_TA_DEFECT',
            14555 : 'SCRIPT_ISSUE',
            14557 : 'HEAD_USHD',
            14559 : 'HEAD_USHD',
            14567 : self.ec14567Map,
            14612 : self.ec14612Map,
            14613 : self.ec14612Map,
            14614 : self.ec14612Map,
            14635 : self.ec14635Map,
##            14663 : 'HEAD_MRE',#self.ec14663Map,
            14670 : self.ec14670Map,
            14539 : self.ec14539Map,
            14703 : self.ec14703Map,
            14722 : self.ec14722Map,
            14805 : 'HEAD_USHD',
            14841 : self.ec14841Map,
            14861 : self.ec14861Map,#'HEAD_USHD',
            14866 : self.ec14866Map,
            14867 : self.ec14866Map,
            14957 : self.ec14866Map,
         },
         # IO
         'IO':
         {
            10197 : 'Comp_PCBA',
            10219 : self.formatErrMap,
            10578 : self.ec10578Map,#'PERF',
            10506 : self.ec10506Map,
            10632 : self.ec10632Map,
            11098 : 'COMP_PCBA',
            13459 : self.ec13459Map,
            14006 : 'REFIN2',
            14555 : 'Script_issue',
         },
      }
      objMsg.printMsg('Auto FA:ec: %d, oper: %s' % (ec, oper))

      if self.dut.driveattr['POTENTIAL_CAUSE'] in [None, 'NONE']:
         if int(ec) in errDict[oper].keys():
            value = errDict[oper][int(ec)]
            if type(value) == types.MethodType :
               #ScriptComment('Here we go')
               value = value()
            self.dut.driveattr['POTENTIAL_CAUSE'] = value
         # For downgrade on the fly, follow the flow of previous failure code
         elif self.dut.driveattr.get('DNGRADE_ON_FLY', 'NONE')[-5:].isdigit() and int(self.dut.driveattr['DNGRADE_ON_FLY'][-5:]) in errDict[oper].keys():
            value = errDict[oper][int(self.dut.driveattr['DNGRADE_ON_FLY'][-5:])]
            if type(value) == types.MethodType:
               value = value()
            self.dut.driveattr['POTENTIAL_CAUSE'] = value
   #-----------------------------------------------------------------------------------------------------------
   def dumpFailureInfo(self):
      #global failHead
      #line = []
      entry = []
      for hd in range(self.dut.imaxHead):
         line = []
         if str(hd) in self.failHead:
            line.append( hd)
         else:
            line.append( 'F')
         if str(hd) in self.failMedia:
            line.append( hd)
         else:
            line.append('F')
         if line[0] == 'F' and line[1] == 'F':
            continue
         entry.append(line)
         
      '''
      status = 'P'
      if self.dut.driveattr.get('POTENTIAL_CAUSE', 'NONE') != 'NONE':
         status = 'F'
      '''
      objMsg.printMsg('AD: POTENTIAL_CAUSE ==> %s' %self.dut.driveattr.get('POTENTIAL_CAUSE', 'NONE'))
      ScriptComment('P000_CFM_TABLE:', writeTimestamp = 0)
      ScriptComment('%-17s%-25s%-25s'%('HEAD', 'MEDIA','POTENTIAL_CAUSE'), writeTimestamp = 0)
      if entry:
         for i in range(len(entry)):
            #ScriptComment('%-17s%-25s%-25s'%(failHead, self.dut.driveattr.get('POTENTIAL_CAUSE', 'NONE'), status), writeTimestamp = 0)
            ScriptComment('%-17s%-25s%-25s'%(entry[i][0], entry[i][1],self.dut.driveattr.get('POTENTIAL_CAUSE', 'NONE')), writeTimestamp = 0)
      else:
         for i in range(self.dut.imaxHead):
            ScriptComment('%-17s%-25s%-25s'%('F', 'F' ,self.dut.driveattr.get('POTENTIAL_CAUSE', 'NONE')), writeTimestamp = 0)
   #-------------------------------------------------------------------------------------------------------
   def run(self, ec):
      self.ec = ec
      objMsg.printMsg('Auto FA: Script Rev: %s' %self.scriptInfo['AUTOFA Script Rev'])
      objMsg.printMsg('Auto FA with ec: %d'%ec)
      self.dut.driveattr['POTENTIAL_CAUSE'] = 'NONE'
      try:
         self.errMsg = self.dut.failureData[0][0]
      except:
         self.errMsg = 'NONE'
      if self.dut.sptActive.getMode() == self.dut.sptActive.availModes.mctBase:
         try:
            self.runDiagWithSF3Mode()
         except:
            ScrCmds.statMsg('Auto FA Debug: fail. Traceback=%s' % traceback.format_exc())
         self.errPotentialMap(self.ec, 'CERT')
      else:
         try:
            self.runDiagWithF3Mode()
         except:
            ScrCmds.statMsg('Auto FA Debug: fail. Traceback=%s' % traceback.format_exc())
         self.errPotentialMap(self.ec, 'IO')

         try:  # display buffer if there is miscompare error
            if hasattr(sptCmds, 'rwErrVal') and sptCmds.rwErrVal in ["8E1D0080", ]:
               objMsg.printMsg('Auto FA  sptCmds.rwErrVal: %s sptCmds.ErrLLLCHS: %s' % (sptCmds.rwErrVal, sptCmds.ErrLLLCHS))
               _c, _h, _s = sptCmds.ErrLLLCHS.split(".")
               sptCmds.gotoLevel('2')
               sptCmds.sendDiagCmd("S%s,%s" % (_c, _h), printResult = True)
               sptCmds.sendDiagCmd("A0", printResult = True)
               sptCmds.sendDiagCmd("R%s" % _s, printResult = True)
               res = sptCmds.sendDiagCmd("B", printResult = True)
         except:
            ScrCmds.statMsg('Auto FA rwErrVal warning. Traceback=%s' % repr(traceback.format_exc()))

      self.dumpFailureInfo()

      

