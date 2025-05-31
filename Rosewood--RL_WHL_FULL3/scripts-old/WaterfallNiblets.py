#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Waterfall Niblets for Luxor programs - Grenada, Carib,
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/27 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/WaterfallNiblets.py $
# $Revision: #22 $
# $DateTime: 2016/12/27 23:52:43 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/WaterfallNiblets.py#22 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from TestParamExtractor import TP
from Test_Switches import testSwitch

CapPerHd_Rap = TP.VbarCapacityGBPerHead

if testSwitch.SMR:
   if testSwitch.FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND:
      ## Applicable for Chengai ##
      MC_SIZE              = 28.0
      MC_SIZE_WTF          = 16.0   # need to finalize
      MC_WTF_SPEC          = 1.0    # need to finalize
      tracks_per_band_wtf  = 1      # One track per band across zone
      MC_SIZE_RAP_WTF      = 15.0   # need to finalize
      MC_SIZE_RAP          = 25.0   # need to finalize
      MC_SIZE_15G          = 17.0   # dummy
   elif testSwitch.FE_0298709_348085_P_PRECISE_MEDIA_CACHE_SIZE_ALLOCATION:
      # Here are the equation get from the F3 firmware. Need to sync up to their code.
      def CalcMCSize(RequiredMC = 25, AddPad = 0.0):
         MEDIA_CACHE_SIZE                         =   RequiredMC
         MEDIA_CACHE_PARTIION_SUPER_PARITY_BYTES  =   0.25 * 1024000000
         MEDIA_CACHE_PARTITION_CAPACITY_IN_BYTES  =   MEDIA_CACHE_SIZE * 1024000000
         MEDIA_CACHE_SCRATCHPAD_CAPACITY_IN_BYTES =   192675840
         DOS_STE_SCAN_MAX_CYL_DEFAULT             =   15
         NumSecsPerTrack                          =   530         # Assume the highest bpipick can go. 
         sector_size                              =   4096
         one_band_size                            =   NumSecsPerTrack * TP.tracksPerBand * sector_size
         MC_GuardTracksCapacityPerHead            =   NumSecsPerTrack * ( ( 5 * DOS_STE_SCAN_MAX_CYL_DEFAULT + 2 )*sector_size / TP.numHeads ) # sector
         MC_ReqCapacityPerHead                    =   ( MEDIA_CACHE_PARTITION_CAPACITY_IN_BYTES + MEDIA_CACHE_PARTIION_SUPER_PARITY_BYTES + MEDIA_CACHE_SCRATCHPAD_CAPACITY_IN_BYTES ) / TP.numHeads
         MC_SIZE                                  =   ( MC_ReqCapacityPerHead + MC_GuardTracksCapacityPerHead + one_band_size ) * TP.numHeads/1e9
         MC_SIZE                                  =   MC_SIZE + AddPad
         return MC_SIZE

      MC_SIZE     = CalcMCSize(25)        # 26.4
      MC_SIZE_15G = CalcMCSize(15, 0.2)   # 16.3 additional 0.2G as req from F3

   else:
      MC_SIZE = 28.0
      MC_SIZE_15G = 17.0 # dummy
      
else:
   MC_SIZE = 0.0

if testSwitch.FE_0308542_348085_P_DESPERADO_3: 
   ISO_BAND_SIZE         = (128 * 1024 * 1024 )/1e6    # In M                                  
   COPY_FORWARD_OVERHEAD = 10.0 * ISO_BAND_SIZE/1000.0   
   Floor   =  ( 10.0 * 1024 * 1024 * 1024) /1e9 
   Annex   =  ( 40.0 * 1024 * 1024 * 1024) /1e9
   MC_SIZE =  ( Floor * 1.04 ) + ( Annex * 0.04 )
else:
   COPY_FORWARD_OVERHEAD = 0

CapPerHd = {
   '100G1H'    : 100.0 + MC_SIZE_15G/1 + COPY_FORWARD_OVERHEAD/1,
   '300G1H'    : 300.0 + MC_SIZE_15G/1 + COPY_FORWARD_OVERHEAD/1,
   '2000G'     : 500.0 + MC_SIZE_15G/4 + COPY_FORWARD_OVERHEAD/4,
   '2000G15'   : 500.0 + MC_SIZE_15G/4 + COPY_FORWARD_OVERHEAD/4,   
   '1500G'     : 375.0 + MC_SIZE_15G/4 + COPY_FORWARD_OVERHEAD/4,
   '1500G3H'   : 500.0 + MC_SIZE_15G/3 + COPY_FORWARD_OVERHEAD/3,
   '1000G'     : 500.0 + MC_SIZE_15G/2 + COPY_FORWARD_OVERHEAD/2,
   '1000G15'   : 500.0 + MC_SIZE_15G/2 + COPY_FORWARD_OVERHEAD/2,
   '1000G3H'   : 333.4 + MC_SIZE_15G/3 + COPY_FORWARD_OVERHEAD/3, 
   '970G'      : 485.0 + MC_SIZE_15G/2 + COPY_FORWARD_OVERHEAD/2,
   '750G'      : 375.0 + MC_SIZE_15G/2 + COPY_FORWARD_OVERHEAD/2,

   '1000G4H'   : 250.0 + MC_SIZE_15G/4 + COPY_FORWARD_OVERHEAD/4,
   '500G'      : 250.0 + MC_SIZE_15G/2 + COPY_FORWARD_OVERHEAD/2,
   '500G15'    : 250.0 + MC_SIZE_15G/2 + COPY_FORWARD_OVERHEAD/2,
   '500G1H'    : 500.0 + MC_SIZE_15G/1 + COPY_FORWARD_OVERHEAD/1,
   '375G1H'    : 375.0 + MC_SIZE_15G/1 + COPY_FORWARD_OVERHEAD/1,

   '1950G4H'   : 487.5 + MC_SIZE/4 + COPY_FORWARD_OVERHEAD/4,   
   '1860G4H'   : 465.0 + MC_SIZE/4 + COPY_FORWARD_OVERHEAD/4,
   '1740G4H'   : 435.0 + MC_SIZE/4 + COPY_FORWARD_OVERHEAD/4,
   '1620G4H'   : 405.0 + MC_SIZE/4 + COPY_FORWARD_OVERHEAD/4,

   '930G2H'    : 465.0 + MC_SIZE/2 + COPY_FORWARD_OVERHEAD/2,
   '870G2H'    : 435.0 + MC_SIZE/2 + COPY_FORWARD_OVERHEAD/2,
   '810G2H'    : 405.0 + MC_SIZE/2 + COPY_FORWARD_OVERHEAD/2,

   '640G2H'    : 320.0 + MC_SIZE/2 + COPY_FORWARD_OVERHEAD/2,
   '680G2H'    : 340.0 + MC_SIZE/2 + COPY_FORWARD_OVERHEAD/2,
   '720G2H'    : 360.0 + MC_SIZE/2 + COPY_FORWARD_OVERHEAD/2,
}

