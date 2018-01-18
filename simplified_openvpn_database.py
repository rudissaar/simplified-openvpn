#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File that contains SimplifiedOpenvpnDatabase class."""

import os
import sqlite3
from simplified_openvpn_config import SimplifiedOpenvpnConfig

class SimplifiedOpenvpnDatabase:
    """Class that contains methods that deal with database."""
    def __init__(self):
        """Method that sets up connection to database."""
        self._config = SimplifiedOpenvpnConfig()
        self.connection = sqlite3.connect(self._config.container + 'sovpn.sqlite')
