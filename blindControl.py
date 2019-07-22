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

def setupGPIO():
  GPIO.setmode(GPIO.BCM)

  GPIO.setup(IN1_APLUS, GPIO.OUT)
  GPIO.setup(IN2_AMINUS, GPIO.OUT)
  GPIO.setup(IN3_BPLUS, GPIO.OUT)
  GPIO.setup(IN4_BMINUS, GPIO.OUT)  

def resetControl():  
  logMessage = "Resetting the GPIO state (set all to low)"
  print logMessage + ' at ' + str(datetime.datetime.now())
  logMsg( logFileName, logMessage )
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

