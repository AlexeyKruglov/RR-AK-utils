#! /usr/bin/awk -f

{ # $1=D (b/w endpoints), $2=H (midpoint to the line b/w endpoints), $4-$3=logical distance b/w the endpoints
  h=$1/2  # g=D/2
  H=$2
  a=sqrt(h**2 + H**2)
  K=a/2/H
  R=a*K
  phi=4*atan2(H,h)
  print R, ($4-$3)/phi, phi/3.1415927*180.
}
