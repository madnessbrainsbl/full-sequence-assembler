#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2010, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# $RCSfile: ReliFunction.py $
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReliFunction.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReliFunction.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
import time
import re
from Constants import *
import ScrCmds
from Rim import objRimType
#from MessageHandler import objMsg      # DT SIC
import MessageHandler as objMsg

from Drive import objDut
import IntfClass

from PowerControl import objPwrCtrl
#from PowerControl import objPwrCtrl

# DT SIC
from ICmdFactory import ICmd
from SerialCls import baseComm
import sptCmds

from TestParameters import *
from ReliTCG import *
from ReliSmart import *
from ReliFailCode import *
#import ReliIntfClass    # DT

OK      = 0
FAIL    = -1
UNDEF   = 'UNDEF'
WBF     = 1  # Write  Buffer select on FillBuff*** commands
RBF     = 2  # Read   Buffer select on FillBuff*** commands
BWR     = 3  # Both Write and Read Buffer select on FillBuff*** commands
SBF     = 4  # Serial Buffer select on FillBuff*** commands

# Global Attribute
ReliAttr = {}

###########################################################################################################

def timetostring(testtime):
    h = testtime / 3600
    m = ((testtime / 60) % 60)
    s = testtime % 60
    timestring = '%02d:%02d:%02d' % (h, m, s)
     
    return timestring
                   


###########################################################################################################
class CReliFunction:
   """
      Reliabiltiy Aux Functions
   """

   
   #------------------------------------------------------------------------------------------------------#
   def __init__(self, testStartTime):
       """
         Instantiation 
       """
       
       self.oFC = CReliFailCode()
       self.IDAttr = {}

       self.Status = OK
       # DT
       self.UnlockDiag = DriveAttributes.get('TCG_LOCK', 'OFF')
       self.UnlockFDE = DriveAttributes.get('FDE_LOCK', 'OFF')
       
       #RT120511: Show N2 if cell is N2
       #RT250511: Update CellType to be SIC or CPC only
       if objRimType.CPCRiser():
          self.CellType = 'CPC'
       else: 
       #   if cellTypeString == 'Neptune2':
       #      self.CellType = 'Neptune2'
       #   else:
       #      self.CellType = 'SIC'
          self.CellType = 'SIC'

       if objRimType.CPCRiserNewSpt():
          self.CellType = self.CellType + '18V'  

       #RT250511: Add PlatformType to determine Gemini, Neptune2 or others
       if cellTypeString == 'Neptune2':
          self.PlatformType = 'Neptune2'  
       else:
          self.PlatformType = 'Gemini'  
       
       self.IntfTimeout = prm_GIOSettings['IDT IntfTimeout']        #10000

       #RT200111: add CtoCtimeout for postscreen
       if self.CellType == 'SIC':
          # SIC Serial timeout in sec
          self.SerialTimeout = prm_GIOSettings['IDT SerialTimeout'] / 1000    #10000
          self.CtoCTimeout = 60  #60 secs
       else:
          # CPC SerialTimeout in msec
          self.SerialTimeout = prm_GIOSettings['IDT SerialTimeout']    
          self.CtoCTimeout = 60000  #60000ms
          
       self.SerialTimeoutExt = self.SerialTimeout * 3       # 30 sec for SIC
       self.TestName = 'Aux Func'
       self.DellPPID = ''
       self.RdWrPatt = 'On'
       self.DiagErrPatt = 'DiagError'
       self.ResetSmartPatt = 'Clear SMART is completed'
       self.TTRPatt = 'TTR'
       self.PackageVer = 'NIL'
       # DT021210 Bug Fix
       #self.ApplePartNum = ['70', '04']   
       self.ApplePartNum = ['700', '701', '702', '703', '704', '705', '706', '707', '708', '709', 
                            '040', '041', '042', '043', '044', '045', '046', '047', '048', '049']   
      
       self.AppleFWSignature = 'AP'

       #RT090911: part number list for DVR drives
       self.DVRPartNum = ['1AD']
       self.DVRTypeDetected = 0
       
       self.NumRetry = 2   
       self.IdDev = IntfClass.CIdentifyDevice().ID
       self.DrvAttr = {}      

       self.UDREnable = 'OFF'   # DT
       self.BlackArmourID = ['BSM3', 'BSM4']
       self.failCode = 0
       self.failLLRET = 'NIL'
       self.getIdenDevData()
       self.testStartTime = testStartTime     
       self.testEndTime = time.time() 
       self.v5 = 5000
       self.v12 = 12000
       self.GListLimit = 0
       self.PListLimit = 0
       self.RListLimit = 0
       self.IOEDCLimit = 0
       self.A198Limit = 0
       self.ODTVLogPage = 0x8F
       
       DriveAttributes['TEST CFG'] = ''        # initialize cfg

       if ConfigVars[CN].has_key('BLACKARMOR_ID') and ConfigVars[CN]['BLACKARMOR_ID'] == 'ON':
          self.BlackArmourID = ConfigVars[CN].get('BLACKARMOR_ID', self.BlackArmourID)

       if ConfigVars[CN].has_key('GLIST LIMIT') and ConfigVars[CN]['GLIST LIMIT'] != UNDEF:
          self.GListLimit = ConfigVars[CN].get('GLIST LIMIT', self.GListLimit)   

       if ConfigVars[CN].has_key('PLIST LIMIT') and ConfigVars[CN]['PLIST LIMIT'] != UNDEF:
          self.PListLimit = ConfigVars[CN].get('PLIST LIMIT', self.PListLimit)   

       if ConfigVars[CN].has_key('RLIST LIMIT') and ConfigVars[CN]['RLIST LIMIT'] != UNDEF:
          self.RListLimit = ConfigVars[CN].get('RLIST LIMIT', self.RListLimit)   

       if ConfigVars[CN].has_key('IOEDC LIMIT') and ConfigVars[CN]['IOEDC LIMIT'] != UNDEF:
          self.IOEDCLimit = ConfigVars[CN].get('IOEDC LIMIT', self.IOEDCLimit)   

       if ConfigVars[CN].has_key('A198 LIMIT') and ConfigVars[CN]['A198 LIMIT'] != UNDEF:
          self.A198Limit = ConfigVars[CN].get('A198 LIMIT', self.A198Limit)   

       self.setPowerOption()
       #self.checkTCG()
       
       objMsg.printMsg('>>>>> Drive SP TCG Lock=%s FDE Lock=%s' % (self.UnlockDiag, self.UnlockFDE))   
       objMsg.printMsg('>>>>> Cell Type=%s' % self.CellType)   
       objMsg.printMsg('>>>>> Cell Interface Timeout=%d msec' % self.IntfTimeout)   
       if self.CellType == 'SIC':
          objMsg.printMsg('>>>>> Cell Serial Timeout=%d sec' % self.SerialTimeout)   
       else:
          objMsg.printMsg('>>>>> Cell Serial Timeout=%d msec' % self.SerialTimeout)      
       
       if ConfigVars[CN].has_key('AUTO CONFIG') and ConfigVars[CN]['AUTO CONFIG'] != UNDEF and ConfigVars[CN]['AUTO CONFIG'] == 'ON':
          # DT281009 Auto test config based on PartNum
          #RT090911: part number detection changed to use generic function
          #RT090911: add detection for DVR type drives
          if self.checkPartNumber('DVR', self.DVRPartNum):
             self.setDVRConfig('ON')
          elif self.checkPartNumber('Apple', self.ApplePartNum):
             self.setAppleConfig()
          elif self.appleFirmwareDetect():  #RT090911: do firmware detect as a fallback when Apple part number not detected
             self.setAppleConfig()
          else:
             self.setStdConfig()    
             
             
   #------------------------------------------------------------------------------------------------------#
   def getIdenDevData(self):
       """
         Digest Identify Device data
       """
       
       self.TestName = 'Identify Device'
       self.printTestName(self.TestName)
       # Word59 Multiple Logical Sector Per Transfer Block 
       self.IDAttr['MultLogSect'] = 1
       if self.IdDev['IDMultipleSctrs'] & 0x100:  # check bit8 word59
          self.IDAttr['MultLogSect'] = self.IdDev['IDMultipleSctrs'] & 0xFF
          objMsg.printMsg('IdenDev > word59=0x%X MultipleLogSectPerBlock=%d' % (self.IdDev['IDMultipleSctrs'], self.IDAttr['MultLogSect']))
       else:
          objMsg.printMsg('IdenDev > Set MultipleLogSectPerBlock as default=%d' % self.IDAttr['MultLogSect'])


       self.IDAttr['Model'] = self.IdDev['IDModel']
       self.IDAttr['SerialNumber']= self.IdDev['IDSerialNumber'].lstrip()
       self.IDAttr['NumLBA'] = self.IdDev['IDDefaultLBAs']
       self.IDAttr['FirmwareRev'] = self.IdDev['IDFirmwareRev']
 
       # Word75 Q-Depth
       self.IDAttr['CmdQDepth'] = (self.IdDev['IDQDepth'] & 0x1F) + 1
       objMsg.printMsg('IdenDev > word75=0x%X CmdQDepth=%d' % (self.IdDev['IDQDepth'], self.IDAttr['CmdQDepth']))

       # SATA          
       if self.IdDev['IDSATACapabilities'] & 0x02:     # check bit 2
          self.IDAttr['SATAMode'] =  'SATA1'
          objMsg.printMsg("IdenDev > word76=0x%X Drive is SATA1" % self.IdDev['IDSATACapabilities'])
       elif self.IdDev['IDSATACapabilities'] & 0x04:   # check bit 3
          self.IDAttr['SATAMode'] =  'SATA2'
          objMsg.printMsg("IdenDev > word76=0x%X Drive is SATA2" % self.IdDev['IDSATACapabilities'])
      
       # Word83
       objMsg.printMsg('IdenDev > word83=0x%X' % self.IdDev['IDCommandSet2'])

       # Check Power Up in Standby (PUIS) support 
       if self.IdDev['IDCommandSet2'] & 0x20:       # check bit 5 word83
          objMsg.printMsg('IdenDev > PUIS supported')
          self.IDAttr['SupportPUIS'] = 'ON'
       else:
          objMsg.printMsg('IdenDev > PUIS not supported')
          self.IDAttr['SupportPUIS'] = 'OFF'

       # Check SetFeature in Power Up support
       if self.IdDev['IDCommandSet2'] & 0x40:       # check bit 6 word83
          objMsg.printMsg('IdenDev > SF in Power Up supported')
          self.IDAttr['SupportSFPowerUp'] = 'ON'
       else:
         objMsg.printMsg('IdenDev > SF in Power Up not supported')
         self.IDAttr['SupportSFPowerUp'] = 'OFF'
      
       # Word86
       objMsg.printMsg('IdenDev > word86=%X' % self.IdDev['IDCommandSet5'])

       # Enable Power Up in Standby (PUIS)
       if self.IdDev['IDCommandSet5'] & 0x20:       # check bit 5 word86
          objMsg.printMsg('IdenDev > PUIS enabled')
          self.IDAttr['EnablePUIS'] = 'ON'
       else:
          objMsg.printMsg('IdenDev > PUIS not enabled')
          self.IDAttr['EnablePUIS'] = 'OFF'

       # Enable SetFeature in Power Up
       if self.IdDev['IDCommandSet5'] & 0x40:       # check bit 6 word83
          objMsg.printMsg('IdenDev > SF in Power Up enabled')
          self.IDAttr['EnableSFPowerUp'] = 'ON'
       else:
          objMsg.printMsg('IdenDev > SF in Power Up not enabled')
          self.IDAttr['EnableSFPowerUp'] = 'OFF'
          
       
       # IDWWW IDModel
       objMsg.printMsg('IdenDev > IDWWN=%s' % self.IdDev['IDWorldWideName'])
       objMsg.printMsg('IdenDev > IDWWK=%s' % self.IdDev['IDModel'])

       #PUIS and SF spinup  
       if self.IDAttr['SupportPUIS'] == 'ON' and self.IDAttr['SupportSFPowerUp'] == 'ON' and \
          self.IDAttr['EnablePUIS'] == 'ON' and self.IDAttr['EnableSFPowerUp'] == 'ON':
          objMsg.printMsg('IdenDev > Set SF in Power Up options')
          self.IDAttr['SFPowerOpt'] = 'ON'
       else:
          objMsg.printMsg('IdenDev > Normal Power Up options [HR, FC] used')
          self.IDAttr['SFPowerOpt'] = 'OFF'


       # Word106 Logical sector per physical sector
       self.IDAttr['NumLogSect'] = 2 ** (int(self.IdDev['IDLogSectPerPhySect']) & 0x0F) 
       objMsg.printMsg('IdenDev > word106=%X LogSect/PhySect=%d' % (self.IdDev['IDLogSectPerPhySect'], self.IDAttr['NumLogSect']))
       objMsg.printMsg('IdenDev > Bit15=0, Bit14=1, and Bit13=1 for multi-logical sector to be enabled') 

       # Set 28/48 LBA mode
       self.IDAttr['Support48Bit'] = 'OFF'
       self.IDAttr['MaxLBA'] = self.IdDev['IDDefaultLBAs'] - 1 # default for 28-bit LBA
       if self.IdDev['IDCommandSet5'] & 0x400:      # check bit 10
          objMsg.printMsg('IdenDev > 48 bit LBA supported')
          self.IDAttr['Support48Bit'] = 'ON'
          self.IDAttr['MaxLBA'] = self.IdDev['IDDefault48bitLBAs'] - 1
       #objMsg.printMsg('IdenDev > MaxLBA=%d' % self.IDAttr['MaxLBA'])

       # Set APM
       if self.IdDev['IDCommandSet2'] & 0x08:       # check bit 3
          objMsg.printMsg('IdenDev > APM supported')
          objMsg.printMsg('IdenDev > Current APM=%X' % self.IdDev['IDCurrAPMValue'])
          if self.IdDev['IDCommandSet5'] & 0x08:          
             self.IDAttr['APM_MODE'] = 'ON'            
             objMsg.printMsg('IdenDev > APM enabled')
          else:                                      
             self.IDAttr['APM_MODE'] = 'OFF'
             objMsg.printMsg('IdenDev > APM disabled')
       else:
          self.IDAttr['APM_MODE'] = 'OFF'
          objMsg.printMsg('IdenDev > APM not supported')

       # Word209 Alignment of logical block in physical block
       self.IDAttr['OffSetLBA0'] = self.IdDev['IDLogInPhyIndex'] & 0x3FFF 
       objMsg.printMsg('IdenDev > word209=%X offset for LBA0=%d' % (self.IdDev['IDLogInPhyIndex'], self.IDAttr['OffSetLBA0']))

       # SeaCos
       objMsg.printMsg('IdenDev > SeaCosCmdSupport=%s' % self.IdDev['IDSeaCOSCmdsSupport'])
       if self.IdDev['IDSeaCOSCmdsSupport'] & 0x10:    # check bit 4
          self.IDAttr['SeaCos_Support'] = 'ON' 
          objMsg.printMsg('IdenDev > SeaCos supported')
       else:
          self.IDAttr['SeaCos_Support'] = 'OFF'
          objMsg.printMsg('IdenDev > SeaCos not supported')


       if self.IdDev['IDSeaCOSCmdsSupport'] & 0x1000:    # check bit 12          
          self.IDAttr['SeaCos_Enable'] = 'ON'
          objMsg.printMsg('IdenDev > SeaCos enabled')
       else:                                      
          self.IDAttr['SeaCos_Enable'] = 'OFF'
          objMsg.printMsg('IdenDev > SeaCos disabled')

       # DT190410 Media Cache support
       objMsg.printMsg('IdenDev > word159 MediaCacheEnable=%X' % self.IdDev['IDMediaCacheEnabled'])
       if self.IdDev['IDMediaCacheEnabled'] & 0x40:    # check bit 6          
          self.IDAttr['MediaCache_Enable'] = 'ON'
          objMsg.printMsg('IdenDev > Media Cache enabled')
       else:                                      
          self.IDAttr['MediaCache_Enable'] = 'OFF'
          objMsg.printMsg('IdenDev > Media Cache disabled')

       
       objMsg.printMsg('IdenDev > IDModel=%s' % self.IDAttr['Model'])
       objMsg.printMsg('IdenDev > SerialNumber=%s' % self.IDAttr['SerialNumber'])
       objMsg.printMsg('IdenDev > DefaultLBA=%d' % self.IDAttr['NumLBA'])
       objMsg.printMsg('IdenDev > MaxLBA=%d' % self.IDAttr['MaxLBA'])
       objMsg.printMsg('IdenDev > FirmwareRev=%s' % self.IDAttr['FirmwareRev'])

       # NVC 
       self.IDAttr['SupportNVC'] = 'OFF'
       self.IDAttr['NVCEnabled'] = 0x0
       if self.IdDev.get('IDNVCEnabled','') and self.IdDev.get('IDNVCMaxLBA',''):    # 2bytes(Enabled?) + 8Bytes(LBA)
          self.IDAttr['NVCEnabled'] = (((self.IdDev['IDNVCEnabled']& 0x00F0)>>4)& 0x1)
       objMsg.printMsg('IdenDev > NVC Support: %d (1-Yes/0-No)' % self.IDAttr['NVCEnabled'])

       return 0

   #------------------------------------------------------------------------------------------------------#
   def preGIOScreen(self):
       """
         Utility pre GIO screen
       """
       # RT050411 Initialize before preGIOScreen starts
       self.Status = OK
       
       self.TestName = 'Pre GIO Screen'
       self.printTestName(self.TestName)
       # Display Dell PPID
       self.getDellPPID()

       # DT140910 Check and clear ODTV Log
       if self.Status == OK:
          if ConfigVars[CN].has_key('ODTV LOG') and ConfigVars[CN]['ODTV LOG'] != 'UNDEF' and ConfigVars[CN]['ODTV LOG'] == 'ON':
             objMsg.printMsg('ODTV LOG=ON, Checking and clearing ODTV Log on Smart Log%X' % self.ODTVLogPage)
             self.clearODTVFailData()
             

       # Verify Smart
       if self.Status == OK:
          self.verifySmart()

       # Check Smart Logs
       if self.Status == OK:
          if ConfigVars[CN].has_key('SMART LOG SCN') and ConfigVars[CN]['SMART LOG SCN'] != 'UNDEF' and ConfigVars[CN]['SMART LOG SCN'] == 'ON':
             objMsg.printMsg('CMS Config set SMART LOG SCN=ON')
             self.checkSmartLogs([0xA1, 0xA8, 0xA9])
       
       # Check Smart Attr
       if self.Status == OK:
          if ConfigVars[CN].has_key('SMART ATTR SCN') and ConfigVars[CN]['SMART ATTR SCN'] != 'UNDEF' and ConfigVars[CN]['SMART ATTR SCN'] == 'ON':
             objMsg.printMsg('CMS Config set SMART ATTR SCN=ON')
             self.checkSmartAttr()

