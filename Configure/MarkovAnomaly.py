#!/usr/bin/env python
from anomaly import *
import sys
sys.path.append("..")
import settings

class MarkovAnomaly(Anomaly):
    def _infect_modulator(self, ano_t, m_id, mod):
        ano_node = self.ano_node
        generator = ano_node.generator

        mod_start = eval(mod['start'])
        mod_profile = mod['profile']
        np1, ap, np2 = self.get_profile_with_ano(mod_start, mod_profile, ano_t)

        # s_id = mod['generator'] # get id for source generator
        generator_list = [ generator[s] for s in mod.states ]
        # import pdb;pdb.set_trace()
        # print 'generator_list', generator_list
        # import pdb;pdb.set_trace()
        ano_node.add_modulator(
                start=str(mod_start),
                profile=np1,
                generator_list = generator_list,
                )

        start, end = ano_t
        st = mod_start + float(np.sum(np1[0]))
        assert(st == start)
        ano_node.add_modulator(
                start=str(start),
                profile=ap,
                generator_list = generator_list,
                markov_desc = self.anoDesc['ano_markov_desc'],
                )
        # import pdb;pdb.set_trace()

        st = mod_start + float(np.sum(np1[0])) + float(np.sum(ap[0]))
        assert(st == end)
        ano_node.add_modulator(
                start=str(end),
                profile=np2,
                generator_list = generator_list,
                )

        # delete original modulator
        del ano_node.modulator[m_id]
        for s_id in mod.states:
            del ano_node.generator[s_id]

