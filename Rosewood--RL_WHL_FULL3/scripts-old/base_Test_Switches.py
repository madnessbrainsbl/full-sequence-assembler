#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: This file holds all operational switches for the process. Flags defined here are overridden by
#                 the program.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/16 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_Test_Switches.py $
# $Revision: #28 $
# $DateTime: 2016/12/16 00:51:36 $
# $Author: hengngi.yeo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_Test_Switches.py#28 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from DesignPatterns import Singleton
from types import ListType, TupleType, DictType, IntType, BooleanType
import sys, os, traceback

import re
_pyver = sys.version_info
PYTHON_VERSION = _pyver[0] + (_pyver[1])/10.0 + (_pyver[2])/100.0 #construct 2.72 or 2.41 etc
PY_27 = PYTHON_VERSION > 2.69
PY_24 = PYTHON_VERSION < 2.50
if PY_27:
   import hashlib
else:
   try:
      import sha
   except:
      # md5 and sha have the same interface although sha is preferred
      #WinFOF 2.4- doesn't support the sha module so this is provided for bench execution.
      import md5 as sha

try:
   CE, CP, CN, CV = ConfigId
except:
   CN = 'bench'
   ConfigVars = {CN:{}}

IterableTypes = (ListType, TupleType)
FlagTypes = (IntType, BooleanType)

class externObject(dict):
   """
   Simple class to provide attribute like access and dictionary like access with defaults
   """
   def clear(self):
      keys = self.keys()
      for key in keys:
         del self[key]

   def __getattr__(self, name):
      if name in self:
         return self[name]
      else:
         return getattr(super(externObject, self), name, 0)

class CBaseSwitches(Singleton):
   __slots__ = ['extern', '__flagFileName'] # Since this is only a container lets optimize
   extern = externObject() # Dictionary used to hold dynamic switches we import from other codes.
   __flagFileName = '' # Used to prevent reloading the same flag file if already loaded


   def __getattr__(self, name):
      """
      Overloaded mechanism to provide attribute like access to the internal __dynamics dict.
      """
      if name in self.extern:
         return self.extern[name]
      else:
         return getattr(super(CBaseSwitches, self),name)

   def importExternalFlags(self, externalFlagFile):
      """
      Sets the current dynamic flags imported from a code flag output.
         Flag File must be a valid python file with 'flag={...}' as the source
      """
      # Why overwrite and note just update?-> for now we don't want the baggage
      # TODO: Evaluate if list of tuple pairs would be lower overhead than dict

      if externalFlagFile == self.__flagFileName:
         return # We have already loaded these

      import ScrCmds
      try:
         #flagCode = ''
         flagCode = open(os.path.join(ScrCmds.getSystemDnldPath(),externalFlagFile), 'r').read()
         flags={}
         gen = re.findall("'(\w+)'\:\s*([1-9][0-9]*),?",flagCode) #for cm memory saving ,only match non zero switch
         for res in gen:
            flags[res[0]] = int(res[1])
         #exec(flagCode)

      except SyntaxError:
         ScrCmds.statMsg("Unable to import flags from %s" % externalFlagFile)
         ScrCmds.statMsg("Error: %s" % (traceback.format_exc(),))
         self.extern.clear()
      except:
         ScrCmds.statMsg("General Error: %s" % (traceback.format_exc(),))
         ScrCmds.statMsg("File Data:\n%s" % flagCode)
         self.extern.clear()
      else:
         # Since flags is local there is no need to create a copy for __dynamics

         self.extern.clear()
         try:
            '''
            for key in flags:
               try:
                  flags[key] = int(flags[key])
               except:
                  # protect against invalid flags
                  pass
            ''' #for cm memory saving
            self.extern.update(flags)

            self.updateExternLocalRefs(externalFlagFile)
         except:
            ScrCmds.statMsg("flags not defined after exec('%s') " % flagCode)
            raise
         else:
            self.__flagFileName = externalFlagFile


   #########################################################################################
   #
   #               Function:  displayAllFlags
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  display all the flags
   #
   #                  Input:  None
   #
   #           Return Value:  None
   #
   #########################################################################################


   def displayAllFlags(self, externalFlagFile = ''):
      # This breaks bench runs ... DO NOT run when winFOF is set!!!
      if not self.winFOF or self.virtualRun:
         if self.virtualRun:
            print "\n\n Verifying the status of all switches \n\n"
         else:
            ScriptComment("\n\n Verifying the status of all switches \n\n")

         testSwitchRef = self

         allSwitches = dir(testSwitchRef)
         allSwitches.sort()
         if self.virtualRun:
            switchFileName = "VE_%s_switchFile.py" % CN
            switchFileNameList = [os.getcwd(), 'results', CN]

            #give dir search 5 tries
            for x in xrange(5):

               switchFilePath = os.path.join(*switchFileNameList)
               if os.path.exists(switchFilePath):
                  break
               else:
                  switchFileNameList.insert(1, '..')


            switchFile = open(os.path.join(switchFilePath, switchFileName), 'w')

         else:
            switchFileName = "%s_%s_switchFile.py" % (os.path.splitext(externalFlagFile)[0], ConfigId[2]) #put configname_switchFile.py
            switchFile = GenericResultsFile(switchFileName)
            switchFile.open('w')

         for localSwitch in allSwitches:
            localSwitchValue = str( eval("testSwitchRef.%s" % ( localSwitch )) )


            if self.virtualRun:
               if type(eval("testSwitchRef.%s" % ( localSwitch ))) in FlagTypes:
                  switchFile.write("%s = %s\n" % (localSwitch,  localSwitchValue ))
#              debug code
#              else:
#                 print "%s is %s" % (localSwitch, type(eval("testSwitchRef.%s" % ( localSwitch ))))
            else:
               switchFile.write("%s = %s\n" % (localSwitch,  localSwitchValue ))

         switchFile.close()
         if not self.virtualRun:
            try:
               RequestService("SendGenericFile", ((switchFileName,), "Platform"))
            except:
               pass

            switchFile.delete()


   #########################################################################################
   #
   #               Function:  updateExternLocalRefs
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  update the extern local references
   #
   #                  Input:  None
   #
   #           Return Value:  None
   #
   #########################################################################################


   def updateExternLocalRefs(self, externalFlagFile = ''):
      import Feature_Release_Test_Switches

      testSwitchRef = self

      objAFH_switch = Feature_Release_Test_Switches.CFeature_Release_Test_Switches( testSwitchRef )
      objAFH_switch.setSwitches( testSwitchRef )
      if self.virtualRun:
         print "updateExternLocalRefs/ standard call to Feature_Release_Test_Switches.CFeature_Release_Test_Switches() worked"
      else:
         ScriptComment("updateExternLocalRefs/ standard call to Feature_Release_Test_Switches.CFeature_Release_Test_Switches() worked")

      if self.virtualRun:
         self.displayAllFlags(externalFlagFile)

      self.getmd5SumForAFH_flags()
      # end of updateExternLocalRefs

   #
   #######################################################################################################################
   #
   #               Function:  getmd5SumForAFH_flags
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  Create a mechanism to quickly check if the PF3 AFH Flags are set correctly.
   #
   #          Prerrequisite:  testSwitch.updateExternLocalRefs() has been called
   #
   #                  Input:  None
   #
   #                 Return:  md5Sum(str)
   #
   #######################################################################################################################


   def getmd5SumForAFH_flags(self, ):
      # This breaks bench runs ... DO NOT run when winFOF is set!!!
      if not self.winFOF:
         flags = dir(self)
         flags.sort()
         regex1 = re.compile("(341036|AFH)")
         if PY_27:
            md5Obj = hashlib.md5()
         else:
            md5Obj = sha.new()


         n = 0
         bitFieldString = "_"
         for flag in flags:
            r1 = regex1.search( flag )
            if r1 != None:
               flagValueStr = str(eval("self.%s" % ( flag) ))
               str0 = str(flag) + flagValueStr
               md5Obj.update( str0 )
               n += 1
               bitFieldString += flagValueStr
         md5Sum = str(md5Obj.hexdigest())

         displayMessage = "AFH Maj: %s, Min: %s,  md5Sum of PF3 AFH flags: %s,  Num Flags: %s,  Flag Field: %s" % \
            ( self.extern.AFH_MAJ_REL_NUM,  self.extern.AFH_MIN_REL_NUM, md5Sum, n, bitFieldString  )
         if self.virtualRun:
            print displayMessage
         else:
            ScriptComment( displayMessage )

         return md5Sum


   #########################################################################################


   # Build target -- This will be updated by the PF3 Make process
   BUILD_TARGET = "RL42"
   TIPS = BUILD_TARGET == "PTIP"



   #########################################################################################
   # Audit Test: The auditTest flag will be set via configVars - DO NOT ENABLE AUDITTEST IN TESTSWITCHES.PY
   auditTest = ConfigVars[CN].get('AuditTest',0)
   shortProcess = ConfigVars[CN].get('shortProcess',0)
   #########################################################################################


   ############### FLAG DEFINES ######################
   ### All Flags should be defined false in here and overriden at the program level.
   ### Please try and maintain the formatting and alphabetic structure.

   ###################AFH Specific
   ACFF_DISABLE_RO_CAL_IN_SF3                                     =   0
   AFH_DISABLE_DYNAMIC_CWORD3_FOR_IPD                             =   0  # disable the TTR
   AFH_ENABLE_CLR_RANGE_CHECK_IN_CROSS_STROKE_CHECK               =   0
   AFH_ENABLE_TEST135_CLOSED_LOOP_DISABLE_TEST35                  =   0
   AFH_FORCE_DPES_TO_DECLARE_LAST_CONSISTENCY_CHECK_RETRY         =   0
   AFH_NEVER_FORCE_DPES_TO_DECLARE                                =   0
   AFH_V3BAR_phase5                                               =   0  # <--- Enable only when MD sys is enabled.
   ALL_DRIVES_GET_WWN                                             =   0  # If intf_type in WWN_INF_TYPE dict list then assign WWN
   AFH_ENABLE_TEST135_ADDITIONAL_MEASUREMENTS_AT_EXTREME_OD_ID    =   0
   AFH_ENABLE_TEST135_OD_ID_ROLLOFF_SCREEN                        =   0
   AFH_ENABLE_CLOSED_LOOP_HIRP_DH                                 =   1
   AFH_IS_RAP_TCS_IN_ANGSTROMS                                    =   0
   AFH_ENABLE_ANGSTROMS_SCALER_USE_254                            =   0
   AFH_ENABLE_PF3_SIM_DATA_OUTPUT_IN_ANGSTROMS                    =   0
   AFH_V35                                                        =   0
   AFH_BURNISH_CHECK_BYPASS_READER_CLR                            =   0
   FE_AFH3_TO_DO_BURNISH_CHECK                                    =   0 
   AutoCommit                                                     =   0
