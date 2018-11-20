#Author: Will Johnson
#Date: 11/20/18
#project: AES tool
#Use Case: Encrypt/Decrypt large strings with AES

#!/usr/bin/python

import sys
import encrypt
import decrypt
import binConv


#takes a plaintext message pt
#returns a message that has been padded by appending 0s.
#final message will be divisible by 16.
def pad_message(pt):
	pt_list = list(pt)
	if(len(pt_list) % 16 != 0):
		for x in range(16 - (len(pt_list) % 16)):
			pt_list.append('0')
			
	return ''.join(pt_list)
	
	

#takes a plaintext message pt
#returns list of messages
#messages are split into 16 character strings
def split_message(pt, size):
	pt_list = list(pt)
	list_of_lists = []
	for x in range(0, len(pt), size):
		this_list = []
		for y in range(size):
			this_list.append(pt_list[x+y])
		list_of_lists.append(''.join(this_list))
	return list_of_lists
	
	
	
#takes message (string)
#creates payload (string)
#Payload is constructed as follows: [size of message, message, padded 0s]
#The size of the  message should be the first 16 bytes
#The message can be of size 9,999,999,999,999,999 characters (bytes)
#Zeros will be added to the message to ensure that it is divisible by 16.	
def create_payload(message):
	#add the size of the message to the top of the payload
	length_string_list = list(str(len(message)))
	
	if(len(length_string_list) > 16):
		print("Please enter a Plaintext that is less than 9,999,999,999,999,999 characters long.")
		return
	elif(len(length_string_list) < 16):
		for x in range(16 - len(length_string_list)):
			length_string_list.insert(0, '0')
	message_with_size = ''.join(length_string_list) + message
	
	#pad the message to ensure it is divisible by 16
	payload = pad_message(message_with_size)
	return payload
	


#takes a list of calculated plaintexts
#returns final message
#Appended 0s will be removed from the message using the message size bytes
def strip_payload(calc_pts):
	payload = ''
	for x in range(len(calc_pts)):
		if(x == 0):
			message_length = int(calc_pts[x])
		else:
			payload = payload + ''.join(calc_pts[x])
	
	payload_list = list(payload)
	stripped_message_list = payload_list[0:message_length]
	message = ''.join(stripped_message_list)
	return message
	
	

#Generates a payload, encrypts payload
#returns list of ciphertexts as a string of hex
def Encrypt(message, key):
	#generate the payload	
	payload = create_payload(message)
	
	#split the total payload into 16 character chunks
	chunks = split_message(payload, 16)
	
	#encrypt all of the chunks of the payload
	cts = []
	for chunk in chunks:
		ct = encrypt.encrypt_block(chunk, key)
		cts.append(ct)
	
	#assemble as ciphertexts together as one hex string
	cts_hex = ''
	for ct in cts:
		byte_list = split_message(ct, 4)
		for byte in byte_list:
			cts_hex = cts_hex + binConv.bits_to_hex(byte)
	return cts_hex
	
	

#Takes a list of ciphertexts as a string of hex (cts_hex) and a key
#returns the final calculated message
def Decrypt(cts_hex, key):
	#Convert string of Hex into a list of Ciphertexts
	cts_bytes = ''
	for letter in cts_hex:
		byte = binConv.bits_from_hex(letter)
		cts_bytes = cts_bytes + byte	
	cts = split_message(cts_bytes, 128)
	
	#Decrypt each ciphertext
	calc_pts = []
	for ct in cts:
		calc_pt = binConv.text_from_bits(decrypt.decrypt_block(ct, key))
		calc_pts.append(calc_pt)
	
	#strip the payload, and reassemble the message!
	calc_message = strip_payload(calc_pts)
	calc_message = calc_message.encode('ascii', 'ignore')
	return calc_message
	
	

def main():
	#collect message and key
	message = sys.argv[1]
	key = 'Sixteen Letters!'
	
	#encrypt
	cts_hex = Encrypt(message, key)
	
	print("CT in Hex: " + cts_hex)
	
	#decrypt
	calc_message = Decrypt(cts_hex, key)
	
	print calc_message
	
if __name__ == "__main__" :
	main()
