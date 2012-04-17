#!/usr/bin/env python
### --  Revision History --
### -- [2012-02-27 14:51:48] Extract Quantized State of Abnormal Flows --
### -- [2012-02-27 15:18:46] Merge the part of generating Nominal PDF to GenNominalPDF --
### --[2012-02-28 17:26:28] Revise TransData, make time start from 0
### -- [2012-02-28 19:07:40] add Mutliple Feature API ---

from DataParser import ParseData
from ClusterAlg import *

import sys
sys.path.append("..")
import settings
from util import *

import numpy as np
from pickle import dump, load
import copy

from Derivative import *
import util

import cPickle as pickle
try:
    from profilehooks import profile
except:
    print '[warning] profilehooks was not found ...'

def TransData(flow):
    uniqueIP = set()
    srcIP = []
    srcIPVec = []
    flowSize = []
    time = []
    endTime = []
    # i = 0
    for f in flow:
        uniqueIP.add( f['srcIP'] )
        srcIP.append( f['srcIP'] )
        srcIPVec.append( f['srcIPVec'] )
        flowSize.append( f['flowSize'] )
        time.append( f['t'] )
        endTime.append( f['endT'] )

    # return uniqueIP, srcIP, srcIPVec, flowSize
    sortIdx = np.argsort(time)
    sortedSrcIP = []
    sortedFlowSize = []
    sortedTime = []
    sortedDur = []
    for idx in sortIdx:
        sortedSrcIP.append(srcIPVec[idx])
        sortedFlowSize.append(flowSize[idx])
        sortedTime.append(time[idx])
        sortedDur.append( endTime[idx] - time[idx] )

    # minT = min(sortedTime)
    # sortedTimeAligned = [t - minT for t in sortedTime]
    return sortedSrcIP, sortedFlowSize, sortedTime, sortedDur
    # return sortedSrcIP, sortedFlowSize, sortedTimeAligned, sortedDur
    # return srcIPVec, flowSize, time

def GetDistToCenter(data, cluster, centerPt, DF):
    i = -1
    dis = []
    for x in data:
        i += 1
        cl = cluster[i]
        dis.append( DF( x, centerPt[cl] ) )

    return dis

def QuantizeState(x, nx, rg):
    minVal, maxVal = rg
    stepSize = (maxVal - minVal) * 1.0 / (nx - 1 )
    res = []
    g = []
    # print 'stepSize: ' + str(stepSize)
    for ele in x:
        seq = round( (ele - minVal ) / stepSize )
        if seq >= nx:
            # import pdb; pdb.set_trace()
            seq = nx
        y = minVal +  seq * stepSize
        res.append(y)
        g.append(seq)
    return res, g

# @profile
def ModelBased(gc, gd, gf, K, ND, NF):
    P = np.zeros( (K * ND * NF, K * ND * NF) )
    fl = len(gc)
    mp = np.zeros((K*ND*NF, ))

    m_list = [gc[i] + gd[i]*K + gf[i]*K*ND for i in xrange(fl)]
    for i in xrange(fl-1):
        mp[m_list[i]] += 1
        P[m_list[i], m_list[i+1]] += 1
    mp[m_list[fl-1]] += 1

    P = P * 1.0 / (fl-1)
    mp = mp / fl
    return P, mp

def ModelFree(gc, gd, gf, K, ND, NF):
    P = np.zeros( (K * ND * NF, ) )
    fl = len(gc)
    # import pdb; pdb.set_trace()
    m_list = [gc[i] + gd[i]*K + gf[i]*K*ND for i in xrange(fl)]
    for i in range(fl):
        idx = m_list[i]
        try:
            P[idx] += 1
        except:
            import pdb; pdb.set_trace()
    P = P * 1.0 / fl
    assert(abs( np.sum(np.sum(P, 0)) - 1.0) < 0.01)
    return P

