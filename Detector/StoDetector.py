#!/usr/bin/env python
"""
This file contains all the stochastic detection techniques
"""
from __future__ import print_function, division, absolute_import
__author__ = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"
__status__ = "Development"

import os
import cPickle as pickle
from math import log

from sadit.util import DataEndException, FetchNoDataException, abstract_method
from sadit.util import save_csv, plt

from .DetectorLib import I1, I2
from .mod_util import plot_points
from .Base import WindowDetector


def is_basic_type(a):
    """ check whether a is a basic type or not

    only int, string, float, dict are considered as basic type

    Parameters
    ---------------
    a : object that needs to be checked.

    Returns
    --------------
    res : {True, False}
        True if a is a basic type and False otherwise.
    """
    if isinstance(a, int):
        return True
    elif isinstance(a, float):
        return True
    elif isinstance(a, str):
        return True
    elif isinstance(a, dict):
        return True
    return False

class StoDetector (WindowDetector):
    """ Abstract Base Class for stochastic anomaly detector.

    Parameters
    -------------
    - desc: dict
            Dictionary of default parameters

        + normal_rg : list
                range of normal traffic, if
        + win_type :
        + max_detect_num
        + interval
        + fea_option
        + entropy_th
        + hoeff_far

    """
    def __init__(self, desc):
        self.desc = desc
        self.record_data = dict(entropy=[], winT=[], threshold=[], em=[])

    def get_em(self, rg, rg_type):
        """abstract method. Get empirical measure,

        Parameters
        -------------
        rg : list
                specify the start and the end point of the data that will be
                used.
        rg_type :  {'flow', 'time'}
                type of the rg.
        """
        abstract_method()

    def init_parser(self, parser):
        """ add parameters

        entropy_th specify the threshold manually.
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
        """ calculate the K-L divergence of two emperical measures

        [abstract method]

        """
        abstract_method()

    # def get_flow_num(self, rg, rg_type):
    #     sp, ep = self.data_file.data._get_where(rg, rg_type)
    #     return ep - sp

    def record(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.record_data[k].append(v)

    def reset_record(self):
        for k, v in self.record_data.iteritems():
            self.record_data[k] = []

    def cal_norm_em(self, **kwargs):
        nominal_rg = self.desc['normal_rg']
        # import pdb;pdb.set_trace()
        rg_type = self.desc['win_type']
        return self.ref_file.get_em(rg=nominal_rg, rg_type=rg_type)

    # def detect(self, data_file, nominal_rg = [0, 1000], rg_type='time',  max_detect_num=None):
    def detect(self, data_file, ref_file=None):
        """ main function to detect.

        it will slide the window, get the emperical measure and get the
        indicator

        Parameters
        --------------------
        data_file : subclass of **DataHandler**.
                See DataHandler.py.

        Returns
        --------------------
        record_data: dict
                + desc : parameters used in the detection
                + threshold : threshold

        """
        # nominal_rg = self.desc['normal_rg']
        rg_type = self.desc['win_type']
        max_detect_num = self.desc['max_detect_num']

        self.data_file = data_file
        self.ref_file = data_file if ref_file is None else ref_file
        # import ipdb;ipdb.set_trace()
        # self.ref_file = ref_file
        # self.norm_em = self.get_em(rg=nominal_rg, rg_type=rg_type)
        self.norm_em = self.cal_norm_em()
        # self.desc['norm_em'] = self.norm_em

        win_size = self.desc['win_size']
        interval = self.desc['interval']

        time = self.desc['fr_win_size'] if ('flow_rate' in self.desc['fea_option'].keys()) else 0

        i = 0
        while True:
            i += 1
            if max_detect_num and i > max_detect_num:
                break
            if rg_type == 'time' : print('time: %f' %(time))
            else: print('flow: %s' %(time))

            try:
                self.rg = [time, time+win_size] # For two window method
                em = self.data_file.get_em(rg=[time, time+win_size], rg_type=rg_type)
                entropy = self.I(em, norm_em=self.norm_em)
                self.record( entropy=entropy, winT = time, threshold = 0, em=em)
            except FetchNoDataException:
                print('there is no data to detect in this window')
            except DataEndException:
                print('reach data end, break')
                break

            time += interval

        self.detect_num = i - 1
        self.save_addi_info()

        return self.record_data

    def save_addi_info(self, **kwargs):
        """  save additional information"""
        # get the threshold:
        if self.desc.get('entropy_th') is not None:
            self.record_data['threshold'] = [self.desc['entropy_th']] * self.detect_num
        elif self.desc.get('hoeff_far') is not None:
            self.record_data['threshold'] = self.get_hoeffding_threshold(self.desc['hoeff_far'])
        else:
            self.record_data['threshold'] = None

        # record the parameters
        self.record_data['desc'] = dict((k, v) \
                for k, v in self.desc.iteritems() if is_basic_type(v))

    def hoeffding_rule(self, n, false_alarm_rate):
        """ hoeffding rule with linear correction term

        Parameters:
        --------------
        n : int
            Number of flows in the window
        false_alarm_rate : float
            false alarm rate

        Returns
        --------------
        ht : float
            hoeffding threshold


        """
        # return -1.0 / n * log(false_alarm_rate) + self.desc['ccoef'] * log(n) / n
        return -1.0 / n * log(false_alarm_rate) + self.desc['ccoef'] / n

    def get_hoeffding_threshold(self, false_alarm_rate):
        """calculate the threshold of hoeffiding rule,

        Parameters:
        ---------------
        false_alarm_rate : float
            false alarm rate

        Returns
        ---------------
        res : list
            list of thresholds for each window.

        Notes:
        ----------------
        :math: `threshold = -1 / |G| log(epsilon)` where |G| is the number of flows in
        the window and `epsilon` is the false alarm_rate

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
        """  plot the detection result

        Parameters:
        ---------------
        See plot_points

        Returns:
        --------------
        None

        """
        rt = self.record_data['winT']
        ep = self.record_data['entropy']
        # import pdb;pdb.set_trace()
        threshold = self.record_data['threshold']
        plot_points(rt, ep, threshold,
                xlabel_=self.desc['win_type'], ylabel_= 'entropy',
                *args, **kwargs)

    def dump(self, data_name):
        # import ipdb;ipdb.set_trace()
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
        """ find abnormal windows out of all windows

        Parameters:
        -----------
        entropy_threshold : list of floats
            list of threshold for each window
        ab_win_portion
            portion of windows considered as abnormal
        ab_win_num : int
            abnormal window number

        Notes
        -----------
        find abnormal windows. There are three standards to select abnormal windows:
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

    def export_ab_flow_entropy(self, entropy, fname,
            entropy_threshold=None, ab_win_portion=None, ab_win_num=None):
        """export abnormal flows based on entropy

        Parameters
        --------------
        entropy : list
            a list of entropy, one number for each window
        fname : str,
            file name of the output abnormal flow
        entropy_threshold, ab_win_portion : str, optional
            criterion to identifi abnormal window, see docs of
            *find_abnormal_windows* for detailed meaning
        ab_win_num : int, optional
            criterion to identifi abnormal window, see docs of
            *find_abnormal_windows* for detailed meaning

        Returns
        --------------
        None

        Notes
        ----------------
        - abnormal windows are identifed.
        - all flows in those windows are exported as abnormal flows.
        - self.data_file.data._get_where() is used in current version, which
          should be fixed in the future

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
            sp, ep = self.data_file.data._get_where([st, st+win_size], rg_type) #FIXME
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
    def I(self, em, norm_em):
        return I1(em, norm_em)

    # def get_em(self, rg, rg_type):
    #     """get empirical measure"""
    #     pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
        # return pmf, Pmb, mpmb
    #     return pmf

