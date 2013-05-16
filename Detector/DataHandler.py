#!/usr/bin/env python
""" Handler Class for Data Files
"""
from __future__ import print_function, division, absolute_import
__author__ = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"

from .ClusterAlg import KMedians
from .DetectorLib import vector_quantize_states, model_based, model_free
from sadit.util import DF, NOT_QUAN, QUAN
from sadit.util import abstract_method, FetchNoDataException, DataEndException

##############################################################
####                  Interface Class                   ######
##############################################################
class DataHandler(object):
    """ virtual base class for Data Hanlder. Data Handler contains one or more
    Data class as the data source. And it generate the emperical measure based
    on the data class.
    """
    def __init__(self, data, desc):
        self.data = data
        self.desc = desc

    def get_em(self, rg=None, rg_type='time'):
        """get emperical measure within a range. emeprical measure is used to
        represent the data in this range. For example, it can the probability
        distribution of flow quantization state within and range(*for the model
        free case*), or the markovian trantion probability for the *model based*
        case"""
        abstract_method()

from socket import inet_ntoa
from struct import pack
def long_to_dotted(ip):
    ip_addr = inet_ntoa(pack('!L', ip))
    return [int(val) for val in ip_addr.rsplit('.')]

from .DetectorLib import get_feature_hash_list
from sadit.util import izip
class QuantizeDataHandler(DataHandler):
    """ Cluster and IP address and Quantize the feature in the Data

    Parameters
    ----------------
    fea_option : dict
        specified the quantized level for each feature


    Examples
    ---------------
    >>> from .Data import PreloadHardDiskFile
    >>> data = PreloadHardDiskFile('Test/n0_flow.txt')
    >>> fea_option = dict(cluster=2, dist_to_center=2, flow_size=2)
    >>> dh = QuantizeDataHandler(data, dict(fea_option=fea_option))
    finish get ip address
    start KMedians ...
    >>> flows = dh.quantize_fea([0, 100], 'flow')
    >>> print(len(flows))
    3
    >>> print(len(flows[0]))
    100
    """
    def __init__(self, data, desc):
        super(QuantizeDataHandler, self).__init__(data, desc)
        self._init_data(data)
        fea_option = desc['fea_option']
        self.fea_option  = fea_option
        self.direct_fea_list = [ k for k in fea_option.keys() if k not in ['cluster', 'dist_to_center']]
        self.fea_QN = [fea_option['cluster'], fea_option['dist_to_center']] + [fea_option[k] for k in self.direct_fea_list]

        self._cluster_src_ip(fea_option['cluster'])
        self._set_fea_range()

    def _init_data(self, data):
        self.data = data

    # def _to_dotted(self, ip):
    #     if isinstance(ip, str):
    #         return tuple( [int(v) for v in ip.rsplit('.')] )
    #     elif isinstance(ip, long):
    #         return long_to_dotted(int(ip))

    def _cluster_src_ip(self, cluster_num):
        src_ip_int_vec_tmp = self.data.get_rows('src_ip')
        src_ip_vec = [tuple(x) for x in src_ip_int_vec_tmp]
        unique_ip = list( set( src_ip_vec ) )
        # unique_src_cluster, center_pt = KMeans(unique_src_IP_vec_set, cluster_num, DF)
        unique_src_cluster, center_pt = KMedians(unique_ip, cluster_num, DF)
        self.cluster_map = dict(zip(unique_ip, unique_src_cluster))
        # self.center_map = dict(zip(unique_src_IP_vec_set, center_pt))
        dist_to_center = [DF( unique_ip[i], center_pt[ unique_src_cluster[i] ]) for i in xrange(len(unique_ip))]
        self.dist_to_center_map = dict(zip(unique_ip, dist_to_center))

    def get_min_max(self, feas):
        min_vec = []
        max_vec = []
        for fea in feas:
            dat = self.data.get_rows(fea)
            min_vec.append(min(dat))
            max_vec.append(max(dat))
        return min_vec, max_vec

    def _set_fea_range(self):
        """set the global range for the feature list, used for quantization"""
        # set global fea range
        min_dist_to_center = min(self.dist_to_center_map.values())
        max_dist_to_center = max(self.dist_to_center_map.values())

        # min_vec = self.data.get_min(self.direct_fea_list)
        # max_vec = self.data.get_max(self.direct_fea_list)
        min_vec, max_vec = self.get_min_max(self.direct_fea_list)

        self.global_fea_range = [
                [0, min_dist_to_center] + min_vec,
                [self.fea_option['cluster']-1, max_dist_to_center] + max_vec,
                ]

    def get_fea_list(self):
        return ['cluster', 'dist_to_center'] + self.direct_fea_list

    def get_fea_slice(self, rg=None, rg_type=None):
        """get a slice of feature. it does some post-processing after get feature
        slice from Data. First it get *direct_fea_vec* from data, which is defined
        in **self.direct_fea_list**. then it cluster
        the source ip address, and insert the cluster label and distance to the
        cluster center to the feature list.
        """
        # get direct feature
        direct_fea_vec = self.data.get_rows(self.direct_fea_list, rg, rg_type)
        if direct_fea_vec is None:
            raise FetchNoDataException("Didn't find any data in this range")

        # calculate indirect feature
        src_ip = self.data.get_rows('src_ip', rg, rg_type)
        fea_vec = []
        for ip, direct_fea in izip(src_ip, direct_fea_vec):
            fea_vec.append( [self.cluster_map[tuple(ip)],
                self.dist_to_center_map[tuple(ip)]] + [float(x) for x in direct_fea])

        # for i in xrange(len(src_ip)):
            # ip = src_ip[i]
            # fea_vec.append( [self.cluster_map[ip], self.dist_to_center_map[ip]] + [float(x) for x in direct_fea_vec[i]])

        # min_vec = self.data.get_min(self.direct_fea_list, rg, rg_type)
        # max_vec = self.data.get_max(self.direct_fea_list, rg, rg_type)

        # dist_to_center_vec = [self.dist_to_center_map[ip] for ip in src_ip]
        # min_dist_to_center = min(dist_to_center_vec)
        # max_dist_to_center = max(dist_to_center_vec)

        # fea_range = [
        #         [0, min_dist_to_center] + min_vec,
        #         [self.fea_option['cluster']-1, max_dist_to_center] + max_vec,
        #         ]

        # quan_flag specify whether a data need to be quantized or not.
        self.quan_flag = [QUAN] * len(self.fea_option.keys())
        self.quan_flag[0] = NOT_QUAN
        # return fea_vec, fea_range
        return fea_vec

    def get_em(self, rg=None, rg_type=None):
        abstract_method()
        # """get empirical measure"""
        # q_fea_vec = self.quantize_fea(rg, rg_type )
        # pmf = model_free( q_fea_vec, self.fea_QN )
        # Pmb, mpmb = model_based( q_fea_vec, self.fea_QN )
        # return pmf, Pmb, mpmb

    def quantize_fea(self, rg=None, rg_type=None):
        """get quantized features for part of the flows"""
        # fea_vec, fea_range = self.get_fea_slice(rg, rg_type)
        fea_vec = self.get_fea_slice(rg, rg_type)
        q_fea_vec = vector_quantize_states(izip(*fea_vec), self.fea_QN, izip(*self.global_fea_range), self.quan_flag)
        return q_fea_vec

    def hash_quantized_fea(self, rg, rg_type):
        q_fea_vec = self.quantize_fea(rg, rg_type)
        return get_feature_hash_list(q_fea_vec, self.fea_QN)


