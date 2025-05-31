#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Interface Command Factory object. Returns the requisite object to execute the propper IOCmd
#              based on RimType
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ICmdFactory.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ICmdFactory.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import Rim
import ScrCmds
import MessageHandler as objMsg

DEBUG = 0

if DEBUG > 0:
   objMsg.printMsg("Creating ICmd object for base %s" % Rim.objRimType.baseType)
   objMsg.printMsg("CPCRiser: %s" % Rim.objRimType.CPCRiser())
   objMsg.printMsg("IOInitRiser: %s" % Rim.objRimType.IOInitRiser())

def ICmdFactory():
   from PowerControl import objPwrCtrl
   if (not testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION) and Rim.objRimType.CPCRiser():   
      if testSwitch.FORCE_SERIAL_ICMD:
         from TestParamExtractor import TP
         objMsg.printMsg("FORCE_SERIAL_ICMD Init CPCRiser SPT_ICmd")
         from SPT_ICmd import CPC_SPT_ICmd
         obj = CPC_SPT_ICmd(params = TP, objPwrCtrl = objPwrCtrl)
      else:
         from CPC_ICmd import CPC_ICmd
         import base_CPC_ICmd_Params
         obj = CPC_ICmd(params=base_CPC_ICmd_Params, objPwrCtrl = objPwrCtrl)
   elif testSwitch.CPC_ICMD_TO_TEST_NUMBER_MIGRATION and Rim.objRimType.CPCRiser():
      from CPC_ICmd_TN import CPC_ICmd_TN
      import base_CPC_ICmd_TN_Params
      obj = CPC_ICmd_TN(params = base_CPC_ICmd_TN_Params, objPwrCtrl = objPwrCtrl)   
   elif Rim.objRimType.IOInitRiser() and Rim.objRimType.baseType in Rim.SATA_RiserBase:
      if DEBUG:
         objMsg.printMsg("res %s and %s" % (Rim.objRimType.baseType in Rim.SATA_RiserBase, Rim.SATA_RiserBase))
      if testSwitch.FORCE_SERIAL_ICMD:
         from TestParamExtractor import TP
         objMsg.printMsg("FORCE_SERIAL_ICMD IOInitRiser SPT_ICmd")
         from SPT_ICmd import SATA_SPT_ICmd
         obj = SATA_SPT_ICmd(params = TP, objPwrCtrl = objPwrCtrl)
      else:
         from SATA_ICmd import SATA_ICmd
         import base_SATA_ICmd_Params
         obj = SATA_ICmd(params = base_SATA_ICmd_Params, objPwrCtrl = objPwrCtrl)
   elif Rim.objRimType.IOInitRiser() and Rim.objRimType.baseType in Rim.SAS_RiserBase:
      if DEBUG:
         objMsg.printMsg("res %s and %s" % (Rim.objRimType.baseType in Rim.SAS_RiserBase, Rim.SAS_RiserBase))
      from SAS_ICmd import SAS_ICmd
      import base_SAS_ICmd_Params
      obj = SAS_ICmd(params = base_SAS_ICmd_Params, objPwrCtrl = objPwrCtrl)
   elif Rim.objRimType.SerialOnlyRiser():
      if DEBUG:
         objMsg.printMsg("res %s and serialOnly" % (Rim.objRimType.baseType ))
      from TestParamExtractor import TP

      if testSwitch.NoIO:
         from SPT_ICmd import SPT_ICmd
         obj = SPT_ICmd(params = TP, objPwrCtrl = objPwrCtrl)
      else:
         from Serial_ICmd import Serial_ICmd
         obj = Serial_ICmd(params = TP, objPwrCtrl = objPwrCtrl)
   else:
      class dummyICmd(object):
         """
         Placeholder class to provide a ref object
            fails if access attempted.
         """
         __slots__ = []
         def __init__(self, *args, **kwargs):
            pass
         def __call__(self, *args, **kwargs):
            ScrCmds.raiseException(11043,  "No ICmd support for Riser %s in base %s" % (riserType, Rim.objRimType.baseType))
         def __getattr__(self, name):
            ScrCmds.raiseException(11043,  "No ICmd support for Riser %s in base %s" % (riserType, Rim.objRimType.baseType))
      obj = dummyICmd()

   return obj

if testSwitch.virtualRun:
   class ICMDObj(object):
      def __getattribute__(self, name):
         obj = ICmdFactory()
         return obj.__getattribute__(name)
   ICmd = ICMDObj()
else:
   ICmd = ICmdFactory()
