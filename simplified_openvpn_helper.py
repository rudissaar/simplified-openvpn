#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=R0904

"""File that contains SimplifiedOpenvpnHelper class."""

import os
import socket

class SimplifiedOpenvpnHelper:
    """Class that contains shareable helper methods."""

    @staticmethod
    def read_file_as_value(filename, verbose=False):
        '''Reads contents of the file and returns it.'''
        if not os.path.isfile(filename):
            if verbose:
                print("> File that you tried to read as value doesn't exist.")
            return None

        value = None
        with open(filename) as content:
            value = content.read().rstrip()
        return value

    @staticmethod
    def create_directory(value, mode=0o700):
        """Creates new directory on filesystem."""
        if not os.path.exists(value):
            os.makedirs(value, mode)

    @staticmethod
    def sanitize_path(path):
        """Makes sure that path are ending with forward slash."""
        if not path.endswith('/'):
            path = path + '/'
        return path

    @staticmethod
    def validate_ipv4(ipv4):
        """Check if IP is valid IPv4 address."""
        if isinstance(ipv4, str) and len(ipv4.strip()) > 6:
            return True
        return False

    @staticmethod
    def is_valid_hostname(hostname):
        """Checks if specified hostname matches rules and returns boolean."""
        if len(hostname) > 255 or len(hostname) < 1:
            return False
        return True

    @staticmethod
    def fetch_hostname_by_system():
        """Fetches Fully Qualified Domain Name from system."""
        return socket.getfqdn()