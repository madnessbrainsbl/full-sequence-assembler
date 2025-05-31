#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2010, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# $RCSfile: ReliFileCompare.py $
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReliFileCompare.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReliFileCompare.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#



from ReliFunction import *
#from MessageHandler import objMsg
import MessageHandler as objMsg
from ReliFailCode import *

import os
import time




CIT_Xfer_Rate = 0x45
CE,CP,CN,CV = ConfigId
OK      = 0
FAIL    = -1
UNDEF   = 'UNDEF'
WBF     = 1  # Write  Buffer select on FillBuff*** commands
RBF     = 2  # Read   Buffer select on FillBuff*** commands
BWR     = 3  # Both Write and Read Buffer select on FillBuff*** commands
SBF     = 4  # Serial Buffer select on FillBuff*** commands

#*************************************************************************************************************
class baseIntfFuncs:
    def __init__( self ):
      self.data = {}
      self.error = 0
      self.cmdStr = ''
      objMsg.printMsg( 'Init baseIntfFuncs')
      
    def getError( self ):
        self.error = self.data.get( 'LLRET', -1 )

    def intfCmd( self, cmdStr = '' ):
        # DT
        #self.cmdStr = cmdStr
        self.cmdStr = 'ICmd.' + cmdStr
        objMsg.printMsg( '##### Cmd=%s' % self.cmdStr)
        try: self.data = eval( self.cmdStr )
        except: self.data['LLRET'] = -1
        self.getError()
        objMsg.printMsg( "%s - ERR: %s, DATA: %s"% ( self.cmdStr, self.error, self.data ) )
        return self.error

#------------------------------------------------------------------
class loadFile( baseIntfFuncs ):

    def __init__( self, filename ):
       baseIntfFuncs.__init__( self )
       self.fileName = filename
       objMsg.printMsg( 'Init loadFile')

    def result( self ):
       return self.error, self.data

    def load( self, retry = 1 ):
       retries = 0
       while retries < retry:
           # DT
           #if not self.intfCmd( "LoadFile( '%s', '%s' )"% ( self.fileName, self.fileName ) ):
           if not LoadFile(self.fileName, self.fileName ):
              break
           retries += 1
       return self.result()
