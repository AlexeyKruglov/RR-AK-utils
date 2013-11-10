#! /usr/bin/awk -f

!/^$/ {
  x=$1
  y=$2
  z=$3
  if(cx!=x) {
    z0=z
    cx=x
  }
  
  print x,y,z-z0
}

/^$/ {print}
