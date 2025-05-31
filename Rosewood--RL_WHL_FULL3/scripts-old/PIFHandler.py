#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: PIF.py handler
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PIFHandler.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/PIFHandler.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from Test_Switches import testSwitch
import ScrCmds

import PIF, re
from ParamDbLogXmlOptimizer import cmStringIO
from array import array
import struct, traceback
from Drive import objDut
import MessageHandler as objMsg
from TestParamExtractor import TP
if testSwitch.FE_0164089_395340_P_B2D2_SELECTION_FEATURE:
   from StateTable import Operations

class CPIFHandler(object):
   instance = None
   def __new__(self, *args, **kwargs):   
      self.customer = None
      if self.instance is None:
         self.instance = object.__new__(self, *args, **kwargs)
         self.pifInfo = {}

         from CustomCfg import CCustomCfg
         self.CustConfig = CCustomCfg()

         # Option to use DCM data (TTR, Screens, etc)
         # if kwargs.get('useDCM', False):
            # self.CustConfig.getDriveConfigAttributes()

      return self.instance

   def __init__(self, *args, **kwargs):
      self.dut = objDut
      self.contentSequence = ['SECURITY_TYPE','FDE_TYPE','POWER_ON_TYPE','ZERO_PTRN_BEFORE','ZERO_PTRN_RQMT','ZERO_PTRN_AFTER']
      
   # Return the dictionary of information for the input pnum .  Start with info for the base 3 chars and then add 6 char and full 9 char
   # Pnum info.  If nothing is found then an empty dictionary is returned
   def getPnumInfo(self, sPnum, dPNumInfo=PIF.dPNumInfo, GetAll=False, force=False, dcm=True):

      if (sPnum != self.pifInfo.get('partNum', None)) or (force==True) or not testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM:

         dInfo = {}
         self.pifInfo = {}
         self.pifInfo['partNum'] = sPnum

         ## 3 char information first
         #if PIF.dPNumInfo.has_key(sPnum[0:3]):
         #   dInfo.update( PIF.dPNumInfo[sPnum[0:3]])
         #
         ## then 6 char information added
         #if PIF.dPNumInfo.has_key(sPnum[0:6]):
         #   dInfo.update( PIF.dPNumInfo[sPnum[0:6]])

         matches = []
         AllLst = []
         #Look for a simple regex match last...
         for tempPnMatch in dPNumInfo:
            #Force a fully matched PN
            pnMatch = tempPnMatch#"%s" % tempPnMatch

            try:

               regVal = re.compile(pnMatch)
            except re.error:
               #Ignore invalid re's... incase
               objMsg.printMsg("Invalid re in PIF PN: '%s'" % pnMatch)
               if testSwitch.FAIL_INVALID_PIF_REGEX:
                  ScrCmds.raiseException(11044,"Script Error in resolving regex for %s" % pnMatch)
               continue
            mMatch = regVal.search(sPnum)
            if mMatch:            #print "Match"
               matches.append((mMatch,dPNumInfo[tempPnMatch]))
               AllLst.append(dPNumInfo[tempPnMatch])
               #dInfo.update(dPNumInfo[tempPnMatch])


         oSpan = [(eval("mat.span()[1]"),pn) for mat,pn in matches]
         oSpan.sort()#reverse = True)

         #Create a dict lookup
         lCaids = {}
         for caid in dInfo.get('lCAIDS',[]):
            lCaids[caid['ID']] = caid

         for span, pn in oSpan:
            for pnId in pn.get('lCAIDS',[]):
               #Override the existing ID
               lCaids[pnId['ID']] = pnId

            #Add the new screens and content
            dInfo.setdefault('Screens',[]).extend([scr for scr in pn.get('Screens',[]) if not scr in dInfo['Screens']])
            dInfo.setdefault('Content',[]).extend([cnt for cnt in pn.get('Content',[]) if not cnt in dInfo['Content']])

         #untransform the lCaids into it's values
         if len(lCaids.values()) > 0:
            dInfo['lCAIDS'] = lCaids.values()


         ## finally any full 9 char pnum info adds to or overrides the other info.
         #if PIF.dPNumInfo.has_key(sPnum):
         #   dInfo.update(PIF.dPNumInfo[sPnum])


         if testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM  & dcm:
            try:
               # Get DCM data on change in part number
               if (self.dut.driveConfigAttrs in [None,{}]) or (not dInfo.get('partNum', None) is None):
                  self.CustConfig.getDriveConfigAttributes(force = True)
               
               screens = self.getDCMScreens()
               # remove official screens intended for Content run
               moveScreens = [screens.pop(screens.index(screen)) for screen in screens if screen in self.CustConfig.dcmContents['ZERO_PTRN_AFTER']]
               # merge DCM and PIF Screens 
               dInfo.setdefault('Screens',[]).extend([screen for screen in screens if screen not in dInfo['Screens']])
               
               content =  self.getDCMContent()  
               content.extend(moveScreens)  # append screens found in 'ZERO_PTRN_AFTER' to content (i.e. 'SMART_DST_LONG')
                              
               dInfo.setdefault('Content',[]).extend([cnt for cnt in content if cnt not in dInfo['Content']])
               dInfo['Content'] = self.sortContents(dInfo['Content'])    # sort merged PIF and DCM 'Content' test sequence
               
            except:
               ScrCmds.raiseException(11044,"Failed to process DCM/PIF screens and contents. %s" % traceback.format_exc())
               
         self.pifInfo['Info'] = dInfo      
         dInfo["AllLst"] = AllLst      
         self.pifInfo['InfoAllLst'] = dInfo      
         
      if GetAll:
         return self.pifInfo.get('InfoAllLst',{})   
      return self.pifInfo.get('Info',{})         


   @staticmethod
   def createTestList(stringified, chars=3):
      return [stringified[i*chars:(i*chars )+chars] for i in xrange(len(stringified)/chars)]

   def getDCMScreens(self, chars=3):
      """ Returns DCM screen names. """
      if self.dut.driveConfigAttrs in [None,{}]:
         return []
      cust_testname = self.dut.driveConfigAttrs.get('CUST_TESTNAME',('=',''))[1]
      if testSwitch.FE_0193449_231166_P_DL1_SUPPORT:
         cust_testname2 = self.dut.driveConfigAttrs.get('CUST_TESTNAME_2',('=',''))[1]
         cust_testname3 = self.dut.driveConfigAttrs.get('CUST_TESTNAME_3',('=',''))[1]
      if DEBUG:
         objMsg.printMsg("cust_testname %s" % (cust_testname,))
         if testSwitch.FE_0193449_231166_P_DL1_SUPPORT:
            objMsg.printMsg("cust_testname2 %s" % (cust_testname2,))
            objMsg.printMsg("cust_testname3 %s" % (cust_testname3,))
      if testSwitch.FE_0193449_231166_P_DL1_SUPPORT:
         screens = self.createTestList(cust_testname, chars)
         screens.extend(self.createTestList(cust_testname2, chars))
         screens.extend(self.createTestList(cust_testname3, chars))
      else:
         screens = [cust_testname[i*chars:(i*chars )+chars] for i in xrange(len(cust_testname)/chars)]

      if DEBUG: objMsg.printMsg("screens %s" % (screens,))
      return [self.CustConfig.dcmScreens[screen] for screen in screens if screen in self.CustConfig.dcmScreens]

   def getDCMContents(self, chars=3):
      '''Returns DCM screen names.'''
      if self.dut.driveConfigAttrs in [None,{}]:
         return []
      cust_testname = self.dut.driveConfigAttrs.get('CUST_TESTNAME',('=',''))[1]
      if testSwitch.FE_0193449_231166_P_DL1_SUPPORT:
         cust_testname2 = self.dut.driveConfigAttrs.get('CUST_TESTNAME_2',('=',''))[1]
         cust_testname3 = self.dut.driveConfigAttrs.get('CUST_TESTNAME_3',('=',''))[1]

      if DEBUG:
         objMsg.printMsg("cust_testname %s" % (cust_testname,))
         if testSwitch.FE_0193449_231166_P_DL1_SUPPORT:
            objMsg.printMsg("cust_testname2 %s" % (cust_testname2,))
            objMsg.printMsg("cust_testname3 %s" % (cust_testname3,))


      if testSwitch.FE_0193449_231166_P_DL1_SUPPORT:
         content = self.createTestList(cust_testname, chars)
         content.extend(self.createTestList(cust_testname2, chars))
         content.extend(self.createTestList(cust_testname3, chars))
      else:
         content = [cust_testname[i*chars:(i*chars )+chars] for i in xrange(len(cust_testname)/chars)]

      if DEBUG: objMsg.printMsg("content %s" % (content,))
      contents = [self.CustConfig.dcmContents[cont] for cont in content if cont in self.CustConfig.dcmContents]

      if DEBUG: objMsg.printMsg("contents %s" % (contents,))
      return contents

   def getDCMContent(self):
      """ Returns 'Contents' to test from DCM. """
      dcmContent  = self.contentSequence
      contents = []
      for content in dcmContent:
         if content in self.dut.driveConfigAttrs:
            if content == 'SECURITY_TYPE':
               if 'FDE_TYPE' in dcmContent:
                  dcmContent.remove('FDE_TYPE')    # for TCG drives, only run TCG test. FDE tests not required.                         
            dcmValue = self.dut.driveConfigAttrs[content][1]
            # get DCM 'Contents'
            if isinstance(self.CustConfig.dcmContents[content], dict):              # handle 'ZERO_PTRN_RQMT'.
               contents.extend(self.CustConfig.dcmContents[content][dcmValue])
            else:
               contents.append(dcmValue)
      return contents
   
   def sortContents(self, tests=[]):
      """ Sorts 'Contents' test sequence""" 
      dcmContent = self.contentSequence
      
      contents = []
      for content in dcmContent:
         for test in tests:
            if content is 'ZERO_PTRN_RQMT':
               contents.extend([test for v in self.CustConfig.dcmContents['ZERO_PTRN_RQMT'].values() if test in v])
            else:
               contents.extend([test for v in self.CustConfig.dcmContents[content] if test in v])

      if 'RLISTCHECK' in tests:  # Ensure 'RLISTCHECK' is the last test
         contents.append(contents.pop(contents.index('RLISTCHECK')))
      return contents             

   def Customer(self, pn):
      """
         Return's key to trigger TTR value for different customers.
         For FDE drives, return examples are: 'FDE', 'FDE_HP', 'FDE_LENOVO'.

         Note: This is a customer detection method based on DCM and PIF screens.
         Use CustomCfg.py CCustomer for firmware code based customer detection.
      """
      if self.customer is None:
         if self.dut.readyTimeLimit is None:
            return None

         customerType = 'STD_OEM'      # Default customer
         securityTypes = self.CustConfig.dcmContents.get('SECURITY_TYPE',[])
         fde = self.dut.driveConfigAttrs.get('SECURITY_TYPE',('=',[]))[1] in securityTypes
         if fde:
            customerType = 'FDE'
         self.customer = customerType
         if hasattr(TP,'CUSTOMER_TYPE'):
            drvPN = self.getPnumInfo(pn)
            for customerName, customerScreens in TP.CUSTOMER_TYPE.iteritems():
               self.customer = customerName
               if bool([customerName for screen in customerScreens if screen in drvPN.get('Screens',[])]):
                  if fde:
                     self.customer = customerType + "_" + customerName  # eg. FDE_HP
                  break
            else:
               self.customer = customerType
                  
         objMsg.printMsg("customer_type: '%s'" % self.customer)
         return self.customer
      else:
         return self.customer
      
   def IsTCG(self):
      """ Returns True if TCG tests found in DCM or PIF."""
      contents = self.getPnumInfo(objDut.partNum).get('Content',[])
      if contents:
         return bool([content for content in contents if content.startswith('TCG')])
      return False

   def IsSDnD(self):
      """ Returns True if SDnD tests found in DCM or PIF."""
      #from CustomCfg import CCustomCfg
      #CustConfig = CCustomCfg()
      #CustConfig.getDriveConfigAttributes()
      #self.CustConfig.getDriveConfigAttributes()
      if str(self.dut.driveConfigAttrs.get('SECURITY_TYPE',(0,None))[1]).rstrip() == 'SECURED BASE (SD AND D)':
         testSwitch.IS_SDnD = 1
         objMsg.printMsg("IsSDnD = 1")
         return True
      else:
         objMsg.printMsg("IsSDnD = 0")
         return False
   
   def IsFDE(self):
      """ Supports detection of FDE customers 'FDE', 'FDE_HP', 'FDE_LENOVO', etc. """
      self.Customer(objDut.partNum) 
      return self.customer.startswith('FDE')

