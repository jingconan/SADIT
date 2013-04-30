#!/usr/bin/env python
"""Class about parsing data files"""
from __future__ import print_function, division, absolute_import
__author__ = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"

import _mysql
from socket import inet_ntoa
from struct import pack
from sadit.util import DataEndException
from .Data import Data
from .DataHandler import QuantizeDataHandler

def long_to_dotted(ip):
    ip_addr = inet_ntoa(pack('!L', ip))
    return [int(val) for val in ip_addr.rsplit('.')]

get_sec_msec = lambda x: [int(x), int( (x-int(x)) * 1e3)]


# from types import ListType
class SQLFile_SperottoIPOM2009(Data):
    def __init__(self, spec):
        self.db = _mysql.connect(**spec)
        self._init()

    def _init(self):
        # select minimum time
        self.db.query("""SELECT start_time, start_msec FROM flows WHERE (id = 1);""")
        r = self.db.store_result()
        self.min_time_tuple = r.fetch_row()[0]
        self.min_time = float("%s.%s"%self.min_time_tuple)

        self.db.query("""SELECT MAX(id) FROM flows;""")
        r = self.db.store_result()
        self.flow_num = int(r.fetch_row()[0][0])

        self.db.query("""SELECT end_time, end_msec FROM flows WHERE (id = %d);"""%(self.flow_num))
        r = self.db.store_result()

        self.max_time_tuple = r.fetch_row()[0]
        self.max_time = float("%s.%s"%self.max_time_tuple)

    def _get_sql_where(self, rg=None, rg_type=None):
        if rg:
            if rg_type == 'flow':
                SQL_SEN_WHERE = """ WHERE ( (id >= %f) AND (id < %f) )""" %tuple(rg)
                if rg[0] > self.flow_num:
                    raise DataEndException("reach data end")

            elif rg_type == 'time':
                st = get_sec_msec (rg[0] + self.min_time)
                ed = get_sec_msec (rg[1] + self.min_time)
                SQL_SEN_WHERE = """ WHERE ( (start_time > %d) OR ( (start_time = %d) AND (start_msec >= %d)) ) AND
                             ( (end_time < %d) OR ( (end_time = %d) and (end_msec < %d) ) )""" %(st[0], st[0], st[1], ed[0], ed[0], ed[1])

                # print 'rg[0]', rg[0]
                # print 'self.min_time', self.min_time
                # print 'current time, ', rg[0] + self.min_time
                # print 'self.maxtime', self.max_time
                if rg[0] + self.min_time > self.max_time:
                    raise DataEndException("reach data end")
            else:
                print('rg_type', rg_type)
                raise ValueError('unknow window type')
        else:
            SQL_SEN_WHERE = ""
        return SQL_SEN_WHERE

    def get_max(self, fea, rg=None, rg_type=None):
        fea_str = ['MAX(%s)'%(f) for f in fea]
        SQL_SEN = """SELECT %s FROM flows"""%(",".join(fea_str)) + self._get_sql_where(rg, rg_type) + ";"
        self.db.query(SQL_SEN)
        r = self.db.store_result().fetch_row(0)
        return r[0]

    def get_min(self, fea, rg=None, rg_type=None):
        fea_str = ['MIN(%s)'%(f) for f in fea]
        SQL_SEN = """SELECT %s FROM flows"""%(",".join(fea_str)) + self._get_sql_where(rg, rg_type) + ";"
        self.db.query(SQL_SEN)
        r = self.db.store_result().fetch_row(0)
        return r[0]

    def get_fea_slice(self, fea, rg=None, rg_type=None):
        """this function is to get a chunk of feature vector.
        The feature belongs flows within the range specified by **rg**
        **rg_type** can be ['flow' | 'time' ].
        """
        SQL_SEN = """SELECT %s FROM flows"""%(",".join(fea)) + self._get_sql_where(rg, rg_type) + ";"
        # print SQL_SEN
        self.db.query(SQL_SEN)
        result = self.db.store_result().fetch_row(0)
        # return [line[0] for line in result] if len(fea) == 1 else result
        return result

class SQLDataFileHandler_SperottoIPOM2009(QuantizeDataHandler):
    """"Data File wrapper for SperottoIPOM2009 format. it is store in mysql server, visit
    http://traces.simpleweb.org/traces/netflow/netflow2/dataset_description.txt
    for more information"""
        # self.quan_flag[ fea_option.keys().index('cluster')] = NOT_QUAN
    def _init_data(self, db_info):
        self.data = SQLFile_SperottoIPOM2009(db_info)

    def _to_dotted(self, ip): return long_to_dotted(int(ip))


if __name__ ==  "__main__":
    db_info = dict(
            host = "localhost",
            db = "labeled",
            read_default_file = "~/.my.cnf",
            )
    # fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2}
    fea_option = {'dist_to_center':2, 'octets':2, 'cluster':2}
    # data_file = SQLDataFileWrapper(db_info, 100, fea_option)
    data_file = SQLDataFileHandler_SperottoIPOM2009(db_info, 100, fea_option)
    # data_file.get_fea_slice([1, 10], 'flow')

    em = data_file.get_em([1, 1000], 'flow')
    print('em, ', em)
