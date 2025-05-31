#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Module loads in data from a fis xml file
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/loadXML.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/loadXML.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
if testSwitch.virtualRun:
   from cmEmul import program
else:
   program = ''
import DbLog, os, sys, re
import DBLogDefs
import MessageHandler as objMsg
import ScrCmds

DEBUG = False


def loadDbLogXML(dut, filePath = os.path.join(".",program.strip(),"virtual.xml")):
   mdbl = DbLog.DbLog(dut)

   if os.path.isfile(filePath):
      loadGemXML(filePath, mdbl)
   else:
      StatMsg("Failed to load product specific virtual.xml. Attempting UnitTest program specific.")
      filePath = os.path.join('..','scripts',program.strip(),'virtual.xml')
      if os.path.isfile(filePath):
         loadGemXML(filePath, mdbl)
      else:
         StatMsg("Failed to load product specific virtual.xml. Attempting global virtual.xml file.")
         filePath = os.path.join('.','virtual.xml')
         if os.path.isfile(filePath):
            loadGemXML(filePath, mdbl)
         else:
            StatMsg("Failed to load global virtual.xml from local path. Expecting UnitTest")
            filePath = os.path.join("..","scripts","virtual.xml")
            if os.path.isfile(filePath):
               loadGemXML(filePath, mdbl)
            else:
               StatMsg("Unable to find parent directory virtual.xml... Searching all sys.path")
               for path in sys.path:
                  vPath = os.path.join(path, 'virtual.xml')
                  if os.path.isfile(vPath):
                     loadGemXML(vPath, mdbl)
                     StatMsg("Using %s" % vPath)
                     break
               else:
                  ScrCmds.raiseException(11049, "Unable to locate a virtual.xml to use for VE")


   if DEBUG > 1:
      StatMsg(mdbl.Tables())
   return mdbl

def StatMsg(data):
   print(data)

def StatErr(data):
   print("="*16 + " ERROR  " + "="*16)
   print(data)
   print("="*40)

def loadGemXML(filePath, dbl):
   if DEBUG:
      import time
      startTime = time.time()
   #Below code leveraged from protos dbLogData loader
   #if os.path.isfile(filePath):

   if filePath.find('</parametric_dblog>') > -1:
      buffer = filePath
   else:
      buffer = open(filePath, 'r').read()

   # Clear out any joined data
   buffer = buffer.replace('</parametric_dblog><parametric_dblog>,\n', '')
   buffer = buffer.replace('</parametric_dblog><parametric_dblog>', '')
   if DEBUG:
      lastTime = time.time()
      print "File Read time= %f" % (lastTime-startTime,)
   #else:
   #   buffer = open(".." + os.sep + "scripts" + os.sep + "virtual.xml", 'r').read()
   j = re.compile('<parametric_dblog>(.+)</parametric_dblog>', re.DOTALL)

   try:
      buffer1 = j.findall(buffer)[0]
   except:
      #try:
         #buffer1 = j.findall("<parametric_dblog>" + buffer + "</parametric_dblog>")[0]
      #except:
      msg = 'Exception Occured: parametric dblog data not found in %s!!\n' % (filePath,)
      objMsg.printMsg(str(msg))
      return

   if DEBUG:
      print "findall time= %f" % (time.time()-lastTime,)
      lastTime = time.time()

   data = {}
   columns = []

   tableData = buffer1.split('TABLE=')
   if DEBUG:
      print "split time= %f" % (time.time()-lastTime,)
      lastTime = time.time()

   rowTimeList = []

   if testSwitch.BF_0144790_231166_P_FIX_GOTF_DBL_REGRADE_DUP_ROWS:
      addedTables = []

   #for table in tableData:
   for x in xrange(len(tableData)):
      #if not table: continue
      if not tableData[x]: continue

      if DEBUG:
         tableStartTime = time.time()

      #rows = table.split('\n')
      rows = tableData[x].split('\n')

      rSplit = rows[0].split()
      table_name = rSplit[0]
      if testSwitch.BF_0144790_231166_P_FIX_GOTF_DBL_REGRADE_DUP_ROWS:
         if not table_name in addedTables:
            addedTables.append(table_name)

      table_type = rSplit[1].split('=')[1]

      columns = rows[1].split(',')
      data_types = rows[2].split(',')

      if DEBUG:
         print "data split time= %f" % (time.time()-tableStartTime,)
         tlastTime = time.time()

      if DEBUG > 1:
         StatMsg(str(data_types))

      tableDef = {
                      'type': 'M' ,
                      'fieldList': []
                                 }

      for counter,col in enumerate(columns):
         temp = DBLogDefs.DbLogColumn(col, data_types[counter], 1)
         tableDef['fieldList'].append(temp)

      if DEBUG:
         print "fieldList time= %f" % (time.time()-tlastTime,)
         tlastTime = time.time()

      # rest of the rows are data rows

      for row in rows[3:]:
         if not row: continue
         rowDict = dict(zip(columns, row.split(',')))
         dbl.Tables(table_name, tableDef).addRecord(rowDict)


      if DEBUG:
         print "RowLoad time= %f" % ((time.time()-tlastTime),)
         print "avgRowLoad time= %f" % ((time.time()-tlastTime)/len(rows[3:]),)


      if DEBUG:
         rowTimeList.append((table_name, time.time()-tableStartTime,))
         print "table %s load time= %f" % rowTimeList[-1]

   if DEBUG:
      rowTimeList.sort(key = lambda item:item[1],reverse = True)
      print "Highest:\n%s" % '\n'.join(map(str, rowTimeList[:10]))

   if testSwitch.BF_0144790_231166_P_FIX_GOTF_DBL_REGRADE_DUP_ROWS:
      return addedTables





def typeData(datType, data):
   if datType == 'N':
      try:
         return int(data)
      except ValueError:
         try:
            return float(data)
         except ValueError:
            return str(data)
   else:
      return str(data.replace('"',''))
if __name__ == "__main__":
   loadDbLogXML(None)
