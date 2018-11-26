pyTRASH - Python Tool for Remote Access Shells (Hopefully)
======
**pyTRASH** is a simple HTTPS beaconing Remote Access Tool (RAT) that is compatible with the c2TRASH Server
## The Protocol

See c2TRASH for the latest documentation

## Features

### Upload

pyTRASH allows the C2 server to upload a file to the machine running goTRASH

### Download

pyTRASH can exfil arbitrary files to the C2 server

### Execute

If a command sent to goTRASH that isn't a specific control command (e.g. `upload` or `download`), it is passed to a raw shell and executed in the background.

The results are sent back to the C2 server.


### Loadable modules

Using python, it is easy to exec / eval python code dynamically to inject additional functionality. The `load_module` command can inject new python modules into the pyTRASH client at runtime.

### Supported Commands

```
Normal Commands:

upload       -  Upload a file to the client
download     -  Download a file from the client
execute      -  Run a shell command
execute_file -  Make a file executable and run

Internal Commands:

send_msg     -  Send a message to the C2 Server
send_file    -  Send a file to the C2 Server

Special Commands:

load_module  -  exec a python file (from the C2 server) in memory to load new functions
exec_py      -  exec a python string in memory

```

### Stability?

Ha, no

