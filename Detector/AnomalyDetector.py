#!/usr/bin/env python
import sys
sys.path.append("..")
import settings
# from Derivative import *
from Derivative import ModelFreeDerivative, ModelBaseDerivative
from DetectorLib import I1, I2, get_dist_to_center, vector_quantize_states, model_based, model_free, SL

from util import Find, abstract_method
from matplotlib.pyplot import figure, plot, subplot, show
import cPickle as pickle

from ClusterAlg import KMeans
from DataParser import ParseData
from operator import itemgetter
import copy

# The Distance Function
DF = lambda x,y:abs(x[0]-y[0]) * (256**3) + abs(x[1]-y[1]) * (256 **2) + abs(x[2]-y[2]) * 256 + abs(x[3]-y[3])

QUAN = 1
NOT_QUAN = 0

class DataEndException(Exception):
    pass

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
    #######################################


class AnoDetector (object):
    def __init__(self, desc):
        self.desc = desc
        # self.record_data = dict(IF=[], IB=[], winT=[], threshold=[], em=[])
        self.record_data = dict(entropy=[], winT=[], threshold=[], em=[])

    def __call__(self, *args, **kwargs):
        return self.detect(*args, **kwargs)

    def record(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.record_data[k].append(v)

    def reset_record(self):
        for k, v in self.record_data.iteritems():
            self.record_data[k] = []

    # def detect(self, f_name):
        # self.data_file = DataFile(f_name,
                # self.desc['win_size'],
                # self.desc['fea_list'])
    def detect(self, data_file):
        self.data_file = data_file
        self.norm_em = self.get_em(rg=[0, 1000], rg_type='time')

        win_size = self.desc['win_size']
        interval = self.desc['interval']
        time = self.desc['fr_win_size']

        while True:
            print 'time: %f' %(time)
            try:
                # d_pmf, d_Pmb, d_mpmb = self.data_file.get_em(rg=[time, time+win_size], rg_type='time')
                em = self.get_em(rg=[time, time+win_size], rg_type='time')
                entropy = self.I(em, self.norm_em)
                self.record( entropy=entropy, winT = time, threshold = 0, em=em )
                time += interval
            except DataEndException:
                print 'reach data end, break'
                break
        return self.record_data

    def plot_entropy(self):
        t2 = self.record_data['winT']
        mt = min(t2)
        rt = [t-mt for t in t2]
        figure()
        plot(rt, self.record_data['entropy'])
        show()


    # def plot_entropy(self):
    #     t2 = self.record_data['winT']
    #     mt = min(t2)
    #     rt = [t-mt for t in t2]
    #     figure()
    #     subplot(211)
    #     plot(rt, self.record_data['IF'])
    #     subplot(212)
    #     plot(rt, self.record_data['IB'])
    #     show()

    def dump(self, data_name):
        pickle.dump( self.record_data, open(data_name, 'w') )

class ModelFreeAnoDetector(AnoDetector):
    def I(self, d_pmf, pmf):
        return I1(d_pmf, pmf)

    def get_em(self, rg, rg_type):
        """get empirical measure"""
        pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
        return pmf

class ModelBaseAnoDetector(AnoDetector):
    def I(self, em, norm_em):
        d_Pmb, d_mpmb = em
        Pmb, mpmb = norm_em
        return I2(d_Pmb, d_mpmb, Pmb, mpmb)

    def get_em(self, rg, rg_type):
        """get empirical measure"""
        pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
        return Pmb, mpmb

import numpy as np
def CalIndicator(deri, intervalRatio):
    '''Calculate the difference of derivative on anomaly time w.r.t normal '''
    tn = len(deri)
    anoStart = int( tn * intervalRatio[0])
    anoStop = int( tn * intervalRatio[1] )
    anoDeri = deri[anoStart:anoStop+1]
    anoAveDeri = np.nansum(anoDeri, axis=0) * 1.0 / len(anoDeri)
    normalAnoValue = np.nansum(deri, axis=0) * 1.0 / tn
    GetChangePercent = lambda a, b:np.array(a)-np.array(b)
    changePer = GetChangePercent(anoAveDeri, normalAnoValue)
    return changePer

class AnoTypeTest(AnoDetector):
    def __init__(self, detector, total_t, ano_t):
        self.detector = detector
        self.total_t = total_t
        self.ano_t = ano_t

    def get_ano_indi(self):
        return CalIndicator(self.deri, self.get_interval_ratio())

    def get_interval_ratio(self):
        return [self.ano_t[0] * 1.0/self.total_t, self.ano_t[1] * 1.0/self.total_t]

    def detect_ano_type(self): abstract_method()

class ModelFreeAnoTypeTest(AnoTypeTest):
    def get_em_vec(self):
        return [ em for em in self.detector.record_data['em'] ]

    def detect_ano_type(self):
        norm_em = self.detector.norm_em
        # import pdb;pdb.set_trace()
        self.deri = [ ModelFreeDerivative(d_pmf, norm_em) for d_pmf in self.get_em_vec() ]
        print 'self.deri', self.deri
        self.ano_indi = self.get_ano_indi()
        print 'self.ano_indi', self.ano_indi

def compare(f_name):
    data_file = DataFile(f_name,
                settings.DETECTOR_DESC['win_size'],
                settings.DETECTOR_DESC['fea_list'])
    # detect = ModelFreeAnoDetector(settings.DETECTOR_DESC)
    detect = ModelBaseAnoDetector(settings.DETECTOR_DESC)
    detect(data_file)
    detect.plot_entropy()

    detect = ModelFreeAnoDetector(settings.DETECTOR_DESC)
    detect(data_file)
    detect.plot_entropy()
    # type_detector = ModelFreeAnoTypeTest(detect, 3000, settings.ANO_DESC['T'])
    # type_detector.detect_ano_type()

    # import pdb;pdb.set_trace()
    # detect.plot_entropy()

if __name__ == "__main__":
    import sys
    print 'sys.argv, ', sys.argv
    compare(sys.argv[1])
