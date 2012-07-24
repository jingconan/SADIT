#!/usr/bin/env python
from Anomaly import Anomaly
# import numpy as np
import cPickle as pickle

class MarkovAnomaly(Anomaly):
    def _infect_modulator(self, ano_t, m_id, mod):
        mod_start = eval(mod['start'])
        mod_profile = mod['profile']
        np1, ap, np2 = self.get_profile_with_ano(mod_start, mod_profile, ano_t)

        generator_list = self.get_generator_list(mod)
        self.ano_node.add_modulator(
                start=str(mod_start),
                profile=np1,
                generator_list = generator_list,
                )

        start, end = ano_t
        # st = mod_start + float(np.sum(np1[0]))
        st = mod_start + float(sum(np1[0]))
        assert(st == start)
        self.add_ano_seg(start, ap, generator_list)

        # st = mod_start + float(np.sum(np1[0])) + float(np.sum(ap[0]))
        st = mod_start + float(sum(np1[0])) + float(sum(ap[0]))
        assert(st == end)
        self.ano_node.add_modulator(
                start=str(end),
                profile=np2,
                generator_list = generator_list,
                )

        self.del_orig_mod_gen(m_id, mod)

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

    def _export_ano_flow_para(self):
        import settings
        import copy
        self.ano_flow_para = copy.deepcopy(self.ano_desc)
        self.ano_flow_para['ano_node_ipdests'] = self.ano_node.ipdests
        pickle.dump(self.ano_flow_para, open(settings.EXPORT_ABNORMAL_FLOW_PARA_FILE, 'w')) # For export abnormal flows
