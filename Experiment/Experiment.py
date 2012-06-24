#!/usr/bin/env python

import sys
sys.path.append("..")
from Configure import gen_anomaly_dot
from Detector import detect

from os import chdir as cd
from os import system as sh
import numpy as np

class Experiment(object):
    """
    base class for all experiments. Three important attributes
        - net_desc: description of the network
        - norm_desc: description of the normal case
        - ano_list: list of anomalies.
    settings module is used to initialize the experiment, we need have a
    settings.py file with attribute 1. **NET_DESC** 2. **NORM_DESC** 3. **ANO_LIST**
    """
    def __init__(self, settings):
        self.settings = settings
    @property
    def win_size(self): return self.settings.DETECTOR_DESC['win_size']
    @property
    def fea_option(self): return self.settings.DETECTOR_DESC['fea_option']
    @property
    def detector_type(self): return self.settings.DETECTOR_DESC['detector_type']
    @property
    def dot_file(self): return self.settings.OUTPUT_DOT_FILE
    @property
    def flow_file(self): return self.settings.ROOT + '/Simulator/n0_flow.txt'
    # def flow_file(self): return self.settings.ROOT + '/Simulator/n0_flow.txt'

    @property
    def ano_list(self): return self.settings.ANO_LIST
    @property
    def net_desc(self): return self.settings.NET_DESC
    @property
    def norm_desc(self): return self.settings.NORM_DESC

    @net_desc.setter
    def net_desc(self, v): self.settings.NET_DESC = v
    @norm_desc.setter
    def norm_desc(self, v): self.settings.NORM_DESC = v
    @ano_list.setter
    def ano_list(self, v): self.settings.ANO_LIST = v

    def update_settings(self, **argv):
        for k, v in argv.iteritems():
            exec 'self.settings.%s = v' %(k)

    def get_star_topo(self):
        g_size = self.g_size
        topo = np.zeros([g_size, g_size])
        for i in xrange(g_size):
            if i in self.srv_node_list:
                continue
            topo[i, self.srv_node_list] = 1
        return topo

    def configure(self):
        gen_anomaly_dot(self.ano_list, self.net_desc, self.norm_desc, self.dot_file)

    def simulate(self):
        cd(self.settings.ROOT + '/Simulator')
        sh('./fs.py %s -t %d' %(self.settings.OUTPUT_DOT_FILE, self.settings.sim_t) )
        cd(self.settings.ROOT)

    def detect(self):
        # return detect(self.flow_file, self.win_size, self.fea_option, self.detector_type, self.settings.DETECTOR_DESC)
        return detect(self.flow_file, self.settings.DETECTOR_DESC)

class AttriChangeExper(Experiment):
    def __init__(self, settings):
        Experiment.__init__(self, settings)

if __name__ == "__main__":
    import settings
    exper = AttriChangeExper(settings)
    exper.configure()
    exper.simulate()
    detector = exper.detect()
    detector.plot_entropy()

