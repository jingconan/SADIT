#!/usr/bin/env python
def binary_search(a, x, lo=0, hi=None):
    """
    Find the index of largest value in a that is smaller than x.
    a is sorted Binary Search
    """
    # import pdb;pdb.set_trace()
    if hi is None: hi = len(a)
    while lo < hi:
        mid = (lo + hi) / 2
        midval = a[mid]
        if midval < x:
            lo = mid + 1
        elif midval > x:
            hi = mid
        else:
            return mid
    return hi-1

Find = binary_search

import settings

import operator
def RFHash(v, q):
    assert( v < reduce(operator.mul, q))
    digit = []
    for i in xrange(len(q)):
        digit.append( v % q[i] )
        v = v / q[i]
    return digit

import numpy as np
def GetStateTable():
    QV = settings.DISCRETE_LEVEL + [settings.CLUSTER_NUMBER]
    QN = reduce(operator.mul, QV)
    sTable = [RFHash(i, QV) for i in xrange(QN)]
    return np.array(sTable)

import settings
Index = lambda mylist, ti:[i for i,n in enumerate(mylist) if n == ti]
FV = ['flowSize', 'flowRate', 'distToCenter', 'cluster']
TV = ['low', 'high']
sTable = GetStateTable()
def sFilter(cond):
    """
    Filter the state table by condition.
    cond is a dict in which each key value pair specify a condition
    for example if the cond = {'flowsize':'high', 'flowRate':'high'}
    means we want to find out the indices for states with high flow size
    and high flow arrival rate
    """
    iSet = set(range(sTable.shape[0]))
    for attr, tp in cond.iteritems():
        ai = FV.index(attr)
        ti = TV.index(tp)
        okIdx = Index( sTable[:, ai], ti)
        iSet = iSet & set(okIdx)
    return list(iSet)




def H1(v):
    pass








if __name__ == "__main__":
    # a = [1, 2, 3, 4, 5]
    # idx = Find2(a, 5)
    # print 'index, ', idx
    # sTable = GetStateTable()
    # print sTable
    # print sTable[:, 1]
    print sFilter({'flowSize':'high', 'flowRate':'high'})
