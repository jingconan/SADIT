#!/usr/bin/env python
""" Flow Stylized Validation Experiemnt. Properties
of flow will be changed( flow size mean, flow access rate), e.t.c
and test with anomaly detectors.
"""
from Detect import Detect
from Sim import Sim
class SimDetect(Detect, Sim):
    """
        - net_desc: description of the network
        - norm_desc: description of the normal case
        - ano_list: list of anomalies.
    """
    def __init__(self, *args, **kwargs):
        Detect.__init__(self, *args, **kwargs)
        # Sim.__init__(self, self.ROOT, self.args.default_settings)
        Sim.__init__(self, *args, **kwargs)

        self.output_flow_file = self.ROOT + \
                '/Simulator/n%i_flow.txt'%(self.args.detect_node_id)
        self.args.data = self.output_flow_file

        self.export_abnormal_flow_file = self.ROOT + \
                '/Simulator/abnormal_n%i_flow.txt'%(self.args.detect_node_id)

    def init_parser(self, parser):
        # super(IIDExper, self).init_parser(parser)
        Detect.init_parser(self, parser)
        parser.add_argument('--detect_node_id', default=0, type=int,
                help = """ specify the node id you want to monitor,
                default value is 0""")
        parser.add_argument('--no_sim', default=False, action='store_true',
                help = """turn on this switch to disable the fs simulaiton""")

    def run(self):
        if not self.args.no_sim:
            Sim.run(self)
        Detect.run(self)
        return self.detector

class AttriChangeExper(SimDetect):
    pass