#if testSwitch.FE_0243269_348085_FIX_BPI_TPI_WATERFALL:
#   CapPerHd.update({'640G'   : 320.0 + MC_SIZE/2,})
#
#if testSwitch.FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND:
#   if testSwitch.CHENGAI: ## Chengai WTF Drives 500G ##
#      CapPerHd.update({'500G' : 250.0 + MC_SIZE_WTF/2,})

sectorFormat_4096                = '4096'
if testSwitch.FE_0297446_348429_P_PRECISE_PARITY_ALLOCATION:
   PBA_TO_LBA_SCALER                = 0.996 # 0.4% spare # 0.5% spare, parity will be calculated on the fly
else:
   PBA_TO_LBA_SCALER                = 0.985 # 0.5% spare, 1% parity
if testSwitch.FE_0268922_504159_VBAR_ATI_ONLY_RELAX_DIR:
   Native_TPI_MARGIN_THRESHOLD = 0 #dont let ump zone to stress, go one relax direction
   SBS_TPI_MARGIN_THRESHOLD    = 0 #dont let ump zone to stress, go one relax direction
else:
   Native_TPI_MARGIN_THRESHOLD = -0.08 #allowed to stress, but not beyond 8%
   SBS_TPI_MARGIN_THRESHOLD    = -0.08 #allowed to stress, but not beyond 8%
Rezone_TPI_MARGIN_THRESHOLD      = 0.0

if testSwitch.FE_0254388_504159_SQZ_BPIC:
   Native_BPI_MARGIN_THRESHOLD = TP.BPI_Squeeze_PushLimit#-0.05 #capped by 5% push per Haoji/RSS request
else: Native_BPI_MARGIN_THRESHOLD = 0

#put variable as a string for dynamically extrach value based on the current ump zone and mc zones
SMRTPIMarginThreshold_Native     = "[(zn in TP.UMP_ZONE[objDut.numZones]) and (testSwitch.RUN_ATI_IN_VBAR and %f or 0.0) or 0.0 for zn in xrange(objDut.numZones)]" % (Native_TPI_MARGIN_THRESHOLD)
SMRTPIMarginThreshold_SBS        = "[(zn in TP.UMP_ZONE[objDut.numZones]) and (testSwitch.RUN_ATI_IN_VBAR and %f or 0.0) or 0.0 for zn in xrange(objDut.numZones)]" % (SBS_TPI_MARGIN_THRESHOLD)
#Native_BPI_MARGIN_THRESHOLD_SMR  = "[(zn in [0,8,9,10,144,145,146,147,148]) and -0.03 or (not zn in TP.UMP_ZONE[objDut.numZones]) and %f or 0.10 for zn in xrange(objDut.numZones)]" % (Native_BPI_MARGIN_THRESHOLD)
if testSwitch.FE_0325893_348429_P_OD_ID_RESONANCE_MARGIN:
   Native_BPI_MARGIN_THRESHOLD_SMR  = "[(zn in [objDut.numZones-1]) and 0.00000001 or (zn in TP.MC_ZONE) and TP.BPI_Squeeze_PushLimit_MC or (zn in [0,8,9,10,144,145,146,147,148]) and TP.BPI_Squeeze_PushLimit_Res or (not zn in TP.UMP_ZONE[objDut.numZones]) and %f or TP.BPIM_FIX_BACKOFF for zn in xrange(objDut.numZones)]" % (Native_BPI_MARGIN_THRESHOLD)
else:
   Native_BPI_MARGIN_THRESHOLD_SMR  = "[(zn in [objDut.numZones-1]) and 0.00000001 or (zn in TP.MC_ZONE) and TP.BPI_Squeeze_PushLimit_MC or (not zn in TP.UMP_ZONE[objDut.numZones]) and %f or TP.BPIM_FIX_BACKOFF for zn in xrange(objDut.numZones)]" % (Native_BPI_MARGIN_THRESHOLD)
