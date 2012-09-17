"""
Manual Topology Experiment with Background Traffic

"""
from __future__ import print_function
import settings
from core.ns3.NS3Config import TopologyNetBT
from experiments import experiment_factory
from core.configure import gen_anomaly_dot

ManualTopoExperiment = experiment_factory('ManualTopoExperiment', BaseClass)
from util import Namespace

zeros = lambda s:[[0 for i in xrange(s[1])] for j in xrange(s[0])]
def get_inet_adj_mat(fname):
    fid = open(fname, 'r')
    i = -1
    while True:
        i += 1
        line = fid.readline()
        if not line: break
        if i == 0:
            totnode, totlink = [int(s.strip()) for s in line.rsplit()]
            adj_mat = zeros([totnode, totnode])
            continue
        if i <= totnode: # ignore the position information
            continue

        _from, _to, _lineBuffer = [s.strip() for s in line.rsplit()]
        adj_mat[int(_from)][int(_to)] = 1
    fid.close()

    return adj_mat

class ManualTopoBTExperiment(ManualTopoExperiment):
    """This is a extension of manual topology experiment which add background traffic
    to the network. """
    DOT_FILE = settings.ROOT + '/net_config/ManualTopoBTTopology.dot'
    def initparser(self, parser):
        ManualTopoExperiment.initparser(self, parser)

        parser.set_defaults(back_traf="net_config/back_traf.py",
                )
        parser.add_option('--back_traf', dest="back_traf",
                help='parameters for back ground traffic',
                )

    def load_back_traf(self, **kwargs):
        """load parameters for generating the background traffic. **kwargs** contains some
        additional parameters"""
        s = kwargs
        execfile(settings.ROOT + '/' + self.options.back_traf, s)
        return Namespace(s)

    def load_exper_settings(self, ns):
        from util import CIDR_to_subnet_mask
        # botnet related configuration
        self.server_id_set = ns.server_id_set
        self.botmaster_id_set = ns.botmaster_id_set
        self.client_id_set = ns.client_id_set
        # print('ns.server_addr', ns.server_addr)

        # parse the server address
        if len(ns.server_addr) == 0:
            self.SERVER_ADDR = ''
            self.NETWORK_BASE = ''
            self.IP_MASK = ''
        else:
            self.SERVER_ADDR, self.NETWORK_BASE, self.IP_MASK = CIDR_to_subnet_mask(ns.server_addr[0]);

    # @staticmethod
    def gen_back_traf_dot(self, net_settings):
        """generate background traffic dot file
        """
        # TODO generate netDesc, normalDesc
        def get_trace_config(net_settings):
            """transform net_setting to trace config"""
            keys = ['pcap_links', 'pcap_nodes',
                    'server_id_set', 'botmaster_id_set', 'client_id_set',
                    'server_addr']
            ns = dict.copy(net_settings)
            return dict(elem for elem in ns.items() if elem[0] in keys)

        # get back_traf parameter
        topo = get_inet_adj_mat(settings.ROOT + '/' + self.options.topology_file)
        back_traf = self.load_back_traf(
                topo = topo,
                srv_node_list = net_settings.server_id_set,
                sim_t = self.options.simtime,
                )

        # call the SADIT/Configure module to generate the dot file specifying the background
        # traffic pattern.
        gen_anomaly_dot(back_traf.ANO_LIST, back_traf.NET_DESC, back_traf.NORM_DESC, self.DOT_FILE)
        return self.DOT_FILE, get_trace_config(net_settings)

    def setup(self):
        BaseClass.setup(self)
        net_settings = self.load_net_settings()
        self.load_exper_settings(net_settings)

        # back_traf = self.load_back_traf() # get back_traf parameter
        dot_file, trace_config = self.gen_back_traf_dot(net_settings)

        self.net = TopologyNetBT(dot_file, trace_config)

        self.net.set_trace()
        self._install_cmds(srv_addr = self.SERVER_ADDR)
        self.print_srv_addr()
        self._set_server_info()
        self.start_nodes()

