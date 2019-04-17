# blind-o-matic
Hackathon project for automatic blind control

This was my project for the Arista Hack-a-thon held in March, 2019.  We had 24 hours to create, implement, test, debug and release a pjoject of our choosing.  I chose to use a stepper motor and a light sensor along with a Raspberry Pi to automatically control the vertical blinds by my desk. 

This project is a result of that effort.  There are 3 ways of controlling the motor that drives the blinds.  This repo has the software to do that.  blindomatic.py contains the CLI interface to the driver, there is online help for that.  It also contains the automatic mode which uses a light sensor to operate the blinds based on the ambient light level.  webBlind.py is a flask app that provides a web interface to control the blinds manually.  You can run this and browse to the address and click the button for the action you want to do.

The web interface is very rudimentary, but I only had 24 hours to get all of the software done as well as getting the stepper motor successfully wired and rigged to the blinds!  

The presentation for the project that was presented at the end can be found in the slide presentation.
