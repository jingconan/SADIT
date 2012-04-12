#!/usr/bin/env python
from unittest import TestCase, main
import sys
sys.path.append("..")
import settings
from Configure.anomaly import *

class MyTest(TestCase):
    def testTargetOneServerDot(self):
        ## Generate Star topology ##
        # total number of nodes
        import settings.target_one_server as ST
        GenAnomalyDot(ST.ANO_LIST, ST.NET_DESC,
            ST.NORM_DESC, ST.OUTPUT_DOT_FILE)


if __name__ == "__main__":
    main()
    # main()
    # GenAnomalyDot(settings.ANO_LIST, settings.NET_DESC,
                # settings.NORM_DESC, settings.OUTPUT_DOT_FILE)
