# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001-2011 Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#-------------------------------------------------------------------------------
# $File: //depot/TCO/DEX/dexChanges.py $
# $Revision: #2 $
# $Change: 639275 $
# $DateTime: 2013/12/04 09:50:41 $
# $Author: alan.a.hewitt $
# $Header: //depot/TCO/DEX/dexChanges.py#2 $
#-------------------------------------------------------------------------------

dexChangeHistory = {
   'V2.44' : (
      "TPD-0000528 - DEX; Eliminate warning for duplicate error code zero entries.",
      "[TPD-0001126] DEX: Add years 2014 thur 2020 to drop down menu of Dexrptgui"
   ),
   'V2.43' : (
      "PFR-0197188: Bug Fix: The ending double quote on PRM_NAME value is gettng removed when a '=' is embedded in string. Only split the first '=' on PRM_NAME script comment.",
      "Improved CRC algorithm to reduce test time",
      "Replace codes.h and proc_codes.h with ErrCodes.py (Will still support code.h and proc_codes.h parsing if ErrCodes.py not found)",
      """Use following python commands to retrieve ErrorCodes.py from FIS:
         import urllib
         url = 'http://shopfloor.fis.shk.minn.seagate.com/drv/ec4py/ec4python.asp'
         urllib.urlretrieve(url, 'ErrorCodes.py')
      """
   ),
   'V2.42' : (
      'Allow dex and dexrtp to unzip result files'
   ),
   'V2.41' : (
      'PFR-0178753: Add optional error message to P_FAULT table.'
   ),
   'V2.40' : (
      'Add years 2012 and 2013 to drop down list in dexrptgui.'
   ),
   'V2.39' : (
      'DEX change per request from Alan Hewitt, allows users to pass in a dictionary of tables codes & spc_ids to skip writing to the parametric file.'
   ),
}