class ModelFreeQuantizeDataHandler(QuantizeDataHandler):
    def get_em(self, rg, rg_type):
        """get model-free empirical measure"""
        q_fea_vec = self.quantize_fea(rg, rg_type )
        return model_free( q_fea_vec, self.fea_QN )

class ModelBasedQuantizeDataHandler(QuantizeDataHandler):
    def get_em(self, rg, rg_type):
        """get model-based empirical measure"""
        q_fea_vec = self.quantize_fea(rg, rg_type )
        return model_based( q_fea_vec, self.fea_QN )

class FBQuantizeDataHandler(QuantizeDataHandler):
    def get_em(self, rg=None, rg_type=None):
        """get empirical measure"""
        q_fea_vec = self.quantize_fea(rg, rg_type )
        pmf = model_free( q_fea_vec, self.fea_QN )
        # Pmb, mpmb = model_based( q_fea_vec, self.fea_QN )
        Pmb = model_based( q_fea_vec, self.fea_QN )
        return pmf, Pmb
        # return pmf, Pmb, mpmb

#######################################
## SVM Temporal Method Handler   ######
#######################################
from sadit.util import Counter
# try:
#     from collections import Counter
# except ImportError:
#     Counter = False

# import operator
class SVMTemporalHandler(QuantizeDataHandler):
    """Data Hanlder for SVM Temporal Detector approach. It use a set of features
    which will be defined here"""
    def __init__(self, data, desc=None):
        QuantizeDataHandler.__init__(self, data, desc)
        # self._init_data(data)
        self.update_unique_src_ip()
        self.large_flow_thres = 5e1

    def update_unique_src_ip(self):
        """be carefule to update unique src ip when using a new file"""
        src_ip = self.data.get_rows('src_ip')
        src_ip = [tuple(ip) for ip in src_ip]
        self.unique_src_ip = list(set())

    def _init_data(self, data):
        self.data = data

    def get_svm_fea_deprec(self, rg=None, rg_type=None):
        """ suppose m is the number of unique source ip address in this data.
        the feature is 2mx1,
        - the first m feature is the frequency of flows with
        each source ip address,
        - the second m feature is the frequence of larges
        flows whose size is > self.large_flow_thres with each source ip address"""
        src_ip = self.data.get_rows('src_ip', rg, rg_type)
        flow_size = self.data.get_rows('flow_size', rg, rg_type)
        n = len(src_ip)
        src_ip = [tuple(ip) for ip in src_ip]
        ct = Counter(src_ip)
        fea_total_flow = [ct[ip] for ip in self.unique_src_ip]

        # import pdb;pdb.set_trace()
        lf_src_ip = [src_ip[i] for i in xrange(n) if flow_size[i] > self.large_flow_thres]
        ct = Counter(lf_src_ip)
        fea_large_flow = [ct[ip] for ip in self.unique_src_ip]
        return fea_total_flow + fea_large_flow

    def get_svm_fea(self, rg=None, rg_type=None):
        q_fea_vec = self.quantize_fea(rg, rg_type )
        pmf = model_free( q_fea_vec, self.fea_QN )
        # Pmb, mpmb = model_based( q_fea_vec, self.fea_QN )
        svm_fea = pmf + [len(q_fea_vec[0])]
        # svm_fea = [len(q_fea_vec[0])]
        print('svm_fea, ', svm_fea)
        return svm_fea

        # return model_free
        # ct = Counter(hash_quan_fea)
        # q_level_num = reduce(operator.mul, self.fea_QN)
        # svm_fea = [0] * q_level_num
        # for k, v in ct.iteritems():
        #     svm_fea[int(k)] = v
        # print 'svm_fea, ', svm_fea
        # return svm_fea