tracks_per_band                  = "[(zn in TP.UMP_ZONE[objDut.numZones]) and 1 or TP.tracksPerBand for zn in xrange(objDut.numZones)]"

### overriding the SBS_TPI_MARGIN_THRESHOLD to let remaining SBS niblet take effect###
if testSwitch.SMR:
   SBS_TPI_MARGIN_THRESHOLD = SMRTPIMarginThreshold_SBS
######################################################################################

Native_ATI_TARGET_OTF_BER = 5.9

if testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
    Native_ATI_TARGET_OTF_BER = 6.9
    SBS_ATI_TARGET_OTF_BER    = 6.2
else:
    Native_ATI_TARGET_OTF_BER = 5.9
    SBS_ATI_TARGET_OTF_BER    = 5.2

TPI_MARGIN_FACTOR_DEFAULT = 0.99  #give more margin to KARNAK

OD_THRUPUT_PERCENT    = 0.93
ID_THRUPUT_PERCENT    = 0.90
       
VbarNiblet_Base = {
   'DRIVE_RPM'                      : 5400,
   'SECTOR_FORMAT'                  : sectorFormat_4096,
   'PBA_TO_LBA_SCALER'              : PBA_TO_LBA_SCALER,
   'NUM_HEADS'                      : TP.numHeads, # Number of heads utilized to make capacity for nib
   'BPI_MINIMUM_AVERAGE'            : 0.7,         # Minimum Mathematical Average of BPI Capabilities for Capacity- Used to guarantee performance
   'BPI_MAXIMUM_AVERAGE'            : 1.4,         # Maximum Mathematical Average of BPI Capabilities for Capacity- Used to guarantee performance
   'TPI_MARGIN_FACTOR'              : TPI_MARGIN_FACTOR_DEFAULT,         # % Tradoff in TPI for each BPI adjustment during waterfall picking
   'BPI_MARGIN_THRESHOLD'           : {
      31  : [0.02]*2 + [0] * 27  + [0.02]*2,
      60  : [0.02]*2 + [0] * 56  + [0.02]*2,
      120 : [0.02]*2 + [0] * 116 + [0.02]*2,
      150 : [0.02]*2 + [0] * 146 + [0.02]*2,
      180 : [0.02]*2 + [0] * 176 + [0.02]*2,
   },
   'TPI_MARGIN_THRESHOLD'           : Native_TPI_MARGIN_THRESHOLD,        # Minimum TPI margin required for nib to be picked
   'BPI_MEASUREMENT_MARGIN'         : 0.0,         # BPI offset in actual capabilty to measured capability
   'TPI_MEASUREMENT_MARGIN'         : 0,        # TPI offset in actual capabilty to measured capability
   'WRITE_FAULT_THRESHOLD'          : 0.08,        # Value to be subtracted when measurements are scaled
   'TPI_OVERCOMP_FACTOR'            : 0.95,        # % Change in TPI format (in % capacity) when making compromises for waterfall
   'BPI_OVERCOMP_FACTOR'            : 1.0,        # % Change in BPI format (in % capacity) when making compromises for waterfall
   'BPI_TPI_OVERCOMP_FACTOR'        : 0.95,        # % Adjustment to de-couple the correlation between BPI and TPI
   "TPI_ROUNDING_FACTOR"            : 100.0,   # Round up or down for TPI
   #"TPI_MARGIN_ADJUSTMENT_BY_ZONE" : [0.03, 0.03, 0.03, 0.02, 0.02, 0.02, 0.01, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
   #"BPI_MARGIN_ADJUSTMENT_BY_ZONE" : [0.02, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],      

   'FORCE_RESTART_NEXT_WTF'         : 0,
   'RPM_RESTART_NEXT_WTF'           : 1, 
   
   'VWFT_SLOPE'                     : 100,
   'VWFT_ADJUSTMENT_CRITERIA'       : 0.02,
   'VWFT_MAX_ALLOWED_ADJUSTMENT'    : -2,
   'VWFT_MIN_ALLOWED_OCLIM'         : 12,
   'VbarHMSBPIMTAdjust'             : -0.02,
   'VbarHMSTPIMTAdjust'             : -0.01,
   'VbarHMSMinZoneSpec'             : 0.0,
   'VbarHMSMinHeadSpec'             : 0.0,
   "ATI_TARGET_OTF_BER"             : Native_ATI_TARGET_OTF_BER,
   "OD_THRUPUT_LIMIT"               : 80.0,
   "ID_THRUPUT_LIMIT"               : 40.0,
   "OD_THRUPUT_PERCENT"             : None,
   "ID_THRUPUT_PERCENT"             : None,
   "THRUPUT_BY_HD"                  : 0,
   'MEDIA_CACHE_CAPACITY'           : MC_SIZE_15G,
   'MEDIA_CACHE_CAPACITY_SPEC'      : 16,
   'MEDIA_CACHE_SIZE_RAP'           : 150, # 25.0G RAP format in 0.1G precision
   'UMP_CAPACITY'                   : 1,
   'UMP_CAPACITY_SPEC'              : 1,
   'UMP_CAPACITY_RAP'               : 1, # program to 25GB
   'NATIVE_DRV'                     : 0,  # 1: native; 0: non-native drv
   'Adaptive_Guard_Band_Margin'     : 0.5
}

