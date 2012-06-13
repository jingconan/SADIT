#!/usr/bin/env python
"""A library of utility function that will be used by detectors
"""
### -- Created at [2012-03-01 14:55:21]
### -- [2012-03-01 17:13:27] support multi feature
### -- [2012-03-01 22:05:29] get_flow_rate, test with flowSize, dur, flowRate

# from OldDetector import *
import sys
sys.path.append("..")

import settings
from util import *

from DataParser import ParseData
from ClusterAlg import *
from Derivative import *

try:
   from matplotlib.pyplot import *
except:
   print 'no matplotlib'
   VIS = False

import operator
import Detector.AnomalyDetector

# The Distance Function
DF = lambda x,y:abs(x[0]-y[0]) * (256**3) + abs(x[1]-y[1]) * (256 **2) + abs(x[2]-y[2]) * 256 + abs(x[3]-y[3])

def I2(P1, mp1, P2, mp2):
    assert( abs(np.sum(mp1)  - 1.0 ) < 1e-3 and abs(np.sum(mp2) - 1.0 ) < 1e-3)
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

def I1(nu, mu):
    a, = np.shape(nu)
    F = lambda x, y:x * np.log( x * 1.0 / y )
    non_zero_idx_set = [i for i in xrange(a) if mu[i] !=0 and nu[i]!=0]

    # FIXME find better to make sure e is nonnegative
    e =  sum( F(nu[i], mu[i]) for i in non_zero_idx_set ) #  ele in non_zero_idx_set for both nu and mu should sum to 1 to make e nonnegative.
    return abs(e)

def quantize_state(x, nx, rg):
    minVal, maxVal = rg
    if minVal == maxVal:
        print '[warning] range size 0, rg: ', rg
        return x, [0]*len(x)

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

def get_dist_to_center(data, cluster, centerPt, DF):
    i = -1
    dis = []
    for x in data:
        i += 1
        cl = cluster[i]
        dis.append( DF( x, centerPt[cl] ) )

    return dis

def trans_data(flow):
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

    return sortedSrcIP, sortedFlowSize, sortedTime, sortedDur

        # show()

def f_hash(digit, level):
    '''This is just a hash function. to map a sequence to a unique number.
    The implemetation is: return digit[0] + digit[1] * level[0] + digit[2] * level[1] * level[0] ...
    '''
    # return digit[0] + digit[1] * level[0] + digit[2] * level[1] * level[0]
    value = digit[0]
    for i in xrange(len(digit)-1):
        value += digit[i+1] * reduce(operator.mul, level[0:i+1])
    return value

def get_feature_hash_list(F, Q):
    '''For each list of feature and corresponding quantized level.
    Get the hash value correspondingly'''
    return [ f_hash(f, Q) for f in zip(*F) ]

def model_based(q_fea_vec, fea_QN):
    '''estimate the transition probability. It has same input parameter with model_free.

    - q_fea_vec :q_fea_vec is a list of list containing all the quantized feature in a window. len(q_fea_vec)
               equals to the number of feature types. len(q_fea_vec[0]) equals to the number of flows in this
               window.
    - fea_QN : this is a list storing the quantized number for each feature.
    '''
    QLevelNum = reduce(operator.mul, fea_QN)
    P = np.zeros( (QLevelNum, QLevelNum) )
    fl = len(q_fea_vec[0])
    mp = np.zeros((QLevelNum, ))
    m_list = get_feature_hash_list(q_fea_vec, fea_QN)

    for i in xrange(fl-1):
        mp[m_list[i]] += 1
        P[m_list[i], m_list[i+1]] += 1
    mp[m_list[fl-1]] += 1

    P = P * 1.0 / (fl-1)
    mp = mp / fl
    return P, mp

def model_free(q_fea_vec, fea_QN):
    '''estimate the probability distribution for model free case. It has same input parameters with model_based

    - q_fea_vec :q_fea_vec is a list of list containing all the quantized feature in a window. len(q_fea_vec)
               equals to the number of feature types. len(q_fea_vec[0]) equals to the number of flows in this
               window.
    - fea_QN : this is a list storing the quantized number for each feature.
    '''
    QLevelNum = reduce(operator.mul, fea_QN)
    P = np.zeros( (QLevelNum, ) )
    fl = len(q_fea_vec[0])
    m_list = get_feature_hash_list(q_fea_vec, fea_QN)

    for i in range(fl):
        idx = m_list[i]
        try:
            P[idx] += 1
        except:
            import pdb; pdb.set_trace()
    P = P * 1.0 / fl
    assert(abs( np.sum(np.sum(P, 0)) - 1.0) < 0.01)
    return P


