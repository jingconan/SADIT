#!/usr/bin/env python
""" Sensitivity analysis anomaly detectors under
markovian traffic model
"""
from AttriSensExper import Sens
from MarkovExper import MarkovExper
import cPickle as pickle
import copy

class MarkovSens(MarkovExper, Sens):
    """Sensitivity analysis of markov anomaly"""
    def __init__(self, *args, **kwargs):
        MarkovExper.__init__(self, *args, **kwargs)
        Sens.__init__(self)
        self.sens_ano = self.ano_list[0] # Only support one anomaly right now
        # self.sens_ano = settings.ANO_LIST[0] # Only support one anomaly right now
        # self.shelve_file = self.settings.ROOT + '/Share/det_obj.out'

    def init_parser(self, parser):
        super(MarkovSens, self).init_parser(parser)
        # ds = '[[0.9, 0.1],[0.7, 0.3],[0.5, 0.5],[0.8,0.2]]'
        ds = '[[0.9, 0.1],[0.7, 0.3]]'
        parser.add_argument('--sta_prob_option', default=ds, type=eval,
                help = """the possible values for stationary probability distribution, should be a list of list."""
                )
        parser.add_argument('--store_res_file', default=self.ROOT + '/Share/det_obj_markov.out',
                help="""file path to store the caculated results""")

        parser.add_argument('--plot', default=None,
                help = """plot previous calculated result""")

    def run(self):
        if self.args.plot:
            self.plot_entropy(self.args.plot)
            return

        self._run(self.args.sta_prob_option)
        self.plot_entropy(self.args.store_res_file)

    def _run(self, sta_prob_option):
        det_obj_shelf = dict()
        self.sens_ano['ano_type'] = 'markov_anomaly'
        self.sens_ano['change'] = {}

        for sta_prob in sta_prob_option:
            self.ano_sta_prob = sta_prob
            self.configure()
            self.simulate()
            det_obj = copy.deepcopy( self.detect() )
            det_obj_shelf[tuple(sta_prob)] = dict(winT=det_obj.record_data['winT'],
                    entropy=det_obj.record_data['entropy'])
            self.store_flow_file('markov_' + '_'.join([str(v) for v in sta_prob]))
            # self.clear_tmp_file()

        # f_obj = open(self.shelve_file, 'w')
        print '--> dump calculated result to [%s]'%(self.args.store_res_file)
        f_obj = open(self.args.store_res_file, 'w')
        pickle.dump(det_obj_shelf, f_obj)
        f_obj.close()

if __name__ == "__main__":
    import settings
    exper = MarkovSens(settings)
    exper.run( [[0.9, 0.1],
                [0.7, 0.3],
                [0.5, 0.5],
                [0.8, 0.2]
                ])
    exper.plot_entropy()
