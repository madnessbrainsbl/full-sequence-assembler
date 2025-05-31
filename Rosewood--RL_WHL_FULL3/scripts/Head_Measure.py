#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Head MeasureMent Module
#  - Contains support for heater resistance maesurement states (GMR_RES_* etc.)
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/16 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Head_Measure.py $
# $Revision: #7 $
# $DateTime: 2016/12/16 00:28:06 $
# $Author: chengyi.guo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Head_Measure.py#7 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from PowerControl import objPwrCtrl
import ScrCmds
from Process import CProcess
from dbLogUtilities import DBLogReader

#----------------------------------------------------------------------------------------------------------
class CSettlingTestAllHd(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import CFSO
      from AFH import CdPES
      from Process import CCudacom
      from Utility import CUtility
      import math

      self.oUtility = CUtility()
      self.oCudacom = CCudacom()
      self.oFSO = CFSO()
      self.odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)

      if not testSwitch.ENABLE_CLR_SETTLING_STATE:
         objMsg.printMsg("CLR settling test disabled ")
         return

      retryCnt = self.params.get('RETRY_COUNT', 0)+1
      for retry in range(retryCnt):
         try:
            self.dut.dblData.delTable('P190_HSC_DATA', forceDeleteDblTable = 1)
            self.dut.dblData.delTable('P190_CSC_DATA', forceDeleteDblTable = 1)
         except:
            objMsg.printMsg("cccccccccccccccfffffffffffffffffff delete table failed" )
         objMsg.printMsg("CLR settling test based on HSC: Run ")
         self.oFSO.St({'test_num': 172, 'prm_name':'prm_vbar_rap_172', 'timeout':1200, 'spc_id': 0, 'CWORD1':0x2,})

         if 1:
            try:
               self.dut.dblData.Tables('P190_HSC_DATA').deleteIndexRecords(1)#del file pointers
               self.dut.dblData.delTable('P190_HSC_DATA')#del RAM objects
            except:
               objMsg.printMsg("table delete failed. ")
               pass

            ColdDownDelay = 30*60*1
            objMsg.printMsg(" ==== SpinDown Drive for %d seconds ====" % ColdDownDelay)
            objPwrCtrl.powerOff()
            ScriptPause(ColdDownDelay)
   ##         ScriptPause(5)
            objMsg.printMsg("=================================================")
            objMsg.printMsg(" <<< Wake Up and Continue testing, collect HSC data.... >>>")
            objMsg.printMsg("=================================================")

   ##         if objRimType.CPCRiser():
   ##            objPwrCtrl.powerOn(ataReadyCheck = False)
   ##         else:
   ##            objPwrCtrl.powerOn()

            objPwrCtrl.powerOn(useESlip=1)

            bercold = []
            berhot = []

            if testSwitch.Delta_BER_IN_CLR_SETTLING:   # Delta BER check in clr setting
               #Cold BER
               #self.oFSO.St({'test_num':250, 'prm_name':['ColdBER_prm_250'], 'RETRIES': 50, 'MAX_ITERATION':0x705, 'ZONE_POSITION': 198, 'spc_id': 1998 + retry*10, 'MAX_ERR_RATE': -90, 'TEST_HEAD': 255, 'NUM_TRACKS_PER_ZONE': 10, 'SKIP_TRACK': 200, 'TLEVEL': 0, 'MINIMUM': -17, 'timeout': 120.0, 'ZONE_MASK': (0L, 1), 'WR_DATA': 0, 'CWORD1': 0x583})
               Local_ClrSettling_ColdBER_prm_250 =  TP.ClrSettling_ColdBER_prm_250.copy()
               Local_ClrSettling_ColdBER_prm_250.update({'spc_id': Local_ClrSettling_ColdBER_prm_250['spc_id'] + retry*10})
               self.oFSO.St(Local_ClrSettling_ColdBER_prm_250)
               tableData2 = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()

               for head in range(self.dut.imaxHead):
                  bercold.append(0)
                  berhot.append(0)

               for head in range(self.dut.imaxHead):
                  for row in tableData2:
                     if (int(row['SPC_ID']) == (Local_ClrSettling_ColdBER_prm_250['spc_id'] + retry*10)) :
                        bercold[int(row['HD_LGC_PSN'])] = float(row['RAW_ERROR_RATE'])

            #zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
            Prm_190 = TP.Prm_190_Settling.copy()
            Prm_190.update({'spc_id': Prm_190['spc_id'] + retry*10})

            try:
               self.dut.dblData.delTable('P190_HSC_DATA', forceDeleteDblTable = 1)
            except:
               objMsg.printMsg("cccccccccccccccfffffffffffffffffff delete table failed" )

            SetFailSafe()
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT: 
                MaskList = self.oUtility.convertListToZoneBankMasks(Prm_190['ZONE'])
                Prm_190.pop('ZONE')
                objMsg.printMsg("MaskList = %s" % MaskList)
                for bank,list in MaskList.iteritems():
                   if list:
                      objMsg.printMsg("list = %s" % list) 
                      Prm_190 ['BIT_MASK_EXT'], Prm_190 ['BIT_MASK'] = self.oUtility.convertListTo64BitMask(list)
                      Prm_190 ['ZONE_MASK_BANK'] = bank
                      objMsg.printMsg("Prm_190 = %s" % Prm_190)
                      self.oFSO.St(Prm_190)
            else:
                if 'ZONE' in Prm_190: del Prm_190['ZONE']
                self.oFSO.St(Prm_190)
            ClearFailSafe()

            if testSwitch.Delta_BER_IN_CLR_SETTLING: #delta ber check during clr settling
               objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)  # added pwrcycle to reset drv b4 BER collection
               #Hot BER
               #self.oFSO.St({'test_num':250, 'prm_name':['HotBER_prm_250'], 'RETRIES': 50, 'MAX_ITERATION':0x705, 'ZONE_POSITION': 198, 'spc_id': 1999 + retry*10, 'MAX_ERR_RATE': -90, 'TEST_HEAD': 255, 'NUM_TRACKS_PER_ZONE': 10, 'SKIP_TRACK': 200, 'TLEVEL': 0, 'MINIMUM': -17, 'timeout': 120.0, 'ZONE_MASK': (0L, 1), 'WR_DATA': 0, 'CWORD1': 0x583})
               Local_ClrSettling_HotBER_prm_250 =  TP.ClrSettling_HotBER_prm_250.copy()
               Local_ClrSettling_HotBER_prm_250.update({'spc_id': Local_ClrSettling_HotBER_prm_250['spc_id'] + retry*10})
               self.oFSO.St(Local_ClrSettling_HotBER_prm_250)

               tableData3 = self.dut.dblData.Tables('P250_ERROR_RATE_BY_ZONE').tableDataObj()

               for head in range(self.dut.imaxHead):
                  for row in tableData3:
                     if (int(row['SPC_ID']) == (Local_ClrSettling_HotBER_prm_250['spc_id'] + retry*10)) :
                        berhot[int(row['HD_LGC_PSN'])] = float(row['RAW_ERROR_RATE'])

               objMsg.printMsg("coldccccccccccccccccc %s" % str(bercold))     #debug
               objMsg.printMsg("hotccccccccccccccccc %s" % str(berhot))     #debug

         #retrieve preamp heater only once
         if testSwitch.FE_0110575_341036_ENABLE_MEASURING_CONTACT_USING_TEST_135 == 1:
            if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
               import AFH_Screens_DH
            else:
               import AFH_Screens_T135
         else:
            if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
               import AFH_Screens_DH
            else:
               import AFH_Screens_T035

         self.odPES = CdPES(TP.masterHeatPrm_11, TP.defaultOCLIM)
         self.odPES.frm.clearCM_SIM_method(self.params.get('clearCM_SIM', 0))

         oPreamp = CPreAmp()
         self.odPES.setMasterHeat(TP.masterHeatPrm_11, setMHeatOn = 1) #enable master heat

         self.odPES.lmt.maxDAC = (2**TP.dpreamp_number_bits_DAC.get(self.dut.PREAMP_TYPE, 0)) - 1

         if 0:                           #testSwitch.AFH_Brinks_Srvo_Cntr == 1:
            self.odPES.oServoFunctions.modifyServoController()

         coefs = self.odPES.getClrCoeff(TP.clearance_Coefficients, self.dut.PREAMP_TYPE, self.dut.AABType)

         #retrieve rpm only once
         tmpParam = dict(TP.getRpmPrm_11_HSC.copy())
         tmpParam["START_ADDRESS"] = self.oUtility.ReturnTestCylWord(144)
         tmpParam["END_ADDRESS"] = self.oUtility.ReturnTestCylWord(144)
         self.oFSO.St(tmpParam)
         rpm=int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)

         for head in range(self.dut.imaxHead):
            #if testSwitch.virtualRun: break
            hp0=0
            hp1=0
            hp2=0
            hp3=0
            hp_3=0
            hp_2=0
            hp_1=0
            hp_0=0
            MAXCSC=0
            MAXCSC1=0
            MAXCSC2=0
            DECAY=0
            CSC_FACTOR1=0.9
            CSC_FACTOR2=50
            rt = 30     #30mins
            MIN_CSC= 1  #1A
            CSCUCL = 7   #A
            CSCLCL = 1   #A
            CSCSTDEV = 2 #A

            try:
                tableData = self.dut.dblData.Tables('P190_HSC_DATA').tableDataObj()
                objMsg.printMsg("processing hsc data for head ----------- %d " %(head ) )
            except:
                objMsg.printMsg("P190_HSC_DATA cannot be retrieved, please check if P190 is suppose to fail. Data processing for P190 will not be execute!!!!!!!!!! " )
                return

            hsc0 = []
            hsc1 = []

            for row in tableData:
               if (int(row['HD_LGC_PSN'])== head) and (int(row['INDEX1']) != 999):                                   #(int(row['INDEX1']) == 29):
                  hsc0.append( int(row['HSC_2T'])  )
                  hsc1.append( int(row['READ_INDEX']) )
                  head =  int(row['HD_LGC_PSN'])
                  zone  =  int(row['DATA_ZONE'])
                  trk  =  int(row['TRK_NUM'])

            #################################################################
            ## Radius

            mCylinder=(trk>>16)&0xFFFF
            lCylinder = trk&0xFFFF
            buf, errorCode = self.oCudacom.Fn(1370, lCylinder, mCylinder, head, 0)
            result = struct.unpack(">LLH", buf)
            radius = (result[2]/(16.0*1000.0))

            #################################################################
            ## Data rate
            from FSO import dataTableHelper
            self.dth = dataTableHelper()
            self.oFSO.getZoneTable() # get zone table
            zonetable = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
            Index = self.dth.getFirstRowIndexFromTable_byZone(zonetable, head, zone)
            datarate  = float(zonetable[Index]['NRZ_FREQ'])

            #################################################################
            ##kfci calculation
            Kfci = 60*datarate*(Prm_190["FREQUENCY"])/(2*3.1416*radius*rpm*100)


            datarate=datarate*(Prm_190["FREQUENCY"])/100

            objMsg.printMsg( "head  ======================= %d"   % (head))
            objMsg.printMsg( "LN zone   ======================= %d"   % (zone))
            objMsg.printMsg( "LN track      ======================= %d"   % (trk))
            objMsg.printMsg( "Kfci     = %f"   % (60*datarate/(2*3.1416*radius*rpm)))
            objMsg.printMsg( "datarate : %f"   % (datarate))
            objMsg.printMsg( "radius : %f"   % (radius))
            objMsg.printMsg( "rpm  : %f"   % (rpm))

            aa =[]
            decay_hp=[]
            pf = 0
            HIRP2_list=[]

            for i in range(0,Prm_190["LOOP_CNT"]):

               #objMsg.printMsg( "hsc0  : %d " %(hsc0[i] ) )
               #objMsg.printMsg( "hsc1  : %d " %(hsc1[i] ) )

               l_2T = (radius*2*3.14159*rpm*4)/(60*(datarate/1000))
               #objMsg.printMsg( "l(2T wavelength) = (radius*2 p*rpm*4)/(60*(f/1000)) = %f"   % (l_2T))
               #objMsg.printMsg( "HIRP2 = (l_2T/(2*3.14159))*(math.log(hsc1/hsc0)) = " )
               aa = (l_2T/(2*3.14159));
               #objMsg.printMsg( "(l_2T/(2*pi)) = %f"   % (aa))
               try:
                  aa =  aa*(math.log(float(hsc1[i])/float(hsc0[i])))*254
               except:
                  objMsg.printMsg("math.log (hsc1/hsc0) failed!!!!!!!!!!!!!!!!!!!!!")

               #objMsg.printMsg( "HIRP2 ===index: %d =====================================================: %f angstroms"   % (i,aa))

               #objMsg.printMsg( "gammaWriterHeatercoeff 1=========================================================: %f "   % (coefs['gammaWriterHeater'][0]))
               #objMsg.printMsg( "gammaWriterHeatercoeff 2=========================================================: %f "   % (coefs['gammaWriterHeater'][1]))
               #objMsg.printMsg( "gammaWriterHeatercoeff 3=========================================================: %f "   % (coefs['gammaWriterHeater'][2]))

               gammaH = float( coefs['gammaWriterHeater'][0] )  +    float( coefs['gammaWriterHeater'][1] )*float(trk/1000) +      float( coefs['gammaWriterHeater'][2] )*float(trk/1000)*float(trk/1000)
               HIRP2_g = gammaH*aa

               #objMsg.printMsg( "HIRP2_Gamma ==========================================================: %f angstroms"   % (HIRP2_g))

               dblog_record = {
                    'HD_PHYS_PSN'     : head,
                    'DATA_ZONE'       : zone,
                    'ITERATION'       : i,
                    'TRACK'           : trk,
                    'HSC0'            : hsc0[i],
                    'HSC1'            : hsc1[i],
                    'HIRP2'           : HIRP2_g,
                    }
               self.dut.dblData.Tables('P190_CSC_DATA').addRecord(dblog_record)

               HIRP2_list.append(HIRP2_g)


               if (i==1):
                  hp1=HIRP2_g
               if (i==2):
                  hp2=HIRP2_g
                  try:
                     decay_hp.append(hp1/hp2)
                  except:
                     decay_hp.append(999)
                     pf=1
               if (i==3):
                  hp3=HIRP2_g
                  try:
                     decay_hp.append(hp2/hp3)
                  except:
                     decay_hp.append(999)
                     pf=1
               if (i==4):
                  hp4=HIRP2_g
                  try:
                     decay_hp.append(hp3/hp4)
                  except:
                     decay_hp.append(999)
                     pf=1

               decay_hp.sort()

               #objMsg.printMsg("decay_hpcccccccccccc %s" % str(decay_hp))

               if (i==(Prm_190["LOOP_CNT"]-1)):
                  hp_0=HIRP2_g
               if (i==(Prm_190["LOOP_CNT"]-2)):
                  hp_1=HIRP2_g
               if (i==(Prm_190["LOOP_CNT"]-3)):
                  hp_2=HIRP2_g


               if (i==(Prm_190["LOOP_CNT"]-1)):
                  MAXCSC=(hp_2+hp_1+hp_0)/3
                  MAXCSC1=MAXCSC*CSC_FACTOR1
                  MAXCSC2=MAXCSC*CSC_FACTOR2
                  try:
                     #DECAY=(hp3/hp4 +hp2/hp3 +hp1/hp2)/3
                     DECAY=decay_hp[1]
                  except:
                     DECAY= 999
                     pf=1

                  a=lambda d:(sum((x-1.*sum(d)/len(d))**2 for x in d)/(1.*(len(d)-1)))**.5

                  #objMsg.printMsg("HIRP2_listcccccccccccc %s" % str(HIRP2_list))

                  stdev=a(HIRP2_list)

                  csc_hap = MAXCSC1

                  if MAXCSC1>7:
                     csc_hap = 0
                  if MAXCSC1<1:
                     csc_hap = 0
                  if stdev>2:
                     csc_hap = 0


                  if (DECAY*100 <= 50):
                     dcy_hap = 50
                  if (DECAY*100 >= 80):
                     dcy_hap = 80
                  if (DECAY*100 > 50) and (DECAY*100 < 80):
                     dcy_hap = round(DECAY*100)


                  dblog_record1 = {
                          'HD_PHYS_PSN'     : head,
                          'BER_COLD'        : 0,
                          'BER_HOT'         : 0,
                          'BER_Delta'       : 0,
                          'MAXCSC'          : ("%.7f"%(MAXCSC)),
                          'MAXCSC1'         : ("%.7f"%(MAXCSC1)),
                          'STDEV'           : ("%.8f"%(stdev)),
                          'DECAY'           : ("%.6f"%(DECAY)),
                          'MINCSC'          : 1,
                          'MAXCSC2'         : CSC_FACTOR2,
                          'REMARK'          : pf,
                          'MAXCSC1_HAP'     : round(csc_hap),
                          'DECAY_HAP'       : dcy_hap,
                  }

                  if testSwitch.Delta_BER_IN_CLR_SETTLING:
                     dblog_record1.update({'BER_COLD'  : ("%.7f"%(bercold[head])),
                                           'BER_HOT'   : ("%.7f"%(berhot[head])),
                                           'BER_Delta' : ("%.7f"%(bercold[head]-berhot[head]))})

                  self.dut.dblData.Tables('P190_CSC_SUMMARY').addRecord(dblog_record1)

         #power cylce only once
         self.oFSO.St({'test_num': 172, 'prm_name':'prm_vbar_rap_172', 'timeout':1200, 'spc_id': 0, 'CWORD1':0x2,})
         objMsg.printMsg(" ==== Test finished , SpinDown Drive for %d seconds ====" % 60)
         objPwrCtrl.powerOff()
         ScriptPause(60)
         objMsg.printMsg("========================================================================================================")
         objMsg.printMsg("========================================================================================================")

         objPwrCtrl.powerOn(useESlip=1)
         self.oFSO.St({'test_num': 172, 'prm_name':'prm_vbar_rap_172', 'timeout':1200, 'spc_id': 0, 'CWORD1':0x2,})

         objMsg.printDblogBin(self.dut.dblData.Tables('P190_CSC_DATA'))
         objMsg.printDblogBin(self.dut.dblData.Tables('P190_CSC_SUMMARY'))

         if testSwitch.ENABLE_CSC_SCREEN:
            cscDeltaBerStatus = 0
            try:
               objMsg.printMsg("ENABLE_CSC_SCREEN is enabled.")
               objMsg.printMsg("testSwitch.ENABLE_CSC_SCREEN = %d" % testSwitch.ENABLE_CSC_SCREEN)
               objMsg.printMsg("MAX_CSC_REQUIRED = %.3f" % TP.CSCScrnSpec['MAX_CSC_REQUIRED'])
               objMsg.printMsg("BER_COLD_REQUIRED = %.3f" % TP.CSCScrnSpec['BER_COLD_REQUIRED'])
               objMsg.printMsg("BER_DELTA_REQUIRED = %.3f" % TP.CSCScrnSpec['BER_DELTA_REQUIRED'])

               PCscTbl = self.dut.dblData.Tables('P190_CSC_SUMMARY').tableDataObj()
               for entry in PCscTbl:
                  objMsg.printMsg("MAXCSC = %.3f" % entry.get('MAXCSC'))
                  objMsg.printMsg("BER_COLD = %.3f" % entry.get('BER_COLD'))
                  objMsg.printMsg("BER_Delta = %.3f" % entry.get('BER_Delta'))
                  if float(entry.get('MAXCSC')) > TP.CSCScrnSpec['MAX_CSC_REQUIRED'] and \
                     float(entry.get('BER_COLD')) > TP.CSCScrnSpec['BER_COLD_REQUIRED'] and \
                     float(entry.get('BER_Delta')) > TP.CSCScrnSpec['BER_DELTA_REQUIRED']:
                     cscDeltaBerStatus = 1
                     #ScrCmds.raiseException(48537, "Can not meet CSC spec" )
            except:
               objMsg.printMsg("P190_CSC_SUMMARY not found!!!!!")

            if cscDeltaBerStatus:
               if retry >= retryCnt - 1:
                  ScrCmds.raiseException(48537, "Can not meet CSC spec" )
               else:
                  objMsg.printMsg("Can not meet CSC spec, trigger CSC retry" )
                  try:
                     self.dut.dblData.delTable('P190_CSC_SUMMARY', forceDeleteDblTable = 1)
                  except:
                     objMsg.printMsg("cccccccccccccccfffffffffffffffffff delete table failed" )
            else:
               break


      if testSwitch.CLR_SETTLING_CLOSEDLOOP:

         MAXCSC_W =0x0000
         DECAY_W = 0x0000
         CONS_W  = CSC_FACTOR2*256 + 1

         objMsg.printMsg('-'*   500 )

         tableData2 = self.dut.dblData.Tables('P190_CSC_SUMMARY').tableDataObj()


         #for head in range(0,self.dut.imaxHead):
         if 1:
            for row in tableData2:
               if (int(row['HD_PHYS_PSN']) == 0):
                  MAXCSC_W= MAXCSC_W + int(row['MAXCSC1_HAP'])
                  DECAY_W= DECAY_W + int(row['DECAY_HAP'])
               if (int(row['HD_PHYS_PSN']) == 1):
                  MAXCSC_W= MAXCSC_W + int(row['MAXCSC1_HAP'])*256
                  DECAY_W= DECAY_W + int(row['DECAY_HAP'])*256

         self.oFSO.St({'test_num':172, 'prm_name':'Display RAP', 'timeout':1800, 'CWORD1':0x9})

         #the line below control CSC ON or OFF in RAP, CLR_SETTLING_CLOSEDLOOP
         #which means without this line, CSC is still OFF, although F3 is CSC-capable and the RAP are all updated based on SETTLING state measurements
         self.oFSO.St({'test_num':178}, CWORD1 = (0x0220), RAP_WORD = ((29696)/2+5, 0x0001, 0x00FF),)

         self.oFSO.St({'test_num':178}, CWORD1 = (0x0220), RAP_WORD = ((29696+4544)/2, MAXCSC_W, 0xFF00),)
         self.oFSO.St({'test_num':178}, CWORD1 = (0x0220), RAP_WORD = ((29696+4544)/2, MAXCSC_W, 0x00FF),)

         self.oFSO.St({'test_num':178}, CWORD1 = (0x0220), RAP_WORD = ((29696+4544+10)/2, CONS_W, 0xFF00),)
         self.oFSO.St({'test_num':178}, CWORD1 = (0x0220), RAP_WORD = ((29696+4544+10)/2, CONS_W, 0x00FF),)

         self.oFSO.St({'test_num':178}, CWORD1 = (0x0220), RAP_WORD = ((29696+4544+10)/2+1, DECAY_W, 0xFF00),)
         self.oFSO.St({'test_num':178}, CWORD1 = (0x0220), RAP_WORD = ((29696+4544+10)/2+1, DECAY_W, 0x00FF),)


         self.oFSO.St({'test_num':172, 'prm_name':'Display RAP', 'timeout':1800, 'CWORD1':0x9})
      return


