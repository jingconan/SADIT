#!/usr/bin/env python
"""  Simualtion to generate the flow data
"""
from BaseExper import BaseExper
from Configure import gen_dot
from os import chdir as cd
from os import system as sh
import os
import os.path


class Sim(BaseExper):
    """
    Attributes:
    -----------------------
    net_desc : dict
        description of the network
    norm_desc : dict
        description of the normal case
    ano_list : list
        list of anomalies.

    """
    def __init__(self, argv):
        super(Sim, self).__init__(argv)

        self.ano_list = self.args.config['ANO_LIST']
        self.net_desc = self.args.config.get('NET_DESC')
        # self.dot_file = self.args.config['OUTPUT_DOT_FILE']
        self.norm_desc = self.args.config['NORM_DESC']
        self.sim_t = self.args.config['sim_t']
        self.dot_file = self.args.dot

    def init_parser(self, parser):
        super(Sim, self).init_parser(parser)
        parser.add_argument('--dot', default=self.ROOT + '/Share/conf.dot',
                            type=os.path.abspath,
                            help="""output dot file""")

        parser.add_argument('--export_ano', default=True,
                            type=bool,
                            help="""[true|false]whether to export abnormal flows or not""")
        parser.add_argument('--dir', default=None,
                            help="""output directory""")



    def configure(self):
        gen_dot(self.ano_list, self.net_desc, self.norm_desc,
                self.dot_file)

    def simulate(self):
        os.environ['EXPORT_ABNORMAL_FLOW'] = 'TRUE' if self.args.export_ano else 'FALSE'
        cd(self.ROOT + '/Simulator')
        sh('python fs.py %s -t %d' % (self.dot_file, self.sim_t))
        dir = self.args.dir
        if dir:
            if not os.path.exists(dir): os.makedirs(dir)
            sh('cp *.txt %s' % (dir))

        cd(self.ROOT)

    def run(self):
        self.configure()
        self.simulate()