#       if self.Status == OK:
#          if ConfigVars[CN].has_key('APPLE CFG SCN') and ConfigVars[CN]['APPLE CFSCN'] == 'ON':
#             objMsg.printMsg('CMS Config set APPLE CFG=ON')
#             self.smartAppleCfgScreen()
       
       # Check Congen
       if self.Status == OK:
          if ConfigVars[CN].has_key('CONGEN CHECK') and ConfigVars[CN]['CONGEN CHECK'] != 'UNDEF' and ConfigVars[CN]['CONGEN CHECK'] == 'ON':
             objMsg.printMsg('CMS Config set CONGEN CHECK=ON')
             self.checkDriveCongen()
          else:   
             objMsg.printMsg('CMS Config set CONGEN CHECK=OFF')
             
       # Check RList Logs
       if self.Status == OK:
          if ConfigVars[CN].has_key('RLIST CHECK') and ConfigVars[CN]['RLIST CHECK'] != 'UNDEF' and ConfigVars[CN]['RLIST CHECK'] == 'ON':
             objMsg.printMsg('CMS Config set RLIST CHECK=ON')
             if ConfigVars[CN].has_key('RLIST LIMIT'):
                self.checkRListLog(ConfigVars[CN]['RLIST LIMIT'])
          else:
             objMsg.printMsg('CMS Config set RLIST CHECK=OFF')      
       
       # Check UDR
       if self.Status == OK: 
          self.checkUDR()
          #if self.DrvAttr['UDR_Enable'] == 'ON':
          if self.UDREnable == 'ON':
             self.disableUDR()
             if self.Status == OK:
                objMsg.printMsg('UDR disabled!')    
             else:
                objMsg.printMsg('UDR disabling failed!')       
       
                    
       # DT140910 Get Serial TTR
       if self.Status == OK:
          if ConfigVars[CN].has_key('SERIAL TTR') and ConfigVars[CN]['SERIAL TTR'] != UNDEF and ConfigVars[CN]['SERIAL TTR'] == 'ON':
             objMsg.printMsg('CMS Config set Serial TTR=ON')
             self.getTTRSpinup()
        
       
       
       return self.Status

   #------------------------------------------------------------------------------------------------------#
   def postGIOScreen(self):
       """
         Utility post GIO screen
         
       """
       self.TestName = 'Post GIO Screen'
       self.printTestName(self.TestName)
       
       if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
          self.powerCycle(useHardReset=1)
       else:
          self.powerCycle()  
       
       # Verify Smart
       if self.Status == OK:
          self.verifySmart()

       # Check Smart Logs
       if self.Status == OK:
          if ConfigVars[CN].has_key('SMART LOG SCN') and ConfigVars[CN]['SMART LOG SCN'] != 'UNDEF' and ConfigVars[CN]['SMART LOG SCN'] == 'ON':
             objMsg.printMsg('CMS Config set SMART LOG SCN=ON')
             self.checkSmartLogs([0xA1, 0xA8, 0xA9])

       # Check Smart Attr
       if self.Status == OK:
          if ConfigVars[CN].has_key('SMART ATTR SCN') and ConfigVars[CN]['SMART ATTR SCN'] != 'UNDEF' and ConfigVars[CN]['SMART ATTR SCN'] == 'ON':
             objMsg.printMsg('CMS Config set SMART ATTR SCN=ON')
             self.checkSmartAttr()

       # Check Congen for corruption
       if self.Status == OK:
          if ConfigVars[CN].has_key('CONGEN CHECK') and ConfigVars[CN]['CONGEN CHECK'] != 'UNDEF' and ConfigVars[CN]['CONGEN CHECK'] == 'ON':
             objMsg.printMsg('CMS Config set CONGEN CHECK=ON')
             self.checkDriveCongen()
          else:   
             objMsg.printMsg('CMS Config set CONGEN CHECK=OFF')
     
       # Check RList Log
       if self.Status == OK:
          if ConfigVars[CN].has_key('RLIST CHECK') and ConfigVars[CN]['RLIST CHECK'] != 'UNDEF' and ConfigVars[CN]['RLIST CHECK'] == 'ON':
             objMsg.printMsg('CMS Config set RLIST CHECK=ON')
             if ConfigVars[CN].has_key('RLIST LIMIT'):
                self.checkRListLog(ConfigVars[CN]['RLIST LIMIT'])
          else:      
             objMsg.printMsg('CMS Config set RLIST CHECK=OFF')
       
       # Reset DOS Table
       if self.Status == OK:
          self.resetDOSTable()

       #RT120112: change due to CPC intrinsic removal
       if self.CellType.find('CPC') >= 0 and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #only send this cmd for Intrinsic CPC 
         # 120 sec timout and 60 sec for char-to-char
         ICmd.SetSerialTimeout(self.SerialTimeout * 12, self.CtoCTimeout)           
          

       # N1 Reset SMART
       if self.Status == OK:
          self.resetSmart()          

       # Enable UDR if supported
       if self.Status == OK:
          if self.UDREnable == 'ON':
             self.enableUDR()

       #RT120112: change due to CPC intrinsic removal
       if self.CellType.find('CPC') >= 0 and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #only send this cmd for intrinsic CPC
         # Restore normal timeout
         ICmd.SetSerialTimeout(self.SerialTimeout)
 
       # Check POH
       if self.Status == OK:
          self.checkSmartPOH()

       return self.Status


   #------------------------------------------------------------------------------------------------------#
   def setPowerOption(self):
       """
         Utility set power on option
       """
       
       if self.IDAttr['SFPowerOpt'] == 'ON':
          ConfigVars[CN]['Power On Set Feature'] = 'ON'
          objMsg.printMsg('Config is set for Power On Set Features to come ready')

   #------------------------------------------------------------------------------------------------------#
   def disableAPM(self, testName):
       """
         Disable Active Power Management
       """
       # Disable APM
       
       self.TestName = ('%s DisableAPM' %testName)
       self.printTestName(self.TestName)
       if self.IDAttr['APM_MODE'] == 'ON':
          #objMsg.printMsg('%s Disable APM' % testName)
          data = ICmd.SetFeatures(0x85)
          self.Status = data['LLRET']
          if self.Status == OK:
             objMsg.printMsg('%s SetFeature(0x85) Disable APM passed, data=%s' % (testName, str(data)))
          else:
             objMsg.printMsg('%s SetFeature(0x85) Disable APM failed, data=%s' % (testName, str(data)))
         
          if self.Status == OK:
             # RandomRead to wake up drive from LBA beyond 100 
            
             # DT041210 Common
             #RT120112: change due to CPC intrinsic removal
             if self.CellType == 'SIC' or (self.CellType.find('CPC') >= 0 and testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION): #for SIC and CPCv3.3
                RandomRead = {
                   'test_num'   : 510,
                   'prm_name'   : "RandomReadDMAExt",
                   'spc_id'     : 1,
                   'timeout' : 252000,
                   'STARTING_LBA' : (0, 0, 0, 100),
                   'MAXIMUM_LBA' : (0, 0, 0, 10000),
                   'TOTAL_BLKS_TO_XFR64': (0, 0, 0, 256),
                   'BLKS_PER_XFR' : 256,
                   'CTRL_WORD1':0x0011,
                   'CTRL_WORD2':0x0000
                }
                ret = ICmd.St(RandomRead)
                data = ICmd.translateStReturnToCPC(ret)    # DT translate initiator return
             else:
                data = ICmd.RandomReadDMAExt(100, 10000, 256, 256, 1)    
                
             self.Status = data['LLRET']
             if self.Status == OK:   
                objMsg.printMsg('%s RandomRead passed, data=%s' % (testName, str(data)))
             else:
                objMsg.printMsg('%s RandomRead failed, data=%s' % (testName, str(data)))
          else:
             objMsg.printMsg('%s Disable APM failed' % testName)
       return self.Status
   
   #------------------------------------------------------------------------------------------------------#
   def enableAPM(self, testName):
       """
         Enable Active Power Management
       """
       apmVal = self.IdDev['IDCurrAPMValue'] & 0xFF
       # Enable APM
       if self.IDAttr['APM_MODE'] == 'ON':
          objMsg.printMsg('%s Enable APM with value=%X' % (testName, apmVal))
          data = ICmd.SetFeatures(0x05, apmVal)
          self.Status = data['LLRET']

          if self.Status == OK:
             objMsg.printMsg('%s APM enabled!' % testName)
          else:
             objMsg.printMsg('%s enable APM failed! Result=%s, Data=%s' % (testName, self.Status, data))     

       return 0
   #------------------------------------------------------------------------------------------------------#
   def setRdWrStatsIDE(self, testName, rdWrSetting):
       """
         Serial Cmd to turn on Read/Write Statistics 
       """
       self.TestName = testName
       
       
       if self.CellType.find('CPC') >= 0:
          ICmd.SetSerialTimeout(self.SerialTimeout)
          ICmd.ClearSerialBuffer() 

       
       self.powerCycle('TCGUnlock')
       self.Status = self.disableAPM(self.TestName)
       
       
       if self.Status == OK:   
          sptCmds.enableDiags(self.NumRetry)
          
          accumulator = baseComm.PChar(CTRL_W)
          serialBuffer = sptCmds.promptRead(self.SerialTimeout, 0, altPattern = "stats", accumulator = accumulator)          
          objMsg.printMsg('CtrlW Data=%s' % str(serialBuffer))
          if serialBuff.find(rdWrSetting) >= 0:         
             objMsg.printMsg('%s SetRdWrtStats Stats passed.  RdWrStats=%s' % (testName, rdWrSetting))      
          else:
             objMsg.printMsg('%s SetRdWrtStats Stats failed.  RdWrStats=%s' % (testName, rdWrSetting))   
             self.Status = FAIL
             
       return 0


   #------------------------------------------------------------------------------------------------------#
   def resetDOSTable(self):
       """
         Utility reset DOS table

       """

       self.TestName = 'Reset DOS'
       self.printTestName(self.TestName)
       
       #RT120112: change due to CPC intrinsic removal
       if self.CellType.find('CPC') >= 0 and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #only for intrinsic CPC
          ICmd.SetSerialTimeout(self.SerialTimeout)
          ICmd.ClearSerialBuffer()  
          
       if self.Status == OK:
          for i in range(self.NumRetry):
             #RT130911: SI/N2 powercycle without prepower sequence 
             self.powerCycle('TCGUnlock', 0)
             self.Status = self.disableAPM(self.TestName)   
             
             sptCmds.enableDiags(self.NumRetry)
             sptCmds.gotoLevel('7')
             #data = sptCmds.sendDiagCmd('m1,0,1000000,1')             
             #objMsg.printMsg('m1,0,1000000,1 Display DOS Table Data=%s' % str(data))
             # Bug fix for Invalid Diag Cmd Parameter       
             data = sptCmds.sendDiagCmd('m,0,1000000,1')             
             objMsg.printMsg('m,0,1000000,1 Display DOS Table Data=%s' % str(data))
             
             data = sptCmds.sendDiagCmd('m100,0,1000000', self.SerialTimeout)   
             objMsg.printMsg('m100,0,1000000 Clear DOS Table Data=%s' % str(data))                 
                
             #data = sptCmds.sendDiagCmd('m1,0,1000000,1', self.SerialTimeout)   
             #objMsg.printMsg('m1,0,1000000,1 Display DOS Table Data=%s' % str(data))       
             # Bug fix for Invalid Diag Cmd Parameter
             data = sptCmds.sendDiagCmd('m,0,1000000,1', self.SerialTimeout)   
             objMsg.printMsg('m,0,1000000,1 Display DOS Table Data=%s' % str(data))
        
             if data.find(self.DiagErrPatt) >= 0 or data.find('Invalid') >= 0:
                objMsg.printMsg('DOS Table reset attempt(%d) failed!' %(i+1))
                self.Status = FAIL
             else:   
                objMsg.printMsg('DOS Table reset passed!')
                self.Status = OK
                break

       return 0
   #------------------------------------------------------------------------------------------------------#
   def resetSmart(self):
       """
         Utility reset SMART using N1
       """
       # DT220610       
       # new error string "Error xxxx DETSEC xxxxxxxx"
       retPat = re.compile('1>')
       errPat = re.compile('Error\s*(?P<rwErrCode>[a-f,0-9,A-F]{4})\s*DETSEC\s*(?P<rwExtCode>[a-f,0-9,A-F]{8})')
    
       self.TestName = 'Reset SMART'
       self.printTestName(self.TestName)
       #RT120112: change due to CPC intrinsic removal
       if self.CellType.find('CPC') >= 0 and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #only for intrinsic CPC
          ICmd.SetSerialTimeout(self.SerialTimeout)
          ICmd.ClearSerialBuffer()
       
       if self.Status == OK:
          #RT130911: SI/N2 powercycle without prepower sequence 
          self.powerCycle('TCGUnlock', 0)
          self.Status = self.disableAPM(self.TestName) 
          
       if self.Status == OK:   
          sptCmds.enableDiags(self.NumRetry)
          sptCmds.gotoLevel('1')
          # DT SIC - Set longer timeout
          #serialBuffer = sptCmds.sendDiagCmd('N1', self.SerialTimeout)   
          serialBuffer = sptCmds.sendDiagCmd('N1', self.SerialTimeout * 12)   
          objMsg.printMsg('N1 Data=%s' % str(serialBuffer))
          
          # DT210610 
          if len(retPat.findall(serialBuffer)) > 0 and len(errPat.findall(serialBuffer))== 0:
             objMsg.printMsg('N1 Reset Smart passed!')
          else:   
             objMsg.printMsg('N1 Reset Smart failed! Error detected!')
             self.Status = FAIL

          if self.Status != OK:
             failure = 'IDT SMART Reset'
             data = {}
             data['LBA'] = '0' 
             data['STS'] = '00' 
             data['ERR'] = '00'           
             self.failLLRET = 'SerialPortError'   
             
             self.failCode = self.oFC.getFailCode(failure)
             self.testEndTime = time.time()
             self.failStatus = ('STS%s-ERR%s' % (int(data['STS']), int(data['ERR']) ))
             self.DrvAttr['MQM_FAIL_TTF'] = timetostring(self.testEndTime-self.testStartTime)
             self.DrvAttr['MQM_FAIL_SEQ'] = failure
             self.DrvAttr['MQM_FAIL_LBA'] = data['LBA']
             self.DrvAttr['MQM_FAIL_CODE'] = self.failCode
             self.DrvAttr['MQM_FAIL_LLRET'] = self.failLLRET
             self.DrvAttr['MQM_FAIL_STATUS'] = self.failStatus
             DriveAttributes.update(self.DrvAttr)

       return 0

   #------------------------------------------------------------------------------------------------------#
   def verifySmart(self):
       """
         Utility verify SMART
       """

       self.TestName = 'Verify Smart'
       self.printTestName(self.TestName) 
       #RT120112: change due to CPC intrinsic removal
       if self.CellType.find('CPC') >= 0 and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #only for intrinsic CPC
          ICmd.ClearSerialBuffer()
          
       if self.Status == OK:
          for i in range(self.NumRetry):
             if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION and objRimType.IOInitRiser():
                pass
             else:    
                self.powerCycle()
             #self.Status = self.disableAPM(self.TestName) 
             data = ICmd.SmartEnableOper()
             self.Status = data['LLRET']
             objMsg.printMsg('SmartEnableOper Data=%s' % str(data))

             if self.Status == OK:
                break
             else:
                objMsg.printMsg('Retry SmartEnable')

          if self.Status == OK:   
             # DT SIC
             #data = ICmd.ReadSectors(100,0,1,0)
             data = ICmd.SmartReadLogSec(0xA1, 1)
             #self.Status = data['LLRET']
             #objMsg.printMsg('ReadSectors Data=%s' % str(data))

          if self.Status == OK:
             data = ICmd.SmartReturnStatus()
             self.Status = data['LLRET']
             objMsg.printMsg('SmartReturnStatus Data=%s' % str(data))

          #if self.Status == OK:
             #serialBuffer = ICmd.GetBuffer(SBF, 0, 100)['DATA']
             #objMsg.printMsg('SmartReturnBuffer=%s' % str(serialBuffer))
             #WriteToResultsFile(serialBuffer + '\n')
             
          if self.Status == OK:
             objMsg.printMsg('Smart Verify passed!')            
             if data.has_key('LBA') != 0: 
                #RT120112: change due to CPC intrinsic removal
                if self.CellType.find('CPC') >= 0 and testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #only for CPCv3.3
                   data['CYL'] = int(data['LBA'], 16) >> 8
                else:
                   data['CYL'] = int(data['LBA']) >> 8
                objMsg.printMsg('SmartReturnStatus LBA shifted 8=%d(0x%X)' % (data['CYL'], data['CYL']))               
                cyl = int(data['CYL'])
                cyl_low = cyl & 0xff
                cyl_high = cyl >> 8          
             if data.has_key('CYL') == 0:
                objMsg.printMsg('SMART Verify failed! SmartReturnStatus missing data(CYL). ' % self.Status)
                #driveattr['failcode'] = failcode['Fin DST Thres']
                failure = 'Fin DST Thres'
                self.Status = FAIL
             else:
                cyl = int(data['CYL'])
                cyl_low = cyl & 0xff
                cyl_high = cyl >> 8

          else:
             objMsg.printMsg('Smart Verify failed!')  
             #RT130511: have to initialize variable failure for failure handling below
             failure = 'IDT Verify Smart'

          if self.Status == OK:
             if (cyl_low == 0xf4) and (cyl_high == 0x2c):
                objMsg.printMsg("SMART Verify failed (threshold exceeded): Cyl=0x2CF4")
                objMsg.printMsg('Serious failure mode, no reruns allowed!')
                #driveattr['failcode'] = failcode['Fin DST Thres']
                failure = 'Fin DST Thres'
                self.Status = FAIL

          if self.Status == OK:
             if (cyl_low == 0x4f) and (cyl_high == 0xc2):
                objMsg.printMsg('SMART Verify passed (thresholds not exceeded):Cyl=0xC24F')
             else:
                objMsg.printMsg("SMART Verify failed (invalid Cyl): not 0x2CF4 or 0xC24F")
                #driveattr['failcode'] = failcode['Fin DST Thres']
                failure = 'Fin DST Thres'
                self.Status = FAIL   
          
          if self.Status != OK:
             #objMsg.printMsg('Verify Smart failed!')       
             data = {}
             data['LBA'] = '0' 
             data['STS'] = '00' 
             data['ERR'] = '00'           
             self.failLLRET = 'SerialPortError'   
             
             self.failCode = self.oFC.getFailCode(failure)
             self.testEndTime = time.time()
             self.failStatus = ('STS%s-ERR%s' % (int(data['STS']), int(data['ERR']) ))
             self.DrvAttr['MQM_FAIL_TTF'] = timetostring(self.testEndTime-self.testStartTime)
             self.DrvAttr['MQM_FAIL_SEQ'] = failure
             self.DrvAttr['MQM_FAIL_LBA'] = data['LBA']
             self.DrvAttr['MQM_FAIL_CODE'] = self.failCode
             self.DrvAttr['MQM_FAIL_LLRET'] = self.failLLRET
             self.DrvAttr['MQM_FAIL_STATUS'] = self.failStatus
             DriveAttributes.update(self.DrvAttr)

       return 0

   #------------------------------------------------------------------------------------------------------#
   def checkRListLog(self, RListLimit):
       """
         Utility check RList Log using V4
       """
       #self.TestName = 'Check RList'
       self.TestName = 'RLIST LOG'
       rlist = -1
       # DT060711 New Rlist signature for Apple code from V4
       #RlistPattern = 'RList: '
       RlistPattern = 'Entries: '
       OldV4Pattern = 'Total'
       temp = 'NotFound'
 
       if self.CellType.find('CPC') >= 0:
          ICmd.SetSerialTimeout(self.SerialTimeout)

       self.printTestName(self.TestName)              
       #RT130911: SI/N2 powercycle without prepower sequence 
       self.powerCycle('TCGUnlock', 0)
       self.Status = self.disableAPM(self.TestName)   
  
       #ICmd.ClearSerialBuffer()  
       #RT310511: revert back name as it was changed by disableAPM()
       self.TestName = 'RLIST LOG'
       
       if self.Status == OK:
          sptCmds.enableDiags(self.NumRetry)
          sptCmds.gotoLevel('T')
          serialBuff = sptCmds.sendDiagCmd('V4', self.SerialTimeoutExt)
          
          # DT TESTINGS
          #serialBuff = 'Reassigned Sectors List Original     New    log log   log     phy     phy     LBA      PBA    cyl  hd  sctr zn  cyl hd  sctr     SFI  993AC9B 254356C3  -----  - ----- 17 2141C 1    9D          ALT     reported  993AC9C 254356C4  -----  - ----- 17 2141C 1    9E          ALT     reported  993AC9D 254356C5  -----  - ----- 17 2141C 1    9F          ALT     reported  993AC9E 254356C6  -----  - ----- 17 2141C 1    A0          ALT     reported  993AC9F 254356C7  -----  - ----- 17 2141C 1    A1          ALT     reported  993ACA0 254356C8  -----  - ----- 17 2141C 1    A2          ALT     reported  993ACA1 254356C9  -----  - ----- 17 2141C 1    A3          ALT     reported  993ACA2 254356CA  -----  - ----- 17 2141C 1    A4          ALT     reported  993ACA3 254356CB  -----  - ----- 17 2141C 1    A5          ALT     reported  993ACA4 254356CC  -----  - ----- 17 2141C 1    A6          ALT     reported  993ACA5 254356CD  -----  - ----- 17 2141C 1    A7          ALT     reported  993ACA6 254356CE  -----  - ----- 17 2141C 1    A8          ALT     reported  993ACA7 254356CF  -----  - ----- 17 2141C 1    A9          ALT     reported  993ACA8 254356D0  -----  - ----- 17 2141C 1    AA          ALT     reported  993ACA9 254356D1  -----  - ----- 17 2141C 1    AB          ALT     reported          Alt   Pending  Total    Alted  Total        Entries Entries Entries    Alts   Alts Head 0              0 Head 1              0 Head 2              0 Total        F      0       F     FFFFFFF1      0  Total Alt Removals:    0 Checksum = F2DD'
          # DT060711 New V4 Return Rlist is from Alts: xxxx
          #serialBuff = 'Reassigned Sectors List Entries: 0003, Alts: 0007, Removed: 0000, Pending: 0000 Idx  LBA        PBA        LLLCHS of LBA PLPCHS of PBA SFI    Hours Msecs  Status   BBM Mask'

          objMsg.printMsg('LevelT V4 Data=%s' % serialBuff)

          # Search new V4 for "RList"
          try:
             m = re.search(RlistPattern, str(serialBuff))
             # DT060711 Revised New V4 Rlist format
             #temp = serialBuff[m.end():].split()[0]
             temp = serialBuff[m.end():].split(',')[0]               
             objMsg.printMsg('%s count=%s' %(self.TestName, str(temp)))     
                
          except:
             temp = 'NotFound'
             pass

          # "RList" not found, search "Total" 3 times
          if temp == 'NotFound':
             objMsg.printMsg('%s Rlist value=%s. Search Rlist from old V4 format.' % (self.TestName, temp))
                
             try:
                m = re.search(OldV4Pattern, serialBuff)
                serialBuff = serialBuff[m.end():]
                m = re.search(OldV4Pattern, serialBuff) 
                serialBuff = serialBuff[m.end():]
                m = re.search(OldV4Pattern, serialBuff) 
                temp = serialBuff[m.end():].split()[0] 
                #objMsg.printMsg('%s RList count=%s' %(self.TestName, str(temp)))      
             except:
                self.Status = FAIL
                pass
                
          if temp != 'NotFound' and self.Status == OK:      
             # Get RList value
             try:
                #temp = int(temp)
                # DT211210
                #rlist = temp
                rlist = int(temp, 16)

                objMsg.printMsg('%s Rlist count=%04d' %(self.TestName, rlist))
                   
                if rlist > RListLimit:
                   self.Status = FAIL
                   objMsg.printMsg('%s RList check failed' %self.TestName)
                else:
                   self.Status = OK
                   objMsg.printMsg('%s RList check passed!' % self.TestName)
   
             
             except ValueError:
                objMsg.printMsg('Error! temp=%s' %temp)      
                #temp = 0
                # DT211210 Fail when firmware did not return
                self.Status = FAIL

       if self.Status == FAIL:
          data = {}
          data['LBA'] = '0' 
          data['STS'] = '00' 
          data['ERR'] = '00'           
          self.failLLRET = 'SerialPortError'   
            
          failure = ('%s %s' % ('IDT', self.TestName))
          objMsg.printMsg('%s RList check failed!' % self.TestName)   
             
          self.failCode = self.oFC.getFailCode(failure)
          self.testEndTime = time.time()
          self.failStatus = ('STS%s-ERR%s' % (int(data['STS']), int(data['ERR']) ))
          self.DrvAttr['MQM_FAIL_TTF'] = timetostring(self.testEndTime-self.testStartTime)
          self.DrvAttr['MQM_FAIL_SEQ'] = failure
          self.DrvAttr['MQM_FAIL_LBA'] = data['LBA']
          self.DrvAttr['MQM_FAIL_CODE'] = self.failCode
          self.DrvAttr['MQM_FAIL_LLRET'] = self.failLLRET
          self.DrvAttr['MQM_FAIL_STATUS'] = self.failStatus
          DriveAttributes.update(self.DrvAttr)             


       return 0

       
   #------------------------------------------------------------------------------------------------------#
   def checkDriveCongen(self):
       """
         Utility check drive congen
       """
       self.TestName = 'Check Congen'
       congenPattern = 'CongenConfigurationState ='
       temp = 'NotFound'
 
       self.printTestName(self.TestName)
       if self.CellType.find('CPC') >= 0:
          ICmd.SetSerialTimeout(self.SerialTimeout)
          
       #RT130911: SI/N2 powercycle without prepower sequence 
       self.powerCycle('TCGUnlock', 0)
       self.Status = self.disableAPM(self.TestName)   
              
       if self.Status == OK:
          sptCmds.enableDiags(self.NumRetry)
          sptCmds.gotoLevel('T')
          serialBuff = sptCmds.sendDiagCmd('F"CongenConfigurationState"', self.SerialTimeoutExt)
          objMsg.printMsg('LevelT F"CongenConfigurationState" Data=%s' % serialBuff)
  
          try:
             m = re.search(congenPattern, str(serialBuff))
             temp = serialBuff[m.end():].split()[0]
          except:
             pass

          objMsg.printMsg('DriveCongen=%s !' % temp)
          offset = temp.find('02')      # 00 or 01 is acceptable
          if offset >= 0:
             self.Status = FAIL
             objMsg.printMsg('Congen check failed!')
          else:
             self.Status = OK
             objMsg.printMsg('Congen check passed!')  

       if self.Status == FAIL:
          data = {}
          data['LBA'] = '0' 
          data['STS'] = '00' 
          data['ERR'] = '00'           
          self.failLLRET = 'SerialPortError'   
            
          failure = ('%s %s' % ('IDT', self.TestName))
          objMsg.printMsg('%s - Congen check failed! Do not ship drive!!!' % self.TestName)                
          
          self.failCode = self.oFC.getFailCode(failure)
          self.testEndTime = time.time()
          self.failStatus = ('STS%s-ERR%s' % (int(data['STS']), int(data['ERR']) ))
          self.DrvAttr['MQM_FAIL_TTF'] = timetostring(self.testEndTime-self.testStartTime)
          self.DrvAttr['MQM_FAIL_SEQ'] = failure
          self.DrvAttr['MQM_FAIL_LBA'] = data['LBA']
          self.DrvAttr['MQM_FAIL_CODE'] = self.failCode
          self.DrvAttr['MQM_FAIL_LLRET'] = self.failLLRET
          self.DrvAttr['MQM_FAIL_STATUS'] = self.failStatus
          DriveAttributes.update(self.DrvAttr)

       return 0
      
       
   #------------------------------------------------------------------------------------------------------#
   def checkUDR(self):
      """
      Utility check for UDR support
      """
      self.TestName = 'Check UDR'
      LTTCPattern = 'LTTC-UDR2 '
      udrPattern = 'enabled '
      temp = 'NotFound'

      self.printTestName(self.TestName)

      if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
         pass  # ICmd T538: SetFeatures already includes hard reset to initialize the drive ready 
      else:
         #RT130911: SI/N2 powercycle without prepower sequence 
         self.powerCycle('TCGUnlock', 0)
      self.Status = self.disableAPM(self.TestName)   
       #RT120112: change due to CPC intrinsic removal
      if self.CellType.find('CPC') >= 0 and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #only for intrinsic CPC
         ICmd.SetSerialTimeout(self.SerialTimeout)  
         ICmd.ClearSerialBuffer()  

      if self.Status == OK:
         sptCmds.enableDiags(self.NumRetry)
          
         #accumulator = baseComm.PChar(CTRL_L)
         #data = sptCmds.promptRead(self.SerialTimeoutExt, 0, altPattern = '>', accumulator = accumulator)          
         
         #data = sptCmds.sendDiagCmd(CTRL_L, 120, altPattern='LTTC-UDR2', raiseException=0)
         data = sptCmds.sendDiagCmd(CTRL_L, self.SerialTimeoutExt, altPattern='LTTC-UDR2', raiseException=0)

         objMsg.printMsg('CtrlL Data=%s' % data)
         try:
            m = re.search(LTTCPattern, str(data))
            data = data[m.end():]

         except:
            pass
       
         offset = data.find(udrPattern)
         if offset >= 0:
            temp = data[offset: offset+7]
            objMsg.printMsg('LTTC UDR2=%s' % str(temp))         
            self.UDREnable = 'ON'
         else:
            objMsg.printMsg('UDR not enabled/supported!')         
            self.UDREnable = 'OFF'                   

      return 0

   
   #------------------------------------------------------------------------------------------------------#
   def disableUDR(self):
       """
         Utility Disable UDR 
       """
    
       self.TestName = 'Disable UDR'
       RevPattern = ': Rev '
       N24CmdSupport = ON
       LBA = 0
       sectCnt = 256

       self.printTestName(self.TestName)       
       
       #RT130911: SI/N2 powercycle without prepower sequence 
       self.powerCycle('TCGUnlock', 0)
       #RT120112: change due to CPC intrinsic removal
       if self.CellType.find('CPC') >= 0 and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #only for intrinsic CPC     
          ICmd.ClearSerialBuffer()
          ICmd.SetSerialTimeout(self.SerialTimeout)
          
       self.Status = self.disableAPM(self.TestName)
       
       if self.Status == OK:
          sptCmds.enableDiags(self.NumRetry)
          sptCmds.gotoLevel('1')
          data = sptCmds.sendDiagCmd('N?', self.SerialTimeout)
          objMsg.printMsg('Level1 N? Data=%s' % data)
          
          try:
             m = re.search(RevPattern, str(data))
             data = data[m.end():].split(',')[0]
             objMsg.printMsg('Rev=%s' % data)      

          except:
             pass
          
          try:
             temp1 = int(data[0:4])
             temp2 = int(data[5:9])
         
          except ValueError: 
             temp1 = -1
             temp2 = -1

          
          rev = temp1*10000 + temp2 
          if rev >= 150001:     # ScPark NSG firmware rev that support N24 to disable UDR 
             objMsg.printMsg('Fimware Rev support N24 to disable UDR!')
             data = sptCmds.sendDiagCmd('N24', self.SerialTimeout)
             objMsg.printMsg('Level1 N24 Data=%s' % data)
             
             # DT LAST
