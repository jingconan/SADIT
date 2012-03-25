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
nodeSeq = 0

import sys
sys.path.append("..")
import settings
from util import *

def LoadValidIP(fileName):
    fid = open(fileName, 'r')
    content = fid.readline()
    # print content
    return content.split(',')


def FixQuoteBug(fileName, delay=0.001):
    # There is a bug in pydot. when link attribute is < 1, pydot will automatically add quote to value
    # which is not desirable. This function try to fix that problem
    fid = open(fileName, 'r')
    content = fid.read()
    content = re.sub('delay="[\d.]*"', 'delay='+str(delay), content)
    fid.close()
    fid = open(fileName, 'w')
    fid.write(content)
    fid.close()


def ParseArg(string):
    # print '---before--'
    # print string
    string = string.replace('"','')
    # print string
    # print '---after--'
    val = string.rsplit(' ')
    attr = dict()
    for v in val:
        sr = v.rsplit('=')
        if len(sr) == 1:
            attr['name'] = sr[0]
        else:
            x, y = sr
            attr[x] = y
    return attr

# Both Modulator and Source are described by Attr
class Attr():
    '''Sub Class of String'''
    def __init__(self, string=None, **args):
        if not string:
            self.attr = args
        else:
            self.attr = ParseArg(string)

    def __str__(self):
        string = '"' + self.attr['name']
        for k, v in self.attr.iteritems():
            if k == 'name':
                continue
            string = string + ' ' + k + '=' + v
        string = string + '"'
        return string

def GenAttr(k, ipdests, ipdst, N, stype):
    '''Generate the default Attribute.
    k is NodeSeq, ipdests is the local ip addr. ipdst is the destination, N is
    the num of modulator and source. We assume for each modulator, there is one associated source'''
    attr = dict()
    attr['autoack'] = '"False"'
    attr['ipdests'] = '"' + ipdests + '"'
    mStr = '"'

    stype = settings.GENERATOR
    exec('gen_para = Load(settings.%s)'%(stype))
    for i in range(N):
        mName = 'm' + str(k) + '_' + str(i)
        sName = 's' + str(k) + '_' + str(i)
        mStr = mStr + mName + ' '

        para = settings.DEFAULT_PROFILE
        m = Attr(name='modulator',
                start=str(para[0]),
                generator=sName,
                profile='((%d,),(%d,))' %(para[1], para[2]))

        # stype = settings.GENERATOR
        if stype == 'HARPOON':
            # para = settings.HARPOON
            para = gen_para
            para = Load(settings.HARPOON)
            fm = dict(fSize_mean=0, fSize_var=1, fStart_lambda=2)
            s = Attr(name='harpoon',
                    ipsrc=ipdests,
                    ipdst=ipdst,
                    flowsize='normal(%f,%f)' %(para[fm['fSize_mean']], para[fm['fSize_var']]),
                    flowstart='exponential(%f)' %(para[fm['fStart_lambda']]),
                    sport='randomchoice(22,80,443)',
                    dport='randomunifint(1025,65535)',
                    lossrate='randomchoice(0.001)')
        elif stype == 'rawflow':
            s = Attr(name='rawflow',
                    ipsrc=ipdests,
                    ipdst=ipdst,
                    flowlets='1',
                    ipproto='udp',
                    pkts='5',
                    bytes='1000',
                    interval='0.2',
                    sport='randomchoice(22,80,443)',
                    dport='randomunifint(1025,65535)',
                    continuous='1')
        elif stype == 'JING':
            para = settings.JING
            # fm = dict(pkts=1, dRate_mean=2, dRate_variance=3, interval_lambda=4, duration_lambda=5)
            fm = dict(pkts=0, dRate_mean=1, dRate_variance=2, interval_lambda=3, duration_lambda=4)
            s = Attr(name='JING',
                    ipsrc=ipdests,
                    ipdst=ipdst,
                    pkts=para[fm['pkts']], #FIXME
                    dRate='normal(%f,%f)' %(para[fm['dRate_mean']], para[fm['dRate_variance']]),
                    interval='exponential(%f)' %(para[fm['interval_lambda']]),
                    duration='exponential(%f)' %(para[fm['duration_lambda']]),
                    sport='randomchoice(22,80,443)',
                    dport='randomunifint(1025,65535)')

        else:
            raise ValueError('unknown mtype')


        attr[mName] = str(m)
        attr[sName] = str(s)

    if mStr == '"':
        mStr = '""'
    else:
        mStr = mStr[0:-1] + '"'
    attr['traffic'] = mStr
    ##### Auxillary Attribute, will not be used by fs simulator #####
    attr['modulator'] = mStr[1:-1] # Modulator Name
    attr['node_seq'] = str(k) # Sequence num of node
    attr['N'] = str(N) # Modulator Number
    attr['gen_para'] = str(gen_para)[1:-1] # parameter for generater, likef default arrival rate, etc.
    return attr

