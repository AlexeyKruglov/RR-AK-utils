#! /usr/bin/python
# Echo server program
import os

out_queue=[]  # list of strings pending output

def openfifo(name):
  try:
    os.remove(name)
  except OSError:
    pass
  os.mkfifo(name)
#  return os.open(name, mode)

pipe_name="/tmp/arduinoproxy"
pipe_in=pipe_name + "in"
pipe_out=pipe_name + "out"

createfifo(pipe_out)
createfifo(pipe_in)

def dump_out():
  if(!outp):
    try
      outp=os.open(pipe_out, os.O_RWONLY || os.O_NONBLOCK)
    except OSError:
      outp=None
  if outp:
    while out_queue:
      outp.write(out_queue.pop(0))

while 1:
  inp=os.open(pipe_in, O_RDONLY)
  data = inp.readline()
  if not data: break
  print data
  out_queue.append(data)
  dump_out()

if outp: outp.close()
inp.close()