#----------------------------------------------------------------------------------------------------------
class CWeakWriteOWTest(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      objMsg.printMsg("Over Write Test: Run ")

      # Reset Tables
      if testSwitch.virtualRun == 0:
         try:
            self.dut.dblData.delTable('P061_OW_MEASUREMENT', forceDeleteDblTable = 1)
         except:
            pass
         try:
            self.dut.dblData.delTable('P061_BAND_OW_MEASUREMENT', forceDeleteDblTable = 1)
         except:
            pass
      tableData = DBLogReader(self.dut, 'P061_OW_MEASUREMENT')
      tableData.ignoreExistingData()
      tableData2 = DBLogReader(self.dut, 'P061_BAND_OW_MEASUREMENT')
      tableData2.ignoreExistingData()

      self.oProc = CProcess()            
      
      # Get Input parameters from State
      if testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
         if self.dut.nextState in ['WEAK_WR_OW2']:
            ow_testzones = self.params.get('OW_ZONE', [0])
         else:
            ow_testzones = [TP.UMP_ZONE[self.dut.numZones][0]]
      else:
         ow_testzones = self.params.get('OW_ZONE', [0])
      smrow_testzones = self.params.get('SMROW_ZONE', [])
      ow_zone_pos = self.params.get('POSITION', [198])
      smrow_zone_pos = self.params.get('SMR_POSITION', [198])

      
      objMsg.printMsg("=================== CMR MODE Measurement==========================")
      for pos in ow_zone_pos:
         prm = TP.WeakWrOWPrm_61.copy()
         prm.update({'ZONE_POSITION': pos})
         if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
            MaskList = self.oProc.oUtility.convertListToZoneBankMasks(ow_testzones)
            for bank, list in MaskList.iteritems():
               if list:
                  prm['BIT_MASK_EXT'], prm['BIT_MASK'] = self.oProc.oUtility.convertListTo64BitMask(list)
                  prm['ZONE_MASK_BANK'] = bank
                  try:
                     self.oProc.St(prm)
                  except:
                     try:
                        objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1) #perform power cycle before this test
                        self.oProc.St(prm)
                     except:                  
                        objMsg.printMsg("WeakWrOWPrm_61 with retry fail")                  
                        pass
                     pass
         else:
            for zn in ow_testzones:
               prm['ZONE'] = zn
               try:
                  self.oProc.St(prm)
               except:
                  objMsg.printMsg("WeakWrOWPrm_61 fail")
                  pass

      if testSwitch.SMR:
         objMsg.printMsg("=================== SMR MODE Measurement==========================")
         prm = TP.WeakWrOWPrm_61.copy()
         prm.update({'CWORD1':0x0031}) # --> Banded Mode
         for pos in smrow_zone_pos:
            prm.update({'ZONE_POSITION': pos})
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               MaskList = self.oProc.oUtility.convertListToZoneBankMasks(smrow_testzones)
               for bank, list in MaskList.iteritems():
                  if list:
                     prm['BIT_MASK_EXT'], prm['BIT_MASK'] = self.oProc.oUtility.convertListTo64BitMask(list)
                     prm['ZONE_MASK_BANK'] = bank
                     try:
                        self.oProc.St(prm)
                     except:
                        objMsg.printMsg("WeakWrOWPrm_61 fail")
                        pass
            else:
               for zn in ow_testzones:
                  prm['ZONE'] = zn
                  try:
                     self.oProc.St(prm)
                  except:
                     objMsg.printMsg("WeakWrOWPrm_61 fail")
                     pass

      if testSwitch.OW_FAIL_ENABLE:
         column_name = 'OW'
         OW_measurement_limit = TP.T61OW_byZone_Limit
         OW_result = {}

         objMsg.printMsg("WeakWriteOWTest Screen %s  with spec %d " %(column_name,OW_measurement_limit ) )
         for row in tableData.iterRows():#for row in tableData:
            hd = int(row['HD_LGC_PSN'])
            zn = int(row['DATA_ZONE'])
            key = hd,zn
            try:
               data = float(row[column_name])
               OW_result.setdefault(key,[]).append(data)
            except: pass
         for key in OW_result.keys():
            if len(OW_result[key]) > 0:
               avg_ow = sum(OW_result[key])/len(OW_result[key])

               if avg_ow < OW_measurement_limit:
                  ScrCmds.raiseException(48450, 'ERROR: WeakWriteOWTest spec failed, (Hd ZN): %s'% str(key))

      if testSwitch.SMROW_FAIL_ENABLE:
         OW_measurement_limit = TP.T61SMROW_Limit
         
         for column_name in ['OW_0','OW_1','OW_2']:         
         
            OW_result = {}

            objMsg.printMsg("WeakWriteOWTest Screen %s  with spec %d " %(column_name,OW_measurement_limit ) )
            for row in tableData2.iterRows():#for row in tableData2:
               hd = int(row['HD_LGC_PSN'])
               zn = int(row['DATA_ZONE'])
               key = hd,zn
               try:
                  data = float(row[column_name])
                  OW_result.setdefault(key,[]).append(data)
               except: pass
               
               
            for key in OW_result.keys():
               failed = 0 

               if len(OW_result[key]) > 0:
                  avg_ow = sum(OW_result[key])/len(OW_result[key])

               for i in range(len(OW_result[key])):
                  if OW_result[key][i] < OW_measurement_limit:
                     failed = failed + 1    

               if failed ==  len(OW_result[key]):
                  objMsg.printMsg("avg_ow %f" % avg_ow)
                  ScrCmds.raiseException(48450, 'ERROR: WeakWriteOWTest spec failed, (Hd ZN): %s'% str(key))

      # For Update on P337 Table (CMR Mode Only)
      try:
         ow_ave_lst_hd = []
         
         for hd in range(0,self.dut.imaxHead):
            zn_lst = []
            for zn in range(self.dut.numZones):
               owlst = []
               ow_ave = 0
               for row in tableData.iterRows(): #for row in tableData:
                  if (int(row['HD_LGC_PSN']) == hd) and (int(row['DATA_ZONE']) == zn):
                     owlst.append(float(row['OW']))

               if len(owlst) > 0:
                  objMsg.printMsg("ow_lst %s" % str(owlst))
                  ow_ave=sum(owlst)/len(owlst)
                  ow_ave_lst_hd.append(ow_ave)
                  zn_lst.append(zn)

         for hd in range(0,self.dut.imaxHead):
            for zn in zn_lst:

               dblog_record = {
                  'SPC_ID'         : self.dut.objSeq.curSeq,#self.dut.objSeq.curRegSPCID,
                  'OCCURRENCE'     : self.dut.objSeq.getOccurrence(),
                  'SEQ'            : self.dut.objSeq.curSeq,
                  'TEST_SEQ_EVENT' : self.dut.objSeq.getTestSeqEvent(0),
                  'HD_PHYS_PSN'     : hd,
                  'DATA_ZONE'       : zn,
                  'HD_LGC_PSN'      : hd,
                  'TRK_NUM'         : 0,
                  'OVERWRITE'       : ow_ave_lst_hd[hd],
                  'HD_STATUS'       : 0,
                  }

               self.dut.dblData.Tables('P337_OVERWRITE').addRecord(dblog_record)

         objMsg.printDblogBin(self.dut.dblData.Tables('P337_OVERWRITE'), self.dut.objSeq.curSeq)


      except:
         objMsg.printMsg("OW data processing fail!!! " )
         pass

      if testSwitch.FE_0332210_305538_P_T337_OVERWRITE_SCREEN:
         from dbLogUtilities import DBLogCheck
         dblchk = DBLogCheck(self.dut)
         if ( dblchk.checkComboScreen(TP.T337_OverWrite_Screen_Spec) == FAIL ):
            if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 48450):
               objMsg.printMsg('Failed for Overwrite combo spec, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
            else:
               ScrCmds.raiseException(48450, 'Failed for Overwrite spec @ Head : %s' % str(dblchk.failHead))

      try:
         objPwrCtrl.powerCycle(5000,12000,10,10)
      except:
         pass
      return


#----------------------------------------------------------------------------------------------------------
class COWTest_FastIO(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.dut = dut
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------   
   def run(self):
      objMsg.printMsg("OW FastIO data collection : Run ")

      if testSwitch.OW_DATA_COLLECTION == 1:
         self.oProc = CProcess()
         try:
            self.dut.dblData.Tables('P061_OW_MEASUREMENT').deleteIndexRecords(1)#del file pointers
            self.dut.dblData.delTable('P061_OW_MEASUREMENT')#del RAM objects
            self.dut.dblData.Tables('P186_BIAS_CAL2').deleteIndexRecords(1)#del file pointers
            self.dut.dblData.delTable('P186_BIAS_CAL2')#del RAM objects
         except:
            objMsg.printMsg("table delete failed. ")
            pass

         SetFailSafe()
         try:
            self.oProc.St(TP.prm_186_MRRes_noSync)
            self.oProc.St(TP.WeakWrOWPrm_61_FastIO)
         except:
            pass
         ClearFailSafe()

         ######################################################################################

         try:
            tableData = self.dut.dblData.Tables('P061_OW_MEASUREMENT').tableDataObj()
            tableData1 = self.dut.dblData.Tables('P186_BIAS_CAL2').tableDataObj()
            spcid = 0
            if self.dut.currentState == 'OW_DATA2':
               spcid = 2
            if self.dut.currentState == 'OW_DATA3':
               spcid = 3
            if self.dut.currentState == 'OW_DATA4':
               spcid = 4
            if self.dut.currentState == 'OW_DATA5':
               spcid = 5
            if self.dut.currentState == 'OW_DATA6':
               spcid = 6
            objMsg.printMsg("Update Table P_OW_SUMMARY " )

            hd_mrr=[]


            for head in range(0,self.dut.imaxHead):
               for row in tableData1:
                  if (int(row['HD_LGC_PSN']) == head):
                     hd_mrr.append(float(row['MRE_RESISTANCE']))



            for head in range(0,self.dut.imaxHead):
               for zone in range(self.dut.numZones):
                  for row in tableData:
                     if (int(row['HD_LGC_PSN']) == head) and (int(row['DATA_ZONE']) == zone):
                        self.dut.dblData.Tables('P_OW_SUMMARY').addRecord({
                           'SPC_ID'              :  spcid,
                           'HD_PHYS_PSN'         :  head,
                           'DATA_ZONE'           :  zone,
                           'TRK_NUM'             :  int(row['TRK_NUM']),
                           'HSC_2T'              :  int(row['HSC_2T']),
                           'OW'                  :  float(row['OW']),
                           'MRE_RESISTANCE'      :  hd_mrr[head]
                        })
            objMsg.printDblogBin(self.dut.dblData.Tables('P_OW_SUMMARY'))

            if self.dut.currentState == 'OW_DATA5':
               tableData = self.dut.dblData.Tables('P_OW_SUMMARY').tableDataObj()
               objMsg.printMsg("OW data analysis ")

               for owdata_i in range(2,6):
                  for head in range(0,self.dut.imaxHead):
                     for zone in range(self.dut.numZones):
                        owlst = []
                        mrrlst = []
                        ow_max = 0
                        ow_min = 0
                        ow_ave = 0
                        mrr_zn = 0
                        for row in tableData:
                           if (int(row['SPC_ID']) == owdata_i ) and (int(row['HD_PHYS_PSN']) == head) and (int(row['DATA_ZONE']) == zone):
                              mrrlst.append(float(row['MRE_RESISTANCE']))
                              objMsg.printMsg("MRE_RESISTANCE = %1.1f" % ( float(row['MRE_RESISTANCE'] )))
                              owlst.append(float(row['OW']))
                              objMsg.printMsg("OW = %1.1f" % ( float(row['OW'] )))

                        if len(owlst) > 0:
                           owlst.sort()
                           objMsg.printMsg("ow_lst %s" % str(owlst))
                           ow_max=owlst.pop(-1)
                           ow_min=owlst.pop(0)
                           ow_ave=sum(owlst)/len(owlst)

                        if len(mrrlst) > 0:
                           mrr_zn=mrrlst.pop(0)

                           self.dut.dblData.Tables('P_OW_DATA').addRecord({
                              'TEST_SEQ_EVENT'         : owdata_i,
                              'HD_PHYS_PSN'         :  head,
                              'DATA_ZONE'           :  zone,
                              'OW_MAX'              :  ow_max,
                              'OW_MIN'              :  ow_min,
                              'OW_DELTA'            :  ow_max-ow_min,
                              'OW_AVE'              :  ow_ave,
                              'MRE_RESISTANCE'      :  mrr_zn
                           })

               objMsg.printDblogBin(self.dut.dblData.Tables('P_OW_DATA'))


               tableData2 = self.dut.dblData.Tables('P_OW_DATA').tableDataObj()

               OW_ave_lst=[]
               for row in tableData2:
                  OW_ave_lst.append(float(row['OW_AVE']))

               if len(owlst) > 0:
                  OW_ave_lst.sort()
                  owave_min = OW_ave_lst.pop(0)


               testzones = [0,12]
               for head in range(0,self.dut.imaxHead):
                  for zone in testzones:
                     for row in tableData2:
                        if (int(row['HD_PHYS_PSN']) == head) and (int(row['DATA_ZONE']) == zone):

                           if(int(row['TEST_SEQ_EVENT']) == 2):
                              objMsg.printMsg("Hd: %d Zn: %d BPINOMINAL  : %1.1f" % (int(row['HD_PHYS_PSN']) ,int(row['DATA_ZONE']) , float(row['OW_AVE'] ))  )
                              objMsg.printMsg('*'*   int( (10*float(row['OW_AVE'])) - int((10*owave_min) ) + 10 )      )

                           if(int(row['TEST_SEQ_EVENT']) == 3):
                              objMsg.printMsg("Hd: %d Zn: %d TRIPLET_OPTI: %1.1f" % (int(row['HD_PHYS_PSN']) ,int(row['DATA_ZONE']) , float(row['OW_AVE'] ))  )
                              objMsg.printMsg('*'*   int( (10*float(row['OW_AVE'])) - int((10*owave_min) ) + 10 )    )


                           if(int(row['TEST_SEQ_EVENT']) == 4):
                              objMsg.printMsg("Hd: %d Zn: %d AFH2        : %1.1f" % (int(row['HD_PHYS_PSN']) ,int(row['DATA_ZONE']) , float(row['OW_AVE'] ))  )
                              objMsg.printMsg('*'*   int( (10*float(row['OW_AVE'])) - int((10*owave_min) ) + 10 )    )


                           if(int(row['TEST_SEQ_EVENT']) == 5):
                              objMsg.printMsg("Hd: %d Zn: %d READ_OPIT   : %1.1f" % (int(row['HD_PHYS_PSN']) ,int(row['DATA_ZONE']) , float(row['OW_AVE'] ))  )
                              objMsg.printMsg('*'*   int( (10*float(row['OW_AVE'])) - int((10*owave_min) ) + 10 )     )

                     objMsg.printMsg('-'*   500 )


         except:
            objMsg.printMsg("OW data processing fail!!! " )
            pass
      #####################################################################################


      else:
         objMsg.printMsg("OW_DATA_COLLECTION is off, OW FastIO data collection skipped. ")

      try:
         objPwrCtrl.powerCycle(5000,12000,10,10)
      except:
         pass
      return


#----------------------------------------------------------------------------------------------------------
class CEWAC(CState):
   """
   Retrieve FNC2 BER
   """
   #----------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import struct
      from FSO import CFSO, dataTableHelper
      from Servo import CServo
      from Process import CCudacom
      from PackageResolution import PackageDispatcher

      self.oFSO = CFSO()
      self.dth = dataTableHelper()
      self.oServ = CServo()
      self.oOudacom = CCudacom()

      objMsg.printMsg('--- ZONE TABLE org---')
      self.oFSO.getZnTblInfo(spc_id = 0, supressOutput = 1)

      zn_lookup  = {
                    0: 0x0000,
                    1: 0x0101,
                    2: 0x0202,
                    3: 0x0303,
                    4: 0x0404,
                    5: 0x0505,
                    6: 0x0606,
                    7: 0x0707,
                    8: 0x0808,
                    9: 0x0909,
                    10: 0x0A0A,
                    11: 0x0B0B,
                    12: 0x0C0C,
                    13: 0x0D0D,
                    14: 0x0E0E,
                    15: 0x0F0F,
                    16: 0x1010,
                    17: 0x1111,
                    18: 0x1212,
                    19: 0x1313,
                    20: 0x1414,
                    21: 0x1515,
                    22: 0x1616,
                    23: 0x1717,
                    }

      try:
         self.dut.dblData.Tables('P069_EWAC_DATA').deleteIndexRecords(1)#del file pointers
         self.dut.dblData.delTable('P069_EWAC_DATA')#del RAM objects
         self.dut.dblData.Tables('P069_EWAC_HSC').deleteIndexRecords(1)#del file pointers
         self.dut.dblData.delTable('P069_EWAC_HSC')#del RAM objects
         if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
            self.dut.dblData.Tables('P069_EWAC_SUMMARY').deleteIndexRecords(1)#del file pointers
            self.dut.dblData.delTable('P069_EWAC_SUMMARY')#del RAM objects
      except:
         objMsg.printMsg("## Failed to delete table P069_EWAC_HSC or P069_EWAC_DATA ##")
         pass

      for head in range(self.dut.imaxHead):

         if 0:  # if TEST_AT_FIXED_FREQ
            nrzFreq_org = 0
            nrzFreq_new = 0

            try:
               track = self.getZeroSkewLogicalTrack(head)
            except:
               track = 180000


            self.oServ.rsk(track, head)
            self.readtrack()
            test_zone = self.getfz()

            #Delete file pointers
            self.dut.dblData.Tables(TP.zone_table['table_name']).deleteIndexRecords(1)
            #Delete RAM objects
            self.dut.dblData.delTable(TP.zone_table['table_name'])
            self.oFSO.getZoneTable(newTable = 1, delTables = 1, supressOutput = 0)
            zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
            Index = self.dth.getFirstRowIndexFromTable_byZone(zt, head, test_zone)
            nrzFreq_org = int(zt[Index]['NRZ_FREQ'])

            try:
               bpi_config_to_set = TP.bpi_config[test_zone]
            except:
               objMsg.printMsg("Getting bpi config FAILED!!!!!!!!!!!!!!!!!!!!!................................." )
               bpi_config_to_set = 200
            # Need to set the bpi confi. To be done

            objMsg.printMsg("Update 0-skew zone Frequency ................................." )
            objMsg.printMsg( "bpi_config_to_set=%d" %(bpi_config_to_set) )
            BpiFileType = TP.BpiFileType
            self.oFSO.St({'test_num':210,'timeout': 600, 'CWORD1': 32})
            if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
               self.oFSO.St({'test_num':210, 'CWORD1': 769, 'BPI_GROUP': (bpi_config_to_set, bpi_config_to_set, 0, 0, 0, 0, 0, 0), 'ZONE': zn_lookup[test_zone], 'timeout': 1800, 'HEAD_RANGE': 255, 'spc_id': 0})
            else:
               self.oFSO.St({'test_num':210,'dlfile': (CN, PackageDispatcher(self.dut, BpiFileType).getFileName()), 'CWORD1': 769, 'BPI_GROUP': (bpi_config_to_set, bpi_config_to_set, 0, 0, 0, 0, 0, 0), 'ZONE': zn_lookup[test_zone], 'timeout': 1800, 'HEAD_RANGE': 255, 'spc_id': 0})


            objMsg.printMsg('--- ZONE TABLE updated---')
            self.oFSO.getZnTblInfo(spc_id = 0, supressOutput = 0)



            #Delete file pointers
            self.dut.dblData.Tables(TP.zone_table['table_name']).deleteIndexRecords(1)
            #Delete RAM objects
            self.dut.dblData.delTable(TP.zone_table['table_name'])
            self.oFSO.getZoneTable(newTable = 1, delTables = 1, supressOutput = 0)
            zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
            Index = self.dth.getFirstRowIndexFromTable_byZone(zt, head, test_zone)
            nrzFreq_new = int(zt[Index]['NRZ_FREQ'])

            F_Ration = int(100*nrzFreq_new/nrzFreq_org)

            objMsg.printMsg( "head=%d" %(head) )
            objMsg.printMsg( "track=%d" %(track) )
            objMsg.printMsg( "track=%s" %(str(track)) )
            objMsg.printMsg( "test_zone=%d" %(test_zone) )
            objMsg.printMsg( "bpi_config_to_set=%d" %(bpi_config_to_set) )
            objMsg.printMsg( "F_Ration=%d" %(F_Ration) )

            delay=2

            self.oFSO.St(TP.spinupPrm_2)
            data_tpi = self.getDataTPI(track, head)
            objMsg.printMsg( "data_tpi=%f" %(data_tpi) )


         EWAC_dac = 99

         t69EwacPrm = TP.prm_OW_EWAC_69.copy()
         t69EwacPrm.update({'HEAD_RANGE': (head | (head << 8))})
         try: self.oFSO.St(t69EwacPrm)
         except:
            objMsg.printMsg("T69 call failed. ")
            pass

         try:
            tableData = self.dut.dblData.Tables('P069_EWAC_HSC').tableDataObj()
            for row in tableData:
               if (int(row['HD_LGC_PSN']) == head) and (int(row['P_OFFSET']) == 888):
                  EWAC_dac  = int(row['TOTAL_OFFSET'])
                  test_zone = int(row['DATA_ZONE'])
                  track     = int(row['TRK_NUM'])

                  self.oFSO.St(TP.spinupPrm_2)
                  data_tpi = self.getDataTPI(track, head)
                  objMsg.printMsg( "data_tpi=%f" %(data_tpi) )


                  objMsg.printMsg("EWAC_dac=%d" % EWAC_dac)
                  objMsg.printMsg( 50*"=")
                  objMsg.printMsg( "HSC")
                  objMsg.printMsg( 50*"=")
                  objMsg.printMsg( "head=%d" %head)
                  objMsg.printMsg( "zone=%d" %test_zone)
                  objMsg.printMsg( "track=%d" %track)
                  objMsg.printMsg( "EWAC test Loop %d -----  EWAC = %f uinch" % ( ( 1),  (2*EWAC_dac/(data_tpi*256*1e3)*1e6) ))
                  objMsg.printMsg(50*"=")

                  dblog_record = {
                       'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[head],
                       'DATA_ZONE'       : test_zone,
                       'TRACK'           : track,
                       'EWAC'            : self.oFSO.oUtility.setDBPrecision((2*EWAC_dac/(data_tpi*256*1e3)*1e6),6,4),
                       'HD_LGC_PSN'      : head,
                       }
                  self.dut.dblData.Tables('P069_EWAC_DATA').addRecord(dblog_record)
                  
                  if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
                     self.dut.objSeq.curRegSPCID = 0

                  dblog_record1 = {                                                   #ccyy
                       'SPC_ID'         : self.dut.objSeq.curRegSPCID,
                       'OCCURRENCE'     : self.dut.objSeq.getOccurrence(),
                       'SEQ'            : self.dut.objSeq.curSeq,
                       'TEST_SEQ_EVENT' : self.dut.objSeq.getTestSeqEvent(0),
                       'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[head],
                       'HD_LGC_PSN'      : head,
                       'DATA_ZONE'       : test_zone,
                       'TRK_NUM'         : track,
                       'EWAC_UIN'        : round(  (2*EWAC_dac/(data_tpi*256*1e3)*1e6)          ,3),
                       'EWAC_NM'         : round(  (2*EWAC_dac/(data_tpi*256*1e3)*1e6)/0.03937 ,3),
                       }
                  self.dut.dblData.Tables('P069_EWAC_SUMMARY').addRecord(dblog_record1)

         except:
            objMsg.printMsg("data processing failed. ")
            pass

      try:
         objMsg.printDblogBin(self.dut.dblData.Tables('P069_EWAC_DATA'))
      except:
         objMsg.printMsg("P069_EWAC_DATA print failed. ")
         pass
         
      try:
         objMsg.printDblogBin(self.dut.dblData.Tables('P069_EWAC_SUMMARY'))
      except:
         objMsg.printMsg("P069_EWAC_SUMMARY print failed. ")
         pass         

      objMsg.printMsg( "Pwr cycle to restore zonetable")
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      objMsg.printMsg('--- ZONE TABLE org---')
      self.oFSO.getZnTblInfo(spc_id = 0, supressOutput = 1)

      if (testSwitch.T69EWAC_T61OW_LIMIT_FORCE_REZONE) and (self.dut.nextState == 'EWAC_TEST'):
         self.checkWaterfallCriteria()

   #----------------------------------------------------------------------------------------------------------
   def checkWaterfallCriteria(self):
      if (self.dut.CAPACITY_PN in TP.Native_Capacity):
         from VBAR import CUtilityWrapper
         lowerCapacityAvailable = (CUtilityWrapper(self.dut, {}).SearchLowerCapacityPn()!=0)
         newWaterfall_Req = self.dut.Waterfall_Req
         newDowngradeOTF = self.dut.driveattr['DNGRADE_ON_FLY']
         objMsg.printMsg("checkWaterfallCriteria start with self.dut.Waterfall_Req=%s, DNGRADE_ON_FLY=%s lowerCapacityAvailable=%s" %(newWaterfall_Req,newDowngradeOTF,str(lowerCapacityAvailable)))
         objMsg.printMsg("Retrieving T061 OW Measurement Data")
         try:
            objMsg.printMsg("Avg by Zone OW Limit = %d" % TP.T61OW_byZone_Limit)
            t61table = self.dut.dblData.Tables('P061_OW_MEASUREMENT').tableDataObj()
            T61OWData  = {}
            for row in t61table:
               if row['HD_PHYS_PSN'] not in T61OWData:
                  T61OWData.update({ row['HD_PHYS_PSN']:{} })
               if row['DATA_ZONE'] not in T61OWData[row['HD_PHYS_PSN']]:
                  T61OWData[row['HD_PHYS_PSN']].update({ row['DATA_ZONE']:[] })
               T61OWData[row['HD_PHYS_PSN']][row['DATA_ZONE']].append( float(row['OW_MEASUREMENT']) )

            # === Check of T61 OW data by zone ===
            sumT61OWData = 0.0
            lenT61OWData = 0
            for hd in T61OWData.keys():
               for zn in T61OWData[hd].keys():
                  avgT61OWData  = sum(T61OWData[hd][zn]) * 1.0 / len(T61OWData[hd][zn])
                  sumT61OWData += sum(T61OWData[hd][zn])
                  lenT61OWData += len(T61OWData[hd][zn])
                  objMsg.printMsg("Avg by Zone OW Hd%s Zn%s = %f" % (hd, zn, avgT61OWData))
                  if avgT61OWData < TP.T61OW_byZone_Limit:
                     objMsg.printMsg("Hd%s Zn%s: T61OW by zone exceeded limit (%f) - Force to Lower Capacity !!" % (hd, zn, avgT61OWData))
                     newWaterfall_Req = "REZONE"
                     newDowngradeOTF  = '%s_%s_T61OW' % (self.dut.nextOper, self.dut.partNum[-3:])
               T61OWData[hd] = sumT61OWData * 1.0 / lenT61OWData

            for hd in T61OWData.keys():
               objMsg.printMsg("Avg by Surface OW Hd%s = %f" % (hd, T61OWData[hd]))
               if (self.dut.HGA_SUPPLIER == 'RHO'):
                  T61OWData[hd] = 0.014 * T61OWData[hd] + 1.75
               else:       # for TDK
                  T61OWData[hd] = 0.015 * T61OWData[hd] + 1.75
               objMsg.printMsg("Converted OW data Hd%s = %f" % (hd, T61OWData[hd]))

         except:
            objMsg.printMsg("##  Get T061 OW Measurement error !!  ##")
            pass

         if (not lowerCapacityAvailable) and (newWaterfall_Req == "REZONE") :
            ScrCmds.raiseException(48450, 'Waterfall path not available for T61OW by zone screening')

         # === Comparison of EWAC and T61 OW data ===
         objMsg.printMsg("Retrieving T069 OW Measurement Data")
         try:
            import math
            t69Data = self.dut.dblData.Tables('P069_EWAC_HSC').tableDataObj()
            T69EwacData = {}
            for row in t69Data:
               if (row['P_OFFSET'] == '888'):
                  hd = row['HD_PHYS_PSN']
                  T69EwacData[hd] = int(row['TOTAL_OFFSET'])
                  objMsg.printMsg("Raw Ewac Data Hd%s = %d" % (hd, T69EwacData[hd]))
                  T69EwacData[hd] = math.log10(T69EwacData[hd])
                  objMsg.printMsg("Converted Ewac Data Hd%s = %f" % (hd, T69EwacData[hd]))
            for hd in T69EwacData.keys():
               if hd in T61OWData:
                  if (T69EwacData[hd] > T61OWData[hd]):  # check if limit exceeded
                     objMsg.printMsg("Hd%s: EWAC exceeded OW (%f > %f) - Force to Lower Capacity !!" % (hd, T69EwacData[hd], T61OWData[hd]))
                     newWaterfall_Req = "REZONE"
                     newDowngradeOTF  = '%s_%s_69E61' % (self.dut.nextOper, self.dut.partNum[-3:])
         except:
            objMsg.printMsg("##  Get T069 OW Measurement error !!  ##")
            pass

         if (not lowerCapacityAvailable) and (newWaterfall_Req == "REZONE") :
            ScrCmds.raiseException(48450, 'Waterfall path not available for EWAC_OW screening')

         try:
            t61table.clear()
            t69Data.clear()
            T61OWData.clear()
            T69EwacData.clear()
         except:
            pass

         if lowerCapacityAvailable and not self.dut.depopMask:
            self.dut.Waterfall_Req = newWaterfall_Req
            self.dut.driveattr['DNGRADE_ON_FLY'] = newDowngradeOTF
            objMsg.printMsg("checkWaterfallCriteria end with self.dut.Waterfall_Req=%s, DNGRADE_ON_FLY=%s" %(newWaterfall_Req,newDowngradeOTF))

   #----------------------------------------------------------------------------------------------------------
   def getDataTPI(self,trk, head):
     #get servo ktpi
     self.oFSO.St({'test_num':11,'timeout': 1000, 'SYM_OFFSET': 142, 'ACCESS_TYPE': 0, 'CWORD1': 512, 'spc_id': 1})
     servo_tpi = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
     objMsg.printMsg("servo_tpi=%s" %(servo_tpi))
     #servo_tpi=400
     self.oFSO.St({'test_num':11,'timeout': 1000, 'SYM_OFFSET': 142, 'ACCESS_TYPE': 0, 'CWORD1': 512, 'spc_id': 1})
     arctpi=int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
     objMsg.printMsg("arctpi=%s" %(arctpi))


     objMsg.printMsg( "***********************************************")
     objMsg.printMsg( "***********    TPI Information    ************")
     objMsg.printMsg("--------")
     objMsg.printMsg("Track -1")
     objMsg.printMsg("--------")
     phy_pos=self.GetServoTrk(trk-1,head)

     objMsg.printMsg("Physical position=%f" %(phy_pos))
     objMsg.printMsg("--------")
     objMsg.printMsg("Track")
     objMsg.printMsg("--------")
     phy_pos1=self.GetServoTrk(trk,head)
     objMsg.printMsg("Physical position=%f" %(phy_pos1))

     objMsg.printMsg("------------------------------------------------")
     objMsg.printMsg("Servo TPI=%d" %servo_tpi)
     objMsg.printMsg("kTPI=%f" %(servo_tpi/(phy_pos1-phy_pos)/1000))
     objMsg.printMsg( "***********************************************")
     kTPI = (servo_tpi/(phy_pos1-phy_pos))/1000
     return kTPI

   #----------------------------------------------------------------------------------------------------------
   def getZeroSkewLogicalTrack(self,head=0):
     """
     Set servo offset on current servo tracking position
     @param offset: Servo offset in dac counts [-127,127]
     @return: Error code
     """
     try:
        buf, errorCode = self.oOudacom.Fn(1392, head)
     except:
        pass
     objMsg.printMsg( "errorCode=%d" %(errorCode) )
     objMsg.printMsg( "int(logical_track[0])=%d" %(int(logical_track[0])) )

     #buf, errorCode = __ReceiveResults()
     #if not errorCode:
     logical_track = struct.unpack("L",buf)
     return int(logical_track[0])

   #----------------------------------------------------------------------------------------------------------
   def getfz(self, quietMode = 0):
     """
     Find current zone drive is in.
     fz() can only tell the zone change performed by cudacom commands, such as wsk, rsk, esk.
     @param quietMode: Non-zero quietMode supresses printing of the current zone
     @return: zone number
     """
     buf, errorCode = self.oOudacom.Fn(1204)
     #buf, errorCode = __ReceiveResults()
     hZone = binascii.hexlify(buf)
     zone = int(hZone, 16)
     if quietMode == 0:
         objMsg.printMsg("Current Zone = %u" %( zone))
     return zone

   #----------------------------------------------------------------------------------------------------------
   def readtrack(self,StopOnError=0):
     """
     Read the current track
     @param StopOnError: If set to 1, will stop on read error
     @return: Error code
     """
     buf, errorCode = self.oOudacom.Fn(1356,StopOnError)
     #buf,errorCode = __ReceiveResults()
     #__displayBuffer(buf)
     return errorCode

   #----------------------------------------------------------------------------------------------------------
   def GetServoTrk(self, trk, head):

#      objMsg.printMsg("trk=%d" %(trk))
     errcode = self.oServ.wsk(trk,head)
#      objMsg.printMsg("errcode=%s" %str(errcode))
     self.oFSO.St({'test_num':11,'timeout': 120, 'PARAM_0_4': (9217, 0, 0, 0, 0)})
     servo_data = self.dut.dblData.Tables('P011_SRVO_DIAG_RESP').tableDataObj()
     self.dut.dblData.Tables('P011_SRVO_DIAG_RESP').deleteIndexRecords(confirmDelete=1)
     self.dut.dblData.delTable('P011_SRVO_DIAG_RESP',forceDeleteDblTable = 1)
     num=len(servo_data)
     servo_data1=servo_data[num-1]
     track1=servo_data1[5]+servo_data1['*']
     offset1=servo_data1[7]+servo_data1[6]
     phy_pos1=int(track1,16)+(int(offset1,16)/4096.0)
     return phy_pos1


#----------------------------------------------------------------------------------------------------------
class CWPE(CState):
   """
   Retrieve FNC2 BER
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      import struct
      from FSO import CFSO, dataTableHelper
      from Servo import CServo
      from Process import CCudacom
      from PackageResolution import PackageDispatcher

      self.oFSO = CFSO()
      self.oServ = CServo()
      self.oOudacom = CCudacom()
      self.dth = dataTableHelper()

      objMsg.printMsg('--- ZONE TABLE org---')
      self.oFSO.getZnTblInfo(spc_id = 0)

      zn_lookup  = {
                    0: 0x0000,
                    1: 0x0101,
                    2: 0x0202,
                    3: 0x0303,
                    4: 0x0404,
                    5: 0x0505,
                    6: 0x0606,
                    7: 0x0707,
                    8: 0x0808,
                    9: 0x0909,
                    10: 0x0A0A,
                    11: 0x0B0B,
                    12: 0x0C0C,
                    13: 0x0D0D,
                    14: 0x0E0E,
                    15: 0x0F0F,
                    16: 0x1010,
                    17: 0x1111,
                    18: 0x1212,
                    19: 0x1313,
                    20: 0x1414,
                    21: 0x1515,
                    22: 0x1616,
                    23: 0x1717,
                    }

      try:
         self.dut.dblData.Tables('P069_WPE_HSC').deleteIndexRecords(1)#del file pointers
         self.dut.dblData.delTable('P069_WPE_HSC')#del RAM objects
         self.dut.dblData.Tables('P069_WPE_DATA').deleteIndexRecords(1)#del file pointers
         self.dut.dblData.delTable('P069_WPE_DATA')#del RAM objects
         self.dut.dblData.Tables('P069_WPE_SUMMARY').deleteIndexRecords(1)#del file pointers
         self.dut.dblData.delTable('P069_WPE_SUMMARY')#del RAM objects
      except:
         objMsg.printMsg("## Failed to delete table P069_WPE_HSC, P069_WPE_DATA or P069_WPE_SUMMARY ##")
         pass


      for head in range(self.dut.imaxHead):

         if 0:  # if TEST_AT_FIXED_FREQ
            nrzFreq_org = 0
            nrzFreq_new = 0

            try:
               track = self.getZeroSkewLogicalTrack(head)
            except:
               track = 180000


            self.oServ.rsk(track, head)
            self.readtrack()
            test_zone = self.getfz()


            #Delete file pointers
            self.dut.dblData.Tables(TP.zone_table['table_name']).deleteIndexRecords(1)
            #Delete RAM objects
            self.dut.dblData.delTable(TP.zone_table['table_name'])
            self.oFSO.getZoneTable(newTable = 1, delTables = 1, supressOutput = 0)
            zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
            Index = self.dth.getFirstRowIndexFromTable_byZone(zt, head, test_zone)
            nrzFreq_org = int(zt[Index]['NRZ_FREQ'])

            try:
               bpi_config_to_set = TP.bpi_config[test_zone]
            except:
               objMsg.printMsg("Getting bpi config FAILED!!!!!!!!!!!!!!!!!!!!!................................." )
               bpi_config_to_set = 200
            # Need to set the bpi confi. To be done

            objMsg.printMsg("Update 0-skew zone Frequency ................................." )
            objMsg.printMsg( "bpi_config_to_set=%d" %(bpi_config_to_set) )
            BpiFileType = TP.BpiFileType
            self.oFSO.St({'test_num':210,'timeout': 600, 'CWORD1': 32})
            if testSwitch.FE_0269922_348085_P_SIGMUND_IN_FACTORY:
                self.oFSO.St({'test_num':210,'CWORD1': 769, 'BPI_GROUP': (bpi_config_to_set, bpi_config_to_set, 0, 0, 0, 0, 0, 0), 'ZONE': zn_lookup[test_zone], 'timeout': 1800, 'HEAD_RANGE': 255, 'spc_id': 0})
            else:
                self.oFSO.St({'test_num':210,'dlfile': (CN, PackageDispatcher(self.dut, BpiFileType).getFileName()), 'CWORD1': 769, 'BPI_GROUP': (bpi_config_to_set, bpi_config_to_set, 0, 0, 0, 0, 0, 0), 'ZONE': zn_lookup[test_zone], 'timeout': 1800, 'HEAD_RANGE': 255, 'spc_id': 0})

            objMsg.printMsg('--- ZONE TABLE updated---')
            self.oFSO.St({'test_num': 172, 'prm_name':'prm_vbar_rap_172', 'timeout':1200, 'spc_id': 0, 'CWORD1':0x2,})



            #Delete file pointers
            self.dut.dblData.Tables(TP.zone_table['table_name']).deleteIndexRecords(1)
            #Delete RAM objects
            self.dut.dblData.delTable(TP.zone_table['table_name'])
            self.oFSO.getZoneTable(newTable = 1, delTables = 1, supressOutput = 0)
            zt = self.dut.dblData.Tables(TP.zone_table['table_name']).tableDataObj()
            Index = self.dth.getFirstRowIndexFromTable_byZone(zt, head, test_zone)
            nrzFreq_new = int(zt[Index]['NRZ_FREQ'])

            F_Ration = int(100*nrzFreq_new/nrzFreq_org)

            objMsg.printMsg( "head=%d" %(head) )
            objMsg.printMsg( "track=%d" %(track) )
            objMsg.printMsg( "track=%s" %(str(track)) )
            objMsg.printMsg( "test_zone=%d" %(test_zone) )
            objMsg.printMsg( "bpi_config_to_set=%d" %(bpi_config_to_set) )
            objMsg.printMsg( "F_Ration=%d" %(F_Ration) )

            delay=2

            self.oFSO.St(TP.spinupPrm_2)
            data_tpi = self.getDataTPI(track, head)
            objMsg.printMsg( "data_tpi=%f" %(data_tpi) )


         EWAC_dac = 99

         headrange = self.oFSO.oUtility.converttoHeadRangeMask(head, head)
         testParam = self.oFSO.oUtility.copy(TP.prm_WPE)
         testParam['HEAD_RANGE'] = headrange
         if self.params.get('ZONE_POSITION', 0):
            testParam['ZONE_POSITION'] = self.params.get('ZONE_POSITION', 0)
         try: self.oFSO.St(testParam)
         except:
            objMsg.printMsg("T69 call failed. ")
            pass
         try:
            tableData = self.dut.dblData.Tables('P069_WPE_HSC').tableDataObj()
            for row in tableData:
               if (int(row['HD_LGC_PSN']) == head) and (int(row['TOTAL_OFFSET']) == 999):
                  WPE_dac_L = float(row['N_OFFSET'])
                  WPE_dac_R = float(row['P_OFFSET'])
                  test_zone = int(row['DATA_ZONE'])
                  track     = int(row['TRK_NUM'])


                  self.oFSO.St(TP.spinupPrm_2)
                  data_tpi = self.getDataTPI(track, head)
                  objMsg.printMsg( "data_tpi=%f" %(data_tpi) )



                  objMsg.printMsg( 50*"=")
                  objMsg.printMsg( "HSC")
                  objMsg.printMsg( 50*"=")
                  objMsg.printMsg( "head=%d" %head)
                  objMsg.printMsg( "zone=%d" %test_zone)
                  objMsg.printMsg( "track=%d" %track)
                  objMsg.printMsg( "WPE N test Loop %d -----  WPE_N = %f uinch" % ( ( 1),  (WPE_dac_L/(data_tpi*256*1e3)*1e6) ))
                  objMsg.printMsg( "WPE P test Loop %d -----  WPE_P = %f uinch" % ( ( 1),  (WPE_dac_R/(data_tpi*256*1e3)*1e6) ))

                  objMsg.printMsg(50*"=")
                  dblog_record = {
                       'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[head],
                       'DATA_ZONE'       : test_zone,
                       'TRACK'           : track,
                       'WPEN'            : (WPE_dac_L/(data_tpi*256*1e3)*1e6) ,
                       'WPEP'            : (WPE_dac_R/(data_tpi*256*1e3)*1e6) ,
                       }
                  self.dut.dblData.Tables('P069_WPE_DATA').addRecord(dblog_record)

                  if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
                     self.dut.objSeq.curRegSPCID = 0

                  dblog_record1 = {
                       'SPC_ID'         : self.dut.objSeq.curRegSPCID,
                       'OCCURRENCE'     : self.dut.objSeq.getOccurrence(),
                       'SEQ'            : self.dut.objSeq.curSeq,
                       'TEST_SEQ_EVENT' : self.dut.objSeq.getTestSeqEvent(0),
                       'HD_PHYS_PSN'     : self.dut.LgcToPhysHdMap[head],
                       'HD_LGC_PSN'      : head,
                       'DATA_ZONE'       : test_zone,
                       'TRK_NUM'         : track,
                       'WPE_NEG'         : round((WPE_dac_L/(data_tpi*256*1e3)*1e6),3) ,
                       'WPE_POS'         : round((WPE_dac_R/(data_tpi*256*1e3)*1e6),3) ,
                       'WPE_UIN'         : round(  (( WPE_dac_L/(data_tpi*256*1e3)*1e6)  + (WPE_dac_R/(data_tpi*256*1e3)*1e6))/2          ,3),
                       'WPE_NM'          : round( (( WPE_dac_L/(data_tpi*256*1e3)*1e6)  + (WPE_dac_R/(data_tpi*256*1e3)*1e6))/(2*0.03937) ,3),
                       }
                  self.dut.dblData.Tables('P069_WPE_SUMMARY').addRecord(dblog_record1)

         except:
            objMsg.printMsg("data processing failed. ")
            pass

      try:
         objMsg.printDblogBin(self.dut.dblData.Tables('P069_WPE_DATA'))
      except:
         objMsg.printMsg("P069_WPE_DATA print failed. ")
         pass

      try:
         objMsg.printDblogBin(self.dut.dblData.Tables('P069_WPE_SUMMARY'))
      except:
         objMsg.printMsg("P069_WPE_SUMMARY print failed. ")
         pass


      try:    tbl = self.dut.dblData.Tables('P069_WPE_SUMMARY').tableDataObj()
      except: tbl = []
      wpeHd = [''] * self.dut.imaxHead
      for rec in tbl:
         wpeHd[int(rec['HD_LGC_PSN'])] = '%1.4f' % float(rec['WPE_UIN'])
      wpeUin = ','.join(wpeHd)
      self.dut.driveattr['WPE_UIN'] = wpeUin
      objMsg.printMsg("Saving %s to WPE_UIN..." % wpeUin)

      abnormal_detected = 0
      try:
         wpe_chk = eval('[%s]' % wpeUin)
      except: 
         abnormal_detected = 1
         objMsg.printMsg("abnormal result detected!")
      if abnormal_detected == 0:      
         if not testSwitch.virtualRun:
            wpe_uin = eval('[%s]' % wpeUin)
            objMsg.printMsg("PoorSovaHDInstCombo_Spec1")
            for hd in xrange(self.dut.imaxHead):
               if TP.PoorSovaHDInstCombo_Spec1 and self.dut.modeloss_avg_info[hd] >=  TP.PoorSovaHDInstCombo_Spec1['Mean_MODE_LOSS'] and self.dut.sigmaloss_avg_info[hd] >= TP.PoorSovaHDInstCombo_Spec1['Mean_SIGMA_LOSS'] and wpe_uin[hd] <= TP.PoorSovaHDInstCombo_Spec1['Drive_WPE_uinch']:
                  if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 10560):
                     objMsg.printMsg('Failed PoorSovaHDInstCombo_Spec1, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
                  else:
                     ScrCmds.raiseException(10560, "Failed PoorSovaHDInstCombo_Spec1 @ Head : [%s]" % str(hd))

      objMsg.printMsg( "Pwr cycle to restore zonetable")
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      objMsg.printMsg('--- ZONE TABLE org---')
      self.oFSO.getZnTblInfo(spc_id = 0)

   #----------------------------------------------------------------------------------------------------------
   def getDataTPI(self,trk, head):
     #get servo ktpi
     self.oFSO.St({'test_num':11,'timeout': 1000, 'SYM_OFFSET': 142, 'ACCESS_TYPE': 0, 'CWORD1': 512, 'spc_id': 1})
     servo_tpi = int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
     objMsg.printMsg("servo_tpi=%s" %(servo_tpi))
     #servo_tpi=400
     self.oFSO.St({'test_num':11,'timeout': 1000, 'SYM_OFFSET': 142, 'ACCESS_TYPE': 0, 'CWORD1': 512, 'spc_id': 1})
     arctpi=int(self.dut.dblData.Tables('P011_SV_RAM_RD_BY_OFFSET').tableDataObj()[-1]['READ_DATA'],16)
     objMsg.printMsg("arctpi=%s" %(arctpi))


     objMsg.printMsg( "***********************************************")
     objMsg.printMsg( "***********    TPI Information    ************")
     objMsg.printMsg("--------")
     objMsg.printMsg("Track -1")
     objMsg.printMsg("--------")
     phy_pos=self.GetServoTrk(trk-1,head)

     objMsg.printMsg("Physical position=%f" %(phy_pos))
     objMsg.printMsg("--------")
     objMsg.printMsg("Track")
     objMsg.printMsg("--------")
     phy_pos1=self.GetServoTrk(trk,head)
     objMsg.printMsg("Physical position=%f" %(phy_pos1))

     objMsg.printMsg("------------------------------------------------")
     objMsg.printMsg("Servo TPI=%d" %servo_tpi)
     objMsg.printMsg("kTPI=%f" %(servo_tpi/(phy_pos1-phy_pos)/1000))
     objMsg.printMsg( "***********************************************")
     kTPI = (servo_tpi/(phy_pos1-phy_pos))/1000
     return kTPI

   #----------------------------------------------------------------------------------------------------------
   def getZeroSkewLogicalTrack(self,head=0):
     """
     Set servo offset on current servo tracking position
     @param offset: Servo offset in dac counts [-127,127]
     @return: Error code
     """
     try:
        buf, errorCode = self.oOudacom.Fn(1392, head)
     except:
        pass
     objMsg.printMsg( "errorCode=%d" %(errorCode) )
     objMsg.printMsg( "int(logical_track[0])=%d" %(int(logical_track[0])) )

     #buf, errorCode = __ReceiveResults()
     #if not errorCode:
     logical_track = struct.unpack("L",buf)
     return int(logical_track[0])

   #----------------------------------------------------------------------------------------------------------
   def getfz(self, quietMode = 0):
     """
     Find current zone drive is in.
     fz() can only tell the zone change performed by cudacom commands, such as wsk, rsk, esk.
     @param quietMode: Non-zero quietMode supresses printing of the current zone
     @return: zone number
     """
     buf, errorCode = self.oOudacom.Fn(1204)
     #buf, errorCode = __ReceiveResults()
     hZone = binascii.hexlify(buf)
     zone = int(hZone, 16)
     if quietMode == 0:
         objMsg.printMsg("Current Zone = %u" %( zone))
     return zone
   
   #----------------------------------------------------------------------------------------------------------
   def readtrack(self,StopOnError=0):
     """
     Read the current track
     @param StopOnError: If set to 1, will stop on read error
     @return: Error code
     """
     buf, errorCode = self.oOudacom.Fn(1356,StopOnError)
     #buf,errorCode = __ReceiveResults()
     #__displayBuffer(buf)
     return errorCode

   #----------------------------------------------------------------------------------------------------------
   def GetServoTrk(self, trk, head):

#      objMsg.printMsg("trk=%d" %(trk))
     errcode = self.oServ.wsk(trk,head)
#      objMsg.printMsg("errcode=%s" %str(errcode))
     self.oFSO.St({'test_num':11,'timeout': 120, 'PARAM_0_4': (9217, 0, 0, 0, 0)})
     servo_data = self.dut.dblData.Tables('P011_SRVO_DIAG_RESP').tableDataObj()
     self.dut.dblData.Tables('P011_SRVO_DIAG_RESP').deleteIndexRecords(confirmDelete=1)
     self.dut.dblData.delTable('P011_SRVO_DIAG_RESP',forceDeleteDblTable = 1)
     num=len(servo_data)
     servo_data1=servo_data[num-1]
     track1=servo_data1[5]+servo_data1['*']
     offset1=servo_data1[7]+servo_data1[6]
     phy_pos1=int(track1,16)+(int(offset1,16)/4096.0)
     return phy_pos1


#----------------------------------------------------------------------------------------------------------
class CRdrResChk(CState):
   """
      Description: Get Reader resistance using SF3 test 186
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self,dut,depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if testSwitch.FE_0124433_357552_RUN_GMR_RES_NO_DEMOD:
         if testSwitch.extern.FE_0125575_357552_SAVE_GMR_RES_RANGE_TO_SIM:
            from RdWr import CMrResRange

            #Pre-existing definition is better, but use SeqNum if doesn't exist
            thisSpcId = TP.spcId_operBase['StateName'].get(self.dut.currentState,self.dut.seqNum)

            if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
               local_prm = TP.get_MR_Resistance_321
               local_prm.update({'spc_id':thisSpcId, 'DblTablesToParse':'P321_BIAS_CAL2'})
               oMrRes = CMrResRange(local_prm, TP.resRangeLim)
            else:
               local_prm_186 = dict(TP.prm_186_MRRes_noSync)
               local_prm_186.update({'spc_id':thisSpcId, 'DblTablesToParse':'P186_BIAS_CAL2'})
               oMrRes = CMrResRange(local_prm_186, TP.T186_ResRangeLim)

            #All options are booleans. So, if present in params, execute
            optionsList = self.params.keys()

            #Call T186 to measure, then save to SIM file
            oMrRes.updateResRangeData(optionsList)

            #Easier to do both at once
            drivePass,failhead = oMrRes.printData_checkLimits(optionsList)

            if drivePass==0 and self.params.get('failForLimitCheck',False):
               ScrCmds.raiseException(14599 ,'Delta head resistance exceeded @ Head : %s' % str(failhead))

         else:
            oProc = CProcess()
            #Pre-existing definition is better, but use 10*SeqNum if doesn't exist
            thisSpcId = TP.spcId_operBase['StateName'].get(self.dut.currentState,10*self.dut.seqNum)

            #Periodic Reader Resistance measure, to look at trends over time
            if testSwitch.FE_0173493_347506_USE_TEST321 and testSwitch.extern.SFT_TEST_0321:
               oProc.St(TP.get_MR_Resistance_321,{'spc_id':thisSpcId})
            else:
               oProc.St(TP.prm_186_MRRes_noSync,{'spc_id':thisSpcId})


#-------------------------------------------------------------------------------------------------------

class CRdrWidthMeasure(CState):   # Orig class name is MT50_10().
   """
   MT50/10 Measurement
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProc = CProcess()
      try:  self.oProc.St(TP.prm_MT50_10_Measurement_269)
      except: pass
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)

      if testSwitch.FE_305538_P_MT50_MT10_SCREEN:
         from dbLogUtilities import DBLogCheck
         dblchk = DBLogCheck(self.dut)
         if ( dblchk.checkComboScreen(TP.T269_MT50_10_Screen_Spec) == FAIL ):
            if testSwitch.ENABLE_ON_THE_FLY_DOWNGRADE and self.downGradeOnFly(1, 14869):
               objMsg.printMsg('Failed for MT50/10 Screen, downgrade to %s as %s' % (self.dut.BG, self.dut.partNum))
            else:
               ScrCmds.raiseException(14869, 'Failed for MT50/10 Screen @ Head : %s' % str(dblchk.failHead))


class CNftDegradationCheck(CState):
   """
   MT50/10 Measurement
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProc = CProcess()
      prm = TP.prm_MT50_10_Measurement_269.copy()
      prm['CWORD1'] = prm['CWORD1'] | 0x80
      prm['OFFSET_SETTING'] = (-1000, 1000, 255)
      try:  self.oProc.St(prm)
      except: pass
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
#----------------------------------------------------------------------------------------------------------

class CEraseBand(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      from FSO import CFSO
      self.oFSO = CFSO()
            
      self.oFSO.getZoneTable()
      
      if 0: #testSwitch.FE_SGP_OPTIZAP_ADDED: #turn on the ZAP
         self.oFSO.St(TP.setZapOnPrm_011)
         self.oFSO.saveSAPtoFLASH()
      
      newPrm_270 = TP.prm_erase_band.copy()
      MaskList = self.oFSO.oUtility.convertListToZoneBankMasks(TP.erase_band_testing_zones)
      for bank,list in MaskList.iteritems():
         if list:
            newPrm_270['ZONE_MASK_EXT'], newPrm_270['ZONE_MASK'] = \
               self.oFSO.oUtility.convertListTo64BitMask(list)
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               newPrm_270['ZONE_MASK_BANK'] = bank
            try:
               self.oFSO.St( newPrm_270 )
            except:
               pass

      if 0: #testSwitch.FE_SGP_OPTIZAP_ADDED: #turn on the ZAP   
         self.oFSO.St(TP.zapPrm_175_zapOff)
#----------------------------------------------------------------------------------------------------------

class CMeasureHeater(CState):
   """
      Description: Class that will measure heater resisistance
      Base: NA
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
   
   #-------------------------------------------------------------------------------------------------------
   def run(self):
      self.oProc = CProcess()
      self.oProc.St(TP.spindownPrm_2)
      if testSwitch.FE_0146434_007955_P_T80_HD_CAL_ITEMS_TO_POP_BY_HD_TYPE:
         heaterResistancePrm_80_copy = TP.heaterResistancePrm_80.copy()
         if self.params.get('hdType') and self.params.get('T80ItemsToPop'):
            if self.dut.HGA_SUPPLIER == self.params['hdType']:
               for i in range(len(self.params['T80ItemsToPop'])):
                  heaterResistancePrm_80_copy.pop(self.params['T80ItemsToPop'][i])
         self.oProc.St(heaterResistancePrm_80_copy)
      else:
         self.oProc.St(TP.heaterResistancePrm_80)
                  

#----------------------------------------------------------------------------------------------------------
class CPreHeaterOpti(CState):
   """
      Class made for calling method that runs preheat optimization
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      self.dut = dut
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):
      if not testSwitch.RUN_PRE_HEAT_OPTI:
         return

      from FSO import CFSO
      self.oFSO = CFSO()
      
      trgPreheatclrindex = 0
      trgWRTclrindex = 1
      trgRDclrindex = 2
      trgMaintclr = 3
      hd_zone_calibration_list = [[{}] for hd in range(0, self.dut.imaxHead)]

      clearance_list = self.readafhclearance()
      ## display Heater dac
      self.oFSO.getAFHWorkingAdaptives()
      ## save original clearance before turning
      clearance_list_org = self.oFSO.oUtility.copy(clearance_list)

      ## initialize paramters and limit
      start_refsector = TP.prm_PREHEAT_ErrRate_250['base']['ELT_REF_SECTOR'][0]
      end_refersector = TP.prm_PREHEAT_ErrRate_250['base']['ELT_REF_SECTOR'][1]
      lowest_clr_limit = TP.prm_PREHEAT_ErrRate_250['lowest_clr_limit']
      pct_limit = TP.prm_PREHEAT_ErrRate_250['pct_limit']
      num_testtrack_perzone = TP.prm_PREHEAT_ErrRate_250['num_testtrack_perzone']

      objMsg.printMsg("start_refsector = %s, end_refersector %s, lowest_clr_limit = %s, pct_limit = %s" % (str(start_refsector),str(end_refersector),str(lowest_clr_limit),str(pct_limit)))

      ## turning preheat clr
      for iHead in range(0, self.dut.imaxHead):
          turningbyzone_flag = 1
          first_round_run = 1
          ### first round scan for optimizing per head
          test_head = (iHead<<8)|(iHead&0xff)
          zone_mask = 0
          zone_mask_ext = 0
          for zone in testZones:
             zone_mask |= (1<<zone)
          #zone_mask = self.oFSO.oUtility.ReturnTestCylWord(self.oFSO.oUtility.setZoneMask(range(self.dut.numZones)))
          zone_mask_ext = self.oFSO.oUtility.ReturnTestCylWord(zone_mask >> 32 & 0xFFFFFFFF)
          zone_mask = self.oFSO.oUtility.ReturnTestCylWord(zone_mask & 0xFFFFFFFF)

          ## Measure Bit Error 2 times at different location to avoid defect at first sector
          elt_bit_error_by_sector_list = [[{}]for i in range(0,num_testtrack_perzone)]
          zone_position = 0;
          for i in range(0,num_testtrack_perzone) :
              TP.prm_PREHEAT_ErrRate_250['base']['ZONE_POSITION'] = zone_position;
              elt_bit_error_by_sector_list[i] = self.measureerror( test_head, zone_mask, zone_mask_ext )
              ## move to next postion zone position
              zone_position = zone_position + 20

          while turningbyzone_flag == 1:
             lsb_bit_mask_scan = 0
             msb_bit_mask_scan = 0

             for iDataZone in elt_bit_error_by_sector_list[i][iHead][0].keys():
             ##for iDataZone in range(0,max_datazone + 1) :

                 if not first_round_run == 1:
                    if hd_zone_calibration_list[iHead][0][iDataZone] == 0:
                         continue
                 ref_error = 0
                 ## prepare list for store hd,zone flag that required decrease target preheat
                 datazone_kyes = hd_zone_calibration_list[iHead][0].keys()
                 if iDataZone not in datazone_kyes:
                     hd_zone_calibration_list[iHead][0].update({iDataZone:[]})

                 current_trgPreheatclr = clearance_list[iHead][0][iDataZone][trgPreheatclrindex]
                 for i in range(0,num_testtrack_perzone) :
                     try:
                         objMsg.printMsg("Position %s, Head[%s], DataZone[%s], current_trgPreheatclr = %s, first sector error = %s, reference error = %s " % (str(i),str(iHead),str(iDataZone),str(current_trgPreheatclr),str(elt_bit_error_by_sector_list[i][iHead][0][iDataZone][0]),str((elt_bit_error_by_sector_list[i][iHead][0][iDataZone][1]/0.9))))
                     except:
                         objMsg.printMsg("Position %s, Head[%s], DataZone[%s], has no data" % (str(i),str(iHead),str(iDataZone)))
                         pass

                 ## prepare for checking limit
                 turning_pct = 0
                 for i in range(0,num_testtrack_perzone) :
                     try:
                         if (elt_bit_error_by_sector_list[i][iHead][0][iDataZone][0] > (elt_bit_error_by_sector_list[i][iHead][0][iDataZone][1]/pct_limit)):
                            turning_pct = turning_pct+1
                     except:
                         pass

                 objMsg.printMsg("hd = %s, zone = %s number of turning_pct is %s" %(str(iHead),str(iDataZone),str(turning_pct)))
                 if (turning_pct > 2) and (current_trgPreheatclr > lowest_clr_limit) :
                     objMsg.printMsg("hd = %s, zone = %s need to decrease target preheat clr" %(str(iHead),str(iDataZone)))
                     flag = 1
                     lsb_bit_mask = 0x00FFFF & (1<<iDataZone)
                     msb_bit_mask = 0xFF0000 & (1<<iDataZone)
                     lsb_bit_mask_scan = (lsb_bit_mask_scan | lsb_bit_mask)
                     msb_bit_mask_scan = (msb_bit_mask_scan | msb_bit_mask)
                     clearance_list[iHead][0][iDataZone][trgPreheatclrindex] = clearance_list[iHead][0][iDataZone][trgPreheatclrindex] - 1
                     new_trgpreheat = clearance_list[iHead][0][iDataZone][trgPreheatclrindex]
                     tgtwrtheat = clearance_list[iHead][0][iDataZone][trgWRTclrindex]
                     tgtrdhead = clearance_list[iHead][0][iDataZone][trgRDclrindex]
                     self.setTargetClearance( iHead, iDataZone, new_trgpreheat, tgtwrtheat, tgtrdhead)
                 else:
                     flag = 0
                 hd_zone_calibration_list[iHead][0][iDataZone] = flag

             objMsg.printMsg("list of hd_zone_calibration_list %s" % (str(hd_zone_calibration_list)))
             objMsg.printMsg("lsb_bit_mask_scan = %s, msb_bit_mask_scan = %s " % (str(lsb_bit_mask_scan),str(msb_bit_mask_scan)))
             ## next round opti
             first_round_run = 0

             if lsb_bit_mask_scan == 0 and msb_bit_mask_scan == 0:
                ## no need to turn this head anymore
                turningbyzone_flag = 0
             else:
                test_head = (iHead<<8)|(iHead&0xff)
               ## zone_mask = (0xFF,0xFFFF)

                zone_position = 0;
                for i in range(0,num_testtrack_perzone) :
                    TP.prm_PREHEAT_ErrRate_250['base']['ZONE_POSITION'] = zone_position;
                    elt_bit_error_by_sector_list[i] = self.measureerror( test_head, zone_mask, zone_mask_ext )
                    ## move to next postion zone position
                    zone_position = zone_position + 20

      objMsg.printMsg("<<<<  Update New Clearance to drive  >>>>")
###      self.oFSO.St({'test_num':178, 'prm_name':[], 'CWORD1': 544}) ## comment out for now for eval, dont' want to update new trg preheat clr to drive
      objPwrCtrl.powerCycle(set5V=5000, set12V=12000, offTime=10, onTime=10, useESlip=1)
      objMsg.printMsg("<<<<  Final AFH table  >>>>")
      self.oFSO.getAFHTargetClearances()

      if testSwitch.virtualRun == 0:
         try:
            self.dut.dblData.delTable('P_PREHEAT_OPTI', forceDeleteDblTable = 1)
         except:
            objMsg.printMsg("Fail to delete P_PREHEAT_OPTI table")
            pass
      self.dut.objSeq.curRegSPCID = 3000

      for head in range(0, self.dut.imaxHead):
         for iDataZone in clearance_list_org[head][0].keys():
             self.dut.dblData.Tables('P_PREHEAT_OPTI').addRecord({
                 'SPC_ID'                    : self.dut.objSeq.curRegSPCID,
                 'OCCURRENCE'                : self.dut.objSeq.getOccurrence(),
                 'SEQ'                       : self.dut.objSeq.curSeq,
                 'TEST_SEQ_EVENT'            : self.dut.objSeq.getTestSeqEvent(0),
                 'HD_PHYS_PSN'               : int(head),  # hd
                 'DATA_ZONE'                 : int(iDataZone),
                 'PRE_HEAT_TRGT_CLRNC_ORG'   : int(clearance_list_org[head][0][iDataZone][trgPreheatclrindex]),  # hd
                 'PRE_HEAT_TRGT_CLRNC_NEW'   : int(clearance_list[head][0][iDataZone][trgPreheatclrindex]),
                 'DELTA_PRE_HEAT_TRGT_CLRNC' : (int(clearance_list_org[head][0][iDataZone][trgPreheatclrindex])-int(clearance_list[head][0][iDataZone][trgPreheatclrindex])),
                 })

      objMsg.printMsg("self.dut.objSeq.curRegSPCID %s"  %(str(self.dut.objSeq.curRegSPCID)))
      objMsg.printMsg("P_PREHEAT_OPTI %s"  %(str(self.dut.dblData.Tables('P_PREHEAT_OPTI'))))
      objMsg.printDblogBin(self.dut.dblData.Tables('P_PREHEAT_OPTI'),spcId32 = self.dut.objSeq.curRegSPCID)
      objMsg.printMsg("<<<<<<<<<<<<<<<<<<<<<<<<<                 End                     >>>>>>>>>>>>>>>>>>>>>>>>>>>>")

   #-------------------------------------------------------------------------------------------------------
   def measureerror (self, test_head, zone_mask, zone_mask_ext):
       
       elt_bit_error_list = [[{}] for hd in range(0, self.dut.imaxHead)]
       if testSwitch.virtualRun == 0:
          try:
             self.dut.dblData.delTable('P211_ELT_REF_SECTORS', forceDeleteDblTable = 1)
          except:
             objMsg.printMsg("Fail to delete table")
             pass

       SetFailSafe()
       TP.prm_PREHEAT_ErrRate_250['base']['TEST_HEAD'] = test_head
       TP.prm_PREHEAT_ErrRate_250['base']['ZONE_MASK'] = zone_mask
       TP.prm_PREHEAT_ErrRate_250['base']['ZONE_MASK_EXT'] = zone_mask_ext

       ## clean up track using 0xFF pattern
       TP.prm_PREHEAT_ErrRate_250['base']["CWORD2"] = 0x0001
       TP.prm_PREHEAT_ErrRate_250['base']['WR_DATA'] = 0xFF
       self.oFSO.St(TP.prm_PREHEAT_ErrRate_250['base'])#P211_ELT_ERROR

       ## start to scan and read error
       TP.prm_PREHEAT_ErrRate_250['base']["CWORD2"] = 0x0009
       TP.prm_PREHEAT_ErrRate_250['base']['WR_DATA'] = 0x00
       self.oFSO.St(TP.prm_PREHEAT_ErrRate_250['base'])#P211_ELT_ERROR
       ClearFailSafe()
       error_table = self.dut.dblData.Tables('P211_ELT_REF_SECTORS').chopDbLog(parseColumn = 'OCCURRENCE', matchStyle = 'max')
       objMsg.printMsg("error_table %s." % (str(error_table)))
       max_sector_per_track = 0
       for ii in xrange(len(error_table)):
          iHead = int(error_table[ii]['HD_PHYS_PSN'])
          iDataZone = int(error_table[ii]['DATA_ZONE'])
          iFirst_sector_err = float (error_table[ii]['FIRST_SECTOR_BIT_ERROR_CNT'])
          iREF_sector_input_err = float (error_table[ii]['AVG_BIT_ERROR_CNT_INPUT'])
          iREF_sector_5_15_err = float (error_table[ii]['AVG_BIT_ERROR_CNT_REF1'])
          iREF_sector_5_25_err = float (error_table[ii]['AVG_BIT_ERROR_CNT_REF2'])
          iREF_sector_5_end_err = float (error_table[ii]['AVG_BIT_ERROR_CNT_REF3'])

          datazone_keys = elt_bit_error_list[iHead][0].keys()
          if iDataZone not in datazone_keys:
             elt_bit_error_list[iHead][0].update({iDataZone:[]})

          elt_bit_error_list[iHead][0][iDataZone].append(iFirst_sector_err)
          elt_bit_error_list[iHead][0][iDataZone].append(iREF_sector_input_err)
          elt_bit_error_list[iHead][0][iDataZone].append(iREF_sector_5_15_err)
          elt_bit_error_list[iHead][0][iDataZone].append(iREF_sector_5_25_err)
          elt_bit_error_list[iHead][0][iDataZone].append(iREF_sector_5_end_err)

       objMsg.printMsg("elt_bit_error_list %s"  %(str(elt_bit_error_list)))
       return elt_bit_error_list

   #-------------------------------------------------------------------------------------------------------
   def readafhclearance (self):
       tableName = 'P172_AFH_DH_CLEARANCE'
       prheatCol = 'PRE_HEAT_TRGT_CLRNC'
       wtheatCol = 'WRT_HEAT_TRGT_CLRNC'
       rdheatCol = 'READ_HEAT_TRGT_CLRNC'

       self.oFSO.St({'test_num':172, 'spc_id': 1, 'prm_name':[], 'CWORD1': 5,'timeout': 100.0})
       afh_clearance_table = self.dut.dblData.Tables(tableName).chopDbLog('SPC_ID', 'match',str(1))
       clearance_list = [[{}] for hd in range(0, self.dut.imaxHead)] ## test [{}]
       hd_zone_calibration_list = [[{}] for hd in range(0, self.dut.imaxHead)]

       for i in xrange(len(afh_clearance_table)):
          iHead   = int(afh_clearance_table[i]['HD_PHYS_PSN'])
          iDataZone  = int(afh_clearance_table[i]['DATA_ZONE'])
          iPreheattargetclr = int(afh_clearance_table[i][prheatCol])
          iTargetWRTclr = int(afh_clearance_table[i][wtheatCol])
          iTargetRDclr = int(afh_clearance_table[i][rdheatCol])

          datazone_kyes = clearance_list[iHead][0].keys()
          if iDataZone not in datazone_kyes:
              clearance_list[iHead][0].update({iDataZone:[]})
          clearance_list[iHead][0][iDataZone].append(iPreheattargetclr)
          clearance_list[iHead][0][iDataZone].append(iTargetWRTclr)
          clearance_list[iHead][0][iDataZone].append(iTargetRDclr)
       return clearance_list

   #-------------------------------------------------------------------------------------------------------
   def setTargetClearance (self, head, DataZone, tgtmaintainheat, tgtwrtheat, tgtrdhead):
       head_range = 0
       lsb_bit_mask = 0
       msb_bit_mask = 0
       head_range = (1 << head)
       lsb_bit_mask = 0x000FFFF & (1<<DataZone)
       msb_bit_mask = 0xFFF0000 & (1<<DataZone)
       msb_bit_mask = (msb_bit_mask>>16)
       self.oFSO.St({'TGT_MAINTENANCE_CLR': (tgtmaintainheat,),'TGT_WRT_CLR': (tgtwrtheat,),'TGT_RD_CLR': (tgtrdhead,),'BIT_MASK': (msb_bit_mask, lsb_bit_mask),'test_num':178,'spc_id': 1,'prm_name':[], 'CWORD1': 0x2204,'CWORD2': 0x780,'HEAD_RANGE': head_range,'timeout': 600.0})
##       self.oFSO.St({'test_num':178, 'prm_name':[], 'CWORD1': 544})
   
   #-------------------------------------------------------------------------------------------------------
   def displayclrtable (self):
       self.oFSO.St({'test_num':172, 'prm_name':[], 'CWORD1': 5,'timeout': 100.0})
   
   #-------------------------------------------------------------------------------------------------------
   def displayworkingadpts ():
       self.oFSO.St({'test_num':172, 'prm_name':[], 'CWORD1': 5,'timeout': 100.0})

