#! /usr/bin/awk -f

BEGIN {
  rown=0
  coln=0
  eol=ORS
}

!/^#/ {
  if(coln<NF) coln=NF
  for(i=1; i<=NF; i++)
    data[rown,i]=$i
  rown++
}

function out_range(l,r) {
  if(r<=l) {
    v=data[l,c]
    if(v=="" || v=="-") v="1/0"
    print v
    return
  }
  m=int((l+r+1.5)/2)
  print "n<"m"?"
  out_range(l,m-1)
  print ":"
  m=int((l+r+1.5)/2)
  out_range(m,r)
}

END {
  OFS=""
  ORS=""
  for(c=1; c<=coln; c++) {
    print "col"c"(n)="
    out_range(0,rown-1)
    print eol
  }
}
