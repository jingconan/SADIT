#!/usr/bin/env python
"""A library of utility function that will be used by detectors
"""
from sadit.util import np, Counter
import operator
import itertools

def adjust_pv(prob, eps):
    """ adjust probability vector so that each value >= eps

    Parameters
    ---------------
    prob : list or tuple
        probability vector
    eps : float
        threshold

    Returns
    --------------
    prob : list
        adjusted probability vector

    Examples
    -------------------
    >>> adjust_pv([0, 0, 1], 0.01)
    [0.01, 0.01, 0.98]

    """
    assert(abs(sum(prob) - 1) < 1e-3)
    a = len(prob)
    zei = [i for i, v in zip(xrange(a), prob) if abs(v) < eps] # zero element indices
    if a == len(zei): # all elements are zero
        return [eps] * a
    zei_sum = sum(prob[i] for i in zei)
    adjustment = (eps * len(zei) - zei_sum) * 1.0 / (a - len(zei))
    prob2 = [v - adjustment for v in prob]
    for idx in zei:
        prob2[idx] = eps
    if min(prob2) < 0:
        print '[warning] EPS is too large in adjust_pv'
        import pdb;pdb.set_trace()
        # return adjust_pv(prob2, eps / 2.0)
    return prob2


DF = lambda x,y:abs(x[0]-y[0]) * (256**3) + abs(x[1]-y[1]) * (256 **2) + abs(x[2]-y[2]) * 256 + abs(x[3]-y[3])

EPS = 1e-20
from math import log
def I1(nu, mu):
    """  Calculate the empirical measure of two probability vector nu and mu

    Parameters
    ---------------
    nu, mu : list or tuple
        two probability vector

    Returns
    --------------
    res : float
        the cross entropy

    Notes
    -------------
    The cross-entropy of probability vector **nu** with respect to **mu** is
    defined as

    .. math::

        H(nu|mu) = \sum_i  nu(i) \log(nu(i)/mu(i)))

    One problem that needs to be addressed is that mu may contains 0 element.

    Examples
    --------------
    >>> print I1([0.3, 0.7, 0, 0], [0, 0, 0.3, 0.7])
    45.4408375578

    """
    assert(len(nu) == len(mu))
    a = len(nu)

    mu = adjust_pv(mu, EPS)
    nu = adjust_pv(nu, EPS)

    H = lambda x, y:x * log( x * 1.0 / y )
    return sum(H(a, b) for a, b in zip(nu, mu))

def adjust_mat(P):
    shape = P.shape
    return np.array(adjust_pv(P.ravel(), EPS)).reshape(shape)

def I2(J1, pi1, J2, pi2):
    """  calculate cross entropy for model-based empirical measure

    Empirical Measure (EM) consists of 1. state probability, 2 joint
    probability.

    Parameters
    ---------------
    mp1, mp2 : list or tuple
        state probability for empirical measure 1 and 2, respectively

    P1, P2 : list of list
        for empirical measure 1 and 2, respectively
        the sum of all elements in P1 should be one

    Returns
    --------------
    y : float
        cross entropy

    Notes
    --------------
    Need to deal with the case when transition probability or state
    probability has zero element.

    We first need to caculate the stochastic matrix
    P(i, j) = J(i, j) / pi[i]

    Examples
    ----------------
    >>> J1 = [[0.2, 0.1], [0.3, 0.4]]
    >>> J2 = [[0.3, 0.1], [0.2, 0.4]]
    >>> print I2(J1, None,  J2, None)
    0.0189456566673
    """
    J1 = np.array(J1) #FIXME use np here
    J2 = np.array(J2)
    n, _ = J1.shape
    assert(n == _)

    J1 = adjust_mat(J1)
    J2 = adjust_mat(J2)

    pi1 = np.sum(J1, axis=1)
    P1Con = J1 / np.dot( pi1.reshape(-1, 1), np.ones((1, n)) )

    pi2 = np.sum(J2, axis=1)
    P2Con = J2 / np.dot( pi2.reshape(-1, 1), np.ones((1, n)) )

    # Compute Expectation of Each Relative Entropy
    y = 0
    for i in range(n):
        # y += mp1[i] * I1(P1Con[i, :], P2Con[i, :])
        y += pi1[i] * I1(P1Con[i], P2Con[i])

    if y < 0: import ipdb;ipdb.set_trace()
    return y

