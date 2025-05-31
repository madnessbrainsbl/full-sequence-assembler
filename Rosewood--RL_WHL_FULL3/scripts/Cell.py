#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: The Cell class is an abstraction of the actual cell where the drive resides during test
#              This class handles all operations pertaining to the cell such as baudrate, power etc.
#              NOTE: Only one instance of the cell must exist in the script environment
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/07/31 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Cell.py $
# $Revision: #3 $
# $DateTime: 2016/07/31 21:26:43 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Cell.py#3 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
from Constants import  *
import time,types
import ScrCmds
from Rim import objRimType
import MessageHandler as objMsg
from Exceptions import CReplugForTempMove

import sptCmds
from UartCls import theUart
from Drive import objDut
import traceback

###########################################################################################################
###########################################################################################################
class CCell:
   #----------------------------------------------------------------------------
   def __init__(self, baud=DEF_BAUD):
      self.eslipMode = 0
      self.dynamicRimType = 0
      self.prmType = 'NAMED'

   def initCell(self):
      self.setBaud(DEF_BAUD)

   #----------------------------------------------------------------------------
   def enableDynamicRimType(self):

      #ALLOW_TEMP_MOVE is the siteconfig setting which must be turn on for DRT to be set to 1. If zero, no need to check the subsequent condition
      if testSwitch.virtualRun:
         Allow_Temp_Move = 0
      else:
         Allow_Temp_Move = RequestService('GetSiteconfigSetting','ALLOW_TEMP_MOVE')[1].get('ALLOW_TEMP_MOVE',0)
      if not Allow_Temp_Move:
         self.dynamicRimType = 0
         ConfigVars[CN]['DYNAMIC_RIM_TYPE'] = 0
         objMsg.printMsg("Dynamic RIM_TYPE Disabled (Host Setting - ALLOW_TEMP_MOVE): %s" % (self.dynamicRimType,))
         return

      if objRimType.SerialOnlyRiser():
         ConfigVars[CN]['DYNAMIC_RIM_TYPE'] = ConfigVars[CN].get('DYNAMIC_RIM_TYPE',0)
      elif not objRimType.SingleDensityRiser():
         ConfigVars[CN]['DYNAMIC_RIM_TYPE'] = ConfigVars[CN].get('DRT_IO',0)
      else:
         ConfigVars[CN]['DYNAMIC_RIM_TYPE'] = 0

      if ConfigVars[CN].get('DYNAMIC_RIM_TYPE',0):
         self.dynamicRimType = 1
      else:
         self.dynamicRimType = 0

      # NO_IO requirement:
      # PRE2-FNC2: controlled by ConfigVars[CN]['DYNAMIC_RIM_TYPE']
      # CRT2-FIN2: controlled by ConfigVars[CN]['DRT_IO',0]
      if testSwitch.NoIO:
         if (objDut.nextOper in ['CRT2','MQM2','FIN2']):
            if ConfigVars[CN].get('DRT_IO',0):
               self.dynamicRimType = 1
            else:
               self.dynamicRimType = 0

      #In Neptune 2, which is single cell environment, no need DRT.
      if objRimType.isNeptuneRiser() or objRimType.IsPSTRRiser():
         objMsg.printMsg("Dynamic Rim Type disabled for Neptune and PSTR.")
         ConfigVars[CN]['DYNAMIC_RIM_TYPE'] = 0
         self.dynamicRimType = 0

      objMsg.printMsg("Dynamic RIM_TYPE Enable : %s" % (self.dynamicRimType,))

   #----------------------------------------------------------------------------
   def enableESlip(self, sendESLIPCmd = True ):
      """
      Sets ESLIP communication on Cell
      This function MUST be called before power is turned on.
      """
      if sendESLIPCmd:
         sptCmds.enableESLIP(retries = 0, timeout = 1, printResult = False)


      self.eslipMode = 1
      UseESlip()
      UseHardSRQ(0)
      objDut.eslipMode = 1
      TraceMessage('*** ESLIP is ENABLED ***')

   #----------------------------------------------------------------------------
   def disableESlip(self):
      """
      Sets ESLIP communication on Cell
      This function MUST be called before power is turned on.
      """
      self.eslipMode = 0
      UseESlip(0)
      UseHardSRQ(0)
      objDut.eslipMode = 0
      TraceMessage('*** ESLIP is DISABLED ***')

   #----------------------------------------------------------------------------
   def UseHardSRQ(self, enable = 0):
      if not objRimType.CPCRiser(): #UseHardSRQ not supported in CPC Cells
         if enable == 0:
            srqMode = "SOFT"
         else:
            srqMode = "HARD"
         objMsg.printMsg(20*'*' + "SETTING %s SRQ ONLY" % srqMode + 20*'*', objMsg.CMessLvl.DEBUG)

         UseHardSRQ(enable)
   #----------------------------------------------------------------------------
   def setBaud(self, baud=DEF_BAUD):
      return theUart.setBaud(baud)

   #----------------------------------------------------------------------------
   def getBaud(self):
      """
      Returns the current baud rate of the cell
      """
      return theUart.getBaud()

   #----------------------------------------------------------------------------
   def powerOn(self, set5V=5000, set12V=12000, pauseTime=10):
      """
      Powers on the Cell
      """
      if objRimType.CPCRiser() or objRimType.IOInitRiser():
         DriveOn(set5V, set12V, pauseTime=pauseTime, upperLimit5V=MAX_5V, lowerLimit5V=MIN_5V)                    # turn on cell power
      else:
         DriveOn(set5V, set12V, pauseTime=pauseTime)
      CellLed(1)                  # turn on the green cell LED

   #----------------------------------------------------------------------------
   def powerOff(self,pauseTime=10):
      """
      Powers off the Cell
      """
      DriveOff(pauseTime)           # turn off cell power and pause in second
      CellLed(0)                  # turn off the green cell LED


   #----------------------------------------------------------------------------
   def setFanSpeed(self,curOper):
      import struct
      import time

      from TestParamExtractor import TP
      driveFanRPM,elecFanRPM = TP.fanSpeed_profile

      if not testSwitch.virtualRun and not testSwitch.winFOF and not objRimType.isNeptuneRiser():
         SetCellFans(driveFanRPM, elecFanRPM)
         time.sleep(0.5)
         tcData = GetTempCtrlData()
         driveRPM,elecRPM = struct.unpack(">2H",tcData[34:38])
         objMsg.printMsg('Drive RPM: %s  Elec RPM: %s' % (driveRPM,elecRPM))

   #----------------------------------------------------------------------------
   def setTemp(self, reqTemp, minTemp, maxTemp, objSeq, objDut, rampMode='wait', nextRimType=''):

      #If PSTR, no need to set temperature
      if objRimType.IsPSTRRiser():
         temp=(ReportTemperature())/10.0
         objMsg.printMsg("PSTR, no need to set temperature,  Cell Temperature: %0.1fC - Temp Set Point:%sC Range %sC-%sC" % (temp,reqTemp,minTemp,maxTemp))
         return

      #Check whether DRT is turn ON/OFF 
      self.enableDynamicRimType()   

      if not objRimType.IsPSTRRiser():
         if riserType in ["MIRKWOOD","SPMIRKWOOD"]:
            SetTemperatureLimits(sleepLimitMultiplier=6) #Required for slow ramping chambers
            SetTemperatureLimits(tempViolationLimit=0)
         if objRimType.IsHDSTRRiser() and testSwitch.FE_0180754_345172_RAMP_TEMP_NOWAIT_HDSTR_SP:
            SetTemperatureLimits(tempViolationLimit=0)
      elif testSwitch.FE_0251909_480505_NEW_TEMP_PROFILE_FOR_ROOM_TEMP_PRE2 and objRimType.IsPSTRRiser():
         SetTemperatureLimits(sleepLimitMultiplier=10) #Required for slow ramping chambers
         SetTemperatureLimits(tempViolationLimit=0)
      # Now Serial Test uses 'wait' mode and IO Test uses 'nowait' mode
      #if testSwitch.virtualRun == 1:
      #   return

      if rampMode.lower() == 'wait':
         rampWait = 1
      elif rampMode.lower() == 'nowait':
         rampWait = 0
      else:
         errorMsg = "Invalid rampMode %s" % (str(rampMode),)
         objMsg.printMsg(errorMsg)
         ScrCmds.raiseException(11044, errorMsg)

      temp=(ReportTemperature())/10.0
      objMsg.printMsg("Before Ramping, Cell Temperature: %0.1fC - Temp Set Point:%sC Range %sC-%sC  Ramp Wait:%s" % (temp,reqTemp,minTemp,maxTemp,rampWait))

      # Set DRT before ramping
      if self.dynamicRimType and testSwitch.BF_233858_402984_FIX_IO_DYNAMIC_RIM_TYPE:
         if temp >= minTemp and temp <= maxTemp:
            self.setCellRimType(nextRimType,reqTemp, setRimType=1)                 # Force set dynamic rim type name if both trays running the same temp.
         else:
            self.setCellRimType(nextRimType,reqTemp, setRimType=0)                 # Try change rim type if adjacent tray is empty

      if not objRimType.IsPSTRRiser() or testSwitch.FE_0251909_480505_NEW_TEMP_PROFILE_FOR_ROOM_TEMP_PRE2:
         move = self.setTemperatureWithMove(reqTemp, nextRimType, objSeq, objDut, wait=rampWait)
         if move:
            # Check if number of moves exceed allowable limit
            DriveAttributes['DRT_MOVECOUNT'] = int(DriveAttributes['DRT_MOVECOUNT']) + 1
            moveLimit = ConfigVars[CN].get('DRT_MAX_COUNT', 5)
            objMsg.printMsg('Prepare to move to another slot for testing. Attempt %s of %s.' %(DriveAttributes['DRT_MOVECOUNT'],moveLimit))
            if DriveAttributes['DRT_MOVECOUNT'] >= moveLimit:
               objMsg.printMsg('Exceeded maximum number of allowable DRT moves.')
               objMsg.printMsg('Resetting MTS move count.')
               DriveAttributes['DRT_MOVECOUNT'] = 0
               RequestService('SetOperation',("*%s" % objDut.nextOper,))                      # Send unyielded oper failure
               ScrCmds.raiseException(11044)
            #failureData = (10606, nextRimType)
            failureData = ()
            raise CReplugForTempMove(failureData)


      temp=(ReportTemperature())/10.0
      objMsg.printMsg("After Ramping,  Cell Temperature: %0.1fC - Temp Set Point:%sC Range %sC-%sC  Ramp Wait:%s" % (temp,reqTemp,minTemp,maxTemp,rampWait))
      DriveAttributes['DRT_MOVECOUNT'] = 0

      if rampWait:
         for loop in range(30):
            if (temp >= minTemp) and (temp <= maxTemp):
               break

            ScriptPause(60)
            temp=(ReportTemperature())/10.0
            objMsg.printMsg("Loop Count:%02d,  Cell Temperature: %0.1fC - Temp Set Point:%sC Range %sC-%sC  Ramp Wait:%s" % (loop+1,temp,reqTemp,minTemp,maxTemp,rampWait))

         if testSwitch.WA_0256539_480505_SKDC_M10P_BRING_UP_DEBUG_OPTION:
            for loop in range(200):
               if (temp >= minTemp) and (temp <= maxTemp):
                  break

               ScriptPause(180)
               temp=(ReportTemperature())/10.0
               objMsg.printMsg("Loop Count:%02d,  Cell Temperature: %0.1fC - Temp Set Point:%sC Range %sC-%sC  Ramp Wait:%s" % (loop+1,temp,reqTemp,minTemp,maxTemp,rampWait))

         # ---- Checks that cell temp is within allowable range ----
         if temp < minTemp:
            errorMsg = "Current Cell Temperature %0.1fC is less than MIN TEMP %sC" % (temp, str(minTemp))
            objMsg.printMsg(errorMsg)
            ScrCmds.raiseException(10606, errorMsg)

         if temp > maxTemp:
            errorMsg = "Current Cell Temperature %0.1fC is greater than MAX TEMP %sC" % (temp, str(maxTemp))
            objMsg.printMsg(errorMsg)
            ScrCmds.raiseException(10605, errorMsg)

      if self.dynamicRimType:
         self.setCellRimType(nextRimType,reqTemp)

   #----------------------------------------------------------------------------
   def askHostForTwoMove(self, nextRimType=None, ambivalent=0):
      """
      Desc: Execute Host Request 'AllowTwoMove' - Check whether there is available slot to move to
         nextRimType='XX' : Use the rim type of 52C
         ambivalent=0     : Ask Host whether drive can be moved
         ambivalent=1     : Ask Host whether drive should be moved (when there is many idle slots)
      """

      drive_rim_type = DriveAttributes['RIM_TYPE']
      if nextRimType:
         drive_rim_type = nextRimType

      if testSwitch.BF_233858_402984_FIX_IO_DYNAMIC_RIM_TYPE:
         stat = RequestService('AllowTwoMove',(ambivalent, drive_rim_type))
         allowMove,idleSlots = stat[1]
         ScrCmds.insertHeader('Request Idle Slot %s' %drive_rim_type, length=60)
         ScriptComment("%-15s -> %s" % ('ambivalentFlag', ambivalent))
         ScriptComment("%-15s -> %s" % ('idleSlots', idleSlots))
         ScriptComment("%-15s -> %s" % ('allowMove', allowMove))
         return stat

      else:
         objMsg.printMsg("RequestService - AllowTwoMove")
         # ambivalent, new_drv_rim_type (Host want me to move?)
         stat = RequestService('AllowTwoMove',(ambivalent,drive_rim_type))
         objMsg.printMsg("AllowTwoMove, stat = %s" % `stat`)
         return stat


   #----------------------------------------------------------------------------
   def setTemperatureWithMove(self, reqTemp, nextRimType, objSeq, objDut, wait=1):
      """
      Only Double Density Cell has Temp Sharing Issue, Single Density Cell should not block the temp ramping.
      Single Density Cell does not require status check
      """
      move_result    = 0
      RAMP_TEMP_FAIL = -1

      if testSwitch.BF_233858_402984_FIX_IO_DYNAMIC_RIM_TYPE and self.dynamicRimType and not objRimType.isNeptuneRiser():
         pass

      # Single density cell or cell with temperature control for each tray. Ex. Neptune
      elif not objRimType.SerialOnlyRiser():
         if wait:
            startRamp = time.time()
            stat = RampToTempWithWait(reqTemp*10)#self.setTemperatureWithWait(reqTemp)
            endRamp = time.time()
            rampTime = endRamp - startRamp
            self.temperatureRampTime(rampTime)
            self.addRampTimeTable(rampTime, objSeq, objDut)
         else:
            stat = RampToTempNoWait(  reqTemp*10)
         return move_result

      while 1:
         # ambivalent=1 - Function will not block if this cell can't ramp
         if wait:
            startRamp = time.time()
            stat = RampToTempWithWait(reqTemp*10,1,ambivalent=self.dynamicRimType)
            endRamp = time.time()
            rampTime = endRamp - startRamp
            self.temperatureRampTime(rampTime)
            self.addRampTimeTable(rampTime, objSeq, objDut)
         else:
            stat = RampToTempNoWait(reqTemp*10,1,ambivalent=self.dynamicRimType)

         if (stat != RAMP_TEMP_FAIL) or (not self.dynamicRimType):
            break

         # Ramp Failed and 3TempMove Enabled
         ScrCmds.insertHeader('Heater is locked!',length=60)
         allow_move,idle_slot = self.askHostForTwoMove(nextRimType)[1]
         if allow_move:
            move_result = 1
            break
         # No available slot to move to... then wait and try again
         else:
            ReportStatus('Pause 5min and retry temp ramp')
            objMsg.printMsg('Pause for 5min and then retry')
            ScriptPause(5*60)

      return move_result

   def temperatureRampTime(self, rampTime):
      """
      Show ramp time in hh:mm:ss format
      """
      m, s = divmod(rampTime, 60)
      h, m = divmod(m, 60)
      objMsg.printMsg("Temperature Ramp Time %d:%02d:%02d." %(h, m, s))

   #----------------------------------------------------------------------------
   def setCellRimType(self, nextRimType, reqTemp, forceSet=0, setRimType=1):
      """
      Sets cell rim type name.
      Where:
         nextRimType = Requested rim type
         reqTemp     = Cell temperature setting
         setRimType  = Dynamic force set rim type
      """

      if self.dynamicRimType or forceSet:
         set_result = 0

         drive_rim_type = DriveAttributes.get('RIM_TYPE')
         if nextRimType:
            drive_rim_type = nextRimType

         objMsg.printMsg('drive_rim_type = %s'%str(drive_rim_type))
         stat = RequestService('GetRimType',drive_rim_type)[1]
         objMsg.printMsg('stat = %s'%str(stat))

         if stat[0]:
            objMsg.printMsg("Fail to GetRimType")
            set_result = -1
            return set_result

         curRimTypeName  = stat[1][0]
         driveRimType    = stat[1][1]
         defaultRimType  = stat[1][2]
         dynamicRimType  = stat[1][3]
         fixRimType      = stat[1][4]

         if DEBUG:
            objMsg.printMsg("curRimTypeName = %s" %curRimTypeName)
            objMsg.printMsg("driveRimType = %s" %driveRimType)
            objMsg.printMsg("defaultRimType = %s" %defaultRimType)
            objMsg.printMsg("dynamicRimType = %s" %dynamicRimType)
            objMsg.printMsg("fixRimType = %s" %fixRimType)

         if testSwitch.FE_0134422_336764_GIO_DYNAMIC_RIMTYPE_SUPPORT:
            newRimTypeName = ''
            if (curRimTypeName in defaultRimType):
               newRimTypeName = dynamicRimType[defaultRimType.index(curRimTypeName)]
               if newRimTypeName not in driveRimType:
                  msg = 'Missing Dynamic Rim Type %s in siteconfig.DYNAMIC_RIM_TYPE' % driveRimType
                  ScrCmds.raiseException(14729,msg)

            if newRimTypeName and (newRimTypeName != curRimTypeName):
               stat = RequestService('SetRimType',(newRimTypeName,1))

               if newRimTypeName != stat[1]:
                  objMsg.printMsg("Fail to SetRimType to %s"%(newRimTypeName,) )
                  set_result = -1
               else:
                  objMsg.printMsg("CellType: %s changed to %s" %(curRimTypeName,newRimTypeName) )
            else:
               objMsg.printMsg("CellType: %s "% curRimTypeName )

         elif (curRimTypeName not in driveRimType) or (curRimTypeName in defaultRimType):
