#! /usr/bin/python
# Serial port proxy server

import socket,os,sys,io,serial,time
import threading,collections

socket_name="/tmp/arduinoproxy"
port_name="/dev/ttyACM0"

die=threading.Event()  # set to terminate

sqc=threading.Semaphore(0)  # number of elements in sq
sq=collections.deque()  # buffer Arduino output since there's no permanent connection to the socket
#sq=Queue.Queue()  # buffer Arduino output since there's no permanent connection to the socket

#    /---->--sock_qu-<----->-\
#  port                     conn---<<---sock
#    \---<--------------<----/

def port_reader(port,sock_qu,sock_quc):
  try:
    while True:
      #line=port.readline()
      time.sleep(0.250)
      line="test. time=%f\n" % time.time()
      sys.stdout.write("< " + line)
      sock_qu.append(line)
      sock_quc.release()
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
  global die
  while True:
    conn_ok.wait()
    while True:
      data = conn.recv(4096)
      if not data: 
        conn_ok.clear()
        conn_bad.set()
        break
      sys.stdout.write("> " + data)
      if data=="disconnect\n":
        conn.close()
        port.close()
        die.set()
        exit()
      port.write(data)
    conn.close()
    conn=None

def socket_writer(sock_qu,sock_quc):
  global conn, conn_ok, conn_bad
  while True:
    conn_ok.wait()
    sock_quc.acquire()
    data=sock_qu.popleft()
    try:
      #if conn==None: raise socket.error
      conn.sendall(data)
    except (socket.error, AttributeError):
      conn_ok.clear()
      conn_bad.set()
      sock_qu.appendleft(data)
      sock_quc.release()


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

def start_thread(target,args,name,daemon=False):
  global thread_list
  th=threading.Thread(target=target,args=args,name=name)
  #if daemon: 
  #  th.setDaemon()
  th.daemon=daemon
  th.start()


# Start worker processes
# threading.Thread(target=port_reader,args=(p,sq,sqc),name="port_reader").start()
start_thread(target=port_reader,args=(None,sq,sqc),name="port_reader",daemon=True)
start_thread(target=socket_writer,args=(sq,sqc),name="socket_writer",daemon=True)
start_thread(target=socket_reader,args=(p,),name="socket_reader")
start_thread(target=socket_connector,args=(s,),name="socket_connector",daemon=True)

die.wait()

print "[stopping threads]"
#for th in threading.enumerate():
#  th.join(0)
