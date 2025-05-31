#----------------G-----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: The Rim object is an abstraction of the cell RIM and implements methods to implement
#              to power on/off rim, download CPC/NIOS/Serial code etc.
#              Note that only once instance of rim must exist in the entire test environment.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CPCRim.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/CPCRim.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import ScrCmds
import time
import sys
import re
import types
import MessageHandler as objMsg
import traceback
from baseRim import baseCRim, BASE_BAUD_LIST

GLOB_RIM_OBJ = None

class CPCRim(baseCRim):
   def __init__(self, objRimType):
      global GLOB_RIM_OBJ
      baseCRim.__init__(self, objRimType)
      self.E0_Pad_List = [0, 1, 2, 3]

      GLOB_RIM_OBJ = objRimType



   #------------------------------------------------------------------------------------------------------#
   def getValidRimBaudList(self, baudRate):
      """
      Returns valid baud rates for rim
      """
      if self.objRimType.CPCRiserNewSpt():
         cellBaudList = BASE_BAUD_LIST
      else:
         cellBaudList = (Baud38400, Baud115200,)# Baud460800, Baud625000, Baud921600, Baud1228000]

      cellBaudList, baudRate = self.base_getValidRimBaudList(baudRate, cellBaudList)

      return cellBaudList, baudRate

   def initRim(self):
      """ CPC RIM FPGA Interface Code Setup """
      ScrCmds.trcBanner("Initializing CPC RIM")
      ScrCmds.insertHeader("Initializing CPC RIM",length = 40)

      try:
         rimObj = InitRimCPCCode()
         TraceMessage("HostVersion: %s " % HostVersion)
         if int( HostVersion.split('.')[0] ) >= 14:  # RPM 14 and higher support CPC on the fly
            startTime = time.time()  # for firmware download
            InitRimCode = rimObj.initRim()
            if rimObj.obj.otf.CVCPCOtf: #configVar CPC on the fly
               self.Unlock = rimObj.obj.otf.releaseCPC
               self.Unlock()
            endTime = time.time()
            TraceMessage("CPC OTF DownloadRim  elapsed: %s" % (endTime-startTime))
         else:
            if self.objRimType.CPCRiserNewSpt():
               cpc_usb1 = None
               cpc_usb2 = None
            else:
               cpc_usb1 = (CN, ConfigVars[CN]['CPC USB1'])
               cpc_usb2 = (CN, ConfigVars[CN]['CPC USB2'])
            cpc_app  = (CN, ConfigVars[CN]['CPC APP'])
            TraceMessage("%s - %s - %s - %s" % (cpc_usb1[1], cpc_usb2[1], cpc_app[1], ConfigVars[CN]['CPC Ver']))
            startTime = time.time()  # for firmware download


            response = DownloadRim(cpc_usb1, cpc_usb2, cpc_app)
            objMsg.printDict(response[1])
            endTime = time.time()
            TraceMessage("DownloadRim  elapsed: %s  response: %s" % ((endTime-startTime),response))
         verr = ICmd.Version()
         if verr['LLRET'] != OK:
            raise
      except:
         if not testSwitch.virtualRun:
            objMsg.printMsg("Error traceback in cpc download: %s" % traceback.format_exc())
            ScrCmds.raiseException(13401, "Download CPC APP/USB1/USB2 failed")

      # check CPC code version against config
      if not testSwitch.virtualRun:
         try:
            
            if rimObj.obj.otf.stripVer(verr['CPCVER']) != rimObj.obj.otf.stripVer(rimObj.obj.otf.ExpectedCPCVersion):
               TraceMessage("CPC RIM Ver = %s Config Ver=%s" % (verr['CPCVER'], ConfigVars[CN]['CPC Ver']))
               ScrCmds.raiseException(13402, "CPC code version does not match with config spec")
         finally:
            if testSwitch.FE_0118039_231166_SEND_CPC_VER_AS_ATTR:
               DriveAttributes['CPC_VER'] = verr['CPCVER']

      # Clear out unused files other rim's might have allocated and forgotten to clean up
      try:
         ICmd.DeleteAllFiles()
      except:
         pass

   def eslipBaudCmd(self, baudString):

      for retryNum in xrange(2*len(self.E0_Pad_List)):
         try:
            res = self.base_eslipBaudCmd(baudString)
            break
         except Exception, eInst:
            eDat = str(eInst)
            if eDat.find('EReceive')> -1 or eDat.find('ESend')> -1:
               #Reset the eslip state-machine
               ICmd.ESync(10, 1)
               #Toggle our ack count
               self.eslipToggleRetry()
            else:
               raise
      else:
         raise Exception, eInst

      return res

   def eslipToggleRetry(self, setACKOff = False):
      try:
         if ICmd.EslipRetry()['EXTRAACK'] == '1' or setACKOff:
            padVal = self.E0_Pad_List.pop(0)
            ICmd.EslipRetry(2, padVal, 0)                       # If we have F3 loaded (interface) FW on the drive, turn off second ACK
            self.E0_Pad_List.append(padVal)
         else:
            ICmd.EslipRetry(2, 3, 1)                       # If not F3: 2 retries, 3x C0 padding with extra ACK
      except:

         ScrCmds.statMsg("ESLIP Retry Toggle failed - Possibly not supported by CPC: %s" % traceback.format_exc())


   def __del__(self):
      #Remove any file buffers we allocated
      try: 
         ICmd.DeleteAllFiles()
      except:
         pass




