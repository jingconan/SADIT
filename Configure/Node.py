# from pydot import *
from pydot import Node
# NODE_NUM = 0

import sys
sys.path.append("..")
# from util import *
from util import types, Load
from mod_util import choose_ip_addr
# from mod_util import *

from Generator import get_generator
from Modulator import Modulator, MarkovModulator, MVModulator

class NNode(Node):
    # node_seq = 0
    def __init__(self, ipdests, node_seq, **argv):
        assert( type(ipdests)== types.TupleType or type(ipdests)== types.ListType )
        self.node_seq = node_seq
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

    def add_interface_addr(self, addr):
        """addr should be the CIDR format. e.g. 10.0.7.0/24
        """
        self.ipdests.append(addr)

    def _get_generator_list(self, dst_node, para_list):
        """returns the default generator list"""
        res = []
        for state in para_list:
            s = Load(state)
            s['ipsrc'] = choose_ip_addr(self.ipdests).rsplit('/')[0]
            s['ipdst'] = choose_ip_addr(dst_node.ipdests).rsplit('/')[0]
            gen = get_generator(s)
            res.append(gen)
        return res

    def init_traffic(self, norm_desc, dst_nodes):
        self.norm_desc = norm_desc
        para_list = norm_desc['node_para']['states']
        for node in dst_nodes:
            self.add_modulator(norm_desc['start'],
                    norm_desc['profile'],
                    self._get_generator_list(node, para_list))


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


    def clear_modulator(self):
        self.traffic = ''
        self.obj_dict['attributes']['mod_num'] = '0'

import copy
class MarkovNode(NNode):
    def __init__(self, ipdests, node_seq, **markov_desc):
        self.markov_desc = markov_desc
        NNode.__init__(self, ipdests, node_seq)
        self.gen_num = 0

    def _gen_generator(self, ipdst):
        self.gen_desc = copy.deepcopy( self.states[self.cs] )
        self.gen_desc['ipsrc'] = choose_ip_addr(self.ipdests).rsplit('/')[0]
        self.gen_desc['ipdst'] = self.ipdst.rsplit('/')[0]
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
            # print 'self.s_id, ', self.s_id
            self.generator[self.s_id] = gen
            s_id_list.append(self.s_id)

        if not markov_desc: markov_desc = self.markov_desc
        # import pdb;pdb.set_trace()
        m = self.get_modulator(start, profile, s_id_list, markov_desc)

        self.modulator[self.m_id] = m

    def get_modulator(self, start, profile, s_id_list, markov_desc):
        # print 'markov_desc', markov_desc
        m = MarkovModulator(
                name='modulator',
                start = str(start),
                generator_states = s_id_list,
                profile=profile,
                **markov_desc
                )
        return m

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


        # print 'self.modulator father, ', self.modulator
        # print '*' * 100
        attr['traffic'] = '"' + ' '.join(key_list) + '"'
        for k, v in zip(key_list, mod_list):
            attr[k] = str(v)

        # update generator
        for k, v in self.generator.iteritems():
            if v: attr[k] = str(v)


class MVNode(MarkovNode):
    """Node for Multi Variable Node"""
    def __init__(self, ipdests, node_seq):
        MarkovNode.__init__(self, ipdests, node_seq)

    @property
    def joint_dist(self): return self.norm_desc['joint_dist']

    @property
    def start(self): return self.norm_desc['start']

    @property
    def profile(self): return self.norm_desc['profile']

    @property
    def para_list(self): return self.norm_desc['node_para']['states']

    @property
    def interval(self): return self.norm_desc['interval']

    def init_traffic(self, norm_desc, dst_nodes):
        # print 'MVNode init_traffic'
        self.norm_desc = norm_desc
        # FIXME why add None cause the problem?
        # self.generator_list = [ [None] + self._get_generator_list(node, self.para_list) for node in dst_nodes ]
        self.generator_list = [ self._get_generator_list(node, self.para_list) for node in dst_nodes ]
        self.add_modulator(self.start,
                self.profile,
                self.generator_list,
                self.joint_dist,
                )

    def add_modulator(self, start, profile, generator_list, joint_dist=None):
        if joint_dist is None : joint_dist = self.joint_dist
        self.mod_num += 1
        s_id_list = self.gen_to_id(generator_list)
        m = self.get_modulator(start, profile, s_id_list, joint_dist) #FIX  A BUG here at [2012-04-25 12:02:11]
        self.modulator[self.m_id] = m
        # print self.modulator

    def get_modulator(self, start, profile, s_id_list, joint_dist):
        m = MVModulator(
                name='modulator',
                start = str(start),
                interval = self.interval,
                generator_states = s_id_list,
                profile = profile,
                joint_dist = joint_dist,
                )
        return m

    def gen_to_id(self, generator_list):
        s_id_list = []
        for gl in generator_list:
            row = []
            for g in gl:
                self.gen_num += 1
                self.generator[self.s_id] = g
                if not g:
                    row.append(None)
                else:
                    row.append(self.s_id)
            s_id_list.append(row)
        return s_id_list
