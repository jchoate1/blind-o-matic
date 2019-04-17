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
STEP_DELAY=0.0052

ROTATIONS_PER_CYCLE = 8

blindStateFile = "currentBlindState.txt"
logFileName = "blindomatic.log"
closedState = "CLOSED"
openState = "OPEN"

def setupGPIO():
  GPIO.setmode(GPIO.BCM)

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

