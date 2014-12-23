#!/usr/bin/env python
""" A library of utility function that will be used by detectors
"""
from __future__ import print_function, division, absolute_import
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
        print( '[warning] EPS is too large in adjust_pv')
        import pdb;pdb.set_trace()
        # return adjust_pv(prob2, eps / 2.0)
    return prob2

def adjust_mat(P):
    """  Adjust the joint distribution matrix P so that the minium value is >= EPS

    Parameters
    ---------------
    P : np.array
        joint distribution matrix P

    Returns
    --------------
    ret : np.array
        ajusted matrix.

    Notes
    --------------
    the sum of all element in P is 1.

    Examples
    -------------------
    >>> adjust_mat(np.array([[0, 0.5], [0, 0.5]]))
    array([[  1.00000000e-20,   5.00000000e-01],
           [  1.00000000e-20,   5.00000000e-01]])

    """
    shape = P.shape
    return np.array(adjust_pv(P.ravel(), EPS)).reshape(shape)

# DF = lambda x,y:abs(x[0]-y[0]) * (256**3) + abs(x[1]-y[1]) * (256 **2) + abs(x[2]-y[2]) * 256 + abs(x[3]-y[3])
from sadit.util import DF

EPS = 1e-50
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

# def I2(J1, pi1, J2, pi2):
def I2(J1, J2):
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
    >>> print I2(J1, J2)
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


def model_based(q_fea_vec, fea_QN):
    """ estimate the transition probability. It has same input parameter with model_free.

    q_fea_vec : list of list
        q_fea_vec is a list of list containing all the quantized feature in a
        window. len(q_fea_vec) equals to the number of feature types.
        len(q_fea_vec[0]) equals to the number of flows in this window.
    fea_QN : list of int
        this is a list storing the quantized number for each feature.
    """
    QLevelNum = reduce(operator.mul, fea_QN)
    P = np.zeros( (QLevelNum, QLevelNum) )
    fl = len(q_fea_vec[0])
    m_list = get_feature_hash_list(q_fea_vec, fea_QN)
    m_list = [int(v) for v in m_list]

    for i in xrange(fl-1):
        P[ m_list[i] ][ m_list[i+1] ] += 1
    P /= (fl - 1 )
    # return P, None
    return P

def model_free(q_fea_vec, fea_QN):
    """ estimate the probability distribution for model free case. It has same input parameters with model_based

    q_fea_vec : list of list
        q_fea_vec is a list of list containing all the quantized feature in a
        window. len(q_fea_vec) equals to the number of feature types.
        len(q_fea_vec[0]) equals to the number of flows in this window.
    fea_QN : list of int
        this is a list storing the quantized number for each feature.
    """
    QLevelNum = reduce(operator.mul, fea_QN)
    P = np.zeros( (QLevelNum, ) )
    fl = len(q_fea_vec[0])
    m_list = get_feature_hash_list(q_fea_vec, fea_QN)
    m_list = [int(v) for v in m_list]

    for v in m_list:
        P[v] += 1
    P /= fl
    assert(abs( sum(P) - 1.0) < 0.01)
    return P

def vector_quantize_states(fea_vec, fea_QN, fea_range, quan_flag=None):
    """ Quantize a vector of numbers.

    Parameters
    ---------------------
    fea_vec : a list of list
        containing all the features in a window. len(fea_vec) equals to
        the number of feature types. len(fea_vec[0]) equals to the number
        of flows in this window.
    fea_QN : list of int
        quantized number for each feature. len(feaQn) equals to the number of feature types.
    fea_range : a list of two-digit tupe
        containing the range for each feature. the length for first diemension
        equals to the number of feature types.  the length of the second
        dimension is two.

    """
    if not quan_flag: quan_flag = len(fea_QN) * [1]
    QS = lambda a, b, c, flag: quantize_state(a, b, c) if flag else a
    res = [ QS(a, b, c, flag) for a, b, c, flag in itertools.izip(fea_vec , fea_QN, fea_range, quan_flag) ]
    return res

def SL(data, st, ed):
    return [d[st:ed] for d in data]



if __name__ == "__main__":
    import doctest
    doctest.testmod()
