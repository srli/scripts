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
....
Actually!
Sort the first column, then sort the second column, no need to calculate multiplication at all

We'll treat this array as a list of tuples? python?
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
		# Don't forget to return something!
		return sort(less)+equal+sort(greater)  # Just use the + operator to join lists
	# Note that you want equal ^^^^^ not pivot
	else:  # You need to hande the part at the end of the recursion - when you only have one element in your array, just return the array.
		return array

def test_sort(array):
	passed = True
	first_product = array[0][1] * array[0][0]
	for i in (2):
		element = array[i]
		first_product = first_product*(element[0]*element[1])
	for i in range(3,len(array)):
		element = array[i]
		prev_element = array[-i]
		product = first_product*(element[0]*element[1])


test_array = [[randint(0,10) for i in range(2)] for j in range(randint(0,20))]
#test_array = [4,6,9,10,20,44,12,0,2,2,4]
print test_array
sorted_array = sort(test_array)
print sorted_array
#epeatarrays = identify_repeats(sorted_array)
#repeatarrays2 = identify_repeats(sorted_array)

#print repeatarrays
#print repeatarrays2