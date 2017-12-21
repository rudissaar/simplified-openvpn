#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pystache
from flask import Flask
from flask import send_file

app = Flask(__name__)
path = '/root/openvpn-clients/'

@app.route('/<slug>')
def client_page(slug):
    data = dict()
    data['slug'] = slug
    data['list_items'] = ''

    files = os.listdir(path + slug)
    for config_file in files:
        if config_file == 'pretty-name.txt':
            continue

        data['list_items'] += '<li><a href="' + slug + '/' + config_file +  '">' + config_file + '</a></li>'

    renderer = pystache.Renderer()
    return renderer.render_path('./share.mustache', data)

@app.route('/<slug>/<config_file>')
def download_config(slug, config_file):
    return send_file(path + slug + '/' + config_file)

if __name__ == '__main__':
    app.run(port=1195)
