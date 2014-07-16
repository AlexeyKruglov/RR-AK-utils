#! /usr/bin/python

#import robot_geom
#geom=robot_geom.RobotGeometryAK()
#p0=geom.r2c(123.3,0,0)
#print p0
#exit()

from marlin_ak import *
import time
import math

e_feedrate=0.25  # mm/sec, incoming filament

def parseG(l):
  ls=l.split(" ")
  res=dict()
  for i in ls:
    res[i[0:1]]=float(i[1:])
  return res

inf=open("gen-cyl/cyl.g0", "r")

rr=MarlinCmdG()
#rr.c("M205 Z10") # Max Z jerk, mm/sec
rr.c("M205 X3 Z10") # Max jerk, mm/sec
#rr.debug = True
#rr.extrude = False
rr.set_feedrate(100)

rr.c("G92 E0")
rr.c("M302")

rr.home()
#rr.pick_pos()
#rr.home_z()

p = rr.get_pos()
print p

x0=-50.
y0=74.
z0=-7.4

print rr.geom.c2r(x0+2.85,y0,z0)

def dist(p0, p1):
  return math.sqrt((p1[0]-p0[0])**2 + (p1[1]-p0[1])**2)

def prime_to(p):
  rr.go(x0+p[0]+5., y0+p[1], z0+p[2]+3, f=20, wait=True)
  if rr.extrude: rr.c("M104 S182")
  time.sleep(10.-0.25)  # wait 10s
  rr.go(x0+p[0]+5., y0+p[1], z0+p[2], f=20)
  rr.go(x0+p[0], y0+p[1], z0+p[2], f=1./3)  # move 5mm for 15s


pp=None

for l in inf:
  print l[:-1]
  lp=parseG(l[:-1])
  if lp['G']==1.:
    cp = map(lambda x: lp[x], ['X','Y','Z','E'])

    if pp==None:
      prime_to(cp[0:3])
      e0 = -cp[3]
      pp=cp
      continue

    cdist = dist(pp[0:2], cp[0:2])
    edist = cp[3] - pp[3]

    if edist < 1e-6: edist = 1e-6
    cfeedrate = e_feedrate * cdist/edist  # in mm/sec in horizontal plane
    if cfeedrate > 149.: cfeedrate = 149.

    print "go %.3f %.3f %.3f %.3f @ %.2f" % (lp['X'], lp['Y'], lp['Z'], lp['E'], cfeedrate)
    rr.go(x = x0+cp[0], y = y0+cp[1], z = z0+cp[2], e = e0+cp[3], f = cfeedrate)

    pp=cp

pp[3]-=0.3
rr.go(x = x0+pp[0], y = y0+pp[1], z = z0+pp[2], e = pp[3], f = 1)
rr.go(x = x0+pp[0], y = y0+pp[1], z = z0+pp[2]+2, e = pp[3], f = 50.)
rr.go(x = x0+pp[0]+5., y = y0+pp[1], z = z0+pp[2]+2. , e = pp[3], f = 50.)
rr.go(x = x0+pp[0]+5., y = y0+pp[1], z = z0+pp[2]+30., e = pp[3], f = 50., wait=True)

if rr.extrude: rr.c("M104 S0")

rr.close()
inf.close()
