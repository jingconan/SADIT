#!/usr/bin/env python
import sys
sys.path.append("..")
import settings
# from Derivative import *
# from DetectorLib import get_feature, I1, I2, SL, get_all_pmf, gen_norminal_pdf, get_flow_rate, get_dist_to_center, vector_quantize_states, model_based, model_free
from DetectorLib import I1, I2, get_dist_to_center, vector_quantize_states, model_based, model_free
# from DetectorLib import ModelFreeDerivative, ModelBaseDerivative, CleanGlobalDeri, PlotModelFree, PlotModelBase

# from util import *
from util import np, Find
from matplotlib.pyplot import figure, plot, subplot, show
import cPickle as pickle

from ClusterAlg import KMeans
# The Distance Function
DF = lambda x,y:abs(x[0]-y[0]) * (256**3) + abs(x[1]-y[1]) * (256 **2) + abs(x[2]-y[2]) * 256 + abs(x[3]-y[3])
from DataParser import ParseData
from operator import itemgetter
import copy
# from sets import Set

QUAN = 1
NOT_QUAN = 0

class DataEndException(Exception):
    pass

class DataFile(object):
    """from file to feature"""
    __slots__ = ['f_name', 'flow', 'cluster', 'center_pt', 'fea', 'fea_range','fea_vec', 'norm_range',
            'unique_src_IP_vec_set', 'src_IP_vec_set', 'cluster_num', 'fr_win_size', 'unique_src_cluster',
            'fea_list', 'fea_handler_map', 'quan_flag', 'fea_QN', 't']

    def __init__(self, f_name, cluster_num, fr_win_size, fea_list):
        self.fea_handler_map = {
            'flow_rate':[ self.get_flow_rate, QUAN ],
            'dist_to_center':[ self.get_dist_to_center, QUAN ],
            'flow_size':[ self.get_flow_size, QUAN ],
            'cluster':[ self.get_cluster, NOT_QUAN ],
            }
        for k in self.fea_handler_map.iterkeys():
            self.fea_handler_map[k].append( fea_list.get(k) )


        self.f_name = f_name
        self.cluster_num = cluster_num
        self.fr_win_size = fr_win_size
        self.fea_list = fea_list.keys()

        self.parse()
        self._cluster_src_ip()
        self.init_flow_src_cluser()
        self.gen_fea()


        self.norm_range = None

    def __add__(self, other):
        """addition of two data files. use for multi files. """
        new_file = copy.deepcopy(self)
        new_file.flow += other.flow
        new_file.sort_flow('t')
        new_file._cluster_src_ip()
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
        self.fea_vec = np.array( self.fea.values() ).T
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
            return self.fea_vec[rg, :]
        elif rg_type == 'time':
            sp = Find(self.t, rg[0])
            ep = Find(self.t, rg[1])
            assert(sp != -1 and ep != -1)
            if (sp == len(self.t)-1 or ep == len(self.t)-1):
                raise DataEndException()
            return self.fea_vec[sp:ep, :]
        else:
            raise ValueError('unknow window type')

    def get_fea_range(self):
        self.fea_range = dict()
        for k, v in self.fea.iteritems():
            self.fea_range[k] = [min(v), max(v)]
        return self.fea_range

    def get_fea_range_vec(self):
        return np.array( self.get_fea_range().values() ).T


    def quantize_fea(self, rg=None, rg_type='time'):
        fea_vec = self.get_fea_slice(rg, rg_type)
        fea_range = self.get_fea_range_vec()
        q_fea_vec = vector_quantize_states(list(fea_vec.T), self.fea_QN, list(fea_range.T), self.quan_flag)
        return q_fea_vec

    def get_em(self, rg=None, rg_type='time'):
        """get empirical measure"""
