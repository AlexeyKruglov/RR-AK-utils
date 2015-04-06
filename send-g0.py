#! /usr/bin/python

#import robot_geom
#geom=robot_geom.RobotGeometryAK()
#p0=geom.r2c(123.3,0,0)
#print p0
#exit()

from marlin_ak import *
import time
import math

e_feedrate=0.2  # mm/sec, incoming filament
e_add = 0.

def parseG(l):
  ls=l.split(" ")
  res=dict()
  for i in ls:
    res[i[0:1]]=float(i[1:])
  return res

inf=open("gen-cyl/cyl.g", "r")

rr=MarlinCmdG()
#rr.c("M205 Z10") # Max Z jerk, mm/sec
rr.c("M205 X3 Z10") # Max jerk, mm/sec
#rr.debug = True
rr.extrude = True
#rr.extrude = False  # !!! debug
rr.set_feedrate(100)

rr.c("G92 E0")
e0=0
e_retract=0  # initialized by prime_to()
rr.c("M302")

rr.home()
#rr.pick_pos()
#rr.home_z()

p = rr.get_pos()
print p

## white paper piece
#x0=-50.
#y0=74.
#z0=-7.6

# yellow sticky paper
x0=-50.
y0=107.
z0=-8.1

# large yellow sticky paper pad
x0=-58.
y0=113.5+0.23
z0=-7.0

print rr.geom.c2r(x0+2.85,y0,z0)

def dist(p0, p1):
  return math.sqrt((p1[0]-p0[0])**2 + (p1[1]-p0[1])**2)

def prime_to_ABS(p):
  global e0, e_retract
  e_retract=0.3
  rr.go(x0+p[0]+5., y0+p[1], z0+p[2]+3., f=20, wait=True)
  if rr.extrude: rr.c("M104 S182")
  time.sleep(10.-2.)  # wait 10s
  rr.go(x0+p[0]+10., y0+p[1], z0+p[2]+3., f=20)
  rr.go(x0+p[0]+5., y0+p[1], z0+p[2], f=5)
  t_e = min(15, 0.3 / e_feedrate)
  x_e = 2.5
  rr.go(x0+p[0]+x_e, y0+p[1], z0+p[2], e0, f=1./3)  # move 5mm for 15s, no extrusion part
  e0 += e_retract
  rr.go(x0+p[0]    , y0+p[1], z0+p[2], e0, f=1./3)  # move 5mm for 15s, extrusion part

def prime_to_PLA(p, e_add1 = e_add):   # e_add = 2 when init'ing a new cut filament
  global e0, e_retract
  e_retract=15.
  rr.go(x0+p[0]+5.+e_add1*5, y0+p[1], z0+p[2]+3., f=20, wait=True)
  if rr.extrude: rr.c("M104 S240")
  if rr.extrude: time.sleep(40.-2.)  # wait 40s
  rr.go(x0+p[0]+15.+e_add1*5, y0+p[1], z0+p[2]+3., f=20)
  rr.go(x0+p[0]+10.+e_add1*5, y0+p[1], z0+p[2]+0.4, f=5)
  e0 += e_retract-1
  rr.go(x0+p[0]+10.+e_add1*5, y0+p[1], z0+p[2]+0.4, e0, f=10)  # extruder move to -1mm (assuming -20mm initial position)
  e0 += 2*0.96+e_add1
  rr.go(x0+p[0]+0.4, y0+p[1], z0+p[2]+0.4, e0, f=1)  # move 5mm for 10s, extrude 2mm (1mm avg)
  e0 += 2*0.04
  rr.go(x0+p[0]    , y0+p[1], z0+p[2]    , e0, f=1.4142, wait=True)
  if rr.extrude: rr.c("M104 S195")

def prime_to(p):
  prime_to_PLA(p)


pp_corr = None

def correct_pull(cp, pp, dt):
  global cp_cor, pp_corr

  if pp_corr == None:
    pp_corr = cp

  v = ( (cp[0]-pp[0])/dt, (cp[1]-pp[1])/dt)
  p1 = (cp[0] + tau1/dt*v[0], cp[1] + tau1/dt*v[1])
  p2 = ( cp_corr[0] + (p1[0] - cp_corr[0])*dt/tau2 , cp_corr[1] + (p1[1] - cp_corr[1])*dt/tau2 )

  pp_corr=cp_corrr
  return p2

pp=None
order=dict()
order['X']=0
order['Y']=1
order['Z']=2
order['E']=3

try:
 for l in inf:
  l = l[:-1]
  print l
  lp=parseG(l)
  if 'G' in lp and lp['G']==1.:
    print lp
    cp = map(lambda x: lp[x] if (x in lp) else pp[order[x]], ['X','Y','Z','E'])

    if pp==None:
      prime_to(cp[0:3])
      e0 -= cp[3]
      pp=cp
      continue

    cdist = dist(pp[0:2], cp[0:2])
    edist = cp[3] - pp[3]

    if False:  # feedrate calculation moved to const-flow.awk
      if edist < 1e-6: edist = 1e-6
      cfeedrate = e_feedrate * cdist/edist  # in mm/sec in horizontal plane
      if cfeedrate > 149.: cfeedrate = 149.

    #cp_corr = correct_pull(cp, pp, edist/e_feedrate)

    if 'F' in lp:
      cfeedrate = lp['F']/60
    else:
      cfeedrate = None

    print "go %.3f %.3f %.3f %.3f @ %.2f" % (cp[0], cp[1], cp[2], cp[3], cfeedrate)
    rr.go(x = x0+cp[0], y = y0+cp[1], z = z0+cp[2], e = e0+cp[3], f = cfeedrate)

    pp=cp
  elif 'G' in lp and lp['G']==4.:
    rr.c(l)

finally:
  if pp!=None:
    rr.go(x = x0+pp[0], y = y0+pp[1], z = z0+pp[2]+2, e = e0+pp[3], f = 50.)
    e0 -= e_retract
    rr.go(x = x0+pp[0], y = y0+pp[1], z = z0+pp[2]+2, e = e0+pp[3], f = 5.)
    e_retract=0
    rr.go(x = x0+pp[0]+5., y = y0+pp[1], z = z0+pp[2]+2. , e = e0+pp[3], f = 50.)
    rr.go(x = x0+pp[0]+5., y = y0+pp[1], z = z0+pp[2]+30., e = e0+pp[3], f = 50., wait=True)

    if rr.extrude: rr.c("M104 S0")

    rr.close()
    inf.close()
