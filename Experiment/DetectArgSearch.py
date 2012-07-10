#!/usr/bin/env python

import sys, os
sys.path.append("..")
from Detector import detect

# ANO_ANA_DATA_FILE = ROOT + '/Share/AnoAna.txt'
# DETECTOR_DESC = dict(
#         interval=20,
#         win_size=200,
#         win_type='time', # 'time'|'flow'
#         fr_win_size=100, # window size for estimation of flow rate
#         false_alarm_rate = 0.001,
#         unified_nominal_pdf = False, # used in sensitivities analysis
#         fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
#         ano_ana_data_file = ANO_ANA_DATA_FILE,
#         normal_rg = None,
#         detector_type = 'mfmb',
#         max_detect_num = 100,
#         data_handler = 'fs_deprec',
#         )

import copy
def get_attr_list(attr_dict):
    """get attributes which are list type,
    do it recursively and merge result into a flat dictioanry"""
    res = dict()
    for k, v in attr_dict.iteritems():
        if isinstance(v, dict):
            lower_res = get_attr_list(v)
            # lower dictionary shouldn't have the same name with up dictionary
            assert(all( lowerk not in attr_dict.keys() for lowerk in lower_res.keys()))
            res.update(lower_res)
        elif isinstance(v, list):
            res[k] = copy.deepcopy(v)
    return res

def change_attr_list(attr_dict, k, v):
    """search dictionary recursively and change an attribute"""
    if k in attr_dict.keys():
        attr_dict[k] = v
        return True
    for k0, v0 in attr_dict.iteritems():
        if isinstance(v0, dict):
            if change_attr_list(v0, k, v):
                return True

    return False


import itertools
import operator
import time
import linecache
class DetectArgSearch(object):
    """
    Run Detect with different parameters in a batch mode.
    """
    def __init__(self, desc_opt):
        self.desc_opt = desc_opt
        self.change_opt = get_attr_list(self.desc_opt)
        if self.change_opt:
            self.comb_num = reduce(operator.mul, [len(v) for k, v in self.change_opt.iteritems()])
            self.comb = itertools.product(*self.change_opt.values())
            self.comb_name = list(self.change_opt.keys())

    def _export_ab_flow_by_idx(self, flow_file, output_file, ab_flow_idx):
        fid = open(output_file, 'w')
        for idx in ab_flow_idx:
            line = linecache.getline(flow_file, idx)
            fid.write(line)
        fid.close()

    def export_ab_flow_raw(self, flow_file, output_file, *args, **kwargs):
        dirname = os.path.dirname(output_file)
        basename = os.path.basename(output_file)

        ab_flow_seq = self.detector.get_ab_flow_seq_mf(*args, **kwargs)
        self._export_ab_flow_by_idx(flow_file, dirname + '/mf-' + basename, ab_flow_seq)

        ab_flow_seq = self.detector.get_ab_flow_seq_mb(*args, **kwargs)
        self._export_ab_flow_by_idx(flow_file, dirname + '/mb-' + basename, ab_flow_seq)

    def export_ab_flow_short_cut(self, fname, desc):
        self.export_ab_flow_raw(
                flow_file = desc['flow_file'],
                output_file = fname,
                entropy_threshold = desc['entropy_threshold'],
                ab_win_portion = desc['ab_win_portion'],
                ab_win_num = desc['ab_win_num'],
                )

    def export_ab_flow_formated(self, fname, desc):
        self.detector.export_abnormal_flow(
                fname,
                entropy_threshold = desc['entropy_threshold'],
                ab_win_portion = desc['ab_win_portion'],
                ab_win_num = desc['ab_win_num'],
                )

    def run(self):
        RES_DIR = '../res/'
        if not self.change_opt:
            template = copy.deepcopy(self.desc_opt)
            self.detector = detect(template['flow_file'], template)
            name = 'res'
            self.detector.plot_entropy(False, RES_DIR+name+'.eps')
            self.export_ab_flow_short_cut(RES_DIR + name + '-raw.txt', template)
            self.export_ab_flow_formated(RES_DIR + name + '-formated.txt', template)
            return

        print 'total number of combination is %i'%(self.comb_num)
        for cb in self.comb:
            print 'run detection with combination: '
            print '-' * 20
            for tup in zip(self.comb_name, cb): print '%s: %s'%tup
            print '-' * 20
            start_time = time.clock()
            template = copy.deepcopy(self.desc_opt)
            for i in xrange(len(cb)):
                res = change_attr_list(template, self.comb_name[i], cb[i])
                if not res: raise Exception('Unkown feature name')

            self.detector = detect(template['flow_file'], template)
            name = '-'.join([n+'_'+str(v) for n, v in zip(self.comb_name, cb)])
            self.detector.plot_entropy(False, RES_DIR+name+'.eps')
            self.export_ab_flow_short_cut(RES_DIR + name+'-raw.txt', template)
            self.export_ab_flow_formated(RES_DIR + name+'-formated.txt', template)

            end_time = time.clock()
            sim_dur = end_time - start_time
            print 'simulation of this combination use [%f]s, total comb num [%i], total time will be[%f]s'%(sim_dur, self.comb_num, sim_dur*self.comb_num )

if __name__ == "__main__":
    import search_arg_settings
    import argparse
    parser = argparse.ArgumentParser(description='DetectArgSearch')
    parser.add_argument('--file', dest='flow_file', default=None,
            help = """the flow file used by experiment, if this option
            is set, it will override the settings in setting file""")
    args = parser.parse_args()
    if args.flow_file:
        search_arg_settings.desc['flow_file'] = args.flow_file
    cls = DetectArgSearch(search_arg_settings.desc)
    cls.run()
