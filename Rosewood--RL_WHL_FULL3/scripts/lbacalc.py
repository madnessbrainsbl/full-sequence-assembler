# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
import ScrCmds
from math import ceil

LBAFixedLBAs = {512: {9:17773524,  18:35566480,   36:71687372,   73:143374744, 146:286749488, 300:585937500},
                514: {36:70512692, 73:141025384, 146:282050768, 300:574712644},
                520: {36:70197547, 73:140395093, 146:280790185, 250:480769236, 500:961538472, 750:1442307704, 1000:1923076936},
                522: {36:68965518, 73:139463602, 146:279041740, 300:570053000},
                524: {36:68766592, 73:137577184, 146:275154368, 250:470743144, 500:941486288, 750:1412229424, 1000:1882972568},
                528: {36:68165733, 73:136331467, 146:272662935, 250:469082836, 300:557874778, 500:938165672,   750:1407248504, 1000:1876331336},
                }

CapToLBAFormulas = {512:  lambda cap: int(ceil(97696368 + (1953504 * (float(cap)-50.0)))),  #idema formula
                    4096: lambda cap: int(ceil(12212046 + (244188 * (float(cap)-50.0)))),   #idema formula
                    520:  lambda cap: int(8*ceil(float(cap) * 573653848 / 300.0 / 8)),
                    524:  lambda cap: int(8*ceil(float(cap) * 566007800 / 300.0 / 8)),
                    528:  lambda cap: int(8*ceil(float(cap) * 557874778 / 300.0 / 8)),
                    4104: lambda cap: int(ceil(float(cap) * 1e9 / 4104.0)),
                    4160: lambda cap: int(ceil(float(cap) * 1e9 / 4160.0)),
                    4192: lambda cap: int(ceil(float(cap) * 1e9 / 4192.0)),
                    4224: lambda cap: int(ceil(float(cap) * 1e9 / 4224.0)),
                    }

def sataCapToLba(capacityGB,sectorsize):
   """
   Convert a capacity in GB to an lba count corresponding to Idema spec
   """

   if sectorsize not in [512,4096]:
      ScrCmds.raiseException(11044, "Invalid sector size for RAP field:  %d" % sectorsize)

   return CapToLBAFormulas[sectorsize](capacityGB)

def sasCapToLba(capacityGB,sectorsize):
   """
   Convert a capacity in GB to an lba count that meets the Seagate sector size lba count
   spreadsheet rev 21.
   """

   # check to see if this capacity has a fixed lba count
   if sectorsize in LBAFixedLBAs and capacityGB in LBAFixedLBAs[sectorsize]:
      return LBAFixedLBAs[sectorsize][capacityGB]

   # check for a formula-based version
   elif sectorsize in CapToLBAFormulas:
      return CapToLBAFormulas[sectorsize](capacityGB)

   # otherwise, fail
   else:
      ScrCmds.raiseException(11044, "Invalid sector size for RAP field:  %d" % sectorsize)

