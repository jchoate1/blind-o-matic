#!/usr/bin/python

from time import sleep
import RPi.GPIO as GPIO
import sys, os, getopt
import datetime
import pdb

PHOTO_INPUT = 4
IN1_APLUS = 5
IN2_AMINUS = 6
IN3_BPLUS = 13
IN4_BMINUS = 19

SPR = 50
step_count=SPR
STEP_DELAY=0.0052

ROTATIONS_PER_CYCLE = 8

# Number of seconds between each reading of photo sensor
READ_SENSOR_SECONDS = 3
# Adding historesis - must get this many consistent readings
# in a row before an action is taken
SMOOTHING_LEVEL = 5

blindStateFile = "currentBlindState.txt"
logFileName = "blindomatic.log"
closedState = "CLOSED"
openState = "OPEN"

def setupGPIO():
  GPIO.setmode(GPIO.BCM)

  GPIO.setup(PHOTO_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

  GPIO.setup(IN1_APLUS, GPIO.OUT)
  GPIO.setup(IN2_AMINUS, GPIO.OUT)
  GPIO.setup(IN3_BPLUS, GPIO.OUT)
  GPIO.setup(IN4_BMINUS, GPIO.OUT)  

def clockwiseTurn(numberOfTurns):  
  setupGPIO()
  for iteration in range(0, numberOfTurns):
    for x in range( step_count):
      GPIO.output(IN1_APLUS, GPIO.LOW)
      GPIO.output(IN2_AMINUS, GPIO.HIGH)
      GPIO.output(IN3_BPLUS, GPIO.HIGH)
      GPIO.output(IN4_BMINUS, GPIO.LOW)
      sleep(STEP_DELAY)
      GPIO.output(IN1_APLUS, GPIO.LOW)
      GPIO.output(IN2_AMINUS, GPIO.HIGH)
      GPIO.output(IN3_BPLUS, GPIO.LOW)
      GPIO.output(IN4_BMINUS, GPIO.HIGH)
      sleep(STEP_DELAY)
      GPIO.output(IN1_APLUS, GPIO.HIGH)
      GPIO.output(IN2_AMINUS, GPIO.LOW)
      GPIO.output(IN3_BPLUS, GPIO.LOW)
      GPIO.output(IN4_BMINUS, GPIO.HIGH)
      sleep(STEP_DELAY)
      GPIO.output(IN1_APLUS, GPIO.HIGH)
      GPIO.output(IN2_AMINUS, GPIO.LOW)
      GPIO.output(IN3_BPLUS, GPIO.HIGH)
      GPIO.output(IN4_BMINUS, GPIO.LOW)
      sleep(STEP_DELAY)
  GPIO.output(IN1_APLUS, GPIO.LOW)
  GPIO.output(IN2_AMINUS, GPIO.LOW)
  GPIO.output(IN3_BPLUS, GPIO.LOW)
  GPIO.output(IN4_BMINUS, GPIO.LOW)
  sleep(STEP_DELAY)

def counterClockwiseTurn(numberOfTurns):  
  setupGPIO()
  for iteration in range(0, numberOfTurns):
    for x in range( step_count):
      GPIO.output(IN1_APLUS, GPIO.HIGH)
      GPIO.output(IN2_AMINUS, GPIO.LOW)
      GPIO.output(IN3_BPLUS, GPIO.HIGH)
      GPIO.output(IN4_BMINUS, GPIO.LOW)
      sleep(STEP_DELAY)
      GPIO.output(IN1_APLUS, GPIO.HIGH)
      GPIO.output(IN2_AMINUS, GPIO.LOW)
      GPIO.output(IN3_BPLUS, GPIO.LOW)
      GPIO.output(IN4_BMINUS, GPIO.HIGH)
      sleep(STEP_DELAY)
      GPIO.output(IN1_APLUS, GPIO.LOW)
      GPIO.output(IN2_AMINUS, GPIO.HIGH)
      GPIO.output(IN3_BPLUS, GPIO.LOW)
      GPIO.output(IN4_BMINUS, GPIO.HIGH)
      sleep(STEP_DELAY)
      GPIO.output(IN1_APLUS, GPIO.LOW)
      GPIO.output(IN2_AMINUS, GPIO.HIGH)
      GPIO.output(IN3_BPLUS, GPIO.HIGH)
      GPIO.output(IN4_BMINUS, GPIO.LOW)
      sleep(STEP_DELAY)
  GPIO.output(IN1_APLUS, GPIO.LOW)
  GPIO.output(IN2_AMINUS, GPIO.LOW)
  GPIO.output(IN3_BPLUS, GPIO.LOW)
  GPIO.output(IN4_BMINUS, GPIO.LOW)
  sleep(STEP_DELAY)

def getBlindState( stateFileName ):
  if not os.path.exists( stateFileName ):
    print "There is no state file, so I don't know the current"
    print "state of the blinds.  Please set the current state and"
    print "try again. Set the state by using -s <STATE> (see help"
    print "for details."
    sys.exit(2)
  filePtr = open( stateFileName, "r")
  currentState = filePtr.read().strip()
  filePtr.close()
  return currentState

def setBlindState( stateFileName, state ):
  filePtr = open( stateFileName, "w")
  filePtr.write( state + "\n")
  filePtr.close()

def logMsg( logFile, logMessage ):
    logFilePtr = open( logFile, 'a' )
    logLine =  str(datetime.datetime.now()) + ' : ' + logMessage + '\n' 
    logFilePtr.write( logLine )
    logFilePtr.close
  
def openBlinds():
  if (getBlindState(blindStateFile) == closedState):
    logMessage = "Opening the blinds"
    print logMessage + ' at ' + str(datetime.datetime.now())
    logMsg( logFileName, logMessage )
    clockwiseTurn(ROTATIONS_PER_CYCLE)
    setBlindState( blindStateFile, openState )
    return True
  return False

def closeBlinds():
  if (getBlindState(blindStateFile) == openState):
    logMessage = "Closing the blinds"
    print logMessage + ' at ' + str(datetime.datetime.now())
    logMsg( logFileName, logMessage )
    counterClockwiseTurn(ROTATIONS_PER_CYCLE)
    setBlindState( blindStateFile, closedState )
    return True
  return False

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
      filePtr = open( blindStateFile, "w")
      filePtr.write( arg + "\n")
      filePtr.close()
      sys.exit()

  # Make sure we have the current state of blinds before we do something.
  initialState = getBlindState(blindStateFile)
  
  if (desiredAction in ['auto','AUTO','automatic', 'AUTOMATIC']):
    print"Running in automatic mode using photo sensor as control"
    lightCount = darkCount = 0
    setupGPIO()
    appendWrite = 'a' if os.path.exists( logFileName ) else 'w'
    logFilePtr = open( logFileName, appendWrite )
    logFilePtr.write("%s : %s started\n" % ( str(datetime.datetime.now()),
                                                   sys.argv[0] ) )
    logFilePtr.close
                     
    # Do an initial reading to start with.
    lightData=GPIO.input(PHOTO_INPUT)
    if lightData:
      print("Sensor detected initial state of blinds is OPEN.")
      openBlinds()
    else:
      print("Sensor detected initial state of blinds is CLOSED.")
      closeBlinds()

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
            if openBlinds():
              # Wait for 5 minutes here before moving on
              # after a state change
              logMsg( logFileName, "Sleeping for 5 mins." )
              sleep( 300 )
              logMsg( logFileName, "Resuming operation after sleep." )
        else:
          if lightCount > 0:
            lightCount = darkCount = 0
          darkCount += 1
          if darkCount >= SMOOTHING_LEVEL:
            if closeBlinds():
              # Wait for 5 minutes here before moving on
              # after a state change
              logMsg( logFileName, "Sleeping for 5 mins." )
              sleep( 300 )
              logMsg( logFileName, "Resuming operation after sleep." )
        sleep( READ_SENSOR_SECONDS )
    except:
      logMsg( logFileName, "Exiting system" )
      GPIO.cleanup() # ensures a clean exit
      sys.exit(2)
      
  if (desiredAction in ['open','OPEN','opened', 'OPENED']):
    openBlinds()
  if (desiredAction in ['close','CLOSE','CLOSED','closed']):
    closeBlinds()

  GPIO.cleanup() # ensures a clean exit

if __name__ == "__main__":
  main(sys.argv[1:])



