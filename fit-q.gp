s1(thx, thy) = 1./(1+thx**2)+1./(1+thy**2)
s2(thx, thy) = ( (1+thx*thy)/(1+thx**2)/(1+thy**2) )**2
l1(thx, thy) = sqrt( s1(thx, thy)/2. + sqrt(s1(thx, thy)**2/4. - s2(thx, thy)) )
l2(thx, thy) = sqrt( s1(thx, thy)/2. - sqrt(s1(thx, thy)**2/4. - s2(thx, thy)) )

thx=0.63
thy=0.53
fit x*l1(thx,thy)+y*l2(thx,thy) "radii.dat" u 1:2:($3/$4):(0.1/$4) via thx,thy
