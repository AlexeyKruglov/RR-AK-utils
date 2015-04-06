#! /usr/bin/gawk -f

# Usage:
# ./skip-bad-angles.awk -v alpha0=<start_angle_in_degrees> input.g >output.g

@include "GC-parser.awkinc"

BEGIN {
  if(alpha0 == "") alpha0 = 90/360.

  pi = 3.14159265359
#  alpha0 /= 360.
  e_steps_per_mm = 203.72*1.02
  period = 3200 / e_steps_per_mm
  e_move_end = 15.0    # mm, the amount of retraction to the parking positions at the end
  e_move_start = e_move_end+1.+0.0  # mm, protraction at the beginning

  alpha0 += e_move_start/period
  calpha = alpha0%1

  intn = 0
  # intervals must not intersect nor touch
  ## v0
  # bad_interval(0, 90)
  # bad_interval(300, 330)
  ## v1
  # bad_interval(293.3, 13.4)
  ## v2
  bad_interval(90*2.4, 90*3.2)
  leave_angle = (2.0+2.0)/period   # revolutions
  dump_align_angle = 90*3.3/360.  # dumped extrusion will be right aligned on this angle position
  dump_w = 1.0                 # mm, dump tracks step
  dump_reg_rot = 90 /180*pi    # radians, CCW, x axis -> direction across dump tracks rotation angle
  dump_reg_x0 = 15   # mm
  dump_reg_y0 = -16   # mm

  max_xy_rate = 150       # mm/sec
  dump_z = 0
  dump_move_z = 2.0
  e_retract = 0.5
  retract_e_rate = 10.0
  dump_k = 100            # mm/revolution = mm/period(e)
  dump_e_rate = 0.4       # mm/sec
  dump_f_rate = dump_e_rate / period * dump_k
  dump_x_reflect = -1

  # min_xy_dist = 2.5  # mm, not implemented
  meta_out=0

  e0=0
  state=0
  # state=0  not retracted
  # state=1  retracted, need to unretract
  cf = dump_f_rate*60

  eps = 1e-6
  CONVFMT=OFMT="%.6f"
}

function bad_interval(l, r) {
  ints[intn, "l"] = l/360.
  ints[intn, "r"] = r/360.
  intn++
}

function frac(x) { return (x%1+1)%1 }
function floor(x) { return x - frac(x) }
function ceil(x) { return -floor(-x) }

# Return angular distance (in # of revolutions, >= 0)
#   find="l": to the next bad interval start
#   find="r": to the next bad interval end
# Infinity -> 10
function angle_left(calpha, find) {
  if(find == "l")
    angle_left_r = angle_left(calpha, "r")
  calpha = frac(calpha)
  angle_left_minleft = 10
  for(i=0; i<intn; i++) {
    angle_left_cleft = ints[i,find] - calpha
    if(angle_left_cleft < 0) angle_left_cleft += 1
    if(angle_left_minleft > angle_left_cleft) angle_left_minleft = angle_left_cleft
  }
  if(find=="l") meta("info", "find="find" calpha="calpha" left_angle="angle_left_minleft)
  if(find == "l" && angle_left_r > 1e-4 && angle_left_minleft >= angle_left_r)
    return 0
  return angle_left_minleft
}

/^[A-Z]/ {
  parse_GC()
  processed=0
}

/^G1 / {
  cdist = sqrt((cx-px)^2 + (cy-py)^2)
  edist = ce-pe
}

function meta(t,s) {
  if(meta_out) print "(<"t"> "s" )"
}

# nstate=1 -> retract
# nstate=0 -> unretract
function retract(nstate, cf) {  # cf in mm/min
  if(state==nstate) return
  meta("retract", "new_state="nstate)
  print "G1 F"retract_e_rate*60
  print "G1 E"pe+e0-nstate*e_retract" F"retract_e_rate*60
  if(nstate==0) {
    print "G1 F"cf
    print "G4 P500"
  } else {
    print "G4 P300"
  }
  state = nstate
}

