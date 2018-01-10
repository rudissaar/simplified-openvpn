#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=R0904

'''Management interface for OpenVPN Community Edition.'''

import os
import socket
import zipfile
import json
from shutil import copyfile
from subprocess import run
import pystache
from slugify import slugify
from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper
from simplified_openvpn_config import SimplifiedOpenvpnConfig


class SimplifiedOpenvpn:
    '''Main class that takes care of managing OpenVPN on your server.'''

    def __init__(self):
        '''Loads config if possible, else asks you to generate config.'''
        self._config = SimplifiedOpenvpnConfig()
        if self.needs_setup():
            self.config_setup()
        else:
            self.load_config()
            self._config = SimplifiedOpenvpnConfig()

    def needs_setup(self):
        '''Check if the script needs to run initial setup.'''
        if os.path.isfile(self._config.sovpn_config_file):
            return False
        return True

    def load_config(self):
        '''Populate properties with values if config file exists.'''
        if os.path.isfile(self._config.sovpn_config_file):
            with open(self._config.sovpn_config_file) as config_file:
                data = json.load(config_file)
                for pool in data:
                    for key, value in data[pool].items():
                        setattr(self, key, value)

    def fetch_hostname_by_reverse_dns(self, ipv4=None):
        '''Tries to fetch hostname by reverse DNS lookup and returns it if possible.'''
        if ipv4 is None:
            ipv4 = self.fetch_external_ipv4()
        if ipv4:
            return socket.gethostbyaddr(ipv4)
        return None

    def get_suggestion_hostname(self):
        '''Returns suggestion for hostname value.'''
        suggestion = _helper.fetch_hostname_by_system()

        if suggestion is None:
            suggestion = self.fetch_hostname_by_reverse_dns()
        return suggestion

    def config_setup(self):
        '''Set up settings for Simplified OpenVPN on current system.'''
        config = dict()

        sample_config_path = os.path.dirname(os.path.realpath(__file__)) + '/sovpn.json'
        with open(sample_config_path) as sample_config:
            config = json.load(sample_config)

        '''Getting hostname for config.'''
        suggestion = self.get_suggestion_hostname()
        while self.hostname is None:
            prompt = '> Enter hostname of your server: '
            if suggestion:
                prompt += '[' + suggestion + '] '
            hostname = input(prompt)
            if hostname.strip() == '':
                hostname = suggestion

            #config['server']['hostname'] = self.hostname = hostname

        '''Getting protocol for config.'''
        suggestion = None
        if config['server']['protocol']:
            suggestion = config['server']['protocol']
        while self.protocol is None:
            prompt = '> Select protocol that you would like to use: (TCP|UDP) '
            if suggestion:
                prompt += '[' + suggestion + '] '
            protocol = input(prompt)
            if protocol.strip() == '':
                protocol = suggestion

            config['server']['protocol'] = self.protocol = protocol.lower()

        '''Getting port for config.'''
        suggestion = None
        if config['server']['port']:
            suggestion = config['server']['port']
        while self.port is None:
            prompt = '> Select port that you are using for for your server: '
            if suggestion:
                prompt += '[' + str(suggestion) + '] '
            port = input(prompt)
            if port.strip() == '':
                port = suggestion

            config['server']['port'] = self.port = int(port)

        '''Write config values to file.'''
        with open(self._config.server_dir + 'sovpn.json', 'w') as config_file:
            config_file.write(json.dumps(config) + "\n")

        client_template_path = os.path.dirname(os.path.realpath(__file__)) + '/templates/client.mustache'
        copyfile(client_template_path, self._config.server_dir + 'client.mustache')

    def client_dir_exists(self, verbose=True):
        if self._config.slug is None or self._config.clients_dir is None:
            return None

        if os.path.isdir(self._config.clients_dir + self._config.slug):
            print('Client this with common name already exists.')
            return True
        return False

    def create_pretty_name_file(self):
        if not self._config.client_dir:
            return False

        if self._config.pretty_name:
            file_path = self._config.client_dir + 'pretty-name.txt'
            file_handle = open(file_path, 'w')
            file_handle.write(self._config.pretty_name + "\n")
            file_handle.close()
            return True

        return False

    def move_client_files(self):
        client_files = [self._config.slug + '.crt', self._config.slug + '.key']
        for client_file in client_files:
            source = self._config.easy_rsa_dir + 'keys/' + client_file
            destination = self._config.client_dir + client_file
            os.rename(source, destination)

    def copy_ca_file(self):
        source = self._config.easy_rsa_dir + 'keys/ca.crt'
        destination = self._config.client_dir + 'ca.crt'
        copyfile(source, destination)

    def copy_ta_file(self):
        source = self._config.server_dir + 'ta.key'
        destination = self._config.client_dir + 'ta.key'
        copyfile(source, destination)

    def create_client_config_options(self):
        config_options = dict()
        config_options['protocol'] = self._config.protocol
        config_options['hostname'] = self._config.hostname
        config_options['ipv4'] = self._config.ipv4
        config_options['port'] = self._config.port
        config_options['slug'] = self._config.slug
        config_options['inline'] = False
        return config_options

    def create_client_config_file(self, config_options, flavour=''):
        '''Creates a single config file/archive for client and writes it to the disk.'''
        config_template = self._config.server_dir + 'client.mustache'
        if not os.path.isfile(config_template):
            return False

        renderer = pystache.Renderer()

        config_path = self._config.client_dir + self._config.hostname
        if flavour != '':
            config_path += '-' + flavour
        config_path += '.ovpn'

        config_file = open(config_path, 'w')
        config_file.write(renderer.render_path(config_template, config_options))
        config_file.close()

        if not config_options['inline']:
            with zipfile.ZipFile(config_path + '.zip', 'w') as config_zip:
                config_zip.write(config_path)
                config_zip.write(self._config.client_dir + 'ca.crt', 'ca.crt')
                config_zip.write(self._config.client_dir + self._config.slug + '.crt', self._config.slug + '.crt')
                config_zip.write(self._config.client_dir + self._config.slug + '.key', self._config.slug + '.key')
                config_zip.write(self._config.client_dir + 'ta.key', 'ta.key')

            '''Remove config file that you just zipped but keep certificates for others.'''
            os.remove(config_path)

    def create_client_config_files(self):
        '''Create different flavours of client's config files.'''
        config_options = self.create_client_config_options()

        '''Plain Windows flavour.'''
        self.create_client_config_file(config_options)

        '''Plain Debian flavour.'''
        config_options['deb'] = True
        self.create_client_config_file(config_options, 'deb')
        config_options['deb'] = False

        '''Plain RedHat flavour.'''
        config_options['rhel'] = True
        self.create_client_config_file(config_options, 'rhel')
        config_options['rhel'] = False

        '''Inline Windows flavour.'''
        config_options['inline'] = True
        config_options['ca'] = _helper.read_file_as_value(self._config.client_dir + 'ca.crt')
        config_options['cert'] = _helper.read_file_as_value(self._config.client_dir + self._config.slug + '.crt')
        config_options['key'] = _helper.read_file_as_value(self._config.client_dir + self._config.slug + '.key')
        config_options['ta'] = _helper.read_file_as_value(self._config.client_dir + 'ta.key')
        self.create_client_config_file(config_options, 'inline')

        '''Inline Debian flavour.'''
        config_options['deb'] = True
        self.create_client_config_file(config_options, 'inline-deb')
        config_options['deb'] = False

        '''Inline RedHat flavour.'''
        config_options['rhel'] = True
        self.create_client_config_file(config_options, 'inline-rhel')
        config_options['rhel'] = False

        '''Clean up.'''
        self.cleanup_client_certificates()

    def cleanup_client_certificates(self):
        '''Cleans up client's certificates as they are no longer needed.'''
        cert_files = [self._config.slug + '.crt', self._config.slug + '.key', 'ca.crt', 'ta.key']
        for cert_file in cert_files:
            os.remove(self._config.client_dir + cert_file)

    def create_client(self, pretty_name=None):
        if self._config.pretty_name is None:
            while pretty_name is None:
                pretty_name = input('Enter Full Name for client: ').strip()
                self._config.slug = pretty_name
                if self.client_dir_exists(self._config.slug) or pretty_name == '':
                    pretty_name = None

            self._config.pretty_name = pretty_name
        else:
            self._config.slug = self._config.pretty_name
            if self.client_dir_exists(self._config.slug):
                exit(1)

        os.chdir(self._config.easy_rsa_dir)
        run('./build-key ' + self._config.slug + ' 1> /dev/null', shell=True)

        self._config.client_dir = self._config.slug
        self.create_pretty_name_file()
        self.move_client_files()
        self.copy_ca_file()
        self.copy_ta_file()

        os.chdir(self._config.client_dir)

        self.create_client_config_files()
