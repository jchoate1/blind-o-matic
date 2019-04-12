#!/usr/bin/python

from time import sleep
import RPi.GPIO as GPIO
import sys, getopt
import pdb
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    text = open('currentBlindState.txt', 'r+')
    content = text.read()
    text.close()
            
    return render_template('index.html',content=content)

@app.route('/open/')
def opener():
    openBlinds()
    return 'Blinds are now Opened'

@app.route('/close/')
def closer():
    closeBlinds()
    return 'Blinds are now Closed.'

IN1_APLUS = 5
IN2_AMINUS = 6
IN3_BPLUS = 13
IN4_BMINUS = 19

SPR = 50
step_count=SPR
delay=0.0052

ROTATIONS_PER_CYCLE = 8

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
      sleep(delay)
      GPIO.output(IN1_APLUS, GPIO.LOW)
      GPIO.output(IN2_AMINUS, GPIO.HIGH)
      GPIO.output(IN3_BPLUS, GPIO.LOW)
      GPIO.output(IN4_BMINUS, GPIO.HIGH)
      sleep(delay)
      GPIO.output(IN1_APLUS, GPIO.HIGH)
      GPIO.output(IN2_AMINUS, GPIO.LOW)
      GPIO.output(IN3_BPLUS, GPIO.LOW)
      GPIO.output(IN4_BMINUS, GPIO.HIGH)
      sleep(delay)
      GPIO.output(IN1_APLUS, GPIO.HIGH)
      GPIO.output(IN2_AMINUS, GPIO.LOW)
      GPIO.output(IN3_BPLUS, GPIO.HIGH)
      GPIO.output(IN4_BMINUS, GPIO.LOW)
      sleep(delay)
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
      sleep(delay)
      GPIO.output(IN1_APLUS, GPIO.HIGH)
      GPIO.output(IN2_AMINUS, GPIO.LOW)
      GPIO.output(IN3_BPLUS, GPIO.LOW)
      GPIO.output(IN4_BMINUS, GPIO.HIGH)
      sleep(delay)
      GPIO.output(IN1_APLUS, GPIO.LOW)
      GPIO.output(IN2_AMINUS, GPIO.HIGH)
      GPIO.output(IN3_BPLUS, GPIO.LOW)
      GPIO.output(IN4_BMINUS, GPIO.HIGH)
      sleep(delay)
      GPIO.output(IN1_APLUS, GPIO.LOW)
      GPIO.output(IN2_AMINUS, GPIO.HIGH)
      GPIO.output(IN3_BPLUS, GPIO.HIGH)
      GPIO.output(IN4_BMINUS, GPIO.LOW)
      sleep(delay)
  GPIO.output(IN1_APLUS, GPIO.LOW)
  GPIO.output(IN2_AMINUS, GPIO.LOW)
  GPIO.output(IN3_BPLUS, GPIO.LOW)
  GPIO.output(IN4_BMINUS, GPIO.LOW)

def openBlinds():
  filePtr = open( blindStateFile, "r")
  currentState = filePtr.read().strip()
  filePtr.close()
  if (currentState == closedState):
    print("Opening the blinds\n")
    clockwiseTurn(ROTATIONS_PER_CYCLE)
  filePtr = open( blindStateFile, "w")
  filePtr.write( openState + "\n")
  filePtr.close()

  #clockwiseTurn(ROTATIONS_PER_CYCLE)
      
def closeBlinds():
  filePtr = open( blindStateFile, "r")
  currentState = filePtr.read().strip()
  filePtr.close()
  if (currentState == openState):
    print("Closing the blinds\n")
    counterClockwiseTurn(ROTATIONS_PER_CYCLE)
  filePtr = open( blindStateFile, "w")
  filePtr.write( closedState + "\n")
  filePtr.close()

  #counterClockwiseTurn(ROTATIONS_PER_CYCLE)

if __name__ == '__main__':
  GPIO.setmode(GPIO.BCM)

  GPIO.setup(IN1_APLUS, GPIO.OUT)
  GPIO.setup(IN2_AMINUS, GPIO.OUT)
  GPIO.setup(IN3_BPLUS, GPIO.OUT)
  GPIO.setup(IN4_BMINUS, GPIO.OUT)

  app.run(debug=True, host='0.0.0.0')
