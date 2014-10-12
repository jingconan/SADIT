""" Use Heuristic Method to Identify PL

"""
from __future__ import print_function, division, absolute_import
try:
     range=xrange
except NameError:
     pass

import numpy as np
def feasible(x, D, lamb, k):
    """  check whether the selection is a feasible solution

    Parameters
    ---------------
    Returns
    --------------
    """
    for j in range(k+1):
        if min( (D[:, j] - lamb).ravel() * x ) >= 0:
            return False
    return True

def improve(x, D, lamb, k):
    for i in range(len(x)):
        if x[i] == 0:
            continue
        x[i] = 0
        if feasible(x, D, lamb, k):
            return True
        x[i] = 1
    return False

def PL_identify(D, lamb):
    """  Idenify the Probability Law (PL)

    Parameters
    ---------------
    D : mxn numpy array matrix
        D_ij is the entropy value calculated using candidate PL i and data in
        window j.
    lamb : float
        detection threshold

    Returns
    --------------
    x : None or list
        if there is no feasible solution, return None, otherwise
        return a list of 0-1 value.

    Examples
    ----------------
    >>> import numpy as np
    >>> D = np.array([[0.2, 0.3], [0.4, 1.4]])
    >>> PL_identify(D, 0.5)
    [1, 0]
    """

    m, n = D.shape
    x = [0] * m
    for k in range(n):
        if not feasible(x, D, lamb, k):
            improvedFlag = False
            for i in (D[:, k] < lamb).nonzero()[0]:
                x[i] = 1
                if improve(x, D, lamb, k):
                    improvedFlag = True
                    break
                x[i] = 0
            if not improvedFlag:
                idx = np.argmin(D[:, k])
                if D[idx, k] > lamb:
                    return None
                x[idx] = 1

            # idx = np.argmin(D[:, k])
            # x[idx] = 1
    # import ipdb;ipdb.set_trace()
    return x
if __name__ == "__main__":
    import doctest
    doctest.testmod()
