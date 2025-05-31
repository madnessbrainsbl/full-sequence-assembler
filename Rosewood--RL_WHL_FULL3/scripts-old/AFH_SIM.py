#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: AFH_SIM Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/09/26 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_SIM.py $
# $Revision: #2 $
# $DateTime: 2016/09/26 02:38:55 $
# $Author: yihua.jiang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/AFH_SIM.py#2 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import types, ScrCmds, struct, traceback
from AFH_constants import *
from Base_SIM import baseDataFileComponent, baseDataFrame, baseSIMFile
import MessageHandler as objMsg
from Drive import objDut
from SIM_FSO import objSimArea

import os

DEBUG = 0
if testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION:
   AFH_VAL = 0
   AFH_NAME = 1
   AFH_FORMAT = 2

class CAFH_Frames(object):
   """
      Class to make accessing the frames data easier.
   """
   instance = None

   def __init__(self):
      pass


   def __new__(self, *args, **kargs):
      self.dut = objDut
      if self.instance is None:
         self.instance = object.__new__(self, *args, **kargs)
         # SIM defaults
         from FSO import CFSO
         import os
         self.mFSO = CFSO()
         self.afhSIMName = "AFH_SIM.bin"
         self.afhSIMPath = os.path.join(ScrCmds.getSystemResultsPath(), self.mFSO.getFofFileName(0), self.afhSIMName)
         self.afhSIMFile = None  #Place holder for afhSIM generic results file
         self.dPesSim = CAFH_SIM(1, self.dut.imaxHead, 4, 2)
         self.headList = range(objDut.imaxHead)   # getZoneTable()  # needs to be called prior to the init so that this is valid

      return self.instance

   def __del__(self):
      del self.mFSO
      del self.dPesSim

   def getAFHSIM(self):
      """
      Retrieve the AFH SIM file from the drive.
      @return: Blank Generic Results File if Exception or no file on disc; CM file if successful
      """
      self.afhSIMFile = GenericResultsFile(self.afhSIMName)

      path = self.mFSO.retrieveHDResultsFile(objSimArea['AFH_SIM_FILE'])

      self.afhSIMFile.open('wb')
      try:
         self.afhSIMFile.write(open(path, 'rb').read())
      finally:
         self.afhSIMFile.close()

      return self.afhSIMFile

   def readFramesFromCM_SIM(self, allow_readFramesFromDrive_SIM = 1):
      if type(self.afhSIMFile) == types.NoneType:
         self.afhSIMFile = GenericResultsFile(self.afhSIMName)

      try:
         self.dPesSim.reloadFromDisc(self.afhSIMFile)
      except:
         objMsg.printMsg('readFramesFromCM_SIM/Could not read CM_SIM file.')
         if allow_readFramesFromDrive_SIM == 1:
            try:
               self.readFramesFromDRIVE_SIM()
            except:
               objMsg.printMsg('readFramesFromCM_SIM/Could not read SIM data from either Drive ETF or CM SIM file.')

      self.display_frames()



   def writeFramesToCM_SIM(self,):
      # self.afhSIMFile does not exist
      try:
         self.dPesSim.readAfterWriteSIM(self.afhSIMFile)
      except:
         self.afhSIMFile = GenericResultsFile(self.afhSIMName)
         self.dPesSim.readAfterWriteSIM(self.afhSIMFile)

   def writeFramesToCM_SIM2(self, filePath):
      # self.afhSIMFile does not exist
      self.dPesSim.readAfterWriteSIM(filePath)


   def clearCM_SIM_method(self, clearCM_SIM):
      if clearCM_SIM == 1:
         self.clearFrames()
         self.writeFramesToCM_SIM()

   #######################################################################################################################
   #
   #               Function:  reinitialize_CAFH_SIM
   #
   #        Original Author:  Michael T. Brady
   #
   #            Description:  re-initializes CAFH_SIM class.
   #
   #          Prerrequisite:  To date (03-May-2010) this is only intended to be used in the depop code.
   #
   #                  Input:  None.
   #
   #           Return  Type:  None
   #
   #           Return Value:  None
   #
   #######################################################################################################################
   def reinitialize_CAFH_SIM(self ):
      self.dPesSim = CAFH_SIM(1, self.dut.imaxHead, 4, 2)


   def clearFrames(self,):
      if testSwitch.FE_0239301_336764_P_CLEAR_DPES_FRAME:
         self.dPesSim.Clear_DPES_FRAMES()
      else:
         self.dPesSim.DPES_FRAMES = []   
      self.dPesSim.DPES_HEADER.set('NumFrames', 0)



   def readFramesFromDRIVE_SIM(self,):
      try:
         # reload /var/merlin/pcfiles/AFHFile/14-1-0 -> memory/FRAMES
         if not testSwitch.virtualRun:
            objMsg.printMsg('attempting to reload afh_sim file from disc (/var/merlin/pcfiles/AFHFile/cell_address -> self.dPesSim.DPES_FRAMES)', objMsg.CMessLvl.VERBOSEDEBUG)
            try:
               self.dPesSim.reloadFromDisc(self.getAFHSIM())
            except:
               failureData = traceback.format_exc()
               objMsg.printMsg('readFramesFromDRIVE_SIM/ failureData:%s' % str(failureData), objMsg.CMessLvl.DEBUG)
               objMsg.printMsg('readFramesFromDRIVE_SIM/ Drive failed to successfully recover AFH SIM file', objMsg.CMessLvl.DEBUG)
               try: ec = failureData[0][2]
               except: ec = 0
               objMsg.printMsg('ec: %s' % str(ec), objMsg.CMessLvl.VERBOSEDEBUG)
               ScrCmds.raiseException(14524,"Failed to find valid SIM data from drive system area.  readFramesFromDRIVE_SIM() failed!")

         else:
            objMsg.printMsg("Virtual Execution on... skipping sim reload from disc")
            try:     self.readFramesFromCM_SIM()
            except:  pass
      except ScriptTestFailure:
         objMsg.printMsg("No AFH SIM Found on disc", objMsg.CMessLvl.DEBUG)
         objMsg.printMsg("Default AFH SIM File created: %s" % self.afhSIMName, objMsg.CMessLvl.VERBOSEDEBUG)
         ScrCmds.raiseException(14524,"New SIM data not Allowed")

   def readFromCM_SIMWriteToDRIVE_SIM(self, exec231):
      if self.mFSO.getFileLen(self.afhSIMPath) == 0:
         ScrCmds.raiseException(14524, "AFH SIM File len is 0")
      self.mFSO.saveResultsFileToDrive(1, filePath = self.afhSIMPath, fileSize = 0, fileType = objSimArea['AFH_SIM_FILE'], exec231 = exec231)


   def display_frames(self, forceDisplay = 0):

      if testSwitch.AFH_ENABLE_ANGSTROMS_SCALER_USE_254 == 1:
         angstromsScaler = 1
      else:
         angstromsScaler = 254.0


      if forceDisplay == 2:
         objMsg.printMsg('********************************************** AFH Frames Stack ***************************************************')
      if forceDisplay == 0 :
         self.summaryDisplayFrames()
      elif forceDisplay == 1:
         self.summaryDisplayFrames()
      elif testSwitch.FE_0315250_322482_P_AFH_CM_OVERLOADING:
         self.summaryDisplayFrames()
      else:

         if (testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1):
            objMsg.printMsg("\n\n")
            str0 = "mode state stateIndex PHYS_HD"
            str0 += " Heater_Element LGC_HD Zone Cylinder"

            str0 += " TestPos Temp WH_DAC HO_DAC"
            str0 += "  wrtClr   rdClr    wPTP"
            objMsg.printMsg(str0)
            str0 = "-" * 116
            objMsg.printMsg(str0)
            for frame in self.dPesSim.DPES_FRAMES:
               if not (frame['mode'] in [AR_MODE]):
                  str0 = "%3s   %3s        %3s     %3s" % (frame['mode'], frame['stateName'], frame['stateIndex'], frame['PHYS_HD'])
                  str0 += "  %13s    %3s  %3s %8s" % (framesIndexToHeaterElementName[frame['Heater Element']], frame['LGC_HD'], frame['Zone'], frame['Cylinder'])
                  str0 += "     %3s %4s    %3s    %3s" % (frame['Measurement Number'], frame['dPES Measure Temp'], frame['Write Heat Contact DAC'], frame['Heater Only Contact DAC'])
                  str0 += "  %6.2f  %6.2f  %6.2f" % ( frame['Write Clearance'] * angstromsScaler, frame['Read Clearance'] * angstromsScaler, frame['WrtLoss'] * angstromsScaler )
                  objMsg.printMsg(str0)
            objMsg.printMsg("\n\n")
         else:

            if testSwitch.FE_0117973_341036_AFH_BETTER_FRAMES_DISPLAY_OPTION  == 1:
               objMsg.printMsg("\n\n")
               str0 = "mode state stateIndex PHYS_HD"
               if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
                  str0 += " Heatr Elemnt LGC_HD Zone Cylinder"
               else:
                  str0 += " consChkIndex LGC_HD Zone Cylinder"

               str0 += " TestPos Temp WH_DAC HO_DAC"
               str0 += "     rdClr    wrtClr      wPTP"
               objMsg.printMsg(str0)
               str0 = "-" * 120
               objMsg.printMsg(str0)
               for frame in self.dPesSim.DPES_FRAMES:
                  if not (frame['mode'] in [AR_MODE]):
                     str0 = "%3s   %3s        %3s     %3s" % (frame['mode'], frame['stateName'], frame['stateIndex'], frame['PHYS_HD'])
                     if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
                        str0 += "          %3s    %3s  %3s %8s" % (frame['Heater Element'], frame['LGC_HD'], frame['Zone'], frame['Cylinder'])
                     else:
                        str0 += "          %3s    %3s  %3s %8s" % (frame['consistCheckIndex'], frame['LGC_HD'], frame['Zone'], frame['Cylinder'])
                     str0 += "     %3s %4s    %3s    %3s" % (frame['Measurement Number'], frame['dPES Measure Temp'], frame['Write Heat Contact DAC'], frame['Heater Only Contact DAC'])
                     str0 += "  %0.8s  %0.8s  %0.8s" % ( frame['Read Clearance'], frame['Write Clearance'], frame['WrtLoss'] )
                     objMsg.printMsg(str0)
               objMsg.printMsg("\n\n")

            else:
               for frame in self.dPesSim.DPES_FRAMES:
                  objMsg.printMsg('frame: %s' % str(frame), objMsg.CMessLvl.VERBOSEDEBUG)

      if forceDisplay == 2:
         objMsg.printMsg('*******************************************************************************************************************')

   def summaryDisplayFrames(self, ):
      disp = {}
      if not (testSwitch.FE_0227626_336764_P_REMOVE_SUMMARY_DISP_FRAME_CAL_FOR_LA_CM_REDUCTION or ConfigVars[CN].get('PRODUCTION_MODE',0)) :
         for frame in self.dPesSim.DPES_FRAMES:
            if frame['MODE'] == AFH_MODE:
               iState = int(frame['stateIndex'])
               iHead = int(frame['LGC_HD'])
               if not iState in disp.keys():
                  disp[iState] = []
               if not iHead in disp[iState]:
                  disp[iState].append(iHead)
      objMsg.printMsg('display_frames/num frames from header: %s, len(DPES_FRAMES): %s, state/head summary: %s' % \
         (self.dPesSim.DPES_HEADER.get('NumFrames'), len(self.dPesSim.DPES_FRAMES), disp ))


   def removePreviousStateInformationIfItExists(self, currentState):
      iPos = len(self.dPesSim.DPES_FRAMES) - 1
      while iPos >= 0:
         if self.dPesSim.DPES_FRAMES[iPos]['stateName'] == currentState[-4:]:
            self.dPesSim.DPES_FRAMES.pop(iPos)
         iPos -= 1

      self.dPesSim.DPES_HEADER.set('NumFrames', len(self.dPesSim.DPES_FRAMES))

   def filterFramesDataKeepMaxStateAndMaxConsistencyCheck(self, ):
      # 1. find max state and max Consistency check
      maxState = -10000

      # 2A.) filter non-AFH contact DAC data
      iPos = len(self.dPesSim.DPES_FRAMES) - 1
      while iPos >= 0:
         if (self.dPesSim.DPES_FRAMES[iPos]['mode'] != AFH_MODE_TEST_135_INTERPOLATED_DATA):
            self.dPesSim.DPES_FRAMES.pop(iPos)
         iPos -= 1

      # 2B.) find lastState
      iPos = len(self.dPesSim.DPES_FRAMES) - 1
      lastState = self.dPesSim.DPES_FRAMES[iPos]['stateIndex']


      # filter lastState
      iPos = len(self.dPesSim.DPES_FRAMES) - 1
      while iPos >= 0:
         if (self.dPesSim.DPES_FRAMES[iPos]['stateIndex'] != lastState):
            self.dPesSim.DPES_FRAMES.pop(iPos)
         iPos -= 1


      # 2C.) By head find non-max consistency check
      for iHead in self.headList:
         maxConsCheckIndex = -10000

         iPos = len(self.dPesSim.DPES_FRAMES) - 1
         while iPos >= 0:
            if (self.dPesSim.DPES_FRAMES[iPos]['LGC_HD'] == iHead) and \
               (self.dPesSim.DPES_FRAMES[iPos]['consistCheckIndex'] > maxConsCheckIndex):
               maxConsCheckIndex = self.dPesSim.DPES_FRAMES[iPos]['consistCheckIndex']
            iPos -= 1

         # By head find filter non-max consistency check
         iPos = len(self.dPesSim.DPES_FRAMES) - 1
         while iPos >= 0:
            if (self.dPesSim.DPES_FRAMES[iPos]['LGC_HD'] == iHead) and \
               (self.dPesSim.DPES_FRAMES[iPos]['consistCheckIndex'] < maxConsCheckIndex):
               self.dPesSim.DPES_FRAMES.pop(iPos)
            iPos -= 1

      # set correct header information
      self.dPesSim.DPES_HEADER.set('NumFrames', len(self.dPesSim.DPES_FRAMES))
      # end of filterFramesDataKeepMaxStateAndByHeadMaxConsistencyCheckOnly


   def openFilePtrsForSelfTestToReadSIMFileDirectly(self, ):
      """
      """
      afhSIM2FileName = "AFH_SIM2.bin"
      afhSIM2FilePathName = os.path.join(ScrCmds.getSystemResultsPath(), self.mFSO.getFofFileName(0), afhSIM2FileName)
      afhSIM2filePtr = GenericResultsFile(afhSIM2FileName)

      # 1. readFrames
      self.readFramesFromCM_SIM()

      # 2. filter
      self.filterFramesDataKeepMaxStateAndMaxConsistencyCheck()

      # 2B. set number measurements per head
      self.dPesSim.DPES_HEADER['Measurements Per Head'] = self.dPesSim.DPES_HEADER[ 'NumFrames' ] / len( self.headList )
      objMsg.printMsg("openFilePtrsForSelfTestToReadSIMFileDirectly/ DPES_HEADER['Measurements Per Head'] set to: %s" % ( self.dPesSim.DPES_HEADER['Measurements Per Head'] ) , objMsg.CMessLvl.DEBUG)

      self.display_frames(1)

      # 3. write to 2nd smaller SIM file which is a filtered sub-set of the standard SIM file
      self.writeFramesToCM_SIM2(afhSIM2filePtr)

      # precaution so that this doesn't get saved using writeFramesToCM_SIM()
      self.clearFrames()


      # 4. open the filePath
      if DEBUG == 1:
         objMsg.printMsg("Open file pointer on CM to file: %s" % afhSIM2FilePathName, objMsg.CMessLvl.DEBUG)
      self.mFSO.configFileObj(afhSIM2FilePathName)

      # 5. redirect using 81
      if DEBUG == 1:
         objMsg.printMsg("ReDirect self-test generic file read to open CM file pointer", objMsg.CMessLvl.DEBUG)
      RegisterResultsCallback(self.mFSO.processRequest81, 81, 0) # Re-direct 81 calls, CM specific command



   def closeFilePtrsForSelfTestToReadSIMFileDirectly(self, ):

      #release the interception
      RegisterResultsCallback('', 81,) # Resume normal 81 calls


   def set_AFH_State(self, AFH_State):
      """
      #######################################################################################################################
      #
      #               Function:  set_AFH_State
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  get the new AFH state number based on frames data
      #
      #                          This is now the older method for setting the AFH state based on the number of frames.
      #
      #          Prerrequisite:  frames data should be loaded
      #
      #                  Input:  current AFH State
      #
      #           Return  Type:  Integer
      #
      #           Return Value:  new AFH State number
      #
      #######################################################################################################################

      """
      for iFrame in self.dPesSim.DPES_FRAMES:
         if iFrame['mode'] == AFH_MODE:
            AFH_State = iFrame['stateIndex']
      AFH_State += 1

      objMsg.printMsg("set_AFH_State/ in stateTable state: %s setting AFH_State to %s" % ( self.dut.nextState[-4:], AFH_State ) )

      return AFH_State


   def set_AFH_StateFromStateTableStateName(self, ):
      """
      #######################################################################################################################
      #
      #               Function:  set_AFH_StateFromStateTableStateName
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  get the new AFH state number based on frames data
      #
      #          Prerrequisite:  The AFH SIM file should be on the current CM.
      #
      #                  Input:  None
      #
      #           Return Value:  current AFH State(int)
      #
      #######################################################################################################################

      """

      stateTableName = self.dut.nextState
      try:
         AFH_State = stateTableToAFH_internalStateNumberTranslation[ stateTableName ]
      except:
         objMsg.printMsg('set_AFH_StateFromStateTableStateName/ StateTable state name: |%s| is NOT a valid AFH state.  Please check the spelling against AFH_Constants.py stateTableToAFH_internalStateNumberTranslation.' % ( stateTableName ))
         raise

      objMsg.printMsg("set_AFH_StateFromStateTableStateName/ in stateTable state: %s setting AFH_State to %s" % ( self.dut.nextState[-4:], AFH_State ) )

      return AFH_State

   def getAFHStateList(self,):
      """
      #######################################################################################################################
      #
      #               Function:  getAFHStateList
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  return a list of AFH statesin frames data.
      #
      #          Prerrequisite:  frames data should be loaded
      #
      #                  Input:  None
      #
      #           Return  Type:  list
      #
      #           Return Value:  list of AFH states
      #
      #######################################################################################################################

      """
      stateList = []
      for frame in self.dPesSim.DPES_FRAMES:
         if frame['mode'] == AFH_MODE and not frame['stateIndex'] in stateList:
            stateList.append(frame['stateIndex'])
      return stateList

   def moveAFHStateInfoFromStateX_toStateY( self, stateX_stateIndex, stateX_stateName, stateY_stateIndex, stateY_stateName):
      """
      #######################################################################################################################
      #
      #               Function:  moveAFHStateInfoFromStateX_toStateY
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  move data from one state name and number to another
      #
      #          Prerrequisite:  frames data should be loaded
      #
      #                  Input:  stateX_stateIndex(int), stateX_stateName(str), stateY_stateIndex(int), stateY_stateName(str)
      #
      #           Return  Type:  list
      #
      #           Return Value:  list of AFH states
      #
      #######################################################################################################################

      """

      for frame in self.dPesSim.DPES_FRAMES:
         currentStateIndex = frame[ 'stateIndex' ]
         currentStateName = frame[ 'stateName' ]
         if ( currentStateIndex == stateX_stateIndex ) and ( currentStateName == stateX_stateName ):
            frame[ 'stateIndex' ] = stateY_stateIndex
            frame[ 'stateName' ] = struct.pack( "4s" , stateY_stateName[-4:])

   def removeDepopFrameDataFromCM_SIM(self, burnish_fail_heads = []):
      if type(self.afhSIMFile) == types.NoneType:
         self.afhSIMFile = GenericResultsFile(self.afhSIMName)

      try:
         self.dPesSim.removeDepopFrameData(self.afhSIMFile, burnish_fail_heads = burnish_fail_heads)
         self.writeFramesToCM_SIM()
      except:
         objMsg.printMsg('readFramesFromCM_SIM/Could not modify CM_SIM file.')
         objMsg.printMsg('Creat CM_SIM file.')
         self.writeFramesToCM_SIM()
         self.dPesSim.removeDepopFrameData(self.afhSIMFile, burnish_fail_heads = burnish_fail_heads)
         self.writeFramesToCM_SIM()
         return 1
      return 0

   def getMinimumTemp(self, desiredStateIndex ):
      """
      #######################################################################################################################
      #
      #               Function:  getMinimumTemp
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  Find the minimum temperature for a given state.
      #
      #          Prerrequisite:  frames data should be loaded
      #
      #                  Input:  desiredStateIndex(int)
      #
      #                 Return:  minTemp(int)
      #
      #######################################################################################################################

      """

      tempList = []
      for frame in self.dPesSim.DPES_FRAMES:

         if (frame['stateIndex'] == desiredStateIndex):
            tempList.append( int(frame['dPES Measure Temp']) )

      tempList.sort()
      if testSwitch.FE_0251909_480505_NEW_TEMP_PROFILE_FOR_ROOM_TEMP_PRE2 or testSwitch.FE_0258915_348429_COMMON_TWO_TEMP_CERT:
         minTemp = max(tempList)
      else:
         minTemp = min(tempList)

      if minTemp < 0:
         objMsg.printMsg("getMinimumTemp/ something wrong finding minimum temp.")
         objMsg.printMsg("getMinimumTemp/ tempList: %s" % (tempList))

      return minTemp


   def SaveSIMFilesToDrive_ETF(self, ):
      """
      #######################################################################################################################
      #
      #               Function:  SaveSIMFilesToDrive_ETF
      #
      #        Original Author:  Michael T. Brady
      #
      #            Description:  Force saving data to SIM file using tried and true legacy methods.  This is essentially the code
      #                          from base_SerialTest.py class CSaveSIMFilesToDUT.
      #
      #          Prerrequisite:  data to be saved should be on the CM currently.
      #
      #                  Input:  None
      #
      #           Return Value:  None
      #
      #######################################################################################################################

      """
      ######################################
      #  Save AFH results to the system area (ETF) of the drive under test
      ######################################
      objMsg.printMsg("Force saving AFH SIM data to drive ETF using legacy methods in SaveSIMFilesToDUT")

      iteration = 0
      self.dut.saveToDisc = -1
      while (self.dut.saveToDisc != 1) and (iteration < 10):
         iteration = iteration + 1

         self.readFromCM_SIMWriteToDRIVE_SIM(exec231 = 1)

      # Here we need to add code to check that the results are valid.

      self.clearFrames()
      self.readFramesFromDRIVE_SIM()
      self.display_frames()

      if self.dPesSim.DPES_FRAMES == [] and not testSwitch.virtualRun:
         objMsg.printMsg('After Writing to the Sim File and then reading the same file back again no data was found!!!')
         ScrCmds.raiseException(11044,"DRIVE_SIM data not Found.")
      ######################################



