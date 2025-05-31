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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CCABuildCfg.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CCABuildCfg.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from Test_Switches import testSwitch
from Process import CProcess
from Drive import objDut
import ScrCmds
import MessageHandler as objMsg


DEBUG = 1

class CCustomCfg(CProcess):
   def __init__(self):
      CProcess.__init__(self)
      self.dut = objDut

      self.custAttrHandlers = {
                     'BYTES_PER_SCTR'     : self.autoValidateDCMAttrString,
                     'BSNS_SEGMENT'       : self.autoValidateDCMAttrString,
                     'CFG'                : self.autoValidateDCMAttrString,
                     'CUST_MODEL_NUM'     : self.autoValidateDCMAttrString,
                     'CUST_TESTNAME'      : self.autoValidateDCMAttrString,
                     'CUST_TESTNAME_2'    : self.autoValidateDCMAttrString,
                     'CUST_TESTSUP_2'     : self.autoValidateDCMAttrString,
                     'CUST_TESTNAME_3'    : self.autoValidateDCMAttrString,
                     'CUST_TESTSUP_3'     : self.autoValidateDCMAttrString,
                     'DLP_SETTING'        : self.autoValidateDCMAttrString,
                     'FMT_PROT_TYPE'      : self.autoValidateDCMAttrString,
                     'SED_LC_STATE'       : self.autoValidateDCMAttrString,
                     'SHIP_MODE_SENSE'    : self.autoValidateDCMAttrString,
                     'TIME_TO_READY'      : self.autoValidateDCMAttrFloat,
                     'WWN'                : self.autoValidateWWNAttr,
                     'USER_LBA_COUNT'     : self.autoValidateDCMAttrLBAs,
                     'ZERO_PTRN_RQMT'     : self.autoValidateZeroPattern,
                     }

      self.Virtdata = ['STATUS:=:PASS',
                  'BYTES_PER_SCTR:=:512',
                  'CUST_MODEL_NUM:=:[SEAGATE ST2000NM0001    ]',
                  'CFG:=:NA',
                  'CUST_TESTNAME:=:NA',
                  'CUST_TESTNAME_2:=:NA',
                  'CUST_TESTSUP_2:=:NA',
                  'CUST_TESTNAME_3:=:NA',
                  'CUST_TESTSUP_3:=:NA',
                  'DLP_SETTING:=:UNLOCKED',
                  'FMT_PROT_TYPE:=:TYPE_0',
                  'SCSI_CODE:=:FWR1',
                  'SED_LC_STATE:=:NA',
                  'SERVER_ERROR=NO ERROR',
                  'SERVO_CODE:=:SRV3',
                  'SHIP_MODE_SENSE:=:SD',
                  'TIME_TO_READY:<:20000',
                  'USER_LBA_COUNT:=:1953525168',
                  'WWN:=:WW_SAS_ID',
                  'ZERO_PTRN_RQMT:=:20']


   def __parseAttrQualifiers(self,data):
      if 'FAILCODE' in data:
         return []
      return [req.split(':') for req in data] #name, relationship, value


   def getDriveConfigAttributes(self, force = False):
      if self.dut.driveConfigAttrs in [None,{}] or force == True:
         self.dut.driveConfigAttrs = {}
         if ConfigVars[CN].get('DCC_PRE_RELEASE', 0):
            data = RequestService("DCMServerRequest",("GetLatest_DriveConfigAttributes",(self.dut.partNum,)))[1]['DATA']
         else:
            data = RequestService("DCMServerRequest", ("GetDriveConfigAttributes",(self.dut.partNum,)))[1]['DATA']
         if DEBUG:
            objMsg.printMsg("'data' from RequestService('GetDriveConfigAttributes'): %s" % data) #Seeing what is returned by the DCM can be helpful for debug
         if testSwitch.virtualRun:
            data = self.Virtdata
         try:
            #Parse the response from the host
            results = self.__parseAttrQualifiers(data)
            #if we received valid data then we set variables.
            if len(results) > 0:
               results = self.validateResults(results)
               for name, relationship, value in results:
                  self.dut.driveConfigAttrs[name] = (relationship, value)
         except:
            import traceback
            objMsg.printMsg("Results from parseAttrs: %s" % (data,),objMsg.CMessLvl.VERBOSEDEBUG)
            objMsg.printMsg("Traceback... \n%s" % traceback.format_exc())
            objMsg.printMsg("Custom Drive Attributes not supported in Host/FIS.")

