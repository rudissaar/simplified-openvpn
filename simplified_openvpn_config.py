#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=R0904

"""file that contains SimplifiedOpenvpnConfig class."""

import os
import json

class SimplifiedOpenvpnConfig:
    """Class that contains shareable configuration."""
    settings = dict()
    settings['server'] = dict()
    settings['client'] = dict()

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