class ModelBaseAnoDetector(StoDetector):
    """ Model based approach, use Markovian Assumption
    """
    def I(self, em, norm_em):
        return I2(em, norm_em)
        # d_Pmb, d_mpmb = em
        # Pmb, mpmb = norm_em
        # return I2(d_Pmb, d_mpmb, Pmb, mpmb)

    # def get_em(self, rg, rg_type):
    #     pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
    #     return Pmb, mpmb


# from .Ident import *
from . import Ident
class FBAnoDetector(StoDetector):
    """model free and model based together, will be faster then run model free
    and model based approaches separately since some intemediate results are reused.
    """
    def I(self, em, norm_em):
        # d_pmf, d_Pmb, d_mpmb = em
        # pmf, Pmb, mpmb = norm_em
        d_pmf, d_Pmb = em
        pmf, Pmb = norm_em
        return I1(d_pmf, pmf), I2(d_Pmb, Pmb)

    # def get_em(self, rg, rg_type):
    #     """get empirical measure"""
    #     pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
    #     return pmf, Pmb, mpmb

    def plot(self, far=None, figure_=None, subplot_=(211, 212),
            title_=['model free', 'model based'],
            pic_name=None, pic_show=False, csv=None,
            *args, **kwargs):
        if not plt: self.save_plot_as_csv()

        rt = self.record_data['winT']
        mf, mb = zip(*self.record_data['entropy'])
        threshold = self.record_data['threshold']

        if csv:
            save_csv(csv, ['rt', 'mf', 'mb', 'threshold'], rt, mf, mb, threshold)

        if figure_ is None: figure_ = plt.figure()
        # import ipdb;ipdb.set_trace()
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


    def export_abnormal_flow(self, fname, entropy_threshold=None,
            ab_win_portion=None, ab_win_num=None):
        """ export the abnormal flows for abnormal windows

        based on model_free entropy and model_based entropy

        See Also
        ---------------
        see **StoDetector.export_ab_flow_entropy** for the meaning of the
        parameters.

        """
        mf, mb = zip(*self.record_data['entropy'])
        # select portion of the window to be abnormal
        dirname = os.path.dirname(fname)
        basename = os.path.basename(fname)

        # for model free entropy
        self.export_ab_flow_entropy(mf, dirname + '/mf-' + basename,
                entropy_threshold, ab_win_portion, ab_win_num)

        # for model based entropy
        self.export_ab_flow_entropy(mb, dirname + '/mb-' + basename,
                entropy_threshold, ab_win_portion, ab_win_num)

    def get_ab_flow_seq(self, entropy_type, entropy_threshold=None,
            ab_win_portion=None, ab_win_num=None,
            ab_flow_info = None):
            # ab_flow_state=None, ab_flow_tran=None):
        """get abnormal flow sequence number.

        the input is citerions which window will be abnormal window

        Parameters:
        ---------------------------
        entropy_type : {'mf', 'mb'}
            type of entropy
        entropy_threshold : list of floats
            list of thresholds, each for a window.
        ab_win_portion : float
            portion of windows that will be considered as abnormal
        ab_win_num :
            number of windows that will be considered as abnormal
        ab_flow_info : list
            represents either abnormal flow state(for model free approach) and
            abnormal flow trantision pair(for model based approach).

        Returns:
        ---------------------------
        ano_flow_seq : list of ints
            a list of sequence for flows that will be considered as abnormal.

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

        Parameters:
        --------------------------------
        ident_type : {'FlowStateIdent', 'ComponentFlowStateIdent',
            'DerivativeFlowStateIdent', 'FlowPairIdent', 'componentflowpairident',
            'DerivativeFlowPairIdent'}
        entropy_type : {'mf', 'mb'}.
                'mf' will identify the flow state
                'mb' will identify the flow transition pair.
        portion : float
                portion of flow state that will be selected as anomalous.
        ab_states_num : int
                the number of flow states that will be selected as anomalous.


        Returns:
        ---------------------------------------
            res : list
                if ident_type is a FlowStateIdent type, each element in the
                    `res` is the sequence of identifed flow states. Otherwise,
                    each element in `res` is a two element pair
                    (from_state_idx, to_state_idx)

        Notes:
        ------------------------------
        - *ident_type* can be any Identification Class in Ident.py
        - **portion** has higher priority
            than **ab_states_num**
        - 1. first the abnormal window indices are identified. 2. according to
          ident_type, some flows in the abnormal window indices are exported.

        """
        em_record_set = self.record_data['em']
        def tran_to_joint(tp, mar):
            """

            Parameters:
            ---------------
                tp : list of list
                    transition probability
                mar : list
                    margin probability

            Returns:
            --------------
                res : list
                    joint probability distribution


            Notes:
            --------------
                joint_prob[a][b] = tp[a][b] * mar[p]

            """
            res = []
            for tp, m in zip(tp,mar):
                res.append([m*p for p in tp])
            return res

        def get_nu_set(em_record_set, entropy_type):
            """  get empirical measure according to entropy_type

            Parameters:
            ---------------
                em_record_set : list
                    result
                entropy_type : {'mf', 'mb'}

            Returns:
            --------------
            res : list
                if entropy_type == 'mf', return model-free empirical measure
                if entropy_type == 'mb', return model-based empirical measure

            """
            if entropy_type == 'mf':
                return [em[0] for em in em_record_set]
            elif entropy_type == 'mb':
                return [tran_to_joint(em[1], em[2]) for em in em_record_set]

        nu_set = get_nu_set(em_record_set, entropy_type)
        mu = get_nu_set([self.norm_em], entropy_type)[0]
        # ident = globals()[ident_type](nu_set, mu)
        ident = getattr(Ident, ident_type)(nu_set, mu)
        mf, mb = zip(*self.record_data['entropy'])
        ab_idx = self.find_abnormal_windows(locals()[entropy_type],
                entropy_threshold, ab_win_portion, ab_win_num)
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

