#!/usr/bin/env python
""" Flow Stylized Validation Experiemnt. Properties
of flow will be changed( flow size mean, flow access rate), e.t.c
and test with anomaly detectors.
"""
from Configure import gen_anomaly_dot
# from Detector import detect
# from Detect import Detect
# import settings

from os import chdir as cd
from os import system as sh

# import argparse
from util import load_para, Namespace
from DetectExper import DetectExper
class FlowStylizedValidationExper(DetectExper):
    """
        - net_desc: description of the network
        - norm_desc: description of the normal case
        - ano_list: list of anomalies.
    """

    def __init__(self, *args, **kwargs):
        super(FlowStylizedValidationExper, self).__init__(*args, **kwargs)
        default_settings = load_para(self.args.default_settings, Namespace)
        self.ano_list = default_settings.ANO_LIST
        self.net_desc = default_settings.NET_DESC
        self.dot_file = default_settings.OUTPUT_DOT_FILE
        self.norm_desc = default_settings.NORM_DESC
        self.sim_t = default_settings.sim_t
        # self.ROOT = default_settings.ROOT
        self.output_flow_file = self.ROOT + '/Simulator/n%i_flow.txt'%(self.args.detect_node_id)
        self.export_abnormal_flow_file = self.ROOT + '/Simulator/abnormal_n%i_flow.txt'%(self.args.detect_node_id)
        self.args.detect = self.output_flow_file

    def init_parser(self, parser):
        super(FlowStylizedValidationExper, self).init_parser(parser)
        parser.add_argument('--detect_node_id', default=0, type=int,
                help = """ specify the node id you want to monitor,
                default value is 0""")

    def configure(self):
        gen_anomaly_dot(self.ano_list, self.net_desc, self.norm_desc, self.dot_file)

    def simulate(self):
        cd(self.ROOT + '/Simulator')
        sh('python fs.py %s -t %d' %(self.dot_file, self.sim_t) )
        cd(self.ROOT)

    # def detect(self):
        # DetectExper.run(self)
        # return self.detector

    def run(self):
        # DetectExper.run(self)
        # return self.detector

        self.configure()
        self.simulate()
        # self.args.detect = self.ROOT + '/Simulator/n0_flow.txt'
        DetectExper.run(self)
        self.detect()
        return self.detector

class AttriChangeExper(FlowStylizedValidationExper):
    pass
