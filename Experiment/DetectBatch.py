#!/usr/bin/env python
""" Argument Search script for optimal parameters for stochastic
method [model free and model based] methdod.
"""
from __future__ import print_function, division
import os
import sys; sys.path.append("..")
from Detector import detect

import copy
# def get_attr_list(attr_dict):
#     """ get attributes which are list type,

#     get attributes which are list type recursively and merge result into a flat
#     dictioanry

#     """
#     res = dict()
#     for k, v in attr_dict.iteritems():
#         if isinstance(v, dict):
#             lower_res = get_attr_list(v)
            # lower dictionary shouldn't have the same name with up dictionary
#             assert(all( lowerk not in attr_dict.keys() for lowerk in lower_res.keys()))
#             res.update(lower_res)
#         elif isinstance(v, list):
#             res[k] = copy.deepcopy(v)
#     return res

def change_attr_list(attr_dict, k, v):
    """search dictionary recursively and change an attribute

    Parameters
    -----------------
    attr_dict : dict
        the dictionary that will be searched and changed
    k :
        the key
    v :
        the value

    """
    if k in attr_dict.keys():
        attr_dict[k] = v
        return True
    for k0, v0 in attr_dict.iteritems():
        if isinstance(v0, dict):
            if change_attr_list(v0, k, v):
                return True

    return False

def dict_sget(d, k):
    """ set dictionary according to a string

    Parameters:
    ---------------
    Returns:
    --------------
    examples
    --------------
    >>> d = {'a':{'b':[1.12]}}
    >>> print(dict_sget(d, 'a.b'))
    [1.12]
    """
    kl = k.rsplit('.')
    v = d
    for kv in kl:
        v = v.get(kv, {})
    return v

def dict_sset(d, k, v):
    """  set dictionary, according to k and v

    Parameters:
    ---------------
    d : dict
        dictionary
    k : string
        key
    v :
        value

    Returns:
    --------------
    None

    Examples
    --------------
    >>> d = {'a':{'b':[1]}}
    >>> dict_sset(d, 'a.b', [2])
    >>> print(d)
    {'a': {'b': [2]}}

    """
    kl = k.rsplit('.')
    struc = d
    for kv in kl[:-1]:
        struc = struc.get(kv, {})
    struc[kl[-1]] = v

def dict_supdate(d, d1):
    """

    Parameters:
    ---------------
    Returns:
    --------------

    Examples
    --------------
    >>> d = {'a':{'b':[1], 'c':[2]}}
    >>> dict_supdate(d, {'a.b':[3]})
    >>> print(d)
    {'a': {'c': [2], 'b': [3]}}
    """
    for k, v in d1.iteritems():
        dict_sset(d, k, v)

