#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description:
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Interpolator.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Interpolator.py#1 $
# Level: 3
#---------------------------------------------------------------------------------------------------------#
from Constants import *
class CPolynomialInterpolator:
   """
      Note that input data must be a list of (x,y) format tuples and in proper order
      e.g [(-1.5,-14.1014), (-0.75,-0.931596), (0,0), (0.75,0.931596), (1.5,14.1014)]
   """
   lagrangeType = 'Lagrange'
   newtonType = 'Newton'

   def __init__(self, data):
      self.data = data
      self.order = len(self.data) - 1
      #print self.data
      #print 'polynomial order = ', self.order

   """
      Construct to call instance like a normal function, Lagrange or Newton form may be specified as input arg
      Default is to use the Lagrange basis, since it is simpler to execute, as Newton form uses recursive calls
   """
   def __call__(self, x, type='Lagrange'):
      return self.calc(x, type)

   """
      Main function to calculate the value of f(x) for any interpolating point x
   """
   def calc(self, x, type='Lagrange'):
      f_of_x = 0
      if self.order > 0:
         for j in range(self.order+1):
            if type == 'Newton':
               f_of_x +=  self.__newtonCoeff(j) * self.__newtonBasis(j, float(x))
            else:
               f_of_x +=  self.__lagrangeCoeff(j) * self.__lagrangeBasis(j, float(x))
      return f_of_x

   def getPoly(self, type):
      """
      @return: List of polynomial coefficients lowest order 1st
      """
      tupOut = []
      for j in range(self.order+1):
         if type == 'Newton':
            tupOut.append(self.__newtonCoeff(j))
         else:
            tupOut.append(self.__lagrangeCoeff(j))
      return tupOut

   """
      Returns the Lagrange basis polynomial for index j and input data point x
   """
   def __lagrangeBasis(self, j, x):
      l_of_x = 1
      xj = self.data[j][0]
      for i in range(self.order+1):
         if i != j:
            xi = self.data[i][0]
            l_of_x = l_of_x * ((x - xi)/(xj - xi))
      return l_of_x

   """
      Returns the coefficient for the Lagrange form
   """
   def __lagrangeCoeff(self, j):
      return self.data[j][1]

   """
      Calculates the Newton basis polynomial for index j and input data point x
   """
   def __newtonBasis(self, j, x):
      n_of_x = 1
      for i in range(j):
         xi = self.data[i][0]
         n_of_x = n_of_x * (x - xi)
      return n_of_x

   """
      Calculates the coefficient for the Newton basis
   """
   def __newtonCoeff(self, j):
      data = [self.data[i] for i in range(j+1)]
      value = self.__dividedDiff(data)
      return value

   """
      Recursive function to calculate divided differences for Newton basis
   """
   def __dividedDiff(self, data):
      n = len(data)
      if n == 1:
         return float(data[0][1])
      if n == 2:
         return ( float((data[1][1] - data[0][1])) / float((data[1][0] - data[0][0])) )
      data_a = [data[i] for i in range(1, n)]
      data_b = [data[i] for i in range(0, n-1)]
      value = ((self.__dividedDiff(data_a) - self.__dividedDiff(data_b)) / (data[n-1][0] - data[0][0]))
      return value


############################################################################################################
# TESTING/DEBUG Here
############################################################################################################
#data_list = [(22.0,0.45), (53.0,0.33)]#, (75.0,.12)]
#m = CPolynomialInterpolator(data_list)
#
#check_point = 0
#print 'Checking for x-point = ', check_point
#print 'Lagrange Interpolator Result = ', m(check_point)
#print 'Newton Interpolator Result = ', m(check_point, 'Newton')
#
#print(m.getPoly(m.newtonType))
#print(m.getPoly(m.lagrangeType))

# Pylab plotting for comparison (red plot is original curve, blue is the interpolated curve based on x-points below)
#new_x_points = [-1.5, -0.8, 0, 0.8, 1.5]
#list_y_Lagrange = []
#for item in new_x_points:
#   list_y_Lagrange.append(m.calc(item))
#
# import pylab
# pylab.clf()
# pylab.plot([data_list[i][0] for i in range(len(data_list))], [data_list[i][1] for i in range(len(data_list))], 'r--')
# pylab.plot([new_x_points[i] for i in range(len(new_x_points))], [list_y_Lagrange[i] for i in range(len(data_list))], 'b--')
# pylab.grid(1)
# pylab.show()

#---------------------------------------------------------------------------------------------------------#
