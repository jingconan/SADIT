"""
======================
Multi Sever Detector
======================
it can detect anomaly for multi server. some anomaly which is
not detectale in one server case may be able to detected
in this case.
"""

import sys
sys.path.append("..")
import settings

from Detector import *

# from settings import ROOT
import settings
# srv_list = settings.NET_DESC['srv_list']

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
    return sortedSrcIP, sortedFlowSize, sortedTime, sortedDur, sortIdx

def GetSrvFlowFile(sl):
    return [settings.ROOT + '/Simulator/n%s_flow.txt'%(i) for i in sl]

def MS_GetFeature(srvFlowNameList, clusterNum):
    """get features for all servers"""
    # return [ GetFeature(fName, clusterNum, cutHead=True) for fName in srvFlowNameList ]
    # import pdb;pdb.set_trace()
    flowSet = [ParseData(fName) for fName in srvFlowNameList]
    flow = []
    i = -1
    srvID = []
    for f in flowSet:
        i += 1
        flow += f #FIXME merge too dict
        srvID += [i]*len(f)

    # import pdb;pdb.set_trace()
    try:
        srcIPVec, flowSize, t, dur, sortIdx = TransData(flow)
    except:
        import pdb;pdb.set_trace()

    # import pdb;pdb.set_trace()
    cluster, centerPt = KMeans(srcIPVec, clusterNum, DF)
    distToCenter = GetDistToCenter(srcIPVec, cluster, centerPt, DF)
    flowRate = GetFlowRate(t, cluster)

    exec settings.LOAD_FEATURE

    sortSrvID = [srvID[i] for i in sortIdx]
    feaVec.append(sortSrvID)

    quanFlag = ( len(feaVec) - 2 ) * [1] + [0, 0]
    feaRange = GetRange(feaVec)
    return feaVec, feaRange, quanFlag, t, centerPt


def CombineMSRecord(feaSet):
    res = feaSet[0]
    res.append([0]*len(res[0]))
    srv_id = 0
    for fs in feaSet[1:]:
        srv_id += 1
        for i in xrange(len(res)-1):
            res[i].append(fs[i])
        res[-1] = [srv_id] * len(fs[0])
    return res

def GetCombineFeature(srvFlowNameList, feaQN):
    # import pdb;pdb.set_trace()
    feaVec, feaRange, quanFlag, t, centerPt = MS_GetFeature(srvFlowNameList, feaQN[-1])
    c_feaQN = feaQN + [len(srvFlowNameList)]
    return feaVec, feaRange, c_feaQN, quanFlag, t, centerPt

def MS_GenNominalPDF(srvFlowNameList, feaQN, dumpFlag =False):
    c_feaVec, c_feaRange, c_feaQN, quanFlag, t, centerPt = GetCombineFeature(srvFlowNameList, feaQN)
    ns = Find(t, min(t) + settings.FLOW_RATE_ESTIMATE_WINDOW)
    ne = Find(t, min(t) + settings.ANOMALY_TIME[0] - 10) + 1
    n_feaVec = SL(c_feaVec, ns, ne)
    # import pdb;pdb.set_trace()

    pmf, Pmb, mpmb = GetAllPMF(n_feaVec, c_feaQN, c_feaRange, quanFlag)
    return pmf, Pmb, mpmb, c_feaVec, c_feaQN, c_feaRange,  quanFlag, t, centerPt


def Detect(srvList, feaQN, wSize):
    srvFlowFile = GetSrvFlowFile(srvList)
    print 'srvFlowFile, ', srvFlowFile
    pmf, Pmb, mpmb, feaVec, feaQN, feaRange, quanFlag, t, centerPt = MS_GenNominalPDF(srvFlowFile, feaQN)

    IF, IB, winT = [], [], []
    threshold = []

    lp = 0 # last Position
    idx = 0 # current position
    ti = settings.DETECTOR_INTERVAL
    # time = 0
    minT = min(t)
    time = minT + settings.FLOW_RATE_ESTIMATE_WINDOW
    sIdx = Find(t, minT + settings.FLOW_RATE_ESTIMATE_WINDOW)
    detectNum = ( ( len(flow) - sIdx ) / dInter - 1 - sIdx ) if (settings.WINDOW_TYPE == 'FLOW') else int((max(t)-wSize - time )/ti)
    print 'detectNum, ', detectNum

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
        d_feaVec = SL(feaVec, lp, idx+1)

        # Update Hoeffding test threshold
        threshold.append( idx-lp+1 ) #FIXME it is not real threshold

        d_pmf, d_Pmb, d_mpmb = GetAllPMF(d_feaVec, feaQN, feaRange,  quanFlag)


        mfEntro = I1(d_pmf, pmf)
        mbEntro = I2(d_Pmb, d_mpmb, Pmb, mpmb)
        if mbEntro ==0:
            import pdb;pdb.set_trace()
        IF.append(mfEntro)
        IB.append(mbEntro)
        winT.append(time)

    return IF, IB, winT, threshold