################################################################################
###METHOD TO TEMPORARILY DISABLE DCM ATTRIBUTES - RJT
##         self.dut.driveConfigAttrs = {}
################################################################################

      return self.dut.driveConfigAttrs


   def validateResults(self, results):  #Handle invalid entry appended by host e.g 'SERVER_ERROR=NO ERROR'
      for dcmEntry in results:
         if len(dcmEntry) != 3:
            dcmParams = dcmEntry[0].split("=")
            if len(dcmParams) == 2:     #name, value
               results[results.index(dcmEntry)]=[dcmParams[0], '=', dcmParams[1]]
            else:
               ScrCmds.raiseException(11044, "Invalid DCM data : %s " %dcmEntry)
      return results


   def ProcessCustomAttributeRequirements(self):
      # Looks for attribute handlers retreived from GetDriveConfigAttributes host service
      self.getDriveConfigAttributes()

      if testSwitch.FE_0152007_357260_P_DCM_ATTRIBUTE_VALIDATION:
         objMsg.printMsg('*' * 60)
         objMsg.printMsg('*' * 60)
         objMsg.printMsg('Validating Customer Required Attributes')
         for name in self.dut.driveConfigAttrs:
            if name in self.custAttrHandlers:
               self.custAttrHandlers[name](name)
      else:
         for name, val in self.dut.driveConfigAttrs.items():
            relationship, value = val
            if name in self.custAttrHandlers:
               self.custAttrHandlers[name]=(relationship,value)


   def autoValidateDCMAttrString(self, attrName):
      self.autoValidateDCMAttr(attrName, str(self.dut.driveConfigAttrs[attrName][1]).rstrip(),\
                                         str(self.dut.driveattr.get(attrName, DriveAttributes.get(attrName,None))).rstrip() )


   def autoValidateDCMAttrFloat(self, attrName):
      self.autoValidateDCMAttr(attrName, float(str(self.dut.driveConfigAttrs[attrName][1]).rstrip()),\
                                         float(str(self.dut.driveattr.get(attrName, DriveAttributes.get(attrName, None))).rstrip()) )


   def autoValidateDCMAttrLBAs(self, attrName):
      if ConfigVars[CN].get('numHeads',0) != 0:
         objMsg.printMsg('NON-STANDARD HEAD COUNT DETECTED : SKIPPING USER_LBA_COUNT DCM ATTRIBUTE CHECK!')
      else:
         self.autoValidateDCMAttr(attrName, float(str(self.dut.driveConfigAttrs[attrName][1]).rstrip()),\
                                            float(str(self.dut.driveattr.get(attrName, DriveAttributes.get(attrName, None))).rstrip()) )


   def autoValidateDCMAttr(self, attrName, dcmVal, attrVal):
      rel = self.dut.driveConfigAttrs[attrName][0].rstrip()
      if rel == '=':
         rel = '=='
      if not eval('attrVal' + rel + 'dcmVal'):
         msg = "Invalid DCM attribute found in validation!\nAttrName:%s\nAttrValue:%s\nAttrRequirement:%s" % (attrName, attrVal, dcmVal)
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(14761, msg)
         else:
            objMsg.printMsg("VE WARNING!!!-> %s" % msg)
      else:
         objMsg.printMsg("Validated attribute %s: %s %s %s" % (attrName, attrVal, rel, dcmVal) )


   def autoValidateZeroPattern(self, attrName):
      attrVal = str(self.dut.driveattr.get(attrName, DriveAttributes.get(attrName, None))).rstrip()
      dcmVal = str(self.dut.driveConfigAttrs[attrName][1]).rstrip()
      if attrVal not in ['None','','NONE'] and dcmVal not in ['None','','NONE'] and int(attrVal) >= int(dcmVal):
         self.dut.driveattr[attrName] = dcmVal
         objMsg.printMsg("Validated attribute %s: %s %s %s" % (attrName, attrVal, '>=', dcmVal) )
      else:
         msg = "Invalid DCM attribute found in validation!\nAttrName:%s\nAttrValue:%s\nAttrRequirement:%s" % (attrName, attrVal, dcmVal)
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(14761, msg)
         else:
            objMsg.printMsg("VE WARNING!!!-> %s" % msg)


   def autoValidateWWNAttr(self, attrName):
      wwAttrName = str(self.dut.driveConfigAttrs[attrName][1]).rstrip()
      if not self.autoValidatesAttrExists(wwAttrName):
         msg = "Invalid DCM attribute found in validation! WWN attribute :%s does not exist" % wwAttrName
         if not testSwitch.virtualRun:
            ScrCmds.raiseException(14761, msg)
         else:
            objMsg.printMsg("VE WARNING!!!-> %s" % msg)
      else:
         objMsg.printMsg("Validated WWN attribute %s exists" % wwAttrName )


   def autoValidatesAttrExists(self, attrName):
      return str(self.dut.driveattr.get(attrName, DriveAttributes.get(attrName,None))).rstrip() not in ['None','','NONE']