def I1(nu, mu):
    a, = np.shape(nu)
    # for i in range(a):
        # if mu[i] == 0 or nu[i] == 0:
            # continue
        # e += nu[i] * np.log( nu[i] * 1.0 / mu[i] )
    F = lambda x, y:x * np.log( x * 1.0 / y )
    nonZeroIdxSet = [i for i in xrange(a) if mu[i] !=0 and nu[i]!=0]

    # FIXME find better to make sure e is nonnegative
    # nu = nu / np.sum(nu[nonZeroIdxSet])
    # mu = mu / np.sum(mu[nonZeroIdxSet])
    e =  sum( F(nu[i], mu[i]) for i in nonZeroIdxSet ) #  ele in nonZeroIdxSet for both nu and mu should sum to 1 to make e nonnegative.
    return abs(e)
    # return e

def I2(P1, mp1, P2, mp2):
    # mp1 = mp1 / np.sum(mp1)
    # mp2 = mp2 / np.sum(mp2)
    assert( abs(np.sum(mp1)  - 1.0 ) < 1e-3 and abs(np.sum(mp2) - 1.0 ) < 1e-3)
    # if np.sum(mp1) == 0 or np.sum(mp2) == 0:
        # raise ValueError('sum zero')

    a, b = np.shape(P1)
    P1Con = copy.deepcopy(P1)
    P2Con = copy.deepcopy(P2)
    for i in range(a):
        for j in range(b):
            if mp1[i] != 0:
                P1Con[i, j] /= mp1[i]
            if mp2[i] != 0:
                P2Con[i, j] /= mp2[i]
    # Compute Expectation of Each Relative Entropy
    y = 0
    for i in range(a):
        y += mp1[i] * I1(P1Con[i, :], P2Con[i, :])
    return y

def FindCenter(data, centerPt, DF):
    cluster = []
    distToCenter = []
    for pt in data:
        dv = []
        for c in centerPt:
            d = DF(pt, c)
            dv.append(d)
        md = min(dv)
        cluster.append(dv.index(md))
        distToCenter.append(md)
    return cluster, distToCenter

# def Find(L, th):
#     i = -1
#     for val in L:
#         i += 1
#         if val > th:
#             return i-1


def GetRange(srcIPVec, clusterNum, flowSize):
    cluster, centerPt = KMeans(srcIPVec, clusterNum, DF)
    distToCenter = GetDistToCenter(srcIPVec, cluster, centerPt, DF)
    distRange = [min(distToCenter), max(distToCenter)]
    flowSizeRange = [min(flowSize), max(flowSize)]
    return distRange, flowSizeRange, cluster, centerPt

def GetFeature(srcIPVec, cluster, centerPt, flowSize, distRange, flowSizeRange, ND, NF):
    '''Return Quantized distance and flowsize as feature'''
    distToCenter = GetDistToCenter(srcIPVec, cluster, centerPt, DF)
    u, posDist = QuantizeState( distToCenter, ND, distRange)
    u, posFlowSize = QuantizeState( flowSize , NF, flowSizeRange)
    return posDist, posFlowSize

# The Distance Function
DF = lambda x,y:abs(x[0]-y[0]) * (256**3) + abs(x[1]-y[1]) * (256 **2) + abs(x[2]-y[2]) * 256 + abs(x[3]-y[3])

# NominalPDFFile = '../share/detect/nominal.p'
NominalPDFFile = settings.NominalPDFFile


##########################################################################################
#### API For Support Multiple Feature
##########################################################################################

