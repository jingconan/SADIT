#!/usr/bin/env python
"""Class about parsing data files"""
__author__ = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"

import _mysql
from DataFile import DataFile

from Detector.DetectorLib import vector_quantize_states, model_based, model_free

from socket import inet_ntoa
from struct import pack
def long_to_dotted(ip):
    ip_addr = inet_ntoa(pack('!L', ip))
    return [int(val) for val in ip_addr.rsplit('.')]

get_sec_msec = lambda x: [int(x), int( (x-int(x)) * 1e3)]

class File(object):
    def __init__(self, spec):
        self.spec = spec
    def get_fea_slice(self, rg=None, rg_type=None): raise Exception('Need to be Implemented')
    def get_range(self, rg=None, rg_type=None): raise Exception('Need to be Implemented')
    def get_min(self, rg=None, rg_time=None, fea=None): raise Exception('Need to be Implemented')

# from types import ListType
class SQLFile_SperottoIPOM2009(File):
    # flow_table_name = 'flows'
    def __init__(self, spec):
        File.__init__(self, spec)
        self.db = _mysql.connect(**spec)
        self._init()

    def _init(self):
        # select minimum time
        self.db.query("""SELECT start_time, start_msec FROM flows WHERE (id = 1);""")
        r = self.db.store_result()
        self.min_time_tuple = r.fetch_row()[0]
        self.min_time = float("%s.%s"%self.min_time_tuple)

    def _get_sql_where(self, rg=None, rg_type=None):
        if rg:
            if rg_type == 'flow':
                SQL_SEN_WHERE = """ WHERE ( (id >= %f) AND (id < %f) )""" %tuple(rg)
            elif rg_type == 'time':
                st = get_sec_msec (rg[0] + self.min_time)
                ed = get_sec_msec (rg[1] + self.min_time)
                SQL_SEN_WHERE = """ WHERE ( (start_time > %d) OR ( (start_time = %d) AND (start_msec >= %d)) ) AND
                             ( (end_time < %d) OR ( (end_time = %d) and (end_msec < %d) ) )""" %(st[0], st[0], st[1], ed[0], ed[0], ed[1])
            else:
                print 'rg_type', rg_type
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


from util import DF, NOT_QUAN, QUAN, DataEndException
from Detector.ClusterAlg import KMeans

