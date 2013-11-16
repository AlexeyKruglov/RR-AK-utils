# Communication with Marlin firmware running on AK's printer

import ArdIO
import time,io

class RRError(Exception):
  def __str__(self):
    return "%s: %s" % self.args

class MarlinCmd:  # Marlin commander class
  ard = None
  check_ok = None
  timeout = None
  echo = None

  def __init__(self, check_ok = True, timeout=None, echo=sys.stderr):  # check_ok = raise RRError on non-ok (Error) command results
    self.check_ok = check_ok
    self.timeout = timeout
    self.echo = echo
    self.ard = ArdIO.ArduinoSocketIO(blocking=True, echo=False)
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

  def c(self, cmd, timeout=None, check_ok=None, echo=None):  # cmd = command without LF
    if timeout == None: timeout = self.timeout
    if check_ok == None: check_ok = self.check_ok
    if echo == None: echo = self.echo

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
      if echo != None and resp2[0:len("echo:")]=="echo:":
        echo.write(resp + "\n")
      if resp2[0:len("Error:")]=="Error:":
        if check_ok:
          raise RRError(cmd, resp)
        return out
      if timeout != None and time.time() > timeout_time:
        if check_ok:
          raise RRError(cmd, "Timeout")
        return None

  def set_feedrate(self, f):
    self.c("G1 F%.1f\n" % (f*60), check_ok=True)

  def go(self, x=None, y=None, z=None, wait=False):  # !!! assume absolute positioning
    cmd="G1"
    if x != None: cmd += " X%.2f" % x
    if y != None: cmd += " Y%.2f" % y
    if z != None: cmd += " Z%.2f" % z
    self.c(cmd, check_ok=True)
    if wait:
      self.wait()

  def get_es(self): # return dict with endstop states
    st=self.c("M119", check_ok=True)  # Get endstop status
    res=dict()
    for l in st[1:-1]:
      x,s = l.split(": ")
      res[x]=s.upper()!="OPEN"
    return res

  def wait(self, time=0):  # Wait for completion of buffered commands + time seconds
    self.c("G4 P%.0f" % (time*1e3), check_ok=True)  # Wait

  def home(self):
    self.c("M80", check_ok=True)  # ATX power on
    self.c("G21", check_ok=True)  # Set units to mm
    es=self.get_es()
    if es["z_min"]:  # too low, go up
      self.c("G92 Z0", check_ok=True)  # set logical position
      self.c("G1 Z30", check_ok=True)  # Go 30mm up
      self.wait()
    if es["y_min"]:  # too close, go deeper
      self.c("G92 Y0", check_ok=True)  # set logical position
      self.c("G1 Y30", check_ok=True)  # Go 30mm deep
      self.wait()
    if es["x_max"]:  # too right, go left
      self.c("G92 X30", check_ok=True)  # set logical position
      self.c("G1 X0", check_ok=True)  # Go 30mm left
      self.wait()
    self.c("G28", check_ok=True)  # Go home

  def home_z(self):
    self.go(z=2, wait=True)
    self.c("G28 Z0", check_ok=True)

  def probe_z(self, es="z_max", z0=0, maxz=0, minz=-6):  # probe vertically with z probe at z_max endstop
    self.c("M205 Z0.1", check_ok=True)  # Maximum z jerk, mm/s
    self.c("M201 Z200", check_ok=True)  # Maximum z acceleration, mm/s^2
    self.home_z()
    step=0.5
    delay=0.1
    cz=maxz
    # self.c("G1 Z%.2f" % cz, check_ok=True)
    self.go(z=cz, wait=True)
    time.sleep(delay)
    while not self.get_es()[es] and cz-step>=minz:
      cz -= step
      #print cz
      # self.c("G1 Z%.2f" % cz, check_ok=True)
      self.go(z=cz, wait=True)
      time.sleep(delay)

    if self.get_es()[es]:
      cz += step
      self.home_z()
      delay = 0.05
      step = 1/46.3
      cz += step*4
      # self.c("G1 Z%.2f" % cz, check_ok=True)
      self.go(z=cz, wait=True)
      time.sleep(delay)
      while not self.get_es()[es] and cz-step>=minz:
        cz -= step
        #print cz
        # self.c("G1 Z%.2f" % cz, check_ok=True)
        self.go(z=cz, wait=True)
        time.sleep(delay)

    # self.c("G1 Z%.2f" % z0, check_ok=True)
    self.go(z=z0)
    return cz+step/2