#------------------------------------------------------------------
class fileTests( baseIntfFuncs ):

    LOADFILE_ERR = -10
    FILE_NOT_EXISTS = -11
    CIT_ATA_ERR = -12
    SET_DRIVE_MODE = -13

    def __init__( self ):

       baseIntfFuncs.__init__( self )
       self.oFC = CReliFailCode()       # DT
       self.failure = 'IDT RAM Miscompare'  # DT set to default
       self.driveattr = {}
       
       self.driveattr['citnumverify'] = 0  # DT initialize
       self.driveattr['citnumfailed'] = 0  # DT initialize

       self.FRvalue   = 0x03   # Set Trasnfer Mode
       self.txferRate = 0x00   # PIO Mode
       self.expandSize = 0
       self.Cmd = ' '
       self.writeLps = 1
       self.verifyLps = 1
       self.regions = 1
       self.filenum = 0
       self.testmode ='PIO'
       self.filename = 'N/A'
       self.TestName = 'File Test'
       self.fileCRC = 0
       self.fileList, self.fileCnt = {}, 0
       objMsg.printMsg( 'Init fileTests')

    def result( self ):
       return self.error, self.data

    def checkError( self ):
       numverify = self.writeLps * self.verifyLps
       testname  = ('Cit FXfer%s' % self.filenum)
       numfailed = 0

       if self.data.has_key( "CRC" ) and self.data.has_key( "ERRCNT" ) and self.error:
          if int( self.data['ERRCNT'] ) < 2:
             self.error = 0
             objMsg.printMsg( 'CIT %s #%s %s - CRC error 1 occurrance - Pass the Drive'%( self.TestName, self.filenum, self.testmode ) )
             self.data['ERRCNT'] = '0'

       if self.data.has_key('ERRCNT'):
          numfailed = int(self.data['ERRCNT'])
          # DT240909 FIS forbid use of ";" replace with "/"
          #attrvalue = '%s;%d;%d' % (self.filename, numfailed, numverify)
          attrvalue = '%s/%d/%d' % (self.filename, numfailed, numverify)
          attrname = 'FX_TEST_%s'%self.filenum
          DriveAttributes[attrname] = attrvalue
          # DT
          #RT190811: fix bug when there is no numfail, the failcode should not have value
          if numfailed :
             self.failure = testname
             self.driveattr['failcode'] = self.oFC.getFailCode(testname)

       if not self.error and not numfailed:
          objMsg.printMsg('CIT %s #%s %s %s - Passed' % ( self.TestName, self.filenum, self.testmode, self.filename))
       elif self.error == self.SET_DRIVE_MODE:
          # DT
          testname = 'Cit SetFeature'
          self.failure = testname
          self.driveattr['failcode'] = self.oFC.getFailCode(testname)    # EC12482 'Cit SetFeature'
       elif self.error == self.FILE_NOT_EXISTS:
          objMsg.printMsg('CIT %s %s - No File Name Found -Name=%s' % (self.TestName, self.filenum, self.filename))
          self.error = 0
       else:
           objMsg.printMsg('CIT %s #%s %s %s - Failed -Data=%s' % ( self.TestName,self.filenum, self.testmode, self.filename, self.data ))
           objMsg.printMsg('CIT %s #%s %s %s - Num Verify=%d -Num Failed=%d' % ( self.TestName, self.filenum, self.testmode, self.filename, numverify, numfailed ))
           self.driveattr['citnumverify'] += numverify     # increment
           self.driveattr['citnumfailed'] += numfailed     # increment
           # DT 
           self.driveattr['failcode'] = self.oFC.getFailCode(testname)
           if self.error == self.CIT_ATA_ERR:
              objMsg.printMsg( 'CIT %s #%s %s Failed NOT Miscompare -Data=%s' % ( self.TestName, self.filenum, self.testmode, self.data ) )
              error_type = FindError(self.data)
              testname = 'Cit FXfer' + error_type
              # DT
              self.failure = testname
              self.driveattr['failcode'] = self.oFC.getFailCode(testname)
           elif self.error == self.LOADFILE_ERR:
              objMsg.printMsg( 'CIT %s #%s %s - Failed Load File -Data=%s' % ( self.TestName, self.filenum, self.filename, self.data ))
              objMsg.printMsg( 'Skipping %s file'%self.filenum )
       # DT
       DriveAttributes.update(self.driveattr)  

       

    def Test( self,  paramsList, deleteFile = 1 ):
       self.fillCmd( paramsList )
       objMsg.printMsg('CIT %s #%s %s start Test: %s'%( self.TestName, self.filenum, self.testmode, time.ctime() ) )
       self.setDriveFR()
       if not self.error:
          if paramsList[0] == 'N/A': self.error = self.FILE_NOT_EXISTS
          else:

              # DT
              #self.data = LoadFile( paramsList[0], paramsList[0] )
              self.error, self.data = loadFile( paramsList[0] ).load()


              if self.error: self.error = self.LOADFILE_ERR
       else: self.error = self.SET_DRIVE_MODE

       # DT
       if not self.error:

          self.intfCmd( self.Cmd )
          if self.error: self.error = self.CIT_ATA_ERR
       self.checkError()
       if not self.error and deleteFile:
          # DT
          #df_data = DeleteFile( self.filename,2 )   #RO Delete file in memory & retry 2x if necessary
          df_data = ICmd.DeleteFile( self.filename,2 )   #RO Delete file in memory & retry 2x if necessary
          objMsg.printMsg('CIT %s #%s %s %s - Delete File data=%s' % ( self.TestName, self.filenum, self.testmode, self.filename, df_data))
       objMsg.printMsg('CIT %s #%s %s end Test: %s'%( self.TestName, self.filenum, self.testmode, time.ctime() ) )
       return self.result()

    def Loop( self, retry = 1, numFile = 0 ):
        ICmd.SetIntfTimeout(60000)
        lst = self.fileList.keys()
        lst.sort()
        doneList, filesTested = [], 0
        cfgFile = ''
        nCnt, retryCnt, = 0, 0
        if numFile: self.fileCnt = numFile
        loadrtry = self.fileCnt * 2 # this will give it 2 retries each file
        while filesTested < self.fileCnt:
              if lst[nCnt] not in doneList:
                 cfgFile = self.fileList[lst[nCnt]]
                 self.filenum = lst[nCnt]
                 self.doTest( ConfigVars[CN][ cfgFile ] )
                 if not self.error:
                    doneList.append(lst[nCnt] )
                    filesTested += 1
                    retryCnt = 0
                    loadrtry -= 2
                 elif self.error in [ self.CIT_ATA_ERR, self.SET_DRIVE_MODE ] :
                    if retryCnt < retry:
                       retryCnt += 1
                       continue
                    else: break
                 elif self.error == self.LOADFILE_ERR:
                    if loadrtry <= 0: break
                    else: loadrtry -= 1
                 else:
                    break
              nCnt += 1
              if nCnt >= self.fileCnt: nCnt = 0
              #objMsg.printMsg(" FILESTESTED: %d-nCNT%d"% ( filesTested, nCnt ) )
        ICmd.SetIntfTimeout(1000)
        if self.error  == OK:
           objMsg.printMsg('CIT Passed %s test - Result = %d' %( self.TestName, self.error ) )
        else:
           objMsg.printMsg('CIT Failed %s test - Data = %s' %( self.TestName, self.data ) )
           
        # DT   
        if self.driveattr.has_key('citnumverify'):
           self.data['citnumverify'] = self.driveattr['citnumverify']
           self.data['citnumfailed'] = self.driveattr['citnumfailed']
        #return self.error
        return self.error, self.data, self.failure

    def doTest( self, paramsList ):
          objMsg.printMsg( "Base class implemntation of doTest" )

    def fillCmd( self, paramsList ):
          objMsg.printMsg("Base class implemntaion of fill Cmd")

    def setDriveFR( self, retry = 1 ):
          self.error = 0
