#! /usr/bin/python

#import robot_geom
#geom=robot_geom.RobotGeometryAK()
#p0=geom.r2c(123.3,0,0)
#print p0
#exit()

from marlin_ak import *
import time

rr=MarlinCmdG()
#rr.c("M205 Z10") # Max Z jerk, mm/sec
rr.c("M205 X3 Z10") # Max Z jerk, mm/sec
#rr.debug = True
rr.set_feedrate(100)

#rr.home()
rr.pick_pos()
rr.home_z()

p = rr.get_pos()
print p
print p[2]-4
z0=-0.3
z1=z0+5

def peano(n,o0,o1, x0,x1,y0,y1):
  if(n<=0):
    rr.go(x=o0+x0/2+y0/2,y=o1+x1/2+y1/2,z=z0)
    return
  peano(n-1, o0,o1, y0/2,y1/2, x0/2,x1/2)
  o0+=y0/2
  o1+=y1/2
  peano(n-1, o0,o1, x0/2,x1/2, y0/2,y1/2)
  o0+=x0/2
  o1+=x1/2
  peano(n-1, o0,o1, x0/2,x1/2, y0/2,y1/2)
  o0+=x0/2
  o1+=x1/2
  peano(n-1, o0,o1, -y0/2,-y1/2, -x0/2,-x1/2)

o=(182.023,-73.438,6.217)

p=(o[0]-0,o[1]+20,p[2])
#p=(p[0]+20,p[1]+0,p[2])
rr.go(x=p[0],y=p[1],z=z1)
peano(4,p[0],p[1], -20.,0., 0.,20.)
#exit()
#rr.go(x=p[0],y=p[1],z=z0)
#rr.go(x=p[0],y=p[1]+20,z=z0)
#rr.go(x=p[0]-100,y=p[1],z=z0)
#rr.go(x=p[0]+10,y=p[1]+80,z=z0)
p = rr.get_pos()
rr.go(x=p[0],y=p[1],z=z1)

rr.close()

