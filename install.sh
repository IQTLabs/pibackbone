#!/bin/bash
set -e

# check for dependencies
python3 -V > /dev/null || echo "First install python3 then try again."
pip3 -V > /dev/null || echo "First install pip3 then try again."
git --version > /dev/null || echo "First install git then try again."
uname -m > /dev/null # TODO check for arm, and version

# install docker if it's not already
docker version || echo "Installing Docker..." && curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh

# pull down pibackbone repo and install
git clone https://github.com/iqtlabs/pibackbone 
cd pibackbone && pip3 install . cd ..
rm -rf pibackbone

# run pibackbone
pibackbone
