#!/usr/bin/env python
""" Will generate the flows record when all the users
follow Markovian model and test with the anomaly detectors
"""
import sys
sys.path.append("..")
# from Experiment import Experiment
from FlowStylizedValidationExper import FlowStylizedValidationExper
# import numpy as np

def Pi2P(pi1Vec):
    p21 = 0.1
    res = []
    for pi1 in pi1Vec:
        p12 = p21 / pi1 - p21
        assert(p12 <= 1)
        res.append( (p12, p21) )
    return res

class MarkovExper(FlowStylizedValidationExper):
    # def __init__(self, settings):
    def __init__(self, *args, **kwargs):
        self.g_size = 10
        self.srv_node_list = (0, 1)
        # self.normal_sta_prob = (0.1, 0.9)
        # self.ano_sta_prob = (0.9, 0.1)
        self.normal_sta_prob = (0, 1)
        self.ano_sta_prob = (1, 0)
        H = {'TYPE':'harpoon', 'flow_size_mean':'4e5', 'flow_size_var':'10', 'flow_arrival_rate':'3'}
        L = {'TYPE':'harpoon', 'flow_size_mean':'4e5', 'flow_size_var':'10', 'flow_arrival_rate':'0.3'}
        self.states = [H, L]

        # Experiment.__init__(self, settings)
        super(MarkovExper, self).__init__(*args, **kwargs)

    def configure(self):
        self.get_net_desc()
        self.get_norm_desc()
        self.get_ano_list()
        super(MarkovExper, self).configure()

    def get_net_desc(self):
        self.net_desc['node_type'] = 'MarkovNode'
        self.net_desc['node_para'] = {
                # 'P':Pi2P(self.normal_sta_prob),
                'P': self.normal_sta_prob, # FIXME use stationary prob
                # 'interval':10,
                'interval':30,
                }

    def get_norm_desc(self):
       self.norm_desc['node_para'] = {
                'states':self.states,
                }

    def get_ano_list(self):
        # ano_markov_prob = Pi2P(self.ano_sta_prob)
        ano_markov_prob = self.ano_sta_prob # FIXME use stationary prob

        ano_desc = {'anoType':'markov_anomaly',
                'ano_node_seq':2,
                'T':(1200, 1400),
                'ano_markov_desc':{'P':ano_markov_prob, 'interval':20},
                'srv_id':0,
                }
        self.ano_list = [ano_desc]

    @property
    def topo(self): return self.get_star_topo()


    # def run(self):
    #     exper.configure()
    #     exper.simulate()
    #     detector = exper.detect()
    #     detector.plot_entropy()


if __name__ == "__main__":
    import settings
    exper = MarkovExper(settings)
    exper.configure()
    exper.simulate()
    detector = exper.detect()
    detector.plot_entropy()
