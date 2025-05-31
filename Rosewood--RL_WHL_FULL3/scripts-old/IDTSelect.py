#-----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2002, All rights reserved                     #
#-----------------------------------------------------------------------------------------# 

##############################################################################
#
# $RCSfile: IDTSelect.py,v $
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $Revision: #1 $
# $Id: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/IDTSelect.py#1 $
# $Date: 2016/05/05 $
# $Author: chiliang.woo $
# $Source: /usr/local/cvsroot/PSG_GeminiScripts/IDTSelect.py,v $
#
##############################################################################

# Definition of CMS Values
#    "Cx-LOOPS"   : "Number of Loops",
#    "Cx-COUNT"   : "Quantity Required",
#    "Cx-LOGIC"   : "Logical Condition",
#    "Cx-EXPNS"   : ['Part Number1', 'Part Number2',],
#    "Cx-PNUM"    : ['Part Number', 'Product', 'Family',],
#    "Cx-ATTR1"   : ['Attr1 Name', 'Attr Value', 'Quantity'],
#    "Cx-ATTR2"   : ['Attr1 Name', 'Attr Value', 'Quantity'],
#    "Cx-ATTR3"   : ['Attr1 Name', 'Attr Value', 'Quantity'],
#    "Cx-TIMES"   : ['Start Time', 'End Time', 'Num Hours', 'Test Time', 'Drives/Slot/Day'],
#    "Cx-GLIST"   : ['Number of Hosts', ['Gemini by Floor','Gemini by Line','Gemini by Oven']],
#-----------------------------------------------------------------------------------------#
from Constants import *
import MessageHandler as objMsg

