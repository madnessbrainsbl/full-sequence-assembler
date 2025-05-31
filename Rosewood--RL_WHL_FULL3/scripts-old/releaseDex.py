# --------------------------------------------------------------------------------------- #
#                                                                                         #
#                                   Seagate Confidential                                  #
#                                                                                         #
# --------------------------------------------------------------------------------------- #

# ******************************************************************************
#
# VCS Information:
#                 $File: //depot/TCO/DEX/releaseDex.py $
#                 $Revision: #6 $
#                 $Change: 639275 $
#                 $Author: alan.a.hewitt $
#                 $DateTime: 2013/12/04 09:50:41 $
#
# ******************************************************************************
#
#  Script to release DEX/DEXRPT.  It zips the files and puts the zip file
#  on a network drive.
#
# *************************************************************************

import getopt,sys,os,zipfile,traceback
import re

RELEASE_TOOL_VERSION = 1.0

DEXFILES = ["dex.py", "dexrpt.py", "dexrptgui.py", "dexChanges.py", "writeresultsfunctions.py", \
           "viewerextractors.py", "rptextractors.py", "resultshandlers.py", "parseresults.py", "parametricextractors.py"]


if __name__ == "__main__":

  errorFlag = False

  # Define a usage summary function
  def usage(errMsg=""):
    msg = """
    ***********************************************************************************
    VERSION: %s

    USAGE:  releaseDex.py -v version -d dexDir -r releaseDir -h
    WHERE:

    OPTION  ARGUMENT       DESCRIPTION

      -v    version        mandatory; version number
      -d    dexDir         optional; directory to pull DEX files from
      -r    releaseDir     optional; directory to put DEX releases
      -h                   optional;  print help menu


    DEFAULT BEHAVIOR:
    - assumes directory for DEX files is c:\mywork\dex
    - assumes release dir is k:\dex_dexrpt
    - assumes a set of python files that should be zipped up

    EXAMPLES:
      releaseDex.py -v 2.06
    ***********************************************************************************
    """ % (RELEASE_TOOL_VERSION)
    print msg
    if errMsg:
      print errMsg
      print ""
    sys.exit()



  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # read & validate command-line args
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  try:
    optList,argList = getopt.getopt(sys.argv[1:], 'v:d:r:h')
  except:
    # Unrecognized option in list or not using required arg with option
    errMsg = "ERROR:  Invalid options"
    usage(errMsg)

  # Set up defaults
  myOptionList = []
  dexDir = 'C:\_Perforce\TCO\DEX'
  releaseDir = "k:\dex_dexrpt"

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # parse command-line args
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  for option,args in optList:
    # The user must pass the version number.
    if option == "-v":
      version = args
    elif option == "-d":
      dexDir = args
    elif option == "-r":
      releaseDir = args
    myOptionList.append(option)

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Check for required args
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  for opt in ["-v"]:
    if opt not in myOptionList:
      errMsg = "ERROR:  %s is a mandatory argument" % (opt)
      usage(errMsg)

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Verify VERSION # is valid
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  errorFlag = False
  if 1:
    versionFileName = "./parseresults.py"
    versionLine = None

    try:
      # print "open", versionFileName
      versionFile = open( versionFileName, "r" ) # open version file (string: VERSION = "#.##")
      try:
        # print "find 'VERSION =' @", versionFileName
        lines = versionFile.readlines()
        for l in lines:
          if l.find("VERSION = ") == 0:
            versionLine = l.strip("\n")
            break
        if versionLine == None:
          errorFlag = True
          print "ERROR! no 'VERSION ='"
      except:
        errorFlag = True
        print "ERROR! parsing '%s' ... no 'VERSION ='" % versionFileName
        versionLine = None
      #  # print "close", versionFileName
      versionFile.close()
    except:
      errorFlag = True
      print "ERROR! '%s' i/o error" % versionFileName
      versionLine = None

    if not errorFlag:
      if versionLine:
        if versionLine.find('"%s"' % version) > 0:
          print "%s it is. here we go..." % version
        else:
          errorFlag = True
          print "ERROR! you silly twit: '-v %s' != '%s' @ %s" % ( version, versionLine, versionFileName )
      else:
        errorFlag = True
        print "ERROR! versionLine = %s" % versionLine

  if not errorFlag:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # source dir exist?
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if not os.path.exists( dexDir ):
      errMsg = "ERROR:  DEX directory %s does not exist" % (dexDir)
      usage(errMsg)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # release dir exist?
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # if os.access( releaseDir, os.F_OK ):
    if not os.path.exists( releaseDir ):
      try:
        os.mkdir( releaseDir )
      except:
        errorFlag = True
        errMsg = "ERROR:  Release directory %s does not exist" % releaseDir
        usage(errMsg)

  if not errorFlag:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ZIP
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    try:
      zipFileName = "v_%s.zip" % version

      # Open a zipe file; truncate & write new if it already exists
      zipFd = zipfile.ZipFile(zipFileName,"w")

      # Create the zipfile based on the list of DEX/DEXRPT files
      for i in os.listdir(dexDir):
        if i in DEXFILES:
          zipFd.write(os.path.join(dexDir, i), i, zipfile.ZIP_DEFLATED)
      zipFd.close()
    except:
      print "ERROR:  Problem creating the zip file."
      print traceback.print_exc()
      sys.exit()

    # If the release directory already exists on the web server, abort.
    fullReleaseDir = os.path.join(releaseDir,"v_%s") % version
    if os.path.exists(fullReleaseDir):
      errMsg = "ERROR:  Release directory %s already exists.  Not copying zip file to release directory." % (fullReleaseDir)
      usage(errMsg)

    os.mkdir(fullReleaseDir)

    cmd = "move %s %s" % (zipFileName,fullReleaseDir)
    err = os.system(cmd)
    if not err:
      print "Release %s completed successfully!" % version
    else:
      print "ERROR: Problem moving zip file %s to release directory %s" % (zipFileName,fullReleaseDir)