def buildTestCCADict():
   '''This function is used to build the CCA test dictionary list and verify
   the mandatory list required to run this CCA_CCV process
   1.  Pull DCM attributes
   2.  Manual Overwrite with base attributes from script file
   3.  Manual Overwrite with partnumber attributes from script file
   4.  Verify all Mandatory CCAs are available
   5.  Cleanup up out of date driveConfigAttrs for OptionalCCAVals
   6.  Protect against shipping a SED customer drive in "MFG" mode
   '''
   CustConfig = CCustomCfg()

   # MANDATORY SET OF CCA NAMES REQUIRED TO RUN CCA_CCV
   if objDut.drvIntf in ['SATA']:
#CHOOI-19May17 OffSpec
#       MandatoryCCAVals = set(['BYTES_PER_SCTR','CUST_MODEL_NUM','CUST_MODEL_NUM2',
#                            'TIME_TO_READY','USER_LBA_COUNT'])
      MandatoryCCAVals = set(['BYTES_PER_SCTR','USER_LBA_COUNT'])
   else:
      MandatoryCCAVals = set(['BYTES_PER_SCTR','CUST_MODEL_NUM','FMT_PROT_TYPE',
                           'SHIP_MODE_SENSE','TIME_TO_READY','USER_LBA_COUNT',
                           'WWN'])

   # OPTIONAL SET OF CCA NAMES THAT ARE AVAILABLE TO RUN CCA_CCV IF NEEDED
   OptionalCCAVals  = set(['CFG','CUST_TESTNAME','CUST_TESTNAME_2',
                        'CUST_TESTSUP_2','CUST_TESTNAME_3',
                        'CUST_TESTSUP_3','FDE_TYPE','SED_LC_STATE',
                        'DLP_SETTING','ZERO_PTRN_RQMT'])

   try:
      from CCA_Control import CCA_override_dict
   except ImportError:
      objMsg.printMsg("The override dictionary 'CCA_override_dict' is missing.")
      ScrCmds.raiseException(14886,"The override dictionary 'CCA_override_dict' is missing.")

   #Pull DCM attributes
   config_attr = CustConfig.getDriveConfigAttributes(True)
   orig_DCM_CCAs = config_attr.copy()  # contains the original pulled DCM CCAs
   objMsg.printMsg("-" * 60)
   objMsg.printMsg("CCAs from DCM:  %s"%config_attr)
   objMsg.printMsg("-" * 60)

   #Pull BaseOverWrite attriubtes from script file
   objDut.driveConfigAttrs.update(CCA_override_dict.get('BASEOVERWRITE',{}).get('CCA_MAN_OVRIDE',{}))
   objMsg.printMsg("CCAs Base overwrite:  %s"%CCA_override_dict.get('BASEOVERWRITE',{}).get('CCA_MAN_OVRIDE',{}))
   objMsg.printMsg("-" * 60)

   #Manual OverWrite with attriubtes from script file
   objDut.driveConfigAttrs.update(CCA_override_dict.get(objDut.partNum,{}).get('CCA_MAN_OVRIDE',{}))
   objMsg.printMsg("CCAs Part Number overwrite:  %s"%CCA_override_dict.get(objDut.partNum,{}).get('CCA_MAN_OVRIDE',{}))
   objMsg.printMsg("-" * 60)

   #Print Final Dictionalry List
   objMsg.printMsg("Final CCA Dictionary List for Part Number:  %s"%objDut.partNum)
   for name in config_attr:
      objMsg.printMsg("%s %s %s"%(name,config_attr[name][0],config_attr[name][1]))
   objMsg.printMsg("-" * 60)

   #Optional CCAs values is use
   objMsg.printMsg("Optional CCA values:  %s"%OptionalCCAVals.intersection(objDut.driveConfigAttrs))
   objMsg.printMsg("-" * 60)

   #Verify all Mandatory CCAs are available
   if DEBUG:
      objMsg.printMsg("Mandatory CCA Values:  %s"%MandatoryCCAVals)
   if not MandatoryCCAVals.issubset(objDut.driveConfigAttrs):
      objMsg.printMsg("Missing CCA values:  %s"%MandatoryCCAVals.difference(objDut.driveConfigAttrs))
      ScrCmds.raiseException(14886,"Required CCA_CCV attributes missing")

   #Display valid DCM CCAs that are being overwritten by the Override CCAs
   #also load DCMCCA_overrite variable with results to be used later
   objMsg.printMsg("-" * 60)
   temp_mes = "\nCCA override results--------------------"
   cnt = 0
   if orig_DCM_CCAs == {}:  # No data retrieved from DCM
      temp_mes = temp_mes + "\n---No DCM CCAs retrieved"
      for name in CCA_override_dict.get('BASEOVERWRITE',{}).get('CCA_MAN_OVRIDE',{}):
         if name in CCA_override_dict.get(objDut.partNum,{}).get('CCA_MAN_OVRIDE',{}):
            temp_mes = temp_mes + "\n---BASE CCA overriden by PN   CCA_Control.py:  " + name
            cnt = cnt+1
   else:
      for name in orig_DCM_CCAs:
         if name in CCA_override_dict.get('BASEOVERWRITE',{}).get('CCA_MAN_OVRIDE',{}):
            temp_mes = temp_mes + "\n---DCM CCA overriden by BASE CCA_Control.py:  " + name
            cnt = cnt+1
         if name in CCA_override_dict.get(objDut.partNum,{}).get('CCA_MAN_OVRIDE',{}):
            temp_mes = temp_mes + "\n---DCM CCA overriden by PN   CCA_Control.py:  " + name
            cnt = cnt+1
   if cnt == 0:
      temp_mes = temp_mes + "\nNo DCM CCAs were overwritten."

   objDut.DCMCCA_overwrite = temp_mes
   objMsg.printMsg("%s"%objDut.DCMCCA_overwrite)
   objMsg.printMsg("-" * 60)

   #Cleanup up out of date driveConfigAttrs for OptionalCCAVals
   #This section in needed to handle previous Seatrack attributes for a
   #reprocessed drive, as well as handling a CCA that updates midrun.
   #CUST_TESTNAME requires special handling since it is a string list of tests

   for name in OptionalCCAVals:
      if (name not in config_attr):
         if DriveAttributes.get(name, '?') != '?':
            objMsg.printMsg("Clearing:  %s"%name)
            DriveAttributes[name] = "?"
      elif (name in config_attr) and (name == 'CUST_TESTNAME') and (DriveAttributes.get(name, '') != ''):
         ccaset = set(config_attr[name][1][i:i+3] for i in xrange(0,len(config_attr[name][1]),3))
         drvset = set(DriveAttributes.get(name)[i:i+3] for i in xrange(0,len(DriveAttributes.get(name)),3))
         drvset.intersection_update(ccaset)
         screenlist = []
         for testName in drvset:
            screenlist.append(testName)
         screenlist.sort()  # alphabetical sort
         testvar = ""
         for testName in screenlist:
            testvar = testvar+testName
         if DriveAttributes.get(name) != testvar:
            objMsg.printMsg("Resetting CUST_TESTNAME to:  '%s'"%testvar)
            DriveAttributes[name] = testvar
   objMsg.printMsg("-" * 60)

   #Protect against shipping a SED customer drive in "MFG" mode
   CCALifeState = str(objDut.driveConfigAttrs.get('SED_LC_STATE',[0,'NA'])[1]).strip()
   if CCALifeState == 'MFG':
      ScrCmds.raiseException(14886,"Illegal shipping LifeState condition.  No customer drive should ever ship in 'MFG' LifeState.")




def updateCUST_TESTNAME(newCCA):
   '''This function will read up the CUST_TESTNAME DriveAttributes string and
   break it into a list.  Will then add the newCCA to the list, sort to
   alphabetical order, then put back to the DriveAttributes.  If newCCA is
   already in list, it is not added again.
   '''
   chars = 3
   cust_testnamestr = DriveAttributes.get('CUST_TESTNAME','')
   screenlist = [cust_testnamestr[i*chars:(i*chars )+chars] for i in xrange(len(cust_testnamestr)/chars)]
   if newCCA not in screenlist:  # ensure new CCA not already in list
      screenlist.append(newCCA)
   screenlist.sort()  # alphabetical sort
   testvar = ""
   for testName in screenlist:
      testvar = testvar+testName
   DriveAttributes['CUST_TESTNAME'] = testvar
   objDut.driveattr['CUST_TESTNAME'] = testvar  # special case, do both
