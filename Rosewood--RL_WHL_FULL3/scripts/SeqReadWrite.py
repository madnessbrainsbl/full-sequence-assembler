#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Mack Interface test states (blocks) to go in here
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SeqReadWrite.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/SeqReadWrite.py#1 $
# Level: 2
#---------------------------------------------------------------------------------------------------------#

from Constants import *
import ScrCmds
from Process import CProcess
import MessageHandler as objMsg

class CSeqReadWrite(CProcess):
   """
   Implements IO Read Write feature.
   """

   def __init__(self, dut):
      CProcess.__init__(self)

   def seqRead(self, prm_IntfTest_St_read):
      """
      Performs sequential Read in DMA mode
      @param dictionary with
         test_num,
         prm_name,
         CWORD1,
         CWORD2,
         STARTING_LBA,
         TOTAL_BLKS_TO_XFR,
         BLKS_PER_XFR,
         DATA_PATTERN0,
         MAX_NBR_ERRORS,
         timeout

      @return
      """
      self.St(prm_IntfTest_St_read)

   def seqWrite(self, prm_IntfTest_St_write):
      """
      Performs sequential write in DMA mode
      @param dictionary with
         test_num,
         prm_name,
         CWORD1,
         CWORD2,
         STARTING_LBA,
         TOTAL_BLKS_TO_XFR,
         BLKS_PER_XFR,
         DATA_PATTERN0,
         MAX_NBR_ERRORS,
         timeout

      @return
      """

      self.St(prm_IntfTest_St_write)
