#! /bin/sh
./optrot.awk table.dat $1 |cat - $1 |./rotg.awk
