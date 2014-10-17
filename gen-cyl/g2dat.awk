#! /usr/bin/gawk -f

@include "GC-parser.awkinc"

BEGIN {
  OFS="\t"
}

/^G1 / {
  parse_GC()
  print cx,cy,cz
}

# /^G1 / { update_p() }
