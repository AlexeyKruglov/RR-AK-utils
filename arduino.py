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
    if not data_in: break
    sys.stdout.write(data_in)

time.sleep(0.1)
recv_data(s)
while True:
  data_out=sys.stdin.readline()
  if not data_out: break
  sys.stderr.write("> " + data_out)
  s.sendall(data_out)
  recv_data(s)

recv_data(s)
time.sleep(0.5)
recv_data(s)
