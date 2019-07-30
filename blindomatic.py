#!/usr/bin/python

import blindControl as ctrl
from time import sleep
import RPi.GPIO as GPIO
import sys, os, getopt
import datetime
import pdb


def main(argv):

  # Make a mapping of possible user requested states to the
  # corresponding action that should be called for the action
  functionMap={}
  actionMap={
    ('auto','AUTO','automatic', 'AUTOMATIC') : ctrl.autoBlinds,
    ('open','OPEN','opened', 'OPENED') : ctrl.openBlinds,
    ('close','CLOSE','CLOSED','closed') : ctrl.closeBlinds,
    ('reset','RESET') : ctrl.resetControl,
    }
  for strings, fun in actionMap.items():
    for key in strings:
      functionMap[ key ] = fun

  # process command line arguments    
  try:
    opts, args = getopt.getopt(argv,"a:hs",["action=","state="])
  except getopt.GetOptError:
    print 'blindomatic.py -a (open, close, auto, reset) [-s state (OPEN, CLOSED)]'
    sys.exit(2)
  for opt,arg in opts:
    if opt == '-h':
      print 'blindomatic.py [-a (open, close, auto, reset)] [-s state (OPEN, CLOSED)]'
      sys.exit()
    elif opt in ( "-a", "--action"):
      if not arg in functionMap:
        print 'blindomatic.py [-a (open, close, auto, reset)] [-s state (OPEN, CLOSED)]'
        sys.exit()
      else:
        desiredAction = functionMap[arg]
    elif opt in ("-s", "--state"):
      filePtr = open( ctrl.blindStateFile, "w")
      if (arg in ['OPEN', 'open', 'OPENED', 'opened']):
          filePtr.write( ctrl.openState + "\n")
      elif (arg in ['CLOSE', 'close', 'CLOSED', 'closed']):
          filePtr.write( ctrl.closedState + "\n")
      else:
          filePtr.write( ctrl.unknownState + "\n")
      filePtr.close()
      sys.exit()

  # Make sure we have the current state of blinds before we do something.
  initialState = ctrl.getBlindState(ctrl.blindStateFile)

  # Do the task that the user wanted, cleanup afterwards if approproiate.
  if desiredAction():
    GPIO.cleanup() # ensures a clean exit

if __name__ == "__main__":
  main(sys.argv[1:])
