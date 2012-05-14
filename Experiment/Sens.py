#!/usr/bin/env python
# Sensitivity Analysis of Anomaly Detection Method.
import sys
sys.path.append("..")
from Experiment import AttriChangeExper, gen_anomaly_dot
from matplotlib.pyplot import figure, plot, show, subplot, title, legend
import cPickle as pickle

import copy
class SensExper(AttriChangeExper):
    def __init__(self, settings):
        AttriChangeExper.__init__(self, settings)
        self.sens_ano = settings.ANO_LIST[0]
        self.shelve_file = '/home/jing/det_obj.out'

    def run(self, attr, rg):
        det_obj_shelf = dict()
        # self.sens_ano['ano_type'] = 'flow_arrival_rate'
        self.sens_ano['ano_type'] = attr
        # figure()
        # for i in [2, 4, 6]:
        for i in rg:
            # self.sens_ano['change']['flow_arrival_rate'] = i;
            self.sens_ano['change'][attr] = i;
            # self.ano_list[0]['change']['flow_arrival_rate'] = i;
            self.configure()
            self.simulate()
            det_obj = copy.deepcopy( self.detect() )
            det_obj_shelf[str(i)] = dict(winT=det_obj.record_data['winT'],
                    entropy=det_obj.record_data['entropy'])
            v = det_obj.record_data['entropy']
            # plot(zip(*v)[0])
            self.clear_tmp_file()

        f_obj = open(self.shelve_file, 'w')
        pickle.dump(det_obj_shelf, f_obj)
        f_obj.close()

    def clear_tmp_file(self):
        import os
        os.system('rm %s'%(self.dot_file))
        os.system('rm %s'%(self.flow_file))

    def plot_entropy(self):
        f_obj = open(self.shelve_file, 'r')
        det_obj_shelf = pickle.load(f_obj)
        f_obj.close()
        figure()
        subplot(211)
        for k, v in det_obj_shelf.iteritems():
            print 'k, ', k
            rt = v['winT']
            mf, mb = zip(*v['entropy'])
            plot(rt, mf)

        title('model free')
        legend(det_obj_shelf.keys())

        subplot(212)
        for k, v in det_obj_shelf.iteritems():
            rt = v['winT']
            mf, mb = zip(*v['entropy'])
            plot(rt, mb)

        title('model based')
        legend(det_obj_shelf.keys())
        show()

    def configure(self):
        gen_anomaly_dot([self.sens_ano], self.net_desc, self.norm_desc, self.dot_file)
        # gen_anomaly_dot(self.ano_list, self.net_desc, self.norm_desc, self.dot_file)

if __name__ == "__main__":
    import settings
    exper = SensExper(settings)
    exper.run('flow_arrival_rate', [2, 4, 6])
    exper.plot_entropy()
