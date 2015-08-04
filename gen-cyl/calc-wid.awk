#! /usr/bin/awk -f

@include "GC-parser.awkinc"

BEGIN {
  hlayer = 0.2  # mm, nominal layer height -- used in track width calculation
  R0 = 2.875
  pi = atan2(1,1)*4
  S0 = pi/4 * R0^2
  maxc = 150  # mm/sec -- xy speed without extrusion (or max xy speed for backward e motion)

  pe=0
  CONVFMT = "%.6f"
}

function abs(x) { return x>0?x:-x }

{
  processed = 0
  parse_GC()
}

/^G[01] / {
  cdist = sqrt((cx-px)^2 + (cy-py)^2)
  edist = ce-pe
}

/^G[01] / {
  processed = 1
  cw = S0 * edist / hlayer / (cdist + 1e-10)

  f["W"] = cw  # mm

  print format_GC()
}

!processed { print }

{ update_p() }
