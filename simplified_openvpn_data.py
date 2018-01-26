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

        sql = self.read_sql_file('create_table_clients.sql')
        self._db.cursor().execute(sql)
        self._db.commit()

    def read_sql_file(self, sql_file):
        """Reads sql from file and returns it."""
        sql = _helper.read_file_as_value(self._config.container + 'sql/' + sql_file)
        return sql

    def insert_share_hash(self, slug, share_hash):
        """Inserts new client record to clients table."""
        sql = self.read_sql_file('insert_client_record.sql')
        self._db.cursor().execute(sql, [slug, share_hash])
        self._db.commit()

    def find_client_slug_by_share_hash(self, share_hash):
        """Returns slug that is fetched by share's hash."""
        sql = self.read_sql_file('find_client_slug_by_hash.sql')
        cursor = self._db.cursor()
        cursor.execute(sql, [share_hash])
        result = cursor.fetchone()
        if result:
            return result[0]
        return None

    def find_client_share_hash_by_slug(self, slug):
        """Returns share's hash that is fetched by slug."""
        sql = self.read_sql_file('find_client_hash_by_slug.sql')
        cursor = self._db.cursor()
        cursor.execute(sql, [slug])
        result = cursor.fetchone()
        if result:
            return result[0]
        return None

    def get_all_client_slugs(self):
        """Returns list that contains client slugs."""
        sql = self.read_sql_file('select_client_slugs.sql')
        cursor = self._db.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        slugs = list()
        for record in result:
            slugs.append(record[0])
        return slugs
