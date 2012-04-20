import numpy as np
from util import abstract_method
from Derivative import ModelFreeDerivative, ModelBaseDerivative

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


class AnoTypeTest(object):
    def __init__(self, detector, total_t, ano_t):
        self.detector = detector
        self.total_t = total_t
        self.ano_t = ano_t

    def get_ano_indi(self):
        return CalIndicator(self.deri, self.get_interval_ratio())

    def get_interval_ratio(self):
        return [self.ano_t[0] * 1.0/self.total_t, self.ano_t[1] * 1.0/self.total_t]

    def get_em_vec(self):
        return [ em for em in self.detector.record_data['em'] ]

    def detect_ano_type(self): abstract_method()

class ModelFreeAnoTypeTest(AnoTypeTest):
    def detect_ano_type(self):
        norm_em = self.detector.norm_em
        self.deri = [ ModelFreeDerivative(d_pmf, norm_em) for d_pmf in self.get_em_vec() ]
        print 'self.deri', self.deri
        self.ano_indi = self.get_ano_indi()
        print 'self.ano_indi', self.ano_indi

class ModelBaseAnoTypeTest(AnoTypeTest):
    def detect_ano_type(self):
        norm_em = self.detector.norm_em
        self.deri = [ ModelBaseDerivative(d_pmf, norm_em) for d_pmf in self.get_em_vec() ]
        self.ano_indi = self.get_ano_indi()