if testSwitch.FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND: 
   VbarNiblet_Base.update({ 
   'MEDIA_CACHE_SIZE_RAP'           : MC_SIZE_RAP,
   })

if testSwitch.VBAR_HMS_V4:
   VbarNiblet_Base.update({
      'VbarHMSBPIMTAdjust' : -0.30,
      'VbarHMSTPIMTAdjust' : -0.01,
      'VbarHMSMinZoneSpec' : 0.35, # AngsanaH Relax Spec
      'VbarHMSMinHeadSpec' : 1.8
   })
if testSwitch.CONDITIONAL_RUN_HMS:
   VbarNiblet_Base.update({
      'VbarHMSMinHeadSpec' : 1.2
   })

if testSwitch.FE_0338929_348429_P_ENABLE_SQZ_HMS:
   VbarNiblet_Base.update({
      'VbarHMSMinZoneSpec' : 0.70, # Squeeze HMS
   })
if testSwitch.SMR:
   if testSwitch.VBAR_2D:
      if testSwitch.FE_0246199_504159_INJECT_VCM_NOISE:
         wtf_slim_track = 0.00 #using vcm noise to replace wtf
      else:
         startZoneMC = testSwitch.ADAPTIVE_GUARD_BAND and 1 or 0
         if testSwitch.FE_348085_P_NEW_UMP_MC_ZONE_LAYOUT: 
            wtf_slim_track = "[TP.MS_WFT] * ( sorted(TP.UMP_ZONE[objDut.numZones])[-2] + 1 ) + [TP.MC_WFT]*5 + [TP.MS_WFT]*(objDut.numZones - (( sorted(TP.UMP_ZONE[objDut.numZones])[-2] + 1 ) + 5))" 
         elif testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
            wtf_slim_track = "[TP.MS_WFT] * %d + [TP.MC_WFT] *(TP.numMC) + [TP.MS_WFT] * (objDut.numZones - (TP.numMC + 1))" % (startZoneMC)
         else:
            wtf_slim_track = "[TP.MS_WFT] * %d + [TP.MC_WFT] *(min(TP.UMP_ZONE[objDut.numZones])-%d) + [TP.MS_WFT] * (objDut.numZones- min(TP.UMP_ZONE[objDut.numZones]))" % (startZoneMC, startZoneMC)
   else: wtf_slim_track = 0.08
   
   VbarNiblet_Base.update({
      'WRITE_FAULT_THRESHOLD'            : 0.12,
      'TRACKS_PER_BAND'                  : tracks_per_band,
      'BPI_MARGIN_THRESHOLD'             : Native_BPI_MARGIN_THRESHOLD_SMR,
      'TPI_MARGIN_THRESHOLD'             : SMRTPIMarginThreshold_Native,
   })
   
   VbarNiblet_Base['WRITE_FAULT_THRESHOLD_SLIM_TRACK'] = wtf_slim_track

   if testSwitch.FE_0302539_348429_P_ENABLE_VBAR_OC2:
      if testSwitch.FE_348085_P_NEW_UMP_MC_ZONE_LAYOUT: 
         VbarNiblet_Base['TPI_OC2COMPENSATION'] = "[TP.TPI_OC2COMPENSATION] * ( sorted(TP.UMP_ZONE[objDut.numZones])[-2] + 1 )  + [0.00] * 5 + [TP.TPI_OC2COMPENSATION] * (objDut.numZones - (( sorted(TP.UMP_ZONE[objDut.numZones])[-2] + 1 ) + 5))"
         VbarNiblet_Base['BPI_OC2COMPENSATION'] = "[0.00] * ( sorted(TP.UMP_ZONE[objDut.numZones])[-2] + 1 )  + [0.00] * 5 + [0.00] * (objDut.numZones - (( sorted(TP.UMP_ZONE[objDut.numZones])[-2] + 1 ) + 5))"
         Additional_TPI_OC2_Margin = "[0.00] * ( sorted(TP.UMP_ZONE[objDut.numZones])[-2] + 1 )  + [0.00] * 5 + [0.00] * (objDut.numZones - (( sorted(TP.UMP_ZONE[objDut.numZones])[-2] + 1 ) + 5))"
         Additional_TPI_OC2_Margin_ret = "[TP.ADD_TPI_OC2COMPENSATION] * ( sorted(TP.UMP_ZONE[objDut.numZones])[-2] + 1 )  + [0.00] * 5 + [TP.ADD_TPI_OC2COMPENSATION] * (objDut.numZones - (( sorted(TP.UMP_ZONE[objDut.numZones])[-2] + 1 ) + 5))"
      elif testSwitch.FE_0385234_356688_P_MULTI_ID_UMP:
         VbarNiblet_Base['TPI_OC2COMPENSATION'] = "[TP.TPI_OC2COMPENSATION] * %d + [0.00] *(TP.numMC) + [TP.TPI_OC2COMPENSATION] * (objDut.numZones - (TP.numMC + 1))" % (startZoneMC)
         VbarNiblet_Base['BPI_OC2COMPENSATION'] = "[0.00] * %d + [0.00] *(TP.numMC) + [0.00] * (objDut.numZones - (TP.numMC + 1))" % (startZoneMC)
         Additional_TPI_OC2_Margin = "[0.00] * %d + [0.00] *(TP.numMC) + [0.00] * (objDut.numZones - (TP.numMC + 1))" % (startZoneMC)
         Additional_TPI_OC2_Margin_ret = "[TP.ADD_TPI_OC2COMPENSATION] * %d + [0.00] *(TP.numMC) + [TP.ADD_TPI_OC2COMPENSATION] * (objDut.numZones - (TP.numMC + 1))" % (startZoneMC)
      else:
         VbarNiblet_Base['TPI_OC2COMPENSATION'] = "[TP.TPI_OC2COMPENSATION] * %d + [0.00] *(min(TP.UMP_ZONE[objDut.numZones])-%d) + [TP.TPI_OC2COMPENSATION] * (objDut.numZones- min(TP.UMP_ZONE[objDut.numZones]))" % (startZoneMC, startZoneMC)
         VbarNiblet_Base['BPI_OC2COMPENSATION'] = "[0.00] * %d + [0.00] *(min(TP.UMP_ZONE[objDut.numZones])-%d) + [0.00] * (objDut.numZones- min(TP.UMP_ZONE[objDut.numZones]))" % (startZoneMC, startZoneMC)
         Additional_TPI_OC2_Margin = "[0.00] * %d + [0.00] *(min(TP.UMP_ZONE[objDut.numZones])-%d) + [0.00] * (objDut.numZones- min(TP.UMP_ZONE[objDut.numZones]))" % (startZoneMC, startZoneMC)
         Additional_TPI_OC2_Margin_ret = "[TP.ADD_TPI_OC2COMPENSATION] * %d + [0.00] *(min(TP.UMP_ZONE[objDut.numZones])-%d) + [TP.ADD_TPI_OC2COMPENSATION] * (objDut.numZones- min(TP.UMP_ZONE[objDut.numZones]))" % (startZoneMC, startZoneMC)
      VbarNiblet_Base['ADDITIONAL_TPI_OC2_MARGIN'] = Additional_TPI_OC2_Margin
      
      VbarNiblet_Base['ADDITIONAL_BPI_OC2_MARGIN'] = "[0 for zn in xrange(objDut.numZones)]"
      if testSwitch.FE_0325893_348429_P_OD_ID_RESONANCE_MARGIN:
         Additional_BPI_OC2_Margin_ret = "[(zn not in TP.MC_ZONE + TP.UMP_ZONE[objDut.numZones] + [objDut.numZones-1]) and TP.ADD_BPI_OC2COMPENSATION or 0 for zn in xrange(objDut.numZones)]"
      else:
         Additional_BPI_OC2_Margin_ret = "[(zn not in TP.MC_ZONE + TP.UMP_ZONE[objDut.numZones] + [objDut.numZones-1]) and TP.ADD_BPI_OC2COMPENSATION or 0 for zn in xrange(objDut.numZones)]"
      
   VbarNiblet_Base['TPI_OTC_MARGIN_THRESHOLD'] = "[(zn in [objDut.numZones-1]) and 0.00000001 or (zn in TP.MC_ZONE) and TP.TPIM_Intra_PushLimit_MC or (zn in [0,8,9,10,144,145,146,147,148]) and TP.TPIM_Intra_PushLimit_Res or (not zn in TP.UMP_ZONE[objDut.numZones]) and TP.TPIM_Intra_PushLimit or 0.00000001 for zn in xrange(objDut.numZones)]"

   if testSwitch.FE_0308542_348085_P_DESPERADO_3: 
      VbarNiblet_Base.update({
         'ISO_BAND_SIZE'         : ISO_BAND_SIZE,
         'COPY_FORWARD_OVERHEAD' : COPY_FORWARD_OVERHEAD,
      })
