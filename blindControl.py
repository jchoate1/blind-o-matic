#!/usr/bin/python
'''
This is a library for the automatic blind control program.  This library 
contains all of the functions that are necessary to drive the stepper motor to 
produce the desired results.  It also contains routines for reading and 
judging the current light level from a separate photovoltaic sensor.
'''

import RPi.GPIO as GPIO
import sys, os, getopt
import datetime
from time import sleep

# GPIO Pins from the H-bridge go to these Pi pins
IN1_APLUS = 5
IN2_AMINUS = 6
IN3_BPLUS = 13
IN4_BMINUS = 19
# Photovoltaicsensor plugged into GPIO 4 on the Pi.
PHOTO_INPUT = 4

#Steps per revolution for the stepper motor we have
SPR = 50
STEP_COUNT=SPR
# Delay is required between activation of next step. Time is in seconds.
# STEP_DELAY=0.0052
STEP_DELAY=0.0026

# Empirically determined that 8 revolutions of the motor are
# required to either close or open the blinds from the opposite
# setting (closed -> open, etc)
ROTATIONS_PER_CYCLE = 8

# The stepper motor will put each of its 4 poles through a complete phase
# angle cycle.  This dict represents the phases we will induce for a rotation.
# We start high, hold for half the cycle and then go low.
phaseAngles={
  0:GPIO.HIGH,
  1:GPIO.HIGH,
  2:GPIO.LOW,
  3:GPIO.LOW,
}

blindStateFile = "currentBlindState.txt"
logFileName = "blindomatic.log"
closedState = "CLOSED"
openState = "OPEN"
unknownState = "UNKNOWN"

## Photo sensor setup values
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

#initialize trends to a basic unknown state
trendLen=3
trendLine=[ unknownState, unknownState, unknownState ]
trendCount=0

def logMsg( logFile, logMessage ):
  '''
  Facility for creating system logging messages
  '''
  logFilePtr = open( logFile, 'a' )
  logLine =  str(datetime.datetime.now()) + ' : ' + logMessage + '\n' 
  logFilePtr.write( logLine )
  logFilePtr.close
  
def deepSleep( interval=TEN_HOURS_IN_SECS ):
  '''
  A very long sleep routine designed to pause the system overnight.  It 
  doesn't needto be precise, it is only to sleep the system for interval number of 
  seconds.  By default, it will return 10 hours after it is called.
  '''
  logMessage = "Going to sleep for the night. See you in the morning!"
  logMsg( logFileName, logMessage )
  sleep( interval )
  logMsg( logFileName, "Waking up and resuming operation." )

def setupGPIO():
  '''
  GPIO pins are setup on the Pi so that they are output only.
  We supress warnings to deal with concurrent use (asynchronous).
  '''
  GPIO.setmode(GPIO.BCM)
  GPIO.setwarnings(False)
  GPIO.setup(IN1_APLUS, GPIO.OUT)
  GPIO.setup(IN2_AMINUS, GPIO.OUT)
  GPIO.setup(IN3_BPLUS, GPIO.OUT)
  GPIO.setup(IN4_BMINUS, GPIO.OUT)  

def resetControl():
  '''
  This function is used to get all of the pins back to a low state so
  the stepper motor will never get constantly driven or locked up.
  '''
  setupGPIO()
  GPIO.output(IN1_APLUS, GPIO.LOW)
  GPIO.output(IN2_AMINUS, GPIO.LOW)
  GPIO.output(IN3_BPLUS, GPIO.LOW)
  GPIO.output(IN4_BMINUS, GPIO.LOW)
  sleep(STEP_DELAY)
  return True

def clockwiseTurn(numberOfTurns):  
  setupGPIO()
  '''
  Each pin of the bridge will run through a complete
  phase, where the B pins are at a 90 degree offset from
  the A pins. We use our phaseAngle dict and traverse it
  4 times for each step through the phase of a turn,
  and we then do that for the number of turns we have
  passed in. By marching through the phases in a
  specific order, we will rotate the rotor in a clockwise
  direction.
  '''
  for iteration in range(0, numberOfTurns):
    for x in range( STEP_COUNT ):
      for phase in range(4):
        GPIO.output(IN1_APLUS, phaseAngles[(phase+3)%4])
        GPIO.output(IN2_AMINUS, phaseAngles[(phase+1)%4])
        GPIO.output(IN3_BPLUS, phaseAngles[(phase+2)%4])
        GPIO.output(IN4_BMINUS, phaseAngles[(phase)%4])
        sleep(STEP_DELAY)
  resetControl()
  
def counterClockwiseTurn(numberOfTurns):  
  setupGPIO()
  '''
  This is the same function as above in clockwiseTurn().  
  See that function for a description.  The only difference 
  is that we march through the phase angles in the reverse order, 
  thus rotating the rotor in a counter clockwise direction.
  '''
  for iteration in range(0, numberOfTurns):
    for x in range( STEP_COUNT ):
      for phase in range(4):
        GPIO.output(IN1_APLUS, phaseAngles[(phase)%4])
        GPIO.output(IN2_AMINUS, phaseAngles[(phase+2)%4])
        GPIO.output(IN3_BPLUS, phaseAngles[(phase+1)%4])
        GPIO.output(IN4_BMINUS, phaseAngles[(phase+3)%4])
        sleep(STEP_DELAY)
  resetControl()

