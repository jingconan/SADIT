#!/usr/bin/env python

# -- Created at [2012-02-27 14:53:50] --
# -- [2012-02-27 15:54:26] Add GetAbnormalFlowQType() --
# -- [2012-02-27 21:27:18] Add ModelFreeDetectAnoType() --
# -- [2012-02-28 12:15:20] Add ModelBseDetectAnoType --
# -- [2012-03-03 00:02:09] Revise FeaRange --
# -- [2012-03-21 23:43:11] add savefig and add "component" to replace derivative


import sys
sys.path.append("..")
import settings
from DataParser import ParseData
import cPickle as pickle

import numpy as np


import operator
def RFHash(v, q):
    """
    RFHash(v, q)
    Reverse Hash Function, v is is a integer,
    q is corresponding quantize level
    """
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



# def AddAnoFlag(flows):
#     abnormal_flows = ParseData('../Simulator/abnormal_flow.txt')
#     abIdxSet = []
#     for f in abnormal_flows:
#         idx = flows.index(f)
#         abIdxSet.append(idx)
#         flows[idx]['anoFlag']= True

#     normalIdxSet = [i for i in xrange(len(flows)) if i not in abIdxSet]
#     for i in normalIdxSet:
#         flows[i]['anoFlag'] = False

#     return flows

from ClusterAlg import ReClustering
from Detector import *
import operator

def AnoGetFeature(fName, centerPt):
    flow = ParseData(fName);
    srcIPVec, flowSize, t, dur = TransData(flow)

    cluster = ReClustering(srcIPVec, centerPt, DF)
    distToCenter = GetDistToCenter(srcIPVec, cluster, centerPt, DF)

    nominalFlow = ParseData(settings.OUTPUT_FLOW_FILE)
    srcIPVec0, flowSize0, t0, dur0 = TransData(nominalFlow)
    cluster0 = ReClustering(srcIPVec0, centerPt, DF)

    flowRate0 = GetFlowRate(t0, cluster0)
    flowRate = [ flowRate0[Find(t0, tv)+1 ] for tv in t]

    exec settings.LOAD_FEATURE
    # print 'flowRate, ', flowRate
    quanFlag = ( len(feaVec) - 1 ) * [1] + [0]
    feaRange = GetRange(feaVec)
    return feaVec, feaRange, quanFlag, t

from Detector import vector_quantize_states
import cPickle as pickle
# @profile
def GetAbnormalFlowQType():
    '''Get Quantized State for Abnormal Flows. '''
    fName = settings.ROOT + '/Simulator/abnormal_flow.txt'
    clusterNum = settings.CLUSTER_NUMBER
    feaQN = settings.DISCRETE_LEVEL + [clusterNum]
    feaRange, centerPt = pickle.load(open(settings.ANO_ANA_DATA_FILE, 'r'))
    # print 'feaRange, ', feaRange
    feaVec, feaRange0, quanFlag, t = AnoGetFeature(fName, centerPt)
    # print 'feaVec, ', feaVec
    # import pdb;pdb.set_trace()
    # print 'feaVec, ', feaVec
    qFeaVec = vector_quantize_states(feaVec , feaQN, feaRange, quanFlag)
    return qFeaVec

from Detector import f_hash, get_feature_hash_list
import collections
def GetAnomalyType():
    '''Get the Type for each abnormal flows, print them out'''
    qFeaVec = GetAbnormalFlowQType()
    # print 'qFeaVec, ', qFeaVec
    feaQN = settings.DISCRETE_LEVEL + [settings.CLUSTER_NUMBER]
    feaHash = get_feature_hash_list(qFeaVec, feaQN)
    counter=collections.Counter(feaHash)
    print 'the anomaly flows are type, ', counter


def LoadDeriData():
    modelFreeDeri = pickle.load(open(settings.MODEL_FREE_DERI_DUMP_FILE, 'r'))
    modelBaseDeri = pickle.load(open(settings.MODEL_BASE_DERI_DUMP_FILE, 'r'))
    import pdb;pdb.set_trace()
    return modelFreeDeri, modelBaseDeri

StateMap = [('low flow size', 'small distance'),
        ('low flow size', 'large distance'),
        ('large flow size', 'small distance'),
        ('large flow size', 'large distance')]

