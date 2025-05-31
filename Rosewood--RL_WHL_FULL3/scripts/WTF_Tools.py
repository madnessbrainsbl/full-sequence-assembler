#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Common waterfall tools
#
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/WTF_Tools.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/WTF_Tools.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
from Drive import objDut
import PIF
import MessageHandler as objMsg
from ScrCmds import HostSetPartnum
from ScrCmds import raiseException
from ScrCmds import CRaiseException
from Utility import CSpcIdHelper
from Utility import getVBARPrintDbgMsgFunction
from PIF import nibletTable

printDbgMsg = getVBARPrintDbgMsgFunction()


#----------------------------------------------------------------------------------------------------------
class CWTF_Tools(object):
   """
      Base class for waterfall tools
   """
   #-------------------------------------------------------------------------------------------------------
   def __init__(self):
      self.dut = objDut

      # Initialize the SPC_ID
      CSpcIdHelper(self.dut).getSetIncrSpcId('P_VBAR_FORMAT_SUMMARY', startSpcId = 0, increment = 0, useOpOffset = 1)

   #-------------------------------------------------------------------------------------------------------
   def WTF_Unyielded(self, ec= 12168):
      objMsg.printMsg("Capacity waterfall with no restart/failure - sending unyielded failcode to FIS")

      #send test time for EC reporting
      self.dut.driveattr['TEST_TIME']  = "0"
      DriveAttributes['TEST_TIME'] = self.dut.driveattr['TEST_TIME']

      #send WTF for EC reporting
      self.dut.driveattr['WTF'] = self.dut.WTF_EC_Backup
      DriveAttributes['WTF'] = self.dut.driveattr['WTF']

      if testSwitch.FE_SGP_EN_REPORT_RESTART_FAILURE and not (testSwitch.EN_REPORT_SAME_CAPACITY_WTF and (self.dut.pn_backup[5] == self.dut.driveattr['PART_NUM'][5])):
         evalOper = "%s" % self.dut.nextOper    #Send the data under the Oper run
      else:
         evalOper = "*%s" % self.dut.nextOper   #Send the data under the *Oper run

      objMsg.printMsg("evalOper=%s self.dut.pn_backup=%s self.dut.driveattr['PART_NUM']=%s" % (evalOper, self.dut.pn_backup, self.dut.driveattr['PART_NUM']))

      try:
         tmp_pn = DriveAttributes['PART_NUM']
         DriveAttributes.update({'CMS_CONFIG':'NONE'}) 
         DriveAttributes.update({'CMS_CONFIG':self.dut.driveattr["CMS_CONFIG"],'LOOPER_COUNT':1, 'PART_NUM': self.dut.pn_backup, 'DNGRADE_ON_FLY':self.dut.driveattr["DNGRADE_ON_FLY"]}) # LOOPER_COUNT to "disable" ADG
         ReportErrorCode(ec)
         RequestService('SetOperation',(evalOper,))
         RequestService('SendRun',(0,))
      finally:
         DriveAttributes['PART_NUM'] = tmp_pn
         DriveAttributes['LOOPER_COUNT'] = '0'                 # "enable" ADG
         ReportErrorCode(0)
         RequestService('SetOperation',(self.dut.nextOper,))   #Reset to the primary operation

      #restore WTF
      self.dut.driveattr['WTF'] = self.dut.WTF
      DriveAttributes['WTF'] = self.dut.driveattr['WTF']

   #-------------------------------------------------------------------------------------------------------
   def buildClusterList(self, updateWTF = 0):
      from base_GOTF import CGOTFGrading
      from StateMachine import CBGPN
      from CommitServices import isTierPN
      self.partNum = self.dut.partNum
      objMsg.printMsg("self.partNum: %s" %(self.partNum))
      self.oGOTF = CGOTFGrading()
      self.objBGPN = CBGPN(self.oGOTF)

      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         if (self.dut.driveattr['ORG_TIER'] in [TIER1, TIER2, TIER3]) or isTierPN( self.dut.partNum ):
            self.objBGPN.GetBGPN(reset_Manual_GOTF = 1)
      else:
         self.objBGPN.GetBGPN()

      self.keyCounter = 0

      self.nibletString = self.dut.serialnum[1:3] + '_'

      if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_VBAR_MSG:
         self.displayAttr()
      self.partNum = self.searchPN(self.partNum)


      if self.dut.Waterfall_Req == 'NONE' and not self.dut.depopMask:
      #if self.dut.Waterfall_Req[0] == 'N':
         objMsg.printMsg("Native, Waterfall_Req: %s " % (self.dut.Waterfall_Req ))
         waterfallType= 'Native'

         # Build niblet string for native waterfall
         if nibletTable[self.partNum][waterfallType][0]:
            self.nibletString += nibletTable[self.partNum][waterfallType][0]
            objMsg.printMsg("nibletString: %s" %(self.nibletString))
            objMsg.printMsg("Waterfall_Req found in nibletTable: %s " % (self.nibletString[3:5]))
            capacity = nibletTable[self.partNum]['Capacity'][self.keyCounter]
            if not '_' in capacity:    # a must to have the drive sector size.
               if testSwitch.WTFCheckSectorSize:
                  raiseException(12150, "ERROR: Drv_Sector_Size not defined at index %s in nibletTable" % self.keyCounter)
            self.nibletString += '_'
            self.nibletString += capacity
            objMsg.printMsg("Capacity found in nibletTable: %s " % (capacity))
            #=== Add part number to TP.VbarPartNumCluster
            self.BuildVbarPartNumCluster(self.partNum, self.keyCounter)
         else:
            objMsg.printMsg("ERROR: Can not find %s in nibletTable for PN %s" % (waterfallType, self.partNum))
            self.displayAttr()
            raiseException(12150, "ERROR: Can not find Waterfall_Req in nibletTable")

      else:
         # Handle non-native waterfall requests
         objMsg.printMsg("self.dut.depopMask: %s" % (self.dut.depopMask))
         objMsg.printMsg("self.dut.globaldepopMask: %s" % (self.dut.globaldepopMask))
         objMsg.printMsg("self.dut.Waterfall_Req[0]: %s" %( str(self.dut.Waterfall_Req[0])))

         # Choose the right row in the nibletTable
         if self.dut.Waterfall_Req[0] == 'R':
            if self.dut.depopMask:
               raiseException(12150, "ERROR: Waterfall_Req conflicts with Depop_Req")

            # set Waterfall_Req to matching value as in nibletTable
            if testSwitch.FORCE_WTF_SET_ATTR_BY_NIBLET_TABLE and self.dut.Waterfall_Req == 'REZONE':
               for nibletindex in range( len(nibletTable[self.partNum]['Capacity']) ):
                  rezone   = nibletTable[self.partNum]['Rezone'][nibletindex]
                  capacity = nibletTable[self.partNum]['Capacity'][nibletindex].split('_')[0]
                  if rezone == '': continue
                  if capacity not in TP.Native_Capacity:
                     self.dut.Waterfall_Req = rezone[0:2]
                     break

            objMsg.printMsg("Rezone, Waterfall_Req: %s" %( self.dut.Waterfall_Req))
            waterfallType= 'Rezone'
         elif self.dut.Waterfall_Req[0] == 'D' or self.dut.depopMask:
            waterfallType = 'Depop'
            objMsg.printMsg("self.dut.Depop_Done: %s" %(str(self.dut.Depop_Done)))
            #if self.dut.Depop_Done == 'NONE':
            numPhysHds = self.dut.Servo_Sn_Prefix_Matrix[self.dut.serialnum[1:3]]['PhysHds']
            if len(self.dut.globaldepopMask) == 0:
               self.dut.Waterfall_Req = 'D' + str(numPhysHds - len(self.dut.depopMask))
            else:
               self.dut.Waterfall_Req = 'D' + str(numPhysHds - len(self.dut.globaldepopMask))
            self.dut.driveattr['DEPOP_DONE'] = 'DONE'    # This could be set to done from previous run or this current run
            self.dut.Depop_Done = 'DONE'                 # This tells us if we have depopped during this operation
            # For rewrite AFH_SIM.bin when depop after AFH
            #DriveAttributes['OTF_DEPOP_MASK'] = self.dut.depopMask[0]
            objMsg.printMsg("Depop Heads: %s" %(self.dut.depopMask))
            objMsg.printMsg("Depop, Waterfall_Req: %s" %(self.dut.Waterfall_Req))
            objMsg.printMsg("Depop, Depop_Req: %s" %(self.dut.Depop_Req))
         else:
            objMsg.printMsg("ERROR: Bad Waterfall_Req: %s" % (self.dut.Waterfall_Req))
            self.displayAttr()
            raiseException(12150, "ERROR: Bad Waterfall_Req")

         objMsg.printMsg("%s, Waterfall_Req: %s" %(waterfallType, self.dut.Waterfall_Req))

         foundMatch = 0
         # Find the niblet key that matches the waterfall request
         for nibletkey in nibletTable[self.partNum][waterfallType]:
            objMsg.printMsg("keycounter:%s nibletKey: %s " % (self.keyCounter, nibletkey))
            objMsg.printMsg("Looping, Waterfall_Req: %s" %( self.dut.Waterfall_Req))
            if self.dut.Waterfall_Req in nibletkey:
               if len(nibletTable[self.partNum]['Capacity']) > self.keyCounter:
                  capacity = nibletTable[self.partNum]['Capacity'][self.keyCounter]
                  objMsg.printMsg("Capacity found in nibletTable: %s " % (capacity))
                  if '_' in capacity:
                     Drv_Sector_Size = capacity.split('_')[1]
                     if Drv_Sector_Size == self.dut.Drv_Sector_Size:
                        foundMatch = 1
                        break
                     elif not testSwitch.WTFCheckSectorSize:
                        objMsg.printMsg("NOT WTFCheckSectorSize")
                        foundMatch = 1
                        break
                  else:
                     if testSwitch.WTFCheckSectorSize:
                        raiseException(12150, "ERROR: Drv_Sector_Size not defined at index %s in nibletTable for ADG/Rerun drive" % self.keyCounter)

               else:
                  raiseException(12150, "ERROR: Capacity not defined at index %s in nibletTable for ADG/Rerun drive" % self.keyCounter)

            self.keyCounter += 1

         if foundMatch:
            objMsg.printMsg("Waterfall_Req(%s) and Drv_sector_Size(%s) found in nibletTable" % (nibletkey, self.dut.Drv_Sector_Size))
            self.nibletString += nibletkey + '_'
            if nibletkey.find('L')> -1:
               self.dut.Niblet_Level = nibletkey.split('L')[-1]
         else:
            self.displayAttr()
            raiseException(12150, "ERROR: Waterfall_Req or Drv_sector_Size not found in nibletTable for ADG/Rerun drive")

         # Add the capacity to the niblet string
         if len(nibletTable[self.partNum]['Capacity']) > self.keyCounter:
            capacity = nibletTable[self.partNum]['Capacity'][self.keyCounter]
            objMsg.printMsg("Capacity found in nibletTable: %s " % (capacity))
            self.nibletString += capacity
            if '_' in capacity:
               self.dut.Drv_Sector_Size = capacity.split('_')[1]
            elif testSwitch.WTFCheckSectorSize:
               raiseException(12150, "ERROR: Drv_Sector_Size not defined at index %s in nibletTable for ADG/Rerun drive" % self.keyCounter)
            #=== Add part number to TP.VbarPartNumCluster
            objMsg.printMsg("PN=%s, keyCounter=%d" % (self.partNum, self.keyCounter) )
            self.BuildVbarPartNumCluster(self.partNum, self.keyCounter)
         else:
            raiseException(12150, "ERROR: Capacity not defined at index %s in nibletTable for ADG/Rerun drive" % self.keyCounter)

      # Check for nibletLibrary in TP object first.  This allows the selection
      # of the proper nibletLibrary based on certain attributes like head type.
      nibletLibrary = getattr(TP, "nibletLibrary", None)
      if nibletLibrary is not None:
         objMsg.printMsg("Using nibletLibrary from TP")
      else:
         from PIF import nibletLibrary as nibletLibrary
         objMsg.printMsg("Using nibletLibrary from PIF")

      # Build the niblet cluster based on niblet strings
      TP.VbarNibletCluster = []     # List of niblets used by VBAR code
      self.VbarNibletCluster = []   # List of niblet data to help locate niblet in nibletTable
      while True:
         objMsg.printMsg("nibletString: %s" %(self.nibletString))

         # Validate presence of niblet string in niblet table
         if nibletLibrary.has_key(self.nibletString):
            objMsg.printMsg("keyCounter: %s Complete nibletstring found: %s" %(str(self.keyCounter),self.nibletString))
         else:
            objMsg.printMsg("Can not find complete nibletstring: %s in nibletLibrary" %(self.nibletString))

            if len(self.VbarNibletCluster) == 0 :
               self.displayAttr()
               raiseException(12150, "ERROR: Can not find complete niblet string in nibletLibrary")
            else:
               objMsg.printMsg("No more niblet, break")
               break

         # Add niblet to cluster structures
         if testSwitch.BF_0274769_321126_ALLOW_EMPTY_PN_FOR_NIBLETTABLE:
            # not native capacity if keyCounter > 0. Then need check if having demand for lower capacity
            if self.keyCounter == 0 or self.isValidNiblet(self.keyCounter):   
               TP.VbarNibletCluster.append(nibletLibrary[self.nibletString])
               self.VbarNibletCluster.append((self.keyCounter, self.nibletString))
         else:
            TP.VbarNibletCluster.append(nibletLibrary[self.nibletString])
            self.VbarNibletCluster.append((self.keyCounter, self.nibletString))

         #Abort loop if only native capacity is allowed
         if ConfigVars[CN].get('NativeWTFOnly',0) == 1:
            objMsg.printMsg("NativeWTFOnly, break")
            break

         self.keyCounter += 1    # Allow all niblets to be found

         # Search for the next niblet table entry
         for index,item in enumerate(nibletTable[self.partNum]['Capacity'][self.keyCounter:]):
            if nibletTable[self.partNum].get('Rezone','') and nibletTable[self.partNum]['Rezone'][self.keyCounter]:
               waterfallType = 'Rezone'
            elif nibletTable[self.partNum].get('Depop','') and nibletTable[self.partNum]['Depop'][self.keyCounter]:
               waterfallType = 'Depop'
            else:
               self.keyCounter += 1
               continue

            self.nibletString = self.dut.serialnum[1:3]
            self.nibletString += '_'
            self.nibletString += nibletTable[self.partNum][waterfallType][self.keyCounter]


            capacity = nibletTable[self.partNum]['Capacity'][self.keyCounter]
            if not '_' in capacity:    # a must to have the drive sector size.
               if testSwitch.WTFCheckSectorSize:
                  raiseException(12150, "ERROR: Drv_Sector_Size not defined at index %s in nibletTable" % self.keyCounter)
            self.nibletString += '_'
            self.nibletString += capacity

            objMsg.printMsg("Counter: %s" %(str(self.keyCounter)))
            #=== Add part number to TP.VbarPartNumCluster
            self.BuildVbarPartNumCluster(self.partNum, self.keyCounter)
            break

         # Abort loop if exhausted all the niblet table entries
         if testSwitch.SKIPZONE and self.dut.nextState == 'DEZONE':
            if (self.keyCounter == len(nibletTable[self.partNum]['Capacity'])):
               objMsg.printMsg("SKIPZONE: Auto rezone/depop, exiting loop for more nibletString")
               break
         else:
            if (self.keyCounter == len(nibletTable[self.partNum]['Capacity'])):
               objMsg.printMsg("Auto rezone/depop, exiting loop for more nibletString")
               break

      #if only native capacity is allowed
      if ConfigVars[CN].get('NativeWTFOnly',0) == 1:
         objMsg.printMsg("NativeWTFOnly = 1")
         self.updateWTF()
         self.displayAttr()
         if not self.dut.WTF == 'D0R0':
            objMsg.printMsg("WTF: %s which is not DORO for EN_WATERFALL = 0" % (self.dut.WTF))
            raiseException(12150, "ERROR: WTF is not DORO for NativeWTFOnly = 1")

      # to update WTF only
      if updateWTF:
         self.keyCounter, self.nibletString = self.VbarNibletCluster[0]
         self.updateWTF()
         if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_VBAR_MSG:
            self.displayAttr()
   
   #-------------------------------------------------------------------------------------------------------
   if testSwitch.BF_0274769_321126_ALLOW_EMPTY_PN_FOR_NIBLETTABLE:
      def isValidNiblet(self, nibletIndex):
         valid = False
         
         newPN = nibletTable[self.partNum]['Part_num'][nibletIndex].rstrip()
         if nibletIndex > 0 and len(newPN) > 0:
            valid = True
         elif nibletIndex == 0:
            valid = True
         
         return valid

   #-------------------------------------------------------------------------------------------------------
   def searchPN(self,partNum):
      objMsg.printMsg("searchPN: Search for valid PN")

      PN_found = 0

      if nibletTable.has_key(partNum):    #check for 9 digit PN 1st
         objMsg.printMsg("9 digits PN found: %s" % (partNum))
         PN_found = 1
      else:                               #check for 6 digit model number
         for item in nibletTable:
            if len(item) in [6,7] and partNum[0:len(item)] == item:
               partNum = item
               objMsg.printMsg("6 digits PN found: %s " % (partNum))
               if DEBUG:   objMsg.printMsg("nibletTable: %s " % (nibletTable[partNum]))
               PN_found = 1
               break

      if PN_found == 0:
         objMsg.printMsg("ERROR: PN: %s not found" %(partNum))
         self.displayAttr()
         raiseException(12150, "ERROR: PN not found")

      return partNum

   #-------------------------------------------------------------------------------------------------------
   def BuildVbarPartNumCluster(self, pn, cnt):
      newPN = nibletTable[pn]['Part_num'][cnt]
      if len(newPN):
         if len(newPN) in [6, 7]:
            TP.VbarPartNumCluster[cnt] = newPN.split('-')[0] + '-' + self.dut.partNum.split('-')[1]
         else:
            TP.VbarPartNumCluster[cnt] = newPN
      else:
         if testSwitch.BF_0274769_321126_ALLOW_EMPTY_PN_FOR_NIBLETTABLE:
            if len(TP.VbarPartNumCluster) - 1 < cnt:
               TP.VbarPartNumCluster.extend(['' for i in range(len(TP.VbarPartNumCluster), cnt + 1)])
            if cnt == 0: TP.VbarPartNumCluster[cnt] = self.dut.partNum
            else: TP.VbarPartNumCluster[cnt] = newPN
         elif cnt > 0:
            raiseException(12150, "No Waterfall Demmand")
         
      printDbgMsg("TP.VbarPartNumCluster[%d]: %s " % (cnt,TP.VbarPartNumCluster[cnt]))

   #-------------------------------------------------------------------------------------------------------
   def updateWTF(self, restart=False):
      from PIF import WTFTable, WTF_rpmTable
      objMsg.printMsg("updateWTF: WTF, Waterfall_Req, Waterfall_Done and Niblet_Level")

      self.dut.WTF_EC_Backup = self.dut.WTF

      ns_found = 0
      for wtfKey in WTFTable:
         if wtfKey[0:5] == self.nibletString[0:5]:
            objMsg.printMsg("WTF entry found: %s  WTF: %s" %(wtfKey,WTFTable[wtfKey]))
            self.dut.WTF = WTFTable[wtfKey]
            try:
               self.dut.WTF += WTF_rpmTable[self.dut.serialnum[1:3]][self.dut.driveattr['SPINDLE_RPM']]
            except:
               pass

            if self.dut.Depop_Req_Backup != 'NONE':
               self.dut.WTF = self.dut.WTF[0] + 'A' + self.dut.WTF[2:]

            if self.dut.Waterfall_Req_Backup != 'NONE':
               self.dut.WTF = self.dut.WTF[0:3] + 'A'

            self.dut.driveattr['WTF'] = self.dut.WTF
            ns_found = 1
            break

      if ns_found == 0:
         objMsg.printMsg("ERROR: Can not find WTF entry: %s in WTFTable" %(self.nibletString[0:5]))
         self.displayAttr()
         raiseException(12150, "ERROR: Can not find WTF entry in WTFTable")
      if self.dut.nextState == 'INIT':
         return

      # If the drive is native or a depop restart was requested, keep waterfall_req set to NONE
      if self.dut.Waterfall_Req == 'NONE' and (self.keyCounter == 0):   # Native
         self.dut.Waterfall_Done = 'NONE'
      elif restart:
         self.dut.Waterfall_Done = 'NONE'
         self.dut.Waterfall_Req = self.nibletString[3:5]
      else:
         self.dut.Waterfall_Done = 'DONE'
         self.dut.Waterfall_Req = self.nibletString[3:5]

      self.dut.Niblet_Level = self.nibletString[6]
      self.dut.Drv_Sector_Size = self.nibletString.split('_')[3]
      self.dut.driveattr['WATERFALL_DONE'] = self.dut.Waterfall_Done
      self.dut.driveattr['WATERFALL_REQ'] = self.dut.Waterfall_Req
      self.dut.driveattr['NIBLET_LEVEL'] = self.dut.Niblet_Level
      self.dut.driveattr['DRV_SECTOR_SIZE'] = self.dut.Drv_Sector_Size
      self.dut.driveattr['DEPOP_REQ'] = self.dut.Depop_Req
   
   #-------------------------------------------------------------------------------------------------------
   def updateATTR(self, partNum, keyCounter):
      from base_GOTF import CGOTFGrading
      from StateMachine import CBGPN
      objMsg.printMsg("updateATTR: updating the Partnumber/Business group")

      self.partNumOrg = self.dut.partNum
      self.oGOTF = CGOTFGrading()
      self.objBGPN = CBGPN(self.oGOTF)

      if (keyCounter != 0):
         if len(nibletTable[partNum]['Part_num'][keyCounter]) >2:   # need to change PN
            self.dut.partNum =  nibletTable[partNum]['Part_num'][keyCounter]
            if len(self.dut.partNum) in [6,7,10]:
               objMsg.printMsg("Len of PN(%s): %s " %(self.dut.partNum,len(self.dut.partNum)))
            else:
               objMsg.printMsg("ERROR: len of PN %s in nibletTable is not 6,7 or 10" %(self.dut.partNum))
               self.displayAttr()
               raiseException(12150, "ERROR: len of PN in nibletTable is not 6,7 or 10")
            if len(self.dut.partNum) in [6,7]:
               objMsg.printMsg("PN %s " %(self.dut.partNum))
               self.dut.partNum += self.partNumOrg[len(self.dut.partNum):10]

            if testSwitch.RELOAD_DEMAND_TABLE_ON_WTF:    # Reload DemandTable from PIF.py upon waterfall
               self.dut.demand_table = self.dut.DEMAND_TABLE[:]   # force demand table reload

            try: self.objBGPN.GetBGPN() # update BG
            except:
               try:
                  objMsg.printMsg("Looking for alternate PN")
                  if len(nibletTable[self.partNum]['altPart_num'][self.keyCounter]) == 10:
                     self.dut.partNum =  nibletTable[self.partNum]['altPart_num'][self.keyCounter]
                     self.objBGPN.GetBGPN() # update BG
                  else :      # no PN
                     objMsg.printMsg("ERROR: No altPN for PN update")
                     self.displayAttr()
                     raiseException(12150, "ERROR: No PN for PN update")
               except:
                  objMsg.printMsg("Waterfall: Part number %s not found in Manual_GOTF" % self.dut.partNum)
                  raiseException(13425, "Part number not found in Manual_GOTF")
            if self.oGOTF.gotfTestGroup(self.dut.BG) == False:
               objMsg.printMsg("ERROR: Wrong BG: %s while changing PN" %(self.dut.BG))
               self.displayAttr()
               raiseException(12150, "ERROR: Wrong BG while changing PN")

            self.dut.driveattr['PART_NUM'] = self.dut.partNum
            self.dut.setDriveCapacity()
            objMsg.printMsg('After WTF self.CAPACITY=%s' % self.dut.CAPACITY_PN)
            objMsg.printMsg('After WTF self.CAPACITY_CUS=%s' % self.dut.CAPACITY_CUS)
            HostSetPartnum(self.dut.partNum)
         else :      # no PN
            objMsg.printMsg("ERROR: No PN for PN update")
            self.displayAttr()
            raiseException(12150, "ERROR: No PN for PN update")
      else :
         objMsg.printMsg("No need to update PN")

      if not testSwitch.FE_0314243_356688_P_CM_REDUCTION_REDUCE_VBAR_MSG:
         self.displayAttr()

   #-------------------------------------------------------------------------------------------------------
   def displayAttr(self):
      objMsg.printMsg("--*******************--")
      objMsg.printMsg("SN              : %s " %(self.dut.serialnum) )
      objMsg.printMsg("PN              : %s " %(self.dut.partNum) )
      objMsg.printMsg("BG              : %s " %(self.dut.BG) )
      objMsg.printMsg("Waterfall_Req   : %s " %(self.dut.Waterfall_Req))
      objMsg.printMsg("Depop_Req       : %s " %(self.dut.Depop_Req))
      objMsg.printMsg("Depop_Done      : %s " %(self.dut.Depop_Done))
      objMsg.printMsg("depopMask       : %s " %(self.dut.depopMask))
      objMsg.printMsg("Niblet_Level    : %s " %(self.dut.Niblet_Level))
      objMsg.printMsg("Drv_Sector_Size : %s " %(self.dut.Drv_Sector_Size))
      objMsg.printMsg("Waterfall_Done  : %s " %(self.dut.Waterfall_Done))
      objMsg.printMsg("WTF             : %s " %(self.dut.WTF))
      objMsg.printMsg("--*******************--")

   #-------------------------------------------------------------------------------------------------------
   def resetWTFAttr(self):
      objMsg.printMsg("Reset WTF attributes")

      self.dut.WTF               = 'NONE'
      self.dut.Waterfall_Req     = 'NONE'
      self.dut.Waterfall_Done    = 'NONE'
      self.dut.Niblet_Level      = 'NONE'
      self.dut.Drv_Sector_Size   = 'NONE'
      self.dut.Depop_Req         = 'NONE'

      self.dut.driveattr['WTF']              = self.dut.WTF
      self.dut.driveattr['WATERFALL_DONE']   = self.dut.Waterfall_Done
      self.dut.driveattr['WATERFALL_REQ']    = self.dut.Waterfall_Req
      self.dut.driveattr['NIBLET_LEVEL']     = self.dut.Niblet_Level
      self.dut.driveattr['DRV_SECTOR_SIZE']  = self.dut.Drv_Sector_Size
      self.dut.driveattr['DEPOP_REQ']        = self.dut.Depop_Req

      self.displayAttr()
