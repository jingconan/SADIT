#!/usr/bin/env python
""" Simulation and Detect
"""
from Detect import Detect
from Sim import Sim
class SimDetect(Detect):
    """
        - net_desc: description of the network
        - norm_desc: description of the normal case
        - ano_list: list of anomalies.
    """
    def __init__(self, argv):
        Detect.__init__(self, argv)
        self.sim = Sim(argv)

        self.output_flow_file = self.ROOT + \
                '/Simulator/n%i_flow.txt'%(self.args.detect_node_id)
        self.args.data = self.output_flow_file

        self.export_abnormal_flow_file = self.ROOT + \
                '/Simulator/abnormal_n%i_flow.txt'%(self.args.detect_node_id)

    def init_parser(self, parser):
        Detect.init_parser(self, parser)
        parser.add_argument('--detect_node_id', default=0, type=int,
                help = """ specify the node id you want to monitor,
                default value is 0""")
        parser.add_argument('--no_sim', default=False, action='store_true',
                help = """turn on this switch to disable the fs simulaiton""")

    def run(self):
        if not self.args.no_sim:
            self.sim.run()
        Detect.run(self)
        return self.detector
