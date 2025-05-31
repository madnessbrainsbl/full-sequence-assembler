#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: All global constants live within this file
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_canonParams.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_canonParams.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

#######################################################################################################################
#######################################################################################################################
# 
# File name is AFH Canonical Parameters
# Canonical in this case refers to the decree that this file 
# will never ever have if testSwitch.flag logic contained in it.
# 
#######################################################################################################################
#######################################################################################################################


#######################################################################################################################
#
#  Imports
# 
#######################################################################################################################

from Constants import *
from Drive import objDut
from ProgramName import getProgramNameGivenTestSwitch
import ScrCmds

#######################################################################################################################
#
#  Functions
# 
#######################################################################################################################


def getTargetClearance():
   programName = getProgramNameGivenTestSwitch( testSwitch )
   dut = objDut
   headType = dut.HGA_SUPPLIER
   
   defaultProfileDict = getTargetClearanceLowerLevel(    
                                    programName,             dut.numZones,           headType,
                                    dut.rpm,                 dut.servoWedges,        dut.AABType,
                                    dut.isDriveDualHeater,   testSwitch.virtualRun
                               )

   # Check to make sure the below data structure was populated with the correct number of elements
   # Based on production mode in order to avoid adding a test switch and breaking the original design
   if ConfigVars[CN]['PRODUCTION_MODE'] == 0:
      fails = []
      for clearance_type in defaultProfileDict.keys():
         if len(defaultProfileDict[clearance_type]) != (dut.numZones + 1):
            fails.append(clearance_type)
      if fails and not testSwitch.virtualRun:
         ScrCmds.raiseException(11044, 'Incorrect number of clearance values entered for these entries: %s' % fails)

   return defaultProfileDict




#######################################################################################################################
#
#               Function:  getTargetClearance
#
#        Original Author:  Michael T. Brady
#
#            Description:  get the target clearance
#
#         Special Notice:  
# 
#                          NEVER EVER PUT if testSwitch.flag  logic into this function.
# 
#                          This function is meant to be very easy to read and maintained by people who are outside of the firmware group.
#                          To be more explicit, every change should be modifying an existing value and no new code should need to be added
#                          in order to accomodate a change value <x> request for program <Y>.
#
#                  Input:  
#
#                 Return:  None
#
#######################################################################################################################

