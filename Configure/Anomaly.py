#!/usr/bin/env python

### -- [2012-03-04 14:56:03] FlowRate and FlowSize anomaly parameter has be changed as
### -- ratio instead of absolute value
##-- [2012-04-08 22:31:20] Add GenAnomalyDot
##-- [2012-04-09 18:31:22] refactoring the whole file
## -- [2012-04-10 01:14:07] FLOW_RATE can work
##-- [2012-04-10 17:16:27] add _infect_modulator, make anomaly more general


# import numpy as np
from __future__ import print_function, division, absolute_import
import settings
from util import Load
from .mod_util import choose_ip_addr
import cPickle as pickle

# from numpy import cumsum, diff
def cumsum(it):
    total = 0
    for x in it:
        total += x
        yield total

def diff(x):
    res = []
    for i in xrange(len(x)-1):
        res.append(x[i+1]-x[i])
    return res


def get_pos(l, v):
    """index of largest element in l that is less than v"""
    for i in xrange(len(l)):
        if l[i] < v :
            continue
        return i - 1

def interval_intersect(i1, i2):
    """  Check whether two intervals **[i1[0], i1[1])** and **[i2[0], i2[1])** have
    intersection or not.

    >>> interval_intersect([1, 3], [3, 4])
    False
    >>> interval_intersect([1, 3], [2.9, 4])
    True
    >>> interval_intersect([1, 3], [0, 0.5])
    False
    >>> interval_intersect([1, 3], [1.5, 2.5])
    True
    >>> interval_intersect([1, 3], [1.5, 4.5])
    True
    >>> interval_intersect((500, 600), (0, 800))
    True
    """
    if i1[0] <= i2[0]:
        if i1[1] > i2[0]:
            return True
        else:
            return False
    elif i1[0] >= i2[1]:
        return False
    else:
        return True

def insert_break_pt(b, dur, num):
    """ *b* is a break point that will break *dur*,
    for example,

    >>> b = 35
    >>> dur = (20, 20, 10)
    >>> num = (1, 2, 1)
    >>> new_dur, new_num, bk_pt = insert_break_pt(b, dur, num)
    >>> print new_dur
    [20, 15, 5, 10]
    >>> print new_num
    [1, 2, 2, 1]
    >>> print bk_pt
    2
    """
    t = [0] + list(cumsum( dur ))
    nt = copy.deepcopy(t)
    new_num = list(copy.deepcopy(num))
    # print 't, ', t
    # print 'b, ', b
    i = get_pos(t, b)

    if i is None:
        raise Exception('[insert_break_pt], maybe you have insert an anomaly in an unsuitable time? ')
    elif i == -1 or i == len(t) - 1:
        return dur, num, i+1;
    else:
        nt.insert(i+1, b)
        new_num.insert(i+1, num[i])
        new_dur = list(diff(nt))
        return new_dur, new_num, i+1

class BadConfigError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

