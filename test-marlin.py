#! /usr/bin/python

from ArdIO import *
import time,io

# Eat up the old input
def eat_input():
  time.sleep(0.1)
  ard.setblocking(False)
  try:
    print ard.readlines()
  except io.BlockingIOError:
    pass
  ard.setblocking(True)

ard = ArduinoSocketIO(blocking=True, echo=False)
eat_input()

def marlincmd(s, timeout=None):  # s = command without LF
  eat_input()
  ard.write(s+"\n")

  timeout_=None
  if timeout != None: timeout_=1
  if timeout_>timeout: 
    timeout_ = timeout
  ard.settimeout(timeout)

  out=[]
  if timeout != None:timeout_time=time.time() + timeout
  while True:
    resp=ard.readline()
    resp = resp[0:-1]
    out.append(resp)
    resp += " "
    if resp[0:3]=="ok " or resp[0:len("Error:")]=="Error:":
      return out
    if timeout != None and time.time()>timeout_time:
      return None


  

#ard.write("M114\n")
#time.sleep(0.2)
#print ard.readline()
#print ard.readline()

print marlincmd("G28")

ard.close()
