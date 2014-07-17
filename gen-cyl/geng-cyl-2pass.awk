#! /usr/bin/awk -f

# Generage G-code(iter0) of a 1 layer helix cylinder

function dist(x0,y0, x1,y1) {
  return sqrt((x1-x0)^2 + (y1-y0)^2)
}

function abs(x) { return x>0?x:-x }
function bound(x,a,b) { return x<a?a:x>b?b:x }  # assume a<=b

function interp(x, x0,x1, y0,y1) {
}

function float(x) { return x+1e-10 }

function go(x,y,z,ch,cw) {
  if(cx!="") {
    cd=dist(cx,cy, x,y)
    ce += cd*cw*ch / in_area / kpd
  }

  x+=1e-10; y+=1e-10; z+=1e-10  # convert int -> float

  print "G1", "X"float(x), "Y"float(y), "Z"float(z), "E"float(ce)
  #v = ch/h/w*in_area

  cx=x; cy=y
}

function p2sincos(phi,r1,r2) {
  dphi=abs(r1-r2)/(r1+r2)
  p2_k = bound(sin(phi)/dphi,-1,1)
  p2_r = (p2_k*(r2-r1) + (r1+r2) )/2  # k=-1 -> r1; k=+1 -> r2
  p2sin = p2_r * sin(2*phi)
  p2cos = p2_r * cos(2*phi)
  cw = (p2_k*(w2-w1) + (w1+w2) )/2
}

{
  tab_z[tabn]=$1
  tab_r1[tabn]=$2
  tab_r2[tabn]=$3
  tabn++
}

function getr1r2(z) {
  if(z<tab_z[0]) z=tab_z[0]
  for(i=1; i<tabn-1; i++)
    if(z<tab_z[i]) break
  r1 = interp(z, tab_z[i-1], tab_z[i], tab_r1[i-1], tab_r1[i])
  r2 = interp(z, tab_z[i-1], tab_z[i], tab_r2[i-1], tab_r2[i])
}

BEGIN {
  pi=3.14159265359

  w=0.75; h=0.2; h0=0.45; w0=0.75
  kpd=0.77*0.86; in_diam=2.9; ce=0
  in_area=in_diam^2  # times pi/4

  CONVFMT="%.4f"

  Di=5.0; Do=8.0
  step=0.25
  Z=1.0

  r1 = (Di+w)/2; w1 = w
  r2 = (Do/2 + r1 + w/2)/2; w2 = Do/2 - r1 - w1/2
  n=int(pi*4*r2/step+1)

  for(i=0; i<n; i++) pz[i]=-h0

  zn=int(Z/h-0.25+1); h=Z/(zn+0.25)
  for(i=-n; i<=n*(zn+1); i++) {
    phi=-i/n*2*pi
    cz=(i/n+0.25)*h
    if(cz<0) cz=0; #else if(cz>Z) cz=Z

    #cr = (ra + (rd+add_r)*cos(phiw)
    p2sincos(phi, r1,r2)
    cw = i<=0 ? w0 : cw

    ipn = (i+n)%n; go(p2cos, p2sin, cz, cz-pz[ipn], cw); if (i>-n) pz[ipn]=cz
  }
}
