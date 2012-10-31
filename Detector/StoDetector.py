#!/usr/bin/env python
"""
This file contains all the stochastic detection techniques
"""
__author__ = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"
__status__ = "Development"

import os
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = False

from DetectorLib import I1, I2
from util import DataEndException, FetchNoDataException, abstract_method
from mod_util import plot_points

import cPickle as pickle
from math import log
# import argparse
# from Base import BaseDetector
from Base import WindowDetector

class StoDetector (WindowDetector):
    """It is an Abstract Base Class for the anomaly detector."""
    def __init__(self, desc):
        self.desc = desc
        self.record_data = dict(entropy=[], winT=[], threshold=[], em=[])

    def __call__(self, *args, **kwargs):
        return self.detect(*args, **kwargs)

    def get_em(self, rg, rg_type):
        """abstract method. Get empirical measure,
        rg is a list specify the start and the end point of the data
            that will be used
        rg_type is the type of the rg, can be ['flow'|'time']"""
        abstract_method()

    def init_parser(self, parser):
        """ entropy_th specify the threshold manually.
        hoeff_far and ccoef are the parameter of hoeffding threshold rule.
        Increase hoeff_far will decrease threshold
        Increase ccoef will increase threshold
        A small window size will make hoeff_far play more role, while a larger
        window size will let ccoef more significant.
        """
        super(StoDetector, self).init_parser(parser)
        parser.add_argument('--hoeff_far', default=0.01, type=float,
                help="""false alarm rate for hoeffding rule, if this parameter is set while
                entropy_th parameter is not set, will calculate threshold according to
                hoeffding rule. Increase hoeff_far will decrease threshold""")

        parser.add_argument('--entropy_th', default=None, type=float,
                help='entropy threshold to determine the anomaly, has \
                higher priority than hoeff_far')

        parser.add_argument('--ccoef', default=30.0, type=float,
                help="""correction coefficient for calculat threshold using hoeffding rule.
                hoeffding threshold is only a asymotical result. An O(n) linear term has been
                abandon during the analysis, however, it practice, this term is important. You
                need run on some test data set to deterine an approraite correction coefficient
                first. Increase ccoef will increase threshold.
                """)


    def I(self, em1, em2):
        """abstract method to calculate the difference of two
        empirical measure"""
        abstract_method()

    def get_flow_num(self, rg, rg_type):
        sp, ep = self.data_file.data._get_where([st, st+win_size], rg_type)
        return ep - sp

    def record(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.record_data[k].append(v)

    def reset_record(self):
        for k, v in self.record_data.iteritems():
            self.record_data[k] = []

    # def detect(self, data_file, nominal_rg = [0, 1000], rg_type='time',  max_detect_num=None):
    def detect(self, data_file):
        """main function to detect. it will slide the window, get the emperical
        measure and get the indicator"""
        nominal_rg = self.desc['normal_rg']
        rg_type = self.desc['win_type']
        max_detect_num = self.desc['max_detect_num']

        self.data_file = data_file
        self.norm_em = self.get_em(rg=nominal_rg, rg_type=rg_type)

        win_size = self.desc['win_size']
        interval = self.desc['interval']

        time = self.desc['fr_win_size'] if ('flow_rate' in self.desc['fea_option'].keys()) else 0

        i = 0
        while True:
            i += 1
            if max_detect_num and i > max_detect_num:
                break
            if rg_type == 'time' : print 'time: %f' %(time)
            else: print 'flow: %s' %(time)

            try:
                self.rg = [time, time+win_size] # For two window method
                em = self.get_em(rg=[time, time+win_size], rg_type=rg_type)
                entropy = self.I(em, norm_em=self.norm_em)
                self.record( entropy=entropy, winT = time, threshold = 0, em=em)
            except FetchNoDataException:
                print 'there is no data to detect in this window'
            except DataEndException:
                print 'reach data end, break'
                break

            time += interval

        self.detect_num = i - 1
        # import pdb;pdb.set_trace()

        # get the threshold:
        # if self.args.entropy_th is not None:
        if self.desc.get('entropy_th') is not None:
            # import pdb;pdb.set_trace()
            self.record_data['threshold'] = [self.args.entropy_th] * self.detect_num
        # elif self.args.hoeff_far is not None:
        elif self.desc.get('hoeff_far') is not None:
            self.record_data['threshold'] = self.get_hoeffding_threshold(self.desc['hoeff_far'])
        else:
            self.record_data['threshold'] = None
        # record the parameters
        # self.record_data['args'] = self.args
        self.record_data['desc'] = self.desc

        return self.record_data
    def hoeffding_rule(self, n, false_alarm_rate):
        """hoeffding rule with linear correction term
        """
        # return -1.0 / n * log(false_alarm_rate) + self.desc['ccoef'] * log(n) / n
        # import pdb;pdb.set_trace()
        # print('ccoef, ', self.desc['ccoef'])
        return -1.0 / n * log(false_alarm_rate) + self.desc['ccoef'] / n

    def get_hoeffding_threshold(self, false_alarm_rate):
        """calculate the threshold of hoeffiding rule,
        threshold = -1 / |G| log(epsilon) where |G| is the number of flows in the window
        and epsilon is the false alarm_rate
        """
        res = []
        for i in xrange(self.detect_num):
            flow_seq = self._get_flow_seq(i)
            flow_num_in_win = flow_seq[1] - flow_seq[0] + 1
            threshold = self.hoeffding_rule(flow_num_in_win, false_alarm_rate)
            res.append(threshold)

        return res

    def _get_flow_seq(self, win_idx):
        """Get the starting and ending sequence number of all flows in this window
        """
        rg_type = self.desc['win_type']
        win_size = self.desc['win_size']
        interval = self.desc['interval']
        if rg_type == 'time':
            # import pdb;pdb.set_trace()
            st = self.record_data['winT'][win_idx]
            sp, ep = self.data_file.data._get_where([st, st+win_size], rg_type)
        elif rg_type == 'flow':
            sp = interval * win_idx
            ep = interval * (win_idx+1)
        else:
            raise Exception('unknow rg type')

        return sp, ep

    # def plot(self, far=None, *args, **kwargs):
    def plot(self, *args, **kwargs):
        rt = self.record_data['winT']
        ep = self.record_data['entropy']
        # import pdb;pdb.set_trace()
        threshold = self.record_data['threshold']
        plot_points(rt, ep, threshold,
                xlabel_=self.desc['win_type'], ylabel_= 'entropy',
                *args, **kwargs)

    def dump(self, data_name):
        pickle.dump( self.record_data, open(data_name, 'w') )
        # pickle.dump(self.__dict__, open(data_name, 'w') )

    def plot_dump(self, data_name, *args, **kwargs):
        """plot dumped data
        """
        self.record_data = pickle.load(open(data_name, 'r'))
        # data = pickle.load(open(data_name, 'r'))
        # self.__dict__.update(data)
        self.plot(*args, **kwargs)

    @staticmethod
    def find_abnormal_windows(entropy, entropy_threshold=None, ab_win_portion=None, ab_win_num=None):
        """find abnormal windows. There are three standards to select abnormal windows:
            1. when the entropy >= entropy_threshold. when entropy_threshold is a list. the length of entropy_threshold should
                equals the length of entropy. The element in this list is the entropy threshold for window with corresponding position.
            2. when it is winthin the top *portion* of entropy, 0 <= *portion* <= 1
            3. when it is the top *sel_num* of entropy
        the priority of 1 > 2 > 3.
        """
        num = len(entropy)
        if not entropy_threshold:
            if ab_win_portion:
                ab_win_num = int( num * ab_win_portion )
            sorted_entropy = sorted(entropy)
            entropy_threshold = sorted_entropy[-1*ab_win_num]
        if isinstance(entropy_threshold, list):
            assert(len(entropy_threshold) == num)
            return [ i for i in xrange(num) if entropy[i] >= entropy_threshold[i] ]
        else:
            return [ i for i in xrange(num) if entropy[i] >= entropy_threshold ]

    def _export_ab_flow_entropy(self, entropy, fname,
            entropy_threshold=None, ab_win_portion=None, ab_win_num=None):
        """export abnormal flows based on entropy
        - **entropy** is a list of entropy, one number for each window
        - **fname** is the output abnormal flow file name
        - **entropy_threshold**, **ab_win_portion** and **ab_win_num** are criterion
        to identifi abnormal window, see docs of *find_abnormal_windows* for detailed meaning
        """

        ab_idx = self.find_abnormal_windows(entropy, entropy_threshold, ab_win_portion, ab_win_num)

        fid = open(fname, 'w')
        rg_type = self.desc['win_type']
        win_size = self.desc['win_size']
        interval = self.desc['interval']
        st = 0
        seq = -1
        for idx in ab_idx:
            seq += 1
            st = self.record_data['winT'][idx] if rg_type == 'time' else (interval * idx)
            # import pdb;pdb.set_trace()
            # data, _ = self.data_file.get_fea_slice([st, st+win_size], rg_type)
            data = self.data_file.get_fea_slice([st, st+win_size], rg_type)
            sp, ep = self.data_file.data._get_where([st, st+win_size], rg_type)
            fid.write('Seq # [%i] for abnormal window: [%i], entropy: [%f], start time [%f]\n'%(seq, idx, entropy[idx], st))
            i = sp-1
            for l in data:
                i += 1
                data_str = '\t'.join( ['%s - %f'%tuple(v) for v in zip(self.data_file.get_fea_list(), l)] )
                fid.write('Sample # %i\t%s\n'%(i, data_str))

        fid.close()

class ModelFreeAnoDetector(StoDetector):
    """Model Free approach, use I.I.D Assumption
    """
    def I(self, d_pmf, pmf):
        return I1(d_pmf, pmf)

    def get_em(self, rg, rg_type):
        """get empirical measure"""
        pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
        # return pmf, Pmb, mpmb
        return pmf

class ModelBaseAnoDetector(StoDetector):
    """ Model based approach, use Markovian approach
    """
    def I(self, em, norm_em):
        d_Pmb, d_mpmb = em
        Pmb, mpmb = norm_em
        return I2(d_Pmb, d_mpmb, Pmb, mpmb)

    def get_em(self, rg, rg_type):
        pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
        return Pmb, mpmb


from Ident import *
class FBAnoDetector(StoDetector):
    """model free and model based together, will be faster then run model free
    and model based approaches separately since some intemediate results are reused.
    """
    def I(self, em, norm_em):
        d_pmf, d_Pmb, d_mpmb = em
        pmf, Pmb, mpmb = norm_em
        return I1(d_pmf, pmf), I2(d_Pmb, d_mpmb, Pmb, mpmb)

    def get_em(self, rg, rg_type):
        """get empirical measure"""
        pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
        return pmf, Pmb, mpmb

    def _save_gnuplot_file(self):
        res_f_name = './res.dat'
        fid = open(res_f_name, 'w')
        rt = self.record_data['winT']
        mf, mb = zip(*self.record_data['entropy'])
        for i in xrange(len(rt)):
            fid.write("%f %f %f\n"%(rt[i], mf[i], mb[i]))
        fid.close()

    def plot(self, far=None, figure_=None, subplot_=[211, 212], title_=['model free', 'model based'],
            pic_name=None, pic_show=False,
            *args, **kwargs):
        # if not VIS: self._save_gnuplot_file(); return;
        if not plt: self._save_gnuplot_file(); return;

        rt = self.record_data['winT']
        mf, mb = zip(*self.record_data['entropy'])
        threshold = self.record_data['threshold']

        if figure_ is None: figure_ = plt.figure()
        plot_points(rt, mf, threshold,
                figure_ = figure_,
                xlabel_=self.desc['win_type'], ylabel_= 'entropy',
                subplot_ = subplot_[0],
                title_ = title_[0],
                pic_name=None, pic_show=False,
                *args, **kwargs)
        plot_points(rt, mb, threshold,
                figure_ = figure_,
                xlabel_=self.desc['win_type'], ylabel_= 'entropy',
                subplot_ = subplot_[1],
                title_ = title_[1],
                pic_name=None, pic_show=False,
                *args, **kwargs)
        if pic_name: plt.savefig(pic_name)
        if pic_show: plt.show()

    def export_abnormal_flow(self, fname, entropy_threshold=None, ab_win_portion=None, ab_win_num=None):
        """
        export the abnormal flows for abnormal windows based on model_free entropy and model_based entropy
        see **AnoDetector.export_abnormal_flow** for the meaning of the parameters.
        """
        mf, mb = zip(*self.record_data['entropy'])
        # select portion of the window to be abnormal
        dirname = os.path.dirname(fname)
        basename = os.path.basename(fname)

        # for model free entropy
        self._export_ab_flow_entropy(mf, dirname + '/mf-' + basename, entropy_threshold, ab_win_portion, ab_win_num)

        # for model based entropy
        self._export_ab_flow_entropy(mb, dirname + '/mb-' + basename, entropy_threshold, ab_win_portion, ab_win_num)

    def get_ab_flow_seq(self, entropy_type, entropy_threshold=None, ab_win_portion=None, ab_win_num=None,
            ab_flow_info = None):
            # ab_flow_state=None, ab_flow_tran=None):
        """get abnormal flow sequence number. the input is citerions which window will be abnormal window
        see **AnoDetector.export_abnormal_flow** for the meaning of the citerion parameters.
        **ab_flow_info** represents either abnormal flow state(for model free approach) and abnormal flow trantision
        pair(for model based approach).
        """
        # assert( (ab_flow_state and not ab_flow_tran) or (not ab_flow_state and ab_flow_tran) )
        # if ab_flow_tran: # set the flow_state be the set of all
            # ab_flow_state = set.union(set([tran[0] for tran in ab_flow_tran]), [tran[1] for tran in ab_flow_tran])

        mf, mb = zip(*self.record_data['entropy'])
        ab_idx = self.find_abnormal_windows(locals()[entropy_type], entropy_threshold, ab_win_portion, ab_win_num)
        # ab_idx = self.find_abnormal_windows(mf, entropy_threshold, ab_win_portion, ab_win_num)
        self.ab_win_idx = ab_idx
        ano_flow_seq = []
        for idx in ab_idx:
            st, ed = self._get_flow_seq(idx)
            # only select those flows belongs to
            # abnormal flow stat or abnormal flow trainsition
            # rg_type = self.desc['win_type']
            # quan_level = self.data_file._quantize_fea([st, ed], rg_type='flow')
            quan_level = self.data_file.hash_quantized_fea([st, ed], rg_type='flow') # TODO, st, ed is alread flow idx, so use 'flow' as rg_type
            # if ab_flow_state:
            if ab_flow_info is None:
                ano_flow_seq += range(st, ed)
                continue
            if not len(ab_flow_info):
                continue

            if entropy_type == 'mf':
                win_ab_flow_seq = [i+st for i in range(0, ed-st) if quan_level[i] in ab_flow_info]
            else:
                ano_tran_set = [(i+st, i+st+1) for i in range(0, ed-st-1) if (quan_level[i], quan_level[i+1]) in ab_flow_info]
                if ano_tran_set:
                    win_ab_flow_seq_raw = [set(flow_states) for flow_states in zip(*ano_tran_set)]
                    win_ab_flow_seq = set.union(*win_ab_flow_seq_raw)
                else:
                    win_ab_flow_seq = []

            ano_flow_seq += win_ab_flow_seq

        return ano_flow_seq

    def ident(self, ident_type, entropy_type, portion=None, ab_states_num=None,
            entropy_threshold=None, ab_win_portion=None, ab_win_num=None):
        """ Identificate the anomalous flow state or flow transition pair
        - **ident_type** can be any Identification Class in Ident.py
        - **entropy_type** can be ['mf'|'mb']. 'mf' will identify the flow state, and 'mb' will identify the flow
                transition pair.
        - **portion** is the portion of flow state that will be selected as anomalous.
        - **ab_states_num** is the number of flow states that will be selected as anomalous. **portion** has higher priority
            than **ab_states_num**
        """
        em_record_set = self.record_data['em']
        def tran_to_joint(tp, mar):
            """input is transition probability, margin probability,
            out put is the joint probability distribution"""
            res = []
            for tp, m in zip(tp,mar):
                res.append([m*p for p in tp])
            return res

        def get_nu_set(em_record_set, entropy_type):
            if entropy_type == 'mf':
                return [em[0] for em in em_record_set]
            elif entropy_type == 'mb':
                return [tran_to_joint(em[1], em[2]) for em in em_record_set]

        nu_set = get_nu_set(em_record_set, entropy_type)
        mu = get_nu_set([self.norm_em], entropy_type)[0]
        ident = globals()[ident_type](nu_set, mu)
        mf, mb = zip(*self.record_data['entropy'])
        ab_idx = self.find_abnormal_windows(locals()[entropy_type], entropy_threshold, ab_win_portion, ab_win_num)
        ident.set_detect_result([(1 if i in ab_idx else 0) for i in xrange(len(nu_set))])
        return ident.filter_states(ab_idx, portion, ab_states_num)

    # def get_ab_flow_seq_mb(self, entropy_threshold=None, ab_win_portion=None, ab_win_num=None):
        # mf, mb = zip(*self.record_data['entropy'])
        # ab_idx = self.find_abnormal_windows(mb, entropy_threshold, ab_win_portion, ab_win_num)
        # ano_flow_seq = []
        # for idx in ab_idx:
            # st, ed = self._get_flow_seq(idx)
            # ano_flow_seq += range(st, ed)

        # return ano_flow_seq

    # def get_ab_flow_seq(self, entropy_threshold=None, ab_win_portion=None, ab_win_num=None):
    #     mf, mb = zip(*self.record_data['entropy'])
    #     ab_idx = self.find_abnormal_windows(mf, entropy_threshold, ab_win_portion, ab_win_num)
    #     ano_flow_seq = []
    #     for idx in ab_idx:
    #         st, ed = self._get_flow_seq(idx)
    #         ano_flow_seq += range(st, ed)

    #     return ano_flow_seq

""" The following part contains several algorithms that select normal emperical
measure in a novel way
"""
class DynamicStoDetector(FBAnoDetector):
    """Base Class for All Dynamic Stochasic Detector
    """
    def I(self, em, **kwargs):
        d_pmf, d_Pmb, d_mpmb = em
        self.desc['em'] = em
        pmf, Pmb, mpmb = self.cal_norm_em(**kwargs)
        return I1(d_pmf, pmf), I2(d_Pmb, d_mpmb, Pmb, mpmb)

    def cal_norm_em(self, **kwargs):
        self.desc.update(kwargs)


class TwoWindowAnoDetector(DynamicStoDetector):
    """ Two Window Stochastic Anomaly Detector
    """
    def init_parser(self, parser):
        super(TwoWindowAnoDetector, self).init_parser(parser)
        parser.add_argument('--norm_win_ratio', default=5.0, type=float,
                help=""" the ratio of normal window with the detection window size.
                """)

    def cal_norm_em(self, **kwargs):
        """ Use emperical measure of large window as nominal emperical measure.
        """
        super(TwoWindowAnoDetector, self).cal_norm_em(**kwargs)

        norm_em = self.desc['norm_em']
        norm_win_size = self.desc['norm_win_ratio'] * self.desc['win_size']
        # st = self.rg[0] - norm_win_size if (self.rg[0] > norm_win_size ) else 0
        if self.rg[0] > norm_win_size:
            norm_rg = [self.rg[0] - norm_win_size, self.rg[0]]
            norm_win_em = self.get_em(rg=norm_rg, rg_type=self.desc['win_type'])
        else:
            norm_win_em = norm_em

        return norm_win_em

import numpy as np
class EM(object):
    """emperical measure
    """
    def __init__(self, data=None):
        if data is not None:
            self.data = [np.array(d) for d in data]
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


class PeriodStoDetector(DynamicStoDetector):
    """Stochastic Detector Designed to Detect Anomaly when the
    normal behaviour change periodically

    """
    def init_parser(self, parser):
        super(PeriodStoDetector, self).init_parser(parser)
        parser.add_argument('--period', default=1000.0, type=float,
                help="""the period of underlying traffic""")

    def cal_norm_em(self, **kwargs):
        super(PeriodStoDetector, self).cal_norm_em(**kwargs)

        norm_em = self.desc['norm_em']

        i = -1 if norm_em is None else 0
        norm_win_em = EM(norm_em)

        period = self.desc['period']
        while True:
            i += 1
            try:
                norm_rg = [self.rg[0] + i * period, self.rg[1] + i * period] #FIXME need to look back
                # import ipdb;ipdb.set_trace()
                norm_win_em = norm_win_em + self.get_em(rg=norm_rg, rg_type=self.desc['win_type'])
            except FetchNoDataException:
                break
            except DataEndException:
                break
        j = 0
        while True:
            i += 1
            j -= 1
            if self.rg[0] + j * period < 0:
                break
            try:
                norm_rg = [self.rg[0] + j * period, self.rg[1] + j * period] #FIXME need to look back
                norm_win_em = norm_win_em + self.get_em(rg=norm_rg, rg_type=self.desc['win_type'])
            except FetchNoDataException:
                break
            except DataEndException:
                break

        norm_win_em = norm_win_em / i
        norm_win_em = norm_win_em.data

        return norm_win_em

    # def plot(self, *args, **kwargs):
    #     rt = self.record_data['winT']
    #     ep = self.record_data['entropy']
    #     i = -1
    #     for v in rt:
    #         i += 1
    #         if v > 3000:
    #             break
    #     threshold = self.record_data['threshold']
    #     plot_points(rt[:i], ep[:i], threshold,
    #             xlabel_=self.desc['win_type'], ylabel_= 'entropy',
    #             *args, **kwargs)


class DummyShiftWindowDetector(DynamicStoDetector):
    """ For data in window i, simply using the data in widnow i-shift to
    calculate norm_em
    """
    def init_parser(self, parser):
        parser.add_argument('--shift', default=0, type=int,
                help="""shift for the window used as reference traffic""")

    def cal_norm_em(self, **kwargs):
        """ For data in window i, simply using the data in widnow i-shift to
        calculate norm_em
        """
        super(DummyShiftWindowDetector, self).cal_norm_em(**kwargs)
        norm_em = self.desc['norm_em']
        win_size = self.desc['win_size']
        shift = self.desc['shift']
        assert(self.rg[1] - self.rg[0] == win_size)
        norm_rg = [self.rg[0] - shift * win_size, self.rg[1] - shift * win_size]
        norm_win_em = self.get_em(rg=norm_rg, rg_type=self.desc['win_type'])
            # norm_win_em = norm_em

        return norm_win_em



from DetectorLib import entropy
class AutoSelectStoDetector(DynamicStoDetector):
    """ Auto Select Suitable Nomral emperical measure
    """
    def __init__(self, desc):
        super(AutoSelectStoDetector, self).__init__(desc)
        self.det = {
                'period': PeriodStoDetector(desc),
                '2w': TwoWindowAnoDetector(desc),
                'shift': DummyShiftWindowDetector(desc),
                }
        self.det_para_name = {
                'period':'period',
                '2w':'norm_win_ratio',
                'shift':'shift',
                }
    def init_parser(self, parser):
        pass
        # for k, v in self.det.iteritems():
        #     v.init_parser(parser)
    def detect(self, data_file):
        self.process_history_data(data_file)
        super(AutoSelectStoDetector, self).detect(data_file)

    def cal_entropy(self, em):
        """calculate entropy for a single emperical measure
        """
        if em is None:
            return float('inf'), float('inf')

        pmf, Pmb, mpmb = em
        pmf = np.array(pmf) / np.sum(pmf)
        mf_entro = entropy(pmf)
        Pmb = np.array(Pmb) / np.sum(Pmb)
        mb_entro = entropy(pmf.reshape(-1,))
        return mf_entro, mb_entro

    def process_history_data(self, history_file):
        win_size = self.desc['win_size']

        pn = self.det_para_name
        data = {
                # 'period':[1e3, 2e3, 1.5e3],
                # 'period':[4e3],
                'period': 1e3 * np.arange(0.2, 4, 0.1),
                # 'norm_win_ratio':[3, 500],
                'norm_win_ratio':range(1, 10),
                # 'shift':[1, 2, 3, 4, 5],
                # 'shift':[-1, -2, -3, -4, -5, -6, -7, -8],
                'shift':range(-40,-1)
                # 'shift':[-20, -22, -30, -33],
                # 'shift':[-1],
                }
        self.desc.update(data)

        self.ref_pool = dict()
        for d_name, d_obj in self.det.iteritems():
            p_name = pn[d_name]
            for val in self.desc.get(p_name, []):
                # d_obj.rg = [0, win_size]
                # d_obj.rg = [1e3, 1e3+win_size]
                d_obj.rg = [2e3, 2e3+win_size]
                # d_obj.rg = [990, 990+win_size]
                d_obj.data_file = history_file
                self.ref_pool['%s_%f'%(p_name, val)] = d_obj.cal_norm_em(**{p_name:val, 'norm_em':None})

        # calculate entropy for each emperical measure
        self.ref_pool_entropy = dict()
        for k, em in self.ref_pool.iteritems():
            self.ref_pool_entropy[k] = self.cal_entropy(em)

    def cal_norm_em(self, **kwargs):
        """calculate normal emperical measure
        """
        super(AutoSelectStoDetector, self).cal_norm_em(**kwargs)
        em_entropy = self.cal_entropy(self.desc['em'])
        ref_entropy = self.ref_pool_entropy.values()
        diff = abs(np.array(em_entropy) - np.array(ref_entropy))
        mf_min_diff, mb_min_diff = np.min(diff, axis=0)
        mf_idx, mb_idx = np.argmin(diff, axis=0)
        print 'mf_min_diff, ', mf_min_diff
        print 'mb_min_diff, ', mb_min_diff

        key = self.ref_pool_entropy.keys()
        # return self.ref_pool[key[mf_idx]], self.ref_pool[key[mb_idx]]
        # return self.ref_pool[key[mf_idx]]
        print 'mb_idx, ', mb_idx
        return self.ref_pool[key[mb_idx]]

    def I(self, em, **kwargs):
        d_pmf, d_Pmb, d_mpmb = em
        self.desc['em'] = em
        h_ref_size = len(self.ref_pool)
        I_rec = np.zeros((h_ref_size, 2))
        i = -1
        for k, norm_em in self.ref_pool.iteritems():
            i += 1
            if norm_em is None:
                I_rec[i, :] = [float('inf'), float('inf')]
                continue

            pmf, Pmb, mpmb = norm_em
            I_rec[i, :] = [I1(d_pmf, pmf), I2(d_Pmb, d_mpmb, Pmb, mpmb)]

        print 'I_rec, ', I_rec
        res = np.min(I_rec, axis=0)
        print 'res, ', res
        return res

import copy
class AdaStoDetector(TwoWindowAnoDetector):

    def detect(self, data_file):
        self.data_file = data_file
        self.info = dict()
        # for win_size in [10, 50, 200, 400, 1000, 1500]:
        # for win_size in [10, 60, 200]:
        for win_size in [50, 100, 200, 500, 1000, 2000]:
            em_info = self.cal_em('time', win_size)
            adj_entro = self.cal_adj_entro(em_info['em'])
            self.info[win_size] = {'em_info':em_info, 'adj_entro':adj_entro}

    def cal_adj_entro(self, em):
        """calculate the cross entropy of two adjacent matrix
        """
        M = len(em)
        adj_entro = []
        for i in xrange(M-1):
            adj_entro.append( self.I(em[i], em[i+1]) )

        return adj_entro

    def plot(self, *args, **kwargs):
        # rt = self.record_data['winT']
        # plt.plot(rt[])
        # import pdb;pdb.set_trace()
        # plot_points(rt[0:-1], self.adj_entro,
                # *args, **kwargs)

        fig = plt.figure()
        mf_ax = fig.add_subplot(211)
        mb_ax = fig.add_subplot(212)
        # mf_fig = plt.figure()
        # mb_fig = plt.figure()
        for ws, info in self.info.iteritems():
            adj_entro = info['adj_entro']
            zip_ae = zip(*adj_entro)
            rt = info['em_info']['winT'][0:-1]
            # plt.plot(rt, zip_ae[0], figure=mf_fig)
            # plt.plot(rt, zip_ae[1], figure=mb_fig)
            mf_ax.plot(rt, zip_ae[0])
            mb_ax.plot(rt, zip_ae[1])
        leg = [str(v) for v in self.info.keys()]
        mf_ax.legend(leg)
        mb_ax.legend(leg)
        plt.savefig('adj_entro.pdf')
        plt.show()
        import pdb;pdb.set_trace()

    def cal_em(self, rg_type, win_size):
        self.record_data = dict(winT=[], em=[], rg=[])
        time = 0
        i = 0
        while True:
            i += 1
            if rg_type == 'time' : print 'time: %f' %(time)
            else: print 'flow: %s' %(time)

            try:
                self.rg = [time, time+win_size] # For two window method
                em = self.get_em(rg=[time, time+win_size], rg_type=rg_type)
                self.record( winT = time, em=em, rg=self.rg)
            except FetchNoDataException:
                print 'there is no data to detect in this window'
            except DataEndException:
                print 'reach data end, break'
                break

            time += win_size
        return copy.deepcopy(self.record_data)



if __name__ == "__main__":
    flag = [1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1]
    res = find_seg(flag)
    print 'res, ', res
    for a, b, f in res:
        print flag[a:b]
        print 'flag, ', f