"""In the following algorithm, the reference empirical measure is calculate for
each window
"""
class DynamicStoDetector(FBAnoDetector):
    """Base Class for All Dynamic Stochasic Detector
    """
    def I(self, em, **kwargs):
        # d_pmf, d_Pmb, d_mpmb = em
        d_pmf, d_Pmb = em
        self.desc['em'] = em
        # pmf, Pmb, mpmb = self.cal_norm_em(**kwargs)
        pmf, Pmb = self.cal_norm_em(**kwargs)
        return I1(d_pmf, pmf), I2(d_Pmb, Pmb)

    def cal_norm_em(self, **kwargs):
        self.desc.update(kwargs)

class TwoWindowAnoDetector(DynamicStoDetector):
    """ Two Window Stochastic Anomaly Detector.
    - A small window to capture the transient information
    - A relative long window as a reference traffic. This window
        should be properly chosen so that it can reflect the stationary
        property of the traffic.

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
            norm_win_em = self.ref_file.get_em(rg=norm_rg, rg_type=self.desc['win_type'])
        else:
            norm_win_em = norm_em

        return norm_win_em

# import numpy as np
# from .DataHandler import CombinedEM

class PeriodStoDetector(DynamicStoDetector):
    """Stochastic Detector Designed to Detect Anomaly when the
    normal behaviour change periodically. Only choose traffic periodically as normal traffic
    """

    def init_parser(self, parser):
        super(PeriodStoDetector, self).init_parser(parser)
        parser.add_argument('--period', default=1000.0, type=float,
                help="""the period of underlying traffic""")

    def cal_norm_em(self, rg=None, **kwargs):
        super(PeriodStoDetector, self).cal_norm_em(**kwargs)
        if rg is None:
            return StoDetector.cal_norm_em(self)

        norm_em = self.desc.get('norm_em', None)
        norm_win_em = norm_em
        # norm_win_em = CombinedEM(norm_em)
        norm_rg_ref = self.desc['normal_rg']
        period = self.desc['period']

        i = -1 if norm_em is None else 0
        j = (norm_rg_ref[0] - rg[0]) / period
        if period >= (norm_rg_ref[1] - norm_rg_ref[0]):
            raise Exception('period is too large')

        while True:
            i += 1
            j += 1
            try:
                # norm_rg = [rg[0] + i * period, rg[1] + i * period] #FIXME need to look back
                norm_rg = [rg[0] + j * period, rg[1] + j * period] #FIXME need to look back
                if norm_rg[1] > norm_rg_ref[1]:
                    break
                norm_win_em = norm_win_em + self.ref_file.get_em(rg=norm_rg, rg_type=self.desc['win_type'])
            except FetchNoDataException:
                break
            except DataEndException:
                break
            except AttributeError: #FIXME
                return
        # j = 0
        # while True:
        #     i += 1
        #     j -= 1
        #     if rg[0] + j * period < norm_rg_ref[0]:
        #         break
        #     try:
        #         norm_rg = [rg[0] + j * period, rg[1] + j * period] #FIXME need to look back
        #         norm_win_em = norm_win_em + self.get_em(rg=norm_rg, rg_type=self.desc['win_type'])
        #     except FetchNoDataException:
        #         break
        #     except DataEndException:
        #         break

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
        """ For data in window *i*, simply using the data in widnow *i-shift* to
        calculate norm_em
        """
        super(DummyShiftWindowDetector, self).cal_norm_em(**kwargs)
        win_size = self.desc['win_size']
        shift = self.desc['shift']
        assert(self.rg[1] - self.rg[0] == win_size)
        norm_rg = [self.rg[0] - shift * win_size, self.rg[1] - shift * win_size]
        # import pdb;pdb.set_trace()
        norm_win_em = self.ref_file.get_em(rg=norm_rg, rg_type=self.desc['win_type'])

        return norm_win_em


"""  Static Detectors. They are weak detectors that will be used by Robust
Detector
"""

class SlowDriftStaticDetector(FBAnoDetector):
    def init_parser(self, parser):
        parser.add_argument('--start', default=0, type=float,
                help="""start point of the normal traffic""")
        parser.add_argument('--delta_t', default=10.0, type=float,
                help="""delta_t is a small time range during which the normal
                behavior is considered unchanged""")

    def cal_norm_em(self, **kwargs):
        self.desc.update(kwargs)
        start = self.desc['start']
        delta_t = self.desc['delta_t']
        win_type = self.desc['win_type']
        rg = [start, start + delta_t]
        print('rg', rg)
        try:
            norm_win_em = self.ref_file.get_em(rg, win_type)
        except FetchNoDataException:
            norm_win_em = None
        except DataEndException:
            norm_win_em = None

        return norm_win_em

import numpy as np
class PeriodStaticDetector(FBAnoDetector):
    """ Reference Empirical Measure is calculated by periodically selection.

        Notes
        ------------------
        The selection is shown as follows

        codeblock:: text

                        +--+         +--+          +--+
                    ----+  +---------+  +- --------+  +------
          |<-start->|   |dt|<--period-->|
        all the traffic within the time range with nonzero value are selected as reference traffic.

    """
    def init_parser(self, parser):
        super(PeriodStaticDetector, self).init_parser(parser)
        parser.add_argument('--start', default=0, type=float,
                help="""start point of the period selection""")
        parser.add_argument('--period', default=1000.0, type=float,
                help="""the period of underlying traffic""")
        parser.add_argument('--delta_t', default=10.0, type=float,
                help="""delta_t is a small time range during which the normal
                behavior is considered unchanged""")

    def _combine(self, win_ems):
        em_sum = [sum(v for v in d if v is not None) for d in zip(*win_ems)]
        num = [sum(1 for v in d if v is not None) for d in zip(*win_ems)]
        # import ipdb;ipdb.set_trace()
        return [em / n for em, n in zip(em_sum, num)]

    def cal_norm_em(self, **kwargs):
        self.desc.update(kwargs)

        start = self.desc['start']
        win_type = self.desc['win_type']
        period = self.desc['period']
        delta_t = self.desc['delta_t']

        win_ems = []
        nrg = self.desc.get('normal_rg')
        nrg = nrg if nrg is not None else [0, float('inf')]
        time = nrg[0] + start + delta_t
        while time < nrg[1]:
            time += period
            try:
                delta_rg = [time - delta_t, time]
                delta_em = self.ref_file.get_em(delta_rg, win_type)
                win_ems.append([np.array(e) for e in delta_em])
            except FetchNoDataException:
                win_ems.appends(None)
            except DataEndException:
                break

        return self._combine(win_ems)
