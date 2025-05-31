#!/usr/bin/env fofpython
# --------------------------------------------------------------------------------------- #
#                                                                                         #
#                                   Seagate Confidential                                  #
#                                                                                         #
# --------------------------------------------------------------------------------------- #

# ******************************************************************************
#
# VCS Information:
#                 $File: //depot/TCO/DEX/dexrptgui.py $
#                 $Revision: #4 $
#                 $Change: 805641 $
#                 $Author: alan.a.hewitt $
#                 $DateTime: 2015/01/05 08:40:20 $
#
# ******************************************************************************


from Tkinter import *
from tkFileDialog import askopenfilename, askdirectory
from tkMessageBox import showerror,showinfo
from parseresults import VERSION
import os,string,time,cPickle
import Pmw


class DEXRPTGUI:

  # Constructor
  def __init__(self):

    # Create an object to contain and manage defaults for GUI fields
    self.guiDefaults = GUIDefaults(initialGUIDefaults = {
                                   "startMonth"         : "",
                                   "startDay"           : "",
                                   "startYear"          : "",
                                   "endMonth"           : "",
                                   "endDay"             : "",
                                   "endYear"            : "",
                                   "resultsFile"        : "",
                                   "resultsFileHistory" : [],
                                   "resultsDirHistory"  : [],
                                   "testNumList"        : "",
                                   "spcIDList"          : "",
                                   "serialNumFile"      : "",
                                   "outputDir"          : "",
                                   "outputFile"         : "",
                                   "outputByTable"      : "",
                                   "lastRunOnly"        : "",
                                   "parseViewerTable"   : "",
                                   "printTestTimeTable" : ""},
                                    filename = "dexrptGuiHistory")

    # Create the root widget; must be created before other widgets
    self.root = Tk()

    # Give a title to the GUI Window
    self.root.title("DEXRPT %s" % VERSION)

    # This protocol handler defines what happens when user hits the 'x'
    self.root.protocol('WM_DELETE_WINDOW',self.root.quit)

    # Create the frame and make it visible
    sFrame = Frame(self.root)
    sFrame.pack()

    # Create sub frame
    # This counter is for positioning all the sub frames declared
    frameRowCount = 0
    sFrame1 = Frame(sFrame, bd=3, relief=RIDGE)
    sFrame1.grid(row=frameRowCount,column=0, sticky=W)
    # This counter is for the widgets within the sub frame
    rowCount = 0

    Label(sFrame1, text="One of the following two fields must be filled in:").grid(row=rowCount,sticky=W)
    rowCount += 1

    # Copy the GUI history into a variable that can be used within this program
    self.resultsFileList = self.guiDefaults["resultsFileHistory"]

    self.resultsFileCombo = Pmw.ComboBox(sFrame1,
                                        label_text = "Path to and Name of Results File",
                                        labelpos = 'w',
                                        scrolledlist_items = self.resultsFileList,
                                        entry_width = 35,
                                        dropdown = 1)
    self.resultsFileCombo.grid(row=rowCount)
    self.resultsFileCombo.component('scrolledlist').component('listbox').bind('<Delete>',self.clearCurrentFile)
    self.createButton("Browse",(lambda:self.browseFile(self.resultsFileCombo)),rowCount,1,sFrame1)

    rowCount += 1
    Label(sFrame1, text="OR").grid(row=rowCount,sticky=W)

    rowCount += 1
    self.resultsDirList = self.guiDefaults["resultsDirHistory"]
    self.resultsDirCombo = Pmw.ComboBox(sFrame1,
                                        label_text = "Directory of Results Files",
                                        labelpos = 'w',
                                        scrolledlist_items = self.resultsDirList,
                                        entry_width = 35,
                                        dropdown = 1)
    self.resultsDirCombo.grid(row=rowCount)
    self.resultsDirCombo.component('scrolledlist').component('listbox').bind('<Delete>',self.clearCurrentDir)
    self.createButton("Browse",(lambda:self.browseDir(self.resultsDirCombo)),rowCount,1,sFrame1)

    entries = (self.resultsFileCombo,self.resultsDirCombo)
    Pmw.alignlabels(entries)

    # Redefine sub frame for date drop down boxes; in separate frame from other options for display purposes only
    frameRowCount += 1
    sFrame1 = Frame(sFrame,  bd=10)
    sFrame1.grid(row=frameRowCount,column=0, sticky=W)
    rowCount = 0
    colCount = 0

    Label(sFrame1, text="Options:").grid(row=rowCount,sticky=W)
    rowCount = rowCount + 1

    # Set up values for the drop down boxes
    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    days = []
    for i in range(1,32):
       days.append(i)
    years = [2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020]

    Label(sFrame1, text="Start Date   ").grid(row=rowCount,column=colCount,sticky=W)
    colCount = colCount + 1

    self.startMonthCombo = Pmw.ComboBox(sFrame1,
                                        label_text = "Month",
                                        labelpos = 'w',
                                        scrolledlist_items = months,
                                        dropdown = 1,
                                        entryfield_value = self.guiDefaults["startMonth"],
                                        entry_width = 3)
    self.startDayCombo = Pmw.ComboBox(sFrame1,
                                      label_text = "Day",
                                      labelpos = 'w',
                                      scrolledlist_items = days,
                                      dropdown = 1,
                                      entryfield_value = self.guiDefaults["startDay"],
                                      entry_width = 3)
    self.startYearCombo = Pmw.ComboBox(sFrame1,
                                       label_text = "Year",
                                       labelpos = 'w',
                                       scrolledlist_items = years,
                                       dropdown = 1,
                                       entryfield_value = self.guiDefaults["startYear"],
                                       entry_width = 4)

    entries = [self.startMonthCombo, self.startDayCombo,self.startYearCombo]

    for i in entries:
       i.grid(row=rowCount,column=colCount,sticky=W)
       colCount = colCount + 1
    rowCount = rowCount + 1
    colCount = 0

    Label(sFrame1, text="End Date   ").grid(row=rowCount,column=colCount,sticky=W)
    colCount = colCount + 1

    self.endMonthCombo = Pmw.ComboBox(sFrame1,
                                      label_text = "Month",
                                      labelpos = 'w',
                                      scrolledlist_items = months,
                                      dropdown = 1,
                                      entryfield_value = time.localtime()[1],
                                      entry_width = 3)
    self.endDayCombo = Pmw.ComboBox(sFrame1,
                                    label_text = "Day",
                                    labelpos = 'w',
                                    scrolledlist_items = days,
                                    dropdown = 1,
                                    entryfield_value = time.localtime()[2],
                                    entry_width = 3)
    self.endYearCombo = Pmw.ComboBox(sFrame1,
                                     label_text = "Year",
                                     labelpos = 'w',
                                     scrolledlist_items = years,
                                     dropdown = 1,
                                     entryfield_value = time.localtime()[0],
                                     entry_width = 4)
    entries = [self.endMonthCombo, self.endDayCombo,self.endYearCombo]

    for i in entries:
       i.grid(row=rowCount,column=colCount,sticky=W)
       colCount = colCount + 1


    # Redefine sub frame
    frameRowCount += 1
    sFrame1 = Frame(sFrame,  bd=10)
    sFrame1.grid(row=frameRowCount,column=0, sticky=W)
    rowCount = 0

    self.testNumEntry = Pmw.EntryField(sFrame1,
                                       labelpos = 'w',
                                       value = self.guiDefaults["testNumList"],
                                       label_text = "Test Number List")
    self.testNumEntry.grid(row=rowCount,column=0, sticky=W)

    rowCount += 1
    self.spcIDEntry = Pmw.EntryField(sFrame1,
                                       labelpos = 'w',
                                       value = self.guiDefaults["spcIDList"],
                                       label_text = "SPCID List")
    self.spcIDEntry.grid(row=rowCount,column=0, sticky=W)

    rowCount += 1
    self.serialNumEntry = Pmw.EntryField(sFrame1,
                                       labelpos = 'w',
                                       value = self.guiDefaults["serialNumFile"],
                                       entry_width = 35,
                                       label_text = "Serial Number File")
    self.serialNumEntry.grid(row=rowCount,column=0, sticky=W)
    # Pass lambda function so the address to the function is passed rather than the actual function; passing the actual function will cause it to execute
    self.createButton("Browse",(lambda:self.browseFile(self.serialNumEntry)),rowCount,1,sFrame1)

    rowCount += 1
    self.outputDirEntry = Pmw.EntryField(sFrame1,
                                       labelpos = 'w',
                                       value = self.guiDefaults["outputDir"],
                                       entry_width = 35,
                                       label_text = "Output Directory")
    rowCount += 1
    self.outputDirEntry.grid(row=rowCount,column=0, sticky=W)
    self.createButton("Browse",(lambda:self.browseDir(self.outputDirEntry)),rowCount,1,sFrame1)

    rowCount += 1
    self.outputFileEntry = Pmw.EntryField(sFrame1,
                                       labelpos = 'w',
                                       value = self.guiDefaults["outputFile"],
                                       entry_width = 35,
                                       label_text = "Output File Name")
    self.outputFileEntry.grid(row=rowCount,column=0, sticky=W)
    self.createButton("Browse",(lambda:self.browseFile(self.outputFileEntry)),rowCount,1,sFrame1)


    entries = (self.testNumEntry,self.spcIDEntry,self.serialNumEntry, self.outputDirEntry,self.outputFileEntry,)
    Pmw.alignlabels(entries)

    self.byTable = IntVar()
    rowCount += 1
    self.outputByTableButton = Checkbutton(sFrame1,text="Output File By Table Name", variable=self.byTable)
    self.outputByTableButton.grid(row=rowCount,column=0,sticky=W)
    if self.guiDefaults["outputByTable"] == 1:
      self.outputByTableButton.select()

    self.lastRun = IntVar()
    rowCount += 1
    self.lastRunOnlyButton = Checkbutton(sFrame1,text="Last Run Only", variable=self.lastRun)
    self.lastRunOnlyButton.grid(row=rowCount,column=0,sticky=W)
    if self.guiDefaults["lastRunOnly"] == 1:
      self.lastRunOnlyButton.select()

    self.parseViewer = IntVar()
    rowCount += 1
    self.parseViewerTableButton = Checkbutton(sFrame1,text="Parse All Tables", variable=self.parseViewer)
    self.parseViewerTableButton.grid(row=rowCount,column=0,sticky=W)
    if self.guiDefaults["parseViewerTable"] == 1:
      self.parseViewerTableButton.select()

    self.testTime = IntVar()
    rowCount += 1
    self.testTimeTableButton = Checkbutton(sFrame1,text="Print TEST_TIME_BY_TEST Table", variable=self.testTime)
    self.testTimeTableButton.grid(row=rowCount,column=0,sticky=W)
    if self.guiDefaults["printTestTimeTable"] == 1:
      self.testTimeTableButton.select()


    # Redefine sub frame
    frameRowCount += 1
    sFrame1 = Frame(sFrame, bd=10)
    sFrame1.grid(row=frameRowCount,column=0, sticky=W)
    rowCount = 0

    buttonInfo = [("Run DEXRPT", self.runDexRpt), ("Clear", self.clearFields), ("Help",self.help), ("Quit", self.quit),]

    columnCount = 0
    for name, command in buttonInfo:
      self.createButton(name,command,rowCount,columnCount,sFrame1)
      columnCount += 1

    # Will stay in event loop until the quit method is called
    self.root.mainloop()


  def createButton(self,name,command,row,col,frame):
    bt = Button(frame,text=name,command=command,underline=0,padx=4,pady=4)
    # Invoke() calls the command associated with the button, and flash() redraws button
    bt.bind('<Return>',func=lambda event,bt=bt:bt.flash() or bt.invoke())
    # Bind the upper and lower case first letters of the button title
    bt.bind(name[0].upper(),func=lambda event,bt=bt:bt.flash() or bt.invoke())
    bt.bind(name[0].lower(),func=lambda event,bt=bt:bt.flash() or bt.invoke())
    bt.grid(row=row, column=col)


  def getGuiValues(self):
    # Grab current values from the gui
    self.inputFilePath    = self.resultsFileCombo.get()
    self.inputDirPath     = self.resultsDirCombo.get()
    self.startMonth       = self.startMonthCombo.get()
    self.startDay         = self.startDayCombo.get()
    self.startYear        = self.startYearCombo.get()
    self.endMonth         = self.endMonthCombo.get()
    self.endDay           = self.endDayCombo.get()
    self.endYear          = self.endYearCombo.get()
    self.testNum          = self.testNumEntry.get()
    self.spcIDList        = self.spcIDEntry.get()
    self.serialNumList    = self.serialNumEntry.get()
    self.outputDir        = self.outputDirEntry.get()
    self.outputFile       = self.outputFileEntry.get()
    self.outputByTable    = self.byTable.get()
    self.lastRunOnly      = self.lastRun.get()
    self.parseViewerTable = self.parseViewer.get()
    self.testTimeTable = self.testTime.get()


  def customValidator(self):
    self.startDate = ""
    self.endDate = ""

    # Validate the input field
    if self.inputFilePath and self.inputDirPath:
      showerror("Input File", "Enter Path to and Name of Results File OR Directory of Results Files.  Do not fill in both fields.")
      return 1

    if not self.inputFilePath and not self.inputDirPath:
      showerror("Input File", "Results file name or directory is mandatory.")
      return 1

    if self.inputFilePath:
      self.inputPath = self.inputFilePath
    elif self.inputDirPath:
      self.inputPath = self.inputDirPath

    if not os.path.isfile(self.inputPath) and not os.path.isdir(self.inputPath):
      showerror("Input File", "Results file name or directory is not a valid file or directory.")
      return 1

    # Validate entry for serial number file
    if self.serialNumList:
      if not os.path.isfile(self.serialNumList):
        showerror("Serial Number File", "Serial number file is not a valid file.")
        return 1

    # Valid the starting and ending date
    # If only a startDate is entered, assume end date is today

    # If some but not all date fields have data, raise error to indicate all fields need to be filled in
    if (self.startMonth and (not self.startDay or not self.startYear)) or (self.startDay and (not self.startMonth or not self.startYear)) or (self.startYear and (not self.startMonth or not self.startDay)):
      showerror("Invalid Date", "Need to enter month,day and year for the starting date.\n")
      return 1
    if (self.endMonth and (not self.endDay or not self.endYear)) or (self.endDay and (not self.endMonth or not self.endYear)) or (self.endYear and (not self.endMonth or not self.endDay)):
      showerror("Invalid Date", "Need to enter month,day and year for the ending date.\n")
      return 1

    if self.startMonth and self.startDay and self.startYear:
      self.startDate = self.formatDate(self.startMonth,self.startDay,self.startYear)
    if self.endMonth and self.endDay and self.endYear:
      self.endDate = self.formatDate(self.endMonth,self.endDay,self.endYear)

    if self.endDate and not self.startDate:
      showerror("Invalid Date", "Need to enter a starting date.\n")
      return 1

    return 0


  def createCommand(self):
    if os.name == "posix":
      cmd = "./dexrpt.py -i %s" % self.inputPath
    else:
      cmd = "dexrpt.py -i %s" % self.inputPath

    if self.outputDir:
      cmd = "%s -d %s" % (cmd,self.outputDir)

    if self.testNum:
      cmd = "%s -t %s" % (cmd,self.testNum)

    if self.startDate:
      cmd = "%s -s %s" % (cmd,self.startDate)

    if self.endDate:
      cmd = "%s -e %s" % (cmd,self.endDate)

    if self.spcIDList:
      cmd = "%s -p %s" % (cmd,self.spcIDList)

    if self.outputFile:
      cmd = "%s -f %s" % (cmd,self.outputFile)

    if self.serialNumList:
      cmd = "%s -n %s" % (cmd,self.serialNumList)

    if self.outputByTable:
      cmd = "%s -o" % (cmd)

    if self.lastRunOnly:
      cmd = "%s -l" % (cmd)

    if self.parseViewerTable:
      cmd = "%s -v" % (cmd)

    if self.testTimeTable:
      cmd = "%s -b" % (cmd)

    return cmd


  def dialogWindow(self,text,title=""):
    # Create a window to display text
    win = Toplevel()
    # Make it so the window disappears when escape key  or the letter 'q' is hit
    win.bind('<Escape>',lambda event,win=win:win.destroy())
    win.bind('Q',lambda event,win=win:win.destroy())
    win.bind('q',lambda event,win=win:win.destroy())

    # Add a text widget with specific dimensions
    myWindow = Pmw.ScrolledText(win,
                         usehullsize = 1,
                         hull_width = 1000,
                         hull_height = 800,)

    # Replace the contents with the value of text
    myWindow.settext(text)
    myWindow.pack()

    win.title(title)
    # Move keyboard focus to this window
    win.focus_set()
    try:
      # Ensure no mouse or keyboard events are sent to wrong window
      win.grab_set()
    except:
      pass

    # Local event loop; does not return until this window is destroyed
    win.wait_window()


  def formatDate(self, month, day, year):
    # This is the format required by the DEXRPT engine

    date = "%02i/%02i/%s"  % (int(month),int(day),year)
    return date


  def saveHistoryList(self, value, myList, myComboBox):
    # If the value already exists in the list delete it
    if value in myList:
      del myList[myList.index(value)]

    # Make sure the list does not have too many entries
    while len(myList) > 9:
      del myList[len(myList)-1]

    # Add the value to the beginning of the list
    if value:
      myList.insert(0,value)
      # Put the list in the combox drop down
      myComboBox.setlist(myList)


  def runDexRpt(self):
    self.getGuiValues()
    self.saveHistoryList(self.inputFilePath, self.resultsFileList, self.resultsFileCombo)
    self.saveHistoryList(self.inputDirPath, self.resultsDirList, self.resultsDirCombo)
    stat = self.customValidator()
    if not stat:
      cmd = self.createCommand()
      os.system(cmd)


  # Bind automatically passes some args to the function it calls hence the extra args
  # TODO:  At some point combine the following two functions into one
  def clearCurrentFile(self,*args,**kwargs):
    # Get a list of currently highlighted items in the listbox
    item = self.resultsFileCombo.component('scrolledlist').getvalue()

    # Delete the item that is currently selected
    del self.resultsFileList[self.resultsFileList.index(item[0])]

    # Put the list in the combox drop down
    self.resultsFileCombo.setlist(self.resultsFileList)


  def clearCurrentDir(self,*args,**kwargs):
    # Get a list of currently highlighted items in the listbox
    item = self.resultsDirCombo.component('scrolledlist').getvalue()

    # Delete the item that is currently selected
    del self.resultsDirList[self.resultsDirList.index(item[0])]

    # Put the list in the combox drop down
    self.resultsDirCombo.setlist(self.resultsDirList)


  def quit(self):
    # Get the values from the gui & save them to a history file
    self.getGuiValues()
    self.saveHistoryList(self.inputFilePath, self.resultsFileList, self.resultsFileCombo)
    self.saveHistoryList(self.inputDirPath, self.resultsDirList, self.resultsDirCombo)

    self.guiDefaults["startMonth"]         = self.startMonth
    self.guiDefaults["startDay"]           = self.startDay
    self.guiDefaults["startYear"]          = self.startYear
    self.guiDefaults["resultsFileHistory"] = self.resultsFileList
    self.guiDefaults["resultsDirHistory"]  = self.resultsDirList
    self.guiDefaults["testNumList"]        = self.testNum
    self.guiDefaults["spcIDList"]          = self.spcIDList
    self.guiDefaults["serialNumFile"]      = self.serialNumList
    self.guiDefaults["outputDir"]          = self.outputDir
    self.guiDefaults["outputFile"]         = self.outputFile
    self.guiDefaults["outputByTable"]      = self.outputByTable
    self.guiDefaults["lastRunOnly"]        = self.lastRunOnly
    self.guiDefaults["parseViewerTable"]   = self.parseViewerTable
    self.guiDefaults["printTestTimeTable"] = self.testTimeTable

    self.root.destroy()


  def help(self):
    try:
      from dexrpt import usageMsg
      self.dialogWindow(usageMsg, "HELP")
    except:
      showerror("Help", "Error displaying help information")


  def clearFields(self):
    # Clear all fields in the GUI
    for combo in (self.resultsFileCombo, self.resultsDirCombo, self.startMonthCombo, self.startDayCombo, self.startYearCombo, self.endMonthCombo, self.endDayCombo, self.endYearCombo):
       combo.setentry("")
    self.testNumEntry.delete(0,END)
    self.spcIDEntry.delete(0,END)
    self.serialNumEntry.delete(0,END)
    self.outputDirEntry.delete(0,END)
    self.outputFileEntry.delete(0,END)
    self.outputByTableButton.deselect()
    self.lastRunOnlyButton.deselect()
    self.parseViewerTableButton.deselect()
    self.testTimeTableButton.deselect()


  def browseFile(self,field):
    # Open a dialog box to browse to a file then set the value of the EntryField to what the user chooses
    entry = askopenfilename()
    if entry:
      field.setentry(entry)


  def browseDir(self,field):
    # Open a dialog box to browse to a dir then set the value of the EntryField to what the user chooses
    entry = askdirectory()
    if entry:
      field.setentry(entry)


