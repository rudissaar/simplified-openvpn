#!/usr/bin/env bash
# Script that installs native dependencies on Fedora GNU/Linux.

# You need root permissions to run this script.
if [[ "${UID}" != '0' ]]; then
    echo '> You need to become root to run this script.'
    exit 1
fi

dnf check-update

dnf install -y \
    python3 \
    python3-pystache \
    python3-flask \
    python3-slugify

