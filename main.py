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
import settings

from util import *
from Sensitivity import *

from API import *

def Run():
    copyfile('./settings_template.py', './settings.py')
    if settings.UNIFIED_NOMINAL_PDF: GlobalGenerateNominalPDF()
    print 'start to configure'
    # GlobalConfigure()
    reload(settings)
    GenAnomalyDot(settings.ANO_DESC,
            settings.NET_DESC,
            settings.NORM_DESC,
            settings.OUTPUT_DOT_FILE)

    print 'start to simulate'
    Simulate()
    print 'start to detect'
    GlobalDetect(settings.OUTPUT_FLOW_FILE)
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

if __name__ == "__main__":
    # Test()
    # mfIndi = ModelFreeDetectAnoType()
    # mbIndi = ModelBaseDetectAnoType()
    # Print(mfIndi, mbIndi)
    # GetAnomalyType()
    Run()
    # MultiRun()





