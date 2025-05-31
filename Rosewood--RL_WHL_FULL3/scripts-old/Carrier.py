#---------------------------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2006, All rights reserved                                     #
#---------------------------------------------------------------------------------------------------------#
# Description: The carrier object implements gemini cell control functions and controls its drive ports.
#              Note that only once instance of carrier must exist in the entire test environment.
# Do NOT modify or remove this copyright and confidentiality notice!
#
# Copyright (c) 2001 - $Date: 2016/05/05 $ Seagate Technology, LLC.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
# Portions are also trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized is
# prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
#
# $File: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Carrier.py $
# $Revision: #1 $
# $DateTime: 2016/05/05 23:40:47 $
# $Author: chiliang.woo $
# $Header: //depot/SGP/PF3/ProductBranches/Rosewood7LC/Gen2B/scripts/Carrier.py#1 $
# Level: 4
#---------------------------------------------------------------------------------------------------------#
from Constants import *
import re, time, sys
import ScrCmds
from Rim import theRim, objRimType
from Cell import theCell
from UartCls import theUart
import traceback
###########################################################################################################
###########################################################################################################
class CCarrier:
   """
    Turn on power to the cell/carrier, set cell baudrate to default, send CUC (carrier unique commands)
    to carrier to probe the carrier type, rev, ID and number of ports. Init all port's baudrate to default.
    ----------
    Arguments:
    ----------
    baud    Initial baud rate that carrier is used to comm with cell
    Cell power arguments:
    set5V=5000, set12V=12000, pauseTime=10, upperLimit5V=5500, lowerLimit5V=3000
   """
   def __init__(self, baud=DEF_BAUD, set5V=5000, set12V=12000, pauseTime=10):
      """
      Initializes all variables related to carrier and calls init methods for carrier
      """
      self.__DEBUG        = 1
      self.carrierId      = 'NONE'        # carrier ID
      self.rev            = 'NONE'        # carrier FPGA Revision
      self.type           = 'NONE'
      self.__carrierTypes = {'X': 'NONE', 'S': 'SDC', 'H': 'HVC',}
      self.__set5V        = set5V  # 5V setting
      self.__set12V       = set12V # 12V setting
      self.__baud         = baud # baud rate
      self.__pauseTime    = pauseTime # pause time in seconds
      self.__portBaud     = []   # keeps port's individual baudrate
      self.__cucPrefix    = 4*CTRL_      # default prefix is Ctrl Underscore
      self.__maxPortIndex = MAX_PORTS-1 # max port number on carrier

      # init port select fail counter for all ports
      self.__selPortFailCnt = {}
      for i in range(MAX_PORTS):
         self.__selPortFailCnt[i] = 0

      self.__portBaud     = [baud for i in range(MAX_PORTS)]   # set up the initial records for ports' baudrate

   #------------------------------------------------------------------------------------------------------#
   def initCarrier(self):
      self.__probeType()              # probe carrier type, carrier_id and update MaxPortIndex
      self.__validateCarrierId()      # check carrier ID length

      # Determine carrier ID based on if it is HVC or SDC or else if no carrier (standard 3.5" drive)
      if    theCarrier.type == 'HVC':
         carrier_id = '%s%02d' % (theCarrier.carrierId, PortIndex)
      elif  theCarrier.type == 'SDC':
         carrier_id = '%s' % theCarrier.carrierId
      else:
         carrier_id = 'NONE'

      return carrier_id
      #DriveAttributes['CARRIER_ID']        = carrier_id # determined above

   #------------------------------------------------------------------------------------------------------#
   def __probeType(self):
      """
      Function:
      Probe Carrier Type by Carrier Unique Commmand(CUC)
      Prerequisite :
      self.PowerOn(set5V, set12V, pauseTime, upperLimit5V, lowerLimit5V) # cell/carrier powered on.
      self.setCellBaud ()      # set default baudrate of cell <--> carriers
      Return:
      sting type
      """
      # only HVCs and SDCs have carrier ids on them
      # In production we shud be able to get carrier sn from Matco
      # On Bench, this is an issue, so how do we determine that this drive is mounted on carrier??????
      TraceMessage('Carrier S/N from Host/Matco: "%s"' % CarrierSN)
      if len(CarrierSN) == 8: # implies some valid carrier serial number passed in from Host/Matco
         theCell.powerOff() # turn off cell power
         theCell.powerOn(self.__set5V, self.__set12V, self.__pauseTime) # turn on cell power
         theCell.setBaud(self.__baud)  # set default baud rate on cell
         self.carrierId = CarrierSN # get s/n from matco (this is more reliable, hence higher priority)
         # self.carrierId = self.__probeId() # Get carrier s/n from carrier FPGA serial port
         TraceMessage("Carrier Id:  %s" % self.carrierId)
         # get the carrier type from a preset dict, retrieval based on second prefix of carrier id
         self.type = self.__carrierTypes.get(self.carrierId[1], 'NONE') # default is 'NONE'

      # execute steps depending on carrier type
      if self.type == 'HVC':
         # Get fpga code revision from the hvc
         self.__maxPortIndex = MAX_PORTS-1 # HVC n-port carrier
         self.__selectPort(-1)   # deselect port command.
         #------------------------
         # now determine code rev
         cnt, err = 0, 1
         while cnt < 2 and err:    #  Allow a couple of retries
            cnt = cnt + 1
            err, serdata = SerialCmd(DOT,'HVC#',3)  #  Send '.' to carrier. A HVC will respond with 'HVC#'
         #------------------------
         if not err:
            self.rev = serdata.split('#')[1] # # format of "#rev#HVC#", where rev ranges from 3 to 9,A to Z
            if self.rev == '5':
               self.__cucPrefix = 4*CTRL_ # this will be the new command prefix for all carrier commands
            else:
               self.__cucPrefix = CTRL_ # this will be the new command prefix for all carrier commands

      elif self.type == 'SDC':
         self.__maxPortIndex = 0   # 1 port carrier
         self.rev = 'NONE' # rev cannot be determined for SDC

      else: # NONE
         # no carrier meaning standard 3.5" drive
         pass

      TraceMessage("Carrier Type: %s" % self.type )
      TraceMessage("Carrier Rev:  %s" % self.rev )

   #------------------------------------------------------------------------------------------------------#
   def __probeId(self):
      TraceMessage("Probing Carrier ID")
      cid = 'NONE'
      error = 1
      theCell.setBaud(Baud9600)      # cell <--> carriers
      #-------------
      # Check if SDC
      #-------------
      if error:
         cnt = 0; retries = 2
         while error and cnt<=retries:
            cnt = cnt + 1
            #print(globals())
            SerialCmd(CTRL_Z, '>')
            SerialCmd('/\r', '>', 2) # goto level T
            SerialCmd(CTRL_Z, '>')
            serdata = SerialCmd(CTRL_ + 'sendID' + CR, 'None', 3)[1]
            try:
               m = re.search('>', serdata)
               csn = serdata[m.end():][:8]
               if len(csn) == 8:
                  cid = csn
                  error = 0
                  TraceMessage("DETECTED SDC")
            except:
               pass
      #-------------
      # Check if HVC
      #-------------
      if error:
         for pfx in [CTRL_, 4*CTRL_]: # check both types of prefixes for HVC
            cnt = 0; retries = 2
            while error and cnt<=retries:
               cnt = cnt + 1
               serdata = SerialCmd(pfx + 'sendID' + DOT, 'None' ,3)[1] # Send string to select a specific drive on the HVC
               try:
                  m = re.search('>', serdata)
                  serdata = serdata[m.end():]
                  p = re.compile(r'\W+')
                  lst = p.split(serdata)
                  if len(lst[0]) == 8: # ['3S472NQF', '']
                     cid = lst[0]
                     error = 0
                     TraceMessage("DETECTED HVC")
               except:
                  pass
      #------------------------------------------------------------------
      TraceMessage("Carrier S/N Read from Carrier: [%s]" % cid)
      return cid

   #------------------------------------------------------------------------------------------------------#
   def __selectPort(self, port = -1):

      # select port is not applicable for SDC and NONE
      if self.type == 'SDC' or self.type == 'NONE':
         return 0
      #
      #  This function will send a port selection string to the HVC carrier
      #  to select the port. After the port has been selected this
      #  function will verify that the correct port was selected by looking
      #  for the port specific response from the carrier.
      #
      cnt = 0
      err   = 1

      if port > self.__maxPortIndex:
         TraceMessage ("Err! Port#%d out of range %d" % (port,self.__maxPortIndex) )
         return err

      #  Setup loop to select port on carrier.
      #  Retry once to select the port.
      #
      if port == -1:   # de-select port
         cucStr = self.__cucPrefix + 'seldN' + 'z' + DOT
         resp   = 'z#'
      else:
         cucStr = self.__cucPrefix + 'seldN' + str(port) + DOT
         resp   = str(port)+'#'

      theCell.setBaud()      # cell <--> carriers

      while (cnt < 2) and err:
         cnt = cnt + 1
         sDrvNum = str(port)
         err,serdata = SerialCmd(cucStr, resp,10)  # Send string to select a specific port on the HVC
         if self.__DEBUG:
            TraceMessage('%s %s %s %s' % (cucStr, resp, err, serdata)) # debug

      if err == 0:
         if self.__portBaud[port] != self.getCellBaud():  # baudrate mis-matching between the selected port and cell
            self.setCellBaud(self.__portBaud[port])  # adjust cell's baudrate
      else:
         TraceMessage("ERR!!! %s received on Port # %s  --  CARRIER FAILED TO SELECT PORT!!!  --" % (serdata,sDrvNum))

      return err

   #------------------------------------------------------------------------------------------------------#
   def __powerToPort(self, ONorOFF='+', set5V=5000, set12V=12000, pauseSeconds=10, driveOnly=0):
      #
      #  This function will send a port power on/off string to the HVC carrier
      #  to turn the port on or off.
      #
      if self.type == 'HVC':
         if self.__DEBUG:
            if ONorOFF == '+':
               TraceMessage('DRIVE #%d POWER ON DELAY=%d' % (PortIndex, pauseSeconds))
            else:
               TraceMessage('DRIVE #%d POWER OFF DELAY=%d' % (PortIndex, pauseSeconds))
         port = PortIndex
         if  port == -1:
            TraceMessage ("Err! Please SelectPort Before PowerToPort!" )
            return 1
         self.setCellBaud ()      # cell <--> carriers
         cucStr = self.__cucPrefix + 'pwr' + ONorOFF + str(port) + DOT
         # Send string to select a specific port on the HVC, 'PMstr' is S1 response
         # Note that power values cannot be changed for HVC since all drives share same power source
         err,data= SerialCmd(cucStr,'PMstr',5)
         if self.__DEBUG:
            TraceMessage ("Port Pwr: %s" % ONorOFF )
            TraceMessage ("Drive Response Detected! %s" % (data,) )
         time.sleep(pauseSeconds)

      elif self.type == 'SDC':
         if ONorOFF == '+':
            CellLed(1)
            if self.__DEBUG:
               TraceMessage('DRIVE POWER ON DELAY=%d' % pauseSeconds)
            if objRimType.CPCRiser() or objRimType.IOInitRiser():
               SetDTRPin(1) == 0
               time.sleep(5)
               #DriveOn(set5V, set12V, pauseTime=pauseSeconds, upperLimit5V=MAX_5V, lowerLimit5V=MIN_5V)
            else:
               SetDTRPin(1) == 0
               time.sleep(5)
               #DriveOn(set5V, set12V, pauseTime=pauseSeconds)
            data = SerialCmd(CTRL_ + 'sendID' + CR, 'None', 3)[1] # debug
            if self.__DEBUG:
               TraceMessage('Ctrl_sendID cmd Response: %s' % data)
            time.sleep(2) # debug
            if self.__DEBUG:
               TraceMessage('voltage levels = %s', `ReportVoltages()`)
         else:
            CellLed(0)
            if self.__DEBUG:
               TraceMessage('DRIVE POWER OFF DELAY=%d' % pauseSeconds)
            #DriveOff(pauseTime=pauseSeconds)
            SetDTRPin(0) == 0
            time.sleep(5)

      else: # 'NONE' implying no carrier --- direct plugin of drive to cell
         if ONorOFF == '+':
            if driveOnly == 0 and not testSwitch.SI_SERIAL_ONLY:
               #theRim.RimOn()
               SetDTRPin(1) == 0
               time.sleep(5)
            CellLed(1)
            if self.__DEBUG:
               TraceMessage('DRIVE POWER ON DELAY=%d' % pauseSeconds)
            if objRimType.CPCRiser() or objRimType.IOInitRiser():
               SetDTRPin(1) == 0
               time.sleep(5)
               #DriveOn(set5V, set12V, pauseTime=pauseSeconds, upperLimit5V=MAX_5V, lowerLimit5V=MIN_5V)
            else:
               SetDTRPin(1) == 0
               time.sleep(5)
               #DriveOn(set5V, set12V, pauseTime=pauseSeconds)
            #time.sleep(2) # debug
            if self.__DEBUG:
               TraceMessage('voltage levels = %s' % `ReportVoltages()`)
         else:
            CellLed(0)
            if self.__DEBUG:
               TraceMessage('DRIVE POWER OFF DELAY=%d' % pauseSeconds)
            #DriveOff(pauseTime=pauseSeconds)
            SetDTRPin(0) == 0
            time.sleep(5)

            if driveOnly == 0 and not testSwitch.SI_SERIAL_ONLY:
               #theRim.RimOff()
               SetDTRPin(0) == 0
               time.sleep(5)

      return 0

   #------------------------------------------------------------------------------------------------------#
   def __validateCarrierId(self):
      if self.type != 'NONE':
         if len(self.carrierId) != 8:
            ScrCmds.raiseException(13501, "Carrier ID's length is not 8")

   #------------------------------------------------------------------------------------------------------#
   def powerOnPort(self, set5V=5000, set12V=12000, onTime=10, driveOnly=0):
      
      if DriveAttributes.get('PCBA_PART_NUM','NONE') in ['100705174','100708196']:
         testSwitch.SP_TO_POWERBLADE = 1 

      if not driveOnly and (testSwitch.SWAPPED_SERIAL_PORT or testSwitch.SP_TO_POWERBLADE) :
         self.configureSPPins()
      self.__powerToPort('+', set5V, set12V, onTime, driveOnly) # turn on power to port (or cell)
      #ScriptPause(10) #  added to work around eslip failures after power cycle

   #------------------------------------------------------------------------------------------------------#
   def powerOffPort(self, offTime=10, driveOnly=0):
      self.__powerToPort('-', 5000, 12000, offTime, driveOnly)

   def configureSPPins(self):
      try:
         if testSwitch.SWAPPED_SERIAL_PORT:
            ScrCmds.statMsg("Configuring SPort to Swapped Tx/Rx")
            SwitchSerialPort(SwappedSPort)     
         else:
            ScrCmds.statMsg("Using default Direct Tx/Rx")
      except:
         ScrCmds.statMsg("SwitchSerialPort is fail:\n%s" % str(traceback.format_exc()))
         pass
      
      try:
         if testSwitch.SP_TO_POWERBLADE:            
            ScrCmds.statMsg("Setting SPort to Powerblade")
            SPortToPogoPins(0)                 
         else:
            ScrCmds.statMsg("Using default SPort to Pogo")
      except:
         ScrCmds.statMsg("SPortToPogoPins is fail:\n%s" % str(traceback.format_exc()))
         pass

   #-----------------------------------------------------------------------------------------#
   def YS(self, timeout=0):
      theCell.setBaud(DEF_BAUD)
      YieldScript(timeout)
      if self.__selectPort(PortIndex) != 0:
         objMsg.printMsg('ERROR: Unable to Select Port on Carrier (h/w issue?)!! FailCount = %d' % self.__selPortFailCnt[PortIndex])
         if self.__selPortFailCnt[PortIndex] < 20:
            self.__selPortFailCnt[PortIndex] += 1
            YieldScript(timeout) # we cannot proceed so simply yield script
         else:
            msg = 'Select Port %d Error Exception, Aborting Thread..' % PortIndex
            ScrCmds.raiseException(13502, 'Select Port %d Error Exception, Aborting Thread..' % PortIndex)


#**********************************************************************************************************
#**********************************************************************************************************
theCarrier = CCarrier() # create carrier instance,power on cell/carrier
TraceMessage('Carrier Instance Created %d' % PortIndex)

#---------------------------------------------------------------------------------------------------------#
