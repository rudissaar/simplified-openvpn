#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File that contains SimplifiedOpenvpnConfig class."""

import os
import json
from shutil import copyfile
from slugify import slugify
from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper
from simplified_openvpn_suggest import SimplifiedOpenvpnSuggest as _suggest
from simplified_openvpn_prompt import SimplifiedOpenvpnPrompt as _prompt

class SimplifiedOpenvpnConfig:
    # pylint: disable=R0902
    # pylint: disable=R0904
    """Class that contains shareable configuration."""
    settings = dict()
    settings['server'] = dict()
    settings['client'] = dict()

    settings['server']['server_dir'] = None
    settings['server']['easy_rsa_dir'] = None
    settings['server']['easy_rsa_ver'] = None
    settings['server']['clients_dir'] = None
    settings['server']['hostname'] = None
    settings['server']['ipv4'] = None
    settings['server']['protocol'] = None
    settings['server']['port'] = None
    settings['server']['mgmt_address'] = None
    settings['server']['mgmt_port'] = None
    settings['server']['sovpn_share_salt'] = None
    settings['server']['sovpn_share_address'] = None
    settings['server']['sovpn_share_port'] = None
    settings['server']['sovpn_share_url'] = None
    settings['server']['sovpn_config_file'] = None
    settings['server']['needs_rotation'] = None

    settings['client']['pretty_name'] = None
    settings['client']['slug'] = None
    settings['client']['share_hash'] = None

    def __init__(self, run_setup=True):
        """Loads config if possible, else asks you to generate config."""
        self.container = _helper.sanitize_path(os.path.dirname(os.path.realpath(__file__)))
        self.override = self.container + 'local/'
        self.loaded = False
        self.needs_rotation = False

        if self.needs_setup():
            if run_setup:
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
        # pylint: disable=W0125
        """Set up settings for Simplified OpenVPN on current system."""
        config = dict()
        config['server'] = dict()

        # Ask value for server_dir property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('server_dir', suggestion_source)

        while self.server_dir is None:
            prompt = _prompt.get('server_dir', suggestion)
            server_dir = input(prompt)
            if server_dir.strip() == '':
                server_dir = suggestion
            self.server_dir = server_dir

        config['server']['server_dir'] = self.server_dir

        # Ask value for easy_rsa_dir property.
        suggestion = self.server_dir + 'easy-rsa'

        while self.easy_rsa_dir is None:
            prompt = _prompt.get('easy_rsa_dir', suggestion)
            easy_rsa_dir = input(prompt)
            if easy_rsa_dir.strip() == '':
                easy_rsa_dir = suggestion
            self.easy_rsa_dir = easy_rsa_dir

        config['server']['easy_rsa_dir'] = self.easy_rsa_dir

        # Ask value for easy_rsa_ver property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('easy_rsa_ver', suggestion_source)

        while self.easy_rsa_ver is None:
            prompt = _prompt.get('easy_rsa_ver', suggestion)
            easy_rsa_ver = input(prompt)
            if easy_rsa_ver.strip() == '':
                easy_rsa_ver = suggestion
            self.easy_rsa_ver = easy_rsa_ver

        config['server']['easy_rsa_ver'] = self.easy_rsa_ver

        # Ask value for clients_dir property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('clients_dir', suggestion_source)

        while self.clients_dir is None:
            prompt = _prompt.get('clients_dir', suggestion)
            clients_dir = input(prompt)
            if clients_dir.strip() == '':
                clients_dir = suggestion
            self.clients_dir = clients_dir

        config['server']['clients_dir'] = self.clients_dir

        # Ask value for hostname property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('hostname', suggestion_source)

        if not self.hostname and self.sovpn_share_url and not suggestion:
            suggestion = '-'

        while self.hostname is None:
            prompt = _prompt.get('hostname', suggestion)
            hostname = input(prompt).strip()
            if hostname == '' and suggestion and suggestion != '-':
                hostname = suggestion
            elif hostname == '-' or (hostname == '' and suggestion == '-'):
                # pylint: disable=R0204
                hostname = False
            self.hostname = hostname

        # If hostname is changes then in most cases we also want to change sharing URL.
        if suggestion != self.hostname and self.sovpn_share_url:
            self.sovpn_share_url = None

        config['server']['hostname'] = self.hostname

        # Ask value for port property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('port', suggestion_source)

        while self.port is None:
            prompt = _prompt.get('port', suggestion)
            port = input(prompt)
            if port.strip() == '':
                port = suggestion
            self.port = port

        config['server']['port'] = self.port

        # Ask value for protocol property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('protocol', suggestion_source)

        while self.protocol is None:
            prompt = _prompt.get('protocol', suggestion)
            protocol = input(prompt)
            if protocol.strip() == '':
                protocol = suggestion
            self.protocol = protocol

        config['server']['protocol'] = self.protocol

        # Ask value for sovpn_share_salt property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('sovpn_share_salt', suggestion_source)

        while self.sovpn_share_salt is None:
            prompt = _prompt.get('sovpn_share_salt', suggestion)
            sovpn_share_salt = input(prompt)
            if sovpn_share_salt.strip() == '':
                sovpn_share_salt = suggestion
            self.sovpn_share_salt = sovpn_share_salt

        config['server']['sovpn_share_salt'] = self.sovpn_share_salt

        # If you changed share salt, then you need to rotate hashes for everybody.
        if self.loaded and suggestion != self.sovpn_share_salt:
            self.needs_rotation = True

        # Ask value for sovpn_share_address property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('sovpn_share_address', suggestion_source)

        while self.sovpn_share_address is None:
            prompt = _prompt.get('sovpn_share_address', suggestion)
            sovpn_share_address = input(prompt)
            if sovpn_share_address.strip() == '':
                sovpn_share_address = suggestion
            self.sovpn_share_address = sovpn_share_address

        config['server']['sovpn_share_address'] = self.sovpn_share_address

        # Ask value for sovpn_share_port property.
        suggestion_source = self.sovpn_config_file if self.loaded else None
        suggestion = self.get_suggestion('sovpn_share_port', suggestion_source)

        while self.sovpn_share_port is None:
            prompt = _prompt.get('sovpn_share_port', suggestion)
            sovpn_share_port = input(prompt)
            if sovpn_share_port.strip() == '':
                sovpn_share_port = suggestion

            # Make sure server and sharing port are different.
            if self.protocol == 'tcp' and self.port == sovpn_share_port:
                print('> Port ' + str(sovpn_share_port) + '/TCP is already used by server.')
                sovpn_share_port = None
            self.sovpn_share_port = sovpn_share_port

        config['server']['sovpn_share_port'] = self.sovpn_share_port

        # Ask value for sovpn_share_url property.
        if self.hostname:
            if self.sovpn_share_url:
                suggestion = self.sovpn_share_url
                self.sovpn_share_url = None
            elif not self.hostname and self.hostname is False:
                suggestion = '-'
            else:
                if self.sovpn_share_port == 443:
                    suggestion = 'https://'
                else:
                    suggestion = 'http://'

                suggestion += self.hostname

                if self.sovpn_share_port != 443 and self.sovpn_share_port != 80:
                    suggestion += ':' + str(self.sovpn_share_port)

                suggestion += '/'

            while self.sovpn_share_url is None:
                prompt = _prompt.get('sovpn_share_url', suggestion)
                sovpn_share_url = input(prompt)
                if sovpn_share_url.strip() == '':
                    sovpn_share_url = suggestion
                self.sovpn_share_url = sovpn_share_url

            config['server']['sovpn_share_url'] = self.sovpn_share_url
        else:
            ipv4 = _helper.fetch_external_ipv4()
            if _helper.is_valid_ipv4(ipv4):
                self.sovpn_share_url = 'http://' + ipv4 + ':' + str(self.sovpn_share_port) + '/'
                config['server']['sovpn_share_url'] = self.sovpn_share_url

        # Ask value for sovpn_config_file property.
        suggestion = self.server_dir + 'sovpn.json'

        while self.sovpn_config_file is None:
            prompt = _prompt.get('sovpn_config_file', suggestion)
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
        copyfile(self.client_template_path, self.server_dir + 'client.mustache')

    def wipe(self):
        """Resets properies to None."""
        properties = list(self.settings['server'].keys())
        properties.remove('easy_rsa_dir')
        properties.remove('easy_rsa_ver')
        properties.remove('sovpn_share_url')
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
    def client_template_path(self):
        """Method that return path of client template file that will be copied to server_dir."""
        if self.override:
            path = self.override + 'client.mustache'
            if os.path.isfile(path):
                return path

        path = self.container + 'templates/client.mustache'
        if os.path.isfile(path):
            return path

        return None

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
        else:
            self.settings['server']['server_dir'] = _helper.sanitize_path(value)

    @property
    def easy_rsa_dir(self):
        """Returns directory of Easy RSA utils."""
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
        else:
            self.settings['server']['easy_rsa_dir'] = _helper.sanitize_path(value)

    @property
    def easy_rsa_ver(self):
        """Returns version of Easy RSA."""
        return self.settings['server']['easy_rsa_ver']

    @easy_rsa_ver.setter
    def easy_rsa_ver(self, value):
        """Assigns new value to easy_rsa_ver property."""
        version = int(value)

        if version in [2, 3]:
            self.settings['server']['easy_rsa_ver'] = version

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
        return hostname

    @hostname.setter
    def hostname(self, value):
        """Assigns new value to hostname property."""
        if value is None:
            self.settings['server']['hostname'] = None
            return
        elif value is False or value == '-':
            self.settings['server']['hostname'] = False
            return

        if not _helper.is_valid_hostname(value):
            print('Value that you specified as Hostname is invalid: (' + value + ')')
        else:
            self.settings['server']['hostname'] = value

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
    def mgmt_address(self):
        """Returns value of mgmt_address property."""
        return self.settings['server']['mgmt_address']

    @mgmt_address.setter
    def mgmt_address(self, value):
        """Assigns new value to mgmt_address property."""
        self.settings['server']['mgmt_address'] = value

    @property
    def mgmt_port(self):
        """Returns value of mgmt_port property."""
        return self.settings['server']['mgmt_port']

    @mgmt_port.setter
    def mgmt_port(self, value):
        """Assigns new value to mgmt_port property."""
        if value is None:
            self.settings['server']['mgmt_port'] = None
            return

        self.settings['server']['mgmt_port'] = int(value)

    @property
    def sovpn_share_salt(self):
        "Returns salt that gets used in sharing."
        return self.settings['server']['sovpn_share_salt']

    @sovpn_share_salt.setter
    def sovpn_share_salt(self, value):
        """Assigns new value to sovpn_share_salt property."""
        self.settings['server']['sovpn_share_salt'] = value

    @property
    def sovpn_share_address(self):
        """Retutns address that gets used in sharing."""
        return self.settings['server']['sovpn_share_address']

    @sovpn_share_address.setter
    def sovpn_share_address(self, value):
        """Assigns new value to sovpn_share_address property."""
        if value is None:
            self.settings['server']['sovpn_share_address'] = None
            return

        self.settings['server']['sovpn_share_address'] = value

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
    def sovpn_share_url(self):
        """Returns value of sovpn_share_property."""
        return self.settings['server']['sovpn_share_url']

    @sovpn_share_url.setter
    def sovpn_share_url(self, value):
        """Assings new value to sovpn_share_url property."""
        if value is None:
            self.settings['server']['sovpn_share_url'] = value
            return

        if not value.endswith('/'):
            value += '/'
        self.settings['server']['sovpn_share_url'] = value

    @property
    def pretty_name(self):
        """Returns value of pretty_name property."""
        return self.settings['client']['pretty_name']

    @pretty_name.setter
    def pretty_name(self, value):
        """Assigns new value to pretty_name property."""
        if value is not None:
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
