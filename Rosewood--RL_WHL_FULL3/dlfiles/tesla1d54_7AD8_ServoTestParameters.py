#==============================================================================
#  T282 special test cylinder values.  These constants equate to 5%, 50%, and
#  95% of stroke, regardless of what the max logical cylinder on the drive is.
#==============================================================================
T282_TEST_CYL_99_PCT =  (0xFFFF, 0xFFFC)     # Extreme ID (99% of max logical cylinder)
T282_TEST_CYL_05_PCT =  (0xFFFF, 0xFFFD)     # OD (5% of max logical cylinder)
T282_TEST_CYL_50_PCT =  (0xFFFF, 0xFFFE)     # MD (50% of max logical cylinder)
T282_TEST_CYL_95_PCT =  (0xFFFF, 0xFFFF)     # ID (95% of max logical cylinder)

#==============================================================================
#  Common SNO / SNOBZ parameters:
#     This section defines all T288 parameters that are exactly the same on
#     each call to T282 when SNO or SNOBZ is executed.
#==============================================================================
doBodeSNO_282 = {
      'test_num'              : 282,
      'prm_name'              : 'doBodeSNO_282',
      'timeout'               : 6000,
      'FREQ_INCR'             : 24,
      'HEAD_RANGE'            : 0x00FF,               # All heads
      'START_CYL'             : T282_TEST_CYL_05_PCT, # OD (5% of max cyl)
      'END_CYL'               : T282_TEST_CYL_05_PCT, # OD (5% of max cyl)
      'SNO_METHOD'            : 1,
      'PEAK_SUMMARY'          : 2,
      'dlfile'                : ('UndefinedPath', 'UndefinedFile'), # NOTE: This file must exist in "C:\var\sterm\dlfiles\bench\".
      'NUM_FCS_CTRL'          : 0,
      'SHARP_THRESH'          : 0, # open up sharpness thresh to be able to detect wider peaks
      'PTS_UNDR_PK'           : 3, # default is 3, used to smooth out noisy bode. Changed due to sharp_thresh
      'PEAK_GAIN_MIN'         : 5,
      'PEAK_WIDTH'            : 250,
      'GAIN_LIMIT'            : 1000,
      'INJECTION_CURRENT'     : 300,
      # NOTE: 'NUM_FCS_CTRL' defaults to 0, but is shown here as a remainder that you must specify which controller response is to be used.
      # If more than one VCM and/or DAC controller is included in the file, this parameter is used to select the one to be used during SNO/SNOBZ.
      # 0 selects the first VCM and DAC controller, 1 selects the second controller (for both VCM and DAC), and so on...
   }


#==============================================================================
#  VCM Notch specific parameters:
#     This section is a list of parameter sets that represent each unique T282
#     call used to place VCM notches.  Each parameter set is combined with the
#     common parameters (above) to invoke T282 to place a single notch (SNO)
#     or multiple notches (SNOBZ).  Through any combiantion of single notch or
#     multi-notch placement calls, you should provide parameter sets to ensure
#     all optimized notches are placed - ie: all notches which cannot be left
#     as defaults for all drives.
#==============================================================================
# SNOBZ parameters for Tesla1d54 notch design
snoNotches_282_VCM = [
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 0,
   'CWORD1': 0x0208,
   'FREQ_LIMIT': (2200,3500,),
   'FREQ_RANGE': (2200,3500,),
   'FREQ_INCR': 10,
   'FILTERS': 2**6,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 750,
   'NOTCH_DEPTH': 1300,
   'SNO_METHOD': 1,
   'HEAD_RANGE': 0,
   'PEAK_WIDTH': 10,
   'PHASE_LIMIT': 65036,
   'MAX_BW_THRESH': 300,
   'MIN_BW_THRESH': 70,
   'CWORD2': 96,
   'NBR_MEAS_REPS': 3,
   'NOTCH_CONFIG': 0,
   'NBR_TFA_SAMPS': 14,
   'NUM_SAMPLES': 10,
   'spc_id': 31,
},
{
   'START_CYL': T282_TEST_CYL_99_PCT,
   'END_CYL': T282_TEST_CYL_99_PCT,
   'NOTCH_TABLE': 0,
   'CWORD1': 0x0208,
   'FREQ_LIMIT': (1300,1800,),
   'FREQ_RANGE': (1300,1800,),
   'FREQ_INCR': 10,
   'FILTERS': 2**7,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 750,
   'NOTCH_DEPTH': 1300,
   'SNO_METHOD': 1,
   'HEAD_RANGE': 0,
   'PEAK_WIDTH': 10,
   'PHASE_LIMIT': 65036,
   'MAX_BW_THRESH': 300,
   'MIN_BW_THRESH': 70,
   'CWORD2': 96,
   'NBR_MEAS_REPS': 3,
   'NOTCH_CONFIG': 0,
   'NBR_TFA_SAMPS': 14,
   'NUM_SAMPLES': 10,
   'spc_id': 32,
},
   ]

