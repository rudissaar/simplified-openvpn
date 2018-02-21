#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File that contains SimplifiedOpenvpnConfig class."""

import os
import json
from shutil import copyfile
from slugify import slugify
from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper
from simplified_openvpn_suggest import SimplifiedOpenvpnSuggest as _suggest

class SimplifiedOpenvpnConfig:
    # pylint: disable=R0902
    # pylint: disable=R0904
    """Class that contains shareable configuration."""
    settings = dict()
    settings['server'] = dict()
    settings['client'] = dict()

    settings['server']['server_dir'] = None
    settings['server']['easy_rsa_dir'] = None
    settings['server']['clients_dir'] = None
    settings['server']['hostname'] = None
    settings['server']['ipv4'] = None
    settings['server']['protocol'] = None
    settings['server']['port'] = None
    settings['server']['sovpn_share_salt'] = None
    settings['server']['sovpn_share_port'] = None
    settings['server']['sovpn_config_file'] = None

    settings['client']['pretty_name'] = None
    settings['client']['slug'] = None
    settings['client']['share_hash'] = None
    settings['client']['client_dir'] = None

    def __init__(self):
        """Loads config if possible, else asks you to generate config."""
        self.container = _helper.sanitize_path(os.path.dirname(os.path.realpath(__file__)))
        self.loaded = False

        if self.needs_setup():
            self.setup()
        else:
            self.load()

    @staticmethod
    def needs_setup():
        """Check if the script needs to run initial setup."""
        container = _helper.sanitize_path(os.path.dirname(os.path.realpath(__file__)))
        sovpn_config_pointer = container + 'sovpn_config_pointer.txt'
        if not os.path.isfile(sovpn_config_pointer):
            return True
        sovpn_config_file = _helper.read_file_as_value(sovpn_config_pointer)
        if os.path.isfile(sovpn_config_file):
            return False
        return True

    def setup(self):
        # pylint: disable=R0912
        # pylint: disable=R0914
        # pylint: disable=R0915
        """Set up settings for Simplified OpenVPN on current system."""
        config = dict()
        config['server'] = dict()

        # Ask value for server_dir property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('server_dir', suggestion_source)

        while self.server_dir is None:
            prompt = '> Enter location of OpenVPN server directory on your server: '
            if suggestion:
                prompt += '[' + suggestion + '] '
            server_dir = input(prompt)
            if server_dir.strip() == '':
                server_dir = suggestion
            self.server_dir = server_dir

        config['server']['server_dir'] = self.server_dir

        # Ask value for easy_rsa_dir property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('easy_rsa_dir', suggestion_source)

        while self.easy_rsa_dir is None:
            prompt = '> Enter location of Easy RSA directory on your server: '
            if suggestion:
                prompt += '[' + suggestion + '] '
            easy_rsa_dir = input(prompt)
            if easy_rsa_dir.strip() == '':
                easy_rsa_dir = suggestion
            self.easy_rsa_dir = easy_rsa_dir

        config['server']['easy_rsa_dir'] = self.easy_rsa_dir

        # Ask value for clients_dir property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('clients_dir', suggestion_source)

        while self.clients_dir is None:
            prompt = "> Enter location for Client's directory on your server: "
            if suggestion:
                prompt += '[' + suggestion + '] '
            clients_dir = input(prompt)
            if clients_dir.strip() == '':
                clients_dir = suggestion
            self.clients_dir = clients_dir

        config['server']['clients_dir'] = self.clients_dir

        # Ask value for hostname property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('hostname', suggestion_source)

        while self.hostname is None:
            prompt = '> Enter hostname of your server: '
            if suggestion:
                prompt += '[' + suggestion + '] '
            hostname = input(prompt)
            if hostname.strip() == '':
                hostname = suggestion
            self.hostname = hostname

        config['server']['hostname'] = self.hostname

        # Ask value for protocol property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('protocol', suggestion_source)

        while self.protocol is None:
            prompt = '> Select protocol that you would like to use: (TCP|UDP) '
            if suggestion:
                prompt += '[' + suggestion.upper() + '] '
            protocol = input(prompt)
            if protocol.strip() == '':
                protocol = suggestion
            self.protocol = protocol

        config['server']['protocol'] = self.protocol

        # Ask value for port property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('port', suggestion_source)

        while self.port is None:
            prompt = '> Select port that you are using for for your server: '
            if suggestion:
                prompt += '[' + str(suggestion) + '] '
            port = input(prompt)
            if port.strip() == '':
                port = suggestion
            self.port = port

        config['server']['port'] = self.port

        # Ask value for sovpn_share_salt property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('sovpn_share_salt', suggestion_source)

        while self.sovpn_share_salt is None:
            prompt = "> Enter random Salt for sharing script: "
            if suggestion:
                prompt += '[' + suggestion + '] '
            sovpn_share_salt = input(prompt)
            if sovpn_share_salt.strip() == '':
                sovpn_share_salt = suggestion
            self.sovpn_share_salt = sovpn_share_salt

        config['server']['sovpn_share_salt'] = self.sovpn_share_salt

        # Ask value for sovpn_share_port property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('sovpn_share_port', suggestion_source)

        while self.sovpn_share_port is None:
            prompt = "> Enter port for sharing script: "
            if suggestion:
                prompt += '[' + str(suggestion) + '] '
            sovpn_share_port = input(prompt)
            if sovpn_share_port.strip() == '':
                sovpn_share_port = suggestion
            self.sovpn_share_port = sovpn_share_port

        config['server']['sovpn_share_port'] = self.sovpn_share_port

        # Ask value for sovpn_config_file property.
        suggestion = self.server_dir + 'sovpn.json'

        while self.sovpn_config_file is None:
            prompt = "> Enter location for Simplified OpenVPN's config file: "
            if suggestion:
                prompt += '[' + suggestion + '] '
            sovpn_config_file = input(prompt)
            if sovpn_config_file.strip() == '':
                sovpn_config_file = suggestion
            self.sovpn_config_file = sovpn_config_file

        # Write sovpn's config file path to pointer file.
        with open(self.sovpn_config_pointer, 'w') as config_path_file:
            config_path_file.write(self.sovpn_config_file + "\n")

        # Write config values to file.
        with open(self.sovpn_config_file, 'w') as config_file:
            config_file.write(json.dumps(config) + "\n")

        # Copy client's template to server's directory.
        client_template_path = self.container + 'templates/client.mustache'
        copyfile(client_template_path, self.server_dir + 'client.mustache')

    def wipe(self):
        """Resets properies to None."""
        properties = list(self.settings['server'].keys())
        properties.remove('sovpn_config_file')

        for current_property in properties:
            if current_property in dir(self):
                setattr(self, current_property, None)

    def load(self):
        """Populate properties with values if config file exists."""
        if self.sovpn_config_file is None:
            self.sovpn_config_file = _helper.read_file_as_value(self.sovpn_config_pointer)

        if os.path.isfile(self.sovpn_config_file):
            with open(self.sovpn_config_file) as config_file:
                data = json.load(config_file)

            for pool in data:
                for key, value in data[pool].items():
                    if key in dir(self):
                        setattr(self, key, value)
        self.loaded = True

    @staticmethod
    def get_suggestion(key, sample_path=None):
        """Gets suggestions from _suggest class if possible."""
        method = getattr(_suggest, key, None)
        if method is not None:
            return method(sample_path)
        return None

    def destroy(self):
        """Removes SOVPN's configuration and data from your system."""
        files_to_remove = [
            self.sovpn_config_file,
            self.sovpn_config_pointer,
            self.container + 'sovpn.sqlite'
        ]

        for file_to_remove in files_to_remove:
            if os.path.isfile(file_to_remove):
                os.remove(file_to_remove)

        print("> Removed SOVPN's configuration and data from your system.")

    @property
    def sovpn_config_pointer(self):
        """Returns path to SOVPN's config file."""
        return self.container + 'sovpn_config_pointer.txt'

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
        if value is None:
            self.settings['server']['server_dir'] = None
            return

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
        if value is None:
            self.settings['server']['easy_rsa_dir'] = None
            return

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
    def clients_dir(self, value):
        """Assigns new value to clients_dir property if possible."""
        if value is None:
            self.settings['server']['clients_dir'] = None
            return

        if not os.path.isdir(value):
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
    def hostname(self):
        """Returns value of hostname property."""
        hostname = self.settings['server']['hostname']
        if hostname is None:
            hostname = self.fetch_hostname_by_config_file()
        return hostname

    @hostname.setter
    def hostname(self, value):
        """Assigns new value to hostname property."""
        if value is None:
            self.settings['server']['hostname'] = None
            return

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

    @ipv4.setter
    def ipv4(self, value):
        """Assigns new value to ipv4 property."""
        if value is None:
            self.settings['server']['ipv4'] = None
            return

        self.settings['server']['ipv4'] = value

    @property
    def port(self):
        """Returns value of port property."""
        return self.settings['server']['port']

    @port.setter
    def port(self, value):
        """Assigns new value to port property."""
        if value is None:
            self.settings['server']['port'] = None
            return

        self.settings['server']['port'] = int(value)

    @property
    def protocol(self):
        """Returns value of protocol property."""
        return self.settings['server']['protocol']

    @protocol.setter
    def protocol(self, value):
        """Assigns new value to protcol property."""
        if value is None:
            self.settings['server']['protocol'] = None
            return

        protocols = ['udp', 'tcp']

        if isinstance(value, str) and value.lower() in protocols:
            self.settings['server']['protocol'] = value.lower()

    @property
    def sovpn_share_salt(self):
        "Returns salt that gets used in sharing."
        return self.settings['server']['sovpn_share_salt']

    @sovpn_share_salt.setter
    def sovpn_share_salt(self, value):
        """Assigns new value to sovpn_share_salt property."""
        self.settings['server']['sovpn_share_salt'] = value

    @property
    def sovpn_share_port(self):
        """Returns port that gets used in sharing."""
        return self.settings['server']['sovpn_share_port']

    @sovpn_share_port.setter
    def sovpn_share_port(self, value):
        """Assigns new value to sovpn_share_port property."""
        if value is None:
            self.settings['server']['sovpn_share_port'] = None
            return

        self.settings['server']['sovpn_share_port'] = value

    @property
    def pretty_name(self):
        """Returns value of pretty_name property."""
        return self.settings['client']['pretty_name']

    @pretty_name.setter
    def pretty_name(self, value):
        """Assigns new value to pretty_name property."""
        self.settings['client']['pretty_name'] = value.strip()

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
    def share_hash(self):
        """Returns generated value of sovpn_hash."""
        share_hash = _helper.generate_share_hash(self.slug, self.sovpn_share_salt)
        return share_hash

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
