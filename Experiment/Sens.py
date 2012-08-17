#!/usr/bin/env python
# Sensitivity Analysis of Anomaly Detection Method.
import sys
sys.path.append("..")
from Experiment import AttriChangeExper, gen_anomaly_dot
from matplotlib.pyplot import figure, plot, show, subplot, title, legend, savefig, xlabel, ylabel
import cPickle as pickle
import copy

def argsort(seq):
    #http://stackoverflow.com/questions/3382352/equivalent-of-numpy-argsort-in-basic-python/3382369#3382369
    #by ubuntu
    return sorted(range(len(seq)), key=seq.__getitem__)


class Sens(object):
    """base class for the sensitivity analysis"""
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

        # plot the curve in order
        sort_dict = sorted(det_obj_shelf.iteritems())
        keys = sorted(det_obj_shelf.iterkeys() )
        legend_txt = [k + ' x' for k in keys]

        for k, v in sort_dict:
            print 'k, ', k
            rt = v['winT']
            mf, mb = zip(*v['entropy'])
            plot(rt, mf)

        # plot the first threshold
        for k, v in sort_dict:
            if v['threshold']:
                plot(v['winT'], v['threshold'], '--')
                break

        title('model free')
        legend(legend_txt)
        ylabel('$I_1$')

        subplot(212)
        for k, v in sort_dict:
            rt = v['winT']
            mf, mb = zip(*v['entropy'])
            plot(rt, mb)

        # plot the first threshold
        for k, v in sort_dict:
            if v['threshold']:
                plot(v['winT'], v['threshold'], '--')
                break

        title('model based')
        legend(legend_txt)
        xlabel('time (s)')
        ylabel('$I_2$')
        savefig(self.settings.ROOT + '/Share/res.eps')
        show()

    def configure(self):
        gen_anomaly_dot([self.sens_ano], self.net_desc, self.norm_desc, self.dot_file)


class AttriSensExper(Sens, AttriChangeExper):
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
        Sens.__init__(self)
        self.sens_ano = settings.ANO_LIST[0]
        # self.shelve_file = '/home/jing/det_obj.out'
        self.shelve_file = self.settings.ROOT + '/Share/det_obj.out'

    def configure(self):
        Sens.configure(self)

    def run(self, attr, rg, far=None):
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
            detector = self.detect()
            det_obj = copy.deepcopy(detector)
            threshold = detector.get_hoeffding_threshold(far) if far else None
            det_obj_shelf[str(i)] = dict(winT=det_obj.record_data['winT'],
                    entropy=det_obj.record_data['entropy'], threshold=threshold)
            # v = det_obj.record_data['entropy']
            self.store_flow_file(str(i))
            self.clear_tmp_file()

        f_obj = open(self.shelve_file, 'w')
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
