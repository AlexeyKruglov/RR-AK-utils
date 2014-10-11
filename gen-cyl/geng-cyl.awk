#! /usr/bin/awk -f

# Generage G-code(iter0) of a 1 layer helix cylinder

function dist(x0,y0, x1,y1) {
  return sqrt((x1-x0)^2 + (y1-y0)^2)
}

function float(x) { return x+1e-10 }

function go(x,y,z,ch,cw) {
  if(cx!="") {
    cd=dist(cx,cy, x,y)
    ce += cd*(ccw*cch + 4*(ccw+cw)*(cch+ch)/4 + cw*ch)/6 / in_area / kpd  # Simpson integration step, exact for linear w(d), h(d)
  }

  print "G1", "X"float(x), "Y"float(y), "Z"float(z), "E"float(ce)
  #v = ch/h/w*in_area

  cx=x; cy=y; cch=ch; ccw=cw
}

BEGIN {
  pi=3.14159265359

  w=0.75; h=0.2; h0=0.45; w0=0.75
#  kpd=0.77*0.86; in_diam=2.9; ce=0  # ABS
#  kpd=0.965; in_diam=2.95; ce=0  # PLA
  kpd=1.06; in_diam=2.95; ce=0  # PLA
  in_area=in_diam^2 * pi/4

  CONVFMT="%.6f"

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
