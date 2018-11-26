
setup:
	pip install netifaces
	pip install prompt_toolkit
	pip install colored
	apt-get install tmux
	chmod +x plugins/metasploit/msfpc.sh

keys:
	openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
	openssl rsa -in key.pem -out key.pem
