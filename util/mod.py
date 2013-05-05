"""put import module sentence that may fail here
"""
from __future__ import print_function, division

try:
    import numpy as np
except ImportError:
    np = None
    print('--> [wanring], no numpy, some funcationality may be affected')

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
    print('--> [wanring], no matplotlib, some funcationality may be affected')

try:
    from collections import Counter
except ImportError:
    Counter = None
    print('--> [wanring], no collection.Counter , some funcationality may be affected')

try:
    import _mysql as mysql
except ImportError:
    mysql = None
    print('--> [warning] cannot import sql related function, reading for sql server is not supported')


#########################################
## Adaption for Python3
#########################################

try:
    import Queue as queue # replace with 'import queue' if using Python 3
except ImportError:
    import queue

try:
    from itertools import izip
except ImportError:
    izip = zip