import itertools
# import operator
import time
import linecache
from Detect import Detect
# from util import load_para
class DetectBatch(Detect):
    """
    Run Detect with different parameters in a batch mode.
    """
    def __init__(self, *args, **kwargs):
        super(DetectBatch, self).__init__(*args, **kwargs)
        self.desc = copy.deepcopy(self.args.config['DETECTOR_DESC'])
        self.batch_var_names = self.desc['batch_var']
        self.batch_var_vals = [dict_sget(self.desc, vn) \
                for vn in self.batch_var_names]

        # self.comb_num = reduce(operator.mul, [len(v) for k, v in self.change_opt.iteritems()])
        # self.comb_name = batch_var_names


    def init_parser(self, parser):
        super(DetectBatch, self).init_parser(parser)
        parser.add_argument('--res_folder', default=None,
                help="""result folder name""")

    def _export_ab_flow_by_idx(self, flow_file, output_file, ab_flow_idx):
        fid = open(output_file, 'w')
        for idx in ab_flow_idx:
            line = linecache.getline(flow_file, idx)
            fid.write(line)
        fid.close()

    def export_ab_flow_raw(self, flow_file, output_file, *args, **kwargs):
        dirname = os.path.dirname(output_file)
        basename = os.path.basename(output_file)

        ab_flow_seq = self.detector.get_ab_flow_seq('mf', *args, **kwargs)
        self._export_ab_flow_by_idx(flow_file, dirname + '/mf-' + basename, ab_flow_seq)

        ab_flow_seq = self.detector.get_ab_flow_seq('mb', *args, **kwargs)
        self._export_ab_flow_by_idx(flow_file, dirname + '/mb-' + basename, ab_flow_seq)

    def export_ab_flow_short_cut(self, fname, desc):
        self.export_ab_flow_raw(
                # flow_file = desc['flow_file'],
                flow_file = desc['data'],
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

    def export_ident_flow(self, fname, entropy_type, desc):
        """instead of exportoing all flows in the suspicious window,
        **export_ident_flow** will export flows only when flows are in anomalous state"""
        flow_state = self.detector.ident(entropy_type=entropy_type,
                entropy_threshold = desc['entropy_threshold'],
                ab_win_portion = desc['ab_win_portion'],
                ab_win_num = desc['ab_win_num'],
                **desc['ident'][entropy_type]
                )
        ab_flow_seq = self.detector.get_ab_flow_seq(entropy_type, ab_flow_info=flow_state,
                entropy_threshold = desc['entropy_threshold'],
                ab_win_portion = desc['ab_win_portion'],
                ab_win_num = desc['ab_win_num'],
                )
        dirname = os.path.dirname(fname)
        basename = os.path.basename(fname)
        # self._export_ab_flow_by_idx(desc['flow_file'],
        self._export_ab_flow_by_idx(desc['data'],
                dirname + '/%s-'%(entropy_type) + basename, ab_flow_seq)


    def export(self, prefix, desc):
        """export outputs"""
        # self.detector.plot_entropy(False, prefix+'.eps')
        self.detector.plot(pic_name = prefix+'.eps')
        self.export_ab_flow_short_cut(prefix+'-raw.txt', desc)
        self.export_ab_flow_formated(prefix+'-formated.txt', desc)
        self.export_ident_flow(prefix+'-ident.txt', 'mf', desc)
        self.export_ident_flow(prefix+'-ident.txt', 'mb', desc)

    def run(self):
        # RES_DIR = './res/'
        RES_DIR = self.desc['res_folder']
        if not os.path.exists(RES_DIR):
            os.makedirs(RES_DIR)

        # self.change_opt = dict(zip(self.batch_var_names, self.batch_var_vals))
        # print 'total number of combination is %i'%(self.comb_num)
        for cb in itertools.product(*self.batch_var_vals):
            print('run detection with combination: ')
            print('-' * 20)
            for tup in zip(self.batch_var_names, cb):
                print('%s: %s'%tup)
            print('-' * 20)
            start_time = time.clock()
            template = copy.deepcopy(self.desc)
            dict_supdate(template, dict(zip(self.batch_var_names, cb)))

            self.detector = detect(template['data'], template)
            name = '-'.join([n+'_'+str(v) \
                    for n, v in zip(self.batch_var_names, cb)])
            self.export(RES_DIR+name, template)

            end_time = time.clock()
            sim_dur = end_time - start_time
            print('sim_dur', sim_dur)
            # print 'simulation of this combination use [%f]s, total comb num [%i], total time will be[%f]s'%(sim_dur, self.comb_num, sim_dur*self.comb_num )

if __name__ == "__main__":
    import doctest
    doctest.testmod()
# if __name__ == "__main__":
#     import search_arg_settings
#     import argparse
#     parser = argparse.ArgumentParser(description='DetectArgSearch')
#     parser.add_argument('--file', dest='flow_file', default=None,
#             help = """the flow file used by experiment, if this option
#             is set, it will override the settings in setting file""")
#     args = parser.parse_args()
#     if args.flow_file:
#         search_arg_settings.desc['flow_file'] = args.flow_file
#     cls = DetectBatch(search_arg_settings.desc)
#     cls.run()
