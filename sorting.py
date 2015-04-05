"""
Given
A random 2D array of number pairs of size N, like the following:
Element A B
Required
Write a program that sorts the elements of the array so that the product of the elements before and after the current element are minimized.
IE: element(k) should be arranged such that
element(k-2)*element(k-1)*element(k) < element(k-1)*element(k)*element(k+1) < element(k)*element(k+1)*element(k+2)
where element(n) is the product of both numbers that belong to that element.
"""
"""
Thoughts
----
Just have to multiply numbers in A with corresp in B to get element(n), assuming the A and B numbers are paired
Literally just a sorted list, the products corollary doesn't really matter since if it's arranged in increasing order, it'll naturally follow
"""
#!/usr/bin/env python
from random import randint

def sort(array):
	#use quicksort
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
		return sort(less)+equal+sort(greater)  # Just use the + operator to join lists
	# Note that you want equal ^^^^^ not pivot
	else:  # You need to hande the part at the end of the recursion - when you only have one element in your array, just return the array.
		return array

def test_sort(array):
	for i in range(2,len(array)-2):
		prev_product = (array[i-2][1] * array[i-2][0])*(array[i-1][1] * array[i-1][0])*(array[i][1] * array[i][0])
	 	current_product = (array[i-1][1] * array[i-1][0])*(array[i][1] * array[i][0])*(array[i+1][1] * array[i+1][0])
	 	next_product = (array[i][1] * array[i][0])*(array[i+1][1] * array[i+1][0])*(array[i+2][1] * array[i+2][0])

	 	if current_product < prev_product:
	 		print "at %i, current product was %i and previous product was %i", i, current_product, prev_product
	 		#print current_product, next_product
	 		raise AssertionError('Sorting not correct, re-evaluate algorithm')
	 	elif current_product > next_product:
	 		print "at %i, current product was %i and next_product was %i", i, current_product, next_product
	 		raise AssertionError('Sorting not correct, re-evaluate algorithm')

if __name__ == '__main__':
	for i in range(100):
		test_array = [[randint(-20,20) for i in range(2)] for j in range(randint(1,100))] #these range values can be changed
		test_array.insert(0, [0,0]) #for sake of testing, we insert a [0,0] when numbers start to become positive
		sorted_array = sort(test_array)
		test_sort(sorted_array)
		sorted_array.remove([0,0]) #then remove so we're not altering the data
	print "Testing complete, sorting correct"