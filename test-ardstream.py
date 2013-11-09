#! /usr/bin/python

from ArdIO import *
import time,io

ard = ArduinoSocketIO(blocking=False)

try:
  print ard.readlines()
except io.BlockingIOError:
  pass

ard.write("M114\n")
time.sleep(0.2)
print ard.readline()
print ard.readline()

ard.close()
