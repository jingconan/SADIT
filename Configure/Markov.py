#!/usr/bin/env python
# Input is the transition probability. p_h2l, pl2h
# Node need provide an important function, AddModulator.
# This
# AddModulator(t, para ), where t is the range of the modulator, and para is the
# parameters needed for the modulator.
# from random import randint
import random
from random import expovariate as exponential

def RandDist(dist):
    '''Generate Random Variable According to Certain Kind of
    Distribution'''

    # TODO Finish A Complete Version
    s = 0
    rv = random.random()
    m = -1
    for p in dist:
        m += 1
        s += p
        if s > rv:
            break

    return m

# class Node:
#     def __init__(self):
#         self.s = []

#     def AddModulator(self, start, end, para, s):
#         self.s.append(s)

#     def Stat(self):
#         sn = 2
#         p = [0] * sn
#         for s in self.s:
#             for i in range(sn):
#                 if s == i:
#                     p[i] += 1
#         sump = 0
#         for pr in p:
#             sump += pr
#         for i in range(sn):
#             p[i] /= ( sump * 1.0)
#         print 'the stationary probability is: ', p



class Markov:
    def __init__(self, para, P, interval, tRange, X=[]):
        ''' X: the label of each state, for showing output
        para is a list of tuple that contains the parameters for each state
        P : the transition probability
        interval: the interval between consequent decision time
        tRange: Markov Modulation Range '''
        print 'Markov'
        self.para = para
        self.P = P
        self.interval = interval
        self.tRange = tRange

    def MHarpoon(self, node):
        '''The input of Run is an empty node, node will be moduled in markovian way'''
        start, end = self.tRange
        interval = self.interval
        P = self.P
        para = self.para
        t = start
        sn = len(self.para) # state number
        cs = random.randint(0, sn-1) # cs: current state
        while True:
            # Determine the State the Node should be
            cs = RandDist(P[cs])
            # node.AddModulator(t, t+interval, para[cs], cs)
            inter = exponential(interval)
            node.AddHarpoon(t, t+inter, para[cs])
            t += inter
            # node.AddHarpoon(t, t+interval, para[cs])
            # t += interval
            if t > end:
                break
        # node.Stat()




if __name__ == "__main__":
    para = [(1, 2), (2, 3)]
    P = [(0.7, 0.3), (0.6, 0.4)]
    # print 'P: ', str(P)
    mv = Markov(para, P, 0.0001, (10, 100))
    node = Node()
    mv.MHarpoon(node)
