#!/usr/bin/env python

### -- Revision History ---
### -- [2012-02-27 19:21:25] Add DumpDerivative() --

import copy
import sys
sys.path.append("..")
import util
import settings
import cPickle as pickle

VB = False

try:
    import numpy as np
except ImportError:
    print 'no numpy in derivative'
try:
   import matplotlib.pyplot as plt
except:
   print 'no matplotlib'

ModelBaseSmallest = []
ModelBaseLargest = []
ModelFreeSmallest = []
ModelFreeLargest = []

ModelBase = []
ModelFree = []

def CleanGlobalDeri():
    global ModelBaseSmallest, ModelBaseLargest, ModelFreeSmallest, ModelFreeLargest
    global ModelBase, ModelFree
    ModelBaseSmallest = []
    ModelBaseLargest = []
    ModelFreeSmallest = []
    ModelFreeLargest = []

    ModelBase = []
    ModelFree = []
    assert(len(ModelBase)==0 and len(ModelFree)==0)

def GetCondProb(P1, mp1, P2, mp2):
    assert( abs(np.sum(mp1)  - 1.0 ) < 1e-3 and abs(np.sum(mp2) - 1.0 ) < 1e-3)
    a, b = np.shape(P1)
    P1Con = copy.deepcopy(P1)
    P2Con = copy.deepcopy(P2)
    for i in range(a):
        for j in range(b):
            if mp1[i] != 0:
                P1Con[i, j] /= mp1[i]
            if mp2[i] != 0:
                P2Con[i, j] /= mp2[i]
    return P1Con, P2Con

def ModelBaseDerivative(P1, mp1, P2, mp2):
    P1Con, P2Con = GetCondProb(P1, mp1, P2, mp2)
    a, b = np.shape(P1Con)
    for i in xrange(a):
        for j in xrange(b):
            if P1Con[i, j] == 0:
                P1Con[i, j] = np.nan
            if P2Con[i, j] == 0:
                P2Con[i, j] = np.nan

    if settings.ANOMALY_TYPE_DETECT_INDI == 'derivative':
        deri = np.log(P1Con * 1.0 / P2Con)
    else:
        deri = P1Con * np.log(P1Con * 1.0 / P2Con)


    ModelBase.append(deri)

    eleIdx = np.nanargmin(deri)
    smallest = np.nanmin(deri)
    largest = np.nanmax(deri)
    if VB:
        print '[Modelbase] most negative derivative: ', smallest
        print '[Modelbase] most positive derivative: ', largest
    ModelBaseSmallest.append(smallest)
    ModelBaseLargest.append(largest)
    return deri

def ModelFreeDerivative(P1, P2):
    a, = P1.shape
    deri = np.zeros( (a, ) )
    for i in xrange(a):
        if P1[i] == 0 or P2[i] == 0:
            deri[i] = np.nan
        else:
             if settings.ANOMALY_TYPE_DETECT_INDI == 'derivative':
                 deri[i] = np.log( P1[i] * 1.0 / P2[i] ) + 1
             else:
                 deri[i] = P1[i] * np.log( P1[i] * 1.0 / P2[i] )

    ModelFree.append(deri)

    eleIdx = np.nanargmin(deri)
    smallest = np.nanmin(deri)
    largest = np.nanmax(deri)
    if VB:
        print '[Modelfree] most negative derivative: ', smallest
        print '[Modelfree] most positive derivative: ', largest
    ModelFreeSmallest.append(smallest)
    ModelFreeLargest.append(largest)
    return deri


def DumpDerivative():
    pickle.dump(ModelFree, open(settings.MODEL_FREE_DERI_DUMP_FILE, 'w'))
    pickle.dump(ModelBase, open(settings.MODEL_BASE_DERI_DUMP_FILE, 'w'))


def PlotModelFree():
    dl = len(ModelFree)
    stateNum = len(ModelFree[0])
    for i in xrange(stateNum):
        plt.figure()
        deriVec = [d[i] for d in ModelFree]
        plt.plot(deriVec)
        plt.title('state: %d'%(i))
        plt.savefig(settings.DERIVATIVE_FIGURE_DIR + 'model_free_state-%d.eps'%(i))

def PlotModelBase():
    dl = len(ModelBaseSmallest)
    m, n = ModelBase[0].shape
    for i in xrange(m):
        for j in xrange(n):
            idx = i * n + j
            fig = plt.figure()
            deriVec = [d[i, j] for d in ModelBase]
            # import pdb;pdb.set_trace()
            plt.plot(deriVec)
            plt.title('i-%d-j-%d' %(i,j))
            plt.savefig(settings.DERIVATIVE_FIGURE_DIR + 'i-%d-j-%d.eps'%(i, j))

    # plt.subplot(211)
    # plt.plot(ModelFreeSmallest)
    # plt.plot(ModelFreeLargest)
    # plt.legend(['smallest', 'largest'])
    # plt.plot([0, dl], [0, 0], 'r--')
    # plt.title('smallest and largest derivative for model free case')

    # plt.subplot(212)
    # plt.plot(ModelBaseSmallest)
    # plt.plot(ModelBaseLargest)
    # plt.legend(['smallest', 'largest'])
    # plt.plot([0, dl], [0, 0], 'r--')
    # plt.title('smallest and largest derivative for model base case')

    # plt.savefig(settings.DERIVATIVE_FIGURE_PATH)
    # plt.show()
