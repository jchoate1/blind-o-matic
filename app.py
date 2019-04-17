#!/usr/bin/python

from time import sleep
import blindControl as ctrl
import RPi.GPIO as GPIO
import sys, getopt
import pdb
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    text = open(ctrl.blindStateFile, 'r+')
    content = text.read()
    text.close()
            
    return render_template('index.html',content=content)

@app.route('/open/')
def opener():
    ctrl.openBlinds()
    content = ctrl.getBlindState(ctrl.blindStateFile)
    return render_template('index.html',content=content)
#    return 'Blinds are now Opened'

@app.route('/close/')
def closer():
    ctrl.closeBlinds()
    content = ctrl.getBlindState(ctrl.blindStateFile)
    return render_template('index.html',content=content)
#    return 'Blinds are now Closed.'

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
