#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
import os
pkg_config = {
    'ipaddr': ('2.1.1', 'http://ipaddr-py.googlecode.com/files/ipaddr-2.1.1.tar.gz'),
    'networkx': ('1.0', 'https://github.com/networkx/networkx/archive/networkx-1.0.tar.gz'),
    'pydot': ('1.0.2', 'http://pydot.googlecode.com/files/pydot-1.0.2.tar.gz'),
    'pyparsing': ('1.5.2', 'http://downloads.sourceforge.net/project/pyparsing/pyparsing/pyparsing-1.5.2/pyparsing-1.5.2.tar.gz'),
    'pyradix': ('0.5', 'http://py-radix.googlecode.com/files/py-radix-0.5.tar.gz'),
    'argparse': ('1.2.1', 'http://argparse.googlecode.com/files/argparse-1.2.1.tar.gz'),
    'numpy': ('1.6.2', 'http://downloads.sourceforge.net/project/numpy/NumPy/1.6.2/numpy-1.6.2.tar.gz'),
    'cython': ('0.20.1', 'http://cython.org/release/Cython-0.20.1.tar.gz'),
}

import sys, os
argv = sys.argv

def get_f_name(url):
    tar_file = url.rsplit('/')[-1]
    folder_name = tar_file.rsplit('.tar.gz')[0]
    return tar_file, folder_name

def install(pkg_name, url):
    print('installing package %s'%(pkg_name))
    # tar_file = url.rsplit('/')[-1]
    # folder_name = tar_file.rsplit('.tar.gz')[0]
    tar_file, folder_name = get_f_name(url)
    if not os.path.isdir(folder_name):
        print('wget %s'%(url))
        os.system('wget %s'%(url))

        print('tar -xzvf %s'%(url.rsplit('/')[-1]))
        os.system('tar -xzvf %s'%(tar_file))

    print('cd %s && python setup.py install'%(folder_name))
    os.system('cd %s && python setup.py install'%(folder_name))

import shutil
def clean():
    for k, (_, url) in pkg_config.iteritems():
        tar_file, folder_name = get_f_name(url)
        if os.path.exists(folder_name):
            shutil.rmtree(folder_name)
            # os.remove(folder_name)
        if os.path.exists(tar_file):
            os.remove(tar_file)

if len(argv) < 2:
    pkgs = pkg_config.keys()
else:
    if argv[1] == '-h':
        print('Usage: python setup-dep.py <packge_name>. Run without argument'
                ' will install all avaliable packages. use --clean to'
                ' clean all downloaded packages')
        sys.exit(0)
    elif argv[1] == '--clean':
        clean()
        sys.exit(0)

    pkgs = argv[1:]

for pkg in pkgs:
    install(pkg_config[pkg][0], pkg_config[pkg][1])





