from Node import *
from Edge import *
from Generator import *
from mod_util import GetIPAdress, FixQuoteBug

from Address import Ipv4AddressHelper

node_map = {
        'NNode':NNode,
        'MarkovNode':MarkovNode,
        'MVNode':MVNode,
        }

####################################
##     Main Class Definition     ###
####################################
class Network(Dot):
    ''' Network Class specifiy the topology of the network.
    '''
    def __init__(self):
        Dot.__init__(self, 'SimConf', graph_type='graph')
        self.node_list = []
        self.NODE_NUM = 0
        self.IPSrcSet, self.AnoSet, _ = GetIPAdress()
        self.mv = None
        # self.Node = node_init_handle

        network = '10.0.7.0'
        mask = '255.255.255.0'
        base = '0.0.0.4'
        self.addr_helper = Ipv4AddressHelper(network, mask, base)

    def init(self, net_desc, norm_desc):
        self.net_desc = net_desc
        self.Node = node_map[self.net_desc['node_type']]
        self.norm_desc = norm_desc
        self._topo(self.net_desc['topo'])
        self._config_traffic()

    def _config_traffic(self):
        """config the traffic of network"""
        nn = len(self.node_list)
        srv_node_list = [self.node_list[i] for i in xrange(nn) if i in self.net_desc['srv_list'] ]
        for i in xrange(nn):
            if i in self.net_desc['srv_list']:
                continue
            self.node_list[i].init_traffic(self.norm_desc, srv_node_list)

    def _topo(self, topo):
        """initialize the topology of the network"""
        # n, _ = topo.shape
        n = len(topo)
        assert(n == len(topo[0]) )
        self.NodeList = []
        for i in xrange(n):
            # FIXME Add start, end to the parameter list
            # node = self.Node([self.IPSrcSet[i]], i, **self.net_desc['node_para'])
            node = self.Node([], i, **self.net_desc['node_para'])
            self.node_list.append(node)
            self.add_node(node)
            # if self.mv: mv.MHarpoon(node)

        for i in xrange(n):
            for j in xrange(n):
                # if topo[i, j]:
                if topo[i][j]:
                    edge = NEdge(self.node_list[i], self.node_list[j], self.net_desc['link_attr'])
                    self.assign_link_interface_ip(i, j)
                    self.add_edge(edge)

    def assign_link_interface_ip(self, i, j):
        node_container = [self.node_list[i], self.node_list[j]]
        self.addr_helper.Assign(node_container)
        self.addr_helper.NewNetwork()

    def write(self, fName):
        '''write the DOT file to *fName*'''
        for node in self.node_list:
            node.sync()
        Dot.write(self, fName)
        FixQuoteBug(fName, float(self.net_desc['link_attr']['delay']))

    def InjectAnomaly(self, A):
        '''Inject Anomaly into the network. A is the one type Anomaly'''
        A.run(self)