#FIXME move this to data_file
        q_fea_vec = self.quantize_fea(rg, rg_type )
        pmf = model_free( q_fea_vec, self.fea_QN )
        Pmb, mpmb = model_based( q_fea_vec, self.fea_QN )
        return pmf, Pmb, mpmb

    ### Function For Extracting Features ###
    def get_cluster(self): return self.cluster
    def get_flow_size(self): return self.get_value_list('flowSize')

    def _get_flow_src_cluster(self, f):
        idx = self.unique_src_IP_vec_set.index(f['srcIPVec'])
        return self.unique_src_cluster[idx]

    def init_flow_src_cluser(self):
        self.cluster = [ self._get_flow_src_cluster(f) for f in self.flow ]

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
    def __init__(self, **desc):
        self.desc = desc
        self.record_data = dict(IF=[], IB=[], winT=[], threshold=[])
        self.data_file = []

    def __call__(self, *args, **kwargs):
        return self.detect(*args, **kwargs)

    def record(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.record_data[k].append(v)

    def reset_record(self):
        for k, v in self.record_data.iteritems():
            self.record_data[k] = []

    def detect(self, fName):
        self.data_file = DataFile(fName, cluster_num=2,
                fr_win_size=100,
                # fea_list={'flow_rate':2, 'dist_to_center':2, 'flow_size':2, 'cluster':2},
                fea_list={'dist_to_center':2, 'flow_size':2, 'cluster':2},
                )

        ### Generate Nominal PDF ###
        pmf, Pmb, mpmb = self.data_file.get_em(rg=[0, 1000], rg_type='time')

        wSize = self.desc['win_size']
        interval = self.desc['interval']
        # t = self.data_file.t
        time = self.desc['fr_win_size']

        # CleanGlobalDeri()
        while True:
            print 'time: %f' %(time)
            try:
                d_pmf, d_Pmb, d_mpmb = self.data_file.get_em(rg=[time, time+wSize], rg_type='time')
            except DataEndException:
                print 'reach data end, break'
                break
            time += interval

            mfEntro = I1(d_pmf, pmf)
            mbEntro = I2(d_Pmb, d_mpmb, Pmb, mpmb)

            self.record(
                    IF = mfEntro,
                    IB = mbEntro,
                    winT = time,
                    threshold = 0 # Hoeffding test threshold
                    )

            # Identify the Most significant state transition for model-base case
            # modelFreeDeri= ModelFreeDerivative(d_pmf, pmf)
            # modelBaseDeri = ModelBaseDerivative(d_Pmb, d_mpmb, Pmb, mpmb)
            # util.Dump2Txt(deri, './deri.res', '2dnp')

        # DumpDerivative()
        # if settings.PLOT_DERIVATIVE:
            # PlotModelBase()
            # PlotModelFree()

        return self.record_data

    def plot_entropy(self):
        t2 = self.record_data['winT']
        mt = min(t2)
        rt = [t-mt for t in t2]
        figure()
        subplot(211)
        plot(rt, self.record_data['IF'])
        subplot(212)
        plot(rt, self.record_data['IB'])
        show()

    def dump(self, data_name):
        pickle.dump( self.record_data, open(data_name, 'w') )

    def get_feature(self):
        self.data = [ DataFile(fn) for fn in self.data_file_name ]

    # def get_feature_nominal_pmf(self, feaQN, fName):
        # if self.desc['unified_nominal_pdf']:
            # pmf, Pmb, mpmb, feaRange = pickle.load(open(NominalPDFFile, 'r'))
            # feaVec, feaRange, quanFlag, t, centerPt = get_feature(fName)
        # else:
            # pmf, Pmb, mpmb, feaVec, feaQN, feaRange,  quanFlag, t, centerPt = gen_norminal_pdf(fName, feaQN)
        # return feaRange, feaVec, quanFlag, pmf, t, Pmb, mpmb

# def ModelFreeDetector(AnoDetector):
#     def get_em(self, data_file, rg=None, rg_type='t'):
#         q_fea_vec = self.quantize_fea(data_file, rg, rg_type)
#         pmf = model_free(qFeaVec, fea_QN)
#         return pmf

# def ModelBaseDetector(AnoDetector):
#     def get_em(self, data_file, rg=None, rg_type='t'):
#         q_fea_vec = self.quantize_fea(data_file, rg, rg_type)
#         Pmb, mpmb = model_based(qFeaVec, fea_QN)
#         return Pmb, mpmb

def compare(fName):
    detect = AnoDetector(**settings.DETECTOR_DESC)
    detect(fName)
    detect.plot_entropy()

if __name__ == "__main__":
    import sys
    print 'sys.argv, ', sys.argv
    compare(sys.argv[1])
