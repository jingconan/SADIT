#!/usr/bin/env python
### -- [2012-03-01 14:45:51] Add FlowRateChange

import os
import cPickle as pickle

import numpy as np
from matplotlib.pyplot import *
import settings

from util import *

from API import *
def FlowRateChange(rg, case):
    '''Simulate under different flow rate and store the simulation result'''
    templateFilePath = './settings_template.py'
    settingsFilePath = './settings.py'
    dataDir = './Share/sens/%s/'%(case)

    CreateSettings(templateFilePath, settingsFilePath,
            ANOMALY_TYPE = 'FLOW_RATE')
    GlobalGenerateNominalPDF()

    if not os.path.exists(dataDir):
        os.mkdir(dataDir)
    i = 0
    for FLOW_RATE in rg:
        i += 1
        # Write New Setting File
        CreateSettings(templateFilePath, settingsFilePath,
            ANOMALY_TYPE = 'FLOW_RATE',
            FLOW_RATE = FLOW_RATE)
        GlobalConfigure()
        Simulate()
        GlobalDetect(settings.OUTPUT_FLOW_FILE, '%s/%f.p'%(dataDir, FLOW_RATE))

    Sensitivity(case)


def Sensitivity(case):
    '''Load the simulation results and show them in the same figure'''
    PREFIX = './Share/sens/%s/' %(case)
    fNameList = os.listdir(PREFIX)
    fNameList = [x for x in fNameList if x[-1] == 'p']
    print 'fNameList', fNameList

    figure()
    h1 = subplot(211)
    h2 = subplot(212)
    IF = list()
    fv = map(lambda x: float(x.split('.p')[0]), fNameList)
    idxSet = np.argsort(fv)
    print 'fv: ', fv
    print 'idxSet: ', idxSet

    # for f in fNameList:
    v = []
    for i in idxSet:
        f = fNameList[i]
        print 'f, ', f
        if case[0:6].lower() == 'markov':
            v.append('pi: %f, %f' %(fv[i], 1-fv[i]))
        elif case[0:4].lower() == 'flow':
            v.append(str(fv[i] ) + ' x')
        else:
            raise ValueError('unknown case')

        t2, IF2, IB2, sampleSize = pickle.load(open(PREFIX + f, 'r'))
        h1.plot(t2, IF2)
        h2.plot(t2, IB2) # v.reverse()

    h1.legend(v)
    h2.legend(v)
    # epsilon = 1e-100
    epsilon = settings.FALSE_ALARM_RATE
    # import pdb; pdb.set_trace()
    # trueThreshold = np.array(1.0 / np.array(sampleSize)) * (-1.0) * np.log(epsilon + np.log(sampleSize) / np.array(sampleSize) )
    threshold = np.array(1.0 / np.array(sampleSize)) * (-1.0) * np.log(epsilon)
    h1.plot(t2, threshold, 'g.-', linewidth=3.0)
    h2.plot(t2, threshold, 'g.-', linewidth=3.0)

    trueThreshold = np.array(1.0 / np.array(sampleSize)) * (-1.0) * np.log(epsilon) + np.log(sampleSize) / np.array(sampleSize)
    h1.plot(t2, trueThreshold, 'r--', linewidth=3.0)
    h2.plot(t2, trueThreshold, 'r--', linewidth=3.0)
    # h2.plot(t2, trueThreshold * 1.5, '--', linewidth=3.0)
    savefig('./res/sen_%s.eps' %(case))
    # show()


def SensitivityCompareThreshold(case, ratio):
    PREFIX = './Share/sens/%s/' %(case)
    fNameList = os.listdir(PREFIX)
    fNameList = [x for x in fNameList if x[-1] == 'p']
    print 'fNameList', fNameList

    figure()
    h1 = subplot(211)
    h2 = subplot(212)
    IF = list()
    fv = map(lambda x: float(x.split('.p')[0]), fNameList)
    idxSet = np.argsort(fv)
    print 'fv: ', fv
    print 'idxSet: ', idxSet

    # for f in fNameList:
    v = []
    for i in idxSet:
        f = fNameList[i]
        print 'f, ', f
        if case[0:6].lower() == 'markov':
            v.append('pi: %f, %f' %(fv[i], 1-fv[i]))
        elif case[0:4].lower() == 'flow':
            v.append(str(fv[i] ) + ' x')
        else:
            raise ValueError('unknown case')

        t2, IF2, IB2, sampleSize = pickle.load(open(PREFIX + f, 'r'))
        h1.plot(t2, IF2)
        h2.plot(t2, IB2) # v.reverse()

    h1.legend(v)
    h2.legend(v)
    # epsilon = 1e-100
    epsilon = settings.FALSE_ALARM_RATE

    for i in ratio:
        trueThreshold = np.array(1.0 / np.array(sampleSize)) * (-1.0) * np.log(epsilon) + i * np.log(sampleSize) / np.array(sampleSize)
        h1.plot(t2, trueThreshold, '--', linewidth=1.0)
        h2.plot(t2, trueThreshold, '--', linewidth=1.0)

    savefig('./res/sen_%s_compare_theshold.eps' %(case))
    show()


if __name__ == "__main__":
    # Sensitivity('flow_size_decr')
    # Sensitivity('flow_size_incr')
    # Sensitivity('flow_rate_incr')
    # Sensitivity('window_size')
    # Sensitivity('flow_rate_decr')
    Sensitivity('FlowRateIncr')
    SensitivityCompareThreshold('FlowRateIncr', [0, 3, 6, 9])
    # Sensitivity('window_size_FLOW_RATE')
    # import sys
    # Sensitivity(sys.argv[1])