####################################
##     Main Class Definition     ###
####################################

class Network(Dot):
    def __init__(self):
        Dot.__init__(self, 'SimConf', graph_type='graph')
        self.nodeList = []
        global nodeSeq
        nodeSeq = 0

    def StarTopoMarkov(self, graphSize, link_attr, IPSrcSet):
        para = settings.MARKOV_PARA
        P = settings.MARKOV_P
        interval = settings.MARKOV_INTERVAL
        simT = settings.DEFAULT_PROFILE[1]
        # print 'para, ', para, 'P: ', P, 'simT:', simT

        mv = Markov(para, P, interval, (0, simT))

        self.link_attr = link_attr
        srvAddr = '165.14.130.9'
        srvNode = ServerNNode(srvAddr)
        self.srvNode = srvNode
        self.add_node(srvNode)

        for ipsrc in IPSrcSet:
            node = NNode(ipsrc, srvAddr, 0)
            self.nodeList.append(node)
            self.add_node(node)
            mv.MHarpoon(node) # Modulator the Behavior of the Node
            edge = NEdge(node, srvNode, link_attr)
            self.add_edge(edge)

    def StarTopo(self, graphSize, link_attr, IPSrcSet):
        print 'Creating the Star topology ....'
        self.link_attr = link_attr
        srvAddr = '165.14.130.9'
        srvNode = ServerNNode(srvAddr)
        self.srvNode = srvNode
        self.add_node(srvNode)

        # Add Node and Link
        # validIP = LoadValidIP('./ips.txt')
        # IPSrcSet = sample(validIP, graphSize-1)
        for ipsrc in IPSrcSet:
            print 'ipsrc, ', ipsrc
            node = NNode(ipsrc, srvAddr)
            self.nodeList.append(node)
            self.add_node(node)
            edge = NEdge(node, srvNode, link_attr)
            self.add_edge(edge)

    def write(self, fName):
        Dot.write(self, fName)
        FixQuoteBug(fName, float(self.link_attr['delay']))

    def InjectAnomaly(self, A):
        A.Run(self)

