# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/12/15 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
#################################################################################################
# INSTRUCTIONS:
# 1. Enclose all numeric data with double quotes e.g "9999.999"
# 2. Enclose all string data with nested single quotes under double quotes e.g. "'hello world'"
#################################################################################################
CfgVars = \
{
    "AABTYPE_HWY"                         : {'value':"'H_25RW3E'",                           'visibility':'ON'},
    "AABTYPE_RHO"                         : {'value':"'501.16'",                             'visibility':'ON'},
    "AABTYPE_TDK"                         : {'value':"'25AS2M3'",                            'visibility':'ON'},
    "ADG_ENABLE"                          : {'value':"0",                                    'visibility':'ON'},
    "ALLOW_HOLD_RESTART"                  : {'value':"1",                                    'visibility':'ON'},
    "AUD_ENABLE"                          : {'value':"0",                                    'visibility':'ON'},
    "AUTO_SEASERIAL"                      : {'value':"1",                                    'visibility':'ON'},
    "BenchTop"                            : {'value':"0",                                    'visibility':'ON'},
    "Business Group"                      : {'value':"''",                                   'visibility':'ON'},
    "CPC APP"                             : {'value':"'CPC_APP.nex'",                        'visibility':'ON'},
    "CPC On The Fly"                      : {'value':"'OFF'",                                'visibility':'ON'},
    "CPC USB1"                            : {'value':"'CPC_USB1.cfg'",                       'visibility':'ON'},
    "CPC USB2"                            : {'value':"'CPC_USB2.cfg'",                       'visibility':'ON'},
    "CPC Ver"                             : {'value':"'2.249'",                              'visibility':'ON'},
    "CST_EvalName"                        : {'value':"'LODT'",                                'visibility':'ON'},
    "ChkStateDepend"                      : {'value':"1",                                    'visibility':'ON'},
    "DDIS_EvalName"                       : {'value':"'DDIS'",                               'visibility':'ON'},
    "DDIS_Select"                         : {'value':"'OFF'",                                 'visibility':'ON'},
    "DISABLE_IMMEDIATE"                   : {'value':"0",                                    'visibility':'ON'},
    "DRIVE_REPLUG_LIMIT"                  : {'value':"2",                                    'visibility':'ON'},
    "DRT_IO"                              : {'value':"0",                                    'visibility':'ON'},
    "DYNAMIC_RIM_TYPE"                    : {'value':"0",                                    'visibility':'ON'},
    "DefEndState"                         : {'value':"{}",                                   'visibility':'ON'},
    "DefInitOper"                         : {'value':"False",                                'visibility':'ON'},
    "DefInitSeqNum"                       : {'value':"0",                                    'visibility':'ON'},
    "DefInitState"                        : {'value':"{'PRE2':'INIT'}",                      'visibility':'ON'},
    "EVAL_MODE"                           : {'value':"'OFF'",                                'visibility':'ON'},
    "FNG_EvalName"                        : {'value':"'FNG2'",                               'visibility':'ON'},
    "GIO_EvalName"                        : {'value':"'GIO'",                                'visibility':'ON'},
    "GIO_SelectConfig"                    : {'value':"'GIOSEL'",                             'visibility':'ON'},
    "GIO_Selection"                       : {'value':"'OFF'",                                'visibility':'ON'},
    "HOLD_BY_HOST_ID"                     : {'value':"[]",                                   'visibility':'ON'},
    "Hdstr Process"                       : {'value':"'N'",                                  'visibility':'ON'},
    "IDDIS_PN"                            : {'value':"['ALL']",                              'visibility':'ON'},
    "IOFIN2"                              : {'value':"0",                                    'visibility':'ON'},
    "IOLESSTAB"                           : {'value':"1",                                    'visibility':'ON'},
    "LODT_ENABLE"                         : {'value':"1",                                    'visibility':'ON'},
    "MessageOutputLevel"                  : {'value':"13",                                   'visibility':'ON'},
    "PRODUCTION_MODE"                     : {'value':"0",                                    'visibility':'ON'},
    "ParamCodeFile"                       : {'value':"(ConfigName,'param_cd.h')",            'visibility':'ON'},
    "PlugBitsMask"                        : {'value':"0",                                    'visibility':'ON'},
    "Power On Hard Reset"                 : {'value':"'ON'",                                 'visibility':'ON'},
    "PythonSyntax"                        : {'value':"'strict'",                             'visibility':'ON'},
    "RELOAD_CONFIG"                       : {'value':"1",                                    'visibility':'ON'},
    "RESTART_ON_FAIL"                     : {'value':"0",                                    'visibility':'ON'},
    "RFE Serial FPGA"                     : {'value':"'Default'",                            'visibility':'ON'},
    "RFE Ver"                             : {'value':"'Default'",                            'visibility':'ON'},
    "RMT2_ENABLED"                        : {'value':"1",                                    'visibility':'ON'},
    "RUN_OPER_ON_FAIL"                    : {'value':"[]",                                   'visibility':'ON'},
    "ReplugECMatrix"                      : {'value':"{}",                                   'visibility':'ON'},
    "ReplugEnabled"                       : {'value':"1",                                    'visibility':'ON'},
    "RESET_WTF_ATTRS"                     : {'value':"1",                                    'visibility':'ON'},
    "RimType"                             : {'value':"'55'",                                 'visibility':'ON'},
    "SAVE_RESULT"                         : {'value':"1",                                    'visibility':'ON'},
    "SAVE_RUNHIST"                        : {'value':"1",                                    'visibility':'ON'},
    "SDAT2_ENABLE"                        : {'value':"0",                                    'visibility':'ON'},
    "SPMQM_ENABLE"                        : {'value':"0",                                    'visibility':'ON'},
    "SUPPRESS_FW_PTABLES"                 : {'value':"0",                                    'visibility':'ON'},
    "StatePwrLossRecovery"                : {'value':"0",                                    'visibility':'ON'},
    "TaaTProcess"                         : {'value':"1",                                    'visibility':'ON'},
    "USE_VALID_OPER"                      : {'value':"1",                                    'visibility':'ON'},
    "anotherLog"                          : {'value':"1",                                    'visibility':'ON'},
    "autoRegress"                         : {'value':"0",                                    'visibility':'ON'},
    "holdDrive"                           : {'value':"0",                                    'visibility':'ON'},
    "numHeads"                            : {'value':"0",                                    'visibility':'ON'},
    "reportstatus"                        : {'value':"0",                                    'visibility':'ON'},
    "resultsLog"                          : {'value':"1",                                    'visibility':'ON'},
    "script"                              : {'value':"(ConfigName, 'BootScript.py')",        'visibility':'ON'},
    "servo_sap"                           : {'value':"'symbol.pag'",                         'visibility':'ON'},
    "traceLog"                            : {'value':"1",                                    'visibility':'ON'},
    "WTF_TO_1500G"                        : {'value':"1",                                    'visibility':'ON'}, # Control 2D PCO to have next niblet @1.5TB, else will b 1TB
    "WTF_TAB"                             : {'value':"'0E0'",                                'visibility':'ON'}, 
    "WTF_Enable"                          : {'value':"1",                                    'visibility':'ON'}, 
    "ENABLE_SHORT_PRE2"                   : {'value':"0",                                    'visibility':'ON'}, # Enable short PRE2 test only for Scopy pattern verification
    "LCT_SPMQM_ENABLE"                    : {'value':"0",                                    'visibility':'ON'}, # Control the SPMQM for drives with LCT(501.42)
    "PBICSwitches"                        : {'value':"'000000'",                             'visibility':'ON'},
    "PBICSwitchesOEM"                     : {'value':"'000000'",                             'visibility':'ON'},
    "ENABLE_STS"                          : {'value':"0",                                    'visibility':'ON'}, 
    "STS_SN"                              : {'value':"['6']",                                  'visibility':'ON'}, 

}

#################################################################################################
