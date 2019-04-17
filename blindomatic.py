#!/usr/bin/python

import blindControl as ctrl
from time import sleep
import RPi.GPIO as GPIO
import sys, os, getopt
import datetime
import pdb

# Number of seconds between each reading of photo sensor
READ_SENSOR_SECONDS = 3
# Adding historesis - must get this many consistent readings
# in a row before an action is taken
SMOOTHING_LEVEL = 5

PHOTO_INPUT = 4

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
    logMessage = ("%s started\n" % ( sys.argv[0] ) )
    ctrl.logMsg( ctrl.logFileName, logMessage )
                     
    lightCount = darkCount = 0
    ctrl.setupGPIO()

    # Do an initial reading to start with.
    lightData=GPIO.input(PHOTO_INPUT)
    if lightData:
      print("Sensor detected initial state of blinds is OPEN.")
      ctrl.openBlinds()
    else:
      print("Sensor detected initial state of blinds is CLOSED.")
      ctrl.closeBlinds()

    try:
      while True:
        lightData=GPIO.input(PHOTO_INPUT)
        # Prevent overflow
        lightCount = 1 if (lightCount == sys.maxint) else lightCount 
        darkCount = 1 if (darkCount == sys.maxint) else darkCount 
        if lightData:
          if darkCount > 0:
            lightCount = darkCount = 0
          lightCount += 1
          if lightCount >= SMOOTHING_LEVEL:
            if ctrl.openBlinds():
              # Wait for 5 minutes here before moving on
              # after a state change
              ctrl.logMsg( ctrl.logFileName, "Sleeping for 5 mins." )
              sleep( 300 )
              ctrl.logMsg( ctrl.logFileName, "Resuming operation." )
        else:
          if lightCount > 0:
            lightCount = darkCount = 0
          darkCount += 1
          if darkCount >= SMOOTHING_LEVEL:
            if ctrl.closeBlinds():
              # Wait for 5 minutes here before moving on
              # after a state change
              ctrl.logMsg( ctrl.logFileName, "Sleeping for 5 mins." )
              sleep( 300 )
              ctrl.logMsg( ctrl.logFileName, "Resuming operation." )
        sleep( READ_SENSOR_SECONDS )
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



