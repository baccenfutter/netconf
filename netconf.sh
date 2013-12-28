#!/bin/bash
# Script        : netconf.sh
# Description   : Commandline-based network manager
# Author        : Brian Wiborg <baccenfutter@c-base.org>
# License       : public domain
# Date          : 2013-12-27
#
# Default configuration directory: ~/.conf/net_conf
#
# Usage:
# netconf               - list networks
# netconf <network>     - connect to <network>

CONFIG_DIR=~/.config/net_conf

# first of all, check if net_conf has been installed properly
if ! python -c "import net_conf" &>/dev/null; then
    echo "Can not find net_conf in python-path!"
    echo "Please install net_conf before running this script."
    exit 1
fi

# bootstrap config directory if it doesn't exist
if [[ ! -d "$CONFIG_DIR" ]]; then
    echo "Creating configuration directory: $CONFIG_DIR"
    mkdir -p "$CONFIG_DIR"
    
    base="$0"
    if [[ -L "$base" ]]; then
        base=$(readlink "$base")
    fi
    path_name=$(dirname $base)
    cp "$path_name"/skel/* "$CONFIG_DIR"
fi

# check if user needs help
if [[ $1 == '--help' ]] || \
        [[ $1 == '-h' ]] || \
        [[ $1 == '-?' ]]
then
    sed '/^$/q' $0 | tail -n +2 | tr '!#' '  ' | tr '#' ' '
    exit 0
fi

# get all *.py files (a.k.a. networks) from config directory
IFS=$'\n' networks=( $(find "$CONFIG_DIR" -maxdepth 1 -type f -name \*.py) )

# transform network file-names into basenames
netnames=( )
for net in ${networks[@]}; do
    name=$(basename "${net%.py}")
    netnames+=( "$name" )
done

# 
if [[ -z $1 ]]; then
    if [[ ${#netnames[@]} -eq 0 ]]; then
        echo "read $CONFIG_DIR/howto.txt"
    else
        echo "Available networks:"
        for net in ${netnames[@]}; do
            echo " - $net"
        done
    fi
    exit
else
    counter=0
    for net in ${netnames[@]}; do
        if [[ "$net" == $1 ]]; then
            python ${networks[counter]}
            exit 0
        fi
        ((counter+=1))
    done
fi
echo "Unknown network: $1"
