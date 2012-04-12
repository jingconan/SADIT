from numpy import *

### ROOT is the root directory for you directory, be aware to change this before you try to run the code
ROOT = '/Users/wangjing/Dropbox/Research/CyberSecurity/code/sadit'

#################################
##   Parameter For Normal Case ##
#################################
sim_t = 3000
start = 0
DEFAULT_PROFILE = ((sim_t,),(1,))

NORM_DESC = dict(
        TYPE = 'NORMAl',
        start = '0',
        gen_desc = {'TYPE':'harpoon', 'flow_size_mean':'4e5', 'flow_size_var':'100', 'flow_arrival_rate':'0.5'},
        profile = DEFAULT_PROFILE,
        )

g_size = 10
srv_node_list = [0, 1]
# srv_node_list = [0]
topo = zeros([g_size, g_size])
for i in xrange(g_size):
    if i in srv_node_list:
        continue
    topo[i, srv_node_list] = 1
link_attr = {'weight':'10', 'capacity':'10000000', 'delay':'0.01'} # link Attribute
ANO_DESC = {'anoType':'TARGET_ONE_SERVER',
        'ano_node_seq':2,
        'T':(1200, 1400),
        'change':{'flow_arrival_rate':1.5},
        'srv_id':0,
        }
ANO_LIST = [ANO_DESC]

NET_DESC = dict(
        topo=topo,
        size=topo.shape[0],
        srv_list=srv_node_list,
        link_attr=link_attr,
        )


OUTPUT_DOT_FILE = ROOT + '/test/conf.dot'
IPS_FILE = ROOT + '/Configure/ips.txt'
