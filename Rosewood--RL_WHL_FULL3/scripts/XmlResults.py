#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: XML Results
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/XmlResults.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/XmlResults.py#1 $
# Level:3
#---------------------------------------------------------------------------------------------------------#
from Constants import *

class XmlResultsTagContent:

    """
    Class used to store individual objects in an XmlResultsFile object.  Intelligently adds objects.
    """

    def __init__(self, initialXmlObj = ''):

        """
        Instantiate a XmlResultsTagContent object from a passed in object.  The entire object is saved.
        """

        if hasattr(initialXmlObj, '__add__'):
            self.__xmlContent = initialXmlObj
        else:
            self.__xmlContent = str(initialXmlObj)

    def __add__(self, other):

        """
        Add these two objects together.  First attempt to use the __add__ methods, otherwise, add their
        string representations (returned by __str__ method) together.  Will throw an exception if either
        object doesn't properly support __str__.
        """

        try:
            self.__xmlContent += other
        except:
            self.__xmlContent = str(self.__xmlContent) + str(other)

        return self

    def __str__(self):

        """
        Return the string representation of the stored object
        """

        return str(self.__xmlContent)


class XmlResults:

    """
    This is a very simple class meant to be instantiated once at the beginning of a script operation.  It provides
    a buffered interface to the Gemini XML Results file.  Note that to minimize memory footprint, this class
    should only be used in cases where an XML entry in the results file MUST be buffered.
    """

    def __init__(self):

        # TagObjectDict will be used to store the individual XmlResultsTagContent objects defined for each XML tag specified
        self.TagObjectDict = {}

    def addInstance(self, tagName, newInstance):

        """
        Used to add an object to the internal XML tag => object dictionary.  If an object already exists under
        the tag name provided, first we'll attempt to add the objects (by using the passed object's __add__
        method).  If this doesn't work, or if the __add__ method doesn't exist, then we'll add the objects
        using the results of the __str__ method.  Note that __str__ MUST be defined for newInstance.
        """

        if (self.TagObjectDict.has_key(tagName)):
            self.TagObjectDict[tagName] += newInstance
        else:
            self.TagObjectDict[tagName] = XmlResultsTagContent(newInstance)

    def __str__(self):

        """
        Return the string that will be used in the XML results file.  This iterates over the internal
        XML tag dictionary outputting one entry for each XML tag => object pair.
        """

        finalXml = ''

        for tagName, tagObjectInstance in self.TagObjectDict.items():
            finalXml += ("<%s>" % tagName)
            finalXml += str(tagObjectInstance)
            finalXml += ("</%s>" % tagName)

        return finalXml
