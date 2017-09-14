#!/bin/bash

/usr/local/bin/start.sh  # rename user etc.

## launch daemonized SSHD
/usr/sbin/sshd

## launch daemonized supervisor
/usr/bin/supervisord

## start the notebook server, passing in all the environment variables
## we run as NB_USER to prevent 'start.sh' from doing its job twice
exec su $NB_USER -p -c "env PATH=$PATH HOME=/home/$NB_USER /usr/local/bin/start-singleuser.sh $*"
