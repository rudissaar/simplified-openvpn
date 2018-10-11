#!/usr/bin/env bash
# Script that installs native dependencies on Debian GNU/Linux.

# You need root permissions to run this script.
if [[ "${UID}" != '0' ]]; then
    echo '> You need to become root to run this script.'
    exit 1
fi

apt-get update
apt-get install -y \
    python3 \
    python3-requests \
    python3-pystache \
    python3-flask \
    python3-slugify

