#!/usr/bin/env python
from Configure import gen_anomaly_dot
from Detector import detect

from os import chdir as cd
from os import system as sh
def simulate(total_t, dot_path):
    # total_t = settings.sim_t
    # dot_path = settings.OUTPUT_DOT_FILE
    cd('./Simulator')
    sh( './fs.py %s -t %d' %(dot_path, total_t) )
    cd('..')


#################################
##   topology ##
#################################
from numpy import zeros, array
g_size = 10
srv_node_list = (0, 1)
topo = zeros([g_size, g_size])
for i in xrange(g_size):
    if i in srv_node_list:
        continue
    topo[i, srv_node_list] = 1
link_attr = {'weight':'10', 'capacity':'10000000', 'delay':'0.01'} # link Attribute

sim_t = 3000
start = 0
DEFAULT_PROFILE = ((sim_t,),(1,))

gen_para_type_list = [
        {'TYPE':'mv', 'flow_size':1e3, 'flow_arrival_rate':0.1},
        # {'TYPE':'mv', 'flow_size':1e4, 'flow_arrival_rate':0.1},
        {'TYPE':'mv', 'flow_size':1e3, 'flow_arrival_rate':1},
        # {'TYPE':'mv', 'flow_size':1e4, 'flow_arrival_rate':1},
        ]
# size of joint_dist equals to m * m ... *m, there n dimensions array and len of each
# dimension equals to m, n is the number of server nodes, m is hte possible type of flows
# joint_dist = array([[0.025, 0.025, 0.025, 0.025],
    # [0.05, 0.03, 0.07, 0.05],
    # [0.04, 0.06, 0.05, 0.05],
    # [0.10, 0.15, 0.125, 0.125]])

joint_dist = array([[0.05, 0.05],
                    [0.45, 0.45]])

norm_desc = dict(
        TYPE = 'NORMAl',
        start = '0',
        node_para = {'states':gen_para_type_list},
        profile = DEFAULT_PROFILE,
        joint_dist = joint_dist,
        interval = 10,
        )

net_desc = dict(
        topo=topo,
        size=topo.shape[0],
        srv_list=srv_node_list,
        link_attr=link_attr,
        node_type='MVNode',
        node_para={},
        )


# from util import get_diff_jpdf
# ano_joint_dist = array([[0.125, 0.125, 0.125, 0.125],
                    # [0.025, 0.025, 0.025, 0.025],
                    # [0.05, 0.05, 0.05, 0.05],
                    # [0.05, 0.05, 0.05, 0.05]
                    # ])

ano_joint_dist = array([[0.05, 0.45],
                    [0.05, 0.45]])
import numpy as np
# ano_joint_dist = get_diff_jpdf(joint_dist, 5)
print 'ano_joint_dist, ', ano_joint_dist
assert(np.sum(joint_dist) == 1)
assert(np.sum(ano_joint_dist) == 1)
assert(not np.array_equal(ano_joint_dist,  joint_dist))

ano_desc = {'anoType':'mv_anomaly',
        'ano_node_seq':2,
        'T':(1200, 1400),
        'change':{'joint_dist':ano_joint_dist},
        }

ano_list = [ano_desc]

class Experiment(object):
    @property
    def win_size(self): return self.settings.DETECTOR_DESC['win_size']
    @property
    def fea_option(self): return self.settings.DETECTOR_DESC['fea_option']
    @property
    def detector_type(self): return self.settings.DETECTOR_DESC['detector_type']
    @property
    def dot_file(self): return self.settings.OUTPUT_DOT_FILE
    @property
    def ano_list(self): return self.settings.ANO_LIST
    @property
    def net_desc(self): return self.settings.NET_DESC
    @property
    def norm_desc(self): return self.settings.NORM_DESC
    @property
    def flow_file(self): return settings.ROOT + '/Simulator/n0_flow.txt'

class MultiSrvExperiment(Experiment):
    def __init__(self, settings):
        self.settings = settings

    def update_settings(self, **argv):
        for k, v in argv.iteritems():
            exec 'self.settings.%s = v' %(k)

    def configure(self):
        gen_anomaly_dot(self.ano_list, self.net_desc, self.norm_desc, self.dot_file)

    def simulate(self):
        simulate(settings.sim_t, settings.OUTPUT_DOT_FILE)

    def detect(self):
        detect(self.flow_file, self.win_size, self.fea_option, self.detector_type)


if __name__ == "__main__":
    import settings
    exper = MultiSrvExperiment(settings)
    exper.update_settings(ANO_LIST=ano_list, NET_DESC=net_desc, NORM_DESC=norm_desc)
    exper.configure()
    exper.simulate()
    exper.detect()