import copy
class Anomaly(object):
    """ basis class for anomaly. Its subclass will provide run() method

    Parameters
    ----------------
    ano_desc: dict
        - **ano_node_seq** : int
            id of the target node
        - **T** : list of floats
            start, end time for the anomaly
        - **change** : dict
            a dictionary specify how the attributes of the existing modules are
            changed. the value is a string, if the first char is '=', it means
            change the attribute to the value behind '='. If the first char is
            '+', it means add the attribute by the value behind '+'. Likewise
            if the first char is 'x', it means multiply the attribute by the
            value behind 'x'.
            for example:

                change = {
                'flow_size_mean':'x2',
                'flow_arrival_rate':'=6',
                'flow_size_var=+3'
                }
            It means change the flow_size_mean to two times of the orginal value, change flow_arrival_rate
            to be 6 and add the flow_size_var by 3.

    Attributes
    -----------------
    ano_desc : desc
        descriptor for anomaly
    ano_node : class of Node
        anomaly node

    """
    def __init__(self, ano_desc):
        self.ano_desc = ano_desc
        self.ano_node = None

    def get_profile_with_ano(self, mod_start, mod_profile, ano_t):
        """ According to anomaly time, break the traffic profile into two profiles
        with normal traffic and one profile with abnormal traffic.

        Parameters
        ----------------
        mod_start : float
            the start time of the traffic
        mod_profile : tuple of tuples
            The first tuple indicates a series of 1 or more time durations (in
            seconds), and the second tuple indicates the number of instances
            of a particular traffic source that should be active.
        ano_t : tuple with two elements
            start and end time of anomaly.

        Notes
        -----------------
        In `fs
        <http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf>`_,
        one modulator can only have one behaviour. In order to simulate the
        change of behaviour of the modulator, the abnormal haviour will be
        generator by new modulators.
        """
        start, end = ano_t
        # start -= mod_start
        # end -= mod_start
        mod_end = sum(mod_profile[0])
        if start <= mod_start: #
            d, n = mod_profile
            i1 = 0
            # new_mod_start = mod_start
        else:
            d, n, i1 = insert_break_pt(start - mod_start, mod_profile[0], mod_profile[1])
            # assert(mod_start + sum(d[0]) == start)
            # new_mod_start = start

        if end >= mod_end:
            i2 = len(d)
        else:
            d, n, i2 = insert_break_pt(end - mod_start, d, n)
            # st = mod_start + sum(d)
        # assert(st == end)

        normal_profile_1 = ( tuple(d[:i1]), tuple(n[:i1]) )
        abnormal_profile = ( tuple(d[i1:i2]), tuple(n[i1:i2]) )
        normal_profile_2 = ( tuple(d[i2:]), tuple(n[i2:]) )
        # import ipdb;ipdb.set_trace()
        return normal_profile_1, abnormal_profile, normal_profile_2

    def infect_modulator(self, ano_t, m_id, mod):
        """ Change behaviour modulator during the time that anomaly happens.

        Parameters
        ----------------------
        ano_t : tuple of floats
            duration of the anomaly
        m_id : str
            the id of modulator that will be infected.
        mod : dict
            attribute of the modulator

        Returns
        -----------------------
        None

        """
        ano_node = self.ano_node
        # generator = ano_node.generator
        start, end = ano_t
        # mod_start = eval(mod['start'])
        mod_start = mod['start']
        mod_profile = mod['profile']
        # s_id = mod['generator'] # get id for source generator

        # check whether this modular should be infect or not
        # only infect this modular with it has intersection with *ano_t*
        mod_end = mod_start + sum(mod_profile[0])
        if not interval_intersect(ano_t, [mod_start, mod_end]):
            return

        np1, ap, np2 = self.get_profile_with_ano(mod_start, mod_profile, ano_t)
        generator_list = self.get_generator_list(mod)

        if len(np1[0]) > 0:
            ano_node.add_modulator(str(mod_start), np1, generator_list)
            st = mod_start + float(sum(np1[0]))
            assert(st == start)

        if len(ap[0]) > 0:
            # self.new_generator = generator[s_id].get_new_gen(self.ano_desc['change'])
            self.add_ano_seg(start, ap, generator_list)

            # export para to help to export ano flo

        if len(np2[0]) > 0:
            ano_node.add_modulator(end, np2, generator_list)

        # delete original modulator
        # del ano_node.modulator[m_id]
        # del ano_node.generator[s_id]
        self.del_orig_mod_gen(m_id, mod)

    def add_ano_seg(self, start, ap, generator_list):
        """  add anomaly segment

        Parameters
        ---------------
        start : float
            start time of the anomaly
        ap : tuple of tuple
            abnormal profile
        generator_list : list of generators
            a list of normal generator duing the anomaly

        Returns
        --------------
        None

        """
        new_generator_list = [g.get_new_gen(self.ano_desc['change']) for g in generator_list ]
        self.ano_node.add_modulator(start=str(start),
                profile=ap,
                generator = new_generator_list)

        self.export_ano_flow_para(new_generator_list)

    def del_orig_mod_gen(self, m_id, mod):
        """  Delete the original modulator and generator

        Parameters
        -------------
        m_id : str
            the id of modulator

        mod : class
            modulator

        """
        del self.ano_node.modulator[m_id]
        s_id = mod['generator'] # get id for source generator
        del self.ano_node.generator[s_id]

    def get_generator_list(self, mod):
        s_id = mod['generator']
        return [ self.ano_node.generator[s_id] ]

    def export_ano_flow_para(self, new_generator_list):
        """export para to help to export ano flows

        Parameters
        -----------------
        new_generator_list : a list of generators
            the abnormal generated inserted duing the anomaly

        Returns
        ------------------
        None

        Notes
        -------------------
        Will dump the parameter data to the **settings.EXPORT_ABNORMAL_FLOW_PARA_FILE**

        """
        assert(len(new_generator_list) == 1)
        new_generator = new_generator_list[0]
        ano_flow_para = copy.deepcopy(new_generator.para)
        ano_flow_para['ano_type'] = self.ano_desc['anoType']
        pickle.dump(ano_flow_para, open(settings.EXPORT_ABNORMAL_FLOW_PARA_FILE, 'w')) # For export abnormal flows

    def run(self, net):
        """inject itself into the network

        Parameters
        ----------------
        net : network class
            class of `Network`.

        """
        self.ano_node = net.node_list[self.ano_desc['ano_node_seq']]
        ano_t = self.ano_desc['T']

        m_back = copy.deepcopy(self.ano_node.modulator)

        # import ipdb;ipdb.set_trace()
        for m_id, mod in m_back.iteritems(): # infect each modulator, change attribute by ratio
            self.infect_modulator(ano_t, m_id, mod)

