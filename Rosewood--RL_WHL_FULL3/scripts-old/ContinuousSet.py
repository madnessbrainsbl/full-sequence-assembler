# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
import types



class cSet(object):
   def __init__(self, *args):
      if len(args) == 1:
         interable = args[0]
      else:
         iterable = args

      if iterable == None or iterable in [(),[]]:
         self.start = None
         self.end = None
      else:
         #if not type(iterable) in [types.TupleType, types.ListType]:
         #   raise TypeError, "Input must be a sequence type."

         if len(iterable) != 2:
            raise AttributeError, "Input must be a start and end integer range not '%s'." % (iterable,)

         self.start = min(iterable)
         self.end = max(iterable)

   def __len__(self):

      try:
         return self.end - self.start
      except:
         return 0

   def __iter__(self):
      for i in [self.start, self.end]:
         yield i

   def __str__(self):
      return "cSet([%d,%d])" % (self.start, self.end)

   def copy(self):
      return cSet(self.start, self.end)

   def update(self, sequence):
      self.start = min(self.start, min(sequence))
      self.end = max(self.end, max(sequence))

   def union(self, sequence):
      return cSet(min(self.start, min(sequence)), max(self.end, max(sequence)))

   def split(self, boundry):
      """
      Function splits its current continuous set into sub sets of equal length divided
         at boundry.
      """
      if (self.end - self.start) < boundry:
         return [self,]

      spans = []
      start = self.start
      end = self.start+ boundry #dummy val to start loop
      while end <= self.end:
         spans.append(cSet(start, end))
         start += boundry + 1
         end = start + boundry

      if start < self.end and end > self.end:
         spans.append(cSet(start, self.end))

      return spans


   def intersection(self, sequence):
      intersect = cSet()
      if self.end < min(sequence) or self.start > max(sequence): #check null intersections first
         return intersect

      if self.start <= min(sequence):
         intersect.start = min(sequence)
      else:
         intersect.start = self.start

      if self.end <= max(sequence):
         intersect.end = self.end
      else:
         intersect.end = max(sequence)

      return intersect

if __name__ == "__main__":
   cSet()