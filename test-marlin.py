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

def marlincmd(s, timeout=None, check_ok=True):  # s = command without LF
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
      if check_ok and resp[0:3]!="ok ":
        raise
      return out
    if timeout != None and time.time()>timeout_time:
      return None


def get_es(): # return dict with endstop states
  st=marlincmd("M119")  # Get endstop status
  if st[-1] != "ok": raise
  res=dict()
  for l in st[1:-1]:
    x,s = l.split(": ")
    res[x]=s.upper()!="OPEN"
  return res

def gohome():
  print marlincmd("M80")  # ATX power on
  print marlincmd("G21")  # Set units to mm
  es=get_es()
  if es["z_min"]:  # too low, go up
    print marlincmd("G92 Z0")  # set logical position
    print marlincmd("G1 Z30")  # Go 30mm up
  if es["y_min"]:  # too close, go up
    print marlincmd("G92 Y0")  # set logical position
    print marlincmd("G1 Y30")  # Go 30mm deep
  if es["x_max"]:  # too right, go up
    print marlincmd("G92 X30")  # set logical position
    print marlincmd("G1 X0")  # Go 30mm left
  print marlincmd("G28")  # Go home

def reset_z():
  return
  marlincmd("G1 Z2")
  marlincmd("G28 Z0")

def probe_z(es="z_max", z0=0, maxz=0, minz=-5.5):  # probe vertically with z probe at z_max endstop
  marlincmd("M205 Z0.1")  # Maximum z jerk, mm/s
  marlincmd("M201 Z200")  # Maximum z acceleration, mm/s^2
  reset_z()
  step=0.5
  delay=0.5
  cz=maxz
  marlincmd("G1 Z%.2f" % cz)
  while not get_es()[es] and cz-step>=minz:
    cz -= step
    time.sleep(delay)
    #print cz
    marlincmd("G1 Z%.2f" % cz)
  if get_es()[es]:
    cz += step
    reset_z()
    step = 0.1
    marlincmd("G1 Z%.2f" % cz)
    time.sleep(delay)
    while not get_es()[es] and cz-step>=minz:
      cz -= step
      #print cz
      marlincmd("G1 Z%.2f" % cz)
      time.sleep(delay)
  marlincmd("G1 Z%.2f" % z0)
  return cz+step/2

def go(x=None,y=None,z=None):
  cmd="G1"
  if x!=None: cmd += " X%.2f" % x
  if y!=None: cmd += " Y%.2f" % y
  if z!=None: cmd += " Z%.2f" % z
  marlincmd(cmd)

#ard.write("M114\n")
#time.sleep(0.2)
#print ard.readline()
#print ard.readline()

#print marlincmd("G28")
#print get_es()
#print marlincmd("G1 Z0")
#print marlincmd("G28")

marlincmd("M203 X150")  # Maximum speed, mm/s
gohome()
print probe_z()
go(y=30)
print probe_z()
go(y=60)
print probe_z()
go(123.3,0,0)

ard.close()
