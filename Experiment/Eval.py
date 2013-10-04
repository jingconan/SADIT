#!/usr/bin/env python
""" Evaluate the performance of detector
get the statistical quantify for the hypotheis test
like False Alarm Rate.
"""
from __future__ import print_function, division, absolute_import
import copy, os
from sadit.Detector.DataParser import RawParseData
from sadit.util import update_not_none, plt
from sadit.util import zdump, zload
import itertools

from .Detect import Detect

def roc(data):
    tpv, fnv, tnv, fpv, _, _ = data
    tpr = [ tp * 1.0 / (tp + fn) for tp, fn in zip(tpv, fnv)]
    # calculate the false positive rate
    fpr = [ fp * 1.0 / (fp + tn) for fp, tn in zip(fpv, tnv)]
    print('fpr, ', fpr)
    print('tpr, ', tpr)
    return fpr, tpr

def get_quantitative(A, B, W):
    """**A** is the referece, and **B** is the detected result, **W** is the whole set
    calculate the true positive, false negative, true negative and false positive
    """
    A = set(A)
    B = set(B)
    W = set(W)
    # no of true positive, no of elements that belongs to B and also belongs to A
    tp = len(set.intersection(A, B))

    # no of false negative no of elements that belongs to A but doesn't belong to B
    fn = len(A - B)

    # no of true negative, no of element that not belongs to A and not belong to B
    tn = len(W - set.union(A, B))
    # no of false positive, no of element that not belongs to A but belongs to B
    fp = len(B - A)

    # sensitivity is the probability of a alarm given that the this flow is anormalous
    sensitivity = tp * 1.0 / (tp + fn)
    # specificity is the probability of there isn't alarm given that the flow is normal
    specificity = tn * 1.0 / (tn + fp)

    return tp, fn, tn, fp, sensitivity, specificity

#############################################################################
##         Visualization Part                                           #####
#############################################################################
def vis(data_name, ident_type_set, fea_handler, title, xlabel=None, ylabel=None,
        pic_name=None, pic_show=False, ylim=None, xlim=None,
        markers='>^+*', line_styles=('-', '-.', '--'),
        subplot=None):
    """ visualize the attribute

    """
    rec = zload(data_name)

    if subplot is None:
        f = plt.figure(1); f.clf()
        ax = f.add_subplot(111)
    else:
        if isinstance(subplot, int):
            ax = plt.gcf().add_subplot(subplot)
        else:
            f = subplot[0]
            ax = f.add_subplot(subplot[1])
    i = -1
    legend_txt = []
    for ident_type in ident_type_set:
        i += 1
        data = zip(*rec[ident_type])
        for fea, handler in fea_handler.iteritems():
            vis_data = handler(data)
            if isinstance(vis_data[0], list) or isinstance(vis_data[0], tuple):
                ax.plot(*vis_data)
            elif isinstance(vis_data[0], int) or isinstance(vis_data[0], float):
                ax.plot(vis_data)
            else:
                raise Exception('Unknown visualization data, check your feature handler please')
            # legend_txt.append('%ith %s'%(i,fea))
            legend_txt.append('%s %s'%(ident_type,fea))

    # plt.legend(legend_txt, loc=4, numpoints=1)
    plt.legend(legend_txt, 'best', numpoints=1)
    for l, ms, ls in zip(ax.lines, itertools.cycle(markers), itertools.cycle(line_styles)):
        l.set_marker(ms)
        l.set_linestyle(ls)
    plt.title(title)
    if xlabel: plt.xlabel(xlabel)
    if ylabel: plt.ylabel(ylabel)
    if ylim: plt.ylim(ylim)
    if xlim: plt.xlim(ylim)

    if pic_name: plt.savefig(pic_name)
    if pic_show: plt.show()

def plot_roc(markers=' ', *args, **kwargs):
    """ plot the ROC curve given the data """
    fea_handler = dict(ROC=roc)
    vis(fea_handler=fea_handler, xlim=[0, 1], ylim=[0, 1.1], markers=markers, *args, **kwargs)

def plot_roc_curve_ident(folder):
    """plot ROC Curve for detection with flow state(transition pair) identification"""
    plot_roc(
            # data_name = './difference_ab_state_num.pk',
            data_name = folder + '/compare_ident.pk',
            # ident_type_set = ['ComponentFlowStateIdent', 'DerivativeFlowStateIdent'],
            ident_type_set = ['ComponentFlowStateIdent', 'ComponentFlowPairIdent'],
            # ident_type_set = ['ComponentFlowPairIdent'],
            title = 'ROC curve of detector with component flow identification',
            # xlabel = 'false positive rate',
            ylabel = 'true positive rate',
            # pic_name = './flow_ident_roc.eps',
            pic_name = None,
            # subplot= [None, 211],
            subplot= 211,
            )

    plot_roc(
            # data_name = './difference_ab_state_num.pk',
            data_name = folder + '/compare_ident.pk',
            ident_type_set = ['DerivativeFlowStateIdent', 'DerivativeFlowPairIdent'],
            # ident_type_set = ['DerivativeFlowPairIdent'],
            title = 'ROC curve of detector with derivative flow identification',
            xlabel = 'false positive rate',
            ylabel = 'true positive rate',
            pic_name = folder + '/flow_ident_roc.eps',
            # subplot = [None, 211],
            subplot = 212,
            # pic_show = True
            )
