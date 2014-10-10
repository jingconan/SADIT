from __future__ import print_function, division, absolute_import
import numpy as np
from PLIdentify import PL_identify
import cPickle as pk

data = pk.load(open('./dump_robust.txt', 'r'))
I_rec = data['I_rec']
# import ipdb;ipdb.set_trace()
n = I_rec[0].shape[0] # no. of candidnate PLs
m = len(I_rec) # window size
D = np.zeros((m, n))
for j in xrange(n):
    for i in xrange(m):
        D[i, j] = I_rec[i][j, 0]

from PLRefine import HeuristicRefinePL
lamb = 1.5
gam = 50
r = 0.5
epsi = 0.001
x = HeuristicRefinePL(D, lamb, gam, r, epsi)

print('x', x)
if x is None:
    print('No feasible selection')
    import sys
    sys.exit(0)
select_D = D[:, np.nonzero(x)[0]]
org_entro = np.min(D, axis=1)
select_entro = np.min(select_D, axis=1)
import matplotlib.pyplot as plt
plt.subplot(311)
plt.plot(D)
plt.subplot(312)
plt.plot(select_D)
plt.subplot(313)
plt.plot(org_entro, 'r-+')
plt.plot(select_entro, 'b-*')
print('select [%d] PLs out of [%d] PLs'%(sum(x), len(x)))
plt.legend(['orginal', 'selected'])
plt.show()
import ipdb;ipdb.set_trace()

