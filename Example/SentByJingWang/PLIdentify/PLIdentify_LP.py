from __future__ import print_function, division, absolute_import
import pyOpt

range = xrange
def PL_identify(D, lamb, ini_sol, alg_name='SLSQP'):
    """  Idenify the Probability Law (PL)

    Parameters
    ---------------
    D : mxn matrix
        D_ij is the entropy value calculated using candidate PL i and data in
        window j.
    lamb : float
        detection threshold
    ini_sol : list with m elements
        initial solution
    alg_name : str {'SLSQP', 'ALGENCAN'}
        algorithm name

    Returns
    --------------

    Examples
    ----------------
    >>> D = [[0.2, 0.3], [0.4, 1.4]]
    >>> ini_sol = [1, 1]
    >>> fstr, xstr, inform, opt_prob = PL_identify(D, 0.5, ini_sol, 'SLSQP')
    >>> print('opt_prob', opt_prob)
    >>> print('inform', inform)
    >>> print('xstr', xstr)
    >>> print('fstr', fstr)
    """

    m = len(D)
    n = len(D[0])
    def objfunc(x):
        f = sum(x)
        cn = n
        g = [0.0] * cn
        for j in range(n):
            g[j] = (D[i][j] - lamb) * x[j] + 0.01

        fail = 0
        return f, g, fail

    opt_prob = pyOpt.Optimization("PL Identification Problem", objfunc)
    opt_prob.addObj('f')
    for i in range(m):
        # opt_prob.addVar('x%d'%(i), 'c', lower=0.0,
                # upper=1.0, value = ini_sol[i])
        opt_prob.addVar('x%d'%(i), 'c', lower=0.0,
                upper=1.0, value = ini_sol[i])

        # opt_prob.addVar('x%d'%(i), 'i', lower=0.0,
                # upper=1.0, value = ini_sol[i])
    opt_prob.addConGroup('ineq', n, type='i')

    alg = getattr(pyOpt, alg_name)()
    [fstr, xstr, inform] = alg(opt_prob)
    return fstr, xstr, inform, opt_prob

if __name__ == "__main__":
    # import doctest
    # doctest.testmod()

    D = [[0.2, 0.3], [0.4, 0.2]]
    ini_sol = [1, 1]
    x = PL_identify(D, 0.2, ini_sol, 'SLSQP')
    print('x', x)