# ------ HAMR related. Starwood7 1D Eval Capacity -------
Native_100G_1H_5400        = VbarNiblet_Base.copy()
Native_300G_1H_5400        = VbarNiblet_Base.copy()

# ------ Rosewood7 1D Capacity -------
Native_1000G_2H_5400       = VbarNiblet_Base.copy()
Native_1000G_2H_5400_MS    = VbarNiblet_Base.copy()
Native_1000G_2H_5400_15G   = VbarNiblet_Base.copy()
Native_970G_2H_5400        = VbarNiblet_Base.copy()
Rezone_750G_2H_5400        = VbarNiblet_Base.copy()
Native_930G_2H_5400        = VbarNiblet_Base.copy()
Native_870G_2H_5400        = VbarNiblet_Base.copy()
Native_810G_2H_5400        = VbarNiblet_Base.copy()
Native_500G_2H_5400        = VbarNiblet_Base.copy()
Rezone_500G_2H_5400_SBS    = VbarNiblet_Base.copy()

# ------ Rosewood7 2D Capacity -------
Native_2000G_4H_5400       = VbarNiblet_Base.copy()
Native_2000G_4H_5400_MS    = VbarNiblet_Base.copy()
Native_2000G_4H_5400_SBS   = VbarNiblet_Base.copy()
Native_2000G_4H_5400_15G   = VbarNiblet_Base.copy()
Rezone_1500G_4H_5400       = VbarNiblet_Base.copy()
Native_1000G_4H_5400_SBS   = VbarNiblet_Base.copy()
Rezone_1000G_4H_5400_SBS   = VbarNiblet_Base.copy()
Native_1860G_4H_5400       = VbarNiblet_Base.copy()
Native_1950G_4H_5400       = VbarNiblet_Base.copy()
Native_1740G_4H_5400       = VbarNiblet_Base.copy()
Native_1620G_4H_5400       = VbarNiblet_Base.copy()
Depop_1500G_3H_5400        = VbarNiblet_Base.copy()
Depop_1500G_3H_5400_SBS    = VbarNiblet_Base.copy()

