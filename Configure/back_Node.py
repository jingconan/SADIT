from pydot import *
from random import sample
import re
NODE_NUM = 0

import sys
sys.path.append("..")
import settings
from util import *
from mod_util import *

from Generator import *
from Modulator import *

class NNode(Node):
    # node_seq = 0
    def __init__(self, ipdests, **argv):
        assert( type(ipdests)== types.TupleType or type(ipdests)== types.ListType )
        global NODE_NUM
        self.node_seq = NODE_NUM
        NODE_NUM += 1
        # default attribute
        attr = dict(
                autoack = '"False"',
                ipdests = '"' + ' '.join(ipdests) + '"',
                mod_num = '0',
                traffic = ''
                )
        obj_dict = {'attributes': attr,
                'name': 'n'+str( self.node_seq ),
                'parent_node_list': None,
                'port': None,
                'sequence': 1,
                'type': 'node'}

        Node.__init__(self, name = 'n'+str(self.node_seq), obj_dict = obj_dict)

        self.ipdests = ipdests
        self.mod_num = 0
        self.modulator = dict()
        self.generator = dict()

    def __str__(self):
        return str(self.obj_dict)

    @property
    def m_id(self):
        """modulator identifier"""
        return 'm' + str(self.node_seq) + '_' + str(self.mod_num)

    @property
    def s_id(self):
        """generator source identifier"""
        return 's' + str(self.node_seq) + '_' + str(self.mod_num)

    def add_modulator(self, start, profile, generator):
        """generator is a Generator Object"""
        assert(len(generator) == 1)
        self.mod_num += 1
        self.generator[self.s_id] = generator[0]

        m = Modulator(name='modulator',
                start=str(start),
                generator=self.s_id,
                profile=profile)
        self.modulator[self.m_id] = m

    def sync(self):
        """sync to the dot property"""
        attr = self.obj_dict['attributes']
        # update ipdests
        attr['ipdests'] = '"' + ' '.join(self.ipdests) + '"'
        # update traffic
        attr['traffic'] = '"' + ' '.join(self.modulator.keys()) + '"'
        # update modultaor
        for k, v in self.modulator.iteritems():
            attr[k] = str(v)
        # update generator
        for k, v in self.generator.iteritems():
            attr[k] = str(v)


    def clear_modulator():
        self.traffic = ''
        self.obj_dict['attributes']['mod_num'] = '0'

import copy
class MarkovNode(NNode):
    def __init__(self, ipdests, **markov_desc):
        self.markov_desc = markov_desc
        NNode.__init__(self, ipdests)
        self.gen_num = 0

    def _gen_generator(self, ipdst):
        self.gen_desc = copy.deepcopy( self.states[self.cs] )
        self.gen_desc['ipsrc'] = choose_ip_addr(self.ipdests)
        self.gen_desc['ipdst'] = self.ipdst
        return get_generator(self.gen_desc)

    @property
    def s_id(self):
        """generator source identifier"""
        return 's' + str(self.node_seq) + '_' + str(self.mod_num) + '_' + str(self.gen_num)

    def add_modulator(self, start, profile, generator_list, markov_desc=None):
        self.mod_num += 1
        s_id_list = []
        for gen in generator_list:
            self.gen_num += 1
            self.generator[self.s_id] = gen
            s_id_list.append(self.s_id)

        if not markov_desc: markov_desc = self.markov_desc
        m = MarkovModulator(
                name='modulator',
                start = str(start),
                generator_states = s_id_list,
                profile=profile,
                **markov_desc
                )

        self.modulator[self.m_id] = m

    def sync(self):
        """sync to the dot property"""
        attr = self.obj_dict['attributes']
        # update ipdests
        attr['ipdests'] = '"' + ' '.join(self.ipdests) + '"'
        # update traffic
        # update modultaor
        key_list = []
        mod_list = []
        for k, v in self.modulator.iteritems():
            j = 0
            for mod in v.mod_list:
                j += 1
                key_list.append(k+'_'+str(j))
                mod_list.append(mod)

        # print '*' * 100
        attr['traffic'] = '"' + ' '.join(key_list) + '"'
        for k, v in zip(key_list, mod_list):
            attr[k] = str(v)

        # update generator
        for k, v in self.generator.iteritems():
            attr[k] = str(v)




