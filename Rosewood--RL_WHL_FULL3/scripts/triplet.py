#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/27 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/triplet.py $
# $Revision: #13 $
# $DateTime: 2016/12/27 18:53:20 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/triplet.py#13 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from State import CState
import MessageHandler as objMsg
from Drive import objDut
from Process import CProcess

verbose = 0       # Set to a value greater than 0 for various levels of debug output in the log.


#----------------------------------------------------------------------------------------------------------
class CMultiMatrixTriplet(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.__dut = objDut
      self.BurnishFailedHeads = self.__dut.BurnishFailedHeads
      objMsg.printMsg("self.BurnishFailedHeads: %s" %(self.BurnishFailedHeads))

   #-------------------------------------------------------------------------------------------------------

   def run(self):
      from PreAmp import CPreAmp
      oProc = CProcess()

      oPreamp = CPreAmp()
      preamp_info = oPreamp.getPreAmpType()
      oPreamp = None  # Allow GC
      self.__dut.PREAMP_TYPE = preamp_info[0]
      if not testSwitch.FE_0334525_348429_INTERPOLATED_DEFAULT_TRIPLET:
         self.Def_Triplet = list(TP.VbarWpTable[self.__dut.PREAMP_TYPE]['ALL'][2])#(Iw, Ovs, Ovd)
      else:
         try:
            self.Def_Triplet = list(TP.VbarWpTable[self.__dut.PREAMP_TYPE]['ALL'][2])#(Iw, Ovs, Ovd)
         except:
            self.Def_Triplet = list(TP.VbarWpTable[self.__dut.PREAMP_TYPE]['OD'][2])#(Iw, Ovs, Ovd)

      # Special handling for burnished drives that have clearance reset in AFH2:
      if len(self.BurnishFailedHeads) != 0 and \
         (testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 or testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK):
         self.headRange = self.BurnishFailedHeads
      else:
         self.headRange = range(self.dut.imaxHead)

      testzonelist = TP.mmt_testzonelist
      iwlist = TP.mmt_iwlist
      iwstep = TP.mmt_iwstep

      self.headvendor = str(self.__dut.HGA_SUPPLIER)
      #objMsg.printMsg('headvendor %s' % str(self.headvendor))
      self.finalTripletTable={}
      for hd in self.headRange:
         self.finalTripletTable[hd] = {}
         for zn in testzonelist:
            self.finalTripletTable[hd][zn] = {}

      objMsg.printMsg("**********************************************")
      objMsg.printMsg("****** Multimatrix triplet control rules *****")
      objMsg.printMsg("**********************************************")
      objMsg.printMsg("Test head/s: %s" %(self.headRange))
      objMsg.printMsg("Test zones: %s" %(TP.mmt_testzonelist))
      if not TP.mmt_use_default_OSD: objMsg.printMsg("OSD tuning list: %s, while osa is fixed at %d" %(TP.mmt_osd_tuninglist, TP.mmt_fixed_osa))
      objMsg.printMsg("OSA tuning list: %s" %(TP.mmt_osa_tuninglist))
      objMsg.printMsg("IW tuning list: %s" %(TP.mmt_iwlist))
      objMsg.printMsg("T250 OSD/OSA knee point saturation criteria: %0.2f (stop when rate of change (ROC) > %0.2f)" %(TP.mmt_deltaBERStop, TP.mmt_deltaBERStop))
      objMsg.printMsg("T250 MAX_ERR_RATE=%d" % (TP.mmt_t250_max_err_rate))
      objMsg.printMsg("T250 OSD BER check for final pick=%d" % (TP.mmt_osdIwKPBERCheck))
      objMsg.printMsg("T51 start condition: DC=%d, n_writes=%d" %(TP.mmt_dc_start_value, TP.mmt_n_writes))
      objMsg.printMsg("T61 Optimizing Lower Bound IW: OW spec=%d(dB)" %(TP.mmt_ow_spec))
      objMsg.printMsg("T61 OW search stop criteria: %d consecutive delta < %d" %(TP.mmt_ow_search_size, TP.mmt_ow_deltaStop))
      objMsg.printMsg("**********************************************")

      oProc.St({'test_num' : 210, 'timeout': 600, 'CWORD1': 32})
      oProc.St({'test_num' : 210, 'prm_name' : 'prm_vbar_formats_210', 'timeout': 60, 'CWORD2': 1, 'CWORD1': 256, 'spc_id': 0})
      oProc.St({'test_num' : 275, 'prm_name' : 'zapPrm_275_zapOn', 'timeout': 1800, 'CWORD1': 131, 'ZAP_SPAN': 0})
      oProc.St({'test_num' : 172, 'prm_name' : 'display_AFH_working_adapts_172', 'timeout': 1800, 'CWORD1': 42})

      if testSwitch.virtualRun:
         return

      ################
      # Optimizing OSD:
      ################
      objMsg.printMsg("*********************************************")
      objMsg.printMsg("************** Optimizing OSD ***************")
      objMsg.printMsg("*********************************************")
      if TP.mmt_use_default_OSD:
         #Set to default Osd value.
         osdKneePointDict={}
         for hd in self.headRange:
            osdKneePointDict[hd]={}
            for zn in testzonelist:
               osdKneePointDict[hd][zn] = self.Def_Triplet[2] 
               objMsg.printMsg("Set Head %d Zone %d Osd to default value: %d" %(hd, zn, osdKneePointDict[hd][zn])) 
      else:
         # Find OSD Knee points. Each OSD has a BER saturation point, which is known as the knee point (KP).
         # 3 consecutive KPs determined the final OSD KP.
         osaDict = {}
         osdDict = {}
         for hd in self.headRange:
            osaDict[hd] = {}
            osdDict[hd] = {}
            for zn in testzonelist:
               osaDict[hd][zn] = TP.mmt_fixed_osa
               osdDict[hd][zn] = TP.mmt_osd_tuninglist
         tuningParam = 'OSD'
         osdKneePointDict = self.findingKneePoint (testzonelist, osaDict, osdDict, iwlist, tuningParam)
         objMsg.printMsg('osdKneePointDict= %s' % (osdKneePointDict))

      # Verifying OSD measurements:
      for hd in self.headRange:
         for zn in testzonelist:
            self.finalTripletTable[hd][zn]['OSD'] = osdKneePointDict[hd][zn]

      self.build_interpolated_curve_fitting('OSD')
      objMsg.printMsg('self.finalTripletTable OSD OSD_fitted = %s' % (self.finalTripletTable))
      # Re-format osdKneePointDict before feeding into OSA routine:
      for hd in self.headRange:
         for zn in testzonelist:
            osdKneePointDict[hd][zn] = self.finalTripletTable[hd][zn]['OSD_fitted']

      objMsg.printMsg('mmtdatadump_osd_found FINAL OSD TABLE')
      objMsg.printMsg('mmtdatadump_osd_found %s\t%s\t%s\t%s' % ('Hd',' Zn','Od','Od_fitted'))    
      for hd in self.headRange:
         for zn in testzonelist:
            objMsg.printMsg('mmtdatadump_osd_found %2d\t%3d\t%2d\t%9d' % (hd,zn,self.finalTripletTable[hd][zn]['OSD'],self.finalTripletTable[hd][zn]['OSD_fitted'])) 


      ################
      # Optimizing OSA:
      ################
      objMsg.printMsg("**************************************************************")
      objMsg.printMsg("*********************** Optimizing OSA ***********************")
      objMsg.printMsg("**************************************************************")
      #objMsg.printMsg("MMT rules when optimzing Osa:")
      #objMsg.printMsg("(1) 5x Osa values will be tested, eg 4,10,16,22,28.")
      #objMsg.printMsg("(2) Start with DC=0, n_writes=1000, Osa=4.")
      #objMsg.printMsg("(3) Min ATI < 4.7 or >=8.5 has no resolution in T51 Osa selection. Thus change in DC or n_writes is required to re-do T51 in order to find the best Osa.")
      #objMsg.printMsg("(4) If min ATI < 4.7, n_writes will be reduced in this order ie 3000, 1000, 500, 100.")
      #objMsg.printMsg("    For head degraded drives, min ATI will remain < 4.7 at DC=0 & n_writes=100. In such case, algo will proceed to test on the remaining 4x Osa.")
      #objMsg.printMsg("(5) If min ATI >= 8.5, DC will be increased by 21.")
      #objMsg.printMsg("    The max DC is capped at IwKP+DC = 127. ")
      #objMsg.printMsg("(6) Once T51 has a resolution (min ATI is 4.7<=ATI<8.5), proceed to test with the remaining 4x Osa values ie 4,10,22,28 using the DC and n_writes settings which Osa=16 is able to find a good T51 resolution.")
      #objMsg.printMsg("(7) The highest min ATI from the 5x Osa will be used to determine the final OSA found.")
      #objMsg.printMsg("(8) Special handling is required when there is more than 1x highest min ATI:")
      #objMsg.printMsg("    (a) When there are >2 highest min ATI, another loop of T51 with new DC and n_writes will be run on the top few Osa to find out which one is the best. eg Q93009CD H1 Z115.")
      #objMsg.printMsg("        If min ATI > 6.7, DC previously found in step (6) will be increased by 7.")
      #objMsg.printMsg("        The max DC is capped at IwKP+DC = 127. ")
      #objMsg.printMsg("        If min ATI <= 6.7, DC previously found in step (6) will be reduced by 7. ")
      #objMsg.printMsg("        If min ATI <= 6.7 & DC=0, n_writes will be reduced in this order ie 3000, 1000, 500, 100.")
      #objMsg.printMsg("    (b) When there are 2x highest min ATI, another loop of T51 with new DC and n_writes will be run to find out which of these 2x Osa is better. ")
      #objMsg.printMsg("        Take the average if both Osa show equal performance. ")
      #objMsg.printMsg("    (c) When there is 1x highest min ATI but 2x second highest min ATI, the Osa with the 1x highest min ATI will be the final selection.")
      #objMsg.printMsg("**************************************************************")
      # Find OSA Knee points. Each OSA has a BER saturation point, which is known as the knee point (KP).
      # 3 consecutive KPs determined the final OSA KP.
      osaDict = {}
      for hd in self.headRange:
         osaDict[hd] = {}
         for zn in testzonelist:
            osaDict[hd][zn] = TP.mmt_osa_tuninglist #range(4,30,6) #{0: {0: [4, 10, 16, 22, 28], 75: [4, 10, 16, 22, 28], 149: [4, 10, 16, 22, 28]}, 1: {0: [4, 10, 16, 22, 28], 75: [4, 10, 16, 22, 28], 149: [4, 10, 16, 22, 28]}}
      tuningParam = 'OSA'
      osdDict = osdKneePointDict 
      
      osaKneePointTable = self.findingKneePoint (testzonelist, osdDict, osaDict, iwlist, tuningParam)
      objMsg.printMsg('osaKneePointTable= %s' % (osaKneePointTable))
 

      # Verifying OSA measurements:
      for hd in osaKneePointTable:
         for zn in osaKneePointTable[hd]:
            for Osd in osaKneePointTable[hd][zn]:
               for Osa in osaKneePointTable[hd][zn][Osd]:
                  if osaKneePointTable[hd][zn][Osd][Osa]['IwKP'] == -1:
                     osaKneePointTable[hd][zn][Osd][Osa]['IwKP'] = -2 # Set to -2 to indicate bad measurement, optimize_osa_t51 routine will handle OSA accordingly.


      # While optimizing Osa, IwKP also defines Sova knee point:
      self.optimize_osa_t51 (testzonelist, osaKneePointTable, iwlist, 0) 

      # Interpolated and curve fit OSA. Feed curve fitted OSA to IW COG sweeping later.
      self.build_interpolated_curve_fitting('OSA')
      objMsg.printMsg('self.finalTripletTable OSD OSD_fitted OSA SOVA_IwKP OSA_fitted = %s' % (self.finalTripletTable))

      # Print table:  
      objMsg.printMsg('mmtdatadump_osa_found FINAL OSA TABLE')
      objMsg.printMsg('mmtdatadump_osa_found %s\t%s\t%s\t%s\t%s\t%s' % ('Hd',' Zn','Od_fitted','Oa','IwKP','Oa_fitted'))    
      for hd in self.headRange:
         for zn in testzonelist:
            objMsg.printMsg('mmtdatadump_osa_found %2d\t%3d\t%9d\t%2d\t%4d\t%9d' % (hd,zn,self.finalTripletTable[hd][zn]['OSD_fitted'],self.finalTripletTable[hd][zn]['OSA'],self.finalTripletTable[hd][zn]['SOVA_IwKP'],self.finalTripletTable[hd][zn]['OSA_fitted']))  


      

      ################
      # Optimizing IW:
      ################
      # power cycle otherwise T61 cannot run after T51.
      from PowerControl import objPwrCtrl
      objPwrCtrl.powerCycle(5000,12000,10,30)
      objPwrCtrl = None  # Allow GC

      objMsg.printMsg("*********************************************************")
      objMsg.printMsg("*************** Optimizing Lower Bound IW ***************")
      objMsg.printMsg("*********************************************************")
      self.runOwHms_LBIw(testzonelist, iwlist)
      #objMsg.printMsg('getOW_HMS_MMTtable1= %s' % (getOW_HMS_MMTtable))
      objMsg.printMsg('self.finalTripletTable OSD OSD_fitted OSA SOVA_IwKP OSA_fitted OW_IwKP = %s' % (self.finalTripletTable))

      #iwUBTable = self.findLBIw(testzonelist, iwlist, iwLBTable, getOW_HMS_MMTtable)
      #objMsg.printMsg('iwUBTable= %s' % (iwUBTable))

      # Set OWKP as IwLB:
      objMsg.printMsg('mmtdatadump_ow_hms_kp SOVA, OW & HMS IWKP TABLE')
      objMsg.printMsg('mmtdatadump_ow_hms_kp %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % ('Hd',' Zn','Od_fitted','Oa_fitted','SOVAIwKP','OWIwKP','HMSIwKP','IwLB'))
      for hd in self.headRange:
         for zn in testzonelist:
            # Verify OW_IwKP data:
            # If OW_IwKP is negative due to invalid measurement, set it to the lowest Iw value. 
            if self.finalTripletTable[hd][zn]['OW_IwKP'] < min(TP.mmt_iwlist):
               self.finalTripletTable[hd][zn]['OW_IwKP'] = min(TP.mmt_iwlist) 
            self.finalTripletTable[hd][zn]['IwLB'] = self.finalTripletTable[hd][zn]['OW_IwKP']
            objMsg.printMsg('mmtdatadump_ow_hms_kp %2d\t%3d\t%9d\t%9d\t%8d\t%6d\t%7d\t%4d' % (hd,zn,self.finalTripletTable[hd][zn]['OSD_fitted'],self.finalTripletTable[hd][zn]['OSA_fitted'],self.finalTripletTable[hd][zn]['SOVA_IwKP'],self.finalTripletTable[hd][zn]['OW_IwKP'],0,self.finalTripletTable[hd][zn]['IwLB']))

      objMsg.printMsg('self.finalTripletTable OSD OSD_fitted OSA SOVA_IwKP OSA_fitted OW_IwKP IwLB = %s' % (self.finalTripletTable))

      # power cycle otherwise T51 cannot run after T61:
      from PowerControl import objPwrCtrl
      objPwrCtrl.powerCycle(5000,12000,10,30)
      objPwrCtrl = None  # Allow GC

      objMsg.printMsg("*********************************************************")
      objMsg.printMsg("*************** Optimizing Upper Bound IW ***************")
      objMsg.printMsg("*********************************************************")
      
      self.finalIwUsingT51 (testzonelist)
      #objMsg.printMsg('finalIwTable= %s' % (finalIwTable))


      objMsg.printMsg("**************************************************************")
      objMsg.printMsg("***************  FINDING IW CENTER OF GRAVITY ****************")
      objMsg.printMsg("**************************************************************")

      # Before COG starts, interpolate OW_IwKP so that all zones will be a Iw min cap at OW_IwKP:
      #self.build_interpolated_curve_fitting('OW_IwKP')

      self.finalIwUsingCOG (testzonelist)
      #objMsg.printMsg('finalIwTable2= %s' % (finalIwTable))

      #objMsg.printMsg("**************************************************************")
      #objMsg.printMsg("******************** Evaluating sub zones ********************")
      #objMsg.printMsg("**************************************************************")
      # power cycle to refresh working heater:
      #from PowerControl import objPwrCtrl
      #objPwrCtrl.powerCycle(5000,12000,10,30)
      #objPwrCtrl = None  # Allow GC
      #objMsg.printMsg("subzonelist: %s" %(subzonelist))
      #objMsg.printMsg("Taking average for OSD, OSA and Upper bound Iw...")
      #for hd in self.headRange:
         #for subzn in subzonelist:
            #finalIwTable[hd][subzn]={}
            #if subzn == 35:
               #finalIwTable[hd][subzn]['Osa']=int(round((finalIwTable[hd][0]['Osa']+finalIwTable[hd][75]['Osa'])/2))
               #finalIwTable[hd][subzn]['Osd']=int(round((finalIwTable[hd][0]['Osd']+finalIwTable[hd][75]['Osd'])/2))
               #finalIwTable[hd][subzn]['IwUB']=int(round((finalIwTable[hd][0]['IwUB']+finalIwTable[hd][75]['IwUB'])/2))
            #else:
               #finalIwTable[hd][subzn]['Osa']=int(round((finalIwTable[hd][75]['Osa']+finalIwTable[hd][149]['Osa'])/2))
               #finalIwTable[hd][subzn]['Osd']=int(round((finalIwTable[hd][75]['Osd']+finalIwTable[hd][149]['Osd'])/2))
               #finalIwTable[hd][subzn]['IwUB']=int(round((finalIwTable[hd][75]['IwUB']+finalIwTable[hd][149]['IwUB'])/2))

      #objMsg.printMsg('finalIwTable_addedsubzns= %s' % (finalIwTable))
      #allzonelist = subzonelist + testzonelist
      #allzonelist.sort()
      #objMsg.printMsg('mmtdatadump_subzones_osa_osd %s\t%s\t%s\t%s\t%s' % ('Hd','Zn','Od','Oa','IwUB'))
      #for hd in self.headRange:
         #for zn in allzonelist:
            #objMsg.printMsg('mmtdatadump_subzones_osa_osd %2d\t%2d\t%2d\t%2d\t%2d' % (hd,zn,finalIwTable[hd][zn]['Osd'],finalIwTable[hd][zn]['Osa'],finalIwTable[hd][zn]['IwUB']))

      #objMsg.printMsg("*************************************************************************")
      #objMsg.printMsg("********** Finding sub zones SOVA Knee points (Lower bound Iw) **********")
      #objMsg.printMsg("*************************************************************************")

      #tuningParam = 'SOVAKNEEPT'
      #osaDict = {}
      #for hd in self.headRange:
         #osaDict[hd] = {}
         #for zn in subzonelist:
            #osaDict[hd][zn] = finalIwTable[hd][zn]['Osa']
      #objMsg.printMsg("osaDict: %s" %(osaDict))
      #osdDict = {}
      #for hd in self.headRange:
         #osdDict[hd] = {}
         #for zn in subzonelist:
            #osdDict[hd][zn] = []
            #osdDict[hd][zn].append(finalIwTable[hd][zn]['Osd'])
      #objMsg.printMsg("osdDict: %s" %(osdDict))


      #osdKneePointDict_sz = self.findingKneePoint (subzonelist, osaDict, osdDict, iwlist, tuningParam)
      #objMsg.printMsg("osdKneePointDict_sz= %s" %(osdKneePointDict_sz))

      #for hd in self.headRange:
         #for zn in subzonelist:
            #for Osa in osdKneePointDict_sz[hd][zn]:
               #for Osd in osdKneePointDict_sz[hd][zn][Osa]:
                  #finalIwTable[hd][zn]['IwKP']=osdKneePointDict_sz[hd][zn][Osa][Osd]['IwKP']
                  #finalIwTable[hd][zn]['FINAL_IW']=osdKneePointDict_sz[hd][zn][Osa][Osd]['IwKP']+iwstep
      #objMsg.printMsg('finalIwTable_addedsubznsIwLB= %s' % (finalIwTable))

      # Print Sova KP, OW KP and HMS KP and the highest KP of them all:
      objMsg.printMsg('mmtdatadump_final2 FINAL TRIPLET TABLE')
      objMsg.printMsg('mmtdatadump_final2 %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % ('Hd',' Zn','Od_fitted','Oa_fitted','SOVAIwKP','OWIwKP','HMSIwKP','FINAL_IW','FINAL_IW_I','FINAL_IW_fitted','FINAL_OSD','FINAL_OSD_I','FINAL_OSD_fitted'))
      for hd in self.headRange:
         for zn in testzonelist:
            objMsg.printMsg('mmtdatadump_final2 %2d\t%3d\t%9d\t%9d\t%8d\t%6d\t%7d\t%8d\t%10d\t%15d\t%9d\t%11d\t%16d' % (hd,zn,self.finalTripletTable[hd][zn]['OSD_fitted'],self.finalTripletTable[hd][zn]['OSA_fitted'],self.finalTripletTable[hd][zn]['SOVA_IwKP'],self.finalTripletTable[hd][zn]['OW_IwKP'],0,self.finalTripletTable[hd][zn]['FINAL_IW'],self.finalTripletTable[hd][zn]['FINAL_IW_I'],self.finalTripletTable[hd][zn]['FINAL_IW_fitted'],self.finalTripletTable[hd][zn]['FINAL_OSD'],self.finalTripletTable[hd][zn]['FINAL_OSD_I'],self.finalTripletTable[hd][zn]['FINAL_OSD_fitted']))


      for table in ['MMT_SUMMARY']:
         try:
            self.dut.dblData.Tables(table).deleteIndexRecords(1)
            self.dut.dblData.delTable(table, forceDeleteDblTable = 1)
         except: pass
      seq, occurrence, testSeqEvent = self.dut.objSeq.registerCurrentTest(0)
      for hd in self.headRange:
         for zn in testzonelist:
             if 'OW_IwKP' in self.finalTripletTable[hd][zn].keys():
                HMSIwKP = self.finalTripletTable[hd][zn]['OW_IwKP']
             else:
                HMSIwKP = 0
             if (self.finalTripletTable[hd][zn]['IwLB'] == self.finalTripletTable[hd][zn]['IwUB']):
               COG_sweep = str(self.finalTripletTable[hd][zn]['IwLB']-7)+"-"+str(self.finalTripletTable[hd][zn]['IwLB']+7) # Must have min 3 points when sweeping COG. 
             else:
               COG_sweep = str(self.finalTripletTable[hd][zn]['IwLB'])+"-"+str(self.finalTripletTable[hd][zn]['IwUB'])
             self.dut.dblData.Tables('MMT_SUMMARY').addRecord({
                'SPC_ID'             : 1,
                'OCCURRENCE'         : occurrence,
                'SEQ'                : seq,
                'TEST_SEQ_EVENT'     : testSeqEvent,
                'HD_LGC_PSN'         : hd,
                'DATA_ZONE'          : zn,
                'SOVAIWKP'           : self.finalTripletTable[hd][zn]['SOVA_IwKP'],
                'OWIWKP'             : self.finalTripletTable[hd][zn]['OW_IwKP'],
                'OW'                 : self.finalTripletTable[hd][zn]['OW'],
                'HMSIWKP'            : 0,
                'IWLB'               : self.finalTripletTable[hd][zn]['IwLB'],
                'IWUB'               : self.finalTripletTable[hd][zn]['IwUB'],
                'COG_SWEEP'          : COG_sweep,
                'OSD'                : self.finalTripletTable[hd][zn]['FINAL_OSD_fitted'],
                'OSA'                : self.finalTripletTable[hd][zn]['OSA_fitted'],
                'IW'                 : self.finalTripletTable[hd][zn]['FINAL_IW_fitted'],
                })
      objMsg.printDblogBin(self.dut.dblData.Tables('MMT_SUMMARY'))

      objMsg.printMsg("*************************************************************************")
      objMsg.printMsg("**************** Display measured & interpolated values *****************")
      objMsg.printMsg("*************************************************************************")
      

      objMsg.printMsg('mmtdatadump_mmt %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % ('Hd',' Zn','Od_fitted','Oa','SOVAIwKP','OSA_I','OSA_fitted','OW_IwKP','IwLB','IwUB','FINAL_IW','FINAL_IW_I','FINAL_IW_fitted','FINAL_OSD','FINAL_OSD_I','FINAL_OSD_fitted'))
      for hd in self.headRange:
         for zn in range(self.dut.numZones):
            if 'OSD' in self.finalTripletTable[hd][zn].keys():
               Osd = self.finalTripletTable[hd][zn]['OSD_fitted']
               Osa = self.finalTripletTable[hd][zn]['OSA']
               SovaIwKP = self.finalTripletTable[hd][zn]['SOVA_IwKP']
               OWIwKP = self.finalTripletTable[hd][zn]['OW_IwKP']
               IwLB = self.finalTripletTable[hd][zn]['IwLB']
               IwUB = self.finalTripletTable[hd][zn]['IwUB']
               final_iw = self.finalTripletTable[hd][zn]['FINAL_IW']
               final_osd = self.finalTripletTable[hd][zn]['FINAL_OSD']
            else:
               Osd = 0
               Osa = 0
               SovaIwKP = 0
               OWIwKP = 0
               IwLB = 0
               IwUB = 0
               final_iw = 0
               final_osd = 0
            objMsg.printMsg('mmtdatadump_mmt %2d\t%3d\t%9d\t%2d\t%8d\t%5d\t%10d\t%7d\t%4d\t%4d\t%8d\t%10d\t%15d\t%9d\t%11d\t%16d' % (hd,zn,Osd,Osa,SovaIwKP,\
               self.finalTripletTable[hd][zn]['OSA_I'],self.finalTripletTable[hd][zn]['OSA_fitted'],OWIwKP,IwLB,IwUB,final_iw,\
               self.finalTripletTable[hd][zn]['FINAL_IW_I'],self.finalTripletTable[hd][zn]['FINAL_IW_fitted'],final_osd,self.finalTripletTable[hd][zn]['FINAL_OSD_I'],self.finalTripletTable[hd][zn]['FINAL_OSD_fitted']))

      #param178_setWP = {'test_num' : 178, 'prm_name' : 'Set WP', 'spc_id': 0, 'CWORD1': 544, 'timeout': 1200, 'WRITE_CURRENT_OFFSET': (0, 0), 'CWORD2': 4359}
      #for hd in self.headRange:
         #for zn in range(self.dut.numZones):
            #param178_setWP.update({'spc_id': 8000, 'HEAD_RANGE': ( 1 << hd ), 'ZONE': zn, 'DURATION': self.tempFinalTripletPick[hd][zn][2], 'DAMPING': self.tempFinalTripletPick[hd][zn][1], 'WRITE_CURRENT': self.tempFinalTripletPick[hd][zn][0]})
            #oProc.St(param178_setWP)

      # Set Triplet to the RAP
      prm_178 = {'test_num': 178, 'prm_name': 'prm_wp_178', 'timeout': 1200, 'spc_id': 0,}

      for hd in self.headRange:
         saveData = {} #init empty dict
         hd_mask = 0x3FF & (1<<hd) # write to one head at a time
         for zn in range(self.dut.numZones):
            triplet = (self.finalTripletTable[hd][zn]['FINAL_IW_fitted'], self.finalTripletTable[hd][zn]['OSA_fitted'], \
               self.finalTripletTable[hd][zn]['FINAL_OSD_fitted']) #'WRITE_CURRENT':triplet[0], 'DAMPING':triplet[1], 'DURATION':triplet[2]
            if not triplet in saveData: #init
               saveData[triplet] = []
               saveData[triplet].append(zn)
            else:
               saveData[triplet].append(zn)
            if (zn == self.dut.numZones/2): #system zone follows the middle zone. Need not be a precise triplet setting since it's an interpolated value.
               saveData[triplet].append(self.dut.numZones)
         objMsg.printMsg("saveData= %s" %saveData)
         for triplet in saveData:
            if testSwitch.FE_0245014_470992_ZONE_MASK_BANK_SUPPORT:
               #bit mask & bit mask ext param is no longer supported
               if testSwitch.extern.FE_0270095_504159_SUPPORT_LOOPING_ZONE_T178:
                  for startZn, endZn in \
                     oProc.oUtility.convertZoneListToZoneRange(saveData[triplet]):
                     prm_178['ZONE'] = (startZn << 8) + endZn
                     prm_178['prm_name'] = 'prm_wp_178_0x%04x_%s_%s_%s' % (prm_178['ZONE'], triplet[0], triplet[1], triplet[2])
                     self.setTriplet(prm_178, triplet, hd_mask)
               else:
                  for zn in saveData[triplet]:
                     prm_178['ZONE'] = zn
                     self.setTriplet(prm_178, triplet, hd_mask)
            else:
               prm_178['BIT_MASK_EXT'], prm_178['BIT_MASK'] = oProc.oUtility.convertListTo64BitMask(saveData[triplet])
               self.setTriplet(prm_178, triplet, hd_mask)

      oProc.St({'test_num':178, 'prm_name':'Save RAP in RAM to FLASH', 'CWORD1':0x220})

      # power cycle to refresh working heater:
      from PowerControl import objPwrCtrl
      objPwrCtrl.powerCycle(5000,12000,10,30)
      objPwrCtrl = None  # Allow GC

      oProc.St({'test_num' : 172, 'prm_name' : 'Retrieve WPs', 'timeout': 100, 'spc_id': 8000, 'CWORD1': 4})
      

   def build_interpolated_curve_fitting(self, meas_key):
      objMsg.printMsg("*************************************************************************")
      objMsg.printMsg("********************* Build %s interpolated values *********************", str(meas_key))
      objMsg.printMsg("*************************************************************************")

      #Build INterpolated Values
      inter_key = meas_key+'_I'             # 'FINAL_IW' will become 'FINAL_IW_I'
      curve_fitted_key = meas_key+'_fitted' # 'FINAL_IW' will become 'FINAL_IW_fitted'


      for hd in self.headRange:
         nX1 = 99
         for nZone in range(self.dut.numZones):
            if self.finalTripletTable[hd].has_key(nZone):
               if self.finalTripletTable[hd][nZone].has_key(meas_key):
                  #objMsg.printMsg("nZone %d" %nZone)
                  if nX1 == 99:
                     nY1Iw = self.finalTripletTable[hd][nZone][meas_key] #self.FinalTripletPick[hd][nZone][0]
                     nX1 = nZone
                  else:
                     nY2Iw = self.finalTripletTable[hd][nZone][meas_key] #self.FinalTripletPick[hd][nZone][0]
                     nX2 = nZone
                     nStepIw = float(float(nY2Iw - nY1Iw) / float(nX2 - nX1))
                     #objMsg.printMsg("nStepIw %0.4f" %nStepIw)
                     for yZone in range(nX1,nX2+1):
                        if not self.finalTripletTable[hd].has_key(yZone):
                           self.finalTripletTable[hd][yZone] = {}
                        self.finalTripletTable[hd][yZone][inter_key] = int(round(nY1Iw + float(nStepIw * (yZone - nX1)),0))
                        #objMsg.printMsg("Hd %d,  Zn %d,  nX1 %d,  nX2 %d,  nY1Iw %d,  nY2Iw %d,  Iw %d,  Oa %d,  Od %d" % (hd, yZone, nX1, nX2, nY1Iw ,nY2Iw , self.tempFinalTripletPick[hd][yZone][0],self.tempFinalTripletPick[hd][yZone][1],self.tempFinalTripletPick[hd][yZone][2]))
                     nX1 = nX2
                     nY1Iw = nY2Iw



      objMsg.printMsg("finalTripletTable 518= %s" %self.finalTripletTable)

      #header_str = 'mmtdatadump_'+str(meas_key)+'_interpolate'
      #objMsg.printMsg('%s %s\t%s\t%s\t%s' % (header_str,'Hd','Zn','M','I'))
      #for hd in self.headRange:
         #for zn in range(self.dut.numZones):
            #if self.finalTripletTable[hd][zn].has_key(meas_key):
               #objMsg.printMsg('%s %2d\t%2d\t%2d\t%2d' % (header_str,hd,zn,self.finalTripletTable[hd][zn][meas_key],self.finalTripletTable[hd][zn][inter_key]))
            #else:
               #objMsg.printMsg('%s %2d\t%2d\t%2d\t%2d' % (header_str,hd,zn,0,self.finalTripletTable[hd][zn][inter_key]))

      # Apply Quad Median Poly Fit
      for hd in self.headRange:
         #for index in range(3):
         #objMsg.printMsg("index= %s" %index)
         
         if meas_key == 'FINAL_IW':
            mincap = 127
            maxcap = 0
         else: #if meas_key == 'OSA' or meas_key == 'OSD' or meas_key == 'FINAL_OSD':
            mincap = 32
            maxcap = 0 

         for zn in TP.mmt_testzonelist:
            if self.finalTripletTable[hd][zn][meas_key] > maxcap:
               maxcap = self.finalTripletTable[hd][zn][meas_key]
            if self.finalTripletTable[hd][zn][meas_key] < mincap:
               mincap = self.finalTripletTable[hd][zn][meas_key]
         header_str = 'mmtdatadump_'+str(meas_key)+'_curve'
         objMsg.printMsg('%s h%d min cap is %d. max cap is %d' % (header_str,hd,mincap,maxcap))
         
         dataList = []
         for zn in range(self.dut.numZones):
            dataList.append(self.finalTripletTable[hd][zn][inter_key])
         objMsg.printMsg("H%d dataList= %s" % (hd,str(dataList)))
         filteredList = self.quadraticMedianfilter(dataList)
         objMsg.printMsg("H%d filteredList= %s" % (hd,str(filteredList)))
         for zn in range(self.dut.numZones):
            self.finalTripletTable[hd][zn][curve_fitted_key] = int(round(filteredList[zn],0))
            # Set min & max cap here:
            self.finalTripletTable[hd][zn][curve_fitted_key] = max(self.finalTripletTable[hd][zn][curve_fitted_key], mincap)
            self.finalTripletTable[hd][zn][curve_fitted_key] = min(self.finalTripletTable[hd][zn][curve_fitted_key], maxcap)

       

      header_str = 'mmtdatadump_'+str(meas_key)+'_curve'
      objMsg.printMsg('%s %s\t%s\t%s\t%s\t%s' % (header_str,'Hd',' Zn','  M','  I','CurveFitted'))
      for hd in self.headRange:
         for zn in TP.mmt_testzonelist:
            if self.finalTripletTable[hd][zn].has_key(meas_key):
               objMsg.printMsg('%s %2d\t%3d\t%3d\t%3d\t%11d' % (header_str,hd,zn,self.finalTripletTable[hd][zn][meas_key],self.finalTripletTable[hd][zn][inter_key],self.finalTripletTable[hd][zn][curve_fitted_key]))
            else:
               objMsg.printMsg('%s %2d\t%3d\t%3d\t%3d\t%11d' % (header_str,hd,zn,0,self.finalTripletTable[hd][zn][inter_key],self.finalTripletTable[hd][zn][curve_fitted_key]))



   def setTriplet(self, prm_178, triplet, hd_mask):
      oProc = CProcess()
      cword1 = 0x0200  # update RAM copy
      prm_178.update({'CWORD1':cword1, 'CWORD2':0x1107, 'HEAD_RANGE':hd_mask,\
         'WRITE_CURRENT':triplet[0], 'DAMPING':triplet[1], 'DURATION':triplet[2]})
      if testSwitch.FE_0308170_403980_P_SHORTEN_MMT_LOGS:
         prm_178['stSuppressResults'] = ST_SUPPRESS__ALL
         objMsg.printMsg("prm_178= %s" %prm_178)

      oProc.St(prm_178)

   def quadraticMedianfilter(self, dataList):

      finalList = []
      finalList.extend(dataList)
      filterList = []
      filterList.extend(dataList)
      objMsg.printMsg('finalList1:%s' % finalList)
      #first do 5 point median filter
      for index in range(len(dataList)):
         temparray=[]
         if index == 0:
            filterList[index] = dataList[index]
         elif index == 1:
            temparray.append(dataList[0])
            for index2 in range (1,5):
               temparray.append(dataList[index2])
            temparray.sort()
            filterList[index]=float(temparray[2])
         elif index == (len(dataList) -2):
            for index2 in range(0,4):
               temparray.append(dataList[len(dataList)-index2-2])
            temparray.append(dataList[len(dataList)-1])
            temparray.sort()
            filterList[index]=float(temparray[2])
         elif index == (len(dataList) -1):
            filterList[index] = dataList[index]
         else:
            for index2 in range(0,5):
               temparray.append(dataList[index + index2 - 2])
            temparray.sort()
            filterList[index]=float(temparray[2])
         #now make quadratic equation of filtered values
         N=0
         s1=0
         s2=0
         s3=0
         s4=0
         t1=0
         t2=0
         t3=0
      objMsg.printMsg('filterList2:%s' % filterList)
      for index in range(len(dataList)):
         N=N+1
         s1=s1+index
         s2=s2+index*index
         s3=s3+index*index*index
         s4=s4+index*index*index*index
         t1=t1+float(filterList[index])
         t2=t2+index*float(filterList[index])
         t3=t3+index*index*float(filterList[index])
      d=N*s2*s4 - N*s3*s3 - s1*s1*s4 - s2*s2*s2 + 2*s1*s2*s3
      A=(N*s2*t3 - N*s3*t2 - s1*s1*t3 - s2*s2*t1 + s1*s2*t2 + s1*s3*t1)/d
      B=(N*s4*t2 - N*s3*t3 - s2*s2*t2 - s1*s4*t1 + s1*s2*t3 + s2*s3*t1)/d
      C=(s1*s3*t3 -s1*s4*t2 -s2*s2*t3 - s3*s3*t1 + s2*s3*t2 + s2*s4*t1)/d
      #apply equation to all values
      for index in range(len(dataList)):
         finalList[index]=A*index*index+B*index+C
      objMsg.printMsg('finalList2:%s' % finalList)
      return finalList


   def findLBIw(self, testzonelist, iwlist, iwUBTable, getOW_HMS_MMTtable): 
      oProc = CProcess()

      iwlist.sort() 
      iwlist.reverse()
      #objMsg.printMsg("iwlist sorted in reverse: %s" %(iwlist))
      #objMsg.printMsg('getOW_HMS_MMTtable0= %s' % (getOW_HMS_MMTtable))
      iwstep = TP.mmt_iwstep

      objMsg.printMsg('mmtdatadump_ow_hms_raw OW & HMS DATA TABLE')
      objMsg.printMsg('mmtdatadump_ow_hms_raw %s\t%s\t%s\t%s\t %s\t %s\t %s\t' % ('Hd','Zn','Od','Oa','Iw','OW','HMS'))
      for hd in self.headRange:
         for zn in testzonelist:
            Osa = iwUBTable[hd][zn]['Osa']
            Osd = iwUBTable[hd][zn]['Osd']
            for Iw in iwlist:
			   if getOW_HMS_MMTtable[hd][zn][Iw]['OW']:
				  OW = getOW_HMS_MMTtable[hd][zn][Iw]['OW']
				  HMS = getOW_HMS_MMTtable[hd][zn][Iw]['HMS']
			   else:
				  OW = -1
				  HMS = -1
			   objMsg.printMsg('mmtdatadump_ow_hms_raw %2d\t%2d\t%2d\t%2d\t%2d\t%0.4f\t%0.4f\t' % (hd,zn,Osd,Osa,Iw,OW,HMS)) 

      for hd in self.headRange:
         for zn in testzonelist:
            OWiwList = []
            OWdataList = []
            HMSiwList = []
            HMSdataList = []
            Osa = iwUBTable[hd][zn]['Osa']
            Osd = iwUBTable[hd][zn]['Osd']
            for Iw in iwlist:
               if 'OW' in getOW_HMS_MMTtable[hd][zn][Iw].keys() and (not getOW_HMS_MMTtable[hd][zn][Iw]['OW'] <= 0):

                  OW = getOW_HMS_MMTtable[hd][zn][Iw]['OW']
                  OWiwList.append(Iw)
                  OWdataList.append(OW)
               else:
                  OW = -1
               if 'HMS' in getOW_HMS_MMTtable[hd][zn][Iw].keys() and (not getOW_HMS_MMTtable[hd][zn][Iw]['HMS'] <= 0):
                   
                  HMS = getOW_HMS_MMTtable[hd][zn][Iw]['HMS']
                  HMSiwList.append(Iw)
                  HMSdataList.append(HMS)
               else:
                  HMS = -1
               #iwList_2ndOderFit.append(Iw) 
               #OWdataList.append(OW) 
               #HMSdataList.append(HMS) 
            objMsg.printMsg("OWiwList: %s" %(OWiwList))
            objMsg.printMsg("OWdataList: %s" %(OWdataList))
            newFittedDataList = self.lumpData_by_2ndOrderFit(OWiwList, OWdataList)
            objMsg.printMsg('newFittedDataList= %s' % (newFittedDataList))
            for item in range(len(newFittedDataList)):
               iIw = OWiwList[item]
               getOW_HMS_MMTtable[hd][zn][iIw]['FittedOW'] = newFittedDataList[item]

            #objMsg.printMsg("HMSiwList: %s" %(HMSiwList))
            #objMsg.printMsg("HMSdataList: %s" %(HMSdataList))
            
            #newFittedDataList2 = self.lumpData_by_2ndOrderFit(HMSiwList, HMSdataList)
            #objMsg.printMsg('newFittedDataList2= %s' % (newFittedDataList2))
            #for Iw in iwlist:
            #for item in range(len(newFittedDataList2)):
               #iIw = HMSiwList[item]
               #getOW_HMS_MMTtable[hd][zn][iIw]['FittedHMS'] = newFittedDataList2[item]

      objMsg.printMsg("getOW_HMS_MMTtable: %s" %(getOW_HMS_MMTtable))
      DeltaFittedOW = -1
      DeltaFittedHMS = -1
      objMsg.printMsg('mmtdatadump_ow_hms_fitted OW & HMS 2ND ORDER FITTED DATA TABLE')
      objMsg.printMsg('mmtdatadump_ow_hms_fitted %s\t%s\t%s\t%s\t %s\t %s\t %s\t %s\t %s\t %s\t %s' % ('Hd','Zn','Od','Oa','Iw','OW','HMS','FittedOW','FittedHMS','DeltaFittedOW','DeltaFittedHMS'))
      for hd in self.headRange:
         for zn in testzonelist:
            Osa = iwUBTable[hd][zn]['Osa']
            Osd = iwUBTable[hd][zn]['Osd']
            for Iw in iwlist:
               if 'OW' in getOW_HMS_MMTtable[hd][zn][Iw].keys():
               
                  OW = getOW_HMS_MMTtable[hd][zn][Iw]['OW']
                  HMS = getOW_HMS_MMTtable[hd][zn][Iw]['HMS']
               else:
                  OW = -1
                  HMS = -1
               if 'FittedOW' in getOW_HMS_MMTtable[hd][zn][Iw].keys():
                  FittedOW = getOW_HMS_MMTtable[hd][zn][Iw]['FittedOW']
                  if not Iw == iwlist[0]:
                     if 'FittedOW' in getOW_HMS_MMTtable[hd][zn][Iw+iwstep].keys():
                        DeltaFittedOW = getOW_HMS_MMTtable[hd][zn][Iw+iwstep]['FittedOW'] - getOW_HMS_MMTtable[hd][zn][Iw]['FittedOW']
                     else: 
                        DeltaFittedOW = -1
               else:
                  FittedOW = -1
                  DeltaFittedOW = -1
               if 'FittedHMS' in getOW_HMS_MMTtable[hd][zn][Iw].keys():
                  FittedHMS = getOW_HMS_MMTtable[hd][zn][Iw]['FittedHMS']
                  if not Iw == iwlist[0]:
                     if 'FittedHMS' in getOW_HMS_MMTtable[hd][zn][Iw+iwstep].keys():
                        DeltaFittedHMS = getOW_HMS_MMTtable[hd][zn][Iw+iwstep]['FittedHMS'] - getOW_HMS_MMTtable[hd][zn][Iw]['FittedHMS']
                     else: 
                        DeltaFittedHMS = -1
               else:
                  FittedHMS = -1  
                  DeltaFittedHMS = -1  
               objMsg.printMsg('mmtdatadump_ow_hms_fitted %2d\t%2d\t%2d\t%2d\t%2d\t%0.4f\t%0.4f\t%0.4f\t%0.4f\t%0.4f\t%0.4f' % (hd,zn,Osd,Osa,Iw,OW,HMS,FittedOW,FittedHMS,DeltaFittedOW,DeltaFittedHMS)) 

      owKP = 999
      for hd in self.headRange:
         for zn in testzonelist:
            owKP = 999
            Osa = iwUBTable[hd][zn]['Osa']
            Osd = iwUBTable[hd][zn]['Osd']
            for Iw in iwlist:
			   if (Iw+iwstep) <= max(iwlist):
			      #objMsg.printMsg("Hd %d Zn %d Iw: %d" %(hd, zn, Iw))
			      if 'FittedOW' in getOW_HMS_MMTtable[hd][zn][Iw].keys() and 'FittedOW' in getOW_HMS_MMTtable[hd][zn][Iw+iwstep].keys():
			         FittedOW = getOW_HMS_MMTtable[hd][zn][Iw]['FittedOW']
			         prevFittedOW = getOW_HMS_MMTtable[hd][zn][Iw+iwstep]['FittedOW']
			         #objMsg.printMsg("FittedOW: %0.4f" %(FittedOW))
			         #objMsg.printMsg("prevFittedOW: %0.4f" %(prevFittedOW))
			         deltaFittedOW = prevFittedOW - FittedOW
			         #objMsg.printMsg("deltaFittedOW: %0.4f" %(deltaFittedOW))
			         #objMsg.printMsg("current owKP: %d" %(owKP))
			         if deltaFittedOW > 3:
			            owKP = Iw+iwstep
			            #objMsg.printMsg("Hd %d Zn %d owKP: %d <------------------------" %(hd, zn, owKP))
			            iwUBTable[hd][zn]['OWIwKP'] = owKP
			            break
            if owKP == 999:
               objMsg.printMsg("Cannot find OW knee point! Default to Sova IwKP, iwUBTable[%d][%d]['IwKP']=%d !" %(hd, zn, iwUBTable[hd][zn]['IwKP']))
               iwUBTable[hd][zn]['OWIwKP'] = iwUBTable[hd][zn]['IwKP']
               #objMsg.printMsg("iwUBTable[%d][%d]['OWIwKP']: %d <<<------------------------" %(hd, zn, iwUBTable[hd][zn]['OWIwKP']))
               continue

      hmsKP = 999
      for hd in self.headRange:
         for zn in testzonelist:
            hmsKP = 999
            Osa = iwUBTable[hd][zn]['Osa']
            Osd = iwUBTable[hd][zn]['Osd']
            for Iw in iwlist:
			   if (Iw+iwstep) <= max(iwlist):
			      #objMsg.printMsg("Hd %d Zn %d Iw: %d" %(hd, zn, Iw))
			      if 'FittedHMS' in getOW_HMS_MMTtable[hd][zn][Iw].keys() and 'FittedHMS' in getOW_HMS_MMTtable[hd][zn][Iw+iwstep].keys():
			         FittedHMS = getOW_HMS_MMTtable[hd][zn][Iw]['FittedHMS']
			         prevFittedHMS = getOW_HMS_MMTtable[hd][zn][Iw+iwstep]['FittedHMS']
			         #objMsg.printMsg("FittedHMS: %0.4f" %(FittedHMS))
			         #objMsg.printMsg("prevFittedHMS: %0.4f" %(prevFittedHMS))
			         deltaFittedHMS = prevFittedHMS - FittedHMS
			         #objMsg.printMsg("deltaFittedHMS: %0.4f" %(deltaFittedHMS))
			         #objMsg.printMsg("current hmsKP: %d" %(hmsKP))
			         if deltaFittedHMS > 0.25:
			            hmsKP = Iw+iwstep
			            #objMsg.printMsg("Hd %d Zn %d hmsKP: %d <------------------------" %(hd, zn, hmsKP))
			            iwUBTable[hd][zn]['HMSIwKP'] = hmsKP
			            break
            if hmsKP == 999:
               #objMsg.printMsg("Cannot find HMS knee point! Default to Sova IwKP, iwUBTable[%d][%d]['IwKP']=%d !" %(hd, zn, iwUBTable[hd][zn]['IwKP']))
               iwUBTable[hd][zn]['HMSIwKP'] = 0 #iwUBTable[hd][zn]['IwKP']
               #objMsg.printMsg("iwUBTable[%d][%d]['HMSIwKP']: %d <<<------------------------" %(hd, zn, iwUBTable[hd][zn]['HMSIwKP']))
               continue

      #objMsg.printMsg("iwUBTable00= %s" %(iwUBTable))

      # Print Sova KP, OW KP and HMS KP and the highest KP of them all:
      objMsg.printMsg('mmtdatadump_ow_hms_kp SOVA, OW & HMS IWKP TABLE')
      objMsg.printMsg('mmtdatadump_ow_hms_kp %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % ('Hd','Zn','Od','Oa','SOVAIwKP','OWIwKP','HMSIwKP','MaxIwKP'))
      for hd in self.headRange:
         for zn in testzonelist:
            maxIwKP = max(iwUBTable[hd][zn]['IwKP'], iwUBTable[hd][zn]['OWIwKP'])
            #if iwUBTable[hd][zn]['IwKP'] >= maxIwKP:
               #maxIwKP = iwUBTable[hd][zn]['IwKP']
            #if iwUBTable[hd][zn]['OWIwKP'] >= maxIwKP:
               #maxIwKP = iwUBTable[hd][zn]['OWIwKP']
            #if iwUBTable[hd][zn]['HMSIwKP'] >= maxIwKP:
               #maxIwKP = iwUBTable[hd][zn]['HMSIwKP']
            #iwUBTable[hd][zn]['IwLB'] = maxIwKP + iwstep  	
            objMsg.printMsg('mmtdatadump_ow_hms_kp %2d\t%2d\t%2d\t%2d\t%2d      \t%2d    \t%2d    \t%2d' % (hd,zn,iwUBTable[hd][zn]['Osd'],iwUBTable[hd][zn]['Osa'],iwUBTable[hd][zn]['IwKP'],iwUBTable[hd][zn]['OWIwKP'],iwUBTable[hd][zn]['HMSIwKP'],maxIwKP))

      return iwUBTable



   def runOwHms_LBIw(self, testzonelist, iwlist):
      oProc = CProcess()
      import Utility
      oUtil = Utility.CUtility()
      
      if testSwitch.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH:
         iwstep = TP.mmt_iwstep
         ow_iwstep = TP.mmt_ow_iwstep
      else:
         iwstep = TP.mmt_iwstep
      ati_param = oUtil.copy(TP.prm_Triplet_ATI_STE)
      param61 = TP.WeakWrOWPrm_61.copy()
      param_HMS = {'test_num' : 211, 'prm_name' : 'measureHMS', 'spc_id': 0, 'HMS_STEP': 1, 'HEAD_MASK': 3, 'ADJ_BPI_FOR_TPI': 0, 'RESULTS_RETURNED': 6, 'NUM_SQZ_WRITES': 0, 'CWORD6': 1, 'TARGET_SER': 5, 'ZONE_MASK': (65535L, 65535L), 'HMS_START': 20, 'ZONE_POSITION': 198, 'spc_id': 0, 'NUM_TRACKS_PER_ZONE': 6, 'TLEVEL': 5, 'START_OT_FOR_TPI': 0, 'HMS_MAX_PUSH_RELAX': 490, 'ZONE_MASK_BANK': 0, 'timeout': 1080000, 'THRESHOLD': 90, 'SET_OCLIM': 655, 'ZONE_MASK_EXT': (65535L, 65535L), 'CWORD2': 3, 'CWORD1': 24588}

      loop_count = 6000
      OW_HMS_MMTtable={}
      for hd in self.headRange:
         OW_HMS_MMTtable[hd] = {}
         for zn in testzonelist:
            OW_HMS_MMTtable[hd][zn] = {}
            for Iw in iwlist:
               OW_HMS_MMTtable[hd][zn][Iw] = {}
               OW_HMS_MMTtable[hd][zn][Iw]['OW'] = -1
               #OW_HMS_MMTtable[hd][zn][Iw]['OW_IwKP'] = -1
               #OW_HMS_MMTtable[hd][zn][Iw]['HMS'] = -1
               #OW_HMS_MMTtable[hd][zn][Iw]['HMS_IwKP'] = -1

      iwlist.sort() 
      if testSwitch.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH:
         objMsg.printMsg("iwlist sorted in incremental order: %s" %(iwlist))
      else:
         iwlist.reverse()
         objMsg.printMsg("iwlist sorted in reverse order: %s" %(iwlist))
      oiwlist = iwlist
      

      if self.dut.BG in ['SBS']:
         if testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
            dbtable = 'P382_OW_MEASUREMENT'
         else:
            dbtable = 'P061_OW_MEASUREMENT'
         
         try:
            self.dut.dblData.Tables(dbtable).deleteIndexRecords(1)#del file pointers
            self.dut.dblData.delTable(dbtable)#del RAM objects
         except:
            objMsg.printMsg("table %s delete failed. "%dbtable)
            pass
      for zn in testzonelist:
         # Reset tracking variables before Iw loop begin:
         for hd in self.headRange:
            Osa = self.finalTripletTable[hd][zn]['OSA_fitted']
            Osd = self.finalTripletTable[hd][zn]['OSD_fitted']
            #IwUB = iwUBTable[hd][zn]['IwUB']
            IwKP = self.finalTripletTable[hd][zn]['SOVA_IwKP']
            if testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
               if testSwitch.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH:
                  # Loop iw in SF3 T61, so only need to pass first item in iwlist.
                  # Loop start from 1 dac (a value of iw=7) upwards, incrementally, by a step size of 2,3 or 7 (defined by TP.mmt_ow_iwstep).
                  iwlist = [TP.mmt_ow_start_iw]
                  objMsg.printMsg("H%d Z%d Loop Iw in T61. New iwlist: %s. Start from 1 dac (a value of Iw=7)." %(hd,zn,iwlist))
               else:
                  # Loop iw in SF3 T61, so only need to pass first item in iwlist, decrementally.
                  # Loop start from sova IwKP + 2 dac downwards.
                  for Iw2 in oiwlist:
                     #objMsg.printMsg("Iw: %d. IwKP: %d." %(Iw2, IwKP))
                     if IwKP <= Iw2:
		                iwlist = [max((Iw2 + (2*iwstep)), 56)]
                  objMsg.printMsg("H%d Z%d Loop Iw in T61. New iwlist: %s. Start from (Sova IwKP + 2 dac) or min 7 dac." %(hd,zn,iwlist))
                     
            for Iw in iwlist:
               objMsg.printMsg("Iw: %d" %(Iw))

               if 'OW_IwKP' in self.finalTripletTable[hd][zn].keys():
                  objMsg.printMsg("finalTripletTable[%d][%d]['OW_IwKP']: %d" %(hd, zn, self.finalTripletTable[hd][zn]['OW_IwKP']))
                  objMsg.printMsg("OW IwKP found. Continue on next head/zone loop.")
                  break

               if IwKP < 0 or testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
                  startIw = max(iwlist)
                  endIw = min(iwlist)
               else:
                  #endIw = IwKP - (4*iwstep) #End at 4 dac above Sova IwKP 
                  startIw = max((IwKP + (2*iwstep)), 56)   #Start from 2 dac below Sova IwKP
                  endIw = min(iwlist)
                  if startIw > max(iwlist):
                     startIw = max(iwlist)

               objMsg.printMsg("startIw: %d" %(startIw))
               objMsg.printMsg("endIw: %d" %(endIw))

               if Iw <= startIw and Iw >= endIw:  
                  #objMsg.printMsg("Iw loop running: %s" %(Iw))
                  

                  objMsg.printMsg("--------------------------------------------------------------------")
                  objMsg.printMsg("-------------------- Loop Count %d, spc_id: %d --------------------" %(loop_count, loop_count))
                  objMsg.printMsg("--------------------------------------------------------------------")
                  objMsg.printMsg("Head %d zn %d, Osd: %d, Osa: %d, Iw: %d" %(hd, zn, Osd, Osa, Iw))

                  #if 1:                      
                  tableData = []
                  if testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
                     cwd1 = 0x0101
                     param61.update({'DELTA_SPEC': TP.mmt_ow_spec})
                     if testSwitch.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH:
                         param61.update({'IW_STEP': iwstep, 'IW_MAX': max(TP.mmt_iwlist)})
                  else:
                     cwd1 = 0x00C1
                  param61.update({'RESULTS_RETURNED': 0, 'spc_id': loop_count, 'HEAD_RANGE': ( (hd << 8) + hd ), 'ZONE': zn, 'CWORD1': cwd1, 'DURATION': Osd, 'WRITE_CURRENT': Iw, 'DAMPING': Osa})
    
                  try:
                     CProcess().St(param61)      
                  except:
                     objMsg.printMsg("WeakWrOWPrm_61 fail. Powercycle and retry...")
                     # power cycle and try with a higher Iw:
                     from PowerControl import objPwrCtrl
                     objPwrCtrl.powerCycle(5000,12000,10,30)
                     objPwrCtrl = None  # Allow GC
                     if testSwitch.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH:
                        Iw += iwstep
                        objMsg.printMsg("Retry with higher Iw: %d" %(Iw))
                        param61.update({'WRITE_CURRENT': Iw})
                     try: CProcess().St(param61)
                     except:
                        objMsg.printMsg("WeakWrOWPrm_61 fail. Update OW saturation point to be the same as Sova's.")
                        self.finalTripletTable[hd][zn]['OW_IwKP'] = IwKP
                        self.finalTripletTable[hd][zn]['OW'] = 0
                        objMsg.printMsg("finalTripletTable[%d][%d]['OW_IwKP']: %d" %(hd, zn, self.finalTripletTable[hd][zn]['OW_IwKP']))
                        objMsg.printMsg("finalTripletTable[%d][%d]['OW']: %f" %(hd, zn, self.finalTripletTable[hd][zn]['OW']))
                        pass

                  if testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
                     dbtable = 'P382_OW_MEASUREMENT'
                  else:
                     dbtable = 'P061_OW_MEASUREMENT'
                  try:
                     tableData = self.dut.dblData.Tables(dbtable).chopDbLog('SPC_ID', 'match',str(loop_count))
                  except: 
                     objMsg.printMsg("%s not found!!!!!", str(dbtable))
                     pass

                  if len(tableData) > 0:
                     for row in tableData:
                        iHead = int(row['HD_LGC_PSN'])
                        iZone = int(row['DATA_ZONE'])
                        iOW = float(row['OW'])
                        if iOW == '-inf':#??
                           iOW = 0
                        #objMsg.printMsg("iOW: %0.4f" %(iOW))
                        if (hd == iHead and zn == iZone and int(row['SPC_ID']) == loop_count):
                           if testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
                              iWRT_CUR = int(row['WRT_CUR'])
                              if testSwitch.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH:
                                 # When FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH is enabled, step size of iw no longer follows a fixed value of 7. It can be a step of 2, 3 or 7.
                                 OW_HMS_MMTtable[iHead][iZone][iWRT_CUR] = {}
                              OW_HMS_MMTtable[iHead][iZone][iWRT_CUR]['OW'] = iOW
                              #objMsg.printMsg("iHead: %d, iZone: %d, iOW: %f, iWRT_CUR: %d" % (iHead, iZone, iOW, iWRT_CUR))
                              #objMsg.printMsg("OW_HMS_MMTtable[%d][%d][%d]['OW']: %f" % (iHead,iZone,iWRT_CUR, OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW']))
                           else:
                              OW_HMS_MMTtable[iHead][iZone][Iw]['OW'] = iOW
                              #objMsg.printMsg("OW_HMS_MMTtable[%d][%d][%d]['OW']: %0.4f" %(hd, zn, Iw, OW_HMS_MMTtable[hd][zn][Iw]['OW']))
                              #objMsg.printMsg("iHead: %d, iZone: %d, iOW: %f, Iw: %d" % (iHead, iZone, iOW, Iw))
                              #objMsg.printMsg("OW_HMS_MMTtable[%d][%d][%d]['OW']: %f" % (iHead,iZone,Iw, OW_HMS_MMTtable[hd][zn][Iw]['OW']))
                
                     fineTuneStepReq = 0
                     if testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
                        iWRT_CUR_list = []
                        for iWRT_CUR in OW_HMS_MMTtable[hd][zn]:
                           if not (OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW'] == -1):
                              iWRT_CUR_list.append(iWRT_CUR)
                        iWRT_CUR_list.sort() 
                        if testSwitch.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH:
                           objMsg.printMsg("iWRT_CUR_list: %s" % str(iWRT_CUR_list))
                           endIw = max(iWRT_CUR_list) #update endIw
                        else:
                           iWRT_CUR_list.reverse()
                           objMsg.printMsg("iWRT_CUR_list: %s" % str(iWRT_CUR_list))
                           endIw = min(iWRT_CUR_list) #update endIw
                        objMsg.printMsg("New endIw: %d" % endIw)

                        #New ow detection algo involving moving average. This is because sometimes an overwrite of 20dB or 23dB cannot be achieved even if the max iw is reached.
                        #This new ow detection algo helps to identify a good working ow properly when ow spec cannot be met.
                        #First, find the moving average of 3 OW measurements.
                        #Treat first & last item differently:
                        for idx in range(len(iWRT_CUR_list)):
                           iWRT_CUR = iWRT_CUR_list[idx]
                           prev_idx = idx - 1
                           next_idx = idx + 1
                           moving_list = []
                           moving_avg = 0
                           moving_list.append(OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW'])
                           if prev_idx in range(len(iWRT_CUR_list)):
                              prev_iWRT_CUR = iWRT_CUR_list[prev_idx]
                              moving_list.append(OW_HMS_MMTtable[hd][zn][prev_iWRT_CUR]['OW'])
                           if next_idx in range(len(iWRT_CUR_list)):
                              next_iWRT_CUR = iWRT_CUR_list[next_idx]
                              moving_list.append(OW_HMS_MMTtable[hd][zn][next_iWRT_CUR]['OW'])
                           objMsg.printMsg("moving_list: %s" % str(moving_list))
                           for iavg in moving_list:
                              moving_avg += iavg
                           moving_avg = moving_avg / len(moving_list)
                           OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW_mAvg'] = moving_avg
                           objMsg.printMsg("OW_HMS_MMTtable[%d][%d][%d]['OW_mAvg']: %f" %(hd, zn, iWRT_CUR, OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW_mAvg']))
                        # Next, find OW knee point 
                        # if OW knee point is not found, 3 consecutive deltaAvg < 1, stop ow search and look for the lowest iw with highest ow:
                        ow_search_cnt = 0
                        ow_best = 0
                        iw_best = 0
                        objMsg.printMsg("mmt_ow_search_size: %d" % TP.mmt_ow_search_size)
                        for idx in range(len(iWRT_CUR_list)):
                           iWRT_CUR = iWRT_CUR_list[idx]
                           objMsg.printMsg("iWRT_CUR: %d" % iWRT_CUR)
                           prev_idx = idx - 1
                           prev_iWRT_CUR = iWRT_CUR_list[prev_idx]

                           if testSwitch.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH:
                              #T61 coarse tune loop will start from 7 (defined in TP.mmt_ow_start_iw) all the way to 105 (max value hardcoded in SF3), iwstep size: 7, stop when >=23bB (defined in TP.mmt_ow_spec) is achieved. 
                              if OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW'] >= 0 and OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW'] >= TP.mmt_ow_spec: #breakpoint. Found OW kp!
                                 self.finalTripletTable[hd][zn]['OW_IwKP'] = iWRT_CUR
                                 self.finalTripletTable[hd][zn]['OW'] = OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW']
                                 objMsg.printMsg("OW IwKP found! finalTripletTable[%d][%d]['OW_IwKP']: %d" %(hd, zn, self.finalTripletTable[hd][zn]['OW_IwKP']))
                                 objMsg.printMsg("finalTripletTable[%d][%d]['OW']: %f" %(hd, zn, self.finalTripletTable[hd][zn]['OW']))
                                 fineTuneStepReq = 1
                                 break
                           else:
                              if OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW'] >= 0 and OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW'] < TP.mmt_ow_spec: #breakpoint. Found OW kp!
                                 objMsg.printMsg("prev_iWRT_CUR: %d" % prev_iWRT_CUR)
                                 if prev_iWRT_CUR <= startIw and 'OW' in OW_HMS_MMTtable[hd][zn][prev_iWRT_CUR].keys():
                                    self.finalTripletTable[hd][zn]['OW_IwKP'] = prev_iWRT_CUR
                                    self.finalTripletTable[hd][zn]['OW'] = OW_HMS_MMTtable[hd][zn][prev_iWRT_CUR]['OW']
                                    objMsg.printMsg("OW IwKP found! finalTripletTable[%d][%d]['OW_IwKP']: %d" %(hd, zn, self.finalTripletTable[hd][zn]['OW_IwKP']))
                                    objMsg.printMsg("finalTripletTable[%d][%d]['OW']: %f" %(hd, zn, self.finalTripletTable[hd][zn]['OW']))
                                    fineTuneStepReq = 1
                                    break
                           
                           moving_list = []
                           moving_avg = 0
                           moving_list.append(OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW'])
                           # find the difference between the current average and the previous average, deltaAvg.
                           if prev_idx in range(len(iWRT_CUR_list)):
                              OW_HMS_MMTtable[hd][zn][iWRT_CUR]['deltaAvg'] = OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW_mAvg'] - OW_HMS_MMTtable[hd][zn][prev_iWRT_CUR]['OW_mAvg']
                           else:
                              OW_HMS_MMTtable[hd][zn][iWRT_CUR]['deltaAvg'] = 0
                           objMsg.printMsg("OW_HMS_MMTtable[%d][%d][%d]['deltaAvg']: %f" %(hd, zn, iWRT_CUR, OW_HMS_MMTtable[hd][zn][iWRT_CUR]['deltaAvg']))
                           if OW_HMS_MMTtable[hd][zn][iWRT_CUR]['deltaAvg'] < TP.mmt_ow_deltaStop and not (OW_HMS_MMTtable[hd][zn][iWRT_CUR]['deltaAvg'] == 0):
                              ow_search_cnt += 1
                           else:
                              ow_search_cnt = 0 #reset counter
                           objMsg.printMsg("ow_search_cnt: %d" % ow_search_cnt)
                           #If there are 3 consecutive deltaAvg < 1, stop ow search:
                           if ow_search_cnt >= TP.mmt_ow_search_size: 
                              #Pick the smallest Iw that has the highest ow value.
                              for idx2 in range(TP.mmt_ow_search_size):
                                 iWRT_CUR = iWRT_CUR_list[idx-idx2]
                                 if OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW'] >= ow_best:
                                    ow_best = OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW']
                                    iw_best = iWRT_CUR
                              self.finalTripletTable[hd][zn]['OW_IwKP'] = iw_best
                              self.finalTripletTable[hd][zn]['OW'] = ow_best
                              objMsg.printMsg("%d repeating consecutive deltaAvg encountered. OW IwKP found! finalTripletTable[%d][%d]['OW_IwKP']: %d" %(TP.mmt_ow_search_size, hd, zn, self.finalTripletTable[hd][zn]['OW_IwKP']))
                              objMsg.printMsg("finalTripletTable[%d][%d]['OW']: %f" %(hd, zn, self.finalTripletTable[hd][zn]['OW']))
                              break

                        if iWRT_CUR == endIw and not 'OW_IwKP' in self.finalTripletTable[hd][zn].keys():
                           if testSwitch.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH:
                              #ending Iw is a big number.
                              self.finalTripletTable[hd][zn]['OW_IwKP'] = min(iWRT_CUR, self.finalTripletTable[hd][zn]['SOVA_IwKP'] - iwstep)
                              # Verify OW_IwKP data:
                              # If OW_IwKP is negative due to invalid measurement, set it to the lowest Iw value. 
                              if self.finalTripletTable[hd][zn]['OW_IwKP'] < min(TP.mmt_iwlist):
                                 self.finalTripletTable[hd][zn]['OW_IwKP'] = min(TP.mmt_iwlist)
                              objMsg.printMsg("Hitting last Iw but still cannot find OW IwKP! Set OW IwKP to min(Iw,Sova Kp - %d): %d" %(iwstep,self.finalTripletTable[hd][zn]['OW_IwKP']))
                           else:
                              #ending Iw is a small number.
                              self.finalTripletTable[hd][zn]['OW_IwKP'] = max(iWRT_CUR, self.finalTripletTable[hd][zn]['SOVA_IwKP'] - iwstep)
                              # Verify OW_IwKP data:
                              # If OW_IwKP is negative due to invalid measurement, set it to the lowest Iw value. 
                              if self.finalTripletTable[hd][zn]['OW_IwKP'] < min(TP.mmt_iwlist):
                                 self.finalTripletTable[hd][zn]['OW_IwKP'] = min(TP.mmt_iwlist)
                              objMsg.printMsg("Hitting last Iw but still cannot find OW IwKP! Set OW IwKP to max(Iw,Sova Kp - %d): %d" %(iwstep,self.finalTripletTable[hd][zn]['OW_IwKP']))
                           if testSwitch.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH:
                              prevIw = Iw
                           else:
                              prevIw = Iw + iwstep
                           self.finalTripletTable[hd][zn]['OW'] = OW_HMS_MMTtable[hd][zn][prevIw]['OW']
                        if fineTuneStepReq == 1:
                           if testSwitch.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH:
                              #if OW IwKP can be found, run T61 fine tune (defined in TP.mmt_ow_iwstep) for better accuracy:
                              #T61 coarse tune result eg at iw=28 OW=9dB and at iw=35 OW=35dB. In T61 fine tune, 2 additional in-between steps will be run, in the case, it will be iw=30 & 32, step size is 2. 
                              loop_count = loop_count + 1
                              owkp = self.finalTripletTable[hd][zn]['OW_IwKP']
                              ow_fine_list = [owkp - iwstep + ow_iwstep, owkp - iwstep + ow_iwstep + ow_iwstep, owkp]
                              objMsg.printMsg("OW fine tune sweep...")
                              param61.update({'IW_STEP': TP.mmt_ow_iwstep, 'WRITE_CURRENT': ow_fine_list[0], 'IW_MAX': (ow_fine_list[1]), 'spc_id': loop_count})
                              try:
                                 CProcess().St(param61)      
                              except:
                                 objMsg.printMsg("WeakWrOWPrm_61 fail")
                                 # power cycle
                                 from PowerControl import objPwrCtrl
                                 objPwrCtrl.powerCycle(5000,12000,10,30)
                                 objPwrCtrl = None  # Allow GC
                                 try: CProcess().St(param61)
                                 except:
                                    objMsg.printMsg("WeakWrOWPrm_61 fail. Update OW saturation point to be the same as Sova's.")
                                    self.finalTripletTable[hd][zn]['OW_IwKP'] = IwKP
                                    self.finalTripletTable[hd][zn]['OW'] = 0
                                    objMsg.printMsg("finalTripletTable[%d][%d]['OW_IwKP']: %d" %(hd, zn, self.finalTripletTable[hd][zn]['OW_IwKP']))
                                    objMsg.printMsg("finalTripletTable[%d][%d]['OW']: %f" %(hd, zn, self.finalTripletTable[hd][zn]['OW']))
                                    pass

                              try:
                                 tableData = self.dut.dblData.Tables('P382_OW_MEASUREMENT').chopDbLog('SPC_ID', 'match',str(loop_count))
                              except: 
                                 objMsg.printMsg("%s not found!!!!!", str(dbtable))
                                 pass

                              if len(tableData) > 0:
                                 for row in tableData:
                                    iHead = int(row['HD_LGC_PSN'])
                                    iZone = int(row['DATA_ZONE'])
                                    iOW = float(row['OW'])
                                    if iOW == '-inf':#??
                                       iOW = 0
                                    #objMsg.printMsg("iOW: %0.4f" %(iOW))
                                    if (hd == iHead and zn == iZone and int(row['SPC_ID']) == loop_count):
                                       iWRT_CUR = int(row['WRT_CUR'])
                                       # When FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH is enabled, step size of iw no longer follows a fixed value of 7. It can be a step of 2, 3 or 7.
                                       OW_HMS_MMTtable[iHead][iZone][iWRT_CUR] = {}
                                       OW_HMS_MMTtable[iHead][iZone][iWRT_CUR]['OW'] = iOW
                                       objMsg.printMsg("iHead: %d, iZone: %d, iOW: %f, iWRT_CUR: %d" % (iHead, iZone, iOW, iWRT_CUR))
                                       objMsg.printMsg("OW_HMS_MMTtable[%d][%d][%d]['OW']: %f" % (iHead,iZone,iWRT_CUR, OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW']))
                                 for iWRT_CUR in ow_fine_list: 
                                    # Pick the smallest Iw that can achieve OW=20dB:
                                    if 'OW' in OW_HMS_MMTtable[hd][zn][iWRT_CUR].keys():
                                       if OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW'] >= TP.mmt_ow_spec:
                                          self.finalTripletTable[hd][zn]['OW_IwKP'] = iWRT_CUR
                                          self.finalTripletTable[hd][zn]['OW'] = OW_HMS_MMTtable[hd][zn][iWRT_CUR]['OW']
                                          break
                                 objMsg.printMsg("OW IwKP after T61 fine tune is finalTripletTable[%d][%d]['OW_IwKP']: %d" %(hd, zn, self.finalTripletTable[hd][zn]['OW_IwKP']))
                                 objMsg.printMsg("finalTripletTable[%d][%d]['OW']: %f" %(hd, zn, self.finalTripletTable[hd][zn]['OW']))

                     else:
                        if 'OW' in OW_HMS_MMTtable[hd][zn][Iw].keys():
                           if OW_HMS_MMTtable[hd][zn][Iw]['OW'] >= 0 and OW_HMS_MMTtable[hd][zn][Iw]['OW'] < TP.mmt_ow_spec: #breakpoint. Found OW kp!
                              prevIw = Iw + iwstep
                              if prevIw <= startIw and 'OW' in OW_HMS_MMTtable[hd][zn][prevIw].keys():
                                 self.finalTripletTable[hd][zn]['OW_IwKP'] = prevIw
                                 self.finalTripletTable[hd][zn]['OW'] = OW_HMS_MMTtable[hd][zn][prevIw]['OW']
                                 objMsg.printMsg("OW IwKP found! finalTripletTable[%d][%d]['OW_IwKP']: %d" %(hd, zn, self.finalTripletTable[hd][zn]['OW_IwKP']))
                                 objMsg.printMsg("finalTripletTable[%d][%d]['OW']: %f" %(hd, zn, self.finalTripletTable[hd][zn]['OW']))
                                 continue

                        if Iw == endIw and not 'OW_IwKP' in self.finalTripletTable[hd][zn].keys():
                           self.finalTripletTable[hd][zn]['OW_IwKP'] = max(Iw, self.finalTripletTable[hd][zn]['SOVA_IwKP'] - 7)
                           objMsg.printMsg("Hitting lowest Iw but still cannot find OW IwKP! Set OW IwKP to max(7,Sova Kp - 7): %d" %(self.finalTripletTable[hd][zn]['OW_IwKP']))
                           prevIw = Iw + iwstep
                           self.finalTripletTable[hd][zn]['OW'] = OW_HMS_MMTtable[hd][zn][prevIw]['OW']

                  loop_count = loop_count + 1

                  #zn_arr = []
                  #zn_arr = [zn]
                  #bank = zn / 64
                  #tableData = []
                  #param_HMS.update({'spc_id': loop_count, 'HEAD_MASK': ( 1 << hd )})
                  #param_HMS['ZONE_MASK_EXT'], param_HMS['ZONE_MASK'] = oProc.oUtility.convertListTo64BitMask(zn_arr)
                  #param_HMS['ZONE_MASK_BANK'] = bank
                  #oUtil = None  # Allow GC
                  #try:              
                        #CProcess().St(param_HMS)      
                  #except:
                        #objMsg.printMsg("measureHMS fail")
                        #pass

                  #try:
                        #tableData = self.dut.dblData.Tables('P211_HMS_CAP_AVG').chopDbLog('SPC_ID', 'match',str(loop_count))
                  #except: 
                        #objMsg.printMsg("P211_HMS_CAP_AVG not found!!!!!")
                        #pass

                  #if len(tableData) > 0:
                        #for row in tableData:
                           #iHead = int(row['HD_LGC_PSN'])
                           #iZone = int(row['DATA_ZONE'])
                           #iHMS_CAP_AVG = float(row['HMS_CAP_AVG'])
                           #objMsg.printMsg("iHMS_CAP_AVG: %0.4f" %(iHMS_CAP_AVG))
                           #if (hd == iHead and zn == iZone and int(row['SPC_ID']) == loop_count):
                              #OW_HMS_MMTtable[hd][zn][Iw]['HMS'] = iHMS_CAP_AVG
                              #objMsg.printMsg("OW_HMS_MMTtable[%d][%d][%d]['HMS']: %0.4f" %(hd, zn, Iw, OW_HMS_MMTtable[hd][zn][Iw]['HMS']))

      objMsg.printMsg("OW_HMS_MMTtable: %s" %(OW_HMS_MMTtable))
                  
                  

      objMsg.printMsg('mmtdatadump_ow %s\t%s\t%s\t%s\t %s\t %s\t%s\t%s\t%s' % ('Hd','Zn','Od_fitted','Oa_fitted','Iw ','OW','HMS   ','OW_mAvg', 'deltaAvg'))
      for hd in self.headRange:
         for zn in testzonelist:
            Osa = self.finalTripletTable[hd][zn]['OSA_fitted']
            Osd = self.finalTripletTable[hd][zn]['OSD_fitted']
            ow_list = []
            for Iw in OW_HMS_MMTtable[hd][zn]:
               if OW_HMS_MMTtable[hd][zn][Iw]['OW'] >= 0:
                  ow_list.append(Iw)
            ow_list.sort()
            for Iw in ow_list:
               if 'OW_mAvg' in OW_HMS_MMTtable[hd][zn][Iw].keys():
                  OW_mAvg = OW_HMS_MMTtable[hd][zn][Iw]['OW_mAvg']
               else:
                  OW_mAvg = 0
               if 'deltaAvg' in OW_HMS_MMTtable[hd][zn][Iw].keys():
                  deltaAvg = OW_HMS_MMTtable[hd][zn][Iw]['deltaAvg']
               else:
                  deltaAvg = 0
               objMsg.printMsg('mmtdatadump_ow %2d\t%3d\t%9d\t%9d\t%3d\t%0.4f\t%0.4f\t%0.4f\t%0.4f' % (hd,zn,Osd,Osa,Iw,OW_HMS_MMTtable[hd][zn][Iw]['OW'],0,OW_mAvg,deltaAvg)) 

      #return OW_HMS_MMTtable

   def lumpData_by_2ndOrderFit(self, iwList, dataList):
      from MathLib import Fit_2ndOrder
      #objMsg.printMsg('iwList %s' % iwList)
      #objMsg.printMsg('dataList %s' % dataList)
      # Get 2nd order polynomial
      a, b, c = Fit_2ndOrder(iwList, dataList)
      #objMsg.printMsg('a= %s b= %s c= %s' % (a,b,c))
      
      if a == -1 and b == -1 and c == -1:
         objMsg.printMsg('Unable to filter by 2nd order')
      else:
         evalData = list(dataList) # make another copy of the list that will be used for iteration
         evalIw = list(iwList) # make another copy of the list that will be used for iteration
         #objMsg.printMsg('evalData %s' % evalData)
         #objMsg.printMsg('evalIw %s' % evalIw)
         errorZones = [] # list to store detected anomalous zone
         iter = 0 # keep iteration counter  for debug
         while 1:
            if verbose: objMsg.printMsg('evalIw %s' % evalIw)
            if verbose: objMsg.printMsg('evalData %s' % evalData)
            contEval = False
            goodData = []
            goodZone = []
            for item in range(len(evalIw)):
               #objMsg.printMsg('item %s' % item)
               fittedData = (a * evalIw[item] * evalIw[item]) + (b * evalIw[item]) + c
               #objMsg.printMsg('fittedData %s' % fittedData)
               #objMsg.printMsg('evalIw[item] %s' % evalIw[item])
               if abs(fittedData - evalData[item]) == 0 : #< 0.15: # hard code criteria for now in detecting anomalous zone
                  goodZone.append(evalIw[item])
                  goodData.append(evalData[item])
                  #if 1: objMsg.printMsg('zn %d fittedData  %.4f  evalData %.4f' % (evalIw[item], fittedData, evalData[item]))
               else:
                  contEval = True
                  errorZones.append(iwList[item])
                  #objMsg.printMsg('zn %d fittedData  %.4f  evalData %.4f FitError > 0.15' % (evalIw[item], fittedData, evalData[item]))
            
            if 0: 
               objMsg.printMsg('iter %d goodZone %s' % (iter, goodZone))
               objMsg.printMsg('iter %d goodData %s' % (iter, goodData))
               objMsg.printMsg('iter %d errorZones %s' % (iter, errorZones))
            
            if contEval == True and len(goodData) > 6: # need at least 6 zones to fit, another bit of hard code here
               a, b, c = Fit_2ndOrder(goodZone, goodData)  #recalculate polynomials for next iteration
               # Update the Eval Data and Zone for next iteration
               evalData = list(goodData)
               evalIw = list(goodZone)
               #objMsg.printMsg('evalData %s' % evalData)
               #objMsg.printMsg('evalIw %s' % evalIw)
            else: break # exit the loop
            iter += 1
            #if iter == 10:
               #break
            
         if len(errorZones): # if there are any zones detected as anomalous
            for item in range(len(iwList)):
               if iwList[item] in errorZones:
                  dataList[item] = (a * iwList[item] * iwList[item]) + (b * iwList[item]) + c # replace data with the final polynomial
         #if 1: objMsg.printMsg('final 2nd_order Filtered Data %s' % dataList)
         
      return dataList


   def finalIwUsingCOG (self, testzonelist): #finalIwTable
      oProc = CProcess()
      #self.headvendor = str(self.__dut.HGA_SUPPLIER)
      #objMsg.printMsg('headvendor %s' % str(self.headvendor)) 

      
      iwstep = TP.mmt_iwstep
      iw_sweep_list_len = 5 #TP.iw_sweep_list_len
      iwlist = TP.mmt_iwlist
      iwlist.sort()
      iwlist.reverse()

      
      # IW COG Sweep:
      for hd in self.headRange:
         for zn in testzonelist:  
            # Initialize Sweep List
            tIndex = 0
            sweepList_Iw = {}

            Osd = self.finalTripletTable[hd][zn]['OSD_fitted']
            nOa = self.finalTripletTable[hd][zn]['OSA_fitted']
            IwMin = self.finalTripletTable[hd][zn]['IwLB']
            IwMax = self.finalTripletTable[hd][zn]['IwUB']

            # Verifying all measurements:
            # If a head is bad and tests unmeasurable, set to use default Iw here:
            if ( self.finalTripletTable[hd][zn]['OSD'] == self.Def_Triplet[2] and \
               self.finalTripletTable[hd][zn]['OSA'] == self.Def_Triplet[1] and \
               self.finalTripletTable[hd][zn]['IwLB'] == min(TP.mmt_iwlist) and \
               self.finalTripletTable[hd][zn]['IwLB'] == self.finalTripletTable[hd][zn]['IwUB'] and \
               self.finalTripletTable[hd][zn]['SOVA_IwKP'] < 0):
                  objMsg.printMsg('H%d Z%d: OSD was defaulted to %d, OSA was defaulted to %d, Sova KP cannot be found (SOVA_IwKP < 0) and IwLB = IwUB = %d. IW shall be defaulted to %d. ' % 
                     (hd,zn,self.finalTripletTable[hd][zn]['OSD'],\
                     self.finalTripletTable[hd][zn]['OSA'],self.finalTripletTable[hd][zn]['IwLB'],self.Def_Triplet[0]))
                  self.finalTripletTable[hd][zn]['FINAL_IW'] = self.Def_Triplet[0]
                  continue


            # Determine iw sweep list:
            if testSwitch.FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH:
               # when FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH is enabled, ow step size no longer follow a value of 7 steps interval. it can be 2,3 or 7.

               for Iw in iwlist:
                  #objMsg.printMsg("Iw: %d. IwMin: %d." %(Iw, IwMin))
                  if IwMin <= Iw:
                     standardIwMin = Iw #To make sure list is in step of 7.
                     #objMsg.printMsg("standardIwMin: %d" %(standardIwMin))
               # Special case when LB=UB:
               if IwMin == IwMax:
                  sweepList = [IwMin, IwMin+iwstep, IwMin+iwstep+iwstep]
               else:
                  sweepList = range(standardIwMin,IwMax + 1, iwstep)
                  if not IwMin in sweepList:
                     sweepList.append(IwMin)
                  if len(sweepList) < 3:
                     # RSS want to maintain a list of min 3 sweeping points:
                     if (IwMin == standardIwMin):
                        sweepList = [IwMin, IwMin+iwstep, IwMin+iwstep+iwstep]
                     else:
                        sweepList = [IwMin, standardIwMin, standardIwMin+iwstep]
               sweepList.sort()
               objMsg.printMsg('hd %d zn %d final sweepList %s' % (hd,zn,str(sweepList)))
            else:
               sweepList = range(IwMin,IwMax + 1, iwstep)
               if len(sweepList) < 3:
                  sweepList = [IwMin - 7, IwMin, IwMin + 7]
               #if len(sweepList) > iw_sweep_list_len:
                  #sweepList = [IwMin, int( round((IwMax - IwMin) / (iw_sweep_list_len-1), 0))+IwMin, int( round((IwMax - IwMin) *2 / (iw_sweep_list_len-1), 0))+IwMin, int( round((IwMax - IwMin) *3 / (iw_sweep_list_len-1), 0))+IwMin, IwMax]
               objMsg.printMsg('hd %d zn %d sweepList %s' % (hd,zn,str(sweepList)))

            for nData in sweepList:
               sweepList_Iw[tIndex] = nData,nOa,Osd
               tIndex += 1
            #objMsg.printMsg('14292 sweepList_Iw updated %s' % str(sweepList_Iw)) 

            # Execute the Sweep
            measData_Iw = {}
            from VBAR import CTripletPicker
            runIwSweep = CTripletPicker()
            adcData_Iw, measData_Iw = runIwSweep.adcSweep(hd,zn,sweepList_Iw)
            #Q9300BRW TS: 402
            #adcData_Iw={0: 0.7974297609454339, 1: 0.7971959747764323, 2: 0.8002236053743452, 3: 0.8014959471303271, 4: 0.8012483063615932, 5: 0.8000925336667493, 6: 0.7986891780902141, 7: 0.796955576934991, 8: 0.7969792848922523, 9: 0.7973045490119404, 10: 0.7963164088016796, 11: 0.7969710497740436}
            #measData_Iw= {0: {'BPI': 0.9584575891494751, 'zHtClr': 100.99040222167969, 'TPI': 0.8319927453994751}, 1: {'BPI': 0.9616151452064514, 'zHtClr': 100.68560028076172, 'TPI': 0.829017698764801}, 2: {'BPI': 0.964772641658783, 'zHtClr': 100.33000183105469, 'TPI': 0.8294426798820496}, 3: {'BPI': 0.9711834192276001, 'zHtClr': 99.89820098876953, 'TPI': 0.8252776265144348}, 4: {'BPI': 0.9711834192276001, 'zHtClr': 99.39019775390625, 'TPI': 0.8250226378440857}, 5: {'BPI': 0.9711834192276001, 'zHtClr': 98.8313980102539, 'TPI': 0.8238325715065002}, 6: {'BPI': 0.9711834192276001, 'zHtClr': 98.1709976196289, 'TPI': 0.8223875761032104}, 7: {'BPI': 0.9711834192276001, 'zHtClr': 97.45980072021484, 'TPI': 0.820602536201477}, 8: {'BPI': 0.9743409752845764, 'zHtClr': 96.69779968261719, 'TPI': 0.8179675340652466}, 9: {'BPI': 0.9807517528533936, 'zHtClr': 95.83419799804688, 'TPI': 0.81295245885849}, 10: {'BPI': 0.9775941967964172, 'zHtClr': 94.89440155029297, 'TPI': 0.8145674467086792}, 11: {'BPI': 0.9807517528533936, 'zHtClr': 93.87840270996094, 'TPI': 0.8126124143600464}}
            #objMsg.printMsg('14300 adcData_Iw %s, measData_Iw %s' %(str(adcData_Iw), str(measData_Iw)))

            # Pick the Best ADC from the List
            TripletPick_Iw ={}
            bestIndex = runIwSweep.pickBestADC(sweepList_Iw, adcData_Iw, True)
            #Q9300BRW TS: 402
            TripletPick_Iw = sweepList_Iw[bestIndex]
            #bestIndex= 2
            #TripletPick_Iw= (49, 22, 20)
            #objMsg.printMsg('14300 bestIndex %s, TripletPick_Iw %s' %(str(bestIndex), str(TripletPick_Iw)))

            #Filter for BPIC Avalanche, Do not pick Iw that is adjacent to BPI drop > 5%
            if bestIndex != len(sweepList_Iw)-1 and self.headvendor == 'RHO': # if already maxed out, can not move to higher Iw
               bestIndex = runIwSweep.pickBestBPIC(sweepList_Iw,measData_Iw, bestIndex)
               TripletPick_Iw = sweepList_Iw[bestIndex]
               #objMsg.printMsg('951 TripletPick_Iw %s' %(str(TripletPick_Iw)))

            ##Filter for No slope BPIC, Set to Default Triplet if found
            bestIndex = runIwSweep.checkNoSlopeBPIC(sweepList_Iw,measData_Iw, bestIndex)
            if bestIndex == -1:
               #TripletPick_Iw = -1, -1, -1
               objMsg.printMsg('No Slope or Saturation found, aborting optimization and set to mid value of LB & UB Iw:')
               self.finalTripletTable[hd][zn]['FINAL_IW'] = (IwMin + IwMax)/2
            else:
               self.finalTripletTable[hd][zn]['FINAL_IW'] = TripletPick_Iw[0]
            objMsg.printMsg("mmtdatadump_final_iw self.finalTripletTable[%d][%d]['FINAL_IW'] %s" %(hd,zn,str(self.finalTripletTable[hd][zn]['FINAL_IW'])))

            # ------------------- Display data
            objMsg.printMsg('*' * 92)
            objMsg.printMsg('%s%s' % (' '* 40, 'WRITE TRIPLET OPTI'))
            if len(sweepList_Iw) > 0:
               objMsg.printMsg('IW SWEEEP LIST')
               runIwSweep.printADClist(hd,zn,sweepList_Iw, adcData_Iw,measData_Iw, TripletPick_Iw, 'O')

      # Interpolate & curve fit IW first before feeding final IW to OSD COG sweeping:
      self.build_interpolated_curve_fitting('FINAL_IW')

      # OSD COG sweep:
      for hd in self.headRange:
         for zn in testzonelist:  
            # Initialize Sweep List
            tIndex = 0
            sweepList_Osd = {}

            Osd = self.finalTripletTable[hd][zn]['OSD_fitted']
            nOa = self.finalTripletTable[hd][zn]['OSA_fitted']
            IwMin = self.finalTripletTable[hd][zn]['IwLB']
            IwMax = self.finalTripletTable[hd][zn]['IwUB']

            # Verifying all measurements:
            # If a head is bad and tests unmeasurable, set to use default Iw here:
            if ( self.finalTripletTable[hd][zn]['OSD'] == self.Def_Triplet[2] and \
               self.finalTripletTable[hd][zn]['OSA'] == self.Def_Triplet[1] and \
               self.finalTripletTable[hd][zn]['IwLB'] == min(TP.mmt_iwlist) and \
               self.finalTripletTable[hd][zn]['IwLB'] == self.finalTripletTable[hd][zn]['IwUB'] and \
               self.finalTripletTable[hd][zn]['SOVA_IwKP'] < 0):
                  objMsg.printMsg('H%d Z%d: OSD was defaulted to %d, OSA was defaulted to %d, Sova KP cannot be found (SOVA_IwKP < 0) and IwLB = IwUB = %d. IW shall be defaulted to %d. ' % 
                     (hd,zn,self.finalTripletTable[hd][zn]['OSD'],\
                     self.finalTripletTable[hd][zn]['OSA'],self.finalTripletTable[hd][zn]['IwLB'],self.Def_Triplet[0]))
                  self.finalTripletTable[hd][zn]['FINAL_OSD'] = self.Def_Triplet[2]
                  continue



            # Determine Osd sweep list:
            tIndex = 0
            sweepList = range(max(Osd-(2*1),2), min(Osd+(2*2)+1,31),2) # [-1,Osd,+1,+2]
            objMsg.printMsg('hd %d zn %d Osd sweepList %s' % (hd,zn,str(sweepList)))

            for nData in sweepList:
               sweepList_Osd[tIndex] = self.finalTripletTable[hd][zn]['FINAL_IW_fitted'],nOa,nData
               tIndex += 1
            #objMsg.printMsg('979 sweepList_Osd updated %s' % str(sweepList_Osd)) 

            # Execute the Sweep
            adcData_Osd, measData_Osd = runIwSweep.adcSweep(hd,zn,sweepList_Osd)
            #objMsg.printMsg('979 adcData_Osd %s, measData_Osd %s' %(str(adcData_Osd), str(measData_Osd)))

            # Pick the Best ADC from the List
            TripletPick_Osd ={}
            bestIndex = runIwSweep.pickBestADC(sweepList_Osd, adcData_Osd, True)
            TripletPick_Osd = sweepList_Osd[bestIndex]
            #objMsg.printMsg('979 bestIndex %s, TripletPick_Osd %s' %(str(bestIndex), str(TripletPick_Osd)))

            #Filter for BPIC Avalanche, Do not pick Iw that is adjacent to BPI drop > 5%
            #if bestIndex != len(sweepList_Osd)-1 and self.headvendor == 'RHO': # if already maxed out, can not move to higher Iw
               #bestIndex = runIwSweep.pickBestBPIC(sweepList_Osd,measData_Osd, bestIndex)
               #TripletPick_Osd = sweepList_Osd[bestIndex]
               #objMsg.printMsg('979 TripletPick_Osd %s' %(str(TripletPick_Osd)))

            ##Filter for No slope BPIC, Set to Default Triplet if found
            #bestIndex = runIwSweep.checkNoSlopeBPIC(sweepList_Iw,measData_Iw, bestIndex)
            #if bestIndex == -1:
               #TripletPick_Iw = -1, -1, -1
               #objMsg.printMsg('No Slope or Saturation found, aborting optimization and set to mid value of LB & UB Iw:')
               #self.finalTripletTable[hd][zn]['FINAL_IW'] = (IwMin + IwMax)/2
            #else:
               #self.finalTripletTable[hd][zn]['FINAL_IW'] = TripletPick_Osd[0]
            self.finalTripletTable[hd][zn]['FINAL_OSD'] = TripletPick_Osd[2]
            objMsg.printMsg("mmtdatadump_final_osd self.finalTripletTable[%d][%d]['FINAL_OSD'] %s" %(hd,zn,str(self.finalTripletTable[hd][zn]['FINAL_OSD'])))

            # ------------------- Display data
            objMsg.printMsg('*' * 92)
            objMsg.printMsg('%s%s' % (' '* 40, 'WRITE TRIPLET OPTI'))
            if len(sweepList_Osd) > 0:
               objMsg.printMsg('OD SWEEEP LIST')
               runIwSweep.printADClist(hd,zn,sweepList_Osd, adcData_Osd,measData_Osd, TripletPick_Osd, 'O')

      # Interpolate & curve fit OSD:
      self.build_interpolated_curve_fitting('FINAL_OSD')

      #return self.finalTripletTable


   def finalIwUsingT51 (self, testzonelist):
      oProc = CProcess()

      #IwLBFound = 1

      #iwUBTableFound = self.opOSAusingT51 (testzonelist, iwUBTable, iwlist, IwLBFound)
      #objMsg.printMsg('iwUBTableFound000= %s' % (iwUBTableFound))
      iwstep = TP.mmt_iwstep
      mmt_iwlist = TP.mmt_iwlist
      mmt_iwlist.sort()
      mmt_iwlist.reverse()
      loop_count = 9000
      meas_data = {}
      #smallestIwUB = {}
      for hd in self.headRange:
         meas_data[hd]={}
         #smallestIwUB[hd] = max(TP.mmt_iwlist) # initialize to an arbitrary large number.
         for zn in testzonelist:  
            meas_data[hd][zn]={}
            #iwUBTable[hd][zn]['IwLB'] = max(iwUBTable[hd][zn]['IwKP'], iwUBTable[hd][zn]['OWIwKP'], iwUBTable[hd][zn]['HMSIwKP'])

      for hd in self.headRange:
         for zn in TP.mmt_subzonelist:  
            Osd = self.finalTripletTable[hd][zn]['OSD_fitted']
            Osa = self.finalTripletTable[hd][zn]['OSA_fitted']
            #iwUBTable[hd][zn]['IwLB'] = max(iwUBTable[hd][zn]['IwKP'], iwUBTable[hd][zn]['OWIwKP'])
            IwKP = self.finalTripletTable[hd][zn]['SOVA_IwKP']
            for Iw2 in mmt_iwlist:
               #objMsg.printMsg("Iw: %d. IwKP: %d." %(Iw2, IwKP))
               if IwKP <= Iw2:
		          standardIwKP = Iw2 #To make sure list is in step of 7.
            iw_ste_check_list = range(min(standardIwKP+(7*7),max(TP.mmt_iwlist)),self.finalTripletTable[hd][zn]['IwLB']-1,-iwstep) # Fixed list LB + 6 = 7 sweeping points.
            if len(iw_ste_check_list) == 0:
               iw_ste_check_list = [self.finalTripletTable[hd][zn]['IwLB']]
             
            #for iw in iw_ste_check_list:
               #meas_data[hd][zn][iw]={}
            for iw in iw_ste_check_list:
               meas_data[hd][zn][iw]={}
               loop_count = loop_count + 1
               objMsg.printMsg("**********************************************************************************")
               objMsg.printMsg('STE checking list: iw_ste_check_list: %s' % (iw_ste_check_list))
               objMsg.printMsg('Head %2d, Zone %2d, Osd:%2d, Osa:%2d, Iw:%2d' % (hd,zn,Osd,Osa,iw)) 
               objMsg.printMsg("**********************************************************************************")
               minRRawBERATI, minRRawBERSTE, minSova = self.getMinRRawBER_T51(hd, zn, Osd, Osa, iw, loop_count, 3000, 11) #Must be 3000 for STE check!
               meas_data[hd][zn][iw]['WorseBER_ATI'] = minRRawBERATI
               meas_data[hd][zn][iw]['WorseBER_STE'] = minRRawBERSTE
               if minRRawBERSTE > 7 : #and minRRawBERATI > 5
                  meas_data[hd][zn][iw]['STATUS'] = 'PASS'
                  self.finalTripletTable[hd][zn]['IwUB'] = iw - iwstep
                  #objMsg.printMsg('STE PASS: %0.2f (>7). ATI PASS: %0.2f (>5). Set Upper Bound IW as %d-%d=%d.' % (minRRawBERSTE,minRRawBERATI,iw,iwstep,iwUBTable[hd][zn]['IwUB']))  
                  objMsg.printMsg('STE PASS: %0.2f (>7). Set Upper Bound IW as %d-%d=%d.' % (minRRawBERSTE,iw,iwstep,self.finalTripletTable[hd][zn]['IwUB']))  
                  if (self.finalTripletTable[hd][zn]['IwUB'] <= self.finalTripletTable[hd][zn]['IwLB']):
                     self.finalTripletTable[hd][zn]['IwUB'] = self.finalTripletTable[hd][zn]['IwLB']
                     objMsg.printMsg('Upper Bound IW cannot be <= Lower Bound IW. Set IwUB = IwLB as %d.' % (self.finalTripletTable[hd][zn]['IwUB']))   
                  break
               meas_data[hd][zn][iw]['STATUS'] = 'FAIL_STE_BER'
               #objMsg.printMsg('STE FAIL: %0.2f (<=7). ATI FAIL: %0.2f (<=5). Try next Iw...' % (minRRawBERSTE, minRRawBERATI))
               objMsg.printMsg('STE FAIL: %0.2f. Try next Iw...' % (minRRawBERSTE))
               if (minRRawBERSTE <= 7) and (iw == min(iw_ste_check_list)):# last iw #or minRRawBERATI <= 5
                  self.finalTripletTable[hd][zn]['IwUB'] = self.finalTripletTable[hd][zn]['IwLB']
                  objMsg.printMsg('STE FAIL: %0.2f. Set Upper Bound IW as %d (same as Lower Bound IW).' % (minRRawBERSTE,self.finalTripletTable[hd][zn]['IwUB']))
            #objMsg.printMsg('COG sweeping range: %d to %d.' % (iwUBTable[hd][zn]['IwLB'], iwUBTable[hd][zn]['IwUB']))
            #if (self.finalTripletTable[hd][zn]['IwUB'] < smallestIwUB[hd]):
               #smallestIwUB[hd] = self.finalTripletTable[hd][zn]['IwUB'] # Keep track of the smallest IwUB value for that head.

      # Use the smallest IwUB for all zones:
      #for hd in self.headRange:
         #objMsg.printMsg('Smallest IwUB in H%d is %d. Updating IwUB in all zones to this value..' % (hd, smallestIwUB[hd]))
         #for zn in testzonelist:  
            #iwUBTable[hd][zn]['IwUB'] = smallestIwUB[hd]

      #objMsg.printMsg('iwUBTable000= %s' % (iwUBTable))
      objMsg.printMsg('self.finalTripletTable OSD OSA SOVA_IwKP OSA_I OW_IwKP IwLB IwUB subzone = %s' % (self.finalTripletTable))

      # Interpolate 2 zones IwUB to get IwUB for all 5 zones:
      # Before interpolation begins, first check to see that zone 0 & 149 measurements are good.
      # There are cases where zone 0 or 149 are bad zone, its IwUB data is not reliable and thus cannot be used in the interpolation for all 5 zones.
      # Verifying zone 0 & 149 measurements:
      for hd in self.headRange:
         for zn in TP.mmt_subzonelist:
            currZnIdx = TP.mmt_subzonelist.index(zn)
            if ( self.finalTripletTable[hd][zn]['OSD'] == self.Def_Triplet[2] and \
               self.finalTripletTable[hd][zn]['OSA'] == self.Def_Triplet[1] and \
               self.finalTripletTable[hd][zn]['IwLB'] == min(TP.mmt_iwlist) and \
               self.finalTripletTable[hd][zn]['IwLB'] == self.finalTripletTable[hd][zn]['IwUB'] and \
               self.finalTripletTable[hd][zn]['SOVA_IwKP'] < 0):
                  objMsg.printMsg('H%d Z%d: OSD was defaulted to %d, OSA was defaulted to %d, Sova KP cannot be found SOVA_IwKP < 0 and IwLB = IwUB = %d. IwUB cannot be use in the interpolation.' % 
                     (hd,zn,self.finalTripletTable[hd][zn]['OSD'],\
                     self.finalTripletTable[hd][zn]['OSA'],self.finalTripletTable[hd][zn]['IwLB']))
                  if (currZnIdx == 0): # current zone is zone 0
                     copyZn = max(TP.mmt_subzonelist) # copy IwUB from zone 149
                  else: # current zone is zone 149
                     copyZn = min(TP.mmt_subzonelist) # copy IwUB from zone 0
                  self.finalTripletTable[hd][zn]['IwUB_I'] = self.finalTripletTable[hd][copyZn]['IwUB']
                  objMsg.printMsg('Copy IwUB=%d from H%d Z%d to H%d Z%d for interpolation.' % (self.finalTripletTable[hd][zn]['IwUB_I'],hd,copyZn,hd,zn))
                  
      # Interpolation begins:
      tempFinalTripletPick = {}
      for hd in self.headRange:
         tempFinalTripletPick[hd] = {}
         nX1 = 99
         for nZone in TP.mmt_subzonelist:
            if self.finalTripletTable[hd].has_key(nZone):
               #objMsg.printMsg("nZone %d" %nZone)
               if nX1 == 99:
                  if 'IwUB_I' in self.finalTripletTable[hd][nZone].keys():
                     nY1Iw = self.finalTripletTable[hd][nZone]['IwUB_I']
                  else:
                     nY1Iw = self.finalTripletTable[hd][nZone]['IwUB']
                  nX1 = nZone
               else:
                  if 'IwUB_I' in self.finalTripletTable[hd][nZone].keys():
                     nY2Iw = self.finalTripletTable[hd][nZone]['IwUB_I']
                  else:
                     nY2Iw = self.finalTripletTable[hd][nZone]['IwUB']
                  nX2 = nZone
                  nStepIw = float(float(nY2Iw - nY1Iw) / float(nX2 - nX1))
                  #objMsg.printMsg("nZone %d nStepIw %0.4f" % (nZone,nStepIw))
                  for yZone in range(nX1,nX2+1):
                     tempFinalTripletPick[hd][yZone] = {}
                     tempFinalTripletPick[hd][yZone][0] = int(round(nY1Iw + float(nStepIw * (yZone - nX1)),0))
                  nX1 = nX2
                  nY1Iw = nY2Iw

      izonelist = [aa for aa in testzonelist if aa not in TP.mmt_subzonelist]

      
      for hd in self.headRange:   
         interpolate_cnt = 0
         interpolate_flag = 1
         for zn in TP.mmt_subzonelist:
            if self.finalTripletTable[hd][zn]['IwUB'] == self.finalTripletTable[hd][zn]['IwLB']:
               interpolate_cnt += 1
         if len(TP.mmt_subzonelist) == interpolate_cnt:
            objMsg.printMsg('All zones from H%d has IwUB=IwLB. No interpolation is required for in between zones. ' % (hd))
            for zn in izonelist:
               self.finalTripletTable[hd][zn]['IwUB'] = self.finalTripletTable[hd][zn]['IwLB']
            interpolate_flag = 0
         if interpolate_flag == 1:
            for zn in izonelist:
               self.finalTripletTable[hd][zn]['IwUB'] = tempFinalTripletPick[hd][zn][0]
               if (self.finalTripletTable[hd][zn]['IwUB'] < self.finalTripletTable[hd][zn]['IwLB']):
                  self.finalTripletTable[hd][zn]['IwUB'] = self.finalTripletTable[hd][zn]['IwLB']
                  objMsg.printMsg('IwUB cannot < IwLB. Set Upper Bound IW of H%d Z%d as %d (same as Lower Bound IW).' % (hd,zn,self.finalTripletTable[hd][zn]['IwUB']))


      #objMsg.printMsg('iwUBTable0000= %s' % (iwUBTable))
      objMsg.printMsg('self.finalTripletTable OSD OSA SOVA_IwKP OSA_I OW_IwKP IwLB IwUB all zones = %s' % (self.finalTripletTable))

      objMsg.printMsg("mmtdatadump_ATI_STE_DBG: Hd   Zn   WRT_CUR  OVRSHT_AMP   OVRSHT_DUR   WORSE_ATI    WORSE_STE    STATUS")
      for hd in self.headRange:
         for zn in testzonelist: 
            for Iw in mmt_iwlist:
                  if meas_data[hd][zn].has_key(Iw):
                     Osa = self.finalTripletTable[hd][zn]['OSA_fitted']
                     Osd = self.finalTripletTable[hd][zn]['OSD_fitted']
                     #objMsg.printMsg("ATI_STE_DBG: Hd  Zn   WRT_CUR   OVRSHT_AMP   OVRSHT_AMP   WORSE_ATI   WORSE_STE   STATUS")
                                     #ATI_STE_DBG:  0   0   125       30           14           6.4200       8.9000       PASS
                     objMsg.printMsg("mmtdatadump_ATI_STE_DBG: %2d  %3d  %3d       %2d           %2d           %0.4f       %0.4f       %s" %
                                     (hd, zn, Iw, Osa, Osd, meas_data[hd][zn][Iw]['WorseBER_ATI'],meas_data[hd][zn][Iw]['WorseBER_STE'], meas_data[hd][zn][Iw]['STATUS']))

      # Print Sova KP, OW KP and HMS KP and the highest KP of them all:
      objMsg.printMsg('mmtdatadump_cog FINAL SOVA, OW & HMS IWKP TABLE')
      objMsg.printMsg('mmtdatadump_cog %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % ('Hd',' Zn','Od_fitted','Oa_fitted','SOVAIwKP','OWIwKP','HMSIwKP','IwLB','IwUB','COG_SWEEP'))
      for hd in self.headRange:
         for zn in testzonelist:
            Osa = self.finalTripletTable[hd][zn]['OSA_fitted']
            Osd = self.finalTripletTable[hd][zn]['OSD_fitted']
            #iwUBTable[hd][zn]['IwLB'] = max(iwUBTable[hd][zn]['IwKP'], iwUBTable[hd][zn]['OWIwKP'], iwUBTable[hd][zn]['HMSIwKP'])
            if (self.finalTripletTable[hd][zn]['IwLB'] == self.finalTripletTable[hd][zn]['IwUB']):
               COG_sweep = str(self.finalTripletTable[hd][zn]['IwLB'])+"-"+str(self.finalTripletTable[hd][zn]['IwLB']+iwstep+iwstep) # Must have min 3 points when sweeping COG. 
            else:
               COG_sweep = str(self.finalTripletTable[hd][zn]['IwLB'])+"-"+str(self.finalTripletTable[hd][zn]['IwUB'])
            #iwUBTable[hd][zn]['FINAL_IW'] = maxIwKP + iwstep
            #iwUBTable[hd][zn]['IwUB']=iwUBTableFound[hd][zn]['IwUB']
            #iwUBTable[hd][zn]['FINAL_IW'] = abs(((iwUBTable[hd][zn]['IwUB'] - iwUBTable[hd][zn]['IwLB'])/3)+iwUBTable[hd][zn]['IwLB']) #abs((iwUBTable[hd][zn]['IwLB'] + iwUBTable[hd][zn]['IwUB']) / 2)

            objMsg.printMsg('mmtdatadump_cog %2d\t%3d\t%9d\t%9d\t%8d\t%6d\t%7d\t%4d\t%4d\t%s' % (hd,zn,Osd,Osa,self.finalTripletTable[hd][zn]['SOVA_IwKP'],self.finalTripletTable[hd][zn]['OW_IwKP'],0,self.finalTripletTable[hd][zn]['IwLB'],self.finalTripletTable[hd][zn]['IwUB'],COG_sweep))
        
      objMsg.printMsg('NOTE: If IwLB=IwUB or list<3, COG_SWEEP=[IwLB,IwLB+%d,IwLB+%d+%d]' % (iwstep,iwstep,iwstep))
      #return self.finalTripletTable


   def opOSAusingT51 (self, testzonelist, osaKneePointTable, iwlist, IwLBFound):
      oProc = CProcess()
      
      iwstep = TP.mmt_iwstep
      self.n_writes = TP.mmt_n_writes #3000
      self.dc = TP.mmt_dc_start_value #0
      self.prev_dc = TP.mmt_dc_start_value #0
      dc_str_counter_all_heads = 0
      
      finalOsaTable={}
      for hd in self.headRange:
         finalOsaTable[hd] = {}
         for zn in testzonelist:
            finalOsaTable[hd][zn] = {}
            finalOsaTable[hd][zn]['IwUB'] = 0

      osaSelectionTable = {}

      #format dictionary:
      if IwLBFound:
         osaKneePointTableTemp = {}
         for hd in self.headRange:
            osaKneePointTableTemp[hd] = {}
            for zn in testzonelist:
               osaKneePointTableTemp[hd][zn] = {}
               Osd = osaKneePointTable[hd][zn]['Osd']
               osaKneePointTableTemp[hd][zn][Osd] = {}
               Osa = osaKneePointTable[hd][zn]['Osa']
               osaKneePointTableTemp[hd][zn][Osd][Osa] = {}
               osaKneePointTableTemp[hd][zn][Osd][Osa] = osaKneePointTable[hd][zn]

         osaKneePointTable = {}
         osaKneePointTable = osaKneePointTableTemp	
         objMsg.printMsg('formatted osaKneePointTable:%s' % (osaKneePointTable))

      # Sort Osa:
      osalistSorted = []
      for hd in self.headRange:
         for zn in testzonelist:
            for Osd in osaKneePointTable[hd][zn]:
               for Osa in osaKneePointTable[hd][zn][Osd]:
                  if not Osa in osalistSorted:
                     osalistSorted.append(Osa)
      osalistSorted.sort()

      
      
      if IwLBFound:
         loop_count = 9000
         #Populate previously found min ATI and STE data to dictionary so that test time can be shortened.
         for hd in self.headRange:
            for zn in testzonelist:
               IwLB_cnt = 1
               #self.dc = TP.mmt_dc_start_value #dc=28
               
               for Osd in osaKneePointTable[hd][zn]:
                  for Osa in osaKneePointTable[hd][zn][Osd]:
                     objMsg.printMsg('Hd %d, Zn %d, Od %d, Oa %d, IwLB_cnt %d' % (hd,zn,Osd,Osa,IwLB_cnt))
                     self.dc = osaKneePointTable[hd][zn][Osd][Osa]['dc_found']
                     self.n_writes = osaKneePointTable[hd][zn][Osd][Osa]['n_writes']
                     objMsg.printMsg('IwLBFound %d, self.dc %d, self.n_writes %d' % (IwLBFound,self.dc,self.n_writes))
                     osaKneePointTable[hd][zn][Osd][Osa]['dc'] = self.dc
                     osaKneePointTable[hd][zn][Osd][Osa]['IwLB_dc'] = osaKneePointTable[hd][zn][Osd][Osa]['IwLB'] + self.dc
                     osaKneePointTable[hd][zn][Osd][Osa]['dc_str_counter'] = 1
                     for cnt in range(1,6):
                        objMsg.printMsg('--- cnt %d' % (cnt))
                        dc_str = 'dc'
                        IwKP_dc_str = 'IwKP_dc'
                        RRAW_BER_ati_str = 'RRAW_BER_ATI'
                        RRAW_BER_ste_str = 'RRAW_BER_STE'
                        roc_str = 'ROC'
                        IwLB_dc_str = 'IwLB_dc'
                        IwLB_STE_str = 'IwLB_STE'
                        IwLB_ATI_str = 'IwLB_ATI'
                        if not cnt == 1:
                           IwKP_dc_str = IwKP_dc_str + str(cnt) # ok
                           RRAW_BER_ati_str = RRAW_BER_ati_str + str(cnt) 
                           RRAW_BER_ste_str = RRAW_BER_ste_str + str(cnt) 
                           roc_str = roc_str + str(cnt) 
                        objMsg.printMsg('--- IwKP_dc_str %s' % (IwKP_dc_str))
                        if IwKP_dc_str in osaKneePointTable[hd][zn][Osd][Osa].keys():
                           objMsg.printMsg('--- osaKneePointTable[%d][%d][%d][%d][%s]: %s' % (hd,zn,Osd,Osa,IwKP_dc_str,osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str]))
                        objMsg.printMsg("--- osaKneePointTable[%d][%d][%d][%d]['IwLB_dc']: %s" % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['IwLB_dc']))
                        if 0: #IwKP_dc_str in osaKneePointTable[hd][zn][Osd][Osa].keys() and osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str] == osaKneePointTable[hd][zn][Osd][Osa]['IwLB_dc']:
                           objMsg.printMsg('<--------------------- match found!')
                           osaKneePointTable[hd][zn][Osd][Osa]['IwLB_STE'] = osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ste_str]
                           objMsg.printMsg("--- osaKneePointTable[%d][%d][%d][%d]['IwLB_STE']: %s" % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['IwLB_STE']))
                           osaKneePointTable[hd][zn][Osd][Osa]['IwLB_ATI'] = osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ati_str]
                           objMsg.printMsg("--- osaKneePointTable[%d][%d][%d][%d]['IwLB_ATI']: %s" % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['IwLB_ATI']))
                           for cnt2 in range(cnt-1,0,-1):#for cnt2 in range(cnt+1,6):#
                              IwLB_cnt = IwLB_cnt + 1
                              objMsg.printMsg('--------- cnt %d, cnt2 %d,IwLB_cnt %d, self.dc %d' % (cnt, cnt2, IwLB_cnt, self.dc))
                              IwLB_dc_str = 'IwLB_dc'
                              IwLB_STE_str = 'IwLB_STE'
                              IwLB_ATI_str = 'IwLB_ATI'
                              if cnt2 == 1:
                                 RRAW_BER_ati_str = 'RRAW_BER_ATI'
                                 RRAW_BER_ste_str = 'RRAW_BER_STE'
                              else:
                                 RRAW_BER_ati_str = 'RRAW_BER_ATI' + str(cnt2)
                                 RRAW_BER_ste_str = 'RRAW_BER_STE' + str(cnt2)
                              if IwLB_cnt >= 2:
                                 IwLB_dc_str = 'IwLB_dc' + str(IwLB_cnt)
                                 IwLB_STE_str = 'IwLB_STE' + str(IwLB_cnt)
                                 IwLB_ATI_str = 'IwLB_ATI' + str(IwLB_cnt)
                                 dc_str = 'dc' + str(IwLB_cnt)

                              if 0: #RRAW_BER_ste_str in osaKneePointTable[hd][zn][Osd][Osa].keys():
                                 objMsg.printMsg('--------- old %s: %s' % (dc_str,osaKneePointTable[hd][zn][Osd][Osa][dc_str]))
                                 self.dc = self.dc - iwstep
                                 osaKneePointTable[hd][zn][Osd][Osa][dc_str] = self.dc
                                 objMsg.printMsg('--------- new %s: %s' % (dc_str,osaKneePointTable[hd][zn][Osd][Osa][dc_str]))
                                 osaKneePointTable[hd][zn][Osd][Osa][IwLB_dc_str] = osaKneePointTable[hd][zn][Osd][Osa]['IwLB'] + osaKneePointTable[hd][zn][Osd][Osa][dc_str]
                                 
                                 osaKneePointTable[hd][zn][Osd][Osa][IwLB_STE_str] = osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ste_str]
                                 osaKneePointTable[hd][zn][Osd][Osa][IwLB_ATI_str] = osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ati_str]
                                 objMsg.printMsg('--------- %s copy to %s: %0.4f' % (RRAW_BER_ste_str,IwLB_STE_str,osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ste_str]))
                                 objMsg.printMsg('--------- %s copy to %s: %0.4f' % (RRAW_BER_ati_str,IwLB_ATI_str,osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ati_str]))
                                 osaKneePointTable[hd][zn][Osd][Osa]['dc_str_counter'] = IwLB_cnt + 1
                                 objMsg.printMsg("======== osaKneePointTable[%d][%d][%d][%d]['dc_str_counter']: %d" % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['dc_str_counter']))
                              else:
                                 objMsg.printMsg('============ IwLB_cnt %d:' % (IwLB_cnt))
                                 osaKneePointTable[hd][zn][Osd][Osa]['dc_str_counter'] = IwLB_cnt
                                 objMsg.printMsg("============ osaKneePointTable[%d][%d][%d][%d]['dc_str_counter']: %d" % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['dc_str_counter']))
                                 break
                           break
         objMsg.printMsg('populated osaKneePointTable:%s' % (osaKneePointTable))
         for hd in self.headRange:
            for zn in testzonelist:
               for Osd in osaKneePointTable[hd][zn]:
                  for Osa in osaKneePointTable[hd][zn][Osd]:
                     objMsg.printMsg("======== osaKneePointTable[%d][%d][%d][%d]['dc_str_counter']: %d" % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['dc_str_counter']))

      else:
         loop_count = 3000
         #objMsg.printMsg('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % ('Hd','Zn','Od','Oa','IwKP','DC','IwKP+DC','FINAL_OSA'))
         for hd in self.headRange:
            for zn in testzonelist:
               for Osd in osaKneePointTable[hd][zn]:
                  for Osa in osalistSorted:
                     osaKneePointTable[hd][zn][Osd][Osa]['dc'] = self.dc
                     osaKneePointTable[hd][zn][Osd][Osa]['n_writes'] = self.n_writes
                     osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc'] = osaKneePointTable[hd][zn][Osd][Osa]['IwKP'] + self.dc
                     osaKneePointTable[hd][zn][Osd][Osa]['FINAL_OSA'] = -1
                     #objMsg.printMsg('%2d\t%2d\t%2d\t%2d\t%2d  \t%2d\t%2d     \t%2d' % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['IwKP'],self.dc,osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc'],osaKneePointTable[hd][zn][Osd][Osa]['FINAL_OSA'])) 


      
      OsaFound = 0
      endOsaLoop = 0
      upperBoundIwFound = 0
      
      for hd in self.headRange:
         for zn in testzonelist:
            for Osd in osaKneePointTable[hd][zn]:
               for Osa in osalistSorted:
                  if Osa in osaKneePointTable[hd][zn][Osd].keys():
                    if IwLBFound:
                       OsaFound = Osa
                       endOsaLoop = 1
                       dc_str_counter = osaKneePointTable[hd][zn][Osd][Osa]['dc_str_counter'] # This value keep track of which DC# T51 is not run yet.
                       dc_n_writes_found = 1
                       dc_plus_minus_found = 1
                       if dc_str_counter == 6:
                          # Find the 2nd order polynomial fitted ROC when 5x min ATI RRAW_BER are present:
                          dc_str = 'dc' + str(dc_str_counter-1) #This is the last obtained when osa was being found previously.
                          IwLB_dc_str = 'IwLB_dc' + str(dc_str_counter-1)
                          IwLB_ATI_str = 'IwLB_ATI' + str(dc_str_counter-1)
                          IwLB_STE_str = 'IwLB_STE' + str(dc_str_counter-1)
                          upperBoundIwFound = 1
                          findUBIwReq = 1
                          dc_str_counter = 5  
                       else:
                          if dc_str_counter <= 2:
                             dc_str = 'dc'
                             IwLB_dc_str = 'IwLB_dc'
                             IwLB_ATI_str = 'IwLB_ATI'
                             IwLB_STE_str = 'IwLB_STE'
                          else: 
                             dc_str = 'dc' + str(dc_str_counter-1) #This is the last obtained when osa was being found previously.
                             IwLB_dc_str = 'IwLB_dc' + str(dc_str_counter-1)
                             IwLB_ATI_str = 'IwLB_ATI' + str(dc_str_counter-1)
                             IwLB_STE_str = 'IwLB_STE' + str(dc_str_counter-1)
                          if dc_str_counter == 1:
                             self.dc = TP.mmt_dc_start_value
                          else:     
                             self.dc = osaKneePointTable[hd][zn][Osd][Osa][dc_str] - iwstep 
                          osaKneePointTable[hd][zn][Osd][OsaFound][dc_str] = self.dc
                          osaKneePointTable[hd][zn][Osd][OsaFound][IwLB_dc_str] = osaKneePointTable[hd][zn][Osd][Osa]['IwLB'] + self.dc
                          #objMsg.printMsg('27632 self.dc %d dc_str %s IwLB_dc_str %s' % (self.dc, dc_str, IwLB_dc_str))
                    else:
                       OsaFound = 0
                       endOsaLoop = 0
                       dc_str_counter = 1
                       self.dc = TP.mmt_dc_start_value
                       self.n_writes = TP.mmt_n_writes # 3000 
                       dc_n_writes_found = 0
                       dc_plus_minus_found = 0
                       dc_plus_minus_step = 7
                       dc_zero_sova = 0
                       dc_plus_delta = 0
                       IwLB_ATI_str = 'IwLB_ATI'
                       IwLB_STE_str = 'IwLB_STE'
                       dc_str = 'dc'
                       n_writes_str = 'n_writes'
                    IwKP_dc_str = 'IwKP_dc'
                    RRAW_BER_ati_str = 'RRAW_BER_ATI'
                    RRAW_BER_ste_str = 'RRAW_BER_STE'
                    upperBoundIwFound = 0
                    findUBIwReq = 0
                    #objMsg.printMsg('IwLBFound %d OsaFound %d endOsaLoop %d' % (IwLBFound, OsaFound, endOsaLoop))
                    avgIsDone = 0
                    #maxminOsaList = []
                    self.osaLoopList = osalistSorted
                    roc = 100

                    while (finalOsaTable[hd][zn]['IwUB'] == 0):
                       # Reset:
                       maxminRRawBERATI = 0
                       maxminRRawBERATI2 = 0
                       maxminRRawBERSTE = 0
                       maxminOsa = 0
                       maxminOsa2 = 0 # Require 2 repeating Osa with highest min ATI RRAW_BER to confirm a final Osa is found!
                       sova_scounter = 0 # saturation counter to keep track if one highest min BITS_IN_ERROR_BER can be found.
                       topOsa = 0
                       top2Osa = 0
                       changeDcFlag = 0
                       #objMsg.printMsg('Start of while loop ----------->\n self.dc: %d, self.n_writes: %d, changeDcFlag: %d' % (self.dc, self.n_writes, changeDcFlag))
                       #objMsg.printMsg('OsaFound: %d, endOsaLoop: %d, upperBoundIwFound: %d, dc_str_counter: %d' % (OsaFound, endOsaLoop, upperBoundIwFound, dc_str_counter))

                       if endOsaLoop == 1 and OsaFound == 0: # Top 2 Osa found are found!
                          #objMsg.printMsg('osaSelectionTable: %s' % (osaSelectionTable))
                          topOsa = osaSelectionTable[hd][zn][self.prev_dc]['Osa']
                          top2Osa = osaSelectionTable[hd][zn][self.prev_dc]['Osa2']

                          objMsg.printMsg('Top 2 Osa found are:%d and %d' % (topOsa, top2Osa))
                          #objMsg.printMsg('osaKneePointTable:%s' % (osaKneePointTable))
                          #objMsg.printMsg('RRAW_BER_ati_str:%s' % (RRAW_BER_ati_str)) #'RRAW_BER_ATI'
                          #objMsg.printMsg('RRAW_BER_ste_str:%s' % (RRAW_BER_ste_str)) #'RRAW_BER_STE' 
                          if osaKneePointTable[hd][zn][Osd][topOsa][IwKP_dc_str] > 127:
                             objMsg.printMsg('IwKP+dc max cap at 127 (old value of %d is too high).' % (osaKneePointTable[hd][zn][Osd][topOsa][IwKP_dc_str]))
                             osaKneePointTable[hd][zn][Osd][topOsa][IwKP_dc_str]=127
                          objMsg.printMsg("**********************************************************************************")
                          objMsg.printMsg('Head %2d, Zone %2d, Osd:%2d, topOsa:%2d, IwKP:%2d, DC(%s):%2d, n_writes(%s):%d, IwKP+dc(%s):%2d.' \
                                          % (hd,zn,Osd,topOsa,osaKneePointTable[hd][zn][Osd][topOsa]['IwKP'],dc_str,osaKneePointTable[hd][zn][Osd][topOsa][dc_str],\
                                              n_writes_str,osaKneePointTable[hd][zn][Osd][topOsa][n_writes_str],IwKP_dc_str,osaKneePointTable[hd][zn][Osd][topOsa][IwKP_dc_str])) 
                          objMsg.printMsg("**********************************************************************************")
                          loop_count = loop_count + 1
                          minRRawBERATI, minRRawBERSTE, minSova = self.getMinRRawBER_T51(hd, zn, Osd, topOsa, osaKneePointTable[hd][zn][Osd][topOsa][IwKP_dc_str], loop_count, self.n_writes,3)
                          osaKneePointTable[hd][zn][Osd][topOsa][RRAW_BER_ati_str] = minRRawBERATI
                          osaKneePointTable[hd][zn][Osd][topOsa][RRAW_BER_ste_str] = minSova
                          #osaKneePointTable[hd][zn][Osd][topOsa][dc_str] = self.dc
                          #osaKneePointTable[hd][zn][Osd][topOsa][n_writes_str] = self.n_writes
                          #osaKneePointTable[hd][zn][Osd][topOsa][IwKP_dc_str] = osaKneePointTable[hd][zn][Osd][topOsa]['IwKP'] + self.dc

                          if osaKneePointTable[hd][zn][Osd][top2Osa][IwKP_dc_str] > 127:
                             objMsg.printMsg('IwKP+dc max cap at 127 (old value of %d is too high).' % (osaKneePointTable[hd][zn][Osd][top2Osa][IwKP_dc_str]))
                             osaKneePointTable[hd][zn][Osd][top2Osa][IwKP_dc_str]=127
                          objMsg.printMsg("**********************************************************************************")
                          objMsg.printMsg('Head %2d, Zone %2d, Osd:%2d, top2Osa:%2d, IwKP:%2d, DC(%s):%2d, n_writes(%s):%d, IwKP+dc(%s):%2d.' \
                                          % (hd,zn,Osd,top2Osa,osaKneePointTable[hd][zn][Osd][top2Osa]['IwKP'],dc_str,osaKneePointTable[hd][zn][Osd][top2Osa][dc_str],\
                                              n_writes_str,osaKneePointTable[hd][zn][Osd][top2Osa][n_writes_str],IwKP_dc_str,osaKneePointTable[hd][zn][Osd][top2Osa][IwKP_dc_str])) 
                          objMsg.printMsg("**********************************************************************************")
                          loop_count = loop_count + 1
                          minRRawBERATI, minRRawBERSTE, minSova = self.getMinRRawBER_T51(hd, zn, Osd, top2Osa, osaKneePointTable[hd][zn][Osd][top2Osa][IwKP_dc_str], loop_count, self.n_writes,3)
                          osaKneePointTable[hd][zn][Osd][top2Osa][RRAW_BER_ati_str] = minRRawBERATI
                          osaKneePointTable[hd][zn][Osd][top2Osa][RRAW_BER_ste_str] = minSova
                          #osaKneePointTable[hd][zn][Osd][top2Osa][dc_str] = self.dc
                          #osaKneePointTable[hd][zn][Osd][top2Osa][n_writes_str] = self.n_writes
                          #osaKneePointTable[hd][zn][Osd][top2Osa][IwKP_dc_str] = osaKneePointTable[hd][zn][Osd][top2Osa]['IwKP'] + self.dc

                          # maxminOsa has a higher min ATI RAW_BER
                          if osaKneePointTable[hd][zn][Osd][topOsa][RRAW_BER_ati_str] > osaKneePointTable[hd][zn][Osd][top2Osa][RRAW_BER_ati_str]:
                             objMsg.printMsg('topOsa %d %s %0.2f > top2Osa %d %s %0.2f' % (topOsa, RRAW_BER_ati_str, osaKneePointTable[hd][zn][Osd][topOsa][RRAW_BER_ati_str], top2Osa, RRAW_BER_ati_str, osaKneePointTable[hd][zn][Osd][top2Osa][RRAW_BER_ati_str]))
                             OsaFound = topOsa   
                             #objMsg.printMsg('OsaFound:%d' % (OsaFound))
                          elif osaKneePointTable[hd][zn][Osd][topOsa][RRAW_BER_ste_str] > osaKneePointTable[hd][zn][Osd][top2Osa][RRAW_BER_ste_str]:
                             objMsg.printMsg('topOsa %d min Sova %0.2f > top2Osa %d min Sova %0.2f' % (topOsa, osaKneePointTable[hd][zn][Osd][topOsa][RRAW_BER_ste_str], top2Osa, osaKneePointTable[hd][zn][Osd][top2Osa][RRAW_BER_ste_str]))
                             OsaFound = topOsa
                          else:
                             objMsg.printMsg('topOsa does not have a higher %s! Take the average of topOsa %d and top2Osa %d!' % (RRAW_BER_ati_str, topOsa, top2Osa)) 
                             avgIsDone = (topOsa + top2Osa) / 2
                             OsaFound = avgIsDone
                             #objMsg.printMsg('OsaFound:%d' % (OsaFound))
                             #objMsg.printMsg('avgIsDone:%d' % (avgIsDone))
                             
                          objMsg.printMsg('mmtdatadump_osa_t51_report hd %d zn %d FINAL OSA %d IS FOUND!' % (hd,zn,OsaFound))

                          if (avgIsDone):
                             osaKneePointTable[hd][zn][Osd][avgIsDone] = {}
                             osaKneePointTable[hd][zn][Osd][avgIsDone]['IwKP'] = (osaKneePointTable[hd][zn][Osd][topOsa]['IwKP']+osaKneePointTable[hd][zn][Osd][top2Osa]['IwKP'])/2 
                             osaKneePointTable[hd][zn][Osd][avgIsDone][dc_str] = osaKneePointTable[hd][zn][Osd][topOsa][dc_str]
                             osaKneePointTable[hd][zn][Osd][avgIsDone][n_writes_str] = osaKneePointTable[hd][zn][Osd][topOsa][n_writes_str]
                             osaKneePointTable[hd][zn][Osd][avgIsDone][IwKP_dc_str] = osaKneePointTable[hd][zn][Osd][avgIsDone]['IwKP'] + osaKneePointTable[hd][zn][Osd][avgIsDone][dc_str]
                             if osaKneePointTable[hd][zn][Osd][avgIsDone][IwKP_dc_str] > 127:
                                osaKneePointTable[hd][zn][Osd][avgIsDone][IwKP_dc_str] = 127
                                osaKneePointTable[hd][zn][Osd][avgIsDone][dc_str] = 127 - osaKneePointTable[hd][zn][Osd][avgIsDone]['IwKP']
                             osaKneePointTable[hd][zn][Osd][avgIsDone][RRAW_BER_ste_str] = -1
                             osaKneePointTable[hd][zn][Osd][avgIsDone][RRAW_BER_ati_str] = -1
                             osaKneePointTable[hd][zn][Osd][avgIsDone]['FINAL_OSA'] = avgIsDone
                             #dc_str_counter = 1
                          else:
                             osaKneePointTable[hd][zn][Osd][OsaFound]['FINAL_OSA'] = OsaFound

                          findUBIwReq = 1
                          
                          finalOsaTable[hd][zn]['Osa'] = OsaFound
                          finalOsaTable[hd][zn]['Osd'] = Osd
                          finalOsaTable[hd][zn]['IwUB'] = 999 # Found Osa, set 999 to exit module.
                          finalOsaTable[hd][zn]['dc_found'] = self.dc
                          finalOsaTable[hd][zn]['n_writes_found'] = self.n_writes
                          finalOsaTable[hd][zn].update(osaKneePointTable[hd][zn][Osd][OsaFound])
                          #objMsg.printMsg('00000. osaKneePointTable:%s' % (osaKneePointTable))
                          #objMsg.printMsg('00000. finalOsaTable:%s' % (finalOsaTable)) 
                                   
                          
                       elif endOsaLoop == 1 and upperBoundIwFound == 0: # Upper bound Iw still not found!   
                          #objMsg.printMsg('osaKneePointTable:%s' % (osaKneePointTable))
                          #objMsg.printMsg('RRAW_BER_ati_str:%s' % (RRAW_BER_ati_str)) #'RRAW_BER_ATI'
                          #objMsg.printMsg('RRAW_BER_ste_str:%s' % (RRAW_BER_ste_str)) #'RRAW_BER_STE' 
                          #objMsg.printMsg('dc_str:%s' % (dc_str)) #'DC' 
                          #objMsg.printMsg('IwLB_ATI_str:%s' % (IwLB_ATI_str)) #'IwLB_ATI' 
                          #objMsg.printMsg('IwLB_STE_str:%s' % (IwLB_STE_str)) #'IwLB_STE'           
                          if osaKneePointTable[hd][zn][Osd][OsaFound][IwLB_dc_str] > 127:
                             objMsg.printMsg('IwLB+DC max cap at 127 (old value of %d is too high).' % (osaKneePointTable[hd][zn][Osd][OsaFound][IwLB_dc_str]))
                             osaKneePointTable[hd][zn][Osd][OsaFound][IwLB_dc_str]=127
                          objMsg.printMsg("**********************************************************************************")
                          objMsg.printMsg('Head %2d, Zone %2d, Osd:%2d, OsaFound:%2d, IwLB:%2d, DC(%s):%2d, n_writes(%s):%d, IwLB+DC(%s):%2d.' \
                                          % (hd,zn,Osd,OsaFound,osaKneePointTable[hd][zn][Osd][OsaFound]['IwLB'],dc_str,osaKneePointTable[hd][zn][Osd][OsaFound][dc_str],\
                                              n_writes_str,osaKneePointTable[hd][zn][Osd][OsaFound][n_writes_str],IwLB_dc_str,osaKneePointTable[hd][zn][Osd][OsaFound][IwLB_dc_str])) 
                          objMsg.printMsg("**********************************************************************************")

                          loop_count = loop_count + 1
                          minRRawBERATI, minRRawBERSTE, minSova = self.getMinRRawBER_T51(hd, zn, Osd, OsaFound, osaKneePointTable[hd][zn][Osd][OsaFound][IwLB_dc_str], loop_count, self.n_writes,3)
                          osaKneePointTable[hd][zn][Osd][OsaFound][IwLB_ATI_str] = minRRawBERATI
                          osaKneePointTable[hd][zn][Osd][OsaFound][IwLB_STE_str] = minSova
                          #osaKneePointTable[hd][zn][Osd][OsaFound][dc_str] = self.dc
                          #osaKneePointTable[hd][zn][Osd][OsaFound][n_writes_str] = self.n_writes
                          #osaKneePointTable[hd][zn][Osd][OsaFound][IwKP_dc_str] = osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] + self.dc
                          findUBIwReq = 1

                       elif dc_plus_minus_found == 0:
                          #Check for unmeasurable zone:
                          #If any of the OSA KP is -2 (unmeasurable), set OSA to default.
                          if osaKneePointTable[hd][zn][Osd][Osa]['IwKP'] == -2:
                             OsaFound = (self.Def_Triplet[1])#(Iw, Ovs, Ovd)
                             objMsg.printMsg('Zone with unmeasurable Sova. Set OSA to default %s. Exit module...' % str(OsaFound)) 
                             if OsaFound in osaKneePointTable[hd][zn][Osd].keys():
                                osaKneePointTable[hd][zn][Osd][OsaFound]['FINAL_OSA'] = OsaFound
                             else:
                                osaKneePointTable[hd][zn][Osd][OsaFound]={}
                                osaKneePointTable[hd][zn][Osd][OsaFound]['FINAL_OSA'] = OsaFound 
                                osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] = 0
                                osaKneePointTable[hd][zn][Osd][OsaFound][dc_str] = 0
                                osaKneePointTable[hd][zn][Osd][OsaFound][n_writes_str] = 0
                                osaKneePointTable[hd][zn][Osd][OsaFound][IwKP_dc_str] = 0
                                osaKneePointTable[hd][zn][Osd][OsaFound][RRAW_BER_ste_str] = -1
                                osaKneePointTable[hd][zn][Osd][OsaFound][RRAW_BER_ati_str] = -1 
                                osaKneePointTable[hd][zn][Osd][OsaFound]['minus_dc'] = -1
                                osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP_minus_dc'] = -1
                                osaKneePointTable[hd][zn][Osd][OsaFound]['RRAW_BER_ATI_minus_dc'] = -1
                                osaKneePointTable[hd][zn][Osd][OsaFound]['RRAW_BER_STE_minus_dc'] = -1
                                osaKneePointTable[hd][zn][Osd][OsaFound]['Sova_avg'] = -1
                             finalOsaTable[hd][zn]['Osa'] = OsaFound
                             finalOsaTable[hd][zn]['Osd'] = Osd
                             finalOsaTable[hd][zn]['IwUB'] = 999 # Found Osa, set 999 to exit module.
                             finalOsaTable[hd][zn].update(osaKneePointTable[hd][zn][Osd][OsaFound])
                             finalOsaTable[hd][zn]['dc_found'] = self.dc
                             finalOsaTable[hd][zn]['n_writes_found'] = self.n_writes
                             dc_plus_minus_found = 1
                             continue 


                          # Detecting the optimal DC value to be used.
                          # Start T51 with smallest Osa.
                          Osa = min(osalistSorted)  
                          objMsg.printMsg('dc-plus-minus. Take smallest Osa: %s' % (Osa)) 
                          objMsg.printMsg('dc-plus-minus. self.dc: %s' % (self.dc))
                          #objMsg.printMsg('dc-plus-minus. IwKP_dc_str: %s' % (IwKP_dc_str)) 
                          #objMsg.printMsg('dc-plus-minus. dc_str: %s' % (dc_str))
                          #objMsg.printMsg('dc-plus-minus. n_writes_str: %s' % (n_writes_str))
                          #objMsg.printMsg('RRAW_BER_ati_str:%s' % (RRAW_BER_ati_str)) #'RRAW_BER_ATI'
                          #objMsg.printMsg('RRAW_BER_ste_str:%s' % (RRAW_BER_ste_str)) #'RRAW_BER_STE'
                          #objMsg.printMsg('self.osaLoopList:%s' % (self.osaLoopList))

                          # Check that new DC is not too high and it's suitable for all OSAs. Iw cannot go beyond 127:
                          for Osa2 in self.osaLoopList:
                             if (osaKneePointTable[hd][zn][Osd][Osa2]['IwKP'] + self.dc) > 127:
                                self.dc = 127 - osaKneePointTable[hd][zn][Osd][Osa2]['IwKP']
                                objMsg.printMsg('dc-plus-minus. new self.dc: %s' % (self.dc))
                          osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str] = osaKneePointTable[hd][zn][Osd][Osa]['IwKP'] + self.dc
                          #objMsg.printMsg("dc-plus-minus. osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str]: %s" % (osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str])) 

                          objMsg.printMsg("**********************************************************************************")
                          objMsg.printMsg('Find %s (%d) & %s (%d): Head %2d, Zone %2d, Osd:%2d, Osa:%2d, IwKP:%2d, DC(%s):%2d, IwKP+dc(%s):%2d.' % (dc_str,self.dc,n_writes_str,self.n_writes,hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['IwKP'],dc_str,osaKneePointTable[hd][zn][Osd][Osa][dc_str],IwKP_dc_str,osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str])) 
                          objMsg.printMsg("**********************************************************************************")
                          loop_count = loop_count + 1
                          minRRawBERATI, minRRawBERSTE, minSova = self.getMinRRawBER_T51(hd, zn, Osd, Osa, osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str], loop_count, self.n_writes,3)
                          osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ati_str] = minRRawBERATI
                          osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ste_str] = minSova
                          if (self.dc == 0): #First run @ DC=0.
                             changeDcFlag = 1 #Change DC to run IwKP + an optimal step in the next loop. 
                             dc_zero_sova = minSova
                             dc_zero_otf = minRRawBERATI
                          else:
                             objMsg.printMsg("dc-plus-minus. Sova @ DC=0: dc_zero_sova: %s" % (dc_zero_sova)) 
                             
                             dc_plus_delta = dc_zero_sova - minSova
                             objMsg.printMsg('dc-plus-minus. dc_plus_delta: %s' % (dc_plus_delta)) 

                             ## No need to check for 0.1 delta:
                             #Proceed to test IwKP - DC and all 5x osa.
                             dc_plus_minus_found = 1
                             continue
                             ##if (dc_plus_delta > TP.mmt_dc_plus_delta_check):
                                ##objMsg.printMsg('dc-plus-minus. The optimal DC is found! self.dc: %s' % (self.dc)) 
                                ###Proceed to test IwKP - DC and all 5x osa.
                                ##dc_plus_minus_found = 1
                                ##continue
                             ##elif osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str] == 127 and (minSova <= 1.65 or dc_plus_delta <= TP.mmt_dc_plus_delta_check):
                                ### Re-start all over from DC=0 to get baseline at lowest n_writes:
                                ##objMsg.printMsg('Iw is hitting MAX but (minSova is still <= 1.65 or dc_plus_delta is still <= %s). Set n_writes = 100, dc = 7 to run on other OSA.' % str(TP.mmt_dc_plus_delta_check)) 
                                ##self.n_writes = 100
                                ##if (self.headvendor == 'RHO'):
                                   ##self.dc = 7
                                ##else:
                                   ##self.dc = 35
                                ##dc_str_counter = 1
                                ##dc_plus_minus_found = 1
                                ##changeDcFlag = 1 #Change DC to run IwKP + an optimal step in the next loop. 
                             ##else:
                                ##changeDcFlag = 1 #Change DC to run IwKP + an optimal step in the next loop.                                            
                          

                                      
                       else:
                          minRRawBERATIList = []
                          minSovaATIList = []
                          minSovaATIList2 = []
                          minSovaATIList3 = []
                          minSovaATIDict = {}
                          RRAW_BER_scounter = 0 # saturation counter to keep track if one highest min RRAW_BER_ATI can be found.
                          RRAW_BER_scounter2 = 0

                          
                          
                          #objMsg.printMsg('finalOsaTable:%s' % (finalOsaTable))
                          #objMsg.printMsg('self.osaLoopList=%s' % (self.osaLoopList))
                          for Osa in self.osaLoopList:
                             #objMsg.printMsg('1355 dc_str_counter: %s' % (dc_str_counter)) 
                             # DC @ 0:
                             objMsg.printMsg("**********************************************************************************")
                             objMsg.printMsg('DC @ 0: Head %2d, Zone %2d, Osd:%2d, Osa:%2d, IwKP:%2d, DC(%s):%2d, n_writes(%s):%d, IwKP+dc(%s):%2d.' \
                                              % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['IwKP'],'dc',osaKneePointTable[hd][zn][Osd][Osa]['dc'],\
                                                  'n_writes',self.n_writes,'IwKP_dc',osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc'])) 
                             objMsg.printMsg("**********************************************************************************")
                             if osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI'] == -1:
                                loop_count = loop_count + 1
                                minRRawBERATI, minRRawBERSTE, minSova = self.getMinRRawBER_T51(hd, zn, Osd, Osa, osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc'], loop_count, self.n_writes,3)
                                osaKneePointTable[hd][zn][Osd][Osa]['n_writes'] = self.n_writes
                                osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI'] = minRRawBERATI
                                osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE'] = minSova
                             elif not osaKneePointTable[hd][zn][Osd][Osa]['n_writes'] == self.n_writes:
                                objMsg.printMsg('Re-run T51 @ DC=0 & n_writes=%s:' % (self.n_writes))
                                loop_count = loop_count + 1
                                minRRawBERATI, minRRawBERSTE, minSova = self.getMinRRawBER_T51(hd, zn, Osd, Osa, osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc'], loop_count, self.n_writes,3)
                                osaKneePointTable[hd][zn][Osd][Osa]['n_writes'] = self.n_writes
                                osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI'] = minRRawBERATI
                                osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE'] = minSova
                             else:
                                objMsg.printMsg('Data @ DC=0 is already available. Do not re-run T51.')
                                minRRawBERATI = osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI']
                                minSova = osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE']
                                objMsg.printMsg('min ATI RRAW_BER:%0.2f' % (osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI']))
                                objMsg.printMsg('min ATI BITS_IN_ERROR_BER:%0.2f' % (osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE']))

                             # @ DC plus
                             if (self.headvendor == 'RHO'):
                                self.dc = 14
                             else:
                                self.dc = 35
                             osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc2'] = osaKneePointTable[hd][zn][Osd][Osa]['IwKP'] + self.dc
                             osaKneePointTable[hd][zn][Osd][Osa]['dc2'] = self.dc
                             osaKneePointTable[hd][zn][Osd][Osa]['n_writes2'] = self.n_writes

                             if osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc2'] > 127:
                                objMsg.printMsg('IwKP+dc max cap at 127 (old value of %d is too high).' % (osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc2']))
                                osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc2']=127
                             objMsg.printMsg("**********************************************************************************")
                             objMsg.printMsg('DC plus: Head %2d, Zone %2d, Osd:%2d, Osa:%2d, IwKP:%2d, DC(%s):%2d, n_writes(%s):%d, IwKP+dc(%s):%2d.' \
                                             % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['IwKP'],'dc2',osaKneePointTable[hd][zn][Osd][Osa]['dc2'],\
                                                 'n_writes2',osaKneePointTable[hd][zn][Osd][Osa]['n_writes2'],'IwKP_dc2',osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc2'])) 
                             objMsg.printMsg("**********************************************************************************")
                             
                             loop_count = loop_count + 1
                             minRRawBERATI_plus, minRRawBERSTE_plus, minSova_plus = self.getMinRRawBER_T51(hd, zn, Osd, Osa, osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc2'], loop_count, self.n_writes,3)
                             osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI2'] = minRRawBERATI_plus
                             osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE2'] = minSova_plus

                             # @ DC minus
                             osaKneePointTable[hd][zn][Osd][Osa]['minus_dc'] = -dc_plus_minus_step
                             osaKneePointTable[hd][zn][Osd][Osa]['IwKP_minus_dc'] = max(osaKneePointTable[hd][zn][Osd][Osa]['IwKP'] - dc_plus_minus_step, 1) # Put a safety value of 1 incase DC minus becomes negative.
                             #objMsg.printMsg("**********************************************************************************")
                             #objMsg.printMsg('DC minus: Head %2d, Zone %2d, Osd:%2d, Osa:%2d, IwKP:%2d, DC(%s):%2d, n_writes(%s):%d, IwKP+dc(%s):%2d.' \
                             #                % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['IwKP'],'minus_dc',osaKneePointTable[hd][zn][Osd][Osa]['minus_dc'],\
                             #                    'n_writes2',osaKneePointTable[hd][zn][Osd][Osa]['n_writes2'],'IwKP_minus_dc',osaKneePointTable[hd][zn][Osd][Osa]['IwKP_minus_dc'])) 
                             #objMsg.printMsg("**********************************************************************************")
                             loop_count = loop_count + 1 
                             #minRRawBERATI_minus, minRRawBERSTE_minus, minSova_minus = self.getMinRRawBER_T51(hd, zn, Osd, Osa, osaKneePointTable[hd][zn][Osd][Osa]['IwKP_minus_dc'], loop_count, self.n_writes,3) 
                             minRRawBERATI_minus, minRRawBERSTE_minus, minSova_minus = 0, 0, 0
                             osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI_minus_dc'] = minRRawBERATI_minus
                             osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE_minus_dc'] = minSova_minus

                             # Taking average of err rate at 3x locations ie DC=0, DC plus and DC minus:
                             osaKneePointTable[hd][zn][Osd][Osa]['Sova_avg'] = (minSova + minSova_plus )/2
                             osaKneePointTable[hd][zn][Osd][Osa]['Otf_avg'] = (minRRawBERATI + minRRawBERATI_plus )/2
                             objMsg.printMsg("**********************************************************************************")
                             objMsg.printMsg('Average err rate @ H%d Z%d IwKP+DC, IwKP, IwKP+DC: Sova_avg=%0.2f, Otf_avg=%0.2f' % (hd,zn,osaKneePointTable[hd][zn][Osd][Osa]['Sova_avg'],osaKneePointTable[hd][zn][Osd][Osa]['Otf_avg']))
                             objMsg.printMsg("**********************************************************************************")

                          #objMsg.printMsg('1.. osaKneePointTable=%s' % (osaKneePointTable))
                          for Osa in self.osaLoopList:
                             minRRawBERATIList.append((osaKneePointTable[hd][zn][Osd][Osa]['Otf_avg'], Osa))
                             minSovaATIList.append((osaKneePointTable[hd][zn][Osd][Osa]['Sova_avg'], Osa))
                             #minSovaATIDict[Osa] = osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ste_str]
                          objMsg.printMsg('minRRawBERATIList:%s' % (minRRawBERATIList))
                          objMsg.printMsg('minSovaATIList:%s' % (minSovaATIList))
                          maxminRRawBERATI, maxminOsaOtf = max(minRRawBERATIList) 
                          maxminSovaATI, maxminOsaSova = max(minSovaATIList)
                          #objMsg.printMsg('1.. maxminRRawBERATI:%s' % (maxminRRawBERATI))
                          #objMsg.printMsg('1.. maxminOsaOtf:%d' % (maxminOsaOtf))
                          #objMsg.printMsg('1.. maxminSovaATI:%s' % (maxminSovaATI))
                          #objMsg.printMsg('1.. maxminOsaSova:%d' % (maxminOsaSova))
                          #objMsg.printMsg('1.. RRAW_BER_scounter:%d' % (RRAW_BER_scounter))

                          for minRRawBERATI, OsaOtf in minRRawBERATIList:
                             if round(minRRawBERATI,4) == round(maxminRRawBERATI,4):
                                RRAW_BER_scounter = RRAW_BER_scounter + 1
                          #objMsg.printMsg('2.. RRAW_BER_scounter:%d' % (RRAW_BER_scounter))

                          #for minSovaATI, Osa in minSovaATIList:
                             #if minSovaATI == maxminSovaATI:
                                #sova_scounter = sova_scounter + 1

                          # when RRAW_BER_scounter = 1 -> There is only 1 highest min RRAW_BER, final optimized Osa can be found.
                          # when RRAW_BER_scounter >= 2 -> There are 2 or more highest min RRAW_BER, need to re-do T51 on highest 2x Osa having the same values. 
                          # when RRAW_BER_scounter = 5, sova_scounter=5 and min RRAW_BER >= 8.5 -> no resolution. min RRAW_BER is flat, need to increase DC to re-try.

                          if (RRAW_BER_scounter == 1): # There is only 1 highest min RRAW_BER, Osa can be found.
                             # Pick only the top Osa as the final Osafound.
                             # Consider Otf:
                             OsaFound =  maxminOsaOtf   
                             objMsg.printMsg('555..1. OsaFound:%s' % (OsaFound))
                          else: 
                             # when RRAW_BER_scounter >= 2 -> There are 2 or more highest min RRAW_BER, need to pick one out of the 2 or take an average.  
                             minRRawBERATIList.sort()
                             minRRawBERATIList.reverse()
                             objMsg.printMsg('555. minRRawBERATIList reverse:%s' % (minRRawBERATIList))

                             for osa_i in range(RRAW_BER_scounter):
                                osa_otf = minRRawBERATIList[osa_i][1]
                                minSovaATIList2.append(osa_otf)
                             objMsg.printMsg('555. minSovaATIList2:%s' % (minSovaATIList2))

                             if (RRAW_BER_scounter == 5):
                                 osa_max_sova = 0
                                 for osa_i in minSovaATIList2:
                                    #objMsg.printMsg('5555. osa_i:%s' % (osa_i))
                                    for sova_j,osa_j in minSovaATIList: 
                                       #objMsg.printMsg('5555. osa_j:%s' % (osa_j))
                                       if osa_i == osa_j:
                                          #objMsg.printMsg('5555. osa_i == osa_j:%s' % (osa_j))
                                          minSovaATIList3.append((sova_j, osa_j))
                                          if sova_j > osa_max_sova:
                                             osa_max_sova = sova_j
                                             OsaFound = osa_j
                                             #RRAW_BER_scounter = RRAW_BER_scounter + 1
                                          break
                                 objMsg.printMsg('555..2. OsaFound:%s' % (OsaFound))
                                 objMsg.printMsg('5555.. minSovaATIList3:%s' % (minSovaATIList3))

                                 for sovaATI, OsaSova in minSovaATIList3:
                                    if round(sovaATI,4) == round(osa_max_sova,4):
                                       RRAW_BER_scounter2 = RRAW_BER_scounter2 + 1
                                 #objMsg.printMsg('5555.. RRAW_BER_scounter2:%d' % (RRAW_BER_scounter2))


                                 if not(RRAW_BER_scounter2 == 1): 
                                    # when RRAW_BER_scounter >= 2 -> There are 2 or more highest min RRAW_BER, need to pick one out of the 2 or take an average.  
                                    minSovaATIList3.sort()
                                    minSovaATIList3.reverse()
                                    objMsg.printMsg('5555. minSovaATIList3 reverse:%s' % (minSovaATIList3))     

                                    sum_osa = 0
                                    for osa_i in range(RRAW_BER_scounter2):
                                       sum_osa = sum_osa + minSovaATIList3[osa_i][1]
                                    objMsg.printMsg('5555. sum_osa:%s' % (sum_osa))
                                    OsaFound = int(round((sum_osa / RRAW_BER_scounter2),0))
                                    objMsg.printMsg('5555..3. OsaFound:%s' % (OsaFound))
                             else:
                                minSovaATIList3 = []
                                sum_osa = 0
                                for osa_i in minSovaATIList2:
                                   sum_osa += osa_i
                                OsaFound = int(round((sum_osa / len(minSovaATIList2)),0))
                                objMsg.printMsg('5555..4. OsaFound:%s' % (OsaFound))

                             if not OsaFound in osalistSorted:
                                #objMsg.printMsg('5555..3. initialize dic for new OsaFound:%s' % (OsaFound))
                                osaKneePointTable[hd][zn][Osd][OsaFound] = {}
                                osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] = 0
                                if minSovaATIList3:
                                   for osa_i in range(RRAW_BER_scounter2):
                                      osa_j = minSovaATIList3[osa_i][1]
                                      osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] += osaKneePointTable[hd][zn][Osd][osa_j]['IwKP']
                                   osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] = osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] / RRAW_BER_scounter2
                                else:
                                   for osa_i in minSovaATIList2:
                                      osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] += osaKneePointTable[hd][zn][Osd][osa_i]['IwKP']
                                   osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] = osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] / len(minSovaATIList2)
                                osaKneePointTable[hd][zn][Osd][OsaFound]['dc'] = 0
                                osaKneePointTable[hd][zn][Osd][OsaFound]['n_writes'] = self.n_writes
                                osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP_dc'] = osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] + osaKneePointTable[hd][zn][Osd][OsaFound]['dc']
                                osaKneePointTable[hd][zn][Osd][OsaFound]['RRAW_BER_STE'] = -1
                                osaKneePointTable[hd][zn][Osd][OsaFound]['RRAW_BER_ATI'] = -1
                                osaKneePointTable[hd][zn][Osd][OsaFound]['dc2'] = self.dc
                                osaKneePointTable[hd][zn][Osd][OsaFound]['n_writes2'] = self.n_writes
                                osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP_dc2'] = osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] + osaKneePointTable[hd][zn][Osd][OsaFound]['dc2']
                                osaKneePointTable[hd][zn][Osd][OsaFound]['RRAW_BER_STE2'] = -1
                                osaKneePointTable[hd][zn][Osd][OsaFound]['RRAW_BER_ATI2'] = -1 
                                osaKneePointTable[hd][zn][Osd][OsaFound]['minus_dc'] = -dc_plus_minus_step
                                osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP_minus_dc'] = max(osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] - dc_plus_minus_step, 1)
                                osaKneePointTable[hd][zn][Osd][OsaFound]['RRAW_BER_ATI_minus_dc'] = -1
                                osaKneePointTable[hd][zn][Osd][OsaFound]['RRAW_BER_STE_minus_dc'] = -1
                                osaKneePointTable[hd][zn][Osd][OsaFound]['Sova_avg'] = -1 
                                osaKneePointTable[hd][zn][Osd][OsaFound]['Otf_avg'] = -1
                                

                          objMsg.printMsg('mmtdatadump_osa_t51_report hd %d zn %d FINAL OSA %d IS FOUND!' % (hd,zn,OsaFound))
                          endOsaLoop = 1
                          findUBIwReq = 1
                          changeDcFlag = 0
                          osaKneePointTable[hd][zn][Osd][OsaFound]['FINAL_OSA'] = OsaFound
                          finalOsaTable[hd][zn]['Osa'] = OsaFound
                          finalOsaTable[hd][zn]['Osd'] = Osd
                          finalOsaTable[hd][zn]['IwUB'] = 999 # Found Osa, set 999 to exit module.
                          finalOsaTable[hd][zn]['dc_found'] = self.dc
                          finalOsaTable[hd][zn]['n_writes_found'] = self.n_writes
                          finalOsaTable[hd][zn].update(osaKneePointTable[hd][zn][Osd][OsaFound])
                          objMsg.printMsg('5555..3. osaKneePointTable=%s' % (osaKneePointTable))
                                   
                                                                      

                       #objMsg.printMsg('findUBIwReq: %d' % (findUBIwReq))
                       #objMsg.printMsg('avgIsDone: %d, OsaFound: %d, topOsa: %d, top2Osa: %d' % (avgIsDone, OsaFound, topOsa, top2Osa))
                       if (findUBIwReq):
                          
                          
                          #objMsg.printMsg('dc_str_counter: %d' % (dc_str_counter))
                          #objMsg.printMsg('osaKneePointTable:%s' % (osaKneePointTable))
                          #objMsg.printMsg('finalOsaTable:%s' % (finalOsaTable))
                          #objMsg.printMsg('avgIsDone:%d' % (avgIsDone))

                          if dc_str_counter < 5:
                             changeDcFlag = 1
                             #objMsg.printMsg('0....changeDcFlag %d, roc %d.' % (changeDcFlag, roc))
                          else:
                             changeDcFlag = 0
                             #objMsg.printMsg('00....changeDcFlag %d, roc %d.' % (changeDcFlag, roc))
                          
                          # Find the 2nd order polynomial fitted ROC when 5x min ATI RRAW_BER are present:
                          if dc_str_counter == 5 and IwLBFound == 1:
                             rawATIList = []
                             for cnt in range(1,dc_str_counter+1):
                                #objMsg.printMsg('6....cnt= %d' % (cnt))
                                RRAW_BER_ati_str = 'IwLB_ATI' #'RRAW_BER_ATI'
                                if not cnt == 1:
                                   RRAW_BER_ati_str = RRAW_BER_ati_str + str(cnt)
                                ati = osaKneePointTable[hd][zn][Osd][OsaFound][RRAW_BER_ati_str]
                                #objMsg.printMsg('6....ati= %0.2f' % (ati))
                                rawATIList.append(ati)
                             #objMsg.printMsg('6....rawATIList= %s' % (rawATIList))
                             fittedATIList = self.lumpData_by_2ndOrderFit(range(1,6), rawATIList)
                             #objMsg.printMsg('6....fittedATIList= %s' % (fittedATIList))

                             for cnt in range(1,dc_str_counter+1):
                                #objMsg.printMsg('7....cnt= %d' % (cnt))
                                roc_str = 'ROC'
                                fitted_ati_str = 'FittedATI'                        
                                if not cnt == 1:
                                   roc_str = roc_str + str(cnt)
                                   fitted_ati_str = fitted_ati_str + str(cnt)
                                   osaKneePointTable[hd][zn][Osd][OsaFound][roc_str]=fittedATIList[cnt-1]- fittedATIList[cnt-2]
                                   #objMsg.printMsg('7....roc_str= %s' % (roc_str))
                                   #objMsg.printMsg('7....fitted roc value= %0.2f' % (osaKneePointTable[hd][zn][Osd][OsaFound][roc_str]))
                                osaKneePointTable[hd][zn][Osd][OsaFound][fitted_ati_str]=fittedATIList[cnt-1]
                                #objMsg.printMsg('7....fitted_ati_str= %s' % (fitted_ati_str))
                                #objMsg.printMsg('7....fitted ati value= %0.2f' % (osaKneePointTable[hd][zn][Osd][OsaFound][fitted_ati_str]))
                                
                             # Find upper bound Iw which has a saturating min ATI RRAW_BER.
                             # when roc (rate of change) between current min ATI RRAW_BER and previous min ATI RRAW_BER is < 0.6, a saturation point is said to have occured!
                             for cnt in range(1,dc_str_counter+1):
                                #objMsg.printMsg('8.... cnt %d' % (cnt))
                                dc_str = 'dc'
                                #IwKP_dc_str = 'IwKP_dc'
                                IwLB_dc_str = 'IwLB_dc'
                                RRAW_BER_ati_str = 'IwLB_ATI' #'RRAW_BER_ATI'
                                RRAW_BER_ste_str = 'IwLB_STE' #'RRAW_BER_STE'
                                roc_str = 'ROC'
                                if not cnt == 1:
                                   dc_str = dc_str + str(cnt) #'dc2'
                                   #IwKP_dc_str = IwKP_dc_str + str(cnt) #'IwKP_dc2'
                                   IwLB_dc_str = IwLB_dc_str + str(cnt) #'IwLB_dc2'
                                   RRAW_BER_ati_str = RRAW_BER_ati_str + str(cnt) #'IwLB_ATI2'
                                   RRAW_BER_ste_str = RRAW_BER_ste_str + str(cnt) #'IwLB_STE2'
                                   roc_str = roc_str + str(cnt) #'ROC2'
                                   if cnt == 2:
                                      prevRRAW_BER_ati_str = 'IwLB_ATI' #'RRAW_BER_ATI'
                                      #prevIwKP_dc_str = 'IwKP_dc'
                                      prevIwLB_dc_str = 'IwLB_dc'
                                      prevRRAW_BER_ste_str = 'IwLB_STE' #'RRAW_BER_STE'
                                      prevDc_str = 'dc'
                                   else:
                                      prevRRAW_BER_ati_str = 'IwLB_ATI' + str(cnt-1)
                                      #prevIwKP_dc_str = 'IwKP_dc' + str(cnt-1)
                                      prevIwLB_dc_str = 'IwLB_dc' + str(cnt-1)
                                      prevRRAW_BER_ste_str = 'IwLB_STE' + str(cnt-1)
                                      prevDc_str = 'dc' + str(cnt-1)

                                   roc = osaKneePointTable[hd][zn][Osd][OsaFound][roc_str]
                                   #objMsg.printMsg('8.... %s %0.2f' % (roc_str, roc))
                                   #objMsg.printMsg('8.... checking STE: %s %0.2f' % (prevRRAW_BER_ste_str, osaKneePointTable[hd][zn][Osd][OsaFound][prevRRAW_BER_ste_str]))
                                   if roc < 0.6 and osaKneePointTable[hd][zn][Osd][OsaFound][prevRRAW_BER_ste_str] > 7:
                                      upperBoundIwFound = 1
                                      finalOsaTable[hd][zn]['IwUB'] = osaKneePointTable[hd][zn][Osd][OsaFound][prevIwLB_dc_str] 
                                      #objMsg.printMsg('88.... roc < 0.6 and %s > 7!' % (prevRRAW_BER_ati_str))
                                      #objMsg.printMsg('88.... UPPER BOUND IW %d IS FOUND!' % (finalOsaTable[hd][zn]['IwUB']))
                                      finalOsaTable[hd][zn]['UB_RRAW_BER_ATI'] = osaKneePointTable[hd][zn][Osd][OsaFound][prevRRAW_BER_ati_str] 
                                      finalOsaTable[hd][zn]['UB_RRAW_BER_STE'] = osaKneePointTable[hd][zn][Osd][OsaFound][prevRRAW_BER_ste_str]
                                      finalOsaTable[hd][zn]['dc'] = osaKneePointTable[hd][zn][Osd][OsaFound][prevDc_str]
                                      break

                             # Print osaKneePointTable at the end of each DC while loop:
                             header_str = 'mmtdatadump_t51_iwub Hd\tZn\tOd\tOa\tIwLB\tDC\tIwLB+DC\tRRAW_BER_ATI\tRRAW_BER_STE'
                             for cnt in range(2,dc_str_counter+1):
                                header_str = header_str + '\tDC'+str(cnt)+'\tIwLB+DC'+str(cnt)+'\tRRAW_BER_ATI'+str(cnt)+'\tRRAW_BER_STE'+str(cnt)+'\tROC'+str(cnt)
                             objMsg.printMsg('%s' % (header_str))
                             osalistSorted2 = []
                             for Osd2 in osaKneePointTable[hd][zn]:
                                for Osa2 in osaKneePointTable[hd][zn][Osd2]:
                                   osalistSorted2.append(Osa2)
                             osalistSorted2.sort()
                             for Osd2 in osaKneePointTable[hd][zn]:
                                for Osa2 in osalistSorted2: #for Osa2 in osaKneePointTable[hd2][zn2][Osd2]:
                                   data_str = str(hd) + ' \t' + str(zn) + '\t' + str(Osd2) + '\t' + str(Osa2) + '\t'
                                   data_str = data_str + str(osaKneePointTable[hd][zn][Osd2][Osa2]['IwLB']) + '  \t'
                                   data_str = data_str + str(osaKneePointTable[hd][zn][Osd2][Osa2]['dc']) + '\t'
                                   data_str = data_str + str(osaKneePointTable[hd][zn][Osd2][Osa2]['IwLB_dc']) + '     \t'
                                   data_str = data_str + str(osaKneePointTable[hd][zn][Osd2][Osa2]['IwLB_ATI']) + '        \t'
                                   data_str = data_str + str(osaKneePointTable[hd][zn][Osd2][Osa2]['IwLB_STE']) + '        \t'
                                   for cnt in range(2,dc_str_counter+1):
                                      dc_str = 'dc'
                                      dc_str = dc_str + str(cnt)
                                      #IwKP_dc_str = 'IwKP_dc'
                                      IwLB_dc_str = 'IwLB_dc'
                                      #IwKP_dc_str = IwKP_dc_str + str(cnt)
                                      IwLB_dc_str = IwLB_dc_str + str(cnt) #'IwLB_dc2'
                                      RRAW_BER_ati_str = 'IwLB_ATI' #'RRAW_BER_ATI'
                                      RRAW_BER_ati_str = RRAW_BER_ati_str + str(cnt)
                                      RRAW_BER_ste_str = 'IwLB_STE' #'RRAW_BER_STE'
                                      RRAW_BER_ste_str = RRAW_BER_ste_str + str(cnt)
                                      roc_str = 'ROC'
                                      roc_str = roc_str + str(cnt)
                                      if dc_str in osaKneePointTable[hd][zn][Osd2][Osa2].keys():
                                         data_str = data_str + str(osaKneePointTable[hd][zn][Osd2][Osa2][dc_str]) + '\t'
                                         data_str = data_str + str(osaKneePointTable[hd][zn][Osd2][Osa2][IwLB_dc_str]) + '      \t'
                                         data_str = data_str + str(osaKneePointTable[hd][zn][Osd2][Osa2][RRAW_BER_ati_str]) + '        \t'
                                         data_str = data_str + str(osaKneePointTable[hd][zn][Osd2][Osa2][RRAW_BER_ste_str]) + '         \t'
                                      else:
                                         data_str = data_str + str(-1) + '\t' + str(-1) + '      \t' + str(-1) + '        \t' + str(-1) + '         \t' 
                                      if roc_str in osaKneePointTable[hd][zn][Osd2][Osa2].keys():
                                         data_str = data_str + str(osaKneePointTable[hd][zn][Osd2][Osa2][roc_str]) + '\t'
                                      else:
                                         data_str = data_str + str(-1) + '     \t'
                                   objMsg.printMsg('mmtdatadump_t51_iwub %s' % (data_str))
                                   break

                             #if roc is still high (did not break out of loop above), pick the first dc:
                             #objMsg.printMsg('9....upperBoundIwFound:%d' % (upperBoundIwFound))
                             if upperBoundIwFound == 0:
                                objMsg.printMsg('99.... All fitted ROCs > 0.6! Pick the last ROC w STE > 7 to determine upper bound Iw!')
                                upperBoundIwFound = 1
                                for cnt in range(dc_str_counter,0,-1):
                                   #objMsg.printMsg('99....cnt:%d' % (cnt))
                                   dc_str = 'dc'
                                   #IwKP_dc_str = 'IwKP_dc'
                                   IwLB_dc_str = 'IwLB_dc'
                                   RRAW_BER_ati_str = 'IwLB_ATI' #'RRAW_BER_ATI'
                                   RRAW_BER_ste_str = 'IwLB_STE' #'RRAW_BER_STE'
                                   roc_str = 'ROC'
                                   if not cnt == 1:
                                      dc_str = dc_str + str(cnt) #'dc2'
                                      #IwKP_dc_str = IwKP_dc_str + str(cnt) #'IwKP_dc2'
                                      IwLB_dc_str = IwLB_dc_str + str(cnt) #'IwLB_dc2'
                                      RRAW_BER_ati_str = RRAW_BER_ati_str + str(cnt) #'IwLB_ATI2'
                                      RRAW_BER_ste_str = RRAW_BER_ste_str + str(cnt) #'IwLB_STE2'
                                      roc_str = roc_str + str(cnt) #'ROC2'
                                   #objMsg.printMsg('99....%s %0.2f' % (RRAW_BER_ste_str, osaKneePointTable[hd][zn][Osd][OsaFound][RRAW_BER_ste_str]))
                                   #if osaKneePointTable[hd][zn][Osd][OsaFound][RRAW_BER_ste_str] > 7:
                                   finalOsaTable[hd][zn]['IwUB'] = osaKneePointTable[hd][zn][Osd][OsaFound][IwLB_dc_str]
                                   finalOsaTable[hd][zn]['UB_RRAW_BER_ATI'] = osaKneePointTable[hd][zn][Osd][OsaFound][RRAW_BER_ati_str]
                                   finalOsaTable[hd][zn]['UB_RRAW_BER_STE'] = osaKneePointTable[hd][zn][Osd][OsaFound][RRAW_BER_ste_str]
                                   finalOsaTable[hd][zn]['dc'] = osaKneePointTable[hd][zn][Osd][OsaFound][dc_str]
                                   objMsg.printMsg('99.... UPPER BOUND IW %d IS FOUND!' % (finalOsaTable[hd][zn]['IwUB']))
                                   break
                                #objMsg.printMsg('finalOsaTable[%d][%d][IwUB]= %d' % (hd, zn, finalOsaTable[hd][zn]['IwUB']))
                                #if upperBoundIwFound == 1 and (finalOsaTable[hd][zn]['IwUB'] == 999 or finalOsaTable[hd][zn]['IwUB'] == 0):
                                #   ScrCmds.raiseException(14635, 'STE fail!')

                       #objMsg.printMsg('OsaFound:%d' % (OsaFound))
                       #objMsg.printMsg('endOsaLoop:%d' % (endOsaLoop))
                       #objMsg.printMsg('upperBoundIwFound:%d' % (upperBoundIwFound))
                       #objMsg.printMsg('dc_plus_minus_found:%d' % (dc_plus_minus_found))
                       #objMsg.printMsg('current old self.dc: %d, self.n_writes: %d' % (self.dc, self.n_writes))
                       #objMsg.printMsg('changeDcFlag: %d' % (changeDcFlag))
                       #objMsg.printMsg('dc_str_counter: %d' % (dc_str_counter))
                       dc_str_counter_all_heads = max (dc_str_counter_all_heads, dc_str_counter)
                       #objMsg.printMsg('dc_str_counter_all_heads: %d' % (dc_str_counter_all_heads))
                       self.prev_dc = self.dc
                       #objMsg.printMsg('set prev_dc to current dc: %d' % (self.prev_dc))
                       if changeDcFlag == 1:
                          if OsaFound:
                             if avgIsDone:
                                avgIsDone = 0 #reset to 0.
                                self.dc = TP.mmt_dc_start_value # Need to re-do T51 from 28 onwards for the new average Osa. 
                                self.prev_dc = self.dc
                                dc_str = 'dc'
                                IwKP_dc_str = 'IwKP_dc'
                                RRAW_BER_ati_str = 'RRAW_BER_ATI'
                                RRAW_BER_ste_str = 'RRAW_BER_STE'
                                roc_str = 'ROC'
                                continue
                             else:
                                self.dc = self.dc - iwstep
                          else:
                             objMsg.printMsg('1111. minSova: %0.2f' % (minSova))
                             objMsg.printMsg('1111. minRRawBERATI: %0.2f, dc_n_writes_found: %d' % (minRRawBERATI, dc_n_writes_found)) 
                             if dc_plus_minus_found == 0:
                                if (self.dc == 0) and (minSova < 1.65 and minRRawBERATI < 4.6): # No resolution, reduce n_writes:
                                   if self.n_writes == 3000:
                                      self.n_writes = 1000
                                   elif self.n_writes == 1000:
                                      self.n_writes = 500
                                   elif self.n_writes == 500:
                                      self.n_writes = 100
                                   elif self.n_writes == 100:
                                      # minSova remains <= 1.65 even at lowest n_writes and dc, let it be, continue to test for other Osa values.
                                      dc_plus_minus_found = 1
                                      dc_str_counter = 1
                                      #if (self.headvendor == 'RHO'):
                                         #self.dc = 7
                                      #else:
                                         #self.dc = 35
                                      objMsg.printMsg('n_writes=100, minSova is still <= 1.65. Set n_writes = 100, dc = %d to run on other OSA.' % (self.dc) )
                                   else:
                                      self.n_writes = 100
                                   objMsg.printMsg('1111. DC=0 & minSova < 1.65 and minRRawBERATI < 4.6. Updated n_writes:%s,self.dc:%s' % (self.n_writes,self.dc))   
                                else:
                                   dc_plus_minus_found = 1
                                   objMsg.printMsg('1111. minSova >= 1.65 OR minRRawBERATI >= 4.6. self.dc:%s, n_writes:%s' % (self.dc,self.n_writes))
                                   continue
                                   #self.dc = self.dc + (2*dc_plus_minus_step)
                                   #self.dc = self.dc + dc_plus_minus_step
                                   #if (self.dc == 0):
                                      #if (self.headvendor == 'RHO'): # First DC increment step is different. HWY requires big jump.
                                         #self.dc = self.dc + 7
                                      #else:
                                         #self.dc = self.dc + 35
                                   #else:
                                      #self.dc = self.dc + 7
                                   
                             

                          objMsg.printMsg('new self.dc: %d, self.n_writes: %d' % (self.dc, self.n_writes))
                          #objMsg.printMsg('new self.prev_dc: %d' % (self.prev_dc))
                          if 0 : #self.dc < 0 and self.n_writes == 100 and OsaFound == 0:
                                #if endOsaLoop == 1: #Osa is not found. endOsaLoop=1 -> 2 top Osa is present. 
                                   #OsaFound = (maxminOsa + maxminOsa2) / 2
                                #else: #Osa cannot be found. Thus set to default.
                                   #Def_Triplet = list(TP.VbarWpTable[self.__dut.PREAMP_TYPE]['ALL'][2])#(Iw, Ovs, Ovd)
                                OsaFound = sorted(osalistSorted)[len(osalistSorted)//2]
                                endOsaLoop = 1
                                self.dc = self.prev_dc
                                objMsg.printMsg('555555. new DC is %d! Osa cannot be optimized! Osa default to %d (OsaFound).' % (self.dc, OsaFound))
                                objMsg.printMsg('mmtdatadump_osa_t51_report hd %d zn %d FINAL OSA %d IS FOUND!' % (hd,zn,OsaFound))
                                #if not OsaFound in osaKneePointTable[hd][zn][Osd].keys():
                                   #osaKneePointTable[hd][zn][Osd][OsaFound]={}
                                   #osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] = (osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP']+osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'])/2 
                                   #osaKneePointTable[hd][zn][Osd][OsaFound]['dc'] = osaKneePointTable[hd][zn][Osd][OsaFound]['dc']
                                   #osaKneePointTable[hd][zn][Osd][OsaFound]['dc'] = osaKneePointTable[hd][zn][Osd][OsaFound]['dc']
                                   #osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP_dc'] = osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] + osaKneePointTable[hd][zn][Osd][OsaFound]['dc']
                                   #osaKneePointTable[hd][zn][Osd][OsaFound]['RRAW_BER_STE'] = -1
                                   #osaKneePointTable[hd][zn][Osd][OsaFound]['RRAW_BER_ATI'] = -1
                                osaKneePointTable[hd][zn][Osd][OsaFound]['FINAL_OSA'] = OsaFound

                                findUBIwReq = 1
                                finalOsaTable[hd][zn]['Osa'] = OsaFound
                                finalOsaTable[hd][zn]['Osd'] = Osd
                                finalOsaTable[hd][zn]['IwUB'] = 999 # Found Osa, set 999 to exit module.
                                finalOsaTable[hd][zn]['dc_found'] = self.dc
                                finalOsaTable[hd][zn]['n_writes_found'] = self.n_writes
                                finalOsaTable[hd][zn].update(osaKneePointTable[hd][zn][Osd][OsaFound])
                                #objMsg.printMsg('555555. osaKneePointTable:%s' % (osaKneePointTable))
                                #objMsg.printMsg('555555. finalOsaTable:%s' % (finalOsaTable)) 
                          else: #  self.dc >= 0
                             # Add new DC and info to dictionary:      
                             dc_str = 'dc'
                             n_writes_str = 'n_writes'
                             IwKP_dc_str = 'IwKP_dc'
                             RRAW_BER_ati_str = 'RRAW_BER_ATI'
                             RRAW_BER_ste_str = 'RRAW_BER_STE'
                             IwLB_dc_str = 'IwLB_dc'
                             IwLB_STE_str = 'IwLB_STE'
                             IwLB_ATI_str = 'IwLB_ATI'
                             if not (self.dc == 0):
                                dc_str_counter = dc_str_counter + 1
                                dc_str = dc_str + str(dc_str_counter) #'dc2'
                                n_writes_str = n_writes_str + str(dc_str_counter)
                                IwKP_dc_str = IwKP_dc_str + str(dc_str_counter) #'IwKP_dc2'
                                RRAW_BER_ati_str = RRAW_BER_ati_str + str(dc_str_counter) #'RRAW_BER_ATI2'
                                RRAW_BER_ste_str = RRAW_BER_ste_str + str(dc_str_counter) #'RRAW_BER_STE2'
                                IwLB_dc_str = IwLB_dc_str + str(dc_str_counter)
                                IwLB_STE_str = IwLB_STE_str + str(dc_str_counter)
                                IwLB_ATI_str = IwLB_ATI_str + str(dc_str_counter) 
                             #objMsg.printMsg('1111. new dc_str: %s' % (dc_str))
                             #objMsg.printMsg('1111. new n_writes_str: %s' % (n_writes_str))
                             #objMsg.printMsg('1111. new IwKP_dc_str: %s' % (IwKP_dc_str))
                             #objMsg.printMsg('1111. new RRAW_BER_ati_str: %s' % (RRAW_BER_ati_str))
                             #objMsg.printMsg('1111. new RRAW_BER_ste_str: %s' % (RRAW_BER_ste_str))
                             #objMsg.printMsg('1111. new IwLB_dc_str: %s' % (IwLB_dc_str))
                             #objMsg.printMsg('1111. new IwLB_STE_str: %s' % (IwLB_STE_str))
                             #objMsg.printMsg('1111. new IwLB_ATI_str: %s' % (IwLB_ATI_str))
                          
                             #if IwLBFound:
                                #osaKneePointTable[hd][zn][Osd][OsaFound][dc_str] = self.dc
                                #osaKneePointTable[hd][zn][Osd][OsaFound][n_writes_str] = self.n_writes
                                #osaKneePointTable[hd][zn][Osd][OsaFound][IwLB_dc_str] = osaKneePointTable[hd][zn][Osd][OsaFound]['IwLB'] + self.dc
                                #osaKneePointTable[hd][zn][Osd][OsaFound][IwLB_ATI_str] = -1 #Initialize to -1.
                                #osaKneePointTable[hd][zn][Osd][OsaFound][IwLB_STE_str] = -1 #Initialize to -1.
                             #elif endOsaLoop == 1: # Highest two Osa are found!
                                #osaKneePointTable[hd][zn][Osd][maxminOsa][dc_str] = self.dc
                                #osaKneePointTable[hd][zn][Osd][maxminOsa][n_writes_str] = self.n_writes
                                #osaKneePointTable[hd][zn][Osd][maxminOsa][IwKP_dc_str] = osaKneePointTable[hd][zn][Osd][maxminOsa]['IwKP'] + self.dc
                                #osaKneePointTable[hd][zn][Osd][maxminOsa][RRAW_BER_ati_str] = -1 #Initialize to -1.
                                #osaKneePointTable[hd][zn][Osd][maxminOsa][RRAW_BER_ste_str] = -1 #Initialize to -1.
                                #osaKneePointTable[hd][zn][Osd][maxminOsa2][dc_str] = self.dc
                                #osaKneePointTable[hd][zn][Osd][maxminOsa2][n_writes_str] = self.n_writes
                                #osaKneePointTable[hd][zn][Osd][maxminOsa2][IwKP_dc_str] = osaKneePointTable[hd][zn][Osd][maxminOsa2]['IwKP'] + self.dc
                                #osaKneePointTable[hd][zn][Osd][maxminOsa2][RRAW_BER_ati_str] = -1 #Initialize to -1.
                                #osaKneePointTable[hd][zn][Osd][maxminOsa2][RRAW_BER_ste_str] = -1 #Initialize to -1.
                                #objMsg.printMsg('333. new maxminOsa DC, %s:%d' % (dc_str, osaKneePointTable[hd][zn][Osd][maxminOsa][dc_str]))
                                #objMsg.printMsg('333. new maxminOsa n_writes, %s:%d' % (n_writes_str, osaKneePointTable[hd][zn][Osd][maxminOsa][n_writes_str]))
                                #objMsg.printMsg('333. new maxminOsa IwKP_dc, %s:%d' % (IwKP_dc_str, osaKneePointTable[hd][zn][Osd][maxminOsa][IwKP_dc_str]))
                                #objMsg.printMsg('333. new maxminOsa2 DC, %s:%d' % (dc_str, osaKneePointTable[hd][zn][Osd][maxminOsa2][dc_str]))
                                #objMsg.printMsg('333. new maxminOsa2 n_writes, %s:%d' % (n_writes_str, osaKneePointTable[hd][zn][Osd][maxminOsa2][n_writes_str]))
                                #objMsg.printMsg('333. new maxminOsa2 IwKP_dc, %s:%d' % (IwKP_dc_str, osaKneePointTable[hd][zn][Osd][maxminOsa2][IwKP_dc_str]))
                             #elif dc_n_writes_found == 0:
                                #objMsg.printMsg('333.. osalistSorted= %s' % (osalistSorted))
                                #objMsg.printMsg('333.. self.dc= %d' % (self.dc))
                                #objMsg.printMsg('333.. self.n_writes= %d' % (self.n_writes))
                                #for Osa in osalistSorted:
                                   #if not OsaFound in osaKneePointTable[hd][zn][Osd].keys():
                             #else:
                                #objMsg.printMsg('333. self.osaLoopList= %s' % (self.osaLoopList))
                                #for Osa in self.osaLoopList:
                                   #osaKneePointTable[hd][zn][Osd][Osa][dc_str] = self.dc
                                   #osaKneePointTable[hd][zn][Osd][Osa][n_writes_str] = self.n_writes
                                   #osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str] = osaKneePointTable[hd][zn][Osd][Osa]['IwKP'] + self.dc
                                   #osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ati_str] = -1 #Initialize to -1.
                                   #osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ste_str] = -1 #Initialize to -1.
                                   #objMsg.printMsg('333. new DC, %s:%d' % (dc_str, osaKneePointTable[hd][zn][Osd][Osa][dc_str]))
                                   #objMsg.printMsg('333. new n_writes, %s:%d' % (n_writes_str, osaKneePointTable[hd][zn][Osd][Osa][n_writes_str]))
                                   #objMsg.printMsg('333. new IwKP_dc, %s:%d' % (IwKP_dc_str, osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str]))
                                #objMsg.printMsg('333. osaKneePointTable= %s' % (osaKneePointTable))
                             
                             
                       # Print table:
                       #objMsg.printMsg('finalOsaTable2:%s' % (finalOsaTable))
                       #objMsg.printMsg('osaKneePointTable2:%s' % (osaKneePointTable))
                       #objMsg.printMsg('dc_str_counter:%s' % (dc_str_counter))
                       # Print osaKneePointTable at the end of each DC while loop:
                       

                       # power cycle to refresh working heater:
                       #from PowerControl import objPwrCtrl
                       #objPwrCtrl.powerCycle(5000,12000,10,30)
                       #objPwrCtrl = None  # Allow GC


      objMsg.printMsg("27287 osaKneePointTable= %s" %(osaKneePointTable))                  
      objMsg.printMsg("finalOsaTable= %s" %(finalOsaTable))
      header_str = 'mmtdatadump_osa_t51_report Hd\tZn\tOd_fitted\tOa\tIwKP\tDC\tn_writes\tIwKP+DC\tRRAW_BER_ATI\tRRAW_BER_STE'
      header_str_arr = []
      for hd in self.headRange:
         for zn in testzonelist:
            for Osd in osaKneePointTable[hd][zn]:
               for Osa in osaKneePointTable[hd][zn][Osd]: 
                           dc_str_counter_all_heads = max(dc_str_counter_all_heads, 15)
                           for cnt in [2]: #Hardcode 2 to print only dc plus #range(2,10):
                              dc_str = 'dc' + str(cnt)
                              if dc_str in osaKneePointTable[hd][zn][Osd][Osa].keys():
                                 if not dc_str in header_str_arr:
                                    header_str_arr.append(dc_str)
                                    header_str = header_str + '\tDC'+str(cnt)+'\tn_writes'+str(cnt)+'\tIwKP+DC'+str(cnt)+'\tRRAW_BER_ATI'+str(cnt)+'\tRRAW_BER_STE'+str(cnt)
      header_str = header_str + '\t-DC'+'\tIwKP-DC'+'\tRRAW_BER_ATI-DC'+'\tRRAW_BER_STE-DC'+'\tSova_avg'+'\tOtf_avg'
      objMsg.printMsg('%s' % (header_str))

                          
      for hd in self.headRange:
         for zn in testzonelist:
            for Osd in osaKneePointTable[hd][zn]:
               self.osaLoopList = [] 
               data_str_arr = []
               for Osa in osaKneePointTable[hd][zn][Osd]:
                  self.osaLoopList.append(Osa)
                  self.osaLoopList.sort()
               for Osa in self.osaLoopList:
                                    data_str = str(hd) + ' \t' + str(zn) + '\t' + str(Osd) + '       \t' + str(Osa) + '\t'
                                    data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['IwKP']) + '  \t'
                                    if 'dc' in osaKneePointTable[hd][zn][Osd][Osa].keys():
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['dc']) + '\t'
                                    else:
                                       data_str = data_str + str(-1)+ '\t'
                                    if 'n_writes' in osaKneePointTable[hd][zn][Osd][Osa].keys():
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['n_writes']) + '\t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc']) + '     \t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI']) + '        \t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE']) + '        \t'
                                    else:
                                       data_str = data_str + str(-1)+ '\t'
                                       data_str = data_str + str(-1)+ '     \t'
                                       data_str = data_str + str(-1)+ '        \t'
                                       data_str = data_str + str(-1)+ '        \t'
                                    for cnt in [2]: #Hardcode 2 to print only dc plus #range(2,10):
                                          dc_str = 'dc' + str(cnt)
                                          n_writes_str = 'n_writes' + str(cnt)
                                          IwKP_dc_str = 'IwKP_dc' + str(cnt)
                                          RRAW_BER_ati_str = 'RRAW_BER_ATI' + str(cnt)
                                          RRAW_BER_ste_str = 'RRAW_BER_STE' + str(cnt)
                                          if dc_str in osaKneePointTable[hd][zn][Osd][Osa].keys():
                                             #if not dc_str in data_str_arr:
                                                #data_str_arr.append(dc_str) 
                                                data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa][dc_str]) + '\t'
                                                data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa][n_writes_str]) + '    \t'
                                                if osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str] > 127:
                                                   osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str]=127
                                                data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa][IwKP_dc_str]) + '      \t'
                                                data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ati_str]) + '        \t'
                                                data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ste_str]) + '         \t'
                                          else:
                                                data_str = data_str + str(-1) + '\t' + str(-1) + '      \t' + str(-1) + '        \t' + str(-1) + '         \t' + str(-1) + '         \t' 
                                    if 'minus_dc' in osaKneePointTable[hd][zn][Osd][Osa].keys():
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['minus_dc']) + '\t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['IwKP_minus_dc']) + '\t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI_minus_dc']) + '\t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE_minus_dc']) + '\t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['Sova_avg']) + '\t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['Otf_avg'])
                                    objMsg.printMsg('mmtdatadump_osa_t51_report %s' % (data_str))

      return finalOsaTable

   # Created a new function optimize_osa_t51 to replace the old one opOSAusingT51 since MMT has evolved drastically since the start of 2015:
   def optimize_osa_t51 (self, testzonelist, osaKneePointTable, iwlist, IwLBFound):
      oProc = CProcess()
      
      iwstep = TP.mmt_iwstep
      self.n_writes = TP.mmt_n_writes #1000
      self.dc = TP.mmt_dc_start_value #0
      self.prev_dc = TP.mmt_dc_start_value #0

      # A return dictionary that stores the final result:
      #finalOsaTable={}
      #for hd in self.headRange:
         #finalOsaTable[hd] = {}
         #for zn in testzonelist:
            #finalOsaTable[hd][zn] = {}

      # Sort Osa:
      osalistSorted = []
      for hd in self.headRange:
         for zn in testzonelist:
            for Osd in osaKneePointTable[hd][zn]:
               for Osa in osaKneePointTable[hd][zn][Osd]:
                  if not Osa in osalistSorted:
                     osalistSorted.append(Osa)
      osalistSorted.sort()
      osastep = osalistSorted[1]-osalistSorted[0]

      # Initialize working variables:
      OsaFound = 0
      loop_count = 3000
      optimal_n_writes_found = 0

      for hd in self.headRange:
         for zn in testzonelist:
            for Osd in osaKneePointTable[hd][zn]:
               for Osa in osalistSorted:
                  # The osaKneePointTable dictionary that was resulted from the previous function, findingKneePoint, may reveal the condition of a drive.
                  # Check for unmeasurable zone:
                  # If any of the OSA KP is -2 (unmeasurable), set OSA to default.
                  if osaKneePointTable[hd][zn][Osd][Osa]['IwKP'] == -2:
                     OsaFound = (self.Def_Triplet[1])#(Iw, Ovs, Ovd)
                     objMsg.printMsg('H%d Z%d has unmeasurable Sova. Set OSA to default %s. Exit module...' % (hd,zn,str(OsaFound))) 
                     osaKneePointTable[hd][zn][Osd]['FINAL_OSA'] = {}
                     osaKneePointTable[hd][zn][Osd]['FINAL_OSA'] = OsaFound
                     break
               # Entry of the main routine:
               # Start T51 OSA optimization with smallest Osa:
               if not 'FINAL_OSA' in osaKneePointTable[hd][zn][Osd].keys():
                  Osa = min(osalistSorted)
                  # Find an optimal T51 n_writes setting to be used:
                  optimal_n_writes_found = 0
                  self.n_writes = TP.mmt_n_writes
                  self.dc = 0
                  while (optimal_n_writes_found == 0):
                     osaKneePointTable[hd][zn][Osd][Osa]['dc'] = self.dc
                     osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc'] = min(osaKneePointTable[hd][zn][Osd][Osa]['IwKP'] + self.dc, 127)
                     osaKneePointTable[hd][zn][Osd][Osa]['n_writes'] = self.n_writes
                     objMsg.printMsg("************* Find an optimal n_writes setting to be used for H%d Z%d in T51 OSA optimization *************" % (hd,zn))
                     objMsg.printMsg('dc (%d) & n_writes (%d): Head %2d, Zone %2d, Osd:%2d, Osa:%2d, IwKP:%2d, DC:%2d, IwKP+dc:%2d.' \
                                     % (self.dc,self.n_writes,hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['IwKP'],self.dc,osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc'])) 
                     objMsg.printMsg("********************************************************************************************")
                     minRRawBERATI, minRRawBERSTE, minSova = self.getMinRRawBER_T51(hd, zn, Osd, Osa, osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc'], loop_count, self.n_writes,3)
                     loop_count += 1
                     if (minSova < 1.65 and minRRawBERATI < 4.6): # No resolution, reduce n_writes to retry T51:
                        if self.n_writes == 3000:
                           self.n_writes = 1000
                        elif self.n_writes == 1000:
                           self.n_writes = 500
                        elif self.n_writes == 500:
                           self.n_writes = 100
                        elif self.n_writes == 100:
                           # minSova & minRRawBERATI remains <= 1.65 even at lowest n_writes, let it be, continue to test for other Osa values.
                           optimal_n_writes_found = 1
                           objMsg.printMsg('n_writes=100, minSova < 1.65 and minRRawBERATI < 4.6. Set n_writes = 100, dc = %d to run on other OSA.' % (self.dc) )
                     else:
                        optimal_n_writes_found = 1
                        objMsg.printMsg('1111. minSova >= 1.65 OR minRRawBERATI >= 4.6. self.dc:%s, n_writes:%s' % (self.dc,self.n_writes))

                  # Update dictionary to track info:
                  osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI'] = minRRawBERATI
                  osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE'] = minSova

                  # After n_writes setting can be determined, proceed to test on 2 stress points on every Osa.
                  # First stress point is at DC=0, and second stress point is at DC=TP.mmt_dc_plus_value.
                  for Osa in osalistSorted:
                     # DC @ 0:
                     self.dc = 0
                     osaKneePointTable[hd][zn][Osd][Osa]['dc'] = self.dc
                     osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc'] = min(osaKneePointTable[hd][zn][Osd][Osa]['IwKP'] + self.dc, 127)
                     osaKneePointTable[hd][zn][Osd][Osa]['n_writes'] = self.n_writes
                     objMsg.printMsg("**********************************************************************************")
                     objMsg.printMsg('DC @ 0: Head %2d, Zone %2d, Osd:%2d, Osa:%2d, IwKP:%2d, DC:%2d, n_writes:%d, IwKP+dc:%2d.' \
                                 % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['IwKP'],osaKneePointTable[hd][zn][Osd][Osa]['dc'],\
                                 osaKneePointTable[hd][zn][Osd][Osa]['n_writes'],osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc'])) 
                     objMsg.printMsg("**********************************************************************************")
                     meas_flag = 0
                     if 'RRAW_BER_ATI' in osaKneePointTable[hd][zn][Osd][Osa].keys():
                        if not osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI'] == -1:
                           objMsg.printMsg('Data for DC@0 is already available. Do not re-run T51.')
                           minRRawBERATI = osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI']
                           minSova = osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE']
                           objMsg.printMsg('min ATI RRAW_BER:%0.2f' % (osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI']))
                           objMsg.printMsg('min ATI BITS_IN_ERROR_BER:%0.2f' % (osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE']))
                        else:
                           meas_flag = 1
                     else:
                        meas_flag = 1
                     if meas_flag == 1:
                        minRRawBERATI, minRRawBERSTE, minSova = self.getMinRRawBER_T51(hd, zn, Osd, Osa, osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc'], loop_count, self.n_writes,3)
                        loop_count += 1
                        # Update dictionary to track info:
                        osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI'] = minRRawBERATI
                        osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE'] = minSova

                     # @ DC plus
                     # Every wafer, head and media configuration may require different DC shift upwards in the higher Iw region to run T51. 
                     self.dc = TP.mmt_dc_plus_value
                     # Update to use dictionary key 'dc2', 'IwKP_dc2' instead of 'dc', 'IwKP_dc' etc. so that proper tracking is in place.
                     osaKneePointTable[hd][zn][Osd][Osa]['dc2'] = self.dc
                     osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc2'] = min(osaKneePointTable[hd][zn][Osd][Osa]['IwKP'] + self.dc, 127)
                     osaKneePointTable[hd][zn][Osd][Osa]['n_writes2'] = self.n_writes
                     objMsg.printMsg("**********************************************************************************")
                     objMsg.printMsg('DC plus: Head %2d, Zone %2d, Osd:%2d, Osa:%2d, IwKP:%2d, DC:%2d, n_writes:%d, IwKP+dc:%2d.' \
                                     % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['IwKP'],osaKneePointTable[hd][zn][Osd][Osa]['dc2'],\
                                     osaKneePointTable[hd][zn][Osd][Osa]['n_writes2'],osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc2'])) 
                     objMsg.printMsg("**********************************************************************************")
                     minRRawBERATI_plus, minRRawBERSTE_plus, minSova_plus = self.getMinRRawBER_T51(hd, zn, Osd, Osa, osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc2'], loop_count, self.n_writes,3)
                     loop_count += 1
                     # Update dictionary to track info:
                     osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI2'] = minRRawBERATI_plus
                     osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE2'] = minSova_plus

                     # Taking average of err rate at 2x locations ie DC=0 and DC plus:
                     osaKneePointTable[hd][zn][Osd][Osa]['Sova_avg'] = (minSova + minSova_plus )/2
                     osaKneePointTable[hd][zn][Osd][Osa]['Otf_avg'] = (minRRawBERATI + minRRawBERATI_plus )/2
                     objMsg.printMsg("**********************************************************************************")
                     objMsg.printMsg('Average err rate H%d Z%d Osd%d Osa%d @ IwKP+DC0, IwKP+DCplus: Sova_avg=%0.4f, Otf_avg=%0.4f' % (hd,zn,Osd,Osa,osaKneePointTable[hd][zn][Osd][Osa]['Sova_avg'],osaKneePointTable[hd][zn][Osd][Osa]['Otf_avg']))
                     objMsg.printMsg("**********************************************************************************")

                  # Check if an additional fine tune step is required:
                  # Check if there is only 1 highest min RRAW_BER, and if its adjacent osa is the second highest min RRAW_BER and there should be only 1 second highest RRAW_BER.
                  #     If there is 1 highest and 1 second highest min RRAW_BER, add an in-between Osa fine step by taking the avergae of the highest 2x Osa and re-run T51 at the fine tune step. 
                  # Also check if there are 2 highest min RRAW_BER. Add an in-between Osa fine step by taking the avergae of the highest 2x Osa and re-run T51 at the fine tune step. 
                  avgFlag = 0
                  minRRawBERATIList = []
                  minSovaATIList = []
                  for Osa in osalistSorted:
                     minRRawBERATIList.append((osaKneePointTable[hd][zn][Osd][Osa]['Otf_avg'], Osa))
                     minSovaATIList.append((osaKneePointTable[hd][zn][Osd][Osa]['Sova_avg'], Osa))
                     #minSovaATIDict[Osa] = osaKneePointTable[hd][zn][Osd][Osa][RRAW_BER_ste_str]
                  minRRawBERATIList.sort()
                  minRRawBERATIList.reverse()
                  objMsg.printMsg('minRRawBERATIList:%s' % (minRRawBERATIList)) 
                  objMsg.printMsg('minSovaATIList:%s' % (minSovaATIList)) 
                  # eg: minRRawBERATIList:[(4.615, 4), (4.805, 10), (4.81, 16), (5.355, 22), (4.85, 28)]
                  # after reverse: [(5.355, 22), (4.85, 28), (4.81, 16), (4.805, 10), (4.615, 4)]
                  topOsa = minRRawBERATIList[0][1]
                  top2Osa = minRRawBERATIList[1][1]
                  topOtf = minRRawBERATIList[0][0]
                  top2Otf = minRRawBERATIList[1][0]
                  top3Otf = minRRawBERATIList[2][0]
                  # 1st == 2nd and 2nd != 3rd: 2 highest min RRAW_BER:
                  if (round(topOtf,4) == round(top2Otf,4)) and (not round(top2Otf,4) == round(top3Otf,4)):
                     objMsg.printMsg('2 top distinct Osa Otf are found.') 
                     objMsg.printMsg('topOtf(%0.4f)=top2Otf(%0.4f) and top2Otf(%0.4f)!=top3Otf(%0.4f)' % (round(topOtf,4),round(top2Otf,4),round(top2Otf,4),round(top3Otf,4)))
                     if abs(topOsa - top2Osa) == osastep: # check for adjacent Osa 
                        avgOsa = (topOsa + top2Osa)/2
                        objMsg.printMsg('And these 2 Osa (%d & %d) are adjacent to each other, thus take an additional fine tune step between them (OSA=%d).' % (topOsa, top2Osa, avgOsa))
                        avgFlag = 1
                     else:
                        objMsg.printMsg('BUT these 2 Osa (%d & %d) are NOT adjacent to each other. No additional fine tune step is required.' % (topOsa, top2Osa))
                        avgFlag = 0
                  # 1st != 2nd and 2nd != 3rd: 1 highest and 1 second highest min RRAW_BER:
                  elif (not round(topOtf,4) == round(top2Otf,4)) and (not round(top2Otf,4) == round(top3Otf,4)):
                     objMsg.printMsg('2 top distinct Osa Otf are found.') 
                     objMsg.printMsg('topOtf(%0.4f)!=top2Otf(%0.4f) and top2Otf(%0.4f)!=top3Otf(%0.4f)' % (round(topOtf,4),round(top2Otf,4),round(top2Otf,4),round(top3Otf,4)))
                     if abs(topOsa - top2Osa) == osastep: # check for adjacent Osa 
                        avgOsa = (topOsa + top2Osa)/2
                        objMsg.printMsg('And these 2 Osa (%d & %d) are adjacent to each other, thus take an additional fine tune step between them (OSA=%d).' % (topOsa, top2Osa, avgOsa))
                        avgFlag = 1
                     else:
                        objMsg.printMsg('BUT these 2 Osa (%d & %d) are NOT adjacent to each other. No additional fine tune step is required.' % (topOsa, top2Osa))
                        avgFlag = 0
                  else:
                     avgFlag = 0
                     objMsg.printMsg('No 2 disctinct highest otf. No additional fine tune step is required.')

                  if avgFlag == 1:
                     #avgOsa = (topOsa + top2Osa)/2
                     # Fine tune for DC @ 0:
                     osaKneePointTable[hd][zn][Osd][avgOsa] = {}
                     osaKneePointTable[hd][zn][Osd][avgOsa]['dc'] = osaKneePointTable[hd][zn][Osd][topOsa]['dc']
                     osaKneePointTable[hd][zn][Osd][avgOsa]['IwKP'] = min((osaKneePointTable[hd][zn][Osd][topOsa]['IwKP']+osaKneePointTable[hd][zn][Osd][top2Osa]['IwKP'])/2, 127)
                     osaKneePointTable[hd][zn][Osd][avgOsa]['IwKP_dc'] = osaKneePointTable[hd][zn][Osd][avgOsa]['IwKP'] + osaKneePointTable[hd][zn][Osd][avgOsa]['dc']
                     osaKneePointTable[hd][zn][Osd][avgOsa]['n_writes'] = osaKneePointTable[hd][zn][Osd][topOsa]['n_writes']
                     objMsg.printMsg("**********************************************************************************")
                     objMsg.printMsg('Fine step @ DC=0: Head %2d, Zone %2d, Osd:%2d, Osa:%2d, IwKP:%2d, DC:%2d, n_writes:%d, IwKP+dc:%2d.' \
                                     % (hd,zn,Osd,avgOsa,osaKneePointTable[hd][zn][Osd][avgOsa]['IwKP'],osaKneePointTable[hd][zn][Osd][avgOsa]['dc'],\
                                     osaKneePointTable[hd][zn][Osd][avgOsa]['n_writes'],osaKneePointTable[hd][zn][Osd][avgOsa]['IwKP_dc'])) 
                     objMsg.printMsg("**********************************************************************************")
                     minRRawBERATI_fine, minRRawBERSTE_fine, minSova_fine = self.getMinRRawBER_T51(hd, zn, Osd, avgOsa, osaKneePointTable[hd][zn][Osd][avgOsa]['IwKP_dc'], loop_count, osaKneePointTable[hd][zn][Osd][avgOsa]['n_writes'],3)
                     loop_count += 1
                     # Update dictionary to track info:
                     osaKneePointTable[hd][zn][Osd][avgOsa]['RRAW_BER_ATI'] = minRRawBERATI_fine
                     osaKneePointTable[hd][zn][Osd][avgOsa]['RRAW_BER_STE'] = minSova_fine
                     # Fine tune for DC plus:
                     osaKneePointTable[hd][zn][Osd][avgOsa]['dc2'] = osaKneePointTable[hd][zn][Osd][topOsa]['dc2']
                     osaKneePointTable[hd][zn][Osd][avgOsa]['IwKP_dc2'] = min(osaKneePointTable[hd][zn][Osd][avgOsa]['IwKP']+osaKneePointTable[hd][zn][Osd][avgOsa]['dc2'], 127)
                     osaKneePointTable[hd][zn][Osd][avgOsa]['n_writes2'] = osaKneePointTable[hd][zn][Osd][topOsa]['n_writes2']
                     objMsg.printMsg("**********************************************************************************")
                     objMsg.printMsg('Fine step @ DC plus: Head %2d, Zone %2d, Osd:%2d, Osa:%2d, IwKP:%2d, DC:%2d, n_writes:%d, IwKP+dc:%2d.' \
                                     % (hd,zn,Osd,avgOsa,osaKneePointTable[hd][zn][Osd][avgOsa]['IwKP'],osaKneePointTable[hd][zn][Osd][avgOsa]['dc2'],\
                                     osaKneePointTable[hd][zn][Osd][avgOsa]['n_writes2'],osaKneePointTable[hd][zn][Osd][avgOsa]['IwKP_dc2'])) 
                     objMsg.printMsg("**********************************************************************************")
                     minRRawBERATI_fine_plus, minRRawBERSTE_fine_plus, minSova_fine_plus = self.getMinRRawBER_T51(hd, zn, Osd, avgOsa, osaKneePointTable[hd][zn][Osd][avgOsa]['IwKP_dc2'], loop_count, osaKneePointTable[hd][zn][Osd][avgOsa]['n_writes2'],3)
                     loop_count += 1
                     # Update dictionary to track info:
                     osaKneePointTable[hd][zn][Osd][avgOsa]['RRAW_BER_ATI2'] = minRRawBERATI_fine_plus
                     osaKneePointTable[hd][zn][Osd][avgOsa]['RRAW_BER_STE2'] = minSova_fine_plus

                     # Taking average of err rate at 2x locations ie DC=0 and DC plus:
                     osaKneePointTable[hd][zn][Osd][avgOsa]['Sova_avg'] = (minSova_fine + minSova_fine_plus )/2
                     osaKneePointTable[hd][zn][Osd][avgOsa]['Otf_avg'] = (minRRawBERATI_fine + minRRawBERATI_fine_plus )/2
                     objMsg.printMsg("**********************************************************************************")
                     objMsg.printMsg('Fine step: Average err rate @ IwKP+DC0, IwKP+DCplus: Sova_avg=%0.4f, Otf_avg=%0.4f' % (osaKneePointTable[hd][zn][Osd][avgOsa]['Sova_avg'],osaKneePointTable[hd][zn][Osd][avgOsa]['Otf_avg']))
                     objMsg.printMsg("**********************************************************************************")

                     # Select the best Osa among topOsa, top2Osa & avgOsa:
                     fineStepOtfList = []
                     RRAW_BER_scounter = 0
                     fineStepOtfList.append((topOtf, topOsa))
                     fineStepOtfList.append((top2Otf, top2Osa))
                     fineStepOtfList.append((osaKneePointTable[hd][zn][Osd][avgOsa]['Otf_avg'], avgOsa))
                     fineStepOtfList.sort()
                     fineStepOtfList.reverse()
                     objMsg.printMsg('555..1. fineStepOtfList:%s' % str(fineStepOtfList))
                     topOsa = fineStepOtfList[0][1]
                     top2Osa = fineStepOtfList[1][1]
                     topOtf = fineStepOtfList[0][0]
                     top2Otf = fineStepOtfList[1][0]
                     maxOtf, maxOsa = max(fineStepOtfList)
                     for iOtf, iOsa in fineStepOtfList:
                        if round(iOtf,4) == round(topOtf,4):
                           RRAW_BER_scounter += 1
                     objMsg.printMsg('555..1. RRAW_BER_scounter:%d' % (RRAW_BER_scounter))
                     if (RRAW_BER_scounter == 1): 
                        # There is only 1 highest min RRAW_BER (otf), Osa can be found.
                        # Pick only the top Osa as the final Osafound.
                        OsaFound = topOsa   
                        objMsg.printMsg('555..1. topOsa is set as OsaFound:%s' % (OsaFound))
                     elif (RRAW_BER_scounter == 2): 
                        # There is 2 highest min RRAW_BER (otf), average osa will be taken.
                        OsaFound = (topOsa + top2Osa) / 2
                        objMsg.printMsg('555..1. An avergae is taken between topOsa %d & top2Osa %d. OsaFound:%s' % (topOsa, top2Osa, OsaFound))
                        # Update dictionary to track info:
                        if not OsaFound in osaKneePointTable[hd][zn][Osd].keys():
                           osaKneePointTable[hd][zn][Osd][OsaFound] = {}
                           osaKneePointTable[hd][zn][Osd][OsaFound]['dc'] = osaKneePointTable[hd][zn][Osd][topOsa]['dc']
                           osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] = (osaKneePointTable[hd][zn][Osd][topOsa]['IwKP']+osaKneePointTable[hd][zn][Osd][top2Osa]['IwKP'])/2
                           osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP_dc'] = min(osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] + osaKneePointTable[hd][zn][Osd][OsaFound]['dc'], 127)
                           osaKneePointTable[hd][zn][Osd][OsaFound]['n_writes'] = osaKneePointTable[hd][zn][Osd][topOsa]['n_writes']
                           osaKneePointTable[hd][zn][Osd][OsaFound]['dc2'] = osaKneePointTable[hd][zn][Osd][topOsa]['dc2']
                           osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP_dc2'] = min(osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP']+osaKneePointTable[hd][zn][Osd][OsaFound]['dc2'], 127)
                           osaKneePointTable[hd][zn][Osd][OsaFound]['n_writes2'] = osaKneePointTable[hd][zn][Osd][topOsa]['n_writes2']
                     else:
                        # There is 3 highest min RRAW_BER (otf), take the middle one as the final Osa..
                        OsaFound = top2Osa
                        objMsg.printMsg('555..1. Set the middle top2Osa %d as OsaFound:%s' % (top2Osa, OsaFound))
                     osaKneePointTable[hd][zn][Osd]['FINAL_OSA'] = {}
                     osaKneePointTable[hd][zn][Osd]['FINAL_OSA'] = OsaFound
                     objMsg.printMsg('mmtdatadump_osa_t51_report hd %d zn %d FINAL OSA %d IS FOUND!' % (hd,zn,osaKneePointTable[hd][zn][Osd]['FINAL_OSA']))
                  else:
                     # Do not have any 2 distinct highest otf, sova may need to be considered.
                     # At the step, there should be 3, 4 or 5 highest otf. 
                     RRAW_BER_scounter = 0
                     osa_w_highest_ber_list = [] # A new dict to keep track of the osa that has the same highest otf value.
                     sum_osa = 0
                     for iOtf, iOsa in minRRawBERATIList:
                        if round(iOtf,4) == round(topOtf,4):
                           RRAW_BER_scounter += 1
                           osa_w_highest_ber_list.append(iOsa)
                           sum_osa += iOsa
                     objMsg.printMsg('555..2. RRAW_BER_scounter:%d' % (RRAW_BER_scounter))
                     objMsg.printMsg('555..2. osa_w_highest_ber_list (otf):%s' % str(osa_w_highest_ber_list))
                     if (RRAW_BER_scounter == 5):
                        objMsg.printMsg('555..3. Since all 5x Osa Otf have the same value, consider Sova too.')
                        # If all 5 osa have the same otf value, no resolution, sova need to be considered.
                        maxSova = 0
                        minSovaATIList2 = [] # A new list that keep track of osa with the highest sova.
                        for iOsa in osa_w_highest_ber_list:
                           #objMsg.printMsg('5555. osa_i:%s' % (osa_i))
                           for sova_j,osa_j in minSovaATIList: 
                              #objMsg.printMsg('5555. osa_j:%s' % (osa_j))
                              if iOsa == osa_j:
                                 #objMsg.printMsg('5555. osa_i == osa_j:%s' % (osa_j))
                                 if sova_j > maxSova:
                                    maxSova = sova_j
                                    OsaFound = osa_j
                                 break
                        objMsg.printMsg('555..3. Osa with maxSova:%s' % (OsaFound))
                        objMsg.printMsg('555..3. maxSova:%s' % (maxSova)) 
                        # Ensure that there is only 1 highest sova. if 2 or more sova is present, need to take an average of the osa having the same sova value.
                        sum_osa = 0
                        osa_w_highest_ber_list = [] # Reset the dict to keep track of the osa that has the same highest sova value.
                        for iSova, iOsa in minSovaATIList:
                           if round(iSova,4) == round(maxSova,4):
                              osa_w_highest_ber_list.append(iOsa)
                              sum_osa += iOsa
                        objMsg.printMsg('555..3. osa_w_highest_ber_list (sova):%s' % str(osa_w_highest_ber_list))
                        if (len(osa_w_highest_ber_list) > 1): 
                           # when RRAW_BER_scounter > 1 -> There are 2 or more highest min Sova, need to pick one out of the 2 or take an average.  
                           OsaFound = int(round((sum_osa / len(osa_w_highest_ber_list)),0))  
                           objMsg.printMsg('555..3. OsaFound after average:%s' % (OsaFound))
    
                     else:
                        # There may be 3 or 4 osa having the same otf value, take the average of these osa.
                        # Or when there is 1 highest otf, and 2 second highest otf, we will get here too. The highest Otf will be picked. 
                        OsaFound = int(round((sum_osa / len(osa_w_highest_ber_list)),0))
                        objMsg.printMsg('555..4. OsaFound after average:%s' % (OsaFound))
                     if not OsaFound in osaKneePointTable[hd][zn][Osd].keys():
                        # Update dictionary to track info:
                        iOsa = osa_w_highest_ber_list[0] # pick first osa to update.
                        osaKneePointTable[hd][zn][Osd][OsaFound] = {}
                        osaKneePointTable[hd][zn][Osd][OsaFound]['dc'] = osaKneePointTable[hd][zn][Osd][iOsa]['dc']
                        osaKneePointTable[hd][zn][Osd][OsaFound]['n_writes'] = osaKneePointTable[hd][zn][Osd][iOsa]['n_writes']
                        osaKneePointTable[hd][zn][Osd][OsaFound]['dc2'] = osaKneePointTable[hd][zn][Osd][iOsa]['dc2']
                        osaKneePointTable[hd][zn][Osd][OsaFound]['n_writes2'] = osaKneePointTable[hd][zn][Osd][iOsa]['n_writes2']
                        sum_osa = 0
                        for iOsa in osa_w_highest_ber_list:
                           sum_osa += osaKneePointTable[hd][zn][Osd][iOsa]['IwKP']
                        osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP'] = int(round((sum_osa / len(osa_w_highest_ber_list)),0))  
                        osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP_dc'] = min(osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP']+osaKneePointTable[hd][zn][Osd][OsaFound]['dc'], 127)
                        osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP_dc2'] = min(osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP']+osaKneePointTable[hd][zn][Osd][OsaFound]['dc2'], 127)
                     objMsg.printMsg('555..5. osaKneePointTable:%s' % str(osaKneePointTable))
                     osaKneePointTable[hd][zn][Osd]['FINAL_OSA'] = {}
                     osaKneePointTable[hd][zn][Osd]['FINAL_OSA'] = OsaFound
                     objMsg.printMsg('mmtdatadump_osa_t51_report hd %d zn %d FINAL OSA %d IS FOUND!' % (hd,zn,osaKneePointTable[hd][zn][Osd]['FINAL_OSA']))
               # Update the return dictionary
               #finalOsaTable[hd][zn]['Osa'] = OsaFound
               #finalOsaTable[hd][zn]['Osd'] = Osd
               #finalOsaTable[hd][zn]['IwUB'] = 999 # Found Osa, set 999 to exit module.
               #finalOsaTable[hd][zn]['dc_found'] = self.dc
               #finalOsaTable[hd][zn]['n_writes_found'] = self.n_writes
               #finalOsaTable[hd][zn].update(osaKneePointTable[hd][zn][Osd][OsaFound])

      for hd in self.headRange:
         for zn in testzonelist:
            for Osd in osaKneePointTable[hd][zn]:
               OsaFound = osaKneePointTable[hd][zn][Osd]['FINAL_OSA']
               self.finalTripletTable[hd][zn]['OSA'] = osaKneePointTable[hd][zn][Osd]['FINAL_OSA']
               if OsaFound in osaKneePointTable[hd][zn][Osd].keys():
                  self.finalTripletTable[hd][zn]['SOVA_IwKP'] = osaKneePointTable[hd][zn][Osd][OsaFound]['IwKP']
               else:
                  self.finalTripletTable[hd][zn]['SOVA_IwKP'] = -1


      objMsg.printMsg("2822 osaKneePointTable= %s" %(osaKneePointTable))  
      header_str = 'mmtdatadump_osa_t51_report Hd\tZn\tOd\tOa\tIwKP\tDC\tn_writes\tIwKP+DC\tRRAW_BER_ATI\tRRAW_BER_STE\tDC2\tn_writes2\tIwKP+DC2\tRRAW_BER_ATI2\tRRAW_BER_STE2\tSova_avg\tOtf_avg'      
      objMsg.printMsg('%s' % (header_str))

      for hd in self.headRange:
         for zn in testzonelist:
            for Osd in osaKneePointTable[hd][zn]:
               osalistSorted = [] 
               data_str_arr = []
               osalistSorted = []
               for Osa in osaKneePointTable[hd][zn][Osd]:
                  if type(Osa) is int:
                     osalistSorted.append(Osa)
                     osalistSorted.sort()
               for Osa in osalistSorted:
                                    data_str = str(hd) + '\t' + str(zn) + '\t' + str(Osd) + '\t' + str(Osa) + '\t'
                                    data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['IwKP']) + '  \t'
                                    if 'dc' in osaKneePointTable[hd][zn][Osd][Osa].keys():
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['dc']) + '\t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['n_writes']) + '\t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc']) + '     \t'
                                    else:
                                       data_str = data_str + str(-1)+ '\t'
                                       data_str = data_str + str(-1)+ '\t'
                                       data_str = data_str + str(-1)+ '     \t'
                                    if 'RRAW_BER_ATI' in osaKneePointTable[hd][zn][Osd][Osa].keys():
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI']) + '        \t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE']) + '        \t'
                                    else:
                                       data_str = data_str + str(-1)+ '        \t'
                                       data_str = data_str + str(-1)+ '        \t'
                                    if 'dc2' in osaKneePointTable[hd][zn][Osd][Osa].keys():
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['dc2']) + '\t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['n_writes2']) + '\t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['IwKP_dc2']) + '     \t'
                                    else:
                                       data_str = data_str + str(-1)+ '\t'
                                       data_str = data_str + str(-1)+ '\t'
                                       data_str = data_str + str(-1)+ '     \t'
                                    if 'RRAW_BER_ATI2' in osaKneePointTable[hd][zn][Osd][Osa].keys():
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_ATI2']) + '        \t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['RRAW_BER_STE2']) + '        \t'
                                    else:
                                       data_str = data_str + str(-1)+ '        \t'
                                       data_str = data_str + str(-1)+ '        \t'
                                    if 'Sova_avg' in osaKneePointTable[hd][zn][Osd][Osa].keys():
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['Sova_avg']) + '\t'
                                       data_str = data_str + str(osaKneePointTable[hd][zn][Osd][Osa]['Otf_avg'])
                                    else:
                                       data_str = data_str + str(-1)+ '\t'
                                       data_str = data_str + str(-1)+ '\t'
                                    objMsg.printMsg('mmtdatadump_osa_t51_report %s' % (data_str))



   def getMinRRawBER_T51(self, hd, zn, Osd, Osa, Iw, loop_count, n_writes, band_size):
      oProc = CProcess()
      import Utility
      oUtil = Utility.CUtility()
      
      minRRawBERATI = 0
      minRRawBERSTE = 0
      minSova = 0
      
      iwstep = TP.mmt_iwstep
      ati_param = oUtil.copy(TP.prm_Triplet_ATI_STE)      
      oUtil = None  # Allow GC      
      ati_param['TEST_HEAD'] = hd
      ati_param['ZONE'] = zn
      ati_param['spc_id'] = loop_count
      ati_param['CENTER_TRACK_WRITES'] = n_writes
      ati_param['CWORD2'] = 0x6
      ati_param['DAMPING'] = Osa
      ati_param['WRITE_CURRENT'] = min(Iw,127)
      ati_param['DURATION'] = Osd
      ati_param['BAND_SIZE'] = band_size
      try: oProc.St(ati_param)
      except:
         from PowerControl import objPwrCtrl
         objPwrCtrl.powerCycle(5000,12000,10,30)
         objPwrCtrl = None  # Allow GC
         try: 
            oProc.St(ati_param)
         except:
            pass

      tableData = []
      try:
         tableData = self.__dut.dblData.Tables('P051_ERASURE_BER').tableDataObj()
      except: 
         objMsg.printMsg("P051_ERASURE_BER not found!!!!!")
         pass

      startIndex = 0
      endIndex = len(tableData)

      # Find the min RRAW_BER & BITS_IN_ERROR_BER:
      if startIndex != endIndex:
         for record in range(startIndex, endIndex):
            iHead = int(tableData[record]['HD_PHYS_PSN'])
            iZone = int(tableData[record]['DATA_ZONE'])
            TEST_TYPE = tableData[record]['TEST_TYPE']
            RRAW_BER = float(tableData[record]['RRAW_BER'])
            TRK_INDEX = int(tableData[record]['TRK_INDEX'])
            BITS_IN_ERROR_BER = float(tableData[record]['BITS_IN_ERROR_BER'])
            if int(tableData[record]['SPC_ID']) == loop_count and TEST_TYPE == 'erasure':
               if  (TRK_INDEX == 1 or TRK_INDEX == -1): 
                  if (minRRawBERATI == 0):
                     minRRawBERATI = RRAW_BER
                  else:
                     if (RRAW_BER < minRRawBERATI):
                        minRRawBERATI = RRAW_BER
                  if (minSova == 0):
                     minSova = BITS_IN_ERROR_BER
                  else:
                     if (BITS_IN_ERROR_BER < minSova):
                        minSova = BITS_IN_ERROR_BER  
               else:
                  if (minRRawBERSTE == 0):
                     minRRawBERSTE = RRAW_BER
                  else:
                     if (RRAW_BER < minRRawBERSTE):
                        minRRawBERSTE = RRAW_BER
                  
      objMsg.printMsg("min ATI RRAW_BER: %0.2f" % (minRRawBERATI)) 
      objMsg.printMsg("min ATI BITS_IN_ERROR_BER: %0.2f" % (minSova))
      objMsg.printMsg("min STE RRAW_BER: %0.2f" % (minRRawBERSTE)) 
      
      return minRRawBERATI, minRRawBERSTE, minSova

   def findingKneePoint (self, testzonelist, tuningDict, tuningList, iwlist, tuningParam):
      
      oProc = CProcess()
      #import Utility
      #oUtil = Utility.CUtility()
      objMsg.printMsg("tuningDict: %s" %(tuningDict))
      objMsg.printMsg("tuningList: %s" %(tuningList))
      iwstep = TP.mmt_iwstep
      if (tuningParam == 'OSD'):
         loop_count = 0
         #tuningList.sort() 
         #tuningList.reverse() # Tune OSD in reverse order
      elif (tuningParam == 'OSA'):
         loop_count = 500
      else:
         loop_count = 1000
      
      deltaBERStop = TP.mmt_deltaBERStop #0.10
      #param250 = {'test_num' : 250, 'prm_name' : 'PrePostPhastOptiAudit_250 all zones', 'spc_id': 0, 'RETRIES': 50, 'ZONE_POSITION': 198, 'MAX_ERR_RATE': -70, 'TEST_HEAD': 255, 'NUM_TRACKS_PER_ZONE': 10, 'SKIP_TRACK': 20, 'TLEVEL': 0, 'MINIMUM': -22, 'ZONE_MASK_BANK': 0, 'timeout': 20000, 'ZONE_MASK_EXT': (0L, 0L), 'CWORD2': 5, 'MAX_ITERATION': 208, 'ZONE_MASK': (0L, 1L), 'WR_DATA': 0, 'CWORD1': 387,}
      param250 = TP.prm_PrePostOptiAudit_250_2.copy()
      
      if testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
         dbtable = 'P382_ERROR_RATE_BY_ZONE'
      else:
         dbtable = 'P250_ERROR_RATE_BY_ZONE'
      try:
         self.dut.dblData.Tables(dbtable).deleteIndexRecords(1)#del file pointers
         self.dut.dblData.delTable(dbtable)#del RAM objects
      except:
         objMsg.printMsg("table %s delete failed. " % str(dbtable))
         pass

      MMTtable={}
      Iw_knee_pt_tracker={}
      KPTable={}
      findingKneePointDict={}
      for hd in self.headRange:
         MMTtable[hd] = {}
         KPTable[hd] = {}
         findingKneePointDict[hd] = {}
         for zn in testzonelist:
            MMTtable[hd][zn] = {}
            KPTable[hd][zn] = {}
            findingKneePointDict[hd][zn] = -1
            Osa = tuningDict[hd][zn]
            MMTtable[hd][zn][Osa] = {}
            KPTable[hd][zn][Osa] = {}
            if (tuningParam == 'SOVAKNEEPT'):
               for Osd in tuningList[hd][zn]:
                  MMTtable[hd][zn][Osa][Osd] = {}
                  KPTable[hd][zn][Osa][Osd] = {}
                  KPTable[hd][zn][Osa][Osd]['IwKP'] = -1
                  #KPTable[hd][zn][Osa][Osd]['RRAW_BER_ATI'] = -1
                  #KPTable[hd][zn][Osa][Osd]['RRAW_BER_STE'] = -1
                  for Iw in iwlist:
                     MMTtable[hd][zn][Osa][Osd][Iw] = {}
                     MMTtable[hd][zn][Osa][Osd][Iw]['BER'] = 1
                     MMTtable[hd][zn][Osa][Osd][Iw]['OW'] = -1
                     MMTtable[hd][zn][Osa][Osd][Iw]['HMS'] = -1
                     MMTtable[hd][zn][Osa][Osd][Iw]['IwKP'] = -1
            else:
               for Osd in tuningList[hd][zn]:
                  MMTtable[hd][zn][Osa][Osd] = {}
                  KPTable[hd][zn][Osa][Osd] = {}
                  KPTable[hd][zn][Osa][Osd]['IwKP'] = -1
                  KPTable[hd][zn][Osa][Osd]['IwKPBER'] = 0
                  #KPTable[hd][zn][Osa][Osd]['RRAW_BER_ATI'] = -1
                  #KPTable[hd][zn][Osa][Osd]['RRAW_BER_STE'] = -1
                  for Iw in iwlist:
                     MMTtable[hd][zn][Osa][Osd][Iw] = {}
                     MMTtable[hd][zn][Osa][Osd][Iw]['BER'] = 1
                     MMTtable[hd][zn][Osa][Osd][Iw]['OW'] = -1
                     MMTtable[hd][zn][Osa][Osd][Iw]['HMS'] = -1
                     MMTtable[hd][zn][Osa][Osd][Iw]['IwKP'] = -1
      #objMsg.printMsg("initMMTtable: %s" %(MMTtable))
      #objMsg.printMsg("initKPTable: %s" %(KPTable))
            
      iwlist.sort() 
      iwlist.reverse()
      orgiwlist = iwlist

      for zn in testzonelist:
         for hd in self.headRange:
            Iw_knee_pt_tracker_flag = 0
            printTableFlag = 0
            Iw_knee_pt = 0 
            Osd_found = 0
            iwlist = orgiwlist #Reset to full iw sweeping list.

            for Osd in tuningList[hd][zn]:
               if (not findingKneePointDict[hd][zn] == -1) and (tuningParam == 'OSD' or tuningParam == 'SOVAKNEEPT'):
                  objMsg.printMsg("findingKneePointDict[%d][%d]: %d" %(hd,zn,findingKneePointDict[hd][zn]))
                  objMsg.printMsg("Continue on next head/zone loop.")
                  break
                      
               # Reset tracking variables for every Iw loop:
               printTableFlag = 0
               Iw_knee_pt_tracker_flag = 0
               Iw_knee_pt_tracker[hd] = -1 
               
               Osa = tuningDict[hd][zn]

               # For test time reduction purpose, pick a lower iw for a shorter iwlist for 2nd Osd index onwards:
               if not (tuningParam == 'SOVAKNEEPT'): 
                  # First Osd index will need to sweep all iw. 2nd Osd onwards can sweep from 2x iw away from the knee point found for first Osd.
                  if tuningList[hd][zn].index(Osd) == 0: 
                     objMsg.printMsg("iwlist sorted in reverse: %s" %(iwlist))
                  else:
                     iwlist_start = max(orgiwlist)
                     iwlist_end = min(orgiwlist)
                     iwlist_step = orgiwlist[0]-orgiwlist[1]
                     objMsg.printMsg("org iwlist_start: %d" %(iwlist_start))
                     prevOsdIndex = tuningList[hd][zn].index(Osd) - 1
                     prevOsd = tuningList[hd][zn][prevOsdIndex]
                     objMsg.printMsg("prevOsd: %d" %(prevOsd))
                     
                     prevOsdIwKP = KPTable[hd][zn][Osa][prevOsd]['IwKP']
                     objMsg.printMsg("prevOsd KP: KPTable[%d][%d][%d][%d]['IwKP']= %d" %(hd,zn,Osa,prevOsd,KPTable[hd][zn][Osa][prevOsd]['IwKP']))
                     if (tuningParam == 'OSD'):
                        if (prevOsdIwKP > 0 and prevOsdIwKP + (iwlist_step * 6) > iwlist_end) and ((prevOsdIwKP + (iwlist_step * 6)) <= max(orgiwlist)):
                           iwlist_start = prevOsdIwKP + (iwlist_step * 6) # iw start index is 3x dac higher than previously found kp.
                           objMsg.printMsg("new iwlist_start: %d" %(iwlist_start))
                     else:
                        if (prevOsdIwKP > 0 and prevOsdIwKP + (iwlist_step * 3) > iwlist_end) and ((prevOsdIwKP + (iwlist_step * 3)) <= max(orgiwlist)):
                           iwlist_start = prevOsdIwKP + (iwlist_step * 3) # iw start index is 3x dac higher than previously found kp.
                           objMsg.printMsg("new iwlist_start: %d" %(iwlist_start))
                     iwlist = range(iwlist_start,iwlist_end-1,-(iwlist_step))
                     iwlist.sort() 
                     iwlist.reverse()
                     objMsg.printMsg("New shortened iwlist sorted in reverse: %s" %(iwlist))

               if testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
                  # Loop iw in SF3 T250, so only need to pass first item in iwlist.
                  iwlist = [iwlist[0]]
                  objMsg.printMsg("Loop Iw in T250. New iwlist: %s" %(iwlist))
               for Iw in iwlist:
                  if (Iw_knee_pt_tracker[hd] == 1): # Stop when ROC is met!
                     objMsg.printMsg("Continue on next Osa/Osd loop.")
                     break

                  loop_count = loop_count + 1 #For updating spc_id.

                  objMsg.printMsg("--------------------------------------------------------------------")
                  objMsg.printMsg("-------------------- Loop Count %d, spc_id: %d --------------------" %(loop_count, loop_count))
                  objMsg.printMsg("--------------------------------------------------------------------")
                  if (tuningParam == 'SOVAKNEEPT'):
                      Osd2 = tuningList[hd][zn][0]
                      objMsg.printMsg("Head: %d, Test zone: %d, Osd: %d, Iw: %d, Osa: %d" %(hd, zn, Osd2, Iw, Osa))
                  else:
                      if (tuningParam == 'OSD'):
                         objMsg.printMsg("Head: %d, Test zone: %d, Osd: %d, Iw: %d, Osa: %d" %(hd, zn, Osd, Iw, Osa))
                      else:
                         objMsg.printMsg("Head: %d, Test zone: %d, Osd: %d, Iw: %d, Osa: %d" %(hd, zn, Osa, Iw, Osd))
                  objMsg.printMsg("Iw_knee_pt_tracker: %s" %(Iw_knee_pt_tracker))
                  objMsg.printMsg("Iw_knee_pt: %s" %(Iw_knee_pt))

                  zn_arr = []
                  zn_arr = [zn]
                  bank = zn / 64
                  tableData = []

                  param250.update({'spc_id': loop_count, 'MINIMUM': -17})
                  param250['ZONE_MASK_EXT'], param250['ZONE_MASK'] = oProc.oUtility.convertListTo64BitMask(zn_arr)
                  param250['ZONE_MASK_BANK'] = bank
                  if testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
                     param250['CWORD2'] = 0x20 
                     param250['DELTA_SPEC'] = (int) (deltaBERStop * 100) #Pass in a whole number
                  else:
                     param250['CWORD2'] = 0x8 
                  #oUtil = None  # Allow GC
    
                  if (tuningParam == 'OSD' or tuningParam == 'SOVAKNEEPT'): 
                     #tuningDict holds different Osa values. tuningList holds Osd which requires to be tuned.
                     paramOsdStr = 'DURATION'
                     paramOsaStr = 'DAMPING'
                  else: 
                     #tuningDict holds different Osd values. tuningList holds Osa which requires to be tuned.
                     paramOsdStr = 'DAMPING'
                     paramOsaStr = 'DURATION'                     
                         
                  if (tuningParam == 'SOVAKNEEPT'):
                     objMsg.printMsg("SOVAKNEEPT: Osd in for loop %d" %(Osd))
                     Osd = tuningList[hd][zn][0]
                     objMsg.printMsg("SOVAKNEEPT: Osd corrected to %d" %(Osd))

                  if (Iw_knee_pt_tracker[hd] < 2): 
                     if testSwitch.UPS_PARAMETERS:
                        param250.update({paramOsaStr: Osa, paramOsdStr: Osd, 'WrCrrnt': Iw, 'HdRg': (hd, hd), 'MxErr': TP.mmt_t250_max_err_rate,})
                     else:
                        param250.update({paramOsaStr: Osa, paramOsdStr: Osd, 'WRITE_CURRENT': Iw, 'TEST_HEAD': (hd<<8)|(hd&0xff),'MAX_ERR_RATE': TP.mmt_t250_max_err_rate,})
                     try: 
                        oProc.St(param250)
                     except:
                        pass

                  
                  try:
                     tableData = self.dut.dblData.Tables(dbtable).chopDbLog('SPC_ID', 'match',str(loop_count))
                  except: 
                     objMsg.printMsg("%s not found!!!!!", str(dbtable))
                     pass
                  if len(tableData) > 0:
                     for row in tableData:
                         iHead = int(row['HD_LGC_PSN'])
                         iZone = int(row['DATA_ZONE'])
                         iBER = float(row['RAW_ERROR_RATE'])
                         Osa = tuningDict[iHead][iZone]
                         if (tuningParam == 'SOVAKNEEPT'):
                            Osd = tuningList[iHead][iZone][0]
                         if testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
                            iWRT_CUR = int(row['WRT_CUR'])
                            MMTtable[iHead][iZone][Osa][Osd][iWRT_CUR]['BER'] = iBER
                            objMsg.printMsg("iHead: %d, iZone: %d, iBER: %f, iWRT_CUR: %d" % (iHead, iZone, iBER, iWRT_CUR))
                            objMsg.printMsg("MMTtable[%d][%d][%d][%d][%d]['BER']: %f" % (hd,zn,Osa,Osd,iWRT_CUR, MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER']))
                         else:
                            MMTtable[iHead][iZone][Osa][Osd][Iw]['BER'] = iBER
                            objMsg.printMsg("iHead: %d, iZone: %d, iBER: %f, Iw: %d" % (iHead, iZone, iBER, Iw))
                            objMsg.printMsg("MMTtable[%d][%d][%d][%d][%d]['BER']: %f" % (hd,zn,Osa,Osd,Iw, MMTtable[hd][zn][Osa][Osd][Iw]['BER']))
                  ### Finding knee point:
                  if testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
                      iWRT_CUR_list = []
                      for iWRT_CUR in MMTtable[hd][zn][Osa][Osd]:
                          if not MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'] == 1:
                             iWRT_CUR_list.append(iWRT_CUR)
                      iWRT_CUR_list.sort() 
                      iWRT_CUR_list.reverse()
                      objMsg.printMsg("iWRT_CUR_list: %s" % str(iWRT_CUR_list))
                      if len(iWRT_CUR_list) > 0:
                        for iWRT_CUR in iWRT_CUR_list: 
                          objMsg.printMsg("MMTtable[%d][%d][%d][%d][%d]['BER']: %f" % (hd,zn,Osa,Osd,iWRT_CUR, MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER']))
                          if iWRT_CUR_list.index(iWRT_CUR) == 0 or iWRT_CUR_list.index(iWRT_CUR) == 1: #Treat 1st and 2nd Iw in iwlist differently in order to find knee point properly:
                             if 0: # Ignore poor BER #(MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'] > -1.5 or MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'] < -4.0): #Ber can be poor > -1.5. Or BER can be un-measurable, 1.0 or -6+.
                                MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP'] = -2 # to indicate BER is unmeasurable for this WP combi.
                                Iw_knee_pt_tracker[hd] = Iw_knee_pt_tracker[hd] + 1
                                Iw = iWRT_CUR # for Iw_knee_pt_tracker loop to work properly
                                objMsg.printMsg("0. Poor BER! BER > -1.5 or BER < -4. Poor BER! IwKP is set to -2.")
                                objMsg.printMsg("0. Iw_knee_pt_tracker[%d] inc by 1: %s" %(hd, Iw_knee_pt_tracker))
                                objMsg.printMsg("0. IwKP: %s" %(MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP']))
                                if Iw_knee_pt_tracker[hd] == 1: #knee point found.
                                    break;
                             else:
                                MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP'] = iWRT_CUR
                                Iw_knee_pt_tracker[hd] = 0 #Initialize Iw_knee_pt_tracker from -1 to 0.
                                objMsg.printMsg("1. Iw_knee_pt_tracker[%d]: %s" %(hd, Iw_knee_pt_tracker))
                                objMsg.printMsg("1. IwKP: %s" %(MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP']))
                          else: #For 3rd Iw onwards in iwlist:
                                prevIwIndex = iWRT_CUR_list.index(iWRT_CUR) - 1
                                prevIw = iWRT_CUR_list[prevIwIndex]                        
                                prev2IwIndex = iWRT_CUR_list.index(iWRT_CUR) - 2
                                prev2Iw = iWRT_CUR_list[prev2IwIndex]
                                #if (MMTtable[hd][zn][Osa][Osd][Iw]['BER'] == 1 or MMTtable[hd][zn][Osa][Osd][prevIw]['BER'] == 1): #There are situation where BER is poor or un-measurable.
                                if 0: # Ignore poor BER #(MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'] > -1.5 or MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'] < -4.0): #Ber can be poor > -1.5. Or BER can be un-measurable, 1.0 or -6+.
                                   if MMTtable[hd][zn][Osa][Osd][prevIw]['IwKP'] > 0: #if prev kp is already found, use prev kp. 
                                      MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP'] = MMTtable[hd][zn][Osa][Osd][prevIw]['IwKP']
                                      objMsg.printMsg("5a. Poor BER! BER > -1.5 or BER < -4. Poor BER! Previous IwKP is valid thus current IwKP is set to previous IwKP.")
                                      objMsg.printMsg("5a. IwKP: %s" %(MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP']))
                                   else:
                                      MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP'] = -2 # to indicate BER is unmeasurable for this WP combi.
                                      objMsg.printMsg("5b. Poor BER! BER > -1.5 or BER < -4. Poor BER! Previous IwKP is invalid too thus current IwKP is set to -2.")
                                      objMsg.printMsg("5b. IwKP: %s" %(MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP']))
                                   Iw_knee_pt_tracker[hd] = Iw_knee_pt_tracker[hd] + 1
                                   Iw = iWRT_CUR # for Iw_knee_pt_tracker loop to work properly
                                   objMsg.printMsg("5. Iw_knee_pt_tracker[%d] inc by 1: %s" %(hd, Iw_knee_pt_tracker))
                                   if Iw_knee_pt_tracker[hd] == 1: #knee point found.
                                      break;
                                   
                                else: # If current & previous Osd - Iw measurable BER info is populated in the MMTtable:
                                   #if self.headvendor == 'RHO': #delta cannot take absolute value for RHo drives:
                                   if ((MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'] - MMTtable[hd][zn][Osa][Osd][prevIw]['BER']) > deltaBERStop): #stopping point to check for knee point saturation
                                      Iw_knee_pt_tracker[hd] = Iw_knee_pt_tracker[hd] + 1
                                      Iw = iWRT_CUR # for Iw_knee_pt_tracker loop to work properly
                                      objMsg.printMsg("3. Current BER %0.4f - previous BER %0.4f = %0.4f > %0.2f rate of change. A knee point is found." % (MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'], MMTtable[hd][zn][Osa][Osd][prevIw]['BER'], (MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'] - MMTtable[hd][zn][Osa][Osd][prevIw]['BER']), deltaBERStop))
                                      objMsg.printMsg("3. Iw_knee_pt_tracker[%d] inc by 1: %s" %(hd, Iw_knee_pt_tracker))
                                      MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP'] = MMTtable[hd][zn][Osa][Osd][prevIw]['IwKP']
                                      objMsg.printMsg("3. IwKP: %s" %(MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP']))
                                      MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['deltaBER'] = (MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'] - MMTtable[hd][zn][Osa][Osd][prevIw]['BER'])
                                      if Iw_knee_pt_tracker[hd] == 1: #knee point found.
                                         break;
                                   else:
                                      #added extra check for unstable BER behaviour due to unstable heads etc:
                                      #if iwlist.index(Iw) > 1:
                                         if ((MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'] - MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER']) > deltaBERStop) and ((MMTtable[hd][zn][Osa][Osd][prevIw]['BER'] - MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER']) > deltaBERStop): 
                                            Iw_knee_pt_tracker[hd] = Iw_knee_pt_tracker[hd] + 1
                                            Iw = iWRT_CUR # for Iw_knee_pt_tracker loop to work properly
                                            objMsg.printMsg("4. Current BER %0.4f - previous 2 BER %0.4f = %0.4f > %0.2f rate of change. A knee point is found." % (MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'], MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER'], (MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'] - MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER']), deltaBERStop))
                                            objMsg.printMsg("4. Iw_knee_pt_tracker[%d] inc by 1: %s" %(hd, Iw_knee_pt_tracker))
                                            if MMTtable[hd][zn][Osa][Osd][prev2Iw]['IwKP'] > 0:
                                               MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP'] = MMTtable[hd][zn][Osa][Osd][prev2Iw]['IwKP']
                                            elif MMTtable[hd][zn][Osa][Osd][prevIw]['IwKP'] > 0:
                                               MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP'] = MMTtable[hd][zn][Osa][Osd][prevIw]['IwKP']
                                            else:
                                               MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP'] = iWRT_CUR 
                                            objMsg.printMsg("4. IwKP: %s" %(MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP']))
                                            MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['deltaBER2'] = (MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['BER'] - MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER'])
                                            MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['deltaBER3'] = (MMTtable[hd][zn][Osa][Osd][prevIw]['BER'] - MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER'])
                                            if Iw_knee_pt_tracker[hd] == 1: #knee point found.
                                               break;
                                         else:
                                            MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP'] = iWRT_CUR
                                            Iw_knee_pt_tracker[hd] = 0
                                            objMsg.printMsg("2. Iw_knee_pt_tracker[%d]: %s" %(hd, Iw_knee_pt_tracker))
                                            objMsg.printMsg("2. IwKP: %s" %(MMTtable[hd][zn][Osa][Osd][iWRT_CUR]['IwKP']))
                      else: #if len(iWRT_CUR_list) > 0:
                        Iw_knee_pt_tracker[hd] = 1
                        objMsg.printMsg("All T250 are not measurable. Force kp found, break loop...") 
                        objMsg.printMsg("6. Iw_knee_pt_tracker[%d]: %s" %(hd, Iw_knee_pt_tracker))  
                  else:
                      MMTtable[hd][zn][Osa][Osd][Iw]['IwKP'] = Iw
                      objMsg.printMsg("1. IwKP: %s" %(MMTtable[hd][zn][Osa][Osd][Iw]['IwKP']))
                      if iwlist.index(Iw) == 0 or iwlist.index(Iw) == 1: #Treat 1st and 2nd Iw in iwlist differently in order to find knee point properly:
                         Iw_knee_pt_tracker[hd] = 0 #Initialize Iw_knee_pt_tracker from -1 to 0.
                         objMsg.printMsg("1. Iw_knee_pt_tracker[%d]: %s" %(hd, Iw_knee_pt_tracker))
                      else: #For 3rd Iw onwards in iwlist:
                         prevIwIndex = iwlist.index(Iw) - 1
                         prevIw = iwlist[prevIwIndex]                        
                         prev2IwIndex = iwlist.index(Iw) - 2
                         prev2Iw = iwlist[prev2IwIndex]
                         if (not MMTtable[hd][zn][Osa][Osd][Iw]['BER'] == 1 and not MMTtable[hd][zn][Osa][Osd][prevIw]['BER'] == 1 and not MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER'] == 1):
                            if ((MMTtable[hd][zn][Osa][Osd][Iw]['BER'] - MMTtable[hd][zn][Osa][Osd][prevIw]['BER']) > deltaBERStop): #stopping point to check for knee point saturation
                                  Iw_knee_pt_tracker[hd] = Iw_knee_pt_tracker[hd] + 1
                                  objMsg.printMsg("3. Current BER %0.4f - previous BER %0.4f = %0.4f > %0.2f rate of change. A knee point is found." % (MMTtable[hd][zn][Osa][Osd][Iw]['BER'], MMTtable[hd][zn][Osa][Osd][prevIw]['BER'], (MMTtable[hd][zn][Osa][Osd][Iw]['BER'] - MMTtable[hd][zn][Osa][Osd][prevIw]['BER']), deltaBERStop))
                                  objMsg.printMsg("3. Iw_knee_pt_tracker[%d] inc by 1: %s" %(hd, Iw_knee_pt_tracker))
                                  MMTtable[hd][zn][Osa][Osd][Iw]['IwKP'] = MMTtable[hd][zn][Osa][Osd][prevIw]['IwKP']
                                  objMsg.printMsg("3. IwKP: %s" %(MMTtable[hd][zn][Osa][Osd][Iw]['IwKP']))
                                  MMTtable[hd][zn][Osa][Osd][Iw]['deltaBER'] = (MMTtable[hd][zn][Osa][Osd][Iw]['BER'] - MMTtable[hd][zn][Osa][Osd][prevIw]['BER'])
                            else:
                                  #added extra check for unstable BER behaviour due to unstable heads etc:
                                  #if iwlist.index(Iw) > 1:
                                  if ((MMTtable[hd][zn][Osa][Osd][Iw]['BER'] - MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER']) > deltaBERStop) and ((MMTtable[hd][zn][Osa][Osd][prevIw]['BER'] - MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER']) > deltaBERStop): 
                                        Iw_knee_pt_tracker[hd] = Iw_knee_pt_tracker[hd] + 1
                                        objMsg.printMsg("4. Current BER %0.4f - previous 2 BER %0.4f = %0.4f > %0.2f rate of change. A knee point is found." % (MMTtable[hd][zn][Osa][Osd][Iw]['BER'], MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER'], (MMTtable[hd][zn][Osa][Osd][Iw]['BER'] - MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER']), deltaBERStop))
                                        objMsg.printMsg("4. Iw_knee_pt_tracker[%d] inc by 1: %s" %(hd, Iw_knee_pt_tracker))
                                        if MMTtable[hd][zn][Osa][Osd][prev2Iw]['IwKP'] > 0:
                                           MMTtable[hd][zn][Osa][Osd][Iw]['IwKP'] = MMTtable[hd][zn][Osa][Osd][prev2Iw]['IwKP']
                                        elif MMTtable[hd][zn][Osa][Osd][prevIw]['IwKP'] > 0:
                                           MMTtable[hd][zn][Osa][Osd][Iw]['IwKP'] = MMTtable[hd][zn][Osa][Osd][prevIw]['IwKP']
                                        else:
                                           MMTtable[hd][zn][Osa][Osd][Iw]['IwKP'] = Iw 
                                        objMsg.printMsg("4. IwKP: %s" %(MMTtable[hd][zn][Osa][Osd][Iw]['IwKP']))
                                        MMTtable[hd][zn][Osa][Osd][Iw]['deltaBER2'] = (MMTtable[hd][zn][Osa][Osd][Iw]['BER'] - MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER'])
                                        MMTtable[hd][zn][Osa][Osd][Iw]['deltaBER3'] = (MMTtable[hd][zn][Osa][Osd][prevIw]['BER'] - MMTtable[hd][zn][Osa][Osd][prev2Iw]['BER'])
                                  #else:
                                        #MMTtable[hd][zn][Osa][Osd][Iw]['IwKP'] = Iw
                                        #Iw_knee_pt_tracker[hd] = 0
                      objMsg.printMsg("5. Iw_knee_pt_tracker[%d]: %s" %(hd, Iw_knee_pt_tracker))
                      objMsg.printMsg("5. IwKP: %s" %(MMTtable[hd][zn][Osa][Osd][Iw]['IwKP']))

                                    
                           
                  if Iw_knee_pt_tracker[hd] == 1: #knee point found.
                        if len(iWRT_CUR_list) == 0:
                           objMsg.printMsg("len(iWRT_CUR_list): %d" %(len(iWRT_CUR_list)))
                           # There will be situation where T250 is unmeasurable and list iWRT_CUR_list will be empty:
                           break
                        objMsg.printMsg("Iw: %d, prevIw: %d" %(Iw, prevIw)) 
                        #A value of 2 is used here is for the count of iw repeating. When iw has repeated itself for 2 times, knee point saturation is considered found for that head and Osa/Osd combi:
                        #objMsg.printMsg("Knee point saturation found for Head %d! Iw_knee_pt_tracker: %s" %(hd, Iw_knee_pt_tracker))
                        #Iw_knee_pt = Iw_knee_pt + 1

                        #if (tuningParam == 'OSD') or (tuningParam == 'SOVAKNEEPT'):
                           #objMsg.printMsg("Test head: %d, Test zone: %d, Osd: %d, Iw: %d, Osa: %d" %(hd, zn, Osd, Iw, Osa))
                        #else: 
                           #objMsg.printMsg("Test head: %d, Test zone: %d, Osd: %d, Iw: %d, Osa: %d" %(hd, zn, Osa, Iw, Osd))
                        #objMsg.printMsg("MMTtable[%d][%d][%d][%d][%d]['IwKP']: %d" % (hd,zn,Osa,Osd,Iw, MMTtable[hd][zn][Osa][Osd][Iw]['IwKP']))
                        
                        KPTable[hd][zn][Osa][Osd]['IwKP'] = MMTtable[hd][zn][Osa][Osd][Iw]['IwKP']
                        objMsg.printMsg("BER saturation point, knee point, is found. KPTable[%d][%d][%d][%d]['IwKP']=%d. " % (hd,zn,Osa,Osd,KPTable[hd][zn][Osa][Osd]['IwKP']))
                        
                        objMsg.printMsg("tuningList[%d][%d].index(%d): %d" %(hd,zn,Osd,tuningList[hd][zn].index(Osd)))
                        objMsg.printMsg("findingKneePointDict[%d][%d]: %d" %(hd,zn,findingKneePointDict[hd][zn]))

                        if (tuningParam == 'OSD' or tuningParam == 'SOVAKNEEPT'):
                            #if not tuningList[hd][zn].index(Osd) == 0: #Usually at this point prevIw is already available.
                            KPTable[hd][zn][Osa][Osd]['IwKPBER'] = MMTtable[hd][zn][Osa][Osd][prevIw]['BER']
                            objMsg.printMsg("KPTable[%d][%d][%d][%d]['IwKPBER']=%s" % (hd,zn,Osa,Osd,KPTable[hd][zn][Osa][Osd]['IwKPBER']))

                            # For certain wafers (such as HWY LSI 5A5J0), saturating point does not happen for 3x repeated times.
                            # In such case, we loop OSD in reverse order and pick the saturating point based on the lowest IWKP.
                            # Iw_knee_pt is 0 before the first KP is found. Iw_knee_pt is assign a value when a kp is found.
                            if (Iw_knee_pt == 0 or KPTable[hd][zn][Osa][Osd]['IwKP'] <= Iw_knee_pt):
                               objMsg.printMsg("KPTable[%d][%d][%d][%d]['IwKP']=%d <= Iw_knee_pt=%d. " % (hd,zn,Osa,Osd,KPTable[hd][zn][Osa][Osd]['IwKP'],Iw_knee_pt))
                               Iw_knee_pt = KPTable[hd][zn][Osa][Osd]['IwKP']
                               objMsg.printMsg("Iw_knee_pt updated: %d" %(Iw_knee_pt))
                               Osd_found = Osd
                               objMsg.printMsg("Osd_found updated: %d" %(Osd_found))
                               
                            else:
                               # Current sweeping OSD has a IWKP > previous sweeping OSD, stop the sweeping. OSD saturationg point is found.
                               objMsg.printMsg("KPTable[%d][%d][%d][%d]['IwKP']=%d > Iw_knee_pt=%d. " % (hd,zn,Osa,Osd,KPTable[hd][zn][Osa][Osd]['IwKP'],Iw_knee_pt))
                               findingKneePointDict[hd][zn] = Osd_found
                               objMsg.printMsg("findingKneePointDict[%d][%d] updated: %d" %(hd,zn,findingKneePointDict[hd][zn]))
                               #loop_count = loop_count + 1 #For updating spc_id.

                               # Sweep all previous found BERs to see if any one has BER greater than the current IwKP BER by 0.8 (TP.mmt_osdIwKPBERCheck):
                               best_ber = KPTable[hd][zn][Osa][Osd_found]['IwKPBER']
                               best_osd = Osd_found
                               objMsg.printMsg("Osd_found %d: %s. To use this IwKPBER to search for next possible greater Osd with higher IwKPBER." %(best_osd, best_ber))
                               objMsg.printMsg("TP.mmt_osd_tuninglist: %s" %str(TP.mmt_osd_tuninglist))
                               for osd3 in TP.mmt_osd_tuninglist: #[28, 24, 20, 16, 12, 8, 4]
                                  if osd3 > Osd_found:
                                     #objMsg.printMsg("Osd with highest BER, best_osd %d: %s" %(best_osd, best_ber))
                                     if KPTable[hd][zn][Osa][osd3]['IwKPBER'] < KPTable[hd][zn][Osa][Osd_found]['IwKPBER'] and KPTable[hd][zn][Osa][osd3]['IwKPBER'] < best_ber:
                                        best_ber = KPTable[hd][zn][Osa][osd3]['IwKPBER']
                                        best_osd = osd3
                                        objMsg.printMsg("New Osd with higher BER, best_osd %d: %s. Delta BER %s." %(best_osd, best_ber,(KPTable[hd][zn][Osa][Osd_found]['IwKPBER'] - best_ber)))
                               if (KPTable[hd][zn][Osa][Osd_found]['IwKPBER'] - best_ber) > TP.mmt_osdIwKPBERCheck:
                                  objMsg.printMsg("KPTable[%d][%d][%d][%d]['IwKPBER']=%s - KPTable[%d][%d][%d][%d]['IwKPBER']=%s > %s" % (hd,zn,Osa,Osd,KPTable[hd][zn][Osa][Osd_found]['IwKPBER'],hd,zn,Osa,Osd,KPTable[hd][zn][Osa][best_osd]['IwKPBER'],TP.mmt_osdIwKPBERCheck))
                                  findingKneePointDict[hd][zn] = best_osd
                                  objMsg.printMsg("New osd is found! findingKneePointDict[%d][%d] updated: %d" %(hd,zn,findingKneePointDict[hd][zn]))
                               else:
                                  objMsg.printMsg("Delta is not > %s. OSD retain as original one (%d). " %(TP.mmt_osdIwKPBERCheck, findingKneePointDict[hd][zn]))

                               break
                            #if no saturation is found at the last Osd, set the last Osd as the final Osd found:
                            if tuningList[hd][zn].index(Osd) == (len(tuningList[hd][zn]) - 1):
                               findingKneePointDict[hd][zn] = max(tuningList[hd][zn])
                               objMsg.printMsg("findingKneePointDict[%d][%d] updated2: %d" %(hd,zn,findingKneePointDict[hd][zn]))
                               #loop_count = loop_count + 1 #For updating spc_id.
                               break
                            if 0: #(tuningList[hd][zn].index(Osd) > 1 and findingKneePointDict[hd][zn] == -1 and (tuningParam == 'OSD' or tuningParam == 'SOVAKNEEPT')): # Check if 3x repetitive knee points have appeared:
    			               prevOsdIndex = tuningList[hd][zn].index(Osd) - 1
    			               prevOsd = tuningList[hd][zn][prevOsdIndex]
    			               prev2OsdIndex = tuningList[hd][zn].index(Osd) - 2
    			               prev2Osd = tuningList[hd][zn][prev2OsdIndex]
    			               objMsg.printMsg("1prevOsd: %s" %(prevOsd))
    			               objMsg.printMsg("1prev2Osd: %s" %(prev2Osd))
    			               objMsg.printMsg("KPTable[hd][zn][Osa][Osd]['IwKP']: %s" %(KPTable[hd][zn][Osa][Osd]['IwKP']))
    			               objMsg.printMsg("KPTable[hd][zn][Osa][prevOsd]['IwKP']: %s" %(KPTable[hd][zn][Osa][prevOsd]['IwKP']))
    			               objMsg.printMsg("KPTable[hd][zn][Osa][prev2Osd]['IwKP']: %s" %(KPTable[hd][zn][Osa][prev2Osd]['IwKP']))
    			               if (KPTable[hd][zn][Osa][Osd]['IwKP'] > KPTable[hd][zn][Osa][prevOsd]['IwKP']) and (KPTable[hd][zn][Osa][prevOsd]['IwKP'] == KPTable[hd][zn][Osa][prev2Osd]['IwKP']):
    			                  objMsg.printMsg("Current IwKP value is greater than previous 2 repetitive IwKP values.")
    			                  objMsg.printMsg("Update current IwKP value to be the same as previous 2 repetitive IwKP values.")
    			                  KPTable[hd][zn][Osa][Osd]['IwKP'] = KPTable[hd][zn][Osa][prevOsd]['IwKP']
                               
                               # Check if 3x repetitive knee points have appeared:
                               # but if osd is the last sweeping item but there is only 2x repeated KPs then we will consider the last 2 KP.
    			               if ((KPTable[hd][zn][Osa][Osd]['IwKP'] == KPTable[hd][zn][Osa][prevOsd]['IwKP'] == KPTable[hd][zn][Osa][prev2Osd]['IwKP'] and (tuningList[hd][zn].index(Osd) < (len(tuningList[hd][zn])-1))) or 
                                  ((tuningList[hd][zn].index(Osd) == (len(tuningList[hd][zn])-1)) and KPTable[hd][zn][Osa][Osd]['IwKP'] == KPTable[hd][zn][Osa][prevOsd]['IwKP'])): 
    			                  if KPTable[hd][zn][Osa][Osd]['IwKP'] > 0: #Optimized Osd must be a positive value. 
    			                     findingKneePointDict[hd][zn] = tuningList[hd][zn][prev2OsdIndex] #KPTable[hd][zn][Osa][Osd]['IwKP']
    			                  else:
    			                     objMsg.printMsg("Setting to default value.")
    			                     #Def_Triplet = list(TP.VbarWpTable[self.__dut.PREAMP_TYPE]['ALL'][2])#(Iw, Ovs, Ovd)
    			                     if (tuningParam == 'OSD' or tuningParam == 'SOVAKNEEPT'):
    			                        findingKneePointDict[hd][zn] = self.Def_Triplet[2] #Set to default Osd value.
    			                     else:
    			                        findingKneePointDict[hd][zn] = self.Def_Triplet[1] #Set to default Osa value.
    			                  objMsg.printMsg("findingKneePointDict[%d][%d]: %s" %(hd, zn, findingKneePointDict[hd][zn]))


                        #Print MMTtable & KPTable:
                        printTableFlag = 0
                        
                  else: 
                     if testSwitch.FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3:
                        objMsg.printMsg("WRT_CUR loop is ending. But still cannot find a KP. Set IwKP: %d" % (MMTtable[hd][zn][Osa][Osd][min(iWRT_CUR_list)]['IwKP']))
                        KPTable[hd][zn][Osa][Osd]['IwKP'] = MMTtable[hd][zn][Osa][Osd][min(iWRT_CUR_list)]['IwKP'] 
                     else:       
                        if Iw == iwlist[(len(iwlist)-1)]: #Still cannot find a kp for the last Iw in the iwlist.
                           if Iw_knee_pt_tracker[hd] == 0:
                              objMsg.printMsg("Iw loop is ending. But still cannot find a KP. Set IwKP: %d" % (MMTtable[hd][zn][Osa][Osd][Iw]['IwKP']))
                              KPTable[hd][zn][Osa][Osd]['IwKP'] = MMTtable[hd][zn][Osa][Osd][Iw]['IwKP']
                           else:
                              KPTable[hd][zn][Osa][Osd]['IwKP'] = Iw #? 
                              objMsg.printMsg("Iw loop is ending. But still cannot find a KP. Set IwKP to Iw: %d" % (Iw))
                           if (tuningParam == 'OSD' or tuningParam == 'SOVAKNEEPT'):
                              objMsg.printMsg("prevIw: %s" %(prevIw))
                              KPTable[hd][zn][Osa][Osd]['IwKPBER'] = MMTtable[hd][zn][Osa][Osd][prevIw]['BER']
                              objMsg.printMsg("KPTable[%d][%d][%d][%d]['IwKPBER']=%s" % (hd,zn,Osa,Osd,KPTable[hd][zn][Osa][Osd]['IwKPBER']))


                           #Print MMTtable & KPTable:
                           printTableFlag = 0
                           #objMsg.printMsg("MMTtable2: %s" %(MMTtable))
                           #objMsg.printMsg("KPTable2: %s" %(KPTable))  

                  #loop_count = loop_count + 1 #For updating spc_id.
               
                            
               # Print MMTtable & KPTable at the end of every Iw loop:
               if (printTableFlag == 1):
                  if (tuningParam == 'OSD' or tuningParam == 'SOVAKNEEPT'):
                     objMsg.printMsg('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % ('Hd','Zn','Iw','Oa','Od','BER','deltaBER','deltaBER2','deltaBER3','IwKP'))
                  else:
                     objMsg.printMsg('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % ('Hd','Zn','Iw','Od','Oa','BER','deltaBER','deltaBER2','deltaBER3','IwKP'))
                  for hd2 in self.headRange:
                     if (hd == hd2):
                        for zn2 in testzonelist:
                           if (zn == zn2): 
                              Osa2 = tuningDict[hd2][zn2]
                              for Osd2 in tuningList[hd2][zn2]:
                                 if (Osd2 <= Osd): #Print shorter table.
                                    for Iw2 in orgiwlist:
                                       if not 'deltaBER' in MMTtable[hd2][zn2][Osa2][Osd2][Iw2].keys():
                                          MMTtable[hd2][zn2][Osa2][Osd2][Iw2]['deltaBER'] = 0
                                       if not 'deltaBER2' in MMTtable[hd2][zn2][Osa2][Osd2][Iw2].keys():
                                          MMTtable[hd2][zn2][Osa2][Osd2][Iw2]['deltaBER2'] = 0
                                       if not 'deltaBER3' in MMTtable[hd2][zn2][Osa2][Osd2][Iw2].keys():
                                          MMTtable[hd2][zn2][Osa2][Osd2][Iw2]['deltaBER3'] = 0    
                                       objMsg.printMsg('%2d\t%2d\t%2d\t%2d\t%2d\t%0.4f\t%0.4f\t%0.4f\t%0.4f\t%2d\t' % (hd2,zn2,Iw2,Osa2,Osd2,MMTtable[hd2][zn2][Osa2][Osd2][Iw2]['BER'],MMTtable[hd2][zn2][Osa2][Osd2][Iw2]['deltaBER'],MMTtable[hd2][zn2][Osa2][Osd2][Iw2]['deltaBER2'],MMTtable[hd2][zn2][Osa2][Osd2][Iw2]['deltaBER3'],MMTtable[hd2][zn2][Osa2][Osd2][Iw2]['IwKP']))

                  if (tuningParam == 'OSD' or tuningParam == 'SOVAKNEEPT'):
                     objMsg.printMsg('%s\t%s\t%s\t%s\t%s' % ('Hd','Zn','Oa','Od','IwKP'))
                  else:
                     objMsg.printMsg('%s\t%s\t%s\t%s\t%s' % ('Hd','Zn','Od','Oa','IwKP'))
                  for hd2 in self.headRange:
                     for zn2 in testzonelist:
                        Osa2 = tuningDict[hd2][zn2]
                        for Osd2 in tuningList[hd2][zn2]:
                           objMsg.printMsg('%2d\t%2d\t%2d\t%2d\t%2d' % (hd2,zn2,Osa2,Osd2,KPTable[hd2][zn2][Osa2][Osd2]['IwKP'])) 
                        
                  #objMsg.printMsg("MMTtable: %s" %(MMTtable))
                  #objMsg.printMsg("KPTable: %s" %(KPTable))  

      objMsg.printMsg("KPTable: %s" %(KPTable))
      objMsg.printMsg("MMTtable: %s" %(MMTtable))
      objMsg.printMsg("findingKneePointDict: %s" %(findingKneePointDict))
      #Print MMTtable:
      mmtdatadump_str = 'mmtdatadump' 
      if (tuningParam == 'OSD'):
         mmtdatadump_str = 'mmtdatadump_osd_ber_info'
      elif (tuningParam == 'SOVAKNEEPT'):
         mmtdatadump_str = 'mmtdatadump_subzones_ber_info'
      else:
         mmtdatadump_str = 'mmtdatadump_osa_ber_info'

      if (tuningParam == 'OSD' or tuningParam == 'SOVAKNEEPT'):
         objMsg.printMsg('%s %s %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (mmtdatadump_str,str(self.__dut.serialnum),'Hd','Zn','Iw','Oa','Od','BER','deltaBER','deltaBER2','deltaBER3','IwKP'))
      else:
         objMsg.printMsg('%s %s %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (mmtdatadump_str,str(self.__dut.serialnum), 'Hd','Zn','Iw','Od','Oa','BER','deltaBER','deltaBER2','deltaBER3','IwKP'))
      for hd in self.headRange:
         for zn2 in testzonelist:
            Osa2 = tuningDict[hd][zn2]
            for Osd2 in tuningList[hd][zn2]:
                  for Iw2 in orgiwlist:
                     if not 'deltaBER' in MMTtable[hd][zn2][Osa2][Osd2][Iw2].keys():
                        MMTtable[hd][zn2][Osa2][Osd2][Iw2]['deltaBER'] = 0
                     if not 'deltaBER2' in MMTtable[hd][zn2][Osa2][Osd2][Iw2].keys():
                        MMTtable[hd][zn2][Osa2][Osd2][Iw2]['deltaBER2'] = 0
                     if not 'deltaBER3' in MMTtable[hd][zn2][Osa2][Osd2][Iw2].keys():
                        MMTtable[hd][zn2][Osa2][Osd2][Iw2]['deltaBER3'] = 0    
                     objMsg.printMsg('%s %s %2d\t%2d\t%2d\t%2d\t%2d\t%0.4f\t%0.4f\t%0.4f\t%0.4f\t%2d' % (mmtdatadump_str,str(self.__dut.serialnum),hd,zn2,Iw2,Osa2,Osd2,MMTtable[hd][zn2][Osa2][Osd2][Iw2]['BER'],MMTtable[hd][zn2][Osa2][Osd2][Iw2]['deltaBER'],MMTtable[hd][zn2][Osa2][Osd2][Iw2]['deltaBER2'],MMTtable[hd][zn2][Osa2][Osd2][Iw2]['deltaBER3'],MMTtable[hd][zn2][Osa2][Osd2][Iw2]['IwKP']))
      #Print KPTable:
      mmtdatadump_str = 'mmtdatadump' 
      if (tuningParam == 'OSD'):
         mmtdatadump_str = 'mmtdatadump_osd_kp'
      elif (tuningParam == 'SOVAKNEEPT'):
         mmtdatadump_str = 'mmtdatadump_subzones_sova_kp'
      else:
         mmtdatadump_str = 'mmtdatadump_osa_kp'
      if (tuningParam == 'OSD'):
         objMsg.printMsg('%s FINAL OSD KNEEPOINT TABLE' % mmtdatadump_str)
         objMsg.printMsg('%s %s\t%s\t%s\t%s\t%s\t%s' % (mmtdatadump_str,'Hd',' Zn',' Oa',' Od','IwKP','IwKPBER'))
      elif (tuningParam == 'SOVAKNEEPT'):
         objMsg.printMsg('%s FINAL SOVA KNEEPOINT TABLE' % mmtdatadump_str)
         objMsg.printMsg('%s %s\t%s\t%s\t%s\t%s\t%s' % (mmtdatadump_str,'Hd',' Zn',' Oa',' Od','IwKP','IwKPBER'))
      else:
         objMsg.printMsg('%s FINAL OSA KNEEPOINT TABLE' % mmtdatadump_str)
         objMsg.printMsg('%s %s\t%s\t%s\t%s\t%s\t%s' % (mmtdatadump_str,'Hd',' Zn',' Od',' Oa','IwKP','IwKPBER'))
      for hd in self.headRange: 
         for zn in testzonelist:
            Osa = tuningDict[hd][zn]
            for Osd in tuningList[hd][zn]:
               objMsg.printMsg('%s %2d\t%3d\t%3d\t%3d\t%4d\t%s' % (mmtdatadump_str,hd,zn,Osa,Osd,KPTable[hd][zn][Osa][Osd]['IwKP'],KPTable[hd][zn][Osa][Osd]['IwKPBER'])) 


      if (tuningParam == 'OSD'):
         return findingKneePointDict
      elif (tuningParam == 'SOVAKNEEPT'):
         return KPTable
      else: 
         return KPTable


#----------------------------------------------------------------------------------------------------------
class CCertBasedATB(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)
      self.__dut = objDut

   #-------------------------------------------------------------------------------------------------------

   def run(self):
      from PreAmp import CPreAmp
      from PowerControl import objPwrCtrl
      oProc = CProcess()

      oPreamp = CPreAmp()
      preamp_info = oPreamp.getPreAmpType()
      oPreamp = None  # Allow GC
      self.__dut.PREAMP_TYPE = preamp_info[0]
      if not testSwitch.FE_0334525_348429_INTERPOLATED_DEFAULT_TRIPLET:
         Def_Triplet = list(TP.VbarWpTable[self.__dut.PREAMP_TYPE]['ALL'][2])#(Iw, Ovs, Ovd)
      else:
         try:
            Def_Triplet = list(TP.VbarWpTable[self.__dut.PREAMP_TYPE]['ALL'][2])#(Iw, Ovs, Ovd)
         except:
            Def_Triplet = list(TP.VbarWpTable[self.__dut.PREAMP_TYPE]['OD'][2])#(Iw, Ovs, Ovd)
      testzonelist = TP.testzonelist
      iwlist = TP.iwlist
      osa_tuninglist = TP.osa_tuninglist
      osd_tuninglist = TP.osd_tuninglist
      iOW = 0
      iWPE_UIN = 0
      iWPE_NM = 0
      loop_count = 1000
      minRRawBEROnTrk, minSovaOnTrk, minRRawBERATI, minSovaATI, minRRawBERSTE, minSovaSTE = 0,0,0,0,0,0

      objMsg.printMsg("**********************************************")
      objMsg.printMsg("******** Cert Based ATB control rules ********")
      objMsg.printMsg("**********************************************")
      objMsg.printMsg("Serial no: %s" %(str(self.__dut.serialnum)))
      objMsg.printMsg("Test zones: %s" %(testzonelist))
      objMsg.printMsg("IW tuning list: %s" %(iwlist))
      objMsg.printMsg("OSA tuning list: %s" %(osa_tuninglist))
      objMsg.printMsg("OSD tuning list: %s" %(osd_tuninglist))

      T69WPEparams = {'ZONE_POSITION': 100}
      from Head_Measure import CWPE
      CWPE(self.dut, T69WPEparams).run() 
      
      wpetable={}
      for hd in range(self.dut.imaxHead):
         wpetable[hd] = {}
         wpetable[hd]['WPE_UIN'] = 0
         wpetable[hd]['WPE_NM'] = 0

      newwpetable = self.getT69WPE(wpetable)
      #objMsg.printMsg("newwpetable: %s" %(newwpetable))
      
      Infotable={}
      for hd in range(self.dut.imaxHead):
         Infotable[hd] = {}
         for zn in testzonelist:
            Infotable[hd][zn] = {}         
            for Iw in iwlist:
               Infotable[hd][zn][Iw] = {}
               for Osa in osa_tuninglist:
                  Infotable[hd][zn][Iw][Osa] = {}
                  for Osd in osd_tuninglist:
                     Infotable[hd][zn][Iw][Osa][Osd] = {}
                     Infotable[hd][zn][Iw][Osa][Osd]['SN'] = str(self.__dut.serialnum)
                     Infotable[hd][zn][Iw][Osa][Osd]['WPE_UIN'] = newwpetable[hd]['WPE_UIN']
                     Infotable[hd][zn][Iw][Osa][Osd]['WPE_NM'] = newwpetable[hd]['WPE_NM']
                     Infotable[hd][zn][Iw][Osa][Osd]['OnTrackOTF'] = 0
                     Infotable[hd][zn][Iw][Osa][Osd]['OnTrackSova'] = 0
                     Infotable[hd][zn][Iw][Osa][Osd]['ATIOTF'] = 0
                     Infotable[hd][zn][Iw][Osa][Osd]['ATISova'] = 0
                     Infotable[hd][zn][Iw][Osa][Osd]['STEOTF'] = 0
                     Infotable[hd][zn][Iw][Osa][Osd]['STESova'] = 0
                     Infotable[hd][zn][Iw][Osa][Osd]['OVW'] = 0

      
  
      for hd in range(self.dut.imaxHead):
         for zn in testzonelist:
            for Iw in iwlist:
               for Osa in osa_tuninglist:
                  for Osd in osd_tuninglist:
                     minRRawBEROnTrk, minSovaOnTrk, minRRawBERATI, minSovaATI, minRRawBERSTE, minSovaSTE = self.runT51(hd, zn, Osd, Osa, Iw, loop_count, TP.n_writes,TP.band_size)
                     loop_count = loop_count + 1
                     Infotable[hd][zn][Iw][Osa][Osd]['OnTrackOTF'] = minRRawBEROnTrk
                     Infotable[hd][zn][Iw][Osa][Osd]['OnTrackSova'] = minSovaOnTrk
                     Infotable[hd][zn][Iw][Osa][Osd]['ATIOTF'] = minRRawBERATI
                     Infotable[hd][zn][Iw][Osa][Osd]['ATISova'] = minSovaATI
                     Infotable[hd][zn][Iw][Osa][Osd]['STEOTF'] = minRRawBERSTE
                     Infotable[hd][zn][Iw][Osa][Osd]['STESova'] = minSovaSTE
      objPwrCtrl.powerCycle(5000,12000,10,30)
      loop_count = 1000
      for hd in range(self.dut.imaxHead):
         for zn in testzonelist:
            for Iw in iwlist:
               for Osa in osa_tuninglist:
                  for Osd in osd_tuninglist:
                     iOW = self.runT61(hd, zn, Osd, Osa, Iw, loop_count)
                     loop_count = loop_count + 1
                     objMsg.printMsg("iOW: %s" % str(iOW))
                     Infotable[hd][zn][Iw][Osa][Osd]['OVW'] = iOW
      

      objMsg.printMsg('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % \
                      ('CERT_BASED_ATB_dump SN','WPE_UIN', 'WPE_NM', 'Hd','Zn','Iw','Oa','Od','OnTrackOTF','OnTrackSova','ATIOTF','ATISova','STEOTF', 'STESova', 'OVW'))
      for hd in range(self.dut.imaxHead):
         for zn in testzonelist:
            for Iw in iwlist:
               for Osa in osa_tuninglist:
                  for Osd in osd_tuninglist:
                     objMsg.printMsg('CERT_BASED_ATB_dump %s\t%0.4f\t%0.4f\t%2d\t%2d\t%2d\t%2d\t%2d\t%0.4f\t%0.4f\t%0.4f\t%0.4f\t%0.4f\t%0.4f\t%0.4f' % \
                                     (Infotable[hd][zn][Iw][Osa][Osd]['SN'], \
                                      Infotable[hd][zn][Iw][Osa][Osd]['WPE_UIN'], \
                                      Infotable[hd][zn][Iw][Osa][Osd]['WPE_NM'], \
                                      hd, zn, Iw, Osa, Osd,\
                                      Infotable[hd][zn][Iw][Osa][Osd]['OnTrackOTF'], \
                                      Infotable[hd][zn][Iw][Osa][Osd]['OnTrackSova'], \
                                      Infotable[hd][zn][Iw][Osa][Osd]['ATIOTF'], \
                                      Infotable[hd][zn][Iw][Osa][Osd]['ATISova'], \
                                      Infotable[hd][zn][Iw][Osa][Osd]['STEOTF'], \
                                      Infotable[hd][zn][Iw][Osa][Osd]['STESova'], \
                                      Infotable[hd][zn][Iw][Osa][Osd]['OVW']))

      objPwrCtrl = None  # Allow GC

   def getT69WPE (self, wpetable):
      oProc = CProcess()
      import Utility
      oUtil = Utility.CUtility()
      tableData = []
      try:
         tableData = self.__dut.dblData.Tables('P069_WPE_SUMMARY').tableDataObj()
      except: 
         objMsg.printMsg("P069_WPE_SUMMARY not found!!!!!")
         pass
      if len(tableData) > 0:
         for row in tableData:
            iHead = int(row['HD_LGC_PSN'])
            iWPE_UIN = float(row['WPE_UIN'])
            iWPE_NM = float(row['WPE_NM'])
            objMsg.printMsg("iHead: %s, iWPE_UIN: %s, iWPE_NM: %s" %(iHead, iWPE_UIN, iWPE_NM))
            wpetable[iHead]['WPE_UIN'] = iWPE_UIN
            wpetable[iHead]['WPE_NM'] = iWPE_NM

      return wpetable

   def runT51(self, hd, zn, Osd, Osa, Iw, loop_count, n_writes, band_size):
      oProc = CProcess()
      import Utility
      oUtil = Utility.CUtility()
      
      minRRawBERATI = 0
      minSovaATI = 0
      minRRawBERSTE = 0
      minSovaSTE = 0
      minRRawBEROnTrk = 0
      minSovaOnTrk = 0

      ati_param = oUtil.copy(TP.prm_Triplet_ATI_STE)      
      oUtil = None  # Allow GC      
      ati_param['TEST_HEAD'] = hd
      ati_param['ZONE'] = zn
      ati_param['spc_id'] = loop_count
      ati_param['CENTER_TRACK_WRITES'] = n_writes
      #ati_param['CWORD1'] = TP.cword1
      #if testSwitch.FE_0273368_348429_ENABLE_TPINOMINAL or testSwitch.FE_0273368_348429_TEMP_ENABLE_TPINOMINAL_FOR_ATI_STE:
      ati_param['CWORD1'] = ati_param['CWORD1'] & 0xBFFF # reset to zero
      ati_param['CWORD2'] = TP.cword2
      ati_param['DAMPING'] = Osa
      ati_param['WRITE_CURRENT'] = min(Iw,127)
      ati_param['DURATION'] = Osd
      ati_param['BAND_SIZE'] = band_size
      ati_param['TLEVEL'] = TP.tlevel
      try: oProc.St(ati_param)
      except:
         from PowerControl import objPwrCtrl
         objPwrCtrl.powerCycle(5000,12000,10,30)
         objPwrCtrl = None  # Allow GC
         try: 
            oProc.St(ati_param)
         except:
            pass

      tableData = []
      try:
         tableData = self.__dut.dblData.Tables('P051_ERASURE_BER').tableDataObj()
      except: 
         objMsg.printMsg("P051_ERASURE_BER not found!!!!!")
         pass

      startIndex = 0
      endIndex = len(tableData)

      # Find the min RRAW_BER & BITS_IN_ERROR_BER:
      if startIndex != endIndex:
         for record in range(startIndex, endIndex):
            iHead = int(tableData[record]['HD_PHYS_PSN'])
            iZone = int(tableData[record]['DATA_ZONE'])
            TEST_TYPE = tableData[record]['TEST_TYPE']
            RRAW_BER = float(tableData[record]['RRAW_BER'])
            TRK_INDEX = int(tableData[record]['TRK_INDEX'])
            BITS_IN_ERROR_BER = float(tableData[record]['BITS_IN_ERROR_BER'])
            if int(tableData[record]['SPC_ID']) == loop_count and TEST_TYPE == 'erasure':
               if  (TRK_INDEX == 1 or TRK_INDEX == -1): 
                  if (minRRawBERATI == 0):
                     minRRawBERATI = RRAW_BER
                  else:
                     if (RRAW_BER < minRRawBERATI):
                        minRRawBERATI = RRAW_BER
                  if (minSovaATI == 0):
                     minSovaATI = BITS_IN_ERROR_BER
                  else:
                     if (BITS_IN_ERROR_BER < minSovaATI):
                        minSovaATI = BITS_IN_ERROR_BER  
               else:
                  if (minRRawBERSTE == 0):
                     minRRawBERSTE = RRAW_BER
                  else:
                     if (RRAW_BER < minRRawBERSTE):
                        minRRawBERSTE = RRAW_BER
                  if (minSovaSTE == 0):
                     minSovaSTE = BITS_IN_ERROR_BER
                  else:
                     if (BITS_IN_ERROR_BER < minSovaSTE):
                        minSovaSTE = BITS_IN_ERROR_BER
            if int(tableData[record]['SPC_ID']) == loop_count and TEST_TYPE == 'baseline':
               if  (TRK_INDEX == 1 or TRK_INDEX == -1): 
                  if (minRRawBEROnTrk == 0):
                     minRRawBEROnTrk = RRAW_BER
                  else:
                     if (RRAW_BER < minRRawBEROnTrk):
                        minRRawBEROnTrk = RRAW_BER
                  if (minSovaOnTrk == 0):
                     minSovaOnTrk = BITS_IN_ERROR_BER
                  else:
                     if (BITS_IN_ERROR_BER < minSovaOnTrk):
                        minSovaOnTrk = BITS_IN_ERROR_BER     
      objMsg.printMsg("min OnTrack RRAW_BER: %0.2f" % (minRRawBEROnTrk)) 
      objMsg.printMsg("min OnTrack BITS_IN_ERROR_BER: %0.2f" % (minSovaOnTrk)) 
      objMsg.printMsg("min ATI RRAW_BER: %0.2f" % (minRRawBERATI)) 
      objMsg.printMsg("min ATI BITS_IN_ERROR_BER: %0.2f" % (minSovaATI))
      objMsg.printMsg("min STE RRAW_BER: %0.2f" % (minRRawBERSTE)) 
      objMsg.printMsg("min STE BITS_IN_ERROR_BER: %0.2f" % (minSovaSTE)) 
      
      return minRRawBEROnTrk, minSovaOnTrk, minRRawBERATI, minSovaATI, minRRawBERSTE, minSovaSTE

   def runT61(self, hd, zn, Osd, Osa, Iw, loop_count): #(self, testzonelist, iwUBTable, iwlist):
      oProc = CProcess()
      import Utility
      oUtil = Utility.CUtility()
      
      param61 = TP.WeakWrOWPrm_61.copy()

                   
      tableData = []
      param61.update({'RESULTS_RETURNED': 0, 'spc_id': loop_count, 'HEAD_RANGE': ( (hd << 8) + hd ), 'ZONE': zn, 'CWORD1':0x00C1, 'DURATION': Osd, 'WRITE_CURRENT': Iw, 'DAMPING': Osa})
    
      try:
         CProcess().St(param61)      
      except:
         objMsg.printMsg("WeakWrOWPrm_61 fail")
         pass

      try:
         tableData = self.dut.dblData.Tables('P061_OW_MEASUREMENT').chopDbLog('SPC_ID', 'match',str(loop_count))
      except: 
         objMsg.printMsg("P061_OW_MEASUREMENT not found!!!!!")
         pass

      if len(tableData) > 0:
         for row in tableData:
            iHead = int(row['HD_LGC_PSN'])
            iZone = int(row['DATA_ZONE'])
            iOW = float(row['OW'])
            if iOW == '-inf':#??
               iOW = 0
            #objMsg.printMsg("iOW: %0.4f" %(iOW))
            if (hd == iHead and zn == iZone and int(row['SPC_ID']) == loop_count):
               objMsg.printMsg("hd %d zn %d Iw %d Osd %d Osa %d OW %0.4f" %(hd, zn, Iw, Osd, Osa, iOW))
               return iOW
      else:
         return 0
   

