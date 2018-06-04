#!/usr/bin env python3
# -*- coding: utf-8 -*-

"""File that contains SimplifiedOpenvpnShare class."""

import os

from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper


class SimplifiedOpenvpnShare:
    """Class that contains methods that will get used by sharing functionality."""

    def __init__(self):
        """Initialises SimplifiedOpenvpnShare class."""
        self.container = _helper.sanitize_path(os.path.dirname(os.path.realpath(__file__)))
        self.override = self.container + 'local/'

        if not os.path.isdir(self.override):
            self.override = None

    @property
    def css(self):
        """Method that return CSS content for sharing page."""
        if self.override:
            override = self.override + 'share.css'
            if os.path.isfile(override):
                return _helper.read_file_as_value(override)

        style = self.container + 'style/share.css'
        if os.path.isfile(style):
            return _helper.read_file_as_value(style)
        else:
            return None
