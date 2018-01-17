#!/usr/bin/env bash

if [[ "${1}" == 'share' ]]; then
    /usr/bin/env python3 './sovpn_share.py'
else
    /usr/bin/env python3 './sovpn_client_create.py'
fi
