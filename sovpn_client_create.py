#!/usr/bin/env python3
from simplified_openvpn import SimplifiedOpenVPN

sovpn = SimplifiedOpenVPN()
sovpn.server_dir = '/root'
sovpn.create_client()
