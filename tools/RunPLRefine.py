#!/usr/bin/env python
"""  Run Probability Law Identification
"""
from __future__ import print_function, division, absolute_import
from sadit.util import np, zload, plt
from sadit.Detector.PLRefine import HeuristicRefinePL
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Probability Law Identification")
    parser.add_argument('sscheck', help='self check file')
    parser.add_argument('lamb', type=float, help='up bound for the threshold')
    parser.add_argument('entro', help="['mf', 'mb'] entropy type")
    args = parser.parse_args()

    data = zload(args.sscheck)

    I_rec = data['I_rec']
    n = I_rec[0].shape[0] # no. of PLs
    m = len(I_rec) # no. of windows
    seq_map = {
            'mf':0,
            'mb':1
            }
    # Convert I_rec to the weight of bipartie graph
    D = np.zeros((m, n))
    for j in xrange(n):
        for i in xrange(m):
            D[i, j] = I_rec[i][j, seq_map[args.entro]]

    x = HeuristicRefinePL(D, args.lamb, 50, 0.5, 0.01)
    if x is None:
        print('No feasible selection')
        import sys
        sys.exit(0)

    print('solution: ', x)
    select_D = D[:, np.nonzero(x)[0]]
    org_entro = np.min(D, axis=1)
    select_entro = np.min(select_D, axis=1)

    plt.subplot(311)
    plt.plot(D)
    plt.title('orginal fitness curves')
    plt.setp(plt.gca().get_xticklabels(), visible=False)

    plt.subplot(312)
    plt.plot(select_D)
    plt.title('selected fitness curves')
    plt.setp(plt.gca().get_xticklabels(), visible=False)

    plt.subplot(313)
    plt.plot(org_entro, 'r-+')
    plt.plot(select_entro, 'b-*')
    plt.title('miniumn of curves')
    plt.legend(['orginal', 'selected'])
    print('select [%d] PLs out of [%d] PLs'%(sum(x), len(x)))
    plt.show()
    # import ipdb;ipdb.set_trace()
