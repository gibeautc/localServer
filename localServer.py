#!/usr/bin/env python

from daemon import runner
import threading
import time
#import database
import datetime
import subprocess
import sys
import os
from wd import checkWD,setupWD
DEBUG=1
INFO=2
WARNING=3
ERROR=4
LOGLEVEL=1

general_launch='/home/pi/SatCom_Client/'
pid_pre='/tmp/'
pid_post='.pid'

service_list=['localconDaemon','syncDaemon']
class Service():
	def __init__(self,fn):
		self.filename=fn
		self.pid=None
		self.status=None
		self.last=time.time()
class App():
	def __init__(self):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/tty'
		self.stderr_path = '/dev/tty'
		self.pidfile_path =  '/tmp/watchdog.pid'
		self.pidfile_timeout = 5
	def run(self):
		self.log(ERROR,"\n\n\n\n\n********Starting up**********")	
		self.services=[]
		self.pipefile,self.pipe=setupWD()
		for service in service_list:
			self.log(INFO,"Adding serive: "+service)
			self.services.append(Service(service))
		
		while True:
			self.log_service()
			self.get_pid_status()
			self.check_pipe()
			self.check_time()
			time.sleep(10)

	def check_pipe(self):
		msg=checkWD(self.pipefile,self.pipe)
		for m in msg:
			found=False
			try:
				n=int(m)
			except:
				continue
			for p in self.services:
				if p.pid is not None:
					if n==int(p.pid):
						#found it
						self.log(INFO,"Got checkin from: "+p.filename)
						p.last=time.time()
						found=True
			if not found:		
				self.log(WARNING,"Found Unknown PID: "+str(n))
	def restart(self,p):
		#can get here either by no PID or by no checkin
		self.log(INFO, "Restarting: "+ p.filename)
		if p.pid is None:
			#no need to stop it
			try:
				subprocess.call(["/home/pi/SatCom_Client/"+p.filename+".py","start"])
			except:
				self.log(ERROR, "Error Launching Daemon")
				self.logerror()
				
		
	def check_time(self):	
		for p in self.services:
			if time.time()-p.last>60:
				self.log(ERROR,p.filename+" Service needs to be restarted")
				#this is the case where we have not heard from it
				self.restart(p)
				
	def log_service(self):
		for serv in self.services:
			self.log(INFO,serv.filename)
			self.log(INFO,"PID:"+str(serv.pid))
			if time.time()-serv.last<60:
				self.log(INFO,"Delta:"+str(int(time.time()-serv.last)))
			else:
				self.log(ERROR,"Delta:"+str(int(time.time()-serv.last)))
			self.log(INFO,"")					
			
	def Pid(self,serv):
		if serv.filename==None or serv.filename=="":
			serv.pid=None
			self.log(ERROR,"No Filename given")
			return
		f=pid_pre+serv.filename+pid_post
		self.log(DEBUG,"Trying to cat: "+f)
		p=subprocess.Popen(["cat",f],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output,err=p.communicate()
		if  err!="":
			serv.pid=None
			self.log(ERROR,"Error Loading PID file:"+err)
			#this is the case where it crashed or isnt running, no PID
			self.restart(serv)
			return
		#self.log(DEBUG,"Output for "+serv.filename+" : "+str(int(output)))
		#print(int(output))
		serv.pid=str(int(output))
		#check if file exists
		#read and set PID 
	

	def get_pid_status(self):
		self.log(DEBUG,"Checking Services....")
		for service in self.services:
			self.Pid(service)

	def logerror(self):
		self.log(ERROR,sys.exc_info())	


	def log(self,level,message):
		level_strings=["","DEBUG- ","INFO- ","WARNING- ","ERROR- "]
		if level>=LOGLEVEL:
			msg=str(datetime.datetime.now())
			msg=msg.split(".")
			msg=msg[0]
			msg=msg+" Client_LocalCon-"+level_strings[level]+str(message)+"\n"
			f=open("/home/pi/logs/client_watchdog",'a+')
			f.write(msg)
			f.close()






app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
