"""put import module sentence that may fail here
"""
from __future__ import print_function, division

try:
    import numpy as np
except ImportError:
    np = None
    print('--> [wanring], no numpy, some funcationality may be affected')

try:
    import guiqwt.pyplot as plt
    print('--> Use [guiqwt] as plot backend')
except ImportError:
    try:
        import matplotlib.pyplot as plt
        # import guiqwt.pyplot as plt
        print('--> Use [matplotlib] as plot backend')
    except ImportError:
        plt = None
        print('--> [wanring], no [guiqwt] and [matplotlib], cannot visualize the result')

try:
    from collections import Counter
except ImportError:
    Counter = None
    print('--> [wanring], no collection.Counter , some funcationality may be affected')

try:
    import _mysql as mysql
    from MySQLdb.constants import FIELD_TYPE
except ImportError:
    mysql = None
    # FIELD_TYPE = object
    # FIELD_TYPE = object

    from Namespace import Namespace
    FIELD_TYPE = Namespace({
            'INT24': None,
            'LONG': None,
            'LONGLONG': None
        })

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