###########################################################################################################
###########################################################################################################
# CPC On The Fly code
class BaseCPCInit:
   """BaseCPCInit: basic CPC Download routines, and check routines"""
   DEBUG = 0
   def __init__( self ):
      """__init__: """

      self.error = 0
      self.BootVer, self.CPCVer,self.ExpectedCPCVersion = '','',''
      self._getCfgVars()
      self.CPCVersion()

   #------------------------------------------------------------------------------------------------------#
   def _getCfgVars( self ):
      """_getCfgVars: get all values associated with the CPC from the ConfigVars"""
      # Get CPC Ver and file
      self.CVCPCVer    = ConfigVars[CN].get('CPC Ver','' )
      self.CVCPCApp    = ConfigVars[CN].get('CPC APP','' )
      # Get Boot Code File and Version
      self.CVCPCBootVer = ConfigVars[CN].get('CPC BOOT VER','')
      self.CVCPCBoot  = ConfigVars[CN].get('CPC BOOT','' )
      self.CVCPCBoot3App = ConfigVars[CN].get('CPC APP B3', '')
      # Get USB FileName
      self.CVCPCUSB1 = ConfigVars[CN].get('CPC USB1', '' )
      self.CVCPCUSB2 = ConfigVars[CN].get('CPC USB2','' )
      self.CVCPCFlash = ConfigVars[CN].get('CPC FLASH','')
      # Get CPC UPgrade Versions
      self.CVCPCUPVer = ConfigVars[CN].get('CPC Upgrade Ver', '' )
      self.CVCPCUPApp = ConfigVars[CN].get('CPC Upgrade APP','' )
      self.ExpectedCPCVersion = self.CVCPCVer
      return 0
   #------------------------------------------------------------------------------------------------------#
   def _printDict( self, inputDict=None ):
      """_print: prints the Dictionary back from the CPC"""
      if inputDict == None:
         inputDict = {}
      tmp = []
      for key in inputDict.keys(): tmp.append( "%s : %s"%(key, inputDict[key]) )
      objMsg.printMsg( "%s"%( ' , '.join( tmp ) ) )
      return 0
   #------------------------------------------------------------------------------------------------------#
   def _exeCmd( self, cmd='', debug=0 ):
      """_exeCmd:"""
      execdict, self.error = {}, 0
      if debug or self.DEBUG: objMsg.printMsg( "cmd: %s"%cmd)
      try:
         execdict = eval( cmd )
      except:
         etype, evalue = sys.exc_info()[:2]
         execdict = { 'ETYPE': '%s'%etype ,'EVALUE':'%s'%evalue , 'LLRET': -1 }
      self.error = execdict.get( 'LLRET', -1 )
      self._printDict( execdict )
      return execdict
   #------------------------------------------------------------------------------------------------------#
   def LoadBootCode( self, bootVer='' ):
      """LoadBootCode: Loads  boot code usually the latest"""
      bootLoaded = 0
      if not bootVer: bootVer = self.CVCPCBootVer
      try:
         if self.BootVer in ['3',]:
            error  = self.DownloadCPC( cpcApp = self.CVCPCBoot3App, bootLoad=1 )
            if not error: error = self.DownloadCPC(bootLoad=1)
            if not error: bootLoaded = 1
         else: bootLoaded = 1
      except: pass
      return bootLoaded
   #------------------------------------------------------------------------------------------------------#
   def stripVer( self, ver='' ):
      """stripVersion: strips out alpha characters so that we could get a solid float number"""
      stripVer = ver
      if ver:
         try:
            stripVer = re.findall( '\d+\.\d+', ver )[0]
         except:
            ScrCmds.raiseException(11044,"Invalid CPC version: %s\nException:%s" % (ver,traceback.format_exc()))
      return stripVer
   #------------------------------------------------------------------------------------------------------#
   def _formMemo( self, cpcVer='' ):
      """_formMemo: Tell other tray to check if he wants to release new CPC or not"""
      memo= {}
      memo['CPCVER'] = cpcVer
      return memo
   #------------------------------------------------------------------------------------------------------#
   def DownloadCPC(self,cpcApp='', ignoreFW=0,cpcVer='', bootLoad=0, forceDL=0 ):
      """DownloadCPC: """
      error = 0
      response = ( 0,{} )
      if not cpcApp: cpcApp = self.CVCPCApp
      if not cpcVer: cpcVer = self.CVCPCVer

      if GLOB_RIM_OBJ.CPCRiserNewSpt():
         usb1 = None
         usb2 = None
      else:
         usb1 = (CN, self.CVCPCUSB1 )
         usb2 = (CN, self.CVCPCUSB2 )

      CPCApp = ( CN, cpcApp )
      CPCFlsBoot = ( self.CVCPCBootVer, ( CN,self.CVCPCFlash ),( CN, self.CVCPCBoot ) )
      try:
         objMsg.printMsg( "%s-%s-%s-%s" % (usb1, usb2, CPCApp, CPCFlsBoot) )

         if ignoreFW:
            response = DownloadRim( usb1,usb2,CPCApp,forceDownload=forceDL,ignoreFWSignature=1, memo=self._formMemo( cpcVer ) )
         elif not bootLoad:
            response = DownloadRim( usb1,usb2,CPCApp,forceDownload=forceDL,memo=self._formMemo(cpcVer))
         else:
            response = DownloadRim( usb1,usb2,CPCApp,None, CPCFlsBoot,forceDownload=forceDL, memo=self._formMemo(cpcVer) )
      except: # You get here when we timeout downloading the CPC code, or CM code doesnt  support reflash
         etype, evalue = sys.exc_info()[:2]
         objMsg.printMsg( "Exception in %s\n%s" % (etype, evalue) )
         response = DownloadRim( usb1,usb2,CPCApp,forceDownload=forceDL )
      objMsg.printMsg( "Download Rim Response: %s" % (response,) )
      stat,res = response
      error = stat
      if not stat and not testSwitch.virtualRun:
         self.BootVer,self.CPCVer = res.get( 'BOOTVER','0' )[0], res.get( 'CPCVER','0' )[0]
         cellcpc = self.stripVer( self.CPCVer )
         cfgcpc = self.stripVer( cpcVer )
         #if float( cellcpc ) != float( cfgcpc ):
         if cellcpc != cfgcpc:
            error = 1
            objMsg.printMsg( "Cell CPC Ver: %s is not equal  to Config CPC Ver: %s"%(self.CPCVer, cpcVer ) )
         else: objMsg.printMsg( "Cell CPC Ver: %s is equal  to Config CPC Ver: %s"%(self.CPCVer, cpcVer ) )
      return error
   #------------------------------------------------------------------------------------------------------#
   def CPCVersion( self ):
      """CPCVersion: """
      Verr = self._exeCmd( "ICmd.Version()" )
      if not self.error:
         self.BootVer = Verr.get( 'BOOTVER', '0' )
         self.CPCVer = Verr.get( 'CPCVER', '0.0' )
      else: self.DownloadCPC( ignoreFW=1 )
      if not self.error:
         objMsg.printMsg( "CPC Ver: %s, Boot Ver: %s" % (self.CPCVer, self.BootVer) )
      return self.BootVer, self.CPCVer
