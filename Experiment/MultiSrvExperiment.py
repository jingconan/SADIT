#!/usr/bin/env python
import sys
sys.path.append("..")
import settings
from Experiment import Experiment
import numpy as np
from Detector import detect



class MultiSrvExperiment(Experiment):
    def __init__(self, settings):
        self.init_para()
        Experiment.__init__(self, settings)
        self.get_net_desc()
        self.get_norm_desc()
        self.get_ano_list()

        # fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':1}
        # self.settings.DETECTOR_DESC['fea_option'] = fea_option


    def two_flow_types(self):
        self.gen_para_type_list = [
                {'TYPE':'mv', 'flow_size':1e4, 'flow_arrival_rate':1},
                # {'TYPE':'mv', 'flow_size':1e4, 'flow_arrival_rate':0.1},
                {'TYPE':'mv', 'flow_size':1e3, 'flow_arrival_rate':0.1},
                # {'TYPE':'mv', 'flow_size':1e4, 'flow_arrival_rate':1},
                ]

        self.joint_dist = np.array([[0.05, 0.05],
                                    [0.45, 0.45]])
        self.ano_joint_dist = np.array([[0.45, 0.45],
                                   [0.05, 0.05]])
        # self.joint_dist = np.array([[1, 0],
                                    # [0, 0]])
        # self.ano_joint_dist = np.array([[0, 0],
                                    # [0, 1]])

    def four_flow_types(self):
        self.gen_para_type_list = [
                {'TYPE':'mv', 'flow_size':1e3, 'flow_arrival_rate':0.1},
                {'TYPE':'mv', 'flow_size':1e4, 'flow_arrival_rate':0.1},
                {'TYPE':'mv', 'flow_size':1e3, 'flow_arrival_rate':1},
                {'TYPE':'mv', 'flow_size':1e4, 'flow_arrival_rate':1},
                ]
        self.joint_dist = np.array([
                                    [0.85, 0.01, 0.01, 0.01],
                                    [0.01, 0.01, 0.01, 0.01],
                                    [0.01, 0.01, 0.01, 0.01],
                                    [0.01, 0.01, 0.01, 0.01],
                                    ])
        from util import get_diff_jpdf
        self.ano_joint_dist =  get_diff_jpdf(self.joint_dist, 4)
        assert( not np.array_equal(self.ano_joint_dist, self.joint_dist) )
        # self.joint_dist = np.array([
        #                             [1, 0, 0, 0],
        #                             [0, 0, 0, 0],
        #                             [0, 0, 0, 0],
        #                             [0, 0, 0, 0],
        #                             ])
        # self.ano_joint_dist = np.array([
        #                             [0, 0, 0, 0],
        #                             [0, 1, 0, 0],
        #                             [0, 0, 0, 0],
        #                             [0, 0, 0, 0],
        #                             ])


    def init_para(self):
        self.g_size = 10
        self.srv_node_list = (0, 1)
        # self.two_flow_types()
        self.four_flow_types()

        # ano_joint_dist = get_diff_jpdf(joint_dist, 5)
        print 'marginal dist for orig variable 1, ', np.sum(self.joint_dist, 0)
        print 'marginal dist for orig variable 2, ', np.sum(self.joint_dist, 1)
        print 'marginal dist for ano variable 1, ', np.sum(self.ano_joint_dist, 0)
        print 'marginal dist for ano variable 2, ', np.sum(self.ano_joint_dist, 1)
        print 'ano_joint_dist, ', self.ano_joint_dist
        print 'ano_sum, ', np.sum(self.ano_joint_dist)
        assert( abs( np.sum(self.ano_joint_dist) - 1) < 1e-3)
        assert(not np.array_equal(self.ano_joint_dist, self.joint_dist))

    @property
    def topo(self): return self.get_star_topo()

    def get_net_desc(self):
        self.net_desc['topo'] = self.topo
        self.net_desc['size'] = self.topo.shape[0]
        self.net_desc['srv_list'] = self.srv_node_list
        self.net_desc['node_type'] = 'MVNode'

    def get_norm_desc(self):
        self.norm_desc['node_para'] = {'states':self.gen_para_type_list}
        self.norm_desc['joint_dist'] = self.joint_dist
        self.norm_desc['interval'] = 10

    def get_ano_list(self):
        self.ano_list = []
        for seq in [2, 3, 4, 5, 6, 7, 8, 9]:
            ano_desc = {'anoType':'mv_anomaly',
                    'ano_node_seq':seq,
                    'T':(1200, 1500),
                    'change':{'joint_dist':self.ano_joint_dist},
                    }
            self.ano_list.append(ano_desc)

    def ms_detect(self):
        flow_file = [self.settings.ROOT + '/Simulator/n0_flow.txt',
                self.settings.ROOT + '/Simulator/n1_flow.txt']
        # print 'win_size, ', self.win_size
        # self.win_size = 10;
        detect(flow_file, self.win_size, self.fea_option, self.detector_type)
        # detect(flow_file, 30, self.fea_option, self.detector_type)

if __name__ == "__main__":
    exper = MultiSrvExperiment(settings)
    exper.configure()
    exper.simulate()
    # exper.detect()
    exper.ms_detect()
