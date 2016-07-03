#!/usr/bin/python -O
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, division

import os
import re
import json
import logging
import shutil
from os import path
import glob
import traceback

import requests
from bs4 import BeautifulSoup
try:
    import lxml
    get_soup = lambda c: BeautifulSoup(c, 'lxml')
except ImportError:
    get_soup = lambda c: BeautifulSoup(c, 'html.parser')

from jinja2 import FileSystemLoader, Environment

import renderers

CURDIR = path.dirname(path.realpath(__file__))
TPLDIR = path.join(CURDIR, 'templates')
ENV = Environment(loader=FileSystemLoader(TPLDIR))
# DISTROS = ['ubuntu', 'debian']
DISTROS = ['ubuntu']

def get_ubuntu_releases():
    url = 'https://wiki.ubuntu.com/Releases'
    ver_pat = re.compile(r'^Ubuntu (\d+\.\d+)')
    cache = dict()
    try:
        res = requests.get(url, timeout=4)
    except:
        return None
    d = dict(Current=[], Future=[], End_of_life=[])
    soup = get_soup(res.content)
    for k in d.keys():
        trs = soup.find(id=k).find_next_sibling('div').select('tr')[1:]
        for tr in trs:
            ps = tr.select('p')[:2]
            matched = ver_pat.search(ps[0].text)
            if matched is None:
                continue
            ver = matched.groups()[0]
            LTS = False
            if not cache.get(ver, None):
                if 'LTS' in ps[0].text:
                    LTS = True
                code = ps[1].text.split()[0].lower()
                cache[ver] = code
                d[k].append((ver, code, LTS))
        logging.debug('ubuntu %s: %s', k, d.get(k))
    return d

def main(tpldir):
    releases = dict()
    get = globals().get
    err = True
    with open('releases.json.new', 'w') as fout:
        for dist in DISTROS:
            f = get('get_{}_releases'.format(dist), None)
            # Not callable
            if not hasattr(f, '__code__'):
                logging.warn('Cannot get releases of `%s`', dist)
                continue
            releases[dist] = f()
            if releases[dist] is None:
                raise ValueError
        err = False
        json.dump(releases, fout, indent=4)

    if not err:
        shutil.copyfile('releases.json.new', 'releases.json')
    os.remove('releases.json.new')

    get = renderers.__dict__.get
    for f in glob.glob(path.join(tpldir, '*.jnj')):
        src = path.basename(f)
        name = path.splitext(src)[0]
        try:
            tpl = ENV.get_template(src)
        except:
            # Template not found
            traceback.print_exc()
            continue

        gen_func = get('{}_conf'.format(name), None)

        try:
            gen_func(tpl.render)
        except:
            logging.error('Rendering %s:', f)
            # Not callable
            traceback.print_exc()

if __name__ == '__main__':
    if os.getenv('DEBUG'):
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.WARNING)
    main(TPLDIR)
