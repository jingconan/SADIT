#!/usr/bin/env python
### -- Created at [2012-03-01 14:55:21]
### -- [2012-03-01 17:13:27] support multi feature

from OldDetector import *

from matplotlib.pyplot import *
def Compare(fName, dataName= ''):
    IF2, IB2, t2, threshold = Detect(fName,
            settings.DISCRETE_LEVEL + [settings.CLUSTER_NUMBER],
            settings.DETECTOR_WINDOW_SIZE)

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

import operator
def FHash(digit, level):
    # return digit[0] + digit[1] * level[0] + digit[2] * level[1] * level[0]
    value = digit[0]
    for i in xrange(len(digit)-1):
        value += digit[i+1] * reduce(operator.mul, level[0:i+1])
    return value

def GetFeatureHashList(F, Q):
    return [ FHash(f, Q) for f in zip(*F) ]

def ModelBased(qFeaVec, feaQN):
    QLevelNum = reduce(operator.mul, feaQN)
    P = np.zeros( (QLevelNum, QLevelNum) )
    fl = len(qFeaVec[0])
    mp = np.zeros((QLevelNum, ))
    m_list = GetFeatureHashList(qFeaVec, feaQN)

    for i in xrange(fl-1):
        mp[m_list[i]] += 1
        P[m_list[i], m_list[i+1]] += 1
    mp[m_list[fl-1]] += 1

    P = P * 1.0 / (fl-1)
    mp = mp / fl
    return P, mp

def ModelFree(qFeaVec, feaQN):
    QLevelNum = reduce(operator.mul, feaQN)
    P = np.zeros( (QLevelNum, ) )
    fl = len(qFeaVec[0])
    m_list = GetFeatureHashList(qFeaVec, feaQN)

    for i in range(fl):
        idx = m_list[i]
        try:
            P[idx] += 1
        except:
            import pdb; pdb.set_trace()
    P = P * 1.0 / fl
    assert(abs( np.sum(np.sum(P, 0)) - 1.0) < 0.01)
    return P


def VectorQuantizeState(feaVec , feaQN, feaRange, quanFlag=None):
    if not quanFlag: quanFlag = len(data) * [1]
    QS = lambda a, b, c, flag: QuantizeState(a, b, c)[1] if flag else a
    return [ QS(a, b, c, flag) for a, b, c, flag in zip(feaVec , feaQN, feaRange, quanFlag) ]

def GetAllPMF(feaVec, feaQN, feaRange,  quanFlag=None):
    '''This Function Support Multiple Features, get probability mass function'''
    qFeaVec = VectorQuantizeState(feaVec, feaQN, feaRange, quanFlag)
    pmf = ModelFree(qFeaVec, feaQN)
    Pmb, mpmb = ModelBased(qFeaVec, feaQN)
    return pmf, Pmb, mpmb

def GetFlowRate(t, cluster):
    '''Get Estimation of Flow Rate For Each User'''
    win = settings.FLOW_RATE_ESTIMATE_WINDOW
    fr = []
    for i in xrange(len(t)):
        idx = Find(t, t[i] - win)
        if idx == -1: idx = 0
        c = cluster[i]
        fr.append( cluster[idx:i] )





def GetFeature(fName, clusterNum):
    flow = ParseData(fName);
    srcIPVec, flowSize, t, dur = TransData(flow)

    cluster, centerPt = KMeans(srcIPVec, clusterNum, DF)
    distToCenter = GetDistToCenter(srcIPVec, cluster, centerPt, DF)

    exec settings.LOAD_FEATURE
    # feaVec = [flowSize,
            # dur,
            # flowRate, # flow arrival rate
            # distToCenter, #distance to quantization center
            # cluster, # cluster is the last one
            # ]

    quanFlag = ( len(feaVec) - 1 ) * [1] + [0]
    feaRange = GetRange(feaVec)
    return feaVec, feaRange, quanFlag, t

# def GenNominalPDF(fName, clusterNum, ND, NF, dumpFlag =False):
def GenNominalPDF(fName, feaQN, dumpFlag =False):
    feaVec, feaRange, quanFlag, t = GetFeature(fName, feaQN[-1])

    ns = 0 # normal start
    ne = Find(t, settings.ANOMALY_TIME[0] - 10) + 1
    n_feaVec = SL(feaVec, ns, ne)

    pmf, Pmb, mpmb = GetAllPMF(n_feaVec, feaQN, feaRange,  quanFlag)

    data = pmf, Pmb, mpmb, feaRange
    if dumpFlag:
        pickle.dump( data, open(NominalPDFFile, 'w') )
    return pmf, Pmb, mpmb, feaVec, feaQN, feaRange,  quanFlag, t

def SL(data, st, ed):
    return [d[st:ed] for d in data]

def GetRange(data):
    return [ (min(x), max(x)) for x in data]

def Detect(fName, feaQN, wSize):
    '''
    feaVec is a list contains all features, len(feaVec) equals to the number of features
    feaRange is a list, each element in the list is a tuple contains the range
    in current version, feature includes:
        1. cluster --> don't need to quantize
        2. distance to cluster center --> quantize
        3. flow size --> quantize
        4. estimate of flow rate --> quantize
    feaVec    |--> qFeaVec --> GenPDF
    feaRange  |
    '''
    ### Generate Nominal PDF ###
    if settings.UNIFIED_NOMINAL_PDF:
        pmf, Pmb, mpmb, distRange, flowSizeRange, cluster, centerPt = pickle.load(open(NominalPDFFile, 'r'))
        feaVec, feaRange, quanFlag, t = GetFeature(fName)
    else:
        pmf, Pmb, mpmb, feaVec, feaQN, feaRange,  quanFlag, t = GenNominalPDF(fName, feaQN)

    IF, IB, winT = [], [], []
    threshold = []

    lp = 0 # last Position
    idx = 0 # current position
    time = 0
    ti = settings.DETECTOR_INTERVAL
    detectNum = ( len(flow) / dInter - 1 ) if (settings.WINDOW_TYPE == 'FLOW') else int((max(t)-wSize )/ti)

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

        print 'time: %f' %(time)
        d_feaVec = SL(feaVec, lp, idx+1)

        # Update Hoeffding test threshold
        threshold.append( idx-lp+1 ) #FIXME it is not real threshold

        d_pmf, d_Pmb, d_mpmb = GetAllPMF(d_feaVec, feaQN, feaRange,  quanFlag)


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


if __name__ == "__main__":
    import sys,os
    os.system('cp ../settings_template.py ../settings.py')
    Compare(sys.argv[1], sys.argv[2])
