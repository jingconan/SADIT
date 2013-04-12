#!/usr/bin/env python
# from types import TupleType
'''
This module implement a typical K-means Clustering.
'''
from __future__ import print_function, division, absolute_import
from random import sample


## {{{ http://code.activestate.com/recipes/577661/ (r2)
import Queue as queue # replace with 'import queue' if using Python 3
class MedianHeap:
    def __init__(self, numbers = None):
        self.median = None
        self.left = queue.PriorityQueue() # max-heap
        self.right = queue.PriorityQueue() # min-heap
        self.diff = 0 # difference in size between left and right

        if numbers:
            for n in numbers:
                self.put(n)

    def top(self):
        return self.median

    def put(self, n):
        if not self.median:
            self.median = n
        elif n <= self.median:
            self.left.put(-n)
            self.diff += 1
        else:
            self.right.put(n)
            self.diff -= 1

        if self.diff > 1:
            self.right.put(self.median)
            self.median = -self.left.get()
            self.diff = 0
        elif self.diff < -1:
            self.left.put(-self.median)
            self.median = self.right.get()
            self.diff = 0

    def get(self):
        median = self.median

        if self.diff > 0:
            self.median = -self.left.get()
            self.diff -= 1
        elif self.diff < 0:
            self.median = self.right.get()
            self.diff += 1
        elif not self.left.empty():
            self.median = -self.left.get()
            self.diff -= 1
        elif not self.right.empty():
            self.median = self.right.get()
            self.diff += 1
        else: # median was the only element
            self.median = None

        return median

try:
    import numpy as np
    NUMPY = True
except:
    NUMPY = False

def GetMedian(numbers):
    if NUMPY:
        return float(np.median(numbers))
    else:
        m = MedianHeap(numbers)
        return m.get()

def ReClustering(data, centerPt, DF):
    cluster = []
    for pt in data:
        dv = []
        for c in centerPt:
            d = DF(pt, c)
            dv.append(d)
        md = min(dv)
        cluster.append(dv.index(md))
    return cluster

def Add(x, y):
    res = []
    for i in xrange(len(x)):
        res.append(x[i]+y[i])

    return res

def NDivide(cSum, cLen):
    res = []
    for i in xrange(len(cSum)):
        x = []
        for j in xrange(len(cSum[0])):
            x.append( cSum[i][j] * 1.0 / cLen[i] )

        res.append(x)
    return res

def CalClusteringCenterKMeans(data, cluster):
    ucLen = max(cluster) + 1
    cSum = [ [0] * len(data[0]) for i in xrange(ucLen)]
    cLen = [0] * ucLen
    i = -1
    for ele in data:
        i += 1
        cl = cluster[i]
        cSum[cl] = Add(cSum[cl], ele)
        cLen[cl] += 1

    try:
        cAve = NDivide(cSum, cLen)
    except:
        import pdb; pdb.set_trace()
    return cAve

def CalClusteringCenterKMedians(data, cluster):
    ucLen = max(cluster) + 1
    cMed = []
    for cl in xrange(ucLen):
        clusterData = [d for i, d in zip(cluster, data) if i == cl]
        med = [GetMedian(vals) for vals in zip(*clusterData)]
        cMed.append(med)
    return cMed

def Equal(x, y):
    if len(x) != len(y):
        return False
    for i in range(len(x)):
        if x[i] != y[i]:
            return False
    return True

def KMeans(data, k, distFunc):
# def KMedians(data, k, distFunc):
    print('start KMeans...')
    # Initialize
    centerPt = sample(data, k)
    while True:
        cluster = ReClustering(data, centerPt, distFunc)
        NewCenterPt = CalClusteringCenterKMeans(data, cluster)
        if Equal(NewCenterPt, centerPt):
            break
        centerPt = NewCenterPt

    return cluster, centerPt

def KMedians(data, k, distFunc):
# def KMeans(data, k, distFunc):
    print('start KMedians ...')
    # Initialize
    centerPt = sample(data, k)
    while True:
        cluster = ReClustering(data, centerPt, distFunc)
        NewCenterPt = CalClusteringCenterKMedians(data, cluster)
        if Equal(NewCenterPt, centerPt):
            break
        centerPt = NewCenterPt

    return cluster, centerPt


def test():
    data = [(5, 6, 8, 9),
            (10, 0, 4, 1),
            (10, 0, 2, 1),
            (10, 0, 5, 1),
            (10, 20, 30, 1),
            (10, 20, 30, 2),
            (10, 20, 30, 3),
            (10, 20, 30, 4),
            (1, 1, 1, 1),
            (10, 20, 30, 6),
            (10, 20, 30, 7),
            (10, 20, 30, 8),
            (10, 200, 1, 1),
            (10, 20, 30, 9),
            (10, 0, 3, 1),
            (2, 3, 5, 6),
            (10, 20, 30, 5)
            ]
    k = 3
    DF = lambda x,y:abs(x[0]-y[0]) * (256**3) + abs(x[1]-y[1]) * (256 **2) + abs(x[2]-y[2]) * 256 + abs(x[3]-y[3])
    # DF = lambda x,y:abs(x[0]-y[0]) * 2 + abs(x[1]-y[1]) * 2 + abs(x[2]-y[2]) * 2+ abs(x[3]-y[3]) * 2
    # DF = lambda x,y: ((x[0]-y[0]) ** 2) * (256 ** 3) + ((x[1]-y[1]) ** 2) * (256 **2) + ((x[2]-y[2]) ** 2) * (256)+ (x[3]-y[3]) ** 2
    # DF = lambda x,y:(x[0]-y[0]) ** 2  + (x[1]-y[1]) ** 2  + (x[2]-y[2]) ** 2 + (x[3]-y[3]) ** 2

    cluster, centerPt = KMeans(data, k, DF)
    print('cluster, ', cluster)
    print('centerPt, ', centerPt)

if __name__ == "__main__":
    from time import clock
    tic = clock()
    for i in xrange(1000):
        test()
    toc = clock()
    print('total simulation time is %f'%(toc-tic))
    # m = MedianHeap([1.4, 2.1, 5.0, 5.0])
    # print('median, ', m.get())