def CalIndicator(deri, intervalRatio):
    '''Calculate the difference of derivative on anomaly time w.r.t normal '''
    tn = len(deri)
    anoStart = int( tn * intervalRatio[0])
    anoStop = int( tn * intervalRatio[1] )
    anoDeri = deri[anoStart:anoStop+1]
    anoAveDeri = np.nansum(anoDeri, axis=0) * 1.0 / len(anoDeri)
    normalAnoValue = np.nansum(deri, axis=0) * 1.0 / tn
    # print 'normalAnoValue, ', normalAnoValue
    # GetChangePercent = lambda a, b:np.abs(np.array(a)-np.array(b)) / np.abs(np.array(b))
    # GetChangePercent = lambda a, b:np.abs(np.array(a)-np.array(b))
    GetChangePercent = lambda a, b:np.array(a)-np.array(b)
    changePer = GetChangePercent(anoAveDeri, normalAnoValue)
    return changePer


def ModelFreeDetectAnoType():
    modelFreeDeri = pickle.load(open(settings.MODEL_FREE_DERI_DUMP_FILE, 'r'))
    totalT = settings.DEFAULT_PROFILE[1]
    assert(settings.WINDOW_TYPE == 'TIME')
    anoT = settings.ANOMALY_TIME
    intervalRatio = [anoT[0] * 1.0/totalT, anoT[1] * 1.0/totalT ]
    anoIndi = CalIndicator(modelFreeDeri, intervalRatio)
    return anoIndi

def ModelBaseDetectAnoType():
    modelBaseDeri = pickle.load(open(settings.MODEL_BASE_DERI_DUMP_FILE, 'r'))
    totalT = settings.DEFAULT_PROFILE[1]
    assert(settings.WINDOW_TYPE == 'TIME')
    anoT = settings.ANOMALY_TIME
    anoIndi = CalIndicator(modelBaseDeri,
            [anoT[0] * 1.0/totalT, ( anoT[0] + anoT[1] ) / ( 2.0* totalT) ])
    return anoIndi



def PrintFriendly(flag):
    for i in xrange(len(flag)):
        print FV[i], TV[flag[i]], '\t',
    print '\n'


from matplotlib.pyplot import *
def ModelFreeHTest(v):
    """
    Test the type of the anomaly with ModelFree Indicator
    """
    th = settings.DERI_TEST_THRESHOLD
    sortDesIdx = list( np.argsort(-1*v) )
    # print 'sortIdx: ', sortDesIdx
    print 'descending derivative: ', v[sortDesIdx]
    figure()
    plot(v[sortDesIdx], '*-')
    title('descending derivative')
    ylabel('derivative')
    savefig(settings.MODEL_FREE_DERI_DESCENDING_FIG)
    close()
    # show()
    # import pdb;pdb.set_trace()
    lastSigIdx = np.nonzero( v[sortDesIdx] > th )[0][-1] #FIXME give hint when threshold is improper
    print 'the suspicious states are: '
    for i in xrange(lastSigIdx+1):
        print 'State [%d]: '%(sortDesIdx[i]),
        PrintFriendly( sTable[sortDesIdx[i], :] )


import numpy as np
def ModelBaseHTest(v):
    """
    Test the type of the anomaly with Model Base Indicator
    """
    m, n = v.shape
    fv = v.flatten() # row major
    th = settings.DERI_TEST_THRESHOLD
    sortDesIdx = list( np.argsort(-1*fv) )
    # print 'sortIdx: ', sortDesIdx
    print 'descending derivative: ', fv[sortDesIdx]
    figure()
    plot(fv[sortDesIdx], '*-')
    title('descending derivative')
    ylabel('derivative')
    savefig(settings.MODEL_BASE_DERI_DESCENDING_FIG)
    close()
    # show()
    lastSigIdx = np.nonzero( fv[sortDesIdx] > th )[0][-1]
    Idx2Sub = lambda x: (x / m, x % m)
    print sortDesIdx[:lastSigIdx]
    subVec = [Idx2Sub(idx) for idx in sortDesIdx[:lastSigIdx]]
    # print 'sort sub:', subVec
    desVec = [x[1] for x in subVec]
    # print 'desVec: ', desVec
    print 'the suspicious states are: '
    for d in desVec:
        # print 100 * '-'
        print 'state [%d]: ' %(d),
        PrintFriendly( sTable[d, :])



    pass

if __name__ == "__main__":
    # posDist, posFlowSize = GetAbnormalFlowQType()
    # value = [x + 2*y for x, y in zip(posDist, posFlowSize)]
    # print value
    # LoadDeriData()
    # anoTypeIdx = ModelFreeDetectAnoType()
    ModelFreeDetectAnoType()
    ModelBaseDetectAnoType()
    # anoType = GetAnomalyType()
    # if anoTypeIdx == anoType:
    #     print 'match'
    # else:
    #     print 'unmatch'

