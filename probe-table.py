#! /usr/bin/python

# Probe table's z position across the table

import marlin_ak
import time,sys
import math

rr = marlin_ak.MarlinCmd()
rr.set_feedrate(100)

#rr.c("M203 X150")  # Maximum speed, mm/s

rr.home()

#time.sleep(1)
#rr.home_z()

def probe1(x,y):
  rr.go(x=x,y=y)
  z0=rr.probe_z()
  sys.stdout.write("%.3f %.3f %.3f\n" % (x,y,z0))
  sys.stdout.flush()
  return z0

def probe_series_r(r):
  #rr.go(x=r)
  #step_y=45

  R1=161.
  R2=76.
  Xperp=91.
  phi1k=269.
  phi2k=115.
  phi2=math.pi/2+(r-Xperp)/phi2k
  R=math.sqrt(R1**2+R2**2-2*R1*R2*math.cos(phi2))/phi1k

  step_y=20/R
  if r>=45: y = -10
  else: y = 25
  while y<=310:
    probe1(r,y)
    y+=step_y
  probe1(r,310)
  sys.stdout.write("\n")
  sys.stdout.flush()

def probe_scan():
  #step_x=24
  step_x=20 *115./76.
  x=143
  while x<=143 and x>=-30:
    probe_series_r(x)
    x-=step_x
  probe_series_r(-30)

try:
  probe_scan()
  #probe_series_r(-30)
except KeyboardInterrupt:
  pass

#print "%.2f" % rr.probe_z()
#rr.go(y=30)
#print "%.2f" % rr.probe_z()
#rr.go(y=60)
#print "%.2f" % rr.probe_z()
###rr.go(123.3,0,0)
#rr.go(123.3,0,0)

rr.go(z=20)
rr.go(x=123, y=20)
rr.go(x=123, y=-5)
rr.close()