class dPESFrame(baseDataFrame):
   """
   Frame class for implementing dPESFrames.
   Contains code for initialization of all structure for the data container.
   """
   def __init__(self):
      baseDataFrame.__init__(self)
      self.lgcHeadIndex = 5
      self.physHeadIndex = 3

   def __del__(self):
      baseDataFrame.__del__(self)

   def loadNew(self, mode, stateName, stateIndex, consistCheckIndex, logHead, zone, cylinder, measureNumber, \
      temperature, long_integer1, long_integer2, float1, float2, float3):
      """
      Adds a new measurement to the frame. Measurement must be added all at once.
      """

      physHead = objDut.LgcToPhysHdMap[logHead]
      
      if testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION:

         self.addItems([[mode, 'mode', 'B',struct.calcsize('B'),5],
                        [stateName, 'stateName', '4s',struct.calcsize('4s'),5],
                        [stateIndex, 'stateIndex', 'B',struct.calcsize('B'),5],
                        [physHead, 'PHYS_HD', 'B',struct.calcsize('B'),5],
                        [consistCheckIndex, 'consistCheckIndex', 'B',struct.calcsize('B'),5],
   
                        [logHead, 'LGC_HD', 'B',struct.calcsize('B'),5],
                        [zone, 'Zone', 'B',struct.calcsize('B'),5],
                        [cylinder, 'Cylinder', 'L',struct.calcsize('L'),5],
                        [measureNumber, 'Measurement Number', 'B',struct.calcsize('B'),5],
   
                        [temperature, 'dPES Measure Temp', 'b',struct.calcsize('b'),5],
   
                        [long_integer1,'long_integer1','l',struct.calcsize('l'),5],
                        [long_integer2,'long_integer2','l',struct.calcsize('l'),5],
                        [float1,'float1','f',struct.calcsize('f'),5],
                        [float2,'float2','f',struct.calcsize('f'),5],
                        [float3,'float3','f',struct.calcsize('f'),5],
   
                       ])
      else:
         self.addItems([baseDataFileComponent(mode, 'mode', 'B'),
                        baseDataFileComponent(stateName, 'stateName', '4s'),
                        baseDataFileComponent(stateIndex, 'stateIndex', 'B'),
                        baseDataFileComponent(physHead, 'PHYS_HD', 'B'),
                        baseDataFileComponent(consistCheckIndex, 'consistCheckIndex', 'B'),

                        baseDataFileComponent(logHead, 'LGC_HD', 'B'),
                        baseDataFileComponent(zone, 'Zone', 'B'),
                        baseDataFileComponent(cylinder, 'Cylinder', 'L'),
                        baseDataFileComponent(measureNumber, 'Measurement Number', 'B'),

                        baseDataFileComponent(temperature, 'dPES Measure Temp', 'b'),

                        baseDataFileComponent(long_integer1,'long_integer1','l'),
                        baseDataFileComponent(long_integer2,'long_integer2','l'),
                        baseDataFileComponent(float1,'float1','f'),
                        baseDataFileComponent(float2,'float2','f'),
                        baseDataFileComponent(float3,'float3','f'),

                       ])

   def loadFile(self, fstream):
      """
      Creates a dummy container then reads from the input stream using inherited methods of the items and baseFrame to get values from the input stream.
      @param fstream: Input filestream to read the values from. Offset into file at frame position assumed.
      """
      self.loadNew(0, "", 0, 0,  0, 0, 0, 0,  0, 0, 0,  0.0, 0.0, 0.0)
      self.readStream(fstream)

   def __translateColNames(self):
      if testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION:
         if self.frameItems[0][AFH_VAL] in [AFH_MODE, AFH_MODE_TEST_135_INTERPOLATED_DATA, AFH_MODE_TEST_135_EXTREME_ID_OD_DATA]:
            self.frameItems[10][AFH_NAME] = 'Write Heat Contact DAC'
            self.frameItems[11][AFH_NAME] = 'Heater Only Contact DAC'
            self.frameItems[12][AFH_NAME] = 'Read Clearance'
            self.frameItems[13][AFH_NAME] = 'Write Clearance'
            self.frameItems[14][AFH_NAME] = 'WrtLoss'
         else:
            self.frameItems[10][AFH_NAME] = ''
            self.frameItems[11][AFH_NAME] = 'total_AR_measurements'
            self.frameItems[12][AFH_NAME] = 'HIRP Slope'
            self.frameItems[13][AFH_NAME] = 'HIRP Offset'
            self.frameItems[14][AFH_NAME] = 'R^2 Adj'
            
         if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            self.frameItems[4][AFH_NAME]   = 'Heater Element'
            
      else:   
         if self.frameItems[0].value in [AFH_MODE, AFH_MODE_TEST_135_INTERPOLATED_DATA, AFH_MODE_TEST_135_EXTREME_ID_OD_DATA]:
            self.frameItems[10].name = 'Write Heat Contact DAC'
            self.frameItems[11].name = 'Heater Only Contact DAC'
            self.frameItems[12].name = 'Read Clearance'
            self.frameItems[13].name = 'Write Clearance'
            self.frameItems[14].name = 'WrtLoss'
         else:
            self.frameItems[10].name = ''
            self.frameItems[11].name = 'total_AR_measurements'
            self.frameItems[12].name = 'HIRP Slope'
            self.frameItems[13].name = 'HIRP Offset'
            self.frameItems[14].name = 'R^2 Adj'

         if testSwitch.FE_0132497_341036_AFH_ENABLE_DUAL_HEATER_SELF_TEST_SUPPORT == 1:
            self.frameItems[4].name   = 'Heater Element'
   def __getitem__(self,key,default = None):
      self.__translateColNames()
      if testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION:
         for x in self.frameItems:
            if x[AFH_NAME] == key:
               return x[AFH_VAL]     
         else: 
            return default
      else:      
         return baseDataFrame.__getitem__(self,key,default)

   if testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION:
      def __setitem__(self, key, value):
         self.__translateColNames()
         for No,element in enumerate(self.frameItems):
            if element[AFH_NAME] == key:
               self.frameItems[No][AFH_VAL] = value
            
   def __str__(self):

      self.__translateColNames()

      outStr = ""
      for item in self.frameItems:
         if testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION:
            outStr += "%s: %s," % (str(item[AFH_NAME]), str(item[AFH_VAL]))
         else:
            outStr += "%s: %s," % (str(item.name), str(item.value))
      return outStr


