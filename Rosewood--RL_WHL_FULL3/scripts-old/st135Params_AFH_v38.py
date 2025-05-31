#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Test Parameters for Muskie
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/st135Params_AFH_v38.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/st135Params_AFH_v38.py#1 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#
#from Constants import *

########################################################################################################################################################################
#
#
#           Constants
#
#
########################################################################################################################################################################
UNINITIALIZED = -1
OFF = 0
ON = 1
DEBUG = 0
CWORD2_RUN_INITIAL_ZONES_BASED_ON_RAP_CLR = 0x0100
CWORD2_CONFIRM_INITIAL_ZONES              = 0x0010
CWORD2_EXTRME_OD_ID_RUN                   = 0x0020

def GetParameter( testDictionary, featureName, programName, optionalIndices = None ):
   if optionalIndices == None:
      optionalIndices = []
   # This function will index into testDictionary and return the parameter for the specified featureName
   # It will find the value regardless of whether the feature is split out by
   # for parameters that have non-standard indices (eg internalRetryRevs has 'HighSkew'), pass a list of those into the extraIndices

   testList = [programName] + optionalIndices
   ParamValue=testDictionary[featureName]


   if DEBUG: print( "Searching with options %s in \n%s" % (testList, ParamValue) )
   while len(testList) > 0:
      found = False
      for test in testList:
         if DEBUG: print " -  Finding %s" % test
         if DEBUG: print " -  ParamValue %s" % str(ParamValue)

         try:
            if test in ParamValue:
               found = True
               ParamValue=ParamValue[test]
               ii = testList.index(test)
               del testList[ii]
               break
            elif test == programName:
               for key in ParamValue:
                  if type(key) == type(()) and test in key:
                     ParamValue = ParamValue[key]
                     ii = testList.index(test)
                     del testList[ii]
                     found = True
                     break

            if not(found) and ('Default' not in testList):
               #At each index level, we allow a 'Default' set of parameters... so add it to the end of the list so its checked last
               testList += ['Default']

         except:
            # in comparison failed becuase we've already indexed down to the final parameter
            # indicies were supplied that do not exist for this parameter... we're done
            testList = []

         if found:
            break

      if not(found):
         break

   if DEBUG: print "Returning %s" % str(ParamValue)
   return ParamValue

########################################################################################################################################################################
#
#          Function:  getSelfTest135Dictionary
#
#   Original Author:  Michael T. Brady
#
#       Description:  Get the test 135 parameter dictionary
#
#           Purpose:  Provide a mechanism where test 135 dictionary can be set in 1 place with access
#                     to production process run-time attributes such as RPM and servoWedges without using
#                     Test Parameter Extractor.  This allows this same code to be run on the bench using WinFoF.
#
#             Input:  AFH_State,  1 for AFH1, 2 for AFH2 , etc.
#
#
#      Return Value:  baseIPD2Prm_135(dict)
#
########################################################################################################################################################################


def getSelfTest135Dictionary( AFH_State,     intHeadRetryCntr,   programName,
                              heaterElement, iHead,              SpokesPerRev,
                              RPM,           headType,           AABType,
                              numZones,      isDriveDualHeater,  virtualRun,
                              benchMode,     enableFAFH,         iConsistencyCheckRetry,
                              preampType     = None,
                              preamp_rev     = 0, wafer_code = None ):

