#!/usr/bin/env python
# Copyright (C)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

##
# @file anomaly.py
# @brief Anomalies Related
# @author Jing Conan Wang, hbhzwj@gmail.com
# @version 0.1
# @date 2011-11-01

### -- [2012-03-04 14:56:03] FlowRate and FlowSize anomaly parameter has be changed as
### -- ratio instead of absolute value


from GenDotConf import *
import numpy as np
from matplotlib.pyplot import *
from types import ListType

import sys
sys.path.append("..")
import settings
import cPickle as pickle
# Used global parameters,
# * link_attr
# * ATYPICAL_IP_FILE
# * IPS_FILE

##-- [2012-04-08 22:31:20] Add GenAnomalyDot
##-- [2012-04-09 18:31:22] refactoring the whole file
## -- [2012-04-10 01:14:07] FLOW_RATE can work


################################
##    Class Definition  ###
# Anomaly Considered:
#     Atypical USer
#     Change of Flow Rate
#     Change of Flow Duration
#     Change of Data Rate
###############################
from numpy import cumsum, hstack, sort, argsort, diff
def get_pos(l, v):
    """index of largest element in l that is less than v"""
    for i in xrange(len(l)):
        if l[i] < v :
            continue
        return i - 1

def insert_break_pt(b, dur, num):
    """it return the new duration, new number,
    the third thing returned in the idex of added
    element"""
    t = [0] + list(cumsum( dur ))
    nt = copy.deepcopy(t)
    new_num = list(copy.deepcopy(num))
    i = get_pos(t, b)
    if i == -1 :
        return dur, num, i+1;
    if i == len(t) - 1:
        return dur, num, i+1
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
class Anomaly:
    '''basis class for anomaly. Its subclass will provide Run() method'''
    def __init__(self, anoDesc):
        self.anoDesc = anoDesc
        self.ano_node = None

    def get_profile_with_ano(self, mod_start, mod_profile, ano_t):
        """in fs, one modulator can only one behaviour
        toe simulate the change of behaviour of the modulator,
        the abnormal haviour will be generator by new modulators."""
        start, end = ano_t
        start -= mod_start
        end -= mod_start
        d, n, i1 = insert_break_pt(start, mod_profile[0], mod_profile[1])
        d, n, i2 = insert_break_pt(end, d, n)
        normal_profile_1 = ( tuple(d[:i1]), tuple(n[:i1]) )
        abnormal_profile = ( tuple(d[i1:i2]), tuple(n[i1:i2]) )
        normal_profile_2 = ( tuple(d[i2:]), tuple(n[i2:]) )
        return normal_profile_1, abnormal_profile, normal_profile_2

    def cut_profile(profile, status):
        """cut into three pieces"""

    def _infect_modulator(self, mod_start, mod_profile, ano_t, m_id, s_id):
        # TODO consider more complex cases.
        # self.get_profile_with_ano(mod_start, mod_profile, ano_t)
        start, end = ano_t

        ano_node = self.ano_node
        generator = ano_node.generator
        np1, ap, np2 = self.get_profile_with_ano(mod_start, mod_profile, ano_t)
        # print 'np1, ',np1, 'ap, ', ap, 'np2', np2
        # import pdb;pdb.set_trace()

        ano_node.add_modulator(start=str(mod_start), profile=np1, generator = generator[s_id])

        ano_type = self.anoDesc['anoType']
        st = mod_start + float(np.sum(np1[0]))
        assert(st == start)
        ano_node.add_modulator(start=str(start),
                profile=ap,
                generator = generator[s_id].get_new_gen(ano_type, self.anoDesc['ratio']))

        st = mod_start + float(np.sum(np1[0])) + float(np.sum(ap[0]))
        assert(st == end)
        ano_node.add_modulator(start=str(end), profile=np2, generator=generator[s_id])



        # simT = mod_profile[0][0]

        # ano_node.add_modulator(
        #         start='0',
        #         profile='((%d,),(1,))' %(start),
        #         generator = generator[s_id],
        #         )

        # ano_type = self.anoDesc['anoType']
        # ano_node.add_modulator(start=str(start),
        #         profile='((%d,),(1,))' %(end-start),
        #         generator = generator[s_id].get_new_gen(ano_type, self.anoDesc['ratio']))

        # ano_node.add_modulator(start=str(end),
        #         profile='((%d,),(1,))' %(simT - end),
        #         generator=generator[s_id])

        del ano_node.modulator[m_id]
        del ano_node.generator[s_id]

    def Run(self, net):
        """inject itself into the network"""
        self.ano_node = net.node_list[self.anoDesc['ano_node_seq']]
        ano_t = self.anoDesc['T']

        m_back = copy.deepcopy(self.ano_node.modulator)
        for m_id, mod in m_back.iteritems(): # For each modulator
            s_id = mod['generator'] # get id for source generator
            mod_start = eval(mod['start'])
            mod_profile = mod['profile']
            self._infect_modulator(mod_start, mod_profile, ano_t, m_id, s_id)


class AtypicalUser(Anomaly):
    '''anomaly of atypical user. an atypical user joins to the network during some time.
    Atypical user refer those user has large IP distance with users in the network.'''
    ATIP = None # Atypical IP Set. Will Select IP from this set and add a node with atypical ip
    idx = 0 # A indicator to seperate the IP that has been selected or not
    NAME = 'AtypicaUser'
    def __init__(self, anoDesc, atip=[]):
        t = anoDesc['T']
        Anomaly.__init__(self, t)
        if AtypicalUser.ATIP == None:
            AtypicalUser.ATIP = atip

    def Run(self, net):
        '''will add a node for atypical user to the network.
        The IP address for atypical user is selected from. settings.ATYPICAL_IP_FILE'''
        ipdest = AtypicalUser.ATIP[AtypicalUser.idx]
        node = NNode(ipdest, self.ipdst)
        start, end = self.t
        node.ModifyAttr(start=str(start), profile='((%d,),(1,))' %(end-start))
        AtypicalUser.idx += 1
        net.add_node(node)
        edge = NEdge(node, net.srvNode, net.link_attr)
        net.add_edge(edge)
        print node

        # Output the local IP address
        # fid = open('../atypical_IP.txt', 'w')
        fid = open(settings.ATYPICAL_IP_FILE, 'w')
        print 'ipdest: ', ipdest
        fid.write(ipdest)
        fid.close

##################################
###  Interface          #######
##################################
anoMap = {'ATYPICAL_USER':AtypicalUser,
        'FLOW_ARRIVAL_RATE':Anomaly,
        'FLOW_SIZE':Anomaly,
        }

def GenAnomalyDot(anoDesc, netDesc, normalDesc, outputFileName):
    anoType = anoDesc['anoType']
    AnoClass = anoMap[anoType]
    A = AnoClass(anoDesc)

    net = Network()
    net.init(netDesc, normalDesc)
    net.InjectAnomaly( A )
    net.write(outputFileName)