# def GetAllPDF(srcIPVec, cluster, centerPt, flowSize, distRange, flowSizeRange, ND, NF):
# @profile
def GetAllPDF_MF(srcIPVec, cluster, centerPt, feature, distRange, featureRange,  clusterNum, ND, featureQ):
    '''This Function Support Multiple Features, _MF means multiple feature
    feature is a list contains all features
    featureQ is a list of quantization set that specifies the quantization level of each feature
    '''
    distToCenter = GetDistToCenter(srcIPVec, cluster, centerPt, DF)
    u, posDist = QuantizeState( distToCenter, ND, distRange)

    posFeature = []
    for i in xrange(len(feature)):
        u, qLevel = QuantizeState( feature[i] , featureQ[i], featureRange[i])
        posFeature.append(qLevel)

    pmf = ModelFree_MF(cluster, posDist, posFeature, clusterNum, ND, featureQ)
    Pmb, mpmb = ModelBased_MF(cluster, posDist, posFeature, clusterNum, ND, featureQ)
    return pmf, Pmb, mpmb

import operator

# @profile
def FeatureHash(digit, level):
    return digit[0] + digit[1] * level[0] + digit[2] * level[1] * level[0]
    # return digit[2] + digit[1] * level[0] + digit[0] * level[1] * level[0]
    # value = digit[0]
    # for i in xrange(len(digit)-1):
        # value += digit[i+1] * reduce(operator.mul, level[0:i+1])
    # return value

import copy


def UnifyF(c, d, feature):
    '''Append c and d to feature'''
    plain = copy.deepcopy(feature)
    plain.append(c)
    plain.append(d)
    return plain

def GetFeatureHashList(gc, gd, posFeature, K, ND, featureQ):
    '''Generate Has Value for all possible features'''
    unifyFeature = UnifyF(gc, gd, posFeature)
    unifyQ = UnifyF(K, ND, featureQ)
    fl = len(gc)
    # import pdb;pdb.set_trace()
    unifyAlignFeature = [ [ f[i] for f in unifyFeature ] for i in xrange(fl)]
    m_list = [ FeatureHash(f, unifyQ) for f in unifyAlignFeature ]
    return m_list

def ModelBased_MF(gc, gd, posFeature, K, ND, featureQ):
    QLevelNum = reduce(operator.mul, featureQ) * K * ND
    P = np.zeros( (QLevelNum, QLevelNum) )
    fl = len(gc)
    mp = np.zeros((QLevelNum, ))
    m_list = GetFeatureHashList(gc, gd, posFeature, K, ND, featureQ)

    for i in xrange(fl-1):
        mp[m_list[i]] += 1
        P[m_list[i], m_list[i+1]] += 1
    mp[m_list[fl-1]] += 1

    P = P * 1.0 / (fl-1)
    mp = mp / fl
    return P, mp

def ModelFree_MF(gc, gd, posFeature, K, ND, featureQ):
    QLevelNum = reduce(operator.mul, featureQ) * K * ND
    P = np.zeros( (QLevelNum, ) )
    fl = len(gc)
    m_list = GetFeatureHashList(gc, gd, posFeature, K, ND, featureQ)

    for i in range(fl):
        idx = m_list[i]
        try:
            P[idx] += 1
        except:
            import pdb; pdb.set_trace()
    P = P * 1.0 / fl
    assert(abs( np.sum(np.sum(P, 0)) - 1.0) < 0.01)
    return P

##########################################################################################
####  END API For Support Multiple Feature
##########################################################################################


def GenNominalPDF(fName, clusterNum, ND, NF):
    # Generate Nominal PDF
    flow = ParseData(fName);
    srcIPVec, flowSize, t, dur = TransData(flow)
    distRange, flowSizeRange, cluster, centerPt = GetRange(srcIPVec, clusterNum, flowSize)

    normalStart = 0
    normalEnd = Find(t, settings.ANOMALY_TIME[0] - 10) + 1

    #FIXME Add feature like flow duration and estimation of flow arrival rate
    pmf, Pmb, mpmb = GetAllPDF_MF(srcIPVec[normalStart:normalEnd], cluster[normalStart:normalEnd],
            centerPt, [flowSize[normalStart:normalEnd]],
            distRange, [flowSizeRange],
            clusterNum, ND, [NF])

    data = pmf, Pmb, mpmb, distRange, flowSizeRange, cluster, centerPt
    pickle.dump( data, open(NominalPDFFile, 'w') )
    return pmf, Pmb, mpmb, distRange, flowSizeRange, cluster, centerPt


