# Communication with Marlin firmware running on AK's printer

import ArdIO
import time,io,sys
import robot_geom

class RRError(Exception):
  def __str__(self):
    return "%s: %s" % self.args

class MarlinCmd:  # Marlin commander class
  ard = None
  check_ok = None
  timeout = None
  echo = None

  extrude=False  # set to False to prevent extrusion

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

  def go(self, x=None, y=None, z=None, e=None, f=None, wait=False):  # !!! assume absolute positioning
    cmd="G1"
    if x != None: cmd += " X%.3f" % x
    if y != None: cmd += " Y%.3f" % y
    if z != None: cmd += " Z%.3f" % z
    if e != None and self.extrude: cmd += " E%.3f" % e
    if f != None: cmd += " F%.1f" % (f*60)
    self.c(cmd, check_ok=True)
    if wait:
      self.wait()

  def get_pos(self): # return position as a 3-tuple
    # Will return 4-tuple or smth else in the future
    l=self.c("M114", check_ok=True)  # Get position
    try:
      l0=l[0]
      #print l0
      l0 = l0[0:l0.index(" Count")]
      #print l0
      #  X:0.00Y:0.00Z:0.00E:0.00
      l0 = l0.split(":")[1:]
      #print l0
      l0 = map(lambda x: float(x.rstrip("XYZE ")),l0)
      #print l0
      if len(l0) < 4: raise
      return tuple(l0[0:3])
    except Exception as e:
      raise RRError("M114","cannot parse: " + "|".join(l) + " exc: " + str(e))

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
      self.c("G1 Z30 F1000", check_ok=True)  # Go 30mm up
      self.wait()
    if es["y_min"]:  # too close, go deeper
      self.c("G92 Y0", check_ok=True)  # set logical position
      self.c("G1 Y30 F1000", check_ok=True)  # Go 30mm deep
      self.wait()
    if es["x_max"]:  # too right, go left
      self.c("G92 X30", check_ok=True)  # set logical position
      self.c("G1 X0 F1000", check_ok=True)  # Go 30mm left
      self.wait()
    self.c("G28", check_ok=True)  # Go home

  def home_z(self):
    MarlinCmd.go(self, z=2, f=16.6666, wait=True)
    self.c("G28 Z0", check_ok=True)

  def probe_z(self, es="z_max", z0=0, maxz=0, minz=-8):  # probe vertically with z probe at z_max endstop
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
  ce=0   # !!!!!!!!!!!!!!!!! assumes E=0 every start!  FIX IT!!!!!
  homed = False
  f=25  # default feedrate = 25 mm/sec
  geom=robot_geom.RobotGeometryAK()
  maxd=0.5  # mm
  debug = False #or True

  #def __init__(self, check_ok = True, timeout=None, echo=sys.stderr):  # check_ok = raise RRError on non-ok (Error) command results
  #  MarlinCmd.__init__(self, check_ok=check_ok, timeout=timeout, echo=echo)

  def home(self):
    MarlinCmd.home(self)
    self.wait()
    time.sleep(0.5) # Oscillation dampling
    self.pick_pos()

  def home_z(self):
    MarlinCmd.home_z(self)
    self.wait()
    self.pick_pos(set_homed = False)

  def pick_pos(self, set_homed = True):  # pick current position with M114 command
    X,Y,Z = MarlinCmd.get_pos(self)
    self.cx, self.cy, self.cz = self.geom.r2c(X,Y,Z)
    if set_homed: self.homed = True

  def set_feedrate(self, f):
    self.f=f
    # Do not sent command since real/raw feedrate ratio depends on travel direction

  def goraw(self, *args, **keys):
    if not self.debug: 
      MarlinCmd.go(self, *args, **keys)
    else:
      #sys.stderr.write("Go %s\n" % str(args))
      sys.stderr.write("Go %f,%f,%f, %f\n" % (keys["x"],keys["y"],keys["z"],keys["f"]))

  def get_pos(self): # return position as a 3-tuple
    return (self.cx, self.cy, self.cz)

  def go(self, x=None, y=None, z=None, e=None, f=None, wait=False):  # !!! assume absolute positioning
    if not self.homed:
      raise RRError("go", "must home() before go()")
    if x==None: x=self.cx
    if y==None: y=self.cy
    if z==None: z=self.cz
    if e==None: e=self.ce
    if f==None: f=self.f
    self.f = f
    cx,cy,cz,ce = self.cx,self.cy,self.cz,self.ce
    cX,cY,cZ = self.geom.c2r(cx,cy,cz)
    dx, dy, dz, de = x-cx, y-cy, z-cz, e-ce
    d = math.sqrt(dx**2 + dy**2 + dz**2)
    n = int(math.ceil(d/self.maxd))
    #print "n=", n
    if n<1: n=1
    dx, dy, dz, de = dx/n, dy/n, dz/n, de/n
    d /= n
    self.goraw(x=cX, y=cY, z=cZ, e=ce, f=self.f, wait = False)  # wait only after the last segment
    for i in range(n): 
      cx+=dx
      cy+=dy
      cz+=dz
      ce+=de
      pX,pY,pZ = cX,cY,cZ
      cX,cY,cZ = self.geom.c2r(cx,cy,cz)
      d_raw = math.sqrt((cX-pX)**2 + (cY-pY)**2 + (cZ-pZ)**2)
      #print "d=%f d_raw=%f" % (d,d_raw)

      self.goraw(x=cX, y=cY, z=cZ, e=ce, f=self.f * (d_raw+1e-5)/(d+1e-5), wait = wait and i == n-1)  # wait only after the last segment
    self.cx,self.cy,self.cz,self.ce = x,y,z,e
