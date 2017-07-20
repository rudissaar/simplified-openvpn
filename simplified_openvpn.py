#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
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

    def set_clients_dir(self, clients_dir):
        clients_dir = self.sanitize_path(clients_dir)
        if not os.path.isdir(clients_dir):
            return False
        else:
            self.settings['clients_dir'] = clients_dir
            return True
        
    def create_client(self):
        print(self.settings)
