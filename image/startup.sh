#!/bin/bash

# Set the conda environment and package folder in the home folder
conda config --system --add envs_dirs /home/$NB_USER/.conda/envs
conda config --system --add pkgs_dirs /home/$NB_USER/.conda/pkgs
