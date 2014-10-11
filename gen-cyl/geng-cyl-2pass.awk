#! /usr/bin/awk -f

# Generage G-code(iter0) of a 1 layer helix cylinder

@include "geng-cyl.awkinc"

function abs(x) { return x>0?x:-x }
function bound(x,a,b) { return x<a?a:x>b?b:x }  # assume a<=b

function interp(x, x0,x1, y0,y1) {
  return y0+(y1-y0)*(x-x0)/(x1-x0+1e-20)
}

function p2sincos(phi,r1,r2) {
  if(passes==1) {
    p2sin = r1 * sin(phi)
    p2cos = r1 * cos(phi)
    cw = w1
  } else {  # passes==2
    dphi=abs(r1-r2)/(r1+r2)
    p2_k = bound(-sin(phi)/dphi,-1,1)
    p2_r = (p2_k*(r2-r1) + (r1+r2) )/2  # k=-1 -> r1; k=+1 -> r2
    p2sin = p2_r * sin(2*phi)
    p2cos = p2_r * cos(2*phi)
    cw = (p2_k*(w2-w1) + (w1+w2) )/2
  }
}

BEGIN {
  from_file=0
  z0=0
  if(passes=="") passes=2
}

/^[^#]/ {
  tabn+=0
  tab_z[tabn]=$1
  tab_r1[tabn]=$2
  tab_r2[tabn]=$3
  tabn++
  from_file=1
  if(z0>tab_z[0]) z0=tab_z[0]
}

/^#/ && $2=="passes" { passes = $3 }

function correct_r(r) { return sqrt(r^2 + delta^2) }

function calc_r_w() {
  if(passes==1) {
    w1 = (Do-Di)/2
    w2 = 0
  } else {  # passes==2
    totw = (Do-Di)/2
    if(0 && totw>w+minw) w1=w
    else w1=totw/2
    w2=totw-w1
  }
  r1 = correct_r((Di+w1)/2)
  r2 = correct_r((Do-w2)/2)
}

function getr1r2(z) {
  z += z0
  if(z<tab_z[0]) z=tab_z[0]
  for(getr1r2_i=1; getr1r2_i<tabn-1; getr1r2_i++)
    if(z<tab_z[getr1r2_i]) break

  # print "#", z,getr1r2_i,tab_z[getr1r2_i-1],tab_z[getr1r2_i], tab_r1[getr1r2_i-1], tab_r1[getr1r2_i]

  Di = interp(z, tab_z[getr1r2_i-1], tab_z[getr1r2_i], tab_r1[getr1r2_i-1], tab_r1[getr1r2_i])
  Do = interp(z, tab_z[getr1r2_i-1], tab_z[getr1r2_i], tab_r2[getr1r2_i-1], tab_r2[getr1r2_i])

  calc_r_w()
  #print "#", z, Di,Do,r1,r2,w1,w2
}

END {
  w=0.75; minw=0.55; h=0.2; h0=0.55; w0=0.75
  kpd=0.77*0.86 *0.75; in_diam=2.9; ce=0
  in_area=in_diam^2 * pi/4
  delta = 0.9

  Di=5.0; Do=23.6
  step=0.25
  Z=8.0

  r1 = (Di+w)/2; w1 = w
  r2 = (Do/2 - w/2)/2; w2 = Do/2 - r1 - w1/2
  n=int(pi*r2/step+1)*2*passes

  for(i=0; i<n; i++) pz[i]=-h0

  zn=int(Z/h-0.25+1); h=Z/(zn+0.25)
  for(i=-n; i<=n*(zn+1); i++) {
    phi=-i/n*2*pi
    cz=(i/n+0.25)*h
    if(i<=0) cz = (((i*2)%n)/n+0.25)*h
    if(cz<0) cz=0; else if(cz>Z) cz=Z

    if(from_file) {
      getr1r2(cz)
      #cr = (ra + (rd+add_r)*cos(phiw)
    }
    if(i<=0 && from_file) {
      Do += w0
      passes=2
      calc_r_w()
    } else passes=1
    p2sincos(phi, r1,r2)
    cw = i<=0 ? w0 : cw

#    ipn = (i+n)%n; go(p2cos, p2sin, cz, cz-pz[ipn], cw); if (i>-n) pz[ipn]=cz
    if(i>0) ipn = (i+n)%n;
    else ipn=(i*2+n*2)%n + int(i*2/n);
    go(p2cos, p2sin, cz, cz-pz[ipn], cw); if (i>-n) pz[ipn]=cz
  }
}
