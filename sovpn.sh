#!/usr/bin/env bash

cd /etc/openvpn/easy-rsa 1> /dev/null
source /etc/openvpn/easy-rsa/vars 1> /dev/null
cd - 1> /dev/null

/usr/bin/env python3 './sovpn_client_create.py'

