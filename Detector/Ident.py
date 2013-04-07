"""Anomalous Flow State or Flow Transition Pair Identification"""
from math import log
# from util import abstract_method
def abstract_method(): raise Exception("abstract_method")

def mean(a, idx_set=None):
    if idx_set:
        a = [a[i] for i in idx_set]
    return sum(a) * 1.0 / len(a);

def argsort(seq):
    """arg sort in descending order"""
    return sorted(range(len(seq)), key=seq.__getitem__, reverse=True)

def get_slice(si, idx_set):
        return [si[i] for i in idx_set]

class FlowStateIdent(object):
    """identify the anomalouse flow state,
    need a series of prob distribution.
    the abnormal window index and anomaly free window
    index.
    """
    def __init__(self, nu_set, mu):
        """P1, P2 are two lists contain the probability distribution """
        assert(isinstance(mu, list) or isinstance(mu, tuple))
        self.nu_set = nu_set
        self.mu = mu
        self._init()

    def _init(self):
        self.detect_num = len(self.nu_set)
        self.state_num = len(self.mu)
        self.info = [self.get_info_state_by_state(nu, self.mu)  for nu in self.nu_set]
        self.state_info = zip(*self.info)

    def get_info_state_by_state(self, nu, mu):
        return [self.info_cal(v1, v2) for v1, v2 in zip(nu, mu)]

    @staticmethod
    def info_cal(v1, v2):
        abstract_method()
        # return 0 if (v1 == 0 or v2 == 0) else v1*log(v1*1.0/v2)

    def set_detect_result(self, detect_result):
        """set the detection result and calculate the state information mean
        for normal state"""
        assert(len(detect_result) == self.detect_num)
        self.ano_free_idx = [ i for i in xrange(self.detect_num) if not detect_result[i]]
        self.norm_state_info_mean = [mean(si, self.ano_free_idx) for si in self.state_info]

    def get_state_likelihood(self, ano_idx_set):
        cal_likelihood = lambda si, norm: abs( mean(si, ano_idx_set) - norm)
        # def cal_likelihood(si, norm):
            # return abs( mean(si, ano_idx_set) - norm)
        self.state_likelihood = [cal_likelihood(si, norm) for si, norm in zip(self.state_info, self.norm_state_info_mean)]
        return self.state_likelihood

    def filter_states(self, ano_idx_set, portion=None, num=None):
        """filter states that may cause the anomaly represetned by *ano_idx_set*,
        you can either set *portion* of state that may be anomalous
        for the *number* that may be anomalouse. the priority of *portion*
        parameter is higher than the priority of *num*"""
        if portion:
            num = int(self.detect_num * portion)
        state_likelihood = self.get_state_likelihood(ano_idx_set)
        sort_idx = argsort(state_likelihood)
        return sort_idx[:num]

class ComponentFlowStateIdent(FlowStateIdent):
    """use component to identify the flow state"""
    @staticmethod
    def info_cal(v1, v2):
        return 0 if (v1 == 0 or v2 == 0) else v1*log(v1*1.0/v2)

class DerivativeFlowStateIdent(FlowStateIdent):
    """use the derivative to identify the flow state"""
    @staticmethod
    def info_cal(v1, v2):
        return 0 if (v1 == 0 or v2 == 0) else log(v1*1.0/v2) + 1

import itertools
class FlowPairIdent(FlowStateIdent):
    def get_info_state_by_state(self, nu, mu):
        m_nu = [sum(p) for p in nu]
        m_mu = [sum(p) for p in mu]
        res = []
        for i in xrange(self.n):
            for j in xrange(self.n):
                res.append( self.info_cal(nu[i][j], m_nu[j], mu[i][j], m_mu[j]) )
        return res

    @staticmethod
    def info_cal(a, ma, b, mb):
        # return a * log( (a*1.0/ma) / (b*1.0/mb))
        abstract_method()

    def sub2idx(self, i, j):
        return i * self.n + j
    def idx2sub(self, idx):
        return idx / self.n, idx % self.n

    def flatten(self, m):
        return itertools.chain(*m)

    def _init(self):
        self.detect_num = len(self.nu_set)
        assert( len(self.mu) == len(self.mu[0]) )
        self.state_num = len(self.mu) * len(self.mu[0])
        self.n = len(self.mu)
        # self.info = [self.get_info_state_by_state(self.flatten(nu), self.flatten(mu)) for nu in nu_set]
        self.info = [self.get_info_state_by_state(nu, self.mu) for nu in self.nu_set]
        self.state_info = zip(*self.info)

    def filter_states(self, ano_idx_set, portion=None, num=None):
        state_idx = super(FlowPairIdent, self).filter_states(ano_idx_set, portion, num)
        return [self.idx2sub(idx) for idx in state_idx]

class componentflowpairident(FlowPairIdent):
    @staticmethod
    def info_cal(a, ma, b, mb):
        return 0 if (a == 0 or ma ==0 or b == 0 or mb == 0) else a * log( (a*1.0/ma) / (b*1.0/mb))

class DerivativeFlowPairIdent(FlowPairIdent):
    @staticmethod
    def info_cal(a, ma, b, mb):
        return  0 if (a == 0 or ma ==0 or b == 0 or mb == 0) else log( (a*1.0/ma) / (b*1.0/mb))
