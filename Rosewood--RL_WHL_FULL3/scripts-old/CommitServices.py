#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2011, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: This is the main class to implement the Customer Configuration functionality.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CommitServices.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CommitServices.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------

from Constants import *
import traceback, re
import PIF
import MessageHandler as objMsg
from TestParamExtractor import TP
import ScrCmds
from Drive import objDut

tierList = [TIER1, TIER2, TIER3]


def dcm(_func):
   """
   Decorator to prevent redundant DCM calls for same part number.
   """
   instances = {}
  
   def getinstance(*args, **kwargs):
       
      if ((_func, kwargs.get('partNum')) not in instances.items()) or kwargs.get('force', False):
         instances.clear()                            # if new part number is called clear the old instance 
         instances[_func] = kwargs.get('partNum')     # remember the last PN call
         return _func(*args, **kwargs)                # allow DCM call for new PN or user choose force

      return objDut.driveConfigAttrs                  # return the existing DCM data for same PN

   return getinstance

def makeModelNumFisReady(rawModelNum, interfaceType):

   if interfaceType == 'SAS':
      #SAS
      model_1 = '[%-24s]' %  (rawModelNum[0:24],)
      model_2 = '[%s]' % ('',)
   else:
      #SATA
      model_1 = '[%-30s]' %  (rawModelNum[0:30],)
      model_2 = '[%-10s]' % (rawModelNum[30:],)

   return model_1, model_2

def parseAttrQualifiers(data):
   """
   Parses the drive attribute qualifiers from FIS
   """
   if 'FAILCODE' in data:
      return []
   return [req.split(':') for req in data] #name, relationship, value

def validateResults(results):  
   """
   Handle invalid entry appended by host e.g 'SERVER_ERROR=NO ERROR'
   """
   for dcmEntry in results:
      if len(dcmEntry) != 3:
         dcmParams = dcmEntry[0].split("=")
         if len(dcmParams) == 2:     #name, value
            results[results.index(dcmEntry)]=[dcmParams[0], '=', dcmParams[1]]
         else:
            ScrCmds.raiseException(11044, "Invalid DCM data : %s " %dcmEntry)
   return results

@dcm
def getDriveConfigAttributes(partNum = None, failInvalidDCM = False):
   """
   Get the drive attributes from the DCM/Autocommit FIS server
   """

   driveConfigAttrs = {}
   if ConfigVars[CN].get('DCC_PRE_RELEASE', 0):
      data = RequestService("DCMServerRequest",("GetLatest_DriveConfigAttributes",(self.dut.partNum,)))[1]['DATA']
   else:
      data = RequestService("DCMServerRequest", ("GetDriveConfigAttributes",(self.dut.partNum,)))[1]['DATA']
   if DEBUG:
      objMsg.printMsg("'data' from RequestService('GetDriveConfigAttributes'): %s" % data) #Seeing what is returned by the DCM can be helpful for debug
   if testSwitch.virtualRun:
      if testSwitch.FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS:
         custModel = getattr(TP, 'veModelNum','ST3500410AS')
         custModel1, custModel2 = makeModelNumFisReady(custModel, 'SATA')
         #'CUST_MN_JUSTIFY:=:RIGHT',
         data = ['STATUS:=:PASS',
                 'CUST_MN_JUSTIFY:=:LEFT', 'CUST_MODEL_NUM:=:%s' % custModel1, 'CUST_MODEL_NUM2:=:%s' % custModel2,
                 'DRV_MODEL_NUM:=:%s' % getattr(TP, 'veModelNum','ST3500410AS'),
                 'TC_LABEL_BLK_PN:=:100545501',
                 'USER_LBA_COUNT:=:312581808',
                 'SERVER_ERROR:=:NO ERROR',
                 'ZERO_PTRN_RQMT:=:20',
                 'CUST_TESTNAME:=:',
                 'BSNS_SEGMENT:=:STD',]
                 #'SECURITY_TYPE:=:TCG',]
      else:
         custModel = getattr(TP, 'veModelNum','ST3500410AS')
         data = ['STATUS:=:PASS',
                 'CUST_MN_JUSTIFY:=:LEFT',
                 'CUST_MODEL_NUM:=:%s' % custModel,
                 'DRV_MODEL_NUM:=:%s' % getattr(TP, 'veModelNum','ST3500410AS'),
                 'TC_LABEL_BLK_PN:=:100545501',
                 'USER_LBA_COUNT:=:312581808',
                 'SERVER_ERROR:=:NO ERROR',
                 'ZERO_PTRN_RQMT:=:10',
                 'CUST_TESTNAME:=:',
                 'BSNS_SEGMENT:=:STD',]

   objMsg.printMsg("%s DCM data = %s" %(partNum, data))

   try:
      #Parse the response from the host
      results = parseAttrQualifiers(data)
      #if we received valid data then we set variables.
      if len(results) > 0:
         results = validateResults(results)
         for name, relationship, value in results:
            driveConfigAttrs[name] = [relationship, value]
         # use below for simulation to force a dcm attribute
         #if 'CUST_TESTNAME' in self.dut.driveConfigAttrs:
         #   if 'DV3' not in self.dut.driveConfigAttrs['CUST_TESTNAME'][1]:
         #      self.dut.driveConfigAttrs['CUST_TESTNAME'][1] += 'DV3' # add lnog dst
   except:
      
      objMsg.printMsg("Results from parseAttrs: %s" % (data,),objMsg.CMessLvl.VERBOSEDEBUG)
      objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
      objMsg.printMsg("Custom Drive Attributes not supported in Host/FIS.")
      if (ConfigVars[CN].get('PRODUCTION_MODE',0) and testSwitch.FE_0173503_357260_P_RAISE_EXCEPTION_IF_UNABLE_TO_READ_DCM) or failInvalidDCM:
         ScrCmds.raiseException(14761, "Custom Drive Attributes - DCM not supported in Host/FIS.")

   return driveConfigAttrs

