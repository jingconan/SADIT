#!/usr/bin/env python
""" Flow Stylized Validation Experiemnt. Properties
of flow will be changed( flow size mean, flow access rate), e.t.c
and test with anomaly detectors.
"""
from Configure import gen_anomaly_dot
from os import chdir as cd
from os import system as sh

from util import load_para, Namespace
from DetectExper import DetectExper
class IIDExper(DetectExper):
    """
        - net_desc: description of the network
        - norm_desc: description of the normal case
        - ano_list: list of anomalies.
    """
    def __init__(self, *args, **kwargs):
        super(IIDExper, self).__init__(*args, **kwargs)
        default_settings = load_para(self.args.default_settings, Namespace)

        self.ano_list = default_settings.ANO_LIST
        self.net_desc = default_settings.NET_DESC
        self.dot_file = default_settings.OUTPUT_DOT_FILE
        self.norm_desc = default_settings.NORM_DESC
        self.sim_t = default_settings.sim_t

        # self.ROOT = default_settings.ROOT
        self.output_flow_file = self.ROOT + '/Simulator/n%i_flow.txt'%(self.args.detect_node_id)
        self.export_abnormal_flow_file = self.ROOT + '/Simulator/abnormal_n%i_flow.txt'%(self.args.detect_node_id)
        self.args.data = self.output_flow_file

    def init_parser(self, parser):
        super(IIDExper, self).init_parser(parser)
        parser.add_argument('--detect_node_id', default=0, type=int,
                help = """ specify the node id you want to monitor,
                default value is 0""")
        parser.add_argument('--no_sim', default=False, action='store_true',
                help = """turn on this switch to disable the fs simulaiton""")

    def configure(self):
        gen_anomaly_dot(self.ano_list, self.net_desc, self.norm_desc, self.dot_file)

    def simulate(self):
        cd(self.ROOT + '/Simulator')
        sh('python fs.py %s -t %d' %(self.dot_file, self.sim_t) )
        cd(self.ROOT)

    def run(self):
        if not self.args.no_sim:
            self.configure()
            self.simulate()
        super(IIDExper, self).run()
        return self.detector

class AttriChangeExper(IIDExper):
    pass
