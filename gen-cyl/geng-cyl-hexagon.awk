#! /usr/bin/awk -f

# Generage G-code(iter0) of a 1 layer helix cylinder

@include "geng-cyl.awkinc"

BEGIN {
  w=0.8; h=0.2; h0=0.35; w0=1.3
#  kpd=0.77*0.86; in_diam=2.9; ce=0  # ABS
#  kpd=0.965; in_diam=2.95; ce=0  # PLA
  kpd=1.06 * (0.6/0.8) * (0.65/0.8); in_diam=2.95; ce=0  # PLA
  in_area=in_diam^2 * pi/4

  n=6
  Wo = 9.8  # outer hexagon width (between the parallel sides)
  Z=3

  ra=(Wo-w)/2 / cos(pi/n)

  for(i=0; i<n; i++) { pzl[i]=pzr[i]=-h0 }  # i-th segment start and stop z

  zn=int(Z/h+1); h=Z/zn
  for(i=-n; i<=n*(zn+1); i++) {
    phi=-i/n*2*pi
    cz=i/n*h
    cw = cz<=0 ? w0 : w
    if(cz<0) cz=0; else if(cz>Z) cz=Z
    ipn = (i+n)%n
    cch = pcz-pzl[ipn]  # on the first call go() does not use cch in calculations
    go(ra*cos(phi), ra*sin(phi), cz, cz-pzr[ipn], cw)
    if(i>-n) { pzl[ipn]=pcz; pzr[ipn]=cz }  # since there's no segment produced on the first call
    pcz=cz
  }
}