def getSixDigTLA(partNum, includeDash = True):
   """
   Returns 6digit TLA plus '-' as requested by includeDash (default True)
   """
   if includeDash:
      return partNum[:7]
   else:
      return partNum[:6]

def isTierPN(partNum):
   return getTab(partNum) in tierList

def getTab(partNum, includeDash = False):
   if includeDash:
      return partNum[-4:]
   else:
      return partNum[-3:]

def getNextTier( partNum ):

   partNum, tier = convertPNtoTier(partNum)
      
   try:
      return tierList[tierList.index(tier):][1]
   except IndexError:
      return None

def convertPNtoTier( partNum ):
   """
   Function converts the input PN to the tiered PN it is associated with
   input: full partNum
   output: partNum[:6]-TIER_TAB, TIER_TAB
   EG: input: 1CH162-501 output: 1CH162-T01
   *if no match then defaultBottomTier is returned (default 'T03')
   """
   
   tab = getTab(partNum)
   if tab in tierList:
      return partNum, tab

   tieredPnMatrix = getattr(PIF, 'tieredPnMatrix', {})
   defaultBottomTier = getattr(PIF, 'defaultBottomTier', TIER3)
   #format is dict {'Txx': [regex list of tab]}
   outputTier = None
   for tier in tieredPnMatrix:
      for tabRegEx in tieredPnMatrix[tier]:
         if re.search(tabRegEx, tab): #does it match
            outputTier = tier
            break
      if outputTier != None:
         break
   if outputTier == None:
      outputTier = defaultBottomTier

   pnTier = getSixDigTLA(partNum) + outputTier

   return pnTier, outputTier

def getBusinessGroup( tab, ManualGotfSub ):
   """
   Find the business group for the input tab and gotf relationship sub-matrix
   """
   bg = None
   pn = None
   if len(tab) > 3:  # Support for part number input for ScPk Manual_GOTF structure
      pn = tab
      tab = getTab(tab)
   tab2 = '-' + tab
   for bgVal in ManualGotfSub.keys():
      pnList = ManualGotfSub[bgVal]
      if (tab in pnList) or (tab2 in pnList) or (pn in pnList):
         bg = bgVal
   return bg

def setFN_PN(currentPN, tierTab):
   """
   Set FN_PN drive attribute with original tier and the final tier and associated business segment
   for serialized yield report
   EG - T01 dive commits to being 1CH162-305 (T03 drive) at the end of test process, FN_PN=T01->T03_STD
   """
   from PIF import Manual_GOTF
   temp, tieredTO = convertPNtoTier(currentPN)  #Don't need temp, which equals pnTier from convertPNtoTier
   #bg = getBusinessGroup(getTab(currentPN), Manual_GOTF['Base'])    # LCO method
   bg = getBusinessGroup(currentPN, objDut.manual_gotf)              # ScPk method
   try:
      finalPN = tierTab + '->' + tieredTO + '_' + bg
   except:
      objMsg.printMsg("Traceback %s." %traceback.format_exc())
      objDut.driveattr['COMMIT_DONE'] = "FAIL"
      ScrCmds.raiseException(11900, "Unable to commit to any part number!")

   objMsg.printMsg("Original Tier to Final Tier and Business Segment : %s" % (finalPN))

   return finalPN
