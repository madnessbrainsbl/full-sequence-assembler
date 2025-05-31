#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# $RCSfile: ReliFailCode.py $
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReliFailCode.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/ReliFailCode.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#





###########################################################################################################
class CReliFailCode:
   """
      Reliabiltiy Fail Code Definition
   """

   

   def __init__(self):
       """
         Instantiation 
       """
       self.FailCode = \
       {
         'IDT Wrt Rd Perform'                   : 13501,
         'IDT Seq WR Compare OD LV'             : 13502,
         'IDT Seq WR Compare OD LV'             : 13503,
         'IDT Load Unload Soft'                 : 13504,
         'IDT Butterfly Wrt In HV'              : 13505,
         'IDT Dram Screen Test'                 : 13506,

         # IDT start
         'IDT BER By Zone'                      : 13507,
         'IDT Check Congen'                     : 13040,            # Check drive congen
         'IDT Multi Mode WR'                    : 13041,            # IDT Test fail codes 13040 to 13100
         'IDT UDMA Multi Switch'                : 13042,
         'IDT Multi Wr Single Rd'               : 13043,
         'IDT Write Simulation'                 : 13044,
         'IDT IdleAPM_TTR'                      : 13045,            # IdleAPM_TTR S3/S4    
         'IDT Butterfly Seek'                   : 13046,            # Skip some failcodes for future use
         'IDT Two Point Seek'                   : 13047,
         'IDT Non Destruct Wrt'                 : 13048,
         'IDT Destructive Wrt'                  : 13049,
         'IDT ODT ATI Test'                     : 13050,            # ATI Test
         'IDT FlushCacheVerify'                 : 13051,            # FlushCache Verify    
         'IDT Power'                            : 13052,            # IDT Test fail codes 13050 to 13101
         'IDT CE LOG'                           : 13053,            # Error code for CE log check
         'IDT ID Data'                          : 13054,
         'IDT A8 LOG'                           : 13055,            # Error code for GList check
         'IDT Ata'                              : 13056,
         #'IDT Congen'                          : 13057,            # DT090709 Change to Smart Reset
         'IDT SMART Reset'                      : 13057,            # Use for SMART N1, abandon 'FIN DST N1' from FIN 
         'IDT Set Status'       		        : 13058,
         'IDT A9 LOG'                           : 13059,            # Error code for PList check
         'IDT Wrt Rd Perform'   		        : 13060,            # Skip some failcodes for future use
         'IDT Verify Smart'     		        : 13061,
         'IDT Sys File Load'    		        : 13062,
         'IDT Write Mobile'     		        : 13063,
         'IDT Transfer Rate'    		        : 13064,
         'IDT Access Time'      		        : 13065,
         'IDT Image FileCopy'   		        : 13066,
         'IDT Image FileRead'   		        : 13067,
         'IDT Short DST'        		        : 13068,
         'IDT Long DST'         		        : 13069,
         'IDT Volt N_N'         		        : 13070,
         'IDT Volt L_L'         		        : 13071,
         'IDT Volt H_H'                         : 13072,
         'IDT Read Mobile'      		        : 13073,
         'IDT Read Drive'       		        : 13074,
         'IDT Low Duty Cycle'   		        : 13075,
         'IDT OS Write Test'            		: 13076,
         'IDT Power cycle 1'    		        : 13077,
         'IDT OS Read Test'     		        : 13078,
         'IDT NV Cache Test'                    : 13079,
         'IDT Write Pattern'    		        : 13080,
         'IDT Read Pattern'     		        : 13081,
         'IDT Read Reverse'     		        : 13082,
         'IDT Read Random'      		        : 13083,
         'IDT Power Mode'       		        : 13084,
         'IDT Idle APM Test'                    : 13085,    
         'IDT Random Write'     		        : 13086,
         'IDT Read By Zone'     		        : 13087,
         'IDT Ram Miscompare'                   : 13088,
         'IDT Get Smart Logs'   		        : 13089,
         'IDT Power cycle 2'    		        : 13090,
         'IDT Write Zero Patt'  		        : 13091,
         'IDT Read Zero Verify' 		        : 13092,
         'IDT Power Multiple'   		        : 13093,
         'IDT Power cycle 3'    		        : 13094,
         'IDT Power cycle 4'    		        : 13095,
         #'IDT Verify Attr'      	            : 13096,            # Replace with DOS RESET
         'IDT DOS RESET'                        : 13096,
         'IDT Full Read Vrfy'   		        : 13097,
         'IDT OS Read Rev'                      : 13098,
         'IDT Read Zero Compare'                : 13099,
         #'IDT SDOD CHECK'                      : 13100,            # SDOD Check
         #'IDT DOS RESET'                       : 13101,            # Deprecated, clash with ESG

         'IDT A184 IOEDC'                       : 13150,
         'IDT SDOD CHECK'                       : 13151,            # SDOD Check   
         'IDT STM IDLE'                         : 13152,            # STM Idle check         
         'IDT MOA SDOD LUL'                     : 13153,            # Separate SDOD LUL  
         'IDT RLIST LOG'                        : 13154,            # Rlist Log Check
         'IDT A198 USC'                         : 13155,            # Apple Reqm A198 Uncorrectable Sect Cnt
         'IDT DELAYWRT'                         : 13156,            # Delay Write
         'IDT MSSTR'                            : 13157,            # MS STR
         'IDT ENC EUP'                          : 13158,            # EUP Encroachment
         'IDT BLUENUNSCAN'                      : 13159,            # Bluenun Scan
         'IDT ZONEDEGRADE'                      : 13160,            # TEMP Zonal Performance Degrade Check            
         'IDT SET UDR'                          : 13161,            # Enable/Disable UDR
         'IDT PRE SCREEN'                       : 13163,            # Pre Test Screen
         'IDT ODTV LOG'                         : 13164,            # ODTV Log

         'IDT UNDEF ERROR'                      : 13169,            # Undefine Error
         # Misc
         'Fin DST Thres'                        : 12378,            # VerifySmart Threshold Exceeded

         # CIT start

         'Cit FXfer0'                           : 12440,            # CIT Test fail codes 12440 to 12485
         'Cit FXfer1'                           : 12441,            # Skip some failcodes for future use
         'Cit FXfer2'                           : 12442,
         'Cit FXfer3'                           : 12443,
         'Cit FXfer4'                           : 12444,
         'Cit FXfer5'                           : 12445,
         'Cit FXfer6'                           : 12446,
         'Cit FXfer7'                           : 12447,
         'Cit FXfer8'                           : 12448,
         'Cit FXfer9'                           : 12449,
         'Cit FXfer_ATO'                        : 12450,
         'Cit FXfer_ADF'                        : 12451,
         'Cit FXfer_AAC'                        : 12452,
         'Cit FXfer_AUB'                        : 12453,
         'Cit FXfer_AAM'                        : 12454,
         'Cit FXfer_DBF'                        : 12455,
         'Cit FXfer_FNF'                        : 12456,
         'Cit FXfer_AWD'                        : 12457,
         'Cit FXfer_GEN'                        : 12458,
         'Cit FXfer_RS'                         : 12459,

         'Cit RAMBuf0'                          : 12460,
         'Cit RAMBuf1'                          : 12461,
         'Cit RAMBuf2'                          : 12462,
         'Cit RAMBuf3'                          : 12463,
         'Cit RAMBuf4'                          : 12464,
         'Cit RAMBuf5'                          : 12465,
         'Cit RAMBuf6'                          : 12466,
         'Cit RAMBuf7'                          : 12467,
         'Cit RAMBuf8'                          : 12468,
         'Cit RAMBuf9'                          : 12469,
         'Cit RAMBuf_ATO'	                    : 12470,
         'Cit RAMBuf_ADF'                       : 12471,
         'Cit RAMBuf_AAC'                       : 12472,
         'Cit RAMBuf_AUB'                       : 12473,
         'Cit RAMBuf_AAM'                       : 12474,
         'Cit RAMBuf_DBF'                       : 12475,
         'Cit RAMBuf_FNF'                       : 12476,
         'Cit RAMBuf_AWD'                       : 12477,
         'Cit RAMBuf_GEN'                       : 12478,
         'Cit RAMBuf_RS'                        : 12479,
         'Cit Power'                            : 12480,
         'Cit FLoad'                            : 12481,
         'Cit SetFeature'                       : 12482,
         'Cit Pre Read'                         : 12483,
         'Cit Write Test'                       : 12484,
         'Cit Buff Miscompare'                  : 12485,
         'Cit FXfer10'                          : 12486,
         'Cit Not Buff_Cmp'                     : 12513,
         'Cit Bit Miscompare'                   : 12705,

         # CIT end

         # To be replaced by IDT in future
         'Fin DST Start'                        : 12375,
         'Fin DST Log'                          : 12376,
         'Fin DST Time'                         : 12377,
         'Fin DST Thres'                        : 12378,
         'Fin DST N1'                           : 12379


      }

 
   #---------------------------------------------------------------------------------------------------------#
   def getFailCode(self, TestStep):
       """
          Get failcode from given test step
       """

       if self.FailCode.has_key(TestStep):
          return self.FailCode[TestStep]
       else:
          return 0

   #---------------------------------------------------------------------------------------------------------#
   #---------------------------------------------------------------------------------------------------------#

         
