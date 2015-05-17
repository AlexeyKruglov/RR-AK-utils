#! /usr/bin/python

def rotate2(phi, x,y):  # rotate phi radians CCW
  return (x*cos(phi) - y*sin(phi), y*cos(phi) + x*sin(phi))
def dist(x1,y1, x2,y2):
  return sqrt((x2-x1)**2 + (y1-y2)**2)

from math import *
import robot_geom
geom=robot_geom.RobotGeometryAK()

def XtoR(X):
  X,Y,Z=X, 30, 0
  x,y,z=geom.r2c(X,Y,Z)
  z=0
  return dist(x,y, geom.xx0, geom.yy0)


print 136.5, XtoR(136.5)
print 73, XtoR(73)
