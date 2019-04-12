#!/usr/bin/python

from time import sleep
import RPi.GPIO as GPIO
import sys, getopt
import pdb

PHOTO_INPUT = 4

def main(argv):
  # desiredAction=''
  # try:
  #   opts, args = getopt.getopt(argv,"hsa",["action=","state="])
  # except getopt.GetOptError:
  #   print 'blindomatic.py [-a (open, close)] [-s state (OPEN, CLOSED)]'
  #   sys.exit(2)
  # for opt,arg in opts:
  #   if opt == '-h':
  #     print 'blindomatic.py [-a (open, close)] [-s state (OPEN, CLOSED)]'
  #     sys.exit()
  #   elif opt in ( "-a", "--action"):
  #     desiredAction = arg
  #   elif opt in ("-s", "--state"):
  #     filePtr = open( blindStateFile, "w")
  #     filePtr.write( arg + "\n")
  #     filePtr.close()
  #     sys.exit()

  GPIO.setmode(GPIO.BCM)

  GPIO.setup(PHOTO_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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



