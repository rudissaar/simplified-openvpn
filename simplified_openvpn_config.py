#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=R0904

"""file that contains SimplifiedOpenvpnConfig class."""

import os
import json
from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper

class SimplifiedOpenvpnConfig:
    """Class that contains shareable configuration."""
    settings = dict()
    settings['server'] = dict()
    settings['client'] = dict()

    settings['server']['server_dir'] = '/etc/openvpn/'
    settings['server']['easy_rsa_dir'] = '/etc/openvpn/easy-rsa/'
    settings['server']['clients_dir'] = '/root/openvpn-clients/'
    settings['server']['sovpn_config_file'] = '/etc/openvpn/sovpn.json'
    settings['server']['sovpn_share_salt'] = None

    def __init__(self):
        """Loads config if possible, else asks you to generate config."""
        self.load_config()
        #if self.needs_setup():
            #self.config_setup()
        #else:
            #self.load_config()

    def needs_setup(self):
        """Check if the script needs to run initial setup."""
        if os.path.isfile(self.sovpn_config_file):
            return False
        return True

    def config_setup(self):
        """Set up settings for Simplified OpenVPN on current system."""
        pass

    def load_config(self):
        """Populate properties with values if config file exists."""
        if os.path.isfile(self.sovpn_config_file):
            with open(self.sovpn_config_file) as config_file:
                data = json.load(config_file)

            for pool in data:
                for key, value in data[pool].items():
                    if key in dir(self):
                        setattr(self, key, value)

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
    def sovpn_config_file(self):
        """Returns absolute path of sovpn's config file."""
        return self.settings['server']['sovpn_config_file']

    @sovpn_config_file.setter
    def sovpn_config_file(self, value):
        """Assigns new valie to sovpn_config_file property."""
        self.settings['server']['sovpn_config_file'] = value

    @property
    def sovpn_share_salt(self):
        "Returns salt that is being used in sovpn_share script."
        return self.settings['server']['sovpn_share_salt']

    @sovpn_share_salt.setter
    def sovpn_share_salt(self, value):
        """Assigns new valie to sovpn_share_salt property."""
        self.settings['server']['sovpn_share_salt'] = value
