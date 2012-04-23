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
        {'TYPE':'mv', 'flow_size':100, 'flow_arrival_rate':0.1},
        {'TYPE':'mv', 'flow_size':1000, 'flow_arrival_rate':0.1},
        {'TYPE':'mv', 'flow_size':100, 'flow_arrival_rate':1},
        {'TYPE':'mv', 'flow_size':1000, 'flow_arrival_rate':1},
        ]
# size of joint_dist equals to m * m ... *m, there n dimensions array and len of each
# dimension equals to m, n is the number of server nodes, m is hte possible type of flows
joint_dist = array([[0.025, 0.025, 0.025, 0.025],
                    [0.05, 0.05, 0.05, 0.05],
                    [0.05, 0.05, 0.05, 0.05],
                    [0.125, 0.125, 0.125, 0.125]])
norm_desc = dict(
        TYPE = 'NORMAl',
        start = '0',
        node_para = {'states':gen_para_type_list},
        profile = DEFAULT_PROFILE,
        joint_dist = joint_dist,
        interval = 100,
        )

net_desc = dict(
        topo=topo,
        size=topo.shape[0],
        srv_list=srv_node_list,
        link_attr=link_attr,
        node_type='MVNode',
        node_para={},
        )

ano_joint_dist = array([[0.125, 0.125, 0.125, 0.125],
                    [0.025, 0.025, 0.025, 0.025],
                    [0.05, 0.05, 0.05, 0.05],
                    [0.05, 0.05, 0.05, 0.05]
                    ])

ano_desc = {'anoType':'mv_anomaly',
        'ano_node_seq':2,
        'T':(1200, 1400),
        'change':{'joint_dist':ano_joint_dist},
        }

ano_list = [ano_desc]



import settings
def main():
    gen_anomaly_dot(ano_list, net_desc, norm_desc, settings.OUTPUT_DOT_FILE)
    simulate(settings.sim_t, settings.OUTPUT_DOT_FILE)
    print 'start detection'
    detect(settings.ROOT + '/Simulator/n0_flow.txt',
            settings.DETECTOR_DESC['win_size'],
            settings.DETECTOR_DESC['fea_option'],
            settings.DETECTOR_DESC['detector_type'],
            )
    print 'start detection'
    detect(settings.ROOT + '/Simulator/n0_flow.txt',
            settings.DETECTOR_DESC['win_size'],
            settings.DETECTOR_DESC['fea_option'],
            settings.DETECTOR_DESC['detector_type'],
            )




    pass

if __name__ == "__main__":
    main()

