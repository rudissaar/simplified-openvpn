#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, inspect
from shutil import copyfile
from slugify import slugify
import pystache
import zipfile

class SimplifiedOpenVPN:
    settings = dict()

    def __init__(self):
        self.settings['clients_dir'] = '/root/openvpn-clients/'
        self.settings['server_dir'] = '/etc/openvpn/'
        self.settings['easy_rsa_dir'] = '/etc/openvpn/easy-rsa/'

    def sanitize_path(self, path):
        if not path.endswith('/'):
            path = path + '/'
        return path

    def handle_common_setting(self, key, value):
        value = self.sanitize_path(value)
        if not os.path.isdir(value):
            return False
        else:
            self.settings[key] = value
            return True

    def set_server_dir(self, value):
        return self.handle_common_setting('server_dir', value)

    def set_easy_rsa_dir(self, value):
        return self.handle_common_setting('easy_rsa_dir', value)
        
    def set_clients_dir(self, value):
        return self.handle_common_setting('clients_dir', value)
        
    def create_client(self):
        print(self.settings)
