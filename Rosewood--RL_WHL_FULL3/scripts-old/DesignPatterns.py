#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: The Rim object is an abstraction of the cell RIM and implements methods to implement
#              to power on/off rim, download CPC/NIOS/Serial code etc.
#              Note that only once instance of rim must exist in the entire test environment.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DesignPatterns.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/DesignPatterns.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
class Borg(object):
   """
   Base object to inherit from to create a borg object which implements a shared state
      so instances can share class variables.s
   """
   _shared_state = {}

   def __new__(cls, *a, **k):
      obj = object.__new__(cls, *a, **k)
      obj.__dict__ = cls._shared_state
      return obj



class Singleton(object):
   """
   Base object to inherit from to implement a singleton object or only 1 instance is ever created through
      inheritance or instantiation
   """
   def __new__(cls, *args, **kwargs):
      if '_inst' not in vars(cls):
         cls._inst = super(Singleton, cls).__new__(cls, *args, **kwargs)
      else:
         def __dummyFunc(cls, *args, **kwargs):pass
         cls.__init__ = __dummyFunc
      return cls._inst

class Null(object):
    """A class for implementing Null objects.
    Copied from http://code.activestate.com/recipes/68205/

    This class ignores all parameters passed when constructing or
    calling instances and traps all attribute and method requests.
    Instances of it always (and reliably) do 'nothing'.

    The code might benefit from implementing some further special
    Python methods depending on the context in which its instances
    are used. Especially when comparing and coercing Null objects
    the respective methods' implementation will depend very much
    on the environment and, hence, these special methods are not
    provided here.
    """
    __slots__ = []

    # object constructing

    def __init__(self, *args, **kwargs):
        "Ignore parameters."
        return None

    # object calling

    def __call__(self, *args, **kwargs):
        "Ignore method calls."
        return self

    # attribute handling

    def __dir__(self):
       return []

    def __getattr__(self, mname):
        "Ignore attribute requests."
        return self

    def __setattr__(self, name, value):
        "Ignore attribute setting."
        return self

    def __delattr__(self, name):
        "Ignore deleting attributes."
        return self

    # misc.

    def __repr__(self):
        "Return a string representation."
        return ""

    def __str__(self):
        "Convert to a string and return it."
        return ""

if __name__ == "__main__":
   import gc
   class mycls(Singleton):
      def __init__(self):
         self.name = str(id(self))

      def __del__(self):
         print "deleting %s" % self.name

   m = mycls()
   print m.name
   del m
   gc.collect()
   n = mycls()
   print n.name

   x = Null()
   print dir(x)