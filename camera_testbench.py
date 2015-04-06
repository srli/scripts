"""
Assumptions
		Camera can be controlled by including the appleCamera interface that has the following functions:
			cameraHandle = initCamera(int cameraPort) -> returns a handle / interface to the camera or -1 if it couldn’t initialize
			image = getImage(int integrationTimems, int focusPosition) -> returns an image with the specified integration time at the
			requested focus position or -1 if there was an error.
			focusPostion = getFocus(cameraHandle myCamera) -> returns the approximate best focus position of the camera

		Images from the camera can be processed by using cameraProcessing interface that has the following functions:
			brightness = getBrightness (image inputImage) -> returns the average brightness of the image.
			sharpness = getSharpness (image inputImage) -> returns the average sharpness of the image.
			imageCenter = getCenter(image inputImage) ->  returns the detected target center of the image,
			as an array with [0] = X, [1] = Y. Ideally, center is (w/2, h/2)
			imageOffset = getOffset (image inputImage) -> returns the detect target tilt offsets of the image,
			as an array, with [0] = X offset, [1] = Y offset, [2] = Z offset from the ideal center. Ideally, offsets are 0.

The code should be commented as if you were handing it off to somebody else to build a test case around.
Python / C is fine for the language used.

		Write a program that will center the camera to the target and finish by saving the image with the best centering,
		best sharpness, and lowest offset
		The image functions will not work with an image that does not have an average brightness of at least 150
		Error handling should report the error and then abort the program.

"""

"""
Ok, so workflow:
Initalize camera (probably want to make this a class)

Get initial focus, getImage with said focus

Check brightness of image. If < 150, loop back to getImage, else print/log warning and loop back to getImage
^getBrightness should be called before any other image function, allows us to make quick escapes

Calculate imageCenter of image, changing X, Y servo positions until center is w/2, h/2. These servo movements should be
pretty large.

Calculate imageOffset in loop. Go through X, Y, Z positions until all offsets are zero (Arduino + SEROVS here).
While in this loop. These servo movements should be smaller.

Calculate sharpness of image. Take a bunch of images here in case the lighting conditions are changing. Shouldn't
need to move servos nor calculate focusPostion

Save sharpest image. End program.

Notes:
(Are we outputting errors/warnings to a .txt file? Might as well)
getFocus needs to be called every time a servo is moved.
Don't know how the servo control scheme works, just assume we're moving it by some scale
Why would we need to use external code/apis when the assumed scripts do the things we need it to do?
^need to write pyserial stuff to communicate with Arduino
^need to also write the .ino stuff that moves servos

Assume we have a move_x, move_y, and move_z script that takes in the distance the servo needs to move
"""
#!/usr/bin/env python

#importing this way so it's clear which interface functions are coming from
import appleCamera
import cameraProcessing

import serial
import struct #packs the move_servo information into bytes to send over serial to Arduino
import warnings
import time

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
		if brightness < 150: 			#Brightness under 150 threshold won't work with cameraProcessing functions, must detect
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
		#Many same concepts as centerCamera, refer to above
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
		return self.finalImage

if __name__ == "__main__":
	cameraPort = 1
	myCamera = CameraTestbench(cameraPort)
	image = myCamera.bestImage()

