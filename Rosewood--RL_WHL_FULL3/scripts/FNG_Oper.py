#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: FNG2 operation and Drive grading based on Reli's CTU grading criteria
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/FNG_Oper.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/FNG_Oper.py#1 $
# Level: 2
#---------------------------------------------------------------------------------------------------------#
from Constants import *

from State import CState
import MessageHandler as objMsg
import ScrCmds
import PIF
from base_GOTF import CGOTFGrading


###########################################################################################################
class CReliCTU(CState):
   #-------------------------------------------------------------------------------------------------------
   def __init__(self, dut, params={}):
      self.params = params
      depList = []
      CState.__init__(self, dut, depList)

   #-------------------------------------------------------------------------------------------------------
   def run(self):

      EC = 14645

      CTU_grading = 0
      ProcessIndex = 0 
      BGIndex = 0
      ReliaIndex = 0 

      self.dut.CTU_SCORE = DriveAttributes.get('CTU_SCORE', 'NONE') 
      self.BG = DriveAttributes.get('BSNS_SEGMENT', 'NONE')

      if self.BG == 'NONE':
         objMsg.printMsg("ERROR: BG = NONE")
         ScrCmds.raiseException(EC, "ERROR: BG = NONE")
      elif (self.BG != self.dut.BG) :
         objMsg.printMsg("ERROR: self.dut.BG:%s != FIS attribute:%s" %(self.dut.BG, self.BG))
         ScrCmds.raiseException(EC, "ERROR: self.dut.BG != FIS attribute")

      self.displayAttr()

      if self.dut.CTU_SCORE == 'NONE':
         objMsg.printMsg("ERROR: CTU_SCORE = NONE")
         ScrCmds.raiseException(EC, "ERROR: CTU_SCORE = NONE")
      elif self.dut.CTU_SCORE == 'CTU_FAIL':
         objMsg.printMsg("ERROR: CTU_SCORE = CTU_FAIL")
         ScrCmds.raiseException(EC, "ERROR: CTU_SCORE = CTU_FAIL")
      elif not PIF.CTUGradingTable.count(self.dut.BG) == 1 :
         objMsg.printMsg("ERROR: Error finding BG in DemandTable" %(self.dut.BG))
         self.displayAttr()
         ScrCmds.raiseException(EC, "ERROR: Error finding BG in DemandTable")
      else:

         objMsg.printMsg("ReliaTable: %s" %(PIF.ReliaTable[self.dut.CTU_SCORE]))
         objMsg.printMsg("ProcessTable: %s" %(PIF.ProcessTable))

         if PIF.ReliaTable[self.dut.CTU_SCORE][0] == 'ALL':
            PIF.ReliaTable[self.dut.CTU_SCORE] = PIF.CTUGradingTable
            objMsg.printMsg("New ReliaTable: %s" %(PIF.ReliaTable[self.dut.CTU_SCORE]))

         if PIF.ProcessTable[0] == 'ALL':
            PIF.ProcessTable = PIF.CTUGradingTable
            objMsg.printMsg("New ProcessTable: %s" %(PIF.ProcessTable))

         for reliaBG in PIF.ReliaTable[self.dut.CTU_SCORE] :

            objMsg.printMsg("***-- reliaBG : %s --***" %reliaBG)

            if not PIF.CTUGradingTable.count(reliaBG) == 1 :
               objMsg.printMsg("ERROR: Error finding reliaBG in DemandTable" %(self.dut.BG))
               self.displayAttr()
               ScrCmds.raiseException(EC, "ERROR: Error finding reliaBG in DemandTable")

            BGIndex = PIF.CTUGradingTable.index(self.dut.BG)
            ReliaIndex = PIF.CTUGradingTable.index(reliaBG)
            objMsg.printMsg("BGIndex      : %s " %BGIndex)
            objMsg.printMsg("ReliaIndex   : %s " %ReliaIndex)

            if ReliaIndex < BGIndex :
               continue

            for processBG in PIF.ProcessTable:
               objMsg.printMsg("processBG    : %s " %processBG)

               if not PIF.CTUGradingTable.count(processBG) == 1 :
                  objMsg.printMsg("ERROR: Error finding processBG in DemandTable" %(processBG))
                  self.displayAttr()
                  ScrCmds.raiseException(EC, "ERROR: Error finding processBG in DemandTable")

               ProcessIndex = PIF.CTUGradingTable.index(processBG)
               objMsg.printMsg("ProcessIndex : %s " %ProcessIndex)

               if ProcessIndex != ReliaIndex:
                  continue

               if ProcessIndex > BGIndex :
                  objMsg.printMsg("Change BG to %s" %processBG)
                  self.dut.BG = processBG

                  # search back BG -> PN
                  objMsg.printMsg("Business group changed to %s" %(self.dut.BG))

                  self.oGOTF = CGOTFGrading()
                  if self.oGOTF.gotfTestGroup(self.dut.BG) == False:
                     objMsg.printMsg("ERROR: Wrong BG: %s to change to, failed GOTF" %(self.dut.BG))
                     self.displayAttr()
                     ScrCmds.raiseException(EC, "ERROR: Wrong BG to change to, failed GOTF")
                     continue

                  if len(PIF.Manual_GOTF) > 0:
                     pn = self.dut.manual_gotf[self.dut.BG][self.dut.bgIndex]
                     if len(pn) != 10:    # safety net
                        objMsg.printMsg("ERROR: Incorrect PN")
                        ScrCmds.raiseException(EC, "ERROR: Incorrect PN")

                     self.dut.partNum = pn
                     self.dut.driveattr['BSNS_SEGMENT'] = self.dut.BG
                     self.dut.driveattr['PART_NUM'] = self.dut.partNum
                     objMsg.printMsg("Part number changed to %s" % str(self.dut.partNum))
                  else:
                     objMsg.printMsg("ERROR: Can not find manual_gotf table")
                     ScrCmds.raiseException(EC, "ERROR: Can not find manual_gotf table")

                  CTU_grading = 1
                  break

               else:
                  objMsg.printMsg("No change to BG %s" %(self.dut.BG))
                  CTU_grading = 1   #up to here, meaning CTU grading is done at least once
                  break

            if CTU_grading:
               break

      if not CTU_grading :
         objMsg.printMsg("ERROR: ReliaTable can not match ProcessTable or DemandTable")
         ScrCmds.raiseException(EC, "ERROR: ReliaTable can not match ProcessTable or DemandTable")

      self.displayAttr()

   #------------------------------------------------------------------------------------------------------#
   def displayAttr(self):
      objMsg.printMsg("--*******************--")
      objMsg.printMsg("PN        : %s " %(self.dut.partNum) )
      objMsg.printMsg("BG        : %s " %(self.dut.BG) )
      objMsg.printMsg("CTU_SCORE : %s " %(self.dut.CTU_SCORE) )
      objMsg.printMsg("--*******************--")


