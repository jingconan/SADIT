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

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

##
# @file GenDotConf.py
# @brief fs simulator config file generator
# @author Jing Conan Wang, hbhzwj@gmail.com
# @version 0.0
# @date 2011-10-24

### -- [2012-03-03 18:09:31] ANOMALY_TIME can be random
### -- [2012-03-04 13:57:49] GenAttr when generate multiple module, parameter can be same instead of random


from pydot import *
from random import sample
import re
from Markov import *
NODE_NUM = 0

import sys
sys.path.append("..")
import settings
from util import *

from Generator import *
from Modulator import *

####################################
##     Main Class Definition     ###
####################################
from random import randint
class Network(Dot):
    ''' Network Class specifiy the topology of the network.
    '''
    def __init__(self):
        Dot.__init__(self, 'SimConf', graph_type='graph')
        self.node_list = []
        global NODE_NUM
        NODE_NUM = 0
        self.IPSrcSet, self.AnoSet, _ = GetIPAdress()
        self.mv = None

    def init(self, net_desc, norm_desc):
        self.net_desc = net_desc
        self.norm_desc = norm_desc
        self._topo(self.net_desc['topo'])
        self._config_traffic()

    def choose_ip_addr(self, ip_addr_set):
        n = len(ip_addr_set)
        return ip_addr_set[randint(0, n-1)]

    def _config_traffic(self):
        """config the traffic of network"""
        nn = len(self.node_list)
        srv_node_list = [self.node_list[i] for i in xrange(nn) if i in self.net_desc['srv_list'] ]
        for i in xrange(nn):
            if i in self.net_desc['srv_list']:
                continue
            node = self.node_list[i]
            for srv_node in srv_node_list:
                start = self.norm_desc['start']
                profile = self.norm_desc['profile']
                para = Load(self.norm_desc['gen_desc'])
                #FIXME should choose ip address randomly
                para['ipsrc'] = self.choose_ip_addr(node.ipdests)
                para['ipdst'] = self.choose_ip_addr(srv_node.ipdests)
                node.add_modulator(start, profile,
                        get_generator(para))

    def _topo(self, topo):
        """initialize the topology of the network"""
        n, _ = topo.shape
        assert(n == _)
        self.NodeList = []
        print 'n, ', n
        for i in xrange(n):
            node = NNode([self.IPSrcSet[i]])
            self.node_list.append(node)
            self.add_node(node)
            if self.mv: mv.MHarpoon(node)

        for i in xrange(n):
            for j in xrange(n):
                if topo[i, j]:
                    edge = NEdge(self.node_list[i], self.node_list[j], self.net_desc['link_attr'])
                    self.add_edge(edge)

    def write(self, fName):
        '''write the DOT file to *fName*'''
        for node in self.node_list:
            node.sync()
        Dot.write(self, fName)
        FixQuoteBug(fName, float(self.net_desc['link_attr']['delay']))

    def InjectAnomaly(self, A):
        '''Inject Anomaly into the network. A is the one type Anomaly'''
        A.Run(self)


class NNode(Node):
    '''NNode is a representation of dot node. It provides several functions
    to modify the attribute of node. The original fs-simulator supports two
    types of generator. 1. **Harpoon**. 2. **rawflow**. In revised version of
    fs simulator, we add support of **JING** generator Just Incomplete and Not Good Generator.
    '''
    # node_seq = 0
    def __init__(self, ipdests):
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
        """generator is a string"""
        self.mod_num += 1
        self.generator[self.s_id] = generator

        m = Modulator(name='modulator',
                start=str(start),
                generator=self.s_id,
                profile=profile)
        self.modulator[self.m_id] = m

    def sync(self):
        """sync to the dot property"""
        attr = self.obj_dict['attributes']
        # update ipdests
        s = '"'.join([ip + ' ' for ip in self.ipdests])
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


class NEdge(Edge):
    def __init__(self, src, dst, attr):
        obj_dict = dict()
        obj_dict[ 'attributes' ] = attr
        obj_dict[ 'type' ] = 'edge'
        obj_dict[ 'parent_graph' ] = None
        obj_dict[ 'parent_edge_list' ] = None
        obj_dict[ 'sequence' ] = None
        if isinstance(src, Node):
            src = src.get_name()
        if isinstance(dst, Node):
            dst = dst.get_name()
        points = ( quote_if_necessary( src) , quote_if_necessary( dst) )
        obj_dict['points'] = points

        Edge.__init__(self, src, dst, obj_dict)