#CHOOI-26May16 OffSpec
   OOS_Code_Enable = 0

   BF_0112487_208705_MUST_FIND_CORRECT_SERVO                      =   0  # Don't default to first servo code listed if servo code isn't listed
   BF_0115022_220554_ENSURE_BER_HAS_A_VALUE_DURING_TARGET_OPTI    =   0  # Fix TARGET OPTI process failure 11044 : After T250 and then BER is equal to NoneType.
   BF_0115535_405392_FIX_RAISE_11049_EC_WITH_CFLASHCORRUPTEXCEPTION = 0  # BF for raise 11049 EC with CFlashCorruption exception
   BF_0119058_399481_NUMCYLS_LIST_LENGTH_EQUAL_TO_NUMHEADS        = 0    # Improve VE data returned from serialScreen.getZoneInfo, prevents imaxHead from being improperly set to 1, or numZones from being blindly set to 17.
   BF_0119072_231166_DISABLE_SKIP_TRACK_LOG_CLEAN_DISC            = 0    # Disable skip track logging in Cleandisc
   BF_0121631_399481_NO_SEEKLBA_IN_RWLBAS                         = 0    # Seek may cause strange failure in following LBA write command.
   BF_0120661_357260_ENABLE_ZAP_DURING_INIT_FS                    = 0    # Turn Zap on during initializeFlawLists() (INIT_FS class)
   BF_0122569_341036_AFH_MASTER_HEAT_SET_T011_USE_MASK_VALUE_FFFE = 0    # Ensure that MASK_VALUE is set properly for T11 calls to modify master heat, to that only the master heat bit is modified
   BF_0122949_231166_CHK_MRG_G_PWR_LOSS_SAFE                      = 0    # Fix bug in CHK_MRG_G where it wasn't power loss safe if power cycled in between g-p and full pack write
   BF_0122964_231166_NO_FAIL_FOR_ZGS_AVAIL_NOT_NEED               = 0    # Don't fail for ZGS disabled in F3 code but enabled on board- is don't care.
   BF_0123402_231166_SET_CELL_BAUD_BEF_ASCII_DBG                  = 0    # Set baud rate on cell prior to trying to do ascii debug retry- prevents a CPC related default baud issue.
   BF_0123471_231166_DEL_CUST_MOD2_IF_INVALID                     = 0    # Remove CUST_MODEL_NUM2 from the self.dut.driveattr if '' or ? so that CUST_MODEL_NUM is sent
   BF_0123842_231166_FILE_XFER_FIX_BNCH_MULTI_BLOCK               = 0    # Fix bugs in FileXferFactory for multi-block memory file xfer and winfof
   BF_0124866_231166_FIX_IOEDC_ATTR_RETR                          = 0    # Fix IOEDC detection and attribute pull
   BF_0124988_231166_FIX_SUPPR_CONST_IMPL                         = 0    # Fix data suppression constants implementation logic
   BF_0125115_231166_FIX_SVO_F3_PKG_MFT_LOOKUP                    = 0    # Fix bug that caused aborts during getPackageTypeFromCodeVersion due to list of servo's supported in f3 codes
   FE_0125537_399481_TA_ONLY_T118_CALL                            = 0
   BF_0126008_7955_FIX_T250_ZONE_RETRY_LOOP                       = 0    # Fix T250 zone retry loop in quickSymbolErrorRate
   BF_0126695_399481_MQM_CORRECT_TEST_AREA_FINDER                 = 0    # Seek to each track in test area to verify that track is not slipped, diag logical tracks can be devoid of LBAs in which case seek fails.  Also fix typo.
   BF_0126696_231166_FIX_CMD_FAIL_IN_SAS_DITS_UNLK                = 0    # Fix command TMO issues when issuing unlock commands due to not waiting for DUT ready
   BF_0127147_357552_REFERENCE_T180_PARAM_BY_STRING_NAME          = 0    # Reference T180 prm dict by string name, so any servo overrides included
   BF_0127472_231166_DONT_CERT_BBT_NO_BBTS                        = 0    # Don't cert BBT in iniator cells when no BBT is found
   BF_0127710_231166_FIX_COM_MODE_POST_MCT_TEST                   = 0    # Re-apply com mode mctBase after an MCT test sucessfully completes if MCT mode isn't set- state reset needed per some power cycle RIM state loss
   BF_0128273_341036_AFH_DEPOP_HEAD_SUPPORT_AFH_SIM               = 0    # AFH depop head support
   BF_0130425_357466_FIX_T597_DOS_VER                             = 0    # Fix T597 and DOS_VERIFY run
   BF_0130884_354753_ANIMAL_SCRIPTS_CHANGES_TO_WORK_WITH_F3TRUNK  = 0    # Minor changes for Animal
   BF_0131166_399481_CONVERT_DISC_RECYCLE_ATTR_TO_INT             = 0
   BF_0132023_161897_SATA_INITIATOR_CRT2_11087                    = 0    # Korat fix for 11087 in SATA Initiator cells for Pharaoh
   BF_0132183_399481_CORRECT_LOGGEDERRORS_LOGIC                   = 0    # loggedErrors reference prior to creation under certain circumstances.
   BF_0131992_409401_DISC_RECYCLE_FROM_NUMHEAD                    = 0    # Korat fix for use imax head rather than fix as defaul when DRV_RWK_MEDIA calculation
   BF_0133084_231166_DYNAMIC_ATTR_PARAM_REDUCTION                 = 0    # Accurately accumulate the drive attribute size in parametric file margin assessments
   BF_0133147_208705_TABLE_MISSING_HEAD_DATA                      = 0    # Fix P_DELTA_RRAW to include valid physical head data
   BF_0133850_372897_REMOVE_BUFFER_LENGTH_IN_CLEARBUFFER          = 0    # Remove BUFFER_LENGTH para to using default value to clean whole buffer
   BF_0133851_372897_BLUENUNSLIDE_BUG_FIX_FOR_SI                  = 0    # BluenunSlide para Multiplier 125 in initiator equal to CPC as 12.5.
   BF_0134600_372897_DST_TEST_BUG_FIX_IN_SI                       = 0    # Drive self test can not raise error casued by SIC code bug, PF3 temp fix.
   BF_0135400_231166_FIX_CTRL_L_ESLIP_TRANSITION                  = 0    # Fix bug where eslip wasn't enabled after CTRL_L in codever
   BF_0136108_231166_P_INCL_ASFT_IN_FORMAT_REQ                    = 0    # Determine and add ASFT defects in the determination of whether we should G-P merge and reformat in format
   BF_0136275_341036_DBLOG_FIX_NULL_DATA_INJECTION_ERROR          = 0
   BF_0136370_231166_ADD_UNLOCK_PRIOR_TO_AVSCAN_UPDATES           = 0
   BF_0137159_231166_FORCE_SPINDOWN_PRIOR_DIAG_FLSH_WRITE         = 0    # Force spin down prior to a diagnostic flash write. This is a new requirement as of HWWA_0133339_357634_SERVO_USES_SGPIO0_ON_GPIO4
   BF_0138112_231166_P_RESET_SOM_STATE_IN_ENDTEST                 = 0    # Fix issue where drives might possibly be shipped not in SOM0 state but SOM1,2
   BF_0139418_399481_P_NO_CTRL_Z_IN_BIE_SETUP_OR_DISABLE          = 0
   BF_0139838_231166_P_FIX_CPCRISERNEWSPT_SEASERIAL               = 0    # Fix seaserial in new CPC SPT cells w/ 1.8v rework
   BF_0140005_231166_P_FIX_FOFFILENAME_REF_BUFFER                 = 0    # fix access mechanisim in getbuffer to check both folder and name spelling of fof filename
   BF_0140398_231166_FIX_STATE_INTF_TRANSITION_IOINT              = 0    # Fix state transition options for interface types to use the interface type determination and not celltype lookup
   BF_0142561_231166_P_FIX_STEP_LBA_SAS                           = 0    # Add support/bf for step_lba support in initiator.
   BF_0142777_231166_P_ADJ_MAX_SAS_LBA_FOR_COUNT                  = 0    # Add +1 in getmaxlba for sas as the cmd 25 returns the max lba not lba count
   BF_0142781_231166_P_FIX_SAS_TTR_PARAMETERS_FOR_START_STOP      = 0    # Fix bug in SAS TTR parameters that didn't evaluate SS unit command appropriately
   FE_0143087_357552_BYPASS_SETUP_JUST_UNLOCK                     = 0    #
   FE_0143280_426568_P_SKIP_REQ_VS_CURRENT_SPEED_CHECK            = 0    # By pass required speed vs current speed check in CSetATASignalSpeed if the flag is set
   BF_0143469_231166_P_DISABLE_G_LIST_ABSOLUTE_FAIL_DOS_VER       = 0    # disable the absolute check of g list entries for dos_verify- differential will still be assessed
   BF_0143505_426568_P_DISPLAY_ENTIRE_DOS_TABLE                   = 0    # issue an m command instead of an m,2000 command before and after DOS_RESET to display table
   BF_0143925_231166_P_FIX_SAS_CUST_MOD_VENDOR_FIELD              = 0    # fix issue where sas cust model num wasn't pulling in both vendor and prodcut fields
   BF_0143937_357260_P_DELAY_5_SEC_BEFORE_CTRL_Z                  = 0    # Sleep for 5 seconds prior to the CTRL_Z in determineCodeType()
   BF_0144006_231166_P_SHIP_PROTECTION_MEDIA_CACHE                = 0
   BF_0144790_231166_P_FIX_GOTF_DBL_REGRADE_DUP_ROWS              = 0    # Remove regrade tables prior to creating dblog data for disc.
   BF_0144913_208705_P_SET_CAPACITY_NOT_MAX_LBA                   = 0    # Modify VBAR to set capacity in the RAP rather than max LBA
   BF_0144993_231166_P_FIX_KEY_ERROR_DBLOG_GOTF_BUG               = 0    # Fix bug assoc. with BF_0144790_231166_P_FIX_GOTF_DBL_REGRADE_DUP_ROWS
   BF_0145059_231166_P_REMOVE_517_EXCEPT_CASE_SAS_PWR_RETRY       = 0    # Fix bug under sas power cycles that had a 517 call in the except clause and shouldn't fail.
   BF_0145286_231166_P_FIX_MOBILE_SCREENS                         = 0    # Bug fixes for incorrect API's for SIC on mobile screens
   BF_0145392_231166_P_CHECK_COMM_MODE_SYNCSF3_SATA               = 0    # Fix syncF3code not identifying com mode appropriate for data collection in codever
   BF_0145507_231166_P_FIX_ATA_READY_IN_CERT_OPER                 = 0    # Don't execute ATA ready check in cert operations in CPC cell
   BF_0160549_342996_P_FIX_ATA_READY_IN_CERT_OPER_ADDN            = 0    # Don't execute ATA ready check in PowerOn method for cert operations in CPC cell
   BF_0145546_231166_P_SEQUENTIAL_CMD_XLATE_SIC                   = 0    # use wdmae not seq command in sic
   BF_0145549_231166_P_FIX_538_ATA_CMDS_SIC                       = 0    # use generic set features commands as opposed to individual 538 commands.
   BF_0145751_231166_P_ADD_DATA_PATTERN0_ATI_CMP                  = 0    # Use data pattern input for ati cmp option to trigger HW pattern compare.
   BF_0146418_231166_P_ONLY_PRINT_ERASE_DELTA_ONCE                = 0    # Move printout of P051_ERASURE_BER_DELTAS to the end of the by head loop
   BF_0147704_231166_P_ALWAYS_SET_LOR_FW_PORT_TCG                 = 0    # Always set the Lock on Reset for FW download port
   BF_0150006_341036_AFH_DH_RETROACTIVE_ADJUST_AFH1_PREHEAT       = 0    # AFH retroactive adjust AFH1 WRITER_HEATER rdClr (HO a.k.a. pre-heat clearance )
   BF_0158268_357360_P_DISABLE_SET_DEF_MODE_PAGES_IN_ODT          = 0    # Disable all mode page clearing from ODT - not needed / changes functionality (breaks) some tabs
   FE_0159623_396795_SET_OUT_OF_BOUNDS_TCS_VALUES_TO_MEAN         = 0    # Allow TCS values outside upper and lower spec to be set to the mean value
   BF_0161447_340210_DUAL_HTR_IN_HEAD_CAL                         = 0    # Make sure heads run in dual/single heater mode in HEAD_CAL
   BF_0162624_409401_P_CHOP_P250_ERROR_RATE_BY_ZONE_WITH_SECTOR_VALUE_SPCID_2 = 0    # Chop P250_ERROR_RATE_BY_ZONE with SECTOR value at SPC_ID = 2.
   BF_0164718_357260_P_HANDLE_LEGACY_32_BIT_LBAS                  = 0    # Provide legacy support for 32 bit LBAs.
   BF_0165681_340210_SERVO_MFT_SN_PREFIX_CHK                      = 0    # clean up SFWP package handling with manifest
   BF_0166676_475827_P_RAISE_11201_FOR_NO_ATTRVAL                 = 0    # Raise EC 11201 when AttrVal of None is passed to AutoValidateDCMAttrFloat
   BF_0166802_470833_P_SETSECTORSIZE_PAGEDATA_FIX                 = 0    # Fix a bug where mode page data was being saved to the wrong variable in CSetSectorSize
   BF_0165661_409401_P_FIX_TIMIEOUT_AT_T510_BUTTERFLY_RETRY       = 0    # Fix Timeout at T510 Butterfly by add T506 to set Timeout before T510 retry (From EC14016 & 14029)
   BF_0163631_340210_CORRECT_FILE_POS                             = 0    # fix 11044 due to dblog parsing
   BF_0169747_470833_P_SENDSLIPFRAME_ACK_BUFFER_CREATION_FIX      = 0    # Create the ACK buffer when sending a block within sendSLIPFrame, and check the the ACK immediately after sending. Fixes an issue where ACKs were lost in Neptune ovens.
   BF_0172780_470833_P_USE_LGC_HD_INSTEAD_OF_PHYS_T250            = 0    # Use the logical head instead of the physical head for the Delta BER check in T250/quickSymbolErrorRate. Roll under BF_0170875_470833_P_USE_LGC_HD_INSTEAD_OF_PHYS when checkin complete.
   BF_0173040_470833_P_FIX_SAS_SIC_T518_HEADER_ISSUES             = 0    # Newer initiator code changed how T518 returns mode sense page data. Now allows for both P518 and P000 tables with different headers (backwards compatible)
   BF_0174138_395340_P_FIX_RUN_WRONG_STATE_TEST_AFTER_PWL         = 0    # Update new "NEXT_STATE" value to objData when current state is skipped by StateTable option to help PWL at next state.
   BF_0176400_475827_P_ENABLE_ESLIP_AFTER_WRT_ZONE_RNG_SEQ        = 0    # Go to ESlip at the end of Write Zone Range Sequence to preclude failures in CUST_CFG
   BF_0177502_357260_P_USE_HD_PHYS_PSN_FOR_LUL_SCAN_COMPARE       = 0    # Compare HD_PHYS_PSN, not HD_LGC_PSN for LUL flawscan compare (potential depop issue)
   BF_0184722_357260_TRACK_CLEANUP_USE_ONLY_LOG_HD                = 0    # Fix CTrackCleanup() to use HD_LGC_PSN only
   BF_0187702_340210_SNGL_HTR_2_PASS                              = 0    # 2 pass for single heater to mimic using read preheat
   BF_0188304_340210_SUPPRESS_UNLOCK_IN_SIC                       = 0    # unlock key suppressed in echo back
   FE_0184418_357260_P_USE_TRACK_WRITES_FOR_CLEANUP               = 0    # Perform track writes for TRACK_CLEANUP (vs LBA writes)
   FE_0187241_357260_P_USE_BAND_WRITES_FOR_CLEANUP                = 0
   FE_SGP_81592_RETRY_DURING_TRACK_CLEANUP_4_CHS_MODE             = ( 0 & FE_0184418_357260_P_USE_TRACK_WRITES_FOR_CLEANUP )
   FE_0254235_081592_ADDING_RETRY_WITH_PWRCYC_IN_SMR_TRACK_CLEANUP = ( 0 & FE_0187241_357260_P_USE_BAND_WRITES_FOR_CLEANUP )
   FE_SGP_81592_ENABLE_FLEX_BIAS_CAL_T136_IN_MDWCAL               = 0
   FE_SGP_81592_MOVE_MDW_TUNING_TO_SVO_TUNE_STATE                 = 0    # Split MDW_CAL into 2 state(SVO_TUNE state), end after calling enableFaskSeekMode
   FE_SGP_COLLECT_SVOAGC_AT_ID                                    = 0    # Flag to run Test 83 during MDW_CAL
   FE_SGP_REPLACE_T152_WITH_T282                                  = 0    # Flag to replace calling Test 282 for BODE plot instead of Test 152
   FE_SGP_ENABLE_BIAS_CAL_SCREEN_VIA_TEST136                      = 0    # Flag to enable abnormal bias profile screening via test 136 in servo opti cal
   FE_AFH_TO_USE_DC_DETCR_ONLY                                    = 0
   FE_0274637_496738_P_DC_DETCR_DSA_CONTACT_DETECTION             = 0
   FE_0278186_496738_P_WRT_CUR_REDUCTION_TO_AVOID_STE             = 0
   FE_0309927_228373_TWO_TEMP_T189_IMPLEMENTATION                 = 0    # Two-T189 for Temperature Dependent Radial Timing Implementation
   FE_0349167_228373_T189_MULTI_PRE2_CRT2_COMPARISON              = 0    # Compare T189 multipliers at PRE2 vs CRT2 in CRT2
   FE_0341704_340866_BODE_SCREEN_IN_CRT2                          = 0    # Run T282 bode screen in CRT2
   FE_0325684_340866_SHOCK_SENSOR_SCREEN                          = 0    # Shock sensor screen in T180
   FE_0335634_228373_WHOLE_SURFACE_SCAN_IN_SNO                    = 0    # Whole surface scan (4% - 99%) in SNO_PHASE 
   FE_0338894_357001_T257_TEST_BY_DISC                            = 0    # Perform WIRRO T257 measurement by disc
   FE_0362477_228373_T180_RESONANCE_RRO_SCRN_CRT2                 = 0    # T180 Resonance RRO Screen in CRT2
   FE_305538_P_ENABLE_CTF_IN_SERIAL_FORMAT                        = 0    # Enable CTF before serial format and revert back after (with power cycle)
   FE_305538_P_CHANGE_OCLIM_IN_SERIAL_FORMAT                      = 0    # Change OCLIM before serial format and revert back after (with power cycle)

   ################# SDAT RELATED #################
   BF_0124078_347508_PHARAOH_MASS_PRO_ADG_SETUP                   =   0   # Use Pharaoh mass PRO ADG settings
   BF_0132740_336764_DEL_P250_TBL_AT_READ_SCRN_OF_HDSTR_FLOW      =   0   # Delete P250_ERROR_RATE_BY_ZONE table at CAL2 HDSTR flow
   BF_0144381_336764_KEEP_LATEST_BER_IF_RE_TEST_PERFORM           =   0   # Keep the latest BER value if T250 retest at same SPC ID
   BF_0149507_010200_SDAT_READ_SYMBOL_TABLE_CONST                 =   0   # Fix all "Read Constant" T11 calls to use ACCESS_TYPE = 0 (avoids reading invalid memory addresses)
   BF_0171907_470833_IGNORE_SDAT2_IN_PROQUAL_CHK                  =   0   # Ignore SDAT2 during the proqual check if it is in the operList
   FE_AFH3_TO_IMPROVE_TCC                                         =   1 #
   FE_AFH3_TO_SAVE_CLEARANCE_TO_RAP                               =   0 #
   FE_AFH4_TO_USE_TWO_ZONES_TCC                                   =   0 #
   FE_0295624_357595_P_FE_357595_HIRP_MOVE_TO_AFTER_AFH2          =   0
   FE_AFH_RSQUARE_TCC                                             =   0 #
   ################################################

   CACHE_TABLEDATA_OBJ                                            =   0   # Return cached tableDataObj vars if valid nominally there is a 0.4% CPU improvement
   CCT_RandomReads                                                =   0
   CCT_SPC_BREAKOUT                                               =   0
   CheckAverageQBER_Enabled                                       =   0
   DATA_COLLECTION_ON                                             =   0   # switch to control all the data collection switches for SP programs
   DBLOG_coherency_Errors                                         =   0   # Enables printing of message "Error in data coherency! Aborting DBLOG" when there is a table column mismatch in dblog
   DECGAIN_OPTI                                                   =   0   # Save optimized DECGAIN Values
   DIAG_POWER_CHOP_ENABLED                                        =   0   # Leave power chop on in diag mode
   DISABLE_EXT_MODE_CMDS_IN_CMD_SET                               =   0   # Disable extended mode commands in command set testing
   DISABLE_POSTCMT2_GOTF_CHK                                      =   0
   DISABLE_T250_SER_ZAP                                           =   0 # Disable T250_SER_ZAP : Enable zap for T250 test tracks pre-zap execution
   DUMP_SERVO_SYMBOL_TABLE_T159                                   =   0
   DeltaBER_Disabled                                              =   0   #Disable delta BER
   DeltaVGA_Enabled                                               =   0   # Enable delta vga screening in Read_Scrn2
   Depop_On_The_Fly                                               =   0
   DoODParticleSweepActions                                       =   0   # Keep as 0 for LUL Products, CSS products may want to set to 1.
   ECWIN_OPTI                                                     =   0   # Save optimized ECWIN Values
   EO_WRT_FULL_RD_FLAWSCAN                                        =   0   # Even odd flawscan with 1 read pass verification
   EVEN_ODD_FLAWSCAN                                              =   0   # enable T109 Even/Odd Flawscan
   FULL_INTERLACE_FLAWSCAN                                        =   0   # enable T109 Even/Odd Flawscan + threshold opti
   EnableDebugLogging                                             =   0
   ENABLE_FAFH_STATE_CHECKING                                     =   0
   FAIL_FOR_MDW_SN_VOST_UNAVAILABLE                               =   0
   FAIL_HSA_PN_INVALID                                            =   0   #Fail the drive if the HSA_PN is invalid and/or AAB support isn't available for this drive
   FAIL_IF_NO_LBA_INFO_FOR_PARTNUMBER                             =   0   #Fail if LBA isn't found in TP override or DCM
   FAIL_INVALID_PIF_REGEX                                         =   0
   ENABLE_FLAWSCAN_BEATUP                                         =   0   # Enable Flaw scan beat-up test to improve Relia GMD.
   ENABLE_T109_FINE_TUNE_THRESHOLD                                =   0   # Enable T109 fine-tune threshold.
   FE_0241396_505235_FLAWSCAN_POWER_LOSS_RECOVERY                 =   0   # Power loss recovery for data flaw scan
   FE_0329412_340866_STRESS_CHANNEL_DURING_FLAW_SCAN              =   0   # During flaw scan state tighten channel setting
   TOPAZ_DRZAP_ENABLE                                             =   0   # TOPAZ and DRZAP

   FE_0110380_231166_USE_SETBAUD_NOT_POWERCYCLE_TO_VERIFY_DOWNLOAD_READY = 0 # Use a setBaud not power cycle to verify drive ready for next dl segment
   FE_0110517_347506_ADD_POWER_MODE_TO_DCM_CONFIG_ATTRS           =   0   #Keep drive in POIS during DL.  Add feature to reset POIS after DL if not specified in DCM
   FE_0110811_320363_DISABLE_SHOCK_SENSOR_IN_ZAP                  =   0   # Disable shock sensor during ZAP
   FE_0111302_231166_RUN_195_IN_SEPERATE_STATE                    =   0   # Disable 195 in read screen and enable full support in CHeadInstability state
   FE_0111448_357260_NO_SPINDOWN_UP_IN_DISPOWERCHOP               =   0   # Removes the 'Z'/'U' diag spin-down / spin-up from disPowerChop()
   FE_0111498_399481_NO_T212_IN_PARTICLE_SWEEP                    =   0   # Replace T212 in particle sweep with  T30 actions.
   FE_0111521_399481_ARBITRARY_NUM_ZONES_IN_ENCROACH_MEASURE      =   0   # Arbitrary number of zones in CRdWRScreen.encroachmentMeasurement()
   FE_0111784_347506_USE_DEFAULT_OCLIM_FOR_FLAWSCAN               =   0   # Use default OCLIM for flawscan per Kyoumarrs request
   FE_0111872_347506_SEASERIAL_RECYCLED_PCBAS                     =   0   # Factory reported issues on recycled PCBA that seaserial fixed.  This is WO since IMG DL should accomplish what seaserial does but currently isn't
   FE_0110581_346294_OCLIM_SCALE_PRE2_CPESSCREENS_T33             =   0   # if = 1, then T33 pretest can set(larger)/restore OCLIM to reduce faults if high RRO..if PES_Scrn_OCLIM_Scaler defined..ie 1.5 = 150% of defaultOCLIM
   FE_0111141_007955_SERIAL_FMT_SET_SHOCK_SENSOR                  =   0   # disable/enable shock sensor before/after serial fmt
   FE_0111377_345334_RUN_T43_BEFORE_T189                          =   0   # run T43 before T189 per servo team
   FE_0112192_345334_ADD_T56_FOR_PZT_CAL                          =   0   # add T56 call for PZT cal and dual stage actuator
   FE_0112188_345334_HEAD_RANGE_SUPPORT_10_HEADS                  =   0   # Add capability to support 10 heads
   FE_0112213_357260_DISABLE_EAW                                  =   0   # Disable Test 234 EAW in CEAW_Screen and CWrite_Screens
   FE_0112289_231166_REMOVE_INEFFICIENT_RETRIES_IN_ESLIP_BAUD_RETRIES = 0 # Remove non-successfull retries in elsip baud negotiation
   FE_0112311_345334_ADD_SERVO_SPINUP_BEFORE_T56                  =   0   # Servo team has requested adding servo spinup before PZT cal
   FE_0111183_340210_SAT_FAIL_MINIMAL_RETRY                       =   0   # handle saturation failures without failing
   FE_0112376_231166_RAISE_11049_EC_WITH_CFLASHCORRUPTEXCEPTION   =   0   # Raise 11049 EC with CFlashCorruption exception so it can be handled appropriately
   FE_0112719_399481_ADD_T126_DATA_TO_DATAFLAWSCAN_TASCAN         =   0   # Add T126 to CDataFlawScan.runTAScan more data for FA
   FE_0112728_357260_RUN_T193_IN_REAL_MODE                        =   0   # Move the T47 'Go Virtual' call to follow T193 so T193 runs in 'Real' mode
   FE_0112760_399481_POWER_CYCLE_AFTER_SET_HEAD_SUPPLIER_IN_SAP   =   0   # Use if SAP fails to update without a power cycle.
   FE_0112851_007955_ADD_HWY_OPTION_TO_SETSAP_HEADTYPE            =   0   # Ability to set SAP bit for HWY hds
   FE_0112902_007955_ISOLATED_PARSE_MILLIONW_PREDICTIN_TABLE      =   0   #Iso parse the millionw_predictin table to reduce RAM overhead
   FE_0113059_357260_APPLY_IVBARZAP_TO_OPTIZAP                    =   0   # Use single T175 call for OptiZap - ala VbarZap
   FE_0113230_345334_REENABLE_DUAL_STAGE_AFTER_SNO_NOTCHES        =   0   # Re-enable dual stage actuator after sno notch
   FE_0113445_347508_RUN_MULTIPLE_MANUAL_GOTF_TABLES              =   0   # Add support to run Pharaoh and Hepburn manual_GOTF tables in same PF3 package
   FE_0113902_345334_SAVE_SAP_WHEN_CHANGING_DUAL_STAGE            =   0   # Save the SAP when Dual stage is changed so it will remain enabled on power on reset
   FE_0114266_231166_INTERPOLATE_SINGLE_ZONE_FAILED_VBAR_MEASURES =   0   # Interpolate failed vbar measurements
   BF_0122926_231166_FIX_DRV_COMP_TRK_NON_PRIME                   =   0   # DRV_COMP_TRK only has P=Prime and R= Rework. L == Rework/recycle so replace
   FE_0114521_007955_WRITE_WWN_USING_F3_DIAG                      =   0   # Write WWN using F3 diag 'J' cmd
   FE_0114584_007955_DISABLE_WRITE_WWN_IN_SETFAMILYINFO           =   0   # Disable writing WWN early in process... if using WRITE_WWN_USING_F3_DIAG via lCAIDS : WRITECAPWWN
   BF_0119055_231166_USE_SVO_CMD_ZAP_CTRL                         =  (0)   # Use servo cmd FF instead of sap shadow variable to control ZAP ERO state
   FE_0114310_340210_ZONE_GRPS_4_TRIPLETS                         =   0
   FE_0120024_340210_ATI_IN_WRT_PWR_PICKER                        =  (0 & FE_0114310_340210_ZONE_GRPS_4_TRIPLETS)
   FE_0121867_340210_ATI_WRT_PWR_REMEASURE_BY_HD                  =  (0 & FE_0120024_340210_ATI_IN_WRT_PWR_PICKER)
   FE_0115422_340210_FORMATS_BY_MARGIN                            =   0   # for experiemental runs only - running format picker based on margins only
   FE_0116041_357260_USE_TP_PARAMS_FOR_PARTICLE_SWP               =   0
   FE_0116041_357260_NO_READS_AT_END_OF_PARTICLE_SWP              =   0
   FE_0116185_357260_ENABLE_SWD_DURING_SERVO_FS                   =   0   # Moves SWD Disable to after runAdjacentServoFS()
   FE_0116390_405392_USE_TP_PARAMS_FOR_AGITATION_SCRN             =   0
   FE_0116390_405392_USE_TP_PARAMS_FOR_UPDATE_MQM_REV             =   0
   FE_0116894_357268_SERVO_SUPPLIED_TEST_PARMS                    =   0   # Enables feature to accept test parameter overrides from servo package
   FE_0117013_399481_DO_IDENTIFYDEVICE_BEFORE_DOWNLOAD            =   0   # Do identify device before download attempt.
   FE_0117022_399481_REENABLE_CRC_RETRIES_FOR_FULL_PACK_WRITE     =   0   # Reenable CRC retries in full pack write.
   BF_0122749_231166_FIX_CRC_RETRIES_PRINT                        =  (0 & FE_0117022_399481_REENABLE_CRC_RETRIES_FOR_FULL_PACK_WRITE )   # Fix bug in FE_0117022_399481_REENABLE_CRC_RETRIES_FOR_FULL_PACK_WRITE that caused TypeError due to cpc ret type
   FE_0117027_399481_ENABLE_WRITE_CACHE_IN_PACK_WRITE             =   0   # Enable Write Cache in Pack Write.
   FE_0117031_007955_CREATE_P186_BIAS_CAL2_MRE_DIFF               =   0   # Table containing MR resistance difference values for GOTF purposes.
   FE_0116900_399481_ATTEMP_UNLOCK_F3_DNLD                        =   0   # Attempt unlock when unlock_m.lod is available.
   FE_0117296_357260_SUPPORT_SECOND_MR_CALL_AND_DIFF              =   0   # New CCalibrateMRRes() PARAMS: DIFF_MR_RESULTS (perf. diff./check) and SAVE_TO_SIM (Save new results to SIM)
   FE_0117758_231166_NVCACHE_CAL_SUPPORT                          =   0   # Add support for NVCache
   FE_0117973_341036_AFH_BETTER_FRAMES_DISPLAY_OPTION             =   0
   FE_0118039_231166_SEND_CPC_VER_AS_ATTR                         =   0   # Send CPC Version to attribute system
   FE_0118213_399481_SET_VE_SERIAL_NUMBER_BY_PART_NUMBER          =   0   # Use a dict of PN pats to pick a matching serial number for VE to better test waterfall.
   FE_0118405_357260_RUN_SECOND_T195_IN_READ_SCRN                 =   0   # Adds a second, unique T195 call in READ_SCRN
   FE_0118648_231166_ADD_NVC_TIMING_CAL                           =   0   # Calibrate the NVC timing
   FE_0118679_231166_NVC_SEQ_REV2                                 =   0   # Rev 2 of the sequence from Mike Baum
   FE_0188555_210191_NVC_SEQ_REV3                                 =   0   # Rev 3 of the sequence from Nicolai Ramier
   FE_NVC_SEQ_REV4                                                =   0   # Rev 4 of the sequence from Munkai Lye
   DISABLE_NVCACHE_WHILE_TESTING                                  =   0   # To disable NVCACHE while testing
   FE_0280862_385431_ENABLE_NVCACHE_INIT                          =   0   # To enable NVCACHE_INIT for Hybrid drive
   FE_0118167_405392_RESET_RELIABILITY_ATTRIBUTE_TO_NONE          =   0   # Reset reliability attributes to NONE
   FE_0118779_357260_SAVE_SLIST_IN_ZAP                            =   0   # Add to repServoFlaws() call in CZap() to save servo flaw table
   FE_0118796_231166_OUTPUT_PF3_BUILD_TARGET                      =   0   # Add build target output to results file
   FE_0118821_231166_USE_PGM_LVL_VOST_DEFAULT                     =   0   # Use a program level default for TPI in VOST
   FE_0118805_405392_POWER_CYCLE_AT_FAILPROC_START                =   0   # PowerCycle at beginning of CFailProc() to prevent adjacent drive fail at IO cell if timeout failure occuring
   FE_0119988_357260_MULTIPLE_T50_ZONE_POSITIONS                  =   0   # Allow T50 to be run at multiple positions per zone
   FE_0120496_231166_DISABLEZAP_IN_MDWCALS                        =   0   # Add call to disable zap in flash at beginning of mdw_cals- ** Most programs shouldn't need this
   FE_0120498_231166_DISABLE_SWD_IN_FORMAT                        =   0   # Disable swd during serial format
   FE_0120663_347508_ADD_SETOPERLIST_FOR_ST240                    =   0   # Add function to setoperlist
   FE_0120910_347508_ADD_FILL_AND_WRITE_SMART_IN_WRITESMARTDATA   =   0   # Add fill and write read to writeSmartData
   FE_0120911_347508_DRAMSCREEN_CLEANUP                           =   0   # Add DramScreen Cleanup
   FE_0120913_347508_FAIL_STATE_INFO_CHANGES                      =   0   # Pharaoh Fail state info changes
   FE_0120918_347508_ATTRIBUTE_LOADING_REDUCTION                  =   0   # CMT and AUD attribute loading reduction
   FE_0121012_399481_SUBSTRING_MATCH_MQM_OK_ERRORS                =   0  and FE_0139481_395340_P_MQM_TEST_ON_NEW_SPSC2_OPER # MQM, support OK sense code substring matches instead of full string matches.
   FE_0121130_231166_ALLOW_AUTO_RERUN_VBAR                        =   0   # Allow the 13409 auto-vbar rerun state transition
   FE_0121254_357260_SKIP_T163_IN_READ_SCRN                       =   0   # Skip the T163 calls in CReadScreen
   FE_0121272_399481_RESTORE_PHUGR                                =   0   # Add restorePHUGRToValThree function to serial format.
   FE_0121280_399481_UPDATE_TO_MEDIA_SYNC_DEFECT_SCREENS          =   0   # Add s1 command to media sync defect screens, and remove ,,,2 portion of I command.
   FE_0121797_341036_AFH_USE_T109_FOR_TEST_135_TRACK_CLEANUP      =   0   # Use test 109 to write customer zeroes in AFH 4 for test 135 track clean-up
   FE_0121885_399481_ALLOW_SPC_ID_TO_BE_SET_BY_CALLER_IN_DISPLAY_G_LIST = 0 # Allow for unique spc_id's in CDisplay_G_list.
   FE_0164115_340210_SMART_FH_WRT                                 =   0   # SMART FH track prep
   FE_0175466_340210_DIAG_UNLOCK                                  =   0   # Diag unlock

   # Below Requires extern.FE_0111342_231166_10_HEAD_SUPPORT and
   # extern.FE_0115432_231166_ADD_APPEND_TO_SPT_RESULTS_FILE_IN_231
   FE_0120780_231166_F3_SPT_RESULTS_ACCESS                        =   0   # Support for extracting SPT_DIAG_RESULTS data from F3 diagnostics
   FE_0000131_231166_GOTF_REGRADE_SUPPORT                         = ( 0 ) #GOTF regrade support. Turn on FE_0120780_231166_F3_SPT_RESULTS_ACCESS and F3/SF3 blockpoint flag SYS_DISC_ALLOC_INFINITY for support post F3 code download
   FE_0121286_231166_FTP_GOTF_PARAMETRIC_FILE                     = ( 1 & FE_0120780_231166_F3_SPT_RESULTS_ACCESS ) #FTP GOTF file for later re-analysis
   FE_0121886_231166_FULL_SUN_MODEL_NUM                           =   0   # Add support for SUN_MODEL_NUM in full form "SEAGATE 'MODEL' YYWW 'modelcode'"
   FE_0121994_399481_REPORT_BER_DATA_BY_HEAD_IN_MQM               =   0
   FE_0122102_399481_GET_CRITICAL_EVENTS_AFTER_G_LIST             =   0   # Show critical event log after display of g list to help identify cause of alt list entries, if any.
   FE_0122125_7955_DISABLE_OPTIZAP_RUN_BEFORE_T250                =   0
   FE_0122163_357915_DUAL_STAGE_ACTUATOR_SUPPORT                  =   0   # Enable dual stage actuator support
   FE_0122180_357915_T150_DISABLE_UACT                            =   0   # Disable the microactuator for calls to T150 on dual actuator drives
   FE_0122186_354753_SUPPORT_FOR_SAS_REVISIONING                  =   0   # Can be enabled for both SATA and SAS - code will determine if SATA or SAS based on drive attributes.  Feature is required for SAS drives to correctly determine the code version name.
   FE_0122225_399481_STRIP_TRAILING_WHITESPACE_IN_ATTRIBUTE_COMPARE = 0   # Strip trailing whitespace from attributes in ATTR_VAL, for comparison only.
   FE_0123391_357915_DISABLE_ADAPTIVE_ANTI_NOTCH_UNTIL_AFTER_ZAP  =   0   # Disable servo's adaptive anti-notch functionality until full-disc ZAP is finished
   FE_0123556_405392_PERFORM_ZERO_WRITE_AFTER_ALT_SECTOR          =   0   # Perform zero write after alt sector if alt list entries.
   FE_0123723_399481_MR_BIAS_BACKOFF_T62_IN_VBAR                  =   0
   FE_0123768_426568_OUTPUT_SERVO_COUNTERS_DURING_FLAWSCAN        =   0   # Outputs Servo parameters during flawscan
   FE_0123777_399481_DO_NOT_FAIL_AUDIT_DRIVES_FOR_GOTF            =   0
   FE_0123775_220554_ENABLE_RPS_SEEK_T237_PF3_SUPPORT             =   0
   FE_0123752_405392_WRITE_WWN_ENHANCEMENT                        =   0   # Allow 6 digits part number to enable/disable writing WWN
   FE_0123872_399481_MQM_AUDITTEST_SKIP_INCOMPATIBLE_PARTS        =   0
   FE_0123983_399481_SNO_IN_MDW                                   =   0
   FE_0124220_426568_RUN_THIRD_T195_IN_READ_SCRN                  =  (0 & FE_0118405_357260_RUN_SECOND_T195_IN_READ_SCRN )   # runs a third Test 195 call in Read_Scrn
   FE_0124492_399481_SINGLE_T252_CALL_IN_COLD_WRITE_SCREEN        =   0   # Set T252 TEST_HEAD and ZONE to 0x00FF and set ZONE_MASK to pick zones, ex. (0x2000, 0x8001) for 0, 15, 29.
   FE_0124554_399481_GET_BER_DATA_USING_LEVEL2_B_CMD              =   0   # Use 2>b command instead of online $ cmd to retrieve BER by zone data.
   FE_0124649_399481_SKIP_MODEL_NUMBER_HANDLER_BY_PN              =   0   # Skip CSetDriveConfigAttributes.handleModelNumber() for part numbers matching regex found as values in TP.Skip_Model_Number_Handler dict.
   FE_0124846_357915_SWOT_SENSOR_SUPPORT                          =   0   # Enable process SWOT sensor SAP bit manipulation, by default this will clear the servo SWOT sensor SAP bit
   FE_0124846_357915_ENABLE_SWOT_SENSOR                           =  (0 &  FE_0124846_357915_SWOT_SENSOR_SUPPORT)   # Set the Servo SAP SWOT-sensor-enabling bit
   FE_0124378_391186_HDSTR_CONTROLLED_BY_FILE                     =   0   # uses input file for HDSTR operations instead of part numbers
   FE_0124465_391186_HDSTR_SHARE_FNC_FNC2_STATES                  =   0   # shared FNC and FNC2 states [Muskie uses this, Pharaoh does not]
   FE_0124468_391186_MUSKIE_HDSTR_SUPPORT                         =   0   # Any other needed changes to support Muskie HDSTR operation
   FE_0124728_357915_FULL_WRT_EO_RD_FLAWSCAN                      =   0   # Flawscan using a full pack write and the even-odd scheme for reads
   FE_0125416_357915_ENABLE_ATS_CALIBRATION                       =   0   # Enable Anticipatory Track Seek calibration (T194) after ZAP
   FE_0125501_357915_PRINT_WWN_FAILURE_INFO                       =   0   # Output additional failure and help information when WWN retrieval fails
   FE_0125530_399481_T250_RETRY_TO_IGNORE_BANDS_WITH_P_LIST_ENTRIES = 0
   FE_0125562_405392_DISABLE_ALL_DEBUG_IF_CELL_NOT_RESPONSE       =   0   # Disable all debug in class CFailProc() to protect adjacent drive failed in case of cell not respond
   FE_0125564_405392_INIT_RIM_PRIOR_TO_POWER_CYCLE                =   0   # Re-Initializing Rim to restorable the cell in case of cell not respond (maybe take a long time)
   FE_0126095_405392_FORCE_CHECK_PCBA_CYCLE_COUNT                 =   0
   FE_0126187_340210_DRIVE_ATTR_CRITERIA                          =   0  # Use HGA supplier/num heads and other drive attributes as criteria
   FE_0125707_340210_CAP_FROM_BPIFILE                             =   0  # Read nominal capacity from bpifile
   FE_0126442_357552_OUTPUT_SERVO_COUNTERS_AFTER_FLAWSCAN_READPASS =  0  # Clear before, dump servo counters after T109 flawscan read pass
   FE_0127082_426568_USE_FREEZE_RESTORE_FOR_ADAPTIVE_ANTINOTCH    =   0  # replace disable/enable of Adaptive Anti-notch in Cert by freeze/restore of Adaptive Anti-notch
   FE_0127664_395340_DISPLAY_LOG_INFO_GLIST_ON_FAIL_LONG_DST      =   0  # Display log information of GLIST after Long DST fail
   FE_0127824_341036_AFH_DISABLE_WHIRP_NOT_CT_ACCESSIBLE          =   0
   FE_0128496_405392_WRHEAT_TWEAK_IN_WEAK_WRITE_TEST              =   0  # Set temperature to 70C and disable write power tweak in weak write test
   FE_0129689_220554_SUPPORT_P_DIAG_PARAMETERS                    =   0  # Add parameters support to 'P' diagnostic command
   FE_0130770_341036_AFH_FORCE_SAVING_AFH_SIM_TO_DRIVE_ETF        =   0  # AFH force save AFH SIM data to drive ETF
   FE_0130771_341036_AFH_FORCE_USE_AFH3_AND_AFH4_IN_TCS_CALC      =   0  # Force using AFH3 and AFH4 data in TCS calculation
   FE_0131531_357915_SPC_ID_IN_STATE_PARAM_FOR_CHEADINSTABILITY   =   0  # Allow the SPC ID for the T195 call in CHeadInstability to be passed in through state param's
   FE_0131646_357915_ALLOW_FAILURE_WHEN_RUNNING_MULTIPLE_T50_ZONE_POS = 0  # Add the ability to fail a specified number of T50 calls for 10482 errors in a given zone when FE_0119988_357260_MULTIPLE_T50_ZONE_POSITIONS is set.
   FE_0131890_341036_AFH_ADD_FOLDING_OF_TCS_CALC                  =   0
   FE_0132647_336764_ADD_T208_TO_FAILPROC                         =   0  # T208 test at FailProc at Serial Port
   FE_0132880_7955_CREATE_P597_SPEC_LIMIT_TABLE                   =   0  # for use with GOTF
   FE_0132889_7955_CREATE_P598_ZONE_DATA_RATE_TABLE               =   0  # for use with GOTF
   FE_0143811_357263_ADD_IPD3                                     =   0 # Use IPD3
   FE_0158916_357263_AGC_BASELINE_JUMP_DETECTION                  =   0 #
   FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT     =   0
   FE_0134030_347506_SAVE_AND_RESTORE                             =   0  #Save state restore points and set drive back to state restore point.  Enable looping of states
   FE_0135028_426568_CLEAR_MODE_PAGES_FOR_SATA                    =   0  # Reset the mode pages for SATA drives
   FE_0138033_426568_P_SET_ZERO_PTRN_RQMT_IN_PACKWRITE            =   0  # sets zero pattern requirement
   FE_0163083_410674_RETRIEVE_P_VBAR_NIBLET_TABLE_AFTER_POWER_RECOVERY  = 0 #Retrieve P_VBAR_NIBLET table after power recovery
   FE_0164322_410674_RETRIEVE_P_VBAR_TABLE_AFTER_POWER_RECOVERY   =   0  #Retrieve VBAR table after recovery (VBAR_FORMAT_SUMMARY, VBAR_HMS_ADJUST, WRT_PWR_PICKER and WRT_PWR_TRIPLETS)
   FE_0203247_463655_AFH_ENABLE_WGC_CLR_SETTING_SUPPORT           =   0   # Save WGC (Write Gate Count) value to RAP
   FE_0207956_463655_AFH_ENABLE_WGC_CLR_DATA_COLLECTION           =   0
   FE_0207956_463655_AFH_ENABLE_WGC_CLR_TUNING                    =   0
   ################# SDAT RELATED #################
   FE_0115640_010200_SDAT_DUAL_STAGE_SUPPORT                      =   0   # Adds uActuator structural bode, and Single / Dual Stage control for all bode tests
   WA_0115641_010200_DISABLE_OL_BODE_ON_DUAL_STAGE                =   0   # Temporary work-around: Use single rate open loop bode on dual stage products - This will be replaced with T288
   BF_0121115_010200_REMOVE_UNNECESSARY_T150_CALLS_IN_SDAT        =   0   # Removes frequency iteration loop from SDAT Lin Cal calls if PDF method is used
   FE_0126858_010200_SDAT_ROBUSTNESS_IMPROVEMENTS                 =   0   # Switch to T288 for all bode measurements, and open up OCLIM for PES collection in Track Follow
   FE_0159886_350037_IMPROVE_ZAP_STATE_CHANGE                     =   1   # Improve Zap state change call.
   FE_0163871_336764_P_DO_LOGPOWERON_AFTER_COMPLETE_FULL_PWC_RETRY  = 0   #Move logpoweron after complete all power cycle retry

   ################################################

   FE_0118875_006800_RUN_T109_MSE_SCAN                            =   0   # T09 MSE scan enable
   FE_0111793_347508_PHARAOH_TTR                                  =   0   # Pharaoh Specific Test Time reductions
   FE_0119998_231166_FACTORY_VBAR_ADC_ENHANCEMENTS                =   0   # Integrate factory ADC enhancements from Pharaoh launch
   FE_0121834_231166_PROC_TCG_SUPPORT                             =   0   # Full TCG security support
   FE_0199808_231166_P_SEND_MSID_TO_FIS                           =   0
   TCGSuperParity                                                 =   0   # Super Parity
   NSG_TCG_OPAL_PROC                                              =   0   # For TCG Opal, use this flag to denote NSG specify change
   PROC_TCG_SKIP_END_TESTING                                      =   0   # For TCG, skip end testing
   FE_0225282_231166_P_TCG2_SUPPORT                               =   0   # Add support for tcg2.0 f3 code
   NO_POWERCYCLE_BEFORE_AND_AFTER_UPDATECODEREVISION              =   0
   FE_0234883_426568_P_IEEE1667_SUPPORT                           =   0   # Support to enable or disable IEEE 1667 Port in SED functionality
   SET_IEEE_1667_DEACTIVATED_IF_SDND_AND_NA                       =   0   # Support to set IEEE 1667 Port for SDnD to 'DEACTIVATED' if NA/None
   PROC_TCG_SIMPLIFIED_EBC                                        =   1
   FE_0280070_385431_HunderedPercentSecuredDrive                  =   1   # 100% secured drive
   FE_0246029_385431_SED_DEBUG_MODE                               =   0   # Debug mode for non production, which will not re-personalize for re-FIN2
   IS_SDnD                                                        =   0   # DO NOT CHANGE: SdnD drive support - This one for debugging or manual trigger only. Auto trigger SDnD personalization based on 'SECURITY_TYPE'= 'SECURED BASE (SD AND D)'.
   FE_0241189_231166_P_NEW_TDCI_API_RETRIES                       =   0   # Enable use of new TDCI api from host as well as retry scheme
   FE_0385431_MOVE_FINAL_LIFE_STATE_TO_END                        =   0   # Change the SED/SDnD lifestate to "USE" at the end
   FE_0385431_SED_ACTIVATION                                      =   0   # To enable activation
   FE_0267840_440337_P_SERIAL_PORT_AUTO_DETECT                    =   0   # Add support for Activation on Secure Drives
   Kwai_CSPCard_Enabled                                           =  (0 & FE_0121834_231166_PROC_TCG_SUPPORT ) # Support the CSPCard authentication
   FE_0122298_231166_ASCII_DEBUG_FIRST_BAUD_CMD                   =   0   # Use ascii debug retry as the initial baud negotiation function as it has a higher success rate for PS programs.
   #FE_0122328_231166_ALLOW_STATE_PRM_IGNORE_ATA_READY             =   0   # Allow state table inputs to ignore ata ready failures for init and downloaducode
   FE_0123282_231166_ADD_SWITCH_CONTROL_TO_STATE_TABLE            =   0   # Allow inputs at state table options of switches to control if state is executed
   OEM_Waterfall_Enable                                           =  (0 & FE_0119998_231166_FACTORY_VBAR_ADC_ENHANCEMENTS ) #Setting that allows waterfall of OEM
   FE_0000103_347508_ENABLE_ZERO_CHECK                            =   0   # Add testswitch to enable zero check
   FE_0000127_347508_ADD_CRCERRORRETRY                            =   0   # Add Extra CrcErrorRetry
   FE_0000132_347508_PHARAOH_WRITE_MOBILE_MODIFICATION            =   0   # Pharaoh Write Mobile Mod to use Icmd.WriteTestSim2
   FE_0122823_231166_ALLOW_SWITCH_REFS_IN_TP                      =   0   # Allow switch refs in Test Parameter resolution
   FE_0122824_231166_ADD_LATENT_SETUP_TO_DUT                      =   0   # Add late setup to DUT settings for extern references
   FE_0122938_231166_FAIL_IF_ZGS_REQ_BY_PN                        =   0   # Fail if optionsByPN_re has ZGS set to 'enabled' and the drive doesn't have a validly calibrated ZGS sensor
   FE_0123153_7955_MEASBER_SET_ZAP_THRU_STATE_PARAMS              =   0   # Ability to turn zap on/leave off at start/end of CMeasureBER
   FE_0130958_336764_ADD_T186_TO_FAILPROC                         =   0   # Add T186 to fail proc
   FE_0124012_231166_ALLOW_PF3_UNLK_CODE_ACCESS                   =   0   # Allow use of pf3 global unlock code
   FE_0124304_231166_FAIL_IF_NO_FLAG_FILE_FOUND                   =   0   # Fail if process can't ID the code on the drive to load the extern flags- also provid permuation based code lookup
   FE_0124433_357552_RUN_GMR_RES_NO_DEMOD                         =   0   # Frequent GMR Resistance measurements good for detecting instability or bi-stable heads
   FE_0124358_391186_T250_ZONE_SWEEP_RETRIES                      =   0   # Changes to improve robustness of T250 pre-ZAP/flawscan [due to not finding a suitable test location in zone]
   FE_0124984_357466_ENABLE_END_OPER_PLUGINS                      =   0   # Enable END operation specified with PF3 plugin files
   FE_0125480_231166_ALLOW_SKIP_INVALID_XFER_SETTINGS             =   1   # Allow skipping the set xfer rate modes that aren't supported based on previous attempts in initiator cell
   FE_0125484_231166_ADD_INIT_PWRON_COMM_RETRIES                  =   0   # Add retries to set baud rate for initiator
   FE_0125503_357552_T33_RVFF_OFF_AND_ON                          =   0   # Run T33 with RVFF OFF and ON
   FE_0126515_399481_WRCUR_TWEAK_IN_FSE_SCREEN                    =   0
   FE_0126871_231166_ROBUST_PCK_COMP_SEARCH                       =   0   # Use a method to identify the components of the BID, BT, CL are in a manifest name by splitting on '.' as opposed to regex
   FE_0127049_231166_CONV_PCKG_ITEMS_NUMBERS                      =  (0 &  FE_0126871_231166_ROBUST_PCK_COMP_SEARCH ) # Convert any integers to true integers to get rid of 00's if there or any formatting gems
   FE_0126994_7955_CREATE_P_DELTA_FB_PICK_TABLE                   =   0   # Table contents - for each head and zone, calculate FBPIC(WP=0) - FBPIC(WP=4) = deltaFBPIC
   FE_0127046_231166_DONT_SET_RIM_Q_ON_LAST_OPER                  =   0   # Don't set RIM_TYPE attribute to ? upon last operation running in sequence. If proqual disabled on automation line this could cause restart of drive in subsequen oven.
   FE_0127527_426568_STEPLBA_SET_BY_TEST_PARAMETER_IN_DOS_VERIFY  =   0   # Make stepLBA be set by a test paramter in CVerifyDOS
   FE_0127479_231166_SUPPRESS_INFO_ONLY_TSTS                      =   1   # Suppress output automatically for 504,507,508,514,538
   FE_0127531_231166_USE_EXPLICIT_INTF_TYPE                       =   0
   FE_0127688_399481_RAP_AFH_PREAMP_TWEAK_IN_FSE_SCREEN           =   0   # Allow FSE screen to change write current and write clearance for screen duration.
   FE_0127808_426568_SET_SWOT_BASED_ON_CONFIG_VAR_IN_CENABLESWOT  =   0   # only set the swot sensor in CEnableSWOT if the config var is set
   FE_0128343_231166_STEP_SIZE_SUPPORT_IF3                        =   0   # Enable support for STEP_LBA input to CPC like interface- STEP_SIZE in IF3 code
   FE_0128864_7955_DUMP_REGS_IF_FAIL_DURING_FPW                   =   0   # Dump registers ( CTRL I ),  if fail during SeqWrtDMAExt ( FULL_PACK_WRITE )
   FE_0128912_7955_CREATE_FORMAT_ZONE_ERROR_RATE_EXT_TABLE        =   0   # Create new table - P_FORMAT_ZONE_ERROR_RATE_EXT,   contains field  'BITSRDLOG10_MINUS_HARDERRRATE'  ( 2nd pass serial fmt only ) ( for GOTF criteria )
   FE_0129198_399481_BIE_THRESH_IN_ENCROACHED_WRITES              =   0   # Bits In Errors based defect detection in the Encroached Write Test
   FE_0129265_405392_SPECIAL_STATES_PLR                           =   0   # Fix power loss recovery for special state (COMPLETE, FAIL_PROC, FAIL)
   FE_0129336_405392_NO_EXCEPTIONAL_PASS_FROM_FAIL_PROC           =   0   # Don't let any drives fell into FAIL_PROC state pass because of exception condition. -> every drives failed
   FE_0129273_336764_ENABLE_MFG_EVAL_CTRL                         =   0   # Enable MFG_EVAL attribute control by CMS switch
   FE_0129491_357260_GENERATE_T234_CHUNK_DELTA_TABLE              =   0   # Create table P_234_BER_CHUNK_DELTA with EAW BER delta data calculated from P234_EAW_ERROR_RATE2
   FE_0129672_357260_DISPLAY_P152_BODE_SENSITIVE_SCORE_IN_LOG     =   0   # Dump the P152_BODE_SENSITIVE_SCORE table to the result file.
   FE_0130092_7955_FPW_ALLOW_1_RETRY_ON_FAIL                      =   0   # Allow 1 retry on Full Pack Write fail
   FE_0130184_399481_OPTION_TO_RUN_LONG_DST_AFTER_G_LIST_MERGE    =   0   # Run Long DST after merge in CCheckMergeGList if state param runLongDSTonMerge set to 1
   FE_0130200_231166_SAVE_ZAP_INCR_STATE_FOR_PLR                  =   0   # Allow advancing the zap head start based on the last head zapped for PLR
   FE_0130977_399481_ENCROACHED_SCREEN_VERIFY_ERRORS              =   0   # Adjacent reads/writes on tracks where odd/even flawscan finds errors.
   FE_0130984_231166_PWR_CYCLE_VER_DNLDUCODE                      =   0   # Add power cycle after successfull download ucode to help naviagte qnr and bridge transitions
   FE_0131136_426568_RUN_T199_TWICE_IN_READ_SCREEN                =   0   # Run test 199 two times after the end of test 195 in CReadScreen
   FE_0131335_220554_NEW_AUD_LODT_FLOW                            =   0   # New flow for running AUD/LODT. Please refer to the flow chart in teamtrack task TPE-0006885 for detail
   FE_0131622_357552_USE_T126_REPSLFAW_INSTEAD_OF_T130            =   0   # Use T126 to report Servo Flaw table instead of T130
   FE_0131647_357552_HACK_SECTOR_SIZES_INTO_RAP                   =   0   # USe Test 178 to write corrected sector sizes and LBA counts into RAP
   FE_0131794_426568_RUN_T25_BEFORE_T185                          =   0   # add a call to test 25 L/UL before calling test 185 for better ramp detection after excercising Head Stack
   FE_0132170_357915_USE_RETRY_PARMS_FOR_T51                      =   0   # Use retryParams in the zone loop for T51 ATI testing
   FE_0131249_231166_ASD_BUTTERFLY_PERF_SCRN                      =   0   # Add the ability to run the ASD butterfly performance screen in DVT_Screens::CASDPerfVerification
   FE_0132440_336764_CFW_DNLD_AT_FNC2_AND_SPSC2                   =   0   # Force CFW download at Failproc at FNC and SPSC2 operation
   FE_0132468_357260_AUTO_SEASERIAL_FOR_CHECKSUM_MISMATCH         =   0   # Add 38912 to list to attempt Auto-SeaSerial retry for download checksum mismatch events
   FE_0132730_336764_RE_WHOLE_PRE2_WHEN_POWER_TRIP_AT_MDW_STATE   =   0   # Re-test whole PRE2 if drive power trip
   FE_0132639_405392_CHANGE_ZONE_DATA_FROM_PHYCYL_TO_LOGCYL       =   0   # Change zones data returned from physical cylinders to logical cylinders in function getZoneInfo()
   FE_0132943_231166_DISABLE_HARD_RESET_DNLD_UCODE                =   0   # Disable the Hard Reset call prior to download ucode
   FE_0133029_231166_RAISE_MISS_DATA_EXC_PHAST_OPTI               =   0   # Refactor the phastopti retry and primary level 3 calls to use try/except to catch data missing exceptions and timeouts and raise those EC's directly.
   FE_0132082_231166_UPLOAD_PREAMP_REV                            =   0   # Append the PREAMP_REV to the PREAMP_INFO attribute
   FE_0133254_357260_CREATE_CLEARANCE_DELTA_TABLE                 =   0   # Create table hold clearance and DAC delta data
   FE_0133706_357260_T234_EAW_RETRY_SUPPORT                       =   0   # Add ability to retry limit based failures and re-apply limits
   FE_0133768_372897_DMAEXTTRANSRATE_TEST_WITH_T641               =   1   # Replace T550 with T641 for DMAExtTransRate test in SATA ICmd
   FE_0133918_357260_USE_RETRY_PARMS_FOR_T50                      =   0   # Use retryParams in the zone loop for T50 ATI testing
   FE_0133860_372897_ADD_PARA_TEST_FUNCTION_FOR_T528              =   0   # Add para 'TEST_FUNCTION': spinUpFlag for T528 in PowerControl.py for SI slot
   FE_0133958_357552_T149_MFGDATE_TO_ETF                          =   0   # Write DriveSN, WWN, Mfg Date to DIF file in ETF
   FE_0134083_231166_UPDATE_SMART_AND_UDS_INIT                    =   0   # Add smart init of head amp for SAS as well as clear uds functionality.
   FE_0133890_231166_VALIDATE_SHIPMENT_DEPENDANCIES               =   0   # Validate required states are executed in CUT2 to provide highest quality shipment possible.
   FE_0134462_399481_DUMP_V4_ALLOW_DIAG_NOT_TO_FAIL               =   0   # Allow dumpReassignedSectorList to pass raiseException value to senddiagcmd, in order to not fail if prompt missed, if for instance you only care about the header.
   FE_0134690_231166_ALLOW_DCAID_IN_CONTENT                       =   0   # Allow input of functions for customer content
   FE_0134776_357915_EO_WRT_EO_RD_FLAWSCAN                        =   0   # Split the write pass into an even track pass and an odd track pass, followed by a read pass of the same configuration.
   FE_0134747_336764_SEPARATE_SCRACHFILL_FROM_DFLAW_STATE         =   0   # Enable take out scrachfill from HDSTR process
   FE_0135314_208705_DELTA_BPIC_SCREEN                            =   0   # Enable screen for heads with high clearance sensitivity
   FE_0135432_426568_REMOVE_CALL_TO_RWK_YIELD_MANAGER             =   0   # Removes the call to rwkYieldManager to get rid of attributes 'DRV_COMP_TRK' & 'DRV_RWK_COMP'
   FE_0135930_231166_ADD_SMART_SRVO_ERR_SCRN                      =   0   # Add functionality to run a smart servo errror screen.
   FE_0139575_336764_SKIP_DSP_SCRN_IF_DRIVE_FAIL_AT_T109_PRE2     =   0   # Skip DSP screen and let it test at FNC2 for drive that fail at T109 PRE2
   FE_0136008_426568_WRITE_PCBA_PART_NUM_CAP                      =   0   # Add functionality to Write PCBA_PART_NUM to CAP
   FE_0136197_341036_AFH_SPECIAL_SPC_ID_FOR_STATE_AFH2B           =   0
   FE_0134422_336764_GIO_DYNAMIC_RIMTYPE_SUPPORT                  =   0   # Allow dynamic rimtype at GIO
   FE_0134715_211118_ENABLE_TEST_335                              =   0   # Enable MDW scan in test process
   WA_0151540_342996_DISABLE_TEST_103                             =   0   #Disable call to Test 103 until code is ported to F3 Trunk and 11153 error is resolved                                                                       #
   FE_0136598_341036_AFH_PRVNT_INDX_ERROR_P_135_FINAL_CONTACT     =   0
   FE_0136807_426568_P_BANSHEE_VSCALE_OPTI                        =   0   # This runs banshee VSCALE opti after regular simple OPTI
   FE_0136821_426568_P_DISABLE_SCRATCH_FILL_PADDING               =   0 and FE_0134747_336764_SEPARATE_SCRACHFILL_FROM_DFLAW_STATE  # This disables cratch fill padding in CDataFlawScan
   FE_0135882_409401_CONTINUE_T135_FROM_FAIL_DRIVE                =   0   # Keep on T135 testing in AFH state
   FE_0137099_220554_P_OTF_DELTA_SCRN_IN_FMT                      =   0   # Enable delta OTF screen in serial format
   FE_0137804_399481_P_BIE_SERIAL_FORMAT                          =   0
   FE_0137948_336764_RETEST_T50_WITH_ZONE_POSITION_141            =   0   # Enable retest T50 with new zone position 141
   FE_0138323_336764_P_T234_EAW_KOR_RETRY_SUPPORT                 =   0   # Enable T234 retry from Korat
   FE_0138325_336764_P_DISABLE_FLAW_TABLE_CHK_AFTER_RETRY_T50_T51 =   0   # Enable auto retry T5051 with disable flaw table check
   FE_0138491_231166_P_BYPASS_UNLK_FOR_TGTP_ON_DUT                =   0   # Bypass UNLK download if TGTP already on drive.
   FE_0138624_357260_P_CREATE_COLD_WRITE_DELTA_TABLE              =   0   # Create table of COLD - HOT delta data for cold write grading
   FE_0138445_336764_P_AUTO_RETEST_T109_FROM_EC11231_EC11049      =   0   # Enable auto retry from EC11049 and EC11231 at T109
   FE_0139178_399481_P_ADD_DFS_AND_TA_SCAN_TO_FEATURE_REV_DISPLAY =   0
   FE_0138677_336764_P_POWER_CYCLE_BEFORE_CFW_AND_S_OVL_DNLD      =   0   # Add powercycle before CFW and S_OVL dnld
   P_DELAY_AFTER_OVL_DNLD                                         =   0   # Add 15 seconds delay after OVL dnld due to BIGS initialization
   FE_0139421_399481_P_BIE_SETTINGS_IN_CHK_MRG_G_FMT              =   0
   FE_0139634_399481_P_DETCR_T134_T94_CHANGES                     =   0
   FE_0139633_341036_AFH_NEW_PROGRAM_NAME_FUNCTION                =   0
   FE_0139645_426568_P_STATE_TABLE_RESET_TIME_TO_READY            =   0   # Allow for a time to ready reset if a state parameter is set in download code
   FE_0139388_341036_AFH_DUAL_HEATER_V32_ABOVE                    =   0
   FE_0139319_336764_P_DELAY_BEFORE_SET_BAUDRATE_FOR_SATA_ON_SAS_SLOT  = 0 # Add delay before set baudrate when power on drive when SATA drive testing on SAS slot
   FE_0140174_220554_P_NO_FPR_AT_END_OF_PARTICLE_SWP              =   0   # No Full Pack Read at the end of Particle Sweep
   FE_0140674_407749_P_TWO_ZONE_INTERPOLATE                       =   0   # Enable retries two another zone interpolate
   FE_0141052_357260_P_ADJUST_211_BACKOFF_FOR_RETRY               =   0   # Apply different fly height adjustment for second T211 BPI measurement retry attempt
   FE_0141097_357260_P_ADD_DNLD_SLEEP                             =   0   # Add sleep prior to code DL
   FE_0141107_357260_P_INCREASE_CMD_TO_FOR_SKIP_CODE_CHECK        =   0   # Increase TO from 10 to 30 for CTRL_Z when checking for F3 code.
   FE_0140444_336764_P_KOR_BER_SPEC_FOR_ORT                       =   0   # Add Korat BER screening per KoratPPA request.
   FE_0141320_220554_P_NO_10S_DELAY_IN_ENABLE_DIAGS               =   0   # Remove 10 seconds delay from enableDiags()
   FE_0141166_409401_P_REPORT_HEAD_WHEN_FAIL_P152_GOTF            =   0   # Reports dblog table when fail grading P152_PEAK_SUMMARY for ADG
   FE_0141706_399481_P_T51_DELTA_TABLE                            =   0
   FE_0141971_220554_P_ADD_DELTA_BER_ATTRIBUTE                    =   0   # Add delta BER atrtribute for the Advance Sweep state
   FE_0142146_426568_P_SKIP_BIE_Y_D_COMMANDS                      =   0   # Add ability to skip BIE thresh setup and Y and D diags even if BIE THRESH is set in test parameters
   FE_0142099_407749_P_NEW_HEADER_FILE_FORMAT                     =   0   # Enable New Header File Format
   FE_0142329_357260_P_USE_DETERMINECODETYPE_FOR_SKIP_CODE_CHECK  =   0   # In CDnldCode(), add retries around 'SKIP_CODE' code checking
   FE_0142350_357260_P_ADD_POWERCYCLE_PRIOR_TO_TGT_DOWNLOAD       =   0   # Add a power cycle in dnldCode() prior to TGT download attempt
   FE_0140570_357263_T135_HEAT_ONLY_FULL_SEARCH                   =   0
   FE_0142458_341036_AFH_NO_RETROACTIVELY_HIRP_ADJUST_NEG_CLR     =   0
   FE_0142623_345963_P_CHK_DELTA_AND_BER_IN_SPEC                  =   0   # Propose new spec of BER : ((Mean(delta) > 0.42) AND (Mean(spcid2) < 4.71))
   FE_0142673_399481_MOVE_SERVO_PARAMETERS_TO_SEPARATE_FILE       =   0
   FE_0143000_341036_AFH_CONS_CHK_3RD_GEN_PHASE_2                 =   0
   FE_0143655_345172_P_SPECIAL_SBR_ENABLE                         =   0   # SBR Special Control
   FE_0143730_399481_P_SEND_WEAK_WRITE_DELTA_TABLE_TO_DB          =   0
   FE_0143743_426568_P_RUN_T_67_FOR_TA_SCAN                       =   0   # Runs test 67 instead of test 134 for TA Scan
   FE_0143795_341036_AFH_CONS_CHK_SUPPORT_FOR_SINGLE_HTR_MODE     =   0
   FE_0143823_357260_P_MQM_WR_TRACKS_BY_HEAD                      =   0   # Add new MQM test 'diagWriteHeadTracks' to perform write pass on given range of tracks and specified head.
   FE_0144322_357260_P_CHECK_FOR_DIAG_INPUT_ERROR                 =   0   # Add check and raise error for 'Input_Command_Error' returned by diag cmd
   FE_0144392_007955_P_V40_DUMP_IN_DISPLAY_G_LIST                 =   0   # Display non-resident Glist in CDisplay_G_list
   FE_0144660_426568_DISABLE_BGMS_IN_PERFORMANCE                  =   0   # Disables BGMS in performance using test 518
   FE_0144766_007955_P_IGNORE_11049_DURING_DFS                    =   0
   FE_0144926_426568_P_DIAG_DISABLE_BGMS_IN_PERFORMANCE           =   0   # For SATA disable BGMS in performance with Diags
   FE_0145164_357260_P_MULTIPLE_ZONES_FOR_EAW                     =   0   # Add ability to run T234 (CEAW_Screen) on multiple zones.
   FE_0145007_208705_HMS_MEAS_IN_FNC2                             =   0   # Update VBAR data handling to support running measurements in additional operations
   FE_0145387_399481_P_VSCALE_OPTI_LLR                            =   0   # Log Likelihood Scaling
   FE_0145389_341036_FAFH_ENABLE_FREQUENCY_SELECT_CAL             =   0
   FE_0145391_341036_FAFH_ENABLE_T191_USE_T74_CAL_FREQ            =   0
   FE_0145400_341036_FAFH_ENABLE_TRACK_PREP                       =   0
   FE_0145405_426568_P_ENC_WR_SCRN_VS_RE_FORMAT_RAW_DELTA         =   0   # ENC_WR_SCRN vs RE_FORMAT RAW delta screen
   FE_0145412_341036_FAFH_ENABLE_AR_MEASUREMENT                   =   0
   FE_0145180_357260_P_BROKER_PROCESS                             =   0   # Enable support for Broker process (program = BROKER, TGT = BRO1 | BRO2)
   FE_0146457_426568_P_USE_HD_LGC_PSN_INSTEAD_OF_HD_PHYS_PSN_IN_T250 = 0  # Add functionality to use the logical head position instead of the physical head position in test 250
   FE_0145589_345963_P_T126_DISABLE_DEBUG_MESSAGE                 =   0   # Disable debug message for T126
   FE_0146862_357260_P_ENABLE_T240_EAW_SCREEN                     =   0   # Enable test 240 in CEAW_Screen - will replace T234 eventually
   FE_0145983_409401_P_SEND_ATTR_FOR_CONTROL_DRIVE_ERROR          =   0   # Send attribute for control drive error on hard defect for TODT
   FE_0147357_341036_AFH_T172_FIX_TRUNK_MERGE_CWORD1_31           =   0
   FE_0148182_407749_P_RETRIES_CHANGE_LOW_BAUDRATE_IN_CPC_DNLDCODE =  0   # Enable retries with change low baud rate during CPC download code.
   FE_0148582_341036_AFH_WHIRP_V35_CHANGE_VALUES                  =   0
   FE_0148837_357260_ENABLE_VERIFY_IN_G_P_MERGE_FORMAT            =   0   # Enable User Partition Certify during G-P merge format pass
   FE_0147794_345172_A_FLAWSCAN_PWR_LOSS_CHK                      =   0   # If power loss has occurred at A_FLAWSCAN state, reset to rerun at INIT_FS.
   FE_0149136_409401_P_DELTA_BER_IMPROVEMENT                      =   0   # To detect head degradation problem
   FE_0149328_345963_P_SET_OPER_FOR_MTS                           =   0   # Set oper for MTS to fix EC11049 by add to "Auto Replug" list due to download code at Test8, CRT2
   FE_0149593_357260_SEAGATE_THERMAL_CHAMBER                      =   0   # Special Script package for testing in STC
   FE_0148761_409401_P_CHECK_HDA_TEMP                             =   0   # Check HDA Temp at the begin of AFH3 and AFH4
   FE_0150074_409401_P_INIT_RETRIEVE_WRITE_SAME_ATTR_WHEN_POWER_LOSS  = 0 # Don't update Write Same attribute equal NONE when power loss
   FE_0150973_357260_P_REDUCE_PARAMETER_EXTRACTOR_VERBOSITY       =   0   # Reduce 'TestParamExtractor = >...' out put from TP extractor
   FE_0150693_409401_P_KORAT_ZAP_OTF                              =   0   # ZAP on the fly for test time reduction
   FE_0150975_345963_P_RISER_TYPE_AND_RISER_EXTENSION_ATTRIBUTES  =   0   # Send riserType and riserExtension attribute to FIS
   FE_0151344_341036_FAFH_ENABLE_T135_FAFH_SPECIFIC_PARAMS        =   0   # FAFH - enable specific params in T135 files only for FAFH.
   FE_0150954_336764_P_ADD_AFH_CLEAN_UP_IN_FAIL_PROC_FOR_DRIVE_FAIL_AFTER_AFH4  = 0 #Perform AFH Clean up in fail proc if drive fail after AFH4 but do not clean up yet.
   #PSTR
   FE_0318846_385431_WAIT_FOR_CERT_TEMP_DOWN                      =   0   #Drive too hot, power down drive and wait
   FE_0318846_385431_FAIL_IF_CERT_TEMP_TOO_HIGH                   =   0   #Fail the drive if too hot as this mean not able to meet the temperature delta at CRT2 

   FE_0158563_345172_HDSTR_SP_PROCESS_ENABLE                      =   0   # HDSTR_SP_PROCESS_ENABLE
   FE_0155953_345172_CHK_DRIVE_TEMP_TO_RERUN_FNC2                 =   0   # HDSTR_SP check Drive temperature is less than 40, require auto retest FNC2 on Gemini.
   FE_0152254_357260_P_CHANGE_1M_ZERO_PTRN_RQMT_TO_12             =   0   # Change the ZERO_PTRN_RQMT attribute setting for 1M zero writes to 12 form 25
   FE_0152007_357260_P_DCM_ATTRIBUTE_VALIDATION                   =   0   # Add support for DCM attribute validation, enable first group of attributes
   FE_0152666_420281_P_USE_T510_INSTEAD_OF_CPC_INTRINSIC_COMMAND  =   0   # Use T510 for Sequential Read/Write in NetApp scrrening instead of "Old" CPC intrinsic command.
   FE_0152667_409401_P_STICKY_CRASH_STOP_SCREENING                =   0   # Add a screen for sticky crash stops by adding a fail criteria to the T25 ran in PRE2.
   FE_0152783_345963_P_HDSTR_TMP_SCRN                             =   0   # Add HDSTR temperature screening (greater than 40c is pass and less than 40c is fail)
   FE_0152905_420281_P_ATTRIBUTE_SEND_FOR_POWER_LOSS_EVENT        =   0   # Attribute send for power loss event
   FE_0152775_420281_P_DISPLAY_ADC_FOR_ADG_CAPTURE_POOR_HEAD      =   0   # Display result file for help ADG capture poor head so far.
   FE_0153218_420281_P_CHOP_P250_ERROR_RATE_BY_ZONE_WITH_SECTOR_VALUE   = 0   # Chop P250_ERROR_RATE_BY_ZONE with SECTOR value.
   FE_0151068_409401_P_KORAT_TTR_DIAG_CMD                         =   0   # Diag Commmand For Test Time Improvement
   FE_0154919_420281_P_SUPPORT_SIO_TEST_RIM_TYPE_55               =   0   # Support SIO test
   FE_0155184_345963_P_DISABLE_ZAP_OFF_AFTER_COMPLETED_ZAP        =   0   # Improve ZAP, Don't run setZapOffPrm_011 after completd ZAP.
   FE_0155594_357260_P_INITIALIZE_DRIVE_INFO_AFTER_INTF_DOWNLOAD  =   0   # At end of CDnlduCode(), re-initialize (CInit_DriveInfo()) drive information
   FE_0156504_357260_P_RAISE_GOTF_FAILURE_THROUGH_FAIL_PROC       =   0   # Use stateTransitionEvent to process GOTF failure
   FE_0156514_357260_P_SERVO_FILES_IN_MANIFEST                    =   0   # Assume Servo package contains valid manifest
   FE_0156449_345963_P_NETAPP_SCRN_ADD_3X_RETRY_WITH_SKIP_100_TRACK     = 0 # Add 3x retry with skip 100 track if EC13426 found at DataErasure test2 and Adjacent Pinch sequence for NetApp Screen.
   FE_0156072_409401_P_ENABLE_COMPARE_TGTA_CODE                   =   0   # Add compare TGTA code in base_IntfTest.py
   FE_0156784_409401_P_CLEAR_OPTI_ZAP_DONE_ATTR_AT_PRE2           =   0   # Clear OPTI_ZAP_DONE attribute for re-run case
   FE_0157311_345172_TURN_ON_ZAP_AFTER_HDSTR_UNLOAD               =   0   # Turn on Zap when HDSTR unload
   FE_0157486_357260_P_DO_NOT_CHECK_ZGS_BIT_IF_DCM_SAYS_NA        =   0   # If DCM ZERO_G_SENSOR attrib indicate 'NA', don't bother checking what F3 bit indicates
   FE_0157566_409401_P_MOVE_ZAP_ON_TO_HDSTR_UNLOAD                =   0   # Move ZapOn from READ_SCRN to HDSTR_UNLOAD state
   FE_0157865_409401_P_TEMP_CHECKING_IN_ZAP_AND_FLAWSCAN_FOR_GHG_FLOW  = 0 # Add temp checking in HDSTR process in ZAP and FLAWSCAN.
   FE_0160792_210191_P_TEMP_CHECKING_IN_GEMINI_CRITICAL_STATES    =   0   # Check Temperature in Gemini for "VBAR_ZAP","ZAP","AFH1","AFH2","AFH3","A_FLAWSCAN","DGTL_FLWSCN"
   FE_0160792_210191_P_TEMP_CHECKING_IN_CRITICAL_STATES_FOR_GHG_FLOW_PHASE_1 = 0 # Add temp checking in HDSTR process for all critical states
   FE_0157921_357260_P_VBAR_ZONEMAP_IN_TESTPARAMETERS             =   0   # Provide VBAR zoneMap in testParameters - otherwise calculated from numZones (must include all user zones, but not system zone)
   FE_0158023_357260_P_AFH_LOOP_COUNT_BY_STATE                    =   0   # Provide loop count for AFK LUL per AFH state
   FE_0158386_345172_HDSTR_SP_PRE2_IN_GEMINI                      =   0   # Support HDSTR_SP with run PRE2 oper in Gemini.
   FE_0158388_345172_HDSTR_SP_CHECK_TEMP_EVAL_PURPOSE             =   0   # Check temp in [PRE2,CAL2,FNC2,FNC] skip all state before MDW_CAL and after download F3 code for evaluation.
   FE_0158632_357260_P_ENABLE_TEST_163_MDW_QUALITY_CHECK          =   0   # Enable calls for T163 MDW Pattern Quality check
   FE_0158373_341036_ENABLE_AFH_LIN_CAL_BEFORE_READER_HEATER      =   0
   FE_0159212_357260_P_USE_2601_FOR_STATIC_DEPOP                  =   0   # Use 2601 servo depop command for static depop (in place of 2301)
   FE_0159364_341036_FAFH_INIT_HIRP_RAP_CORR_REF_TRK              =   0
   FE_0159091_345963_P_DISABLE_ZBZ_BY_CHANGE_CWORD2               =   0   # Disable ZBZ feature in ZAP process in order to perform 100% Read ZAP in "GHG" process by change CWORD2
   FE_0159305_409401_P_KORAT_TTR_DIAG_CMD_BY_OPTI_READ_ONLY       =   0   # Diag Commmand For Test Time Improvement by optimize read operation only
   FE_0159968_409401_P_HDSTR_HIGH_TEMP_SCRN                       =   0   # High temperature screening in GHG process
   FE_0159969_409401_P_RETEST_FULL_FNC2_IF_HDSTR_HIGH_TEMP_SCRN_FAIL   = 0 # Auto retest full FNC2 if high temperature screening failed
   FE_0159477_350037_SAMPLE_MONITOR                               =   0   # Sample monitor, selectively enable sdat based on the truth value delivered from a remote server.
   FE_0159970_409401_P_HDSTR_SP_HIGH_TEMP_SCRN                    =   0   # High temperature screening in HG process
   FE_0158685_345172_ENABLE_HDSTR_TEMP_CHECK                      =   0   # Support HDSTR check temperature
   FE_0165651_345172_FE_PROC_TEST_FLOW_ATTR_FOR_SEPARATE_FLOW     =   0   #Add new attributes to separate yield by process test flow(PROC_TEST_FLOW).
   FE_0161827_345172_P_CONTROL_TEMP_PROFILE_BY_HEAD               =   0   # Add flag to control temp profile by Head to support HG & GHG2.
   FE_0159477_350037_SAMPLE_MONITOR                               =   0   # Sample monitor, selectively enable sdat based on the truth value delivered from a remote server.
   FE_0159597_357426_DSP_SCREEN                                   =   0   # DSP Screen, selectively enable DSP based on the truth value delivered from a remote server.
   FE_0160686_220554_P_USE_ZONE_1_INSTEAD_OF_0_IN_WEAK_WRITE_SCRN =   0   # Use zone 1 insread of 0 in weak write screen for OD test area
   FE_0160713_409401_P_ADD_AFH_CLEAN_UP_AT_AUTO_REPLUG_FOR_DRIVE_FAIL_AFTER_AFH4 =   0   # To do AFH Clean up when fail and will be performed Auto-Replug after pass AFH4.
   FE_0161719_470833_P_ADD_PWC_RETRY_TO_SWD_TEST_227              =   0   # (MantaRay) Perform power cycle and retry to Test 227 for EC10469 in FNC2/SWD_Ver2 in CSkipWriteDetectAdjustment (base_SerialTest.py).
   FE_0162672_357260_P_FORCE_GET_PPID                             =   0   # Forse request for PPID from server - regardless of existing attributes.
   FE_0162925_409401_P_ADD_MORE_ATTR_TO_CTRL_RWM_MQM              =   0   # Add more attribute,MEDIA_RECYCLE and LINE_NUM, to control Rework MQM
   FE_0162917_407749_P_AFH_LUL_FOR_RETRY_BY_ERROR_CODE            =   0   # Enable to select AFH Load / Unload when retry by error code
   FE_0163145_470833_P_NEPTUNE_SUPPORT_PROC_CTRL20_21             =   0   # Enable Neptune support. For use of PROC_CTRL20 and PROC_CTRL21.
   FE_0163564_410674_GET_ZONE_INFO_BY_HEAD_AND_BY_ZONE            =   0   # Change command to get zone info from x0 to x0,hd,zone and fix EC10566 at IOSC2.
   FE_0163769_357260_P_SKIP_FORMAT_OR_PACK_WRITE_IF_ZERO_PAT_DONE =   0   # If we've already completyed a full pack write (in this operation) don't re-do another pack write or format pass
   FE_0163943_470833_P_T250_ADD_RETRY_NO_FLAWLIST_SCAN            =   0   # Perform an additional retry during T250_BER_FNC2 (spc_id=2) that doesn't scan the flawlist
   FE_0164090_409401_P_ADD_CRX_CNT_ATTR_TO_CTRL_RWK_MQM           =   0   # Add CRX_CNT attribute to control Rework MQM
   FE_0164093_460646_P_PN_SWOP_FEATURE                            =   0   # Enable PartNum swop feature
   FE_0164094_407749_P_ADD_AUTO_RETRIES_FOR_READ_CMD              =   0   # Add auto retries for R,,,,1 command.
   FE_0164158_460646_P_ENABLE_RUN_CCV2_BY_SETOPER_ATTR            =   0   # Enable for run CCV2 by set oper attribute
   FE_0164363_395340_P_AFH_FRAMES_STACK_ON_FNC_FNC2               =   0   # Show AFH frames stack on FNC/FNC2 by drives fail for ADG verify Data
   FE_0164370_395340_P_FIRST_ODT_SEQUENT_TEST_FOR_SATA            =   0   # Increase ODT sequesttest to SATA process.
   FE_0165521_409401_P_SET_3_HOLE_DSP                             =   0   # Update 3-hole DSP setting
   FE_0165754_409401_P_SKIP_DSP_SCRN_FOR_2_HD                     =   0   # Skip DSP Screen for 2 HD at FNC/FNC2
   FE_0166346_475827_P_DSP_SCREEN_PARAMS_ABSTRACTION              =   0   # Enable abstraction of DSP_SCREEN related params to Testparameters.py
   FE_0166912_336764_P_ADD_T25_TO_FAILPROC                        =   0   # Enable performing T25 at FailProc
   FE_0167407_357260_P_SUPPRESS_OVERLAY_FILE_INFO                 =   0   # Suppress 'Overlay File IR...' output in result file
   FE_0167407_357260_P_SUPPRESS_EXECUTION_INFO                    =   0   # Suppress 'Execution Info:...' output in result file
   FE_0168360_470833_P_REDUCE_ZONE_BER_DATA_OUTPUT                =   0   # Reduce getZoneBERData output to only print for the current spc_id (table = P_FORMAT_ZONE_ERROR_RATE)
   FE_0168623_357260_P_HANDLE_LBA_FREE_ZONES                      =   0   # Handle the possibility of a zone with no user LBAs
   FE_0169486_357260_P_DEPOP_REQ_OVERRIDES_DEPOP_MASK             =   0   # Ignore TP defined depopMask and use heads as defined by DEPOP_REQ if populated.
   FE_0169617_220554_P_SET_SIM_FSO_SIMDICT_ADAPT_FS_PRM_TO_38912  =   0   # Set SIM_FSO.py simDict.ADAPT_FS_PRM to 38912
   FE_0172346_475827_P_FORMAT_TO_512_IF_ALT_SECT_SIZE             =   0   # Include a quick format to 512 if converting from alternate sector size to alternate sector size
   FE_0173306_475827_P_SUPPORT_TRUNK_AND_BRANCH_F3_FOR_GET_TRACK_INFO = 0  # Allows calculation of proper track cleanup range for both trunk and branch F3 code, regardless of flag settings.
   FE_0173493_347506_USE_TEST321                                  =   0   # Use test 321 to perform mr resistance measurements and calibrations instead of T186
   FE_0173503_357260_P_RAISE_EXCEPTION_IF_UNABLE_TO_READ_DCM      =   0   # If we cannot read customer attributes, raise 14761
   FE_0173503_357260_CLEAR_CCV_ATTRIUBUTES_IN_CCV2                =   0   # If CCV2, clear relavant CSM attrs.
   FE_0174192_395340_P_USE_C5_C6_TO_CHECK_P_LIST_ON_CUT2          =   0   # Fix fail ODT failure (C5 & C6) at CUT2
   FE_0174228_395340_P_AUTO_RETRY_FPW_R_NETAPP_MQM                =   0   # Auto retry full pack W/R for NetApp Screen
   FE_0175785_357360_EXTRA_597_IOPS_TESTING                       =   0   # Perform additional T597 passes with modified parameters per PIF
   FE_0176570_336764_ALWAYS_PAUSE_AFTER_SEASERIAL_FAIL            =   0   # Always add sometime pause if Seaserial fail and try again
   FE_0176418_336764_TIMESTAMP_UDS_CLEAR_ENABLE                   =   0   # Issue DITs command to clear UDS timestamp and frame0 flag20 of SMART
   FE_0176665_475827_RUN_T246_IN_MDW_CAL                          =   0   # Run new T246 in MDW Cal as addition to T46.
   FE_0177176_345172_ENABLE_RETURN_VALUE_CHECKING_FROM_T507       =   0   # Add feature checking from 'CTRL_Z' and 'CTRL_T' after send T507.
   FE_0177689_357260_P_FORCED_ON_THE_FLY_DEPOP                    =   0   # Support for forced 'on-the-fly' depop
   FE_0177865_336764_P_MOVE_OPER_CHECK_AFTER_FLG_LOADED           =   0   # Move operation check after FLG file loaded.
   FE_0178352_357260_P_PHYS_TO_LGC_HD_MAP_INCLUDES_ALL_HDS        =   0   # Pad out PhysToLgcHdMap with INVALID_HD (0xff) for missing heads
   FE_0178548_475827_P_DISABLE_BERP_T51_PARAMS                    =   0   # With BERP disabled in selftest, T51 parameter changes are needed
   FE_0178990_357260_DEPOP_USE_PHYSICAL_HEADS                     =   0   # Reference Phys head ( not logical head )
   FE_0182188_231166_P_ALLOW_DETS_CE_LOG_CAPTURE                  =   0   # Allow capture of CE log data through SPT DETS command
   FE_0183110_231166_P_OPTIMIZE_CCV_PWR_CYCLES                    =   0   # Optimize the CCV power cycle sequence
   FE_0183111_231166_P_CCV_CHECK_ALL_DOS                          =   0   # Check all DOS types for validation
   FE_0222955_470833_P_DOS_CHECK_NEED_TO_SCAN_ONLY                =   0   # F3 removed DOSOughtToScan references, this new method only uses DOSNeedToScan for the congen parameter check
   FE_0195908_231166_P_WRT_ST_MODEL_PART_INTERNAL                 =   0
   FE_0190035_336764_P_ENABLE_SAMPLING_CCV_ITEM_IN_DRIVE_VER_S_LIST = 0   # Enable sample monitoring to count drive only in Drive_Ver_S list in PIF
   FE_0190477_357260_P_SKIP_GOTF_FOR_SELECT_STATES                =   0   # Skip GOTF grading on states in GOTF_EXCLUDED_STATES list
   FE_0191645_470833_P_ONLY_ADD_TGT_AFTER_TWO_FAILED_DNLDS        =   0   # Only add 'UNLK','TGT' to the download sequence after two failed download attempts... currently does this after only one failed attempt
   FE_0190119_470833_P_SBS_SKIP_WRT_ALT_TONES_AND_SMART_MFG_FRAME =   0   # Skip writing alt tones and the SMART Manufacturing frame in SBS code (necessary when SBS has different F3 requirements than standard build targets, as these two properties are not supported)
   FE_0197001_409401_P_CHK_BG_FOR_PROTECTION_RE_CONFIG            =   0   # Enable checking BSNS_SEGMENT for protection re-config process
   FE_0205034_497324_P_SMART_BD_ATTRIBUTE                         =   0   #Cut spec SMART attribute "BD"(189) at the end of CUT2

   FE_0212759_409401_P_RESET_SCN_ATTR                             =   0   # Reset SCN_TEST_DONE = NONE at PRE2 and FIN2
   FE_0220066_395340_P_AUTO_RE_DL_GTGA_FOR_ALL_DOWNGRADE          =   0   # Re-Download TGTA for all GOTF downgrade with IO sequence test
   ADJUST_TPI_FOR_CONSTANT_MARGIN                                 =   0   # After HMS runs, lock BPI pick and adjust TPI pick to achieve constant margin.
   ADJUST_HMS_FOR_CONSTANT_MARGIN                                 =   0   # Set both VbarHMSMinTargetHMSCap and VbarHMSMaxTargetHMSCap to the single VHMSConstantMarginTarget value for constant HMS capability.
   FINE_OPTI_ZAP_ENABLED                                          =   0   # Perform MiniZap before fine ujog
   FNG2_Mode                                                      =   0   # FNG2_Mode 1 for simplified method, 2 for RequestService (restart with 4C) method
   FORCE_LOWER_BAUD_RATE                                          =   0
   FORCE_MR_CLEAN                                                 =   0
   FailcodeTypeNotFound                                           =   0   #Fail if a download key is specified and that file isn't spec'd in Codes.py
   FtpPCFiles                                                     =   0   # Send PC files to designated server
   FtpRestoreRecords                                              =   1   # Send restore records to designated server
   GA_0113069_231166_ENABLE_VERBOSE_DEBUG_IN_238_AGC_JOG          =   0   # Enable verbose output of test 238 agc uJog- implemented in TP
   GA_0115421_231166_MEASURE_BER_POST_WP_OPTI_NOM_FMT             =   0   # Enable measuring the BER in between WP opti and Full zone picker
   GA_0115920_357915_REPORT_SERVO_FLAW_TABLE_BETWEEN_READ_AND_WRITE_SCANS = 0 # Enable outputting the servo flaws table between the flawscan write and read passes, to facilitate FA.
   GA_0117198_231166_PRESERVE_PCFILES_CONFIGVAR_SUPPORT           =   0   # Enable the use of configvar to prevent deletion of pcfiles and generic files for RBF of a config while keeping drive state constant
   FE_0168920_322482_ADAPTIVE_THRESHOLD_FLAWSCAN_LSI              =   0   # Analog flaw scan threshold by head by zone for LSI
   FE_0000000_348432_AFS_SYNC_UP_AFS_THRESHOLD                    =   0   # SMR: Same AFS threshold for SLIM and FAT tracks.

   #  *** Requires local CM modification at this time. See Michael Magill for mod.
   GA_0149146_357260_LBA_READS_IN_AFH_CLEANUP                     =   0   # Enable read verifies (LBA mode) in AFH Cleanup - for FA purposes
   SGP_81592_CHS_READS_IN_AFH_CLEANUP                             =   0   # Enable read verifies (CHS mode) in AFH Cleanup - for FA purposes
   GANTRY_INSERTION_PROTECTION                                    =   0   #Enable the disabling of a cell to reduce the probability of insertion disturbance during a sensitive test
   GOTFGradingRevCheck                                            =   0
   HDI_ENABLED                                                    =   0   # Flag to enable defect scan (HDI detection) in ADV_SWEEP.
   HOLLIDAY_SINGLE_CODE_SET                                       =   0   # Flag to enable single code set for TDK-RHO, FUJI-RMO, 1Disc-2Disc.
   IOWriteReadRemoval                                             =   0   # to enable write read removal for test time saving
   InitSmart_NeedMoreDelay                                        =   0
   IS_DUAL_HEATER                                                 =   0   # this is set by PF3 code
   IS_DH_CODE_ENABLED                                             =   0   # this is set dynamically based on the SF3 AFH Major/Minor rev #'s
   IS_F3_TRUNK                                                    =   0   # this is to control flow for trunk only targets
   IS_DETCR                                                       =   0   # this is modify Test 109 to support DETCR TA
   MARVELL_T195_VERSION                                           =   0   # Use the Marvell/TCO version of HD_STABILITY
   MARVELL_PHAST_MICROJOG                                         =   0   # Turn on and use PHAST microjog (T238) for Marvell
   MAX_WP_IDX_WP_BREAKS                                           =   0   # Break in the WP filter routines if filter criteria or index limits violated
   Media_Cache                                                    =   0
   MEASCQM_DATA                                                   =   0   # Enables measCQM data collection
   NPT_LOG_REDUCTION                                              =   0
   QBER_skip_flawscan_prep                                        =   0   # Do not flawscan (prep) the QBER tracks..no point since defect list isnt being used anyway (LCO)-AT THIS TIME 2/22/08
   runMSDscreen                                                   =   0   # run MSD screens during format
   SEA_SWEEPER_ENABLED                                            =   0
   SEA_SWEEPER_RPM                                                =   0
   SEND_OPERATION_METRICS                                         =   0
   SET_HEAD_SUPPLIER_IN_SAP                                       =   0   # Set the hga supplier in the sap- requires servo support
   ServoAccousticMode                                             =   0
   SNODataCollection                                              =   0
   T109_STRESSOR_ENABLE                                           =   0
   T109_STRESSOR_END_CYL                                          =   0
   T176_AUTOFREQ                                                  =   0   # Enable auto compute of servo frequency for T176
   T250_SER_ZAP                                                   =   0   # Enable zap for T250 test tracks pre-zap execution
   TCC_MEASTEMP_SPIN_ENABLED                                      =   0   # For Wyatt and Crockett, drive needs to be spinning during temperature measurement
   TEST_86_DEPOP_SUPPORT                                          =   0
   TIMEOUT_TIMER_SEC_SUPPORT                                      =   0
   USE_DEFAULT_TA_LPF                                             =   0   # Use default TA_LPF values from RAP and don't exec SF3 opti of them.
   USE_HGA_AAB_ATTR                                               =   0   # Use the parameter ATTR_AAB_MATRIX to resolve attributes to determine aab type- fallback to configvar if not available
   USE_HGA_VENDOR_ATTR                                            =   0   # Use the drive attribute HGA_VENDOR to identify head type- fallback to configvar if not available
   USE_HSA_WAFER_CODE_ATTR                                        =   0   # Define HSA_WAFER_CODE, derived from FIS attr HEAD_SN_00. Fail drive if cannot get from FIS or ConfigVar
   #####   DBLOG Switches  #######
   ADD_PARAMETRICS_TO_LIMITS                                      =   0   # Enables increasing the parametric loading up to the maximum parametric limit
   USE_LOAD_ONLY_IN_PRODUCTION                                    =   0   # Enables the use of productionLoadOnly if non empty and PRODUCTION_MODE is set
   USE_PREAMP_VENDOR_ATTR                                         =   0
   USE_WAFER_CODE_ATTR                                            =   0   # Use the parameter WAFER_CODE_MATRIX to resolve attributes to determine wafer code- fallback to configvar if not available
   VARIABLE_OST                                                   =   0   # Enable read/write of OST value from MDW_SN information
   VSCALE_OPTI                                                    =   0   # Save optimized VSCALE Values
   VgaPcFileFlashUpdate                                           =   0   # Enable if VGA opti requires a split update of SAP from PCFile and RAP from FLASH

   WA_0110324_357260_POWER_CYCLE_TO_READ_TEMP                     =   0   # PowerCycle drive to force PreAmp temp re-read (workaround for Casey / Extreme3 Servo bug)
   WA_0110375_231166_DISABLE_POWERCYCLE_PRIOR_TO_OVL_DOWNLOAD     =   0   # Don't power cycle prior to OVL download. This may require F3 to process MCT complete message only after TGT reset is complete-> IFR-0108774
   WA_0110971_009438_POWER_CYCLE_AT_ZAP_START                     =   0   # Add a power cycle prior to ZAP of first head.  PDD-0110971
   WA_0111543_399481_SKIP_readFromCM_SIMWriteToDRIVE_SIM_IN_HIRP  =   0   # possible fix for delta VBAR clearance math error causing many more drives to retest VBAR.
   WA_0111638_231166_DISABLE_SETTING_OF_PREAMP_HEATER_MODE        =   0   # Disable setting preamp heater mode until preamp support is enabled and/or fw is fixed
   WA_0111716_007955_POWERCYCLE_AT_VBAR_START                     =   0   # powercycle at beginning of VBAR to workaround issue caused by T195 before VBAR
   WA_0111581_341036_AFH_RUN_AFH1_SCREENS_AFTER_HIRP              =   0   # when enabling this flag be sure and add the AFH1_SCREENS state in the StateTable.py
   WA_0112377_231166_ADD_POWER_CYCLE_RETRY_FOR_11049_EC_BANSHEE_1_0 = 0   # For power cycle retry for banshee 1.0- remove at banshee 2.0
   WA_0112479_231166_POWERCYCLE_AND_CONTINUE_ON_11049_ERR_FOR_BANSHEE_1_0 = 0 # Ignore all 11049 errors- hack for banshee 1.0 bringup
   WA_0112781_007955_CREATE_P051_MILLIONW_PREDICTIN_EXT           =   0   # new table created for GOTF - using abs track index & cal_raw field
   WA_0115021_231166_DISABLE_WRITING_RESULTS_FILE_TO_DUT          =   0   # Disable writing the results file to DUT at end of oper
   WA_0115472_208705_DISALLOW_13409_WATERFALL                     =   0   # Disallow EC13409 from waterfalling so that they impact native yields
   WA_0119554_231166_DIAG_MAX_LBA_LEN_LIMITED                     =   0   # Split lba cmds into smaller cmds based on 0xF000 boundry until diag/llrw is fixed
   WA_0120500_231166_PH_CRT2_ESLIP_DNLD_SETTING                   =   0   # Explicitly set ESLIP sync and modes if CRT2 in download and in cpc cell
   WA_0121440_7955_FORCE_SATA_NO_JMPR                             =   0
   WA_0121752_399481_USE_U_CMD_TO_SPIN_UP_IN_WEAK_WRITE_SCREEN    =   0   # If drive freaks out when told to do a write when heads are still on ramp, we can issue u command to spin up before writing.
   WA_0122534_231166_DIAGS_UNSUPPORTED                            =   0   # Flag to enable if ascii diagnostics aren't supported
   WA_0122681_231166_EXTENDED_BAD_CLUMP_TIMEOUT                   =   0   # Add additional time for bad clump drives to come SPT ready
   WA_0123631_399481_SKIP_T234_T252_DURING_AUDIT                  =   0
   WA_0124639_231166_DRIVE_SMART_NOT_SUPPORTED                    =   0   # Early life cycle flag to disable all smart commands if product doesn't support it but F3 has SMART flag enabled
   WA_0124831_231166_FORCE_INTF_TYPE                              =   0   # allow usage of force key/value define in TP.partNumInterfaceMatrix
   WA_0125062_399481_IGNORE_00003003_IN_MQM_SQUEEZE               =   0
   WA_0125708_426568_FULLY_DISABLE_LVFF                           =   0   # Add encroachment workaround to fully disable LVFF
   WA_0126043_426568_TOGGLE_SAPBIT_FOR_HIGH_BW_FILTER             =   0   # Modifies the sap bit 11 offset 239 so Servo will then use either a high or low BW filter based on PCBA number
   WA_0126798_357260_FORCE_DIAG_OVERLAY_LOAD                      =   0   # In diagWeakWriteScreen, force diag overlay loading by issuing ovly cmd
   WA_0126987_426568_RUN_TEST_193_TWICE_WITH_NEW_GAIN_VALUE       =   0   # Run test 193 twice with a new gain value if it fails for error code 14598
   WA_0128885_357915_SEPARATE_OD_ODD_EVEN_FLAWSCAN                =   0   # Add a separate OD odd/even flawscan sequence at the start of flawscan.  This allows different parameters to be used for flawscan and is intended to provide a more aggressive flawscan at the OD
   WA_0129386_426568_DISABLE_LVFF_AFTER_ZAP_BASED_ON_PCBA_NUM     =   0 and not testSwitch.WA_0125708_426568_FULLY_DISABLE_LVFF  # If the drives doesn't have low noise caps disable LVFF after ZAP
   WA_0129851_399481_ENCROACHED_SCREEN_ERROR_FILTERING            =   0
   WA_0130075_357260_SKIP_SPEED_CHECK                             =   0   # Skips attempt to reset ATA Speed to nominal - intended to case where speed is reported correctly, but SCT-BIST support is not available.
   WA_0130599_357466_T528_EC10124                                 =   0   # Work around for T528 EC10124 failures
   WA_0133429_399481_RETRY_ALT_LBA_IN_ENC_WR_SCRN                 =   0   # Encrroached write screen 2>F(lba),A1 has sporadic failure with 0000500E diagerror.
   WA_0136676_7955_P_POWER_DOWN_DELAY_AFTER_PARTICLE_SWEEP        =   0   # 10 min delay after power down
   WA_0169134_470833_P_T538_EC10179_UNKNOWN_MODEL_NUMBER          =   0   # If T538 returns EC10179 for an unknown model number, call T507 to work around issue
   WA_0173899_475827_P_SKIP_ATA_READY_CHECK_AFTER_G_P_MERGE_FORMAT =  0   # Mitigates TTR failures caused due to Mediacache
   WA_0174392_470833_P_POWERCYCLE_UPON_RETRY_IN_ZERO_PATTERN_WRITE=   0   # Perform a power cycle, plus re-enable the write cache, before retrying the zero pattern write
   WA_0175502_357260_P_VBAR_DEPOP_DO_NOT_ALLOW_HEAD_ZERO          =   0   # Do not allow depop of head 0
   WA_0264977_321126_WAIT_UNTIL_DST_COMPLETION                    =   0   # No command to abort DST. After PLR, need wait some time to avoid 10340

   ######### Initiator support #########
   WA_0117940_231166_IGNORE_INIT_DL_MISMATCH                      =   0   # Ignore initiator rev mismatches- broken for now
   WA_0122875_231166_NOM_SPEED_TP_OVERRIDE                        =   0   # Add support for a speedOptions override parameter if F3 reporting unsupported speeds.
   WA_0124652_231166_DISABLE_SET_XFER_SPEED                       =   0   # Do not set xfer rate in SIC and CPC
   BF_0126057_231166_FAIL_INVALID_TST_RETURN                      =   0   # Fail if test returns test num of 0== test didn't run
   FE_0134158_357552_CLEAR_MODE_PAGES_FOR_SAS                     =   0   # Clear mode pages on SAS drives
   FE_0134771_357552_TCO_STYLE_CCV                                =   0   # Run TCO-style Customer Configuration Verification
   BF_0135010_357552_ADD_POWER_CYCLE_AT_CCV_START                 =   0   # Add power cycle to read up SMART attrs
   WA_0134988_395340_RESET_TIMEOUT_THAT_REMAIN_ON_CPC             =   0   # Use T506 to clear run time setting that remain on CPC.
   WA_0150637_357260_P_SKIP_P1_1_IN_NVCACHE_INIT                  =   0   # Skip P1,1 diag prior to T1 in initializeNVCTiming()
   ######### End Initiator support flags #######

   WA_0124296_340210_DOWNGRADE_TO_STD_ONLY                        =   0
   WA_157020_357260_P_POWER_CYCLE_BEFORE_TGT_DOWNLOAD             =   0   # In serial download, powerCycle before TGT download
   WIJITA_ADJ                                                     =   0
   WO_MULTIRATESNO_TT122                                          =   0
   WO_V3BAR_ENABLED                                               =   0
   WTFunitTest                                                    =   0
   XML_SUM_IN_RESULTS_FILE                                        =   0   # Enables printing of XML DBLOG data to results file for data collection
   ZGS_Enabled                                                    =   0
   allow1TempCERT                                                 =   0
   autoDocument                                                   =   0   # Enables Bootscript to autodocument !!REQUIRES EPYDOC
   autoRegression                                                 =   0   # Enable to allow FTP of automated regression results to AutoReg server
   buildCustomFW                                                  =   0
   captureDriveVars                                               =   0   # For documenting driveVars later
   checkMediaFlip                                                 =   0   # Enable checking TA_CNT and VRFD_FLAWS for Media Flip
   checkSN                                                        =   0   #  Enable checking the PCBA SN in CAP against the FIS attribute
   customerConfigInCAP                                            =   0
   disableTestDataOutput                                          =   0
   disable_tests_deferred_spin                                    =   0
   failIfPhysCacheSizeExceeded                                    =   0
   failUnitTest                                                   =   0
   forceDummyPartNumWWN                                           =   0
   forceNewWWN                                                    =   0   # Forces retrieval of new WWN from DCM
   forceRapDownLoad                                               =   0   # Force RAP download if preampID and preampRev do not match
   gui                                                            =   0
   jumperdetect                                                   =   0
   modifyRunTimeServoController                                   =   0
   operationLoop                                                  =   0   #Handle loop limit evaluation in CEndTesting
   operationLoopLimit                                             =   0   #Limit to raise exception when loop limit exceeded
   plantBodeMeasurement                                           =   0
   pressureSensorEnabled                                          =   0
   proqualCheck                                                   =   ConfigVars[CN].get('PRODUCTION_MODE',0)   #Set this flag to enable Proqual checking for valid operation using the attribute
   resetWaterfallAttributes                                       =   0
   setManufacturingStatus                                         =   0
   targetOptiIn251                                                =   0
   GA_0113384_231166_DUMP_RAP_OPTI_DATA_PRE_AND_POST_OPTI         =   0   # Use test 255 to dump opt params pre-post opti for simple opti
   FE_0161887_007867_VBAR_REDUCE_T255_LOG_DUMPS                   =   0   # Eliminate the test 255 dumps prior to the opti call and skip reporting of P255_NPML_TAP0_1_LSI_DATA, P255_NPML_TAP2_3_LSI_DATA, and P255_NPML_BIAS_LSI_DATA
   GA_0152127_357267_ERROR_RATE_AUDIT_PRE_AND_POST_OPTI           =   0   # Use test 250 to verify error rate improvement from simple opti test 251
   unitTest                                                       =   0
   upload_ADP_ATTR                                                =   0
   useASCII_IOEDC_CMD                                             =   0   #Use ascii cmds to determine IOEDC enable status as opposed to sdbp
   useDefaultTargetForAFS                                         =   0   # Use the default NPT target during AFS to standardize the expected gain relative to amplitude response for AFS filters.
   useNonIntelligentPNCacheScheme                                 =   0
   virtualRun                                                     =   0   # Set to run in bench debugger w/o drive attached- <<Not in Gemini>>
   winFOF                                                         =   0   # Set to run in winFOF- <<Not in Gemini>>
   DISABLE_SCORECOMPARE                                           =   0
   CELL_TEST                                                      =   0   # Program build target is a celltest config- for preparing bare initiators and configuration of cell hardware
   COMPART_SSO_SCREENING                                          =   0   # The screening for Compart SSO due to high spin up timeout at RDT
   WA_0121630_325269_SAS_TGT_DNLD_IGNORE_TIMEOUT                  =   0   # When downloading TGT code for SAS, workaround known timeout and just continue.
   FE_0125486_354753_SCRIPTS_SUPPORT_FOR_DOS_PARMS_SUPPORT        =   0   # Support in the scripts for using T213 for STE/ATI and DOS Parms
   FE_0131645_208705_MAX_LBA_FOR_SAS                              =   0   # Add hard-coded entries for 520, 524, and 528-byte sector sizes for SAS
   ZAP_PF3_MAJ_REL_NUM                                            =   0   # Define the ZAP release number
   ZAP_PF3_MIN_REL_NUM                                            =   0   # Define the ZAP release number
   FE_0125510_209214_ZAP_PARAMETER_CLEANUP_1                      =   0   # Cleanup ZAP parameters rev 1
   FE_0132665_209214_ZAP_PARAMETER_CLEANUP_2                      =   0   # Cleanup ZAP parameters rev 2
   FE_0135186_357552_UNLOCK_BY_BUILD_TARGET                       =   0   # Ability to have different unlock files by built target
   WA_0135289_357552_DSENSE_BIT_NOT_DEFAULT_ON_34_BIT_LBA         =   0   # MR_SAS Control mode page (0xA) D_Sense bit should be set on 34-bit LBA
   FE_0135335_342029_P_DETCR_TP_SUPPORT                           =   0   # DETCR SUPPORT
   FE_0135719_342029_DFS_PF3_DEVELOPMENT                          =   0   #Digital Flaw Scan PF3 support in SF3
   BF_0135968_357552_FIX_PIFHANDLER_ATTRLEN_NAME                  =   0   #Fix typo in PIFHandler attrLen name
   FE_0135987_357552_TRUNCATE_DTD_ATTR_TO_SPEC_LENGTH             =   0   #Limit FIS attribute length stored in DTD to dictionary spec'd length
   FE_0136005_357552_USE_ALL_FIS_ATTRS_FOR_DTD_CREATION           =   0   #Open up to all DriveAttributes for DataToDisc binary
   FE_0136017_357552_DELL_PPID_FOR_SAS                            =   0   #Extra/different update/checking for SAS
   FE_0137096_342029_P_T64_SUPPORT                                =   0   # Run T64 servo defect padding instead of T126 padding.
   FE_0137414_357552_CHECK_SLIP_SPACE_FOR_FIELD_REFORMAT          =   0   #Ensure available slip sector for customer re-format
   WA_0137866_231166_P_MANUAL_GOTF_REGRADE_SAS_BACKEND            =   0   # Special handling for re-grade for SAS drives
   FE_0137578_395340_P_T33_CHANGE_ID_SCOPE                        =   0   #Change scope ID Zone of T33 for Mantaray Product
   FE_0137957_357552_POWER_CYCLE_FOR_CODE_LOADS                   =   0   #Add power cycle in PowerControl, mainly for code loads
   FE_0138035_208705_P_NO_TARGET_OPTI_IN_VBAR_HMS                 =   0   #Remove target opti from VBAR_HMS opti
   FE_0138460_357552_FORCE_REFORMAT_IN_CSASFORMAT_CLASS           =   0   #Force a T511 SCSI FORMAT unconditionally
   FE_0138708_009410_FWA_P_SWD_DISABLE_ZERO_LATENCY               =   0   #Trunk workaround, since zero latency in T198 not working on the trunk.  This flag should be removed when the developer has pushed back the support
   FE_0138759_357263_FWA_P_REMOVE_UNAVAILABLE_PARAMS              =   0   #Trunk workaround, waiting on T50 support to be pushed up to the trunk.  This flag should be removed when the developer has pushed back the support
   FE_0139087_231166_P_ALLOW_TP_OVERRIDE_SPEED_LOOKUP             =   0   # Allow TP to override speed setting.
   FE_0139136_357552_T530_CHECK_PLIST_AND_SPARE_SPACE             =   0   #Check PList and Spare sectors for space for field re-format
   FE_0139240_208705_P_IMPROVED_MAX_LBA_CALC                      =   0   # Align max LBA values with official Seagate requirements
   WA_0139361_395340_P_PARTICLE_AGITATION_IO_PLUG                 =   0   #Support change PARTICLE_SWP3 to PARTICLE_AGT on CRT2
   FE_0139501_357552_KEEP_ALL_ZEROS_CHECK_TO_500MB                =   0   #Skip all 00's check outside first 500MB
   WA_0139515_231166_P_OVERRIDE_TO_8_PHYSICAL_TO_LOGICAL_BLOCKS_IN_CPC = 0 # Override the number of physical to logical blocks in cpc to support Bogart 4k emulation w/o reporting in id device
   WA_0139526_231166_P_HARD_RESET_PRIOR_IDENT                     =   0   # Add a hard reset prior to id device to get around a hang seen in grenada
   FE_0139481_395340_P_MQM_TEST_ON_NEW_SPSC2_OPER                 =   0   #Support MQM for new SPSC2 operation like Muskie.
   BF_0142220_395340_P_FIX_LONG_TIME_RW_ON_DIAG_COMMAND           =   0   #Fix long test time RW on diag command for SPSC2
   BF_0156546_395340_P_FIX_CONDITION_PWL_AT_MERGE_G_TO_P          =   0   #Change condition for PWL at CHK_MRG_G state.
   FE_0139584_357552_SUPPORT_NON_DEFAULT_SECTOR_SIZE              =   0   #Allows PIF to dictate non-512 sector size; calls format
   WA_0139839_231166_P_RETRY_11102_IN_MERGE_G                     =   0   # Add retry for 11102 in SAS initiator cells in merge g command as workaround to initiator buffer corruption
   FE_0139892_231166_P_SEARCH_FLED_FAIL_PROC                      =   0   # Move flash led search inside of failproc
   FE_0139688_395340_P_T56_T33_TO_CAPTURE_EC14787_HIGH_NRRO       =   0   #T56 before T33 at PES_SCRN to capture EC14787 (high NRRO).
   FE_0140102_357552_ENABLE_COMPARE_CODE_FUNCTIONALITY            =   0   #Add base_serialTest CMP_CODE functionality in base_intfTest.py
   FE_0140112_357552_FAIL_FOR_IO_TCM_ECC_ERRORS                   =   0   #Check for IO and TCM ECC errors in ASIC
   FE_0140446_357552_PER_TAB_ZEROS_CHECK                          =   0   #In CCV, perform all 00's check only in those locations required per TAB
   FE_0140980_231166_P_SUPPORT_TAG_Q_SI_0_QD                      =   0   #Add support for test 645 in SI to implement test 597 with 0 que depth until SI supports NCQ
   FE_0141083_357552_PI_FORMAT_SUPPORT                            =   0   #Add ability to run SCSI FORMAT with Protection Information
   WA_0141203_357552_FULL_POWER_CYCLE_AFTER_CODE_LOAD             =   0   #Some code loads require drive and initiator power cycle
   FE_0141300_231166_P_ADD_SUPPORT_FOR_STPA                       =   0   # Add support for STPA in package resolution
   BF_0141335_357552_MAKE_WCE_DISABLE_VOLATILE                    =   0   #Make changes volatile
   WA_0141450_231166_DISABLE_LGC_PHYS_MAP_SUPP_SRVO               =   0   # Disable filling of lgc physical map support since servo doesn't support...
   WA_0141401_395340_P_T199_DATA_FOR_DEBUG_ANALYSE                =   0   #Increase T199 at FAIL_PROC for Debug team analyse failure.
   WA_0147953_395340_P_MAX_DELTA_RAW_ERROR_RATE_AFTER_RE_FORMAT   =   0   #Get max delta RAW_ERROR_RATE from ENC_WR_SCRN and RE_FORMAT
   WA_0142094_395340_P_NEW_ADG_MAX_MIN_CLEARANCE_AFH1             =   0   #Create New Attribute for Max&Min Clearance by Head from T172
   FE_0141467_231166_P_SAS_FDE_SUPPORT                            =   0   # Add support for FDE on SAS- also implements other FDE improvements in a backward compatible fashion
   WA_0141609_231166_P_NO_FLG_MATCH_GID                           =   0   # Ignore BID GID in flag resolution
   FE_0141653_231166_P_FORCE_DCM_MODEL_AVAILABLE                  =   0   # Fail drive if model number isn't available in the DCM for validation
   WA_0141744_357552_BYPASS_T515_CERTIFY                          =   0   #Skip T515 certify call
   FE_0142439_357552_ADDED_LOG_PAGE_CLEAR                         =   0   #Clear out log pages for SAS
   FE_0142471_405392_P_ALLOW_OPERLIST_OVERRIDE_OPERATIONS         =   0   # Allow OperList to override Operations.
   BF_0142538_231166_P_FIX_UNDERBAR_MODEL_SAS                     =   0   # Remove trailing _ on sas model number retrieved from test 514
   FE_0142909_231166_P_SUPPORT_SAS_DRV_MODEL_NUM                  =   0   # Add support for retrieval of drive model number (internal) for sas
   FE_0142897_208705_BPI_NOMINAL_IN_RESTART_VBAR                  =   0   # Add BPI Nominal measurements to RESTART_VBAR state
   FE_0142983_357552_ADD_SECTSIZE_TO_ICMD                         =   0   #Add sector size attribute to ICmd object
   FE_0142977_395340_P_AUTO_RETRY_T80_AT_HEAD_CAL_BY_EC           =   0   # Auto retry T80 at HEAD_CAL by EC10427
   FE_0149438_395340_P_LUL_BEFORE_RUN_AFH                         =   0   # Use LUL before AFH to help contact measurement from particle on Head.
   FE_0151079_395340_P_FIX_TEST_TIME_FPW_T510_ON_3TB              =   0   # Fix long test time T510 FPW on 3TB
   FE_0151315_395340_P_POWER_TRIP_AT_CHK_MRG_G_ON_CUT2            =   0   # Fix Power trip for CHK_MRG_G on CUT2 by H/M team by Re-Initializing slips
   FE_0155771_395340_P_HDSTR_UPDATE_ZAP_DATA_ON_GHG_PROCESS       =   0   # Update ZAP data after HDSRT unload to fix EC10129 serial format
   FE_0155867_395340_P_FIRST_ODT_SEQUENT_TEST_FOR_SAS             =   0   # Increase ODT sequesttest to SAS process.
   FE_0157872_395340_P_T135_ON_FAIL_PROC_FOR_ADG                  =   0   # Increase T135 to keep new max clearance from Drive fail.
   FE_0157975_395340_P_POWER_TRIP_AT_FORMAT_IOSC2_ON_IOSC2        =   0   # Fix EC10124 at FORMAT_IOSC2  on IOSC2
   FE_0158668_395340_P_UPDATE_OPER_ATTR_FOR_ODT_TES               =   0   # Update SET_OPER and VALID_OPER to ODT2 for routing.
   FE_0158690_395340_P_UADATE_ATTR_PRE2_DATE_TIME                 =   0   # Update Attribute PRE2_DATE_TIME for Process team summary his works
   FE_0159194_395340_P_CMS_UPDATE_MFG_EVAL_TO_SWOP_PCO            =   0   # Use CMS Swith to help Process Team change PCO for next Operation on the fly.
   FE_0159864_395340_P_POWER_TRIP_AT_SECTOR_SIZE_STATE            =   0   # Fix EC10124 when Power Trip at T511 SECTOR_SIZE on FIN2
   FE_0159866_395340_P_POWER_TRIP_AT_Z_PI_FORMAT_ON_CUT2          =   0   # Fix EC10124 when Power Trip at T511 Z_PI_FORMAT on CUT2
   FE_0159867_395340_P_POWER_TRIP_AT_IBM_SECTOR_SIZE_ON_FIN2      =   0   # Fix EC10124 when Power Trip at IBM_SECTOR_SIZE on FIN2
   FE_0160608_395340_P_FIX_FAILURE_FROM_T514_ON_SIC               =   0   # Fix failure from T514 on SIC with: EC10100, EC10197
   FE_0160968_395340_P_FIX_POWER_CYCLE_FAIL_ON_PWL                =   0   # Fix Power cycle fail when Power Trip
   FE_0155250_395340_P_SUPPORT_GHG_PROCESS                        =   0   # Increase GHG Process
   FE_0144125_336764_P_GEMINI_CENTRAL_DRIVE_COUNT_SUPPORT         =   0   # if Gemini central survice support drive count by site.
   FE_0152991_426568_P_SHORT_NET_APP_SCREEN                       =   0   # Quick run through on net app screen
   ZEST                                                           =   0
   WA_0143406_231166_DISABLE_SAS_SKIP_TRK_MERGE                   =   0   #disable the usage of skip track merge option for sas format.
   WA_0143409_426568_P_CAST_STRINGS_IN_SONY_SCREEN                =   0   # Cast strings to ints in Sony Screen
   BF_0143903_357552_P_SED_PERSONALIZE_BEFORE_CUST_CFG            =   0   #Setup up SED before configuring drive
   FE_0144101_208705_P_NO_TARGET_OPTI_IN_VBAR_ZN                  =   0   # No target opti in VBAR_ZN state
   FE_0142952_010200_SFW_PKG_BIN_SENSITIVITY_SCORING_LIMITS       =   0   # Use binary limit file from servo package (if provided) for sensitivity scoring
   FE_0144401_231166_P_SUPPORT_VEND_CMD_SEP                       =   0   # add PN lookup in order to use vendor field for model number string for sas
   FE_0143702_325269_P_PRESSURE_SENSOR_SUPPORT                    =   0   # Calibrate the Pressure Sensor (Only for programs that have a Pressure Sensor)
   FE_0148166_381158_DEPOP_ON_THE_FLY                             =   0   # Enable Depop on the Fly
   FE_0145290_231166_P_SUPPORT_QUTOES_CUST_MODEL_NUM              =   0   # Add support to put "" around model numbers > 32chars
   FE_0145606_231166_P_USE_LOW_BAUD_AMPS_CHECK                    =   0   # Use 38400/low baud in amps_check to mitigate data loss failures
   FE_0145622_357552_P_ADD_MODE_PAGE_RESET_AT_FIN2_START          =   0   # Add mode page reset on SAS right after FIN2 code load
   FE_0145513_357552_P_IF3_IGNORE_11107_ERRORS                    =   0   # Ignore 11107 errors on initiator card
   FE_0145432_325269_P_CLEAN_OFF_HEAD_DEBRI                       =   0   # Support knocking debris off the head following major AFH failure
   FE_0143876_421106_P_HDSTR_OR_GEMINI_PROCESS_WITH_DRIVE_ATTR    =   0   # distinguish between HDSTR OR GEMINI process with drive attribute
   WA_0145880_231166_P_FIX_INIT_HANG_BDG_DL                       =   0   # Add ignore and init power cycle for bridge code causing initiator hang
   FE_0146187_007955_P_SET_OCLIM_BEFORE_AFTER_T213                =   0   # Set desired OCLIM value in state params for CSteAti
   FE_0146430_231166_P_ENABLE_CERTIFY_SAS_FMT                     =   0   # Enable certify during the CUT2 check merge g scsi format for sas
   FE_0146434_007955_P_T80_HD_CAL_ITEMS_TO_POP_BY_HD_TYPE         =   0
   FE_0146555_231166_P_VER_TEMP_SAT_INIT                          =   0   # Validate the HDA temp is saturated to cell prior to starting test
   FE_0162554_336764_ENABLE_SLIP_LIST_INFO_DISP_AT_FAIL_PROC      =   0   # Enable diag command to display slip list at fail proc for more debugging data
   FE_0146575_231166_P_CHCK_PARAMS_0_ALTS                         =   0   # If FAIL_NEW_DEFECTS is set boolean True (1) in stateparams for CDisplay_G_list then if new defects are found drive is failed with 10506 FC
   FE_0146586_007955_P_ADD_RW_SCREEN_TO_FEATURE_REV_DISPLAY       =   0
   FE_0146721_007955_P_ALLOW_DRVMODELNUM_LBA_OVERRIDES_AT_LCO_ONLY  = 0
   FE_0144363_421106_P_TIMEOUT_SPEC_FOR_SMART_LONG_DST            =   0   #Add the Timeout spec for SmartLongDST test
   FE_0146812_231166_P_ALLOW_DL_UNLK_BY_PN_TCG                    =   0   # Add feature to allow unlock of download port for tcg personalization by PN
   FE_0146821_231166_P_ALLOW_FDE_UNLK_SKIP_MISS_CODES             =   0   # Add feature to allow tcg unlock to bypass tcg code download and just leave drive in setup state for future download
   FE_0146843_007955_P_DISABLE_PRINT_ERASE_DELTA                  =   0   # disable printing table 'P051_ERASURE_BER_DELTAS' to resultsfile
   FE_0146953_231166_P_DETECT_FLASH_CHECKSUM_FAIL                 =   0   # detect flash corruption in promptread
   FE_0147072_007955_P_EAW_USE_T240_IN_PLACE_OF_T234              =   0   # Use T240 instead of T234 in EAW screen
   BF_0147076_357552_P_ADD_SKUA_21_REV                            =   0   # Add support for Skua 2.1 to Mantaray SAS Dell PPID
   FE_0147082_231166_P_VERIFY_MEDIA_CACHE                         =   0   # Verify media cache via sct command
   FE_0147105_426568_P_COMBO_STATE_SELECTION_P_TESTSWITCH         =   0   # Add functionality to select a state based on testSwitches and 'P' in the arguements
   BF_0147176_357552_P_PWRCYCLE_AFTER_CALLBACK_FOR_D_SENSE        =   0   # Add power cycle after callback to reset initiator D_SENSE handling
   BF_0147585_426568_P_FIX_SRVO_CNTRLR_ID_SPELLING                =   0   # fix spelling of Drive Attribute SRVO_CNTRLR_ID in Servo.py
   FE_0147574_426568_P_FAIL_SAFE_BASED_ON_ERROR_CODE              =   0   # Add capability to make a test fail safe for certain error codes
   FE_0147058_208705_SHORTEN_VBAR_LOGS                            =   0   # Reduce VBAR log sizes
   FE_0147914_231166_P_ADD_SUPPORT_MC_INIT_DIAG                   =   0   # Add ability to init the media cache and use it if verify fails 1 time
   FE_0147919_426568_P_SKIP_PRE2DRIVEATTRRESET_IF_PLR             =   0   # Skip calling function PRE2DriveAttrReset if it is Power Loss Recovery (PLR) in PRE2 since DRIVE_SCORE is reset after PLR
   FE_0147966_231166_P_IGNORE_UNLK_DNLD_FAIL                      =   0   # Ignore unlk download failures in interface download
   FE_0148140_426568_P_FAIL_BPIC_DELTA_GREATER_EQUAL_TO_THRESHOLD =   0   # Fail if the delta in deltaBPICScreen is greater or equal to the threshold limit instead of less than
   BF_0148226_357552_P_CHECK_SECTSIZE_ATTR_EXIST                  =   0   # Check for existence of attribute prior to use
   FE_0148237_357552_P_ADD_HP_SPECIFIC_BGMS_DISABLE               =   0   # Disable BGMS for HP through modified command
   FE_0148305_231166_P_ALLOW_POST_CMT2_DOWNGRADE                  =   0   # Allow drive to downgrade to a lower BG after CMT2- use when autocommit isn't enabled.
   FE_0148599_357552_P_MOVE_RESET_SMART_TO_BEGINNING              =   0   # Move Reset Smart to FIN2 beginning, right after code load
   BF_0148668_357552_P_USE_ATAREADYCHECK_FALSE_PWRCYCLE           =   0   # Utilize TCG, spinup fixes in PowerControl instead of simple powerCycle
   FE_0148727_231166_P_ENABLE_WC_ZONE_XFER                        =   0   # Enable write cache before 598 execution
   FE_0148766_007955_P_FNC2_FAILPROC_DONT_LOAD_CFW_IF_F3_LOADED   =   0
   BF_0149206_231166_P_SET_LOR_AND_UNLOCK_DL_PORT                 =   0   # set LOR and unlock dl port specifically and disable download for init trusted tcg as it isn't required after unlock.
   FE_0149287_426568_P_PASS_IF_DRIVE_SCORE_GREATER_CUST_SCORE     =   0   # Pass a drive if the GOTF drive score is greater than the customer score
   FE_0149287_426568_P_GOTF_SCORE_POWER_LOSS_SAFE                 =   0   # Retain the drive score in the even of a power loss
   WA_0149421_231166_P_REMOVE_SPACES_MODEL_NUM                    =   0   # Strip all white space from beg and end on model number until FIS full space enabled model number support is functional
   FE_0149477_007955_P_SAVE_SAP_ON_NON_DUAL_STAGE_ACT             =   0   # Save SAP in CServoTune : at end of bode - on non dual actuator drives
   WA_0149624_007955_P_ENABLE_RESETWATERFALLATTTRIBUTE_FOR_LCO    =   0   # if site = LCO set resetWaterfallAttribute = 1
   FE_0149739_357552_P_FMT_PI_SKIP_MP3_RESET                      =   0   # Bypass reset mode page 3 if format with PI
   FE_0150126_007955_P_DUMP_SERVO_FLAW_LIST_AT_END_OF_DFS         =   0
   FE_0150178_209214_ZAP_USE_FIXED_ZGAIN                          =   0   # Use a fixed zgain for full stroke zap.
   BF_0150238_231166_P_FIX_DOS_VERIFY_1B_PARSE                    =   0   # Fix the DOS_VERIFY event count to use decimal repr.
   BF_0150521_231166_P_RAW_SAS_MODEL_QUERY                        =   0   # Use raw log grab for model number extraction
   FE_0150604_208705_P_VBAR_HMS_PHASE_2_INCREASE_TGT_CLR          =   0   # Use separate parameter blocks for VBAR_WP versus VBAR_ZN
   FE_0151000_007955_P_TRIPAD_UNVISITED_T118_CALL                 =   0   # Call T118 Tripad Unvisited
   BF_0151111_231166_P_USE_ALL_INTF_CAPABLE_CACHE_CMD             =   0   # Utilize the base class reference to implement enable/disable write cache commands.
   FE_0151342_007955_P_CREATE_P_FMT_T250_RAW_ERROR_RATE_DELTA_TABLE = 0   # table containing delta between T250 & last serial fmt raw error rate data
   FE_0151360_231166_P_ADD_SUPPORT_SAS_SED_CRT2_UNLK              =   0   # Add support to unlock a SAS TCG locked drive in CRT2 if in initiator cell.
   BF_0151621_231166_P_SYNC_BAUD_DIS_INIT_ESLIP_FAIL              =   0   # Fix bug in disableinitaitorcommunication for initiator testing where initial eslip baud command failed and cell to drive uart baud rates were out of sync.
   FE_0151714_208705_IGNORE_HEAD_COUNT_FROM_DEPOP                 =   0   # Use the head count from the familyInfo structure, not the depop head mask
   FE_0151675_231166_P_SUPPORT_SINGLE_DIAG_INIT_SHIP              =   0   # Add support for single diag and step drive initialization to process
   BF_0151846_231166_P_SUPPORT_PN_BASED_SN_FIELD                  =   0   # Add support for SAS PN specific SN shifted offsets into STD_INQUIRY buffer
   FE_0151949_345172_P_SEND_ATTR_PRE2_START_FOR_DAILY_TRACKING_YIELD = 0   # Send attribute PRE2_START for daily tracking yield and easy control between script send attributes and C/R key SBR at Host.
   FE_0167431_345172_P_SEND_ATTR_PRE2_BP                          =   0   # Send attribute PRE2_BP for daily tracking yield and together with separate yield by BP head.
   FE_0152175_007955_ADD_NUM_PHYS_HDS_TO_DUT_OBJ                  =   0
   BF_0152393_231166_P_RE_ADD_LEGACY_ESLIP_PORT_INCR_TMO          =   0   # Add additional timeout wait times for eslip and re-add legacy eslip protocol on exception
   WA_0152247_231166_P_POWER_CYCLE_RETRY_SIM_ERRORS               =   0   # Add feature to implement a power cycle retry for read header error due to read issue after reset
   FE_0152577_231166_P_FIS_SUPPORTS_CUST_MODEL_BRACKETS           =   0   # Add support for [] in CUST_MODEL_NUM dcm validation
   FE_0152759_231166_P_ADD_ROBUST_PN_SN_SEARCH_AND_VALIDATION     =   0   # Add robust SN search for SAS where offset into buffer can be based on PN
   FE_0152922_231166_P_DNLD_U_CODE_PKG_CODE_VER                   =   0   # Add code version verification for codes downloaded using package resolution in download u code
   BF_0152505_231166_P_USE_V_CMD_FMT_DEF_LIST                     =   0   # Use V command as opposed to G,79 command for non resident g list in fnc2
   FE_0153357_007955_P_USE_DETCR_PREAMP_SETUP_STATE               =   0   # Move DETCR preamp setup ( T186, 94 ) into it's own class
   FE_0153649_231166_P_ADD_INC_DRIVE_ATTR                         =   0   # Add SIC rev to attributes
   FE_0153930_007955_P_FMT_CMD_DONT_DEFAULT_DefectListOptions_TO_3 =  0
   FE_0154003_231166_P_ALLOW_BYPASS_MC_CMDS_BASED_F3_FLAG         =   0   # Allow MC commands to be bypassed if we don't detect F3 MC flag enabled
   BF_0153991_231166_P_FIX_DEF_MATCH_PN_ROBUST_SEARCH             =   0   # Fix bug related to FE_0152759_231166_P_ADD_ROBUST_PN_SN_SEARCH_AND_VALIDATION
   FE_0153302_426568_REPLACE_WORKLOAD_SIOP_W_T_597                =   0   # Replace Net App Data SIOP Test with test 597
   BF_0154261_231166_P_FIX_LGC_PHYS_MAP_DEF_PHYS_HDS              =   0   # Fix lgc_phys head map to be based default on physical head map to prevent a detection race condition
   FE_0154423_231166_P_ADD_POST_STATE_TEMP_MEASUREMENT            =   0   # Add a temperature measurement to the end of all states and beginning of end and fail
   FE_0154440_007955_P_SYNC_BAUD_RATE_IN_MQM_GET_MAX_CYLS         =   0   # Add syncBaudRate() in diagGetMaxCylinders to keep from overflowing CM buffer
   FE_0154456_220554_P_POWER_CYCLE_AFTER_RESONANCE_SCREEN         =   0   # Add power cycle at the end of resonance screen
   FE_0154480_220554_P_SPIN_DOWN_BEFORE_T186_DURING_HEAD_CAL      =   0   # Add spin down before T186 during HEAD_CAL
   BF_0154839_231166_P_USE_CERT_TEMP_REF_HDA_SATURATION           =   0   # Use the cert temperature and not cell temperature for hot temp testing
   FE_0154841_231166_P_USE_SEEKS_HEAT_HDA                         =   0   # Utilize random seeks to speed HDA heating
   WA_0154353_350027_LCO_DISABLE_TA_DETECTION_AND_CHARACTERIZATION  = 0   #Add a flag to be able to disable TA Scanning and Characterization
   FE_0154366_231166_P_FDE_OPAL_SUPPORT                           =   0   # Enable support for OPAL FDE type
   BF_0155209_231166_P_FIX_SPT_ALT_BUFFER_DATA_SIZE               =   0   # Fix the call to MakeAlternateBuffer for serial port size to use sector input and not bytes.
   FE_0155581_231166_PROCESS_CUSTOMER_SCREENS_THRU_DCM            =   0   # Add capability to run content by DCM attribute
   BF_0155580_231166_P_DISABLE_517_PWR_CYCLE_SATA                 =   0   # don't run 517 on power cycle in Sata IC.
   FE_0155584_231166_P_RUN_ALL_DIAG_CMDS_LOW_BAUD                 =   0   # Set baud rate to low baud for all diag cmd transfers.
   FE_0134663_006800_P_T186_TDK_HEAD_SUPPORT                      =   0   # pass parameter to test to distinguish between RHO and TDK head.
   FE_0152536_081849_P_AAU_FAULT_DETECTION_ENABLE                 =   0   # Set to enable AAU FAULT detection that forces CPC reset for recovery.
   FE_0155812_007955_P_T176_DONT_RECAL_IF_POLYZAP_SAVED_TO_SAP    =   0   # If Polyzap enabled, dont recalibrate the RW gap cals if previous polyzap values were saved in SAP
   FE_0155919_426568_P_FTP_CCV_FILE                               =   0   # Sends the generated CCV file to the CCV_FILES folder on the Platform server
   FE_0155925_007955_P_T251_SEPERATE_SYS_AREA_PARAMS              =   0   # In simple opti - split out sys area T251 params
   FE_0156020_231166_P_UPLOAD_USER_SLIP_LIST_TBL                  =   0   # Upload P_USER_SLIP_LIST to oracle
   BF_0156216_231166_MODIFY_PROMPT_SEARCH_FOR_SF3_PROMPT_DETECTION=   0   # Add sf3 prompt detection
   WA_0156250_231166_P_DONT_SET_PROC_BAUD_ENABLE_ESLIP            =   0   # Don't transition to PROCESS baud rate on enable eslip.
   FE_0155956_336764_P_SEND_OPER_TES_TIME_AS_ATTRIBUTE            =   0   # Send <oper>_test_time as attribute
   BF_0156515_231166_P_EXT_ON_TIME_INIT_PWR_ON                    =   0   # Use extended RimOn time at first INC power on
   BF_0156739_231166_P_FIX_NO_DEPOP_PHYS_MAP                      =   0   # Fix issue in populating physical head map when not enabled in servo
   BF_0156309_231166_P_FIX_FDE_CHK                                =   0   # Fix the sequence of commands for SED identification in interface INIT
   BF_0157043_231166_P_DISABLE_DRV_MODEL_NUM_VALIDATION           =   0   # Disable validation of DRV_MODEL_NUM against DCM value as there is not way to 100% extract that value from HDA
   BF_0157044_231166_P_NEW_SERVO_PREFIX_DEPOP_RE_MATCH            =   0   # Fix the servo mechanical prefix regex search to search all files using existing file name and correct prefix
   BF_0157147_231166_P_SET_XFER_PRIOR_LOCK_DOWN                   =   0   # Set Xfer rate prior to power cycle after sct-bist command
   BF_0157252_231166_P_USE_NON_EXT_FIELD_28_BIT_VALIDATION        =   0   # Use the non-extended field not the 28bit field to validate the 28bit lba reporting based on ATA8 spec.
   FE_0157407_231166_P_USE_SINGLE_CHAR_SVO_REL_PREFIX             =   0   # Utilize just the first servo char in a match sequence... should be enabled with a change to Servo_Sn_Prefix_Matrix to indicate B\w for the regex servo
   BF_0157429_231166_P_FIX_LOCKED_SED_DRV_INIT                    =   0   # Fix init sequence for sed non locked drives
   BF_0157606_426568_P_POWER_CYCLE_AFTER_SET_MODE_PAGES_ODT       =   0   # Power Cycle after the saved mode pages is set to the default mode pages in ODT screen
   BF_0157675_231166_P_FIX_SIC_TTR_SCALER_TO_MS                   =   0   # Fix TTR attribute in SIC cell to be in MSEC not seconds.
   FE_0157728_426568_P_CONDITIONAL_CODE_DNLD_G_P_MERGE            =   0   # Add ability to conditionally download TGTP code if there are items in the G List needing to be merge
   FE_0157843_426568_P_CUSTOM_SPIN_UP_TIMEOUT                     =   0   # Create Custom SpinUp timout in Power Control
   BF_0157187_231166_P_FIX_BER_DATA_ZONE_PARSE_RETURN             =   0   # Fix getBERDataByZone implementation for current F3 output- deploy into mqm
   FE_0158153_231166_P_ALL_SPT_MQM_NO_ATA_RDY                     =   0   # Modify MQM to have all spt power cycles not check ata ready
   WA_0158450_231166_P_ONLY_RESET_OVL_FOR_SHIP_FLED_FIX           =   0   # Only run removal of overlays for SHIP command to WA FLED
   FE_0158637_426568_P_REMOVE_FULL_PACK_RW_FROM_ODT               =   0   # Remove full pack read and 1/16-16/16 pack write from ODT screen
   FE_0158862_231166_P_VERIFY_OVL_DNLD_U_CODE                     =   0   # Verify if OVL download successfull in dnld code state
   FE_0158866_231166_P_RETRY_DNLD_CODE_NON_COMMIT                 =   0   # Allow retries in donwload u code to commit code if compare check fails
   FE_0158815_208705_VBAR_ZN_MEAS_ONLY                            =   0   # VBAR HMS Phase 4:  Prevent VBAR_ZN from changing formats or waterfalling
   FE_0158827_208705_VBAR_HMS2_WATERFALL                          =   0   # VBAR HMS Phase 4:  Enable waterfall in VBAR_HMS2 state
   WA_0159131_007955_P_PWR_CYCLE_BEFORE_BODE_TEST                 =   0   # Power cycle before bode in CPreParticleSweepBode
   BF_0159246_231166_P_ALWAYS_SET_BAUD_SYNC_CMD                   =   0   # Always set the baud rate even if process thinks it is at the baud rate for syncbaud diag.
   WA_0159248_231166_P_DELAY_DIAG_FOR_MC_INIT                     =   0   # Add a 30 second delay prior to diag usage for MC init.
   WA_0159243_231166_P_FORCE_SET_FDE_TYPE_ATTR                    =   0   # Force set the FDE and Security attributes for TCG to dcm values.
   FE_0159339_007955_P_FAIL_PROC_GET_MR_VALUES_ON_RAMP_186        =   0   # In FAIL_PROC get MR values while on ramp
   FE_0159186_321126_RUN_OPER_BY_VALID_OPER                       =   0   # Run operation based on valid oper but not drive attribute OPER_INDEX
   BF_0159554_426568_P_UNDO_INCORRECT_SETTING_OF_CFG              =   0   # Remove incorrect setting of attribute CFG
   FE_0159615_448877_P_ALLOW_T054_TO_FAIL                         =   0   # Revove T054 fail safe so test does not continue if it fails
   FE_0159624_220554_P_POWER_CYCLE_AT_BEGINNING_OF_SWDVERIFY      =   0   # Add power cycle at beginning of CDualHeaterSWDVerif
   FE_0160361_220554_P_SET_T130_TIMEOUT_TO_3600_SECONDS           =   0   # Increase T130 to report the primary defect list timeout to 3600 seconds.

   BF_0160098_231166_P_DISABLE_READY_VAR_CHECK_DISABLED           =   0   # Disable publishing ata ready time if atareadycheck variable set false
   FE_0160076_336764_FORCED_SEASERIAL_AT_INIT_PRE2                =   0   # Forced Seaserial test at INIT PRE2
   FE_0160412_231166_P_ALLOCATE_TPM_FILE_IN_SIM                   =   0   # Allocate the TPM file to the SIM
   FE_0160791_7955_P_ADD_STATE_TABLE_SWITCH_CONTROL_IN_H_OPT      =   0   # Allows HDSTR states ('H' OPT) to be turned on/off via test switch ( i.e [{'GRENADA' : 1},'H']] )
   BF_0160951_231166_P_ALLOW_SED_REP_INFO_RESP_CALLBACK           =   0   # Allow _REPORT_INFO response as well as _INPROGRESS response to the SED callbacks
   FE_0160920_443615_NUM_WRITES_32BIT_FOR_PF3                     =   0   # Enable this flag to use NUM_WRITES_32BIT parameter for 32bit values in programs which want to use 32bit values
   BF_0161058_395340_P_FIX_RERUNVBAR_COUNT_ON_PWL                 =   0   # Fix bug rerunVbar count when power loss recovery
   FE_0161256_395340_P_CLEAR_MFG_EVAL_FOR_PASSER_OR_FAILED        =   0   # Clear MFG_EVAL value for Passer and Failed.
   FE_0162081_007955_MDWCAL_RUN_T163_T335_AFTER_T185              =   0
   FE_0162093_426568_P_HEAD_VENDOR_STATE_SELECTION                =   0   # Add ability to run a state based on the head vendor
   WA_0162362_007955_SPLIT_TEST_335_INTO_2_CALLS                  =   0   # 1st run OD/MD, 2nd run ID ( w/ error limits applied )
   FE_0162444_208705_ASYMMETRIC_VBAR_HMS                          =   0   # VBAR HMS:  Adjust high-cap zones just enough to offset low-cap adjustments
   BF_0162483_426568_P_SKIP_POWER_CYCLES_IN_DISABLE_INITIATOR     =   0   # Disable the power off power on calls when disabling the initiator
   GA_0160140_350027_REPORT_CHANNEL_DIE_TEMP_THROUGHOUT_PROCESS   =   0   # Gadget to report channel die temp at end of process states when SF3 is on-drive
   FE_0162716_395340_P_MQM_REWORK_FOR_PRE_ODT_SS                  =   0   # Add new sequest test on PRE_ODT_SS for rework condition.
   BF_0162753_231166_P_ALWAYS_PWR_CYCLE_PRE_DNLD                  =   0   # Power cycle prior to download in base_SerialTest to
   BF_0162945_231166_P_FIX_APM_DISABLE_DEF_SPIN_PIN               =   0   # Fix issue where ESC key as APM disable causes drive to be stuck in BFW
   WA_0162966_231166_P_ALLOW_EXT_TIME_DEFERRED_SPIN_BFW_TRANS     =   0   # Allow for extra time if testing F3 QNR in SAS slot for APM/Deferred to be disabled
   WA_0163780_231166_P_DO_NOT_ENABLE_SWD_FOR_AFS                  =   0   # Don't enable SWD agc unsafes for afs
   BF_0163148_231166_P_ALLOW_RETRIES_FOR_ENABLE_ESLIP             =   0   # Allow retries for enable eslip
   FE_0163194_395340_P_FIX_ECC_LV_FOR_MAXDELTARAW                 =   0   # Set new ECC_LEVEL to get max delta RAW at serial format
   BF_0163418_231166_P_ECHO_DRV_MODEL_NUM_TO_FIS_DCM              =   0   # Only echo back the drv_model_num to fis- don't validate against dcm
   BF_0163462_007955_REVERSE_IDDEV_AND_VALIDATEDRVSN              =   0   # reverse order of identify device & validate drv sn, so  if exception in oFSO.validateDriveSN(),    oIdentifyDevice will be defined
   BF_0163420_231166_P_UTILIZE_SERIAL_CMD_FOR_SERIAL_FMT_G_LIST   =   0   # Use serial command instead of interface command to dump g list
   BF_0163537_010200_CONSISTENT_PKG_RES_NO_FILE_FOUND_RESPONSE    =   0   # Make the servo and generic Package Resolution getFileName response for "file not found" consistent (return None)
   BF_0163578_231166_P_FIX_DO_SERVO_CMD10_USAGE                   =   0   # Overload usage of SERVO_CMD to allow SERVO_CMD10 output
   BF_0163756_208705_VBAR_HMS_TARG_COPY2                          =   0   # Add TARG_COPY2 after VBAR_WP2 to ensure targets get copied properly
   BF_0163846_231166_P_SATA_DNLD_ROBUSTNESS                       =   0   # Add code download robustness improvements for sata
   WA_0164214_231166_P_DISABLE_DIAGS_IN_INTERFACE_OPS             =   0   # disable diagnostics if running in interface ops
   BF_0164283_007955_FIX_ZONEDATA_DICT_STRUCT                     =   0   # fix creation of zoneData dictionary in getBERDataByZone
   FE_0163822_341036_AFH_DISABLE_VCAT_FOR_T135                    =   0   # AFH disable VCAT during contact detect.
   FE_0164089_395340_P_B2D2_SELECTION_FEATURE                     =   0   # Add B2D2 selection feature by ProcessControl file.
   BF_0164148_321126_IGNORE_GETPWRONSPINUPTIME_FOR_CPSSPTRISER    =   0   # Don't call cpc function GetPwrOnSpinUpTime if drive run with new cpc spt riser
   BF_0164505_231166_P_ALWAYS_PWR_CYCL_POST_SPT_DNLD              =   0   # Always power cycle the drive at the end of serial download before we verify the code on hda
   FE_0164651_426568_P_DELTA_BER_MEAN_BY_HEAD                     =   0   # Delta BER by Head
   ZFS                                                            =   0   # Combined ZAP and flawscan
   ZFS_LEGACY_MODE                                                =   0   # This method of ZAP uses T275 and does not write the flawscan pattern
   FE_0234376_229876_T109_READ_ZFS                                =   0   # Read ZAP flawscan
   BF_0164962_231166_P_FIX_DOS_CHK_THRESH_ENABLE                  =   0   # fix the dos check thresholds to be >0 and not explicit
   FE_0165086_231166_P_INGORE_TTR_IN_FIN2_DL                      =   0   # Ignore the TTR time in interface download
   FE_0165113_231166_P_SIC_PHY_READY_TTR                          =   0   # Use PHY ready to detect TTR as well as send options bits and mean adjust the result
   FE_0165256_208705_VBAR_STORE_TEMP                              =   0   # Store VBAR temperature for settling table
   FE_0165107_163023_P_FIX_TPII_WITH_PRESET_IN_VBAR               =   0   # In VBAR process, to write preset TPI settings and keep them unchaged across the VBAR process
   BF_0165552_231166_P_RESET_COM_PWRCYCLE_INITIATOR               =   0   # Fix issue where powercycle rim didn't reset the com mode
   FE_0165687_341036_AFH_SKIP_DELTA_VBAR_CHK_AFH2B_READER_HTR     =   0   # For DH skip DELTA VBAR check only in AFH2B for the READER_HEATER
   BF_0165869_231166_P_SIC_PHY_TTR_METRIC                         =   0   # Fix issue where 528 was raising a failure and not allowing the parametric adjustment to happen in process
   BF_0165911_231166_P_FIX_NEXTPRE2_WITH_PLR                      =   0   # Fix issue with 11044 in PLR with nextpre2 function
   FE_0165920_341036_DISABLE_READER_HEATER_CONTACT_DETECT_AFH2    =   0
   FE_0166236_010200_ADD_VCM_SENSITIVITY_ON_DS_PRODUCTS           =   0   # Measure single stage (VCM) sensitivity on dual stage products, using T282
   FE_0161626_231166_P_DISABLE_TEMP_MSR_BLUE_NUN                  =   0   # Disable the apple temperature collection in amps prior to blue nun
   BF_0166446_231166_P_FIX_ZONE_BER_PARSING_FOR_LARGE_ERROR       =   0   # Fix issue where large numbers in ber data break zone parsing
   FE_0166516_007867_PF3_VBAR_CONSOLIDATED_T211_CALLS             =   0   # Consolidate Test 211 calls for multiple heads and zones to reduce CM loading and log file size.
   BF_0166867_231166_P_FIX_CRT2_SF3_INIT_DRV_INFO_DETCT           =   0   # fix issue with power cycle transitions in CRT2 not id'ing the code type
   BF_0167020_231166_P_SF3_DETECTION_ROBUSTNESS                   =   0   # Robustness changes for sf3 mode detection
   BF_0166991_231166_P_USE_PROD_MODE_DEV_PROD_HOSTSITE_FIX        =   0   # Add production mode configvar to replace the site id as testing modfication.
   FE_0167297_395340_P_CHECK_P233_TABLE_AFTER_UNLOAD              =   0   # Check Data P233 Table after unload data from ST240
   FE_0167320_007955_CREATE_P_DELTA_BURNISH_TA_SUM_COMBO          =   0   # combo of P_AFH_DH_BURNISH_CHECK and P134_TA_SUM_HD2 for GOTF
   FE_0167481_007955_ZAP_OFF_DURING_LUL_T109                      =   0
   FE_0166634_231166_SAS_SMART_FH_TRACK_INIT                      =   0   # init smart FH alt tone tracks for sas
   FE_0166720_407749_P_SENDING_ATTR_BPI_TPI_INFO_FOR_ADG_DISPOSE  =   0   # Enable sending attribute BPI_CAP_MIN, BPI_CAP_AVG, TPI_CAP_MIN and TPI_CAP_AVG for ADG dispose improment.
   FE_0168027_007867_USE_PHYS_HDS_IN_VBAR_DICT                    =   0   # Use physical rather than logical head indexing in the VBAR meas dictionary so Depop on the Fly will function correctly.
   WA_0168153_007955_USE_AP2_WITH_BLUENUNSLIDE                    =   0   # Associate AP2 with Bluenun slide instead of AP3
   FE_0168081_347508_ENABLE_SAMTOL                                =   0   # Run state to check if servo supports SAMTOL, if supported it will enable the SAMTOL bit
   BF_0168507_231166_P_ROBUST_CHANGE_TO_BER_BY_ZONE_PARSE         =   0   # Make the ber parsing more robust when syntax errors occur in by zone parsing.
   FE_0168661_231166_P_ALLOW_SAS_RESET_DOS                        =   0   # Allow SAS to reset DOS
   FE_0168477_209214_ZAP_REV_ALLOCATION                           =   0   # Disable read ZAP and increase write zap
   BF_0168885_231166_P_REORDER_INTF_INIT_TEMP_CHECK_AT_END        =   0   # Reorder the interface init to fix sata pois mis-match sequence
   FE_0169171_231166_MC_PART_B_SEP_TBL_PARSE                      =   0   # Flag the MC Zone parsing... there is a PF3 bug causing erroneous parsing out of the log.
   BF_0169360_231166_P_ALLOW_CHAR_ROBUST_BER_BY_ZONE              =   0   # Add more robust output parsing to ber by zone $ output
   FE_0169221_007867_VBAR_ADD_SETTLING_CLR_CALC                   =   0   # Add clearance settling correction to the clearance settling algorithm.
   FE_0169378_475827_ADD_SPINUP_BEFORE_T177                       =   0   # Add a spinup call before T177 in HEAD_CAL.  Fixes servo failure for Lombard
   BF_0169635_231166_P_USE_CERT_OPER_DUT                          =   0   # Use dut cert oper instead of power control cert oper
   BF_0169624_007955_USE_CAMPSCheck_IN_CCV                        =   0
   FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS              =   0
   WA_0169062_470167_P_GET_CURRENT_B2D2_RIMTYPE                   =   0   # Fix get new RimType for B2D2 operation
   WA_0171457_231166_DO_NOT_EXEC_G_LIST_CHECK                     =   0   # Add WA to not execute G list pull due to failures with sas oommand.
   FE_0171507_231166_P_SERIAL_CMDS_SAS_FORMAT_IN_IO               =   0   # Use spt diags in io for sas check merge g
   BF_0170582_208705_BPI_NOMINAL_CAPS                             =   0   # Force format reset before BPI Nominal measurements.
   BF_0170793_231166_P_FIX_ZAP_CCV_CHECK_EXACT_PARSE              =   0   # Fix CCV parse of zap status
   BF_0170041_409401_P_FIX_11049_DRIVE_SKIP_REPLUG_AFTER_DONE_AFH4 =  0   # Bug fix on EC11049@CRT2 (Drive skip re-plug flow after done AFH track cleanup)
   WA_0171001_395340_P_CHANGE_EC_11049_FROM_T177_HEAD_CAL         =   0   # Raise real error code for T177 "HEAD_CAL" by use T208 when T177 faili EC11049
   FE_0171260_231166_P_F3_CODE_USES_INLINE_PARITY_TRK_OUTPUT_IN_TRK_INFO = 0 # fix issue where trunk code is outputting a new column... on della w/o new rev for this snapshot
   FE_0171570_208705_HMS_MARGIN_RAIL                              =   0   # HMS margin only includes the measured settle amount if it is positive
   WA_0171802_395340_P_PHYSICAL_HEAD_ATTRIBUTE_UPDATE             =   0   # Update Physical Head Attribute to know current heads which are enabled
   BF_0171855_475827_SUPPORT_NEW_R_LIST_FORMAT_FOR_R_LIST_DUMP    =   0   # Support new format of R List to preclude parse error during RListDump in CHK_MRG_G
   FE_0170519_407749_P_HSA_BP_ENABLE_DELTA_BURNISH_AND_OTF_CHECK  =   0   # Enable HSA BP (4.0, 4.5 with 20 Angstrom) delta burnish and OTF check criteria
   WA_0171451_407749_P_DOWNGRADE_TO_SBS_ONLY                      =   0   # Enable for downgrade to SBS only
   FE_0171684_007867_DISPLAY_PICKER_AS_TBL                        =   0   # Convert textual picker data into DBLog Table data.
   BF_0171855_475827_SUPPORT_NEW_R_LIST_FORMAT_FOR_R_LIST_DUMP    =   0   # Support new format of R List to preclude parse error during RListDump in CHK_MRG_G
   FE_0172018_208705_P_ENABLE_HMS_2PT                             =   0   # VBAR HMS:  Enable 2-point crossing algo in T211
   BF_0172797_231166_EXACT_MATCH_DETERMINE_CODE_TYPE              =   0   # Don't modify the existing known code type on drive if we can't exactly id it.
   WA_0173484_231166_P_DO_FPW_2T_PRIOR_TA                         =   0   # Do a full pack 2T write prior to TA scan to fix any wedge setup discrepencies.
   FE_0173470_007867_WRT_PICKER_ZERO_HOT_WRT_CURR_ADJUST          =   0   # Don't allow the write current hot offset value to be non-zero for TI-3948 preamps.
   FE_0173689_231166_ENABLE_DIE_TEMP_FAIL                         =   0   # Fail drive for die temp beyond max.
   FE_0173804_007955_ADD_T130_TALIST_DATA_TO_DATAFLAWSCAN_TASCAN  =   0   # Option to dump TA list via T130 in TA scan
   FE_0174019_426568_P_PRINT_BERP_SETTING_IN_LOG                  =   0   # This prints the setting of BERP in the log file during tests affected by BERP
   BF_0174032_231166_P_FULL_PWR_CYCLE_ENABLE_INIT_FAIL            =   0   # Fix bug in SAS INIT usage where enable init fails and full power cycle wasn't tried.
   FE_0174396_231166_P_MOVE_CLEANUP_TO_OWN_STATE                  =   0   # Run cleanup as a seperate step in the process
   FE_0174524_426568_P_ENABLE_ATS_CALIBRATION_AFTER_FLAWSCAN      =   0   # Anticipatory Track Seek calibration after Analog flawscan
   WA_0174645_231166_P_PWR_CYCLE_ALL_ON_INVALID_SED               =   0   # Add power cycle for invalid SED responses
   FE_0174482_231166_P_USE_INC_CODE_BY_SOC_TYPE                   =   0   # Add feature to identify codes by SOC type
   FE_0174818_231166_P_RESET_SMART_POST_DL                        =   0   # Reset smart post download micro code
   FE_0174828_231166_P_TTR_REMOVE_INTF_TEMP_MSMT_NON_INIT         =   0   # Remove temp measurement in interface ops if not state == INIT
   FE_0174882_231166_P_PROCESS_PENDING_TO_ALT                     =   0   # Process the pending list into the alt list
   FE_0175236_231166_P_VERIFY_SERVO_CODE_IN_INTF_DNLD             =   0   # Validate servo committed to flash after sfw download
   FE_0175446_231166_P_IV_FILENAME_USAGE_SED                      =   0   # Use IV_FILENAME as opposed to IV_SW_VER to upload IV version used to oracle
   FE_0175461_231166_P_SET_0X80_0_ALL_TRUNK_AFH_STATES            =   0   # Modify code for trunk to accomodate the new Error code on trunk and CWORD usage for trunk code in 135 retry
   BF_0175149_407749_P_COMPART_SCREEN_USE_LGC_INSTEAD_OF_PHYS_HDS =   0   # Use logical rather than physical head, to prevent the issue when drive was depoped head 1.
   FE_0175666_007955_ENABLE_DISABLE_WTF_ATTRS_USING_CONFIGVAR     =   0   # Configvar "RESET_WTF_ATTRS"
   BF_0176258_231166_RE_ENABLE_INTERFACE_END_DUAL_STAGE           =   0   # Fix issue where drive left in diagnostic mode at end of dual stage act check
   FE_0176468_231166_P_REMOVE_PFM_ID_PF3_WRITE                    =   0   # Don't use pf3 to write pfm_id to cap. SF3 will do it.
   FE_0174845_379676_HUMIDITY_SENSOR_CALIBRATION                  =   0   # Adds calls into T235 to log relative humidity and mixed ratio.  Saves these values to the RAP in AFH2.
   FE_0176704_007955_SUPPORT_DEPOP_OTF_SPLIT_VBAR                 =   0   # Split VBAR i.e VBAR_WP1, VBAR_ZN, etc
   FE_0177083_231166_P_SCREEN_DECREASED_SLIP_LIST_ENTRIES         =   0   # Require a 0 degredation of slip lists in backend.
   FE_0178765_231166_P_SAVE_INITIATOR_INFO_FILE                   =   0   # Save information about initiator in pickle file for automated parsing.
   FE_0205626_231166_P_VER_1_INIT_PKL_FILE                        =   0   # Use the version 1 pkl file for saving initiator information
   FE_0216004_433430_ENABLE_CCV_TEST                              =   0
   FE_0227432_433430_IDENTIFY_POSSIBLE_WORK_FLOOR_RELATED_ISSUE   =   0
   BF_0274769_321126_ALLOW_EMPTY_PN_FOR_NIBLETTABLE               =   0   # Allow empty PN for PIF.py/NibletTable
   DUMP_INFO_IN_FAIL_PROC                                         =   0
   ENABLE_PARAJOG_SCREEN                                          =   0
   ENABLE_ADDITIONAL_FLAWSCAN_AT_ID                               =  (0 & ENABLE_PARAJOG_SCREEN ) # enable additional flawscan at ID before actual whole surface flawscan
   FE_0113290_231166_NPT_TARGETS_FROM_PARAM_FOR_T251              =   0
   FE_SGP_348432_TPIMT_BHBZ                                       =   0   # Based on T51 erasure OTF to assign TPI_MARGIN_THRESHOLD scale by head by zone
   FE_SGP_348432_USE_BPI_CFG                                      =   0   # Use BPI config during BPI measurement
   FE_SGP_81592_ADD_CHANNEL_CODE_1_SUPPORT_FOR_9100               =   0   # Add support to handle Marvell 9100 BPI file
   FE_SGP_81592_SUPPORT_DIFFERENT_WFTHRES_IN_1_NIBLET             =   0   # Add code to detect 2 different preamp mfr and pick up the Vbar Wrt Fault Thresh from within the same niblet.
   BF_0177886_231166_P_FIX_XFR_RATE_DIAG_TRANSITION               =   0   # Fix transfer rate initialization after diag commands
   FE_SGP_81592_SUPPORT_FOR_NPT_TGT_LIST_WITH_5_INPUTS            =  (0 & FE_0113290_231166_NPT_TARGETS_FROM_PARAM_FOR_T251)
   FE_SGP_81592_DISABLE_HEATER_RES_MEAS_T80                       =   0   # Disable Test 80, Heater Resistance Measurement from Head_Cal
   FE_SGP_81592_ADD_PWR_CYCLE_BEFORE_CALLING_T191                 =   0   # Workaround for test 191 running into hang between P172_CLR_COEF_ADJ display and T191
   FE_SGP_T191_BPI_PUSH_BY_ZONE                                   =   0
   FE_SGP_81592_SAVING_RD_SCRN2_BER_DATA_TO_ETF                   =   0   # Switch to enable code to support saving BER data from Read_Screen2 into ETF for future references
   FE_SGP_348429_VBAR_TPIM_SLOPE_CAL                              =   0   # Flag to use Slope Cal to provide TPI Mgn Thresh
   FE_0253362_356688_ADC_SUMMARY                                  =   0   # to display P_VBAR_ADC_SUMMARY
   FE_0261758_356688_LBR                                          =   0   # last band recovery
   FE_0335607_356688_P_TRIGGER_LBR_BY_CONDITION                   =   0   # trigger LBR by condition
   FE_0385234_356688_P_MULTI_ID_UMP                               =   0   # Cactus multiple ID ump zones
   FE_SGP_SET_SERIALFMT_OCLIMIT                                   =   0   # Enable scripts to modify OCLimit before running Serial Fmt
   FE_SGP_T250_SER_SYMBOL_UNIT                                    =   0   # Switch to toggle the unit for symbol used in T250, where 0 equ sym per bit & 1 equ sym per sym
   FE_SGP_RELOAD_DEMAND_TABLE_ON_WTF                              =   0   # Reload DemandTable from PIF.py upon waterfall
   FE_SGP_VBAR_SYMBOL_ERROR_RATE                                  =   0   # Use symbol error rate for BPI/TPI measurement (found only in TestParameters.py)
   FE_SGP_VBAR_RUN_RW_OPTI                                        =   0   # Flag to run vbar opti during T211. (found only in TestParameters.py)
   FE_SGP_EN_REPORT_WTF_FAILURE                                   =   0   # Capacity WTF - sending unyielded failcode to FIS
   FE_SGP_EN_REPORT_RESTART_FAILURE                               =   0   # Option to report "PRE2"/"*PRE2" when restart due to waterfall failure
   EN_REPORT_SAME_CAPACITY_WTF                                    =   0   # Option to send unyielded WTF EC to FIS for drive with same capacity but diff tab, 1 = send, 0 = not send
   WTFCheckSectorSize                                             =   0   # check sector size when do waterfall for ADG/rerun/ force WTF drives
   FE_SGP_FORCE_2_RUN_MINIZAP_OR_ENABLE_ZAP                       =   0   # Swtich to run minizap/enable zap depending on current state
   FE_SGP_81592_COLLECT_BER_B4_N_AFTER_RD_OPTI                    =   0   # Flag to enable collection of BER b4 & after channel opti using Test 250
   FE_SGP_81592_COLLECT_ATINBER_DATA_IN_FINE_OPTI                 =   0   # Flag to enable collection of ATI & BER during fine opti state using Test 51 & 250 respectively
   FE_SGP_HSA_OFFSET_SCRN                                         =   0   # Flag to enable screening of uneven "disc to base plate" gap.
   FE_SGP_PREAMP_GAIN_TUNING                                      =   0   # Flag to enable preamp gain tuning using VGA value obtain during seek.
   FE_SGP_SPECIFY_BOX_PADDING_SIZE_DURING_SERIAL_FMT              =   0   # Flag to enable the definition of box padding size during Serial FMT,
   FE_SGP_SUPPORT_OFFTRK_RW_DURING_SERIAL_FMT                     =   0   # Flag to enable the definition of Read & Write OFFTRACK during Serial FMT
   FE_SGP_SKIP_TEST_167_IN_RD_SCRN                                =   0   # Flag to skip test 167 in read_scrn state
   FE_0184276_322482_AFH_64ZONES_T135_SQUEEZE_PARAM               =   0
   FE_0194098_322482_SCREEN_DETCR_OPEN_CONNECTION                 =   0
   FE_SGP_ENABLE_BER_SCREEN_AT_RDSCN1_N_RDSCN2                    =   0   # Flag to enable BER failing criteria during Rd Scrn 1 & 2
   FE_SGP_AUTO_SF3_CODEDL_SELECTION_VIA_HGA_SUPPLIER              =   0   # Flag to allow Codes.py to define STPT (for TDK hds) & STPR (for RHO hds) as 2 separate SF3 code to DL.
   FE_SGP_DEFINE_AABTYPE_IN_CONFIG_VAR_BASED_ON_HGA_SUPPLIER      =   0   # Flag to support definition of AABTYPE_RHO & AABTYPE_TDK in ConfigVars
   FE_SGP_SCREEN_TCC1_USING_MODIFIED_DICT                         =   0   # Flag to enable TCC1 screening in AFH4 using modified dictionary data when calling screenHardFailTCC1_andTCC2 method.
   FE_SGP_348432_SET_CAP_TO_MIN_WHEN_TPIC_BPIC_INVALID            =   0   # Flag to enable feature where a minimum value is assigned to BPIC/TPIC instead of -1 when measurement cannot be obtained due to LLRW
   pztCalTestEnabled                                              =   0
   shockSensorTestEnabled                                         =   0
   pressureSensorEnabled                                          =   0
   WA_SGP_DISABLE_USING_SRV_DATA_ON_DISC                          =   0   # Flag to fix seek error when running Big ZAP.
   WA_SGP_FIX_OVERLAY_NOT_LOADED_WITH_CWORD1_20_IN_T172           =   0   # Flag to run jumper test in order to load SF3 overlay into buffer
   WA_SGP_SAVE_RAPNSAP_B4_OPTIZAP_RETRY                           =   0   # Save a copy of the current SAP & RAP into the Flash b4 retry phastopti
   WA_SGP_PWRCYCLE_PRIOR_2_FINEOPTI                               =   0   # Workaround to avoid T138 hang due to the T251 spin up
   EnableDebugLogging_T598                                        =   0   # Defect list checking after T598
   FE_0007406_402984_USE_INTFTTR_MAX_VALUE                        =   0   # Use the max in twenty power cycle loop value in INFTTR test as TIME_TO_READY value
   NEW_TTR_SPEC_CHECK                                             =   0   # Fail drive if multiple Max TTR above TTR spec.   
   EnableAVScanCalmFeature                                        =   0   # AVSCAN test
   BF_0180078_231166_P_FIX_R_W_BEG_END_CPC_API                    =   0   # Fix issue with CPC api called with incorrect number of parameters in rw beg end
   FE_0179998_231166_P_SUPPORT_DV3_AS_LAST_CONTENT                =   0   # Allow DV3 to indicate long dst is last content- also support content in DCM attributes
   FE_0180513_007955_COMBINE_CRT2_FIN2_CUT2                       =   0   # A merge of CRT2 & CUT2 states into FIN2, for I/O test time savings
   BF_0180787_231166_P_REMOVE_FDE_CALLBACKS_FOR_CHECKFDE          =   0   # fix bug where checkfdestate left the callbacks for fde active.
   BF_0185696_231166_P_DRIVEON_BEFORE_528                         =   0   # Power on drive prior to 528 in SIC... to allow 528 to work properly
   FE_0180710_426568_P_PSID_MSYMK_AUTH_REQUIRED_FOR_SED_ACCESS    =   0   # Must authenticate to both MakerSYMK and PSID to open SED admin session
   FE_0180754_345172_RAMP_TEMP_NOWAIT_HDSTR_SP                    =   0   # Support of Tester to improve ST240 SP report temperature.
   FE_0179705_231166_P_RUN_BLUE_NUN_AT_1_5G                       =   0   # Reduce the transfer rate to 1.5 G for blue nun
   FE_0180898_231166_OPTIMIZE_ATTR_VAL_FUNCS                      =   0   # Optimize the usage of ATTR_VAL as well as utilize re-pull functions for cust_config
   BF_0179267_231166_P_FIX_WWN_CCV_PULL                           =   0   # Fix pull of WWN for drives that get wwn in cust cfg
   FE_0182319_426568_P_SKIP_LBA_MODEL_NUM_CHK_IF_NUM_HEADS_SET    =   0   # Skip ATTR VAL checks if running non native capticity via plugins
   FE_0200009_497324_P_AUTO_RERUN_AND_ZERO_PATTERN_ACTIVITY       =   0   # Add auto rerun if the drive are return result is not 'AAU_MISCOMPARE:Buffer miscompare', if the drive fail EC10158 at T510 and expected result is not zero
   BF_0183298_231166_P_FIX_DRV_MODEL_NUM_ECHO_OPT_ATTRVAL         =   0   # fix issue where drive model num wasn't echo'd for FIS validation
   FE_0184238_475827_P_ADD_RETRIES_FOR_CCVTEST_UDR2_CHK           =   0   # Add retries to Ctrl+L command parsing in CCVTest for robustness
   FE_0181878_007523_CCA_CCV_PROCESS_LCO                          =   0   # Implements CCA CCV testing process in LCO branches
   FE_0184924_231166_P_BYPASS_INIT_PWR_CYCLE_UNLK_AND_SED         =   0   # add feature to bypass init and power cycle if downloading SED sequence or UNLK files- required for SED
   FE_0177786_231166_P_REM_CE_AND_VER_SMART_IN_CLEANUP            =   0   # Disable re ce and verify smart in cleanup
   FE_0185387_231166_P_RECONFIGURE_CONFIGVAR                      =   0   # Allow FIN2 to be a reconfigure operation
   BF_0185687_007955_P_PREVENT_DOWNGRADE_TO_HIGHER_BG             =   0   # Prevent "downgrade" to "higher" business group ( i.e. if started as 'STD' cant accidently be changed to 'OEM1F')
   FE_0185032_231166_P_TIERED_COMMIT_SUPPORT                      =   0   # Implement tiered commit support
   FORCE_TIER_VE                                                  =   0   # Force PN's and flow as tier
   FE_0185033_231166_P_MODULARIZE_DCM_COMMIT                      =   0   # Modularize the DCM ACMT functions for better re-usability
   FE_0213483_009408_DISABLE_DOS_CLEARING_IN_SATA_CCV             =   0   # Disable DOS Clear
   FE_0189561_418088_IRECOVERY_SUPPORT                            =   0   #Enable iRecovery feature
   FE_0190240_007955_USE_FILE_LIST_FUNCTIONS_FROM_DUT_OBJ         =   0   # Use filelist functions in Drive.py - moved from setup.py
   FE_0191007_231166_P_ADD_MC_PART_A_VERIFY_DIAG_CLEANUP          =   0   # Call MC partition a verification diag in cleanup- 1s tt increase
   FE_0178064_231166_P_DISABLE_UDR_CHK_IN_CLEANUP                 =   0   # TT enhancement to only check UDR2 enabled in CCV audit.
   FE_0247889_505898_PRECODER                                     =   0   # Enable precoder register tuning (karnak plus)
   FE_0298712_403980_PRECODER_IN_T251                             =   0   # Added precoder tuning in T251 (CheopsAM)
   FE_0311911_403980_P_PRECODER_IN_READ_OPTI_ONLY                 =  (0 & FE_0298712_403980_PRECODER_IN_T251) # Run T251 precoder tuning in READ_OPTI only.
   luxorM93_channel_switch                                        =   0   # Set when running LuxorM9300 boards
   CPCWriteReadRemoval                                            =   0   # For WR_VERIFY IO TT reduction
   IOWriteReadRemoval                                             =   0   # For WR_VERIFY IO TT reduction
   FE_SGP_402984_P_SUPPRESS_SUPPRESSED_OUTPUT_INFO                =   0   # Dblog size reduction. Suppress suppressed output info.
   FE_0166305_357263_T135_RAP_CONSISTENCY_CHECK                   =   0
   FE_0177394_433430_SPINUP_FOR_POIS_ENABLED                      =   0
   SDBP_TN_GET_JUMPER_SETTING                                     =   0   # SDBP using Test Number Flags
   SDBP_TN_GET_NUMBER_OF_HEADS_AND_ZONES                          =   0   # SDBP using Test Number Flags
   SDBP_TN_GET_BASIC_DRIVE_INFORMATION                            =   0   # SDBP using Test Number Flags
   SDBP_TN_GET_UDR2                                               =   0   # SDBP using Test Number Flags
   CHECK_SUPERPARITY_INVALID_RATIO                                =   0   #Check SuperParityInvalidRatio against spec at FIN2, S_PARITY_CHK
   FE_AFH_BURNISH_CHECK_BY_RDDAC                                  =   0
   ADAPTIVE_GUARD_BAND                                            =   0   # Enable Adaptive guard band
   Enable_ATAFS                                                   =   0
   COTTONWOOD                                                     =   0
   ROSEWOOD7                                                      =   0
   ROSEWOOD72D                                                    =   0
   ANGSANAH                                                       =   0
   CHENGAI                                                        =   0
   YARRAR                                                         =   0
   KARNAK                                                         =   0
   KARNAKPLUSBP9                                                  =   0
   CHENGAI_ZNSRV_BP10                                             =   0
   THIRTY_TRACKS_PER_BAND                                         =   0
   M10P                                                           =   0
   M11P                                                           =   0
   M0A3000                                                        =   0
   M0A3100                                                        =   0
   M0A4100                                                        =   0
   M0A4200                                                        =   0
   M0A5100                                                        =   0
   M1A1000                                                        =   0
   M1A2000                                                        =   0
   M11P_BRING_UP                                                  =   0
   RUN_ATI_IN_VBAR                                                =   0
   TPIM_SMOOTH                                                    =   0   # Enable Smoothing in TPIM
   FE_0285640_348429_VBAR_ATI_CHECK_FOR_STE                       =   0   # Switch to check STE Tracks before compensating for ATI
   FE_0285640_348429_VBAR_ATI_CHECK_FOR_STE_10K                   =   0   # Switch to check STE Tracks using 10k Writes before compensating for ATI
   FE_0285640_348429_VBAR_STE_BACKOFF_BPI                         =   0   # Switch to backoff BPI when detected STe ISSUE during VBAR ATI
   FE_0316337_348429_VBAR_ATI_STEEP_BACKOFF                       =   0   # Switch to put additional backoff when detect Steep ATI Degradation
   RUN_HEAD_POLARITY_TEST                                         =   0
   IS_2D_DRV                                                      =   0
   BodeScreen                                                     =   0
   FE_0243291_305538_VCM_PZT_SCREENING                            =   0
   FE_0243291_305538_VCM_PZT_SCREENING_FAIL                       =   0
   BodeScreen_Fail_Enabled                                        =   0
   RUN_HEAD_SCREEN                                                =   0
   FE_SGP_OPTIZAP_ADDED                                           =   0
   VBAR_TPI_MARGIN_THRESHOLD_BY_HD_BY_ZN                          =   0
   RUN_ZEST                                                       =   0
   EnableT250DataSavingToSIM                                      =   0
   AFH3_ENABLED                                                   =   0
   ADAPTIVE_GUARD_BAND                                            =   0
   EnableVariableGB_by_Ramp                                       =   0
   RUN_T176_IN_VBAR                                               =   0
   RUN_FINE_UJOG_IN_VBAR                                          =   0
   OW_FAIL_ENABLE                                                 =   0   #Turn on Over Write test failing criteria
   OW_DATA_COLLECTION                                             =   (0 & DATA_COLLECTION_ON)  #Turn on Over Write test data collection in PRE2,CRT2
   Enable_OAR_PAD                                                 =   0   # This switch will map OAR failure tracks as skip trk in servo defect lists.
   Enable_OAR_SCREEN_Failling_Spec                                =   0   # This switch will enable screening of OAR with threshold defined in TestParameters.py
   FE_0304753_348085_P_SEGMENTED_BER                              =   0
   Enable_BPIC_ZONE_0_BY_FSOW_AND_SEGMENT                         =   0   # This switch will enable BPIC tweaking at zone 0 using First Sector OverWrite and Segment BER data
   BF_0179082_231166_P_INCREASE_PARAMETRIC_FILE_MARGINS           =   0
   FE_SGP_81592_ENABLE_2_PLUG_PROCESS_FLOW                        =   0   # Set to 1 in order to enable 2-plug process flow in state table
   VBAR_CHECK_IMBALANCED_HEAD                                     =   0
   VBAR_CHECK_MINIMUM_THRUPUT                                     =   0
   FE_SGP_402984_ALLOW_MULTIPLE_FAIL_STATE_RETRIES                =   0   # Allow multiple state retries during mass pro
   VBART51_MEASURE_ODTRACK                                        =   0   # Enable VBAR T51 measure on OD Tracks of OD ZOnes
   VBAR_T51_STEP_FOLLOW_SERPENT                                   =   0   # Flag to use smallest serpent width step in T51 Measurements
   VBAR_T51_ITER_OPTIMIZATION                                     =   0   # Flag to use a default offset when OTF BER is saturated at ATIC
   CAL_TRUE_MAX_CAPACITY                                          =   0
   FE_0188217_357260_P_AUTO_DETECT_TRACK_INFO                     =   0   # Detect various return formats when retrieving track data
   RUN_F3_BER                                                     =   0
   RUN_WEAK_WR_DELTABER                                           =   0
   RUN_APO_DELTABER                                               =   0
   RUN_PRE_HEAT_OPTI                                              =   0   # this switch will enable PRE_HEAT_OPTI test in CRT2, at this state, only for collectin data
   FE_0189781_357595_HEAD_RECOVERY                                =   0
   FE_0189781_357595_HEAD_RECOVERY_VMM_DATA_COLLECTION            =   0
   FE_0193449_231166_P_DL1_SUPPORT                                =   0   # Add support for DL1 and cust testname 2 and 3
   FE_0193436_231166_P_SUPPORT_FW_NAME_REV_25                     =   0   # Add support for the FW name convention rev 2.5 includes SFWTGT and extended package revision support
   RUN_VBIAS_T186                                                 =   0
   RUN_VBIAS_T186_A2D                                             =   0
   RUN_T191_HIRP_OPEN_LOOP                                        =   0
   DISPLAY_SMR_FMT_SUMMARY                                        =   0
   RUN_VWFT_SUPPORT                                               =   0
   RUN_STRONG_WRT_SCREEN                                          =   0
   ADD_SPINUP_AFTER_UPDATING_FLASH                                =   0
   AGC_SCRN_DESTROKE                                              =   0   # Enable ADC Screen Destroke without new RAP(same as YarraBP)
   AGC_DATA_COLLECTION                                            =   0   # Enable AGC Data Collection
   AGC_SCRN_DESTROKE_WITH_NEW_RAP                                 =   0   # Enable ADC Screen Destroke wtih new RAP
   RUN_T195_IN_FNC2_CRT2                                          =   0
   FE_0253168_403980_RD_OPTI_ODD_ZONE_COPY_TO_EVEN                =   0   # opti on odd zones, copy results to adjacent even zones
   FE_0271421_403980_P_ZONE_COPY_OPTIONS                          =   0   # opti on middle zones, copy results to zones on both side
   TTR_REDUCED_PARAMS_T251                                        =   0   # reduced params to tune for PreOpti, Bpinominal & Vbar
   TTR_BPINOMINAL_V2                                              =   0   # 2-pt BpiNom 1
   TTR_T176_READ_PC_FILE                                          =   0   # rw_gap_cal - read from pc file
   TTR_BPINOMINAL_V2_CONST_AVG                                    =   0 & (TTR_BPINOMINAL_V2)
   IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT                 =   0
   IN_DRIVE_AFH_COEFF_PER_HEAD_GENERATION_SUPPORT_DATA_COLLECTION =   0
   DOS_THRESHOLD_BY_BG                                            =   0  # this switch will enable test 178 to set Dos STEThresholdScalar, STERange and ATIThresholdScalar   according to drive business  group
   DOS_THRESHOLD_BY_ATI                                           =   0  # set Dos STEThresholdScalar, STERange and ATIThresholdScalar   according to Head's Write Screen ATI result
   Enable_Reconfig_WTF_Niblet_Level_Check                         =   0   # Re-config Waterfall Control
   AFH2_FAIL_BURNISH_RERUN_AFH1                                   =   0
   RUN_4PCT_ZAP                                                   =   0
   RUN_3P5PCT_ZAP                                                 =   0  # RZAP 7% and WZAP 3.5
   RUN_SNO                                                        =   0
   RUN_SNO_PD                                                     =   0
   RUN_FOF_SCREEN                                                 =   0
   GOTF_GRADING_TABLE_BY_RPM                                      =   0   # sync with YarraBP
   RECONFIG_RPM_CHK                                               =   0   # sync with YarraBP
   RUN_LUL_MAX_CURRENT_SCREEN                                     =   0
   BF_0194845_231166_P_EN_ESLIP_POST_FMT_NONMCPREP                =   0   # Enable Eslip post format for prep non mc state
   FAIL_ON_INITIATOR_REVISION_CHECK_FAILURE                       =   0   # Fail if unable to detect SIC revision
   USE_ICMD_DOWNLOAD_RIM_CODE                                     =   0   # Download initiator code using ICmd.downloadIORimCode()
   IO_MQM_SIC_TESTTIME_OPTIMIZATION                               =   0   # IOMQM modules
   T69EWAC_T61OW_LIMIT_FORCE_REZONE                               =   0   # forced rezone based on t61 ow vs t69 ewac criteria
   RUN_SKIPWRITE_SCRN                                             =   0
   RUN_SKIPWRITE_SCRN_FAIL_ENABLE                                 =   0
   RUN_DIBIT_IN_CHANNEL_OPTI                                      =   0
   RESET_TCC1_SLOPE_IF_BOTH_TCC1_AND_BER_OVER_SPEC                =   0   # Reset Tcc1 slope to default vaule if both Tcc1 slope & BER are over spec
   ENABLE_BYPASS_T193_EC10414                                     =   0
   ENABLE_BYPASS_T151_EC10007                                     =   0
   RUN_T150_BEFORE_T176_RETRY                                     =   0
   ENABLE_1ST_MDW_TRACK_CAL                                       =   0
   ENABLE_ON_THE_FLY_DOWNGRADE                                    =   1   # Down grade on the fly by error code
   BF_0196490_231166_P_FIX_TIER_SU_CUST_TEST_CUST_SCREEN          = ( 0 and FE_0185032_231166_P_TIERED_COMMIT_SUPPORT ) # fix bugs related to tier and allow bypass of blue nun if complete
   CHANGE_PREAMP_GAIN_BEFORE_T177_RETRY                           =   0
   ENABLE_HEAD_INSTABILITY_WATERFALL                              =   0   # Waterfall head instability failure
   ENABLE_WATERFALL_OAR                                           =   0   # Waterfall to 320G if fail OAR
   SGP_4K_MAX_LBA_CALCULATION                                     =   0
   FE_SGP_81592_23KHZ_RESONANCE_SCRN_AT_7200RPM                   =   0   # YarraBP feature integration: 23kHz bode scrn @ 7200rpm
   FE_0198029_231166_P_WWN_BEG_AND_END                            =   0   # Write WWN to cap 100% and validate 100% if not tier and not already performed. Perform at SETUP and FIN2
   COMBO_SPEC_SCRN                                                =   0   # enable GMD/NMD combo screen in WRITE_SCRN
   COMBO_SPEC_SCRN_FAIL_ENABLE                                    =   0   # enable fail reporting for COMBO_SPEC_SCRN
   FE_0320123_505235_P_MIN_ERASURE_BER_SCREEN                     =   0   # Enable min erasure BER screen
   FE_0324384_518226_P_CRT2_1K_COMBO_SPEC_SCREEN                  =   0   # CRT2 1K combo spec screen
   ENABLE_DOWNGRADE_ON_ZONE_REMAP                                 =   1   # enable GOTF if zone remap is used.
   PRINT_TABLE_P_DELTA_RRAW                                       =   0
   FE_SGP_81592_REZAP_ON_MAXRRO_EXCEED_LIMIT                      =   0   # switch to enable re-zap (Test 175) when maxRRO (frm Test 33) is greater than limit defined as MAX_RRO (in ServoParameters.py)
   FE_0198600_231166_P_SEND_CMT2_INLINE_EVENT                     =   0   # Send CMT2 event during COMMIT operation.
   FE_SGP_505235_MOVING_REZAP_TO_INDIVIDUAL_TEST                  =   0   # moving re-zap routine to an individual test to facilitate test time analysis
   FE_SGP_505235_ENABLE_REZAP_ATTRIBUTE                           =   0
   FE_SGP_517205_TIMEOUT_REZAP_ATTRIBUTE                          =   0   # enable rerun of re-zap if D_FLAWSCAN -> Test 109 time out (EC 11049)
   NoIO                                                           =   0   # No-IO FIN2 Support for SBS
   FORCE_SERIAL_ICMD                                              =   0   # if 1, then force serial commands, even in IO cells
   SI_SERIAL_ONLY                                                 =   0   # if 1 force use SI serial port only (no interface)
   FORCE_IO_FIN2                                                  =   0   # if 1, force to run CUT2 (FIN2 in CPC/SI commands) (for development)
   SP_RETRY_WORKAROUND                                            =   0   # if 1, workaround SP retries not as robust as IO
   FE_0246520_356922_SPMQM_Y2_RETRY                               =   0   # Level F Y2 Retry setting after power cycle
   FE_0249024_356922_CTRLZ_Y2_RETRY                               =   0   # Level F Y2 Retry setting after ctrlz
   FE_0255791_356922_SPMQM_ZONETRUPUT_WRITE_READ                  =   0   # SPMQM IDT_PM_ZONETHRUPUT - Do Write Followed by Read
   FE_0314744_496648_GET_CAP_VAL_USING_DETS                       =   0   # get cap values using dets command
   RW72D_SBS_RETAIL_MQM                                           =   0   # RW72D SBS MQM modules

   FE_AFH4_TRACK_CLEAN_UP                                         =   0
   FE_SGP_81592_TRIGGER_PWR_CYL_ON_1_RETRY_OF_ESLIP_RECOVERY      =   0   # Switch to enable only 1 retry to establish ESLIP comm before a pwr cycle is triggered.
   FE_SGP_81592_ADD_FULL_STROKE_RND_SK_IN_BASIC_SWEEP_2_IMPROVE_T136  =  0  # Switch to add test 30 full stroke rnd sk in basic sweep.
   CHECK_FAILURE_FOR_EC10522_IN_RS2A_2C_2H                        =   0   # Enable to allow failure for EC10522 in READ_SCRN2A, READ_SCRN2C & READ_SCRN2H.
   HSC_BASED_TCS_CAL                                              =   0   # NCTC HSC based TCS Cal
   NCTC_CLOSED_LOOP                                               =   0   # NCTC HSC based TCS Cal Closed Loop
   HSC_SEEK_LOSS_CAL                                              =   0   # HSC Seek Loss Profile
   ENABLE_MIN_HEAT_RECOVERY                                       =   0   # Enable minimum heat recovery
   INITIALIZE_FLAW_LIST_BEFORE_FULL_ZAP                           =   0
   ENABLE_THERMAL_SHOCK_RECOVERY_V3                               =   0   # Screen head instability by doing TSR using T297 data.
   FE_0314308_403980_P_ON_TSHR_PRE2                               =   0   # Enable TSHR in PRE2 for T297 head instability failed drives.
   FE_0314308_403980_P_ON_TSHR_FNC2                               =   0   # Enable TSHR in FNC2 for T250 DBS head instability failed drives.
   FE_0322846_403980_P_DUAL_HEATER_N_BIAS_TSHR                    =   0   # Enable writer heater and voltage bias support during T72 thermal shock head recovery.
   USE_T72_VMM_TO_CHK_HD_INSTABILITY                              =   0   # using T72 (VMM) fro thermal shock head
   ENABLE_T315_SCRN                                               =   0   # Screen head instability using P315_INSTABILITY_METRIC data
   RD_OPTI_SEPARATE_PARM_FOR_320G                                 =   0   # use different read opti parm for 320G.
   ENABLE_TCC_RESET_BY_HEAD_BEFORE_AFH4                           =   0   # Use to enable TCS RESET by head before AFH4
   FE_0205578_348432_T118_PADDING_BY_VBAR                         =   0   # T118 padding by vbar
   ENABLE_T118_EXTEND_ISOLATED_DEFECT_PADDING                     =   0   # Enable T118 extend isolated defect padding. (Requested by Sebastian to close RW2D Relia MSD NMD issue.)
   FE_0202455_231166_P_RESET_XFER_CAP_POST_DL                     =   0   # Reset the max transfer rate attempt attribute XFER_CAP after download u code successfully completes.
   BPICHMS                                                        =   0   # Quick BPI at Backoff Clearance
   RUN_TEST_315                                                   =   0
   HARD_CODE_SERIAL_FORMAT_CMD                                    =   0
   ENABLE_CLR_SETTLING_STATE                                      =   0
   Delta_BER_IN_CLR_SETTLING                                      =   0
   CLR_SETTLING_CLOSEDLOOP                                        =   0
   ENABLE_HMSCAP_SCREEN                                           =   0   # enable HMSCAP screen
   ENABLE_CSC_SCREEN                                              =   0   # enable CSC screen
   ENABLE_SCRN_HEAD_INSTABILITY_BY_SOVA_DATA_ERR                  =   0   # enable screen head instability by sova data err
   ENABLE_DATA_COLLECTION_IN_READSCRN2H_FOR_HEAD_INSTABILITY_SCRN =   0   # enable data collection in readscrn2h for head instability screen by sova data err
   ENABLE_DATA_COLLECTION_IN_READSCRN2_FOR_HEAD_INSTABILITY_SCRN  =   0   # enable data collection in readscrn2 for head instability screen by sova data err
   ENABLE_HEAD_INSTABILITY_SCRN_IN_READSCRN2                      =   0   # enable head instability screen by sova datsa err in readscrn2
   FE_0368834_505898_P_MARGINAL_SOVA_HEAD_INSTABILITY_SCRN        =   0   # enable marginal sova head instability screen
   FE_SGP_81592_PWRCYCLE_RETRY_WHEN_T175_REPORT_EC11087_IN_ZAP    =   0   # Added pwr cycle n retry once if Test 175 reported EC11087 (hang) in FNC2 ZAP state.
   REDUCE_LOG_SIZE                                                =   0
   CLEAR_DATA_SCRUB_TABLE_AFTER_CLEAR_ALT_LIST                    =   0
   ENABLE_DESTROKE_BASE_ON_T193_CHROME                            =   0   # enable Destroke base on T193 Chrome
   FE_0208720_470167_P_AUTO_DOWNGRADE_BLUENUN_FAIL_FOR_APPLE      =   0   # Adding auto downgrade (GOTF) for drives apple that failing EC14520 at Bluenun Scan after downgrade complete need to download new TGTA
   FE_SGP_402984_RAISE_EWLM_CLEAR_FAILURE                         =   0   # Raise exception if EWLM SMART log page B6h not cleared
   BF_0217062_347506_RESET_BIST_SPEED_AFTER_DOWNLOAD              =   0   # Reset SCT-BIST to nominal speed after download to clear a locked-down speed from previous process run.  Firmware does not reset upon download so process needs to do so.
   USE_ZERO_LATENCY_WRITE_IN_T50_T51                              =   0   # set to 0x10 (cword1 bit 4) to turn on ZLW
   FE_SGP_81592_DISPLAY_ZAP_AUDIT_STATS_IN_OPTIZAP                =   0   # enable displaying of zap audit stats during minizap
   SKIP_HIRP1A                                                    =   0   # bypass HIRP1A states
   AutoFAEnabled                                                  =   0   # enable auto FA
   AutoFA_IDDIS_Enabled                                           =   0   # enable DDIS2 opration
   SKIPZONE                                                       =   0
   VARIABLE_SPARES                                                =   0   # enable variable spare
   FE_0349420_356688_P_ENABLE_OPTI                                =   0   # run opti when bpi adjust triggered
   FE_0319957_356688_P_STORE_BPIP_MAX_IN_SIM                      =   0   # store BPIP_MAX to SIM to support variable spare BPI margin check
   FE_0363840_356688_P_ENABLE_GT_WRITE                            =   0   # write last trk of each zone to overwirte Aperio left over signal between the zone to zone boundary.
   FE_ENABLE_SFT_BEATUP                                           =   0   # enable MQM beatup after serial format.
   FE_0221005_504374_P_3TIER_MULTI_OPER                           =   0   # To be able to run Serial Port only states within the 3-Tier flow and structure
   FE_ENABLE_PREAMP_OVERHEAT_SCRN                                 =   0   # enable preamp over heat scrn
   TESTS_FOR_JOINT_LAB                                            =   0   # enable tests required for Joint Lab Project.
   FE_0219921_402984_ENABLE_CLEAR_EWLM                            =   0   # Activate clearing of EWLM
   BYPASS_N2_CMD                                                  =   0   # For AngH product, F3 code not yet ready for /1N2
   FE_0221365_402984_RESTORE_OVERLAY                              =   0   # Recover TGT and OVL codes prior to GIO or MQM
   IS_QUICK_FMT                                                   =   0
   OAR_CW_SEC                                                     =   0   # OAR by codeword or sector segment
   ENABLE_DIHA_FOR_INSTABLE_HD_SCRN                               =   0   # DIHA for Heading Screening
   ENABLE_WRITER_THERMAL_CLR_COEF_CAL                             =   0   # Writer TCC value calculation
   FE_HEATER_RELIEF_RECONFIG                                      =   0   # Heater relief reconfiguration
   FE_HEATER_RELIEF_RECONFIG_FORCE_ON                             =   0   # Heater relief reconfiguration
   BF_0224594_358501_LIMIT_MIN_BPIC_SET_DURING_HMSADJ             =   0   # To limit the Min BPIC that VBAR HMS ADJ can adjust to
   FE_TRIPLET_WPC_TUNING                                          =   0  # Enable WPC Tunng during Triplet Opti
   FE_TRIPLET_WPC_TUNING_PF3_VERSION                              =   0 & FE_TRIPLET_WPC_TUNING  # Only involves PF3 Changes as of this time
   FE_ENHANCED_TRIPLET_OPTI                                       =   0   # Triplet OSD/OSA Limiting for recovery of strong write
   FE_0251897_505235_STORE_WPC_RANGE_IN_SIM                       =   0 & FE_TRIPLET_WPC_TUNING # Saving and retrieving WPC range in SIM file
   FE_0191751_231166_P_172_DUMP_PREAMP                            =   0   # Dump preamp regs content via T172
   RUN_T176_INSIDE_VBAR_HMS                                       =   0   # Run st176 inside vbar hms
   ENABLE_SMART_TCS_LIMITS_DATA_COLLECTION                        =   0   # enable smart TCS limits for data collection only
   ENABLE_SMART_TCS_LIMITS                                        =   0   # enable smart TCS limits
   INIT_CONGEN_SKIP                                               =   0   # Skip Init Congen
   RUN_HSC_OD_ID                                                  =   0   # Run HSC OD ID
   T118_OPTIMIZED_PADDING_PARAMETERS                              =   0   # Flag to select T118 optimized padding parameters
   FLAWSCAN_ADAPT_THRES_TTR_FOR_WTF                               =   0   # Flag to enable flawscan adaptive threshold testime reduction for WTF drive.
   FE_0168920_322482_ADAPTIVE_THRESHOLD_FLAWSCAN_LSI              =   0   # Flag to enable flawscan adaptive QMLVL (LSI - MMSP)
   BF_0230280_358501_FIX_WRONG_WRITE_CURRENT_SAVED_IN_TRIPLET_OPTI =  0   # This is to fix a bug where Iw value exceeds maximum allowed value.
   IS_FAFH                                                        =   1
   DISPLAY_FAFH_PARAM_FILE_FOR_DEBUG                              =   1
   FE_ENABLE_MT50_10_DATA_COLLECTION                              =   0   # run MT50/10 in PRE2 after EWAC/WPE test
   FE_SGP_505235_MDWCAL_INPLACE_DESTROKE                          =   0   # In-place destroke for MDW_CAL with EC11216
   RUN_T250_AFTER_ZAP_FLAWSCAN                                    =   0
   RUN_T250_3_TIMES_ON_FAILED_DRIVES                              =   0
   FE_SGP_ENABLE_HMS_ITER_VIA_EWAC_RESULT                         =   0   # Switch to enable triggering of HMS iteraion using EWAC data/results
   DISABLE_UNLOAD_OPER_FOF_SCRN                                   =   0   # Run unload operation to ramp
   RUN_MOTOR_JITTER_SCRN                                          =   0   # Run Motor Jitter Screen
   RUN_ATS_SEEK_TUNING                                            =   0   # Run ATS Seek Tuning
   FE_0238194_348432_T109_REWRITE_BEFORE_VERIFY_READ              =   0   # Rewrite once before first verify read
   ENABLE_T175_ZAP_CONTROL                                        =   0   # Uses T175 to turn ZAP on/off instead of T011 & T178. Reduce CM load.
   FE_0238515_081592_SET_ZAP_SEC_CYL_TO_20PCT_OF_MAX_TRK          =   0   # Update SEC_CYL parms for Test 175 to 20% of max trk of every hd before calling T175
   FE_0228550_357260_P_LIMIT_LOGICAL_TRACK_RANGE_PER_PHYSICAL_MAX =   0   # For Track Cleanup calculations, use Log Trk of Max Physical track as max Logical (Accouts for cases where additional log track may exist - e.g. Media Cache
   BF_0209197_357260_P_TRACK_CLEANUP_HANDLE_MAX_TRACK             =   0   # Handle cases at or near end of logical space
   BF_0219840_357260_P_USE_DEFECT_LOG_TO_MANAGE_TRACK_CLEANUP_ERRORS =  0 # Use Defect Log to track diag errors during writeTrackRange() (TRACK_CLEANUP)_
   FE_0252611_433430_CLEAR_UDS                                    =   0   # Clear UDS (Unified Debug System) at end of FIN2
   FE_0243151_403980_AVERAGE_RAP_REG_VALUES                       =   0   # Read RAP register values from all heads and zones, find average and save the average value back to RAP.
   FE_0252611_433430_CLEAR_UDS                                    =   0   # Clear UDS logs at end of FIN2
   ENABLE_TCC_SCRN_IN_AFH4                                        =   0   # Screen TCC in AFH4
   ENABLE_HEAD_SCRN_IN_PRE2                                       =   0   # Enable Head Screen in PRE2
   ENABLE_HEAD_SCRN_IN_FNC2                                       =   0   # Enable Head Screen in FNC2
   ENABLE_HEAD_SCRN_IN_CRT2                                       =   0   # Enable Head Screen in CRT2
   ENABLE_ATE_SCRN                                                =   0   # Enable ATE SCRN
   FE_348429_0247869_TRIPLET_INTEGRATED_ATISTE                    =   0   # Enable ATI/STE Test in Triplet Opti to define the maximum tuneable WP
   FE_0332552_348429_TRIPLET_INTEGRATED_OW_HMS                    =   0   # Enable OW/HMS Test in Triplet Opti to define the minimum tuneable WP
   FE_0334525_348429_INTERPOLATED_DEFAULT_TRIPLET                 =   0   # Interpolated Default Triplet from OD to ID
   FE_0327703_403980_P_CERT_BASED_ATB                             =   0   # Enable CERT_BASED_ATB, in place of bench run ATB done by RSS.
   BF_233858_402984_FIX_IO_DYNAMIC_RIM_TYPE                       =   0   # Fix IO double density cell temperature sharing in dynamic rim type config
   FE_0251909_480505_NEW_TEMP_PROFILE_FOR_ROOM_TEMP_PRE2          =   0   # PRE2~FNC2 (ROOM TEMP) and CRT2~FIN2 (HOT TEMP), PSTR temp control
   FE_0255243_505898_T315_ODD_EVEN_ZONE                           =   0   # Enable Odd/Even test zone selection for head instability
   WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION              =   0   # For SKDC M10P Bring up workaround option
   FE_0258650_480505_SKDC_M10P_PROCESS_TIME_REDUCTION             =   0   # For SKDC M10P Bring up Process Time Reduction items
   FE_0261922_305538_CONSOLIDATE_AFH_TARGET_ZONES                 =   0   # Consolidate all zone bit masks to single T178 call for the same target clearance settings in init rap
   WA_0262223_480505_FIX_QNR_CODE_DOWNLOAD_ISSUE_FOR_PSTR         =   0   # PSTR QNR code download issue (after download power cycle, send serial command)
   WA_0277152_480505_RUN_QUICK_FORMAT_BEFORE_INITMCCACHE          =   0   # Quick Format before initMCCache (/CU2)
   FE_0245993_504374_P_MANUAL_COMMIT_DOWNGRADE_TO_TIER            =   0   # Capability for Manual Commit, 9-Digit CC PN drives to downgrade to Tier tab, if applicable, and follow Tier flow
   DB_0275227_480505_WRITE_SCRN_MONITORING_ONLY                   =   0   # run ATI test w/o screening
   WA_0299052_517205_RECONNECT_AND_CONTINUE_ON_11049_ERR_FOR_T178 =   0   #Ignore all 11049 errors @ T178. Re establish connection and continue
   FE_0303934_517205_SET_OVERSHOOT_PARAM_AT_SETUP_PROC            =   0 # to set write current rise time,Overshoot rise time and overshoot fall time @ PRE2-SETUP_PROC
   
   
   WA_REMOVE_PCBA_SN_CHK_FRM_STATE_TABLE_DURING_EM_PHASE          =   0   # this switch will remove PCBA_SN_CHECK state in PRE2
   SWAPPED_SERIAL_PORT                                            =   0   #(1: Swapped, 0:Direct, default is Direct, Swapped for M8 only)
   SP_TO_POWERBLADE                                               =   0   #(1: PowerBlade, 0:PogoPin, default is PogoPin)
   FORCE_UPDATE_BPI_ALL_HEADS_ALL_ZONES                           =   0   # if enable will update the BPI config all head all zone
                                                                        # during BPIN, BPIN2, WATERFALL
   FE_0242583_433430_RETRIEVE_TABLE_FROM_RESULTSFILE_DIRECTLY     =   0   # CM memory saving, retrieve table records from results file instead of load whole table into memory
   FE_0242599_433430_USE_LIST_FOR_MARGINMATRIX                    =   0   # use list instead of dict for memory saving

   CAL2_OPERATION_ENABLE                                          =   0    # Enable CAL2 operation (split from PRE2 LIN_SCREEN2)
   SDAT2_OPERATION_ENABLE                                         =   0    # Enable SDAT2 operation after FNC2
   FORCE_WTF_SET_ATTR_BY_NIBLET_TABLE                             =   0    # Change waterfall req attr to the correct one based on niblet table
   BIGS_FIRMWARE_NEED_SPECIAL_CMD_IN_F3                           =   0    # Issue T>Wfefe in F3 mode in CRT2 for BIGS feature
   SERIAL_FORMAT_IN_CRT2_FOR_IOLESS_OPERATION                     =   0    # Move serial format from FNC2 to CRT2 when running IO-less mode
   CHECK_AND_WAIT_HDA_TEMP_IN_AFH                                 =   0    # Check and wait for hda temp to reach needed range
   DEPOP_TESTING                                                  =   0    # Enable depop testing (force depop at selected parts of process)
   RUN_T195_IN_CAL2                                               =   0    # Add T195 in CAL2 after Vbar for data collection
   ENABLE_THERMAL_SHOCK_RECOVERY_V2                               =   0    # Do not fail TSR in PRE2, combo spec with T250 in FNC2
   UPDATE_SYMBOL_ENTRY_239_BIT14_IN_ZAP                           =   0    # Enable setting of u16_Flags (symbol entry 239) bit 14 to disable PES notch filter during zap
   WA_0241988_305538_DNLD_F3_2X_WORKAROUND                        =   0    # Enable duplicate download of F3 firmware in CRT2 as workaround for TTR issue in Angsana2D
   FE_0262764_514721_RUN_PRECODER_IN_CAL2                         =   0    # Enable Precoder in M10P
   FE_0262766_480561_RUN_MRBIAS_OPTI_T251                         =   0    # MR BIAS Opti(test251 feature)
   FE_0264856_480505_USE_OL_GAIN_INSTEAD_OF_S_GAIN_IN_282         =   0    # Open Loop gain instead of Sensitivity gain in doBodePrm_282
   FE_0266393_305538_AEGIS_SCREEN                                 =   0    # Aegis Screen
   FE_OAR_ELT                                                     =   0    # OAR ELT
   FE_0267507_454766_WRITE_ZOUT_OPTI                              =   0    # Opti write zout
   FE_0267637_454766_PREAMP_TEMPTRM_TUNE                          =   0    # Over temp fault trim tune for TI7550
   FE_SGP_402984_POWER_CYCLE_ON_UNSUCCESSFUL_CHANGE_BAUD          =   0    # Do not exhaust unsuccessful change baud functions to save test time
   FE_0277874_504159_P_UPDATE_SNO_PHASE_DATA                      =   0    # Update SNO data to SAP
   FE_0271705_509053_NO_WAIT_FOR_SATAPHY_READY_UNDER_LOOPBACK     =   0    # Feature on/off for F3 ready fail under SATA Loopback (PSTR)
   FE_0280534_480505_DETCR_ON_OFF_BECAUSE_SERVO_DISABLE_DETCR_BY_DEFAULT = 0 # needed due to M10P servo code, servo code disables DETCR by default so DETCR on/off commands need to be called before and after using DETCR
   FE_0283639_402984_TURN_OFF_THRUPUT_RAW_AND_LARGE_SHOCK_DETECT  =   0    # Turn off RAW and large shock detection during FIN2 throughput
   FE_0000000_305538_HYBRID_DRIVE                                 =   0    # Used by TP for hybrid p/n detection
   FE_0298339_305538_T177_RETRY_CHANGE_TEST_CYL                   =   0    # Retry at test cyl (+5k) if fail T177
   FE_0302539_348429_P_ENABLE_VBAR_OC2                            =   0    # Enable VBAR OC2 state to change BPIC, TPIC or both
   FE_0307316_356688_P_ADC_SUMMARY_OC2                            =   0    # to display OC2 P_VBAR_ADC_SUMMARY
   FE_0370517_348429_ADDITIONAL_OC2_BPI_PUSH                      =   0    # AMADC Enable additional BPI Margin Push, i.e. in retail
   FE_0303511_305538_P_ENABLE_UNLOAD_CURR_OVER_TIME_SCREEN        =   0    # Enable unload current screening based on stdev and max values
   FE_0303725_348429_P_VBAR_MARGIN_RELOAD                         =   0    # Switch to turn on VBAR margin reload prior to OTC Margin Tuning
   ENABLE_PREAMP_DIE_TEMPERATURE_RECENTER                         =   0    # preamp TI temperature compensation 
   FE_0308035_403980_P_MULTIMATRIX_TRIPLET                        =   0    # New triplet opti
   FE_0308170_403980_P_SHORTEN_MMT_LOGS                           =   0    # Suppress log for new triplet opti
   FE_0315271_348085_P_OPTIMIZING_TCC_BY_BER_FOR_CM_OVERLOADING   =   0    # Optimize the TCC BY BER for CM Overloading improvement.
   FE_0320895_502689_P_RUN_SPIO_LOW_BAUD                          =   0    # In SPFIN2, use lower 38K baud rate
   ENABLE_SBS_DWNGRADE_BASED_ON_SOC_BIT                           =   0    # Based on SOC bit, downgrade fast drives to SBS tab
   FE_0332676_348085_P_SUPPORT_REVBAR_AT_CAL2_FOR_DEPOP           =   0    # Support reVbar at CAL2 for Dynamic Depop

   FE_0358600_322482_P_ESNR_CBD                                   =   0    # T488 to measure eSNR and CBD
   ######################################################################
   ############## SMR related switches only : Start #####################
   ######################################################################
   SMR = 0
   DESPERADO = 0
   Media_Cache = 0
   SMRPRODUCT = 0
   FE_0191830_320363_P_DISABLE_T50_51_IN_WRITE_SCREEN             =   0   # Disable T50/51 in Write Screen for SMR
   LCO_VBAR_PROCESS                                               =   0   #LCO cert process bring up
   ENABLE_ZEST_BIT_IN_SAP                                         =   0
   VBAR_HMS_MEAS_ONLY                                             =   0
   CONDITIONAL_RUN_HMS                                            =   0
   SCP_HMS                                                        =   0
   FE_0325284_348429_P_VBAR_SMR_HMS                               =   0 & SCP_HMS# use new method to cater for SMR Zone Alignment
   FE_SEGMENTED_BPIC                                              =   0   # Turn On to run New Segmented BPIC Tuning
   FE_0321700_348429_P_SEGMENTED_BPIC_SQZ                         =   0   # Turn On to run New Segmented BPIC Tuning Squeeze
   FE_CONSOLIDATED_BPI_MARGIN                                     =   0   # Turn On to run Consolidated Margin when running SCP_HMS and New Segmented BPIC Tuning
   FAST_SCP_HMS                                                   =   0   # SCP_HMS implementation without changing format, fast version
   FAST_SCP_HMS_VERIFY                                            =   0 and FAST_SCP_HMS  # invoke setting the BPIC - HMS Margin and measure the HMSC for verification purpose
   FE_0338929_348429_P_ENABLE_SQZ_HMS                             =   0   # Enable Squeeze Writes in HMS
   SMR_NEW_GUARD_TRK_PITCH_ALG                                    =   0
   SMR_TRIPLET_OPTI_WITH_EFFECTIVE_TPIC                           =   0
   SMR_TRIPLET_OPTI_SET_BPI_TPI                                   =   0
   WORKAROUND_TARGET_SIM_FILE_THRESHED                            =   0
   ENABLE_MEDIA_CACHE                                             =   0
   ADV_DEFECT_BAND_INSIDE_WRITE_SCRN                              =   0   # Enable advanced defect free band scheme in write_scrn
   FE_0215591_007867_COMPUTE_TPIC_AS_RATIO_MERGE_CL537310         =   0   # new definition of the TPIC
   FE_0252331_504159_SHINGLE_WRITE                                =   0   # Run Shingle write
   RD_SCRN2_FAIL_RERUN_ZAP                                        =   0   # Rerun ZAP when RD_SCRN2 fail
   FE_0194980_357260_P_LIMIT_SMR_TRACK_CLEANUP_TO_VALID_BANDS     =   0
   FE_0187241_357260_P_USE_BAND_WRITES_FOR_CLEANUP                =   0
   FE_0258639_305538_CONSOLIDATE_BANDS_BEFORE_CLEANUP             =   0   # Consolidate all overlapped and contiguous bands before performing band writes in track cleanup
   UMP_SHL_FLAWSCAN                                               =   0   # Interlace scan for UMP zones, seq scan for SHL zones.
   FE_0245944_504159_USE_DFT_VAL_RADIUS_GAP_FRE_FRM_RAP_SAP       =   0   # Use default values for Frequency, Gap & Raduis frm RAP&SAP
   FE_0246017_081592_ENABLE_RV_SENSOR_IN_CERT_PROCESS             =   0   # Switch to enable RV sensor from PRE2 operation onwards
   FE_0247885_081592_BODE_PLOT_AT_7200RPM                         =   0   # Switch to enable 7200RPM bode plot (test 282) at the beginning of PRE2
   FE_0250198_348085_AUTO_DETECT_TEST_TRACK_WEAK_WR_DELTABER      =   0   # auto detect the test track at od of Media cache zone
   FE_0250539_348085_MEDIA_CACHE_WITH_CAPACITY_ALIGNED            =   0
   FE_0251080_081592_ENABLE_SDD_SED_FOR_LINGGI_BASE_PRODUCT       =   0   # Flag to enable code download flow (5-1) for SDD & SED config for product using Linggi branch
   ENABLE_T396_DATACOLLECTION                                     =   0   # use to control T396 data collection
   FE_0253166_504159_MERGE_FAT_SLIM                               =   0   # Merging WRITE_FAT, WRITE_SLIM into WRITE_MERGE_SMR_SCRN
   FE_0254388_504159_SQZ_BPIC                                     =   0   #SQUEEZE BPIC Measurement
   FE_0254064_081592_CLEANUP_WKWRT_DELTABER_TRKS_USING_MC_INIT    =   0   # Switch to replace +/- 1 track cleanup in WkWrt_DeltaBER state with MC Init that will wrt pass all MC zone
   FE_348429_0255607_ENABLE_BAND_WRITE_T251                       =   0   # Enable Band Write when tuning Channel in SMR format
   FE_0261598_504159_SCREEN_OTF                                   =   0   # Enable OTF Screening
   DC_0205578_348432_T118_PADDING_BY_VBAR                         =   0   # Data collection (DC) for T118 Padding by vbar
   FE_0245014_470992_ZONE_MASK_BANK_SUPPORT                       =   0   # Add Zone Mask Bank Parameter to support 64+ zones (Up to 250 zones)
   FE_402984_271733_FAIL_DRIVE_WITH_MC_RESIDUE                    =   0   # Option to fail drive if media cache is not cleared
   INVALID_SUPER_PARITY_FULL_PACK_WRITE                           =   0   # replace G>Q,,22 super parity cleanup (not SMR friendly) with full pack write, temporarily
   GET_MANIFEST_FILE_BASED_ON_CODETYPE_ONLY                       =   0
   FE_0313724_517205_DISPLAY_SOC_INFO                             =   0   # Display SOC info in T 166
   FE_0316568_305538_P_ENABLE_TORN_WRITE_PROTECTION               =   0   # Enable Torn Write Protection bit in SAP in CRT2
   FE_0317559_305538_P_USE_MEDIA_PART_NUM                         =   0   # Use media part num to determine media type
   FE_0328298_305538_P_ENABLE_ADAPTIVE_AFH_DETCR_BIAS             =   0   # Enable adaptive DETCR CD bias by zone group (need SF3 support)
   FE_0334752_305538_P_USE_HSA_PART_NUM                           =   0   # Use HSA_PART_NUM to determine IBE3 process for HWY rd tgt clr
   FE_0335463_305538_P_USE_MEDIA_PART_NUM_FOR_AFH                 =   0   # Use MEDIA_PART_NUM to determine UV process for rd tgt clr
   FE_0336349_305538_P_RUN_SQZWRITE2_IN_CRT2                      =   0   # Run another SqzWrite test in CRT2
   ENABLE_SONY_FT2                                                =   0   # Enable SONY FT2 screening algo
   FE_0385813_385431_Enable_MSFT_CactusScreen                     =   0   #Enable Miscrosoft Cactus test
   ######################################################################
   ############## SMR related switches only : End #######################
   ######################################################################

   WA_KARNAK_DECREASED_1H_CAPACITY                                =   0
   MR_RESISTANCE_MONITOR                                          =   0
   WA_SAVE_SAP_BY_PCFILE                                          =   0
   SMR_2D_VBAR_OTC_BASED                                          =   0
   RUN_EAW_IN_WRITESCREEN                                         =   1   # default is to run
   WA_DETCRTA_NOT_CONNECT_SOC                                     =   0
   SKIP_MR_RESISTANCE_CHECK                                       =   0
   RSS_TARGETLIST_GEN                                             =   0
   RW_4K_SYSTEM_DISC_SECTOR                                       =   0   #4K system zone
   ASD_DEFECT_LIST_INITIATION                                     =   0
   DNLD_F3_5IN1_SED                                               =   0
   ENABLE_NAND_SCREEN                                             =   0 #Screen NAND Flash life cycle and bad clumps for AngH
   LAUNCHPAD_RELEASE                                              =   0
   FE_0243269_348085_FIX_BPI_TPI_WATERFALL                        =   0
   FE_0243459_348085_DUAL_OCLIM_CUSTOMER_CERT                     =   0
   WA_0247335_348085_WATERFALL_WITH_10_DIGITS_PARTNUMBER          =   0
   CLEAR_NAND_FLASH_ON_RECYCLE_PCBA                               =   0

   VBAR_2D                                                        =   0   # Main flag to toggle 2D_VBAR
   VBAR_ADP_EQUAL_ADC                                             =   0 and VBAR_2D  # Set BPIP/TPIP = BPIC/TPIC, only when running data collection
   OTC_BASED_QTPI                                                 =   0 and VBAR_2D  # Use OTC based Measurement in QTPI
   VBAR_SKIP_MIN_CAPABILITY_CHECK                                 =   0 and VBAR_2D  # Skip checking of BPI/TPI below minimum configs
   FAST_2D_VBAR                                                   =   0 and VBAR_2D  # Use T211 to generate BER vs BPIC Slope
   FAST_2D_VBAR_INTERLACE                                         =   0 and VBAR_2D and FAST_2D_VBAR # Interlace Measurement in Fast VBAR
   WP_FAIL_SAFE_SATURATION                                        =   0 and VBAR_2D  # Fail safe No saturation EC13409 during WP
   FAST_2D_VBAR_XFER_PER_HD                                       =   0 and VBAR_2D  # Transfer Function Per Head
   FAST_2D_VBAR_XFER_PER_HD_FILTER                                =   0 and VBAR_2D  # Enable Filtering of BPIC and TPIC_S when picking the best Target SFR
   FAST_2D_VBAR_XFER_PER_HD_DELTA_BPI                             =   0 and VBAR_2D  # Enable BPI Delta when calculation for BPIC
   FAST_2D_VBAR_2DIR_SWEEP                                        =   0 and VBAR_2D  # Enable 2x T211 Call to trigger BPI Sweep data using higher and lower target SFRs
   FAST_2D_VBAR_TPI_FF                                            =   0 and VBAR_2D  # TPI Feed Forward during Fast 2D Measurement
   FAST_2D_VBAR_UNVISITED_ZONE                                    =   0 and FAST_2D_VBAR_XFER_PER_HD   # Use PolyFit when predicting parameters for VBAR Unvisted Zone
   FAST_2D_VBAR_UMP_FIX_BEST_TARGET_SOVA_BER                      =   0 and FAST_2D_VBAR_UNVISITED_ZONE
   FAST_2D_VBAR_TESTTRACK_CONTROL                                 =   0 and FAST_2D_VBAR_UNVISITED_ZONE
   FAST_2D_MEASURE_SQZ_BER                                        =   0 and FAST_2D_VBAR_UNVISITED_ZONE
   FE_0320673_356688_P_BEST_TARGET_SOVA_BER_FAVOUR                =   0 # best target sova selection biase to DefaultTargetSFRIndex   
   FE_0253509_348429_UVZ_IMPROVE_FILTERING1                       =   0  # Add 2nd and 2nd zone to the last in disabled 5pt median filter, also use mean in lumping algo
   FE_0289797_348429_ZONE_ALIGN_IMPROVE_FILTERING                 =   0 # Filtering method for use in Zone Alignement
   EFFECTIVE_TPIC_EQUAL_TPIS                                      =   0   # When saving format, save Track Pitch as TPIS instead of EFfective TPI
   skipVBARDictionaryCheck                                        =   0 and VBAR_2D  # Skip VBAR Dictionary Check specially when adding new keys but skipping the entire PRE2 process.
   FE_0273368_348429_ENABLE_TPINOMINAL                            =   0 # Switch to Enable TPINOMINAL before TRIPLET_OPTI and VBAR TUNING
   FE_0273368_348429_TEMP_ENABLE_TPINOMINAL_FOR_ATI_STE           =   0 # temporary switch to enable TPINOMINAL before TRIPLET_OPTI when ATI STE Feature Turned On
   FE_0279318_348429_SPLIT_2DVBAR_MODULES                         =   0 # Switch to split VBAR_ZN into 2D VBAR Modules.
   FE_0281130_348429_ENABLE_SINGULAR_SMR_DIR_SHIFT                =   0 # Switch to enable single interzone SMR Direction Shift by head
   WA_0308810_504266_RDS_ED_MICROJOG                              =   0 # Download SF3 with RDS Encoding/Decoding(ED) before MicroJog is run when Markov ED is default SF3
   WA_0309963_504266_504_LDPC_PARAM                               =   1 # Update Param when SEL_ZONE is enabled in SF3 with 504 parity across all regions
   FE_0315237_504266_T240_DISABLE_SKIP_TRACK                      =   0 # Disable mapping out the test track as long as truning ON and OFF of Degauss feature is disabled
   FE_0320340_348085_P_OAR_SCREENING_SPEC                         =   0 # Failing spec for the OAR test
   FE_0320939_305538_P_T287_ZEST_SCREEN_SPEC                      =   0 # Enable failing spec for Prism Zest test 287

   #**** VBAR MARGIN BY S2D SWITCHES ****#
   FAST_2D_S2D_TEST                                               =   0 and VBAR_2D

   #**** VBAR MARGIN BY OTC SWITCHES ****#
   VBAR_MARGIN_BY_OTC                                             =   0 and VBAR_2D and ( not FAST_2D_VBAR_UNVISITED_ZONE ) # Run T211 OTC Margin measurements in VBAR
   OTC_BASED_RD_OFFSET                                            =   0 and VBAR_2D  # set read ujog offset in RAP using VBAR OTC Bucket Rd Offset
   OTC_MEAS_ONLY_SHINGLE_DIR                                      =   0 and VBAR_2D  # Set to measure OTC Bucket only in selected shingle direction during VBAR_OTC
   OTC_RESET_RD_OFFSET_BEFORE_TUNE                                =   0 and VBAR_2D  # reset read offset before tuning.
   OTC_REV_CONTROL                                                =   0 and FAST_2D_VBAR_UNVISITED_ZONE # VBAR_OTC to measure at rev control to save test time
   VBAR_2D_DEBUG_MODE                                             =   0  # 2D VBAR FAST DEBUG MODE

   #**** TMR/Noise Inject SWITCHES ****#
   MEASURE_TMR                                                    =   0  #meausure TMR during VBAR OTC
   NOISE_INJECTION_ON_TMR_DURING_T211                             =   0  # Add Nooise Injection on T211 at VBAR_ZN
   NOISE_INJECTION_ON_TMR                                         =   0  # Add Nooise Injection on TMR State
   APPLY_FILTER_ON_SMR_TPI                                        =   0 and VBAR_2D  # Appply filter on both TPI IDSS and ODSS
   FE_0318595_348429_P_APPLY_FILTER_ON_UMP_TPI                    =   0 # Appply filter on UMP TPI DSS
   OTC_BUCKET_LINEAR_FIT                                          =   0 and VBAR_MARGIN_BY_OTC # use linear fit to finally compute the TPI OTC
   OTC_SKIP_ZONE_MAXIMIZATION                                     =   0 and VBAR_MARGIN_BY_OTC # Skip relaxing track pitch during Calculate track pitch, do not turn On in Mass PRO
   OTC_BUCKET_ZONE_POLYFITTED                                     =   0 and VBAR_MARGIN_BY_OTC # Zone Fitting in TPI OTC
   OTC_NOT_STOP_ON_TARGET                                         =   0 and VBAR_MARGIN_BY_OTC # T211 OTC Measurement stop only when TPI adjust exceed +/-7%, this is to have enough data for linear regression
   FE_0288274_348429_OTC_MARGIN_MULTIZONE                         =   0  # Consolidate multiple test zones into ST single call
   FE_0247538_402984_MASK_CUDACOM_ARGS_16BIT                      =   0  # Mask cucdom *args to 16 bits. Converts signed to unsigned integers passed to CM fn function

   #**** VBAR MARGIN BY OTC TRACK PITCH SWITCHES ****#
   FE_0293889_348429_VBAR_MARGIN_BY_OTCTP                         =   0 # Switch to enable OTC margin version 2 that reduce test time
   FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_INTERBAND_MARGIN        =   0 # switch to enable interband Margin for SMR zones
   FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_RD_OFFSET_CALC          =   0 # switch to enable read offset calculate by OTC measurements
   FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_OVERRIDE_TP_TG          =   0 # switch to override the desperadoplus picker TP and TG maximization
   FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_USE_MULTI_WRITES        =   0 # switch to use multi writes OTC instead of single write
   FE_0293889_348429_VBAR_MARGIN_BY_OTCTP_INTERBAND_MEAS          =   0 # switch to measure interband OTC

   ENABLE_CERT_SUMMARY_DATA                                       =   0
   ENABLE_NEW_CERT_DONE_BIT12                                     =   0
   FE_0247196_334287_FIXED_WP_FQ_ET                               =   0

   #**** Logging Tuning SWITCHES ****#
   T251_TURNOFF_REPORT_OPTIONS_DURING_VBAR_ZN                     =   0
   T211_TURNOFF_REPORT_OPTIONS_DURING_2DVBAR_TPIC_MEAS            =   0
   T211_MERGE_READ_OFFSET_TBL_INTO_TPI_MEAS_TBL                   =   0

   FE_0254909_348085_VBAR_REDUCDED_TG                             =   0 # new track guard calculation
   SMR_SGL_SHINGLE_DIRECTION_SWITCH                               =   0
   FE_0228288_336764_P_PAUSE_CRITICAL_LOCATION_AT_VBAR_FOR_LA_CM_REDUCTION   =  0
   FE_0232067_211428_VBAR_USE_DESPERADO_PLUS_FORMAT_PICKER        =   0
   FE_0257373_348085_ZONED_SERVO_CAPACITY_CALCULATION             =   0
   FE_0256852_480505_DISPLAY_VBAR_MAX_CAPACITY_PER_HEAD           =   0 # Add Display max capacity per head to function getDriveCapacity
   FE_0257372_504159_TPI_DSS_UMP_MEASURMENT                       =   0 # UMP TPI_DSS Special Measurement instead of linear fit
   FE_0257006_348085_EXCLUDE_UMP_FROM_TCC_BY_BER                  =   0
   FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND              =   0
   FE_0262424_504159_ST210_SETTING_FORMAT_IN_ZONE                 =   0  # Calling t210 setting format by passing param in term of zone
   FE_0221722_379676_BYPASS_TPM_DOWNLOAD                          =   0  # There's no need to do this anymore.  Process breaks without this after F3Trunk CL 567957
   FE_0184102_326816_ZONED_SERVO_SUPPORT                          =   0  # Flag to enable & disable zoned servo
   DiagOverlayWipeOnly                                            =   0  # to wipe the Diag Overlay
   CPC_ICMD_TO_TEST_NUMBER_MIGRATION                              =   0  # This switch is to be enabled for CPC non-intrinsic function testing
   TRUNK_BRINGUP                                                  =   0  # This switch is to be enabled for CPC non-intrinsic function testing
   MARVELL_SRC                                                    =   0  # This switch will be enabled for Strike eagle and cheopsM
   WA_0276349_228371_CHEOPSAM_SRC_BRING_UP                        =   0  # This switch will be enabled for cheopsam as workaround, will revisit whehter can be removed when program mature
   FE_0276349_228371_CHEOPSAM_SRC                                 =   0  # This switch will be enabled for cheopsam as feature
   RECONFIG_CHECK_BASED_ON_BSNS_SEGMENT                           =   0  # Reconfig based on drive FIS attributes BSNS_SEGMENTx rather than PIF ReConfigTable
   ENABLE_FAFH_FIN2                                               =   0
   SINGLEPASSFLAWSCAN                                             =   0
   SINGLEPASSFLAWSCAN_AUDIT                                       =   0
   SINGLEPASSFLAWSCAN_WRITE_FMT                                   =   0
   FE_0272568_358501_P_ADAPTIVE_BIE_IN_SPF                        =   0
   FE_0272573_358501_P_SKIP_WRITE_IN_SPF                          =   0
   FE_0267792_504159_USE_LOWER_KTPI_START_POINT_MEASUREMENT       =   0 # Use lower ktpi to tpi_dsss measurement
   FE_0267804_504159_P_VBAR_ATI_FOR_DATA_COLLECTION               =   0 # Collect ATIC for UMP zones for data collection purpose only
   WRITE_HDA_TEMPERATURE_TO_SAP                                   =   0 # ported from SNO A2D feature.
   FE_0246199_504159_INJECT_VCM_NOISE                             =   0 # Inject VCM noise to simulate WTF backoff
   FE_0268922_504159_VBAR_ATI_ONLY_RELAX_DIR                      =   0 # Only allowed to relax tpi direction inside vbar_ati
   FE_0242596_356922_CLEAR_SEACORDER                              =   0
   FE_0269922_348085_P_SIGMUND_IN_FACTORY                         =   1 # Sigmund In Factory
   FE_0273221_348085_P_SUPPORT_MULTIPLE_SF3_OVL_DOWNLOAD          =   0
   FE_0272909_480561_BER_MEASUREMENT_FOR_MONITORING               =   0 # Add BER test in CAL2/FNC2 to check head deg and monitor BER
   FE_228371_ZAP_SPECIFIC_ZONE_BF_READ_OPTI                       =   0 # turn off if vbar_otc/squeeze offset test time reduction not decided
   FE_228371_DETCR_TA_SERVO_CODE_SUPPORTED                        =   1 # servo code not support detcr programming
   FE_0274346_356688_ZONE_ALIGNMENT                               =   0 # zone alignment for test zone optimization
   FE_0367608_348429_ZONE_ALIGNMENT_TTR                           =   0 # enable zone alignment for 150zone test time reduction
   FE_0293167_356688_VBAR_MARGIN_ZONE_ALIGNMENT                   =   0 # zone alignment for test zone optimization in VBAR_MARGIN
   FE_0367608_348429_VBAR_MARGIN_ZONE_ALIGNMENT_OTC_TTR           =   0 # TTR zone alignment for test zone optimization in VBAR OTC MARGIN
   FE_0376137_348429_VBAR_MARGIN_ZONE_ALIGNMENT_SEG_TTR           =   0 # TTR zone alignment for test zone optimization in VBAR SEG/OAR MARGIN
   FE_0376137_348429_VBAR_MARGIN_ZONE_ALIGNMENT_SHMS_TTR          =   0 # TTR zone alignment for test zone optimization in VBAR SHMS MARGIN
   FE_0384272_348429_VBAR_MARGIN_ZONE_ALIGNMENT_SEG_TTR2          =   0 # Further TTR in VBAR SEG/OAR MARGIN
   FE_0384272_348429_VBAR_MARGIN_ZONE_ALIGNMENT_SHMS_TTR2         =   0 # Further TTR in VBAR SHMS MARGIN
   FE_0293167_356688_VBAR_MARGIN_ZONE_COPY                        =   0 # zone copy for test zone optimization in VBAR_MARGIN
   FE_0376137_356688_VBAR_MARGIN_ZONE_COPY_TTR                    =   0 # Implement Zone Copy in VBAR Margin Opti with TTR
   FE_0364447_356688_P_VBAR_OTC_ZONE_ALIGNMENT_TTR                =   0 # TTR zone alignment for test zone optimization in VBAR_OTC RD OFFSET Tuning
   FE_0302686_356688_P_VBAR_OTC_ZONE_ALIGNMENT                    =   0 # zone alignment for test zone optimization in VBAR_OTC, VBAR_OTC2   
   FE_0279297_348085_PROG_MC_UMP_IN_RAP                           =   0 # program the mc size and ump size at RAP
   RUN_PREVBAR_ZAP                                                =   0 # common test switch to run PRE VBAR ZAP
   RUN_TPINOMINAL1                                                =   0 # run pre TPINOMINAL prior to Triplet Opti
   FE_0281621_305538_SET_SERVO_TRK_0_VALUE                        =   0 # Update servo trk 0 (from RAP if available)
   FE_0276246_231166_P_ENABLE_SET_OVS_RISE_TIME                   =   0   # Set the overshoot rise time in the rap- Compatible with Rap27v7
   FE_0283799_454766_P_DTH_ADJ_ON_THE_FLY                         =   0 # dTh adjustment on the fly base on CRT2 BER
   FE_0284435_504159_P_VAR_MC_UMP_ZONES                           =   0 # Read number/start of MC and UMP zones
   FE_0284077_007867_SGL_CALL_250_ZN_VBAR_SUPPORT                 =   0 # Single st( ) call using ZONE_MASK_BLOCK input parameter
   USE_TEST231_RETRIVE_BPI_PROFILE_FILE                           =   0
   FE_0296361_402984_DEFECT_LIST_TRACKING_FROM_CRT2               =   0 # Trace defect lists at the start of FIN2 to verify CRT2 not causing defect lists
   FE_0297446_348429_P_PRECISE_PARITY_ALLOCATION                  =   0 # Calculate overhead for super parity sector on the fly during format picker routine
   FE_0297449_348429_P_RUN_ATI_TEST_POST_VBAR                     =   0 # Run ATI test (CAL2/PRE2) after VBAR prior to Full ZAP
   FE_0299263_348429_P_USE_FULL_AGB_CAPACITY_BY_DEFAULT           =   0 # Use full AGB by default during the VBAR Picker whether have excess capacity or not
   FE_0321677_356688_P_USE_FULL_AGB_CAPACITY_FOR_NATIVE_ONLY      =   0 # Use full AGB for native only during the VBAR Picker
   FE_0298709_348085_P_PRECISE_MEDIA_CACHE_SIZE_ALLOCATION        =   0 # Calculate the media cache size precisely according to the firmware calclulation.
   FE_0309959_348085_P_DEFAULT_580KTPI_FOR_DATA_TRACK_SUPPORT     =   0 # Default RAP data track is 580ktpi, the script will bring down by 15% ( 0.85 )
   FE_0309814_348429_SPLIT_VBAR_MARGIN_MODULES                    =   0 # Switch to split VBAR_MARGIN into Sub Modules.
   FE_xxxxxxx_348429_P_SET_ADC_FMT                                =   0 # consolidate under one switch
   FE_0309812_348429_P_LOAD_BY_ACTIVE_HEAD_ZONES                  =   0 # Switch to load the BPI Config data by active heads/zones
   FE_0309818_348429_P_MOVE_POST_VBAR_STATES_TO_FNC2              =   0 # Switch to end CAL2 operation after VBAR FMT PICKER
   FE_0310548_348429_P_CM_REDUCTION_REDUCE_VBAR_DATA              =   0 # Switch to suppress Critical VBAR Tables in log
   FE_0311724_348429_P_LOAD_COMMON_TRACK_PER_ZONE                 =   0 # Load one copy of tracks per zone in bpi config
   FE_0312337_348429_P_GET_MARGIN_MATRIX_ON_THE_FLY               =   0 # skip building dictionary for Margin Matrix and get it on the fly
   FE_0312338_348429_P_GET_CLOSEST_BPI_BY_HD_ZN                   =   0 # Get closest BPI file by given head and zone only 
   FE_0314630_402984_FIX_SERIAL_ZONE_AVG_CAL                      =   0 # New method to fix serial thruput average calculation
   FE_ENABLE_HEAD_PIN_REVERSAL_SCREEN                             =   0 # Head Pin Reversal Screening Test
   FE_0315250_322482_P_AFH_CM_OVERLOADING                         =   0 # AFH reduce printing to save CM memory / CPU
   FE_0328119_322482_P_SAVE_AFH_CERT_TEMP_TO_FIS                  =   0 # save AFH cert temperature in attribute then retrive in CRT2 to save test time
   FE_0318342_402984_CHECK_HDA_FW                                 =   0 # Check HDA, firmware, servo and IV code integrity in CRT2
   FE_0321705_348429_P_ADD_SHIFTZONE_IN_MARGIN                    =   0 # include SMR shift zone boundary in margin measurements
   FE_0376137_348429_P_ADD_SHIFTZONE_IN_MARGIN_BY_HD              =   0 # include SMR shift zone boundary in margin measurements by head
   FE_0325893_348429_P_OD_ID_RESONANCE_MARGIN                     =   0 # Enable more backoff on BPI/TPI margin at OD/ID zones for resonance.
   FE_0325513_348429_P_RUN_PRE_VBAR_PES                           =   0 # Run pre VBAR PES on test zones 
   FE_0331809_433430_P_STOP_TEST_IF_INIT_FAILED                   =   0 # Stop test if failed at INIT during PWL recovery
   FE_0338482_348429_P_DESPERADOPLUS_EFFECTIVE_TPI_CALC           =   0 # Calculate using desperado plus effective tpi
   FE_0345101_348429_P_AVM_RD_OFFSET_AND_CHANNEL_TUNE             =   0 # Enable Read Offset Tuning before AVM and Channel Tuning before Margin OTC
   FE_0345891_348429_TPIM_SOVA_USING_FIX_TRANSFER                 =   0 # Enable AVM Estimator TPIM SOVA using fixed transfer between TPIM and SQZ SOVA BER

   #################################################################################
   ###################       special for Common 2 Temp CERT         ################
   #################################################################################
   FE_0258915_348429_COMMON_TWO_TEMP_CERT                                        = 0 # Turn On Common 2Temp CERT, ambient PRE2/CAL2/FNC2 and hot CRT2
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00001                            = 0  # Turn on Burnish Spec for Common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00002                            = 0  # Turn on ID Burnish Spec for Common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00003                            = 0  # Turn On Mean HMSC and min HMSC screen for common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00004                            = 0  # Turn On ID Region Verified and Unverified Flaw Screen for common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00005                            = 0  # Turn On High Severity TA in AFH Test Zones screen for common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00006                            = 0  # Turn On LUL Time Screen for common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00007                            = 0  # Turn On T250 and TSR Screen for common 2Temp CERT
   FE_0258915_348429_COMMON_TWO_TEMP_CERT_SCRN_A00008                            = 0  # Turn On TCC and HMSC Screen
   FE_348429_COMMON_TEST_POSITION                                                = 0  # Test Zone Position to point to common reference
   FE_348429_DYNAMIC_CERT_RECOVERY                                               = 0  # Enable Dynamic CERT Recovery, initial implementation to tweak zone position
   FE_OPEN_UP_DTH_VALUE                                                          = 0  # Open up dTH temp trigger to avoid trigger during CERT
   FE_0308779_356996_SNO_BODE_DATA_VERIFY                                        = 0  # Verify BODE DATA after SNO. Retest if data is bogus
   FE_0322256_356996_T282_SENSITIVITY_LIMIT_CHECK                                = 0  # Run T282 for Sensitivity Limit Check
   #################################
   #################################################################################
   ###################                      PBIC                    ################
   #################################################################################
   PBIC_SUPPORT                                                   = 0    #To support Performance based Intelligent Cert
   PBIC_DATA_COLLECTION_MODE                                      = 1  & PBIC_SUPPORT
   #################################################################################

   FE_PREAMP_DUAL_POLARITY_SUPPORT_DETCR_TA                                      = 0  # to turn on dual polarity in flaw scan
   FE_0284269_228371_SUPPORT_CL794987_NEW_PREAMP_WR_CMD                          = 0  # turn on when CL794987 is taken
   FE_0294085_357595_P_CM_LOADING_REDUCTION                                      = 0

   #################################################################################
   ###################                      SPFS                    ################
   #################################################################################
   SPFS_DISABLE_FSB = 0
   SPFS_DISABLE_EVM = 0

   #################################################################################
   ###################                      CM LOAD REDUCTION                    ################
   #################################################################################
   FE_0227626_336764_P_REMOVE_SUMMARY_DISP_FRAME_CAL_FOR_LA_CM_REDUCTION  = 0 # Remove summaryDisplayFrames calculation for reduce CM load average.
   FE_0227617_336764_P_OPTIMIZE_WRITE_READ_AFH_FRAME_FOR_LA_CM_REDUCTION  = 0 # Optimize write read frame algorithm for reduce CM load average.
   FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION     = 0 # Change the method to access frame data
   FE_0239301_336764_P_CLEAR_DPES_FRAME                                   = 0 # Clear DPES frame for memory reduction
   FE_0299849_356688_P_CM_REDUCTION_REDUCE_PRINT                          = 0 # Reduce debug msg and table printing
   CM_REDUCTION_REDUCE_PRINTMSG                                           = 0
   CM_REDUCTION_REDUCE_PRINTDBLOGBIN                                      = 0
   FE_0314243_356688_P_CM_REDUCTION_REDUCE_VBAR_MSG                       = 0 # Reduce VBAR printing   
   FE_0314243_356688_P_CM_REDUCTION_REDUCE_CHANNEL_MSG                    = 0 # Reduce Channel printing
   FE_0314243_356688_P_CM_REDUCTION_REDUCE_ATI_MSG                        = 0 # Reduce ATI printing
   FE_0314243_356688_P_CM_REDUCTION_REDUCE_TRIPLET_MSG                    = 0 # Reduce Triplet printing
   FE_0314243_356688_P_CM_REDUCTION_REDUCE_FILE_MSG                       = 0 # Reduce file related printing
   FE_0314243_356688_P_CM_REDUCTION_REDUCE_PROCESS_MSG                    = 0 # Reduce process related printing
   
   FE_0297451_348429_P_USE_ACTUAL_DENSITY_IN_INITIAL_PICKER               = 0 # Use actual capacity based on ADC on initial picker and margin return calculation
   FE_0337427_348429_TRACKPITCH_BASED_MARGIN_RETURN                       = 0 # Use track pitch based margin return to improve the picker iteration
   FE_0337430_348429_ITERATIVE_MARGIN_RETURN                              = 0 # Use iterative Margin Return in case the initial pick > Target by > 1% Nominal
   ENABLE_TARGET_TUNING_T251                                              = 0 # enable target tuning  
   USE_NEW_PROGRAMMABLE_TARGET_LIST_0727_2015                             = 0 # enable new target list RSS provide July 27
   FE_0308542_348085_P_DESPERADO_3                                        = 0
   FE_0325260_348085_P_VARIABLE_GUARD_TRACKS_FOR_ISO_BAND_ISOLATION       = 0
   FE_348085_P_NEW_UMP_MC_ZONE_LAYOUT                                     = 0 # New layout UMP, MC, Main Store.
   SPLIT_BASE_SERIAL_TEST_FOR_CM_LA_REDUCTION                             = 0 # Split base_SerialTest.py
   SPLIT_VBAR_FOR_CM_LA_REDUCTION                                         = 0 # Split VBAR.py

   FE_0306627_403980_P_ZONEINSERTION_FOR_DIFF_WRITE_POWER                 = 0 # Zoneinsertion: insert test zone which has different write power setting.
   FE_0236367_357260_P_REMOVE_REDUNDANT_T135_PARAM_DISPLAY                = 0   # Remove extra display of T135 parameters.
  
   FE_0227602_336764_P_REDUCE_T11_TEST_LOOP_FOR_LA_CM_REDUCTION           = 0 # Reduce T11 test loop
   T134_TA_FAILURE_SPEC                                                   = 0 # fail TA spec
   FE_0320143_305538_P_T134_TA_SCREEN_SPEC                                = 0 # fail TA screening
   FE_0331797_228371_P_T134_TA_SCREEN_SPEC_TRK300                         = 0 # fail TA screening
   FE_0332210_305538_P_T337_OVERWRITE_SCREEN                              = 0 # fail overwrite screening
   FE_0332210_305538_P_T250_SQZ_WRITE_SCREEN                              = 0 # fail sqz write screening
   FE_0332210_305538_P_SERFMT_OTF_SCREEN                                  = 0 # fail serial format OTF screening
   FE_0338712_305538_P_AFH_CLR_SCREENING                                  = 0 # fail AFH clearance screening
   FE_0340631_305538_P_RDSCRN2H_COMBO_SCREEN                              = 0 # fail Read Scrn2H max/mean BER screening
   FE_305538_P_MT50_MT10_SCREEN                                           = 0 # fail MT50/MT10 screening
   FE_305538_P_T297_WPE_SCREEN                                            = 0 # fail WPE/T297 screening
   FE_305538_P_T250_COMBO_SCREEN                                          = 0 # fail delta and avg BER combo screening
   FE_0365907_305538_P_T185_UFCO_OFFSET_SCREEN                            = 0 # fail rampcyl and lul combo screening
   T215_DETCR_TA_PAD_BY_SEVERITY                                          = 0 # padding by severity

   FE_0237612_336764_P_ADD_RESULT_FILE_READ_BUFFER_FOR_LA_CM_REDUCTION    = 0 # Add result file read buffer 
   WA_0000000_348432_FLAWSCAN_AMPLITUDE_DROP                              = 0 # Workaround for T109 amplitude drop issue.
   FE_ENABLE_T117_SCREEN_NUM_SCRATCH_PHPZ                                 = 0 # RW1D TVM UDE failure CA.
   FE_0341719_228371_MORE_PAD_LOW_SEVERITY_TA                             = 0 # extra padding the same as high severity TA
   FE_0342075_228371_TA_PADDING_SBS_2D                                    = 0 # TA padding for retail 2D


   #HAMR
   HAMR                                                                   = 0 # HARM related
   UPS_PARAMETERS                                                         = 0 # for UPS input structure   
   CHEOPSAM_LITE_SOC                                                      = 0 # for cheopsam lite only

   #High RPM ZAP
   FE_0335299_454766_P_ENABLE_HIGH_RPM_ZAP                                = 0 # for high RPM ZAP   
   FE_0335299_454766_P_ENABLE_HIGH_RPM_ZAP_DEBUG                          = 0 # for high RPM ZAP DEBUG
   FE_0343664_403980_P_ENABLE_PRECAUTIONARY_OPTI                          = 0 # T256
   FE_0345154_403980_P_ZONE_COPY_OPTIONS_T256                             = 0 # T256 zone copy
   FE_0345901_403980_P_MMT_TO_LOOP_IW_IN_SF3                              = 0 # for MMT
   FE_0352662_403980_P_MMT_IW_SWEEP_LOW_TO_HIGH                           = 0 # (MMT) Iw sweep enhancement

   #################################################################################
   ###################                      SCOPY                   ################
   #################################################################################
   SCOPY_TARGET                                                           = 0 # Using for common SCOPY option
   WRITE_SERVO_PATTERN_USING_SCOPY                                        = 0 # Write servo pattern using servo copy

   #RFWD
   FE_0334158_379676_P_RFWD_FFV_1_POINT_5                                 = 0 # Download FFV code, invoke test 393 and compare signatures in CCV
   FE_305538_P_T33_REZAP_ON_MAXRRO_EXCEED_LIMIT                           = 0 # Trigger reZap when maxRRO (frm Test 33) exceeded limit

   POST_SERVO_FLAW_SCAN_IN_CRT2                                           = 0 # Issue T126 for full surface scan in CRT2

   FE_0360203_518226_2D_CTU_RDG_RDCLR_COMBO_SCREEN                        = 0   
   #AFH SCREEN
   FE_0359619_518226_REAFH2AFH3_BYHEAD_SCREEN                             = 0
   AGC_SCRN_DESTROKE_FOR_SBS                                              = 0
   FE_1111111_KillHead                                                    = 0