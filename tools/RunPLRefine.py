#!/usr/bin/env python
"""  Run Probability Law Identification
"""
from __future__ import print_function, division, absolute_import
from sadit.util import np, zload, plt
from sadit.Detector.PLRefine import HeuristicRefinePL
import argparse
import sys

def mplot(x, mat):
    m, n = mat.shape
    # linestyles = ['_', '-', '--', ':', '-.']
    linestyles = ['-', '--', '-.']
    # styles = ['+', '*', 'x']
    styles = ['']
    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')

    for i in range(n):
        color = colors[i % len(colors)]
        style = styles[i % len(styles)]
        ls = linestyles[i % len(linestyles)]
        plt.plot(x, mat[:, i], linestyle=ls, marker=style,
                color=color, markersize=4)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Probability Law Identification")
    parser.add_argument('sscheck', help='self check file')
    parser.add_argument('lamb', type=float, help='up bound for the threshold')
    parser.add_argument('entro', help="['mf', 'mb'] entropy type")
    parser.add_argument('pic_name', default=None, help="output picture name")

    args = parser.parse_args()

    data = zload(args.sscheck)
    # import ipdb;ipdb.set_trace()

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
        # import sys
        sys.exit(0)

    print('solution: ', x)
    select_D = D[:, np.nonzero(x)[0]]
    org_entro = np.nanmin(D, axis=1)
    select_entro = np.nanmin(select_D, axis=1)

    plt.subplot(411)
    plt.plot(D)
    plt.title('divergence between traffic and all candidate PLs')
    plt.setp(plt.gca().get_xticklabels(), visible=False)
    plt.ylabel('divergence')

    plt.subplot(412)
    # plt.plot(select_D)
    mplot(range(m), select_D)
    plt.title('divergence between traffic and selected PLs')
    plt.setp(plt.gca().get_xticklabels(), visible=False)
    plt.ylabel('divergence')


    ##### plot selected model id with PL Identification #######
    plt.subplot(413)
    selected_model = []
    for j in xrange(m):
        e = select_entro[j]
        idx = (D[j, :] == e).nonzero()[0][0]
        selected_model.append(idx)
    # import ipdb;ipdb.set_trace()
    # selected_model = sorted(selected_model)
    plt.plot(selected_model, linewidth=2)
    plt.ylabel('PL Seq.')
    # plt.yticks(range(0, 30, 10), size='small')
    plt.ylim([0, n])
    plt.gca().get_xaxis().set_visible(False)


    plt.subplot(414)
    plt.plot(org_entro, 'r-+')
    plt.plot(select_entro, 'b-*')
    plt.title('miniumn of curves')
    plt.legend(['orginal', 'selected'])
    plt.ylabel('divergence')
    print('select [%d] PLs out of [%d] PLs'%(sum(x), len(x)))
    plt.xlabel('time (hour)')
    if args.pic_name:
        plt.savefig(args.pic_name)
    plt.show()
    # import ipdb;ipdb.set_trace()
