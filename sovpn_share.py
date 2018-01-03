#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pystache
import sqlite3
from flask import Flask
from flask import send_file
from simplified_openvpn_helper import SimplifiedOpenvpnHelper as _helper
from simplified_openvpn_config import SimplifiedOpenvpnConfig

_config = SimplifiedOpenvpnConfig()

app = Flask(__name__)
path = _config.clients_dir

@app.route('/<slug>')
def client_page(slug):
    data = dict()
    data['client_name'] = slug
    data['list_items'] = ''

    files = os.listdir(path + slug)
    for config_file in files:
        if config_file == 'pretty-name.txt':
            data['client_name'] = _helper.read_file_as_value(path + slug + '/' + config_file)
            continue

        data['list_items'] += '<li><a href="' + slug + '/' + config_file +  '">' + config_file + '</a></li>'

    renderer = pystache.Renderer()
    return renderer.render_path('./templates/share.mustache', data)

@app.route('/<slug>/<config_file>')
def download_config(slug, config_file):
    return send_file(path + slug + '/' + config_file)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1195)
