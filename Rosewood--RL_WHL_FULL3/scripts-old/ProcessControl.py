# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
from Test_Switches import testSwitch

ReworkMQM = {
            #'Condition0' : {'PN':'*',      'PRIME':'*',     'SBR':'*',   'CLRM_EXIT_DATE':'*',  'DRV_RWK_COMP':'*',    'MEDIA_RECYCLE':'*',  'LINE_NUM':'*',   'CRX_CNT':'*'},    #Set to run mini netapp mqm (same KT_MQMV2) all drives
            #'Condition1' : {'PN':'*',      'PRIME':'P',     'SBR':'*',   'CLRM_EXIT_DATE':'*',  'DRV_RWK_COMP':'*',    'MEDIA_RECYCLE':'7',  'LINE_NUM':'101', 'CRX_CNT':'1'},
}
if testSwitch.FE_0164089_395340_P_B2D2_SELECTION_FEATURE:
                     # [{                                      PN Sampling List}, { Percentage Sampling},Percentage Default]
                     # [{0:[],10:['9SM160-999','9SM260-002'],100:['9KC16V-040']}, {10:['1','2','A','G']},                 0]
   #B2D2TestCondition = [{0:[],10:['9SM160-999','9SM260-002'],100:['9KC16V-040']}, {10:['1','2','A','G']},                 100]
   B2D2TestCondition = [{0:[],10:[],100:[]}, {10:['1','2','A','G']},                 0]
if testSwitch.FE_0164093_460646_P_PN_SWOP_FEATURE:
   PN_Swop = {
               #'nextOper' : {'CurrentPN'    :  'NextPN',...},
               #'CAL2'     : {'9SM160-001'   :  '9SM160-002',...},
   }
