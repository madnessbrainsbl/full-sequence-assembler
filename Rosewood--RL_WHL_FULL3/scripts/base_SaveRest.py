#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: base Serial Port calibration states
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SaveRest.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_SaveRest.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
if testSwitch.FE_0134030_347506_SAVE_AND_RESTORE:
   
   from Constants import *
   from State import CState
   import MessageHandler as objMsg


   #----------------------------------------------------------------------------------------------------------
   class CLoop(CState):
      """
         Description: Class that will provide state looping capability.  Once the loop is complete, the FAIL transition will be executed
         Base:
         Usage: Should be run only if you want to loop on a state(s)
         Params:  Number of loops to execute

      """
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         self.loopCountLimit = self.params.get('LOOPS', 0)
         depList = []
         CState.__init__(self, dut, depList)


      #-------------------------------------------------------------------------------------------------------
      def dependencies(self, oper, state):
         TraceMessage( '--- Dependency Check Oper - %s --- State - %s ---' % (oper, state) )
         #
         #  Checking Dependency variables of classes that must run prior to this class running
         #  This overrides the CSTATE dependencies method.  This is needed to be able to transition out of the loop

         self.dut.stateData[state] = 1 # set dep flag indicating that this class has been run
         for dep in self.depList:
            if self.dut.stateData.get(dep,0) == 0:
               import ScrCmds
               ScrCmds.raiseException(13403, "State dependency failure.")

         self.dut.stateLoopCounter[self.dut.currentState] = self.dut.stateLoopCounter.setdefault(self.dut.currentState,0) + 1

         self.dut.stateTransitionEvent = 'pass'
         if self.dut.stateLoopCounter[self.dut.currentState] > self.loopCountLimit:
            self.dut.stateTransitionEvent = 'fail'

      #-------------------------------------------------------------------------------------------------------
      def run(self):
         objMsg.printMsg("LOOP COUNTER")

         #increment the counter
         self.dut.stateLoopCounter[self.dut.currentState] = self.dut.stateLoopCounter.setdefault(self.dut.currentState,0) + 1

         objMsg.printMsg("Number of times this state has been entered:   %d " % self.dut.stateLoopCounter[self.dut.currentState])
         objMsg.printMsg("Number of times allowed to enter this state:  %d" % self.loopCountLimit)

         #check if loop is complete
         if self.dut.stateLoopCounter[self.dut.currentState] > self.loopCountLimit:
            import ScrCmds
            objMsg.printMsg("The loop limit HAS been exceeded -- moving on to the FAIL transition in the state table")
            ScrCmds.raiseException(11044,"Operation Loop Limit Exceeded")
         else:
            objMsg.printMsg("The loop limit HAS NOT been exceeded -- moving on to the PASS transition in the state table")

   #-------------------------------------------------------------------------------------------------------------
   class CRestoreDriveState(CState):
      """
         Description: Class that will set the drive to a restore point that was obtained from a previous process run
         Params:  Restore key name
      """
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)

         self.restoreStateName     = self.params.get('STATE_NAME', None)
         self.baseline             = self.params.get('BASELINE', self.dut.sbr)
         self.operName             = self.params.get('OPERATION', self.dut.nextOper)
         self.fileNameBase         = self.params.get('FILENAME_BASE', None)

      #-------------------------------------------------------------------------------------------------------
      def run(self):
         from SaveAndRestore import CSetRestorePoint
         oRestore = CSetRestorePoint(self.restoreStateName, self.baseline, self.operName, self.fileNameBase)
         oRestore.run()


#-------------------------------------------------------------------------------------------------------------
   class CSaveDriveState(CState):
      """
         Description: Class that will saves the necessary pieces required to create a restore point
         Params:  Restore key name
      """
      #-------------------------------------------------------------------------------------------------------
      def __init__(self, dut, params={}):
         self.params = params
         depList = []
         CState.__init__(self, dut, depList)
         self.restoreStateName = self.params.get('STATE_NAME', self.dut.lastState)
         self.baseline         = self.params.get('BASELINE', self.dut.sbr)

      #-------------------------------------------------------------------------------------------------------
      def run(self):
         from SaveAndRestore import CCreateRestorePoint
         oSave = CCreateRestorePoint(self.restoreStateName,self.baseline, self.dut.nextOper)
         oSave.run()
