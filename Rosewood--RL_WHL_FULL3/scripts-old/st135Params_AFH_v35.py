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
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/st135Params_AFH_v35.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/st135Params_AFH_v35.py#1 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#


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
CWORD2_RUN_INITIAL_ZONES_BASED_ON_RAP_CLR = 0x0100
CWORD2_CONFIRM_INITIAL_ZONES              = 0x0010
CWORD2_EXTRME_OD_ID_RUN                   = 0x0020



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
                              benchMode,     enableFAFH,         iConsistencyCheckRetry ):


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

   import types

   # this is here for robustness
   programNameList = programName.split(".")
   if len(programNameList) >= 1:
      programName = programNameList[0]


   if virtualRun:
      SpokesPerRev = 272
      RPM = 7200  # you should strongly consider adding this so that the calculation is correct in VE mode

      if iHead == 0:
         headType = 'RHO'
      else:
         headType = 'TDK'


   #
   if benchMode == 1:
      pass
      # ABSOLUTELY no testSwitch references in AFH v21 and forward.  It is NOT allowed.
##     class CSwitches:
##        pass
##
##     testSwitch = CSwitches()

   else:
      from Test_Switches import testSwitch




   ####################################################################################################################################################
   #
   #
   #                                         FAFH Work-arounds
   #
   #
   ####################################################################################################################################################

   # Due to the Zone Order change; allow a Grenada and Grenada_FAFH to allow the zone order to be smaller for current production,
   #    but remain larger as required for TCS curve fitting in AFH3 and AFH4 for FAFH.

   programName_FAFH = programName
   if (enableFAFH == 1) and (programName == "Grenada"):
      programName_FAFH = "Grenada_FAFH"





   ####################################################################################################################################################
   #
   #
   #                                         Test Limit Input Dictionaries by Program and Head Type
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
         'WRITER_HEATER':{                                    #Maximum allowed signed ID-OD Delta in DAC.  Values must lie between -128 and +127
            'Grenada' : {'TDK': (0,0), 'RHO': (0,0)},             #First entry will force a global retry.
            'Megalodon':{'TDK': (0,0), 'RHO': (30,60)},            # Second entry will fail drive on last global retry
            'Carib'   : {'TDK': (0,0), 'RHO': (22,0)}},
         'READER_HEATER':{                                    #Maximum allowed signed ID-OD Delta in DAC.  Values must lie between -128 and +127
            'Grenada' : {'TDK': (0,0), 'RHO': (0,0)},             #First entry will force a global retry.
            'Megalodon':{'TDK': (0,0), 'RHO': (30,60)},            # Second entry will fail drive on last global retry
            'Carib'   : {'TDK': (0,0), 'RHO': (22,0)}}},
      'Min_IDOD_DeltaDAC':{                                    #Minimum allowed signed ID-OD delta in DAC.  Values must lie between -128 and +127
         'WRITER_HEATER':{
            'Grenada' : {'TDK': (70,75), 'RHO': (30,50)},         #First entry will force a global retry.
            'Megalodon':{'TDK': (30,50), 'RHO': (-30,-60)},        #Second entry will fail drive on last global retry
            'Carib' :   {'TDK': (30,50), 'RHO': (-22,100)}},
         'READER_HEATER':{
            'Grenada' : {'TDK': (70,75), 'RHO': (30,50)},         #First entry will force a global retry.
            'Megalodon':{'TDK': (30,50), 'RHO': (-30,-60)},        #Second entry will fail drive on last global retry
            'Carib' :   {'TDK': (30,50), 'RHO': (-20,100)}}},
      'MaxDACRange':{                                          #Maximum allowed unsigned contact dac range.  Values must lie between 0 and 255
         'WRITER_HEATER':{
            'Grenada' : {'TDK': (100,110), 'RHO': (40,75)},            #First entry is applies during initial global retry.
            'Megalodon':{'TDK': (75,75), 'RHO': (30,60)},
            'Carib' :   {'TDK': (75,75), 'RHO': (35,150)}},
         'READER_HEATER':{
            'Grenada' : {'TDK': (100,110), 'RHO': (40,75)},            #First entry is applies during initial global retry.
            'Megalodon':{'TDK': (75,75), 'RHO': (30,60)},
            'Carib' :   {'TDK': (75,75), 'RHO': (45,150)}}},
      'MinInterpolatedDAC':{                                   #Minimum Interpolated DAC.  Values must lie between 0 and 255
         'WRITER_HEATER':{
            'Grenada' : {'TDK': (12,12), 'RHO': (30,28)},            #First entry will force a global retry.
            'Megalodon':{'TDK': (12,12), 'RHO': (12,12)},
            'Carib' :   {'TDK': (12,12), 'RHO': (12,12)}},
         'READER_HEATER':{
            'Grenada' : {'TDK': (12,12), 'RHO': (55,53)},            #First entry will force a global retry.
            'Megalodon':{'TDK': (12,12), 'RHO': (12,12)},
            'Carib' :   {'TDK': (12,12), 'RHO': (12,12)}}},
      'ZoneSlopeZones':{                                       #Zones to use for zone to zone delta.  0x0401 will apply limit to (zone4-zone1)
         'WRITER_HEATER':{
            'Grenada' : {'TDK': (0x0400), 'RHO': (0x0400)},
            'Megalodon':{'TDK': (0x0400), 'RHO': (0x0400)},
            'Carib' :   {'TDK': (0x0400), 'RHO': (0x0400)}},
         'READER_HEATER':{
            'Grenada' : {'TDK': (0x0400), 'RHO': (0x0400)},
            'Megalodon':{'TDK': (0x0400), 'RHO': (0x0400)},
            'Carib' :   {'TDK': (0x0400), 'RHO': (0x0400)}}},
      'MaxZoneToZoneSlope':{                                   #Maximum allowed signed delta between the two zones specified in ZoneSlopeZones.
         'WRITER_HEATER':{
            'Grenada' : {'TDK': (127,127), 'RHO': (127,127)},        #First entry will force a global retry.
            'Megalodon':{'TDK': (127,127), 'RHO': (127,127)},
            'Carib' :   {'TDK': (127,127), 'RHO': (127,127)}},
         'READER_HEATER':{
            'Grenada' : {'TDK': (127,127), 'RHO': (127,127)},        #First entry will force a global retry.
            'Megalodon':{'TDK': (127,127), 'RHO': (127,127)},
            'Carib' :   {'TDK': (127,127), 'RHO': (127,127)}}},
      'MinZoneToZoneSlope':{                                   #Minimum allowed signed delta between the two zones specified in ZoneSlopeZones.
         'WRITER_HEATER':{
            'Grenada' : {'TDK': (-127,-127), 'RHO': (-127,-127)},    #First entry will force a global retry.
            'Megalodon':{'TDK': (-127,-127), 'RHO': (-127,-127)},
            'Carib' :   {'TDK': (-127,-127), 'RHO': (-127,-127)}},
         'READER_HEATER':{
            'Grenada' : {'TDK': (-127,-127), 'RHO': (-127,-127)},    #First entry will force a global retry.
            'Megalodon':{'TDK': (-127,-127), 'RHO': (-127,-127)},
            'Carib' :   {'TDK': (-127,-127), 'RHO': (-127,-127)}}},
      'MaxSearchInterference':{                                #Maximum unsigned interference in dac based on final interpolation
         'WRITER_HEATER':{
            'Grenada' : {'TDK': (120), 'RHO': (120)},                #Limit will force failure regardless of global retry count
            'Megalodon':{'TDK': (120), 'RHO': (120)},
            'Carib' :   {'TDK': (120), 'RHO': (120)}},
         'READER_HEATER':{
            'Grenada' : {'TDK': (120), 'RHO': (120)},                #Limit will force failure regardless of global retry count
            'Megalodon':{'TDK': (120), 'RHO': (120)},
            'Carib' :   {'TDK': (120), 'RHO': (120)}}},
      'MaxResidualStdev':{                                     #Maximum unsigned residual standard deviation.  50 = 5 dac
         'WRITER_HEATER':{
            'Grenada' : {'TDK': (50,50), 'RHO': (50,50)},            #First entry will force a global retry.
            'Megalodon':{'TDK': (50,50), 'RHO': (50,50)},
            'Carib' :   {'TDK': (50,50), 'RHO': (50,50)}},
         'READER_HEATER':{
            'Grenada' : {'TDK': (50,50), 'RHO': (50,50)},            #First entry will force a global retry.
            'Megalodon':{'TDK': (50,50), 'RHO': (50,50)},
            'Carib' :   {'TDK': (50,50), 'RHO': (50,50)}}},
      'MaxExtrapolationTracks':{                               #Maximum number of tracks the final dual curve fit can extrapolate
         'WRITER_HEATER':{
            'Grenada' : {'TDK': (25000), 'RHO': (25000)},            #Fixed limit does not change during global retries SHD changed from 12000 to 25000
            'Megalodon':{'TDK': (28000), 'RHO': (28000)},
            'Carib' :   {'TDK': (17000), 'RHO': (17000)}},
         'READER_HEATER':{
            'Grenada' : {'TDK': (25000), 'RHO': (25000)},            #Fixed limit does not change during global retries SHD Changed to 25k
            'Megalodon':{'TDK': (28000), 'RHO': (28000)},
            'Carib' :   {'TDK': (17000), 'RHO': (17000)}}}
      }

   ####################################################################################################################


   ########################################## Final Curve Fit Limits in Angstrom ######################################
   # First Element under head index is the initial limit which will force initial global retries.
   # The second element under head index is the final failure in subsequent global retries.
   FinalCurveFitLimitsAngstrom = {
     'Max_IDOD_DeltaClr':{
        'WRITER_HEATER':{                                    #Maximum ID-OD Delta.  Signed Value (ID-OD)
           'Grenada' :  {'TDK': (0,0), 'RHO': (0,0)},
           'Megalodon': {'TDK': (0,0), 'RHO': (0,0)},
           'Carib' :    {'TDK': (0,0), 'RHO': (100,100)}},
        'READER_HEATER':{
           'Grenada' :  {'TDK': (0,0), 'RHO': (0,0)},
           'Megalodon': {'TDK': (0,0), 'RHO': (0,0)},
           'Carib' :    {'TDK': (0,0), 'RHO': (100,100)}}},
     'Min_IDOD_DeltaClr':{
        'WRITER_HEATER':{                                    #Min ID-OD Delta.  Signed Value (ID-OD)
           'Grenada' :  {'TDK': (127,127), 'RHO': (127,127)},
           'Megalodon': {'TDK': (127,127), 'RHO': (127,127)},
           'Carib' :    {'TDK': (127,127), 'RHO': (-100,-100)}},
        'READER_HEATER':{
           'Grenada' :  {'TDK': (127,127), 'RHO': (127,127)},
           'Megalodon': {'TDK': (127,127), 'RHO': (127,127)},
           'Carib' :    {'TDK': (127,127), 'RHO': (-100,-100)}}},
     'MaxClrRange':{                                          #Maximum Clearance range
        'WRITER_HEATER':{
           'Grenada' :  {'TDK': (127,127), 'RHO': (127,127)},
           'Megalodon': {'TDK': (127,127), 'RHO': (127,127)},
           'Carib' :    {'TDK': (127,127), 'RHO': (127,127)}},
        'READER_HEATER':{
           'Grenada' :  {'TDK': (127,127), 'RHO': (127,127)},
           'Megalodon': {'TDK': (127,127), 'RHO': (127,127)},
           'Carib' :    {'TDK': (127,127), 'RHO': (127,127)}}},
     'MaxConsistencyLimit':{
        'PreHirp':{
           'WRITER_HEATER':{                                  #Maximum Delta between HO and WPH Clr.  Signed Value (HO-WPH)
              'Grenada' :  {'TDK': (0,0), 'RHO': (0,0)},
              'Megalodon': {'TDK': (0,0), 'RHO': (0,0)},
              'Carib' :    {'TDK': (0,0), 'RHO': (100,100)}},
           'READER_HEATER':{                                  #Maximum Delta between HO and WPH Clr.  Signed Value (HO-WPH)
              'Grenada' :  {'TDK': (0,0), 'RHO': (0,0)},
              'Megalodon': {'TDK': (0,0), 'RHO': (0,0)},
              'Carib' :    {'TDK': (0,0), 'RHO': (100,100)}}},
        'PostHirp':{
           'WRITER_HEATER':{                                  #Maximum Delta between HO and WPH Clr.  Signed Value (HO-WPH)
              'Grenada' :  {'TDK': (0,0), 'RHO': (0,0)},
              'Megalodon': {'TDK': (0,0), 'RHO': (0,0)},
              'Carib' :    {'TDK': (0,0), 'RHO': (100,100)}},
           'READER_HEATER':{                                  #Maximum Delta between HO and WPH Clr.  Signed Value (HO-WPH)
              'Grenada' :  {'TDK': (0,0), 'RHO': (0,0)},
              'Megalodon': {'TDK': (0,0), 'RHO': (0,0)},
              'Carib' :    {'TDK': (0,0), 'RHO': (100,100)}}}},
     'MinConsistencyLimit':{
        'PreHirp':{
           'WRITER_HEATER':{                                  #Maximum Delta between HO and WPH Clr.  Signed Value (HO-WPH)
              'Grenada' :  {'TDK': (25,25), 'RHO': (25,25)},
              'Megalodon': {'TDK': (25,25), 'RHO': (25,25)},
              'Carib' :    {'TDK': (25,25), 'RHO': (-100,-100)}},
           'READER_HEATER':{                                  #Maximum Delta between HO and WPH Clr.  Signed Value (HO-WPH)
              'Grenada' :  {'TDK': (25,25), 'RHO': (25,25)},
              'Megalodon': {'TDK': (25,25), 'RHO': (25,25)},
              'Carib' :    {'TDK': (25,25), 'RHO': (-100,-100)}}},
        'PostHirp':{
           'WRITER_HEATER':{                                  #Maximum Delta between HO and WPH Clr.  Signed Value (HO-WPH)
              'Grenada' :  {'TDK': (25,25), 'RHO': (25,25)},
              'Megalodon': {'TDK': (25,25), 'RHO': (25,25)},
              'Carib' :    {'TDK': (25,25), 'RHO': (-100,-100)}},
           'READER_HEATER':{                                  #Maximum Delta between HO and WPH Clr.  Signed Value (HO-WPH)
              'Grenada' :  {'TDK': (25,25), 'RHO': (25,25)},
              'Megalodon': {'TDK': (25,25), 'RHO': (25,25)},
              'Carib' :    {'TDK': (25,25), 'RHO': (-100,-100)}}}},
     'MaxCrossHeaterConsistencyLimit':{
        'PreHirp':{                                  #Maximum Clearance Delta between Reader Heater and Writer Heater.  Signed Value (Reader-Writer)
           'Grenada' :  {'TDK': (0,0), 'RHO': (47,65)},
           'Megalodon': {'TDK': (0,0), 'RHO': (43,53)},
           'Carib' :    {'TDK': (0,0), 'RHO': (43,53)}},
        'PostHirp':{                                 #Maximum Clearance Delta between Reader Heater and Writer Heater.  Signed Value (Reader-Writer)
           'Grenada' :  {'TDK': (0,0), 'RHO': (44,52)},
           'Megalodon': {'TDK': (0,0), 'RHO': (33,43)},
           'Carib' :    {'TDK': (0,0), 'RHO': (33,43)}}},
     'MinCrossHeaterConsistencyLimit':{
        'PreHirp':{                                  #Minimum Clearance Delta between Reader Heater and Writer Heater.  Signed Value (Reader-Writer)
           'Grenada' :  {'TDK': (25,25), 'RHO': (-47,-65)},
           'Megalodon': {'TDK': (25,25), 'RHO': (-30,-40)},
           'Carib' :    {'TDK': (25,25), 'RHO': (-27,-37)}},
        'PostHirp':{                                  #Minimum Clearance Delta between Reader Heater and Writer Heater.  Signed Value (Reader-Writer)
           'Grenada' :  {'TDK': (25,25), 'RHO': (-26,-34)},
           'Megalodon': {'TDK': (25,25), 'RHO': (-30,-40)},
           'Carib' :    {'TDK': (25,25), 'RHO': (-17,-27)}}}
     }
   ###################################################################################################################

   ######################################  FastIO Revs ###############################################################
   ###


   initialRevs={
      'Grenada' :{
         'HighSkew': {'TDK':30,'RHO':30},  #these values are used during the initial attempt
         'LowSkew' : {'TDK':50,'RHO':50}},
      'Megalodon':{
         'HighSkew': {'TDK':30,'RHO':30},  #these values are used during the initial attempt
         'LowSkew' : {'TDK':50,'RHO':50}},
      'Carib':{
         'HighSkew': {'TDK':30,'RHO':30},  #these values are used during the initial attempt
         'LowSkew' : {'TDK':50,'RHO':50}}
      }

   lowSkewZones={                           #inclusive zones to use "LowSkew" revs.  (Lower Zone,Higher Zone)
      'Grenada'  :   (10,22),
      'Megalodon':   (11,16),
      'Carib'    :   (14,22)
      }
   internalRetryRevs={
      'Grenada' :{
         'HighSkew': {'TDK':50,'RHO':50},  #these values are used during the initial attempt
         'LowSkew' : {'TDK':70,'RHO':70}},
      'Megalodon':{
         'HighSkew': {'TDK':50,'RHO':50},  #these values are used during the initial attempt
         'LowSkew' : {'TDK':70,'RHO':70}},
      'Carib':{
         'HighSkew': {'TDK':40,'RHO':40},  #these values are used during the initial attempt
         'LowSkew' : {'TDK':60,'RHO':60}}
      }
   ####################################################################################################################

   ######################################  On the fly contact dac regression limits ###################################
   ### These limits apply during the contact search.  Dac limit failures will cause an internal retry
   ### These do not apply to the final interpolation and will not (directly) cause test failures or global retries

   SearchLimits = {
      'ZoneOrder':{
         'WRITER_HEATER': {
            'Grenada_FAFH' : {1:(28,2,1,25,6,21,11,29,0),  #first key within product indicates AFH state.  Only enter zones to be tested (no -1's needed) shd added zone 28 and 1
                              2:(28,2,1,25,6,21,11,29,0),
                              3:(28,1,25,6,21,11,29,0),
                              4:(28,1,25,6,21,11,29,0)},
            'Grenada':  {1:(28,2,25,6,21,11,29,1,0),  #first key within product indicates AFH state.  Only enter zones to be tested (no -1's needed)
                         2:(28,2,25,6,21,11,29,1,0),  #shd removed zone 28,1, 14 and mode from Zn20 to 22 to get higher skew.
                         3:(28,2,25,6,1),
                         4:(28,2,25,6,1)},
            'Megalodon':{1:(21,2,18,5,16,8,11,1,22,0,23),
                         2:(22,1,18,5,8,16,11,23,0),
                         3:(22,1,18,5,8),
                         4:(22,1,18,5,8)},
            'Carib':    {1:(26,3,23,7,20,12,2,27,1,28,0,29),
                         2:(26,3,23,7,20,12,2,27,1,28,0,29),
                         3:(0,7,20,23,29),
                         4:(0,7,20,23,29),
                         25:(0,7,20,23,29)},  # shouldn't matter, this should be ignored based on CWORD1 settings.  MTB 18-Feb-2011
            }, #end of WRITER_HEATER
         'READER_HEATER': {
            'Grenada_FAFH': {1:(28,2,1,25,6,21,11,29,0),  #first key within product indicates AFH state.  Only enter zones to be tested (no -1's needed)
                             2:(28,2,1,25,6,21,11,29,0),  #shd removed zone 28,1, 14 and mode from Zn20 to 22 to get higher skew.
                             3:(28,2,25,6,1),
                             4:(28,2,25,6,1)},
            'Grenada':  {1:(28,2,25,6,21,11,29,1,0),  #first key within product indicates AFH state.  Only enter zones to be tested (no -1's needed)
                         2:(28,2,25,6,21,11,29,1,0),  #shd removed zone 28,1, 14 and mode from Zn20 to 22 to get higher skew.
                         3:(28,2,25,6,1),
                         4:(28,2,25,6,1)},
            'Megalodon':{1:(21,2,18,5,16,8,11,1,22,0,23),
                         2:(22,1,18,5,8,16,11,23,0),
                         3:(22,1,18,5,8),
                         4:(22,1,18,5,8)},
            'Carib':    {1:(26,3,23,7,20,12,2,27,1,28,0,29),
                         2:(26,3,23,7,20,12,2,27,1,28,0,29),
                         3:(0,7,20,23,29),
                         4:(0,7,20,23,29),
                         25:(0,7,20,23,29)},  # shouldn't matter, this should be ignored based on CWORD1 settings.  MTB 18-Feb-2011
            }, #end of READER_HEATER
         }, # end of ZoneOrder
      'MaxExtrapolationTracks':{                                           #Maximum OTF regression extrapolation.  Failures use default start/end dacs
         'Grenada' :    {'TDK': (42000), 'RHO': (42000)},                  #if this limit is exceeded in a given zone, then OTF is turned on in that zone  SHD changed to 45k from 40k
         'Megalodon':   {'TDK': (40000), 'RHO': (40000)},
         'Carib' :      {'TDK': (40000), 'RHO': (40000)}},
      'MinWICD':{
         'WRITER_HEATER':{                                                      #Min unsigned internal retry Dac Delta between WPH and HO
            'Grenada' :    {'TDK': (0x0204,0x0204), 'RHO': (0x0102,0x0102)},    #First entry applies in AFH1.  Second for all other states
            'Megalodon':   {'TDK': (0x0204,0x0204), 'RHO': (0x0204,0x0204)},    #LSB applies during initial internal retry
            'Carib' :      {'TDK': (0x0204,0x0204), 'RHO': (0x0204,0x0204)}
            },   #MSB applies during subsequent internal retries
         'READER_HEATER':{
            'Grenada' :    {'TDK': (0x0204,0x0204), 'RHO': (0x0204,0x0204)},
            'Megalodon':   {'TDK': (0x0204,0x0204), 'RHO': (0x0204,0x0204)},
            'Carib' :      {'TDK': (0x0204,0x0204), 'RHO': (0x0204,0x0204)},
            },
         },
      'MaxWICD':{
         'WRITER_HEATER':{                                                        #Max unsigned internal retry Dac Delta between WPH and HO
            'Grenada' :    {'TDK': (0x241E,0x241E), 'RHO': (0x241E,0x241E)},      #First entry applies in AFH1.  Second for all other states
            'Megalodon':   {'TDK': (0x241E,0x241E), 'RHO': (0x241E,0x241E)},
            'Carib' :      {'TDK': (0x241E,0x241E), 'RHO': (0x241E,0x241E)},
            },
         'READER_HEATER':{
            'Grenada' :    {'TDK': (0x241E,0x241E), 'RHO': (0x241E,0x241E)},
            'Megalodon':   {'TDK': (0x241E,0x241E), 'RHO': (0x241E,0x241E)},
            'Carib' :      {'TDK': (0x241E,0x241E), 'RHO': (0x241E,0x241E)},
            },
         },
      'MaxZoneToZoneDelta':{
         'WRITER_HEATER':{                                                    #Maximum unsigned zone to zone delta
            'Grenada' :    {'TDK': (0x0C0A,0x0C0A), 'RHO': (0x0C0A,0x0C0A)},  #First entry applies in AFH1.  Second for all other states
            'Megalodon':   {'TDK': (0x0C0A,0x0C0A), 'RHO': (0x0C0A,0x0C0A)},
            'Carib' :      {'TDK': (0x0C0A,0x0C0A), 'RHO': (0x0C0A,0x0C0A)}
            },
         'READER_HEATER':{
            'Grenada' :    {'TDK': (0x0C0A,0x0C0A), 'RHO': (0x0C0A,0x0C0A)},
            'Megalodon':   {'TDK': (0x0C0A,0x0C0A), 'RHO': (0x0C0A,0x0C0A)},
            'Carib' :      {'TDK': (0x0C0A,0x0C0A), 'RHO': (0x0C0A,0x0C0A)},
            }
         },
      'GlobalHeaterLimits':{                                                  #Global heater search start dac and max dac
         'WRITER_HEATER':{
            'Grenada' :    {'TDK': (30,200,0x0103,6), 'RHO': (25,230,0x0103,6)},  #First Entry is the start dac for initial zones
            'Megalodon':   {'TDK': (30,200,0x0103,6), 'RHO': (30,160,0x0103,6)},  #Second Entry is the max search dac
            'Carib' :      {'TDK': (30,200,0x0103,6), 'RHO': (15,180,0x0103,6)},  #Third Entry is the search step in dac.  MSB=fine, LSB=coarse
            },                                                                    #Fourth Entry is the fine serach backup
         'READER_HEATER':{
            'Grenada' :    {'TDK': (30,250,0x0103,6), 'RHO': (50,250,0x0204,10)},
            'Megalodon':   {'TDK': (30,250,0x0103,6), 'RHO': (50,250,0x0205,10)},
            'Carib' :      {'TDK': (30,250,0x0103,6), 'RHO': (30,250,0x0103,6)},
            },
         },
   }
   ####################################################################################################################

   ######################################  Search Options ###################################
   ### These limits apply during the contact search.  Dac limit failures will cause an internal retry
   ### These do not apply to the final interpolation and will not (directly) cause test failures or global retries
   SearchOptions = {
      'ShutOffHighFreqDuringGlobalRetries' : {
         'Grenada'   :  {'TDK': 0, 'RHO': 0},
         'Megalodon' :  {'TDK': 0, 'RHO': 0},
         'Carib'     :  {'TDK': 0, 'RHO': 0}},
      'IncreaseAGCMinFreqDuringGlobalRetries': {
         'Grenada'   :  {'TDK': 0, 'RHO': 0},
         'Megalodon' :  {'TDK': 0, 'RHO': 1},
         'Carib'     :  {'TDK': 0, 'RHO': 0}},       ## Increases the minimum AGC frequency during retries
      'DeTuneIPD2SensitivityDuringGlobalRetries': {
         'Grenada'   :  {'TDK': 0, 'RHO': 0},
         'Megalodon' :  {'TDK': 0, 'RHO': 1},
         'Carib'     :  {'TDK': 0, 'RHO': 0}},       ## Increases the minimum AGC frequency during retries
      'RunReaderHeaterWPH' :  {
         'Grenada'   :  {'TDK': 0, 'RHO': 0},
         'Megalodon' :  {'TDK': 0, 'RHO': 0},
         'Carib'     :  {'TDK': 0, 'RHO': 0}},
      'EnableCurveFitDuringTCSCal':{
         'WRITER_HEATER':{
            'Grenada_FAFH'  :   {'TDK': 0, 'RHO': 1},
            'Grenada'       :   {'TDK': 0, 'RHO': 0},
            'Megalodon'     :   {'TDK': 0, 'RHO': 0},
            'Carib'         :   {'TDK': 0, 'RHO': 0},
            },
         'READER_HEATER':{
            'Grenada_FAFH'  :   {'TDK': 0, 'RHO': 0},
            'Grenada'       :   {'TDK': 0, 'RHO': 0},
            'Megalodon'     :   {'TDK': 0, 'RHO': 0},
            'Carib'         :   {'TDK': 0, 'RHO': 0}}},
      'RunReaderHeaterOffPreheatClrInAFH1':{
         'Grenada'      : {'TDK': 0, 'RHO':1},
         'Megalodon'    : {'TDK': 0, 'RHO':0},
         'Carib'        : {'TDK': 0, 'RHO':0}},
      'AGCDetectorZones':{                               #Specify the inclusive range of zones for which the AGC detector will be enabled
         'Grenada'      : {'TDK': (6,21), 'RHO':(6,21)}, #(8,20) will run AGC in zones 8-20
         'Grenada_FAFH' : {'TDK': (6,21), 'RHO':(6,21)},
         'Megalodon'    : {'TDK': (0,23), 'RHO':(8,18)},
         'Carib'        : {'TDK': (19,21), 'RHO':(19,21)}},
      'IPDVersionToExecute':{                           #first entry is used beyond first global retrie, second is first 2 attempts
         'Grenada'      : {'TDK': (3,2), 'RHO':(3,2)},  #(3,2) will use IPD2 on the first 2 global retries and IPD3 on the third and beyond
         'Megalodon'    : {'TDK': (3,2), 'RHO':(3,2)},
         'Carib'        : {'TDK': (3,2), 'RHO':(3,2)}},
      'AFH1_WriteTriplet':{
         'Grenada'      : {'TDK': (-1,-1,-1), 'RHO':(6,4,10)},  #This input determines the write power applied during aFH1 for the WRITER_HEATER
         'Megalodon'    : {'TDK': (-1,-1,-1), 'RHO':(-1,-1,-1)},     #it should be chosen to be as close as possible to the average AFH2 pick
         'Carib'        : {'TDK': (-1,-1,-1), 'RHO':( 5, 0, 7)}}  #(-1,-1,-1) will use the default triplet
      }

   baseIPD2Prm_135 = {
      'test_num':135,
      'prm_name':'baseIPD2Prm_135',
      'timeout':10000,

      'HEAD_RANGE'                     : (0x0101),          # heads to test
      'TEST_CYL'                       : (0, 50),           # test cyl only used for atomic tests
      'ZONE_POSITION'                  : (100,),            # Controls where within the zone to test ( 100 = 50% )
      'INITIAL_DELAY'                  : (30,  ),           # ms Delay after initial contact
      'RETEST_DELAY'                   : (100, ),           # ms Delay after retry contact is tripped
      'DYNAMIC_THRESH_BACKOFF'         : (12,),             # dynamic threshold lag
      'MAX_BASELINE_DAC'               : (20,),             # max baseline dac for dynamic threshold
      'DACS_BEYOND_CONTACT'            : (0,),               # dacs to measure after contact is declared
      'PATTERN_IDX'                    : (-1,),              # write pattern -1: random
      'LO_RAMP_CONT_RANGE'             : (255, 0),          # Refresh the IPD stats every 10 dacs at appropriate retry depth
      'AGC_RETRY_ZONES'                : (0x3FFF, 0xFFFF),  # if a bit is RESET here, AGC detectors will be shut off in that zone at the 4th retry
      'PES_RETRY_ZONES'                : (0x3FFF, 0xFFFF),  # if a bit is RESET here, PES detectors will be shut off in that zone at the 4th retry
      'BASELINE_REVS'                  : (0x0508,),
      'COARSE_CONFIRM_INTERFERENCE'    :  2,
      'CONTACT_VERIFY'                 : (0x0201,),          # Retry verifies, initial verifies
      'DEBUG_PRINT'                    : (0x02B1,),          # Controls debug output
      'GAIN'                           : (7,),
      'MOVING_BACKOFF'                 : (0xFF28,),              # Local-Reference Dac Backoff


      # the following parameters have values that are calculated based on the limit dictionaries above.
      # these values are initialzed to -999
      'CONTACT_LIMITS'                 : [-999, 0x1104, -999, -999, -160, 160, -999],
      'CURVE_FIT2'                     : [3,4,120,5, -999, -999, 0, 0 ],
      'HEATER'                         : [-999, -999],  # ( [StartDac,EndDac], [FineStep,CoarseStep] )
      'READ_HEAT'                      : ( -999,),            # Maximum Dac for HeatOnly measurement if "CWORD1_RUN_WPH_AND_HO" is set
   }


   ###  TEST_LIMITS_5   ### Added by SHD to incorporate States
   if AFH_State in [1]:
      baseIPD2Prm_135['TEST_LIMITS_5'] = [ 0x0401, 0x0603, -999, 0, 0, ]       # (Low points/Low order, High points/High order, Extrapolation limit,  Not used, Not used) SHD changed param 2 from 0503 to 0603
   elif AFH_State in [2]:
      baseIPD2Prm_135['TEST_LIMITS_5'] = [ 0xFF01, 0xFF03, -999, 0, 0, ]
   else:
      baseIPD2Prm_135['TEST_LIMITS_5'] = [ 0xFF01, 0xFF03, -999, 0, 0, ]       # (Low points/Low order, High points/High order, Extrapolation limit,  Not used, Not used)


   ###  CWORD1 & 2  ###

   if AFH_State in [1]:
      baseIPD2Prm_135["CWORD1"]        = 0x6F16
      baseIPD2Prm_135["CWORD2"]        = 0x00C5
   elif AFH_State in [2]:
      baseIPD2Prm_135["CWORD1"]        = 0x6F16
      baseIPD2Prm_135["CWORD2"]        = 0x01C5
   else:
      baseIPD2Prm_135["CWORD1"]        = 0x4F16
      baseIPD2Prm_135["CWORD2"]        = 0x0180

   if (SearchOptions['EnableCurveFitDuringTCSCal'][heaterElement][programName_FAFH][headType] == 1) and (AFH_State in [3,4]):
      baseIPD2Prm_135["CWORD2"]        |= 0x0040 #turn on dual curve fit
      baseIPD2Prm_135["CWORD1"]        |= 0x2000 #turn on final curve fit
   if (SearchOptions['RunReaderHeaterOffPreheatClrInAFH1'][programName][headType] == 1) and (AFH_State == 1) and (heaterElement == 'READER_HEATER') and (intHeadRetryCntr<2):
      baseIPD2Prm_135["CWORD2"]        |= 0x0100 #run off rap in initial zones
      baseIPD2Prm_135['TEST_LIMITS_5'][0] = 0xFF01 #make all zones initial zones
      baseIPD2Prm_135['TEST_LIMITS_5'][1] = 0xFF03 #make all zones initial zones


   ###  DAC_RANGE  ###
   if ( AFH_State == 1):
      if heaterElement == "WRITER_HEATER":
         baseIPD2Prm_135['DAC_RANGE']     = ( -21, 0x1e12, 6,)                          # start search, max search end, min search end.  All relative to expected contact dac
      else:
         baseIPD2Prm_135['DAC_RANGE']     = ( -32, 0x1e12, 6,)                          # start search, max search end, min search end.  All relative to expected contact dac
   elif ( AFH_State in [2,4]):
      baseIPD2Prm_135['DAC_RANGE']     = ( -21, 18, 18,)                         # start search, max search end, min search end.  All relative to expected contact dac
   elif ( AFH_State == 3):
      baseIPD2Prm_135['DAC_RANGE']     = ( -21, 18, 18,)                         # start search, max search end, min search end.  All relative to expected contact dac

   ###  DETECTOR_BIT_MASK  ###

   LowerAGCWord=0
   UpperAGCWord=0
   MinAGCZone=min(SearchOptions['AGCDetectorZones'][programName][headType])
   MaxAGCZone=max(SearchOptions['AGCDetectorZones'][programName][headType])
   for ii in range(32) :
      if ii<16:
         if (ii>=MinAGCZone and ii<=MaxAGCZone):
            LowerAGCWord |= (1 << ii)
      else:
         if (ii>=MinAGCZone and ii<=MaxAGCZone):
            UpperAGCWord |= (1 << (ii-16) )

   baseIPD2Prm_135["DETECTOR_BIT_MASK"]   =  (0xFFFF,0xFFFF, UpperAGCWord,LowerAGCWord , 0xFFFF,0xFFFF, UpperAGCWord,LowerAGCWord, 0xFFFF,0xFFFF, 0xFFFF,0xFFFF)


   ### WRITE_TRIPLET  ####

   if ( (isDriveDualHeater == 1) and (SearchOptions['RunReaderHeaterWPH'][programName][headType] == 0) and (heaterElement == "READER_HEATER") ):
      baseIPD2Prm_135['WRITE_TRIPLET']    =  (0, 0, 0)      # write triplet used during contact detect (WCA,OSA,OSW)
      baseIPD2Prm_135["CWORD1"]           &= ~0x0400        # shut off bit that runs WPH and HO
   elif ( (isDriveDualHeater == 1) and (heaterElement == "READER_HEATER") ):
      baseIPD2Prm_135['WRITE_TRIPLET']    =  (6, 6, 6)      # set fixed high power write triplet for reader heater shd changed to 6,6,6 from 12,12,12
   elif ( (AFH_State==1) and (heaterElement == "WRITER_HEATER") ):
      baseIPD2Prm_135['WRITE_TRIPLET']    =  SearchOptions['AFH1_WriteTriplet'][programName][headType]
   else:
      baseIPD2Prm_135['WRITE_TRIPLET']    =  (-1, -1, -1)   # write triplet used during contact detect (WCA,OSA,OSW)


   ################################################################################################################################################################################################################################################
   IntegrationLimits=0x735F   #default sensitivity
   IPDIndex = 1
   if intHeadRetryCntr ==1 :
      if ( (SearchOptions['DeTuneIPD2SensitivityDuringGlobalRetries'][programName][headType] == 1) and (SearchOptions['IPDVersionToExecute'][programName][headType][IPDIndex] == 2) ):
         #only detune IPD2... IPD3 is not detuned
         IntegrationLimits=0x7D5F
   elif intHeadRetryCntr >=2 :
      IPDIndex = 0
      if ( (SearchOptions['DeTuneIPD2SensitivityDuringGlobalRetries'][programName][headType] == 1) and (SearchOptions['IPDVersionToExecute'][programName][headType][IPDIndex] == 2) ):
         #only detune IPD2... IPD3 is not detuned
         IntegrationLimits=0x7D5F


   if SearchOptions['IPDVersionToExecute'][programName][headType][IPDIndex] == 3:
      SpectralMask=0x1421
   else:
      SpectralMask=0x0431
   baseIPD2Prm_135["SPECTRAL_DETECTOR1"]  = ( 0x00C9, 0x0001, 0x0E1E, 650, 1, SpectralMask, 0x1, 0x1, IntegrationLimits, -1)  ## TDA PES ##
   baseIPD2Prm_135["SPECTRAL_DETECTOR5"]  = ( 0x00C9, 0x0001, 0x0E1E, 650, 1, SpectralMask, 0x4, 0x4, IntegrationLimits, -1)  ## LF PES ##
   baseIPD2Prm_135["SPECTRAL_DETECTOR6"]  = ( 0x0289, 0x0001, 0x0E1E, 650, 1, SpectralMask, 0x10, 0x1, IntegrationLimits, -1)  ## TDA VCM current ##
   baseIPD2Prm_135["SPECTRAL_DETECTOR4"]  = ( 0x00A9, 0x0001, 0x0E1E, 650, 1, SpectralMask, 0x2008, 0x2, IntegrationLimits, -1)  ## TDA AGC ##


   ################################################################################################################################################################################################################################################


   ###  V3BAR Destroking Parameters  ###

   if ( AFH_State == 25):
      baseIPD2Prm_135["WRITE_TRIPLET"] = ( 0, 0, 0,)           # set to 0 to force main detect to be heater only
      baseIPD2Prm_135["CWORD1"]        = ( 0x0B02, )
      baseIPD2Prm_135["CWORD2"]        = ( 0x0090, )

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
         ( ((FinalCurveFitLimitsAngstrom['Max_IDOD_DeltaClr'][heaterElement][programName][headType][limitIndex] << 8)   & 0xFF00) +
           ((FinalCurveFitLimitsAngstrom['Min_IDOD_DeltaClr'][heaterElement][programName][headType][limitIndex])        & 0x00FF    ),
           ( FinalCurveFitLimitsAngstrom['MaxClrRange'][heaterElement][programName][headType][limitIndex]                           ),
           ((FinalCurveFitLimitsAngstrom['MaxConsistencyLimit'][hirpState][heaterElement][programName][headType][limitIndex] << 8) & 0xFF00) +
           ((FinalCurveFitLimitsAngstrom['MinConsistencyLimit'][hirpState][heaterElement][programName][headType][limitIndex])       &0x00FF)   )
   else:

      baseIPD2Prm_135['CLEARANCE_CONSISTENCY_LIMIT_DH']= \
         ( ((FinalCurveFitLimitsAngstrom['Max_IDOD_DeltaClr'][heaterElement][programName][headType][limitIndex] << 8)   & 0xFF00) +
           ((FinalCurveFitLimitsAngstrom['Min_IDOD_DeltaClr'][heaterElement][programName][headType][limitIndex])        & 0x00FF    ),
           ( FinalCurveFitLimitsAngstrom['MaxClrRange'][heaterElement][programName][headType][limitIndex]                           ),
           ((FinalCurveFitLimitsAngstrom['MaxConsistencyLimit'][hirpState][heaterElement][programName][headType][limitIndex] << 8) & 0xFF00) +
           ((FinalCurveFitLimitsAngstrom['MinConsistencyLimit'][hirpState][heaterElement][programName][headType][limitIndex])       &0x00FF),
           ((FinalCurveFitLimitsAngstrom['MaxCrossHeaterConsistencyLimit'][hirpState][programName][headType][limitIndex] << 8) & 0xFF00) +
           ((FinalCurveFitLimitsAngstrom['MinCrossHeaterConsistencyLimit'][hirpState][programName][headType][limitIndex])       &0x00FF)    )
   baseIPD2Prm_135['MAX_MIN_DELTA']= \
      ( ((FinalCurveFitLimitsDAC['Max_IDOD_DeltaDAC'][heaterElement][programName][headType][limitIndex] << 8)   & 0xFF00) +
        ((FinalCurveFitLimitsDAC['Min_IDOD_DeltaDAC'][heaterElement][programName][headType][limitIndex])        & 0x00FF),
        ( FinalCurveFitLimitsDAC['MaxDACRange'][heaterElement][programName][headType][limitIndex]))

   baseIPD2Prm_135['ZONE_DAC_DELTA']= \
      ( ( FinalCurveFitLimitsDAC['ZoneSlopeZones'][heaterElement][programName][headType]                               ),
        ((FinalCurveFitLimitsDAC['MaxZoneToZoneSlope'][heaterElement][programName][headType][limitIndex] << 8) & 0xFF00) +
        ((FinalCurveFitLimitsDAC['MinZoneToZoneSlope'][heaterElement][programName][headType][limitIndex]     ) & 0x00FF))


   baseIPD2Prm_135['CURVE_FIT2'][4]=FinalCurveFitLimitsDAC['MaxExtrapolationTracks'][heaterElement][programName][headType]
   baseIPD2Prm_135['CURVE_FIT2'][5]=FinalCurveFitLimitsDAC['MaxResidualStdev'][heaterElement][programName][headType][limitIndex]



   ##################################### Contact Search Limits ##################################################
   #


   baseIPD2Prm_135['CONTACT_LIMITS'][0]=(
      (FinalCurveFitLimitsDAC['MaxSearchInterference'][heaterElement][programName][headType] << 8) + \
      (FinalCurveFitLimitsDAC['MinInterpolatedDAC'][heaterElement][programName][headType][limitIndex]))


   print "SearchLimits['MinWICD']", SearchLimits['MinWICD']
   print "programName", programName
   print "heaterElement", heaterElement
   print "SearchLimits['MinWICD'][heaterElement]", SearchLimits['MinWICD'][heaterElement]

   baseIPD2Prm_135['CONTACT_LIMITS'][2]=(SearchLimits['MinWICD'][heaterElement][programName][headType][StateIndex])
   baseIPD2Prm_135['CONTACT_LIMITS'][3]=(SearchLimits['MaxWICD'][heaterElement][programName][headType][StateIndex])
   baseIPD2Prm_135['CONTACT_LIMITS'][6]=(SearchLimits['MaxZoneToZoneDelta'][heaterElement][programName][headType][StateIndex])

   baseIPD2Prm_135['TEST_LIMITS_5'][2]=(SearchLimits['MaxExtrapolationTracks'][programName][headType])
   baseIPD2Prm_135['HEATER'][0] = (SearchLimits['GlobalHeaterLimits'][heaterElement][programName][headType][0] << 8) + \
      SearchLimits['GlobalHeaterLimits'][heaterElement][programName][headType][1]
   baseIPD2Prm_135['HEATER'][1] = (SearchLimits['GlobalHeaterLimits'][heaterElement][programName][headType][2])
   baseIPD2Prm_135['READ_HEAT'] = (SearchLimits['GlobalHeaterLimits'][heaterElement][programName][headType][1])
   baseIPD2Prm_135['FINE_SEARCH_BACKUP'] = (SearchLimits['GlobalHeaterLimits'][heaterElement][programName][headType][3])


   ###################################Revs_by_zone and Zone_Order ########################################
   zoneList=list(SearchLimits['ZoneOrder'][heaterElement][programName_FAFH][AFH_State])
   revsList=[]
   for ii in range(32):
      if ii<len(zoneList) :
         if (zoneList[ii]>=lowSkewZones[programName][0] and zoneList[ii]<=lowSkewZones[programName][1]):
            revs_ii = (internalRetryRevs[programName]['LowSkew'][headType] << 8) + initialRevs[programName]['LowSkew'][headType]
         else:
            revs_ii = (internalRetryRevs[programName]['HighSkew'][headType] << 8) + initialRevs[programName]['HighSkew'][headType]
         revsList.append( revs_ii )
      else:
         revs_ii = (internalRetryRevs[programName]['HighSkew'][headType] << 8) + initialRevs[programName]['HighSkew'][headType]
         revsList.append( revs_ii)
   baseIPD2Prm_135["REVS_BY_ZONE"] = revsList

   for ii in range(32-len(zoneList)) :
      zoneList.append(-1)
   baseIPD2Prm_135['ZONE_ORDER']=zoneList

   ##################################### FastIO Parameters  ##################################################
   if headType == 'RHO':
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

   baseIPD2Prm_135['B_WR_NUM_WEDGES'     ] = (fastIO_B)
   baseIPD2Prm_135['E_POST_RD_NUM_WEDGES'] = (fastIO_E)

   #if headType in ['RHO']:
   #   MinAGCBin=10
   #else:
   MinAGCBin=0
   EndFreq = int(Nyquist + PESFr)

   if (intHeadRetryCntr > 0):
      if (SearchOptions['ShutOffHighFreqDuringGlobalRetries'][programName][headType] == 1):
         EndFreq = int(10 * PESFr)
      if (SearchOptions['IncreaseAGCMinFreqDuringGlobalRetries'][programName][headType] == 1):
         if headType in ['RHO']:
            MinAGCBin=20
         else:
            MinAGCBin=10

   MinAGCBinWithBLJ=MinAGCBin+10


   baseIPD2Prm_135['M0_FREQ_RANGE'       ] = (0,EndFreq)   #Full spectra PES Freq Range                     0x1
   baseIPD2Prm_135['M1_FREQ_RANGE'       ] = (0,int(Nyquist + AGCFr))   #Full spectra AGC Freq Range        0x2
   baseIPD2Prm_135['M2_FREQ_RANGE'       ] = (0,int(Nyquist + LFPESFr)) #Full spectra LF PES Freq Range   0x4
   baseIPD2Prm_135['M3_FREQ_RANGE'       ] = (int(AGCFr*MinAGCBin),int(Nyquist + AGCFr))   #AGC Freq Range sans LF          0x8
   baseIPD2Prm_135['M4_FREQ_RANGE'       ] = (0, EndFreq)   #Full spectra VCM Freq Range                             0x10
   baseIPD2Prm_135['M5_FREQ_RANGE'       ] = (int(AGCFr*MinAGCBinWithBLJ),int(Nyquist + AGCFr))   #AGC when BLJ is detected          0x20

   baseIPD2Prm_135['SECTOR_RANGE1'       ] = (SpokesPerRev - PESDftN,SpokesPerRev)  #HF PES
   baseIPD2Prm_135['SECTOR_RANGE2'       ] = (AGCEndSpoke-AGCDftN,AGCEndSpoke)  #AGC
   baseIPD2Prm_135['SECTOR_RANGE3'       ] = (fastIO_B , SpokesPerRev)  #LF PES



   ########################################################################################################################################################################
   #
   #
   #           Return Completed Dictionary
   #
   #
   ########################################################################################################################################################################

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
