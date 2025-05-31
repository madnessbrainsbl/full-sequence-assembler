#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Singleton object to keep track of uart settings
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/UartCls.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/UartCls.py#1 $
# Level:4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from DesignPatterns import Singleton
from Rim import objRimType

class CUart(Singleton):
   """
   Class to keep track of uart settings
   """
   def __init__(self):
      Singleton.__init__(self)
      self.__cellBaud = DEF_BAUD

   #----------------------------------------------------------------------------
   def setBaud(self, baud=DEF_BAUD):
      """
      Sets the cell's uart baud rate
      """
      if objRimType.CPCRiser() and not objRimType.CPCRiserNewSpt():
         try:
            ICmd.BaudRate( baud, 0, baud, exc = 1)
         except:
            ICmd.BaudRate(DEF_BAUD,3000, exc = 1)

      else:
         SetBaudRate(baud)                                  #  Change cell baud rate
      self.__cellBaud = baud

   #----------------------------------------------------------------------------
   def getBaud(self):
      """
      Returns the current baud rate of the cell
      """
      return self.__cellBaud

theUart = CUart() #Singleton object to keep track of uart settings
