#Author: Will Johnson
#Date: 11/20/18
#project: AES tool
#Use Case: Encrypt/Decrypt large strings with AES

#!/usr/bin/python

import sys
import bitWise
import binConv

#substitutes a matrix of bytes with another matrix of bytes
#This function can be changed.  It just has to do the inverse of 
#the sub bytes in the decrypt file
#Think S box (the one I did here is very weak)
def sub_bytes(pt):
	ctL = []
	for bit in pt:
		if bit == '0':
			ctL.append('1')
		elif bit == '1':
			ctL.append('0')
	ct = ''.join(ctL)
	return ct

#Mixes the columns of a given byte matrix around.
#This function can be changed.  It just has to do the opposite of 
#the one in the decrypt file
def mix_cols(pt):
	ptList = list(pt)
	ctList = []
	col1 = []
	col2 = []
	col3 = []
	col4 = []
	cols = [col1, col2, col3, col4]

	for x in range(len(pt)):
		cols[x % 4].append(ptList[x])

	for y in range(len(col1)):
		ctList.append(cols[3][y])
		ctList.append(cols[2][y])
		ctList.append(cols[1][y])
		ctList.append(cols[0][y])

	return ''.join(ctList)

#Shifts rows of a byte matrix by given AES standards
def shift_rows(pt):
	row1 = []
	row2 = []
	row3 = []
	row4 = []
	ptList = list(pt)

	for x in range(len(pt)):
		if(x < 32):
			row1.append(ptList[x])
		elif(x < 64):
			row2.append(ptList[x])
		elif(x < 96):
			row3.append(ptList[x])
		elif(x < 128):
			row4.append(ptList[x])

	row1s = ''.join(row1)
	row2s = bitWise.shift_left(''.join(row2), 8)
	row3s = bitWise.shift_left(''.join(row3), 16)
	row4s = bitWise.shift_left(''.join(row4), 24)

	return row1s + row2s + row3s + row4s

#encrypts one AES block
#takes a plaintext pt, and a key
#returns a ciphertext CT
def encrypt_block(pt, key):
	#convert pt to binary
	ptb = binConv.text_to_bits(pt)
	
	#generate the round keys, convert them to binary
	round_keys = bitWise.key_expansion(key)
	round_keys_b = []
	for key in round_keys:
		keyb = binConv.text_to_bits(key)
		round_keys_b.append(keyb)

	#pre transformation
	working_ct = bitWise.xor(round_keys_b[0], ptb)

	#10 Rounds of encryption
	for x in range(10):
		working_ct = sub_bytes(working_ct)
		working_ct = shift_rows(working_ct)
		if(x < 9):
			working_ct = mix_cols(working_ct)
		working_ct = bitWise.xor(round_keys_b[x], working_ct)

	ct = working_ct
	return ct
