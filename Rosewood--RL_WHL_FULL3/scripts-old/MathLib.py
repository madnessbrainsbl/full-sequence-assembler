#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2008, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: Math Library Module
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/MathLib.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/MathLib.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#

from Constants import *
from TestParamExtractor import TP
import math, types, struct
import ScrCmds
from Process import CCudacom
import MessageHandler as objMsg
from array import array
from Drive import objDut   # usage is objDut
import FSO
from Process import CProcess
import binascii
import Utility

READ_SCALING   = 0
READ_OFFSET    = 1
WRITE_SCALING  = 2
WRITE_OFFSET   = 3

DEBUG = 0


class CDAC_limits:
   """
      Small library to track math function heater DAC limits
   """
   def __init__(self):
      self.minDAC = 0
      self.maxDAC = 63
      self.maxclr_USL = TP.clr_USL_Hard


#######################################################################################################################
#
#               Function:  stDev
#
#            Description:  Calculates the population standard deviation.
# 
#                  Input:  vals
#
#           Return  Type:  stdev
#
#######################################################################################################################

def stDev(vals):
   return math.sqrt(sampleVar(vals))

def sampleVar(vals):
   n = len(vals)
   mn = mean(vals)
   deviations = []
   for item in vals:
      deviations.append(item-mn)
   return sumSquares(deviations)/float(n)


#######################################################################################################################
#
#               Function:  stDev_standard
#
#            Description:  Calculates the usual standard deviation.  NOT the population standard deviation.
#                          Based on sample-based statistics.  See wiki page here http://en.wikipedia.org/wiki/Standard_deviation#Population-based_statistics
# 
#                   Note:  Performance improvements from M. Massey.
# 
#                  Input:  vals(list)
#
#           Return  Type:  stdev
#
#######################################################################################################################

def stDev_standard(vals):
   mean = sum(vals, 0.0)/len(vals)
   stdev = math.sqrt( sum([(item-mean) ** 2.0 for item in vals])/(len(vals) - 1.0) )
   return stdev

def sumSquares(vals):
   return sum([ret**2 for ret in vals])

def mean(vals):
   itMean = sum(vals)/float(len(vals))
   return itMean

def mode(vals):
   freqDict = {}
   for val in vals:
      #init to 0 if not already there
      freqDict.setdefault(val,0)
      freqDict[val] += 1

   dictItems = freqDict.items()
   mxVal = dictItems[0][1]
   modeItem = dictItems[0][0]

   for item,val in freqDict.items():
      if val > mxVal:
         mxVal = val
         modeItem = item

   return modeItem

def median(inputVals):
   safeVals = [d for d in inputVals]
   safeVals.sort()
   if len(safeVals)%2 == 1:
      #Odd value
      medOut = safeVals[int(len(safeVals))/int(2)]
   else:
      #even value
      medOut = ((safeVals[len(safeVals)/2]+safeVals[len(safeVals)/2-1])/2.0)
   return medOut

def nearest(inIterant, compareVal):
   """
   Returns the index of the nearest value in the simple list inIterant to the input value compareVal
   """
   difList = [abs(i-compareVal) for i in inIterant]
   difList.sort()

   try:
      return inIterant.index(compareVal + difList[0])
   except ValueError:
      return inIterant.index(compareVal - difList[0])


def floatXpower2(X, pow):
   """Return X * 2^pow"""
   return typeFloatConvert(X) * (2**pow)

def SolveQuadratic(a, b, c , negTrunc = 1):
   """
   Solves a quadratic equation of the form 0=c+bx+ax^2
   """
   X = 0.0
   if ( a == 0 ):
      if ( b == 0 ):
         X = 0
      else:
         X = ( -c / float(b) )
   else:  # a is non-zero
      X = ( b**2 ) - ( floatXpower2(a * c, 2 ))
      if ( X > 0 ):
         X = ( math.sqrt( X ) - b ) / floatXpower2( a, 1 )
   if ( X < 0 ) and negTrunc == 1:

      X = 0;

   if DEBUG == 1:
      objMsg.printMsg("Output from SolveQuadratic;  X: %s, a: %s, b: %s, c: %s" % (X, a, b, c))
   return( typeFloatConvert(X) );

def Fit_2ndOrder(X,Y):
      N=-1
      s1=0
      s2=0
      s3=0
      s4=0
      t1=0
      t2=0
      t3=0
      #objMsg.printMsg('XList:%s' % X)
      #objMsg.printMsg('YList:%s' % Y)
      for index in X:
         N=N+1
         s1=s1+index
         s2=s2+index*index
         s3=s3+index*index*index
         s4=s4+index*index*index*index
         t1=t1+float(Y[N])
         t2=t2+index*float(Y[N])
         t3=t3+index*index*float(Y[N])
      N = len(X)
      d=N*s2*s4 - N*s3*s3 - s1*s1*s4 - s2*s2*s2 + 2*s1*s2*s3
      if d==0:
         return -1,-1,-1
      A=(N*s2*t3 - N*s3*t2 - s1*s1*t3 - s2*s2*t1 + s1*s2*t2 + s1*s3*t1)/d
      B=(N*s4*t2 - N*s3*t3 - s2*s2*t2 - s1*s4*t1 + s1*s2*t3 + s2*s3*t1)/d
      C=(s1*s3*t3 -s1*s4*t2 -s2*s2*t3 - s3*s3*t1 + s2*s3*t2 + s2*s4*t1)/d
      #objMsg.printMsg('A:%4f' % A)
      #objMsg.printMsg('B:%4f' % B)
      #objMsg.printMsg('C:%4f' % C)
      return A,B,C

