#!/bin/bash
set -e

cwd=$PWD

# install basics
sudo apt-get update && sudo apt-get install -yq build-essential git python3-pip python3-smbus python3-urwid screen tmux

# check for dependencies
python3 -V > /dev/null || echo "First install python3 then try again."
pip3 -V > /dev/null || echo "First install pip3 then try again."
git --version > /dev/null || echo "First install git then try again."
uname -m > /dev/null # TODO check for arm, and version

# install docker if it's not already
docker version || echo "Installing Docker..." && curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo usermod -aG docker "$(whoami)"

# pull down pibackbone repo and install
cd /opt
git clone https://github.com/iqtlabs/pibackbone 
cd pibackbone
pip3 install .
sudo cp scripts/pibackbone_cron /etc/cron.d/pibackbone

# disable unneeded services
sudo systemctl stop avahi-daemon.service
sudo systemctl stop avahi-daemon.socket
sudo systemctl stop apt-daily-upgrade.service
sudo systemctl stop apt-daily-upgrade.timer
sudo systemctl disable avahi-daemon.service
sudo systemctl disable avahi-daemon.socket
sudo systemctl disable apt-daily-upgrade.service
sudo systemctl disable apt-daily-upgrade.timer

# TODO change swap size to 8GB
# sudo dphys-swapfile swapoff
# sudo vi /etc/dphys-swapfile
# CONF_SWAPSIZE=8192
# sudo dphys-swapfile setup
# sudo dphys-swapfile swapon
# requires a reboot to take effect

# set raspi-config options
sudo cp config.txt /boot/config.txt
sudo raspi-config nonint do_i2c 0

cd "$cwd"

# run pibackbone
pibackbone