#--------------------------------  CIT File Compare -------------------------------------#

class fileCompare( fileTests ):
    def __init__( self, multiSect=1 ):
       fileTests.__init__( self )

       self.TestName = 'File Compare'
       self.startLBA = 0
       self.sctrCnt = 256
       self.multiSect = multiSect
       objMsg.printMsg( 'Init fileCompare')
       objMsg.printMsg( 'MultiSect=%d' % self.multiSect)
    #startLBA,scnt,rvlp,wlp,regions,filename,testSize
    def fillCmd( self, paramsList ):
        self.filename = paramsList[0]
        self.testmode = paramsList[1]
        self.verifyLps = paramsList[2]
        self.writeLps = paramsList[3]
        self.expandSize =  self.data.get( 'SIZE', paramsList[4]*1024*1024 )
        self.regions = paramsList[5]
        self.Cmd+= "( %d,%d,%d,%d,%d,'%s',%s)"% \
                    (self.startLBA,self.sctrCnt, self.verifyLps,self.writeLps, self.regions,\
                     self.filename,self.expandSize)

    def doTest( self,  paramsList=[] ):
         objMsg.printMsg('----------------------------------------------------------------------------------------------')
         if paramsList[1].upper() == 'PIO':
            self.error,self.data = fileComparePIO( self.filenum, paramsList ).result()
         if paramsList[1].upper() == 'DMA':
            self.error,self.data = fileCompareDMA( self.filenum, paramsList, CIT_Xfer_Rate ).result()
         if paramsList[1].upper() == 'MULTI':
            # DT
            #self.error,self.data = fileCompareMulti( self.filenum, paramsList, 0x08 ).result()
            #self.error,self.data = fileCompareMulti( self.filenum, paramsList, ID_data['MultSec'] ).result()
            self.error,self.data = fileCompareMulti( self.filenum, paramsList, self.multiSect ).result()

    def setDriveFR( self, retry = 1 ):
       retries = 0
       while retries < retry:
           # DT
           if not self.intfCmd( "SetFeatures( %d, %d )"% ( self.FRvalue, self.txferRate ) ):
           #if not ICmd.SetFeatures( self.FRvalue, self.txferRate ):
              if retries != retry:
                 # DT Invalid
                 #self.intfCmd( "ReadDMALBA( %d, %d )"% ( 0, 256 ) )
                 self.intfCmd( "ReadDMA( %d, %d )" %( 0, 256 ) )
                 #ICmd.ReadDMALBA( 0, 256 )
              break
           else:
              ICmd.HardReset()
              ICmd.Wait( 10 )
           retries += 1

#------------------------------------------------------------------
class fileCompareMulti( fileCompare ):
    def __init__( self, filenum, paramsList, modevalue = 0x00 ):
       fileCompare.__init__( self )
       self.modeValue = modevalue
       self.filenum = filenum
       self.Cmd ='WRFileCompareMulti'
       self.Test( paramsList )
       objMsg.printMsg( 'Init fileCompareMulti')
    def setDriveFR( self, retry = 1 ):
       # DT
       self.intfCmd( "SetMultipleMode( %d )"% self.modeValue )
       #ICmd.SetMultipleMode( self.modeValue )
