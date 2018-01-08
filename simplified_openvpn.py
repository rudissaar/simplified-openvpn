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
from requests import get
from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper
from simplified_openvpn_config import SimplifiedOpenvpnConfig


class SimplifiedOpenvpn:
    '''Main class that takes care of managing OpenVPN on your server.'''
    settings = dict()
    settings['server'] = dict()
    settings['client'] = dict()

    settings['server']['hostname'] = None
    settings['server']['ipv4'] = None
    settings['server']['ipv6'] = None
    settings['server']['port'] = None
    settings['server']['protocol'] = None

    settings['client']['slug'] = None
    settings['client']['pretty_name'] = None

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

    def fetch_external_ipv4(self):
        '''Fetch external IPv4 address.'''
        ipv4 = get('http://api.ipify.org').text

        if _helper.validate_ipv4(ipv4):
            return ipv4.strip()
        return None

    def get_external_ipv4(self):
        '''Return external IPv4 address, prompt for it if necessary.'''
        ipv4 = self.fetch_external_ipv4()

        while ipv4 is None:
            ipv4 = input('Enter External IP address for server: ').strip()

            if not _helper.validate_ipv4(ipv4):
                return None

        return ipv4.strip()

    def fetch_hostname_by_reverse_dns(self, ipv4=None):
        '''Tries to fetch hostname by reverse DNS lookup and returns it if possible.'''
        if ipv4 is None:
            ipv4 = self.fetch_external_ipv4()
        if ipv4:
            return socket.gethostbyaddr(ipv4)
        return None

    def fetch_hostname_by_config_file(self):
        '''Tries to fetch hostname from sovpn config file.'''
        if os.path.isfile(self._config.sovpn_config_file):
            with open(self._config.sovpn_config_file) as config_file:
                data = json.load(config_file)
                hostname = data['server']['hostname']

            if _helper.is_valid_hostname(hostname):
                return hostname

        return None

    def get_suggestion_hostname(self):
        '''Returns suggestion for hostname value.'''
        suggestion = _helper.fetch_hostname_by_system()

        if suggestion is None:
            suggestion = self.fetch_hostname_by_reverse_dns()
        return suggestion

    @property
    def hostname(self):
        '''Returns value of hostname property.'''
        hostname = self.settings['server']['hostname']
        if hostname is None:
            hostname = self.fetch_hostname_by_config_file()

        return hostname

    @hostname.setter
    def hostname(self, value):
        '''Assign new value to hostname property.'''
        if not _helper.is_valid_hostname(value):
            print('Value that you specified as Hostname is invalid: (' + value + ')')
        else:
            self.settings['server']['hostname'] = value

    @property
    def ipv4(self):
        '''Returns value of ipv4 property.'''
        ipv4 = self.settings['server']['ipv4']
        if ipv4 is None:
            ipv4 = self.get_external_ipv4()
        return ipv4

    @property
    def port(self):
        return self.settings['server']['port']

    @port.setter
    def port(self, value):
        self.settings['server']['port'] = int(value)

    @property
    def slug(self):
        return self.settings['client']['slug']

    @slug.setter
    def slug(self, value):
        slug = slugify(value)
        self.settings['client']['slug'] = slug

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

            config['server']['hostname'] = self.hostname = hostname

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

    @staticmethod
    def sanitize_path(path):
        '''Makes sure that path are ending with forward slash.'''
        if not path.endswith('/'):
            path = path + '/'
        return path

    @staticmethod
    def create_directory(value, mode=0o700):
        '''Creates new directory on filesystem.'''
        if not os.path.exists(value):
            os.makedirs(value, mode)

    def handle_common_dir_setting(self, key, value, pool='server'):
        '''Checks if directory can be assigned to property and sets it if possible.'''
        value = self.sanitize_path(value)
        if not os.path.isdir(value):
            return False

        self.settings[pool][key] = value
        return True

    @property
    def protocol(self):
        '''Returns value of protocol property.'''
        if self.settings['server']['protocol'] is not None:
            return self.settings['server']['protocol']
        return None

    @protocol.setter
    def protocol(self, value):
        '''Assigns new value to protcol property.'''
        protocols = ['udp', 'tcp']

        if isinstance(value, str) and value.lower() in protocols:
            self.settings['server']['protocol'] = value.lower()

    @property
    def pretty_name(self):
        '''Returns value of pretty_name property.'''
        return self.settings['client']['pretty_name']

    @pretty_name.setter
    def pretty_name(self, value):
        '''Assigns new value to pretty_name property.'''
        self.settings['client']['pretty_name'] = value.strip()

    @property
    def client_dir(self):
        '''Returns value of client_dir property.'''
        return self.settings['client']['client_dir']

    @client_dir.setter
    def client_dir(self, slug, create=True):
        '''Assigns new value to client_dir property.'''
        value = self._config.clients_dir + slug
        if create:
            self.create_directory(value)
        status = self.handle_common_dir_setting('client_dir', value, 'client')

    def client_dir_exists(self, verbose=True):
        if self.slug is None or self._config.clients_dir is None:
            return None

        if os.path.isdir(self._config.clients_dir + self.slug):
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
            source = self._config.easy_rsa_dir + 'keys/' + client_file
            destination = self.settings['client']['client_dir'] + client_file
            os.rename(source, destination)

    def copy_ca_file(self):
        source = self._config.easy_rsa_dir + 'keys/ca.crt'
        destination = self.settings['client']['client_dir'] + 'ca.crt'
        copyfile(source, destination)

    def copy_ta_file(self):
        source = self._config.server_dir + 'ta.key'
        destination = self.settings['client']['client_dir'] + 'ta.key'
        copyfile(source, destination)

    def create_client_config_options(self):
        config_options = dict()
        config_options['protocol'] = self.protocol
        config_options['hostname'] = self.hostname
        config_options['ipv4'] = self.ipv4
        config_options['port'] = self.port
        config_options['slug'] = self.slug
        config_options['inline'] = False
        return config_options

    def create_client_config_file(self, config_options, flavour=''):
        '''Creates a single config file/archive for client and writes it to the disk.'''
        config_template = self._config.server_dir + 'client.mustache'
        if not os.path.isfile(config_template):
            return False

        renderer = pystache.Renderer()

        config_path = self.client_dir + self.hostname
        if flavour != '':
            config_path += '-' + flavour
        config_path += '.ovpn'

        config_file = open(config_path, 'w')
        config_file.write(renderer.render_path(config_template, config_options))
        config_file.close()

        if not config_options['inline']:
            with zipfile.ZipFile(config_path + '.zip', 'w') as config_zip:
                config_zip.write(config_path)
                config_zip.write(self.client_dir + 'ca.crt')
                config_zip.write(self.client_dir + self.slug + '.crt')
                config_zip.write(self.client_dir + self.slug + '.key')
                config_zip.write(self.client_dir + 'ta.key')

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
        config_options['ca'] = _helper.read_file_as_value(self.client_dir + 'ca.crt')
        config_options['cert'] = _helper.read_file_as_value(self.client_dir + self.slug + '.crt')
        config_options['key'] = _helper.read_file_as_value(self.client_dir + self.slug + '.key')
        config_options['ta'] = _helper.read_file_as_value(self.client_dir + 'ta.key')
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
        cert_files = [self.slug + '.crt', self.slug + '.key', 'ca.crt', 'ta.key']
        for cert_file in cert_files:
            os.remove(self.client_dir + cert_file)

    def create_client(self, pretty_name=None):
        if self.settings['client']['pretty_name'] is None:
            while pretty_name is None:
                pretty_name = input('Enter Full Name for client: ').strip()
                self.slug = pretty_name
                if self.client_dir_exists(self.slug) or pretty_name == '':
                    pretty_name = None

            self.settings['client']['pretty_name'] = pretty_name
        else:
            self.slug = self.settings['client']['pretty_name']
            if self.client_dir_exists(self.slug):
                exit(1)

        os.chdir(self._config.easy_rsa_dir)
        run('./build-key ' + self.slug + ' 1> /dev/null', shell=True)

        self.client_dir = self.slug
        self.create_pretty_name_file()
        self.move_client_files(self.slug)
        self.copy_ca_file()
        self.copy_ta_file()

        os.chdir(self.settings['client']['client_dir'])

        self.create_client_config_files()
