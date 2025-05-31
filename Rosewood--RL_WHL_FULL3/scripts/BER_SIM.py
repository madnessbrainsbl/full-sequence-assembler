# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
from Constants import *
import ScrCmds
import MessageHandler as objMsg
from FSO import CFSO
from Drive import objDut
from SIM_FSO import objSimArea

import os
DEBUG = 0

class CBERFile:
    def __init__(self,):
        self.oFSO = CFSO()
        self.dut = objDut
        
        self.berSIMName = "berSIM"
        self.berSIMNameL = "berSIMLoad"
        self.berSIMPath = os.path.join(ScrCmds.getSystemResultsPath(), self.oFSO.getFofFileName(0), self.berSIMName)
        self.berSIMFile = None
        self.berList = []

    def writeToFile(self, berTbl):
        self.berSIMFile = GenericResultsFile(self.berSIMName)
        try:
            self.berSIMFile.open('w')
            objMsg.printMsg('Creating File...')
            self.berSIMFile.write(str(berTbl))
        finally:
            self.berSIMFile.close()
        objMsg.printMsg('File Created')

    def saveFileToDrive(self):
        objMsg.printMsg('Saving file to drive...')
        self.oFSO.saveResultsFileToDrive(1, self.berSIMPath, 0, objSimArea['BER_SIM_FILE'], 1)
        objMsg.printMsg('Save file completed')
        if not testSwitch.virtualRun:
            path = self.oFSO.retrieveHDResultsFile(objSimArea['BER_SIM_FILE'])
            objMsg.printMsg('path : %s'%path)

    def readFromDrive(self):
        self.berSIMFileLoad = GenericResultsFile(self.berSIMNameL)
        
        if not testSwitch.virtualRun:
            path = self.oFSO.retrieveHDResultsFile(objSimArea['BER_SIM_FILE'])
        else:
            path = self.berSIMPath
        self.berSIMFileLoad.open('wb')
        try:
            self.berSIMFileLoad.write(open(path, 'rb').read())
        finally:
            self.berSIMFileLoad.close()
        
        try:
            self.berSIMFileLoad.open('r')
            berStr = self.berSIMFileLoad.read(-1)
        finally:
            self.berSIMFileLoad.close()
        
        if DEBUG:
            objMsg.printMsg('Read BER string from drive : %s'%str(berStr))
        
        ## String to List
        self.berList = eval(berStr)
        objMsg.printMsg('self.berList = %s'%self.berList)
        
        ## Fill in table
        if berStr[-1] in [']']:
            for r in range(len(self.berList)):
                self.dut.dblData.Tables('P_QUICK_ERR_RATE').addRecord(self.berList[r])
        
        if DEBUG:
            objMsg.printMsg('Table print')
            tbl = self.dut.dblData.Tables('P_QUICK_ERR_RATE').tableDataObj()
            objMsg.printMsg(tbl)
