#!/bin/sh
# Script that installs dependencies on NetBSD.

PYTHON_VERSION='3.6'

# You need root permissions to run this script.
if [ "$(id -u)" != '0' ]; then
    echo '> You need to become root to run this script.'
    exit 1
fi

# Export package mirror if it's not defined.
[ -z "${PKG_PATH}" ]
if [ "${?}" = '0' ]; then
    MIRROR='http://cdn.NetBSD.org/pub/pkgsrc/packages/NetBSD/'
    PKG_PATH="${MIRROR}$(uname -p)/$(uname -r | cut -f '1 2' -d . | cut -f 1 -d _)/All"
    export PKG_PATH
fi

PYTHON_PKG_VERSION=$(echo ${PYTHON_VERSION} | tr -d .)

# Install and use native dependencies much as possible.
pkg_add -v python${PYTHON_PKG_VERSION}
pkg_add -v py${PYTHON_PKG_VERSION}-pip
pkg_add -v py${PYTHON_PKG_VERSION}-pystache
pkg_add -v py${PYTHON_PKG_VERSION}-flask
pkg_add -v py${PYTHON_PKG_VERSION}-requests
pkg_add -v py${PYTHON_PKG_VERSION}-sqlite3

# NetBSD's package repository doesn't include slugify, so we use pip to install it.
pip${PYTHON_VERSION} install python-slugify

# If it's possible then create python3 link that points to more specific version.
if [ ! -L '/usr/bin/python3' ] && [ ! -f '/usr/bin/python3' ]; then
    which python${PYTHON_VERSION} 1> /dev/null 2>&1

    if [ "${?}" = '0' ]; then
        ln -sf $(which python${PYTHON_VERSION}) /usr/bin/python3
    fi
fi

