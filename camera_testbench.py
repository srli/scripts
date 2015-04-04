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
#!/usr/bin/env python

from appleCamera import *
from cameraProcessing import *

if __name__ == "__main__":
	print "hello"
	integrationTimes = 10
	cameraPort = 1
	cameraHandle = initCamera(cameraPort)
	if cameraHandle == -1:
		raise AssertionError('Camera could not initialize, check connections')
	while True: #this is bad, fix this, loops forever
		focusPostion = getFocus() #this auto focuses the image
		image = getImage(integrationTimes, focusPostion)
		brightness = getBrightness(image)
		sharpness = getSharpness(image)
		imageCenter = getCenter(image)
		imageOffset = getOffset(image)