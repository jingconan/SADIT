from __future__ import print_function, division, absolute_import
from pydot import Node
from sadit.util import types, Load
from copy import deepcopy

from .mod_util import choose_ip_addr
from .Generator import get_generator
from .Modulator import Modulator, MarkovModulator
# from .Modulator import MVModulator

# def load_base_traffic(f_name):
#     """  Load Base Traffic

#     Parameters:
#     ---------------
#     f_name : str
#         name of the base traffic
#     Returns:
#     --------------
#     """
#     with open(f_name, 'r') as fid:
#         time = []
#         traffic = []
#         for line in fid.readlines():
#             t, val = [float(l) for l in line.split()]
#             time.append(t)
#             traffic.append(val)
#         return time, traffic

# import numpy as np
# def loadtxt

from numpy import loadtxt

def check_pipe_para(para):
    """

    Parameters
    ---------------
    para : list or str
        if para is list, return itself, if para is str starts with "< " and
            follows by a file name, load the parameters in the txt

    Returns
        para : lsit
            a list of parameters
    --------------
    """
    if isinstance(para, str) and para.startswith('< '):
        f_name = para.split('< ')[0]
        return loadtxt(f_name)
    return para

class NNode(Node):
    """ Normal Node

    Parameters
    ---------------
    ipdests : list of str
        ip table for the node
    node_seq : int
        id of the node

    Attributes
    ----------------
    ipdests : list of str
        ip table for the node
    node_seq : int
        id of the node
    mod_num : int
        number of modulators
    obj_dict : dict
        used to generate str
    norm_desc : dict
        descriptor for normal traffic
    modulator : list of modulator classes
    generator : list of generator classes

    """
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

    def _get_generator_list(self, dst_node, states):
        """ create one generator for each state in **states**.
            - **ipsrc** is randomly choosen from **self.ipdests**
            - **ipdst** is randomly choosen from dst_node.ipdests
        """
        gl = []
        for state in states:
            s = Load(state)
            s['ipsrc'] = choose_ip_addr(self.ipdests).rsplit('/')[0]
            s['ipdst'] = choose_ip_addr(dst_node.ipdests).rsplit('/')[0]
            gen = get_generator(s)
            gl.append(gen)
        return gl

    def init_traffic(self, norm_desc, dst_nodes):
        if norm_desc['TYPE'] == 'stationary':
            self.init_traffic_static(norm_desc, dst_nodes)
        elif norm_desc['TYPE'] == 'dynamic':
            self.init_traffic_dynamic(norm_desc, dst_nodes)
        else:
            raise Exception("unknown tye of NORM_DESC")

    def init_traffic_static(self, norm_desc, dst_nodes):
        """  Initialize the normal traffic
        """
        self.norm_desc = norm_desc
        states = norm_desc['node_para']['states']
        for node in dst_nodes:
            self.add_modulator(norm_desc['start'],
                    norm_desc['profile'],
                    self._get_generator_list(node, states))


    def init_traffic_dynamic(self, norm_desc, dst_nodes):
        """  initialize normal traffic that is time varying

        Parameters
        ---------------------
        norm_desc : dict
            descriptor for normal traffic.
            - start : str
                start time for normal traffic
            - sim_t : float
                end time for normal traffic
            - node_para : dict
                specify the additional parameters
                + states : list
                    define the basedline distribution of flow size, flow
                    arrival
                + shifts : dict
                    defines the change of normal traffic distributions. the
                    parameters of traffic distribution is a function of time.
                    shifts stores the values of those function at discrete
                    values.
                    * time : list
                        discretized time
                    * base_type : list


        Notes
        ----------------------------
        """
        self.norm_desc = norm_desc
        states = norm_desc['node_para']['states']
        shifts = norm_desc['node_para']['shifts']
        # sim_t = norm_desc['sim_t']
        # start = Load(norm_desc['start'])
        # sv = shifts['val']

        # shifts_val = check_pipe_para(shifts['val'])
        # print('shifts_val', shifts_val)
        shifts_time = check_pipe_para(shifts['time'])
        # print('shifts_time', shifts_time)
        assert(isinstance(shifts['base_type'], list))

        def add_shifts_to_states(states, base_type, shift_val):
            """ sf:
                - base_type:
                - val:
            """
            # res = deepcopy(states)
            for i in xrange(len(states)):
                states[i][base_type] += '+ %f'%(shift_val)
            # return res

        # if len(shifts_time) != len(shifts_val):
        #     raise Exception("shifts['val'] is wrong!!")

        for node in dst_nodes:
            for i in xrange(len(shifts_time) - 1): # each discretized interval

                # create shifted_states
                shifted_states  = deepcopy(states)
                for base_type in shifts['base_type']:
                    add_shifts_to_states(shifted_states,
                            base_type,
                            shifts[base_type][i])

                pf = ((shifts_time[i+1] - shifts_time[i], ), (1,))
                gl = self._get_generator_list(node, shifted_states)
                self.add_modulator( str(shifts_time[i]), pf, gl)

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
        # self.traffic = '' # FIXME remove
        self.obj_dict['attributes']['mod_num'] = '0'