class NNode(Node):
    def __init__(self, ipdest, ipdst, N=1, stype='JING'):
        global nodeSeq
        nodeSeq += 1
        attr =  GenAttr(nodeSeq, ipdest, ipdst, N, stype)
        obj_dict = {'attributes': attr,
                'name': 'n'+str(nodeSeq),
                'parent_node_list': None,
                'port': None,
                'sequence': 1,
                'type': 'node'}
        Node.__init__(self, name = 'n'+str(nodeSeq), obj_dict = obj_dict)
        self.ipdest = ipdest
        self.ipdst = ipdst

    def __str__(self):
        return str(self.obj_dict)

    def ModifyAttr(self, **args):
        # Search Layer by Layer
        attr = self.obj_dict['attributes']
        # print args
        for k, v in args.iteritems():
            if k  == 'seq':
                continue
            if k in attr.iterkeys(): #TODO
                attr[k] = v
            else:
                mName = attr['modulator']
                # print attr[mName]
                mSplit = mName.rsplit(' ')
                if len(mSplit) != 1:
                    # print "[Warning] Don't suppose node with multi modulator and source "
                    # print mSplit
                    if not args.has_key('seq'):
                        raise TypeError('You need specify the modulator sequence number when there are multi modulator')
                    else:
                        mn = mSplit[args['seq']]
                else:
                    mn = mName

                m = Attr(attr[mn])
                # print 'm: ', m
                if k in m.attr.iterkeys():
                    # print 'type(v)', type(v)
                    # print 'v: ', v
                    m.attr[k] = v
                    attr[mn] = str(m)
                else:
                    sName = m.attr['generator']
                    s = Attr(attr[sName])
                    if k in s.attr.iterkeys():
                        s.attr[k] = v
                        attr[sName] = str(s)
                    else:
                        raise ValueError('not proper argument key value')

    def AddModulator(self, start, profile, generator):
        attr = self.obj_dict['attributes']
        N = int(attr['N']) # Num of Modultor
        N += 1
        attr['N'] = str(N)
        nodeSeq = int(attr['node_seq'])
        mName = 'm' + str(nodeSeq) + '_' + str(N)
        mStr = attr['modulator']
        if mStr == '':
            mStr = mName
        else:
            mStr = mStr + ' ' + mName
        attr['traffic'] = '"' + mStr + '"'
        attr['modulator'] = mStr
        sName = 's' + str(nodeSeq) + '_' + str(N)
        attr[sName] = generator

        m = Attr(name='modulator',
                start=str(start),
                generator=sName,
                profile=profile)
        attr[mName] = str(m)

    def GetJING(self, **para):
        s = Attr(name='JING',
                ipsrc=para['ipsrc'],
                ipdst=para['ipdst'],
                pkts=para['pkts'],
                dRate='normal(%s,%s)' %(para['dRate_mean'], para['dRate_variance']),
                interval='exponential(%s)' %(para['interval_lambda']),
                duration='exponential(%s)' %(para['duration_lambda']),
                sport='randomchoice(22,80,443)',
                dport='randomunifint(1025,65535)')
        return str(s)

    def GetRawFlow(self, ipsrc, ipdst, flowlets, ipproto, dport, sport, pkts, bytes, interval, continuous):
        return str( Attr(name='rawflow',
                ipsrc=ipsrc,
                ipdst=ipdst,
                flowlets=flowlets,
                ipproto=ipproto,
                pkts=pkts,
                bytes=bytes,
                interval=interval,
                sport=sport,
                dport=dport,
                continuous=continuous) )

    def GetHarpoon(self, ipsrc, ipdst, flowsize, flowstart, sport, dport, lossrate):
        return str( Attr(name='harpoon', ipsrc=ipsrc, ipdst=ipdst, flowsize=flowsize, flowstart=flowstart, sport=sport, dport=dport, lossrate=lossrate) )

    def AddHarpoon(self, start, end, para): # For Markovian Modulator
        # print 'para, ', para
        flowsize, flowstart = para
        profile = '((%f,),(%d,))' %(end-start, 1)
        sport='randomchoice(22,80,443)'
        dport='randomunifint(1025,65535)'
        lossrate='randomchoice(0.001)'
        g = self.GetHarpoon(self.ipdest, self.ipdst, flowsize, flowstart, sport, dport, lossrate)
        self.AddModulator(start, profile, g)

class ServerNNode(Node):
    def __init__(self, addr):
        destIP = addr
        attr = {'autoack':'"False"', 'ipdests':'"'+ destIP +'"'}
        obj_dict = {'attributes': attr,
                'name': 'n'+str(nodeSeq),
                'parent_node_list': None,
                'port': None,
                'sequence': 1,
                'type': 'node'}
        Node.__init__(self, name = 'n'+str(nodeSeq), obj_dict = obj_dict)

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


def main():
    # Size of the Graph
    # graphSize = 5
    # link Attribute
    # link_attr = {'weight':'10', 'capacity':'10000000', 'delay':'0.001'}
    # net = Network(graphSize, link_attr)
    # net = Network(graphSize, link_attr)
    # net.write('./output2.dot')
    # string = 'harpoon ipdst=165.14.130.9 ipsrc=127.118.14.249 flowsize=normal(40000000,4000000) lossrate=randomchoice(0.001) flowstart=exponential(10.0) dport=randomunifint(1025,65535) sport=randomchoice(22,80,443)'
    # x = ParseArg(string)
    # print x
    node = NNode('165.14.130.9', '1.1.1.1')
    node.ModifyAttr(flowsize='asdfwofwlefw')
    print node



if __name__ == "__main__":
    main()


