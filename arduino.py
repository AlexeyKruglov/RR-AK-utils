#! /usr/bin/python
# arduinoproxy stdin/stdout <-> socket adapter

import os,sys,socket,time

socket_name="/tmp/arduinoproxy"
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(socket_name)
s.setblocking(0)

def recv_data(s):
  while True:
    try: data_in=s.recv(4096)
    except socket.error: break
    sys.stdout.write(data_in)

recv_data(s)
while True:
  data_out=sys.stdin.readline()
  if not data_out: break
  print "> %s" % data_out
  s.sendall(data_out)
  recv_data(s)

recv_data(s)
time.sleep(0.5)
recv_data(s)