import copy
class MarkovNode(NNode):
    def __init__(self, ipdests, node_seq):
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

    def add_modulator(self, start, profile, generator_list,
            node_para=None):
        self.mod_num += 1
        s_id_list = []
        for gen in generator_list:
            self.gen_num += 1
            # print 'self.s_id, ', self.s_id
            self.generator[self.s_id] = gen
            s_id_list.append(self.s_id)


        if node_para is None:
            node_para = self.norm_desc['node_para']
        # import pdb;pdb.set_trace()
        m = self.get_modulator(start, profile, s_id_list, node_para)

        self.modulator[self.m_id] = m

    def get_modulator(self, start, profile, s_id_list,
            node_para):
        return MarkovModulator('modulator', float(start), profile,
                s_id_list, node_para)

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


# class MVNode(MarkovNode):
#     """Node for Multi Variable Node"""
#     def __init__(self, ipdests, node_seq):
#         MarkovNode.__init__(self, ipdests, node_seq)

#     @property
#     def joint_dist(self): return self.norm_desc['joint_dist']

#     @property
#     def start(self): return self.norm_desc['start']

#     @property
#     def profile(self): return self.norm_desc['profile']

#     @property
#     def para_list(self): return self.norm_desc['node_para']['states']

#     @property
#     def interval(self): return self.norm_desc['interval']

#     def init_traffic(self, norm_desc, dst_nodes):
        # print 'MVNode init_traffic'
#         self.norm_desc = norm_desc
        # FIXME why add None cause the problem?
        # self.generator_list = [ [None] + self._get_generator_list(node, self.para_list) for node in dst_nodes ]
#         self.generator_list = [ self._get_generator_list(node, self.para_list) for node in dst_nodes ]
#         self.add_modulator(self.start,
#                 self.profile,
#                 self.generator_list,
#                 self.joint_dist,
#                 )

#     def add_modulator(self, start, profile, generator_list, joint_dist=None):
#         if joint_dist is None : joint_dist = self.joint_dist
#         self.mod_num += 1
#         s_id_list = self.gen_to_id(generator_list)
#         m = self.get_modulator(start, profile, s_id_list, joint_dist) #FIX  A BUG here at [2012-04-25 12:02:11]
#         self.modulator[self.m_id] = m

#     def get_modulator(self, start, profile, s_id_list, joint_dist):
#         m = MVModulator(
#                 name='modulator',
#                 start = str(start),
#                 interval = self.interval,
#                 generator_states = s_id_list,
#                 profile = profile,
#                 joint_dist = joint_dist,
#                 )
#         return m

#     def gen_to_id(self, generator_list):
#         s_id_list = []
#         for gl in generator_list:
#             row = []
#             for g in gl:
#                 self.gen_num += 1
#                 self.generator[self.s_id] = g
#                 if not g:
#                     row.append(None)
#                 else:
#                     row.append(self.s_id)
#             s_id_list.append(row)
#         return s_id_list
