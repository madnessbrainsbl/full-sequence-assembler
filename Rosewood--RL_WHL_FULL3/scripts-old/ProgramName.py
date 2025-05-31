#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Test Parameters for Banshee programs - Trinidad, MantaRay, Sentosa, Bogart
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ProgramName.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ProgramName.py#1 $
# Level: 1
#---------------------------------------------------------------------------------------------------------#


DEFAULT_PF3_BUILD_TARGET = "Luxor.GRDH"
DEFAULT_PF3_BUILD_TARGET = "Sentosa.SE01"

# Please keep this list alphabetazied and in order.
buildTargetToProgramName = {
   "Rosewood7" : ['RW11','RW12'],
   "YarraR"    : ['RY00'],
   "Angsana"   : ['AA00'],
   "Angsana2D" : ['AA2D'],
   "AngsanaH"  : ['Karnak'],
   "Chengai"   : ['SMR00'],
   "M10P"      : ['M0A3000','M0A3100', 'M0A4100', 'M0A4200', 'M0A5100'],
   "M11P"      : ['M1A2000'],
   "M11P_BRING_UP": ['M1A1000'],
}


def getBuildTargetName():

   from Constants import PF3_BUILD_TARGET

   buildTargetList = PF3_BUILD_TARGET.split(".")

   if len(buildTargetList) >= 2:
      buildTargetName = buildTargetList[1]
   else:
      buildTargetName = ""

   return buildTargetName


#
def getProgramFolder():

   from Constants import PF3_BUILD_TARGET

   buildTargetList = PF3_BUILD_TARGET.split(".")

   if len(buildTargetList) >= 1:
      programFolderName = buildTargetList[0]
   else:
      programFolderName = ""

   return programFolderName

#


def isProgramName( programName ):
   programNameFound = getProgramName()

   print "line 79 - programNameFound", programNameFound

   if programNameFound == programName:
      return True
   else:
      return False


#
#
def getProgramName():
   buildTargetName = getBuildTargetName()
   programNameFound = "NOT_FOUND"

   for programName in buildTargetToProgramName:

      list = buildTargetToProgramName[ programName ]

      for tgtName in list:
         if tgtName == buildTargetName:
            programNameFound = programName


   return programNameFound

def getProgramNameGivenTestSwitch( testSwitch ):
   DEBUG = 0

   validProgramNames = buildTargetToProgramName.keys()   # ("Angsana", "Angsana2D", "Kinta", "AngsanaH", "YarraR", "Chengai", "M10P")
   programNameList = [name for name in dir(testSwitch) if name.upper() in map(str.upper, validProgramNames)]

   if DEBUG == 1:
      import MessageHandler as objMsg
      objMsg.printMsg("getProgramNameGivenTestSwitch/ programNameList: %s" % (programNameList))

   programNameEvaluationList = [ eval("testSwitch.%s" % (name)) for name in programNameList]

   if DEBUG == 1:
      objMsg.printMsg("getProgramNameGivenTestSwitch/ programNameEvaluationList: %s" % (programNameEvaluationList))

   if sum(programNameEvaluationList) == 0:
      programName = "NONE_PROGRAM"
      return programName
   else:
      for i in range(0, len(programNameEvaluationList)):
         if programNameEvaluationList[i] == 1:
            programName = programNameList[i]

   programName = programName.capitalize()

   # this is a hack, but it's legacy spelling of the program name
   if programName == "Mantaray":
      programName = "MantaRay"
   if programName == "M10p":
      programName = "M10P"

   return programName



############################################################################################

featureMatrix = {
   "DUAL_HEATER":   [ "GR25", "GR37", "GR3B", "GR3C", "GRDH", "MG3B", "KH01" ],
   }
#
def isFeature( featureNameRequested ):
   buildTargetName = getBuildTargetName()
   if buildTargetName in featureMatrix[featureNameRequested]:
      return True
   else:
      return False


############################################################################################
# Main Section of code.
if __name__ == "__main__":

   print "getProgramName()", getProgramName()


   print "isProgramName( 'Grenada' )", isProgramName( 'Grenada' )
   print "isProgramName( 'Sentosa' )", isProgramName( 'Sentosa' )

   print "isFeature('DUAL_HEATER')", isFeature('DUAL_HEATER')



