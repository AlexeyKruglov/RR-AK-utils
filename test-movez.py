#! /usr/bin/python

#import robot_geom
#geom=robot_geom.RobotGeometryAK()
#p0=geom.r2c(123.3,0,0)
#print p0
#exit()

from marlin_ak import *
import time,sys

rr=MarlinCmdG()
rr.c("M205 Z10") # Max Z jerk, mm/sec
#rr.debug = True
rr.set_feedrate(100)

#rr.home()
rr.pick_pos()
rr.home_z()

p0 = rr.get_pos()

try:
  while True:
    p = rr.get_pos()
    print p
    print rr.geom.c2r(p[0],p[1],p[2])
    cmd=sys.stdin.readline()
    if cmd[0:1]=="c":  # put a cross at z=arg
      z=float(cmd[1:])
      rr.go(z=z+2)
      size=2  # half-size, mm
      rr.go(x=p[0]-size, y=p[1], z=z)
      rr.go(x=p[0]+size, y=p[1], z=z)
      rr.go(x=p[0], y=p[1]-size, z=z+2)
      rr.go(x=p[0], y=p[1]-size, z=z)
      rr.go(x=p[0], y=p[1]+size, z=z)
      rr.go(x=p[0], y=p[1], z=30)
    elif cmd[0:1]=="Z":  # go z=arg (Cartesian)
      z=float(cmd[1:])
      rr.go(z=z)
    elif cmd[0:1]=="X":  # go x=arg (Cartesian)
      x=float(cmd[1:])
      rr.go(x=x)
    elif cmd[0:1]=="Y":  # go y=arg (Cartesian)
      y=float(cmd[1:])
      rr.go(y=y)
    elif cmd[0:1]=="z":  # go Z=arg
      z=float(cmd[1:])
      rr.goraw(z=z)
      rr.pick_pos()
    elif cmd[0:1]=="x":  # go X=arg
      x=float(cmd[1:])
      rr.goraw(x=x)
      rr.pick_pos()
    elif cmd[0:1]=="y":  # go Y=arg
      y=float(cmd[1:])
      rr.goraw(y=y)
      rr.pick_pos()
    elif cmd[0:1]=="h":  # home
      rr.home()
    elif cmd[0:1]=="H":  # home z
      rr.home_z()
      rr.pick_pos()
    else:  # go z = z+arg
      dz=float(cmd)
      z=p[2]+dz
      rr.go(z=z)
finally:
  rr.close()

