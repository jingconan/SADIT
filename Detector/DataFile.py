#!/usr/bin/env python
"""Class about parsing data files"""
__author__ = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"

import sys
sys.path.append("..")
import copy
from operator import itemgetter
from Detector.ClusterAlg import KMeans
from Detector.DataParser import ParseData
from Detector.DetectorLib import get_dist_to_center, vector_quantize_states, model_based, model_free, SL
from util import Find, DataEndException, DF, NOT_QUAN, QUAN
from util import abstract_method, FetchNoDataException

class Data(object):
    """virtual base class for data"""
    def get_fea_slice(self, rg=None, rg_type=None): abstract_method()
    def get_max(self, fea, rg=None, rg_type=None): abstract_method()
    def get_min(self, fea, rg=None, rg_time=None): abstract_method()

class DataHandler(object):
    """virtual base class for Data Hanlder"""
    def get_em(self, rg=None, rg_type='time'): abstract_method()


from DataParser import RawParseData
class PreloadHardDiskFile(Data):
    def __init__(self, f_name):
        """ data_order can be flow_first | feature_first
        """
        self.f_name = f_name
        self._init()

    def _init(self):
        self.fea_vec, self.fea_name = RawParseData(self.f_name)
        self.zip_fea_vec = None
        self.t = [ float(t) for t in self._get_value_list('start_time')]
        # import pdb;pdb.set_trace()
        self.min_time = min(self.t)
        self.max_time = max(self.t)
        self.flow_num = len(self.t)

    def _get_value_list(self, key):
        fidx = self.fea_name.index(key)
        self.zip_fea_vec = self.zip_fea_vec if self.zip_fea_vec else zip(*self.fea_vec)
        return self.zip_fea_vec[fidx]

    def _get_where(self, rg=None, rg_type=None):
        if not rg: return 0, self.flow_num-1
        if rg_type == 'flow':
            sp, ep = rg
            if sp >= self.flow_num: raise DataEndException()
        elif rg_type == 'time':
            sp = Find(self.t, rg[0]+self.min_time)
            ep = Find(self.t, rg[1]+self.min_time)
            assert(sp != -1 and ep != -1)
            # import pdb;pdb.set_trace()
            if (sp == len(self.t)-1 or ep == len(self.t)-1):
                raise DataEndException()
        else:
            raise ValueError('unknow window type')
        return sp, ep


    def get_fea_slice(self, fea=None, rg=None, rg_type=None, data_order='flow_first'):
        """this function is to get a chunk of feature vector.
        The feature belongs flows within the range specified by **rg**
        **rg_type** can be ['flow' | 'time' ].
        data_order can be flow_first | feature_first
        """
        sp, ep = self._get_where(rg, rg_type)
        if fea:
            fea_idx = [self.fea_name.index(f) for f in fea]
            if data_order == 'flow_first':
                return [[ v[i] for i in fea_idx] for v in self.fea_vec[sp:ep]]
            elif data_order == 'feature_first':
                return [self._get_value_list(f)[sp:ep] for f in fea]

        if data_order == 'flow_first':
            return self.fea_vec[sp:ep]
        elif data_order == 'feature_first':
            return [fv[sp:ep] for fv in self.zip_fea_vec]


    def get_max(self, fea, rg=None, rg_type=None):
        sp, ep = self._get_where(rg, rg_type)
        fea = fea if fea else self.fea_name
        return [max(self._get_value_list(f)[sp:ep]) for f in fea]

    def get_min(self, fea, rg=None, rg_type=None):
        sp, ep = self._get_where(rg, rg_type)
        fea = fea if fea else self.fea_name
        return [min(self._get_value_list(f)[sp:ep]) for f in fea]

