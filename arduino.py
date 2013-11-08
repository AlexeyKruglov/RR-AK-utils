#! /usr/bin/python
# arduinoproxy stdin/stdout <-> socket adapter

import os,sys,socket,time
import threading

socket_name="/tmp/arduinoproxy"
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(socket_name)
#s.setblocking(0)

terminate=threading.Event()  # set to terminate

def recv_data(s):
  while True:
    try:
      data_in=s.recv(4096)
      if not data_in: raise socket.error
    except socket.error:
      terminate.set()
      break
    sys.stdout.write(data_in)
    sys.stdout.flush()

def send_data(s):
  while True:
    data_out=sys.stdin.readline()
    if not data_out: break
    sys.stderr.write("> " + data_out)
    try:
      s.sendall(data_out)
    except socket.error:
      terminate.set()
      break

def start_thread(target,args,name,daemon=False):
  global thread_list
  th=threading.Thread(target=target,args=args,name=name)
  #if daemon: 
  #  th.setDaemon()
  th.daemon=daemon
  th.start()


start_thread(target=recv_data,args=(s,),name="recv_data",daemon=True)
time.sleep(0.1)
start_thread(target=send_data,args=(s,),name="send_data",daemon=True)

terminate.wait(0.5)  # no more than 0.5 sec

try: s.close()
except socket.error: pass
