#!/usr/bin/env python3
from simplified_openvpn import SimplifiedOpenVPN

sovpn = SimplifiedOpenVPN()
sovpn.set_clients_dir('/home')
sovpn.create_client()
