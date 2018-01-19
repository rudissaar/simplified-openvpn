#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File that contains SimplifiedOpenvpnData class."""

import os
import sqlite3
from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper
from simplified_openvpn_config import SimplifiedOpenvpnConfig

class SimplifiedOpenvpnData:
    """Class that contains methods that deal with database."""
    def __init__(self):
        """Method that sets up connection to database."""
        self._config = SimplifiedOpenvpnConfig()
        self.db = sqlite3.connect(self._config.container + 'sovpn.sqlite')
        sql = _helper.read_file_as_value(self._config.container + 'sql/create_table_clients.sql')
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
    
    def insert_client(self, slug, pretty_name = None):
        """Inserts new client record to clients table."""
        sql = _helper.read_file_as_value(self._config.container + 'sql/insert_clients_record.sql')
        cursor = self.db.cursor()
        cursor.execute(sql, [slug, pretty_name, 'aaa'])
        self.db.commit()
        
