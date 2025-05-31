#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: This is the first script that must be executed by the CM. This is a measure to replace
#              FOFexec calls with import calls, in order to conserve memory space.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/11/08 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/BootScript.py $
# $Revision: #2 $
# $DateTime: 2016/11/08 00:12:47 $
# $Author: gang.c.wang $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/BootScript.py#2 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
try:
   print(str(PortIndex))
   wFOFActive = None
except:
   try:
      print(str(DeviceType))
      wFOFActive = 1
   except:
      wFOFActive = 0

if wFOFActive == 0:
   import sys, os
   
   print
   print '*'*20, 'Entering virtual execution mode...'
   print 'Current Path:', os.getcwd()
   print 'Arguments:', sys.argv
   print '*'*20
   
   def updateSysPath(pgmName):
      npgmName = os.path.basename(pgmName).split('.')
      if len(npgmName) > 1:
         #load product dir
         upperDir = os.path.dirname(pgmName)
         if os.path.join(upperDir,npgmName[0]) not in sys.path:
            sys.path.insert(0,os.path.join(upperDir,npgmName[0]))
         #Build target takes precidence over product dir
         if pgmName.replace('.',os.sep) not in sys.path:
            sys.path.insert(0,pgmName.replace('.',os.sep))
      else:
         if pgmName not in sys.path:
            sys.path.insert(0,pgmName)

   def updateParameters():
      global virtualPgm, virtualPartNum, forcePullDex, logFlag, gui
      # Accomodate 3 methods to supply program name:
         # 1. Command line:  bootscript.py pgmName
         # 2. pgm_Constants.py
         # 3. Prompted for input

      # Method #1
      # Level 1,2 files may be in program-specific folder. If so, MUST supply pgmName
      if len(sys.argv) > 1:
         virtualPgm = sys.argv[1]
         print('Program from command line: %s' % (virtualPgm))

      try:
         if not sys.argv[2] == 'gui':
            virtualPartNum = sys.argv[2].upper()
            print('PartNum from command line: %s' % (virtualPartNum))
      except:
         pass

      if len(sys.argv) > 3:
         forcePullDex = True
      gui = 'gui' in sys.argv

      # Method #2
      if not virtualPgm:
         try:
            from pgm_Constants import virtualPgm
            print('Program from pgm_Constants.py: %s' % (virtualPgm))
         except:
            # Method #3
            if not virtualPgm:
               print("Please enter program name: ")
               response = sys.stdin.readline()
               if response.find(' ') != -1:
                  splitResponse = response.split(' ')
                  if splitResponse[1] == 'log':
                     logFlag = 1
                     virtualPgm = splitResponse[0]
                  elif len(splitResponse) == 2:
                     virtualPgm, virtualPartNum = splitResponse
                  virtualPartNum = virtualPartNum.upper()
                  print('Program from input: %s' % (virtualPartNum))
               else:
                  virtualPgm = response
               print('Program from input: %s' % (virtualPgm))

               pgmPath = os.getcwd() + os.sep + str(virtualPgm).strip()
               updateSysPath(pgmPath)
               
      # Now try importing the part number with the new path
      if not virtualPartNum:
         try:
            from pgm_Constants import virtualPartNum
            print('Program from pgm_Constants.py: %s' % (virtualPartNum))
         except:
            pass
            
      virtualPgm = virtualPgm.strip()
      virtualPartNum = virtualPartNum.strip()

   virtualPgm = ''
   virtualPartNum = ''
   forcePullDex = False
   logFlag = 0
   gui = False
   updateParameters()
   
   # Modify global switches to run virtually
   import base_Test_Switches
   base_Test_Switches.BUILD_TARGET = virtualPgm.split('.')[-1]

   from Test_Switches import testSwitch
   testSwitch.virtualRun = 1
   testSwitch.winFOF = 1
   testSwitch.gui = gui

   import cmEmul
   cmEmul.program = virtualPgm
   cmEmul.UserScriptPath = cmEmul.createUserScriptPath(virtualPgm)
   cmEmul.riserType, cmEmul.partNum = cmEmul.setPartNum(virtualPartNum)
   
elif wFOFActive == 1:
   msg = '\n*** Entering WinFOF mode... ***'
   print(msg)
   print('Current Path: ', os.getcwd())
   print('Arguments: ', sys.argv)
   print('*'*(len(msg)-1))
   
   from Test_Switches import testSwitch
   testSwitch.virtualRun = 0
   testSwitch.winFOF = 1

else:
   from Constants import *
   from StateTable import StateTable


