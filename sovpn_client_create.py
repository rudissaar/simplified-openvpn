#!/usr/bin/env python3
from simplified_openvpn import SimplifiedOpenVPN

sovpn = SimplifiedOpenVPN()
sovpn.set_server_dir('/uba')
sovpn.create_client()
