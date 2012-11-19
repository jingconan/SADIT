#!/usr/bin/env python
"""A library of utility function that will be used by detectors
"""
### -- Created at [2012-03-01 14:55:21]
### -- [2012-03-01 17:13:27] support multi feature
### -- [2012-03-01 22:05:29] get_flow_rate, test with flowSize, dur, flowRate
import sys
sys.path.append("..")
from util import np, Counter
import operator
import math
def shannon_entropy(prob):
    """calculate shannon entropy
    """
    return sum(-1 * p * math.log(p) for p in prob if (p > 0 and p < 1))

# The Distance Function
DF = lambda x,y:abs(x[0]-y[0]) * (256**3) + abs(x[1]-y[1]) * (256 **2) + abs(x[2]-y[2]) * 256 + abs(x[3]-y[3])
import copy
def I2(P1, mp1, P2, mp2):
    # assert( abs(np.sum(mp1)  - 1.0 ) < 1e-3 and abs(np.sum(mp2) - 1.0 ) < 1e-3)
    # a, b = np.shape(P1)
    a = len(P1)
    b = len(P1[0])
    P1Con = copy.deepcopy(P1)
    P2Con = copy.deepcopy(P2)
    for i in range(a):
        for j in range(b):
            if mp1[i] != 0:
                # P1Con[i, j] /= mp1[i]
                P1Con[i][j] /= mp1[i]
            if mp2[i] != 0:
                P2Con[i][j] /= mp2[i]
    # Compute Expectation of Each Relative Entropy
    y = 0
    for i in range(a):
        # y += mp1[i] * I1(P1Con[i, :], P2Con[i, :])
        y += mp1[i] * I1(P1Con[i], P2Con[i])
    return y

from math import log
def I1(nu, mu):
    # a, = np.shape(nu)
    a = len(nu)
    # F = lambda x, y:x * np.log( x * 1.0 / y )
    F = lambda x, y:x * log( x * 1.0 / y )
    non_zero_idx_set = [i for i in xrange(a) if mu[i] !=0 and nu[i]!=0]

    # FIXME find better to make sure e is nonnegative
    e =  sum( F(nu[i], mu[i]) for i in non_zero_idx_set ) #  ele in non_zero_idx_set for both nu and mu should sum to 1 to make e nonnegative.
    return abs(e)

def quantize_state(x, nx, rg):
    """quantize state

    Input:
        - *x* is a list of elements that need to be quantized
        - *nx* is the quantized level. the quantized value can be [0, ...,
          nx-1]
        - *rg* is the range for the feature
    Output:
        - quantized level
    """

    minVal, maxVal = rg
    if minVal == maxVal:
        print '[warning] range size 0, rg: ', rg
        return x, [0]*len(x)

    stepSize = (maxVal - minVal) * 1.0 / (nx - 1 )
    g = []
    for ele in x:
        seq = int( (ele - minVal ) / stepSize + 0.5)
        if seq >= nx-1:
            seq = nx -1
        g.append(seq)
    # return res, g
    return g

def np_quantize_state(x, nx, rg):
    """fast quantize_state that use numpy library
    """
    x = np.array(x)
    minVal, maxVal = rg
    if minVal == maxVal:
        print('[warning] range size 0, rg: ', rg)
        return x, [0]*len(x)

    stepSize = (maxVal - minVal) * 1.0 / (nx - 1 )
    return np.round( (x - minVal) / stepSize)

if np:
    quantize_state = np_quantize_state

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

# def f_hash(digit, level):
#     '''This is just a hash function. to map a sequence to a unique number.
#     The implemetation is: return digit[0] + digit[1] * level[0] + digit[2] * level[1] * level[0] ...
#     '''
#     if len(digit) == 3: # just try to make it faster for special case
#         return digit[0] + digit[1] * level[0] + digit[2] * level[1] * level[0]
#     else:
#         value = digit[0]
#         basis = [1]
#         for i in xrange( len(digit) - 1 ):
#             basis.append( basis[-1] * level[i] )
#         value = sum( d*b for d, b zip(digit, basis) )

        # for i in xrange(len(digit)-1):
            # value += digit[i+1] * reduce(operator.mul, level[0:i+1])
        # return value

basis_cache = dict() # ugly global cache of basis to accelerate the program
def get_feature_hash_list(F, level):
    ''' For each list of feature and corresponding quantized level.
    Get the hash value correspondingly
    '''
    # import pdb;pdb.set_trace()
    if isinstance(level, list):
        level = tuple(level)
    basis = basis_cache.get(level, None)
    if basis is None:
        basis = [1]
        for i in xrange( len(level) - 1 ):
            basis.append( basis[-1] * level[i] )

    return [ sum( d*b for d, b in zip(digits, basis) ) for digits in zip(*F) ]

