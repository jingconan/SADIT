#!/usr/bin/env python
"""
the goal of this file is to provide a lib of joint probability transformation.
During the transformation, the marginal distribution is unchanged.
now only consider the 2-d case.
"""
def joint_prob_trans(A, d):
    """
    - A is the reference joint distribution,
    - d is the degree of the change.
    """
    # P_star = max_entropy(A)
    # return d * P_star + (1-d) * A

try:
    from numpy import array, ones, dot, vstack
    from numpy.ma import log
    import numpy as np
except ImportError:
    print 'numpy cannot be imported'

def H(x, y):
    """Cross Entropy Function"""
    x = x.reshape(-1)
    y = y.reshape(-1)
    return dot(x, log(x/y))

def eq_cons(x, A, epsilon):
    t, _ = A.shape
    v1 = ones([t, 1])
    P = x.reshape(A.shape)
    # import pdb;pdb.set_trace()
    r1 = dot(P, v1) - dot(A, v1)
    r2 = dot(P.T, v1) - dot(A.T, v1)
    r3 = H(P, A) - epsilon
    return vstack([r1, r2, r3.reshape(-1, 1)]).reshape(-1,)

try:
   from scipy.optimize import fmin_slsqp
except:
   print 'no scipy'

def get_diff_jpdf_with_ini(A, P0, epsilon):
    """Get joint distribution with same marginal distribution with A
    and cross entropy with A is epsilon."""
    t, _ = A.shape
    obj_func = lambda x: dot(x, log(x))
    f_eqcons = lambda x: eq_cons(x, A, epsilon)
    out = fmin_slsqp(func = obj_func,
            x0 = P0.reshape(-1,),
            f_eqcons = f_eqcons,
            bounds = [[0, 1]] *t*t,
            )
    return  out.reshape(A.shape)

def get_diff_jpdf(A, epsilon):
    return get_diff_jpdf_with_ini(A, A, epsilon)


def test_p2():
    print '-' * 40
    A = array([
        [0.1, 0.1, 0.1],
        [0.1, 0.1, 0.1],
        [0.1, 0.1, 0.2],
        ])
    out = get_diff_jpdf_with_ini(A, A, 0.7)
    print 'out, ', out
    print 'sum, ', np.sum(out)
    print '-' * 40

if __name__ == "__main__":
    test_p2()


