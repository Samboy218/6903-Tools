goTRASH - go Tool for Remote Access Shells (Hopefully)
======
**goTRASH** is a simple HTTPS beaconing Remote Access Tool (RAT) that is compatible with the c2TRASH Server
## The Protocol

See c2TRASH for the latest documentation

## Features

### Upload

goTRASH allows the C2 server to upload a file to the machine running goTRASH

### Download

goTRASH can exfil arbitrary files to the C2 server

### Execute

If a command sent to goTRASH that isn't a specific control command (e.g. `upload` or `download`), it is passed to a raw shell and executed in the background.

The results are sent back to the C2 server.


### Cross platform

Using go, it should be possible to compile goTRASH to a platform-specific binary (limiting dependency problems)

### Stability?

Ha, no

