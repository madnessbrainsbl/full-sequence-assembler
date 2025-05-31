#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2010, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: AFH Parameters for Tambora
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/st054Params_AFH.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $perp
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/st054Params_AFH.py#1 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#




########################################################################################################################################################################
#
#          Function:  getSelfTest054Dictionary
#
#   Original Author:  D. Klingbeil / Michael T. Brady
#
#       Description:  Get the pressure sensor test paramaters for self-test 054
#
#             Input:  programName       # program name(str)               e.g. Tambora, Carib, Grenada, etc.
#                     AABType           # Advanced Air Bearing Type(str)  e.g. '201.02', '201.04', etc.
#                     siteName          # Site name(str)                  e.g. 'LCO'
#                     headVendor        # head vendor(string)             e.g. "RHO", "TDK", "HWY", etc.
#
#      Return Value:  prm_054_PressureSensorCal(dict)
#
########################################################################################################################################################################


def getSelfTest054Dictionary(programName, AABType, siteName, headVendor ):


   prm_054_PressureSensorCal = {
      'test_num'                 : 54,
      'prm_name'                 : 'prm_054_PressureSensorCal',
      'timeout'                  : 60,
      'spc_id'                   : 1,
      'CWORD1'                   : 0x0001,
      #'LIMIT32'                  : (600, 10),
      'NUM_SAMPLES'              : 10,
      'MIN_ALTITUDE_ADJ'         : 3000,
      'MAX_ALTITUDE_ADJ'         : 15000,
      }
   if programName == 'Carib':
      prm_054_PressureSensorCal.update({'MIN_ALTITUDE_ADJ' : 500, 'MAX_ALTITUDE_ADJ' : 15000})
      prm_054_PressureSensorCal.update({'LIMIT32' : (600, 100), 'REF_ADC' :  248 })
      prm_054_PressureSensorCal.update({'timeout' : 160})

   if headVendor in ['TDK', 'HWY']:
      headVendor = 'TDK'


   pscCoeff = {
      'Carib': {
         'RHO'       : {
            '110.38' : ( 464, 2630, -553 ),  # put in for VE
            '201.01NH_2HTR'    : (464, 2630, -553),
            }, # end of Carib RHO
         'TDK'    : {
            'TDK_WT6G'  : (0.467900313, 2.63338E-06, -5.53515E-12),
            }, # end of Carib TDK
         },
      'Tambora'   : {
         'RHO'       : {
            '201.02'    : (802, -6666, 3230), # First look.Evaluated with NWM lube/201.02 aab
            '201.04'    : (802, -6666, 3230), # These are .02 coefficients 
            '201.08'    : (841, -6676, 3191), # These are .08 coefficients
            '110.88'    : (0x0000, 0x0000, 0x0001),
            }, # end of Tambora RHO
         'TDK'    : {
            'SG1'       : (474, -9431, 4522), # Gen 2B TDK LPL-2.
            }, # end of Tambora TDK
         'MIN_ALTITUDE_ADJ'         : 4500,
         'MAX_ALTITUDE_ADJ'         : 15000,  ## Tambora specific adjustments
         }, # end of Tambora
      } # end of pscCoeff

   prm_054_PressureSensorCal['PSC_COEFF'] = pscCoeff[programName][headVendor][AABType]


   if siteName in ['LCO']:
      prm_054_PressureSensorCal.update({'REF_ADC':(248)})      # Location relative to about 5kft Altitude
   else:
      prm_054_PressureSensorCal.update({'REF_ADC':(300)})      # Location relative to about 300ft Altitude
      # should this be 300 or 303 in the factory?


   return prm_054_PressureSensorCal
