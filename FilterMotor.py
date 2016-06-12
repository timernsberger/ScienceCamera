#!/usr/bin/env python

#==>add usage docstring
"""
#install for raspberrypi
#libusb via aptget
#phidgetlib from phidget website
#pip install phidgets


"""

import time
import os
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, CurrentChangeEventArgs, StepperPositionChangeEventArgs, VelocityChangeEventArgs
from Phidgets.Devices.Stepper import Stepper
from Phidgets.Phidget import PhidgetLogLevel
import fw_io
import numpy as np


class FilterMotor(object):
	def __init__(self):
		"""Add docs to all functions"""
		self.stepper = None
		self.fw = fw_io.FWIO()
		self.dict = {"velocity":None, "amp":None, "acceleration":None, "position":None, "power":None, "hall":None, "commanded":None, "filterDelta":6860, "ID":None}

	def DisplayDeviceInfo(self):
		#==> rename to getDeviceInfo
    		print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (self.stepper.isAttached(), self.stepper.getDeviceName(), self.stepper.getSerialNum(), self.stepper.getDeviceVersion()))
    		print("Number of Motors: %i" % (self.stepper.getMotorCount()))
		return

	def connDev(self):
		"""connect to device and open serial connection to arduino"""
		self.stepper = Stepper()
                self.stepper.openPhidget()
                self.stepper.waitForAttach(10000)

		self.setParm(20000,6000,0.75)

		self.fw.openPort()
		time.sleep(2)
		return

	def disconnDev(self):
		time.sleep(1)
		self.motorPower(False)
		self.stepper.closePhidget()
		return

	def motorPower(self, val = False):
		self.stepper.setEngaged(0,val)
		return

	def setParm(self, acc, vel, cur):
		self.stepper.setAcceleration(0, acc) 
	    	self.stepper.setVelocityLimit(0, vel)
		self.stepper.setCurrentLimit(0,cur)
		if cur>1.4:				
			print "Cannot set current above 1.5. Current set to 0.5"
			return
		return
 
	def status(self):
		self.dict['power'] = self.stepper.getEngaged(0)
		self.dict['position'] = int(self.stepper.getCurrentPosition(0))
		self.dict['acceleration'] =self.stepper.getAcceleration(0)
		self.dict['velocity'] = self.stepper.getVelocityLimit(0)
		self.dict['amp'] = self.stepper.getCurrentLimit(0)
		self.dict['hall'] = self.fw.getStatus()
		return self.dict

	def setPos(self, pos = None):
		self.stepper.setCurrentPosition(0, int(pos))	
		return

	def moveMotor(self, pos = None):
		self.motorPower(True)
		self.stepper.setTargetPosition(0, int(pos))
		self.dict["commanded"] = pos
		return

	def nudge(self, mov):
		x = self.stepper.getCurrentPosition(0) + mov 
		self.movemotor(x)
		time.sleep(0.5)
		print "New Position:", self.stepper.getCurrentPosition(0)
		return

	def test3(self):
		x = 0
		while x != 1:
			continue
		print "hi" 

	def filterselect(self, num = None):
		print "Moving to filter position %d" % num
		if int(num)<= 6 and int(num)>=0:
			self.movemotor(int(num)*7050)
			tpos = num*7050
			while self.getCurrentPosition() != tpos:
				continue
			while switch == false:
				self.movemotor(tpos+1000)
				if switch == True:
					self.motorstop()
					self.setCurrentPosition(0,tpos)
				else: 
					self.movemotor(tpos-1000)
					if switch == True:
						self.motorstop()
						self.setCurrentPosition(0,tpos)
			
		elif int(num)>6:
			print "Not Valid Filter Number"
		elif int(num)<0:
			print "Not Valid Filter Number"

	def test(self, x): #test for drifting
		n=0		
		while n<x:
			n+=1
			print n
			self.filterselect(6)
			time.sleep(8)
			self.filterselect(0)
			time.sleep(8)	

	def motorStop(self):
		self.stepper.setVelocityLimit(0,0)
		time.sleep(0.2)
		self.setParm(20000,6000,0.75)
		return

	def home(self): 
		crossArr = [0]
		pastHome = 0
		previousPos = 0
		print "starting home sequence"
		self.setPos(0)
		print "starting slew"
		self.moveMotor(100000)
		time.sleep(1)
		self.status()
		while int(self.dict['position']) < int(self.dict['commanded']):
			self.status()
			if self.dict['hall'][0] == '0':
				if self.dict['hall'][0] == '0' and self.dict['hall'][1] == '0':
					if pastHome == 0: 
						pastHome = pastHome + 1
                                        	print "First Home: ", self.status()
						previousPos = self.dict['position']
					if  self.dict['position'] - previousPos >  3000:
						pastHome = pastHome + 1
						print "Second Home: ", self.status() 
					if pastHome == 2:
						print "Set Home"
						self.motorStop()
						time.sleep(1)
						self.setPos(0)
						break
				if self.dict['position'] - previousPos >  3000:
					print self.dict['position'] - previousPos
					crossArr.append(self.dict['position'] - previousPos)
					print self.status(), crossArr
					previousPos = self.dict['position']
		del crossArr[0]
		del crossArr[0]
		self.dict['filterDelta'] = int(np.mean(crossArr))
		print "home"
		return

if __name__ == "__main__":
	p = FilterMotor()
	p.connDev()
	time.sleep(1)
	p.home()
	time.sleep(1)
	p.disconnDev()

