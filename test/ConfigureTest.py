#!/usr/bin/env python
from unittest import TestCase, main
import sys
sys.path.append("..")
from Configure import *

class MyTest(TestCase):
    def _testMarkov(self):
        import test_settings.target_one_server as ST
        GenAnomalyDot([], ST.NET_DESC, ST.NORM_DESC, ST.OUTPUT_DOT_FILE)

    def _testMarkovPAnomaly(self):
        import test_settings.markov_p_ano as ST
        GenAnomalyDot(ST.ANO_LIST, ST.NET_DESC, ST.NORM_DESC, ST.OUTPUT_DOT_FILE)

    def testNormal(self):
        import test_settings.target_one_server as ST
        NET_DESC  = ST.NET_DESC
        NET_DESC['node_type'] = 'NNode'
        NORM_DESC = ST.NORM_DESC
        del NORM_DESC['node_para']['states'][1]
        GenAnomalyDot([], ST.NET_DESC, ST.NORM_DESC, ST.OUTPUT_DOT_FILE)

    def _testAttriAnomaly(self):
        import test_settings.target_one_server as ST
        anomaly = ['flow_size_mean', 'flow_size_var', 'flow_arrival_rate']
        ANO_LIST = ST.ANO_LIST
        for ano in anomaly:
            ANO_DESC = {'anoType':ano,
                    'ano_node_seq':2,
                    'T':(1200, 1400),
                    'change':{ano:1.5},
                    'srv_id':0,
                    }
            GenAnomalyDot([ANO_DESC], ST.NET_DESC, ST.NORM_DESC, ST.OUTPUT_DOT_FILE)

if __name__ == "__main__":
    main()
    # main()
    # GenAnomalyDot(settings.ANO_LIST, settings.NET_DESC,
                # settings.NORM_DESC, settings.OUTPUT_DOT_FILE)
