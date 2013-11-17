#! /usr/bin/python

#import robot_geom
#geom=robot_geom.RobotGeometryAK()
#p0=geom.r2c(123.3,0,0)
#print p0
#exit()

from marlin_ak import *
import time

rr=MarlinCmdG()
rr.c("M205 Z10") # Max Z jerk, mm/sec
#rr.debug = True
rr.set_feedrate(100)

#rr.home()
rr.pick_pos()
rr.home_z()

p = rr.get_pos()
print p
print p[2]-4
z0=1.2
z1=z0+5

p=(p[0]-0,p[1]+0,p[2])
rr.go(x=p[0],y=p[1],z=z0)
#rr.go(x=p[0],y=p[1]+80,z=z0)
#rr.go(x=p[0]-80,y=p[1],z=z0)
rr.go(x=p[0]+80,y=p[1]+80,z=z0)
#p = rr.get_pos()
rr.go(x=p[0],y=p[1],z=z1)

rr.close()

