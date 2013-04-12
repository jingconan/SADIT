#!/usr/bin/env python
########################
### MVBehaviour test ###
########################

from unittest import TestCase, main, skip
from Behaviour import MVBehaviour
import numpy as np

class MVBehaveTest(MVBehaviour):
    def stage(self):
        pass

@skip("classing skipping")
class TestMultiServer(TestCase):
    def setUp(self):
        joint_dist = np.array([[0.2, 0.1],
            [0.1, 0.6]])
        self.mv_beh = MVBehaveTest(joint_dist, None, 0.1)

    def testBehave(self):
        self.mv_beh.behave(0, 1000)
        self.mv_beh._sample_freq()

########################
### MVBehaviour test ###
########################
gen_para_type_list = [
        {'TYPE':'mv', 'flow_size':100, 'flow_arrival_rate':0.1},
        {'TYPE':'mv', 'flow_size':1000, 'flow_arrival_rate':0.1},
        {'TYPE':'mv', 'flow_size':100, 'flow_arrival_rate':1},
        {'TYPE':'mv', 'flow_size':1000, 'flow_arrival_rate':1},
        ]
from Generator import MVGenerator
@skip("classing skipping")
class TestMSGenerator(TestCase):
    def setUp(self):
        pass
    def testSync(self):
        print '------ start to test generator --------'
        for no in range(4):
            mv = MVGenerator(type_no = no,
                    ipsrc = '0.0.0.0',
                    ipdst = '0.0.0.0',
                    states = gen_para_type_list,
                    TYPE = 'harpoon')
            mv.sync()
            # print mv

########################
### MVNode test ###
########################


########################
### Network test  ###
########################



#################################
##   topology ##
#################################
from numpy import zeros, array
g_size = 10
srv_node_list = [0]
# srv_node_list = [0, 1]
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

gen_desc = {'TYPE':'harpoon', 'flow_size_mean':'4e3', 'flow_size_var':'100', 'flow_arrival_rate':'1'}
gen_para_type_list =[gen_desc]
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
        # size=topo.shape[0],
        size = len(topo),
        srv_list=srv_node_list,
        link_attr=link_attr,
        # node_type='MVNode',
        node_type = 'NNode',
        node_para={},
        )

from Network import Network
# @skip("classing skipping")
class TestNetwork(TestCase):
    def setUp(self):
        pass

    def testNetwork(self):
        net = Network()
        net.init(net_desc, norm_desc)
        net.write('./res.dot')

if __name__ == "__main__":
    main()


