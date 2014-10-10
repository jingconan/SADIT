from __future__ import print_function, division, absolute_import
from pydot import Dot
from sadit.util import get_net_addr, CIDR_to_subnet_mask

from .Edge import NEdge
from .Node import NNode, MarkovNode
# from .Node import MVNode
from .mod_util import FixQuoteBug
from .Address import Ipv4AddressHelper


node_map = {
        'NNode':NNode,
        'MarkovNode':MarkovNode,
        # 'MVNode':MVNode,
        }

check_table = {
        'ms':1e-3,
        'kbps':1e3,
        'mbps':1e6,
        }
def convert_unit(val):
    """convert unit of delay and capacity to second and bps, respectively
    """
    val = val.lower()
    for k,v in check_table.iteritems():
        if k in val:
            return float(val.rsplit(k)[0]) * v

def link_attr_list_to_map(l):
    """ convert link attribute with list format to map format

    Parameters
    ---------------
    l : list of strings or dict
        if `l` is a dict, return it directly. If `l` is a list, l[0] is the
        string representation of 'delay' and l[1] is the string
        representation of 'capcacity'.

    Returns
    --------------
    m : dict
        - 'delay' : float
        - 'capacity' : int
        - 'weight' : str
            now it is set as '10'
    """
    if isinstance(l, dict): # dirty code for backword compatibility
        return l
    attr_name = ['delay', 'capacity']
    # han specify the format of the attribute
    han = { 'delay':float,
            'capacity':int
            }
    nl = [str(han[n](convert_unit(v))) for n, v in zip(attr_name, l)]
    m = dict(zip(attr_name, nl))
    m['weight'] = '10'
    return m

####################################
##     Main Class Definition     ###
####################################
class Network(Dot):
    """ Network Class specifiy the topology of the network.


    Attributes
    -------------
    node_list : list
        list of nodes
    net_desc : dict
        descriptor for the network
    norm_desc : dict
        descriptor for the normal traffic
    Node : constructor {NNode, MarkovNode, MVNode}
        constructor to create new Node
    addr_helper : Ipv4AddressHelper class
        manage Ipv4 Address

    """
    def __init__(self):
        Dot.__init__(self, 'SimConf', graph_type='graph')
        self.node_list = []

    def _init_addr_helper(self):
        """initialize the address helper"""
        ipv4_net_addr_base = self.net_desc.get('ipv4_net_addr_base', '10.0.7.4/24')
        addr, network, mask = CIDR_to_subnet_mask(ipv4_net_addr_base)
        base = get_net_addr(addr, mask)
        self.addr_helper = Ipv4AddressHelper(network, mask, base)

    def init(self, net_desc, norm_desc):
        """  Initialize the network

        Parameters
        ---------------
        net_desc : dict
            descriptor for network
        norm_desc : dict
            descriptor for normal traffic

        Returns
        --------------
        None
        """
        self.net_desc = net_desc
        self.norm_desc = norm_desc

        self._init_addr_helper()
        self.Node = node_map[net_desc['node_type']]
        self.create_topology(self.net_desc['topo'])
        self.config_traffic(self.norm_desc['src_nodes'],
                self.norm_desc['dst_nodes'])


    def config_traffic(self, src_nodes, dst_nodes):
        """ config the traffic of network, initialize traffic from any node in
        `src_nodes` to any node in `dst_Nodes`.

        Parameters
        ------------------
        src_nodes : list of ints
            sequences of source nodes
        dst_nodes : list of ints
            sequence of destination nodes
        """
        dst_node_list = [self.node_list[i] for i in dst_nodes]
        for i in src_nodes:
            self.node_list[i].init_traffic(self.norm_desc, dst_node_list)

    def create_topology(self, topo):
        """initialize the topology of the network

        Parameters
        -----------------
        topo : list of list, or numpy 2d array, or scipy sparse matrix
            adjacent matrix of the graph.

        """
        # n = len(topo)
        # assert(n == len(topo[0]) )
        def size(topo):
            return len(topo) if isinstance(topo, list) else topo.shape[0]

        for i in xrange(size(topo)):
            # Create node without specifying the ipdests
            node = self.Node([], i)
            self.node_list.append(node)
            self.add_node(node)

        def nonzero(topo):
            if isinstance(topo, list):
                n = len(topo)
                assert(n == len(topo[0]))
                return [(i, j) for i in xrange(n) for j in xrange(n) if
                        topo[i][j]]
            else:  # numpy matrix of scipy sparse matrix
                X, Y = topo.nonzero()
                return zip(X.reshape(-1), Y.reshape(-1))


        # for i in xrange(n):
            # for j in xrange(n):
                # if topo[i][j]:
        for (i, j) in nonzero(topo):
            la_dft = self.net_desc['link_attr_default']
            link_attr_list = self.net_desc.get('link_attr', {}).get((i, j), la_dft)
            edge = NEdge(self.node_list[i],
                         self.node_list[j],
                         link_attr_list_to_map(link_attr_list))
            self.assign_link_interface_ip(i, j)
            self.add_edge(edge)

    def assign_link_interface_ip(self, i, j):
        """ assign ip address for link between node i and node j

        Parameters
        ---------------
        i, j : int
            Node id for two end points of the link

        Returns
        --------------
        None

        Notes
        --------------
        `link_to_ip_map` is a dictionary defining the ip address for each link.
        If the link can be founded in `link_to_ip_map`, corresponding ip
        address will be assigned, otherwise `addr_helper` will create a new
        subnetwork for this link and assign ip addresses accordingly.

        """
        # if link_to_ip_map is defined and (i,j) is inside
        if_addr = self.net_desc.get('link_to_ip_map', {}).get((i,j), None)
        if if_addr is not None:
            if if_addr[0] is not '':
                self.node_list[i].add_interface_addr(if_addr[0])
            if if_addr[1] is not '':
                self.node_list[j].add_interface_addr(if_addr[1])
            return
        node_container = [self.node_list[i], self.node_list[j]]
        self.addr_helper.Assign(node_container)
        self.addr_helper.NewNetwork()

    def write(self, f_name):
        """write the DOT file to *fName*

        """
        for node in self.node_list:
            node.sync()
        Dot.write(self, f_name)
        # FixQuoteBug(fName, float(self.net_desc['link_attr']['delay']))
        FixQuoteBug(f_name)

    def inject_anomaly(self, A):
        """ Inject Anomaly into the network. A is the one type Anomaly

        Parameters
        ---------------------
        A : subclass of Anomaly

        Returns
        ----------------------
        None

        """
        A.run(self)
