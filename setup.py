from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("CythonUtil.pyx")
)

import shutil
shutil.copyfile('./build/lib.linux-x86_64-2.7/sadit/CythonUtil.so',
    'CythonUtil.so')
import CythonUtil
CythonUtil.c_parse_records('./Benchmarks/n0_flow.txt')
