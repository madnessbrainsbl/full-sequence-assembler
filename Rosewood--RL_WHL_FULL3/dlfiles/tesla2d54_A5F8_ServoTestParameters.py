#==============================================================================
#  T282 special test cylinder values.  These constants equate to 5%, 50%, and
#  95% of stroke, regardless of what the max logical cylinder on the drive is.
#==============================================================================
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
      'FREQ_INCR'             : 20,
      'HEAD_RANGE'            : 0x00FF,               # All heads
      'START_CYL'             : T282_TEST_CYL_05_PCT, # OD (5% of max cyl)
      'END_CYL'               : T282_TEST_CYL_05_PCT, # OD (5% of max cyl)
      'SNO_METHOD'            : 1,
      'PEAK_SUMMARY'          : 2,
      'dlfile'                : ('UndefinedPath', 'UndefinedFile'), # NOTE: This file must exist in "C:\var\sterm\dlfiles\bench\".
      'NUM_FCS_CTRL'          : 0,
      'SHARP_THRESH'          : 0, # open up sharpness thresh to be able to detect wider peaks
      'PTS_UNDR_PK'           : 5, # default is 3, used to smooth out noisy bode. Changed due to sharp_thresh
      'PEAK_GAIN_MIN'         : 5,
      'PEAK_WIDTH'            : 250,
      'GAIN_LIMIT'            : 1000,
      'INJECTION_CURRENT'     : 70,
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
# SNOBZ parameters for Tesla2d54 notch design ( HIGH_BANDWIDTH_VER1 )
snoNotches_282_VCM = [
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 0,
   'CWORD1': 0x2108,
   'FREQ_LIMIT': (10800,11800,),
   'FREQ_RANGE': (10800,11800,),
   'FILTERS': 2**2,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 760,
   'NOTCH_DEPTH': 1900,
   'HEAD_RANGE': (0x00FF),
   'INJECTION_CURRENT': 300,
   'spc_id': 31,
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
# SNOBZ parameters for Tesla2d54 notch design ( HIGH_BANDWIDTH_VER1 )
snoNotches_282_DAC = [
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (6600,7500,),
   'FREQ_RANGE': (6600,7500,),
   'FILTERS': 2**0,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 160,
   'NOTCH_DEPTH': 310,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 300,
   'spc_id': 40,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (8100,9200,),
   'FREQ_RANGE': (8100,9200,),
   'FILTERS': 2**1,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 600,
   'NOTCH_DEPTH': 350,
   'HEAD_RANGE': (0x0002),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 41,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (8100,9200,),
   'FREQ_RANGE': (8100,9200,),
   'FILTERS': 2**1,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 700,
   'NOTCH_DEPTH': 500,
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 42,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (9500,10500,),
   'FREQ_RANGE': (9500,10500,),
   'FILTERS': 2**2,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 1140,
   'NOTCH_DEPTH': 900,
   'HEAD_RANGE': (0x0002),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 43,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (10100,11120,),
   'FREQ_RANGE': (10100,11120,),
   'FILTERS': 2**2,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 1140,
   'NOTCH_DEPTH': 900,
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 44,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (11090,11600,),
   'FREQ_RANGE': (11090,11600,),
   'FILTERS': 2**3,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 500,
   'NOTCH_DEPTH': 1500,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 45,
   'FREQ_INCR': 10,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (17200,19000,),
   'FREQ_RANGE': (17200,19000,),
   'FILTERS': 2**5,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 2000,
   'NOTCH_DEPTH': 400,
   'HEAD_RANGE': (0x00FF),
   'AUTO_SCALE_SEED': 260,
   'spc_id': 46,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (19000,22000,),
   'FREQ_RANGE': (19000,22000,),
   'FILTERS': 2**6,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 2500,
   'NOTCH_DEPTH': 1900,
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 47,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (19000,24500,),
   'FREQ_RANGE': (19000,24500,),
   'FILTERS': 2**6+2**7,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,1900,2500,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1600,1900,),
   'HEAD_RANGE': (0x0102),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 48,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (19000,22000,),
   'FREQ_RANGE': (19000,22000,),
   'FILTERS': 2**6,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 2500,
   'NOTCH_DEPTH': 1900,
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 49,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (22000,24500,),
   'FREQ_RANGE': (22000,24500,),
   'FILTERS': 2**7,
   'NBR_NOTCHES': (1),
   'BANDWIDTH': 4500,
   'NOTCH_DEPTH': 1600,
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 50,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (22000,25000,),
   'FREQ_RANGE': (22000,25000,),
   'FILTERS': 2**7+2**8,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,1900,4500,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1000,1700,),
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 51,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (24500,28000,),
   'FREQ_RANGE': (24500,28000,),
   'FILTERS': 2**8+2**9,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,4200,4200,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1500,1500,),
   'HEAD_RANGE': (0x0000),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 52,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (24500,28000,),
   'FREQ_RANGE': (24500,28000,),
   'FILTERS': 2**8+2**9,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,4200,4200,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,1700,1700,),
   'HEAD_RANGE': (0x0102),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 53,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (25000,31500,),
   'FREQ_RANGE': (25000,31500,),
   'FILTERS': 2**9+2**10+2**11,
   'NBR_NOTCHES': (3),
   'BANDWIDTH_BY_ZONE': (0,0,0,4000,4000,4000,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,1900,1900,1900,),
   'HEAD_RANGE': (0x0303),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 54,
},
{
   'START_CYL': T282_TEST_CYL_05_PCT,
   'END_CYL': T282_TEST_CYL_05_PCT,
   'NOTCH_TABLE': 2,
   'CWORD1': 0x2110,
   'FREQ_LIMIT': (28000,31500,),
   'FREQ_RANGE': (28000,31500,),
   'FILTERS': 2**10+2**11,
   'NBR_NOTCHES': (2),
   'BANDWIDTH_BY_ZONE': (0,0,0,0,3000,3000,),
   'NOTCH_DEPTH_BY_ZONE': (0,0,0,0,2300,2300,),
   'HEAD_RANGE': (0x0002),
   'AUTO_SCALE_SEED': 180,
   'spc_id': 55,
},
   ]

