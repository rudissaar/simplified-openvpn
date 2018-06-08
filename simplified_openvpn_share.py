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
    def css_path(self):
        """Method that return path of CSS file that will be used for sharing page."""
        if self.override:
            path = self.override + 'share.css'
            if os.path.isfile(path):
                return path

        path = self.container + 'style/share.css'
        if os.path.isfile(path):
            return path

        return None

    @property
    def css(self):
        """Method that return CSS content for sharing page."""
        if self.css_path:
            return _helper.read_file_as_value(self.css_path)

        return None
