#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: The Rim object is an abstraction of the cell RIM and implements methods to implement
#              to power on/off rim, download CPC/NIOS/Serial code etc.
#              Note that only once instance of rim must exist in the entire test environment.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SerialRim.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SerialRim.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import ScrCmds, time
import MessageHandler as objMsg

from baseRim import baseCRim


class SerialRim(baseCRim):
   def __init__(self, objRimType):
      baseCRim.__init__(self,objRimType)

   def initRim(self):
      ScrCmds.trcBanner("Testing Started on SerialOnly Cell")
      ScrCmds.insertHeader("Testing Started on SerialOnly Cell",length = 40)

   def initSerialRreFpga(self):
      """ Serial Pipe Setup """
      try:
         fpgaFile = (CN, ConfigVars[CN]['RFE Serial FPGA'])
         TraceMessage('Downloading Serial FPGA File. Pls Wait..')
         startTime = time.time()  # for firmware download
         response = DownloadRFEFPGA(fpgaFile)
         endTime = time.time()
         TraceMessage("DownloadRim  elapsed: %d (secs)  response: %s" % (endTime-startTime, `response`))
         if response[1] != 'Done':
           raise
      except:
         ScrCmds.raiseException(13400, "Download SerialFPGA failed")

   #------------------------------------------------------------------------------------------------------#
   def getValidRimBaudList(self, baudRate):
      """
      Returns valid baud rates for rim
      """

      cellBaudList = (Baud38400, Baud115200, Baud390000, Baud460800, Baud625000, Baud921600, Baud1228000)

      cellBaudList, baudRate = self.base_getValidRimBaudList(baudRate, cellBaudList)

      return cellBaudList, baudRate