class FakeDataHandler(object):
    """ This Data Handler do nothing"""
    def __init__(self, data, *args, **kwargs):
        self.data = data


from sadit.util import np
from .DetectorLib import quantize_state

def regularize(val):
    max_ = np.max(val)
    min_ = np.min(val)
    return val if (max_ == min_) else (val - min_) / (max_ - min_)

# FIXME depreciated
class CombinedEM(object):
    """Combined model-free and model-based emperical measure

    list of np.array
    """
    def __init__(self, data=None):
        if data is not None:
            self.data = [(np.array(d) if d is not None else None) for d in data]
        else:
            self.data = None

    def __add__(self, val):
        if self.data is None:
            self.data = [np.array(d) for d in val]
            return self

        for i in xrange(len(self.data)):
            self.data[i] = self.data[i] + val[i]
        return self

    def __div__(self, val):
        for i in xrange(len(self.data)):
            self.data[i] /= val
        return self

    def quantize(self, quan_N):
        quan_EM_list = []
        for i in xrange(len(self.data)):
            dat = self.data[i]
            if dat is None:
                quan_EM = None
            else:
                quan_level = quantize_state(dat.flatten(), quan_N, [0, 1])
                quan_EM = np.array(quan_level).reshape(dat.shape)
            quan_EM_list.append(quan_EM)
        return CombinedEM(quan_EM_list)

    def regularize(self):
        self.data = [(regularize(d) if d is not None else None) for d in self.data]

    @property
    def mf(self):
        return self.data[0]

    @property
    def mb(self):
        return self.data[1], self.data[2]

def flatten(val):
    return None if val is None else val.flatten()

class CombinedEMList(object):
    def __init__(self, em_list=None):
        self.data = [] if em_list is None else em_list

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for d in self.data:
            yield d

    def __getitem__(self, key):
        return self.data[key]

    def quantize(self, g_quan_N):
        self.data = [d.quantize(g_quan_N) for d in self.data]
        self.g_quan_N = g_quan_N

    def append(self, em):
        self.data.append(CombinedEM(em))
        self.mf_shape = None if self.data[-1].mf is None else self.data[-1].mf.shape
        self.mb_shape = None if self.data[-1].mb[0] is None else (self.data[-1].mb[0].shape, self.data[-1].mb[1].shape)

    def regularize(self):
        for d in self.data:
            d.regularize()

