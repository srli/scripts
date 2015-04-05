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

# class Camera():
# 	def __init__(self, cameraPort):
# 		self.cameraHandle = appleCamera.initCamera(cameraPort)
# 		self.integrationTimes = 10

# 	def takeImage(self):
# 		focusPostion = appleCamera.getFocus(self)
# 		image = appleCamera.getImage(self.integrationTimes, focusPostion)
# 		return image

# class Image():
# 	def __init__(self, brightness):
# 		self.brightness = brightness

if __name__ == "__main__":
	cameraPort = 1 #probably want to make this an argv input
	integrationTimes = 10 #not sure what this is, will make constant for now
	h = 480
	w = 600
	biggest_sharpness = 0

	myCamera = appleCamera.initCamera(cameraPort)
	if myCamera == -1:
		raise AssertionError('Camera could not initialize, check connections')
	#initializing complete

	while True: #this is bad, fix this, loops forever
		focusPostion = appleCamera.getFocus(myCamera)
		image = appleCamera.getImage(integrationTimes, focusPostion)
		processing_image = True
		while processing_image:
			brightness = cameraProcessing.getBrightness(image)
			if brightness < 150:
				#warning here, take another image
				raise AssertionError('Image too dark, retake')
				break #this is gross

			imageCenter = cameraProcessing.getCenter(image)
			centerDiffs = [imageCenter[0] - w/2, imageCenter[1] - h/2]
			if centerDiffs[0] != 0: #probably can't be exactly equal to 0...
				move_x(centerDiffs[0]*0.5) #we're multiplying by a scale so the camera doesn't shoot off in a direction
				break
			elif centerDiffs[1] != 0: #this way we move 1 direction at a time
				move_y(centerDiffs[1]*0.5)
				break

			imageOffset = cameraProcessing.getOffset(image)
			#same concept with offsetDiffs, start with Z offset though

			for i in range(10):
				sharpness = cameraProcessing.getSharpness(image)
				if sharpness > biggest_sharpness:
					finalImage = image
