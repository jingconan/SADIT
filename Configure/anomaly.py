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

##################################
####    Interface          #######
##################################
def GenAtypicalUserAnomalyDot(startTime, endTime, outputFileName):
    """ Generate DOT file with anomaly of atypical user.
    the topology is assumed to be start topology. You can change to other
    topology by change the net.StarTopo() function.

    - startTime: start time of the anomaly
    - endTime: endTime of the anomaly
    - outputFileName: name for the output DOT file.
    """
    IPSrcSet, AnoSet, graphSize = GetIPAdress()
    net= Network()
    net.StarTopo(graphSize, settings.link_attr, IPSrcSet)
    A = AtypicalUser( (startTime, endTime), AnoSet )
    net.InjectAnomaly( A )
    net.write(outputFileName)


def GenFlowSizeAnomalyDot(startTime, endTime, fSize_mean, fSize_var, outputFileName):
    '''Generate DOT file with anomaly of flow size. The topology is assumed to be star topology.

    - *fSize_mean* :the mean of flow size for anomaly
    - *fSize_var* :the variance of flow size for anomaly,
    - *outputFileName* : the name for output DOT File'''
    IPSrcSet, AnoSet, graphSize = GetIPAdress()
    net= Network()
    net.StarTopo(graphSize, settings.link_attr, IPSrcSet[0:-2])
    A = FlowSize((startTime, endTime),
            IPSrcSet[-1], fSize_mean, fSize_var)
    net.InjectAnomaly( A )
    net.write(outputFileName)


def GenFlowRateAnomalyDot(startTime, endTime, lamb, outputFileName):
    '''Generate DOT file with anomaly of  flow arrival rate. the topology is assume to be
    start topology

    - *startTime* :start time of anomaly
    - *endTime* :endTime of anomaly,
    - *lamb* :flow arrvial rate during anomaly.
    - *outputFileName* :name for output DOT file'''
    IPSrcSet, AnoSet, graphSize = GetIPAdress()
    net= Network()
    net.StarTopo(graphSize, settings.link_attr, IPSrcSet[0:-2])
    A = FlowRate((startTime, endTime),
            IPSrcSet[-1], lamb)
    net.InjectAnomaly( A )
    net.write(outputFileName)


##################################
####    Utility Function  #######
##################################
def GetIPAdress():
    '''
    Select normal IP address and abnormal IP address,
    the distance  between normal IP address and abnormal IP
    address is very large
    '''
    IPMat = GetIPMat() #  Get All IPs
    DF = lambda x,y:np.abs(x[0]-y[0])* (256 ** 3) + np.abs(x[1]- y[1]) * (256 ** 2) + np.abs(x[2] - y[2]) * (256) + np.abs(x[3] - y[3])
    # Calculate the center and distance to centers
    center, dis = CalIPCenter(IPMat, DF)
    sortIdx = np.argsort(dis, axis=0)
    ratio = 0.001 # Portion of selected points
    IPNum = len(dis)
    corePts = list( sortIdx[ range(int(IPNum * ratio)) ] );
    anoPts = list( sortIdx[ range(int(IPNum * (1-ratio)), IPNum, 1) ] )

    graphSize = len(corePts) + len(anoPts) # Size of the Graph

    IPSrcSet = []
    for pt in corePts:
        IPSrcSet.append("%d.%d.%d.%d" %(IPMat[pt, 0], IPMat[pt, 1], IPMat[pt, 2], IPMat[pt, 3]))
    AnoSet = []
    for pt in anoPts:
        AnoSet.append("%d.%d.%d.%d" %(IPMat[pt, 0], IPMat[pt, 1], IPMat[pt, 2], IPMat[pt, 3]))
    return IPSrcSet, AnoSet, graphSize

def CalIPCenter(IPMat, DF):
    '''*IPMat* is a Mx4 numpy matrix contains M ip addresses.
    *DF* is a user defined distance function'''
    IPNum, y = np.shape(IPMat)
    IPCenter = np.mean(IPMat, axis=0)
    dis = np.zeros( (IPNum, 1) )
    for i in range(IPNum):
        dis[i] = DF(IPMat[i,:], IPCenter)
    return IPCenter, dis


def PlotPts(IPMat, corePts, anoPts, c):
    figure()
    for pt in corePts:
        plot(IPMat[pt, 0], IPMat[pt, 1], 'bo')
    for pt in anoPts:
        plot(IPMat[pt, 0], IPMat[pt, 1], 'ro')
    plot(c[0], c[1], 'go')


def GetIPMat():
    '''load valid ip adrees from setting.IPS_FILE'''
    # IP = LoadValidIP('./ips.txt')
    IP = LoadValidIP(settings.IPS_FILE)
    IPNum = len(IP)
    IPMat = np.zeros( (IPNum, 4) )
    i = -1
    for ip in IP:
        i += 1
        val = ip.split('.')
        ipInt = [int(x) for x in val]
        IPMat[i, :] = ipInt
    return IPMat


