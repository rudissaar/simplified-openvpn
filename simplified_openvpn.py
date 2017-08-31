#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import socket
import re
import pystache
import zipfile
import json
from shutil import copyfile
from subprocess import run
from slugify import slugify
from requests import get


class SimplifiedOpenVPN:
    settings = dict()
    settings['server'] = dict()
    settings['client'] = dict()

    settings['server']['clients_dir'] = '/root/openvpn-clients/'
    settings['server']['server_dir'] = '/etc/openvpn/'
    settings['server']['easy_rsa_dir'] = '/etc/openvpn/easy-rsa/'
    settings['server']['sovpn_config_file'] = '/etc/openvpn/sovpn.json'
    settings['server']['hostname'] = None
    settings['server']['protocol'] = 'udp'

    settings['client']['pretty_name'] = None

    def __init__(self):
        self.load_config()

    def load_config(self):
        config_file_path = self.settings['server']['sovpn_config_file']
        if os.path.isfile(config_file_path):
            with open(config_file_path) as config_file:
                data = json.load(config_file)
                for pool in data:
                    for key, value in data[pool].items():
                        setattr(self, key, value)

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
            return False
        return True

    is_valid_domain = is_valid_hostname

    @staticmethod
    def fetch_hostname_by_system():
        return socket.getfqdn()

    @staticmethod
    def fetch_hostname_by_reverse_dns(ip):
        return socket.gethostbyaddr(ip)

    def fetch_hostname_by_config_file(self):
        if os.path.isfile(self.settings['server']['sovpn_config_file']):
            with open(self.settings['server']['sovpn_config_file']) as config_file:
                data = json.load(config_file)
                hostname = data['server']['hostname']

            if self.is_valid_hostname(hostname):
                return hostname

        return None

    @property
    def hostname(self):
        hostname = self.settings['server']['hostname']
        if hostname is None:
            hostname = self.fetch_hostname_by_config_file()

        return hostname

    @hostname.setter
    def hostname(self, value):
        if not self.is_valid_hostname(value):
            return False

        self.settings['server']['hostname'] = value
        return True

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
        status = self.handle_common_dir_setting('easy_rsa_dir', value)
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

    @property
    def protocol(self):
        if self.settings['server']['protocol'] is not None:
            return self.settings['server']['protocol']
        return None

    @protocol.setter
    def protocol(self, value):
        protocols = ['udp', 'tcp']
        if isinstance(value, str) and value.lower() in protocols:
            self.settings['server']['protocol'] = value
        else:
            print('Value that you specified as protocol is invalid: ("' + value + ')')
            print('Allowed values:')
            for protocol in protocols:
                print('>' + protocol, end=' ')

    @property
    def pretty_name(self):
        return self.settings['client']['pretty_name']

    @pretty_name.setter
    def pretty_name(self, value):
        self.settings['client']['pretty_name'] = value.strip()

    @property
    def client_dir(self):
        return self.settings['client']['client_dir']

    @client_dir.setter
    def client_dir(self, slug, create=True):
        value = self.settings['server']['clients_dir'] + slug
        if create:
            self.create_directory(value)
        status = self.handle_common_dir_setting('client_dir', value, 'client')

    def client_dir_exists(self, slug, verbose=True):
        if os.path.isdir(self.settings['server']['clients_dir'] + slug):
            print('Client this with common name already exists.')
            return True
        return False

    def create_pretty_name_file(self):
        if not self.settings['client']['client_dir']:
            return False

        if self.settings['client']['pretty_name']:
            file_path = self.settings['client']['client_dir'] + 'pretty-name.txt'
            file_handle = open(file_path, 'w')
            file_handle.write(self.settings['client']['pretty_name'] + "\n")
            file_handle.close()
            return True

        return False

    def move_client_files(self, slug):
        client_files = [slug + '.crt', slug + '.key']
        for client_file in client_files:
            source = self.settings['server']['easy_rsa_dir'] + 'keys/' + client_file
            destination = self.settings['client']['client_dir'] + client_file
            os.rename(source, destination)

    def copy_ca_file(self):
        source = self.settings['server']['easy_rsa_dir'] + 'keys/ca.crt'
        destination = self.settings['client']['client_dir'] + 'ca.crt'
        copyfile(source, destination)
         
    def copy_ta_file(self):
        source = self.settings['server']['server_dir'] + 'ta.key'
        destination = self.settings['client']['client_dir'] + 'ta.key'
        copyfile(source, destination)

    def create_client_config_options(self):
        config_options = dict()
        config_options['protocol'] = self.protocol
        return config_options

    def create_client_config_file(self):
        config_template = self.settings['server']['server_dir'] + 'client.mustache'
        if not os.path.isfile(config_template):
           return False

        renderer = pystache.Renderer()

        config_options = self.create_client_config_options()
        config_path = self.settings['client']['client_dir'] + self.hostname + '.ovpn'
        config_file = open(config_path, 'w')
        config_file.write(renderer.render_path(config_template, config_options))
        config_file.close()

    def create_client_config_files(self):
        self.create_client_config_file()

    def create_client(self, pretty_name=None):
        if self.settings['client']['pretty_name'] is None:
            while pretty_name is None:
                pretty_name = input('Enter Full Name for client: ').strip()
                slug = slugify(pretty_name)
                if self.client_dir_exists(slug) or pretty_name == '':
                    pretty_name = None

            self.settings['client']['pretty_name'] = pretty_name
        else:
            slug = slugify(self.settings['client']['pretty_name'])
            if self.client_dir_exists(slug):
                exit(1)

        os.chdir(self.settings['server']['easy_rsa_dir'])
        run('./build-key ' + slug + ' 1> /dev/null', shell=True)

        self.client_dir = slug
        self.create_pretty_name_file()
        self.move_client_files(slug)
        self.copy_ca_file()
        self.copy_ta_file()

        os.chdir(self.settings['client']['client_dir'])

        self.create_client_config_files() 

