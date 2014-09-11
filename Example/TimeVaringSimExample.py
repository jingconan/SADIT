# ROOT = '/home/wangjing/Dropbox/Research/sadit'
ROOT = '/home/jzh/software/sadit'

#################################
##   Network Topology ##
#################################
zeros = lambda s:[[0 for i in xrange(s[1])] for j in xrange(s[0])]
# from numpy import zeros

## --- Graph Size -----
g_size = 10

## --- Server Node List ----
srv_node_list = [0]

## --- Network topology -----
# - star topology for each server.
topo = zeros([g_size, g_size])
for i in xrange(g_size):
    if i in srv_node_list:
        continue
    # topo[i, srv_node_list] = 1
    for srv_node in srv_node_list:
        topo[i][srv_node] = 1

# link Attribute
link_attr_default = {
        'weight':'10',
        'capacity':'10000000',
        'delay':'0.01'
        }

NET_DESC = dict(
        topo=topo,
        size = len(topo),
        srv_list = srv_node_list,
        link_attr_default = link_attr_default,
        node_type = 'NNode',
        node_para = {},
        )

#################################
##   Parameter For Normal Case ##
#################################
sim_t = 3600 * 24 * 7 # simulation time
start = 0 # start time
DEFAULT_PROFILE = ((sim_t,),(1,))

gen_desc1 = {
        'TYPE':'harpoon', # type of flow generated, defined in fs
        'flow_size_mean':'4e3', # flow size is normal distribution. Mean
        'flow_size_var':'100', # variance
        'flow_arrival_rate':'0.1' # flow arrival is poisson distribution. Arrival rate
        }

import numpy as np
from numpy import loadtxt
dis_interval = 3600
shift1 =  {
        'flow_size_mean' : 1e3 * loadtxt(ROOT  + '/Example/traffic_val_a_week.txt'),
        'time' : np.array(range(168)) * 3600,
        'base_type': ['flow_size_mean'],
        # 'base_type': ['flow_arrival_rate'],
        }

NORM_DESC = dict(
        TYPE = 'dynamic',
        # TYPE = 'stationary',
        start = '0',
        sim_t = sim_t,
        node_para = {
                    'states': [gen_desc1],
                    'shifts': shift1,
                    },
        profile = DEFAULT_PROFILE,
        src_nodes = range(g_size),
        dst_nodes = srv_node_list,
        )

#################################
##   Parameter For Anomaly     ##
#################################
ANO_DESC_TEMP = {
        'anoType':'anomaly',
        'ano_node_seq':2,
        'T':'REPLACE_ME',
        'change':{'flow_size_mean':'x1.3'},
        'srv_id':0,
        }

ANO_LIST = []
import copy
# for i in [1, 2, 3, 4, 5, 6, 7]:
for i in range(1, 50):
    ano_desc = copy.deepcopy(ANO_DESC_TEMP)
    ano_desc['T'] = (i * 5000, i * 5000+ 1000)
    ANO_LIST.append(ano_desc)
