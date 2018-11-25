import os
import shlex
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

def prepare_listener(listener_cmd, options={}):
    s = "catch {} {}".format("{RHOST}", shlex.quote(listener_cmd))
    
    s = _replace_vars(s, options)    
    s = _replace_vars(s, _get_default_vars())  
    print(s)
    return s
