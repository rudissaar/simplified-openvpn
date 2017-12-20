#!/usr/bin/env bash
# TODO: Source ENV by using python.

cd /etc/openvpn/easy-rsa 1> /dev/null
source /etc/openvpn/easy-rsa/vars 1> /dev/null
cd - 1> /dev/null

if [[ "${1}" == 'share' ]]; then
    /usr/bin/env python3 './sovpn_share.py'
else
    /usr/bin/env python3 './sovpn_client_create.py'
fi
