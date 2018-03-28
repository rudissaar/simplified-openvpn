#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Management interface for OpenVPN Community Edition."""

import os
import zipfile
from shutil import copyfile
from subprocess import run
import pystache
from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper
from simplified_openvpn_config import SimplifiedOpenvpnConfig
from simplified_openvpn_data import SimplifiedOpenvpnData

class SimplifiedOpenvpn:
    """Main class that takes care of managing OpenVPN on your server."""

    def __init__(self):
        """Loads config if possible, else asks you to generate config."""
        self._config = SimplifiedOpenvpnConfig()
        self.load_env()

    def load_env(self):
        """Exports environment variables from vars file."""
        vars_file_path = self._config.easy_rsa_dir + 'vars'
        if not os.path.isfile(vars_file_path):
            print("> Can't find vars file from EASY RSA directory, exiting.")
            exit(1)

        with open(vars_file_path, 'r') as vars_file:
            easy_rsa = self._config.easy_rsa_dir.rstrip('/')

            for line in vars_file.readlines():
                line = line.strip()
                if line.startswith('#'):
                    continue

                if line.startswith('export'):
                    line = line.strip('export').strip()
                    key, value = line.split('=')
                    value = value.strip('"')

                    if value.startswith('`') and value.endswith('`'):
                        value = value.strip('`')
                    if key == 'EASY_RSA':
                        value = easy_rsa
                    if key == 'KEY_CONFIG':
                        value = easy_rsa + '/openssl.cnf'
                    value = value.replace('$EASY_RSA', easy_rsa)

                    # Assing new enviorment variable.
                    os.environ[key] = value

    def client_exists(self, verbose=True):
        """Checks if client with generated slug already exists."""
        if os.path.isdir(self._config.clients_dir + self._config.slug):
            if verbose:
                print('> Client with this name already exists.')
            return True
        return False

    def create_pretty_name_file(self):
        """Creates file that contains origianl input for client name."""
        if self._config.client_dir and self._config.pretty_name:
            with open(self._config.client_dir + 'pretty-name.txt', 'w') as pretty_name_file:
                pretty_name_file.write(self._config.pretty_name + "\n")
                return True
        return False

    def copy_client_files(self):
        """Copies client's keys to client's directory."""
        client_files = [self._config.slug + '.crt', self._config.slug + '.key']
        for client_file in client_files:
            source = self._config.easy_rsa_dir + 'keys/' + client_file
            destination = self._config.client_dir + client_file
            copyfile(source, destination)

        # Remove Private Key from keys directory to make things a little bit more secure.
        os.remove(self._config.easy_rsa_dir + 'keys/' + self._config.slug + '.key')

        # Remove CSR, we don't need it anymore.
        os.remove(self._config.easy_rsa_dir + 'keys/' + self._config.slug + '.csr')

    def copy_ca_file(self):
        """Copies certificate authority key to client's directory."""
        source = self._config.easy_rsa_dir + 'keys/ca.crt'
        destination = self._config.client_dir + 'ca.crt'
        copyfile(source, destination)

    def copy_ta_file(self):
        """Copies TLS Auth key to client's directory."""
        source = self._config.server_dir + 'ta.key'
        destination = self._config.client_dir + 'ta.key'
        copyfile(source, destination)

    def create_config(self):
        """Creates up basic config that can be changed based on flavour."""
        config = dict()
        config['protocol'] = self._config.protocol
        config['hostname'] = self._config.hostname
        config['ipv4'] = self._config.ipv4
        config['port'] = self._config.port
        config['slug'] = self._config.slug
        config['inline'] = False
        return config

    def write_config(self, options, flavour=''):
        """Writes a single config file/archive for client to the disk."""
        template = self._config.server_dir + 'client.mustache'
        if not os.path.isfile(template):
            print("> Template for client's config is missing, exiting.")
            exit(1)

        renderer = pystache.Renderer()
        client_dir = self._config.client_dir
        slug = self._config.slug

        # Creates up name for config file.
        config_path = client_dir + self._config.hostname
        if flavour != '':
            config_path += '-' + flavour
        config_path += '.ovpn'

        with open(config_path, 'w') as config_file:
            config_file.write(renderer.render_path(template, options))

        if not options['inline']:
            with zipfile.ZipFile(config_path + '.zip', 'w') as config_zip:
                config_zip.write(config_path)
                config_zip.write(client_dir + 'ca.crt', 'ca.crt')
                config_zip.write(client_dir + slug + '.crt', slug + '.crt')
                config_zip.write(client_dir + slug + '.key', slug + '.key')
                config_zip.write(client_dir + 'ta.key', 'ta.key')

            # Remove config file that you just zipped but keep certificates for others.
            os.remove(config_path)

    def generate_config_files(self, verbose=True):
        """Generates different flavours of config files."""
        ca_path = self._config.client_dir + 'ca.crt'
        cert_path = self._config.client_dir + self._config.slug + '.crt'
        key_path = self._config.client_dir + self._config.slug + '.key'
        ta_path = self._config.client_dir + 'ta.key'
        options = self.create_config()

        # Plain Windows flavour.
        self.write_config(options)

        # Plain Debian flavour.
        options['deb'] = True
        self.write_config(options, 'deb')
        options['deb'] = False

        # Plain RedHat flavour.
        options['rhel'] = True
        self.write_config(options, 'rhel')
        options['rhel'] = False

        # Inline Windows flavour.
        options['inline'] = True
        options['ca'] = _helper.read_file_as_value(ca_path)
        options['cert'] = _helper.read_file_as_value(cert_path)
        options['key'] = _helper.read_file_as_value(key_path)
        options['ta'] = _helper.read_file_as_value(ta_path)
        self.write_config(options, 'inline')

        # Inline Debian flavour.
        options['deb'] = True
        self.write_config(options, 'inline-deb')
        options['deb'] = False

        # Inline RedHat flavour.
        options['rhel'] = True
        self.write_config(options, 'inline-rhel')
        options['rhel'] = False

        # Clean up.
        self.cleanup_client_certificates()

        if verbose:
            print('> Client "' + self._config.slug + '" was successfully created.')

    def insert_share_hash(self, verbose=True):
        """Inserts client's data to database."""
        sovpn_data = SimplifiedOpenvpnData()
        sovpn_data.insert_share_hash(self._config.slug, self._config.share_hash)
        if verbose:
            print('> Share Hash: ' + self._config.share_hash)

    def rotate_share_hashes(self):
        """Generates share hashes for clients who can be found in database."""
        sovpn_data = SimplifiedOpenvpnData()
        slugs = sovpn_data.get_all_client_slugs()
        for slug in slugs:
            share_hash = _helper.generate_share_hash(slug, self._config.sovpn_share_salt)
            sovpn_data.rotate_share_hash(slug, share_hash)

    def cleanup_client_certificates(self):
        """Cleans up client's certificates as they are no longer needed."""
        cert_files = [self._config.slug + '.crt', self._config.slug + '.key', 'ca.crt', 'ta.key']
        for cert_file in cert_files:
            os.remove(self._config.client_dir + cert_file)

    def create_client(self, pretty_name=None):
        """Entry point for client creation process."""
        if self._config.pretty_name is None:
            while pretty_name is None:
                pretty_name = input('> Enter Full Name for client: ').strip()
                self._config.slug = pretty_name
                if self.client_exists(self._config.slug) or pretty_name == '':
                    pretty_name = None

            self._config.pretty_name = pretty_name
        else:
            self._config.slug = self._config.pretty_name
            self.client_exists(True)

        # Key generation.
        cmd = './build-key ' + self._config.slug + ' 1> /dev/null'
        run(cmd, shell=True, cwd=self._config.easy_rsa_dir)

        # Config generation.
        self._config.client_dir = self._config.slug
        self.create_pretty_name_file()
        self.copy_client_files()
        self.copy_ca_file()
        self.copy_ta_file()
        self.generate_config_files()
        self.insert_share_hash()
