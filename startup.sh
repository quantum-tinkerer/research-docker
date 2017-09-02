#!/bin/bash

/usr/local/bin/start.sh  # rename user etc.

## launch daemonized SSHD
/usr/sbin/sshd

## launch daemonized supervisor
/usr/bin/supervisord

## rename the host to something cool
if [[ ! -z "$NB_HOSTNAME" ]]; then
    hostname "$NB_HOSTNAME"
fi

## start the notebook server, passing in all the environment variables
## we run as NB_USER to prevent 'start.sh' from doing its job twice
exec su -l $NB_USER -p -c "env PATH=$PATH /usr/local/bin/start-singleuser.sh $*"