class HardDiskFileHandler(object):
    """Data is stored as Hard Disk File"""
    def __init__(self, db_info, fr_win_size, fea_option):
        self._init_data(db_info)
        self.fr_win_size = fr_win_size
        self.fea_option  = fea_option
        self._cluster_src_ip(fea_option['cluster'])
        self.direct_fea_list = [ k for k in fea_option.keys() if k not in ['cluster', 'dist_to_center']]
        # self.fea_QN = fea_option.values()
        self.fea_QN = [fea_option['cluster'], fea_option['dist_to_center']] + [fea_option[k] for k in self.direct_fea_list]

    def _init_data(self, f_name):
        self.data = PreloadHardDiskFile(f_name)

    def _to_dotted(self, ip): return tuple( [int(v) for v in ip.rsplit('.')] )

    def _cluster_src_ip(self, cluster_num):
        src_ip_int_vec_tmp = self.data.get_fea_slice(['src_ip']) #FIXME, need to only use the training data
        src_ip_int_vec = [x[0] for x in src_ip_int_vec_tmp]
        print 'finish get ip address'
        unique_src_IP_int_vec_set = list( set( src_ip_int_vec ) )
        unique_src_IP_vec_set = [self._to_dotted(ip) for ip in unique_src_IP_int_vec_set]
        print 'start kmeans...'
        unique_src_cluster, center_pt = KMeans(unique_src_IP_vec_set, cluster_num, DF)
        print 'center_pt', center_pt
        print  'unique_src_cluster', unique_src_cluster
        self.cluster_map = dict(zip(unique_src_IP_int_vec_set, unique_src_cluster))
        # self.center_map = dict(zip(unique_src_IP_vec_set, center_pt))
        dist_to_center = [DF( unique_src_IP_vec_set[i], center_pt[ unique_src_cluster[i] ]) for i in xrange(len(unique_src_IP_vec_set))]
        self.dist_to_center_map = dict(zip(unique_src_IP_int_vec_set, dist_to_center))

    def get_fea_slice(self, rg, rg_type):
        # get direct feature from sql server
        direct_fea_vec = self.data.get_fea_slice(self.direct_fea_list, rg, rg_type)
        # import pdb;pdb.set_trace()
        if not direct_fea_vec:
            raise FetchNoDataException("Didn't find any data in this range")

        # calculate indirect feature
        src_ip_tmp = self.data.get_fea_slice(['src_ip'], rg, rg_type)
        src_ip = [x[0] for x in src_ip_tmp]
        fea_vec = []
        for i in xrange(len(src_ip)):
            ip = src_ip[i]
            fea_vec.append( [self.cluster_map[ip], self.dist_to_center_map[ip]] + [float(x) for x in direct_fea_vec[i]])
        # import pdb;pdb.set_trace()

        min_vec = self.data.get_min(self.direct_fea_list, rg, rg_type)
        max_vec = self.data.get_max(self.direct_fea_list, rg, rg_type)

        dist_to_center_vec = [self.dist_to_center_map[ip] for ip in src_ip]
        min_dist_to_center = min(dist_to_center_vec)
        max_dist_to_center = max(dist_to_center_vec)

        fea_range = [
                [0, min_dist_to_center] + [float(x) for x in min_vec],
                [self.fea_option['cluster']-1, max_dist_to_center] + [float(x) for x in max_vec],
                ]

        self.quan_flag = [QUAN] * len(self.fea_option.keys())
        self.quan_flag[0] = NOT_QUAN
        return fea_vec, fea_range

    def get_em(self, rg=None, rg_type='time'):
        """get empirical measure"""
        q_fea_vec = self._quantize_fea(rg, rg_type )
        pmf = model_free( q_fea_vec, self.fea_QN )
        Pmb, mpmb = model_based( q_fea_vec, self.fea_QN )
        # print 'pmf, ', pmf
        return pmf, Pmb, mpmb

    def _quantize_fea(self, rg=None, rg_type='time'):
        """get quantized features for part of the flows"""
        fea_vec, fea_range = self.get_fea_slice(rg, rg_type)
        # import pdb;pdb.set_trace()
        q_fea_vec = vector_quantize_states(zip(*fea_vec), self.fea_QN, zip(*fea_range), self.quan_flag)
        return q_fea_vec