def getTargetClearanceLowerLevel(       programName,   numZones,           headType,
                                        RPM,           SpokesPerRev,       AABType,
                                        isDriveDualHeater,  virtualRun
                                ):
   ScriptComment("program_name %s, AABType %s" % (programName,AABType))
   if programName == 'M11P_BRING_UP':
      programName = 'M10P'
   elif programName == 'M11P':
      programName = 'M11P'
   else:
      programName = 'Kinta'
   
   targetClrDict = {
      'TGT_WRT_CLR' : {
         'Grenada'  :   {'TDK': [18.0] * (numZones + 1), 'RHO': [18.0] * (numZones + 1) },
         'Kahuna'   :   {'TDK': [18.0] * (numZones + 1), 'RHO': [18.0] * (numZones + 1) },
         'Megalodon':   {'TDK': [18.0] * (numZones + 1), 'RHO': [18.0] * (numZones + 1) },
         'M10P'       : {'TDK': [12.0] * (numZones + 1), 'RHO': [12.0] * (numZones + 1) },
         },
      'TGT_MAINTENANCE_CLR' : {
         'Grenada'  :   {'TDK': [18.0] * (numZones + 1), 'RHO': [18.0] * (numZones + 1) },
         'Kahuna'   :   {'TDK': [18.0] * (numZones + 1), 'RHO': [18.0] * (numZones + 1) },
         'Megalodon':   {'TDK': [18.0] * (numZones + 1), 'RHO': [18.0] * (numZones + 1) },
         'M10P'       : {'TDK': [12.0] * (numZones + 1), 'RHO': [12.0] * (numZones + 1) },
         },
      'TGT_PREWRT_CLR' : {
         'Grenada'  :   {'TDK': [18.0] * (numZones + 1), 'RHO': [18.0] * (numZones + 1) },
         'Kahuna'   :   {'TDK': [18.0] * (numZones + 1), 'RHO': [18.0] * (numZones + 1) },         
         'Megalodon':   {'TDK': [18.0] * (numZones + 1), 'RHO': [18.0] * (numZones + 1) },
         'M10P'       : {'TDK': [12.0] * (numZones + 1), 'RHO': [12.0] * (numZones + 1) },
         },
      'TGT_RD_CLR' : {
         'Grenada'  :   {'TDK': [28.0] * (numZones + 1), 'RHO': [28.0] * (numZones + 1) },
         'Kahuna'   :   {'TDK': [18.0] * (numZones + 1), 'RHO': [18.0] * (numZones + 1) },         
         'Megalodon':   {'TDK': [28.0] * (numZones + 1), 'RHO': [28.0] * (numZones + 1) },
         'M10P'       : {'TDK': [12.0] * (numZones + 1), 'RHO': [12.0] * (numZones + 1) },
         },
   }

   defaultProfileDict = {}
   
   if programName in ['Kinta']:
      from TestParamExtractor import TP
      defaultProfileDict = TP.afhZoneTargets
   else:
      defaultProfileDict['TGT_WRT_CLR']          = targetClrDict['TGT_WRT_CLR'][programName][headType]
      defaultProfileDict['TGT_MAINTENANCE_CLR']  = targetClrDict['TGT_MAINTENANCE_CLR'][programName][headType]
      defaultProfileDict['TGT_PREWRT_CLR']       = targetClrDict['TGT_PREWRT_CLR'][programName][headType]
      defaultProfileDict['TGT_RD_CLR']           = targetClrDict['TGT_RD_CLR'][programName][headType] 
 
   return defaultProfileDict
   # end of getTargetClearance


def getTCS_values():
   programName = getProgramNameGivenTestSwitch( testSwitch )
   dut = objDut
   headType = dut.HGA_SUPPLIER
   tcc_DH_values = getTCS_valuesLowerLevel(programName, headType)

   return tcc_DH_values




def getTCS_valuesLowerLevel(programName, headType):
   if programName == 'M11P_BRING_UP':
      programName = 'M10P'
   elif programName == 'M11P':
      programName = 'M11P'
   else:
      programName = 'Kinta'
   
