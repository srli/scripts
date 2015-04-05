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

We'll treat this array as a list of tuples? python or c++
c++ works better
"""
#include <stdio.h>      /* printf, scanf, puts, NULL */
#include <stdlib.h>     /* srand, rand */
#include <time.h>

int main{
	int seed;
	int array[n][2];

	seed = srand (time(NULL));
	return 0;
}