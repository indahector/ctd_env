#!/bin/bash
set -e
set -x

mkdir tmp
cd tmp
curl -O https://repo.anaconda.com/archive/Anaconda3-2023.09-0-MacOSX-arm64.sh
### Follow instructions of installer
bash Anaconda3-2023.09-0-MacOSX-arm64.sh

PYTHON_VERSION=3.11
ENVIRONMENT_NAME=ctd-env

conda create -y --quiet -c conda-forge -n ${ENVIRONMENT_NAME} python=${PYTHON_VERSION}

source activate $ENVIRONMENT_NAME

# install mamba
conda install -c conda-forge mamba --quiet --yes

# install conda packages (channels managed in YAML file)
# pip dependencies also managed in YAML file
mamba env update -f requirements.yml

source activate $ENVIRONMENT_NAME
  
mamba env update -f requirements.yml

#remove temp file
rm $HOME/.my_conda_envs

cd ..
