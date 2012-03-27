from distutils.core import setup
from distutils.extension import Extension

setup(name='ipaddrgen',
      author='J. Raffensperger and J. Sommers',
      author_email='jsommers@colgate.edu',
      url='http://cs.colgate.edu/faculty/jsommers',
      description='Module for realistic generation of IP addresses',
      version='032011-alpha',
      ext_modules=[Extension('_ipaddrgen', ['ipaddrgen.i','addrgen_trie.c'],
                             swig_opts=['-modern', '-I.'])],
      py_modules=['ipaddrgen'],
     )
