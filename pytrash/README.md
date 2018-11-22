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

### Stability?

Ha, no

