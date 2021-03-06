#! /usr/bin/gawk -f

@include "GC-parser.awkinc"

BEGIN {
  sx=sy=sphi=0
  file_coords = 1
  xn=0  # coord #

  cn=0  # constraint #
  inf_r = 1000e3  # = 1 km
  tail_len=10
  x_abort_safety=5

  maxs=1

  pi=atan2(1,1)*4
  xi=-65+20 - xc; yi=113.5-yc
}

function add_circle(x,y,r,s) {  # s=1 -- circle inside; s=-1 -- circle outside
  cs[cn,0]=x
  cs[cn,1]=y
  cs[cn,2]=r
  cs[cn,3]=s
  cn++
}

function add_line(x0,y0, nx,ny) {
  add_line_n = sqrt(nx^2 + ny^2)
  nx /= add_line_n
  ny /= add_line_n
  cs[cn,0]=x0 + inf_r * nx
  cs[cn,1]=y0 + inf_r * ny
  cs[cn,2]=inf_r
  cs[cn,3]=1
  cn++
}

/^#/ && $2 == "line" {
  add_line($3,$4, $5,$6)
  add_line($3 - x_abort_safety,$4, $5,$6)
}

/^#/ && $2 == "circle" {
  add_circle($3,$4, $5, $6)
  add_circle($3 - x_abort_safety,$4, $5, $6)
}

function add_point(x,y) {
  xs[xn,0]=x
  xs[xn,1]=y
  sumx += xs[xn,0]
  sumy += xs[xn,1]
  xn++
}

/^[GM]/ {
  parse_GC()
  if("X" in f || "Y" in f) {
    add_point(f["X"]+0, f["Y"]+0)
    if(tail_len!=0 && xn==0) add_point(f["X"]+0, f["Y"]+0)
  }
}

function pos(x) { return (x>0)?x:0 }
function min(a,b) { return (a<b)?a:b }

function get_rc() {  # get max distance (=radius) from (xc,yc)
  get_rc_res=0
  for(get_rc_i=0; get_rc_i<xn; get_rc_i++) {
    get_rc_d = sqrt((xs[get_rc_i,0]-xc)^2 + (xs[get_rc_i,1]-yc)^2)
    if(get_rc_res < get_rc_d) get_rc_res = get_rc_d
  }
  return get_rc_res
}

function cost_points(x,y) {
  costp_r=0
  costp_drx=costp_dry=0
  for(costp_i=0; costp_i<cn; costp_i++) {
    costp_dx = x-cs[costp_i,0]
    costp_dy = y-cs[costp_i,1]
    costp_d = sqrt(costp_dx^2 + costp_dy^2)
    costp_v = cs[costp_i,3] * (costp_d - cs[costp_i,2])
    # print "#",x,y,costp_i, costp_v
    if(costp_v > 0) {
      costp_r += costp_v^2/2
      costp_drx += costp_dx/costp_d * costp_v
      costp_dry += costp_dy/costp_d * costp_v
      if(costp_maxr < costp_d) costp_maxr = costp_d
    }
  }
  return costp_r
}

function cost() {
  cost_v=0
  cost_dcx=cost_dcy=cost_dca=0
  costp_maxr=0
  for(cost_i=0; cost_i<xn; cost_i++) {
    cost_cosa0 = cos(a0)
    cost_sina0 = sin(a0)
    cost_x = (xs[cost_i,0] - xc) * cost_cosa0 - (xs[cost_i,1] - yc) * cost_sina0 + x0
    cost_y = (xs[cost_i,0] - xc) * cost_sina0 + (xs[cost_i,1] - yc) * cost_cosa0 + y0
    if(tail_len != 0 && cost_i==1) cost_x += tail_len
    cost_cv = cost_points(cost_x, cost_y)
    if(cost_v < cost_cv) {
      cost_v = cost_cv
      cost_dcx = costp_drx
      cost_dcy = costp_dry
      cost_dca = \
        costp_drx * (-(xs[cost_i,0] - xc) * cost_sina0 - (xs[cost_i,1] - yc) * cost_cosa0) + \
        costp_dry * ( (xs[cost_i,0] - xc) * cost_cosa0 - (xs[cost_i,1] - yc) * cost_sina0)
    }
  }
  cost_maxr = costp_maxr
  return cost_v
}

function add_cost_prior() {
  cost_dcx += (x0-xi)*k
  cost_dcy += (y0-yi)*k
}

END {
  xc = sumx/xn; yc = sumy/xn
  rc=get_rc()
  print "#center", xc, yc
  print "#xn",xn
  print "#cn",cn
  x0=y0=a0=0
  x0=xi; y0=yi
  OFS="\t"
  cc=1

  iter=0; maxiter=-1
  k=1
  while(1) {
    cc=cost()
    add_cost_prior()
    print "#optrot",iter, maxiter, cc,x0,y0,a0,xc,yc,a0/pi*180,k
    if(cc<=0 && maxiter>=0 && iter>=maxiter) break
    if(cc<=0 && maxiter<0)
      maxiter=(iter+1)*3
    dcx = cost_dcx #+ pdcx
    dcy = cost_dcy #+ pdcy
    dca = cost_dca #* (iter%2 == 0) #+ pdca
    if(iter % 2 == 0) {
      dca=0
      if(cc>0) k/=1.25; else k*=1.25
    } else dcx=dcy=0
    s = -maxs / (sqrt(dcx^2 + dcy^2 + (rc*dca)^2) + 1e-20)
    x0 += s * dcx
    y0 += s * dcy
    a0 += s * dca
    pdcx = cost_dcx
    pdcy = cost_dcy
    pdca = cost_dca
    iter++
  }
}