class DTDFileCreator:

   def __init__(self,DTDSpec, caidCallback):
      fname = 'DtdFile.bin'
      self.dut = objDut

      self.caidCallback = caidCallback

      try:
         self.dtdFile = GenericResultsFile(fname)
      except:
         self.dtdFile = cmStringIO(fname)

      self.DTDSpec = DTDSpec

      self.__initializeFile()

   def __initializeFile(self):
      dumPat = self.DTDSpec['defaultByte']
      lastByte = self.DTDSpec['baseFmt'][-1][1]

      #Initialize the bytearray
      buff = array('B',(dumPat,)*lastByte)

      #Set the slices
      for slice in self.DTDSpec['baseFmt']:
         sliceLen = slice[1]-slice[0]
         buff[slice[0]:slice[1]] = array('B',(slice[2],)*sliceLen)

      self.dtdFile.open('wb')

      #buff.tofile(self.dtdFile)
      self.dtdFile.write(buff.tostring())
      self.dtdFile.seek(0)

   def __del__(self):
      self.dtdFile.close()

   def applyAttrSpec(self):

      try:
         for attr,spec in self.DTDSpec['AttrLocs'].items():
            spec = list(spec)
            if len(spec) == 1:
               spec.extend([spec[0]+1,0])
            elif len(spec) == 2:
               spec.append(0)

            if testSwitch.FE_0135987_357552_TRUNCATE_DTD_ATTR_TO_SPEC_LENGTH:
               specLen = spec[1] - spec[0]
               default = chr(self.DTDSpec['defaultByte'])*specLen
            else:
               attrLen = spec[1] - spec[0]
               default = chr(self.DTDSpec['defaultByte'])*attrLen

            default = array('c',default)

            #attrVal = self.dut.driveattr.get(attr,default)
            attrVal = self.caidCallback(attr,default)

            if testSwitch.FE_0135987_357552_TRUNCATE_DTD_ATTR_TO_SPEC_LENGTH:
               insertionPt = 0
               if spec[2] == 1 and len(attrVal) < specLen:
                  #RIGHT justified
                  insertionPt = specLen - len(attrVal)

               if len(attrVal) > specLen:
                  if spec[2] == 1:
                     #RIGHT justified, drop beginning chars
                     attrVal = attrVal[(len(attrVal)-specLen):]
                  else:
                     #LEFT justified, drop ending chars
                     attrVal = attrVal[:specLen]

            else:
               if spec[2] == 1:
                  if testSwitch.BF_0135968_357552_FIX_PIFHANDLER_ATTRLEN_NAME:
                     #RIGHT justify
                     insertionPt = attrLen - len(attrVal)
                  else:
                     insertionPt = arrLen- len(attrVal)
               else:
                  #LEFT justify
                  insertionPt = 0

            default[insertionPt:insertionPt+len(attrVal)] = array('c',attrVal)

            self.dtdFile.seek(spec[0])

            self.dtdFile.write(default.tostring())


      finally:
         self.dtdFile.close()