#  "WRITER_HEATER":

   # Note the "Nan" values below are values that have never been set

   tcsInternalValuesDict = {

      # params relating to main slope TCC1

      'TCS1' : {
         "WRITER_HEATER": {
            'Grenada'  :   {'TDK': 0.09,     'RHO': 0.09  },
            'Kahuna'   :   {'TDK': 0.09,     'RHO': 0.09  },            
            'Megalodon':   {'TDK': 0.03,     'RHO': 0.03 },
            'Kinta':   {'TDK': -0.254,     'RHO': -0.127 },
            'M10P'     :   {'TDK':-0.1290,   'RHO':-0.1290},
         },
         "READER_HEATER": {
            'Grenada'  :   {'TDK': -0.17,    'RHO': -0.17 },
            'Kahuna'   :   {'TDK': -0.17,    'RHO': -0.17 },            
            'Megalodon':   {'TDK': -0.23,    'RHO': -0.23 },
            'Kinta':   {'TDK': -0.254,    'RHO': -0.3048 },
            'M10P'     :   {'TDK': -0.4328,  'RHO': -0.4328},
         },
      },
      'TCS1_USL' : {
         "WRITER_HEATER": {
            'Grenada'  :   {'TDK': 0.635,    'RHO': 0.635  },
            'Kahuna'   :   {'TDK': 1.000,    'RHO': 1.000  },            
            'Megalodon':   {'TDK': 0.7,      'RHO': 0.7  },
            'Kinta':   {'TDK': -0.127,      'RHO':-0.127},
            'M10P'     :   {'TDK': 3.000,    'RHO': 3.000  },
         },
         "READER_HEATER": {
            'Grenada'  :   {'TDK': 0.465,    'RHO': 0.465  },
            'Kahuna'   :   {'TDK': 1.000,    'RHO': 1.000  },            
            'Megalodon':   {'TDK': 0.7,      'RHO': 0.7  },
            'Kinta':   {'TDK': -0.127,      'RHO': -0.127  },
            'M10P'     :   {'TDK': 3.000,    'RHO': 3.000  },
         },
      },
      'TCS1_LSL' : {
         "WRITER_HEATER": {
            'Grenada'  :   {'TDK': -0.635,   'RHO': -0.635  },
            'Kahuna'   :   {'TDK': -1.000,   'RHO': -1.000  },            
            'Megalodon':   {'TDK': -0.7,     'RHO': -0.7  },
            'Kinta':   {'TDK': -1.016,      'RHO': -1.016  },
            'M10P'     :   {'TDK': -3.000,   'RHO': -3.000  },
         },
         "READER_HEATER": {
            'Grenada'  :   {'TDK': -0.805,   'RHO': -0.805  },
            'Kahuna'   :   {'TDK': -1.000,   'RHO': -1.000  },            
            'Megalodon':   {'TDK': -0.7,     'RHO': -0.7  },
            'Kinta':   {'TDK': -1.016,      'RHO': -1.016  },
            'M10P'     :   {'TDK': -3.000,   'RHO': -3.000  },
         },
      },

      # params relating to TCC1 modified slope ( first started on Muskie )

      'enableModifyTCS_values'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 1,        'RHO': 1   }, 
            'Kahuna'   :   {'TDK': 1,        'RHO': 1   },             
            'Megalodon':   {'TDK': 1,        'RHO': 1   }, 
            'Kinta':   {'TDK': 1,      'RHO': 1  },
            'M10P'     :   {'TDK': 0,        'RHO': 0   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': 1,        'RHO': 1   }, 
            'Kahuna'   :   {'TDK': 1,        'RHO': 1   },             
            'Megalodon':   {'TDK': 1,        'RHO': 1   }, 
            'Kinta':   {'TDK': 1,      'RHO': 1  },
            'M10P'     :   {'TDK': 0,        'RHO': 0   },
         },
      },

      'MODIFIED_SLOPE_USL' : {
         "WRITER_HEATER": {
            'Grenada'  :   {'TDK': 0.630,    'RHO': 0.630  },
            'Kahuna'   :   {'TDK': 1.000,    'RHO': 1.000  },            
            'Megalodon':   {'TDK': 0.15,     'RHO': 0.15  },
            'Kinta':   {'TDK': -0.127,      'RHO': -0.127  },
            'M10P'     :   {'TDK': 1.000,    'RHO': 1.000  },
         },
         "READER_HEATER": {
            'Grenada'  :   {'TDK': 0.460,    'RHO': 0.460  },
            'Kahuna'   :   {'TDK': 1.000,    'RHO': 1.000  },            
            'Megalodon':   {'TDK': -0.05,    'RHO': -0.05  },
            'Kinta':   {'TDK': -0.127,      'RHO': -0.127  },
            'M10P'     :   {'TDK': 1.000,    'RHO': 1.000  },
         },
      },
      'MODIFIED_SLOPE_LSL'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': -0.63,    'RHO': -0.63   },
            'Kahuna'   :   {'TDK': -1.000,    'RHO': -1.000   },              
            'Megalodon':   {'TDK': -0.1,     'RHO': -0.1   }, 
            'Kinta':   {'TDK': -1.016,      'RHO': -1.016  },
            'M10P'     :   {'TDK': -1.000,   'RHO': -1.000  },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': -0.8,     'RHO': -0.8   },
            'Kahuna'   :   {'TDK': -1.000,     'RHO': -1.000  },              
            'Megalodon':   {'TDK': -0.4,     'RHO': -0.4   }, 
            'Kinta':   {'TDK': -1.016,      'RHO': -1.016 },
            'M10P'     :   {'TDK': -1.000,   'RHO': -1.000 },
         },
      },




      # the following was auto-generated from the original python code.

      # cold slope adder params

      'dTc'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 0.0,      'RHO': 0.0   },
            'Kahuna'   :   {'TDK': 0.0,      'RHO': 0.0   },  
            'Megalodon':   {'TDK': 0.0,      'RHO': 0.0   }, 
            'Kinta':   {'TDK': -0.033528,      'RHO': 0 },
            'M10P'     :   {'TDK': 0.0,      'RHO': 0.0   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': 0.0,      'RHO': 0.0   }, 
            'Kahuna'   :   {'TDK': 0.0,      'RHO': 0.0   }, 
            'Megalodon':   {'TDK': 0.0,      'RHO': 0.0   }, 
            'Kinta':   {'TDK': -0.033528,      'RHO': 0.254  },
            'M10P'     :   {'TDK': 0.0,      'RHO': 0.0   },
         },
      },
      'COLD_TEMP_DTC'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 28,       'RHO': 28   }, 
            'Kahuna'   :   {'TDK': 28,       'RHO': 28   },             
            'Megalodon':   {'TDK': 28,       'RHO': 28   }, 
            'Kinta':   {'TDK': 20,      'RHO': 10  },
            'M10P'     :   {'TDK': 0,       'RHO':  0    },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': 28,       'RHO': 28   }, 
            'Kahuna'   :   {'TDK': 28,       'RHO': 28   },             
            'Megalodon':   {'TDK': 28,       'RHO': 28   }, 
            'Kinta':   {'TDK': 20,      'RHO': 10  },
            'M10P'     :   {'TDK': 0,       'RHO':  0    },
         },
      },

      'COLD_dTc_MAX'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 0.2,      'RHO': 0.2   }, 
            'Kahuna'   :   {'TDK': 0.2,      'RHO': 0.2   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': 0.0,      'RHO': 0.0   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kahuna'   :   {'TDK': "Nan",    'RHO': "Nan"   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': "Nan",    'RHO': "Nan"   },
         },
      },

      'COLD_dTc_MIN'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': -0.2,     'RHO': -0.2   }, 
            'Kahuna'   :   {'TDK': -0.2,     'RHO': -0.2   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK':  0.0,     'RHO':  0.0   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kahuna'   :   {'TDK': "Nan",    'RHO': "Nan"   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan" },
            'M10P'     :   {'TDK': "Nan",    'RHO': "Nan"   },
         },
      },

      # hot slope adder

      'dTh'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 0.0,      'RHO': 0.0   }, 
            'Kahuna'   :   {'TDK': 0.0,      'RHO': 0.0   },             
            'Megalodon':   {'TDK': 0.0,      'RHO': 0.0   }, 
            'Kinta':   {'TDK': -0.3683,      'RHO': -0.252476  },
            'M10P'     :   {'TDK': 0.0,      'RHO': 0.0   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': 0.0,      'RHO': 0.0   }, 
            'Kahuna'   :   {'TDK': 0.0,      'RHO': 0.0   },             
            'Megalodon':   {'TDK': 0.0,      'RHO': 0.0   }, 
            'Kinta':   {'TDK': -0.3683,      'RHO': -0.508 },
            'M10P'     :   {'TDK': 0.0,      'RHO': 0.0   },
         },
      },
      'HOT_TEMP_DTH'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 60,       'RHO': 60   }, 
            'Kahuna'   :   {'TDK': 60,       'RHO': 60   },             
            'Megalodon':   {'TDK': 60,       'RHO': 60   }, 
            'Kinta':   {'TDK': 48,      'RHO': 55  },
            'M10P'     :   {'TDK': 65,       'RHO': 65   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': 60,       'RHO': 60   }, 
            'Kahuna'   :   {'TDK': 60,       'RHO': 60   },             
            'Megalodon':   {'TDK': 60,       'RHO': 60   }, 
            'Kinta':   {'TDK': 48,      'RHO': 55  },
            'M10P'     :   {'TDK': 65,       'RHO': 65   },
         },
      },

      'HOT_dTh_MAX'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 0.1,      'RHO': 0.1   }, 
            'Kahuna'   :   {'TDK': 0.1,      'RHO': 0.1   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': 0.0,      'RHO': 0.0   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kahuna'   :   {'TDK': "Nan",    'RHO': "Nan"   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': "Nan",    'RHO': "Nan"   },
         },
      },

      'HOT_dTh_MIN'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': -0.1,     'RHO': -0.1   }, 
            'Kahuna'   :   {'TDK': -0.1,     'RHO': -0.1   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK':  0.0,     'RHO':  0.0   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kahuna'   :   {'TDK': "Nan",    'RHO': "Nan"   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': "Nan",    'RHO': "Nan"   },
         },
      },


      # HMS margin HOT specs

      'HMSMarginThreshold_Hot'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 1.2,      'RHO': 1.2   }, 
            'Kahuna'   :   {'TDK': 1.2,      'RHO': 1.2   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': 1.2,      'RHO': 1.2   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kahuna'   :   {'TDK': "Nan",    'RHO': "Nan"   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': "Nan",    'RHO': "Nan"   },
         },
      },
      'HMSMargin_Hot_Temp'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 75.0,     'RHO': 75.0   }, 
            'Kahuna'   :   {'TDK': 75.0,     'RHO': 75.0   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': 75.0,     'RHO': 75.0   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kahuna'   :   {'TDK': "Nan",    'RHO': "Nan"   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': "Nan",    'RHO': "Nan"   },
         },
      },
      'HMSMarginSafe_Hot'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 2.5,      'RHO': 2.5   }, 
            'Kahuna'   :   {'TDK': 2.5,      'RHO': 2.5   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'       : {'TDK': 2.5, 'RHO': 2.5 },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kahuna'   :   {'TDK': "Nan",    'RHO': "Nan"   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'       : {'TDK': "Nan", 'RHO': "Nan" },
         },
      },

      # HMS margin COLD specs

      'HMSMarginThreshold_Cold'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 1.2,      'RHO': 1.2   }, 
            'Kahuna'   :   {'TDK': 1.2,      'RHO': 1.2   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': 1.2,      'RHO': 1.2   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kahuna'   :   {'TDK': "Nan",    'RHO': "Nan"   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': "Nan",    'RHO': "Nan"   },
         },
      },

      'HMSMargin_Cold_Temp'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 0.0,      'RHO': 0.0   }, 
            'Kahuna'   :   {'TDK': 0.0,      'RHO': 0.0   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': 0.0,      'RHO': 0.0   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kahuna'   :   {'TDK': "Nan",    'RHO': "Nan"   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'     :   {'TDK': "Nan",    'RHO': "Nan"   },
         },
      },

      'HMSMarginSafe_Cold'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 1.5,      'RHO': 1.5   }, 
            'Kahuna'   :   {'TDK': 1.5,      'RHO': 1.5   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan"  },
            'M10P'       : {'TDK': 1.5, 'RHO': 1.5 },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kahuna'   :   {'TDK': "Nan",    'RHO': "Nan"   },             
            'Megalodon':   {'TDK': "Nan",    'RHO': "Nan"   }, 
            'Kinta':   {'TDK': "Nan",      'RHO': "Nan" },
            'M10P'     :   {'TDK': "Nan",    'RHO': "Nan"   },
         },
      },





      # TCC2
      'TCS2' : {
         "WRITER_HEATER": {
            'Grenada'  :   {'TDK': 0.0,      'RHO': 0.0  },
            'Kahuna'   :   {'TDK': 0.0,      'RHO': 0.0  },            
            'Megalodon':   {'TDK': 0.0,      'RHO': 0.0  },
            'Kinta':   {'TDK': 0.0,      'RHO': 0.0  },
            'M10P'     :   {'TDK': 0.0,      'RHO': 0.0  },
         },
         "READER_HEATER": {
            'Grenada'  :   {'TDK': 0.0,      'RHO': 0.0  },
            'Kahuna'   :   {'TDK': 0.0,      'RHO': 0.0  },            
            'Megalodon':   {'TDK': 0.0,      'RHO': 0.0  },
            'Kinta':   {'TDK': 0.0,      'RHO': 0.0 },
            'M10P'     :   {'TDK': 0.0,      'RHO': 0.0  },
         },
      },
      'TCS2_LSL'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': -1.0,     'RHO': -1.0   }, 
            'Kahuna'   :   {'TDK': -1.0,     'RHO': -1.0   },             
            'Megalodon':   {'TDK': -1.0,     'RHO': -1.0   }, 
            'Kinta':   {'TDK': -1.0,      'RHO': -1.0  },
            'M10P'     :   {'TDK': -1.0,     'RHO': -1.0   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': -1.0,     'RHO': -1.0   }, 
            'Kahuna'   :   {'TDK': -1.0,     'RHO': -1.0   },              
            'Megalodon':   {'TDK': -1.0,     'RHO': -1.0   },
            'Kinta':   {'TDK': -1.0,      'RHO': -1.0  },
            'M10P'     :   {'TDK': -1.0,     'RHO': -1.0   },
         },
      },
      'TCS2_USL'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': 1.0,      'RHO': 1.0   }, 
            'Kahuna'   :   {'TDK': 1.0,      'RHO': 1.0   },             
            'Megalodon':   {'TDK': 1.0,      'RHO': 1.0   }, 
            'Kinta':   {'TDK': 1.0,      'RHO': 1.0  },
            'M10P'     :   {'TDK': 1.0,      'RHO': 1.0   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': 1.0,      'RHO': 1.0   }, 
            'Kahuna'   :   {'TDK': 1.0,      'RHO': 1.0   },             
            'Megalodon':   {'TDK': 1.0,      'RHO': 1.0   }, 
            'Kinta':   {'TDK': 1.0,      'RHO': 1.0  },
            'M10P'     :   {'TDK': 1.0,      'RHO': 1.0   },
         },
      },

      'clearanceDataType'  : {  
         'WRITER_HEATER'  : {  
            'Grenada'  :   {'TDK': "Write Clearance",     'RHO': "Write Clearance"   }, 
            'Kahuna'   :   {'TDK': "Write Clearance",     'RHO': "Write Clearance"   },             
            'Megalodon':   {'TDK': "Write Clearance",     'RHO': "Write Clearance"   }, 
            'Kinta':   {'TDK': "Write Clearance" ,      'RHO': "Write Clearance"  },
            'M10P'     :   {'TDK': "Write Clearance",     'RHO': "Write Clearance"   },
         },
         'READER_HEATER'  : {  
            'Grenada'  :   {'TDK': "Read Clearance",     'RHO': "Read Clearance"   }, 
            'Kahuna'   :   {'TDK': "Read Clearance",     'RHO': "Read Clearance"   },             
            'Megalodon':   {'TDK': "Read Clearance",     'RHO': "Read Clearance"   }, 
            'Kinta':   {'TDK': "Read Clearance",      'RHO': "Read Clearance"  },
            'M10P'     :   {'TDK': "Read Clearance",     'RHO': "Read Clearance"   },
         },
      },


   }


   tcc_DH_values = {}
   tcc_DH_values["WRITER_HEATER"] = {}
   tcc_DH_values["READER_HEATER"] = {}

   if programName in []:
      from TestParamExtractor import TP
      tcc_DH_values = TP.tcc_DH_values
   else:
      # simple swapping of order
      for htr in [ "WRITER_HEATER", "READER_HEATER" ]:
         for parm in tcsInternalValuesDict:
            tcc_DH_values[htr][parm] = tcsInternalValuesDict[parm][htr][programName][headType]
   #
   

   return tcc_DH_values

   # end of getTCS_values

  