class IDTSelect:

   def __init__(self):
       self.OK = 0
       self.ON = 1
       self.OFF = 0
       self.PASS = 0
       self.FAIL = -1
       self.RunDrive  = 0
       self.RunForced = 0
       self.AttrDict  = {}
       self.ConfigMatch = self.FAIL
       self.AttributeMatch = self.FAIL

   #-----------------------------------------------------------------------------------------# 
   def DemandCheck(self, TestType):
       self.TestType = TestType
       objMsg.printMsg('********************************************************************')

       #return self.OFF
       self.FindPNConfig()
       if self.ConfigMatch == self.FAIL: return self.OFF

       self.DisplayCriteria()
       self.CheckCriteria()
       if self.AttributeMatch == self.PASS:
          self.SetupAttrMatch()

          try:
             result = RequestService('AllowODTRun',(self.ConfigID, self.HostCfgCount, self.HostMax, \
                                      self.GemList, self.StartTime, self.EndTime, self.ProdMax))

             objMsg.printMsg('SelectCriteria AllowODTRun result = %s %s' % (result[0],result[1]))
             if result[1] == self.OK: self.RunDrive = self.ON
          except:
             objMsg.printMsg('SelectCriteria AllowODTRun Host Service Not Supported')

       objMsg.printMsg('SelectCriteria AllowODTRun Config-%s RunDrive=%d' % (self.ConfigID, self.RunDrive))
       objMsg.printMsg('********************************************************************')
       return self.RunDrive

   #-----------------------------------------------------------------------------------------# 
   def FindPNConfig(self):
       D_Msg = self.ON 
       CE,CP,CN,CV = ConfigId                 #Equip, Product, Name, Version from Config
       self.ConfigID = DriveAttributes['PART_NUM']        # ConfigID = Drive Part Number
       ConfigVars[CN]['GIO_SelectConfig'] = ConfigVars[CN].get('GIO_SelectConfig','GIO_SELECT')
       self.SelectConfig = ConfigVars[CN]['GIO_SelectConfig']
       self.CMSConfigVars = RequestService('GetCMSConfigVars',(self.SelectConfig,))
       self.SelectCriteria = self.CMSConfigVars[1]
       if len(self.SelectCriteria) < 1:
          objMsg.printMsg('Invalid or Unmapped CMS Config')
          objMsg.printMsg('SelectCriteria ConfigID   = %s' % self.ConfigID)
          objMsg.printMsg('SelectCriteria ConfigName = %s' % self.SelectConfig)
          objMsg.printMsg('SelectCriteria ConfigVars = %s' % self.SelectCriteria)
          #objMsg.printMsg('SelectCriteria GetCMSConfigVars = %s' % self.CMSConfigVars)
          self.ConfigMatch == self.FAIL
       else:
          self.ExcludedPN = self.PASS
          objMsg.printMsg('SelectCriteria ConfigID = %s' % self.ConfigID)
          for loop in range(1,self.SelectCriteria['Criteria Count']+1): 
             self.CxExpns = ('C%d-EXPNS' % loop)
             if self.SelectCriteria.has_key(self.CxExpns) != 0:
                if D_Msg: objMsg.printMsg('SelectCriteria Has Excluded PN ConfigVar %s %s' % \
                          (self.CxExpns, self.SelectCriteria[self.CxExpns]))

                for NumExpn in range(len(self.SelectCriteria[self.CxExpns])):
                    #objMsg.printMsg('NumExpn %d CxExpn %s' % (NumExpn,self.SelectCriteria[self.CxExpns][NumExpn]))
                    ExpnConfigID = self.ConfigID[0]
                    #objMsg.printMsg('ExpnConfigID %s' %  ExpnConfigID)
                    for Char in range(1,len(self.SelectCriteria[self.CxExpns][NumExpn])):
                        #objMsg.printMsg('Char %d CxExpnChar %s' % (Char,self.SelectCriteria[self.CxExpns][NumExpn][Char]))
                        if self.SelectCriteria[self.CxExpns][NumExpn][Char] == '?':
                           ExpnConfigID += '?' 
                        else:
                           ExpnConfigID += self.ConfigID[Char] 
                        #objMsg.printMsg('ExpnConfigID %s' %  ExpnConfigID)

                    if D_Msg: objMsg.printMsg('SelectCriteria ConfigID %s ExConfigID %s ExPartNum %s' % \
                              (self.ConfigID, ExpnConfigID, self.SelectCriteria[self.CxExpns][NumExpn]))

                    if ExpnConfigID == self.SelectCriteria[self.CxExpns][NumExpn]:
                       objMsg.printMsg('SelectCriteria Excluded Part Number Match - Drive Excluded')
                       self.ExcludedPN = self.FAIL                      # Fail selection if Part number is Excluded 
                       self.ConfigMatch = self.FAIL
                       break
                    else:
                       objMsg.printMsg('SelectCriteria Excluded Part Number NO Match - Drive Not Excluded')
             else:
                objMsg.printMsg('SelectCriteria No Excluded PN ConfigVar %s' % self.CxExpns)

          if self.ExcludedPN == self.PASS:                       # Continue if part number is not excluded
             if D_Msg: 
                #objMsg.printMsg('SelectCriteria ConfigID   = %s' % self.ConfigID)
                objMsg.printMsg('SelectCriteria ConfigName = %s' % self.SelectConfig)
                objMsg.printMsg('SelectCriteria ConfigVars = %s' % self.SelectCriteria)
                objMsg.printMsg('SelectCriteria Prod Max Count = %s' % self.SelectCriteria['Prod Max Count'])
                objMsg.printMsg('SelectCriteria Host Max Count = %s' % self.SelectCriteria['Host Max Count'])
                objMsg.printMsg('SelectCriteria Criteria Count = %s' % self.SelectCriteria['Criteria Count'])
             for loop in range(1,self.SelectCriteria['Criteria Count']+1): 
                self.CxPnum =  ('C%d-PNUM' % loop)
                self.CxTable = ('C%d-' % loop)
                if D_Msg: objMsg.printMsg('SelectCriteria PN = %s %s' % (self.CxPnum, self.SelectCriteria[self.CxPnum]))
                if self.ConfigID in self.SelectCriteria[self.CxPnum]:
                   self.ConfigMatch = self.PASS; break
                elif self.ConfigID[:6] in self.SelectCriteria[self.CxPnum]: 
                     self.ConfigMatch = self.PASS
                     self.ConfigID = self.ConfigID[:6]; break
                elif self.ConfigID[:3] in self.SelectCriteria[self.CxPnum]: 
                     self.ConfigMatch = self.PASS
                     self.ConfigID = self.ConfigID[:3]; break
                else:
                     objMsg.printMsg('SelectCriteria Config-%s - %s - %s Not Found in %s' % \
                            (self.ConfigID, self.ConfigID[:6], self.ConfigID[:3], self.CxPnum))

          if self.ConfigMatch == self.PASS:
             objMsg.printMsg('SelectCriteria Config-%s Found in Criteria Table %s' % (self.ConfigID, self.CxPnum))
          elif self.ExcludedPN == self.FAIL:
             objMsg.printMsg('SelectCriteria PN-%s Excluded in %s %s' % \
               (self.ConfigID, self.CxExpns, self.SelectCriteria[self.CxExpns]))
          else:
             objMsg.printMsg('SelectCriteria Config-%s - %s - %s Not Found in Criteria Table' % \
                    (self.ConfigID, self.ConfigID[:6], self.ConfigID[:3]))
       return 0

   #-----------------------------------------------------------------------------------------# 
   def DisplayCriteria(self):
       self.AttrNum = 0
       while self.SelectCriteria:     # Loop until break # Display All before Match Check
           self.AttrNum += 1
           self.AttrName = ('%sATTR%d' % (self.CxTable, self.AttrNum))
           if self.SelectCriteria.has_key(self.AttrName) == 0: break
           objMsg.printMsg('SelectCriteria Config-%s %s: %s' % \
                  (self.ConfigID, self.AttrName, self.SelectCriteria[self.AttrName]))
       return 0

   #-----------------------------------------------------------------------------------------# 
   def CheckCriteria(self):
       D_Msg = 1
       self.AttrNum = 0
       while self.SelectCriteria:     # Loop until break # Check all Attributes for Match
           self.AttrNum += 1
           self.AttrName = ('%sATTR%d' % (self.CxTable, self.AttrNum))
           self.LoopName  = ('%sLOOPS' % self.CxTable)
           self.CountName = ('%sCOUNT' % self.CxTable)
           self.LogicName = ('%sLOGIC' % self.CxTable)
           self.TimeName  = ('%sTIMES' % self.CxTable)
           self.GListName = ('%sGLIST' % self.CxTable)
           if self.SelectCriteria.has_key(self.AttrName) == 0: break
           if DriveAttributes.has_key(self.SelectCriteria[self.AttrName][0]):
              self.KeyName  = self.SelectCriteria[self.AttrName][0]
              self.KeyValue = DriveAttributes[self.SelectCriteria[self.AttrName][0]]
              self.CriteriaValue = self.SelectCriteria[self.AttrName][1]
              #objMsg.printMsg('')
              objMsg.printMsg('SelectCriteria Config-%s %s: Key Found=%s SeatrackValue=%s CriteriaValue=%s' % \
                     (self.ConfigID, self.AttrName, self.KeyName, self.KeyValue, self.CriteriaValue))
              if self.KeyValue != self.CriteriaValue: 
                 objMsg.printMsg('SelectCriteria Config-%s %s: Seatrack Value Does Not Match Criteria Table' % \
                        (self.ConfigID, self.AttrName))
                 if self.SelectCriteria[self.LogicName] == 'ALL MATCH':
                    objMsg.printMsg('SelectCriteria Config-%s %s: All Criteria Does Not Match - FAIL Selection' % \
                           (self.ConfigID, self.AttrName))
                    self.AttributeMatch = self.FAIL
                    break 
                 else:
                    objMsg.printMsg('SelectCriteria Config-%s %s: Does Not Match Criteria - Check Next Attribute' % \
                           (self.ConfigID, self.AttrName))
              else:
                 self.AttrMax  = self.SelectCriteria[self.AttrName][2]
                 self.NumRuns  = self.SelectCriteria[self.TimeName][4]
                 self.NumHosts = self.SelectCriteria[self.GListName][0]
                 self.MatchLogic = self.SelectCriteria[self.LogicName]
                 self.AttrPerHost = (self.AttrMax / (self.NumHosts * self.NumRuns))
                 objMsg.printMsg('SelectCriteria Config-%s %s: %s AttrMax=%s NumRuns=%s NumHosts=%s AttrPerHost=%s' % \
                        ( self.ConfigID, self.AttrName, self.MatchLogic, self.AttrMax, \
                 self.NumRuns,   self.NumHosts,   self.AttrPerHost ))
                 self.AttrKeyName = ('%s_%s' % (self.KeyName, self.KeyValue))
                 self.AttrDict[self.AttrKeyName] = self.AttrPerHost
                 self.MatchKeyValue = self.CriteriaValue
                 if D_Msg: objMsg.printMsg('SelectCriteria AttrDict = %s' % self.AttrDict)
                 self.AttributeMatch = self.PASS
                 objMsg.printMsg('SelectCriteria Config-%s %s: Seatrack Value Matchs Criteria Table' % \
                        (self.ConfigID, self.AttrName))
           else:
              objMsg.printMsg('SelectCriteria Config-%s %s: Key Not Found=%s' % \
                     (self.ConfigID, self.AttrName, self.SelectCriteria[self.AttrName][0]))
              if self.SelectCriteria[self.LogicName] == 'ALL MATCH':
                 objMsg.printMsg('SelectCriteria Config-%s %s: All Criteria Does Not Match - FAIL Selection' % \
                        (self.ConfigID, self.AttrName))
                 self.AttributeMatch = self.FAIL
                 break 
              else:
                 objMsg.printMsg('SelectCriteria Config-%s %s: Key Not Found=%s - Check Next Attribute' % \
                        (self.ConfigID, self.AttrName, self.SelectCriteria[self.AttrName][0]))
       return 0

   #-----------------------------------------------------------------------------------------# 
   def SetupAttrMatch(self):
       self.StartTime    = self.SelectCriteria[self.TimeName][0]
       self.EndTime      = self.SelectCriteria[self.TimeName][1]
       self.GemList      = self.SelectCriteria[self.GListName][1]
       self.ProdMax      = self.SelectCriteria['Prod Max Count']
       self.HostMax      = self.SelectCriteria['Host Max Count']
       self.CfgCount     = self.SelectCriteria[self.CountName]
       self.NumHosts     = self.SelectCriteria[self.GListName][0]
       self.NumRuns      = self.SelectCriteria[self.TimeName][4]
       self.TestTime     = self.SelectCriteria[self.TimeName][3]
       self.TotalHours   = self.SelectCriteria[self.TimeName][2]
       self.HostCfgCount = (self.CfgCount / (self.NumHosts * self.NumRuns))
       self.ConfigID     = self.ConfigID + '_' + self.MatchKeyValue

       objMsg.printMsg('SelectCriteria Attribute Criteria Match Found ---------------------')
       objMsg.printMsg('SelectCriteria Config-%s StartTime=%s EndTime=%s HoursPerDay=%0.0f' % \
              ( self.ConfigID, self.StartTime, self.EndTime, self.TotalHours)) 
       objMsg.printMsg('SelectCriteria Config-%s TestTime=%0.0f RunsPerDay/PerHost=%0.0f' % \
              ( self.ConfigID, self.TestTime, self.NumRuns)) 
       objMsg.printMsg('SelectCriteria Config-%s ProdMaxCount=%s HostMaxCount=%s' % \
              ( self.ConfigID, self.ProdMax, self.HostMax))
       objMsg.printMsg('SelectCriteria Config-%s TotalCfgCount=%s HostCfgCount=%s' % \
              ( self.ConfigID, self.CfgCount, self.HostCfgCount))
       objMsg.printMsg('SelectCriteria Config-%s NumHosts=%s GeminiList=%s' % \
              ( self.ConfigID, self.NumHosts, self.GemList)) 
       objMsg.printMsg('SelectCriteria Config-%s TestLoops=%d AttrList=%s' % \
              ( self.ConfigID, self.SelectCriteria[self.LoopName], self.AttrDict))
       return 0

#-----------------------------------  End of File  ---------------------------------------#

