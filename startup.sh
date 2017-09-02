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

## start the notebook server
exec su $NB_USER -c "/usr/local/bin/start-singleuser.sh $*"
