"""
@author: Sophia Li

This code initializes a camera handler from appleCamera, then centers a camera to a scene and saves an image with the lowest offest,
highest sharpness and best centering using functions from cameraProcessing.

It requires an Arduino/MBED device connected on port /dev/ttyACM0 to move the camera servos
"""
#!/usr/bin/env python

#importing this way so it's clear which interface functions are coming from
import appleCamera
import cameraProcessing

import serial
import struct 	#packs the moveCamera information into bytes to send over serial to Arduino
import warnings
import time
import json 	#for saving the final image

class CameraTestbench:
	def __init__(cameraPort):
		#Initializing the camera handler
		self.myCamera = appleCamera.initCamera(cameraPort)
		if self.myCamera == -1:
			raise AssertionError('Camera could not initialize, check connections/port')

		#Opening serial port for communcation with Arduino/MBED device
		try:
			self.ser = serial.Serial('/dev/ttyACM0, 9660')
		except:
			raise AssertionError('Could not open port ttyACM0, check connections/port')

		#Arbitrary defined constants. Change for the situation
		self.integrationTimes = 15 		#Not sure what this is, change as necessary

		self.imageHeightCenter = 480/2	#Common image dimensions (480x600). Value divided by 2 because we want the center
		self.imageWidthCenter = 600/2

		self.centerThreshold = 5 		#Defining center and offset thresholds, because it's hard to get exactly the optimal numbers. Saves time calibrating
		self.offsetThreshold = 0.1 		#Smaller thresholds mean more precise camera centering/zeroing but at cost of time

		self.servoRate = 0.7 			#Defines how quickly the servos will spin depending on distance to desired value
										#This can be set to 1, then defined inside the Arduino script

		#Initalizing various variables
		self.focusPostion = 0
		self.current_image = 0

		self.sharpestImage = 0
		self.bestImage = self.current_image

		self.moveCamera = [0,0,0] 		#formatted in [x, y, z]


	def takeImage(self):
		self.focusPostion = appleCamera.getFocus(self.myCamera)
		self.current_image = appleCamera.getImage(self.integrationTimes, self.focusPostion)


	def checkBrightness(self):
		bright = True
		brightness = cameraProcessing.getBrightness(self.current_image)
		if brightness < 150: 			#Brightness under 150 threshold won't work with cameraProcessing functions, must  check here
			#raise AssertionError('Image too dark, change camera setting conditions') 	#Can also raise AssertionError to exit program
			warnings.warn('Image too dark, retake necessary')
			bright = False
		return bright


	def centerCamera(self):
		centering = True
		timeout = time.time() + 60*2	#timeout 2 minutes from now, prevents infinite loops

		while centering:
			self.takeImage()
			if self.checkBrightness():	#If brightness is >150, then run rest of cameraProcessing steps. Otherwise, skip everything and take another image
				imageCenter = cameraProcessing.getCenter(self.current_image)
				centerDiffs = [imageCenter[0] - self.imageWidthCenter, imageCenter[1] - self.imageHeightCenter]
				for i in range(2):
					self.moveCamera[i] = (centerDiffs[i]*self.servoRate)
				if (abs(centerDiffs[0]) and abs(centerDiffs[1]) < self.centerThreshold) or time.time() > timeout: 	#if X, Y position are within centerThreshold, centering is done
					centering = False																				#if loop has been running too long, centering also autoexits


	def zeroOffset(self):
		#Many same concepts as centerCamera, refer to above comments
		zeroing = True
		timeout = time.time() + 60*2

		while zeroing:
			self.takeImage()
			if self.checkBrightness():
				imageOffset = cameraProcessing.getOffset(self.current_image)
				for i in range(3):
					self.moveCamera[i] = (imageOffset[i]*self.servoRate)
				if (abs(imageOffset[0]) and abs(imageOffset[1]) and abs(imageOffset[2]) < self.offsetThreshold) or time.time() > timeout:
					zeroing = False


	def findSharpest(self):
		for i in range(10): 								#Take 10 images and pick the sharpest of them all, can change this number
			self.takeImage()
			if self.checkBrightness():
				sharpness = cameraProcessing.getSharpness(self.current_image)
				if sharpness > self.sharpestImage:
					self.finalImage = self.current_image	#Rewrites finalImage to current_image when the current has a better sharpness


	def moveServos(self):
		for i in self.moveCamera:
			serialString += struct.pack('!B', i) 			#Packing each element in moveCamera list to a binary string for serialWrite
		self.ser.write(serialString)						#Expecting Arduino code to accept this serial string and act on it


	def bestImage(self):
		self.centerCamera()
		self.zeroOffset()
		self.findSharpest()
		with open('image.txt', 'w') as outfile:				#This writes the image as a string to a .txt file. Can be easily changed to save in different formats
			json.dump(self.finalImage, outfile)


if __name__ == "__main__":
	cameraPort = 1
	myCamera = CameraTestbench(cameraPort)
	myCamera.bestImage()
