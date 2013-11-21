set pm3d
set palette
unset surface
set macros

set xrange [0:250]
set yrange [-100:150]
set size 0.455,1

load "./coord.gpinc"

if(!exists("file")) file="probe3.dat"

#splot file u (x($1,$2)):(y($1,$2)):3

#fit [-1e3:1e3] [-1e3:1e3] p2skew(x)+z0 file u 1:2:3:(1) via sx,sy,z0
#splot file u (x($1,$2)):(y($1,$2)):($3-p2skew($1)-z0)

#fit [-1e3:1e3] [-1e3:1e3] p2skew(x)+plane(x,y)+z0 file u 1:2:3:(1) via sx,sy,px,py,z0
#splot file u (x($1,$2)):(y($1,$2)):($3-(p2skew($1)+plane($1,$2)+z0))

f(x,y)=p2skew(x)+plane(x,y)+warp(x,y)+z0 + wm*(ws*sin(2*pi*y/wp)+wc*cos(2*pi*y/wp))*plane2(x,y)
if(!exists("wm")) wm=1

if(!exists("initw") || initw) wp=86; ws=0.00001; wc=0.00001; p2a=1; initw=0

#var1="sx,sy,px,py,pxx,pxy"
var1="px,py,pxx,pxy"
#var2="ws,wc,p2a,wp"
var2="ws,wc,wp"

##fit [-1e3:1e3] [-1e3:1e3] f(x,y) file u 1:2:3:(1) via @var1,z0
fit [-1e3:1e3] [-1e3:1e3] f(x,y) file u 1:2:3:(1) via @var1,z0
splot file u (x($1,$2)):(y($1,$2)):($3-f($1,$2))
fit [-1e3:1e3] [-1e3:1e3] f(x,y) file u 1:2:3:(1) via @var2
splot file u (x($1,$2)):(y($1,$2)):($3-f($1,$2))
#splot [-40:140] [-20:320] file u ($1):($2):($3-f($1,$2))

fit [-1e3:1e3] [-1e3:1e3] f(x,y) file u 1:2:3:(1) via @var1,z0
splot file u (x($1,$2)):(y($1,$2)):($3-f($1,$2))
fit [-1e3:1e3] [-1e3:1e3] f(x,y) file u 1:2:3:(1) via @var2,z0
splot file u (x($1,$2)):(y($1,$2)):($3-f($1,$2))
fit [-1e3:1e3] [-1e3:1e3] f(x,y) file u 1:2:3:(1) via @var1,z0
splot file u (x($1,$2)):(y($1,$2)):($3-f($1,$2))
fit [-1e3:1e3] [-1e3:1e3] f(x,y) file u 1:2:3:(1) via @var2,z0
splot file u (x($1,$2)):(y($1,$2)):($3-f($1,$2))
fit [-1e3:1e3] [-1e3:1e3] f(x,y) file u 1:2:3:(1) via @var1,z0,@var2
splot file u (x($1,$2)):(y($1,$2)):($3-f($1,$2))
