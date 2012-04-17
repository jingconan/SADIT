#!/usr/bin/env python
from unittest import TestCase, main
import sys
sys.path.append("..")
from Configure import *
from util import *
from Configure.mod_util import *

class Configure(TestCase):
    def _testMarkovBehaviour(self):
        import Configure.MarkovBehaviour as TM
        interval = 1
        P = [[0.1, 0.9], [0.2, 0.8]]
        states = ['1','2']
        TM.MarkovBehaviour()
        pass

    def testEdge(self):
        pass

    def testGenerator(self):
        import Configure as TM
        import normal
        gen_desc = {'TYPE':'harpoon',
                'flow_size_mean':'4e5',
                'flow_size_var':'100',
                'flow_arrival_rate':'0.5'}

        # import pdb;pdb.set_trace()
        gen_desc['ipsrc'] = '0.0.0.0'
        gen_desc['ipdst'] = '1.1.1.1'
        gen = TM.HarpoonG(**Load(gen_desc))
        gen.sync()
        string = str(gen)
        print '+' * 100
        print 'string\n', string
        print '+' * 100


    def testModulator(self):
        pass

    def testNode(self):
        pass

    def testNetwork(self):
        pass

    def _testMarkov(self):
        import target_one_server as ST
        GenAnomalyDot([], ST.NET_DESC, ST.NORM_DESC, ST.OUTPUT_DOT_FILE)

    def _testMarkovPAnomaly(self):
        import markov_p_ano as ST
        GenAnomalyDot(ST.ANO_LIST, ST.NET_DESC, ST.NORM_DESC, ST.OUTPUT_DOT_FILE)

    def _testNoAnomaly(self):
        import simple as ST
        GenAnomalyDot([], ST.NET_DESC, ST.NORM_DESC, ST.OUTPUT_DOT_FILE)

    def _testSimpleAnomaly(self):
        import simple as ST
        GenAnomalyDot([], ST.NET_DESC, ST.NORM_DESC, ST.OUTPUT_DOT_FILE)

    def _testAttriAnomaly(self):
        import target_one_server as ST
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

class AnomalyTest(TestCase):
    def setUp(self):
        pass

    def testAnomaly(self):
        pass

    def testMarkovAnomaly(self):
        pass



if __name__ == "__main__":
    main()
    # main()
    # GenAnomalyDot(settings.ANO_LIST, settings.NET_DESC,
                # settings.NORM_DESC, settings.OUTPUT_DOT_FILE)