class SQLDataFileHandler_SperottoIPOM2009(object):
    """"Data File wrapper for SperottoIPOM2009 format. it is store in mysql server, visit
    http://traces.simpleweb.org/traces/netflow/netflow2/dataset_description.txt
    for more information"""
    def __init__(self, db_info, fr_win_size, fea_option):
        self.data = SQLFile_SperottoIPOM2009(db_info)
        self.fr_win_size = fr_win_size
        self.fea_option  = fea_option
        self._cluster_src_ip(fea_option['cluster'])
        self.direct_fea_list = [ k for k in fea_option.keys() if k not in ['cluster', 'dist_to_center']]
        self.fea_QN = fea_option.values()

        # self.quan_flag[ fea_option.keys().index('cluster')] = NOT_QUAN

    def _cluster_src_ip(self, cluster_num):
        src_ip_int_vec_tmp = self.data.get_fea_slice(['src_ip']) #FIXME, need to only use the training data
        src_ip_int_vec = [x[0] for x in src_ip_int_vec_tmp]
        print 'finish get ip address'
        unique_src_IP_int_vec_set = list( set( src_ip_int_vec ) )
        unique_src_IP_vec_set = [long_to_dotted(int(ip)) for ip in unique_src_IP_int_vec_set]
        print 'start kmeans...'
        unique_src_cluster, center_pt = KMeans(unique_src_IP_vec_set, cluster_num, DF)
        print 'center_pt', center_pt
        # print  'unique_src_cluster', unique_src_cluster
        self.cluster_map = dict(zip(unique_src_IP_int_vec_set, unique_src_cluster))
        # self.center_map = dict(zip(unique_src_IP_vec_set, center_pt))
        dist_to_center = [DF(unique_src_IP_vec_set[i], center_pt[ unique_src_cluster[i] ]) for i in xrange(len(unique_src_IP_vec_set))]
        self.dist_to_center_map = dict(zip(unique_src_IP_int_vec_set, dist_to_center))

    def get_fea_slice(self, rg, rg_type):
        print 'get_fea_slice'
        # get direct feature from sql server
        direct_fea_vec = self.data.get_fea_slice(self.direct_fea_list, rg, rg_type)
        if not direct_fea_vec:
            raise DataEndException('Reach Data End')
        # calculate indirect feature
        src_ip_tmp = self.data.get_fea_slice(['src_ip'], rg, rg_type)
        src_ip = [x[0] for x in src_ip_tmp]
        fea_vec = []
        for i in xrange(len(src_ip)):
            ip = src_ip[i]
            fea_vec.append([float(x) for x in direct_fea_vec[i]] + [self.dist_to_center_map[ip], self.cluster_map[ip]])
        min_vec = self.data.get_min(self.direct_fea_list, rg, rg_type)
        max_vec = self.data.get_max(self.direct_fea_list, rg, rg_type)

        dist_to_center_vec = [self.dist_to_center_map[ip] for ip in src_ip]
        min_dist_to_center = min(dist_to_center_vec)
        max_dist_to_center = max(dist_to_center_vec)

        fea_range = [[float(x) for x in min_vec] + [min_dist_to_center, 0], [float(x) for x in max_vec] + [max_dist_to_center, self.fea_option['cluster']]]
        self.quan_flag = [QUAN] * len(self.fea_option.keys())
        self.quan_flag[-1] = NOT_QUAN
        return fea_vec, fea_range

    def get_em(self, rg=None, rg_type='time'):
        """get empirical measure"""
        q_fea_vec = self._quantize_fea(rg, rg_type )
        pmf = model_free( q_fea_vec, self.fea_QN )
        Pmb, mpmb = model_based( q_fea_vec, self.fea_QN )
        return pmf, Pmb, mpmb

    def _quantize_fea(self, rg=None, rg_type='time'):
        """get quantized features for part of the flows"""
        print '_quantize_fea'
        fea_vec, fea_range = self.get_fea_slice(rg, rg_type)
        # import pdb;pdb.set_trace()
        q_fea_vec = vector_quantize_states(zip(*fea_vec), self.fea_QN, zip(*fea_range), self.quan_flag)
        return q_fea_vec


class SQLDataFileWrapper(DataFile):
    """Wrapper the DataFile for real file to SQL server,
    It preloads all the data thus requires large memory"""

    label = ["id", "src_ip", "dst_ip", "packets", "octets", "start_time", "start_msec", "end_time", "end_msec", "src_port", "dst_port", "tcp_flags", "prot"]

    def __init__(self, db_info, fr_win_size, fea_option):
        print 'db_info', db_info
        self.db_info = db_info
        self.db = _mysql.connect(**db_info)
        DataFile.__init__(self, '', fr_win_size, fea_option)

    def _sql_to_flow(self, line):
        f = dict()
        for i in xrange(len(self.label)):
            if self.label[i] in ['src_ip', 'dst_ip']:
                try:
                    f[self.label[i]] = long_to_dotted(int(line[i]))
                except:
                    import pdb;pdb.set_trace()
            else:
                f[self.label[i]] = int(line[i])
        return f


    def parse(self):
        """a functioin to load the data file and store them in **self.flow**
        """
        self.db.query("""SELECT * FROM flows;""")
        r = self.db.store_result()
        self.flow = []

        while True:
            result = r.fetch_row(1)
            self.flow.append(self._sql_to_flow(result[0]))

        print 'result, ', result
        import pdb;pdb.set_trace()

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
    print 'em, ', em