# ------ Rosewood7 1D/2D 1-head Capacity -------
Native_500G_1H_5400        = VbarNiblet_Base.copy()
Native_500G_1H_5400_SBS    = VbarNiblet_Base.copy()
Rezone_375G_1H_5400        = VbarNiblet_Base.copy()

# ------ Rosewood7 2D 3-head Capacity -------
Static_Depop_1000G_3H_5400 = VbarNiblet_Base.copy()      # RW7 Common Part Number for 1TB Support
Static_Depop_1000G_3H_5400_15G = VbarNiblet_Base.copy()      # RW7 Common Part Number for 1TB Support

# ------ Chengai-Mule 1D Capacity -------
Native_750G_2H_5400        = VbarNiblet_Base.copy()
Native_750G_2H_5400_SBS    = VbarNiblet_Base.copy()
Rezone_500G_2H_5400        = VbarNiblet_Base.copy()
Rezone_500G_2H_5400_15G    = VbarNiblet_Base.copy()


#Chengai niblets
Native_640G_2H_5400        = VbarNiblet_Base.copy()
Native_680G_2H_5400        = VbarNiblet_Base.copy()
Native_720G_2H_5400        = VbarNiblet_Base.copy()


# ------ HAMR related. Starwood7 1D Eval Capacity -------
Native_100G_1H_5400.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['100G1H'] * 1,
   'CAPACITY_TARGET'       : CapPerHd['100G1H'] / CapPerHd_Rap,
   'NUM_HEADS'             : 1,
})
Native_300G_1H_5400.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['300G1H'] * 1,
   'CAPACITY_TARGET'       : CapPerHd['300G1H'] / CapPerHd_Rap,
   'NUM_HEADS'             : 1,
})
# ------ Rosewood7 1D Capacity -------
Native_1000G_2H_5400.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['1000G'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['1000G'] / CapPerHd_Rap,
   'NUM_HEADS'             : 2,
   'NATIVE_DRV'            : 1,
})
Native_1000G_2H_5400_MS.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['1000G'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['1000G'] / CapPerHd_Rap,
   'NUM_HEADS'             : 2,
   'NATIVE_DRV'            : 1,
   'TPI_OTC_MARGIN_THRESHOLD':  "[(zn in [objDut.numZones-1]) and 0.00000001 or (zn in TP.MC_ZONE) and TP.TPIM_Intra_PushLimit_MC or (zn in [0,8,9,10,144,145,146,147,148]) and TP.TPIM_Intra_PushLimit_Res or (not zn in TP.UMP_ZONE[objDut.numZones]) and -0.025 or 0.00000001 for zn in xrange(objDut.numZones)]",
})
Native_1000G_2H_5400_15G.update({
   'DRIVE_CAPACITY'        : CapPerHd['1000G15'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['1000G15'] / CapPerHd_Rap,
   'NUM_HEADS'             : 2,
   # 'ATI_TARGET_OTF_BER'    : SBS_ATI_TARGET_OTF_BER,
   # 'TPI_MARGIN_THRESHOLD'  : SBS_TPI_MARGIN_THRESHOLD,
   'ADDITIONAL_TPI_OC2_MARGIN' : Additional_TPI_OC2_Margin_ret,
   'MEDIA_CACHE_CAPACITY'           : MC_SIZE_15G,
   'MEDIA_CACHE_CAPACITY_SPEC'      : 16,
   'MEDIA_CACHE_SIZE_RAP'           : 150, # program MC to 15.0GB
   'NATIVE_DRV'            : 1,
   'ADDITIONAL_BPI_OC2_MARGIN'      : Additional_BPI_OC2_Margin_ret,
})

Native_970G_2H_5400.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['970G'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['970G'] / CapPerHd_Rap,
   'NUM_HEADS'             : 2,
   'NATIVE_DRV'            : 1,
})
Rezone_750G_2H_5400.update({
   'DRIVE_CAPACITY'        : CapPerHd['750G'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['750G'] / CapPerHd_Rap,
   'NUM_HEADS'             : 2,
})
Native_930G_2H_5400.update({
   'DRIVE_CAPACITY'        : CapPerHd['930G2H'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['930G2H']/CapPerHd_Rap,
   'NUM_HEADS'             : 2,
})
Native_870G_2H_5400.update({
   'DRIVE_CAPACITY'        : CapPerHd['870G2H'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['870G2H']/CapPerHd_Rap,
   'NUM_HEADS'             : 2,
})
Native_810G_2H_5400.update({
   'DRIVE_CAPACITY'        : CapPerHd['810G2H'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['810G2H']/CapPerHd_Rap,
   'NUM_HEADS'             : 2,
})
Native_500G_2H_5400.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['500G'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['500G']/CapPerHd_Rap,
   'NUM_HEADS'             : 2,
   'OD_THRUPUT_PERCENT'    : OD_THRUPUT_PERCENT,
   'ID_THRUPUT_PERCENT'    : ID_THRUPUT_PERCENT,
   'THRUPUT_BY_HD'         : 51.5,
})
Rezone_500G_2H_5400_SBS.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['500G'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['500G']/CapPerHd_Rap,
   'NUM_HEADS'             : 2,
   'OD_THRUPUT_PERCENT'    : OD_THRUPUT_PERCENT,
   'ID_THRUPUT_PERCENT'    : ID_THRUPUT_PERCENT,
})

# ------ Rosewood7 2D Capacity -------
Native_2000G_4H_5400.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['2000G'] * 4,
   'CAPACITY_TARGET'       : CapPerHd['2000G'] / CapPerHd_Rap,
   'NUM_HEADS'             : 4,
   'NATIVE_DRV'            : 1,
})
Native_2000G_4H_5400_MS.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['2000G'] * 4,
   'CAPACITY_TARGET'       : CapPerHd['2000G'] / CapPerHd_Rap,
   'NUM_HEADS'             : 4,
   'NATIVE_DRV'            : 1,
   'TPI_OTC_MARGIN_THRESHOLD':  "[(zn in [objDut.numZones-1]) and 0.00000001 or (zn in TP.MC_ZONE) and TP.TPIM_Intra_PushLimit_MC or (zn in [0,8,9,10,144,145,146,147,148]) and TP.TPIM_Intra_PushLimit_Res or (not zn in TP.UMP_ZONE[objDut.numZones]) and -0.025 or 0.00000001 for zn in xrange(objDut.numZones)]",
})
Native_2000G_4H_5400_SBS.update({
   'DRIVE_CAPACITY'        : CapPerHd['2000G'] * 4,
   'CAPACITY_TARGET'       : CapPerHd['2000G'] / CapPerHd_Rap,
   'NUM_HEADS'             : 4,
   'ATI_TARGET_OTF_BER'    : SBS_ATI_TARGET_OTF_BER,
   'TPI_MARGIN_THRESHOLD'  : SBS_TPI_MARGIN_THRESHOLD,
   'ADDITIONAL_TPI_OC2_MARGIN' : Additional_TPI_OC2_Margin_ret,
})
Native_2000G_4H_5400_15G.update({
   'DRIVE_CAPACITY'        : CapPerHd['2000G15'] * 4,
   'CAPACITY_TARGET'       : CapPerHd['2000G15'] / CapPerHd_Rap,
   'NUM_HEADS'             : 4,
   'ATI_TARGET_OTF_BER'    : SBS_ATI_TARGET_OTF_BER,
   'TPI_MARGIN_THRESHOLD'  : SBS_TPI_MARGIN_THRESHOLD,
   'ADDITIONAL_TPI_OC2_MARGIN' : Additional_TPI_OC2_Margin_ret,
   'NATIVE_DRV'            : 1,
   'ADDITIONAL_BPI_OC2_MARGIN'      : Additional_BPI_OC2_Margin_ret,
})
Rezone_1500G_4H_5400.update({
   'DRIVE_CAPACITY'        : CapPerHd['1500G'] * 4,
   'CAPACITY_TARGET'       : CapPerHd['1500G'] / CapPerHd_Rap,
   'NUM_HEADS'             : 4,
   'OD_THRUPUT_PERCENT'    : OD_THRUPUT_PERCENT,
   'ID_THRUPUT_PERCENT'    : ID_THRUPUT_PERCENT,
})
Native_1000G_4H_5400_SBS.update({
   'DRIVE_CAPACITY'        : CapPerHd['1000G4H'] * 4,
   'CAPACITY_TARGET'       : CapPerHd['1000G4H'] / CapPerHd_Rap,
   'NUM_HEADS'             : 4,
   'OD_THRUPUT_PERCENT'    : OD_THRUPUT_PERCENT,
   'ID_THRUPUT_PERCENT'    : ID_THRUPUT_PERCENT,
})
Rezone_1000G_4H_5400_SBS.update({
   'DRIVE_CAPACITY'        : CapPerHd['1000G4H'] * 4,
   'CAPACITY_TARGET'       : CapPerHd['1000G4H'] / CapPerHd_Rap,
   'NUM_HEADS'             : 4,
   'OD_THRUPUT_PERCENT'    : OD_THRUPUT_PERCENT,
   'ID_THRUPUT_PERCENT'    : ID_THRUPUT_PERCENT,
})
Depop_1500G_3H_5400.update({
   'DRIVE_CAPACITY'        : CapPerHd['1500G3H'] * 3,
   'CAPACITY_TARGET'       : CapPerHd['1500G3H'] / CapPerHd_Rap,
   'NUM_HEADS'             : 3,
   'NATIVE_DRV'            : 1,
})
Depop_1500G_3H_5400_SBS.update({
   'DRIVE_CAPACITY'        : CapPerHd['1500G3H'] * 3,
   'CAPACITY_TARGET'       : CapPerHd['1500G3H'] / CapPerHd_Rap,
   'NUM_HEADS'             : 3,
   'ATI_TARGET_OTF_BER'    : SBS_ATI_TARGET_OTF_BER,
   'TPI_MARGIN_THRESHOLD'  : SBS_TPI_MARGIN_THRESHOLD,
   'NATIVE_DRV'            : 1,
})
Native_1860G_4H_5400.update({
   'DRIVE_CAPACITY'        : CapPerHd['1860G4H'] * 4,
   'CAPACITY_TARGET'       : CapPerHd['1860G4H']/CapPerHd_Rap,
   'NUM_HEADS'             : 4,
})

