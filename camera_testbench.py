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
import warnings

if __name__ == "__main__":
	cameraPort = 1 #probably want to make this an argv input
	integrationTimes = 10 #not sure what this is, will make constant for now
	h = 480 #typical image dimensions
	w = 600

	myCamera = appleCamera.initCamera(cameraPort)
	if myCamera == -1:
		raise AssertionError('Camera could not initialize, check connections')
	#initializing complete

	taking_image = True
	centering = True
	offsetting = True

	highest_sharpness = 0
	i = 0
	try:
		ser = serial.Serial('/dev/ttyACM0, 9660')
	except:
		raise AssertionError('Could not connect to Arduino, check connections')

	while taking_image: #this is bad, fix this, loops forever
		focusPostion = appleCamera.getFocus(myCamera)
		image = appleCamera.getImage(integrationTimes, focusPostion)

		try:
			brightness = cameraProcessing.getBrightness(image)
			if brightness < 150:
				warnings.warn('Image too dark, retaking')
				continue
		except:
			warnings.warn('Image too dark, retaking')
			continue

		if centering:
			move_direction = [0,0,0] #x,y,z
			imageCenter = cameraProcessing.getCenter(image)
			centerDiffs = [imageCenter[0] - w/2, imageCenter[1] - h/2]
			if (-5 >= centerDiffs[0]) or (centerDiffs[0] >= 5): #probably can't be exactly equal to 0... however, this code can easily be changed for 0
				move_direction[0] = (centerDiffs[0]*0.5) #we're multiplying by a scale so the camera doesn't shoot off in a direction
			elif (-5 >= centerDiffs[1]) or (centerDiffs[1] >= 5): #this way we move 1 direction at a time
				move_direction[1] = (centerDiffs[1]*0.5)
			else:
				centering = False
			ser.write(move_direction)
			continue

		if offsetting:
			move_direction = [0,0,0]
			imageOffset = cameraProcessing.getOffset(image)
			if (-5 >= imageOffset[0]) or (imageOffset[0] >= 5): #probably can't be exactly equal to 0... however, this code can easily be changed for 0
				move_direction[0] = (imageOffset[0]*0.5) #could do this in a loop...
			elif (-5 >= imageOffset[1]) or (imageOffset[1] >= 5): #this way we move 1 direction at a time
				move_direction[1] = (imageOffset[1]*0.5)
			elif (-5 >= imageOffset[2]) or (imageOffset[2] >= 5): #this way we move 1 direction at a time
				move_direction[2] = (imageOffset[2]*0.5)
			else:
				offsetting = False
			ser.write(move_direction)
			continue

		if i < 10:
			sharpness = cameraProcessing.getSharpness(image)
			if sharpness > biggest_sharpness:
				finalImage = image
			i += 1

		if i == 10:
			taking_image = False
			#save somehow finalImage
