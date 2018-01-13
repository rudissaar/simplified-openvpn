#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=R0904
# pylint: disable=R0912

"""file that contains SimplifiedOpenvpnConfig class."""

import os
import json
from slugify import slugify
from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper
from simplified_openvpn_suggest import SimplifiedOpenvpnSuggest as _suggest

class SimplifiedOpenvpnConfig:
    """Class that contains shareable configuration."""
    settings = dict()
    settings['server'] = dict()
    settings['client'] = dict()

    settings['server']['server_dir'] = None
    settings['server']['easy_rsa_dir'] = '/etc/openvpn/easy-rsa/'
    settings['server']['clients_dir'] = '/root/openvpn-clients/'
    settings['server']['sovpn_share_salt'] = None
    settings['server']['hostname'] = None
    settings['server']['ipv4'] = None
    settings['server']['protocol'] = None
    settings['server']['port'] = None
    settings['server']['sovpn_config_file'] = None

    settings['client']['slug'] = None
    settings['client']['pretty_name'] = None
    settings['client']['client_dir'] = None

    def __init__(self):
        """Loads config if possible, else asks you to generate config."""
        if self.needs_setup():
            self.config_setup()
        else:
            self.load_config()

    @staticmethod
    def needs_setup():
        """Check if the script needs to run initial setup."""
        file_path = os.path.dirname(os.path.realpath(__file__)) + '/sovpn-config-path.txt'
        if not os.path.isfile(file_path):
            return True
        sovpn_config_file = _helper.read_file_as_value(file_path)
        if os.path.isfile(sovpn_config_file):
            return False
        return True

    def config_setup(self):
        """Set up settings for Simplified OpenVPN on current system."""
        config = dict()
        config['server'] = dict()

        suggestion = self.get_suggestion('server_dir')
        while self.server_dir is None:
            prompt = '> Enter location of OpenVPN server directory on your server: '
            if suggestion:
                prompt += '[' + suggestion + '] '
            server_dir = input(prompt)
            if server_dir.strip() == '':
                server_dir = suggestion
            self.server_dir = server_dir

        config['server']['server_dir'] = self.server_dir

        suggestion = self.get_suggestion('hostname')
        while self.hostname is None:
            prompt = '> Enter hostname of your server: '
            if suggestion:
                prompt += '[' + suggestion + '] '
            hostname = input(prompt)
            if hostname.strip() == '':
                hostname = suggestion
            self.hostname = hostname

        config['server']['hostname'] = self.hostname

        suggestion = self.get_suggestion('protocol')
        while self.protocol is None:
            prompt = '> Select protocol that you would like to use: (TCP|UDP) '
            if suggestion:
                prompt += '[' + suggestion.upper() + '] '
            protocol = input(prompt)
            if protocol.strip() == '':
                protocol = suggestion
            self.protocol = protocol

        config['server']['protocol'] = self.protocol

        suggestion = self.get_suggestion('port')
        while self.port is None:
            prompt = '> Select port that you are using for for your server: '
            if suggestion:
                prompt += '[' + str(suggestion) + '] '
            port = input(prompt)
            if port.strip() == '':
                port = suggestion
            self.port = port

        config['server']['port'] = self.port

        suggestion = self.server_dir + 'sovpn.json'
        while self.sovpn_config_file is None:
            prompt = "> Enter location for Simplified OpenVPN's config file: "
            if suggestion:
                prompt += '[' + suggestion + '] '
            sovpn_config_file = input(prompt)
            if sovpn_config_file.strip() == '':
                sovpn_config_file = suggestion
            self.sovpn_config_file = sovpn_config_file

        print(config)
        exit()

    def load_config(self):
        """Populate properties with values if config file exists."""
        if os.path.isfile(self.sovpn_config_file):
            with open(self.sovpn_config_file) as config_file:
                data = json.load(config_file)

            for pool in data:
                for key, value in data[pool].items():
                    if key in dir(self):
                        setattr(self, key, value)

    @staticmethod
    def get_suggestion(key):
        """Gets suggestions from _suggest class if possible."""
        method = getattr(_suggest, key, None)
        if method is not None:
            return method()
        return None

    @property
    def sovpn_config_file(self):
        """Returns absolute path of sovpn's config file."""
        return self.settings['server']['sovpn_config_file']

    @sovpn_config_file.setter
    def sovpn_config_file(self, value):
        """Assigns new value to sovpn_config_file property."""
        self.settings['server']['sovpn_config_file'] = value

    @property
    def server_dir(self):
        """Returns directory of OpenVPN server."""
        return self.settings['server']['server_dir']

    @server_dir.setter
    def server_dir(self, value):
        """Assings new value to server_dir property if possible."""
        status = os.path.isdir(value)

        if not status:
            print("Value that you specified as Server's directory is invalid: (" + value + ")")
            print('Make sure that the value you gave meets following requirements:')
            print('> Does the directory really exist in your filesystem?')
            print('> The specified directory has write and execute permissions.')
            exit(1)

        self.settings['server']['server_dir'] = _helper.sanitize_path(value)

    @property
    def easy_rsa_dir(self):
        """Returns directory of EasyRSA utils."""
        return self.settings['server']['easy_rsa_dir']

    @easy_rsa_dir.setter
    def easy_rsa_dir(self, value):
        """Assings new value to easy_rsa_dir property if possible."""
        status = os.path.isdir(value)

        if not status:
            print("Value that you specified as directory for Easy RSA is invalid: (" + value + ")")
            print('Make sure that the value you gave meets following requirements:')
            print('> Does the directory really exist in your filesystem?')
            print('> The specified directory has write and execute permissions.')
            exit(1)

        self.settings['server']['easy_rsa_dir'] = _helper.sanitize_path(value)

    @property
    def clients_dir(self):
        """Returns path of directory that contains files for all users."""
        return self.settings['server']['clients_dir']

    @clients_dir.setter
    def clients_dir(self, value, create=False):
        """Assigns new value to clients_dir property if possible."""
        if create:
            _helper.create_directory(value)

        if not os.path.isdir(value):
            if create:
                _helper.create_directory(value)

        status = os.path.isdir(value)

        if not status:
            print("Value that you specified as directory for clients is invalid: (" + value + ")")
            print('Make sure that the value you gave meets following requirements:')
            print('> Does the directory really exist in your filesystem?')
            print('> The specified directory has write and execute permissions.')
            exit(1)

        self.settings['server']['clients_dir'] = _helper.sanitize_path(value)

    @property
    def sovpn_share_salt(self):
        "Returns salt that is being used in sovpn_share script."
        return self.settings['server']['sovpn_share_salt']

    @sovpn_share_salt.setter
    def sovpn_share_salt(self, value):
        """Assigns new value to sovpn_share_salt property."""
        self.settings['server']['sovpn_share_salt'] = value

    @property
    def hostname(self):
        """Returns value of hostname property."""
        hostname = self.settings['server']['hostname']
        if hostname is None:
            hostname = self.fetch_hostname_by_config_file()
        return hostname

    @hostname.setter
    def hostname(self, value):
        """Assigns new value to hostname property."""
        if not _helper.is_valid_hostname(value):
            print('Value that you specified as Hostname is invalid: (' + value + ')')
        else:
            self.settings['server']['hostname'] = value

    def fetch_hostname_by_config_file(self):
        """Tries to fetch hostname from sovpn config file."""
        if self.sovpn_config_file and os.path.isfile(self.sovpn_config_file):
            with open(self.sovpn_config_file) as config_file:
                data = json.load(config_file)
                hostname = data['server']['hostname']

            if _helper.is_valid_hostname(hostname):
                return hostname
        return None

    @property
    def ipv4(self):
        """Returns value of IPv4 property."""
        ipv4 = self.settings['server']['ipv4']
        if ipv4 is None:
            value = _helper.fetch_external_ipv4()
            if _helper.is_valid_ipv4(value):
                ipv4 = value
        return ipv4

    @property
    def port(self):
        """Returns value of port property."""
        return self.settings['server']['port']

    @port.setter
    def port(self, value):
        """Assigns new value to port property."""
        self.settings['server']['port'] = int(value)

    @property
    def protocol(self):
        """Returns value of protocol property."""
        return self.settings['server']['protocol']

    @protocol.setter
    def protocol(self, value):
        """Assigns new value to protcol property."""
        protocols = ['udp', 'tcp']

        if isinstance(value, str) and value.lower() in protocols:
            self.settings['server']['protocol'] = value.lower()

    @property
    def slug(self):
        """Returns value of slug property."""
        return self.settings['client']['slug']

    @slug.setter
    def slug(self, value):
        """Assigns new value to slug property."""
        slug = slugify(value)
        self.settings['client']['slug'] = slug

    @property
    def pretty_name(self):
        """Returns value of pretty_name property."""
        return self.settings['client']['pretty_name']

    @pretty_name.setter
    def pretty_name(self, value):
        """Assigns new value to pretty_name property."""
        self.settings['client']['pretty_name'] = value.strip()

    @property
    def client_dir(self):
        """Returns value of client_dir property."""
        return self.settings['client']['client_dir']

    @client_dir.setter
    def client_dir(self, create=True):
        """Assigns new value to client_dir property and creates directory for it if needed."""
        value = self.clients_dir + self.slug
        if create:
            _helper.create_directory(value)
        self.settings['client']['client_dir'] = _helper.sanitize_path(value)