#------------------------------------------------------------------
class fileComparePIO( fileCompare ):
    def __init__( self, filenum, paramsList, xferRate = 0x00 ):
       fileCompare.__init__( self )
       self.Cmd = 'WRFileComparePIO'
       self.filenum = filenum
       self.txferRate = xferRate
       self.Test( paramsList )
       objMsg.printMsg( 'Init fileComparePIO')
#------------------------------------------------------------------
class fileCompareDMA( fileCompare ):
    def __init__( self, filenum,  paramsList, xferRate ):
       fileCompare.__init__( self )
       self.Cmd = 'WRFileCompareDMA'
       self.filenum = filenum
       self.txferRate = xferRate
       self.Test( paramsList )
       objMsg.printMsg( 'Init fileCompareDMA')
#------------------------------------------------------------------


#--------------------------------  CIT File Transfer -------------------------------------#
#class fileTransfer( fileTests ):
#    def __init__( self ):
#       fileTests.__init__( self )
#       self.TestName = 'File Transfer'
#       self.Cmd = "FileTXTest"
#       self.fileCRC = 0
#       self.fileMD5 = 0
#       self.txferRate = 0x0100 #PIO
#       self.compare = 1
#       self.expandSize =  10*1024*1024 #10Mb
#       self.regions = 1
#
#    def fillCmd( self, paramsList ):
#       self.filename = paramsList[0]
#       self.fileCRC = paramsList[1]
#       self.fileMD5 = paramsList[2]
#       self.testmode = paramsList[3]
#       self.verifyLps = paramsList[4]
#       self.writeLps = paramsList[5]
#       try:
#          if paramsList[6] == 'NOEXP':
#             self.expandSize =  0
#       except:
#          self.expandSize =  10*1024*1024 #10Mb
#
#       self.Cmd+= "( '%s',%d,%d,%d,%d, %d,%d,%d,'%s')"% (self.filename,
#                    self.expandSize,self.writeLps,self.verifyLps,self.regions,\
#                    self.txferRate, self.compare, self.fileCRC,self.fileMD5 )
#
#    def doTest( self, paramsList=[] ):
#       objMsg.printMsg('----------------------------------------------------------------------------------------------')
#       if paramsList[3].upper() == 'PIO':
#          self.error,self.data = self.Test( paramsList, 0 )
#       if paramsList[3].upper() == 'DMA':
#          self.error,self.data = fileTransferDMA( self.filenum, paramsList,  CIT_Xfer_Rate ).result()
#       if paramsList[3].upper() == 'MULTI':
#          self.error,self.data = fileTransferMulti( self.filenum, paramsList, 0x208 ).result()
#
##------------------------------------------------------------------
#class fileTransferMulti( fileTransfer ):
#       def __init__( self, filenum, paramsList, modevalue = 0x0442 ):
#            fileTransfer.__init__( self )
#            self.filenum = filenum
#            self.txferRate = modevalue
#            self.Test( paramsList, 0 )
##------------------------------------------------------------------
#class fileTransferDMA( fileTransfer ):
#       def __init__( self,  filenum, paramsList, modevalue = 0x42 ):
#            fileTransfer.__init__( self )
#            value = { 0x45: 0x0445, 0x44: 0x0444, 0x42: 0x0442 }
#            self.filenum = filenum
#            self.txferRate = value[ modevalue ]
#            self.Test( paramsList, 0 )
##------------------------------------------------------------------
#------------------------------------------------------------------


class Compare( fileCompare ):
    def __init__( self, multiSect ):
       fileCompare.__init__( self, multiSect )  # DT add multiSect
       self.fileList, self.fileCnt = getFileList( "CIT CPC Xfer File" )
       # DT 
       self.multiSect = multiSect

       objMsg.printMsg( 'Init Compare')
#------------------------------------------------------------------
#------------------------------------------------------------------
def getFileList( searchStr = 'CIT Xfer File' ):
   fileList = {}
   objMsg.printMsg('getFileList')
   for item in ConfigVars[CN].keys():
       if item.find( searchStr ) != -1:
          try:
              fileList[ item.split( searchStr )[1] ] = item
          except:
              fileList[item] = item



   objMsg.printMsg("%s"% fileList )
   return fileList, len( fileList.keys() )

