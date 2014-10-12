from __future__ import print_function, division, absolute_import
import numpy as np
from PLIdentify import PL_identify
import cPickle as pk

data = pk.load(open('./dump_robust.txt', 'r'))
I_rec = data['I_rec']
# import ipdb;ipdb.set_trace()
n = len(I_rec) # window size
m = I_rec[0].shape[0] # no. of PLs
D = np.zeros((m, n))
for j in xrange(n):
    for i in xrange(m):
        D[i, j] = I_rec[j][i, 0]

lamb = 1.5
x = PL_identify(D, lamb)
if x is None:
    print('No feasible selection')
    import sys
    sys.exit(0)
print('x, ', x)
select_D = D[np.nonzero(x)[0], :]
org_entro = np.min(D, axis=0)
select_entro = np.min(select_D, axis=0)
import matplotlib.pyplot as plt
plt.subplot(311)
plt.plot(D.T)
plt.subplot(312)
plt.plot(select_D.T)
plt.subplot(313)
plt.plot(org_entro, 'r-+')
plt.plot(select_entro, 'b-*')
print('select [%d] PLs out of [%d] PLs'%(sum(x), len(x)))
plt.legend(['orginal', 'selected'])
plt.show()
import ipdb;ipdb.set_trace()