#             if data.find{'DiagError') >= 0:
#                objMsg.printMsg('N24 to disable UDR failed!') 
#                self.Status = FAIL 
#             else:
#                objMsg.printMsg('N24 to disable UDR passed!')
                
          else:
             objMsg.printMsg('Firmware Rev does not support N24 to disable UDR!')
             N24CmdSupport = OFF

       
       # Disable UDR using WriteLong
       if self.Status == OK and N24CmdSupport == OFF:
          self.powerCycle()
          objMsg.printMsg('UDR enabled, using ReadLong/WriteLong to disable UDR. LBA=%d SectCnt=%d' % (LBA, sectCnt))
          
          ICmd.ClearBinBuff(WBF);  ICmd.ClearBinBuff(RBF)
          stat = ICmd.ReadLong(LBA)

          #RT120112: change due to CPC intrinsic removal  update on 230412 for failures in Tambora (UDR drive)
          if self.CellType.find('CPC') >= 0 and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #only for intrinsic CPC
             data = stat
          else:
             data = ICmd.translateStReturnToCPC(stat)

          self.Status = data['LLRET']
          objMsg.printMsg('ReadLong. Result=%s Data=%s' % (str(self.Status), str(data)))
          if self.Status != OK:
             objMsg.printMsg('ReadLong failed. Result=%s Data=%s' % (str(self.Status), str(data)))
             
          if self.Status == OK:
             ICmd.BufferCopy(WBF, 0, RBF, 0, 512)
             stat = ICmd.WriteLong(LBA)
             #RT120112: change due to CPC intrinsic removal  update on 230412 for failures in Tambora (UDR drive)
             if self.CellType.find('CPC') >= 0 and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: #only for intrinsic CPC
                data = stat
             else:
                data = ICmd.translateStReturnToCPC(stat)

             self.Status = data['LLRET']
             objMsg.printMsg('WriteLong. Result=%s Data=%s' % (str(self.Status), str(data)))
             
          if self.Status == OK:   
             objMsg.printMsg('WriteLong passed. UDR Disabled successful!')
          else: 
             objMsg.printMsg('WriteLong failed. Result=%s Data=%s' % (str(self.Status), str(data)))
             
          if self.Status != OK:
             failure = 'IDT SET UDR'
             data = {}
             data['LBA'] = '0' 
             data['STS'] = '00' 
             data['ERR'] = '00'           
             self.failLLRET = 'SerialPortError'   

             self.failCode = self.oFC.getFailCode(failure)
             self.testEndTime = time.time()
             self.failStatus = ('STS%s-ERR%s' % (int(data['STS']), int(data['ERR']) ))
             self.DrvAttr['MQM_FAIL_TTF'] = timetostring(self.testEndTime-self.testStartTime)
             self.DrvAttr['MQM_FAIL_SEQ'] = failure
             self.DrvAttr['MQM_FAIL_LBA'] = data['LBA']
             self.DrvAttr['MQM_FAIL_CODE'] = self.failCode
             self.DrvAttr['MQM_FAIL_LLRET'] = self.failLLRET
             self.DrvAttr['MQM_FAIL_STATUS'] = self.failStatus
             DriveAttributes.update(self.DrvAttr)


       return 0
   
   #------------------------------------------------------------------------------------------------------#
   def enableUDR(self):
       """
         Utility enabling UDR using N23
         Assume drive in serial diagnostic mode level 1
       """

       self.TestName = 'Enable UDR'
       LTTCPattern = 'LTTC-UDR2 '
       TogglePattern = 'enabled '  # 'disabled ' 
       temp = 'NotFound'
       
       self.printTestName(self.TestName)
       
       if self.CellType.find('CPC') >= 0:
          # DT200111 Fix Bug in Flush Serial Buffer
          ICmd.ClearSerialBuffer()  
       
       if self.Status == OK:
          if self.CellType.find('CPC') >= 0:
             serialBuffer = sptCmds.sendDiagCmd('N23', self.SerialTimeout)
          else : #RT200111 Prolong serial timeout to 60secs
             serialBuffer = sptCmds.sendDiagCmd('N23', self.CtoCTimeout)
          objMsg.printMsg('Level1 N23 Data=%s' % serialBuffer)

          if serialBuffer.find('DiagError') >= 0:
             objMsg.printMsg('N23 UDR Re-enabling failed!') 
             self.Status = FAIL 
             failure = 'IDT SET UDR'
             data = {}
             data['LBA'] = '0' 
             data['STS'] = '00' 
             data['ERR'] = '00'           
             self.failLLRET = 'SerialPortError'   
                          
             self.failCode = self.oFC.getFailCode(failure)
             self.testEndTime = time.time()
             self.failStatus = ('STS%s-ERR%s' % (int(data['STS']), int(data['ERR']) ))
             self.DrvAttr['MQM_FAIL_TTF'] = timetostring(self.testEndTime-self.testStartTime)
             self.DrvAttr['MQM_FAIL_SEQ'] = failure
             self.DrvAttr['MQM_FAIL_LBA'] = data['LBA']
             self.DrvAttr['MQM_FAIL_CODE'] = self.failCode
             self.DrvAttr['MQM_FAIL_LLRET'] = self.failLLRET
             self.DrvAttr['MQM_FAIL_STATUS'] = self.failStatus
             DriveAttributes.update(self.DrvAttr)
             
       return 0


   #------------------------------------------------------------------------------------------------------#
   def checkSeaCos(self):
       """
         Utility check for SeaCos

       """

       self.TestName = 'Check SeaCos'
       self.printTestName(self.TestName)
       if self.Status == OK:
          self.powerCycle()
          self.Status = self.disableAPM(self.TestName) 
          
       if self.CellType.find('CPC') >= 0:   
          ICmd.ClearSerialBuffer()
       
       if self.Status == OK:
          sptCmds.enableDiags(self.NumRetry)
          accumulator = baseComm.PChar(CTRL_Z)
          data = sptCmds.promptRead(self.SerialTimeout, 0, altPattern = "&>", accumulator = accumulator)          

          objMsg.printMsg('CtrlZ Data=%s' % data)
  
          if (data.find('Serial Port Disabled') >= 0) or (data.find('?>') >= 0):
             objMsg.printMsg('Serial port locked! Trusted drive detected!')
             self.IDAttr['Kwai Unlock'] = 'ON'
             #self.checkTCG()

          elif (self.IDAttr['SeaCos_Support'] == 'ON') and (self.IDAttr['SeaCos_Enable'] == 'ON'):                      
             objMsg.printMsg('SeaCOS support enabled, but serial port not locked!')
             self.Status = FAIL
          else:
             self.IDAttr['Kwai Unlock'] = 'OFF'

       return 0

   #------------------------------------------------------------------------------------------------------#
   def checkBlackArmour(self):
       """
         Utility check for BlackArmour FDE from CtrlA returns

       """
       self.TestName = 'BlackArmour Detection'
       rev = 'NotFound'
       self.printTestName(self.TestName)
       if self.Status == OK:
        
          self.powerCycle()
          self.Status = self.disableAPM(self.TestName) 
          
          if self.CellType.find('CPC') >= 0:
             ICmd.ClearSerialBuffer() 
          
          if self.Status == OK:
             sptCmds.enableDiags(self.NumRetry)
             accumulator = baseComm.PChar(CTRL_A)
             data = sptCmds.promptRead(self.SerialTimeout, 0, altPattern = "Package Version:", accumulator = accumulator)          

             for signature in self.BlackArmourID:
                objMsg.printMsg('Checking BlackArmour signature=%s' % str(signature))
                ind = data.find(signature)
                if ind >= 0:
                   rev = data[ind-7: ind+16]
                   self.IDAttr['BlackArmour'] = 'ON'
                   self.IDAttr['InterfaceUnlock'] = 'ON'
                   objMsg.printMsg('BlackArmour signature=%s detected! Rev=%s ' % (str(signature), str(rev)))
                   break
                else:
                   objMsg.printMsg('Drive not FDE BlackArmour! Rev=%s ' % str(rev))

       return 0

   #------------------------------------------------------------------------------------------------------#
   def checkTCG(self):
    
       """
         Utility check for TCG 
       """
       T_Msg = ON    
       result = OK
       self.TestName = 'TCG Detection'    

       #SetBaudRate(Baud38400)
       
