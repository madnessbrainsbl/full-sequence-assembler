#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Contains p/n to rim type mappings
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/13 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/RL42/RimTypes.py $
# $Revision: #1 $
# $DateTime: 2016/05/13 03:43:43 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/RL42/RimTypes.py#1 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#

import base_RimTypes

intfTypeMatrix = \
   {
   'SATA':
      {
      'rimTypeMatrix':
         {
         'PRE2'   :['55', 'C7', '5A', '51', '54', '56', 'C5', '5B'], #AAB: added C5 added 5B
         'CAL2'   :['55', 'C7', '5A', '51', '54', '56', 'C5'], #AAB: added C5
         'FNC2'   :['55', 'C7', '5A', '51', '54', '56', 'C5'], #AAB: added C5
         'SDAT2'  :['55', 'C7', '5A', '51', '54', '56', 'C5'], #AAB: added C5
         'CRT2'   :['75', 'C7', '51', '54', '56', 'C5', '57'], #AAB: added C5
         'MQM2'   :['57', 'C7', '51', '54', '56', 'C5', '75'], #AAB: added C5
         'CMT2'   :['57', '53', '56', 'C7'], #AAB: added C7
#CHOOI-03Jun17 OffSpec
#         'FIN2'   :['57', 'DF', '53', '56', 'C7', '75', '5B'], #AAB: added C7 added 75: for No-IO FIN2 Support added 5B
         'FIN2'   :['75', 'DF', '53', '56', 'C7', '75', '5B'], #AAB: added C7 added 75: for No-IO FIN2 Support added 5B
         'CUT2'   :['57', 'DF', '53', '56', 'C7'], #AAB: added C7
         'FNG2'   :['57', '53', '56', 'C7'], #AAB: added C7
         'AUD2'   :['C7', '53', '56', 'C7'], #AAB: added C7
         'IDT2'   :['57', '53', '56', 'C7'], #AAB: added C7
         'CCV2'   :['57', '53', '56', 'C7'], #AAB: added C7
         },
      'riserTypeMatrix':
         base_RimTypes.riserTypeMatrix_SATA,
      },
   'FC':
      {
      'rimTypeMatrix':
         {
         '' : []
         },
      'riserTypeMatrix':
         base_RimTypes.riserTypeMatrix_FC,
      },
   'SAS':
      {
      'rimTypeMatrix':
         {
         'PRE2'   :['61', '6E'],
         'CAL2'   :['61', '6E'],
         'HDT'    :['XX'],
         'FNC'    :['61', '6E'],
         'FNC2'   :['61', '6E'],
         'SDAT2'  :['61', '6E'],
         'SPSC2'  :['61', '6E'],
         'CRT2'   :['EG','63'],
         'CMT2'   :['EG','63'],
         'IOSC2'  :['EG','63'],
         'FIN2'   :['EG','63'],
         'AUD2'   :['EG','63'],
         'CUT2'   :['EG','63'],
         'IDT2'   :['EG','63'],
         },
      'riserTypeMatrix':
         base_RimTypes.riserTypeMatrix_35_SAS,
      }
   }

#CHK_18V_RISER = ['11', '12', '24', '31', '33', '41']
#---------------------------------------------------------------------------------------------------------#