class CAFH_SIM(baseSIMFile):
   """
   Class for implementing the Adaptive Fly Height SIM file.
   """

   AFH_SIM_MJR = 0x0001
   AFH_SIM_MNR = 0x0001
   AFH_FILE_SIZE_OF_FRAME = 36



   def __init__(self, new = 0, numHeads= 8, measPerHead = 4, numTemps = 4):
      """
      Initialization of class handles the basic setup of the SIM file w/ required framework.
      Initialized:
         - Heads
         - Measurements per head
         - Number of temperatures each measurement repeated in
         - AFH File header
         - dPES measurement header
         - Empty measurement frames container
      """
      baseSIMFile.__init__(self)    # calls base class

      #Set up default values
      self.numHeads = numHeads
      self.measPerHead = measPerHead
      self.numTemps = 0

      #Intialize Containers
      self.AFH_DATA_FILE_HEADER = baseDataFrame()
      self.DPES_HEADER = baseDataFrame()
      self.DPES_FRAMES = []
      self.measTableSize = 9

      #Initialize base container headers
      self.createBaseStruct()

   def __del__(self):
      del self.AFH_DATA_FILE_HEADER
      del self.DPES_HEADER
      while len(self.DPES_FRAMES)> 0:
         del_frame = self.DPES_FRAMES.pop(0)
         del del_frame
      del self.DPES_FRAMES

   def Clear_DPES_FRAMES(self):
      while len(self.DPES_FRAMES)> 0:
         del_frame = self.DPES_FRAMES.pop(0)
         del del_frame

   def createBaseStruct(self):
      """
      Add contstuction items for required file headers... Called durng init. Not recommended for re-call during implementation.
      """

      self.AFH_DATA_FILE_HEADER.addItems([
                                 baseDataFileComponent(0,'RESERVED1','B'+'x'*3),
                                 baseDataFileComponent(self.AFH_SIM_MJR,'MAJOR_REV'),
                                 baseDataFileComponent(self.AFH_SIM_MNR,'MINOR_REV'),
                                 baseDataFileComponent(0,'RESERVED2','B'+'x'*12), # the number 7 here is the number of fields in the AFH_SIM file
                                     ])

      self.DPES_HEADER.addItems([     baseDataFileComponent(self.numHeads,'HdCount'),
                                 baseDataFileComponent(self.measPerHead,'Measurements Per Head'),
                                 baseDataFileComponent(self.numTemps,'NumFrames', 'l'),
                                 baseDataFileComponent(self.AFH_FILE_SIZE_OF_FRAME,'FrameSize','H'),
                                 baseDataFileComponent(0,'RESERVED','B'+'x'*12)])

      if DEBUG == 1:
         objMsg.printMsg("createBaseStruct/self.AFH_DATA_FILE_HEADER   : %s" % str(self.AFH_DATA_FILE_HEADER))
         objMsg.printMsg("createBaseStruct/self.DPES_HEADER   : %s" % str(self.DPES_HEADER))


   def addMeasurement(self, mode, stateName, stateIndex, consistCheckIndex, head, zone, cylinder, measureNumber, \
      temperature, long_integer1, long_integer2, float1, float2, float3):
      """
      Add a dPES measurement to the AFH SIM file.
      """
      tmp = dPESFrame()

      tmp.loadNew(mode, stateName, stateIndex, consistCheckIndex, head, zone, cylinder, measureNumber, \
      temperature, long_integer1, long_integer2, float1, float2, float3)
      self.DPES_FRAMES.append(tmp)
      self.DPES_HEADER.set('NumFrames', self.DPES_HEADER['NumFrames']+1 )

   def readAfterWriteSIM(self, fRef):

      writeSIM_md5sum = self.writeToDisc(fRef)
      readSIM_md5sum = self.reloadFromDisc(fRef)
      n = 0
      while (writeSIM_md5sum != readSIM_md5sum) and (n < 10):
         n += 1
         objMsg.printMsg('\nVery SEVERE error has occurred.  md5sum values from written and read values do not match!!!\n', objMsg.CMessLvl.CRITICAL)
         ScrCmds.raiseException(11044, 'SIM file read after write verify failure.  md5sum of written file does not match md5sum of file read')
         writeSIM_md5sum = self.writeToDisc(fRef)
         readSIM_md5sum = self.reloadFromDisc(fRef)

      if (n >= 9) :
         ScrCmds.raiseException(11044, 'md5sum error on AFH SIM.')
      # at this point we need to think of something clever to do in order to try and read the SIM file back
      # or at the least even part of it.



   def writeToDisc(self, fRef):
      """
      Write the data/information contained in memory to disc plus include a crc on the end of the file.
      """

      fRef.open('wb')
      try:
         self.AFH_DATA_FILE_HEADER.writeStream(fRef)
         self.DPES_HEADER.writeStream(fRef)
         if testSwitch.FE_0227617_336764_P_OPTIMIZE_WRITE_READ_AFH_FRAME_FOR_LA_CM_REDUCTION:
            data = ""
         for measurement in self.DPES_FRAMES:

            #First we update the physical to logical map
            if testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION:
               measurement['LGC_HD'] =  objDut.PhysToLgcHdMap[measurement['PHYS_HD']]
               for item in measurement.frameItems:
                  data+=struct.pack(item[AFH_FORMAT],item[AFH_VAL])
            else:
               measurement.set('LGC_HD', objDut.PhysToLgcHdMap[measurement.get('PHYS_HD')])
               #then we write the stream
               if testSwitch.FE_0227617_336764_P_OPTIMIZE_WRITE_READ_AFH_FRAME_FOR_LA_CM_REDUCTION:
                  data += measurement.bufferStream()
               else:
                  measurement.writeStream(fRef)
         if testSwitch.FE_0227617_336764_P_OPTIMIZE_WRITE_READ_AFH_FRAME_FOR_LA_CM_REDUCTION:
            fRef.write(data)
            if testSwitch.FE_0239301_336764_P_CLEAR_DPES_FRAME:
               del data
            else:
               data = None

         #self.putCRC(fRef)
      finally:
         fRef.close()

      md5sum_write = str(self.generate_md5sum(fRef, -1))
      if DEBUG == 1:
         objMsg.printMsg("writeToDisc/ SIM data length : %s  and  md5sum: %s" % (str(self.returnFileSize(fRef)), str(md5sum_write)))
      self.append_md5sum(fRef)
      if DEBUG == 1:
         objMsg.printMsg("writeToDisc/ SIM file length : %s " % str(self.returnFileSize(fRef)))

      return md5sum_write


   def reloadFromDisc(self, fRef):
      """
      Reload the data from an AFH file <<Will over-write all items in memory>>
      """

      # ------------->  Step 1. Determine if SIM file is still valid by md5sum comparison <----------
      # idea here is to compare the md5sum string at the end of the SIM file with the
      # actual md5sum of the file READ from the binary data itself.

      string_at_end_of_file = str(self.getFile_md5sum(fRef))  # used to get the 32 type string off the end of the SIM file

      fRef.open('rb')
      fRef.seek(0, 2)          #Seek to end of file
      fileSize = fRef.tell()  #Get byte offset.. size of file in bytes

      sim_file_read_md5sum = str(self.generate_md5sum(fRef, fileSize - 32))

      fileLength = self.returnFileSize(fRef)


      if string_at_end_of_file != sim_file_read_md5sum:
         objMsg.printMsg('md5sum did not match!  Severe Error!!!')

         ScrCmds.raiseException(11044, 'md5sum error on AFH SIM. Expected:%s Rec:%s' % (string_at_end_of_file, sim_file_read_md5sum)) #


      fRef.open('rb')
      fRef.seek(0, 0)          #Go back to beginning
      try:
         self.AFH_DATA_FILE_HEADER.readStream(fRef)
         self.DPES_HEADER.readStream(fRef)
         if testSwitch.FE_0227617_336764_P_OPTIMIZE_WRITE_READ_AFH_FRAME_FOR_LA_CM_REDUCTION:
            post = fRef.tell()
            dataSize = fileSize - post - 32
            data = fRef.read(dataSize)
            dataIndex = 0         
         if self.DPES_HEADER['HdCount'] == 0:
            self.DPES_HEADER['HdCount'] = 1
         if self.DPES_HEADER['Measurements Per Head'] == 0:
            self.DPES_HEADER['Measurements Per Head'] = 4
         tNumFrames = self.DPES_HEADER.get('NumFrames')
         objMsg.printMsg("reloadFromDisc/DPES_HEADER: %s, Number of meas Frames = %s, md5sum: %s, md5sum at end of file: %s, file length: %s, " % \
         (str(self.DPES_HEADER), tNumFrames, str(sim_file_read_md5sum), string_at_end_of_file, fileLength ), objMsg.CMessLvl.DEBUG)
         if testSwitch.FE_0239301_336764_P_CLEAR_DPES_FRAME:
            while len(self.DPES_FRAMES)> 0:
               del_frame = self.DPES_FRAMES.pop(0)
               del del_frame
         else:
            self.DPES_FRAMES = []
         for x in range(tNumFrames): #fRef.tell() < fileSize + self.measTableSize:

            tmp = dPESFrame()
            if testSwitch.FE_0227617_336764_P_OPTIMIZE_WRITE_READ_AFH_FRAME_FOR_LA_CM_REDUCTION:
               tmp.loadNew(0, "", 0, 0,  0, 0, 0, 0,  0, 0, 0,  0.0, 0.0, 0.0)   
               for item in tmp.frameItems:
                  if testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION:
                     itemSize = struct.calcsize(item[AFH_FORMAT])
                     item[AFH_VAL] = struct.unpack(item[AFH_FORMAT],data[dataIndex:dataIndex+itemSize])[AFH_VAL]
                  else:
                     itemSize = struct.calcsize(item.format)
                     item.value = struct.unpack(item.format,data[dataIndex:dataIndex+itemSize])[AFH_VAL]
                  dataIndex += itemSize
               if testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION:
                  tmp['LGC_HD'] = objDut.PhysToLgcHdMap[tmp['PHYS_HD']]
               else:
                  tmp.set('LGC_HD', objDut.PhysToLgcHdMap[tmp.get('PHYS_HD')])
            else:
               tmp.loadFile(fRef)
               tmp.set('LGC_HD', objDut.PhysToLgcHdMap[tmp.get('PHYS_HD')])
            self.DPES_FRAMES.append(tmp)
         if testSwitch.FE_0227617_336764_P_OPTIMIZE_WRITE_READ_AFH_FRAME_FOR_LA_CM_REDUCTION:
            if testSwitch.FE_0239301_336764_P_CLEAR_DPES_FRAME:
               del data
            else:
               data = None       
      finally:
         fRef.close()

      return sim_file_read_md5sum

   def removeDepopFrameData(self, fRef, burnish_fail_heads = []):
      """
      Reload the data from an AFH file <<Will over-write all items in memory>>
      """

      # ------------->  Step 1. Determine if SIM file is still valid by md5sum comparison <----------
      # idea here is to compare the md5sum string at the end of the SIM file with the
      # actual md5sum of the file READ from the binary data itself.

      string_at_end_of_file = str(self.getFile_md5sum(fRef))  # used to get the 32 type string off the end of the SIM file

      fRef.open('rb')
      fRef.seek(0, 2)          #Seek to end of file
      fileSize = fRef.tell()  #Get byte offset.. size of file in bytes

      sim_file_read_md5sum = str(self.generate_md5sum(fRef, fileSize - 32))

      fileLength = self.returnFileSize(fRef)


      if string_at_end_of_file != sim_file_read_md5sum:
         objMsg.printMsg('md5sum did not match!  Severe Error!!!')

         if (not testSwitch.virtualRun) and (testSwitch.raiseAFHCRCErrors == 1):
            ScrCmds.raiseException(11044, 'md5sum error on AFH SIM. Expected:%s Rec:%s' % (fileCRC, crc)) #

      fRef.open('rb')
      fRef.seek(0, 0)          #Go back to beginning
      try:
         self.AFH_DATA_FILE_HEADER.readStream(fRef)
         self.DPES_HEADER.readStream(fRef)
         if testSwitch.FE_0227617_336764_P_OPTIMIZE_WRITE_READ_AFH_FRAME_FOR_LA_CM_REDUCTION:
            post = fRef.tell()
            dataSize = fileSize - post - 32
            data = fRef.read(dataSize)
            dataIndex = 0                 
         if self.DPES_HEADER['HdCount'] == 0:
            self.DPES_HEADER['HdCount'] = 1
         if self.DPES_HEADER['Measurements Per Head'] == 0:
            self.DPES_HEADER['Measurements Per Head'] = 4
         tNumFrames = self.DPES_HEADER.get('NumFrames')
         objMsg.printMsg("reloadFromDisc/DPES_HEADER: %s, Number of meas Frames = %s, md5sum: %s, md5sum at end of file: %s, file length: %s, " % \
         (str(self.DPES_HEADER), tNumFrames, str(sim_file_read_md5sum), string_at_end_of_file, fileLength ), objMsg.CMessLvl.DEBUG)
         if testSwitch.FE_0239301_336764_P_CLEAR_DPES_FRAME:
            while len(self.DPES_FRAMES)> 0:
               del_frame = self.DPES_FRAMES.pop(0)
               del del_frame
         else:
            self.DPES_FRAMES = []
    
         numFramesAfterDepop = 0
         for x in range(tNumFrames): #fRef.tell() < fileSize + self.measTableSize:
            if DEBUG == 1:
               print("\nStart Frame %s\n" % fRef.tell())
            tmp = dPESFrame()
            if testSwitch.FE_0227617_336764_P_OPTIMIZE_WRITE_READ_AFH_FRAME_FOR_LA_CM_REDUCTION:
               tmp.loadNew(0, "", 0, 0,  0, 0, 0, 0,  0, 0, 0,  0.0, 0.0, 0.0)   
               for item in tmp.frameItems:
                  if testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION:
                     itemSize = struct.calcsize(item[AFH_FORMAT])
                     item[AFH_VAL] = struct.unpack(item[AFH_FORMAT],data[dataIndex:dataIndex+itemSize])[AFH_VAL]
                  else:
                     itemSize = struct.calcsize(item.format)
                     item.value = struct.unpack(item.format,data[dataIndex:dataIndex+itemSize])[AFH_VAL]
                  dataIndex += itemSize
               if testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION:
                  phyHead = tmp['PHYS_HD']
               else:
                  phyHead = tmp.get('PHYS_HD')
            else:            
               tmp.loadFile(fRef)
               phyHead = tmp.get('PHYS_HD')

            if (testSwitch.AFH2_FAIL_BURNISH_RERUN_AFH1 or testSwitch.FE_AFH3_TO_DO_BURNISH_CHECK) and burnish_fail_heads :
               objMsg.printMsg("PhyHead: %s in burnish_fail_heads %s" % (phyHead, str(burnish_fail_heads)))  
               if int(phyHead) not in burnish_fail_heads:                   
                  numFramesAfterDepop = numFramesAfterDepop + 1   
                  self.DPES_FRAMES.append(tmp)
            else:
               objMsg.printMsg("PhyHead: %s " % phyHead)
               objMsg.printMsg("OTFDepopMask : %d " % int(DriveAttributes.get('OTF_DEPOP_MASK','20')))

               objMsg.printMsg("removeDepopFrameData/ objDut.PhysToLgcHdMap %s " % str(objDut.PhysToLgcHdMap))
               #objMsg.printMsg("removeDepopFrameData/ objDut.PhysToLgcHdMap[tmp.get('PHYS_HD')] %s " % str(objDut.PhysToLgcHdMap[tmp.get('PHYS_HD')]))
                   
               if int(phyHead) != int(DriveAttributes.get('OTF_DEPOP_MASK','20')):
                  if testSwitch.FE_0227617_336764_P_OPTIMIZE_WRITE_READ_AFH_FRAME_FOR_LA_CM_REDUCTION and testSwitch.FE_0237593_336764_P_OPTIMIZE_FRAME_ACCESS_DATA_FOR_CM_LA_REDUCTION:
                     tmp['LGC_HD'] = objDut.PhysToLgcHdMap[tmp['PHYS_HD']]
                  else:
                     tmp.set('LGC_HD', objDut.PhysToLgcHdMap[tmp.get('PHYS_HD')])

                  numFramesAfterDepop = numFramesAfterDepop + 1   
                  self.DPES_FRAMES.append(tmp)

         self.DPES_HEADER.set('HdCount', objDut.imaxHead )
         self.DPES_HEADER.set('NumFrames', numFramesAfterDepop )
         objMsg.printMsg("AfterDepop DPES_HEADER: %s," % str(self.DPES_HEADER), objMsg.CMessLvl.DEBUG)
      finally:
         fRef.close()

      return sim_file_read_md5sum

if __name__ == '__main__':
   pass

#---------------------------------------------------------------------------------------------------------#
