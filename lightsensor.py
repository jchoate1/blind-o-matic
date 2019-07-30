#!/usr/bin/python

# Quick test program to play with the light sensor.

from time import sleep
import RPi.GPIO as GPIO
import sys, getopt
import pdb

PHOTO_INPUT = 4

def main(argv):

  GPIO.setmode(GPIO.BCM)
  GPIO.setup(PHOTO_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setwarnings(False)

  try:
    while True:
      lightData=GPIO.input(PHOTO_INPUT)
      if lightData:
        print "It is very dark in here"
      else:
        print "It is very light in here"
      sleep( 2 ) 
  except (KeyboardInterrupt, SystemExit):
            raise
  except:
    GPIO.cleanup() # ensures a clean exit
    sys.exit(2)
    
if __name__ == "__main__":
  main(sys.argv[1:])