Native_1950G_4H_5400.update({
   'DRIVE_CAPACITY'        : CapPerHd['1950G4H'] * 4,
   'CAPACITY_TARGET'       : CapPerHd['1950G4H']/CapPerHd_Rap,
   'NUM_HEADS'             : 4,
   'UMP_CAPACITY'          : 50,
   'UMP_CAPACITY_SPEC'     : 46,
   'UMP_CAPACITY_RAP'      : 50, # program to 50GB   
   'NATIVE_DRV'            : 1,   
})
Native_1740G_4H_5400.update({
   'DRIVE_CAPACITY'        : CapPerHd['1740G4H'] * 4,
   'CAPACITY_TARGET'       : CapPerHd['1740G4H']/CapPerHd_Rap,
   'NUM_HEADS'             : 4,
})
Native_1620G_4H_5400.update({
   'DRIVE_CAPACITY'        : CapPerHd['1620G4H'] * 4,
   'CAPACITY_TARGET'       : CapPerHd['1620G4H']/CapPerHd_Rap,
   'NUM_HEADS'             : 4,
})


# ------ Rosewood7 1D/2D 1-head Capacity -------
Native_500G_1H_5400.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['500G1H'] * 1,
   'CAPACITY_TARGET'       : CapPerHd['500G1H'] / CapPerHd_Rap,
   'NUM_HEADS'             : 1,
   'NATIVE_DRV'            : 1,
})
Native_500G_1H_5400_SBS.update({
   'DRIVE_CAPACITY'        : CapPerHd['500G1H'] * 1,
   'CAPACITY_TARGET'       : CapPerHd['500G1H'] / CapPerHd_Rap,
   'NUM_HEADS'             : 1,
   'ATI_TARGET_OTF_BER'    : SBS_ATI_TARGET_OTF_BER,
   'TPI_MARGIN_THRESHOLD'  : SBS_TPI_MARGIN_THRESHOLD,
   'NATIVE_DRV'            : 1,
})
Rezone_375G_1H_5400.update({
   'DRIVE_CAPACITY'        : CapPerHd['375G1H'] * 1,
   'CAPACITY_TARGET'       : CapPerHd['375G1H'] / CapPerHd_Rap,
   'NUM_HEADS'             : 1,
})


