#!/usr/bin/python

import RPi.GPIO as GPIO
import sys, os, getopt
import datetime
from time import sleep

IN1_APLUS = 5
IN2_AMINUS = 6
IN3_BPLUS = 13
IN4_BMINUS = 19

SPR = 50
step_count=SPR
#STEP_DELAY=0.0052
STEP_DELAY=0.0026

ROTATIONS_PER_CYCLE = 8

blindStateFile = "currentBlindState.txt"
logFileName = "blindomatic.log"
closedState = "CLOSED"
openState = "OPEN"
unknownState = "UNKNOWN"

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
TEN_HOURS_IN_SECS = 36000

# Photovoltaicsensor plugged into GPIO 4 on the Pi.
PHOTO_INPUT = 4

#initialize trends to a basic unknown state
trendLen=3
trendLine=[ unknownState, unknownState, unknownState ]
trendCount=0


def setupGPIO():
  GPIO.setmode(GPIO.BCM)

  GPIO.setup(IN1_APLUS, GPIO.OUT)
  GPIO.setup(IN2_AMINUS, GPIO.OUT)
  GPIO.setup(IN3_BPLUS, GPIO.OUT)
  GPIO.setup(IN4_BMINUS, GPIO.OUT)  

def resetControl():  
  setupGPIO()
  GPIO.output(IN1_APLUS, GPIO.LOW)
  GPIO.output(IN2_AMINUS, GPIO.LOW)
  GPIO.output(IN3_BPLUS, GPIO.LOW)
  GPIO.output(IN4_BMINUS, GPIO.LOW)
  sleep(STEP_DELAY)
  return True

def clockwiseTurn(numberOfTurns):  
  setupGPIO()
  sleep(STEP_DELAY)
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
  resetControl()
  
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
  resetControl()

def getBlindState( stateFileName ):
  if not os.path.exists( stateFileName ):
    print "There is no state file, so I don't know the current"
    print "state of the blinds.  Please set the current state and"
    print "try again. Set the state by using -s <STATE> (see help"
    print "for details."
    logMsg( logFileName, "No/missing state file - cannot continue." )
    sys.exit(2)
  filePtr = open( stateFileName, "r")
  currentState = filePtr.read().strip()
  filePtr.close()
  if currentState == unknownState:
    print "I don't know the current state of the blinds."
    print "This could lead to potential damage of the blinds"
    print "or the driver system.  Therefore we cannot continue."
    print "Please set the current state and try again."
    print "Set the state by using -s <STATE> (see help for details.)"
    logMsg( logFileName, "Unknown current blind state" )
    sys.exit(2)
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
    try:
      clockwiseTurn(ROTATIONS_PER_CYCLE)
      setBlindState( blindStateFile, openState )
      return True
    except:
      logMsg( logFileName, "Error opening blinds." )
      #Make sure we clean up the possibly bad state of the pins.
      resetControl()
  return False

def closeBlinds():
  if (getBlindState(blindStateFile) == openState):
    logMessage = "Closing the blinds"
    print logMessage + ' at ' + str(datetime.datetime.now())
    logMsg( logFileName, logMessage )
    try:
      counterClockwiseTurn(ROTATIONS_PER_CYCLE)
      setBlindState( blindStateFile, closedState )
      return True
    except:
      logMsg( logFileName, "Error opening blinds." )
      #Make sure we clean up the possibly bad state of the pins.
      resetControl()
  return False

def evaluateLightLevel( period=OBSERVE_PERIOD ):
  numReadings = period/READ_SENSOR_SECONDS
  lightCount = darkCount = 0

  tempFileName = '/tmp/lastLight.txt'
  prevLightCount = 999999
  if os.path.exists( tempFileName ):
    filePtr = open( tempFileName, "r")
    prevLightCount = filePtr.read().strip()
    filePtr.close()

  while numReadings:
    lightData=GPIO.input(PHOTO_INPUT)
    if lightData:
      darkCount += 1
    else:
      lightCount += 1
    numReadings -= 1
    sleep(READ_SENSOR_SECONDS)

  # Record this light count for comparison next time
  filePtr = open( tempFileName, "w")
  filePtr.write( "%d\n" % lightCount )
  filePtr.close()
  
  #Take our counted data and determine what state we should be in
  if darkCount > 0:
    ratio = lightCount / float( darkCount)
  else:
    # if darkCount is 0, then we absolutely need to close the blinds
    if lightCount != int(prevLightCount):
      logMessage = ( "light: %d dark: %d, Ratio undefined." %
                     (lightCount, darkCount))
    return closedState

  # Use the ratio for hysteresis
  # 0 - 0.5 ratio means darkCount is decidedly more, return open state
  # Any value greater than 2 means that numerator (lightCount) is decidedly
  # more so return closed state.
  # Values between 0.5 to 1.5 are too close to call, return unknown state
  if lightCount != int(prevLightCount):
    logMessage = ( "light: %d dark: %d, Ratio was %f" %
                   (lightCount, darkCount, ratio))
    logMsg(logFileName, logMessage)

  if ratio <= 0.5:
    return openState
  if ratio >= 1.5:
    return closedState
  return unknownState

def deepSleep( interval=TEN_HOURS_IN_SECS ):
  logMessage = "Going to sleep for the night. See you in the morning!"
  logMsg( logFileName, logMessage )
  sleep( interval )
  logMsg( logFileName, "Waking up and resuming operation." )

def checkTrend( curState ):
  global trendLine, trendCount
  trendLine[trendCount] = curState
  trendCount = ( trendCount + 1 ) % trendLen
  if all( elem == trendLine[0] for elem in trendLine):
    return True
  return False

def autoBlinds():
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(PHOTO_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  print"Running in automatic mode using photo sensor as control"
  logMessage = ("%s started" % ( sys.argv[0] ) )
  logMsg( logFileName, logMessage )
                     
  lightCount = darkCount = 0

  # Do an initial reading to start with. A sigle reading is good for this
  try:
    lightData=GPIO.input(PHOTO_INPUT)
    if lightData:
      print("Sensor detected initial state of blinds should be OPEN.")
      openBlinds()
    else:
      print("Sensor detected initial state of blinds should be CLOSED.")
      closeBlinds()
  except:
    logMsg( logFileName, "Error reading initial light data." )
    GPIO.cleanup() # ensures a clean exit
    sys.exit(2)
    
  try:
    while True:
      decision = evaluateLightLevel()
      if decision == openState:
        if checkTrend( openState ):
          openBlinds()
      elif decision == closedState:
        if checkTrend( closedState ):
          closeBlinds()
      elif decision == unknownState:
        checkTrend( unknownState )
        logMsg( logFileName, "Inconclusive light data. Doing nothing" )

      # I don't need to see log messages all night long when it is
      # dark out anyway, so I am going to put the system to sleep
      # for a period at night  Just approximately check for when
      # it is time for bed, and then sleep for an interval until morning.
      if ( datetime.datetime.now().hour == BEDTIME_HOUR ):
        deepSleep( TEN_HOURS_IN_SECS )

  except:
    logMsg( logFileName, "Error controling blinds. Exiting system." )
    GPIO.cleanup() # ensures a clean exit
    sys.exit(2)

