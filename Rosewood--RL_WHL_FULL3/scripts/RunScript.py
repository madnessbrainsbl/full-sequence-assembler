#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Main control script, instantiates carrier, drive, and executes test object
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/RunScript.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/RunScript.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
from Exceptions import CRaiseException,CReplugException,CReplugForTempMove

import traceback
###########################################################################################################
###########################################################################################################
def main():
   '''All exceptions are processed in this module.  Exceptions from State.py are
   re-raised.  This allows for end() in Setup.py to always be the last function called
   for either a PASS or FAIL state, thus insuring that the P_EVENT_SUMMARY table
   is populated.'''
   #------------------------------------------------------------------------------------------------------#
   ReportErrorCode(0) # reset GUI err msg window

   #------------------------------------------------------------------------------------------------------#
   from Setup import CSetup
   objTest = CSetup() # create test object

   if not IsDrivePlugged():
      ReportErrorCode(11045)
      ReportStatus('Drive is NOT plugged in!')
      failureData = ['Drive is NOT plugged in!', 999, 11045]

      holdDriveEC = ConfigVars[CN].get('holdDriveEC',[])
      if 11045 in holdDriveEC:
         ScriptComment('HOLD DRIVE !')
         ReportRestartFlags({'holdDrive':1})
      else:
         ScriptComment('DO NOT HOLD DRIVE !')

      raise ScriptTestFailure, failureData

   else:
      ScriptComment('Drive PLUGGED')
   try:
      try:
         objTest.initializeComponents()
         objTest.setup()
         objTest.execute()
      finally:
         from Cell import theCell
         theCell.resetCellRimType()
         if getattr(objTest, 'genExcept', None) == None:
            objTest.genExcept = traceback.format_exc()

   except (ScriptTestFailure):
      restartFlags = objTest.errHandler('test')

      restartFlags = objTest.setNextOper(restartFlags)  #Add for running SDAT2 in FAIL_SAFE mode
      objTest.end(restartFlags)

      return restartFlags

   except FOFTemperatureRampFailure:
      #Handle early temp ramp failures
      restartFlags = objTest.errHandler('script')

      restartFlags = objTest.setNextOper(restartFlags)  #Add for running SDAT2 in FAIL_SAFE mode
      objTest.end(restartFlags)

      if testSwitch.winFOF == 1: #Add for running SDAT2 in FAIL_SAFE mode
         return restartFlags
   except CReplugException, inst:
      errCode = int(str(inst))

      restartFlags = objTest.forceReplug(errCode)
      objTest.end(restartFlags)

   except CReplugForTempMove,exceptionData:
      # Replug for drives which want to ramp temp in another proper slot
      objTest.replugForTempMove(exceptionData.failureData)
   except CRaiseException,exceptionData:
      objTest.genExcept = traceback.format_exc()
      restartFlags = objTest.errHandler('raise',exceptionData.failureData)

      restartFlags = objTest.setNextOper(restartFlags)  #Add for running SDAT2 in FAIL_SAFE mode
      objTest.end(restartFlags)

      if testSwitch.winFOF == 1: #Add for running SDAT2 in FAIL_SAFE mode
         return restartFlags
   except:
      objTest.genExcept = traceback.format_exc()
      restartFlags = objTest.errHandler('script')

      restartFlags = objTest.setNextOper(restartFlags)  #Add for running SDAT2 in FAIL_SAFE mode
      objTest.end(restartFlags)

      if testSwitch.winFOF == 1: #Add for running SDAT2 in FAIL_SAFE mode
         return restartFlags

   else:
      restartFlags = objTest.setNextOper()
      restartFlags = objTest.end(restartFlags)
      if testSwitch.winFOF == 1:
         return restartFlags

#---------------------------------------------------------------------------------------------------------#
