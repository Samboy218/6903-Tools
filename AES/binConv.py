#Author: Will Johnson
#Date: 11/20/18
#project: AES tool
#Use Case: Encrypt/Decrypt large strings with AES

#!/usr/bin/python

import sys
import binascii

#take a string of text
#return a string of bits
def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
	bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
	return bits.zfill(8 * ((len(bits) + 7) // 8))

#take a string of bits
#return a string of hex
def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
	n = int(bits, 2)
	return int2bytes(n).decode(encoding, errors)

#makes this possible in python 2 OR python 3
def int2bytes(i):
	hex_string = '%x' % i
	n = len(hex_string)
	return binascii.unhexlify(hex_string.zfill(n + (n & 1)))

#takes a string of bits
#returns a hex character
def bits_to_hex(bits):
	if(bits == '0000'): return '0'
	elif(bits == '0001'): return '1'
	elif(bits == '0010'): return '2'
	elif(bits == '0011'): return '3'
	elif(bits == '0100'): return '4'
	elif(bits == '0101'): return '5'
	elif(bits == '0110'): return '6'
	elif(bits == '0111'): return '7'
	elif(bits == '1000'): return '8'
	elif(bits == '1001'): return '9'
	elif(bits == '1010'): return 'a'
	elif(bits == '1011'): return 'b'
	elif(bits == '1100'): return 'c'
	elif(bits == '1101'): return 'd'
	elif(bits == '1110'): return 'e'
	elif(bits == '1111'): return 'f'
	else: return ' '
	
#takes a hex character
#returns a string of bits	
def bits_from_hex(hex_data):
	if(hex_data == '0'): return '0000'
	elif(hex_data == '1'): return '0001'
	elif(hex_data == '2'): return '0010'
	elif(hex_data == '3'): return '0011'
	elif(hex_data == '4'): return '0100'
	elif(hex_data == '5'): return '0101'
	elif(hex_data == '6'): return '0110'
	elif(hex_data == '7'): return '0111'
	elif(hex_data == '8'): return '1000'
	elif(hex_data == '9'): return '1001'
	elif(hex_data == 'a'): return '1010'
	elif(hex_data == 'b'): return '1011'
	elif(hex_data == 'c'): return '1100'
	elif(hex_data == 'd'): return '1101'
	elif(hex_data == 'e'): return '1110'
	elif(hex_data == 'f'): return '1111'
	else: return ' '
