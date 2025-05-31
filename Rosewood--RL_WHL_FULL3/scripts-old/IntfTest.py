#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Mack Interface test states (blocks) to go in here
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/IntfTest.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Amazon/IntfTest.py#1 $
# Level: 2
#---------------------------------------------------------------------------------------------------------#


#from DataSequencer import objSeq
from base_IntfTest import *
from CapacityScrn import CCapScrn
from CodeVer import theCodeVersion
import IntfClass
import IntfTTR
import re
#from StateMachine import CBGPN
from base_GOTF import CGOTFGrading
from DBLogDefs import DbLogColumn
from TestParamExtractor import TP
xfer_set_lst = [0x47, 0x48]

###########################################################################################################
