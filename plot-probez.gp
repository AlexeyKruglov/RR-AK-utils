set pm3d
set palette

set xrange [50:350]
set yrange [-100:200]
set size 0.5,1

load "./coord.gpinc"

splot "log_pr" u (x($1,$2)):(y($1,$2)):3

fit [-1e3:1e3] [-1e3:1e3] p2skew(x)+z0 "log_pr" u 1:2:3:(1) via sx,sy,z0
splot "log_pr" u (x($1,$2)):(y($1,$2)):($3-p2skew($1)-z0)

fit [-1e3:1e3] [-1e3:1e3] p2skew(x)+plane(x,y)+z0 "log_pr" u 1:2:3:(1) via sx,sy,px,py,z0
splot "log_pr" u (x($1,$2)):(y($1,$2)):($3-(p2skew($1)+plane($1,$2)+z0))

fit [-1e3:1e3] [-1e3:1e3] p2skew(x)+plane(x,y)+warp(x,y)+z0 "log_pr" u 1:2:3:(1) via sx,sy,px,py,pxx,pxy,pyy,z0
splot "log_pr" u (x($1,$2)):(y($1,$2)):($3-(p2skew($1)+plane($1,$2)+warp($1,$2)+z0))
