#!/bin/bash

/usr/local/bin/start.sh  # rename user etc.

# start.sh does not explicitly set permissions on /home/$NB_USER
# and if we are mounting this from the docker host for the first
# time it will have root permissions
chown $NB_UID:$NB_GID /home/$NB_USER
cd /home/$NB_USER  # make sure that we're in the right place

# Set the conda environment and package folder in the home folder
conda config --system --add envs_dirs /home/$NB_USER/.conda/envs
conda config --system --add pkgs_dirs /home/$NB_USER/.conda/pkgs

## launch daemonized SSHD
mkdir -p /var/run/sshd
/usr/sbin/sshd

## launch daemonized supervisor
/usr/bin/supervisord

## start the notebook server, passing in all the environment variables
## we run as NB_USER to prevent 'start.sh' from doing its job twice
exec su $NB_USER -p -c "env PATH=$PATH HOME=/home/$NB_USER /usr/local/bin/start-singleuser.sh $*"