if testSwitch.autoDocument == 1:
   # Download epydoc at: http://epydoc.sourceforge.net/installing.html
   try:
      import epydoc
      del epydoc
   except:
      print("Please download epydoc from http://epydoc.sourceforge.net/installing.html")
   else:
      import glob
      fileList = glob.glob(ScriptPath + CN + '\\*.py')

      print("To Do Document: %s" % str(fileList))
      for myFile in fileList:
         if myFile.find('BootScript.py') == -1:
            fileName = myFile[myFile.rfind('\\')+1:]
            print("Documenting: %s" % fileName)
            resp = os.system('python C:\\Python27\\Lib\\site-packages\\epydoc\\cli.py --html -o C:\\epydocs\\F3\\' + fileName.split('.')[0] + ' ' + myFile)
            print("Documentation Complete...")

if testSwitch.winFOF == 1:
   from cmEmul import ConfigVars, CN, DriveAttributes, stInfo, TraceMessage
   import RunScript
   from StateTable import Operations

   restartFlags = {'doRestart':1}
   TraceMessage(restartFlags)
   if testSwitch.virtualRun:
      def wrap(key, val, initArgs = ''):
         return '<%s %s>%s</%s>' % (key, initArgs, val ,key)
      resultsList = []
      stInfo.createLogFile(virtualPgm,logFlag)

   # import RunScript, Constants, Rim, ICmdFactory, SerialCls, Setup
   while restartFlags['doRestart'] == 1:
      curOper = cmEmul.Operation
      restartFlags = RunScript.main()
      if testSwitch.virtualRun:
         resultsList.append([curOper, cmEmul.ErrorCode])
      if restartFlags == None:
         break

      operList = ConfigVars[CN].get('OperList', Operations)
      cmEmul.Operation = operList[int(DriveAttributes.get('OPER_INDEX',0))]

      #Clear resluts file
      if testSwitch.virtualRun:
         filePath = os.path.join(cmEmul.ResultsFilePath, 'bench.rp1')
         print('*'*20, 'Reset results file: %s' % (filePath))
         open(filePath,'w').write('')

      # Reload the memory space for updates to non-dynamic memory values
      # reload(Constants)
      # reload(Rim)
      # reload(ICmdFactory)
      # reload(SerialCls)
      # reload(Setup)

      print("-"*40)
      print("VE Results")
      print("-"*40)
      print("%5s:\t%10s" % ('OPER', 'ERROR_CODE'))
      print("-"*40)
      print('\n'.join(["%5s:\t%10s" % (i[0],i[1]) for i in resultsList]))
      print("-"*40)

      print("<VE_RESULTS>")
      rows = []
      for line in ["<td>%s</td><td>%s</td>" % (i[0], i[1]) for i in resultsList]:
         rows.append(wrap('tr', line))
      print wrap('table',''.join(rows), initArgs = 'border = 2')
      print("</VE_RESULTS>")
   sys.exit(resultsList[-1][1])

else:
   import RunScript, Constants, Rim, ICmdFactory, SerialCls, Setup, Test_Switches, StateMachine, TestParameters, ServoParameters, Servo_Tuning, Feature_Release_Test_Switches
   import AFH_params, AFH_params_Rosewood, AFH_canonParams, AFH_coeffs_Rosewood, AFH_coeffs_RosewoodLC, st054Params_AFH, st135Params_AFH_v35, st135Params_AFH_v36, st135Params_AFH_v38
   if HOST_ID in ConfigVars[CN].get('HOLD_BY_HOST_ID',[]) or DriveAttributes.get('MTS_HOLD_DRIVE','N') == 'Y':
      TraceMessage('Enable holdDrive for HOST_ID: %s' %HOST_ID)
      ReportRestartFlags({'holdDrive':1})
      ConfigVars[CN]['holdDrive'] = 1
   try:
      if ConfigVars[CN].get('DISABLE_IMMEDIATE',0) == 1:
         RequestService('DisableCell')

      validOP = DriveAttributes['VALID_OPER'].replace("*",'')
      TraceMessage("VALID_OPER/SET_OPER - %s"%(validOP,))

      restartFlags = {'doRestart':1}
      TraceMessage(restartFlags)
      while restartFlags['doRestart'] == 1:
         restartFlags = RunScript.main()
         
         if restartFlags == None: break
         
         # Reload the memory space for updates to non-dynamic memory values
         reload(Test_Switches)
         reload(Feature_Release_Test_Switches)
         reload(Constants)
         reload(Rim)
         reload(ICmdFactory)
         reload(SerialCls)
         reload(Setup)
         reload(StateMachine)
         reload(TestParameters)
         reload(ServoParameters)
         reload(Servo_Tuning)

         reload(AFH_params)
         reload(AFH_params_Rosewood)
         reload(AFH_canonParams)
         reload(AFH_coeffs_Rosewood)
         reload(AFH_coeffs_RosewoodLC)
         reload(st054Params_AFH)
         reload(st135Params_AFH_v35)
         reload(st135Params_AFH_v36)
         reload(st135Params_AFH_v38)

   finally:
      if ConfigVars[CN].get('DISABLE_IMMEDIATE',0) == 1:
         RequestService('EnableCell')
      if testSwitch.virtualRun:
         stInfo.closeLogFile()