class GUIDefaults:
  def __init__(self,initialGUIDefaults,filename):
    # Try to read up the history list
    self.initialGUIDefaults = initialGUIDefaults
    try:
      self.historyFileName = filename
      self.guiDefaults = cPickle.load(open(self.historyFileName))
    except:
      self.guiDefaults = self.initialGUIDefaults.copy()


  def __save(self):
    # Try to save a value to the history file
    try:
      cPickle.dump(self.guiDefaults,open(self.historyFileName,"w"))
    except:
      pass


  def __getitem__(self,key):
    try:
      value = self.guiDefaults[key]
    # If this script is asking for fields that are not in the guiDefaults file a KeyError occurs
    # This can happen when I add fields on the form; use the value from the hardcoded initial GUI defaults
    except KeyError:
      value = self.initialGUIDefaults[key]
    return value


  def __setitem__(self,key,value):
    # Save the values back to GUIDefaults.
    self.guiDefaults[key] = value
    self.__save()


###############
# Main Entry
###############
if __name__ == "__main__":

  # Script should not be run as root
  try:
    uid = os.getuid()
  except:
    print "Cannot determine user id. (Typical on windows)"
    uid = 999
  if 0 == uid:
    print "Please do not run as user root."
    sys.exit()

  gui = DEXRPTGUI()




