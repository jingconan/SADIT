from __future__ import print_function, division, absolute_import
from .MarkovAnomaly import MarkovAnomaly

class MVAnomaly(MarkovAnomaly):
    @property
    def joint_dist(self): return self.ano_desc['change']['joint_dist']

    def del_mod(self, node, m_id, mod):
        del node.modulator[m_id]
        for row in mod.states:
            for s_id in row:
                if s_id is not None: del node.generator[s_id]

    def add_ano_mod(self, start, ap, generator_list):
        # import pdb;pdb.set_trace()
        self.ano_node.add_modulator(
                start=str(start),
                profile=ap,
                generator_list = generator_list,
                joint_dist = self.joint_dist,
                )

    def get_generator_list(self, mod):
        return [ [ self.ano_node.generator.get(ID, None) for ID in id_row ] for id_row in mod.states ]
