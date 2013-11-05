#! /usr/bin/python
# arduinoproxy stdin/stdout <-> socket adapter

import os,sys,socket,time
import threading

socket_name="/tmp/arduinoproxy"
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(socket_name)
#s.setblocking(0)

def recv_data(s):
  while True:
    data_in=s.recv(4096)
    sys.stdout.write(data_in)

recv_data(s)
while True:
  data_out=sys.stdin.readline()
  if not data_out: break
  s.sendall(data_out)
  recv_data(s)

recv_data(s)
time.sleep(0.5)
recv_data(s)
