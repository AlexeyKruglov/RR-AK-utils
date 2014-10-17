#! /usr/bin/gawk -f

# Usage:
# ./skip-bad-angles.awk -v alpha0=<start_angle_in_degrees> input.g >output.g

@include "GC-parser.awkinc"

BEGIN {
  OFS="\t"
}

/^G1 / {
  parse_GC()
  print cx,cy,cz
}

# /^G1 / { update_p() }
