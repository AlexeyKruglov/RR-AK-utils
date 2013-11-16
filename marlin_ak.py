# Communication with Marlin firmware running on AK's printer

import ArdIO
import time,io
import robot_geom

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
    self.set_feedrate(f=25)  # 25 mm/sec = default feedrate in Marlin

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

  def go(self, x=None, y=None, z=None, f=None, wait=False):  # !!! assume absolute positioning
    cmd="G1"
    if x != None: cmd += " X%.2f" % x
    if y != None: cmd += " Y%.2f" % y
    if z != None: cmd += " Z%.2f" % z
    if f != None: cmd += " F%.2f" % f
    self.c(cmd, check_ok=True)
    if wait:
      self.wait()

  def get_pos(self): # return position as a 3-tuple
    # Will return 4-tuple or smth else in the future
    st=self.c("M114", check_ok=True)  # Get position
    try:
      l0=l[0]
      l0 = l0[0:l.index(" ")]
      #  X:0.00Y:0.00Z:0.00E:0.00
      l0 = l0.split(":")[1:]
      l0 = map(lambda x: float(x.rstrip("XYZE")),l0)
      if length(l0) != 4: raise
      return tuple(l0[0:3])
    except:
      raise RRError("M114","cannot parse: " + "|".join(l))

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

import math

# Not reenterant!
class MarlinCmdG(MarlinCmd):  # wrapper 
  cx=0
  cy=0
  cz=0
  homed = False
  f=25  # default feedrate = 25 mm/sec
  geom=robot_geom.RobotGeometryAK()
  maxd=1  # mm
  debug = False or True

  def __init__(self, check_ok = True, timeout=None, echo=sys.stderr):  # check_ok = raise RRError on non-ok (Error) command results
    MarlinCmd.__init(self, check_ok=check_ok, timeout=timeout, echo=echo)

  def home(self):
    MarlinCmd.home(self)
    self.wait()
    self.cx, self.cy, self.cz = self.geom.r2c(MarlinCmd.get_pos(self))
    self.homed = True

  def home_z(self):
    MarlinCmd.home_z(self)
    self.wait()
    self.cx, self.cy, self.cz = self.geom.r2c(MarlinCmd.get_pos(self))

  def set_feedrate(self, f):
    self.f=f
    # Do not sent command since real/raw feedrate ratio depends on travel direction

  def goraw(self, *args):
    if not self.debug: 
      MarlinCmd.go(self, *args)
    else 
      sys.stderr.write("Go %f,%f,%f, %f\n" % (x,y,z,f))

  def get_pos(self): # return position as a 3-tuple
    return (self.cx, self.cy, self.cz)

  def go(self, x=self.cx, y=self.cy, z=self.cz, f=self.f, wait=False):  # !!! assume absolute positioning
    if not self.homed:
      raise RRError("go", "must home() before go()")
    self.f = f
    cx,cy,cz = x,y,z
    cX,cY,cZ = self.geom.c2r(cx,cy,cz)
    dx, dy, dz = x-cx, y-cy, z-cz
    d = math.sqrt(dx**2 + dy**2 + dz**2)
    n = math.ceil(d/self.maxd)
    if n<1: n=1
    dx, dy, dz = dx/n, dy/n, dz/n
    d /= n
    for i in range(n): 
      cx+=dx
      cy+=dy
      cz+=dz
      pX,pY,pZ = cX,cY,cZ
      cX,cY,cZ = self.geom.c2r(cx,cy,cz)
      d_raw = math.sqrt((cX-pX)**2 + (cY-pY)**2 + (cZ-pZ)**2)

      self.goraw(x=cx, y=cy, z=cz, f=self.f * d/d_raw, wait = i == n-1 and wait)  # wait only after the last segment
    self.cx,self.cy,self.cz = x,y,z
