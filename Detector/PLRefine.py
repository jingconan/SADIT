from __future__ import print_function, division, absolute_import
import numpy as np

def GreedySolve(A, gam, cv):
    m, n = A.shape
    x = np.zeros((n,))
    C = set([])
    while len(C) < m:
        S = np.zeros((n,))
        for j in xrange(n):
            if x[j] == 1:
                continue
            dC = set(xrange(m)) - C
            S[j] = sum(A[i,j] for i in dC) / (gam * cv[j])
        j_plus = np.argmax(S)
        x[j_plus] = 1
        C = C | set(i for i in dC if A[i,j_plus])
    return x

def HeuristicRefinePL(D, lamb, gam0, r, epsi):
    m, n = D.shape
    A = (D < lamb)
    if len(np.sum(A, axis=1).nonzero()[0]) != m:
        return None
    cv = np.zeros((n,))
    for j in xrange(n):
        N_j = np.nonzero(A[:, j])[0]
        D_j = np.diff(N_j)
        cv[j] = np.std(D_j) / np.mean(D_j)
    print('cv', cv)

    x = []
    # gam = 50
    # r = 0.8
    gam = gam0
    while len(x) <= 1 or not np.array_equal(x[-1], x[-2]) or gam > epsi:
        gam = r * gam
        print('gam', gam)
        xk = GreedySolve(A, gam, cv)
        x.append(xk)
    x = np.array(x)
    sumx = np.sum(x, axis=1)
    print('sumx', sumx)
    j_star = np.argmin(sumx)
    return x[j_star]