#------------------------------------------------------------------------------------------------------#
class CPCOnTheFly( BaseCPCInit ):
   """CPCOnTheFly: Does CPC on the Fly"""
   def __init__( self ):
      BaseCPCInit.__init__( self )
      #objMsg.printMsg( "CPC On The Fly Object............." )
      self.EvalVers = ConfigVars[CN].get( "Eval Versions",['5','8','9'] )
      self.CVCPCOtf = self._checkEnabledCPCOTF()
   #------------------------------------------------------------------------------------------------------#
   def releaseCPC( self ):
      """_releaseCPC: this should tell the CPC to either release CPC Lock or not"""
      self.error = 0
      relCPC = self._checkDLRequest()
      if relCPC:
         try:
            self.error = self.DownloadCPC( ignoreFW = 1 )
            self.error = 2 # if CPC OTF download is ok
         except:
            self.error = -1
      return self.error

   #------------------------------------------------------------------------------------------------------#
   def _checkEnabledCPCOTF( self, cfgVars = 'CPC On The Fly' ):
      """_checkEnabledCPCOTF"""
      switch = {0:'Disabled',1:'Enabled'}
      enabled = 0
      if ConfigVars[CN].get( cfgVars, 'OFF' ).upper() in ['ON',]:
         enabled = 1
      objMsg.printMsg( "Config Vars 'CPC On The Fly' switch is %s"%switch[enabled] )
      return enabled
   #------------------------------------------------------------------------------------------------------#
   def _checkIfEvalVer( self, cpcVer='', cellcpc='' ):
      """_checkIfEvalVer"""
      inEvalVer = 0
      evalVer = re.findall( "\d+", cpcVer )
      if len(evalVer ):
         if evalVer[0] in self.EvalVers:
            objMsg.printMsg( "Requested CPC Ver is  Eval Version" )

            if len( cellcpc ):
               cpcVer = self.stripVer( cpcVer )
               cellcpc = self.stripVer( cellcpc )
               if cpcVer.split( '.' )[1] >= cellcpc.split( '.' )[1]:
                  objMsg.printMsg( "Eval Version[ %s] is greater than equal to curent version[%s]"%( cpcVer, cellcpc ) )
                  inEvalVer = 1

      return inEvalVer
   #------------------------------------------------------------------------------------------------------#
   def _checkDLRequest( self ):
      """_checkDLRequest: """
      releaseCPC,cpcReset, cpcVer = 0,0, self.CPCVer
      self.FwFile,self.Memo = CheckDownloadRequest()
      objMsg.printMsg( "Check DL Request : Firmware File: %s, Memo: %s" % ( self.FwFile, self.Memo ) )
      if self.Memo and not testSwitch.virtualRun:
         if not self.error and self.CPCVer and self.Memo['CPCVER']:
            memoVer = self.stripVer( self.Memo['CPCVER'] )
            cpcVer = self.stripVer( self.CPCVer )
            if float( memoVer ) > float( cpcVer ):
               if not self._checkIfEvalVer( self.Memo['CPCVER'], self.CPCVer ):
                  objMsg.printMsg( "Requested CPC Ver is not Eval Version and higher than Actual CPC Ver" )
                  objMsg.printMsg( "CPCVer: %s, Req Ver: %s"%(self.CPCVer, self.Memo) )
                  self.ExpectedCPCVersion = memoVer
                  releaseCPC = 1
            elif self._checkForceDL() and (float( memoVer ) == float( cpcVer )):
               objMsg.printMsg( "Requested CPC Force Reset. " )
               self.ExpectedCPCVersion = cpcVer
               releaseCPC = 1
      return releaseCPC
   #------------------------------------------------------------------------------------------------------#
   def _checkForceDL(self):
      """_checkForceDL: """
      cpcReset = 0
      if testSwitch.FE_0152536_081849_P_AAU_FAULT_DETECTION_ENABLE:
         try:
            cpcRstFile = str(CellIndex)+'_AAU'
            error, cpcReset = RequestService('GetTuple',(cpcRstFile,))
            objMsg.printMsg("cpcReset: %d"%int(cpcReset))
         except:
            objMsg.printMsg("cpcReset: 0")
      return cpcReset
