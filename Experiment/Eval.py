#!/usr/bin/env python
"""
to evaluate the performance of detector
get the statistical quantify for the hypotheis test
like False Alarm Rate, True
"""
from Experiment import AttriChangeExper
from Detector.DataParser import RawParseData

import matplotlib.pyplot as plt
import cPickle as pickle

class Eval(AttriChangeExper):
    """plot ROC curve for the hypothesis test"""
    OUT_STRING = """tp: %f\t fn: %f\t tn: %f\t fp: %f
sensitivity: %f\tspecificity: %f
"""

    def __init__(self, settings):
        AttriChangeExper.__init__(self, settings)

    def get_ab_flow_seq(self):
        normal_flow_file_name = settings.ROOT + '/Simulator/n0_flow.txt'
        self.normal_flow, self.fea_name = RawParseData(normal_flow_file_name)

        ab_flow_file_name = settings.ROOT + '/Simulator/abnormal_n0_flow.txt'
        self.flow, self.fea_name =  RawParseData(ab_flow_file_name)

        return [self.normal_flow.index(f) for f in self.flow]

    def eval_mutiple(self):
        for ab_win_num in xrange(1, 20, 2):
            # for num in [1, 2, 3, 4, 5, 6]:
            for ab_states_num in [2, 4]:
                print 'ab_win_num, ', ab_win_num
                res = self.eval(ident_type='ComponentFlowStateIdent',
                        entropy_type='mf',
                        ab_states_num=ab_states_num,
                        ab_win_num=ab_win_num)
                print self.OUT_STRING%res

    def eval_diff_ab_state_num(self):
        ab_win_num = 3
        # ident_type_set = ['ComponentFlowStateIdent', 'DerivativeFlowStateIdent',
                # 'ComponentFlowPairIdent', 'DerivativeFlowPairIdent']

        ident_type_set = ['ComponentFlowPairIdent', 'DerivativeFlowPairIdent']
        rec = dict(ComponentFlowPairIdent=[],
                DerivativeFlowPairIdent=[])
        for ident_type in ident_type_set:
            for ab_states_num in xrange(64):
                res = self.eval(ident_type=ident_type,
                        entropy_type='mb',
                        ab_states_num=ab_states_num,
                        ab_win_num=ab_win_num)

                print self.OUT_STRING%res
                rec[ident_type].append(res)

        pickle.dump(rec, open('./difference_ab_state_num.pk', 'w'))
        self._vis_eval_diff_ab_state_num()

    def _vis(self, data_name, ident_type_set, fea_handler, title, xlabel, ylabel, pic_name):
        import itertools
        rec = pickle.load(open(data_name, 'r'))
        legend_txt = []
        f = plt.figure(1); f.clf()
        ax = f.add_subplot(111)
        i = -1
        for ident_type in ident_type_set:
            i += 1
            data = zip(*rec[ident_type])
            for fea, handler in fea_handler.iteritems():
                ax.plot(handler(data))
                legend_txt.append('%ith %s'%(i,fea))

        plt.legend(legend_txt, loc=4)
        for l, ms, ls in zip(ax.lines, itertools.cycle('>^+*'), itertools.cycle(['--', '-.', '-'])):
            l.set_marker(ms)
            l.set_linestyle(ls)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.savefig(pic_name)
        plt.show()

    def _vis_eval_diff_ab_state_num(self):
        self._vis(
                data_name = './difference_ab_state_num.pk',
                ident_type_set = ['ComponentFlowPairIdent', 'DerivativeFlowPairIdent'],
                fea_handler = dict(
                    sensitivity = lambda x: x[-1],
                    specificity = lambda x: x[-2],
                    ),
                title = 'sensitivity and specificity vs no. of abnormal flow transition pair',
                xlabel = 'no. of abnormal flow transition pair',
                ylabel = 'sensitivity and specificity',
                pic_name = './difference_ab_tran_pair_num_sens_spec.eps'
                )

        self._vis(
                data_name = './difference_ab_state_num.pk',
                ident_type_set = ['ComponentFlowPairIdent', 'DerivativeFlowPairIdent'],
                fea_handler = dict(
                    fnr = lambda x: [1-v for v in x[-1]],
                    fpr = lambda x: [1-v for v in x[-2]],
                    ),
                title = 'fnr and fpr vs no. of abnormal flow transition pair',
                xlabel = 'no. of abnormal flow transition pair',
                ylabel = 'fnr and fpr',
                pic_name = './difference_ab_tran_pair_num_fnr_fpr.eps'
                )

    def eval_hoeffding(self):
        """evaluate the performance of detector under the hoeffding optimal rule"""
        false_alarm_rate = 0.05
        entropy_threshold = self.detector.get_hoeffding_threshold(false_alarm_rate)
        res = self.eval(ident_type='ComponentFlowStateIdent',
                entropy_type='mf',
                entropy_threshold=entropy_threshold,
                ab_states_num=2)
        print self.OUT_STRING%res

    def eval(self, ident_type, entropy_type=None, portion=None, ab_states_num=None,
            entropy_threshold=None, ab_win_portion=None, ab_win_num=None):
        """
        calculate the true positive, false negative, true negative, false positive, sensitivity and
        specificity for a given detection
        **sensitivity** is the probability of a alarm given that the this flow is anormalous
        **specificity** is the probability of there isn't alarm given that the flow is normal
        """
        self.real_ab_flow_seq = self.get_ab_flow_seq()
        ab_states = self.detector.ident(ident_type,
                entropy_type, portion, ab_states_num,
                entropy_threshold, ab_win_portion, ab_win_num)
        print 'ab_states, ', ab_states
        self.ab_seq = self.detector.get_ab_flow_seq(entropy_type,
                entropy_threshold, ab_win_portion, ab_win_num,
                ab_states)
        print 'abnormal window indices are: ', self.detector.ab_win_idx

        tp, fn, tn, fp = self.get_quantitative(self.real_ab_flow_seq, self.ab_seq, range(len(self.normal_flow)))
        # sensitivity is the probability of a alarm given that the this flow is anormalous
        sensitivity = tp * 1.0 / (tp + fn)
        # specificity is the probability of there isn't alarm given that the flow is normal
        specificity = tn * 1.0 / (tn + fp)
        # print OUT%(tp, fn, tn, fp, sensitivity, specificity)
        return (tp, fn, tn, fp, sensitivity, specificity)

    def get_quantitative(self, A, B, W):
        """**A** is the referece, and **B** is the detected result, **W** is the whole set"""
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

        return tp, fn, tn, fp

        # get sensitivity
        # get specificity
        print 'ab_seq, ', self.ab_seq
        ir = self.get_intersection_ratio(self.real_ab_flow_seq, self.ab_seq)
        print 'the intersection ratio is, ', ir

    def get_intersection_ratio(self, A, B):
        self.ins = set.intersection(set(A), set(B))
        self.uns = set.union(set(A), B)
        return len(self.ins) * 1.0 / len(self.uns)


if __name__ == "__main__":
    import settings
    exper = Eval(settings)
    # exper.configure()
    # exper.simulate()
    # exper.detect()
    # exper.eval_diff_ab_state_num()
    exper._vis_eval_diff_ab_state_num()
    # exper.eval_mutiple()
    # exper.eval_hoeffding()
    # detector.plot_entropy()

