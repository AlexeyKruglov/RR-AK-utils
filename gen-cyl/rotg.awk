#! /usr/bin/gawk -f

@include "GC-parser.awkinc"

BEGIN {
  pi=atan2(1,1)*4
  OFMT=CONVFMT="%.8f"
}

/^#optrot/ {
  x0=$5
  y0=$6
  a0=$7
  xc=$8
  yc=$9
}

/^[GM]/ {
  parse_GC()
  if(("X" in f || "Y" in f) && cG !~ /^G(92|28)$/) {
    X1 = (cx - xc) * cos(a0) - (cy - yc) * sin(a0) + x0
    Y1 = (cx - xc) * sin(a0) + (cy - yc) * cos(a0) + y0
    f["X"]=X1
    f["Y"]=Y1
  }
  print format_GC()
}

!/^[GM]/ { print }
