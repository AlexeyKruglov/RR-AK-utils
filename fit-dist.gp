load "coord.gpinc"

set grid

dist(x0,y0,x1,y1)=sqrt((x1-x0)**2 + (y1-y0)**2)

load "geom-cal.dat.gpinc"
fit dist(x(col1(x),col2(x)),y(col1(x),col2(x)), x(col3(x),col4(x)),y(col3(x),col4(x))) "geom-cal.dat" u 0:5 via Xperp,R1,R2
plot "geom-cal.dat"  u 5:(dist(x(col1($0),col2($0)),y(col1($0),col2($0)), x(col3($0),col4($0)),y(col3($0),col4($0))))
#plot "geom-cal.dat"  u (col3($0)):(col4($0))
replot x

#f(n)=dist(x(col1(n),col2(n)),y(col1(n),col2(n)), x(col3(n),col4(n)),y(col3(n),col4(n)))
#print f(0), f(1), f(2), f(3), f(4)
#n=0
#print x(col1(n),col2(n)),y(col1(n),col2(n)), x(col3(n),col4(n)),y(col3(n),col4(n))
#print col1(n),col2(n), col3(n),col4(n)
#n=2
#print x(col1(n),col2(n)),y(col1(n),col2(n)), x(col3(n),col4(n)),y(col3(n),col4(n))
#print col1(n),col2(n), col3(n),col4(n)
