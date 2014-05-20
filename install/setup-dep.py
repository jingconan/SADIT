#!/usr/bin/env python
import os
packages=['ipaddr-2.1.1', 'networkx-1.0', 'pydot-1.0.2',
	'pyparsing1.5.2', 'pyradix', 'argparse-1.2.1',
    'cython-0.20'
	#'numpy-1.6.2',
	]
packages_urls = [
	'http://ipaddr-py.googlecode.com/files/ipaddr-2.1.1.tar.gz',
	'http://networkx.lanl.gov/download/networkx/networkx-1.0.1.tar.gz',
	'http://pydot.googlecode.com/files/pydot-1.0.2.tar.gz',
	'http://downloads.sourceforge.net/project/pyparsing/pyparsing/pyparsing-1.5.2/pyparsing-1.5.2.tar.gz',
	'http://py-radix.googlecode.com/files/py-radix-0.5.tar.gz',
	'http://argparse.googlecode.com/files/argparse-1.2.1.tar.gz',
	'http://downloads.sourceforge.net/project/numpy/NumPy/1.6.2/numpy-1.6.2.tar.gz',
    'http://cython.org/release/Cython-0.20.1.tar.gz'
]

for i in xrange(len(packages)):
	url = packages_urls[i]
	print('installing package %s'%(packages[i]))
	print('wget %s'%(url))
	os.system('wget %s'%(url))

	print('tar -xzvf %s'%(url.rsplit('/')[-1]))
	tar_file = url.rsplit('/')[-1]
	os.system('tar -xzvf %s'%(tar_file))

	folder_name = tar_file.rsplit('.tar.gz')[0]
	print('cd %s && python setup.py install'%(folder_name))
	os.system('cd %s && python setup.py install'%(folder_name))





