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
import itertools

class Eval(AttriChangeExper):
    """plot ROC curve for the hypothesis test"""
    OUT_STRING = """tp: %f\t fn: %f\t tn: %f\t fp: %f
sensitivity: %f\tspecificity: %f
"""
    def __init__(self, settings):
        AttriChangeExper.__init__(self, settings)
        self.real_ab_flow_seq = None

    def get_ab_flow_seq(self):
        """get the sequence of all abnormal flows, get the reference ground truth"""
        normal_flow_file_name = self.settings.ROOT + '/Simulator/n0_flow.txt'
        self.normal_flow, self.fea_name = RawParseData(normal_flow_file_name)

        ab_flow_file_name = self.settings.ROOT + '/Simulator/abnormal_n0_flow.txt'
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

    def eval_diff_ab_win_num(self):
        """eval the results under difference abnormal window number"""
        entropy_type_vec = ['mf', 'mb']
        rec = dict()
        for entropy_type in entropy_type_vec:
            rec[entropy_type] = []
            for ab_win_num in xrange(1, 100, 2):
                print 'ab_win_num, ', ab_win_num
                res = self.eval(ab_win_num=ab_win_num, entropy_type=entropy_type)
                print self.OUT_STRING%res
                rec[entropy_type].append(res)

        pickle.dump(rec, open(self.settings.ROOT+'/res/diff_ab_win_num.pk', 'w'))

    def compare_ident_method(self, ab_win_num = 40):
        """compare different identification method.calculate the statistical measure
        to show the performance
        refer the return value of self.eval for the metric calculated for different
        identification method.

        **ab_win_num** specify the number of windows that selected as abnormal window. So
        it influence the performance of the original stochasticl detecotring before applying
        the flow state identification techiniques. More specifically, it influence the largest
        true positive rate the stotchastic detector can achieve.
        """
        idents= {
                'ComponentFlowStateIdent':'mf',
                'DerivativeFlowStateIdent':'mf',
                'ComponentFlowPairIdent':'mb',
                'DerivativeFlowPairIdent':'mb',
                }
        max_ab_state_num = dict(mf=12, mb=144) # it influence the max ab_state_num it will search
        rec = dict(zip(idents.keys(), [list() for i in xrange(len(idents))]))
        for ident_type, entropy_type in idents.iteritems():
            print 'ident_type, ', ident_type
            for ab_states_num in xrange(max_ab_state_num[entropy_type]):
                print 'ab_states_num, ', ab_states_num
                res = self.eval(ident_type=ident_type,
                        entropy_type=entropy_type,
                        ab_states_num=ab_states_num,
                        ab_win_num=ab_win_num)

                print self.OUT_STRING%res
                rec[ident_type].append(res)

        pickle.dump(rec, open(self.settings.ROOT + '/res/compare_ident.pk', 'w'))


        # self._vis_eval_diff_ab_state_num()

    def eval_hoeffding(self):
        """evaluate the performance of detector under the hoeffding optimal rule"""
        false_alarm_rate = 0.05
        entropy_threshold = self.detector.get_hoeffding_threshold(false_alarm_rate)
        res = self.eval(ident_type='ComponentFlowStateIdent',
                entropy_type='mf',
                entropy_threshold=entropy_threshold,
                ab_states_num=2)
        print self.OUT_STRING%res

    def eval(self, ident_type=None, entropy_type=None, portion=None, ab_states_num=None,
            entropy_threshold=None, ab_win_portion=None, ab_win_num=None):
        """
        calculate the true positive, false negative, true negative, false positive, sensitivity and
        specificity for a given detection
        **sensitivity** is the probability of a alarm given that the this flow is anormalous
        **specificity** is the probability of there isn't alarm given that the flow is normal
        """
        if not self.real_ab_flow_seq:
            self.real_ab_flow_seq = self.get_ab_flow_seq()
        ab_states = None
        if ident_type is not None:
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

        return tp, fn, tn, fp

    def _get_intersection_ratio(self, A, B):
        self.ins = set.intersection(set(A), set(B))
        self.uns = set.union(set(A), B)
        return len(self.ins) * 1.0 / len(self.uns)


   #############################################################################
   ##         Visualization Part                                           #####
   #############################################################################
    def _vis(self, data_name, ident_type_set, fea_handler, title, xlabel=None, ylabel=None,
            pic_name=None, pic_show=False, ylim=None, xlim=None,
            markers='>^+*', line_styles=('-', '-.', '--'),
            subplot=None):
        """visualize the attribute"""
        rec = pickle.load(open(data_name, 'r'))
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

    def _vis_roc(self, markers=' ', *args, **kwargs):
        """plot the ROC curve given the data"""
        def roc(data):
            tpv, fnv, tnv, fpv, _, _ = data
            tpr = [ tp * 1.0 / (tp + fn) for tp, fn in zip(tpv, fnv)]
            # calculate the false positive rate
            fpr = [ fp * 1.0 / (fp + tn) for fp, tn in zip(fpv, tnv)]
            print 'fpr, ', fpr
            print 'tpr, ', tpr
            return fpr, tpr

        fea_handler = dict(ROC=roc)
        self._vis(fea_handler=fea_handler, xlim=[0, 1], ylim=[0, 1.1], markers=markers, *args, **kwargs)

    def plot_roc_curve_ident(self):
        """plot ROC Curve for detection with flow state(transition pair) identification"""
        self._vis_roc(
                # data_name = './difference_ab_state_num.pk',
                data_name = self.settings.ROOT+'/res/compare_ident.pk',
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

        self._vis_roc(
                # data_name = './difference_ab_state_num.pk',
                data_name = self.settings.ROOT+'/res/compare_ident.pk',
                ident_type_set = ['DerivativeFlowStateIdent', 'DerivativeFlowPairIdent'],
                # ident_type_set = ['DerivativeFlowPairIdent'],
                title = 'ROC curve of detector with derivative flow identification',
                xlabel = 'false positive rate',
                ylabel = 'true positive rate',
                pic_name = self.settings.ROOT+'/res/flow_ident_roc.eps',
                # subplot = [None, 211],
                subplot = 212,
                # pic_show = True
                )
    def plot_roc_curve(self):
        self._vis_roc(
                data_name = self.settings.ROOT+'/res/diff_ab_win_num.pk',
                ident_type_set = ['mf', 'mb'],
                title = 'ROC curve of stochastic anomaly detector',
                xlabel = 'false positive rate',
                ylabel = 'true positive rate',
                pic_name = self.settings.ROOT+'/res/flow_roc.eps',
                # pic_show = True
                markers='o+'
                )

    def plot_roc_curve_seperate(self):
        self._vis_roc(
                data_name = self.settings.ROOT+'/res/diff_ab_win_num.pk',
                ident_type_set = ['mf'],
                title = 'ROC curve of stochastic anomaly detector',
                xlabel = 'false positive rate',
                ylabel = 'true positive rate',
                pic_name = self.settings.ROOT+'/res/flow_roc.eps',
                # pic_show = True
                markers='o+',
                subplot = 211,
                )

        self._vis_roc(
                data_name = self.settings.ROOT+'/res/diff_ab_win_num.pk',
                ident_type_set = ['mb'],
                title = 'ROC curve of stochastic anomaly detector',
                xlabel = 'false positive rate',
                ylabel = 'true positive rate',
                pic_name = self.settings.ROOT+'/res/flow_roc.eps',
                # pic_show = True
                markers='o+',
                subplot = 212,
                )
        pass


    def _vis_eval_diff_ab_state_num(self):
        self._vis(
                data_name = self.settings.ROOT+'/res/compare_ident.pk',
                ident_type_set = ['ComponentFlowPairIdent', 'DerivativeFlowPairIdent'],
                fea_handler = dict(
                    sensitivity = lambda x: x[-1],
                    specificity = lambda x: x[-2],
                    ),
                title = 'sensitivity and specificity vs no. of abnormal flow transition pair',
                xlabel = 'no. of abnormal flow transition pair',
                ylabel = 'sensitivity and specificity',
                pic_name = self.settings.ROOT+'/res/difference_ab_tran_pair_num_sens_spec.eps',
                # pic_show = True
                )



        self._vis(
                data_name = self.settings.ROOT+'/res/compare_ident.pk',
                ident_type_set = ['ComponentFlowPairIdent', 'DerivativeFlowPairIdent'],
                fea_handler = dict(
                    fnr = lambda x: [1-v for v in x[-1]],
                    fpr = lambda x: [1-v for v in x[-2]],
                    ),
                title = 'fnr and fpr vs no. of abnormal flow transition pair',
                xlabel = 'no. of abnormal flow transition pair',
                ylabel = 'fnr and fpr',
                pic_name = self.settings.ROOT+'/res/difference_ab_tran_pair_num_fnr_fpr.eps'
                )




if __name__ == "__main__":
    import settings
    exper = Eval(settings)
    # exper.configure()
    # exper.simulate()
    # exper.detect()

    # exper.compare_ident_method()
    exper.plot_roc_curve_ident()
    # exper._vis_eval_diff_ab_state_num()

    # exper.eval_diff_ab_win_num()
    # exper.plot_roc_curve()
    # exper.plot_roc_curve_seperate()

    # exper.eval_mutiple()
    # exper.eval_hoeffding()
    # detector.plot_entropy()

