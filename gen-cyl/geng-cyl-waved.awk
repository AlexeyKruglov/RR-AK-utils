#! /usr/bin/awk -f

# Generage G-code(iter0) of a 1 layer helix cylinder

@include "geng-cyl.awkinc"

BEGIN {
  w=0.7; h=0.2; h0=0.45
  kpd=0.77*0.86; in_diam=2.9; ce=0
  in_area=in_diam^2 * pi/4

  Di=4.9; Do=8.1+0.35; nw=8
  step=0.25
  Z=6.5

  ra = (Di+Do)/4
  rd = (Do-Di-2*w)/4
  n=int(pi*2*ra/step+1)

  for(i=0; i<n; i++) pz[i]=-h0

  zn=int(Z/h+1); h=Z/zn
  for(i=-n; i<=n*(zn+1); i++) {
    phi=-i/n*2*pi
    phiw = phi*nw
    cz=i/n*h
    cw = cz<=0 ? w0 : w
    if(cz<0) cz=0; else if(cz>Z) cz=Z

    add_r = (cz<0.5 ? 0.5-cz : 0)/2
    cr = (ra+add_r) + (rd+add_r)*cos(phiw)

    ipn = (i+n)%n; go(cr*cos(phi), cr*sin(phi), cz, cz-pz[ipn], cw); if (i>-n) pz[ipn]=cz
  }
}
