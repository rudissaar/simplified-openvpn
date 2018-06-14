#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File that contains SimplifiedOpenvpnSuggest class."""

import os
import json
import random
import string
from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper

class SimplifiedOpenvpnSuggest:
    """Class that contains methods that will give you suggestions."""
    @staticmethod
    def get_value_from_sample(key, sample_path=None):
        """Get suggestion from sample config."""
        if sample_path is None:
            sample_path = os.path.dirname(os.path.realpath(__file__)) + '/sovpn.json'

        sample = _helper.read_file_as_value(sample_path)
        defaults = json.loads(sample)
        if key in defaults['server']:
            return defaults['server'][key]
        return None

    @staticmethod
    def server_dir(sample_path=None):
        # pylint: disable=E0602
        """Getting suggestion for server_dir."""
        suggestion = __class__.get_value_from_sample(_helper.current_method(), sample_path)
        return suggestion

    @staticmethod
    def easy_rsa_ver(sample_path=None):
        # pylint: disable=E0602
        """Getting suggestion for easy_rsa_ver."""
        suggestion = __class__.get_value_from_sample(_helper.current_method(), sample_path)
        return suggestion

    @staticmethod
    def clients_dir(sample_path=None):
        # pylint: disable=E0602
        """Getting suggestion for clients_dir."""
        suggestion = __class__.get_value_from_sample(_helper.current_method(), sample_path)
        if suggestion is None:
            suggestion = _helper.sanitize_path(os.path.expanduser('~')) + 'openvpn-clients'
        return suggestion

    @staticmethod
    def hostname(sample_path=None):
        # pylint: disable=E0602
        """Returns suggestion for hostname."""
        suggestion = __class__.get_value_from_sample(_helper.current_method(), sample_path)
        if suggestion is None:
            suggestion = _helper.fetch_hostname_by_system()
        if suggestion is None:
            suggestion = _helper.fetch_hostname_by_reverse_dns()
        return suggestion

    @staticmethod
    def protocol(sample_path=None):
        # pylint: disable=E0602
        """Getting suggestion for protocol."""
        suggestion = __class__.get_value_from_sample(_helper.current_method(), sample_path)
        return suggestion

    @staticmethod
    def port(sample_path=None):
        # pylint: disable=E0602
        """Getting suggestion for port."""
        suggestion = __class__.get_value_from_sample(_helper.current_method(), sample_path)
        return suggestion

    @staticmethod
    def sovpn_share_salt(sample_path=None):
        # pylint: disable=E0602
        """Getting suggestion for sovpn_share_salt."""
        suggestion = __class__.get_value_from_sample(_helper.current_method(), sample_path)
        if suggestion is None:
            chars = string.ascii_letters + string.digits
            length = random.randint(10, 16)
            suggestion = ''.join(random.choice(chars) for _ in range(length))
        return suggestion

    @staticmethod
    def sovpn_share_address(sample_path=None):
        # pylint: disable=E0602
        """Getting suggestion for sovpn_share_address."""
        suggestion = __class__.get_value_from_sample(_helper.current_method(), sample_path)
        return suggestion

    @staticmethod
    def sovpn_share_port(sample_path=None):
        # pylint: disable=E0602
        """Getting suggestion for sovpn_share_port."""
        suggestion = __class__.get_value_from_sample(_helper.current_method(), sample_path)
        return suggestion