def linreg(X, Y):
   """
   Summary
      Linear regression of y = ax + b
   Usage
      real, real, real = linreg(list, list)
   Returns coefficients to the regression line "y=ax+b" from x[] and y[], and R^2 Value

   Test data
   X=[1,2,3,4]
   Y=[357.14,53.57,48.78,10.48]
   print linreg(X,Y)
   should be:
   Slope  Y-Int   R
   -104.477   378.685 0.702499064
   """

   if len(X) != len(Y):
      raise ValueError, 'unequal length'
   N = len(X)
   Sx = Sy = Sxx = Syy = Sxy = 0.0
   for x, y in map(None, X, Y):
      Sx = Sx + x
      Sy = Sy + y
      Sxx = Sxx + x*x
      Syy = Syy + y*y
      Sxy = Sxy + x*y
   det = Sxx * N - Sx * Sx
   
   if det == 0: #(divide by zero error)
      return 0, 0, 0
      
   #objMsg.printMsg("Sxx= %4.3f  Sx= %4.3f  N= %d  det= %4.3f  Sxy= %4.3f  Sy= %4.3f" % (Sxx,Sx,N,det,Sxy,Sy))

   a, b = (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det
   meanerror = residual = 0.0
   for x, y in map(None, X, Y):
      meanerror += (y - Sy/N)**2
      residual += (y - a * x - b)**2

   # Protect against all data points having the same value, (divide by zero error)
   if not meanerror == 0.0:
      RR = 1.0 - residual/meanerror
   else:
      RR = 1.0

   #ss = residual / (N-2)
   #Var_a, Var_b = ss * N / det, ss * Sxx / det
   #print "y=ax+b"
   #print "N= %d" % N
   #print "a= %g \\pm t_{%d;\\alpha/2} %g" % (a, N-2, math.sqrt(Var_a))
   #print "b= %g \\pm t_{%d;\\alpha/2} %g" % (b, N-2, math.sqrt(Var_b))
   #print "R^2= %g" % RR
   #print "s^2= %g" % ss
   return a, b, RR

def typeFloatConvert(value):
   if type(value) == types.StringType:
      value = float(value)
   return value

def prec_int(value):
   return int(value*1e7)

   # ----------------->   End of method  <-------------------------------------------------------



def getNestDictVals(inDict):
   mastOut = []
   if type(inDict) == types.DictType:
      for item in inDict.values():
         if type(item) == types.DictType:
            mastOut += getNestDictVals(item) #Recurse deeper
         elif type(item) == types.ListType:
            mastOut.append(item[AFH_DET]) #Grab the value from the value offset
         else:
            ScrCmds.raiseException(11044,"Invalid input parameter for AFH Dict: %s" % str(item))
   elif type(inDict) == types.IntType:
      mastOut = inDict
   return mastOut

def linear_interpolate(x0, y0, x1, y1, x2):
   """
   Simple linear interpolator to avoid overhead of calling CPolynomialInterpolator.
   """
   x0 = float(x0)
   y0 = float(y0)
   x1 = float(x1)
   y1 = float(y1)
   x2 = float(x2)

   if ((x1-x0) == 0):
      objMsg.printMsg('No interpolation support for vertical line')
      return -1

   slope = (y1 - y0)/float(x1-x0)
   y2 = float((slope * (x2-x0)) + y0)

   #objMsg.printMsg('Inside linear_interpolate method - x0: %s, y0: %s, x1: %s, y1: %s, x2: %s, y2: %s' % \
   #   ( str(x0), str(y0), str(x1), str(y1), str(x2), str(y2) ))

   return y2


def three_point_average_array(input_array, output_array_type):
   """
   Simple three point average of an array input
   """
   output_array = array(output_array_type)   # should be f for float see python reference on array module

   if (len(input_array) < 3):
      return -1

   maxpos = len(input_array) - 1
   output_array.append((input_array[0] + input_array[1])/float(2))

   for pos in range(1, maxpos):
      output_array.append((input_array[pos - 1] + input_array[pos] + input_array[pos + 1]) / float(3))
   output_array.append((input_array[maxpos] + input_array[maxpos - 1])/float(2))

   return output_array


   # Note to self:
   # 1.) change API calls to make sure that calls are now cudacom(logical cyl) instead of logical cylinder
   # 2.) make sure to change AR code so that this takes effect there too as well
   # - test 35 and 191 assume that input cylinder is of type nominal logical


#######################################################################################################################
#
#               Function:  trimmedAverage
#
#        Original Author:  Michael T. Brady
#
#            Description:  calculates a "trimmed" average by removing a certain percentage of the maximum and 
#                          minimum data points in a list passed by inputDataList.
# 
#                          Note: if there are an odd number of data points to be removed this currently biases
#                          up by removing the lower data point last.
#
#          Prerrequisite:  None
# 
#                   Note:  This will NOT modify the original inputDataList.
#
#                  Input:  inputDataList(list), percentToTrim(int or float), 
#
#           Return  Type:  status(int), trimmedAvg(float)
#
#######################################################################################################################

def trimmedAverage( inputDataList, percentToTrim ):
   DEBUG = ON
   if DEBUG == ON:
      objMsg.printMsg("\n\n\n")
   status = NOT_OK
   trimmedAvg = -65536

   if DEBUG == ON:
      objMsg.printMsg("inputDataList: %s" % ( inputDataList ))

   oUtility = Utility.CUtility()
   tmpList = oUtility.copy( inputDataList )
   tmpList.sort()

   if DEBUG == ON:
      objMsg.printMsg("original tmpList: %s" % ( tmpList ))
   if DEBUG == ON:
      objMsg.printMsg("percentToTrim: %s" % ( percentToTrim ))

   numToTrim = 2 * int( len( tmpList ) * (percentToTrim / 100.0) )
   if DEBUG == ON:
      objMsg.printMsg("number of points to discard: %s" % ( numToTrim ))

   if (len(tmpList) - numToTrim) < 4:
      return NOT_OK, trimmedAvg


   while (numToTrim >= 2):
      if DEBUG == ON:
         objMsg.printMsg("going to pop: %s" % ( tmpList[0] ))
      tmpList.pop(0)
      if DEBUG == ON:
         objMsg.printMsg("going to pop: %s" % ( tmpList[-1] ))
      tmpList.pop()
      numToTrim -= 2


   if DEBUG == ON:
      objMsg.printMsg("tmpList: %s" % ( tmpList ))

   if len(tmpList) >= 1:
      trimmedAvg = mean(tmpList)    # mean() is guaranteed to return a float
      status = OK

   if DEBUG == ON:
      objMsg.printMsg("final numToTrim: %s" % ( numToTrim ))
   if DEBUG == ON:
      objMsg.printMsg("final tmpList: %s" % ( tmpList ))

   if DEBUG == ON:
      objMsg.printMsg("\n\n\n")

   return status, trimmedAvg


#######################################################################################################################
#
#          Function:  getTrimmedMean
#
#   Original Author:  Michael T. Brady
#
#       Description:  determine if the mean changed?
#
#             Input:  xList(list), trimPercentage(float)
#
#      Return Value:
#
#######################################################################################################################

def getTrimmedMean( xList, trimPercentage ):

   status = NOT_OK

   trimPercentage = trimPercentage / 100.0
   if trimPercentage == 0.5:
      objMsg.printMsg("getTrimmedMean/ can not trim all the data.")
      return status, 0.0, 0.0, 0.0, 0.0

   xList.sort()
   n = len(xList)
   nTrim = int( trimPercentage * n )



   # compute Winsorize list
   xListLower = [ xList[nTrim] for local_1 in range(0, nTrim) ]
   xListCenter = xList[nTrim:-nTrim]
   xListUpper = [ xList[-nTrim-1] for local_1 in range(0, nTrim) ]
   xListWinsorized = xListLower + xListCenter + xListUpper

   if (len(xListCenter) < 3):
      objMsg.printMsg("getTrimmedMean/ Not enough data. n=%s" % (n))
      return status, 0.0, 0.0, 0.0, 0.0

   # compute winsorized variance and standard deviation

   trimmedMean = sum( xListCenter ) / float( n - ( 2 * nTrim ))

   WMean = mean( xListWinsorized )

   variance1 = 0.0
   for x in xListWinsorized:
      variance1 += pow((x - WMean ), 2 )
   variance1 = variance1 * float(1 / float(n - 1 ))

   xListWinsorizedStandardDeviation = pow( variance1 , 0.5 )

   # std error on the mean
   sampleErrorOfMean = xListWinsorizedStandardDeviation / float( (1 - (2 * trimPercentage)) * pow(n, 0.5))

   status = OK

   return status, trimmedMean, xListWinsorizedStandardDeviation, variance1, sampleErrorOfMean




class CAFH_Computations(CProcess):
   """
   """
   def __init__(self, ):
      """__init__: Intializes the class level variables.
      """
      CProcess.__init__(self)
      self.dut = objDut

      self.mFSO = FSO.CFSO()
      self.dth = FSO.dataTableHelper()
      self.clearAllCachedTrackInformation()

      self.CONVERT_WORDS_FAILED = -1
      self.UNPACK_BUFFER_FAILED = -2
      self.CUDACOM_CALL_COMPLETELY_FAILED = 14629


      self.INPUT_LOGICAL_TRACK_VALID  = 0
      self.INPUT_NOMINAL_TRACK_VALID  = 1
      self.INPUT_RADIUS_VALID         = 2

   def __del__(self, ):
      self.emptyHIRPscaleOffsetTable()
      

   def getHeaterClr(self, HeaterDac, iHead, cyl, coefs, maxclr_USL):
      """
      Returns the heater only clearance in u" based on the WHIRP equation.

      Equations
      =========
         T = c1 + c2*H + c3*H*H + c4*C + c5*C*H + c6*C*C
      """

      C = self.logicalTrackToNominalTrack(iHead, cyl) / 1000.0

      RdClr = coefs[0] + (coefs[1]*HeaterDac) + (coefs[2]*(HeaterDac**2)) + (coefs[3]*C) + (coefs[4]*C*HeaterDac) + (coefs[5]*(C**2))
      RdClr = self.fromClrToHirpClr(iHead, cyl, RdClr, "RdClr")

      if (RdClr > maxclr_USL):
         objMsg.printMsg('Calculated Clr: %s GREATER THAN maximum: %s' % (str(RdClr), str(maxclr_USL)))
         objMsg.printMsg('Serious error indicating that either WHIRP/HIRP coefficients are incorrect.')
         ScrCmds.raiseException(11200, "Calculated Clr GREATER THAN maximum possible value!")

      if DEBUG == 1:
         objMsg.printMsg('getHeaterClr/HeaterDac:%s, cyl:%s, RdClr:%s' % (str(HeaterDac), str(cyl), str(RdClr)), objMsg.CMessLvl.VERBOSEDEBUG)
         objMsg.printMsg('getHeaterClr/coefs  : %s' % str(coefs), objMsg.CMessLvl.VERBOSEDEBUG)

      return(RdClr)


   def SolveForHeat(self, T, iHead, cyl, coefs, minDAC, maxDAC):
      """
      Returns the calculated heater DAC setting to achieve target clearance acutation

      @param T: target clearance actuation
      @param C: physical cylinder / 1000.0
      @param H: heater DAC value

      Equations
      =========
         T = c1 + c2*H + c3*H*H + c4*C + c5*C*H + c6*C*C
         0 = c3*H*H + (c2 + c5*C)*H + (c1 + c4*C + c6*C*C - T)
         0 = c3*H*H + b*H + c

      @return: Heater DAC value (preheat or read heat)
      """

      if DEBUG == 1:
         objMsg.printMsg('SolveForHeat/Actuation:%s, cyl:%s' % (str(T), str(cyl)), objMsg.CMessLvl.VERBOSEDEBUG)
         objMsg.printMsg('SolveForHeat/coefs: %s' % str(coefs), objMsg.CMessLvl.VERBOSEDEBUG)

      C = self.logicalTrackToNominalTrack(iHead, cyl) / 1000.0
      T = self.fromHirpClrToClr(iHead, cyl, T, "RdClr")

      c = (coefs[5] * (C**2)
         + coefs[3] * C
         + coefs[0]
         - T)

      b = (coefs[4] * C
         + coefs[1])

      H = int(SolveQuadratic(coefs[2], b, c))
      if DEBUG == 1:
         objMsg.printMsg("H:%s;b:%s;c:%s" % (H, b, c), objMsg.CMessLvl.VERBOSEDEBUG)


      if (H < minDAC):
         objMsg.printMsg('Warning calculated DAC value: %s less than minimum DAC value: %s' % \
            (str(H), str(minDAC)), objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg("H:%s;b:%s;c:%s" % (H, b, c), objMsg.CMessLvl.VERBOSEDEBUG)
         H = minDAC

      if (H > (2 * maxDAC)):
         objMsg.printMsg("Requested calculated heater actuation: %s GREATER THAN 2*maximum: %s" % (str(H), str(2 * maxDAC)))
         ScrCmds.raiseException(11200, "Requested calculated heater actuation GREATER THAN 2*maximum")

      if (H > maxDAC):
         objMsg.printMsg('Warning calculated DAC value: %s greater than maximum DAC value: %s' % \
            (str(H), str(maxDAC)), objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg("H:%s;b:%s;c:%s" % (H, b, c), objMsg.CMessLvl.VERBOSEDEBUG)
         H = maxDAC

      return(H)


   def CalcClearanceLoss(self, iHead, cyl, freq, Iw, Ovs, Osd, coefs):
      """
      Calculate the clearance loss due to write protrusion
      """
      C = self.logicalTrackToNominalTrack(iHead, cyl) / 1000.0

      if DEBUG == 1:
         objMsg.printMsg(str(coefs))
      freq = float(freq)/1000.0
      Iw = int(Iw)
      Ovs = int(Ovs)
      Osd = int(Osd)
      clrLoss = coefs[0] + (coefs[1]*C) + (coefs[2]*(C**2)) \
         + (coefs[3]*freq) + (coefs[4]*freq*C) + (coefs[5]*freq**2) \
         + (coefs[6]*Iw) + (coefs[7]*C*Iw) + (coefs[8]*Iw*freq) + (coefs[9]*Iw**2) \
         + (coefs[10]*Ovs) + (coefs[11]*C*Ovs) + (coefs[12]*Ovs*freq) + (coefs[13]*Ovs*Iw) + (coefs[14]*Ovs**2)

      if len(coefs) in [21, 22]:
         # The reason there could be 22 items in the list is that there could be an additional item of a string value
         # representing the nominal logical trk mode labeled AFH_Uniform_Track_Lbl in the TestParameters.
         clrLoss = coefs[0] + (coefs[1]*C) + (coefs[2]*(C**2)) + \
         (coefs[3]*freq) + (coefs[4]*freq*C) + (coefs[5]*freq**2) + \
         (coefs[6]*Iw) + (coefs[7]*C*Iw) + (coefs[8]*Iw*freq) + (coefs[9]*Iw**2) + \
         (coefs[10]*Ovs) + (coefs[11]*C*Ovs) + (coefs[12]*Ovs*freq) + (coefs[13]*Ovs*Iw) + (coefs[14]*Ovs**2) + \
         (coefs[15]*Osd) + (coefs[16]*Osd*C) + (coefs[17]*Osd*freq) + (coefs[18]*Osd*Iw) + (coefs[19]*Osd*Ovs) + (coefs[20]*Osd**2)

      clrLoss = self.fromWriteLossToHirpWriteLoss(iHead,cyl,clrLoss)
      return(clrLoss)


   def getWriteClr(self, iHead, cyl, coefs, writeLoss, HeaterDac, maxclr_USL):
      """
      Return the write clearance in u"
      Equations
      =========
         T = c1 + c2*C + c3*C*C + c4*H + c5*C*H + c6*H*H + c7*writeLoss + c8*C*writeLoss + c9*writeLoss*H + c10*writeLoss*writeLoss

      Note:  Do NOT pass HirpWriteLoss to this function.  writeLoss is not recalculated for computational reasons.
      """
      C = self.logicalTrackToNominalTrack(iHead, cyl) / 1000.0

      WHClr = coefs[0] + (coefs[1]*C) + (coefs[2]*(C**2)) + (coefs[3]*HeaterDac) + (coefs[4]* C * HeaterDac) \
          + (coefs[5]*(HeaterDac**2)) + (coefs[6]*writeLoss) + (coefs[7]*C*writeLoss) + (coefs[8]*writeLoss*HeaterDac) + (coefs[9]*(writeLoss**2))
      WHClr = self.fromClrToHirpClr(iHead, cyl, WHClr, "WrtClr")

      if (WHClr > maxclr_USL):
         objMsg.printMsg('Calculated Clr: %s GREATER THAN maximum: %s' % (str(WHClr), str(maxclr_USL)))
         objMsg.printMsg('Serious error indicating that either WHIRP/HIRP coefficients are incorrect.')
         ScrCmds.raiseException(11200, "Calculated Clr GREATER THAN maximum possible value!")

      if DEBUG == 1:
         objMsg.printMsg('getWriteClr/W+HDac:%s, cyl:%s, writeLoss:%s, WHClr:%s' % (str(HeaterDac), str(cyl), str(writeLoss), str(WHClr)), objMsg.CMessLvl.VERBOSEDEBUG)
         objMsg.printMsg('getWriteClr/coefs  : %s' % str(coefs), objMsg.CMessLvl.VERBOSEDEBUG)

      return(WHClr)



   def SolveForWriteHeat(self, T, iHead, cyl, coefs, writeLoss, minDAC, maxDAC):
      """
      Returns the calculated write DAC setting to achieve target clearance acutation
      @return: Write heater DAC value

      @param T: target clearance actuation
      @param writeLoss: clearance loss due to writing
      @param C: physical cylinder / 1000.0
      @param H: write heater DAC value

      Equations
      =========
         T = c1 + c2*C + c3*C*C + c4*H + c5*C*H + c6*H*H + c7*writeLoss + c8*C*writeLoss + c9*writeLoss*H + c10*writeLoss*writeLoss
         0 = c6*H*H + (c4 + c5*C + c9*writeLoss)*H + (c1 + c2*C + c3*C*C + c7*writeLoss + c8*C*writeLoss + c10*writeLoss*writeLoss - T)
         0 = c6*H*H + b*H + c

      Note:  Do NOT pass HirpWriteLoss to this function.  writeLoss is not recalculated for computational reasons.

      """
      T = self.fromHirpClrToClr(iHead, cyl, T, "WrtClr")

      C = self.logicalTrackToNominalTrack(iHead, cyl) / 1000.0

      c = (coefs[9] * (writeLoss**2)
         + coefs[7] * C * writeLoss
         + coefs[6] * writeLoss
         + coefs[2] * (C**2)
         + coefs[1] * C
         + coefs[0]
         - T)

      b = (coefs[8] * writeLoss
         + coefs[4] * C
         + coefs[3])


      H = int(SolveQuadratic(coefs[5], b, c))

      if DEBUG == 1:
         objMsg.printMsg("H:%s;b:%s;c:%s;writeLoss:%s;T:%s" % (H, b, c, writeLoss, T), objMsg.CMessLvl.DEBUG)

      if (H < minDAC):
         objMsg.printMsg('Warning calculated DAC value: %s less than minimum DAC value: %s' % \
            (str(H), str(minDAC)), objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg("H:%s;b:%s;c:%s;writeLoss:%s;T:%s" % (H, b, c, writeLoss, T), objMsg.CMessLvl.DEBUG)
         H = minDAC

      if (H > (2 * maxDAC)):
         objMsg.printMsg("Requested calculated heater actuation: %s GREATER THAN 2*maximum: %s" % (str(H), str(2 * maxDAC)))
         ScrCmds.raiseException(11200, "Requested calculated heater actuation GREATER THAN 2*maximum")

      if (H > maxDAC):
         objMsg.printMsg('Warning calculated DAC value: %s greater than maximum DAC value: %s' % \
            (str(H), str(maxDAC)), objMsg.CMessLvl.IMPORTANT)
         objMsg.printMsg("H:%s;b:%s;c:%s;writeLoss:%s;T:%s" % (H, b, c, writeLoss, T), objMsg.CMessLvl.DEBUG)
         H = maxDAC

      return( H )

   def fromClrToHirpClr(self, iHead, iZone, Clr, ClrType, verbose = 0):
      if ClrType == 'RdClr':
         return (self.scaleOffsetTable[iHead][iZone][READ_SCALING] * Clr) + self.scaleOffsetTable[iHead][iZone][READ_OFFSET]
      elif ClrType == 'WrtClr':
         return (self.scaleOffsetTable[iHead][iZone][WRITE_SCALING] * Clr) + self.scaleOffsetTable[iHead][iZone][WRITE_OFFSET]
      else:
         ScrCmds.raiseException(11044, "AFH - invalid Clr type: %s passed to fromClrToHirpClr " % str(ClrType))

   def fromClrToInDrvAdjClr(self, iHead, trk, Clr, ClrType, verbose = 0):
      iZone = self.mFSO.trackToZone(iHead, trk)
      if ClrType == 'WrtClr':
         deltaWL = self.getDeltaWrtClr(iHead, iZone)
      else:
         ScrCmds.raiseException(11044, "AFH - invalid Clr type: %s passed to fromClrToInDrvAdjClr " % str(ClrType))
      WrtClr = Clr - deltaWL
      if verbose != 0:
         objMsg.printMsg("iHead: %2s, trk: %8s, Clr: %0.6f, deltaWL:%s, WrtClr: %s " % \
         (iHead, trk, Clr, deltaWL, WrtClr), objMsg.CMessLvl.DEBUG)
      return WrtClr

   def fromWriteLossToHirpWriteLoss(self, iHead, trk, writeLoss, verbose = 0):
      iZone = self.mFSO.trackToZone(iHead, trk)
      scale, offset = self.getHirpWriteScaleOffset(iHead, iZone)
      HirpWriteLoss = scale * writeLoss
      if verbose != 0:
         objMsg.printMsg("iHead: %2s, trk: %8s, writeLoss: %0.6f, scale:%s, HirpWriteLoss: %s " % \
         (iHead, trk, writeLoss, scale, HirpWriteLoss), objMsg.CMessLvl.DEBUG)
      return HirpWriteLoss

   def fromHirpWriteLossToWriteLoss(self, iHead, trk, HirpWriteLoss, verbose = 0):
      iZone = self.mFSO.trackToZone(iHead, trk)
      scale, offset = self.getHirpWriteScaleOffset(iHead, iZone)
      writeLoss = float(HirpWriteLoss / float(scale))
      if verbose != 0:
         objMsg.printMsg("iHead: %2s, trk: %8s, writeLoss: %0.6f, scale:%s, HirpWriteLoss: %s " % \
         (iHead, trk, writeLoss, scale, HirpWriteLoss), objMsg.CMessLvl.DEBUG)
      return writeLoss


   def fromHirpClrToClr(self, iHead, iZone, HirpClr, ClrType, verbose = 0):
      if ClrType == 'RdClr':
         return (HirpClr - self.scaleOffsetTable[iHead][iZone][READ_OFFSET])/self.scaleOffsetTable[iHead][iZone][READ_SCALING]
      elif ClrType == 'WrtClr':
         return (HirpClr - self.scaleOffsetTable[iHead][iZone][WRITE_OFFSET])/self.scaleOffsetTable[iHead][iZone][WRITE_SCALING]
      else:
         ScrCmds.raiseException(11044, "AFH - invalid Clr type: %s passed to fromHirpClrToClr " % str(ClrType))

   def getHirpReadScaleOffset(self, iHead, iZone):
      sclOffTbl = self.dut.dblData.Tables('P172_CLR_COEF_ADJ').tableDataObj()
      scale = float(self.dth.getRowFromTable(sclOffTbl, iHead, iZone)['READ_SCALING'])
      offset = float(self.dth.getRowFromTable(sclOffTbl, iHead, iZone)['READ_OFFSET'])

      if ( testSwitch.extern.FE_0140583_341036_AFH_TABLE_OUTPUT_ANGSTROMS == 1) and \
         (not ( testSwitch.extern.CLEARANCE_IN_ANGSTROMS == 1)) and \
         (not ( testSwitch.AFH_ENABLE_ANGSTROMS_SCALER_USE_254 == 1)):
         from AFH_constants import AFH_MICRO_INCHES_TO_ANGSTROMS
         offset = float(offset) / float(AFH_MICRO_INCHES_TO_ANGSTROMS)

      return scale, offset


   def getHirpWriteScaleOffset(self, iHead, iZone):
      sclOffTbl = self.dut.dblData.Tables('P172_CLR_COEF_ADJ').tableDataObj()
      scale = float(self.dth.getRowFromTable(sclOffTbl, iHead, iZone)['WRITE_SCALING'])
      offset = float(self.dth.getRowFromTable(sclOffTbl, iHead, iZone)['WRITE_OFFSET'])

      if ( testSwitch.extern.FE_0140583_341036_AFH_TABLE_OUTPUT_ANGSTROMS == 1) and \
         (not ( testSwitch.extern.CLEARANCE_IN_ANGSTROMS == 1)) and \
         (not ( testSwitch.AFH_ENABLE_ANGSTROMS_SCALER_USE_254 == 1)):
         from AFH_constants import AFH_MICRO_INCHES_TO_ANGSTROMS
         offset = float(offset) / float(AFH_MICRO_INCHES_TO_ANGSTROMS)

      return scale, offset

   def buildHirpScaleOffsetTable(self):
      if testSwitch.extern.FE_0140583_341036_AFH_TABLE_OUTPUT_ANGSTROMS and not testSwitch.extern.CLEARANCE_IN_ANGSTROMS and not testSwitch.AFH_ENABLE_ANGSTROMS_SCALER_USE_254:
         AFH_UNIT_ADJUSTMENT = float(AFH_MICRO_INCHES_TO_ANGSTROMS)
      else:
         AFH_UNIT_ADJUSTMENT = 1.0

      clrCoefAdjTable = self.dut.dblData.Tables('P172_CLR_COEF_ADJ').tableDataObj()

      self.scaleOffsetTable = [[() for zone in range(self.dut.numZones) ] for head in range(self.dut.imaxHead)]
      for row in clrCoefAdjTable:
         if int(row['DATA_ZONE']) < self.dut.numZones:
            self.scaleOffsetTable[int(row['HD_LGC_PSN'])][int(row['DATA_ZONE'])] = \
                                   (float(row['READ_SCALING']), \
                                    float(row['READ_OFFSET'])/AFH_UNIT_ADJUSTMENT, \
                                    float(row['WRITE_SCALING']), \
                                    float(row['WRITE_OFFSET'])/AFH_UNIT_ADJUSTMENT)

      self.dut.dblData.delTable('P172_CLR_COEF_ADJ')
      del clrCoefAdjTable

   def emptyHIRPscaleOffsetTable (self):
      for headData in self.scaleOffsetTable:
         del headData[:]
      del self.scaleOffsetTable[:]
      del self.scaleOffsetTable

   def getDeltaWrtClr(self, iHead, iZone):
      deltaWrtLossTbl = self.dut.dblData.Tables('P192_DELTA_WL').tableDataObj()
      deltaWL = float(self.dth.getRowFromTable(deltaWrtLossTbl, iHead, iZone,'ZN_PSN','HD_PHYS_PSN')['DELTA_WL'])
      if deltaWL < -100 or deltaWL > 100:
         deltaWL = 0
      return deltaWL
   # when updating the methods in __ make sure to update apply_HIRP_adjustment_retroactively_to_frames in AR.py
   def __lwords(self, the_lword):
      the_lword = int(the_lword)
      """
      @return: tuple of words from long/double word
      """
      return (((the_lword>>16)&0xFFFF), the_lword&0xFFFF)



   def clearAllCachedTrackInformation(self,):
      self.logical2Nominal = {}
      self.nominal2Logical = {}
      self.nominal2Radius = {}

   def logicalTrackToNominalTrack(self, iHead, lTrack, uniformTrack = 1):
      lTrack = int(lTrack)

      key = str(iHead) + "-" + str(lTrack)  # consider making this %2d-%8d
      if key in self.logical2Nominal.keys():
         return self.logical2Nominal[key]
      if testSwitch.virtualRun:
         nominalTrk = int(lTrack + 1)
      else:
         # So for performance, 1st try cudacom and then try rely on test 49 if all else fails.
         try:
            buf, result, errorCode = self.cudacomTrkConversionUpperLevel(iHead, lTrack, self.INPUT_LOGICAL_TRACK_VALID)
            nominalTrk = result[self.INPUT_NOMINAL_TRACK_VALID]
         except:
            self.St({'test_num':49, 'prm_name':'LogicalToNominal', 'timeout': 200, 'CWORD1': (8,), 'TEST_HEAD': iHead, 'HT_ONLY_TEST_CYL':self.oUtility.ReturnTestCylWord(lTrack),  'ACCESS_TYPE': (1)})
            trkConvTbl = self.dut.dblData.Tables('P049_TRACK_CONVERT').tableDataObj()
            nominalTrk = int(self.dth.getRowFromTable_byHead(trkConvTbl, iHead)['NOMINAL_CYL'])
      self.logical2Nominal[key] = nominalTrk
      return self.logical2Nominal[key]



   def NominalTrackTologicalTrack(self, iHead, uTrack, uniformTrack = 1):
      uTrack = int(uTrack)

      key = str(iHead) + "-" + str(uTrack)
      if key in self.nominal2Logical.keys():
         return self.nominal2Logical[key]


      if testSwitch.virtualRun:
         logicalTrk = int(uTrack - 1)
      else:
         try:
            buf, result, errorCode = self.cudacomTrkConversionUpperLevel(iHead, uTrack, self.INPUT_NOMINAL_TRACK_VALID)
            logicalTrk = result[self.INPUT_LOGICAL_TRACK_VALID]
         except:
            self.St({'test_num':49, 'prm_name':'NominalToLogical', 'timeout': 200, 'CWORD1': (8,), 'TEST_HEAD': iHead,  'HT_ONLY_TEST_CYL':self.oUtility.ReturnTestCylWord(uTrack), 'ACCESS_TYPE': (0)})
            trkConvTbl = self.dut.dblData.Tables('P049_TRACK_CONVERT').tableDataObj()
            logicalTrk = int(self.dth.getRowFromTable_byHead(trkConvTbl, iHead)['RW_LOGICAL_CYL'])

      self.nominal2Logical[key] = logicalTrk
      return self.nominal2Logical[key]


   def UniformTrackToRadius(self, iHead, uTrack, uniformTrack = 1):
      uTrack = int(uTrack)
      if testSwitch.virtualRun:
         return radius

      buf, result, errorCode = self.cudacomTrkConversionUpperLevel(iHead, uTrack, 2)

      if errorCode != 0:
         if not uniformTrack:
            objMsg.printMsg("Uniform to radius query failed.")
            return -1.0
         else:
            ScrCmds.raiseException(errorCode,"NominalTrackTologicalTrack/ cudacom 1370 failed for track %s" % uTrack)

      radiusQ4_milli_inches = result[self.INPUT_RADIUS_VALID]
      radius_milli_inches = radiusQ4_milli_inches / 16.0      # Divide by 16 because radiusQ4_milli_inches is a Q4 number
      radius = radius_milli_inches / 1000.0
      return radius



   def cudacomTrkConversionUpperLevel(self, iHead, genericTrk, conversionType):
      retryLimit = 10
      retry = 0
      errorCode = self.UNPACK_BUFFER_FAILED
      badErrorCodeStatus = [self.CONVERT_WORDS_FAILED, self.UNPACK_BUFFER_FAILED, self.CUDACOM_CALL_COMPLETELY_FAILED, 10264]
      while (retry < retryLimit) and (errorCode in badErrorCodeStatus):
         buf, result, errorCode = self.cudacomTrkConversionLowerLevel(iHead, genericTrk, conversionType)
         objMsg.printMsg("cudacomTrkConversionUpperLevel/ retry: %s.  INPUT Hd: %s, genericTrk: %s, conversionType: %s OUTPUT Buffer: %s, result: %s, errorCode: %s" % \
            (retry,iHead, genericTrk, conversionType, binascii.hexlify(buf), result, errorCode ))
         retry += 1
      return buf, result, errorCode


   def cudacomTrkConversionLowerLevel(self, iHead, genericTrk, conversionType):
      # 1.) Convert Track from track decimal to 2 words
      objCudacom = CCudacom()
      mCylinder, lCylinder = self.__lwords(genericTrk)   # a generic trk could be logical or nominal or a radius
      try:
         objCudacom = CCudacom()
         mCylinder, lCylinder = self.__lwords(genericTrk)   # a generic trk could be logical or nominal or a radius
      except:
         objMsg.printMsg("cudacomTrkConversionUpperLevel/__lwords conversion failed!")
         return [], [], self.CONVERT_WORDS_FAILED

      #2.) Call cudacom command 1370, suppress failure if call completely failed to return data
      try:
         buf, errorCode = objCudacom.Fn(1370, lCylinder, mCylinder, iHead, conversionType)
      except:
         objMsg.printMsg("cudacomTrkConversionLowerLevel/ Cudacom 1370 call completely failed!  No data was returned." )
         return [], [], self.CUDACOM_CALL_COMPLETELY_FAILED

      #3.) Cudacom command returned an error code
      if errorCode != 0:
         return buf, [], errorCode

      #4.) try to decode buffer
      try:
         result = struct.unpack(">LLH", buf)
         if DEBUG == 1:
            objMsg.printMsg("Logical Trk : %u, Nominal Logical Trk: %u, (radius inches: %0.3f) " % \
            (result[0], result[1], (result[2]/(16.0*1000.0))), objMsg.CMessLvl.DEBUG)
      except:
         return buf, [], self.UNPACK_BUFFER_FAILED

      #5.) it actually worked correctly
      return buf, result, errorCode


   def nominalCylTrkList2logicalCylTrkList(self, iHead, nominalTrkList, uniformTrkMode):
      logicalTrkList = []
      for nominalCyl in nominalTrkList:
         logicalTrkList.append(self.NominalTrackTologicalTrack(iHead, nominalCyl, uniformTrkMode))
      return logicalTrkList
