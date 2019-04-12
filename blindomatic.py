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

def openBlinds():
  filePtr = open( blindStateFile, "r")
  currentState = filePtr.read().strip()
  filePtr.close()
  if (currentState == closedState):
    logFilePtr = open( logFileName, 'a' )
    logFilePtr.write("Opening the blinds at %s\n" % datetime.datetime.now() )
    logFilePtr.close
    print ("Opening the blinds at: %s" % datetime.datetime.now())
    clockwiseTurn(ROTATIONS_PER_CYCLE)
  filePtr = open( blindStateFile, "w")
  filePtr.write( openState + "\n")
  filePtr.close()

def closeBlinds():
  filePtr = open( blindStateFile, "r")
  currentState = filePtr.read().strip()
  filePtr.close()
  if (currentState == openState):
    logFilePtr = open( logFileName, 'a' )
    logFilePtr.write("Closing the blinds at %s\n" % datetime.datetime.now() )
    logFilePtr.close
    print ("Closing the blinds at: %s" % datetime.datetime.now())
    counterClockwiseTurn(ROTATIONS_PER_CYCLE)
  filePtr = open( blindStateFile, "w")
  filePtr.write( closedState + "\n")
  filePtr.close()

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

  if (desiredAction in ['auto','AUTO','automatic', 'AUTOMATIC']):
    print"Running in automatic mode using photo sensor as control"
    lightCount = darkCount = 0
    setupGPIO()
    appendWrite = 'a' if os.path.exists( logFileName ) else 'w'
    logFilePtr = open( logFileName, appendWrite )
    logFilePtr.write("%s started at %s\n" % (sys.argv[0],
                                             datetime.datetime.now() ) )
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
            openBlinds()
            # Wait for 5 minutes here before moving on
            # after a state change
            sleep( 300 )
        else:
          if lightCount > 0:
            lightCount = darkCount = 0
          darkCount += 1
          if darkCount >= SMOOTHING_LEVEL:
            closeBlinds()
            # Wait for 5 minutes here before moving on
            # after a state change
            sleep( 300 )
        sleep( READ_SENSOR_SECONDS )
    except:
      GPIO.cleanup() # ensures a clean exit
      sys.exit(2)
      
  if (desiredAction in ['open','OPEN','opened', 'OPENED']):
    openBlinds()
  if (desiredAction in ['close','CLOSE','CLOSED','closed']):
    closeBlinds()

  GPIO.cleanup() # ensures a clean exit

if __name__ == "__main__":
  main(sys.argv[1:])



