#! /usr/bin/awk -f

@include "GC-parser.awkinc"

BEGIN {
  erate = 1.0 * 1.  # mm/sec
  maxc = 150  # mm/sec -- xy speed without extrusion (or max xy speed for backward e motion)

  pe=0
  CONVFMT = "%.6f"
}

function abs(x) { return x>0?x:-x }

{
  processed = 0
  parse_GC()
}

/^G1 / {
  cdist = sqrt((cx-px)^2 + (cy-py)^2)
  edist = ce-pe
}

/^G1 / && ce>pe {
  processed = 1
  f["F"] = erate / edist * cdist
  f["F"] *= 60  # convert to mm/min

  print format_GC()
}

/^G1 / && ce<=pe {
  processed = 1
  cf = erate / (abs(edist) + 1e-10) * cdist
  if(cf > maxc) cf = maxc

  f["F"] = cf * 60  # convert to mm/min

  print format_GC()
}

!processed { print }

{ update_p() }