#       from sptCmds import *
#       if(sptCmds.checkTCG()):
#          self.UnlockDiag = 'ON' 
       
#       ICmd.SetIntfTimeout(10000)
#       ICmd.SetSerialTimeout(10000)
#       
#       ICmd.ClearSerialBuffer()
#       
#       
#       #ConfigVars[CN]['TCG Unlock'] = 'OFF'
#       CtrlZ = '\x1A'
#       self.printTestName(self.TestName)
#    
#       if ConfigVars[CN].has_key('TCG ENABLE') and ConfigVars[CN]['TCG ENABLE'] != UNDEF and ConfigVars[CN]['TCG ENABLE'] == 'ON':
#          objMsg.printMsg('Config TCG ENABLE set to ON!')
#
#          if self.Status == OK:
#             self.powerCycle()
#             self.Status = self.disableAPM(self.TestName) 
#             ICmd.ClearSerialBuffer() 
#
#          if self.Status == OK:    
#             #data = Ctrl('Z', m)
#             data = ICmd.SerialCommand(CtrlZ)
#             self.Status = data['LLRET']
#             SerialBuff = ICmd.GetBuffer(SBF, 0, 1024)['DATA']
#             objMsg.printMsg('CtrlZ Result=%s Data=%s' % (self.Status, data))
#             objMsg.printMsg( 'UnlockDrive Data returned from Ctrl-Z command = %s' % SerialBuff )
#             # Drive is locked if serial port returned 'TCG' 
#             if SerialBuff.find('&>')>-1: 
#                objMsg.printMsg('Drive serial port locked - TCG Trusted Drive')
#                self.UnlockDiag = 'ON'
#             else:      
#                self.Status = FAIL
             
