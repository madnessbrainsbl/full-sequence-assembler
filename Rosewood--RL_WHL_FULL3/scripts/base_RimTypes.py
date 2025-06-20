#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Contains basic rim-riser type mappings
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_RimTypes.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/base_RimTypes.py#1 $
# Level: 2
#---------------------------------------------------------------------------------------------------------#


riserTypeMatrix_SATA = \
   {
   'SerialOnlyList' : ['P5SER1','P5SER1A1ST0S5XXX','P5SER0','P5SER0A1ST0S5XXX','DDSATA','DDPSATA','DDSATAM2','DMSATAM','DMPSATAM','DDSAS','DDSASM','DDSATA_18','DDFC','SPMIRKWOOD','HDSTR','DDSATA', 'DDPSATAD3ST0SCL11', 'DDPSATA', 'DDSATAD3ST0SCL12', 'DMPSATAM', 'DMSATAMF2ST0S8X12', 'DMPSATAMF2ST0S8X12', 'DMSATAMF2SX0S8X50', 'DMSATAM', 'DMSATAMF2ST0S8X01', 'DDPSATAD3ST0SDX12', 'DDPSATAD3ST0SCX12', 'DMPSATAMF2ST0P8L11', 'DDSATAD3ST0SCX12', 'DDSATAD3ST6TCX12', 'DMSATAMF2SX0S8X60'],
   'CPCList'        : ['DDIPATA','DDIPSATA','DIATAM','DISATAM','DIPATAM','DIPSATAM','DDIPSAT2','DIPSAT2M',\
                       'P1CPC1D3ST3PCL41','P1CPC2D3ST3PCL41','P1CPC1','P1CPC2','P2CPC0','P2CPC1','P4CPC1','DDIPSAT2D3ST3PCX12', 'DDIPSATA', 'DDIPSAT2', 'P1CPC1D3ST3PCX41', 'P2CPC1F2ST3PCX41', 'DDIPSATAM', 'DIPSAT2M', 'P4CPC1F2ST3P8L41', 'DIPSATAM', 'P1CPC1D3ST3PCL41', 'P4CPC1F2ST3P8X41', 'P2CPC0F2ST3PCL01', 'DDIPSATAD3ST3PCX12', 'P1CPC1D3ST0PCL11', 'P1CPC1D3ST0SCL12'],
   'NIOSList'       : ['ATA','SATA','ATAM','SATAM'],
   'IOInitList'     : ['P1INI0_ST6G','P1INI0D3ST6TDT31','P1INI0D3ST6TCT31','P1INI0D3ST6TCT33','P1INI0D3SS6TCT33','P5INI1N2ST6B5XXX','P5INI1N2ST6L5XXX','P1INI0D2ST6TCX33', 'P1INI0D2ST6TDX33', 'P5INI1N2ST6B5XXX', 'P5INI0X1ST6L5XXX', 'P1INI0D3ST6TCT33', 'P1INI0D3ST6TCT31', 'P1INI0D3ST6LCX33', 'P1INI0D2ST6LCX33', 'P1INI0D3ST6TDT31', 'P1INI0D2ST6LDX33', 'P1INI0D3ST6LDX33', 'P1INI0F2ST6TCT31', 'P5INI1N1ST6L5XXX', 'P1INI0D3ST6TCX33', 'P1INI0D3ST6TDX33', 'P5INI1N1ST6T5XXX', 'P1INI0D3ST6TCX31', 'P1INI0F2SS6TCT31', 'P1INI0', 'P5INI1'],
   }

riserTypeMatrix_FC = \
   {
   'SerialOnlyList' : [],
   'CPCList'        : [],
   'NIOSList'       : [],
   'IOInitList'     : ['FC4'],
   }

riserTypeMatrix_35_SAS = \
   {
   'SerialOnlyList' : ['DDSAS', 'DDSAS_18','DDSASD3SX0SCX60', 'DDSASD3SX0SDX60', 'DDSASM', 'DDSASMF2SX0SDX01', 'DDSASD3SX0SCX12', 'DDSAS', 'DDSASMF2SX0SCL12', 'DDSASD3SX0SCX50', 'DDSASMF2SX0SDX12', 'DDSASMF2SX0SCX33', 'DDPSATAD3SX0SCX60', 'DDSASD3SX0SDL12', 'DDSASD3SX0SCX33', 'DDSATAD3SX0SCX60', 'DDPSATAD3SX0SCX50', 'HDSTR', 'DDSASMF2SX0SCX12', 'DMPSATAMF2SX0S8X60', 'DDSASD3SX0SCT12', 'DDSATAD3SX0SCX50', 'DDSASD3SX0SDX33', 'DDPSATAD3SX0SDX50', 'DDSASMF2SX0SDX33', 'DDSASMF2SX0SCX01', 'DMPSATAMF2SX0S8X50', 'DDPSATAD3SX0SDX60', 'DDSASMF2SS0SCT02', 'DDSASD3SX0SDX50', 'DDSASD3SX0SDT12', 'DDSASD3SX0SDX12'],
   'CPCList'        : [],
   'NIOSList'       : [],
   'IOInitList'     : ['SAS','P1INI0D3SS6TDT31','SASM','MIRKWOOD','P1INI0F2SS6TCT31','P1INI0D3SS6TCT33','P1INI0D3SS6TCT31','P1INI0D3SS6TCX33','P1INI0D3SS6TDT33','P1INI0F2SS6TCX33', 'P1INI0F2SS6TCT31', 'P1INI0F2SS6TDX33', 'SAS', 'P1INI0D3SS6TDX33', 'P1INI0D2SS6TDT31', 'DDSASIO', 'P1INI0F2SS6TDT31', 'P1INI0F2SS6TCT01', 'P1INI0D3SS6TCT31', 'P1INI0D3SS6TCT33', 'P1INI0D3SS6TCX33', 'P1INI0F2ST6LCX33', 'P1INI0F2ST6TDX33', 'SASM', 'P1INI0F2ST6TCX33', 'P1INI0D2SS6TDX33', 'P1INI0F2ST6LDX33', 'P1INI0D3SS6TDT31'],
   }
