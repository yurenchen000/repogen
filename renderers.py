#!/usr/bin/python -O
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, with_statement, division

import os
from os import path
import json
import itertools

PROTOCOLS = ('ftp', 'http', 'https')

CURDIR = path.dirname(path.realpath(__file__))
CFGDIR = path.join(CURDIR, 'conf')
if not path.exists(CFGDIR):
    os.makedirs(CFGDIR)

def save(*args, content):
    cfg = '-'.join(args)
    with open(path.join(CFGDIR, cfg), 'w') as fout:
        fout.writelines(content)

def ubuntu_conf(render):
    meta = dict()
    with open('releases.json', 'r') as fin:
        meta = json.load(fin)
    if meta.get('ubuntu', None) is None:
        raise ValueError
    rel = meta.get('ubuntu')
    take_ver = lambda xs: (x[1] for x in xs)
    info = itertools.chain(take_ver(rel.get('Current')), take_ver(rel.get('Future')))
    for proto, ipv, vers in itertools.product(PROTOCOLS, ['4', '6'], info):
        save('ubuntu',
             proto, ipv, vers,
             content=render(PROTO=proto, VERSION=vers,
                            URL='mirrors.ustc.edu.cn' if ipv == '4' else 'ipv6.mirrors.ustc.edu.cn'))

    info = take_ver(rel.get('End_of_life'))
    for proto, ipv, vers in itertools.product(PROTOCOLS, ['4', '6'], info):
        save('ubuntu',
             proto, ipv, vers,
             content=render(PROTO=proto, VERSION=vers,
                            URL='mirrors.ustc.edu.cn/ubuntu-old-releases' if ipv == '4'
                            else 'ipv6.mirrors.ustc.edu.cn/ubuntu-old-releases'))


def debian_conf(render):
    for proto, ipv, vers in itertools.product(PROTOCOLS, ['4', '6'], ['sid', 'stretch', 'jessie', 'wheezy']):
        save('debian', proto, ipv, vers,
             content=render(PROTO=proto, IP='' if ipv == '4' else 'ipv6.', VERSION=vers))

def archlinux_conf(render):
    for proto, ipv in itertools.product(PROTOCOLS, ['4', '6']):
        save('archlinux', proto, ipv,
             content=render(PROTO=proto, IP='' if ipv == '4' else 'ipv6.'))