#--------------------------------  CIT Find Test Error  ----------------------------------#
def FindError(data):
    D_Msg = OFF
    result = OK
    error_type = '_GEN'
    fail_patt = \
    [
       ("ATA_CMDTIMEOUT",      '_ATO'),
       ("ATA_DRIVEFAULT",      '_ADF'),
       ("ATA_WAIT_FOR_DRDY",   '_AWD'),
       ("ATA_ABORTED_COMMAND", '_AAC'),
       ("ATA_UDMATXBUSY",      '_AUB'),
       ("ATA_ADDRESS_MARK",    '_AAM'),
       ("IFC_DMABRIDGEFAIL",   '_DBF'),
       ("FS_FILENOTFOUND",     '_FNF'),
    ]

    for fail in range(len(fail_patt)):
        if D_Msg: objMsg.printMsg('fail_patt %d = %s = %s' % (fail,fail_patt[fail][0],fail_patt[fail][1]))
        if D_Msg: objMsg.printMsg('fail_patt input data = %s' % data)
        data = '%s' % data
        if D_Msg: objMsg.printMsg('fail_patt string data = %s' % data)
        offset = data.find(fail_patt[fail][0])
        if offset >= 0:
           error_type = fail_patt[fail][1]
           break

    return error_type









#-----------------------------------------------------------------------------------------#
#class layout:  baseIntFuncs--->fileTests -->fileCompare -l-> fileCompareDMA, PIO, Multi
#                          l                        l------>fileTransfer -i-> fileTransferDMA, Multi
#                          l----->loadFile
#call this classes Compare(retry = 1, numFile = 0 ),   Transfer().Loop( retry = 1, numFile = 0 )
# retry - Retry for ATA General Errors
# numFile - Number of desired files to test.
#-----------------------------------------------------------------------------------------#



##############################################################################

# Below are from CPC2Func.py

##############################################################################
#-----------------------------------------------------------------------------------------#
def LoadFile(srcFile, dstFile, doMD5=0, scrFileDir=''):

   if ConfigVars[CN].has_key('CPC Reserve'):
      min_space = ConfigVars[CN]['CPC Reserve']
   else:
      min_space = 10000000

   fres = {}
   objMsg.printMsg( 'Inside CPC LoadFile')
   # DT
   #fres = filterResponse(InterfaceCmd("FreeSpace",[]))
   fres = ICmd.FreeSpace()
   freeSpace = int(fres['FREE'])

   objMsg.printMsg('Free Space :%s bytes' % freeSpace )

   if min_space and (freeSpace < min_space):
      WriteToResultsFile('\nFree Space 1:%s bytes\n'%(freeSpace))
      # DT
      #filterResponse(InterfaceCmd('DeleteAllFiles',[]))
      ICmd.DeleteAllFiles()
      fres = {}
      # DT
      #fres = filterResponse(InterfaceCmd("FreeSpace",[]))
      fres = ICmd.FreeSpace()
      freeSpace = int(fres['FREE'])
      # DT
      WriteToResultsFile('\nFree Space 2:%s bytes\n'%(freeSpace))
      #WriteToResultsFile('\nAfter Clear CPC Buffer - Free Space:%s bytes\n'%(freeSpace) + FileDir() + '\n')

   ID = ImageFileDir(srcFile,dstFile,scrFileDir)
   # objMsg.printMsg('LoadFile ImageFileDir=%s' % ID)

   # print ID

   if ID['RESULT'].find ('FS_OPENFORWRITE') >= 0:

   #if ID['LLRET'] != 0:   #  File does not exist
      try:
         # DT
         #print "Filling Buffer"
         objMsg.printMsg('Filling Buffer')
         ImageBufferStuff = FillImageBuffer(srcFile,dstFile,scrFileDir)
	 print "*-*" * 500
	 print ImageBufferStuff
	 return ImageBufferStuff
        # return testLoadFile(srcFile,dstFile)
#         fl = open(os.path.join(UserDownloadsPath,ConfigId[2],srcFile))
#         data = fl.read()
#         fl.close()
#         return FillImageBuffer(dstFile,data)
      except:
         failure = "Failed opening %s file!!" % srcFile
         RES = {}
         RES['RESULT'] = failure
         RES['LLRET']  = -1
         try:
            fl.close()
         except:
           pass

         return RES

   return ID



#-----------------------------------------------------------------------------------------#
def ImageFileDir(srcFile,dstFile,scrFileDir=''):
   #print "ConfigVars = ",ConfigVars
   #print "ConfigId = ",ConfigId
   if scrFileDir == '':