#      if self.DrvAttr['TCG Unlock'] == 'ON':
#       if self.UnlockDiag == 'ON':
#          objMsg.printMsg('>>>>> TCG Drive discovered.  InitTCGState!')
#          InitTCGState()    # Can Skip as Process script already performed

       return 0

   #------------------------------------------------------------------------------------------------------#
   def getDellPPID(self):
       """
         Utility read Log9A for Dell PPID
       """
       ppid = ''
       pattern1 = '\xFF'          
       pattern2 = '\x00'

       self.TestName = 'Get DellPPID'
       self.printTestName(self.TestName)
       if self.Status == OK:
          for i in range(self.NumRetry):
             self.powerCycle()
             data = ICmd.SmartEnableOper()
             self.Status = data['LLRET']
             objMsg.printMsg('SmartEnableOper Data=%s' % str(data))

             if self.Status == OK:
                break
             else:
                objMsg.printMsg('Retry SmartEnableOper')

          if self.Status == OK:   
             data = ICmd.SmartReadLogSec(0x9A,1)    # 1 sector
             self.Status = data['LLRET']
             objMsg.printMsg('SmartReadLogSec Data=%s' % str(data))
   
          if self.Status == OK:
             smartData = ICmd.GetBuffer(RBF, 0, 512*1)['DATA']   # RBF get 1 sector  
             objMsg.printMsg('SmartReadLogSec Data=%s' % str(smartData) )
             #WriteToResultsFile(smartData + '\n')  

          if self.Status == OK:
             if (smartData[0] == pattern1) or (smartData[0] == pattern2):
                objMsg.printMsg('No Dell PPID Info Found in Log9A!')
                
             else:
                objMsg.printMsg('Dell PPID found in Log9A!')
                for item in range(1, len(smartData), 2):
                   ppid += smartData[item]+ smartData[item-1]
                self.DellPPID = ppid[:len(smartData)]
                objMsg.printMsg('Dell PPID=%s' % str(self.DellPPID))
                self.DrvAttr['DELLPPID'] = self.DellPPID
     
       return 0
 
   #------------------------------------------------------------------------------------------------------#
   def checkSmartPOH(self):
       """
         Utility check POH value after SMART reset
         
       """
       self.TestName = 'Check SmartPOH'
       self.printTestName(self.TestName)    
       if self.Status == OK:
          for i in range(self.NumRetry):
             #RT130911: SI/N2 powercycle without prepower sequence 
             self.powerCycle('NO', 0)
             #self.Status = self.disableAPM(self.TestName) 
             data = ICmd.SmartEnableOper()
             self.Status = data['LLRET']
             objMsg.printMsg('SmartEnableOper Data=%s' % str(data))

             if self.Status == OK:
                break
             else:
                objMsg.printMsg('Retry SmartEnableOper')

          if self.Status == OK:   
             data = ICmd.SmartReadData()
             self.Status = data['LLRET']
             #smartData = data['GETBUFFER']['DATA']
             objMsg.printMsg('SmartReadData Data=%s' % str(data))

          if self.Status == OK:
             smartData = ICmd.GetBuffer(RBF, 0, 512)['DATA']     
             #objMsg.printMsg('SmartReadData SmartData=%s' % smartData)
             #WriteToResultsFile(smartData + '\n')  

          if self.Status == OK:
             smartAttr = CSmartAttributes(smartData)
             smartAttr.decodeAttribute(9)
             POH_Raw = smartAttr.Attribute['RawValue']
             objMsg.printMsg('Smart Attribute POH Raw = 0x%X' % POH_Raw)            
             # DT050109 Check 4 bytes (0-3) only
             POH_Raw = POH_Raw & 0xFFFFFFFF
             objMsg.printMsg('Smart Attribute POH & 0xFFFFFFFF = 0x%X' % POH_Raw)  
             if POH_Raw != 0:
                objMsg.printMsg('Check POH failed!')            
                self.Status = FAIL
             else:
                objMsg.printMsg('Check POH passed!')            
          
       return 0

   #------------------------------------------------------------------------------------------------------#
   def checkSmartLogs(self, LogList, check=ON):
       """
         Utility check SMART Logs

            Log A1  Critical Event Log
            Log A7  Reserved (RList)
            Log A8  Grown Defect Log (GList)
            Log A9  Pending Defect Log (PList)
         
         Usage : checkSmartLogs([0xA1,0xA8,0xA9])
                 checkSmartLogs([0xA1,0xA8,0xA9], OFF)  # purely in display mode
                  
         
       """
       #RT120911: initialize the failure variable and add exception handler
       failure = 'NIL'
       
       if check == ON: self.TestName = 'Check SmartLog'
       else : self.TestName = 'Display SmartLog'    
       self.printTestName(self.TestName) 
       if self.Status == OK:
          try: 
             for i in range(self.NumRetry):
                if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION and objRimType.IOInitRiser():
                   pass # Let ICmd smart hard reset handle the IO reset 
                else:
                   self.powerCycle()
                #self.Status = self.disableAPM(self.TestName) 
                data = ICmd.SmartEnableOper()
                self.Status = data['LLRET']
                objMsg.printMsg('SmartEnableOper Data=%s' % str(data))

                if self.Status == OK:
                   break
                else:
                   objMsg.printMsg('Retry SmartEnableOper')

             if self.Status == OK:

                for log in range(len(LogList)):
                   CurrLog = LogList[log]
                   LogSize = self.getSmartLogSize(CurrLog) # returns number of sectors
                   
                   if LogSize == 0:
                      objMsg.printMsg('%X Log not supported, Log=%d sectors, ' % (CurrLog,LogSize) )   
                      continue
                 
                   objMsg.printMsg('%X Log Count=%d sectors' % (CurrLog, LogSize) )   
                   data = ICmd.SmartReadLogSec(CurrLog, LogSize)
                   objMsg.printMsg('SmartReadLogSec Data=%s' % str(data))
                   self.Status = data['LLRET']
                   
                   if self.Status == OK:
                      smartData = ICmd.GetBuffer(RBF, 0, 512* LogSize)['DATA']     
                      #objMsg.printMsg('SmartReadLogSec Data=%s' % str(smartData))  
                      #defectBuffer = data['GETBUFFER']['DATA'][:512*LogSize]

                      # DT180809 Apple RList Check
                      if CurrLog == 0xA7:
                         RList = CSmartDefect(smartData, LogSize)
                         defectList = RList.defectList
                         numOfEvents = len(defectList)
                         objMsg.printMsg('Number of Events in RList:%d' % numOfEvents)
                         if numOfEvents > 0:
                            objMsg.printMsg('RList Entries:%s'  % defectList)
                            objMsg.printMsg('RList Limit:%d' % self.RListLimit)
                            if numOfEvents > self.RListLimit:
                               objMsg.printMsg('RList Entries Exceeds Limit!')
                               # DT300510
                               if check == ON: 
                                  failure = 'IDT RLIST LOG'
                                  self.Status = FAIL
              
                      if CurrLog == 0xA8:
                         GList = CSmartDefect(smartData, LogSize)
                         defectList = GList.defectList
                         numOfEvents = len(defectList)
                         objMsg.printMsg('Number of Events in GList:%d' % numOfEvents)
                         if numOfEvents > 0:
                            objMsg.printMsg('GList Entries:%s' % defectList)
                            objMsg.printMsg('GList Limit:%d' % self.GListLimit)
                            if numOfEvents > self.GListLimit:
                               objMsg.printMsg('GList Entries Exceeds Limit!')
                               # DT300510
                               if check == ON: 
                                  failure = 'IDT A8 LOG'
                                  self.Status = FAIL
                          
                      if CurrLog == 0xA9:
                         PList = CSmartDefect(smartData, LogSize)
                         defectList = PList.defectList
                         numOfEvents = len(defectList)
                         objMsg.printMsg('Number of Events in PList:%d' % numOfEvents)
                         if numOfEvents > 0:
                            objMsg.printMsg('PList Entries:%s' % defectList)
                            objMsg.printMsg('PList Limit:%d' % self.PListLimit)
                            if numOfEvents > self.PListLimit:
                               objMsg.printMsg('PList Entries Exceeds Limit!')
                               # DT300510
                               if check == ON: 
                                  failure = 'IDT A9 LOG'
                                  self.Status = FAIL

                      if CurrLog == 0xA1:
                         # DT TEMP
                         #objMsg.printMsg('CE Log Raw Data: %s' % str(smartData))
                         CELog = CSmartCriticalEventF3(smartData, LogSize)
                         eventList = CELog.eventList
                         numOfEvents = len(eventList)
                         numOfCriticalEvents = CELog.getCriticalEventCnt()
                         objMsg.printMsg('Number of Events in CE Log:%d' % numOfEvents)
                         objMsg.printMsg('Number of Critical Events in CE Log:%d' % numOfCriticalEvents)
                         if numOfCriticalEvents > 0:
                            objMsg.printMsg('CE Log Entries: %s' % eventList)
                            objMsg.printMsg('CE Log Entries Exceeds Limit: Event Type (2,3,7 or B) exists!')
                            # DT300510
                            if check == ON: 
                               failure = 'IDT CE LOG'
                               self.Status = FAIL

          except:
             ScrCmds.raiseException(13061)
             self.Status = FAIL
             
          # DT300510
          if check == ON: 
             if self.Status == OK:
                objMsg.printMsg('Smart Logs Check passed!')          
             else:
                objMsg.printMsg('Smart Logs Check failed!')       
                if data.has_key('LBA') == 0: data['LBA'] = '0' 
                if data.has_key('STS') == 0: data['STS'] = '00' 
                if data.has_key('ERR') == 0: data['ERR'] = '00'           
                if data.has_key('LLRET'): self.failLLRET = data['LLRET']   
             
                self.failCode = self.oFC.getFailCode(failure)
                self.testEndTime = time.time()
                self.failStatus = ('STS%s-ERR%s' % (int(data['STS']), int(data['ERR']) ))
                self.DrvAttr['MQM_FAIL_TTF'] = timetostring(self.testEndTime-self.testStartTime)
                self.DrvAttr['MQM_FAIL_SEQ'] = failure
                self.DrvAttr['MQM_FAIL_LBA'] = data['LBA']
                self.DrvAttr['MQM_FAIL_CODE'] = self.failCode
                self.DrvAttr['MQM_FAIL_LLRET'] = self.failLLRET
                self.DrvAttr['MQM_FAIL_STATUS'] = self.failStatus
                DriveAttributes.update(self.DrvAttr)


       return 0
       
   #------------------------------------------------------------------------------------------------------#
   def getSmartLogSize(self, LogNum):
       """
         Utility get Smart Log size
       """
       size = 0
        
       # get log size from :log 0, 1 sector
       if self.Status == OK:   
          data = ICmd.SmartReadLogSec(0, 1)
          self.Status = data['LLRET']
          objMsg.printMsg('SmartReadLogSec(0,1) Status=%s' % str(self.Status))
          
          if self.Status == OK:
             # DT140610
             try: 
                smartData = ICmd.GetBuffer(RBF, 0, 512)['DATA']     
                #objMsg.printMsg("SmartData=%s" % smartData)
                #size = ord(data['GETBUFFER']['DATA'][LogNum*2])
                size = ord(smartData[LogNum*2])
                objMsg.printMsg('LogSize=%d' % size)
             except: objMsg.printMsg("Serial Buffer is Empty") 
            
          else:
             objMsg.printMsg('SmartReadLogSec failed. Log0x0 Data=%s' % data)
             
       return size

   
   #------------------------------------------------------------------------------------------------------#
   def checkSmartAttr(self, check=ON):
       """
         Utility check SMART Attribute 
            Attr 5      Retired Sector Count   
            Attr 184    IOEDC 
            Attr 197    Pending Sparing Count
            Attr 198    Uncorrectable Sector Count
            Byte 410    Retired Sector Count when last Smart Reset
            Byte 412    Pending Spare Count when last Smart Reset
           
            check = OFF Display only 
         
       """
       
       if check == ON: self.TestName = 'Check SmartAttribute'
       else: self.TestName = 'Display SmartAttribute'
       self.printTestName(self.TestName) 
       if ConfigVars[CN].has_key('SMART CHECK B410') and ConfigVars[CN]['SMART CHECK B410'] != UNDEF and ConfigVars[CN]['SMART CHECK B410'] == 'OFF':
          Check_B410 = OFF

       if ConfigVars[CN].has_key('SMART CHECK B412') and ConfigVars[CN]['SMART CHECK B412'] != UNDEF and ConfigVars[CN]['SMART CHECK B412'] == 'OFF':   
          Check_B412 = OFF
                
       if ConfigVars[CN].has_key('SMART CHECK IOEDC') and ConfigVars[CN]['SMART CHECK IOEDC'] != UNDEF and ConfigVars[CN]['SMART CHECK IOEDC'] == 'ON':   
          Check_IOEDC = ON

       if ConfigVars[CN].has_key('SMART CHECK A198') and ConfigVars[CN]['SMART CHECK A198'] != UNDEF and ConfigVars[CN]['SMART CHECK A198'] == 'ON':   
          Check_A198 = ON
 

       if self.Status == OK:
          for i in range(self.NumRetry):
             if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION and objRimType.IOInitRiser():
                pass # Let ICmd smart hard reset handle the IO reset
             else:    
                self.powerCycle()
             #self.Status = self.disableAPM(self.TestName) 
             data = ICmd.SmartEnableOper()
             self.Status = data['LLRET']
             objMsg.printMsg('SmartEnableOper Data=%s' % str(data))

             if self.Status == OK:
                break
             else:
                objMsg.printMsg('Retry SmartEnableOper')

          if self.Status == OK:   
             data = ICmd.SmartReadData()
             self.Status = data['LLRET']
             #smartData = data['GETBUFFER']['DATA']
             objMsg.printMsg('SmartReadData Status=%s' % str(self.Status))

          if self.Status == OK:
             smartData = ICmd.GetBuffer(RBF, 0, 512)['DATA']
             #objMsg.printMsg('SmartReadData SmartData=%s' % (smartData))  
             #WriteToResultsFile(smartData + '\n')  

          if self.Status == OK:
             smartAttr = CSmartAttributes(smartData)
  
             smartAttr.decodeAttribute(5)
             A5_RetdSectCnt = smartAttr.Attribute['RawValue']
             smartAttr.decodeAttribute(197)
             A197_PendSpareCnt = smartAttr.Attribute['RawValue']
             smartAttr.decodeAttribute(198)
             A198_UncorrSectCnt = smartAttr.Attribute['RawValue']
             smartAttr.decodeAttribute(184)
             A184_IOEDC = smartAttr.Attribute['RawValue']
             
             # Read direct from buffer 
             B410_RepRetdSectCnt = (ord(smartAttr.buffer[410]) & 0xFF) + ((ord(smartAttr.buffer[411]) & 0xFF) << 8)
             B412_RepPendSpareCnt = (ord(smartAttr.buffer[412]) & 0xFF) + ((ord(smartAttr.buffer[413]) & 0xFF) << 8)
             
             objMsg.printMsg('Retired Sector Count(Attr5): %d' % A5_RetdSectCnt)
             objMsg.printMsg('Reported IOEDC Errors(Attr184): %d' % A184_IOEDC) 
             objMsg.printMsg('Pending Spare Count(Attr197): %d' % A197_PendSpareCnt) 
             objMsg.printMsg('Uncorrectable Sector Count(Attr198): %d' % A198_UncorrSectCnt) 
             objMsg.printMsg('Spare Count(B410) when last SmartReset: %d' % B410_RepRetdSectCnt)
             objMsg.printMsg('Pending Spare Count(B412) when last SmartReset: %d' % B412_RepPendSpareCnt)
            
             #################################################################
             # DT270510 Added for display
             smartAttr.decodeAttribute(1)     # Raw Error Rate
             A1_RAW = smartAttr.Attribute['RawValue']
             objMsg.printMsg('Raw Error Rate(Attr1): %d, 0x%X' % ((A1_RAW & 0xFFFFFFFF), A1_RAW))
             
             smartAttr.decodeAttribute(188)     # Cmd Timeout
             A188_CmdTimeout = smartAttr.Attribute['RawValue']
             objMsg.printMsg('Cmd Timeout Count >7.5s (Attr188): %d, 0x%X' % ((A188_CmdTimeout & 0xFFFF00000000), A188_CmdTimeout))
                          
             smartAttr.decodeAttribute(195)     # ECC OTF
             A195_ECCOTF = smartAttr.Attribute['RawValue']
             objMsg.printMsg('ECC On-The-Fly Count(Attr195): %d, 0x%X' % ((A195_ECCOTF & 0xFFFFFFFF), A195_ECCOTF))
             
             smartAttr.decodeAttribute(199)     # UDMA CRC Error Count
             A199_UDMACRCErrCnt = smartAttr.Attribute['RawValue']
             objMsg.printMsg('UDMA ECC Error Count(Attr199): %d, 0x%X' % ((A199_UDMACRCErrCnt & 0xFFFFFFFF), A199_UDMACRCErrCnt))
             
             B422_NumRAWReWrt = (ord(smartAttr.buffer[422]) & 0xFF) + ((ord(smartAttr.buffer[423]) & 0xFF) << 8)
             B438_SysWrtFailCnt = (ord(smartAttr.buffer[438]) & 0xFF) + ((ord(smartAttr.buffer[439]) & 0xFF) << 8)
             objMsg.printMsg('Number of ReadAfterWrite(422) need Rewrite: %d' % B422_NumRAWReWrt)
             objMsg.printMsg('Number of System Write Failures(438): %d' % B438_SysWrtFailCnt)
             
             #################################################################
            
             

             if (A5_RetdSectCnt > self.GListLimit):
                objMsg.printMsg('Retired Sector Count(Attr5) exceeded Glist limit')
                # DT270510
                if check == ON:
                   failure = 'IDT A8 LOG'
                   self.Status = FAIL
          
             if (A197_PendSpareCnt > self.PListLimit):
                objMsg.printMsg('Pending Spare Count(Attr197) exceeded Plist limit')
                # DT270510
                if check == ON:
                   failure = 'IDT A9 LOG'
                   self.Status = FAIL

             if (A184_IOEDC > self.IOEDCLimit):
                objMsg.printMsg('Reported IOEDC Errors(Attr184) exceeded IOEDC limit')
                # DT270510
                if check == ON:
                   failure = 'IDT A184 IOEDC'
                   self.Status = FAIL

             if (A198_UncorrSectCnt > self.A198Limit):
                objMsg.printMsg('Uncorrectable Sector Count(Attr198) exceeded A198 limit')
                # DT270510
                if check == ON:
                   failure = 'IDT A198 USC'
                   self.Status = FAIL

             if (B410_RepRetdSectCnt > self.GListLimit):
                objMsg.printMsg('Spare Count(410) when last SmartReset exceeded Glist limit')
                # DT270510
                if check == ON:
                   failure = 'IDT A8 LOG'
                   self.Status = FAIL

             if (B412_RepPendSpareCnt > self.PListLimit):
                objMsg.printMsg('Pending Spare Count(412) when last SmartReset exceeded Plist limit')
                # DT270510
                if check == ON:
                   failure = 'IDT A9 LOG'
                   self.Status = FAIL
          
          # DT270510
          if check == ON:   
             if self.Status == OK:
                objMsg.printMsg('Smart Attribute Check passed!')          
             else:
                objMsg.printMsg('Smart Attribute Check failed!')       
                if data.has_key('LBA') == 0: data['LBA'] = '0' 
                if data.has_key('STS') == 0: data['STS'] = '00' 
                if data.has_key('ERR') == 0: data['ERR'] = '00'           
                if data.has_key('LLRET'): self.failLLRET = data['RESULT']   
                self.failCode = self.oFC.getFailCode(failure)
                self.testEndTime = time.time()
                self.failStatus = ('STS%s-ERR%s' % (int(data['STS']), int(data['ERR']) ))
                self.DrvAttr['MQM_FAIL_TTF'] = timetostring(self.testEndTime-self.testStartTime)
                self.DrvAttr['MQM_FAIL_SEQ'] = failure
                self.DrvAttr['MQM_FAIL_LBA'] = data['LBA']
                self.DrvAttr['MQM_FAIL_CODE'] = self.failCode
                self.DrvAttr['MQM_FAIL_LLRET'] = self.failLLRET
                self.DrvAttr['MQM_FAIL_STATUS'] = self.failStatus
                DriveAttributes.update(self.DrvAttr)

       return 0

   #------------------------------------------------------------------------------------------------------#
   def powerCycle(self, Unlock='NO', PrePower=1, driveOnly = 0, useHardReset = 0):
       """
          Utility Power Cycle
       """
       
       self.TestName = ('PowerCycle Unlock=%s' %Unlock)
       self.printTestName(self.TestName)    
       
       self.prePowerCycle(PrePower)
       
       objMsg.printMsg("PowerOn 5V=%s 12V=%s" % (self.v5, self.v12))
       if testSwitch.IO_MQM_SIC_TESTTIME_OPTIMIZATION:
          if useHardReset and (Unlock is 'NO'):
             objMsg.printMsg("Cell temperature =%s degC" % str(ReportTemperature()/10 ) )
             self.defaultSetup()    # Use ICmd.HardReset to initialize drive option for SIC test time reduction.   
             return 0               # SetFeatures in EnableAPM uses hard reset to initialize drive.
          objPwrCtrl.powerCycle(self.v5, self.v12, driveOnly = driveOnly)
       else:  
          objPwrCtrl.powerCycle(self.v5, self.v12)
       
       objMsg.printMsg("Cell temperature =%s degC" % str(ReportTemperature()/10 ) )

       if Unlock == 'TCGUnlock':
          if self.UnlockDiag == 'ON':
             objMsg.printMsg('>>>>> TCG Unlocking Diag!' )
             ReliUnlockDiagUDE()
             #DirectUnlockDiagUDE()
          if self.UnlockFDE == 'ON':
             objMsg.printMsg('>>>>> FDE Unlocking Diag!')
             from KwaiPrep import CKwaiPrepTest
             oKwaiPrep = CKwaiPrepTest(objDut)
             result = oKwaiPrep.UnlockSerialPort()
             objMsg.printMsg("FDE SerialPort Unlock result=%s" % result)
             
             
             
       self.defaultSetup()
       
       return 0

   #------------------------------------------------------------------------------------------------------#
   def powerCycleTimer(self, offTime=10, onTime=10, Unlock='NO'):
       """
          Utility Power Cycle with Timer
       """
       
       self.prePowerCycle()
       
       objMsg.printMsg("PowerOn 5V=%s 12V=%s offTime=%s onTime=%s" % (self.v5, self.v12, offTime, onTime))
       objPwrCtrl.powerCycle(self.v5, self.v12, offTime, onTime)
       objMsg.printMsg("Cell temperature =%s degC" % str(ReportTemperature()/10 ) )

       if Unlock == 'TCGUnlock':
          if self.UnlockDiag == 'ON':
             objMsg.printMsg('>>>>> TCG Unlocking Diag!')
             ReliUnlockDiagUDE()
             #DirectUnlockDiagUDE()
          if self.UnlockFDE == 'ON':
             objMsg.printMsg('>>>>> FDE Unlocking Diag!')
             from KwaiPrep import CKwaiPrepTest
             oKwaiPrep = CKwaiPrepTest(objDut)
             result = oKwaiPrep.UnlockSerialPort()
             objMsg.printMsg("FDE SerialPort Unlock result=%s" % result)

       self.defaultSetup()
       
       return 0

   #------------------------------------------------------------------------------------------------------#
   def powerCycleVoltageTimer(self, offTime=10, onTime=10, v5=5000, v12=12000, Unlock='NO'):
       """
          Utility Power Cycle with Timer
       """
       
       self.prePowerCycle()
       # DT120511 Bug Fix
       #objMsg.printMsg("PowerOn 5V=%s 12V=%s offTime=%s onTime=%s" % (self.v5, self.v12, offTime, onTime))
       objMsg.printMsg("PowerOn 5V=%s 12V=%s offTime=%s onTime=%s" % (v5, v12, offTime, onTime))
       objPwrCtrl.powerCycle(v5, v12, offTime, onTime)
       objMsg.printMsg("Cell temperature =%s degC" % str(ReportTemperature()/10 ) )

       if Unlock == 'TCGUnlock':
          if self.UnlockDiag == 'ON':
             objMsg.printMsg('>>>>> TCG Unlocking Diag!' )
             ReliUnlockDiagUDE()
             #DirectUnlockDiagUDE()
          if self.UnlockFDE == 'ON':
             objMsg.printMsg('>>>>> FDE Unlocking Diag!')
             from KwaiPrep import CKwaiPrepTest
             oKwaiPrep = CKwaiPrepTest(objDut)
             result = oKwaiPrep.UnlockSerialPort()
             objMsg.printMsg("FDE SerialPort Unlock result=%s" % result)
             


       self.defaultSetup()
       return 0

   #------------------------------------------------------------------------------------------------------#
   def selectDrvTempRamp(self):
       """
          Utility select drive for temp ramp based on serial number
       """

       select = 'NO'

       SNList = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
       objMsg.printMsg('Ramp Temp SN List = %s' %  SNList)
       if self.IDAttr['SerialNumber'][7] in SNList:
          objMsg.printMsg('Serial Number Match Selection, Drive test with temperature ramping.')
          select = 'YES'
       else:
          objMsg.printMsg('Ramp to 22deg with Wait - DriveOff, ReleaseHeater/Fan')      
          select = 'NO'          
       
       return select

   #------------------------------------------------------------------------------------------------------#
   def rampTemp(self, temp, Wait=ON, MaxH=600, UpRate=40, DownRate=10):
       """
          Utility to ramp temperature
       """
       #CheckSlotType()
       SetTemperatureLimits(MaxH, UpRate, DownRate)

      #RT250111: N2 support, N2 no set fan speed
       if not cellTypeString == 'Neptune2': 
          try:
             objMsg.printMsg('Set Cell Fans Speed - 3100, 2927')
             SetCellFans(3100, 2927)
          except:
             objMsg.printMsg('Set Cell Fans Speed not supported')
             pass

       if Wait == ON:
          objMsg.printMsg('Ramp To Temp %d with wait (Cell Temp=%s)' % (temp, str(ReportTemperature()) ))
          RampToTempWithWait(temp*10, 1)                  # temp in tenths of degrees
       else:
          objMsg.printMsg('Ramp To To Temp %d with No wait (Cell Temp=%s)' % (temp, str(ReportTemperature()) ))
          RampToTempNoWait(temp*10, 1)                    # temp in tenths of degrees