#------------------------------------------------------------------------------------------------------#
class CPCValidation:
   """CPCValidation: Contains all methods to validate the  CPC"""
   def __init__( self, cpcObj = None, ):
      #objMsg.printMsg( "CPC Validation Object........." )
      cpcObj = CPCOnTheFly()
      self.otf = cpcObj
   #------------------------------------------------------------------------------------------------------#
   def selectEquipment( self ):
      """_selectEquipment: Selects the Equipment base on a ConfigVar switch to do CPC on the Fly or not"""
      selected = 0
      hostId, cmip = HOST_ID,CMIP
      cfgVars = { 'HOST ID':hostId,'CM IP':cmip }
      objMsg.printMsg( 'Machine Info: HOSTID : %s, CMIP: %s '%(hostId,cmip ) )
      for item in cfgVars.keys():
         selected = 0
         if not ConfigVars[CN].get( item, '' ): break
         if isinstance( ConfigVars[CN][item], types.StringType ) and ConfigVars[CN][item].upper() in ['ALL', cfgVars[item].upper() ]:
            objMsg.printMsg( "%s Selection is set to All"%item )
            selected = 1
         elif type( ConfigVars[CN][item] ) in [types.ListType, types.TupleType ]:
            if cfgVars[item] in ConfigVars[CN][item]:
               objMsg.printMsg( "Found Selected%s = %s in ConfigVars[CN][%s]"%(item,cfgVars[item],item) )
               selected = 1
         if not selected: break
      return selected
   #------------------------------------------------------------------------------------------------------#
   def checkCPCVersion( self, cmpVal = '==',getcpc=1 ) :
      """_checkCPCVersion: checks the cell CPC version against our Upgrade version to load or not"""
      loadCPC= 0
      cmpDict = { '>': 'larger', '=': 'equal', '<': 'less' }
      if getcpc: bootVer,cpcVer = self.otf.CPCVersion()
      if not cpcVer: self.otf.CVCPCVer
      #else: cpcVer = self.otf.CVCPCVer
      if self.otf.CVCPCUPVer and self.otf.CVCPCUPApp:
         cpcUpVer = self.otf.stripVer( self.otf.CVCPCUPVer )
         cellVer = self.otf.stripVer( cpcVer )
         tmp = 'if %.03f %s %.03f: loadCPC = 1'%( float( cpcUpVer ) , cmpVal, float( cellVer ) )
         try: exec( tmp  )
         except:
            etype, evalue = sys.exc_info()[:2]
            objMsg.printMsg( "Error getting CPC Versions:\n\t%s\n\t%s"%(etype, evalue) )
         cmpMsg=''
         for c in cmpVal: cmpMsg += ', ' + cmpDict[c]
         objMsg.printMsg( "[If CPC Upgrade Ver] is %s than [Current Cell CPC Ver]"%cmpMsg )
         objMsg.printMsg( "%s"%tmp )
      objMsg.printMsg( 'checkCPCVersion: flag = %d'%loadCPC )
      return loadCPC