# from AnomalyAna import AddAnoFlag

def Detect(fName, clusterNum, ND, NF, wSize):
    flow = ParseData(fName);
    srcIPVec, flowSize, t, dur = TransData(flow)
    ### Generate Nominal PDF ###
    if settings.UNIFIED_NOMINAL_PDF:
        pmf, Pmb, mpmb, distRange, flowSizeRange, cluster, centerPt = pickle.load(open(NominalPDFFile, 'r'))
    else:
        pmf, Pmb, mpmb, distRange, flowSizeRange, cluster, centerPt = GenNominalPDF(fName, clusterNum, ND, NF)

    IF, IB, winT = [], [], []
    threshold = []

    lp = 0 # last Position
    idx = 0 # current position
    time = 0
    ti = settings.DETECTOR_INTERVAL
    detectNum = ( len(flow) / dInter - 1 ) if (settings.WINDOW_TYPE == 'FLOW') else int((max(t)-wSize )/ti)
    minT = min(t)

    CleanGlobalDeri()
    for i in range(detectNum):
        # Find Data
        if settings.WINDOW_TYPE == 'FLOW':
            lp = idx + 1
            idx += wSize
            time = t[lp]
        elif settings.WINDOW_TYPE == 'TIME':
            time += ti
            lp = Find(t, time)
            idx = Find(t, time+wSize)
        else:
            raise ValueError('unknow window type')

        print 'time: %f' %(time - minT)

        sIP = srcIPVec[lp:(idx+1)]
        fs = flowSize[lp:(idx+1)]
        localCluster = cluster[lp:(idx+1)]
        if len(fs) == 0:
            continue

        # Update Hoeffding test threshold
        threshold.append( idx-lp+1 ) #FIXME it is not real threshold

        d_pmf, d_Pmb, d_mpmb = GetAllPDF_MF(sIP, localCluster, centerPt, [fs], distRange, [flowSizeRange],  clusterNum, ND, [NF])

        mfEntro = I1(d_pmf, pmf)
        mbEntro = I2(d_Pmb, d_mpmb, Pmb, mpmb)
        IF.append(mfEntro)
        IB.append(mbEntro)
        winT.append(time)

        # Identify the Most significant state transition for model-base case
        modelFreeDeri= ModelFreeDerivative(d_pmf, pmf)
        modelBaseDeri = ModelBaseDerivative(d_Pmb, d_mpmb, Pmb, mpmb)
        # util.Dump2Txt(deri, './deri.res', '2dnp')

    DumpDerivative()
    if settings.PLOT_DERIVATIVE:
        PlotModelBase()
        PlotModelFree()

    return IF, IB, winT, threshold

from matplotlib.pyplot import *
def Compare(fName, dataName= ''):
    ws = settings.DETECTOR_WINDOW_SIZE
    prefix = settings.DETECTOR_PREFIX
    clusterNum = settings.CLUSTER_NUMBER
    ND, NF = settings.DISCRETE_LEVEL

    # print 'Window Size: ', ws
    # print 'Prefix: ', prefix

    IF2, IB2, t2, threshold = Detect(fName=fName,
            clusterNum=clusterNum,
            ND=ND,
            NF=NF,
            wSize = ws)

    if dataName != '':
        import cPickle as pickle
        # data = t2, IF2, IB2 #FIXME ATTENTION the order
        data = t2, IF2, IB2, threshold
        pickle.dump( data, open(dataName, 'w') )
    else:
        figure()
        subplot(211)
        plot(t2, IF2)
        subplot(212)
        plot(t2, IB2)
        show()

if __name__ == "__main__":
    import sys,os
    os.system('cp ../settings_template.py ../settings.py')
    Compare(sys.argv[1], sys.argv[2])