def getBlindState( stateFileName ):
  '''
  Read and return our central blind state file.  If there is no
  blind state file, we cannot continue, so alert the user and
  cause the system to exit immediately.  If we ever tried to close 
  the closed blinds, or open the open blinds, we could damage the 
  walls, blinds, system, or any combination thereof.  So we need 
  to know the state of the blinds before we can begin.
  '''
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
  # We need to know that the blinds are either opened or closed currently
  # otherwise we have a problem controlling them.
  if not (currentState == openState) and not (currentState == closedState) :
    print "ERROR - State of the blinds is not known."
    print "This could lead to potential damage of the blinds"
    print "or the driver system.  Therefore we cannot continue."
    print "Please set the current state and try again."
    print "Set the state by using -s <STATE> (see help for details.)"
    logMsg( logFileName, "Unknown current blind state" )
    sys.exit(2)
  # Assuming we successfully read the current blind state, return that to
  # the caller.
  return currentState

def setBlindState( stateFileName, state ):
  '''
  Write the state of the blinds to a well known file so everything stays coordinated.
  '''
  filePtr = open( stateFileName, "w")
  filePtr.write( state + "\n")
  filePtr.close()

def openBlinds():
  '''
  The action function that will perform and log the action
  of opening the blinds.  This function serves as an API to the
  blinds control.  Users should simply call this function to affect
  opening the blinds. If the blinds are already open,
  no action is taken.  The function returns True if an action
  was taken, and False otherwise.
  '''
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
  '''
  The action function that will perform and log the action
  of closing the blinds.  This function serves as an API to the
  blinds control.  Users should simply call this function to affect
  closing the blinds. If the blinds are already closed,
  no action is taken.  The function returns True if an action
  was taken, and False otherwise.
  '''
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

def checkTrend( curState ):
  '''
  An attempt at hysteresis. See whether our last several measurements
  agree with the current measurement.  Only if we see a trend develop,
  should we actually take action.
  '''
  global trendLine, trendCount
  trendLine[trendCount] = curState
  trendCount = ( trendCount + 1 ) % trendLen
  if all( elem == trendLine[0] for elem in trendLine):
    return True
  return False

def evaluateLightLevel( period=OBSERVE_PERIOD, interval=READ_SENSOR_SECONDS ):
  '''
  This function collects the light levels using a photovoltaic
  sensor attached to the GPIO pins for some given amount of time.  
  It takes a reading at given intervals for a period specified by 
  the caller.  Because we are using GPIO, readings are binary.  2 
  counters are maintained to hold the number of readings classified 
  as "dark", and "light".
  Once all readings for a period are gathered, the ratio between light
  and dark levels is computed, and we return what we believe the state of
  the blinds should be based on this ratio (open for dark out,
  closed for light out).
  Probably there is a better way to deal with the readings for more accurate
  hysteresis.
  '''
  numReadings = period/interval
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
    sleep( interval )

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

def autoBlinds():
  '''
  This is an API to the blind control system that is called to automatically 
  control the blinds.  This driver function that will be called when the user wants
  automatic operation.  One called, the function runs and will not return unless an
  error is encountered, or the program is terminated. It simply loops gathering
  the light levels at given intervals and takes the approproiate actions
  along the way.
  '''
  #Set up the photo sensor as an input to the machine
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(PHOTO_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  
  print"Running in automatic mode using photo sensor as control"
  logMessage = ("%s started" % ( sys.argv[0] ) )
  logMsg( logFileName, logMessage )
                     
  lightCount = darkCount = 0

  # Do an initial reading to start with. A sigle reading is good for this
  try:
    firstState = unknownState
    lightData=GPIO.input(PHOTO_INPUT)
    if lightData:
      print("Sensor detected initial state of blinds should be OPEN.")
      firstState=openState
      openBlinds()
    else:
      print("Sensor detected initial state of blinds should be CLOSED.")
      firstState=closedState
      closeBlinds()
    for i in range(trendLen):
      trendLine[i]=firstState
  except:
    logMsg( logFileName, "Error reading initial light data." )
    GPIO.cleanup() # ensures a clean exit
    sys.exit(2)

  #This is the main loop - do this forever.
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
        # Inconclusive state should not modify or affect the current
        # trend, so we don't make any move when the data is inconclusive.
        logMsg( logFileName, "Inconclusive light data. Doing nothing" )

      # I don't need to see log messages all night long when it is
      # dark out anyway, so I am going to put the system to sleep
      # for a period at night  Just approximately check for when
      # it is time for bed, and then sleep for an interval until morning.
      if ( datetime.datetime.now().hour == BEDTIME_HOUR ):
        deepSleep( TEN_HOURS_IN_SECS )

  except:
    # In an exception or quit, we log a message and then cleanup the
    # GPIO signals and finally just exit.
    logMsg( logFileName, "Error controling blinds. Exiting system." )
    GPIO.cleanup() # ensures a clean exit
    sys.exit(2)