# DT 
#       if ConfigVars.has_key('DDCell Max Temp Diff') and ConfigVars['DDCell Max Temp Diff'] > 0:
#          objMsg.printMsg('Releasing Heater Control')
#          ReleaseTheHeater()

      #RT250111: N2 support, use N2 ambient temperature setting
       if not cellTypeString == 'Neptune2': 
          try:    ReleaseTheFans()  # Release Fan control
          except: pass

    
       return 0


   #------------------------------------------------------------------------------------------------------#
   def printTestName(self, msg):
      """
         Utility for display
      """

      #objMsg.printMsg('')
      #objMsg.printMsg('')
      objMsg.printMsg('*'*50)
      objMsg.printMsg('>>>>> %s' % msg)
      objMsg.printMsg('*'*50)

   #------------------------------------------------------------------------------------------------------#
   def defaultSetup(self):
      """
         Utility to default drive test settings
      """

      
      if self.CellType.find('CPC') >= 0 and not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION: # only for intrinsic CPC
         objMsg.printMsg('Default System Setup after Powercycle')
         ICmd.SetIntfTimeout(prm_GIOSettings['IDT IntfTimeout'])
         ICmd.SetSerialTimeout(prm_GIOSettings['IDT SerialTimeout'])
         
         SetBaudRate(Baud38400)
      
         ICmd.ClearBinBuff(BWR)
         ICmd.ClearBinBuff(SBF)
      
         #ICmd.ReceiveSerialCtrl(1)
         #ICmd.SerialNoTimeout('.')
         #objMsg.printMsg('ReceiveSerialCtrl ON and Dot Cmd!') 
         
         
      # DT141211 Add enableAPM
      self.enableAPM('DefaultSetup')
      

   #------------------------------------------------------------------------------------------------------#
   def prePowerCycle(self, PrePower=1):
      """
         Utility to prepare drive 
      """
            
      # DT110211 - bug fix
      # pass
      # RT230311 - skip this for SIC and N2
      #RT090911: use this for every test step, regardless of SI, N2 or CPC
      #if self.CellType.find('CPC') >= 0:
      #RT130911: for SI, check if prepower needs to be done
      if self.CellType.find('SIC') >= 0 and PrePower == 0:
         return

      ICmd.FlushCache()
      ICmd.StandbyImmed()      # DT280710 Added by Julius CT request
      objMsg.printMsg('>>>>> FlushCache and StandbyImmed prior powercycle')      
      
      # DT TEST - PENDING CORETEAM APPROVAL word159 not reporting correctly now
      
