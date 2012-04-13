#!/usr/bin/env python
##
# @file allinone.py
# @brief
# @author Jing Conan Wang, hbhzwj@gmail.com
# @version 1.3
# @date 2012-02-15
# Copyright (C)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

### -- [2012-03-01 14:44:26] seperate some functions to API.py, rename run, main

from shutil import copyfile
from time import clock as now

# from util import *
# from Sensitivity import *
from API import *

def run():
    # copyfile('./settings_template.py', './settings.py')
    reload(settings)
    if settings.UNIFIED_NOMINAL_PDF: GlobalGenerateNominalPDF()
    print 'start to configure'
    GenAnomalyDot(settings.ANO_LIST,
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
    import sys
    dispatcher[sys.argv[1]]()

    # Test()
    # mfIndi = ModelFreeDetectAnoType()
    # mbIndi = ModelBaseDetectAnoType()
    # Print(mfIndi, mbIndi)
    # GetAnomalyType()
    # Run()
    # MultiRun()





