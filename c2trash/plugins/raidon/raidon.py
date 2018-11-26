import shlex
import os
from .. import plugin

def get_cmds():
    return ['drop_raidon']

def drop_raidon(cmd_str, arg_str=""):
    target = plugin._get_target()
    if not target:
        print("Set target first!")
        return
    if not arg_str:
        print("Syntax: drop_raidon <path-to-raidon> [-o <name-on-target>]")
        return

    arg_str, outname = plugin.get_filename(arg_str) 

    return plugin._drop_tool(arg_str, plugin.nc_listener(), outname=outname)