#------------------------------------------------------------------------------------------------------#
class InitRimCPCCode:
   """InitRimCPCCode: """
   def __init__( self ):
      self.obj = CPCValidation()
      objMsg.printMsg( "Init Rim CPC Code Object.........." )
   #------------------------------------------------------------------------------------------------------#
   def initRim( self,retry=3 ):
      """_initRim: Downloads the Appropriate CPC"""
      error,retryCnt,dlUpgrade, dlForce = 0,0,0,0
      appCPC, verCPC = '',''
      if self.obj.otf.BootVer != self.obj.otf.CVCPCBootVer:
         bootLoaded = self.obj.otf.LoadBootCode()
         if not bootLoaded: return -1
      if self.obj.otf._checkForceDL():
         dlForce = 1
      elif self.obj.otf._checkEnabledCPCOTF() and self.obj.otf.CPCVer == self.obj.otf.CVCPCVer:
         dlUpgrade = 1
      if self.obj.otf.CPCVer != self.obj.otf.CVCPCVer or dlUpgrade or dlForce:
         cpcOtfUpgrade = self._CPCUpgrade()
         if cpcOtfUpgrade:
            appCPC = self.obj.otf.CVCPCUPApp
            verCPC = self.obj.otf.CVCPCUPVer
            self.obj.otf.ExpectedCPCVersion = verCPC
         if self.obj.otf.CPCVer != self.obj.otf.CVCPCUPVer or dlForce:
            while retryCnt < retry:
               objMsg.printMsg( "Downloading CPC Try #%d"%( retryCnt+1 ) )
               error =   self.obj.otf.DownloadCPC( cpcApp=appCPC,cpcVer=verCPC,forceDL=dlForce)
               if not error: 
                  cpcReset = str(CellIndex)+'_AAU'
                  RequestService('PutTuple',(cpcReset,0,)) #Reset the flag after successful download
                  break
               retryCnt += 1
      return error
   #------------------------------------------------------------------------------------------------------#
   def _CPCUpgrade(self):
      """_CPCUpgrade: """
      upgrade = 0
      if self.obj.otf.CVCPCOtf and self.obj.selectEquipment():
         if self.obj.checkCPCVersion( cmpVal='>=' ):
            upgrade = 1
         elif self.obj.otf._checkIfEvalVer( self.obj.otf.CPCVer ):
            upgrade = 1
      return upgrade

