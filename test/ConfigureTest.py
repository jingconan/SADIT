#!/usr/bin/env python
from unittest import TestCase, main
import sys
sys.path.append("..")
from Configure.anomaly import *

class MyTest(TestCase):
    def testAttriAnomaly(self):
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
        # self.assertEqual(1, 2)
    def testAtypicalUserAnomaly(self):
        import test_settings.target_one_server as ST
        gen_desc = {'TYPE':'harpoon', 'flow_size_mean':'4e5', 'flow_size_var':'100', 'flow_arrival_rate':'0.5'},
        ANO_DESC = {'anoType':'atypical_user',
                'T':(1200, 1400),
                'gen_desc':ST.NORM_DESC['gen_desc'],
                'link_to':[1] * ST.g_size,
                'link_attr':{'weight':'10', 'capacity':'10000000', 'delay':'0.01'}, # link Attribute
                'ATIP':['123, 234, 12, 3'],
                # 'ATIP':[[123, 234, 12, 3]],
                }

        GenAnomalyDot([ANO_DESC], ST.NET_DESC, ST.NORM_DESC, ST.OUTPUT_DOT_FILE)


if __name__ == "__main__":
    main()
    # main()
    # GenAnomalyDot(settings.ANO_LIST, settings.NET_DESC,
                # settings.NORM_DESC, settings.OUTPUT_DOT_FILE)
