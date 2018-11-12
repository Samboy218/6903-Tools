# 6903-tools


# Brainstorming

Minimal, cross platform implant written in Go (easy to write, compiles to binary).
POC: https://github.com/EgeBalci/EGESPLOIT 
Features:

    *    Beacon (basic functionality done)

    *    Upload (basic functionality done)

    *    Download (basic functionality done)

    *    Execute

    *    Windows: DLL injection / Ability to throw back full shells / meterpreter
Resources:

        https://silentbreaksecurity.com/srdi-shellcode-reflective-dll-injection/
        https://github.com/monoxgas/sRDI
        https://0x00sec.org/t/weaponized-exploit-writing-in-go-fusion0/3184

Python HTTPS "C2" server

    *    "interactive" command execution (very, very basic functionality done)

    *    changing implant configuration variables (basic functionality done)

    *    organizing output of commands

    *    upload / download (basic functionality done)

    *    Handler multiplexing through IPTables -- e.g. have all shells connect to kali:443. Through IPTables, if sourceIP = target1 and destport=443, rewrite destport=XXX1 -- spawn listener on XXX1

    *    Additional: logging callbacks, logging commands sent, countdown to next expected beacon, logging results of commands

Python, Meterpreter-like RAT

    *    Dynamic (python) code injection (very basic functionality done)

POC  of Python C2 and Python RAT in pyTRASH (Python Tool For Remote Access Shells, Hopefully)

Windows-Specific things:

    *    Would be very cool and realistic

    *    Probably hard to develop? Visual Studio, Windows SDK, etc.

    *    Maybe we could make something windows-specific (a simple RAT, keylogger, Ransomware, etc.) as a standalone DLL to simplify things and load it with the persistent implant.

    *    A RAT could be relatively easily written in C# and basically be a powershell wrapper (https://www.blackhillsinfosec.com/powershell-w-o-powershell-simplified/ )

Cool Module Ideas (DLL or Python, dynamically loadable):

    *    Keylogger

    *    Screen Capture

    *    Ransomware

    *    Encryption (e.g. RC4 comms to the C2 server wrapped in HTTPS)

    *    Alternate exfil comms -- e.g. exfil via DNS or ICMP

    *    "Track" remote files for automatic exfil


Quality of Life Ideas:

    *    Tab completion on server

    *    UUIDs for targets and commands that are sent to implant

    *    Cosmetic fixes on Server TUI

Known Challenges

    *   NAT -- targets are not uniquely identifiable by source IP address -- need UUIDs!

    *   Impant death -- implants should basically never die, ever. Wrap in a massive try / catch that alerts the C2

    *   Multiple implants -- related to need for UUIDs. Multiple implants / implant instances on the same victim will conflict and do very scary things