class AddModulatorAnomaly(Anomaly):
    """ Anomaly that add new modulators

    Instead of infecting existing modulators, simply add new modulators.

    Parameters
    --------------------
    ano_desc: dict
        In addition to the elementself in Anomaly, it also has:

        - **dst_nodes** : list of ints
            the id of destination node of the modulators, will add one
            modulator for each dst_nodes
        - **gen_desc** : dict
            the descriptor for the generator of the modulator

    """
    def run(self, net):
        self.ano_node = net.node_list[self.ano_desc['ano_node_seq']]
        self.net = net
        self._config_traffic()

    def _config_traffic(self):
        """add modulator to each srv"""
        nn = len(self.net.node_list)
        srv_node_list = [self.net.node_list[i] for i in xrange(nn) if i in self.ano_desc['dst_nodes'] ]
        start, end = self.ano_desc['T']
        for srv_node in srv_node_list:
            gen_desc = Load(self.ano_desc['gen_desc'])
            gen_desc['ipsrc'] = choose_ip_addr(self.ano_node.ipdests).rsplit('/')[0]
            gen_desc['ipdst'] = choose_ip_addr(srv_node.ipdests).rsplit('/')[0]
            self.ano_node.add_modulator(start=str(start),
                    profile='((%d,),(1,))' %(end-start),
                    generator=[get_generator(gen_desc)] )


from .Edge import NEdge
from .Node import NNode
from .Generator import get_generator
class AtypicalUserAnomaly(Anomaly):
    """ Anomaly of atypical user. an atypical user joins to the network during
    some time.

    Atypical user refer those user has large IP distance with users in the
    network. New link will be created for this new Node.

    Parameters
    ----------------
    ano_desc : dict
        In addition to the elementself in Anomaly, it also has:

        - **ATIP** : a list of string
            set of atypical IPs
        - **link_to** : list of ints with range {1, -1}
                represents the connection to all other nodes
                + *link_to[i] == 1* means there is link from atypical node to node i.
                + *link_to[i] == -1* means there is link from node i to this atypical node.

    """
    ATIP = None # Atypical IP Set. Will Select IP from this set and add a node with atypical ip
    idx = 0 # A indicator to seperate the IP that has been selected or not
    NAME = 'AtypicaUser'
    def __init__(self, ano_desc):
        self.ano_desc = ano_desc
        Anomaly.__init__(self, ano_desc)
        if self.ATIP == None:
            self.ATIP = ano_desc['ATIP']
        self.net = None
        self.ano_node = None

    def _change_topology(self):
        link_to = self.ano_desc['link_to']
        link_attr = self.ano_desc['link_attr']
        for i in xrange(len(link_to)):
            if link_to[i] == 1:
                edge = NEdge(self.ano_node, self.net.node_list[i], link_attr )
            elif link_to[i] == -1:
                edge = NEdge(self.net.node_list[i], self.ano._ode, link_attr )
            else:
                raise ValueError('unknown link_to value')
            self.net.add_edge(edge)

    def _config_traffic(self):
        nn = len(self.net.node_list)
        srv_node_list = [self.net.node_list[i] for i in xrange(nn) if i in self.net.net_desc['srv_list'] ]
        start, end = self.ano_desc['T']
        for srv_node in srv_node_list:
            gen_desc = Load(self.ano_desc['gen_desc'])
            gen_desc['ipsrc'] = choose_ip_addr(self.ano_node.ipdests).rsplit('/')[0]
            gen_desc['ipdst'] = choose_ip_addr(srv_node.ipdests).rsplit('/')[0]
            self.ano_node.add_modulator(start=str(start),
                    profile='((%d,),(1,))' %(end-start),
                    generator=get_generator(gen_desc) )

    def _get_ano_node(self):
        ipdest = [ self.ATIP[self.idx] ]
        self.idx += 1

        nn = len(self.net.node_list) # Add by J.W
        self.ano_node = NNode(ipdest, nn)
        self._config_traffic()

    def _export_ip_addr(self):
        fid = open(settings.EXPORT_ABNORMAL_FLOW_PARA_FILE, 'w')
        fid.write( ' '.join([str(i) for i in self.ano_node.ipdests]) )
        fid.close()

    def export_ano_flow_para(self):
        """export para to help to export ano flows"""
        self._export_ip_addr()

    def run(self, net):
        '''will add a node for atypical user to the network.
        The IP address for atypical user is selected from. settings.atypical_ip_file'''
        self.net = net
        self._get_ano_node()
        net.add_node(self.ano_node)
        self._change_topology()

        self._export_ano_flow_para()

class TargetOneServer(Anomaly):
    """ Only change the behaviour in one server ano_desc should have id
    **srv_id** of that sever node

    """
    def run(self, net):
        self.ano_node = net.node_list[self.ano_desc['ano_node_seq']]
        ano_t = self.ano_desc['T']
        srv_id = self.ano_desc['srv_id']
        srv_ip_addr = net.node_list[srv_id].ipdests
        m_back = copy.deepcopy(self.ano_node.modulator)
        for m_id, mod in m_back.iteritems(): # For each modulator
            s_id = mod['generator'] # get id for source generator
            if self.ano_node.generator[s_id]['ipdst'] not in srv_ip_addr:
                continue
            self.infect_modulator(ano_t, m_id, mod)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