#      print "UserDownloadsPath = ",UserDownloadsPath
      objMsg.printMsg('UserDownloadsPath = %s' %UserDownloadsPath)
      newFilename = UserDownloadsPath + '/' + ConfigId[2] + '/' + srcFile
   else:
      print scrFileDir
      newFilename = scrFileDir + '/' + srcFile
   #print "newFilename  -->> ",newFilename
   #print "ImageFileDir -->> ",srcFile

   size = os.path.getsize(newFilename)
   result = ICmd.ImageFileDir(dstFile, size)
#   return filterResponse(InterfaceCmd('ImageFileDir',[dstFile,size]))
   return result

#-----------------------------------------------------------------------------------------#
def FillImageBuffer(srcFile,dstFile,scrFileDir=''):

   try:     #  Try opening the file
      if scrFileDir == '':
         fl = open(os.path.join(UserDownloadsPath,ConfigId[2],srcFile))
      else:
         fl = open(os.path.join(scrFileDir,srcFile))
   except:  #  Failed opening the file
      failure = "Could not successfully open the %s file!!" % srcFile
      RES = {}
      RES['RESULT'] = failure
      try:
         fl.close()
      except:
         pass
      return (-1,RES)

   sectOffset = 0
   dataLen    = 131072

   while dataLen == 131072:
      data = fl.read(131072)
      dataLen = len(data)

      #
      #  Transfer data to the Write Buffer in the NIOS, at specific Offset
      #
      if dataLen:
         # DT
         #ret = filterResponse(InterfaceCmd("BinaryTransfer",[data,0,dstFile,sectOffset]))
         ret = ICmd.BinaryTransfer(data,0,dstFile,sectOffset)
         sectOffset = sectOffset + 256

   try:     #  Try closing the file
      fl.close()
   except:
      objMsg.printMsg('Exception on try fl.close')
      pass

   if ret['RESULT'].find('IEK_OK') != -1:
      #
      #  Make sure the MD5's match.
      #
      
      # DT
      #InterfaceCmd('UpdateImageMD5',[dstFile])  # Update the MD5 on the file in the NIOS
      ICmd.UpdateImageMD5(dstFile)  # Update the MD5 on the file in the NIOS

      # DT
      #ifd = filterResponse(InterfaceCmd('ImageFileDir',[dstFile]))  # Get MD5 information
      ifd = ICmd.ImageFileDir(dstFile)  # Get MD5 information
      ifd['LLRET'] = 0
      # objMsg.printMsg('FillImageBuffer ImageFileDir=%s' % ifd)

      #
      #  Close the file on the CPC
      #
      #InterfaceCmd('FCloseFile',[dstFile]) # Removed 12-Aug-04 as per Steve Schumacher

      if ifd['LLRET'] == 0:
         filesMD5 = ifd['MD5']

         #
         #  Calculate the MD5 of the file on the CM
         #
         localMD5 = calcMD5(srcFile,scrFileDir)

         #
         #  Compare the MD5 CRC's
         #
         for i in range(0,16):
            if filesMD5[i] != localMD5[i]:
               objMsg.printMsg('MD5 mismatch - filesMD5=%s localMD5=%s' %  (filesMD5[i], localMD5[i]))
               # DT
               #DeleteImageFile(dstFile)       #  Remove the image file from the File System
               ICmd.DeleteImageFile(dstFile)       #  Remove the image file from the File System
               objMsg.printMsg('MD5 mismatch - file deleted=%s' %  dstFile)
               ifd['LLRET']  = -1
               ifd['RESULT'] = 'MD5 CRC compare FAILED!!'
               return ifd

      else:
         return ifd

   return ret

#-----------------------------------------------------------------------------------------#
def calcMD5(srcFile,scrFileDir=''):
   #
   #  This function will open a file and calculate the MD5 crc on that file
   #  then pass the MD5 crc back to the requestor.
   #
   import md5
   m = md5.new()
   try:
      if scrFileDir == '':
         fl = open(os.path.join(UserDownloadsPath,ConfigId[2],srcFile))
      else:
         fl = open(os.path.join(scrFileDir,srcFile))
   except:
      return ''
   length = 512
   while length == 512:
      data = fl.read(512)
      m.update(data)
      length = len(data)
#      print `data`

   fl.close()
   return m.digest()



#-----------------------------------------------------------------------------------------#
#def DeleteImageFile(filename="None"):
#   if filename == 'None':
#      return filterResponse(InterfaceCmd('DeleteImageFile',[]))          # Delete entire image buffer FAT (File Allocation Table)
#   else:
#      return filterResponse(InterfaceCmd('DeleteImageFile',[filename]))  # Delete a specific file out of the FAT



#-----------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------#


#----------------------------------  End of File  ----------------------------------------#