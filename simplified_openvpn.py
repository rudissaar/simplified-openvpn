#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, socket, re
from shutil import copyfile
from subprocess import run
from slugify import slugify
from requests import get
import pystache
import zipfile

class SimplifiedOpenVPN:
    settings = dict()
    settings['server'] = dict()
    settings['client'] = dict()

    # Defaults.
    settings['server']['clients_dir'] = '/root/openvpn-clients/'
    settings['server']['server_dir'] = '/etc/openvpn/'
    settings['server']['easy_rsa_dir'] = '/etc/openvpn/easy-rsa/'

    def __init__(self):
        pass

    @staticmethod
    def validate_ip(ip):
        if type(ip) is str and len(ip.strip()) > 6:
            return True
        return False

    def fetch_external_ip(self):
        ip = get('http://api.ipify.org').text
        if self.validate_ip(ip):
            return ip.strip()
        return None

    def get_external_ip(self):
        ip = self.fetch_external_ip()
        while ip is None:
            ip = input('Enter External IP for server: ').strip()
            if not self.validate_ip(ip):
                ip = None
        return ip.strip()

    @staticmethod
    def is_valid_hostname(hostname):
        if len(hostname) > 255:
            print('False')
            return False
        print('True')
        return True

    is_valid_domain = is_valid_hostname

    @staticmethod
    def fetch_hostname_by_system():
        return socket.getfqdn()

    @staticmethod
    def fetch_hostname_by_reverse_dns(ip):
        return socket.gethostbyaddr(ip)

    def server_install(self):
        hostname = self.fetch_hostname_by_system()
        self.is_valid_domain(hostname)

    @staticmethod
    def sanitize_path(path):
        if not path.endswith('/'):
            path = path + '/'
        return path

    @staticmethod
    def create_directory(value, mode=0o700):
        if not os.path.exists(value):
            os.makedirs(value, mode)

    def handle_common_dir_setting(self, key, value, pool='server'):
        value = self.sanitize_path(value)
        if not os.path.isdir(value):
            return False
        else:
            self.settings[pool][key] = value
            return True

    @property
    def server_dir(self):
        return self.settings['server']['server_dir']

    @server_dir.setter
    def server_dir(self, value):
        status = self.handle_common_dir_setting('server_dir', value)
        if not status:
            print("Value that you specified as Server's directory is invalid: (" + value + ")")
            print('Make sure that the value you gave meets following requirements:')
            print('> Does the directory really exist in your filesystem?')
            print('> The specified directory has write and execute permissions.')
            exit(1)

    @property
    def easy_rsa_dir(self):
        return self.settings['server']['easy_rsa_dir']

    @easy_rsa_dir.setter
    def easy_rsa_dir(self, value):
        status = self.handle_common_setting('easy_rsa_dir', value)
        if not status:
            print("Value that you specified as directory for Easy RSA is invalid: (" + value + ")")
            print('Make sure that the value you gave meets following requirements:')
            print('> Does the directory really exist in your filesystem?')
            print('> The specified directory has write and execute permissions.')
            exit(1)

    @property
    def clients_dir(self):
        return self.settings['server']['clients_dir']

    @clients_dir.setter
    def clients_dir(self, value, create=False):
        if create:
            self.create_directory(value)

        status = self.handle_common_dir_setting('clients_dir', value)
        if not status:
            print("Value that you specified as directory for clients is invalid: (" + value + ")")
            print('Make sure that the value you gave meets following requirements:')
            print('> Does the directory really exist in your filesystem?')
            print('> The specified directory has write and execute permissions.')
            exit(1)

    def client_dir(self, slug, create=True):
        value = self.settings['clients_dir'] + slug
        if create:
            self.create_directory(value)
        status = self.handle_common_setting('client_dir', value)

    def client_dir_exists(self, slug, verbose=True):
        if os.path.isdir(self.settings['clients_dir'] + slug):
            print('Client this with common name already exists.')
            return True
        return False

    def move_client_files(self, slug):
        client_files = [slug + '.crt', slug + '.key']
        for client_file in client_files:
            os.rename(self.settings['easy_rsa_dir'] + 'keys/' + client_file, self.settings['client_dir'] + client_file)

    def copy_ca_file(self):
         copyFile(self.settings['easy_rsa_dir'] + 'keys/ca.crt', self.settings['client_dir'] + 'ca.crt')
         
    def copy_ta_file(self):
         copyFile(self.settings['server_dir'] + 'ta.key', self.settings['client_dir'] + 'ta.key')

    def create_client(self, common_name=None):
        if common_name is None:
            while common_name is None:
                common_name = input('Enter Common Name for client: ').strip()
                slug = slugify(common_name)
                if self.client_dir_exists(slug) or common_name == '':
                    common_name = None
        else:
            slug = slugify(common_name.strip())
            if self.client_dir_exists(slug):
                exit(1)

        os.chdir(self.settings['easy_rsa_dir'])
        run('./build-key ' + slug + ' 1> /dev/null', shell=True)

        self.set_client_dir(slug)
        self.move_client_files(slug)
        self.copy_ca_file()
        self.copy_ta_file()
