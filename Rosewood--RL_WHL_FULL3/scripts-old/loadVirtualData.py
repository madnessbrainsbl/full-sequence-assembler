#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2009, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Load Virtual.xml data Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/loadVirtualData.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/loadVirtualData.py#1 $
# Level: 3

#---------------------------------------------------------------------------------------------------------#
from Constants import *
import DBLog2
import os, re, array, sys, types, time
sys.path.append(os.path.join("..","Tools", "AFH"))

if testSwitch.virtualRun:
   from sizeof import *

from DbLogAlias import dbLogTableAliases

from cmEmul import program # copied from current loadXML.py

from DBLogDefs2 import DbLogTblDefs

###########################################################################################################
# 
# The purpose of this file and functions is simply to load the virtual.xml data into the DBLog data
#
###########################################################################################################

def loadVirtualXMLData():
   
   ###########################################################################################################
   #
   # state definitions
   #
   ###########################################################################################################
   
   NO_TBL_FOUND = 0
   TBL_FOUND = 1
   COLUMNS_DEFINED = 2
   SKIP_COLUMN_TYPE_DEFINITION = 3
   GET_DATA = 4
   
   startTime = time.clock()
   print "Beginning to load virtual.xml data"
   
   fileName = 'virtual.xml'
   filePath = '.'
   
   print "program", program
   fileNameAndPath = os.path.join(".", program.strip(), "virtual.xml")
   if not os.path.isfile( fileNameAndPath ):
      fileNameAndPath = os.path.join(".", "virtual.xml")
   if not os.path.isfile( fileNameAndPath ):
      print "virtual.xml file not found!"


   rdPtr = open( fileNameAndPath, 'r')
   allLinesInVirtualFile = rdPtr.readlines()
   rdPtr.close()
   
   allLinesInVirtualFile.pop()      # skip the last line in the file

   debug1TablesLoaded = {}

   numberOfTables = 0
   state = 0
   for line in allLinesInVirtualFile:
   
      if ( state == NO_TBL_FOUND ) or ( state == GET_DATA ):
      
         r1 = re.search("(TABLE=)(?P<tableName>(\w){1,1000})", line )
         if r1 != None:
            state = TBL_FOUND
            tableName = str(r1.group('tableName'))
            continue
      
      if state == TBL_FOUND:
#        print "line 78 trying to load data for tableName", tableName
         state = COLUMNS_DEFINED
         # load the columns...
         columns = line[:-1].split(",")
         if not (tableName in dbLogTableAliases.keys()):
            state = NO_TBL_FOUND
         else:
            state = SKIP_COLUMN_TYPE_DEFINITION
            numberOfTables += 1
         continue
   
      if state == SKIP_COLUMN_TYPE_DEFINITION:
         columnTypeDefintion = line[:-1].split(",")
   
         state = GET_DATA
         continue
   
      if state == GET_DATA:
         dataTypeDefinition = ['B'] * len(columns)
   
         data = line[:-1].split(",")
   
         dataDict = {}
         for i1 in range(0, len(columns)):
            dataDict[ columns[i1] ] = data[ i1 ]
   
            
         if not (tableName in debug1TablesLoaded):
            debug1TablesLoaded[tableName] = ""

         if not (tableName in DbLogTblDefs):
            DbLogTblDefs[ tableName ] = {}
            ####           DbLogTblDefs[ tableName ]['type'] = "'%s'" % (tableType)
            DbLogTblDefs[ tableName ]['columnNames'] = columns
            DbLogTblDefs[ tableName ]['columnTypes'] = columnTypeDefintion

         # This hack job here is necessary because the column types for some SF3 tables are not specified.
         if DbLogTblDefs[tableName]['columnTypes'] == [""]:
            DbLogTblDefs[tableName]['columnTypes'] = []


            for i in range(0, len(DbLogTblDefs[tableName]['columnNames'])):
               col = DbLogTblDefs[tableName]['columnNames'][i]

               if not (col in columns):
                  colType = "V"     # This is ridiculous.  So, if the definitions for the table are completely mismatched store the data as a string.
               else:
                  colType = columnTypeDefintion[ columns.index( col ) ]
               DbLogTblDefs[tableName]['columnTypes'].append( colType )

#              print "DbLogTblDefs[tableName]['columnTypes']", DbLogTblDefs[tableName]['columnTypes'], "DbLogTblDefs[ tableName ]['columnNames']", DbLogTblDefs[ tableName ]['columnNames']

         DBLog2.addRow( tableName, dataDict )
   
   
         continue
   
   # Finished loading data.

   endTime1 = time.clock()
   loadTime = endTime1 - startTime
   
   print "tried to load the following tables debug1TablesLoaded: ", len(debug1TablesLoaded), debug1TablesLoaded
   print "Finished loading %4d tables from virtual.xml data in %3.2f seconds requiring  %8d bytes\n\n" % ( DBLog2.getNumTablesLoaded(), loadTime , DBLog2.getSizeAllTablesInBytes() )

   # end of loadVirtualXMLData




###########################################################################################################
# 
# Main
#
###########################################################################################################


if __name__ == "__main__":

   loadVirtualXMLData()
   DBLog2.displayAllDBlogTablesAndTheirContents()