#      if self.IDAttr['MediaCache_Enable'] == 'ON':
#         objMsg.printMsg('StandbyImmed and delay 10sec for Media Cache drive')
#         ICmd.StandbyImmed()   # Add for media cache 
#         time.sleep(10)    # Add 10 sec for media cache
#      else:   
#         objMsg.printMsg('IdleImmed and delay 3sec') 
#         ICmd.IdleImmediate()
#         time.sleep(3)    
      
      
   #------------------------------------------------------------------------------------------------------#
   def GIOFAPreDiagnose(self):
       """
          Utility to provide pre diagnosis for FA 
       """
       FAPD = OFF
       self.TestName = 'FAPD'
       self.printTestName(self.TestName) 
       if ConfigVars[CN].has_key('GIO FAPD') and ConfigVars[CN]['GIO FAPD'] != UNDEF and ConfigVars[CN]['GIO FAPD'] == 'ON':
          FAPD = ON

       self.disableAPM(self.TestName)
       
       # NOT COMPLETE
       


   #------------------------------------------------------------------------------------------------------#
   def PrepSerialDiag(self):
       """
          Utility to Prepare Serial Diagnostic dump 
                    
       """ 
       ICmd.ReceiveSerialCtrl(1)
       ICmd.SerialNoTimeout('.')

       objMsg.printMsg('ReceiveSerialCtrl=ON') 
   
   #------------------------------------------------------------------------------------------------------#
   def GetSerialDiag(self):
       """
          Utility to get Serial Diagnostic dump 
          Pre-requisite ReceiveSerialCtrl need to enable store flag
          
       """
       self.printTestName('Get Serial Diagnostic')
       self.disableAPM('GetSerialDiag')
       data=''      # initialize
       result = {'CNT' : -1}
       
       while (result[CNT] != '0'):
          result = ICmd.GetSerialTail(256)
          data += result['DATA']
          objMsg.printMsg('SerialBuffer=%s' %data) 
          
       ICmd.SerialDone()
       ICmd.ClearSerialBuffer()
       objMsg.printMsg('SerialDone and Buffer cleared!')        
       self.enableAPM('GetSerialDiag')

   #------------------------------------------------------------------------------------------------------#
   #RT090911: transform to a generic part number checking utility
   #def checkApplePartNum(self):
   def checkPartNumber(self, func='Generic', partnumlist=[]):
       """
          Utility to Check for Part Number
                    
       """  
    
       CHECK_PN = ON
       PNDetect = 0
       
       #testing
       #DriveAttributes['PART_NUM'] = '9SA092-700'
       #DriveAttributes['PART_NUM'] = '9SA092-262'
       #DriveAttributes['PART_NUM'] = '1AD123-456'

       if CHECK_PN == ON:
          self.TestName = func + ' PartNum Check'
          self.printTestName(self.TestName)

          PNHd = DriveAttributes['PART_NUM'].split('-')[0]
          PNTail = DriveAttributes['PART_NUM'].split('-')[1]
          objMsg.printMsg('>>>>> PartNum=%s [%s]-[%s]' % ( DriveAttributes['PART_NUM'], PNHd, PNTail))

          #RT090911: determine if we check head or check tail of part number
          if (func=='Apple'):
             parttocheck = PNTail
          else:
             parttocheck = PNHd
             
          #PartNumPat = re.compile(r'^(\w{6})-(\w{3})$')
          for cfg in range(len(partnumlist)):
             objMsg.printMsg('>>>>> Checking for %s PartNum signature=%s' % ( func, partnumlist[cfg] ))
             found = parttocheck.find(partnumlist[cfg])
             if found >= 0:
                if (func=='Apple') :
                   DriveAttributes['TEST CFG'] = 'APPLE CFG'
                objMsg.printMsg('>>>>> PartNum=%s matched %s PartNum' % (DriveAttributes['PART_NUM'], func))    
                PNDetect = 1   
                break
                   
       return PNDetect

   #-----------------------------------------------------------------------------------------#
   def appleFirmwareDetect(self):
       """
          Utility to Check Signature of Apple Code in Firmware Package Version
                    
       """ 
       self.TestName = 'Firmware Package Check'
       AppleFWDetect = 0
       PackVer_REGEX = '\s*Package Version:*\s*(?P<PackageVersion>[\.a-zA-Z0-9\-]*)'
       timeout = 20
    
       SetBaudRate(Baud38400)
          
       self.printTestName(self.TestName)              
       #RT140911: SI/N2 do not do prepower cycle
       self.powerCycle('TCGUnlock', 0)
       self.Status = self.disableAPM(self.TestName)
       sptCmds.enableDiags(self.NumRetry)

       try:
          data = sptCmds.execOnlineCmd(CTRL_Z, timeout = timeout, waitLoops = 100)
          objMsg.printMsg('CtrlZ Data=%s' % str(data))  
          
          FWData = sptCmds.sendDiagCmd(CTRL_L, self.SerialTimeoutExt, raiseException=0)
          objMsg.printMsg('CtrlL Data=%s' % str(FWData))
        
       except Exception, e:
          objMsg.printMsg("Serial Port Exception data : %s"%e)
          objMsg.printMsg('%s failed' % self.TestName)
       else:
          objMsg.printMsg('Checking for Signature=%sxx' % self.AppleFWSignature)
          patMatch = re.search(PackVer_REGEX, FWData)

          if patMatch == None:
             objMsg.printMsg('Error in parsing Package Version from CtrlL!')  
          else:
             packVer = patMatch.group('PackageVersion')
             self.PackageVer = packVer
             pat = packVer[23:]
             objMsg.printMsg('Package Version=%s, Pattern=%s' % (self.PackageVer, pat))
             if pat.find(self.AppleFWSignature) >= 0:
                AppleFWDetect = 1
                DriveAttributes['TEST CFG'] = 'APPLE CFG'
                #RT240811: use self.AppleFWSignature
                objMsg.printMsg('>>>>> Drive with Apple firmware code detected, signature=%s, ver=%s' % (self.AppleFWSignature, self.PackageVer)) 
             else:
                objMsg.printMsg('>>>>> Drive with normal firmware detected')  
       
       return AppleFWDetect   

   #-----------------------------------------------------------------------------------------#
   def setAppleConfig(self):
       """
          Utility to Set Test Config
                    
       """ 
       if DriveAttributes['TEST CFG'] == 'APPLE CFG':
          ConfigVars[CN]['RLIST CHECK'] = 'ON'
          ConfigVars[CN]['RLIST LIMIT'] = 0
