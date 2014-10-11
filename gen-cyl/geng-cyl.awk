#! /usr/bin/awk -f

# Generage G-code(iter0) of a 1 layer helix cylinder

@include "geng-cyl.awkinc"

BEGIN {
  w=0.75; h=0.2; h0=0.45; w0=0.75
#  kpd=0.77*0.86; in_diam=2.9; ce=0  # ABS
#  kpd=0.965; in_diam=2.95; ce=0  # PLA
  kpd=1.06; in_diam=2.95; ce=0  # PLA
  in_area=in_diam^2 * pi/4

  Di=3.5; step=0.5
  Z=2

  ra=(Di+w)/2
  n=int(pi*2*ra/step+1)

  for(i=0; i<n; i++) pz[i]=-h0

  zn=int(Z/h+1); h=Z/zn
  for(i=-n; i<=n*(zn+1); i++) {
    phi=-i/n*2*pi
    cz=i/n*h
    cw = cz<=0 ? w0 : w
    if(cz<0) cz=0; # else if(cz>Z) cz=Z
    ipn = (i+n)%n; go(ra*cos(phi), ra*sin(phi), cz, cz-pz[ipn], cw); if (i>-n) pz[ipn]=cz
  }
}
