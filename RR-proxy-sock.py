#! /usr/bin/python
# Serial port proxy server

import socket,os,io,serial,time
import threading,collections

socket_name="/tmp/arduinoproxy"
port_name="/dev/ttyACM0"


sq=collections.deque()  # buffer Arduino output since there's no permanent connection to the socket
#sq=Queue.Queue()  # buffer Arduino output since there's no permanent connection to the socket

#    /---->--sock_qu-<----->-\
#  port                     conn---<<---sock
#    \---<--------------<----/

def port_reader(port,sock_qu):
  try:
    while True:
      #line=port.readline()
      time.sleep(0.250)
      line="test. time=%f\n" % time.time()
      print "> %s" % line
      sock_qu.append(line)
  finally:
    #port.close()
    pass

conn=None
conn_ok=threading.Event()  # set when the connection is supposeedly ok
conn_bad=threading.Event() # not conn_ok -- to be able to wait for bad connention
conn_ok.clear()
conn_bad.set()

def socket_connector(sock):
  global conn, conn_ok, conn_bad
  try:
    while True:
      conn, addr = sock.accept()
      print "[connected]"
      conn_bad.clear()
      conn_ok.set()
      conn_bad.wait()
      print "[disconnected]"
  finally:
    sock.close()

def socket_reader(port):
  global conn, conn_ok, conn_bad
  while True:
    conn_ok.wait()
    while True:
      data = conn.recv(4096)
      if not data: 
        conn_ok.clear()
        conn_bad.set()
        break
      print "> %s" % data
      if data=="disconnect\n":
        exit()
      port.write(data)
    conn.close()
    conn=None

def socket_writer(sock_qu):
  global conn, conn_ok, conn_bad
  while True:
    conn_ok.wait()
    data=sock_qu.popleft()
    try:
      conn.sendall(data)
    except socket.error:
      conn_ok.clear()
      conn_bad.set()
      sock_qu.appendleft(data)


# Open port
#p=serial.Serial(port_name,115200)
#p=os.open("testfile",os.O_WRONLY | os.O_CREAT)
p=open("testfile","w")
time.sleep(0.51)

# Create listening socket
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
  os.remove(socket_name)
except OSError:
  pass
s.bind(socket_name)
s.listen(0)

# Start worker processes
# threading.Thread(target=port_reader,args=(p,sq),name="port_reader").start()
threading.Thread(target=port_reader,args=(None,sq),name="port_reader").start()
threading.Thread(target=socket_writer,args=(sq,),name="socket_writer").start()
threading.Thread(target=socket_reader,args=(p,),name="socket_reader").start()
threading.Thread(target=socket_connector,args=(s,),name="socket_connector").start()
