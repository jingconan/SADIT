#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
from .Anomaly import Anomaly
from sadit.util import zdump
from sadit import settings
import copy

class MarkovAnomaly(Anomaly):
    def del_orig_mod_gen(self, m_id, mod):
        del self.ano_node.modulator[m_id]
        for s_id in mod.states:
            del self.ano_node.generator[s_id]

    def get_generator_list(self, mod):
        return [ self.ano_node.generator[s] for s in mod.states ]

    def add_ano_seg(self, start, ap, generator_list):
        self.ano_node.add_modulator(start, ap, generator_list,
                self.ano_desc['node_para'])
        # import ipdb;ipdb.set_trace()

    def export_ano_flow_para(self):
        self.ano_flow_para = copy.deepcopy(self.ano_desc)
        self.ano_flow_para['ano_node_ipdests'] = self.ano_node.ipdests
        zdump(self.ano_flow_para, settings.EXPORT_ABNORMAL_FLOW_PARA_FILE) # For export abnormal flows
