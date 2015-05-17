#! /usr/bin/python

def rotate2(phi, x,y):  # rotate phi radians CCW
  return (x*cos(phi) - y*sin(phi), y*cos(phi) + x*sin(phi))

from math import *
import robot_geom
geom=robot_geom.RobotGeometryAK()
geom.dR2_dz=0
geom.R2dphi2_dz=0

X,Y,Z=geom.c2r(-65, 113.5, -9.2)

phi1=(Y-geom.Yperp)/geom.phi1k
phi2=(X-geom.Xperp)/geom.phi2k-pi/2

R = geom.R2
phi = phi1+phi2
print phi, phi/pi*180

x,y = rotate2(-pi/4, 0.0369, 0.0108)
print x,y

dR,Rdphi = rotate2(-phi, x,y)
print dR,Rdphi