#==============================================================================
#  uActuator Notch specific parameters:
#     This section is a list of parameter sets that represent each unique T282
#     call used to place DAC notches.  Each parameter set is combined with the
#     common parameters (above) to invoke T282 to place a single notch (SNO)
#     or multiple notches (SNOBZ).  Through any combiantion of single notch or
#     multi-notch placement calls, you should provide parameter sets to ensure
#     all optimized notches are placed - ie: all notches which cannot be left
#     as defaults for all drives.
#==============================================================================
# SNOBZ parameters for Tesla2d54 notch design ( HYAW_CON_02 )
snoNotches_282_DAC = [
{ # hd0/1 - notch 21.6k idx1: 2^0=1
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x0110,
   'FREQ_LIMIT': (20000,22500,),
   'FREQ_RANGE': (20000,22500,),
   'FREQ_INCR': 24,
   'FILTERS': 2**0,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 1500,
   'NOTCH_DEPTH': 1000,
   'SNO_METHOD': 1,
   'HEAD_RANGE': (0x00FF),
   'INJECTION_CURRENT': 70,
   'spc_id': 41,
},
{ # hd0/1 - notch 18.5k idx7: 2^6=64
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x0110,
   'FREQ_LIMIT': (17000,20500,),
   'FREQ_RANGE': (17000,20500,),
   'FREQ_INCR': 24,
   'FILTERS': 2**6,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 700,
   'NOTCH_DEPTH': 600,
   'SNO_METHOD': 1,
   'HEAD_RANGE': (0x00FF),
   'INJECTION_CURRENT': 70,
   'spc_id': 42,
},
{ # hd0/1 - notch 32.5k idx4: 2^3=8
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x0110,
   'FREQ_LIMIT': (30000,33500,),
   'FREQ_RANGE': (30000,33500,),
   'FREQ_INCR': 24,
   'FILTERS': 2**3,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 6000,
   'NOTCH_DEPTH': 2500,
   'SNO_METHOD': 1,
   'HEAD_RANGE': (0x00FF),
   'INJECTION_CURRENT': 70,
   'spc_id': 43,
},
{ # hd0 SNOBZ - notch27.5k idx2+5+6 2^1+2^4+2^5=50
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x0110,
   'FREQ_LIMIT': (23000,29900,),
   'FREQ_RANGE': (23000,29900,),
   'FREQ_INCR': 10,
   'FILTERS': 2**1+2**4+2**5,
   'NBR_NOTCHES': (3),
   'BANDWIDTH_BY_ZONE': (0,0,0,500,500,8000,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,800,800,3000,),
   'SNO_METHOD': 1,
   'HEAD_RANGE': (0),
   'INJECTION_CURRENT': 70,
   'spc_id': 44,
},
{ # hd1 SNOBZ - notch27.5k idx2+3+5 2^1+2^2+2^4=22
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x0110,
   'FREQ_LIMIT': (23000,29900,),
   'FREQ_RANGE': (23000,29900,),
   'FREQ_INCR': 10,
   'FILTERS': 2**1+2**2+2**4,
   'NBR_NOTCHES': (3),
   'BANDWIDTH_BY_ZONE': (0,0,0,900,1500,8000,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,900,1000,2500,),
   'SNO_METHOD': 1,
   'HEAD_RANGE': (0x0101),
   'INJECTION_CURRENT': 70,
   'spc_id': 44,
},
]

