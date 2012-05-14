"""Class about parsing data files"""
import sys
sys.path.append("..")
import copy
from operator import itemgetter
from Detector.ClusterAlg import KMeans
from Detector.DataParser import ParseData
from Detector.DetectorLib import get_dist_to_center, vector_quantize_states, model_based, model_free, SL
from util import Find, DataEndException, DF, NOT_QUAN, QUAN


class DataFile(object):
    """from file to feature"""
    __slots__ = ['f_name', 'flow', 'cluster', 'center_pt', 'fea', 'fea_range','fea_vec',
            'unique_src_IP_vec_set', 'src_IP_vec_set', 'cluster_num', 'fr_win_size', 'unique_src_cluster',
            'fea_list', 'fea_handler_map', 'quan_flag', 'fea_QN', 't']
    def __init__(self, f_name, fr_win_size, fea_option):
        self.fea_handler_map = {
            'flow_rate':[ self.get_flow_rate, QUAN ],
            'dist_to_center':[ self.get_dist_to_center, QUAN ],
            'flow_size':[ self.get_flow_size, QUAN ],
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

    def _add_quan_num(self, fea_list):
        for k in self.fea_handler_map.iterkeys():
            self.fea_handler_map[k].append( fea_list.get(k) )

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
        self.fea = dict()
        for fk in self.fea_list:
            self.fea[fk] = self.fea_handler_map[fk][0]()
        self.quan_flag =  [ self.fea_handler_map[k][1] for k in self.fea.keys() ]
        self.fea_QN = [ self.fea_handler_map[k][2] for k in self.fea.keys() ]
        # import pdb;pdb.set_trace()
        # self.fea_vec = np.array( self.fea.values() ).T
        self.fea_vec = self.fea.values()

    def gen_rel_time_spot(self):
        self.t = self.get_value_list('t')
        mint = min(self.t)
        self.t = [ t - mint for t in self.t ]

    def sort_flow(self, key='time'):
        self.flow = sorted( self.flow, key=itemgetter(key) )

    def argsort_flow(self, key='time'):
        return sorted( range(len(self.flow)), key=itemgetter(key) )

    def get_value_list(self, key): return [ f.get(key) for f in self.flow ]

    def _cluster_src_ip(self):
        self.src_IP_vec_set = self.get_value_list('srcIPVec')
        self.unique_src_IP_vec_set = list( set( self.src_IP_vec_set ) )
        self.unique_src_cluster, self.center_pt = KMeans(self.unique_src_IP_vec_set, self.cluster_num, DF)

    def get_fea_slice(self, rg, rg_type):
        if not rg: return self.fea_vec
        if rg_type == 'flow':
            # return self.fea_vec[rg, :]
            return SL(self.fea_vec, rg[0], rg[1])
        elif rg_type == 'time':
            sp = Find(self.t, rg[0])
            ep = Find(self.t, rg[1])
            assert(sp != -1 and ep != -1)
            if (sp == len(self.t)-1 or ep == len(self.t)-1):
                raise DataEndException()
            # return self.fea_vec[sp:ep, :]
            return SL(self.fea_vec, sp, ep)
        else:
            raise ValueError('unknow window type')

    def get_fea_range(self):
        self.fea_range = dict()
        for k, v in self.fea.iteritems():
            self.fea_range[k] = [min(v), max(v)]
        return self.fea_range

    def get_fea_range_vec(self):
        return self.get_fea_range().values()

    def quantize_fea(self, rg=None, rg_type='time'):
        fea_vec = self.get_fea_slice(rg, rg_type)
        fea_range = self.get_fea_range_vec()
        # q_fea_vec = vector_quantize_states(list(fea_vec.T), self.fea_QN, list(fea_range.T), self.quan_flag)
        q_fea_vec = vector_quantize_states(fea_vec, self.fea_QN, fea_range, self.quan_flag)
        return q_fea_vec

    def get_em(self, rg=None, rg_type='time'):
        """get empirical measure"""
        q_fea_vec = self.quantize_fea(rg, rg_type )
        pmf = model_free( q_fea_vec, self.fea_QN )
        Pmb, mpmb = model_based( q_fea_vec, self.fea_QN )
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
