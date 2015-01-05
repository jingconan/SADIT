from __future__ import print_function, division, absolute_import
import pyOpt
import math

range = xrange
def PL_identify(D, lamb, T, ini_sol):
    """  Idenify the Probability Law (PL)

    Parameters
    ---------------
    D : mxn matrix
        D_ij is the entropy value calculated using candidate PL i and data in
        window j
    lamb : float
        detection threshold
    T : float
        parameter in logistic function. The unit step function is approximated
        by L(x) = 1 / ( 1 + exp(-x / T))
    ini_sol : mxn matrix
        initial solution

    Returns
    --------------
    """

    L = lambda x: 1.0 / ( 1 + math.exp(-1.0 * x / T))
    # m, n = D.shape
    m = len(D)
    n = len(D[0])
    def objfunc(x):
        f = sum(L(sum(x[(n * i):(n * (i + 1))])) for i in range(m))
        # print('f', f)
        cn = (m * n + n)
        g = [0.0] * cn
        for j in range(n):
            g[j] = -1 * sum(x[i * n + j] for i in range(m)) + 1

        for i in range(m):
            for j in range(n):
                g[n + i * n + j] = D[i][j] * x[i * n + j] - lamb

        fail = 0
        # print('g, ', g)
        return f, g, fail

    opt_prob = pyOpt.Optimization("PL Identification Problem", objfunc)
    opt_prob.addObj('f')
    for i in range(m):
        for j in range(n):
            opt_prob.addVar('x%d_%d'%(i,j), 'c', lower=0.0,
                    upper=1.0, value = ini_sol[i][j])
            # opt_prob.addVar('x%d%d'%(i,j), 'i', lower=0,
                    # upper=1, value=0)
    opt_prob.addConGroup('eq', n, type='e')
    opt_prob.addConGroup('ineq', m * n, type='i')
    print('opt_prob: ', opt_prob)
    # return
    slsqp = pyOpt.SLSQP()
    [fstr, xstr, inform] = slsqp(opt_prob, sens_type='FD')

    # alg  = pyOpt.ALGENCAN ()
    # [fstr, xstr, inform] = alg(opt_prob)

    print('fstr', fstr)
    print('inform', inform)
    print('xstr', xstr)

    print(opt_prob.solution(0))

# D = [[0.2, 0.3],
#     [0.4, 1.4]]
# ini_sol = [
#         [1, 0],
#         [1, 0.5]
#         ]
# PL_identify(D, 0.5, 1, ini_sol)
