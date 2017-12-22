#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=R0904

import os

class SimplifiedOpenvpnHelper:
    @staticmethod
    def read_file_as_value(filename, verbose=False):
        '''Reads contents of the file and returns it.'''
        if not os.path.isfile(filename):
            if verbose:
                print("> File that you tried to read as value doesn't exist.")
            return None

        value = None
        with open(filename) as content:
            value = content.read().rstrip()
        return value
