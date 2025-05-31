#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: The drive object holds the current status of drive, FIS attributes, and drive related methods
#              In HVC environment more than one instance of drive will run per carrier (cell)
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/27 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Drive.py $
# $Revision: #31 $
# $DateTime: 2016/12/27 20:31:10 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Drive.py#31 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
import time, types, traceback, re, os
from DesignPatterns import Null
import ScrCmds
import DbLog, Utility
from DebugDataHandler import debugMessageObject
from Parsers import DbLogParser
from DataSequencer import CDataSequencer
import MessageHandler as objMsg
import Codes, types
try:
   from PIF import DemandTable
except:
   DemandTable = []
from driveStateMarshall import CSaveMarshall

DEBUG = 0

###########################################################################################################
###########################################################################################################
class CDrive(object):
   #------------------------------------------------------------------------------------------------------#
   def __init__(self, port=PortIndex):
      self.birthtime       = time.time()
      self.port            = port
      self.serialnum       = HDASerialNumber
      self.globaldepopMask = []
      self.downsizecapacity = 0
      self.__validateDriveSN() # validate drive serial number before proceeding

      self.driveattr       = {}
      self.OldBG           = "NONE"
      if testSwitch.FE_0131335_220554_NEW_AUD_LODT_FLOW:
         self.ExtraOper       = 0 # ExtraOper = 1 - Run AUD flow. ExtraOper = 2 - Run LODT flow. ExtraOper = 0 - Normal process
      else:
         self.LODT            = 0
      self.IsSDI = False
      self.SkipY2 = False
      self.SkipPCycle = False

   def __getattribute__(self,name):
      return super(CDrive, self).__getattribute__(name)


   def initializeDut(self):
      import PIF
      from Rim import objRimType
      DemandTable = getattr(PIF, 'DemandTable', [])

      # Original Demand Table - Please do not change this variable!
      # DemandTable from PIF.py and self.demand_table variables could be
      # modified in the middle of running script. This Original Demand Table
      # backups the initial DemandTable from PIF.py.
      self.DEMAND_TABLE = DemandTable[:]

      self.objData = CSaveMarshall(self.serialnum, 2)

      self.nextState       = 'INIT'
      self.endState        = ''
      self.lastState       = ''
      self.nextOper        = 'PRE2'
      self.certOper        = True
      self.reconfigOper    = False
      self.currentState    = 'INIT'
      self.resetCustConfigAttr = True
      if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
         self.lastState       = ''
      if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
         self.handleIRecoveryAttr()
         self.initializeIRecoveryDut()
      self.seqNum          = 0
      self.stateData       = {} # state data dict
      self.failureState    = 'NONE'
      self.failState       = ''
      self.failData        = ''
      self.failureData     = ()
      self.failType        = 0  # fail tpye 0: ScriptTestFailure 1: CRaiseException
      self.forceMove       = 0
      self.Status_GOTF     = 1
      self.curTestInfo = {'state': '','param': '', 'occur': '', 'tstSeqEvt': '', 'test': '', 'seq':'', 'stackInfo':'', 'testPriorFail':''}
      self.failTestInfo = {'state': '','param': '', 'occur': 1, 'tstSeqEvt': 1, 'test': '', 'seq':'', 'stackInfo':''}
      self.stateTransitionEvent  = 'procStart' # init to default
      self.powerLossEvent = 0
      self.SpecialPwrLoss = 0
      self.productionFileLimits = None
      self.CCVSampling    = 0
      self.hsc_ht_lst = []
      self.fail_head_TSR = []
      self.fail_head_TSR2 = []
      self.modeloss_avg_info = []
      self.sigmaloss_avg_info = []
      self.skipWRVerify = 0
      self.spmqm_module = 'NONE'
      self.powerLossState = ''

      #For CPC tracking
      self.TrackingList = ''
      self.stateDBLogInfo = {}
      self.stateDBLogInfo[self.currentState] = [] # init with default values otherwise failure before statemachine is instantiated will throw up
      self.numLba = 0
      self.numTrackingZone = 0
      self.BurnishFailedHeads = []
      self.AFH3FailBurnish = 0

      if testSwitch.SKIPZONE:
         self.skipzn = [] #[(0xff, 0xff)]   # head, zon, BER, unver, ver

      self.IDExtraPaddingSize = 0
      if testSwitch.ENABLE_MIN_HEAT_RECOVERY == 1:
         self.MaxIwByAFH = {}
      if testSwitch.ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4 == 1:
         self.TccResetHeadList = []
      self.TccChgByBerHeadList = []
      self.__getChamberType()
      self.__initDriveAttributes() # init drive container attributes with FIS attribute values or ConfigVar values
      self.saveResult      = 0 #Allow or disallow saving results file to the dut

      self.operList = self.__getOperList() # get OperList before isAUDFlow
      self.ExtraOper = self.isAUDFlow()
      if self.ExtraOper == 0:
         self.ExtraOper = self.isLODTFlow()
      self.sbr             = self.driveattr['SUB_BUILD_GROUP']

      self.stateSequence   = {}
      self.stateDependencies = {}
      self.stateRerun      = {}
      self.operList = self.__setDriveState() # determine next oper and state of drive

      self.PSTROper = self.nextOper in getattr(TP,'PSTROperList')

      benchTop_Enable = RequestService('GetSiteconfigSetting','SKDC_BENCHTOP_ENABLE')[1]
      objMsg.printMsg("benchTop_Enable=%s" %benchTop_Enable)
      if type(benchTop_Enable) == types.StringType and benchTop_Enable == 'Error or not supported':
         objMsg.printMsg("***WARNING: RequestService('GetSiteconfigSetting') requires Host RPM 14.2-16 ***")
      elif type(benchTop_Enable) == types.DictType:
         if benchTop_Enable.get('SKDC_BENCHTOP_ENABLE',0) == 1:   # GWA 14x pack, 6x pack, PSTR case
            objMsg.printMsg("Before set BenchTop=%s, hotBenchTop=%s" % (ConfigVars[CN].get('BenchTop', 0), ConfigVars[CN].get('hotBenchTop', 0)))
            ConfigVars[CN]['BenchTop'] = 1
            ConfigVars[CN]['hotBenchTop'] = 1
            objMsg.printMsg("After set BenchTop=%s, hotBenchTop=%s" % (ConfigVars[CN].get('BenchTop', 0), ConfigVars[CN].get('hotBenchTop', 0)))
         elif self.PSTROper and objRimType.IsPSTRRiser():     # GWA gemini, Wuxi equipment case
            objMsg.printMsg("Before set BenchTop=%s, hotBenchTop=%s" % (ConfigVars[CN].get('BenchTop', 0), ConfigVars[CN].get('hotBenchTop', 0)))
            ConfigVars[CN]['BenchTop'] = 1
            ConfigVars[CN]['hotBenchTop'] = 1
            objMsg.printMsg("After set BenchTop=%s, hotBenchTop=%s" % (ConfigVars[CN].get('BenchTop', 0), ConfigVars[CN].get('hotBenchTop', 0)))
      else:
         objMsg.printMsg("can't retrive SKDC_BENCHTOP_ENABLE flag from siteconfig.py")

      if len(DriveAttributes.get('PART_NUM_SEC', '*')) == 10 and not (self.nextOper == 'CCV2' or self.nextOper == 'IDT2') and self.ExtraOper == 0:
         ScrCmds.statMsg("Copy PART_NUM_SEC to PART_NUM")
         DriveAttributes['PART_NUM']      = DriveAttributes.get('PART_NUM_SEC', DriveAttributes['PART_NUM']) 
         DriveAttributes['PART_NUM_SEC']  = '*'
         RequestService("SetPartnum", DriveAttributes['PART_NUM']) #Update Host GUI display
         self.driveattr['PART_NUM']       = DriveAttributes.get('PART_NUM', 'NONE')
         self.driveattr['ORG_PN']         = DriveAttributes.get('PART_NUM', 'NONE')
         self.driveattr['PART_NUM_SEC']   = DriveAttributes.get('PART_NUM_SEC', 'NONE')
         ScrCmds.statMsg("After Update: PART_NUM = %s , PART_NUM_SEC = %s" % (DriveAttributes['PART_NUM'], DriveAttributes['PART_NUM_SEC']))

      if self.nextOper == 'CCV2' and self.driveattr.get('PART_NUM_SEC','NONE') not in ['*', 'NONE', None]: #CCV2 based on Child PN, local PART_NUM is not updated to FIS in CCV2
         self.driveattr['PART_NUM']       = self.driveattr['PART_NUM_SEC']

      if self.nextOper is not 'FNG2':
         self.driveattr['AUD_TEST_DONE']     = 'NONE'
         self.driveattr['IDT_TEST_DONE']     = 'NONE'

      if testSwitch.FE_0151949_345172_P_SEND_ATTR_PRE2_START_FOR_DAILY_TRACKING_YIELD:
         from time import localtime
         year,month,day = localtime()[:3]
         self.startDate = "%02d-%02d%04d"%(month,day,year)
         if self.nextOper == 'PRE2':
            DriveAttributes['PRE2_START'] = self.startDate
         else:
            DriveAttributes['PRE2_START'] = DriveAttributes.get('PRE2_START','NONE')
      if testSwitch.FE_0167431_345172_P_SEND_ATTR_PRE2_BP:
         from time import localtime
         year,month,day = localtime()[:3]
         self.startDate = "%02d-%02d%04d"%(month,day,year)
         if self.nextOper == 'PRE2':
            DriveAttributes['PRE2_BP'] = '%s_%s'%(self.startDate,DriveAttributes.get('HSA_PART_NUM','NONE'))
         else:
            DriveAttributes['PRE2_BP'] = DriveAttributes.get('PRE2_BP','NONE')

      if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
         self.resetIRecoveryDut()

      if testSwitch.WA_0149624_007955_P_ENABLE_RESETWATERFALLATTTRIBUTE_FOR_LCO:
         if testSwitch.BF_0166991_231166_P_USE_PROD_MODE_DEV_PROD_HOSTSITE_FIX:
            if ConfigVars[CN]['PRODUCTION_MODE'] == 0:
               testSwitch.resetWaterfallAttributes = 1
         else:
            if RequestService('GetSiteconfigSetting','CMSHostSite')[1].get('CMSHostSite','NA') in ['LCO']:
               testSwitch.resetWaterfallAttributes = 1

      if testSwitch.FE_0175666_007955_ENABLE_DISABLE_WTF_ATTRS_USING_CONFIGVAR:
         if ConfigVars[CN].get('RESET_WTF_ATTRS', None) == 1:
            testSwitch.resetWaterfallAttributes = 1
         elif ConfigVars[CN].get('RESET_WTF_ATTRS', None) == 0:
            testSwitch.resetWaterfallAttributes = 0

      if not self.powerLossEvent:
         self.__getWTFattributes()    # init waterfall attributes
      
      # Set waterfall attributes
      self.WTF = self.driveattr['WTF']
      self.Waterfall_Req = self.driveattr['WATERFALL_REQ']
      self.Waterfall_Done = self.driveattr['WATERFALL_DONE']
      self.Niblet_Level = self.driveattr['NIBLET_LEVEL']
      self.Drv_Sector_Size = self.driveattr['DRV_SECTOR_SIZE']
      self.Depop_Req = self.driveattr['DEPOP_REQ']
      self.Depop_Done = self.driveattr['DEPOP_DONE']

      #Keep the original attributes to comply with factory PCM reporting
      self.Waterfall_Req_Backup  = self.Waterfall_Req
      self.Depop_Req_Backup      = self.Depop_Req
      self.WTF_EC_Backup         = self.WTF

      self.modelnum        = self.driveattr['MODEL_NUM']
      self.rimType         = DriveAttributes.get('RIM_TYPE','')
      self.mediaPartNum    = self.driveattr['MEDIA_PART_NUM']
      self.programName     = TP.program

      SPC_Criteria = ''
      #Special Criteria by Cell type
      if objRimType.IOInitRiser():
         SPC_Criteria += 'SIC'
      elif objRimType.CPCRiser():
         SPC_Criteria += 'CPC'
      else:
         SPC_Criteria += 'SP'

      #Special Criteria by Prime Rework
      if DriveAttributes.get('PRIME','N') == 'N':
         SPC_Criteria += '_RWK'
      else:
         SPC_Criteria += '_PRIME'

      self.nextOper_BEG += SPC_Criteria
      self.nextOper_CCV += SPC_Criteria

      if ( not testSwitch.FE_0144125_336764_P_GEMINI_CENTRAL_DRIVE_COUNT_SUPPORT ) or \
         ( ( ConfigVars[CN].get('CONFIG_SAMPLE',0) == 0 ) or \
           ( self.chamberType not in ["GEMINI"] and ( self.chamberType in ["HDSTR"] and not ConfigVars[CN].get('Config Monitoring HDSTR Support', 0) ) ) or \
           ConfigVars[CN].get('BenchTop', 0) ):
         if ( self.chamberType in ["HDSTR"] and not ConfigVars[CN].get('Config Monitoring HDSTR Support', 0) ):
            driveCount = ConfigVars[CN].get("Pilot Quantity",100)+1
         else:
            driveCount = 1
      else:
         driveCount = RequestService('AddConfigSample', (CN, str(EditRev), self.driveattr['PART_NUM'] , self.nextOper_BEG) )[1]

      ScrCmds.statMsg("EditRev    - %s" % (EditRev,) )
      ScrCmds.statMsg("AddConfigDrive driveCount - %s" % (driveCount,) )

      if objRimType.IsHDSTRRiser() and (not testSwitch.FE_0158563_345172_HDSTR_SP_PROCESS_ENABLE and not testSwitch.FE_0158386_345172_HDSTR_SP_PRE2_IN_GEMINI):
         ScrCmds.raiseException(11044, "HDSTR SP PROCESS DISABLE Drives should not test on HDSTR Chamber")

      #self.driveattr['CM_IP']                   =  CMIP

      self.driveattr['PILOT_TEST_QTY'] = ConfigVars[CN].get("Pilot Quantity",100)
      self.driveattr['CCV_QTY']        = ConfigVars[CN].get("CCV Quantity",50)

      if driveCount <= int(ConfigVars[CN].get("Pilot Quantity",100)):
         self.driveattr['PILOT_TEST_GROUP']     =  'Y'
      else:
         self.driveattr['PILOT_TEST_GROUP']     =  'N'
      self.driveattr['CCV_GROUP']               =  'N'
      if SPC_Criteria:
         self.driveattr['PILOT_TYPE']              =  SPC_Criteria
         self.driveattr['CCV_TYPE']                =  SPC_Criteria
      else:
         self.driveattr['PILOT_TYPE']              =  'NORMAL'
         self.driveattr['CCV_TYPE']                =  'NORMAL'
      if testSwitch.COMPART_SSO_SCREENING:
         self.driveattr['FREQ_MAX_GAIN']         = int(DriveAttributes.get('FREQ_MAX_GAIN',0))
      self.partNum         = self.__setPartNum()
      self.driveConfigAttrs= {}
      self.drvIntf         = self.getDriveInterface()
      self.evalMode        = ConfigVars[CN].get('EVAL_MODE','OFF')
      self.replugECMatrix  = self.__getReplugECMatrix()
      self.eslipMode       = 0
      self.errCode         = 0
      self.errMsg          = ''
      self.failTest        = ''
      self.failTemp        = ''
      self.failV5          = ''
      self.failV12         = ''
      if not testSwitch.FE_0121886_231166_FULL_SUN_MODEL_NUM:
         self.driveConfigAttrs = None #from GetDriveConfigAttributes
      if testSwitch.FE_0152175_007955_ADD_NUM_PHYS_HDS_TO_DUT_OBJ:
         self.numPhysHds   = TP.Servo_Sn_Prefix_Matrix[self.serialnum[1:3]]['PhysHds']
      self.imaxHead        = TP.numHeads
      self.readyTimeLimit  = None   # set to NONE to trigger TTRLimit checking
      self.maxTrack        = None
      self.maxServoTrack   = None
      chnlType = getattr(TP,'channelType',{self.partNum[0:3]:None})
      self.channelType = chnlType.get(self.partNum[0:3],None)
      self.SOCType         = None
      self.rpm             = None
      self.servoWedges     = None
      self.arcTPI          = None
      if testSwitch.FE_0152175_007955_ADD_NUM_PHYS_HDS_TO_DUT_OBJ:
         self.LgcToPhysHdMap = range(self.numPhysHds)
      else:
         self.LgcToPhysHdMap  = range(self.imaxHead)
      self.PhysToLgcHdMap  = list(self.LgcToPhysHdMap) #Initialize so phys=lgc
      self.HDSTR_RECORD_ACTIVE = 'N'   # DB June 23, 2008
      self.OST             = None
      #self.maxCyl_185 = None
      self.numZones        = 16
      self.numMCZones      = 0
      self.systemZoneNum   = 16
      self.systemAreaUserZones = {} #By head what user zone to use for copy of user zone data to system area
      self.codes           = {}
      self.mdwCalComplete  = self.driveattr['MDW_CAL_STATE']
      self.systemAreaPrepared = int(self.driveattr.get('SYS_AREA_PREPD', 0))
      self.DriveVarsMaster = {}
      self.statesExec = {}
      self.statesSkipped = {}
      oUtil = Utility.CUtility()
      self.demand_table = oUtil.copy(DemandTable)
      self.nextOperOverride = None
      self.restartOnFail = ConfigVars[CN].get('RESTART_ON_FAIL',0)
      self.PREAMP_TYPE = None
      self.PREAMP_MFR  = None
      self.PREAMP_ID   = None
      self.PREAMP_REV  = None

      #HAMR
      if testSwitch.HAMR:
         self.lbcEnabled = False

      if testSwitch.FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION:
         self.dataZonesWithZipperZones = [ [] for hd in range(self.imaxHead)]

      if testSwitch.FE_0273221_348085_P_SUPPORT_MULTIPLE_SF3_OVL_DOWNLOAD:
         try:
            self.registerOvl = self.objData.retrieve('registerOvl')
            ScrCmds.statMsg("registerOvl retrieved=%s" % self.registerOvl)
         except:
            self.registerOvl     = 0

      self.DRV_SECTOR_SIZE = DriveAttributes.get('DRV_SECTOR_SIZE', '4096')
      if '_' in self.DRV_SECTOR_SIZE:
         self.DRV_SECTOR_SIZE = self.DRV_SECTOR_SIZE.split('_')[0]
      if self.DRV_SECTOR_SIZE == 'NONE':
         self.DRV_SECTOR_SIZE = '4096'
      ScrCmds.statMsg("self.DRV_SECTOR_SIZE=%s" % self.DRV_SECTOR_SIZE)
      self.VbarRestarted   = 0
      self.OTFDepop        = 0
      self.VbarDone        = 0   # for depop use
      self.pn_backup       = self.driveattr['PART_NUM']
      if not testSwitch.FE_0131335_220554_NEW_AUD_LODT_FLOW:
         self.LODT          = self.isLODTFlow()
      self.GIO_select_run = 0
      self.HDSTR_UNLOAD_ACTIVE = 'N'
      if self.nextOper != 'PRE2' and self.nextOper != 'FNC2':
         self.OldBG = DriveAttributes.get('BSNS_SEGMENT', "NONE")

      if self.nextOper != 'PRE2':
         self.BG = DriveAttributes.get('BSNS_SEGMENT', "NONE")
      else:
         self.BG = "NONE"

      if self.BG == 'NONE':
         self.BG = ConfigVars[CN].get("Business Group")
      if self.BG == 'NONE':  # if not specified in ConfigVars, use first BG in demand table - knl 16Apr08
         try:
            self.BG = self.demand_table[0]
         except:
            self.BG = None
      self.setDriveCapacity()
      self.downgradeOTF    = 0
      self.downgradeRerun  = []

      self.sptActive       = Null()
      self.appendHDResultsFile = 1

      self.__printInfo() # print out necessary info for user
      self.dblData = DbLog.DbLog(self)
      self.objSeq = CDataSequencer(self)
      self.dblParser = DbLogParser(self)
      self.overlayHandler = None
      self.certOper = self.nextOper in getattr(TP,'CertOperList', ['PRE2', 'CAL2', 'FNC2', 'SDAT2', 'CRT2','SPSC2'])
      #self.reconfigOper = self.nextOper in getattr(TP,'ReconfigOperList', ['CRT2','FIN2','CUT2','FNG2'])
      self.f3Active = 1    #Default 1, as certOper will call sptActive.setMode with determineCodeType = True
      if not (testSwitch.M11P_BRING_UP or testSwitch.M11P):
         self.PSTROper = self.nextOper in getattr(TP,'PSTROperList')

      #Set AAB/Wafer detection via attrs (if supported)
      self.AABType = None
      self.WaferCode = None
      self.HGA_SUPPLIER = None
      self.HSA_WAFER_CODE = None
      self.MediaType = None
      self.IBE3Process = False
      self.UVProcess = False
      self.__set_HSA_PN_attributes()
      self.heaterElementList = []

      if testSwitch.virtualRun == 1:
         self.__loadVirtualXml()

      self.saveToDisc = -1
      if testSwitch.FE_0163083_410674_RETRIEVE_P_VBAR_NIBLET_TABLE_AFTER_POWER_RECOVERY and \
         testSwitch.FE_0164322_410674_RETRIEVE_P_VBAR_TABLE_AFTER_POWER_RECOVERY:
         self.OCC_VBAR_NIBLET = 1
         self.OCC_PWR_PICKER = 1
         self.OCC_PWR_TRIPLETS = 1
         self.vbar_niblet = []
         self.vbar_format_sum = []
         self.vbar_hms_adjust = []
         self.wrt_pwr_picker = []
         self.wrt_pwr_triplets = []
      if testSwitch.FE_0143876_421106_P_HDSTR_OR_GEMINI_PROCESS_WITH_DRIVE_ATTR:
         if self.nextOper == 'PRE2':
            self.HDSTR_PROC = ConfigVars[CN].get("Hdstr Process", 'N')
            ScrCmds.statMsg('Reset the HDSTR_PROC in PRE2')
         elif self.nextOper != 'PRE2' and DriveAttributes.get('ST240_PROC', 'N') != 'N':  #'Y' is drive is designated for HDSTR and 'N' for Gemini and 'C' when HDSTR process is complete
            self.HDSTR_PROC = 'Y'   # HDSTR PROCESS
            ScrCmds.statMsg('HDSTR PROCESS ')
         else:
            self.HDSTR_PROC = 'N'   # Gemini PROCESS
            ScrCmds.statMsg('Gemini PROCESS')

         if self.nextOper == 'PRE2' or self.HDSTR_PROC == 'Y':
            DriveAttributes['ST240_PROC'] = 'N'
            self.driveattr['ST240_PROC'] = 'N'
         else:
            self.driveattr['ST240_PROC'] = DriveAttributes.get('ST240_PROC', 'N')
      else:
         if self.nextOper == 'PRE2' or ConfigVars[CN].get("Hdstr Process",'N') == 'Y':
            DriveAttributes['ST240_PROC'] = 'N'
            self.driveattr['ST240_PROC'] = 'N'
         else:
            self.driveattr['ST240_PROC'] = DriveAttributes.get('ST240_PROC', 'N')

         self.HDSTR_PROC = ConfigVars[CN].get("Hdstr Process", 'N')                #'Y' is drive is designated for HDSTR and 'N' for Gemini and 'C' when HDSTR process is complete

      self.HDSTR_RETEST = 0                                      # Auto re-test in FNC is disabled
      if testSwitch.FE_0158386_345172_HDSTR_SP_PRE2_IN_GEMINI:
         self.HDSTR_SP2_PROC = self.__selectHDSTR_SP()
      else:
         self.HDSTR_SP2_PROC = 'N'
      ScrCmds.statMsg("HDSTR_SP2_PROC =%s"%self.HDSTR_SP2_PROC)
      ScrCmds.statMsg('---------------------------------')
      if objRimType.IsHDSTRRiser():
         self.driveattr['HDSTR_SP_PROC'] = 'Y'
      else:
         self.driveattr['HDSTR_SP_PROC'] = 'N'

      if testSwitch.FE_0124378_391186_HDSTR_CONTROLLED_BY_FILE:
         if not testSwitch.FE_0143876_421106_P_HDSTR_OR_GEMINI_PROCESS_WITH_DRIVE_ATTR and not testSwitch.virtualRun:
            if objRimType.IsHDSTRRiser():
               self.HDSTR_PROC = 'N'
            else:
               self.HDSTR_PROC = self.__selectSt240MK()    # HDSTR to be controlled by part number/SBG instead of package
         else:
            if self.__selectSt240MK() and self.HDSTR_PROC == 'Y':
               self.HDSTR_PROC = 'Y'
            else:
               self.HDSTR_PROC = 'N'
            self.__selectSt240()
      else:
         if testSwitch.FE_0143876_421106_P_HDSTR_OR_GEMINI_PROCESS_WITH_DRIVE_ATTR:
            self.__selectSt240()

      self.HDSTR_IN_GEMINI     = getattr(TP,'hdstrTestFlags',{}).get("Hdstr_In_Gemini",    'N')   #  Default is no HDSTR in Gemini
      self.HDSTR_DELAY_IN_MINS = getattr(TP,'hdstrTestFlags',{}).get("Hdstr_Delay_In_Mins", 1 )   #  Only used if HDSTR_IN_GEMINI is 'Y'
      if testSwitch.FE_0165651_345172_FE_PROC_TEST_FLOW_ATTR_FOR_SEPARATE_FLOW:
         if self.nextOper in ['PRE2','CAL2','FNC2']:
            self.driveattr['PROC_TEST_FLOW'] = self.__TestFlowAtt()
         else:
            self.driveattr['PROC_TEST_FLOW'] = DriveAttributes.get('PROC_TEST_FLOW','GEM')
         ScrCmds.statMsg("driveattr[PROC_TEST_FLOW] = %s"%self.driveattr['PROC_TEST_FLOW'])

      if self.powerLossEvent:

         try:
            '''
            DBLOG Power Loss Recovery support. Example usage:
            splr = str(self.dut.dblData.Tables('P598_ZONE_XFER_RATE'))
            self.dut.objData.update({'DBLOG_PLR': splr})
            '''
            ScrCmds.statMsg("DBLOG_PLR self.dblData=%s" % str(self.dblData))
            splr = '<parametric_dblog>' + self.objData.retrieve('DBLOG_PLR') + '</parametric_dblog>'
            ScrCmds.statMsg("DBLOG_PLR splr=%s" % splr)

            import loadXML
            loadXML.loadGemXML(splr, self.dblData)
         except:
            ScrCmds.statMsg("DBLOG_PLR Traceback: %s" % traceback.format_exc())

         if testSwitch.FE_0180513_007955_COMBINE_CRT2_FIN2_CUT2:
            self.certOper = self.objData.retrieve('certOper')
         ScrCmds.statMsg('Powerloss detect update HDSTR_PROC from latest one')
         self.HDSTR_PROC = self.objData.retrieve('HDSTR_PROC')
         self.HDSTR_UNLOAD_ACTIVE = self.objData.retrieve('HDSTR_UNLOAD_ACTIVE')
         self.HDSTR_RETEST = self.objData.retrieve('HDSTR_RETEST')
         self.CCVSampling = self.objData.retrieve('CCVSampling')
         if testSwitch.FE_0163083_410674_RETRIEVE_P_VBAR_NIBLET_TABLE_AFTER_POWER_RECOVERY:
            self.OCC_VBAR_NIBLET = self.objData.retrieve('OCC_VBAR_NIBLET')
            self.vbar_niblet = self.objData.retrieve('vbar_niblet')
            for rowData in self.vbar_niblet:
               self.dblData.Tables('P_VBAR_NIBLET').addRecord(rowData)

         if testSwitch.FE_0164322_410674_RETRIEVE_P_VBAR_TABLE_AFTER_POWER_RECOVERY:
            self.OCC_PWR_PICKER = self.objData.retrieve('OCC_PWR_PICKER')
            self.OCC_PWR_TRIPLETS = self.objData.retrieve('OCC_PWR_TRIPLETS')
            self.vbar_format_sum = self.objData.retrieve('vbar_format_sum')
            self.vbar_hms_adjust = self.objData.retrieve('vbar_hms_adjust')
            self.wrt_pwr_picker = self.objData.retrieve('wrt_pwr_picker')
            self.wrt_pwr_triplets = self.objData.retrieve('wrt_pwr_triplets')
            try:
               self.spcIdHelper = self.objData.retrieve('spcIdHelper')
            except:
               ScrCmds.statMsg("spcIdHelper not use in %s"%self.nextOper)
               pass
            for row in self.vbar_format_sum:
               self.dblData.Tables('P_VBAR_FORMAT_SUMMARY').addRecord(row)
            for row in self.vbar_hms_adjust:
               self.dblData.Tables('P_VBAR_HMS_ADJUST').addRecord(row)
            for row in self.wrt_pwr_picker:
               self.dblData.Tables('P_WRT_PWR_PICKER').addRecord(row)
            for row in self.wrt_pwr_triplets:
               self.dblData.Tables('P_WRT_PWR_TRIPLETS').addRecord(row)
      ScrCmds.statMsg('--------------------------------')
      ScrCmds.statMsg('Current HDSTR_SP2_PROC = %s' % self.HDSTR_SP2_PROC)
      ScrCmds.statMsg('Current HDSTR_PROC = %s' % self.HDSTR_PROC)
      ScrCmds.statMsg('Current HDSTR_UNLOAD_ACTIVE = %s' % self.HDSTR_UNLOAD_ACTIVE)
      ScrCmds.statMsg('Current HDSTR_RETEST = %s' % self.HDSTR_RETEST)
      ScrCmds.statMsg('--------------------------------')

      self.IdDevice = {}

      try:
         res = self.objData.retrieve('KwaiPrepDone')
         ScrCmds.statMsg("KwaiPrepDone retrieved=%s" % res)
      except:
         self.objData.update({'KwaiPrepDone': 0})

      try:
         self.birthtime = self.objData.retrieve('birthtime')
         ScrCmds.statMsg("birthtime retrieved=%f" % self.birthtime)
      except:
         self.objData.update({'birthtime': self.birthtime})
      try:
         self.rerunReason = self.objData.retrieve('rerunReason')
      except:
         self.rerunReason = ()
      try:
         self.BTC = self.objData.retrieve('BTC')
      except:
         self.BTC = 0
      
      if testSwitch.FE_0121834_231166_PROC_TCG_SUPPORT:
         try:
            res = self.objData.retrieve('TCGPrepDone')
            ScrCmds.statMsg("TCGPrepDone retrieved=%s" % res)
            if self.objData.retrieve('TCGPrepDone') == 1:
               self.driveattr['FDE_DRIVE'] = 'FDE'
         except:
            self.objData.update({'TCGPrepDone': 0})
      if testSwitch.FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM:
         # PLR for CCustomConfig
         try:
            self.CustomCfgTestDone = self.objData.retrieve('CustomCfgTestDone')
            ScrCmds.statMsg("self.CustomCfgTestDone retrieved=%s" % self.CustomCfgTestDone)
         except:
            self.CustomCfgTestDone = []

      self.TCG_locked = False
      self.Servo_Sn_Prefix_Matrix = TP.Servo_Sn_Prefix_Matrix
      self.GotDrvInfo = 0
      self.scanTime = HostItems.get("ScanTime", 0) # scanTime == 0 means not fresh load
      self.manual_gotf = {}
      self.gotfBsnsList = []  # GOTF Business Group list
      self.longattr_bg     = ''
      self.rerunVbar = 0

      if testSwitch.auditTest:
         self.auditTestRAPDict = {}

      self.supprResultsFile = debugMessageObject()
      self.__depopInPartNum()
      self.capacity = getattr(TP,'capacityBySBR',None)
      self.prevOperStatus = {}

      if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
         self.localRestoreSet = []
         self.stateLoopCounter = {}
         #self.baselineRestoreSet = self.loadBaselineRestoreFiles()

      self.baudRate = DEF_BAUD #baud rate of drive
      self.isDriveDualHeater = 0
      self.R2A_BER_TABLE = []
      self.raiseSerialformat = 0

      if testSwitch.FE_0139892_231166_P_SEARCH_FLED_FAIL_PROC:
         self.flashLedSearch_endTest = True
      if testSwitch.FE_0141971_220554_P_ADD_DELTA_BER_ATTRIBUTE:
         self.deltaBER = {}

      self.TCGComplete = False #don't allow more unlocks for this oper

      if testSwitch.FE_0154423_231166_P_ADD_POST_STATE_TEMP_MEASUREMENT:
         try:
            self.stateTemperatureData = self.objData.retrieve('stateTemperatureData')
         except:
            self.stateTemperatureData = {}
            self.objData.update({'stateTemperatureData': {}})

      if testSwitch.FE_0155184_345963_P_DISABLE_ZAP_OFF_AFTER_COMPLETED_ZAP:
         self.zapDone = 0

      if testSwitch.FE_SGP_505235_ENABLE_REZAP_ATTRIBUTE:
         self.rezapAttr = 0 # bit0~7: indicate if re-ZAPed; bit8~15: indicate if requested to force re-ZAP

      if testSwitch.FE_0170519_407749_P_HSA_BP_ENABLE_DELTA_BURNISH_AND_OTF_CHECK and self.nextOper == 'FNC2':
         if DriveAttributes.get('HSA_PART_NUM','NONE') in TP.HSA_PART_NUM_BP.get(self.partNum[6:],[]):
            self.HSA_BP_PN = 1
         else:
            self.HSA_BP_PN = 0

      self.PRE2JumpStateInStatetable = False

      if ConfigVars[CN].get("BODE_SCRN_AUDIT", 0):
         if self.partNum[:6] in TP.Bode_Scrn_Audit['PN']:
            if self.serialnum[-1] in TP.Bode_Scrn_Audit['SN_sampler']:
               testSwitch.RUN_MANTARAY_BODE_SCRN = 0
            else:
               testSwitch.RUN_MANTARAY_BODE_SCRN = 1
      else:
         if self.partNum[:6] in TP.Bode_Scrn_Audit['PN']:
            testSwitch.RUN_MANTARAY_BODE_SCRN = 0

      if ConfigVars[CN].get("FPW", 0) and DriveAttributes.get('HSA_VENDOR','NONE') in TP.HSA_VENDOR_LST:
         testSwitch.RUN_FPW = 1
      if testSwitch.CONDITIONAL_RUN_HMS:
         self.skipHMS = False

      self.oldPN = None    # Part number tracking to optimize DCM call

      DriveAttributes['DRT_MOVECOUNT'] = DriveAttributes.get('DRT_MOVECOUNT', 0) # Dynamic rim type move counter
      self.UPSTests = set()
      self.UPSParmCtrlTestList = [0, 8]
      self.UPSTestTmoutPercent = 0.0 # The percentage of the test timeout. To allow test to output debug data before test times out, typical value is 0.9 and 0 disables feature
      self.parmCode = 0
      self.parmXRef = {}

      if testSwitch.WRITE_SERVO_PATTERN_USING_SCOPY and ConfigVars[CN].get("ENABLE_SHORT_PRE2", 0) and self.nextOper == 'PRE2':
         objMsg.printMsg("Enable short PRE2 test only for Scopy pattern verification")
         self.driveattr['ENABLE_SHORT_PRE2'] = 1
         
      self.FPW_PRIOR_TO_FIN2_LONGDST = 0
      
   if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
      #------------------------------------------------------------------------------------------------------#
      def handleIRecoveryAttr(self):
         attrName  = 'IR_RE_OPER'
         attrName2 = 'IR_HSP_ACTIVE'
         attrName3 = 'IR_REPLUG_STAT'
         attrName4 = 'IR_RUN_CNT'

         if not testSwitch.virtualRun:
            if ConfigVars[CN].get('BenchTop', 0) == 0: #if in real production use RequestService to get more update Attributes
               name, returnedData = RequestService('GetAttributes', (attrName,attrName2,attrName3,attrName4))
               objMsg.printMsg("iRecovery : GetAttributes %s, %s, %s and %s result = name : %s, data : %s" %(attrName,attrName2,attrName3,attrName4,`name`,`returnedData`))
            else:
               name,returnedData    = ('GetAttributes',{attrName: DriveAttributes.get(attrName,'UNKNOWN'),attrName2:DriveAttributes.get(attrName2,'UNKNOWN'),attrName3:DriveAttributes.get(attrName3,'UNKNOWN'),attrName4:DriveAttributes.get(attrName4,'UNKNOWN')})
         else:
            name,returnedData = ('GetAttributes',{attrName: 'UNKNOWN',attrName2:'UNKNOWN',attrName3:'UNKNOWN',attrName4:'UNKNOWN'})

         self.IR_REOPER_VALUE      = returnedData.get(attrName ,'UNKNOWN')
         self.IR_HSP_ACTIVE_VALUE  = returnedData.get(attrName2,'UNKNOWN')
         self.IR_REPLUG_STAT_VALUE = returnedData.get(attrName3,'UNKNOWN')
         self.IR_RUN_CNT_VALUE     = returnedData.get(attrName4,'UNKNOWN')

      #------------------------------------------------------------------------------------------------------#
      def initializeIRecoveryDut(self):
         self.IR_Active          = False
         self.RecoveryStateList  = []

         DriveAttributes['IR_ADG_HOLDING']   = 'NONE'
         DriveAttributes['IR_ADG_DISPOSE']   = 'NONE'

         try:
            self.IR_RUN_CNT = int(self.IR_RUN_CNT_VALUE)
         except:
            self.IR_RUN_CNT = 0

         self.IR_RUN_LIST_startIndex   = int(self.IR_RUN_CNT/iRecovery_RUN_LIST_perAttr)
         self.IR_NAME_LIST_startIndex  = int(self.IR_RUN_CNT/iRecovery_NAME_LIST_perAttr)

         attrName  = 'IR_RUN_LIST_'  + str(self.IR_RUN_LIST_startIndex)
         attrName2 = 'IR_NAME_LIST_' + str(self.IR_NAME_LIST_startIndex) # IR_NAME_LIST use start index same as IR_RUN_LIST
         if not testSwitch.virtualRun:
            if ConfigVars[CN].get('BenchTop', 0) == 0: #if in real production use RequestService to get more update Attributes
               name, returnedData = RequestService('GetAttributes', (attrName,attrName2))
               objMsg.printMsg("iRecovery : GetAttributes %s and %s result = name : %s, data : %s" %(attrName,attrName2,`name`,`returnedData`))
            else:
               name,returnedData    = ('GetAttributes',{attrName: DriveAttributes.get(attrName,'UNKNOWN'),attrName2:DriveAttributes.get(attrName2,'UNKNOWN')})
         else:
            name,returnedData = ('GetAttributes',{attrName: 'UNKNOWN',attrName2:'UNKNOWN'})

         IR_RUN_LIST = returnedData.get(attrName,'UNKNOWN')
         IR_NAME_LIST = returnedData.get(attrName2,'UNKNOWN')

         if IR_RUN_LIST in ['UNKNOWN','NONE','',None,'NEVER']:
            self.PendingMerge2_IR_RUN_LIST = ""
         else:
            self.PendingMerge2_IR_RUN_LIST = IR_RUN_LIST + '/'

         if IR_NAME_LIST in ['UNKNOWN','NONE','',None,'NEVER']:
            self.PendingMerge2_IR_NAME_LIST = ""
         else:
            self.PendingMerge2_IR_NAME_LIST = IR_NAME_LIST + '/'

      #------------------------------------------------------------------------------------------------------#
      def resetIRecoveryDut(self):
         if self.IR_REOPER_VALUE != 'RUNNING' and self.nextOper == 'PRE2' and self.IR_REPLUG_STAT_VALUE != 'WAIT': # Reset iRecovery Attribute
            DriveAttributes['IR_EFFECTIVE']  = 'NONE'
            DriveAttributes['IR_ACTIVE']     = 'N'
            DriveAttributes['IR_STATUS']     = 'NONE'
            DriveAttributes['IR_RE_OPER']    = 'NONE'
            DriveAttributes['IR_RUN_CNT']    = 0
            DriveAttributes['IR_HSP_ACTIVE'] = 'N'
            DriveAttributes['IR_VERSION']    = 'N'

            #Reset IR_RUN_LIST_x
            self.PendingMerge2_IR_NAME_LIST = ""
            self.PendingMerge2_IR_RUN_LIST  = ""
            self.IR_RUN_CNT = 0
            for i in range(self.IR_RUN_LIST_startIndex+1):
               cmd = 'DriveAttributes["IR_RUN_LIST_%s"] = "NONE"' %(i)
               objMsg.printMsg("iRecovery : Reset IR_RUN_LIST...")
               objMsg.printMsg(cmd)
               exec(cmd)
            for i in range(self.IR_NAME_LIST_startIndex+1):
               cmd = 'DriveAttributes["IR_NAME_LIST_%s"] = "NONE"' %(i)
               objMsg.printMsg("iRecovery : Reset IR_NAME_LIST...")
               objMsg.printMsg(cmd)
               exec(cmd)
            self.IR_NAME_LIST_startIndex = 0
            self.IR_RUN_LIST_startIndex  = 0
            DriveAttributes['IR_REPLUG_CNT']  = 0
         if self.IR_REPLUG_STAT_VALUE == 'WAIT':
            DriveAttributes['IR_REPLUG_STAT'] = 'DONE'

      #------------------------------------------------------------------------------------------------------#

   def setup(self):
      """
      Setup the context specific dut variables. Extern dependant flags resolved via
         default code-extern flag resolution should go here as overrides to defaults in initializeDut
      """

      if testSwitch.WA_0149624_007955_P_ENABLE_RESETWATERFALLATTTRIBUTE_FOR_LCO:
         if testSwitch.BF_0166991_231166_P_USE_PROD_MODE_DEV_PROD_HOSTSITE_FIX:
            if ConfigVars[CN]['PRODUCTION_MODE'] == 0:
               testSwitch.resetWaterfallAttributes = 1
         else:
            if RequestService('GetSiteconfigSetting','CMSHostSite')[1].get('CMSHostSite','NA') in ['LCO']:
               testSwitch.resetWaterfallAttributes = 1

      self.__getWTFattributes()    # init waterfall attributes

      # Set waterfall attributes
      self.WTF = self.driveattr['WTF']
      self.Waterfall_Req = self.driveattr['WATERFALL_REQ']
      self.Waterfall_Done = self.driveattr['WATERFALL_DONE']
      self.Niblet_Level = self.driveattr['NIBLET_LEVEL']
      self.Drv_Sector_Size = self.driveattr['DRV_SECTOR_SIZE']
      self.Depop_Req = self.driveattr['DEPOP_REQ']
      self.Depop_Done = self.driveattr['DEPOP_DONE']
      #Set if this is a reprocessed MC drive or not- default not
      self.MCDriveReprocess = testSwitch.Media_Cache

   def controlship(self):
      try:
         import PIF
         PIF.SHIPHOLD_SBR_PREFIX
      except:
         ScrCmds.statMsg("Setting SHIPHOLD_SBR_PREFIX missing in PIF")
         return
      for sbrprefix in PIF.SHIPHOLD_SBR_PREFIX:
         pat = '^'+sbrprefix
         if re.search(pat, DriveAttributes.get('SUB_BUILD_GROUP', '')):
            self.driveattr['NOSHIP'] = 'EONHOLD'
            break


   #------------------------------------------------------------------------------------------------------#
   def __loadVirtualXml(self):
      import loadXML

      ScrCmds.insertHeader("Loading virtual dblog data",length = 40)
      startTime = time.time()

      self.dblData = loadXML.loadDbLogXML(self)    # old method

      try:
         dvData = self.dblData.Tables("P000_DRIVE_VAR_TABLE").tableDataObj()
         for row in dvData:
            addVal = row['VALUE']
            try:
               addVal = float(row['VALUE'])
            except:
               try:
                  addVal = int(row['VALUE'])
               except:
                  addVal = str(row['VALUE'])
            DriveVars[row['DRIVE_VAR']] = addVal
         ScrCmds.statMsg("DriveVars: %s" % str(DriveVars))
      except:
         ScrCmds.statMsg(traceback.format_exc())

         for table in self.dblData.dblTables().keys():
            self.stateDBLogInfo[self.currentState].append(table)

      ScrCmds.statMsg("Load XML Time: %f" % (time.time()-startTime,))
      ScrCmds.statMsg('*' * 80)

   #------------------------------------------------------------------------------------------------------#
   def __printInfo(self):
      ScrCmds.insertHeader("HDA Info",length = 40)
      ScrCmds.statMsg('Printing Info for Drive in Port %d:' % self.port)
      ScrCmds.statMsg('Drive Serial Number: %s' % self.serialnum)
   #------------------------------------------------------------------------------------------------------#
   def getworkfloor(self):
      if len(HOST_ID) == 8 and HOST_ID[0:2] in ['AK','LC','SH','SS','TC','TK','WX','NS','NW']:
         return HOST_ID[2:5]
      elif len(HOST_ID) == 7 and HOST_ID[0] in ['L','R','T','U','X']:
         return HOST_ID[1:4]
      else:
         return "NONE"
   #------------------------------------------------------------------------------------------------------#
   def __initDriveAttributes(self):

      # Now we initialize all drive attributes within the drive container
      # All these attributes must be updated at end of operation
      self.driveattr['CMS_CONFIG']        = CN
      self.driveattr['CMS_VER']           = CV
      if testSwitch.FE_0227432_433430_IDENTIFY_POSSIBLE_WORK_FLOOR_RELATED_ISSUE:
         self.driveattr['WORKFLOOR']      = self.getworkfloor()
      if not ConfigVars[CN].get('BenchTop', 0):
         self.driveattr['EDIT_REV']       = EditRev
         EpocTime                         = int(EditRev)+946659600
      else:
         self.driveattr['EDIT_REV']       = 0
         EpocTime                         = 946659600
      # The attribute below requires new service from Gemini central - removed for SP branch
      self.driveattr['VE_ID']             = 1
      self.driveattr['RISER_TYPE']        = riserType
      if testSwitch.FE_0150975_345963_P_RISER_TYPE_AND_RISER_EXTENSION_ATTRIBUTES:
         if riserExtension == "":
            self.driveattr['RISER_TYPE']  = riserType + '_' + 'NONE'
         else:
            self.driveattr['RISER_TYPE']  = riserType + '_' + riserExtension
      self.driveattr['OPER_INDEX']        = int(DriveAttributes.get('OPER_INDEX',0))
      self.driveattr['NEXT_STATE']        = DriveAttributes.get('NEXT_STATE', 'INIT')
      self.driveattr['FAIL_STATE']        = DriveAttributes.get('FAIL_STATE', 'NONE')
      self.driveattr['FAIL_CODE']         = DriveAttributes.get('FAIL_CODE', 0)
      self.driveattr['TEST_TIME']         = DriveAttributes.get('TEST_TIME', 0)
      self.driveattr['MFG_EVAL']          = DriveAttributes.get('MFG_EVAL', '?')
      self.driveattr['MODEL_NUM']         = DriveAttributes.get('MODEL_NUM', 'NONE')
      self.driveattr['SUB_BUILD_GROUP']   = DriveAttributes.get('SUB_BUILD_GROUP','STD')
      self.driveattr['PART_NUM']          = DriveAttributes.get('PART_NUM', ConfigVars[CN].get('PartNum', partNum))
      self.driveattr['ORG_PN']            = DriveAttributes.get('PART_NUM', ConfigVars[CN].get('PartNum', partNum))
      self.driveattr['MDW_CAL_STATE']     = int(DriveAttributes.get('MDW_CAL_STATE',0))
      self.driveattr['SYS_AREA_PREPD']    = int(DriveAttributes.get('SYS_AREA_PREPD',0))
      self.driveattr['MEDIA_PART_NUM']    = DriveAttributes.get('MEDIA_PART_NUM')
      self.driveattr['PWR_CYC_COUNT']     = int(DriveAttributes.get('PWR_CYC_COUNT', 0))
      self.driveattr['BLUENUNSCAN']       = DriveAttributes.get('BLUENUNSCAN','NONE')
      self.driveattr['WTF_CTRL']          = DriveAttributes.get('WTF_CTRL','NONE') # Track Rerun Process
      self.driveattr['CUST_SCORE']        = DriveAttributes.get('CUST_SCORE', 'NONE')
      self.driveattr['DRIVE_SCORE']       = DriveAttributes.get('DRIVE_SCORE', 'NONE')
      self.driveattr['COMMIT_DONE']       = DriveAttributes.get('COMMIT_DONE', 'NONE')
      self.driveattr['CMT2_TEST_DONE']    = DriveAttributes.get('CMT2_TEST_DONE', 'NONE')
      self.driveattr['GRADING_REV']       = DriveAttributes.get('GRADING_REV', 'NONE')
      self.driveattr['USB_DRIVE']         = DriveAttributes.get('USB_DRIVE', 'NONE')
      self.driveattr['FDE_DRIVE']         = DriveAttributes.get('FDE_DRIVE', 'NONE')
      self.driveattr['GOTF_BEST_SCORE']   = DriveAttributes.get('GOTF_BEST_SCORE', 'NONE')
      self.driveattr['ZERO_G_SENSOR']     = DriveAttributes.get('ZERO_G_SENSOR','NA')
      self.driveattr['FAIL_SAFE']         = DriveAttributes.get('FAIL_SAFE','N')
      self.driveattr['DRAM_PHYS_SIZE']    = int(DriveAttributes.get('DRAM_PHYS_SIZE',0))
      self.driveattr['GOTF_BIN_CTQ']      = DriveAttributes.get('GOTF_BIN_CTQ', 'NONE')
      self.driveattr['GOTF_BIN_BEST']     = DriveAttributes.get('GOTF_BIN_BEST', 'NONE')
      self.driveattr['FNG2_TEST_DONE']    = 'NONE'
      self.driveattr['DNGRADE_ON_FLY']    = DriveAttributes.get('DNGRADE_ON_FLY', 'NONE')
      self.driveattr['PROC_CTRL10']       = DriveAttributes.get('PROC_CTRL10', 'NONE')
      self.driveattr['POTENTIAL_CAUSE']   = 'NONE'
      self.driveattr['CCVTEST']           = 'NONE'
      self.driveattr['IEEE1667_INTF']     = DriveAttributes.get('IEEE1667_INTF', 'NONE')
      self.driveattr['DESTROKE_REQ']      = DriveAttributes.get('DESTROKE_REQ', 'NONE')
      self.driveattr['SOC_TYPE']          = DriveAttributes.get('SOC_TYPE', 0)

      self.driveattr['HOST_ID']           = HOST_ID     #CHOOI-26AUG16

      try:    self.driveattr['CERT_TEMP'] = DriveAttributes['CERT_TEMP']
      except: pass
      self.driveattr['IDT_TEST_METHOD']   = 'NONE'
      if testSwitch.FE_0318342_402984_CHECK_HDA_FW:
         self.driveattr['HDA_FW']         = DriveAttributes.get('HDA_FW', 'NONE')
      if testSwitch.FE_0150074_409401_P_INIT_RETRIEVE_WRITE_SAME_ATTR_WHEN_POWER_LOSS:
         self.driveattr['WRITE_SAME']     = 'NONE'
      if testSwitch.FE_0145983_409401_P_SEND_ATTR_FOR_CONTROL_DRIVE_ERROR:
         self.driveattr['TODT_DEF']       = DriveAttributes.get('TODT_DEF', 'NONE')
      if testSwitch.FE_0131335_220554_NEW_AUD_LODT_FLOW:
         self.driveattr['AUD_TEST_DONE']  = 'NONE'
         self.driveattr['IDT_TEST_DONE']  = 'NONE'
      self.driveattr['RIM_TYPE']          = DriveAttributes.get('RIM_TYPE', 'NONE')
      self.driveattr['NON_DCM_SCREENS']   = 'NONE'          # Attribute to store non-DCM screens
      self.driveattr['SPINDLE_RPM']       = DriveAttributes.get('SPINDLE_RPM', 'NONE')
      self.driveattr['OPTI_ZAP_DONE']     = int(DriveAttributes.get('OPTI_ZAP_DONE', 0))
      if testSwitch.FE_0156784_409401_P_CLEAR_OPTI_ZAP_DONE_ATTR_AT_PRE2 and self.nextOper == 'PRE2':
         self.driveattr['OPTI_ZAP_DONE']  = 0
      if DriveAttributes.has_key('WW_SATA_ID') and len(DriveAttributes['WW_SATA_ID']) == 16:
         self.driveattr['WW_SATA_ID']     = DriveAttributes['WW_SATA_ID']
      if testSwitch.FE_0163145_470833_P_NEPTUNE_SUPPORT_PROC_CTRL20_21:
         self.driveattr['PROC_CTRL20']    = 'NONE'          # Attribute to store cell temp
         self.driveattr['PROC_CTRL21']    = 'NONE'          # Attribute to store drive temp
      try: self.driveattr['PROC_CTRL30']   = "0X%X" % (int(DriveAttributes.get('PROC_CTRL30', '0'),16))
      except: self.driveattr['PROC_CTRL30'] = '0'             # Attribute for special flow drives
      if testSwitch.FE_0365343_518226_SPF_REZAP_BY_HEAD:
         try: self.driveattr['SPF_CUR_HEAD']   = DriveAttributes.get('SPF_CUR_HEAD', 0)
         except: self.driveattr['SPF_CUR_HEAD'] = 0   
      if testSwitch.FE_0359619_518226_REAFH2AFH3_BYHEAD_SCREEN:
         try: self.driveattr['RE_AFH2_HEAD']   = DriveAttributes.get('RE_AFH2_HEAD', '0')
         except: self.driveattr['RE_AFH2_HEAD'] = '0'         
      self.driveattr['PRE2_FINAL_TEMP']   = DriveAttributes.get('PRE2_FINAL_TEMP', 'NONE')
      for intfType in ('WW_SATA_ID', 'WW_SAS_ID', 'WW_FC_ID'):  # Retrieve all valid WWNs from DriveAttributes
         if DriveAttributes.has_key(intfType) and len(DriveAttributes[intfType]) == 16:
            self.driveattr[intfType]      = DriveAttributes[intfType]
      if testSwitch.FE_0170519_407749_P_HSA_BP_ENABLE_DELTA_BURNISH_AND_OTF_CHECK:
         self.driveattr['DOWNGRADE_OTF']  = DriveAttributes.get('DOWNGRADE_OTF', 'NONE')
      self.driveattr['XFER_CAP']          = float(DriveAttributes.get('XFER_CAP', 99))
      self.driveattr['TDCI_COMM_LIFE']    = DriveAttributes.get('TDCI_COMM_LIFE', 0)
      self.driveattr['TD_SID']            = DriveAttributes.get('TD_SID', 'NONE')
      self.driveattr['WPE_UIN']           = DriveAttributes.get('WPE_UIN', '')
      self.driveattr['RFWD_SIGNATURE_1']  = DriveAttributes.get('RFWD_SIGNATURE_1', '')
      self.driveattr['RFWD_SIGNATURE_2']  = DriveAttributes.get('RFWD_SIGNATURE_2', '')
      self.driveattr['RFWD_SIGNATURE_3']  = DriveAttributes.get('RFWD_SIGNATURE_3', '')
      if testSwitch.FE_0368834_505898_P_MARGINAL_SOVA_HEAD_INSTABILITY_SCRN:
         self.driveattr['HMSC_AVG']       = DriveAttributes.get('HMSC_AVG', '')
      if testSwitch.FE_0152905_420281_P_ATTRIBUTE_SEND_FOR_POWER_LOSS_EVENT: # Attribute send for power loss event
         self.driveattr['POWER_LOSS']     = DriveAttributes.get('POWER_LOSS', 'N')
      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         self.driveattr['FN_PN']             = DriveAttributes.get('FN_PN', 'NONE')
         self.driveattr['ORG_TIER']          = DriveAttributes.get('ORG_TIER', 'NONE')

      if testSwitch.PBIC_SUPPORT:
         self.driveattr['FIN2_PBIC_CTRL']   = DriveAttributes.get('FIN2_PBIC_CTRL', 'NONE')

         if testSwitch.PBIC_DATA_COLLECTION_MODE:
            self.driveattr['PBIC_STATUS']   = DriveAttributes.get('PBIC_STATUS', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX0')
         else:
            self.driveattr['PBIC_STATUS']   = DriveAttributes.get('PBIC_STATUS', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX1')
      else:
         self.driveattr['PBIC_STATUS']   = DriveAttributes.get('PBIC_STATUS', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
      self.driveattr['SCOPY_TYPE']        = DriveAttributes.get('SCOPY_TYPE', 'NONE')
      if testSwitch.WRITE_SERVO_PATTERN_USING_SCOPY:
         self.driveattr['ENABLE_SHORT_PRE2'] = 0

      ####################################################
      #Initialize Country of Origin Attribute COO
      country_of_origin_xlate = {
         '3':'SG',
         'Q':'SG',
         '5':'WX',
         'W':'WX',
         '6':'SS',
         'S':'SS',
         '9':'TK',
         '4':'TK',
         'Z':'TK',
         '1':'US',
         'M':'US',
         'P':'US',
         '7':'KR',
         }
      self.driveattr['COO'] = country_of_origin_xlate.get(HDASerialNumber[:1],'NA')
      self.driveattr['QA_CTRL1'] = DriveAttributes.get('QA_CTRL1', 'NONE')
      self.driveattr['QA_CTRL2'] = DriveAttributes.get('QA_CTRL2', 'NONE')
      self.driveattr['QA_CTRL3'] = DriveAttributes.get('QA_CTRL3', 'NONE')
      self.driveattr['QA_CTRL4'] = DriveAttributes.get('QA_CTRL4', 'NONE')
      self.driveattr['QA_CTRL5'] = DriveAttributes.get('QA_CTRL5', 'NONE')
      self.driveattr['DRV_QA_TRK'] = DriveAttributes.get('DRV_QA_TRK', 'NONE')
      if not testSwitch.FE_0131335_220554_NEW_AUD_LODT_FLOW:
         if DriveAttributes.has_key('LODT'):
            self.driveattr['LODT'] = 'NONE'   # Reset LODT to NONE in each operation
      if testSwitch.FE_0189781_357595_HEAD_RECOVERY or testSwitch.ENABLE_THERMAL_SHOCK_RECOVERY_V3:
         self.driveattr['THERM_SHK_RCVRY'] = int(DriveAttributes.get('THERM_SHK_RCVRY', 0))  # TSR attr to indicate which head is baked/shocked
      if testSwitch.ENABLE_THERMAL_SHOCK_RECOVERY_V3:
         self.driveattr['THERM_SHK_RCVRY_V3'] = 0
      # Support 'Remove Drive's Green SBR label' project
      # In C/R will set last character of SBR to "L" for drives that need run LODT after CMT
      # After CMT, will auto key in LODT flow if drive with LODT_FORCE = Y
      pat = r'\w+L$'
      if re.search(pat, DriveAttributes.get('SUB_BUILD_GROUP', ''), re.IGNORECASE):
         self.driveattr['LODT_FORCE'] = 'Y'
      else:
         self.driveattr['LODT_FORCE'] = 'NONE'

      if testSwitch.FE_0334158_379676_P_RFWD_FFV_1_POINT_5:
         DriveAttributes['RFWD_SEVERITY'] = 0

   #------------------------------------------------------------------------------------------------------#
   def __validateDriveSN(self):
      if len(HDASerialNumber) != 8:
         msg = 'Invalid Drive SN Length [%d]!' % len(HDASerialNumber)
         ScrCmds.raiseException(12264)

   #------------------------------------------------------------------------------------------------------#
   def __getOperList(self):
      # Get Oper List first in case of 11044 in AUD flow.
      from StateTable import Operations
      operList = []
      if testSwitch.FE_0120663_347508_ADD_SETOPERLIST_FOR_ST240:
         operList = self.__setOperList()
      else:
         for oper in ConfigVars[CN].get('OperList',Operations):
            if type(oper) == types.ListType:
               operList.extend(oper)
            else:
               operList.append(oper)

         endOper = DriveAttributes.get('END_OPER','')
         if endOper == '' and testSwitch.FE_0124984_357466_ENABLE_END_OPER_PLUGINS:
            endOper = ConfigVars[CN].get('DefEndOper','')

         if endOper in operList:
            operList= operList[:operList.index(endOper)+1]

      ScrCmds.statMsg('Operation list: %s' % operList)
      return operList
   #------------------------------------------------------------------------------------------------------#
   def __setDriveState(self):
      ScrCmds.insertHeader("Initializing Drive State",length = 40)
      from StateTable import StateTable
      # First init next state, next oper and sequence number to default values
      self.failureState = self.nextState # init failure state to next_state to handle script failures

      from StateTable import Operations
      operList = self.operList

      if testSwitch.FE_0143655_345172_P_SPECIAL_SBR_ENABLE:
         ScrCmds.statMsg('BUG RUN_OPER_ON_FAIL Before: %s' % ConfigVars[CN]['RUN_OPER_ON_FAIL'])
         if self.spSBG.sp_SBG:
            if not self.spSBG.spSBGSDAT:
               ScrCmds.statMsg("Special SBR Condition 2 -Disable SDAT.")
               if 'SDAT2' in ConfigVars[CN].get('RUN_OPER_ON_FAIL',[]):
                  ScrCmds.statMsg("Remove SDAT2 oper from ConfigVars[RUN_OPER_ON_FAIL] when Special SBR Condition 2 Disable --> Old ConfigVars[RUN_OPER_ON_FAIL]: %s" %ConfigVars[CN]['RUN_OPER_ON_FAIL'])
                  ConfigVars[CN]['RUN_OPER_ON_FAIL'].remove('SDAT2')
                  ScrCmds.statMsg("ConfigVars[RUN_OPER_ON_FAIL]: %s" %ConfigVars[CN]['RUN_OPER_ON_FAIL'])
               if 'SDAT2' in operList:
                  ScrCmds.statMsg("Remove SDAT2 oper from Operation List when Special SBR Condition 2 Disable --> Old Operation List: %s" %operList)
                  operList.remove('SDAT2')
            else:
               ScrCmds.statMsg("Special SBR Condition 2 -Enable SDAT.")
               if 'SDAT2' not in operList:
                  operList.insert(operList.index('FNC2')+1,'SDAT2')
                  ScrCmds.statMsg("Add SDAT2 oper in operList when Condition 2 Enable ")
               if 'SDAT2' not in ConfigVars[CN].get('RUN_OPER_ON_FAIL',[]):
                  ScrCmds.statMsg("Add SDAT2 oper in ConfigVars[RUN_OPER_ON_FAIL] when Condition 2 Enable --> Old ConfigVar[RUN_OPER_ON_FAIL]: %s" %ConfigVars[CN]['RUN_OPER_ON_FAIL'])
                  ConfigVars[CN]['RUN_OPER_ON_FAIL'].append('SDAT2')

            if self.spSBG.spSBGIDT:
               ScrCmds.statMsg("Special SBR Condition 8 -Enable ODT test (100%).")
               if 'IDT2' not in operList:
                  ScrCmds.statMsg("Add IDT2 oper in Operation List when Special SBR Condition 8 Enable --> Old Operation List: %s" %operList)
                  operList.append('IDT2')
            else:
               ScrCmds.statMsg("Special SBR Condition 8 -Disable ODT test (100%).")
               if 'IDT2' in operList:
                  ScrCmds.statMsg("Remove IDT2 oper from Operation List when Special SBR Condition 8 Disable --> Old Operation List: %s" %operList)
                  operList.remove('IDT2')

         ScrCmds.statMsg('BUG RUN_OPER_ON_FAIL After: %s' % ConfigVars[CN]['RUN_OPER_ON_FAIL'])
      ScrCmds.statMsg('Operation list: %s' % operList)

      if DriveAttributes.get('SET_OPER','') == 'CCV2':
         from StateTable import CCV2Operations
         operList = ConfigVars[CN].get('CCV2OperList',CCV2Operations )
         self.objData.update({'CCV2_operList':operList})
         ScrCmds.statMsg('Operation list changed: %s' % operList)
      self.driveattr['OPER_INDEX'] = int(DriveAttributes.get('OPER_INDEX',0))

      if ConfigVars[CN].get('USE_VALID_OPER',0):
         #AutoDebug updates VALID_OPER via proqual.  Gemini system populates VALID_OPER when loading into Gemini.
         setOper = DriveAttributes.get('VALID_OPER','')
      else:
         setOper = DriveAttributes.get('SET_OPER','')

      discLot = DriveAttributes.get('DISC_1_LOT', '')
      ScrCmds.statMsg('DISC_1_LOT: %s' % (discLot))
      if self.driveattr['SCOPY_TYPE'] != 'NONE':
         ScrCmds.statMsg("Detected SCOPY_TYPE = %s" % (self.driveattr['SCOPY_TYPE']))
      if discLot and (discLot[13:15] in TP.MDSW_DiscLotNum or discLot[0] in TP.MDSW_DiscLotNum):
         media_type = 'MDSW'
         ScrCmds.statMsg("ASSW(MDSW) Media detected.")
      else:
         media_type = 'MDW'
         ScrCmds.statMsg("MDW Media detected.")
         if testSwitch.virtualRun and testSwitch.SCOPY_TARGET:
            media_type = 'MDSW'
            ScrCmds.statMsg("Virtual ASSW(MDSW) Media detected.")

      if DriveAttributes.get('OPERATION_AFT','') == 'MQM2_PENDING' and \
         ((int(ConfigVars[CN].get('SPMQM_ENABLE', 0)) and DriveAttributes.get('AAB', '501.42') not in ['501.42']) or \
         (int(ConfigVars[CN].get('LCT_SPMQM_ENABLE', 0)) and DriveAttributes.get('AAB', '501.42') in ['501.42'])):
         setOper = 'MQM2'
         DriveAttributes['OPERATION_AFT'] = ''
         objMsg.printMsg("MQM2 operation. setOper = %s, OPERATION_AFT = %s" % (setOper, DriveAttributes['OPERATION_AFT']))

      if setOper == 'HDT':
         setOper = 'FNC'
      elif setOper == 'PWA':
         self.driveattr['OPER_INDEX'] = 0
         DriveAttributes['OPER_INDEX'] = 0
         DriveAttributes['SET_OPER'] = '?'
         DriveAttributes['VALID_OPER'] = '?'
      if setOper == 'CAL':
         setOper = 'CAL2'

      if testSwitch.FE_0198600_231166_P_SEND_CMT2_INLINE_EVENT and setOper == 'CMT2':
         objMsg.printMsg("Detected CMT2 restart: Advancing statetable to COMMIT in FIN2")
         self.nextState = 'COMMIT'
         self.resetCustConfigAttr = False
         setOper = 'FIN2'

      if setOper in operList:
         ScrCmds.statMsg("Detected SET_OPER = %s" % (setOper))
         if setOper == 'SCOPY' and media_type == 'MDW':
            setOper =  operList[operList.index(setOper)+1]
            ScrCmds.statMsg("Due to MDW Media, reset SET_OPER = %s" % (setOper))
         if setOper == 'STS' :
            if ConfigVars[CN].get("ENABLE_STS", 0) :
                ScrCmds.statMsg("STS Enable, checking SN for auto sampling")
                if (self.serialnum[-1] in ConfigVars[CN].get("STS_SN", ['%']) or '%' in  ConfigVars[CN].get("STS_SN", ['%'])) :
                    ScrCmds.statMsg("SN matched! Run STS, SET_OPER = %s" % (setOper))
                else:
                    setOper = operList[operList.index(setOper)+1]
                    ScrCmds.statMsg("SN not matched! Skipped STS. SET_OPER = %s" % (setOper))
            else:
                setOper = operList[operList.index(setOper)+1]
                ScrCmds.statMsg("STS not enable, Skipped STS. SET_OPER = %s" % (setOper))
         ScrCmds.statMsg("Setting OPER_INDEX: %s" % (operList.index(setOper)))
         self.driveattr['OPER_INDEX'] = operList.index(setOper)
         DriveAttributes['OPER_INDEX'] = operList.index(setOper)
         DriveAttributes['SET_OPER'] = '?'
         DriveAttributes['VALID_OPER'] = '?'  #Need to clear so OPER_INDEX can control after reset from VALID_OPER or SET_OPER
      else:
         ScrCmds.statMsg('Detected OPER_INDEX = %s' % self.driveattr['OPER_INDEX'])
         if self.driveattr['OPER_INDEX'] >= len(operList):
            ScrCmds.raiseException(11044, 'No operations in list')
         if operList[self.driveattr['OPER_INDEX']] == 'SCOPY' and media_type == 'MDW':
            self.driveattr['OPER_INDEX'] += 1
            DriveAttributes['OPER_INDEX'] = self.driveattr['OPER_INDEX']
            ScrCmds.statMsg('MDW Media detected. Reset OPER_INDEX = %s' % (self.driveattr['OPER_INDEX']))
         if operList[self.driveattr['OPER_INDEX']] == 'STS' :
            if ConfigVars[CN].get("ENABLE_STS", 0) :
                ScrCmds.statMsg("STS Enable, checking SN for auto sampling")
                if (self.serialnum[-1] in ConfigVars[CN].get("STS_SN", ['%']) or '%' in  ConfigVars[CN].get("STS_SN", ['%'])) :
                    ScrCmds.statMsg("SN matched! Run STS, SET_OPER = %s" % (setOper))
                else:
                    self.driveattr['OPER_INDEX'] += 1
                    ScrCmds.statMsg("SN not matched! Skipped STS. SET_OPER = %s" % (setOper))
            else:
                self.driveattr['OPER_INDEX'] += 1
                ScrCmds.statMsg("STS not enable, Skipped STS. SET_OPER = %s" % (setOper))

      self.nextOper = operList[self.driveattr['OPER_INDEX']]
      self.nextOper_BEG = self.nextOper+'_BEG'
      self.nextOper_CCV = self.nextOper+'_CCV'
      self.seqNum    = defInitSeqNum = ConfigVars[CN].get('DefInitSeqNum', 0) # get default value from configvars

      if self.nextOper == 'SCOPY' or (self.nextOper == 'PRE2' and media_type == 'MDW'):
         self.driveattr['SCOPY_TYPE'] = DriveAttributes['SCOPY_TYPE'] = media_type
         ScrCmds.statMsg("Reset SCOPY_TYPE = %s" % (media_type))

      if self.chamberType in ['B2D','SP240']:
         self.nextOper = mirkwoodOperMapping.get(self.nextOper,'ERROR')
      if self.nextOper == 'ERROR':
         ScrCmds.raiseException(11044,'%s operation not valid for chamber %s' % (self.nextOper,self.chamberType))

      if testSwitch.FE_0180513_007955_COMBINE_CRT2_FIN2_CUT2:
         self.certOper = self.nextOper in getattr(TP,'CertOperList', ['PRE2', 'CAL2', 'FNC2', 'SDAT2', 'CRT2','SPSC2', 'FIN2'])
      else:
         self.certOper = self.nextOper in getattr(TP,'CertOperList', ['PRE2', 'CAL2', 'FNC2', 'SDAT2', 'CRT2','SPSC2'])

      if testSwitch.FE_0185387_231166_P_RECONFIGURE_CONFIGVAR:
         self.reconfigOper = int(DriveAttributes.get('RECONFIG', 0)) or ConfigVars[CN].get('RECONFIG', 0)
         if self.reconfigOper:
            self.resetCustConfigAttr = False

         if self.nextOper == 'PRE2':
            self.reconfigOper = False
         elif self.reconfigOper and self.nextOper not in ['FIN2']:
            ScrCmds.raiseException(11043, ' ! Wrong starting operation for RECONFIG -- when RECONFIG is set drive must be started from FIN2')
         if self.reconfigOper:
            self.certOper = False
      else:
         self.reconfigOper = False

      self.endState = ConfigVars[CN].get('DefEndState', {}).get(self.nextOper,'')
      #Format for ConfigVar variable DefEndState {'PRE2':'INIT','FNC2':'INIT','FIN2':'INIT'}
      if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
         if DriveAttributes.get('STOP_STATE','NONE') not in ['?', 'INIT', '', 'NOVALID', 'NONE', 'NA']:
            self.endState  = DriveAttributes['STOP_STATE']
            DriveAttributes['STOP_STATE'] = 'NONE'
      if self.endState not in StateTable.get(self.nextOper,{}).keys():
         self.endState = ''

      if self.nextState != 'COMMIT':
         self.nextState = ConfigVars[CN].get('DefInitState',{}).get(self.nextOper,'INIT') # default init state

      defInitState = self.nextState

      if self.nextState not in StateTable.get(self.nextOper,{}).keys():
         ScrCmds.statMsg('Invalid Init state, restore back to INIT')
         self.nextState = 'INIT'

      # Next we determine the drive's next state and operation
      # try:
         # savedState  = self.objData.retrieve('NEXT_STATE') # this we must get from the drive marshalled/pickled data
         # ScrCmds.statMsg('Drive Marshall Saved State = %s' % savedState)

         # # in case of PLR, sometime it is prefered to rerun from other state instead
         # PwrLossInitState = getattr(TP,"PwrLossInitState",{}).get(self.nextOper,{})
         # if savedState in PwrLossInitState:
            # if savedState == "SPMQM":
               # run_GIOmodules = []
               # for item in getattr(TP,"prm_GIOModules", {}): #Get running prm_GIOmodules
                  # if item[1] == 'ON':
                     # run_GIOmodules.append(item)
               # spmqm_plr = self.objData.get('spmqm_plr', 0)
               # if run_GIOmodules[spmqm_plr][0] == PwrLossInitState.get(savedState,'').get('SPMQM_Module',''):
                  # savedState = PwrLossInitState.get(savedState,'').get('NextState',savedState)
               # del run_GIOmodules
            # else:
               # savedState = PwrLossInitState.get(savedState,'').get('NextState',savedState)
            # ScrCmds.statMsg('Drive Marshall Saved State override by TestParameters (PwrLossInitState) setting = %s' % savedState)
      # except:
         # savedState  = defInitState

      # Next we determine the drive's next sequence number
      # try:
         # savedSeqNum  = self.objData.retrieve('SEQ_NUM') # this we must get from the drive marshalled/pickled data
         # ScrCmds.statMsg('Drive Marshall Saved Seq Num = %d' % savedSeqNum)
      # except:
         # savedSeqNum  = defInitSeqNum # use default

      # Next we reload the stateDbLogInfo for reference if available
      # try:
         # self.stateDBLogInfo = self.objData.retrieve('STATE_DBLOG_INFO')
         # if DEBUG > 0:
            # ScrCmds.statMsg('STATE_DBLOG_INFO retrieved: %s' % self.stateDBLogInfo)
      # except:
         # pass

      #See if there were any pending depop requests prior to PLR
      try:
         self.depopMask = self.objData.retrieve('depopMask')
      except:
         pass

      if testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1:
         try:
            self.BurnishFailedHeads = self.objData.retrieve('BurnishdHeads')
         except:
            self.BurnishFailedHeads = []
      if testSwitch.AGC_SCRN_DESTROKE or testSwitch.AGC_SCRN_DESTROKE_FOR_SBS:
         try:
            self.IDExtraPaddingSize = self.objData.retrieve('IDExtraPaddingSize')
         except:
            self.IDExtraPaddingSize = 0
      if testSwitch.ENABLE_MIN_HEAT_RECOVERY == 1:
         try:
            self.MaxIwByAFH = self.objData.retrieve('MaxIwByAFH')
         except:
            self.MaxIwByAFH = {}
      if testSwitch.ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4 == 1:
         try:
            self.TccResetHeadList = self.objData.retrieve('TccResetHeadList')
         except:
            self.TccResetHeadList = []
      try:
         self.TccChgByBerHeadList = self.objData.retrieve('TccChgByBerHeadList')
      except:
         self.TccChgByBerHeadList = []
      self.recoverProcessData()

      ####################################################
      # NCTC TCC update
      ####################################################

      self.R_THERMAL_CLR_COEF1= []
      self.W_THERMAL_CLR_COEF1= []

      self.NCTC_VALID_TCC = 1

      if testSwitch.PBIC_SUPPORT:
         ####################################################
         # PBIC KPIVs
         ####################################################


         # HD CAL KPIVs --------------------------

         self.MRR_BH= []
         self.CUR_BH= []
         self.BIASCUR_BH= []
         self.FINALGAIN_BH= []

         # MDW /SERVO CAL KPIVs ------------------

         self.RAMP_BH= []
         self.TRK0_BH= []
         self.ECCEN_BH= []
         self.BDFCONS_BH = []
         self.MAXPKPK_BH = []
         self.HDOFFSET_O = []         
         self.HDOFFSET_S = []         

         # AFH KPIVs -----------------------------

         self.RCLR0_BZ= []
         self.RCLR0_BH= []
         self.RCLR1_BZ= []
         self.RCLR1_BH= []
         self.WCLR_BZ= []
         self.WCLR_BH= []
         self.BNSH_BH= []

         # In-situ measurement KPIVs -------------

         self.EWAC_BH= []
         self.WPEN_BH= []
         self.WPEP_BH= []
         self.OW_BH= []
         self.OWQ_BH= []
         self.OW1_BH= []
         self.OWQ1_BH= []
         self.MT10_BH= []
         self.MT50_BH= []
         self.EBN_BH= []
         self.EBP_BH= []

         # VBAR KPIVs ----------------------------

         self.BPIM_BH= []
         self.TPIM_BH= []
         self.BPIM_BZ= []
         self.TPIM_BZ= []
         self.BPIC_BH= []
         self.TPIC_BH= []
         self.BPIC_BZ= []
         self.TPIC_BZ= []
         self.BPICQ_BH= []
         self.TPICQ_BH= []
         self.HMSC_BZ= []
         self.HMSC_BH= []
         self.HMSM_BZ= []
         self.HMSM_BH= []
         self.NetCap = 0.0

         # RRO/NRRO KPIVs ------------------------

         self.RRO_BH= []
         self.NRRO_BH= []
         self.RAWRO_BH= []         
         self.RRO_BZ= []
         self.NRRO_BZ= []
         self.RAWRO_BZ= []
         
         # READ_SCRN T250 KPIVs ------------------

         self.ER_BH= []
         self.ER_BZ= []
         self.ERQ_BH=[]
         self.ER2_BH= []
         self.ER2_BZ= []
         self.ER2Q_BH=[]
         self.SQZER_BH= []
         self.SQZERMax_BH= []
         self.SQZER_BZ= []
         self.SQZERQ_BH=[]

         # Flaw Scan KPIVs -----------------------

         self.REGFLAW_BH= []
         self.VLAW_BH= []
         self.TAFLAW_BH=[]
         self.TOTALTA_BH=[]
         self.VERFW_BH=[]
         self.VERFW_BZ=[]
         self.UNVERFW_BH=[]
         self.UNVERFW_BZ=[]
         ####################################################
         # PBIC KPIVs ends
         ###################################################


      ####################################################
      # Operation summary data
      ####################################################
      self.x_zone_list = []
      self.OTCbackoff = []

      # check if autodiag/process wanted to jump to a specific state other than 'INIT' or unknown state (?)
      # if DriveAttributes.get('NEXT_STATE','INIT') not in ['?', 'INIT']:
         # self.nextState  = DriveAttributes['NEXT_STATE']
         # self.stateTransitionEvent = 'procJumpToState'
         # self.seqNum = defInitSeqNum # start from default for this case
      # else:
         # # determine if this is a power loss situation or if user aborted midway
         # if savedState in [defInitState]: # check if saved state is same as default init state
            # self.seqNum = defInitSeqNum # set seq to default value
         # else:
            # recoveryFlag = ConfigVars[CN].get('StatePwrLossRecovery', 1) # check if power loss recovery is enabled in configvars
            # if recoveryFlag:
               # self.stateTransitionEvent = 'procStatePowerLoss'
               # if self.objData.retrieve('NEXT_OPER') == 'CCV2':
                  # if self.objData.get('CCV2_operList',None) != None: #Fix EC14526 PWL issue CCV2 incorrected oper list after PWL
                     # operList = self.objData.retrieve('CCV2_operList')
                  # else:
                     # from StateTable import CCV2Operations
                     # operList = ConfigVars[CN].get('CCV2OperList',CCV2Operations )
                  # ScrCmds.statMsg('Power lost event detected. Operation list changed: %s' % operList)
               # if ConfigVars[CN].get('PreserveProcFiles', 0) == 1 and testSwitch.GA_0117198_231166_PRESERVE_PCFILES_CONFIGVAR_SUPPORT:
                  # objMsg.printMsg("Detected same-cell restart with PreserveProcFiles.")
                  # self.seqNum = savedSeqNum + 1 # increment savedSeqNum to avoid duplication of SEQ for the same TS
               # elif savedState in ConfigVars[CN].get('Power Loss Restart',['MDW_CAL']) and testSwitch.FE_0132730_336764_RE_WHOLE_PRE2_WHEN_POWER_TRIP_AT_MDW_STATE:
                  # self.nextState = defInitState
                  # self.seqNum = savedSeqNum + 1 # increment savedSeqNum to avoid duplication of SEQ for the same TS
               # elif savedState == 'A_FLAWSCAN' and testSwitch.FE_0147794_345172_A_FLAWSCAN_PWR_LOSS_CHK:
                  # objMsg.printMsg("Power loss issue at A_FLAWSCAN rerun at INIT_FS_TEMP")
                  # self.nextState = 'INIT_FS_TEMP'
                  # self.seqNum = savedSeqNum + 1 # increment savedSeqNum to avoid duplication of SEQ for the same TS
               # else:
                  # self.nextState = savedState
                  # self.seqNum = savedSeqNum + 1 # increment savedSeqNum to avoid duplication of SEQ for the same TS :: start from saved (marshalled) seq number
                  # try:  #failure data may not always exist
                     # self.failureData = self.objData.retrieve('failureData')
                     # self.failTestInfo = self.objData.retrieve('failTestInfo')
                  # except:
                     # ScrCmds.statMsg('PLR:  Failure data does not exist')

               # if savedState == 'FAIL' and testSwitch.FE_0129336_405392_NO_EXCEPTIONAL_PASS_FROM_FAIL_PROC:
                  # savedState = 'FAIL_PROC' # if savedState = FAIL, re-run state FAIL_PROC

               # if savedState in ['COMPLETE', 'FAIL_PROC'] and testSwitch.FE_0129265_405392_SPECIAL_STATES_PLR:
                  # # Determine the drive's next operation
                  # try:
                     # savedOper = self.objData.retrieve('NEXT_OPER') # this we must get from the drive marshalled/pickled data
                     # ScrCmds.statMsg('Drive Marshall Saved Oper = %s' % savedOper)
                  # except:
                     # savedOper = self.nextOper

                  # # Determine the drive's failure state/last state to execute
                  # try:
                     # if savedState == 'COMPLETE':
                        # self.failureState = self.objData.retrieve('failureState')
                     # else:
                        # self.failureState = self.objData.retrieve('failTestInfo')['state']
                     # ScrCmds.statMsg('Drive Marshall Failure State = %s' % self.failureState)
                  # except:
                     # self.failureState = self.nextState # init failure state to next_state to handle script failures

                  # # Recover the failure data
                  # if savedState == 'FAIL_PROC':
                     # try:
                        # self.failureData = self.objData.retrieve('failureData')
                     # except:
                        # pass

                     # try:
                        # self.genExcept = self.objData.retrieve('genExcept')
                     # except:
                        # pass

                  # self.nextState = savedState
                  # self.seqNum = savedSeqNum # start from saved (marshalled) seq number
                  # self.SpecialPwrLoss = 1

      #Check for power loss recovery attributes
      # if self.stateTransitionEvent == 'procStatePowerLoss':
         # self.powerLossState = self.objData.retrieve('NEXT_STATE') # must get from the drive marshalled/pickled data
         # self.powerLossEvent = 1
         # ScrCmds.statMsg('Before PLR, drive.attr OPER_INDEX = %s' % self.driveattr['OPER_INDEX'])
         # ScrCmds.statMsg('Before PLR, drive.attr RIM_TYPE = %s' % self.driveattr['RIM_TYPE'])
         # ScrCmds.statMsg('Before PLR, self.nextOper= %s' % self.nextOper)
         # try:
            # self.driveattr.update(self.objData.retrieve('DriveAttributes'))
         # except KeyError:
            # ScrCmds.statMsg("No valid DriveAttributes found in marshall object.")

         # if testSwitch.FE_0152905_420281_P_ATTRIBUTE_SEND_FOR_POWER_LOSS_EVENT: # Attribute send for power loss event
            # self.driveattr['POWER_LOSS'] = 'Y'+'_'+str(savedState)

         # if 'recur' in self.objData:
            # #decrement the depop restart pointer so we don't count this restart as depop
            # if self.objData['recur'] > 0:
               # self.objData['recur'] -= 1

         # try:  #failure data may not always exist
            # self.TrackingList = self.objData.retrieve('TrackingList')
         # except:
            # ScrCmds.statMsg('PLR:  TrackingList does not exist')

         # try:
            # self.stateSequence = self.objData.retrieve('stateSequence')
            # self.stateSequence[self.nextOper].pop()
         # except:
            # self.stateSequence = {}
         # objMsg.printMsg("stateSequence=%s" %  (self.stateSequence))

         # # Retrieving NEXT_OPER and RIM_TYPE
         # try:
            # savedOper         = self.objData.retrieve('NEXT_OPER') # this we must get from the drive marshalled/pickled data
            # savedOper_Index   = self.driveattr['OPER_INDEX']
            # savedRimType      = self.driveattr['RIM_TYPE']
         # except:
            # #If can not find the NEXT_OPER, RIM_TYPE and OPER_INDEX, it is better to fail the drive as too risky to continue
            # ScrCmds.raiseException(11044, 'PLR error: No valid NEXT_OPER, OPER_INDEX or RIM_TYPE in marshall object')

         # self.nextOper = savedOper
         # DriveAttributes['RIM_TYPE'] = savedRimType       # This rim_type maybe used in other places.

         # # Make sure the drive start test with power loss operation
         # if self.SpecialPwrLoss == 1 and testSwitch.FE_0129265_405392_SPECIAL_STATES_PLR:
            # if savedOper != self.nextOper:
               # ScrCmds.statMsg('Special States PLR: Detected NEXT_OPER = %s setting OPER_INDEX: %s' % (savedOper,operList.index(savedOper)))
               # DriveAttributes['OPER_INDEX'] = self.driveattr['OPER_INDEX'] = operList.index(savedOper)
               # if self.driveattr['OPER_INDEX'] < len(operList):
                  # self.nextOper = operList[self.driveattr['OPER_INDEX']]
               # else:
                  # ScrCmds.raiseException(11044, 'No operations in list')

         # ScrCmds.statMsg('After PLR, drive.attr OPER_INDEX = %s' % self.driveattr['OPER_INDEX'])
         # ScrCmds.statMsg('After PLR, drive.attr RIM_TYPE = %s' % self.driveattr['RIM_TYPE'])
         # ScrCmds.statMsg('After PLR, self.nextOper= %s' % self.nextOper)
      # else:
         # #Reach here when 1) Normal process OR 2) Marshell data unavailable
         # #Host will update FOF_RESTART = 0 for normal process (not recoveryMode)
         # ScrCmds.statMsg('This is either Normal Process (or) CM crush')
         # ScrCmds.statMsg('FOF_RESTART = %s' % int(DriveAttributes['FOF_RESTART']))
         # if int(DriveAttributes['FOF_RESTART']) == 0:
            # DriveAttributes['FOF_RESTART'] = 1
            # ScrCmds.statMsg('Normal Process')
         # else:
            # ScrCmds.statMsg('PLR event from CM Crush')

      ScrCmds.statMsg('Drive Next State = %s' % self.nextState)
      ScrCmds.statMsg('Drive End State = %s' % self.endState)
      ScrCmds.statMsg('Drive Next State Sequence Number = %d' % self.seqNum)
      ScrCmds.statMsg('State Transition Event = %s' % self.stateTransitionEvent)

      return operList
   #----------------------------------------------------------------------------
   def recoverProcessData(self):
      '''Recover data from the marshall object self.dut.objData and put it into the self.dut object
         This will be done in a PLR event or a user-selected restore'''
      self.setProcessData()

   def storeProcessData(self):
      '''Save data in the self.dut object to the from the marshall object self.dut.objData
         This will run after ever state'''
      self.setProcessData(saveToObjData = 1)

   def setProcessData(self, saveToObjData = 0):
      '''Exchange data between the self.dut object and self.dut.objData.'''

      objMsg.printMsg('Setting process data for %d heads' % TP.numHeads)

      #self.dut data that needs to be saved for plr and restore operations.  Key = attributes name and value = default
      #The restore point can be saved in one process and then restored in a new process so....
      #DO NOT PUT CONFIG SPECIFIC ATTRIBUTES IN THIS DICTIONARY LIKE SEQ, SBR, CONFIG, etc.  This will screw up restore operations
      #DO NOT PUT GEMINI HARDWARE SPECIFIC ATTRIBUTES
      processDataToRecover = {
                           'RERUN_VBAR'  : 0,
                           'AFHCleanUp'  : 0,
                           'vbar_wpmeas' : {},
                           'vbar_znmeas' : {},
                           'wrPwrPick'   : {},
                           'vbar_formats': [],
                           'vbar_iterations': 0,
                           'BPIMarginThresholdAdjust' : [0.00] * TP.numHeads,
                           'TPIMarginThresholdAdjust' : [0.00] * TP.numHeads,
                           }

      if testSwitch.PBIC_SUPPORT:
         processDataToRecover['pbic_znkpivs'] = {}

      if testSwitch.FE_0111183_340210_SAT_FAIL_MINIMAL_RETRY:
         processDataToRecover['satFail_HdsZns'] = []

      if testSwitch.FE_0152775_420281_P_DISPLAY_ADC_FOR_ADG_CAPTURE_POOR_HEAD:
         processDataToRecover['avgADC'] = [0.00] * TP.numHeads

      for attribute, default in processDataToRecover.items():
         if saveToObjData:
            #save the self.dut variables to the marshall object.
            self.objData.update({attribute: getattr(self,attribute, default)})
         else:
            #retrieve the variables from the marshall object and update self.dut
            try:
               attrValue = self.objData.retrieve(attribute)
            except:
               attrValue = default

            setattr(self,attribute, attrValue)

   def __setPartNum(self):
      '''Allow user to manual set PART_NUM via Part Num field in Host GUI.
      Set ConfigVar variable LOCAL_PART_NUM = 1'''
      if ConfigVars[CN].get('LOCAL_PART_NUM',0):
         ScrCmds.statMsg('Using Local Part Num: %s' %partNum)
         return partNum
      else:
         return self.driveattr['PART_NUM']



   def getAttrDetectedVals(self, attrName, detectionDict, defaultValue=None):
      import Utility
      oUtil = Utility.CUtility()

      attr = DriveAttributes.get(attrName)
      if not attr in detectionDict:
         if attr == 'AAB':
            objMsg.printMsg("Attributes identified an invalid aabtype.")
         attr = None

      if attr == None:
         #possibly masspro/prepro

         attr = oUtil.lookupValInNestedDict(DriveAttributes , detectionDict)

         if attr == None:
            #If we never got a match
            try:
               #try a configvar override

               #Patch old configs
               if not 'HGA_VENDOR' in ConfigVars[CN] and 'HDTYPE' in ConfigVars[CN]:
                  ConfigVars[CN]['HGA_VENDOR'] = ConfigVars[CN]['HDTYPE']
               if not 'HGA_SUPPLIER' in ConfigVars[CN] and 'HDTYPE' in ConfigVars[CN]:
                  ConfigVars[CN]['HGA_SUPPLIER'] = ConfigVars[CN]['HDTYPE']

               attr = oUtil.lookupValInNestedDict(ConfigVars[CN] , detectionDict)

               # Allow AABTYPE to compensate for other attr/configvar detections
               if attrName == 'AAB' and attr == None:
                  attr = ConfigVars[CN]['AABTYPE']

               # Allow HGA_SUPPLIER to compensate for other attr/configvar detections
               if attrName == 'HGA_SUPPLIER' and attr == None:
                  attr = ConfigVars[CN]['HGA_SUPPLIER']
               # Allow MEDIA_CODE to compensate for other attr/configvar detections
               if attrName == 'MEDIA_CODE' and attr == None:
                  objMsg.printMsg("Cannot find media code attribute")
               if attr == None or attr == '':
                  raise KeyError
            except KeyError:
               if testSwitch.virtualRun:
                  return defaultValue
               if attr == None:
                  ScrCmds.raiseException(11201, "Unable to detect %s through attributes. No detection attributes found in %s for drive." % (attrName,detectionDict.items()))
               else:
                  ScrCmds.raiseException(11043, "Unable to detect %s through attributes or ConfigVar[CN]['%s']" % (attrName,attrName))

      return attr

   def setHGADefaults(self):
      self.HGA_SUPPLIER = ConfigVars[CN].get('HDTYPE', getattr(TP,'DefaultSupplier','RHO'))
      self.preampVendor = ConfigVars[CN].get('PREAMP', getattr(TP,'DefaultPreampVendor','Unknown'))
      self.WaferCode = ConfigVars[CN].get('WAFERCODE', getattr(TP, 'DefaultWaferCode', '__'))

      self.AABType = ConfigVars[CN].get('AABTYPE', None)

      self.HGA_PART_NUM_0 = DriveAttributes.get('HGA_PART_NUM_0', 'UNKNOWN')

   def __set_HSA_PN_attributes(self):

      if testSwitch.FAIL_HSA_PN_INVALID == 0 and testSwitch.USE_HGA_VENDOR_ATTR == 0:
         #abort if the program doesn't need AAB/HGA_VENDOR detection
         self.setHGADefaults()
         self.displayHeadInfo()
         return

      self.setHGADefaults()

      if testSwitch.USE_HGA_VENDOR_ATTR:
         #set hga supplier
         self.HGA_SUPPLIER = self.getAttrDetectedVals('HGA_SUPPLIER', getattr(TP, 'HGA_SUPPLIER_LOOKUP', {}), self.HGA_SUPPLIER)

      if testSwitch.USE_PREAMP_VENDOR_ATTR:
         #set hga supplier
         self.preampVendor = self.getAttrDetectedVals('PREAMP_SUPPLIER', getattr(TP, 'PREAMP_SUPPLIER_LOOKUP', {}), self.preampVendor)
      else:
         ScrCmds.statMsg("Default PREAMP vendor selected. Preamp type will be updated when the actual preamp in use is identified.")

      if testSwitch.AAB_PER_HGA_SUPPLIER:
         self.AABType = TP.AAB_TYPE

      elif testSwitch.USE_HGA_AAB_ATTR:
         self.AABType = DriveAttributes.get('AAB', None)
         ScrCmds.statMsg("AABType from FIS AAB attr is %s" % self.AABType)
         if (self.HGA_SUPPLIER == 'HWY' and self.AABType != None):
            self.AABType = 'H_' + self.AABType
         if (self.HGA_SUPPLIER == 'RHO' and self.AABType not in TP.AAB_RHO):
            self.AABType = ConfigVars[CN].get('AABTYPE_RHO', None)
         if (self.HGA_SUPPLIER == 'TDK' and self.AABType not in TP.AAB_TDK):
            self.AABType = ConfigVars[CN].get('AABTYPE_TDK', None)
         if (self.HGA_SUPPLIER == 'HWY' and self.AABType not in TP.AAB_HWY):
            self.AABType = ConfigVars[CN].get('AABTYPE_HWY', None)
         if self.AABType in ('', None):
            self.AABType = ConfigVars[CN].get('AABTYPE', None)
         if testSwitch.virtualRun:
            self.AABType = getattr(TP,'DefaultAABType',None)

      if (self.HGA_SUPPLIER == 'RHO' and self.AABType not in TP.AAB_RHO) or (self.HGA_SUPPLIER == 'TDK' and self.AABType not in TP.AAB_TDK):
         ScrCmds.raiseException(11044, "AABType <%s> is not supported." % self.AABType)

      if testSwitch.USE_WAFER_CODE_ATTR:
         #Set WaferCode
         self.WaferCode = self.getAttrDetectedVals('MEDIA_CODE', getattr(TP, 'WAFER_CODE_MATRIX', {}), self.WaferCode)

      if testSwitch.USE_HSA_WAFER_CODE_ATTR:
         sn = HDASerialNumber[1:3]
         if sn in TP.staticDepopSerialNum.keys() and TP.staticDepopSerialNum[sn] == 0:
            key = 'HEAD_SN_01'
         else:
            key = 'HEAD_SN_00'
         self.HSA_WAFER_CODE = DriveAttributes.get(key, None)
         ScrCmds.statMsg("%s from FIS attr is %s" % (key, self.HSA_WAFER_CODE))
         if self.HSA_WAFER_CODE != None:
            if self.HGA_SUPPLIER == 'RHO':
               self.HSA_WAFER_CODE = self.HSA_WAFER_CODE[:3] # first 3 char is HSA wafer code for RHO, e.g. NG8HHIDCK0 ==> NG8
            else:
               self.HSA_WAFER_CODE = self.HSA_WAFER_CODE[:5] # first 5 char is HSA wafer code for HWY/TDK, e.g. 4A4C524J79 ==> 4A4C5
         else:
            if self.HGA_SUPPLIER == 'RHO' and self.HSA_WAFER_CODE == None:
               self.HSA_WAFER_CODE = ConfigVars[CN].get('HSA_WAFER_RHO', None) # HSA_WAFER_RHO defined in ConfigVar
            if self.HGA_SUPPLIER == 'HWY' and self.HSA_WAFER_CODE == None:
               self.HSA_WAFER_CODE = ConfigVars[CN].get('HSA_WAFER_HWY', None) # HSA_WAFER_HWY defined in ConfigVar
            if self.HSA_WAFER_CODE == None:
               self.HSA_WAFER_CODE = ConfigVars[CN].get('HSA_WAFER_DEF', None) # HSA_WAFER_DEF defined in ConfigVar
            if self.HSA_WAFER_CODE == None:
               if testSwitch.virtualRun:
                  self.HSA_WAFER_CODE = getattr(TP, 'DefaultHsaWaferCode', None)
               else:
                  ScrCmds.raiseException(11044, "HSA wafer code is not defined in FIS/ConfigVar.") # fail if cannot define HSA_WAFER_CODE properly
      else: # if switch disabled, set hsa wafer code to default
         self.HSA_WAFER_CODE = getattr(TP, 'DefaultHsaWaferCode', None)

      if testSwitch.FE_0317559_305538_P_USE_MEDIA_PART_NUM or testSwitch.FE_0335463_305538_P_USE_MEDIA_PART_NUM_FOR_AFH:
         MediaPartNum = DriveAttributes.get('MEDIA_PART_NUM', None)
         ScrCmds.statMsg("MEDIA_PART_NUM from FIS attr is %s" % MediaPartNum)
         if testSwitch.virtualRun:
            MediaPartNum = getattr(TP, 'DefaultMediaPartNum', None)
         if MediaPartNum == None:
            MediaPartNum = ConfigVars[CN].get('MEDIA_PARTNUM_DEF', None) # MEDIA_PARTNUM_DEF defined in ConfigVar
         if MediaPartNum == None:
            ScrCmds.raiseException(11044, "Media part num is not defined in FIS.") # fail if cannot define MediaType properly
         MediaPartNum = int(MediaPartNum, 10)
         ScrCmds.statMsg("MediaPartNum = %d" % MediaPartNum)

      if testSwitch.FE_0335463_305538_P_USE_MEDIA_PART_NUM_FOR_AFH:
         if MediaPartNum == None:
            ScrCmds.statMsg("Media part num is not defined in FIS.")
         else:
            if MediaPartNum in getattr(TP, 'UV_MediaPartNum', []):
               self.UVProcess = True

      if testSwitch.FE_0317559_305538_P_USE_MEDIA_PART_NUM:
         self.MediaType = self.dictListLookup(getattr(TP, 'MediaType_List', {}), MediaPartNum)
         if self.MediaType == None:
            ScrCmds.raiseException(11044, "Media type is unknown/uncategorized.") # fail if cannot define MediaType properly
      else: # if switch disabled, set media type to default
         MediaPartNum = getattr(TP, 'DefaultMediaPartNum', None)
         if MediaPartNum != None:
            MediaPartNum = int(MediaPartNum, 10)
         self.MediaType = self.dictListLookup(getattr(TP, 'MediaType_List', {}), MediaPartNum)

      if testSwitch.FE_0334752_305538_P_USE_HSA_PART_NUM and self.HGA_SUPPLIER == 'HWY': # only for HWY
         hsaPN = DriveAttributes.get('HSA_PART_NUM', None)
         ScrCmds.statMsg("HSA_PART_NUM from FIS attr is %s" % hsaPN)
         if hsaPN == None:
            ScrCmds.statMsg("HSA part num is not defined in FIS.")
         else:
            hsaPN = int(hsaPN, 10)
            if hsaPN in getattr(TP, 'IBE3_HsaPartNum', []):
               self.IBE3Process = True

      self.displayHeadInfo()

   #----------------------------------------------------------------------------
   def dictListLookup(self, dictObj, value, default = None):
      """
      Lookup key for value in dict items' list - return 1st match or error if default not provided.
      """
      for key,val in dictObj.iteritems():
         if value in val:
            return key
      return default

   #----------------------------------------------------------------------------
   def setDriveCapacity(self):
      '''Seperate drive by capacity and Customer Level.'''

      self.CAPACITY_PN = TP.capacity.get(self.driveattr['PART_NUM'][5], 'NONE')
      # There are 2 special PN,
      # PN -998 in script some times it was recoginze as OEM, NOT STD
      # PN "9WSG4.-...", Test parameter deal in different way, need be careful.
      # Set default value for CAPACITY_CUS.
      if self.BG != None:
         self.CAPACITY_CUS = self.CAPACITY_PN + '_' + self.BG
      else:
         self.CAPACITY_CUS = self.CAPACITY_PN + '_' + 'NONE'
      if self.driveattr['PART_NUM'][-3:] in getattr(TP, 'SPE_PN_LIST', ['998']) or self.driveattr['PART_NUM'] in getattr(TP, 'SPE_PN_LIST', []):
         self.CAPACITY_CUS = self.CAPACITY_PN + '_' + 'OEM1B'

   def displayHeadInfo(self):
      #let the user know what was selected
      ScrCmds.insertHeader('HEAD Vendor Settings')
      ScrCmds.statMsg("HGA Vendor     %s detected." % self.HGA_SUPPLIER)
      ScrCmds.statMsg("PREAMP Vendor  %s detected." % self.preampVendor)
      ScrCmds.statMsg("AABType        %s detected." % self.AABType)
      if testSwitch.USE_WAFER_CODE_ATTR:
         ScrCmds.statMsg("WaferCode      %s detected." % self.WaferCode)
      ScrCmds.statMsg("HSA_WaferCode  %s detected." % self.HSA_WAFER_CODE)
      ScrCmds.statMsg("DiscType       %s detected." % self.driveattr['SCOPY_TYPE'])
      ScrCmds.statMsg("MediaType      %s detected." % self.MediaType)
      ScrCmds.statMsg("IBE3 Process = %s" % self.IBE3Process)
      ScrCmds.statMsg("UV Process   = %s" % self.UVProcess)
      ScrCmds.insertHeader('')

      ###########################
   def __selectSt240(self):

      if testSwitch.FE_0143876_421106_P_HDSTR_OR_GEMINI_PROCESS_WITH_DRIVE_ATTR:
         from StateTable import Operations
         # Determining Process Flow
         ScrCmds.statMsg('Now ST240_PROC is --->> %s' % self.driveattr.get('ST240_PROC','Invalid'))
         if self.driveattr.get('ST240_PROC','N') != 'Y' and self.driveattr.get('ST240_PROC','N') != 'C': #Excludes ST240 unload and beyond
            if self.HDSTR_PROC == 'Y':
               ScrCmds.statMsg('ST240 Process Selected for, change to P')
               self.driveattr['ST240_PROC'] = 'P'
            else:
               ScrCmds.statMsg('Drive did NOT meet any of the ST240 selection criteria,change to N')
               self.driveattr['ST240_PROC'] = 'N'

         elif self.driveattr.get('ST240_PROC','N') == 'Y' or self.driveattr.get('ST240_PROC','N') == 'C':
            ScrCmds.statMsg('ST240 Process Resumption.')

         else:
            ScrCmds.statMsg('This drive is NOT running the ST240 process')
         return Operations

      else:

         from StateTable import Operations
      try:
         from StateTable import Operations_ST240
      except:
         Operations_ST240 = []

      # Determining Process Flow
      ScrCmds.statMsg('Now ST240_PROC is --->> %s' % self.driveattr.get('ST240_PROC','Invalid'))
      if self.driveattr.get('ST240_PROC','N') != 'Y' and self.driveattr.get('ST240_PROC','N') != 'C': #Excludes ST240 unload and beyond
         if ConfigVars[CN].get("Hdstr Process", 'N') == 'Y':
            run_st240 = True
            ScrCmds.statMsg('ST240 Process Selected for')
            self.driveattr['ST240_PROC'] = 'P'
            return Operations_ST240

         else:
            ScrCmds.statMsg('Drive did NOT meet any of the ST240 selection criteria.')
            self.driveattr['ST240_PROC'] = 'N'
            return Operations

      elif self.driveattr.get('ST240_PROC','N') == 'Y' or self.driveattr.get('ST240_PROC','N') == 'C':
         ScrCmds.statMsg('ST240 Process Resumption.')
         return Operations_ST240
      else:
         ScrCmds.statMsg('This drive is NOT running the ST240 process')
         return Operations


   #----------------------------------------------------------------------------
   def __setOperList(self):
      '''Create operation list that can be truncated by DriveAttribute END_OPER.
      This will allow users to indicate ending operation without having to modify
      StateTable.  TCO has a Web App that allows END_OPER to be modified.
      Added section to set operList to ['SDAT2'] to run SDAT(only) if drv fails
      PRE2 after MDW, otherwise set operList via endOper '''
      operList = []
      if self.chamberType in ['B2D','B2D2','SP240','STC']:
         from StateTable import mirkwoodOperations
         for chamberType,operList in mirkwoodOperations.items():
            if nextOper in operList:
               operList = mirkwoodOperations[chamberType]
               break
            else:
               operList = []
               ScrCmds.raiseException(11044, '%s oper not found in operation lists' % self.nextOper)
      else:
         operList = self.__selectSt240()


      if ConfigVars[CN].get('OperList',False):
         if type(ConfigVars[CN].get('OperList',False)) == types.ListType:
            operList = ConfigVars[CN].get('OperList',False)
         else:
            operList = [ConfigVars[CN].get('OperList',False),]
         ScrCmds.statMsg('Operation list changed: %s' % operList)

      endOper = DriveAttributes.get('END_OPER','')
      if endOper == '' and testSwitch.FE_0124984_357466_ENABLE_END_OPER_PLUGINS:
         endOper = ConfigVars[CN].get('DefEndOper','')

      if DriveAttributes.get('SDAT_AFTR_PRE2_F','') == 1:
         operList = ['SDAT2']
         ScrCmds.statMsg('Operation list changed: %s' % operList)

      elif endOper in operList:
         operList = operList[0:operList.index(endOper)+1]
         ScrCmds.statMsg('Operation list changed: %s' % operList)
      else:
         ScrCmds.statMsg('Operation list: %s' % operList)
      return operList

   #------------------------------------------------------------------------------------------------------#
   def getDriveInterface(self):
      '''
      Use DriveAttribute INTERFACE and global variable partNum to determine current
      interface type.  The default interface type is DriveAttribute['INTERFACE'], if user
      wishes to use a modified partNum from desktop partNum field, then set
      UsePartNumInterface = None or assign one of the following valid interface types:
      LC=SCSI
      FC=Fiber channel
      FCV=12v Fibre Channel
      AS=SATA
      NS=? SATA
      SS= SAS
      '''



      if testSwitch.FE_0127531_231166_USE_EXPLICIT_INTF_TYPE:
         interfaceMatrixPneumonic = {
           'LC':   'SCSI',

           'FC':   'FC',
          'FCV':   'FC12V',

          'SATA':  'SATA',
           'AS':   'SATA',
           'NS':   'SATA',

           'SS':   'SAS',
           'SAS':  'SAS',
               }

         #If you want to explicitly want to set an interface type then use the configvar to set the corresponding INTERFACE setup- not the pneumonic
         drvIntf = ConfigVars[CN].get('UsePartNumInterface',None)

         if drvIntf in [None, 'NONE','None','none']:


            #Wasn't specified or default was specified
            drvIntf = DriveAttributes.get('INTERFACE', None)


            if drvIntf == None:
               #Couldn't find a match so attempt PN interface lookup
               #4th character of partnum determines Interface for PSG
               #4th-6th characters of partnum determines Interface for ESG
               partNumInterface = self.partNum[3:6]
               if partNumInterface[0] in ['1','2']:
                  partNumInterface = partNumInterface[0] +'XX'  #XX->ignore cache size and head count for PSG
                  drvIntf = TP.partNumInterfaceMatrix.get(partNumInterface,'NONE')
               else:
                  drvIntf = TP.partNumInterfaceMatrix.get(partNumInterface,'NONE')

            #lets pull in the attributes to determine the pneumonic interface for use in process code
            drvIntf = interfaceMatrixPneumonic.get(drvIntf, None)

         if testSwitch.WA_0124831_231166_FORCE_INTF_TYPE:
            drvIntf = TP.partNumInterfaceMatrix.get('force', drvIntf )

         if drvIntf == None:
            #If we still don't know what the interface type is then fail to prevent incorrect processing
            ScrCmds.raiseException(10179,  "Unable to determine interface type from DriveAttributes or ConfigVars.")



      else:
         drvIntf = ConfigVars[CN].get('UsePartNumInterface',DriveAttributes.get('INTERFACE','NONE'))
         if drvIntf == 'NONE':
            #4th character of partnum determines Interface for PSG
            #4th-6th characters of partnum determines Interface for ESG
            partNumInterface = self.partNum[3:6]
            if partNumInterface[0] in ['1','2']:
               partNumInterface = partNumInterface[0] +'XX'  #XX->ignore cache size and head count for PSG
               drvIntf = TP.partNumInterfaceMatrix.get(partNumInterface,'NONE')
            else:
               drvIntf = TP.partNumInterfaceMatrix.get(partNumInterface,'NONE')

         if testSwitch.WA_0124831_231166_FORCE_INTF_TYPE:
            drvIntf = TP.partNumInterfaceMatrix.get('force', drvIntf )

      ScrCmds.statMsg('Drive Interface: %s' % drvIntf)
      return drvIntf

   #----------------------------------------------------------------------------
   def __getChamberType(self):

      chamberType = RequestService('GetSiteconfigSetting','ChamberType')[1]
      ScrCmds.statMsg("chamberType: %s" % chamberType)
      if type(chamberType) == types.StringType and chamberType  == 'Error or not supported':
         ScrCmds.statMsg("***WARNING: RequestService('GetSiteconfigSetting') requires Host RPM 14.2-16 ***")
      elif type(chamberType) == types.DictType:
         chamberType = chamberType.get('ChamberType','UNKNOWN')
      if chamberType in CHAMBER_TYPES:
         self.chamberType = chamberType
      elif len(HOST_ID) == 8 and HOST_ID[0:2] in ['AK','LC','SH','SS','TC','TK','WX']:
         self.chamberType = 'GEMINI'
      elif len(HOST_ID) == 7:
         if HOST_ID[0] in ['L','R']:
            self.chamberType = 'SP240'
         elif HOST_ID[0] in ['T']:
            self.chamberType = 'STC'
         elif HOST_ID[0] in ['U']:
            self.chamberType = 'B2D'
         elif HOST_ID[0] in ['X']:
            self.chamberType = 'B2D2'
         else:
            self.chamberType = chamberType
            ScrCmds.statMsg(HOST_ID_MSG)
      #elif len(HOST_ID) == 5:
      #   if HOST_ID[0:3] in ['NEP']:
      #      self.chamberType = 'NEPTUNE'
      else:
         self.chamberType = 'MANUAL'
         ScrCmds.statMsg("Add ChamberType (%s) to /var/merlin/host/siteconfig.py" % CHAMBER_TYPES)
      ScrCmds.statMsg("chamberType: %s" % self.chamberType)

      if self.chamberType in ['B2D','SP240','MANUAL']:
         DriveAttributes['3TempMove_ENABLE'] = 0   #Disable Dynamic Rim Type if not in Gemini Chamber
         ReportRestartFlags({'holdDrive':0})       #Turn off holdDrive feature since only needed on GEMINI chambers

   #----------------------------------------------------------------------------
   def __getReplugECMatrix(self):
      replugMatrix = getattr(TP,'replugECMatrix',{})
      if ConfigVars[CN].get('ReplugECMatrix',{}) != {}:
         replugMatrix.update(ConfigVars[CN]['ReplugECMatrix'])
      ScrCmds.statMsg('%s %s' % ('replugECMatrix',replugMatrix))
      return replugMatrix

   def __getWTFYTM(self):
      self.WTFYTM = 0
      self.PN_TEMP  = self.driveattr['PART_NUM']
      if (self.Waterfall_Req[0] == 'R' or self.Depop_Req[0] == 'D') :
         self.WTFYTM = 1
      ScrCmds.statMsg("WTFYTM:%s CurrentPN:%s"%(self.WTFYTM,self.PN_TEMP))

   def __getWTFattributes(self):
      """
      Reset waterfall attributes. Factory wants to keep attributes to save test time.
      """

      if testSwitch.resetWaterfallAttributes \
       and (int(DriveAttributes.get('DR_REPLUG_CNT',0)) == 0)\
       and not ('recur' in self.objData )\
       and self.nextOper == 'PRE2':
         self.driveattr['WTF']               = 'NONE'
         self.driveattr['WATERFALL_REQ']     = 'NONE'
         self.driveattr['WATERFALL_DONE']    = 'NONE'
         self.driveattr['NIBLET_LEVEL']      = 'NONE'
         self.driveattr['DRV_SECTOR_SIZE']   = 'NONE'
         self.driveattr['DEPOP_REQ']         = 'NONE'
         self.driveattr['DEPOP_DONE']        = 'NONE'
         self.driveattr['DEPOP_OTF']         = 'NONE'
      else:
         self.driveattr['WTF']               = DriveAttributes.get('WTF', 'NONE')
         self.driveattr['WATERFALL_REQ']     = DriveAttributes.get('WATERFALL_REQ', 'NONE')
         self.driveattr['WATERFALL_DONE']    = DriveAttributes.get('WATERFALL_DONE', 'NONE')
         self.driveattr['NIBLET_LEVEL']      = DriveAttributes.get('NIBLET_LEVEL', 'NONE')
         self.driveattr['DRV_SECTOR_SIZE']   = DriveAttributes.get('DRV_SECTOR_SIZE', 'NONE')
         # RW7 Common Part Number for 1TB Support
         self.driveattr['DEPOP_REQ']         = DriveAttributes.get('DEPOP_REQ', 'NONE')
         self.driveattr['DEPOP_DONE']        = DriveAttributes.get('DEPOP_DONE', 'NONE')
         self.driveattr['DEPOP_OTF']         = DriveAttributes.get('DEPOP_OTF', 'NONE')

      if self.nextOper in ['SCOPY', 'PRE2', 'STS']:
         sn = HDASerialNumber[1:3]
         if sn in TP.staticDepopSerialNum.keys():
            self.driveattr['DEPOP_REQ'] = 'D'+str(TP.staticDepopSerialNum[sn])
      self.BTC = HDASerialNumber[1:3] in TP.staticDepopSerialNum.keys()
      self.objData.update({'BTC': self.BTC})
         
      if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
         if ConfigVars[CN].get('DEPOP_HEADS', 'NATIVE') != 'NATIVE':
            self.driveattr['DEPOP_REQ']       =  ConfigVars[CN].get('DEPOP_HEADS', 'NONE')
            self.driveattr['WATERFALL_REQ']   =  ConfigVars[CN].get('WATERFALL_REQ', 'NONE')

      if testSwitch.M11P_BRING_UP:
         if ConfigVars[CN].get('DEPOP_HEADS', 'NATIVE') != 'NATIVE':
            self.driveattr['DEPOP_REQ']       =  ConfigVars[CN].get('DEPOP_HEADS', 'NONE')
            self.driveattr['WATERFALL_REQ']   =  ConfigVars[CN].get('WATERFALL_REQ', 'NONE')
            
      #set up depop Mask
      if not getattr(self, 'depopMask', []):                                  # Local variable from state or PLR overrides TP
         if testSwitch.FE_0169486_357260_P_DEPOP_REQ_OVERRIDES_DEPOP_MASK and getattr(TP,'depopMask',[]) and self.driveattr['DEPOP_REQ'] != 'NONE':
            self.depopMask = getattr(TP,'depopRequired',[])                   # DEPOP_REQ trumps TP.depopMask, unless depopRequired exists.
         else:
            self.depopMask = getattr(TP,'depopMask',[])                       # Else, just use TP.depopmask if available

      if self.driveattr['DEPOP_REQ'] != 'NONE':
         for hd in map(int, self.driveattr['DEPOP_REQ'][1:].split(',')):    # E.g. 'D1,2,3'
            if hd not in self.depopMask:
               self.depopMask.append(hd)


   def updateDepop_Req(self):
      """
       Keep Depop_Req variable in sync with self.dut.depopMask
       """
      if self.depopMask:
         depop_req = 'D' + ','.join(map(str, self.depopMask))
         self.driveattr['DEPOP_REQ'] = depop_req
         self.Depop_Req = depop_req

   #----------------------------------------------------------------------------
   def updateFISAttr(self):
      #Save off current state of dut variables to attrs if necessary
      if getattr(self, 'systemAreaPrepared',  None) != None:
         self.driveattr['SYS_AREA_PREPD'] = self.systemAreaPrepared


      oUtil = Utility.CUtility()

      if self.nextOper == 'CMT2':
         tmpattr = {'TEST_TIME': '', 'CMT2_TEST_DONE': '', 'FAIL_STATE': 'NONE', 'OPER_INDEX': 0, 'FAIL_CODE': '0', 'PWR_CYC_COUNT': 0, 'NEXT_STATE': 'INIT', 'POWER_ON_TYPE': 'NA'}
      elif self.nextOper == 'AUD2':
         tmpattr = {'TEST_TIME': '', 'AUD2_TEST_DONE': '', 'FAIL_STATE': 'NONE', 'OPER_INDEX': 0, 'FAIL_CODE': '0', 'PWR_CYC_COUNT': 0, 'NEXT_STATE': 'INIT'}

      if self.nextOper in ['CMT2','AUD2'] and testSwitch.FE_0120918_347508_ATTRIBUTE_LOADING_REDUCTION and not testSwitch.virtualRun:
         #for quick audit and FIS update states lets send a subset of attributes- this breaks VE so don't do this for ve
         for key,val in tmpattr.items():
            tmpattr[key] = self.driveattr.get(key, '?')
         self.driveattr = tmpattr
         ScrCmds.statMsg(str(self.driveattr))

      # update long attributes
      dict = {}
      try:
         if self.longattr_bg != "":
            from StateMachine import CLongAttr
            dict = CLongAttr().EncodeAttr(self.longattr_bg)
      except:
         pass
      self.driveattr.update(dict)

      if type(self.driveattr.get('CUST_TESTNAME','')) == types.ListType:
         outVar = []
         for testName in self.driveattr['CUST_TESTNAME']:
            outVar.append(testName)
            outVar.append('and')

         del outVar[-1] #remove last 'and'
         self.driveattr['CUST_TESTNAME'] = ' '.join(map(str,outVar))


      import MessageHandler as objMsg

      for key,val in self.driveattr.items():
         if val in ['', None]:
            val ='?'
         self.driveattr[key] = objMsg.cleanASCII(str(val))

      #Remove certain attributes from sending to FIS
      if self.nextOper == "CCV2":
         objMsg.printMsg("For CCV2 operation, update necessary attributes only")
         from base_CCV import CCCV_main
         tmp_dict = CCCV_main(self, self).trim_CCV2Attr()
         DriveAttributes.update(tmp_dict) # update all drive attributes in one go
      else:
         oUtil.safeDictDelete(['MODEL_NUM',],self.driveattr)
         DriveAttributes.update(self.driveattr) # update all drive attributes in one go


   def setMyParser(self, useCMLogic = 0):
      # Inline dblog parser
      RegisterResultsCallback(self.dblParser.parseHeader,[2,3],useCMLogic)

   #----------------------------------------------------------------------------
   def __depopInPartNum(self):
      """Set the part number based on the CN['numHeads'] attribute:
      0 = use existing
      1+ = set the numHeads digit to this number, set previous digit so that we can tell what it used to be
      -1 = return the partnum to its original state
      """
      if testSwitch.buildCustomFW:
         numHeads = ConfigVars[CN].get('numHeads',0)
         key = {'0':'2', '1':'4', '2':'6', '3':'8'} # an encoding of partNum[4] to head num
         Modified = False
         partNumber = self.partNum
         if numHeads != 0:
            if numHeads == -1:
               if self.partNum[4]!='4': # if the drive has been depopped
                  self.partNum=self.partNum[:4] + '4' + key[self.partNum[4]] + self.partNum[6:]
                  Modified = True
            else:
               if self.partNum[4]=='4': # make sure that the cache digit is what we expect
                  if int(self.partNum[5]) > numHeads: # make sure that we depopping to a lower head count
                     key = dict([(v, k) for k, v in key.iteritems()]) # invert key
                     self.partNum=self.partNum[:4] + key[self.partNum[5]] + str(numHeads) + self.partNum[6:] # 'borrow' cache digit to save numHeads
                     Modified = True
         self.imaxHead=int(self.partNum[5])
         if Modified:
            ScrCmds.insertHeader('Depop Drive',length = 40)
            objMsg.printMsg('Part number changed: %s to %s' % ( partNumber,self.partNum))
            self.driveattr['PART_NUM']=self.partNum
            DriveAttributes['PART_NUM']=self.partNum

   #------------------------------------------------------------------------------------------------------#
   def isLODTFlow(self):
      """
      Process need to tag attribute SET_OPER = IDT2 and give refin2 rework code.
      Drive with FAIL_CODE = 0, SET_OPER = IDT2, AUD_TEST_DONE = PASS must skip all the tests and go into CST2 package.
      """
      from Rim import objRimType

      if ConfigVars[CN].get('AUD_ENABLE', 0):                          #Check the last oper before CST2
         LastOperState = DriveAttributes.get('AUD_TEST_DONE', '')
      else:
         if self.operList[-1] == 'IDT2':
            LastOperState = DriveAttributes.get('%s_TEST_DONE'%self.operList[-2], 'NONE')
         else:
            LastOperState = DriveAttributes.get('%s_TEST_DONE'%self.operList[-1], 'NONE')

      #For no IO process, drive will replug if need run GIO test in last operation
      if ConfigVars[CN].get('USE_VALID_OPER',0):
         setOper = DriveAttributes.get('VALID_OPER','')
      else:
         setOper = DriveAttributes.get('SET_OPER','')

      if setOper not in self.operList:
         try:
            setOper = self.operList[int(DriveAttributes.get('OPER_INDEX',0))]
         except:
            setOper = ''

      if DriveAttributes.get('SET_OPER','') != "CCV2" and ConfigVars[CN].get('LODT_ENABLE', 0) and int(DriveAttributes.get('FAIL_CODE', 0)) == 0 and \
         LastOperState == 'PASS' and \
         (objRimType.CPCRiser(ReportReal = True) or objRimType.IOInitRiser()) and \
         (DriveAttributes.get('SET_OPER', '') == 'IDT2' or DriveAttributes.get('VALID_OPER', '') == 'IDT2' or \
         (self.powerLossEvent and self.objData.retrieve('NEXT_OPER') in ['IDT2']) or \
         DriveAttributes.get('IDT_TEST_DONE', 'NONE') == 'PENDING' or DriveAttributes.get('GIO_TEST_DONE', 'NONE') == 'PENDING' or \
         setOper == 'IDT2'):
         self.objData.update({'NEXT_OPER':'IDT2'})
         return 2
      else:
         return 0

   #------------------------------------------------------------------------------------------------------#
   def isAUDFlow(self):
      """After CMT pass. Drive will be re-inserted into Gemini automatically and retest.
      (Process change route table to allow that)
      if need to rerun AUD, Process need to tag attribute SET_OPER = IDT2 and give refin2 rework code
      """
      from Rim import objRimType

      if DriveAttributes.get('SET_OPER','') != "CCV2" and ConfigVars[CN].get('AUD_ENABLE', 0) and int(DriveAttributes.get('FAIL_CODE', 0)) == 0 and \
         (DriveAttributes.get('VALID_OPER', '') in ['AUD'] or DriveAttributes.get('SET_OPER', '') in ['AUD']) and \
         objRimType.CPCRiser(ReportReal = True):
         if self.operList[-1] == 'IDT2' and DriveAttributes.get('%s_TEST_DONE'%self.operList[-2], 'NONE') == 'PASS':
            return 1
         elif DriveAttributes.get('%s_TEST_DONE'%self.operList[-1], 'NONE') == 'PASS':
            return 1
         else:
            return 0
      else:
         return 0
   #----------------------------------------------------------------------------
   def isSupposedToRunGIO(self):
      """
      Function evaluates if this drive is targeted for GIO (ODT/IDT)
      2 = FORCED
      1 = SELECT
      """
      restartIDT = 0
      if ConfigVars[CN].has_key('GIO_Selection') and ConfigVars[CN]['GIO_Selection'] != 'OFF':
         ConfigVars[CN]['GIO_EvalName'] = ConfigVars[CN].get('GIO_EvalName','GIO_TEST')
         ScrCmds.statMsg('GIO_EvalName = %s GIO_Selection = %s' % \
                        (ConfigVars[CN]['GIO_EvalName'], ConfigVars[CN]['GIO_Selection']))
         if ConfigVars[CN]['GIO_Selection'] == 'FORCED':
            ScrCmds.statMsg('GIO_Selection - Demand Check = FORCED - Run Drive')
            restartIDT = 2
         elif ConfigVars[CN]['GIO_Selection'] == 'SELECT' or ConfigVars[CN]['GIO_Selection'] == 'ON':
            Demand = IDTSelect()
            restartIDT = Demand.DemandCheck('IDT')      # Check Demand table, to turn the test on/off
            if restartIDT:
               ScrCmds.statMsg('GIO_Selection - Demand Check = Pass - Run Drive')
      return restartIDT


   #----------------------------------------------------------------------------
   def resetFDEAttributes(self):
      """
      Reset all existing FDE drive attributes.
      The drive attributes are:
       - FDE_DRIVE
       - TD_SID
       - IFD_PBI_01_PN
       - IFD_PBI_01_HASH
       - TD_FILESYS_ID
      """
      self.driveattr['FDE_DRIVE'] = 'NONE'
      self.driveattr['IEEE1667_INTF'] = 'NONE'

      if not testSwitch.FE_0280070_385431_HunderedPercentSecuredDrive:
         from PIFHandler import CPIFHandler
         customer = CPIFHandler()

         if customer.IsTCG() or customer.IsFDE() or customer.IsSDnD():
            objMsg.printMsg("Secure drive, no need to reset TD_SID'")
         else:
            objMsg.printMsg("Non secure drive, attempting to reset TD_SID'")
            if DriveAttributes.has_key('TD_SID'):
               DriveAttributes.update({'TD_SID': 'NONE'})
               self.driveattr['TD_SID'] = 'NONE'
      else:
         objMsg.printMsg("100% Secure drive, no need to reset TD_SID'")

      if DriveAttributes.has_key('IFD_PBI_01_PN'):
         DriveAttributes.update({'IFD_PBI_01_PN': 'NONE'})
         self.driveattr['IFD_PBI_01_PN'] = 'NONE'
      if DriveAttributes.has_key('IFD_PBI_01_HASH'):
         DriveAttributes.update({'IFD_PBI_01_HASH': 'NONE'})
         self.driveattr['IFD_PBI_01_HASH'] = 'NONE'
      if DriveAttributes.has_key('TD_FILESYS_ID'):
         DriveAttributes.update({'TD_FILESYS_ID': 'NONE'})
         self.driveattr['TD_FILESYS_ID'] = 'NONE'

   def setSystemAreaState(self, systemAreaPrepared = 0):
      self.systemAreaPrepared = self.driveattr['SYS_AREA_PREPD'] = systemAreaPrepared

   def reset_DUT_dnld_segment(self, codeType):
      if codeType in ['IMG', 'CMB', 'CMZ', 'SAP', 'TXT_TPM', 'IMG_BIN']:
         self.mdwCalComplete = self.driveattr['MDW_CAL_STATE'] = 0
         self.driveattr['DEPOP_DONE'] = 'NONE'

      if codeType in ['IMG', 'RAP', 'RAPA', 'RAPT', 'RAPL', 'TXT_TPM', 'IMG_BIN']:
         self.systemAreaPrepared = 0

      self.GotDrvInfo = 0

   def __TestFlowAtt(self):
      from Rim import objRimType
      if testSwitch.virtualRun:
         return 'GEM'
      else:
         if testSwitch.FE_0124378_391186_HDSTR_CONTROLLED_BY_FILE and not testSwitch.FE_0143876_421106_P_HDSTR_OR_GEMINI_PROCESS_WITH_DRIVE_ATTR:
            Test_Value = self.__selectSt240MK(DebugMsg=0)
            if Test_Value == 'Y':
               return 'GHG'
         if testSwitch.FE_0158386_345172_HDSTR_SP_PRE2_IN_GEMINI:
            Test_Value = self.__selectHDSTR_SP(DebugMsg=0)
            if Test_Value == 'Y':
               return 'GHG2'
         if objRimType.IsHDSTRRiser():
            return 'HG'
         else:
            Test_Value = 'GEM'
         return Test_Value

   def __selectHDSTR_SP(self,DebugMsg=1):
      from st240_selection import HDSTR_SP2_Config
      HDSTR_SP2AttrList = {'SN':HDASerialNumber, 'PN':DriveAttributes['PART_NUM'], 'SBG':DriveAttributes['SUB_BUILD_GROUP']}
      if DebugMsg:
         ScrCmds.statMsg('------ HDSTR_SP2 Selection ------')
         ScrCmds.statMsg('Serial Num = %s'%str(HDSTR_SP2AttrList['SN']))
         ScrCmds.statMsg('Part Number = %s'%str(HDSTR_SP2AttrList['PN']))
         ScrCmds.statMsg('Sub Build Group = %s'%str(HDSTR_SP2AttrList['SBG']))

      keyList = HDSTR_SP2_Config.keys()
      keyList.sort()
      run_st240 = False
      for key in keyList:
         for attribute in HDSTR_SP2_Config[key]:
            if not HDSTR_SP2AttrList.has_key(attribute):
               ScrCmds.raiseException(11044, 'HDSTR_SP2_Config attribute "%s" is undefined in select HDSTR_SP. Valid attributes = %s'%(attribute,HDSTR_SP2AttrList.keys()))
            if HDSTR_SP2_Config[key][attribute] == '*':
               run_st240 = True
            elif attribute == 'SN':
               if HDSTR_SP2AttrList['SN'][1:3] == HDSTR_SP2_Config[key]['SN']:
                  run_st240 = True
               else:
                  run_st240 = False
                  break
            elif HDSTR_SP2_Config[key][attribute][0:1] == '-':
               if HDSTR_SP2AttrList[attribute][6:10] == HDSTR_SP2_Config[key][attribute]:
                  run_st240 = True
               else:
                  run_st240 = False
                  break
            elif attribute == 'SBG':
               if HDSTR_SP2AttrList['SBG'] == HDSTR_SP2_Config[key]['SBG']:
                  run_st240 = True
               else:
                  run_st240 = False
                  break
            elif HDSTR_SP2AttrList[attribute] == HDSTR_SP2_Config[key][attribute]:
               run_st240 = True
            else:
               run_st240 = False
               break
         if run_st240:
            if testSwitch.FE_0189561_418088_IRECOVERY_SUPPORT:
               if self.IR_HSP_ACTIVE_VALUE == 'Y':
                  objMsg.printMsg("iRecovery : Overwrite HDSTR_SP2 Selection to 'N' since use to fail from FNC2 in HDSTR_SP machine")
                  return 'N'
            return 'Y'
         else:
            if DebugMsg:
               ScrCmds.statMsg('GHG2 Process NOT Selected for "%s" criteria.'%key)
      else:
         return 'N'


   def __selectSt240MK(self,DebugMsg=1):
      #Select ST240 criteria for Muskie drive
      from st240_selection import ST240Config

      serialnum = HDASerialNumber
      partNum   = DriveAttributes['PART_NUM']
      sbr       = DriveAttributes['SUB_BUILD_GROUP']
      if DebugMsg:
         ScrCmds.statMsg('------ HDSTR(GHG) Selection ------')
         ScrCmds.statMsg('Serial Num = %s'%str(serialnum))
         ScrCmds.statMsg('Part Number = %s'%str(partNum))
         ScrCmds.statMsg('Sub Build Group = %s'%str(sbr))

      ST240AttrList = {'SN':serialnum, 'PN':partNum, 'SBG':sbr}
      keyList = ST240Config.keys()
      keyList.sort()

      if testSwitch.FE_0143876_421106_P_HDSTR_OR_GEMINI_PROCESS_WITH_DRIVE_ATTR:
         for key in keyList:
            for attribute in ST240Config[key]:

               if not ST240AttrList.has_key(attribute):
                  ScrCmds.raiseException(11044, 'ST240Config attribute "%s" is undefined in selectSt240. Valid attributes = %s'%(attribute,ST240AttrList.keys()))

               if ST240Config[key][attribute] == '*':
                  run_st240 = True
               elif attribute == 'SN':
                  if ST240AttrList['SN'][1:3] == ST240Config[key]['SN']:
                     run_st240 = True
                  else:
                     run_st240 = False
                     break
               elif ST240Config[key][attribute][0:1] == '-':
                  if ST240AttrList[attribute][6:10] == ST240Config[key][attribute]:
                     run_st240 = True
                  else:
                     run_st240 = False
                     break
               elif attribute == 'SBG':
                  if ST240AttrList['SBG'] == ST240Config[key]['SBG']:
                     run_st240 = True
                  else:
                     run_st240 = False
                     break
               elif ST240AttrList[attribute] == ST240Config[key][attribute]:
                  run_st240 = True
               else:
                  run_st240 = False
                  break
         return run_st240

      else:
         for key in keyList:
            for attribute in ST240Config[key]:

               if not ST240AttrList.has_key(attribute):
                  ScrCmds.raiseException(11044, 'ST240Config attribute "%s" is undefined in selectSt240. Valid attributes = %s'%(attribute,ST240AttrList.keys()))

               if ST240Config[key][attribute] == '*':
                  run_st240 = True
               elif attribute == 'SN':
                  if ST240AttrList['SN'][1:3] == ST240Config[key]['SN']:
                     run_st240 = True
                  else:
                     run_st240 = False
                     break
               elif ST240Config[key][attribute][0:1] == '-':
                  if ST240AttrList[attribute][6:10] == ST240Config[key][attribute]:
                     run_st240 = True
                  else:
                     run_st240 = False
                     break
               elif attribute == 'SBG':
                  if ST240AttrList['SBG'] == ST240Config[key]['SBG']:
                     run_st240 = True
                  else:
                     run_st240 = False
                     break
               elif ST240AttrList[attribute] == ST240Config[key][attribute]:
                  run_st240 = True
               else:
                  run_st240 = False
                  break

            if (run_st240 and not self.nextOper == 'FNC2') :#and (ConfigVars[CN].get("Hdstr Process", 'N') == 'Y'): #Don't assign ST240 oper on re-FNC2 drive
               if DebugMsg:
                  ScrCmds.statMsg('ST240 Process Selected for "%s" criteria.'%key)
               self.driveattr['ST240_PROC'] = 'P'
               return 'Y'
            else:
               if DebugMsg:
                  ScrCmds.statMsg('ST240 Process NOT Selected for "%s" criteria.'%key)
         else:
            if DebugMsg:
               ScrCmds.statMsg('Drive did NOT meet any of the ST240 selection criteria.')
            self.driveattr['ST240_PROC'] = 'N'
            return 'N'

   #elif (self.driveattr.get('ST240_PROC','N') == 'Y' or self.driveattr.get('ST240_PROC','N') == 'C') and not self.nextOper == 'FNC2':
   #   ScrCmds.statMsg('ST240 Process Resumption.')
   #   return Operations_ST240
   #else:
   #   ScrCmds.statMsg('This drive is NOT running the ST240 process')
   #   return Operations

   if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
      def loadBaselineRestoreFiles(self):
         """Determine if baseline restore files where loaded into the config.  If so, keep a dictionary of what is available"""
         import os, re
         restorePath = ScrCmds.getSystemDnldPath()

         restoreBaselines = {}
         for fileName in os.listdir(restorePath):
            if 'RESTORE_%s' %HDASerialNumber in fileName.upper():
               pat = 'RESTORE_%s_.*%s_\d*_(?P<state>.*)_(?P<request>[\w\d]*)\.\w*' %(HDASerialNumber, self.nextOper)   #'RESTORE_1YDBENCH_bench_PRE2_1_baseline_state_FLASHIMG.BIN'
               match = re.match(pat,fileName)
               if match:
                  state, restore_type = match.groups()
                  if state not in restoreBaselines:
                     restoreBaselines[state] = {}
                  restoreBaselines[state].update({restore_type:os.path.join(restorePath,fileName)})

         objMsg.printMsg('Baseline Restore Dictionary = %s' %restoreBaselines)
         return restoreBaselines
   #----------------------------------------------------------------------------
   def cust_testname(self, test, attrName = 'CUST_TESTNAME'):
      ''' Support multiple selection of customer unique tests.'''
      tests = self.driveattr.get(attrName,'NONE').replace('NONE','')
      if not test in tests:
         return self._sort(tests + test)
      return self._sort(tests)

   #----------------------------------------------------------------------------
   def _sort(self, cust_testname, chars = 3):
      ''' Returns sorted testnames as per Seatrack requirement with each default test
          name code length equals to 3 characters (i.e AP2 for Apple BLUENUN test).
          Example: 'AP2AP1AP3'
          Returns: 'AP1AP2AP3'
      '''
      # Validate correct code length format
      if len(cust_testname) % chars != 0:
         ScrCmds.raiseException(11044, "Invalid test code length (test code = '%s')." %cust_testname)
      # List then sort customer test codes
      tests = [cust_testname[i * chars : (i * chars ) + chars] for i in xrange(len(cust_testname) / chars)]
      tests.sort()
      return ''.join(tests)

   def updateCellTemp(self, cellTemp):
      if self.driveattr['PROC_CTRL20'] == 'NONE':
         self.driveattr['PROC_CTRL20'] = str(cellTemp)
      else:
         self.driveattr['PROC_CTRL20'] = self.driveattr['PROC_CTRL20'] + '/' + str(cellTemp)

   def updateDriveTemp(self, driveTemp):
      if self.driveattr['PROC_CTRL21'] == 'NONE':
         self.driveattr['PROC_CTRL21'] = str(driveTemp)
      else:
         self.driveattr['PROC_CTRL21'] = self.driveattr['PROC_CTRL21'] + '/' + str(driveTemp)

   def isFDE(self):
      if self.IdDevice.has_key('FDE') and (self.IdDevice['FDE'] & 0x4001 == 0x4001):
         return True
      else:
         return False

   #------------------------------------------------------------------------------------------------------#
   def cleanCodesDictCmsWilds(self):
      """
      Procedure to clean the Codes.fwConfig CMS wildcards
         and convert them to regex values
      """
      for key,value in Codes.fwConfig.items():
         if key.find('%') > -1:
            Codes.fwConfig[Utility.convertCmsWildCardToRe(key)] = value
            del Codes.fwConfig[key]


   def buildFileList(self):
      from Rim import objRimType

      internalPN = self.partNum
      if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
         self.cleanCodesDictCmsWilds()

      objMsg.printMsg("Codes.fwConfig = \n%s" % (Codes.fwConfig,))
      # TT: ENH-00254: select codes based on full p/n rather than base p/n
      try:
         if testSwitch.FE_0145180_357260_P_BROKER_PROCESS:
            try:
               self.codeDictToSearch = Codes.fwConfig[internalPN]
            except:
               self.codeDictToSearch = Codes.fwConfig['broker']
         elif testSwitch.FE_0149593_357260_SEAGATE_THERMAL_CHAMBER:
            self.codeDictToSearch = Codes.fwConfig['STCstc']
         else:
            if testSwitch.FE_0185032_231166_P_TIERED_COMMIT_SUPPORT:
               objMsg.printMsg("Looking for %s" % internalPN)
               #tierPN, tier = CommitServices.convertPNtoTier(self.partNum)
               self.codeDictToSearch = Utility.getSortedRegexMatch(internalPN, Codes.fwConfig)
               #self.codeDictToSearch.update(Utility.getSortedRegexMatch(tierPN, Codes.fwConfig))
            else:
               self.codeDictToSearch = Codes.fwConfig[internalPN]
      except:
         objMsg.printMsg(traceback.format_exc())
         if not testSwitch.virtualRun == 1:
            ScrCmds.raiseException(10345, "FwConfig: PN=%s not found in Codes.py" % (internalPN,))
         else:
            self.codeDictToSearch = {'TPM':'dummy'}

      self.buildCustomFWList()

      if testSwitch.FE_0174482_231166_P_USE_INC_CODE_BY_SOC_TYPE:
         #Add SOC type to the codeDictToSearch
         socFiles = getattr(Codes, 'socFiles', False)
         if socFiles:
            incCode = socFiles.get(objRimType.getRiserSOCType(), False)
            if incCode:
               self.codeDictToSearch['INCP'] = incCode
            else:
               objMsg.printMsg("INC Code type of %s not supported in Codes.py" % (objRimType.getRiserSOCType(),))
         else:
            objMsg.printMsg("No socFiles dict in Codes.py")

      missingFileList = [] # list of missing dnld and support files

      # check if missing firmware files, append files to config list
      for codeType,codeFileName in self.codeDictToSearch.items(): # iterate through dictionary
         #For furture scale-ability we will assume handling for all types being a list.
         if not type(codeFileName) in [types.ListType, types.TupleType]:
            #Convert base file to an iterable so iteration is the same.
            codeFileList = [codeFileName]
         else:
            codeFileList = list(codeFileName)
         self.codes[codeType] = codeFileList

         #Iterate over all files in the codetype list
         for codesFileName in codeFileList:
            #Zip files are expanded upon config preperation in the CM so we can't look for a physical version of them
            zipMultiPat = '(%s)(\.[zipZIP]{3})'
            zipMatch = re.search(zipMultiPat % '\S*',codesFileName)
            if zipMatch == None:
               for fileName in self.getAlternateFileNames(codesFileName):
                  filePath = os.path.join(ScrCmds.getSystemDnldPath(), fileName)
                  if os.path.isfile(filePath) and fileName in os.listdir(ScrCmds.getSystemDnldPath()):
                     fileIndex = self.codes[codeType].index(codesFileName)
                     self.codes[codeType][fileIndex] = fileName
                     break
               else:
                  missingFileList.append(codesFileName)

      # check if missing support dlfile files
      try:
         for dlType,dlFile in Codes.dlConfig.items():
            for fileName in self.getAlternateFileNames(dlFile):
               filePath = os.path.join(ScrCmds.getSystemDnldPath(), fileName)
               if os.path.isfile(filePath) and fileName in os.listdir(ScrCmds.getSystemDnldPath()):
                  self.codes[dlType] = fileName
                  break
            else:
               self.codes[dlType] = fileName
               missingFileList.append(dlFile)
      except:
         pass


      ScrCmds.insertHeader("Firmware for PN %s" % self.partNum)
      codeTypeList = self.codes.keys()
      codeTypeList.sort()
      for codeType in codeTypeList:
         #Convert single item lists back to string item to insure backwards compatibilty with packageResolution.
         if type(self.codes[codeType]) in [types.ListType, types.TupleType] and len(self.codes[codeType]) == 1:
            self.codes[codeType] = self.codes[codeType][0]
         ScrCmds.statMsg("%15s: %s" %(codeType,self.codes[codeType]))
      ScrCmds.insertHeader("")

      # check if missing common files
      for file in Codes.commonFiles:
         if os.path.splitext(file)[1] != '.py':
            filePath1 = os.path.join(ScrCmds.getSystemParamsPath(), file)
            filePath2 = os.path.join(ScrCmds.getSystemDnldPath(), file)
            if not (os.path.isfile(filePath1) or os.path.isfile(filePath2)):
               missingFileList.append(file)

      # raise exception if any listed file is missing
      if len(missingFileList) > 0:
         ScrCmds.statMsg('Missing file(s):')
         ScrCmds.statMsg(`missingFileList`)
         if testSwitch.winFOF == 1 or testSwitch.virtualRun == 1:   #Ignore missing files if winFOF
            ScrCmds.statMsg("winFOF mode active ignoring missing files...")
         else:
            ScrCmds.raiseException(10326, "1 or more Listed files are missing %s" % str(missingFileList))

   #----------------------------------------------------------------------------
   def buildCustomFWList(self):
      if testSwitch.buildCustomFW:


         if self.capacity == None:
            if not testSwitch.virtualRun:
               ScrCmds.raiseException(11044, "Capacity not defined for SBR %s" % self.sbr)
            else:
               self.capacity = ConfigVars[CN].get('CapacityTarget',400)

         ScrCmds.statMsg('%s %s %s %s' % (self.HGA_SUPPLIER,self.imaxHead,self.capacity,self.preampVendor))
         for key in self.codeDictToSearch.keys():
            if type(self.codeDictToSearch[key]) == types.DictType:
               for keyList,codeName in self.codeDictToSearch[key].items():
                  headList,hgaVendor,preampVendor,capacitySpec = keyList
                  if hgaVendor in [self.HGA_SUPPLIER,None]:
                     if self.imaxHead in headList or headList == () and capacitySpec in [self.capacity, None] and \
                        preampVendor in [self.preampVendor,None]:
                        self.codeDictToSearch[key] = codeName
                        break
               else:
                  ScrCmds.raiseException(11044, "Firmware selection failed")

   #----------------------------------------------------------------------------
   def getAlternateFileNames(self,codesFileName):
      '''Load alternate file names into a list to be parsed by buildFileList'''
      alternateFileNameList = []
      if type(codesFileName) in [types.ListType, types.TupleType]:
         for item in codesFileName:
            alternateFileNameList.extend(self.getAlternateFileNames(item))
      else:
         baseName,fileExt = os.path.splitext(codesFileName)
         alternateFileNameList.append('%s%s'% (baseName.upper(),fileExt.lower()))
         alternateFileNameList.append('%s%s'% (baseName.lower(),fileExt.upper()))
         alternateFileNameList.append(codesFileName.upper())
         alternateFileNameList.append(codesFileName.lower())
         alternateFileNameList.append(codesFileName)

      return alternateFileNameList

   #------------------------------------------------------------------------------------------------------#
   def checkBGforReFIN2(self):
      '''
      BSNS_SEGMENT check for protection re-config process
      '''
      if self.nextOper == 'FIN2':
         from StateMachine import CLongAttr
         longattr_bsns = CLongAttr().DecodeAttr(DriveAttributes)
         list_bsns = longattr_bsns.split("/")

         if self.BG not in list_bsns:
            ScrCmds.raiseException(48590, "Fail BSNS_SEGMENT, %s isn't in passed Business Segment %s."%(self.BG, list_bsns))

   #------------------------------------------------------------------------------------------------------#
   def isprime(self):
      """ Determines prime or reconfig drives."""
      return bool(self.scanTime) # scanTime == 0 means not fresh load


class CspSBGContainer(object):
   def __init__( self,driveattr):

      self.driveattr = driveattr
      if testSwitch.virtualRun:
         self.sbr = 'KTGRD2FB34A'
      else:
         self.sbr = self.driveattr['SUB_BUILD_GROUP']
      #if testSwitch.FE_0143655_345172_P_SPECIAL_SBR_ENABLE:
      ScrCmds.statMsg("********* Turn on condition build for Special SBR. *********")
      self.sp_SBG            = 0
      self.spSBGParametrics  = 0    #Con#1. Turn on/off drive parametric (100%).
      self.spSBGSDAT         = 0    #Con#2. Turn on/off SDAT for passer drive.
      self.spSBGAutoRerun    = 0    #Con#3  Turn on/off Auto-Rerun.
      self.spSBGWaVBAR       = 0    #Con#4  Turn on/off waterfall from VBAR.
      self.spSBGGOTFPN       = 0    #Con#5  Turn on/off Waterfall to other PartNum
      #self.spSBGInterface   = None    #Con#6  Indicate Interface type(SATA or SAS)
      self.spSBGGOTF         = 0    #Con#7  Turn on/off GOTFs.
      self.spSBGIDT          = 0    #Con#8  Turn on/off IDT test. #self.spSBGODT
      self.spSBGHoldPass     = 0    #Con#9   Hold passer drives.
      self.spSBGHoldFail     = 0    #Hold#10 all failure drives.
      if testSwitch.FE_0143655_345172_P_SPECIAL_SBR_ENABLE:
         self.initializeSpSBR()

   def initializeSpSBR(self):
      Base32Digit = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','J','K','L','M','N','P','Q','R','S','T','V','W','X','Y']
      FISData     = ['D','P','S','E','X'] #D=DesignCenter,P=Pre-Volume,S=SpecialVolume,E=EvaluationBuild,ConditionFlag = ''
      if len(self.sbr) <= 12 and self.sbr[0:2] in ['TK','KT','SS','DJ','WX',] and self.sbr[4] in FISData and self.sbr[6] in Base32Digit and self.sbr[7] in Base32Digit:
         self.sp_SBG            = 1
         D5SpSBG          = Base32Digit.index(self.sbr[6])
         D6SpSBG          = Base32Digit.index(self.sbr[7])
         self.spSBGParametrics = D5SpSBG>>4 & 1   #Con 1
         self.spSBGSDAT        = D5SpSBG>>3 & 1   #Con 2
         self.spSBGAutoRerun   = D5SpSBG>>2 & 1   #Con 3
         self.spSBGWaVBAR      = D5SpSBG>>1 & 1   #Con 4
         self.spSBGGOTFPN      = D5SpSBG    & 1   #Con 5
         if int(self.spSBGSDAT) == 1 and not D6SpSBG&1:
            D6SpSBG+=1
            ScrCmds.statMsg("Special SBR:Change status Hold all failure drives when SDAT turn on")
         self.spSBGGOTF        = D6SpSBG>>3 & 1   #Con 7
         self.spSBGIDT         = D6SpSBG>>2 & 1   #Con 8
         self.spSBGHoldPass    = D6SpSBG>>1 & 1   #Con 9
         self.spSBGHoldFail    = D6SpSBG    & 1   #Con 10

         ConditionFlag         = "".join([str((D5SpSBG >> y) & 1) for y in range(5-1, -1, -1)])
         ConditionFlag         = ConditionFlag + "".join([str((D6SpSBG >> y) & 1) for y in range(5-1, -1, -1)])
         ScrCmds.statMsg("-"*65)
         ScrCmds.statMsg("Special SBR's Name Conditions Checking:Match Special SBR's Name Control.")
         ScrCmds.statMsg("********* Condition of special SBR  project : %s. *********" % ConditionFlag)
         self.driveattr['CONDITIONS_BUILD'] = ConditionFlag
         if self.spSBGParametrics:
            ScrCmds.statMsg("Condition 1 -Enable drive parametric (100%).")
         else:
            ScrCmds.statMsg("Condition 1 -Disable drive parametric (100%).")
         if self.spSBGSDAT:
            ScrCmds.statMsg("Condition 2 -Enable SDAT.")
         else:
            ScrCmds.statMsg("Condition 2 -Disable SDAT.")
         if self.spSBGAutoRerun:
            ScrCmds.statMsg("Condition 3 -Enable Auto-Rerun.")
         else:
            ScrCmds.statMsg("Condition 3 -Disable Auto-Rerun.")
         if self.spSBGWaVBAR:
            ScrCmds.statMsg("Condition 4 -Enable Waterfall from VBAR.")
         else:
            ScrCmds.statMsg("Condition 4 -Disable Waterfall from VBAR.")
         if self.spSBGGOTFPN:
            ScrCmds.statMsg("Condition 5 -Enable downgrade to other tab.")
         else:
            ScrCmds.statMsg("Condition 5 -Disable downgrade to other tab.")
         if self.spSBGGOTF:
            ScrCmds.statMsg("Condition 7 -Enable GOTFs.")
         else:
            ScrCmds.statMsg("Condition 7 -Disable GOTFs.")
         if self.spSBGIDT:
            ScrCmds.statMsg("Condition 8 -Enable ODT test (100%).")
            ConfigVars[CN]['GIO_Selection'] = 'FORCED'
         else:
            ScrCmds.statMsg("Condition 8 -Disable ODT test (100%).")
            ConfigVars[CN]['GIO_Selection'] = 'OFF'
         if self.spSBGHoldPass:
            self.driveattr['SBR_PASS'] = 'HOLD'
            ScrCmds.statMsg("Condition 9 -Enable hold passer drives.")
         else:
            self.driveattr['SBR_PASS'] = 'NONE'
            ScrCmds.statMsg("Condition 9 -Disable hold passer drives.")
         if self.spSBGHoldFail:
            ScrCmds.statMsg("Condition 10 -Enable hold all failure drives.")
         else:
            ScrCmds.statMsg("Condition 10 -Disable hold all failure drives.")
         ScrCmds.statMsg("-"*65)
      else:
         ScrCmds.statMsg("SBR's Name Conditions Checking:No Special SBR's Name Control.")
         return


###########################################################################################################
###########################################################################################################
objDut = CDrive(PortIndex)
TraceMessage('Drive Instance Created %d' % PortIndex)


###########################################################################################################
###########################################################################################################
#---------------------------------------------------------------------------------------------------------#
