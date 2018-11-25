SETTINGS = {
"exfil_dir":"/root/exfil/",
"static_dir":"static/",
"shell_dir":"shell/",
"plugins_dir":"plugins/",
"deploy_dir":"deploy/",
"payloads_dir":"payloads/",
"handlers_dir":"handlers/",
"plugin_cmds":[],
#"default_shell_handler":"nc -nvlp {REAL_PORT};",
#"default_shell_plugin":"False",
"default_shell_handler":"switchblade/switchblade.py -p {REAL_PORT};",
"default_shell_plugin":"True",
"tmux_welcome":"tmux_welcome.sh",
"LHOST":None,
"LPORT":None,
"RHOST":None,
"target":None,
"vars":["target", "LHOST", "LPORT", "RHOST", "STATIC_URL"],
"protocol":"https",
"STATIC_URL":None,
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

curr_prompt = None

style_dict = {
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
}

