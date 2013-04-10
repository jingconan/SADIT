#!/usr/bin/env python
""" Sensitivity analysis of anomaly detector under
attribute anomaly. The detector will be run under
different degree of attribute anoamly, and the output
will be drawn in the same plot.
"""
from __future__ import print_function, division
from IIDExper import AttriChangeExper, gen_anomaly_dot
import matplotlib.pyplot as plt
import cPickle as pickle
import copy

def argsort(seq):
    #http://stackoverflow.com/questions/3382352/equivalent-of-numpy-argsort-in-basic-python/3382369#3382369
    #by ubuntu
    return sorted(range(len(seq)), key=seq.__getitem__)


class Sens(object):
    """base class for the sensitivity analysis"""
    def store_flow_file(self, suffix):
        import shutil
        shutil.copyfile(self.output_flow_file, self.ROOT+'/Share/n0_flow_%s.txt'%(suffix))
        file_name = self.ROOT + '/Share/abnormal_flow_%s.txt'%(suffix)
        shutil.copyfile(self.export_abnormal_flow_file, file_name)

    def clear_tmp_file(self):
        import os
        os.system('rm %s'%(self.dot_file))
        os.system('rm %s'%(self.output_flow_file))

    def plot_entropy(self, store_res_file=None):
        # f_obj = open(self.shelve_file, 'r')
        # f_obj = open(self.args.store_res_file, 'r')
        f_obj = open(store_res_file, 'r')
        det_obj_shelf = pickle.load(f_obj)
        f_obj.close()
        plt.figure()
        plt.subplot(211)

        # plot the curve in order
        sort_dict = sorted(det_obj_shelf.iteritems())
        keys = sorted(det_obj_shelf.iterkeys() )
        # print('keys, ', keys)
        legend_txt = [str(k) + ' x' for k in keys]

        for k, v in sort_dict:
            # print 'k, ', k
            rt = v['winT']
            mf, mb = zip(*v['entropy'])
            plt.plot(rt, mf)

        # plot the first threshold
        for k, v in sort_dict:
            if v.get('threshold', None):
                plt.plot(v['winT'], v['threshold'], '--')
                break

        plt.title('model free')
        plt.legend(legend_txt)
        plt.ylabel('$I_1$')

        plt.subplot(212)
        for k, v in sort_dict:
            rt = v['winT']
            mf, mb = zip(*v['entropy'])
            plt.plot(rt, mb)

        # plot the first threshold
        for k, v in sort_dict:
            if v.get('threshold', None):
                plt.plot(v['winT'], v['threshold'], '--')
                break

        plt.title('model based')
        plt.legend(legend_txt)
        plt.xlabel('time (s)')
        plt.ylabel('$I_2$')
        plt.savefig(self.ROOT + '/Share/res.eps')
        plt.show()

    def configure(self):
        gen_anomaly_dot([self.sens_ano], self.net_desc, self.norm_desc, self.dot_file)


class AttriSensExper(Sens, AttriChangeExper):
    """SensExper is experiment to get the sensitivity result.
    it will change parameters and run the simulation for several times
    and plot the both model based and model free entropy
    ex:
    """
    def __init__(self, *args, **kwargs):
        AttriChangeExper.__init__(self, *args, **kwargs)
        Sens.__init__(self)
        self.sens_ano = self.ano_list[0]
        # self.shelve_file = '/home/jing/det_obj.out'
        self.shelve_file = self.ROOT + '/Share/det_obj.out'

    def configure(self):
        Sens.configure(self)

    def init_parser(self, parser):
        super(AttriSensExper, self).init_parser(parser)
        parser.add_argument('--sens_attr', default=None, type=str,
                help = """ specify the attribute you want to sensitivity
                analysis, can be [flow_arrival_rate | flow_size_mean | flow_size_var ]""")

        parser.add_argument('--rg', default=None, type=lambda x: [float(v)for v in x.rsplit(',')],
                help = """ specify the values for degreee of anomaly, shoule be a command seperated number
                for example: rg=2,3,4
                """)

        parser.add_argument('--store_res_file', default=self.ROOT + '/Share/det_obj.out',
                help="""file path to store the caculated results""")

        parser.add_argument('--plot', default=None,
                help = """plot previous calculated result""")

    def run(self):
        if self.args.plot:
            self.plot_entropy(self.args.plot)
            return

        if self.args.sens_attr is None or self.args.rg is None or self.args.detect_node_id is None:
            raise Exception('you need to specify --sens_attr, --rg and --detect_node_id option')
        self._run(self.args.sens_attr, self.args.rg, self.args.hoeff_far)

    def _run(self, attr, rg, far=None):
        """attr is the name of attribute that will be changed. possible
        attrs are :
            - flow_arrival_rate
            - flow_size_mean
            - flow_size_var
        rg is the list of possible values for *attr*.
        """
        print('attr, ', attr)
        print('rg, ', rg)
        det_obj_shelf = dict()
        self.sens_ano['ano_type'] = attr
        self.sens_ano['change'] = {}
        for i in rg:
            self.sens_ano['change'][attr] = i;
            self.configure()
            self.simulate()
            detector = self.detect()
            det_obj = copy.deepcopy(detector)
            threshold = detector.get_hoeffding_threshold(far) if far else None
            det_obj_shelf[str(i)] = dict(winT=det_obj.record_data['winT'],
                    entropy=det_obj.record_data['entropy'], threshold=threshold)
            # v = det_obj.record_data['entropy']
            self.store_flow_file(str(i))
            self.clear_tmp_file()

        # f_obj = open(self.shelve_file, 'w')
        f_obj = open(self.args.store_res_file, 'w')
        pickle.dump(det_obj_shelf, f_obj)
        f_obj.close()

if __name__ == "__main__":
    import settings
    exper = AttriSensExper(settings)
    # exper.run('flow_arrival_rate', [2, 4, 6])
    # exper.run('flow_arrival_rate', [6])
    # exper.run('flow_arrival_rate', [2, 3, 4, 5, 6])
    # exper.run('flow_arrival_rate', [0.1, 0.3, 0.4, 0.6, 0.8])
    # exper.run('flow_arrival_rate', [0.2, 0.4, 0.6])
    # exper.run('flow_size_mean', [2, 3, 4, 5], 0.1)
    # exper.run('flow_size_mean', [2, 3, 4, 1], 0.1)
    # exper.run('flow_arrival_rate', [2, 3, 4, 5], 0.1)
    # exper.run('flow_size_mean', [2], 0.1)
    # exper.run('flow_size_mean', [0.2, 0.4, 0.6])
    # exper.run('flow_size_var', [2, 3, 4, 5])
    exper.plot_entropy()