def P2F_RAW(flowRate, flowDuration, pktRate): # Change Prameter to FS Format for rawflow
    pass
# interval =
    # flowlets # Number of Flowlets in Flow
    # bytes # Number of Flowlets in each flow
    # interval # Interval between flowlets.
    # pkts # Number of packets in each emitted flow


def F2P_RAW(flowlets, bytes, interval, pkts ):
    pktRate = bytes * pkts / interval
    flowDuration = flowlets * interval
    flowRate = 1.0 / flowDuration




################################
##    Class Definition  ###
# Anomaly Considered:
#     Atypical USer
#     Change of Flow Rate
#     Change of Flow Duration
#     Change of Data Rate
###############################

class Anomaly:
    '''basis class for anomaly. Its subclass will provide Run() method'''
    def __init__(self, t):
        self.t = t # t is a tuple, the first element is start time, the second element is end time
        self.ipdst = '165.14.130.9' # FIXME Should be a Parameter

class AtypicalUser(Anomaly):
    '''anomaly of atypical user. an atypical user joins to the network during some time.
    Atypical user refer those user has large IP distance with users in the network.'''
    ATIP = None # Atypical IP Set. Will Select IP from this set and add a node with atypical ip
    idx = 0 # A indicator to seperate the IP that has been selected or not
    NAME = 'AtypicaUser'
    def __init__(self, t, atip=[]):
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


class FlowRate(Anomaly):
    '''anomaly of flow arrival rate, during the time of anomaly, the flow arrival rate of a user will change, you need specifiy *t*, which is tuple containing the starting time
    and end time of the anomaly. *ip* is the ip adress of the user that cause the anomaly.
    *ratio* is the ratio between abnormal and normal flow arrival rate.'''
    # def __init__(self, t, ip, il):
    def __init__(self, t, ip, ratio):
        # fr is flow rate
        Anomaly.__init__(self, t)
        self.ip = ip
        # self.il = il #interval_lambda
        self.ratio = ratio

    def Run(self, net):
        para = settings.DEFAULT_PROFILE
        simT = para[1]
        node = NNode(self.ip, self.ipdst, 3)
        start, end = self.t
        node.ModifyAttr(seq=0, start='0',
                profile='((%d,),(1,))' %(start))

        normalRate = float( node.obj_dict['attributes']['gen_para'].rsplit(', ')[2] )
        pickle.dump(self.ratio * normalRate, open(settings.ANO_CONF_PARA_FILE, 'w'))

        node.ModifyAttr(seq=1, start=str(start),
                profile='((%d,),(1,))' %(end-start),
                flowstart='exponential(%f)' %(self.ratio * normalRate))
                # flowstart='exponential(%f)' %(self.il))
        # print 'self.il: ', self.il, 'start: ', start, 'end: ', end

        node.ModifyAttr(seq=2, start=str(end),
                profile='((%d,),(1,))' %(simT - end))

        net.add_node(node)
        edge = NEdge(node, net.srvNode, net.link_attr)
        net.add_edge(edge)

class FlowSize(Anomaly):
    '''anomaly of flow size. during the time of anomaly, the flow size of a user will change.'''
    def __init__(self, t, ip, fSize_mean_ratio, fSize_var):
    # def __init__(self, t, ip, fSize_mean, fSize_var):
        # fr is flow rate
        Anomaly.__init__(self, t)
        self.ip = ip
        # self.fSize_mean = fSize_mean #interval_lambda
        self.fSize_mean_ratio = fSize_mean_ratio #interval_lambda
        self.fSize_var = fSize_var

    def Run(self, net):
        para = settings.DEFAULT_PROFILE
        simT = para[1]
        node = NNode(self.ip, self.ipdst, 3)
        start, end = self.t

        normalFSMean = float( node.obj_dict['attributes']['gen_para'].rsplit(', ')[0] )
        pickle.dump(normalFSMean * self.fSize_mean_ratio, open(settings.ANO_CONF_PARA_FILE, 'w'))

        node.ModifyAttr(seq=0, start='0',
                profile='((%d,),(1,))' %(start))

        node.ModifyAttr(seq=1, start=str(start),
                profile='((%d,),(1,))' %(end-start),
                flowsize='normal(%f,%f)' %(normalFSMean * self.fSize_mean_ratio, self.fSize_var))
                # flowsize='normal(%f,%f)' %(self.fSize_mean, self.fSize_var))

        node.ModifyAttr(seq=2, start=str(end),
                profile='((%d,),(1,))' %(simT - end))

        net.add_node(node)
        edge = NEdge(node, net.srvNode, net.link_attr)
        net.add_edge(edge)

if __name__ == "__main__":
    GenAtypicalUserAnomalyDot(2000, 3000, './out2.dot')
    # GenFlowSizeAnomalyDot(2000, 3000, 40000, 400, './out3.dot')
    # GenFlowRateAnomalyDot(2000, 3000, 1, './out4.dot')



