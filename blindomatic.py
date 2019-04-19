#!/usr/bin/python

import blindControl as ctrl
from time import sleep
import RPi.GPIO as GPIO
import sys, os, getopt
import datetime
import pdb

# Number of seconds between each reading of photo sensor
READ_SENSOR_SECONDS = 3
# Number of seconds to gather data to make a decision
OBSERVE_PERIOD = 300
# Adding hysteresis - must get this many consistent readings
# in a row before an action is taken
SMOOTHING_LEVEL = 5
# Time at night (hour) to put system to deep sleep for the night
BEDTIME_HOUR = 21
# Number of seconds in 10 hours used to put system to deep sleep.
TEN_HOURS_IN_SECS = 3600

PHOTO_INPUT = 4
def evaluateLightLevel( period=OBSERVE_PERIOD ):
  numReadings = period/READ_SENSOR_SECONDS
  lightCount = darkCount = 0
  while numReadings:
    lightData=GPIO.input(PHOTO_INPUT)
    if lightData:
      darkCount += 1
    else:
      lightCount += 1
    numReadings -= 1
    sleep(READ_SENSOR_SECONDS)

  #Take our counted data and determine what state we should be in
  if darkCount > 0:
    ratio = lightCount / float( darkCount)
  else:
    # if darkCount is 0, then we absolutely need to close the blinds
    ctrl.logMsg(ctrl.logFileName, "Only light reading - no ratio available")
    return ctrl.closedState

  # Use the ratio for hysteresis
  # 0 - 0.5 ratio means darkCount is decidedly more, return open state
  # Any value greater than 2 means that numerator (lightCount) is decidedly
  # more so return closed state.
  # Values between 0.5 to 1.5 are too close to call, return unknown state
  logMessage = ( "light: %d dark: %d, Ratio was %f" %
                 (lightCount, darkCount, ratio))
  ctrl.logMsg(ctrl.logFileName, logMessage)
  if ratio <= 0.5:
    return ctrl.openState
  if ratio >= 1.5:
    return ctrl.closedState
  return ctrl.unknownState

def deepSleep( interval=TEN_HOURS_IN_SECS ):
  logMessage = "Going to sleep for the night. See you in the morning!"
  ctrl.logMsg( ctrl.logFileName, logMessage )
  sleep( interval )
  ctrl.logMsg( ctrl.logFileName, "Waking up and resuming operation." )

def main(argv):
  desiredAction=''
  try:
    opts, args = getopt.getopt(argv,"hsa",["action=","state="])
  except getopt.GetOptError:
    print 'blindomatic.py [-a (open, close, auto)] [-s state (OPEN, CLOSED)]'
    sys.exit(2)
  for opt,arg in opts:
    if opt == '-h':
      print 'blindomatic.py [-a (open, close, auto)] [-s state (OPEN, CLOSED)]'
      sys.exit()
    elif opt in ( "-a", "--action"):
      desiredAction = arg
    elif opt in ("-s", "--state"):
      filePtr = open( ctrl.blindStateFile, "w")
      if (arg in ['OPEN', 'open', 'OPENED', 'opened']):
          filePtr.write( ctrl.openState + "\n")
      elif (arg in ['CLOSE', 'close', 'CLOSED', 'closed']):
          filePtr.write( ctrl.closedState + "\n")
      else:
          filePtr.write( ctrl.unknownState + "\n")
      filePtr.close()
      sys.exit()

  # Make sure we have the current state of blinds before we do something.
  initialState = ctrl.getBlindState(ctrl.blindStateFile)
  if (desiredAction in ['auto','AUTO','automatic', 'AUTOMATIC']):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PHOTO_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    print"Running in automatic mode using photo sensor as control"
    logMessage = ("%s started" % ( sys.argv[0] ) )
    ctrl.logMsg( ctrl.logFileName, logMessage )
                     
    lightCount = darkCount = 0
    ctrl.setupGPIO()

    # Do an initial reading to start with. A sigle reading is good for this
    lightData=GPIO.input(PHOTO_INPUT)
    if lightData:
      print("Sensor detected initial state of blinds should be OPEN.")
      ctrl.openBlinds()
    else:
      print("Sensor detected initial state of blinds should be CLOSED.")
      ctrl.closeBlinds()

    try:
      while True:
        decision = evaluateLightLevel()
        if decision == ctrl.openState:
          ctrl.openBlinds()
        elif decision == ctrl.closedState:
          ctrl.closeBlinds()
        elif decision == ctrl.unknownState:
          ctrl.logMsg( ctrl.logFileName, "Unknown blind state. Doing nothing" )

        # I don't need to see log messages all night long when it is
        # dark out anyway, so I am going to put the system to sleep
        # for a period at night  Just approximately check for when
        # it is time for bed, and then sleep for an interval until morning.
        if ( datetime.datetime.now().hour == BEDTIME_HOUR ):
          deepSleep( TEN_HOURS_IN_SECS )

    except:
      ctrl.logMsg( ctrl.logFileName, "Exiting system" )
      GPIO.cleanup() # ensures a clean exit
      sys.exit(2)
      
  if (desiredAction in ['open','OPEN','opened', 'OPENED']):
    ctrl.openBlinds()
  if (desiredAction in ['close','CLOSE','CLOSED','closed']):
    ctrl.closeBlinds()

  GPIO.cleanup() # ensures a clean exit

if __name__ == "__main__":
  main(sys.argv[1:])