def plot_roc_curve(folder):
    plot_roc(
            data_name = folder + '/diff_ab_win_num.pk',
            ident_type_set = ['mf', 'mb'],
            title = 'ROC curve of stochastic anomaly detector',
            xlabel = 'false positive rate',
            ylabel = 'true positive rate',
            pic_name = folder + '/flow_roc.eps',
            # pic_show = True
            markers='o+'
            )

def plot_roc_curve_seperate(folder):
    plot_roc(
            data_name = folder + '/diff_ab_win_num.pk',
            ident_type_set = ['mf'],
            title = 'ROC curve of stochastic anomaly detector',
            xlabel = 'false positive rate',
            ylabel = 'true positive rate',
            pic_name = folder + '/flow_roc.eps',
            # pic_show = True
            markers='o+',
            subplot = 211,
            )

    plot_roc(
            data_name = folder + '/diff_ab_win_num.pk',
            ident_type_set = ['mb'],
            title = 'ROC curve of stochastic anomaly detector',
            xlabel = 'false positive rate',
            ylabel = 'true positive rate',
            pic_name = folder + '/flow_roc.eps',
            # pic_show = True
            markers='o+',
            subplot = 212,
            )
    pass


def _vis_eval_diff_ab_state_num(folder):
    vis(
            data_name = folder +'/compare_ident.pk',
            ident_type_set = ['ComponentFlowPairIdent', 'DerivativeFlowPairIdent'],
            fea_handler = dict(
                sensitivity = lambda x: x[-1],
                specificity = lambda x: x[-2],
                ),
            title = 'sensitivity and specificity vs no. of abnormal flow transition pair',
            xlabel = 'no. of abnormal flow transition pair',
            ylabel = 'sensitivity and specificity',
            pic_name = folder +'/difference_ab_tran_pair_num_sens_spec.eps',
            # pic_show = True
            )



    vis(
            data_name = folder +'/compare_ident.pk',
            ident_type_set = ['ComponentFlowPairIdent', 'DerivativeFlowPairIdent'],
            fea_handler = dict(
                fnr = lambda x: [1-v for v in x[-1]],
                fpr = lambda x: [1-v for v in x[-2]],
                ),
            title = 'fnr and fpr vs no. of abnormal flow transition pair',
            xlabel = 'no. of abnormal flow transition pair',
            ylabel = 'fnr and fpr',
            pic_name = folder +'/difference_ab_tran_pair_num_fnr_fpr.eps'
            )


