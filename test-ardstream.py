#! /usr/bin/python

from ArdIO import *
import time,io

ard = ArduinoSocketIO(blocking=True)

try:
  ard.setblocking(False)
  print ard.readlines()
except io.BlockingIOError:
  pass
ard.setblocking(True)

ard.write("M114\n")
time.sleep(0.2)
print ard.readline()
print ard.readline()

ard.close()
