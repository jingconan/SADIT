#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
from .Anomaly import Anomaly
import cPickle as pickle

class MarkovAnomaly(Anomaly):
    def del_orig_mod_gen(self, m_id, mod):
        del self.ano_node.modulator[m_id]
        for s_id in mod.states:
            del self.ano_node.generator[s_id]

    def get_generator_list(self, mod):
        return [ self.ano_node.generator[s] for s in mod.states ]

    def add_ano_seg(self, start, ap, generator_list):
        self.ano_node.add_modulator(
                start=str(start),
                profile=ap,
                generator_list = generator_list,
                markov_desc = self.ano_desc['ano_markov_desc'],
                )

    def export_ano_flow_para(self):
        import settings
        import copy
        self.ano_flow_para = copy.deepcopy(self.ano_desc)
        self.ano_flow_para['ano_node_ipdests'] = self.ano_node.ipdests
        pickle.dump(self.ano_flow_para, open(settings.EXPORT_ABNORMAL_FLOW_PARA_FILE, 'w')) # For export abnormal flows
