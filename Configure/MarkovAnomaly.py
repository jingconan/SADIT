#!/usr/bin/env python
from anomaly import *
import sys
sys.path.append("..")
import settings

##################################
####    Interface          #######
##################################
# Generate Markov Transition Probability
def GenMarkovTranAnomalyDot(startTime, endTime, p12, p21, outputFileName):
    '''
    startTime:
    endTime: end time for anomaly
    ip: the ip address for abnormal node
    p12: is the transition probabitliy from state 1 to state 2
    p21: is the transition probability froms state 2 to state 1
    outputFileName: will write down the dot file to outputFileName
    '''
    IPSrcSet, AnoSet, graphSize = GetIPAdress()
    net= Network()
    net.StarTopoMarkov(graphSize, settings.link_attr, IPSrcSet[0:-2])
    TranP = [(1-p12, p12), (p21, 1-p21)]
    # import pdb; pdb.set_trace()
    A = MarkovAnoP((startTime, endTime), IPSrcSet[-1], TranP)
    net.InjectAnomaly( A )
    net.write(outputFileName)

##################################
####    Utility Function  #######
##################################


##################################
####    Anomaly Definition #######
##################################
class MarkovAnoP(Anomaly):
    '''
    Users has Markov Behavior, Abnomal User has different stationary probability
    '''
    def __init__(self, t, ip, P2):
        Anomaly.__init__(self, t)
        self.ip = ip
        self.P2 = P2

    def Run(self, net):
        node = NNode(self.ip, self.ipdst, 0)
        start, end = self.t

        para = settings.MARKOV_PARA
        P = settings.MARKOV_P
        interval = settings.MARKOV_INTERVAL
        simT = settings.DEFAULT_PROFILE[1]

        mv1 = Markov(para, P, interval, (0, start))
        mv1.MHarpoon(node)
        mv2 = Markov(para, self.P2,  interval, (start, end))
        mv2.MHarpoon(node)
        mv3 = Markov(para, P, interval, (end, simT))
        mv3.MHarpoon(node)


        net.add_node(node)
        edge = NEdge(node, net.srvNode, net.link_attr)
        net.add_edge(edge)

        # Output the local IP address
        # fid = open('../atypical_IP.txt', 'w')
        # fid = open('../abnormal_user_IP.txt', 'w')
        fid = open(settings.ABNORMAL_USER_IP_FILE, 'w')
        # print 'ipdest: ', ipdest
        print 'self.ip: ', self.ip
        fid.write(self.ip)
        fid.close()

if __name__ == '__main__':
    GenMarkovTranAnomalyDot(2000, 3000, 0.1, 0.3, './out.dot')

