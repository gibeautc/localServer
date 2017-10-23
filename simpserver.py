#!/usr/bin/env python
import socket
import sys
import time
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setblocking(0)
host=''
port=8888


def print_con(conList):
	for con in conList:
		print("PID: "+str(con.pid)+"  :"+str(con.status))
class SyncCon:
	def __init__(self,c,addr):
		self.con=c
		self.addr=addr
		self.pid=""
		self.last=time.time()
		self.status=True
try:
	s.bind((host,port))
except socket.error as msg:
	print("Bind Failed. Error Coee: "+str(msg[0])+" Message: "+msg[1])
	sys.exit()

s.listen(10)
print("Now Listening")

con=[]
while True:
	print_con(con)
	time.sleep(1)
	for x in range(len(con)):
		sc=con[x]
		if not sc.status:
			continue
		rec=sc.con.recv(1024)
		if "PID" in rec:
			print("Got a check in")
			sp=rec.split(":")
			sc.pid=sp[1]
			sc.last=time.time()
		if time.time()-sc.last>10:
			print("Connection timing out...closing")
			sc.con.close()
			sc.status=False
	try:
		c,addr=s.accept()
		con.append(SyncCon(c,addr))
		print("Got Connection from ",addr)
		c.send("Thank you for connecting")
	except:
		continue
