#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, division

import os
import re
import json
import logging
import shutil
from os import path
import traceback
from distutils.version import StrictVersion

import requests
from bs4 import BeautifulSoup
get_soup = lambda c: BeautifulSoup(c, 'lxml')

from jinja2 import FileSystemLoader, Environment

import renderers

CURDIR = path.dirname(path.realpath(__file__))
TPLDIR = path.join(CURDIR, 'templates')
ENV = Environment(loader=FileSystemLoader(TPLDIR))
DISTROS = ['ubuntu', 'debian', 'archlinux']

def get_archlinux_releases():
    return ''
def get_debian_releases():
    return ''

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
    # Fetch latest releases for each distros
    releases = dict()
    get = globals().get
    rel_info_tmp = path.join(CURDIR, 'releases.json.new')
    rel_info = path.join(CURDIR, 'releases.json')

    with open(rel_info_tmp, 'w') as fout:
        for dist in DISTROS:
            f = get('get_{}_releases'.format(dist), None)
            # Not callable
            if not hasattr(f, '__code__'):
                logging.warn('Cannot get releases of `%s`', dist)
                continue
            releases[dist] = f()
            if releases[dist] is None:
                os.remove(rel_info_tmp)
                raise ValueError
        json.dump(releases, fout, indent=4)

    shutil.copyfile(rel_info_tmp, rel_info)
    os.remove(rel_info_tmp)

    # Generate configuration for each distros
    get = renderers.__dict__.get
    for dist in DISTROS:
        try:
            tpl = ENV.get_template('{}.jnj'.format(dist))
        except:
            # Template not found
            traceback.print_exc()
            continue

        gen_func = get('{}_conf'.format(dist), None)

        try:
            gen_func(tpl.render)
        except:
            logging.error('Rendering %s:', f)
            # Not callable
            traceback.print_exc()

    # Generate index.html
    with open(path.join(CURDIR, 'index.html'), 'w') as fout,\
         open(path.join(CURDIR, 'releases.json'), 'r') as fin:
        releases = json.load(fin).get('ubuntu')
        tpl = ENV.get_template('index.html')
        info = list((name, vers, False) for vers, name, _ in releases.get('Future'))
        info.extend(list((name, vers, False) for vers, name, _ in releases.get('Current')))
        info.extend(list((name, vers, True) for vers, name, _ in releases.get('End_of_life')))
        info.sort(key=lambda x: StrictVersion(x[1]), reverse=True)
        fout.write(tpl.render(info=info))

if __name__ == '__main__':
    if os.getenv('DEBUG'):
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.WARNING)
    main(TPLDIR)