#CHOOI-05Dec16 Modify Start
#             if not curRimTypeName.__contains__("_T"):
#                newRimTypeName = curRimTypeName + "_T" + str(reqTemp)
#             else:
#                newRimTypeName = curRimTypeName
# 
#             if DEBUG:
#                objMsg.printMsg("newRimTypeName = %s "%newRimTypeName)

            newRimTypeName = curRimTypeName
            objMsg.printMsg("newRimTypeName = %s "%newRimTypeName)
#CHOOI-05Dec16 Modify End

            if not ((newRimTypeName in dynamicRimType) and (newRimTypeName in driveRimType)):
               ScrCmds.raiseException(14729, 'Missing Dynamic Rim Type %s in siteconfig.DYNAMIC_RIM_TYPE.' % newRimTypeName)

            if newRimTypeName != curRimTypeName:
               stat = RequestService('SetRimType',(newRimTypeName,setRimType))        # Dynamic force set rim type

               if newRimTypeName != stat[1]:
                  objMsg.printMsg("Fail to SetRimType to %s"%(newRimTypeName,) )
                  set_result = -1
               else:
                  objMsg.printMsg("CellType: %s changed to %s" %(curRimTypeName,newRimTypeName) )
            else:
               objMsg.printMsg("CellType: %s "% curRimTypeName )
         return set_result


   def resetCellRimType(self, ):
      """
      Reset Cell RIM_TYPE to default RIM_TYPE
      """
      self.enableDynamicRimType()   
      if self.dynamicRimType:
         try:
            set_result = 0

            drive_rim_type = DriveAttributes.get('RIM_TYPE','NONE')
            stat = RequestService('GetRimType',drive_rim_type)[1]
            objMsg.printMsg('stat = %s'%str(stat))
            if stat[0]:
               objMsg.printMsg("Fail to GetRimType")
               set_result = -1
               return set_result

            cellRimType    = stat[1][0]
            driveRimType   = stat[1][1]
            defaultRimType = stat[1][2]
            dynamicRimType = stat[1][3]
            fixRimType     = stat[1][4]

            if DEBUG:
               objMsg.printMsg("cellRimType = %s" %cellRimType)
               objMsg.printMsg("driveRimType = %s" %driveRimType)
               objMsg.printMsg("defaultRimType = %s" %defaultRimType)
               objMsg.printMsg("dynamicRimType = %s" %dynamicRimType)
               objMsg.printMsg("fixRimType = %s" %fixRimType)

            # CURRENT_CELL_RIM_TYPE is DYNAMIC_RIM_TYPE
            if (cellRimType in dynamicRimType):
               newRimType = ''

               if cellRimType.__contains__("_T"):
                  newRimType = cellRimType.split("_T")[0]
               else:
                  for rimType in defaultRimType:
                     if rimType in driveRimType:
                        newRimType = rimType
                        break

               if newRimType and (newRimType != cellRimType):
                  # Prevent changing cell rim types to other cell types (i.e P4CPC1_T46 to DMSATAM)
                  if (objRimType.CPCRiser(ReportReal=True) and newRimType in objRimType.CPCRiserList()) or \
                     (objRimType.IOInitRiser() and newRimType in objRimType.IOInitRiserList()) or \
                     (objRimType.SerialOnlyRiser() and newRimType in objRimType.SerialOnlyRiserList()):

                     # Set Default RIM_TYPE if no drive testing in another slot
                     for retry in xrange(2):
                        stat = RequestService('SetRimType',(newRimType,0))
                        if newRimType == stat[1]:
                           objMsg.printMsg("CellType: %s changed to %s" %(cellRimType,newRimType) )
                           break
                        time.sleep(120)   # wait for 2 min before retry
                     else:
                        objMsg.printMsg("Fail to SetRimType to %s"%(newRimType,) )
                        set_result = -1
                  else:
                     objMsg.printMsg("CellType: %s not allowed to change to %s" %(cellRimType,newRimType) )

         except:
            objMsg.printMsg("Exception to resetCellRimType")
            objMsg.printMsg("Traceback %s" %traceback.format_exc())
            set_result = -2
         return set_result

   #------------------------------------------------------------------------------------------------------#
   def addRampTimeTable(self, rampTime, objSeq, objDut):
      ######################## DBLOG Implementation- Setup
      curSeq,occurrence,testSeqEvent = objSeq.registerCurrentTest(0)
      rampTime = ('%3.2f' % rampTime)
      ######################## DBLOG Implementation- Closure

      objDut.dblData.Tables('TEST_TIME_BY_TEST').addRecord(
         {
         'SPC_ID': 0,
         'OCCURRENCE': occurrence,
         'SEQ':curSeq,
         'TEST_SEQ_EVENT': testSeqEvent,
         'TEST_NUMBER': 0,
         'ELAPSED_TIME': rampTime,
         'PARAMETER_NAME':'TEMP_RAMP_TIME',
         })

###########################################################################################################
###########################################################################################################
theCell = CCell() # create carrier instance,power on cell/carrier
TraceMessage('Cell Instance Created %d' % PortIndex)