# class ModelFreeEM(object):
#     def __init__(self, q_fea_vec, fea_QN):
#         self.q_fea_vec = q_fea_vec
#         self.fea_QN = fea_QN

#     def add(self):
#         pass

#     def get_dist(self):
#         pmf = model_free(zip(*self.q_fea_vec), self.fea_QN)
#         return pmf

# class ModelBasedEM(object):
#     def __init__(self, fea):
#         pass
#     pass

class GeneralizedEMHandler(DataHandler):
    """ Generalized Emperical Measure Handler

    Can Treat the emperical measure caculated by normal data handler as
    feature and calcuale the generalized EM
    """
    def __init__(self, data, desc):
        super(GeneralizedEMHandler, self).__init__(data, desc)
        self.desc = desc
        self.small_win_size = desc['small_win_size']
        self.g_quan_N = desc['g_quan_N']
        self.handler = QuantizeDataHandler(data, desc)

    def quantize_fea(self, rg=None, rg_type=None):
        """get quantized features for part of the flows"""
        fea_vec = self.get_fea_slice(rg, rg_type)
        q_fea_vec = vector_quantize_states(izip(*fea_vec), self.fea_QN,
                izip(*self.global_fea_range), self.quan_flag)
        return q_fea_vec

    def cal_base_em_list(self, rg, rg_type):
        """calculate all the base emperical that will be used as feature"""
        if rg is None:
            rg = [0, float('inf')]

        pt = rg[0]
        em_list = CombinedEMList()

        while pt <= rg[1]:
            try:
                em = self.handler.get_em(
                        rg=[pt, pt+self.small_win_size],
                        rg_type=rg_type)
                # print('t: %i em: %s'%(pt, em))
                em_list.append( em )
                pt += self.small_win_size
            except FetchNoDataException:
                print('there is no data to detect in this window')
            except DataEndException:
                print('reach data end, break')
                if rg[1] != float('inf'):
                    raise
                break

        self.em_list = em_list
        # print('leng, ', len(self.em_list.data))

    def get_em(self, rg, rg_type):
        self.cal_base_em_list(rg, rg_type)
        self.em_list.regularize()
        self.em_list.quantize(self.g_quan_N)

        mf = self.get_mf_dist()
        mb = self.get_mb_dist()
        return mf, mb[0], mb[1]


class QuantizeGeneralizedEMHandler(GeneralizedEMHandler):
    def get_em(self, *args, **kwargs):
        """get generalized emperical measure
        """
        return self.handler.get_em(*args, **kwargs)



""" The following two handlers has the same output with QuantizeDataHandler,
which means it can work with any Detector that receive QuantizeDataHandler,
which includes:
    1. ModelFreeAnoDetector
    2. ModelBaseAnoDetector
    3. FBAnoDetector
    4. PeriodStoDetector
    5. TwoWindowAnoDetector
    6. AutoSelectStoDetector
"""

class ModelFreeFeaGeneralizedEMHandler(GeneralizedEMHandler):
    """ calculate the model free and model based emprical measure when the
    underline feature is model free emperical empeasure
    """
    def get_mf_dist(self):
        """ model free distribution of model free emperical measure
        """
        N = len(self.em_list[0].mf.flatten())
        # return model_free([flatten(em.mf) for em in self.em_list],
        #         [self.g_quan_N]*N)
        print('len self.em_list', len(self.em_list))
        mf = model_free([flatten(em.mf) for em in self.em_list],
                [self.g_quan_N]*N)
        print('mf ', mf )
        return mf

    def get_mb_dist(self):
        """ model free distribution of model free emperical measure
        """
        N = len(self.em_list[0].mf.flatten())
        return model_based([flatten(em.mf) for em in self.em_list],
                [self.g_quan_N]*N)

class ModelBasedFeaGeneralizedEMHandler(GeneralizedEMHandler):
    """ calculate the model free and model based emprical measure when the
    underline feature is model based emperical empeasure
    """
    def get_mf_dist(self):
        """ model free distribution of model based emperical measure
        """
        N = len(self.em_list[0].mb[0].flatten())
        return model_free([flatten(em.mb[0]) for em in self.em_list],
                [self.g_quan_N]*N)

    def get_mb_dist(self):
        """ model based distribution of model based emperical measure
        """
        N = len(self.em_list[0].mb[0].flatten())
        return model_based([flatten(em.mb[0]) for em in self.em_list],
                [self.g_quan_N]*N)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

