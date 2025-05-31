#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Class to store column definition including name and type
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/06 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DBLogDefs.py $
# $Revision: #2 $
# $DateTime: 2016/05/06 00:36:23 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DBLogDefs.py#2 $
# Level:3
#---------------------------------------------------------------------------------------------------------#
from Constants import *

class DbLogColumn:

   """
   Class used to store column definition including name and type.
   """
   __slots__ = ['__columnName', '__columnType', '__dbUpload' ]
   def __init__(self, columnName, columnType, dbUpload = 1):
      self.__columnName = columnName
      self.__columnType = columnType
      self.__dbUpload = dbUpload

   def getName(self):
      return self.__columnName

   def getType(self):
      return self.__columnType

   def getDbUpload(self):
      return self.__dbUpload

   def __str__(self):
      """
      Returns a default string describing the instance.
      """
      return "%s:%s:%s" % (str(self.__columnName), str(self.__columnType), str(self.__dbUpload))

class DbLogTableDefinitions:

   """
   Defines all available oracle tables.  This content/file should eventually be generated directly from EDD.
   """

   OracleTables = {
      'ZN_WRITE_STRESS':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('TEST_NAME', 'V'),
                  DbLogColumn('RUN_NUM', 'N'),
                  DbLogColumn('RUN_TIME', 'N'),
                        ]
            },

      'INTF_SEQREAD_THRUPUT':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('START_LBA', 'N'),
                  DbLogColumn('END_LBA', 'N'),
                  DbLogColumn('SEQREAD_THRUPUT', 'N'),
                              ]
            },

      'INTF_SEQWRITE_THRUPUT':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('START_LBA','N'),
                  DbLogColumn('END_LBA', 'N'),
                  DbLogColumn('SEQWRITE_THRUPUT', 'N'),
                           ]
            },

      'INTF_SEQWR_THRUPUT':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('START_LBA','N'),
                  DbLogColumn('END_LBA', 'N'),
                  DbLogColumn('SEQWR_THRUPUT', 'N'),
                       ]
            },

      'TEST_TIME_BY_TEST':
            {
                'type': 'S',
                'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('TEST_NUMBER', 'N'),
                  DbLogColumn('ELAPSED_TIME', 'N'),
                  DbLogColumn('PARAMETER_NAME','V'),
                  DbLogColumn('TEST_STATUS','N'),
                  DbLogColumn('CELL_TEMP','N'),
                  DbLogColumn('SZ','N',1),
                  DbLogColumn('RSS','N',1),
                  DbLogColumn('CPU_ET','N',1),
                           ]
            },
      'P035_PHYS_CLR':
            {
                'type': 'M',
                'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('DATA_ZONE','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('RD_CLR','N'),
                  DbLogColumn('WRT_CLR','N'),
                  DbLogColumn('WRT_LOSS','N'),
                  DbLogColumn('DIODE_TEMP','N'),
                           ]
            },
      'P_BURNISH_CHECK':
            {
                'type': 'M',
                'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('TEST_PSN','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),

                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('WRT_HTR_CLRNC_1','N'),

                  DbLogColumn('WRT_HTR_CLRNC_2','N'),
                  DbLogColumn('MOD_CALC_AVG_1','N'),
                  DbLogColumn('MOD_CALC_AVG_2','N'),
                  DbLogColumn('DELTA_BURNISH_CHECK','N'),

                  DbLogColumn('BRNSH_USL','N'),
                  DbLogColumn('HD_STATUS','N'),
                           ]
            },
      'P_TRIPLET_WPC':
            {
                'type': 'M',
                'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('DATA_ZONE','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('WRT_CUR','N'),
                  DbLogColumn('OVRSHT','N'),
                  DbLogColumn('OVRSHT_DUR','N'),
                  DbLogColumn('WPC','N'),
                  DbLogColumn('SLOPE','N'),
                  DbLogColumn('INTERCEPT','N'),
                  DbLogColumn('RSQ','N'),
                           ]
            },
      'P_TRIPLET_OSA_OSD':
            {
                'type': 'M',
                'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('DATA_ZONE','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('WRT_CUR','N'),
                  DbLogColumn('OVRSHT','N'),
                  DbLogColumn('OVRSHT_DUR','N'),
                  DbLogColumn('ERROR_RATE','N'),
                  DbLogColumn('SLOPE','N'),
                  DbLogColumn('INTERCEPT','N'),
                  DbLogColumn('RSQ','N'),
                  DbLogColumn('STATUS','N'),
                           ]
            },
      'P_AFH_DH_BURNISH_CHECK':
            {
                'type': 'S',
                'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),

                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('TEST_PSN','N'),

                  DbLogColumn('TEST_TYPE','V'),
                  DbLogColumn('ACTIVE_HEATER','V'),
                  DbLogColumn('CLR_ACTUATION_MODE','V'),

                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('WRT_HTR_CLR_1','N'),

                  DbLogColumn('WRT_HTR_CLR_2','N'),
                  DbLogColumn('MOD_CALC_AVG_1','N'),
                  DbLogColumn('MOD_CALC_AVG_2','N'),
                  DbLogColumn('DELTA_BURNISH_CHECK','N'),

                  DbLogColumn('BURNISH_USL','N'),
                  DbLogColumn('HD_STATUS','N'),
                  DbLogColumn('BURNISH_LSL','N'),
                           ]
            },
      'P51_DDIS_DEBUG':
          {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('FAIL_ZN', 'N'),
                  DbLogColumn('BASELINE_BER', 'N'),
                  DbLogColumn('ERASURE_BER', 'N'),
                  DbLogColumn('TRK_INDEX', 'N'),
                  DbLogColumn('FAIL_STATE', 'N'),
                  ]
           },
      'P_BURNISH_CHECK2':
            {
                'type': 'M',
                'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('TEST_PSN','N'),
                  DbLogColumn('ACTUATION_MODE','V'),
                  DbLogColumn('SPC_ID', 'V'),

                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),

                  DbLogColumn('STATE_NUM_2','N'),
                  DbLogColumn('CLRNC_2','N'),
                  DbLogColumn('STATE_NUM_1','N'),
                  DbLogColumn('CLRNC_1','N'),

                  DbLogColumn('DELTA_BURNISH_CHECK','N'),
                  DbLogColumn('BRNSH_USL','N'),
                  DbLogColumn('HD_STATUS','N'),
                           ]
            },

      'P_CLEARANCE_DELTAS':
            {
                'type': 'M',
                'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('TEST_PSN','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('WH_CLRNC_1','N'),
                  DbLogColumn('WH_CLRNC_2','N'),
                  DbLogColumn('WH_CLRNC_DELTA','N'),
                  DbLogColumn('HO_CLRNC_1','N'),
                  DbLogColumn('HO_CLRNC_2','N'),
                  DbLogColumn('HO_CLRNC_DELTA','N'),
                  DbLogColumn('WH_DAC_1','N'),
                  DbLogColumn('WH_DAC_2','N'),
                  DbLogColumn('WH_DAC_DELTA','N'),
                  DbLogColumn('HO_DAC_1','N'),
                  DbLogColumn('HO_DAC_2','N'),
                  DbLogColumn('HO_DAC_DELTA','N'),
                           ]
            },

      'P_DAC_CLR':
            {
                'type': 'M',
                'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('TRK_NUM','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),

                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('RD_HEAT_DAC','N'),

                  DbLogColumn('RD_CLR','N'),
                  DbLogColumn('RD_TEMP','N'),
                  DbLogColumn('WRT_HEAT_DAC','N'),
                  DbLogColumn('WRT_CLR','N'),

                  DbLogColumn('WRT_TEMP','N'),
                  DbLogColumn('CHK_NUM','N'),
                  DbLogColumn('MSRMNT_STATUS','V'),

                           ]
            },
      'P035_TEMP_CAP':
            {
                'type': 'V',
                'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('COLD_CAP','N'),
                  DbLogColumn('HOT_CAP','N'),
                           ]
            },
      'P_TEMP_LIMIT_WITH_0_WRT_HTR_DAC':
            {
                'type': 'V',
                'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('TCC1','N'),
                  DbLogColumn('TEMP_LIMIT1','N'),
                  DbLogColumn('TEMP_LIMIT2','N'),
                           ]
            },
      'P035_TEMP_CAP2':
            {
                'type': 'V',
                'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('COLD_CAP','N'),
                  DbLogColumn('HOT_CAP','N'),
                  DbLogColumn('REGION','N'),
                           ]
            },
      'P_DESTROKE_CLEARANCE':
           {
                'type': 'S',
                'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),

                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('LGC_TRK_NUM','N'),
                  DbLogColumn('NOM_CYL','N'),

                  DbLogColumn('RADIUS','N'),
                  DbLogColumn('ACTUATION_MODE','V'),
                  DbLogColumn('AFH_ZONE','N'),
                  DbLogColumn('HEATER_DAC','N'),

                  DbLogColumn('CLEARANCE','N'),
                  DbLogColumn('MIN_CLEARANCE_SPEC','N'),
                           ]
           },
      'P_CLEARANCE_SCREEN':
           {
                'type': 'M',
                'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),

                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('SCREEN_NAME','V'),
                  DbLogColumn('ACTUATION_MODE','V'),

                  DbLogColumn('ZONE1','N'),
                  DbLogColumn('CLEARANCE1','N'),
                  DbLogColumn('ZONE2','N'),
                  DbLogColumn('CLEARANCE2','N'),

                  DbLogColumn('DELTA_CLEARANCE','N'),
                  DbLogColumn('LIMIT','N'),
                           ]
           },
      'P_62KHZ_OD_CONTACT_MODULATION_CLEARANCE_SCREEN':
           {
                'type': 'M',
                'fieldList': [
                  DbLogColumn('SPC_ID', 'V',0),
                  DbLogColumn('OCCURRENCE', 'N',0),
                  DbLogColumn('SEQ', 'N',0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N',0),

                  DbLogColumn('HD_PHYS_PSN','N',0),
                  DbLogColumn('HD_LGC_PSN','N',0),
                  DbLogColumn('SCREEN_NAME','V',0),
                  DbLogColumn('ACTUATION_MODE','V',0),

                  DbLogColumn('OD_WHDAC','N',0),
                  DbLogColumn('ID_WHDAC','N',0),
                  DbLogColumn('evenHead/oddHead_OD_WHDAC_DELTA','N',0),


                  DbLogColumn('criteria1_WH_DAC_limit','N',0),
                  DbLogColumn('criteria2_WH_DAC_limit','N',0),
                  DbLogColumn('criteria3_WH_DAC_limit','N',0),

                  DbLogColumn('criteria1','N',0),
                  DbLogColumn('criteria2','N',0),
                  DbLogColumn('criteria3','N',0),
                  DbLogColumn('RESULT','N',0),

                           ]
           },
      'P_SWD_ADJUSTMENT':
            {
                'type': 'M',
                'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('DATA_ZONE','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('DIODE_TEMP','N'),
                  DbLogColumn('RD_CLR_ADJ','N'),
                  DbLogColumn('WRT_CLR_ADJ','N'),
                  DbLogColumn('RD_CLR_ADJ_PCT','N'),
                  DbLogColumn('WRT_CLR_ADJ_PCT','N'),
                           ]
            },
      'P211_VBAR_CAPS_WPPS':
            {
                'type': 'M',
                'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('DATA_ZONE','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('BPI_CAP','N'),
                  DbLogColumn('TPI_CAP','N'),
                  DbLogColumn('WP_PICK','N'),
                           ]
            },

      'P190_CSC_DATA':
            {
                  'type': 'S',
                  'fieldList':[
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('ITERATION',      'N'),
                  DbLogColumn('TRACK',          'N'),
                  DbLogColumn('HSC0',           'N'),
                  DbLogColumn('HSC1',           'N'),
                  DbLogColumn('HIRP2',          'N'),
                           ]
            },
      'P190_CSC_SUMMARY':
            {
                  'type': 'S',
                  'fieldList':[
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('BER_COLD',       'N'),
                  DbLogColumn('BER_HOT',        'N'),
                  DbLogColumn('BER_Delta',      'N'),
                  DbLogColumn('MAXCSC',         'N'),
                  DbLogColumn('MAXCSC1',        'N'),
                  DbLogColumn('STDEV',          'N'),
                  DbLogColumn('DECAY',          'N'),
                  DbLogColumn('MINCSC',         'N'),
                  DbLogColumn('MAXCSC2',        'N'),
                  DbLogColumn('REMARK',         'N'),
                  DbLogColumn('MAXCSC1_HAP',    'N'),
                  DbLogColumn('DECAY_HAP',      'N'),
                           ]
            },
            
      'P190_TCC_DATA':
            {
                  'type': 'S',
                  'fieldList':[
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('TRACK',          'N'),
                  DbLogColumn('HSC_RH',            'N'),
                  DbLogColumn('HSC_WH',            'N'),
                           ]
            },

      'P190_DIHA_DATA':
            {
                  'type': 'S',
                  'fieldList':[
                  DbLogColumn('SPC_ID', 'N'),
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('TRACK',          'N'),
                  DbLogColumn('REV',          'N'),
                  DbLogColumn('HSC_MEAN',            'N'),
                  DbLogColumn('HSC_STDEV',            'N'),
                           ]
            },

      'P190_DIHA_SUMMARY':
            {
                  'type': 'S',
                  'fieldList':[
                  DbLogColumn('SPC_ID', 'N'),
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  #DbLogColumn('TRACK',          'N'),
                  DbLogColumn('HSC_MEAN_MEAN',            'N'),
                  DbLogColumn('HSC_STDEV_MEAN',            'N'),
                  DbLogColumn('HSC_MEAN_STDEV',            'N'), 
                  DbLogColumn('HSC_STDEV_STDEV',            'N'),
                  DbLogColumn('HSC_STDEV2_MEAN',            'N'),
                  DbLogColumn('HSC_STDEV2_STDEV',            'N'),
                           ]
            },

      'P190_TCC_SUMMARY':
            {
                  'type': 'S',
                  'fieldList':[
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('TRACK',          'N'),
                  DbLogColumn('HSC0_RH',        'N'),
                  DbLogColumn('HSC0_WH',        'N'),                  
                  DbLogColumn('HSC1_RH',        'N'),
                  DbLogColumn('HSC1_WH',        'N'),                  
                  DbLogColumn('HIRP2_RH',       'N'),
                  DbLogColumn('HIRP2_WH',       'N'),                  
                  DbLogColumn('TC1_RH',         'N'),
                  DbLogColumn('TC1_WH',         'N'),
                  DbLogColumn('TEMP_HI',        'N'),
                  DbLogColumn('TEMP_LO',        'N'),
                           ]
            },

      'P190_TEST_TRACKS':
            {
                  'type': 'S',
                  'fieldList':[
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('HD_LGC_PSN',     'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('TRK_NUM',        'N'),
                  DbLogColumn('TRK_RANGE',      'N'),
                           ]
            },
            
      'P190_SKLOSS_DATA_BASE':
            {
                  'type': 'S',
                  'fieldList':[
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('TRACK',          'N'),
                  DbLogColumn('HSC_RH',            'N'),
                  DbLogColumn('HSC_WH',            'N'),
                           ]
            },
      'P190_SKLOSS_DATA_ODID':
            {
                  'type': 'S',
                  'fieldList':[
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('TRACK',          'N'),
                  DbLogColumn('HSC0_RH',        'N'),
                  DbLogColumn('HSC0_WH',        'N'),                  
                  DbLogColumn('HSC1_RH',        'N'),
                  DbLogColumn('HSC1_WH',        'N'),                  
                  DbLogColumn('HIRP2_RH',       'N'),
                  DbLogColumn('HIRP2_ODID',       'N'),                  
                           ]
            },
      'P190_SKLOSS_DATA_IDOD':
            {
                  'type': 'S',
                  'fieldList':[
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('TRACK',          'N'),
                  DbLogColumn('HSC0_RH',        'N'),
                  DbLogColumn('HSC0_WH',        'N'),                  
                  DbLogColumn('HSC1_RH',        'N'),
                  DbLogColumn('HSC1_WH',        'N'),                  
                  DbLogColumn('HIRP2_RH',       'N'),
                  DbLogColumn('HIRP2_IDOD',       'N'),                  
                           ]
            },

      'P211_HMS_CAP_AVG':
            {
                'type': 'S',
                'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('DATA_ZONE','N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('NUM_TRKS_TESTED','N'),
                  DbLogColumn('HMS_CAP_AVG','N'),
                  DbLogColumn('ZERO_HEAT_CLR','N'),
                  DbLogColumn('CAP_SLOPE','N'),
                           ]
            },
      'P211_HMS_CAP_AVG2':
            {
                'type': 'S',
                'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('DATA_ZONE','N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('NUM_TRKS_TESTED','N'),
                  DbLogColumn('HMS_CAP_AVG','N'),
                  DbLogColumn('ZERO_HEAT_CLR','N'),
                  DbLogColumn('CAP_SLOPE','N'),
                  DbLogColumn('CAP_PENALTY','N'),
                           ]
            },
      'P_VBAR_NIBLET':
            {
                'type': 'S',
                'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('CAP_TRGT', 'N'),
                  DbLogColumn('NUM_HEADS', 'N'),
                  DbLogColumn('BPI_MIN_AVG', 'N'),
                  DbLogColumn('BPI_MAX_AVG', 'N'),
                  DbLogColumn('TPI_MRGN_FACTOR', 'N'),
                  DbLogColumn('BPI_MRGN_THRSHLD', 'N'),
                  DbLogColumn('TPI_MRGN_THRSHLD', 'N'),
                  DbLogColumn('BPI_MEAS_MRGN', 'N'),
                  DbLogColumn('TPI_MEAS_MRGN', 'N'),
                  DbLogColumn('TPI_OVERCOMP_FACTOR', 'N'),
                  DbLogColumn('BPI_OVERCOMP_FACTOR', 'N'),
                  DbLogColumn('BPI_TPI_OVERCOMP_FACTOR', 'N'),
                           ]
            },
      'P_VBAR_SUMMARY2':
            {
               'type': 'V',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('BPI_CAP', 'N'),
                  DbLogColumn('BPI_PICK', 'N'),
                  DbLogColumn('BPI_MRGN', 'N'),
                  DbLogColumn('BPI_TABLE_NUM', 'N'),
                  DbLogColumn('TPI_CAP', 'N'),
                  DbLogColumn('TPI_PICK', 'N'),
                  DbLogColumn('TPI_MRGN', 'N'),
                  DbLogColumn('TPI_TABLE_NUM', 'N'),
                           ]
            },

      'P_VBAR_FORMAT_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('BPI_CAP', 'N'),
                  DbLogColumn('BPI_INTERPOLATED', 'V'),
                  DbLogColumn('BPI_PICK', 'N'),
                  DbLogColumn('BPI_MRGN', 'N'),
                  DbLogColumn('BPI_TABLE_NUM', 'N'),
                  DbLogColumn('TPI_CAP', 'N'),
                  DbLogColumn('TPI_INTERPOLATED', 'V'),
                  DbLogColumn('TPI_PICK', 'N'),
                  DbLogColumn('TPI_MRGN', 'N'),
                  DbLogColumn('TPI_TABLE_NUM', 'N'),
                           ]
            },
      'P_VBAR_FORMAT_SUMMARY_SMR':
            {
               'type': 'S',
               'fieldList': [
                  #DbLogColumn('SPC_ID', 'V'),
                  #DbLogColumn('OCCURRENCE', 'N'),
                  #DbLogColumn('SEQ', 'N'),
                  #DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('BPI_CAP', 'N'),
                  DbLogColumn('BPI_MAX', 'N'),
                  DbLogColumn('BPI_PICK', 'N'),
                  DbLogColumn('BPI_MRGN', 'N'),
                  DbLogColumn('TPI_CAP_S', 'N'),
                  DbLogColumn('TPI_MAX_S', 'N'),
                  DbLogColumn('TPI_PICK_S', 'N'),
                  DbLogColumn('TPI_MRGN_S', 'N'),
                  DbLogColumn('TPI_CAP_F', 'N'),
                  DbLogColumn('TPI_MAX_F', 'N'),
                  DbLogColumn('TPI_PICK_F', 'N'),
                  DbLogColumn('TPI_MRGN_F', 'N'),
                           ]
            },
            
      'P_VBAR_ADC_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('PARAMETER_NAME', 'V'),                  
                  DbLogColumn('DRV_CAPACITY', 'N'),                                                                     
                           ]
            },
      'P_VBAR_THRUPUT_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  #DbLogColumn('SPC_ID', 'V'),
                  #DbLogColumn('OCCURRENCE', 'N'),
                  #DbLogColumn('SEQ', 'N'),
                  #DbLogColumn('TEST_SEQ_EVENT', 'N'),                  
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('ZN_THRUPUT_NOM', 'N'),
                  DbLogColumn('ZN_THRUPUT_LIMIT', 'N'),
                  DbLogColumn('INIT_THRUPUT', 'N'),         
                  DbLogColumn('END_THRUPUT', 'N'),
                  DbLogColumn('RESULT', 'V'),
                           ]
            },
      'P_VBAR_THRUPUT_BPI_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('BPI_CAP', 'N'),
                  DbLogColumn('BPIP', 'N'),
                  DbLogColumn('BPI_MRGN', 'N'),
                  DbLogColumn('BPI_TABLE_NUM', 'N'),
                           ]
            },
      'P_VBAR_ATI_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  #DbLogColumn('SPC_ID', 'V'),
                  #DbLogColumn('OCCURRENCE', 'N'),
                  #DbLogColumn('SEQ', 'N'),
                  #DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('ATIC_OTF', 'N'),
                  DbLogColumn('STEC_OTF', 'N'),
                  DbLogColumn('ATIP_OTF', 'N'),         
                  DbLogColumn('TPIM', 'N'),
                  DbLogColumn('BPIM', 'N'),
                  DbLogColumn('WORSE_POS', 'N'),
                  DbLogColumn('ITER', 'N'),                                                    
                           ]
            },            
      'P_VBAR_MAX_FORMAT_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('BPI_CAP', 'N'),
                  DbLogColumn('BPIM_SEG', 'N'),
                  DbLogColumn('BPIM_FSOW', 'N'),
                  DbLogColumn('BPIM_HMS', 'N'),
                  DbLogColumn('BPIM_SQZBPIC', 'N'),
                  DbLogColumn('BPIM_FINAL', 'N'),
                  DbLogColumn('BPIP_MAX', 'N'),
                  DbLogColumn('TPI_CAP', 'N'),
                  DbLogColumn('TPIM_ATI', 'N'),
                  DbLogColumn('TPIP_MAX', 'N'),
                  DbLogColumn('ADC_MAX', 'N'),
                  DbLogColumn('NIBLET_IDX', 'N'),
                           ]
            },
      'P_SQZ_BPIC_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('BPIC', 'N'),
                  DbLogColumn('SQZBPIC_ODSS', 'N'),
                  DbLogColumn('SQZBPIC_ODSS', 'N'),
                  DbLogColumn('SQZBPIC', 'N'),
                  DbLogColumn('BPIM', 'N'),
                           ]
            },
      'P_TPI_SOVA_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('TGT_SOVA_BER', 'N'),
                  DbLogColumn('ACT_SOVA_BER', 'N'),
                  DbLogColumn('TPIM_SOVA', 'N'),
                           ]
            },
      'P_VBAR_BPI_SLOPE_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  #DbLogColumn('SPC_ID', 'V'),
                  #DbLogColumn('OCCURRENCE', 'N'),
                  #DbLogColumn('SEQ', 'N'),
                  #DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('BPI_SLOPE', 'N'),
                  DbLogColumn('BPI_INTCPT', 'N'),
                  DbLogColumn('BPI_RSQ', 'N'),
                  DbLogColumn('TGT_BER', 'N'),
                  DbLogColumn('BPIM_RSEG', 'N'),
                  DbLogColumn('BPIM_RFSW', 'N'),
                  DbLogColumn('BPI_CUR', 'N'),
                  DbLogColumn('BPI_CAP', 'N'),
                           ]
            },
      'P_VBAR_HMS_SLOPE_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  #DbLogColumn('SPC_ID', 'V'),
                  #DbLogColumn('OCCURRENCE', 'N'),
                  #DbLogColumn('SEQ', 'N'),
                  #DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('HMS_SLOPE', 'N'),
                  DbLogColumn('HMS_INTCPT', 'N'),
                  DbLogColumn('HMS_RSQ', 'N'),
                  DbLogColumn('BPI_CAP', 'N'),
                  DbLogColumn('HMS_CAP', 'N'),
                  DbLogColumn('HMS_TGT', 'N'),
                  DbLogColumn('BPI_HMS', 'N'),
                  DbLogColumn('BPIM_HMS', 'N'),
                           ]
            },
      'P_VBAR_CAP_SUMMARY_BY_HD':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('BPI_CAP_AVG', 'N'),
                  DbLogColumn('BPI_CAP_MIN', 'N'),
                  DbLogColumn('BPI_MRGN_AVG', 'N'),
                  DbLogColumn('BPI_MRGN_MIN', 'N'),
                  DbLogColumn('VZB_TABLE', 'N'),
                  DbLogColumn('TPI_CAP_AVG', 'N'),
                  DbLogColumn('TPI_CAP_MIN', 'N'),
                  DbLogColumn('TPI_MRGN_AVG', 'N'),
                  DbLogColumn('TPI_MRGN_MIN', 'N'),
                           ]
            },
      'P_VBAR_BANDED_FMT_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('BPIC', 'N'),
                  DbLogColumn('TPI_DSS', 'N'),
                  DbLogColumn('TPI_IDSS', 'N'),
                  DbLogColumn('TPI_ODSS', 'N'),
                  DbLogColumn('TPI_EFF', 'N'),
                  DbLogColumn('TPI_MAX', 'N'),
                  DbLogColumn('RD_OFFSET', 'N'),
                  DbLogColumn('DIR', 'V'),
                           ]
            },
      'P_VBAR_OTC_RAW_OFFSET':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('NUM_WRITE', 'N'),
                  DbLogColumn('NOSS_N_OFFSET', 'N'),
                  DbLogColumn('NOSS_P_OFFSET', 'N'),
                  DbLogColumn('IDSS_N_OFFSET', 'N'),
                  DbLogColumn('IDSS_P_OFFSET', 'N'),
                  DbLogColumn('ODSS_N_OFFSET', 'N'),
                  DbLogColumn('ODSS_P_OFFSET', 'N'),
                           ]
            },
      'P_VBAR_OTC_SUMMARY2':
            {
               'type': 'S',
               'fieldList': [
                  #DbLogColumn('SPC_ID', 'V'),
                  #DbLogColumn('OCCURRENCE', 'N'),
                  #DbLogColumn('SEQ', 'N'),
                  #DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('BPIC', 'N'),
                  DbLogColumn('TPI_DSS', 'N'),
                  DbLogColumn('TPI_IDSS', 'N'),
                  DbLogColumn('TPI_ODSS', 'N'),
                  DbLogColumn('TPI_INTER', 'N'),
                  DbLogColumn('TPI_INTRA', 'N'),
                  DbLogColumn('TPI_UMP', 'N'),
                  DbLogColumn('INTRA_IDSS', 'N'),
                  DbLogColumn('INTRA_ODSS', 'N'),
                  DbLogColumn('OTC_NOSS', 'N'),
                  DbLogColumn('OTC_IDSS', 'N'),
                  DbLogColumn('OTC_ODSS', 'N'),
                  DbLogColumn('RD_OFFSET', 'N'),
                  DbLogColumn('DIR', 'V'),
                  DbLogColumn('TG_CAP', 'N'),
                  DbLogColumn('TG_TUNED', 'N'),
                  DbLogColumn('EQV_TG_COEF', 'N'),
                  DbLogColumn('TPIC_FAT', 'N'),
                  DbLogColumn('INTER_MARGIN', 'N'),
                  DbLogColumn('INTRA_MARGIN', 'N'),
                           ]
            },
      'P_VBAR_OTC_BAND_SCRN':
            {
               'type': 'S',
               'fieldList': [
                  #DbLogColumn('SPC_ID', 'V'),
                  #DbLogColumn('OCCURRENCE', 'N'),
                  #DbLogColumn('SEQ', 'N'),
                  #DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('OTC_NOSS', 'N'),
                  DbLogColumn('OTC_FAT', 'N'),
                  DbLogColumn('OTC_FSLIM', 'N'),
                  DbLogColumn('OTC_LSLIM', 'N'),
                  DbLogColumn('DIR', 'V'),
                           ]
            },
      'P_VBAR_2D_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  #DbLogColumn('SPC_ID', 'V'),
                  #DbLogColumn('OCCURRENCE', 'N'),
                  #DbLogColumn('SEQ', 'N'),
                  #DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('TARGET_SFR', 'N'),
                  DbLogColumn('BPIC', 'N'),
                  DbLogColumn('TPI_DSS', 'N'),
                  DbLogColumn('TPI_IDSS', 'N'),
                  DbLogColumn('TPI_ODSS', 'N'),
                  DbLogColumn('TPI_EFF', 'N'),
                  DbLogColumn('ADC_EFF', 'N'),
                  DbLogColumn('ADC_CMR', 'N'),
                  DbLogColumn('ADC_SMR', 'N'),
                  DbLogColumn('RD_OFFSET', 'N'),
                  DbLogColumn('DIR', 'V'),
                           ]
            },
      'P_VBAR_2D_BEST_SOVA_BY_ZONES':
            {
               'type': 'S',
               'fieldList': [
                  #DbLogColumn('SPC_ID', 'V'),
                  #DbLogColumn('OCCURRENCE', 'N'),
                  #DbLogColumn('SEQ', 'N'),
                  #DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('BEST_SOVA', 'N'),
                  DbLogColumn('BPIC', 'N'),
                           ]
            },
      'P_VBAR_WRT_FAULT_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('TPI_MRGN_MIN', 'N'),
                  DbLogColumn('WRT_FAULT_ADJUSTMENT', 'N'),
                  DbLogColumn('WRT_FAULT_FINAL', 'N'),
                           ]
            },

      'P_EVENT_SUMMARY':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('RUN_TIME', 'N'),
                  DbLogColumn('SLOT', 'N'),
                  DbLogColumn('COMPLETION_CODE', 'N'),
                  DbLogColumn('FAILING_SEQ', 'N'),
                  DbLogColumn('FAILING_TEST', 'N'),
                  DbLogColumn('FAILING_SEQ_VER', 'N'),
                  DbLogColumn('FAILING_PORTID', 'N'),
                  DbLogColumn('FAILING_EVENT', 'N'),
                  DbLogColumn('FAILING_SQ_EVT', 'N'),
                  DbLogColumn('FAILING_TST_EVT', 'N'),
                  DbLogColumn('FAILING_TS_EVT', 'N'),
                  DbLogColumn('FAILING_5V', 'N'),
                  DbLogColumn('FAILING_12V', 'N'),
                  DbLogColumn('FAILING_TEMP', 'N'),
                  DbLogColumn('SUB_BUILD_GROUP', 'V'),
                  DbLogColumn('EQUIP_ID', 'V'),
                  DbLogColumn('CM_VERSION', 'V'),
                  DbLogColumn('HOST_VER', 'V'),
                  DbLogColumn('CONFIG_NAME', 'V'),
                  DbLogColumn('CONFIG_VER', 'V'),
                  DbLogColumn('DEX_VER', 'V'),
                  DbLogColumn('PWR_LOSS_CNT', 'N'),
                  DbLogColumn('PARAM_DICTIONARY_VER', 'N'),
                  DbLogColumn('FAIL_STATE', 'V'),
                  DbLogColumn('FAIL_DATA', 'V'),
                  DbLogColumn('FAIL_PARAMETER_NAME', 'V'),
                           ]
           },
      'P_VBAR_MEASUREMENTS':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('WRT_PWR_NDX','N'),
                  DbLogColumn('BPI_CAP', 'N'),
                  DbLogColumn('TPI_CAP', 'N'),
                  DbLogColumn('HMS_CAP', 'N'),
                  DbLogColumn('ADC', 'N'),
                  DbLogColumn('BPICHMS', 'N'),
                           ]
           },
      'P_VBAR_FORMAT_SUMMARY_ZN0':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('BPIC_ORIG', 'N'),
                  DbLogColumn('BPIC_FSOW', 'N'),
                  DbLogColumn('BPIC_SEGM', 'N'),
                  DbLogColumn('BPIC_MINM', 'N'),
                  DbLogColumn('BPIC_FINL', 'N'),
                  DbLogColumn('BPIC_ORIG_SCALE', 'N'),
                  DbLogColumn('BPIC_FINL_SCALE', 'N'),
                  DbLogColumn('TPIC_ORIG', 'N'),
                  DbLogColumn('TPIC_FINL', 'N'),
                  DbLogColumn('TPIC_ORIG_SCALE', 'N'),
                  DbLogColumn('TPIC_FINL_SCALE', 'N'),
                           ]
            },

      'VBAR_PICKER_DATA':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HEAD',  'N'),
                  DbLogColumn('ZONE',  'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('WRCLR', 'N'),
                  DbLogColumn('WRPWR', 'N'),
                  DbLogColumn('FREQ',  'N'),
                  DbLogColumn('CLRWHT','N'),
                  DbLogColumn('WPWHT', 'N'),
                  DbLogColumn('BPIC',  'N'),
                  DbLogColumn('FBPIC', 'N'),
                  DbLogColumn('TPIC',  'N'),
                  DbLogColumn('FTPIC', 'N'),
                           ]
           },
      'P_WRT_PWR_PICKER':
            {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('WRT_PWR_NDX', 'N'),
                  DbLogColumn('WRT_HEAT_CLRNC', 'N'),
                  DbLogColumn('CLRNC_WGHT_FUNC', 'N'),
                  DbLogColumn('STRTN_PWR_WGHT_FUNC', 'N'),
                  DbLogColumn('FITNESS_PWR_WGHT_FUNC', 'N'),
                  DbLogColumn('BPI_CAP', 'N'),
                  DbLogColumn('FLTR_BPI_CAP', 'N'),
                  DbLogColumn('TPI_CAP', 'N'),
                  DbLogColumn('FLTR_TPI_CAP', 'N'),
                  DbLogColumn('SATURATION_PEAK', 'N'),
                  DbLogColumn('CAPACITY_CALC', 'N'),
                  DbLogColumn('SATURATION_PICK', 'V'),
                  DbLogColumn('CAPACITY_PICK', 'V'),
                           ]
            },
      'P_TRIPLET_ATI_STE_TEST':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE',  'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('WP_INDEX', 'N'),
                  DbLogColumn('WRT_CUR', 'N'),
                  DbLogColumn('OVRSHT_AMP',  'N'),
                  DbLogColumn('OVRSHT_DUR','N'),
                  DbLogColumn('WORSE_BASE_BER', 'N'),
                  DbLogColumn('WORSE_ATI_BER', 'N'),
                  DbLogColumn('DELTA_ATI_BER',  'N'),
                  DbLogColumn('WORSE_STE_BER', 'N'),
                  DbLogColumn('DELTA_STE_BER',  'N'),
                  DbLogColumn('STATUS', 'N'),
                           ]
           },
      'P_TRIPLET_OW_HMS_TEST':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE',  'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('WP_INDEX', 'N'),
                  DbLogColumn('WRT_CUR', 'N'),
                  DbLogColumn('OVRSHT_AMP',  'N'),
                  DbLogColumn('OVRSHT_DUR','N'),
                  DbLogColumn('OW', 'N'),
                  DbLogColumn('HMSC', 'N'),
                  DbLogColumn('STATUS', 'N'),
                           ]
           },
      'P_WRT_PWR_TRIPLETS':
            {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('WRT_PWR_NDX', 'N'),
                  DbLogColumn('ZONE_TYPE', 'V'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('WRT_CUR', 'N'),
                  DbLogColumn('OVRSHT', 'N'),
                  DbLogColumn('OVRSHT_DUR', 'N'),
                           ]
            },
      'P_DELTA_FB_PICK':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DELTA_FB_PICK', 'N'),
                           ]
            },
      'P_SDAT_INFO':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SBR', 'N',0),
                  DbLogColumn('START_DATE', 'N',0),
                  DbLogColumn('PROJECT', 'N',0),
                  DbLogColumn('SN', 'N',0),
                  DbLogColumn('INTERFACE', 'N',0),
                  DbLogColumn('TESTER', 'N',0),
                  DbLogColumn('SLOT_NUM', 'N',0),
                  DbLogColumn('TEMP', 'N',0),
                  DbLogColumn('VOLTS_5', 'N',0),
                  DbLogColumn('VOLTS_12', 'N',0),
                  DbLogColumn('MULTI', 'N',0),
                  DbLogColumn('MAX_CONT', 'N',0),
                  DbLogColumn('S_TPI', 'N',0),
                  DbLogColumn('MAX_CYL', 'N',0),
                  DbLogColumn('PLOT_TYPE', 'N',0),
                  DbLogColumn('T150_METHOD', 'N',0),
                  DbLogColumn('MIXED_RATE_NOTCH_NUM', 'N',0),
                  DbLogColumn('TMR_VERIFY', 'N',0),
                  DbLogColumn('TRACK_FOLLOW', 'N',0),
                  DbLogColumn('DCSQ', 'N',0),
                  DbLogColumn('DUAL_STAGE', 'N',0),
                  DbLogColumn('T288_BODE', 'N',0),
                  DbLogColumn('CUSTOM_RV', 'N',0),
                           ]
           },
      'P_SDAT_ECCENTRICITY':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('HEAD', 'N',0),
                  DbLogColumn('SIN', 'N',0),
                  DbLogColumn('COS', 'N',0),
                  DbLogColumn('ECCENTRICITY', 'N',0),
                           ]
           },
      'P_SDAT_CONTROLLER_MAP':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('HEAD', 'N',0),
                  DbLogColumn('CONT', 'N',0),
                           ]
           },
      'P_SDAT_TMR_VERF':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('NUM_PTS', 'N',0),
                  DbLogColumn('REVS', 'N',0),
                           ]
           },
      'P_SDAT_TMR_VERF_HI_RO':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('HD', 'N',0),
                  DbLogColumn('HI_RRO_TRK', 'N',0),
                  DbLogColumn('HI_RRO', 'N',0),
                  DbLogColumn('HI_NRRO_TRK', 'N',0),
                  DbLogColumn('HI_NRRO', 'N',0),
                           ]
           },
      'P_SDAT_MAM_BS':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('HD', 'N',0),
                  DbLogColumn('MAM_PRE', 'N',0),
                  DbLogColumn('BS_PRE', 'N',0),
                  DbLogColumn('NUM_SEEKS', 'N',0),
                  DbLogColumn('MAM_POST', 'N',0),
                  DbLogColumn('BS_POST', 'N',0),
                  DbLogColumn('SECS', 'N',0),
                           ]
           },
      'P_SDAT_PES':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('TID', 'N',0),
                  DbLogColumn('HD', 'N',0),
                  DbLogColumn('CYL', 'N',0),
                  DbLogColumn('RAWRO', 'N',0),
                  DbLogColumn('RRO', 'N',0),
                  DbLogColumn('NRRO', 'N',0),
                           ]
           },
      'P_SDAT_TRK0':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('HD', 'N',0),
                  DbLogColumn('TRK0', 'N',0),
                           ]
           },
      'P_GROWN_DEFECT_LIST':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('PBA', 'N'),
                  DbLogColumn('ERR_LENGTH', 'N'),
                  DbLogColumn('RW_FLAGS', 'V'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('PHYS_TRK_NUM', 'N'),
                  DbLogColumn('PHYS_SECTOR', 'N'),
                           ]
           },
      'P_PENDING_DEFECT_LIST':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('TOTAL_DFCTS_DRIVE', 'N'),
                           ]
           },
      'P_ENC_LOG_DEF':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('TRK_LGC_NUM', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('TRK_PHYS_NUM', 'N'),
                  DbLogColumn('LBA', 'N'),
                  DbLogColumn('SECTOR_LGC', 'N'),
                  DbLogColumn('SECTOR_PHYS', 'N'),
                           ]
           },

      'P_QUICK_ERR_RATE':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('TRK_NUM', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('RBIT', 'N'),
                  DbLogColumn('RRAW', 'N'),
                  DbLogColumn('OTF', 'N'),
                  DbLogColumn('HARD', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                           ]
           },

      'P_DELTA_RRAW':
            {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('DATA_ZONE', 'N', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('DELTA_RRAW', 'N', 0),
                           ]
            },

      'P_DELTA_OTF':
            {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('DATA_ZONE', 'N', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('TRK_NUM', 'N', 0),
                  DbLogColumn('DELTA_OTF', 'N', 0)
                           ]
            },
      'P_DELTA_OTF_2':
            {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('DELTA_OTF', 'N', 0)
                           ]
            },
      'P_AVERAGE_ERR_RATE':
           {
               'type': 'V',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('SUM_QBER', 'N'),
                  DbLogColumn('CNT_QBER', 'N'),
                  DbLogColumn('AVG_QBER', 'N'),
                           ]
           },

      'P_SERVOVGA':
          {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('TRK_NUM', 'N'),
                  DbLogColumn('ZONE', 'N'),
                  DbLogColumn('SERVOVGA', 'N'),
                           ]
           },

      'P_DELTAVGA':
           {
               'type': 'V',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DELTAVGA', 'N'),
                           ]
           },

      'P_SIDE_ENCROACH_BER':
          {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('TRK_NUM', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DELTA_BER_PERCENTAGE', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('BASELINE_BER', 'N'),
                  DbLogColumn('ERASURE_BER', 'N'),
                  DbLogColumn('DELTA_BER', 'N'),
                  DbLogColumn('TYPE', 'V'),
                  DbLogColumn('WRT_TRK_AWAY_TUT_NDX', 'N'),
                  ]
           },

      'P172_AREAL_DENSITY_VBAR':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('AREAL_DENSITY_BPI', 'N'),
                  DbLogColumn('AREAL_DENSITY_TPI', 'N'),
                  DbLogColumn('AREAL_DENSITY_VBAR', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  ]
           },
      'P210_VBAR_THRSHLD':
           {
               'type': 'V',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('TPI_VBAR_SERT', 'N'),
                  DbLogColumn('BPI_VBAR_SERT', 'N'),
                  ]
           },
      'P210_CAPACITY_HD2':
           {
               'type':'V',
               'fieldList':[
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('HD_CAPACITY','N'),
               ]
           },
      'P210_CAPACITY_DRIVE':
           {
               'type':'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('DRV_CAPACITY','N'),
               ]
           },
      'TEST_TIME_BY_STATE':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('OPER', 'V'),
                  DbLogColumn('STATE_NAME', 'V'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('START_TIME', 'D'),
                  DbLogColumn('END_TIME', 'D'),
                  DbLogColumn('ELAPSED_TIME','N'),
                  DbLogColumn('CPU_ELAPSED_TIME','N'),
                  DbLogColumn('SZ_START','N'),
                  DbLogColumn('RSS_START','N'),
                  DbLogColumn('SZ_END','N'),
                  DbLogColumn('RSS_END','N'),
                  DbLogColumn('DRIVE_TEMP','N'),
                            ]
           },
      'TESTER_TIMESTAMP':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('OP_NAME', 'V'),
                  DbLogColumn('EQUIP_ID', 'V'),
                  DbLogColumn('EQUIP_TYPE', 'V'),
                  DbLogColumn('TEST_TYPE', 'V'),  # Place holder, for consistency with ST10 CTMX
                  DbLogColumn('AUTOMATION_TIME', 'D'),
                  DbLogColumn('SCAN_TIME', 'D'),
                  DbLogColumn('INSERT_TIME', 'D'),
                  DbLogColumn('OPERATION_START_TIME', 'D'),
                  DbLogColumn('FIRST_TEST_TIME', 'D'),  # Place holder, for consistency with ST10 CTMX
                  DbLogColumn('LAST_TEST_TIME', 'D'),  # Place holder, for consistency with ST10 CTMX
                  DbLogColumn('OPERATION_PF_TIME', 'D'),
                            ]
           },
      'P_MINOR_FAIL_CODE':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('TEST_NUMBER', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('ERROR_CODE', 'V'),
                  DbLogColumn('FAIL_DATA', 'V'),
                           ]
           },
      'P_FORMAT_ZONE_ERROR_RATE':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('ECC_LEVEL', 'N'),
                  DbLogColumn('NUM_READ_RETRIES', 'N'),
                  DbLogColumn('BITS_READ_LOG10', 'N'),
                  DbLogColumn('HARD_ERROR_RATE', 'N'),
                  DbLogColumn('SOFT_ERROR_RATE', 'N'),
                  DbLogColumn('OTF_ERROR_RATE', 'N'),
                  DbLogColumn('RAW_ERROR_RATE', 'N'),
                  DbLogColumn('BITS_WRITTEN_LOG10', 'N'),
                  DbLogColumn('BITS_UNWRITEABLE_LOG10', 'N'),
                  DbLogColumn('BITS_WITH_WRT_RETRY_LOG10', 'N'),
                  DbLogColumn('SYMBOLS_READ_LOG10', 'N'),
                  DbLogColumn('SYMBOL_ERROR_RATE', 'N'),
                                       ]
           },
      'P_WEAK_WRITE_BER_DELTA':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('HEAD', 'N', 0),
                  DbLogColumn('ZONE', 'N', 0),
                  DbLogColumn('RBIT', 'N', 0),
                  DbLogColumn('HARD_ERROR_RATE', 'N', 0),
                  DbLogColumn('HARD_ERROR_DELTA', 'N', 0),
                  DbLogColumn('OTF_ERROR_RATE', 'N', 0),
                  DbLogColumn('OTF_ERROR_DELTA', 'N', 0),
                  DbLogColumn('RAW_ERROR_RATE', 'N', 0),
                  DbLogColumn('RAW_ERROR_DELTA', 'N', 0),
                                       ]
           },
      'P_DELTA_ERROR_RATE':
           {
               'type': 'S',
               'fieldList' : [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('BITS_READ_LOG10', 'N'),
                  DbLogColumn('HARD_ERROR_RATE', 'N'),
                  DbLogColumn('HARD_ERROR_DELTA', 'N'),
                  DbLogColumn('OTF_ERROR_RATE', 'N'),
                  DbLogColumn('OTF_ERROR_DELTA', 'N'),
                  DbLogColumn('RAW_ERROR_RATE', 'N'),
                  DbLogColumn('RAW_ERROR_DELTA', 'N'),
                             ]
           },
      'P_HEAD_ERROR_RATE':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('BITS_READ_LOG10', 'N'),
                  DbLogColumn('HARD_ERROR_RATE', 'N'),
                  DbLogColumn('SOFT_ERROR_RATE', 'N'),
                  DbLogColumn('OTF_ERROR_RATE', 'N'),
                  DbLogColumn('RAW_ERROR_RATE', 'N'),
                  DbLogColumn('SYMBOLS_READ_LOG10', 'N'),
                  DbLogColumn('SYMBOL_ERROR_RATE', 'N'),
                  DbLogColumn('BITS_WRITTEN_LOG10', 'N'),
                  DbLogColumn('BITS_UNWRITEABLE_LOG10', 'N'),
                  DbLogColumn('BITS_WITH_WRT_RETRY_LOG10', 'N'),
                                       ]
           },
      'P000_DEFECTIVE_PBAS':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('NUMBER_OF_PBAS', 'N'),
                  DbLogColumn('RLIST_SECTORS', 'N'),
                  DbLogColumn('RLIST_WEDGES', 'N'),
                                       ]
           },
      'CCT_SPC_2':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('CMD_TIME', 'N', 0),
                  DbLogColumn('TEST_NUMBER', 'N', 0),
                  ]
           },

      'CCT_SPC_3':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('CMD_TIME', 'N', 0),
                  DbLogColumn('TEST_NUMBER', 'N', 0),
                  ]
           },

      'CCT_SPC_15':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('CMD_TIME', 'N', 0),
                  DbLogColumn('TEST_NUMBER', 'N', 0),
                  ]
           },


      'P_CCT_DISTRIBUTION':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('CCT_BIN_NUM', 'N', 0),
                  DbLogColumn('BIN_THRESHOLD', 'N', 0),
                  DbLogColumn('BIN_ENTRIES', 'N', 0),
                  ]
           },

      'P_CCT_MAX_CMD_TIMES':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('CMD_RANK', 'N', 0),
                  DbLogColumn('CMD_TIME', 'N', 0),
                  DbLogColumn('LBA', 'N', 0),
                  ]
           },

      'P_TIME_TO_READY':
           {
               'type':  'S',
               'fieldList':  [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('SET_3V', 'N'),
                  DbLogColumn('SET_5V', 'N'),
                  DbLogColumn('SET_12V', 'N'),
                  DbLogColumn('SENSE_VOLTAGE_3V', 'N'),
                  DbLogColumn('SENSE_VOLTAGE_5V', 'N'),
                  DbLogColumn('SENSE_VOLTAGE_12V', 'N'),
                  DbLogColumn('SENSE_CURRENT_3V', 'N'),
                  DbLogColumn('SENSE_CURRENT_5V', 'N'),
                  DbLogColumn('SENSE_CURRENT_12V', 'N'),
                  DbLogColumn('POWER_OPTIONS', 'V'),
                  DbLogColumn('DEVICE_ERROR_RGSTR', 'N'),
                  DbLogColumn('DEVICE_STATUS_RGSTR', 'N'),
                  DbLogColumn('SPIN_UP_TIME_TO_READY', 'N'),
               ]
           },
      'FBP_TABLE': # field balance plane (dummy DBLog not sent to FIS by adding to TestParameters.py parametric_no_load) knl
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('FBP1_COL', 'N'), # from attribute FBP1
                  DbLogColumn('FBP2_COL', 'N'), # from attribute FBP2
                            ]
           },
      'P_NPT_OPTI_AGERE':
           {
               'type':  'S',
               'fieldList':  [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('TARG_T0', 'N'),
                  DbLogColumn('TARG_T1', 'N'),
                  DbLogColumn('TARG_T2', 'N'),
                  DbLogColumn('TDTARGR', 'N'),
                  DbLogColumn('RAW_ERROR_RATE', 'N'),
                  DbLogColumn('FINAL_NPT_FLAG', 'N'),
                            ]
           },
      'P_BLUE_NUN_SCAN': #
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('LBA', 'N', 0), #
                  DbLogColumn('CMD_TIME', 'N', 0), #
                  DbLogColumn('MAX_CMD_TIME', 'N', 0), #
                            ]
           },
      'P_BLUE_NUN_SCORE': #
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('PASS', 'N', 0), #
                            ]
           },

      'P_GOTF_TABLE_SUMMARY':
            {
               'type':'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('DBLOG_TABLE', 'V'),
                  DbLogColumn('DBLOG_COLUMN', 'V'),
                  DbLogColumn('DBLOG_FILTER_COL', 'V'),
                  DbLogColumn('DBLOG_POSITION', 'N'),
                  DbLogColumn('BUSINESS_GROUP', 'V'),
                  DbLogColumn('PF_RESULT', 'V')
                    ]
            },
      'P_CUSTOMER_TEST':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('CUST_TEST_NAME', 'V', 0),
                  DbLogColumn('CUST_TEST_PASS', 'N', 0),
                            ]
            },
      'P107_DELTA_DEFECT_COUNT':
            {
                'type':'V',
                'fieldList':[
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('DELTA_DEFECT_COUNT', 'N')
                    ]
            },
      'CRITICAL_EVENT_LOG':
           {
               'type': 'V',
               'fieldList': [
                  DbLogColumn('EVENT_CTR', 'N'),
                  DbLogColumn('ERR_CODE', 'V'),
                  DbLogColumn('TIMESTAMP', 'N'),
                  DbLogColumn('LBA', 'N'),
                              ]
           },

      'P_TTR':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('TTR', 'N'),
                           ],
            },
      'P_THROUGHPUT_DATA':
            {
               'type':'S',
               'fieldList':[
                  DbLogColumn('SPC_ID',         'V',  0),
                  DbLogColumn('OCCURRENCE',     'N',  0),
                  DbLogColumn('SEQ',            'N',  0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N',  0),
                  DbLogColumn('RW_MODE',        'V',  0),   #PK Varchar(6) DEF: Read-write mode mneumonic... either "READ" or "WRITE"
                  DbLogColumn('DATA_ZONE',      'N',  0),   #PK 0-99       DEF:  Zone throughput was tested in
                  DbLogColumn('CYL_SKEW',       'N',  0),   #PK 0-999      DEF:  Cylinder Skew throughput was tested at
                  DbLogColumn('HD_SKEW',        'N',  0),   #PK 0-999      DEF:  Head Skew throughput was tested at
                  DbLogColumn('THROUGHPUT',     'N',  0),   #0-9999.9999   DEF: Throughput in kilobytes per second
                    ]
            },
      'P_LUL_DEFECT_DIFF_HD':
            {
               'type':'V',
               'fieldList':[
                  DbLogColumn('HD_PHYS_PSN',       'V',  0),
                  DbLogColumn('SPC_ID',            'V',  0),
                  DbLogColumn('OCCURRENCE',        'N',  0),
                  DbLogColumn('SEQ',               'N',  0),
                  DbLogColumn('TEST_SEQ_EVENT',    'N',  0),
                  DbLogColumn('DEFECT_COUNT',      'N',  0),
                  DbLogColumn('DEFECT_COUNT_DIFF', 'N',  0),
               ]
            },
      'P_LUL_DEFECT_DIFF_DRIVE':
            {
               'type':'S',
               'fieldList':[
                  DbLogColumn('SPC_ID',            'V',  0),
                  DbLogColumn('OCCURRENCE',        'N',  0),
                  DbLogColumn('SEQ',               'N',  0),
                  DbLogColumn('TEST_SEQ_EVENT',    'N',  0),
                  DbLogColumn('DEFECT_COUNT',      'N',  0),
                  DbLogColumn('DEFECT_COUNT_DIFF', 'N',  0),
               ]
            },

      'P069_EWAC_DATA':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('TRACK',          'N'),
                  DbLogColumn('EWAC',           'N'),
                  DbLogColumn('HD_LGC_PSN',     'N'),
                           ]
            },
      'P069_WPE_DATA':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('TRACK',          'N'),
                  DbLogColumn('WPEN',           'N'),
                  DbLogColumn('WPEP',           'N'),
                           ]
            },
      'P069_WPE_SUMMARY':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('HD_LGC_PSN',     'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('TRK_NUM',        'N'),
                  DbLogColumn('WPE_NEG',        'N'),
                  DbLogColumn('WPE_POS',        'N'),
                  DbLogColumn('WPE_UIN',        'N'),
                  DbLogColumn('WPE_NM',         'N'),
                           ]
            },
      'P069_EWAC_SUMMARY':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('HD_LGC_PSN',     'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('TRK_NUM',        'N'),
                  DbLogColumn('EWAC_UIN',        'N'),
                  DbLogColumn('EWAC_NM',         'N'),
                           ]
            }, 
      'P337_OVERWRITE':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('DATA_ZONE',      'N'),                  
                  DbLogColumn('HD_LGC_PSN',     'N'),
                  DbLogColumn('TRK_NUM',        'N'),
                  DbLogColumn('OVERWRITE',      'N'),
                  DbLogColumn('HD_STATUS',      'N'),
                           ]
            },                       
      'P109_WEDGE_FLAW_01':
            {
               'type':'V',
               'fieldList':[
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('TRK_NUM', 'N'),
                  DbLogColumn('WEDGE', 'N'),
                    ]
            },
      'P109_WEDGE_FLAW_02':
            {
               'type':'V',
               'fieldList':[
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('TRK_NUM', 'N'),
                  DbLogColumn('WEDGE', 'N'),
                    ]
            },
      'P109_NEW_WEDGE_FLAW':
            {
               'type':'V',
               'fieldList':[
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('TRK_NUM', 'N'),
                  DbLogColumn('WEDGE', 'N'),
                    ]
            },
      'P109_VANISH_WEDGE_FLAW':
            {
               'type':'V',
               'fieldList':[
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('TRK_NUM', 'N'),
                  DbLogColumn('WEDGE', 'N'),
                    ]
            },
      'P109_WEDGE_FLAW_COUNT':
            {
               'type':'V',
               'fieldList':[
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('FLAW_CNT_01', 'N'),
                  DbLogColumn('FLAW_CNT_02', 'N'),
                  DbLogColumn('NEW_FLAW_CNT', 'N'),
                  DbLogColumn('VANISH_FLAW_CNT', 'N'),
                    ]
            },
      'P_SCREEN_DEFECTS':
            {
               'type':'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('SCREEN_NAME','V'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('PHYS_TRK_NUM', 'N'),
                  DbLogColumn('LGC_TRK_NUM', 'N'),
                  DbLogColumn('PHYS_SECTOR', 'N'),
                  DbLogColumn('LGC_SECTOR', 'N'),
                  DbLogColumn('LBA', 'N'),
                  DbLogColumn('RW_SENSE_CODE', 'V'),
                  DbLogColumn('DIAGNOSTIC_ERR_CODE', 'V'),
                    ]
            },
      'P055_CONTACT_SUMMARY2':
            {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('DATA_ZONE','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('HTR_DAC','N'),
                  DbLogColumn('RD_HTR_DAC','N'),
                           ]
            },
      'P172_VBAR':
            {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('TRK_NUM', 'N'),
                  DbLogColumn('VBAR_BPI', 'N'),
                  DbLogColumn('VBAR_TPI', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  ]
           },
      'P_HIRP_CAL_POLY_FIT':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('ORIG_BACKOFF_DAC', 'N'),
                  DbLogColumn('FITTED_BACKOFF_DAC', 'N'),
                  DbLogColumn('SIGMA_POLY_FIT', 'N'),
                  DbLogColumn('POLYNOMIAL_DEGREE', 'N'),
                  ]
           },
      'P210_VBAR_THRSHLD2':
           {
               'type': 'V',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('TPI_VBAR_SERT', 'N'),
                  DbLogColumn('BPI_VBAR_SERT', 'N'),
                  ]
           },
      'P_234_BER_CHUNK_DELTA':
           {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('HEAD', 'N', 0),
                  DbLogColumn('ZONE', 'N', 0),
                  DbLogColumn('DEGAUSS', 'N', 0),
                  DbLogColumn('BASELINE_BER_CHUNK1', 'N', 0),
                  DbLogColumn('DELTA_BER_CHUNK1', 'N', 0),
                  DbLogColumn('BASELINE_BER_CHUNK2', 'N', 0),
                  DbLogColumn('DELTA_BER_CHUNK2', 'N', 0),
                  DbLogColumn('BASELINE_BER_CHUNK3', 'N', 0),
                  DbLogColumn('DELTA_BER_CHUNK3', 'N', 0),
                                       ]
           },
      'P_DOS_VERIFY':
           {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('NUM_GLIST_DEFECTS', 'N'),     # Numeric 9999.0; The number of G list entries added during the DOS verification screen
                  DbLogColumn('NUM_PENDING_LIST_DEFECTS', 'N'),     # Numeric 9999.0; The number of P list entries added during the DOS verification screen
                  DbLogColumn('NUM_DOS_CRITICAL_EVENTS', 'N'),   # Numeric 9999.0; The number of DOS critical Event Log entries added during the DOS verification screen
                  ]
               },
           
      'P_SUSTAINED_TRANSFER_RATE':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('START_LBA', 'V'),
                  DbLogColumn('TOTAL_TEST_LBAS', 'N'),
                  DbLogColumn('WRITE_XFER_RATE', 'N'),
                  DbLogColumn('READ_XFER_RATE', 'N'),
                  ]
            },           

      'P000_DEPOP_HEADS':
           {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  ]
               },

      'P598_ZONE_XFER_RATE':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('DATA_ZONE', 'N'),      # SEQUENTIAL GROUPING OF DATA TRACKS ON THE DISC COUNTING FROM 0 BEGINNING AT THE OD2
                  DbLogColumn('SPC_ID', 'V'),         # USER DEFINED DATA IDENTIFIER
                  DbLogColumn('OCCURRENCE', 'N'),     # COUNTER FOR ALL TESTS WITHIN A SEQUENCE
                  DbLogColumn('SEQ', 'N'),            # USER DEFINED NUMBER THAT IS ASSIGNED TO A GROUP OF TESTS
                  DbLogColumn('TEST_SEQ_EVENT', 'N'), # COUNTER FOR A SPECIFIC TEST WITHIN A SEQUENCE
                  DbLogColumn('TIME', 'N'),           # TIME IT TOOK TO TRANSFER THE REQUIRED BLOCKS FOR THIS ZONE
                  DbLogColumn('DATA_RATE', 'N'),      # THE DATA RATE USING THE ACTUAL TIME TAKEN TO TRANSFER THE REQUIRED BLOCKS
                  DbLogColumn('LBAS_XFERED', 'N'),    # NUMBER OF LOGICAL BLOCKS TRANSFERED IN THIS ZONE
                  DbLogColumn('CALC_RATE', 'N'),      # THE CALCULATED DATA RATE USING IDEAL VALUES FOR TIME 
                  DbLogColumn('RATIO', 'N'),          # THE RATIO OF DATA_RATE OVER CALC_RATE
                  DbLogColumn('STATUS', 'N'),
                  DbLogColumn('START_LBA', 'N'),      # START_LBA (not in FIS)
                  DbLogColumn('END_LBA', 'N'),        # END_LBA (not in FIS)
                  DbLogColumn('MAX_TIME_PER_XFER', 'N'),
                  DbLogColumn('LBA_AT_MAX_TIME', 'N'),
                  DbLogColumn('MIN_TIME_PER_XFER', 'N'),
                  DbLogColumn('LBA_AT_MIN_TIME', 'N'),
                  DbLogColumn('PARAMETER_1', 'N'),    # THE FIRST INPUT PARAMETER TO THE TEST WHEN CALLED USING THE TEN PARAMETER FORMAT.
                              ]
           },
      'P051_MILLIONW_PREDICTIN_EXT':
           {
               'type': 'M',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('ABS_TRACK_INDEX', 'N'),
                  DbLogColumn('RRAW_BER10K', 'N'),
                  DbLogColumn('RRAW_BER', 'N'),
                  DbLogColumn('CAL_RRAW', 'N'),
                  ]
               },

      'P186_BIAS_CAL2_MRE_DIFF':
           {
               'type': 'M',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('MRE_DIFF_VAL', 'N'),
                  ]
               },
      'P_VBAR_HMS_ADJUST':
           {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID',         'V'),
                  DbLogColumn('OCCURRENCE',     'N'),
                  DbLogColumn('SEQ',            'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN',    'N'),
                  DbLogColumn('HD_LGC_PSN',     'N'),
                  DbLogColumn('DATA_ZONE',      'N'),
                  DbLogColumn('ITERATION',      'N'),
                  DbLogColumn('HMS_CAP',        'N'),
                  DbLogColumn('HMS_MRGN',       'N'),
                  DbLogColumn('BPI_ADJ',        'N'),
                  DbLogColumn('CUM_BPI_ADJ',    'N'),
                  DbLogColumn('BPI_CAP',        'N'),
                  DbLogColumn('BPI_PICK',       'N'),
                  DbLogColumn('TPI_PICK',       'N'),
                  DbLogColumn('ACTIVE_ZONE',    'N'),
                  DbLogColumn('OUT_OF_SPEC',    'V'),
                  DbLogColumn('TPI_CAP',        'N'),
                  DbLogColumn('TGT_WRT_CLR',    'N'),
                  DbLogColumn('CAP_PENALTY',    'N'),
                  ]
               },
      'P_SMR_FORMAT_SUMMARY':
           {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID',            'V'),
                  DbLogColumn('OCCURRENCE',        'N'),
                  DbLogColumn('SEQ',               'N'),
                  DbLogColumn('TEST_SEQ_EVENT',    'N'),
                  DbLogColumn('HD_PHYS_PSN',       'N'),
                  DbLogColumn('DATA_ZONE',         'N'),
                  DbLogColumn('HD_LGC_PSN',        'N'),
                  DbLogColumn('TPIC_S',            'N'),
                  DbLogColumn('TP_S',              'N'),
                  DbLogColumn('TPIC_D',            'N'),
                  DbLogColumn('TP_D',              'N'),
                  DbLogColumn('PICK',              'N'),
                  DbLogColumn('EFF_TPIC',          'N'),
                  DbLogColumn('BANDSIZE_RATIO',    'N'),
                  DbLogColumn('BANDSIZE_PICK',     'N'),
                  DbLogColumn('SHINGLE_TRK_PITCH', 'N'),
                  DbLogColumn('GUARD_TRK_PITCH',   'N'),
                  DbLogColumn('SHINGLE_DIR',       'N'),
                  DbLogColumn('UJOG_SQUEEZE',      'N'),
                  DbLogColumn('BANDSIZE_PHY',      'N'),
                  DbLogColumn('TRK_PITCH',         'N'),
                  DbLogColumn('TRK_GUARD',         'N'),
                  DbLogColumn('NUM_LGC_TRKS',      'N'),
                  DbLogColumn('NOM_TRKS_ALLOC',    'N'),
                  DbLogColumn('NOM_TRKS_USED',     'N'),
                  DbLogColumn('NUM_OF_BANDS',      'N'),
                  ]
               },
      'P211_TPI_MARGIN_HISTOGRAM':
           {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('TPI_MRGN', 'N'),
                  DbLogColumn('BIN_COUNT', 'N'),
                  ]
               },

      'P_VBAR_INITIAL_PICKS':
           {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE','N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('BPI_CAP', 'N'),
                  DbLogColumn('BPI_TABLE_NUM', 'N'),
                  DbLogColumn('BPI_PICK', 'N'),
                  DbLogColumn('BPI_MRGN', 'N'),
                  DbLogColumn('TPI_CAP', 'N'),
                  DbLogColumn('TPI_TABLE_NUM', 'N'),
                  DbLogColumn('TPI_PICK', 'N'),
                  DbLogColumn('TPI_MRGN', 'N'),
                  ]
               },

      'P_VBAR_PICKER_FMT_ADJUST':
           {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE','N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('COMPUTED_CAP_GB', 'N'),      # Starting capacity before adjustment
                  DbLogColumn('AVE_DENSITY', 'N'),          # Starting average density before adjustment, (relative to nominal)
                  DbLogColumn('HD_PHYS_PSN', 'N'),          # Physical head selected for adjustment
                  DbLogColumn('HD_LGC_PSN', 'N'),           # Logical head selected for adjustment
                  DbLogColumn('DATA_ZONE', 'N'),            # Data zone selected for adjustment
                  DbLogColumn('OP_MODE', 'N'),              # Adjustment purpose: 'C' for Capacity, 'P' for Performance
                  DbLogColumn('CAP_ADJUST', 'N'),           # Increase or decrease capacity
                  DbLogColumn('FMT_TYPE', 'N'),             # BPI or TPI being adjusted
                  DbLogColumn('RELATIVE_PICK', 'N'),        # BPI Pick or TPI Pick, format relative to nominal
                  DbLogColumn('SELECTED_FORMAT', 'N'),      # Selected format number, BPI or TPI, from the format table
                  DbLogColumn('BPI_AVE', 'N'),              # Performance based the average of BPI picks across all heads and zones
                  ]
               },
      'P_OAR_SUMMARY':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('TRK_NUM', 'N', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('REGION', 'N', 0),
                  DbLogColumn('AVG_BITERR', 'N', 0),
                  DbLogColumn('NUM_SAMPLE', 'N', 0),
                   ]
               },
      'P_OAR_SCREEN_SUMMARY':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('TRK_NUM', 'N', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('MAX_BIT_IN_ERROR', 'N', 0),
                  DbLogColumn('MIN_BIT_IN_ERROR', 'N', 0),
                  DbLogColumn('DELTA', 'N', 0),
                  DbLogColumn('RESULT', 'V', 0),
                   ]
               },
      'P_AGB_STARTTRACK':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('START_TRACK', 'N', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                   ]
               },
      'P_VBAR_PICKER_RESULTS':
           {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE','N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('TARGET_CAPACITY', 'N'),
                  DbLogColumn('FINAL_DENSITY', 'N'),
                  DbLogColumn('TARGET_CAP_GB', 'N'),
                  DbLogColumn('COMPUTED_CAP_GB', 'N'),
                  DbLogColumn('MIN_BPI_AVE_LIMIT', 'N'),
                  DbLogColumn('BPI_AVE', 'N'),
                  DbLogColumn('MAX_BPI_AVE_LIMIT', 'N'),
                  ]
               },
      'P_SETTLING_SUMMARY':
           {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('WRT_CLRNC', 'N'),
                  DbLogColumn('DWELL_TIME', 'N'),
                  DbLogColumn('HARD_ERR_RATE_SETTLE', 'N'),
                  DbLogColumn('RAW_ERR_RATE_SETTLE', 'N'),
                  DbLogColumn('HARD_ERR_RATE_TIME_0', 'N'),
                  DbLogColumn('RAW_ERR_RATE_TIME_0', 'N'),
                  DbLogColumn('RAP_TARGET_WRT_CLRNC', 'N'),
                  DbLogColumn('HD_CLRNC_SETTLE', 'N'),
                  DbLogColumn('SETTLE_SLOPE', 'N'),
                  DbLogColumn('SETTLE_INTERCEPT', 'N'),
                  DbLogColumn('SETTLE_R_SQUARED', 'N'),
                  DbLogColumn('BPI_CAP_VBAR', 'N'),
                  DbLogColumn('TPI_CAP_VBAR', 'N'),
                  DbLogColumn('HMS_CAP_VBAR', 'N'),
                  DbLogColumn('HMS_MRGN_VBAR', 'N'),
                  DbLogColumn('TEMP_VBAR', 'N'),
                  DbLogColumn('HMS_CAP_1', 'N'),
                  DbLogColumn('HMS_MRGN_1', 'N'),
                  DbLogColumn('TEMP_CUR_1', 'N'),
                  DbLogColumn('DELTA_HMS_CAP_1', 'N'),
                  DbLogColumn('DELTA_TEMP_1', 'N'),
                  DbLogColumn('HMS_CAP_INIT', 'N'),
                  ]
               },
      'P195_VGA_CSM':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('TRK_NUM', 'N', 0),
                  DbLogColumn('HD_LGC_PSN', 'N', 0),
                  DbLogColumn('ITER', 'N', 0),
                  DbLogColumn('VGA', 'N', 0),
                  DbLogColumn('CSM', 'N', 0),
                  DbLogColumn('ERROR_CODE', 'N', 0),
                  ]
              },
      'P195_VGA_CSM_STDEV':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('TRK_NUM', 'N', 0),
                  DbLogColumn('HD_LGC_PSN', 'N', 0),
                  DbLogColumn('CSM_STDEV', 'N', 0),
                  DbLogColumn('CSM_AVG', 'N', 0),
                  DbLogColumn('CSM_NORM_STDEV', 'N', 0),
                  ]
              },
      'P_TCS_SUMMARY':
           {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('HMS_HOT', 'N'),
                  DbLogColumn('TEMP_HOT', 'N'),
                  DbLogColumn('HMS_COLD', 'N'),
                  DbLogColumn('TEMP_COLD', 'N'),
                  DbLogColumn('TCS', 'N'),
                  DbLogColumn('ADD_TCS_COLD_DTC', 'N'),
                  DbLogColumn('ADD_TCS_HOT_DTH', 'N'),
                  DbLogColumn('HMS_CAP_COLD', 'N'),
                  DbLogColumn('HMS_CAP_HOT', 'N'),
                  ]
               },
      'P_TCS_ZN_SUMMARY':
           {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HMS_HOT', 'N'),
                  DbLogColumn('TEMP_HOT', 'N'),
                  DbLogColumn('HMS_COLD', 'N'),
                  DbLogColumn('TEMP_COLD', 'N'),
                  DbLogColumn('TCS', 'N'),
                  DbLogColumn('HMS_CAP_COLD', 'N'),
                  DbLogColumn('HMS_CAP_HOT', 'N'),
                  ]
               },

      'P_TA_DWELL_SUMRY_HD':
           {
               'type':'M',
               'fieldList':[
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('DWELL_GRPNG_ID','N'),
                  DbLogColumn('SPC_ID','V'),
                  DbLogColumn('OCCURRENCE','N'),
                  DbLogColumn('SEQ','N'),
                  DbLogColumn('TEST_SEQ_EVENT','N'),
                  DbLogColumn('DWELL_GRPNG_AMP_MAX','N'),
                  DbLogColumn('DWELL_GRPNG_AMP_MIN','N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('TA_DWELL_CNT','N'),
                  DbLogColumn('DWELL_TIME','N'),
                  DbLogColumn('SURF_PASS_FAIL_ELIGIBLE','N'),
                  DbLogColumn('RES_HD_STATUS','N'),
                  DbLogColumn('RES_START','N'),
                  DbLogColumn('RES_END','N'),
                  DbLogColumn('RES_DELTA','N'),
                  DbLogColumn('BER_HD_STATUS','N'),
                  DbLogColumn('BER_START','N'),
                  DbLogColumn('BER_END','N'),
                  DbLogColumn('BER_DELTA','N'),
                  DbLogColumn('HD_STATUS','N'),
                        ]
               },
      'P210_VBAR_FORMATS':
           {
               'type':'S',
               'fieldList':[
                  DbLogColumn('SPC_ID','V'),
                  DbLogColumn('OCCURRENCE','N'),
                  DbLogColumn('SEQ','N'),
                  DbLogColumn('TEST_SEQ_EVENT','N'),
                  DbLogColumn('HD_LGC_PSN','N'),
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('DATA_ZONE','N'),
                  DbLogColumn('BPI_FMT','N'),
                  DbLogColumn('TPI_FMT','N'),
                   ]
               },

      'P_FORMAT_ZONE_ERROR_RATE_EXT':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('BITSRDLOG10_MINUS_HARDERRRATE', 'N'),

               ]
            },
      'P_ASD_PERFORMANCE_SCRN':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('TEST_MODE', 'V'),
                  DbLogColumn('TEST_TIME', 'N'),

               ]
            },

      'P_AFH_MEASURED_TCC':
            {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('DATA_ZONE','N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),

                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN','N'),

                  DbLogColumn('ACTUATION_MODE','V'),

                  DbLogColumn('WRT_CLR_1','N'),
                  DbLogColumn('TEMP_1','N'),

                  DbLogColumn('WRT_CLR_2','N'),
                  DbLogColumn('TEMP_2','N'),

                  DbLogColumn('UNMODIFIED_SLOPE_MSRMNT','N'),
                  DbLogColumn('UNMODIFIED_THERMAL_CLR_COEF_1','N'),

                  DbLogColumn('MODIFIED_SLOPE_LSL','N'),
                  DbLogColumn('MODIFIED_SLOPE_USL','N'),

                  DbLogColumn('MODIFIED_THERMAL_CLR_COEF_1','N'),
                  DbLogColumn('THERMAL_CLR_COEF_2','N'),
                  ]
            },
      # PK = usual + HD_PHYS_PSN, DATA_ZONE, RETRY_NUM, ACTUATION_MODE
      'P_AFH_DH_CONSISTENCY_CHK':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),

                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('DATA_ZONE','N'),

                  DbLogColumn('RETRY_NUM','N'),
                  DbLogColumn('HD_LGC_PSN','N'),

                  DbLogColumn('CLR_ACTUATION_MODE','V'),

                  DbLogColumn('TRIMMED_MEAN','N'),
                  DbLogColumn('TRIMMED_MEAN_LSL','N'),
                  DbLogColumn('TRIMMED_MEAN_USL','N'),

                  DbLogColumn('WINSORIZED_STD_DEV','N'),
                  DbLogColumn('WINSORIZED_STD_DEV_LSL','N'),
                  DbLogColumn('WINSORIZED_STD_DEV_USL','N'),

                  DbLogColumn('POINTS_IN_ERR_CNT','N'),
                  DbLogColumn('POINTS_IN_ERR_ALLOWED','N'),
                  DbLogColumn('MAX_CLR_DELTA','N'),
                  DbLogColumn('CHK_FAIL_CRITERIA','V'),
                  ]
            },

      'P_AFH_DH_MEASURED_TCC':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),

                  DbLogColumn('HD_PHYS_PSN','N'),
                  DbLogColumn('ACTIVE_HEATER','V'),

                  DbLogColumn('DATA_ZONE','N'),

                  DbLogColumn('HD_LGC_PSN','N'),

                  DbLogColumn('CLR_ACTUATION_MODE','V'),

                  DbLogColumn('WRT_CLR_1','N'),
                  DbLogColumn('TEMP_1','N'),

                  DbLogColumn('WRT_CLR_2','N'),
                  DbLogColumn('TEMP_2','N'),

                  DbLogColumn('RAW_SLOPE_MSRMNT','N'),
                  DbLogColumn('RAW_TCC_1','N'),

                  DbLogColumn('MOD_SLOPE_LSL','N'),
                  DbLogColumn('MOD_SLOPE_USL','N'),

                  DbLogColumn('MOD_TCC_1','N'),
                  DbLogColumn('RAW_TCC_2','N'),
                  ]
            },

      'P597_ADV_TAG_Q':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('TEST_MODE', 'N'),
                  DbLogColumn('RCVBL_RD_ERR', 'N'),
                  DbLogColumn('RCVBL_WRT_ERR', 'N'),
                  DbLogColumn('RCVBL_SRVO_ERR', 'N'),
                  DbLogColumn('UNRCVBL_ERR', 'N'),
                  DbLogColumn('WRT_XTND_CMD', 'N'),
                  DbLogColumn('RD_XTND_CMD', 'N'),
                  DbLogColumn('WRT_VFY_CMD', 'N'),
                  DbLogColumn('SEEK_XTND_CMD', 'N'),
                  DbLogColumn('NUM_OTHER_CMD', 'N'),
                  DbLogColumn('IOPS', 'N'),
               ]
            },
      'P597_SPEC_LIMIT':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('WCE_SPEC', 'N'),
                  DbLogColumn('WCE', 'N'),
                  DbLogColumn('WCD_SPEC', 'N'),
                  DbLogColumn('WCD', 'N'),
                  DbLogColumn('READ_SPEC', 'N'),
                  DbLogColumn('READ', 'N'),
                  DbLogColumn('NUM_FAIL_COLS', 'N'),
               ]
            },
      'P598_ZONE_DATA_RATE':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('DATA_RATE_SPEC', 'N'),
                  DbLogColumn('DATA_RATE', 'N'),
                  DbLogColumn('WRITE_READ', 'V'),
                  DbLogColumn('PASS_FAIL', 'V'),
                  DbLogColumn('TOTAL_ZONES_FAIL', 'N'),
                  ]
            },

      'P_COLD_WRITE_DELTA':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('HEAD', 'N', 0),
                  DbLogColumn('BITS_READ', 'N', 0),
                  DbLogColumn('HARD_ERROR_RATE', 'N', 0),
                  DbLogColumn('HARD_ERROR_DELTA', 'N', 0),
                  DbLogColumn('SOFT_ERROR_RATE', 'N', 0),
                  DbLogColumn('SOFT_ERROR_DELTA', 'N', 0),
                  DbLogColumn('OTF_ERROR_RATE', 'N', 0),
                  DbLogColumn('OTF_ERROR_DELTA', 'N', 0),
                  DbLogColumn('RAW_ERROR_RATE', 'N', 0),
                  DbLogColumn('RAW_ERROR_DELTA', 'N', 0),
                  ]
             },
      'P051_ERASURE_BER_DELTAS':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('TRK_INDEX', 'N'),
                  DbLogColumn('TRK_NUM', 'N'),
                  DbLogColumn('NUM_WRT_BASELINE', 'N'),
                  DbLogColumn('NUM_WRT_ERASURE', 'N'),
                  DbLogColumn('SCTR_READ_CNT_BASELINE', 'N'),
                  DbLogColumn('SCTR_READ_CNT_ERASURE', 'N'),
                  DbLogColumn('BITS_IN_ERROR_BASELINE', 'N'),
                  DbLogColumn('BITS_IN_ERROR_ERASURE', 'N'),
                  DbLogColumn('BITS_IN_ERROR_DELTA', 'N'),
                  DbLogColumn('BITS_IN_ERROR_RATIO', 'N'),
                  DbLogColumn('BITS_IN_ERROR_BER_BASELINE', 'N'),
                  DbLogColumn('BITS_IN_ERROR_BER_ERASURE', 'N'),
                  DbLogColumn('BITS_IN_ERROR_BER_DELTA', 'N'),
                  DbLogColumn('OTF_BER_BASELINE', 'N'),
                  DbLogColumn('OTF_BER_ERASURE', 'N'),
                  DbLogColumn('OTF_BER_DELTA', 'N'),
            ]
         },

      'P051_ERASURE_BER':
            {
               'type': 'M',
               'fieldList':[
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('TEST_TYPE', 'V'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('TRK_NUM', 'N'),
                  DbLogColumn('HARD_ERR_CNT', 'N'),
                  DbLogColumn('ONE_PLUS_RTY_CNT', 'N'),
                  DbLogColumn('SIX_PLUS_RTY_CNT', 'N'),
                  DbLogColumn('ONE_PLUS_ECC_CNT', 'N'),
                  DbLogColumn('SCTR_READ_CNT', 'N'),
                  DbLogColumn('T_LEVEL', 'N'),
                  DbLogColumn('TRK_INDEX', 'N'),
                  DbLogColumn('NUM_WRT', 'N'),
                  DbLogColumn('HARD_BER', 'N'),
                  DbLogColumn('OTF_BER', 'N'),
                  DbLogColumn('SOFT_BER', 'N'),
                  DbLogColumn('RRAW_BER', 'N'),
                  DbLogColumn('BITS_IN_ERROR', 'N'),
                  DbLogColumn('BITS_IN_ERROR_BER', 'N'),
               ]
            },

      'P_FMT_T250_RAW_ERROR_RATE_DELTA':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('T250_RAW_ERROR_RATE', 'N'),
                  DbLogColumn('FMT_RAW_ERROR_RATE', 'N'),
                  DbLogColumn('RAW_ERROR_RATE_DELTA', 'N'),
                        ]
            },

      'P_VBAR_SMR_MEASUREMENT':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('BPI_CAP', 'N'),
                  DbLogColumn('SQZ_TYPE', 'N'),
                  DbLogColumn('MSRD_BPI', 'N'),
                  DbLogColumn('SQZ_CAP', 'V'),
                        ]
            },
      'P_USER_SLIP_LIST':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('SLIP_LIST_ENTRIES', 'N'),
                  DbLogColumn('TOTAL_SPARE_SECTORS', 'N'),
                           ]
            },
      'P_180_NRRO_RRO_SUMMARY':
            {
               'type'      : 'S',
               'fieldList' : [
                  DbLogColumn('SPC_ID',            'V', 0),
                  DbLogColumn('OCCURRENCE',        'N', 0),
                  DbLogColumn('SEQ',               'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT',    'N', 0),
                  DbLogColumn('HD_LGC_PSN',        'N', 0),
                  DbLogColumn('FREQ_RANGE_NUM',    'N', 0),
                  DbLogColumn('MAX_NRRO_FFT_AMP',  'N', 0),
                  DbLogColumn('MAX_RRO_FFT_AMP',   'N', 0),
                  ]
             },
      'P_RD_WRT_DAC_DELTA':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('HEAD', 'N', 0),
                  DbLogColumn('ZONE', 'N', 0),
                  DbLogColumn('CNTCT_DAC_DELTA', 'N', 0),
                  DbLogColumn('CLR_DELTA', 'N', 0),
                  DbLogColumn('MSRD_INTRPLTD', 'N', 0),
                  DbLogColumn('CONTACT_TEMP', 'N', 0),
                           ]
            },
      'P_DELTA_OTF_TABLE':
            {
               'type': 'S',
               'fieldList':[
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DELTA_OTF', 'N'),
                           ]
            },
      'P_TEMPERATURES':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('STATE_NAME', 'V', 0),
                  DbLogColumn('DRIVE_TEMP', 'N', 0),
                  DbLogColumn('CELL_TEMP', 'N', 0),
                  DbLogColumn('REQ_TEMP', 'N', 0),
                  DbLogColumn('INPUT_TEMP', 'N', 0),
                  DbLogColumn('OUTPUT_TEMP', 'N', 0),
                  DbLogColumn('ELEC_TEMP', 'N', 0),
                  DbLogColumn('DRIVE_FAN_RPM', 'N', 0),
                  DbLogColumn('ELEC_FAN_RPM', 'N', 0),
                  ]
            },
      'P_FASTSOC':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('SOC_TYPE', 'N', 0),
                  ]
            },
      'P_PREHEAT_OPTI':
           {
              'type': 'M',
              'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('DATA_ZONE', 'N', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('PRE_HEAT_TRGT_CLRNC_ORG', 'N', 0),
                  DbLogColumn('PRE_HEAT_TRGT_CLRNC_NEW', 'N', 0),
                  DbLogColumn('DELTA_PRE_HEAT_TRGT_CLRNC', 'N', 0),
                   ]
           },
           
      'P190_HSC_DATA':
           {
              'type': 'M',
              'fieldList': [
                  DbLogColumn('HD_PHYS_PSN',    'N', 0),
                  DbLogColumn('DATA_ZONE',      'N', 0),
                  DbLogColumn('HD_LGC_PSN',     'N', 0),
                  DbLogColumn('TRK_NUM',        'N', 0),
                  DbLogColumn('HSC_2T',         'N', 0),
                  DbLogColumn('READ_INDEX',     'N', 0),
                  DbLogColumn('INDEX1',         'N', 0),
                  DbLogColumn('INDEX2',         'N', 0),
                  DbLogColumn('DATA1',          'N', 0),
                  DbLogColumn('DATA2',          'N', 0),
                  DbLogColumn('MODE',           'N', 0),
                  DbLogColumn('WRT_CUR',        'N', 0),
                  DbLogColumn('OVS_WRT_CUR',    'N', 0),
                  DbLogColumn('OVS_DUR',        'N', 0),
                  DbLogColumn('WRITE_HEAT',     'N', 0),
                  DbLogColumn('READ_HEAT',      'N', 0),
                   ]
           },
        
      'P_DELTA_MRE':
           {
               'type': 'V',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),                  
                  DbLogColumn('DELTA_MRE', 'N'),                  
                                       ]
           },
      'P_HSC_OD_ID':
           {
              'type': 'V',
              'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('HSC_OD', 'N', 0),
                  DbLogColumn('HSC_ID', 'N', 0),
                   ]
           },
      'P_TEMP_WEAK_WRITE_BER':
           {
               'type': 'V',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('TRK_NUM', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('COLD_BER10', 'N'),
                  DbLogColumn('HOT_BER10', 'N'),
                  DbLogColumn('DELTA_BER10', 'N'),
                  DbLogColumn('USL_DELTA_BER10', 'N'),
                  DbLogColumn('LSL_COLD_BER10', 'N'),
                  DbLogColumn('HD_STATUS', 'N'),
                                       ]
           },
      'P_TEMP_APO_BER':
           {
               'type': 'V',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('TRK_NUM', 'N'),
                  DbLogColumn('SECTOR', 'N'),
                  DbLogColumn('LONG_BER', 'N'),
                  DbLogColumn('SHORT_BER', 'N'),
                  DbLogColumn('SECTOR_DBER', 'N'),
                  DbLogColumn('FIRST_SECTOR_DBER', 'N'),
                  DbLogColumn('STABLE_SECTOR_DBER', 'N'),
                  DbLogColumn('WORST_LONG_DBER', 'N'),
                  DbLogColumn('WORST_SHORT_DBER', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                                       ]
           },
        'P_ERROR_RATE_STATUS':
           {
              'type': 'M',
              'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('HD_STATUS', 'V', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                   ]
           },
        'P_DFLAWSCAN_STATUS':
           {
              'type': 'M',
              'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('HD_STATUS', 'V', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
             ]
           },
        'P195_SUMMARY':
          {
              'type': 'V',
              'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('HD_STATUS', 'V', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
             ]
           },
        'P072_SUMMARY':
          {
              'type': 'V',
              'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('HD_STATUS', 'V', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
             ]
           },      
      'P_ENC_CHALLENGE_LOG':
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('ROW_NUM',              'N'),
                  DbLogColumn('CHALLENGE_TYPE',       'V'),
                  DbLogColumn('CHALLENGE_RANDOM_DATA','V'),
                  DbLogColumn('CHALLENGE_BITS',       'V'),     
                  ]
           },
      'P251_FITNESS_R_SQUARED':
           {
              'type': 'M',
              'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('DATA_ZONE', 'N', 0),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('RGSTR_ID', 'N', 0),
                  DbLogColumn('R_SQUARED', 'N', 0),
                  DbLogColumn('FIT_SLOPE', 'N', 0),
                   ]
           },
      'P_PRECODER_SUMMARY':
          {
             'type': 'M',
             'fieldList': [
                 DbLogColumn('HD_PHYS_PSN', 'N', 0),
                 DbLogColumn('DATA_ZONE', 'N', 0),
                 DbLogColumn('SPC_ID', 'V', 0),
                 DbLogColumn('OCCURRENCE', 'N', 0),
                 DbLogColumn('SEQ', 'N', 0),
                 DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                 DbLogColumn('COMBI', 'N'),
                 DbLogColumn('RAW_ERROR_RATE', 'N'),
                 DbLogColumn('PCodeMap0', 'N'),
                 DbLogColumn('PCodeMap1', 'N'),
                 DbLogColumn('IDX0_3', 'N'),
                 DbLogColumn('IDX4_7', 'N'),
                 ]
          },
      'P_SP_AEGIS_SUMMARY':
         {
            'type'      : 'M',
            'fieldList' : [
               DbLogColumn('SPC_ID', 'V'),
               DbLogColumn('ITEM', 'N'),
               DbLogColumn('DATA', 'N'),
               DbLogColumn('STATUS', 'N'),
            ]
         },
         
      'P_PBIC_KPIV_PRE2':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('KPIV1', 'N'),
                  DbLogColumn('KPIV2', 'N'),
                  DbLogColumn('KPIV3', 'N'),
                  DbLogColumn('KPIV4', 'N'),
                  DbLogColumn('KPIV5', 'N'),
                  DbLogColumn('KPIV6', 'N'),
                  DbLogColumn('KPIV7', 'N'),
                  DbLogColumn('KPIV8', 'N'),
                  DbLogColumn('KPIV9', 'N'),
                  DbLogColumn('KPIV10', 'N'),
                  DbLogColumn('KPIV11', 'N'),
                  DbLogColumn('KPIV12', 'N'),
                  DbLogColumn('KPIV13', 'N'),
                  DbLogColumn('KPIV14', 'N'),
                  DbLogColumn('KPIV15', 'N'),
                  DbLogColumn('KPIV16', 'N'),
                  DbLogColumn('KPIV17', 'N'),
                  DbLogColumn('KPIV18', 'N'),
                  DbLogColumn('KPIV19', 'N'),
                  DbLogColumn('KPIV20', 'N'),
                  DbLogColumn('KPIV21', 'N'),
                  DbLogColumn('KPIV22', 'N'),
                  DbLogColumn('KPIV23', 'N'),
                  DbLogColumn('KPIV24', 'N'),
                  DbLogColumn('KPIV25', 'N'),
                  DbLogColumn('KPIV26', 'N'),
                  DbLogColumn('KPIV27', 'N'),
                  DbLogColumn('KPIV28', 'N'),
                  DbLogColumn('KPIV29', 'N'),
                  DbLogColumn('KPIV30', 'N'),
                           ]
            },
      'P_PBIC_KPIV_CAL2':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('KPIV1', 'N'),
                  DbLogColumn('KPIV2', 'N'),
                  DbLogColumn('KPIV3', 'N'),
                  DbLogColumn('KPIV4', 'N'),
                  DbLogColumn('KPIV5', 'N'),
                  DbLogColumn('KPIV6', 'N'),
                  DbLogColumn('KPIV7', 'N'),
                  DbLogColumn('KPIV8', 'N'),
                  DbLogColumn('KPIV9', 'N'),
                  DbLogColumn('KPIV10', 'N'),
                  DbLogColumn('KPIV11', 'N'),
                  DbLogColumn('KPIV12', 'N'),
                  DbLogColumn('KPIV13', 'N'),
                  DbLogColumn('KPIV14', 'N'),
                  DbLogColumn('KPIV15', 'N'),
                  DbLogColumn('KPIV16', 'N'),
                  DbLogColumn('KPIV17', 'N'),
                  DbLogColumn('KPIV18', 'N'),
                  DbLogColumn('KPIV19', 'N'),
                  DbLogColumn('KPIV20', 'N'),
                  DbLogColumn('KPIV21', 'N'),
                  DbLogColumn('KPIV22', 'N'),
                  DbLogColumn('KPIV23', 'N'),
                  DbLogColumn('KPIV24', 'N'),
                  DbLogColumn('KPIV25', 'N'),
                  DbLogColumn('KPIV26', 'N'),
                  DbLogColumn('KPIV27', 'N'),
                  DbLogColumn('KPIV28', 'N'),
                  DbLogColumn('KPIV29', 'N'),
                  DbLogColumn('KPIV30', 'N'),
                           ]
            },
      'P_PBIC_KPIV_FNC2':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('KPIV1', 'N'),
                  DbLogColumn('KPIV2', 'N'),
                  DbLogColumn('KPIV3', 'N'),
                  DbLogColumn('KPIV4', 'N'),
                  DbLogColumn('KPIV5', 'N'),
                  DbLogColumn('KPIV6', 'N'),
                  DbLogColumn('KPIV7', 'N'),
                  DbLogColumn('KPIV8', 'N'),
                  DbLogColumn('KPIV9', 'N'),
                  DbLogColumn('KPIV10', 'N'),
                  DbLogColumn('KPIV11', 'N'),
                  DbLogColumn('KPIV12', 'N'),
                  DbLogColumn('KPIV13', 'N'),
                  DbLogColumn('KPIV14', 'N'),
                  DbLogColumn('KPIV15', 'N'),
                  DbLogColumn('KPIV16', 'N'),
                  DbLogColumn('KPIV17', 'N'),
                  DbLogColumn('KPIV18', 'N'),
                  DbLogColumn('KPIV19', 'N'),
                  DbLogColumn('KPIV20', 'N'),
                  DbLogColumn('KPIV21', 'N'),
                  DbLogColumn('KPIV22', 'N'),
                  DbLogColumn('KPIV23', 'N'),
                  DbLogColumn('KPIV24', 'N'),
                  DbLogColumn('KPIV25', 'N'),
                  DbLogColumn('KPIV26', 'N'),
                  DbLogColumn('KPIV27', 'N'),
                  DbLogColumn('KPIV28', 'N'),
                  DbLogColumn('KPIV29', 'N'),
                  DbLogColumn('KPIV30', 'N'),
                           ]
            },
      'P_PBIC_KPIV_CRT2':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('KPIV1', 'N'),
                  DbLogColumn('KPIV2', 'N'),
                  DbLogColumn('KPIV3', 'N'),
                  DbLogColumn('KPIV4', 'N'),
                  DbLogColumn('KPIV5', 'N'),
                  DbLogColumn('KPIV6', 'N'),
                  DbLogColumn('KPIV7', 'N'),
                  DbLogColumn('KPIV8', 'N'),
                  DbLogColumn('KPIV9', 'N'),
                  DbLogColumn('KPIV10', 'N'),
                  DbLogColumn('KPIV11', 'N'),
                  DbLogColumn('KPIV12', 'N'),
                  DbLogColumn('KPIV13', 'N'),
                  DbLogColumn('KPIV14', 'N'),
                  DbLogColumn('KPIV15', 'N'),
                  DbLogColumn('KPIV16', 'N'),
                  DbLogColumn('KPIV17', 'N'),
                  DbLogColumn('KPIV18', 'N'),
                  DbLogColumn('KPIV19', 'N'),
                  DbLogColumn('KPIV20', 'N'),
                  DbLogColumn('KPIV21', 'N'),
                  DbLogColumn('KPIV22', 'N'),
                  DbLogColumn('KPIV23', 'N'),
                  DbLogColumn('KPIV24', 'N'),
                  DbLogColumn('KPIV25', 'N'),
                  DbLogColumn('KPIV26', 'N'),
                  DbLogColumn('KPIV27', 'N'),
                  DbLogColumn('KPIV28', 'N'),
                  DbLogColumn('KPIV29', 'N'),
                  DbLogColumn('KPIV30', 'N'),
                           ]
            },
         
      }

   if testSwitch.FE_0143730_399481_P_SEND_WEAK_WRITE_DELTA_TABLE_TO_DB:
      OracleTables.update({
         'P_WEAK_WRITE_BER_DELTA':
         {
            'type': 'S',
            'fieldList' : [
               DbLogColumn('SPC_ID', 'V'),
               DbLogColumn('OCCURRENCE', 'N'),
               DbLogColumn('SEQ', 'N'),
               DbLogColumn('TEST_SEQ_EVENT', 'N'),
               DbLogColumn('HD_LGC_PSN', 'N'),
               DbLogColumn('HD_PHYS_PSN', 'N'),
               DbLogColumn('DATA_ZONE', 'N'),
               DbLogColumn('BITS_READ_LOG10', 'N'),
               DbLogColumn('HARD_ERROR_RATE', 'N'),
               DbLogColumn('HARD_ERROR_DELTA', 'N'),
               DbLogColumn('OTF_ERROR_RATE', 'N'),
               DbLogColumn('OTF_ERROR_DELTA', 'N'),
               DbLogColumn('RAW_ERROR_RATE', 'N'),
               DbLogColumn('RAW_ERROR_DELTA', 'N'),
            ]
         },
      })
   if testSwitch.FE_0167320_007955_CREATE_P_DELTA_BURNISH_TA_SUM_COMBO:
      OracleTables.update({
         'P134_TA_SUM_HD2':
         {
            'type': 'S',
            'fieldList':[
               DbLogColumn('SPC_ID', 'V'),
               DbLogColumn('OCCURRENCE', 'N'),
               DbLogColumn('SEQ', 'N'),
               DbLogColumn('TEST_SEQ_EVENT', 'N'),
               DbLogColumn('HD_PHYS_PSN','N'),
               DbLogColumn('HD_LGC_PSN','N'),
               DbLogColumn('TA_CNT','N'),
               DbLogColumn('SQRT_AMP_WIDTH','N'),
               DbLogColumn('MAX_AMP_WIDTH','N'),
               DbLogColumn('AMP0_CNT','N'),
               DbLogColumn('AMP1_CNT','N'),
               DbLogColumn('AMP2_CNT','N'),
               DbLogColumn('AMP3_CNT','N'),
               DbLogColumn('AMP4_CNT','N'),
               DbLogColumn('AMP5_CNT','N'),
               DbLogColumn('AMP6_CNT','N'),
               DbLogColumn('AMP7_CNT','N'),
               ]
         },
         'P_DELTA_BURNISH_TA_SUM_COMBO':
         {
            'type': 'S',
            'fieldList':[
               DbLogColumn('SPC_ID', 'V'),
               DbLogColumn('OCCURRENCE', 'N'),
               DbLogColumn('SEQ', 'N'),
               DbLogColumn('TEST_SEQ_EVENT', 'N'),
               DbLogColumn('HD_PHYS_PSN', 'N'),
               DbLogColumn('HD_LGC_PSN', 'N'),
               DbLogColumn('TEST_TYPE', 'N'),
               DbLogColumn('ACTIVE_HEATER', 'N'),
               DbLogColumn('DELTA_BURNISH_CHECK', 'N'),
               DbLogColumn('TA_CNT', 'N'),
               DbLogColumn('SQRT_AMP_WIDTH','N'),
               DbLogColumn('MAX_AMP_WIDTH','N'),
               DbLogColumn('AMP0_CNT','N'),
               DbLogColumn('AMP1_CNT','N'),
               DbLogColumn('AMP2_CNT','N'),
               DbLogColumn('AMP3_CNT','N'),
               DbLogColumn('AMP4_CNT','N'),
               DbLogColumn('AMP5_CNT','N'),
               DbLogColumn('AMP6_CNT','N'),
               DbLogColumn('AMP7_CNT','N'),
                    ]
         },
      })

   if testSwitch.FE_0170519_407749_P_HSA_BP_ENABLE_DELTA_BURNISH_AND_OTF_CHECK:
      OracleTables.update({
         'P_HSA_BP_DELTA_OTF_TABLE':
         {
            'type': 'S',
            'fieldList':[
               DbLogColumn('SPC_ID', 'V'),
               DbLogColumn('OCCURRENCE', 'N'),
               DbLogColumn('SEQ', 'N'),
               DbLogColumn('TEST_SEQ_EVENT', 'N'),
               DbLogColumn('HD_PHYS_PSN', 'N'),
               DbLogColumn('DATA_ZONE', 'N'),
               DbLogColumn('HD_LGC_PSN', 'N'),
               DbLogColumn('DELTA_OTF', 'N'),
               DbLogColumn('HSA_BP_PN', 'N'),
           ]
         },
         'P_HSA_BP_DELTA_BURNISH_CHECK':
         {
            'type': 'S',
            'fieldList':[
               DbLogColumn('SPC_ID', 'V'),
               DbLogColumn('OCCURRENCE', 'N'),
               DbLogColumn('SEQ', 'N'),
               DbLogColumn('TEST_SEQ_EVENT', 'N'),
               DbLogColumn('HD_PHYS_PSN', 'N'),
               DbLogColumn('HD_LGC_PSN', 'N'),
               DbLogColumn('TEST_TYPE', 'N'),
               DbLogColumn('ACTIVE_HEATER', 'N'),
               DbLogColumn('DELTA_BURNISH_CHECK', 'N'),
               DbLogColumn('HSA_BP_PN', 'N'),
           ]
         },
         'P152_BODE_GAIN_PHASE': 
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('FREQUENCY', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('GAIN', 'N'),
                  DbLogColumn('PHASE', 'N'),

                                       ]
           },
        'P152_BODE_SCRN_SUM': 
           {
               'type': 'M',
               'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('TRACK', 'N'),
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('FILTER_IDX', 'N'),
                  DbLogColumn('FREQ_START', 'N'),
                  DbLogColumn('FREQ_END', 'N'),
                  DbLogColumn('MAX_GAIN', 'N'),
                  DbLogColumn('GAIN_LIMIT', 'N'),
                  DbLogColumn('STATUS', 'N'),
                                       ]
           },

      })

   if 0:#testSwitch.OW_DATA_COLLECTION:
      OracleTables.update({
         'P061_OW_MEASUREMENT':
           {
              'type': 'M',
              'fieldList': [
                 DbLogColumn('HD_PHYS_PSN', 'N', 0),
                 DbLogColumn('DATA_ZONE', 'N', 0),
                 DbLogColumn('HD_LGC_PSN', 'V', 0),
                 DbLogColumn('TRK_NUM', 'N', 0),
                 DbLogColumn('HSC_2T_DATA', 'N', 0),
                 DbLogColumn('DEV_2T_DATA', 'N', 0),
                 DbLogColumn('DEV_DIV_AVE_2T', 'N', 0),
                 DbLogColumn('HSC_MIN_2T', 'N', 0),
                 DbLogColumn('MIN_2T_SS', 'N', 0),
                 DbLogColumn('HSC_MAX_2T', 'V', 0),
                 DbLogColumn('MAX_2T_SS', 'N', 0),
                 DbLogColumn('DELTA_2T', 'N', 0),
                 DbLogColumn('HSC_13T_DATA', 'V', 0),
                 DbLogColumn('DEV_13T_DATA', 'N', 0),
                 DbLogColumn('DEV_DIV_AVE_13T', 'N', 0),
                 DbLogColumn('OW_MEASUREMENT', 'N', 0),
                 DbLogColumn('MODE', 'N', 0),
                 DbLogColumn('WRT_CUR', 'N', 0),
                 DbLogColumn('OVS_WRT_CUR', 'N', 0),
                 DbLogColumn('OVS_DUR', 'V', 0),
                 DbLogColumn('WRITE_HEAT', 'N', 0),
                 DbLogColumn('READ_HEAT', 'V', 0),
               ]
           },
      })

   if 1:
      OracleTables.update({
         'P321_BIAS_CAL2_MRE_DIFF': OracleTables['P186_BIAS_CAL2_MRE_DIFF']
      })

      OracleTables.update({
         'DBS_MTRIX_BY_ZONE':
         {
            'type': 'M',
            'fieldList': [
                DbLogColumn('HD_PHYS_PSN', 'N', 0),
                DbLogColumn('DATA_ZONE', 'N', 0),
                DbLogColumn('SPC_ID', 'V', 0),
                DbLogColumn('OCCURRENCE', 'N', 0),
                DbLogColumn('SEQ', 'N', 0),
                DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                DbLogColumn('RAW_BER', 'N', 0),
                DbLogColumn('STDEV', 'N', 0),
                DbLogColumn('DELTA', 'N', 0),
                DbLogColumn('AVG_STDEV_HD', 'N', 0),
                DbLogColumn('AVG_DELTA_HD', 'N', 0),
                DbLogColumn('COUNT', 'N', 0),
            ]
         },
      })
   if 1:
      OracleTables.update({
         'P_DTH_ADDER':
         {
            'type': 'M',
            'fieldList': [
                DbLogColumn('HD_PHYS_PSN', 'N', 0),
                DbLogColumn('READ_SCRN2_AVG', 'N', 0),
                DbLogColumn('READ_SCRN2H_AVG', 'N', 0),
                DbLogColumn('DELTA_BER', 'N', 0),
                DbLogColumn('DTH_COMPENSATION', 'N', 0),
                DbLogColumn('WH_DTH_OLD', 'N', 0),
                DbLogColumn('RH_DTH_OLD', 'N', 0),
                DbLogColumn('WH_DTH_NEW', 'N', 0),
                DbLogColumn('RH_DTH_NEW', 'N', 0),
            ]
         },
      })

      OracleTables.update({
         'ADZ_SUMARRY':
         {
            'type': 'M',
            'fieldList': [
                DbLogColumn('SPC_ID', 'V', 0),
                DbLogColumn('OCCURRENCE', 'N', 0),
                DbLogColumn('SEQ', 'N', 0),
                DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                DbLogColumn('DEF_ZOUT', 'N', 0),
                DbLogColumn('DEF_ZOUT_OHM', 'N', 0),
                DbLogColumn('BEST_ZOUT', 'N', 0),
                DbLogColumn('BEST_ZOUT_OHM', 'N', 0),
                DbLogColumn('DEF_EQU_BEST', 'N', 0),
            ]
         },
      })

   if testSwitch.FE_0148166_381158_DEPOP_ON_THE_FLY:
      OracleTables.update({
         'P176_TIMEOUT_FAIL_DEPOP':
         {
            'type': 'S',
            'fieldList' : [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('HD_STATUS', 'N', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
            ]
         },
      })

   OracleTables.update({
      'P_TCC_BY_BER':
      {
         'type': 'S',
         'fieldList' : [
               DbLogColumn('SPC_ID', 'V', 0),
               DbLogColumn('OCCURRENCE', 'N', 0),
               DbLogColumn('SEQ', 'N', 0),
               DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
               DbLogColumn('HD_LGC_PSN', 'N', 0),
               DbLogColumn('HD_PHYS_PSN', 'N', 0),
               DbLogColumn('SEGMENT', 'N', 0),
               DbLogColumn('DATA_ZONE', 'N', 0),
               DbLogColumn('STEP', 'N', 0),
               DbLogColumn('STEP_SIZE', 'N', 0),
               DbLogColumn('NEW_TCC1', 'N', 0),
               DbLogColumn('ORIG_TCC1', 'N', 0),
               DbLogColumn('TARGET_BER', 'N', 0),
               DbLogColumn('FINAL_BER', 'N', 0),
               DbLogColumn('START_BER', 'N', 0),
               DbLogColumn('SLOPE_TYPE', 'N', 0),
               DbLogColumn('DIRECTION', 'N', 0),
               DbLogColumn('REVERT', 'N', 0),
               DbLogColumn('DELTA_PRE_HEAT', 'N', 0),
               DbLogColumn('DELTA_WRT_HEAT', 'N', 0),
               DbLogColumn('DELTA_RD_HEAT', 'N', 0),
         ]
      },
   })

   OracleTables.update({
      'P_PHOTO_DIODE_SUMMARY':
      {
         'type': 'S',
         'fieldList' : [
               DbLogColumn('SPC_ID', 'V', 0),
               DbLogColumn('OCCURRENCE', 'N', 0),
               DbLogColumn('SEQ', 'N', 0),
               DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
               DbLogColumn('HD_PHYS_PSN', 'N', 0),
               DbLogColumn('HD_LGC_PSN', 'N', 0),
               DbLogColumn('DATA_ZONE', 'N', 0),
               DbLogColumn('PD_GAIN', 'N', 0),
               DbLogColumn('IBIAS_LASER_CUR_DAC', 'N', 0),
               DbLogColumn('IBIAS_LASER_CUR_MA', 'N', 0),
         ]
      },
   })

   OracleTables.update({
      'P_HAMR_LASER_CALIBRATION':
      {
         'type': 'S',
         'fieldList' : [
               DbLogColumn('SPC_ID', 'V', 0),
               DbLogColumn('OCCURRENCE', 'N', 0),
               DbLogColumn('SEQ', 'N', 0),
               DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
               DbLogColumn('HD_PHYS_PSN', 'N', 0),
               DbLogColumn('HD_LGC_PSN', 'N', 0),
               DbLogColumn('DATA_ZONE', 'N', 0),
               DbLogColumn('MSRD_INTRPLTD', 'N', 0),
               DbLogColumn('LASER_THRSHLD_CUR_DAC', 'N', 0),
               DbLogColumn('LASER_OPERATING_CUR_DAC', 'N', 0),
               DbLogColumn('LASER_TOTAL_CUR_MA', 'N', 0),
         ]
      },
   })

   OracleTables.update({
      'P_FINE_LASER_CAL':
      {
         'type': 'S',
         'fieldList' : [
               DbLogColumn('SPC_ID', 'V', 0),
               DbLogColumn('OCCURRENCE', 'N', 0),
               DbLogColumn('SEQ', 'N', 0),
               DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
               DbLogColumn('HD_PHYS_PSN', 'N', 0),
               DbLogColumn('HD_LGC_PSN', 'N', 0),
               DbLogColumn('DATA_ZONE', 'N', 0),
               DbLogColumn('LASER_THRSHLD_CUR_DAC', 'N', 0),
               DbLogColumn('LASER_OPERATING_CUR_DAC', 'N', 0),
               DbLogColumn('WORKING_WRWH_DAC', 'N', 0),
               DbLogColumn('SNGL_TRK_BER', 'N', 0),
               DbLogColumn('SQZ_TRK_BER', 'N', 0),
               DbLogColumn('BER_DELTA', 'N', 0),
               DbLogColumn('SWEEP_MODE', 'N', 0),
               DbLogColumn('LDI_UPDATE_FLAG', 'N', 0),
         ]
      },
   })
   OracleTables.update({
      'P_HAMR_LBC_SETTINGS':
      {
         'type': 'S',
         'fieldList' : [
               DbLogColumn('SPC_ID', 'V', 0),
               DbLogColumn('OCCURRENCE', 'N', 0),
               DbLogColumn('SEQ', 'N', 0),
               DbLogColumn('TEST_SEQ_EVENT', 'N', 0),                            
               DbLogColumn('HD_LGC_PSN', 'N', 0),                                
               DbLogColumn('DATA_ZONE', 'N', 0),                                 
               DbLogColumn('RAP_MASTER_SWITCH', 'N', 0),                         
               DbLogColumn('SAP_MASTER_SWITCH', 'N', 0),                         
               DbLogColumn('SAP_PD_HARDWARE_GAIN', 'N', 0),                      
               DbLogColumn('SAP_PD_LOW_PASS_FILTER', 'N', 0),                    
               DbLogColumn('SAP_LBC_KP', 'N', 0),                                
               DbLogColumn('SAP_LBC_KI', 'N', 0),                                
               DbLogColumn('RAP_MLCFCA', 'N', 0),                                
               DbLogColumn('RAP_ITH_OFFSET', 'N', 0),     
               DbLogColumn('RAP_PD_TARGET', 'N', 0),             ]
      },
   })
   OracleTables.update({
      'P_HAMR_SERVO_LASER_CTRL':
      {
         'type': 'S',
         'fieldList' : [
               DbLogColumn('SPC_ID', 'V', 0),
               DbLogColumn('OCCURRENCE', 'N', 0),
               DbLogColumn('SEQ', 'N', 0),
               DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
               DbLogColumn('OUTPUT_ACCUM', 'N', 0),
               DbLogColumn('OUTPUT_AVG', 'N', 0),
               DbLogColumn('ERROR_INTEGRAL', 'N', 0),
               DbLogColumn('STATUS', 'N', 0),
               DbLogColumn('NEW_MSRMNT', 'N', 0),
               DbLogColumn('NEW_TEST_MSRMNT', 'N', 0),
               DbLogColumn('CONTROL_EFFORT', 'N', 0), 
               DbLogColumn('CMD_THRSH_CURR', 'N', 0), 
               DbLogColumn('PD_TARGET', 'N', 0),      
               DbLogColumn('MSRMNT_CNT', 'N', 0),     

         ]
      },
   })
   OracleTables.update({
      'P_HAMR_SERVO_DIAG_INFO':
      {
         'type': 'S',
         'fieldList' : [
               DbLogColumn('SPC_ID', 'V', 0),
               DbLogColumn('OCCURRENCE', 'N', 0),
               DbLogColumn('SEQ', 'N', 0),                    
               DbLogColumn('TEST_SEQ_EVENT', 'N', 0),         
               DbLogColumn('MAX_IBIAS_CYL', 'N', 0),          
               DbLogColumn('MAX_CMD_IBIAS', 'N', 0),          
               DbLogColumn('MAX_CMD_IOP', 'N', 0),            
               DbLogColumn('MAX_POS_IBIAS_ADJ', 'N', 0),      
               DbLogColumn('MAX_NEG_IBIAS_ADJ', 'N', 0),      
               DbLogColumn('MAX_WHRM', 'N', 0),               
               DbLogColumn('MAX_WHWM', 'N', 0),               
               DbLogColumn('MAX_RHRM', 'N', 0),
               DbLogColumn('MAX_RHWM', 'N', 0),
               DbLogColumn('SWEEP_MODE', 'N', 0),
               DbLogColumn('LDI_UPDATE_FLAG', 'N', 0),
         ]
      },
   })

   if testSwitch.CONDITIONAL_RUN_HMS:
      OracleTables.update({
         'P_HMS_EWAC':
         {
            'type': 'S',
            'fieldList' : [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('AVE_HMS_CAP', 'N', 0),
                  DbLogColumn('MIN_HMS_CAP', 'N', 0),
                  DbLogColumn('AVE_EWAC', 'N', 0),
                  DbLogColumn('HMS_SKIP', 'N', 0),
            ]
         },
      })
   if testSwitch.FE_0207956_463655_AFH_ENABLE_WGC_CLR_TUNING:
      OracleTables.update({
           'P253_WGC_ELT_CODEWORD':
           {
              'type': 'M',
              'fieldList': [
                  DbLogColumn('HD_PHYS_PSN', 'N', 0),
                  DbLogColumn('DATA_ZONE', 'N', 0),
                  DbLogColumn('SPC_ID', 'V', 0),
                  DbLogColumn('OCCURRENCE', 'N', 0),
                  DbLogColumn('SEQ', 'N', 0),
                  DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                  DbLogColumn('CWD_00', 'N', 0),
                  DbLogColumn('CWD_01', 'N', 0),
                  DbLogColumn('CWD_02', 'N', 0),
                  DbLogColumn('CWD_03', 'N', 0),
                  DbLogColumn('CWD_04', 'N', 0),
                  DbLogColumn('CWD_05', 'N', 0),
                  DbLogColumn('CWD_06', 'N', 0),
                  DbLogColumn('CWD_07', 'N', 0),
                  DbLogColumn('CWD_08', 'N', 0),
                  DbLogColumn('CWD_09', 'N', 0),
                  DbLogColumn('CWD_REF', 'N', 0),
                  DbLogColumn('WRTHEAT', 'N', 0),
                  DbLogColumn('TRG_CLR', 'N', 0),
                  DbLogColumn('CW_CNT', 'N', 0),
                   ]
           },
      })
   if testSwitch.FE_0208720_470167_P_AUTO_DOWNGRADE_BLUENUN_FAIL_FOR_APPLE:
      OracleTables.update({
         'P_SCREENS_STATUS':
           {
            'type': 'S',
            'fieldList': [
               DbLogColumn('SCREEN', 'N', 0),
               DbLogColumn('STATUS', 'N', 0),
               ]
           },
         })
   if testSwitch.FE_0271421_403980_P_ZONE_COPY_OPTIONS:
      OracleTables.update({
          'OPTI_ZN_SUMMARY':
            {
             'type': 'M',
             'fieldList': [
                 DbLogColumn('HD_PHYS_PSN', 'N', 0),
                 DbLogColumn('OPTI_ZONE', 'N', 0),
                 DbLogColumn('ZN_GRP_START', 'N', 0),
                 DbLogColumn('ZN_GRP_END', 'N', 0),
                 DbLogColumn('ZN_COPY_OPTION', 'N', 0),
                 ]
            },
         })
   if testSwitch.FE_0345891_348429_TPIM_SOVA_USING_FIX_TRANSFER:
      OracleTables.update({
         'P_VBAR_MAX_FORMAT_SUMMARY':
            {
               'type': 'S',
               'fieldList': [
                  DbLogColumn('SPC_ID', 'V'),
                  DbLogColumn('OCCURRENCE', 'N'),
                  DbLogColumn('SEQ', 'N'),
                  DbLogColumn('TEST_SEQ_EVENT', 'N'),
                  DbLogColumn('HD_PHYS_PSN', 'N'),
                  DbLogColumn('HD_LGC_PSN', 'N'),
                  DbLogColumn('DATA_ZONE', 'N'),
                  DbLogColumn('BPI_CAP', 'N'),
                  DbLogColumn('BPIM_SEG', 'N'),
                  DbLogColumn('BPIM_FSOW', 'N'),
                  DbLogColumn('BPIM_HMS', 'N'),
                  DbLogColumn('BPIM_SQZBPIC', 'N'),
                  DbLogColumn('BPIM_FINAL', 'N'),
                  DbLogColumn('BPIP_MAX', 'N'),
                  DbLogColumn('TPI_CAP', 'N'),
                  DbLogColumn('TPIM_ATI', 'N'),
                  DbLogColumn('TPIP_MAX', 'N'),
                  DbLogColumn('ADC_MAX', 'N'),
                  DbLogColumn('NIBLET_IDX', 'N'),
                  DbLogColumn('TPIM_OTC', 'N'),
                  DbLogColumn('TPIM_SOVA', 'N'),
                           ]
            },
         })
   if testSwitch.FE_0308035_403980_P_MULTIMATRIX_TRIPLET:
      OracleTables.update({
          'MMT_SUMMARY':
            {
             'type': 'M',
             'fieldList': [
                 DbLogColumn('SPC_ID', 'V', 0),
                 DbLogColumn('OCCURRENCE', 'N', 0),
                 DbLogColumn('SEQ', 'N', 0),
                 DbLogColumn('TEST_SEQ_EVENT', 'N', 0),
                 DbLogColumn('HD_LGC_PSN', 'N', 0),
                 DbLogColumn('DATA_ZONE', 'N', 0),
                 DbLogColumn('SOVAIWKP', 'N', 0),
                 DbLogColumn('OWIWKP', 'N', 0),
                 DbLogColumn('OW', 'N', 0),
                 DbLogColumn('HMSIWKP', 'N', 0),
                 DbLogColumn('IWLB', 'N', 0),
                 DbLogColumn('IWUB', 'N', 0),
                 DbLogColumn('COG_SWEEP', 'N', 0),
                 DbLogColumn('OSD', 'N', 0),
                 DbLogColumn('OSA', 'N', 0),
                 DbLogColumn('IW', 'N', 0),
                 ]
            },
         })

if __name__ == "__main__":
   tableFMT = '#define %(name)s            65000  // %(cols)s'
   colWidthFMT = '//      %(name)-43s// %(colWidths)s'
   colMaskFMT = '//      %(name)-43s// %(colMasks)s'
   coltypeFMT = '//      %(name)-43s// %(dataTypes)s'
   tblTypeFMT = '//      %(name)-43s// %(type)s'

   evalTable = 'P_USER_SLIP_LIST'
   #evalTable = None

   if evalTable == None:
      tables = DbLogTableDefinitions.OracleTables.items()
   else:
      tables = [(evalTable,DbLogTableDefinitions.OracleTables[evalTable]),]

   procHeaders = ['SPC_ID', 'SEQ', 'TEST_SEQ_EVENT', 'OCCURRENCE']

   for tableName,table in tables:
      delIndicies = []
      for index,col in enumerate(table['fieldList']):
         if col.getName() in procHeaders:
            delIndicies.append(index)

      for enumId, index in enumerate(delIndicies):
         del table['fieldList'][index-enumId]


      cols = [i.getName() for i in table['fieldList']]
      columnWidths = [str(len(i)) for i in cols]

      genFMTStr = '%c%ss'

      colFmts = [genFMTStr % ('%',i) for i in columnWidths]


      colMasks = [str(i.getDbUpload()) for i in table['fieldList']]
      dataTypes = [i.getType() for i in table['fieldList']]


      print tableFMT % {'name':tableName, 'cols':','.join(cols), }
      print colWidthFMT % {'name':tableName+'_COL_WIDTH','colWidths':','.join([i % (columnWidths[index],) for index,i in enumerate(colFmts)]), }
      print colMaskFMT % {'name':tableName+'_COL_MASK','colMasks':','.join([i % (colMasks[index],) for index,i in enumerate(colFmts)])}
      print coltypeFMT % {'name':tableName+'_COL_TYPES','dataTypes':  ','.join([i % (dataTypes[index],) for index,i in enumerate(colFmts)]), }
      print tblTypeFMT % {'name':tableName+'_TABLE_TYPE','type':table['type']}
