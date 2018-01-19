#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File that contains SimplifiedOpenvpnData class."""

import sqlite3
from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper
from simplified_openvpn_config import SimplifiedOpenvpnConfig

class SimplifiedOpenvpnData:
    """Class that contains methods that deal with database."""
    def __init__(self):
        """Method that sets up connection to database."""
        self._config = SimplifiedOpenvpnConfig()
        self._db = sqlite3.connect(self._config.container + 'sovpn.sqlite')

        sql = _helper.read_file_as_value(self._config.container + 'sql/create_table_clients.sql')
        self._db.cursor().execute(sql)
        self._db.commit()

    def insert_share_hash(self, slug, share_hash):
        """Inserts new client record to clients table."""
        sql = _helper.read_file_as_value(self._config.container + 'sql/insert_clients_record.sql')
        self._db.cursor().execute(sql, [slug, share_hash])
        self._db.commit()
