#! /usr/bin/python

import io,serial,time

TIMEOUT_G=15
TIMEOUT_M=1
timeout=0

ard=serial.Serial('/dev/ttyACM0',115200,timeout=0)
#ard=ard_ser.FileLike
time.sleep(0.52)

timeout=time.time()+TIMEOUT_M

def ardans():
  res=''
  to_wait = timeout-time.time()
  if to_wait>0: time.sleep(to_wait)
  return ard.readlines()

def ardcmd(s, block=True):
  global timeout
  ard.write(s + '\n')
  if s[0:1]=='M': cmd_timeout=TIMEOUT_M
  else: cmd_timeout=TIMEOUT_G
  timeout=max(timeout,time.time()+cmd_timeout)
  if block:
    return ardans()

print ardans()

try:
  #print ardcmd('G28')
  print ardcmd('M114')
  lines=ardans()
  print lines
finally:
  ard.close()
