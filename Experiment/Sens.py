#!/usr/bin/env python
# Sensitivity Analysis of Anomaly Detection Method.
import sys
sys.path.append("..")
from Experiment import AttriChangeExper, gen_anomaly_dot
from matplotlib.pyplot import figure, plot, show, subplot, title, legend
import cPickle as pickle
import copy

class SensExper(AttriChangeExper):
    """SensExper is experiment to get the sensitivity result.
    it will change parameters and run the simulation for several times
    and plot the both model based and model free entropy
    ex:
    .. code-block:: python

        import settings
        exper = SensExper(settings)
        exper.run('flow_arrival_rate', [2, 4, 6])
        exper.plot_entropy()

    """
    def __init__(self, settings):
        AttriChangeExper.__init__(self, settings)
        self.sens_ano = settings.ANO_LIST[0]
        self.shelve_file = '/home/jing/det_obj.out'

    def run(self, attr, rg):
        """attr is the name of attribute that will be changed. possible
        attrs are :
            - flow_arrival_rate
            - flow_size_mean
            - flow_size_var
        rg is the list of possible values for *attr*.
        """
        det_obj_shelf = dict()
        self.sens_ano['ano_type'] = attr
        self.sens_ano['change'] = {}
        for i in rg:
            self.sens_ano['change'][attr] = i;
            self.configure()
            self.simulate()
            det_obj = copy.deepcopy( self.detect() )
            det_obj_shelf[str(i)] = dict(winT=det_obj.record_data['winT'],
                    entropy=det_obj.record_data['entropy'])
            # v = det_obj.record_data['entropy']
            self.store_flow_file(str(i))
            self.clear_tmp_file()

        f_obj = open(self.shelve_file, 'w')
        pickle.dump(det_obj_shelf, f_obj)
        f_obj.close()

    def store_flow_file(self, suffix):
        import settings, shutil
        shutil.copyfile(settings.OUTPUT_FLOW_FILE, settings.ROOT+'/Share/n0_flow_%s.txt'%(suffix))
        file_name = settings.ROOT + '/Share/abnormal_flow_%s.txt'%(suffix)
        shutil.copyfile(settings.EXPORT_ABNORMAL_FLOW_FILE, file_name)

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

if __name__ == "__main__":
    import settings
    exper = SensExper(settings)
    exper.run('flow_arrival_rate', [1, 2, 3, 4, 5, 6])
    exper.plot_entropy()
