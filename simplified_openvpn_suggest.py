#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=R0904

"""File that contains SimplifiedOpenvpnSuggest class."""

from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper

class SimplifiedOpenvpnSuggest:
    """Class that contains methods that will give you suggestions."""
    @staticmethod
    def hostname():
        """Returns suggestion for hostname"""
        suggestion = _helper.fetch_hostname_by_system()
        if suggestion is None:
            suggestion = _helper.fetch_hostname_by_reverse_dns()
        return suggestion
