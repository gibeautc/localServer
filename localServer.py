#!/usr/bin/env python

from daemon import runner
import threading
import time
#import database
import datetime
import subprocess
import sys
import os
DEBUG=1
INFO=2
WARNING=3
ERROR=4
LOGLEVEL=1

class SyncCon:
	def __init__(self,c,addr):
		self.con=c
		self.addr=addr
		self.pid=""
		self.last=time.time()
		self.status=True
class App():
	def __init__(self):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/tty'
		self.stderr_path = '/dev/tty'
		self.pidfile_path =  '/tmp/localServer.pid'
		self.pidfile_timeout = 5
	def run(self):
		self.log(ERROR,"\n\n\n\n\n******************")
		self.s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.s.setblocking(0)
		host=''
		port=8888
		
		try:
			self.s.bind((host,port))
		except socket.error as msg:
			print("Bind Failed. Error Coee: "+str(msg[0])+" Message: "+msg[1])
			sys.exit()

		self.s.listen(10)
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

	def logerror(self):
		self.log(ERROR,sys.exc_info())	


	def log(self,level,message):
		level_strings=["","DEBUG- ","INFO- ","WARNING- ","ERROR- "]
		if level>=LOGLEVEL:
			msg=str(datetime.datetime.now())
			msg=msg.split(".")
			msg=msg[0]
			msg=msg+" Client_LocalCon-"+level_strings[level]+str(message)+"\n"
			f=open("/home/pi/logs/localServer.log",'a+')
			f.write(msg)
			f.close()






app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
