#!/usr/bin/env python
### -- [2012-03-01 14:44:26] seperate some functions to API.py, rename run, main

from shutil import copyfile
from time import clock as now
from API import *

def run():
    # copyfile('./settings_template.py', './settings.py')
    reload(settings)
    if settings.UNIFIED_NOMINAL_PDF: GlobalGenerateNominalPDF()
    print 'start to configure'
    gen_anomaly_dot(settings.ANO_LIST,
            settings.NET_DESC,
            settings.NORM_DESC,
            settings.OUTPUT_DOT_FILE)

    print 'start to simulate'
    Simulate()
    # print 'start to detect'
    # GlobalDetect(settings.OUTPUT_FLOW_FILE)
    # anoType = GetAnomalyType()
    # print 'anoType, ', anoType

def Test():
    GlobalDetect(settings.OUTPUT_FLOW_FILE)

    mfIndi = ModelFreeDetectAnoType()
    ModelFreeHTest(mfIndi)

    mbIndi = ModelBaseDetectAnoType()
    # PrintModelBase(mbIndi)
    ModelBaseHTest(mbIndi)
    anoType = GetAnomalyType()
    # print 'anoType, ', anoType


def MultiRun():
    sh('./clean.sh')
    import settings_template

    # rg = [0.8, 0.6, 0.4, 0.2]
    # rg = [1.5, 2]
    # rg = [1, 2, 3, 4, 5, 6]
    rg = settings_template.FLOW_RATE_RANGE
    case = 'FlowRateIncr'
    FlowRateChange(rg, case)

    # rg = settings_template.FLOW_SIZE_RANGE
    # case = 'FlowSizeIncr'
    # FlowSizeChange(rg, case)

from pylab import *
def test_msdesctor():
    print 'start to detect'
    copyfile('./settings/multi_srv_targ_one.py', './settings.py')
    reload(settings)
    GlobalDetect(settings.OUTPUT_FLOW_FILE)

    IF2, IB2, t2, threshold  = MSDetect(settings.NET_DESC['srv_list'],
            settings.DISCRETE_LEVEL + [settings.CLUSTER_NUMBER],
            settings.DETECTOR_WINDOW_SIZE)
    rt = array(t2) - min(t2)
    figure()
    subplot(211)
    plot(rt, IF2)
    subplot(212)
    plot(rt, IB2)
    savefig(settings.ROOT + '/res/entropy-multi-server.eps')
    import pdb;pdb.set_trace()
    # show()

def old_detector():
    copyfile('./settings/multi_srv_targ_one_with_fr.py', './settings.py')
    reload(settings)
    GlobalDetect(settings.OUTPUT_FLOW_FILE)


def multi_srv_targ_one():
    copyfile('./settings/multi_srv_targ_one.py', './settings.py')
    reload(settings)
    run()

dispatcher = {
        'ms':multi_srv_targ_one,
        't':test_msdesctor,
        'od':old_detector,
        }
if __name__ == "__main__":
    run()
    # import sys
    # dispatcher[sys.argv[1]]()

    # Test()
    # mfIndi = ModelFreeDetectAnoType()
    # mbIndi = ModelBaseDetectAnoType()
    # Print(mfIndi, mbIndi)
    # GetAnomalyType()
    # Run()
    # MultiRun()





