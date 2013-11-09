# Arduino proxy socket IO class

import threading,socket,sys,io,errno

class ArduinoSocketIO(io.BufferedIOBase):
  socket_name = None
  sock = None
  conn = None
  MAX_BUFFER = 65536
  blocking = True
  timeout = None
  echo_out = None
  echo_in = None

  def __init__(self,socket_name="/tmp/arduinoproxy", echo=False, echo_out=sys.stderr, echo_in=sys.stderr, blocking=True, timeout=None):
    self.socket_name = socket_name
    if echo:
      self.echo_in = echo_in
      self.echo_out = echo_out
    if timeout != None: self.timeout = timeout
    elif not blocking: self.timeout = 0.0

    self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    self.sock.connect(socket_name)
    # if blocking: self.sock.setblocking(1)
    # else:        self.sock.setblocking(0)
    self.sock.settimeout(self.timeout)

  def readable(self):
    return True
  def writable(self):
    return True

  def close(self):
    self.sock.close()

  def settimeout(self, timeout=None):
    self.timeout = timeout
    self.sock.settimeout(self.timeout)

  def setblocking(self, blocking=True):
    if blocking: self.settimeout(None)
    else: self.settimeout(0.0)
    self.sock.settimeout(self.timeout)

  def readall(self):
    return self.read(n = self.MAX_BUFFER)  # not correct, but will go

  def read(self, n = None):
    if n<0: n = None
    if n == None:
      raise
      return self.readall()
    try:
      data_in=self.sock.recv(n)
    except socket.error, e:
      cerrno, cerrstr = e
      if cerrno != 11: raise
      data_in = None
    #if data_in != None: print "[%i -> %i]" % (n,len(data_in))
    if self.timeout != None and not data_in:
      raise io.BlockingIOError(errno.EAGAIN,0)
    if self.echo_in != None:
      self.echo_in.write(data_in)
      #self.echo_in.write("> " + data_in)
      self.echo_in.flush()
    return bytes(data_in)

  def unblock_read(self):  # Unblock a blocking read() call
    if self.timeout>0.0:
      self.sock.settimeout(0.0)
      self.sock.settimeout(self.timeout)

  def write(self, b):
    if self.echo_out != None:
      self.echo_out.write(b)
      #self.echo_out.write("> " + b)
      self.echo_out.flush()
    self.sock.sendall(b)
    return len(b)

