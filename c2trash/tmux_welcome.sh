#!/bin/bash
# This script has to return the keystrokes that should be sent to new tmux panes
# POC for automated shell handling (e.g. connection received-> execute a set of commands
cat << EOD
(
(sleep 1; cat << EOF
Welcome to a Tmux Session!
This is your host machine, be nice to it.

Helpful Commands:

CTRL+B,D    :   Detach (return to pyTRASH prompt)
CTRL+D      :   Kill this session
CTRL+B,)    :   Cycle through other Tmux Sessions
EOF
) &
)  2>&1
clear
EOD