class Eval(Detect):
    """plot ROC curve for the hypothesis test"""
    OUT_STRING = """tp: %f\t fn: %f\t tn: %f\t fp: %f
sensitivity: %f\tspecificity: %f
"""
    real_ab_flow_seq = None

    def init_parser(self, parser):
        super(Eval, self).init_parser(parser)
        parser.add_argument('--max_search_mf_states', type=int,
                help = """max number of abnormal model free states it will search"""
                )

        parser.add_argument('--max_search_mb_states', type=int,
                help = """max number of abnormal model free states it will
                search"""
                )

        parser.add_argument('-a', '--ab_flows_data', default=None,
                help = """file name for the abnormal flows exported by simulator
                itself. used as reference"""
                )

        parser.add_argument('--res_folder', default=None,
                help = """result folder"""
                )

        parser.add_argument('--plot', default=False, action='store_true',
                help = """plot the result or not"""
                )

    def get_ab_flow_seq(self):
        """get the sequence of all abnormal flows, get the reference ground truth"""
        normal_flow_file_name = self.desc['data']
        self.normal_flow, self.fea_name = RawParseData(normal_flow_file_name)

        ab_flow_file_name = self.desc['ab_flows_data']
        self.flow, self.fea_name =  RawParseData(ab_flow_file_name)

        return [self.normal_flow.index(f) for f in self.flow]

    # def eval_mutiple(self):
    #     for ab_win_num in xrange(1, 20, 2):
    #         for ab_states_num in [2, 4]:
    #             print 'ab_win_num, ', ab_win_num
    #             res = self.eval(ident_type='ComponentFlowStateIdent',
    #                     entropy_type='mf',
    #                     ab_states_num=ab_states_num,
    #                     ab_win_num=ab_win_num)
    #             print self.OUT_STRING%res

    def eval_diff_ab_win_num(self, folder):
        """eval the results under difference abnormal window number"""
        entropy_type_vec = ['mf', 'mb']
        rec = dict()
        for entropy_type in entropy_type_vec:
            rec[entropy_type] = []
            for ab_win_num in xrange(1, 100, 2):
                print('ab_win_num, ', ab_win_num)
                res = self.eval(ab_win_num=ab_win_num, entropy_type=entropy_type)
                print(self.OUT_STRING%res)
                rec[entropy_type].append(res)

        # import ipdb;ipdb.set_trace()
        zdump(rec, folder + '/diff_ab_win_num.pk')

    def compare_ident_method(self, ab_win_num, res_folder):
        """ compare different identification method.

        calculate the statistical measure to show the performance refer the
        return value of self.eval for the metric calculated for different
        identification method.

        Parameters:
        -----------------------
        ab_win_num : int
            specify the number of windows that selected as abnormal window. So
            it influence the performance of the original stochasticl
            detecotring before applying the flow state identification
            techiniques. More specifically, it influence the largest true
            positive rate the stotchastic detector can achieve.

        """
        idents= {
                'ComponentFlowStateIdent':'mf',
                'DerivativeFlowStateIdent':'mf',
                'ComponentFlowPairIdent':'mb',
                'DerivativeFlowPairIdent':'mb',
                }
        # max_ab_state_num = dict(mf=12, mb=144) # it influence the max ab_state_num it will search
        max_ab_state_num = dict(mf=self.desc['max_search_mf_states'],
                mb=self.desc['max_search_mb_states']) # it influence the max ab_state_num it will search
        rec = dict(zip(idents.keys(), [list() for i in xrange(len(idents))]))
        for ident_type, entropy_type in idents.iteritems():
            print('ident_type, ', ident_type)
            for ab_states_num in xrange(max_ab_state_num[entropy_type]):
                print('ab_states_num, ', ab_states_num)
                res = self.eval(ident_type, entropy_type,
                        ab_states_num=ab_states_num,
                        ab_win_num=ab_win_num)

                print(self.OUT_STRING%res)
                rec[ident_type].append(res)

        # import ipdb;ipdb.set_trace()
        zdump(rec, res_folder + '/compare_ident.pk')

    def eval_hoeffding(self, false_alarm_rate):
        """evaluate the performance of detector under the hoeffding optimal rule"""
        # false_alarm_rate = 0.05
        entropy_threshold = self.detector.get_hoeffding_threshold(false_alarm_rate)
        res = self.eval(ident_type='ComponentFlowStateIdent',
                entropy_type='mf',
                entropy_threshold=entropy_threshold,
                ab_states_num=2)
        print(self.OUT_STRING%res)

    def eval(self, ident_type=None, entropy_type=None, portion=None, ab_states_num=None,
            entropy_threshold=None, ab_win_portion=None, ab_win_num=None):
        """ evaluate a method

        Parameters:
        ---------------------------
        ident_type, entropy_type, portion, ab_states_num :
            See StoDetector.FBAnoDetector.ident for the meaning of these
            parameters

        entropy_threshold, ab_win_portion, ab_win_num,
            See StoDetector.FBAnoDetector.get_ab_flow_seq for the meaning of
            these parameters

        Notes:
        ---------------------------
        calculate the following metrics for a given detection
            - true positive (TP),
            - false negative (FN),
            - true negative (TN),
            - false positive (FP),
            - sensitivity and specificity
        1. **sensitivity** is the probability of a alarm given that the this
        flow is anormalous. 2. **specificity** is the probability of there
        isn't alarm given that the flow is normal

        """
        if not self.real_ab_flow_seq:
            self.real_ab_flow_seq = self.get_ab_flow_seq()

        # identify the sequence for abnormal flows states
        ab_states = None
        if ident_type is not None:
            ab_states = self.detector.ident(ident_type,
                    entropy_type, portion, ab_states_num,
                    entropy_threshold, ab_win_portion, ab_win_num)

        # calculate sequence for all flows that are identified as abnormal
        self.ab_seq = self.detector.get_ab_flow_seq(entropy_type,
                entropy_threshold, ab_win_portion, ab_win_num,
                ab_states)

        print('ab_states, ', ab_states)
        print('abnormal window indices are: ',
                self.detector.ab_win_idx)

        return get_quantitative(self.real_ab_flow_seq,
                self.ab_seq,
                range(len(self.normal_flow)))

    def run(self):
        self.desc = copy.deepcopy(self.args.config['DETECTOR_DESC'])
        update_not_none(self.desc, self.args.__dict__)

        rf = self.desc['res_folder']
        ab_win_num = self.desc['ab_win_num']

        # only plot the result
        if self.desc['plot']:
            plt.figure()
            plot_roc_curve(rf)
            plt.figure()
            plot_roc_curve_ident(rf)
            plt.figure()
            plot_roc_curve_seperate(rf)
            plt.show()
            return

        if not os.path.exists(rf):
            os.makedirs(rf)

        self.detect()

        # compare different identification method under a ab_win_num
        self.compare_ident_method(ab_win_num, rf)

        # evaluate under different ab_win_num
        self.eval_diff_ab_win_num(rf)

        # evaluate hoeffding test rule
        false_alarm_rate = self.desc['false_alarm_rate']
        self.eval_hoeffding(false_alarm_rate)
