#!/usr/bin/env python
"""
Analyze the alert of sperottoIPOM2009 data
"""
__author__ = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"
__status__ = "Development"


import _mysql

db_info = dict(
        host = "localhost",
        db = "labeled",
        read_default_file = "~/.my.cnf",
        )


db = _mysql.connect(**db_info)
db.query("""SELECT timestamp FROM alerts;""")
r = db.store_result()
result = r.fetch_row(0)
time = [int(x[0]) for x in result if x[0]]

from matplotlib.pyplot import *
min_t = min(time)
nt = [t - min_t for t in time]
plot(nt, [1]*len(time), 'r+')
axis([0, 2000, 0.9, 1.1])
# savefig('ano_vis.eps')
show()