# def quantize_state(x, nx, rg):
#     minVal, maxVal = rg
#     if minVal == maxVal:
#         print '[warning] range size 0, rg: ', rg
#         return x, [0]*len(x)

#     stepSize = (maxVal - minVal) * 1.0 / (nx - 1 )
#     g = []
#     for ele in x:
#         seq = int( (ele - minVal ) / stepSize + 0.5)
#         if seq >= nx-1:
#             seq = nx -1
#         g.append(seq)
#     return g

def quantize_state(x, nx, rg):
    """ fast quantize_state that use numpy library

    Parameters
    ------------------
    x : is a list of elements that need to be quantized
    nx : is the quantized level. the quantized value can be [0, ..., nx-1]
    rg : is the range for the feature

    Returns
    ------------------
    quan : quantized level
    """
    x = np.array(x)
    minVal, maxVal = rg
    if minVal == maxVal:
        print('[warning] range size 0, rg: ', rg)
        return x, [0]*len(x)

    stepSize = (maxVal - minVal) * 1.0 / nx
    quan = np.floor( (x - minVal) / stepSize )
    quan[quan == nx] = nx-1 # Fix for the largest value.
    return quan

# if np:
    # quantize_state = np_quantize_state

# def get_dist_to_center(data, cluster, centerPt, DF):
#     i = -1
#     dis = []
#     for x in data:
#         i += 1
#         cl = cluster[i]
#         dis.append( DF( x, centerPt[cl] ) )

#     return dis

# def trans_data(flow):
#     uniqueIP = set()
#     srcIP = []
#     srcIPVec = []
#     flowSize = []
#     time = []
#     endTime = []
#     for f in flow:
#         uniqueIP.add( f['srcIP'] )
#         srcIP.append( f['srcIP'] )
#         srcIPVec.append( f['srcIPVec'] )
#         flowSize.append( f['flowSize'] )
#         time.append( f['t'] )
#         endTime.append( f['endT'] )

#     sortIdx = np.argsort(time)
#     sortedSrcIP = []
#     sortedFlowSize = []
#     sortedTime = []
#     sortedDur = []
#     for idx in sortIdx:
#         sortedSrcIP.append(srcIPVec[idx])
#         sortedFlowSize.append(flowSize[idx])
#         sortedTime.append(time[idx])
#         sortedDur.append( endTime[idx] - time[idx] )

#     return sortedSrcIP, sortedFlowSize, sortedTime, sortedDur

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

# basis_cache = dict() # ugly global cache of basis to accelerate the program
# def get_feature_hash_list_old(F, level):
#     ''' For each list of feature and corresponding quantized level.
#     Get the hash value correspondingly
#     '''
#     import pdb;pdb.set_trace()
#     if isinstance(level, list):
#         level = tuple(level)
#     basis = basis_cache.get(level, None)
#     if basis is None:
#         basis = [1]
#         for i in xrange( len(level) - 1 ):
#             basis.append( basis[-1] * level[i] )

#     return [ sum( d*b for d, b in zip(digits, basis) ) for digits in zip(*F) ]

cache_ = dict()
def get_feature_hash_list(F, level):
    """ calculate the

    Parameters:
    ---------------
    F : list


    Returns:
    --------------
    Examples
    --------------
    """
    # FIXME Add doctest here
    level = tuple(level)
    try:
        return [cache_[level][vec] for vec in itertools.izip(*F)]
    except KeyError:
        # import ipdb;ipdb.set_trace()
        basis = [1]
        cache_[level] = dict()
        for i in xrange( len(level) - 1 ):
            basis.append( basis[-1] * level[i] )
        for digits in itertools.product(*[range(d) for d in level]):
            cache_[level][digits] = sum( d*b for d, b in zip(digits, basis) )

        return get_feature_hash_list(F, level)


from sadit.util import zeros
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


def model_based(q_fea_vec, fea_QN):
    """ Estimate the transition probability.

    It has same input parameter with model_free.

    Parameters
    -------------
    q_fea_vec : list of list
        q_fea_vec is a list of list containing all the quantized feature in a
        window. len(q_fea_vec) equals to the number of feature types.
        len(q_fea_vec[0]) equals to the number of flows in this window.
    fea_QN : list
        this is a list storing the quantized number for each feature.
    """
    if len(q_fea_vec[0]) < 2:
        # print('these is only one sample in the range, cannot calculate ' \
                # 'model based emperical measure')
        return None, None

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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
