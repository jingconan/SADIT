from Node import *
from Edge import *
from Generator import *

node_map = {
        'NNode':NNode,
        'MarkovNode':MarkovNode
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
        global NODE_NUM
        NODE_NUM = 0
        self.IPSrcSet, self.AnoSet, _ = GetIPAdress()
        self.mv = None
        # self.Node = node_init_handle

    def init(self, net_desc, norm_desc):
        self.net_desc = net_desc
        self.Node = node_map[self.net_desc['node_type']]
        self.norm_desc = norm_desc
        self._topo(self.net_desc['topo'])
        self._config_traffic()

    def _get_generator(self, src_node, dst_node):
        # import pdb;pdb.set_trace()
        para = self.norm_desc['node_para']
        res = []
        for state in para['states']:
            s = Load(state)
            s['ipsrc'] = choose_ip_addr(src_node.ipdests)
            s['ipdst'] = choose_ip_addr(dst_node.ipdests)
            gen = get_generator(s)
            res.append(gen)
        return res

    def _config_traffic(self):
        """config the traffic of network"""
        nn = len(self.node_list)
        srv_node_list = [self.node_list[i] for i in xrange(nn) if i in self.net_desc['srv_list'] ]
        for i in xrange(nn):
            if i in self.net_desc['srv_list']:
                continue
            node = self.node_list[i]
            for srv_node in srv_node_list:
                # self._add_modulator(node, srv_node)
                start = self.norm_desc['start']
                profile = self.norm_desc['profile']
                node.add_modulator(start, profile,
                        self._get_generator(node, srv_node))

    def _topo(self, topo):
        """initialize the topology of the network"""
        n, _ = topo.shape
        assert(n == _)
        self.NodeList = []
        print 'n, ', n
        for i in xrange(n):
            # FIXME Add start, end to the parameter list
            node = self.Node([self.IPSrcSet[i]], **self.net_desc['node_para']) #FIXME no necessary to be NNode
            self.node_list.append(node)
            self.add_node(node)
            if self.mv: mv.MHarpoon(node)

        for i in xrange(n):
            for j in xrange(n):
                if topo[i, j]:
                    edge = NEdge(self.node_list[i], self.node_list[j], self.net_desc['link_attr'])
                    self.add_edge(edge)

    def write(self, fName):
        '''write the DOT file to *fName*'''
        for node in self.node_list:
            node.sync()
        Dot.write(self, fName)
        FixQuoteBug(fName, float(self.net_desc['link_attr']['delay']))

    def InjectAnomaly(self, A):
        '''Inject Anomaly into the network. A is the one type Anomaly'''
        A.run(self)