def vector_quantize_states(fea_vec , fea_QN, fea_range, quan_flag=None):
    '''Quantize a vector of numbers.

    - fea_vec : is a list of list containing all the features in a window. len(fea_vec)
               equals to the number of feature types. len(fea_vec[0]) equals to the number of flows in this
               window.
    - fea_QN : quantized number for each feature. len(feaQn) equals to the number of feature types.
    - fea_range : a list of two-digit tupe containing the range for each user. the
                 length for first diemension equals to the number of feature types.
                 the length of the second dimension is two.

    '''
    if not quan_flag: quan_flag = len(fea_QN) * [1]
    try:
        QS = lambda a, b, c, flag: quantize_state(a, b, c)[1] if flag else a
        res = [ QS(a, b, c, flag) for a, b, c, flag in zip(fea_vec , fea_QN, fea_range, quan_flag) ]
    except:
        import pdb;pdb.set_trace()
    return res

def get_all_pmf(fea_vec, fea_QN, fea_range,  quan_flag=None):
    '''This Function Support Multiple Features, get probability mass function

    - fea_vec : is a list of list containing all the features in a window. len(fea_vec)
               equals to the number of feature types. len(fea_vec[0]) equals to the number of flows in this
               window.
    - fea_QN : quantized number for each feature. len(feaQn) equals to the number of feature types.
    - fea_range : a list of two-digit tupe containing the range for each user. the
                 length for first diemension equals to the number of feature types.
                 the length of the second dimension is two.

    '''
    qFeaVec = vector_quantize_states(fea_vec, fea_QN, fea_range, quan_flag)
    # import pdb;pdb.set_trace()
    pmf = model_free(qFeaVec, fea_QN)
    Pmb, mpmb = model_based(qFeaVec, fea_QN)
    return pmf, Pmb, mpmb

def get_flow_rate(t, cluster):
    '''Get Estimation of Flow Rate For Each User input:

    - **t** : arrival time
    - **cluster** : cluster labels flows

    output is Estimated flow arrival rate for each time
    '''
    win = settings.FLOW_RATE_ESTIMATE_WINDOW
    fr = []
    for i in xrange(len(t)):
        idx = Find(t, t[i] - win)
        if idx == -1: idx = 0
        c = cluster[i]
        fr.append( cluster[idx:i].count(c) )

    return fr


def get_feature(fName, clusterNum, cutHead=True):
    '''Get feature by parsing the data file.

    - fName : is the name for the flow file generated by fs-simulator
    - clusterNum : the number of cluster in K-means clustering.
    - cutHead : if we use estimated value of flow rate. The beginning part of
                the estimation will be not accurate. cutHead flag indicates
                whether we need to delete beginning part of the data or not.

    '''
    flow = ParseData(fName);
    srcIPVec, flowSize, t, dur = trans_data(flow)

    # import pdb;pdb.set_trace()
    cluster, centerPt = KMeans(srcIPVec, clusterNum, DF)
    distToCenter = get_dist_to_center(srcIPVec, cluster, centerPt, DF)
    flowRate = get_flow_rate(t, cluster)

    if cutHead:
        ns = Find(t, min(t) + settings.FLOW_RATE_ESTIMATE_WINDOW)
        srcIPVec = srcIPVec[ns:]
        flowSize = flowSize[ns:]
        t = t[ns:]
        dur = dur[ns:]
        flowRate = flowRate[ns:]

    exec settings.LOAD_FEATURE

    quanFlag = ( len(feaVec) - 1 ) * [1] + [0]
    feaRange = get_range(feaVec)
    return feaVec, feaRange, quanFlag, t, centerPt

# def gen_norminal_pdf(fName, clusterNum, ND, NF, dumpFlag =False):
def gen_norminal_pdf(f_name, fea_QN, dump_flag =False):
    '''This function is to generate the nominal probability densition function for
    both model free and model free case.

    - f_name : is the name for the flow file generated by fs-simulator
    - fea_QN : quantized number for each feature. len(feaQn) equals to the number of feature types.
    - dump_flag : indicate whether dump the generated nominal pdf to a data file.

    '''

    '''Generate the nominal probability mass function'''
    feaVec, feaRange, quanFlag, t, centerPt = get_feature(f_name, fea_QN[-1])

    # ns = 0 # normal start
    ns = Find(t, min(t) + settings.FLOW_RATE_ESTIMATE_WINDOW)
    ne = Find(t, min(t) + settings.ANOMALY_TIME[0] - 10) + 1
    n_feaVec = SL(feaVec, ns, ne)

    pmf, Pmb, mpmb = get_all_pmf(n_feaVec, fea_QN, feaRange,  quanFlag)

    data = pmf, Pmb, mpmb, feaRange
    if dump_flag:
        pickle.dump( data, open(NominalPDFFile, 'w') )
    return pmf, Pmb, mpmb, feaVec, fea_QN, feaRange,  quanFlag, t, centerPt

def SL(data, st, ed):
    return [d[st:ed] for d in data]

def get_range(data):
    return [ (min(x), max(x)) for x in data ]

if __name__ == "__main__":
    Detector.AnomalyDetector.compare(sys.argv[1])
