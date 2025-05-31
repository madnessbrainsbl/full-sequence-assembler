#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Test Parameters for Extreme3
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_params_Chengai.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $perp
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/AFH_params_Chengai.py#1 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from AFH_constants import angstromsScaler
from Utility import CUtility
Utl = CUtility()
from Test_Switches import testSwitch
from TestParameters import numHeads
from TestParameters import program
from base_TestParameters import prm_191_0002

AAB_TYPE = { # Defaul AAB TYPE to override Config VAR
   'ATTRIBUTE': 'HGA_SUPPLIER',
   'DEFAULT'  : 'RHO',
   'RHO'      : '501.02' ,
   'TDK'      : '26YR4' ,
   'HWY'      : 'H_26YR4' ,
}
#Each Prea-amp + AAB + Power Mode combination will have 2 sets of coefficients.
#   1. WP + Heater
#   2. Heater only
#Coefficient abstraction..
#
AAB_RHO = ['500.06','500.26','501.00','501.02','501.11','501.32','500.03']
AAB_TDK = ['26YR4','26YR42','26YR6','25M92','25AS2', '25AS2M2', '25AS2M3']
AAB_HWY = ['H_26YR4','H_26YR42','H_26YR6','H_25M92','H_25AS2', 'H_25AS2M2','H_25AS2M3']

DefaultRHOAABType = '501.02'
DefaultTDKAABType = '25AS2M2'
DefaultHWYAABType = 'H_25AS2M2'
DefaultAABType = DefaultHWYAABType

#Attributes used to detect the head manufacturer.
HGA_SUPPLIER_LOOKUP = {
      'RHO': { 'HGA_SUPPLIER' : ['RHO'] },
      'TDK': { 'HGA_SUPPLIER' : ['TDK'] },
      'HWY': { 'HGA_SUPPLIER' : ['HWY'] },
      }
#Attributes used to detect the wafer code.
WAFER_CODE_MATRIX = {
      'SDK' : { 'MEDIA_CODE' : ['PH','DK','DT','DH', 'WT','WK','PK','WT','PT','WH'] },
      'RMO' : { 'MEDIA_CODE' : ['PA','PF','SG','SF','SM','SW','SE','SA','WF','PF','WW','PW','WA'] },
      }


ATTR_AAB_MATRIX = {}


if testSwitch.FE_0150604_208705_P_VBAR_HMS_PHASE_2_INCREASE_TGT_CLR:
      writeClearance = 18.0
      readClearance = 18.0
else:
      writeClearance = 15.0
      readClearance = 15.0

defaultProfile = {
      'ATTRIBUTE':'numZones',
      'DEFAULT': 60,
      31 : {
         'TGT_WRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(32)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(32)],
            },
         'TGT_MAINTENANCE_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(32)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(32)],
            },

         'TGT_PREWRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(32)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(32)],
            },
         'TGT_RD_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(readClearance/angstromsScaler,8) for i in xrange(32)],
            'TDK'                : [round(readClearance/angstromsScaler,8) for i in xrange(32)],
            },

         }, # end of 31 : {
      60 : {
         'TGT_WRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(61)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(61)],
            },
         'TGT_MAINTENANCE_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(61)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(61)],
            },

         'TGT_PREWRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(61)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(61)],
            },
         'TGT_RD_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(readClearance/angstromsScaler,8) for i in xrange(61)],
            'TDK'                : [round(readClearance/angstromsScaler,8) for i in xrange(61)],
            },
         }, # end of 60 : {
      120 : {
         'TGT_WRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(121)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(121)],
            },
         'TGT_MAINTENANCE_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(121)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(121)],
            },

         'TGT_PREWRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(121)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(121)],
            },
         'TGT_RD_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(readClearance/angstromsScaler,8) for i in xrange(121)],
            'TDK'                : [round(readClearance/angstromsScaler,8) for i in xrange(121)],
            },
         }, # end of 180
      150 : {
         'TGT_WRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(151)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(151)],
            },
         'TGT_MAINTENANCE_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(151)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(151)],
            },

         'TGT_PREWRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(151)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(151)],
            },
         'TGT_RD_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(readClearance/angstromsScaler,8) for i in xrange(151)],
            'TDK'                : [round(readClearance/angstromsScaler,8) for i in xrange(151)],
            },
         }, # end of 180
      180 : {
         'TGT_WRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(181)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(181)],
            },
         'TGT_MAINTENANCE_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(181)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(181)],
            },

         'TGT_PREWRT_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(writeClearance/angstromsScaler,8) for i in xrange(181)],
            'TDK'                : [round(writeClearance/angstromsScaler,8) for i in xrange(181)],
            },
         'TGT_RD_CLR' : {
            'ATTRIBUTE' : 'HGA_SUPPLIER',
            'DEFAULT' : 'RHO',
            'RHO'                : [round(readClearance/angstromsScaler,8) for i in xrange(181)],
            'TDK'                : [round(readClearance/angstromsScaler,8) for i in xrange(181)],
            },
         }, # end of 180 : {
      } # end of defaultProfile = {
####### Tgt Clr related params START here ##########

