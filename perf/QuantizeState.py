from __future__ import print_function, division
@profile
def quantize_state(x, nx, rg):
    """quantize state

    Input:
        - *x* is a list of elements that need to be quantized
        - *nx* is the quantized level. the quantized value can be [0, ...,
          nx-1]
        - *rg* is the range for the feature
    Output:
        - quantized value
        - quantized level
    """

    minVal, maxVal = rg
    if minVal == maxVal:
        print('[warning] range size 0, rg: ', rg)
        return x, [0]*len(x)

    stepSize = (maxVal - minVal) * 1.0 / (nx - 1 )
    res = []
    g = []
    for ele in x:
        seq = int( (ele - minVal ) / stepSize + 0.5)
        if seq >= nx-1:
            seq = nx -1
        y = minVal +  seq * stepSize
        res.append(y)
        g.append(seq)
    return res, g

import numpy as np
@profile
def np_quantize_state(x, nx, rg):
    x = np.array(x)
    minVal, maxVal = rg
    if minVal == maxVal:
        print('[warning] range size 0, rg: ', rg)
        return x, [0]*len(x)

    stepSize = (maxVal - minVal) * 1.0 / (nx - 1 )
    return np.round((x - minVal) / stepSize)



import random
for i in xrange(10000):
    x = [random.random() for i in xrange(100)]
    _, res = quantize_state(x, 2, [0, 1])
    res2 = np_quantize_state(x, 2, [0, 1])
    # import pdb;pdb.set_trace()
    assert(all(res2 == np.array(res)))

