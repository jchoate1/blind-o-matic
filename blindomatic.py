#!/usr/bin/python

from time import sleep
import RPi.GPIO as GPIO
import sys, getopt
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
closedState = "CLOSED"
openState = "OPEN"

def clockwiseTurn(numberOfTurns):  
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

def counterClockwiseTurn(numberOfTurns):  
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

def openBlinds():
  filePtr = open( blindStateFile, "r")
  currentState = filePtr.read().strip()
  filePtr.close()
#  print("Current State is: %s, Closed state is %s\n" % (currentState, openState))
  if (currentState == closedState):
    print ("Opening the blinds at: %s" % datetime.datetime.now())
    clockwiseTurn(ROTATIONS_PER_CYCLE)
  filePtr = open( blindStateFile, "w")
  filePtr.write( openState + "\n")
  filePtr.close()

  #clockwiseTurn(ROTATIONS_PER_CYCLE)
      
def closeBlinds():
  filePtr = open( blindStateFile, "r")
  currentState = filePtr.read().strip()
  filePtr.close()
#  print("Current State is: %s, Closed state is %s\n" % (currentState, closedState))
  if (currentState == openState):
    print ("Closing the blinds at: %s" % datetime.datetime.now())
    counterClockwiseTurn(ROTATIONS_PER_CYCLE)
  filePtr = open( blindStateFile, "w")
  filePtr.write( closedState + "\n")
  filePtr.close()

  #counterClockwiseTurn(ROTATIONS_PER_CYCLE)

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

  GPIO.setmode(GPIO.BCM)

  GPIO.setup(PHOTO_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(IN1_APLUS, GPIO.OUT)
  GPIO.setup(IN2_AMINUS, GPIO.OUT)
  GPIO.setup(IN3_BPLUS, GPIO.OUT)
  GPIO.setup(IN4_BMINUS, GPIO.OUT)  
  if (desiredAction in ['auto','AUTO','automatic', 'AUTOMATIC']):
    print"Running in automatic mode using photo sensor as control"
    lightCount = darkCount = 0

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

      # try:
      #   lightData=GPIO.input(PHOTO_INPUT)
      #   if lightData:
      #     if darkCount > 0:
      #       darkCount = 0
      #       lightCount = 0
      #     lightCount += 1
      #     if lightCount >= 3:
      #       print ("Opening blinds at: %s" % datetime.datetime.now())
      #       openBlinds()
      #   else:
      #     if lightCount > 0:
      #       lightCount = 0
      #       darkCount = 0
      #     darkCount += 1
      #     if darkCount >= 3:
      #       print ("Closing blinds at: %s" % datetime.datetime.now())
      #       closeBlinds()
      # except (KeyboardInterrupt, SystemExit):
      #   raise
      # except:
      #   GPIO.cleanup() # ensures a clean exit
      #   sys.exit(2)
      
  if (desiredAction in ['open','OPEN','opened', 'OPENED']):
    openBlinds()
  if (desiredAction in ['close','CLOSE','CLOSED','closed']):
    closeBlinds()

  GPIO.cleanup() # ensures a clean exit

if __name__ == "__main__":
  main(sys.argv[1:])



