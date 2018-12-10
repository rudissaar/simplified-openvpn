#!/usr/bin env python3
# -*- coding: utf-8 -*-

"""File that contains SimplifiedOpenvpnMgmt class."""

import sys
import socket

from simplified_openvpn_config import SimplifiedOpenvpnConfig

class SimplifiedOpenvpnMgmt:
    """Class that contains methods that deal with management interface."""
    def __init__(self):
        """Constructor method."""
        self._config = SimplifiedOpenvpnConfig()

        if self.check_config():
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self._config.mgmt_address, self._config.mgmt_port))

    def check_config(self):
        """Checks if management interface is configured to be used."""
        if not self._config.mgmt_address or not self._config.mgmt_port:
            print('> Management interface is not configured.')
            sys.exit(1)

        return True

    def kick(self, slug):
        """Kills connection for specific user identified by slug."""
        try:
            command = 'kill ' + slug + "\n"
            self._socket.sendall(str.encode(command))
        finally:
            self._socket.close()
