#!/usr/bin/env python
import sys
sys.path.append("..")
from Experiment import Experiment
# import numpy as np

def Pi2P(pi1Vec):
    p21 = 0.1
    res = []
    for pi1 in pi1Vec:
        p12 = p21 / pi1 - p21
        assert(p12 <= 1)
        res.append( (p12, p21) )
    return res

class MarkovExperiment(Experiment):
    def __init__(self, settings):
        self.g_size = 10
        self.srv_node_list = (0, 1)
        self.normal_sta_prob = (0.1, 0.9)
        self.ano_sta_prob = (0.9, 0.1)
        H = {'TYPE':'harpoon', 'flow_size_mean':'4e4', 'flow_size_var':'100', 'flow_arrival_rate':'3'}
        L = {'TYPE':'harpoon', 'flow_size_mean':'4e3', 'flow_size_var':'100', 'flow_arrival_rate':'0.3'}
        self.states = [H, L]


        Experiment.__init__(self, settings)
        self.get_net_desc()
        self.get_norm_desc()
        self.get_ano_list()

    def get_net_desc(self):
        self.net_desc['node_type'] = 'MarkovNode'
        self.net_desc['node_para'] = {
                'P':Pi2P(self.normal_sta_prob),
                'interval':10,
                }

    def get_norm_desc(self):
       self.norm_desc['node_para'] = {
                'states':self.states,
                }

    def get_ano_list(self):
        ano_markov_prob = Pi2P(self.ano_sta_prob)
        ano_desc = {'anoType':'markov_anomaly',
                'ano_node_seq':2,
                'T':(1200, 1400),
                'ano_markov_desc':{'P':ano_markov_prob, 'interval':10},
                'srv_id':0,
                }
        self.ano_list = [ano_desc]

    @property
    def topo(self): return self.get_star_topo()

if __name__ == "__main__":
    import settings
    exper = MarkovExperiment(settings)
    exper.configure()
    exper.simulate()
    detector = exper.detect()
    detector.plot_entropy()
