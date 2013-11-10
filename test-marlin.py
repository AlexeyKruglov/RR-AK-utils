#! /usr/bin/python

from ArdIO import *
import time,io

class RRError(Exception):
  pass
  def __str__(self):
    return "%s: %s" % self.args

class MarlinCmd:  # Marlin commander class
  ard = None
  check_ok = None
  timeout = None

  def __init__(self, check_ok = True, timeout=None):  # check_ok = raise RRError on non-ok (Error) command results
    self.check_ok = check_ok
    self.timeout = timeout
    self.ard = ArduinoSocketIO(blocking=True, echo=False)
    time.sleep(0.1)
    self.eat_input()

  def __del__(self):
    self.close()

  def close(self):
    if self.ard != None: self.ard.close()

  # Eat up the old input
  def eat_input(self):
    self.ard.setblocking(False)
    try:
      print self.ard.readlines()
    except io.BlockingIOError:
      pass
    self.ard.setblocking(True)

  def c(self, cmd, timeout=None, check_ok=None):  # cmd = command without LF
    if timeout == None: timeout = self.timeout
    if check_ok == None: check_ok = self.check_ok

    self.eat_input()
    self.ard.write(cmd+"\n")

    timeout_=None
    if timeout != None: timeout_=1
    if timeout_>timeout: 
      timeout_ = timeout
    self.ard.settimeout(timeout_)

    out=[]
    if timeout != None: timeout_time = time.time() + timeout
    while True:
      resp = self.ard.readline()
      resp = resp[0:-1]
      out.append(resp)
      resp2 = resp + " "
      if resp2[0:3]=="ok ":
        return out
      if resp2[0:len("Error:")]=="Error:":
        if check_ok:
          raise RRError(cmd, resp)
        return out
      if timeout != None and time.time() > timeout_time:
        if check_ok:
          raise RRError(cmd, "Timeout")
        return None

  def go(self, x=None, y=None, z=None):  # !!! assume absolute positioning
    cmd="G1"
    if x != None: cmd += " X%.2f" % x
    if y != None: cmd += " Y%.2f" % y
    if z != None: cmd += " Z%.2f" % z
    self.c(cmd, check_ok=True)

  def get_es(self): # return dict with endstop states
    st=self.c("M119", check_ok=True)  # Get endstop status
    res=dict()
    for l in st[1:-1]:
      x,s = l.split(": ")
      res[x]=s.upper()!="OPEN"
    return res

  def home(self):
    print self.c("M80", check_ok=True)  # ATX power on
    print self.c("G21", check_ok=True)  # Set units to mm
    es=self.get_es()
    if es["z_min"]:  # too low, go up
      print self.c("G92 Z0", check_ok=True)  # set logical position
      print self.c("G1 Z30", check_ok=True)  # Go 30mm up
    if es["y_min"]:  # too close, go deeper
      print self.c("G92 Y0", check_ok=True)  # set logical position
      print self.c("G1 Y30", check_ok=True)  # Go 30mm deep
    if es["x_max"]:  # too right, go left
      print self.c("G92 X30", check_ok=True)  # set logical position
      print self.c("G1 X0", check_ok=True)  # Go 30mm left
    print self.c("G28", check_ok=True)  # Go home

  def home_z(self):
    self.c("G1 Z2", check_ok=True)
    self.c("G28 Z0", check_ok=True)

  def probe_z(self, es="z_max", z0=0, maxz=0, minz=-5.5):  # probe vertically with z probe at z_max endstop
    self.c("M205 Z0.1", check_ok=True)  # Maximum z jerk, mm/s
    self.c("M201 Z200", check_ok=True)  # Maximum z acceleration, mm/s^2
    self.home_z()
    step=0.5
    delay=0.25*4
    cz=maxz
    # self.c("G1 Z%.2f" % cz, check_ok=True)
    self.go(z=cz)
    time.sleep(delay)
    while not self.get_es()[es] and cz-step>=minz:
      cz -= step
      print cz
      # self.c("G1 Z%.2f" % cz, check_ok=True)
      self.go(z=cz)
      time.sleep(delay)

    if self.get_es()[es]:
      cz += step
      #self.home_z()
      step = 0.1
      # self.c("G1 Z%.2f" % cz, check_ok=True)
      self.go(z=cz)
      time.sleep(delay)
      while not self.get_es()[es] and cz-step>=minz:
        cz -= step
        print cz
        # self.c("G1 Z%.2f" % cz, check_ok=True)
        self.go(z=cz)
        time.sleep(delay)

    # self.c("G1 Z%.2f" % z0, check_ok=True)
    self.go(z=z0)
    return cz+step/2

rr = MarlinCmd()



#ard.write("M114\n")
#time.sleep(0.2)
#print ard.readline()
#print ard.readline()

#print rr.c("G28")
#print get_es()
#print rr.c("G1 Z0")
#print rr.c("G28")

#rr.c("M203 X150")  # Maximum speed, mm/s

rr.home()

time.sleep(1)
rr.home_z()

exit()

print rr.probe_z()
#rr.go(y=30)
#print rr.probe_z()
#rr.go(y=60)
#print rr.probe_z()
##rr.go(123.3,0,0)
#rr.go(123.3,0,0)

rr.close()
