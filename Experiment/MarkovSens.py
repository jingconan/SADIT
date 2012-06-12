#!/usr/bin/env python
from Sens import Sens
from MarkovExperiment import MarkovExperiment
import cPickle as pickle
import copy

class MarkovSens(MarkovExperiment, Sens):
    """Sensitivity analysis of markov anomaly"""
    def __init__(self, settings):
        MarkovExperiment.__init__(self, settings)
        Sens.__init__(self)
        self.sens_ano = settings.ANO_LIST[0] # Only support one anomaly right now
        self.shelve_file = self.settings.ROOT + '/Share/det_obj.out'

    def run(self, sta_prob_option):
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

        f_obj = open(self.shelve_file, 'w')
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
