"""
@author: Sophia Li

This code generates 100 2byN arrays of random numbers and sorts so that element[k] is
	element(k-2)*element(k-1)*element(k) < element(k-1)*element(k)*element(k+1) < element(k)*element(k+1)*element(k+2)

It uses quicksort, the foundational code found from: http://stackoverflow.com/questions/18262306/quick-sort-with-python
"""

#!/usr/bin/env python
from random import randint

def sort(array):
	#using quicksort
	less = []
	equal = []
	greater = []

	if len(array) > 1:
		pivot = (array[0][0]*array[0][1])
		for element in array:
			x = (element[0]*element[1])
			if x < pivot:
				less.append(element)
			if x == pivot:
				equal.append(element)
			if x > pivot:
				greater.append(element)
		return sort(less)+equal+sort(greater)  #Using + operator to join lists
	else:  #When one element in array, returns the array.
		return array


def test_sort(array):
	for i in range(2,len(array)-2):
		prev_product = (array[i-2][1] * array[i-2][0])*(array[i-1][1] * array[i-1][0])*(array[i][1] * array[i][0])
	 	current_product = (array[i-1][1] * array[i-1][0])*(array[i][1] * array[i][0])*(array[i+1][1] * array[i+1][0])
	 	next_product = (array[i][1] * array[i][0])*(array[i+1][1] * array[i+1][0])*(array[i+2][1] * array[i+2][0])

	 	if current_product < prev_product:
	 		print "at index %i, current product was %i and previous product was %i" % (i, current_product, prev_product)
	 		raise AssertionError('Sorting not correct, re-evaluate algorithm')
	 	elif current_product > next_product:
	 		print "at index %i, current product was %i and next_product was %i" % (i, current_product, next_product)
	 		raise AssertionError('Sorting not correct, re-evaluate algorithm')


if __name__ == '__main__':
	for i in range(100): 				#doing 100 trials
		test_array = [[randint(-20,20) for i in range(2)] for j in range(randint(1,100))] 	#these range values can be changed
		test_array.insert(0, [0,0]) 	#for sake of testing, we insert a [0,0] so there's a buffer between negative and positive elements
		sorted_array = sort(test_array)
		#print sorted_array
		test_sort(sorted_array)
		sorted_array.remove([0,0]) 		#then remove so we're not altering the data
	print "Testing complete, sorting correct"