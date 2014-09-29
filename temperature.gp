set grid
set key left top
set y2tics
set xrange [558e3:]
t0=1.411e9

plot "./temperature.log" u ($1-t0):6 w lines ls 2
replot "./temperature.log" u ($1-t0):4 w lines ls 1
replot "./temperature.log" u ($1-t0):16 axes x1y2 w lines ls 3

print "t0 =", t0
show xrange