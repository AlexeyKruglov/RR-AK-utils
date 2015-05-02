all: cyl.g1 cyl.g cyl.g.dat

.PHONY: all

cyl.g1: cyl.g0 const-flow.awk
	./const-flow.awk cyl.g0 >cyl.g1

cyl.g: cyl.g1 skip-bad-angles.awk alpha0.dat
	#./skip-bad-angles.awk -v `cat alpha0.dat` cyl.g1 >cyl.g
	cp cyl.g1 cyl.g

cyl.g.dat: cyl.g
	./g2dat.awk cyl.g >cyl.g.dat