#  AFH_State                  # AFH State number(integer).  =1 for AFH1, =2 for AFH2, etc.
#  intHeadRetryCntr           # Global head retry counter(integer).  = 0 for initial measurement, =1 for the 1st retry.
#  programName                # Program Name(string)  = "Trinidad", ="Grenada", etc.
#
#  heaterElement              # active heater element for contact detection(string) = "WRITER_HEATER" or "READER_HEATER"
#  iHead                      # logical head number being tested(integer).  For Bench testing, set this to 0.
#  SpokesPerRev               # number of servo wedges per track(integer)
#
#
#  RPM                        # RPM for the drive(integer)
#  headType                   # head vendor(string) = "RHO", "TDK", "HWY", etc.
#  AABType                    # Air bearing type(string)
#
#  numZones                   # number of logical zones(integer)
#  isDriveDualHeater          # enables dual heater contact detect(integer) = 0 for disable, =1 for enable
#  virtualRun                 # enable Process PF3 virtual exeution run.  = 0 for disable, = 1 for enable.  = 0 for real process and Bench level runs.




   ########################################################################################################################################################################
   #
   #
   #
   #
   #
   ########################################################################################################################################################################

   if benchMode == 1:
      pass
      # ABSOLUTELY no testSwitch references in AFH v21 and forward.  It is NOT allowed.
      ##     class CSwitches:
      ##        pass
      ##
      ##     testSwitch = CSwitches()

   else:
      from Test_Switches import testSwitch
      import types
      # this is here for robustness
      programNameList = programName.split(".")
      if len(programNameList) >= 1:
         programName = programNameList[0]

      if programName in ['MakaraSAS']:
         programName = 'Makara'

   if virtualRun:
      SpokesPerRev = 272
      RPM = 7200  # you should strongly consider adding this so that the calculation is correct in VE mode
      numZones = 60

   if AFH_State == 5:
      AFH_State = 2

   zones = (str(numZones)+'Zone')

   ####################################################################################################################################################
   #
   #
   #                                         Test Limit Input Dictionaries by Program and Head Type
   #
   #        NOTICE: The new GetParmeter functionality added to this file makes it far more flexible.  If a parameter is not broken out by headType or
   #        heaterElement, those indices can simply be added without any other code changes and everything will still work.  If other special indices
   #        added (ie, other than headType or heaterElement), then minor code changes will be needed to add the new index to the optionalIndices list
   #        that is passed to the GetParameter function.
   #        The Default program functionality can be used to simplify dictionaries that contain duplicate entries across several programs.  If the programName
   #        is removed from a given feature, the code will select the parameter listed in the 'Default' entry
   #        The order of indices doesn't matter -- they can be indexed in any order and the proper parameter will be selected.
   #                                 But beware, while you can supply an index that doesn't exist and still find the correct parameter,
   #                                 if an index does exist, it must be supplied or failure will result
   #
   #
   ####################################################################################################################################################




   ########################################## Final Curve Fit Limits in dac ######################################
   # First Element under head index is the initial limit which will force initial global retries.
   # The second element under head index is the final failure in subsequent global retries.
   # ZoneSlopeZones is an exception -- it specifies two zones (MSB and LSB) and does not change with global retry count
   # Signed values must lie between -128 and 127.  Unsigned values must lie between 0 and 255
   FinalCurveFitLimitsDAC = {
      'Max_IDOD_DeltaDAC':{
         # SIGNED: Maximum allowed (ID-OD) delta in Dac. Values must lie between -128 and +127.
         # First entry applies during initial global retries, last entry applies to final global retry
         # Causes: OD_ID_DAC_LIMIT_FAILURE           14703    /* Drive Head - Failed OD/ID Dac Limit */
         'WRITER_HEATER' :{
            ('M10P', 'M11P_BRING_UP')                            : {'TDK': (15,25), 'HWY': (15,25), 'RHO': (22,30), 'URHO': (35,50), 'USAE': (0,0), 'URHOA': (35,50)},
            'Crawford'                                           : {'TDK': (15,25), 'RHO': (0,0),   'URHO': (35,50), 'USAE': (0,0), 'URHOA': (35,50)},
            'Default'                                            : (0,0),
            'Lamarr'                                             : {'TDK': (15,28), 'URHO': (35,50)},
            'MakaraPlus'                                         : {'TDK': (30,60), 'HWY': (30,60), 'URHO': (35,80)},
            'Makara'                                             : (30,60),
            'Tatsu'                                              : {'TDK': (0,0), 'URHO': (75,150)},
            },
         'READER_HEATER':{
            'Default'                                            : (0,0),
            ('M10P', 'M11P_BRING_UP')                            : {'TDK' : (30,38), 'HWY' : (30,38), 'RHO': (22,30), 'URHO':(40,50),'USAE':(0,0),'URHOA':(40,50)},
            'Crawford'                                           : {'TDK': (30,38), 'RHO': (0,0),   'URHO': (40,50), 'USAE': (0,0), 'URHOA': (40,50)},
            'Lamarr'                                             : {'TDK': (28,55), 'URHO': (40,50)},
            'MakaraPlus'                                         : {'TDK': (25,60), 'HWY': (25,60), 'URHO': (40,85)},
            'Makara'                                             : (30,60),
            'Tatsu'                                              : {'TDK': (0,0), 'URHO': (75,150)},
            }
         },
      'Min_IDOD_DeltaDAC':{
         # SIGNED: Minimum allowed (ID-OD) delta in Dac. Values must lie between -128 and +127.
         # First entry applies during initial global retries, last entry applies to final global retry
         # Causes: OD_ID_DAC_LIMIT_FAILURE           14703    /* Drive Head - Failed OD/ID Dac Limit */
         'WRITER_HEATER':{
            'Crawford'                                           : {'TDK': (-25,-35),  'RHO': (30,50), 'URHO': (-30,-50)},
            ('M10P', 'M11P_BRING_UP')                            : {'TDK' : (-25,-35), 'HWY' : (-25,-35), 'RHO': (-50,-70), 'URHO':(-30,-50),'USAE':(0,0),'URHOA':(-30,-50)},
            'GrenadaBP2'                                         : {'RHO': (30,50),   'URHO': (30,50), 'USAE': (30,50)},
            'Lamarr'                                             : {'TDK': (-18,-30),  'URHO': (-30,-50)},
            'MakaraPlus'                                         : {'TDK': (-40,-85), 'HWY': (-40,-85), 'URHO': (-70,-85)},
            'Makara'                                             : (-30,-35),
            ( 'PharaohOasis', 'HepburnOasis' )                   : {'URHO': (50,60),'USAE': (30,50)},
            'Tatsu'                                              : {'TDK': (30,50), 'URHO': (-75,-150)},
            },
         'READER_HEATER':{
            ( 'PharaohOasis', 'HepburnOasis' )                   : {'URHO': (60,75),   'USAE': (30,50)},
            ('M10P', 'M11P_BRING_UP')                            : {'TDK': (-30,-50), 'HWY': (-30,-50), 'RHO': (-30,-50),   'URHO': (-50,-75), 'USAE': (0,0), 'URHOA': (-50,-75)},
            'Crawford'                                           : {'TDK': (-30,-50),  'URHO': (-50,-75)},
            'GrenadaBP2'                                         : (30,50),
            'Lamarr'                                             : {'TDK': (-33,-60),  'URHO': (-50,-75)},
            'Makara'                                             : (-35,-48),
            'MakaraPlus'                                         : {'TDK': (-36,-75), 'HWY': (-36,-75), 'URHO': (-90,-110)},
            'Tatsu'                                              : {'TDK': (30,50),    'URHO': (-75,-150)},
            }
         },
      'MaxDACRange':{
         # UNSIGNED: Maximum allowed contact dac range.  Values must lie betwee 0 and 255
         # First entry applies during initial global retries, last entry applies to final global retry
         # Causes: OD_ID_DAC_LIMIT_FAILURE           14703    /* Drive Head - Failed OD/ID Dac Limit */
         'WRITER_HEATER':{
            ( 'PharaohOasis', 'HepburnOasis' )                   : {'URHO': (50,65), 'USAE': (30,75)},
            ('M10P', 'M11P_BRING_UP')                            : {'TDK': (40,60), 'HWY': (40,60),  'RHO': (100,120), 'URHO': (40,75), 'USAE': (0,0), 'URHOA': (40,75)},
            'Crawford'                                           : {'TDK': (40,60),   'RHO': (30,75), 'URHO': (40,75), 'USAE': (30,75), 'URHOA': (40,75)},
            'GrenadaBP2'                                         : (30,75),
            'Lamarr'                                             : {'TDK': (40,60),   'URHO': (40,75)},
            'MakaraPlus'                                         : {'TDK': (50,80), 'HWY': (55,90), 'URHO': (50,100)},
            'Makara'                                             : (30,60),
            'Tatsu'                                              : {'TDK': (50,75),   'URHO': (50,65)},
            },
         'READER_HEATER':{
            ( 'PharaohOasis', 'HepburnOasis' )                   : {'URHO': (75,85), 'USAE': (40,75)},
            ('M10P', 'M11P_BRING_UP')                            : {'TDK': (70,90),  'HWY': (70,90),  'RHO': (100,120), 'URHO': (50,95),  'USAE': (0,0), 'URHOA':(50,95)},
            'Crawford'                                           : {'TDK': (70,90),   'RHO': (30,75), 'URHO': (50,95), 'USAE': (30,75), 'URHOA': (50,100)},
            'GrenadaBP2'                                         : (40,75),
            'Lamarr'                                             : {'TDK': (60,90),   'URHO': (50,100)},
            'MakaraPlus'                                         : {'TDK': (50,80),  'HWY': (50,90), 'URHO': (65,110)},
            'Makara'                                             : (45,60),
            'Tatsu'                                              : {'TDK': (75,75),   'URHO': (75,150)},
            }
         },
      'MinInterpolatedDAC':{
         # UNSIGNED: Minimum Interpolated DAC.  Values must lie between 0 and 255
         # First entry applies during initial global retries, last entry applies to final global retry
         # Causes: MIN_CLEARANCE_FAILURE             14710    /* DRV Head - Failed Min Clearance Limit  */
         'WRITER_HEATER':{
            ( 'PharaohOasis', 'HepburnOasis' )                   : {'URHO': (20,15), 'USAE': (20,15)},
            ('M10P', 'M11P_BRING_UP')                            : {'TDK': (20,12), 'HWY': (20,12), 'RHO': (15,12), 'URHO': (25,15), 'USAE': (0,0), 'URHOA':(25,15)},
            'Crawford'                                           : {'TDK': (45,20), 'URHO': (35,18)},
            'GrenadaBP2'                                         : {'RHO': (30,28), 'URHO': (20,15),'USAE': (20,15)},
            'Lamarr'                                             : {'TDK': (22,12), 'URHO': (35,18)},
            'Makara'                                             : (34,30),
            'MakaraPlus'                                         : {'TDK': (48,35), 'HWY': (48,35), 'URHO': (50,36)},
            'Tatsu'                                              : {'TDK': (12,12), 'URHO': (15,15)},
            },
         'READER_HEATER':{
            ( 'PharaohOasis', 'HepburnOasis' )                   : (35,30),
            ('M10P', 'M11P_BRING_UP')                            : {'TDK': (20,12), 'HWY': (20,12), 'RHO': (30,20), 'URHO': (60,30), 'USAE': (0,0), 'URHOA':(60,30)},
            'Crawford'                                           : {'TDK': (12,12), 'RHO': (55,53),'URHO': (70,50)},
            'GrenadaBP2'                                         : {'RHO': (55,53), 'URHO': (35,30),'USAE': (35,30)},
            'Lamarr'                                             : {'TDK': (20,10), 'URHO': (60,45)},
            'Makara'                                             : (45,40),
            'MakaraPlus'                                         : {'TDK': (55,35), 'HWY': (50,35), 'URHO': (70,40)},
            'Tatsu'                                              : {'TDK': (12,12), 'URHO': (12,12)},
            }
         },
      'ZoneSlopeZones':{
         # MSB/LSB specifies zones to use for zone-to-zone delta.  0x0401 will apply limit to (zone4-zone1)
         # Zone-to-Zone delta is a signed limit calculated using the zones specified: MSB minus LSB
         'WRITER_HEATER':{
            ( 'PharaohOasis', 'HepburnOasis' )                   : 0x0b00,
            ('M10P', 'M11P_BRING_UP')                            : {'TDK': 0x1E00, 'HWY': 0x1E00, 'RHO': 0x0400, 'URHO': 0x0b00, 'USAE': 0x0400, 'URHOA': 0x0b00},
            'Crawford'                                           : {'TDK': 0x1E00, 'RHO': 0x0400, 'URHO': 0x0700 },
            'Default'                                            : 0x0400,
            'GrenadaBP2'                                         : {'RHO': 0x0400, 'URHO': 0x0b00, 'USAE': 0x0f00},
            'Lamarr'                                             : 0x1E00},
         'READER_HEATER':{
            'Default'                                            : 0x0400,
            ('M10P', 'M11P_BRING_UP')                            : {'TDK': 0x1E00, 'HWY': 0x1E00, 'RHO': 0x0400, 'URHO': 0x0b00, 'USAE': 0x0400, 'URHOA': 0x0b00},
            ( 'Lamarr', 'Crawford' )                             : {'TDK': 0x1E00, 'RHO': 0x0400, 'URHO': 0x1E00},
            'GrenadaBP2'                                         : {'Default': 0x0400, 'USAE': 0x0f00}}
         },
      'MaxZoneToZoneSlope':{
         # SIGNED: Maximum allowed signed delta between the two zones specified in ZoneSlopeZones.  Values must lie between -128 and +127
         # First entry applies during initial global retries, last entry applies to final global retry
         # Causes: ZONE_SPAN_DAC_DELTA_FAILURE       14941    /* Zone Span DAC Delta check failed */
         'WRITER_HEATER':{
            'Default'                                            : (127,127),
            ('M10P', 'M11P_BRING_UP')                            : {'TDK': (127,127), 'HWY': (127,127), 'RHO': (20,127),'URHO': (15,127),'USAE': (127,127),'URHOA': (15,127)},
            'Crawford'                                           : {'Default': (127,127),'URHO': (18,22)},
            'GrenadaBP2'                                         : {'RHO': (15,127), 'URHO':  (15,127),'USAE': (20,127)}},
         'READER_HEATER':{
            'Default'                                            : (127,127),
            ('M10P', 'M11P_BRING_UP')                            : {'TDK' : (127,127), 'HWY' : (127,127), 'RHO': (20,127), 'URHO':(15,127),'USAE':(127,127),'URHOA':(15,127)},
            'GrenadaBP2'                                         : {'Default': (127,127),'USAE': (33,127)}}
         },
      'MinZoneToZoneSlope':{
         # SIGNED: Minimum allowed signed delta between the two zones specified in ZoneSlopeZones.  Values must lie between -128 and +127
         # First entry applies during initial global retries, last entry applies to final global retry
         # Causes: ZONE_SPAN_DAC_DELTA_FAILURE       14941    /* Zone Span DAC Delta check failed */
         'WRITER_HEATER':{
            'Default'                                            : (-127,-127),
            ('M10P', 'M11P_BRING_UP')                            : {'TDK' : (-127,-127), 'HWY' : (-127,-127), 'RHO': (-35,-127), 'URHO':(-35,-127),'USAE':(-127,-127),'URHOA':(-35,-127)},
            'GrenadaBP2'                                         : {'RHO': (-15,-127), 'URHO': (-15,-127), 'USAE': (4,-127)}},
         'READER_HEATER':{
            'Default'                                            : (-127,-127),
            ('M10P', 'M11P_BRING_UP')                            : {'TDK' : (-127,-127), 'HWY' : (-127,-127), 'RHO': (-45,-127), 'URHO':(-45,-127),'USAE':(-127,-127),'URHOA':(-45,-127)},
            'GrenadaBP2'                                         : {'Default': (-127,-127),'USAE': (9,-127)}}
         },
      'MaxSearchInterference':{
         # UNSIGNED: Maximum interference in dac based on final interpolation (maximum dacs into contact).  Values must lie between 0 and 255
         # Interference is determed as the maximum tested heater dac minus the final interpolated contact dac in that zone
         # Causes: DELTA_DAC_MAXED_OUT               14925    /* Delta DAC Exceeded */           Note: causes 14567 on LCO Branch
         #
         'Default'      : 120,
         },
      'MaxExtrapolationTracks':{
         # UNSIGNED: Maximum number of tracks the final dual curve fit can extrapolate
         # Causes: TOO_FEW_POINTS_FOR_FINAL_FIT      14841    /* Too Few Data Points for Final Fit */
         'Default'      : 32000,
         ( 'AstorMule', 'GrenadaBP2',  'PharaohOasis', 'HepburnOasis' )            : 25000,
         ( 'M10P', 'M11P_BRING_UP')                                                : 32000,
         ( 'Makara', 'MakaraPlus', 'Tatsu' )                                       : 28000,
         },
      'MaxPredictionInterval':{
         # UNSIGNED: Maximum allowed prediction interval on the final curve fit.  Units in DAC.  Values must lie between 0 and 255
         # First entry applies during initial global retries, last entry applies to final global retry
         # Causes: FINAL_CURVE_FIT_STDDEV_FAILURE    14942    /* Final Curve Fit Std Dev Limit Exceeds */
         'WRITER_HEATER':{
            'Default'                                            : (10,20),
            ('M10P', 'M11P_BRING_UP')                            : {'TDK': (10,15), 'HWY': (10,15), 'RHO': (150,300),'URHO': ( 10, 20),'USAE': (10,20),'URHOA':(10,20)},
            'Crawford'                                           : {'TDK': (10,15), 'RHO': (10,20),'URHO': (10,30)},
            'MakaraPlus'                                         : {'TDK': (15,30), 'HWY': (20,30), 'URHO': (20,30)}, 
            'Tatsu'                                              : {'TDK': (10,30), 'URHO': (10,30)},
            },
         'READER_HEATER':{
            'Default'                                            : (20,40),
            ('M10P', 'M11P_BRING_UP')                            : {'TDK': (15,20), 'HWY': (15,20), 'RHO': (200,400),'URHO': ( 20, 40),'USAE': (25,50), 'URHOA':(20,40)},
            'Crawford'                                           : {'TDK': (15,20),  'RHO': (25,50),'URHO': (35,60)},
            'Lamarr'                                             : {'TDK': (20,40),  'URHO': (22,45)},
            'MakaraPlus'                                         : {'TDK': (15,30), 'HWY': (25,30), 'URHO': (25,30)}, 
            ( 'PharaohOasis', 'HepburnOasis' )                   : {'URHO': (20,40), 'USAE': (20,40)},
            'Tatsu'                                              : {'TDK': (20,40),  'URHO': (20,40)}}
         },
      'DeletedResidualDiscardLimit':{
         # UNSIGNED: Maximum allowed deleted residual before a point is discarded from final curve fit.
         # Units in tenths of a dac.  A limit of 50 = 5 Dac
         'WRITER_HEATER':{
            'Default'                                            : (120,125),
            ('M10P', 'M11P_BRING_UP')                            : {'TDK' : (120,125), 'HWY' : (120,125), 'RHO': (120,120), 'URHO':(120,125),'USAE':(120,125),'URHOA':(120,125)},
            'Crawford'                                           : {'TDK': (120,125), 'RHO': (120,125),'URHO': (195,200)},
            'Lamarr'                                             : {'TDK': (195,200), 'URHO': (195,200)},
            'Makara'                                             : (80,120),
            'MakaraPlus'                                         : (150,200),
            'Tatsu'                                              : {'TDK': (120,120), 'URHO': (80,120)},
            },
         'READER_HEATER':{
            'Default'                                            : (120,120),
            ('M10P', 'M11P_BRING_UP')                            : {'TDK' : (120,140), 'HWY' : (120,140), 'RHO': (140,140), 'URHO':(140,145),'USAE':(140,145),'URHOA':(140,145)},
            'Crawford'                                           : {'TDK': (120,140), 'RHO': (140,145),'URHO': (225,230)},
            'GrenadaBP2'                                         : {'RHO': (140,145),'URHO': (140,145),'USAE': (140,145)},
            'Lamarr'                                             : {'TDK': (225,230),'URHO': (225,230)},
            'MakaraPlus'                                         : (160,200),
            ( 'PharaohOasis', 'HepburnOasis' )                   : {'URHO': (140,145), 'USAE': (140,145)},
            }
         },
      }

   ####################################################################################################################


   ########################################## Final Curve Fit Limits in Angstrom ######################################
   # First Element under head index is the initial limit which will force initial global retries.
   # The second element under head index is the final failure in subsequent global retries.
   FinalCurveFitLimitsAngstrom = {
     'InterpolatedBurnish': {
        # SIGNED limit on the upper and lower 95th percentile burnish calculated by subtracting rap clearance from current interpolated clearance.  Values must lie between -128 and 127
        # StateList specifies the list of states in which the burnish check will run.
        # Causes: POSITIVE_BURNISH_FAILURE          15006    /* T135: Burnish failure */  or
        #         NEGATIVE_BURNISH_FAILURE          15007    /* T135: Burnish failure */
        'WRITER_HEATER':{'Default'  : {'USL': 127, 'LSL': -127, 'StateList':[2,3,4,6,7]}},
        'READER_HEATER':{'Default'  : {'USL': 127, 'LSL': -127, 'StateList':[2,3,4,6,7]}}},
     'Max_IDOD_DeltaClr':{
        # SIGNED: Maximum ID minus OD Delta in Angstrom.  Signed value calcualted as (ID-OD).  Values must lie between -128 and +127
        # First entry applies during initial global retries, last entry applies to final global retry
        # Causes: OD_ID_CLEARANCE_LIMIT_EXCEEDED    14846    /* OD ID Clearance Limit Failure */
        'WRITER_HEATER':{
           'Default'                                             : (0,0),
           ('M10P', 'M11P_BRING_UP')                             : (100,-100),
           'Makara'                                              : (18,18),
           'MakaraPlus'                                          : (20,20),
           'Tatsu'                                               : (25,35)},
        'READER_HEATER':{
           'Default'                                             : (0,0),
           ('M10P', 'M11P_BRING_UP')                             : (100,100),
           'Makara'                                              : (25,25),
           'MakaraPlus'                                          : (25,25),
           'Tatsu'                                               : {'TDK': (35,45), 'URHO': (25,25)}}
        },
     'Min_IDOD_DeltaClr':{
        # SIGNED: Minimum ID minus OD Delta in Angstrom.  Signed value calcualted as (ID-OD).  Values must lie between -128 and +127
        # First entry applies during initial global retries, last entry applies to final global retry
        # Causes: OD_ID_CLEARANCE_LIMIT_EXCEEDED    14846    /* OD ID Clearance Limit Failure */
        'WRITER_HEATER':{
           'Default'                                             : (127,127),
           ('M10P', 'M11P_BRING_UP')                             : (-100,-100),
           'Makara'                                              : (-127,-127),
           'MakaraPlus'                                          : {'TDK': (-20,-40), 'HWY': (-25,-45), 'URHO': (-30,-45)},
           'Tatsu'                                               : (-127,-127)},
        'READER_HEATER':{
           'Default'                                             : (127,127),
           ('M10P', 'M11P_BRING_UP')                             : (-100,-100),
           'Makara'                                              : (-127,-127),
           'MakaraPlus'                                          : {'TDK': (-15,-40), 'HWY': (-20,-40), 'URHO': (-23,-40)},
           'Tatsu'                                               : (-127,-127)}
        },
     'MaxClrRange':{
        # UNSIGNED: Maximum Clearance range in Angstrom.  Values must lie between 0 and 255
        # First entry applies during initial global retries, last entry applies to final global retry
        # Causes: MAX_ALL_ZONE_CLEARANCE_LIMIT_EXCEEDED 14848 /* Max All Zone Clearance limit failure */
        'WRITER_HEATER':{
           'Default'                                             : (127,127)},
        'READER_HEATER':{
           'Default'                                             : (127,127)}},
     'MaxConsistencyLimit':{
        # SIGNED: Maximum allowed delta in angstrom between HO and WPH clearance.
        # Signed values calculated as (HO-WPH) and must lie between -128 and +127
        # First entry applies during initial global retries, last entry applies to final global retry
        # Causes: MAX_WIRP_CLEARANCE_LIMIT_EXCEEDED 14847    /* Max WIRP Clearance Limit Failure */
        'PreHirp':{
           'WRITER_HEATER':{
              'Default'                                          : (0,0)},
           'READER_HEATER':{
              'Default'                                          : (0,0)}
           },
        'PostHirp':{
           'WRITER_HEATER':{
              'Default'                                          : (0,0)},
           'READER_HEATER':{
              'Default'                                          : (0,0)}
           }
        },
     'MinConsistencyLimit':{
        # SIGNED: Minimum allowed delta in angstrom between HO and WPH clearance.
        # Signed values calculated as (HO-WPH) and must lie between -128 and +127
        # First entry applies during initial global retries, last entry applies to final global retry
        # Causes: MAX_WIRP_CLEARANCE_LIMIT_EXCEEDED 14847    /* Max WIRP Clearance Limit Failure */
        'PreHirp':{
           'WRITER_HEATER':{
              'Default'                                          : (25,25)},
           'READER_HEATER':{
              'Default'                                          : (25,25)}
           },
        'PostHirp':{
           'WRITER_HEATER':{
              'Default'                                          : (25,25)},
           'READER_HEATER':{
              'Default'                                          : (25,25)}
           }
        },
     'MaxCrossHeaterConsistencyLimit':{
        # SIGNED: Maximum allowed delta in angstrom between Preheat and Read clearance.  Current measured result is compared against RAP profile of
        # other heater.  Signed values calculated as (Read-Preheat) and must lie between -128 and +127
        # First entry applies during initial global retries, last entry applies to final global retry
        # Causes: XHEATER_CLR_DELTA_EXCEEDED        42197    /* AFH- Cross heater clearance delta exceeded. */
        'PreHirp':{
           ( 'PharaohOasis', 'HepburnOasis', 'GrenadaBP2' )      : (47,65),
           'MakaraPlus'                                          : {'TDK': (34,46), 'HWY': (34,46), 'URHO': (26,36)},
           'Tatsu'                                               : {'TDK': (43,53), 'URHO': (43,53)},
           ('M10P', 'M11P_BRING_UP')                             : {'TDK': (20,27), 'HWY': (20,27), 'RHO': (43,53),'URHO': (25,35),'USAE': (20,27),'URHOA': (25,35)},
           'Crawford'                                            : {'TDK': (20,27), 'URHO': (20,40)},
           'Lamarr'                                              : {'TDK': (50,80), 'URHO': (20,40)},
           'Makara'                                              : (43,53)},
        'PostHirp':{
           'Default'                                             : (33,43),
           'MakaraPlus'                                          : {'TDK': (24,30), 'HWY': (24,30), 'URHO': (18,30)},
           ('M10P', 'M11P_BRING_UP')                             : {'TDK': (20,27), 'HWY': (20,27), 'RHO': (33,43),'URHO': (25,35),'USAE': (20,27),'URHOA': (25,35)},
           'Crawford'                                            : {'TDK': (20,27), 'URHO': (25,40)},
           'Lamarr'                                              : {'TDK': (50,80), 'URHO': (25,40)},
           ( 'PharaohOasis', 'HepburnOasis', 'GrenadaBP2' )      : (44,52)},
        },
     'MinCrossHeaterConsistencyLimit':{
        # SIGNED: Minimum allowed delta in angstrom between Preheat and Read clearance.  Current measured result is compared against RAP profile of
        # other heater.  Signed values calculated as (Read-Preheat) and must lie between -128 and +127
        # First entry applies during initial global retries, last entry applies to final global retry
        # Causes: XHEATER_CLR_DELTA_EXCEEDED        42197    /* AFH- Cross heater clearance delta exceeded. */
        'PreHirp':{
           'Default'                                             : (-47,-65),
           ('M10P', 'M11P_BRING_UP')                             : {'TDK': (-20,-40), 'HWY': (-20,-40), 'RHO': (-27,-37),'URHO': (-10,-25),'USAE': (-20,-40),'URHOA': (-10,-25)},
           'Crawford'                                            : {'TDK': (-20,-40), 'URHO': (-20,-30)},
           'Lamarr'                                              : {'TDK': (-50,-80), 'URHO': (-20,-30)},
           'Tatsu'                                               : (-40,-50),
           'MakaraPlus'                                          : {'TDK': (-30,-42), 'HWY': (-30,-42), 'URHO': (-30,-40)},
           'Makara'                                              : (-30,-40)},
        'PostHirp':{
           'Default'                                             : (-26,-34),
           ('M10P', 'M11P_BRING_UP')                             : {'TDK': (-20,-40), 'HWY': (-20,-40), 'RHO': (-30,-40),'URHO': (-10,-25),'USAE': (-20,-40),'URHOA': (-10,-25)},
           'Crawford'                                            : {'TDK': (-20,-40), 'URHO': (-20,-30)},
           'Lamarr'                                              : {'TDK': (-50,-80), 'URHO': (-20,-30)},
           'Tatsu'                                               : (-40,-50),
           'MakaraPlus'                                          : {'TDK': (-10,-40), 'HWY': (-10,-40), 'URHO': (-20,-35)},
           'Makara'                                              : (-30,-40)},
        },
     'MaxRapConsistencyLimit':{
        # SIGNED: Maximum allowed delta in angstrom between current measured result and the corresponding RAP profile
        # Signed values calculated as (Current-Rap) and must lie between -128 and +127
        # First entry applies during initial global retries, last entry applies to final global retry
        # Causes: DELTA_VS_RAP_CLEARANCE_EXCEEDED   48394    /* Clearance Delta vs. RAP Exceeded Limit */
        'WRITER_HEATER':{
           'Default'                                             : (13,26),
           ('M10P', 'M11P_BRING_UP')                             : (30,40),
           ('Tatsu','MakaraPlus')                                : (20,40)},
        'READER_HEATER':{
           'Default'                                             : (13,26),
           ('M10P', 'M11P_BRING_UP')                             : (30,40),
           ('Tatsu','MakaraPlus')                                : (20,40)},
        },
     'MinRapConsistencyLimit':{
        # SIGNED: Minimum allowed delta in angstrom between current measured result and the corresponding RAP profile
        # Signed values calculated as (Current-Rap) and must lie between -128 and +127
        # First entry applies during initial global retries, last entry applies to final global retry
        # Causes: DELTA_VS_RAP_CLEARANCE_EXCEEDED   48394    /* Clearance Delta vs. RAP Exceeded Limit */
        'WRITER_HEATER':{
           'Default'                                             : (-13,-26),
           ('M10P', 'M11P_BRING_UP')                             : (-30,-40),
           ('Tatsu', 'MakaraPlus')                               : (-20,-40)},
        'READER_HEATER':{
           'Default'                                             : (-13,-26),
           ('M10P', 'M11P_BRING_UP')                             : (-30,-40),
           ('Tatsu', 'MakaraPlus')                               : (-20,-40)}
        }
     }
   ###################################################################################################################

   ######################################  FastIO Revs ###############################################################
   ###

   FastIOSetup={
      'FastIORevs':{
         # Number of fastIO revs collected and averaged during the zeroeth internal retry
         'Default':{
            'HighSkew'                                           : {'Initial': 30, 'InternalRetry':50 },
            'LowSkew'                                            : {'Initial': 30, 'InternalRetry':50 }},
         ('Crawford','Lamarr') :{
            'WRITER_HEATER'                                      :{'Initial': 30, 'InternalRetry':50},
            'READER_HEATER'                                      :{'Initial': 30, 'InternalRetry':{'TDK':42,'URHO':50}}},
         'MakaraPlus'                                            :30,
         'Tatsu'                                                 :30,
         ('M10P', 'M11P_BRING_UP')                               :30,
         },
      'lowSkewZones':{
         ('M10P', 'M11P_BRING_UP')                               : {'60Zone' : (20,44), '150Zone' : (50, 110), '250Zone' : (83,196)},
         'Crawford'                                              : {'60Zone' : (21,44), '250Zone' : (83,196)},
         ('GrenadaBP2', 'PharaohOasis', 'HepburnOasis' )         : (20,44),
         ('Lamarr','Makara')                                     : {'60Zone' : (20,47), '250Zone' : (83,196)},
         ( 'MakaraPlus', 'Tatsu' )                               : (95,159)
      }
   }

   ####################################################################################################################

   ######################################  On the fly contact dac regression limits ###################################
   ### These limits apply during the contact search.  Dac limit failures will cause an internal retry
   ### These do not apply to the final interpolation and will not (directly) cause test failures or global retries

   SearchLimits = {
      'ZoneOrder':{
         # First key within product indicates AFH state.  List dictates order in which zones are measured
         # NOTE: if the curve fit is enabled in AFH3 and 4 or if FAFH is enabled, the AFH3 and 4 zone orders are forced to match AFH2

         ('M10P', 'M11P_BRING_UP'):       {1  :(130,10,95,25,110,40,0,149),
                                           2  :(130,10,95,25,110,40,0,149),
                                           3  :(130,10,95,25,110,40,0,149),
                                           4  :(130,10,95,25,110,40,0,149)},
         ('Crawford',
          'Lamarr')         : {'60Zone' : {1  :(51,7,47,3,56,59,22,41,14,0),
                                           2  :(51,7,47,3,56,59,22,41,14,0),
                                           3  :(0,7,14,47,59),
                                           4  :(0,7,14,47,59)},
                              '250Zone' : {1  :(212,33,183,54,108,84,16,232,0,249),
                                           2  :(212,33,183,54,108,84,16,232,0,249),
                                           3  :(0,54,108,183,249),
                                           4  :(0,54,108,183,249)}},

         ( 'GrenadaBP2',
           'PharaohOasis',
           'HepburnOasis' ) : {1  :(58,4,50,12,42,22,59,1,0),
                               2  :(58,4,50,12,42,22,59,1,0),
                               3  :(58,4,50,12,1),
                               4  :(58,4,50,12,1)},

         'Makara'           : {'60Zone'  : {1  :(51,8,45,13,39,18,4,56,0,59,27),
                                            2  :(51,8,45,13,39,18,4,56,0,59,27),
                                            3  :(51,8,45,13,39,18,4,56,0,59,27),
                                            4  :{'WRITER_HEATER': (51,8,45,13,39,18,4,56,0,59,27), 'READER_HEATER':(0,13,27,45,59)},
                                            6  :(51,8,45,13,39,18,4,56,0,59,27)},
                               '250Zone' : {1  :(212,33,183,54,108,84,16,232,0,249),
                                            2  :(212,33,183,54,108,84,16,232,0,249),
                                            3  :(0,54,108,183,249),
                                            4  :(0,54,108,183,249)}},

          'MakaraPlus'      : {1  :(216,33,165,94,191,74,16,232,115,0,249,53),
                               2  :(216,33,165,94,191,74,16,232,115,0,249,53),
                               3  :(0,53,94,165,191,249),
                               4  :(0,53,94,165,191,249),
                               6  :(216,33,165,94,191,74,16,232,115,0,249,53)},

          'Tatsu'           : {1  :(216,33,165,94,191,74,16,232,115,0,249,53),
                               2  :(216,33,165,94,191,74,16,232,115,0,249,53),
                               3  :(216,33,165,94,191,74,16,232,115,0,249,53),
                               4  :(216,33,165,94,191,74,16,232,115,0,249,53),
                               6  :(216,33,165,94,191,74,16,232,115,0,249,53),
                               7  :(216,33,165,94,191,74,16,232,115,0,249,53)},
         },
      'MaxExtrapolationTracks':{
         # UNSIGNED: Maximum On the fly regression extrapolation in tracks.  If limit is exceeded the OTF regression is disabled
         ( 'AstorMule', 'Crawford', 'Lamarr' )                                                 : 54000,
         ( 'M10P', 'M11P_BRING_UP')                                                            : 25000,
         ( 'Grenada', 'GrenadaBP15', 'GrenadaBP2', 'PharaohOasis', 'HepburnOasis' )            : 42000,
         ( 'Makara', 'MakaraPlus', 'Kahuna', 'KahunaR', 'KM9', 'Tatsu' )                       : 40000,
         },
      'MinWICD':{
         'WRITER_HEATER':{
            # UNSIGNED: Minimum allowed delta between WPH and HO contact dac.  Forces internal retries
            # First index applies in AFH1, second in all subsequent states.  LSB applies during initial attempt. MSB applies during internal retries
            'Default'               : (0x0102,0x0102),
            ( 'M10P', 'M11P_BRING_UP')  : (0x0102,0x0102),
            ('Makara','Tatsu')      : (0x0204,0x0204)},
         'READER_HEATER':{
            'Default'               : (0x0204,0x0204)},
         },
      'MaxWICD':{
         # UNSIGNED: Maximum allowed delta between WPH and HO contact dac.  Forces internal retries
         # First index applies in AFH1, second in all subsequent states.  LSB applies during initial attempt. MSB applies during internal retries
         'WRITER_HEATER':{
            'Default'                                       : (0x241E,0x241E),
            ( 'AstorMule', 'M10P', 'M11P_BRING_UP', 'Crawford', 'Lamarr' )    : {'TDK': (0x140F,0x140F), 'HWY': (0x140F,0x140F), 'RHO': (0x241E,0x241E),'URHO': (0x1E10,0x1E16),'URHOA': (0x1E10,0x1E16)},
            'MakaraPlus'                                    : (0x3246, 0x3246)},
         'READER_HEATER':{
            'Default'                                       : (0x241E,0x241E)}
         },
      'DacRangeLimits':{
         # SIGNED: Determines how far the search starts before the expected contact dac and how far beyond it is allowed to go
         # We allow two different settings for all three sub parameters in DAC_RANGE.  One when the on the fly curve fit is running (index: 'OTF_CurveFit')
         # And another when we're running off the rap (index: 'RapBased')
         'BackOffFromExpectedContact':{
            #This determines how far we back up from the expected contact dac to start the search.
            #Enter as a negative number
            'WRITER_HEATER':{
               'Default'                                    : {'OTF_CurveFit': -21, 'RapBased': -21},
               ('AstorMule', 'M10P', 'M11P_BRING_UP', 'Crawford')             : {'OTF_CurveFit': -32, 'RapBased': -32},
               'MakaraPlus'                                 : {'OTF_CurveFit': -42, 'RapBased': -42}},
            'READER_HEATER':{
               'Default'                                    : {'OTF_CurveFit': -50,  'RapBased': -42},
               'MakaraPlus'                                 : {'OTF_CurveFit': -90,  'RapBased': -80},
               ('AstorMule', 'M10P', 'M11P_BRING_UP', 'Crawford')             : {'OTF_CurveFit': -60,  'RapBased': -52}},
            },
         'MinimumPushBeyondExpectedContact':{
            #When the on the fly curve fit is running the end dac is determined by the 95% prediction interval on that regression in the given zone
            #If the curve fit has very low uncertainty, the PI will be small and the search can be stopped too soon after crossing the expected contact dac
            #use this parameter to ensure the end dac is at least "x" dacs beyond the expected contact dac.
            #When running off the rap clearance, this parameter is not used... but values are still needed in states 2 through 4 because it is possible that running
            #off the rap be disabled during global retries.
            #First Entry applies during initial internal retries, second entry is used during second and all subsequent internal retries
            'WRITER_HEATER':{
               'Default'                                    : {'OTF_CurveFit': [6,6],  'RapBased': [18,18]},
               'MakaraPlus'                                 : {'OTF_CurveFit': [12,12], 'RapBased': [36,36]},
               ( 'AstorMule', 'M10P', 'M11P_BRING_UP' )     : {'OTF_CurveFit': [8,12], 'RapBased': [18,25]},
               ( 'Crawford', 'Lamarr' )                     : {'OTF_CurveFit': [6,10], 'RapBased': [18,30]}},
            'READER_HEATER':{
               'Default'                                    : {'OTF_CurveFit': [12,12], 'RapBased': [30,30]},
               'MakaraPlus'                                 : {'OTF_CurveFit': [24,24], 'RapBased': [60,60]},
               ( 'AstorMule', 'M10P', 'M11P_BRING_UP', 'Crawford', 'Lamarr' ) : {'OTF_CurveFit': [12,20], 'RapBased': [30,45]}}
            },
         'MaximumPushBeyondExpectedContact':{
            #When the on the fly curve fit is running the end dac is determined by the 95% prediction interval on that regression in the given zone
            #If the curve fit has very high uncertainty, the regression is unreliable and should be disabled.  This limit specifies the maximum prediction interval.
            #When the PI is above this limit, the on the fly curve fit is disabled during the given internal retry
            #When running off the rap clearance, this parameter specifies how far the search is allowed to go beyond the expected contact dac
            #First Entry applies during initial internal retries, second entry is used during second and all subsequent internal retries
            'WRITER_HEATER':{
               'Default'                                    : {'OTF_CurveFit': [18,30], 'RapBased': [18,18]},
               'MakaraPlus'                                 : {'OTF_CurveFit': [36,60], 'RapBased': [36,36]},
               ( 'AstorMule', 'M10P', 'M11P_BRING_UP', 'Crawford', 'Lamarr' ) : {'OTF_CurveFit': [16,24], 'RapBased': [18,30]}},
            'READER_HEATER':{
               'Default'                                    : {'OTF_CurveFit': [30,45], 'RapBased': [30,30]},
               'MakaraPlus'                                 : {'OTF_CurveFit': [60,90], 'RapBased': [60,60]},
               ( 'AstorMule', 'M10P', 'M11P_BRING_UP', 'Crawford', 'Lamarr' ) : {'OTF_CurveFit': [45,70], 'RapBased': [30,45]}}}},
      'MaxZoneToZoneDelta':{
         # UNSIGNED: Maximum allowed zone to zone delta used during on the fly curve fit.  Forces internal retries
         # First index applies in AFH1, second in all subsequent states.  LSB applies during initial attempt. MSB applies during internal retries
         'WRITER_HEATER':{
            'Default'                                       : (0x0C0A,0x0C0A),
            'MakaraPlus'                                    : (0x1814,0x1814),
            },
         'READER_HEATER':{
            'Default'                                       : (0x0C0A,0x0C0A),
            'MakaraPlus'                                    : (0x1814,0x1814),
            }
         },
      'MinOTFBurnishLimitsInAngstrom':{
         # These On the Fly burnish limits apply after contact is declared in each zone
         # They are used in aFH states in which the search is based off the rap clearance (AFH2-4)
         # Burnish is defined as the current measured clearance (not interpolated) minus the the rap clearance
         # This dictionary contains the minimum allowed burnish.  A value of 10A entered here will ensure that if the current
         #    meausured clearance is more than 10 angstrom *lower* than the rap value, an internal retry will be issued.  Enter as a positive number!!
         # If the delta is exceeded the zone will be marked bad and an internal retry issued
         # The first entry applies in AFH2, the second in AFH3 and 4.  LSB contains initial limit, MSB applies after 2nd internal retry
         'WRITER_HEATER':{
            'Default'      :   (0x190A,0x190A)},
         'READER_HEATER':{
            'Default'      :   {'TDK': (0x190A,0x0C0A), 'HWY': (0x190A,0x0C0A), 'RHO': (0x190A,0x190A),'URHO': (0x190A,0x190A),'USAE': (0x190A,0x190A),'URHOA': (0x190A,0x190A)}}
         },
      'MaxOTFBurnishLimitsInAngstrom':{
         # These On the Fly burnish limits apply after contact is declared in each zone
         # They are used in aFH states in which the search is based off the rap clearance (AFH2-4)
         # Burnish is defined as the current measured clearance (not interpolated) minus the the rap clearance
         # This dictionary contains the minimum allowed burnish.  A value of 10A entered here will ensure that if the current
         #    meausured clearance is more than 10 angstrom *higher* than the rap value, an internal retry will be issued.  Enter as a positive number!!
         # If the delta is exceeded the zone will be marked bad and an internal retry issued
         # The first entry applies in AFH2, the second in AFH3 and 4.  LSB contains initial limit, MSB applies after 2nd internal retry
         'WRITER_HEATER':{
            'Default'      :   (0x190A,0x190A)},
         'READER_HEATER':{
            'Default'      :   {'TDK': (0x190A,0x0C0A), 'HWY': (0x190A,0x0C0A), 'RHO': (0x190A,0x190A),'URHO': (0x190A,0x190A),'USAE': (0x190A,0x190A),'URHOA': (0x190A,0x190A)}}
         },
      'GlobalHeaterLimits':{
         # First Entry is the start dac for initial zones.  Second Entry is the maximum global heater dac
         # Third Entry is search step in dac.  MSB=fine, LSB=coarse.  Fourth entry is the fine search backup
         'WRITER_HEATER':{
            ( 'PharaohOasis', 'HepburnOasis', 'GrenadaBP2' )   : {'RHO': (25,230,0x0103,6), 'URHO': (12,230,0x0103,6),'USAE': (12,230,0x0103,6)},
            ( 'AstorMule', 'M10P', 'M11P_BRING_UP' )           : {'TDK': (20,230,0x0104,8), 'HWY': (20,230,0x0104,8), 'RHO': (30,230,0x0103,8),'URHO': (12,230,0x0103,6),'USAE': (25,230,0x0103,6),'URHOA': (12,230,0x0103,6)},
            'Crawford'                                         : {'TDK': (20,230,0x0104,8), 'RHO':  (25,230,0x0103,6),'URHO': (15,230,0x0105,10)},
            'GrenadaBP2'                                       : {'RHO': (25,230,0x0103,6), 'URHO': (12,230,0x0103,6),'USAE': (12,230,0x0103,6)},
            'Lamarr'                                           : {'TDK': (15,210,0x0102,10),'URHO': (15,210,0x0105,10)},
            'Tatsu'                                            : {'TDK': (18,200,0x0103,6), 'URHO': (15,160,0x0103,6)},
            'MakaraPlus'                                       : {'TDK': (18,230,0x0103,10), 'HWY': (18,230,0x0103,10), 'URHO': (18,230,0x0102,10)},
            'Makara'                                           : (15,160,0x0102,6),
            },
         'READER_HEATER':{
            ( 'AstorMule', 'M10P', 'M11P_BRING_UP' )           : {'TDK': (20,250,0x0104,8), 'HWY': (20,250,0x0104,8), 'RHO': (30,250,0x0103,10),'URHO': (30,250,0x0203,10),'USAE': (50,250,0x0204,10),'URHOA': (30,250,0x0203,10)},
            'Crawford'                                         : {'TDK': (20,250,0x0104,8), 'RHO' : (50,250,0x0203,10),'URHO': (30,250,0x0207,16)},
            'Lamarr'                                           : {'TDK': (15,250,0x0102,16),'URHO': (30,250,0x0207,16)},
            'Makara'                                           : (30,250,0x0205,10),
            'Tatsu'                                            : {'TDK': (18,250,0x0103,6), 'URHO': (30,250,0x0205,10)},
            'MakaraPlus'                                       : (18,250,0x0205,14),
            ( 'PharaohOasis', 'HepburnOasis','GrenadaBP2' )    : {'RHO': (50,250,0x0204,10),'URHO': (25,250,0x0204,10), 'USAE': (25,250,0x0204,10)}
            },
         }
   }
   ####################################################################################################################

   ######################################  Search Options ###################################
   ### These limits apply during the contact search.  Dac limit failures will cause an internal retry
   ### These do not apply to the final interpolation and will not (directly) cause test failures or global retries
   SearchOptions = {
      'MasterDetectorEnable' : {
         # Enter a list of detectors to enable.  Any detector not listed will be run in open loop mode.  Valid detectos are 1:6
         'Default'      :  [1,2,3,4,5,6],
         ( 'M10P', 'M11P_BRING_UP') : [1,2,3,5,6],
         'Makara'       :  [1,3,5,6],
         'MakaraPlus'   :  [1,3,5,6],
         },
      'UpdateRapClearanceStateIndexList' : {
         # Enter a list of AFH state indices in which update the rap clearance
         'Default'      :  [1,2],
         ( 'M10P', 'M11P_BRING_UP') : [1,2,3],
         'Makara'       :  [1,2,6],
         'MakaraPlus'   :  [1,2,6],
         },
      'WriteTripletForOpenLoopStates' : {
         # Enter the write triplet as a list to be used in aFH states in which the rap clearance is not updated.
         # This feature reduces burnish and test time by keeping T135 from having to add extra zones at write triplet transitions
         # An empty list will disable the feature, and the adapted triplet replete with whatever added zones
         # To ease maintenance, if AFH1_WriteTriplet is anything other than (-1,-1,-1), that triplet will be used rather than what is specified here
         'Default'             :  [5,5,5],
         'Tatsu'               :  [-1,-1,-1],
         ('AstorMule', 'M10P', 'M11P_BRING_UP' ) :  [-1,-1,-1],
         },
      'CoarseConfirmInterferenceInDac' : {
         # If a detector trips in the coarse search, the heat is increased by the amount listed here to confirm.
         # If contact is confirmed, the original coarse dac becomes the contact dac and the heater is backed up to start the fine search
         # The fine search can reset the contact dac if contact is found at a lower dac.
         # This coarse push beyond contact is known to increase burnish risk.  A setting of 0 is safest.
         'Default'      :  2,
         ( 'M10P', 'M11P_BRING_UP') : 1,
         'Makara'       :  0,
         'MakaraPlus': {
            'WRITER_HEATER':  0,
            'READER_HEATER':  1},
         },
      'ReverseZoneOrderOnLastAFH1Retry': {
         # This feature allows for the standard zone order to be reversed in AFH1.  If the ZoneOrder list here is populated, then the feature is enabled.  An empty list disables it.
         # InitialPointsAndOrder and FinalPointsAndOrder allows for unique on the fly regression setttings for this feature.
         # HeaterList lists which heater to enable it on.  ['W','H'] for both
         # NoPESZones is the inclusive zones between which all PES detectors are disabled.
         # This feature will run DETCR only in between the zones specified allowing for a higher start dac for the PES based detectors... which generally will reclaim unstable heads
         # This feature needs to be combined with disabling AGC detectors on the final retry in order to be effective
         'Default'   :  {'ZoneOrder': [],'InitialPointsAndOrder': 0x0502, 'FinalPointsAndOrder': 0x0603 ,'HeaterList': ['W','R'], 'NoPesZones': (12,48)},
         ( 'M10P', 'M11P_BRING_UP') : {'ZoneOrder': [],'InitialPointsAndOrder': 0x0502, 'FinalPointsAndOrder': 0x0603 ,'HeaterList': ['W','R'], 'NoPesZones': (30,120)},
         'MakaraPlus':  {'URHO': {'ZoneOrder': [74,165,94,115,191,53,216,33,232,16,249,0],'InitialPointsAndOrder': 0x0502, 'FinalPointsAndOrder': 0x0603 ,'HeaterList': ['W'], 'NoPesZones': (74,116)},
                         'HWY' : {'ZoneOrder': [],'InitialPointsAndOrder': 0x0502, 'FinalPointsAndOrder': 0x0603 ,'HeaterList': ['W','R'], 'NoPesZones': (12,48)},
                         'TDK' : {'ZoneOrder': [],'InitialPointsAndOrder': 0x0502, 'FinalPointsAndOrder': 0x0603 ,'HeaterList': ['W','R'], 'NoPesZones': (12,48)}}},
      'ShutOffHighFreqDuringGlobalRetries' : {
         # Shuts off everything above 1kHz in PES detectors during final global retry...
         # This is dangerous and should be avoided if at all possible
         'Default'                           : 0,
         'GrenadaBP2'                        : 1,
         ( 'PharaohOasis', 'HepburnOasis' )  : 1,
         'MakaraPlus'                        : {'WRITER_HEATER':  0,'READER_HEATER':  1}
         },
      'EnableClosedLoopDetcrOnlyWhenHighFreqIsDisabled' : {
         # A one here will turn closed loop detcr on if high frequency is disabled
         # as a result of enabling the above switch 'ShutOffHighFreqDuringGlobalRetries'
         'Default'      :  0,
         },
      'DisableRunningOffTheRapDuringRetries': {
         #Enter a list of states in which running off the rap will be disabled.  An empty list will disable the feature
         #Enter the retry depth at which running off the rap will be disabled.  A value of 2 will disable running off the rap in the 2nd retry (third attempt)
         'Default'      : {'StateList':[2]   , 'ConsistencyChkRetryDepth': 2, 'StandardRetryDepth': 3},
         'MakaraPlus'   : {'StateList':[2,6], 'ConsistencyChkRetryDepth': 2, 'StandardRetryDepth': 2},
         'Makara'       : {'StateList':[2,6], 'ConsistencyChkRetryDepth': 2, 'StandardRetryDepth': 2}},
      'ShutOffDetectorsDuringFinalRetries' : {
         # Specify the retry count at which to shut off the specified list of detectors under the index 'DisableAtRetryNum'
         # If 'DisableAtRetryNum' = 2, all detectors will run during global retries 0 and 1 and the specified detectors will be disabled in retry 2, 3, and beyond
         # Enter a list of detectors to shut off for each head vendor index.  An empty list [] leaves all detectors active
         # Note: disabling time domain averaged AGC detector 4 will also disable frequency domain averaged AGC detector 2 if its active
         'Default'      :  {'DisableAtRetryNum': 3, 'TDK': [4,5], 'RHO': [4,5], 'URHO': [4,5], 'USAE': [4,5], 'URHOA': [4,5]},
         },
      'IncreaseAGCMinFreqDuringGlobalRetries': {
         # Increases the minimum AGC frequency during global retries
         'Default'      :  0,
         'Makara'       :  1,
         'Tatsu'        :  {'TDK': 0,'URHO': 1},
         'MakaraPlus'   :  1,
         },
      'DeTuneIPD2SensitivityDuringGlobalRetries': {
         # Increases IPD2 integration thresholds during global retries.  Does not affect IPD3
         'Default'      :  0,
         ( 'M10P', 'M11P_BRING_UP')  : 1,
         'Makara'       :  1,
         'Tatsu'        :  {'TDK': 0,'URHO': 1},
         'MakaraPlus'   :  1,
         },
      'RunReaderHeaterWPH' :  {
         # Turns on WPH contact detect on READER_HEATER
         'Default'      :  0,
         },
      'EnableFrequencyDomainAvgAGCDetector' : {
         # Creates frequency domain-averaged AGC Detector SPECTRAL_DETCTOR2 based off detector 4
         # Detector two is also used for LOW SKEW closed-loop DETCR detector.  ** If enabled, the DETCR detector takes precedence **
         'Default'                      :  0,
         'Makara'                       :  1,
         'Tatsu'                        :  {'TDK': 0, 'URHO': 1},
         'MakaraPlus'                   :  1,
         },
      'RunClosedLoopDETCRContactDetector' : {
         # Enables the DETCR detector to declare contact.  When set to 0, DETCR will run open-loop
         # DETCR Late-detect algorithm always runs. Do NOT disable detector 4 in ShutOffDetectorsDuringFinalRetry if DETCR is open loop!!!
         'Default'      :  1,
         'GrenadaBP2'   :  0},
      'RunClosedLoopDETCRInLowSkewZones' : {
         # This enables detector 2 **always as closed loop DETCR** but will only run in specified inclusive zone range
         # This Detector will only run if standard DETCR detector (#3) is configured to run open loop
         # If detector 3 is closed loop, the list input here will be forced to []
         # An empty list [] shuts this detector off.  Order of zones doesn't matter [11,15] = [15,11].
         # When active, this low skew DETCR detector will override EnableFrequencyDomainAvgAGCDetector (see above comments)
         'Default'      :  []},
      'CloseDETCRLoopWhenAGCIsDisabled' : {
         # Enables closed loop DETCR detector 3 to declare contact whenever AGC detectors (4 and if enabled, 2) are disabled.
         # If RunClosedLoopDETCRContactDetector = 1, this setting has no effect (since DETCR is already closed loop)
         'Default'      :  0},
      'EnableCurveFitDuringTCSCal':{
         'WRITER_HEATER':{
            # Note: if FAFH is enabled, the curve fit will be automatically enabled during AFH3 and 4 on the WRITER_HEATER
            'Default'       :   0},
         'READER_HEATER':{
            'Default'       :   0}},
      'RunReaderHeaterOffPreheatClrInAFH1':{
         'Default'                  : {'TDK': 0,'HWY': 0,'RHO':1,'URHO': 1,'USAE': 1,'URHOA': 1},
         'Makara'                   : 0,
         ( 'MakaraPlus','Tatsu' )   : 1},
      'AGCDetectorZones'      :{
         # Specifies an inclusive range of zones in which the AGC detector will be enabled -- (8,20) will run AGC in zones 8-20
         'Default'                                       : {'17Zone': (13,51), '60Zone': (13,51), '250Zone': (52,212)},
         'AstorMule'                                     : {'TDK': (52,212),'HWY': (52,212),'RHO':(52,212),'URHO': (52,212),'USAE': (52,212),'URHOA': (52,212)},
         ( 'M10P', 'M11P_BRING_UP' )                     : {'TDK': (40,100),'HWY': (40,100),'RHO':(40,100),'URHO': (40,100),'USAE': (40,100),'URHOA': (40,100)},
         ( 'PharaohOasis', 'HepburnOasis','GrenadaBP2' ) : (12,42),
         },
      'IPDVersionToExecute':{
         # first entry is used beyond first global retry, second is first 2 attempts
         # (3,2) will use IPD2 on the first 2 global retries and IPD3 on the third and beyond
         'WRITER_HEATER':{
            'Default'      : (3,2)},
         'READER_HEATER':{
            'Default'      : {'TDK': (3,3), 'HWY': (3,3), 'RHO':(3,2),'URHO': (3,2),'USAE': (3,2),'URHOA': (3,2)}}
         },
      'AFH1_WriteTriplet':{
         # This input determines the write triplet applied during aFH1 for the WRITER_HEATER
         # it should be chosen to be as close as possible to the average AFH2 pick
         # (-1,-1,-1) will use the default RAP triplet
         ( 'PharaohOasis', 'HepburnOasis') : (-1, -1, -1),
         ( 'AstorMule', 'M10P', 'M11P_BRING_UP' )            : {'TDK': (-1,-1,-1), 'HWY': (-1,-1,-1), 'RHO':(-1,-1,-1),'URHO': (-1,-1,-1),'USAE': (-1,-1,-1), 'URHOA': (-1,-1,-1)},
         'Crawford'                        : {'TDK': ( 7, 6, 7), 'RHO':(-1,-1,-1), 'URHO': ( 7, 4, 6)},
         'GrenadaBP2'                      : (6,4,10),
         'Lamarr'                          : {'TDK': (11, 8, 7), 'URHO': ( 7, 3, 7)},
         'Makara'                          : ( 4, 6,11),
         'Tatsu'                           : (82,2,13),
         'MakaraPlus'                      : {'TI5552':  {'TDK': (10, 2, 7),  'HWY': (7, 4, 6),   'URHO': (7, 3, 7)},
                                              'LSI5230': {'TDK': (10, 2, 7),  'HWY': (7, 4, 6),   'URHO': (7, 4, 6)},
                                              'LSI5830': {'TDK': (86, 3, 13), 'HWY': (92, 8, 13), 'URHO': (76, 4, 13)}},
         },
      'OTFRegressionOrder':{
         # This determines the number of points (MSB) needed to enable the on the fly curve fit of a given order (LSB)
         # The initial values are in effect as soon as the initial number of points is reached.  The remain in effect
         # until the final number of points is reached.
         'InitialPointsAndOrder':{
            'AstorMule'                            : {'TDK': 0x0502, 'HWY': 0x0502, 'RHO': 0x0401, 'URHO': 0x0401, 'USAE': 0x0401, 'URHOA': 0x0401},
            ( 'M10P', 'M11P_BRING_UP' )            : {'TDK': 0x0502, 'HWY': 0x0502, 'RHO': 0x0402, 'URHO': 0x0402, 'USAE': 0x0402, 'URHOA': 0x0402},
            ('Crawford','Lamarr')                  : {'TDK': 0x0502, 'RHO': 0x0401, 'URHO': 0x0401},
            'Default'                              : 0x0401,
            'GrenadaBP2'                          : {'Default': 0x0401, 'USAE': 0x0402},
            'MakaraPlus'               : {'TDK': 0x0402, 'HWY': 0x0402, 'URHO': 0x0401},
            'Tatsu'              : {'TDK': 0x0402, 'URHO': 0x0401}},
         'FinalPointsAndOrder':{
            'Default'      : 0x0603,
            ('AstorMule', 'M10P', 'M11P_BRING_UP', 'Crawford','Lamarr')     : {'TDK': 0x0804, 'HWY': 0x0804, 'RHO': 0x0603, 'URHO': 0x0603, 'URHOA': 0x0603}}
         },
      'DiscardAndFinalRegressionOrder':{
         # The first entry determines the polynomial order used during the discard routine on the final curve fit.
         # The second entery determines the poly order used during the final curve fit [discard,final]
         'Default'                           : [3,4],
         ( 'M10P', 'M11P_BRING_UP' )         : [2,3],
         ( 'MakaraPlus','Tatsu','Makara' )   : [4,4]},
      'MovingBackoff':{
         # First entry is the moving backoff in dac between reference and stressed heat.
         # Second entry is the dynamic threshold lag in dac
         'READER_HEATER':{
            'Default'      : [60,20],
            'MakaraPlus'   : [60,40],
            'Lamarr'       : {'TDK': [20,12], 'URHO': [60,20]}},
         'WRITER_HEATER':{
            'Default'      : [40,12],
            'MakaraPlus'   : [40,24],
            'Lamarr'       : {'TDK': [20,12],'URHO': [40,12]}}},
      'DebugOutputMode':{
         # Set to 'Production' to reduce size of REVS_IN_CONTACT table as well as only dump the combo table on a retry
         # Set to 'Engineering' to dump combo table
         'Default'       :    'Engineering',
         'Lamarr'        :    'Production'},
      }

   detcrSetup={
      # Determines preamp setup for DETCR detector.  BiasDac sets the DETCR bias.  TargetFaultCount determines the target number of faults
      # per rev when finding the noise floor at each heater dac.  ConfidenceLevel is determines the certainty required when calculating the
      # prediction interval used to normalize the data: (0:95%, 1:99%, 2:99.5, 3:99.8, 4:99.9, 5:99.98%).  MinPredStdev is the minimum allowed
      # stdev used when calculating the prediction interval scaled by 100: 50=0.5 (unit is Vth dac)
      # Filter sets [HP,LP] filter options
      'PreampAndIPDSetup': {
         'Default':{
            'BiasDac'         : {'WRITER_HEATER': {'TDK': 22, 'Default': 20},'READER_HEATER':20},
            'Filter'          : [0,2],
            'TargetFaultCount': 30,
            'ConfidenceLevel' : {'WRITER_HEATER': {'TDK': 1, 'Default': 4 }, 'READER_HEATER':4},
            'MinPredStdev'    : {'WRITER_HEATER': {'TDK': 25,'Default': 50}, 'READER_HEATER':50},
            'BlnkHtrChange'   : {'TI5552': 2, 'LSI5230': 0, 'LSI5231': 0},
            'BlnkModeChange'  : {'TI5552': 3, 'LSI5230': 4, 'LSI5231': 4}},
         'GrenadaBP2':{
            'BiasDac'         : 20,
            'Filter'          : [0,2],
            'TargetFaultCount': 30,
            'ConfidenceLevel' : 4,
            'MinPredStdev'    : 50},
         ( 'MakaraPlus', 'Tatsu','AstorMule', 'M10P', 'M11P_BRING_UP' ) :{
            'BiasDac'         : {None: 20, 'TI5552': 20, 'LSI5230': 20,'LSI5830': 37,'AVAGO5831': 37,'TI7551': 37},
            'Filter'          : [0,2],
            'TargetFaultCount': 30,
            'ConfidenceLevel' : 2,
            'MinPredStdev'    : 25,
            'BlnkHtrChange'   : {'TI5552': 2, 'LSI5230': 0, 'LSI5830': 0, 'AVAGO5831': 0, 'TI7551': 0},
            'BlnkModeChange'  : {'TI5552': 3, 'LSI5230': 4, 'LSI5830': 4, 'AVAGO5831': 4, 'TI7551': 4}},
         ( 'PharaohOasis', 'HepburnOasis' ):{
            'BiasDac'         : 20,
            'Filter'          : [0,2],
            'TargetFaultCount': 30,
            'ConfidenceLevel' : 4,
            'MinPredStdev'    : 50,
            'BlnkHtrChange'   : {'TI5551': 2, 'LSI2935': 0},
            'BlnkModeChange'  : {'TI5551': 3, 'LSI2935': 4}},
         }
      }

   baseIPD2Prm_135 = {
      'test_num':135,
      'prm_name':'baseIPD2Prm_135',
      'timeout':40000,

      'HEAD_RANGE'                     : 0x0101,          # heads to test
      'ZONE_POSITION'                  : 100,            # Controls where within the zone to test ( 100 = 50% )
      'INITIAL_DELAY'                  : 30,           # ms Delay after initial contact
      'RETEST_DELAY'                   : 100,           # ms Delay after retry contact is tripped
      'MAX_BASELINE_DAC'               : 20,             # max baseline dac for dynamic threshold
      'PATTERN_IDX'                    : -1,             # write pattern -1: random
      'LO_RAMP_CONT_RANGE'             : (-1, 0),            # Never refresh the IPD stats every
      'BASELINE_REVS'                  : 0x0508,
      'CONTACT_VERIFY'                 : 0x0201,          # Retry verifies, initial verifies
      'DEBUG_PRINT'                    : 0x2011,          # Controls debug output
      'GAIN'                           : 7,
      # the following parameters have values that are calculated based on the limit dictionaries above.
      # these values are initialzed to -999
      'DAC_RANGE'                      : [-999,-999,-999],
      'CONTACT_LIMITS'                 : [-999, 0x1104, -999, -999, -160, 160, -999],
      'CURVE_FIT2'                     : [-999,-999,-999,5, -999, -999, -999, 0 ],
      'HEATER'                         : [-999, -999],  # ( [StartDac,EndDac], [FineStep,CoarseStep] )
      'READ_HEAT'                      : -999,            # Maximum Dac for HeatOnly measurement if "CWORD1_RUN_WPH_AND_HO" is set
   }
   if benchMode == 0:
      if getattr(testSwitch, 'KAHUNA', 0) or getattr(testSwitch, 'KAHUNAR', 0):
         baseIPD2Prm_135['COARSE_CONFIRM_INTERFERENCE'] = 2

   ### DEBUG_PRINT ###
   if GetParameter(SearchOptions,'DebugOutputMode',programName,[heaterElement,headType]) == 'Production':
      baseIPD2Prm_135['DEBUG_PRINT'] =  0xA039
      if  benchMode ==0:
         if testSwitch.extern.FE_0262706_357263_T135_EXTRA_GLOBAL_DISPLAY_OPTIONS :
            baseIPD2Prm_135['DEBUG_PRINT_1'] =  0x0001

   ### MOVING BACKOFF ###
   if programName in SearchOptions['MovingBackoff'][heaterElement]:
      programIndex = programName
   else:
      programIndex = 'Default'

   baseIPD2Prm_135['MOVING_BACKOFF'] = 0xFF00 + GetParameter(SearchOptions,'MovingBackoff',programIndex,[heaterElement,headType])[0]
   baseIPD2Prm_135['DYNAMIC_THRESH_BACKOFF']  = GetParameter(SearchOptions,'MovingBackoff',programIndex,[heaterElement,headType])[1]

   ### COARSE_CONFIRM_INTERFERENCE ###
   baseIPD2Prm_135['COARSE_CONFIRM_INTERFERENCE'] = GetParameter(SearchOptions,'CoarseConfirmInterferenceInDac',programName,[heaterElement,headType])

   ###  TEST_LIMITS_5   ### Added by SHD to incorporate States
   if (AFH_State == 1 and GetParameter(SearchOptions,'ReverseZoneOrderOnLastAFH1Retry',programName,[heaterElement,headType,'ZoneOrder']) and (heaterElement[0] in GetParameter(SearchOptions,'ReverseZoneOrderOnLastAFH1Retry',programName,[heaterElement,headType,'HeaterList'])) and (intHeadRetryCntr == 3) ):
      ReversedOrderRun = True
      InitialOrder = GetParameter(SearchOptions,'ReverseZoneOrderOnLastAFH1Retry',programName,[heaterElement,headType,'InitialPointsAndOrder'])
      FinalOrder   = GetParameter(SearchOptions,'ReverseZoneOrderOnLastAFH1Retry',programName,[heaterElement,headType,'FinalPointsAndOrder'])
   else:
      ReversedOrderRun = False
      InitialOrder = GetParameter(SearchOptions,'OTFRegressionOrder',programName,[heaterElement,headType,'InitialPointsAndOrder'])
      FinalOrder   = GetParameter(SearchOptions,'OTFRegressionOrder',programName,[heaterElement,headType,'FinalPointsAndOrder'])


   if AFH_State in [1]:
      baseIPD2Prm_135['TEST_LIMITS_5'] = [ InitialOrder, FinalOrder, -999, 0, 0, ]       # (Low points/Low order, High points/High order, Extrapolation limit,  Not used, Not used) SHD changed param 2 from 0503 to 0603
   else:
      baseIPD2Prm_135['TEST_LIMITS_5'] = [ 0xFF01, 0xFF03, -999, 0, 0, ]


   ## Detcr Setup ###
   baseIPD2Prm_135["TEST_LIMITS_3RD_10"]  = [ -999, #MSB=[Threshold range, gain], LSB=[filter, event counter]     [upper nibble, lower nibble]
                                              -999, #MSB= bias, LSB=target fault count
                                              0x0002, #Flags, bit0=disable u-actuator, bit1=calibrate threshold
                                              -999, #MSB=confidence level (0:95%, 1:99%, 2:99.5, 3:99.8, 4:99.9, 5:99.98%), LSB=maximum range of dacs to fit
                                              0x0603, #MSB=regression lag in dac, LSB=minimum number of unique Vth points before curve fit
                                              -999, #LSB=minimum regression prediction stdev divided by 100 0x32=0.5
                                              0, 0, 0, 0 ] #not used

   baseIPD2Prm_135["TEST_LIMITS_3RD_10"][0] = (0x17 << 8) + (GetParameter(detcrSetup,'PreampAndIPDSetup',programName,[heaterElement,headType,'Filter',(str(numZones)+'Zone')])[1] <<4) + 0x0003
   baseIPD2Prm_135["TEST_LIMITS_3RD_10"][1] = (GetParameter(detcrSetup,'PreampAndIPDSetup',programName,[heaterElement,headType,'BiasDac',preampType,(str(numZones)+'Zone')]) << 8) + GetParameter(detcrSetup,'PreampAndIPDSetup',programName,[heaterElement,headType,'TargetFaultCount',(str(numZones)+'Zone')])
   baseIPD2Prm_135["TEST_LIMITS_3RD_10"][3] = (GetParameter(detcrSetup,'PreampAndIPDSetup',programName,[heaterElement,headType,'ConfidenceLevel',(str(numZones)+'Zone')]) << 8) + 0xFF
   baseIPD2Prm_135["TEST_LIMITS_3RD_10"][5] =  GetParameter(detcrSetup,'PreampAndIPDSetup',programName,[heaterElement,headType,'MinPredStdev',(str(numZones)+'Zone')])
   baseIPD2Prm_135["TEST_LIMITS_3RD_10"][6] =  GetParameter(detcrSetup,'PreampAndIPDSetup',programName,[heaterElement,headType,'Filter',(str(numZones)+'Zone')])[0]
   if preampType:
      baseIPD2Prm_135["TEST_LIMITS_3RD_10"][7] =  ((GetParameter(detcrSetup,'PreampAndIPDSetup',programName,[heaterElement,headType,'BlnkModeChange',preampType,(str(numZones)+'Zone')]) & 0xF) <<4) | (GetParameter(detcrSetup,'PreampAndIPDSetup',programName,[heaterElement,headType,'BlnkHtrChange',preampType,(str(numZones)+'Zone')]) & 0xF)


   ###  CWORD1 & 2  ###

   if AFH_State in GetParameter(SearchOptions,'UpdateRapClearanceStateIndexList',programName,[heaterElement,headType]):
      baseIPD2Prm_135["CWORD1"]        = 0x6F16
      baseIPD2Prm_135["CWORD2"]        = 0x01C5
      if AFH_State ==1:
         baseIPD2Prm_135["CWORD2"]     = 0x00C5
   else:
      baseIPD2Prm_135["CWORD1"]        = 0x4F16
      baseIPD2Prm_135["CWORD2"]        = 0x0180


   if (AFH_State in [3,4,7]) and ( (enableFAFH == 1 and heaterElement == 'WRITER_HEATER') or (GetParameter(SearchOptions,'EnableCurveFitDuringTCSCal',programName,[heaterElement,headType]) == 1) ):
      baseIPD2Prm_135["CWORD2"]        |= 0x0040 #turn on dual curve fit
      baseIPD2Prm_135["CWORD1"]        |= 0x2000 #turn on final curve fit
   if (GetParameter(SearchOptions,'RunReaderHeaterOffPreheatClrInAFH1',programName,[heaterElement,headType,zones]) == 1) and (AFH_State == 1) and (heaterElement == 'READER_HEATER') and ( (iConsistencyCheckRetry < 2) and (intHeadRetryCntr < 2)):
      baseIPD2Prm_135["CWORD2"]        |= 0x0100 #run off rap in initial zones
      baseIPD2Prm_135['TEST_LIMITS_5'][0] = 0xFF01 #make all zones initial zones
      baseIPD2Prm_135['TEST_LIMITS_5'][1] = 0xFF03 #make all zones initial zones


   if AFH_State in ( GetParameter(SearchOptions,'DisableRunningOffTheRapDuringRetries',programName,[heaterElement,headType,'StateList']) ):
      if ( (iConsistencyCheckRetry >= GetParameter(SearchOptions,'DisableRunningOffTheRapDuringRetries',programName,[heaterElement,headType,'ConsistencyChkRetryDepth']) ) or
      (     intHeadRetryCntr       >= GetParameter(SearchOptions,'DisableRunningOffTheRapDuringRetries',programName,[heaterElement,headType,'StandardRetryDepth'      ]) )      ):
         baseIPD2Prm_135["CWORD2"]        &= ~0x0100 #shut off running off the rap
         baseIPD2Prm_135['TEST_LIMITS_5'] = [ InitialOrder, FinalOrder, -999, 0, 0, ]

   if benchMode == 0:
      baseIPD2Prm_135["CWORD2"]        &= 0xFF7F # disable bit 0x80

   ###  DAC_RANGE  ###
   if (baseIPD2Prm_135['CWORD2'] & 0x0100) == 0:
      DacRangeIndex = 'OTF_CurveFit'
   else:
      DacRangeIndex = 'RapBased'


   baseIPD2Prm_135['DAC_RANGE'][0]     =   GetParameter(SearchLimits,'DacRangeLimits',programName,['BackOffFromExpectedContact'      ,heaterElement,headType,DacRangeIndex])
   baseIPD2Prm_135['DAC_RANGE'][1]     = ((GetParameter(SearchLimits,'DacRangeLimits',programName,['MaximumPushBeyondExpectedContact',heaterElement,headType,DacRangeIndex])[1] << 8) & 0xFF00) + \
                                         ((GetParameter(SearchLimits,'DacRangeLimits',programName,['MaximumPushBeyondExpectedContact',heaterElement,headType,DacRangeIndex])[0]     ) & 0x00FF)
   baseIPD2Prm_135['DAC_RANGE'][2]     = ((GetParameter(SearchLimits,'DacRangeLimits',programName,['MinimumPushBeyondExpectedContact',heaterElement,headType,DacRangeIndex])[1] << 8) & 0xFF00) + \
                                         ((GetParameter(SearchLimits,'DacRangeLimits',programName,['MinimumPushBeyondExpectedContact',heaterElement,headType,DacRangeIndex])[0]     ) & 0x00FF)

   ###  DETECTOR_BIT_MASK/DETECTOR_ZONE_RANGE  ###
   AllZones = numZones << 8
   if ReversedOrderRun:
      MSBPesZone =  min( GetParameter(SearchOptions,'ReverseZoneOrderOnLastAFH1Retry',programName,[heaterElement,headType,'NoPesZones']) )
      LSBPesZone =  max( GetParameter(SearchOptions,'ReverseZoneOrderOnLastAFH1Retry',programName,[heaterElement,headType,'NoPesZones']) )
      if numZones > 60:
         #before 250 support was enabled, shutting off a detector over a range of zones was achieved by making the MSB smaller than the LSB
         PESZoneRange = (MSBPesZone << 8) | LSBPesZone
      else:
         #before 250 support was enabled, shutting off a detector over a range of zones was achieved by using negative zones
         PESZoneRange = ( (-MSBPesZone << 8) & 0xFF00) | (-LSBPesZone & 0x00FF)
   else:
      PESZoneRange = AllZones

   disableLowSkewDETCRDetector = False
   UpperAGCZone=(GetParameter(SearchOptions,'AGCDetectorZones',programName,[heaterElement,headType,zones ])[0])
   LowerAGCZone=(GetParameter(SearchOptions,'AGCDetectorZones',programName,[heaterElement,headType,zones ])[1])
   AGCZoneRange = (UpperAGCZone << 8 ) | LowerAGCZone
   if GetParameter(SearchOptions,'RunClosedLoopDETCRContactDetector',programName,[heaterElement,headType]) == 1 or GetParameter(SearchOptions,'RunClosedLoopDETCRInLowSkewZones',programName,[heaterElement,headType]) == []:
      #force no low skew detcr detector if closed loop detcr is already enabled
      disableLowSkewDETCRDetector = True
   else:
      disableLowSkewDETCRDetector = False
   if disableLowSkewDETCRDetector :
      baseIPD2Prm_135["DETECTOR_ZONE_RANGE"] = (PESZoneRange, AGCZoneRange, AllZones, AGCZoneRange,PESZoneRange,PESZoneRange)
   else:
      UpperLowSkewDetcrZone = GetParameter(SearchOptions,'RunClosedLoopDETCRInLowSkewZones',programName,[heaterElement,headType])[0]
      LowerLowSkewDetcrZone = GetParameter(SearchOptions,'RunClosedLoopDETCRInLowSkewZones',programName,[heaterElement,headType])[1]
      LowSkewDetcrZoneRange = (UpperLowSkewDetcrZone << 8) + LowerLowSkewDetcrZone
      baseIPD2Prm_135["DETECTOR_ZONE_RANGE"] = (PESZoneRange, LowSkewDetcrZoneRange, AllZones, AGCZoneRange,PESZoneRange,PESZoneRange)

   ### WRITE_TRIPLET  ####
   CWRD2=baseIPD2Prm_135['CWORD2']
   AFH1Triplet     = GetParameter(SearchOptions,'AFH1_WriteTriplet',programName,[heaterElement,headType,zones,preampType])
   OpenLoopTriplet = GetParameter(SearchOptions,'WriteTripletForOpenLoopStates',programName,[heaterElement,headType])

   if ( (isDriveDualHeater == 1) and (GetParameter(SearchOptions,'RunReaderHeaterWPH',programName,[heaterElement,headType]) == 0) and (heaterElement == "READER_HEATER") ):
      baseIPD2Prm_135['WRITE_TRIPLET']    =  (0, 0, 0)      # write triplet used during contact detect (WCA,OSA,OSW)
      baseIPD2Prm_135["CWORD1"]           &= ~0x0400        # shut off bit that runs WPH and HO
   elif ( (isDriveDualHeater == 1) and (heaterElement == "READER_HEATER") ):
      baseIPD2Prm_135['WRITE_TRIPLET']    =  (6, 6, 6)      # set fixed high power write triplet for reader heater shd changed to 6,6,6 from 12,12,12
   elif ( (AFH_State==1) and (heaterElement == "WRITER_HEATER") ):
      baseIPD2Prm_135['WRITE_TRIPLET']    =  AFH1Triplet
   elif (not(CWRD2 & 0x0001) and (heaterElement == "WRITER_HEATER") and (len(OpenLoopTriplet) ==3)):
      if list(AFH1Triplet) == [-1,-1,-1]:
         baseIPD2Prm_135['WRITE_TRIPLET'] = OpenLoopTriplet
      else:
         baseIPD2Prm_135['WRITE_TRIPLET'] = AFH1Triplet
   else:
      baseIPD2Prm_135['WRITE_TRIPLET']    =  (-1, -1, -1)   # write triplet used during contact detect (WCA,OSA,OSW)

   if not testSwitch.FE_0274637_496738_P_DC_DETCR_DSA_CONTACT_DETECTION:
      ### MR BIAS ADJUSTMENT ###
      if (iConsistencyCheckRetry > 0) or (intHeadRetryCntr > 0):
         baseIPD2Prm_135["MR_BIAS_OFFSET"]      = 0  # turn MR bias down to minimum during all retries

   ################################################################################################################################################################################################################################################
   IntegrationLimits=0x735F   #default sensitivity
   IPDIndex = 1
   if intHeadRetryCntr ==1 :
      if ( (GetParameter(SearchOptions,'DeTuneIPD2SensitivityDuringGlobalRetries',programName,[heaterElement,headType]) == 1) and (GetParameter(SearchOptions,'IPDVersionToExecute',programName,[heaterElement,headType])[IPDIndex] == 2) ):
         #only detune IPD2... IPD3 is not detuned
         IntegrationLimits=0x7D5F
   elif intHeadRetryCntr >=2 :
      IPDIndex = 0
      if ( (GetParameter(SearchOptions,'DeTuneIPD2SensitivityDuringGlobalRetries',programName,[heaterElement,headType]) == 1) and (GetParameter(SearchOptions,'IPDVersionToExecute',programName,[heaterElement,headType])[IPDIndex] == 2) ):
         #only detune IPD2... IPD3 is not detuned
         IntegrationLimits=0x7D5F


   if GetParameter(SearchOptions,'IPDVersionToExecute',programName,[heaterElement,headType])[IPDIndex] == 3:
      SpectralMask=0x1421
   else:
      SpectralMask=0x0431
   baseIPD2Prm_135['SPECTRAL_DETECTOR1']  = [ 0x00C9, 0x0001, 0x0E1E, 650, 1, SpectralMask, 0x1, 0x1, IntegrationLimits, -1]  ## TDA PES ##
   if not disableLowSkewDETCRDetector:
      baseIPD2Prm_135['SPECTRAL_DETECTOR2']  = [ 0x0889, 0x0001, 0x0F0F, 650, 1, 0x1421, 0x2, 0x1, 0x735F, -1]  ## Low Skew Only DETCR
   #if not testSwitch.FE_0270329_379676_P_DISABLE_SPECTRAL_DETECTOR3:
   baseIPD2Prm_135['SPECTRAL_DETECTOR3']  = [ 0x0889, 0x0001, 0x0F0F, 650, 1, 0x1421, 0x2, 0x1, 0x735F, -1]  ## DETCR
   baseIPD2Prm_135['SPECTRAL_DETECTOR4']  = [ 0x00A9, 0x0001, 0x0E1E, 650, 1, SpectralMask, 0x2008, 0x2, IntegrationLimits, -1]  ## TDA AGC ##
   baseIPD2Prm_135['SPECTRAL_DETECTOR5']  = [ 0x00C9, 0x0001, 0x0E1E, 650, 1, SpectralMask, 0x4, 0x4, IntegrationLimits, -1]  ## LF PES ##
   baseIPD2Prm_135['SPECTRAL_DETECTOR6']  = [ 0x0289, 0x0001, 0x0E1E, 650, 1, SpectralMask, 0x10, 0x1, IntegrationLimits, -1]  ## TDA VCM current ##

   SafeToDisableDETCR = 1
   RetryCountLimit = GetParameter(SearchOptions,'ShutOffDetectorsDuringFinalRetries',programName,[heaterElement,'DisableAtRetryNum',headType]) #
   if (iConsistencyCheckRetry >= RetryCountLimit) or (intHeadRetryCntr >= RetryCountLimit):
      for DetectorNum in range(1,7):
         if ( (('SPECTRAL_DETECTOR' + str(DetectorNum)) in baseIPD2Prm_135) and (DetectorNum in GetParameter(SearchOptions,'ShutOffDetectorsDuringFinalRetries',programName,[heaterElement,headType]) )):
            baseIPD2Prm_135[('SPECTRAL_DETECTOR' + str(DetectorNum))][0] |= 0x0002 #makes detector run open loop
            if (DetectorNum == 4) and (GetParameter(SearchOptions,'CloseDETCRLoopWhenAGCIsDisabled',programName,[heaterElement,headType]) == 1):
               #AGC was just disabled and we need to close detcr loop
               SafeToDisableDETCR = 0
   if ( ( GetParameter(SearchOptions,'EnableFrequencyDomainAvgAGCDetector',programName,[heaterElement,headType]) == 1) and (('SPECTRAL_DETECTOR4') in baseIPD2Prm_135) and (disableLowSkewDETCRDetector) ):
      baseIPD2Prm_135['SPECTRAL_DETECTOR2'] = list(baseIPD2Prm_135['SPECTRAL_DETECTOR4']) #copy detector 4 (TDA AGC) settings into detector 2
      baseIPD2Prm_135['SPECTRAL_DETECTOR2'][5] &= 0xFFF0 #shut off time domain average
      baseIPD2Prm_135['SPECTRAL_DETECTOR2'][5] += 0x0002 #turn on frequency domain average

   if ((GetParameter(SearchOptions,'ShutOffHighFreqDuringGlobalRetries',programName,[heaterElement,headType]) == 1) and (intHeadRetryCntr >= 3)):
      if GetParameter(SearchOptions,'EnableClosedLoopDetcrOnlyWhenHighFreqIsDisabled',programName,[heaterElement,headType]) == 1:
         SafeToDisableDETCR = 0  #We are turning off high frequency so turn on closed loop detcr

   if (  (GetParameter(SearchOptions,'RunClosedLoopDETCRContactDetector',programName,[heaterElement,headType]) == 0) and \
         ( ('SPECTRAL_DETECTOR3') in baseIPD2Prm_135 )                                                               and \
         (SafeToDisableDETCR ==1)):
      baseIPD2Prm_135['SPECTRAL_DETECTOR3'][0] |= 0x0002 #make detecr run open loop

   elif ((SafeToDisableDETCR == 0) and (not disableLowSkewDETCRDetector)):
      #DETCR detector 3 is is running closed loop and Detector 2 is low skew closed loop detcr... don't need low skew DETCR detector
      del baseIPD2Prm_135['SPECTRAL_DETECTOR2']
   for DetectorNum in range(1,7):
      if ( (('SPECTRAL_DETECTOR' + str(DetectorNum)) in baseIPD2Prm_135) and (DetectorNum not in (GetParameter(SearchOptions,'MasterDetectorEnable',programName,[heaterElement,headType])) ) ):
         baseIPD2Prm_135[('SPECTRAL_DETECTOR' + str(DetectorNum))][0] |= 0x0002 #makes detector run open loop


   ################################################################################################################################################################################################################################################


   ###  V3BAR Destroking Parameters  ###

   if ( AFH_State == 25):
      baseIPD2Prm_135["WRITE_TRIPLET"] = ( 0, 0, 0,)           # set to 0 to force main detect to be heater only
      baseIPD2Prm_135["CWORD1"]        = 0x0B02
      baseIPD2Prm_135["CWORD2"]        = 0x0090

   ################################################################################################################################################################################################################################################

   ########################################################################################################################################################################
   #
   #
   #           FAFH params
   #
   #
   ########################################################################################################################################################################

   if enableFAFH == 1:

      FAFH_HOT_MEASUREMENT = 0
      FAFH_COLD_MEASUREMENT = 1

      if AFH_State in [3]:
         baseIPD2Prm_135["CERT_TEMPERATURE"] = FAFH_HOT_MEASUREMENT
      elif AFH_State in [4]:
         baseIPD2Prm_135["CERT_TEMPERATURE"] = FAFH_COLD_MEASUREMENT
      else:
         pass



   ########################################################################################################################################################################
   #
   #
   #           Calculated Parameters
   #
   #
   ########################################################################################################################################################################


   # set limitIndex = 1 meaning to use the "opened-up" parameters in either the case where
   # 1. last head retry
   # or
   # 2. last consistency check retry
   if (iConsistencyCheckRetry >= 3) or (intHeadRetryCntr >= 3):
      limitIndex=1
   else:
      limitIndex=0



   if AFH_State ==1:
      StateIndex=0
   else:
      StateIndex=1

   ###  DUAL_HEATER_CONTROL  ###

   if isDriveDualHeater == 1:
      if heaterElement == "WRITER_HEATER":
         elementType = 0      # 0 = Write  (old traditional path)
      else:
         elementType = 1      # 1 = reader heater (new)
      baseIPD2Prm_135["DUAL_HEATER_CONTROL"]           = ( elementType, 0x0000 )   #SHD for dual heater 1st parameter 0=Write 1=Read heater, 2nd parameter in - active heat value
   else:
      elementType = 0


   ##################################### Final Curve Fit Limits ##################################################
   if AFH_State == 1:
      hirpState='PreHirp'
   else:
      hirpState='PostHirp'


   if isDriveDualHeater == 0:
      baseIPD2Prm_135['CLEARANCE_CONSISTENCY_LIMIT']= \
         ( ((GetParameter(FinalCurveFitLimitsAngstrom,'Max_IDOD_DeltaClr'  ,programName,[heaterElement,headType])[limitIndex]  << 8)          & 0xFF00) +
           ((GetParameter(FinalCurveFitLimitsAngstrom,'Min_IDOD_DeltaClr'  ,programName,[heaterElement,headType])[limitIndex]      )          & 0x00FF    ),
           ( GetParameter(FinalCurveFitLimitsAngstrom,'MaxClrRange'        ,programName,[heaterElement,headType])[limitIndex]                             ),
           ((GetParameter(FinalCurveFitLimitsAngstrom,'MaxConsistencyLimit',programName,[heaterElement,headType,hirpState])[limitIndex] << 8) & 0xFF00) +
           ((GetParameter(FinalCurveFitLimitsAngstrom,'MinConsistencyLimit',programName,[heaterElement,headType,hirpState])[limitIndex]     ) & 0x00FF)   )
   else:
      if ( (heaterElement == "WRITER_HEATER") and (AFH_State ==2) ):
         baseIPD2Prm_135['TRGT_WR_CLEARANCE']= \
            ( ((GetParameter(FinalCurveFitLimitsAngstrom,'MaxRapConsistencyLimit',programName,[heaterElement,headType])[limitIndex] << 8) & 0xFF00) +
              ((GetParameter(FinalCurveFitLimitsAngstrom,'MinRapConsistencyLimit',programName,[heaterElement,headType])[limitIndex]     ) & 0x00FF    ) )
      if ( (heaterElement == "READER_HEATER") and (AFH_State ==2) ):
         baseIPD2Prm_135['TRGT_RD_CLEARANCE']= \
            ( ((GetParameter(FinalCurveFitLimitsAngstrom,'MaxRapConsistencyLimit',programName,[heaterElement,headType])[limitIndex] << 8) & 0xFF00) +
              ((GetParameter(FinalCurveFitLimitsAngstrom,'MinRapConsistencyLimit',programName,[heaterElement,headType])[limitIndex]     ) & 0x00FF    ) )

      baseIPD2Prm_135['CLEARANCE_CONSISTENCY_LIMIT_DH']= \
         [ ((GetParameter(FinalCurveFitLimitsAngstrom,'Max_IDOD_DeltaClr'             ,programName,[heaterElement,headType])[limitIndex] << 8) & 0xFF00) +
           ((GetParameter(FinalCurveFitLimitsAngstrom,'Min_IDOD_DeltaClr'             ,programName,[heaterElement,headType])[limitIndex]     ) & 0x00FF    ),
           ( GetParameter(FinalCurveFitLimitsAngstrom,'MaxClrRange'                   ,programName,[heaterElement,headType])[limitIndex]                           ),
           ((GetParameter(FinalCurveFitLimitsAngstrom,'MaxConsistencyLimit'           ,programName,[heaterElement,headType,hirpState])[limitIndex] << 8) & 0xFF00) +
           ((GetParameter(FinalCurveFitLimitsAngstrom,'MinConsistencyLimit'           ,programName,[heaterElement,headType,hirpState])[limitIndex]     ) &0x00FF),
           ((GetParameter(FinalCurveFitLimitsAngstrom,'MaxCrossHeaterConsistencyLimit',programName,[heaterElement,headType,hirpState])[limitIndex] << 8) & 0xFF00) +
           ((GetParameter(FinalCurveFitLimitsAngstrom,'MinCrossHeaterConsistencyLimit',programName,[heaterElement,headType,hirpState])[limitIndex]     ) &0x00FF)    ]


      if (limitIndex==1) and (AFH_State not in GetParameter(SearchOptions,'UpdateRapClearanceStateIndexList',programName,[heaterElement,headType])):
         # Disable the cross heater consistency check in AFH3 and 4 on the last retry
         baseIPD2Prm_135['CLEARANCE_CONSISTENCY_LIMIT_DH'][3] = ( (127 << 8) & 0xFF00 ) + (-127 & 0x00FF)

   if (benchMode == 0) and (testSwitch.extern.FE_0276401_357263_T135_CALCULATE_AVERAGE_BURNISH):
      if AFH_State in GetParameter(FinalCurveFitLimitsAngstrom,'InterpolatedBurnish',programName,[heaterElement,headType,'StateList']):
         baseIPD2Prm_135['RAP_BURNISH'] = [GetParameter(FinalCurveFitLimitsAngstrom,'InterpolatedBurnish',programName,[heaterElement,headType,'LSL']),
                                           GetParameter(FinalCurveFitLimitsAngstrom,'InterpolatedBurnish',programName,[heaterElement,headType,'USL']) ]

   baseIPD2Prm_135['MAX_MIN_DELTA']= \
      ( ((GetParameter(FinalCurveFitLimitsDAC,'Max_IDOD_DeltaDAC',programName,[heaterElement,headType])[limitIndex] << 8)   & 0xFF00) +
        ((GetParameter(FinalCurveFitLimitsDAC,'Min_IDOD_DeltaDAC',programName,[heaterElement,headType])[limitIndex]     )   & 0x00FF),
        ( GetParameter(FinalCurveFitLimitsDAC,'MaxDACRange',programName,[heaterElement,headType])[limitIndex]           )           )

   baseIPD2Prm_135['ZONE_DAC_DELTA']= \
      ( ( GetParameter(FinalCurveFitLimitsDAC,'ZoneSlopeZones',programName,[heaterElement,headType])                               ),
        ((GetParameter(FinalCurveFitLimitsDAC,'MaxZoneToZoneSlope',programName,[heaterElement,headType])[limitIndex] << 8) & 0xFF00) +
        ((GetParameter(FinalCurveFitLimitsDAC,'MinZoneToZoneSlope',programName,[heaterElement,headType])[limitIndex]     ) & 0x00FF))



   baseIPD2Prm_135['CURVE_FIT2'][0]=GetParameter(SearchOptions,'DiscardAndFinalRegressionOrder',programName,[heaterElement,headType])[0]
   baseIPD2Prm_135['CURVE_FIT2'][1]=GetParameter(SearchOptions,'DiscardAndFinalRegressionOrder',programName,[heaterElement,headType])[1]
   baseIPD2Prm_135['CURVE_FIT2'][2]=GetParameter(FinalCurveFitLimitsDAC,'DeletedResidualDiscardLimit',programName,[heaterElement,headType])[limitIndex]
   baseIPD2Prm_135['CURVE_FIT2'][4]=GetParameter(FinalCurveFitLimitsDAC,'MaxExtrapolationTracks',programName,[heaterElement,headType])
   baseIPD2Prm_135['CURVE_FIT2'][6]=GetParameter(FinalCurveFitLimitsDAC,'MaxPredictionInterval',programName,[heaterElement,headType])[limitIndex]


   ##################################### Contact Search Limits ##################################################
   #


   baseIPD2Prm_135['CONTACT_LIMITS'][0]=(
      (GetParameter(FinalCurveFitLimitsDAC,'MaxSearchInterference',programName,[heaterElement,headType]) << 8) + \
      (GetParameter(FinalCurveFitLimitsDAC,'MinInterpolatedDAC'   ,programName,[heaterElement,headType])[limitIndex] )  )

   baseIPD2Prm_135['CONTACT_LIMITS'][2] = GetParameter(SearchLimits,'MinWICD'           ,programName,[heaterElement,headType])[StateIndex]
   baseIPD2Prm_135['CONTACT_LIMITS'][3] = GetParameter(SearchLimits,'MaxWICD'           ,programName,[heaterElement,headType])[StateIndex]
   baseIPD2Prm_135['CONTACT_LIMITS'][6] = GetParameter(SearchLimits,'MaxZoneToZoneDelta',programName,[heaterElement,headType])[StateIndex]

   baseIPD2Prm_135['TEST_LIMITS_5'][2]   = GetParameter(SearchLimits,'MaxExtrapolationTracks',programName,[heaterElement,headType])
   baseIPD2Prm_135['HEATER'][0]          = (GetParameter(SearchLimits,'GlobalHeaterLimits',programName,[heaterElement,headType])[0] << 8) + \
      GetParameter(SearchLimits,'GlobalHeaterLimits',programName,[heaterElement,headType])[1]
   baseIPD2Prm_135['HEATER'][1]          = GetParameter(SearchLimits,'GlobalHeaterLimits',programName,[heaterElement,headType])[2]
   baseIPD2Prm_135['READ_HEAT']          = GetParameter(SearchLimits,'GlobalHeaterLimits',programName,[heaterElement,headType])[1]
   baseIPD2Prm_135['FINE_SEARCH_BACKUP'] = GetParameter(SearchLimits,'GlobalHeaterLimits',programName,[heaterElement,headType])[3]

   #### OTF Burnish Limits ####
   if AFH_State ==2:
      baseIPD2Prm_135['BURNISH'] = [GetParameter(SearchLimits,'MinOTFBurnishLimitsInAngstrom',programName,[heaterElement,headType])[0],
                                    GetParameter(SearchLimits,'MaxOTFBurnishLimitsInAngstrom',programName,[heaterElement,headType])[0] ]
   elif AFH_State in [3,4,6,7]:
      baseIPD2Prm_135['BURNISH'] = [GetParameter(SearchLimits,'MinOTFBurnishLimitsInAngstrom',programName,[heaterElement,headType])[1],
                                    GetParameter(SearchLimits,'MaxOTFBurnishLimitsInAngstrom',programName,[heaterElement,headType])[1] ]

   ###################################Revs_by_zone and Zone_Order ########################################
   if (AFH_State in [3,4]) and ( (enableFAFH == 1 and heaterElement == 'WRITER_HEATER') or (GetParameter(SearchOptions,'EnableCurveFitDuringTCSCal',programName,[heaterElement,headType]) == 1) ):
      # force zone list in AFH3 and 4 to match AFH2 whenever FAFH is running or when the curve fit is enabled in AFH 3 and 4
      zoneList=list( GetParameter(SearchLimits,'ZoneOrder',programName,[heaterElement,headType,zones ])[2] )
   else:
      if ReversedOrderRun:
         zoneList = GetParameter(SearchOptions,'ReverseZoneOrderOnLastAFH1Retry',programName,[heaterElement,headType,'ZoneOrder'])
      else:
         zoneList=list( GetParameter(SearchLimits,'ZoneOrder',programName,[heaterElement,headType,zones, AFH_State ]))#[AFH_State] )
   revsList=[]

   #note: Forcing the minimum (maximum) zone into the MSB (LSB) will now ensure you get what you ask for regardless of whether the SF3 bugfix to address this logic flaw is in or not:
   baseIPD2Prm_135["BLOCK"] = ((min( GetParameter(FastIOSetup,'lowSkewZones',programName,[heaterElement,headType,(str(numZones) + 'Zone')]) ) << 8) + (max( GetParameter(FastIOSetup,'lowSkewZones',programName,[heaterElement,headType,(str(numZones) + 'Zone')]) )),
                               (GetParameter(FastIOSetup,'FastIORevs',programName,[heaterElement,headType,'LowSkew','InternalRetry']) << 8) + (GetParameter(FastIOSetup,'FastIORevs',programName,[heaterElement,headType,'LowSkew','Initial'])),
                               (GetParameter(FastIOSetup,'FastIORevs',programName,[heaterElement,headType,'HighSkew','InternalRetry']) << 8) + (GetParameter(FastIOSetup,'FastIORevs',programName,[heaterElement,headType,'HighSkew','Initial'])) )


   for ii in range(32-len(zoneList)) :
      zoneList.append(-1)
   baseIPD2Prm_135['ZONE_ORDER']=zoneList

   ##################################### FastIO Parameters  ##################################################
   if headType in ['RHO','URHO','USAE', 'URHOA']:
      AGCTransient =  12             #percentage of rev to discard from AGC to avoid heat transient effect
   elif headType in ['TDK', 'HWY']:
      AGCTransient =  12            #percentage of rev to discard from AGC to avoid heat transient effect

   WriteLength      =  90                                               #percentage of the rev to write/heat

   fastIO_B          = int(SpokesPerRev*WriteLength/100.0)              #set fastIO segment B to x percent of a rev
   AGCEndSpoke       = int(fastIO_B)                                    #AGC detectors avoid spacing transient
   fastIO_E          = SpokesPerRev - fastIO_B                          #set fastIO segment C to complete rev when added to B
   #### optimize DFT length for PES
   PESDftN           = int(SpokesPerRev)                                     #maximum DftN

   #### now margin for DFT speed

   while PESDftN > 0:
      if PESDftN % 8 == 0:  # fast DFT is most efficient for lengths that are multiples of 8
         break
      PESDftN = PESDftN - 1

   #### optimize DFT length for AGC
   AGCDftN           = fastIO_B - int(AGCTransient/100.0*SpokesPerRev)  #maximum AGCDftN --

   ### now margin for dft speed
   while AGCDftN > 0:
      if AGCDftN % 8 == 0:  # fast DFT is most efficient for lengths that are multiples of 8
         break
      AGCDftN = AGCDftN - 1

   Nyquist           = RPM/120*SpokesPerRev
   PESFr             = RPM/60*SpokesPerRev/PESDftN
   AGCFr             = RPM/60*SpokesPerRev/AGCDftN
   LFPESFr           = RPM/60*SpokesPerRev/(SpokesPerRev-fastIO_B)

   baseIPD2Prm_135['B_WR_NUM_WEDGES'     ] = fastIO_B
   baseIPD2Prm_135['E_POST_RD_NUM_WEDGES'] = fastIO_E

   #if headType in ['RHO']:
   #   MinAGCBin=10
   #else:
   MinAGCFreq=0
   EndFreq = int(Nyquist + PESFr)

   if (intHeadRetryCntr > 0):#purposefully only do this on the intHeadRetryCntr and not on consistency check retries for reduced risk
      if (( GetParameter(SearchOptions,'ShutOffHighFreqDuringGlobalRetries',programName,[heaterElement,headType]) == 1) and (intHeadRetryCntr >= 3)):
         #only shut off HF on the last attempt
         EndFreq = int(10 * PESFr)
      if ( GetParameter(SearchOptions,'IncreaseAGCMinFreqDuringGlobalRetries',programName,[heaterElement,headType]) == 1):
         if headType in ['RHO','URHO','USAE', 'URHOA']:
            MinAGCFreq=2200
         else:
            MinAGCFreq=1200

   MinAGCFreqWithBLJ=MinAGCFreq+8000 #min AGC bin when a baseline jump is detected


   baseIPD2Prm_135['M0_FREQ_RANGE'       ] = (0,EndFreq)   #Full spectra PES Freq Range                           0x1
   baseIPD2Prm_135['M2_FREQ_RANGE'       ] = (0,EndFreq)   #Full spectra LF PES Freq Range                        0x4
   baseIPD2Prm_135['M3_FREQ_RANGE'       ] = (MinAGCFreq,int(Nyquist + AGCFr))   #AGC Freq Range sans LF          0x8
   baseIPD2Prm_135['M4_FREQ_RANGE'       ] = (0, EndFreq)   #Full spectra VCM Freq Range                          0x10
   baseIPD2Prm_135['M5_FREQ_RANGE'       ] = (MinAGCFreqWithBLJ,int(Nyquist + AGCFr))   #AGC when BLJ is detected 0x20

   baseIPD2Prm_135['SECTOR_RANGE1'       ] = (SpokesPerRev - PESDftN,SpokesPerRev)  #HF PES
   baseIPD2Prm_135['SECTOR_RANGE2'       ] = (AGCEndSpoke-AGCDftN,AGCEndSpoke)  #AGC
   baseIPD2Prm_135['SECTOR_RANGE3'       ] = (fastIO_B , SpokesPerRev)  #LF PES

   #For DC DETCR
   baseIPD2Prm_135['SPECTRAL_DETECTOR1'] = [201, 0x400, 3614, 650, 1, 1073, 1, 1, 29535, -1]
   baseIPD2Prm_135['CONTACT_VERIFY'] = 0x303
   
   # modify for extended tracing feature
   baseIPD2Prm_135['B_WR_NUM_WEDGES'] = SpokesPerRev                                            # use full wedge
   baseIPD2Prm_135['CWORD2'] |= 0x8
   if (AFH_State in [2,3,4]):
      baseIPD2Prm_135['CWORD2'] |= 0x8000
                                            # allow more than 2 revs
   #baseIPD2Prm_135['DC_DETCR'] = [32913, 4376, 5, 256, 7, 5, 3, 55, 0, 0, 200]                 # change HFACH frequency for out-of-phase motion
   baseIPD2Prm_135['DC_DETCR'] = [32913, RPM + RPM/120, 5, 256, 7, 5, 3, 50, 0, 0, 200]         # change HFACH frequency for out-of-phase motion
   
   baseIPD2Prm_135['DETCR_DETECTOR'] = [113, 1800, 0x107, 220, 3, -10, 0, 100, 23120, 21792]     # change dRdP criteria
   baseIPD2Prm_135['E_POST_RD_NUM_WEDGES'] = SpokesPerRev                                       # use full wedge
   baseIPD2Prm_135['M3_FREQ_RANGE'] = (RPM-500, RPM+500)                                        # Frequency range for out-of-phase motion detector
   baseIPD2Prm_135['MOVING_BACKOFF'] = 0x0010                                                   # no back-off in C-phase
   baseIPD2Prm_135['SPECTRAL_DETECTOR3'] = [0x8889, 1, 3855, 650, 1, 5153, 1, 2, 29535, -1]     # changed definition for DC_WAVE_CALC
   baseIPD2Prm_135['SPECTRAL_DETECTOR5'] = [329, 1024, 3614, 650, 1, 1073, 8, 1, 29535, -1]     # Using fixed reference for using C-phase as reference
   if testSwitch.FE_0274637_496738_P_DC_DETCR_DSA_CONTACT_DETECTION:
      del(baseIPD2Prm_135['DYNAMIC_THRESH_BACKOFF'])
      del(baseIPD2Prm_135['INITIAL_DELAY'])
      del(baseIPD2Prm_135['LO_RAMP_CONT_RANGE'])   
      del(baseIPD2Prm_135['PATTERN_IDX'])
      del(baseIPD2Prm_135['RETEST_DELAY'])
      del(baseIPD2Prm_135['GAIN'])
      del(baseIPD2Prm_135['ZONE_POSITION'])

   ########################################################################################################################################################################
   #
   #
   #           Return Completed Dictionary
   #
   #
   ########################################################################################################################################################################

   #objMsg.printMsg('MybaseIPD2Prm_135 = %s ' % (str(baseIPD2Prm_135)), )
   return baseIPD2Prm_135

   ########################################################################################################################################################################
   #
   #
   #           Parameter defines/definititions
   #
   #
   ########################################################################################################################################################################

   #define CWORD1_UNUSED_BIT                          ( 0x0001 )
   #define CWORD1_MASK_SERVO_UNSAFES                  ( 0x0002 )
   #define CWORD1_TEST_ALL_TRACKS                     ( 0x0004 )
   #define CWORD1_RUN_CONCURRENT                      ( 0x0008 )
   #define CWORD1_RUN_BY_SPECIFIED_ZONE_ORDER         ( 0x0010 )
   #define CWORD1_RUN_BY_ZONE_OD_TO_ID                ( 0x0020 )
   #define CWORD1_RUN_BY_ZONE_ID_TO_OD                ( 0x0040 )
   #define CWORD1_TEST_ALL_HEADS                      ( 0x0080 )
   #define CWORD1_RUN_FIND_GOOD_TRACK                 ( 0x0100 )
   #define CWORD1_SEEK_AWAY_ON_CONTACT                ( 0x0200 )
   #define CWORD1_RUN_WPH_AND_HO                      ( 0x0400 )
   #define CWORD1_NORMALIZE_AGC                       ( 0x0800 )
   #define CWORD1_LIMIT_DAC_RANGE_BASED_ON_PREV_TRACK ( 0x1000 )
   #define CWORD1_CURVE_FIT_FINAL_CONTACT_DACS        ( 0x2000 )
   #define CWORD1_LIMIT_DAC_RANGE_BASED_ON_REGRESSION ( 0x4000 )
   #define CWORD1_INTERPOLATE_CLEARANCE               ( 0x8000 )


   #define CWORD2_SAVE_RESULTS_TO_RAM                 ( 0x0001 )
   #define CWORD2_SAVE_RESULTS_TO_FLASH               ( 0x0002 )
   #define CWORD2_UPDATE_SYSTEM_ZONE                  ( 0x0004 )
   #define CWORD2_ALLOW_MORE_THAN_2_FASTIO_REVS       ( 0x0008 )
   #define CWORD2_CONFIRM_INITIAL_ZONES               ( 0x0010 )
   #define CWORD2_EXTRME_OD_ID_RUN                    ( 0x0020 )
   #define CWORD2_DO_DUAL_CURVE_FIT                   ( 0x0040 )
   #define CWORD2_FAIL_IF_GLOBAL_MAX_DAC_REACHED      ( 0x0080 )
   #define CWORD2_RUN_INITIAL_ZONES_BASED_ON_RAP_CLR  ( 0x0100 )
   #define CWORD2_INTERPOLATE_WIRP_LIMITS             ( 0x0200 )
   #define CWORD2_RMS_MOTION_CALCULATION              ( 0x0400 )
   #define CWORD2_PRED_INTERVAL_DYNAMIC_THRESHOLD     ( 0x0800 )


   #define GLOBAL_DISPLAY_OPTIONS_PER_ITERATION_AGC_STATS      (0x0001)
   #define GLOBAL_DISPLAY_OPTIONS_DUMP_TIME_AVERAGED_AGC       (0x0002)
   #define GLOBAL_DISPLAY_OPTIONS_DUMP_TIME_AVERAGED_PES       (0x0004)
   #define GLOBAL_DISPLAY_OPTIONS_DISABLE_TRACK_SUMMARY_OUTPUT (0x0008)
   #define GLOBAL_DISPLAY_OPTIONS_DUMP_REVS_IN_CONTACT         (0x0010)
   #define GLOBAL_DISPLAY_OPTIONS_DUMP_DATA_ON_RETRY           (0x0020)
   #define GLOBAL_DISPLAY_OPTIONS_DUMP_LOW_AVERAGED_REF_AGC    (0x0040)
   #define GLOBAL_DISPLAY_OPTIONS_DUMP_SET_SAVE_RESTORE_OCLIM  (0x0080)
   #define GLOBAL_DISPLAY_OPTIONS_POLY_FIT                     (0x0100)
   #define GLOBAL_DISPLAY_OPTIONS_AGC_OPTI                     (0x0200)
