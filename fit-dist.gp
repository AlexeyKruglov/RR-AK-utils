load "coord.gpinc"

set grid

dist(x0,y0,x1,y1)=sqrt((x1-x0)**2 + (y1-y0)**2)
only(x) = x!=0 ? 0 : 1/0


# dist
func1(x) = dist(xi(col1(x),col2(x),col6(x)),yi(col1(x),col2(x),col6(x)), xi(col3(x),col4(x),col6(x)),yi(col3(x),col4(x),col6(x)))
# abs x
func3(x) = xi(col1(x),col2(x),2) + only(!noabs)
# abs y
func4(x) = yi(col1(x),col2(x),2) + only(!noabs)

func(x) = (col6(x)==3)? func3(x): (col6(x)==4)? func4(x): func1(x)


load "geom-cal.dat.gpinc"
# fit dist(x(col1(x),col2(x)),y(col1(x),col2(x)), x(col3(x),col4(x)),y(col3(x),col4(x))) "geom-cal.dat" u 0:5 via Xperp,R1,R2
#fit dist(xi(col1(x),col2(x),col6(x)),yi(col1(x),col2(x),col6(x)), xi(col3(x),col4(x),col6(x)),yi(col3(x),col4(x),col6(x))) "geom-cal.dat" u 0:5 via Xperp,R1,R2, Xperp_2,R2_2

noabs=1
#fit func(x) "geom-cal.dat" u 0:5 via Xperp,R1,R2, Xperp_2,R2_2
fit [:10] func(x) "geom-cal.dat" u 0:($5) via Xperp,R1,R2, Xperp_2,R2_2, phi2k,phi1k
noabs=0
#fit [11:] func3(x) "geom-cal.dat" u 0:5 via Y0,xx0
fit [11:] func(x) "geom-cal.dat" u 0:5 via Y0,xx0,yy0

fit func(x) "geom-cal.dat" u 0:5 via Xperp,R1,R2, Xperp_2,R2_2, phi2k,phi1k, Y0,xx0,yy0

# Xperp           = 86.0537          +/- 2.751        (3.196%)
# R1              = 158.162          +/- 1.408        (0.8902%)
# R2              = 72.9029          +/- 1.995        (2.737%)
# Xperp_2         = 65.7656          +/- 1.868        (2.841%)
# R2_2            = 94.9426          +/- 3.049        (3.212%)
# phi2k           = 108.933          +/- 3.728        (3.422%)
# phi1k           = 270.429          +/- 2.051        (0.7584%)
# Y0              = -180.322         +/- 5.797        (3.215%)
# xx0             = -235.9           +/- 2.102        (0.8912%)
# yy0             = 26.8296          +/- 2.627        (9.79%)

plot "geom-cal.dat"  u 5:(func($0))
#plot "geom-cal.dat"  u 5:(dist(x(col1($0),col2($0)),y(col1($0),col2($0)), x(col3($0),col4($0)),y(col3($0),col4($0))))
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
