#! /usr/bin/python
# Serial port proxy server

import socket,os,io,serial,time
import threading,collections,Queue

socket_name="/tmp/arduinoproxy"
port_name="/dev/ttyACM0"


#sq=collections.deque()  # buffer Arduino output since there's no permanent connection to the socket
sq=Queue.Queue()  # buffer Arduino output since there's no permanent connection to the socket

def port_reader(port,sock_qu):
  try:
    while True:
      #line=port.readline()
      time.sleep(0.250)
      line="test. time=%f\n" % time.time()
      print "> %s" % line
      if conn:
        try:
          conn.send(line)
        except socket.error:
          sock_qu.
          print "error!!!"
          exit()
      else: sock_qu.put(line)
  finally:
    #port.close()
    pass

conn=None
def socket_listener(sock,qu,port):
  global conn
  try:
    while True:
      conn, addr = sock.accept()
      print "[connected]"
      while True:
        try:
          conn.sendall(qu.get_nowait())
        except Queue.Empty:
          break
      while True:
        data = conn.recv(4096)
        if not data: break
        print "> \"%s\"" % data
        if data=="disconnect\n":
          exit()
        port.write(data)
      print "[disconnected]"
      conn.close()
      conn=None
  finally:
    sock.close()



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

# Start worker processed
# threading.Thread(target=port_reader,args=(p,sq)).start()
threading.Thread(target=port_reader,args=(None,sq)).start()
threading.Thread(target=socket_listener,args=(s,sq,p)).start()