from util import zeros
def model_based_deprec(q_fea_vec, fea_QN):
    '''estimate the transition probability. It has same input parameter with model_free.

    - q_fea_vec :q_fea_vec is a list of list containing all the quantized feature in a window. len(q_fea_vec)
               equals to the number of feature types. len(q_fea_vec[0]) equals to the number of flows in this
               window.
    - fea_QN : this is a list storing the quantized number for each feature.
    '''
    QLevelNum = reduce(operator.mul, fea_QN)
    # P = np.zeros( (QLevelNum, QLevelNum) )
    P = zeros( (QLevelNum, QLevelNum) )
    fl = len(q_fea_vec[0])
    mp = zeros((QLevelNum, ))
    m_list = get_feature_hash_list(q_fea_vec, fea_QN)

    for i in xrange(fl-1):
        mp[ int(m_list[i]) ] += 1
        P[ int(m_list[i]) ][ int(m_list[i+1]) ] += 1
    mp[ int(m_list[fl-1]) ] += 1

    # P = P * 1.0 / (fl-1)
    for i in xrange(len(P)):
        for j in xrange(len(P[0])):
            P[i][j] = P[i][j] * 1.0 / (fl -1)
    # mp = mp / fl
    mp = [v*1.0/fl for v in mp]
    return P, mp

import itertools

def model_based(q_fea_vec, fea_QN):
    '''estimate the transition probability. It has same input parameter with model_free.

    - q_fea_vec :q_fea_vec is a list of list containing all the quantized feature in a window. len(q_fea_vec)
               equals to the number of feature types. len(q_fea_vec[0]) equals to the number of flows in this
               window.
    - fea_QN : this is a list storing the quantized number for each feature.
    '''
    QLevelNum = reduce(operator.mul, fea_QN)
    m_list = get_feature_hash_list(q_fea_vec, fea_QN)
    mp = zeros((QLevelNum, ))
    ct = Counter(m_list)
    total = len(m_list)
    for k, v in ct.iteritems():
        mp[int(k)] = v * 1.0 / total

    P = zeros( (QLevelNum, QLevelNum) )
    tran_pairs = itertools.izip(m_list[:-1], m_list[1:])
    tran_ct = Counter(tran_pairs)
    total_tran = total - 1
    for (i, j), freq in tran_ct.iteritems():
        P[int(i)][int(j)] = freq * 1.0 / total_tran

    return P, mp

def model_free_deprec(q_fea_vec, fea_QN):
    '''estimate the probability distribution for model free case. It has same input parameters with model_based

    - q_fea_vec :q_fea_vec is a list of list containing all the quantized feature in a window. len(q_fea_vec)
               equals to the number of feature types. len(q_fea_vec[0]) equals to the number of flows in this
               window.
    - fea_QN : this is a list storing the quantized number for each feature.
    '''
    QLevelNum = reduce(operator.mul, fea_QN)
    # P = np.zeros( (QLevelNum, ) )
    P = [0] * QLevelNum
    fl = len(q_fea_vec[0])
    m_list = get_feature_hash_list(q_fea_vec, fea_QN)

    for i in range(fl):
        idx = int(m_list[i])
        try:
            P[idx] += 1
        except Exception as e:
            print e
            import pdb; pdb.set_trace()
    # P = P * 1.0 / fl
    P = [v*1.0/fl for v in P]
    assert(abs( sum(P) - 1.0) < 0.01)
    # assert(abs( np.sum(np.sum(P, 0)) - 1.0) < 0.01)
    return P

def model_free(q_fea_vec, fea_QN):
    '''estimate the probability distribution for model free case. It has same input parameters with model_based

    - q_fea_vec :q_fea_vec is a list of list containing all the quantized feature in a window. len(q_fea_vec)
               equals to the number of feature types. len(q_fea_vec[0]) equals to the number of flows in this
               window.
    - fea_QN : this is a list storing the quantized number for each feature.
    '''
    # import pdb;pdb.set_trace()
    QLevelNum = reduce(operator.mul, fea_QN)
    P = [0] * QLevelNum
    # fl = len(q_fea_vec[0])
    m_list = get_feature_hash_list(q_fea_vec, fea_QN)

    ct = Counter(m_list)
    total = sum(ct.values())
    try:
        for k, v in ct.iteritems():
            P[int(k)] = v * 1.0 / total
    except:
        import pdb;pdb.set_trace()
    return P

if not Counter :
    model_free = model_free_deprec
    model_based = model_based_deprec

def vector_quantize_states(fea_vec , fea_QN, fea_range, quan_flag=None):
    '''Quantize a vector of numbers.

    - fea_vec : is a list of list containing all the features in a window. len(fea_vec)
               equals to the number of feature types. len(fea_vec[0]) equals to the number of flows in this
               window.
    - fea_QN : quantized number for each feature. len(feaQn) equals to the number of feature types.
    - fea_range : a list of two-digit tupe containing the range for each feature. the
                 length for first diemension equals to the number of feature types.
                 the length of the second dimension is two.

    '''
    if not quan_flag: quan_flag = len(fea_QN) * [1]
    QS = lambda a, b, c, flag: quantize_state(a, b, c) if flag else a
    res = [ QS(a, b, c, flag) for a, b, c, flag in itertools.izip(fea_vec , fea_QN, fea_range, quan_flag) ]
    return res

def SL(data, st, ed):
    return [d[st:ed] for d in data]

def get_range(data):
    return [ (min(x), max(x)) for x in data ]