afhZoneTargets = {
   'ATTRIBUTE':'numZones',
   'DEFAULT': 31,
   31:{
      'ATTRIBUTE':'AABType',
      '25AS2':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
         },
      '25AS2M2':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
         },
      '26YR4':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
         },
      '25AS2':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
         },
      '26YR42':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(29)] + [16, 17, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(29)] + [16, 17, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(29)] + [16, 17, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(29)] + [16, 17, 15] ),
         },

      '26YR6':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(32)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(32)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(32)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(32)] ),
         },
      '25M92':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(29)] + [16, 17, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(29)] + [16, 17, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(29)] + [16, 17, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(29)] + [16, 17, 15] ),
         },     
      'H_25AS2':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
         },
      'H_25AS2M2':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
         },
      'H_25AS2M3':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
         },
      'H_26YR4':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
         },
      'H_25AS2':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(28)] + [16, 17, 18, 15] ),
         },
      'H_26YR42':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(29)] + [16, 17, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(29)] + [16, 17, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(29)] + [16, 17, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(29)] + [16, 17, 15] ),
         },

      'H_26YR6':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(32)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(32)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(32)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(32)] ),
         },
      'H_25M92':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(29)] + [16, 17, 15] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(29)] + [16, 17, 15] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(29)] + [16, 17, 15] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(29)] + [16, 17, 15] ),
         },
      '500.00':{
            "TGT_WRT_CLR"         : tuple( [17, 17, 16] + [15 for i in range(29)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [17, 17, 16] + [15 for i in range(29)] ),
            "TGT_PREWRT_CLR"      : tuple( [17, 17, 16] + [15 for i in range(29)] ),
            "TGT_RD_CLR"          : tuple( [17, 17, 16] + [15 for i in range(29)] ),
         },
      '500.06':{
            "TGT_WRT_CLR"         : tuple( [17, 17, 16] + [15 for i in range(29)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [17, 17, 16] + [15 for i in range(29)] ),
            "TGT_PREWRT_CLR"      : tuple( [17, 17, 16] + [15 for i in range(29)] ),
            "TGT_RD_CLR"          : tuple( [17, 17, 16] + [15 for i in range(29)] ),
         },
      '500.26':{
            "TGT_WRT_CLR"         : tuple( [17, 17, 16] + [15 for i in range(29)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [17, 17, 16] + [15 for i in range(29)] ),
            "TGT_PREWRT_CLR"      : tuple( [17, 17, 16] + [15 for i in range(29)] ),
            "TGT_RD_CLR"          : tuple( [17, 17, 16] + [15 for i in range(29)] ),
         },
      '501.00':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(32)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(32)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(32)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(32)] ),
         },
      '501.02':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(32)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(32)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(32)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(32)] ),
         },
      '501.11':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(32)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(32)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(32)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(32)] ),
         },
      '500.03':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(32)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(32)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(32)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(32)] ),
         },         
      '2112-BP07':{
            "TGT_WRT_CLR"         : tuple( [17, 17, 16] + [15 for i in range(29)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [17, 17, 16] + [15 for i in range(29)] ),
            "TGT_PREWRT_CLR"      : tuple( [17, 17, 16] + [15 for i in range(29)] ),
            "TGT_RD_CLR"          : tuple( [17, 17, 16] + [15 for i in range(29)] ),
         },
      },
   60:{
      'ATTRIBUTE':'AABType',
      'DEFAULT'  : '25AS2M2',
      '26YR4':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      '25AS2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(61)] ),
         },
      '25AS2M2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      '25AS2M3':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      '26YR42':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },

      '26YR6':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      '25M92':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },  
      'H_26YR4':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      'H_25AS2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(61)] ),
         },
      'H_25AS2M2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      'H_25AS2M3':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      'H_26YR42':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },

      'H_26YR6':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      'H_25M92':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      '500.00':{
            "TGT_WRT_CLR"         : (17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,),
            "TGT_MAINTENANCE_CLR" : (17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,),
            "TGT_PREWRT_CLR"      : (17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,),
            "TGT_RD_CLR"          : (17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,),
         },
      '500.06':{
            "TGT_WRT_CLR"         : (17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,),
            "TGT_MAINTENANCE_CLR" : (17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,),
            "TGT_PREWRT_CLR"      : (17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,),
            "TGT_RD_CLR"          : (17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,),
         },
      '500.26':{
            "TGT_WRT_CLR"         : (17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,),
            "TGT_MAINTENANCE_CLR" : (17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,),
            "TGT_PREWRT_CLR"      : (17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,),
            "TGT_RD_CLR"          : (17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,),
         },
      '501.00':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(61)] ),
         },
      '501.02':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      '501.11':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      '501.32':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(61)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(61)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(61)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(61)] ),
         },
      },
   120:{
      'ATTRIBUTE':'AABType',
      'DEFAULT'  : '25AS2M2',
      '26YR4':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      '25AS2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(121)] ),
         },
      '25AS2M2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      '25AS2M3':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      '26YR42':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },

      '26YR6':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      '25M92':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },  
      'H_26YR4':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      'H_25AS2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(121)] ),
         },
      'H_25AS2M2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      'H_25AS2M3':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      'H_26YR42':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      'H_26YR6':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      'H_25M92':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      '500.00':{
            "TGT_WRT_CLR"         : (17, 17, 16) + tuple( [15 for i in range(121-3)] ),
            "TGT_MAINTENANCE_CLR" : (17, 17, 16) + tuple( [15 for i in range(121-3)] ),
            "TGT_PREWRT_CLR"      : (17, 17, 16) + tuple( [15 for i in range(121-3)] ),
            "TGT_RD_CLR"          : (17, 17, 16) + tuple( [15 for i in range(121-3)] ),
         },
      '500.06':{
          "TGT_WRT_CLR"         : (17, 17, 16) + tuple( [15 for i in range(121-3)] ),
          "TGT_MAINTENANCE_CLR" : (17, 17, 16) + tuple( [15 for i in range(121-3)] ),
          "TGT_PREWRT_CLR"      : (17, 17, 16) + tuple( [15 for i in range(121-3)] ),
          "TGT_RD_CLR"          : (17, 17, 16) + tuple( [15 for i in range(121-3)] ),
         },
      '500.26':{
          "TGT_WRT_CLR"         : (17, 17, 16) + tuple( [15 for i in range(121-3)] ),
          "TGT_MAINTENANCE_CLR" : (17, 17, 16) + tuple( [15 for i in range(121-3)] ),
          "TGT_PREWRT_CLR"      : (17, 17, 16) + tuple( [15 for i in range(121-3)] ),
          "TGT_RD_CLR"          : (17, 17, 16) + tuple( [15 for i in range(121-3)] ),
         },
      '501.00':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(121)] ),
         },
      '501.02':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      '501.11':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      '501.32':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(121)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(121)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(121)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(121)] ),
         },
      },
   150:{
      'ATTRIBUTE':'AABType',
      'DEFAULT'  : '25AS2M2',
      '26YR4':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      '25AS2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(151)] ),
         },
      '25AS2M2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      '25AS2M3':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      '26YR42':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },

      '26YR6':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      '25M92':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },  
      'H_26YR4':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      'H_25AS2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(151)] ),
         },
      'H_25AS2M2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      'H_25AS2M3':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      'H_26YR42':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      'H_26YR6':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      'H_25M92':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      '500.00':{
            "TGT_WRT_CLR"         : (17, 17, 16) + tuple( [15 for i in range(151-3)] ),
            "TGT_MAINTENANCE_CLR" : (17, 17, 16) + tuple( [15 for i in range(151-3)] ),
            "TGT_PREWRT_CLR"      : (17, 17, 16) + tuple( [15 for i in range(151-3)] ),
            "TGT_RD_CLR"          : (17, 17, 16) + tuple( [15 for i in range(151-3)] ),
         },
      '500.06':{
          "TGT_WRT_CLR"         : (17, 17, 16) + tuple( [15 for i in range(151-3)] ),
          "TGT_MAINTENANCE_CLR" : (17, 17, 16) + tuple( [15 for i in range(151-3)] ),
          "TGT_PREWRT_CLR"      : (17, 17, 16) + tuple( [15 for i in range(151-3)] ),
          "TGT_RD_CLR"          : (17, 17, 16) + tuple( [15 for i in range(151-3)] ),
         },
      '500.26':{
          "TGT_WRT_CLR"         : (17, 17, 16) + tuple( [15 for i in range(151-3)] ),
          "TGT_MAINTENANCE_CLR" : (17, 17, 16) + tuple( [15 for i in range(151-3)] ),
          "TGT_PREWRT_CLR"      : (17, 17, 16) + tuple( [15 for i in range(151-3)] ),
          "TGT_RD_CLR"          : (17, 17, 16) + tuple( [15 for i in range(151-3)] ),
         },
      '501.00':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(151)] ),
         },
      '501.02':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      '501.11':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      '501.32':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(151)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(151)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(151)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(151)] ),
         },
      },
   180:{
      'ATTRIBUTE':'AABType',
      'DEFAULT'  : '25AS2M2',
      '26YR4':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      '25AS2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(181)] ),
         },
      '25AS2M2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      '25AS2M3':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      '26YR42':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },

      '26YR6':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      '25M92':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },  
      'H_26YR4':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      'H_25AS2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(181)] ),
         },
      'H_25AS2M2':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      'H_25AS2M3':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      'H_26YR42':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      'H_26YR6':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      'H_25M92':{
            "TGT_WRT_CLR"         : tuple( [15 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [15 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [15 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      '500.00':{
            "TGT_WRT_CLR"         : (17, 17, 16) + tuple( [15 for i in range(181-3)] ),
            "TGT_MAINTENANCE_CLR" : (17, 17, 16) + tuple( [15 for i in range(181-3)] ),
            "TGT_PREWRT_CLR"      : (17, 17, 16) + tuple( [15 for i in range(181-3)] ),
            "TGT_RD_CLR"          : (17, 17, 16) + tuple( [15 for i in range(181-3)] ),
         },
      '500.06':{
          "TGT_WRT_CLR"         : (17, 17, 16) + tuple( [15 for i in range(181-3)] ),
          "TGT_MAINTENANCE_CLR" : (17, 17, 16) + tuple( [15 for i in range(181-3)] ),
          "TGT_PREWRT_CLR"      : (17, 17, 16) + tuple( [15 for i in range(181-3)] ),
          "TGT_RD_CLR"          : (17, 17, 16) + tuple( [15 for i in range(181-3)] ),
         },
      '500.26':{
          "TGT_WRT_CLR"         : (17, 17, 16) + tuple( [15 for i in range(181-3)] ),
          "TGT_MAINTENANCE_CLR" : (17, 17, 16) + tuple( [15 for i in range(181-3)] ),
          "TGT_PREWRT_CLR"      : (17, 17, 16) + tuple( [15 for i in range(181-3)] ),
          "TGT_RD_CLR"          : (17, 17, 16) + tuple( [15 for i in range(181-3)] ),
         },
      '501.00':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [12 for i in range(181)] ),
         },
      '501.02':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      '501.11':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      '501.32':{
            "TGT_WRT_CLR"         : tuple( [12 for i in range(181)] ),
            "TGT_MAINTENANCE_CLR" : tuple( [12 for i in range(181)] ),
            "TGT_PREWRT_CLR"      : tuple( [12 for i in range(181)] ),
            "TGT_RD_CLR"          : tuple( [15 for i in range(181)] ),
         },
      },
}

####### Tgt Clr related params END here ##########





prm_191_0002["CWORD1"] = (0x02D1,)
Test135_numHeadRetries = 3  # Retry limit in T135. Set to 5. Default is 3



##################COPY FROM YARRABP START ##############################
#Firmware equation governing TCS1 and TCS2
#TCS1 * Delta temp + TCS2 * Delta temp^2
tccDict_178 = {}
if 0:
   tccDict_178 = {
   'ATTRIBUTE':'HGA_SUPPLIER',
   'DEFAULT': 'TDK',
   'RHO':  {
   #  'default'                  : 0,
      'TCS1'                     : -0.000681, #-0.0005, # this seems too high.
      'TCS2'                     : 0,
      # suggested values
      'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
      'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
      'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
      'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
      'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
      'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
      'dTc'                      : 0.00125,            # very std dTc, dTh settings.  Should be the same as legacy RAP.
      'dTh'                      : -0.000994,
      'COLD_TEMP_DTC'            : 20,
      'HOT_TEMP_DTH'             : 48,
      'enableModifyTCS_values'   : 1,
      'dThR'                     : (-0.132558906, -0.215893826, -0.22533878, -0.239824326, -0.238614585,), #(-0.243479616, -0.304232345, -0.325618118, -0.310389887, -0.32423583),
      'dTcR'                     : (0.129842132, 0.170155248, 0.165560576, 0.155187447, 0.135608736,), #(0.129842132,0.170155248, 0.165560576,0.155187447,0.135608736),
   },
   'TDK':  {
      'ATTRIBUTE':'AABType',
      'DEFAULT': '26YR4',
      '26YR4': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of '26YR4'
      '25AS2': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of '25AS2'
      '25AS2M2': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of '25AS2M2'
      '26YR42': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of '26YR42'

      '26YR6': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of '26YR6'
      '25M92': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of '25M92'
   },#end of 'TDK'
   
   'HWY':  {
      'ATTRIBUTE':'AABType',
      'DEFAULT': 'H_26YR4',
      'H_26YR4': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of 'H_26YR4'
      'H_25AS2': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of 'H_25AS2'
      'H_25AS2M2': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of 'H_25AS2M2'
      'H_25AS2M3': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of 'H_25AS2M2'
      'H_26YR42': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of 'H_26YR42'

      'H_26YR6': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of 'H_26YR6'
      'H_25M92': { 
         #  'default'                  : 0,
         'TCS1'                     : -0.001, #-0.0005, # this seems too high.
         'TCS2'                     : 0,
         # suggested values
         'TCS1_LSL'                 : -0.0040,        # was -0.0020 -> -2.0 n"/C
         'MODIFIED_SLOPE_LSL'       : -0.0040,        # -1.5 n"/C
         'MODIFIED_SLOPE_USL'       : -0.0005,        # -0.5 n"/C
         'TCS1_USL'                 : -0.0005,        # was 0.0005 ->  +0.5 n"/C
         'TCS2_USL'                 : 1.0,            # 1 u"/C (essentially disable)
         'TCS2_LSL'                 : -1.0,           # -1 u"/C (essentially disable)
         'dTc'                      : 0.0005, #Updated on 17 Oct 2011 # very std dTc, dTh settings.  Should be the same as legacy RAP.
         'dTh'                      : -0.002, #updated on 17 Oct 2011.
         'COLD_TEMP_DTC'            : 10, #updated on 17 Oct 2011.
         'HOT_TEMP_DTH'             : 55, #updated on 17 Oct 2011.
         'enableModifyTCS_values'   : 1,
         'dThR'                     : (-0.298103195 / 254.0, -0.404627717 / 254.0, -0.344044506 / 254.0, -0.236665516 / 254.0, -0.185345043 / 254.0,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
         'dTcR'                     : (0.112182395 / 254.0, 0.149864432 / 254.0, 0.1259926 / 254.0, 0.137140324 / 254.0, 0.11726935 / 254.0,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
      },#end of 'H_25M92'
   }#end of 'HWY'
}


##########
# NOTE:  FOR Dual HEATER(DH) the above limits from single heater don't apply anymore.
##########

#### NOTE:  TCC related params are in Angstroms now

tcc_DH_dict_178 = {
      'ATTRIBUTE': 'HGA_SUPPLIER',
      'DEFAULT'  : 'RHO',
      'TDK'      : 
      {
          'ATTRIBUTE':'AABType',
          'DEFAULT': '26YR4',
          '26YR4': {
                "WRITER_HEATER"   : {
                   'TCS1'                     :  -0.3949,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      :  -0.1,            #  Angstroms/C
                   'dTh'                      :  -0.4,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Write Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },
                "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                   'TCS1'                     :  -0.3949,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      : -0.1,          #  Angstroms/C
                   'dTh'                      : -0.4,          #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Read Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },},
          '25AS2M2': {
                "WRITER_HEATER"   : {
                   'TCS1'                     :  -0.3949,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      :  0,            #  Angstroms/C
                   'dTh'                      :  -0.2794,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Write Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },
                "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                   'TCS1'                     :  -0.3949,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      : 0,          #  Angstroms/C
                   'dTh'                      : -0.3048,          #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Read Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },},
          '25AS2M3': {
                "WRITER_HEATER"   : {
                   'TCS1'                     :  -0.13,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      :  -0.254,            #  Angstroms/C
                   'dTh'                      :  -0.2794,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Write Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },
                "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                   'TCS1'                     :  -0.256,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      : 0,          #  Angstroms/C
                   'dTh'                      : -0.3048,          #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Read Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },},

          '25AS2': {
                "WRITER_HEATER"   : {
                   'TCS1'                     :  -0.3949,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      :  -0.1,            #  Angstroms/C
                   'dTh'                      :  -0.4,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Write Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },
                "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                   'TCS1'                     :  -0.3949,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      : -0.1,          #  Angstroms/C
                   'dTh'                      : -0.4,          #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Read Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },},
         '26YR42': {
                "WRITER_HEATER"   : {
                   'TCS1'                     :  -0.254,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : -0.127,              #  Angstroms/C
                   'TCS1_LSL'                 : -1.016,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      :  0.0005*254,            #  Angstroms/C
                   'dTh'                      :  -0.002*254,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Write Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },
                "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                   'TCS1'                     :  -0.254,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : -0.127,              #  Angstroms/C
                   'TCS1_LSL'                 : -1.016,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      : 0.0005*254,          #  Angstroms/C
                   'dTh'                      : -0.002*254,          #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Read Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },},
           '26YR6': {
                "WRITER_HEATER"   : {
                   'TCS1'                     :  -0.254,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : -0.127,              #  Angstroms/C
                   'TCS1_LSL'                 : -1.016,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      :  0.0005*254,            #  Angstroms/C
                   'dTh'                      :  -0.002*254,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Write Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },
                "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                   'TCS1'                     :  -0.254,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : -0.127,              #  Angstroms/C
                   'TCS1_LSL'                 : -1.016,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      : 0.0005*254,          #  Angstroms/C
                   'dTh'                      : -0.002*254,          #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Read Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },},
         '25M92': {
              "WRITER_HEATER"   : {
                 'TCS1'                     :  -0.254,
                 'TCS2'                     :  0.0,
        
                 'TCS1_USL'                 : -0.127,              #  Angstroms/C
                 'TCS1_LSL'                 : -1.016,              #  Angstroms/C
        
                 'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
                 'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
                 'enableModifyTCS_values'   : 1,
        
                 'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                 'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
        
                 'dTc'                      :  0.0005*254,            #  Angstroms/C
                 'dTh'                      :  -0.002*254,            #  Angstroms/C
                 'COLD_TEMP_DTC'            : 10,
                 'HOT_TEMP_DTH'             : 55,
                 'clearanceDataType'        : 'Write Clearance',
                 'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                 'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                 },
              "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                 'TCS1'                     :  -0.254,
                 'TCS2'                     :  0.0,
        
                 'TCS1_USL'                 : -0.127,              #  Angstroms/C
                 'TCS1_LSL'                 : -1.016,              #  Angstroms/C
        
                 'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
                 'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
                 'enableModifyTCS_values'   : 1,
        
                 'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                 'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
        
                 'dTc'                      : 0.0005*254,          #  Angstroms/C
                 'dTh'                      : -0.002*254,          #  Angstroms/C
                 'COLD_TEMP_DTC'            : 10,
                 'HOT_TEMP_DTH'             : 55,
                 'clearanceDataType'        : 'Read Clearance',
                 'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                 'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                 },},
           },# end of TDK
      'HWY'      : 
      {
          'ATTRIBUTE':'AABType',
          'DEFAULT': 'H_26YR4',
          'H_26YR4': {
                "WRITER_HEATER"   : {
                   'TCS1'                     :  -0.3949,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      :  -0.1,            #  Angstroms/C
                   'dTh'                      :  -0.4,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Write Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },
                "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                   'TCS1'                     :  -0.3949,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      : -0.1,          #  Angstroms/C
                   'dTh'                      : -0.4,          #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Read Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },},
          'H_25AS2M2': {
                "WRITER_HEATER"   : {
                   'TCS1'                     :  -0.3949,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      :  0,            #  Angstroms/C
                   'dTh'                      :  -0.2540,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Write Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },
                "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                   'TCS1'                     :  -0.3949,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      : 0,          #  Angstroms/C
                   'dTh'                      : -0.3810,          #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Read Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },},
          'H_25AS2M3': {
                "WRITER_HEATER"   : {
                   'TCS1'                     :  -0.13,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      :  -0.2540,            #  Angstroms/C
                   'dTh'                      :  -0.2540,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Write Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },
                "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                   'TCS1'                     :  -0.256,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      : 0,          #  Angstroms/C
                   'dTh'                      : -0.3810,          #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Read Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },},
          'H_25AS2': {
                "WRITER_HEATER"   : {
                   'TCS1'                     :  -0.3949,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      :  -0.1,            #  Angstroms/C
                   'dTh'                      :  -0.4,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Write Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },
                "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                   'TCS1'                     :  -0.3949,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : 0.0522,              #  Angstroms/C
                   'TCS1_LSL'                 : -0.8419,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : 0.0522,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -0.8419,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      : -0.1,          #  Angstroms/C
                   'dTh'                      : -0.4,          #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Read Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },},
         'H_26YR42': {
                "WRITER_HEATER"   : {
                   'TCS1'                     :  -0.254,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : -0.127,              #  Angstroms/C
                   'TCS1_LSL'                 : -1.016,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      :  0.0005*254,            #  Angstroms/C
                   'dTh'                      :  -0.002*254,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Write Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },
                "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                   'TCS1'                     :  -0.254,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : -0.127,              #  Angstroms/C
                   'TCS1_LSL'                 : -1.016,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      : 0.0005*254,          #  Angstroms/C
                   'dTh'                      : -0.002*254,          #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Read Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },},
           'H_26YR6': {
                "WRITER_HEATER"   : {
                   'TCS1'                     :  -0.254,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : -0.127,              #  Angstroms/C
                   'TCS1_LSL'                 : -1.016,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      :  0.0005*254,            #  Angstroms/C
                   'dTh'                      :  -0.002*254,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Write Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },
                "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                   'TCS1'                     :  -0.254,
                   'TCS2'                     :  0.0,
          
                   'TCS1_USL'                 : -0.127,              #  Angstroms/C
                   'TCS1_LSL'                 : -1.016,              #  Angstroms/C
          
                   'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
                   'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
                   'enableModifyTCS_values'   : 1,
          
                   'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                   'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
          
                   'dTc'                      : 0.0005*254,          #  Angstroms/C
                   'dTh'                      : -0.002*254,          #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   'clearanceDataType'        : 'Read Clearance',
                   'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                   'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                   },},
         'H_25M92': {
              "WRITER_HEATER"   : {
                 'TCS1'                     :  -0.254,
                 'TCS2'                     :  0.0,
        
                 'TCS1_USL'                 : -0.127,              #  Angstroms/C
                 'TCS1_LSL'                 : -1.016,              #  Angstroms/C
        
                 'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
                 'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
                 'enableModifyTCS_values'   : 1,
        
                 'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                 'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
        
                 'dTc'                      :  0.0005*254,            #  Angstroms/C
                 'dTh'                      :  -0.002*254,            #  Angstroms/C
                 'COLD_TEMP_DTC'            : 10,
                 'HOT_TEMP_DTH'             : 55,
                 'clearanceDataType'        : 'Write Clearance',
                 'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                 'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                 },
              "READER_HEATER"   : {          #dummy ONLY, TDK doesn't have READER_HEATER
                 'TCS1'                     :  -0.254,
                 'TCS2'                     :  0.0,
        
                 'TCS1_USL'                 : -0.127,              #  Angstroms/C
                 'TCS1_LSL'                 : -1.016,              #  Angstroms/C
        
                 'MODIFIED_SLOPE_USL'       : -0.127,              # fold limits in Ang/C
                 'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
                 'enableModifyTCS_values'   : 1,
        
                 'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
                 'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
        
                 'dTc'                      : 0.0005*254,          #  Angstroms/C
                 'dTh'                      : -0.002*254,          #  Angstroms/C
                 'COLD_TEMP_DTC'            : 10,
                 'HOT_TEMP_DTH'             : 55,
                 'clearanceDataType'        : 'Read Clearance',
                 'dThR'                     : (-0.298103195, -0.404627717, -0.344044506, -0.236665516, -0.185345043,), #(-0.392623462, -0.47364523, -0.446210815, -0.340337043, -0.264545981),
                 'dTcR'                     : (0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935,), #(0.112182395, 0.149864432, 0.1259926, 0.137140324, 0.11726935),
                 },},
           },# end of HWY
      'RHO'      : 
      {
      'ATTRIBUTE':'AABType',
      'DEFAULT': '2112-BP07',
      '2112-BP07':{
          "WRITER_HEATER"   : {
             'TCS1'                     :  -0.127, #-0.00017275u, #previous: 0.02667A/0.000105u, updated on 19 Oct 2011.
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.0000,              #  Angstroms/C
             'TCS1_LSL'                 : -1.016,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.0000,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  0.209301525, #0.20930108, #0.00082402u #previous: 0.1171194A/0.00046110u  #  Angstroms/C
             'dTh'                      :  -0.381, #-0.0010598u #previous: -0.5664708A/-0.0022302u  #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Write Clearance',
             'dThR'                     : (-0.132558906,-0.215893826,-0.22533878,-0.239824326,-0.238614585,), #(-0.243479616, -0.304232345, -0.325618118, -0.310389887, -0.32423583),
             'dTcR'                     : (0.129842132, 0.170155248,0.165560576,0.155187447,0.135608736,), #(0.129842132,0.170155248, 0.165560576,0.155187447,0.135608736),
             },
          "READER_HEATER"   : {
             'TCS1'                     :  -0.381, #-0.0019492u #previous: -0.3807714A/-0.0014991u 
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.0000,              #  Angstroms/C
             'TCS1_LSL'                 : -1.016,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.0000,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  -0.2032,#0.4950968, #0.0019492u #previous: 0.5245608A/0.0020652u #  Angstroms/C
             'dTh'                      :  -0.26918061,#-0.2691892, #-0.0010598u #previous:-0.4260596A/-0.0016774u  #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Read Clearance',
             'dThR'                     : (-0.234296198, -0.363856248, -0.310628675, -0.252700716, -0.239524892,), #(-0.442652399, -0.407185004, -0.400915193, -0.400231224, -0.373329883,),
             'dTcR'                     : (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,), # (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,),                
             },
          }, #end of 2112-BP07
      '500.00':{
          "WRITER_HEATER"   : {
             'TCS1'                     :  -0.127, #-0.00017275u, #previous: 0.02667A/0.000105u, updated on 19 Oct 2011.
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.0000,              #  Angstroms/C
             'TCS1_LSL'                 : -1.016,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.0000,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  -0.000897*254, #  Angstroms/C
             'dTh'                      :  -0.001136*254, #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Write Clearance',
             'dThR'                     : (-0.132558906,-0.215893826,-0.22533878,-0.239824326,-0.238614585,), #(-0.243479616, -0.304232345, -0.325618118, -0.310389887, -0.32423583),
             'dTcR'                     : (0.129842132, 0.170155248,0.165560576,0.155187447,0.135608736,), #(0.129842132,0.170155248, 0.165560576,0.155187447,0.135608736),
             },
          "READER_HEATER"   : {
             'TCS1'                     :  -0.381, #-0.0019492u #previous: -0.3807714A/-0.0014991u 
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.0000,              #  Angstroms/C
             'TCS1_LSL'                 : -1.016,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.0000,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  -0.001669*254,#  Angstroms/C
             'dTh'                      :  -0.001659*254,#  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Read Clearance',
             'dThR'                     : (-0.234296198, -0.363856248, -0.310628675, -0.252700716, -0.239524892,), #(-0.442652399, -0.407185004, -0.400915193, -0.400231224, -0.373329883,),
             'dTcR'                     : (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,), # (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,),                
             },
          }, #end of 500.00
      '500.06':{
          "WRITER_HEATER"   : {
             'TCS1'                     :  -0.127, #-0.00017275u, #previous: 0.02667A/0.000105u, updated on 19 Oct 2011.
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.0000,              #  Angstroms/C
             'TCS1_LSL'                 : -1.016,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.0000,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  -0.000897*254,  #  Angstroms/C
             'dTh'                      :  -0.000989*254,  #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Write Clearance',
             'dThR'                     : (-0.132558906,-0.215893826,-0.22533878,-0.239824326,-0.238614585,), #(-0.243479616, -0.304232345, -0.325618118, -0.310389887, -0.32423583),
             'dTcR'                     : (0.129842132, 0.170155248,0.165560576,0.155187447,0.135608736,), #(0.129842132,0.170155248, 0.165560576,0.155187447,0.135608736),
             },
          "READER_HEATER"   : {
             'TCS1'                     :  -0.381, #-0.0019492u #previous: -0.3807714A/-0.0014991u 
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.0000,              #  Angstroms/C
             'TCS1_LSL'                 : -1.016,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.0000,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  -0.001669*254, #  Angstroms/C
             'dTh'                      :  -0.001272*254, #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Read Clearance',
             'dThR'                     : (-0.234296198, -0.363856248, -0.310628675, -0.252700716, -0.239524892,), #(-0.442652399, -0.407185004, -0.400915193, -0.400231224, -0.373329883,),
             'dTcR'                     : (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,), # (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,),                
             },
          }, #end of 500.06
      '500.26':{
          "WRITER_HEATER"   : {
             'TCS1'                     :  -0.127, #-0.00017275u, #previous: 0.02667A/0.000105u, updated on 19 Oct 2011.
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.0000,              #  Angstroms/C
             'TCS1_LSL'                 : -1.016,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.0000,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  0.209301525, #0.20930108, #0.00082402u #previous: 0.1171194A/0.00046110u  #  Angstroms/C
             'dTh'                      :  -0.381, #-0.0010598u #previous: -0.5664708A/-0.0022302u  #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Write Clearance',
             'dThR'                     : (-0.132558906,-0.215893826,-0.22533878,-0.239824326,-0.238614585,), #(-0.243479616, -0.304232345, -0.325618118, -0.310389887, -0.32423583),
             'dTcR'                     : (0.129842132, 0.170155248,0.165560576,0.155187447,0.135608736,), #(0.129842132,0.170155248, 0.165560576,0.155187447,0.135608736),
             },
          "READER_HEATER"   : {
             'TCS1'                     :  -0.381, #-0.0019492u #previous: -0.3807714A/-0.0014991u 
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.0000,              #  Angstroms/C
             'TCS1_LSL'                 : -1.016,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.0000,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.016,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  -0.2032,#0.4950968, #0.0019492u #previous: 0.5245608A/0.0020652u #  Angstroms/C
             'dTh'                      :  -0.26918061,#-0.2691892, #-0.0010598u #previous:-0.4260596A/-0.0016774u  #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Read Clearance',
             'dThR'                     : (-0.234296198, -0.363856248, -0.310628675, -0.252700716, -0.239524892,), #(-0.442652399, -0.407185004, -0.400915193, -0.400231224, -0.373329883,),
             'dTcR'                     : (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,), # (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,),                
             },
          }, #end of 500.26
      '501.00':{
          "WRITER_HEATER"   : {
             'TCS1'                     :  0.0376, #-0.00017275u, #previous: 0.02667A/0.000105u, updated on 19 Oct 2011.
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.8729,              #  Angstroms/C
             'TCS1_LSL'                 : -0.7978,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.8729,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -0.7978,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  -0.2, #0.20930108, #0.00082402u #previous: 0.1171194A/0.00046110u  #  Angstroms/C
             'dTh'                      :  -0.3,            #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Write Clearance',
             'dThR'                     : (-0.132558906,-0.215893826,-0.22533878,-0.239824326,-0.238614585,), #(-0.243479616, -0.304232345, -0.325618118, -0.310389887, -0.32423583),
             'dTcR'                     : (0.129842132, 0.170155248,0.165560576,0.155187447,0.135608736,), #(0.129842132,0.170155248, 0.165560576,0.155187447,0.135608736),
             },
          "READER_HEATER"   : {
             'TCS1'                     :  -0.2194, #-0.0019492u #previous: -0.3807714A/-0.0014991u 
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.7403,              #  Angstroms/C
             'TCS1_LSL'                 : -1.1791,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.7403,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.1791,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  -0.15, #  Angstroms/C
             'dTh'                      :  -0.45,  #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Read Clearance',
             'dThR'                     : (-0.234296198, -0.363856248, -0.310628675, -0.252700716, -0.239524892,), #(-0.442652399, -0.407185004, -0.400915193, -0.400231224, -0.373329883,),
             'dTcR'                     : (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,), # (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,),                
             },
          }, #end of 501.00
      '501.02':{
          "WRITER_HEATER"   : {
             'TCS1'                     :  -0.0460, #-0.00017275u, #previous: 0.02667A/0.000105u, updated on 19 Oct 2011.
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.7389,              #  Angstroms/C
             'TCS1_LSL'                 : -0.8308,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.7389,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -0.8308,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  0, #0.20930108, #0.00082402u #previous: 0.1171194A/0.00046110u  #  Angstroms/C
             'dTh'                      :  -0.2286,            #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Write Clearance',
             'dThR'                     : (-0.132558906,-0.215893826,-0.22533878,-0.239824326,-0.238614585,), #(-0.243479616, -0.304232345, -0.325618118, -0.310389887, -0.32423583),
             'dTcR'                     : (0.129842132, 0.170155248,0.165560576,0.155187447,0.135608736,), #(0.129842132,0.170155248, 0.165560576,0.155187447,0.135608736),
             },
          "READER_HEATER"   : {
             'TCS1'                     :  -0.2313, #-0.0019492u #previous: -0.3807714A/-0.0014991u 
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.5531,              #  Angstroms/C
             'TCS1_LSL'                 : -1.0157,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.5531,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.0157,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  0, #  Angstroms/C
             'dTh'                      :  -0.4318,  #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Read Clearance',
             'dThR'                     : (-0.234296198, -0.363856248, -0.310628675, -0.252700716, -0.239524892,), #(-0.442652399, -0.407185004, -0.400915193, -0.400231224, -0.373329883,),
             'dTcR'                     : (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,), # (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,),                
             },
          }, #end of 501.02
      '501.11':{
          "WRITER_HEATER"   : {
             'TCS1'                     :  -0.04, #-0.00017275u, #previous: 0.02667A/0.000105u, updated on 19 Oct 2011.
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0,              #  Angstroms/C
             'TCS1_LSL'                 : -0.8308,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -0.8308,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  -0.125, #0.20930108, #0.00082402u #previous: 0.1171194A/0.00046110u  #  Angstroms/C
             'dTh'                      :  -0.2286,            #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Write Clearance',
             'dThR'                     : (-0.132558906,-0.215893826,-0.22533878,-0.239824326,-0.238614585,), #(-0.243479616, -0.304232345, -0.325618118, -0.310389887, -0.32423583),
             'dTcR'                     : (0.129842132, 0.170155248,0.165560576,0.155187447,0.135608736,), #(0.129842132,0.170155248, 0.165560576,0.155187447,0.135608736),
             },
          "READER_HEATER"   : {
             'TCS1'                     :  -0.281, #-0.0019492u #previous: -0.3807714A/-0.0014991u 
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0,              #  Angstroms/C
             'TCS1_LSL'                 : -1.0157,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.0157,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  0, #  Angstroms/C
             'dTh'                      :  -0.4318,  #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Read Clearance',
             'dThR'                     : (-0.234296198, -0.363856248, -0.310628675, -0.252700716, -0.239524892,), #(-0.442652399, -0.407185004, -0.400915193, -0.400231224, -0.373329883,),
             'dTcR'                     : (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,), # (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,),                
             },
          }, #end of 501.02
      '501.32':{
          "WRITER_HEATER"   : {
             'TCS1'                     :  -0.0460, #-0.00017275u, #previous: 0.02667A/0.000105u, updated on 19 Oct 2011.
             'TCS2'                     :  0.0,

             'TCS1_USL'                 : 0.7389,              #  Angstroms/C
             'TCS1_LSL'                 : -0.8308,              #  Angstroms/C

             'MODIFIED_SLOPE_USL'       : 0.7389,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -0.8308,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,

             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)

             'dTc'                      :  0, #0.20930108, #0.00082402u #previous: 0.1171194A/0.00046110u  #  Angstroms/C
             'dTh'                      :  -0.2286,            #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Write Clearance',
             'dThR'                     : (-0.132558906,-0.215893826,-0.22533878,-0.239824326,-0.238614585,), #(-0.243479616, -0.304232345, -0.325618118, -0.310389887, -0.32423583),
             'dTcR'                     : (0.129842132, 0.170155248,0.165560576,0.155187447,0.135608736,), #(0.129842132,0.170155248, 0.165560576,0.155187447,0.135608736),
             },
          "READER_HEATER"   : {
             'TCS1'                     :  -0.2313, #-0.0019492u #previous: -0.3807714A/-0.0014991u 
             'TCS2'                     :  0.0,

             'TCS1_USL'                 : 0.5531,              #  Angstroms/C
             'TCS1_LSL'                 : -1.0157,              #  Angstroms/C

             'MODIFIED_SLOPE_USL'       : 0.5531,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.0157,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,

             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)

             'dTc'                      :  0, #  Angstroms/C
             'dTh'                      :  -0.4318,  #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Read Clearance',
             'dThR'                     : (-0.234296198, -0.363856248, -0.310628675, -0.252700716, -0.239524892,), #(-0.442652399, -0.407185004, -0.400915193, -0.400231224, -0.373329883,),
             'dTcR'                     : (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,), # (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,),                
             },
          }, #end of 501.32

      '500.03':{
          "WRITER_HEATER"   : {
             'TCS1'                     :  -0.0460, #-0.00017275u, #previous: 0.02667A/0.000105u, updated on 19 Oct 2011.
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.7389,              #  Angstroms/C
             'TCS1_LSL'                 : -0.8308,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.7389,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -0.8308,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  -0.2, #0.20930108, #0.00082402u #previous: 0.1171194A/0.00046110u  #  Angstroms/C
             'dTh'                      :  -0.3,            #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Write Clearance',
             'dThR'                     : (-0.132558906,-0.215893826,-0.22533878,-0.239824326,-0.238614585,), #(-0.243479616, -0.304232345, -0.325618118, -0.310389887, -0.32423583),
             'dTcR'                     : (0.129842132, 0.170155248,0.165560576,0.155187447,0.135608736,), #(0.129842132,0.170155248, 0.165560576,0.155187447,0.135608736),
             },
          "READER_HEATER"   : {
             'TCS1'                     :  -0.2313, #-0.0019492u #previous: -0.3807714A/-0.0014991u 
             'TCS2'                     :  0.0,
    
             'TCS1_USL'                 : 0.5531,              #  Angstroms/C
             'TCS1_LSL'                 : -1.0157,              #  Angstroms/C
    
             'MODIFIED_SLOPE_USL'       : 0.5531,              # fold limits in Ang/C
             'MODIFIED_SLOPE_LSL'       : -1.0157,              # fold limits in Ang/C
             'enableModifyTCS_values'   : 1,
    
             'TCS2_USL'                 :  1.0,                #  1 A/C (essentially disable)
             'TCS2_LSL'                 : -1.0,                # -1 A/C (essentially disable)
    
             'dTc'                      :  -0.15, #  Angstroms/C
             'dTh'                      :  -0.45,  #  Angstroms/C
             'COLD_TEMP_DTC'            : 10,
             'HOT_TEMP_DTH'             : 55,
             'clearanceDataType'        : 'Read Clearance',
             'dThR'                     : (-0.234296198, -0.363856248, -0.310628675, -0.252700716, -0.239524892,), #(-0.442652399, -0.407185004, -0.400915193, -0.400231224, -0.373329883,),
             'dTcR'                     : (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,), # (0.404427199, 0.406108519, 0.370105768, 0.295996974, 0.285660827,),                
             },
          }, #end of 501.02
      },# end of RHO
   }
##################COPY FROM YARRABP END##############################

if not testSwitch.FE_0169232_341036_ENABLE_AFH_TGT_CLR_CANON_PARAMS :
   tcc_DH_values = tcc_DH_dict_178



tcc_OFF = {
          "WRITER_HEATER"   : {
                   'TCS1'                     :  0,
                   'TCS2'                     :  0.0,
                   'dTc'                      :  0,            #  Angstroms/C
                   'dTh'                      :  0,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   },
          "READER_HEATER"   : {          
                   'TCS1'                     :  0,
                   'TCS2'                     :  0.0,
                   'dTc'                      :  0,            #  Angstroms/C
                   'dTh'                      :  0,            #  Angstroms/C
                   'COLD_TEMP_DTC'            : 10,
                   'HOT_TEMP_DTH'             : 55,
                   },                
}

