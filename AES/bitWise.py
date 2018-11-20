#Author: Will Johnson
#Date: 11/20/18
#project: AES tool
#Use Case: Encrypt/Decrypt large strings with AES

#!/usr/bin/python

import sys

#logical shift the given string s by order positions to the left
def shift_left(s, order):
	s_list = list(s)
	for w in range(order):
		temp = s_list[0]
		for x in range(0, len(s_list)-1,):
			s_list[x] = s_list[x + 1]
		s_list[len(s_list)-1] = temp
	return ''.join(s_list)

#logical shift the given string s by order positions to the right
def shift_right(s, order):
	s_list = list(s)
	for w in range(order):
		temp = s_list[len(s_list)-1]
		for x in range(len(s_list)-1, 0, -1) :
			s_list[x] = s_list[x-1]
		s_list[0] = temp
	return ''.join(s_list)

#xor the two given strings
#assume they are already in binary
#assume they are the same length
def xor(s1, s2):
	s1_list = list(s1)
	s2_list = list(s2)
	r_list = []
	if len(s1) != len(s2):
		print "string lengths do not match!"
		return ' '
		
	for x in range(len(s1_list)):
		if(s1_list[x] == '1' and s2_list[x] == '1'):
			r = '0'
		elif(s1_list[x] == '0' and s2_list[x] == '0'):
			r = '0'
		else:
			r = '1'
		r_list.append(r)
	return ''.join(r_list)
	
#takes 16 byte key
#returns ten 16 byte round keys
def key_expansion(key):
	key_l = list(key)
	if len(key) != 16:
		return " "
	key_list = []
	for x in range(10):
		key_list.append(shift_right(key, x))
	return key_list	