# ------ Rosewood7 2D 3-head Capacity -------
# Quick and dirty hack to align the max lba same as 1D.
Static_Depop_1000G_3H_5400.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['1000G'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['1000G3H'] / CapPerHd_Rap,
   'NUM_HEADS'             : 3,
   'OD_THRUPUT_PERCENT'    : OD_THRUPUT_PERCENT,
   'ID_THRUPUT_PERCENT'    : ID_THRUPUT_PERCENT,
})

Static_Depop_1000G_3H_5400_15G.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['1000G'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['1000G3H'] / CapPerHd_Rap,
   'NUM_HEADS'             : 3,
   'OD_THRUPUT_PERCENT'    : OD_THRUPUT_PERCENT,
   'ID_THRUPUT_PERCENT'    : ID_THRUPUT_PERCENT,
})

# ------ Chengai-Mule 1D Capacity -------
Native_750G_2H_5400.update({
   'DRIVE_CAPACITY'        : CapPerHd['750G'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['750G']/CapPerHd_Rap,
   'NUM_HEADS'             : 2,
})
Native_750G_2H_5400_SBS.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['750G'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['750G']/CapPerHd_Rap,
   'NUM_HEADS'             : 2,
   "ATI_TARGET_OTF_BER"    : SBS_ATI_TARGET_OTF_BER,
   'TPI_MARGIN_THRESHOLD'  : SBS_TPI_MARGIN_THRESHOLD,
})
Rezone_500G_2H_5400.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['500G'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['500G']/CapPerHd_Rap,
   'NUM_HEADS'             : 2,
   'OD_THRUPUT_PERCENT'    : OD_THRUPUT_PERCENT,
   'ID_THRUPUT_PERCENT'    : ID_THRUPUT_PERCENT,
   'THRUPUT_BY_HD'         : 51.5,
})
Rezone_500G_2H_5400_15G.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['500G15'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['500G15']/CapPerHd_Rap,
   'NUM_HEADS'             : 2,
})

Native_640G_2H_5400.update({ 
   'DRIVE_CAPACITY'        : CapPerHd['640G2H'] * 2,
   'CAPACITY_TARGET'       : CapPerHd['640G2H']/CapPerHd_Rap,
   'NUM_HEADS'             : 2,
})

Native_680G_2H_5400.update({ 
'DRIVE_CAPACITY':	CapPerHd['680G2H'] * 2,
'CAPACITY_TARGET':	CapPerHd['680G2H']/CapPerHd_Rap,
'NUM_HEADS':	2,
})

Native_720G_2H_5400.update({ 
'DRIVE_CAPACITY':	CapPerHd['720G2H'] * 2,
'CAPACITY_TARGET':	CapPerHd['720G2H']/CapPerHd_Rap,
'NUM_HEADS':	2,
})


if testSwitch.FE_0258044_348085_WATERFALL_WITH_ONE_TRK_PER_BAND: 
   if testSwitch.CHENGAI:
      Rezone_500G_2H_5400.update({ 
      'TPI_MARGIN_FACTOR':  0.5,
      'TRACKS_PER_BAND'  :  tracks_per_band_wtf,
      'MEDIA_CACHE_CAPACITY'           : MC_SIZE_WTF,
      'MEDIA_CACHE_CAPACITY_SPEC'      : MC_WTF_SPEC,
      'MEDIA_CACHE_SIZE_RAP'           : MC_SIZE_RAP_WTF,
      'UMP_CAPACITY'                   : 1.0,
      'UMP_CAPACITY_SPEC'              : 1.0,
      })