function move_noextr(ox,oy, nx,ny,nz) {  # always move at pz+dump_move_z
  meta("move_noextr", "from="ox","oy" to="nx","ny","nz)
  retract(1)
  print "G1 F"max_xy_rate*60
  # print "G1 X"ox" Y"oy" Z"pz+dump_move_z" F"max_xy_rate*60
  print "G1 Z"pz+dump_move_z" F"max_xy_rate*60
  print "G1 X"nx" Y"ny" Z"pz+dump_move_z" F"max_xy_rate*60
  print "G1 X"nx" Y"ny" Z"nz" F"max_xy_rate*60
}

function conv_dump_coord(x, y) {
  # print "!!!", x,y
  x *= dump_x_reflect
  #x -= dump_reg_x0
  #y -= dump_reg_y0
  ret_x = x*cos(dump_reg_rot) - y*sin(dump_reg_rot) + dump_reg_x0
  ret_y = y*cos(dump_reg_rot) + x*sin(dump_reg_rot) + dump_reg_y0
  # print "!!!", ret_x,ret_y, x,y
}

function dump_angle(dangle) {  # skip dangle revolutions
  meta("dump_angle","dangle="dangle)
  xpos = ceil(calpha+dangle - dump_align_angle - eps) * dump_w
  ypos0 = -(calpha        - dump_align_angle - xpos) * dump_k
  ypos1 = -(calpha+dangle - dump_align_angle - xpos) * dump_k
  conv_dump_coord(xpos,ypos0); xpos0=ret_x; ypos0=ret_y
  conv_dump_coord(xpos,ypos1); xpos1=ret_x; ypos1=ret_y

  move_noextr(px,py, xpos0,ypos0,dump_z)

  retract(0, dump_f_rate*60)
  calpha += dangle
  e0 += dangle*period
  # extrude (dump)
  print "G1 X"xpos1" Y"ypos1" Z"dump_z" E"pe+e0" F"dump_f_rate*60

  # move back
  move_noextr(xpos1,ypos1, px,py,pz)
}

function extr_portion(nde) {
  meta("extr_portion","cdist="nde" totdist="edist)
  r = nde/edist
  npx = px + r*(cx-px)
  npy = py + r*(cy-py)
  npz = pz + r*(cz-pz)
  npe = pe + nde

  retract(0, cf)
  f["F"]=cf  # ??? interpolate feedrate?
  # print "G1 F"f["F"]
  f["G"]="1"
  f["X"]=npx
  f["Y"]=npy
  f["Z"]=npz
  f["E"]=npe+e0
  print format_GC()
  calpha += nde/period

  px=npx; py=npy; pz=npz; pe=npe
  edist-=nde
  left-=nde  # note: we do not update left_angle
}

/^G1 / {
  if("E" in f) f["E"] += e0
  if("F" in f) cf = f["F"]
  if(edist<=0) {  # no extr, just move
    print format_GC()
    calpha += edist / period
  } while(edist+0>0) {  # extr
    left_angle = angle_left(calpha, "l")
    left = period * left_angle
    # print "# left_l="left
    cedist = edist
    if(cedist > left) cedist=left
    extr_portion(cedist)
    if(left <= 0) {
      # print "# left_l2="left
      left_angle = angle_left(calpha, "r")
      left = period * left_angle
      # print "# left_r="left
      dump_angle(left_angle)
    }
  }
  processed=1
}

!processed { print }

/^G1 / { update_p() }

END {
  left_angle = angle_left(calpha, "l")
  while(left_angle < leave_angle) {
    r_left_angle = angle_left(calpha, "r")
    dump_angle(r_left_angle)
    left_angle = angle_left(calpha, "l")
  }
  # vvv !!! int part may diverge across runs if int(e_move_end/period)!=int(e_move_start/period)
  print "alpha0="calpha-(e_move_end/period)%1 >"alpha1.dat"
}