class DataFile(object):
    """from file to feature, this class is *depreciated*"""
    __slots__ = ['f_name', 'flow', 'cluster', 'center_pt', 'fea', 'fea_range','fea_vec',
            'unique_src_IP_vec_set', 'src_IP_vec_set', 'cluster_num', 'fr_win_size', 'unique_src_cluster',
            'fea_list', 'fea_handler_map', 'quan_flag', 'fea_QN', 't']
    def __init__(self, f_name, fr_win_size, fea_option):
        self.fea_handler_map = {
            'flow_rate':[ self.get_flow_rate, QUAN ],
            'dist_to_center':[ self.get_dist_to_center, QUAN ],
            'flow_size':[ self.get_flow_size, QUAN ],
            # 'octets':[ self.get_flow_size, QUAN ],
            'cluster':[ self.get_cluster, NOT_QUAN ],
            }
        self.f_name = f_name
        self.fr_win_size = fr_win_size

        self._add_quan_num(fea_option)
        self.fea_list = fea_option.keys()
        self.cluster_num = fea_option['cluster']

        self.parse()
        self._init_cluster()
        self.gen_rel_time_spot()
        self.gen_fea()

    def _get_flow_src_cluster(self, f):
        idx = self.unique_src_IP_vec_set.index(f['srcIPVec'])
        return self.unique_src_cluster[idx]

    def _init_cluster(self):
        """self.cluster is a vector which specify cluster of src ip for each flow"""
        self._cluster_src_ip()
        self.cluster = [ self._get_flow_src_cluster(f) for f in self.flow ]

    def _add_quan_num(self, fea_option):
        for k in self.fea_handler_map.iterkeys():
            self.fea_handler_map[k].append( fea_option.get(k) )

    def __add__(self, other):
        """addition of two data files. use for multi files. """
        new_file = copy.deepcopy(self)
        new_file.flow += other.flow
        new_file.sort_flow('t')
        new_file._init_cluster()
        self.gen_rel_time_spot()
        new_file.gen_fea()
        return new_file

    def parse(self):
        """a functioin to load the data file and store them in **self.flow**
        """
        import types
        self.flow = []
        if type(self.f_name) == types.ListType:
            # import pdb;pdb.set_trace()
            for f in self.f_name:
                self.flow += ParseData(f)
        else:
            self.flow = ParseData(self.f_name)
        self.sort_flow('t')

    def gen_fea(self):
        """suppose the number of feature used is N
        this function will set
        - self.quan_flag: a Nx1 indicating whether each feature
            need to be quantized or not
        - self.fea_QN: a Nx1 indicating the quanzied level for each
            feature.
        - self.fea_vec: a list of list contains the features for each flow.
        """
        self.fea = dict()
        for fk in self.fea_list:
            self.fea[fk] = self.fea_handler_map[fk][0]()
        self.quan_flag =  [ self.fea_handler_map[k][1] for k in self.fea.keys() ]
        self.fea_QN = [ self.fea_handler_map[k][2] for k in self.fea.keys() ]
        # import pdb;pdb.set_trace()
        # self.fea_vec = np.array( self.fea.values() ).T
        self.fea_vec = self.fea.values()

    def gen_rel_time_spot(self):
        """get the time stamp, normalize it, making it starts from zero"""
        self.t = self.get_value_list('t')
        mint = min(self.t)
        self.t = [ t - mint for t in self.t ]

    def sort_flow(self, key='time'):
        """sort flows according to a attribute, which is 'key', the default 'key' is time"""
        self.flow = sorted( self.flow, key=itemgetter(key) )

    def argsort_flow(self, key='time'):
        """indexes that can sort the flow"""
        return sorted( range(len(self.flow)), key=itemgetter(key) )

    def get_value_list(self, key): return [ f.get(key) for f in self.flow ]

    def _cluster_src_ip(self):
        self.src_IP_vec_set = self.get_value_list('srcIPVec')
        self.unique_src_IP_vec_set = list( set( self.src_IP_vec_set ) )
        # import pdb;pdb.set_trace()
        self.unique_src_cluster, self.center_pt = KMeans(self.unique_src_IP_vec_set, self.cluster_num, DF)

    def get_fea_slice(self, rg, rg_type):
        """this function is to get a chunk of feature vector.
        The feature belongs flows within the range specified by **rg**
        **rg_type** can be ['flow' | 'time' ].
        """
        if not rg: return self.fea_vec
        if rg_type == 'flow':
            # return self.fea_vec[rg, :]
            return SL(self.fea_vec, rg[0], rg[1])
        elif rg_type == 'time':
            sp = Find(self.t, rg[0])
            ep = Find(self.t, rg[1])
            assert(sp != -1 and ep != -1)
            # print 'sp, ', sp, 'ep, ', ep
            if (sp == len(self.t)-1 or ep == len(self.t)-1):
                raise DataEndException()
            # return self.fea_vec[sp:ep, :]
            return SL(self.fea_vec, sp, ep)
        else:
            raise ValueError('unknow window type')

    def get_fea_range(self):
        """get the range of the feature vector. """
        self.fea_range = dict()
        for k, v in self.fea.iteritems():
            self.fea_range[k] = [min(v), max(v)]
        return self.fea_range

    def get_fea_range_vec(self):
        return self.get_fea_range().values()

    def quantize_fea(self, rg=None, rg_type='time'):
        """get quantized features for part of the flows"""
        fea_vec = self.get_fea_slice(rg, rg_type)
        fea_range = self.get_fea_range_vec()
        # import pdb;pdb.set_trace()
        # q_fea_vec = vector_quantize_states(list(fea_vec.T), self.fea_QN, list(fea_range.T), self.quan_flag)
        q_fea_vec = vector_quantize_states(fea_vec, self.fea_QN, fea_range, self.quan_flag)
        return q_fea_vec

    def get_em(self, rg=None, rg_type='time'):
        """get empirical measure"""
        q_fea_vec = self.quantize_fea(rg, rg_type )
        pmf = model_free( q_fea_vec, self.fea_QN )
        Pmb, mpmb = model_based( q_fea_vec, self.fea_QN )
        # print 'pmf, ', pmf
        return pmf, Pmb, mpmb

    ### Function For Extracting Features ###
    def get_cluster(self): return self.cluster
    def get_flow_size(self): return self.get_value_list('flowSize')

    def plot_flow_size(self):
        import matplotlib.pyplot as plt
        flow_size = self.get_flow_size()
        print 'range of flow size %f, %f' %( min(flow_size), max(flow_size) )
        plt.figure()
        plt.plot(flow_size)
        plt.show()

    def get_flow_rate(self):
        t = self.get_value_list('t')
        win = self.fr_win_size
        fr = []
        for i in xrange(len(t)):
            idx = Find(t, t[i] - win)
            if idx == -1: idx = 0
            c = self.cluster[i]
            fr.append( self.cluster[idx:i].count(c) )
        return fr

    def get_dist_to_center(self):
        return get_dist_to_center(self.src_IP_vec_set, self.cluster, self.center_pt, DF)