# Reference:
#         ConfigVars['SMART CHECK IOEDC'] = 'ON'
#         ConfigVars['IOEDC Limit'] = 0
#         ConfigVars['SMART CHECK A198'] = 'ON'
#         ConfigVars['A198 Limit'] = 0
#         ConfigVars['SMART CHECK B410'] = 'ON'
#         ConfigVars['SMART CHECK B412'] = 'ON'
          objMsg.printMsg('>>>>> Apple Test config set!')
      
       return


   #-----------------------------------------------------------------------------------------#
   def setStdConfig(self):
       """
          Utility to Set Std Config
                    
       """ 
       if DriveAttributes['TEST CFG'] != 'APPLE CFG':
          ConfigVars[CN]['RLIST CHECK'] = 'OFF'
          ConfigVars[CN]['RLIST LIMIT'] = 0
          objMsg.printMsg('>>>>> Normal Test Config set! RList check not enforced!')

       return
       
   #-----------------------------------------------------------------------------------------#
   #RT090911: set DVR type drive config
   def setDVRConfig(self, onoff='OFF'):
      ConfigVars[CN]['IDT_DVR_TEST'] = onoff
      
   # start
   #------------------------------------------------------------------------------------------------------#
   def ReadODTVData(self):
       """
          Utility to Read Smart 8F for ODTV Data
                    
       """ 
       self.TestName = 'Read Log 8F for ODTV Data'
       self.printTestName(self.TestName)  
       self.powerCycle()
       data = ICmd.SmartReadLogSec(self.logpage,1)    # 1 sector
       smartData = ICmd.GetBuffer(RBF, 0, 512*1)['DATA']   # RBF get 1 sector  

       return smartData

   #------------------------------------------------------------------------------------------------------#   
   def logODTVFailData(self, errCode, failLBA, failLLRET, failerr):
       """
          Utility to Write ODTV Data to Smart 8F
                    
       """ 
       self.TestName = 'Write Log 8F for ODTV Data'
       self.printTestName(self.TestName)  
        
       ODTVLogString = ("<errorlist><date>%s</date><error>%s</error><lba>%s</lba><llret>%s</llret><ataerr>%s</ataerr><temp>%s</temp></errorlist>" % (time.strftime("%d-%m-%Y %H:%M:%S"), errCode, failLBA, failLLRET, failerr, str(ReportTemperature()/10)))
       pattern = '\x00'
      
       self.powerCycle()

       ICmd.ClearBinBuff(WBF)
       ICmd.ClearBinBuff(RBF)

       data = ICmd.SmartReadLogSec(self.ODTVLogPage, 1)    # 1 sector
       smartData = ICmd.GetBuffer(RBF, 0, 512*1)['DATA']   # RBF get 1 sector  

       if (smartData[0] == pattern):
          ICmd.FillBuffer(WBF, 0, ODTVLogString)
          ICmd.SmartWriteLogSec(self.ODTVLogPage, 1)
          #RT17082010: verify data written in
          data = ICmd.SmartReadLogSec(self.ODTVLogPage, 1)    # 1 sector
          smartData = ICmd.GetBuffer(RBF, 0, 512*1)['DATA']   # RBF get 1 sector  
          objMsg.printMsg('Data written into Smart Page %x: %s' % (self.ODTVLogPage, smartData))
       else:
          objMsg.printMsg('SMARTlog %x not empty. Not writing failure info' % self.ODTVLogPage)
      
       return
   
   #------------------------------------------------------------------------------------------------------#
   def clearODTVFailData(self):
       """
          Utility to Clear Smart 8F
          - Clear Log8F if not null
                    
       """ 
       
       self.TestName = 'Clear Log 8F for ODTV Data'
       self.printTestName(self.TestName)  
       
       pattern = '\x00'
       smartData = self.ReadODTVData()
      
       if (smartData[0] != pattern):
          objMsg.printMsg('SMARTlog %x is not empty' % self.ODTVLogPage)
       
       ICmd.ClearBinBuff(WBF)
       ICmd.SmartWriteLogSec(self.ODTVLogPage, 1)
       objMsg.printMsg('SMARTlog %x cleared!' % self.ODTVLogPage)
      
       return


   #------------------------------------------------------------------------------------------------------#
   def getTTRSpinup(self):
       """
          Utility to extract early TTR from Serial Diagnostic Ctrl-L signon
                    
       """ 
       self.TestName = 'Serial TTR'
       self.SerialTTR = 0     # ms
       
       # sample = 'TTR: 2993 (Spinup = 2183, TCC = 21, RdRsv = 664)'
       
       TTR_REGEX = 'Spinup\s=\s*(?P<EarlyTTR>\d+)'
     
       if self.Status == OK:
    
          SetBaudRate(Baud38400)
          ICmd.SetSerialTimeout(20000)
          
          self.printTestName(self.TestName)              
          self.powerCycle('TCGUnlock')
          self.Status = self.disableAPM(self.TestName)
    
       if self.Status == OK:
          data = ICmd.Ctrl('Z', matchStr='T>')    
          self.Status = data['LLRET']
          objMsg.printMsg('CtrlZ Data=%s' % str(data))  
          
       if self.Status == OK: 
          data = ICmd.Ctrl('L')
          self.Status = data['LLRET']
          objMsg.printMsg('CtrlL Data=%s' % str(data))
        
          FWData = ICmd.GetBuffer(SBF, 0, 1536)['DATA']
          objMsg.printMsg('CtrlL: %s' % FWData)
   
       if self.Status == OK:
          objMsg.printMsg('Checking for Signature=%s' % self.TTRPatt)
          patMatch = re.search(TTR_REGEX, FWData)

          if patMatch == None:
             objMsg.printMsg('Error in parsing TTR Early Spinup from CtrlL! EarlyTTR not supported in Firmware!')  
             # KIV
             #self.Status = FAIL
          else:
             try:
                self.SerialTTR = int(patMatch.group('EarlyTTR'))
             except ValueError:
                self.SerialTTR = 0
             
             if self.SerialTTR:
                objMsg.printMsg('>>>>> Serial TTR Spinup=%4d ms' % self.SerialTTR)
                self.DrvAttr['MQM_TTR_SPINUP'] = self.SerialTTR
                DriveAttributes.update(self.DrvAttr)
             else:
                objMsg.printMsg('>>>>> Error in reading Serial TTR Spinup!')
       
       return 0   

   #------------------------------------------------------------------------------------------------------#
   #RT300311: add method to return CellType to caller
   def getCellType(self):
       return self.CellType

   #------------------------------------------------------------------------------------------------------#
   #RT250511: add method to return PlatformType to caller
   def getPlatformType(self):
       return self.PlatformType
